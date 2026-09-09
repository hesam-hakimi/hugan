"""Finite first-phase Program/Discovered Safe driver with a real outer return.

This is independent of c2 and v3 execution adapters. A stored result, a caller
boolean, or a new process cannot reconstruct this driver's returned state.
"""

from __future__ import annotations

import base64
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import replace
from threading import RLock

from universal_coding_agent.core.cancellation import OwnedOperationKind
from universal_coding_agent.core.safe_models import SafeTaskRequest
from universal_coding_agent.product.local_product_binding import check
from universal_coding_agent.product.local_product_command_store import active
from universal_coding_agent.product.program_continuation_execution_store import (
    canonical,
    locked,
    sha,
)
from universal_coding_agent.product.program_orchestrator import _JSON_VALUE_ADAPTER
from universal_coding_agent.product.program_source_evidence import strict_json
from universal_coding_agent.providers.base import CancellableModelProvider

_DRIVER = ContextVar("uca_local_first_phase_driver", default=None)


def current_driver():
    driver = _DRIVER.get()
    if driver is not None:
        check(
            type(driver) is LocalFirstPhaseDriver
            and active(driver.part.store.connection) is driver.part
            and driver.part.driver is driver,
            "recovery_required",
        )
    return driver


class _Provider:
    def __init__(self, driver):
        self.driver = driver

    def capabilities(self):
        return self.driver.host.provider.capabilities()

    def probe(self):
        with self.driver.callback():
            return self.driver.host.provider.probe()

    def invoke(self, request):
        driver = self.driver
        with driver.callback(), driver.coordinator._invocation_context(driver.context):
            signal = driver.coordinator.signal(driver.task_id)
            with signal.operation(OwnedOperationKind.PROVIDER):
                provider = driver.host.provider
                if isinstance(provider, CancellableModelProvider):
                    return provider.invoke_cancellable(request, signal)
                return provider.invoke(request)

    def invoke_cancellable(self, request, cancellation):
        check(
            cancellation._coordinator is self.driver.coordinator
            and cancellation.task_id == self.driver.task_id,
            "recovery_required",
        )
        return self.invoke(request)


