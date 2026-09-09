"""Complete bounded recorded Product reads, with no execution-service imports."""

from __future__ import annotations

import os
import sqlite3
import struct
import sys
import time
from contextlib import ExitStack, closing, contextmanager
from pathlib import Path
from threading import RLock

from universal_coding_agent.product.local_product_binding import (
    ACTION_FIELDS,
    AUTHORITY,
    LOCATOR,
    RESULT_FIELDS,
    check,
    identifier,
    nofollow_bytes,
    parse_json,
    read_locator,
)
from universal_coding_agent.product.local_product_command_store import (
    BINDINGS,
    DECISIONS,
    HEADS,
    PROGRAMS,
    QUOTES,
    REQUESTS,
    schema,
)
from universal_coding_agent.product.program_continuation_execution_store import (
    HEADS as V3_HEADS,
)
from universal_coding_agent.product.program_continuation_execution_store import (
    _request as v3_request,
)
from universal_coding_agent.product.program_continuation_execution_store import (
    canonical,
    check_schema,
    composed_read_budget,
    identity,
    normalized_sql,
    schema_row,
    sha,
)
from universal_coding_agent.product.program_source_acceptance_v2_status import (
    completed_preview,
    completed_request,
)
from universal_coding_agent.product.program_source_acceptance_v2_store import Reader

REQUEST_COLUMNS = tuple(
    (
        "program_id request_id project_id binding_sha256 sequence action payload_sha256 "
        "state child_map_sha256 response_sha256 claim_sha256"
    ).split()
)
RESPONSE_FIELDS = set(
    (
        "schema project_id program_id binding_sha256 request_id action request_sha256 "
        "request_status command_revision receipt_sha256 outcome result authority"
    ).split()
)
CORE_FIELDS = set(
    (
        "schema project_id program_id task_id thread_id phase_id host_sha256 binding_sha256 "
        "before_sha256 after_sha256 generation initialization_receipt_sha256 "
        "transition_sha256 evidence_sha256 checkpoint_sha256 result_sha256 phase_report_sha256 "
        "program_row_sha256 phase_row_sha256 execution_row_sha256 program_control_row_sha256 "
        "task_control_row_sha256 plan_sha256 requirement_sha256 recovery_history_sha256 "
        "source_policy_sha256 git_policy_sha256 test_policy_sha256 origin_inventory_sha256 "
        "execution_inventory_sha256 "
        "filesystem_identity_sha256 first_result_receipt_sha256"
    ).split()
)

# Closing any descriptor for an inode drops this process's POSIX locks, including
# SQLite's locks on other connections. Retain these non-inheritable read-only FDs
# until process exit; release only our OFD locks. This is a bounded observer cache,
# never a worker handle, execution lease, or authority to resume an operation.
_READ_DESCRIPTORS = {}
_READ_DESCRIPTOR_LOCK = RLock()
_MAX_READ_DESCRIPTORS = 256
READ_URI = "?mode=ro&vfs=unix&readonly_shm=1"


@contextmanager
def _pinned_read_lock(path, pin, offset, length):
    check(sys.platform == "linux" and struct.calcsize("l") == 8, "store_unavailable")
    import fcntl

    command = getattr(fcntl, "F_OFD_SETLK", 37)
    key = (str(path), *pin[1:], offset, length)
    with _READ_DESCRIPTOR_LOCK:
        entry = _READ_DESCRIPTORS.get(key)
        if entry is None:
            check(len(_READ_DESCRIPTORS) < _MAX_READ_DESCRIPTORS, "store_unavailable")
            fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
            entry = _READ_DESCRIPTORS[key] = [fd, 0]
        fd = entry[0]
        info = os.fstat(fd)
        check((info.st_dev, info.st_ino) == tuple(pin[1:]), "binding_changed")
        if entry[1] == 0:
            lock = struct.pack("hhqqi", fcntl.F_RDLCK, os.SEEK_SET, offset, length, 0)
            fcntl.fcntl(fd, command, lock + b"\x00" * 4)
        entry[1] += 1
    try:
        yield fd
    finally:
        with _READ_DESCRIPTOR_LOCK:
            entry[1] -= 1
            if entry[1] == 0:
                lock = struct.pack("hhqqi", fcntl.F_UNLCK, os.SEEK_SET, offset, length, 0)
                fcntl.fcntl(fd, command, lock + b"\x00" * 4)


@contextmanager
def read_guard(path):
    """Keep existing database/WAL/SHM bytes unchanged during bounded reads.

    Database shared-range locking prevents exclusive close cleanup. Shared OFD
    locks over WAL recovery/read-lock bytes prevent recovery and read-mark writes,
    including a same-process cached read/write SHM mapping. SQLite can use
    an existing older read mark while reading the latest committed WAL snapshot.
    The readonly_shm URI also prevents a fresh reader from initializing SHM. We do
    not hold or synthesize the DMS lock that would assert another SQLite client.
    A stopped WAL store with absent sidecars is unavailable to pure readers;
    only explicit host startup may open its existing database for normal use.
    """
    pin = identity(path)
    check(pin[0] == str(path), "binding_changed")
    with _pinned_read_lock(path, pin, 0x40000002, 510) as fd, ExitStack() as locks:
        header = os.pread(fd, 100, 0)
        check(
            header[:16] == b"SQLite format 3\x00" and header[18:20] in {b"\x01\x01", b"\x02\x02"},
            "store_unavailable",
        )
        sidecars = []
        if header[18:20] == b"\x02\x02":
            for suffix in ("-wal", "-shm"):
                sidecar = identity(str(path) + suffix)
                check(sidecar[0] == str(path) + suffix, "binding_changed")
                sidecars.append(sidecar)
            # Writer/checkpoint slots 120/121 remain available. A command may
            # hold its writer lock while a reader observes the prior committed
            # pending request. Recovery and all read marks use slots 122..127.
            locks.enter_context(_pinned_read_lock(sidecars[-1][0], sidecars[-1], 122, 6))
        yield
        check(
            identity(path) == pin and all(identity(item[0]) == item for item in sidecars),
            "binding_changed",
        )


