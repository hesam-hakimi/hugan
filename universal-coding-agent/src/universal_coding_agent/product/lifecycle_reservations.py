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
_WORKER_KINDS = frozenset({"standalone_task", "program_execution"})


@dataclass(frozen=True)
class LifecycleReservationSnapshot:
    remote_task_ids: frozenset[str]
    program_ids: frozenset[str]
    worker_task_ids: frozenset[str]
    worker_program_ids: frozenset[str]


class DurableLifecycleReservationStore:
    """Fail-closed cross-runtime serialization for lifecycle actions and workers.

    Rows contain only local Task/Program identity and an unexposed random ownership
    token. Rows deliberately survive an interrupted process; no TTL or automatic
    recovery policy may silently weaken the serialization boundary.
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
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS lifecycle_worker_ownership (
                worker_kind TEXT NOT NULL,
                scope_id TEXT NOT NULL,
                task_id TEXT NOT NULL,
                program_id TEXT NOT NULL,
                owner_token TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL,
                PRIMARY KEY (worker_kind, scope_id),
                CHECK (worker_kind IN ('standalone_task', 'program_execution')),
                CHECK (
                    (worker_kind = 'standalone_task'
                     AND task_id = scope_id AND program_id = '')
                    OR
                    (worker_kind = 'program_execution'
                     AND program_id = scope_id AND task_id = '')
                )
            )
            """
        )
        self.connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS one_standalone_worker_per_task
            ON lifecycle_worker_ownership(task_id)
            WHERE worker_kind = 'standalone_task'
            """
        )
        self.connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS one_execution_worker_per_program
            ON lifecycle_worker_ownership(program_id)
            WHERE worker_kind = 'program_execution'
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
            worker_rows = self.connection.execute(
                """
                SELECT worker_kind, scope_id, task_id, program_id,
                       owner_token, created_at
                FROM lifecycle_worker_ownership
                WHERE task_id = ? OR (? != '' AND program_id = ?)
                """,
                (task_id, program_id, program_id),
            ).fetchall()
            self._validate_worker_rows(worker_rows)
            if worker_rows:
                raise ValueError("local worker is active")
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
            worker_clauses = ["program_id = ?"]
            worker_parameters: list[str] = [program_id]
            if task_ids:
                placeholders = ", ".join("?" for _ in task_ids)
                worker_clauses.append(f"task_id IN ({placeholders})")
                worker_parameters.extend(task_ids)
            worker_rows = self.connection.execute(
                """
                SELECT worker_kind, scope_id, task_id, program_id,
                       owner_token, created_at
                FROM lifecycle_worker_ownership
                WHERE """
                + " OR ".join(worker_clauses),
                tuple(worker_parameters),
            ).fetchall()
            self._validate_worker_rows(worker_rows)
            if worker_rows:
                raise ValueError("local worker is active")
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

    def reserve_standalone_worker(self, task_id: str) -> str:
        self._validate_identity(task_id, "task_id")
        owner_token = uuid.uuid4().hex
        with self._transaction():
            reservation_rows = self.connection.execute(
                """
                SELECT reservation_kind, scope_id, task_id, program_id,
                       owner_token, created_at
                FROM lifecycle_reservations
                WHERE reservation_kind = 'remote_operation' AND task_id = ?
                """,
                (task_id,),
            ).fetchall()
            self._validate_rows(reservation_rows)
            if reservation_rows:
                raise ValueError("remote-operation lifecycle action is active")
            worker_rows = self.connection.execute(
                """
                SELECT worker_kind, scope_id, task_id, program_id,
                       owner_token, created_at
                FROM lifecycle_worker_ownership
                WHERE task_id = ?
                """,
                (task_id,),
            ).fetchall()
            self._validate_worker_rows(worker_rows)
            if worker_rows:
                raise ValueError("local worker is already active")
            self.connection.execute(
                """
                INSERT INTO lifecycle_worker_ownership(
                    worker_kind, scope_id, task_id, program_id,
                    owner_token, created_at
                ) VALUES ('standalone_task', ?, ?, '', ?, ?)
                """,
                (task_id, task_id, owner_token, _utc_now()),
            )
        return owner_token

    def reserve_program_worker(self, program_id: str) -> str:
        self._validate_identity(program_id, "program_id")
        owner_token = uuid.uuid4().hex
        with self._transaction():
            reservation_rows = self.connection.execute(
                """
                SELECT reservation_kind, scope_id, task_id, program_id,
                       owner_token, created_at
                FROM lifecycle_reservations
                WHERE program_id = ?
                """,
                (program_id,),
            ).fetchall()
            self._validate_rows(reservation_rows)
            if any(row[0] == "program_control" for row in reservation_rows):
                raise ValueError("Program control action is active")
            if reservation_rows:
                raise ValueError("remote-operation lifecycle action is active")
            worker_rows = self.connection.execute(
                """
                SELECT worker_kind, scope_id, task_id, program_id,
                       owner_token, created_at
                FROM lifecycle_worker_ownership
                WHERE program_id = ?
                """,
                (program_id,),
            ).fetchall()
            self._validate_worker_rows(worker_rows)
            if worker_rows:
                raise ValueError("Program worker is already active")
            self.connection.execute(
                """
                INSERT INTO lifecycle_worker_ownership(
                    worker_kind, scope_id, task_id, program_id,
                    owner_token, created_at
                ) VALUES ('program_execution', ?, '', ?, ?, ?)
                """,
                (program_id, program_id, owner_token, _utc_now()),
            )
        return owner_token

    def release_remote_operation(self, task_id: str, owner_token: str) -> None:
        self._release("remote_operation", task_id, owner_token)

    def release_program_control(self, program_id: str, owner_token: str) -> None:
        self._release("program_control", program_id, owner_token)

    def release_standalone_worker(self, task_id: str, owner_token: str) -> None:
        self._release_worker("standalone_task", task_id, owner_token)

    def release_program_worker(self, program_id: str, owner_token: str) -> None:
        self._release_worker("program_execution", program_id, owner_token)

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
                worker_rows = self.connection.execute(
                    """
                    SELECT worker_kind, scope_id, task_id, program_id,
                           owner_token, created_at
                    FROM lifecycle_worker_ownership
                    """
                ).fetchall()
                self._validate_worker_rows(worker_rows)
            except (sqlite3.DatabaseError, ValueError) as exc:
                raise ValueError("durable lifecycle reservation state is unavailable") from exc
        return LifecycleReservationSnapshot(
            remote_task_ids=frozenset(row[2] for row in rows if row[0] == "remote_operation"),
            program_ids=frozenset(row[3] for row in rows if row[0] == "program_control"),
            worker_task_ids=frozenset(
                row[2] for row in worker_rows if row[0] == "standalone_task"
            ),
            worker_program_ids=frozenset(
                row[3] for row in worker_rows if row[0] == "program_execution"
            ),
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

    def _release_worker(self, kind: str, scope_id: str, owner_token: str) -> None:
        if kind not in _WORKER_KINDS:
            raise ValueError("invalid lifecycle worker kind")
        self._validate_identity(scope_id, "scope_id")
        if not _OWNER_TOKEN.fullmatch(owner_token):
            raise ValueError("invalid lifecycle worker ownership token")
        with self._transaction():
            row = self.connection.execute(
                """
                SELECT worker_kind, scope_id, task_id, program_id,
                       owner_token, created_at
                FROM lifecycle_worker_ownership
                WHERE worker_kind = ? AND scope_id = ?
                """,
                (kind, scope_id),
            ).fetchone()
            if row is None:
                raise ValueError("durable lifecycle worker ownership is missing")
            self._validate_worker_rows([row])
            if row[4] != owner_token:
                raise ValueError("durable lifecycle worker ownership mismatch")
            deleted = self.connection.execute(
                """
                DELETE FROM lifecycle_worker_ownership
                WHERE worker_kind = ? AND scope_id = ? AND owner_token = ?
                """,
                (kind, scope_id, owner_token),
            ).rowcount
            if deleted != 1:
                raise ValueError("durable lifecycle worker release was ambiguous")

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

    @classmethod
    def _validate_worker_rows(cls, rows: list[tuple[object, ...]]) -> None:
        for row in rows:
            if len(row) != 6:
                raise ValueError("invalid durable lifecycle worker row")
            kind, scope_id, task_id, program_id, owner_token, created_at = row
            if kind not in _WORKER_KINDS or not isinstance(created_at, str):
                raise ValueError("invalid durable lifecycle worker row")
            cls._validate_identity(str(scope_id), "scope_id")
            if not _OWNER_TOKEN.fullmatch(str(owner_token)):
                raise ValueError("invalid durable lifecycle worker owner")
            try:
                datetime.fromisoformat(created_at)
            except ValueError as exc:
                raise ValueError("invalid durable lifecycle worker timestamp") from exc
            if kind == "standalone_task":
                cls._validate_identity(str(task_id), "task_id")
                if task_id != scope_id or program_id:
                    raise ValueError("invalid standalone lifecycle worker")
            elif task_id or program_id != scope_id:
                raise ValueError("invalid Program lifecycle worker")


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
