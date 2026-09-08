"""V3 immutable records, bounded historical readers and attached effect transactions.

This module deliberately imports no execution, provider, Program or Safe service.
The read functions open only an existing Program database. Effect transactions
use the caller's actual acceptance connection, never a substituted connection.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import time
from contextlib import ExitStack, closing, contextmanager
from pathlib import Path

MAX_RECORD = 65_536
MAX_TOTAL = 1_048_576
PREFIX = "uca-program-continuation-"
FLAGS = {
    "execution_authorized": False,
    "automatic_execution": False,
    "source_acceptance_authorized": False,
    "consumer_bound": True,
}
FIELDS = {
    "uca-program-source-dispatch-root-3": "schema host_sha256 program_store control_store",
    "uca-program-source-dispatch-guard-3": (
        "schema operation_id program_id task_id thread_id host_sha256 intent_sha256"
    ),
    "uca-program-source-dispatch-intent-3": (
        "schema operation_id program_id phase_id task_id thread_id host_sha256 "
        "preparation_receipt_sha256 preparation_row materialization_row owner_binding_sha256 "
        "edit_protocol dependency_ref dependency_sha256 generation source_sha256 "
        "acceptance_receipt_sha256 materialization_id materialization_receipt_sha256 "
        "origin_repository_url origin_repository_sha256 origin_base_sha origin_tree_sha "
        "derived_git_commit_sha derived_git_tree_sha object_format requirement_sha256 "
        "plan_sha256 policy_sha256 transport_id"
    ),
    "uca-program-source-dispatch-3": "schema intent intent_sha256 guard_sha256",
    PREFIX + "authority-3": (
        "schema admission_sha256 epoch state predecessor_sha256 witness_sha256 "
        "owner_sha256 filesystem_sha256 retained_sha256"
    ),
    PREFIX + "settlement-3": (
        "schema admission_sha256 epoch action request_id invocation_sha256 boundary "
        "checkpoint_sha256 task_sha256 scope_sha256 result_sha256 authority_sha256 "
        "filesystem_sha256 retained_sha256 revoked registrations_absent remote_absence_sha256"
    ),
    PREFIX + "proposal-3": (
        "schema admission_sha256 operation_id program_id parked_epoch parked_receipt_sha256 "
        "settlement_sha256 checkpoint_sha256 task_sha256 scope_sha256 dependency_sha256 "
        "source_sha256 preparation_receipt_sha256 materialization_receipt_sha256 "
        "witness_sha256 authority_sha256 next_action"
    ),
    PREFIX + "scope-decision-3": (
        "schema request_id proposal_sha256 parked_receipt_sha256 parked_epoch "
        "scope_sha256 approval_id approved epoch authority_sha256"
    ),
    PREFIX + "receipt-3": (
        "schema host_sha256 operation_id program_id admission_sha256 sequence "
        "old_epoch epoch state action request_id request_sha256 predecessor_sha256 "
        "settlement_sha256 proposal_sha256 decision_sha256 result_sha256 outcome"
    ),
    PREFIX + "request-3": (
        "schema host_sha256 operation_id program_id request_id action admission_sha256 "
        "expected_state expected_epoch expected_receipt_sha256 proposal_sha256 "
        "scope_sha256 approval_id approved preparation_receipt_sha256"
    ),
    PREFIX + "response-3": (
        "schema operation_id program_id request_id request_status state epoch "
        "admission_sha256 receipt_sha256 proposal_sha256 scope_sha256 result_sha256 "
        "terminal_status execution_authorized automatic_execution "
        "source_acceptance_authorized consumer_bound"
    ),
    PREFIX + "outcome-3": (
        "schema state epoch scope_sha256 result_sha256 terminal_status "
        "execution_authorized automatic_execution source_acceptance_authorized consumer_bound"
    ),
}
FIELDS = {schema: frozenset(fields.split()) for schema, fields in FIELDS.items()}
DISPATCH = "program_source_dispatches_v3"
HEADS = "program_source_continuation_heads_v3"
RECEIPTS = "program_source_continuation_receipts_v3"
REQUESTS = "program_source_continuation_requests_v3"
TABLES = (DISPATCH, HEADS, RECEIPTS, REQUESTS)
_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{1,127}\Z")
_HASH = re.compile(r"[0-9a-f]{64}\Z")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def identifier(value):
    require(type(value) is str and _ID.fullmatch(value), "invalid bounded v3 identifier")


def digest(value, *, nullable=False):
    require(
        (nullable and value is None) or (type(value) is str and _HASH.fullmatch(value)),
        "invalid v3 digest",
    )


def integer(value):
    require(type(value) is int and 0 <= value < 2**63 - 1, "invalid v3 integer")


def canonical(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def bounded_json(raw, *, maximum=MAX_RECORD):
    require(type(raw) is bytes and 0 < len(raw) <= maximum, "v3 metadata byte bound exceeded")
    depth, quoted, escaped = 0, False, False
    for char in raw:
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
            require(depth <= 8, "v3 metadata depth bound exceeded")
        elif char in (93, 125):
            depth -= 1
            require(depth >= 0, "invalid v3 JSON nesting")

    def pairs(items):
        require(len(items) <= 64, "v3 object field bound exceeded")
        result = {}
        for key, value in items:
            require(key not in result and len(key.encode()) <= 128, "invalid v3 JSON key")
            result[key] = value
        return result

    def invalid(_):
        raise ValueError("v3 metadata requires bounded integers")

    value = json.loads(raw, object_pairs_hook=pairs, parse_float=invalid, parse_constant=invalid)

    def check(item):
        if type(item) is str:
            require(len(item.encode()) <= 4096, "v3 scalar byte bound exceeded")
        elif type(item) is int:
            require(-(2**63) < item < 2**63, "v3 integer bound exceeded")
        elif type(item) is list:
            require(len(item) <= 1024, "v3 metadata list bound exceeded")
            for child in item:
                check(child)
        elif type(item) is dict:
            for child in item.values():
                check(child)
        else:
            require(item is None or type(item) is bool, "invalid v3 value")

    check(value)
    require(canonical(value) == raw, "v3 JSON must use its exact canonical encoding")
    return value


def parse_record(raw, schema):
    value = bounded_json(raw)
    require(
        type(value) is dict and value.keys() == FIELDS[schema] and value["schema"] == schema,
        "invalid v3 record schema or fields",
    )
    for key, item in value.items():
        if key.endswith("_sha256"):
            digest(item, nullable=True)
        elif key in {"epoch", "old_epoch", "parked_epoch", "sequence", "expected_epoch"}:
            integer(item)
        elif key in FLAGS:
            require(item is FLAGS[key], "v3 metadata cannot confer authority")
    if schema == "uca-program-source-dispatch-3":
        parse_record(canonical(value["intent"]), "uca-program-source-dispatch-intent-3")
        require(sha(canonical(value["intent"])) == value["intent_sha256"], "v3 intent differs")
    if schema == "uca-program-source-dispatch-root-3":
        for key in ("program_store", "control_store"):
            pin = value[key]
            require(
                type(pin) is list
                and len(pin) == 3
                and type(pin[0]) is str
                and Path(pin[0]).is_absolute(),
                "invalid v3 store pin",
            )
            integer(pin[1])
            integer(pin[2])
    if schema == PREFIX + "receipt-3":
        parse_record(canonical(value["outcome"]), PREFIX + "outcome-3")
    for key in ("program_id", "phase_id", "task_id", "thread_id", "operation_id", "request_id"):
        if key in value:
            identifier(value[key])
    if "operation_id" in value:
        require(re.fullmatch(r"[0-9a-f]{32}", value["operation_id"]), "invalid v3 operation ID")
    if schema.endswith("request-3"):
        action = value["action"]
        require(action in {"admit", "dispatch", "approve_scope"}, "unknown v3 request action")
        require(
            value["expected_state"]
            == {"admit": "absent", "dispatch": "admitted", "approve_scope": "parked_scope"}[action],
            "v3 request state differs",
        )
        for key in ("admission_sha256", "expected_receipt_sha256"):
            require((value[key] is None) == (action == "admit"), "invalid v3 request null field")
        require(
            (value["preparation_receipt_sha256"] is not None) == (action == "admit"),
            "invalid v3 preparation request",
        )
        for key in ("proposal_sha256", "scope_sha256", "approval_id", "approved"):
            require(
                (value[key] is not None) == (action == "approve_scope"),
                "invalid v3 decision request",
            )
        if action == "approve_scope":
            identifier(value["approval_id"])
            require(type(value["approved"]) is bool, "invalid v3 strict scope decision")
    if schema in {PREFIX + "response-3", PREFIX + "outcome-3", PREFIX + "receipt-3"}:
        state = value["state"]
        require(state in {"admitted", "parked_scope", "closed"}, "unknown v3 outcome state")
        require(value["epoch"] == (1 if state == "closed" else 0), "invalid v3 outcome epoch")
        require(
            (value["result_sha256"] is None) == (state == "admitted"), "invalid v3 result reference"
        )
        if "terminal_status" in value:
            require(
                (value["terminal_status"] in {"completed", "blocked", "failed"})
                if state == "closed"
                else value["terminal_status"] is None,
                "invalid v3 terminal status",
            )
        if "scope_sha256" in value:
            require(
                (value["scope_sha256"] is None) == (state == "admitted"),
                "invalid v3 scope reference",
            )
    if schema == PREFIX + "receipt-3":
        action = {"admitted": "admit", "parked_scope": "dispatch", "closed": "approve_scope"}[
            value["state"]
        ]
        require(
            value["action"] == action
            and value["sequence"] == {"admit": 1, "dispatch": 2, "approve_scope": 3}[action]
            and value["old_epoch"] == 0
            and value["outcome"]["state"] == value["state"]
            and value["outcome"]["epoch"] == value["epoch"]
            and value["outcome"]["result_sha256"] == value["result_sha256"],
            "impossible v3 receipt transition",
        )
        require(
            (value["predecessor_sha256"] is None) == (action == "admit")
            and (value["settlement_sha256"] is None) == (action == "admit")
            and (value["proposal_sha256"] is not None) == (action == "approve_scope")
            and (value["decision_sha256"] is not None) == (action == "approve_scope"),
            "invalid v3 receipt null fields",
        )
    if schema == PREFIX + "response-3":
        require(
            value["request_status"] == "completed"
            and (value["proposal_sha256"] is not None) == (value["state"] == "parked_scope"),
            "invalid v3 completed response",
        )
    if schema == PREFIX + "scope-decision-3":
        identifier(value["approval_id"])
        require(
            type(value["approved"]) is bool and value["parked_epoch"] == 0 and value["epoch"] == 1,
            "invalid v3 scope decision",
        )
    if schema == PREFIX + "proposal-3":
        require(
            value["next_action"] == "scope_decision" and value["parked_epoch"] == 0,
            "unsupported v3 proposal action",
        )
    if schema == PREFIX + "settlement-3":
        require(
            value["revoked"] is True
            and value["registrations_absent"] is True
            and (value["action"], value["epoch"], value["boundary"])
            in {("dispatch", 0, "scope"), ("approve_scope", 1, "terminal")},
            "invalid v3 settlement",
        )
    if schema == PREFIX + "authority-3":
        require(
            value["state"]
            in {
                "admitted",
                "discovery_started",
                "discovered",
                "safe_started",
                "resume_started",
                "parked_scope",
                "closed",
            },
            "invalid v3 authority state",
        )
        require(
            (value["owner_sha256"] is None) == (value["state"] in {"parked_scope", "closed"}),
            "invalid v3 owner witness",
        )
    nullable_schemas = {
        PREFIX + "request-3",
        PREFIX + "receipt-3",
        PREFIX + "response-3",
        PREFIX + "outcome-3",
        PREFIX + "authority-3",
    }
    for key, item in value.items():
        if key.endswith("_sha256") and schema not in nullable_schemas:
            digest(item)
    optional_digests = {
        "predecessor_sha256",
        "owner_sha256",
        "result_sha256",
        "scope_sha256",
        "settlement_sha256",
        "proposal_sha256",
        "decision_sha256",
    }
    if schema == PREFIX + "request-3":
        optional_digests |= {
            "admission_sha256",
            "expected_receipt_sha256",
            "preparation_receipt_sha256",
        }
    for key, item in value.items():
        if key.endswith("_sha256") and key not in optional_digests:
            digest(item)
    return value


class Reader:
    def __init__(self, connection):
        self.connection, self.total, self.cache = connection, 0, {}

    def budget(self, n, maximum=MAX_RECORD):
        require(type(n) is int and 0 <= n <= maximum, "v3 read byte bound exceeded")
        self.total += n
        require(self.total <= MAX_TOTAL, "v3 aggregate read bound exceeded")

    def rows(self, table, fields, where="1", args=(), *, order="", limit=100, page=False):
        suffix = f" FROM {table} WHERE {where}"
        if order:
            suffix += " ORDER BY " + order
        suffix += f" LIMIT {limit + 1}"
        sizes = self.connection.execute(
            "SELECT " + ",".join(f"length(CAST({k} AS BLOB)),typeof({k})" for k in fields) + suffix,
            args,
        ).fetchall()
        require(page or len(sizes) <= limit, "v3 row bound exceeded")
        for row in sizes:
            for i in range(0, len(row), 2):
                require(row[i + 1] in {"text", "integer", "null"}, "invalid v3 row field")
                self.budget(row[i] or 0, 4096)
        return [
            dict(zip(fields, row, strict=True))
            for row in self.connection.execute(
                "SELECT " + ",".join(fields) + suffix,
                args,
            ).fetchall()
        ]

    def record(self, value, schema):
        digest(value)
        if value not in self.cache:
            row = self.connection.execute(
                "SELECT length(content),typeof(content) FROM program_source_artifacts "
                "WHERE sha256=?",
                (value,),
            ).fetchone()
            require(row is not None and row[1] == "blob", "missing v3 record")
            self.budget(row[0])
            raw = self.connection.execute(
                "SELECT content FROM program_source_artifacts WHERE sha256=?", (value,)
            ).fetchone()[0]
            require(sha(raw) == value, "v3 record digest differs")
            self.cache[value] = raw
        return parse_record(self.cache[value], schema)

    def receipt(self, value, program_id):
        first, previous, count = None, None, 0
        while value is not None:
            count += 1
            require(count <= 3, "v3 receipt chain exceeds the explicit three-action slice")
            receipt = self.record(value, PREFIX + "receipt-3")
            require(receipt["program_id"] == program_id, "v3 receipt Program differs")
            rows = self.rows(
                RECEIPTS,
                ("operation_id", "program_id", "sequence"),
                "receipt_sha256=?",
                (value,),
                limit=1,
            )
            require(
                len(rows) == 1 and all(rows[0][k] == receipt[k] for k in rows[0]),
                "v3 receipt history is missing",
            )
            requests = self.rows(
                REQUESTS,
                ("payload_sha256", "response_sha256", "status"),
                "host_sha256=? AND program_id=? AND request_id=?",
                (receipt["host_sha256"], program_id, receipt["request_id"]),
                limit=1,
            )
            require(
                len(requests) == 1
                and requests[0]["status"] == "completed"
                and requests[0]["payload_sha256"] == receipt["request_sha256"],
                "v3 predecessor request history is missing",
            )
            payload = self.record(requests[0]["payload_sha256"], PREFIX + "request-3")
            response = self.record(requests[0]["response_sha256"], PREFIX + "response-3")
            require(
                response["receipt_sha256"] == value
                and all(
                    payload[k] == receipt[k]
                    for k in ("operation_id", "program_id", "request_id", "action", "host_sha256")
                )
                and all(
                    response[k] == receipt[k]
                    for k in ("operation_id", "program_id", "request_id", "admission_sha256")
                )
                and all(
                    response[k] == receipt["outcome"][k]
                    for k in receipt["outcome"]
                    if k != "schema"
                ),
                "v3 immutable request history differs",
            )
            if previous is not None:
                require(
                    previous["sequence"] == receipt["sequence"] + 1
                    and previous["operation_id"] == receipt["operation_id"]
                    and previous["admission_sha256"] == receipt["admission_sha256"],
                    "v3 predecessor receipt differs",
                )
            first = first or receipt
            previous, value = receipt, receipt["predecessor_sha256"]
        return first


def closed_foundation(connection, program_id):
    """Validate all inert d2a predecessors without constructing its owner service."""
    from universal_coding_agent.product.program_continuation_handoff import (
        _RECEIPT_FIELDS,
        SCHEMA,
        _descriptor,
        _digest,
        _identifier,
        _integer,
        _strict_json,
    )

    reader = Reader(connection)
    heads = reader.rows(
        "program_continuation_heads",
        ("program_id", "schema", "host_sha256", "epoch", "state", "receipt_sha256"),
        "program_id=?",
        (program_id,),
        limit=1,
    )
    indexes = reader.rows(
        "program_continuation_receipts",
        ("receipt_sha256", "program_id", "sequence"),
        "program_id=?",
        (program_id,),
        order="sequence DESC",
    )
    requests = reader.rows(
        "program_continuation_requests",
        (
            "host_sha256",
            "program_id",
            "request_id",
            "request_sha256",
            "action",
            "epoch",
            "status",
            "receipt_sha256",
        ),
        "program_id=?",
        (program_id,),
    )
    if not heads:
        require(not indexes and not requests, "partial d2a history blocks v3")
        return
    head = heads[0]
    require(
        head["schema"] == SCHEMA and head["state"] == "closed", "active or parked d2a blocks v3"
    )
    _digest(head["host_sha256"])
    _digest(head["receipt_sha256"])
    _integer(head["epoch"])
    require(
        indexes and indexes[0]["receipt_sha256"] == head["receipt_sha256"],
        "closed d2a head differs",
    )
    by_digest = {row["receipt_sha256"]: row for row in indexes}
    by_request = {row["request_id"]: row for row in requests}
    require(
        len(by_digest) == len(indexes) == len(by_request) == len(requests),
        "closed d2a history is incomplete",
    )
    current_digest, later, seen, seen_requests = head["receipt_sha256"], None, set(), set()
    while current_digest:
        require(
            current_digest in by_digest and current_digest not in seen,
            "closed d2a predecessor is missing or cyclic",
        )
        index = by_digest[current_digest]
        size = connection.execute(
            "SELECT length(content),typeof(content) FROM program_continuation_receipts "
            "WHERE receipt_sha256=?",
            (current_digest,),
        ).fetchone()
        require(size is not None and size[1] == "blob", "closed d2a receipt is missing")
        reader.budget(size[0])
        raw = connection.execute(
            "SELECT content FROM program_continuation_receipts WHERE receipt_sha256=?",
            (current_digest,),
        ).fetchone()[0]
        require(sha(raw) == current_digest, "closed d2a receipt digest differs")
        record = _strict_json(raw)
        require(record.keys() == _RECEIPT_FIELDS, "closed d2a receipt fields differ")
        require(
            record["schema"] == SCHEMA
            and record["program_id"] == program_id
            and record["host_sha256"] == head["host_sha256"]
            and record["sequence"] == index["sequence"]
            and record["execution_authorized"] is False
            and record["consumer_bound"] is False,
            "closed d2a receipt binding differs",
        )
        _descriptor(record["descriptor"])
        require(
            record["descriptor"]["program_id"] == program_id,
            "closed d2a descriptor Program differs",
        )
        _integer(record["sequence"])
        _integer(record["epoch"])
        _identifier(record["request_id"])
        for key in (
            "request_sha256",
            "witness_sha256",
            "predecessor_sha256",
            "owner_sha256",
            "released_owner_sha256",
        ):
            _digest(
                record[key],
                empty=key in {"predecessor_sha256", "owner_sha256", "released_owner_sha256"},
            )
        action = record["action"]
        require(
            type(action) is str
            and action in {"create", "park", "claim", "close"}
            and record["state"]
            == {"create": "owned", "claim": "owned", "park": "parked", "close": "closed"}[action],
            "closed d2a transition differs",
        )
        require(
            bool(record["owner_sha256"]) == (record["state"] == "owned")
            and bool(record["released_owner_sha256"]) == (record["state"] != "owned"),
            "closed d2a owner witness differs",
        )
        request = by_request.get(record["request_id"])
        require(
            request is not None
            and request["request_id"] not in seen_requests
            and request["status"] == "completed"
            and request["receipt_sha256"] == current_digest
            and all(
                request[key] == record[key]
                for key in ("host_sha256", "program_id", "request_sha256", "action", "epoch")
            ),
            "closed d2a predecessor request differs",
        )
        if later is None:
            require(
                record["action"] == "close" and record["epoch"] == head["epoch"],
                "d2a history is not an inert closure",
            )
        else:
            require(
                later["sequence"] == record["sequence"] + 1
                and later["epoch"] == record["epoch"] + (later["action"] == "claim")
                and later["descriptor"] == record["descriptor"]
                and later["witness_sha256"] == record["witness_sha256"]
                and record["state"] == ("parked" if later["action"] == "claim" else "owned"),
                "closed d2a predecessor transition differs",
            )
            if later["action"] == "claim":
                require(
                    later["owner_sha256"] != record["released_owner_sha256"],
                    "closed d2a claim reused ownership",
                )
            else:
                require(
                    later["released_owner_sha256"] == record["owner_sha256"],
                    "closed d2a released owner differs",
                )
        if action == "create":
            require(
                record["sequence"] == 1
                and record["epoch"] == 0
                and not record["predecessor_sha256"],
                "invalid initial d2a receipt",
            )
        else:
            require(bool(record["predecessor_sha256"]), "closed d2a predecessor is missing")
        seen.add(current_digest)
        seen_requests.add(record["request_id"])
        current_digest, later = record["predecessor_sha256"], record
    require(
        seen == by_digest.keys() and seen_requests == by_request.keys(),
        "closed d2a history contains unlinked records",
    )


@contextmanager
def locked(lock):
    require(lock.acquire(timeout=2), "v3 host lock contention; explicit diagnosis required")
    try:
        yield
    finally:
        lock.release()


def identity(path):
    path = Path(path).resolve(strict=True)
    info = path.stat()
    require(path.is_file(), "v3 requires existing on-disk stores")
    return [str(path), info.st_dev, info.st_ino]


def durable(connection, aliases, *, rollback):
    for alias in aliases:
        mode = connection.execute(f"PRAGMA {alias}.journal_mode").fetchone()[0]
        sync = connection.execute(f"PRAGMA {alias}.synchronous").fetchone()[0]
        allowed = {"delete", "truncate", "persist"} | (set() if rollback else {"wal"})
        require(mode in allowed and sync in {2, 3}, "v3 requires durable journal synchronization")


def read_only_pragma(name, argument):
    if name in {
        "database_list",
        "journal_mode",
        "synchronous",
        "query_only",
        "trusted_schema",
        "foreign_keys",
        "user_version",
        "application_id",
        "schema_version",
        "page_count",
        "freelist_count",
    }:
        return argument is None
    return name in {"table_info", "table_xinfo", "index_list", "index_info", "index_xinfo"} and (
        type(argument) is str and len(argument) <= 128
    )


DDL = (
    f"""CREATE TABLE {DISPATCH} (
        operation_id TEXT PRIMARY KEY, program_id TEXT NOT NULL, phase_id TEXT NOT NULL,
        task_id TEXT NOT NULL UNIQUE, thread_id TEXT NOT NULL UNIQUE,
        admission_sha256 TEXT NOT NULL UNIQUE, host_sha256 TEXT NOT NULL,
        preparation_receipt_sha256 TEXT NOT NULL UNIQUE, guard_sha256 TEXT NOT NULL)""",
    f"""CREATE TABLE {HEADS} (
        operation_id TEXT PRIMARY KEY, program_id TEXT NOT NULL, epoch INTEGER NOT NULL,
        state TEXT NOT NULL, sequence INTEGER NOT NULL, receipt_sha256 TEXT,
        authority_sha256 TEXT NOT NULL, filesystem_sha256 TEXT NOT NULL,
        retained_sha256 TEXT NOT NULL, task_sha256 TEXT, discovery_sha256 TEXT,
        decision_sha256 TEXT, checkpoint_sha256 TEXT, result_sha256 TEXT,
        proposal_sha256 TEXT, settlement_sha256 TEXT, invocation_sha256 TEXT,
        invocation_state TEXT, invocation_action TEXT, request_id TEXT,
        revision INTEGER NOT NULL)""",
    f"""CREATE UNIQUE INDEX one_active_program_continuation_v3 ON {HEADS}(program_id)
        WHERE state != 'closed'""",
    f"""CREATE TABLE {RECEIPTS} (
        receipt_sha256 TEXT PRIMARY KEY, operation_id TEXT NOT NULL, program_id TEXT NOT NULL,
        sequence INTEGER NOT NULL, UNIQUE(operation_id, sequence))""",
    f"""CREATE TABLE {REQUESTS} (
        host_sha256 TEXT NOT NULL, program_id TEXT NOT NULL, request_id TEXT NOT NULL,
        operation_id TEXT NOT NULL, action TEXT NOT NULL, payload_sha256 TEXT NOT NULL,
        status TEXT NOT NULL, response_sha256 TEXT,
        PRIMARY KEY(host_sha256, program_id, request_id))""",
    """CREATE TABLE control.uca_source_dispatch_tasks_v3 (
        task_id TEXT PRIMARY KEY, thread_id TEXT NOT NULL UNIQUE,
        admission_sha256 TEXT NOT NULL, host_sha256 TEXT NOT NULL)""",
)


def normalized_sql(value):
    # Preserve quoted SQL literals; removing their whitespace would equate
    # semantically different partial-index predicates.
    return "".join(
        part if index % 2 else re.sub(r"\s+", "", part)
        for index, part in enumerate(re.split(r"('(?:''|[^'])*')", value))
    )


def check_schema(connection, *, control=True):
    for statement in DDL:
        match = re.search(r"CREATE (TABLE|UNIQUE INDEX) ([\w.]+)", statement)
        kind, qualified = match.groups()
        alias, name = qualified.split(".") if "." in qualified else ("main", qualified)
        if alias == "control" and not control:
            continue
        row = schema_row(connection, name, alias)
        expected = statement.replace("control.", "", 1) if alias == "control" else statement
        require(
            row is not None
            and row[0] == ("table" if kind == "TABLE" else "index")
            and type(row[1]) is str
            and normalized_sql(row[1]) == normalized_sql(expected),
            "v3 store schema differs from the explicit definition",
        )


def schema_row(connection, name, alias="main"):
    size = connection.execute(
        f"SELECT length(sql),typeof(sql) FROM {alias}.sqlite_master WHERE name=?", (name,)
    ).fetchone()
    if size is None:
        return None
    require(
        size[1] == "text" and type(size[0]) is int and 0 < size[0] <= MAX_RECORD,
        "v3 schema SQL byte bound exceeded",
    )
    return connection.execute(
        f"SELECT type,sql FROM {alias}.sqlite_master WHERE name=?", (name,)
    ).fetchone()


class ContinuationExecutionStore:
    def __init__(self, acceptance, lifecycle):
        self.acceptance, self.lifecycle = acceptance, lifecycle
        self.connection = acceptance.connection
        self.objects = (
            acceptance.programs,
            acceptance.programs.control,
            lifecycle,
            acceptance.safe.remote_operations,
            acceptance,
        )
        self.aliases = ("main", "control", "lifecycle", "remote", "safe")
        self.originals = (
            acceptance.programs.connection,
            acceptance.safe.control.connection,
            lifecycle.connection,
            acceptance.safe.remote_operations.connection,
            acceptance.safe.connection,
        )
        self.identities = tuple(
            identity(db.execute("PRAGMA database_list").fetchone()[2]) for db in self.originals
        )
        require(len({tuple(p[1:]) for p in self.identities}) == 5, "v3 stores must be distinct")
        with locked(acceptance._lock):
            require(not self.connection.in_transaction, "v3 requires a committed acceptance store")
            attached = {row[1]: row[2] for row in self.connection.execute("PRAGMA database_list")}
            if "remote" not in attached:
                self.connection.execute("ATTACH DATABASE ? AS remote", (self.identities[3][0],))
            self.pins()

    def pins(self):
        require(self.acceptance.connection is self.connection, "v3 acceptance connection changed")
        attached = {row[1]: row[2] for row in self.connection.execute("PRAGMA database_list")}
        for alias, pin, original in zip(self.aliases, self.identities, self.originals, strict=True):
            require(
                identity(attached[alias]) == pin
                and identity(original.execute("PRAGMA database_list").fetchone()[2]) == pin,
                "v3 store identity changed",
            )
        require(
            self.acceptance.safe.control is self.objects[1]
            and self.acceptance.safe.remote_operations is self.objects[3],
            "v3 host store object changed",
        )

    def durability(self):
        for i, original in enumerate(self.originals):
            durable(original, ("main",), rollback=i < 3)
        durable(self.connection, ("main", "control", "lifecycle"), rollback=True)
        durable(self.connection, ("safe", "remote"), rollback=False)

    def schema(self):
        check_schema(self.connection)

    @contextmanager
    def transaction(self, *, initialize=False, barrier=None):
        db = self.connection
        with ExitStack() as locks:
            # Existing control APIs take control before cancellation. No adapter
            # callback holds its local lock while acquiring these host locks.
            for obj in self.objects:
                locks.enter_context(locked(obj._lock))
            require(not db.in_transaction, "nested v3 effect transaction is forbidden")
            self.pins()
            self.durability()
            if barrier is not None:
                locks.enter_context(barrier)
            prior_trusted = db.execute("PRAGMA trusted_schema").fetchone()[0]
            db.execute("PRAGMA trusted_schema=OFF")
            allowed = {
                "main": {
                    *TABLES,
                    "program_source_artifacts",
                    "programs",
                    "program_phases",
                    "program_executions",
                },
                "control": {"control_state", "uca_source_dispatch_tasks_v3"},
                "lifecycle": {"lifecycle_worker_ownership"},
            }
            if initialize:
                allowed = {"main": {*TABLES, "sqlite_master"}, "control": {"sqlite_master"}}
            ddl_actions = {
                sqlite3.SQLITE_CREATE_TABLE,
                sqlite3.SQLITE_CREATE_INDEX,
                sqlite3.SQLITE_DROP_TABLE,
                sqlite3.SQLITE_DROP_INDEX,
                sqlite3.SQLITE_ALTER_TABLE,
                sqlite3.SQLITE_CREATE_TRIGGER,
                sqlite3.SQLITE_DROP_TRIGGER,
                sqlite3.SQLITE_CREATE_VIEW,
                sqlite3.SQLITE_DROP_VIEW,
                sqlite3.SQLITE_ATTACH,
                sqlite3.SQLITE_DETACH,
            }

            def authorizer(action, name, column, database, trigger):
                if trigger:
                    return sqlite3.SQLITE_DENY
                if action == sqlite3.SQLITE_PRAGMA:
                    return (
                        sqlite3.SQLITE_OK if read_only_pragma(name, column) else sqlite3.SQLITE_DENY
                    )
                if action in {sqlite3.SQLITE_INSERT, sqlite3.SQLITE_UPDATE, sqlite3.SQLITE_DELETE}:
                    if (
                        not initialize
                        and database == "main"
                        and name in {"program_source_artifacts", DISPATCH, RECEIPTS}
                        and action != sqlite3.SQLITE_INSERT
                    ):
                        return sqlite3.SQLITE_DENY
                    return (
                        sqlite3.SQLITE_OK
                        if name in allowed.get(database, ())
                        else sqlite3.SQLITE_DENY
                    )
                if action in ddl_actions:
                    good = initialize and (
                        action == sqlite3.SQLITE_CREATE_TABLE
                        and (
                            (database == "main" and name in TABLES)
                            or (database == "control" and name == "uca_source_dispatch_tasks_v3")
                        )
                        or action == sqlite3.SQLITE_CREATE_INDEX
                        and (
                            name.startswith("sqlite_autoindex_")
                            or name == "one_active_program_continuation_v3"
                        )
                    )
                    return sqlite3.SQLITE_OK if good else sqlite3.SQLITE_DENY
                return sqlite3.SQLITE_OK

            try:
                deadline, ticks = time.monotonic() + 30, 0

                def progress():
                    nonlocal ticks
                    ticks += 1
                    return int(ticks > 20_000 or time.monotonic() > deadline)

                db.set_progress_handler(progress, 1000)
                db.set_authorizer(authorizer)
                db.execute("BEGIN IMMEDIATE")
                self.pins()
                if not initialize:
                    self.schema()
                for alias, tables in allowed.items():
                    for name in tables - {"sqlite_master"}:
                        require(
                            db.execute(
                                f"SELECT 1 FROM {alias}.sqlite_master "
                                "WHERE type='trigger' AND tbl_name=?",
                                (name,),
                            ).fetchone()
                            is None,
                            "v3 effect table has an unexpected trigger",
                        )
                yield Reader(db)
                self.pins()
                self.boundary("before_commit")
                db.commit()
                self.boundary("after_commit")
            except BaseException:
                if db.in_transaction:
                    db.rollback()
                raise
            finally:
                db.set_authorizer(None)
                db.set_progress_handler(None, 0)
                db.execute(f"PRAGMA trusted_schema={prior_trusted}")

    def boundary(self, name):
        """No-op fault seam for deterministic process-death observations."""

    def persist_locator(self, root):
        from universal_coding_agent.product.program_source_routing import LOCATOR, read_root_locator

        safe = self.acceptance.safe
        path = safe.artifacts.root.parent / LOCATOR
        raw = canonical(root)
        parse_record(raw, root["schema"])
        try:
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        except FileExistsError:
            require(read_root_locator(safe) == root, "immutable v3 root locator differs")
            fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
            writing = False
        else:
            writing = True
        try:
            if writing:
                offset = 0
                while offset < len(raw):
                    size = os.write(fd, raw[offset:])
                    require(size > 0, "v3 root locator write made no progress")
                    offset += size
            os.fsync(fd)
        finally:
            os.close(fd)
        parent = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            os.fsync(parent)
        finally:
            os.close(parent)
        require(read_root_locator(safe) == root, "v3 root locator changed during publication")

    @contextmanager
    def guard_transaction(self):
        """The only v3 write on Safe: immutable root/control and task denial pins."""
        db = self.acceptance.safe.connection
        require(not db.in_transaction, "nested checkpoint guard write is forbidden")
        statements = {
            "uca_source_dispatch_control": """CREATE TABLE uca_source_dispatch_control (
                singleton INTEGER PRIMARY KEY CHECK(singleton = 1),
                control_path TEXT NOT NULL, control_device INTEGER NOT NULL,
                control_inode INTEGER NOT NULL)""",
            "uca_source_dispatch_tasks_v3_guard": """
                CREATE TABLE uca_source_dispatch_tasks_v3_guard (
                guard_key TEXT PRIMARY KEY, task_id TEXT NOT NULL UNIQUE,
                thread_id TEXT NOT NULL UNIQUE, content BLOB NOT NULL)""",
        }
        creating = True

        def authorizer(action, name, column, database, trigger):
            if trigger:
                return sqlite3.SQLITE_DENY
            if action == sqlite3.SQLITE_PRAGMA:
                return sqlite3.SQLITE_OK if read_only_pragma(name, column) else sqlite3.SQLITE_DENY
            if action in {sqlite3.SQLITE_INSERT, sqlite3.SQLITE_UPDATE, sqlite3.SQLITE_DELETE}:
                permitted = database == "main" and (
                    name in statements
                    and action == sqlite3.SQLITE_INSERT
                    or creating
                    and name == "sqlite_master"
                )
                return sqlite3.SQLITE_OK if permitted else sqlite3.SQLITE_DENY
            if action in {sqlite3.SQLITE_CREATE_TABLE, sqlite3.SQLITE_CREATE_INDEX}:
                permitted = (
                    creating
                    and database == "main"
                    and (name in statements or name.startswith("sqlite_autoindex_"))
                )
                return sqlite3.SQLITE_OK if permitted else sqlite3.SQLITE_DENY
            if action in {
                sqlite3.SQLITE_DROP_TABLE,
                sqlite3.SQLITE_DROP_INDEX,
                sqlite3.SQLITE_ALTER_TABLE,
                sqlite3.SQLITE_CREATE_TRIGGER,
                sqlite3.SQLITE_DROP_TRIGGER,
                sqlite3.SQLITE_CREATE_VIEW,
                sqlite3.SQLITE_DROP_VIEW,
                sqlite3.SQLITE_ATTACH,
                sqlite3.SQLITE_DETACH,
            }:
                return sqlite3.SQLITE_DENY
            return sqlite3.SQLITE_OK

        trusted = db.execute("PRAGMA trusted_schema").fetchone()[0]
        db.execute("PRAGMA trusted_schema=OFF")
        db.set_authorizer(authorizer)
        db.set_progress_handler(lambda: 1, 2_000_000)
        try:
            db.execute("BEGIN IMMEDIATE")
            self.pins()
            durable(db, ("main",), rollback=False)
            for name, statement in statements.items():
                found = schema_row(db, name)
                if found is None:
                    db.execute(statement)
                else:
                    require(
                        found[0] == "table"
                        and isinstance(found[1], str)
                        and normalized_sql(found[1]) == normalized_sql(statement),
                        "checkpoint guard schema differs",
                    )
                require(
                    db.execute(
                        "SELECT 1 FROM sqlite_master WHERE type='trigger' AND tbl_name=?", (name,)
                    ).fetchone()
                    is None,
                    "checkpoint guard has a trigger",
                )
            creating = False
            yield
            self.pins()
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.set_authorizer(None)
            db.set_progress_handler(None, 0)
            db.execute(f"PRAGMA trusted_schema={trusted}")

    def initialize(self):
        from universal_coding_agent.product.program_source_routing import table

        with self.transaction(initialize=True):
            present = [table(self.connection, name) for name in TABLES]
            registry = table(self.connection, "uca_source_dispatch_tasks_v3", "control")
            require(
                not any(present) and not registry or all(present) and registry,
                "incomplete v3 schema; initialization cannot repair it",
            )
            if not any(present):
                for statement in DDL:
                    self.connection.execute(statement)
            self.schema()


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
        deadline, ticks = time.monotonic() + 2, 0

        def progress():
            nonlocal ticks
            ticks += 1
            return int(ticks > 2000 or time.monotonic() > deadline)

        db.set_progress_handler(progress, 1000)
        try:
            db.execute("BEGIN")
            check_schema(db, control=False)
            yield Reader(db)
        finally:
            db.rollback()


def _request(reader, program_id, request_id):
    rows = reader.rows(
        REQUESTS,
        (
            "host_sha256",
            "program_id",
            "request_id",
            "operation_id",
            "action",
            "payload_sha256",
            "status",
            "response_sha256",
        ),
        "program_id=? AND request_id=?",
        (program_id, request_id),
        limit=1,
    )
    if not rows:
        return None
    row = rows[0]
    payload = reader.record(row["payload_sha256"], PREFIX + "request-3")
    require(
        all(
            payload[k] == row[k]
            for k in ("host_sha256", "operation_id", "program_id", "request_id", "action")
        ),
        "v3 request binding differs",
    )
    require(row["status"] in {"pending", "completed"}, "invalid v3 request state")
    if row["status"] == "pending":
        require(row["response_sha256"] is None, "pending v3 request has a response")
        return row
    response = reader.record(row["response_sha256"], PREFIX + "response-3")
    require(
        all(response[k] == row[k] for k in ("operation_id", "program_id", "request_id")),
        "v3 response binding differs",
    )
    receipt = reader.receipt(response["receipt_sha256"], program_id)
    require(
        receipt["request_sha256"] == row["payload_sha256"]
        and receipt["request_id"] == request_id
        and receipt["program_id"] == program_id,
        "v3 response receipt differs",
    )
    require(
        response["admission_sha256"] == receipt["admission_sha256"]
        and all(response[k] == receipt["outcome"][k] for k in receipt["outcome"] if k != "schema"),
        "v3 recorded response outcome differs",
    )
    if response["proposal_sha256"]:
        proposal = reader.record(response["proposal_sha256"], PREFIX + "proposal-3")
        require(
            proposal["parked_receipt_sha256"] == response["receipt_sha256"]
            and proposal["admission_sha256"] == response["admission_sha256"]
            and proposal["scope_sha256"] == response["scope_sha256"]
            and proposal["settlement_sha256"] == receipt["settlement_sha256"],
            "v3 recorded proposal differs",
        )
    found = reader.rows(
        RECEIPTS,
        ("operation_id", "program_id", "sequence"),
        "receipt_sha256=?",
        (response["receipt_sha256"],),
        limit=1,
    )
    require(
        len(found) == 1 and all(found[0][k] == receipt[k] for k in found[0]),
        "missing v3 response receipt history",
    )
    row["response"] = response
    return row


def request_result(database_path, program_id, request_id):
    identifier(program_id)
    identifier(request_id)
    with read_session(database_path) as reader:
        row = _request(reader, program_id, request_id)
        if row and row["status"] == "completed":
            return row["response"]
        return {
            "program_id": program_id,
            "request_id": request_id,
            **FLAGS,
            "request_status": "pending" if row else "unknown",
            "blockers": ["recovery_required"],
        }


def status(database_path, program_id, operation_id, *, after_sequence=0, limit=20):
    identifier(program_id)
    identifier(operation_id)
    integer(after_sequence)
    require(type(limit) is int and 1 <= limit <= 100, "invalid v3 page limit")
    with read_session(database_path) as reader:
        rows = reader.rows(
            HEADS,
            (
                "operation_id",
                "program_id",
                "state",
                "epoch",
                "receipt_sha256",
                "request_id",
                "proposal_sha256",
            ),
            "operation_id=? AND program_id=?",
            (operation_id, program_id),
            limit=1,
        )
        require(len(rows) == 1, "v3 operation is missing")
        head = rows[0]
        require(
            head["state"]
            in {
                "admitted",
                "discovery_started",
                "discovered",
                "safe_started",
                "resume_started",
                "parked_scope",
                "closed",
            },
            "unknown v3 head state",
        )
        receipt = reader.receipt(head["receipt_sha256"], program_id)
        page = reader.rows(
            RECEIPTS,
            ("receipt_sha256", "sequence"),
            "operation_id=? AND sequence>?",
            (operation_id, after_sequence),
            order="sequence",
            limit=limit,
            page=True,
        )
        receipts = [
            reader.record(row["receipt_sha256"], PREFIX + "receipt-3") for row in page[:limit]
        ]
        pending = head["state"] not in {"admitted", "parked_scope", "closed"}
        require(
            receipt["operation_id"] == operation_id and receipt["program_id"] == program_id,
            "v3 head receipt differs",
        )
        request = _request(reader, program_id, receipt["request_id"])
        require(request and request["status"] == "completed", "v3 head request is incomplete")
        if not pending:
            require(
                head["state"] == receipt["state"]
                and head["epoch"] == receipt["epoch"]
                and head["proposal_sha256"] == request["response"]["proposal_sha256"],
                "v3 head state differs from recorded outcome",
            )
        return {
            **request["response"],
            "state": "recovery_required" if pending else head["state"],
            "recorded_state": head["state"],
            "recorded_epoch": head["epoch"],
            "current_authority_verified": False,
            "blockers": ["recovery_required"] if pending else [],
            "receipts": receipts,
            "next_sequence": page[limit - 1]["sequence"] if len(page) > limit else None,
        }
