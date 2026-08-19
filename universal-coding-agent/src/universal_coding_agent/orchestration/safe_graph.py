from __future__ import annotations

import operator
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Any, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from universal_coding_agent.context.safe_compiler import SafeContextCompiler
from universal_coding_agent.core.models import ModelRequest, ProjectManifest, TaskStatus
from universal_coding_agent.core.safe_models import (
    PatchProposal,
    SafeReviewResult,
    SafeTaskRequest,
    StructuredEditProposal,
    TestExecutionResult,
)
from universal_coding_agent.orchestration.structured_output import (
    StructuredOutputError,
    invoke_structured,
)
from universal_coding_agent.providers.base import ModelProvider
from universal_coding_agent.repository.indexer import RepositoryIndexer
from universal_coding_agent.safe.patching import SafeEditEngine, SafePatchEngine
from universal_coding_agent.safe.testing import SafeTestRunner
from universal_coding_agent.sandbox.git import GitSandboxManager
from universal_coding_agent.storage.artifacts import ArtifactStore


class SafeGraphState(TypedDict, total=False):
    task: dict[str, Any]
    status: str
    base_sha: str
    sandbox_path: str
    sandbox_id: str
    manifest_ref: str
    scope_ref: str
    scope_hash: str
    scope_approved: bool | None
    scope_approval_ref: str
    implementer_context_ref: str
    implementer_validation_ref: str
    edit_proposal_ref: str
    edit_validation_ref: str
    edit_apply_ref: str
    edits_applied: bool
    patch_proposal_ref: str
    patch_ref: str
    patch_validation_ref: str
    patch_applied: bool
    rollback_checkpoint_ref: str
    tests_ref: str
    reviewer_context_ref: str
    reviewer_validation_ref: str
    review_ref: str
    reviewer_verdict: str
    rollback_ref: str
    rolled_back: bool
    final_report_ref: str
    safe_errors: Annotated[list[str], operator.add]
    events: Annotated[list[dict[str, Any]], operator.add]


@dataclass(frozen=True)
class SafeGraphServices:
    provider: ModelProvider
    sandbox: GitSandboxManager
    indexer: RepositoryIndexer
    context: SafeContextCompiler
    artifacts: ArtifactStore
    edit_engine: SafeEditEngine
    patch_engine: SafePatchEngine
    test_runner: SafeTestRunner


