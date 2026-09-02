from __future__ import annotations

import ast
import hashlib
import hmac
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator, model_validator

from universal_coding_agent.core.models import FrozenModel
from universal_coding_agent.core.safe_models import normalize_repository_path
from universal_coding_agent.product.call_graphs import (
    CALL_GRAPH_POLICY_VERSION,
    PythonCallGraph,
    PythonSymbol,
    PythonSymbolKind,
    RepositoryCallGraphError,
    RepositoryCallGraphService,
    UnresolvedCallReason,
)
from universal_coding_agent.product.dependency_graphs import PythonDependencyGraph
from universal_coding_agent.product.search_service import (
    RepositoryDispatchEvidenceState,
    RepositoryDispatchEvidenceStateError,
    SearchService,
)
from universal_coding_agent.storage.artifacts import ArtifactStore

DEFAULT_DISPATCH_EVIDENCE_MAX_BYTES = 12_000_000
DEFAULT_DISPATCH_SOURCE_MAX_BYTES = 64_000_000
DEFAULT_DISPATCH_MAX_CLASSES = 100_000
DEFAULT_DISPATCH_MAX_BASES = 200_000
DEFAULT_DISPATCH_MAX_SITES = 250_000
DEFAULT_DISPATCH_MAX_CANDIDATES = 500_000
DEFAULT_DISPATCH_MAX_EXPRESSION_BYTES = 1_024
DISPATCH_EVIDENCE_POLICY_VERSION = "1"
_PROJECT_ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")


class RepositoryDispatchEvidenceError(ValueError):
    """Dynamic-dispatch evidence cannot satisfy its bounded provenance contract."""


class BaseResolution(StrEnum):
    RESOLVED = "resolved"
    AMBIGUOUS = "ambiguous"
    UNRESOLVED = "unresolved"
    UNSUPPORTED = "unsupported"


class DispatchResolution(StrEnum):
    EXACT_DECLARED_TYPE = "exact_declared_type"
    POLYMORPHIC_CANDIDATES = "polymorphic_candidates"
    UNKNOWN_RECEIVER = "unknown_receiver"
    AMBIGUOUS_RECEIVER = "ambiguous_receiver"
    UNSAFE_HIERARCHY = "unsafe_hierarchy"
    MISSING_METHOD = "missing_method"
    UNSUPPORTED_RECEIVER = "unsupported_receiver"


