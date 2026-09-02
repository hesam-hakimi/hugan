from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from universal_coding_agent.product.dependency_graphs import (
    DependencyImpactConfidence,
    RepositoryDependencyError,
    RepositoryDependencyService,
    UnresolvedImportReason,
)
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
    _git(root, "config", "user.email", "dependency@example.test")
    _git(root, "config", "user.name", "Dependency Test")
    for path, content in files.items():
        _write(root, path, content)
    return root, _commit(root, "initial dependency fixture")


def _services(
    tmp_path: Path,
    **dependency_limits: int,
) -> tuple[
    ArtifactStore,
    SearchService,
    RepositoryIndexService,
    RepositoryDependencyService,
]:
    artifacts = ArtifactStore(tmp_path / "artifacts")
    search = SearchService(tmp_path / "search.sqlite")
    indexes = RepositoryIndexService(artifacts, search)
    dependencies = RepositoryDependencyService(
        artifacts,
        search,
        indexes,
        **dependency_limits,
    )
    return artifacts, search, indexes, dependencies


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


def _build(
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


def test_graph_resolves_absolute_relative_and_src_layout_without_guessing(
    tmp_path: Path,
) -> None:
    root, base_sha = _repository(
        tmp_path,
        {
            "src/pkg/__init__.py": "",
            "src/pkg/core.py": "VALUE = 1\n",
            "src/pkg/service.py": (
                "from . import core\n"
                "from .core import VALUE\n"
                "import external_sdk\n"
            ),
            "tests/test_service.py": "from pkg import service\n",
            "dup.py": "VALUE = 1\n",
            "dup/__init__.py": "VALUE = 2\n",
            "uses_dup.py": "import dup\n",
            "src/pkg/outside.py": "from .. import impossible\n",
        },
    )
    _artifacts, search, indexes, dependencies = _services(tmp_path / "state")
    try:
        indexed = _index(indexes, root, base_sha, None)
        built = _build(dependencies, indexed.snapshot_sha256, None)

        nodes = {node.path: node for node in built.graph.nodes}
        assert nodes["src/pkg/core.py"].module == "pkg.core"
        assert nodes["src/pkg/service.py"].imports == (
            ".:core",
            ".core:VALUE",
            "external_sdk",
        )
        assert {
            (edge.source_path, edge.target_path, edge.raw_import)
            for edge in built.graph.edges
        } >= {
            ("src/pkg/service.py", "src/pkg/core.py", ".:core"),
            ("src/pkg/service.py", "src/pkg/core.py", ".core:VALUE"),
            ("tests/test_service.py", "src/pkg/service.py", "pkg:service"),
        }
        unresolved = {
            (item.source_path, item.raw_import): item
            for item in built.graph.unresolved_imports
        }
        assert unresolved[("uses_dup.py", "dup")].reason is (
            UnresolvedImportReason.AMBIGUOUS_MODULE
        )
        assert unresolved[("uses_dup.py", "dup")].candidate_paths == (
            "dup.py",
            "dup/__init__.py",
        )
        assert unresolved[("src/pkg/service.py", "external_sdk")].reason is (
            UnresolvedImportReason.MISSING_OR_EXTERNAL
        )
        assert unresolved[("src/pkg/outside.py", "..:impossible")].reason is (
            UnresolvedImportReason.RELATIVE_OUTSIDE_PACKAGE
        )
    finally:
        search.close()


def test_incremental_graph_reuses_only_safe_nodes_and_matches_full_resolution(
    tmp_path: Path,
) -> None:
    root, first_sha = _repository(
        tmp_path,
        {
            "a.py": "VALUE = 1\n",
            "b.py": "import a\nVALUE = a.VALUE\n",
            "tests/test_b.py": "import b\ndef test_b():\n    assert b.VALUE\n",
        },
    )
    _artifacts, search, indexes, dependencies = _services(tmp_path / "state")
    try:
        first_index = _index(indexes, root, first_sha, None)
        first_graph = _build(dependencies, first_index.snapshot_sha256, None)
        assert first_graph.graph.delta.recomputed_paths == (
            "a.py",
            "b.py",
            "tests/test_b.py",
        )

        _write(root, "b.py", "import a\nVALUE = a.VALUE\nCHANGED = True\n")
        second_sha = _commit(root, "modify one module")
        second_index = _index(
            indexes,
            root,
            second_sha,
            first_index.snapshot_sha256,
        )
        second_graph = _build(
            dependencies,
            second_index.snapshot_sha256,
            first_graph.graph_sha256,
        )
        assert second_graph.graph.delta.reused_paths == (
            "a.py",
            "tests/test_b.py",
        )
        assert second_graph.graph.delta.recomputed_paths == ("b.py",)

        full = dependencies._derive_graph(
            project_id=PROJECT_ID,
            snapshot_ref=second_index.snapshot_ref,
            snapshot=second_index.snapshot,
            snapshot_sha256=second_index.snapshot_sha256,
            policy_sha256=second_graph.graph.policy_sha256,
            previous=None,
            previous_ref=None,
            previous_sha256=None,
        )
        assert second_graph.graph.nodes == full.nodes
        assert second_graph.graph.edges == full.edges
        assert second_graph.graph.unresolved_imports == full.unresolved_imports

        _write(root, "c.py", "VALUE = 3\n")
        third_sha = _commit(root, "change module map")
        third_index = _index(
            indexes,
            root,
            third_sha,
            second_index.snapshot_sha256,
        )
        third_graph = _build(
            dependencies,
            third_index.snapshot_sha256,
            second_graph.graph_sha256,
        )
        assert third_graph.graph.delta.reused_paths == ()
        assert third_graph.graph.delta.recomputed_paths == (
            "a.py",
            "b.py",
            "c.py",
            "tests/test_b.py",
        )
    finally:
        search.close()


def test_modified_module_reports_transitive_sources_and_tests_through_cycle(
    tmp_path: Path,
) -> None:
    root, first_sha = _repository(
        tmp_path,
        {
            "core.py": "VALUE = 1\n",
            "a.py": "import b\nimport core\n",
            "b.py": "import a\n",
            "tests/test_cycle.py": "import b\ndef test_cycle():\n    assert b\n",
        },
    )
    _artifacts, search, indexes, dependencies = _services(tmp_path / "state")
    try:
        first_index = _index(indexes, root, first_sha, None)
        first_graph = _build(dependencies, first_index.snapshot_sha256, None)

        _write(root, "core.py", "VALUE = 2\n")
        second_sha = _commit(root, "modify dependency root")
        second_index = _index(
            indexes,
            root,
            second_sha,
            first_index.snapshot_sha256,
        )
        second_graph = _build(
            dependencies,
            second_index.snapshot_sha256,
            first_graph.graph_sha256,
        )
        result = dependencies.analyze_current_delta(
            project_id=PROJECT_ID,
            expected_repository_snapshot_sha256=second_index.snapshot_sha256,
            expected_graph_sha256=second_graph.graph_sha256,
        )

        sources = {item.path: item for item in result.report.impacted_sources}
        assert set(sources) == {"a.py", "b.py", "core.py"}
        assert sources["core.py"].depth == 0
        assert sources["core.py"].confidence is DependencyImpactConfidence.HIGH
        assert sources["a.py"].dependency_chain == ("core.py", "a.py")
        assert sources["b.py"].dependency_chain == ("core.py", "a.py", "b.py")
        assert sources["b.py"].confidence is DependencyImpactConfidence.MEDIUM
        assert len(result.report.impacted_tests) == 1
        impacted_test = result.report.impacted_tests[0]
        assert impacted_test.path == "tests/test_cycle.py"
        assert impacted_test.dependency_chain == (
            "core.py",
            "a.py",
            "b.py",
            "tests/test_cycle.py",
        )
    finally:
        search.close()


def test_deleted_module_uses_predecessor_graph_for_current_test_impact(
    tmp_path: Path,
) -> None:
    root, first_sha = _repository(
        tmp_path,
        {
            "old.py": "VALUE = 1\n",
            "consumer.py": "import old\nVALUE = old.VALUE\n",
            "tests/test_consumer.py": "import consumer\n",
        },
    )
    _artifacts, search, indexes, dependencies = _services(tmp_path / "state")
    try:
        first_index = _index(indexes, root, first_sha, None)
        first_graph = _build(dependencies, first_index.snapshot_sha256, None)

        _git(root, "rm", "old.py")
        second_sha = _commit(root, "delete imported module")
        second_index = _index(
            indexes,
            root,
            second_sha,
            first_index.snapshot_sha256,
        )
        second_graph = _build(
            dependencies,
            second_index.snapshot_sha256,
            first_graph.graph_sha256,
        )
        result = dependencies.analyze_current_delta(
            project_id=PROJECT_ID,
            expected_repository_snapshot_sha256=second_index.snapshot_sha256,
            expected_graph_sha256=second_graph.graph_sha256,
        )

        assert result.report.previous_graph_sha256 == first_graph.graph_sha256
        sources = {item.path: item for item in result.report.impacted_sources}
        assert sources["old.py"].present_in_current_snapshot is False
        assert sources["consumer.py"].dependency_chain == (
            "old.py",
            "consumer.py",
        )
        assert result.report.impacted_tests[0].dependency_chain == (
            "old.py",
            "consumer.py",
            "tests/test_consumer.py",
        )
        assert result.report.impacted_tests[0].present_in_current_snapshot is True
    finally:
        search.close()


def test_renamed_module_uses_predecessor_graph_for_current_test_impact(
    tmp_path: Path,
) -> None:
    root, first_sha = _repository(
        tmp_path,
        {
            "old.py": "VALUE = 1\n",
            "consumer.py": "import old\nVALUE = old.VALUE\n",
            "tests/test_consumer.py": "import consumer\n",
        },
    )
    _artifacts, search, indexes, dependencies = _services(tmp_path / "state")
    try:
        first_index = _index(indexes, root, first_sha, None)
        first_graph = _build(dependencies, first_index.snapshot_sha256, None)

        _git(root, "mv", "old.py", "new.py")
        second_sha = _commit(root, "rename imported module")
        second_index = _index(
            indexes,
            root,
            second_sha,
            first_index.snapshot_sha256,
        )
        assert tuple(
            (item.old_path, item.new_path)
            for item in second_index.snapshot.delta.renamed_paths
        ) == (("old.py", "new.py"),)
        second_graph = _build(
            dependencies,
            second_index.snapshot_sha256,
            first_graph.graph_sha256,
        )
        result = dependencies.analyze_current_delta(
            project_id=PROJECT_ID,
            expected_repository_snapshot_sha256=second_index.snapshot_sha256,
            expected_graph_sha256=second_graph.graph_sha256,
        )

        assert result.report.changed_paths == ("new.py", "old.py")
        assert result.report.previous_graph_sha256 == first_graph.graph_sha256
        impacted_test = result.report.impacted_tests[0]
        assert impacted_test.dependency_chain == (
            "old.py",
            "consumer.py",
            "tests/test_consumer.py",
        )
        assert impacted_test.present_in_current_snapshot is True
    finally:
        search.close()


def test_hash_policy_and_artifact_drift_fail_closed_without_state_change(
    tmp_path: Path,
) -> None:
    root, base_sha = _repository(tmp_path, {"a.py": "VALUE = 1\n"})
    artifacts, search, indexes, dependencies = _services(tmp_path / "state")
    try:
        indexed = _index(indexes, root, base_sha, None)
        built = _build(dependencies, indexed.snapshot_sha256, None)
        namespace = dependencies.namespace(PROJECT_ID)

        with pytest.raises(RepositoryDependencyError, match="snapshot hash"):
            _build(dependencies, "f" * 64, built.graph_sha256)
        with pytest.raises(RepositoryDependencyError, match="predecessor"):
            _build(dependencies, indexed.snapshot_sha256, "e" * 64)
        with pytest.raises(RepositoryDependencyError, match="graph hash"):
            dependencies.analyze_current_delta(
                project_id=PROJECT_ID,
                expected_repository_snapshot_sha256=indexed.snapshot_sha256,
                expected_graph_sha256="d" * 64,
            )

        changed_policy = RepositoryDependencyService(
            artifacts,
            search,
            indexes,
            max_edges=99_999,
        )
        with pytest.raises(RepositoryDependencyError, match="policy"):
            _build(changed_policy, indexed.snapshot_sha256, built.graph_sha256)

        graph_path = artifacts.root / built.graph_ref.removeprefix("artifact://")
        graph_path.write_text("{}", encoding="utf-8")
        with pytest.raises(RepositoryDependencyError, match="integrity verification"):
            dependencies.analyze_current_delta(
                project_id=PROJECT_ID,
                expected_repository_snapshot_sha256=indexed.snapshot_sha256,
                expected_graph_sha256=built.graph_sha256,
            )
        state = search.repository_dependency_graph_state(namespace)
        assert state is not None
        assert state.graph_sha256 == built.graph_sha256
    finally:
        search.close()


def test_snapshot_reference_drift_fails_closed_even_when_bytes_match(
    tmp_path: Path,
) -> None:
    root, base_sha = _repository(tmp_path, {"a.py": "VALUE = 1\n"})
    artifacts, search, indexes, dependencies = _services(tmp_path / "state")
    try:
        indexed = _index(indexes, root, base_sha, None)
        built = _build(dependencies, indexed.snapshot_sha256, None)
        alternate = artifacts.write_text(
            "repository-indexes/project-alpha/alternate/snapshot-copy.json",
            indexed.snapshot.canonical_content(),
            "application/json",
        )
        assert alternate.uri != indexed.snapshot_ref
        assert alternate.sha256 == indexed.snapshot_sha256
        search.connection.execute(
            "UPDATE repository_index_state SET snapshot_ref = ? WHERE namespace = ?",
            (alternate.uri, indexes.namespace(PROJECT_ID)),
        )
        search.connection.commit()

        with pytest.raises(RepositoryDependencyError, match="snapshot reference"):
            _build(dependencies, indexed.snapshot_sha256, built.graph_sha256)
        with pytest.raises(RepositoryDependencyError, match="active repository snapshot"):
            dependencies.analyze_current_delta(
                project_id=PROJECT_ID,
                expected_repository_snapshot_sha256=indexed.snapshot_sha256,
                expected_graph_sha256=built.graph_sha256,
            )
        state = search.repository_dependency_graph_state(
            dependencies.namespace(PROJECT_ID)
        )
        assert state is not None
        assert state.repository_snapshot_ref == indexed.snapshot_ref
        assert state.graph_sha256 == built.graph_sha256
    finally:
        search.close()


def test_graph_state_transaction_rolls_back_and_retry_succeeds(tmp_path: Path) -> None:
    root, first_sha = _repository(tmp_path, {"a.py": "VALUE = 1\n"})
    _artifacts, search, indexes, dependencies = _services(tmp_path / "state")
    try:
        first_index = _index(indexes, root, first_sha, None)
        first_graph = _build(dependencies, first_index.snapshot_sha256, None)

        _write(root, "a.py", "VALUE = 2\n")
        second_sha = _commit(root, "advance dependency graph")
        second_index = _index(
            indexes,
            root,
            second_sha,
            first_index.snapshot_sha256,
        )
        namespace = dependencies.namespace(PROJECT_ID)
        search.connection.execute(
            f"""
            CREATE TRIGGER reject_dependency_graph_state
            BEFORE INSERT ON repository_dependency_graph_state
            WHEN NEW.namespace = '{namespace}'
            BEGIN
                SELECT RAISE(ABORT, 'injected dependency-graph failure');
            END
            """
        )
        search.connection.commit()

        with pytest.raises(RepositoryDependencyError, match="transaction failed"):
            _build(
                dependencies,
                second_index.snapshot_sha256,
                first_graph.graph_sha256,
            )
        state = search.repository_dependency_graph_state(namespace)
        assert state is not None
        assert state.graph_sha256 == first_graph.graph_sha256

        search.connection.execute("DROP TRIGGER reject_dependency_graph_state")
        search.connection.commit()
        retried = _build(
            dependencies,
            second_index.snapshot_sha256,
            first_graph.graph_sha256,
        )
        assert retried.graph_sha256 != first_graph.graph_sha256
        assert search.repository_dependency_graph_state(namespace).graph_sha256 == (
            retried.graph_sha256
        )
    finally:
        search.close()


def test_workspace_restart_replays_exact_graph_and_preserves_project_isolation(
    tmp_path: Path,
) -> None:
    alpha_root, alpha_sha = _repository(tmp_path / "alpha", {"alpha.py": "VALUE = 1\n"})
    beta_root, beta_sha = _repository(tmp_path / "beta", {"beta.py": "VALUE = 2\n"})
    workspace_root = tmp_path / "workspace"
    workspace = ProductWorkspace.create(workspace_root, FakeModelProvider({}))
    try:
        alpha_index = _index(workspace.repository_indexes, alpha_root, alpha_sha, None)
        alpha_graph = _build(
            workspace.dependency_graphs,
            alpha_index.snapshot_sha256,
            None,
        )
        beta_index = _index(
            workspace.repository_indexes,
            beta_root,
            beta_sha,
            None,
            project_id="project-beta",
            repository_url="https://example.test/project-beta.git",
        )
        beta_graph = _build(
            workspace.dependency_graphs,
            beta_index.snapshot_sha256,
            None,
            project_id="project-beta",
        )
        assert alpha_graph.graph_ref != beta_graph.graph_ref
    finally:
        workspace.close()

    reopened = ProductWorkspace.create(workspace_root, FakeModelProvider({}))
    try:
        replay = _build(
            reopened.dependency_graphs,
            alpha_index.snapshot_sha256,
            alpha_graph.graph_sha256,
        )
        assert replay.replayed is True
        assert replay.graph_ref == alpha_graph.graph_ref
        beta_state = reopened.search.repository_dependency_graph_state(
            reopened.dependency_graphs.namespace("project-beta")
        )
        assert beta_state is not None
        assert beta_state.graph_sha256 == beta_graph.graph_sha256
        reopened.search.clear_namespace(
            reopened.dependency_graphs.namespace(PROJECT_ID)
        )
        assert reopened.search.repository_dependency_graph_state(
            reopened.dependency_graphs.namespace(PROJECT_ID)
        ) is None
        assert reopened.search.repository_dependency_graph_state(
            reopened.dependency_graphs.namespace("project-beta")
        ) == beta_state
        reopened.search.clear_namespace(
            reopened.repository_indexes.namespace("project-beta")
        )
        assert reopened.search.repository_dependency_graph_state(
            reopened.dependency_graphs.namespace("project-beta")
        ) is None
    finally:
        reopened.close()


def test_graph_and_impact_bounds_fail_before_exposing_new_active_evidence(
    tmp_path: Path,
) -> None:
    root, first_sha = _repository(
        tmp_path,
        {
            "core.py": "VALUE = 1\n",
            "a.py": "import core\n",
            "b.py": "import a\n",
        },
    )
    _artifacts, search, indexes, too_small = _services(
        tmp_path / "small-state",
        max_nodes=2,
    )
    try:
        indexed = _index(indexes, root, first_sha, None)
        with pytest.raises(RepositoryDependencyError, match="node limit"):
            _build(too_small, indexed.snapshot_sha256, None)
        assert search.repository_dependency_graph_state(
            too_small.namespace(PROJECT_ID)
        ) is None
    finally:
        search.close()

    _artifacts, search, indexes, shallow = _services(
        tmp_path / "shallow-state",
        max_impact_depth=1,
    )
    try:
        first_index = _index(indexes, root, first_sha, None)
        first_graph = _build(shallow, first_index.snapshot_sha256, None)
        _write(root, "core.py", "VALUE = 2\n")
        second_sha = _commit(root, "trigger bounded traversal")
        second_index = _index(
            indexes,
            root,
            second_sha,
            first_index.snapshot_sha256,
        )
        second_graph = _build(
            shallow,
            second_index.snapshot_sha256,
            first_graph.graph_sha256,
        )
        with pytest.raises(RepositoryDependencyError, match="depth limit"):
            shallow.analyze_current_delta(
                project_id=PROJECT_ID,
                expected_repository_snapshot_sha256=second_index.snapshot_sha256,
                expected_graph_sha256=second_graph.graph_sha256,
            )
    finally:
        search.close()


@pytest.mark.parametrize(
    ("dependency_limits", "files", "error"),
    (
        (
            {"max_edges": 1},
            {
                "a.py": "VALUE = 1\n",
                "b.py": "import a\n",
                "c.py": "import a\n",
            },
            "edge limit",
        ),
        (
            {"max_unresolved": 1},
            {"a.py": "import external_one\nimport external_two\n"},
            "unresolved-import limit",
        ),
        (
            {"graph_max_bytes": 100},
            {"a.py": "VALUE = 1\n"},
            "byte limit",
        ),
    ),
)
def test_each_remaining_graph_bound_fails_before_active_state(
    tmp_path: Path,
    dependency_limits: dict[str, int],
    files: dict[str, str],
    error: str,
) -> None:
    root, base_sha = _repository(tmp_path, files)
    _artifacts, search, indexes, dependencies = _services(
        tmp_path / "state",
        **dependency_limits,
    )
    try:
        indexed = _index(indexes, root, base_sha, None)
        with pytest.raises(RepositoryDependencyError, match=error):
            _build(dependencies, indexed.snapshot_sha256, None)
        assert search.repository_dependency_graph_state(
            dependencies.namespace(PROJECT_ID)
        ) is None
    finally:
        search.close()


@pytest.mark.parametrize(
    ("dependency_limits", "error"),
    (
        ({"max_impact_nodes": 1}, "traversal limit"),
        ({"impact_max_bytes": 100}, "byte limit"),
    ),
)
def test_each_remaining_impact_bound_preserves_active_graph_state(
    tmp_path: Path,
    dependency_limits: dict[str, int],
    error: str,
) -> None:
    root, first_sha = _repository(
        tmp_path,
        {
            "core.py": "VALUE = 1\n",
            "consumer.py": "import core\n",
        },
    )
    _artifacts, search, indexes, dependencies = _services(
        tmp_path / "state",
        **dependency_limits,
    )
    try:
        first_index = _index(indexes, root, first_sha, None)
        first_graph = _build(dependencies, first_index.snapshot_sha256, None)
        _write(root, "core.py", "VALUE = 2\n")
        second_sha = _commit(root, "trigger impact bound")
        second_index = _index(
            indexes,
            root,
            second_sha,
            first_index.snapshot_sha256,
        )
        second_graph = _build(
            dependencies,
            second_index.snapshot_sha256,
            first_graph.graph_sha256,
        )

        with pytest.raises(RepositoryDependencyError, match=error):
            dependencies.analyze_current_delta(
                project_id=PROJECT_ID,
                expected_repository_snapshot_sha256=second_index.snapshot_sha256,
                expected_graph_sha256=second_graph.graph_sha256,
            )
        state = search.repository_dependency_graph_state(
            dependencies.namespace(PROJECT_ID)
        )
        assert state is not None
        assert state.graph_sha256 == second_graph.graph_sha256
    finally:
        search.close()
