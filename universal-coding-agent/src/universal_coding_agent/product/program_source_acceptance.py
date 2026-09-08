"""Durable, owner/CAS guarded acceptance of one actual Safe source transition.

Only the Program database is written in an acceptance transaction. Attached
control, lifecycle and checkpoint stores are held against concurrent writers.
No filesystem materialization, provider invocation or phase advancement occurs.
"""

from __future__ import annotations

import base64
import re
import sqlite3
from contextlib import contextmanager
from dataclasses import replace
from pathlib import Path
from threading import RLock

from universal_coding_agent.core.safe_models import SafeModePolicy, SafeTaskRequest
from universal_coding_agent.product.lifecycle_reservations import DurableLifecycleReservationStore
from universal_coding_agent.product.models import ProgramPlan
from universal_coding_agent.product.program_orchestrator import ProgramOrchestrator
from universal_coding_agent.product.program_source_attestation import (
    ProgramGitSourceAttestationService,
)
from universal_coding_agent.product.program_source_evidence import (
    capture_safe_source_evidence,
    strict_json,
)
from universal_coding_agent.product.program_source_transitions import (
    ProgramSourceError,
    ProgramSourceIdentity,
    ProgramSourceSnapshot,
    _canonical,
    _digest,
    _hash,
    _identifier,
    _require,
)
from universal_coding_agent.safe_service import SafeAgentService


