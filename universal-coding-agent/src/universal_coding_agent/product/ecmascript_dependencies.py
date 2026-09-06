from __future__ import annotations

import hashlib
import hmac
import json
import re
from collections import defaultdict, deque
from enum import StrEnum
from pathlib import PurePosixPath
from typing import Literal

from pydantic import Field, field_validator, model_validator

from universal_coding_agent.core.models import FrozenModel
from universal_coding_agent.core.safe_models import normalize_repository_path
from universal_coding_agent.product.repository_indexes import (
    RepositoryIndexError,
    RepositoryIndexService,
    RepositoryIndexSnapshot,
)
from universal_coding_agent.product.search_service import (
    RepositoryDependencyGraphState,
    RepositoryDependencyGraphStateError,
    RepositorySearchIndexState,
    SearchService,
)
from universal_coding_agent.repository.indexer import INDEX_POLICY_VERSION
from universal_coding_agent.storage.artifacts import ArtifactStore

DEFAULT_ECMASCRIPT_DEPENDENCY_GRAPH_MAX_BYTES = 8_000_000
DEFAULT_ECMASCRIPT_DEPENDENCY_IMPACT_MAX_BYTES = 2_000_000
DEFAULT_ECMASCRIPT_DEPENDENCY_GRAPH_MAX_NODES = 20_000
DEFAULT_ECMASCRIPT_DEPENDENCY_GRAPH_MAX_EDGES = 100_000
DEFAULT_ECMASCRIPT_DEPENDENCY_GRAPH_MAX_UNRESOLVED = 100_000
DEFAULT_ECMASCRIPT_DEPENDENCY_IMPACT_MAX_NODES = 10_000
DEFAULT_ECMASCRIPT_DEPENDENCY_IMPACT_MAX_DEPTH = 12
ECMASCRIPT_DEPENDENCY_GRAPH_POLICY_VERSION = "1"

_PROJECT_ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")
_URL_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
_REFERENCE_KINDS = frozenset(
    {
        "esm-import",
        "esm-export",
        "ts-import-equals",
    }
)
_ECMASCRIPT_LANGUAGES = frozenset({"javascript", "typescript"})
_EXTENSIONLESS_FILE_SUFFIXES = (".ts", ".tsx", ".d.ts", ".js", ".jsx")
_TYPESCRIPT_EXTENSION_SUBSTITUTIONS = {
    ".js": (".ts", ".tsx", ".d.ts", ".js", ".jsx"),
    ".mjs": (".mts", ".d.mts", ".mjs"),
    ".cjs": (".cts", ".d.cts", ".cjs"),
}
_RECOGNIZED_EXPLICIT_SUFFIXES = tuple(
    sorted(
        {
            ".d.mts",
            ".d.cts",
            ".d.ts",
            ".ts",
            ".tsx",
            ".mts",
            ".cts",
            ".js",
            ".jsx",
            ".mjs",
            ".cjs",
        },
        key=lambda value: (-len(value), value),
    )
)


class RepositoryECMAScriptDependencyError(ValueError):
    """ECMAScript dependency evidence cannot satisfy its bounded provenance contract."""


class ECMAScriptReferenceKind(StrEnum):
    ESM_IMPORT = "esm-import"
    ESM_EXPORT = "esm-export"
    TYPESCRIPT_IMPORT_EQUALS = "ts-import-equals"


class ECMAScriptResolutionBasis(StrEnum):
    EXACT_RELATIVE = "exact_relative"
    TYPESCRIPT_EXTENSION_SUBSTITUTION = "typescript_extension_substitution"
    UNIQUE_EXTENSION_CANDIDATE = "unique_extension_candidate"
    UNIQUE_DIRECTORY_INDEX_CANDIDATE = "unique_directory_index_candidate"


class ECMAScriptUnresolvedReason(StrEnum):
    BARE_OR_EXTERNAL = "bare_or_external"
    ABSOLUTE_OR_URL = "absolute_or_url"
    RELATIVE_OUTSIDE_REPOSITORY = "relative_outside_repository"
    UNSUPPORTED_TARGET_TYPE = "unsupported_target_type"
    MISSING_TARGET = "missing_target"
    AMBIGUOUS_TARGET = "ambiguous_target"
    INVALID_REFERENCE = "invalid_reference"


