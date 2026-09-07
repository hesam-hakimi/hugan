from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from universal_coding_agent.product.ecmascript_dependencies import (
    ECMAScriptDependencyImpactItem,
    ECMAScriptImpactConfidence,
    ECMAScriptReferenceKind,
    ECMAScriptResolutionBasis,
    ECMAScriptUnresolvedReason,
    RepositoryECMAScriptDependencyError,
    RepositoryECMAScriptDependencyService,
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
    _git(root, "config", "user.email", "ecmascript-dependency@example.test")
    _git(root, "config", "user.name", "ECMAScript Dependency Test")
    for path, content in files.items():
        _write(root, path, content)
    return root, _commit(root, "initial ECMAScript dependency fixture")


def _services(
    tmp_path: Path,
    **dependency_limits: int,
) -> tuple[
    ArtifactStore,
    SearchService,
    RepositoryIndexService,
    RepositoryECMAScriptDependencyService,
]:
    artifacts = ArtifactStore(tmp_path / "artifacts")
    search = SearchService(tmp_path / "search.sqlite")
    indexes = RepositoryIndexService(artifacts, search)
    dependencies = RepositoryECMAScriptDependencyService(
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
    dependencies: RepositoryECMAScriptDependencyService,
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


def test_resolves_bounded_relative_candidates_and_records_typed_unresolved_evidence(
    tmp_path: Path,
) -> None:
    root, base_sha = _repository(
        tmp_path,
        {
            "src/app.ts": (
                'import "./exact.ts";\n'
                'import runtime from "./runtime.js";\n'
                'import declaration from "./declaration.js";\n'
                'import plain from "./plain";\n'
                'export * from "./folder";\n'
                'import legacy = require("./legacy.cjs");\n'
                'import react from "react";\n'
                'import remote from "https://example.test/remote.js";\n'
                'import "./styles.css";\n'
                'import "./missing";\n'
                'import "../../outside";\n'
            ),
            "src/exact.ts": "export const exact = true;\n",
            "src/runtime.ts": "export default true;\n",
            "src/declaration.d.ts": "declare const value: boolean; export default value;\n",
            "src/plain.js": "export default true;\n",
            "src/folder/index.ts": "export const folder = true;\n",
            "src/legacy.cts": "export = true;\n",
            "src/styles.css": "body {}\n",
        },
    )
    _artifacts, search, indexes, dependencies = _services(tmp_path / "state")
    try:
        indexed = _index(indexes, root, base_sha, None)
        built = _build(dependencies, indexed.snapshot_sha256, None)

        edges = {(edge.module_specifier, edge.target_path): edge for edge in built.graph.edges}
        assert edges[("./exact.ts", "src/exact.ts")].resolution_basis is (
            ECMAScriptResolutionBasis.EXACT_RELATIVE
        )
        assert edges[("./runtime.js", "src/runtime.ts")].resolution_basis is (
            ECMAScriptResolutionBasis.TYPESCRIPT_EXTENSION_SUBSTITUTION
        )
        assert edges[("./declaration.js", "src/declaration.d.ts")].resolution_basis is (
            ECMAScriptResolutionBasis.TYPESCRIPT_EXTENSION_SUBSTITUTION
        )
        assert edges[("./plain", "src/plain.js")].resolution_basis is (
            ECMAScriptResolutionBasis.UNIQUE_EXTENSION_CANDIDATE
        )
        folder = edges[("./folder", "src/folder/index.ts")]
        assert folder.reference_kind is ECMAScriptReferenceKind.ESM_EXPORT
        assert folder.resolution_basis is (
            ECMAScriptResolutionBasis.UNIQUE_DIRECTORY_INDEX_CANDIDATE
        )
        legacy = edges[("./legacy.cjs", "src/legacy.cts")]
        assert legacy.reference_kind is ECMAScriptReferenceKind.TYPESCRIPT_IMPORT_EQUALS
        assert legacy.resolution_basis is (
            ECMAScriptResolutionBasis.TYPESCRIPT_EXTENSION_SUBSTITUTION
        )

        unresolved = {item.module_specifier: item for item in built.graph.unresolved_references}
        assert unresolved["react"].reason is ECMAScriptUnresolvedReason.BARE_OR_EXTERNAL
        assert unresolved["https://example.test/remote.js"].reason is (
            ECMAScriptUnresolvedReason.ABSOLUTE_OR_URL
        )
        assert unresolved["./styles.css"].reason is (
            ECMAScriptUnresolvedReason.UNSUPPORTED_TARGET_TYPE
        )
        assert unresolved["./missing"].reason is ECMAScriptUnresolvedReason.MISSING_TARGET
        assert unresolved["../../outside"].reason is (
            ECMAScriptUnresolvedReason.RELATIVE_OUTSIDE_REPOSITORY
        )
        assert "src/styles.css" not in {node.path for node in built.graph.nodes}
    finally:
        search.close()


def test_ambiguous_and_configuration_dependent_targets_are_never_guessed(
    tmp_path: Path,
) -> None:
    root, base_sha = _repository(
        tmp_path,
        {
            "src/app.ts": (
                'import choice from "./choice";\n'
                'import runtime from "./runtime.js";\n'
                'import modern from "./modern";\n'
                'import invalid from "./choice.ts?raw";\n'
                'import alias from "@app/alias";\n'
            ),
            "src/browser.js": 'import value from "./typescript-only.js";\n',
            "src/choice.ts": "export default true;\n",
            "src/choice.js": "export default true;\n",
            "src/runtime.ts": "export default true;\n",
            "src/runtime.js": "export default true;\n",
            "src/modern.mts": "export default true;\n",
            "src/typescript-only.ts": "export default true;\n",
        },
    )
    _artifacts, search, indexes, dependencies = _services(tmp_path / "state")
    try:
        indexed = _index(indexes, root, base_sha, None)
        built = _build(dependencies, indexed.snapshot_sha256, None)
        unresolved = {
            (item.source_path, item.module_specifier): item
            for item in built.graph.unresolved_references
        }

        choice = unresolved[("src/app.ts", "./choice")]
        assert choice.reason is ECMAScriptUnresolvedReason.AMBIGUOUS_TARGET
        assert choice.candidate_paths == ("src/choice.js", "src/choice.ts")
        runtime = unresolved[("src/app.ts", "./runtime.js")]
        assert runtime.reason is ECMAScriptUnresolvedReason.AMBIGUOUS_TARGET
        assert runtime.candidate_paths == ("src/runtime.js", "src/runtime.ts")
        assert unresolved[("src/app.ts", "./modern")].reason is (
            ECMAScriptUnresolvedReason.MISSING_TARGET
        )
        assert unresolved[("src/app.ts", "./choice.ts?raw")].reason is (
            ECMAScriptUnresolvedReason.INVALID_REFERENCE
        )
        assert unresolved[("src/app.ts", "@app/alias")].reason is (
            ECMAScriptUnresolvedReason.BARE_OR_EXTERNAL
        )
        assert unresolved[("src/browser.js", "./typescript-only.js")].reason is (
            ECMAScriptUnresolvedReason.MISSING_TARGET
        )
    finally:
        search.close()


def test_incremental_graph_reuses_only_safe_nodes_and_matches_full_rebuild(
    tmp_path: Path,
) -> None:
    root, first_sha = _repository(
        tmp_path,
        {
            "src/dependency.ts": "export const value = 1;\n",
            "src/app.ts": 'import { value } from "./dependency";\n',
            "tests/app.test.ts": 'import "../src/app.ts";\n',
        },
    )
    _artifacts, search, indexes, dependencies = _services(tmp_path / "state")
    try:
        first_index = _index(indexes, root, first_sha, None)
        first_graph = _build(dependencies, first_index.snapshot_sha256, None)
        assert first_graph.graph.delta.recomputed_paths == (
            "src/app.ts",
            "src/dependency.ts",
            "tests/app.test.ts",
        )

        _write(
            root,
            "src/app.ts",
            'import { value } from "./dependency";\nexport const changed = value;\n',
        )
        second_sha = _commit(root, "modify one ECMAScript module")
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
            "src/dependency.ts",
            "tests/app.test.ts",
        )
        assert second_graph.graph.delta.recomputed_paths == ("src/app.ts",)

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
        assert second_graph.graph.unresolved_references == full.unresolved_references

        _write(root, "src/new-module.ts", "export const value = 2;\n")
        third_sha = _commit(root, "change ECMAScript candidate map")
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
            "src/app.ts",
            "src/dependency.ts",
            "src/new-module.ts",
            "tests/app.test.ts",
        )
    finally:
        search.close()


