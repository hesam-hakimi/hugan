from __future__ import annotations

import os
import sqlite3
import stat
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from threading import Barrier, Event

import pytest

import universal_coding_agent.product.coverage_evidence as coverage_evidence_module
import universal_coding_agent.product.search_service as search_service_module
from universal_coding_agent.core.safe_models import SafeModePolicy, TestProfile
from universal_coding_agent.product.call_graphs import RepositoryCallGraphService
from universal_coding_agent.product.coverage_evidence import (
    CoverageLineRange,
    CoverageScopeFile,
    RepositoryCoverageEvidenceError,
    RepositoryCoverageEvidenceService,
    TrustedCoverageFile,
    TrustedCoverageProfile,
    TrustedCoverageRun,
    TrustedTestCoverage,
    trusted_test_policy_sha256,
    trusted_test_profile_sha256,
)
from universal_coding_agent.product.dependency_graphs import RepositoryDependencyService
from universal_coding_agent.product.dispatch_evidence import RepositoryDispatchEvidenceService
from universal_coding_agent.product.repository_indexes import RepositoryIndexService
from universal_coding_agent.product.search_service import (
    RepositoryCoverageEvidenceState,
    RepositoryCoverageEvidenceStateError,
    RepositoryDispatchEvidenceStateError,
    SearchService,
)
from universal_coding_agent.product.workspace import ProductWorkspace
from universal_coding_agent.providers.fake import FakeModelProvider
from universal_coding_agent.storage.artifacts import ArtifactStore

PROJECT_ID = "project-alpha"
REPOSITORY_URL = "https://example.test/project-alpha.git"


@dataclass
class _Services:
    artifacts: ArtifactStore
    search: SearchService
    indexes: RepositoryIndexService
    dependencies: RepositoryDependencyService
    calls: RepositoryCallGraphService
    dispatch: RepositoryDispatchEvidenceService
    coverage: RepositoryCoverageEvidenceService


@dataclass
class _Upstreams:
    index: object
    dependency: object
    call: object
    dispatch: object


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True, text=True
    ).stdout.strip()


