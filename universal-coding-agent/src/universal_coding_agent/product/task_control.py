from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from threading import RLock

from universal_coding_agent.core.cancellation import (
    CancellationCoordinator,
    CancellationReport,
)
from universal_coding_agent.core.remote_operations import (
    RemoteOperationDisposition,
    RemoteOperationDispositionOutcome,
    RemoteOperationSnapshot,
    RemoteOperationState,
)
from universal_coding_agent.product.models import (
    ControlAction,
    ControlDecision,
    ControlEntityType,
    ControlRecord,
    ControlState,
)


class TaskControlService:
    """Persistent control state with cooperative boundaries and owned-work cancellation.

    Callers check at safe boundaries. Pause stops new work at the next boundary; cancel is
    terminal once observed. The lock makes the same service safe to use from an execution
    worker and a concurrent UI/API control request.
    """

    def __init__(
        self,
        database_path: Path,
        *,
        cancellation: CancellationCoordinator | None = None,
    ) -> None:
        self.database_path = database_path.resolve()
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()
        self.cancellation = cancellation or CancellationCoordinator()
        self.connection = sqlite3.connect(self.database_path, check_same_thread=False)
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS control_state (
                entity_type TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                state TEXT NOT NULL,
                reason TEXT NOT NULL,
                revision INTEGER NOT NULL,
                PRIMARY KEY (entity_type, entity_id)
            )
            """
        )
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS cancellation_reports (
                task_id TEXT PRIMARY KEY,
                reason TEXT NOT NULL,
                active_operation_kinds TEXT NOT NULL,
                owned_processes_observed INTEGER NOT NULL,
                owned_cancellable_operations_observed INTEGER NOT NULL DEFAULT 0,
                terminate_requests INTEGER NOT NULL,
                kill_requests INTEGER NOT NULL,
                cancellable_operation_cancel_requests INTEGER NOT NULL DEFAULT 0,
                processes_still_active INTEGER NOT NULL,
                cancellable_operations_still_active INTEGER NOT NULL DEFAULT 0,
                cooperative_fallback INTEGER NOT NULL
            )
            """
        )
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS remote_operation_dispositions (
                task_id TEXT PRIMARY KEY,
                audit_ref TEXT NOT NULL UNIQUE,
                outcome TEXT NOT NULL,
                reason TEXT NOT NULL,
                recorded_at TEXT NOT NULL,
                program_id TEXT NOT NULL,
                phase_id TEXT NOT NULL,
                slice_id TEXT NOT NULL,
                transport TEXT NOT NULL,
                transport_scope TEXT NOT NULL,
                operation_ref TEXT NOT NULL,
                base_sha TEXT NOT NULL,
                remote_state TEXT NOT NULL,
                remote_status TEXT NOT NULL,
                remote_revision INTEGER NOT NULL,
                remote_updated_at TEXT NOT NULL,
                provider_confirmed_cancelled INTEGER NOT NULL,
                confirmed_by_operator INTEGER NOT NULL,
                provider_calls_made INTEGER NOT NULL,
                output_consumed INTEGER NOT NULL,
                graph_resumed INTEGER NOT NULL,
                program_phase_advanced INTEGER NOT NULL
            )
            """
        )
        self._ensure_cancellation_report_columns()
        self.connection.commit()

    def close(self) -> None:
        with self._lock:
            self.connection.close()

    def ensure(
        self,
        entity_type: ControlEntityType,
        entity_id: str,
    ) -> ControlRecord:
        with self._lock:
            current = self.get(entity_type, entity_id)
            if current is not None:
                return current
            self.connection.execute(
                """
                INSERT INTO control_state(entity_type, entity_id, state, reason, revision)
                VALUES (?, ?, ?, '', 0)
                """,
                (entity_type.value, entity_id, ControlState.RUNNING.value),
            )
            self.connection.commit()
            return self.get_required(entity_type, entity_id)

    def get(
        self,
        entity_type: ControlEntityType,
        entity_id: str,
    ) -> ControlRecord | None:
        with self._lock:
            row = self.connection.execute(
                """
                SELECT state, reason, revision FROM control_state
                WHERE entity_type = ? AND entity_id = ?
                """,
                (entity_type.value, entity_id),
            ).fetchone()
            if row is None:
                return None
            return ControlRecord(
                entity_type=entity_type,
                entity_id=entity_id,
                state=ControlState(row[0]),
                reason=row[1],
                revision=row[2],
            )

    def get_required(
        self,
        entity_type: ControlEntityType,
        entity_id: str,
    ) -> ControlRecord:
        with self._lock:
            record = self.get(entity_type, entity_id)
            if record is None:
                raise KeyError(entity_id)
            return record

    def request_pause(
        self,
        entity_type: ControlEntityType,
        entity_id: str,
        *,
        reason: str = "",
    ) -> ControlRecord:
        with self._lock:
            record = self.ensure(entity_type, entity_id)
            if record.state in {
                ControlState.CANCELLED,
                ControlState.FAILED,
                ControlState.COMPLETED,
            }:
                raise ValueError("terminal work cannot be paused")
            if record.state is ControlState.CANCEL_REQUESTED:
                return record
            return self._set(entity_type, entity_id, ControlState.PAUSE_REQUESTED, reason)

    def resume(
        self,
        entity_type: ControlEntityType,
        entity_id: str,
    ) -> ControlRecord:
        with self._lock:
            record = self.ensure(entity_type, entity_id)
            if record.state not in {ControlState.PAUSED, ControlState.PAUSE_REQUESTED}:
                raise ValueError("only paused work can be resumed")
            return self._set(entity_type, entity_id, ControlState.RUNNING, "")

    def request_cancel(
        self,
        entity_type: ControlEntityType,
        entity_id: str,
        *,
        reason: str = "",
    ) -> ControlRecord:
        with self._lock:
            record = self.ensure(entity_type, entity_id)
            if record.state in {
                ControlState.CANCELLED,
                ControlState.FAILED,
                ControlState.COMPLETED,
            }:
                return record
            if record.state is ControlState.CANCEL_REQUESTED:
                return record
            record = self._set(
                entity_type,
                entity_id,
                ControlState.CANCEL_REQUESTED,
                reason,
            )
        if entity_type is ControlEntityType.TASK:
            report = self.cancellation.cancel_task(entity_id, reason=reason)
            self._store_cancellation_report(report)
        return record

    def checkpoint(
        self,
        entity_type: ControlEntityType,
        entity_id: str,
        *,
        safe_boundary: bool = True,
    ) -> ControlDecision:
        with self._lock:
            record = self.ensure(entity_type, entity_id)
            if record.state is ControlState.CANCEL_REQUESTED:
                record = self._set(
                    entity_type,
                    entity_id,
                    ControlState.CANCELLED,
                    record.reason,
                )
                return ControlDecision(action=ControlAction.CANCEL, record=record)
            if record.state is ControlState.CANCELLED:
                return ControlDecision(action=ControlAction.CANCEL, record=record)
            if record.state is ControlState.FAILED:
                return ControlDecision(action=ControlAction.CANCEL, record=record)
            if record.state is ControlState.PAUSE_REQUESTED and safe_boundary:
                record = self._set(
                    entity_type,
                    entity_id,
                    ControlState.PAUSED,
                    record.reason,
                )
                return ControlDecision(action=ControlAction.PAUSE, record=record)
            if record.state is ControlState.PAUSED:
                return ControlDecision(action=ControlAction.PAUSE, record=record)
            return ControlDecision(action=ControlAction.CONTINUE, record=record)

    def ensure_task(self, task_id: str) -> ControlRecord:
        return self.ensure(ControlEntityType.TASK, task_id)

    def get_task(self, task_id: str) -> ControlRecord | None:
        return self.get(ControlEntityType.TASK, task_id)

    def task_action(self, task_id: str) -> ControlAction:
        return self.checkpoint(ControlEntityType.TASK, task_id).action

    def pause_task(self, task_id: str, *, reason: str = "") -> ControlRecord:
        return self.request_pause(ControlEntityType.TASK, task_id, reason=reason)

    def resume_task(self, task_id: str) -> ControlRecord:
        return self.resume(ControlEntityType.TASK, task_id)

    def cancel_task(self, task_id: str, *, reason: str = "") -> ControlRecord:
        return self.request_cancel(ControlEntityType.TASK, task_id, reason=reason)

    def cancellation_report(self, task_id: str) -> CancellationReport | None:
        with self._lock:
            row = self.connection.execute(
                """
                SELECT reason, active_operation_kinds, owned_processes_observed,
                       owned_cancellable_operations_observed, terminate_requests,
                       kill_requests, cancellable_operation_cancel_requests,
                       processes_still_active, cancellable_operations_still_active,
                       cooperative_fallback
                FROM cancellation_reports WHERE task_id = ?
                """,
                (task_id,),
            ).fetchone()
            if row is None:
                return None
            kinds = tuple(item for item in row[1].split(",") if item)
            return CancellationReport(
                task_id=task_id,
                reason=row[0],
                active_operation_kinds=kinds,
                owned_processes_observed=row[2],
                owned_cancellable_operations_observed=row[3],
                terminate_requests=row[4],
                kill_requests=row[5],
                cancellable_operation_cancel_requests=row[6],
                processes_still_active=row[7],
                cancellable_operations_still_active=row[8],
                cooperative_fallback=bool(row[9]),
            )

    def remote_operation_disposition(
        self,
        task_id: str,
    ) -> RemoteOperationDisposition | None:
        with self._lock:
            row = self.connection.execute(
                """
                SELECT audit_ref, outcome, reason, recorded_at,
                       program_id, phase_id, slice_id, transport,
                       transport_scope, operation_ref, base_sha,
                       remote_state, remote_status, remote_revision,
                       remote_updated_at, provider_confirmed_cancelled,
                       confirmed_by_operator, provider_calls_made,
                       output_consumed, graph_resumed, program_phase_advanced
                FROM remote_operation_dispositions WHERE task_id = ?
                """,
                (task_id,),
            ).fetchone()
            if row is None:
                return None
            return RemoteOperationDisposition(
                audit_ref=row[0],
                task_id=task_id,
                outcome=RemoteOperationDispositionOutcome(row[1]),
                reason=row[2],
                recorded_at=row[3],
                program_id=row[4],
                phase_id=row[5],
                slice_id=row[6],
                transport=row[7],
                transport_scope=row[8],
                operation_ref=row[9],
                base_sha=row[10],
                remote_state=RemoteOperationState(row[11]),
                remote_status=row[12],
                remote_revision=row[13],
                remote_updated_at=row[14],
                provider_confirmed_cancelled=bool(row[15]),
                confirmed_by_operator=bool(row[16]),
                provider_calls_made=row[17],
                output_consumed=bool(row[18]),
                graph_resumed=bool(row[19]),
                program_phase_advanced=bool(row[20]),
            )

    def record_remote_operation_disposition(
        self,
        snapshot: RemoteOperationSnapshot,
        outcome: RemoteOperationDispositionOutcome,
        *,
        reason: str,
        confirmed: bool,
        program_id: str = "",
        phase_id: str = "",
        slice_id: str = "",
    ) -> RemoteOperationDisposition:
        """Close orphaned local task state without invoking the remote provider."""

        if not confirmed:
            raise ValueError("remote-operation disposition requires explicit confirmation")
        normalized_reason = reason.strip()
        if not normalized_reason:
            raise ValueError("remote-operation disposition requires a reason")
        if len(normalized_reason) > 2000:
            raise ValueError("remote-operation disposition reason is too long")
        if snapshot.state is RemoteOperationState.ACTIVE:
            raise ValueError("an active remote-operation lease cannot be disposed")

        with self._lock:
            existing = self.remote_operation_disposition(snapshot.task_id)
            if existing is not None:
                if _same_disposition_request(
                    existing,
                    snapshot=snapshot,
                    outcome=outcome,
                    reason=normalized_reason,
                    program_id=program_id,
                    phase_id=phase_id,
                    slice_id=slice_id,
                ):
                    return existing
                raise ValueError("remote-operation disposition is immutable")

            control = self.ensure_task(snapshot.task_id)
            target_state = (
                ControlState.CANCELLED
                if outcome is RemoteOperationDispositionOutcome.CANCELLED
                else ControlState.FAILED
            )
            if control.state is ControlState.COMPLETED:
                raise ValueError("completed task state cannot be replaced by a disposition")
            if control.state in {ControlState.CANCELLED, ControlState.FAILED}:
                if control.state is not target_state:
                    raise ValueError("terminal task state conflicts with disposition outcome")

            recorded_at = datetime.now(UTC).isoformat()
            payload = {
                "schema_version": "1",
                "task_id": snapshot.task_id,
                "outcome": outcome.value,
                "reason": normalized_reason,
                "recorded_at": recorded_at,
                "program_id": program_id,
                "phase_id": phase_id,
                "slice_id": slice_id,
                "transport": snapshot.transport,
                "transport_scope": snapshot.transport_scope,
                "operation_ref": snapshot.operation_ref,
                "base_sha": snapshot.base_sha,
                "remote_state": snapshot.state.value,
                "remote_status": snapshot.last_status,
                "remote_revision": snapshot.revision,
                "remote_updated_at": snapshot.updated_at,
                "provider_confirmed_cancelled": bool(
                    snapshot.state is RemoteOperationState.TERMINAL
                    and snapshot.last_status == "cancelled"
                ),
                "confirmed_by_operator": True,
                "provider_calls_made": 0,
                "output_consumed": False,
                "graph_resumed": False,
                "program_phase_advanced": False,
            }
            audit_ref = _audit_ref(payload)
            disposition = RemoteOperationDisposition(
                audit_ref=audit_ref,
                **payload,
            )
            self.connection.execute(
                """
                INSERT INTO remote_operation_dispositions(
                    task_id, audit_ref, outcome, reason, recorded_at,
                    program_id, phase_id, slice_id, transport,
                    transport_scope, operation_ref, base_sha,
                    remote_state, remote_status, remote_revision,
                    remote_updated_at, provider_confirmed_cancelled,
                    confirmed_by_operator, provider_calls_made,
                    output_consumed, graph_resumed, program_phase_advanced
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    disposition.task_id,
                    disposition.audit_ref,
                    disposition.outcome.value,
                    disposition.reason,
                    disposition.recorded_at,
                    disposition.program_id,
                    disposition.phase_id,
                    disposition.slice_id,
                    disposition.transport,
                    disposition.transport_scope,
                    disposition.operation_ref,
                    disposition.base_sha,
                    disposition.remote_state.value,
                    disposition.remote_status,
                    disposition.remote_revision,
                    disposition.remote_updated_at,
                    int(disposition.provider_confirmed_cancelled),
                    int(disposition.confirmed_by_operator),
                    disposition.provider_calls_made,
                    int(disposition.output_consumed),
                    int(disposition.graph_resumed),
                    int(disposition.program_phase_advanced),
                ),
            )
            self.connection.execute(
                """
                UPDATE control_state
                SET state = ?, reason = ?, revision = ?
                WHERE entity_type = ? AND entity_id = ?
                """,
                (
                    target_state.value,
                    normalized_reason,
                    control.revision + 1,
                    ControlEntityType.TASK.value,
                    snapshot.task_id,
                ),
            )
            self.connection.commit()
            return self.remote_operation_disposition(snapshot.task_id) or disposition

    def complete_task(self, task_id: str) -> ControlRecord:
        return self.mark_completed(ControlEntityType.TASK, task_id)

    def mark_completed(
        self,
        entity_type: ControlEntityType,
        entity_id: str,
    ) -> ControlRecord:
        with self._lock:
            record = self.ensure(entity_type, entity_id)
            if record.state in {ControlState.CANCELLED, ControlState.FAILED}:
                return record
            return self._set(entity_type, entity_id, ControlState.COMPLETED, "")

    def _set(
        self,
        entity_type: ControlEntityType,
        entity_id: str,
        state: ControlState,
        reason: str,
    ) -> ControlRecord:
        with self._lock:
            record = self.ensure(entity_type, entity_id)
            self.connection.execute(
                """
                UPDATE control_state
                SET state = ?, reason = ?, revision = ?
                WHERE entity_type = ? AND entity_id = ?
                """,
                (
                    state.value,
                    reason[:2000],
                    record.revision + 1,
                    entity_type.value,
                    entity_id,
                ),
            )
            self.connection.commit()
            return self.get_required(entity_type, entity_id)

    def _store_cancellation_report(self, report: CancellationReport) -> None:
        with self._lock:
            self.connection.execute(
                """
                INSERT OR REPLACE INTO cancellation_reports(
                    task_id, reason, active_operation_kinds,
                    owned_processes_observed, owned_cancellable_operations_observed,
                    terminate_requests, kill_requests,
                    cancellable_operation_cancel_requests, processes_still_active,
                    cancellable_operations_still_active, cooperative_fallback
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    report.task_id,
                    report.reason,
                    ",".join(report.active_operation_kinds),
                    report.owned_processes_observed,
                    report.owned_cancellable_operations_observed,
                    report.terminate_requests,
                    report.kill_requests,
                    report.cancellable_operation_cancel_requests,
                    report.processes_still_active,
                    report.cancellable_operations_still_active,
                    int(report.cooperative_fallback),
                ),
            )
            self.connection.commit()

    def _ensure_cancellation_report_columns(self) -> None:
        existing = {
            str(row[1])
            for row in self.connection.execute(
                "PRAGMA table_info(cancellation_reports)"
            ).fetchall()
        }
        additions = {
            "owned_cancellable_operations_observed": "INTEGER NOT NULL DEFAULT 0",
            "cancellable_operation_cancel_requests": "INTEGER NOT NULL DEFAULT 0",
            "cancellable_operations_still_active": "INTEGER NOT NULL DEFAULT 0",
        }
        for name, declaration in additions.items():
            if name not in existing:
                self.connection.execute(
                    f"ALTER TABLE cancellation_reports ADD COLUMN {name} {declaration}"
                )


def _audit_ref(payload: dict[str, object]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _same_disposition_request(
    existing: RemoteOperationDisposition,
    *,
    snapshot: RemoteOperationSnapshot,
    outcome: RemoteOperationDispositionOutcome,
    reason: str,
    program_id: str,
    phase_id: str,
    slice_id: str,
) -> bool:
    return (
        existing.task_id == snapshot.task_id
        and existing.outcome is outcome
        and existing.reason == reason
        and existing.program_id == program_id
        and existing.phase_id == phase_id
        and existing.slice_id == slice_id
        and existing.transport == snapshot.transport
        and existing.transport_scope == snapshot.transport_scope
        and existing.operation_ref == snapshot.operation_ref
        and existing.base_sha == snapshot.base_sha
        and existing.remote_state is snapshot.state
        and existing.remote_status == snapshot.last_status
        and existing.remote_revision == snapshot.revision
        and existing.remote_updated_at == snapshot.updated_at
    )
