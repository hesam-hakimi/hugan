from __future__ import annotations

import hashlib
import os
import re
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from threading import RLock

from universal_coding_agent.core.remote_operations import (
    PrivateRemoteOperationLease,
    RemoteOperationAction,
    RemoteOperationSnapshot,
    RemoteOperationState,
)

_TASK_ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")
_TRANSPORT = re.compile(r"^[a-z][a-z0-9._-]{2,63}$")


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
        self.connection.commit()

    def close(self) -> None:
        with self._lock:
            self.connection.close()

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


def _operation_ref(operation_id: str) -> str:
    return "sha256:" + hashlib.sha256(operation_id.encode("utf-8")).hexdigest()


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()