class ECMAScriptDependencyNode(FrozenModel):
    path: str = Field(min_length=1, max_length=4096)
    language: Literal["javascript", "typescript"]
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    is_test: bool = False
    module_references: tuple[str, ...] = ()

    @field_validator("path")
    @classmethod
    def validate_path(cls, value: str) -> str:
        return normalize_repository_path(value)

    @field_validator("module_references")
    @classmethod
    def validate_module_references(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        if values != tuple(sorted(set(values))):
            raise ValueError("ECMAScript module references must be unique and sorted")
        if any(not value or len(value) > 8192 for value in values):
            raise ValueError("ECMAScript module reference is empty or oversized")
        return values


class ECMAScriptDependencyEdge(FrozenModel):
    source_path: str = Field(min_length=1, max_length=4096)
    target_path: str = Field(min_length=1, max_length=4096)
    reference_kind: ECMAScriptReferenceKind
    module_specifier: str = Field(min_length=1, max_length=4096)
    resolution_basis: ECMAScriptResolutionBasis

    @field_validator("source_path", "target_path")
    @classmethod
    def validate_path(cls, value: str) -> str:
        return normalize_repository_path(value)


class ECMAScriptUnresolvedReference(FrozenModel):
    source_path: str = Field(min_length=1, max_length=4096)
    raw_reference: str = Field(min_length=1, max_length=8192)
    module_specifier: str = Field(default="", max_length=4096)
    reason: ECMAScriptUnresolvedReason
    candidate_paths: tuple[str, ...] = ()

    @field_validator("source_path")
    @classmethod
    def validate_source_path(cls, value: str) -> str:
        return normalize_repository_path(value)

    @field_validator("candidate_paths")
    @classmethod
    def validate_candidate_paths(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(normalize_repository_path(value) for value in values)
        if normalized != tuple(sorted(set(normalized))):
            raise ValueError("unresolved ECMAScript candidates must be unique and sorted")
        return normalized


class ECMAScriptDependencyGraphDelta(FrozenModel):
    reused_paths: tuple[str, ...] = ()
    recomputed_paths: tuple[str, ...] = ()
    deleted_paths: tuple[str, ...] = ()

    @field_validator("reused_paths", "recomputed_paths", "deleted_paths")
    @classmethod
    def validate_paths(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(normalize_repository_path(value) for value in values)
        if normalized != tuple(sorted(set(normalized))):
            raise ValueError("ECMAScript graph delta paths must be unique and sorted")
        return normalized


class ECMAScriptDependencyGraph(FrozenModel):
    schema_version: Literal["1"] = "1"
    project_id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")
    repository_url: str = Field(min_length=1, max_length=2048)
    base_ref: str = Field(min_length=1, max_length=256)
    base_sha: str = Field(pattern=r"^[0-9a-f]{40,64}$")
    namespace: str = Field(pattern=r"^explicit:ecmascript-dependency-graph:[a-zA-Z0-9._-]+$")
    repository_snapshot_ref: str = Field(pattern=r"^artifact://[a-zA-Z0-9._/-]+$")
    repository_snapshot_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    policy_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    candidate_map_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    previous_graph_ref: str | None = Field(
        default=None,
        pattern=r"^artifact://[a-zA-Z0-9._/-]+$",
    )
    previous_graph_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    nodes: tuple[ECMAScriptDependencyNode, ...] = ()
    edges: tuple[ECMAScriptDependencyEdge, ...] = ()
    unresolved_references: tuple[ECMAScriptUnresolvedReference, ...] = ()
    delta: ECMAScriptDependencyGraphDelta

    @model_validator(mode="after")
    def validate_graph(self) -> ECMAScriptDependencyGraph:
        expected_namespace = f"explicit:ecmascript-dependency-graph:{self.project_id}"
        if self.namespace != expected_namespace:
            raise ValueError("ECMAScript graph namespace does not match project identity")
        if (self.previous_graph_ref is None) != (self.previous_graph_sha256 is None):
            raise ValueError("ECMAScript graph predecessor reference and hash must be paired")
        node_paths = tuple(node.path for node in self.nodes)
        if node_paths != tuple(sorted(set(node_paths))):
            raise ValueError("ECMAScript graph nodes must be unique and sorted")
        edge_keys = tuple(_edge_key(edge) for edge in self.edges)
        if edge_keys != tuple(sorted(set(edge_keys))):
            raise ValueError("ECMAScript graph edges must be unique and sorted")
        unresolved_keys = tuple(_unresolved_key(item) for item in self.unresolved_references)
        if unresolved_keys != tuple(sorted(set(unresolved_keys))):
            raise ValueError("unresolved ECMAScript references must be unique and sorted")
        known = set(node_paths)
        if any(
            edge.source_path not in known or edge.target_path not in known for edge in self.edges
        ):
            raise ValueError("ECMAScript graph edge references an unknown node")
        if any(item.source_path not in known for item in self.unresolved_references):
            raise ValueError("unresolved ECMAScript reference has an unknown source")
        reused = set(self.delta.reused_paths)
        recomputed = set(self.delta.recomputed_paths)
        deleted = set(self.delta.deleted_paths)
        if reused & recomputed:
            raise ValueError("ECMAScript graph reused and recomputed paths overlap")
        if reused | recomputed != known:
            raise ValueError("ECMAScript graph delta does not cover every current node")
        if deleted & known:
            raise ValueError("ECMAScript graph deleted paths remain in the current graph")
        return self

    def canonical_content(self) -> str:
        return _canonical_json(self.model_dump(mode="json"))

    def canonical_hash(self) -> str:
        return hashlib.sha256(self.canonical_content().encode("utf-8")).hexdigest()


class ECMAScriptImpactConfidence(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"


class ECMAScriptDependencyImpactItem(FrozenModel):
    path: str = Field(min_length=1, max_length=4096)
    changed_path: str = Field(min_length=1, max_length=4096)
    is_test: bool
    present_in_current_snapshot: bool
    depth: int = Field(ge=0)
    confidence: ECMAScriptImpactConfidence
    dependency_chain: tuple[str, ...] = Field(min_length=1)
    reference_chain: tuple[str, ...] = ()
    resolution_chain: tuple[ECMAScriptResolutionBasis, ...] = ()

    @field_validator("path", "changed_path")
    @classmethod
    def validate_path(cls, value: str) -> str:
        return normalize_repository_path(value)

    @field_validator("dependency_chain")
    @classmethod
    def validate_chain(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(normalize_repository_path(value) for value in values)

    @model_validator(mode="after")
    def validate_evidence_chain(self) -> ECMAScriptDependencyImpactItem:
        if self.dependency_chain[0] != self.changed_path:
            raise ValueError("ECMAScript impact chain must begin with the changed path")
        if self.dependency_chain[-1] != self.path:
            raise ValueError("ECMAScript impact chain must end with the impacted path")
        if self.depth != len(self.dependency_chain) - 1:
            raise ValueError("ECMAScript impact depth does not match its dependency chain")
        if len(self.reference_chain) != self.depth:
            raise ValueError("ECMAScript impact reference chain does not match its depth")
        if len(self.resolution_chain) != self.depth:
            raise ValueError("ECMAScript impact resolution chain does not match its depth")
        if self.confidence != _impact_confidence(self.depth, self.resolution_chain):
            raise ValueError("ECMAScript impact confidence does not match its evidence")
        return self


class ECMAScriptDependencyImpactReport(FrozenModel):
    schema_version: Literal["1"] = "1"
    project_id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")
    repository_url: str = Field(min_length=1, max_length=2048)
    base_ref: str = Field(min_length=1, max_length=256)
    base_sha: str = Field(pattern=r"^[0-9a-f]{40,64}$")
    repository_snapshot_ref: str = Field(pattern=r"^artifact://[a-zA-Z0-9._/-]+$")
    repository_snapshot_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    graph_ref: str = Field(pattern=r"^artifact://[a-zA-Z0-9._/-]+$")
    graph_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    previous_graph_ref: str | None = Field(
        default=None,
        pattern=r"^artifact://[a-zA-Z0-9._/-]+$",
    )
    previous_graph_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    changed_paths: tuple[str, ...]
    impacted_sources: tuple[ECMAScriptDependencyImpactItem, ...] = ()
    impacted_tests: tuple[ECMAScriptDependencyImpactItem, ...] = ()

    @field_validator("changed_paths")
    @classmethod
    def validate_changed_paths(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(normalize_repository_path(value) for value in values)
        if normalized != tuple(sorted(set(normalized))):
            raise ValueError("ECMAScript impact changed paths must be unique and sorted")
        return normalized

    @model_validator(mode="after")
    def validate_report(self) -> ECMAScriptDependencyImpactReport:
        if (self.previous_graph_ref is None) != (self.previous_graph_sha256 is None):
            raise ValueError("ECMAScript impact predecessor reference and hash must be paired")
        source_paths = tuple(item.path for item in self.impacted_sources)
        test_paths = tuple(item.path for item in self.impacted_tests)
        if source_paths != tuple(sorted(set(source_paths))):
            raise ValueError("impacted ECMAScript sources must be unique and sorted")
        if test_paths != tuple(sorted(set(test_paths))):
            raise ValueError("impacted ECMAScript tests must be unique and sorted")
        if any(item.is_test for item in self.impacted_sources):
            raise ValueError("impacted ECMAScript source result contains a test")
        if any(
            not item.is_test or not item.present_in_current_snapshot for item in self.impacted_tests
        ):
            raise ValueError("impacted ECMAScript tests must be current tracked tests")
        return self

    def canonical_content(self) -> str:
        return _canonical_json(self.model_dump(mode="json"))

    def canonical_hash(self) -> str:
        return hashlib.sha256(self.canonical_content().encode("utf-8")).hexdigest()


class RepositoryECMAScriptDependencyGraphResult(FrozenModel):
    graph_ref: str = Field(pattern=r"^artifact://[a-zA-Z0-9._/-]+$")
    graph_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    graph: ECMAScriptDependencyGraph
    replayed: bool = False


class RepositoryECMAScriptDependencyImpactResult(FrozenModel):
    report_ref: str = Field(pattern=r"^artifact://[a-zA-Z0-9._/-]+$")
    report_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    report: ECMAScriptDependencyImpactReport


class RepositoryECMAScriptDependencyService:
    """Build bounded ECMAScript dependency evidence from verified snapshots."""

    def __init__(
        self,
        artifacts: ArtifactStore,
        search: SearchService,
        repository_indexes: RepositoryIndexService,
        *,
        graph_max_bytes: int = DEFAULT_ECMASCRIPT_DEPENDENCY_GRAPH_MAX_BYTES,
        impact_max_bytes: int = DEFAULT_ECMASCRIPT_DEPENDENCY_IMPACT_MAX_BYTES,
        max_nodes: int = DEFAULT_ECMASCRIPT_DEPENDENCY_GRAPH_MAX_NODES,
        max_edges: int = DEFAULT_ECMASCRIPT_DEPENDENCY_GRAPH_MAX_EDGES,
        max_unresolved: int = DEFAULT_ECMASCRIPT_DEPENDENCY_GRAPH_MAX_UNRESOLVED,
        max_impact_nodes: int = DEFAULT_ECMASCRIPT_DEPENDENCY_IMPACT_MAX_NODES,
        max_impact_depth: int = DEFAULT_ECMASCRIPT_DEPENDENCY_IMPACT_MAX_DEPTH,
    ) -> None:
        limits = (
            graph_max_bytes,
            impact_max_bytes,
            max_nodes,
            max_edges,
            max_unresolved,
            max_impact_nodes,
            max_impact_depth,
        )
        if any(limit < 1 for limit in limits):
            raise ValueError("ECMAScript dependency limits must be positive")
        self.artifacts = artifacts
        self.search = search
        self.repository_indexes = repository_indexes
        self.graph_max_bytes = graph_max_bytes
        self.impact_max_bytes = impact_max_bytes
        self.max_nodes = max_nodes
        self.max_edges = max_edges
        self.max_unresolved = max_unresolved
        self.max_impact_nodes = max_impact_nodes
        self.max_impact_depth = max_impact_depth

    def build_graph(
        self,
        *,
        project_id: str,
        expected_repository_snapshot_sha256: str,
        expected_previous_graph_sha256: str | None,
    ) -> RepositoryECMAScriptDependencyGraphResult:
        self._validate_project_id(project_id)
        try:
            repository_state, snapshot = self.repository_indexes.verified_active_snapshot(
                project_id,
                expected_snapshot_sha256=expected_repository_snapshot_sha256,
            )
        except RepositoryIndexError as exc:
            raise RepositoryECMAScriptDependencyError(str(exc)) from exc
        namespace = self.namespace(project_id)
        active_state = self.search.repository_dependency_graph_state(namespace)
        previous: ECMAScriptDependencyGraph | None = None
        if active_state is None:
            if expected_previous_graph_sha256 is not None:
                raise RepositoryECMAScriptDependencyError(
                    "expected predecessor ECMAScript dependency graph does not exist"
                )
        else:
            if expected_previous_graph_sha256 != active_state.graph_sha256:
                raise RepositoryECMAScriptDependencyError(
                    "expected predecessor does not match the active ECMAScript dependency graph"
                )
            previous = self._load_active_graph(active_state)
            self._verify_graph_compatibility(previous, project_id=project_id)
            if hmac.compare_digest(
                active_state.repository_snapshot_sha256,
                repository_state.snapshot_sha256,
            ):
                if active_state.repository_snapshot_ref != repository_state.snapshot_ref:
                    raise RepositoryECMAScriptDependencyError(
                        "active ECMAScript dependency graph snapshot reference does not match "
                        "the active repository state"
                    )
                return RepositoryECMAScriptDependencyGraphResult(
                    graph_ref=active_state.graph_ref,
                    graph_sha256=active_state.graph_sha256,
                    graph=previous,
                    replayed=True,
                )

        policy_sha256 = self._policy_sha256()
        graph = self._derive_graph(
            project_id=project_id,
            snapshot_ref=repository_state.snapshot_ref,
            snapshot=snapshot,
            snapshot_sha256=repository_state.snapshot_sha256,
            policy_sha256=policy_sha256,
            previous=previous,
            previous_ref=active_state.graph_ref if active_state else None,
            previous_sha256=active_state.graph_sha256 if active_state else None,
        )
        graph_ref, graph_sha256 = self._write_graph(graph)
        state = RepositoryDependencyGraphState(
            namespace=namespace,
            project_id=project_id,
            repository_url=snapshot.repository_url,
            base_ref=snapshot.base_ref,
            base_sha=snapshot.base_sha,
            repository_snapshot_ref=repository_state.snapshot_ref,
            repository_snapshot_sha256=repository_state.snapshot_sha256,
            graph_ref=graph_ref,
            graph_sha256=graph_sha256,
            policy_sha256=policy_sha256,
        )
        try:
            self.search.apply_repository_dependency_graph_state(
                state=state,
                expected_previous_graph_sha256=expected_previous_graph_sha256,
            )
        except RepositoryDependencyGraphStateError as exc:
            raise RepositoryECMAScriptDependencyError(str(exc)) from exc
        verified = self._load_graph(graph_ref, graph_sha256)
        return RepositoryECMAScriptDependencyGraphResult(
            graph_ref=graph_ref,
            graph_sha256=graph_sha256,
            graph=verified,
        )

    def verified_active_graph(
        self,
        *,
        project_id: str,
        expected_repository_snapshot_ref: str,
        expected_repository_snapshot_sha256: str,
        expected_graph_ref: str,
        expected_graph_sha256: str,
    ) -> tuple[
        RepositorySearchIndexState,
        RepositoryIndexSnapshot,
        RepositoryDependencyGraphState,
        ECMAScriptDependencyGraph,
    ]:
        """Load one exact active ECMAScript graph and its verified snapshot."""

        self._validate_project_id(project_id)
        try:
            repository_state, snapshot = self.repository_indexes.verified_active_snapshot(
                project_id,
                expected_snapshot_sha256=expected_repository_snapshot_sha256,
            )
        except RepositoryIndexError as exc:
            raise RepositoryECMAScriptDependencyError(str(exc)) from exc
        if repository_state.snapshot_ref != expected_repository_snapshot_ref:
            raise RepositoryECMAScriptDependencyError(
                "active repository snapshot reference does not match"
            )
        graph_state = self.search.repository_dependency_graph_state(self.namespace(project_id))
        if graph_state is None:
            raise RepositoryECMAScriptDependencyError(
                "active ECMAScript dependency graph does not exist"
            )
        if graph_state.graph_ref != expected_graph_ref or not hmac.compare_digest(
            graph_state.graph_sha256, expected_graph_sha256
        ):
            raise RepositoryECMAScriptDependencyError(
                "active ECMAScript dependency graph reference or hash does not match"
            )
        if (
            graph_state.repository_snapshot_ref != repository_state.snapshot_ref
            or not hmac.compare_digest(
                graph_state.repository_snapshot_sha256,
                repository_state.snapshot_sha256,
            )
        ):
            raise RepositoryECMAScriptDependencyError(
                "active ECMAScript dependency graph does not match the active repository snapshot"
            )
        graph = self._load_active_graph(graph_state)
        self._verify_graph_compatibility(graph, project_id=project_id)
        return repository_state, snapshot, graph_state, graph

    def analyze_current_delta(
        self,
        *,
        project_id: str,
        expected_repository_snapshot_sha256: str,
        expected_graph_sha256: str,
    ) -> RepositoryECMAScriptDependencyImpactResult:
        self._validate_project_id(project_id)
        try:
            repository_state, snapshot = self.repository_indexes.verified_active_snapshot(
                project_id,
                expected_snapshot_sha256=expected_repository_snapshot_sha256,
            )
        except RepositoryIndexError as exc:
            raise RepositoryECMAScriptDependencyError(str(exc)) from exc
        graph_state = self.search.repository_dependency_graph_state(self.namespace(project_id))
        if graph_state is None:
            raise RepositoryECMAScriptDependencyError(
                "active ECMAScript dependency graph does not exist"
            )
        if not hmac.compare_digest(graph_state.graph_sha256, expected_graph_sha256):
            raise RepositoryECMAScriptDependencyError(
                "active ECMAScript dependency graph hash does not match"
            )
        if (
            graph_state.repository_snapshot_ref != repository_state.snapshot_ref
            or not hmac.compare_digest(
                graph_state.repository_snapshot_sha256,
                repository_state.snapshot_sha256,
            )
        ):
            raise RepositoryECMAScriptDependencyError(
                "active ECMAScript dependency graph does not match the active repository snapshot"
            )
        graph = self._load_active_graph(graph_state)
        self._verify_graph_compatibility(graph, project_id=project_id)

        previous_graph_ref: str | None = None
        previous_graph_sha256: str | None = None
        previous_graph: ECMAScriptDependencyGraph | None = None
        if snapshot.previous_snapshot_ref and snapshot.previous_snapshot_sha256:
            try:
                previous_snapshot = self.repository_indexes.verified_snapshot(
                    snapshot.previous_snapshot_ref,
                    expected_sha256=snapshot.previous_snapshot_sha256,
                )
            except RepositoryIndexError as exc:
                raise RepositoryECMAScriptDependencyError(str(exc)) from exc
            self._verify_predecessor_snapshot(snapshot, previous_snapshot)
            previous_graph = self._matching_predecessor_graph(
                graph,
                expected_snapshot_ref=snapshot.previous_snapshot_ref,
                expected_snapshot_sha256=snapshot.previous_snapshot_sha256,
            )
            if previous_graph is None:
                previous_graph = self._derive_graph(
                    project_id=project_id,
                    snapshot_ref=snapshot.previous_snapshot_ref,
                    snapshot=previous_snapshot,
                    snapshot_sha256=snapshot.previous_snapshot_sha256,
                    policy_sha256=self._policy_sha256(),
                    previous=None,
                    previous_ref=None,
                    previous_sha256=None,
                )
                previous_graph_ref, previous_graph_sha256 = self._write_graph(previous_graph)
            else:
                previous_graph_ref = graph.previous_graph_ref
                previous_graph_sha256 = graph.previous_graph_sha256
            if (
                previous_graph.repository_snapshot_ref != snapshot.previous_snapshot_ref
                or previous_graph.repository_snapshot_sha256 != snapshot.previous_snapshot_sha256
                or previous_graph.repository_url != previous_snapshot.repository_url
                or previous_graph.base_ref != previous_snapshot.base_ref
                or previous_graph.base_sha != previous_snapshot.base_sha
            ):
                raise RepositoryECMAScriptDependencyError(
                    "predecessor ECMAScript graph does not match repository provenance"
                )

        changed_paths, current_seeds, previous_seeds = _changed_paths(snapshot)
        impacts = self._impacts(
            current=graph,
            previous=previous_graph,
            current_seeds=current_seeds,
            previous_seeds=previous_seeds,
        )
        current_paths = {node.path for node in graph.nodes}
        sources = tuple(
            sorted(
                (item for item in impacts if not item.is_test),
                key=lambda item: item.path,
            )
        )
        tests = tuple(
            sorted(
                (item for item in impacts if item.is_test and item.path in current_paths),
                key=lambda item: item.path,
            )
        )
        report = ECMAScriptDependencyImpactReport(
            project_id=project_id,
            repository_url=snapshot.repository_url,
            base_ref=snapshot.base_ref,
            base_sha=snapshot.base_sha,
            repository_snapshot_ref=repository_state.snapshot_ref,
            repository_snapshot_sha256=repository_state.snapshot_sha256,
            graph_ref=graph_state.graph_ref,
            graph_sha256=graph_state.graph_sha256,
            previous_graph_ref=previous_graph_ref,
            previous_graph_sha256=previous_graph_sha256,
            changed_paths=changed_paths,
            impacted_sources=sources,
            impacted_tests=tests,
        )
        content = report.canonical_content()
        if len(content.encode("utf-8")) > self.impact_max_bytes:
            raise RepositoryECMAScriptDependencyError(
                "ECMAScript dependency impact report exceeds its byte limit"
            )
        report_sha256 = report.canonical_hash()
        reference = self.artifacts.write_text(
            (
                f"ecmascript-dependency-impacts/{project_id}/{snapshot.base_sha}/"
                f"report-{report_sha256}.json"
            ),
            content,
            "application/json",
        )
        if not hmac.compare_digest(reference.sha256, report_sha256):
            raise RepositoryECMAScriptDependencyError(
                "ECMAScript dependency impact artifact hash mismatch"
            )
        verified = self._load_report(reference.uri, report_sha256)
        return RepositoryECMAScriptDependencyImpactResult(
            report_ref=reference.uri,
            report_sha256=report_sha256,
            report=verified,
        )

    @staticmethod
    def namespace(project_id: str) -> str:
        return f"explicit:ecmascript-dependency-graph:{project_id}"

    def _derive_graph(
        self,
        *,
        project_id: str,
        snapshot_ref: str,
        snapshot: RepositoryIndexSnapshot,
        snapshot_sha256: str,
        policy_sha256: str,
        previous: ECMAScriptDependencyGraph | None,
        previous_ref: str | None,
        previous_sha256: str | None,
    ) -> ECMAScriptDependencyGraph:
        nodes = tuple(
            sorted(
                (
                    ECMAScriptDependencyNode(
                        path=item.path,
                        language=item.project_file.language,
                        sha256=item.project_file.sha256,
                        is_test=item.project_file.is_test,
                        module_references=tuple(sorted(set(item.project_file.imports))),
                    )
                    for item in snapshot.files
                    if item.project_file.language in _ECMASCRIPT_LANGUAGES
                ),
                key=lambda node: node.path,
            )
        )
        if len(nodes) > self.max_nodes:
            raise RepositoryECMAScriptDependencyError(
                "ECMAScript dependency graph exceeds its node limit"
            )
        node_paths = frozenset(node.path for node in nodes)
        candidate_map_sha256 = hashlib.sha256(
            _canonical_json(sorted(node_paths)).encode("utf-8")
        ).hexdigest()

        previous_nodes = {node.path: node for node in previous.nodes} if previous else {}
        previous_edges: dict[str, list[ECMAScriptDependencyEdge]] = defaultdict(list)
        previous_unresolved: dict[str, list[ECMAScriptUnresolvedReference]] = defaultdict(list)
        if previous:
            for edge in previous.edges:
                previous_edges[edge.source_path].append(edge)
            for item in previous.unresolved_references:
                previous_unresolved[item.source_path].append(item)

        can_reuse_resolution = bool(
            previous and previous.candidate_map_sha256 == candidate_map_sha256
        )
        edges: list[ECMAScriptDependencyEdge] = []
        unresolved: list[ECMAScriptUnresolvedReference] = []
        reused: list[str] = []
        recomputed: list[str] = []
        for node in nodes:
            if can_reuse_resolution and previous_nodes.get(node.path) == node:
                reused.append(node.path)
                edges.extend(previous_edges.get(node.path, ()))
                unresolved.extend(previous_unresolved.get(node.path, ()))
                continue
            recomputed.append(node.path)
            for raw_reference in node.module_references:
                edge, unresolved_reference = _resolve_reference(
                    node,
                    raw_reference,
                    node_paths,
                )
                if edge is not None:
                    edges.append(edge)
                elif unresolved_reference is not None:
                    unresolved.append(unresolved_reference)

        edges_tuple = tuple(sorted(set(edges), key=_edge_key))
        unresolved_tuple = tuple(sorted(set(unresolved), key=_unresolved_key))
        if len(edges_tuple) > self.max_edges:
            raise RepositoryECMAScriptDependencyError(
                "ECMAScript dependency graph exceeds its edge limit"
            )
        if len(unresolved_tuple) > self.max_unresolved:
            raise RepositoryECMAScriptDependencyError(
                "ECMAScript dependency graph exceeds its unresolved-reference limit"
            )
        graph = ECMAScriptDependencyGraph(
            project_id=project_id,
            repository_url=snapshot.repository_url,
            base_ref=snapshot.base_ref,
            base_sha=snapshot.base_sha,
            namespace=self.namespace(project_id),
            repository_snapshot_ref=snapshot_ref,
            repository_snapshot_sha256=snapshot_sha256,
            policy_sha256=policy_sha256,
            candidate_map_sha256=candidate_map_sha256,
            previous_graph_ref=previous_ref,
            previous_graph_sha256=previous_sha256,
            nodes=nodes,
            edges=edges_tuple,
            unresolved_references=unresolved_tuple,
            delta=ECMAScriptDependencyGraphDelta(
                reused_paths=tuple(reused),
                recomputed_paths=tuple(recomputed),
                deleted_paths=tuple(sorted(set(previous_nodes) - {node.path for node in nodes})),
            ),
        )
        if len(graph.canonical_content().encode("utf-8")) > self.graph_max_bytes:
            raise RepositoryECMAScriptDependencyError(
                "ECMAScript dependency graph exceeds its byte limit"
            )
        return graph

    def _impacts(
        self,
        *,
        current: ECMAScriptDependencyGraph,
        previous: ECMAScriptDependencyGraph | None,
        current_seeds: tuple[str, ...],
        previous_seeds: tuple[str, ...],
    ) -> tuple[ECMAScriptDependencyImpactItem, ...]:
        current_nodes = {node.path: node for node in current.nodes}
        previous_nodes = {node.path: node for node in previous.nodes} if previous else {}
        selected: dict[str, ECMAScriptDependencyImpactItem] = {}
        traversed: set[tuple[str, str, str]] = set()
        for label, graph, nodes, seeds in (
            ("current", current, current_nodes, current_seeds),
            ("previous", previous, previous_nodes, previous_seeds),
        ):
            if graph is None:
                if seeds:
                    raise RepositoryECMAScriptDependencyError(
                        "ECMAScript impact requires the verified predecessor graph"
                    )
                continue
            reverse: dict[str, list[ECMAScriptDependencyEdge]] = defaultdict(list)
            for edge in graph.edges:
                reverse[edge.target_path].append(edge)
            for target_path in reverse:
                reverse[target_path].sort(key=_edge_key)
            for seed in seeds:
                if seed not in nodes:
                    continue
                queue = deque([(seed, (seed,), (), ())])
                visited = {seed}
                while queue:
                    path, chain, reference_chain, resolution_chain = queue.popleft()
                    traversed.add((label, seed, path))
                    if len(traversed) > self.max_impact_nodes:
                        raise RepositoryECMAScriptDependencyError(
                            "ECMAScript dependency impact exceeds its traversal limit"
                        )
                    historical_node = nodes[path]
                    current_node = current_nodes.get(path)
                    is_test = (
                        current_node.is_test
                        if current_node is not None
                        else historical_node.is_test
                    )
                    depth = len(chain) - 1
                    confidence = _impact_confidence(depth, resolution_chain)
                    item = ECMAScriptDependencyImpactItem(
                        path=path,
                        changed_path=seed,
                        is_test=is_test,
                        present_in_current_snapshot=current_node is not None,
                        depth=depth,
                        confidence=confidence,
                        dependency_chain=chain,
                        reference_chain=reference_chain,
                        resolution_chain=resolution_chain,
                    )
                    prior = selected.get(path)
                    if prior is None or _impact_key(item) < _impact_key(prior):
                        selected[path] = item
                    dependent_edges = reverse.get(path, ())
                    if depth == self.max_impact_depth:
                        if any(edge.source_path not in visited for edge in dependent_edges):
                            raise RepositoryECMAScriptDependencyError(
                                "ECMAScript dependency impact exceeds its depth limit"
                            )
                        continue
                    for edge in dependent_edges:
                        dependent = edge.source_path
                        if dependent in visited:
                            continue
                        visited.add(dependent)
                        queue.append(
                            (
                                dependent,
                                (*chain, dependent),
                                (*reference_chain, _raw_reference(edge)),
                                (*resolution_chain, edge.resolution_basis),
                            )
                        )
        if len(selected) > self.max_impact_nodes:
            raise RepositoryECMAScriptDependencyError(
                "ECMAScript dependency impact exceeds its result limit"
            )
        return tuple(selected[path] for path in sorted(selected))

    def _matching_predecessor_graph(
        self,
        graph: ECMAScriptDependencyGraph,
        *,
        expected_snapshot_ref: str,
        expected_snapshot_sha256: str,
    ) -> ECMAScriptDependencyGraph | None:
        if not graph.previous_graph_ref or not graph.previous_graph_sha256:
            return None
        previous = self._load_graph(
            graph.previous_graph_ref,
            graph.previous_graph_sha256,
        )
        self._verify_graph_compatibility(previous, project_id=graph.project_id)
        if (
            previous.repository_snapshot_ref != expected_snapshot_ref
            or previous.repository_snapshot_sha256 != expected_snapshot_sha256
        ):
            return None
        return previous

    @staticmethod
    def _verify_predecessor_snapshot(
        current: RepositoryIndexSnapshot,
        previous: RepositoryIndexSnapshot,
    ) -> None:
        if previous.project_id != current.project_id:
            raise RepositoryECMAScriptDependencyError(
                "repository predecessor project scope does not match"
            )
        if (
            previous.repository_url != current.repository_url
            or previous.base_ref != current.base_ref
        ):
            raise RepositoryECMAScriptDependencyError(
                "repository predecessor source identity does not match"
            )
        if not hmac.compare_digest(previous.policy_sha256, current.policy_sha256):
            raise RepositoryECMAScriptDependencyError(
                "repository predecessor policy does not match"
            )

    def _write_graph(self, graph: ECMAScriptDependencyGraph) -> tuple[str, str]:
        content = graph.canonical_content()
        if len(content.encode("utf-8")) > self.graph_max_bytes:
            raise RepositoryECMAScriptDependencyError(
                "ECMAScript dependency graph exceeds its byte limit"
            )
        graph_sha256 = graph.canonical_hash()
        reference = self.artifacts.write_text(
            (
                f"ecmascript-dependency-graphs/{graph.project_id}/{graph.base_sha}/"
                f"graph-{graph_sha256}.json"
            ),
            content,
            "application/json",
        )
        if not hmac.compare_digest(reference.sha256, graph_sha256):
            raise RepositoryECMAScriptDependencyError(
                "ECMAScript dependency graph artifact hash mismatch"
            )
        return reference.uri, graph_sha256

    def _load_active_graph(
        self,
        state: RepositoryDependencyGraphState,
    ) -> ECMAScriptDependencyGraph:
        graph = self._load_graph(state.graph_ref, state.graph_sha256)
        if (
            graph.namespace != state.namespace
            or graph.project_id != state.project_id
            or graph.repository_url != state.repository_url
            or graph.base_ref != state.base_ref
            or graph.base_sha != state.base_sha
            or graph.repository_snapshot_ref != state.repository_snapshot_ref
            or graph.repository_snapshot_sha256 != state.repository_snapshot_sha256
            or graph.policy_sha256 != state.policy_sha256
        ):
            raise RepositoryECMAScriptDependencyError(
                "active ECMAScript graph state does not match artifact provenance"
            )
        return graph

    def _load_graph(
        self,
        reference: str,
        expected_sha256: str,
    ) -> ECMAScriptDependencyGraph:
        try:
            content = self.artifacts.read_text_bounded_verified(
                reference,
                expected_sha256=expected_sha256,
                max_bytes=self.graph_max_bytes,
            )
            graph = ECMAScriptDependencyGraph.model_validate_json(content)
        except (OSError, UnicodeError, ValueError) as exc:
            raise RepositoryECMAScriptDependencyError(
                "ECMAScript dependency graph failed bounded integrity verification"
            ) from exc
        if not hmac.compare_digest(graph.canonical_hash(), expected_sha256):
            raise RepositoryECMAScriptDependencyError(
                "ECMAScript dependency graph canonical hash mismatch"
            )
        return graph

    def _load_report(
        self,
        reference: str,
        expected_sha256: str,
    ) -> ECMAScriptDependencyImpactReport:
        try:
            content = self.artifacts.read_text_bounded_verified(
                reference,
                expected_sha256=expected_sha256,
                max_bytes=self.impact_max_bytes,
            )
            report = ECMAScriptDependencyImpactReport.model_validate_json(content)
        except (OSError, UnicodeError, ValueError) as exc:
            raise RepositoryECMAScriptDependencyError(
                "ECMAScript impact report failed bounded integrity verification"
            ) from exc
        if not hmac.compare_digest(report.canonical_hash(), expected_sha256):
            raise RepositoryECMAScriptDependencyError(
                "ECMAScript impact report canonical hash mismatch"
            )
        return report

    def _verify_graph_compatibility(
        self,
        graph: ECMAScriptDependencyGraph,
        *,
        project_id: str,
    ) -> None:
        if graph.project_id != project_id or graph.namespace != self.namespace(project_id):
            raise RepositoryECMAScriptDependencyError(
                "ECMAScript dependency graph project scope does not match"
            )
        if not hmac.compare_digest(graph.policy_sha256, self._policy_sha256()):
            raise RepositoryECMAScriptDependencyError(
                "ECMAScript dependency graph policy does not match"
            )

    def _policy_sha256(self) -> str:
        return hashlib.sha256(
            _canonical_json(
                {
                    "schema_version": "1",
                    "ecmascript_dependency_graph_policy_version": (
                        ECMASCRIPT_DEPENDENCY_GRAPH_POLICY_VERSION
                    ),
                    "repository_index_policy_version": INDEX_POLICY_VERSION,
                    "resolver": "ecmascript-conservative-relative-v1",
                    "reference_kinds": sorted(_REFERENCE_KINDS),
                    "extensionless_file_suffixes": list(_EXTENSIONLESS_FILE_SUFFIXES),
                    "typescript_extension_substitutions": {
                        key: list(value)
                        for key, value in sorted(_TYPESCRIPT_EXTENSION_SUBSTITUTIONS.items())
                    },
                    "graph_max_bytes": self.graph_max_bytes,
                    "impact_max_bytes": self.impact_max_bytes,
                    "max_nodes": self.max_nodes,
                    "max_edges": self.max_edges,
                    "max_unresolved": self.max_unresolved,
                    "max_impact_nodes": self.max_impact_nodes,
                    "max_impact_depth": self.max_impact_depth,
                }
            ).encode("utf-8")
        ).hexdigest()

    @staticmethod
    def _validate_project_id(project_id: str) -> None:
        if not _PROJECT_ID.fullmatch(project_id):
            raise RepositoryECMAScriptDependencyError("project ID is invalid")


def _resolve_reference(
    node: ECMAScriptDependencyNode,
    raw_reference: str,
    node_paths: frozenset[str],
) -> tuple[ECMAScriptDependencyEdge | None, ECMAScriptUnresolvedReference | None]:
    if len(raw_reference) > 8192:
        raise RepositoryECMAScriptDependencyError(
            "ECMAScript module reference exceeds its graph limit"
        )
    kind_text, separator, module_specifier = raw_reference.partition(":")
    if (
        not separator
        or kind_text not in _REFERENCE_KINDS
        or not module_specifier
        or len(module_specifier) > 4096
    ):
        return None, _unresolved_reference(
            node,
            raw_reference,
            module_specifier if len(module_specifier) <= 4096 else "",
            ECMAScriptUnresolvedReason.INVALID_REFERENCE,
        )
    reference_kind = ECMAScriptReferenceKind(kind_text)
    if any(ord(character) < 32 or ord(character) == 127 for character in module_specifier):
        return None, _unresolved_reference(
            node,
            raw_reference,
            module_specifier,
            ECMAScriptUnresolvedReason.INVALID_REFERENCE,
        )
    if module_specifier.startswith("/") or _URL_SCHEME.match(module_specifier):
        return None, _unresolved_reference(
            node,
            raw_reference,
            module_specifier,
            ECMAScriptUnresolvedReason.ABSOLUTE_OR_URL,
        )
    if not module_specifier.startswith(("./", "../")):
        return None, _unresolved_reference(
            node,
            raw_reference,
            module_specifier,
            ECMAScriptUnresolvedReason.BARE_OR_EXTERNAL,
        )
    if (
        "\\" in module_specifier
        or "?" in module_specifier
        or "#" in module_specifier
        or "%" in module_specifier
    ):
        return None, _unresolved_reference(
            node,
            raw_reference,
            module_specifier,
            ECMAScriptUnresolvedReason.INVALID_REFERENCE,
        )

    target, reason = _normalize_relative_target(node.path, module_specifier)
    if target is None:
        return None, _unresolved_reference(
            node,
            raw_reference,
            module_specifier,
            reason or ECMAScriptUnresolvedReason.INVALID_REFERENCE,
        )
    suffix = _recognized_suffix(target)
    if suffix is None and PurePosixPath(target).suffix:
        return None, _unresolved_reference(
            node,
            raw_reference,
            module_specifier,
            ECMAScriptUnresolvedReason.UNSUPPORTED_TARGET_TYPE,
        )

    candidates = _resolution_candidates(node, target, suffix=suffix)
    matched = tuple(sorted(path for path in candidates if path in node_paths))
    if not matched:
        return None, _unresolved_reference(
            node,
            raw_reference,
            module_specifier,
            ECMAScriptUnresolvedReason.MISSING_TARGET,
        )
    if len(matched) > 1:
        return None, _unresolved_reference(
            node,
            raw_reference,
            module_specifier,
            ECMAScriptUnresolvedReason.AMBIGUOUS_TARGET,
            candidate_paths=matched,
        )
    target_path = matched[0]
    return (
        ECMAScriptDependencyEdge(
            source_path=node.path,
            target_path=target_path,
            reference_kind=reference_kind,
            module_specifier=module_specifier,
            resolution_basis=candidates[target_path],
        ),
        None,
    )


def _unresolved_reference(
    node: ECMAScriptDependencyNode,
    raw_reference: str,
    module_specifier: str,
    reason: ECMAScriptUnresolvedReason,
    *,
    candidate_paths: tuple[str, ...] = (),
) -> ECMAScriptUnresolvedReference:
    return ECMAScriptUnresolvedReference(
        source_path=node.path,
        raw_reference=raw_reference,
        module_specifier=module_specifier,
        reason=reason,
        candidate_paths=candidate_paths,
    )


def _normalize_relative_target(
    source_path: str,
    module_specifier: str,
) -> tuple[str | None, ECMAScriptUnresolvedReason | None]:
    source_directory = PurePosixPath(source_path).parent
    parts = [] if source_directory == PurePosixPath(".") else list(source_directory.parts)
    specifier_parts = module_specifier.split("/")
    if any(part == "" for part in specifier_parts):
        return None, ECMAScriptUnresolvedReason.INVALID_REFERENCE
    for part in specifier_parts:
        if part == ".":
            continue
        if part == "..":
            if not parts:
                return None, ECMAScriptUnresolvedReason.RELATIVE_OUTSIDE_REPOSITORY
            parts.pop()
            continue
        parts.append(part)
    if not parts:
        return None, ECMAScriptUnresolvedReason.INVALID_REFERENCE
    try:
        return normalize_repository_path("/".join(parts)), None
    except ValueError:
        return None, ECMAScriptUnresolvedReason.INVALID_REFERENCE


def _recognized_suffix(path: str) -> str | None:
    lower = path.lower()
    return next(
        (suffix for suffix in _RECOGNIZED_EXPLICIT_SUFFIXES if lower.endswith(suffix)),
        None,
    )


def _resolution_candidates(
    node: ECMAScriptDependencyNode,
    target: str,
    *,
    suffix: str | None,
) -> dict[str, ECMAScriptResolutionBasis]:
    candidates: dict[str, ECMAScriptResolutionBasis] = {}
    if suffix is not None:
        _add_candidate(
            candidates,
            target,
            ECMAScriptResolutionBasis.EXACT_RELATIVE,
        )
        substitutions = (
            _TYPESCRIPT_EXTENSION_SUBSTITUTIONS.get(suffix, ())
            if node.language == "typescript"
            else ()
        )
        if substitutions:
            stem = target[: -len(suffix)]
            for replacement in substitutions:
                candidate = f"{stem}{replacement}"
                basis = (
                    ECMAScriptResolutionBasis.EXACT_RELATIVE
                    if candidate == target
                    else ECMAScriptResolutionBasis.TYPESCRIPT_EXTENSION_SUBSTITUTION
                )
                _add_candidate(candidates, candidate, basis)
        return candidates

    for replacement in _EXTENSIONLESS_FILE_SUFFIXES:
        _add_candidate(
            candidates,
            f"{target}{replacement}",
            ECMAScriptResolutionBasis.UNIQUE_EXTENSION_CANDIDATE,
        )
        _add_candidate(
            candidates,
            f"{target}/index{replacement}",
            ECMAScriptResolutionBasis.UNIQUE_DIRECTORY_INDEX_CANDIDATE,
        )
    return candidates


def _add_candidate(
    candidates: dict[str, ECMAScriptResolutionBasis],
    path: str,
    basis: ECMAScriptResolutionBasis,
) -> None:
    normalized = normalize_repository_path(path)
    current = candidates.get(normalized)
    if current is None or _resolution_basis_rank(basis) < _resolution_basis_rank(current):
        candidates[normalized] = basis


def _resolution_basis_rank(basis: ECMAScriptResolutionBasis) -> int:
    return {
        ECMAScriptResolutionBasis.EXACT_RELATIVE: 0,
        ECMAScriptResolutionBasis.TYPESCRIPT_EXTENSION_SUBSTITUTION: 1,
        ECMAScriptResolutionBasis.UNIQUE_EXTENSION_CANDIDATE: 2,
        ECMAScriptResolutionBasis.UNIQUE_DIRECTORY_INDEX_CANDIDATE: 3,
    }[basis]


def _impact_confidence(
    depth: int,
    resolution_chain: tuple[ECMAScriptResolutionBasis, ...],
) -> ECMAScriptImpactConfidence:
    high_confidence_bases = {
        ECMAScriptResolutionBasis.EXACT_RELATIVE,
        ECMAScriptResolutionBasis.TYPESCRIPT_EXTENSION_SUBSTITUTION,
    }
    if depth <= 1 and all(basis in high_confidence_bases for basis in resolution_chain):
        return ECMAScriptImpactConfidence.HIGH
    return ECMAScriptImpactConfidence.MEDIUM


def _changed_paths(
    snapshot: RepositoryIndexSnapshot,
) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    current = (
        set(snapshot.delta.added_paths)
        | set(snapshot.delta.modified_paths)
        | {item.new_path for item in snapshot.delta.renamed_paths}
    )
    previous = set(snapshot.delta.deleted_paths) | {
        item.old_path for item in snapshot.delta.renamed_paths
    }
    return tuple(sorted(current | previous)), tuple(sorted(current)), tuple(sorted(previous))


def _raw_reference(edge: ECMAScriptDependencyEdge) -> str:
    return f"{edge.reference_kind.value}:{edge.module_specifier}"


def _edge_key(edge: ECMAScriptDependencyEdge) -> tuple[str, str, str, str, str]:
    return (
        edge.source_path,
        edge.target_path,
        edge.reference_kind.value,
        edge.module_specifier,
        edge.resolution_basis.value,
    )


def _unresolved_key(
    item: ECMAScriptUnresolvedReference,
) -> tuple[str, str, str, str, tuple[str, ...]]:
    return (
        item.source_path,
        item.raw_reference,
        item.module_specifier,
        item.reason.value,
        item.candidate_paths,
    )


def _impact_key(
    item: ECMAScriptDependencyImpactItem,
) -> tuple[int, str, tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    return (
        item.depth,
        item.changed_path,
        item.dependency_chain,
        item.reference_chain,
        tuple(basis.value for basis in item.resolution_chain),
    )


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
