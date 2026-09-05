from __future__ import annotations

import re
from pathlib import Path

from universal_coding_agent.core.models import PhasePlan, ProjectFile, ProjectManifest, TaskRequest
from universal_coding_agent.safety.sanitizer import sanitize_text

_WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_.-]{2,}")


class ContextCompiler:
    def __init__(
        self,
        *,
        planner_char_budget: int = 80_000,
        reviewer_char_budget: int = 60_000,
        max_files: int = 12,
        max_chars_per_file: int = 6000,
    ) -> None:
        self.role_budgets = {"planner": planner_char_budget, "reviewer": reviewer_char_budget}
        self.max_files = max_files
        self.max_chars_per_file = max_chars_per_file

    def compile_planner(self, root: Path, task: TaskRequest, manifest: ProjectManifest) -> str:
        ranked = self._rank_files(task.objective, manifest)
        sections = [
            "# Task",
            task.objective,
            "# Repository",
            (
                f"URL: {manifest.repository_url}\n"
                f"Base ref: {manifest.base_ref}\n"
                f"Base SHA: {manifest.base_sha}"
            ),
            "# Project summary",
            f"Languages: {manifest.language_counts}\nTracked indexed files: {len(manifest.files)}",
            "# Instructions and architecture",
            (
                f"Instructions: {list(manifest.instruction_paths)}\n"
                f"Architecture: {list(manifest.architecture_paths)}"
            ),
            "# Relevant bounded files",
            self._snippets(root, ranked),
        ]
        return self._bound("\n\n".join(sections), "planner")

    def compile_reviewer(
        self,
        root: Path,
        task: TaskRequest,
        manifest: ProjectManifest,
        plan: PhasePlan,
        checks: list[dict[str, object]],
    ) -> str:
        terms = task.objective + " " + " ".join(plan.requirements) + " " + " ".join(plan.exclusions)
        ranked = self._rank_files(terms, manifest)
        sections = [
            "# Original task",
            task.objective,
            "# Typed plan",
            plan.model_dump_json(indent=2),
            "# Read-only checks",
            repr(checks),
            "# Independent repository context",
            self._snippets(root, ranked),
        ]
        return self._bound("\n\n".join(sections), "reviewer")

    def _rank_files(self, text: str, manifest: ProjectManifest) -> list[ProjectFile]:
        terms = {item.lower() for item in _WORD.findall(text)}
        scored: list[tuple[int, ProjectFile]] = []
        priority = set(manifest.instruction_paths) | set(manifest.architecture_paths)
        for item in manifest.files:
            haystack = " ".join((item.path, *item.symbols, *item.imports)).lower()
            score = sum(1 for term in terms if term in haystack)
            if item.path in priority:
                score += 4
            if item.is_test:
                score += 1
            if score:
                scored.append((score, item))
        scored.sort(key=lambda pair: (-pair[0], pair[1].path))
        chosen = [item for _, item in scored[: self.max_files]]
        if not chosen:
            chosen = list(manifest.files[: self.max_files])
        return chosen

    def _snippets(self, root: Path, files: list[ProjectFile]) -> str:
        output: list[str] = []
        root = root.resolve()
        for item in files:
            path = (root / item.path).resolve()
            if root not in path.parents or not path.is_file():
                continue
            try:
                value = path.read_text(encoding="utf-8", errors="replace")[
                    : self.max_chars_per_file
                ]
            except OSError:
                continue
            output.append(f"## {item.path}\n```text\n{sanitize_text(value)}\n```")
        return "\n\n".join(output)

    def _bound(self, value: str, role: str) -> str:
        budget = self.role_budgets[role]
        if len(value) <= budget:
            return value
        marker = "\n\n[context truncated by deterministic character budget]"
        return value[: budget - len(marker)] + marker
