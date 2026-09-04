from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from threading import RLock

from universal_coding_agent.core.remote_operations import (
    PrivateRemoteOperationLease,
    RemoteOperationAction,
    RemoteOperationDisposition,
    RemoteOperationDispositionOutcome,
    RemoteOperationLeaseRetirement,
    RemoteOperationLeaseStore,
    RemoteOperationSnapshot,
    RemoteOperationState,
)

_TASK_ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")
_TRANSPORT = re.compile(r"^[a-z][a-z0-9._-]{2,63}$")


@dataclass(frozen=True)
class RetainedRemoteOperationLeaseEvidence:
    """Identifier-free fields needed to preview one existing retirement action."""

    task_id: str
    transport: str
    transport_scope: str
    operation_ref: str
    base_sha: str
    updated_at: str
    last_status: str
    state: RemoteOperationState
    revision: int
    retirement_present: bool


class SqliteRemoteOperationLeaseStore:
    """Private storage for opaque remote-operation identifiers.

    The database is deliberately separate from task-control, artifacts, and public product
    state. Only identifier-free snapshots may leave this service.
    """

    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path.resolve()
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.database_path.touch(mode=0o600, exist_ok=True)
        try:
            os.chmod(self.database_path, 0o600)
        except OSError:
            pass
        self._lock = RLock()
        self.connection = sqlite3.connect(self.database_path, check_same_thread=False)
        self.connection.execute("PRAGMA secure_delete = ON")
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS remote_operation_leases (
                task_id TEXT PRIMARY KEY,
                thread_id TEXT NOT NULL,
                transport TEXT NOT NULL,
                transport_scope TEXT NOT NULL,
                operation_id TEXT NOT NULL,
                operation_ref TEXT NOT NULL,
                base_sha TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                last_status TEXT NOT NULL,
                state TEXT NOT NULL,
                cancellation_requested INTEGER NOT NULL,
                revision INTEGER NOT NULL,
                reconciliation_attempts INTEGER NOT NULL,
                cancel_requests INTEGER NOT NULL,
                last_action TEXT NOT NULL
            )
            """
        )
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS remote_operation_lease_retirements (
                task_id TEXT PRIMARY KEY,
                retirement_ref TEXT NOT NULL UNIQUE,
                disposition_audit_ref TEXT NOT NULL UNIQUE,
                disposition_outcome TEXT NOT NULL,
                program_id TEXT NOT NULL,
                phase_id TEXT NOT NULL,
                slice_id TEXT NOT NULL,
                reason TEXT NOT NULL,
                retired_at TEXT NOT NULL,
                transport TEXT NOT NULL,
                transport_scope TEXT NOT NULL,
                operation_ref TEXT NOT NULL,
                base_sha TEXT NOT NULL,
                remote_state TEXT NOT NULL,
                remote_status TEXT NOT NULL,
                remote_revision INTEGER NOT NULL,
                remote_updated_at TEXT NOT NULL,
                confirmed_by_operator INTEGER NOT NULL,
                private_lease_rows_retired INTEGER NOT NULL,
                private_identifier_retained_in_active_store INTEGER NOT NULL,
                provider_calls_made INTEGER NOT NULL,
                output_consumed INTEGER NOT NULL,
                graph_resumed INTEGER NOT NULL,
                task_outcome_changes_made INTEGER NOT NULL,
                program_outcome_changes_made INTEGER NOT NULL,
                program_phase_advanced INTEGER NOT NULL
            )
            """
        )
        self.connection.execute(
            """
            CREATE TRIGGER IF NOT EXISTS reject_retired_remote_operation_lease
            BEFORE INSERT ON remote_operation_leases
            WHEN EXISTS (
                SELECT 1 FROM remote_operation_lease_retirements
                WHERE task_id = NEW.task_id
            )
            BEGIN
                SELECT RAISE(ABORT, 'retired remote-operation task identity cannot be reused');
            END
            """
        )
        self.connection.commit()

    def close(self) -> None:
        with self._lock:
            self.connection.close()

    def provider_store(self) -> RemoteOperationLeaseStore:
        """Return a provider-facing view without operator retirement authority."""

        return _ProviderRemoteOperationLeaseStore(self)

    def register(
        self,
        *,
        task_id: str,
        thread_id: str,
        transport: str,
        transport_scope: str,
        operation_id: str,
        base_sha: str,
        status: str,
        state: RemoteOperationState,
    ) -> PrivateRemoteOperationLease:
        self._validate_identity(
            task_id=task_id,
            thread_id=thread_id,
            transport=transport,
            transport_scope=transport_scope,
            operation_id=operation_id,
            base_sha=base_sha,
            status=status,
        )
        operation_ref = _operation_ref(operation_id)
        now = _utc_now()
        with self._lock:
            if self.retirement(task_id) is not None:
                raise ValueError("retired remote-operation task identity cannot be reused")
            current = self.private_lease(task_id)
            if current is not None and current.state is RemoteOperationState.ACTIVE:
                if (
                    current.transport != transport
                    or current.transport_scope != transport_scope
                    or current.operation_id != operation_id
                    or current.base_sha != base_sha
                    or current.thread_id != thread_id
                ):
                    raise ValueError(
                        "task already has a different active remote-operation lease"
                    )
                return self.record_status(task_id, status=status, state=state)
            self.connection.execute(
                """
                INSERT OR REPLACE INTO remote_operation_leases(
                    task_id, thread_id, transport, transport_scope,
                    operation_id, operation_ref,
                    base_sha, created_at, updated_at, last_status, state,
                    cancellation_requested, revision, reconciliation_attempts,
                    cancel_requests, last_action
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 0, 0, '')
                """,
                (
                    task_id,
                    thread_id,
                    transport,
                    transport_scope,
                    operation_id,
                    operation_ref,
                    base_sha,
                    now,
                    now,
                    status,
                    state.value,
                ),
            )
            self.connection.commit()
            return self.private_lease_required(task_id)

    def private_lease(self, task_id: str) -> PrivateRemoteOperationLease | None:
        with self._lock:
            row = self.connection.execute(
                """
                SELECT thread_id, transport, transport_scope, operation_id,
                       operation_ref, base_sha,
                       created_at, updated_at, last_status, state,
                       cancellation_requested, revision, reconciliation_attempts,
                       cancel_requests, last_action
                FROM remote_operation_leases WHERE task_id = ?
                """,
                (task_id,),
            ).fetchone()
            if row is None:
                return None
            return PrivateRemoteOperationLease(
                task_id=task_id,
                thread_id=row[0],
                transport=row[1],
                transport_scope=row[2],
                operation_id=row[3],
                operation_ref=row[4],
                base_sha=row[5],
                created_at=row[6],
                updated_at=row[7],
                last_status=row[8],
                state=RemoteOperationState(row[9]),
                cancellation_requested=bool(row[10]),
                revision=row[11],
                reconciliation_attempts=row[12],
                cancel_requests=row[13],
                last_action=(RemoteOperationAction(row[14]) if row[14] else None),
            )

    def private_lease_required(self, task_id: str) -> PrivateRemoteOperationLease:
        lease = self.private_lease(task_id)
        if lease is None:
            raise KeyError(task_id)
        return lease

    def public_snapshot(self, task_id: str) -> RemoteOperationSnapshot | None:
        lease = self.private_lease(task_id)
        if lease is None:
            return None
        return RemoteOperationSnapshot(
            task_id=lease.task_id,
            thread_id=lease.thread_id,
            transport=lease.transport,
            transport_scope=lease.transport_scope,
            operation_ref=lease.operation_ref,
            base_sha=lease.base_sha,
            created_at=lease.created_at,
            updated_at=lease.updated_at,
            last_status=lease.last_status,
            state=lease.state,
            cancellation_requested=lease.cancellation_requested,
            revision=lease.revision,
            reconciliation_attempts=lease.reconciliation_attempts,
            cancel_requests=lease.cancel_requests,
            last_action=lease.last_action,
        )

    def retained_lease_page(
        self,
        *,
        after_task_id: str = "",
        limit: int = 26,
    ) -> tuple[RetainedRemoteOperationLeaseEvidence, ...]:
        """Read one bounded keyset page without selecting the opaque identifier."""

        if after_task_id and _TASK_ID.fullmatch(after_task_id) is None:
            raise ValueError("retained lease inventory cursor is invalid")
        if limit < 1 or limit > 101:
            raise ValueError("retained lease inventory limit must be between 1 and 101")
        with self._lock:
            rows = self.connection.execute(
                """
                SELECT leases.task_id, leases.transport, leases.transport_scope,
                       leases.operation_ref, leases.base_sha, leases.updated_at,
                       leases.last_status, leases.state, leases.revision,
                       CASE WHEN retirements.task_id IS NULL THEN 0 ELSE 1 END
                FROM remote_operation_leases AS leases
                LEFT JOIN remote_operation_lease_retirements AS retirements
                  ON retirements.task_id = leases.task_id
                WHERE leases.task_id COLLATE BINARY > ?
                ORDER BY leases.task_id COLLATE BINARY
                LIMIT ?
                """,
                (after_task_id, limit),
            ).fetchall()
        return tuple(
            RetainedRemoteOperationLeaseEvidence(
                task_id=row[0],
                transport=row[1],
                transport_scope=row[2],
                operation_ref=row[3],
                base_sha=row[4],
                updated_at=row[5],
                last_status=row[6],
                state=RemoteOperationState(row[7]),
                revision=row[8],
                retirement_present=bool(row[9]),
            )
            for row in rows
        )

    def retirement(
        self,
        task_id: str,
    ) -> RemoteOperationLeaseRetirement | None:
        with self._lock:
            row = self.connection.execute(
                """
                SELECT retirement_ref, disposition_audit_ref, disposition_outcome,
                       program_id, phase_id, slice_id, reason, retired_at,
                       transport, transport_scope, operation_ref, base_sha,
                       remote_state, remote_status, remote_revision, remote_updated_at,
                       confirmed_by_operator, private_lease_rows_retired,
                       private_identifier_retained_in_active_store,
                       provider_calls_made, output_consumed, graph_resumed,
                       task_outcome_changes_made, program_outcome_changes_made,
                       program_phase_advanced
                FROM remote_operation_lease_retirements WHERE task_id = ?
                """,
                (task_id,),
            ).fetchone()
            if row is None:
                return None
            retirement = RemoteOperationLeaseRetirement(
                retirement_ref=row[0],
                task_id=task_id,
                disposition_audit_ref=row[1],
                disposition_outcome=RemoteOperationDispositionOutcome(row[2]),
                program_id=row[3],
                phase_id=row[4],
                slice_id=row[5],
                reason=row[6],
                retired_at=row[7],
                transport=row[8],
                transport_scope=row[9],
                operation_ref=row[10],
                base_sha=row[11],
                remote_state=RemoteOperationState(row[12]),
                remote_status=row[13],
                remote_revision=row[14],
                remote_updated_at=row[15],
                confirmed_by_operator=bool(row[16]),
                private_lease_rows_retired=row[17],
                private_identifier_retained_in_active_store=bool(row[18]),
                provider_calls_made=row[19],
                output_consumed=bool(row[20]),
                graph_resumed=bool(row[21]),
                task_outcome_changes_made=row[22],
                program_outcome_changes_made=row[23],
                program_phase_advanced=bool(row[24]),
            )
            _validate_retirement_ref(retirement)
            return retirement

    def retire(
        self,
        disposition: RemoteOperationDisposition,
        *,
        reason: str,
        confirmed: bool,
    ) -> RemoteOperationLeaseRetirement:
        """Atomically retain a redacted tombstone and delete one opaque lease row."""

        if not confirmed:
            raise ValueError("private lease retirement requires explicit confirmation")
        normalized_reason = reason.strip()
        if not normalized_reason:
            raise ValueError("private lease retirement requires a reason")
        if len(normalized_reason) > 2000:
            raise ValueError("private lease retirement reason is too long")
        validate_remote_operation_disposition(disposition)

        with self._lock:
            self.connection.execute("BEGIN IMMEDIATE")
            try:
                existing = self.retirement(disposition.task_id)
                current = self.private_lease(disposition.task_id)
                if existing is not None:
                    if current is not None:
                        raise ValueError(
                            "retired task unexpectedly retains a private lease"
                        )
                    if _same_retirement_request(
                        existing,
                        disposition=disposition,
                        reason=normalized_reason,
                    ):
                        self.connection.commit()
                        return existing
                    raise ValueError("private lease retirement receipt is immutable")
                if current is None:
                    raise ValueError("task has no private remote-operation lease to retire")
                _validate_retirement_binding(current, disposition)

                retired_at = _utc_now()
                payload = {
                    "schema_version": "1",
                    "task_id": disposition.task_id,
                    "disposition_audit_ref": disposition.audit_ref,
                    "disposition_outcome": disposition.outcome.value,
                    "program_id": disposition.program_id,
                    "phase_id": disposition.phase_id,
                    "slice_id": disposition.slice_id,
                    "reason": normalized_reason,
                    "retired_at": retired_at,
                    "transport": disposition.transport,
                    "transport_scope": disposition.transport_scope,
                    "operation_ref": disposition.operation_ref,
                    "base_sha": disposition.base_sha,
                    "remote_state": disposition.remote_state.value,
                    "remote_status": disposition.remote_status,
                    "remote_revision": disposition.remote_revision,
                    "remote_updated_at": disposition.remote_updated_at,
                    "confirmed_by_operator": True,
                    "private_lease_rows_retired": 1,
                    "private_identifier_retained_in_active_store": False,
                    "provider_calls_made": 0,
                    "output_consumed": False,
                    "graph_resumed": False,
                    "task_outcome_changes_made": 0,
                    "program_outcome_changes_made": 0,
                    "program_phase_advanced": False,
                }
                retirement = RemoteOperationLeaseRetirement(
                    retirement_ref=_retirement_ref(payload),
                    **payload,
                )
                self.connection.execute(
                    """
                    INSERT INTO remote_operation_lease_retirements(
                        task_id, retirement_ref, disposition_audit_ref,
                        disposition_outcome, program_id, phase_id, slice_id, reason,
                        retired_at, transport, transport_scope, operation_ref,
                        base_sha, remote_state, remote_status, remote_revision,
                        remote_updated_at, confirmed_by_operator,
                        private_lease_rows_retired,
                        private_identifier_retained_in_active_store,
                        provider_calls_made, output_consumed, graph_resumed,
                        task_outcome_changes_made, program_outcome_changes_made,
                        program_phase_advanced
                    ) VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                    )
                    """,
                    (
                        retirement.task_id,
                        retirement.retirement_ref,
                        retirement.disposition_audit_ref,
                        retirement.disposition_outcome.value,
                        retirement.program_id,
                        retirement.phase_id,
                        retirement.slice_id,
                        retirement.reason,
                        retirement.retired_at,
                        retirement.transport,
                        retirement.transport_scope,
                        retirement.operation_ref,
                        retirement.base_sha,
                        retirement.remote_state.value,
                        retirement.remote_status,
                        retirement.remote_revision,
                        retirement.remote_updated_at,
                        int(retirement.confirmed_by_operator),
                        retirement.private_lease_rows_retired,
                        int(retirement.private_identifier_retained_in_active_store),
                        retirement.provider_calls_made,
                        int(retirement.output_consumed),
                        int(retirement.graph_resumed),
                        retirement.task_outcome_changes_made,
                        retirement.program_outcome_changes_made,
                        int(retirement.program_phase_advanced),
                    ),
                )
                deleted = self.connection.execute(
                    """
                    DELETE FROM remote_operation_leases
                    WHERE task_id = ? AND operation_ref = ? AND revision = ? AND state = ?
                    """,
                    (
                        disposition.task_id,
                        disposition.operation_ref,
                        disposition.remote_revision,
                        disposition.remote_state.value,
                    ),
                )
                if deleted.rowcount != 1:
                    raise ValueError("private lease retirement did not delete exactly one row")
                self.connection.commit()
                return retirement
            except BaseException:
                self.connection.rollback()
                raise

    def record_action(
        self,
        task_id: str,
        action: RemoteOperationAction,
        *,
        reconciliation: bool,
    ) -> PrivateRemoteOperationLease:
        with self._lock:
            current = self.private_lease_required(task_id)
            if current.state is not RemoteOperationState.ACTIVE:
                return current
            cancel_increment = int(action is RemoteOperationAction.CANCEL)
            reconciliation_increment = int(reconciliation)
            self.connection.execute(
                """
                UPDATE remote_operation_leases
                SET cancellation_requested = CASE WHEN ? THEN 1
                                                   ELSE cancellation_requested END,
                    revision = revision + 1,
                    reconciliation_attempts = reconciliation_attempts + ?,
                    cancel_requests = cancel_requests + ?,
                    last_action = ?,
                    updated_at = ?
                WHERE task_id = ?
                """,
                (
                    cancel_increment,
                    reconciliation_increment,
                    cancel_increment,
                    action.value,
                    _utc_now(),
                    task_id,
                ),
            )
            self.connection.commit()
            return self.private_lease_required(task_id)

    def record_status(
        self,
        task_id: str,
        *,
        status: str,
        state: RemoteOperationState,
    ) -> PrivateRemoteOperationLease:
        if not status or len(status) > 64:
            raise ValueError("remote-operation status must contain 1 to 64 characters")
        with self._lock:
            current = self.private_lease_required(task_id)
            if current.state is not RemoteOperationState.ACTIVE:
                return current
            self.connection.execute(
                """
                UPDATE remote_operation_leases
                SET last_status = ?, state = ?, revision = revision + 1, updated_at = ?
                WHERE task_id = ?
                """,
                (status, state.value, _utc_now(), task_id),
            )
            self.connection.commit()
            return self.private_lease_required(task_id)

    def mark_unavailable(
        self,
        task_id: str,
        *,
        status: str = "remote_state_unavailable",
    ) -> PrivateRemoteOperationLease:
        return self.record_status(
            task_id,
            status=status,
            state=RemoteOperationState.UNAVAILABLE,
        )

    @staticmethod
    def _validate_identity(
        *,
        task_id: str,
        thread_id: str,
        transport: str,
        transport_scope: str,
        operation_id: str,
        base_sha: str,
        status: str,
    ) -> None:
        if _TASK_ID.fullmatch(task_id) is None:
            raise ValueError("task_id is invalid for private remote-operation persistence")
        if thread_id and _TASK_ID.fullmatch(thread_id) is None:
            raise ValueError("thread_id is invalid for private remote-operation persistence")
        if _TRANSPORT.fullmatch(transport) is None:
            raise ValueError("transport is invalid for private remote-operation persistence")
        if not (
            len(transport_scope) == 71
            and transport_scope.startswith("sha256:")
            and all(char in "0123456789abcdef" for char in transport_scope[7:])
        ):
            raise ValueError("transport_scope must be a SHA-256 reference")
        if not operation_id or len(operation_id) > 1024:
            raise ValueError("remote-operation identifier must contain 1 to 1024 characters")
        if base_sha and (
            len(base_sha) not in range(40, 65)
            or any(char not in "0123456789abcdef" for char in base_sha)
        ):
            raise ValueError("base_sha must be an immutable hexadecimal Git object ID")
        if not status or len(status) > 64:
            raise ValueError("remote-operation status must contain 1 to 64 characters")


