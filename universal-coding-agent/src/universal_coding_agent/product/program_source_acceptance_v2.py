"""Explicit final source acceptance of a recaptured, settled v3 result.

The original continuation owner is never loaded or reconstructed. Each live call
privately owns one new worker; interrupted calls remain durably ambiguous.
"""

from __future__ import annotations

import base64
from dataclasses import asdict

from universal_coding_agent.core.safe_models import SafeTaskRequest
from universal_coding_agent.product.models import PhaseResult
from universal_coding_agent.product.program_continuation_execution_store import (
    canonical,
    require,
    sha,
)
from universal_coding_agent.product.program_source_acceptance_v2_store import (
    DECISIONS,
    EXACT_FIELDS,
    PROPOSALS,
    REQUESTS,
    AcceptanceStore,
    Reader,
    record,
)
from universal_coding_agent.product.program_source_capture_budget import (
    CaptureBudget,
    charge,
)
from universal_coding_agent.product.program_source_evidence import (
    _capture_at_owned_destination,
    strict_json,
)
from universal_coding_agent.product.program_source_terminal_proof import terminal_history


class ProgramSourceAcceptanceV2Service:
    """Trusted local host composition. Public calls accept only exact metadata."""

    def __init__(self, continuation):
        self.v3, self.store = continuation, continuation.store
        self.db = AcceptanceStore(continuation)
        self.host_sha256 = sha(self._host())
        with self.db.transaction(initialize=True):
            pass

    def _host(self):
        v3, store = self.v3, self.store
        v3._host_gate()
        limits = {
            "max_files": 20_000,
            "max_changes": 1_000,
            "max_file_bytes": 1_000_000,
            "max_total_bytes": 16_000_000,
            "max_artifact_bytes": 24_000_000,
        }
        require(
            all(0 < value <= limits[key] for key, value in asdict(store.source.policy).items()),
            "source limits exceed the bounded acceptance contract",
        )
        return canonical(
            {
                "schema": "uca-source-acceptance-host-2",
                "source_host_sha256": store.host_sha256,
                "continuation_host_sha256": v3.host_sha256,
                "stores": v3.db.identities,
                "program_artifacts": str(store.programs.artifacts.root),
                "safe_artifacts": str(store.safe.artifacts.root),
                "origin": str(store.attestor.root),
                "git_host_sha256": store.attestor.host_binding_sha256,
                "git_policy_sha256": store.attestor.policy_sha256,
                "source_policy": asdict(store.source.policy),
                "test_policy": store.trusted_policy.model_dump(mode="json"),
                "repository_url": store.repository_url,
                "preparation_host_sha256": v3.preparation.host_sha256,
                "capture_bytes": 256_000_000,
            }
        )

    def _host_gate(self):
        require(sha(self._host()) == self.host_sha256, "source acceptance host/policy changed")

    def _quiet(self, tasks):
        coordinator = self.store.safe.control.cancellation
        for task in tasks:
            require(
                not any(coordinator._registration_snapshot(task).values()),
                "source acceptance has active owned work",
            )
            context = coordinator._invocations.get(task)
            require(context is None or context.revoked, "source acceptance has a live invocation")
            executions = Reader(self.store.connection).rows(
                "program_executions", ("program_id", "thread_id"), "task_id=?", (task,), limit=1
            )
            require(len(executions) == 1, "source acceptance task execution is missing")
            execution = executions[0]
            require(
                self.store.connection.execute(
                    "SELECT 1 FROM remote.remote_operation_leases "
                    "WHERE task_id=? OR thread_id=? LIMIT 1",
                    (task, execution["thread_id"]),
                ).fetchone()
                is None,
                "source acceptance has retained remote work",
            )
            require(
                self.store.connection.execute(
                    "SELECT 1 FROM remote.remote_operation_lease_retirements "
                    "WHERE task_id=? OR program_id=? LIMIT 1",
                    (task, execution["program_id"]),
                ).fetchone()
                is None,
                "source acceptance has remote disposition history",
            )

    def _baseline(self, reader, program, operation, owner=None):
        self._host_gate()
        row, admission, historical, completed = terminal_history(reader, program, operation)
        require(row["host_sha256"] == self.v3.host_sha256, "v3 host differs")
        self.v3._legacy_collision(admission)
        # Locator and the two guard envelopes each have an established 64 KiB
        # maximum. Charge that conservative ceiling before the legacy guard reads.
        charge(3 * 65_537)
        self.v3._verify_guard(admission, row["guard_sha256"])
        registry = reader.rows(
            "control.uca_source_dispatch_tasks_v3",
            ("task_id", "thread_id", "admission_sha256", "host_sha256"),
            "task_id=? OR thread_id=?",
            (row["task_id"], row["thread_id"]),
            limit=1,
        )
        require(
            registry
            == [{k: row[k] for k in ("task_id", "thread_id", "admission_sha256", "host_sha256")}],
            "v3 control registry differs",
        )
        current, owner_sha, tasks = self.v3._witness(admission, owner)
        require(current == historical, "terminal semantic authority/source/recovery changed")
        self._quiet(tasks)
        self.v3._remote_absence(admission)
        return row, admission, historical, completed, owner_sha, tasks

    def _checkpoint(self, row, admission, budget):
        db, thread = self.store.connection, row["thread_id"]
        for name in ("checkpoints", "writes"):
            require(
                db.execute(
                    f"SELECT 1 FROM safe.{name} WHERE thread_id=? AND checkpoint_ns!='' LIMIT 1",
                    (thread,),
                ).fetchone()
                is None,
                "unsupported checkpoint namespace",
            )
        # Every raw value is bounded in the actual SELECT before driver allocation.
        sizes = db.execute(
            "SELECT length(checkpoint),length(metadata) FROM safe.checkpoints "
            "WHERE thread_id=? AND checkpoint_ns='' "
            "ORDER BY checkpoint_id DESC LIMIT 1",
            (thread,),
        ).fetchone()
        require(
            sizes is not None
            and all(type(n) is int and n >= 0 for n in sizes)
            and sum(sizes) <= 16_000_000,
            "selected checkpoint byte bound exceeded",
        )
        charge(sum(sizes))
        selected = db.execute(
            """SELECT
            CASE WHEN typeof(checkpoint_id)='text' AND length(CAST(checkpoint_id AS BLOB))<=128
                THEN checkpoint_id END,
            CASE WHEN parent_checkpoint_id IS NULL OR (typeof(parent_checkpoint_id)='text'
                AND length(CAST(parent_checkpoint_id AS BLOB))<=128) THEN parent_checkpoint_id END,
            CASE WHEN type='msgpack' THEN type END,
            CASE WHEN typeof(checkpoint)='blob' AND typeof(metadata)='blob'
                AND length(checkpoint)=? AND length(metadata)=?
                AND length(checkpoint)+length(metadata)<=16000000 THEN substr(checkpoint,1,?) END,
            CASE WHEN typeof(checkpoint)='blob' AND typeof(metadata)='blob'
                AND length(checkpoint)=? AND length(metadata)=?
                AND length(checkpoint)+length(metadata)<=16000000 THEN substr(metadata,1,?) END
            FROM safe.checkpoints WHERE thread_id=? AND checkpoint_ns=''
            ORDER BY checkpoint_id DESC LIMIT 1""",
            (sizes[0], sizes[1], sizes[0], sizes[0], sizes[1], sizes[1], thread),
        ).fetchone()
        require(
            selected is not None
            and type(selected[0]) is str
            and selected[2] == "msgpack"
            and type(selected[3]) is bytes
            and type(selected[4]) is bytes,
            "selected checkpoint type/identity/size differs",
        )
        require(
            db.execute(
                "SELECT 1 FROM safe.writes WHERE thread_id=? AND checkpoint_ns='' "
                "AND checkpoint_id=? LIMIT 1",
                (thread, selected[0]),
            ).fetchone()
            is None,
            "terminal checkpoint contains pending writes",
        )
        import ormsgpack

        def deny_extension(code, data):
            raise ValueError("unsupported terminal checkpoint extension")

        ormsgpack.unpackb(selected[3], ext_hook=deny_extension)
        raw = canonical(
            {
                "checkpoint": {
                    "thread_id": thread,
                    "checkpoint_ns": "",
                    "checkpoint_id": selected[0],
                    "parent_checkpoint_id": selected[1],
                    "type": selected[2],
                    "checkpoint": base64.b64encode(selected[3]).decode(),
                    "metadata": base64.b64encode(selected[4]).decode(),
                },
                "writes": [],
            }
        )
        require(sha(raw) == row["checkpoint_sha256"], "actual terminal checkpoint changed")
        # The ordinary graph reader selects these same locked bytes again.
        charge(sum(sizes))
        point = self.store.safe.graph.get_state(
            {
                "configurable": {
                    "thread_id": thread,
                    "checkpoint_ns": "",
                    "checkpoint_id": selected[0],
                }
            }
        )
        state = point.values
        require(
            not point.next
            and not point.tasks
            and state.get("status") == "completed"
            and point.config["configurable"]["checkpoint_id"] == selected[0],
            "actual Safe graph is not the exact completed terminal",
        )
        require(
            state.get("task") == strict_json(self.store._get(row["task_sha256"])),
            "actual terminal Safe task differs",
        )
        task = SafeTaskRequest.model_validate(state["task"])
        destination = (
            self.v3.preparation.filesystem.root / ("execution-" + row["operation_id"]) / "repo"
        )
        require(
            task.task_id == row["task_id"]
            and task.thread_id == thread
            and state.get("sandbox_path") == str(destination)
            and state.get("sandbox_id") == row["task_id"]
            and state.get("base_sha") == admission["derived_git_commit_sha"]
            and state.get("scope_hash") == task.manifest.canonical_hash()
            and not task.require_publish_approval
            and not state.get("publish_approved"),
            "actual terminal source/scope/publication differs",
        )
        budget.settled()
        return raw, state, destination

    def _origin(self, before, budget):
        attestor = self.store.attestor
        inventory = budget.inventory(attestor.root)
        origin = attestor.attest(before.identity)
        attestor.verify_retained_files(origin.snapshot.files)
        require(
            inventory == budget.inventory(attestor.root), "origin changed during Git inspection"
        )
        return canonical(
            {"attestation": strict_json(origin.receipt_bytes()), "inventory": inventory}
        )

    def _program_evidence(self, row, admission, state, baseline):
        artifacts, programs = self.store.programs.artifacts, self.store.programs
        prefix = self.v3._result_prefix(row["program_id"], row["phase_id"], row["task_id"], state)
        names = (
            "safe-result.json",
            "phase-execution-report.json",
            "phase-result.json",
            "phase-summary.md",
        )
        refs = [f"artifact://{prefix}/{name}" for name in names]
        raw = [artifacts._read_bytes_bounded(ref, max_bytes=2_000_000) for ref in refs]
        result_pair = strict_json(self.store._get(row["result_sha256"]))
        require(
            result_pair == {"result_sha256": sha(raw[0]), "report_sha256": sha(raw[1])}
            and strict_json(raw[0]) == state,
            "actual Program result/report changed",
        )
        report, result = strict_json(raw[1]), PhaseResult.model_validate(strict_json(raw[2]))
        execution = next(e for e in baseline["executions"] if e["task_id"] == row["task_id"])
        phase = next(p for p in baseline["phases"] if p["phase_id"] == row["phase_id"])
        require(
            execution["result_ref"] == refs[0]
            and execution["phase_report_ref"] == refs[1]
            and phase["result_ref"] == refs[2]
            and phase["summary_ref"] == refs[3]
            and report["schema"] == "uca-program-source-execution-report-3"
            and report["program_id"] == row["program_id"]
            and report["phase_id"] == row["phase_id"]
            and report["program_status"] == report["phase_status"] == "completed"
            and report["admission_sha256"] == row["admission_sha256"]
            and report["source_acceptance_authorized"] is False
            and report["execution_authorized"] is False
            and report["automatic_execution"] is False
            and report["consumer_bound"] is True
            and len(report["bindings"]) == 1,
            "actual Program report binding differs",
        )
        binding = report["bindings"][0]
        require(
            all(
                binding[k] == execution[k]
                for k in (
                    "task_id",
                    "thread_id",
                    "program_id",
                    "phase_id",
                    "requirement_hash",
                    "status",
                    "safe_status",
                    "result_ref",
                    "expected_base_sha",
                )
            ),
            "actual Program execution differs",
        )
        require(
            result.phase_id == row["phase_id"]
            and result.reviewer_verdict == "PASS"
            and result.changed_paths == tuple(state.get("actual_changed_paths", ()))
            and result.tests == (f"{row['task_id']}: {state['tests_ref']}",)
            and programs._phase_summary(row["program_id"], result).encode() == raw[3],
            "actual Program phase evidence differs",
        )
        return canonical(
            {
                "schema": "uca-program-source-evidence-2",
                "artifacts": [
                    {
                        "ref": ref,
                        "sha256": sha(value),
                        "content_base64": base64.b64encode(value).decode(),
                    }
                    for ref, value in zip(refs, raw, strict=True)
                ],
            }
        )

    def _capture(self, reader, payload, owner, budget):
        row, admission, baseline, completed, owner_sha, tasks = self._baseline(
            reader, payload["program_id"], payload["operation_id"], owner
        )
        require(
            row["receipt_sha256"] == payload["terminal_receipt_sha256"]
            and admission["source_sha256"] == payload["before_sha256"]
            and admission["generation"] == payload["generation"],
            "requested baseline differs",
        )
        before = self.store.source.load_snapshot(
            self.store._get(admission["source_sha256"]), expected_sha256=admission["source_sha256"]
        )
        plan = self.store._plan(before.identity)
        require(
            len(plan.phases) == 2
            and all(not p.slices for p in plan.phases)
            and plan.phases[1].phase_id == admission["phase_id"],
            "Program is not the final linear unit",
        )
        require(
            not plan.phases[0].dependencies
            and tuple(plan.phases[1].dependencies) == (plan.phases[0].phase_id,)
            and before.generation == 1
            and before.identity.program_id == row["program_id"]
            and before.identity.repository_sha256 == admission["origin_repository_sha256"]
            and before.identity.origin_base_sha == admission["origin_base_sha"]
            and before.identity.origin_tree_sha == admission["origin_tree_sha"],
            "source origin/generation or linear dependency differs",
        )
        require(
            self.v3._lineage(admission, before) == self.store._get(admission["dependency_sha256"]),
            "actual first-phase evidence changed",
        )
        self.store.programs.artifacts.read_bytes_bounded_verified(
            admission["dependency_ref"],
            expected_sha256=admission["dependency_sha256"],
            max_bytes=48_000,
        )
        for item in strict_json(self.store._get(row["discovery_sha256"])):
            self.store.safe.artifacts.read_bytes_bounded_verified(
                item["ref"], expected_sha256=item["sha256"], max_bytes=2_000_000
            )
        filesystem = self.v3._verify_files(row, admission)
        checkpoint, state, destination = self._checkpoint(row, admission, budget)
        task = SafeTaskRequest.model_validate(state["task"])
        require(
            (task.task_id, task.thread_id)
            == self.store.programs._execution_ids(row["program_id"], row["phase_id"], None)
            and task.objective == plan.phases[1].objective
            and task.manifest.acceptance_criteria
            == self.store.programs._execution_acceptance_criteria(plan.phases[1], None),
            "actual Safe task is not the approved final execution unit",
        )
        evidence = _capture_at_owned_destination(
            state=state,
            before=before,
            artifacts=self.store.safe.artifacts,
            repository_url=self.store.repository_url,
            policy=self.store.trusted_policy,
            attestor=self.store.attestor,
            sandbox=destination,
        )
        program_evidence = self._program_evidence(row, admission, state, baseline)
        origin = self._origin(before, budget)
        require(
            filesystem == self.v3._verify_files(row, admission),
            "filesystem changed during Git inspection",
        )
        transition = self.store.source.prepare(
            before,
            expected_source_sha256=admission["source_sha256"],
            phase_id=row["phase_id"],
            task_id=row["task_id"],
            slice_id=None,
            allowed_paths=evidence.allowed_paths,
            evidence_sha256=tuple(
                sorted({sha(evidence.payload), sha(checkpoint), sha(program_evidence)})
            ),
            edits=evidence.edits,
        )
        transition_raw = self.store.source.transition_bytes(transition)
        after = self.store.source.materialize(
            before, transition, approved_transition_sha256=sha(transition_raw)
        )
        after_raw = self.store.source.snapshot_bytes(after)
        inventory = canonical(budget.files)
        core = {
            "schema": "uca-source-evidence-core-2",
            "program_id": row["program_id"],
            "operation_id": row["operation_id"],
            "task_id": row["task_id"],
            "execution_schema": "uca-program-source-dispatch-3",
            "admission_sha256": row["admission_sha256"],
            "terminal_receipt_sha256": row["receipt_sha256"],
            "settlement_sha256": row["settlement_sha256"],
            "terminal_response_sha256": completed["response_sha256"],
            "decision_sha256": row["decision_sha256"],
            "checkpoint_sha256": sha(checkpoint),
            "result_sha256": row["result_sha256"],
            "preparation_receipt_sha256": admission["preparation_receipt_sha256"],
            "materialization_receipt_sha256": admission["materialization_receipt_sha256"],
            "dependency_sha256": admission["dependency_sha256"],
            "baseline_sha256": sha(canonical(baseline)),
            "source_host_sha256": self.store.host_sha256,
            "host_sha256": self.host_sha256,
            "evidence_sha256": sha(evidence.payload),
            "program_evidence_sha256": sha(program_evidence),
            "filesystem_sha256": sha(filesystem),
            "origin_sha256": sha(origin),
            "inventory_sha256": sha(inventory),
            "transition_sha256": sha(transition_raw),
            "before_sha256": admission["source_sha256"],
            "after_sha256": sha(after_raw),
            "generation": 1,
            "predecessor_receipt_sha256": admission["acceptance_receipt_sha256"],
        }
        witness = {
            "schema": "uca-source-capture-witness-2",
            "program_id": row["program_id"],
            "operation_id": row["operation_id"],
            "host_sha256": self.host_sha256,
            "baseline_sha256": core["baseline_sha256"],
            "owner_sha256": owner_sha,
            "pins_sha256": sha(canonical(self.v3.db.identities)),
            "checkpoint_sha256": sha(checkpoint),
            "filesystem_sha256": sha(filesystem),
            "inventory_sha256": sha(inventory),
            "core_sha256": sha(canonical(core)),
        }
        candidate = {
            "schema": "uca-source-candidate-2",
            "revision": 1,
            **{
                k: core[k]
                for k in (
                    "program_id",
                    "task_id",
                    "operation_id",
                    "host_sha256",
                    "transition_sha256",
                    "before_sha256",
                    "after_sha256",
                    "generation",
                    "predecessor_receipt_sha256",
                    "terminal_receipt_sha256",
                )
            },
            "core_sha256": sha(canonical(core)),
        }
        for value in (core, witness, candidate):
            record(canonical(value), value["schema"])
        budget.settled()
        self._quiet(tasks)
        return (
            candidate,
            witness,
            (
                checkpoint,
                evidence.payload,
                program_evidence,
                filesystem,
                origin,
                inventory,
                transition_raw,
                after_raw,
                canonical(baseline),
                canonical(core),
            ),
            tasks,
        )

    def preview_source_transition(
        self,
        program_id,
        operation_id,
        *,
        request_id,
        terminal_receipt_sha256,
        before_sha256,
        generation,
    ):
        return self._operate(
            {
                "schema": "uca-source-request-2",
                "program_id": program_id,
                "operation_id": operation_id,
                "host_sha256": self.host_sha256,
                "action": "preview",
                "request_id": request_id,
                "terminal_receipt_sha256": terminal_receipt_sha256,
                "before_sha256": before_sha256,
                "generation": generation,
                **{
                    k: None
                    for k in (
                        "approval_id",
                        "approved",
                        "candidate_sha256",
                        "revision",
                        "core_sha256",
                        "transition_sha256",
                        "predecessor_receipt_sha256",
                    )
                },
            }
        )

    def decide_source_transition(
        self,
        program_id,
        operation_id,
        *,
        request_id,
        approval_id,
        approved,
        candidate_sha256,
        revision,
        core_sha256,
        transition_sha256,
        before_sha256,
        generation,
        predecessor_receipt_sha256,
        terminal_receipt_sha256,
    ):
        return self._operate(
            {
                "schema": "uca-source-request-2",
                "host_sha256": self.host_sha256,
                "action": "decide",
                **{k: v for k, v in locals().items() if k != "self"},
            }
        )

    def source_transition_request_result(self, program_id, request_id):
        from universal_coding_agent.product.program_source_acceptance_v2_status import (
            request_result,
        )

        return request_result(
            self.store.programs.database_path, self.host_sha256, program_id, request_id
        )

    def source_transition_status(self, program_id):
        from universal_coding_agent.product.program_source_acceptance_v2_status import (
            source_transition_status,
        )

        return source_transition_status(self.store.programs.database_path, program_id)

    def _operate(self, payload):
        record(canonical(payload), payload["schema"])
        program, operation, request_id = (
            payload[k] for k in ("program_id", "operation_id", "request_id")
        )
        from universal_coding_agent.product.program_source_acceptance_v2_status import (
            completed_request,
        )

        # Replay is exclusively historical and performs no host/filesystem recapture.
        with self.db.transaction(label="lookup") as reader:
            replay = completed_request(reader, self.host_sha256, program, request_id, payload)
            if replay is not None:
                return replay
        budget = CaptureBudget()
        with budget.activate():
            with self.db.transaction(label="claim") as reader:
                replay = completed_request(reader, self.host_sha256, program, request_id, payload)
                if replay is not None:
                    return replay
                row, admission, baseline, _, _, tasks = self._baseline(reader, program, operation)
                require(
                    row["receipt_sha256"] == payload["terminal_receipt_sha256"]
                    and admission["source_sha256"] == payload["before_sha256"]
                    and admission["generation"] == payload["generation"],
                    "requested source head differs",
                )
                proposals = reader.rows(
                    PROPOSALS,
                    ("candidate_sha256",),
                    "program_id=? AND task_id=?",
                    (program, row["task_id"]),
                    limit=1,
                )
                if payload["action"] == "preview":
                    require(not proposals, "another preview already prepared this task")
                else:
                    require(
                        proposals == [{"candidate_sha256": payload["candidate_sha256"]}],
                        "candidate was not prepared by this host",
                    )
                    candidate = reader.record(payload["candidate_sha256"], "uca-source-candidate-2")
                    require(
                        all(
                            payload[k] == candidate[k]
                            for k in EXACT_FIELDS.split()
                            if k != "candidate_sha256"
                        )
                        and candidate["host_sha256"] == self.host_sha256,
                        "exact candidate approval differs",
                    )
                    require(
                        not reader.rows(
                            DECISIONS,
                            ("candidate_sha256",),
                            "candidate_sha256=?",
                            (payload["candidate_sha256"],),
                            limit=1,
                        ),
                        "candidate decision is final",
                    )
                owner = self.v3.lifecycle.reserve_program_worker_in_transaction(
                    self.store.connection, program, task_ids=tasks
                )
                _, owner_sha, _ = self.v3._witness(admission, owner)
                payload_sha = self.db.put(payload)
                baseline_sha = self.store._put(canonical(baseline))
                self.store.connection.execute(
                    f"INSERT INTO {REQUESTS} VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (
                        self.host_sha256,
                        program,
                        request_id,
                        operation,
                        payload["action"],
                        payload_sha,
                        baseline_sha,
                        owner_sha,
                        "pending",
                        None,
                    ),
                )
            # Once claimed, any exception intentionally retains the private worker.
            with self.db.transaction(label="capture") as reader:
                captured = self._capture(reader, payload, owner, budget)
            self.db.boundary("capture_returned")

            def final_check():
                budget.recheck_files()
                require(
                    budget.inventory(self.store.attestor.root)
                    == strict_json(blobs[4])["inventory"],
                    "origin inventory changed before commit",
                )
                historical_row = self.v3._row(operation)
                historical_admission = self.v3._admission(historical_row)
                require(
                    sha(self.v3._verify_files(historical_row, historical_admission))
                    == witness["filesystem_sha256"],
                    "retained inventory changed before commit",
                )
                budget.settled()
                self._quiet(tasks)
                self.v3.lifecycle.check_program_worker_in_transaction(
                    self.store.connection, program, task_ids=tasks, owner_token=None
                )
                self._host_gate()

            with self.db.transaction(label="final", verify=final_check) as reader:
                repeated = self._capture(reader, payload, owner, budget)
                require(repeated == captured, "source capture/witness changed before commit")
                candidate, witness, blobs, tasks = repeated
                require(
                    witness["baseline_sha256"] == baseline_sha
                    and witness["owner_sha256"] == owner_sha,
                    "claimed capture authority differs",
                )
                candidate_sha = sha(canonical(candidate))
                if payload["action"] == "decide":
                    require(
                        candidate_sha == payload["candidate_sha256"],
                        "reviewed evidence core changed",
                    )
                for raw in blobs:
                    self.store._put(raw)
                self.db.put(candidate)
                witness_sha = self.db.put(witness)
                approval_sha = receipt_sha = None
                status = "prepared"
                if payload["action"] == "preview":
                    self.store.connection.execute(
                        f"INSERT INTO {PROPOSALS} VALUES (?,?,?,?,?)",
                        (program, candidate["task_id"], operation, candidate_sha, payload_sha),
                    )
                else:
                    approval_sha = self.db.put({**payload, "schema": "uca-source-approval-2"})
                    status = "accepted" if payload["approved"] else "rejected"
                    if payload["approved"]:
                        receipt_sha = self.db.put(
                            {
                                "schema": "uca-source-acceptance-receipt-2",
                                "program_id": program,
                                "operation_id": operation,
                                "task_id": candidate["task_id"],
                                "candidate_sha256": candidate_sha,
                                "approval_sha256": approval_sha,
                                "core_sha256": candidate["core_sha256"],
                                "transition_sha256": candidate["transition_sha256"],
                                "predecessor_sha256": candidate["before_sha256"],
                                "predecessor_receipt_sha256": candidate[
                                    "predecessor_receipt_sha256"
                                ],
                                "terminal_receipt_sha256": candidate["terminal_receipt_sha256"],
                                "source_sha256": candidate["after_sha256"],
                                "generation": 2,
                                "host_sha256": self.store.host_sha256,
                                "acceptance_host_sha256": self.host_sha256,
                                "witness_sha256": witness_sha,
                                "materialization_ready": False,
                                "execution_authorized": False,
                                "automatic_execution": False,
                            }
                        )
                        self.store.connection.execute(
                            "INSERT INTO program_source_acceptances VALUES (?,?,?,?,?)",
                            (
                                candidate_sha,
                                approval_sha,
                                receipt_sha,
                                program,
                                candidate["task_id"],
                            ),
                        )
                        changed = self.store.connection.execute(
                            """UPDATE program_source_heads
                            SET generation=2,source_sha256=?,receipt_sha256=? WHERE program_id=?
                            AND generation=1 AND source_sha256=? AND receipt_sha256=?
                            AND host_sha256=?""",
                            (
                                candidate["after_sha256"],
                                receipt_sha,
                                program,
                                candidate["before_sha256"],
                                candidate["predecessor_receipt_sha256"],
                                self.store.host_sha256,
                            ),
                        ).rowcount
                        require(changed == 1, "source head compare-and-swap lost")
                        self.db.boundary("after_source_head")
                    self.store.connection.execute(
                        f"INSERT INTO {DECISIONS} VALUES (?,?,?,?,?)",
                        (
                            candidate_sha,
                            approval_sha,
                            receipt_sha,
                            payload_sha,
                            int(payload["approved"]),
                        ),
                    )
                response = {
                    "schema": "uca-source-response-2",
                    "program_id": program,
                    "operation_id": operation,
                    "host_sha256": self.host_sha256,
                    "request_id": request_id,
                    "request_sha256": payload_sha,
                    "action": payload["action"],
                    "status": status,
                    "candidate_sha256": candidate_sha,
                    "candidate": candidate,
                    "approval_sha256": approval_sha,
                    "receipt_sha256": receipt_sha,
                    "witness_sha256": witness_sha,
                    "execution_authorized": False,
                    "automatic_execution": False,
                    "materialization_ready": False,
                }
                response_sha = self.db.put(response)
                changed = self.store.connection.execute(
                    f"""UPDATE {REQUESTS} SET status='completed',
                    response_sha256=? WHERE host_sha256=? AND program_id=? AND request_id=?
                    AND status='pending' AND payload_sha256=? AND owner_sha256=?
                    AND baseline_sha256=?""",
                    (
                        response_sha,
                        self.host_sha256,
                        program,
                        request_id,
                        payload_sha,
                        owner_sha,
                        baseline_sha,
                    ),
                ).rowcount
                require(changed == 1, "source request claim changed")
                self.db.boundary("after_response")
                budget.settled()
                self._quiet(tasks)
                self.v3.lifecycle.release_program_worker_in_transaction(
                    self.store.connection, program, task_ids=tasks, owner_token=owner
                )
                self.db.boundary("after_worker_release")
            return response
