"""Bounded historical source metadata for the Product view; never execution authority.

Read existing SQLite records without constructing effectful source/Safe services.
Receipt hashes and relational metadata are checked. Source blobs, checkpoint and
artifact files, filesystem identity and current worker authority are not requalified.
"""

from __future__ import annotations

import json
import sqlite3
import time
from contextlib import closing
from pathlib import Path

from universal_coding_agent.product.program_source_transitions import (
    ProgramSourceIdentity,
    _canonical,
    _digest,
    _hash,
    _identifier,
)

MAX_RECORDS = 100
MAX_FIELD_BYTES = 128
MAX_METADATA_BYTES = 64 * 1024
MAX_TOTAL_METADATA_BYTES = 1024 * 1024
DISPATCH_STATES = frozenset({
    "admitted", "discovery_started", "discovered", "safe_started",
    "awaiting_scope_approval", "resume_started", "terminal",
})


class ProgramSourceStatusError(ValueError):
    """Recorded metadata cannot be safely projected; do not fall back to v1."""


def _expect(condition: bool) -> None:
    if not condition:
        raise ValueError("inconsistent source metadata")


def program_source_status(database_path: Path, program_id: str) -> dict:
    """Return only allowlisted, bounded recorded metadata from one read snapshot.

    mode=ro forbids database creation/writes. Ordinary locking remains enabled;
    immutable/nolock/read_uncommitted would be incorrect for these live stores.
    """
    _identifier(program_id)
    try:
        with closing(sqlite3.connect(
            database_path.resolve(strict=True).as_uri() + "?mode=ro",
            uri=True, isolation_level=None, timeout=0.5,
        )) as connection:
            try:
                connection.row_factory = sqlite3.Row
                connection.execute("PRAGMA query_only = ON")
                connection.execute("PRAGMA trusted_schema = OFF")
                deadline, ticks = time.monotonic() + 2, 0

                def bounded_work():
                    nonlocal ticks
                    ticks += 1
                    return int(ticks > 1000 or time.monotonic() > deadline)

                connection.set_progress_handler(bounded_work, 1000)
                connection.execute("BEGIN")
                return _SourceReader(connection).snapshot(program_id)
            finally:
                # A sqlite connection context does not close the connection.
                connection.rollback()
    except (OSError, sqlite3.Error, ValueError, TypeError, KeyError, RecursionError) as exc:
        raise ProgramSourceStatusError("recorded Program source metadata is unavailable") from exc