class _ProviderRemoteOperationLeaseStore:
    """Narrow provider capability for lease lifecycle persistence and reconciliation."""

    __slots__ = ("__store",)

    def __init__(self, store: SqliteRemoteOperationLeaseStore) -> None:
        self.__store = store

    def register(
        self,
        *,
        task_id: str,
        thread_id: str,
        transport: str,
        transport_scope: str,
        operation_id: str,
        base_sha: str,
        status: str,
        state: RemoteOperationState,
    ) -> PrivateRemoteOperationLease:
        return self.__store.register(
            task_id=task_id,
            thread_id=thread_id,
            transport=transport,
            transport_scope=transport_scope,
            operation_id=operation_id,
            base_sha=base_sha,
            status=status,
            state=state,
        )

    def private_lease(self, task_id: str) -> PrivateRemoteOperationLease | None:
        return self.__store.private_lease(task_id)

    def public_snapshot(self, task_id: str) -> RemoteOperationSnapshot | None:
        return self.__store.public_snapshot(task_id)

    def record_action(
        self,
        task_id: str,
        action: RemoteOperationAction,
        *,
        reconciliation: bool,
    ) -> PrivateRemoteOperationLease:
        return self.__store.record_action(
            task_id,
            action,
            reconciliation=reconciliation,
        )

    def record_status(
        self,
        task_id: str,
        *,
        status: str,
        state: RemoteOperationState,
    ) -> PrivateRemoteOperationLease:
        return self.__store.record_status(task_id, status=status, state=state)

    def mark_unavailable(
        self,
        task_id: str,
        *,
        status: str = "remote_state_unavailable",
    ) -> PrivateRemoteOperationLease:
        return self.__store.mark_unavailable(task_id, status=status)


