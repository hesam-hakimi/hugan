from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import Field, field_validator, model_validator

from universal_coding_agent.core.models import (
    FrozenModel,
    ModelRequest,
    ProjectFile,
    ProjectManifest,
    RepositorySpec,
)
from universal_coding_agent.core.safe_models import ChangeOperation, normalize_repository_path
from universal_coding_agent.orchestration.structured_output import (
    StructuredOutputError,
    invoke_structured,
)
from universal_coding_agent.providers.base import ModelProvider
from universal_coding_agent.repository.indexer import RepositoryIndexer
from universal_coding_agent.safety.sanitizer import sanitize_text

_TERM = re.compile(r"[A-Za-z][A-Za-z0-9_-]{2,}")


class ImpactConfidence(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DiscoveryCandidate(FrozenModel):
    path: str
    component: str
    score: int = Field(ge=0)
    reasons: tuple[str, ...] = ()
    imports: tuple[str, ...] = ()
    imported_by: tuple[str, ...] = ()

    @field_validator("path")
    @classmethod
    def validate_path(cls, value: str) -> str:
        return normalize_repository_path(value)


class DiscoverySnapshot(FrozenModel):
    repository_url: str
    base_ref: str
    base_sha: str
    objective: str
    tracked_file_count: int = Field(ge=1)
    language_counts: dict[str, int] = Field(default_factory=dict)
    candidates: tuple[DiscoveryCandidate, ...] = Field(min_length=1, max_length=80)
    dependency_edges: tuple[str, ...] = ()
    instruction_paths: tuple[str, ...] = ()
    architecture_paths: tuple[str, ...] = ()

    @property
    def candidate_paths(self) -> tuple[str, ...]:
        return tuple(item.path for item in self.candidates)


class ImpactChange(FrozenModel):
    path: str
    operation: ChangeOperation = ChangeOperation.MODIFY
    component: str = Field(min_length=1, max_length=200)
    confidence: ImpactConfidence
    rationale: str = Field(min_length=1, max_length=2000)
    evidence_paths: tuple[str, ...] = ()

    @field_validator("path")
    @classmethod
    def validate_path(cls, value: str) -> str:
        return normalize_repository_path(value)

    @field_validator("evidence_paths")
    @classmethod
    def validate_evidence_paths(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(normalize_repository_path(item) for item in values)
        if len(normalized) != len(set(normalized)):
            raise ValueError("evidence_paths must be unique")
        return normalized


class SolutionImpactPlan(FrozenModel):
    summary: str = Field(min_length=1, max_length=4000)
    components: tuple[str, ...] = Field(min_length=1, max_length=32)
    changes: tuple[ImpactChange, ...] = Field(min_length=1, max_length=16)
    rejected_candidates: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_unique_changes(self) -> SolutionImpactPlan:
        paths = [item.path for item in self.changes]
        if len(paths) != len(set(paths)):
            raise ValueError("impact plan change paths must be unique")
        return self


@dataclass(frozen=True)
class SolutionDiscoveryResult:
    manifest: ProjectManifest
    snapshot: DiscoverySnapshot
    plan: SolutionImpactPlan
    diagnostics: dict[str, Any]


class SolutionDiscoveryError(RuntimeError):
    pass


class SolutionArchitectureAnalyzer:
    """Build a bounded, deterministic architecture neighborhood before LLM reasoning."""

    def __init__(self, *, max_candidates: int = 48, lexical_seed_count: int = 16) -> None:
        self.max_candidates = max_candidates
        self.lexical_seed_count = lexical_seed_count

    def build_snapshot(
        self,
        objective: str,
        manifest: ProjectManifest,
    ) -> DiscoverySnapshot:
        files = {item.path: item for item in manifest.files}
        module_map = {
            module: item.path
            for item in manifest.files
            if item.language == "python"
            for module in [self._python_module(item.path)]
            if module
        }
        imports: dict[str, set[str]] = defaultdict(set)
        imported_by: dict[str, set[str]] = defaultdict(set)
        for item in manifest.files:
            for raw_import in item.imports:
                target = self._resolve_python_import(raw_import, module_map)
                if target is None or target == item.path:
                    continue
                imports[item.path].add(target)
                imported_by[target].add(item.path)

        terms = self._terms(objective)
        scores: dict[str, int] = {}
        reasons: dict[str, list[str]] = defaultdict(list)
        for item in manifest.files:
            score, item_reasons = self._lexical_score(item, terms)
            if item.path in manifest.architecture_paths:
                score += 4
                item_reasons.append("architecture reference")
            if item.path in manifest.instruction_paths:
                score += 3
                item_reasons.append("repository instruction")
            scores[item.path] = score
            reasons[item.path].extend(item_reasons)

        lexical_seeds = sorted(
            manifest.files,
            key=lambda item: (-scores[item.path], item.path),
        )[: self.lexical_seed_count]
        for seed in lexical_seeds:
            seed_score = scores[seed.path]
            if seed_score <= 0:
                continue
            for target in imports.get(seed.path, set()):
                scores[target] += 8
                reasons[target].append(f"imported by lexical seed {seed.path}")
            for source in imported_by.get(seed.path, set()):
                scores[source] += 6
                reasons[source].append(f"imports lexical seed {seed.path}")

        first_hop = [path for path, score in scores.items() if score > 0]
        for path in first_hop:
            for target in imports.get(path, set()):
                scores[target] += 3
                reasons[target].append(f"dependency of candidate {path}")
            for source in imported_by.get(path, set()):
                scores[source] += 2
                reasons[source].append(f"dependent of candidate {path}")

        ranked_paths = sorted(files, key=lambda path: (-scores[path], path))
        selected = [path for path in ranked_paths if scores[path] > 0][: self.max_candidates]
        if not selected:
            selected = ranked_paths[: self.max_candidates]
        selected_set = set(selected)

        candidates = tuple(
            DiscoveryCandidate(
                path=path,
                component=self._component(path),
                score=scores[path],
                reasons=tuple(self._unique(reasons[path])[:8]),
                imports=tuple(sorted(imports.get(path, set()) & selected_set)),
                imported_by=tuple(sorted(imported_by.get(path, set()) & selected_set)),
            )
            for path in selected
        )
        edges = tuple(
            sorted(
                f"{source} -> {target}"
                for source in selected
                for target in imports.get(source, set())
                if target in selected_set
            )
        )
        return DiscoverySnapshot(
            repository_url=manifest.repository_url,
            base_ref=manifest.base_ref,
            base_sha=manifest.base_sha,
            objective=objective,
            tracked_file_count=len(manifest.files),
            language_counts=manifest.language_counts,
            candidates=candidates,
            dependency_edges=edges,
            instruction_paths=manifest.instruction_paths,
            architecture_paths=manifest.architecture_paths,
        )

    @staticmethod
    def _python_module(path: str) -> str | None:
        if not path.endswith(".py"):
            return None
        parts = path[:-3].split("/")
        if parts[-1] == "__init__":
            parts = parts[:-1]
        return ".".join(parts) or None

    @staticmethod
    def _resolve_python_import(raw_import: str, module_map: dict[str, str]) -> str | None:
        module = raw_import.split(":", 1)[0].strip(".")
        if module in module_map:
            return module_map[module]
        parts = module.split(".")
        while len(parts) > 1:
            parts.pop()
            candidate = ".".join(parts)
            if candidate in module_map:
                return module_map[candidate]
        return None

    @staticmethod
    def _component(path: str) -> str:
        parts = path.split("/")
        if len(parts) >= 2:
            return "/".join(parts[:2])
        return parts[0]

    @staticmethod
    def _terms(text: str) -> set[str]:
        terms: set[str] = set()
        for raw in _TERM.findall(text.lower()):
            terms.add(raw)
            terms.update(part for part in raw.replace("-", "_").split("_") if len(part) >= 3)
        return terms

    @staticmethod
    def _lexical_score(item: ProjectFile, terms: set[str]) -> tuple[int, list[str]]:
        haystack = " ".join((item.path, *item.symbols, *item.imports)).lower()
        matches = sorted(term for term in terms if term in haystack)
        score = len(matches) * 3
        if item.is_test:
            score += 1
        reasons = [f"objective term: {term}" for term in matches[:6]]
        return score, reasons

    @staticmethod
    def _unique(values: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for value in values:
            if value in seen:
                continue
            seen.add(value)
            result.append(value)
        return result


class SolutionDiscoveryContextCompiler:
    def __init__(
        self,
        *,
        max_snippet_files: int = 28,
        max_chars_per_file: int = 3500,
        char_budget: int = 140_000,
    ) -> None:
        self.max_snippet_files = max_snippet_files
        self.max_chars_per_file = max_chars_per_file
        self.char_budget = char_budget

    def compile(self, root: Path, snapshot: DiscoverySnapshot) -> str:
        candidate_lines = []
        for item in snapshot.candidates:
            candidate_lines.append(
                "\n".join(
                    (
                        f"- path: {item.path}",
                        f"  component: {item.component}",
                        f"  score: {item.score}",
                        f"  reasons: {list(item.reasons)}",
                        f"  imports: {list(item.imports)}",
                        f"  imported_by: {list(item.imported_by)}",
                    )
                )
            )
        sections = [
            "# Requirement",
            snapshot.objective,
            "# Repository summary",
            (
                f"Base SHA: {snapshot.base_sha}\n"
                f"Tracked indexed files: {snapshot.tracked_file_count}\n"
                f"Languages: {snapshot.language_counts}"
            ),
            "# Discovery rules",
            (
                "Select the smallest coherent existing-file change scope. Lexical similarity is "
                "not proof of runtime relevance. Prefer active dependency/import chains and reject "
                "legacy, batch, analytics, examples, generated snapshots, and documentation-only "
                "decoys unless the requirement truly needs them. Every proposed path must come "
                "from the bounded candidate set below. Do not propose new files in this milestone."
            ),
            "# Bounded architecture candidates",
            "\n".join(candidate_lines),
            "# Dependency edges",
            "\n".join(snapshot.dependency_edges) or "(none resolved)",
            "# Bounded candidate snippets",
            self._snippets(root, snapshot.candidates[: self.max_snippet_files]),
        ]
        value = "\n\n".join(sections)
        if len(value) <= self.char_budget:
            return value
        marker = "\n\n[discovery context truncated by deterministic character budget]"
        return value[: self.char_budget - len(marker)] + marker

    def _snippets(self, root: Path, candidates: tuple[DiscoveryCandidate, ...]) -> str:
        root = root.resolve()
        output: list[str] = []
        for item in candidates:
            path = (root / item.path).resolve()
            if root not in path.parents or not path.is_file():
                continue
            try:
                value = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            output.append(
                f"## {item.path}\n```text\n"
                f"{sanitize_text(value[: self.max_chars_per_file])}\n```"
            )
        return "\n\n".join(output)


class SolutionDiscoveryService:
    def __init__(
        self,
        provider: ModelProvider,
        *,
        indexer: RepositoryIndexer | None = None,
        analyzer: SolutionArchitectureAnalyzer | None = None,
        compiler: SolutionDiscoveryContextCompiler | None = None,
    ) -> None:
        self.provider = provider
        self.indexer = indexer or RepositoryIndexer()
        self.analyzer = analyzer or SolutionArchitectureAnalyzer()
        self.compiler = compiler or SolutionDiscoveryContextCompiler()

    def discover(
        self,
        root: Path,
        repository: RepositorySpec,
        *,
        base_sha: str,
        objective: str,
    ) -> SolutionDiscoveryResult:
        manifest = self.indexer.build_manifest(
            root,
            repository_url=repository.url,
            base_ref=repository.base_ref,
            base_sha=base_sha,
        )
        snapshot = self.analyzer.build_snapshot(objective, manifest)
        context = self.compiler.compile(root, snapshot)
        request = ModelRequest(
            role="solution_discovery",
            system_prompt=SOLUTION_DISCOVERY_SYSTEM_PROMPT,
            user_prompt=context,
            response_schema=SolutionImpactPlan.model_json_schema(),
            max_output_tokens=8_000,
            metadata={"base_sha": base_sha},
        )
        try:
            structured = invoke_structured(
                self.provider,
                request,
                SolutionImpactPlan,
                repair_guidance=SOLUTION_DISCOVERY_REPAIR_GUIDANCE,
            )
        except StructuredOutputError as exc:
            raise SolutionDiscoveryError(f"solution discovery failed safely: {exc.code}") from exc

        plan = structured.value
        self._validate_plan(root, snapshot, plan)
        return SolutionDiscoveryResult(
            manifest=manifest,
            snapshot=snapshot,
            plan=plan,
            diagnostics=structured.diagnostics,
        )

    @staticmethod
    def _validate_plan(
        root: Path,
        snapshot: DiscoverySnapshot,
        plan: SolutionImpactPlan,
    ) -> None:
        root = root.resolve()
        candidates = set(snapshot.candidate_paths)
        errors: list[str] = []
        for change in plan.changes:
            if change.operation is not ChangeOperation.MODIFY:
                errors.append(f"create is not enabled for discovery scope: {change.path}")
            if change.path not in candidates:
                errors.append(
                    "proposed path is outside bounded discovery candidates: "
                    f"{change.path}"
                )
            target = (root / change.path).resolve()
            if root not in target.parents or not target.is_file():
                errors.append(f"proposed path is not an existing contained file: {change.path}")
            for evidence in change.evidence_paths:
                if evidence not in candidates:
                    errors.append(
                        f"evidence path is outside bounded discovery candidates: {evidence}"
                    )
        if errors:
            raise SolutionDiscoveryError("; ".join(errors))


SOLUTION_DISCOVERY_SYSTEM_PROMPT = """You are the solution-level impact planner for a bounded
coding agent. Analyze the requirement, candidate source snippets, and deterministic dependency
edges. Return exactly one SolutionImpactPlan JSON object. Propose the minimum coherent set of
existing files that truly need implementation changes. Do not select a file merely because its
name resembles the requirement. Use dependency evidence to distinguish active runtime paths from
legacy, batch, analytics, examples, generated snapshots, and other decoys. Every change must use
operation 'modify' and a path copied exactly from the bounded candidate set. Use evidence_paths to
show why each selected file belongs to the active implementation chain. Do not write code, patches,
or shell commands. Do not invent paths."""

SOLUTION_DISCOVERY_REPAIR_GUIDANCE = """Return one valid SolutionImpactPlan JSON object only.
Keep every change path inside the supplied bounded candidate set, use only operation 'modify', keep
paths unique, and provide concrete dependency evidence for the smallest coherent runtime scope."""
