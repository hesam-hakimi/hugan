from __future__ import annotations

import ast
import hashlib
import hmac
import json
import re
import subprocess
from collections import defaultdict
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator, model_validator

from universal_coding_agent.core.models import FrozenModel
from universal_coding_agent.core.safe_models import normalize_repository_path
from universal_coding_agent.product.dependency_graphs import (
    DEPENDENCY_GRAPH_POLICY_VERSION,
    PythonDependencyGraph,
    RepositoryDependencyError,
    RepositoryDependencyService,
)
from universal_coding_agent.product.repository_indexes import RepositoryIndexSnapshot
from universal_coding_agent.product.search_service import (
    RepositoryCallGraphState,
    RepositoryCallGraphStateError,
    SearchService,
)
from universal_coding_agent.repository.indexer import (
    INDEX_POLICY_VERSION,
    RepositoryIndexingError,
)
from universal_coding_agent.storage.artifacts import ArtifactStore

DEFAULT_CALL_GRAPH_MAX_BYTES = 12_000_000
DEFAULT_CALL_GRAPH_MAX_SOURCE_BYTES = 64_000_000
DEFAULT_CALL_GRAPH_MAX_SYMBOLS = 100_000
DEFAULT_CALL_GRAPH_MAX_EDGES = 250_000
DEFAULT_CALL_GRAPH_MAX_UNRESOLVED = 250_000
DEFAULT_CALL_GRAPH_MAX_CALLS_PER_FILE = 50_000
DEFAULT_CALL_GRAPH_MAX_EXPRESSION_BYTES = 1_024
CALL_GRAPH_POLICY_VERSION = "1"
_PROJECT_ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")


class RepositoryCallGraphError(ValueError):
    """Python call evidence cannot satisfy its bounded provenance contract."""


class PythonSymbolKind(StrEnum):
    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"


class PythonParseFailureReason(StrEnum):
    INVALID_UTF8 = "invalid_utf8"
    SYNTAX_ERROR = "syntax_error"
    UNSUPPORTED_MODE = "unsupported_mode"


class PythonCallResolution(StrEnum):
    LEXICAL_SYMBOL = "lexical_symbol"
    IMPORTED_SYMBOL = "imported_symbol"
    IMPORTED_MODULE_ATTRIBUTE = "imported_module_attribute"
    EXPLICIT_CLASS_ATTRIBUTE = "explicit_class_attribute"


class UnresolvedCallReason(StrEnum):
    NO_ENCLOSING_SYMBOL = "no_enclosing_symbol"
    UNSUPPORTED_CONTEXT = "unsupported_context"
    UNSUPPORTED_CALLEE = "unsupported_callee"
    UNRESOLVED_NAME = "unresolved_name"
    SHADOWED_NAME = "shadowed_name"
    AMBIGUOUS_SYMBOL = "ambiguous_symbol"
    UNRESOLVED_IMPORT = "unresolved_import"
    MISSING_IMPORTED_SYMBOL = "missing_imported_symbol"
    DYNAMIC_RECEIVER = "dynamic_receiver"
    WILDCARD_IMPORT = "wildcard_import"


class PythonCallGraphFile(FrozenModel):
    path: str = Field(min_length=1, max_length=4096)
    module: str = Field(min_length=1, max_length=4096)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    parse_failure: PythonParseFailureReason | None = None

    @field_validator("path")
    @classmethod
    def validate_path(cls, value: str) -> str:
        return normalize_repository_path(value)

    @model_validator(mode="after")
    def validate_module(self) -> PythonCallGraphFile:
        if self.module != _python_module(self.path):
            raise ValueError("call-graph file module does not match its path")
        return self


class PythonSymbol(FrozenModel):
    symbol_id: str = Field(min_length=1, max_length=8192)
    path: str = Field(min_length=1, max_length=4096)
    module: str = Field(min_length=1, max_length=4096)
    qualname: str = Field(min_length=1, max_length=4096)
    name: str = Field(min_length=1, max_length=512)
    kind: PythonSymbolKind
    line: int = Field(ge=1)
    column: int = Field(ge=0)
    end_line: int = Field(ge=1)
    is_async: bool = False
    parent_symbol_id: str | None = Field(default=None, max_length=8192)

    @field_validator("path")
    @classmethod
    def validate_path(cls, value: str) -> str:
        return normalize_repository_path(value)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not value.isidentifier():
            raise ValueError("Python symbol name is not an identifier")
        return value

    @model_validator(mode="after")
    def validate_identity(self) -> PythonSymbol:
        expected = _symbol_id(
            self.module,
            self.qualname,
            self.kind,
            self.line,
            self.column,
        )
        if self.symbol_id != expected:
            raise ValueError("Python symbol ID does not match its canonical identity")
        if self.end_line < self.line:
            raise ValueError("Python symbol end line precedes its start line")
        if self.kind is PythonSymbolKind.CLASS and self.is_async:
            raise ValueError("Python class symbols cannot be async")
        return self