def test_modified_module_reports_cycle_safe_sources_and_current_tests_with_evidence(
    tmp_path: Path,
) -> None:
    root, first_sha = _repository(
        tmp_path,
        {
            "src/core.ts": 'import "./consumer.ts";\nexport const value = 1;\n',
            "src/service.ts": 'import { value } from "./core.ts";\n',
            "src/consumer.ts": 'import "./service";\n',
            "tests/consumer.test.ts": 'import "../src/consumer.ts";\n',
        },
    )
    _artifacts, search, indexes, dependencies = _services(tmp_path / "state")
    try:
        first_index = _index(indexes, root, first_sha, None)
        first_graph = _build(dependencies, first_index.snapshot_sha256, None)

        _write(
            root,
            "src/core.ts",
            'import "./consumer.ts";\nexport const value = 2;\n',
        )
        second_sha = _commit(root, "modify ECMAScript dependency root")
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
        assert set(sources) == {"src/consumer.ts", "src/core.ts", "src/service.ts"}
        assert sources["src/core.ts"].confidence is ECMAScriptImpactConfidence.HIGH
        assert sources["src/service.ts"].dependency_chain == (
            "src/core.ts",
            "src/service.ts",
        )
        assert sources["src/service.ts"].reference_chain == ("esm-import:./core.ts",)
        assert sources["src/service.ts"].resolution_chain == (
            ECMAScriptResolutionBasis.EXACT_RELATIVE,
        )
        consumer = sources["src/consumer.ts"]
        assert consumer.dependency_chain == (
            "src/core.ts",
            "src/service.ts",
            "src/consumer.ts",
        )
        assert consumer.confidence is ECMAScriptImpactConfidence.MEDIUM
        assert consumer.resolution_chain == (
            ECMAScriptResolutionBasis.EXACT_RELATIVE,
            ECMAScriptResolutionBasis.UNIQUE_EXTENSION_CANDIDATE,
        )
        assert result.report.impacted_tests[0].dependency_chain == (
            "src/core.ts",
            "src/service.ts",
            "src/consumer.ts",
            "tests/consumer.test.ts",
        )
        assert result.report.impacted_tests[0].present_in_current_snapshot is True
    finally:
        search.close()


