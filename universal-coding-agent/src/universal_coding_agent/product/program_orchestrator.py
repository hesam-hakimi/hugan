from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from universal_coding_agent.core.models import ModelRequest
from universal_coding_agent.orchestration.structured_output import invoke_structured
from universal_coding_agent.product.models import (
    ControlAction,
    ControlEntityType,
    PhaseResult,
    PhaseStatus,
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
from universal_coding_agent.storage.artifacts import ArtifactStore

_PROGRAM_SYSTEM_PROMPT = """You are a software delivery program planner.
Return exactly one JSON object matching the supplied schema. Decompose the approved
requirement into the smallest coherent phases that can be delivered and reviewed safely.
Use explicit phase dependencies, acceptance criteria, expected components, and stop
conditions. Do not invent business requirements. Preserve security, compatibility, data
migration, testing, documentation, and rollback concerns when the approved contract requires
them. Do not write code or claim execution has happened."""

_PROGRAM_REPAIR_GUIDANCE = """Preserve the proposed program while correcting JSON structure.
Every dependency must be an exact phase_id declared in the same response. Remove dependency
cycles and keep at least one phase."""


class ProgramOrchestrator:
    """Persistent program/phase orchestration above Safe Mode.

    It does not bypass Safe Mode. It determines which phase is allowed to start, records the
    phase result, writes a durable phase report, and stops future phases when paused, cancelled,
    blocked, or when the approved requirement hash changes.
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
        self.connection.commit()

    def close(self) -> None:
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
        structured = invoke_structured(
            self.provider,
            request,
            ProgramPlanDraft,
            repair_guidance=_PROGRAM_REPAIR_GUIDANCE,
        )
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
        row = self._program_row_required(program_id)
        return ProgramPlan.model_validate(self.artifacts.read_json(row[4]))

    def status(self, program_id: str) -> ProgramStatus:
        row = self._program_row_required(program_id)
        return ProgramStatus(row[1])

    def phase_status(self, program_id: str, phase_id: str) -> PhaseStatus:
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
        self.control.request_pause(ControlEntityType.PROGRAM, program_id, reason=reason)

    def resume(self, program_id: str) -> None:
        self.control.resume(ControlEntityType.PROGRAM, program_id)
        if self.status(program_id) is ProgramStatus.PAUSED:
            self._set_program_status(program_id, ProgramStatus.RUNNING)

    def cancel(self, program_id: str, *, reason: str = "") -> None:
        self.control.request_cancel(ControlEntityType.PROGRAM, program_id, reason=reason)
        decision = self.control.checkpoint(ControlEntityType.PROGRAM, program_id)
        if decision.action is ControlAction.CANCEL:
            self._cancel_program(program_id)

    def require_realign(self, program_id: str, new_requirement_hash: str) -> bool:
        row = self._program_row_required(program_id)
        if row[2] == new_requirement_hash:
            return False
        self._set_program_status(program_id, ProgramStatus.REALIGNMENT_REQUIRED)
        return True

    def _cancel_program(self, program_id: str) -> None:
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
        self.connection.commit()

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