class PythonClassEvidence(FrozenModel):
    class_symbol_id: str = Field(min_length=1, max_length=8192)
    path: str = Field(min_length=1, max_length=4096)
    module: str = Field(min_length=1, max_length=4096)
    qualname: str = Field(min_length=1, max_length=4096)
    direct_base_class_ids: tuple[str, ...] = ()
    hierarchy_safe: bool

    @field_validator("path")
    @classmethod
    def validate_path(cls, value: str) -> str:
        return normalize_repository_path(value)

    @field_validator("direct_base_class_ids")
    @classmethod
    def validate_bases(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        if values != tuple(sorted(set(values))):
            raise ValueError("direct base class IDs must be unique and sorted")
        return values


class PythonBaseEvidence(FrozenModel):
    class_symbol_id: str = Field(min_length=1, max_length=8192)
    expression: str = Field(min_length=1, max_length=4096)
    line: int = Field(ge=1)
    column: int = Field(ge=0)
    resolution: BaseResolution
    candidate_class_ids: tuple[str, ...] = ()

    @field_validator("candidate_class_ids")
    @classmethod
    def validate_candidates(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        if values != tuple(sorted(set(values))):
            raise ValueError("base candidates must be unique and sorted")
        return values

    @model_validator(mode="after")
    def validate_resolution(self) -> PythonBaseEvidence:
        if self.resolution is BaseResolution.RESOLVED and len(self.candidate_class_ids) != 1:
            raise ValueError("resolved base evidence requires exactly one candidate")
        if self.resolution is BaseResolution.AMBIGUOUS and len(self.candidate_class_ids) < 2:
            raise ValueError("ambiguous base evidence requires multiple candidates")
        if self.resolution in {BaseResolution.UNRESOLVED, BaseResolution.UNSUPPORTED} and (
            self.candidate_class_ids
        ):
            raise ValueError("unresolved base evidence cannot retain candidates")
        return self


class PythonDispatchSite(FrozenModel):
    source_path: str = Field(min_length=1, max_length=4096)
    caller_symbol_id: str = Field(min_length=1, max_length=8192)
    line: int = Field(ge=1)
    column: int = Field(ge=0)
    expression: str = Field(min_length=1, max_length=4096)
    receiver_expression: str = Field(min_length=1, max_length=4096)
    method_name: str = Field(min_length=1, max_length=512)
    resolution: DispatchResolution
    receiver_class_ids: tuple[str, ...] = ()
    candidate_method_ids: tuple[str, ...] = ()

    @field_validator("source_path")
    @classmethod
    def validate_path(cls, value: str) -> str:
        return normalize_repository_path(value)

    @field_validator("receiver_class_ids", "candidate_method_ids")
    @classmethod
    def validate_candidates(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        if values != tuple(sorted(set(values))):
            raise ValueError("dispatch candidates must be unique and sorted")
        return values

    @model_validator(mode="after")
    def validate_resolution(self) -> PythonDispatchSite:
        resolved = {
            DispatchResolution.EXACT_DECLARED_TYPE,
            DispatchResolution.POLYMORPHIC_CANDIDATES,
        }
        if self.resolution in resolved:
            if not self.receiver_class_ids or not self.candidate_method_ids:
                raise ValueError(
                    "resolved dispatch evidence requires receiver and method candidates"
                )
        elif self.candidate_method_ids:
            raise ValueError("unresolved dispatch evidence cannot retain method candidates")
        return self


class PythonDispatchEvidence(FrozenModel):
    schema_version: Literal["1"] = "1"
    project_id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")
    repository_url: str = Field(min_length=1, max_length=2048)
    base_ref: str = Field(min_length=1, max_length=256)
    base_sha: str = Field(pattern=r"^[0-9a-f]{40,64}$")
    namespace: str = Field(pattern=r"^explicit:repository-dispatch-evidence:[a-zA-Z0-9._-]+$")
    repository_snapshot_ref: str = Field(pattern=r"^artifact://[a-zA-Z0-9._/-]+$")
    repository_snapshot_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    dependency_graph_ref: str = Field(pattern=r"^artifact://[a-zA-Z0-9._/-]+$")
    dependency_graph_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    call_graph_ref: str = Field(pattern=r"^artifact://[a-zA-Z0-9._/-]+$")
    call_graph_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    policy_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    previous_evidence_ref: str | None = Field(
        default=None, pattern=r"^artifact://[a-zA-Z0-9._/-]+$"
    )
    previous_evidence_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    classes: tuple[PythonClassEvidence, ...] = ()
    bases: tuple[PythonBaseEvidence, ...] = ()
    dispatch_sites: tuple[PythonDispatchSite, ...] = ()

    @model_validator(mode="after")
    def validate_evidence(self) -> PythonDispatchEvidence:
        if self.namespace != f"explicit:repository-dispatch-evidence:{self.project_id}":
            raise ValueError("dispatch-evidence namespace does not match project identity")
        if (self.previous_evidence_ref is None) != (self.previous_evidence_sha256 is None):
            raise ValueError("dispatch-evidence predecessor reference and hash must be paired")
        class_ids = tuple(item.class_symbol_id for item in self.classes)
        if class_ids != tuple(sorted(set(class_ids))):
            raise ValueError("dispatch classes must be unique and sorted")
        known_classes = set(class_ids)
        for item in self.classes:
            if any(base not in known_classes for base in item.direct_base_class_ids):
                raise ValueError("dispatch class references an unknown base")
        base_keys = tuple(_base_key(item) for item in self.bases)
        if base_keys != tuple(sorted(set(base_keys))):
            raise ValueError("base evidence must be unique and sorted")
        if any(item.class_symbol_id not in known_classes for item in self.bases):
            raise ValueError("base evidence references an unknown class")
        site_keys = tuple(_site_key(item) for item in self.dispatch_sites)
        if site_keys != tuple(sorted(set(site_keys))):
            raise ValueError("dispatch sites must be unique and sorted")
        if any(
            class_id not in known_classes
            for item in self.dispatch_sites
            for class_id in item.receiver_class_ids
        ):
            raise ValueError("dispatch site references an unknown receiver class")
        return self

    def canonical_content(self) -> str:
        return _canonical_json(self.model_dump(mode="json"))

    def canonical_hash(self) -> str:
        return hashlib.sha256(self.canonical_content().encode("utf-8")).hexdigest()


class RepositoryDispatchEvidenceResult(FrozenModel):
    evidence_ref: str = Field(pattern=r"^artifact://[a-zA-Z0-9._/-]+$")
    evidence_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    evidence: PythonDispatchEvidence
    replayed: bool = False


@dataclass(frozen=True)
class _ParsedFile:
    path: str
    module: str
    tree: ast.Module
    imports: dict[str, tuple[str, str | None]]


class RepositoryDispatchEvidenceService:
    """Build conservative Python dispatch candidates without runtime inference."""

    def __init__(
        self,
        artifacts: ArtifactStore,
        search: SearchService,
        call_graphs: RepositoryCallGraphService,
        *,
        evidence_max_bytes: int = DEFAULT_DISPATCH_EVIDENCE_MAX_BYTES,
        max_source_bytes: int = DEFAULT_DISPATCH_SOURCE_MAX_BYTES,
        max_classes: int = DEFAULT_DISPATCH_MAX_CLASSES,
        max_bases: int = DEFAULT_DISPATCH_MAX_BASES,
        max_sites: int = DEFAULT_DISPATCH_MAX_SITES,
        max_candidates: int = DEFAULT_DISPATCH_MAX_CANDIDATES,
        max_expression_bytes: int = DEFAULT_DISPATCH_MAX_EXPRESSION_BYTES,
    ) -> None:
        limits = (
            evidence_max_bytes,
            max_source_bytes,
            max_classes,
            max_bases,
            max_sites,
            max_candidates,
            max_expression_bytes,
        )
        if any(limit < 1 for limit in limits):
            raise ValueError("repository dispatch-evidence limits must be positive")
        if max_expression_bytes > 4096:
            raise ValueError("dispatch-expression byte limit cannot exceed the schema limit")
        self.artifacts = artifacts
        self.search = search
        self.call_graphs = call_graphs
        self.evidence_max_bytes = evidence_max_bytes
        self.max_source_bytes = max_source_bytes
        self.max_classes = max_classes
        self.max_bases = max_bases
        self.max_sites = max_sites
        self.max_candidates = max_candidates
        self.max_expression_bytes = max_expression_bytes

    @staticmethod
    def namespace(project_id: str) -> str:
        return f"explicit:repository-dispatch-evidence:{project_id}"

    def build_evidence(
        self,
        *,
        project_id: str,
        root: Path,
        expected_call_graph_ref: str,
        expected_call_graph_sha256: str,
        expected_previous_evidence_ref: str | None,
        expected_previous_evidence_sha256: str | None,
    ) -> RepositoryDispatchEvidenceResult:
        self._validate_project_id(project_id)
        if (expected_previous_evidence_ref is None) != (expected_previous_evidence_sha256 is None):
            raise RepositoryDispatchEvidenceError(
                "expected dispatch-evidence predecessor reference and hash must be paired"
            )
        try:
            call_state, call_graph = self.call_graphs.verified_active_graph(
                project_id=project_id,
                expected_graph_ref=expected_call_graph_ref,
                expected_graph_sha256=expected_call_graph_sha256,
            )
            _, _, _, dependency_graph = self.call_graphs.dependencies.verified_active_graph(
                project_id=project_id,
                expected_repository_snapshot_ref=call_state.repository_snapshot_ref,
                expected_repository_snapshot_sha256=call_state.repository_snapshot_sha256,
                expected_graph_ref=call_state.dependency_graph_ref,
                expected_graph_sha256=call_state.dependency_graph_sha256,
            )
        except (RepositoryCallGraphError, ValueError) as exc:
            raise RepositoryDispatchEvidenceError(str(exc)) from exc
        self._verify_clean_base(root, call_graph.base_sha)
        namespace = self.namespace(project_id)
        active = self.search.repository_dispatch_evidence_state(namespace)
        previous: PythonDispatchEvidence | None = None
        if active is None:
            if expected_previous_evidence_sha256 is not None:
                raise RepositoryDispatchEvidenceError(
                    "expected predecessor dispatch evidence does not exist"
                )
        else:
            if (
                active.evidence_ref != expected_previous_evidence_ref
                or active.evidence_sha256 != expected_previous_evidence_sha256
            ):
                raise RepositoryDispatchEvidenceError(
                    "expected predecessor does not match active dispatch evidence"
                )
            previous = self._load_active(active)
            self._verify_compatibility(previous, project_id)
            if active.call_graph_ref == call_state.graph_ref and hmac.compare_digest(
                active.call_graph_sha256, call_state.graph_sha256
            ):
                self._verify_clean_base(root, call_graph.base_sha)
                return RepositoryDispatchEvidenceResult(
                    evidence_ref=active.evidence_ref,
                    evidence_sha256=active.evidence_sha256,
                    evidence=previous,
                    replayed=True,
                )
        evidence = self._derive(
            project_id=project_id,
            root=root,
            call_graph=call_graph,
            call_graph_ref=call_state.graph_ref,
            call_graph_sha256=call_state.graph_sha256,
            dependency_graph=dependency_graph,
            previous_ref=active.evidence_ref if active else None,
            previous_sha256=active.evidence_sha256 if active else None,
        )
        evidence_ref, evidence_sha256 = self._write(evidence)
        self._verify_clean_base(root, call_graph.base_sha)
        state = RepositoryDispatchEvidenceState(
            namespace=namespace,
            project_id=project_id,
            repository_url=call_graph.repository_url,
            base_ref=call_graph.base_ref,
            base_sha=call_graph.base_sha,
            repository_snapshot_ref=call_graph.repository_snapshot_ref,
            repository_snapshot_sha256=call_graph.repository_snapshot_sha256,
            dependency_graph_ref=call_graph.dependency_graph_ref,
            dependency_graph_sha256=call_graph.dependency_graph_sha256,
            call_graph_ref=call_state.graph_ref,
            call_graph_sha256=call_state.graph_sha256,
            evidence_ref=evidence_ref,
            evidence_sha256=evidence_sha256,
            policy_sha256=evidence.policy_sha256,
        )
        try:
            self.search.apply_repository_dispatch_evidence_state(
                state=state,
                expected_previous_evidence_ref=expected_previous_evidence_ref,
                expected_previous_evidence_sha256=expected_previous_evidence_sha256,
            )
        except RepositoryDispatchEvidenceStateError as exc:
            raise RepositoryDispatchEvidenceError(str(exc)) from exc
        return RepositoryDispatchEvidenceResult(
            evidence_ref=evidence_ref,
            evidence_sha256=evidence_sha256,
            evidence=self._load(evidence_ref, evidence_sha256),
        )

    def verified_active_evidence(
        self,
        *,
        project_id: str,
        expected_evidence_ref: str,
        expected_evidence_sha256: str,
    ) -> tuple[RepositoryDispatchEvidenceState, PythonDispatchEvidence]:
        self._validate_project_id(project_id)
        state = self.search.repository_dispatch_evidence_state(self.namespace(project_id))
        if state is None:
            raise RepositoryDispatchEvidenceError(
                "active repository dispatch evidence does not exist"
            )
        if state.evidence_ref != expected_evidence_ref or not hmac.compare_digest(
            state.evidence_sha256, expected_evidence_sha256
        ):
            raise RepositoryDispatchEvidenceError(
                "active dispatch-evidence reference or hash does not match"
            )
        try:
            self.call_graphs.verified_active_graph(
                project_id=project_id,
                expected_graph_ref=state.call_graph_ref,
                expected_graph_sha256=state.call_graph_sha256,
            )
        except RepositoryCallGraphError as exc:
            raise RepositoryDispatchEvidenceError(
                "active dispatch evidence no longer matches its verified call graph"
            ) from exc
        evidence = self._load_active(state)
        self._verify_compatibility(evidence, project_id)
        return state, evidence

    def _derive(
        self,
        *,
        project_id: str,
        root: Path,
        call_graph: PythonCallGraph,
        call_graph_ref: str,
        call_graph_sha256: str,
        dependency_graph: PythonDependencyGraph,
        previous_ref: str | None,
        previous_sha256: str | None,
    ) -> PythonDispatchEvidence:
        parsed = self._parse(root, call_graph, dependency_graph)
        class_symbols = tuple(
            sorted(
                (item for item in call_graph.symbols if item.kind is PythonSymbolKind.CLASS),
                key=lambda item: item.symbol_id,
            )
        )
        if len(class_symbols) > self.max_classes:
            raise RepositoryDispatchEvidenceError("dispatch evidence exceeds its class limit")
        class_by_id = {item.symbol_id: item for item in class_symbols}
        class_lookup: dict[tuple[str, str], list[str]] = defaultdict(list)
        for item in class_symbols:
            class_lookup[(item.module, item.qualname)].append(item.symbol_id)
        unsafe = {(item.module, item.qualname) for item in call_graph.unsafe_symbol_bindings}
        bases: list[PythonBaseEvidence] = []
        direct: dict[str, set[str]] = defaultdict(set)
        unsafe_classes: set[str] = set()
        trees = {item.path: item for item in parsed}
        for symbol in class_symbols:
            node = _find_class_node(trees[symbol.path].tree, symbol)
            if node is None:
                unsafe_classes.add(symbol.symbol_id)
                continue
            if len(node.bases) > 1:
                unsafe_classes.add(symbol.symbol_id)
            for base in node.bases:
                expression = ast.unparse(base)
                if len(expression.encode("utf-8")) > self.max_expression_bytes:
                    raise RepositoryDispatchEvidenceError(
                        "dispatch evidence exceeds its expression limit"
                    )
                candidates, supported = _resolve_class_expression(
                    base,
                    file=trees[symbol.path],
                    owner=symbol,
                    class_lookup=class_lookup,
                    class_by_id=class_by_id,
                    unsafe=unsafe,
                )
                if not supported:
                    resolution = BaseResolution.UNSUPPORTED
                elif len(candidates) == 1:
                    resolution = BaseResolution.RESOLVED
                    direct[symbol.symbol_id].add(candidates[0])
                elif len(candidates) > 1:
                    resolution = BaseResolution.AMBIGUOUS
                else:
                    resolution = BaseResolution.UNRESOLVED
                if resolution is not BaseResolution.RESOLVED:
                    unsafe_classes.add(symbol.symbol_id)
                bases.append(
                    PythonBaseEvidence(
                        class_symbol_id=symbol.symbol_id,
                        expression=expression,
                        line=base.lineno,
                        column=base.col_offset,
                        resolution=resolution,
                        candidate_class_ids=tuple(sorted(candidates)),
                    )
                )
                if len(bases) > self.max_bases:
                    raise RepositoryDispatchEvidenceError(
                        "dispatch evidence exceeds its base limit"
                    )
        unsafe_classes.update(_cyclic_classes(direct))
        descendants: dict[str, set[str]] = {
            item.symbol_id: {item.symbol_id} for item in class_symbols
        }
        for child in class_by_id:
            for parent in _ancestors(child, direct):
                descendants.setdefault(parent, {parent}).add(child)
        methods: dict[tuple[str, str], list[str]] = defaultdict(list)
        for symbol in call_graph.symbols:
            if symbol.kind is PythonSymbolKind.METHOD and symbol.parent_symbol_id is not None:
                if (symbol.module, symbol.qualname) not in unsafe:
                    methods[(symbol.parent_symbol_id, symbol.name)].append(symbol.symbol_id)
        classes = tuple(
            PythonClassEvidence(
                class_symbol_id=symbol.symbol_id,
                path=symbol.path,
                module=symbol.module,
                qualname=symbol.qualname,
                direct_base_class_ids=tuple(sorted(direct.get(symbol.symbol_id, ()))),
                hierarchy_safe=symbol.symbol_id not in unsafe_classes,
            )
            for symbol in class_symbols
        )
        dynamic_keys = {
            (item.source_path, item.caller_symbol_id, item.line, item.column, item.expression)
            for item in call_graph.unresolved_calls
            if item.reason is UnresolvedCallReason.DYNAMIC_RECEIVER
            and item.caller_symbol_id is not None
        }
        collector = _DispatchCollector(
            parsed=parsed,
            call_graph=call_graph,
            class_lookup=class_lookup,
            class_by_id=class_by_id,
            unsafe=unsafe,
            direct=direct,
            descendants=descendants,
            unsafe_classes=unsafe_classes,
            methods=methods,
            dynamic_keys=dynamic_keys,
            max_sites=self.max_sites,
            max_candidates=self.max_candidates,
            max_expression_bytes=self.max_expression_bytes,
        )
        sites = collector.collect()
        try:
            evidence = PythonDispatchEvidence(
                project_id=project_id,
                repository_url=call_graph.repository_url,
                base_ref=call_graph.base_ref,
                base_sha=call_graph.base_sha,
                namespace=self.namespace(project_id),
                repository_snapshot_ref=call_graph.repository_snapshot_ref,
                repository_snapshot_sha256=call_graph.repository_snapshot_sha256,
                dependency_graph_ref=call_graph.dependency_graph_ref,
                dependency_graph_sha256=call_graph.dependency_graph_sha256,
                call_graph_ref=call_graph_ref,
                call_graph_sha256=call_graph_sha256,
                policy_sha256=self._policy_sha256(),
                previous_evidence_ref=previous_ref,
                previous_evidence_sha256=previous_sha256,
                classes=classes,
                bases=tuple(sorted(bases, key=_base_key)),
                dispatch_sites=sites,
            )
        except ValueError as exc:
            raise RepositoryDispatchEvidenceError(
                "repository dispatch evidence failed canonical validation"
            ) from exc
        if len(evidence.canonical_content().encode("utf-8")) > self.evidence_max_bytes:
            raise RepositoryDispatchEvidenceError("dispatch evidence exceeds its byte limit")
        return evidence

    def _parse(
        self,
        root: Path,
        call_graph: PythonCallGraph,
        dependency_graph: PythonDependencyGraph,
    ) -> tuple[_ParsedFile, ...]:
        root = root.resolve()
        module_by_path = {item.path: item.module for item in dependency_graph.nodes}
        edge_targets = {
            (item.source_path, item.raw_import): module_by_path[item.target_path]
            for item in dependency_graph.edges
        }
        total = 0
        parsed: list[_ParsedFile] = []
        for file in call_graph.files:
            if file.parse_failure is not None:
                continue
            path = (root / file.path).resolve()
            if path == root or root not in path.parents:
                raise RepositoryDispatchEvidenceError("Python source path escapes the source root")
            try:
                data = path.read_bytes()
            except OSError as exc:
                raise RepositoryDispatchEvidenceError("Python source cannot be read") from exc
            total += len(data)
            if total > self.max_source_bytes:
                raise RepositoryDispatchEvidenceError(
                    "dispatch evidence exceeds its source-byte limit"
                )
            if not hmac.compare_digest(hashlib.sha256(data).hexdigest(), file.sha256):
                raise RepositoryDispatchEvidenceError(
                    "Python source drifted from the verified call graph"
                )
            try:
                tree = ast.parse(data.decode("utf-8"), filename=file.path)
            except (UnicodeError, SyntaxError, ValueError, RecursionError) as exc:
                raise RepositoryDispatchEvidenceError(
                    "verified Python source no longer parses identically"
                ) from exc
            parsed.append(
                _ParsedFile(
                    path=file.path,
                    module=file.module,
                    tree=tree,
                    imports=_import_bindings(tree, file.path, edge_targets),
                )
            )
        return tuple(parsed)

    def _write(self, evidence: PythonDispatchEvidence) -> tuple[str, str]:
        content = evidence.canonical_content()
        if len(content.encode("utf-8")) > self.evidence_max_bytes:
            raise RepositoryDispatchEvidenceError("dispatch evidence exceeds its byte limit")
        digest = evidence.canonical_hash()
        reference = self.artifacts.write_text(
            f"dispatch-evidence/{evidence.project_id}/{evidence.base_sha}/evidence-{digest}.json",
            content,
            "application/json",
        )
        if not hmac.compare_digest(reference.sha256, digest):
            raise RepositoryDispatchEvidenceError("dispatch-evidence artifact hash mismatch")
        return reference.uri, digest

    def _load(self, reference: str, expected_sha256: str) -> PythonDispatchEvidence:
        try:
            content = self.artifacts.read_text_bounded_verified(
                reference,
                expected_sha256=expected_sha256,
                max_bytes=self.evidence_max_bytes,
            )
            evidence = PythonDispatchEvidence.model_validate_json(content)
        except (OSError, UnicodeError, ValueError) as exc:
            raise RepositoryDispatchEvidenceError(
                "dispatch evidence failed bounded integrity verification"
            ) from exc
        if not hmac.compare_digest(evidence.canonical_hash(), expected_sha256):
            raise RepositoryDispatchEvidenceError("dispatch-evidence canonical hash mismatch")
        return evidence

    def _load_active(self, state: RepositoryDispatchEvidenceState) -> PythonDispatchEvidence:
        evidence = self._load(state.evidence_ref, state.evidence_sha256)
        expected = (
            state.namespace,
            state.project_id,
            state.repository_url,
            state.base_ref,
            state.base_sha,
            state.repository_snapshot_ref,
            state.repository_snapshot_sha256,
            state.dependency_graph_ref,
            state.dependency_graph_sha256,
            state.call_graph_ref,
            state.call_graph_sha256,
            state.policy_sha256,
        )
        actual = (
            evidence.namespace,
            evidence.project_id,
            evidence.repository_url,
            evidence.base_ref,
            evidence.base_sha,
            evidence.repository_snapshot_ref,
            evidence.repository_snapshot_sha256,
            evidence.dependency_graph_ref,
            evidence.dependency_graph_sha256,
            evidence.call_graph_ref,
            evidence.call_graph_sha256,
            evidence.policy_sha256,
        )
        if actual != expected:
            raise RepositoryDispatchEvidenceError(
                "active dispatch-evidence state does not match artifact provenance"
            )
        return evidence

    def _verify_compatibility(self, evidence: PythonDispatchEvidence, project_id: str) -> None:
        if evidence.project_id != project_id or evidence.namespace != self.namespace(project_id):
            raise RepositoryDispatchEvidenceError("dispatch-evidence project scope does not match")
        if not hmac.compare_digest(evidence.policy_sha256, self._policy_sha256()):
            raise RepositoryDispatchEvidenceError("dispatch-evidence policy does not match")

    def _verify_clean_base(self, root: Path, base_sha: str) -> None:
        try:
            self.call_graphs._verify_clean_base(root, base_sha)
        except RepositoryCallGraphError as exc:
            raise RepositoryDispatchEvidenceError(str(exc)) from exc

    def _policy_sha256(self) -> str:
        return hashlib.sha256(
            _canonical_json(
                {
                    "schema_version": "1",
                    "dispatch_evidence_policy_version": DISPATCH_EVIDENCE_POLICY_VERSION,
                    "call_graph_policy_version": CALL_GRAPH_POLICY_VERSION,
                    "resolver": "python-conservative-dynamic-dispatch-v1",
                    "evidence_max_bytes": self.evidence_max_bytes,
                    "max_source_bytes": self.max_source_bytes,
                    "max_classes": self.max_classes,
                    "max_bases": self.max_bases,
                    "max_sites": self.max_sites,
                    "max_candidates": self.max_candidates,
                    "max_expression_bytes": self.max_expression_bytes,
                }
            ).encode("utf-8")
        ).hexdigest()

    @staticmethod
    def _validate_project_id(project_id: str) -> None:
        if not _PROJECT_ID.fullmatch(project_id):
            raise RepositoryDispatchEvidenceError("project ID is invalid")


class _DispatchCollector(ast.NodeVisitor):
    def __init__(
        self,
        *,
        parsed: tuple[_ParsedFile, ...],
        call_graph: PythonCallGraph,
        class_lookup: dict[tuple[str, str], list[str]],
        class_by_id: dict[str, PythonSymbol],
        unsafe: set[tuple[str, str]],
        direct: dict[str, set[str]],
        descendants: dict[str, set[str]],
        unsafe_classes: set[str],
        methods: dict[tuple[str, str], list[str]],
        dynamic_keys: set[tuple[str, str, int, int, str]],
        max_sites: int,
        max_candidates: int,
        max_expression_bytes: int,
    ) -> None:
        self.parsed = parsed
        self.symbols = call_graph.symbols
        self.class_lookup = class_lookup
        self.class_by_id = class_by_id
        self.unsafe = unsafe
        self.direct = direct
        self.descendants = descendants
        self.unsafe_classes = unsafe_classes
        self.methods = methods
        self.dynamic_keys = dynamic_keys
        self.max_sites = max_sites
        self.max_candidates = max_candidates
        self.max_expression_bytes = max_expression_bytes
        self.file: _ParsedFile | None = None
        self.current_symbol: PythonSymbol | None = None
        self.bindings: dict[str, str | None] = {}
        self.sites: list[PythonDispatchSite] = []
        self.candidate_count = 0

    def collect(self) -> tuple[PythonDispatchSite, ...]:
        for file in self.parsed:
            self.file = file
            self.current_symbol = None
            self.bindings = {}
            self.visit(file.tree)
        return tuple(sorted(self.sites, key=_site_key))

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_function(node)

    def _visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        if self.file is None:
            raise RepositoryDispatchEvidenceError("dispatch traversal has no source file")
        symbol = _find_symbol(self.symbols, self.file.path, node)
        if symbol is None:
            return
        prior_symbol, prior_bindings = self.current_symbol, self.bindings
        self.current_symbol = symbol
        self.bindings = {}
        parent = self.class_by_id.get(symbol.parent_symbol_id or "")
        positional = [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]
        for argument in positional:
            if argument.annotation is None:
                continue
            candidates, supported = _resolve_class_expression(
                argument.annotation,
                file=self.file,
                owner=symbol,
                class_lookup=self.class_lookup,
                class_by_id=self.class_by_id,
                unsafe=self.unsafe,
            )
            self.bindings[argument.arg] = (
                candidates[0] if supported and len(candidates) == 1 else None
            )
        if parent is not None and positional and not node.decorator_list:
            self.bindings[positional[0].arg] = parent.symbol_id
        for statement in node.body:
            self.visit(statement)
        self.current_symbol, self.bindings = prior_symbol, prior_bindings

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        for statement in node.body:
            self.visit(statement)

    def visit_If(self, node: ast.If) -> None:
        self._visit_conditionally(node)

    def visit_For(self, node: ast.For) -> None:
        self._visit_conditionally(node)

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        self._visit_conditionally(node)

    def visit_While(self, node: ast.While) -> None:
        self._visit_conditionally(node)

    def visit_Try(self, node: ast.Try) -> None:
        self._visit_conditionally(node)

    def visit_With(self, node: ast.With) -> None:
        self._visit_conditionally(node)

    def visit_AsyncWith(self, node: ast.AsyncWith) -> None:
        self._visit_conditionally(node)

    def visit_Match(self, node: ast.Match) -> None:
        self._visit_conditionally(node)

    def _visit_conditionally(self, node: ast.AST) -> None:
        for child in ast.walk(node):
            if isinstance(child, ast.Name) and isinstance(child.ctx, (ast.Store, ast.Del)):
                self.bindings[child.id] = None
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        self.visit(node.value)
        if self.current_symbol is None:
            return
        class_id = self._constructor_class(node.value)
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            prior = self.bindings.get(name, class_id)
            self.bindings[name] = class_id if prior == class_id else None
            return
        for target in node.targets:
            for name in _stored_names(target):
                self.bindings[name] = None

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if node.value is not None:
            self.visit(node.value)
        if self.current_symbol is None or not isinstance(node.target, ast.Name):
            return
        if self.file is None:
            raise RepositoryDispatchEvidenceError("dispatch traversal has no source file")
        candidates, supported = _resolve_class_expression(
            node.annotation,
            file=self.file,
            owner=self.current_symbol,
            class_lookup=self.class_lookup,
            class_by_id=self.class_by_id,
            unsafe=self.unsafe,
        )
        annotated = candidates[0] if supported and len(candidates) == 1 else None
        constructed = self._constructor_class(node.value) if node.value is not None else None
        self.bindings[node.target.id] = constructed if constructed == annotated else None

    def visit_Name(self, node: ast.Name) -> None:
        if self.current_symbol is not None and isinstance(node.ctx, (ast.Store, ast.Del)):
            self.bindings[node.id] = None

    def visit_Call(self, node: ast.Call) -> None:
        if self.file is not None and self.current_symbol is not None:
            expression = ast.unparse(node.func)
            key = (
                self.file.path,
                self.current_symbol.symbol_id,
                node.lineno,
                node.col_offset,
                expression,
            )
            if key in self.dynamic_keys:
                self._record(node, expression)
        self.generic_visit(node)

    def _record(self, node: ast.Call, expression: str) -> None:
        if len(self.sites) >= self.max_sites:
            raise RepositoryDispatchEvidenceError("dispatch evidence exceeds its site limit")
        if len(expression.encode("utf-8")) > self.max_expression_bytes:
            raise RepositoryDispatchEvidenceError("dispatch evidence exceeds its expression limit")
        if not isinstance(node.func, ast.Attribute):
            raise RepositoryDispatchEvidenceError(
                "dynamic-receiver evidence does not identify an attribute call"
            )
        receiver = node.func.value
        receiver_expression = ast.unparse(receiver)
        declared: str | None = None
        resolution = DispatchResolution.UNSUPPORTED_RECEIVER
        if isinstance(receiver, ast.Name):
            declared = self.bindings.get(receiver.id)
            resolution = (
                DispatchResolution.UNKNOWN_RECEIVER
                if receiver.id not in self.bindings
                else DispatchResolution.AMBIGUOUS_RECEIVER
            )
        receiver_ids: tuple[str, ...] = ()
        method_ids: tuple[str, ...] = ()
        if declared is not None:
            possible = tuple(sorted(self.descendants.get(declared, {declared})))
            receiver_ids = possible
            if any(item in self.unsafe_classes for item in possible):
                resolution = DispatchResolution.UNSAFE_HIERARCHY
            else:
                targets: set[str] = set()
                missing = False
                for class_id in possible:
                    target = _method_target(class_id, node.func.attr, self.direct, self.methods)
                    if target is None:
                        missing = True
                    else:
                        targets.add(target)
                if missing or not targets:
                    resolution = DispatchResolution.MISSING_METHOD
                else:
                    method_ids = tuple(sorted(targets))
                    resolution = (
                        DispatchResolution.EXACT_DECLARED_TYPE
                        if len(possible) == 1
                        else DispatchResolution.POLYMORPHIC_CANDIDATES
                    )
        self.candidate_count += len(receiver_ids) + len(method_ids)
        if self.candidate_count > self.max_candidates:
            raise RepositoryDispatchEvidenceError("dispatch evidence exceeds its candidate limit")
        self.sites.append(
            PythonDispatchSite(
                source_path=self.file.path,
                caller_symbol_id=self.current_symbol.symbol_id,
                line=node.lineno,
                column=node.col_offset,
                expression=expression,
                receiver_expression=receiver_expression,
                method_name=node.func.attr,
                resolution=resolution,
                receiver_class_ids=receiver_ids,
                candidate_method_ids=method_ids,
            )
        )

    def _constructor_class(self, node: ast.expr | None) -> str | None:
        if not isinstance(node, ast.Call) or self.file is None or self.current_symbol is None:
            return None
        candidates, supported = _resolve_class_expression(
            node.func,
            file=self.file,
            owner=self.current_symbol,
            class_lookup=self.class_lookup,
            class_by_id=self.class_by_id,
            unsafe=self.unsafe,
        )
        return candidates[0] if supported and len(candidates) == 1 else None


def _resolve_class_expression(
    node: ast.expr | None,
    *,
    file: _ParsedFile,
    owner: PythonSymbol,
    class_lookup: dict[tuple[str, str], list[str]],
    class_by_id: dict[str, PythonSymbol],
    unsafe: set[tuple[str, str]],
) -> tuple[tuple[str, ...], bool]:
    if node is None:
        return (), True
    module: str
    qualname: str
    if isinstance(node, ast.Name):
        imported = file.imports.get(node.id)
        if imported is not None:
            module, imported_name = imported
            if imported_name is None:
                return (), False
            qualname = imported_name
        else:
            module, qualname = file.module, node.id
    elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
        imported = file.imports.get(node.value.id)
        if imported is None or imported[1] is not None:
            return (), False
        module, qualname = imported[0], node.attr
    else:
        return (), False
    if (module, qualname) in unsafe:
        return (), True
    candidates = tuple(
        sorted(
            item
            for item in class_lookup.get((module, qualname), ())
            if class_by_id[item].parent_symbol_id is None
        )
    )
    return candidates, True


def _import_bindings(
    tree: ast.Module,
    path: str,
    edge_targets: dict[tuple[str, str], str],
) -> dict[str, tuple[str, str | None]]:
    bindings: dict[str, tuple[str, str | None]] = {}
    ambiguous: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                target = edge_targets.get((path, alias.name))
                if target is None:
                    continue
                name = alias.asname or alias.name.split(".", 1)[0]
                value = (target, None)
                if name in bindings and bindings[name] != value:
                    ambiguous.add(name)
                bindings[name] = value
        elif isinstance(node, ast.ImportFrom):
            module_text = f"{'.' * node.level}{node.module or ''}"
            for alias in node.names:
                if alias.name == "*":
                    continue
                target = edge_targets.get((path, f"{module_text}:{alias.name}"))
                if target is None:
                    continue
                name = alias.asname or alias.name
                value = (target, alias.name)
                if name in bindings and bindings[name] != value:
                    ambiguous.add(name)
                bindings[name] = value
        elif not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            for child in ast.walk(node):
                if isinstance(child, ast.Name) and isinstance(child.ctx, (ast.Store, ast.Del)):
                    ambiguous.add(child.id)
    for name in ambiguous:
        bindings.pop(name, None)
    return bindings


def _find_class_node(tree: ast.Module, symbol: PythonSymbol) -> ast.ClassDef | None:
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.ClassDef)
            and node.lineno == symbol.line
            and node.col_offset == symbol.column
            and node.name == symbol.name
        ):
            return node
    return None


def _find_symbol(
    symbols: tuple[PythonSymbol, ...], path: str, node: ast.FunctionDef | ast.AsyncFunctionDef
) -> PythonSymbol | None:
    for symbol in symbols:
        if (
            symbol.path == path
            and symbol.line == node.lineno
            and symbol.column == node.col_offset
            and symbol.name == node.name
            and symbol.kind in {PythonSymbolKind.FUNCTION, PythonSymbolKind.METHOD}
        ):
            return symbol
    return None


def _stored_names(node: ast.expr) -> tuple[str, ...]:
    return tuple(item.id for item in ast.walk(node) if isinstance(item, ast.Name))


def _cyclic_classes(direct: dict[str, set[str]]) -> set[str]:
    cyclic: set[str] = set()
    for start in direct:
        stack: list[tuple[str, tuple[str, ...]]] = [(start, ())]
        while stack:
            current, path = stack.pop()
            if current in path:
                cyclic.update(path[path.index(current) :])
                continue
            stack.extend((base, (*path, current)) for base in direct.get(current, ()))
    return cyclic


def _ancestors(class_id: str, direct: dict[str, set[str]]) -> set[str]:
    found: set[str] = set()
    pending = list(direct.get(class_id, ()))
    while pending:
        item = pending.pop()
        if item in found:
            continue
        found.add(item)
        pending.extend(direct.get(item, ()))
    return found


def _method_target(
    class_id: str,
    method_name: str,
    direct: dict[str, set[str]],
    methods: dict[tuple[str, str], list[str]],
) -> str | None:
    current = class_id
    seen: set[str] = set()
    while current not in seen:
        seen.add(current)
        candidates = methods.get((current, method_name), ())
        if len(candidates) == 1:
            return candidates[0]
        bases = direct.get(current, set())
        if len(bases) != 1:
            return None
        current = next(iter(bases))
    return None


def _base_key(item: PythonBaseEvidence) -> tuple[object, ...]:
    return (item.class_symbol_id, item.line, item.column, item.expression, item.resolution.value)


def _site_key(item: PythonDispatchSite) -> tuple[object, ...]:
    return (
        item.source_path,
        item.caller_symbol_id,
        item.line,
        item.column,
        item.expression,
        item.resolution.value,
    )


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
