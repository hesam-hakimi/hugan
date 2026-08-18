from __future__ import annotations

from pathlib import Path

from universal_coding_agent.core.models import ProjectManifest
from universal_coding_agent.core.safe_models import (
    PatchProposal,
    SafeTaskRequest,
    TestExecutionResult,
    safe_json,
)
from universal_coding_agent.safety.sanitizer import sanitize_text


class SafeContextCompiler:
    def __init__(
        self,
        *,
        implementer_char_budget: int = 120_000,
        reviewer_char_budget: int = 100_000,
        patch_repair_char_budget: int = 180_000,
        max_chars_per_file: int = 24_000,
        patch_repair_max_chars_per_file: int = 60_000,
    ) -> None:
        self.implementer_char_budget = implementer_char_budget
        self.reviewer_char_budget = reviewer_char_budget
        self.patch_repair_char_budget = patch_repair_char_budget
        self.max_chars_per_file = max_chars_per_file
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
            "# Mandatory output contract",
            (
                "Return exactly one JSON object matching PatchProposal. The unified_diff must "
                "be a git-style text patch. Change only approved paths and operations. Do not "
                "rename, delete, copy, modify symlinks, emit binary patches, stage, commit, push, "
                "create a pull request, merge, deploy, or run commands. Every unchanged/context "
                "line in every hunk must be copied exactly from the supplied base file state; do "
                "not invent an anchor line or an existing heading."
            ),
        ]
        return self._bound("\n\n".join(sections), self.implementer_char_budget)

    def compile_patch_repair(
        self,
        root: Path,
        task: SafeTaskRequest,
        proposal: PatchProposal,
        validation_errors: tuple[str, ...],
    ) -> str:
        sections = [
            "# Bounded patch applicability repair",
            (
                "The previous PatchProposal was schema-valid and stayed inside the approved "
                "file manifest, but deterministic git apply --check rejected it. Repair only "
                "patch applicability. Preserve the original task intent, exact changed_paths, "
                "approved operations, requested test profiles, and semantic changes."
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
            "# Repair contract",
            (
                "Return exactly one PatchProposal JSON object. Do not add or remove changed "
                "paths. Do not change create/modify operations. Do not broaden the task. Do not "
                "add Markdown fences to unified_diff. Use exact current base-file text for all "
                "unchanged and removed hunk lines. If an earlier hunk relied on invented or stale "
                "context, replace that context with exact lines from the supplied file state. "
                "Hunk line numbers may be recalculated, but correctness is determined by exact "
                "context and later git apply --check."
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
            "# Proposed patch summary",
            proposal.summary,
            "# Applied unified diff",
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
                "test evidence, and compatibility. PASS only when the patch is fully acceptable. "
                "Use PASS_WITH_CONDITIONS, BLOCKED, or FAIL when any follow-up is required."
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
    ) -> str:
        repository_root = root.resolve()
        limit = max_chars_per_file or self.max_chars_per_file
        output: list[str] = []
        for entry in task.manifest.allowed_changes:
            path = (repository_root / entry.path).resolve()
            if path != repository_root and repository_root not in path.parents:
                raise ValueError("approved file escapes repository")
            if path.is_symlink():
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
                content = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                output.append(f"## {entry.path}\nState: UNREADABLE")
                continue
            bounded = sanitize_text(content[:limit])
            truncated = len(content) > limit
            if line_numbers:
                bounded = self._with_line_numbers(bounded)
            suffix = "\n[FILE CONTENT TRUNCATED BY REPAIR BUDGET]" if truncated else ""
            output.append(
                f"## {entry.path}\nOperation: {entry.operation.value}\n"
                f"```text\n{bounded}{suffix}\n```"
            )
        return "\n\n".join(output)

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
