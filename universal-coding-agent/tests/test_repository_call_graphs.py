from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from universal_coding_agent.product.call_graphs import (
    PythonCallResolution,
    PythonParseFailureReason,
    PythonSymbolKind,
    RepositoryCallGraphError,
    RepositoryCallGraphService,
    UnresolvedCallReason,
)
from universal_coding_agent.product.dependency_graphs import RepositoryDependencyService
from universal_coding_agent.product.repository_indexes import RepositoryIndexService
from universal_coding_agent.product.search_service import SearchService
from universal_coding_agent.product.workspace import ProductWorkspace
from universal_coding_agent.providers.fake import FakeModelProvider
from universal_coding_agent.storage.artifacts import ArtifactStore

PROJECT_ID = "project-alpha"
REPOSITORY_URL = "https://example.test/project-alpha.git"


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _write(root: Path, relative: str, content: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _commit(root: Path, message: str) -> str:
    _git(root, "add", "-A")
    _git(root, "commit", "-m", message)
    return _git(root, "rev-parse", "HEAD")


def _repository(tmp_path: Path, files: dict[str, str]) -> tuple[Path, str]:
    root = tmp_path / "source"
    root.mkdir(parents=True)
    _git(root, "init", "-b", "main")
    _git(root, "config", "user.email", "call-graph@example.test")
    _git(root, "config", "user.name", "Call Graph Test")
    for path, content in files.items():
        _write(root, path, content)
    return root, _commit(root, "initial call-graph fixture")


def _services(
    tmp_path: Path,
    **call_limits: int,
) -> tuple[
    ArtifactStore,
    SearchService,
    RepositoryIndexService,
    RepositoryDependencyService,
    RepositoryCallGraphService,
]:
    artifacts = ArtifactStore(tmp_path / "artifacts")
    search = SearchService(tmp_path / "search.sqlite")
    indexes = RepositoryIndexService(artifacts, search)
    dependencies = RepositoryDependencyService(artifacts, search, indexes)
    calls = RepositoryCallGraphService(
        artifacts,
        search,
        dependencies,
        **call_limits,
    )
    return artifacts, search, indexes, dependencies, calls


def _index(
    indexes: RepositoryIndexService,
    root: Path,
    base_sha: str,
    previous_sha256: str | None,
    *,
    project_id: str = PROJECT_ID,
    repository_url: str = REPOSITORY_URL,
):
    return indexes.index(
        project_id=project_id,
        root=root,
        repository_url=repository_url,
        base_ref="main",
        base_sha=base_sha,
        expected_previous_snapshot_sha256=previous_sha256,
    )


def _dependency_graph(
    dependencies: RepositoryDependencyService,
    snapshot_sha256: str,
    previous_graph_sha256: str | None,
    *,
    project_id: str = PROJECT_ID,
):
    return dependencies.build_graph(
        project_id=project_id,
        expected_repository_snapshot_sha256=snapshot_sha256,
        expected_previous_graph_sha256=previous_graph_sha256,
    )


def _call_graph(
    calls: RepositoryCallGraphService,
    root: Path,
    indexed,
    dependencies,
    previous=None,
    *,
    project_id: str = PROJECT_ID,
):
    return calls.build_graph(
        project_id=project_id,
        root=root,
        expected_repository_snapshot_ref=indexed.snapshot_ref,
        expected_repository_snapshot_sha256=indexed.snapshot_sha256,
        expected_dependency_graph_ref=dependencies.graph_ref,
        expected_dependency_graph_sha256=dependencies.graph_sha256,
        expected_previous_call_graph_ref=(previous.graph_ref if previous else None),
        expected_previous_call_graph_sha256=(previous.graph_sha256 if previous else None),
    )


def _symbol_map(graph) -> dict[tuple[str, str], list]:
    values: dict[tuple[str, str], list] = {}
    for symbol in graph.symbols:
        values.setdefault((symbol.module, symbol.qualname), []).append(symbol)
    return values


def _edge_names(graph) -> set[tuple[str, str, PythonCallResolution]]:
    symbols = {item.symbol_id: item for item in graph.symbols}
    return {
        (
            symbols[edge.caller_symbol_id].qualname,
            symbols[edge.target_symbol_id].qualname,
            edge.resolution,
        )
        for edge in graph.edges
    }


def test_extracts_canonical_symbols_and_only_unambiguous_static_calls(
    tmp_path: Path,
) -> None:
    root, base_sha = _repository(
        tmp_path,
        {
            "src/pkg/__init__.py": "",
            "src/pkg/core.py": (
                "def leaf():\n"
                "    return 1\n\n"
                "class Worker:\n"
                "    def run(self):\n"
                "        return leaf()\n\n"
                "    def dynamic(self):\n"
                "        return self.run()\n\n"
                "def outer():\n"
                "    def inner():\n"
                "        return leaf()\n"
                "    return inner()\n"
            ),
            "src/pkg/service.py": (
                "import pkg.core as core\n"
                "from pkg.core import leaf as imported_leaf\n"
                "from pkg.core import Worker\n\n"
                "def invoke(callback):\n"
                "    core.leaf()\n"
                "    imported_leaf()\n"
                "    Worker()\n"
                "    Worker.run(None)\n"
                "    callback()\n"
                "    unknown()\n\n"
                "core.leaf()\n"
            ),
        },
    )
    _artifacts, search, indexes, dependency_service, calls = _services(tmp_path / "state")
    try:
        indexed = _index(indexes, root, base_sha, None)
        dependencies = _dependency_graph(
            dependency_service,
            indexed.snapshot_sha256,
            None,
        )
        head_before = _git(root, "rev-parse", "HEAD")
        tree_before = _git(root, "rev-parse", "HEAD^{tree}")
        built = _call_graph(calls, root, indexed, dependencies)

        symbols = _symbol_map(built.graph)
        assert symbols[("pkg.core", "leaf")][0].kind is PythonSymbolKind.FUNCTION
        assert symbols[("pkg.core", "Worker")][0].kind is PythonSymbolKind.CLASS
        assert symbols[("pkg.core", "Worker.run")][0].kind is PythonSymbolKind.METHOD
        assert symbols[("pkg.core", "outer.<locals>.inner")][0].parent_symbol_id == (
            symbols[("pkg.core", "outer")][0].symbol_id
        )
        assert all(item.symbol_id.startswith("python:") for item in built.graph.symbols)

        edges = _edge_names(built.graph)
        assert (
            "Worker.run",
            "leaf",
            PythonCallResolution.LEXICAL_SYMBOL,
        ) in edges
        assert (
            "outer.<locals>.inner",
            "leaf",
            PythonCallResolution.LEXICAL_SYMBOL,
        ) in edges
        assert (
            "outer",
            "outer.<locals>.inner",
            PythonCallResolution.LEXICAL_SYMBOL,
        ) in edges
        assert (
            "invoke",
            "leaf",
            PythonCallResolution.IMPORTED_MODULE_ATTRIBUTE,
        ) in edges
        assert (
            "invoke",
            "leaf",
            PythonCallResolution.IMPORTED_SYMBOL,
        ) in edges
        assert (
            "invoke",
            "Worker",
            PythonCallResolution.IMPORTED_SYMBOL,
        ) in edges
        assert (
            "invoke",
            "Worker.run",
            PythonCallResolution.EXPLICIT_CLASS_ATTRIBUTE,
        ) in edges

        unresolved = {(item.expression, item.reason) for item in built.graph.unresolved_calls}
        assert ("self.run", UnresolvedCallReason.DYNAMIC_RECEIVER) in unresolved
        assert ("callback", UnresolvedCallReason.SHADOWED_NAME) in unresolved
        assert ("unknown", UnresolvedCallReason.UNRESOLVED_NAME) in unresolved
        assert ("core.leaf", UnresolvedCallReason.NO_ENCLOSING_SYMBOL) in unresolved
        assert _git(root, "rev-parse", "HEAD") == head_before
        assert _git(root, "rev-parse", "HEAD^{tree}") == tree_before
        assert _git(root, "status", "--porcelain") == ""
    finally:
        search.close()


def test_records_ambiguous_unresolved_and_parse_evidence_without_guessing(
    tmp_path: Path,
) -> None:
    root, base_sha = _repository(
        tmp_path,
        {
            "ambiguous.py": (
                "def duplicate():\n"
                "    return 1\n\n"
                "def duplicate():\n"
                "    return 2\n\n"
                "def caller():\n"
                "    duplicate()\n"
                "    callback = lambda: duplicate()\n"
                "    callback()\n"
                "    (lambda: None)()\n"
            ),
            "external.py": (
                "import external_sdk\n"
                "from missing_package import operation\n"
                "from plugin_api import *\n\n"
                "def invoke_external():\n"
                "    external_sdk.run()\n"
                "    operation()\n"
                "    wildcard_name()\n"
            ),
            "broken.py": "def broken(:\n",
        },
    )
    (root / "invalid_utf8.py").write_bytes(b"\xff\xfe")
    base_sha = _commit(root, "add invalid UTF-8 Python source")
    _artifacts, search, indexes, dependency_service, calls = _services(tmp_path / "state")
    try:
        indexed = _index(indexes, root, base_sha, None)
        dependencies = _dependency_graph(
            dependency_service,
            indexed.snapshot_sha256,
            None,
        )
        built = _call_graph(calls, root, indexed, dependencies)

        files = {item.path: item for item in built.graph.files}
        assert files["broken.py"].parse_failure is PythonParseFailureReason.SYNTAX_ERROR
        assert files["invalid_utf8.py"].parse_failure is (PythonParseFailureReason.INVALID_UTF8)
        reasons = {(item.expression, item.reason): item for item in built.graph.unresolved_calls}
        ambiguous = reasons[("duplicate", UnresolvedCallReason.AMBIGUOUS_SYMBOL)]
        assert len(ambiguous.candidate_symbol_ids) == 2
        assert ("duplicate", UnresolvedCallReason.UNSUPPORTED_CONTEXT) in reasons
        assert ("callback", UnresolvedCallReason.SHADOWED_NAME) in reasons
        assert ("<Lambda>", UnresolvedCallReason.UNSUPPORTED_CALLEE) in reasons
        assert ("external_sdk.run", UnresolvedCallReason.UNRESOLVED_IMPORT) in reasons
        assert ("operation", UnresolvedCallReason.UNRESOLVED_IMPORT) in reasons
        assert ("wildcard_name", UnresolvedCallReason.WILDCARD_IMPORT) in reasons
        ambiguous_targets = set(ambiguous.candidate_symbol_ids)
        assert not any(edge.target_symbol_id in ambiguous_targets for edge in built.graph.edges)
    finally:
        search.close()


def test_conditional_decorated_and_reassigned_bindings_never_emit_edges(
    tmp_path: Path,
) -> None:
    root, base_sha = _repository(
        tmp_path,
        {
            "targets.py": (
                "def safe():\n"
                "    return 1\n\n"
                "def replaced():\n"
                "    return 2\n"
                "replaced = object()\n\n"
                "class Worker:\n"
                "    def run(self):\n"
                "        return 3\n"
                "    run = object()\n"
            ),
            "consumer.py": (
                "from targets import safe, replaced, Worker\n"
                "if True:\n"
                "    from targets import safe as conditional_safe\n\n"
                "def caller():\n"
                "    safe()\n"
                "    replaced()\n"
                "    Worker.run(None)\n"
                "    conditional_safe()\n\n"
                "def outer():\n"
                "    @safe()\n"
                "    def decorated():\n"
                "        return 1\n"
                "    return decorated()\n"
            ),
        },
    )
    _artifacts, search, indexes, dependency_service, calls = _services(tmp_path / "state")
    try:
        indexed = _index(indexes, root, base_sha, None)
        dependencies = _dependency_graph(
            dependency_service,
            indexed.snapshot_sha256,
            None,
        )
        built = _call_graph(calls, root, indexed, dependencies)
        edges = _edge_names(built.graph)
        assert ("caller", "safe", PythonCallResolution.IMPORTED_SYMBOL) in edges
        assert not any(
            target in {"replaced", "Worker.run"} for _caller, target, _resolution in edges
        )
        assert not any(edge.expression == "conditional_safe" for edge in built.graph.edges)
        unsafe = {(item.module, item.qualname) for item in built.graph.unsafe_symbol_bindings}
        assert ("targets", "replaced") in unsafe
        assert ("targets", "Worker.run") in unsafe
        reasons = {(item.expression, item.reason) for item in built.graph.unresolved_calls}
        assert ("replaced", UnresolvedCallReason.AMBIGUOUS_SYMBOL) in reasons
        assert ("Worker.run", UnresolvedCallReason.AMBIGUOUS_SYMBOL) in reasons
        assert ("conditional_safe", UnresolvedCallReason.AMBIGUOUS_SYMBOL) in reasons
        assert ("safe", UnresolvedCallReason.UNSUPPORTED_CONTEXT) in reasons
    finally:
        search.close()


def test_incremental_reuse_matches_rebuild_and_tracks_complete_resolution_index(
    tmp_path: Path,
) -> None:
    root, first_sha = _repository(
        tmp_path,
        {
            "a.py": "def leaf():\n    return 1\n",
            "b.py": "import a\ndef invoke():\n    return a.leaf()\n",
        },
    )
    _artifacts, search, indexes, dependency_service, calls = _services(tmp_path / "state")
    try:
        first_index = _index(indexes, root, first_sha, None)
        first_dependency = _dependency_graph(
            dependency_service,
            first_index.snapshot_sha256,
            None,
        )
        first_call = _call_graph(calls, root, first_index, first_dependency)
        assert first_call.graph.delta.recomputed_paths == ("a.py", "b.py")

        _write(root, "b.py", "import a\ndef invoke():\n    result = a.leaf()\n    return result\n")
        second_sha = _commit(root, "modify a call body without changing symbols")
        second_index = _index(
            indexes,
            root,
            second_sha,
            first_index.snapshot_sha256,
        )
        second_dependency = _dependency_graph(
            dependency_service,
            second_index.snapshot_sha256,
            first_dependency.graph_sha256,
        )
        second_call = _call_graph(
            calls,
            root,
            second_index,
            second_dependency,
            first_call,
        )
        assert second_call.graph.delta.reused_paths == ("a.py",)
        assert second_call.graph.delta.recomputed_paths == ("b.py",)

        clean = calls._derive_graph(
            project_id=PROJECT_ID,
            root=root,
            snapshot=second_index.snapshot,
            snapshot_ref=second_index.snapshot_ref,
            snapshot_sha256=second_index.snapshot_sha256,
            dependency_graph=second_dependency.graph,
            dependency_graph_ref=second_dependency.graph_ref,
            dependency_graph_sha256=second_dependency.graph_sha256,
            policy_sha256=second_call.graph.policy_sha256,
            previous=None,
            previous_ref=None,
            previous_sha256=None,
        )
        assert second_call.graph.files == clean.files
        assert second_call.graph.symbols == clean.symbols
        assert second_call.graph.edges == clean.edges
        assert second_call.graph.unresolved_calls == clean.unresolved_calls

        _write(root, "a.py", "def leaf():\n    return 1\nleaf = object()\n")
        third_sha = _commit(root, "make an exported symbol unsafe")
        third_index = _index(
            indexes,
            root,
            third_sha,
            second_index.snapshot_sha256,
        )
        third_dependency = _dependency_graph(
            dependency_service,
            third_index.snapshot_sha256,
            second_dependency.graph_sha256,
        )
        third_call = _call_graph(
            calls,
            root,
            third_index,
            third_dependency,
            second_call,
        )
        assert third_call.graph.delta.reused_paths == ()
        assert third_call.graph.delta.recomputed_paths == ("a.py", "b.py")
        unsafe = {(item.module, item.qualname) for item in third_call.graph.unsafe_symbol_bindings}
        assert unsafe == {("a", "leaf")}
        assert not any(edge.expression == "a.leaf" for edge in third_call.graph.edges)
        assert any(
            item.expression == "a.leaf" and item.reason is UnresolvedCallReason.AMBIGUOUS_SYMBOL
            for item in third_call.graph.unresolved_calls
        )
    finally:
        search.close()


def test_exact_refs_hashes_policy_source_and_artifact_drift_fail_closed(
    tmp_path: Path,
) -> None:
    root, base_sha = _repository(
        tmp_path,
        {"a.py": "def leaf():\n    return 1\n"},
    )
    artifacts, search, indexes, dependency_service, calls = _services(tmp_path / "state")
    try:
        indexed = _index(indexes, root, base_sha, None)
        dependencies = _dependency_graph(
            dependency_service,
            indexed.snapshot_sha256,
            None,
        )
        built = _call_graph(calls, root, indexed, dependencies)
        state_before = search.repository_call_graph_state(calls.namespace(PROJECT_ID))

        with pytest.raises(RepositoryCallGraphError, match="snapshot reference"):
            calls.build_graph(
                project_id=PROJECT_ID,
                root=root,
                expected_repository_snapshot_ref=(indexed.snapshot_ref + "-different"),
                expected_repository_snapshot_sha256=indexed.snapshot_sha256,
                expected_dependency_graph_ref=dependencies.graph_ref,
                expected_dependency_graph_sha256=dependencies.graph_sha256,
                expected_previous_call_graph_ref=built.graph_ref,
                expected_previous_call_graph_sha256=built.graph_sha256,
            )
        with pytest.raises(RepositoryCallGraphError, match="dependency graph reference"):
            calls.build_graph(
                project_id=PROJECT_ID,
                root=root,
                expected_repository_snapshot_ref=indexed.snapshot_ref,
                expected_repository_snapshot_sha256=indexed.snapshot_sha256,
                expected_dependency_graph_ref=(dependencies.graph_ref + "-different"),
                expected_dependency_graph_sha256=dependencies.graph_sha256,
                expected_previous_call_graph_ref=built.graph_ref,
                expected_previous_call_graph_sha256=built.graph_sha256,
            )
        with pytest.raises(RepositoryCallGraphError, match="predecessor"):
            calls.build_graph(
                project_id=PROJECT_ID,
                root=root,
                expected_repository_snapshot_ref=indexed.snapshot_ref,
                expected_repository_snapshot_sha256=indexed.snapshot_sha256,
                expected_dependency_graph_ref=dependencies.graph_ref,
                expected_dependency_graph_sha256=dependencies.graph_sha256,
                expected_previous_call_graph_ref=built.graph_ref,
                expected_previous_call_graph_sha256="f" * 64,
            )
        changed_policy = RepositoryCallGraphService(
            artifacts,
            search,
            dependency_service,
            max_edges=249_999,
        )
        with pytest.raises(RepositoryCallGraphError, match="policy"):
            _call_graph(
                changed_policy,
                root,
                indexed,
                dependencies,
                built,
            )

        _write(root, "a.py", "def leaf():\n    return 2\n")
        with pytest.raises(RepositoryCallGraphError, match="not clean"):
            _call_graph(calls, root, indexed, dependencies, built)
        _git(root, "restore", "a.py")
        assert search.repository_call_graph_state(calls.namespace(PROJECT_ID)) == state_before

        graph_path = artifacts.root / built.graph_ref.removeprefix("artifact://")
        graph_path.write_text("{}", encoding="utf-8")
        with pytest.raises(RepositoryCallGraphError, match="integrity verification"):
            calls.verified_active_graph(
                project_id=PROJECT_ID,
                expected_graph_ref=built.graph_ref,
                expected_graph_sha256=built.graph_sha256,
            )
        assert search.repository_call_graph_state(calls.namespace(PROJECT_ID)) == state_before
    finally:
        search.close()


def test_state_transaction_rolls_back_and_exact_retry_succeeds(tmp_path: Path) -> None:
    root, base_sha = _repository(
        tmp_path,
        {"a.py": "def leaf():\n    return 1\n"},
    )
    _artifacts, search, indexes, dependency_service, calls = _services(tmp_path / "state")
    try:
        indexed = _index(indexes, root, base_sha, None)
        dependencies = _dependency_graph(
            dependency_service,
            indexed.snapshot_sha256,
            None,
        )
        search.connection.execute(
            """
            CREATE TRIGGER fail_call_graph_state
            BEFORE INSERT ON repository_call_graph_state
            BEGIN
                SELECT RAISE(ABORT, 'forced call graph failure');
            END
            """
        )
        with pytest.raises(RepositoryCallGraphError, match="transaction failed"):
            _call_graph(calls, root, indexed, dependencies)
        assert search.repository_call_graph_state(calls.namespace(PROJECT_ID)) is None

        search.connection.execute("DROP TRIGGER fail_call_graph_state")
        search.connection.commit()
        retried = _call_graph(calls, root, indexed, dependencies)
        state = search.repository_call_graph_state(calls.namespace(PROJECT_ID))
        assert state is not None
        assert state.graph_sha256 == retried.graph_sha256
        replayed = _call_graph(calls, root, indexed, dependencies, retried)
        assert replayed.replayed is True
        assert replayed.graph_ref == retried.graph_ref
        assert replayed.graph_sha256 == retried.graph_sha256
    finally:
        search.close()


def test_dependency_state_race_fails_before_call_graph_advancement(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, base_sha = _repository(
        tmp_path,
        {"a.py": "def leaf():\n    return 1\n"},
    )
    _artifacts, search, indexes, dependency_service, calls = _services(tmp_path / "state")
    try:
        indexed = _index(indexes, root, base_sha, None)
        dependencies = _dependency_graph(
            dependency_service,
            indexed.snapshot_sha256,
            None,
        )
        original_write = calls._write_graph

        def race_dependency_state(graph):
            result = original_write(graph)
            search.connection.execute(
                """
                UPDATE repository_dependency_graph_state
                SET graph_ref = ?
                WHERE namespace = ?
                """,
                (
                    "artifact://dependency-graphs/project-alpha/raced.json",
                    dependency_service.namespace(PROJECT_ID),
                ),
            )
            search.connection.commit()
            return result

        monkeypatch.setattr(calls, "_write_graph", race_dependency_state)
        with pytest.raises(RepositoryCallGraphError, match="dependency graph changed"):
            _call_graph(calls, root, indexed, dependencies)
        assert search.repository_call_graph_state(calls.namespace(PROJECT_ID)) is None
    finally:
        search.close()


@pytest.mark.parametrize(
    ("limits", "message"),
    [
        ({"max_source_bytes": 1}, "source-byte limit"),
        ({"max_symbols": 1}, "symbol limit"),
        ({"max_edges": 1}, "edge limit"),
        ({"max_unresolved": 1}, "unresolved-call limit"),
        ({"max_calls_per_file": 1}, "per-file call limit"),
        ({"graph_max_bytes": 1}, "byte limit"),
    ],
)
def test_independent_bounds_fail_before_active_state(
    tmp_path: Path,
    limits: dict[str, int],
    message: str,
) -> None:
    root, base_sha = _repository(
        tmp_path,
        {
            "a.py": (
                "def first():\n"
                "    return 1\n\n"
                "def second():\n"
                "    first()\n"
                "    missing_one()\n"
                "    missing_two()\n"
                "    return first()\n"
            )
        },
    )
    _artifacts, search, indexes, dependency_service, calls = _services(
        tmp_path / "state",
        **limits,
    )
    try:
        indexed = _index(indexes, root, base_sha, None)
        dependencies = _dependency_graph(
            dependency_service,
            indexed.snapshot_sha256,
            None,
        )
        with pytest.raises(RepositoryCallGraphError, match=message):
            _call_graph(calls, root, indexed, dependencies)
        assert search.repository_call_graph_state(calls.namespace(PROJECT_ID)) is None
    finally:
        search.close()


def test_workspace_restart_replay_project_isolation_and_clear_cascade(
    tmp_path: Path,
) -> None:
    alpha_root, alpha_sha = _repository(
        tmp_path / "alpha",
        {"alpha.py": "def alpha():\n    return 1\n"},
    )
    beta_root, beta_sha = _repository(
        tmp_path / "beta",
        {"beta.py": "def beta():\n    return 2\n"},
    )
    workspace_root = tmp_path / "workspace"
    workspace = ProductWorkspace.create(workspace_root, FakeModelProvider())
    try:
        alpha_index = _index(
            workspace.repository_indexes,
            alpha_root,
            alpha_sha,
            None,
        )
        alpha_dependency = _dependency_graph(
            workspace.dependency_graphs,
            alpha_index.snapshot_sha256,
            None,
        )
        alpha_call = _call_graph(
            workspace.call_graphs,
            alpha_root,
            alpha_index,
            alpha_dependency,
        )
        beta_index = _index(
            workspace.repository_indexes,
            beta_root,
            beta_sha,
            None,
            project_id="project-beta",
            repository_url="https://example.test/project-beta.git",
        )
        beta_dependency = _dependency_graph(
            workspace.dependency_graphs,
            beta_index.snapshot_sha256,
            None,
            project_id="project-beta",
        )
        beta_call = _call_graph(
            workspace.call_graphs,
            beta_root,
            beta_index,
            beta_dependency,
            project_id="project-beta",
        )
        assert alpha_call.graph.namespace != beta_call.graph.namespace
        assert alpha_call.graph.project_id == PROJECT_ID
        assert beta_call.graph.project_id == "project-beta"
    finally:
        workspace.close()

    reopened = ProductWorkspace.create(workspace_root, FakeModelProvider())
    try:
        replayed = _call_graph(
            reopened.call_graphs,
            alpha_root,
            alpha_index,
            alpha_dependency,
            alpha_call,
        )
        assert replayed.replayed is True
        assert replayed.graph_sha256 == alpha_call.graph_sha256
        reopened.search.clear_namespace(reopened.repository_indexes.namespace(PROJECT_ID))
        assert (
            reopened.search.repository_call_graph_state(reopened.call_graphs.namespace(PROJECT_ID))
            is None
        )
        assert (
            reopened.search.repository_dependency_graph_state(
                reopened.dependency_graphs.namespace(PROJECT_ID)
            )
            is None
        )
        assert (
            reopened.search.repository_call_graph_state(
                reopened.call_graphs.namespace("project-beta")
            )
            is not None
        )
    finally:
        reopened.close()
