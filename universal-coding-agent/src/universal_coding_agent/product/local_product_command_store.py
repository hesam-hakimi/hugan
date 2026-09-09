"""Exact local Product participation in existing owning transactions.

An active participant is an identity registered by the one host, not caller
data. Claims survive every exception. Only a proven outcome may release a worker.
The immutable root child map never changes; its extensions are ordered, linked
records in the local decision journal, including while a command is pending.
"""

from __future__ import annotations

import sqlite3
import time
from contextlib import ExitStack, contextmanager
from contextvars import ContextVar

from universal_coding_agent.product.local_product_binding import (
    AUTHORITY,
    RESULT_FIELDS,
    check,
    parse_json,
)
from universal_coding_agent.product.program_continuation_execution_store import (
    canonical,
    durable,
    locked,
    normalized_sql,
    read_only_pragma,
    schema_row,
    sha,
)
from universal_coding_agent.product.program_source_acceptance_v2_store import Reader

BINDINGS = "local_product_bindings_v1"
PROGRAMS = "local_product_programs_v1"
REQUESTS = "local_product_requests_v1"
HEADS = "local_product_heads_v1"
QUOTES = "local_product_first_quotes_v1"
DECISIONS = "local_product_decisions_v1"
DDL = {
    BINDINGS: f"""CREATE TABLE {BINDINGS} (
        project_id TEXT PRIMARY KEY, binding_sha256 TEXT NOT NULL UNIQUE)""",
    PROGRAMS: f"""CREATE TABLE {PROGRAMS} (
        program_id TEXT PRIMARY KEY, project_id TEXT NOT NULL, binding_sha256 TEXT NOT NULL,
        mapping_sha256 TEXT NOT NULL UNIQUE)""",
    REQUESTS: f"""CREATE TABLE {REQUESTS} (
        program_id TEXT NOT NULL, request_id TEXT NOT NULL, project_id TEXT NOT NULL,
        binding_sha256 TEXT NOT NULL, sequence INTEGER NOT NULL, action TEXT NOT NULL,
        payload_sha256 TEXT NOT NULL, state TEXT NOT NULL, child_map_sha256 TEXT NOT NULL,
        response_sha256 TEXT, claim_sha256 TEXT NOT NULL,
        PRIMARY KEY(program_id,request_id), UNIQUE(program_id,sequence),
        CHECK(state IN ('pending','completed')),
        CHECK((state='pending')=(response_sha256 IS NULL)))""",
    HEADS: f"""CREATE TABLE {HEADS} (
        program_id TEXT PRIMARY KEY, revision INTEGER NOT NULL, last_receipt_sha256 TEXT,
        pending_request_id TEXT, next_sequence INTEGER NOT NULL)""",
    QUOTES: f"""CREATE TABLE {QUOTES} (
        program_id TEXT NOT NULL, task_id TEXT NOT NULL, quote_sha256 TEXT NOT NULL UNIQUE,
        request_id TEXT NOT NULL, PRIMARY KEY(program_id,task_id))""",
    DECISIONS: f"""CREATE TABLE {DECISIONS} (
        program_id TEXT NOT NULL, request_id TEXT NOT NULL, sequence INTEGER NOT NULL,
        kind TEXT NOT NULL, record_sha256 TEXT NOT NULL UNIQUE,
        PRIMARY KEY(program_id,request_id,sequence))""",
}
INDEXES = {
    BINDINGS: {("project_id",), ("binding_sha256",)},
    PROGRAMS: {("program_id",), ("mapping_sha256",)},
    REQUESTS: {("program_id", "request_id"), ("program_id", "sequence")},
    HEADS: {("program_id",)},
    QUOTES: {("program_id", "task_id"), ("quote_sha256",)},
    DECISIONS: {("program_id", "request_id", "sequence"), ("record_sha256",)},
}
_ACTIVE = ContextVar("uca_local_product_participation", default=None)


