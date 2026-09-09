"""Explicit host-owned local Product commands. No scheduler or recovery adoption."""

from __future__ import annotations

import os
import re
from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path
from threading import Condition, RLock

from universal_coding_agent.core.models import RepositorySpec
from universal_coding_agent.core.safe_models import SafeModePolicy, SafeTaskRequest
from universal_coding_agent.product.local_product_binding import (
    LOCATOR,
    LocalProductBinding,
    check,
    read_locator,
    root_pin,
    write_locator,
)
from universal_coding_agent.product.local_product_command_store import (
    BINDINGS,
    DECISIONS,
    HEADS,
    PROGRAMS,
    QUOTES,
    REQUESTS,
    LocalProductParticipation,
    LocalProductStore,
    active,
)
from universal_coding_agent.product.program_continuation_dispatch import (
    ProgramContinuationDispatchService,
)
from universal_coding_agent.product.program_continuation_execution_store import (
    canonical,
    identity,
    sha,
)
from universal_coding_agent.product.program_execution_base import ProgramExecutionBaseService
from universal_coding_agent.product.program_source_acceptance import ProgramSourceAcceptanceService
from universal_coding_agent.product.program_source_acceptance_v2 import (
    ProgramSourceAcceptanceV2Service,
)
from universal_coding_agent.product.program_source_acceptance_v2_store import Reader
from universal_coding_agent.product.program_source_attestation import (
    ProgramGitSourceAttestationService,
)
from universal_coding_agent.product.program_source_evidence import strict_json
from universal_coding_agent.product.program_source_materialization import (
    ProgramSourceMaterializationService,
)
from universal_coding_agent.product.program_source_transitions import ProgramSourceIdentity
from universal_coding_agent.providers.base import (
    RemoteOperationLeaseAwareProvider,
    RestartReconciliationModelProvider,
)
from universal_coding_agent.safe.testing import SafeTestRunner
from universal_coding_agent.safe_service import SafeAgentService
from universal_coding_agent.safety.sanitizer import sanitize_text