def _operation_ref(operation_id: str) -> str:
    return "sha256:" + hashlib.sha256(operation_id.encode("utf-8")).hexdigest()


def _retirement_ref(payload: dict[str, object]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _validate_retirement_binding(
    lease: PrivateRemoteOperationLease,
    disposition: RemoteOperationDisposition,
) -> None:
    if lease.state is RemoteOperationState.ACTIVE:
        raise ValueError("an active private remote-operation lease cannot be retired")
    if not retained_lease_matches_disposition(lease, disposition):
        raise ValueError("private lease does not match the durable disposition")


def _same_retirement_request(
    existing: RemoteOperationLeaseRetirement,
    *,
    disposition: RemoteOperationDisposition,
    reason: str,
) -> bool:
    return (
        existing.task_id == disposition.task_id
        and existing.disposition_audit_ref == disposition.audit_ref
        and existing.disposition_outcome is disposition.outcome
        and existing.program_id == disposition.program_id
        and existing.phase_id == disposition.phase_id
        and existing.slice_id == disposition.slice_id
        and existing.reason == reason
        and existing.transport == disposition.transport
        and existing.transport_scope == disposition.transport_scope
        and existing.operation_ref == disposition.operation_ref
        and existing.base_sha == disposition.base_sha
        and existing.remote_state is disposition.remote_state
        and existing.remote_status == disposition.remote_status
        and existing.remote_revision == disposition.remote_revision
        and existing.remote_updated_at == disposition.remote_updated_at
    )


def retained_lease_matches_disposition(
    lease: PrivateRemoteOperationLease | RetainedRemoteOperationLeaseEvidence,
    disposition: RemoteOperationDisposition,
) -> bool:
    return bool(
        lease.task_id == disposition.task_id
        and lease.transport == disposition.transport
        and lease.transport_scope == disposition.transport_scope
        and lease.operation_ref == disposition.operation_ref
        and lease.base_sha == disposition.base_sha
        and lease.state is disposition.remote_state
        and lease.last_status == disposition.remote_status
        and lease.revision == disposition.remote_revision
        and lease.updated_at == disposition.remote_updated_at
    )


def validate_remote_operation_disposition(
    disposition: RemoteOperationDisposition,
) -> None:
    """Recompute the canonical redacted audit reference before trusting a reload."""

    payload = disposition.model_dump(mode="json", exclude={"audit_ref"})
    if _retirement_ref(payload) != disposition.audit_ref:
        raise ValueError("durable remote disposition audit reference is invalid")


def _validate_retirement_ref(retirement: RemoteOperationLeaseRetirement) -> None:
    payload = retirement.model_dump(mode="json", exclude={"retirement_ref"})
    if _retirement_ref(payload) != retirement.retirement_ref:
        raise ValueError("durable private lease retirement reference is invalid")


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()
