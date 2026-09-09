from __future__ import annotations

import hashlib
import hmac
import json
import re
from collections import defaultdict, deque
from enum import StrEnum
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

DEFAULT_DEPENDENCY_GRAPH_MAX_BYTES = 8_000_000
DEFAULT_DEPENDENCY_IMPACT_MAX_BYTES = 2_000_000
DEFAULT_DEPENDENCY_GRAPH_MAX_NODES = 20_000
DEFAULT_DEPENDENCY_GRAPH_MAX_EDGES = 100_000
DEFAULT_DEPENDENCY_GRAPH_MAX_UNRESOLVED = 100_000
DEFAULT_DEPENDENCY_IMPACT_MAX_NODES = 10_000
DEFAULT_DEPENDENCY_IMPACT_MAX_DEPTH = 12
DEPENDENCY_GRAPH_POLICY_VERSION = "1"
_PROJECT_ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")


class RepositoryDependencyError(ValueError):
    """Repository dependency evidence cannot satisfy its bounded provenance contract."""


class UnresolvedImportReason(StrEnum):
    MISSING_OR_EXTERNAL = "missing_or_external"
    AMBIGUOUS_MODULE = "ambiguous_module"
    RELATIVE_OUTSIDE_PACKAGE = "relative_outside_package"
    INVALID_IMPORT = "invalid_import"