@contextmanager
def read_session(path, *, binding_only=False):
    path = Path(path)
    locator = read_locator(path.parent / LOCATOR)
    check(
        locator is not None and list(identity(path)) == locator["program_store"], "binding_changed"
    )
    check(read_locator(Path(locator["safe_root"][0]) / LOCATOR) == locator, "binding_changed")
    with (
        composed_read_budget(),
        read_guard(path),
        ExitStack() as pins,
        closing(
            sqlite3.connect(path.as_uri() + READ_URI, uri=True, isolation_level=None, timeout=0.5)
        ) as db,
    ):
        db.execute("PRAGMA query_only=ON")
        db.execute("PRAGMA trusted_schema=OFF")
        deadline, ticks = time.monotonic() + 5, 0

        def progress():
            nonlocal ticks
            ticks += 1
            return int(ticks > 20_000 or time.monotonic() >= deadline)

        db.set_progress_handler(progress, 1000)
        try:
            db.execute("BEGIN")
            schema(db)
            reader = ProductReader(db)
            reader.locator = locator
            binding = reader.local(locator["binding_sha256"], "uca-local-product-host-binding-1")
            for alias, index in (("control", 1), ("lifecycle", 2), ("remote", 3), ("safe", 4)):
                pin = binding["stores"][index]
                check(list(identity(pin[0])) == pin, "binding_changed")
                if not binding_only:
                    pins.enter_context(read_guard(pin[0]))
                    db.execute(f"ATTACH DATABASE ? AS {alias}", (Path(pin[0]).as_uri() + READ_URI,))
            yield reader
            check(list(identity(path)) == locator["program_store"], "binding_changed")
        finally:
            db.rollback()


