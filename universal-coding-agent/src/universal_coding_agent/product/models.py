from __future__ import annotations

import hashlib
import json
from enum import StrEnum
from typing import Any

from pydantic import Field, model_validator

from universal_coding_agent.core.models import FrozenModel, PhasePlan, SlicePlan

_DECISION_KEY_PATTERN = r"^[a-z][a-z0-9_]{2,63}$"


class DocumentRole(StrEnum):
    REQUIREMENT = "requirement"
    ARCHITECTURE = "architecture"
    TECHNICAL_CONTRACT = "technical_contract"
    ERROR_LOG = "error_log"
    CONFIG_SAMPLE = "config_sample"
    REFERENCE = "reference"
    USER_INSTRUCTION = "user_instruction"


class ContextScope(StrEnum):
    PROGRAM = "program"
    PHASE = "phase"
    TASK = "task"


class ContextDocument(FrozenModel):
    document_id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")
    filename: str = Field(min_length=1, max_length=255)
    role: DocumentRole
    scope: ContextScope
    scope_id: str = Field(min_length=1, max_length=128)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    size: int = Field(ge=0)
    media_type: str = Field(min_length=1, max_length=128)
    content_ref: str = Field(pattern=r"^artifact://[a-zA-Z0-9._/-]+$")
    metadata_ref: str = Field(pattern=r"^artifact://[a-zA-Z0-9._/-]+$")


class SearchSourceType(StrEnum):
    CODE = "code"
    DOCUMENT = "document"
    ARTIFACT = "artifact"
    DECISION = "decision"


class SearchHit(FrozenModel):
    record_id: str
    source_type: SearchSourceType
    source_id: str
    path: str
    score: float = Field(ge=0)
    excerpt: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ClarificationSeverity(StrEnum):
    BLOCKING = "blocking"
    MATERIAL = "material"
    MINOR = "minor"


class RequirementStatus(StrEnum):
    NEEDS_CLARIFICATION = "needs_clarification"
    READY_FOR_APPROVAL = "ready_for_approval"
    APPROVED = "approved"
    SUPERSEDED = "superseded"


class DraftRequirement(FrozenModel):
    statement: str = Field(min_length=1, max_length=4000)
    category: str = Field(default="functional", min_length=1, max_length=64)
    evidence_refs: tuple[str, ...] = ()


class DraftAcceptanceCriterion(FrozenModel):
    statement: str = Field(min_length=1, max_length=4000)
    requirement_indexes: tuple[int, ...] = ()


class DraftClarification(FrozenModel):
    decision_key: str = Field(pattern=_DECISION_KEY_PATTERN)
    question: str = Field(min_length=1, max_length=2000)
    severity: ClarificationSeverity
    rationale: str = Field(min_length=1, max_length=2000)
    options: tuple[str, ...] = ()
    recommended_answer: str = ""
    evidence_refs: tuple[str, ...] = ()


class RequirementDraft(FrozenModel):
    title: str = Field(min_length=1, max_length=200)
    objective: str = Field(min_length=1, max_length=8000)
    requirements: tuple[DraftRequirement, ...]
    acceptance_criteria: tuple[DraftAcceptanceCriterion, ...]
    constraints: tuple[str, ...] = ()
    exclusions: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()
    clarifications: tuple[DraftClarification, ...] = ()

    @model_validator(mode="after")
    def validate_clarification_keys(self) -> RequirementDraft:
        keys = [item.decision_key for item in self.clarifications]
        if len(keys) != len(set(keys)):
            raise ValueError("clarification decision keys must be unique")
        return self


class RequirementItem(FrozenModel):
    requirement_id: str = Field(pattern=r"^R-[0-9]{3}$")
    statement: str = Field(min_length=1, max_length=4000)
    category: str = Field(min_length=1, max_length=64)
    evidence_refs: tuple[str, ...] = ()


class AcceptanceCriterion(FrozenModel):
    criterion_id: str = Field(pattern=r"^AC-[0-9]{3}$")
    statement: str = Field(min_length=1, max_length=4000)
    requirement_ids: tuple[str, ...] = ()


class ClarificationQuestion(FrozenModel):
    question_id: str = Field(pattern=r"^Q-[0-9]{3}$")
    decision_key: str = Field(pattern=_DECISION_KEY_PATTERN)
    question: str = Field(min_length=1, max_length=2000)
    severity: ClarificationSeverity
    rationale: str = Field(min_length=1, max_length=2000)
    options: tuple[str, ...] = ()
    recommended_answer: str = ""
    evidence_refs: tuple[str, ...] = ()


