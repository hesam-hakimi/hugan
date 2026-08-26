from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from threading import RLock
from typing import Any, Protocol

from pydantic import TypeAdapter

from universal_coding_agent.core.models import ModelRequest, RepositorySpec, SlicePlan
from universal_coding_agent.core.remote_operations import (
    RemoteOperationDisposition,
    RemoteOperationDispositionOutcome,
)
from universal_coding_agent.core.safe_models import SafeContextEvidence, SafeModePolicy
from universal_coding_agent.orchestration.structured_output import (
    StructuredOutputError,
    invoke_structured,
)
from universal_coding_agent.product.models import (
    AcceptedPhaseEvidence,
    AcceptedPhaseEvidenceBundle,
    AcceptedSafeExecutionEvidence,
    ControlAction,
    ControlEntityType,
    ControlState,
    PhaseResult,
    PhaseStatus,
    ProgramExecutionBinding,
    ProgramExecutionStatus,
    ProgramPhase,
    ProgramPlan,
    ProgramPlanDraft,
    ProgramStatus,
    RequirementContract,
    RequirementStatus,
    SearchSourceType,
)
from universal_coding_agent.product.search_service import SearchService
from universal_coding_agent.product.task_control import TaskControlService
from universal_coding_agent.providers.base import ModelProvider
from universal_coding_agent.safety.sanitizer import sanitize_text
from universal_coding_agent.storage.artifacts import ArtifactStore

_PROGRAM_SYSTEM_PROMPT = """You are a software delivery program planner.
Return exactly one JSON object matching the supplied schema. Decompose the approved
requirement into the smallest coherent phases that can be delivered and reviewed safely.
Use explicit phase dependencies, acceptance criteria, expected components, and stop
conditions. Do not invent business requirements. Preserve security, compatibility, data
migration, testing, documentation, and rollback concerns when the approved contract requires
them. Do not write code or claim execution has happened.

Dependency levels are strict and must never be mixed:
- ProgramPhase.dependencies contains only exact phase_id values declared in this program.
- SlicePlan.dependencies contains only exact slice_id values declared inside that same phase.
- A slice must never place a phase_id or a slice_id from another phase in SlicePlan.dependencies.
- Prior-phase contracts, outputs, decisions, or prerequisites belong in
  SlicePlan.external_dependencies as descriptive stable references, while ordering between
  phases belongs in ProgramPhase.dependencies.
If a phase contains one slice, that slice normally has an empty dependencies array."""

_PROGRAM_REPAIR_GUIDANCE = """Preserve the proposed program while correcting JSON structure.
For ProgramPhase.dependencies, use only exact phase_id values declared in the same response.
For each SlicePlan.dependencies, use only exact slice_id values declared inside that same phase.
Move all cross-phase slice prerequisites to SlicePlan.external_dependencies and express phase
ordering in ProgramPhase.dependencies. Never replace a cross-phase slice ID with a phase ID
inside SlicePlan.dependencies. Remove dependency cycles and keep at least one phase."""

_PHASE_UNIT_KEY = "__phase__"
_ACTIVE_EXECUTION_STATUSES = {
    ProgramExecutionStatus.STARTING,
    ProgramExecutionStatus.AWAITING_SCOPE_APPROVAL,
    ProgramExecutionStatus.RUNNING,
}
_JSON_VALUE_ADAPTER = TypeAdapter(Any)


class ProgramExecutionError(RuntimeError):
    """A program execution unit could not cross its next safe boundary."""


class DiscoveredSafeExecutionPort(Protocol):
    def start(
        self,
        *,
        task_id: str,
        thread_id: str,
        title: str,
        objective: str,
        repository: RepositorySpec,
        policy: SafeModePolicy,
        test_profiles: tuple[str, ...],
        acceptance_criteria: tuple[str, ...] = (),
        accepted_evidence: tuple[SafeContextEvidence, ...] = (),
        expected_base_sha: str = "",
    ) -> dict[str, Any]: ...

    def resume(self, thread_id: str, approved: bool) -> dict[str, Any]: ...