class SafeModeGraph:
    """Human-approved structured edits materialized only inside an isolated Git sandbox."""

    def __init__(self, services: SafeGraphServices):
        self.services = services

    def build(self, *, checkpointer: object):
        builder = StateGraph(SafeGraphState)
        builder.add_node("validate", self.validate)
        builder.add_node("sandbox", self.prepare_sandbox)
        builder.add_node("index", self.index_repository)
        builder.add_node("scope_approval", self.approve_scope)
        builder.add_node("implement", self.implement)
        builder.add_node("apply_edits", self.apply_edits)
        builder.add_node("validate_patch", self.validate_patch)
        builder.add_node("tests", self.run_tests)
        builder.add_node("review", self.review)
        builder.add_node("finalize", self.finalize)

        builder.add_edge(START, "validate")
        builder.add_edge("validate", "sandbox")
        builder.add_conditional_edges(
            "sandbox",
            self.route_after_sandbox,
            {"index": "index", "finalize": "finalize"},
        )
        builder.add_edge("index", "scope_approval")
        builder.add_conditional_edges(
            "scope_approval",
            self.route_after_scope_approval,
            {"implement": "implement", "finalize": "finalize"},
        )
        builder.add_conditional_edges(
            "implement",
            self.route_after_implement,
            {"apply_edits": "apply_edits", "finalize": "finalize"},
        )
        builder.add_conditional_edges(
            "apply_edits",
            self.route_after_apply_edits,
            {"validate_patch": "validate_patch", "finalize": "finalize"},
        )
        builder.add_conditional_edges(
            "validate_patch",
            self.route_after_patch_validation,
            {"tests": "tests", "finalize": "finalize"},
        )
        builder.add_conditional_edges(
            "tests",
            self.route_after_tests,
            {"review": "review", "finalize": "finalize"},
        )
        builder.add_edge("review", "finalize")
        builder.add_edge("finalize", END)
        return builder.compile(checkpointer=checkpointer)

    def validate(self, state: SafeGraphState) -> dict[str, Any]:
        task = SafeTaskRequest.model_validate(state["task"])
        scope_ref = self.services.artifacts.write_json(
            f"tasks/{task.task_id}/approved-change-manifest.json",
            task.manifest.model_dump(mode="json"),
        )
        return {
            "status": TaskStatus.VALIDATING.value,
            "scope_ref": scope_ref.uri,
            "scope_hash": task.manifest.canonical_hash(),
            "edits_applied": False,
            "patch_applied": False,
            "events": [self._event("validate", f"validated safe task {task.task_id}")],
        }

    def prepare_sandbox(self, state: SafeGraphState) -> dict[str, Any]:
        task = SafeTaskRequest.model_validate(state["task"])
        try:
            info = self.services.sandbox.prepare(task.task_id, task.repository)
        except (OSError, ValueError, RuntimeError) as exc:
            return {
                "status": TaskStatus.FAILED.value,
                "safe_errors": [f"sandbox:{type(exc).__name__}"],
                "events": [self._event("sandbox", "failed safely")],
            }
        if info.base_sha != task.manifest.base_sha:
            return {
                "status": TaskStatus.BLOCKED.value,
                "base_sha": info.base_sha,
                "sandbox_path": info.path,
                "sandbox_id": info.sandbox_id,
                "safe_errors": ["scope:base_sha_mismatch"],
                "events": [self._event("sandbox", "approved base SHA does not match")],
            }
        return {
            "status": TaskStatus.SANDBOX_READY.value,
            "base_sha": info.base_sha,
            "sandbox_path": info.path,
            "sandbox_id": info.sandbox_id,
            "events": [self._event("sandbox", f"prepared immutable base {info.base_sha}")],
        }

    def index_repository(self, state: SafeGraphState) -> dict[str, Any]:
        task = SafeTaskRequest.model_validate(state["task"])
        manifest = self.services.indexer.build_manifest(
            Path(state["sandbox_path"]),
            repository_url=task.repository.url,
            base_ref=task.repository.base_ref,
            base_sha=state["base_sha"],
        )
        reference = self.services.artifacts.write_json(
            f"tasks/{task.task_id}/repository-manifest.json",
            manifest.model_dump(mode="json"),
        )
        return {
            "status": "awaiting_scope_approval",
            "manifest_ref": reference.uri,
            "events": [self._event("index", f"indexed {len(manifest.files)} tracked files")],
        }

    def approve_scope(self, state: SafeGraphState) -> dict[str, Any]:
        task = SafeTaskRequest.model_validate(state["task"])
        decision = interrupt(
            {
                "type": "safe_scope_approval",
                "task_id": task.task_id,
                "base_sha": task.manifest.base_sha,
                "plan_hash": task.manifest.plan_hash,
                "scope_hash": state["scope_hash"],
                "allowed_changes": [
                    item.model_dump(mode="json") for item in task.manifest.allowed_changes
                ],
                "denied_prefixes": list(task.manifest.denied_prefixes),
                "test_profiles": list(task.manifest.test_profiles),
                "acceptance_criteria": list(task.manifest.acceptance_criteria),
            }
        )
        approved = bool(decision.get("approved")) if isinstance(decision, dict) else bool(decision)
        approval_ref = self.services.artifacts.write_json(
            f"tasks/{task.task_id}/scope-approval.json",
            {
                "approved": approved,
                "scope_hash": state["scope_hash"],
                "base_sha": task.manifest.base_sha,
                "plan_hash": task.manifest.plan_hash,
            },
        )
        return {
            "scope_approved": approved,
            "scope_approval_ref": approval_ref.uri,
            "status": TaskStatus.PLANNING.value if approved else TaskStatus.BLOCKED.value,
            "events": [self._event("scope_approval", "approved" if approved else "rejected")],
        }

    def implement(self, state: SafeGraphState) -> dict[str, Any]:
        task = SafeTaskRequest.model_validate(state["task"])
        project_manifest = ProjectManifest.model_validate(
            self.services.artifacts.read_json(state["manifest_ref"])
        )
        context = self.services.context.compile_implementer(
            Path(state["sandbox_path"]),
            task,
            project_manifest,
        )
        context_ref = self.services.artifacts.write_text(
            f"tasks/{task.task_id}/implementer-context.md",
            context,
            "text/markdown",
        )
        request = ModelRequest(
            role="implementer",
            system_prompt=IMPLEMENTER_SYSTEM_PROMPT,
            user_prompt=context,
            response_schema=StructuredEditProposal.model_json_schema(),
            max_output_tokens=16_000,
            metadata={
                "task_id": task.task_id,
                "scope_hash": state["scope_hash"],
                "base_sha": task.manifest.base_sha,
                "structured_edit_protocol": "v1",
            },
        )
        try:
            structured = invoke_structured(
                self.services.provider,
                request,
                StructuredEditProposal,
                repair_guidance=IMPLEMENTER_REPAIR_GUIDANCE,
            )
        except StructuredOutputError as exc:
            validation_ref = self.services.artifacts.write_json(
                f"tasks/{task.task_id}/implementer-model-validation.json",
                exc.diagnostics,
            )
            return {
                "status": TaskStatus.FAILED.value,
                "implementer_context_ref": context_ref.uri,
                "implementer_validation_ref": validation_ref.uri,
                "safe_errors": [f"implementer:{exc.code}"],
                "events": [self._event("implementer", f"failed safely: {exc.code}")],
            }

        proposal = structured.value
        validation_ref = self.services.artifacts.write_json(
            f"tasks/{task.task_id}/implementer-model-validation.json",
            structured.diagnostics,
        )
        proposal_ref = self.services.artifacts.write_json(
            f"tasks/{task.task_id}/edit-proposal.json",
            proposal.model_dump(mode="json"),
        )
        repair_note = " after schema repair" if structured.repair_used else ""
        return {
            "status": TaskStatus.PLANNING.value,
            "implementer_context_ref": context_ref.uri,
            "implementer_validation_ref": validation_ref.uri,
            "edit_proposal_ref": proposal_ref.uri,
            "events": [
                self._event("implementer", f"proposed structured edits{repair_note}")
            ],
        }

    def apply_edits(self, state: SafeGraphState) -> dict[str, Any]:
        task = SafeTaskRequest.model_validate(state["task"])
        proposal = StructuredEditProposal.model_validate(
            self.services.artifacts.read_json(state["edit_proposal_ref"])
        )
        validation = self.services.edit_engine.validate(
            Path(state["sandbox_path"]),
            task.manifest,
            proposal,
        )
        validation_ref = self.services.artifacts.write_json(
            f"tasks/{task.task_id}/edit-validation.json",
            validation.model_dump(mode="json"),
        )
        if not validation.valid:
            return {
                "status": TaskStatus.BLOCKED.value,
                "edit_validation_ref": validation_ref.uri,
                "safe_errors": ["edit:validation_failed"],
                "events": [self._event("edit_validation", "rejected")],
            }

        checkpoint_ref = self.services.artifacts.write_json(
            f"tasks/{task.task_id}/rollback-checkpoint.json",
            {
                "base_sha": task.manifest.base_sha,
                "plan_hash": task.manifest.plan_hash,
                "scope_hash": state["scope_hash"],
                "changed_paths": list(proposal.changed_paths),
                "pre_apply_status": [],
                "materialization": "structured_edits_v1",
            },
        )
        try:
            result = self.services.edit_engine.apply(
                Path(state["sandbox_path"]),
                task.manifest,
                proposal,
            )
        except (OSError, ValueError, RuntimeError) as exc:
            return {
                "status": TaskStatus.FAILED.value,
                "edit_validation_ref": validation_ref.uri,
                "rollback_checkpoint_ref": checkpoint_ref.uri,
                "safe_errors": [f"edit_apply:{type(exc).__name__}"],
                "events": [self._event("edit_apply", "failed safely")],
            }
        apply_ref = self.services.artifacts.write_json(
            f"tasks/{task.task_id}/edit-apply.json",
            {
                "changed_paths": list(result.changed_paths),
                "status_lines": list(result.status_lines),
            },
        )
        return {
            "status": TaskStatus.CHECKING.value,
            "edit_validation_ref": validation_ref.uri,
            "rollback_checkpoint_ref": checkpoint_ref.uri,
            "edit_apply_ref": apply_ref.uri,
            "edits_applied": True,
            "patch_applied": True,
            "events": [
                self._event("edit_apply", "materialized approved structured edits in sandbox")
            ],
        }

    def validate_patch(self, state: SafeGraphState) -> dict[str, Any]:
        task = SafeTaskRequest.model_validate(state["task"])
        edit_proposal = StructuredEditProposal.model_validate(
            self.services.artifacts.read_json(state["edit_proposal_ref"])
        )
        try:
            proposal = self.services.patch_engine.capture_worktree_proposal(
                Path(state["sandbox_path"]),
                task.manifest,
                edit_proposal,
            )
        except (OSError, ValueError, RuntimeError) as exc:
            return {
                "status": TaskStatus.FAILED.value,
                "safe_errors": [f"patch_capture:{type(exc).__name__}"],
                "events": [self._event("patch_capture", "failed safely")],
            }

        proposal_ref = self.services.artifacts.write_json(
            f"tasks/{task.task_id}/patch-proposal.json",
            proposal.model_dump(mode="json"),
        )
        patch_ref = self.services.artifacts.write_text(
            f"tasks/{task.task_id}/proposed.patch",
            proposal.unified_diff,
            "text/x-diff",
        )
        result = self.services.patch_engine.validate_materialized(
            Path(state["sandbox_path"]),
            task.manifest,
            proposal,
        )
        result_ref = self.services.artifacts.write_json(
            f"tasks/{task.task_id}/patch-validation.json",
            result.model_dump(mode="json"),
        )
        response: dict[str, Any] = {
            "patch_proposal_ref": proposal_ref.uri,
            "patch_ref": patch_ref.uri,
            "patch_validation_ref": result_ref.uri,
            "events": [
                self._event(
                    "patch_validation",
                    "validated canonical Git diff" if result.valid else "rejected canonical diff",
                )
            ],
        }
        if result.valid:
            response["status"] = TaskStatus.CHECKING.value
        else:
            response["status"] = TaskStatus.BLOCKED.value
            response["safe_errors"] = ["patch:validation_failed"]
        return response

    def run_tests(self, state: SafeGraphState) -> dict[str, Any]:
        task = SafeTaskRequest.model_validate(state["task"])
        try:
            results = self.services.test_runner.run_profiles(
                Path(state["sandbox_path"]),
                task.policy,
                task.manifest.test_profiles,
            )
            in_scope, actual_paths = self.services.patch_engine.verify_changed_paths(
                Path(state["sandbox_path"]),
                tuple(item.path for item in task.manifest.allowed_changes),
            )
        except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
            return {
                "status": TaskStatus.FAILED.value,
                "safe_errors": [f"tests:{type(exc).__name__}"],
                "events": [self._event("tests", "failed safely")],
            }
        reference = self.services.artifacts.write_json(
            f"tasks/{task.task_id}/test-results.json",
            {
                "results": [item.model_dump(mode="json") for item in results],
                "actual_changed_paths": list(actual_paths),
                "scope_intact": in_scope,
            },
        )
        errors: list[str] = []
        if not all(item.passed for item in results):
            errors.append("tests:focused_profile_failed")
        if not in_scope:
            errors.append("tests:out_of_scope_workspace_change")
        response: dict[str, Any] = {
            "status": TaskStatus.CHECKING.value,
            "tests_ref": reference.uri,
            "events": [self._event("tests", f"ran {len(results)} fixed profiles")],
        }
        if errors:
            response["safe_errors"] = errors
        return response

    def review(self, state: SafeGraphState) -> dict[str, Any]:
        task = SafeTaskRequest.model_validate(state["task"])
        proposal = PatchProposal.model_validate(
            self.services.artifacts.read_json(state["patch_proposal_ref"])
        )
        tests_payload = self.services.artifacts.read_json(state["tests_ref"])
        tests = tuple(
            TestExecutionResult.model_validate(item)
            for item in tests_payload.get("results", [])
        )
        actual_paths = tuple(tests_payload.get("actual_changed_paths", []))
        context = self.services.context.compile_reviewer(
            Path(state["sandbox_path"]),
            task,
            proposal,
            tests,
            actual_paths,
        )
        context_ref = self.services.artifacts.write_text(
            f"tasks/{task.task_id}/safe-reviewer-context.md",
            context,
            "text/markdown",
        )
        request = ModelRequest(
            role="reviewer",
            system_prompt=SAFE_REVIEWER_SYSTEM_PROMPT,
            user_prompt=context,
            response_schema=SafeReviewResult.model_json_schema(),
            max_output_tokens=4_000,
            metadata={
                "task_id": task.task_id,
                "scope_hash": state["scope_hash"],
            },
        )
        try:
            structured = invoke_structured(
                self.services.provider,
                request,
                SafeReviewResult,
                repair_guidance=SAFE_REVIEWER_REPAIR_GUIDANCE,
            )
        except StructuredOutputError as exc:
            validation_ref = self.services.artifacts.write_json(
                f"tasks/{task.task_id}/safe-reviewer-model-validation.json",
                exc.diagnostics,
            )
            return {
                "status": TaskStatus.FAILED.value,
                "reviewer_context_ref": context_ref.uri,
                "reviewer_validation_ref": validation_ref.uri,
                "safe_errors": [f"reviewer:{exc.code}"],
                "events": [self._event("reviewer", f"failed safely: {exc.code}")],
            }
        review_result = structured.value
        validation_ref = self.services.artifacts.write_json(
            f"tasks/{task.task_id}/safe-reviewer-model-validation.json",
            structured.diagnostics,
        )
        review_ref = self.services.artifacts.write_json(
            f"tasks/{task.task_id}/safe-review.json",
            review_result.model_dump(mode="json"),
        )
        return {
            "status": TaskStatus.REVIEWING.value,
            "reviewer_context_ref": context_ref.uri,
            "reviewer_validation_ref": validation_ref.uri,
            "review_ref": review_ref.uri,
            "reviewer_verdict": review_result.verdict.value,
            "events": [
                self._event("reviewer", f"verdict {review_result.verdict.value}")
            ],
        }

    def finalize(self, state: SafeGraphState) -> dict[str, Any]:
        task = SafeTaskRequest.model_validate(state["task"])
        tests_payload = (
            self.services.artifacts.read_json(state["tests_ref"])
            if state.get("tests_ref")
            else {"results": [], "scope_intact": False, "actual_changed_paths": []}
        )
        tests_passed = all(
            bool(item.get("passed")) for item in tests_payload.get("results", [])
        )
        scope_intact = bool(tests_payload.get("scope_intact", False))
        safe_errors = list(state.get("safe_errors", []))
        successful = (
            state.get("scope_approved") is True
            and state.get("patch_applied") is True
            and state.get("patch_validation_ref") is not None
            and not safe_errors
            and tests_passed
            and scope_intact
            and state.get("reviewer_verdict") == "PASS"
        )

        rolled_back = False
        rollback_ref: str | None = None
        if state.get("patch_applied") and not successful:
            proposal = StructuredEditProposal.model_validate(
                self.services.artifacts.read_json(state["edit_proposal_ref"])
            )
            rolled_back = self.services.edit_engine.restore(
                Path(state["sandbox_path"]),
                task.manifest,
                proposal.changed_paths,
            )
            if not rolled_back:
                safe_errors.append("rollback:incomplete")
            reference = self.services.artifacts.write_json(
                f"tasks/{task.task_id}/rollback-result.json",
                {
                    "attempted": True,
                    "succeeded": rolled_back,
                    "remaining_status": list(
                        self.services.edit_engine.status_lines(Path(state["sandbox_path"]))
                    ),
                    "method": "deterministic_worktree_restore",
                },
            )
            rollback_ref = reference.uri

        status = TaskStatus.COMPLETED.value if successful else TaskStatus.BLOCKED.value
        report = {
            "task_id": task.task_id,
            "thread_id": task.thread_id,
            "title": task.title,
            "status": status,
            "repository": task.repository.model_dump(mode="json"),
            "base_sha": state.get("base_sha"),
            "plan_hash": task.manifest.plan_hash,
            "scope_hash": state.get("scope_hash"),
            "scope_approved": state.get("scope_approved"),
            "sandbox_id": state.get("sandbox_id"),
            "manifest_ref": state.get("manifest_ref"),
            "scope_ref": state.get("scope_ref"),
            "scope_approval_ref": state.get("scope_approval_ref"),
            "implementer_context_ref": state.get("implementer_context_ref"),
            "implementer_validation_ref": state.get("implementer_validation_ref"),
            "structured_edit_protocol": "v1",
            "edit_proposal_ref": state.get("edit_proposal_ref"),
            "edit_validation_ref": state.get("edit_validation_ref"),
            "edit_apply_ref": state.get("edit_apply_ref"),
            "model_authored_patch": False,
            "canonical_patch_generated_by": "git",
            "patch_proposal_ref": state.get("patch_proposal_ref"),
            "patch_ref": state.get("patch_ref"),
            "patch_validation_ref": state.get("patch_validation_ref"),
            "patch_repair_used": False,
            "rollback_checkpoint_ref": state.get("rollback_checkpoint_ref"),
            "tests_ref": state.get("tests_ref"),
            "reviewer_context_ref": state.get("reviewer_context_ref"),
            "reviewer_validation_ref": state.get("reviewer_validation_ref"),
            "review_ref": state.get("review_ref"),
            "reviewer_verdict": state.get("reviewer_verdict"),
            "safe_errors": safe_errors,
            "approved_changed_paths": tests_payload.get("actual_changed_paths", []),
            "sandbox_patch_retained": successful,
            "rolled_back": rolled_back,
            "rollback_ref": rollback_ref,
            "source_repository_modified": False,
            "stage_commit_push_pr_merge_deploy": False,
        }
        reference = self.services.artifacts.write_json(
            f"tasks/{task.task_id}/safe-final-report.json",
            report,
        )
        response: dict[str, Any] = {
            "status": status,
            "rolled_back": rolled_back,
            "rollback_ref": rollback_ref,
            "final_report_ref": reference.uri,
            "events": [self._event("finalize", status)],
        }
        if "rollback:incomplete" in safe_errors and "rollback:incomplete" not in state.get(
            "safe_errors", []
        ):
            response["safe_errors"] = ["rollback:incomplete"]
        return response

    @staticmethod
    def route_after_sandbox(state: SafeGraphState) -> str:
        return "finalize" if state.get("safe_errors") else "index"

    @staticmethod
    def route_after_scope_approval(state: SafeGraphState) -> str:
        return "implement" if state.get("scope_approved") else "finalize"

    @staticmethod
    def route_after_implement(state: SafeGraphState) -> str:
        return "finalize" if state.get("safe_errors") else "apply_edits"

    @staticmethod
    def route_after_apply_edits(state: SafeGraphState) -> str:
        return "validate_patch" if state.get("patch_applied") else "finalize"

    @staticmethod
    def route_after_patch_validation(state: SafeGraphState) -> str:
        return "finalize" if state.get("safe_errors") else "tests"

    @staticmethod
    def route_after_tests(state: SafeGraphState) -> str:
        return "review" if state.get("tests_ref") else "finalize"

    @staticmethod
    def _event(stage: str, summary: str) -> dict[str, str]:
        return {"stage": stage, "summary": summary[:1000]}


