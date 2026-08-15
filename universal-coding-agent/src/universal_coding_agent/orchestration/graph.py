from __future__ import annotations

import hashlib
import json
import operator
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Any, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from universal_coding_agent.context.compiler import ContextCompiler
from universal_coding_agent.core.models import (
    ModelRequest,
    PhasePlan,
    ProjectManifest,
    ReviewResult,
    TaskRequest,
    TaskStatus,
)
from universal_coding_agent.providers.base import ModelProvider
from universal_coding_agent.repository.indexer import RepositoryIndexer
from universal_coding_agent.sandbox.git import GitSandboxManager
from universal_coding_agent.storage.artifacts import ArtifactStore


class TaskGraphState(TypedDict, total=False):
    task: dict[str, Any]
    status: str
    base_sha: str
    sandbox_path: str
    sandbox_id: str
    manifest_ref: str
    planner_context_ref: str
    plan_ref: str
    plan_hash: str
    plan_approved: bool | None
    checks_ref: str
    reviewer_context_ref: str
    review_ref: str
    reviewer_verdict: str
    final_report_ref: str
    safe_errors: Annotated[list[str], operator.add]
    events: Annotated[list[dict[str, Any]], operator.add]


@dataclass(frozen=True)
class GraphServices:
    provider: ModelProvider
    sandbox: GitSandboxManager
    indexer: RepositoryIndexer
    context: ContextCompiler
    artifacts: ArtifactStore