def _write(root: Path, relative: str, content: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _commit(root: Path, message: str, *, allow_empty: bool = False) -> str:
    _git(root, "add", "-A")
    args = ["commit", "-m", message]
    if allow_empty:
        args.append("--allow-empty")
    _git(root, *args)
    return _git(root, "rev-parse", "HEAD")


def _repository(
    tmp_path: Path,
    *,
    name: str = "source",
) -> tuple[Path, str]:
    root = tmp_path / name
    root.mkdir(parents=True)
    _git(root, "init", "-b", "main")
    _git(root, "config", "user.email", "coverage@example.test")
    _git(root, "config", "user.name", "Coverage Test")
    _write(root, "src/pkg/__init__.py", "")
    _write(
        root,
        "src/pkg/core.py",
        "def leaf(value: int):\n"
        "    return value + 1\n"
        "\n"
        "class Worker:\n"
        "    def run(self):\n"
        "        return leaf(1)\n",
    )
    _write(
        root,
        "tests/test_core.py",
        "from pkg.core import Worker, leaf\n"
        "\n"
        "def test_leaf():\n"
        "    assert leaf(1) == 2\n"
        "\n"
        "def test_worker():\n"
        "    assert Worker().run() == 2\n",
    )
    _write(root, "notes.txt", "tracked non-Python evidence\n")
    return root, _commit(root, "initial coverage fixture")


def _services(state_root: Path, **coverage_limits: int) -> _Services:
    artifacts = ArtifactStore(state_root / "artifacts")
    search = SearchService(state_root / "search.sqlite")
    indexes = RepositoryIndexService(artifacts, search)
    dependencies = RepositoryDependencyService(artifacts, search, indexes)
    calls = RepositoryCallGraphService(artifacts, search, dependencies)
    dispatch = RepositoryDispatchEvidenceService(artifacts, search, calls)
    coverage = RepositoryCoverageEvidenceService(
        artifacts,
        search,
        dispatch,
        **coverage_limits,
    )
    return _Services(
        artifacts=artifacts,
        search=search,
        indexes=indexes,
        dependencies=dependencies,
        calls=calls,
        dispatch=dispatch,
        coverage=coverage,
    )


def _build_upstreams(
    root: Path,
    base_sha: str,
    services: _Services,
    *,
    project_id: str = PROJECT_ID,
    repository_url: str = REPOSITORY_URL,
    previous: _Upstreams | None = None,
) -> _Upstreams:
    index = services.indexes.index(
        project_id=project_id,
        root=root,
        repository_url=repository_url,
        base_ref="main",
        base_sha=base_sha,
        expected_previous_snapshot_sha256=(
            previous.index.snapshot_sha256 if previous else None
        ),
    )
    dependency = services.dependencies.build_graph(
        project_id=project_id,
        expected_repository_snapshot_sha256=index.snapshot_sha256,
        expected_previous_graph_sha256=(
            previous.dependency.graph_sha256 if previous else None
        ),
    )
    call = services.calls.build_graph(
        project_id=project_id,
        root=root,
        expected_repository_snapshot_ref=index.snapshot_ref,
        expected_repository_snapshot_sha256=index.snapshot_sha256,
        expected_dependency_graph_ref=dependency.graph_ref,
        expected_dependency_graph_sha256=dependency.graph_sha256,
        expected_previous_call_graph_ref=(previous.call.graph_ref if previous else None),
        expected_previous_call_graph_sha256=(
            previous.call.graph_sha256 if previous else None
        ),
    )
    dispatch = services.dispatch.build_evidence(
        project_id=project_id,
        root=root,
        expected_call_graph_ref=call.graph_ref,
        expected_call_graph_sha256=call.graph_sha256,
        expected_previous_evidence_ref=(
            previous.dispatch.evidence_ref if previous else None
        ),
        expected_previous_evidence_sha256=(
            previous.dispatch.evidence_sha256 if previous else None
        ),
    )
    return _Upstreams(
        index=index,
        dependency=dependency,
        call=call,
        dispatch=dispatch,
    )


def _policy(*profile_ids: str) -> SafeModePolicy:
    selected = profile_ids or ("focused",)
    return SafeModePolicy(
        profiles=tuple(
            TestProfile(
                profile_id=profile_id,
                argv=("python", "-m", "pytest", "-q"),
                cwd=".",
                timeout_seconds=300,
                output_limit=20_000,
            )
            for profile_id in selected
        )
    )


def _coverage_file(snapshot, path: str, *ranges: tuple[int, int]) -> TrustedCoverageFile:
    source = next(item for item in snapshot.files if item.path == path)
    return TrustedCoverageFile(
        path=path,
        source_sha256=source.project_file.sha256,
        ranges=tuple(
            CoverageLineRange(start_line=start, end_line=end) for start, end in ranges
        ),
    )


def _scope_file(snapshot, path: str) -> CoverageScopeFile:
    source = next(item for item in snapshot.files if item.path == path)
    return CoverageScopeFile(path=path, source_sha256=source.project_file.sha256)


def _trusted_run(
    root: Path,
    upstreams: _Upstreams,
    policy: SafeModePolicy,
    *,
    project_id: str = PROJECT_ID,
    repository_url: str = REPOSITORY_URL,
    run_id: str = "coverage-run-001",
) -> TrustedCoverageRun:
    snapshot = upstreams.index.snapshot
    profile = policy.profiles[0]
    test_source = next(
        item for item in snapshot.files if item.path == "tests/test_core.py"
    )
    tree_oid = _git(root, "rev-parse", "HEAD^{tree}")
    tests = (
        TrustedTestCoverage(
            profile_id=profile.profile_id,
            test_id="tests/test_core.py::test_leaf",
            test_path="tests/test_core.py",
            test_source_sha256=test_source.project_file.sha256,
            covered_files=(
                _coverage_file(snapshot, "src/pkg/core.py", (1, 2)),
                _coverage_file(snapshot, "tests/test_core.py", (3, 4)),
            ),
        ),
        TrustedTestCoverage(
            profile_id=profile.profile_id,
            test_id="tests/test_core.py::test_worker",
            test_path="tests/test_core.py",
            test_source_sha256=test_source.project_file.sha256,
            covered_files=(
                _coverage_file(snapshot, "src/pkg/core.py", (4, 6)),
                _coverage_file(snapshot, "tests/test_core.py", (6, 7)),
            ),
        ),
    )
    return TrustedCoverageRun(
        run_id=run_id,
        project_id=project_id,
        repository_url=repository_url,
        base_ref="main",
        base_sha=snapshot.base_sha,
        source_tree_before_oid=tree_oid,
        source_tree_after_oid=tree_oid,
        repository_snapshot_ref=upstreams.index.snapshot_ref,
        repository_snapshot_sha256=upstreams.index.snapshot_sha256,
        dependency_graph_ref=upstreams.dependency.graph_ref,
        dependency_graph_sha256=upstreams.dependency.graph_sha256,
        call_graph_ref=upstreams.call.graph_ref,
        call_graph_sha256=upstreams.call.graph_sha256,
        dispatch_evidence_ref=upstreams.dispatch.evidence_ref,
        dispatch_evidence_sha256=upstreams.dispatch.evidence_sha256,
        trusted_test_policy_sha256=trusted_test_policy_sha256(policy),
        profiles=(
            TrustedCoverageProfile(
                profile_id=profile.profile_id,
                profile_sha256=trusted_test_profile_sha256(profile),
                passed=True,
                returncode=0,
                collection_complete=True,
                execution_complete=True,
                test_count=len(tests),
            ),
        ),
        coverage_scope=(
            _scope_file(snapshot, "src/pkg/core.py"),
            _scope_file(snapshot, "tests/test_core.py"),
        ),
        tests=tests,
        unattributed_files=(
            _coverage_file(snapshot, "src/pkg/core.py", (1, 1), (4, 4)),
        ),
    )


def _write_run(
    artifacts: ArtifactStore,
    run: TrustedCoverageRun,
) -> tuple[str, str]:
    digest = run.canonical_hash()
    reference = artifacts.write_text(
        f"trusted-coverage-runs/{run.project_id}/{run.base_sha}/run-{digest}.json",
        run.canonical_content(),
        "application/json",
    )
    assert reference.sha256 == digest
    return reference.uri, reference.sha256


def _record(
    services: _Services,
    root: Path,
    upstreams: _Upstreams,
    policy: SafeModePolicy,
    run_ref: str,
    run_sha256: str,
    previous=None,
    *,
    project_id: str = PROJECT_ID,
):
    return services.coverage.record_trusted_run(
        project_id=project_id,
        root=root,
        trusted_test_policy=policy,
        trusted_run_ref=run_ref,
        trusted_run_sha256=run_sha256,
        expected_dispatch_evidence_ref=upstreams.dispatch.evidence_ref,
        expected_dispatch_evidence_sha256=upstreams.dispatch.evidence_sha256,
        expected_previous_evidence_ref=(previous.evidence_ref if previous else None),
        expected_previous_evidence_sha256=(
            previous.evidence_sha256 if previous else None
        ),
    )


def test_search_schema_adds_coverage_tables_without_losing_existing_rows(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "legacy-search.sqlite"
    connection = sqlite3.connect(database_path)
    connection.execute(
        """
        CREATE TABLE search_records (
            record_id TEXT PRIMARY KEY,
            namespace TEXT NOT NULL,
            source_type TEXT NOT NULL,
            source_id TEXT NOT NULL,
            path TEXT NOT NULL,
            content TEXT NOT NULL,
            metadata_json TEXT NOT NULL
        )
        """
    )
    connection.execute(
        """
        INSERT INTO search_records (
            record_id, namespace, source_type, source_id,
            path, content, metadata_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "legacy-record",
            "project:legacy",
            "artifact",
            "legacy-source",
            "legacy.txt",
            "legacy content",
            "{}",
        ),
    )
    connection.commit()
    connection.close()

    search = SearchService(database_path)
    try:
        assert search.connection.execute(
            "SELECT COUNT(*) FROM search_records WHERE record_id = 'legacy-record'"
        ).fetchone()[0] == 1
        table_names = {
            row[0]
            for row in search.connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }
        assert "repository_coverage_evidence_state" in table_names
        assert "repository_coverage_run_ledger" in table_names
    finally:
        search.close()


def test_records_exact_host_attested_file_and_symbol_evidence(
    tmp_path: Path,
) -> None:
    root, base_sha = _repository(tmp_path)
    services = _services(tmp_path / "state")
    policy = _policy()
    try:
        head_before = _git(root, "rev-parse", "HEAD")
        tree_before = _git(root, "rev-parse", "HEAD^{tree}")
        upstreams = _build_upstreams(root, base_sha, services)
        run = _trusted_run(root, upstreams, policy)
        run_ref, run_sha256 = _write_run(services.artifacts, run)
        result = _record(
            services, root, upstreams, policy, run_ref, run_sha256
        )
        evidence = result.evidence
        assert evidence.trusted_run_ref == run_ref
        assert evidence.trusted_run_sha256 == run_sha256
        assert evidence.source_tree_oid == tree_before
        assert evidence.repository_snapshot_sha256 == upstreams.index.snapshot_sha256
        assert evidence.dependency_graph_sha256 == upstreams.dependency.graph_sha256
        assert evidence.call_graph_sha256 == upstreams.call.graph_sha256
        assert evidence.dispatch_evidence_sha256 == upstreams.dispatch.evidence_sha256
        assert evidence.tests[0].test_id.endswith("test_leaf")
        assert evidence.tests[1].test_id.endswith("test_worker")
        symbols = {item.symbol_id: item.qualname for item in upstreams.call.graph.symbols}
        leaf_file = evidence.tests[0].covered_files[0]
        worker_file = evidence.tests[1].covered_files[0]
        assert {symbols[item] for item in leaf_file.covered_symbol_ids} == {"leaf"}
        assert {symbols[item] for item in worker_file.covered_symbol_ids} == {
            "Worker",
            "Worker.run",
        }
        assert evidence.unattributed_files[0].ranges == run.unattributed_files[0].ranges
        assert result.evidence_ref != run_ref
        assert _git(root, "rev-parse", "HEAD") == head_before
        assert _git(root, "rev-parse", "HEAD^{tree}") == tree_before
        assert _git(root, "status", "--porcelain") == ""
        independent = _services(tmp_path / "independent-state")
        try:
            independent_upstreams = _build_upstreams(root, base_sha, independent)
            independent_run = _trusted_run(root, independent_upstreams, policy)
            independent_ref, independent_sha256 = _write_run(
                independent.artifacts, independent_run
            )
            independent_result = _record(
                independent,
                root,
                independent_upstreams,
                policy,
                independent_ref,
                independent_sha256,
            )
            assert independent_run == run
            assert independent_result.evidence == evidence
            assert independent_result.evidence_ref == result.evidence_ref
            assert independent_result.evidence_sha256 == result.evidence_sha256
        finally:
            independent.search.close()
    finally:
        services.search.close()


def test_failed_stale_or_incompatible_runs_fail_before_active_state(
    tmp_path: Path,
) -> None:
    root, base_sha = _repository(tmp_path)
    services = _services(tmp_path / "state")
    policy = _policy()
    try:
        upstreams = _build_upstreams(root, base_sha, services)
        baseline = _trusted_run(root, upstreams, policy)
        core_source = next(
            item
            for item in upstreams.index.snapshot.files
            if item.path == "src/pkg/core.py"
        )
        drifted_core_sha256 = "c" * 64
        drifted_source = baseline.model_copy(
            update={
                "coverage_scope": tuple(
                    item.model_copy(update={"source_sha256": drifted_core_sha256})
                    if item.path == "src/pkg/core.py"
                    else item
                    for item in baseline.coverage_scope
                ),
                "tests": tuple(
                    item.model_copy(
                        update={
                            "covered_files": tuple(
                                covered.model_copy(
                                    update={"source_sha256": drifted_core_sha256}
                                )
                                if covered.path == "src/pkg/core.py"
                                else covered
                                for covered in item.covered_files
                            )
                        }
                    )
                    for item in baseline.tests
                ),
                "unattributed_files": tuple(
                    item.model_copy(update={"source_sha256": drifted_core_sha256})
                    if item.path == "src/pkg/core.py"
                    else item
                    for item in baseline.unattributed_files
                ),
            }
        )
        mutations = (
            (
                baseline.model_copy(
                    update={
                        "profiles": (
                            baseline.profiles[0].model_copy(update={"passed": False}),
                        )
                    }
                ),
                "did not pass and complete",
            ),
            (
                baseline.model_copy(
                    update={"trusted_test_policy_sha256": "e" * 64}
                ),
                "test policy does not match",
            ),
            (
                baseline.model_copy(
                    update={
                        "profiles": (
                            baseline.profiles[0].model_copy(
                                update={"profile_sha256": "e" * 64}
                            ),
                        )
                    }
                ),
                "profile digest does not match",
            ),
            (
                baseline.model_copy(
                    update={
                        "profiles": (
                            baseline.profiles[0].model_copy(update={"returncode": 1}),
                        )
                    }
                ),
                "did not pass and complete",
            ),
            (
                baseline.model_copy(
                    update={
                        "profiles": (
                            baseline.profiles[0].model_copy(
                                update={"collection_complete": False}
                            ),
                        )
                    }
                ),
                "did not pass and complete",
            ),
            (
                baseline.model_copy(
                    update={
                        "profiles": (
                            baseline.profiles[0].model_copy(
                                update={"execution_complete": False}
                            ),
                        )
                    }
                ),
                "did not pass and complete",
            ),
            (
                baseline.model_copy(
                    update={"source_tree_after_oid": "f" * 40}
                ),
                "source tree does not match",
            ),
            (
                baseline.model_copy(
                    update={"dispatch_evidence_sha256": "d" * 64}
                ),
                "exact active upstream chain",
            ),
            (
                baseline.model_copy(
                    update={
                        "tests": (
                            baseline.tests[0].model_copy(
                                update={
                                    "test_id": "src/pkg/core.py::test_leaf",
                                    "test_path": "src/pkg/core.py",
                                    "test_source_sha256": core_source.project_file.sha256,
                                }
                            ),
                            baseline.tests[1],
                        )
                    }
                ),
                "tracked test file",
            ),
            (
                drifted_source,
                "scope does not match",
            ),
            (
                baseline.model_copy(
                    update={
                        "tests": (
                            baseline.tests[0].model_copy(
                                update={
                                    "covered_files": (
                                        baseline.tests[0].covered_files[0].model_copy(
                                            update={
                                                "ranges": (
                                                    CoverageLineRange(
                                                        start_line=999,
                                                        end_line=999,
                                                    ),
                                                )
                                            }
                                        ),
                                        baseline.tests[0].covered_files[1],
                                    )
                                }
                            ),
                            baseline.tests[1],
                        )
                    }
                ),
                "outside its source file",
            ),
            (
                baseline.model_copy(
                    update={
                        "tests": tuple(
                            item.model_copy(update={"covered_files": ()})
                            for item in baseline.tests
                        ),
                    }
                ),
                "no per-test line coverage evidence",
            ),
        )
        for run, message in mutations:
            run_ref, run_sha256 = _write_run(services.artifacts, run)
            with pytest.raises(RepositoryCoverageEvidenceError, match=message):
                _record(
                    services,
                    root,
                    upstreams,
                    policy,
                    run_ref,
                    run_sha256,
                )
            assert (
                services.search.repository_coverage_evidence_state(
                    services.coverage.namespace(PROJECT_ID)
                )
                is None
            )
    finally:
        services.search.close()


def test_missing_noncanonical_and_aggregate_only_receipts_fail_closed(
    tmp_path: Path,
) -> None:
    root, base_sha = _repository(tmp_path)
    services = _services(tmp_path / "state")
    policy = _policy()
    try:
        upstreams = _build_upstreams(root, base_sha, services)
        run = _trusted_run(root, upstreams, policy)
        run_ref, run_sha256 = _write_run(services.artifacts, run)
        with pytest.raises(RepositoryCoverageEvidenceError, match="integrity verification"):
            _record(
                services,
                root,
                upstreams,
                policy,
                "artifact://trusted-coverage-runs/missing.json",
                "a" * 64,
            )
        with pytest.raises(RepositoryCoverageEvidenceError, match="integrity verification"):
            _record(
                services,
                root,
                upstreams,
                policy,
                run_ref,
                "b" * 64,
            )
        aggregate = services.artifacts.write_json(
            "tasks/task-1/test-results.json",
            {
                "results": [
                    {
                        "profile_id": "focused",
                        "passed": True,
                        "returncode": 0,
                        "duration_ms": 1,
                        "output": "pass",
                    }
                ],
                "actual_changed_paths": [],
                "scope_intact": True,
            },
        )
        with pytest.raises(RepositoryCoverageEvidenceError, match="unexpected JSON field"):
            _record(
                services,
                root,
                upstreams,
                policy,
                aggregate.uri,
                aggregate.sha256,
            )
        noncanonical = services.artifacts.write_json(
            "trusted-coverage-runs/noncanonical.json",
            run.model_dump(mode="json"),
        )
        with pytest.raises(RepositoryCoverageEvidenceError, match="canonical hash"):
            _record(
                services,
                root,
                upstreams,
                policy,
                noncanonical.uri,
                noncanonical.sha256,
            )
    finally:
        services.search.close()


def test_base_and_source_tree_bindings_are_independent(tmp_path: Path) -> None:
    root, first_sha = _repository(tmp_path)
    services = _services(tmp_path / "state")
    policy = _policy()
    try:
        first = _build_upstreams(root, first_sha, services)
        first_tree = _git(root, "rev-parse", "HEAD^{tree}")
        second_sha = _commit(root, "same tree, new Base", allow_empty=True)
        assert _git(root, "rev-parse", "HEAD^{tree}") == first_tree
        second = _build_upstreams(
            root,
            second_sha,
            services,
            previous=first,
        )
        current = _trusted_run(root, second, policy)
        stale_base = current.model_copy(update={"base_sha": first_sha})
        stale_ref, stale_sha256 = _write_run(services.artifacts, stale_base)
        with pytest.raises(RepositoryCoverageEvidenceError, match="upstream chain"):
            _record(
                services,
                root,
                second,
                policy,
                stale_ref,
                stale_sha256,
            )
        stale_tree = current.model_copy(update={"source_tree_before_oid": "f" * 40})
        tree_ref, tree_sha256 = _write_run(services.artifacts, stale_tree)
        with pytest.raises(RepositoryCoverageEvidenceError, match="source tree"):
            _record(
                services,
                root,
                second,
                policy,
                tree_ref,
                tree_sha256,
            )
    finally:
        services.search.close()


@pytest.mark.parametrize(
    ("limits", "message"),
    [
        ({"run_max_bytes": 1}, "integrity verification"),
        ({"max_source_bytes": 1}, "source-byte limit"),
        ({"policy_max_bytes": 1}, "test policy exceeds its byte limit"),
        ({"profile_max_bytes": 1}, "test profile exceeds its byte limit"),
        ({"max_profiles": 1}, "test policy exceeds its profile limit"),
        ({"max_scope_files": 1}, "scope-file limit"),
        ({"max_tests": 1}, "test limit"),
        ({"max_files_per_test": 1}, "per-test file limit"),
        ({"max_file_observations": 1}, "file-observation limit"),
        ({"max_ranges_per_file": 1}, "per-file range limit"),
        ({"max_ranges": 1}, "line-range limit"),
        ({"max_covered_lines": 1}, "covered-line limit"),
        ({"max_symbol_bindings": 1}, "symbol-binding limit"),
        ({"max_symbol_evaluations": 1}, "symbol-evaluation limit"),
        ({"max_symbol_output_bytes": 1}, "symbol-output byte limit"),
        ({"max_test_id_bytes": 4}, "test-ID byte limit"),
        ({"evidence_max_bytes": 1}, "byte limit"),
    ],
)
def test_independent_bounds_fail_before_active_state(
    tmp_path: Path,
    limits: dict[str, int],
    message: str,
) -> None:
    root, base_sha = _repository(tmp_path)
    services = _services(tmp_path / "state", **limits)
    policy = (
        _policy("focused", "secondary") if "max_profiles" in limits else _policy()
    )
    try:
        upstreams = _build_upstreams(root, base_sha, services)
        run = _trusted_run(root, upstreams, policy)
        run_ref, run_sha256 = _write_run(services.artifacts, run)
        with pytest.raises(RepositoryCoverageEvidenceError, match=message):
            _record(
                services,
                root,
                upstreams,
                policy,
                run_ref,
                run_sha256,
            )
        assert (
            services.search.repository_coverage_evidence_state(
                services.coverage.namespace(PROJECT_ID)
            )
            is None
        )
    finally:
        services.search.close()


@pytest.mark.parametrize(
    "limit_name",
    [
        "run_max_bytes",
        "evidence_max_bytes",
        "max_source_bytes",
        "policy_max_bytes",
        "profile_max_bytes",
        "max_profiles",
        "max_scope_files",
        "max_tests",
        "max_files_per_test",
        "max_file_observations",
        "max_ranges_per_file",
        "max_ranges",
        "max_json_items",
        "max_json_depth",
        "max_covered_lines",
        "max_symbol_bindings",
        "max_symbol_evaluations",
        "max_symbol_output_bytes",
        "max_test_id_bytes",
        "git_timeout_seconds",
        "git_output_max_bytes",
    ],
)
def test_every_service_limit_changes_the_coverage_policy_digest(
    tmp_path: Path,
    limit_name: str,
) -> None:
    services = _services(tmp_path / "state")
    try:
        changed = RepositoryCoverageEvidenceService(
            services.artifacts,
            services.search,
            services.dispatch,
            **{limit_name: 1},
        )
        assert changed._policy_sha256() != services.coverage._policy_sha256()
    finally:
        services.search.close()


@pytest.mark.parametrize(
    ("limits", "message"),
    [
        ({"git_timeout_seconds": float("nan")}, "finite number"),
        ({"git_timeout_seconds": float("inf")}, "finite number"),
        ({"git_timeout_seconds": True}, "finite number"),
        ({"git_output_max_bytes": 1.5}, "must be integers"),
        ({"max_ranges": float("nan")}, "must be integers"),
        ({"max_tests": True}, "must be integers"),
    ],
)
def test_non_integral_or_non_finite_service_limits_are_rejected(
    tmp_path: Path,
    limits: dict[str, object],
    message: str,
) -> None:
    services = _services(tmp_path / "state")
    try:
        with pytest.raises(ValueError, match=message):
            RepositoryCoverageEvidenceService(
                services.artifacts,
                services.search,
                services.dispatch,
                **limits,
            )
    finally:
        services.search.close()


@pytest.mark.parametrize(
    ("limits", "content", "message"),
    [
        (
            {"max_ranges": 1},
            '{"unattributed_files":['
            '{"path":"a","source_sha256":"a","ranges":['
            '{"start_line":1,"end_line":1},'
            '{"start_line":3,"end_line":3}]}]}',
            "line-range limit",
        ),
        (
            {"max_json_items": 2},
            '{"tests":[],"profiles":[],"coverage_scope":[]}',
            "structural-item limit",
        ),
        (
            {"max_json_depth": 2},
            '{"unattributed_files":[{}]}',
            "JSON-depth limit",
        ),
        ({}, '{"tests":[{}]}', "missing a required JSON field"),
        ({}, '{"unexpected":0}', "unexpected JSON field"),
        ({}, '{"tests":[],"tests":[]}', "duplicate JSON field"),
    ],
)
def test_json_structure_limits_fail_before_model_allocation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    limits: dict[str, int],
    content: str,
    message: str,
) -> None:
    services = _services(tmp_path / "state", **limits)
    try:
        reference = services.artifacts.write_text(
            "trusted-coverage-runs/preflight.json",
            content,
            "application/json",
        )

        def unexpected_parse(cls, value):
            pytest.fail("Pydantic parsing ran before structural preflight")

        monkeypatch.setattr(
            TrustedCoverageRun,
            "model_validate_json",
            classmethod(unexpected_parse),
        )
        with pytest.raises(RepositoryCoverageEvidenceError, match=message):
            services.coverage._load_run(reference.uri, reference.sha256)
    finally:
        services.search.close()


@pytest.mark.parametrize(
    "content",
    [
        b"",
        b"one",
        b"one\n",
        b"one\r\ntwo\rthree",
        "one\u0085two\u2028three\u2029".encode(),
        b"\n" * 100_000,
    ],
)
def test_incremental_utf8_line_count_matches_python_splitlines(content: bytes) -> None:
    assert coverage_evidence_module._utf8_line_count(content) == len(
        content.decode("utf-8").splitlines()
    )


def test_incremental_utf8_line_count_rejects_invalid_text() -> None:
    with pytest.raises(UnicodeDecodeError):
        coverage_evidence_module._utf8_line_count(b"valid\n\xff")


@pytest.mark.parametrize(
    "failure", ["timeout", "stdout", "stderr", "combined", "descendant"]
)
def test_git_verification_is_bounded(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failure: str,
) -> None:
    services = _services(
        tmp_path / "state",
        git_timeout_seconds=1,
        git_output_max_bytes=1,
    )
    child_pid_path = tmp_path / "child.pid"
    try:
        fake_bin = tmp_path / "bin"
        fake_bin.mkdir()
        _write(
            fake_bin,
            "git",
            f"#!{sys.executable}\n"
            "import os\n"
            "from pathlib import Path\n"
            "import subprocess\n"
            "import sys\n"
            "import time\n"
            f"mode = {failure!r}\n"
            "if mode == 'timeout':\n"
            "    time.sleep(10)\n"
            "elif mode == 'descendant':\n"
            "    child = subprocess.Popen([sys.executable, '-c', "
            "'import time; time.sleep(10)'], stdout=sys.stdout, stderr=sys.stderr)\n"
            f"    Path({str(child_pid_path)!r}).write_text(str(child.pid))\n"
            "elif mode == 'combined':\n"
            "    os.write(1, b'x')\n"
            "    os.write(2, b'y')\n"
            "elif mode in {'stdout', 'stderr'}:\n"
            "    descriptor = 1 if mode == 'stdout' else 2\n"
            "    while True:\n"
            "        os.write(descriptor, b'x' * 65536)\n",
        )
        (fake_bin / "git").chmod(0o755)
        monkeypatch.setenv("PATH", f"{fake_bin}{os.pathsep}{os.environ['PATH']}")
        message = (
            "bounded Git verification failed"
            if failure in {"timeout", "descendant"}
            else "output limit"
        )
        started = time.monotonic()
        with pytest.raises(RepositoryCoverageEvidenceError, match=message):
            services.coverage._run_git(tmp_path, ("rev-parse", "HEAD"))
        assert time.monotonic() - started < 3
        if failure == "descendant" and os.name == "posix":
            child_pid = int(child_pid_path.read_text(encoding="utf-8"))
            live_deadline = time.monotonic() + 1
            while True:
                try:
                    status = Path(f"/proc/{child_pid}/stat").read_text(
                        encoding="ascii"
                    )
                except FileNotFoundError:
                    break
                if status.split()[2] == "Z":
                    break
                if time.monotonic() >= live_deadline:
                    pytest.fail("Git descendant remained live after bounded failure")
                time.sleep(0.01)
    finally:
        services.search.close()


def test_git_operation_deadline_fails_before_starting_another_process(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    services = _services(tmp_path / "state")
    try:
        monkeypatch.setattr(
            coverage_evidence_module.subprocess,
            "Popen",
            lambda *args, **kwargs: pytest.fail("expired Git operation started a process"),
        )
        with pytest.raises(RepositoryCoverageEvidenceError, match="operation deadline"):
            services.coverage._run_git(
                tmp_path,
                ("rev-parse", "HEAD"),
                deadline=time.monotonic() - 1,
            )
    finally:
        services.search.close()


def test_git_operation_deadline_includes_process_startup(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    services = _services(tmp_path / "state", git_timeout_seconds=5)
    real_popen = subprocess.Popen
    try:
        fake_bin = tmp_path / "bin"
        fake_bin.mkdir()
        _write(
            fake_bin,
            "git",
            f"#!{sys.executable}\n"
            "import time\n"
            "time.sleep(10)\n",
        )
        (fake_bin / "git").chmod(0o755)
        monkeypatch.setenv("PATH", f"{fake_bin}{os.pathsep}{os.environ['PATH']}")

        def delayed_process(*args, **kwargs):
            time.sleep(0.3)
            return real_popen(*args, **kwargs)

        monkeypatch.setattr(
            coverage_evidence_module.subprocess,
            "Popen",
            delayed_process,
        )
        started = time.monotonic()
        with pytest.raises(RepositoryCoverageEvidenceError, match="verification failed"):
            services.coverage._run_git(
                tmp_path,
                ("rev-parse", "HEAD"),
                deadline=started + 0.4,
            )
        assert time.monotonic() - started < 0.6
    finally:
        services.search.close()


def test_git_selector_failure_terminates_process_and_closes_pipes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    services = _services(tmp_path / "state")
    spawned: list[subprocess.Popen[bytes]] = []
    real_popen = subprocess.Popen
    try:
        fake_bin = tmp_path / "bin"
        fake_bin.mkdir()
        _write(
            fake_bin,
            "git",
            f"#!{sys.executable}\n"
            "import time\n"
            "time.sleep(10)\n",
        )
        (fake_bin / "git").chmod(0o755)
        monkeypatch.setenv("PATH", f"{fake_bin}{os.pathsep}{os.environ['PATH']}")

        def capture_process(*args, **kwargs):
            process = real_popen(*args, **kwargs)
            spawned.append(process)
            return process

        def fail_selector():
            raise OSError("selector allocation failed")

        monkeypatch.setattr(coverage_evidence_module.subprocess, "Popen", capture_process)
        monkeypatch.setattr(
            coverage_evidence_module.selectors,
            "DefaultSelector",
            fail_selector,
        )
        with pytest.raises(RepositoryCoverageEvidenceError, match="verification failed"):
            services.coverage._run_git(tmp_path, ("rev-parse", "HEAD"))
        assert len(spawned) == 1
        assert spawned[0].poll() is not None
        assert spawned[0].stdout is not None and spawned[0].stdout.closed
        assert spawned[0].stderr is not None and spawned[0].stderr.closed
    finally:
        for process in spawned:
            if process.poll() is None:
                process.kill()
                process.wait()
        services.search.close()


def test_git_verification_ignores_valid_fsmonitor_state_without_running_hook(
    tmp_path: Path,
) -> None:
    root, base_sha = _repository(tmp_path)
    services = _services(tmp_path / "state")
    policy = _policy()
    marker = tmp_path / "fsmonitor-ran"
    hook = tmp_path / "fsmonitor-hook"
    try:
        upstreams = _build_upstreams(root, base_sha, services)
        run = _trusted_run(root, upstreams, policy)
        run_ref, run_sha256 = _write_run(services.artifacts, run)
        _write(
            tmp_path,
            hook.name,
            f"#!{sys.executable}\n"
            "import sys\n"
            "from pathlib import Path\n"
            f"Path({str(marker)!r}).write_text('executed')\n"
            "sys.stdout.buffer.write(b'token\\0')\n",
        )
        hook.chmod(0o755)
        _git(root, "config", "core.fsmonitor", str(hook))
        _git(root, "update-index", "--fsmonitor")
        _git(root, "update-index", "--fsmonitor-valid", "src/pkg/core.py")
        assert _git(root, "ls-files", "-f", "--", "src/pkg/core.py").startswith("h ")
        marker.unlink(missing_ok=True)
        _record(
            services,
            root,
            upstreams,
            policy,
            run_ref,
            run_sha256,
        )
        assert not marker.exists()
    finally:
        services.search.close()


def test_git_verification_does_not_lazy_fetch_promised_objects(tmp_path: Path) -> None:
    source, _base_sha = _repository(tmp_path)
    origin = tmp_path / "origin.git"
    partial = tmp_path / "partial"
    subprocess.run(
        ["git", "clone", "--bare", str(source), str(origin)],
        check=True,
        capture_output=True,
    )
    _git(origin, "config", "uploadpack.allowFilter", "true")
    subprocess.run(
        [
            "git",
            "clone",
            "--filter=tree:0",
            "--no-checkout",
            origin.as_uri(),
            str(partial),
        ],
        check=True,
        capture_output=True,
    )
    missing_object = subprocess.run(
        ["git", "-C", str(partial), "cat-file", "-e", "HEAD^{tree}"],
        check=False,
        capture_output=True,
        env={**os.environ, "GIT_NO_LAZY_FETCH": "1"},
    )
    assert missing_object.returncode != 0

    marker = tmp_path / "lazy-fetch-ran"
    upload_pack = tmp_path / "upload-pack"
    _write(
        tmp_path,
        upload_pack.name,
        f"#!{sys.executable}\n"
        "from pathlib import Path\n"
        f"Path({str(marker)!r}).write_text('executed')\n",
    )
    upload_pack.chmod(0o755)
    _git(partial, "config", "remote.origin.uploadpack", str(upload_pack))
    services = _services(tmp_path / "state")
    try:
        with pytest.raises(RepositoryCoverageEvidenceError, match="verification failed"):
            services.coverage._run_git(partial, ("rev-parse", "HEAD^{tree}"))
        assert not marker.exists()
    finally:
        services.search.close()


def test_policy_source_run_and_evidence_drift_fail_closed(tmp_path: Path) -> None:
    root, base_sha = _repository(tmp_path)
    services = _services(tmp_path / "state")
    policy = _policy()
    try:
        upstreams = _build_upstreams(root, base_sha, services)
        run = _trusted_run(root, upstreams, policy)
        run_ref, run_sha256 = _write_run(services.artifacts, run)
        recorded = _record(
            services, root, upstreams, policy, run_ref, run_sha256
        )
        state, verified = services.coverage.verified_active_evidence(
            project_id=PROJECT_ID,
            trusted_test_policy=policy,
            expected_evidence_ref=recorded.evidence_ref,
            expected_evidence_sha256=recorded.evidence_sha256,
        )
        assert state.evidence_sha256 == verified.canonical_hash()
        with pytest.raises(RepositoryCoverageEvidenceError, match="reference or hash"):
            services.coverage.verified_active_evidence(
                project_id=PROJECT_ID,
                trusted_test_policy=policy,
                expected_evidence_ref=recorded.evidence_ref + "-different",
                expected_evidence_sha256=recorded.evidence_sha256,
            )
        changed_policy = _policy("different")
        with pytest.raises(RepositoryCoverageEvidenceError, match="test policy"):
            services.coverage.verified_active_evidence(
                project_id=PROJECT_ID,
                trusted_test_policy=changed_policy,
                expected_evidence_ref=recorded.evidence_ref,
                expected_evidence_sha256=recorded.evidence_sha256,
            )
        _write(root, "src/pkg/core.py", "def drifted():\n    return True\n")
        with pytest.raises(RepositoryCoverageEvidenceError, match="repository snapshot"):
            _record(
                services,
                root,
                upstreams,
                policy,
                run_ref,
                run_sha256,
                recorded,
            )
        _git(root, "restore", "src/pkg/core.py")
        run_path = services.artifacts.root / run_ref.removeprefix("artifact://")
        run_content = run_path.read_text(encoding="utf-8")
        run_path.write_text("{}", encoding="utf-8")
        with pytest.raises(RepositoryCoverageEvidenceError, match="integrity verification"):
            services.coverage.verified_active_evidence(
                project_id=PROJECT_ID,
                trusted_test_policy=policy,
                expected_evidence_ref=recorded.evidence_ref,
                expected_evidence_sha256=recorded.evidence_sha256,
            )
        run_path.write_text(run_content, encoding="utf-8")
        evidence_path = (
            services.artifacts.root
            / recorded.evidence_ref.removeprefix("artifact://")
        )
        evidence_path.write_text("{}", encoding="utf-8")
        with pytest.raises(RepositoryCoverageEvidenceError, match="integrity verification"):
            services.coverage.verified_active_evidence(
                project_id=PROJECT_ID,
                trusted_test_policy=policy,
                expected_evidence_ref=recorded.evidence_ref,
                expected_evidence_sha256=recorded.evidence_sha256,
            )
    finally:
        services.search.close()


def test_service_policy_drift_rejects_active_verification_and_exact_replay(
    tmp_path: Path,
) -> None:
    root, base_sha = _repository(tmp_path)
    services = _services(tmp_path / "state")
    policy = _policy()
    try:
        upstreams = _build_upstreams(root, base_sha, services)
        run = _trusted_run(root, upstreams, policy)
        run_ref, run_sha256 = _write_run(services.artifacts, run)
        recorded = _record(
            services,
            root,
            upstreams,
            policy,
            run_ref,
            run_sha256,
        )
        changed = RepositoryCoverageEvidenceService(
            services.artifacts,
            services.search,
            services.dispatch,
            max_json_items=(
                coverage_evidence_module.DEFAULT_COVERAGE_MAX_JSON_ITEMS - 1
            ),
        )
        with pytest.raises(RepositoryCoverageEvidenceError, match="policy does not match"):
            changed.verified_active_evidence(
                project_id=PROJECT_ID,
                trusted_test_policy=policy,
                expected_evidence_ref=recorded.evidence_ref,
                expected_evidence_sha256=recorded.evidence_sha256,
            )
        with pytest.raises(RepositoryCoverageEvidenceError, match="policy does not match"):
            changed.record_trusted_run(
                project_id=PROJECT_ID,
                root=root,
                trusted_test_policy=policy,
                trusted_run_ref=run_ref,
                trusted_run_sha256=run_sha256,
                expected_dispatch_evidence_ref=upstreams.dispatch.evidence_ref,
                expected_dispatch_evidence_sha256=upstreams.dispatch.evidence_sha256,
                expected_previous_evidence_ref=recorded.evidence_ref,
                expected_previous_evidence_sha256=recorded.evidence_sha256,
            )
    finally:
        services.search.close()


def test_out_of_scope_python_drift_is_bound_to_the_exact_base_blob(
    tmp_path: Path,
) -> None:
    root, base_sha = _repository(tmp_path)
    services = _services(tmp_path / "state")
    policy = _policy()
    path = "src/pkg/__init__.py"
    try:
        _git(root, "update-index", "--assume-unchanged", path)
        _write(root, path, "SIDE_EFFECT = True\n")
        assert _git(root, "status", "--porcelain") == ""
        upstreams = _build_upstreams(root, base_sha, services)
        run = _trusted_run(root, upstreams, policy)
        run_ref, run_sha256 = _write_run(services.artifacts, run)
        with pytest.raises(RepositoryCoverageEvidenceError, match="exact Base Git blob"):
            _record(
                services,
                root,
                upstreams,
                policy,
                run_ref,
                run_sha256,
            )
    finally:
        _git(root, "update-index", "--no-assume-unchanged", path)
        _git(root, "restore", path)
        services.search.close()


def test_denied_tracked_file_is_rejected_without_reading_it(
    tmp_path: Path,
) -> None:
    root, _base_sha = _repository(tmp_path)
    path = ".env"
    _write(root, path, "PLACEHOLDER=value\n")
    base_sha = _commit(root, "add denied tracked fixture")
    services = _services(tmp_path / "state")
    policy = _policy()
    try:
        upstreams = _build_upstreams(root, base_sha, services)
        assert all(item.path != path for item in upstreams.index.snapshot.files)
        run = _trusted_run(root, upstreams, policy)
        run_ref, run_sha256 = _write_run(services.artifacts, run)
        with pytest.raises(RepositoryCoverageEvidenceError, match="outside the active snapshot"):
            _record(
                services,
                root,
                upstreams,
                policy,
                run_ref,
                run_sha256,
            )
    finally:
        services.search.close()


def test_external_tracked_symlink_is_rejected_before_coverage_state(
    tmp_path: Path,
) -> None:
    root, _base_sha = _repository(tmp_path)
    external = tmp_path / "external.py"
    external.write_text("VALUE = 1\n", encoding="utf-8")
    (root / "external.py").symlink_to(external)
    base_sha = _commit(root, "add external symlink fixture")
    services = _services(tmp_path / "state")
    policy = _policy()
    try:
        upstreams = _build_upstreams(root, base_sha, services)
        assert all(
            item.path != "external.py" for item in upstreams.index.snapshot.files
        )
        run = _trusted_run(root, upstreams, policy)
        run_ref, run_sha256 = _write_run(services.artifacts, run)
        with pytest.raises(RepositoryCoverageEvidenceError, match="unsupported entry"):
            _record(
                services,
                root,
                upstreams,
                policy,
                run_ref,
                run_sha256,
            )
        assert (
            services.search.repository_coverage_evidence_state(
                services.coverage.namespace(PROJECT_ID)
            )
            is None
        )
    finally:
        services.search.close()


@pytest.mark.parametrize(
    ("index_flag", "clear_flag"),
    [
        ("--assume-unchanged", "--no-assume-unchanged"),
        ("--skip-worktree", "--no-skip-worktree"),
    ],
)
def test_unchanged_index_visibility_flags_are_rejected(
    tmp_path: Path,
    index_flag: str,
    clear_flag: str,
) -> None:
    root, base_sha = _repository(tmp_path)
    services = _services(tmp_path / "state")
    policy = _policy()
    path = "src/pkg/core.py"
    try:
        upstreams = _build_upstreams(root, base_sha, services)
        run = _trusted_run(root, upstreams, policy)
        run_ref, run_sha256 = _write_run(services.artifacts, run)
        _git(root, "update-index", index_flag, path)
        with pytest.raises(RepositoryCoverageEvidenceError, match="visibility flags"):
            _record(
                services,
                root,
                upstreams,
                policy,
                run_ref,
                run_sha256,
            )
    finally:
        _git(root, "update-index", clear_flag, path)
        services.search.close()


def test_index_identity_uses_one_combined_bounded_read(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, base_sha = _repository(tmp_path)
    services = _services(tmp_path / "state")
    calls: list[tuple[str, ...]] = []
    try:
        upstreams = _build_upstreams(root, base_sha, services)
        snapshot_files = {
            item.path: item for item in upstreams.index.snapshot.files
        }
        real_run_git = services.coverage._run_git

        def capture_run_git(root, arguments, **kwargs):
            calls.append(arguments)
            return real_run_git(root, arguments, **kwargs)

        monkeypatch.setattr(services.coverage, "_run_git", capture_run_git)
        services.coverage._verify_index_visibility(
            root,
            snapshot_files,
            deadline=time.monotonic() + 5,
        )
        assert calls == [("ls-files", "-v", "-s", "-z", "--")]
    finally:
        services.search.close()


@pytest.mark.parametrize(
    ("index_flag", "clear_flag"),
    [
        ("--assume-unchanged", "--no-assume-unchanged"),
        ("--skip-worktree", "--no-skip-worktree"),
    ],
)
def test_hidden_worktree_drift_cannot_escape_exact_base_blob_verification(
    tmp_path: Path,
    index_flag: str,
    clear_flag: str,
) -> None:
    root, base_sha = _repository(tmp_path)
    services = _services(tmp_path / "state")
    policy = _policy()
    path = "src/pkg/core.py"
    try:
        _git(root, "update-index", index_flag, path)
        _write(
            root,
            path,
            "def leaf(value: int):\n"
            "    return value + 2\n"
            "\n"
            "class Worker:\n"
            "    def run(self):\n"
            "        return leaf(1)\n",
        )
        assert _git(root, "status", "--porcelain") == ""
        upstreams = _build_upstreams(root, base_sha, services)
        run = _trusted_run(root, upstreams, policy)
        run_ref, run_sha256 = _write_run(services.artifacts, run)
        with pytest.raises(RepositoryCoverageEvidenceError, match="exact Base Git blob"):
            _record(
                services,
                root,
                upstreams,
                policy,
                run_ref,
                run_sha256,
            )
        assert (
            services.search.repository_coverage_evidence_state(
                services.coverage.namespace(PROJECT_ID)
            )
            is None
        )
    finally:
        _git(root, "update-index", clear_flag, path)
        _git(root, "restore", path)
        services.search.close()


def test_scope_only_file_is_bound_to_its_exact_base_blob(tmp_path: Path) -> None:
    root, base_sha = _repository(tmp_path)
    services = _services(tmp_path / "state")
    policy = _policy()
    path = "notes.txt"
    try:
        _git(root, "update-index", "--assume-unchanged", path)
        _write(root, path, "hidden scope-only drift\n")
        assert _git(root, "status", "--porcelain") == ""
        upstreams = _build_upstreams(root, base_sha, services)
        baseline = _trusted_run(root, upstreams, policy)
        run = baseline.model_copy(
            update={
                "coverage_scope": tuple(
                    sorted(
                        (*baseline.coverage_scope, _scope_file(upstreams.index.snapshot, path)),
                        key=lambda item: item.path,
                    )
                )
            }
        )
        run_ref, run_sha256 = _write_run(services.artifacts, run)
        with pytest.raises(RepositoryCoverageEvidenceError, match="exact Base Git blob"):
            _record(
                services,
                root,
                upstreams,
                policy,
                run_ref,
                run_sha256,
            )
    finally:
        _git(root, "update-index", "--no-assume-unchanged", path)
        _git(root, "restore", path)
        services.search.close()


def test_executable_mode_drift_cannot_hide_behind_core_filemode_false(
    tmp_path: Path,
) -> None:
    root, base_sha = _repository(tmp_path)
    services = _services(tmp_path / "state")
    policy = _policy()
    source_path = root / "src/pkg/core.py"
    original_mode = source_path.stat().st_mode
    try:
        _git(root, "config", "core.filemode", "false")
        source_path.chmod(original_mode | stat.S_IXUSR)
        assert _git(root, "status", "--porcelain") == ""
        upstreams = _build_upstreams(root, base_sha, services)
        run = _trusted_run(root, upstreams, policy)
        run_ref, run_sha256 = _write_run(services.artifacts, run)
        with pytest.raises(RepositoryCoverageEvidenceError, match="mode does not match"):
            _record(
                services,
                root,
                upstreams,
                policy,
                run_ref,
                run_sha256,
            )
    finally:
        source_path.chmod(original_mode)
        services.search.close()


def test_source_swap_to_symlink_during_verification_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, base_sha = _repository(tmp_path)
    services = _services(tmp_path / "state")
    policy = _policy()
    source_path = root / "src/pkg/core.py"
    outside_path = tmp_path / "outside-core.py"
    outside_path.write_bytes(source_path.read_bytes())
    try:
        upstreams = _build_upstreams(root, base_sha, services)
        run = _trusted_run(root, upstreams, policy)
        run_ref, run_sha256 = _write_run(services.artifacts, run)
        real_open = coverage_evidence_module.os.open
        swapped = False

        def swap_before_open(path, flags, *args, **kwargs):
            nonlocal swapped
            if not swapped and Path(path) == source_path:
                source_path.unlink()
                source_path.symlink_to(outside_path)
                swapped = True
            return real_open(path, flags, *args, **kwargs)

        monkeypatch.setattr(coverage_evidence_module.os, "open", swap_before_open)
        with pytest.raises(RepositoryCoverageEvidenceError, match="opened safely"):
            _record(
                services,
                root,
                upstreams,
                policy,
                run_ref,
                run_sha256,
            )
        assert swapped is True
    finally:
        if source_path.is_symlink():
            source_path.unlink()
        _git(root, "restore", "src/pkg/core.py")
        services.search.close()


def test_tracked_symlink_test_source_is_rejected(tmp_path: Path) -> None:
    root, _base_sha = _repository(tmp_path)
    _git(root, "rm", "tests/test_core.py")
    _write(
        root,
        "ignored/test_core_target.py",
        "from pkg.core import Worker, leaf\n"
        "\n"
        "def test_leaf():\n"
        "    assert leaf(1) == 2\n"
        "\n"
        "def test_worker():\n"
        "    assert Worker().run() == 2\n",
    )
    _write(root, ".gitignore", "ignored/\n")
    (root / "tests").mkdir(exist_ok=True)
    (root / "tests/test_core.py").symlink_to("../ignored/test_core_target.py")
    base_sha = _commit(root, "track test symlink")
    services = _services(tmp_path / "state")
    policy = _policy()
    try:
        upstreams = _build_upstreams(root, base_sha, services)
        run = _trusted_run(root, upstreams, policy)
        run_ref, run_sha256 = _write_run(services.artifacts, run)
        with pytest.raises(RepositoryCoverageEvidenceError, match="unsupported file mode"):
            _record(
                services,
                root,
                upstreams,
                policy,
                run_ref,
                run_sha256,
            )
    finally:
        services.search.close()


def test_test_run_identity_cannot_be_rebound_to_different_receipt(
    tmp_path: Path,
) -> None:
    root, base_sha = _repository(tmp_path)
    services = _services(tmp_path / "state")
    policy = _policy()
    try:
        upstreams = _build_upstreams(root, base_sha, services)
        first_run = _trusted_run(root, upstreams, policy)
        first_ref, first_sha256 = _write_run(services.artifacts, first_run)
        first = _record(
            services,
            root,
            upstreams,
            policy,
            first_ref,
            first_sha256,
        )
        conflicting_run = first_run.model_copy(
            update={
                "unattributed_files": (
                    _coverage_file(
                        upstreams.index.snapshot,
                        "src/pkg/core.py",
                        (2, 2),
                    ),
                )
            }
        )
        conflict_ref, conflict_sha256 = _write_run(
            services.artifacts, conflicting_run
        )
        with pytest.raises(RepositoryCoverageEvidenceError, match="identity conflicts"):
            _record(
                services,
                root,
                upstreams,
                policy,
                conflict_ref,
                conflict_sha256,
                first,
            )
        active = services.search.repository_coverage_evidence_state(
            services.coverage.namespace(PROJECT_ID)
        )
        assert active is not None
        assert active.evidence_sha256 == first.evidence_sha256
        services.search.clear_namespace(services.coverage.namespace(PROJECT_ID))
        assert (
            services.search.repository_coverage_evidence_state(
                services.coverage.namespace(PROJECT_ID)
            )
            is None
        )
        with pytest.raises(RepositoryCoverageEvidenceError, match="identity conflicts"):
            _record(
                services,
                root,
                upstreams,
                policy,
                conflict_ref,
                conflict_sha256,
            )
        restored = _record(
            services,
            root,
            upstreams,
            policy,
            first_ref,
            first_sha256,
        )
        assert restored.evidence_sha256 == first.evidence_sha256
    finally:
        services.search.close()


def test_state_transaction_rolls_back_and_exact_retry_succeeds(tmp_path: Path) -> None:
    root, base_sha = _repository(tmp_path)
    services = _services(tmp_path / "state")
    policy = _policy()
    try:
        upstreams = _build_upstreams(root, base_sha, services)
        first_run = _trusted_run(root, upstreams, policy, run_id="coverage-run-001")
        first_ref, first_sha256 = _write_run(services.artifacts, first_run)
        first = _record(
            services, root, upstreams, policy, first_ref, first_sha256
        )
        second_run = _trusted_run(root, upstreams, policy, run_id="coverage-run-002")
        second_ref, second_sha256 = _write_run(services.artifacts, second_run)
        services.search.connection.execute(
            """
            CREATE TRIGGER fail_coverage_state
            BEFORE INSERT ON repository_coverage_evidence_state
            BEGIN
                SELECT RAISE(ABORT, 'forced coverage failure');
            END
            """
        )
        with pytest.raises(RepositoryCoverageEvidenceError, match="transaction failed"):
            _record(
                services,
                root,
                upstreams,
                policy,
                second_ref,
                second_sha256,
                first,
            )
        state = services.search.repository_coverage_evidence_state(
            services.coverage.namespace(PROJECT_ID)
        )
        assert state is not None
        assert state.evidence_sha256 == first.evidence_sha256
        assert (
            services.search.connection.execute(
                """
                SELECT 1
                FROM repository_coverage_run_ledger
                WHERE project_id = ? AND test_run_id = ?
                """,
                (PROJECT_ID, "coverage-run-002"),
            ).fetchone()
            is None
        )
        services.search.connection.execute("DROP TRIGGER fail_coverage_state")
        services.search.connection.commit()
        retried = _record(
            services,
            root,
            upstreams,
            policy,
            second_ref,
            second_sha256,
            first,
        )
        assert retried.evidence.test_run_id == "coverage-run-002"
        restored_first = _record(
            services,
            root,
            upstreams,
            policy,
            first_ref,
            first_sha256,
            retried,
        )
        assert restored_first.evidence.test_run_id == "coverage-run-001"
        assert (
            restored_first.evidence.previous_evidence_sha256
            == retried.evidence_sha256
        )
    finally:
        services.search.close()


def test_ignored_run_ledger_insert_fails_before_pointer_advancement(
    tmp_path: Path,
) -> None:
    root, base_sha = _repository(tmp_path)
    services = _services(tmp_path / "state")
    policy = _policy()
    try:
        upstreams = _build_upstreams(root, base_sha, services)
        run = _trusted_run(root, upstreams, policy)
        run_ref, run_sha256 = _write_run(services.artifacts, run)
        services.search.connection.execute(
            """
            CREATE TRIGGER ignore_coverage_run_ledger
            BEFORE INSERT ON repository_coverage_run_ledger
            BEGIN
                SELECT RAISE(IGNORE);
            END
            """
        )
        services.search.connection.commit()
        with pytest.raises(
            RepositoryCoverageEvidenceError,
            match="ledger verification failed",
        ):
            _record(
                services,
                root,
                upstreams,
                policy,
                run_ref,
                run_sha256,
            )
        assert (
            services.search.repository_coverage_evidence_state(
                services.coverage.namespace(PROJECT_ID)
            )
            is None
        )
        assert (
            services.search.connection.execute(
                "SELECT COUNT(*) FROM repository_coverage_run_ledger"
            ).fetchone()[0]
            == 0
        )
    finally:
        services.search.close()


def test_concurrent_coverage_state_transitions_have_one_linearized_winner(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, base_sha = _repository(tmp_path)
    services = _services(tmp_path / "state")
    policy = _policy()
    try:
        upstreams = _build_upstreams(root, base_sha, services)
        dispatch_state = services.search.repository_dispatch_evidence_state(
            services.dispatch.namespace(PROJECT_ID)
        )
        assert dispatch_state is not None

        def candidate(suffix: str) -> RepositoryCoverageEvidenceState:
            return RepositoryCoverageEvidenceState(
                namespace=services.coverage.namespace(PROJECT_ID),
                project_id=PROJECT_ID,
                repository_url=REPOSITORY_URL,
                base_ref="main",
                base_sha=base_sha,
                source_tree_oid=_git(root, "rev-parse", "HEAD^{tree}"),
                repository_snapshot_ref=upstreams.index.snapshot_ref,
                repository_snapshot_sha256=upstreams.index.snapshot_sha256,
                dependency_graph_ref=upstreams.dependency.graph_ref,
                dependency_graph_sha256=upstreams.dependency.graph_sha256,
                call_graph_ref=upstreams.call.graph_ref,
                call_graph_sha256=upstreams.call.graph_sha256,
                dispatch_evidence_ref=upstreams.dispatch.evidence_ref,
                dispatch_evidence_sha256=upstreams.dispatch.evidence_sha256,
                trusted_run_ref=(
                    f"artifact://trusted-coverage-runs/{PROJECT_ID}/run-{suffix}.json"
                ),
                trusted_run_sha256=suffix * 64,
                test_run_id=f"coverage-run-{suffix}",
                trusted_test_policy_sha256=trusted_test_policy_sha256(policy),
                evidence_ref=(
                    f"artifact://coverage-evidence/{PROJECT_ID}/evidence-{suffix}.json"
                ),
                evidence_sha256=suffix * 64,
                policy_sha256="f" * 64,
            )

        candidates = (candidate("a"), candidate("b"))
        barrier = Barrier(2)
        opened_connections = []
        real_connect = search_service_module.sqlite3.connect

        def tracked_connect(*args, **kwargs):
            connection = real_connect(*args, **kwargs)
            opened_connections.append(connection)
            return connection

        monkeypatch.setattr(
            search_service_module.sqlite3,
            "connect",
            tracked_connect,
        )

        def apply(state: RepositoryCoverageEvidenceState) -> str:
            barrier.wait()
            try:
                services.search.apply_repository_coverage_evidence_state(
                    state=state,
                    expected_previous_evidence_ref=None,
                    expected_previous_evidence_sha256=None,
                )
            except RepositoryCoverageEvidenceStateError:
                return "rejected"
            return "committed"

        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = tuple(pool.map(apply, candidates))
        assert sorted(outcomes) == ["committed", "rejected"]
        assert len(opened_connections) == 2
        assert all(
            connection is not services.search.connection
            for connection in opened_connections
        )
        active = services.search.repository_coverage_evidence_state(
            services.coverage.namespace(PROJECT_ID)
        )
        assert active in candidates
        ledger_rows = services.search.connection.execute(
            """
            SELECT project_id, test_run_id, trusted_run_ref, trusted_run_sha256
            FROM repository_coverage_run_ledger
            WHERE project_id = ?
            """,
            (PROJECT_ID,),
        ).fetchall()
        assert len(ledger_rows) == 1
        assert ledger_rows[0][1] == active.test_run_id
    finally:
        services.search.close()


def test_concurrent_shared_rollback_cannot_undo_coverage_clear(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, base_sha = _repository(tmp_path)
    services = _services(tmp_path / "state")
    policy = _policy()
    release_clear = Event()
    clear_started = Event()
    try:
        upstreams = _build_upstreams(root, base_sha, services)
        run = _trusted_run(root, upstreams, policy)
        run_ref, run_sha256 = _write_run(services.artifacts, run)
        _record(services, root, upstreams, policy, run_ref, run_sha256)
        dispatch_state = services.search.repository_dispatch_evidence_state(
            services.dispatch.namespace(PROJECT_ID)
        )
        assert dispatch_state is not None
        services.search.connection.execute(
            """
            CREATE TRIGGER pause_coverage_clear
            BEFORE DELETE ON repository_coverage_evidence_state
            BEGIN
                SELECT pause_coverage_clear();
            END
            """
        )
        services.search.connection.execute("PRAGMA busy_timeout = 25")
        services.search.connection.commit()
        real_connect = search_service_module.sqlite3.connect

        def pause_clear() -> int:
            clear_started.set()
            assert release_clear.wait(timeout=5)
            return 0

        def connect_with_clear_hook(*args, **kwargs):
            connection = real_connect(*args, **kwargs)
            connection.create_function("pause_coverage_clear", 0, pause_clear)
            return connection

        monkeypatch.setattr(
            search_service_module.sqlite3,
            "connect",
            connect_with_clear_hook,
        )
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(
                services.search.clear_namespace,
                services.coverage.namespace(PROJECT_ID),
            )
            try:
                assert clear_started.wait(timeout=5)
                with pytest.raises(RepositoryDispatchEvidenceStateError):
                    services.search.apply_repository_dispatch_evidence_state(
                        state=dispatch_state,
                        expected_previous_evidence_ref=dispatch_state.evidence_ref,
                        expected_previous_evidence_sha256=(
                            dispatch_state.evidence_sha256
                        ),
                    )
            finally:
                release_clear.set()
            future.result(timeout=5)
        assert (
            services.search.repository_coverage_evidence_state(
                services.coverage.namespace(PROJECT_ID)
            )
            is None
        )
    finally:
        release_clear.set()
        services.search.close()


def test_upstream_state_race_fails_before_coverage_advancement(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, base_sha = _repository(tmp_path)
    services = _services(tmp_path / "state")
    policy = _policy()
    try:
        upstreams = _build_upstreams(root, base_sha, services)
        run = _trusted_run(root, upstreams, policy)
        run_ref, run_sha256 = _write_run(services.artifacts, run)
        original_write = services.coverage._write

        def race_dispatch_state(evidence):
            result = original_write(evidence)
            services.search.connection.execute(
                """
                UPDATE repository_dispatch_evidence_state
                SET evidence_ref = ?
                WHERE namespace = ?
                """,
                (
                    "artifact://dispatch-evidence/project-alpha/raced.json",
                    services.dispatch.namespace(PROJECT_ID),
                ),
            )
            services.search.connection.commit()
            return result

        monkeypatch.setattr(services.coverage, "_write", race_dispatch_state)
        with pytest.raises(RepositoryCoverageEvidenceError, match="evidence chain changed"):
            _record(
                services,
                root,
                upstreams,
                policy,
                run_ref,
                run_sha256,
            )
        assert (
            services.search.repository_coverage_evidence_state(
                services.coverage.namespace(PROJECT_ID)
            )
            is None
        )
    finally:
        services.search.close()


def test_exact_replay_rechecks_upstream_state_in_transaction(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, base_sha = _repository(tmp_path)
    services = _services(tmp_path / "state")
    policy = _policy()
    try:
        upstreams = _build_upstreams(root, base_sha, services)
        run = _trusted_run(root, upstreams, policy)
        run_ref, run_sha256 = _write_run(services.artifacts, run)
        recorded = _record(
            services,
            root,
            upstreams,
            policy,
            run_ref,
            run_sha256,
        )
        original_load_active = services.coverage._load_active
        load_count = 0

        def race_replay(state):
            nonlocal load_count
            evidence = original_load_active(state)
            load_count += 1
            if load_count == 2:
                services.search.connection.execute(
                    """
                    UPDATE repository_dispatch_evidence_state
                    SET evidence_ref = ?
                    WHERE namespace = ?
                    """,
                    (
                        "artifact://dispatch-evidence/project-alpha/replay-raced.json",
                        services.dispatch.namespace(PROJECT_ID),
                    ),
                )
                services.search.connection.commit()
            return evidence

        monkeypatch.setattr(services.coverage, "_load_active", race_replay)
        with pytest.raises(RepositoryCoverageEvidenceError, match="evidence chain changed"):
            _record(
                services,
                root,
                upstreams,
                policy,
                run_ref,
                run_sha256,
                recorded,
            )
        active = services.search.repository_coverage_evidence_state(
            services.coverage.namespace(PROJECT_ID)
        )
        assert active is not None
        assert active.evidence_sha256 == recorded.evidence_sha256
    finally:
        services.search.close()


def test_exact_replay_restart_project_isolation_and_cascade_cleanup(
    tmp_path: Path,
) -> None:
    workspace_root = tmp_path / "workspace"
    workspace = ProductWorkspace.create(workspace_root, FakeModelProvider())
    alpha_root, alpha_sha = _repository(tmp_path / "alpha")
    beta_root, beta_sha = _repository(tmp_path / "beta")
    policy = _policy()
    services = _Services(
        artifacts=workspace.artifacts,
        search=workspace.search,
        indexes=workspace.repository_indexes,
        dependencies=workspace.dependency_graphs,
        calls=workspace.call_graphs,
        dispatch=workspace.dispatch_evidence,
        coverage=workspace.coverage_evidence,
    )
    try:
        alpha_upstreams = _build_upstreams(alpha_root, alpha_sha, services)
        alpha_run = _trusted_run(alpha_root, alpha_upstreams, policy)
        alpha_ref, alpha_run_sha256 = _write_run(workspace.artifacts, alpha_run)
        alpha = _record(
            services,
            alpha_root,
            alpha_upstreams,
            policy,
            alpha_ref,
            alpha_run_sha256,
        )
        replay = _record(
            services,
            alpha_root,
            alpha_upstreams,
            policy,
            alpha_ref,
            alpha_run_sha256,
            alpha,
        )
        assert replay.replayed is True
        beta_upstreams = _build_upstreams(
            beta_root,
            beta_sha,
            services,
            project_id="project-beta",
            repository_url="https://example.test/project-beta.git",
        )
        beta_run = _trusted_run(
            beta_root,
            beta_upstreams,
            policy,
            project_id="project-beta",
            repository_url="https://example.test/project-beta.git",
            run_id="coverage-run-001",
        )
        beta_ref, beta_run_sha256 = _write_run(workspace.artifacts, beta_run)
        beta = _record(
            services,
            beta_root,
            beta_upstreams,
            policy,
            beta_ref,
            beta_run_sha256,
            project_id="project-beta",
        )
    finally:
        workspace.close()

    reopened = ProductWorkspace.create(workspace_root, FakeModelProvider())
    try:
        reopened_services = _Services(
            artifacts=reopened.artifacts,
            search=reopened.search,
            indexes=reopened.repository_indexes,
            dependencies=reopened.dependency_graphs,
            calls=reopened.call_graphs,
            dispatch=reopened.dispatch_evidence,
            coverage=reopened.coverage_evidence,
        )
        restart_replay = _record(
            reopened_services,
            alpha_root,
            alpha_upstreams,
            policy,
            alpha_ref,
            alpha_run_sha256,
            alpha,
        )
        assert restart_replay.replayed is True
        assert restart_replay.evidence_sha256 == alpha.evidence_sha256
        state, evidence = reopened.coverage_evidence.verified_active_evidence(
            project_id=PROJECT_ID,
            trusted_test_policy=policy,
            expected_evidence_ref=alpha.evidence_ref,
            expected_evidence_sha256=alpha.evidence_sha256,
        )
        assert state.evidence_sha256 == evidence.canonical_hash()
        reopened.search.clear_namespace(
            reopened.repository_indexes.namespace(PROJECT_ID)
        )
        assert (
            reopened.search.repository_coverage_evidence_state(
                reopened.coverage_evidence.namespace(PROJECT_ID)
            )
            is None
        )
        beta_state = reopened.search.repository_coverage_evidence_state(
            reopened.coverage_evidence.namespace("project-beta")
        )
        assert beta_state is not None
        assert beta_state.evidence_sha256 == beta.evidence_sha256
    finally:
        reopened.close()


def test_line_ranges_and_test_contexts_require_canonical_order() -> None:
    with pytest.raises(ValueError, match="canonically merged"):
        TrustedCoverageFile(
            path="src/pkg/core.py",
            source_sha256="a" * 64,
            ranges=(
                CoverageLineRange(start_line=1, end_line=2),
                CoverageLineRange(start_line=3, end_line=4),
            ),
        )
    with pytest.raises(ValueError, match="surrounding whitespace"):
        TrustedTestCoverage(
            profile_id="focused",
            test_id=" test-id",
            test_path="tests/test_core.py",
            test_source_sha256="a" * 64,
        )
    with pytest.raises(ValueError, match="not bound"):
        TrustedTestCoverage(
            profile_id="focused",
            test_id="tests/other.py::test_core",
            test_path="tests/test_core.py",
            test_source_sha256="a" * 64,
        )
