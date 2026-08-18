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
        max_chars_per_file: int = 24_000,
    ) -> None:
        self.implementer_char_budget = implementer_char_budget
        self.reviewer_char_budget = reviewer_char_budget
        self.max_chars_per_file = max_chars_per_file

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
                "create a pull request, merge, deploy, or run commands."
            ),
        ]
        return self._bound("\n\n".join(sections), self.implementer_char_budget)

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

    def _allowed_file_state(self, root: Path, task: SafeTaskRequest) -> str:
        repository_root = root.resolve()
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
            bounded = sanitize_text(content[: self.max_chars_per_file])
            output.append(
                f"## {entry.path}\nOperation: {entry.operation.value}\n"
                f"```text\n{bounded}\n```"
            )
        return "\n\n".join(output)

    @staticmethod
    def _bound(value: str, budget: int) -> str:
        if len(value) <= budget:
            return value
        marker = "\n\n[context truncated by deterministic character budget]"
        return value[: budget - len(marker)] + marker