class RequirementContract(FrozenModel):
    alignment_id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")
    version: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=200)
    objective: str = Field(min_length=1, max_length=8000)
    requirements: tuple[RequirementItem, ...]
    acceptance_criteria: tuple[AcceptanceCriterion, ...]
    constraints: tuple[str, ...] = ()
    exclusions: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()
    clarifications: tuple[ClarificationQuestion, ...] = ()
    answers: dict[str, str] = Field(default_factory=dict)
    status: RequirementStatus

    @model_validator(mode="after")
    def validate_clarification_keys(self) -> RequirementContract:
        keys = [item.decision_key for item in self.clarifications]
        if len(keys) != len(set(keys)):
            raise ValueError("contract clarification decision keys must be unique")
        return self

    def canonical_hash(self) -> str:
        payload = self.model_dump(mode="json", exclude={"status"})
        encoded = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


class RequirementAlignmentResult(FrozenModel):
    contract: RequirementContract
    requirement_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    contract_ref: str = Field(pattern=r"^artifact://[a-zA-Z0-9._/-]+$")
    context_ref: str = Field(pattern=r"^artifact://[a-zA-Z0-9._/-]+$")
    validation_ref: str = Field(pattern=r"^artifact://[a-zA-Z0-9._/-]+$")


class ProgramStatus(StrEnum):
    DRAFT = "draft"
    AWAITING_APPROVAL = "awaiting_approval"
    RUNNING = "running"
    PAUSED = "paused"
    BLOCKED = "blocked"
    REALIGNMENT_REQUIRED = "realignment_required"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class PhaseStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    BLOCKED = "blocked"
    FAILED = "failed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class ProgramPhase(FrozenModel):
    phase_id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{1,63}$")
    title: str = Field(min_length=1, max_length=200)
    objective: str = Field(min_length=1, max_length=4000)
    dependencies: tuple[str, ...] = ()
    slices: tuple[SlicePlan, ...] = ()
    acceptance_criteria: tuple[str, ...] = ()
    stop_conditions: tuple[str, ...] = ()
    expected_components: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_slices(self) -> ProgramPhase:
        PhasePlan(
            phase_id=self.phase_id,
            title=self.title,
            objective=self.objective,
            slices=self.slices,
        )
        return self


class ProgramPlan(FrozenModel):
    program_id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")
    title: str = Field(min_length=1, max_length=200)
    objective: str = Field(min_length=1, max_length=8000)
    requirement_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    phases: tuple[ProgramPhase, ...]
    definition_of_done: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_phase_graph(self) -> ProgramPlan:
        phase_ids = [phase.phase_id for phase in self.phases]
        if not phase_ids:
            raise ValueError("program requires at least one phase")
        if len(phase_ids) != len(set(phase_ids)):
            raise ValueError("phase IDs must be unique")
        known = set(phase_ids)
        dependency_map = {phase.phase_id: set(phase.dependencies) for phase in self.phases}
        for phase in self.phases:
            unknown = dependency_map[phase.phase_id] - known
            if unknown:
                raise ValueError(
                    f"phase {phase.phase_id} has unknown dependencies: {sorted(unknown)}"
                )
            if phase.phase_id in phase.dependencies:
                raise ValueError(f"phase {phase.phase_id} cannot depend on itself")
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(phase_id: str) -> None:
            if phase_id in visiting:
                raise ValueError("phase dependency graph contains a cycle")
            if phase_id in visited:
                return
            visiting.add(phase_id)
            for dependency in dependency_map[phase_id]:
                visit(dependency)
            visiting.remove(phase_id)
            visited.add(phase_id)

        for phase_id in phase_ids:
            visit(phase_id)
        return self

    def canonical_hash(self) -> str:
        encoded = self.model_dump_json().encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


class ProgramPlanDraft(FrozenModel):
    title: str = Field(min_length=1, max_length=200)
    objective: str = Field(min_length=1, max_length=8000)
    phases: tuple[ProgramPhase, ...]
    definition_of_done: tuple[str, ...] = ()


class PhaseResult(FrozenModel):
    phase_id: str
    summary: str = Field(min_length=1, max_length=8000)
    changed_paths: tuple[str, ...] = ()
    decisions: tuple[str, ...] = ()
    tests: tuple[str, ...] = ()
    reviewer_verdict: str = ""
    known_risks: tuple[str, ...] = ()
    artifact_refs: tuple[str, ...] = ()


class ControlEntityType(StrEnum):
    TASK = "task"
    PROGRAM = "program"


class ControlState(StrEnum):
    RUNNING = "running"
    PAUSE_REQUESTED = "pause_requested"
    PAUSED = "paused"
    CANCEL_REQUESTED = "cancel_requested"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class ControlAction(StrEnum):
    CONTINUE = "continue"
    PAUSE = "pause"
    CANCEL = "cancel"


class ControlRecord(FrozenModel):
    entity_type: ControlEntityType
    entity_id: str
    state: ControlState
    reason: str = ""
    revision: int = Field(ge=0)


class ControlDecision(FrozenModel):
    action: ControlAction
    record: ControlRecord