class ObserveGraph:
    def __init__(self, services: GraphServices):
        self.services = services

    def build(self, *, checkpointer: object):
        builder = StateGraph(TaskGraphState)
        builder.add_node("validate", self.validate)
        builder.add_node("sandbox", self.prepare_sandbox)
        builder.add_node("index", self.index_repository)
        builder.add_node("plan", self.plan)
        builder.add_node("approval", self.approve_plan)
        builder.add_node("checks", self.run_checks)
        builder.add_node("review", self.review)
        builder.add_node("finalize", self.finalize)
        builder.add_edge(START, "validate")
        builder.add_edge("validate", "sandbox")
        builder.add_edge("sandbox", "index")
        builder.add_edge("index", "plan")
        builder.add_conditional_edges(
            "plan",
            self.route_after_plan,
            {"approval": "approval", "checks": "checks", "finalize": "finalize"},
        )
        builder.add_conditional_edges(
            "approval",
            self.route_after_approval,
            {"checks": "checks", "finalize": "finalize"},
        )
        builder.add_edge("checks", "review")
        builder.add_edge("review", "finalize")
        builder.add_edge("finalize", END)
        return builder.compile(checkpointer=checkpointer)

    def validate(self, state: TaskGraphState) -> dict[str, Any]:
        task = TaskRequest.model_validate(state["task"])
        return {
            "status": TaskStatus.VALIDATING.value,
            "events": [self._event("validate", f"validated task {task.task_id}")],
        }

    def prepare_sandbox(self, state: TaskGraphState) -> dict[str, Any]:
        task = TaskRequest.model_validate(state["task"])
        info = self.services.sandbox.prepare(task.task_id, task.repository)
        return {
            "status": TaskStatus.SANDBOX_READY.value,
            "base_sha": info.base_sha,
            "sandbox_path": info.path,
            "sandbox_id": info.sandbox_id,
            "events": [self._event("sandbox", f"prepared immutable base {info.base_sha}")],
        }

    def index_repository(self, state: TaskGraphState) -> dict[str, Any]:
        task = TaskRequest.model_validate(state["task"])
        manifest = self.services.indexer.build_manifest(
            Path(state["sandbox_path"]),
            repository_url=task.repository.url,
            base_ref=task.repository.base_ref,
            base_sha=state["base_sha"],
        )
        reference = self.services.artifacts.write_json(
            f"tasks/{task.task_id}/repository-manifest.json", manifest.model_dump(mode="json")
        )
        return {
            "status": TaskStatus.INDEXED.value,
            "manifest_ref": reference.uri,
            "events": [self._event("index", f"indexed {len(manifest.files)} tracked files")],
        }

    def plan(self, state: TaskGraphState) -> dict[str, Any]:
        task = TaskRequest.model_validate(state["task"])
        manifest_data = self.services.artifacts.read_json(state["manifest_ref"])
        manifest = ProjectManifest.model_validate(manifest_data)
        context = self.services.context.compile_planner(Path(state["sandbox_path"]), task, manifest)
        context_ref = self.services.artifacts.write_text(
            f"tasks/{task.task_id}/planner-context.md", context, "text/markdown"
        )
        response = self.services.provider.invoke(
            ModelRequest(
                role="planner",
                system_prompt=PLANNER_SYSTEM_PROMPT,
                user_prompt=context,
                response_schema=PhasePlan.model_json_schema(),
                max_output_tokens=4000,
                metadata={"task_id": task.task_id},
            )
        )
        payload = response.structured or _parse_single_json(response.content)
        plan = PhasePlan.model_validate(payload)
        plan_ref = self.services.artifacts.write_json(
            f"tasks/{task.task_id}/phase-plan.json", plan.model_dump(mode="json")
        )
        plan_hash = hashlib.sha256(plan.model_dump_json().encode("utf-8")).hexdigest()
        status = (
            TaskStatus.AWAITING_PLAN_APPROVAL.value
            if task.require_plan_approval
            else TaskStatus.PLANNING.value
        )
        return {
            "status": status,
            "planner_context_ref": context_ref.uri,
            "plan_ref": plan_ref.uri,
            "plan_hash": plan_hash,
            "events": [self._event("planner", f"created {len(plan.slices)}-slice phase plan")],
        }

    def approve_plan(self, state: TaskGraphState) -> dict[str, Any]:
        task = TaskRequest.model_validate(state["task"])
        plan = PhasePlan.model_validate(self.services.artifacts.read_json(state["plan_ref"]))
        decision = interrupt(
            {
                "type": "plan_approval",
                "task_id": task.task_id,
                "plan_hash": state["plan_hash"],
                "phase_id": plan.phase_id,
                "slice_ids": [item.slice_id for item in plan.slices],
                "blockers": list(plan.blockers),
            }
        )
        approved = bool(decision.get("approved")) if isinstance(decision, dict) else bool(decision)
        return {
            "plan_approved": approved,
            "status": (TaskStatus.PLANNING.value if approved else TaskStatus.BLOCKED.value),
            "events": [self._event("approval", "approved" if approved else "rejected")],
        }

    def run_checks(self, state: TaskGraphState) -> dict[str, Any]:
        task = TaskRequest.model_validate(state["task"])
        checks = self.services.sandbox.read_only_git_checks(Path(state["sandbox_path"]))
        reference = self.services.artifacts.write_json(f"tasks/{task.task_id}/checks.json", checks)
        return {
            "status": TaskStatus.CHECKING.value,
            "checks_ref": reference.uri,
            "events": [self._event("checks", f"ran {len(checks)} fixed read-only checks")],
        }

    def review(self, state: TaskGraphState) -> dict[str, Any]:
        task = TaskRequest.model_validate(state["task"])
        manifest = ProjectManifest.model_validate(
            self.services.artifacts.read_json(state["manifest_ref"])
        )
        plan = PhasePlan.model_validate(self.services.artifacts.read_json(state["plan_ref"]))
        checks = self.services.artifacts.read_json(state["checks_ref"])
        context = self.services.context.compile_reviewer(
            Path(state["sandbox_path"]), task, manifest, plan, checks
        )
        context_ref = self.services.artifacts.write_text(
            f"tasks/{task.task_id}/reviewer-context.md", context, "text/markdown"
        )
        response = self.services.provider.invoke(
            ModelRequest(
                role="reviewer",
                system_prompt=REVIEWER_SYSTEM_PROMPT,
                user_prompt=context,
                response_schema=ReviewResult.model_json_schema(),
                max_output_tokens=3200,
                metadata={"task_id": task.task_id},
            )
        )
        payload = response.structured or _parse_single_json(response.content)
        review = ReviewResult.model_validate(payload)
        review_ref = self.services.artifacts.write_json(
            f"tasks/{task.task_id}/review.json", review.model_dump(mode="json")
        )
        return {
            "status": TaskStatus.REVIEWING.value,
            "reviewer_context_ref": context_ref.uri,
            "review_ref": review_ref.uri,
            "reviewer_verdict": review.verdict.value,
            "events": [self._event("reviewer", f"verdict {review.verdict}")],
        }

    def finalize(self, state: TaskGraphState) -> dict[str, Any]:
        task = TaskRequest.model_validate(state["task"])
        status = TaskStatus.COMPLETED.value
        checks = (
            self.services.artifacts.read_json(state["checks_ref"])
            if state.get("checks_ref")
            else []
        )
        plan = (
            PhasePlan.model_validate(self.services.artifacts.read_json(state["plan_ref"]))
            if state.get("plan_ref")
            else None
        )
        if (
            state.get("plan_approved") is False
            or state.get("safe_errors")
            or any(not bool(item.get("passed")) for item in checks)
            or (plan is not None and bool(plan.blockers))
            or state.get("reviewer_verdict") in {"BLOCKED", "FAIL"}
        ):
            status = TaskStatus.BLOCKED.value
        report = {
            "task_id": task.task_id,
            "thread_id": task.thread_id,
            "title": task.title,
            "status": status,
            "repository": task.repository.model_dump(mode="json"),
            "base_sha": state.get("base_sha"),
            "sandbox_id": state.get("sandbox_id"),
            "manifest_ref": state.get("manifest_ref"),
            "plan_ref": state.get("plan_ref"),
            "checks_ref": state.get("checks_ref"),
            "review_ref": state.get("review_ref"),
            "reviewer_verdict": state.get("reviewer_verdict"),
            "safe_errors": state.get("safe_errors", []),
            "source_changes": [],
            "commit_push_pr_merge_deploy": False,
        }
        reference = self.services.artifacts.write_json(
            f"tasks/{task.task_id}/final-report.json", report
        )
        return {
            "status": status,
            "final_report_ref": reference.uri,
            "events": [self._event("finalize", str(status))],
        }

    @staticmethod
    def route_after_plan(state: TaskGraphState) -> str:
        if state.get("safe_errors"):
            return "finalize"
        task = TaskRequest.model_validate(state["task"])
        return "approval" if task.require_plan_approval else "checks"

    @staticmethod
    def route_after_approval(state: TaskGraphState) -> str:
        return "checks" if state.get("plan_approved") else "finalize"

    @staticmethod
    def _event(stage: str, summary: str) -> dict[str, str]:
        return {"stage": stage, "summary": summary[:1000]}


def _parse_single_json(value: str) -> dict[str, Any]:
    text = value.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3 and lines[-1].strip() == "```":
            text = "\n".join(lines[1:-1])
            if text.lstrip().startswith("json"):
                text = text.lstrip()[4:].lstrip("\n")
    decoder = json.JSONDecoder()
    payload, end = decoder.raw_decode(text.lstrip())
    if text.lstrip()[end:].strip():
        raise ValueError("model returned trailing content after the JSON object")
    if not isinstance(payload, dict):
        raise ValueError("model output must be one JSON object")
    return payload


PLANNER_SYSTEM_PROMPT = """You are a read-only software phase planner.
Return exactly one JSON object matching the supplied schema. Build an evidence-backed
phase plan with small slices, explicit dependencies, acceptance criteria, checks,
exclusions, rollback notes, and stop conditions. Treat missing contracts as blockers.
Do not claim to modify files or run commands."""

REVIEWER_SYSTEM_PROMPT = """You are an independent read-only reviewer.
Return exactly one JSON object matching the supplied schema. Review the plan against the
original task, repository context, security boundaries, scope, and read-only check evidence.
Findings must be concise strings. Do not include private reasoning or Markdown outside the
JSON object."""