def schema(db, *, initialize=False):
    present = [schema_row(db, name) for name in DDL]
    check(all(present) or initialize and not any(present), "recorded_evidence_invalid")
    for name, statement in DDL.items():
        found = schema_row(db, name)
        if found is None:
            db.execute(statement)
            found = schema_row(db, name)
        check(
            found[0] == "table" and normalized_sql(found[1]) == normalized_sql(statement),
            "recorded_evidence_invalid",
        )
        check(
            db.execute(
                "SELECT 1 FROM sqlite_master WHERE type='trigger' AND tbl_name=?", (name,)
            ).fetchone()
            is None,
            "recorded_evidence_invalid",
        )
        indexes = db.execute(f"PRAGMA index_list('{name}')").fetchall()
        actual = set()
        for index in indexes:
            check(
                index[1].startswith("sqlite_autoindex_")
                and index[2] == 1
                and index[3] in {"pk", "u"}
                and index[4] == 0,
                "recorded_evidence_invalid",
            )
            actual.add(tuple(r[2] for r in db.execute(f"PRAGMA index_info('{index[1]}')")))
        check(actual == INDEXES[name], "recorded_evidence_invalid")
    unexpected = db.execute(
        "SELECT name FROM sqlite_master WHERE name GLOB 'local_product_*' LIMIT 100"
    ).fetchall()
    check({r[0] for r in unexpected} == set(DDL), "unsupported_version")


def active(connection):
    """Only the exact host-registered live participant may enlarge a SQL seam."""
    part = _ACTIVE.get()
    if part is None:
        return None
    check(
        type(part) is LocalProductParticipation
        and part.store.connection is connection
        and part.host.participants.get(part.key) is part,
        "recovery_required",
    )
    return part


def participation_sql(connection, action, name, database):
    part = active(connection)
    if part is None or database != "main":
        return False
    allowed = {
        REQUESTS: {sqlite3.SQLITE_INSERT, sqlite3.SQLITE_UPDATE},
        HEADS: {sqlite3.SQLITE_UPDATE},
        QUOTES: {sqlite3.SQLITE_INSERT},
        DECISIONS: {sqlite3.SQLITE_INSERT},
    }
    return action in allowed.get(name, ())


def current_participant():
    part = _ACTIVE.get()
    return active(part.store.connection) if type(part) is LocalProductParticipation else None


def require_managed_command(source, program, actions, *, claimed=True, owner=None, child=None):
    """Deny raw managed entry; this check adds no legacy authority or proof."""
    from universal_coding_agent.product.local_product_binding import local_program_route

    if not local_program_route(source.programs.database_path, program):
        return None
    part = active(source.connection)
    check(
        part is not None
        and part.host.source is source
        and part.key[0] == program
        and part.payload["action"] in actions,
        "recovery_required",
    )
    if child is not None:
        check(child in {part.child_id, part.child_id + "-admit"}, "request_conflict")
    if claimed:
        row = source.connection.execute(
            f"SELECT r.state,r.claim_sha256,h.pending_request_id "
            f"FROM {REQUESTS} r JOIN {HEADS} h USING(program_id) "
            "WHERE r.program_id=? AND r.request_id=?",
            part.key,
        ).fetchone()
        check(
            row is not None
            and tuple(row) == ("pending", part.claim_sha, part.key[1])
            and part.owner_token is not None
            and (owner is None or owner == part.owner_token),
            "recovery_required",
        )
    return part