class _SourceReader:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
        self.remaining = MAX_TOTAL_METADATA_BYTES

    def table(self, name):
        row = self.connection.execute(
            "SELECT type FROM sqlite_schema WHERE name = ?", (name,),
        ).fetchone()
        _expect(row is None or row[0] == "table")
        return row is not None

    def rows(self, table, fields, where, parameters, *, limit=MAX_RECORDS):
        # All SQL identifiers/clauses are fixed internal strings. Check persisted
        # lengths before retrieving values, in the same transaction snapshot.
        tail = f" FROM {table} WHERE {where} LIMIT {limit + 1}"
        sizes = self.connection.execute(
            "SELECT " + ",".join(f"length(CAST({f} AS BLOB))" for f in fields) + tail,
            parameters,
        ).fetchall()
        _expect(len(sizes) <= limit)
        _expect(all(n is None or 0 <= n <= MAX_FIELD_BYTES for row in sizes for n in row))
        return self.connection.execute(
            "SELECT " + ",".join(fields) + tail, parameters,
        ).fetchall()

    def metadata(self, digest):
        _digest(digest)
        row = self.connection.execute(
            "SELECT length(content), typeof(content) FROM program_source_artifacts WHERE sha256=?",
            (digest,),
        ).fetchone()
        _expect(row is not None and row[1] == "blob")
        _expect(0 < row[0] <= min(MAX_METADATA_BYTES, self.remaining))
        self.remaining -= row[0]
        raw = self.connection.execute(
            "SELECT content FROM program_source_artifacts WHERE sha256=?", (digest,),
        ).fetchone()[0]
        _expect(_hash(raw) == digest)

        def pairs(items):
            result = {}
            for key, value in items:
                _expect(key not in result)
                result[key] = value
            return result

        value = json.loads(raw, object_pairs_hook=pairs)
        _expect(isinstance(value, dict) and _canonical(value) == raw)
        return value

    def snapshot(self, program_id):
        programs = self.rows(
            "programs", ("requirement_hash", "plan_hash"), "program_id=?", (program_id,), limit=1,
        )
        _expect(len(programs) == 1)
        program = programs[0]
        result = {
            "schema": "uca-program-source-status-1", "program_id": program_id,
            "status": "uninitialized", "origin": None, "accepted": None,
            "lineage": [], "dispatches": [], "matches_current_plan": None,
            "automatic_execution": False, "filesystem_verified": False,
            "current_authority_verified": False, "source_bytes_verified": False,
        }
        tables = {name: self.table(name) for name in (
            "program_source_heads", "program_source_artifacts", "program_source_candidates",
            "program_source_acceptances", "program_source_dispatches", "program_execution_bases",
        )}
        if not any(tables.values()):
            return result
        _expect(all(tables[name] for name in (
            "program_source_heads", "program_source_artifacts", "program_source_candidates",
            "program_source_acceptances",
        )))
        heads = self.rows(
            "program_source_heads",
            ("generation", "source_sha256", "host_sha256", "initial_receipt_sha256",
             "receipt_sha256"), "program_id=?", (program_id,), limit=1,
        )
        acceptances = self.rows(
            "program_source_acceptances",
            ("candidate_sha256", "approval_sha256", "receipt_sha256", "task_id"),
            "program_id=?", (program_id,),
        )
        executions = self.rows(
            "program_executions",
            ("phase_id", "task_id", "thread_id", "requirement_hash", "expected_base_sha"),
            "program_id=?", (program_id,),
        )
        bases = self.rows(
            "program_execution_bases",
            ("operation_id", "phase_id", "state", "completion_sha256"),
            "program_id=?", (program_id,),
        ) if tables["program_execution_bases"] else []
        dispatches = []
        if tables["program_source_dispatches"]:
            for execution in executions:
                rows = self.rows(
                    "program_source_dispatches",
                    ("operation_id", "task_id", "admission_sha256", "host_sha256", "state"),
                    "task_id=?", (execution["task_id"],), limit=1,
                )
                if rows:
                    dispatches.append((rows[0], execution))
        # A prepared phase that has acquired an execution binding must retain its
        # admission. Reading by both identities catches a missing/misbound task or
        # dispatch row without silently presenting a complete v1 history.
        operations = {row["operation_id"] for row, _ in dispatches}
        for base in bases:
            bound = any(ex["phase_id"] == base["phase_id"] for ex in executions)
            if base["state"] != "abandoned" and bound:
                _expect(base["state"] == "complete" and base["operation_id"] in operations)
            if tables["program_source_dispatches"]:
                rows = self.rows("program_source_dispatches", ("task_id",), "operation_id=?",
                                 (base["operation_id"],), limit=1)
                _expect(not rows or base["operation_id"] in operations)
        if not heads:
            _expect(not acceptances and not dispatches and not bases)
            return result
        head = heads[0]
        _expect(type(head["generation"]) is int and 0 <= head["generation"] <= MAX_RECORDS)
        for key in ("source_sha256", "host_sha256", "initial_receipt_sha256", "receipt_sha256"):
            _digest(head[key])
        initial = self.metadata(head["initial_receipt_sha256"])
        _expect(initial["schema"] == "uca-source-initialization-1")
        _expect(initial["host_sha256"] == head["host_sha256"])
        attestation = initial["attestation"]
        _expect(attestation["schema"] == "uca-program-git-source-attestation-1")
        identity = ProgramSourceIdentity(**attestation["identity"])
        _expect(identity.program_id == program_id)
        _digest(initial["source_sha256"])
        _expect(attestation["snapshot_sha256"] == initial["source_sha256"])
        history = [{
            "generation": 0, "source_sha256": initial["source_sha256"],
            "predecessor_sha256": None, "task_id": None,
            "receipt_sha256": head["initial_receipt_sha256"],
        }]
        execution_map = {row["task_id"]: row for row in executions}
        _expect(len(execution_map) == len(executions))
        for row in acceptances:
            history.append(self.acceptance(row, head, identity, execution_map))
        history.sort(key=lambda item: item["generation"])
        _expect(len(history) == head["generation"] + 1)
        for i, entry in enumerate(history):
            _expect(entry["generation"] == i)
            if i:
                _expect(entry["predecessor_sha256"] == history[i - 1]["source_sha256"])
        _expect(history[-1]["source_sha256"] == head["source_sha256"])
        _expect(history[-1]["receipt_sha256"] == head["receipt_sha256"])
        projected = [self.dispatch(row, execution, identity, history, bases)
                     for row, execution in dispatches]
        projected.sort(key=lambda item: (item["generation"], item["operation_id"]))
        result.update(
            status="recorded",
            origin={"repository_sha256": identity.repository_sha256,
                    "git_commit_sha": identity.origin_base_sha,
                    "git_tree_sha": identity.origin_tree_sha},
            accepted=history[-1], lineage=history, dispatches=projected,
            matches_current_plan=(identity.requirement_sha256 == program["requirement_hash"]
                                  and identity.plan_sha256 == program["plan_hash"]),
        )
        return result

    def acceptance(self, row, head, identity, executions):
        receipt = self.metadata(row["receipt_sha256"])
        _expect(receipt["schema"] == "uca-source-acceptance-receipt-1")
        _expect(receipt["program_id"] == identity.program_id)
        _expect(receipt["host_sha256"] == head["host_sha256"])
        _expect(receipt["materialization_ready"] is False)
        for key in ("candidate_sha256", "approval_sha256", "task_id"):
            _expect(receipt[key] == row[key])
        for key in ("source_sha256", "predecessor_sha256", "transition_sha256"):
            _digest(receipt[key])
        _expect(type(receipt["generation"]) is int and 1 <= receipt["generation"] <= MAX_RECORDS)
        candidate = self.metadata(row["candidate_sha256"])
        candidates = self.rows(
            "program_source_candidates", ("program_id",), "candidate_sha256=?",
            (row["candidate_sha256"],), limit=1,
        )
        _expect(len(candidates) == 1 and candidates[0][0] == identity.program_id)
        _expect(candidate["schema"] == "uca-source-candidate-1")
        _expect(candidate["program_id"] == identity.program_id)
        _expect(candidate["task_id"] == row["task_id"])
        _expect(candidate["host_sha256"] == head["host_sha256"])
        _expect(candidate["before_sha256"] == receipt["predecessor_sha256"])
        _expect(candidate["after_sha256"] == receipt["source_sha256"])
        _expect(type(candidate["generation"]) is int
                and candidate["generation"] + 1 == receipt["generation"])
        _expect(candidate["transition_sha256"] == receipt["transition_sha256"])
        approval = self.metadata(row["approval_sha256"])
        _expect(approval["schema"] == "uca-source-approval-1")
        _identifier(approval["approval_id"])
        _expect(approval["candidate_sha256"] == row["candidate_sha256"])
        _expect(approval["approved_transition_sha256"] == receipt["transition_sha256"])
        execution = executions[row["task_id"]]
        binding = candidate["binding"]["execution"]
        _expect(binding["program_id"] == identity.program_id)
        for key in ("task_id", "thread_id", "phase_id", "requirement_hash", "expected_base_sha"):
            _expect(binding[key] == execution[key])
        _expect(execution["requirement_hash"] == identity.requirement_sha256)
        _identifier(row["task_id"])
        return {"generation": receipt["generation"], "source_sha256": receipt["source_sha256"],
                "predecessor_sha256": receipt["predecessor_sha256"], "task_id": row["task_id"],
                "receipt_sha256": row["receipt_sha256"]}

    def dispatch(self, row, execution, identity, history, bases):
        admission = self.metadata(row["admission_sha256"])
        _expect(admission["schema"] == "uca-program-source-dispatch-2")
        _expect(admission["program_id"] == identity.program_id)
        for key in ("task_id", "operation_id", "host_sha256"):
            _expect(admission[key] == row[key])
        _expect(len(row["operation_id"]) == 32
                and all(c in "0123456789abcdef" for c in row["operation_id"]))
        for key in ("task_id", "thread_id", "phase_id"):
            _expect(admission[key] == execution[key])
            _identifier(admission[key], minimum=2)
        _expect(execution["requirement_hash"] == identity.requirement_sha256)
        _expect(admission["origin_repository_sha256"] == identity.repository_sha256)
        _expect(admission["origin_base_sha"] == identity.origin_base_sha)
        _expect(admission["origin_tree_sha"] == identity.origin_tree_sha)
        _expect(admission["dispatch_authorized"] is True
                and admission["automatic_execution"] is False)
        base = next((b for b in bases if b["operation_id"] == row["operation_id"]), None)
        _expect(base is not None and base["state"] == "complete")
        _expect(base["phase_id"] == admission["phase_id"])
        _expect(base["completion_sha256"] == admission["preparation_receipt_sha256"])
        preparation = self.metadata(base["completion_sha256"])
        _expect(preparation["schema"] == "uca-program-execution-base-receipt-1")
        _expect(preparation["execution_base_complete"] is True
                and preparation["dispatch_authorized"] is False)
        for key in ("operation_id", "program_id", "phase_id", "task_id", "thread_id",
                    "generation", "source_sha256", "acceptance_receipt_sha256",
                    "origin_repository_sha256", "origin_base_sha", "origin_tree_sha",
                    "derived_git_commit_sha", "derived_git_tree_sha"):
            _expect(type(preparation[key]) is type(admission[key])
                    and preparation[key] == admission[key])
        generation = admission["generation"]
        _expect(type(generation) is int and 0 < generation < len(history))
        _expect(admission["source_sha256"] == history[generation]["source_sha256"])
        _expect(admission["acceptance_receipt_sha256"] == history[generation]["receipt_sha256"])
        for key in ("derived_git_commit_sha", "derived_git_tree_sha"):
            value = admission[key]
            _expect(isinstance(value, str) and len(value) == len(identity.origin_base_sha)
                    and all(c in "0123456789abcdef" for c in value))
        _expect(execution["expected_base_sha"] == admission["derived_git_commit_sha"])
        _expect(row["state"] in DISPATCH_STATES)
        accepted = any(item["task_id"] == row["task_id"] for item in history)
        _expect(not accepted or row["state"] == "terminal")
        return {
            "operation_id": row["operation_id"], "task_id": row["task_id"],
            "phase_id": admission["phase_id"], "generation": generation,
            "source_sha256": admission["source_sha256"], "state": row["state"],
            "execution_schema": admission["schema"], "admission_sha256": row["admission_sha256"],
            "derived_git_commit_sha": admission["derived_git_commit_sha"],
            "derived_git_tree_sha": admission["derived_git_tree_sha"],
            "source_accepted": accepted,
        }


def require_legacy_program_route(database_path: Path, program_id: str, task_id=None) -> None:
    """Reject routing cumulative source through v1; never grant v2 permission."""
    status = program_source_status(database_path, program_id)
    if status["status"] == "uninitialized":
        return
    if (not status["matches_current_plan"]
            or (task_id is None and status["accepted"]["generation"] > 0)
            or any(row["task_id"] == task_id for row in status["dispatches"])):
        raise ValueError(
            "recorded cumulative source requires the explicit source-aware host service"
        )