def test_impact_item_rejects_confidence_that_does_not_match_its_evidence() -> None:
    with pytest.raises(ValueError, match="confidence does not match"):
        ECMAScriptDependencyImpactItem(
            path="src/consumer.ts",
            changed_path="src/core.ts",
            is_test=False,
            present_in_current_snapshot=True,
            depth=1,
            confidence=ECMAScriptImpactConfidence.MEDIUM,
            dependency_chain=("src/core.ts", "src/consumer.ts"),
            reference_chain=("esm-import:./core.ts",),
            resolution_chain=(ECMAScriptResolutionBasis.EXACT_RELATIVE,),
        )


def test_deleted_module_uses_verified_predecessor_graph_for_current_test_impact(
    tmp_path: Path,
) -> None:
    root, first_sha = _repository(
        tmp_path,
        {
            "src/old.ts": "export const value = 1;\n",
            "src/consumer.ts": 'import { value } from "./old.ts";\n',
            "tests/consumer.test.ts": 'import "../src/consumer.ts";\n',
        },
    )
    _artifacts, search, indexes, dependencies = _services(tmp_path / "state")
    try:
        first_index = _index(indexes, root, first_sha, None)
        first_graph = _build(dependencies, first_index.snapshot_sha256, None)
        _git(root, "rm", "src/old.ts")
        second_sha = _commit(root, "delete imported ECMAScript module")
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
        assert sources["src/old.ts"].present_in_current_snapshot is False
        assert sources["src/consumer.ts"].dependency_chain == (
            "src/old.ts",
            "src/consumer.ts",
        )
        assert result.report.impacted_tests[0].dependency_chain == (
            "src/old.ts",
            "src/consumer.ts",
            "tests/consumer.test.ts",
        )
    finally:
        search.close()


def test_renamed_module_retains_old_path_impact_and_new_path_delta_evidence(
    tmp_path: Path,
) -> None:
    root, first_sha = _repository(
        tmp_path,
        {
            "src/old.ts": "export const value = 1;\n",
            "src/consumer.ts": 'import { value } from "./old.ts";\n',
            "tests/consumer.test.ts": 'import "../src/consumer.ts";\n',
        },
    )
    _artifacts, search, indexes, dependencies = _services(tmp_path / "state")
    try:
        first_index = _index(indexes, root, first_sha, None)
        first_graph = _build(dependencies, first_index.snapshot_sha256, None)
        _git(root, "mv", "src/old.ts", "src/new.ts")
        second_sha = _commit(root, "rename imported ECMAScript module")
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

        assert result.report.changed_paths == ("src/new.ts", "src/old.ts")
        assert result.report.previous_graph_sha256 == first_graph.graph_sha256
        assert result.report.impacted_tests[0].dependency_chain == (
            "src/old.ts",
            "src/consumer.ts",
            "tests/consumer.test.ts",
        )
    finally:
        search.close()