class LocalProductHost:
    def __init__(self, workspace, binding):
        check(type(binding) is LocalProductBinding, "binding_changed")
        self.workspace, self.binding = workspace, binding
        self.config = binding.value
        self.programs, self.lifecycle = workspace.programs, workspace.lifecycle_reservations
        self.provider = workspace.provider
        check(
            not isinstance(
                self.provider,
                (RemoteOperationLeaseAwareProvider, RestartReconciliationModelProvider),
            ),
            "unsupported_transport",
        )
        check(
            SafeTestRunner.from_environment().adapter_module_path is None, "unsupported_transport"
        )
        self.safe_root = Path(self.config["safe_state_root"])
        self.policy = SafeModePolicy.model_validate(self.config["policy"])
        self.repository = RepositorySpec(
            url=self.config["origin_repository_url"], base_ref=self.config["origin_commit_sha"]
        )
        check(
            os.environ.get("UCA_SAFE_EDIT_PROTOCOL", "v1").strip().lower()
            == self.config["edit_protocol"],
            "binding_changed",
        )
        self.participants = {}
        self._condition = Condition(RLock())
        self._calls, self._closing = 0, False
        binding.preflight(self.programs.database_path)
        # Read independent locators before schema initialization; lost namespaces
        # cannot be silently recreated and adopted by another startup.
        self._prior_locators = [
            read_locator(path)
            for path in (self.programs.database_path.parent / LOCATOR, self.safe_root / LOCATOR)
        ]
        if any(self._prior_locators):
            check(
                self._prior_locators[0] is not None
                and self._prior_locators[0] == self._prior_locators[1],
                "binding_changed",
            )
            from universal_coding_agent.product.local_product_command_store import schema

            schema(self.programs.connection)
        self.safe_root.mkdir(parents=True, exist_ok=True)
        (self.safe_root / "sandboxes").mkdir(exist_ok=True)
        safe = SafeAgentService.create(
            self.safe_root,
            self.provider,
            allow_local_sources=True,
            control=workspace.control,
            remote_operations=workspace.remote_operations,
        )
        attestor = ProgramGitSourceAttestationService(
            Path(self.config["source_root"]), sha(self.config["origin_repository_url"].encode())
        )
        self.source = ProgramSourceAcceptanceService(
            programs=self.programs,
            lifecycle=self.lifecycle,
            safe=safe,
            attestor=attestor,
            repository_url=self.config["origin_repository_url"],
            trusted_policy=self.policy,
        )
        self.materialization = ProgramSourceMaterializationService(self.source)
        self.preparation = ProgramExecutionBaseService(self.materialization)
        self.continuation = ProgramContinuationDispatchService(
            self.preparation,
            self.provider,
            lifecycle=self.lifecycle,
            transport_id=self.config["transport_id"],
        )
        self.final = None
        self.commands_store = LocalProductStore(self)
        self._descriptor_raw = canonical(self.descriptor())
        self.binding_sha256 = sha(self._descriptor_raw)
        self.persist_binding()

    def descriptor(self):
        self.continuation._host_gate()
        check(self.workspace.provider is self.provider, "binding_changed")
        plans = []
        for item in self.config["programs"]:
            plan = self.programs.plan(item["program_id"])
            check(
                plan.canonical_hash() == item["plan_sha256"]
                and plan.requirement_hash == item["requirement_sha256"],
                "binding_changed",
            )
            check(
                len(plan.phases) == 2
                and all(not phase.slices for phase in plan.phases)
                and not plan.phases[0].dependencies
                and tuple(plan.phases[1].dependencies) == (plan.phases[0].phase_id,),
                "unsupported_program",
            )
            row = self.programs.connection.execute(
                "SELECT plan_hash,requirement_hash,plan_ref FROM programs WHERE program_id=?",
                (item["program_id"],),
            ).fetchone()
            check(
                row is not None
                and row[0] == item["plan_sha256"]
                and row[1] == item["requirement_sha256"],
                "binding_changed",
            )
            pairs = [
                self.programs._execution_ids(plan.program_id, phase.phase_id, None)
                for phase in plan.phases
            ]
            plans.append(
                {**item, "task_ids": [p[0] for p in pairs], "thread_ids": [p[1] for p in pairs]}
            )
        return {
            "schema": "uca-local-product-host-binding-1",
            "configuration": self.config,
            "programs": plans,
            "stores": self.continuation.db.identities,
            "roots": [
                root_pin(p)
                for p in (
                    Path(self.config["source_root"]),
                    self.safe_root,
                    Path(self.config["owned_execution_root"]),
                    self.programs.artifacts.root,
                    self.source.safe.artifacts.root,
                )
            ],
            "source_host_sha256": self.source.host_sha256,
            "git_host_sha256": self.source.attestor.host_binding_sha256,
            "git_policy_sha256": self.source.attestor.policy_sha256,
            "source_policy": asdict(self.source.source.policy),
            "provider_type": type(self.provider).__module__
            + "."
            + type(self.provider).__qualname__,
            "provider_capabilities": self.provider.capabilities().model_dump(mode="json"),
            "continuation_host_sha256": self.continuation.host_sha256,
            "publication_enabled": False,
        }

    def persist_binding(self):
        store, db = self.commands_store, self.source.connection
        descriptor = strict_json(self._descriptor_raw)
        locator = {
            "schema": "uca-local-product-root-1",
            "program_store": list(identity(self.programs.database_path)),
            "safe_root": root_pin(self.safe_root),
            "binding_sha256": self.binding_sha256,
            "programs": descriptor["programs"],
        }
        if any(self._prior_locators):
            check(self._prior_locators[0] == locator, "binding_changed")
        with store.transaction(initialize=True):
            old = db.execute(
                f"SELECT binding_sha256 FROM {BINDINGS} WHERE project_id=?",
                (self.config["project_id"],),
            ).fetchone()
            if old is not None:
                check(
                    old[0] == self.binding_sha256 and store.get(old[0]) == descriptor,
                    "binding_changed",
                )
                check(all(self._prior_locators), "binding_changed")
            else:
                check(not any(self._prior_locators), "binding_changed")
                for item in descriptor["programs"]:
                    check(
                        db.execute(
                            "SELECT 1 FROM program_source_heads WHERE program_id=?",
                            (item["program_id"],),
                        ).fetchone()
                        is None
                        and db.execute(
                            "SELECT 1 FROM program_executions WHERE program_id=?",
                            (item["program_id"],),
                        ).fetchone()
                        is None,
                        "binding_changed",
                    )
                    check(
                        self.programs.status(item["program_id"]).value == "running",
                        "unsupported_program",
                    )
                db.execute(
                    f"INSERT INTO {BINDINGS} VALUES (?,?)",
                    (self.config["project_id"], store.put(self._descriptor_raw)),
                )
                for item in descriptor["programs"]:
                    mapping = {
                        "schema": "uca-local-product-program-binding-1",
                        **item,
                        "project_id": self.config["project_id"],
                        "binding_sha256": self.binding_sha256,
                    }
                    db.execute(
                        f"INSERT INTO {PROGRAMS} VALUES (?,?,?,?)",
                        (
                            item["program_id"],
                            self.config["project_id"],
                            self.binding_sha256,
                            store.put(mapping),
                        ),
                    )
                    db.execute(
                        f"INSERT INTO {HEADS} VALUES (?,0,NULL,NULL,0)", (item["program_id"],)
                    )
        for path in (self.programs.database_path.parent / LOCATOR, self.safe_root / LOCATOR):
            write_locator(path, locator)
        self.locator = locator

    @contextmanager
    def call(self):
        with self._condition:
            check(not self._closing, "store_unavailable")
            self._calls += 1
        try:
            yield
        finally:
            with self._condition:
                self._calls -= 1
                self._condition.notify_all()

    def close(self):
        with self._condition:
            self._closing = True
            self._condition.wait_for(lambda: self._calls == 0)
        self.source.close()
        self.source.safe.close()

    def current_binding(self, payload):
        check(payload["project_id"] == self.config["project_id"], "project_not_found")
        check(
            payload["program_id"] in {p["program_id"] for p in self.config["programs"]},
            "program_not_bound",
        )
        check(
            payload["expected_binding_sha256"] == self.binding_sha256
            and canonical(self.descriptor()) == self._descriptor_raw,
            "binding_changed",
        )
        for path in (self.programs.database_path.parent / LOCATOR, self.safe_root / LOCATOR):
            check(read_locator(path) == self.locator, "binding_changed")

    def verify_origin(self, program):
        import time

        from universal_coding_agent.product.program_source_attestation import _GitBudget

        attestor = self.source.attestor
        origin = attestor.attest(self.identity(program))
        attestor.verify_retained_files(origin.snapshot.files)
        budget = _GitBudget(
            time.monotonic() + attestor.policy.operation_timeout_seconds,
            attestor.policy.max_git_output_bytes,
        )
        check(
            attestor._run(("rev-parse", "HEAD"), b"", budget).decode().strip()
            == self.config["origin_commit_sha"],
            "source_changed",
        )

    def final_controls(self, part):
        p = part.payload
        if p["action"] == "reconcile_outcome":
            return
        claim = part.store.get(part.claim_sha)
        baseline = claim["baseline"]
        current = self.semantic(part.key[0], p.get("task_id"))
        if p["action"] in {"start_first_phase", "decide_first_scope"}:
            current = self.semantic(part.key[0], part.driver.task_id)
            expected_task_revision = (p["task_control_revision"] or 0) + (
                1 if current["execution"]["status"] == "completed" else 0
            )
            check(
                current["task_control"]["revision"] == expected_task_revision
                and current["program_control"] == baseline["program_control"],
                "proposal_changed",
            )
            self.verify_origin(part.key[0])
        elif p["action"] != "decide_continuation_scope":
            check(current["program_control"] == baseline["program_control"], "proposal_changed")
            if "task_control" in baseline:
                check(current["task_control"] == baseline["task_control"], "proposal_changed")
        check(
            current["recovery_history_sha256"] == baseline["recovery_history_sha256"],
            "proposal_changed",
        )

    def task_ids(self, program):
        return tuple(
            r[0]
            for r in self.source.connection.execute(
                "SELECT task_id FROM program_executions WHERE program_id=? "
                "ORDER BY task_id LIMIT 101",
                (program,),
            )
        )

    def rows(self, table, where, args):
        alias, name = table.split(".") if "." in table else ("main", table)
        fields = tuple(
            r[1] for r in self.source.connection.execute(f"PRAGMA {alias}.table_info('{name}')")
        )
        check(fields and len(fields) <= 64, "recorded_evidence_invalid")
        return Reader(self.source.connection).rows(table, fields, where, args, limit=100)

    def semantic(self, program, task=None):
        programs = self.rows("programs", "program_id=?", (program,))
        controls = self.rows(
            "control.control_state", "entity_type='program' AND entity_id=?", (program,)
        )
        source = self.rows("program_source_heads", "program_id=?", (program,))
        history = self.rows(
            "lifecycle.lifecycle_recovery_receipts",
            "program_id=? OR task_id IN "
            "(SELECT task_id FROM program_executions WHERE program_id=?)",
            (program, program),
        )
        history.sort(key=lambda item: item["recovery_ref"])
        check(len(programs) == len(controls) == 1 and len(source) <= 1, "recorded_evidence_invalid")
        result = {
            "program": programs[0],
            "program_control": controls[0],
            "source": source[0] if source else None,
            "recovery_history_sha256": self.commands_store.put(history),
        }
        if task is not None:
            executions = self.rows(
                "program_executions", "program_id=? AND task_id=?", (program, task)
            )
            check(len(executions) == 1, "recorded_evidence_invalid")
            phases = self.rows(
                "program_phases",
                "program_id=? AND phase_id=?",
                (program, executions[0]["phase_id"]),
            )
            tasks = self.rows(
                "control.control_state", "entity_type='task' AND entity_id=?", (task,)
            )
            check(len(phases) == len(tasks) == 1, "recorded_evidence_invalid")
            result.update(execution=executions[0], phase=phases[0], task_control=tasks[0])
        return result

    def quiet(self, program):
        coordinator = self.source.safe.control.cancellation
        tasks = self.task_ids(program)
        check(len(tasks) <= 2, "unsupported_program")
        for task in tasks:
            check(not any(coordinator._registration_snapshot(task).values()), "recovery_required")
            context = coordinator._invocations.get(task)
            check(context is None or context.revoked, "recovery_required")
        db = self.source.connection
        check(
            db.execute(
                "SELECT 1 FROM remote.remote_operation_leases WHERE task_id IN "
                "(SELECT task_id FROM program_executions WHERE program_id=?) OR thread_id IN "
                "(SELECT thread_id FROM program_executions WHERE program_id=?) LIMIT 1",
                (program, program),
            ).fetchone()
            is None,
            "recovery_required",
        )
        check(
            db.execute(
                "SELECT 1 FROM remote.remote_operation_lease_retirements WHERE program_id=? "
                "OR task_id IN (SELECT task_id FROM program_executions WHERE program_id=?) LIMIT 1",
                (program, program),
            ).fetchone()
            is None,
            "recovery_required",
        )

    def identity(self, program):
        item = next(p for p in self.config["programs"] if p["program_id"] == program)
        return ProgramSourceIdentity(
            program,
            self.source.attestor.repository_sha256,
            item["requirement_sha256"],
            item["plan_sha256"],
            self.config["origin_commit_sha"],
            self.config["origin_tree_sha"],
        )

    def admission(self, payload):
        self.current_binding(payload)
        self.recorded_history(payload)
        db, program, action = self.source.connection, payload["program_id"], payload["action"]
        check(
            db.execute(
                f"SELECT 1 FROM {REQUESTS} WHERE program_id=? AND request_id=?",
                (program, payload["request_id"]),
            ).fetchone()
            is None,
            "request_conflict",
        )
        head = db.execute(
            f"SELECT revision,pending_request_id FROM {HEADS} WHERE program_id=?", (program,)
        ).fetchone()
        check(head is not None and head[0] == payload["expected_revision"], "revision_conflict")
        check(head[1] is None, "program_busy")
        semantic = self.semantic(program, payload.get("task_id"))
        check(
            semantic["program"]["requirement_hash"] == payload["requirement_sha256"]
            and semantic["program"]["plan_hash"] == payload["plan_sha256"],
            "binding_changed",
        )
        check(
            semantic["program_control"]["revision"] == payload["program_control_revision"]
            and semantic["program_control"]["state"] in {"running", "completed"},
            "proposal_changed",
        )
        if payload.get("task_id"):
            check(
                semantic["task_control"]["revision"] == payload["task_control_revision"],
                "proposal_changed",
            )
        elif action == "start_continuation":
            task = self.programs._execution_ids(
                program, self.programs.plan(program).phases[0].phase_id, None
            )[0]
            control = self.rows(
                "control.control_state", "entity_type='task' AND entity_id=?", (task,)
            )
            check(
                len(control) == 1 and control[0]["revision"] == payload["task_control_revision"],
                "proposal_changed",
            )
        if action == "initialize_source":
            check(semantic["source"] is None and not self.task_ids(program), "source_changed")
            check(
                payload["origin_commit_sha"] == self.config["origin_commit_sha"]
                and payload["origin_tree_sha"] == self.config["origin_tree_sha"],
                "source_changed",
            )
        else:
            check(semantic["source"] is not None, "source_changed")
            if "before_sha256" in payload:
                check(
                    semantic["source"]["source_sha256"] == payload["before_sha256"]
                    and semantic["source"]["generation"] == payload["generation"],
                    "source_changed",
                )
        if action == "start_first_phase":
            check(not self.task_ids(program), "program_busy")
        elif action == "decide_first_scope":
            from universal_coding_agent.product.local_product_first_phase import (
                capture_first_boundary,
            )

            state, checkpoint, _, witness = capture_first_boundary(self, program)
            proposal = self.commands_store.get(payload["scope_proposal_sha256"])
            self.completed_link(program, "first_scope_proposal", payload["scope_proposal_sha256"])
            check(
                proposal["checkpoint_sha256"] == payload["checkpoint_sha256"] == sha(checkpoint)
                and proposal["scope_sha256"] == payload["scope_sha256"] == state["scope_hash"],
                "proposal_changed",
            )
            check(
                all(
                    proposal[name + "_row_sha256"] == sha(canonical(witness[name]))
                    for name in ("program", "phase", "execution", "program_control", "task_control")
                )
                and proposal["recovery_history_sha256"] == witness["recovery_history_sha256"],
                "proposal_changed",
            )
        elif action == "preview_first_source":
            check(semantic["execution"]["status"] == "completed", "recorded_evidence_invalid")
            check(
                db.execute(
                    f"SELECT 1 FROM {QUOTES} WHERE program_id=? AND task_id=?",
                    (program, payload["task_id"]),
                ).fetchone()
                is None,
                "source_decision_final",
            )
            check(
                self.first_result(program, terminal=True)["result_sha256"]
                == payload["result_sha256"],
                "proposal_changed",
            )
        elif action == "decide_first_source":
            self.reviewed_first_quote(payload)
            check(
                not self.completed_kind(program, "first_source_decision"), "source_decision_final"
            )
        elif action == "start_continuation":
            check(
                len(self.task_ids(program)) == 1
                and semantic["source"]["receipt_sha256"] == payload["acceptance_receipt_sha256"],
                "source_changed",
            )
        elif action == "decide_final_source":
            previews = self.completed_kind(program, "final_source_preview")
            check(
                len(previews) == 1
                and previews[0]["candidate_sha256"] == payload["candidate_sha256"]
                and previews[0]["evidence_view_sha256"] == payload["evidence_view_sha256"],
                "proposal_changed",
            )
        self.quiet(program)
        return semantic, self.task_ids(program)

    def recorded_history(self, payload):
        from universal_coding_agent.product.local_product_status import ProductReader
        from universal_coding_agent.product.program_continuation_execution_store import (
            composed_read_budget,
        )

        with composed_read_budget():
            reader = ProductReader(self.source.connection)
            reader.locator = self.locator
            reader.all_requests(payload["project_id"], payload["program_id"])
        return reader

    def completed_kind(self, program, kind):
        rows = self.source.connection.execute(
            f"SELECT d.record_sha256,r.state FROM {DECISIONS} d "
            f"JOIN {REQUESTS} r USING(program_id,request_id) WHERE d.program_id=? AND d.kind=? "
            "ORDER BY r.sequence,d.sequence LIMIT 101",
            (program, kind),
        ).fetchall()
        check(len(rows) <= 100, "recorded_evidence_invalid")
        result = []
        for row in rows:
            check(row[1] == "completed", "recovery_required")
            link = self.commands_store.get(row[0])
            result.append(self.commands_store.get(link["value_sha256"]))
        return result

    def completed_link(self, program, kind, value_sha):
        check(
            any(sha(canonical(value)) == value_sha for value in self.completed_kind(program, kind)),
            "recorded_evidence_invalid",
        )

    def first_result(self, program, *, terminal):
        values = [
            r
            for r in self.completed_kind(program, "first_result")
            if (r["execution_status"] == "completed") == terminal
        ]
        check(len(values) == 1, "recorded_evidence_invalid")
        return values[0]

    def reviewed_first_quote(self, payload):
        quote = self.commands_store.get(payload["quote_sha256"])
        self.completed_link(payload["program_id"], "first_source_quote", payload["quote_sha256"])
        core = self.commands_store.get(quote["core_sha256"])
        check(
            quote["schema"] == "uca-local-first-source-quote-1"
            and quote["program_id"] == payload["program_id"]
            and quote["task_id"] == payload["task_id"]
            and quote["quote_revision"] == payload["quote_revision"]
            and quote["core_sha256"] == payload["core_sha256"]
            and quote["evidence_view_sha256"] == payload["evidence_view_sha256"]
            and core["initialization_receipt_sha256"] == payload["predecessor_receipt_sha256"]
            and all(
                core[k] == payload[k] for k in ("transition_sha256", "before_sha256", "generation")
            ),
            "proposal_changed",
        )
        return quote, core

    def tests_summary(self, state):
        if not state.get("tests_ref"):
            return None
        raw = self.source.safe.artifacts._read_bytes_bounded(
            state["tests_ref"], max_bytes=2_000_000
        )
        check(sha(raw) == state["tests_sha256"], "recorded_evidence_invalid")
        tests = strict_json(raw)
        profiles = [
            {
                "profile_id": item["profile_id"],
                "passed": item["passed"],
                "exit_code": item["returncode"],
            }
            for item in tests["results"]
        ]
        return {
            "profiles": profiles,
            "all_required_passed": all(item["passed"] for item in profiles),
        }

    def evidence_view(self, state, kind, *, core_sha256=None, source_evidence_sha256):
        task = SafeTaskRequest.model_validate(state["task"])
        chunks = []

        def add(kind, text, path=None):
            check(type(text) is str, "evidence_view_unavailable")
            check(
                sanitize_text(text) == text
                and not re.search(
                    r"(?:Bearer\s+\S+|sk-[A-Za-z0-9]{12,}|AKIA[A-Z0-9]{16}|"
                    r"-----BEGIN .*PRIVATE KEY)",
                    text,
                ),
                "evidence_view_unavailable",
            )
            for private in (
                self.config["source_root"],
                str(self.workspace.root),
                str(self.safe_root),
            ):
                check(private not in text, "evidence_view_unavailable")
            # Validate the entire material before splitting at UTF-8 boundaries.
            while text:
                end = min(len(text), 65_536)
                while len(text[:end].encode()) > 65_536:
                    end //= 2
                chunks.append(
                    {"index": len(chunks), "relative_path": path, "kind": kind, "text": text[:end]}
                )
                text = text[end:]

        if kind == "scope":
            for change in task.manifest.allowed_changes:
                add("scope", canonical(change.model_dump(mode="json")).decode(), change.path)
            add(
                "scope",
                canonical(
                    {
                        "acceptance_criteria": task.manifest.acceptance_criteria,
                        "test_profiles": task.manifest.test_profiles,
                    }
                ).decode(),
            )
        else:
            patch = self.source.safe.artifacts._read_bytes_bounded(
                state["patch_ref"], max_bytes=1_000_000
            )
            add("diff", patch.decode("utf-8"))
            add("tests", canonical(self.tests_summary(state)).decode())
            review_raw = self.source.safe.artifacts._read_bytes_bounded(
                state["review_ref"], max_bytes=65_536
            )
            check(sha(review_raw) == state["review_sha256"], "recorded_evidence_invalid")
            review = strict_json(review_raw)
            add(
                "review",
                canonical(
                    {k: review[k] for k in ("verdict", "required_actions", "confidence")}
                ).decode(),
            )
        view = {
            "schema": "uca-local-product-evidence-view-1",
            "view_kind": kind,
            "program_id": task.metadata.get("local_product_program_id")
            or self.programs.execution_binding(task.task_id).program_id,
            "task_id": task.task_id,
            "core_sha256": core_sha256,
            "source_evidence_sha256": source_evidence_sha256,
            "chunks": chunks,
            "redacted": False,
            "complete": True,
        }
        raw = canonical(view)
        check(len(raw) <= 1_048_576, "evidence_view_unavailable")
        return self.commands_store.put(raw)

    def validate_first_terminal(self, state, binding):
        part = active(self.source.connection)
        check(
            part is not None and state.get("scope_approved") is part.payload.get("approved"),
            "proposal_changed",
        )
        task = binding["task_id"]
        check(
            state.get("final_report_ref") == f"artifact://tasks/{task}/safe-final-report.json",
            "recorded_evidence_invalid",
        )
        raw = self.source.safe.artifacts._read_bytes_bounded(
            state["final_report_ref"], max_bytes=2_000_000
        )
        report = strict_json(raw)
        check(
            report["task_id"] == task
            and report["thread_id"] == binding["thread_id"]
            and all(
                report.get(k) == state.get(k)
                for k in (
                    "status",
                    "scope_hash",
                    "scope_approved",
                    "rolled_back",
                    "rollback_ref",
                    "tests_ref",
                    "tests_sha256",
                    "review_ref",
                    "review_sha256",
                    "reviewer_verdict",
                )
            ),
            "recorded_evidence_invalid",
        )
        self.commands_store.put(raw)
        check(
            not state.get("patch_applied")
            or state["status"] == "completed"
            or state.get("rolled_back") is True,
            "recovery_required",
        )
        # Completion's actual full v1 capture is performed after the outer seal,
        # in the separately requested source preview. This driver never accepts.
        if state["status"] == "completed":
            check(
                state.get("reviewer_verdict") == "PASS"
                and self.tests_summary(state)["all_required_passed"],
                "recorded_evidence_invalid",
            )
        else:
            head = self.source._head(binding["program_id"])
            before = self.source.source.load_snapshot(
                self.source._get(head["source_sha256"]), expected_sha256=head["source_sha256"]
            )
            execution = ProgramGitSourceAttestationService(
                Path(state["sandbox_path"]),
                self.source.attestor.repository_sha256,
                source_policy=self.source.source.policy,
                git_policy=self.source.attestor.policy,
            )
            execution.verify_retained_files(before.files)

    def execute(self, payload):
        from universal_coding_agent.product.local_product_status import request_result

        with self.call():
            historical = request_result(self.programs.database_path, payload)
            if historical is not None:
                return historical
            part = LocalProductParticipation(self, payload)
            with self._condition:
                check(part.key not in self.participants, "program_busy")
                self.participants[part.key] = part
            with part.activate():
                action = payload["action"]
                if action == "reconcile_outcome":
                    return self.reconcile(part)
                if action not in {
                    "decide_continuation_scope",
                    "preview_final_source",
                    "decide_final_source",
                }:
                    with self.commands_store.transaction(participant=part):
                        part.claim()
                if action == "initialize_source":
                    self.source.initialize(
                        self.identity(part.key[0]), owner_token=part.owner_token, participation=part
                    )
                elif action in {"start_first_phase", "decide_first_scope"}:
                    from universal_coding_agent.product.local_product_first_phase import (
                        LocalFirstPhaseDriver,
                    )

                    part.driver = LocalFirstPhaseDriver(part)
                    part.driver.drive()
                elif action in {"preview_first_source", "decide_first_source"}:
                    from universal_coding_agent.product.local_product_first_source import (
                        LocalFirstSource,
                    )

                    LocalFirstSource(self).run(part)
                elif action == "start_continuation":
                    self.start_continuation(part)
                elif action == "decide_continuation_scope":
                    self.continuation.approve_scope(
                        part.key[0],
                        payload["operation_id"],
                        request_id=part.child_id,
                        **{
                            k: payload[k]
                            for k in (
                                "admission_sha256",
                                "expected_epoch",
                                "expected_receipt_sha256",
                                "proposal_sha256",
                                "scope_sha256",
                                "approval_id",
                                "approved",
                            )
                        },
                    )
                else:
                    self.final_command(part)
                check(part.response is not None, "recovery_required")
                return 200, part.response

    def start_continuation(self, part):
        material = self.materialization.begin(
            part.key[0],
            owner_token=part.owner_token,
            acceptance_receipt_sha256=part.payload["acceptance_receipt_sha256"],
        )
        with self.commands_store.transaction(participant=part):
            part.link("materialization", {"operation_id": material["operation_id"]})
        material_receipt = self.materialization.reconcile(
            material["operation_id"], owner_token=part.owner_token
        )
        base = self.preparation.begin(material["operation_id"], owner_token=part.owner_token)
        with self.commands_store.transaction(participant=part):
            part.link(
                "preparation",
                {
                    "operation_id": base["operation_id"],
                    "materialization_receipt_sha256": self.commands_store.put(material_receipt),
                },
            )
        receipt = self.preparation.reconcile(base["operation_id"], owner_token=part.owner_token)
        with self.commands_store.transaction(participant=part):
            part.link(
                "prepared_base",
                {
                    "operation_id": base["operation_id"],
                    "receipt_sha256": self.commands_store.put(receipt),
                },
            )
        admitted = self.continuation.admit(
            part.key[0],
            base["operation_id"],
            request_id=part.child_id + "-admit",
            preparation_receipt_sha256=sha(canonical(receipt)),
            owner_token=part.owner_token,
        )
        self.continuation.dispatch(
            part.key[0],
            base["operation_id"],
            request_id=part.child_id,
            admission_sha256=admitted["admission_sha256"],
            expected_epoch=admitted["epoch"],
            expected_receipt_sha256=admitted["receipt_sha256"],
            owner_token=part.owner_token,
        )

    def final_command(self, part):
        from universal_coding_agent.product.local_product_status import read_session
        from universal_coding_agent.product.program_source_terminal_proof import terminal_history

        # Reject premature input before a final-service constructor can establish
        # its versioned tables. This is recorded proof, not current acceptance.
        with read_session(self.programs.database_path) as reader:
            reader.all_requests(part.payload["project_id"], part.key[0])
            terminal, _, _, _ = terminal_history(reader, part.key[0], part.payload["operation_id"])
            check(
                terminal["receipt_sha256"] == part.payload["terminal_receipt_sha256"]
                and terminal["task_id"] == part.payload["task_id"],
                "proposal_changed",
            )
        if self.final is None:
            self.final = ProgramSourceAcceptanceV2Service(self.continuation)
        p = part.payload
        if p["action"] == "preview_final_source":
            return self.final.preview_source_transition(
                part.key[0],
                p["operation_id"],
                request_id=part.child_id,
                terminal_receipt_sha256=p["terminal_receipt_sha256"],
                before_sha256=p["before_sha256"],
                generation=1,
            )
        return self.final.decide_source_transition(
            part.key[0],
            p["operation_id"],
            request_id=part.child_id,
            **{
                k: p[k]
                for k in (
                    "candidate_sha256",
                    "revision",
                    "core_sha256",
                    "transition_sha256",
                    "before_sha256",
                    "generation",
                    "predecessor_receipt_sha256",
                    "terminal_receipt_sha256",
                    "approval_id",
                    "approved",
                )
            },
        )

    def continuation_completed(self, part, lower_payload, response):
        check(
            part.payload["action"] in {"start_continuation", "decide_continuation_scope"}
            and response["program_id"] == part.key[0]
            and response["request_id"] in {part.child_id, part.child_id + "-admit"},
            "recovery_required",
        )
        if response["state"] == "admitted":
            part.link(
                "admission",
                {
                    "payload_sha256": self.commands_store.put(lower_payload),
                    "response_sha256": self.commands_store.put(response),
                },
            )
            return
        row = self.continuation._row(response["operation_id"])
        admission = self.continuation._admission(row)
        adapter = self.continuation._live.get(response["operation_id"])
        check(adapter is not None and adapter.owner_token == part.owner_token, "recovery_required")
        adapter._returned_proof()
        state = adapter._result_state()
        parked = response["state"] == "parked_scope"
        check(parked or response["state"] == "closed", "recovery_required")
        result = {
            "operation_id": row["operation_id"],
            "phase_id": row["phase_id"],
            "task_id": row["task_id"],
            "thread_id": row["thread_id"],
            "admission_sha256": response["admission_sha256"],
            "epoch": response["epoch"],
            "v3_receipt_sha256": response["receipt_sha256"],
            "proposal_sha256": response["proposal_sha256"],
            "scope_sha256": response["scope_sha256"],
            "result_sha256": response["result_sha256"],
            "execution_status": "awaiting_scope_approval"
            if parked
            else ("completed" if response["terminal_status"] == "completed" else "failed"),
        }
        if parked:
            result["evidence_view_sha256"] = self.evidence_view(
                state, "scope", source_evidence_sha256=response["receipt_sha256"]
            )
        execution_row = self.source.connection.execute(
            "SELECT result_ref,phase_report_ref FROM program_executions WHERE task_id=?",
            (row["task_id"],),
        ).fetchone()
        part.link(
            "continuation",
            {
                "schema": "uca-local-product-continuation-link-1",
                "operation_id": row["operation_id"],
                "admission_sha256": row["admission_sha256"],
                "payload_sha256": self.commands_store.put(lower_payload),
                "response_sha256": self.commands_store.put(response),
                "source_sha256": admission["source_sha256"],
                "checkpoint_sha256": row["checkpoint_sha256"],
                "task_sha256": row["task_sha256"],
                "discovery_sha256": row["discovery_sha256"],
                "filesystem_sha256": row["filesystem_sha256"],
                "retained_sha256": row["retained_sha256"],
                "result_sha256": self.commands_store.put(
                    self.programs.artifacts._read_bytes_bounded(
                        execution_row[0], max_bytes=8_000_000
                    )
                ),
                "report_sha256": self.commands_store.put(
                    self.programs.artifacts._read_bytes_bounded(
                        execution_row[1], max_bytes=2_000_000
                    )
                ),
            },
        )
        outcome = (
            "scope_required"
            if parked
            else (
                "terminal_unaccepted"
                if response["terminal_status"] == "completed"
                else ("rejected" if part.payload.get("approved") is False else "failed")
            )
        )
        part.finish(outcome, result, lower=response, released=True)

    def final_completed(self, part, response):
        payload, candidate = part.payload, response["candidate"]
        check(
            payload["action"] in {"preview_final_source", "decide_final_source"}
            and response["program_id"] == part.key[0]
            and response["request_id"] == part.child_id
            and candidate["task_id"] == payload["task_id"],
            "recovery_required",
        )
        if payload["action"] == "preview_final_source":
            row = self.continuation._row(payload["operation_id"])
            _, state, boundary = self.continuation._checkpoint(
                row, self.continuation._admission(row)
            )
            check(boundary == "terminal", "recorded_evidence_invalid")
            core = self.commands_store.get(candidate["core_sha256"])
            view_sha = self.evidence_view(
                state,
                "source",
                core_sha256=candidate["core_sha256"],
                source_evidence_sha256=core["evidence_sha256"],
            )
            part.link(
                "final_source_preview",
                {
                    "schema": "uca-local-final-source-preview-1",
                    "candidate_sha256": response["candidate_sha256"],
                    "evidence_view_sha256": view_sha,
                    "response_sha256": self.commands_store.put(response),
                },
            )
            result = {
                **{
                    k: candidate[k]
                    for k in (
                        "operation_id",
                        "task_id",
                        "revision",
                        "core_sha256",
                        "transition_sha256",
                        "before_sha256",
                        "after_sha256",
                        "generation",
                        "predecessor_receipt_sha256",
                        "terminal_receipt_sha256",
                    )
                },
                "candidate_sha256": response["candidate_sha256"],
                "evidence_view_sha256": view_sha,
            }
            outcome = "source_preview_recorded"
        else:
            check(response["status"] in {"accepted", "rejected"}, "recorded_evidence_invalid")
            part.link(
                "final_source_decision",
                {
                    "schema": "uca-local-final-source-decision-1",
                    "candidate_sha256": response["candidate_sha256"],
                    "approved": payload["approved"],
                    "response_sha256": self.commands_store.put(response),
                },
            )
            result = {
                "operation_id": candidate["operation_id"],
                "task_id": candidate["task_id"],
                "candidate_sha256": response["candidate_sha256"],
                "approved": payload["approved"],
                "source_receipt_sha256": response["receipt_sha256"],
                "generation": 2 if payload["approved"] else 1,
                "source_sha256": candidate["after_sha256"]
                if payload["approved"]
                else candidate["before_sha256"],
            }
            outcome = "source_accepted" if payload["approved"] else "rejected"
        part.finish(outcome, result, lower=response, released=True)

    def reconcile(self, observer):
        from universal_coding_agent.product.local_product_status import (
            read_session,
            recorded_request,
        )

        payload = observer.payload
        with read_session(self.programs.database_path) as reader:
            reader.all_requests(payload["project_id"], payload["program_id"])
            target = reader.records.get(payload["target_request_id"])
            check(target is not None, "request_not_found")
        with self.commands_store.transaction(participant=observer):
            observer.claim_observation(target)
        row = target["row"]
        disposition = "historical_completed"
        if row["state"] == "pending":
            disposition = "unsupported_target"
            if row["action"] in {"start_continuation", "decide_continuation_scope"}:
                disposition = "original_live_evidence_missing"
                original = self.participants.get(
                    (payload["program_id"], payload["target_request_id"])
                )
                if original is not None:
                    adapters = [
                        a
                        for a in self.continuation._live.values()
                        if a.payload["request_id"] == original.child_id
                    ]
                    if len(adapters) == 1 and adapters[0].operation_id == payload["operation_id"]:
                        try:
                            adapters[0]._returned_proof()
                            with original.reconcile_context(observer):
                                self.continuation.reconcile(
                                    payload["program_id"],
                                    adapters[0].operation_id,
                                    request_id=original.child_id,
                                )
                            return recorded_request(
                                self.programs.database_path,
                                payload["project_id"],
                                payload["program_id"],
                                payload["request_id"],
                            )
                        except Exception:
                            disposition = "proof_invalid"
                            observed = recorded_request(
                                self.programs.database_path,
                                payload["project_id"],
                                payload["program_id"],
                                payload["request_id"],
                            )
                            if observed[0] == 200:
                                return observed
        with self.commands_store.transaction(participant=observer):
            observer.finish_observation(
                disposition, row["request_id"], row["state"], row["response_sha256"]
            )
        return 200, observer.response