class LocalProductStore:
    def __init__(self, host):
        self.host = host
        self.owner = host.continuation.db
        self.source = host.source
        self.connection = self.source.connection

    def put(self, value):
        raw = value if type(value) is bytes else canonical(value)
        return self.source._put(raw)

    def get(self, value, *, maximum=65_536):
        return parse_json(
            Reader(self.connection).raw(value, maximum=maximum),
            maximum=maximum,
            strings=65_536,
            canonical_only=True,
        )

    def boundary(self, name):
        """Deterministic fault boundary; never recovery authority."""

    @contextmanager
    def transaction(self, *, initialize=False, participant=None, barrier=None):
        """Program/lifecycle atomic writes; control/Safe/remote writer exclusion.

        This independent policy preserves the v3 execution and v2 acceptance
        authorizers. No provider invocation occurs in this transaction.
        """
        db, owner = self.connection, self.owner
        with ExitStack() as stack:
            for obj in owner.objects:
                stack.enter_context(locked(obj._lock))
            check(not db.in_transaction, "store_unavailable")
            owner.pins()
            for index, original in enumerate(owner.originals):
                durable(original, ("main",), rollback=index in {0, 2})
            durable(db, ("main", "lifecycle"), rollback=True)
            durable(db, ("control", "safe", "remote"), rollback=False)
            stack.enter_context(locked(self.source.safe.control.cancellation._lock))
            if barrier is not None:
                stack.enter_context(barrier)
            if participant is not None:
                check(active(db) is participant and participant.store is self, "recovery_required")
            allowed = {
                "main": {
                    REQUESTS: {sqlite3.SQLITE_INSERT, sqlite3.SQLITE_UPDATE},
                    HEADS: {sqlite3.SQLITE_UPDATE},
                    QUOTES: {sqlite3.SQLITE_INSERT},
                    DECISIONS: {sqlite3.SQLITE_INSERT},
                    "program_source_artifacts": {sqlite3.SQLITE_INSERT},
                },
                "lifecycle": {
                    "lifecycle_worker_ownership": {sqlite3.SQLITE_INSERT, sqlite3.SQLITE_DELETE}
                },
            }
            if initialize:
                allowed["main"].update(
                    {n: {sqlite3.SQLITE_INSERT} for n in (BINDINGS, PROGRAMS, HEADS)}
                )
            if participant is not None:
                action = participant.payload["action"]
                if action == "initialize_source":
                    allowed["main"]["program_source_heads"] = {sqlite3.SQLITE_INSERT}
                elif action in {"preview_first_source", "decide_first_source"}:
                    allowed["main"]["program_source_candidates"] = {sqlite3.SQLITE_INSERT}
                    if action == "decide_first_source":
                        allowed["main"]["program_source_acceptances"] = {sqlite3.SQLITE_INSERT}
                        allowed["main"]["program_source_heads"] = {sqlite3.SQLITE_UPDATE}
            trusted = db.execute("PRAGMA trusted_schema").fetchone()[0]
            db.execute("PRAGMA trusted_schema=OFF")

            def authorizer(action, name, column, database, trigger):
                if trigger:
                    return sqlite3.SQLITE_DENY
                if action == sqlite3.SQLITE_PRAGMA:
                    return (
                        sqlite3.SQLITE_OK if read_only_pragma(name, column) else sqlite3.SQLITE_DENY
                    )
                if action in {sqlite3.SQLITE_INSERT, sqlite3.SQLITE_UPDATE, sqlite3.SQLITE_DELETE}:
                    ok = action in allowed.get(database, {}).get(name, ()) or (
                        initialize and database == "main" and name == "sqlite_master"
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

            deadline = time.monotonic() + 120
            ticks = 0

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
                yield Reader(db)
                schema(db)
                owner.pins()
                self.boundary("before_commit")
                if participant is not None:
                    participant.before_commit()
                db.commit()
                self.boundary("after_commit")
            except BaseException:
                if db.in_transaction:
                    db.rollback()
                raise
            finally:
                db.set_authorizer(None)
                db.set_progress_handler(None, 0)
                db.execute(f"PRAGMA trusted_schema={trusted}")


class LocalProductParticipation:
    """A private, exact class joining one command to its actual lower owner."""

    def __init__(self, host, payload):
        self.host, self.store, self.payload = host, host.commands_store, payload
        self.key = (payload["program_id"], payload["request_id"])
        self.owner_token = self.claim_sha = self.response = None
        self.driver = self.capture_budget = self.final_source = None
        self.tasks = ()
        self.final_check = False
        self.reconciliation_observer = None
        self.child_id = "lp-" + sha(
            canonical(
                {
                    "schema": "uca-local-product-child-id-1",
                    "action": payload["action"],
                    "program_id": self.key[0],
                    "request_id": self.key[1],
                    "binding_sha256": payload["expected_binding_sha256"],
                }
            )
        )

    @contextmanager
    def activate(self):
        check(_ACTIVE.get() is None, "recovery_required")
        check(
            type(self) is LocalProductParticipation
            and self.host.participants.get(self.key) is self,
            "recovery_required",
        )
        token = _ACTIVE.set(self)
        try:
            yield self
        finally:
            _ACTIVE.reset(token)
            with self.store.source._lock:
                row = self.store.connection.execute(
                    f"SELECT state FROM {REQUESTS} WHERE program_id=? AND request_id=?", self.key
                ).fetchone()
                if row is None or row[0] == "completed":
                    self.host.participants.pop(self.key, None)
            # Only pending original objects survive. This is no return proof.

    @contextmanager
    def reconcile_context(self, observer):
        check(
            active(self.store.connection) is observer
            and observer.host is self.host
            and self.host.participants.get(self.key) is self
            and self.payload["action"] in {"start_continuation", "decide_continuation_scope"},
            "recovery_required",
        )
        self.reconciliation_observer = observer
        token = _ACTIVE.set(self)
        try:
            yield
        finally:
            _ACTIVE.reset(token)
            self.reconciliation_observer = None

    def before_commit(self):
        if self.final_source is not None and self.final_check:
            self.final_source.recheck(self)
        if self.capture_budget is not None:
            self.capture_budget.recheck_files()
            self.capture_budget.settled()
        if self.final_check:
            self.host.current_binding(self.payload)
            self.host.final_controls(self)
            if self.driver is not None:
                self.driver.returned_proof()
            from universal_coding_agent.product.local_product_status import ProductReader
            from universal_coding_agent.product.program_continuation_execution_store import (
                composed_read_budget,
            )

            with composed_read_budget():
                reader = ProductReader(self.store.connection)
                reader.locator = self.host.locator
                reader.all_requests(self.payload["project_id"], self.key[0])

    def claim(self, *, owner=None, lower_payload=None):
        db, payload = self.store.connection, self.payload
        check(db.in_transaction and active(db) is self, "recovery_required")
        baseline, tasks = self.host.admission(payload)
        self.tasks = tasks
        if owner is None:
            owner = self.host.lifecycle.reserve_program_worker_in_transaction(
                db, self.key[0], task_ids=tasks
            )
        self.owner_token = owner
        exact_owner = self.host.lifecycle.check_program_worker_in_transaction(
            db, self.key[0], task_ids=tasks, owner_token=owner
        )
        head = dict(
            db.execute(f"SELECT * FROM {HEADS} WHERE program_id=?", (self.key[0],)).fetchone()
        )
        check(head["next_sequence"] < 100, "program_busy")
        check(head["pending_request_id"] is None, "program_busy")
        check(head["revision"] == payload["expected_revision"], "revision_conflict")
        root = {
            "schema": "uca-local-product-child-map-1",
            "program_id": self.key[0],
            "request_id": self.key[1],
            "child_request_id": self.child_id,
            "children": [],
        }
        root_sha = self.store.put(root)
        payload_sha = self.store.put(payload)
        claim = {
            "schema": "uca-local-product-claim-1",
            "program_id": self.key[0],
            "request_id": self.key[1],
            "payload_sha256": payload_sha,
            "binding_sha256": self.host.binding_sha256,
            "baseline": baseline,
            "child_map_sha256": root_sha,
            "owner_sha256": sha(canonical(list(exact_owner))),
            "revision": head["revision"],
            "sequence": head["next_sequence"],
            "predecessor_receipt_sha256": head["last_receipt_sha256"],
        }
        self.claim_sha = self.store.put(claim)
        db.execute(
            f"INSERT INTO {REQUESTS} VALUES (?,?,?,?,?,?,?,'pending',?,NULL,?)",
            (
                *self.key,
                payload["project_id"],
                self.host.binding_sha256,
                head["next_sequence"],
                payload["action"],
                payload_sha,
                root_sha,
                self.claim_sha,
            ),
        )
        changed = db.execute(
            f"UPDATE {HEADS} SET pending_request_id=?,next_sequence=next_sequence+1 "
            "WHERE program_id=? AND revision=? AND pending_request_id IS NULL",
            (self.key[1], self.key[0], head["revision"]),
        ).rowcount
        check(changed == 1, "program_busy")
        if lower_payload is not None:
            self.link("lower_claim", {"payload_sha256": self.store.put(lower_payload)})
        self.store.boundary("after_claim")

    def link(self, kind, value):
        db = self.store.connection
        check(db.in_transaction and active(db) is self and self.claim_sha, "recovery_required")
        rows = db.execute(
            f"SELECT sequence,record_sha256 FROM {DECISIONS} "
            "WHERE program_id=? AND request_id=? ORDER BY sequence DESC LIMIT 1",
            self.key,
        ).fetchall()
        sequence, predecessor = (rows[0][0] + 1, rows[0][1]) if rows else (0, self.claim_sha)
        check(sequence < 100, "recorded_evidence_invalid")
        value_sha = self.store.put(value)
        record = {
            "schema": "uca-local-product-child-link-1",
            "program_id": self.key[0],
            "request_id": self.key[1],
            "sequence": sequence,
            "kind": kind,
            "predecessor_sha256": predecessor,
            "value_sha256": value_sha,
        }
        record_sha = self.store.put(record)
        db.execute(
            f"INSERT INTO {DECISIONS} VALUES (?,?,?,?,?)", (*self.key, sequence, kind, record_sha)
        )
        return record_sha

    def finish(self, outcome, result, *, lower=None, released=False):
        db = self.store.connection
        check(db.in_transaction and active(db) is self and self.claim_sha, "recovery_required")
        self.host.current_binding(self.payload)
        claim = self.store.get(self.claim_sha)
        if lower is not None:
            self.link("lower_outcome", lower)
        journal = [
            dict(r)
            for r in db.execute(
                f"SELECT sequence,kind,record_sha256 FROM {DECISIONS} "
                "WHERE program_id=? AND request_id=? ORDER BY sequence",
                self.key,
            )
        ]
        receipt = {
            "schema": "uca-local-product-receipt-1",
            "program_id": self.key[0],
            "project_id": self.payload["project_id"],
            "request_id": self.key[1],
            "request_sha256": claim["payload_sha256"],
            "claim_sha256": self.claim_sha,
            "binding_sha256": self.host.binding_sha256,
            "outcome": outcome,
            "command_revision": claim["revision"] + 1,
            "predecessor_receipt_sha256": claim["predecessor_receipt_sha256"],
            "children": journal,
            "released_owner_sha256": claim["owner_sha256"],
        }
        receipt_sha = self.store.put(receipt)
        fields = RESULT_FIELDS[self.payload["action"]].split()
        check(set(result) <= set(fields), "recorded_evidence_invalid")
        response = {
            "schema": "uca-local-product-response-1",
            "project_id": self.payload["project_id"],
            "program_id": self.key[0],
            "binding_sha256": self.host.binding_sha256,
            "request_id": self.key[1],
            "action": self.payload["action"],
            "request_sha256": claim["payload_sha256"],
            "request_status": "completed",
            "command_revision": claim["revision"] + 1,
            "receipt_sha256": receipt_sha,
            "outcome": outcome,
            "result": {key: result.get(key) for key in fields},
            "authority": AUTHORITY,
        }
        response_raw = canonical(response)
        check(len(response_raw) <= 1_048_576, "recorded_evidence_invalid")
        response_sha = self.store.put(response_raw)
        check(
            db.execute(
                f"UPDATE {REQUESTS} SET state='completed',response_sha256=? "
                "WHERE program_id=? AND request_id=? AND state='pending' AND claim_sha256=?",
                (response_sha, *self.key, self.claim_sha),
            ).rowcount
            == 1,
            "recovery_required",
        )
        check(
            db.execute(
                f"UPDATE {HEADS} SET revision=revision+1,last_receipt_sha256=?,"
                "pending_request_id=NULL WHERE program_id=? AND revision=? "
                "AND pending_request_id=?",
                (receipt_sha, self.key[0], claim["revision"], self.key[1]),
            ).rowcount
            == 1,
            "recovery_required",
        )
        self.store.boundary("after_response")
        if not released:
            self.host.lifecycle.release_program_worker_in_transaction(
                db,
                self.key[0],
                task_ids=self.host.task_ids(self.key[0]),
                owner_token=self.owner_token,
            )
        self.host.lifecycle.check_program_worker_in_transaction(
            db, self.key[0], task_ids=self.host.task_ids(self.key[0]), owner_token=None
        )
        self.store.boundary("after_worker_release")
        self.final_check = True
        self.response = response_raw
        if self.reconciliation_observer is not None:
            self.reconciliation_observer.finish_observation(
                "original_live_seal_completed", self.key[1], "completed", response_sha
            )
        return response

    def claim_observation(self, target):
        db, payload = self.store.connection, self.payload
        check(
            db.in_transaction and active(db) is self and payload["action"] == "reconcile_outcome",
            "recovery_required",
        )
        self.host.current_binding(payload)
        current = self.host.recorded_history(payload).records.get(payload["target_request_id"])
        check(current is not None and current["row"] == target["row"], "request_conflict")
        check(
            all(
                payload[key] == target["payload"][key]
                for key in (
                    "requirement_sha256",
                    "plan_sha256",
                    "program_control_revision",
                    "task_control_revision",
                )
            ),
            "proposal_changed",
        )
        operations = {
            value["operation_id"]
            for kind, value in target["links"]
            if value.get("operation_id")
            and kind in {"preparation", "prepared_base", "continuation"}
        }
        expected_operation = target["payload"].get("operation_id")
        if expected_operation is not None:
            operations.add(expected_operation)
        check(
            operations
            == ({payload["operation_id"]} if payload["operation_id"] is not None else set()),
            "request_conflict",
        )
        head = db.execute(
            f"SELECT revision,next_sequence FROM {HEADS} WHERE program_id=?", (self.key[0],)
        ).fetchone()
        check(head is not None and head[0] == payload["expected_revision"], "revision_conflict")
        check(head[1] < 100, "program_busy")
        check(
            target["row"]["payload_sha256"] == payload["target_request_sha256"]
            and target["claim"]["revision"] == payload["target_revision"],
            "request_conflict",
        )
        others = db.execute(
            f"SELECT payload_sha256 FROM {REQUESTS} WHERE program_id=? "
            "AND action='reconcile_outcome' AND state='pending' LIMIT 101",
            (self.key[0],),
        ).fetchall()
        check(len(others) <= 100, "recorded_evidence_invalid")
        for row in others:
            check(
                self.store.get(row[0])["target_request_id"] != payload["target_request_id"],
                "program_busy",
            )
        root_sha = self.store.put(
            {
                "schema": "uca-local-product-child-map-1",
                "program_id": self.key[0],
                "request_id": self.key[1],
                "child_request_id": self.child_id,
                "children": [],
            }
        )
        payload_sha = self.store.put(payload)
        claim = {
            "schema": "uca-local-product-observation-claim-1",
            "program_id": self.key[0],
            "request_id": self.key[1],
            "payload_sha256": payload_sha,
            "binding_sha256": payload["expected_binding_sha256"],
            "sequence": head[1],
            "revision": head[1],
            "child_map_sha256": root_sha,
            "target_request_id": payload["target_request_id"],
            "target_request_sha256": payload["target_request_sha256"],
            "target_revision": payload["target_revision"],
        }
        self.claim_sha = self.store.put(claim)
        db.execute(
            f"INSERT INTO {REQUESTS} VALUES (?,?,?,?,?,?,?,'pending',?,NULL,?)",
            (
                *self.key,
                payload["project_id"],
                payload["expected_binding_sha256"],
                head[1],
                payload["action"],
                payload_sha,
                root_sha,
                self.claim_sha,
            ),
        )
        check(
            db.execute(
                f"UPDATE {HEADS} SET next_sequence=next_sequence+1 "
                "WHERE program_id=? AND next_sequence=?",
                (self.key[0], head[1]),
            ).rowcount
            == 1,
            "program_busy",
        )
        self.store.boundary("after_observation_claim")

    def finish_observation(self, disposition, target_id, target_status, target_response):
        db = self.store.connection
        participant = active(db)
        check(
            participant is self or participant.reconciliation_observer is self, "recovery_required"
        )
        claim = self.store.get(self.claim_sha)
        check(
            claim["schema"] == "uca-local-product-observation-claim-1"
            and claim["target_request_id"] == target_id,
            "recovery_required",
        )
        target = db.execute(
            f"SELECT state,response_sha256,payload_sha256 FROM {REQUESTS} "
            "WHERE program_id=? AND request_id=?",
            (self.key[0], target_id),
        ).fetchone()
        check(
            target is not None
            and tuple(target) == (target_status, target_response, claim["target_request_sha256"]),
            "recovery_required",
        )
        result = {
            "target_request_id": target_id,
            "target_request_sha256": claim["target_request_sha256"],
            "target_status": target_status,
            "target_response_sha256": target_response,
            "disposition": disposition,
        }
        receipt = {
            "schema": "uca-local-product-observation-receipt-1",
            "program_id": self.key[0],
            "request_id": self.key[1],
            "claim_sha256": self.claim_sha,
            "command_revision": claim["revision"],
            "result": result,
        }
        response = {
            "schema": "uca-local-product-response-1",
            "project_id": self.payload["project_id"],
            "program_id": self.key[0],
            "binding_sha256": self.payload["expected_binding_sha256"],
            "request_id": self.key[1],
            "action": "reconcile_outcome",
            "request_sha256": claim["payload_sha256"],
            "request_status": "completed",
            "command_revision": claim["revision"],
            "receipt_sha256": self.store.put(receipt),
            "outcome": "reconciled" if target_status == "completed" else "blocked",
            "result": result,
            "authority": AUTHORITY,
        }
        self.response = canonical(response)
        check(
            db.execute(
                f"UPDATE {REQUESTS} SET state='completed',response_sha256=? "
                "WHERE program_id=? AND request_id=? AND state='pending' AND claim_sha256=?",
                (self.store.put(self.response), *self.key, self.claim_sha),
            ).rowcount
            == 1,
            "recovery_required",
        )
        self.store.boundary("after_observation_response")
        return self.response

    def source_transaction(self, source):
        check(
            source is self.store.source
            and self.payload["action"]
            in {"initialize_source", "preview_first_source", "decide_first_source"},
            "recovery_required",
        )
        return self.store.transaction(participant=self)

    def source_finalized(self, source, receipt):
        check(source is self.store.source, "recovery_required")
        if self.payload["action"] == "initialize_source":
            self.host.verify_origin(self.key[0])
            return self.finish(
                "initialized",
                {
                    "generation": 0,
                    "source_sha256": receipt["source_sha256"],
                    "initialization_receipt_sha256": self.store.put(receipt),
                },
                lower=receipt,
            )
        check(
            self.payload["action"] == "decide_first_source" and self.final_source is not None,
            "recovery_required",
        )
        return self.final_source.accepted(self, receipt)