class PythonDependencyNode(FrozenModel):
    path: str = Field(min_length=1, max_length=4096)
    module: str = Field(min_length=1, max_length=4096)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    is_test: bool = False
    imports: tuple[str, ...] = ()

    @field_validator("path")
    @classmethod
    def validate_path(cls, value: str) -> str:
        return normalize_repository_path(value)

    @field_validator("imports")
    @classmethod
    def validate_imports(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        if values != tuple(sorted(set(values))):
            raise ValueError("dependency node imports must be unique and sorted")
        if any(not value or len(value) > 4096 for value in values):
            raise ValueError("dependency node import is empty or oversized")
        return values


class PythonDependencyEdge(FrozenModel):
    source_path: str = Field(min_length=1, max_length=4096)
    target_path: str = Field(min_length=1, max_length=4096)
    raw_import: str = Field(min_length=1, max_length=4096)

    @field_validator("source_path", "target_path")
    @classmethod
    def validate_path(cls, value: str) -> str:
        return normalize_repository_path(value)


class PythonUnresolvedImport(FrozenModel):
    source_path: str = Field(min_length=1, max_length=4096)
    raw_import: str = Field(min_length=1, max_length=4096)
    reason: UnresolvedImportReason
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
            raise ValueError("unresolved import candidates must be unique and sorted")
        return normalized


class PythonDependencyGraphDelta(FrozenModel):
    reused_paths: tuple[str, ...] = ()
    recomputed_paths: tuple[str, ...] = ()
    deleted_paths: tuple[str, ...] = ()

    @field_validator("reused_paths", "recomputed_paths", "deleted_paths")
    @classmethod
    def validate_paths(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(normalize_repository_path(value) for value in values)
        if normalized != tuple(sorted(set(normalized))):
            raise ValueError("dependency graph delta paths must be unique and sorted")
        return normalized


class PythonDependencyGraph(FrozenModel):
    schema_version: Literal["1"] = "1"
    project_id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")
    repository_url: str = Field(min_length=1, max_length=2048)
    base_ref: str = Field(min_length=1, max_length=256)
    base_sha: str = Field(pattern=r"^[0-9a-f]{40,64}$")
    namespace: str = Field(
        pattern=r"^explicit:repository-dependency-graph:[a-zA-Z0-9._-]+$"
    )
    repository_snapshot_ref: str = Field(pattern=r"^artifact://[a-zA-Z0-9._/-]+$")
    repository_snapshot_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    policy_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    module_map_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    previous_graph_ref: str | None = Field(
        default=None, pattern=r"^artifact://[a-zA-Z0-9._/-]+$"
    )
    previous_graph_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    nodes: tuple[PythonDependencyNode, ...] = ()
    edges: tuple[PythonDependencyEdge, ...] = ()
    unresolved_imports: tuple[PythonUnresolvedImport, ...] = ()
    delta: PythonDependencyGraphDelta

    @model_validator(mode="after")
    def validate_graph(self) -> PythonDependencyGraph:
        if self.namespace != f"explicit:repository-dependency-graph:{self.project_id}":
            raise ValueError("dependency graph namespace does not match project identity")
        if (self.previous_graph_ref is None) != (self.previous_graph_sha256 is None):
            raise ValueError("dependency graph predecessor reference and hash must be paired")
        node_paths = tuple(node.path for node in self.nodes)
        if node_paths != tuple(sorted(set(node_paths))):
            raise ValueError("dependency graph nodes must be unique and sorted")
        edge_keys = tuple(_edge_key(edge) for edge in self.edges)
        if edge_keys != tuple(sorted(set(edge_keys))):
            raise ValueError("dependency graph edges must be unique and sorted")
        unresolved_keys = tuple(_unresolved_key(item) for item in self.unresolved_imports)
        if unresolved_keys != tuple(sorted(set(unresolved_keys))):
            raise ValueError("unresolved imports must be unique and sorted")
        known = set(node_paths)
        if any(
            edge.source_path not in known or edge.target_path not in known
            for edge in self.edges
        ):
            raise ValueError("dependency graph edge references an unknown node")
        if any(item.source_path not in known for item in self.unresolved_imports):
            raise ValueError("unresolved import references an unknown node")
        reused = set(self.delta.reused_paths)
        recomputed = set(self.delta.recomputed_paths)
        deleted = set(self.delta.deleted_paths)
        if reused & recomputed:
            raise ValueError("dependency graph reused and recomputed paths overlap")
        if reused | recomputed != known:
            raise ValueError("dependency graph delta does not cover every current node")
        if deleted & known:
            raise ValueError("dependency graph deleted paths remain in the current graph")
        return self

    def canonical_content(self) -> str:
        return _canonical_json(self.model_dump(mode="json"))

    def canonical_hash(self) -> str:
        return hashlib.sha256(self.canonical_content().encode("utf-8")).hexdigest()


class DependencyImpactConfidence(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"


class DependencyImpactItem(FrozenModel):
    path: str = Field(min_length=1, max_length=4096)
    changed_path: str = Field(min_length=1, max_length=4096)
    is_test: bool
    present_in_current_snapshot: bool
    depth: int = Field(ge=0)
    confidence: DependencyImpactConfidence
    dependency_chain: tuple[str, ...] = Field(min_length=1)

    @field_validator("path", "changed_path")
    @classmethod
    def validate_path(cls, value: str) -> str:
        return normalize_repository_path(value)

    @field_validator("dependency_chain")
    @classmethod
    def validate_chain(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(normalize_repository_path(value) for value in values)

    @model_validator(mode="after")
    def validate_endpoints(self) -> DependencyImpactItem:
        if self.dependency_chain[0] != self.changed_path:
            raise ValueError("impact chain must begin with the changed path")
        if self.dependency_chain[-1] != self.path:
            raise ValueError("impact chain must end with the impacted path")
        if self.depth != len(self.dependency_chain) - 1:
            raise ValueError("impact depth does not match its dependency chain")
        return self


class DependencyImpactReport(FrozenModel):
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
        default=None, pattern=r"^artifact://[a-zA-Z0-9._/-]+$"
    )
    previous_graph_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    changed_paths: tuple[str, ...]
    impacted_sources: tuple[DependencyImpactItem, ...] = ()
    impacted_tests: tuple[DependencyImpactItem, ...] = ()

    @field_validator("changed_paths")
    @classmethod
    def validate_changed_paths(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(normalize_repository_path(value) for value in values)

    @model_validator(mode="after")
    def validate_report(self) -> DependencyImpactReport:
        if (self.previous_graph_ref is None) != (self.previous_graph_sha256 is None):
            raise ValueError("impact predecessor graph reference and hash must be paired")
        if self.changed_paths != tuple(sorted(set(self.changed_paths))):
            raise ValueError("impact changed paths must be unique and sorted")
        source_paths = tuple(item.path for item in self.impacted_sources)
        test_paths = tuple(item.path for item in self.impacted_tests)
        if source_paths != tuple(sorted(set(source_paths))):
            raise ValueError("impacted sources must be unique and sorted")
        if test_paths != tuple(sorted(set(test_paths))):
            raise ValueError("impacted tests must be unique and sorted")
        if any(item.is_test for item in self.impacted_sources):
            raise ValueError("impacted source result contains a test")
        if any(
            not item.is_test or not item.present_in_current_snapshot
            for item in self.impacted_tests
        ):
            raise ValueError("impacted test result must be a current tracked test")
        return self

    def canonical_content(self) -> str:
        return _canonical_json(self.model_dump(mode="json"))

    def canonical_hash(self) -> str:
        return hashlib.sha256(self.canonical_content().encode("utf-8")).hexdigest()


class RepositoryDependencyGraphResult(FrozenModel):
    graph_ref: str = Field(pattern=r"^artifact://[a-zA-Z0-9._/-]+$")
    graph_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    graph: PythonDependencyGraph
    replayed: bool = False


class RepositoryDependencyImpactResult(FrozenModel):
    report_ref: str = Field(pattern=r"^artifact://[a-zA-Z0-9._/-]+$")
    report_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    report: DependencyImpactReport


class RepositoryDependencyService:
    """Build bounded Python dependency evidence from verified repository snapshots."""

    def __init__(
        self,
        artifacts: ArtifactStore,
        search: SearchService,
        repository_indexes: RepositoryIndexService,
        *,
        graph_max_bytes: int = DEFAULT_DEPENDENCY_GRAPH_MAX_BYTES,
        impact_max_bytes: int = DEFAULT_DEPENDENCY_IMPACT_MAX_BYTES,
        max_nodes: int = DEFAULT_DEPENDENCY_GRAPH_MAX_NODES,
        max_edges: int = DEFAULT_DEPENDENCY_GRAPH_MAX_EDGES,
        max_unresolved: int = DEFAULT_DEPENDENCY_GRAPH_MAX_UNRESOLVED,
        max_impact_nodes: int = DEFAULT_DEPENDENCY_IMPACT_MAX_NODES,
        max_impact_depth: int = DEFAULT_DEPENDENCY_IMPACT_MAX_DEPTH,
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
            raise ValueError("repository dependency limits must be positive")
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
    ) -> RepositoryDependencyGraphResult:
        self._validate_project_id(project_id)
        try:
            repository_state, snapshot = self.repository_indexes.verified_active_snapshot(
                project_id,
                expected_snapshot_sha256=expected_repository_snapshot_sha256,
            )
        except RepositoryIndexError as exc:
            raise RepositoryDependencyError(str(exc)) from exc
        namespace = self.namespace(project_id)
        active_state = self.search.repository_dependency_graph_state(namespace)
        previous: PythonDependencyGraph | None = None
        if active_state is None:
            if expected_previous_graph_sha256 is not None:
                raise RepositoryDependencyError(
                    "expected predecessor dependency graph does not exist"
                )
        else:
            if expected_previous_graph_sha256 != active_state.graph_sha256:
                raise RepositoryDependencyError(
                    "expected predecessor does not match the active dependency graph"
                )
            previous = self._load_active_graph(active_state)
            self._verify_graph_compatibility(previous, project_id=project_id)
            if hmac.compare_digest(
                active_state.repository_snapshot_sha256,
                repository_state.snapshot_sha256,
            ):
                if active_state.repository_snapshot_ref != repository_state.snapshot_ref:
                    raise RepositoryDependencyError(
                        "active dependency graph snapshot reference does not match "
                        "the active repository state"
                    )
                return RepositoryDependencyGraphResult(
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
            raise RepositoryDependencyError(str(exc)) from exc
        verified = self._load_graph(graph_ref, graph_sha256)
        return RepositoryDependencyGraphResult(
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
        PythonDependencyGraph,
    ]:
        """Load one exact active dependency graph and all of its verified provenance."""

        self._validate_project_id(project_id)
        try:
            repository_state, snapshot = self.repository_indexes.verified_active_snapshot(
                project_id,
                expected_snapshot_sha256=expected_repository_snapshot_sha256,
            )
        except RepositoryIndexError as exc:
            raise RepositoryDependencyError(str(exc)) from exc
        if repository_state.snapshot_ref != expected_repository_snapshot_ref:
            raise RepositoryDependencyError(
                "active repository snapshot reference does not match"
            )
        graph_state = self.search.repository_dependency_graph_state(
            self.namespace(project_id)
        )
        if graph_state is None:
            raise RepositoryDependencyError("active dependency graph does not exist")
        if (
            graph_state.graph_ref != expected_graph_ref
            or not hmac.compare_digest(
                graph_state.graph_sha256,
                expected_graph_sha256,
            )
        ):
            raise RepositoryDependencyError(
                "active dependency graph reference or hash does not match"
            )
        if (
            graph_state.repository_snapshot_ref != repository_state.snapshot_ref
            or not hmac.compare_digest(
                graph_state.repository_snapshot_sha256,
                repository_state.snapshot_sha256,
            )
        ):
            raise RepositoryDependencyError(
                "active dependency graph does not match the active repository snapshot"
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
    ) -> RepositoryDependencyImpactResult:
        self._validate_project_id(project_id)
        try:
            repository_state, snapshot = self.repository_indexes.verified_active_snapshot(
                project_id,
                expected_snapshot_sha256=expected_repository_snapshot_sha256,
            )
        except RepositoryIndexError as exc:
            raise RepositoryDependencyError(str(exc)) from exc
        graph_state = self.search.repository_dependency_graph_state(self.namespace(project_id))
        if graph_state is None:
            raise RepositoryDependencyError("active dependency graph does not exist")
        if not hmac.compare_digest(graph_state.graph_sha256, expected_graph_sha256):
            raise RepositoryDependencyError("active dependency graph hash does not match")
        if (
            graph_state.repository_snapshot_ref != repository_state.snapshot_ref
            or not hmac.compare_digest(
                graph_state.repository_snapshot_sha256,
                repository_state.snapshot_sha256,
            )
        ):
            raise RepositoryDependencyError(
                "active dependency graph does not match the active repository snapshot"
            )
        graph = self._load_active_graph(graph_state)
        self._verify_graph_compatibility(graph, project_id=project_id)

        previous_graph_ref: str | None = None
        previous_graph_sha256: str | None = None
        previous_graph: PythonDependencyGraph | None = None
        if snapshot.previous_snapshot_ref and snapshot.previous_snapshot_sha256:
            try:
                previous_snapshot = self.repository_indexes.verified_snapshot(
                    snapshot.previous_snapshot_ref,
                    expected_sha256=snapshot.previous_snapshot_sha256,
                )
            except RepositoryIndexError as exc:
                raise RepositoryDependencyError(str(exc)) from exc
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
                or previous_graph.repository_snapshot_sha256
                != snapshot.previous_snapshot_sha256
                or previous_graph.repository_url != previous_snapshot.repository_url
                or previous_graph.base_ref != previous_snapshot.base_ref
                or previous_graph.base_sha != previous_snapshot.base_sha
            ):
                raise RepositoryDependencyError(
                    "predecessor dependency graph does not match repository provenance"
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
            sorted((item for item in impacts if not item.is_test), key=lambda item: item.path)
        )
        tests = tuple(
            sorted(
                (
                    item
                    for item in impacts
                    if item.is_test and item.path in current_paths
                ),
                key=lambda item: item.path,
            )
        )
        report = DependencyImpactReport(
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
            raise RepositoryDependencyError("dependency impact report exceeds its byte limit")
        report_sha256 = report.canonical_hash()
        reference = self.artifacts.write_text(
            (
                f"dependency-impacts/{project_id}/{snapshot.base_sha}/"
                f"report-{report_sha256}.json"
            ),
            content,
            "application/json",
        )
        if not hmac.compare_digest(reference.sha256, report_sha256):
            raise RepositoryDependencyError("dependency impact artifact hash mismatch")
        verified = self._load_report(reference.uri, report_sha256)
        return RepositoryDependencyImpactResult(
            report_ref=reference.uri,
            report_sha256=report_sha256,
            report=verified,
        )

    @staticmethod
    def namespace(project_id: str) -> str:
        return f"explicit:repository-dependency-graph:{project_id}"

    def _derive_graph(
        self,
        *,
        project_id: str,
        snapshot_ref: str,
        snapshot: RepositoryIndexSnapshot,
        snapshot_sha256: str,
        policy_sha256: str,
        previous: PythonDependencyGraph | None,
        previous_ref: str | None,
        previous_sha256: str | None,
    ) -> PythonDependencyGraph:
        nodes = tuple(
            sorted(
                (
                    PythonDependencyNode(
                        path=item.path,
                        module=_python_module(item.path),
                        sha256=item.project_file.sha256,
                        is_test=item.project_file.is_test,
                        imports=tuple(sorted(set(item.project_file.imports))),
                    )
                    for item in snapshot.files
                    if item.project_file.language == "python"
                ),
                key=lambda node: node.path,
            )
        )
        if len(nodes) > self.max_nodes:
            raise RepositoryDependencyError("dependency graph exceeds its node limit")
        module_map = _module_map(nodes)
        module_map_sha256 = hashlib.sha256(
            _canonical_json(
                [(module, list(paths)) for module, paths in sorted(module_map.items())]
            ).encode("utf-8")
        ).hexdigest()

        previous_nodes = {node.path: node for node in previous.nodes} if previous else {}
        previous_edges: dict[str, list[PythonDependencyEdge]] = defaultdict(list)
        previous_unresolved: dict[str, list[PythonUnresolvedImport]] = defaultdict(list)
        if previous:
            for edge in previous.edges:
                previous_edges[edge.source_path].append(edge)
            for item in previous.unresolved_imports:
                previous_unresolved[item.source_path].append(item)

        can_reuse_resolution = bool(
            previous and previous.module_map_sha256 == module_map_sha256
        )
        edges: list[PythonDependencyEdge] = []
        unresolved: list[PythonUnresolvedImport] = []
        reused: list[str] = []
        recomputed: list[str] = []
        for node in nodes:
            if can_reuse_resolution and previous_nodes.get(node.path) == node:
                reused.append(node.path)
                edges.extend(previous_edges.get(node.path, ()))
                unresolved.extend(previous_unresolved.get(node.path, ()))
                continue
            recomputed.append(node.path)
            for raw_import in node.imports:
                target, reason, candidates = _resolve_import(node, raw_import, module_map)
                if target is not None:
                    if target != node.path:
                        edges.append(
                            PythonDependencyEdge(
                                source_path=node.path,
                                target_path=target,
                                raw_import=raw_import,
                            )
                        )
                    continue
                unresolved.append(
                    PythonUnresolvedImport(
                        source_path=node.path,
                        raw_import=raw_import,
                        reason=reason or UnresolvedImportReason.INVALID_IMPORT,
                        candidate_paths=candidates,
                    )
                )

        edges_tuple = tuple(sorted(set(edges), key=_edge_key))
        unresolved_tuple = tuple(sorted(set(unresolved), key=_unresolved_key))
        if len(edges_tuple) > self.max_edges:
            raise RepositoryDependencyError("dependency graph exceeds its edge limit")
        if len(unresolved_tuple) > self.max_unresolved:
            raise RepositoryDependencyError("dependency graph exceeds its unresolved-import limit")
        graph = PythonDependencyGraph(
            project_id=project_id,
            repository_url=snapshot.repository_url,
            base_ref=snapshot.base_ref,
            base_sha=snapshot.base_sha,
            namespace=self.namespace(project_id),
            repository_snapshot_ref=snapshot_ref,
            repository_snapshot_sha256=snapshot_sha256,
            policy_sha256=policy_sha256,
            module_map_sha256=module_map_sha256,
            previous_graph_ref=previous_ref,
            previous_graph_sha256=previous_sha256,
            nodes=nodes,
            edges=edges_tuple,
            unresolved_imports=unresolved_tuple,
            delta=PythonDependencyGraphDelta(
                reused_paths=tuple(reused),
                recomputed_paths=tuple(recomputed),
                deleted_paths=tuple(sorted(set(previous_nodes) - {node.path for node in nodes})),
            ),
        )
        if len(graph.canonical_content().encode("utf-8")) > self.graph_max_bytes:
            raise RepositoryDependencyError("dependency graph exceeds its byte limit")
        return graph

    def _impacts(
        self,
        *,
        current: PythonDependencyGraph,
        previous: PythonDependencyGraph | None,
        current_seeds: tuple[str, ...],
        previous_seeds: tuple[str, ...],
    ) -> tuple[DependencyImpactItem, ...]:
        current_nodes = {node.path: node for node in current.nodes}
        previous_nodes = {node.path: node for node in previous.nodes} if previous else {}
        selected: dict[str, DependencyImpactItem] = {}
        traversed: set[tuple[str, str, str]] = set()
        for label, graph, nodes, seeds in (
            ("current", current, current_nodes, current_seeds),
            ("previous", previous, previous_nodes, previous_seeds),
        ):
            if graph is None:
                if seeds:
                    raise RepositoryDependencyError(
                        "dependency impact requires the verified predecessor graph"
                    )
                continue
            reverse: dict[str, set[str]] = defaultdict(set)
            for edge in graph.edges:
                reverse[edge.target_path].add(edge.source_path)
            for seed in seeds:
                if seed not in nodes:
                    continue
                queue = deque([(seed, (seed,))])
                visited = {seed}
                while queue:
                    path, chain = queue.popleft()
                    traversed.add((label, seed, path))
                    if len(traversed) > self.max_impact_nodes:
                        raise RepositoryDependencyError(
                            "dependency impact exceeds its traversal limit"
                        )
                    node = nodes[path]
                    depth = len(chain) - 1
                    item = DependencyImpactItem(
                        path=path,
                        changed_path=seed,
                        is_test=node.is_test,
                        present_in_current_snapshot=path in current_nodes,
                        depth=depth,
                        confidence=(
                            DependencyImpactConfidence.HIGH
                            if depth <= 1
                            else DependencyImpactConfidence.MEDIUM
                        ),
                        dependency_chain=chain,
                    )
                    prior = selected.get(path)
                    if prior is None or _impact_key(item) < _impact_key(prior):
                        selected[path] = item
                    dependents = sorted(reverse.get(path, ()))
                    if depth == self.max_impact_depth:
                        if any(dependent not in visited for dependent in dependents):
                            raise RepositoryDependencyError(
                                "dependency impact exceeds its depth limit"
                            )
                        continue
                    for dependent in dependents:
                        if dependent in visited:
                            continue
                        visited.add(dependent)
                        queue.append((dependent, (*chain, dependent)))
        if len(selected) > self.max_impact_nodes:
            raise RepositoryDependencyError("dependency impact exceeds its result limit")
        return tuple(selected[path] for path in sorted(selected))

    def _matching_predecessor_graph(
        self,
        graph: PythonDependencyGraph,
        *,
        expected_snapshot_ref: str,
        expected_snapshot_sha256: str,
    ) -> PythonDependencyGraph | None:
        if not graph.previous_graph_ref or not graph.previous_graph_sha256:
            return None
        previous = self._load_graph(graph.previous_graph_ref, graph.previous_graph_sha256)
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
            raise RepositoryDependencyError(
                "repository predecessor project scope does not match"
            )
        if (
            previous.repository_url != current.repository_url
            or previous.base_ref != current.base_ref
        ):
            raise RepositoryDependencyError(
                "repository predecessor source identity does not match"
            )
        if not hmac.compare_digest(previous.policy_sha256, current.policy_sha256):
            raise RepositoryDependencyError("repository predecessor policy does not match")

    def _write_graph(self, graph: PythonDependencyGraph) -> tuple[str, str]:
        content = graph.canonical_content()
        if len(content.encode("utf-8")) > self.graph_max_bytes:
            raise RepositoryDependencyError("dependency graph exceeds its byte limit")
        graph_sha256 = graph.canonical_hash()
        reference = self.artifacts.write_text(
            (
                f"dependency-graphs/{graph.project_id}/{graph.base_sha}/"
                f"graph-{graph_sha256}.json"
            ),
            content,
            "application/json",
        )
        if not hmac.compare_digest(reference.sha256, graph_sha256):
            raise RepositoryDependencyError("dependency graph artifact hash mismatch")
        return reference.uri, graph_sha256

    def _load_active_graph(
        self, state: RepositoryDependencyGraphState
    ) -> PythonDependencyGraph:
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
            raise RepositoryDependencyError(
                "active dependency graph state does not match artifact provenance"
            )
        return graph

    def _load_graph(self, reference: str, expected_sha256: str) -> PythonDependencyGraph:
        try:
            content = self.artifacts.read_text_bounded_verified(
                reference,
                expected_sha256=expected_sha256,
                max_bytes=self.graph_max_bytes,
            )
            graph = PythonDependencyGraph.model_validate_json(content)
        except (OSError, UnicodeError, ValueError) as exc:
            raise RepositoryDependencyError(
                "dependency graph failed bounded integrity verification"
            ) from exc
        if not hmac.compare_digest(graph.canonical_hash(), expected_sha256):
            raise RepositoryDependencyError("dependency graph canonical hash mismatch")
        return graph

    def _load_report(self, reference: str, expected_sha256: str) -> DependencyImpactReport:
        try:
            content = self.artifacts.read_text_bounded_verified(
                reference,
                expected_sha256=expected_sha256,
                max_bytes=self.impact_max_bytes,
            )
            report = DependencyImpactReport.model_validate_json(content)
        except (OSError, UnicodeError, ValueError) as exc:
            raise RepositoryDependencyError(
                "dependency impact report failed bounded integrity verification"
            ) from exc
        if not hmac.compare_digest(report.canonical_hash(), expected_sha256):
            raise RepositoryDependencyError("dependency impact report canonical hash mismatch")
        return report

    def _verify_graph_compatibility(
        self, graph: PythonDependencyGraph, *, project_id: str
    ) -> None:
        if graph.project_id != project_id or graph.namespace != self.namespace(project_id):
            raise RepositoryDependencyError("dependency graph project scope does not match")
        if not hmac.compare_digest(graph.policy_sha256, self._policy_sha256()):
            raise RepositoryDependencyError("dependency graph policy does not match")

    def _policy_sha256(self) -> str:
        return hashlib.sha256(
            _canonical_json(
                {
                    "schema_version": "1",
                    "dependency_graph_policy_version": DEPENDENCY_GRAPH_POLICY_VERSION,
                    "repository_index_policy_version": INDEX_POLICY_VERSION,
                    "resolver": "python-static-module-v1",
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
            raise RepositoryDependencyError("project ID is invalid")


def _python_module(path: str) -> str:
    parts = path[:-3].split("/")
    if len(parts) > 1 and parts[0] == "src":
        parts = parts[1:]
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts) or "__root__"


def _module_map(nodes: tuple[PythonDependencyNode, ...]) -> dict[str, tuple[str, ...]]:
    values: dict[str, list[str]] = defaultdict(list)
    for node in nodes:
        if node.module != "__root__":
            values[node.module].append(node.path)
    return {module: tuple(sorted(paths)) for module, paths in values.items()}


def _resolve_import(
    node: PythonDependencyNode,
    raw_import: str,
    module_map: dict[str, tuple[str, ...]],
) -> tuple[str | None, UnresolvedImportReason | None, tuple[str, ...]]:
    module_text, separator, imported_name = raw_import.partition(":")
    level = len(module_text) - len(module_text.lstrip("."))
    module_text = module_text[level:]
    if separator and not imported_name:
        return None, UnresolvedImportReason.INVALID_IMPORT, ()
    if level:
        package = _source_package(node.path)
        parts = package.split(".") if package else []
        ascend = level - 1
        if not parts or ascend >= len(parts):
            return None, UnresolvedImportReason.RELATIVE_OUTSIDE_PACKAGE, ()
        parts = parts[: len(parts) - ascend]
        if module_text:
            parts.extend(module_text.split("."))
        base_module = ".".join(parts)
    else:
        base_module = module_text
    if not base_module:
        return None, UnresolvedImportReason.INVALID_IMPORT, ()

    candidate_module = base_module
    if separator and imported_name != "*":
        deeper = f"{base_module}.{imported_name}"
        if deeper in module_map:
            candidate_module = deeper
    paths = module_map.get(candidate_module, ())
    if not paths and candidate_module != base_module:
        paths = module_map.get(base_module, ())
    if not paths:
        return None, UnresolvedImportReason.MISSING_OR_EXTERNAL, ()
    if len(paths) > 1:
        return None, UnresolvedImportReason.AMBIGUOUS_MODULE, paths
    return paths[0], None, ()


def _source_package(path: str) -> str:
    module = _python_module(path)
    if module == "__root__":
        return ""
    if path.endswith("/__init__.py"):
        return module
    return module.rpartition(".")[0]


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


def _edge_key(edge: PythonDependencyEdge) -> tuple[str, str, str]:
    return edge.source_path, edge.target_path, edge.raw_import


def _unresolved_key(
    item: PythonUnresolvedImport,
) -> tuple[str, str, str, tuple[str, ...]]:
    return item.source_path, item.raw_import, item.reason.value, item.candidate_paths


def _impact_key(
    item: DependencyImpactItem,
) -> tuple[int, str, tuple[str, ...]]:
    return item.depth, item.changed_path, item.dependency_chain


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