def test_exact_graph_verification_rejects_reference_and_digest_drift(
    tmp_path: Path,
) -> None:
    root, base_sha = _repository(
        tmp_path,
        {
            "src/dependency.ts": "export const value = 1;\n",
            "src/app.ts": 'import "./dependency.ts";\n',
        },
    )
    _artifacts, search, indexes, dependencies = _services(tmp_path / "state")
    try:
        indexed = _index(indexes, root, base_sha, None)
        built = _build(dependencies, indexed.snapshot_sha256, None)
        repository_state, snapshot, graph_state, graph = dependencies.verified_active_graph(
            project_id=PROJECT_ID,
            expected_repository_snapshot_ref=indexed.snapshot_ref,
            expected_repository_snapshot_sha256=indexed.snapshot_sha256,
            expected_graph_ref=built.graph_ref,
            expected_graph_sha256=built.graph_sha256,
        )
        assert repository_state.snapshot_ref == indexed.snapshot_ref
        assert snapshot == indexed.snapshot
        assert graph_state.graph_ref == built.graph_ref
        assert graph == built.graph

        with pytest.raises(
            RepositoryECMAScriptDependencyError,
            match="reference or hash",
        ):
            dependencies.verified_active_graph(
                project_id=PROJECT_ID,
                expected_repository_snapshot_ref=indexed.snapshot_ref,
                expected_repository_snapshot_sha256=indexed.snapshot_sha256,
                expected_graph_ref=built.graph_ref,
                expected_graph_sha256="f" * 64,
            )
    finally:
        search.close()


def test_hash_policy_snapshot_reference_and_artifact_drift_fail_closed(
    tmp_path: Path,
) -> None:
    root, base_sha = _repository(tmp_path, {"src/app.ts": "export const value = 1;\n"})
    artifacts, search, indexes, dependencies = _services(tmp_path / "state")
    try:
        indexed = _index(indexes, root, base_sha, None)
        built = _build(dependencies, indexed.snapshot_sha256, None)
        namespace = dependencies.namespace(PROJECT_ID)

        with pytest.raises(RepositoryECMAScriptDependencyError, match="snapshot hash"):
            _build(dependencies, "f" * 64, built.graph_sha256)
        with pytest.raises(RepositoryECMAScriptDependencyError, match="predecessor"):
            _build(dependencies, indexed.snapshot_sha256, "e" * 64)
        with pytest.raises(RepositoryECMAScriptDependencyError, match="graph hash"):
            dependencies.analyze_current_delta(
                project_id=PROJECT_ID,
                expected_repository_snapshot_sha256=indexed.snapshot_sha256,
                expected_graph_sha256="d" * 64,
            )

        changed_policy = RepositoryECMAScriptDependencyService(
            artifacts,
            search,
            indexes,
            max_edges=99_999,
        )
        with pytest.raises(RepositoryECMAScriptDependencyError, match="policy"):
            _build(changed_policy, indexed.snapshot_sha256, built.graph_sha256)

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
        with pytest.raises(RepositoryECMAScriptDependencyError, match="snapshot reference"):
            _build(dependencies, indexed.snapshot_sha256, built.graph_sha256)
        search.connection.execute(
            "UPDATE repository_index_state SET snapshot_ref = ? WHERE namespace = ?",
            (indexed.snapshot_ref, indexes.namespace(PROJECT_ID)),
        )
        search.connection.commit()

        graph_path = artifacts.root / built.graph_ref.removeprefix("artifact://")
        graph_path.write_text("{}", encoding="utf-8")
        with pytest.raises(
            RepositoryECMAScriptDependencyError,
            match="integrity verification",
        ):
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


