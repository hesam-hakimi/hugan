"""Explicit materialization of an actual accepted Program source snapshot.

SQLite intent/allocation/completion commits and filesystem durability are separate
boundaries. No provider, Program advancement, Git checkout, publication, cleanup,
or implicit recovery is reachable through this service.
"""

from __future__ import annotations

import re
import uuid

from universal_coding_agent.product.program_source_acceptance import ProgramSourceAcceptanceService
from universal_coding_agent.product.program_source_evidence import strict_json
from universal_coding_agent.product.program_source_transitions import (
    _canonical,
    _digest,
    _hash,
    _identifier,
    _require,
)
from universal_coding_agent.sandbox.owned_source import OwnedSourcePolicy, OwnedSourceTree


class ProgramSourceMaterializationService:
    """Trusted host API using the existing private lifecycle worker ownership.

    `status` is historical information only. `reconcile` explicitly performs
    bounded recovery; `verify_complete` revalidates bytes and current authority.
    A completion receipt is not a SandboxInfo or authority to dispatch a phase.
    """

    def __init__(self, acceptance: ProgramSourceAcceptanceService,
                 policy: OwnedSourcePolicy | None = None):
        self.acceptance = acceptance
        self.policy = policy or OwnedSourcePolicy()
        self.filesystem = OwnedSourceTree(acceptance.safe.artifacts.root.parent / "sandboxes",
                                          self.policy)
        self.host_sha256 = _hash(_canonical({
            "schema": "uca-source-materialization-host-1",
            "acceptance_host_sha256": acceptance.host_sha256,
            "policy_sha256": self.policy.canonical_hash(), "root": str(self.filesystem.root),
        }))
        with acceptance._transaction():
            acceptance.connection.execute("""CREATE TABLE IF NOT EXISTS
                program_source_materializations (
                    operation_id TEXT PRIMARY KEY,
                    program_id TEXT NOT NULL,
                    acceptance_receipt_sha256 TEXT NOT NULL,
                    binding_sha256 TEXT NOT NULL,
                    host_sha256 TEXT NOT NULL,
                    intent_sha256 TEXT NOT NULL,
                    state TEXT NOT NULL
                        CHECK(state IN ('intent','allocated','complete','abandoned')),
                    allocation_sha256 TEXT,
                    completion_sha256 TEXT,
                    abandonment_sha256 TEXT)""")
            acceptance.connection.execute("""CREATE UNIQUE INDEX IF NOT EXISTS
                one_active_source_materialization ON program_source_materializations
                (program_id, acceptance_receipt_sha256, binding_sha256, host_sha256)
                WHERE state != 'abandoned'""")

    def _accepted(self, program_id, receipt_sha256, owner_token):
        _identifier(program_id)
        _digest(receipt_sha256)
        store = self.acceptance
        head = store._head(program_id)
        row = store.connection.execute("""SELECT * FROM program_source_acceptances
            WHERE program_id = ? AND receipt_sha256 = ?""",
                                       (program_id, receipt_sha256)).fetchone()
        _require(row is not None and head["receipt_sha256"] == receipt_sha256,
                 "materialization requires the current actual acceptance receipt")
        receipt = strict_json(store._get(receipt_sha256))
        snapshot = store.source.load_snapshot(store._get(head["source_sha256"]),
                                              expected_sha256=head["source_sha256"])
        _require(receipt.get("schema") == "uca-source-acceptance-receipt-1"
                 and receipt.get("materialization_ready") is False
                 and receipt.get("host_sha256") == store.host_sha256
                 and receipt.get("program_id") == snapshot.identity.program_id == program_id
                 and receipt.get("source_sha256") == head["source_sha256"]
                 and receipt.get("generation") == snapshot.generation == head["generation"]
                 and receipt.get("predecessor_sha256") == snapshot.predecessor_sha256
                 and receipt.get("candidate_sha256") == row["candidate_sha256"]
                 and receipt.get("approval_sha256") == row["approval_sha256"]
                 and receipt.get("task_id") == row["task_id"],
                 "accepted source receipt or lineage differs")
        binding = store._binding(snapshot.identity, owner_token)
        store._plan(snapshot.identity)
        return receipt, snapshot, binding

    def begin(self, program_id: str, *, acceptance_receipt_sha256: str,
              owner_token: str) -> dict:
        """Persist an owner-bound intent. No destination is created by this call."""
        store = self.acceptance
        with store._transaction():
            receipt, snapshot, binding = self._accepted(program_id, acceptance_receipt_sha256,
                                                        owner_token)
            self.filesystem.layout(snapshot)
            binding_sha = _hash(_canonical(binding))
            existing = store.connection.execute("""SELECT operation_id FROM
                program_source_materializations WHERE program_id = ?
                AND acceptance_receipt_sha256 = ? AND binding_sha256 = ?
                AND host_sha256 = ? AND state != 'abandoned'""",
                (program_id, acceptance_receipt_sha256, binding_sha, self.host_sha256)).fetchone()
            if existing:
                return self.status(existing[0])
            with self.filesystem.root_handle() as (_, chain):
                operation_id = uuid.uuid4().hex
                intent = {"schema": "uca-source-materialization-intent-1",
                          "operation_id": operation_id, "program_id": program_id,
                          "acceptance_receipt_sha256": acceptance_receipt_sha256,
                          "source_sha256": receipt["source_sha256"],
                          "predecessor_sha256": receipt["predecessor_sha256"],
                          "generation": receipt["generation"], "binding": binding,
                          "host_sha256": self.host_sha256, "root_chain": chain}
                intent_sha = store._put(_canonical(intent))
                store.connection.execute("""INSERT INTO program_source_materializations
                    (operation_id, program_id, acceptance_receipt_sha256, binding_sha256,
                     host_sha256, intent_sha256, state) VALUES (?, ?, ?, ?, ?, ?, 'intent')""",
                    (operation_id, program_id, acceptance_receipt_sha256, binding_sha,
                     self.host_sha256, intent_sha))
                self.filesystem.anchor(chain)
            return self.status(operation_id)

    def _row(self, operation_id):
        _require(isinstance(operation_id, str) and re.fullmatch(r"[0-9a-f]{32}", operation_id)
                 is not None, "invalid materialization operation identity")
        row = self.acceptance.connection.execute("""SELECT * FROM
            program_source_materializations WHERE operation_id = ?""", (operation_id,)).fetchone()
        _require(row is not None and row["host_sha256"] == self.host_sha256,
                 "materialization is missing or host policy changed")
        return row

    def status(self, operation_id: str) -> dict:
        """Read durable state without filesystem inspection, writes or recovery."""
        with self.acceptance._lock:
            row = self._row(operation_id)
            return {"operation_id": operation_id, "state": row["state"],
                    "intent_sha256": row["intent_sha256"],
                    "completion_sha256": row["completion_sha256"],
                    "abandonment_sha256": row["abandonment_sha256"]}

    def _load(self, operation_id, owner_token):
        row = self._row(operation_id)
        intent = strict_json(self.acceptance._get(row["intent_sha256"]))
        _require(intent["operation_id"] == operation_id
                 and intent["program_id"] == row["program_id"]
                 and intent["host_sha256"] == self.host_sha256
                 and intent["acceptance_receipt_sha256"] == row["acceptance_receipt_sha256"]
                 and _hash(_canonical(intent["binding"])) == row["binding_sha256"],
                 "materialization intent binding differs")
        receipt, snapshot, binding = self._accepted(row["program_id"],
                                                    row["acceptance_receipt_sha256"], owner_token)
        _require(binding == intent["binding"]
                 and all(receipt[key] == intent[key] for key in
                         ("source_sha256", "predecessor_sha256", "generation")),
                 "materialization owner, control revision or source CAS changed")
        return row, intent, snapshot

    @staticmethod
    def _marker(row):
        return _canonical({"schema": "uca-owned-source-marker-1",
                           "operation_id": row["operation_id"],
                           "intent_sha256": row["intent_sha256"]})

    def _allocate(self, operation_id, owner_token, deadline):
        store = self.acceptance
        with store._transaction():
            row, intent, _ = self._load(operation_id, owner_token)
            _require(row["state"] != "abandoned", "materialization was abandoned")
            if row["state"] != "intent":
                return
            with self.filesystem.root_handle(intent["root_chain"]) as (root, _):
                allocation = self.filesystem.allocate(root, "source-" + operation_id,
                                                       self._marker(row), deadline)
                self.filesystem.anchor(intent["root_chain"])
                self._load(operation_id, owner_token)
                allocation_sha = store._put(_canonical(allocation))
                changed = store.connection.execute("""UPDATE program_source_materializations
                    SET state = 'allocated', allocation_sha256 = ?
                    WHERE operation_id = ? AND state = 'intent' AND intent_sha256 = ?""",
                    (allocation_sha, operation_id, row["intent_sha256"])).rowcount
                _require(changed == 1, "materialization allocation CAS changed")

    def reconcile(self, operation_id: str, *, owner_token: str) -> dict:
        """Explicit recovery: create missing files or verify a fully staged tree.

        An ambiguous allocation or an incomplete/corrupt existing file is never
        adopted/overwritten. The owner may abandon the record and begin anew.
        """
        deadline = self.filesystem.deadline()
        self._allocate(operation_id, owner_token, deadline)
        return self._finish(operation_id, owner_token, deadline, allow_fill=True)

    def verify_complete(self, operation_id: str, *, owner_token: str) -> dict:
        """Revalidate the current accepted lineage and exact complete filesystem.

        This does not create a Git checkout or authorize a subsequent execution.
        Every future source consumer must repeat verification at its own boundary.
        """
        return self._finish(operation_id, owner_token, self.filesystem.deadline(), allow_fill=False)

    def _finish(self, operation_id, owner_token, deadline, *, allow_fill):
        store = self.acceptance
        with store._transaction():
            row, intent, snapshot = self._load(operation_id, owner_token)
            _require(row["state"] == "complete" or allow_fill and row["state"] == "allocated",
                     "materialization is not complete or recoverable")
            tree = self.filesystem.layout(snapshot)
            allocation = strict_json(store._get(row["allocation_sha256"]))
            with self.filesystem.root_handle(intent["root_chain"]) as (root, _):
                arguments = (root, "source-" + operation_id, self._marker(row), allocation,
                             tree, deadline)
                proof = self.filesystem.inspect(*arguments, fill=row["state"] == "allocated")
                if row["state"] == "complete":
                    receipt = strict_json(store._get(row["completion_sha256"]))
                    _require(receipt["intent_sha256"] == row["intent_sha256"]
                             and receipt["allocation_sha256"] == row["allocation_sha256"]
                             and proof == store._get(receipt["filesystem_sha256"]),
                             "completed source filesystem or receipt changed")
                else:
                    receipt = {"schema": "uca-source-materialization-receipt-1",
                               "operation_id": operation_id,
                               "intent_sha256": row["intent_sha256"],
                               "allocation_sha256": row["allocation_sha256"],
                               "acceptance_receipt_sha256": row["acceptance_receipt_sha256"],
                               "source_sha256": intent["source_sha256"],
                               "predecessor_sha256": intent["predecessor_sha256"],
                               "generation": intent["generation"],
                               "host_sha256": self.host_sha256,
                               "filesystem_sha256": store._put(proof),
                               "origin_base_sha": snapshot.identity.origin_base_sha,
                               "origin_tree_sha": snapshot.identity.origin_tree_sha,
                               "derived_git_commit_sha": None, "derived_git_tree_sha": None,
                               "materialization_complete": True, "automatic_execution": False}
                self._load(operation_id, owner_token)
                _require(proof == self.filesystem.inspect(*arguments),
                         "source changed at completion boundary")
                self.filesystem.anchor(intent["root_chain"])
                self.filesystem.check_time(deadline)
                if row["state"] != "complete":
                    receipt_sha = store._put(_canonical(receipt))
                    changed = store.connection.execute("""UPDATE program_source_materializations
                        SET state = 'complete', completion_sha256 = ? WHERE operation_id = ?
                        AND state = 'allocated' AND allocation_sha256 = ?""",
                        (receipt_sha, operation_id, row["allocation_sha256"])).rowcount
                    _require(changed == 1, "materialization completion CAS changed")
                return receipt

    def abandon(self, operation_id: str, *, owner_token: str, reason: str) -> dict:
        """Record explicit abandonment; preserve every filesystem byte for inspection."""
        _require(isinstance(reason, str) and 0 < len(reason) <= 2000,
                 "bounded materialization abandonment reason required")
        store = self.acceptance
        with store._transaction():
            row, _, _ = self._load(operation_id, owner_token)
            _require(row["state"] != "complete", "a completed materialization cannot be abandoned")
            receipt = {"schema": "uca-source-materialization-abandonment-1",
                       "operation_id": operation_id, "intent_sha256": row["intent_sha256"],
                       "reason": reason, "filesystem_cleanup": False}
            if row["state"] == "abandoned":
                _require(store._get(row["abandonment_sha256"]) == _canonical(receipt),
                         "materialization abandonment replay differs")
            else:
                sha = store._put(_canonical(receipt))
                store.connection.execute("""UPDATE program_source_materializations
                    SET state = 'abandoned', abandonment_sha256 = ? WHERE operation_id = ?""",
                                         (sha, operation_id))
            return receipt
