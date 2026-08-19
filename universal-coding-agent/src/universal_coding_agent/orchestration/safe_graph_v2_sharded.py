from __future__ import annotations

from pathlib import Path
from typing import Any

from universal_coding_agent.context.sharded_line_edit_compiler import (
    ShardedLineAddressedContextCompiler,
)
from universal_coding_agent.core.models import ModelRequest, ProjectManifest, TaskStatus
from universal_coding_agent.core.safe_models import SafeTaskRequest, StructuredEditProposal
from universal_coding_agent.orchestration.safe_graph import SafeGraphState
from universal_coding_agent.orchestration.safe_graph_v2 import (
    LINE_ADDRESSED_IMPLEMENTER_REPAIR_GUIDANCE,
    LINE_ADDRESSED_IMPLEMENTER_SYSTEM_PROMPT,
    LineAddressedSafeModeGraph,
)
from universal_coding_agent.orchestration.structured_output import (
    StructuredOutputError,
    invoke_structured,
)


class ShardedLineAddressedSafeModeGraph(LineAddressedSafeModeGraph):
    """Protocol-v2 graph with one bounded implementer call per approved file.

    The original v2 model boundary exposed every approved file and every line token in one
    prompt. Real multi-file tasks showed that a model could invent or cross-wire an address
    while the deterministic engine correctly rejected it. This graph removes that failure
    surface by making each model call file-local, validating that shard before combining it,
    and permitting at most one same-file address correction before failing closed.
    """

    def implement(self, state: SafeGraphState) -> dict[str, Any]:
        task = SafeTaskRequest.model_validate(state["task"])
        project_manifest = ProjectManifest.model_validate(
            self.services.artifacts.read_json(state["manifest_ref"])
        )
        root = Path(state["sandbox_path"])
        compiler = self.services.context
        if not isinstance(compiler, ShardedLineAddressedContextCompiler):
            return {
                "status": TaskStatus.FAILED.value,
                "safe_errors": ["implementer:sharded_context_unavailable"],
                "events": [self._event("implementer", "sharded context unavailable")],
            }

        combined_edits = []
        requested_profiles: list[str] = []
        assumptions: list[str] = []
        summaries: list[str] = []
        shard_records: list[dict[str, Any]] = []
        aggregate_attempts: list[dict[str, Any]] = []
        context_lines = ["# File-sharded implementer contexts"]
        schema_repair_used = False
        address_correction_used = False

        for index, entry in enumerate(task.manifest.allowed_changes, start=1):
            context = compiler.compile_implementer_for_path(
                root,
                task,
                project_manifest,
                entry.path,
            )
            context_ref = self.services.artifacts.write_text(
                f"tasks/{task.task_id}/implementer-context-{index:03d}.md",
                context,
                "text/markdown",
            )
            context_lines.append(f"- {entry.path}: {context_ref.uri}")

            initial = self._invoke_shard(
                task,
                state,
                entry.path,
                index,
                context,
                phase="initial",
            )
            if isinstance(initial, StructuredOutputError):
                aggregate_ref = self._write_aggregate_validation(
                    task.task_id,
                    shard_records,
                    aggregate_attempts,
                    schema_repair_used,
                    address_correction_used,
                    failure={"path": entry.path, "code": initial.code},
                )
                context_index_ref = self.services.artifacts.write_text(
                    f"tasks/{task.task_id}/implementer-context.md",
                    "\n".join(context_lines) + "\n",
                    "text/markdown",
                )
                return {
                    "status": TaskStatus.FAILED.value,
                    "implementer_context_ref": context_index_ref.uri,
                    "implementer_validation_ref": aggregate_ref.uri,
                    "safe_errors": [f"implementer:{initial.code}"],
                    "events": [
                        self._event(
                            "implementer",
                            f"file shard failed safely for {entry.path}: {initial.code}",
                        )
                    ],
                }

            structured, diagnostics_ref = initial
            schema_repair_used = schema_repair_used or structured.repair_used
            self._collect_attempts(
                aggregate_attempts,
                structured.diagnostics,
                entry.path,
                "initial",
            )
            proposal = structured.value
            errors = self._validate_shard(root, task, proposal, entry.path, entry.operation)
            shard_record: dict[str, Any] = {
                "path": entry.path,
                "initial_validation_ref": diagnostics_ref.uri,
                "initial_errors": list(errors),
                "address_correction_used": False,
            }

            if errors:
                address_correction_used = True
                shard_record["address_correction_used"] = True
                correction_context = compiler.compile_address_correction_for_path(
                    root,
                    task,
                    project_manifest,
                    entry.path,
                    proposal,
                    errors,
                )
                correction_context_ref = self.services.artifacts.write_text(
                    f"tasks/{task.task_id}/implementer-address-correction-context-{index:03d}.md",
                    correction_context,
                    "text/markdown",
                )
                corrected = self._invoke_shard(
                    task,
                    state,
                    entry.path,
                    index,
                    correction_context,
                    phase="address_correction",
                )
                shard_record["address_correction_context_ref"] = correction_context_ref.uri
                if isinstance(corrected, StructuredOutputError):
                    shard_records.append(shard_record)
                    aggregate_ref = self._write_aggregate_validation(
                        task.task_id,
                        shard_records,
                        aggregate_attempts,
                        schema_repair_used,
                        address_correction_used,
                        failure={"path": entry.path, "code": corrected.code},
                    )
                    context_index_ref = self.services.artifacts.write_text(
                        f"tasks/{task.task_id}/implementer-context.md",
                        "\n".join(context_lines) + "\n",
                        "text/markdown",
                    )
                    return {
                        "status": TaskStatus.FAILED.value,
                        "implementer_context_ref": context_index_ref.uri,
                        "implementer_validation_ref": aggregate_ref.uri,
                        "safe_errors": [f"implementer_address_correction:{corrected.code}"],
                        "events": [
                            self._event(
                                "implementer",
                                f"address correction failed safely for {entry.path}",
                            )
                        ],
                    }

                corrected_structured, corrected_diagnostics_ref = corrected
                schema_repair_used = (
                    schema_repair_used or corrected_structured.repair_used
                )
                self._collect_attempts(
                    aggregate_attempts,
                    corrected_structured.diagnostics,
                    entry.path,
                    "address_correction",
                )
                corrected_proposal = corrected_structured.value
                corrected_errors = list(
                    self._validate_shard(
                        root,
                        task,
                        corrected_proposal,
                        entry.path,
                        entry.operation,
                    )
                )
                if set(corrected_proposal.requested_test_profiles) != set(
                    proposal.requested_test_profiles
                ):
                    corrected_errors.append(
                        "address correction changed the requested test-profile set"
                    )
                shard_record["address_correction_validation_ref"] = (
                    corrected_diagnostics_ref.uri
                )
                shard_record["corrected_errors"] = corrected_errors
                if corrected_errors:
                    rejected_ref = self.services.artifacts.write_json(
                        f"tasks/{task.task_id}/edit-proposal-rejected-{index:03d}.json",
                        corrected_proposal.model_dump(mode="json"),
                    )
                    shard_record["rejected_proposal_ref"] = rejected_ref.uri
                    shard_records.append(shard_record)
                    aggregate_ref = self._write_aggregate_validation(
                        task.task_id,
                        shard_records,
                        aggregate_attempts,
                        schema_repair_used,
                        address_correction_used,
                        failure={
                            "path": entry.path,
                            "code": "shard_validation_failed",
                            "errors": corrected_errors,
                        },
                    )
                    context_index_ref = self.services.artifacts.write_text(
                        f"tasks/{task.task_id}/implementer-context.md",
                        "\n".join(context_lines) + "\n",
                        "text/markdown",
                    )
                    return {
                        "status": TaskStatus.BLOCKED.value,
                        "implementer_context_ref": context_index_ref.uri,
                        "implementer_validation_ref": aggregate_ref.uri,
                        "safe_errors": ["edit:shard_validation_failed"],
                        "events": [
                            self._event(
                                "implementer",
                                f"single file-local address correction rejected for {entry.path}",
                            )
                        ],
                    }
                proposal = corrected_proposal

            shard_record["accepted"] = True
            shard_records.append(shard_record)
            combined_edits.extend(proposal.edits)
            requested_profiles.extend(proposal.requested_test_profiles)
            assumptions.extend(proposal.assumptions)
            summaries.append(proposal.summary)

        combined = StructuredEditProposal(
            summary=("; ".join(summaries))[:4000] or "Apply approved file-sharded edits.",
            edits=tuple(combined_edits),
            requested_test_profiles=tuple(self._unique(requested_profiles)),
            assumptions=tuple(self._unique(assumptions)),
        )
        final_validation = self.services.edit_engine.validate(root, task.manifest, combined)
        if not final_validation.valid:
            aggregate_ref = self._write_aggregate_validation(
                task.task_id,
                shard_records,
                aggregate_attempts,
                schema_repair_used,
                address_correction_used,
                failure={
                    "code": "combined_validation_failed",
                    "errors": list(final_validation.errors),
                },
            )
            context_index_ref = self.services.artifacts.write_text(
                f"tasks/{task.task_id}/implementer-context.md",
                "\n".join(context_lines) + "\n",
                "text/markdown",
            )
            return {
                "status": TaskStatus.BLOCKED.value,
                "implementer_context_ref": context_index_ref.uri,
                "implementer_validation_ref": aggregate_ref.uri,
                "safe_errors": ["edit:combined_shard_validation_failed"],
                "events": [self._event("implementer", "combined shard validation rejected")],
            }

        context_index_ref = self.services.artifacts.write_text(
            f"tasks/{task.task_id}/implementer-context.md",
            "\n".join(context_lines) + "\n",
            "text/markdown",
        )
        validation_ref = self._write_aggregate_validation(
            task.task_id,
            shard_records,
            aggregate_attempts,
            schema_repair_used,
            address_correction_used,
        )
        proposal_ref = self.services.artifacts.write_json(
            f"tasks/{task.task_id}/edit-proposal.json",
            combined.model_dump(mode="json"),
        )
        correction_note = " with bounded file-local correction" if address_correction_used else ""
        return {
            "status": TaskStatus.PLANNING.value,
            "implementer_context_ref": context_index_ref.uri,
            "implementer_validation_ref": validation_ref.uri,
            "initial_edit_proposal_ref": proposal_ref.uri,
            "edit_proposal_ref": proposal_ref.uri,
            "events": [
                self._event(
                    "implementer",
                    f"combined {len(shard_records)} validated file shards{correction_note}",
                )
            ],
        }

    def _invoke_shard(
        self,
        task: SafeTaskRequest,
        state: SafeGraphState,
        target_path: str,
        index: int,
        context: str,
        *,
        phase: str,
    ):
        request = ModelRequest(
            role="implementer",
            system_prompt=SHARDED_LINE_ADDRESSED_IMPLEMENTER_SYSTEM_PROMPT,
            user_prompt=context,
            response_schema=StructuredEditProposal.model_json_schema(),
            max_output_tokens=16_000,
            metadata={
                "task_id": task.task_id,
                "scope_hash": state["scope_hash"],
                "base_sha": task.manifest.base_sha,
                "structured_edit_protocol": "v2-line-addressed-sharded",
                "target_path": target_path,
                "shard_phase": phase,
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
            self.services.artifacts.write_json(
                f"tasks/{task.task_id}/implementer-model-validation-{index:03d}-{phase}.json",
                exc.diagnostics,
            )
            return exc
        diagnostics_ref = self.services.artifacts.write_json(
            f"tasks/{task.task_id}/implementer-model-validation-{index:03d}-{phase}.json",
            structured.diagnostics,
        )
        return structured, diagnostics_ref

    def _validate_shard(
        self,
        root: Path,
        task: SafeTaskRequest,
        proposal: StructuredEditProposal,
        target_path: str,
        target_operation,
    ) -> tuple[str, ...]:
        errors: list[str] = []
        if len(proposal.edits) != 1:
            errors.append("file shard must contain exactly one FileEdit")
        else:
            edit = proposal.edits[0]
            if edit.path != target_path:
                errors.append(
                    f"file shard path is {edit.path}, expected assigned path {target_path}"
                )
            if edit.operation is not target_operation:
                errors.append(
                    f"file shard operation is {edit.operation.value}, expected {target_operation.value}"
                )
        validation = self.services.edit_engine.validate(root, task.manifest, proposal)
        errors.extend(validation.errors)
        return tuple(self._unique(errors))

    def _write_aggregate_validation(
        self,
        task_id: str,
        shards: list[dict[str, Any]],
        attempts: list[dict[str, Any]],
        schema_repair_used: bool,
        address_correction_used: bool,
        *,
        failure: dict[str, Any] | None = None,
    ):
        payload: dict[str, Any] = {
            "role": "implementer",
            "repair_used": schema_repair_used,
            "address_correction_used": address_correction_used,
            "sharded": True,
            "shards": shards,
            "attempts": attempts,
        }
        if failure is not None:
            payload["failure"] = failure
        return self.services.artifacts.write_json(
            f"tasks/{task_id}/implementer-model-validation.json",
            payload,
        )

    @staticmethod
    def _collect_attempts(
        target: list[dict[str, Any]],
        diagnostics: dict[str, Any],
        path: str,
        phase: str,
    ) -> None:
        attempts = diagnostics.get("attempts") if isinstance(diagnostics, dict) else None
        if not isinstance(attempts, list):
            return
        for item in attempts:
            if isinstance(item, dict):
                target.append({**item, "shard_path": path, "shard_phase": phase})

    @staticmethod
    def _unique(values):
        result = []
        seen = set()
        for value in values:
            if value not in seen:
                seen.add(value)
                result.append(value)
        return result

    def finalize(self, state: SafeGraphState) -> dict[str, Any]:
        result = super().finalize(state)
        task = SafeTaskRequest.model_validate(state["task"])
        final_ref = result.get("final_report_ref")
        if final_ref:
            report = self.services.artifacts.read_json(final_ref)
            report["structured_edit_protocol"] = "v2-line-addressed"
            report["line_addressed_edits"] = True
            report["file_sharded_implementer"] = True
            report["semantic_anchor_repair_enabled"] = False
            rewritten = self.services.artifacts.write_json(
                f"tasks/{task.task_id}/safe-final-report.json",
                report,
            )
            result["final_report_ref"] = rewritten.uri
        return result


SHARDED_LINE_ADDRESSED_IMPLEMENTER_SYSTEM_PROMPT = """You are one file-local shard of a bounded
code implementer operating in an isolated Git sandbox. Return exactly one StructuredEditProposal
JSON object containing exactly one FileEdit for the assigned path and approved operation. Never
emit Git patch syntax or shell commands. For modify operations, TextReplacement.old_text must be
one @range, @before, or @after token copied exactly from the assigned file state in this prompt.
Never invent a line number or fingerprint. Put exact replacement or inserted text in new_text,
preserve complete-line boundaries and line endings, and keep replacements non-overlapping. Do not
delete, rename, copy, modify symlinks, stage, commit, push, create a pull request, merge, deploy, or
broaden scope. Git will generate the canonical patch after the control plane validates and combines
all independently bounded file shards."""