class ProgramSourceAcceptanceService:
    """Trusted host adapter. Caller-supplied Safe reports/hashes are never admission inputs."""

    def __init__(
        self, *, programs: ProgramOrchestrator, lifecycle: DurableLifecycleReservationStore,
        safe: SafeAgentService, attestor: ProgramGitSourceAttestationService,
        repository_url: str, trusted_policy: SafeModePolicy,
    ) -> None:
        self.programs, self.safe, self.attestor = programs, safe, attestor
        self.repository_url, self.trusted_policy = repository_url, trusted_policy
        self.source = attestor.source
        _require(safe.control.database_path == programs.control.database_path,
                 "Safe and Program must share the existing control authority")
        _require(bool(repository_url) and type(trusted_policy) is SafeModePolicy,
                 "missing host repository/test policy binding")
        safe.graph.checkpointer.setup()
        checkpoint_path = Path(safe.connection.execute("PRAGMA database_list").fetchone()[2])
        paths = [programs.database_path, programs.control.database_path,
                 lifecycle.database_path, checkpoint_path]
        paths = [path.resolve(strict=True) for path in paths]
        _require(len(set(paths)) == len(paths), "acceptance stores must be distinct existing files")
        _require(checkpoint_path == safe.artifacts.root.parent / "safe-checkpoints.sqlite",
                 "Safe checkpoint/artifact host binding differs")
        self.host_sha256 = _hash(_canonical({
            "schema": "uca-source-acceptance-host-1", "database_paths": list(map(str, paths)),
            "safe_artifacts": str(safe.artifacts.root),
            "program_artifacts": str(programs.artifacts.root), "repository_url": repository_url,
            "git_host_sha256": attestor.host_binding_sha256,
            "git_policy_sha256": attestor.policy_sha256,
            "test_policy": trusted_policy.model_dump(mode="json"),
        }))
        self._lock = RLock()
        self.connection = sqlite3.connect(paths[0], isolation_level=None, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA busy_timeout = 5000")
        for alias, path in zip(("control", "lifecycle", "safe"), paths[1:], strict=True):
            self.connection.execute(f"ATTACH DATABASE ? AS {alias}", (str(path),))
        with self._transaction():
            self.connection.execute("""CREATE TABLE IF NOT EXISTS program_source_artifacts (
                sha256 TEXT PRIMARY KEY, content BLOB NOT NULL)""")
            self.connection.execute("""CREATE TABLE IF NOT EXISTS program_source_heads (
                program_id TEXT PRIMARY KEY, generation INTEGER NOT NULL,
                source_sha256 TEXT NOT NULL, host_sha256 TEXT NOT NULL,
                initial_receipt_sha256 TEXT NOT NULL, receipt_sha256 TEXT NOT NULL)""")
            self.connection.execute("""CREATE TABLE IF NOT EXISTS program_source_candidates (
                candidate_sha256 TEXT PRIMARY KEY, program_id TEXT NOT NULL)""")
            self.connection.execute("""CREATE TABLE IF NOT EXISTS program_source_acceptances (
                candidate_sha256 TEXT PRIMARY KEY, approval_sha256 TEXT NOT NULL,
                receipt_sha256 TEXT NOT NULL, program_id TEXT NOT NULL,
                task_id TEXT NOT NULL, UNIQUE(program_id, task_id))""")

    def close(self) -> None:
        with self._lock:
            self.connection.close()

    @contextmanager
    def _transaction(self):
        with self._lock:
            try:
                self.connection.execute("BEGIN IMMEDIATE")
                yield
                self.connection.commit()
            except BaseException as exc:
                if self.connection.in_transaction:
                    self.connection.rollback()
                if isinstance(exc, sqlite3.Error):
                    raise ProgramSourceError("source acceptance transaction rejected") from exc
                raise

    def _put(self, raw: bytes) -> str:
        _require(type(raw) is bytes and len(raw) <= self.source.policy.max_artifact_bytes,
                 "immutable source artifact exceeds policy")
        sha = _hash(raw)
        self.connection.execute(
            "INSERT OR IGNORE INTO program_source_artifacts VALUES (?, ?)", (sha, raw))
        _require(self._get(sha) == raw, "immutable source artifact conflict")
        return sha

    def _get(self, sha: str) -> bytes:
        from universal_coding_agent.product.program_source_capture_budget import charge

        _digest(sha)
        row = self.connection.execute(
            "SELECT length(content) FROM program_source_artifacts WHERE sha256 = ?", (sha,)
        ).fetchone()
        _require(row is not None and row[0] <= self.source.policy.max_artifact_bytes,
                 "missing or oversized immutable source artifact")
        charge(row[0])
        selected = self.connection.execute(
            "SELECT CASE WHEN typeof(content)='blob' AND length(content)=? "
            "THEN substr(content,1,?) END FROM program_source_artifacts WHERE sha256 = ?",
            (row[0], row[0], sha),
        ).fetchone()
        _require(selected is not None, "immutable source artifact disappeared")
        raw = selected[0]
        _require(type(raw) is bytes and _hash(raw) == sha, "immutable source artifact corrupted")
        return raw

    def _head(self, program_id: str) -> sqlite3.Row:
        _identifier(program_id)
        row = self.connection.execute(
            "SELECT * FROM program_source_heads WHERE program_id = ?", (program_id,)).fetchone()
        _require(row is not None and row["host_sha256"] == self.host_sha256,
                 "source head is missing or host policy changed")
        return row

    def current(self, program_id: str) -> ProgramSourceSnapshot:
        """Read only. Never infer pending approval or resume a graph after restart."""
        with self._lock:
            head = self._head(program_id)
            snapshot = self.source.load_snapshot(self._get(head["source_sha256"]),
                                                 expected_sha256=head["source_sha256"])
            _require(snapshot.identity.program_id == program_id
                     and snapshot.generation == head["generation"], "source head is inconsistent")
            return snapshot

    def receipt(self, candidate_sha256: str) -> dict:
        with self._lock:
            row = self.connection.execute(
                "SELECT receipt_sha256 FROM program_source_acceptances WHERE candidate_sha256 = ?",
                (candidate_sha256,)).fetchone()
            _require(row is not None, "source candidate was not accepted")
            return strict_json(self._get(row[0]))

    def _binding(self, identity: ProgramSourceIdentity, owner_token: str,
                 task_id: str | None = None) -> dict:
        program_id = identity.program_id
        _require(isinstance(owner_token, str) and re.fullmatch(r"[0-9a-f]{32}", owner_token)
                 is not None, "invalid lifecycle owner token")
        owner = self.connection.execute("""SELECT * FROM lifecycle.lifecycle_worker_ownership
            WHERE worker_kind = 'program_execution' AND scope_id = ?""", (program_id,)).fetchone()
        _require(owner is not None and owner["owner_token"] == owner_token
                 and owner["program_id"] == program_id and owner["task_id"] == "",
                 "current Program worker does not own source acceptance")
        conflicts = self.connection.execute("""SELECT 1 FROM lifecycle.lifecycle_reservations
            WHERE program_id = ? OR task_id IN
              (SELECT task_id FROM program_executions WHERE program_id = ?) LIMIT 1""",
                                            (program_id, program_id)).fetchone()
        other_worker = self.connection.execute("""SELECT 1 FROM lifecycle.lifecycle_worker_ownership
            WHERE owner_token != ? AND (program_id = ? OR task_id IN
              (SELECT task_id FROM program_executions WHERE program_id = ?)) LIMIT 1""",
                                               (owner_token, program_id, program_id)).fetchone()
        _require(conflicts is None and other_worker is None,
                 "conflicting lifecycle action is active")
        program = self.connection.execute(
            "SELECT * FROM programs WHERE program_id = ?", (program_id,)).fetchone()
        _require(program is not None and program["status"] in ("running", "completed")
                 and program["requirement_hash"] == identity.requirement_sha256
                 and program["plan_hash"] == identity.plan_sha256
                 and program["plan_ref"] == f"artifact://programs/{program_id}/program-plan.json",
                 "Program is unapproved, stopped, realigned or changed")
        control = self.connection.execute("""SELECT * FROM control.control_state
            WHERE entity_type = 'program' AND entity_id = ?""", (program_id,)).fetchone()
        _require(control is not None and control["state"] in ("running", "completed"),
                 "Program control does not allow source acceptance")
        binding = {"program": dict(program), "program_control": dict(control),
                   "owner_binding_sha256": _hash(_canonical(dict(owner)))}
        if task_id is not None:
            execution = self.connection.execute(
                "SELECT * FROM program_executions WHERE task_id = ?", (task_id,)).fetchone()
            _require(execution is not None and execution["program_id"] == program_id
                     and execution["requirement_hash"] == identity.requirement_sha256
                     and execution["status"] == "completed"
                     and execution["safe_status"] == "completed"
                     and not execution["error_ref"] and not execution["remote_disposition_ref"],
                     "Program execution is not completed and bound to this requirement")
            phase = self.connection.execute("""SELECT * FROM program_phases
                WHERE program_id = ? AND phase_id = ?""",
                                            (program_id, execution["phase_id"])).fetchone()
            _require(phase is not None and phase["status"] in ("running", "completed"),
                     "Program phase is not eligible for source acceptance")
            task_control = self.connection.execute("""SELECT * FROM control.control_state
                WHERE entity_type = 'task' AND entity_id = ?""", (task_id,)).fetchone()
            _require(task_control is not None and task_control["state"] == "completed",
                     "Safe task control is not completed")
            binding.update(execution=dict(execution), phase=dict(phase),
                           task_control=dict(task_control))
        return binding

    def _checkpoint(self, thread_id: str) -> bytes:
        sizes = self.connection.execute("""SELECT checkpoint_id,
            length(checkpoint), length(metadata)
            FROM safe.checkpoints WHERE thread_id = ? AND checkpoint_ns = ''
            ORDER BY checkpoint_id DESC LIMIT 1""", (thread_id,)).fetchone()
        _require(sizes is not None and sum(sizes[1:]) <= 16_000_000,
                 "missing or oversized completed Safe checkpoint")
        _require(self.connection.execute("""SELECT 1 FROM safe.writes WHERE thread_id = ?
            AND checkpoint_ns = '' AND checkpoint_id = ? LIMIT 1""",
                                        (thread_id, sizes[0])).fetchone() is None,
                 "Safe checkpoint has pending writes")
        row = self.connection.execute("""SELECT * FROM safe.checkpoints WHERE thread_id = ?
            AND checkpoint_ns = '' AND checkpoint_id = ?""", (thread_id, sizes[0])).fetchone()
        data = dict(row)
        for key in ("checkpoint", "metadata"):
            data[key] = base64.b64encode(data[key]).decode("ascii")
        raw = _canonical(data)
        _require(len(raw) <= self.source.policy.max_artifact_bytes, "checkpoint exceeds policy")
        return raw

    def _plan(self, identity: ProgramSourceIdentity) -> ProgramPlan:
        raw = self.programs.artifacts._read_bytes_bounded(
            f"artifact://programs/{identity.program_id}/program-plan.json", max_bytes=2_000_000)
        plan = ProgramPlan.model_validate(strict_json(raw))
        _require(plan.program_id == identity.program_id
                 and plan.requirement_hash == identity.requirement_sha256
                 and plan.canonical_hash() == identity.plan_sha256, "approved Program plan differs")
        return plan

    def initialize(self, identity: ProgramSourceIdentity, *, owner_token: str) -> dict:
        _require(type(identity) is ProgramSourceIdentity, "invalid Program origin identity")
        with self._transaction():
            binding = self._binding(identity, owner_token)
        self._plan(identity)
        attestation = self.attestor.attest(identity)
        raw = self.source.snapshot_bytes(attestation.snapshot)
        receipt = _canonical({"schema": "uca-source-initialization-1",
                              "source_sha256": _hash(raw), "host_sha256": self.host_sha256,
                              "attestation": strict_json(attestation.receipt_bytes())})
        with self._transaction():
            _require(self._binding(identity, owner_token) == binding,
                     "initialization binding drifted")
            existing = self.connection.execute(
                "SELECT * FROM program_source_heads WHERE program_id = ?",
                (identity.program_id,)).fetchone()
            if existing is not None:
                _require(existing["host_sha256"] == self.host_sha256
                         and self._get(existing["initial_receipt_sha256"]) == receipt,
                         "Program source already has another origin")
                return strict_json(receipt)
            snapshot_sha, receipt_sha = self._put(raw), self._put(receipt)
            self.connection.execute("INSERT INTO program_source_heads VALUES (?, 0, ?, ?, ?, ?)",
                                    (identity.program_id, snapshot_sha, self.host_sha256,
                                     receipt_sha, receipt_sha))
        return strict_json(receipt)

    def _dispatch_for(self, task_id):
        self._deny_v3(task_id)
        row = self.connection.execute(
            "SELECT 1 FROM control.uca_source_dispatch_tasks WHERE task_id = ?", (task_id,)
        ).fetchone()
        if row is None:
            return None
        dispatch = getattr(self, "source_dispatch", None)
        _require(dispatch is not None, "v2 source capture requires its explicit dispatch service")
        return dispatch

    def _deny_v3(self, task_id):
        from universal_coding_agent.product.program_source_routing import (
            require_no_v3,
            safe_v3_route,
        )
        require_no_v3(self.connection, task_id=task_id)
        row = self.connection.execute("SELECT thread_id FROM program_executions WHERE task_id=?",
                                      (task_id,)).fetchone()
        if row is not None and safe_v3_route(self.safe, row[0], task_id):
            raise ValueError("v3 source acceptance is not implemented in this slice")

    def _capture(self, before: ProgramSourceSnapshot, task_id: str, owner_token: str):
        self._deny_v3(task_id)
        with self._transaction():
            binding = self._binding(before.identity, owner_token, task_id)
            checkpoint = self._checkpoint(binding["execution"]["thread_id"])
        plan = self._plan(before.identity)
        execution = binding["execution"]
        _require((execution["task_id"], execution["thread_id"])
                 == self.programs._execution_ids(before.identity.program_id,
                     execution["phase_id"], execution["slice_id"] or None)
                 and execution["unit_key"] == (execution["slice_id"] or "__phase__"),
                 "Program execution lineage differs")
        point = strict_json(checkpoint)
        snapshot = self.safe.graph.get_state({"configurable": {
            "thread_id": execution["thread_id"], "checkpoint_ns": "",
            "checkpoint_id": point["checkpoint_id"]}})
        _require(not snapshot.next and not snapshot.tasks, "Safe graph is not terminal")
        state = snapshot.values
        task = SafeTaskRequest.model_validate(state["task"])
        phase = next((phase for phase in plan.phases
                      if phase.phase_id == execution["phase_id"]), None)
        _require(phase is not None, "execution phase is absent from approved Program")
        unit = next((item for item in phase.slices if item.slice_id == execution["slice_id"]), None)
        _require((not phase.slices and not execution["slice_id"]) or unit is not None,
                 "execution slice is absent from approved Program")
        unit = unit or phase
        criteria = self.programs._execution_acceptance_criteria(phase,
                                                               unit if unit is not phase else None)
        _require(task.task_id == task_id and task.thread_id == execution["thread_id"]
                 and task.objective == unit.objective
                 and task.manifest.acceptance_criteria == criteria,
                 "Safe request is not the exact approved execution unit")
        _require(not execution["expected_base_sha"]
                 or execution["expected_base_sha"] == task.manifest.base_sha,
                 "v1 accepted evidence Base guard differs")
        dispatch = self._dispatch_for(task_id)
        if dispatch is None:
            evidence = capture_safe_source_evidence(
                state=state, before=before, artifacts=self.safe.artifacts,
                repository_url=self.repository_url, policy=self.trusted_policy,
                attestor=self.attestor)
        else:
            evidence = dispatch.capture(task_id, owner_token, state)
        prefix = f"programs/{before.identity.program_id}/phases/{execution['phase_id']}"
        result_uri = f"artifact://{prefix}/executions/{task_id}/safe-result-completed.json"
        report_uri = f"artifact://{prefix}/phase-execution-report.json"
        if dispatch is not None:
            prefix = dispatch._result_prefix(
                before.identity.program_id, execution["phase_id"], task_id, state
            )
            result_uri = f"artifact://{prefix}/safe-result.json"
            report_uri = f"artifact://{prefix}/phase-execution-report.json"
        _require(execution["result_ref"] == result_uri
                 and execution["phase_report_ref"] == report_uri,
                 "Program evidence is not owned by the execution")
        result_raw = self.programs.artifacts._read_bytes_bounded(result_uri, max_bytes=8_000_000)
        result = strict_json(result_raw)
        result_state = result.get("state", result)
        for key in ("task", "status", "base_sha", "scope_hash", "scope_approved", "safe_errors",
                    "rolled_back", "rollback_ref", "patch_applied", "final_report_ref",
                    "patch_ref", "tests_ref", "tests_sha256", "review_ref", "review_sha256",
                    "review_provenance_ref", "review_provenance_sha256", "reviewer_verdict"):
            _require(result_state.get(key) == state.get(key),
                     "Program result differs from the actual Safe checkpoint")
        report_raw = self.programs.artifacts._read_bytes_bounded(report_uri, max_bytes=2_000_000)
        report = strict_json(report_raw)
        _require(report.get("program_id") == before.identity.program_id
                 and report.get("requirement_hash") == before.identity.requirement_sha256
                 and report.get("phase_id") == execution["phase_id"]
                 and report.get("phase_status") == binding["phase"]["status"],
                 "Program phase report differs from its durable binding")
        report_bindings = [item for item in report.get("bindings", [])
                           if item.get("task_id") == task_id]
        _require(len(report_bindings) == 1 and all(
            report_bindings[0].get(key) == execution[key]
            for key in ("program_id", "phase_id", "task_id", "thread_id", "requirement_hash",
                        "status", "safe_status", "result_ref", "error_ref")),
                 "Program phase report has no exact completed execution")
        payload = _canonical({"schema": ("uca-program-safe-source-evidence-2" if dispatch
                                          else "uca-program-safe-source-evidence-1"),
                              "safe": strict_json(evidence.payload),
                              "program_result_base64": base64.b64encode(result_raw).decode(),
                              "phase_report_base64": base64.b64encode(report_raw).decode()})
        _require(len(payload) <= self.source.policy.max_artifact_bytes,
                 "complete Program/Safe evidence exceeds policy")
        evidence = replace(evidence, payload=payload)
        return binding, checkpoint, evidence

    def _expect_head(self, program_id: str, source_sha: str, generation: int) -> None:
        _digest(source_sha)
        _require(type(generation) is int and generation >= 0, "invalid expected generation")
        head = self._head(program_id)
        _require((head["source_sha256"], head["generation"]) == (source_sha, generation),
                 "stale source generation or predecessor")

    def prepare(self, program_id: str, task_id: str, *, owner_token: str,
                expected_source_sha256: str, expected_generation: int) -> dict:
        self._deny_v3(task_id)
        with self._transaction():
            self._expect_head(program_id, expected_source_sha256, expected_generation)
            before = self.current(program_id)
        binding, checkpoint, evidence = self._capture(before, task_id, owner_token)
        execution = binding["execution"]
        transition = self.source.prepare(
            before, expected_source_sha256=expected_source_sha256,
            phase_id=execution["phase_id"], task_id=task_id,
            slice_id=execution["slice_id"] or None, allowed_paths=evidence.allowed_paths,
            evidence_sha256=tuple(sorted({_hash(evidence.payload), _hash(checkpoint)})),
            edits=evidence.edits)
        transition_raw = self.source.transition_bytes(transition)
        after = self.source.materialize(before, transition,
                                       approved_transition_sha256=_hash(transition_raw))
        candidate = {"schema": "uca-source-candidate-1", "program_id": program_id,
                     "task_id": task_id, "host_sha256": self.host_sha256,
                     "before_sha256": expected_source_sha256, "generation": expected_generation,
                     "after_sha256": transition.after_sha256,
                     "transition_sha256": _hash(transition_raw),
                     "evidence_sha256": _hash(evidence.payload),
                     "checkpoint_sha256": _hash(checkpoint), "binding": binding}
        raw = _canonical(candidate)
        with self._transaction():
            self._expect_head(program_id, expected_source_sha256, expected_generation)
            _require(self._binding(before.identity, owner_token, task_id) == binding
                     and self._checkpoint(execution["thread_id"]) == checkpoint,
                     "execution changed during evidence capture")
            dispatch = self._dispatch_for(task_id)
            if dispatch is not None:
                dispatch.acceptance_gate(task_id, owner_token)
            for blob in (self.source.snapshot_bytes(after), transition_raw, evidence.payload,
                         checkpoint, raw):
                self._put(blob)
            self.connection.execute("INSERT OR IGNORE INTO program_source_candidates VALUES (?, ?)",
                                    (_hash(raw), program_id))
        return {"candidate_sha256": _hash(raw), **candidate}

    def accept(self, candidate_sha256: str, *, approved_transition_sha256: str,
               approval_id: str, owner_token: str) -> dict:
        _identifier(approval_id)
        _digest(approved_transition_sha256)
        with self._transaction():
            candidate = strict_json(self._get(candidate_sha256))
            self._deny_v3(candidate["task_id"])
            _require(candidate.get("schema") == "uca-source-candidate-1"
                     and candidate["host_sha256"] == self.host_sha256
                     and candidate["transition_sha256"] == approved_transition_sha256,
                     "exact source-transition approval differs")
            _require(self.connection.execute("""SELECT 1 FROM program_source_candidates
                WHERE candidate_sha256 = ? AND program_id = ?""",
                                            (candidate_sha256, candidate["program_id"])).fetchone(),
                     "source candidate was not prepared by this host")
            before = self.source.load_snapshot(self._get(candidate["before_sha256"]),
                                               expected_sha256=candidate["before_sha256"])
            self._binding(before.identity, owner_token)
            approval = _canonical({"schema": "uca-source-approval-1", "approval_id": approval_id,
                                   "candidate_sha256": candidate_sha256,
                                   "approved_transition_sha256": approved_transition_sha256})
            prior = self.connection.execute("""SELECT * FROM program_source_acceptances
                WHERE candidate_sha256 = ?""", (candidate_sha256,)).fetchone()
            dispatch = self._dispatch_for(candidate["task_id"])
            if dispatch is not None:
                dispatch.acceptance_gate(candidate["task_id"], owner_token,
                                         replay=prior is not None)
            if prior is not None:
                _require(prior["approval_sha256"] == _hash(approval), "accepted approval differs")
                return self.receipt(candidate_sha256)
            self._expect_head(candidate["program_id"], candidate["before_sha256"],
                              candidate["generation"])
        binding, checkpoint, evidence = self._capture(before, candidate["task_id"], owner_token)
        _require(binding == candidate["binding"]
                 and _hash(checkpoint) == candidate["checkpoint_sha256"]
                 and _hash(evidence.payload) == candidate["evidence_sha256"],
                 "prepared evidence, checkpoint or control revision drifted")
        with self._transaction():
            self._binding(before.identity, owner_token)
            prior = self.connection.execute("""SELECT * FROM program_source_acceptances
                WHERE candidate_sha256 = ?""", (candidate_sha256,)).fetchone()
            dispatch = self._dispatch_for(candidate["task_id"])
            if dispatch is not None:
                dispatch.acceptance_gate(candidate["task_id"], owner_token,
                                         replay=prior is not None)
            if prior is not None:
                _require(prior["approval_sha256"] == _hash(approval), "accepted approval differs")
                return self.receipt(candidate_sha256)
            self._expect_head(candidate["program_id"], candidate["before_sha256"],
                              candidate["generation"])
            _require(self._binding(before.identity, owner_token, candidate["task_id"]) == binding
                     and self._checkpoint(binding["execution"]["thread_id"]) == checkpoint,
                     "acceptance binding changed at commit")
            transition = self.source.load_transition(self._get(approved_transition_sha256),
                                                     expected_sha256=approved_transition_sha256)
            after = self.source.materialize(before, transition,
                                           approved_transition_sha256=approved_transition_sha256)
            _require(self.source.snapshot_hash(after) == candidate["after_sha256"]
                     and self._get(candidate["after_sha256"]) == self.source.snapshot_bytes(after)
                     and self._get(candidate["evidence_sha256"]) == evidence.payload
                     and self._get(candidate["checkpoint_sha256"]) == checkpoint,
                     "prepared immutable payloads differ")
            receipt = _canonical({"schema": "uca-source-acceptance-receipt-1",
                                  "program_id": candidate["program_id"],
                                  "task_id": candidate["task_id"],
                                  "candidate_sha256": candidate_sha256,
                                  "transition_sha256": approved_transition_sha256,
                                  "approval_sha256": self._put(approval),
                                  "source_sha256": candidate["after_sha256"],
                                  "predecessor_sha256": candidate["before_sha256"],
                                  "generation": after.generation, "host_sha256": self.host_sha256,
                                  "materialization_ready": False})
            receipt_sha = self._put(receipt)
            self.connection.execute("INSERT INTO program_source_acceptances VALUES (?, ?, ?, ?, ?)",
                                    (candidate_sha256, _hash(approval), receipt_sha,
                                     candidate["program_id"], candidate["task_id"]))
            updated = self.connection.execute("""UPDATE program_source_heads SET generation = ?,
                source_sha256 = ?, receipt_sha256 = ? WHERE program_id = ? AND generation = ?
                AND source_sha256 = ? AND host_sha256 = ?""",
                (after.generation, candidate["after_sha256"], receipt_sha, candidate["program_id"],
                 candidate["generation"], candidate["before_sha256"], self.host_sha256))
            _require(updated.rowcount == 1, "source head compare-and-swap lost")
        return strict_json(receipt)