class PythonUnsafeSymbolBinding(FrozenModel):
    module: str = Field(min_length=1, max_length=4096)
    qualname: str = Field(min_length=1, max_length=4096)
    candidate_symbol_ids: tuple[str, ...] = Field(min_length=1)

    @field_validator("candidate_symbol_ids")
    @classmethod
    def validate_candidates(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        if values != tuple(sorted(set(values))):
            raise ValueError("unsafe symbol candidates must be unique and sorted")
        return values


class PythonCallEdge(FrozenModel):
    source_path: str = Field(min_length=1, max_length=4096)
    caller_symbol_id: str = Field(min_length=1, max_length=8192)
    target_symbol_id: str = Field(min_length=1, max_length=8192)
    line: int = Field(ge=1)
    column: int = Field(ge=0)
    expression: str = Field(min_length=1, max_length=4096)
    resolution: PythonCallResolution

    @field_validator("source_path")
    @classmethod
    def validate_path(cls, value: str) -> str:
        return normalize_repository_path(value)


class PythonUnresolvedCall(FrozenModel):
    source_path: str = Field(min_length=1, max_length=4096)
    caller_symbol_id: str | None = Field(default=None, max_length=8192)
    line: int = Field(ge=1)
    column: int = Field(ge=0)
    expression: str = Field(min_length=1, max_length=4096)
    reason: UnresolvedCallReason
    candidate_symbol_ids: tuple[str, ...] = ()

    @field_validator("source_path")
    @classmethod
    def validate_path(cls, value: str) -> str:
        return normalize_repository_path(value)

    @field_validator("candidate_symbol_ids")
    @classmethod
    def validate_candidates(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        if values != tuple(sorted(set(values))):
            raise ValueError("unresolved call candidates must be unique and sorted")
        return values

    @model_validator(mode="after")
    def validate_candidate_reason(self) -> PythonUnresolvedCall:
        if self.candidate_symbol_ids and self.reason is not UnresolvedCallReason.AMBIGUOUS_SYMBOL:
            raise ValueError("only ambiguous calls may retain symbol candidates")
        return self


class PythonCallGraphDelta(FrozenModel):
    reused_paths: tuple[str, ...] = ()
    recomputed_paths: tuple[str, ...] = ()
    deleted_paths: tuple[str, ...] = ()

    @field_validator("reused_paths", "recomputed_paths", "deleted_paths")
    @classmethod
    def validate_paths(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(normalize_repository_path(value) for value in values)
        if normalized != tuple(sorted(set(normalized))):
            raise ValueError("call-graph delta paths must be unique and sorted")
        return normalized


class PythonCallGraph(FrozenModel):
    schema_version: Literal["1"] = "1"
    project_id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")
    repository_url: str = Field(min_length=1, max_length=2048)
    base_ref: str = Field(min_length=1, max_length=256)
    base_sha: str = Field(pattern=r"^[0-9a-f]{40,64}$")
    namespace: str = Field(pattern=r"^explicit:repository-call-graph:[a-zA-Z0-9._-]+$")
    repository_snapshot_ref: str = Field(pattern=r"^artifact://[a-zA-Z0-9._/-]+$")
    repository_snapshot_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    dependency_graph_ref: str = Field(pattern=r"^artifact://[a-zA-Z0-9._/-]+$")
    dependency_graph_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    policy_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    symbol_index_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    previous_graph_ref: str | None = Field(default=None, pattern=r"^artifact://[a-zA-Z0-9._/-]+$")
    previous_graph_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    files: tuple[PythonCallGraphFile, ...] = ()
    symbols: tuple[PythonSymbol, ...] = ()
    unsafe_symbol_bindings: tuple[PythonUnsafeSymbolBinding, ...] = ()
    edges: tuple[PythonCallEdge, ...] = ()
    unresolved_calls: tuple[PythonUnresolvedCall, ...] = ()
    delta: PythonCallGraphDelta

    @model_validator(mode="after")
    def validate_graph(self) -> PythonCallGraph:
        if self.namespace != f"explicit:repository-call-graph:{self.project_id}":
            raise ValueError("call-graph namespace does not match project identity")
        if (self.previous_graph_ref is None) != (self.previous_graph_sha256 is None):
            raise ValueError("call-graph predecessor reference and hash must be paired")
        file_paths = tuple(item.path for item in self.files)
        if file_paths != tuple(sorted(set(file_paths))):
            raise ValueError("call-graph files must be unique and sorted")
        symbol_keys = tuple(_symbol_key(item) for item in self.symbols)
        if symbol_keys != tuple(sorted(set(symbol_keys))):
            raise ValueError("call-graph symbols must be unique and sorted")
        symbol_ids = {item.symbol_id for item in self.symbols}
        if len(symbol_ids) != len(self.symbols):
            raise ValueError("call-graph symbol IDs must be unique")
        known_paths = set(file_paths)
        file_modules = {item.path: item.module for item in self.files}
        by_id = {item.symbol_id: item for item in self.symbols}
        qualified_ids: dict[tuple[str, str], list[str]] = defaultdict(list)
        for symbol in self.symbols:
            qualified_ids[(symbol.module, symbol.qualname)].append(symbol.symbol_id)
            if symbol.path not in known_paths:
                raise ValueError("call-graph symbol references an unknown file")
            if symbol.module != file_modules[symbol.path]:
                raise ValueError("call-graph symbol module does not match its file")
            if symbol.parent_symbol_id is not None:
                parent = by_id.get(symbol.parent_symbol_id)
                if parent is None or parent.path != symbol.path:
                    raise ValueError("call-graph symbol parent is invalid")
                separator = "." if parent.kind is PythonSymbolKind.CLASS else ".<locals>."
                if symbol.qualname != f"{parent.qualname}{separator}{symbol.name}":
                    raise ValueError("call-graph symbol qualified parent is invalid")
                if (
                    symbol.kind is PythonSymbolKind.METHOD
                    and parent.kind is not PythonSymbolKind.CLASS
                ) or (
                    symbol.kind is PythonSymbolKind.FUNCTION
                    and parent.kind is PythonSymbolKind.CLASS
                ):
                    raise ValueError("call-graph method identity is invalid")
            elif symbol.qualname != symbol.name or symbol.kind is PythonSymbolKind.METHOD:
                raise ValueError("top-level call-graph symbol identity is invalid")
        unsafe_keys = tuple(_unsafe_binding_key(item) for item in self.unsafe_symbol_bindings)
        if unsafe_keys != tuple(sorted(set(unsafe_keys))):
            raise ValueError("unsafe symbol bindings must be unique and sorted")
        for item in self.unsafe_symbol_bindings:
            if item.candidate_symbol_ids != tuple(
                sorted(qualified_ids.get((item.module, item.qualname), ()))
            ):
                raise ValueError("unsafe symbol binding candidates are incomplete")
            for candidate_id in item.candidate_symbol_ids:
                candidate = by_id.get(candidate_id)
                if (
                    candidate is None
                    or candidate.module != item.module
                    or candidate.qualname != item.qualname
                ):
                    raise ValueError("unsafe symbol binding candidate is invalid")
        edge_keys = tuple(_edge_key(item) for item in self.edges)
        if edge_keys != tuple(sorted(set(edge_keys))):
            raise ValueError("call-graph edges must be unique and sorted")
        for edge in self.edges:
            caller = by_id.get(edge.caller_symbol_id)
            if (
                caller is None
                or edge.target_symbol_id not in symbol_ids
                or caller.path != edge.source_path
            ):
                raise ValueError("call-graph edge references an unknown symbol")
        unresolved_keys = tuple(_unresolved_key(item) for item in self.unresolved_calls)
        if unresolved_keys != tuple(sorted(set(unresolved_keys))):
            raise ValueError("unresolved calls must be unique and sorted")
        for item in self.unresolved_calls:
            if item.source_path not in known_paths:
                raise ValueError("unresolved call references an unknown file")
            if item.caller_symbol_id is not None:
                caller = by_id.get(item.caller_symbol_id)
                if caller is None or caller.path != item.source_path:
                    raise ValueError("unresolved call references an unknown caller")
            if any(candidate not in symbol_ids for candidate in item.candidate_symbol_ids):
                raise ValueError("unresolved call candidate is unknown")
        reused = set(self.delta.reused_paths)
        recomputed = set(self.delta.recomputed_paths)
        deleted = set(self.delta.deleted_paths)
        if reused & recomputed:
            raise ValueError("call-graph reused and recomputed paths overlap")
        if reused | recomputed != known_paths:
            raise ValueError("call-graph delta does not cover every current file")
        if deleted & known_paths:
            raise ValueError("call-graph deleted paths remain in the current graph")
        if not hmac.compare_digest(
            self.symbol_index_sha256,
            _symbol_index_hash(
                self.files,
                self.symbols,
                self.unsafe_symbol_bindings,
            ),
        ):
            raise ValueError("call-graph symbol index hash does not match its evidence")
        return self

    def canonical_content(self) -> str:
        return _canonical_json(self.model_dump(mode="json"))

    def canonical_hash(self) -> str:
        return hashlib.sha256(self.canonical_content().encode("utf-8")).hexdigest()


class RepositoryCallGraphResult(FrozenModel):
    graph_ref: str = Field(pattern=r"^artifact://[a-zA-Z0-9._/-]+$")
    graph_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    graph: PythonCallGraph
    replayed: bool = False


class RepositoryCallGraphService:
    """Build bounded static Python call evidence from exact repository state."""

    def __init__(
        self,
        artifacts: ArtifactStore,
        search: SearchService,
        dependencies: RepositoryDependencyService,
        *,
        graph_max_bytes: int = DEFAULT_CALL_GRAPH_MAX_BYTES,
        max_source_bytes: int = DEFAULT_CALL_GRAPH_MAX_SOURCE_BYTES,
        max_symbols: int = DEFAULT_CALL_GRAPH_MAX_SYMBOLS,
        max_edges: int = DEFAULT_CALL_GRAPH_MAX_EDGES,
        max_unresolved: int = DEFAULT_CALL_GRAPH_MAX_UNRESOLVED,
        max_calls_per_file: int = DEFAULT_CALL_GRAPH_MAX_CALLS_PER_FILE,
        max_expression_bytes: int = DEFAULT_CALL_GRAPH_MAX_EXPRESSION_BYTES,
    ) -> None:
        limits = (
            graph_max_bytes,
            max_source_bytes,
            max_symbols,
            max_edges,
            max_unresolved,
            max_calls_per_file,
            max_expression_bytes,
        )
        if any(limit < 1 for limit in limits):
            raise ValueError("repository call-graph limits must be positive")
        if max_expression_bytes > 4096:
            raise ValueError("call-expression byte limit cannot exceed the schema limit")
        self.artifacts = artifacts
        self.search = search
        self.dependencies = dependencies
        self.repository_indexes = dependencies.repository_indexes
        self.graph_max_bytes = graph_max_bytes
        self.max_source_bytes = max_source_bytes
        self.max_symbols = max_symbols
        self.max_edges = max_edges
        self.max_unresolved = max_unresolved
        self.max_calls_per_file = max_calls_per_file
        self.max_expression_bytes = max_expression_bytes

    def build_graph(
        self,
        *,
        project_id: str,
        root: Path,
        expected_repository_snapshot_ref: str,
        expected_repository_snapshot_sha256: str,
        expected_dependency_graph_ref: str,
        expected_dependency_graph_sha256: str,
        expected_previous_call_graph_ref: str | None,
        expected_previous_call_graph_sha256: str | None,
    ) -> RepositoryCallGraphResult:
        self._validate_project_id(project_id)
        if (expected_previous_call_graph_ref is None) != (
            expected_previous_call_graph_sha256 is None
        ):
            raise RepositoryCallGraphError(
                "expected call-graph predecessor reference and hash must be paired"
            )
        try:
            repository_state, snapshot, dependency_state, dependency_graph = (
                self.dependencies.verified_active_graph(
                    project_id=project_id,
                    expected_repository_snapshot_ref=expected_repository_snapshot_ref,
                    expected_repository_snapshot_sha256=(expected_repository_snapshot_sha256),
                    expected_graph_ref=expected_dependency_graph_ref,
                    expected_graph_sha256=expected_dependency_graph_sha256,
                )
            )
        except RepositoryDependencyError as exc:
            raise RepositoryCallGraphError(str(exc)) from exc
        self._verify_clean_base(root, snapshot.base_sha)

        namespace = self.namespace(project_id)
        active_state = self.search.repository_call_graph_state(namespace)
        previous: PythonCallGraph | None = None
        if active_state is None:
            if expected_previous_call_graph_sha256 is not None:
                raise RepositoryCallGraphError(
                    "expected predecessor repository call graph does not exist"
                )
        else:
            if (
                expected_previous_call_graph_ref != active_state.graph_ref
                or expected_previous_call_graph_sha256 != active_state.graph_sha256
            ):
                raise RepositoryCallGraphError(
                    "expected predecessor does not match the active repository call graph"
                )
            previous = self._load_active_graph(active_state)
            self._verify_graph_compatibility(previous, project_id=project_id)
            if (
                active_state.repository_snapshot_ref == repository_state.snapshot_ref
                and hmac.compare_digest(
                    active_state.repository_snapshot_sha256,
                    repository_state.snapshot_sha256,
                )
                and active_state.dependency_graph_ref == dependency_state.graph_ref
                and hmac.compare_digest(
                    active_state.dependency_graph_sha256,
                    dependency_state.graph_sha256,
                )
            ):
                self._verify_clean_base(root, snapshot.base_sha)
                return RepositoryCallGraphResult(
                    graph_ref=active_state.graph_ref,
                    graph_sha256=active_state.graph_sha256,
                    graph=previous,
                    replayed=True,
                )

        policy_sha256 = self._policy_sha256()
        graph = self._derive_graph(
            project_id=project_id,
            root=root,
            snapshot=snapshot,
            snapshot_ref=repository_state.snapshot_ref,
            snapshot_sha256=repository_state.snapshot_sha256,
            dependency_graph=dependency_graph,
            dependency_graph_ref=dependency_state.graph_ref,
            dependency_graph_sha256=dependency_state.graph_sha256,
            policy_sha256=policy_sha256,
            previous=previous,
            previous_ref=active_state.graph_ref if active_state else None,
            previous_sha256=active_state.graph_sha256 if active_state else None,
        )
        graph_ref, graph_sha256 = self._write_graph(graph)
        self._verify_clean_base(root, snapshot.base_sha)
        state = RepositoryCallGraphState(
            namespace=namespace,
            project_id=project_id,
            repository_url=snapshot.repository_url,
            base_ref=snapshot.base_ref,
            base_sha=snapshot.base_sha,
            repository_snapshot_ref=repository_state.snapshot_ref,
            repository_snapshot_sha256=repository_state.snapshot_sha256,
            dependency_graph_ref=dependency_state.graph_ref,
            dependency_graph_sha256=dependency_state.graph_sha256,
            graph_ref=graph_ref,
            graph_sha256=graph_sha256,
            policy_sha256=policy_sha256,
        )
        try:
            self.search.apply_repository_call_graph_state(
                state=state,
                expected_previous_graph_ref=expected_previous_call_graph_ref,
                expected_previous_graph_sha256=expected_previous_call_graph_sha256,
            )
        except RepositoryCallGraphStateError as exc:
            raise RepositoryCallGraphError(str(exc)) from exc
        verified = self._load_graph(graph_ref, graph_sha256)
        return RepositoryCallGraphResult(
            graph_ref=graph_ref,
            graph_sha256=graph_sha256,
            graph=verified,
        )

    def verified_active_graph(
        self,
        *,
        project_id: str,
        expected_graph_ref: str,
        expected_graph_sha256: str,
    ) -> tuple[RepositoryCallGraphState, PythonCallGraph]:
        self._validate_project_id(project_id)
        state = self.search.repository_call_graph_state(self.namespace(project_id))
        if state is None:
            raise RepositoryCallGraphError("active repository call graph does not exist")
        if state.graph_ref != expected_graph_ref or not hmac.compare_digest(
            state.graph_sha256, expected_graph_sha256
        ):
            raise RepositoryCallGraphError(
                "active repository call-graph reference or hash does not match"
            )
        try:
            self.dependencies.verified_active_graph(
                project_id=project_id,
                expected_repository_snapshot_ref=state.repository_snapshot_ref,
                expected_repository_snapshot_sha256=state.repository_snapshot_sha256,
                expected_graph_ref=state.dependency_graph_ref,
                expected_graph_sha256=state.dependency_graph_sha256,
            )
        except RepositoryDependencyError as exc:
            raise RepositoryCallGraphError(
                "active repository call graph no longer matches its verified inputs"
            ) from exc
        graph = self._load_active_graph(state)
        self._verify_graph_compatibility(graph, project_id=project_id)
        return state, graph

    @staticmethod
    def namespace(project_id: str) -> str:
        return f"explicit:repository-call-graph:{project_id}"

    def _derive_graph(
        self,
        *,
        project_id: str,
        root: Path,
        snapshot: RepositoryIndexSnapshot,
        snapshot_ref: str,
        snapshot_sha256: str,
        dependency_graph: PythonDependencyGraph,
        dependency_graph_ref: str,
        dependency_graph_sha256: str,
        policy_sha256: str,
        previous: PythonCallGraph | None,
        previous_ref: str | None,
        previous_sha256: str | None,
    ) -> PythonCallGraph:
        parsed = self._parse_sources(root, snapshot, dependency_graph)
        symbols = tuple(
            sorted(
                (
                    symbol
                    for item in parsed
                    if item.analyzer is not None
                    for symbol in item.analyzer.symbols
                ),
                key=_symbol_key,
            )
        )
        if len(symbols) > self.max_symbols:
            raise RepositoryCallGraphError("repository call graph exceeds its symbol limit")
        files = tuple(item.file for item in parsed)
        symbol_index = _SymbolIndex(
            symbols,
            tuple(item.analyzer for item in parsed if item.analyzer is not None),
        )
        unsafe_symbol_bindings = symbol_index.unsafe_bindings()
        symbol_index_sha256 = _symbol_index_hash(
            files,
            symbols,
            unsafe_symbol_bindings,
        )

        previous_files = {item.path: item for item in previous.files} if previous else {}
        previous_edges: dict[str, list[PythonCallEdge]] = defaultdict(list)
        previous_unresolved: dict[str, list[PythonUnresolvedCall]] = defaultdict(list)
        if previous:
            for edge in previous.edges:
                previous_edges[edge.source_path].append(edge)
            for item in previous.unresolved_calls:
                previous_unresolved[item.source_path].append(item)
        can_reuse = bool(previous and previous.symbol_index_sha256 == symbol_index_sha256)
        edges: list[PythonCallEdge] = []
        unresolved: list[PythonUnresolvedCall] = []
        reused: list[str] = []
        recomputed: list[str] = []
        for item in parsed:
            if can_reuse and previous_files.get(item.file.path) == item.file:
                reused.append(item.file.path)
                edges.extend(previous_edges.get(item.file.path, ()))
                unresolved.extend(previous_unresolved.get(item.file.path, ()))
                continue
            recomputed.append(item.file.path)
            if item.tree is None or item.analyzer is None:
                continue
            collector = _CallCollector(
                path=item.file.path,
                tree=item.tree,
                analyzer=item.analyzer,
                symbol_index=symbol_index,
                max_expression_bytes=self.max_expression_bytes,
                max_calls=self.max_calls_per_file,
            )
            try:
                file_edges, file_unresolved = collector.collect()
            except RepositoryCallGraphError:
                raise
            except (RecursionError, ValueError) as exc:
                raise RepositoryCallGraphError(
                    "Python call traversal exceeded its metadata bounds"
                ) from exc
            edges.extend(file_edges)
            unresolved.extend(file_unresolved)
            if len(edges) > self.max_edges:
                raise RepositoryCallGraphError("repository call graph exceeds its edge limit")
            if len(unresolved) > self.max_unresolved:
                raise RepositoryCallGraphError(
                    "repository call graph exceeds its unresolved-call limit"
                )

        edges_tuple = tuple(sorted(set(edges), key=_edge_key))
        unresolved_tuple = tuple(sorted(set(unresolved), key=_unresolved_key))
        if len(edges_tuple) > self.max_edges:
            raise RepositoryCallGraphError("repository call graph exceeds its edge limit")
        if len(unresolved_tuple) > self.max_unresolved:
            raise RepositoryCallGraphError(
                "repository call graph exceeds its unresolved-call limit"
            )
        current_paths = {item.path for item in files}
        try:
            graph = PythonCallGraph(
                project_id=project_id,
                repository_url=snapshot.repository_url,
                base_ref=snapshot.base_ref,
                base_sha=snapshot.base_sha,
                namespace=self.namespace(project_id),
                repository_snapshot_ref=snapshot_ref,
                repository_snapshot_sha256=snapshot_sha256,
                dependency_graph_ref=dependency_graph_ref,
                dependency_graph_sha256=dependency_graph_sha256,
                policy_sha256=policy_sha256,
                symbol_index_sha256=symbol_index_sha256,
                previous_graph_ref=previous_ref,
                previous_graph_sha256=previous_sha256,
                files=files,
                symbols=symbols,
                unsafe_symbol_bindings=unsafe_symbol_bindings,
                edges=edges_tuple,
                unresolved_calls=unresolved_tuple,
                delta=PythonCallGraphDelta(
                    reused_paths=tuple(reused),
                    recomputed_paths=tuple(recomputed),
                    deleted_paths=tuple(sorted(set(previous_files) - current_paths)),
                ),
            )
        except ValueError as exc:
            raise RepositoryCallGraphError(
                "repository call graph failed canonical validation"
            ) from exc
        if len(graph.canonical_content().encode("utf-8")) > self.graph_max_bytes:
            raise RepositoryCallGraphError("repository call graph exceeds its byte limit")
        return graph

    def _parse_sources(
        self,
        root: Path,
        snapshot: RepositoryIndexSnapshot,
        dependency_graph: PythonDependencyGraph,
    ) -> tuple[_ParsedPython, ...]:
        root = root.resolve()
        snapshot_files = {item.path: item for item in snapshot.files}
        dependency_paths = {item.path for item in dependency_graph.nodes}
        expected_paths = {
            item.path for item in snapshot.files if item.project_file.language == "python"
        }
        if dependency_paths != expected_paths:
            raise RepositoryCallGraphError(
                "dependency graph Python paths do not match the repository snapshot"
            )
        dependency_nodes = {item.path: item for item in dependency_graph.nodes}
        edge_targets: dict[tuple[str, str], str] = {}
        for edge in dependency_graph.edges:
            key = (edge.source_path, edge.raw_import)
            prior = edge_targets.get(key)
            if prior is not None and prior != edge.target_path:
                raise RepositoryCallGraphError(
                    "dependency graph contains ambiguous resolved import evidence"
                )
            edge_targets[key] = edge.target_path
        total_source_bytes = 0
        symbol_count = 0
        parsed: list[_ParsedPython] = []
        for path in sorted(expected_paths):
            snapshot_file = snapshot_files[path]
            dependency_node = dependency_nodes[path]
            if (
                dependency_node.sha256 != snapshot_file.project_file.sha256
                or dependency_node.module != _python_module(path)
            ):
                raise RepositoryCallGraphError(
                    "dependency graph node does not match repository snapshot metadata"
                )
            if snapshot_file.git_mode not in {"100644", "100755"}:
                parsed.append(
                    _ParsedPython(
                        file=PythonCallGraphFile(
                            path=path,
                            module=dependency_node.module,
                            sha256=dependency_node.sha256,
                            parse_failure=PythonParseFailureReason.UNSUPPORTED_MODE,
                        )
                    )
                )
                continue
            source_path = (root / path).resolve()
            if source_path == root or root not in source_path.parents:
                raise RepositoryCallGraphError("Python source path escapes the source root")
            try:
                data = source_path.read_bytes()
            except OSError as exc:
                raise RepositoryCallGraphError("Python source cannot be read") from exc
            total_source_bytes += len(data)
            if total_source_bytes > self.max_source_bytes:
                raise RepositoryCallGraphError(
                    "repository call graph exceeds its source-byte limit"
                )
            project_file = snapshot_file.project_file
            if len(data) != project_file.size or not hmac.compare_digest(
                hashlib.sha256(data).hexdigest(), project_file.sha256
            ):
                raise RepositoryCallGraphError(
                    "Python source drifted from the verified repository snapshot"
                )
            try:
                source = data.decode("utf-8")
            except UnicodeDecodeError:
                parsed.append(
                    _ParsedPython(
                        file=PythonCallGraphFile(
                            path=path,
                            module=dependency_node.module,
                            sha256=dependency_node.sha256,
                            parse_failure=PythonParseFailureReason.INVALID_UTF8,
                        )
                    )
                )
                continue
            try:
                tree = ast.parse(source, filename=path)
            except (SyntaxError, ValueError, RecursionError):
                parsed.append(
                    _ParsedPython(
                        file=PythonCallGraphFile(
                            path=path,
                            module=dependency_node.module,
                            sha256=dependency_node.sha256,
                            parse_failure=PythonParseFailureReason.SYNTAX_ERROR,
                        )
                    )
                )
                continue
            targets = {
                raw_import: dependency_nodes[target_path].module
                for (source_path_key, raw_import), target_path in edge_targets.items()
                if source_path_key == path
            }
            analyzer = _SymbolAnalyzer(
                path=path,
                module=dependency_node.module,
                import_targets=targets,
                max_symbols=(self.max_symbols - symbol_count),
            )
            try:
                analyzer.visit(tree)
            except RepositoryCallGraphError:
                raise
            except (RecursionError, ValueError) as exc:
                raise RepositoryCallGraphError(
                    "Python symbol traversal exceeded its metadata bounds"
                ) from exc
            symbol_count += len(analyzer.symbols)
            parsed.append(
                _ParsedPython(
                    file=PythonCallGraphFile(
                        path=path,
                        module=dependency_node.module,
                        sha256=dependency_node.sha256,
                    ),
                    tree=tree,
                    analyzer=analyzer,
                )
            )
        return tuple(parsed)

    def _write_graph(self, graph: PythonCallGraph) -> tuple[str, str]:
        content = graph.canonical_content()
        if len(content.encode("utf-8")) > self.graph_max_bytes:
            raise RepositoryCallGraphError("repository call graph exceeds its byte limit")
        graph_sha256 = graph.canonical_hash()
        reference = self.artifacts.write_text(
            (f"call-graphs/{graph.project_id}/{graph.base_sha}/graph-{graph_sha256}.json"),
            content,
            "application/json",
        )
        if not hmac.compare_digest(reference.sha256, graph_sha256):
            raise RepositoryCallGraphError("repository call-graph artifact hash mismatch")
        return reference.uri, graph_sha256

    def _load_active_graph(self, state: RepositoryCallGraphState) -> PythonCallGraph:
        graph = self._load_graph(state.graph_ref, state.graph_sha256)
        if (
            graph.namespace != state.namespace
            or graph.project_id != state.project_id
            or graph.repository_url != state.repository_url
            or graph.base_ref != state.base_ref
            or graph.base_sha != state.base_sha
            or graph.repository_snapshot_ref != state.repository_snapshot_ref
            or graph.repository_snapshot_sha256 != state.repository_snapshot_sha256
            or graph.dependency_graph_ref != state.dependency_graph_ref
            or graph.dependency_graph_sha256 != state.dependency_graph_sha256
            or graph.policy_sha256 != state.policy_sha256
        ):
            raise RepositoryCallGraphError(
                "active repository call-graph state does not match artifact provenance"
            )
        return graph

    def _load_graph(self, reference: str, expected_sha256: str) -> PythonCallGraph:
        try:
            content = self.artifacts.read_text_bounded_verified(
                reference,
                expected_sha256=expected_sha256,
                max_bytes=self.graph_max_bytes,
            )
            graph = PythonCallGraph.model_validate_json(content)
        except (OSError, UnicodeError, ValueError) as exc:
            raise RepositoryCallGraphError(
                "repository call graph failed bounded integrity verification"
            ) from exc
        if not hmac.compare_digest(graph.canonical_hash(), expected_sha256):
            raise RepositoryCallGraphError("repository call-graph canonical hash mismatch")
        return graph

    def _verify_graph_compatibility(
        self,
        graph: PythonCallGraph,
        *,
        project_id: str,
    ) -> None:
        if graph.project_id != project_id or graph.namespace != self.namespace(project_id):
            raise RepositoryCallGraphError("repository call-graph project scope does not match")
        if not hmac.compare_digest(graph.policy_sha256, self._policy_sha256()):
            raise RepositoryCallGraphError("repository call-graph policy does not match")

    def _policy_sha256(self) -> str:
        return hashlib.sha256(
            _canonical_json(
                {
                    "schema_version": "1",
                    "call_graph_policy_version": CALL_GRAPH_POLICY_VERSION,
                    "dependency_graph_policy_version": DEPENDENCY_GRAPH_POLICY_VERSION,
                    "repository_index_policy_version": INDEX_POLICY_VERSION,
                    "resolver": "python-static-symbol-v1",
                    "graph_max_bytes": self.graph_max_bytes,
                    "max_source_bytes": self.max_source_bytes,
                    "max_symbols": self.max_symbols,
                    "max_edges": self.max_edges,
                    "max_unresolved": self.max_unresolved,
                    "max_calls_per_file": self.max_calls_per_file,
                    "max_expression_bytes": self.max_expression_bytes,
                }
            ).encode("utf-8")
        ).hexdigest()

    def _verify_clean_base(self, root: Path, base_sha: str) -> None:
        try:
            self.repository_indexes.indexer.verify_clean_base(root, base_sha=base_sha)
        except (RepositoryIndexingError, subprocess.SubprocessError) as exc:
            raise RepositoryCallGraphError(str(exc)) from exc

    @staticmethod
    def _validate_project_id(project_id: str) -> None:
        if not _PROJECT_ID.fullmatch(project_id):
            raise RepositoryCallGraphError("project ID is invalid")


class _BindingKind(StrEnum):
    SYMBOL = "symbol"
    IMPORT_MODULE = "import_module"
    IMPORT_SYMBOL = "import_symbol"
    SHADOW = "shadow"
    UNRESOLVED_IMPORT = "unresolved_import"


@dataclass(frozen=True)
class _Binding:
    kind: _BindingKind
    symbol_id: str | None = None
    target_module: str | None = None
    imported_name: str | None = None
    access_parts: tuple[str, ...] = ()
    conditional: bool = False


@dataclass
class _Scope:
    parent: str | None
    bindings: dict[str, set[_Binding]] = field(default_factory=dict)
    wildcard_import: bool = False

    def bind(self, name: str, binding: _Binding) -> None:
        self.bindings.setdefault(name, set()).add(binding)


@dataclass(frozen=True)
class _ParsedPython:
    file: PythonCallGraphFile
    tree: ast.Module | None = None
    analyzer: _SymbolAnalyzer | None = None


class _SymbolAnalyzer(ast.NodeVisitor):
    def __init__(
        self,
        *,
        path: str,
        module: str,
        import_targets: dict[str, str],
        max_symbols: int,
    ) -> None:
        self.path = path
        self.module = module
        self.import_targets = import_targets
        self.max_symbols = max_symbols
        self.symbols: list[PythonSymbol] = []
        self.symbols_by_id: dict[str, PythonSymbol] = {}
        self.node_symbols: dict[int, str] = {}
        self.scopes: dict[str | None, _Scope] = {None: _Scope(parent=None)}
        self.current_scope: str | None = None
        self.conditional_depth = 0

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_function(node, is_async=False)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_function(node, is_async=True)

    def _visit_function(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        *,
        is_async: bool,
    ) -> None:
        parent = self.symbols_by_id.get(self.current_scope or "")
        kind = (
            PythonSymbolKind.METHOD
            if parent is not None and parent.kind is PythonSymbolKind.CLASS
            else PythonSymbolKind.FUNCTION
        )
        symbol = self._new_symbol(node, kind=kind, is_async=is_async)
        self._scope().bind(
            node.name,
            _Binding(
                kind=_BindingKind.SYMBOL,
                symbol_id=symbol.symbol_id,
                conditional=bool(self.conditional_depth),
            ),
        )
        lexical_parent = self._child_lexical_parent()
        self.scopes[symbol.symbol_id] = _Scope(parent=lexical_parent)
        prior = self.current_scope
        prior_conditional_depth = self.conditional_depth
        self.current_scope = symbol.symbol_id
        self.conditional_depth = 0
        self._bind_arguments(node.args)
        for statement in node.body:
            self.visit(statement)
        self.current_scope = prior
        self.conditional_depth = prior_conditional_depth

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        symbol = self._new_symbol(node, kind=PythonSymbolKind.CLASS, is_async=False)
        self._scope().bind(
            node.name,
            _Binding(
                kind=_BindingKind.SYMBOL,
                symbol_id=symbol.symbol_id,
                conditional=bool(self.conditional_depth),
            ),
        )
        lexical_parent = self._child_lexical_parent()
        self.scopes[symbol.symbol_id] = _Scope(parent=lexical_parent)
        prior = self.current_scope
        prior_conditional_depth = self.conditional_depth
        self.current_scope = symbol.symbol_id
        self.conditional_depth = 0
        for statement in node.body:
            self.visit(statement)
        self.current_scope = prior
        self.conditional_depth = prior_conditional_depth

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            raw_import = alias.name
            bound_name = alias.asname or alias.name.split(".", 1)[0]
            target_module = self.import_targets.get(raw_import)
            if target_module is None:
                self._scope().bind(
                    bound_name,
                    _Binding(
                        kind=_BindingKind.UNRESOLVED_IMPORT,
                        conditional=bool(self.conditional_depth),
                    ),
                )
                continue
            access_parts = (
                (alias.asname,) if alias.asname is not None else tuple(alias.name.split("."))
            )
            self._scope().bind(
                bound_name,
                _Binding(
                    kind=_BindingKind.IMPORT_MODULE,
                    target_module=target_module,
                    access_parts=access_parts,
                    conditional=bool(self.conditional_depth),
                ),
            )

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module_text = f"{'.' * node.level}{node.module or ''}"
        base_module = _absolute_from_module(
            path=self.path,
            module=self.module,
            module_text=node.module or "",
            level=node.level,
        )
        for alias in node.names:
            raw_import = f"{module_text}:{alias.name}"
            if alias.name == "*":
                self._scope().wildcard_import = True
                continue
            bound_name = alias.asname or alias.name
            target_module = self.import_targets.get(raw_import)
            if target_module is None:
                self._scope().bind(
                    bound_name,
                    _Binding(
                        kind=_BindingKind.UNRESOLVED_IMPORT,
                        conditional=bool(self.conditional_depth),
                    ),
                )
                continue
            child_module = f"{base_module}.{alias.name}" if base_module else alias.name
            if target_module == child_module:
                binding = _Binding(
                    kind=_BindingKind.IMPORT_MODULE,
                    target_module=target_module,
                    access_parts=(bound_name,),
                    conditional=bool(self.conditional_depth),
                )
            else:
                binding = _Binding(
                    kind=_BindingKind.IMPORT_SYMBOL,
                    target_module=target_module,
                    imported_name=alias.name,
                    conditional=bool(self.conditional_depth),
                )
            self._scope().bind(bound_name, binding)

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, (ast.Store, ast.Del)):
            self._scope().bind(
                node.id,
                _Binding(
                    kind=_BindingKind.SHADOW,
                    conditional=bool(self.conditional_depth),
                ),
            )

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        if node.name is not None:
            self._scope().bind(
                node.name,
                _Binding(kind=_BindingKind.SHADOW, conditional=True),
            )
        self.generic_visit(node)

    def visit_MatchAs(self, node: ast.MatchAs) -> None:
        if node.name is not None:
            self._scope().bind(
                node.name,
                _Binding(kind=_BindingKind.SHADOW, conditional=True),
            )
        self.generic_visit(node)

    def visit_MatchStar(self, node: ast.MatchStar) -> None:
        if node.name is not None:
            self._scope().bind(
                node.name,
                _Binding(kind=_BindingKind.SHADOW, conditional=True),
            )

    def visit_MatchMapping(self, node: ast.MatchMapping) -> None:
        if node.rest is not None:
            self._scope().bind(
                node.rest,
                _Binding(kind=_BindingKind.SHADOW, conditional=True),
            )
        self.generic_visit(node)

    def visit_Global(self, node: ast.Global) -> None:
        for name in node.names:
            self._scope().bind(
                name,
                _Binding(kind=_BindingKind.SHADOW, conditional=True),
            )

    def visit_Nonlocal(self, node: ast.Nonlocal) -> None:
        for name in node.names:
            self._scope().bind(
                name,
                _Binding(kind=_BindingKind.SHADOW, conditional=True),
            )

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
        self.conditional_depth += 1
        self.generic_visit(node)
        self.conditional_depth -= 1

    def _new_symbol(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef,
        *,
        kind: PythonSymbolKind,
        is_async: bool,
    ) -> PythonSymbol:
        if len(self.symbols) >= self.max_symbols:
            raise RepositoryCallGraphError("repository call graph exceeds its symbol limit")
        parent = self.symbols_by_id.get(self.current_scope or "")
        if parent is None:
            qualname = node.name
        elif parent.kind is PythonSymbolKind.CLASS:
            qualname = f"{parent.qualname}.{node.name}"
        else:
            qualname = f"{parent.qualname}.<locals>.{node.name}"
        symbol = PythonSymbol(
            symbol_id=_symbol_id(
                self.module,
                qualname,
                kind,
                node.lineno,
                node.col_offset,
            ),
            path=self.path,
            module=self.module,
            qualname=qualname,
            name=node.name,
            kind=kind,
            line=node.lineno,
            column=node.col_offset,
            end_line=node.end_lineno or node.lineno,
            is_async=is_async,
            parent_symbol_id=self.current_scope,
        )
        self.symbols.append(symbol)
        self.symbols_by_id[symbol.symbol_id] = symbol
        self.node_symbols[id(node)] = symbol.symbol_id
        return symbol

    def _child_lexical_parent(self) -> str | None:
        if self.current_scope is None:
            return None
        current = self.symbols_by_id[self.current_scope]
        if current.kind is PythonSymbolKind.CLASS:
            return self.scopes[self.current_scope].parent
        return self.current_scope

    def _bind_arguments(self, arguments: ast.arguments) -> None:
        values = [
            *arguments.posonlyargs,
            *arguments.args,
            *arguments.kwonlyargs,
        ]
        if arguments.vararg is not None:
            values.append(arguments.vararg)
        if arguments.kwarg is not None:
            values.append(arguments.kwarg)
        for argument in values:
            self._scope().bind(
                argument.arg,
                _Binding(kind=_BindingKind.SHADOW),
            )

    def _scope(self) -> _Scope:
        return self.scopes[self.current_scope]

    def lookup(self, scope_id: str | None, name: str) -> tuple[tuple[_Binding, ...], bool]:
        current = scope_id
        while True:
            scope = self.scopes[current]
            bindings = scope.bindings.get(name)
            if bindings:
                return tuple(sorted(bindings, key=_binding_key)), False
            if scope.wildcard_import:
                return (), True
            if current is None:
                return (), False
            current = scope.parent


class _SymbolIndex:
    def __init__(
        self,
        symbols: tuple[PythonSymbol, ...],
        analyzers: tuple[_SymbolAnalyzer, ...],
    ) -> None:
        self.by_id = {item.symbol_id: item for item in symbols}
        values: dict[tuple[str, str], list[str]] = defaultdict(list)
        for item in symbols:
            values[(item.module, item.qualname)].append(item.symbol_id)
        self.by_qualified_name = {
            key: tuple(sorted(symbol_ids)) for key, symbol_ids in values.items()
        }
        self.unsafe_qualified_names: set[tuple[str, str]] = set()
        for analyzer in analyzers:
            for scope_id, scope in analyzer.scopes.items():
                owner = analyzer.symbols_by_id.get(scope_id or "")
                if owner is not None and owner.kind is not PythonSymbolKind.CLASS:
                    continue
                prefix = f"{owner.qualname}." if owner is not None else ""
                for name, bindings in scope.bindings.items():
                    qualified_name = f"{prefix}{name}"
                    if (
                        len(bindings) > 1
                        or any(
                            binding.kind is _BindingKind.SHADOW or binding.conditional
                            for binding in bindings
                        )
                    ) and (
                        analyzer.module,
                        qualified_name,
                    ) in self.by_qualified_name:
                        self.unsafe_qualified_names.add((analyzer.module, qualified_name))

    def candidates(self, module: str, qualname: str) -> tuple[str, ...]:
        return self.by_qualified_name.get((module, qualname), ())

    def is_unsafe(self, module: str, qualname: str) -> bool:
        return (module, qualname) in self.unsafe_qualified_names

    def unsafe_bindings(self) -> tuple[PythonUnsafeSymbolBinding, ...]:
        return tuple(
            PythonUnsafeSymbolBinding(
                module=module,
                qualname=qualname,
                candidate_symbol_ids=self.candidates(module, qualname),
            )
            for module, qualname in sorted(self.unsafe_qualified_names)
        )


class _CallCollector(ast.NodeVisitor):
    def __init__(
        self,
        *,
        path: str,
        tree: ast.Module,
        analyzer: _SymbolAnalyzer,
        symbol_index: _SymbolIndex,
        max_expression_bytes: int,
        max_calls: int,
    ) -> None:
        self.path = path
        self.tree = tree
        self.analyzer = analyzer
        self.symbol_index = symbol_index
        self.max_expression_bytes = max_expression_bytes
        self.max_calls = max_calls
        self.current_scope: str | None = None
        self.unsupported_context = 0
        self.edges: list[PythonCallEdge] = []
        self.unresolved: list[PythonUnresolvedCall] = []

    def collect(self) -> tuple[tuple[PythonCallEdge, ...], tuple[PythonUnresolvedCall, ...]]:
        self.visit(self.tree)
        return tuple(self.edges), tuple(self.unresolved)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_function(node)

    def _visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        self.unsupported_context += 1
        for expression in _definition_outer_expressions(node):
            self.visit(expression)
        self.unsupported_context -= 1
        prior = self.current_scope
        self.current_scope = self.analyzer.node_symbols[id(node)]
        for statement in node.body:
            self.visit(statement)
        self.current_scope = prior

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.unsupported_context += 1
        for expression in [*node.decorator_list, *node.bases]:
            self.visit(expression)
        for keyword in node.keywords:
            self.visit(keyword.value)
        self.unsupported_context -= 1
        prior = self.current_scope
        self.current_scope = self.analyzer.node_symbols[id(node)]
        for statement in node.body:
            self.visit(statement)
        self.current_scope = prior

    def visit_Lambda(self, node: ast.Lambda) -> None:
        self.unsupported_context += 1
        self.visit(node.body)
        self.unsupported_context -= 1

    def visit_Call(self, node: ast.Call) -> None:
        if len(self.edges) + len(self.unresolved) >= self.max_calls:
            raise RepositoryCallGraphError("repository call graph exceeds its per-file call limit")
        expression = _callee_expression(node.func)
        if len(expression.encode("utf-8")) > self.max_expression_bytes:
            raise RepositoryCallGraphError(
                "repository call graph exceeds its call-expression limit"
            )
        if self.current_scope is None:
            self._add_unresolved(
                node,
                expression,
                UnresolvedCallReason.NO_ENCLOSING_SYMBOL,
            )
        elif self.unsupported_context:
            self._add_unresolved(
                node,
                expression,
                UnresolvedCallReason.UNSUPPORTED_CONTEXT,
            )
        else:
            target, resolution, reason, candidates = self._resolve(node.func)
            if target is not None and resolution is not None:
                self.edges.append(
                    PythonCallEdge(
                        source_path=self.path,
                        caller_symbol_id=self.current_scope,
                        target_symbol_id=target,
                        line=node.lineno,
                        column=node.col_offset,
                        expression=expression,
                        resolution=resolution,
                    )
                )
            else:
                self._add_unresolved(
                    node,
                    expression,
                    reason or UnresolvedCallReason.UNSUPPORTED_CALLEE,
                    candidates,
                )
        self.generic_visit(node)

    def _resolve(
        self,
        callee: ast.expr,
    ) -> tuple[
        str | None,
        PythonCallResolution | None,
        UnresolvedCallReason | None,
        tuple[str, ...],
    ]:
        if isinstance(callee, ast.Name):
            bindings, wildcard = self.analyzer.lookup(self.current_scope, callee.id)
            if not bindings:
                reason = (
                    UnresolvedCallReason.WILDCARD_IMPORT
                    if wildcard
                    else UnresolvedCallReason.UNRESOLVED_NAME
                )
                return None, None, reason, ()
            return self._resolve_name_bindings(bindings)
        parts = _attribute_parts(callee)
        if parts is None or len(parts) < 2:
            return None, None, UnresolvedCallReason.UNSUPPORTED_CALLEE, ()
        bindings, wildcard = self.analyzer.lookup(self.current_scope, parts[0])
        if not bindings:
            reason = (
                UnresolvedCallReason.WILDCARD_IMPORT
                if wildcard
                else UnresolvedCallReason.UNRESOLVED_NAME
            )
            return None, None, reason, ()
        return self._resolve_attribute_bindings(bindings, parts)

    def _resolve_name_bindings(
        self,
        bindings: tuple[_Binding, ...],
    ) -> tuple[
        str | None,
        PythonCallResolution | None,
        UnresolvedCallReason | None,
        tuple[str, ...],
    ]:
        if any(item.kind is _BindingKind.SHADOW for item in bindings):
            return None, None, UnresolvedCallReason.SHADOWED_NAME, ()
        if any(item.kind is _BindingKind.UNRESOLVED_IMPORT for item in bindings):
            return None, None, UnresolvedCallReason.UNRESOLVED_IMPORT, ()
        candidates: set[str] = set()
        resolutions: set[PythonCallResolution] = set()
        missing_imported = False
        unsafe = any(binding.conditional for binding in bindings)
        for binding in bindings:
            if binding.kind is _BindingKind.SYMBOL and binding.symbol_id is not None:
                candidates.add(binding.symbol_id)
                resolutions.add(PythonCallResolution.LEXICAL_SYMBOL)
            elif (
                binding.kind is _BindingKind.IMPORT_SYMBOL
                and binding.target_module is not None
                and binding.imported_name is not None
            ):
                resolved = self.symbol_index.candidates(
                    binding.target_module,
                    binding.imported_name,
                )
                candidates.update(resolved)
                resolutions.add(PythonCallResolution.IMPORTED_SYMBOL)
                missing_imported = missing_imported or not resolved
                unsafe = unsafe or self.symbol_index.is_unsafe(
                    binding.target_module,
                    binding.imported_name,
                )
            elif binding.kind is _BindingKind.IMPORT_MODULE:
                return None, None, UnresolvedCallReason.UNSUPPORTED_CALLEE, ()
        return _final_resolution(
            candidates,
            resolutions,
            missing_imported=missing_imported,
            unsafe=unsafe,
        )

    def _resolve_attribute_bindings(
        self,
        bindings: tuple[_Binding, ...],
        parts: tuple[str, ...],
    ) -> tuple[
        str | None,
        PythonCallResolution | None,
        UnresolvedCallReason | None,
        tuple[str, ...],
    ]:
        if any(item.kind is _BindingKind.UNRESOLVED_IMPORT for item in bindings):
            return None, None, UnresolvedCallReason.UNRESOLVED_IMPORT, ()
        if any(item.kind is _BindingKind.SHADOW for item in bindings):
            return None, None, UnresolvedCallReason.DYNAMIC_RECEIVER, ()
        candidates: set[str] = set()
        resolutions: set[PythonCallResolution] = set()
        missing_imported = False
        dynamic = False
        unsafe = any(binding.conditional for binding in bindings)
        for binding in bindings:
            if binding.kind is _BindingKind.IMPORT_MODULE and binding.target_module is not None:
                prefix = binding.access_parts
                if not prefix or parts[: len(prefix)] != prefix or len(parts) == len(prefix):
                    dynamic = True
                    continue
                qualname = ".".join(parts[len(prefix) :])
                resolved = self.symbol_index.candidates(binding.target_module, qualname)
                candidates.update(resolved)
                resolutions.add(PythonCallResolution.IMPORTED_MODULE_ATTRIBUTE)
                missing_imported = missing_imported or not resolved
                unsafe = unsafe or self.symbol_index.is_unsafe(
                    binding.target_module,
                    qualname,
                )
            elif binding.kind is _BindingKind.IMPORT_SYMBOL:
                if binding.target_module is None or binding.imported_name is None:
                    dynamic = True
                    continue
                base = self.symbol_index.candidates(
                    binding.target_module,
                    binding.imported_name,
                )
                class_bases = [
                    item
                    for item in base
                    if self.symbol_index.by_id[item].kind is PythonSymbolKind.CLASS
                ]
                if len(class_bases) != len(base) or not base:
                    dynamic = True
                    continue
                qualname = f"{binding.imported_name}.{'.'.join(parts[1:])}"
                resolved = self.symbol_index.candidates(binding.target_module, qualname)
                candidates.update(resolved)
                resolutions.add(PythonCallResolution.EXPLICIT_CLASS_ATTRIBUTE)
                missing_imported = missing_imported or not resolved
                unsafe = unsafe or self.symbol_index.is_unsafe(
                    binding.target_module,
                    binding.imported_name,
                )
                unsafe = unsafe or self.symbol_index.is_unsafe(
                    binding.target_module,
                    qualname,
                )
            elif binding.kind is _BindingKind.SYMBOL and binding.symbol_id is not None:
                base = self.symbol_index.by_id[binding.symbol_id]
                if base.kind is not PythonSymbolKind.CLASS:
                    dynamic = True
                    continue
                qualname = f"{base.qualname}.{'.'.join(parts[1:])}"
                resolved = self.symbol_index.candidates(base.module, qualname)
                candidates.update(resolved)
                resolutions.add(PythonCallResolution.EXPLICIT_CLASS_ATTRIBUTE)
                dynamic = dynamic or not resolved
                unsafe = unsafe or self.symbol_index.is_unsafe(base.module, qualname)
        if dynamic and candidates:
            return (
                None,
                None,
                UnresolvedCallReason.AMBIGUOUS_SYMBOL,
                tuple(sorted(candidates)),
            )
        if dynamic and not candidates and not missing_imported:
            return None, None, UnresolvedCallReason.DYNAMIC_RECEIVER, ()
        return _final_resolution(
            candidates,
            resolutions,
            missing_imported=missing_imported,
            unsafe=unsafe,
        )

    def _add_unresolved(
        self,
        node: ast.Call,
        expression: str,
        reason: UnresolvedCallReason,
        candidates: tuple[str, ...] = (),
    ) -> None:
        self.unresolved.append(
            PythonUnresolvedCall(
                source_path=self.path,
                caller_symbol_id=self.current_scope,
                line=node.lineno,
                column=node.col_offset,
                expression=expression,
                reason=reason,
                candidate_symbol_ids=tuple(sorted(set(candidates))),
            )
        )


def _final_resolution(
    candidates: set[str],
    resolutions: set[PythonCallResolution],
    *,
    missing_imported: bool,
    unsafe: bool,
) -> tuple[
    str | None,
    PythonCallResolution | None,
    UnresolvedCallReason | None,
    tuple[str, ...],
]:
    ordered = tuple(sorted(candidates))
    if unsafe or len(ordered) > 1 or len(resolutions) > 1:
        return None, None, UnresolvedCallReason.AMBIGUOUS_SYMBOL, ordered
    if len(ordered) == 1 and len(resolutions) == 1 and not missing_imported:
        return ordered[0], next(iter(resolutions)), None, ()
    if ordered:
        return None, None, UnresolvedCallReason.AMBIGUOUS_SYMBOL, ordered
    reason = (
        UnresolvedCallReason.MISSING_IMPORTED_SYMBOL
        if missing_imported
        else UnresolvedCallReason.UNRESOLVED_NAME
    )
    return None, None, reason, ()


def _definition_outer_expressions(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> tuple[ast.expr, ...]:
    expressions: list[ast.expr] = [*node.decorator_list]
    expressions.extend(node.args.defaults)
    expressions.extend(item for item in node.args.kw_defaults if item is not None)
    annotations = [
        item.annotation
        for item in [
            *node.args.posonlyargs,
            *node.args.args,
            *node.args.kwonlyargs,
        ]
        if item.annotation is not None
    ]
    if node.args.vararg is not None and node.args.vararg.annotation is not None:
        annotations.append(node.args.vararg.annotation)
    if node.args.kwarg is not None and node.args.kwarg.annotation is not None:
        annotations.append(node.args.kwarg.annotation)
    expressions.extend(annotations)
    if node.returns is not None:
        expressions.append(node.returns)
    return tuple(expressions)


def _absolute_from_module(
    *,
    path: str,
    module: str,
    module_text: str,
    level: int,
) -> str:
    if level == 0:
        return module_text
    package = module if path.endswith("/__init__.py") else module.rpartition(".")[0]
    parts = package.split(".") if package and package != "__root__" else []
    ascend = level - 1
    if not parts or ascend >= len(parts):
        return ""
    parts = parts[: len(parts) - ascend]
    if module_text:
        parts.extend(module_text.split("."))
    return ".".join(parts)


def _python_module(path: str) -> str:
    parts = path[:-3].split("/")
    if len(parts) > 1 and parts[0] == "src":
        parts = parts[1:]
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts) or "__root__"


def _symbol_id(
    module: str,
    qualname: str,
    kind: PythonSymbolKind,
    line: int,
    column: int,
) -> str:
    return f"python:{module}:{qualname}:{kind.value}:{line}:{column}"


def _callee_expression(node: ast.expr) -> str:
    parts = _attribute_parts(node)
    if parts is not None:
        return ".".join(parts)
    if isinstance(node, ast.Lambda):
        return "<Lambda>"
    return f"<{node.__class__.__name__}>"


def _attribute_parts(node: ast.expr) -> tuple[str, ...] | None:
    parts: list[str] = []
    current = node
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    if not isinstance(current, ast.Name):
        return None
    parts.append(current.id)
    return tuple(reversed(parts))


def _binding_key(
    binding: _Binding,
) -> tuple[str, str, str, str, tuple[str, ...], bool]:
    return (
        binding.kind.value,
        binding.symbol_id or "",
        binding.target_module or "",
        binding.imported_name or "",
        binding.access_parts,
        binding.conditional,
    )


def _symbol_index_hash(
    files: tuple[PythonCallGraphFile, ...],
    symbols: tuple[PythonSymbol, ...],
    unsafe_symbol_bindings: tuple[PythonUnsafeSymbolBinding, ...],
) -> str:
    payload = {
        "files": [
            {
                "path": item.path,
                "module": item.module,
                "parse_failure": (item.parse_failure.value if item.parse_failure else None),
            }
            for item in files
        ],
        "symbols": [
            {
                "symbol_id": item.symbol_id,
                "path": item.path,
                "module": item.module,
                "qualname": item.qualname,
                "kind": item.kind.value,
                "parent_symbol_id": item.parent_symbol_id,
            }
            for item in symbols
        ],
        "unsafe_symbol_bindings": [item.model_dump(mode="json") for item in unsafe_symbol_bindings],
    }
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _symbol_key(
    symbol: PythonSymbol,
) -> tuple[str, int, int, str, str]:
    return (
        symbol.path,
        symbol.line,
        symbol.column,
        symbol.kind.value,
        symbol.symbol_id,
    )


def _unsafe_binding_key(
    item: PythonUnsafeSymbolBinding,
) -> tuple[str, str, tuple[str, ...]]:
    return item.module, item.qualname, item.candidate_symbol_ids


def _edge_key(
    edge: PythonCallEdge,
) -> tuple[str, int, int, str, str, str, str]:
    return (
        edge.source_path,
        edge.line,
        edge.column,
        edge.caller_symbol_id,
        edge.target_symbol_id,
        edge.expression,
        edge.resolution.value,
    )


def _unresolved_key(
    item: PythonUnresolvedCall,
) -> tuple[str, int, int, str, str, str, tuple[str, ...]]:
    return (
        item.source_path,
        item.line,
        item.column,
        item.caller_symbol_id or "",
        item.expression,
        item.reason.value,
        item.candidate_symbol_ids,
    )


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
