from __future__ import annotations

import os
import re
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from threading import RLock

_IDENTITY = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")
_OWNER_TOKEN = re.compile(r"^[0-9a-f]{32}$")
_KINDS = frozenset({"remote_operation", "program_control"})


@dataclass(frozen=True)
class LifecycleReservationSnapshot:
    remote_task_ids: frozenset[str]
    program_ids: frozenset[str]


class DurableLifecycleReservationStore:
    """Fail-closed cross-runtime serialization for local lifecycle actions.

    Rows contain only local Task/Program identity and an unexposed random ownership
    token. A row deliberately survives an interrupted process; P1.2m adds no TTL or
    automatic recovery policy that could silently weaken the reservation.
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
        self.connection = sqlite3.connect(
            self.database_path,
            check_same_thread=False,
            isolation_level=None,
        )
        self.connection.execute("PRAGMA busy_timeout = 5000")
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS lifecycle_reservations (
                reservation_kind TEXT NOT NULL,
                scope_id TEXT NOT NULL,
                task_id TEXT NOT NULL,
                program_id TEXT NOT NULL,
                owner_token TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL,
                PRIMARY KEY (reservation_kind, scope_id),
                CHECK (reservation_kind IN ('remote_operation', 'program_control')),
                CHECK (
                    (reservation_kind = 'remote_operation'
                     AND task_id = scope_id)
                    OR
                    (reservation_kind = 'program_control'
                     AND program_id = scope_id AND task_id = '')
                )
            )
            """
        )
        self.connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS one_remote_reservation_per_task
            ON lifecycle_reservations(task_id)
            WHERE reservation_kind = 'remote_operation'
            """
        )
        self.connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS one_control_reservation_per_program
            ON lifecycle_reservations(program_id)
            WHERE reservation_kind = 'program_control'
            """
        )

    def close(self) -> None:
        with self._lock:
            self.connection.close()

    def reserve_remote_operation(self, task_id: str, *, program_id: str = "") -> str:
        self._validate_identity(task_id, "task_id")
        if program_id:
            self._validate_identity(program_id, "program_id")
        owner_token = uuid.uuid4().hex
        with self._transaction():
            rows = self.connection.execute(
                """
                SELECT reservation_kind, scope_id, task_id, program_id,
                       owner_token, created_at
                FROM lifecycle_reservations
                WHERE (reservation_kind = 'remote_operation' AND task_id = ?)
                   OR (? != '' AND reservation_kind = 'program_control'
                                  AND program_id = ?)
                """,
                (task_id, program_id, program_id),
            ).fetchall()
            self._validate_rows(rows)
            if any(row[0] == "remote_operation" for row in rows):
                raise ValueError("remote-operation lifecycle action is already active")
            if rows:
                raise ValueError("Program control action is already active")
            self.connection.execute(
                """
                INSERT INTO lifecycle_reservations(
                    reservation_kind, scope_id, task_id, program_id,
                    owner_token, created_at
                ) VALUES ('remote_operation', ?, ?, ?, ?, ?)
                """,
                (task_id, task_id, program_id, owner_token, _utc_now()),
            )
        return owner_token

    def reserve_program_control(
        self,
        program_id: str,
        *,
        task_ids: tuple[str, ...],
    ) -> str:
        self._validate_identity(program_id, "program_id")
        if len(set(task_ids)) != len(task_ids):
            raise ValueError("Program lifecycle reservation has duplicate Task identity")
        for task_id in task_ids:
            self._validate_identity(task_id, "task_id")
        owner_token = uuid.uuid4().hex
        with self._transaction():
            clauses = [
                "(reservation_kind = 'program_control' AND program_id = ?)",
                "(reservation_kind = 'remote_operation' AND program_id = ?)",
            ]
            parameters: list[str] = [program_id, program_id]
            if task_ids:
                placeholders = ", ".join("?" for _ in task_ids)
                clauses.append(
                    f"(reservation_kind = 'remote_operation' AND task_id IN ({placeholders}))"
                )
                parameters.extend(task_ids)
            rows = self.connection.execute(
                """
                SELECT reservation_kind, scope_id, task_id, program_id,
                       owner_token, created_at
                FROM lifecycle_reservations
                WHERE """
                + " OR ".join(clauses),
                tuple(parameters),
            ).fetchall()
            self._validate_rows(rows)
            if any(row[0] == "program_control" for row in rows):
                raise ValueError("Program control action is already active")
            if rows:
                raise ValueError("remote-operation lifecycle action is active")
            self.connection.execute(
                """
                INSERT INTO lifecycle_reservations(
                    reservation_kind, scope_id, task_id, program_id,
                    owner_token, created_at
                ) VALUES ('program_control', ?, '', ?, ?, ?)
                """,
                (program_id, program_id, owner_token, _utc_now()),
            )
        return owner_token

    def release_remote_operation(self, task_id: str, owner_token: str) -> None:
        self._release("remote_operation", task_id, owner_token)

    def release_program_control(self, program_id: str, owner_token: str) -> None:
        self._release("program_control", program_id, owner_token)

    def snapshot(self) -> LifecycleReservationSnapshot:
        with self._lock:
            try:
                rows = self.connection.execute(
                    """
                    SELECT reservation_kind, scope_id, task_id, program_id,
                           owner_token, created_at
                    FROM lifecycle_reservations
                    """
                ).fetchall()
                self._validate_rows(rows)
            except (sqlite3.DatabaseError, ValueError) as exc:
                raise ValueError("durable lifecycle reservation state is unavailable") from exc
        return LifecycleReservationSnapshot(
            remote_task_ids=frozenset(row[2] for row in rows if row[0] == "remote_operation"),
            program_ids=frozenset(row[3] for row in rows if row[0] == "program_control"),
        )

    def _release(self, kind: str, scope_id: str, owner_token: str) -> None:
        if kind not in _KINDS:
            raise ValueError("invalid lifecycle reservation kind")
        self._validate_identity(scope_id, "scope_id")
        if not _OWNER_TOKEN.fullmatch(owner_token):
            raise ValueError("invalid lifecycle reservation ownership token")
        with self._transaction():
            row = self.connection.execute(
                """
                SELECT reservation_kind, scope_id, task_id, program_id,
                       owner_token, created_at
                FROM lifecycle_reservations
                WHERE reservation_kind = ? AND scope_id = ?
                """,
                (kind, scope_id),
            ).fetchone()
            if row is None:
                raise ValueError("durable lifecycle reservation is missing")
            self._validate_rows([row])
            if row[4] != owner_token:
                raise ValueError("durable lifecycle reservation ownership mismatch")
            deleted = self.connection.execute(
                """
                DELETE FROM lifecycle_reservations
                WHERE reservation_kind = ? AND scope_id = ? AND owner_token = ?
                """,
                (kind, scope_id, owner_token),
            ).rowcount
            if deleted != 1:
                raise ValueError("durable lifecycle reservation release was ambiguous")

    def _transaction(self):
        return _ImmediateTransaction(self)

    @staticmethod
    def _validate_identity(value: str, name: str) -> None:
        if not _IDENTITY.fullmatch(value):
            raise ValueError(f"invalid lifecycle reservation {name}")

    @classmethod
    def _validate_rows(cls, rows: list[tuple[object, ...]]) -> None:
        for row in rows:
            if len(row) != 6:
                raise ValueError("invalid durable lifecycle reservation row")
            kind, scope_id, task_id, program_id, owner_token, created_at = row
            if kind not in _KINDS or not isinstance(created_at, str):
                raise ValueError("invalid durable lifecycle reservation row")
            cls._validate_identity(str(scope_id), "scope_id")
            if not _OWNER_TOKEN.fullmatch(str(owner_token)):
                raise ValueError("invalid durable lifecycle reservation owner")
            try:
                datetime.fromisoformat(created_at)
            except ValueError as exc:
                raise ValueError("invalid durable lifecycle reservation timestamp") from exc
            if kind == "remote_operation":
                cls._validate_identity(str(task_id), "task_id")
                if task_id != scope_id:
                    raise ValueError("invalid remote-operation lifecycle reservation")
                if program_id:
                    cls._validate_identity(str(program_id), "program_id")
            elif task_id or program_id != scope_id:
                raise ValueError("invalid Program lifecycle reservation")


class _ImmediateTransaction:
    def __init__(self, store: DurableLifecycleReservationStore) -> None:
        self.store = store

    def __enter__(self) -> None:
        self.store._lock.acquire()
        try:
            self.store.connection.execute("BEGIN IMMEDIATE")
        except sqlite3.DatabaseError as exc:
            self.store._lock.release()
            raise ValueError("durable lifecycle reservation state is unavailable") from exc

    def __exit__(self, exc_type, exc, traceback) -> bool:
        try:
            if exc_type is None:
                self.store.connection.execute("COMMIT")
            else:
                self.store.connection.execute("ROLLBACK")
                if isinstance(exc, sqlite3.DatabaseError):
                    raise ValueError(
                        "durable lifecycle reservation state is unavailable"
                    ) from exc
        except sqlite3.DatabaseError as database_error:
            raise ValueError(
                "durable lifecycle reservation transaction could not be finalized"
            ) from database_error
        finally:
            self.store._lock.release()
        return False


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()
