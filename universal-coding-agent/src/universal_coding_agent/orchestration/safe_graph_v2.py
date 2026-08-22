from __future__ import annotations

from pathlib import Path
from typing import Any

from universal_coding_agent.core.models import ModelRequest, ProjectManifest, TaskStatus
from universal_coding_agent.core.safe_models import SafeTaskRequest, StructuredEditProposal
from universal_coding_agent.orchestration.safe_graph import SafeGraphState, SafeModeGraph
from universal_coding_agent.orchestration.structured_output import (
    StructuredOutputError,
    invoke_structured,
)


class LineAddressedSafeModeGraph(SafeModeGraph):
    """Protocol-v2 Safe Mode graph.

    The graph keeps the existing approval, sandbox, Git-diff, test, review, and rollback
    machinery. Only the model-to-edit boundary changes: old_text carries immutable line-address
    tokens rather than model-copied source text.
    """

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
            system_prompt=LINE_ADDRESSED_IMPLEMENTER_SYSTEM_PROMPT,
            user_prompt=context,
            response_schema=StructuredEditProposal.model_json_schema(),
            max_output_tokens=16_000,
            metadata={
                "task_id": task.task_id,
                "scope_hash": state["scope_hash"],
                "base_sha": task.manifest.base_sha,
                "structured_edit_protocol": "v2-line-addressed",
            },
        )
        try:
            structured = invoke_structured(
                self.services.provider,
                request,
                StructuredEditProposal,
                repair_guidance=LINE_ADDRESSED_IMPLEMENTER_REPAIR_GUIDANCE,
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
            "initial_edit_proposal_ref": proposal_ref.uri,
            "edit_proposal_ref": proposal_ref.uri,
            "events": [
                self._event(
                    "implementer",
                    f"proposed line-addressed structured edits{repair_note}",
                )
            ],
        }

    def finalize(self, state: SafeGraphState) -> dict[str, Any]:
        result = super().finalize(state)
        task = SafeTaskRequest.model_validate(state["task"])
        final_ref = result.get("final_report_ref")
        if final_ref:
            report = self.services.artifacts.read_json(final_ref)
            report["structured_edit_protocol"] = "v2-line-addressed"
            report["line_addressed_edits"] = True
            report["semantic_anchor_repair_enabled"] = False
            rewritten = self.services.artifacts.write_json(
                f"tasks/{task.task_id}/safe-final-report.json",
                report,
            )
            result["final_report_ref"] = rewritten.uri
        return result

    @staticmethod
    def route_after_tests(state: SafeGraphState) -> str:
        # Deterministic test failure is terminal evidence. Do not spend another model call asking
        # a reviewer to reinterpret a failed acceptance gate.
        if state.get("safe_errors"):
            return "finalize"
        return "review" if state.get("tests_ref") else "finalize"


LINE_ADDRESSED_IMPLEMENTER_SYSTEM_PROMPT = """You are a bounded code implementer operating in
an isolated Git sandbox. Return exactly one StructuredEditProposal JSON object. Never emit Git
patch syntax or shell commands. For approved modify files, TextReplacement.old_text is not source
text: it must be one immutable line-address token copied exactly from the supplied file state.
Use @range:<LINE_ID>..<LINE_ID> to replace complete inclusive lines, @before:<LINE_ID> to insert
complete lines before an anchor, or @after:<LINE_ID> to insert complete lines after an anchor.
LINE_ID values are supplied by the control plane and bind a line number to a content fingerprint at
the frozen Base SHA. Put the exact replacement or inserted text in new_text. Keep edits
non-overlapping, preserve line endings, and modify only approved paths and operations. Do not
delete, rename, copy, modify symlinks, stage, commit, push, create a pull request, merge, deploy,
or broaden scope. Git will generate the canonical patch after deterministic materialization."""

LINE_ADDRESSED_IMPLEMENTER_REPAIR_GUIDANCE = """Return only StructuredEditProposal JSON. Keep
all edits inside the approved path/operation manifest and use only approved test profile IDs. For
modify edits, old_text must be a valid @range, @before, or @after token copied exactly from the
line-addressed file state; never place source code or prose in old_text. Preserve complete-line
boundaries and line endings. Do not emit Git patch syntax, Markdown patch fences, or commands."""