IMPLEMENTER_SYSTEM_PROMPT = """You are a bounded code implementer operating in an
isolated Git sandbox. Return exactly one StructuredEditProposal JSON object. Describe semantic
text edits only; never emit Git patch syntax or shell commands. For each approved modify path,
use exact non-overlapping old_text anchors copied verbatim from the supplied base-file state and
provide the replacement new_text. Each old_text anchor must occur exactly once. For an approved
create path, provide complete UTF-8 text content. Do not delete, rename, copy, modify symlinks,
stage, commit, push, create a pull request, merge, deploy, or broaden scope. The control plane
will materialize edits deterministically and Git will generate the canonical diff."""

IMPLEMENTER_REPAIR_GUIDANCE = """Return only StructuredEditProposal JSON. Keep every edit
inside the approved path/operation manifest and use only approved test profile IDs. Do not emit
unified_diff, diff --git, ---/+++, @@ hunks, Markdown patch fences, or commands. For modify edits,
old_text must be an exact unique substring from the supplied base-file state and replacements
within one file must not overlap."""

SAFE_REVIEWER_SYSTEM_PROMPT = """You are an independent Safe Mode reviewer. Return exactly
one SafeReviewResult JSON object. Review the original requirement, approved scope, the canonical
Git diff generated by the tool from deterministically materialized structured edits, focused test
results, compatibility, and security boundaries. Return PASS only when no condition or follow-up
remains. Never approve out-of-scope paths or publication actions."""

SAFE_REVIEWER_REPAIR_GUIDANCE = """Keep every finding field as an array of concise strings.
Use only the declared verdict and confidence enums. Preserve substantive findings while
correcting JSON structure and field types."""
