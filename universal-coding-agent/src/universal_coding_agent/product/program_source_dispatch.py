"""Explicit source-aware execution admission, checkpoint reconciliation and Safe adapter.

The execution state machine is versioned separately from Safe's edit protocol.
An interrupted effectful invocation is never repeated from an intermediate checkpoint.
"""

from __future__ import annotations

import base64
import os
from dataclasses import replace
from pathlib import Path

from universal_coding_agent.core.safe_models import (
    SafeTaskRequest,
)
from universal_coding_agent.discovered_safe_service import DiscoveredSafeAgentService
from universal_coding_agent.product.models import PhaseResult, ProgramExecutionBinding
from universal_coding_agent.product.program_execution_base import ProgramExecutionBaseService
from universal_coding_agent.product.program_source_evidence import (
    _capture_at_owned_destination,
    strict_json,
)
from universal_coding_agent.product.program_source_execution_adapter import AdmittedSafeExecution
from universal_coding_agent.product.program_source_transitions import (
    _canonical,
    _digest,
    _hash,
    _identifier,
    _require,
)


def _protocol():
    value = os.environ.get("UCA_SAFE_EDIT_PROTOCOL", "v1").strip().lower()
    if value in {"v2", "v2-line-addressed", "line-addressed"}:
        return "v2-line-addressed"
    _require(value == "v1", "unsupported Safe edit protocol")
    return value


