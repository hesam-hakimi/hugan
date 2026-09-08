"""Version-2 immutable metadata and a separate source/lifecycle transaction policy.

Recorded readers import no effectful host or provider. Execution's authorizer is
not reused or enlarged. Only the Program and lifecycle stores can be mutated.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from contextlib import ExitStack, closing, contextmanager
from pathlib import Path

from universal_coding_agent.product.program_continuation_execution_store import (
    MAX_RECORD,
    bounded_json,
    canonical,
    check_schema,
    digest,
    durable,
    identifier,
    integer,
    locked,
    normalized_sql,
    parse_record,
    read_only_pragma,
    require,
    schema_row,
    sha,
)
from universal_coding_agent.product.program_continuation_execution_store import (
    Reader as V3Reader,
)

PROPOSALS = "program_source_candidates_v2"
DECISIONS = "program_source_decisions_v2"
REQUESTS = "program_source_requests_v2"
DDL = {
    PROPOSALS: f"""CREATE TABLE {PROPOSALS} (
        program_id TEXT NOT NULL, task_id TEXT NOT NULL, operation_id TEXT NOT NULL,
        candidate_sha256 TEXT NOT NULL UNIQUE, request_sha256 TEXT NOT NULL,
        PRIMARY KEY(program_id,task_id))""",
    DECISIONS: f"""CREATE TABLE {DECISIONS} (
        candidate_sha256 TEXT PRIMARY KEY, approval_sha256 TEXT NOT NULL,
        receipt_sha256 TEXT, request_sha256 TEXT NOT NULL, approved INTEGER NOT NULL)""",
    REQUESTS: f"""CREATE TABLE {REQUESTS} (
        host_sha256 TEXT NOT NULL, program_id TEXT NOT NULL, request_id TEXT NOT NULL,
        operation_id TEXT NOT NULL, action TEXT NOT NULL, payload_sha256 TEXT NOT NULL,
        baseline_sha256 TEXT NOT NULL, owner_sha256 TEXT NOT NULL, status TEXT NOT NULL,
        response_sha256 TEXT, PRIMARY KEY(host_sha256,program_id,request_id))""",
}
SHARED = {
    "program_source_artifacts": """CREATE TABLE program_source_artifacts (
        sha256 TEXT PRIMARY KEY, content BLOB NOT NULL)""",
    "program_source_heads": """CREATE TABLE program_source_heads (
        program_id TEXT PRIMARY KEY, generation INTEGER NOT NULL,
        source_sha256 TEXT NOT NULL, host_sha256 TEXT NOT NULL,
        initial_receipt_sha256 TEXT NOT NULL, receipt_sha256 TEXT NOT NULL)""",
    "program_source_acceptances": """CREATE TABLE program_source_acceptances (
        candidate_sha256 TEXT PRIMARY KEY, approval_sha256 TEXT NOT NULL,
        receipt_sha256 TEXT NOT NULL, program_id TEXT NOT NULL,
        task_id TEXT NOT NULL, UNIQUE(program_id, task_id))""",
}
INDEX_COLUMNS = {
    "program_source_artifacts": {("sha256",)},
    "program_source_heads": {("program_id",)},
    "program_source_acceptances": {("candidate_sha256",), ("program_id", "task_id")},
    PROPOSALS: {("candidate_sha256",), ("program_id", "task_id")},
    DECISIONS: {("candidate_sha256",)},
    REQUESTS: {("host_sha256", "program_id", "request_id")},
}
PREFIX = "uca-source-"
CANDIDATE_FIELDS = (
    "program_id task_id operation_id host_sha256 revision core_sha256 transition_sha256 "
    "before_sha256 after_sha256 generation predecessor_receipt_sha256 terminal_receipt_sha256"
)
EXACT_FIELDS = (
    "candidate_sha256 revision core_sha256 transition_sha256 before_sha256 generation "
    "predecessor_receipt_sha256 terminal_receipt_sha256"
)
FIELDS = {
    "candidate": CANDIDATE_FIELDS,
    "approval": "program_id operation_id host_sha256 action approval_id request_id approved "
    + EXACT_FIELDS,
    "request": "program_id operation_id host_sha256 action request_id approval_id approved "
    + EXACT_FIELDS,
    "evidence-core": "program_id operation_id task_id execution_schema admission_sha256 "
    "terminal_receipt_sha256 settlement_sha256 terminal_response_sha256 decision_sha256 "
    "checkpoint_sha256 result_sha256 preparation_receipt_sha256 materialization_receipt_sha256 "
    "dependency_sha256 baseline_sha256 source_host_sha256 host_sha256 evidence_sha256 "
    "program_evidence_sha256 filesystem_sha256 origin_sha256 inventory_sha256 "
    "transition_sha256 before_sha256 after_sha256 generation predecessor_receipt_sha256",
    "capture-witness": "program_id operation_id host_sha256 baseline_sha256 owner_sha256 "
    "pins_sha256 checkpoint_sha256 filesystem_sha256 inventory_sha256 core_sha256",
    "acceptance-receipt": "program_id operation_id task_id candidate_sha256 approval_sha256 "
    "core_sha256 transition_sha256 predecessor_sha256 predecessor_receipt_sha256 "
    "terminal_receipt_sha256 source_sha256 generation host_sha256 acceptance_host_sha256 "
    "witness_sha256 materialization_ready execution_authorized automatic_execution",
    "response": "program_id operation_id host_sha256 request_id request_sha256 action status "
    "candidate_sha256 candidate approval_sha256 receipt_sha256 witness_sha256 "
    "execution_authorized automatic_execution materialization_ready",
}
FIELDS = {PREFIX + k + "-2": frozenset(("schema " + v).split()) for k, v in FIELDS.items()}


def record(raw, schema):
    value = bounded_json(raw)
    require(
        type(value) is dict and value.keys() == FIELDS[schema] and value["schema"] == schema,
        "invalid source acceptance v2 record",
    )
    for key, item in value.items():
        if key.endswith("_sha256"):
            digest(item, nullable=True)
        if key in {"program_id", "operation_id", "task_id", "request_id", "approval_id"}:
            if item is not None:
                identifier(item)
        if key in {"revision", "generation"} and item is not None:
            integer(item)
        if key in {"execution_authorized", "automatic_execution", "materialization_ready"}:
            require(item is False, "source acceptance metadata grants no execution")
    if "approved" in value:
        require(
            value["approved"] is None or type(value["approved"]) is bool,
            "source decision must be a strict boolean",
        )
    if "action" in value:
        require(value["action"] in {"preview", "decide"}, "unknown source acceptance action")
    if schema == PREFIX + "candidate-2":
        require(
            value["revision"] == 1 and value["generation"] == 1,
            "only the first final source proposal is supported",
        )
        require(all(value[k] is not None for k in value), "incomplete candidate")
    if schema in {PREFIX + "request-2", PREFIX + "approval-2"}:
        preview = value["action"] == "preview"
        nulls = {
            "approval_id",
            "approved",
            "candidate_sha256",
            "revision",
            "core_sha256",
            "transition_sha256",
            "predecessor_receipt_sha256",
        }
        require(all((value[k] is None) == preview for k in nulls), "request argument shape differs")
        require(value["generation"] == 1, "unsupported source generation")
        for k in ("before_sha256", "terminal_receipt_sha256", "host_sha256"):
            digest(value[k])
        if not preview:
            require(value["revision"] == 1, "unsupported candidate revision")
        if schema == PREFIX + "approval-2":
            require(not preview, "approval is not a preview")
    if schema == PREFIX + "response-2":
        record(canonical(value["candidate"]), PREFIX + "candidate-2")
        require(
            sha(canonical(value["candidate"])) == value["candidate_sha256"],
            "response candidate differs",
        )
        require(value["status"] in {"prepared", "accepted", "rejected"}, "invalid source outcome")
        require(
            (value["approval_sha256"] is None) == (value["status"] == "prepared")
            and (value["receipt_sha256"] is not None) == (value["status"] == "accepted"),
            "source outcome linkage differs",
        )
    return value


class Reader(V3Reader):
    def __init__(self, connection):
        super().__init__(connection)
        self.artifact_total, self.artifact_sizes = 0, {}

    def artifact(self, value, *, maximum=24_000_000):
        """Hash stored opaque bytes in bounded chunks, without decoding source/evidence.

        This separate budget never relaxes the small canonical metadata budget.
        The caller's transaction pins the rows for the complete logical read.
        """
        from universal_coding_agent.product.program_source_capture_budget import charge

        digest(value)
        require(0 < maximum <= 24_000_000, "invalid stored artifact bound")
        if value in self.artifact_sizes:
            require(self.artifact_sizes[value] <= maximum, "stored artifact exceeds bound")
            return
        header = self.connection.execute(
            "SELECT length(content),typeof(content) FROM program_source_artifacts WHERE sha256=?",
            (value,),
        ).fetchone()
        require(
            header is not None and header[1] == "blob" and 0 < header[0] <= maximum,
            "missing or oversized source lineage artifact",
        )
        size = header[0]
        require(self.artifact_total + size <= 256_000_000, "stored lineage aggregate bound")
        self.artifact_total += size
        hasher = hashlib.sha256()
        for offset in range(0, size, 65_536):
            length = min(65_536, size - offset)
            charge(length)
            selected = self.connection.execute(
                "SELECT CASE WHEN typeof(content)='blob' AND length(content)=? "
                "THEN substr(content,?,?) END FROM program_source_artifacts WHERE sha256=?",
                (size, offset + 1, length, value),
            ).fetchone()
            require(
                selected is not None and type(selected[0]) is bytes and len(selected[0]) == length,
                "stored source lineage artifact changed",
            )
            hasher.update(selected[0])
        require(hasher.hexdigest() == value, "stored source lineage artifact hash differs")
        self.artifact_sizes[value] = size

    def raw(self, value, *, maximum=MAX_RECORD):
        digest(value)
        if value in self.cache:
            require(len(self.cache[value]) <= maximum, "cached record exceeds metadata bound")
            return self.cache[value]
        header = self.connection.execute(
            "SELECT length(content),typeof(content) FROM program_source_artifacts WHERE sha256=?",
            (value,),
        ).fetchone()
        require(header is not None and header[1] == "blob", "missing source metadata")
        self.budget(header[0], maximum)
        selected = self.connection.execute(
            "SELECT CASE WHEN typeof(content)='blob' AND length(content)=? "
            "THEN substr(content,1,?) END FROM program_source_artifacts WHERE sha256=?",
            (header[0], header[0], value),
        ).fetchone()
        require(
            selected is not None and type(selected[0]) is bytes and sha(selected[0]) == value,
            "source metadata bytes differ",
        )
        self.cache[value] = selected[0]
        return selected[0]

    def record(self, value, schema):
        raw = self.raw(value)
        return record(raw, schema) if schema in FIELDS else parse_record(raw, schema)

    def metadata(self, value):
        raw = self.raw(value)
        # Legacy c1 no-follow observations contain unsigned 64-bit filesystem
        # inode numbers. New control revisions continue to use the v3 integer parser.
        depth, quoted, escaped = 0, False, False
        for byte in raw:
            if quoted:
                if escaped:
                    escaped = False
                elif byte == 92:
                    escaped = True
                elif byte == 34:
                    quoted = False
            elif byte == 34:
                quoted = True
            elif byte in (91, 123):
                depth += 1
                require(depth <= 8, "legacy metadata depth exceeded")
            elif byte in (93, 125):
                depth -= 1

        def pairs(items):
            require(
                len(items) <= 64 and len({k for k, _ in items}) == len(items),
                "duplicate/oversized legacy metadata object",
            )
            require(all(len(k.encode()) <= 128 for k, _ in items), "legacy metadata key bound")
            return dict(items)

        def invalid(value):
            raise ValueError("invalid legacy metadata number")

        result = json.loads(
            raw, object_pairs_hook=pairs, parse_constant=invalid, parse_float=invalid
        )

        def check(item):
            if type(item) is int:
                require(-(2**63) < item < 2**64, "legacy metadata integer bound")
            elif type(item) is str:
                require(len(item.encode()) <= 4096, "legacy metadata string bound")
            elif type(item) is list:
                require(len(item) <= 1024, "legacy metadata list bound")
                for child in item:
                    check(child)
            elif type(item) is dict:
                for child in item.values():
                    check(child)

        check(result)
        require(canonical(result) == raw, "legacy metadata is not canonical")
        return result

    def rows(self, table, fields, where="1", args=(), *, order="", limit=100, page=False):
        require(1 <= limit <= 100 and not page, "source history bound exceeded")
        # Bounded actual projection as well as a same-snapshot size check.
        suffix = f" FROM {table} WHERE {where}"
        suffix += (" ORDER BY " + order) if order else ""
        suffix += f" LIMIT {limit + 1}"
        sizes = self.connection.execute(
            "SELECT " + ",".join(f"length(CAST({k} AS BLOB)),typeof({k})" for k in fields) + suffix,
            args,
        ).fetchall()
        require(len(sizes) <= limit, "source row count exceeded")
        for row in sizes:
            for i in range(0, len(row), 2):
                require(row[i + 1] in {"text", "integer", "null"}, "invalid source row type")
                self.budget(row[i] or 0, 4096 if "ref" in fields[i // 2] else 128)
        selected = self.connection.execute(
            "SELECT "
            + ",".join(
                f"CASE WHEN typeof({k}) IN ('text','integer','null') "
                f"AND coalesce(length(CAST({k} AS BLOB)),0)<=4096 THEN {k} END"
                for k in fields
            )
            + suffix,
            args,
        ).fetchall()
        return [dict(zip(fields, row, strict=True)) for row in selected]


def schema(connection, *, initialize=False):
    check_schema(connection, control=False)
    present = [schema_row(connection, name) is not None for name in DDL]
    require(not any(present) or all(present), "partial acceptance schema cannot be repaired")
    if initialize and not any(present):
        for statement in DDL.values():
            connection.execute(statement)
    for name, statement in {**SHARED, **DDL}.items():
        found = schema_row(connection, name)
        require(
            found is not None
            and found[0] == "table"
            and normalized_sql(found[1]) == normalized_sql(statement),
            "source acceptance table/unique barrier differs",
        )
        require(
            connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type='trigger' AND tbl_name=?", (name,)
            ).fetchone()
            is None,
            "source acceptance table has a trigger",
        )
        indexes = connection.execute(f"PRAGMA main.index_list({name})").fetchmany(4)
        require(len(indexes) == len(INDEX_COLUMNS[name]), "source ledger index set differs")
        columns = set()
        for index in indexes:
            require(
                type(index[1]) is str
                and len(index[1]) <= 128
                and index[1].startswith("sqlite_autoindex_" + name + "_")
                and index[2] == 1
                and index[3] in {"pk", "u"}
                and index[4] == 0,
                "source ledger unique index differs",
            )
            parts = connection.execute(f"PRAGMA main.index_info({index[1]})").fetchmany(4)
            require(
                all(type(part[2]) is str and len(part[2]) <= 128 for part in parts),
                "source ledger index column differs",
            )
            columns.add(tuple(part[2] for part in parts))
        require(columns == INDEX_COLUMNS[name], "source ledger uniqueness columns differ")


class AcceptanceStore:
    def __init__(self, continuation):
        self.v3 = continuation
        self.connection = continuation.store.connection

    def boundary(self, name):
        """Fault-observation seam. No recovery authority is associated with a seam."""

    @contextmanager
    def transaction(self, *, initialize=False, label="read", verify=None):
        owner, db = self.v3.db, self.connection
        with ExitStack() as stack:
            for obj in owner.objects:
                stack.enter_context(locked(obj._lock))
            require(not db.in_transaction, "nested source acceptance transaction")
            owner.pins()
            for i, original in enumerate(owner.originals):
                durable(original, ("main",), rollback=i in {0, 2})
            durable(db, ("main", "lifecycle"), rollback=True)
            durable(db, ("control", "safe", "remote"), rollback=False)
            stack.enter_context(locked(self.v3.store.safe.control.cancellation._lock))
            trusted = db.execute("PRAGMA trusted_schema").fetchone()[0]
            db.execute("PRAGMA trusted_schema=OFF")
            allowed = {
                "main": {
                    **{
                        name: {sqlite3.SQLITE_INSERT}
                        for name in (
                            PROPOSALS,
                            DECISIONS,
                            "program_source_acceptances",
                            "program_source_artifacts",
                        )
                    },
                    REQUESTS: {sqlite3.SQLITE_INSERT, sqlite3.SQLITE_UPDATE},
                    "program_source_heads": {sqlite3.SQLITE_UPDATE},
                },
                "lifecycle": {
                    "lifecycle_worker_ownership": {sqlite3.SQLITE_INSERT, sqlite3.SQLITE_DELETE}
                },
            }

            def authorizer(action, name, column, database, trigger):
                if trigger:
                    return sqlite3.SQLITE_DENY
                if action == sqlite3.SQLITE_PRAGMA:
                    return (
                        sqlite3.SQLITE_OK if read_only_pragma(name, column) else sqlite3.SQLITE_DENY
                    )
                if action in {sqlite3.SQLITE_INSERT, sqlite3.SQLITE_UPDATE, sqlite3.SQLITE_DELETE}:
                    ok = (
                        (database == "main" and name == "sqlite_master")
                        if initialize
                        else action in allowed.get(database, {}).get(name, ())
                    )
                    return sqlite3.SQLITE_OK if ok else sqlite3.SQLITE_DENY
                if action in {
                    sqlite3.SQLITE_SELECT,
                    sqlite3.SQLITE_READ,
                    sqlite3.SQLITE_FUNCTION,
                    sqlite3.SQLITE_TRANSACTION,
                    sqlite3.SQLITE_RECURSIVE,
                }:
                    return sqlite3.SQLITE_OK
                ok = (
                    initialize
                    and database == "main"
                    and (
                        action == sqlite3.SQLITE_CREATE_TABLE
                        and name in DDL
                        or action == sqlite3.SQLITE_CREATE_INDEX
                        and name.startswith("sqlite_autoindex_")
                    )
                )
                return sqlite3.SQLITE_OK if ok else sqlite3.SQLITE_DENY

            deadline, ticks = time.monotonic() + 120, 0

            def progress():
                nonlocal ticks
                ticks += 1
                return int(ticks > 20_000 or time.monotonic() >= deadline)

            try:
                db.set_authorizer(authorizer)
                db.set_progress_handler(progress, 1000)
                db.execute("BEGIN IMMEDIATE")
                owner.pins()
                schema(db, initialize=initialize)
                if not initialize:
                    check_schema(db)
                yield Reader(db)
                owner.pins()
                schema(db)
                self.boundary(label + "_before_commit")
                if verify is not None:
                    verify()
                    owner.pins()
                db.commit()
                self.boundary(label + "_after_commit")
            except BaseException:
                if db.in_transaction:
                    db.rollback()
                raise
            finally:
                db.set_authorizer(None)
                db.set_progress_handler(None, 0)
                db.execute(f"PRAGMA trusted_schema={trusted}")

    def put(self, value):
        raw = canonical(value)
        record(raw, value["schema"])
        return self.v3.store._put(raw)


@contextmanager
def read_session(database_path):
    with closing(
        sqlite3.connect(
            Path(database_path).resolve(strict=True).as_uri() + "?mode=ro",
            uri=True,
            isolation_level=None,
            timeout=0.5,
        )
    ) as db:
        db.execute("PRAGMA query_only=ON")
        db.execute("PRAGMA trusted_schema=OFF")
        deadline = time.monotonic() + 2
        db.set_progress_handler(lambda: int(time.monotonic() >= deadline), 1000)
        try:
            db.execute("BEGIN")
            schema(db)
            yield Reader(db)
        finally:
            db.rollback()
