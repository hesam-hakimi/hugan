from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class TaskMode(StrEnum):
    OBSERVE = "observe"
    SAFE = "safe"


class TaskStatus(StrEnum):
    RECEIVED = "received"
    VALIDATING = "validating"
    SANDBOX_READY = "sandbox_ready"
    INDEXED = "indexed"
    PLANNING = "planning"
    AWAITING_PLAN_APPROVAL = "awaiting_plan_approval"
    CHECKING = "checking"
    REVIEWING = "reviewing"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"


class ReviewVerdict(StrEnum):
    PASS = "PASS"
    PASS_WITH_CONDITIONS = "PASS_WITH_CONDITIONS"
    BLOCKED = "BLOCKED"
    FAIL = "FAIL"


class RepositorySpec(FrozenModel):
    url: str = Field(min_length=1, max_length=2048)
    base_ref: str = Field(min_length=1, max_length=256)

    @field_validator("url", "base_ref")
    @classmethod
    def no_control_characters(cls, value: str) -> str:
        if any(ord(char) < 32 for char in value):
            raise ValueError("control characters are not allowed")
        return value.strip()


class TaskRequest(FrozenModel):
    task_id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")
    thread_id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")
    title: str = Field(min_length=1, max_length=200)
    objective: str = Field(min_length=1, max_length=50_000)
    repository: RepositorySpec
    mode: TaskMode = TaskMode.OBSERVE
    require_plan_approval: bool = False
    metadata: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def phase_one_is_observe_only(self) -> "TaskRequest":
        if self.mode is not TaskMode.OBSERVE:
            raise ValueError("this milestone supports observe mode only")
        return self


class ModelCapabilities(FrozenModel):
    structured_output: bool = True
    tool_calls: bool = False
    reasoning_tokens: bool = False
    actual_model_identity: bool = False


class ModelRequest(FrozenModel):
    role: str = Field(min_length=1, max_length=64)
    system_prompt: str = Field(min_length=1, max_length=100_000)
    user_prompt: str = Field(min_length=1, max_length=500_000)
    response_schema: dict[str, Any] | None = None
    max_output_tokens: int = Field(default=2400, ge=128, le=32_000)
    metadata: dict[str, str] = Field(default_factory=dict)


class ModelResponse(FrozenModel):
    content: str = ""
    structured: dict[str, Any] | None = None
    actual_model: str | None = None
    finish_reason: str | None = None
    completion_tokens: int | None = Field(default=None, ge=0)
    reasoning_tokens: int | None = Field(default=None, ge=0)
    safe_diagnostics: dict[str, str | int | bool | None] = Field(default_factory=dict)


class EvidenceItem(FrozenModel):
    kind: str = Field(min_length=1, max_length=64)
    path: str = Field(min_length=1, max_length=1024)
    summary: str = Field(min_length=1, max_length=2000)
    line_start: int | None = Field(default=None, ge=1)
    line_end: int | None = Field(default=None, ge=1)
    confidence: str = Field(default="evidenced", pattern=r"^(evidenced|inference|unknown)$")


class SlicePlan(FrozenModel):
    slice_id: str = Field(min_length=1, max_length=64)
    title: str = Field(min_length=1, max_length=200)
    objective: str = Field(min_length=1, max_length=4000)
    dependencies: tuple[str, ...] = ()
    included_scope: tuple[str, ...] = ()
    excluded_scope: tuple[str, ...] = ()
    expected_paths: tuple[str, ...] = ()
    acceptance_criteria: tuple[str, ...] = ()
    recommended_checks: tuple[str, ...] = ()
    rollback_note: str = ""
    stop_conditions: tuple[str, ...] = ()


class PhasePlan(FrozenModel):
    phase_id: str = Field(min_length=1, max_length=64)
    title: str = Field(min_length=1, max_length=200)
    objective: str = Field(min_length=1, max_length=4000)
    requirements: tuple[str, ...] = ()
    exclusions: tuple[str, ...] = ()
    evidence: tuple[EvidenceItem, ...] = ()
    slices: tuple[SlicePlan, ...] = ()
    architecture_decisions_required: tuple[str, ...] = ()
    blockers: tuple[str, ...] = ()
    final_acceptance_criteria: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_slice_graph(self) -> "PhasePlan":
        ids = [item.slice_id for item in self.slices]
        if len(ids) != len(set(ids)):
            raise ValueError("slice IDs must be unique")
        known = set(ids)
        dependency_map = {item.slice_id: set(item.dependencies) for item in self.slices}
        for item in self.slices:
            unknown = dependency_map[item.slice_id] - known
            if unknown:
                raise ValueError(
                    f"slice {item.slice_id} has unknown dependencies: {sorted(unknown)}"
                )
            if item.slice_id in item.dependencies:
                raise ValueError(f"slice {item.slice_id} cannot depend on itself")

        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(slice_id: str) -> None:
            if slice_id in visiting:
                raise ValueError("slice dependency graph contains a cycle")
            if slice_id in visited:
                return
            visiting.add(slice_id)
            for dependency in dependency_map[slice_id]:
                visit(dependency)
            visiting.remove(slice_id)
            visited.add(slice_id)

        for slice_id in ids:
            visit(slice_id)
        return self


class ReadOnlyCheck(FrozenModel):
    name: str
    passed: bool
    summary: str
    details_ref: str | None = None


class ReviewResult(FrozenModel):
    verdict: ReviewVerdict
    requirement_findings: tuple[str, ...] = ()
    scope_findings: tuple[str, ...] = ()
    security_findings: tuple[str, ...] = ()
    test_findings: tuple[str, ...] = ()
    required_actions: tuple[str, ...] = ()
    confidence: str = Field(default="medium", pattern=r"^(low|medium|high)$")


class ProjectFile(FrozenModel):
    path: str
    size: int = Field(ge=0)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    language: str
    is_test: bool = False
    symbols: tuple[str, ...] = ()
    imports: tuple[str, ...] = ()


class ProjectManifest(FrozenModel):
    repository_url: str
    base_ref: str
    base_sha: str = Field(pattern=r"^[0-9a-f]{40,64}$")
    files: tuple[ProjectFile, ...]
    instruction_paths: tuple[str, ...] = ()
    architecture_paths: tuple[str, ...] = ()
    test_paths: tuple[str, ...] = ()
    language_counts: dict[str, int] = Field(default_factory=dict)


class SandboxInfo(FrozenModel):
    sandbox_id: str
    repository_url: str
    base_ref: str
    base_sha: str
    path: str
    clean: bool


class ArtifactReference(FrozenModel):
    uri: str = Field(pattern=r"^artifact://[a-zA-Z0-9._/-]+$")
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    media_type: str
    size: int = Field(ge=0)