class ProductReader(Reader):
    def __init__(self, connection):
        super().__init__(connection)
        self.verified = set()
        self.locator = None
        self.records = {}

    def local(self, value, name=None, *, maximum=65_536):
        record = parse_json(
            self.raw(value, maximum=maximum),
            maximum=maximum,
            strings=65_536 if maximum > 65_536 else 4096,
            canonical_only=True,
        )
        if name is not None:
            check(
                type(record) is dict and record.get("schema") == name, "recorded_evidence_invalid"
            )
        return record

    def mapping(self, project, program=None):
        identifier(project)
        bindings = self.rows(
            BINDINGS, ("project_id", "binding_sha256"), "project_id=?", (project,), limit=1
        )
        check(len(bindings) == 1, "project_not_found")
        binding = self.local(bindings[0]["binding_sha256"], "uca-local-product-host-binding-1")
        check(
            binding["configuration"]["project_id"] == project
            and self.locator["binding_sha256"] == bindings[0]["binding_sha256"],
            "binding_changed",
        )
        if program is not None:
            identifier(program)
            mappings = self.rows(
                PROGRAMS,
                ("program_id", "project_id", "binding_sha256", "mapping_sha256"),
                "program_id=?",
                (program,),
                limit=1,
            )
            check(len(mappings) == 1 and mappings[0]["project_id"] == project, "program_not_bound")
            mapping = self.local(
                mappings[0]["mapping_sha256"], "uca-local-product-program-binding-1"
            )
            check(
                mapping["binding_sha256"]
                == mappings[0]["binding_sha256"]
                == bindings[0]["binding_sha256"]
                and mapping["program_id"] == program
                and mapping["project_id"] == project,
                "binding_changed",
            )
            pinned = [
                {
                    k: v
                    for k, v in mapping.items()
                    if k not in {"schema", "project_id", "binding_sha256"}
                }
            ]
            check(
                pinned == [p for p in binding["programs"] if p["program_id"] == program],
                "binding_changed",
            )
        return bindings[0]["binding_sha256"], binding

    def candidate1(self, value, core=None):
        candidate = self.metadata(value)
        check(
            candidate.get("schema") == "uca-source-candidate-1" and candidate["generation"] == 0,
            "unsupported_version",
        )
        check(
            self.rows(
                "program_source_candidates",
                ("program_id",),
                "candidate_sha256=?",
                (value,),
                limit=1,
            )
            == [{"program_id": candidate["program_id"]}],
            "recorded_evidence_invalid",
        )
        for key in (
            "before_sha256",
            "after_sha256",
            "transition_sha256",
            "evidence_sha256",
            "checkpoint_sha256",
        ):
            self.artifact(candidate[key])
            if core is not None:
                check(candidate[key] == core[key], "recorded_evidence_invalid")
        if core is not None:
            check(
                candidate["program_id"] == core["program_id"]
                and candidate["task_id"] == core["task_id"]
                and all(
                    sha(canonical(candidate["binding"][name])) == core[name + "_row_sha256"]
                    for name in ("program", "phase", "execution", "program_control", "task_control")
                ),
                "recorded_evidence_invalid",
            )
        return candidate

    def first_result(self, value):
        result = self.local(value, "uca-local-first-result-receipt-1")
        for key in ("result_sha256", "checkpoint_sha256"):
            self.artifact(result[key])
        witness = self.local(result["witness_sha256"])
        self.local(witness["recovery_history_sha256"])
        check(
            witness["execution"]["task_id"] == result["task_id"]
            and witness["execution"]["program_id"] == result["program_id"]
            and witness["execution"]["status"] == result["execution_status"],
            "recorded_evidence_invalid",
        )
        return result, witness

    def quote(self, value):
        quote = self.local(value, "uca-local-first-source-quote-1")
        check(
            quote.keys()
            == set(
                (
                    "schema project_id program_id task_id quote_revision core_sha256 "
                    "preview_candidate_sha256 preview_request_sha256 evidence_view_sha256"
                ).split()
            )
            and quote["quote_revision"] == 1,
            "recorded_evidence_invalid",
        )
        core = self.local(quote["core_sha256"], "uca-local-first-source-core-1")
        check(
            core.keys() == CORE_FIELDS
            and core["generation"] == 0
            and all(core[k] == quote[k] for k in ("project_id", "program_id", "task_id")),
            "recorded_evidence_invalid",
        )
        self.candidate1(quote["preview_candidate_sha256"], core)
        for key in (
            "result_sha256",
            "phase_report_sha256",
            "origin_inventory_sha256",
            "execution_inventory_sha256",
            "filesystem_identity_sha256",
        ):
            self.artifact(core[key])
        self.local(core["recovery_history_sha256"])
        result, witness = self.first_result(core["first_result_receipt_sha256"])
        check(
            result["execution_status"] == "completed"
            and result["result_sha256"] == core["result_sha256"]
            and witness["source"]["initial_receipt_sha256"]
            == core["initialization_receipt_sha256"],
            "recorded_evidence_invalid",
        )
        self.view(quote["evidence_view_sha256"], quote["program_id"], core=quote["core_sha256"])
        indexes = self.rows(
            QUOTES, ("program_id", "task_id", "request_id"), "quote_sha256=?", (value,), limit=1
        )
        check(
            len(indexes) == 1
            and indexes[0]["program_id"] == quote["program_id"]
            and indexes[0]["task_id"] == quote["task_id"],
            "recorded_evidence_invalid",
        )
        preview = self.records.get(indexes[0]["request_id"])
        check(
            preview is not None
            and preview["row"]["state"] == "completed"
            and preview["row"]["payload_sha256"] == quote["preview_request_sha256"]
            and preview["response"]["result"]["quote_sha256"] == value,
            "recorded_evidence_invalid",
        )
        return quote, core

    def view(self, value, program, *, core=None):
        view = self.local(value, "uca-local-product-evidence-view-1", maximum=1_048_576)
        check(
            view.keys()
            == set(
                (
                    "schema view_kind program_id task_id core_sha256 source_evidence_sha256 "
                    "chunks redacted complete"
                ).split()
            )
            and view["program_id"] == program
            and type(view["redacted"]) is bool
            and type(view["complete"]) is bool
            and view["complete"]
            and view["view_kind"] in {"scope", "source"},
            "recorded_evidence_invalid",
        )
        check(
            (view["core_sha256"] is None) == (view["view_kind"] == "scope"),
            "recorded_evidence_invalid",
        )
        if core is not None:
            check(view["core_sha256"] == core, "recorded_evidence_invalid")
        if view["view_kind"] == "source":
            linked = self.local(view["core_sha256"])
            check(
                linked["schema"] in {"uca-local-first-source-core-1", "uca-source-evidence-core-2"}
                and linked["program_id"] == program
                and linked["task_id"] == view["task_id"]
                and linked["evidence_sha256"] == view["source_evidence_sha256"],
                "recorded_evidence_invalid",
            )
        self.artifact(view["source_evidence_sha256"])
        for index, chunk in enumerate(view["chunks"]):
            check(
                type(chunk) is dict
                and chunk.keys() == {"index", "relative_path", "kind", "text"}
                and chunk["index"] == index
                and chunk["kind"] in {"scope", "diff", "tests", "review"}
                and type(chunk["text"]) is str
                and len(chunk["text"].encode()) <= 65_536,
                "recorded_evidence_invalid",
            )
            path = chunk["relative_path"]
            check(
                path is None
                or type(path) is str
                and not Path(path).is_absolute()
                and ".." not in Path(path).parts,
                "recorded_evidence_invalid",
            )
        return view

    def link_value(self, kind, value, program):
        if kind == "first_evidence":
            check(
                value.keys() == {"schema", "program_id", "task_id", "evidence_sha256", "artifacts"}
                and value["schema"] == "uca-local-first-evidence-1"
                and value["program_id"] == program
                and type(value["artifacts"]) is list
                and 0 < len(value["artifacts"]) <= 32,
                "recorded_evidence_invalid",
            )
            self.artifact(value["evidence_sha256"])
            for artifact in value["artifacts"]:
                self.artifact(artifact)
        elif kind == "first_result":
            self.first_result(sha(canonical(value)))
        elif kind == "first_scope_proposal":
            check(value["schema"] == "uca-local-first-scope-proposal-1", "unsupported_version")
            receipt, witness = self.first_result(value["first_result_receipt_sha256"])
            check(
                receipt["checkpoint_sha256"] == value["checkpoint_sha256"]
                and all(
                    value[name + "_row_sha256"] == sha(canonical(witness[name]))
                    for name in ("program", "phase", "execution", "program_control", "task_control")
                ),
                "recorded_evidence_invalid",
            )
        elif kind == "first_source_quote":
            self.quote(sha(canonical(value)))
        elif kind == "first_source_decision":
            quote, core = self.quote(value["quote_sha256"])
            old = self.candidate1(value["preview_candidate_sha256"], core)
            new = self.candidate1(value["decision_candidate_sha256"], core)
            check(
                quote["preview_candidate_sha256"] == value["preview_candidate_sha256"]
                and value["preview_candidate_sha256"] != value["decision_candidate_sha256"]
                and old["binding"]["owner_binding_sha256"] != new["binding"]["owner_binding_sha256"]
                and value["core_sha256"] == quote["core_sha256"],
                "recorded_evidence_invalid",
            )
            if value["approved"]:
                receipt = self.metadata(value["source_receipt_sha256"])
                check(
                    receipt["schema"] == "uca-source-acceptance-receipt-1"
                    and receipt["candidate_sha256"] == value["decision_candidate_sha256"],
                    "recorded_evidence_invalid",
                )
            else:
                check(value["source_receipt_sha256"] is None, "recorded_evidence_invalid")
        elif kind in {"lower_claim", "admission", "continuation"}:
            if kind == "continuation":
                for key in (
                    "checkpoint_sha256",
                    "task_sha256",
                    "discovery_sha256",
                    "filesystem_sha256",
                    "retained_sha256",
                    "result_sha256",
                    "report_sha256",
                    "source_sha256",
                ):
                    self.artifact(value[key])
                discovery = self.metadata(value["discovery_sha256"])
                check(
                    type(discovery) is list and 0 < len(discovery) <= 32,
                    "recorded_evidence_invalid",
                )
                for item in discovery:
                    check(
                        type(item) is dict and item.keys() == {"ref", "sha256"},
                        "recorded_evidence_invalid",
                    )
                    self.artifact(item["sha256"])
            if "payload_sha256" in value:
                self.metadata(value["payload_sha256"])
            if "response_sha256" in value:
                response = self.metadata(value["response_sha256"])
                if response["schema"] == "uca-program-continuation-response-3":
                    row = v3_request(self, program, response["request_id"])
                    check(
                        row is not None and row["response_sha256"] == value["response_sha256"],
                        "recorded_evidence_invalid",
                    )
        elif kind in {"materialization", "preparation", "prepared_base"}:
            table = (
                "program_source_materializations"
                if kind == "materialization"
                else "program_execution_bases"
            )
            rows = self.rows(
                table,
                ("program_id", "intent_sha256", "allocation_sha256", "completion_sha256"),
                "operation_id=?",
                (value["operation_id"],),
                limit=1,
            )
            check(len(rows) == 1 and rows[0]["program_id"] == program, "recorded_evidence_invalid")
            for key in ("intent_sha256", "allocation_sha256", "completion_sha256"):
                if rows[0][key]:
                    self.metadata(rows[0][key])
            for key in ("receipt_sha256", "materialization_receipt_sha256"):
                if key in value:
                    self.metadata(value[key])
        elif kind in {"final_source_preview", "final_source_decision"}:
            candidate = completed_preview(self, value["candidate_sha256"])
            response = self.record(value["response_sha256"], "uca-source-response-2")
            actual = completed_request(
                self, response["host_sha256"], program, response["request_id"]
            )
            check(actual == response, "recorded_evidence_invalid")
            if kind == "final_source_preview":
                self.view(value["evidence_view_sha256"], program, core=candidate["core_sha256"])
        elif kind == "lower_outcome":
            schema_name = value.get("schema")
            if schema_name == "uca-source-initialization-1":
                self.artifact(value["source_sha256"])
            elif schema_name == "uca-program-continuation-response-3":
                row = v3_request(self, program, value["request_id"])
                check(
                    row is not None and self.metadata(row["response_sha256"]) == value,
                    "recorded_evidence_invalid",
                )
            elif schema_name == "uca-source-response-2":
                check(
                    completed_request(self, value["host_sha256"], program, value["request_id"])
                    == value,
                    "recorded_evidence_invalid",
                )
            else:
                check(schema_name == "uca-source-acceptance-receipt-1", "unsupported_version")
                self.candidate1(value["candidate_sha256"])
        else:
            check(False, "unsupported_version")

    def all_requests(self, project, program):
        binding_sha, binding = self.mapping(project, program)
        self.namespaces(program)
        heads = self.rows(
            HEADS,
            (
                "program_id",
                "revision",
                "last_receipt_sha256",
                "pending_request_id",
                "next_sequence",
            ),
            "program_id=?",
            (program,),
            limit=1,
        )
        check(len(heads) == 1, "recorded_evidence_invalid")
        head = heads[0]
        check(
            type(head["revision"]) is int
            and type(head["next_sequence"]) is int
            and 0 <= head["revision"] <= head["next_sequence"] <= 100,
            "recorded_evidence_invalid",
        )
        rows = self.rows(
            REQUESTS, REQUEST_COLUMNS, "program_id=?", (program,), order="sequence", limit=100
        )
        check(
            [r["sequence"] for r in rows] == list(range(head["next_sequence"])),
            "recorded_evidence_invalid",
        )
        revision, previous, pending = 0, None, []
        for row in rows:
            observation = row["action"] == "reconcile_outcome"
            payload = self.local(row["payload_sha256"])
            check(
                payload["action"] in ACTION_FIELDS
                and payload.keys()
                == ACTION_FIELDS[payload["action"]]
                | {"project_id", "program_id"}
                | ({"target_request_id"} if payload["action"] == "reconcile_outcome" else set()),
                "recorded_evidence_invalid",
            )
            check(
                all(
                    payload[k] == row[k]
                    for k in ("project_id", "program_id", "request_id", "action")
                )
                and row["project_id"] == project
                and row["binding_sha256"] == binding_sha
                and payload["expected_binding_sha256"] == binding_sha,
                "recorded_evidence_invalid",
            )
            claim = self.local(
                row["claim_sha256"],
                "uca-local-product-observation-claim-1"
                if observation
                else "uca-local-product-claim-1",
            )
            root = self.local(row["child_map_sha256"], "uca-local-product-child-map-1")
            check(
                claim["payload_sha256"] == row["payload_sha256"]
                and claim["sequence"] == row["sequence"]
                and claim["child_map_sha256"] == row["child_map_sha256"]
                and root["children"] == [],
                "recorded_evidence_invalid",
            )
            if observation:
                check(
                    claim["revision"] == row["sequence"]
                    and "owner_sha256" not in claim
                    and claim["target_request_id"] == payload["target_request_id"],
                    "recorded_evidence_invalid",
                )
                target = self.records.get(claim["target_request_id"])
                check(
                    target is not None
                    and target["row"]["payload_sha256"] == claim["target_request_sha256"]
                    and target["claim"]["revision"] == claim["target_revision"],
                    "recorded_evidence_invalid",
                )
            else:
                check(
                    claim["revision"] == revision
                    and claim["predecessor_receipt_sha256"] == previous,
                    "recorded_evidence_invalid",
                )
                self.local(claim["baseline"]["recovery_history_sha256"])
            journal = self.rows(
                DECISIONS,
                ("sequence", "kind", "record_sha256"),
                "program_id=? AND request_id=?",
                (program, row["request_id"]),
                order="sequence",
                limit=100,
            )
            check(
                [r["sequence"] for r in journal] == list(range(len(journal))),
                "recorded_evidence_invalid",
            )
            record = {
                "row": row,
                "payload": payload,
                "claim": claim,
                "journal": journal,
                "response": None,
                "links": [],
            }
            self.records[row["request_id"]] = record
            if row["state"] == "completed":
                response = self.local(
                    row["response_sha256"], "uca-local-product-response-1", maximum=1_048_576
                )
                check(
                    response.keys() == RESPONSE_FIELDS
                    and response["authority"] == AUTHORITY
                    and response["request_status"] == "completed"
                    and response["result"].keys() == set(RESULT_FIELDS[row["action"]].split())
                    and response["request_sha256"] == row["payload_sha256"]
                    and all(
                        response[k] == row[k]
                        for k in (
                            "project_id",
                            "program_id",
                            "request_id",
                            "action",
                            "binding_sha256",
                        )
                    ),
                    "recorded_evidence_invalid",
                )
                if observation:
                    receipt = self.local(
                        response["receipt_sha256"], "uca-local-product-observation-receipt-1"
                    )
                    check(
                        not journal
                        and receipt["claim_sha256"] == row["claim_sha256"]
                        and receipt["command_revision"]
                        == response["command_revision"]
                        == claim["revision"]
                        and response["outcome"]
                        == (
                            "reconciled"
                            if response["result"]["target_status"] == "completed"
                            else "blocked"
                        )
                        and receipt["result"] == response["result"],
                        "recorded_evidence_invalid",
                    )
                    result = response["result"]
                    check(
                        result["target_request_sha256"] == target["row"]["payload_sha256"]
                        and result["target_request_id"] == target["row"]["request_id"],
                        "recorded_evidence_invalid",
                    )
                    if result["target_status"] == "completed":
                        check(
                            result["target_response_sha256"] == target["row"]["response_sha256"]
                            and target["response"] is not None,
                            "recorded_evidence_invalid",
                        )
                    else:
                        check(
                            result["target_status"] == "pending"
                            and result["target_response_sha256"] is None,
                            "recorded_evidence_invalid",
                        )
                else:
                    receipt = self.local(response["receipt_sha256"], "uca-local-product-receipt-1")
                    revision += 1
                    check(
                        receipt["claim_sha256"] == row["claim_sha256"]
                        and receipt["children"] == journal
                        and receipt["predecessor_receipt_sha256"] == previous
                        and receipt["command_revision"] == response["command_revision"] == revision
                        and receipt["outcome"] == response["outcome"]
                        and receipt["released_owner_sha256"] == claim["owner_sha256"],
                        "recorded_evidence_invalid",
                    )
                    previous = response["receipt_sha256"]
                record["response"] = response
                if response["result"].get("evidence_view_sha256"):
                    self.view(response["result"]["evidence_view_sha256"], program)
            else:
                check(
                    row["state"] == "pending" and row["response_sha256"] is None,
                    "recorded_evidence_invalid",
                )
                if not observation:
                    pending.append(row["request_id"])
            predecessor = row["claim_sha256"]
            for item in journal:
                link = self.local(item["record_sha256"], "uca-local-product-child-link-1")
                check(
                    link["predecessor_sha256"] == predecessor
                    and link["kind"] == item["kind"]
                    and link["sequence"] == item["sequence"]
                    and link["program_id"] == program
                    and link["request_id"] == row["request_id"],
                    "recorded_evidence_invalid",
                )
                value = self.local(link["value_sha256"])
                record["links"].append((item["kind"], value))
                self.link_value(item["kind"], value, program)
                predecessor = item["record_sha256"]
        check(
            revision == head["revision"]
            and previous == head["last_receipt_sha256"]
            and pending == ([head["pending_request_id"]] if head["pending_request_id"] else []),
            "recorded_evidence_invalid",
        )
        self.source_history(program)
        return head, binding

    def namespaces(self, program):
        from universal_coding_agent.product.program_source_acceptance_v2_store import (
            DDL as FINAL_DDL,
        )
        from universal_coding_agent.product.program_source_acceptance_v2_store import SHARED
        from universal_coding_agent.product.program_source_routing import V3_TABLES, table

        expected = {
            **SHARED,
            "program_source_candidates": """CREATE TABLE program_source_candidates (
                candidate_sha256 TEXT PRIMARY KEY, program_id TEXT NOT NULL)""",
            "program_source_materializations": """CREATE TABLE program_source_materializations (
                operation_id TEXT PRIMARY KEY, program_id TEXT NOT NULL,
                acceptance_receipt_sha256 TEXT NOT NULL, binding_sha256 TEXT NOT NULL,
                host_sha256 TEXT NOT NULL, intent_sha256 TEXT NOT NULL,
                state TEXT NOT NULL CHECK(state IN ('intent','allocated','complete','abandoned')),
                allocation_sha256 TEXT, completion_sha256 TEXT, abandonment_sha256 TEXT)""",
            "program_execution_bases": """CREATE TABLE program_execution_bases (
                operation_id TEXT PRIMARY KEY, program_id TEXT NOT NULL, phase_id TEXT NOT NULL,
                materialization_id TEXT NOT NULL, host_sha256 TEXT NOT NULL,
                intent_sha256 TEXT NOT NULL,
                state TEXT NOT NULL CHECK(state IN ('intent','allocated','complete','abandoned')),
                allocation_sha256 TEXT, completion_sha256 TEXT, abandonment_sha256 TEXT)""",
        }
        for name, statement in expected.items():
            found = schema_row(self.connection, name)
            check(
                found is not None
                and found[0] == "table"
                and normalized_sql(found[1]) == normalized_sql(statement),
                "recorded_evidence_invalid",
            )
        allowed = set(expected) | set(V3_TABLES) | set(FINAL_DDL) | {"program_source_dispatches"}
        found = self.connection.execute(
            "SELECT substr(name,1,129),type FROM sqlite_master WHERE "
            "(name GLOB 'program_source_*' OR name GLOB 'program_execution_base*') "
            "AND type IN ('table','view') LIMIT 101"
        ).fetchall()
        check(
            len(found) <= 100 and all(name in allowed and kind == "table" for name, kind in found),
            "unsupported_version",
        )
        for name in allowed:
            check(
                self.connection.execute(
                    "SELECT 1 FROM sqlite_master WHERE type='trigger' AND tbl_name=? LIMIT 1",
                    (name,),
                ).fetchone()
                is None,
                "recorded_evidence_invalid",
            )
        if table(self.connection, "program_source_dispatches"):
            check(
                not self.rows(
                    "program_source_dispatches",
                    ("program_id",),
                    "program_id=?",
                    (program,),
                    limit=1,
                ),
                "unsupported_version",
            )

    def source_history(self, program):
        heads = self.rows(
            "program_source_heads",
            (
                "program_id",
                "generation",
                "source_sha256",
                "host_sha256",
                "initial_receipt_sha256",
                "receipt_sha256",
            ),
            "program_id=?",
            (program,),
            limit=1,
        )
        if not heads:
            check(
                not any(
                    r["response"] and r["row"]["action"] == "initialize_source"
                    for r in self.records.values()
                ),
                "recorded_evidence_invalid",
            )
            self.v3_history(program, {"generation": 0})
            return None
        head = heads[0]
        check(
            type(head["generation"]) is int and head["generation"] in {0, 1, 2},
            "unsupported_version",
        )
        initial = self.metadata(head["initial_receipt_sha256"])
        check(
            initial["schema"] == "uca-source-initialization-1"
            and initial["host_sha256"] == head["host_sha256"]
            and initial["attestation"]["identity"]["program_id"] == program
            and initial["source_sha256"] == initial["attestation"]["snapshot_sha256"],
            "recorded_evidence_invalid",
        )
        self.artifact(initial["source_sha256"])
        check(
            any(
                r["response"]
                and r["row"]["action"] == "initialize_source"
                and r["response"]["result"]["initialization_receipt_sha256"]
                == head["initial_receipt_sha256"]
                for r in self.records.values()
            ),
            "recorded_evidence_invalid",
        )
        rows = self.rows(
            "program_source_acceptances",
            ("candidate_sha256", "approval_sha256", "receipt_sha256", "task_id"),
            "program_id=?",
            (program,),
            limit=2,
        )
        check(len(rows) == head["generation"], "recorded_evidence_invalid")
        if head["generation"] == 0:
            check(
                head["source_sha256"] == initial["source_sha256"]
                and head["receipt_sha256"] == head["initial_receipt_sha256"],
                "recorded_evidence_invalid",
            )
        history = []
        for row in rows:
            receipt = self.metadata(row["receipt_sha256"])
            check(
                all(
                    receipt[k] == row[k] for k in ("candidate_sha256", "approval_sha256", "task_id")
                )
                and receipt["program_id"] == program,
                "recorded_evidence_invalid",
            )
            self.artifact(receipt["source_sha256"])
            approval = self.metadata(row["approval_sha256"])
            check(
                approval["candidate_sha256"] == row["candidate_sha256"], "recorded_evidence_invalid"
            )
            if receipt["schema"] == "uca-source-acceptance-receipt-1":
                candidate = self.candidate1(row["candidate_sha256"])
                check(
                    receipt["generation"] == 1
                    and receipt["predecessor_sha256"] == initial["source_sha256"]
                    and receipt["source_sha256"] == candidate["after_sha256"]
                    and approval["approved_transition_sha256"] == candidate["transition_sha256"],
                    "recorded_evidence_invalid",
                )
                matches = [
                    v
                    for r in self.records.values()
                    for kind, v in r["links"]
                    if kind == "first_source_decision"
                    and v["source_receipt_sha256"] == row["receipt_sha256"]
                ]
                check(len(matches) == 1, "recorded_evidence_invalid")
            else:
                check(
                    receipt["schema"] == "uca-source-acceptance-receipt-2"
                    and receipt["generation"] == 2,
                    "unsupported_version",
                )
                response = completed_request(
                    self, approval["host_sha256"], program, approval["request_id"]
                )
                check(
                    response["receipt_sha256"] == row["receipt_sha256"], "recorded_evidence_invalid"
                )
            history.append({**receipt, "receipt_sha256": row["receipt_sha256"]})
        history.sort(key=lambda r: r["generation"])
        if history:
            check(
                [r["generation"] for r in history] == list(range(1, head["generation"] + 1))
                and history[-1]["source_sha256"] == head["source_sha256"]
                and history[-1]["receipt_sha256"] == head["receipt_sha256"],
                "recorded_evidence_invalid",
            )
        self.v3_history(program, head)
        return head

    def v3_history(self, program, source):
        from universal_coding_agent.product.program_source_acceptance_v2_status import (
            source_transition_status_in_reader,
        )
        from universal_coding_agent.product.program_source_acceptance_v2_store import (
            DDL as FINAL_DDL,
        )
        from universal_coding_agent.product.program_source_acceptance_v2_store import (
            schema as final_schema,
        )
        from universal_coding_agent.product.program_source_routing import V3_TABLES, table
        from universal_coding_agent.product.program_source_terminal_proof import terminal_history

        present = [table(self.connection, name) for name in V3_TABLES]
        final_present = [table(self.connection, name) for name in FINAL_DDL]
        check(not any(final_present) or all(final_present), "recorded_evidence_invalid")
        check(not any(present) or all(present), "recorded_evidence_invalid")
        if not any(present):
            check(source["generation"] < 2 and not any(final_present), "recorded_evidence_invalid")
            return
        check_schema(self.connection)
        if all(final_present):
            final_schema(self.connection)

        def no_final_records():
            from universal_coding_agent.product.program_source_acceptance_v2_store import PROPOSALS
            from universal_coding_agent.product.program_source_acceptance_v2_store import (
                REQUESTS as FINAL_REQUESTS,
            )

            check(
                not any(final_present)
                or all(
                    not self.rows(name, ("program_id",), "program_id=?", (program,), limit=1)
                    for name in (PROPOSALS, FINAL_REQUESTS)
                ),
                "recorded_evidence_invalid",
            )

        dispatches = self.rows(
            V3_TABLES[0],
            ("operation_id", "admission_sha256", "guard_sha256", "task_id", "thread_id"),
            "program_id=?",
            (program,),
            limit=1,
        )
        heads = self.rows(
            V3_TABLES[1],
            (
                "operation_id",
                "state",
                "epoch",
                "sequence",
                "receipt_sha256",
                "checkpoint_sha256",
                "result_sha256",
                "settlement_sha256",
                "authority_sha256",
            ),
            "program_id=?",
            (program,),
            limit=1,
        )
        check(len(dispatches) == len(heads), "recorded_evidence_invalid")
        receipts = self.rows(
            V3_TABLES[2],
            ("receipt_sha256", "operation_id", "sequence"),
            "program_id=?",
            (program,),
            order="sequence",
            limit=3,
        )
        requests = self.rows(
            V3_TABLES[3],
            ("request_id", "operation_id", "status"),
            "program_id=?",
            (program,),
            limit=3,
        )
        if not heads:
            check(
                not receipts and not requests and source["generation"] < 2,
                "recorded_evidence_invalid",
            )
            no_final_records()
            return
        row, dispatch = heads[0], dispatches[0]
        check(
            type(row["sequence"]) is int and 1 <= row["sequence"] <= 3,
            "recorded_evidence_invalid",
        )
        check(
            row["operation_id"] == dispatch["operation_id"]
            and [r["sequence"] for r in receipts] == list(range(1, row["sequence"] + 1)),
            "recorded_evidence_invalid",
        )
        envelope = self.record(dispatch["admission_sha256"], "uca-program-source-dispatch-3")
        admission = envelope["intent"]
        self.v3_authority(row["authority_sha256"], dispatch["admission_sha256"])
        self.v3_companions(admission, dispatch)
        check(
            admission["program_id"] == program
            and admission["operation_id"] == row["operation_id"]
            and envelope["guard_sha256"] == dispatch["guard_sha256"],
            "recorded_evidence_invalid",
        )
        for frozen, name in (
            (admission["preparation_row"], "program_execution_bases"),
            (admission["materialization_row"], "program_source_materializations"),
        ):
            check(
                self.rows(name, tuple(frozen), "operation_id=?", (frozen["operation_id"],), limit=1)
                == [frozen],
                "recorded_evidence_invalid",
            )
            for key in ("intent_sha256", "allocation_sha256", "completion_sha256"):
                metadata = self.metadata(frozen[key])
                if key == "completion_sha256":
                    check(
                        metadata["intent_sha256"] == frozen["intent_sha256"]
                        and metadata["allocation_sha256"] == frozen["allocation_sha256"],
                        "recorded_evidence_invalid",
                    )
                    self.artifact(metadata["filesystem_sha256"])
                    if name == "program_execution_bases":
                        attestation = self.metadata(metadata["git_attestation_sha256"])
                        check(
                            attestation["schema"] == "uca-program-git-source-attestation-1"
                            and attestation["identity"]["program_id"] == program
                            and attestation["identity"]["origin_base_sha"]
                            == metadata["derived_git_commit_sha"]
                            and attestation["identity"]["origin_tree_sha"]
                            == metadata["derived_git_tree_sha"]
                            and attestation["object_format"] == admission["object_format"],
                            "recorded_evidence_invalid",
                        )
        self.metadata(admission["dependency_sha256"])
        completed = 0
        for request in requests:
            check(request["operation_id"] == row["operation_id"], "recorded_evidence_invalid")
            actual = v3_request(self, program, request["request_id"])
            check(actual is not None, "recorded_evidence_invalid")
            if actual.get("response", {}).get("proposal_sha256"):
                proposal = self.record(
                    actual["response"]["proposal_sha256"], "uca-program-continuation-proposal-3"
                )
                authority = self.v3_authority(
                    proposal["authority_sha256"], dispatch["admission_sha256"]
                )
                check(
                    authority["witness_sha256"] == proposal["witness_sha256"]
                    and authority["predecessor_sha256"] == proposal["parked_receipt_sha256"],
                    "recorded_evidence_invalid",
                )
            completed += request["status"] == "completed"
        check(completed == len(receipts), "recorded_evidence_invalid")
        for indexed in receipts:
            receipt = self.record(indexed["receipt_sha256"], "uca-program-continuation-receipt-3")
            self.receipt(indexed["receipt_sha256"], program)
            check(indexed["operation_id"] == row["operation_id"], "recorded_evidence_invalid")
            if receipt["settlement_sha256"]:
                settlement = self.record(
                    receipt["settlement_sha256"], "uca-program-continuation-settlement-3"
                )
                self.v3_authority(settlement["authority_sha256"], dispatch["admission_sha256"])
                self.artifact(settlement["checkpoint_sha256"])
                self.artifact(settlement["task_sha256"])
                self.metadata(settlement["result_sha256"])
                self.artifact(settlement["filesystem_sha256"])
                self.artifact(settlement["retained_sha256"])
                binding = self.local(self.locator["binding_sha256"])
                remote_absence = {
                    "store": binding["stores"][3],
                    "task_id": admission["task_id"],
                    "thread_id": admission["thread_id"],
                    "leases": [],
                    "retirements": [],
                }
                check(
                    settlement["remote_absence_sha256"] == sha(canonical(remote_absence)),
                    "recorded_evidence_invalid",
                )
                check(
                    settlement["revoked"]
                    and settlement["registrations_absent"]
                    and settlement["epoch"] == receipt["epoch"]
                    and settlement["request_id"] == receipt["request_id"],
                    "recorded_evidence_invalid",
                )
            if receipt["decision_sha256"]:
                decision = self.record(
                    receipt["decision_sha256"], "uca-program-continuation-scope-decision-3"
                )
                self.v3_authority(decision["authority_sha256"], dispatch["admission_sha256"])
        last = self.record(row["receipt_sha256"], "uca-program-continuation-receipt-3")
        if row["state"] == "closed" and last["outcome"]["terminal_status"] == "completed":
            terminal_history(self, program, row["operation_id"])
            if all(final_present):
                final_schema(self.connection)
                source_transition_status_in_reader(self, program)
        else:
            check(source["generation"] < 2, "recorded_evidence_invalid")
            no_final_records()

    def v3_authority(self, value, admission_sha):
        record = self.record(value, "uca-program-continuation-authority-3")
        check(record["admission_sha256"] == admission_sha, "recorded_evidence_invalid")
        for key in ("witness_sha256", "filesystem_sha256", "retained_sha256"):
            self.artifact(record[key])
        if record["predecessor_sha256"]:
            self.record(record["predecessor_sha256"], "uca-program-continuation-receipt-3")
        return record

    def v3_companions(self, admission, dispatch):
        from universal_coding_agent.product.program_source_routing import GUARD_TABLE
        from universal_coding_agent.product.program_source_routing import LOCATOR as V3_LOCATOR

        binding = self.local(self.locator["binding_sha256"])
        check(admission["host_sha256"] == binding["continuation_host_sha256"], "binding_changed")
        expected = {
            "schema": "uca-program-source-dispatch-root-3",
            "host_sha256": admission["host_sha256"],
            "program_store": binding["stores"][0],
            "control_store": binding["stores"][1],
        }
        raw = nofollow_bytes(Path(binding["configuration"]["safe_state_root"]) / V3_LOCATOR)
        self.budget(len(raw))
        check(raw == canonical(expected), "recorded_evidence_invalid")
        statements = {
            "uca_source_dispatch_control": """CREATE TABLE uca_source_dispatch_control (
                singleton INTEGER PRIMARY KEY CHECK(singleton = 1),
                control_path TEXT NOT NULL, control_device INTEGER NOT NULL,
                control_inode INTEGER NOT NULL)""",
            GUARD_TABLE: """CREATE TABLE uca_source_dispatch_tasks_v3_guard (
                guard_key TEXT PRIMARY KEY, task_id TEXT NOT NULL UNIQUE,
                thread_id TEXT NOT NULL UNIQUE, content BLOB NOT NULL)""",
        }
        for name, statement in statements.items():
            found = schema_row(self.connection, name, "safe")
            check(
                found is not None
                and found[0] == "table"
                and normalized_sql(found[1]) == normalized_sql(statement),
                "recorded_evidence_invalid",
            )
            check(
                self.connection.execute(
                    "SELECT 1 FROM safe.sqlite_master WHERE type='trigger' AND tbl_name=?", (name,)
                ).fetchone()
                is None,
                "recorded_evidence_invalid",
            )
        controls = self.rows(
            "safe.uca_source_dispatch_control",
            ("control_path", "control_device", "control_inode"),
            "singleton=1",
            limit=1,
        )
        check(
            controls
            == [
                dict(
                    zip(
                        ("control_path", "control_device", "control_inode"),
                        binding["stores"][1],
                        strict=True,
                    )
                )
            ],
            "recorded_evidence_invalid",
        )
        registry = self.rows(
            "control.uca_source_dispatch_tasks_v3",
            ("task_id", "thread_id", "admission_sha256", "host_sha256"),
            "task_id=? OR thread_id=?",
            (admission["task_id"], admission["thread_id"]),
            limit=1,
        )
        check(
            registry
            == [
                {
                    "task_id": admission["task_id"],
                    "thread_id": admission["thread_id"],
                    "admission_sha256": dispatch["admission_sha256"],
                    "host_sha256": admission["host_sha256"],
                }
            ],
            "recorded_evidence_invalid",
        )
        guard = {
            "schema": "uca-program-source-dispatch-guard-3",
            "intent_sha256": sha(canonical(admission)),
            **{
                key: admission[key]
                for key in ("operation_id", "program_id", "task_id", "thread_id", "host_sha256")
            },
        }
        check(sha(canonical(guard)) == dispatch["guard_sha256"], "recorded_evidence_invalid")
        for key, task, thread, record in (
            ("root", "", "", expected),
            (admission["operation_id"], admission["task_id"], admission["thread_id"], guard),
        ):
            raw = canonical(record)
            self.budget(len(raw))
            found = self.connection.execute(
                f"SELECT substr(task_id,1,129),substr(thread_id,1,129),"
                "CASE WHEN typeof(content)='blob' AND length(content)=? "
                "THEN substr(content,1,?) END "
                f"FROM safe.{GUARD_TABLE} WHERE guard_key=?",
                (len(raw), len(raw), key),
            ).fetchall()
            check(
                [tuple(row) for row in found] == [(task, thread, raw)], "recorded_evidence_invalid"
            )