class LocalFirstPhaseDriver:
    def __init__(self, part):
        self.part, self.host = part, part.host
        self.program_id = part.key[0]
        self.phase = self.host.programs.plan(self.program_id).phases[0]
        self.task_id, self.thread_id = self.host.programs._execution_ids(
            self.program_id, self.phase.phase_id, None
        )
        self.coordinator = self.host.source.safe.control.cancellation
        self.context = None
        self.running = self.returned = self.revoked = False
        self.callbacks = 0
        self.lock = RLock()
        self.actual_result = self.outer_result = None
        self.provider = _Provider(self)
        self.executor = None

    def __repr__(self):
        return "LocalFirstPhaseDriver(private finite invocation)"

    @contextmanager
    def callback(self):
        with locked(self.lock):
            check(
                current_driver() is self and self.running and not self.revoked, "recovery_required"
            )
            self.callbacks += 1
        try:
            yield
        finally:
            with locked(self.lock):
                self.callbacks -= 1

    def gate(self, thread_id, task_id=None, action="run"):
        check(
            current_driver() is self
            and self.running
            and not self.revoked
            and thread_id == self.thread_id
            and task_id in {None, self.task_id}
            and action
            == ("run" if self.part.payload["action"] == "start_first_phase" else "resume"),
            "recovery_required",
        )
        self.host.verify_origin(self.program_id)
        with self.part.store.transaction():
            self.host.current_binding(self.part.payload)
            self.host.lifecycle.check_program_worker_in_transaction(
                self.part.store.connection,
                self.program_id,
                task_ids=self.host.task_ids(self.program_id),
                owner_token=self.part.owner_token,
            )
            claim = self.part.store.get(self.part.claim_sha)
            semantic = self.host.semantic(self.program_id)
            check(
                semantic["program_control"] == claim["baseline"]["program_control"]
                and semantic["recovery_history_sha256"]
                == claim["baseline"]["recovery_history_sha256"],
                "proposal_changed",
            )

    def bind_services(self, services, root, protocol):
        check(
            root == self.host.safe_root
            and protocol == self.host.config["edit_protocol"]
            and services.provider is self.provider
            and services.cancellation is self.coordinator,
            "binding_changed",
        )
        return replace(services, execution_boundary=self)

    def node(self, name, state, action):
        with self.callback():
            self.gate(
                self.thread_id,
                self.task_id,
                "run" if self.part.payload["action"] == "start_first_phase" else "resume",
            )
            task = SafeTaskRequest.model_validate(state["task"])
            check(
                task.task_id == self.task_id
                and task.thread_id == self.thread_id
                and task.metadata.get("local_product_binding_sha256") == self.host.binding_sha256
                and task.policy == self.host.policy
                and task.repository == self.host.repository
                and not task.require_publish_approval,
                "binding_changed",
            )
            result = action(state)
            self.host.verify_origin(self.program_id)
            return result

    def discovery_completed(self, task):
        check(
            self.part.payload["action"] == "start_first_phase"
            and task.task_id == self.task_id
            and task.thread_id == self.thread_id
            and task.manifest.base_sha == self.host.config["origin_commit_sha"]
            and not task.context_evidence,
            "source_changed",
        )
        return task.model_copy(
            update={
                "metadata": {
                    **task.metadata,
                    "local_product_binding_sha256": self.host.binding_sha256,
                    "local_product_program_id": self.program_id,
                }
            }
        )

    def start(self, **kwargs):
        with self.callback():
            self.actual_result = self.executor.start(**kwargs)
            return self.actual_result

    def resume(self, thread_id, approved):
        check(
            type(approved) is bool and approved is self.part.payload["approved"], "invalid_command"
        )
        with self.callback():
            self.actual_result = self.executor.resume(thread_id, approved)
            return self.actual_result

    def drive(self):
        check(
            not self.running
            and not self.returned
            and not self.revoked
            and self.context is None
            and self.part.driver is self,
            "recovery_required",
        )
        self.context = self.coordinator._new_invocation(self.task_id)
        self.running = True
        token = _DRIVER.set(self)
        try:
            # Keep the actual ProductWorkspace factory and Program consumer.
            self.executor = replace(
                self.host.workspace.discovered_safe(
                    state_root=self.host.safe_root, allow_local_sources=True
                ),
                provider=self.provider,
            )
            with self.coordinator._invocation_context(self.context):
                if self.part.payload["action"] == "start_first_phase":
                    result = self.host.programs.start_next_execution(
                        program_id=self.program_id,
                        current_requirement_hash=self.part.payload["requirement_sha256"],
                        repository=self.host.repository,
                        policy=self.host.policy,
                        test_profiles=tuple(self.host.policy.profile_map()),
                        executor=self,
                    )
                else:
                    result = self.host.programs.continue_execution(
                        program_id=self.program_id,
                        task_id=self.task_id,
                        current_requirement_hash=self.part.payload["requirement_sha256"],
                        executor=self,
                        approved=self.part.payload["approved"],
                    )
            with locked(self.lock):
                self.outer_result, self.returned = result, True
            self.part.store.boundary("first_outer_returned")
        finally:
            with locked(self.lock):
                self.running, self.revoked = False, True
            self.coordinator._revoke_invocation(self.context)
            _DRIVER.reset(token)
        from universal_coding_agent.product.program_source_capture_budget import CaptureBudget

        # Capture begins after mutable Program/Safe work actually returned.
        # Its earlier checkpoint/report preimages are retained in prior receipts.
        self.part.capture_budget = CaptureBudget()
        with self.part.capture_budget.activate():
            return self.seal()

    def returned_proof(self):
        with locked(self.lock):
            check(
                self.returned
                and self.revoked
                and not self.running
                and self.callbacks == 0
                and self.context is not None
                and self.context.revoked
                and self.actual_result is not None
                and self.outer_result is not None,
                "recovery_required",
            )

    def seal(self):
        self.returned_proof()
        # Host locks precede the bounded registration barrier, as in PR28.
        with self.part.store.transaction(
            participant=self.part, barrier=self.coordinator._settlement_barrier(self.context)
        ):
            self.returned_proof()
            self.host.quiet(self.program_id)
            captured = capture_first_boundary(self.host, self.program_id)
            state, checkpoint, binding, witness = captured
            check(binding == self.outer_result.model_dump(mode="json"), "recorded_evidence_invalid")
            expected = _JSON_VALUE_ADAPTER.dump_python(self.actual_result, mode="json")
            result_raw = self.host.programs.artifacts._read_bytes_bounded(
                binding["result_ref"], max_bytes=8_000_000
            )
            check(strict_json(result_raw) == expected, "recorded_evidence_invalid")
            result_sha = self.part.store.put(result_raw)
            checkpoint_sha = self.part.store.put(checkpoint)
            witness_sha = self.part.store.put(witness)
            claim = self.part.store.get(self.part.claim_sha)
            first_receipt = {
                "schema": "uca-local-first-result-receipt-1",
                "program_id": self.program_id,
                "task_id": self.task_id,
                "request_sha256": claim["payload_sha256"],
                "result_sha256": result_sha,
                "checkpoint_sha256": checkpoint_sha,
                "witness_sha256": witness_sha,
                "released_owner_sha256": claim["owner_sha256"],
                "execution_status": binding["status"],
            }
            first_sha = self.part.store.put(first_receipt)
            self.part.link("first_result", first_receipt)
            scope = state["scope_hash"]
            result = {
                "phase_id": self.phase.phase_id,
                "task_id": self.task_id,
                "thread_id": self.thread_id,
                "execution_status": binding["status"],
                "scope_sha256": scope,
                "checkpoint_sha256": checkpoint_sha,
                "result_sha256": result_sha,
                "reviewer_verdict": state.get("reviewer_verdict"),
                "tests_summary": self.host.tests_summary(state),
            }
            if binding["status"] == "awaiting_scope_approval":
                check(self.part.payload["action"] == "start_first_phase", "recovery_required")
                proposal = {
                    "schema": "uca-local-first-scope-proposal-1",
                    "project_id": self.part.payload["project_id"],
                    "program_id": self.program_id,
                    "task_id": self.task_id,
                    "thread_id": self.thread_id,
                    "phase_id": self.phase.phase_id,
                    "binding_sha256": self.host.binding_sha256,
                    "plan_sha256": self.part.payload["plan_sha256"],
                    "requirement_sha256": self.part.payload["requirement_sha256"],
                    "checkpoint_sha256": checkpoint_sha,
                    "scope_sha256": scope,
                    "before_sha256": witness["source"]["source_sha256"],
                    "initialization_receipt_sha256": witness["source"]["initial_receipt_sha256"],
                    "recovery_history_sha256": witness["recovery_history_sha256"],
                    "first_result_receipt_sha256": first_sha,
                    **{
                        name + "_row_sha256": sha(canonical(witness[name]))
                        for name in (
                            "program",
                            "phase",
                            "execution",
                            "program_control",
                            "task_control",
                        )
                    },
                }
                result["scope_proposal_sha256"] = self.part.store.put(proposal)
                self.part.link("first_scope_proposal", proposal)
                result["evidence_view_sha256"] = self.host.evidence_view(
                    state, "scope", source_evidence_sha256=first_sha
                )
                outcome = "scope_required"
            else:
                check(
                    binding["status"] in {"completed", "failed", "cancelled"}, "recovery_required"
                )
                outcome = (
                    "terminal_unaccepted"
                    if binding["status"] == "completed"
                    else ("rejected" if self.part.payload.get("approved") is False else "failed")
                )
            self.part.finish(outcome, result)
            self.returned_proof()
            self.host.quiet(self.program_id)
        return self.part.response