def test_graph_state_transaction_rolls_back_and_exact_retry_succeeds(
    tmp_path: Path,
) -> None:
    root, first_sha = _repository(
        tmp_path,
        {"src/app.ts": "export const value = 1;\n"},
    )
    _artifacts, search, indexes, dependencies = _services(tmp_path / "state")
    try:
        first_index = _index(indexes, root, first_sha, None)
        first_graph = _build(dependencies, first_index.snapshot_sha256, None)
        _write(root, "src/app.ts", "export const value = 2;\n")
        second_sha = _commit(root, "advance ECMAScript graph")
        second_index = _index(
            indexes,
            root,
            second_sha,
            first_index.snapshot_sha256,
        )
        namespace = dependencies.namespace(PROJECT_ID)
        search.connection.execute(
            f"""
            CREATE TRIGGER reject_ecmascript_dependency_graph_state
            BEFORE INSERT ON repository_dependency_graph_state
            WHEN NEW.namespace = '{namespace}'
            BEGIN
                SELECT RAISE(ABORT, 'injected ECMAScript dependency-graph failure');
            END
            """
        )
        search.connection.commit()

        with pytest.raises(RepositoryECMAScriptDependencyError, match="transaction failed"):
            _build(
                dependencies,
                second_index.snapshot_sha256,
                first_graph.graph_sha256,
            )
        state = search.repository_dependency_graph_state(namespace)
        assert state is not None
        assert state.graph_sha256 == first_graph.graph_sha256

        search.connection.execute("DROP TRIGGER reject_ecmascript_dependency_graph_state")
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


def test_workspace_restart_replays_graph_and_preserves_language_and_project_isolation(
    tmp_path: Path,
) -> None:
    alpha_root, alpha_sha = _repository(
        tmp_path / "alpha",
        {
            "python_module.py": "VALUE = 1\n",
            "src/app.ts": "export const value = 1;\n",
        },
    )
    beta_root, beta_sha = _repository(
        tmp_path / "beta",
        {"src/app.js": "export const value = 2;\n"},
    )
    workspace_root = tmp_path / "workspace"
    workspace = ProductWorkspace.create(workspace_root, FakeModelProvider({}))
    try:
        alpha_index = _index(
            workspace.repository_indexes,
            alpha_root,
            alpha_sha,
            None,
        )
        alpha_ecmascript = _build(
            workspace.ecmascript_dependencies,
            alpha_index.snapshot_sha256,
            None,
        )
        alpha_python = workspace.dependency_graphs.build_graph(
            project_id=PROJECT_ID,
            expected_repository_snapshot_sha256=alpha_index.snapshot_sha256,
            expected_previous_graph_sha256=None,
        )
        beta_index = _index(
            workspace.repository_indexes,
            beta_root,
            beta_sha,
            None,
            project_id="project-beta",
            repository_url="https://example.test/project-beta.git",
        )
        beta_ecmascript = _build(
            workspace.ecmascript_dependencies,
            beta_index.snapshot_sha256,
            None,
            project_id="project-beta",
        )
        assert alpha_ecmascript.graph_ref != beta_ecmascript.graph_ref

        workspace.search.clear_namespace(workspace.ecmascript_dependencies.namespace(PROJECT_ID))
        assert (
            workspace.search.repository_dependency_graph_state(
                workspace.ecmascript_dependencies.namespace(PROJECT_ID)
            )
            is None
        )
        python_state = workspace.search.repository_dependency_graph_state(
            workspace.dependency_graphs.namespace(PROJECT_ID)
        )
        assert python_state is not None
        assert python_state.graph_sha256 == alpha_python.graph_sha256
        alpha_ecmascript = _build(
            workspace.ecmascript_dependencies,
            alpha_index.snapshot_sha256,
            None,
        )
    finally:
        workspace.close()

    reopened = ProductWorkspace.create(workspace_root, FakeModelProvider({}))
    try:
        replay = _build(
            reopened.ecmascript_dependencies,
            alpha_index.snapshot_sha256,
            alpha_ecmascript.graph_sha256,
        )
        assert replay.replayed is True
        assert replay.graph_ref == alpha_ecmascript.graph_ref
        beta_state = reopened.search.repository_dependency_graph_state(
            reopened.ecmascript_dependencies.namespace("project-beta")
        )
        assert beta_state is not None
        assert beta_state.graph_sha256 == beta_ecmascript.graph_sha256

        reopened.search.clear_namespace(reopened.repository_indexes.namespace(PROJECT_ID))
        assert (
            reopened.search.repository_dependency_graph_state(
                reopened.ecmascript_dependencies.namespace(PROJECT_ID)
            )
            is None
        )
        assert (
            reopened.search.repository_dependency_graph_state(
                reopened.dependency_graphs.namespace(PROJECT_ID)
            )
            is None
        )
        assert (
            reopened.search.repository_dependency_graph_state(
                reopened.ecmascript_dependencies.namespace("project-beta")
            )
            == beta_state
        )
    finally:
        reopened.close()


