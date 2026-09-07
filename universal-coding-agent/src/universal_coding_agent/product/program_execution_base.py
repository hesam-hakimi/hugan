"""Durable preparation of a separate Base for the next linear Program phase.

This host service grants no Safe execution or scope approval. Status is read-only;
allocation and reconciliation are explicit and reuse current Program ownership.
"""

from __future__ import annotations

import re
import time
import uuid

from universal_coding_agent.product.program_source_attestation import (
    ProgramGitSourceAttestationService,
    _GitBudget,
)
from universal_coding_agent.product.program_source_evidence import strict_json
from universal_coding_agent.product.program_source_materialization import (
    ProgramSourceMaterializationService,
)
from universal_coding_agent.product.program_source_transitions import (
    _canonical,
    _hash,
    _require,
)
from universal_coding_agent.sandbox.owned_execution import OwnedExecutionTree
from universal_coding_agent.sandbox.owned_source import OwnedSourcePolicy


class ProgramExecutionBaseService:
    """Prepare, recover and attest a Base; do not dispatch a Program execution.

    The first phase still uses the original Base. Subsequent preparation admits
    only the current accepted predecessor of an approved, unsliced linear plan.
    No caller source, destination, Git identity or evidence bundle is accepted.
    """

    def __init__(self, materialization: ProgramSourceMaterializationService,
                 policy: OwnedSourcePolicy | None = None):
        self.materialization = materialization
        self.acceptance = materialization.acceptance
        self.filesystem = OwnedExecutionTree(materialization.filesystem.root,
                                            policy or OwnedSourcePolicy())
        self.host_sha256 = _hash(_canonical({
            "schema": "uca-program-execution-base-host-1",
            "materialization_host_sha256": materialization.host_sha256,
            "filesystem_policy_sha256": self.filesystem.policy.canonical_hash(),
        }))
        with self.acceptance._transaction():
            self.acceptance.connection.execute("""CREATE TABLE IF NOT EXISTS
                program_execution_bases (
                    operation_id TEXT PRIMARY KEY, program_id TEXT NOT NULL,
                    phase_id TEXT NOT NULL, materialization_id TEXT NOT NULL,
                    host_sha256 TEXT NOT NULL, intent_sha256 TEXT NOT NULL,
                    state TEXT NOT NULL
                        CHECK(state IN ('intent','allocated','complete','abandoned')),
                    allocation_sha256 TEXT, completion_sha256 TEXT, abandonment_sha256 TEXT)""")
            self.acceptance.connection.execute("""CREATE UNIQUE INDEX IF NOT EXISTS
                one_active_program_execution_base ON program_execution_bases(program_id, phase_id)
                WHERE state != 'abandoned'""")

    def _authority(self, materialization_id, owner_token):
        """Repeat complete source proof while holding the existing authority transaction."""
        store, material = self.acceptance, self.materialization
        row, intent, snapshot = material._load(materialization_id, owner_token)
        _require(row["state"] == "complete", "execution Base requires completed materialization")
        receipt = strict_json(store._get(row["completion_sha256"]))
        _require(receipt["intent_sha256"] == row["intent_sha256"]
                 and receipt["allocation_sha256"] == row["allocation_sha256"]
                 and receipt["source_sha256"] == intent["source_sha256"]
                 and receipt["acceptance_receipt_sha256"] == row["acceptance_receipt_sha256"],
                 "execution materialization receipt differs")
        fs = material.filesystem
        with fs.root_handle(intent["root_chain"]) as (root, _):
            proof = fs.inspect(root, "source-" + materialization_id, material._marker(row),
                               strict_json(store._get(row["allocation_sha256"])),
                               fs.layout(snapshot), fs.deadline())
            _require(proof == store._get(receipt["filesystem_sha256"]),
                     "completed materialization filesystem changed")
            fs.anchor(intent["root_chain"])
        plan = store._plan(snapshot.identity)
        for index, phase in enumerate(plan.phases):
            _require(not phase.slices and phase.dependencies ==
                     (() if index == 0 else (plan.phases[index - 1].phase_id,)),
                     "execution Base requires an unsliced linear Program")
        index = snapshot.generation
        _require(0 < index < len(plan.phases), "no next accepted-source Program phase")
        accepted = strict_json(store._get(row["acceptance_receipt_sha256"]))
        prior_task, _ = store.programs._execution_ids(
            snapshot.identity.program_id, plan.phases[index - 1].phase_id, None)
        _require(accepted["task_id"] == prior_task, "accepted predecessor is not the prior phase")
        for prior in plan.phases[:index]:
            state = store.connection.execute("""SELECT status FROM program_phases
                WHERE program_id = ? AND phase_id = ?""",
                (plan.program_id, prior.phase_id)).fetchone()
            _require(state is not None and state[0] == "completed",
                     "execution dependency is not completed")
        phase = plan.phases[index]
        phase_row = store.connection.execute("""SELECT * FROM program_phases
            WHERE program_id = ? AND phase_id = ?""", (plan.program_id, phase.phase_id)).fetchone()
        _require(phase_row is not None and phase_row["status"] == "pending",
                 "execution target phase is not pending")
        _require(store.connection.execute("""SELECT 1 FROM program_executions
            WHERE program_id = ? AND phase_id = ?""",
            (plan.program_id, phase.phase_id)).fetchone() is None,
            "execution target phase is already bound")
        task_id, thread_id = store.programs._execution_ids(plan.program_id, phase.phase_id, None)
        binding = {"source_authority": intent["binding"], "phase": dict(phase_row),
                   "program_id": plan.program_id, "phase_id": phase.phase_id,
                   "task_id": task_id, "thread_id": thread_id,
                   "materialization_id": materialization_id,
                   "materialization_receipt_sha256": row["completion_sha256"],
                   "acceptance_receipt_sha256": row["acceptance_receipt_sha256"],
                   "source_sha256": intent["source_sha256"], "generation": index}
        return snapshot, binding

    def begin(self, materialization_id: str, *, owner_token: str) -> dict:
        """Record exact admission before allocating a new private execution destination."""
        store = self.acceptance
        with store._transaction():
            snapshot, binding = self._authority(materialization_id, owner_token)
            self.filesystem.execution_layout(snapshot, store.source)
            row = store.connection.execute("""SELECT * FROM program_execution_bases
                WHERE program_id = ? AND phase_id = ? AND state != 'abandoned'""",
                (binding["program_id"], binding["phase_id"])).fetchone()
            if row is not None:
                self._load(row["operation_id"], owner_token)
                _require(row["materialization_id"] == materialization_id,
                         "execution Base replay uses another materialization")
                return self.status(row["operation_id"])
            with self.filesystem.root_handle() as (_, chain):
                operation_id = uuid.uuid4().hex
                intent = {"schema": "uca-program-execution-base-intent-1",
                          "operation_id": operation_id, "host_sha256": self.host_sha256,
                          "binding": binding, "root_chain": chain}
                sha = store._put(_canonical(intent))
                store.connection.execute("""INSERT INTO program_execution_bases
                    (operation_id, program_id, phase_id, materialization_id, host_sha256,
                     intent_sha256, state) VALUES (?, ?, ?, ?, ?, ?, 'intent')""",
                    (operation_id, binding["program_id"], binding["phase_id"],
                     materialization_id, self.host_sha256, sha))
                self.filesystem.anchor(chain)
            return self.status(operation_id)

    def _row(self, operation_id):
        _require(isinstance(operation_id, str) and re.fullmatch(r"[0-9a-f]{32}", operation_id),
                 "invalid execution Base operation identity")
        row = self.acceptance.connection.execute("""SELECT * FROM program_execution_bases
            WHERE operation_id = ?""", (operation_id,)).fetchone()
        _require(row is not None and row["host_sha256"] == self.host_sha256,
                 "execution Base is missing or host policy changed")
        return row

    def _load(self, operation_id, owner_token):
        row = self._row(operation_id)
        intent = strict_json(self.acceptance._get(row["intent_sha256"]))
        snapshot, binding = self._authority(row["materialization_id"], owner_token)
        _require(intent["operation_id"] == operation_id
                 and intent["host_sha256"] == self.host_sha256
                 and intent["binding"] == binding
                 and binding["program_id"] == row["program_id"]
                 and binding["phase_id"] == row["phase_id"],
                 "execution Base source, phase, owner or control binding changed")
        return row, intent, snapshot

    def status(self, operation_id: str) -> dict:
        """Historical database report only; no filesystem or provider work on reload."""
        with self.acceptance._lock:
            row = self._row(operation_id)
            return {key: row[key] for key in ("operation_id", "state", "intent_sha256",
                                            "completion_sha256", "abandonment_sha256")}

    @staticmethod
    def _marker(row):
        return _canonical({"schema": "uca-owned-execution-base-marker-1",
                           "operation_id": row["operation_id"],
                           "intent_sha256": row["intent_sha256"]})

    def _allocate(self, operation_id, owner_token, deadline):
        store = self.acceptance
        with store._transaction():
            row, intent, _ = self._load(operation_id, owner_token)
            _require(row["state"] != "abandoned", "execution Base was abandoned")
            if row["state"] != "intent":
                return
            with self.filesystem.root_handle(intent["root_chain"]) as (root, _):
                allocation = self.filesystem.allocate(root, "execution-" + operation_id,
                                                       self._marker(row), deadline)
                self.filesystem.anchor(intent["root_chain"])
                self._load(operation_id, owner_token)
                sha = store._put(_canonical(allocation))
                changed = store.connection.execute("""UPDATE program_execution_bases
                    SET state = 'allocated', allocation_sha256 = ?
                    WHERE operation_id = ? AND state = 'intent'""", (sha, operation_id)).rowcount
                _require(changed == 1, "execution Base allocation CAS changed")

    def reconcile(self, operation_id: str, *, owner_token: str) -> dict:
        """Explicitly fill only missing exact files and verify the real derived Git Base."""
        deadline = self.filesystem.deadline()
        self._allocate(operation_id, owner_token, deadline)
        return self._finish(operation_id, owner_token, deadline, allow_fill=True)

    def verify_complete(self, operation_id: str, *, owner_token: str) -> dict:
        return self._finish(operation_id, owner_token, self.filesystem.deadline(), allow_fill=False)

    def _verify_git(self, operation_id, snapshot, layout, deadline):
        inherited = self.acceptance.attestor
        path = self.filesystem.root / ("execution-" + operation_id) / "repo"
        attestor = ProgramGitSourceAttestationService(
            path, inherited.repository_sha256, source_policy=inherited.source.policy,
            git_policy=inherited.policy)
        # All fixed commands share the caller deadline and one cumulative output budget.
        budget = _GitBudget(min(deadline, time.monotonic()
                                + inherited.policy.operation_timeout_seconds),
                            inherited.policy.max_git_output_bytes)
        identity = snapshot.identity
        from dataclasses import replace
        actual = attestor._attest(replace(identity, origin_base_sha=layout.commit_sha,
                                         origin_tree_sha=layout.tree_sha), budget=budget)
        _require(actual.snapshot.files == snapshot.files,
                 "derived execution Base is not the complete accepted source")
        _require(attestor._run(("rev-parse", "HEAD"), b"", budget)
                 == layout.commit_sha.encode() + b"\n", "derived execution HEAD differs")
        _require(attestor._run(("status", "--porcelain=v1", "-z", "-uall"), b"", budget) == b"",
                 "derived execution index or worktree is not clean")
        return actual

    def _finish(self, operation_id, owner_token, deadline, *, allow_fill):
        store = self.acceptance
        with store._transaction():
            row, intent, snapshot = self._load(operation_id, owner_token)
            _require(row["state"] == "complete" or allow_fill and row["state"] == "allocated",
                     "execution Base is not complete or recoverable")
            layout = self.filesystem.execution_layout(snapshot, store.source)
            allocation = strict_json(store._get(row["allocation_sha256"]))
            with self.filesystem.root_handle(intent["root_chain"]) as (root, _):
                args = (root, "execution-" + operation_id, self._marker(row), allocation,
                        layout.tree, deadline)
                proof = self.filesystem.inspect(*args, fill=row["state"] == "allocated")
                if row["state"] == "complete":
                    receipt = strict_json(store._get(row["completion_sha256"]))
                    _require(proof == store._get(receipt["filesystem_sha256"]),
                             "completed execution Base filesystem changed")
                actual = self._verify_git(operation_id, snapshot, layout, deadline)
                self._load(operation_id, owner_token)
                _require(proof == self.filesystem.inspect(*args),
                         "execution Base changed during Git verification")
                self.filesystem.anchor(intent["root_chain"])
                self.filesystem.check_time(deadline)
                expected = {"schema": "uca-program-execution-base-receipt-1",
                            "operation_id": operation_id, "host_sha256": self.host_sha256,
                            "intent_sha256": row["intent_sha256"],
                            "allocation_sha256": row["allocation_sha256"],
                            **intent["binding"],
                            "origin_repository_url": store.repository_url,
                            "origin_repository_sha256": snapshot.identity.repository_sha256,
                            "origin_base_sha": snapshot.identity.origin_base_sha,
                            "origin_tree_sha": snapshot.identity.origin_tree_sha,
                            "derived_git_commit_sha": layout.commit_sha,
                            "derived_git_tree_sha": layout.tree_sha,
                            "derived_git_parents": [], "object_format": layout.object_format,
                            "git_attestation_sha256": store._put(actual.receipt_bytes()),
                            "filesystem_sha256": store._put(proof),
                            "execution_base_complete": True, "dispatch_authorized": False,
                            "cross_phase_source_handoff": False, "automatic_execution": False}
                if row["state"] == "complete":
                    _require(receipt == expected, "completed execution Base receipt differs")
                else:
                    sha = store._put(_canonical(expected))
                    changed = store.connection.execute("""UPDATE program_execution_bases
                        SET state = 'complete', completion_sha256 = ?
                        WHERE operation_id = ? AND state = 'allocated'
                        AND allocation_sha256 = ?""",
                        (sha, operation_id, row["allocation_sha256"])).rowcount
                    _require(changed == 1, "execution Base completion CAS changed")
                return expected

    def abandon(self, operation_id: str, *, owner_token: str, reason: str) -> dict:
        _require(isinstance(reason, str) and 0 < len(reason) <= 2000,
                 "bounded execution Base abandonment reason required")
        store = self.acceptance
        with store._transaction():
            row, _, _ = self._load(operation_id, owner_token)
            _require(row["state"] != "complete", "completed execution Base cannot be abandoned")
            receipt = {"schema": "uca-program-execution-base-abandonment-1",
                       "operation_id": operation_id, "intent_sha256": row["intent_sha256"],
                       "reason": reason, "filesystem_cleanup": False}
            if row["state"] == "abandoned":
                _require(store._get(row["abandonment_sha256"]) == _canonical(receipt),
                         "execution Base abandonment replay differs")
            else:
                sha = store._put(_canonical(receipt))
                store.connection.execute("""UPDATE program_execution_bases
                    SET state = 'abandoned', abandonment_sha256 = ? WHERE operation_id = ?""",
                    (sha, operation_id))
            return receipt