def pending(record):
    row, claim = record["row"], record["claim"]
    return {
        "schema": "uca-local-product-pending-1",
        "project_id": row["project_id"],
        "program_id": row["program_id"],
        "request_id": row["request_id"],
        "request_sha256": row["payload_sha256"],
        "request_status": "pending",
        "code": "pending_or_recovery_required",
        "command_revision": claim["revision"],
        "authority": AUTHORITY,
    }


def request_result(path, payload):
    with read_session(path) as reader:
        reader.all_requests(payload["project_id"], payload["program_id"])
        found = reader.records.get(payload["request_id"])
        if found is None:
            return None
        check(found["row"]["payload_sha256"] == sha(canonical(payload)), "request_conflict")
        if found["response"] is None:
            return 202, canonical(pending(found))
        return 200, reader.raw(found["row"]["response_sha256"], maximum=1_048_576)


def project_result(path, project, *, enabled):
    with read_session(path) as reader:
        binding_sha, binding = reader.mapping(project)
        return {
            "schema": "uca-local-product-project-1",
            "project_id": project,
            "display_name": binding["configuration"]["display_name"],
            "configured": True,
            "commands_enabled": enabled,
            "program_ids": sorted(p["program_id"] for p in binding["programs"]),
            "binding_sha256": binding_sha,
            "authority": AUTHORITY,
        }