class ProgramOrchestrator:
    """Persistent program/phase orchestration above Safe Mode.

    It does not bypass Safe Mode. It determines which phase and slice may start, binds one unit
    to an injected Discovered Safe execution port, records durable evidence, and stops future
    work when paused, cancelled, blocked, or when the approved requirement hash changes.
    """

    def __init__(
        self,
        database_path: Path,
        artifacts: ArtifactStore,
        provider: ModelProvider,
        search: SearchService,
        control: TaskControlService,
    ) -> None:
        self.database_path = database_path.resolve()
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.artifacts = artifacts
        self.provider = provider
        self.search = search
        self.control = control
        self._lock = RLock()
        self.connection = sqlite3.connect(self.database_path, check_same_thread=False)
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS programs (
                program_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                requirement_hash TEXT NOT NULL,
                plan_hash TEXT NOT NULL,
                plan_ref TEXT NOT NULL
            )
            """
        )
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS program_phases (
                program_id TEXT NOT NULL,
                phase_id TEXT NOT NULL,
                status TEXT NOT NULL,
                result_ref TEXT NOT NULL DEFAULT '',
                summary_ref TEXT NOT NULL DEFAULT '',
                PRIMARY KEY(program_id, phase_id)
            )
            """
        )
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS program_executions (
                program_id TEXT NOT NULL,
                phase_id TEXT NOT NULL,
                unit_key TEXT NOT NULL,
                slice_id TEXT NOT NULL DEFAULT '',
                task_id TEXT NOT NULL UNIQUE,
                thread_id TEXT NOT NULL UNIQUE,
                requirement_hash TEXT NOT NULL,
                status TEXT NOT NULL,
                safe_status TEXT NOT NULL DEFAULT '',
                result_ref TEXT NOT NULL DEFAULT '',
                phase_report_ref TEXT NOT NULL DEFAULT '',
                error_ref TEXT NOT NULL DEFAULT '',
                accepted_evidence_ref TEXT NOT NULL DEFAULT '',
                accepted_evidence_hash TEXT NOT NULL DEFAULT '',
                expected_base_sha TEXT NOT NULL DEFAULT '',
                remote_disposition_ref TEXT NOT NULL DEFAULT '',
                PRIMARY KEY(program_id, phase_id, unit_key)
            )
            """
        )
        self._ensure_execution_column(
            "accepted_evidence_ref", "TEXT NOT NULL DEFAULT ''"
        )
        self._ensure_execution_column(
            "accepted_evidence_hash", "TEXT NOT NULL DEFAULT ''"
        )
        self._ensure_execution_column("expected_base_sha", "TEXT NOT NULL DEFAULT ''")
        self._ensure_execution_column(
            "remote_disposition_ref", "TEXT NOT NULL DEFAULT ''"
        )
        self.connection.commit()

    def close(self) -> None:
        with self._lock:
            self.connection.close()

    def create_program(
        self,
        *,
        program_id: str,
        requirement: RequirementContract,
        requirement_hash: str,
        top_k: int = 20,
    ) -> ProgramPlan:
        if requirement.status is not RequirementStatus.APPROVED:
            raise ValueError("program planning requires an approved requirement contract")
        if requirement.canonical_hash() != requirement_hash:
            raise ValueError("requirement hash does not match the approved contract")
        if self._program_row(program_id) is not None:
            raise ValueError(f"program already exists: {program_id}")
        evidence = self.search.search(requirement.objective, top_k=top_k)
        context = self._planner_context(requirement, requirement_hash, evidence)
        context_ref = self.artifacts.write_text(
            f"programs/{program_id}/program-planner-context.md",
            context,
            "text/markdown",
        )
        request = ModelRequest(
            role="program_planner",
            system_prompt=_PROGRAM_SYSTEM_PROMPT,
            user_prompt=context,
            response_schema=ProgramPlanDraft.model_json_schema(),
            max_output_tokens=8000,
            metadata={"program_id": program_id, "requirement_hash": requirement_hash},
        )
        try:
            structured = invoke_structured(
                self.provider,
                request,
                ProgramPlanDraft,
                repair_guidance=_PROGRAM_REPAIR_GUIDANCE,
            )
        except StructuredOutputError as exc:
            self.artifacts.write_json(
                f"programs/{program_id}/program-planner-validation.json",
                exc.diagnostics,
            )
            raise
        self.artifacts.write_json(
            f"programs/{program_id}/program-planner-validation.json",
            structured.diagnostics,
        )
        draft = structured.value
        plan = ProgramPlan(
            program_id=program_id,
            title=draft.title,
            objective=draft.objective,
            requirement_hash=requirement_hash,
            phases=draft.phases,
            definition_of_done=draft.definition_of_done,
        )
        plan_ref = self.artifacts.write_json(
            f"programs/{program_id}/program-plan.json",
            plan.model_dump(mode="json"),
        )
        plan_hash = plan.canonical_hash()
        self.connection.execute(
            """
            INSERT INTO programs(program_id, status, requirement_hash, plan_hash, plan_ref)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                program_id,
                ProgramStatus.AWAITING_APPROVAL.value,
                requirement_hash,
                plan_hash,
                plan_ref.uri,
            ),
        )
        self.connection.executemany(
            """
            INSERT INTO program_phases(program_id, phase_id, status)
            VALUES (?, ?, ?)
            """,
            [
                (program_id, phase.phase_id, PhaseStatus.PENDING.value)
                for phase in plan.phases
            ],
        )
        self.connection.commit()
        self.control.ensure(ControlEntityType.PROGRAM, program_id)
        self.search.index_text(
            namespace="programs",
            source_type=SearchSourceType.DECISION,
            source_id=program_id,
            path=f"program:{program_id}:plan",
            text=self._program_summary(plan, plan_hash),
            metadata={
                "program_id": program_id,
                "plan_hash": plan_hash,
                "requirement_hash": requirement_hash,
                "context_ref": context_ref.uri,
            },
        )
        return plan

    def approve_program(self, program_id: str, plan_hash: str) -> ProgramPlan:
        row = self._program_row_required(program_id)
        if row[3] != plan_hash:
            raise ValueError("plan hash changed; approval rejected")
        self.connection.execute(
            "UPDATE programs SET status = ? WHERE program_id = ?",
            (ProgramStatus.RUNNING.value, program_id),
        )
        self.connection.commit()
        return self.plan(program_id)

    def plan(self, program_id: str) -> ProgramPlan:
        with self._lock:
            row = self._program_row_required(program_id)
            return ProgramPlan.model_validate(self.artifacts.read_json(row[4]))

    def status(self, program_id: str) -> ProgramStatus:
        with self._lock:
            row = self._program_row_required(program_id)
            return ProgramStatus(row[1])

    def phase_status(self, program_id: str, phase_id: str) -> PhaseStatus:
        with self._lock:
            row = self.connection.execute(
                """
                SELECT status FROM program_phases WHERE program_id = ? AND phase_id = ?
                """,
                (program_id, phase_id),
            ).fetchone()
            if row is None:
                raise KeyError(phase_id)
            return PhaseStatus(row[0])

    def ready_phases(self, program_id: str) -> tuple[ProgramPhase, ...]:
        if self.status(program_id) is not ProgramStatus.RUNNING:
            return ()
        decision = self.control.checkpoint(ControlEntityType.PROGRAM, program_id)
        if decision.action is ControlAction.PAUSE:
            self._set_program_status(program_id, ProgramStatus.PAUSED)
            return ()
        if decision.action is ControlAction.CANCEL:
            self._cancel_program(program_id)
            return ()
        plan = self.plan(program_id)
        completed = {
            phase.phase_id
            for phase in plan.phases
            if self.phase_status(program_id, phase.phase_id) is PhaseStatus.COMPLETED
        }
        return tuple(
            phase
            for phase in plan.phases
            if self.phase_status(program_id, phase.phase_id) is PhaseStatus.PENDING
            and set(phase.dependencies).issubset(completed)
        )

    def start_phase(self, program_id: str, phase_id: str) -> ProgramPhase:
        ready = {phase.phase_id: phase for phase in self.ready_phases(program_id)}
        phase = ready.get(phase_id)
        if phase is None:
            raise ValueError("phase is not ready to start")
        self.connection.execute(
            """
            UPDATE program_phases SET status = ? WHERE program_id = ? AND phase_id = ?
            """,
            (PhaseStatus.RUNNING.value, program_id, phase_id),
        )
        self.connection.commit()
        return phase

    def start_next_execution(
        self,
        *,
        program_id: str,
        current_requirement_hash: str,
        repository: RepositorySpec,
        policy: SafeModePolicy,
        test_profiles: tuple[str, ...],
        executor: DiscoveredSafeExecutionPort,
    ) -> ProgramExecutionBinding:
        """Start at most one approved dependency-ready unit through Discovered Safe Mode."""

        requested_profiles = self._validate_execution_profiles(policy, test_profiles)
        with self._lock:
            self._require_execution_ready(program_id, current_requirement_hash)
            active = self._active_execution(program_id)
            if active is not None:
                return active
            phase, slice_plan = self._next_execution_unit(program_id)
            accepted_evidence, expected_base_sha = self._prepare_accepted_evidence(
                program_id,
                phase,
                current_requirement_hash,
            )
            if self.phase_status(program_id, phase.phase_id) is PhaseStatus.PENDING:
                self.start_phase(program_id, phase.phase_id)
            task_id, thread_id = self._execution_ids(
                program_id,
                phase.phase_id,
                slice_plan.slice_id if slice_plan is not None else None,
            )
            binding = ProgramExecutionBinding(
                program_id=program_id,
                phase_id=phase.phase_id,
                slice_id=slice_plan.slice_id if slice_plan is not None else None,
                task_id=task_id,
                thread_id=thread_id,
                requirement_hash=current_requirement_hash,
                status=ProgramExecutionStatus.STARTING,
                accepted_evidence_ref=(
                    accepted_evidence[0].source_ref if accepted_evidence else ""
                ),
                accepted_evidence_hash=(
                    accepted_evidence[0].sha256 if accepted_evidence else ""
                ),
                expected_base_sha=expected_base_sha,
            )
            self._insert_execution(binding)
            self.control.ensure_task(task_id)
            self._write_phase_execution_report(program_id, phase.phase_id)
            binding = self.execution_binding(task_id)

        title = (
            f"{phase.title}: {slice_plan.title}" if slice_plan is not None else phase.title
        )[:200]
        objective = slice_plan.objective if slice_plan is not None else phase.objective
        criteria = self._execution_acceptance_criteria(phase, slice_plan)
        try:
            result = executor.start(
                task_id=task_id,
                thread_id=thread_id,
                title=title,
                objective=objective,
                repository=repository,
                policy=policy,
                test_profiles=requested_profiles,
                acceptance_criteria=criteria,
                accepted_evidence=accepted_evidence,
                expected_base_sha=expected_base_sha,
            )
        except Exception as exc:
            with self._lock:
                self._record_execution_error(binding, exc)
            raise ProgramExecutionError(
                f"Discovered Safe execution failed safely: {type(exc).__name__}"
            ) from exc

        with self._lock:
            return self._record_execution_result(binding, result)

    def continue_execution(
        self,
        *,
        program_id: str,
        task_id: str,
        current_requirement_hash: str,
        executor: DiscoveredSafeExecutionPort,
        approved: bool,
    ) -> ProgramExecutionBinding:
        """Resume one bound Safe thread after an explicit human scope decision."""

        with self._lock:
            self._require_execution_ready(program_id, current_requirement_hash)
            binding = self.execution_binding(task_id)
            if binding.program_id != program_id:
                raise ProgramExecutionError("execution binding belongs to another program")
            if binding.status is ProgramExecutionStatus.COMPLETED:
                return binding
            if binding.status not in _ACTIVE_EXECUTION_STATUSES:
                raise ProgramExecutionError("execution binding is terminal")
            thread_id = binding.thread_id

        try:
            result = executor.resume(thread_id, approved)
        except Exception as exc:
            with self._lock:
                self._record_execution_error(binding, exc)
            raise ProgramExecutionError(
                f"Discovered Safe resume failed safely: {type(exc).__name__}"
            ) from exc

        with self._lock:
            return self._record_execution_result(binding, result)

    def execution_binding(self, task_id: str) -> ProgramExecutionBinding:
        with self._lock:
            row = self.connection.execute(
                """
                SELECT program_id, phase_id, slice_id, task_id, thread_id,
                       requirement_hash, status, safe_status, result_ref,
                       phase_report_ref, error_ref, accepted_evidence_ref,
                       accepted_evidence_hash, expected_base_sha,
                       remote_disposition_ref
                FROM program_executions WHERE task_id = ?
                """,
                (task_id,),
            ).fetchone()
            if row is None:
                raise KeyError(task_id)
            return self._binding_from_row(row)

    def execution_bindings(self, program_id: str) -> tuple[ProgramExecutionBinding, ...]:
        with self._lock:
            rows = self.connection.execute(
                """
                SELECT program_id, phase_id, slice_id, task_id, thread_id,
                       requirement_hash, status, safe_status, result_ref,
                       phase_report_ref, error_ref, accepted_evidence_ref,
                       accepted_evidence_hash, expected_base_sha,
                       remote_disposition_ref
                FROM program_executions WHERE program_id = ? ORDER BY rowid
                """,
                (program_id,),
            ).fetchall()
            return tuple(self._binding_from_row(row) for row in rows)

    def record_remote_operation_disposition(
        self,
        disposition: RemoteOperationDisposition,
    ) -> ProgramExecutionBinding:
        """Stop one orphaned Program binding without resuming its Safe graph."""

        with self._lock:
            binding = self.execution_binding(disposition.task_id)
            if (
                disposition.program_id != binding.program_id
                or disposition.phase_id != binding.phase_id
                or disposition.slice_id != (binding.slice_id or "")
            ):
                raise ProgramExecutionError(
                    "remote-operation disposition does not match execution binding"
                )

            target_status = (
                ProgramExecutionStatus.CANCELLED
                if disposition.outcome
                is RemoteOperationDispositionOutcome.CANCELLED
                else ProgramExecutionStatus.FAILED
            )
            target_phase_status = (
                PhaseStatus.CANCELLED
                if disposition.outcome
                is RemoteOperationDispositionOutcome.CANCELLED
                else PhaseStatus.FAILED
            )
            if binding.remote_disposition_ref:
                payload = self.artifacts.read_json(binding.remote_disposition_ref)
                if (
                    binding.status is target_status
                    and payload.get("audit_ref") == disposition.audit_ref
                ):
                    return binding
                raise ProgramExecutionError(
                    "execution binding already has a different remote disposition"
                )
            if binding.status not in _ACTIVE_EXECUTION_STATUSES:
                raise ProgramExecutionError("execution binding is already terminal")

            reference = self.artifacts.write_json(
                (
                    f"programs/{binding.program_id}/phases/{binding.phase_id}/executions/"
                    f"{binding.task_id}/remote-operation-disposition.json"
                ),
                disposition.model_dump(mode="json"),
            )
            self.connection.execute(
                """
                UPDATE program_executions
                SET status = ?, remote_disposition_ref = ?
                WHERE task_id = ?
                """,
                (target_status.value, reference.uri, binding.task_id),
            )
            self.connection.execute(
                """
                UPDATE program_phases SET status = ?
                WHERE program_id = ? AND phase_id = ?
                """,
                (
                    target_phase_status.value,
                    binding.program_id,
                    binding.phase_id,
                ),
            )
            self.connection.execute(
                "UPDATE programs SET status = ? WHERE program_id = ?",
                (ProgramStatus.BLOCKED.value, binding.program_id),
            )
            self.connection.commit()
            self._write_phase_execution_report(binding.program_id, binding.phase_id)
            return self.execution_binding(binding.task_id)

    def complete_phase(self, program_id: str, result: PhaseResult) -> str:
        if self.phase_status(program_id, result.phase_id) is not PhaseStatus.RUNNING:
            raise ValueError("only a running phase can be completed")
        result_ref = self.artifacts.write_json(
            f"programs/{program_id}/phases/{result.phase_id}/phase-result.json",
            result.model_dump(mode="json"),
        )
        summary = self._phase_summary(program_id, result)
        summary_ref = self.artifacts.write_text(
            f"programs/{program_id}/phases/{result.phase_id}/phase-summary.md",
            summary,
            "text/markdown",
        )
        self.connection.execute(
            """
            UPDATE program_phases
            SET status = ?, result_ref = ?, summary_ref = ?
            WHERE program_id = ? AND phase_id = ?
            """,
            (
                PhaseStatus.COMPLETED.value,
                result_ref.uri,
                summary_ref.uri,
                program_id,
                result.phase_id,
            ),
        )
        self.connection.commit()
        self.search.index_text(
            namespace="programs",
            source_type=SearchSourceType.ARTIFACT,
            source_id=f"{program_id}:{result.phase_id}",
            path=f"program:{program_id}:phase:{result.phase_id}",
            text=summary,
            metadata={
                "program_id": program_id,
                "phase_id": result.phase_id,
                "result_ref": result_ref.uri,
                "summary_ref": summary_ref.uri,
            },
        )
        if all(
            self.phase_status(program_id, phase.phase_id) is PhaseStatus.COMPLETED
            for phase in self.plan(program_id).phases
        ):
            self._set_program_status(program_id, ProgramStatus.COMPLETED)
            self.control.mark_completed(ControlEntityType.PROGRAM, program_id)
        return summary_ref.uri

    def block_phase(self, program_id: str, phase_id: str, *, reason: str) -> str:
        self.connection.execute(
            """
            UPDATE program_phases SET status = ? WHERE program_id = ? AND phase_id = ?
            """,
            (PhaseStatus.BLOCKED.value, program_id, phase_id),
        )
        self._set_program_status(program_id, ProgramStatus.BLOCKED)
        ref = self.artifacts.write_json(
            f"programs/{program_id}/phases/{phase_id}/block.json",
            {"phase_id": phase_id, "reason": reason},
        )
        return ref.uri

    def pause(self, program_id: str, *, reason: str = "") -> None:
        with self._lock:
            self.control.request_pause(ControlEntityType.PROGRAM, program_id, reason=reason)
            self._pause_active_executions(program_id, reason or "program pause requested")

    def resume(self, program_id: str) -> None:
        with self._lock:
            self.control.resume(ControlEntityType.PROGRAM, program_id)
            if self.status(program_id) is ProgramStatus.PAUSED:
                self._set_program_status(program_id, ProgramStatus.RUNNING)
            for binding in self.execution_bindings(program_id):
                if binding.status not in _ACTIVE_EXECUTION_STATUSES:
                    continue
                record = self.control.get_task(binding.task_id)
                if record is not None and record.state in {
                    ControlState.PAUSED,
                    ControlState.PAUSE_REQUESTED,
                }:
                    self.control.resume_task(binding.task_id)

    def cancel(self, program_id: str, *, reason: str = "") -> None:
        with self._lock:
            self.control.request_cancel(ControlEntityType.PROGRAM, program_id, reason=reason)
            decision = self.control.checkpoint(ControlEntityType.PROGRAM, program_id)
            if decision.action is ControlAction.CANCEL:
                self._cancel_program(program_id, reason=reason)

    def require_realign(self, program_id: str, new_requirement_hash: str) -> bool:
        with self._lock:
            row = self._program_row_required(program_id)
            if row[2] == new_requirement_hash:
                return False
            self._set_program_status(program_id, ProgramStatus.REALIGNMENT_REQUIRED)
            self._pause_active_executions(
                program_id,
                "approved requirement hash changed",
            )
            for phase_id in {
                binding.phase_id for binding in self.execution_bindings(program_id)
            }:
                self._write_phase_execution_report(program_id, phase_id)
            return True

    def _cancel_program(self, program_id: str, *, reason: str = "") -> None:
        self._set_program_status(program_id, ProgramStatus.CANCELLED)
        self.connection.execute(
            """
            UPDATE program_phases SET status = ?
            WHERE program_id = ? AND status IN (?, ?, ?)
            """,
            (
                PhaseStatus.CANCELLED.value,
                program_id,
                PhaseStatus.PENDING.value,
                PhaseStatus.PAUSED.value,
                PhaseStatus.RUNNING.value,
            ),
        )
        active = [
            binding
            for binding in self.execution_bindings(program_id)
            if binding.status in _ACTIVE_EXECUTION_STATUSES
        ]
        for binding in active:
            self.control.cancel_task(
                binding.task_id,
                reason=reason or "program cancelled",
            )
            self.connection.execute(
                """
                UPDATE program_executions SET status = ? WHERE task_id = ?
                """,
                (ProgramExecutionStatus.CANCELLED.value, binding.task_id),
            )
        self.connection.commit()
        for phase_id in {binding.phase_id for binding in active}:
            self._write_phase_execution_report(program_id, phase_id)

    def _require_execution_ready(
        self,
        program_id: str,
        current_requirement_hash: str,
    ) -> None:
        row = self._program_row_required(program_id)
        if row[2] != current_requirement_hash:
            self.require_realign(program_id, current_requirement_hash)
            raise ProgramExecutionError("program requires requirement realignment")
        status = ProgramStatus(row[1])
        if status is ProgramStatus.PAUSED:
            raise ProgramExecutionError("program is paused")
        if status is not ProgramStatus.RUNNING:
            raise ProgramExecutionError(f"program is not running: {status.value}")
        decision = self.control.checkpoint(ControlEntityType.PROGRAM, program_id)
        if decision.action is ControlAction.PAUSE:
            self._set_program_status(program_id, ProgramStatus.PAUSED)
            self._pause_active_executions(
                program_id,
                decision.record.reason or "program paused",
            )
            raise ProgramExecutionError("program is paused")
        if decision.action is ControlAction.CANCEL:
            self._cancel_program(program_id, reason=decision.record.reason)
            raise ProgramExecutionError("program is not running: cancelled")

    def _next_execution_unit(
        self,
        program_id: str,
    ) -> tuple[ProgramPhase, SlicePlan | None]:
        plan = self.plan(program_id)
        running = [
            phase
            for phase in plan.phases
            if self.phase_status(program_id, phase.phase_id) is PhaseStatus.RUNNING
        ]
        if len(running) > 1:
            raise ProgramExecutionError("program has multiple running phases")
        if running:
            phase = running[0]
        else:
            ready = self.ready_phases(program_id)
            if not ready:
                raise ProgramExecutionError("program has no dependency-ready execution unit")
            phase = ready[0]

        bindings = [
            item
            for item in self.execution_bindings(program_id)
            if item.phase_id == phase.phase_id
        ]
        if not phase.slices:
            if not bindings:
                return phase, None
            raise ProgramExecutionError("phase execution unit has already been bound")

        completed = {
            item.slice_id
            for item in bindings
            if item.status is ProgramExecutionStatus.COMPLETED and item.slice_id is not None
        }
        bound = {item.slice_id for item in bindings if item.slice_id is not None}
        for slice_plan in phase.slices:
            if slice_plan.slice_id in bound:
                continue
            if set(slice_plan.dependencies).issubset(completed):
                return phase, slice_plan
        raise ProgramExecutionError("phase has no dependency-ready execution unit")

    def _prepare_accepted_evidence(
        self,
        program_id: str,
        target_phase: ProgramPhase,
        requirement_hash: str,
    ) -> tuple[tuple[SafeContextEvidence, ...], str]:
        dependency_ids = self._prior_dependency_phase_ids(program_id, target_phase)
        if not dependency_ids:
            return (), ""

        phases: list[AcceptedPhaseEvidence] = []
        source_base_shas: set[str] = set()
        for phase_id in dependency_ids:
            row = self.connection.execute(
                """
                SELECT status, result_ref, summary_ref FROM program_phases
                WHERE program_id = ? AND phase_id = ?
                """,
                (program_id, phase_id),
            ).fetchone()
            if row is None or PhaseStatus(row[0]) is not PhaseStatus.COMPLETED:
                raise ProgramExecutionError(
                    f"accepted evidence dependency is not completed: {phase_id}"
                )
            result_ref, summary_ref = str(row[1]), str(row[2])
            if not result_ref or not summary_ref:
                raise ProgramExecutionError(
                    f"accepted evidence is missing phase artifacts: {phase_id}"
                )
            try:
                result_content = self.artifacts.read_text(result_ref)
                summary_content = self.artifacts.read_text(summary_ref)
                phase_result = PhaseResult.model_validate(json.loads(result_content))
            except Exception as exc:
                raise ProgramExecutionError(
                    f"accepted evidence phase artifacts are invalid: {phase_id}"
                ) from exc
            if phase_result.phase_id != phase_id:
                raise ProgramExecutionError("accepted evidence phase identity mismatch")
            if phase_result.reviewer_verdict != "PASS" or not phase_result.tests:
                raise ProgramExecutionError(
                    f"accepted evidence lacks PASS review or trusted tests: {phase_id}"
                )

            bindings = tuple(
                item
                for item in self.execution_bindings(program_id)
                if item.phase_id == phase_id
            )
            if not bindings or any(
                item.status is not ProgramExecutionStatus.COMPLETED
                or item.requirement_hash != requirement_hash
                for item in bindings
            ):
                raise ProgramExecutionError(
                    f"accepted evidence has incomplete or drifted executions: {phase_id}"
                )
            report_refs = {item.phase_report_ref for item in bindings}
            if len(report_refs) != 1 or not next(iter(report_refs)):
                raise ProgramExecutionError(
                    f"accepted evidence phase report is missing: {phase_id}"
                )
            phase_report_ref = next(iter(report_refs))
            try:
                report_content = self.artifacts.read_text(phase_report_ref)
                report = json.loads(report_content)
            except Exception as exc:
                raise ProgramExecutionError(
                    f"accepted evidence phase report is invalid: {phase_id}"
                ) from exc
            if (
                report.get("phase_id") != phase_id
                or report.get("phase_status") != PhaseStatus.COMPLETED.value
                or report.get("requirement_hash") != requirement_hash
            ):
                raise ProgramExecutionError(
                    f"accepted evidence phase report provenance mismatch: {phase_id}"
                )

            executions: list[AcceptedSafeExecutionEvidence] = []
            for binding in bindings:
                try:
                    execution_result_content = self.artifacts.read_text(binding.result_ref)
                    payload = json.loads(execution_result_content)
                    state = self._safe_state(payload)
                    execution = AcceptedSafeExecutionEvidence(
                        task_id=binding.task_id,
                        slice_id=binding.slice_id,
                        source_base_sha=str(
                            state.get("base_sha") or payload.get("base_sha") or ""
                        ),
                        result_ref=binding.result_ref,
                        result_sha256=hashlib.sha256(
                            execution_result_content.encode("utf-8")
                        ).hexdigest(),
                        tests_ref=str(
                            state.get("tests_ref") or payload.get("tests_ref") or ""
                        ),
                        review_ref=str(
                            state.get("review_ref") or payload.get("review_ref") or ""
                        ),
                        final_report_ref=str(
                            state.get("final_report_ref")
                            or payload.get("final_report_ref")
                            or ""
                        ),
                        reviewer_verdict=str(
                            state.get("reviewer_verdict")
                            or payload.get("reviewer_verdict")
                            or ""
                        ),
                    )
                except Exception as exc:
                    raise ProgramExecutionError(
                        f"accepted Safe execution evidence is invalid: {binding.task_id}"
                    ) from exc
                source_base_shas.add(execution.source_base_sha)
                executions.append(execution)

            phases.append(
                AcceptedPhaseEvidence(
                    phase_id=phase_id,
                    result_ref=result_ref,
                    result_sha256=hashlib.sha256(
                        result_content.encode("utf-8")
                    ).hexdigest(),
                    summary_ref=summary_ref,
                    summary_sha256=hashlib.sha256(
                        summary_content.encode("utf-8")
                    ).hexdigest(),
                    phase_report_ref=phase_report_ref,
                    phase_report_sha256=hashlib.sha256(
                        report_content.encode("utf-8")
                    ).hexdigest(),
                    summary=sanitize_text(phase_result.summary),
                    changed_paths=phase_result.changed_paths,
                    decisions=tuple(sanitize_text(item) for item in phase_result.decisions),
                    tests=phase_result.tests,
                    reviewer_verdict=phase_result.reviewer_verdict,
                    known_risks=tuple(
                        sanitize_text(item) for item in phase_result.known_risks
                    ),
                    executions=tuple(executions),
                )
            )

        if len(source_base_shas) != 1:
            raise ProgramExecutionError(
                "accepted prior-phase evidence does not share one immutable Base SHA"
            )
        source_base_sha = next(iter(source_base_shas))
        bundle = AcceptedPhaseEvidenceBundle(
            program_id=program_id,
            target_phase_id=target_phase.phase_id,
            requirement_hash=requirement_hash,
            source_base_sha=source_base_sha,
            dependency_phase_ids=dependency_ids,
            phases=tuple(phases),
        )
        content = json.dumps(
            bundle.model_dump(mode="json"),
            separators=(",", ":"),
            sort_keys=True,
            ensure_ascii=False,
        )
        evidence_hash = bundle.canonical_hash()
        if len(content) > 48_000:
            raise ProgramExecutionError(
                "accepted prior-phase evidence exceeds the bounded Safe context budget"
            )
        reference = self.artifacts.write_text(
            (
                f"programs/{program_id}/phases/{target_phase.phase_id}/"
                f"accepted-prior-phase-evidence-{evidence_hash}.json"
            ),
            content,
            "application/json",
        )
        if reference.sha256 != evidence_hash:
            raise ProgramExecutionError("accepted evidence artifact hash mismatch")
        return (
            (
                SafeContextEvidence(
                    source_ref=reference.uri,
                    sha256=evidence_hash,
                    content=content,
                ),
            ),
            source_base_sha,
        )

    def _prior_dependency_phase_ids(
        self,
        program_id: str,
        target_phase: ProgramPhase,
    ) -> tuple[str, ...]:
        plan = self.plan(program_id)
        by_id = {item.phase_id: item for item in plan.phases}
        required: set[str] = set()

        def visit(phase_id: str) -> None:
            if phase_id in required:
                return
            required.add(phase_id)
            for dependency in by_id[phase_id].dependencies:
                visit(dependency)

        for dependency in target_phase.dependencies:
            visit(dependency)
        return tuple(item.phase_id for item in plan.phases if item.phase_id in required)

    def _active_execution(self, program_id: str) -> ProgramExecutionBinding | None:
        active = [
            binding
            for binding in self.execution_bindings(program_id)
            if binding.status in _ACTIVE_EXECUTION_STATUSES
        ]
        if len(active) > 1:
            raise ProgramExecutionError("program has multiple active Safe execution bindings")
        return active[0] if active else None

    def _insert_execution(self, binding: ProgramExecutionBinding) -> None:
        unit_key = binding.slice_id or _PHASE_UNIT_KEY
        self.connection.execute(
            """
            INSERT INTO program_executions(
                program_id, phase_id, unit_key, slice_id, task_id, thread_id,
                requirement_hash, status, safe_status, result_ref,
                phase_report_ref, error_ref, accepted_evidence_ref,
                accepted_evidence_hash, expected_base_sha, remote_disposition_ref
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                binding.program_id,
                binding.phase_id,
                unit_key,
                binding.slice_id or "",
                binding.task_id,
                binding.thread_id,
                binding.requirement_hash,
                binding.status.value,
                binding.safe_status,
                binding.result_ref,
                binding.phase_report_ref,
                binding.error_ref,
                binding.accepted_evidence_ref,
                binding.accepted_evidence_hash,
                binding.expected_base_sha,
                binding.remote_disposition_ref,
            ),
        )
        self.connection.commit()

    def _record_execution_result(
        self,
        binding: ProgramExecutionBinding,
        result: dict[str, Any],
    ) -> ProgramExecutionBinding:
        state = self._safe_state(result)
        safe_status = str(state.get("status", "")).strip().lower()
        errors = state.get("safe_errors", ())
        cancelled = isinstance(errors, (list, tuple)) and "control:cancelled" in errors
        if cancelled:
            execution_status = ProgramExecutionStatus.CANCELLED
        elif safe_status == "completed":
            execution_status = ProgramExecutionStatus.COMPLETED
        elif safe_status in {"blocked", "failed"}:
            execution_status = ProgramExecutionStatus.FAILED
        elif safe_status == "awaiting_scope_approval":
            execution_status = ProgramExecutionStatus.AWAITING_SCOPE_APPROVAL
        else:
            execution_status = ProgramExecutionStatus.RUNNING

        stored_result = _JSON_VALUE_ADAPTER.dump_python(result, mode="json")
        result_ref = self.artifacts.write_json(
            (
                f"programs/{binding.program_id}/phases/{binding.phase_id}/executions/"
                f"{binding.task_id}/safe-result-{execution_status.value}.json"
            ),
            stored_result,
        )
        current = self.execution_binding(binding.task_id)
        if current.status is ProgramExecutionStatus.CANCELLED:
            execution_status = ProgramExecutionStatus.CANCELLED
        self.connection.execute(
            """
            UPDATE program_executions
            SET status = ?, safe_status = ?, result_ref = ?
            WHERE task_id = ?
            """,
            (
                execution_status.value,
                safe_status[:64],
                result_ref.uri,
                binding.task_id,
            ),
        )
        self.connection.commit()

        if execution_status is ProgramExecutionStatus.COMPLETED:
            self._complete_execution_phase_if_ready(binding.program_id, binding.phase_id)
        elif execution_status is ProgramExecutionStatus.FAILED:
            self._fail_execution_phase(binding.program_id, binding.phase_id)
        elif execution_status is ProgramExecutionStatus.CANCELLED:
            self._cancel_program(binding.program_id, reason="Safe execution cancelled")
        self._write_phase_execution_report(binding.program_id, binding.phase_id)
        return self.execution_binding(binding.task_id)

    def _record_execution_error(
        self,
        binding: ProgramExecutionBinding,
        error: Exception,
    ) -> ProgramExecutionBinding:
        error_ref = self.artifacts.write_json(
            (
                f"programs/{binding.program_id}/phases/{binding.phase_id}/executions/"
                f"{binding.task_id}/execution-error.json"
            ),
            {
                "error_type": type(error).__name__,
                "message": sanitize_text(str(error))[:2000],
            },
        )
        current = self.execution_binding(binding.task_id)
        status = current.status
        if status is not ProgramExecutionStatus.CANCELLED:
            status = ProgramExecutionStatus.FAILED
        self.connection.execute(
            """
            UPDATE program_executions SET status = ?, error_ref = ? WHERE task_id = ?
            """,
            (status.value, error_ref.uri, binding.task_id),
        )
        self.connection.commit()
        if status is ProgramExecutionStatus.FAILED:
            self._fail_execution_phase(binding.program_id, binding.phase_id)
        self._write_phase_execution_report(binding.program_id, binding.phase_id)
        return self.execution_binding(binding.task_id)

    def _complete_execution_phase_if_ready(self, program_id: str, phase_id: str) -> None:
        plan = self.plan(program_id)
        phase = next(item for item in plan.phases if item.phase_id == phase_id)
        bindings = tuple(
            binding
            for binding in self.execution_bindings(program_id)
            if binding.phase_id == phase_id
        )
        expected_count = len(phase.slices) or 1
        if len(bindings) != expected_count or any(
            binding.status is not ProgramExecutionStatus.COMPLETED
            for binding in bindings
        ):
            return
        if self.phase_status(program_id, phase_id) is not PhaseStatus.RUNNING:
            return

        artifact_refs: list[str] = []
        changed_paths: list[str] = []
        test_evidence: list[str] = []
        reviewer_verdicts: list[str] = []
        for binding in bindings:
            artifact_refs.append(binding.result_ref)
            payload = self.artifacts.read_json(binding.result_ref)
            state = self._safe_state(payload)
            verdict = state.get("reviewer_verdict")
            if isinstance(verdict, str) and verdict:
                reviewer_verdicts.append(verdict)
            paths = state.get("actual_changed_paths", ())
            if isinstance(paths, (list, tuple)):
                changed_paths.extend(str(path) for path in paths if isinstance(path, str))
            tests_ref = state.get("tests_ref")
            if isinstance(tests_ref, str) and tests_ref.startswith("artifact://"):
                test_evidence.append(f"{binding.task_id}: {tests_ref}")
            for value in (*payload.values(), *state.values()):
                if isinstance(value, str) and value.startswith("artifact://"):
                    artifact_refs.append(value)
        if (
            len(reviewer_verdicts) != len(bindings)
            or any(verdict != "PASS" for verdict in reviewer_verdicts)
            or len(test_evidence) != len(bindings)
        ):
            self._fail_execution_phase(program_id, phase_id)
            return
        self.complete_phase(
            program_id,
            PhaseResult(
                phase_id=phase_id,
                summary=(
                    f"Completed {len(bindings)} approved Discovered Safe execution "
                    "unit(s) in dependency order."
                ),
                changed_paths=tuple(dict.fromkeys(changed_paths)),
                tests=tuple(test_evidence),
                reviewer_verdict="PASS",
                artifact_refs=tuple(dict.fromkeys(artifact_refs)),
            ),
        )

    def _fail_execution_phase(self, program_id: str, phase_id: str) -> None:
        self.connection.execute(
            """
            UPDATE program_phases SET status = ? WHERE program_id = ? AND phase_id = ?
            """,
            (PhaseStatus.FAILED.value, program_id, phase_id),
        )
        self._set_program_status(program_id, ProgramStatus.BLOCKED)

    def _pause_active_executions(self, program_id: str, reason: str) -> None:
        for binding in self.execution_bindings(program_id):
            if binding.status not in _ACTIVE_EXECUTION_STATUSES:
                continue
            record = self.control.get_task(binding.task_id)
            if record is not None and record.state is ControlState.RUNNING:
                self.control.pause_task(binding.task_id, reason=reason)

    def _write_phase_execution_report(self, program_id: str, phase_id: str) -> str:
        phase = next(
            item for item in self.plan(program_id).phases if item.phase_id == phase_id
        )
        bindings = tuple(
            binding
            for binding in self.execution_bindings(program_id)
            if binding.phase_id == phase_id
        )
        reference = self.artifacts.write_json(
            f"programs/{program_id}/phases/{phase_id}/phase-execution-report.json",
            {
                "program_id": program_id,
                "program_status": self.status(program_id).value,
                "requirement_hash": self._program_row_required(program_id)[2],
                "phase_id": phase_id,
                "phase_title": phase.title,
                "phase_status": self.phase_status(program_id, phase_id).value,
                "bindings": [binding.model_dump(mode="json") for binding in bindings],
            },
        )
        self.connection.execute(
            """
            UPDATE program_executions SET phase_report_ref = ?
            WHERE program_id = ? AND phase_id = ?
            """,
            (reference.uri, program_id, phase_id),
        )
        self.connection.commit()
        return reference.uri

    @staticmethod
    def _execution_ids(
        program_id: str,
        phase_id: str,
        slice_id: str | None,
    ) -> tuple[str, str]:
        key = "\0".join((program_id, phase_id, slice_id or _PHASE_UNIT_KEY))
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:24]
        task_id = f"program-safe-{digest}"
        return task_id, f"{task_id}-thread"

    @staticmethod
    def _execution_acceptance_criteria(
        phase: ProgramPhase,
        slice_plan: SlicePlan | None,
    ) -> tuple[str, ...]:
        criteria = list(phase.acceptance_criteria)
        if slice_plan is not None:
            criteria.extend(slice_plan.acceptance_criteria)
        return tuple(dict.fromkeys(criteria))

    @staticmethod
    def _validate_execution_profiles(
        policy: SafeModePolicy,
        requested: tuple[str, ...],
    ) -> tuple[str, ...]:
        if not requested:
            raise ProgramExecutionError(
                "program execution requires at least one trusted test profile"
            )
        if len(requested) != len(set(requested)):
            raise ProgramExecutionError("program execution test profiles must be unique")
        unknown = [item for item in requested if item not in policy.profile_map()]
        if unknown:
            raise ProgramExecutionError(
                "program execution test profiles are not present in trusted policy: "
                + ", ".join(unknown)
            )
        return requested

    @staticmethod
    def _safe_state(result: dict[str, Any]) -> dict[str, Any]:
        state = result.get("state")
        return state if isinstance(state, dict) else result

    @staticmethod
    def _binding_from_row(row: tuple[Any, ...]) -> ProgramExecutionBinding:
        return ProgramExecutionBinding(
            program_id=row[0],
            phase_id=row[1],
            slice_id=row[2] or None,
            task_id=row[3],
            thread_id=row[4],
            requirement_hash=row[5],
            status=ProgramExecutionStatus(row[6]),
            safe_status=row[7],
            result_ref=row[8],
            phase_report_ref=row[9],
            error_ref=row[10],
            accepted_evidence_ref=row[11],
            accepted_evidence_hash=row[12],
            expected_base_sha=row[13],
            remote_disposition_ref=row[14],
        )

    def _ensure_execution_column(self, name: str, declaration: str) -> None:
        columns = {
            str(row[1])
            for row in self.connection.execute("PRAGMA table_info(program_executions)")
        }
        if name not in columns:
            self.connection.execute(
                f"ALTER TABLE program_executions ADD COLUMN {name} {declaration}"
            )

    def _set_program_status(self, program_id: str, status: ProgramStatus) -> None:
        self.connection.execute(
            "UPDATE programs SET status = ? WHERE program_id = ?",
            (status.value, program_id),
        )
        self.connection.commit()

    def _program_row(self, program_id: str):
        return self.connection.execute(
            """
            SELECT program_id, status, requirement_hash, plan_hash, plan_ref
            FROM programs WHERE program_id = ?
            """,
            (program_id,),
        ).fetchone()

    def _program_row_required(self, program_id: str):
        row = self._program_row(program_id)
        if row is None:
            raise KeyError(program_id)
        return row

    @staticmethod
    def _planner_context(requirement, requirement_hash: str, evidence) -> str:
        lines = [
            "# Approved requirement",
            "",
            f"Requirement hash: {requirement_hash}",
            "",
            json.dumps(
                requirement.model_dump(mode="json"),
                indent=2,
                sort_keys=True,
                ensure_ascii=False,
            ),
            "",
            "## Retrieved solution evidence",
        ]
        for hit in evidence:
            lines.extend(
                [
                    f"### {hit.path}",
                    f"score={hit.score:.2f}; source={hit.source_type.value}",
                    "```text",
                    hit.excerpt,
                    "```",
                ]
            )
        return "\n".join(lines) + "\n"

    @staticmethod
    def _program_summary(plan: ProgramPlan, plan_hash: str) -> str:
        lines = [
            f"# {plan.title}",
            "",
            f"Program: `{plan.program_id}`",
            f"Plan hash: `{plan_hash}`",
            f"Requirement hash: `{plan.requirement_hash}`",
            "",
            "## Phases",
        ]
        for phase in plan.phases:
            dependencies = ", ".join(phase.dependencies) or "none"
            lines.append(f"- {phase.phase_id}: {phase.title} (depends on: {dependencies})")
        lines.extend(["", "## Definition of done"])
        lines.extend(f"- {item}" for item in plan.definition_of_done)
        return "\n".join(lines) + "\n"

    def _phase_summary(self, program_id: str, result: PhaseResult) -> str:
        plan = self.plan(program_id)
        phase = next(item for item in plan.phases if item.phase_id == result.phase_id)
        lines = [
            f"# {phase.phase_id} - {phase.title}",
            "",
            "Status: COMPLETED",
            "",
            "## Objective",
            phase.objective,
            "",
            "## Result",
            result.summary,
            "",
            "## Changed paths",
        ]
        lines.extend(f"- {item}" for item in result.changed_paths)
        lines.extend(["", "## Decisions"])
        lines.extend(f"- {item}" for item in result.decisions)
        lines.extend(["", "## Tests"])
        lines.extend(f"- {item}" for item in result.tests)
        lines.extend(["", "## Reviewer", result.reviewer_verdict or "Not recorded"])
        lines.extend(["", "## Known risks"])
        lines.extend(f"- {item}" for item in result.known_risks)
        return "\n".join(lines) + "\n"