def capture_first_boundary(host, program):
    """Strict first-generation decoder, independent of the v3 operation format."""
    db, safe = host.source.connection, host.source.safe
    phase = host.programs.plan(program).phases[0]
    task_id, thread = host.programs._execution_ids(program, phase.phase_id, None)
    for name in ("checkpoints", "writes"):
        check(
            db.execute(
                f"SELECT 1 FROM safe.{name} WHERE thread_id=? AND checkpoint_ns!='' LIMIT 1",
                (thread,),
            ).fetchone()
            is None,
            "recorded_evidence_invalid",
        )
    headers = db.execute(
        "SELECT checkpoint_id,type,length(checkpoint),length(metadata) "
        "FROM safe.checkpoints WHERE thread_id=? AND checkpoint_ns='' "
        "ORDER BY checkpoint_id DESC LIMIT 1",
        (thread,),
    ).fetchone()
    check(
        headers is not None
        and type(headers[0]) is str
        and len(headers[0]) <= 128
        and headers[1] == "msgpack"
        and all(type(n) is int and n >= 0 for n in headers[2:])
        and sum(headers[2:]) <= 16_000_000,
        "recorded_evidence_invalid",
    )
    point_id, encoding, point_size, metadata_size = headers
    row = db.execute(
        "SELECT thread_id,checkpoint_ns,checkpoint_id,parent_checkpoint_id,type,"
        "CASE WHEN typeof(checkpoint)='blob' AND length(checkpoint)=? "
        "THEN substr(checkpoint,1,?) END AS checkpoint,"
        "CASE WHEN typeof(metadata)='blob' AND length(metadata)=? "
        "THEN substr(metadata,1,?) END AS metadata "
        "FROM safe.checkpoints WHERE thread_id=? AND checkpoint_ns='' AND checkpoint_id=? "
        "AND type=? AND (parent_checkpoint_id IS NULL OR length(parent_checkpoint_id)<=128)",
        (point_size, point_size, metadata_size, metadata_size, thread, point_id, encoding),
    ).fetchone()
    check(
        row is not None and type(row["checkpoint"]) is bytes and type(row["metadata"]) is bytes,
        "recorded_evidence_invalid",
    )
    count, size = db.execute(
        "SELECT count(*),coalesce(sum(length(value)),0) FROM safe.writes "
        "WHERE thread_id=? AND checkpoint_ns='' AND checkpoint_id=?",
        (thread, point_id),
    ).fetchone()
    check(count <= 1 and size <= 16_000_000, "recorded_evidence_invalid")
    writes = db.execute(
        "SELECT thread_id,checkpoint_ns,checkpoint_id,task_id,idx,channel,type,"
        "CASE WHEN typeof(value)='blob' AND length(value)=? THEN substr(value,1,?) END AS value "
        "FROM safe.writes WHERE thread_id=? AND checkpoint_ns='' AND checkpoint_id=? "
        "AND length(task_id)<=128 AND length(channel)<=128 AND type='msgpack' LIMIT 2",
        (size, size, thread, point_id),
    ).fetchall()
    check(
        len(writes) == count and all(type(w["value"]) is bytes for w in writes),
        "recorded_evidence_invalid",
    )
    import ormsgpack

    def plain(code, data):
        raise ValueError("unsupported first checkpoint extension")

    def interrupt(code, data):
        value = ormsgpack.unpackb(data, ext_hook=plain)
        check(
            code == 2
            and type(value) is list
            and len(value) == 3
            and value[:2] == ["langgraph.types", "Interrupt"]
            and type(value[2]) is dict
            and value[2].keys() == {"value", "id"}
            and type(value[2]["id"]) is str
            and len(value[2]["id"]) <= 128,
            "recorded_evidence_invalid",
        )
        return value[2]

    ormsgpack.unpackb(row["checkpoint"], ext_hook=plain)
    for write in writes:
        ormsgpack.unpackb(write["value"], ext_hook=interrupt)
    point = safe.graph.get_state(
        {"configurable": {"thread_id": thread, "checkpoint_ns": "", "checkpoint_id": point_id}}
    )
    check(point.config["configurable"]["checkpoint_id"] == point_id, "recorded_evidence_invalid")
    state = point.values
    task = SafeTaskRequest.model_validate(state["task"])
    check(
        task.task_id == task_id
        and task.thread_id == thread
        and task.repository == host.repository
        and task.policy == host.policy
        and task.manifest.base_sha == host.config["origin_commit_sha"]
        and task.objective == phase.objective
        and task.manifest.acceptance_criteria
        == host.programs._execution_acceptance_criteria(phase, None)
        and task.metadata.get("local_product_binding_sha256") == host.binding_sha256
        and state.get("scope_hash") == task.manifest.canonical_hash()
        and state.get("sandbox_path") == str(host.safe_root / "sandboxes" / task_id / "repo")
        and state.get("sandbox_id") == task_id
        and not task.require_publish_approval
        and not state.get("publish_approved"),
        "recorded_evidence_invalid",
    )
    binding = host.programs.execution_binding(task_id).model_dump(mode="json")
    if tuple(point.next) == ("scope_approval",):
        check(
            state.get("status") == binding["status"] == "awaiting_scope_approval"
            and state.get("scope_approved") is None
            and not state.get("patch_applied")
            and len(point.tasks) == 1
            and len(writes) == 1,
            "recorded_evidence_invalid",
        )
        pending, write = point.tasks[0], writes[0]
        check(
            pending.name == "scope_approval"
            and pending.path == ("__pregel_pull", "scope_approval")
            and pending.error is None
            and pending.state is None
            and pending.result is None
            and len(pending.interrupts) == 1
            and write["task_id"] == pending.id
            and write["channel"] == "__interrupt__"
            and write["idx"] == -3,
            "recorded_evidence_invalid",
        )
        expected = {
            "type": "safe_scope_approval",
            "task_id": task_id,
            "base_sha": task.manifest.base_sha,
            "plan_hash": task.manifest.plan_hash,
            "scope_hash": state["scope_hash"],
            "allowed_changes": [c.model_dump(mode="json") for c in task.manifest.allowed_changes],
            "denied_prefixes": list(task.manifest.denied_prefixes),
            "test_profiles": list(task.manifest.test_profiles),
            "acceptance_criteria": list(task.manifest.acceptance_criteria),
        }
        decoded = safe.graph.checkpointer.serde.loads_typed((write["type"], write["value"]))
        check(
            pending.interrupts[0].value == expected and tuple(decoded) == tuple(pending.interrupts),
            "recorded_evidence_invalid",
        )
    else:
        check(
            not point.next
            and not point.tasks
            and not writes
            and state.get("status") in {"completed", "failed", "blocked"}
            and binding["status"] in {"completed", "failed", "cancelled"},
            "recovery_required",
        )
        host.validate_first_terminal(state, binding)

    def encode(record):
        return {
            k: base64.b64encode(v).decode() if type(v) is bytes else v
            for k, v in dict(record).items()
        }

    raw = canonical({"checkpoint": encode(row), "writes": [encode(w) for w in writes]})
    check(len(raw) <= 24_000_000, "recorded_evidence_invalid")
    witness = host.semantic(program, task_id)
    return state, raw, binding, witness