class ProgramSourceDispatchService:
    def __init__(self, preparation: ProgramExecutionBaseService, provider):
        self.preparation, self.store, self.provider = preparation, preparation.acceptance, provider
        self.store.safe.bind_source_dispatch_control()
        self.host_sha256 = _hash(
            _canonical(
                {
                    "schema": "uca-program-source-dispatch-host-2",
                    "atomic_store_policy": "rollback-full-bound-root-once-handoff-2",
                    "preparation_host_sha256": preparation.host_sha256,
                    "edit_protocol": _protocol(),
                }
            )
        )
        with self.store._transaction():
            self.store.connection.execute("""CREATE TABLE IF NOT EXISTS program_source_dispatches (
                operation_id TEXT PRIMARY KEY, task_id TEXT NOT NULL UNIQUE,
                admission_sha256 TEXT NOT NULL UNIQUE, host_sha256 TEXT NOT NULL,
                state TEXT NOT NULL, authority_sha256 TEXT NOT NULL,
                filesystem_sha256 TEXT NOT NULL, retained_sha256 TEXT NOT NULL,
                task_sha256 TEXT, discovery_sha256 TEXT, approval_sha256 TEXT,
                checkpoint_sha256 TEXT, result_sha256 TEXT,
                invocation_sha256 TEXT, invocation_kind TEXT, invocation_state TEXT)""")
        self.store.source_dispatch = self

    def _durability(self):
        self.store.safe.verify_source_dispatch_control(required=True)
        # Only these two databases are written by admission/result transactions.
        # The attached WAL checkpoint database is held against writers and READ ONLY.
        for alias in ("main", "control"):
            mode = self.store.connection.execute(f"PRAGMA {alias}.journal_mode").fetchone()[0]
            sync = self.store.connection.execute(f"PRAGMA {alias}.synchronous").fetchone()[0]
            _require(
                mode in {"delete", "truncate", "persist"} and sync >= 2,
                "v2 atomic admission requires durable rollback journals for Program/control",
            )

    def _json(self, digest):
        return strict_json(self.store._get(digest))

    @staticmethod
    def _result_prefix(program, phase, task, state):
        return (
            f"programs/{program}/phases/{phase}/executions/{task}/"
            f"source-results/{_hash(_canonical(state))}"
        )

    def _row(self, operation_id):
        _require(
            isinstance(operation_id, str)
            and len(operation_id) == 32
            and all(c in "0123456789abcdef" for c in operation_id),
            "invalid admission ID",
        )
        row = self.store.connection.execute(
            """SELECT * FROM program_source_dispatches
            WHERE operation_id = ?""",
            (operation_id,),
        ).fetchone()
        _require(
            row is not None and row["host_sha256"] == self.host_sha256,
            "source-aware admission is missing or belongs to another host",
        )
        return row

    def status(self, operation_id):
        """Database-only historical observation. Does not validate or repair a filesystem."""
        with self.store._lock:
            row = self._row(operation_id)
            admission = self._json(row["admission_sha256"])
            task = (
                SafeTaskRequest.model_validate(self._json(row["task_sha256"]))
                if row["task_sha256"]
                else None
            )
            result = {
                k: row[k]
                for k in (
                    "operation_id",
                    "task_id",
                    "admission_sha256",
                    "state",
                    "task_sha256",
                    "approval_sha256",
                    "checkpoint_sha256",
                    "result_sha256",
                )
            }
            result.update(
                execution_schema=admission["schema"],
                program_id=admission["program_id"],
                phase_id=admission["phase_id"],
                thread_id=admission["thread_id"],
                scope=task.manifest.model_dump(mode="json") if task else None,
                scope_sha256=task.manifest.canonical_hash() if task else None,
                automatic_execution=False,
            )
            return result

    def _authority(self, admission, owner_token):
        store = self.store
        before = store.source.load_snapshot(
            store._get(admission["source_sha256"]), expected_sha256=admission["source_sha256"]
        )
        binding = store._binding(before.identity, owner_token)
        store._plan(before.identity)
        _require(
            binding["owner_binding_sha256"] == admission["owner_binding_sha256"],
            "source-aware worker ownership changed",
        )
        task = admission["task_id"]
        execution = store.connection.execute(
            "SELECT * FROM program_executions WHERE task_id = ?", (task,)
        ).fetchone()
        phase = store.connection.execute(
            """SELECT * FROM program_phases
            WHERE program_id = ? AND phase_id = ?""",
            (admission["program_id"], admission["phase_id"]),
        ).fetchone()
        control = store.connection.execute(
            """SELECT * FROM control.control_state
            WHERE entity_type = 'task' AND entity_id = ?""",
            (task,),
        ).fetchone()
        _require(
            execution is not None and phase is not None and control is not None,
            "source-aware execution authority is incomplete",
        )
        binding.update(execution=dict(execution), phase=dict(phase), task_control=dict(control))
        return binding, before

    def _load(self, operation_id, owner_token, *, after_finalize=False, accepted_replay=False):
        self._durability()
        row = self._row(operation_id)
        admission = self._json(row["admission_sha256"])
        _require(
            admission["schema"] == "uca-program-source-dispatch-2"
            and admission["operation_id"] == operation_id
            and admission["host_sha256"] == self.host_sha256
            and admission["task_id"] == row["task_id"]
            and admission["edit_protocol"] == _protocol(),
            "stored v2 admission differs",
        )
        binding, before = self._authority(admission, owner_token)
        expected = self._json(row["authority_sha256"])
        if after_finalize:
            expected = {
                **expected,
                "task_control": {
                    **expected["task_control"],
                    "state": "completed",
                    "reason": "",
                    "revision": expected["task_control"]["revision"] + 1,
                },
            }
        _require(binding == expected, "source-aware execution/control authority changed")
        head = self.store._head(admission["program_id"])
        if accepted_replay:
            prior = self.store.connection.execute(
                """SELECT receipt_sha256
                FROM program_source_acceptances WHERE program_id = ? AND task_id = ?""",
                (admission["program_id"], admission["task_id"]),
            ).fetchone()
            _require(
                prior is not None and head["receipt_sha256"] == prior[0],
                "source-aware acceptance replay is not current",
            )
            receipt = self._json(prior[0])
            _require(
                receipt["predecessor_sha256"] == admission["source_sha256"]
                and receipt["generation"] == admission["generation"] + 1,
                "accepted v2 lineage changed",
            )
        else:
            _require(
                head["source_sha256"] == admission["source_sha256"]
                and head["generation"] == admission["generation"]
                and head["receipt_sha256"] == admission["acceptance_receipt_sha256"],
                "source-aware predecessor or source generation changed",
            )
        registered = self.store.connection.execute(
            """SELECT * FROM control.uca_source_dispatch_tasks
            WHERE task_id = ?""",
            (admission["task_id"],),
        ).fetchone()
        _require(
            registered is not None
            and dict(registered)
            == {
                "task_id": admission["task_id"],
                "thread_id": admission["thread_id"],
                "admission_sha256": row["admission_sha256"],
                "host_sha256": self.host_sha256,
            },
            "Safe checkpoint admission registry differs",
        )
        _require(
            self._lineage(admission, before) == self.store._get(admission["dependency_sha256"]),
            "accepted dependency evidence changed after admission",
        )
        if row["discovery_sha256"]:
            for item in self._json(row["discovery_sha256"]):
                self.store.safe.artifacts.read_bytes_bounded_verified(
                    item["ref"], expected_sha256=item["sha256"], max_bytes=2_000_000
                )
        if row["result_sha256"]:
            digests = self._json(row["result_sha256"])
            for key, digest in (
                ("result_ref", digests["result_sha256"]),
                ("phase_report_ref", digests["report_sha256"]),
            ):
                self.store.programs.artifacts.read_bytes_bounded_verified(
                    binding["execution"][key], expected_sha256=digest, max_bytes=8_000_000
                )
        return row, admission, before

    def _lineage(self, receipt, before):
        """Versioned dependency context: exact accepted predecessors, never a v1 Base relabel."""
        plan = self.store._plan(before.identity)
        entries, previous = [], None
        for index, phase in enumerate(plan.phases[: before.generation]):
            task, _ = self.store.programs._execution_ids(plan.program_id, phase.phase_id, None)
            row = self.store.connection.execute(
                """SELECT * FROM program_source_acceptances
                WHERE program_id = ? AND task_id = ?""",
                (plan.program_id, task),
            ).fetchone()
            _require(row is not None, "dependency source acceptance is missing")
            accepted = self._json(row["receipt_sha256"])
            _require(
                accepted["generation"] == index + 1
                and (previous is None or accepted["predecessor_sha256"] == previous),
                "dependency acceptance lineage differs",
            )
            candidate = self._json(row["candidate_sha256"])
            frozen = self._json(candidate["evidence_sha256"])
            prefix = f"programs/{plan.program_id}/phases/{phase.phase_id}"
            refs = [
                f"artifact://{prefix}/executions/{task}/safe-result-completed.json",
                f"artifact://{prefix}/phase-execution-report.json",
                f"artifact://{prefix}/phase-result.json",
                f"artifact://{prefix}/phase-summary.md",
            ]
            if frozen["schema"] == "uca-program-safe-source-evidence-2":
                saved_state = strict_json(base64.b64decode(frozen["program_result_base64"]))
                prefix = self._result_prefix(plan.program_id, phase.phase_id, task, saved_state)
                refs = [
                    f"artifact://{prefix}/{name}"
                    for name in ("safe-result.json", "phase-execution-report.json",
                                 "phase-result.json", "phase-summary.md")
                ]
            raw = [
                self.store.programs.artifacts._read_bytes_bounded(ref, max_bytes=2_000_000)
                for ref in refs
            ]
            _require(
                base64.b64decode(frozen["program_result_base64"], validate=True) == raw[0]
                and base64.b64decode(frozen["phase_report_base64"], validate=True) == raw[1],
                "accepted dependency Program artifacts changed",
            )
            result = PhaseResult.model_validate(strict_json(raw[2]))
            safe_result = strict_json(raw[0])
            safe_result = safe_result.get("state", safe_result)
            _require(
                tuple(result.changed_paths) == tuple(safe_result.get("actual_changed_paths", ()))
                and result.tests == (f"{task}: {safe_result.get('tests_ref')}",)
                and self.store.programs._phase_summary(plan.program_id, result).encode() == raw[3],
                "dependency result/summary differs from actual Safe evidence",
            )
            _require(
                result.phase_id == phase.phase_id
                and result.reviewer_verdict == "PASS"
                and bool(result.tests),
                "dependency phase result is not qualified",
            )
            entries.append(
                {
                    "phase_id": phase.phase_id,
                    "task_id": task,
                    "acceptance_receipt_sha256": row["receipt_sha256"],
                    "source_sha256": accepted["source_sha256"],
                    "predecessor_sha256": accepted["predecessor_sha256"],
                    "artifacts": [
                        {"ref": ref, "sha256": _hash(data)}
                        for ref, data in zip(refs, raw, strict=True)
                    ],
                    "summary": result.summary,
                }
            )
            previous = accepted["source_sha256"]
        _require(previous == receipt["source_sha256"], "dependency head is not the current source")
        content = _canonical(
            {
                "schema": "uca-accepted-source-lineage-2",
                "program_id": plan.program_id,
                "requirement_sha256": before.identity.requirement_sha256,
                "plan_sha256": before.identity.plan_sha256,
                "target_phase_id": receipt["phase_id"],
                "execution_base_sha": receipt["derived_git_commit_sha"],
                "source_sha256": previous,
                "phases": entries,
            }
        )
        _require(len(content) <= 48_000, "source-aware dependency context exceeds its bound")
        return content

    def admit(self, operation_id: str, *, preparation_receipt_sha256: str, owner_token: str):
        _digest(preparation_receipt_sha256)
        store, base = self.store, self.preparation
        with store._transaction():
            self._durability()
            existing = store.connection.execute(
                """SELECT 1 FROM program_source_dispatches
                WHERE operation_id = ?""",
                (operation_id,),
            ).fetchone()
            if existing:
                row, admission, _ = self._load(operation_id, owner_token)
                _require(
                    admission["preparation_receipt_sha256"] == preparation_receipt_sha256,
                    "consumed preparation receipt differs",
                )
                self._verify_files(row, admission)
                return self.status(operation_id)
            receipt = base._finish_locked(
                operation_id, owner_token, base.filesystem.deadline(), allow_fill=False
            )
            _require(
                _hash(_canonical(receipt)) == preparation_receipt_sha256,
                "exact preparation receipt approval differs",
            )
            before = store.current(receipt["program_id"])
            authority = store._binding(before.identity, owner_token)
            _require(
                authority["program"]["status"] == "running"
                and authority["program_control"]["state"] == "running",
                "admission requires a running Program",
            )
            context = self._lineage(receipt, before)
            context_ref = store.programs.artifacts.write_text(
                f"programs/{receipt['program_id']}/source-dispatch/{operation_id}/lineage-v2.json",
                context.decode(),
                "application/json",
            )
            base_row = dict(base._row(operation_id))
            material_row = dict(base.materialization._row(receipt["materialization_id"]))
            admission = {
                "schema": "uca-program-source-dispatch-2",
                "operation_id": operation_id,
                "host_sha256": self.host_sha256,
                "preparation_receipt_sha256": preparation_receipt_sha256,
                "preparation_row": base_row,
                "materialization_row": material_row,
                "owner_binding_sha256": authority["owner_binding_sha256"],
                "edit_protocol": _protocol(),
                "dependency_ref": context_ref.uri,
                "dependency_sha256": store._put(context),
                "dispatch_authorized": True,
                "automatic_execution": False,
                **{
                    key: receipt[key]
                    for key in (
                        "program_id",
                        "phase_id",
                        "task_id",
                        "thread_id",
                        "generation",
                        "source_sha256",
                        "acceptance_receipt_sha256",
                        "materialization_id",
                        "materialization_receipt_sha256",
                        "origin_repository_url",
                        "origin_repository_sha256",
                        "origin_base_sha",
                        "origin_tree_sha",
                        "derived_git_commit_sha",
                        "derived_git_tree_sha",
                    )
                },
            }
            _require(
                not store.connection.execute(
                    """SELECT 1 FROM safe.checkpoints
                WHERE thread_id = ? LIMIT 1""",
                    (admission["thread_id"],),
                ).fetchone(),
                "execution thread already has a Safe checkpoint",
            )
            sha = store._put(_canonical(admission))
            store.connection.execute(
                """INSERT INTO program_executions
                (program_id, phase_id, unit_key, task_id, thread_id, requirement_hash, status,
                 expected_base_sha) VALUES (?, ?, '__phase__', ?, ?, ?, 'starting', ?)""",
                (
                    admission["program_id"],
                    admission["phase_id"],
                    admission["task_id"],
                    admission["thread_id"],
                    before.identity.requirement_sha256,
                    admission["derived_git_commit_sha"],
                ),
            )
            changed = store.connection.execute(
                """UPDATE program_phases SET status = 'running'
                WHERE program_id = ? AND phase_id = ? AND status = 'pending'""",
                (admission["program_id"], admission["phase_id"]),
            ).rowcount
            _require(changed == 1, "phase admission CAS changed")
            store.connection.execute(
                """INSERT INTO control.control_state
                VALUES ('task', ?, 'running', '', 0)""",
                (admission["task_id"],),
            )
            store.connection.execute(
                "INSERT INTO control.uca_source_dispatch_tasks VALUES (?, ?, ?, ?)",
                (admission["task_id"], admission["thread_id"], sha, self.host_sha256),
            )
            binding, _ = self._authority(admission, owner_token)
            store.connection.execute(
                """INSERT INTO program_source_dispatches
                (operation_id, task_id, admission_sha256, host_sha256, state, authority_sha256,
                 filesystem_sha256, retained_sha256) VALUES (?, ?, ?, ?, 'admitted', ?, ?, ?)""",
                (
                    operation_id,
                    admission["task_id"],
                    sha,
                    self.host_sha256,
                    store._put(_canonical(binding)),
                    receipt["filesystem_sha256"],
                    receipt["source_sha256"],
                ),
            )
            return self.status(operation_id)

    def _verify_files(self, row, admission, *, retained=None, mutable=()):
        """Verify immutable material and complete private worktree including .git and inodes."""
        base, store = self.preparation, self.store
        b = base._row(admission["operation_id"])
        m = base.materialization._row(admission["materialization_id"])
        _require(
            dict(b) == admission["preparation_row"] and dict(m) == admission["materialization_row"],
            "consumed preparation changed",
        )
        before = store.source.load_snapshot(
            store._get(admission["source_sha256"]), expected_sha256=admission["source_sha256"]
        )
        material = base.materialization
        intent = self._json(m["intent_sha256"])
        receipt = self._json(m["completion_sha256"])
        fs, deadline = material.filesystem, base.filesystem.deadline()
        with fs.root_handle(intent["root_chain"]) as (root, _):
            proof = fs.inspect(
                root,
                "source-" + m["operation_id"],
                material._marker(m),
                self._json(m["allocation_sha256"]),
                fs.layout(before),
                deadline,
            )
            _require(
                proof == store._get(receipt["filesystem_sha256"]),
                "accepted immutable materialization changed",
            )
            fs.anchor(intent["root_chain"])
        current = retained or store.source.load_snapshot(
            store._get(row["retained_sha256"]), expected_sha256=row["retained_sha256"]
        )
        layout = base.filesystem.execution_layout(before, store.source)
        tree = base.filesystem.layout(current)
        tree[".git"] = layout.tree[".git"]
        intent = self._json(b["intent_sha256"])
        fs = base.filesystem
        with fs.root_handle(intent["root_chain"]) as (root, _):
            proof = fs.inspect(
                root,
                "execution-" + b["operation_id"],
                base._marker(b),
                self._json(b["allocation_sha256"]),
                tree,
                deadline,
            )
            old, new = self._json(row["filesystem_sha256"]), strict_json(proof)
            _require(
                old["owner"] == new["owner"]
                and old["operation"] == new["operation"]
                and set(old["entries"]) == set(new["entries"]),
                "owned execution inventory changed",
            )
            parents = {""}
            for path in mutable:
                parents.update(
                    str(parent) + "/" for parent in Path(path).parents if str(parent) != "."
                )
            for path, stamp in new["entries"].items():
                expected = old["entries"][path]
                if path in mutable:
                    _require(
                        stamp[:1] == expected[:1] and stamp[2:5] == expected[2:5] and stamp[6] == 1,
                        "approved edit ownership/mode changed",
                    )
                elif mutable and path in parents:
                    _require(stamp[:5] == expected[:5], "approved parent was substituted")
                else:
                    _require(stamp == expected, "retained source or Git metadata changed")
            if current.files == before.files:
                base._verify_git(b["operation_id"], before, layout, deadline)
            fs.anchor(intent["root_chain"])
        return proof

    def _adapter(self, operation_id, owner_token):
        return AdmittedSafeExecution(self, operation_id, owner_token)

    def dispatch(self, operation_id, *, owner_token):
        adapter = self._adapter(operation_id, owner_token)
        with self.store._transaction():
            row, admission, _ = self._load(operation_id, owner_token)
            _require(
                row["state"] in {"admitted", "discovered"},
                "dispatch already started; use explicit checkpoint reconciliation",
            )
            self._verify_files(row, admission)
            fresh = row["state"] == "admitted"
            if fresh:
                self._state(operation_id, "admitted", "discovery_started")
            adapter._authorize("discovery" if fresh else "safe_prepare")
        if fresh:
            self._discovery().start_admitted(adapter)
        else:
            adapter.start_safe()
            with adapter.safe_service() as safe:
                safe.run(adapter.task())
        return self.reconcile(operation_id, owner_token=owner_token)

    def _discovery(self):
        return DiscoveredSafeAgentService.create(
            self.store.safe.artifacts.root.parent,
            self.provider,
            control=self.store.safe.control,
            remote_operations=self.store.safe.remote_operations,
        )

    def _state(self, operation_id, old, new, **fields):
        assignments = ", ".join(["state = ?", *(key + " = ?" for key in fields)])
        changed = self.store.connection.execute(
            f"UPDATE program_source_dispatches SET {assignments} "
            "WHERE operation_id = ? AND state = ?",
            (new, *fields.values(), operation_id, old),
        ).rowcount
        _require(changed == 1, "source-aware dispatch state CAS changed")

    def approve_scope(self, operation_id, *, owner_token, scope_sha256, approved, approval_id):
        _digest(scope_sha256)
        _identifier(approval_id)
        _require(type(approved) is bool, "explicit scope decision is required")
        adapter = self._adapter(operation_id, owner_token)
        with self.store._transaction():
            row, admission, _ = self._load(operation_id, owner_token)
            _require(row["state"] == "awaiting_scope_approval", "scope decision is not pending")
            task = SafeTaskRequest.model_validate(self._json(row["task_sha256"]))
            _require(task.manifest.canonical_hash() == scope_sha256, "new exact scope hash differs")
            self._verify_files(row, admission)
            checkpoint, state, next_nodes = self._checkpoint(admission)
            _require(
                _hash(checkpoint) == row["checkpoint_sha256"]
                and next_nodes == ("scope_approval",)
                and not state.get("scope_approved"),
                "scope checkpoint changed",
            )
            approval = {
                "schema": "uca-source-dispatch-scope-decision-2",
                "admission_sha256": row["admission_sha256"],
                "approval_id": approval_id,
                "scope_sha256": scope_sha256,
                "approved": approved,
            }
            self._state(
                operation_id,
                row["state"],
                "resume_started",
                approval_sha256=self.store._put(_canonical(approval)),
            )
            adapter._authorize("resume")
        with adapter.safe_service() as safe:
            safe.resume(admission["thread_id"], approved)
        return self.reconcile(operation_id, owner_token=owner_token)

    def _checkpoint(self, admission):
        """Read the actual checkpoint, including bounded pending interrupt writes."""
        db = self.store.connection
        sizes = db.execute(
            """SELECT length(checkpoint), length(metadata) FROM safe.checkpoints
            WHERE thread_id = ? AND checkpoint_ns = ''
            ORDER BY checkpoint_id DESC LIMIT 1""",
            (admission["thread_id"],),
        ).fetchone()
        _require(
            sizes is not None and sum(sizes) <= 16_000_000,
            "missing or oversized Safe handoff checkpoint",
        )
        row = db.execute(
            """SELECT * FROM safe.checkpoints WHERE thread_id = ?
            AND checkpoint_ns = '' ORDER BY checkpoint_id DESC LIMIT 1""",
            (admission["thread_id"],),
        ).fetchone()
        _require(row is not None, "Safe handoff has no proven checkpoint")
        # SQLite length checks precede pending-write payload retrieval.
        _require(
            sum(len(v) for v in row if isinstance(v, bytes)) <= 16_000_000,
            "Safe checkpoint exceeds dispatch bound",
        )
        args = (admission["thread_id"], row["checkpoint_id"])
        sizes = db.execute(
            """SELECT count(*), coalesce(sum(length(value)), 0) FROM safe.writes
            WHERE thread_id = ? AND checkpoint_ns = '' AND checkpoint_id = ?""",
            args,
        ).fetchone()
        _require(sizes[0] <= 128 and sizes[1] <= 16_000_000, "Safe writes exceed dispatch bound")
        writes = db.execute(
            """SELECT * FROM safe.writes WHERE thread_id = ?
            AND checkpoint_ns = '' AND checkpoint_id = ? ORDER BY task_id, idx""",
            args,
        ).fetchall()

        def encoded(r):
            return {
                k: base64.b64encode(v).decode() if isinstance(v, bytes) else v
                for k, v in dict(r).items()
            }

        raw = _canonical({"checkpoint": encoded(row), "writes": [encoded(w) for w in writes]})
        point = self.store.safe.graph.get_state(
            {
                "configurable": {
                    "thread_id": admission["thread_id"],
                    "checkpoint_id": row["checkpoint_id"],
                }
            }
        )
        state = point.values
        stored = self._row(admission["operation_id"])
        _require(
            state.get("task") == self._json(stored["task_sha256"]),
            "checkpoint task/thread does not match stored v2 admission",
        )
        if state.get("sandbox_path"):
            _require(
                state["sandbox_path"]
                == str(
                    self.preparation.filesystem.root
                    / ("execution-" + admission["operation_id"])
                    / "repo"
                ),
                "checkpoint destination differs from stored admission",
            )
        if not point.next:
            _require(not point.tasks and not writes, "terminal Safe checkpoint has pending work")
        return raw, state, tuple(point.next)

    def reconcile(self, operation_id, *, owner_token):
        """No provider work: accept only a real scope stop or a terminal Safe checkpoint."""
        with self.store._transaction():
            row, admission, _ = self._load(operation_id, owner_token)
            _require(
                row["state"]
                in {"safe_started", "resume_started", "awaiting_scope_approval", "terminal"},
                "no recoverable Safe handoff; started discovery is ambiguous",
            )
            self._verify_files(row, admission)
            checkpoint, state, next_nodes = self._checkpoint(admission)
            if row["state"] in {"awaiting_scope_approval", "terminal"}:
                _require(
                    _hash(checkpoint) == row["checkpoint_sha256"], "recorded checkpoint drifted"
                )
                return self.status(operation_id)
            if row["state"] == "safe_started":
                _require(
                    next_nodes == ("scope_approval",)
                    and state.get("status") == "awaiting_scope_approval"
                    and state.get("scope_approved") is None,
                    "Safe start is ambiguous; no exact scope stop",
                )
                target, execution_status = "awaiting_scope_approval", "awaiting_scope_approval"
            else:
                _require(
                    not next_nodes and state.get("status") in {"completed", "failed", "blocked"},
                    "Safe resume is ambiguous; provider work cannot be replayed",
                )
                approval = self._json(row["approval_sha256"])
                _require(
                    state.get("scope_approved") is approval["approved"],
                    "actual Safe scope decision differs",
                )
                target = "terminal"
                execution_status = "completed" if state["status"] == "completed" else "failed"
                if execution_status == "completed":
                    self._capture_safe(row, admission, state)
            self._record(row, admission, state, execution_status)
            # Current authority was verified before the result transaction. Read its
            # exact post-result rows here, including the intentional blocked outcome.
            authority = self._json(row["authority_sha256"])
            for key, query, parameters in (
                (
                    "program",
                    "SELECT * FROM programs WHERE program_id = ?",
                    (admission["program_id"],),
                ),
                (
                    "program_control",
                    "SELECT * FROM control.control_state "
                    "WHERE entity_type = 'program' AND entity_id = ?",
                    (admission["program_id"],),
                ),
                (
                    "phase",
                    "SELECT * FROM program_phases WHERE program_id = ? AND phase_id = ?",
                    (admission["program_id"], admission["phase_id"]),
                ),
                (
                    "execution",
                    "SELECT * FROM program_executions WHERE task_id = ?",
                    (admission["task_id"],),
                ),
            ):
                authority[key] = dict(self.store.connection.execute(query, parameters).fetchone())
            self._state(
                operation_id,
                row["state"],
                target,
                authority_sha256=self.store._put(_canonical(authority)),
                checkpoint_sha256=self.store._put(checkpoint),
            )
            return self.status(operation_id)

    def _record(self, row, admission, state, status):
        """Derive Program output from the actual checkpoint under the attached transaction."""
        store, program, phase, task = (
            self.store,
            admission["program_id"],
            admission["phase_id"],
            admission["task_id"],
        )
        # Each proven checkpoint has immutable result artifacts. A crash after a file write
        # but before the DB commit must leave the prior committed report intact.
        prefix = self._result_prefix(program, phase, task, state)
        result_ref = store.programs.artifacts.write_json(
            f"{prefix}/safe-result.json", state
        )
        store.connection.execute(
            """UPDATE program_executions SET status = ?, safe_status = ?,
            result_ref = ? WHERE task_id = ?""",
            (status, state["status"], result_ref.uri, task),
        )
        if status == "completed":
            result = PhaseResult(
                phase_id=phase,
                summary="Completed one admitted source-aware Safe unit.",
                changed_paths=tuple(state.get("actual_changed_paths", ())),
                tests=(f"{task}: {state['tests_ref']}",),
                reviewer_verdict="PASS",
                artifact_refs=tuple(
                    v for v in state.values() if isinstance(v, str) and v.startswith("artifact://")
                ),
            )
            result_artifact = store.programs.artifacts.write_json(
                f"{prefix}/phase-result.json", result.model_dump(mode="json")
            )
            summary_ref = store.programs.artifacts.write_text(
                f"{prefix}/phase-summary.md",
                store.programs._phase_summary(program, result),
                "text/markdown",
            )
            store.connection.execute(
                """UPDATE program_phases SET status = 'completed',
                result_ref = ?, summary_ref = ? WHERE program_id = ? AND phase_id = ?""",
                (result_artifact.uri, summary_ref.uri, program, phase),
            )
            remaining = store.connection.execute(
                """SELECT 1 FROM program_phases
                WHERE program_id = ? AND status != 'completed' LIMIT 1""",
                (program,),
            ).fetchone()
            if remaining is None:
                store.connection.execute(
                    "UPDATE programs SET status = 'completed' WHERE program_id = ?", (program,)
                )
                store.connection.execute(
                    """UPDATE control.control_state
                    SET state = 'completed', reason = '', revision = revision + 1
                    WHERE entity_type = 'program' AND entity_id = ?""",
                    (program,),
                )
        elif status == "failed":
            store.connection.execute(
                "UPDATE program_phases SET status = 'failed' WHERE program_id = ? AND phase_id = ?",
                (program, phase),
            )
            store.connection.execute(
                "UPDATE programs SET status = 'blocked' WHERE program_id = ?", (program,)
            )
        execution = dict(
            store.connection.execute(
                "SELECT * FROM program_executions WHERE task_id = ?", (task,)
            ).fetchone()
        )
        execution.pop("unit_key")
        binding = ProgramExecutionBinding.model_validate(
            {**execution, "slice_id": execution["slice_id"] or None}
        )
        phase_status = store.connection.execute(
            "SELECT status FROM program_phases WHERE program_id = ? AND phase_id = ?",
            (program, phase),
        ).fetchone()[0]
        program_status = store.connection.execute(
            "SELECT status FROM programs WHERE program_id = ?", (program,)
        ).fetchone()[0]
        report_ref = store.programs.artifacts.write_json(
            f"{prefix}/phase-execution-report.json",
            {
                "schema": "uca-program-source-execution-report-2",
                "program_id": program,
                "program_status": program_status,
                "requirement_hash": binding.requirement_hash,
                "phase_id": phase,
                "phase_status": phase_status,
                "admission_sha256": row["admission_sha256"],
                "cross_phase_source_handoff": status == "completed",
                "automatic_execution": False,
                "bindings": [binding.model_dump(mode="json")],
            },
        )
        store.connection.execute(
            "UPDATE program_executions SET phase_report_ref = ? WHERE task_id = ?",
            (report_ref.uri, task),
        )
        store.connection.execute(
            "UPDATE program_source_dispatches SET result_sha256 = ? WHERE operation_id = ?",
            (
                store._put(
                    _canonical(
                        {"result_sha256": result_ref.sha256, "report_sha256": report_ref.sha256}
                    )
                ),
                row["operation_id"],
            ),
        )

    def _capture_safe(self, row, admission, state):
        before = self.store.source.load_snapshot(
            self.store._get(admission["source_sha256"]), expected_sha256=admission["source_sha256"]
        )
        evidence = _capture_at_owned_destination(
            state=state,
            before=before,
            artifacts=self.store.safe.artifacts,
            repository_url=self.store.repository_url,
            policy=self.store.trusted_policy,
            attestor=self.store.attestor,
            sandbox=self.preparation.filesystem.root
            / ("execution-" + row["operation_id"])
            / "repo",
        )
        payload = strict_json(evidence.payload)
        payload.update(
            schema="uca-safe-source-evidence-2",
            admission_sha256=row["admission_sha256"],
            admission=admission,
            scope_decision=self._json(row["approval_sha256"]),
        )
        return replace(evidence, payload=_canonical(payload))

    def capture(self, task_id, owner_token, state):
        row = self.store.connection.execute(
            "SELECT operation_id FROM program_source_dispatches WHERE task_id = ?", (task_id,)
        ).fetchone()
        _require(row is not None, "v2 execution is missing")
        with self.store._transaction():
            row, admission, _ = self._load(row[0], owner_token)
            _require(row["state"] == "terminal", "v2 execution is not reconciled")
            self._verify_files(row, admission)
            _, actual, next_nodes = self._checkpoint(admission)
            _require(not next_nodes and actual == state, "v2 capture checkpoint differs")
            return self._capture_safe(row, admission, state)

    def acceptance_gate(self, task_id, owner_token, *, replay=False):
        row = self.store.connection.execute(
            "SELECT operation_id FROM program_source_dispatches WHERE task_id = ?", (task_id,)
        ).fetchone()
        _require(row is not None, "v2 execution is missing")
        row, admission, _ = self._load(row[0], owner_token, accepted_replay=replay)
        _require(row["state"] == "terminal", "v2 execution is not terminal")
        self._verify_files(row, admission)