def test_public_export_and_workspace_composition_expose_the_same_service(tmp_path: Path) -> None:
    from universal_coding_agent.product import RepositoryECMAScriptDependencyService

    workspace = ProductWorkspace.create(tmp_path / "workspace", FakeModelProvider({}))
    try:
        assert isinstance(
            workspace.ecmascript_dependencies,
            RepositoryECMAScriptDependencyService,
        )
        assert workspace.ecmascript_dependencies.artifacts is workspace.artifacts
        assert workspace.ecmascript_dependencies.search is workspace.search
        assert workspace.ecmascript_dependencies.repository_indexes is workspace.repository_indexes
    finally:
        workspace.close()


@pytest.mark.parametrize(
    ("dependency_limits", "files", "error"),
    (
        (
            {"max_nodes": 1},
            {
                "src/a.ts": "export const a = 1;\n",
                "src/b.ts": "export const b = 2;\n",
            },
            "node limit",
        ),
        (
            {"max_edges": 1},
            {
                "src/a.ts": "export const a = 1;\n",
                "src/b.ts": 'import "./a.ts";\n',
                "src/c.ts": 'import "./a.ts";\n',
            },
            "edge limit",
        ),
        (
            {"max_unresolved": 1},
            {"src/app.ts": 'import "first";\nimport "second";\n'},
            "unresolved-reference limit",
        ),
        (
            {"graph_max_bytes": 100},
            {"src/app.ts": "export const value = 1;\n"},
            "byte limit",
        ),
    ),
)
def test_each_graph_bound_fails_before_exposing_active_state(
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
        with pytest.raises(RepositoryECMAScriptDependencyError, match=error):
            _build(dependencies, indexed.snapshot_sha256, None)
        assert search.repository_dependency_graph_state(dependencies.namespace(PROJECT_ID)) is None
    finally:
        search.close()


@pytest.mark.parametrize(
    ("dependency_limits", "error"),
    (
        ({"max_impact_depth": 1}, "depth limit"),
        ({"max_impact_nodes": 1}, "traversal limit"),
        ({"impact_max_bytes": 100}, "byte limit"),
    ),
)
def test_each_impact_bound_preserves_the_active_graph(
    tmp_path: Path,
    dependency_limits: dict[str, int],
    error: str,
) -> None:
    root, first_sha = _repository(
        tmp_path,
        {
            "src/core.ts": "export const value = 1;\n",
            "src/consumer.ts": 'import "./core.ts";\n',
            "src/transitive.ts": 'import "./consumer.ts";\n',
        },
    )
    _artifacts, search, indexes, dependencies = _services(
        tmp_path / "state",
        **dependency_limits,
    )
    try:
        first_index = _index(indexes, root, first_sha, None)
        first_graph = _build(dependencies, first_index.snapshot_sha256, None)
        _write(root, "src/core.ts", "export const value = 2;\n")
        second_sha = _commit(root, "trigger ECMAScript impact bound")
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

        with pytest.raises(RepositoryECMAScriptDependencyError, match=error):
            dependencies.analyze_current_delta(
                project_id=PROJECT_ID,
                expected_repository_snapshot_sha256=second_index.snapshot_sha256,
                expected_graph_sha256=second_graph.graph_sha256,
            )
        state = search.repository_dependency_graph_state(dependencies.namespace(PROJECT_ID))
        assert state is not None
        assert state.graph_sha256 == second_graph.graph_sha256
    finally:
        search.close()


def test_graph_and_impact_analysis_preserve_the_exact_source_repository(
    tmp_path: Path,
) -> None:
    root, first_sha = _repository(
        tmp_path,
        {
            "src/core.ts": "export const value = 1;\n",
            "tests/core.test.ts": 'import "../src/core.ts";\n',
        },
    )
    _artifacts, search, indexes, dependencies = _services(tmp_path / "state")
    try:
        first_index = _index(indexes, root, first_sha, None)
        first_graph = _build(dependencies, first_index.snapshot_sha256, None)
        assert _git(root, "rev-parse", "HEAD") == first_sha
        assert _git(root, "status", "--porcelain=v1") == ""

        _write(root, "src/core.ts", "export const value = 2;\n")
        second_sha = _commit(root, "advance immutable source fixture")
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
        dependencies.analyze_current_delta(
            project_id=PROJECT_ID,
            expected_repository_snapshot_sha256=second_index.snapshot_sha256,
            expected_graph_sha256=second_graph.graph_sha256,
        )
        assert _git(root, "rev-parse", "HEAD") == second_sha
        assert _git(root, "status", "--porcelain=v1") == ""
    finally:
        search.close()