def recorded_request(path, project, program, request):
    with read_session(path) as reader:
        reader.all_requests(project, program)
        record = reader.records.get(request)
        check(record is not None, "request_not_found")
        return (
            (202, canonical(pending(record)))
            if record["response"] is None
            else (200, reader.raw(record["row"]["response_sha256"], maximum=1_048_576))
        )


def status(path, project, program, *, operation=None, after_sequence=None, limit=20):
    with read_session(path) as reader:
        head, binding = reader.all_requests(project, program)
        db = reader.connection
        control_pin = binding["stores"][1]
        check(list(identity(control_pin[0])) == control_pin, "binding_changed")
        program_rows = reader.rows(
            "programs",
            ("status", "requirement_hash", "plan_hash"),
            "program_id=?",
            (program,),
            limit=1,
        )
        controls = reader.rows(
            "control.control_state",
            ("revision",),
            "entity_type='program' AND entity_id=?",
            (program,),
            limit=1,
        )
        check(len(program_rows) == len(controls) == 1, "recorded_evidence_invalid")
        source_rows = reader.rows(
            "program_source_heads",
            ("generation", "source_sha256", "receipt_sha256"),
            "program_id=?",
            (program,),
            limit=1,
        )
        accepted = source_rows[0] if source_rows else None
        executions = reader.rows(
            "program_executions",
            ("phase_id", "task_id", "thread_id", "status"),
            "program_id=?",
            (program,),
            order="phase_id",
            limit=2,
        )
        execution, task_revision = None, None
        if executions:
            task_order = next(
                p["task_ids"] for p in binding["programs"] if p["program_id"] == program
            )
            check(
                all(row["task_id"] in task_order for row in executions), "recorded_evidence_invalid"
            )
            executions.sort(key=lambda row: task_order.index(row["task_id"]))
            latest = executions[-1]
            control = reader.rows(
                "control.control_state",
                ("revision",),
                "entity_type='task' AND entity_id=?",
                (latest["task_id"],),
                limit=1,
            )
            check(len(control) == 1, "recorded_evidence_invalid")
            task_revision = control[0]["revision"]
            execution = {
                "schema": "uca-program-execution-1",
                "operation_id": None,
                **latest,
                "derived_commit_sha": None,
                "derived_tree_sha": None,
                "result_sha256": None,
            }
            if db.execute("SELECT 1 FROM sqlite_master WHERE name=?", (V3_HEADS,)).fetchone():
                check_schema(db, control=False)
                v3 = reader.rows(
                    "program_source_dispatches_v3",
                    ("operation_id", "admission_sha256", "task_id"),
                    "program_id=?",
                    (program,),
                    limit=1,
                )
                if v3:
                    admission = reader.record(
                        v3[0]["admission_sha256"], "uca-program-source-dispatch-3"
                    )["intent"]
                    check(admission["task_id"] == latest["task_id"], "recorded_evidence_invalid")
                    execution.update(
                        schema="uca-program-source-dispatch-3",
                        operation_id=v3[0]["operation_id"],
                        derived_commit_sha=admission["derived_git_commit_sha"],
                        derived_tree_sha=admission["derived_git_tree_sha"],
                    )
            for item in reader.records.values():
                response = item["response"]
                if response and response["result"].get("task_id") == latest["task_id"]:
                    if "result_sha256" in response["result"]:
                        execution["result_sha256"] = response["result"]["result_sha256"]
        if operation is not None:
            check(
                execution is not None and execution["operation_id"] == operation,
                "operation_not_found",
            )
        requests, decisions = [], {"scope_decision": None, "source_decision": None}
        for item in reader.records.values():
            row, response = item["row"], item["response"]
            if after_sequence is None or row["sequence"] > after_sequence:
                requests.append(
                    {
                        "sequence": row["sequence"],
                        "request_id": row["request_id"],
                        "action": row["action"],
                        "request_status": row["state"],
                        "outcome": response["outcome"] if response else None,
                        "response_sha256": row["response_sha256"],
                    }
                )
            if response and row["action"].startswith("decide_"):
                p = item["payload"]
                name = "scope_decision" if "scope" in row["action"] else "source_decision"
                decisions[name] = {
                    "request_id": row["request_id"],
                    "approved": p["approved"],
                    "proposal_sha256": next(
                        p[k]
                        for k in (
                            "scope_proposal_sha256",
                            "proposal_sha256",
                            "quote_sha256",
                            "candidate_sha256",
                        )
                        if k in p
                    ),
                    "receipt_sha256": response["receipt_sha256"],
                }
        config, current = binding["configuration"], program_rows[0]
        return {
            "schema": "uca-local-product-status-1",
            "project_id": project,
            "program_id": program,
            "binding_sha256": reader.locator["binding_sha256"],
            "command_revision": head["revision"],
            "program_status": current["status"],
            "program_control_revision": controls[0]["revision"],
            "task_control_revision": task_revision,
            "requirement_sha256": current["requirement_hash"],
            "plan_sha256": current["plan_hash"],
            "original": {
                "commit_sha": config["origin_commit_sha"],
                "tree_sha": config["origin_tree_sha"],
                "object_format": config["object_format"],
            },
            "accepted": accepted,
            "execution": execution,
            **decisions,
            "requests": requests[:limit],
            "next_cursor": requests[limit - 1]["sequence"] if len(requests) > limit else None,
            "blockers": ["recovery_required"] if head["pending_request_id"] else [],
            "authority": AUTHORITY,
        }


def evidence(path, project, program, value, *, after_chunk=None, limit=1):
    with read_session(path) as reader:
        reader.all_requests(project, program)
        check(
            any(
                record["response"]
                and record["response"]["result"].get("evidence_view_sha256") == value
                for record in reader.records.values()
            ),
            "evidence_not_found",
        )
        view = reader.view(value, program)
        start = 0 if after_chunk is None else after_chunk + 1
        end = min(start + limit, len(view["chunks"]))
        return {
            "schema": "uca-local-product-evidence-page-1",
            "evidence_view_sha256": value,
            "total_chunks": len(view["chunks"]),
            "next_chunk": end if end < len(view["chunks"]) else None,
            "view": {**view, "chunks": view["chunks"][start:end]},
            "authority": AUTHORITY,
        }
