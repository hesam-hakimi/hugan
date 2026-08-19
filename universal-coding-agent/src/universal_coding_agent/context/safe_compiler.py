from __future__ import annotations

import hashlib
from pathlib import Path

from universal_coding_agent.core.models import ProjectManifest
from universal_coding_agent.core.safe_models import (
    PatchProposal,
    SafeTaskRequest,
    StructuredEditProposal,
    TestExecutionResult,
    safe_json,
)
from universal_coding_agent.safety.sanitizer import sanitize_text


class SafeContextCompiler:
    def __init__(
        self,
        *,
        implementer_char_budget: int = 240_000,
        reviewer_char_budget: int = 120_000,
        edit_repair_char_budget: int = 220_000,
        patch_repair_char_budget: int = 180_000,
        max_chars_per_file: int = 70_000,
        edit_repair_max_chars_per_file: int = 140_000,
        patch_repair_max_chars_per_file: int = 60_000,
    ) -> None:
        self.implementer_char_budget = implementer_char_budget
        self.reviewer_char_budget = reviewer_char_budget
        self.edit_repair_char_budget = edit_repair_char_budget
        self.patch_repair_char_budget = patch_repair_char_budget
        self.max_chars_per_file = max_chars_per_file
        self.edit_repair_max_chars_per_file = edit_repair_max_chars_per_file
        self.patch_repair_max_chars_per_file = patch_repair_max_chars_per_file

    def compile_implementer(
        self,
        root: Path,
        task: SafeTaskRequest,
        project_manifest: ProjectManifest,
    ) -> str:
        sections = [
            "# Safe task",
            task.objective,
            "# Immutable repository identity",
            (
                f"Repository: {project_manifest.repository_url}\n"
                f"Base ref: {project_manifest.base_ref}\n"
                f"Base SHA: {project_manifest.base_sha}"
            ),
            "# Human-approved change manifest",
            safe_json(task.manifest.model_dump(mode="json")),
            "# Exact allowed file state",
            self._allowed_file_state(root, task),
            "# Mandatory structured-edit contract",
            (
                "Return exactly one JSON object matching StructuredEditProposal. Do not emit a "
                "unified diff, diff --git headers, ---/+++ markers, @@ hunks, Markdown patch "
                "fences, shell commands, or Git commands. For each modified file, return one "
                "FileEdit containing one or more non-overlapping exact text replacements. Each "
                "old_text must be copied verbatim from the supplied base-file state and must be "
                "specific enough to occur exactly once in that file. new_text is the exact text "
                "that should replace that anchor. For an approved create operation, return the "
                "complete UTF-8 text content. Change only approved paths and operations. Do not "
                "delete, rename, copy, modify symlinks, stage, commit, push, create a pull "
                "request, merge, deploy, or run commands. The tool, not the model, will apply the "
                "structured edits and ask Git to generate the canonical patch."
            ),
        ]
        return self._bound("\n\n".join(sections), self.implementer_char_budget)

    def compile_edit_repair(
        self,
        root: Path,
        task: SafeTaskRequest,
        proposal: StructuredEditProposal,
        validation_errors: tuple[str, ...],
    ) -> str:
        """Compile one bounded semantic-anchor repair with exact frozen file state."""

        failed_paths = self._paths_from_validation_errors(
            proposal.changed_paths,
            validation_errors,
        )
        sections = [
            "# Bounded structured-edit anchor repair",
            (
                "The initial StructuredEditProposal was schema-valid, but deterministic edit "
                "validation rejected one or more exact replacement anchors. This is the only "
                "semantic edit-repair attempt. The control plane will still require exact unique "
                "anchors and will fail closed if the repaired proposal is not deterministically "
                "applicable."
            ),
            "# Original safe task",
            task.objective,
            "# Frozen human-approved change manifest",
            safe_json(task.manifest.model_dump(mode="json")),
            "# Deterministic edit-validation errors",
            safe_json(list(validation_errors)),
            "# Rejected structured-edit proposal",
            safe_json(proposal.model_dump(mode="json")),
            "# Exact frozen base-file state for paths requiring anchor repair",
            self._allowed_file_state(
                root,
                task,
                max_chars_per_file=self.edit_repair_max_chars_per_file,
                only_paths=set(failed_paths),
            ),
            "# Mandatory repair contract",
            (
                "Return exactly one StructuredEditProposal JSON object. Preserve the exact set of "
                "edited paths, operations, requested test profiles, and substantive requested "
                "changes from the rejected proposal. Do not add, remove, or substitute files. "
                "Correct only the semantic edit anchors/replacements necessary to make the edits "
                "deterministically applicable. Every old_text must be copied verbatim from the "
                "exact frozen base-file state above and must occur exactly once. Do not emit Git "
                "patch syntax, Markdown patch fences, commands, or publication actions."
            ),
        ]
        return self._bound("\n\n".join(sections), self.edit_repair_char_budget)

    def compile_patch_repair(
        self,
        root: Path,
        task: SafeTaskRequest,
        proposal: PatchProposal,
        validation_errors: tuple[str, ...],
    ) -> str:
        """Legacy raw-patch repair context retained for old persisted runs only."""

        sections = [
            "# Legacy bounded patch applicability repair",
            (
                "This context exists only for compatibility with persisted pre-structured-edit "
                "runs. New Safe Mode runs do not ask a model to author or repair Git patches."
            ),
            "# Original safe task",
            task.objective,
            "# Frozen human-approved change manifest",
            safe_json(task.manifest.model_dump(mode="json")),
            "# Deterministic validation failure",
            safe_json(list(validation_errors)),
            "# Rejected proposal summary",
            proposal.summary,
            "# Rejected unified diff",
            f"```diff\n{proposal.unified_diff}```",
            "# Exact current base file state for approved paths",
            self._allowed_file_state(
                root,
                task,
                max_chars_per_file=self.patch_repair_max_chars_per_file,
                line_numbers=True,
            ),
        ]
        return self._bound("\n\n".join(sections), self.patch_repair_char_budget)

    def compile_reviewer(
        self,
        root: Path,
        task: SafeTaskRequest,
        proposal: PatchProposal,
        tests: tuple[TestExecutionResult, ...],
        actual_changed_paths: tuple[str, ...],
    ) -> str:
        sections = [
            "# Original safe task",
            task.objective,
            "# Approved change manifest",
            safe_json(task.manifest.model_dump(mode="json")),
            "# Tool-generated patch summary",
            proposal.summary,
            "# Canonical Git diff generated from the materialized sandbox",
            f"```diff\n{proposal.unified_diff}\n```",
            "# Actual changed paths",
            safe_json(list(actual_changed_paths)),
            "# Focused test results",
            safe_json([item.model_dump(mode="json") for item in tests]),
            "# Post-change approved file state",
            self._allowed_file_state(root, task),
            "# Review rules",
            (
                "Independently verify requirement satisfaction, exact scope, security boundaries, "
                "test evidence, and compatibility. The implementer supplied structured edits; "
                "the Git diff above was generated deterministically by the tool from the sandbox. "
                "PASS only when the result is fully acceptable. Use PASS_WITH_CONDITIONS, "
                "BLOCKED, or FAIL when any follow-up is required."
            ),
        ]
        return self._bound("\n\n".join(sections), self.reviewer_char_budget)

    def _allowed_file_state(
        self,
        root: Path,
        task: SafeTaskRequest,
        *,
        max_chars_per_file: int | None = None,
        line_numbers: bool = False,
        only_paths: set[str] | None = None,
    ) -> str:
        repository_root = root.resolve()
        limit = max_chars_per_file or self.max_chars_per_file
        output: list[str] = []
        for entry in task.manifest.allowed_changes:
            if only_paths is not None and entry.path not in only_paths:
                continue
            path = repository_root / entry.path
            resolved = path.resolve()
            if resolved != repository_root and repository_root not in resolved.parents:
                raise ValueError("approved file escapes repository")
            if self._contains_symlink_component(repository_root, entry.path):
                output.append(f"## {entry.path}\nSYMLINK_REJECTED")
                continue
            if not path.exists():
                output.append(
                    f"## {entry.path}\nOperation: {entry.operation.value}\nState: ABSENT"
                )
                continue
            if not path.is_file():
                output.append(f"## {entry.path}\nState: NOT_A_REGULAR_FILE")
                continue
            try:
                payload = path.read_bytes()
                content = payload.decode("utf-8")
            except (OSError, UnicodeDecodeError):
                output.append(f"## {entry.path}\nState: NOT_READABLE_UTF8_TEXT")
                continue

            bounded_raw = content[:limit]
            bounded = sanitize_text(bounded_raw)
            content_sha = hashlib.sha256(payload).hexdigest()
            truncated = len(content) > limit
            redacted = bounded != bounded_raw
            if redacted:
                output.append(
                    f"## {entry.path}\nOperation: {entry.operation.value}\n"
                    f"SHA256: {content_sha}\nState: CONTENT_REDACTED_FOR_SAFETY\n"
                    "Exact model-authored replacements are not permitted for redacted content."
                )
                continue
            if line_numbers:
                bounded = self._with_line_numbers(bounded)
            suffix = (
                "\n[FILE CONTENT TRUNCATED BY DETERMINISTIC CONTEXT BUDGET]"
                if truncated
                else ""
            )
            output.append(
                f"## {entry.path}\nOperation: {entry.operation.value}\n"
                f"SHA256: {content_sha}\nTruncated: {str(truncated).lower()}\n"
                f"```text\n{bounded}{suffix}\n```"
            )
        return "\n\n".join(output)

    @staticmethod
    def _paths_from_validation_errors(
        changed_paths: tuple[str, ...],
        validation_errors: tuple[str, ...],
    ) -> tuple[str, ...]:
        matched = tuple(
            path
            for path in changed_paths
            if any(path in error for error in validation_errors)
        )
        return matched or changed_paths

    @staticmethod
    def _contains_symlink_component(root: Path, relative: str) -> bool:
        cursor = root
        for part in Path(relative).parts:
            cursor = cursor / part
            if cursor.is_symlink():
                return True
        return False

    @staticmethod
    def _with_line_numbers(value: str) -> str:
        return "\n".join(
            f"{index:06d}: {line}"
            for index, line in enumerate(value.splitlines(), start=1)
        )

    @staticmethod
    def _bound(value: str, budget: int) -> str:
        if len(value) <= budget:
            return value
        marker = "\n\n[context truncated by deterministic character budget]"
        return value[: budget - len(marker)] + marker