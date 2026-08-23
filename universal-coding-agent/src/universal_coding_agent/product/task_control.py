from __future__ import annotations

import sqlite3
from pathlib import Path
from threading import RLock

from universal_coding_agent.core.cancellation import (
    CancellationCoordinator,
    CancellationReport,
)
from universal_coding_agent.product.models import (
    ControlAction,
    ControlDecision,
    ControlEntityType,
    ControlRecord,
    ControlState,
)


class TaskControlService:
    """Persistent cooperative pause/resume/cancel state.

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
                terminate_requests INTEGER NOT NULL,
                kill_requests INTEGER NOT NULL,
                processes_still_active INTEGER NOT NULL,
                cooperative_fallback INTEGER NOT NULL
            )
            """
        )
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
            if record.state in {ControlState.CANCELLED, ControlState.COMPLETED}:
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
            if record.state in {ControlState.CANCELLED, ControlState.COMPLETED}:
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
                       terminate_requests, kill_requests, processes_still_active,
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
                terminate_requests=row[3],
                kill_requests=row[4],
                processes_still_active=row[5],
                cooperative_fallback=bool(row[6]),
            )

    def complete_task(self, task_id: str) -> ControlRecord:
        return self.mark_completed(ControlEntityType.TASK, task_id)

    def mark_completed(
        self,
        entity_type: ControlEntityType,
        entity_id: str,
    ) -> ControlRecord:
        with self._lock:
            record = self.ensure(entity_type, entity_id)
            if record.state is ControlState.CANCELLED:
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
                    owned_processes_observed, terminate_requests, kill_requests,
                    processes_still_active, cooperative_fallback
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    report.task_id,
                    report.reason,
                    ",".join(report.active_operation_kinds),
                    report.owned_processes_observed,
                    report.terminate_requests,
                    report.kill_requests,
                    report.processes_still_active,
                    int(report.cooperative_fallback),
                ),
            )
            self.connection.commit()
