"""Inert Program continuation metadata and atomic worker ownership handoffs.

No execution consumer is registered here. References are historical intent, not
checkpoint, source, approval or quiescence proofs. Importing this module loads no
Program, Safe, provider, Git, web or execution service. Only a trusted local host
with already-open stores may construct it; public records never restore tokens.
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import time
from contextlib import ExitStack, contextmanager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from universal_coding_agent.product.lifecycle_reservations import (
        DurableLifecycleReservationStore,
    )
    from universal_coding_agent.product.program_orchestrator import ProgramOrchestrator

SCHEMA = "uca-program-continuation-handoff-1"
MAX_PAGE = 100
MAX_RECORD_BYTES = 64 * 1024
MAX_TOTAL_BYTES = 1024 * 1024
MAX_FIELD_BYTES = 4096
_ID = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9._-]{1,127}\Z")
_HASH = re.compile(r"[0-9a-f]{64}\Z")
_TOKEN = re.compile(r"[0-9a-f]{32}\Z")
_TABLES = (
    "program_continuation_heads",
    "program_continuation_receipts",
    "program_continuation_requests",
)
_DESCRIPTOR_FIELDS = frozenset(
    {
        "schema",
        "program_id",
        "phase_id",
        "task_id",
        "thread_id",
        "requirement_sha256",
        "plan_sha256",
        "source_generation",
        "source_sha256",
        "acceptance_receipt_sha256",
        "admission_sha256",
        "checkpoint_sha256",
        "result_sha256",
        "approval_core_sha256",
        "next_action",
        "execution_authorized",
        "consumer_bound",
    }
)
_RECEIPT_FIELDS = frozenset(
    {
        "schema",
        "program_id",
        "host_sha256",
        "sequence",
        "epoch",
        "state",
        "action",
        "request_id",
        "request_sha256",
        "predecessor_sha256",
        "descriptor",
        "witness_sha256",
        "owner_sha256",
        "released_owner_sha256",
        "execution_authorized",
        "consumer_bound",
    }
)
_PROGRAM = ("program_id", "status", "requirement_hash", "plan_hash", "plan_ref")
_PHASE = ("program_id", "phase_id", "status", "result_ref", "summary_ref")
_EXECUTION = (
    "program_id",
    "phase_id",
    "unit_key",
    "slice_id",
    "task_id",
    "thread_id",
    "requirement_hash",
    "status",
    "safe_status",
    "result_ref",
    "phase_report_ref",
    "error_ref",
    "accepted_evidence_ref",
    "accepted_evidence_hash",
    "expected_base_sha",
    "remote_disposition_ref",
)
_CONTROL = ("entity_type", "entity_id", "state", "reason", "revision")
_SOURCE = (
    "program_id",
    "generation",
    "source_sha256",
    "host_sha256",
    "initial_receipt_sha256",
    "receipt_sha256",
)
_OWNER = ("worker_kind", "scope_id", "task_id", "program_id", "owner_token", "created_at")


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _identifier(value, *, empty=False):
    _require(
        type(value) is str and ((empty and value == "") or _ID.fullmatch(value)),
        "invalid bounded handoff identifier",
    )


def _digest(value, *, empty=False):
    _require(
        type(value) is str and ((empty and value == "") or _HASH.fullmatch(value)),
        "invalid handoff digest",
    )


def _integer(value):
    _require(type(value) is int and 0 <= value < 2**63 - 1, "invalid handoff integer")


def _canonical(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode()


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _strict_json(data):
    _require(
        type(data) is bytes and 0 < len(data) <= MAX_RECORD_BYTES,
        "handoff metadata exceeds its byte bound",
    )
    # Bound nesting BEFORE recursive JSON parsing or canonicalization, including
    # malformed JSON. Brackets inside strings cannot inflate or hide the depth.
    depth, quoted, escaped = 0, False, False
    for char in data:
        if quoted:
            if escaped:
                escaped = False
            elif char == 92:
                escaped = True
            elif char == 34:
                quoted = False
        elif char == 34:
            quoted = True
        elif char in (91, 123):
            depth += 1
            _require(depth <= 8, "handoff metadata nesting exceeds its bound")
        elif char in (93, 125):
            depth -= 1
            _require(depth >= 0, "invalid handoff JSON")

    def pairs(items):
        _require(len(items) <= 64, "handoff metadata field count exceeds its bound")
        result = {}
        for key, value in items:
            _require(
                key not in result and len(key.encode()) <= 128,
                "duplicate or oversized handoff JSON key",
            )
            result[key] = value
        return result

    def invalid_number(_value):
        raise ValueError("invalid handoff JSON number")

    try:
        result = json.loads(
            data, object_pairs_hook=pairs, parse_float=invalid_number, parse_constant=invalid_number
        )
        _require(
            type(result) is dict and _canonical(result) == data, "handoff JSON must be canonical"
        )
        return result
    except (UnicodeError, RecursionError, json.JSONDecodeError) as exc:
        raise ValueError("invalid handoff JSON") from exc


def _descriptor(value):
    _require(
        type(value) is dict and value.keys() == _DESCRIPTOR_FIELDS,
        "invalid handoff descriptor fields",
    )
    _require(
        value["schema"] == SCHEMA
        and value["next_action"] == "foundation_only"
        and value["execution_authorized"] is False
        and value["consumer_bound"] is False,
        "handoff descriptor is inert and has no execution consumer",
    )
    for key in ("program_id", "phase_id", "task_id", "thread_id"):
        _identifier(value[key], empty=key in {"task_id", "thread_id"})
    _require(bool(value["task_id"]) == bool(value["thread_id"]), "incomplete task identity")
    for key in _DESCRIPTOR_FIELDS:
        if key.endswith("_sha256"):
            _digest(value[key], empty=key not in {"requirement_sha256", "plan_sha256"})
    generation = value["source_generation"]
    if generation is None:
        _require(
            value["source_sha256"] == value["acceptance_receipt_sha256"] == "",
            "uninitialized source descriptor differs",
        )
    else:
        _integer(generation)
        _digest(value["source_sha256"])
        _digest(value["acceptance_receipt_sha256"])
    return value


class HandoffResult:
    """Public immutable outcome plus an optional first-response-only private token.

    Serialize ``public`` only. The local envelope is deliberately not a dataclass
    or mapping, and its repr never includes its private owner token.
    """

    __slots__ = ("_public_bytes", "_owner_token")

    def __init__(self, public, owner_token=None):
        self._public_bytes = _canonical(public)
        self._owner_token = owner_token

    @property
    def public(self):
        return json.loads(self._public_bytes)

    @property
    def owner_token(self):
        return self._owner_token

    def __repr__(self):
        return f"HandoffResult(public={self.public!r})"


class _Reader:
    def __init__(self, connection):
        self.connection, self.total = connection, 0
        self.cache = {}

    def budget(self, size, *, maximum):
        _require(type(size) is int and 0 <= size <= maximum, "handoff field exceeds its byte bound")
        self.total += size
        _require(self.total <= MAX_TOTAL_BYTES, "handoff aggregate exceeds its byte bound")

    def rows(
        self, table, fields, where="1", parameters=(), *, order="", limit=MAX_PAGE, page=False
    ):
        # Table, field and order strings are module-owned SQL; only values come
        # from callers. Sizes and types are fetched before any field contents.
        suffix = f" FROM {table} WHERE {where}"
        if order:
            suffix += " ORDER BY " + order
        suffix += f" LIMIT {limit + 1}"
        sizes = self.connection.execute(
            "SELECT " + ",".join(f"length(CAST({f} AS BLOB)),typeof({f})" for f in fields) + suffix,
            parameters,
        ).fetchall()
        _require(page or len(sizes) <= limit, "handoff row set exceeds its bound")
        for row in sizes:
            for index in range(0, len(row), 2):
                _require(row[index + 1] in {"text", "integer"}, "invalid metadata field type")
                self.budget(row[index], maximum=MAX_FIELD_BYTES)
        return [
            dict(zip(fields, row, strict=True))
            for row in self.connection.execute(
                "SELECT " + ",".join(fields) + suffix, parameters
            ).fetchall()
        ]

    def exists(self, table, alias="main"):
        return bool(
            self.connection.execute(
                f"SELECT 1 FROM {alias}.sqlite_master WHERE type='table' AND name=?", (table,)
            ).fetchone()
        )


class ProgramContinuationHandoffStore:
    def __init__(
        self,
        programs: ProgramOrchestrator,
        lifecycle: DurableLifecycleReservationStore,
        *,
        host_id: str,
    ):
        _identifier(host_id)
        self.programs, self.lifecycle = programs, lifecycle
        self.stores = (programs, programs.control, lifecycle)
        self.paths = tuple(store.database_path.resolve(strict=True) for store in self.stores)
        self.identities = tuple(self._identity(path) for path in self.paths)
        _require(
            len(set(self.paths)) == 3
            and len({(item[1], item[2]) for item in self.identities}) == 3,
            "handoff requires three distinct existing stores",
        )
        self.host_sha256 = _sha(
            _canonical(
                {
                    "schema": SCHEMA,
                    "host_id": host_id,
                    "stores": self.identities,
                }
            )
        )
        self._pins()

    @staticmethod
    def _identity(path):
        info = path.stat()
        _require(path.is_file(), "handoff requires on-disk stores")
        return (str(path), info.st_dev, info.st_ino)

    def _pins(self):
        _require(
            self.programs is self.stores[0]
            and self.programs.control is self.stores[1]
            and self.lifecycle is self.stores[2],
            "handoff host store binding differs",
        )
        _require(
            tuple(self._identity(path) for path in self.paths) == self.identities,
            "handoff store identity changed",
        )
        for store, path in zip(self.stores, self.paths, strict=True):
            databases = {row[1]: row[2] for row in store.connection.execute("PRAGMA database_list")}
            _require(
                databases.get("main") == str(path)
                and store.database_path.resolve(strict=True) == path,
                "handoff host store binding differs",
            )

    @staticmethod
    def _durability(connection, aliases):
        for alias in aliases:
            mode = connection.execute(f"PRAGMA {alias}.journal_mode").fetchone()[0]
            sync = connection.execute(f"PRAGMA {alias}.synchronous").fetchone()[0]
            _require(
                mode in {"delete", "truncate", "persist"} and sync in {2, 3},
                "handoff requires rollback journals and FULL or EXTRA synchronization",
            )

    @contextmanager
    def _session(self, *, write=False):
        connection = None
        with ExitStack() as locks:
            for store in self.stores:
                locks.enter_context(store._lock)
            try:
                self._pins()
                if write:
                    for store in self.stores:
                        _require(
                            not store.connection.in_transaction,
                            "handoff requires committed host stores",
                        )
                    for store in (self.programs, self.lifecycle):
                        self._durability(store.connection, ("main",))
                mode = "rw" if write else "ro"
                connection = sqlite3.connect(
                    self.paths[0].as_uri() + "?mode=" + mode,
                    uri=True,
                    isolation_level=None,
                    timeout=2,
                )
                connection.execute(
                    "ATTACH DATABASE ? AS control", (self.paths[1].as_uri() + "?mode=" + mode,)
                )
                connection.execute(
                    "ATTACH DATABASE ? AS lifecycle", (self.paths[2].as_uri() + "?mode=" + mode,)
                )
                connection.execute("PRAGMA trusted_schema=OFF")
                if write:
                    self._durability(connection, ("main", "lifecycle"))
                else:
                    connection.execute("PRAGMA query_only=ON")
                deadline, ticks = time.monotonic() + 3, 0

                def progress():
                    nonlocal ticks
                    ticks += 1
                    return int(ticks > 2000 or time.monotonic() > deadline)

                def authorize(action, table, _column, database, trigger):
                    if action in {
                        sqlite3.SQLITE_INSERT,
                        sqlite3.SQLITE_UPDATE,
                        sqlite3.SQLITE_DELETE,
                    }:
                        allowed = (database == "main" and table in (*_TABLES, "sqlite_master")) or (
                            database == "lifecycle" and table == "lifecycle_worker_ownership"
                        )
                        return (
                            sqlite3.SQLITE_OK
                            if write and allowed and not trigger
                            else sqlite3.SQLITE_DENY
                        )
                    return sqlite3.SQLITE_OK

                connection.set_progress_handler(progress, 1000)
                connection.set_authorizer(authorize)
                # A read-only URI cannot exclude a concurrent WAL control writer.
                # IMMEDIATE must reserve all three stores through commit. Control
                # remains logically read-only: the authorizer forbids every write
                # and it never becomes a modified commit participant.
                connection.execute("BEGIN IMMEDIATE" if write else "BEGIN")
                # Establish all three read snapshots before projecting any rows.
                for alias in ("main", "control", "lifecycle"):
                    connection.execute(f"SELECT 1 FROM {alias}.sqlite_master LIMIT 1").fetchone()
                self._pins()
                yield _Reader(connection)
                self._pins()
                if write:
                    self._boundary("before_commit")
                    connection.commit()
                    self._boundary("after_commit")
            except (sqlite3.Error, OSError) as exc:
                raise ValueError(
                    "handoff stores are unavailable; explicit diagnosis required"
                ) from exc
            finally:
                if connection is not None:
                    try:
                        if connection.in_transaction:
                            connection.rollback()
                    finally:
                        connection.close()

    def _boundary(self, _name):
        """No-op fault boundary for process-death tests; never invokes external work."""

    def _schema(self, reader, *, create=False):
        present = [reader.exists(table) for table in _TABLES]
        _require(not any(present) or all(present), "incomplete handoff schema")
        if not any(present) and create:
            for ddl in (
                """CREATE TABLE program_continuation_heads (
                program_id TEXT PRIMARY KEY, schema TEXT NOT NULL, host_sha256 TEXT NOT NULL,
                epoch INTEGER NOT NULL, state TEXT NOT NULL, receipt_sha256 TEXT NOT NULL)""",
                """CREATE TABLE program_continuation_receipts (
                receipt_sha256 TEXT PRIMARY KEY, program_id TEXT NOT NULL,
                sequence INTEGER NOT NULL,
                content BLOB NOT NULL, UNIQUE(program_id, sequence))""",
                """CREATE TABLE program_continuation_requests (
                host_sha256 TEXT NOT NULL, program_id TEXT NOT NULL, request_id TEXT NOT NULL,
                request_sha256 TEXT NOT NULL, action TEXT NOT NULL, epoch INTEGER NOT NULL,
                status TEXT NOT NULL, receipt_sha256 TEXT NOT NULL,
                PRIMARY KEY(host_sha256, program_id, request_id))""",
            ):
                reader.connection.execute(ddl)
            return True
        return all(present)

    def _semantic(self, reader, descriptor):
        program_id = descriptor["program_id"]
        program = reader.rows("programs", _PROGRAM, "program_id=?", (program_id,), limit=1)
        _require(len(program) == 1, "handoff Program is missing")
        program = program[0]
        _require(all(type(value) is str for value in program.values()), "invalid Program row")
        _digest(program["requirement_hash"])
        _digest(program["plan_hash"])
        _require(
            program["status"]
            in {
                "draft",
                "awaiting_approval",
                "running",
                "paused",
                "blocked",
                "realignment_required",
                "cancelled",
                "completed",
            },
            "invalid Program status",
        )
        _require(
            program["plan_ref"] == f"artifact://programs/{program_id}/program-plan.json",
            "handoff Program plan reference differs",
        )
        phases = reader.rows(
            "program_phases", _PHASE, "program_id=?", (program_id,), order="phase_id"
        )
        executions = reader.rows(
            "program_executions", _EXECUTION, "program_id=?", (program_id,), order="task_id"
        )
        _require(
            any(row["phase_id"] == descriptor["phase_id"] for row in phases),
            "handoff phase is missing",
        )
        for row in phases + executions:
            _require(all(type(value) is str for value in row.values()), "invalid Program unit row")
            _identifier(row["phase_id"])
        for row in executions:
            _identifier(row["task_id"])
            _identifier(row["thread_id"])
            _digest(row["requirement_hash"])
            _require(
                row["status"]
                in {
                    "starting",
                    "awaiting_scope_approval",
                    "running",
                    "completed",
                    "failed",
                    "cancelled",
                },
                "invalid Program execution status",
            )
        for row in phases:
            _require(
                row["status"]
                in {
                    "pending",
                    "running",
                    "paused",
                    "blocked",
                    "failed",
                    "cancelled",
                    "completed",
                },
                "invalid Program phase status",
            )
        tasks = tuple(row["task_id"] for row in executions)
        if descriptor["task_id"]:
            _require(
                any(
                    row["task_id"] == descriptor["task_id"]
                    and row["thread_id"] == descriptor["thread_id"]
                    and row["phase_id"] == descriptor["phase_id"]
                    for row in executions
                ),
                "handoff execution identity differs",
            )
        task_clause = ",".join("?" for _ in tasks) or "NULL"
        controls = reader.rows(
            "control.control_state",
            _CONTROL,
            f"(entity_type='program' AND entity_id=?) OR "
            f"(entity_type='task' AND entity_id IN ({task_clause}))",
            (program_id, *tasks),
            order="entity_type,entity_id",
            limit=101,
        )
        program_control = [row for row in controls if row["entity_type"] == "program"]
        _require(len(program_control) == 1, "handoff Program control is missing")
        for row in controls:
            _integer(row["revision"])
            _identifier(row["entity_id"])
            _require(
                all(type(row[key]) is str for key in ("entity_type", "state", "reason")),
                "invalid handoff control row",
            )
            _require(
                row["state"]
                in {
                    "running",
                    "pause_requested",
                    "paused",
                    "cancel_requested",
                    "cancelled",
                    "failed",
                    "completed",
                },
                "invalid handoff control state",
            )
        if descriptor["task_id"]:
            _require(
                any(
                    row["entity_type"] == "task" and row["entity_id"] == descriptor["task_id"]
                    for row in controls
                ),
                "handoff Task control is missing",
            )
        legacy = reader.rows(
            "control.uca_source_dispatch_tasks", ("task_id",), f"task_id IN ({task_clause})", tasks
        )
        dispatches = []
        if reader.exists("program_source_dispatches"):
            dispatches = reader.rows(
                "program_source_dispatches", ("task_id",), f"task_id IN ({task_clause})", tasks
            )
        source = (
            reader.rows("program_source_heads", _SOURCE, "program_id=?", (program_id,), limit=1)
            if reader.exists("program_source_heads")
            else []
        )
        if source:
            _integer(source[0]["generation"])
            for key in _SOURCE[2:]:
                _digest(source[0][key])
        snapshot = {
            "program": program,
            "phases": phases,
            "executions": executions,
            "controls": controls,
            "source": source,
            "legacy": legacy + dispatches,
        }
        raw = _canonical(snapshot)
        _require(len(raw) <= MAX_RECORD_BYTES, "handoff witness exceeds its byte bound")
        valid = (
            program["status"] == "running"
            and program_control[0]["state"] == "running"
            and all(row["state"] in {"running", "completed"} for row in controls)
            and all(row["status"] in {"pending", "running", "completed"} for row in phases)
            and all(row["requirement_hash"] == program["requirement_hash"] for row in executions)
            and not legacy
            and not dispatches
            and program["requirement_hash"] == descriptor["requirement_sha256"]
            and program["plan_hash"] == descriptor["plan_sha256"]
            and (source[0]["generation"] if source else None) == descriptor["source_generation"]
            and (source[0]["source_sha256"] if source else "") == descriptor["source_sha256"]
            and (source[0]["receipt_sha256"] if source else "")
            == descriptor["acceptance_receipt_sha256"]
        )
        return _sha(raw), tasks, valid

    def _request_row(self, reader, program_id, request_id):
        fields = (
            "host_sha256",
            "program_id",
            "request_id",
            "request_sha256",
            "action",
            "epoch",
            "status",
            "receipt_sha256",
        )
        rows = reader.rows(
            _TABLES[2],
            fields,
            "host_sha256=? AND program_id=? AND request_id=?",
            (self.host_sha256, program_id, request_id),
            limit=1,
        )
        if not rows:
            return None
        row = rows[0]
        _digest(row["request_sha256"])
        _digest(row["receipt_sha256"], empty=row["status"] == "in_progress")
        _integer(row["epoch"])
        _require(
            row["action"] in {"create", "park", "claim", "close"}
            and row["status"] in {"completed", "in_progress"},
            "invalid handoff request",
        )
        return row

    def _receipt(self, reader, digest, program_id):
        _digest(digest)
        if digest in reader.cache:
            result = reader.cache[digest]
            _require(result["program_id"] == program_id, "receipt Program differs")
            return result
        rows = reader.rows(
            _TABLES[1],
            ("receipt_sha256", "program_id", "sequence"),
            "receipt_sha256=?",
            (digest,),
            limit=1,
        )
        _require(
            len(rows) == 1 and rows[0]["program_id"] == program_id,
            "handoff receipt is missing or belongs to another Program",
        )
        size, kind = reader.connection.execute(
            "SELECT length(content),typeof(content) FROM program_continuation_receipts "
            "WHERE receipt_sha256=?",
            (digest,),
        ).fetchone()
        _require(kind == "blob", "invalid handoff receipt storage type")
        reader.budget(size, maximum=MAX_RECORD_BYTES)
        data = reader.connection.execute(
            "SELECT content FROM program_continuation_receipts WHERE receipt_sha256=?", (digest,)
        ).fetchone()[0]
        _require(_sha(data) == digest, "handoff receipt digest differs")
        result = _strict_json(data)
        _require(result.keys() == _RECEIPT_FIELDS, "invalid handoff receipt fields")
        _require(
            result["schema"] == SCHEMA
            and result["host_sha256"] == self.host_sha256
            and result["program_id"] == program_id
            and result["sequence"] == rows[0]["sequence"]
            and result["execution_authorized"] is False
            and result["consumer_bound"] is False,
            "handoff receipt binding differs",
        )
        _descriptor(result["descriptor"])
        _require(result["descriptor"]["program_id"] == program_id, "descriptor Program differs")
        _integer(result["epoch"])
        _integer(result["sequence"])
        _identifier(result["request_id"])
        for key in (
            "host_sha256",
            "request_sha256",
            "predecessor_sha256",
            "witness_sha256",
            "owner_sha256",
            "released_owner_sha256",
        ):
            _digest(
                result[key],
                empty=key in {"predecessor_sha256", "owner_sha256", "released_owner_sha256"},
            )
        action, state = result["action"], result["state"]
        _require(
            type(action) is str
            and action in {"create", "park", "claim", "close"}
            and state
            == {"create": "owned", "claim": "owned", "park": "parked", "close": "closed"}[action],
            "invalid handoff receipt transition",
        )
        _require(
            bool(result["owner_sha256"]) == (state == "owned")
            and bool(result["released_owner_sha256"]) == (state != "owned"),
            "invalid handoff receipt owner witness",
        )
        request = self._request_row(reader, program_id, result["request_id"])
        _require(
            request is not None
            and request["status"] == "completed"
            and request["receipt_sha256"] == digest
            and request["action"] == action
            and request["epoch"] == result["epoch"]
            and request["request_sha256"] == result["request_sha256"],
            "handoff receipt request differs",
        )
        reader.cache[digest] = result
        return result

    def _linked(self, reader, digest, program_id):
        current = self._receipt(reader, digest, program_id)
        if current["action"] == "create":
            _require(
                current["sequence"] == 1
                and current["epoch"] == 0
                and not current["predecessor_sha256"],
                "invalid initial handoff receipt",
            )
            return current
        previous = self._receipt(reader, current["predecessor_sha256"], program_id)
        action = current["action"]
        _require(
            current["sequence"] == previous["sequence"] + 1
            and current["epoch"] == previous["epoch"] + (action == "claim")
            and current["descriptor"] == previous["descriptor"]
            and current["witness_sha256"] == previous["witness_sha256"]
            and previous["state"] == ("parked" if action == "claim" else "owned"),
            "handoff predecessor transition differs",
        )
        if action == "claim":
            _require(
                current["owner_sha256"] != previous["released_owner_sha256"],
                "handoff claim reused ownership",
            )
        else:
            _require(
                current["released_owner_sha256"] == previous["owner_sha256"],
                "handoff released owner differs",
            )
        return current

    def _head(self, reader, program_id, *, complete_chain=False):
        rows = reader.rows(
            _TABLES[0],
            ("program_id", "schema", "host_sha256", "epoch", "state", "receipt_sha256"),
            "program_id=?",
            (program_id,),
            limit=1,
        )
        latest = reader.rows(
            _TABLES[1],
            ("receipt_sha256", "sequence"),
            "program_id=?",
            (program_id,),
            order="sequence DESC",
            limit=1,
            page=True,
        )
        if not rows:
            orphan = reader.connection.execute(
                "SELECT 1 FROM program_continuation_requests WHERE program_id=? LIMIT 1",
                (program_id,),
            ).fetchone()
            _require(not latest and not orphan, "handoff head is missing")
            return None
        head = rows[0]
        _integer(head["epoch"])
        _require(
            head["schema"] == SCHEMA and head["host_sha256"] == self.host_sha256,
            "handoff head belongs to another schema or host",
        )
        receipt = self._linked(reader, head["receipt_sha256"], program_id)
        _require(
            head["state"] == receipt["state"]
            and head["epoch"] == receipt["epoch"]
            and latest
            and latest[0]["receipt_sha256"] == head["receipt_sha256"]
            and latest[0]["sequence"] == receipt["sequence"],
            "handoff head differs",
        )
        if complete_chain:
            # Mutations must not step past missing older history. Indexed digest
            # reads share the operation's aggregate/SQL/time budget; oversized
            # history fails closed. Status remains a bounded keyset projection.
            previous = receipt
            while previous["predecessor_sha256"]:
                previous = self._linked(reader, previous["predecessor_sha256"], program_id)
        return receipt, head["receipt_sha256"]

    def _outcome(self, receipt, digest):
        proposal = ""
        if receipt["state"] == "parked":
            proposal = _sha(
                _canonical(
                    {
                        "schema": SCHEMA,
                        "host_sha256": self.host_sha256,
                        "action": "claim",
                        "program_id": receipt["program_id"],
                        "epoch": receipt["epoch"],
                        "receipt_sha256": digest,
                        "descriptor_sha256": _sha(_canonical(receipt["descriptor"])),
                        "witness_sha256": receipt["witness_sha256"],
                    }
                )
            )
        return {
            "schema": SCHEMA,
            "request_status": "completed",
            "receipt_sha256": digest,
            "receipt": receipt,
            "proposal_sha256": proposal,
            "execution_authorized": False,
            "consumer_bound": False,
        }

    def _replay(self, reader, program_id, request_id, request_sha256):
        request = self._request_row(reader, program_id, request_id)
        if request is None:
            return None
        _require(
            request["request_sha256"] == request_sha256,
            "handoff request ID was already used with different content",
        )
        _require(request["status"] == "completed", "handoff request requires explicit diagnosis")
        receipt = self._linked(reader, request["receipt_sha256"], program_id)
        return HandoffResult(self._outcome(receipt, request["receipt_sha256"]))

    def create(
        self, program_id: str, *, request_id: str, owner_token: str, descriptor: bytes
    ) -> HandoffResult:
        """Record explicit foundation intent under an already reserved exact worker."""
        parsed = _descriptor(_strict_json(descriptor))
        _require(parsed["program_id"] == program_id, "descriptor Program differs")
        return self._change(
            "create", program_id, request_id, owner_token=owner_token, descriptor=parsed
        )

    def park(
        self,
        program_id: str,
        *,
        request_id: str,
        expected_epoch: int,
        expected_receipt_sha256: str,
        owner_token: str,
    ) -> HandoffResult:
        return self._change(
            "park",
            program_id,
            request_id,
            owner_token=owner_token,
            expected_epoch=expected_epoch,
            expected_receipt=expected_receipt_sha256,
        )

    def claim(
        self,
        program_id: str,
        *,
        request_id: str,
        expected_epoch: int,
        expected_receipt_sha256: str,
        descriptor_sha256: str,
        proposal_sha256: str,
        confirmed: bool,
    ) -> HandoffResult:
        _require(confirmed is True, "handoff claim requires explicit exact proposal confirmation")
        _digest(descriptor_sha256)
        _digest(proposal_sha256)
        return self._change(
            "claim",
            program_id,
            request_id,
            expected_epoch=expected_epoch,
            expected_receipt=expected_receipt_sha256,
            descriptor_sha256=descriptor_sha256,
            proposal_sha256=proposal_sha256,
        )

    def close(
        self,
        program_id: str,
        *,
        request_id: str,
        expected_epoch: int,
        expected_receipt_sha256: str,
        owner_token: str,
    ) -> HandoffResult:
        return self._change(
            "close",
            program_id,
            request_id,
            owner_token=owner_token,
            expected_epoch=expected_epoch,
            expected_receipt=expected_receipt_sha256,
        )

    def _change(
        self,
        action,
        program_id,
        request_id,
        *,
        owner_token=None,
        descriptor=None,
        expected_epoch=0,
        expected_receipt="",
        descriptor_sha256="",
        proposal_sha256="",
    ):
        _identifier(program_id)
        _identifier(request_id)
        _integer(expected_epoch)
        _digest(expected_receipt, empty=action == "create")
        if action != "claim":
            _require(
                type(owner_token) is str and _TOKEN.fullmatch(owner_token),
                "invalid private worker ownership",
            )
        payload = {
            "schema": SCHEMA,
            "host_sha256": self.host_sha256,
            "program_id": program_id,
            "action": action,
            "request_id": request_id,
            "expected_epoch": expected_epoch,
            "expected_receipt_sha256": expected_receipt,
            "descriptor": descriptor,
            "descriptor_sha256": descriptor_sha256,
            "proposal_sha256": proposal_sha256,
            "owner_token_sha256": _sha(owner_token.encode()) if owner_token else "",
        }
        request_sha256 = _sha(_canonical(payload))
        with self._session(write=True) as reader:
            _require(self._schema(reader, create=action == "create"), "handoff is uninitialized")
            replay = self._replay(reader, program_id, request_id, request_sha256)
            if replay is not None:
                return replay
            from universal_coding_agent.product.program_source_routing import require_no_v3
            require_no_v3(reader.connection, program_id=program_id, active_only=True)
            head = self._head(reader, program_id, complete_chain=True)
            if action == "create":
                _require(head is None, "handoff already exists; explicit diagnosis required")
                epoch, sequence, predecessor = 0, 1, ""
            else:
                _require(head is not None, "handoff is missing")
                previous, predecessor = head
                _require(
                    previous["epoch"] == expected_epoch and predecessor == expected_receipt,
                    "handoff epoch or receipt changed",
                )
                _require(
                    previous["state"] == ("parked" if action == "claim" else "owned"),
                    "handoff state requires explicit diagnosis",
                )
                descriptor = previous["descriptor"]
                epoch = previous["epoch"] + (action == "claim")
                sequence = previous["sequence"] + 1
                _integer(epoch)
                _integer(sequence)
                if action == "claim":
                    _require(
                        descriptor_sha256 == _sha(_canonical(descriptor))
                        and proposal_sha256
                        == self._outcome(previous, predecessor)["proposal_sha256"],
                        "handoff proposal differs",
                    )
            witness, tasks, valid = self._semantic(reader, descriptor)
            _require(
                valid, "handoff requires unchanged approved Program/source/control; no v2 adoption"
            )
            if head:
                _require(witness == previous["witness_sha256"], "handoff semantic inputs changed")
            connection = reader.connection
            private_token = None
            if action == "claim":
                private_token = self.lifecycle.reserve_program_worker_in_transaction(
                    connection, program_id, task_ids=tasks
                )
                owner_token = private_token
                self._boundary("after_worker")
            owner = self.lifecycle.check_program_worker_in_transaction(
                connection, program_id, task_ids=tasks, owner_token=owner_token
            )
            owner_sha256 = _sha(_canonical(owner))
            if action in {"park", "close"}:
                _require(
                    owner_sha256 == previous["owner_sha256"],
                    "handoff owner witness differs; recovery required",
                )
            state = {"create": "owned", "claim": "owned", "park": "parked", "close": "closed"}[
                action
            ]
            receipt = {
                "schema": SCHEMA,
                "program_id": program_id,
                "host_sha256": self.host_sha256,
                "sequence": sequence,
                "epoch": epoch,
                "state": state,
                "action": action,
                "request_id": request_id,
                "request_sha256": request_sha256,
                "predecessor_sha256": predecessor,
                "descriptor": descriptor,
                "witness_sha256": witness,
                "owner_sha256": owner_sha256 if state == "owned" else "",
                "released_owner_sha256": owner_sha256 if state != "owned" else "",
                "execution_authorized": False,
                "consumer_bound": False,
            }
            data = _canonical(receipt)
            _require(len(data) <= MAX_RECORD_BYTES, "handoff receipt exceeds its byte bound")
            digest = _sha(data)
            connection.execute(
                "INSERT INTO program_continuation_receipts VALUES (?, ?, ?, ?)",
                (digest, program_id, sequence, data),
            )
            self._boundary("after_receipt")
            if action in {"park", "close"}:
                self.lifecycle.release_program_worker_in_transaction(
                    connection, program_id, task_ids=tasks, owner_token=owner_token
                )
                self._boundary("after_worker")
            connection.execute(
                "INSERT INTO program_continuation_requests "
                "VALUES (?, ?, ?, ?, ?, ?, 'completed', ?)",
                (self.host_sha256, program_id, request_id, request_sha256, action, epoch, digest),
            )
            self._boundary("after_request")
            if action == "create":
                connection.execute(
                    "INSERT INTO program_continuation_heads VALUES (?, ?, ?, ?, ?, ?)",
                    (program_id, SCHEMA, self.host_sha256, epoch, state, digest),
                )
            else:
                count = connection.execute(
                    """UPDATE program_continuation_heads SET epoch=?, state=?, receipt_sha256=?
                    WHERE program_id=? AND host_sha256=? AND epoch=? AND receipt_sha256=?""",
                    (
                        epoch,
                        state,
                        digest,
                        program_id,
                        self.host_sha256,
                        expected_epoch,
                        predecessor,
                    ),
                ).rowcount
                _require(count == 1, "handoff head compare-and-swap failed")
            self._boundary("after_head")
            result = HandoffResult(self._outcome(receipt, digest), private_token)
        return result

    def request_result(self, program_id: str, request_id: str) -> dict:
        """Read recorded outcome only. Unknown/in-progress is diagnosis, never retry authority."""
        _identifier(program_id)
        _identifier(request_id)
        with self._session() as reader:
            request = (
                self._request_row(reader, program_id, request_id) if self._schema(reader) else None
            )
            if request is None or request["status"] == "in_progress":
                return {
                    "schema": SCHEMA,
                    "program_id": program_id,
                    "request_id": request_id,
                    "request_status": "unknown" if request is None else "in_progress",
                    "diagnosis_required": True,
                    "execution_authorized": False,
                    "consumer_bound": False,
                }
            receipt = self._linked(reader, request["receipt_sha256"], program_id)
            return self._outcome(receipt, request["receipt_sha256"])

    def status(self, program_id: str, *, after_sequence: int = 0, limit: int = 20) -> dict:
        """Read a bounded keyset page and current blockers, without repairing any store.

        Each returned receipt and its immediate predecessor are checked. This is
        recorded metadata, not an unbounded historical audit or execution proof.
        """
        _identifier(program_id)
        _integer(after_sequence)
        _require(type(limit) is int and 1 <= limit <= MAX_PAGE, "invalid handoff page limit")
        with self._session() as reader:
            head = self._head(reader, program_id) if self._schema(reader) else None
            if head is None:
                return {
                    "schema": SCHEMA,
                    "program_id": program_id,
                    "state": "uninitialized",
                    "execution_authorized": False,
                    "consumer_bound": False,
                    "receipts": [],
                    "next_sequence": None,
                    "blockers": [],
                }
            receipt, digest = head
            witness, tasks, valid = self._semantic(reader, receipt["descriptor"])
            blockers = []
            if not valid or witness != receipt["witness_sha256"]:
                blockers.append("semantic_inputs_changed")
            task_clause = ",".join("?" for _ in tasks) or "NULL"
            where, params = f"program_id=? OR task_id IN ({task_clause})", (program_id, *tasks)
            workers = reader.rows("lifecycle.lifecycle_worker_ownership", _OWNER, where, params)
            self.lifecycle._validate_worker_rows([tuple(row.values()) for row in workers])
            if receipt["state"] == "owned":
                if (
                    len(workers) != 1
                    or _sha(_canonical(tuple(workers[0].values()))) != receipt["owner_sha256"]
                ):
                    blockers.append("recovery_required")
            elif workers:
                blockers.append("worker_conflict")
            reservations = reader.rows(
                "lifecycle.lifecycle_reservations", ("reservation_kind", *_OWNER[1:]), where, params
            )
            self.lifecycle._validate_rows([tuple(row.values()) for row in reservations])
            if reservations:
                blockers.append("lifecycle_action_active")
            page = reader.rows(
                _TABLES[1],
                ("receipt_sha256", "sequence"),
                "program_id=? AND sequence>?",
                (program_id, after_sequence),
                order="sequence",
                limit=limit,
                page=True,
            )
            records = [
                self._outcome(
                    self._linked(reader, row["receipt_sha256"], program_id), row["receipt_sha256"]
                )
                for row in page[:limit]
            ]
            return {
                **self._outcome(receipt, digest),
                "program_id": program_id,
                "state": receipt["state"],
                "blockers": blockers,
                "receipts": records,
                "next_sequence": page[limit - 1]["sequence"] if len(page) > limit else None,
            }
