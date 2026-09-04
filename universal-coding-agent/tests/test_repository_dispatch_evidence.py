from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from universal_coding_agent.product.call_graphs import RepositoryCallGraphService
from universal_coding_agent.product.dependency_graphs import RepositoryDependencyService
from universal_coding_agent.product.dispatch_evidence import (
    BaseResolution,
    DispatchResolution,
    RepositoryDispatchEvidenceError,
    RepositoryDispatchEvidenceService,
)
from universal_coding_agent.product.repository_indexes import RepositoryIndexService
from universal_coding_agent.product.search_service import SearchService
from universal_coding_agent.product.workspace import ProductWorkspace
from universal_coding_agent.providers.fake import FakeModelProvider
from universal_coding_agent.storage.artifacts import ArtifactStore

PROJECT_ID = "project-alpha"
REPOSITORY_URL = "https://example.test/project-alpha.git"


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True, text=True
    ).stdout.strip()


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
    _git(root, "config", "user.email", "dispatch@example.test")
    _git(root, "config", "user.name", "Dispatch Test")
    for path, content in files.items():
        _write(root, path, content)
    return root, _commit(root, "initial dispatch fixture")


def _services(tmp_path: Path, **limits: int):
    artifacts = ArtifactStore(tmp_path / "artifacts")
    search = SearchService(tmp_path / "search.sqlite")
    indexes = RepositoryIndexService(artifacts, search)
    dependencies = RepositoryDependencyService(artifacts, search, indexes)
    calls = RepositoryCallGraphService(artifacts, search, dependencies)
    dispatch = RepositoryDispatchEvidenceService(artifacts, search, calls, **limits)
    return artifacts, search, indexes, dependencies, calls, dispatch


def _build(root: Path, base_sha: str, services, previous=None):
    _artifacts, _search, indexes, dependencies, calls, dispatch = services
    indexed = indexes.index(
        project_id=PROJECT_ID,
        root=root,
        repository_url=REPOSITORY_URL,
        base_ref="main",
        base_sha=base_sha,
        expected_previous_snapshot_sha256=None,
    )
    dependency = dependencies.build_graph(
        project_id=PROJECT_ID,
        expected_repository_snapshot_sha256=indexed.snapshot_sha256,
        expected_previous_graph_sha256=None,
    )
    call = calls.build_graph(
        project_id=PROJECT_ID,
        root=root,
        expected_repository_snapshot_ref=indexed.snapshot_ref,
        expected_repository_snapshot_sha256=indexed.snapshot_sha256,
        expected_dependency_graph_ref=dependency.graph_ref,
        expected_dependency_graph_sha256=dependency.graph_sha256,
        expected_previous_call_graph_ref=None,
        expected_previous_call_graph_sha256=None,
    )
    result = dispatch.build_evidence(
        project_id=PROJECT_ID,
        root=root,
        expected_call_graph_ref=call.graph_ref,
        expected_call_graph_sha256=call.graph_sha256,
        expected_previous_evidence_ref=(previous.evidence_ref if previous else None),
        expected_previous_evidence_sha256=(previous.evidence_sha256 if previous else None),
    )
    return indexed, dependency, call, result


def _symbols(call_graph) -> dict[str, object]:
    return {item.symbol_id: item for item in call_graph.symbols}


def test_emits_conservative_override_candidates_from_explicit_types(
    tmp_path: Path,
) -> None:
    root, base_sha = _repository(
        tmp_path,
        {
            "models.py": (
                "class Base:\n"
                "    def run(self):\n"
                "        return self.helper()\n"
                "    def helper(self):\n"
                "        return 1\n\n"
                "class Child(Base):\n"
                "    def run(self):\n"
                "        return 2\n"
            ),
            "consumer.py": (
                "from models import Base, Child\n\n"
                "def annotated(worker: Base):\n"
                "    return worker.run()\n\n"
                "def constructed():\n"
                "    worker = Child()\n"
                "    return worker.run()\n"
            ),
        },
    )
    services = _services(tmp_path / "state")
    try:
        head_before = _git(root, "rev-parse", "HEAD")
        tree_before = _git(root, "rev-parse", "HEAD^{tree}")
        _indexed, _dependency, call, built = _build(root, base_sha, services)
        symbols = _symbols(call.graph)
        sites = list(built.evidence.dispatch_sites)
        annotated = next(
            item for item in sites if symbols[item.caller_symbol_id].qualname == "annotated"
        )
        assert annotated.resolution is DispatchResolution.POLYMORPHIC_CANDIDATES
        assert {symbols[item].qualname for item in annotated.receiver_class_ids} == {
            "Base",
            "Child",
        }
        assert {symbols[item].qualname for item in annotated.candidate_method_ids} == {
            "Base.run",
            "Child.run",
        }
        constructed = next(
            item for item in sites if symbols[item.caller_symbol_id].qualname == "constructed"
        )
        assert constructed.resolution is DispatchResolution.EXACT_DECLARED_TYPE
        assert {symbols[item].qualname for item in constructed.candidate_method_ids} == {
            "Child.run"
        }
        self_site = next(item for item in sites if item.expression == "self.helper")
        assert self_site.resolution is DispatchResolution.POLYMORPHIC_CANDIDATES
        assert {symbols[item].qualname for item in self_site.candidate_method_ids} == {
            "Base.helper"
        }
        assert _git(root, "rev-parse", "HEAD") == head_before
        assert _git(root, "rev-parse", "HEAD^{tree}") == tree_before
        assert _git(root, "status", "--porcelain") == ""
    finally:
        services[1].close()


def test_records_unknown_missing_and_unsafe_hierarchy_without_guessing(
    tmp_path: Path,
) -> None:
    root, base_sha = _repository(
        tmp_path,
        {
            "cases.py": (
                "class Left:\n"
                "    def run(self):\n"
                "        return 1\n\n"
                "class Right:\n"
                "    def run(self):\n"
                "        return 2\n\n"
                "class Mixed(Left, Right):\n"
                "    pass\n\n"
                "class Empty:\n"
                "    pass\n\n"
                "class CycleA(CycleB):\n"
                "    def run(self):\n"
                "        return 1\n\n"
                "class CycleB(CycleA):\n"
                "    pass\n\n"
                "class Reassigned:\n"
                "    def run(self):\n"
                "        return 1\n"
                "Reassigned = object()\n\n"
                "def unknown(value):\n"
                "    value.run()\n\n"
                "def unsafe(value: Mixed):\n"
                "    value.run()\n\n"
                "def missing(value: Empty):\n"
                "    value.run()\n\n"
                "def cycle(value: CycleA):\n"
                "    value.run()\n\n"
                "def unsafe_binding(value: Reassigned):\n"
                "    value.run()\n"
            )
        },
    )
    services = _services(tmp_path / "state")
    try:
        _indexed, _dependency, call, built = _build(root, base_sha, services)
        symbols = _symbols(call.graph)
        sites = {
            symbols[item.caller_symbol_id].qualname: item for item in built.evidence.dispatch_sites
        }
        resolutions = {item.resolution for item in sites.values()}
        assert DispatchResolution.UNKNOWN_RECEIVER in resolutions
        assert DispatchResolution.UNSAFE_HIERARCHY in resolutions
        assert DispatchResolution.MISSING_METHOD in resolutions
        assert sites["cycle"].resolution is DispatchResolution.UNSAFE_HIERARCHY
        assert sites["unsafe_binding"].resolution is (DispatchResolution.AMBIGUOUS_RECEIVER)
        mixed_bases = [
            item for item in built.evidence.bases if item.expression in {"Left", "Right"}
        ]
        assert len(mixed_bases) == 2
        assert all(item.resolution is BaseResolution.RESOLVED for item in mixed_bases)
        assert all(
            not item.candidate_method_ids
            for item in sites.values()
            if item.resolution
            not in {
                DispatchResolution.EXACT_DECLARED_TYPE,
                DispatchResolution.POLYMORPHIC_CANDIDATES,
            }
        )
    finally:
        services[1].close()


def test_conditional_assignment_and_decorated_method_remain_unresolved(
    tmp_path: Path,
) -> None:
    root, base_sha = _repository(
        tmp_path,
        {
            "cases.py": (
                "class Worker:\n"
                "    @staticmethod\n"
                "    def decorated(self):\n"
                "        self.run()\n"
                "    def run(self):\n"
                "        return 1\n\n"
                "def conditional(flag):\n"
                "    if flag:\n"
                "        worker = Worker()\n"
                "    worker.run()\n\n"
                "def deleted():\n"
                "    worker = Worker()\n"
                "    del worker\n"
                "    worker.run()\n\n"
                "def unpacked():\n"
                "    left, right = Worker()\n"
                "    left.run()\n"
            )
        },
    )
    services = _services(tmp_path / "state")
    try:
        _indexed, _dependency, call, built = _build(root, base_sha, services)
        symbols = _symbols(call.graph)
        by_caller = {
            symbols[item.caller_symbol_id].qualname: item for item in built.evidence.dispatch_sites
        }
        assert by_caller["Worker.decorated"].resolution is (DispatchResolution.UNKNOWN_RECEIVER)
        assert by_caller["conditional"].resolution is (DispatchResolution.AMBIGUOUS_RECEIVER)
        assert by_caller["deleted"].resolution is DispatchResolution.AMBIGUOUS_RECEIVER
        assert by_caller["unpacked"].resolution is DispatchResolution.AMBIGUOUS_RECEIVER
        assert not by_caller["Worker.decorated"].candidate_method_ids
        assert not by_caller["conditional"].candidate_method_ids
    finally:
        services[1].close()


def test_exact_refs_policy_source_and_artifact_drift_fail_closed(tmp_path: Path) -> None:
    root, base_sha = _repository(
        tmp_path,
        {"a.py": "class A:\n    def run(self):\n        return self.run()\n"},
    )
    services = _services(tmp_path / "state")
    artifacts, search, _indexes, _dependencies, _calls, dispatch = services
    try:
        _indexed, _dependency, call, built = _build(root, base_sha, services)
        with pytest.raises(RepositoryDispatchEvidenceError, match="call-graph reference"):
            dispatch.build_evidence(
                project_id=PROJECT_ID,
                root=root,
                expected_call_graph_ref=call.graph_ref + "-different",
                expected_call_graph_sha256=call.graph_sha256,
                expected_previous_evidence_ref=built.evidence_ref,
                expected_previous_evidence_sha256=built.evidence_sha256,
            )
        changed_policy = RepositoryDispatchEvidenceService(
            artifacts, search, services[4], max_sites=249_999
        )
        with pytest.raises(RepositoryDispatchEvidenceError, match="policy"):
            changed_policy.build_evidence(
                project_id=PROJECT_ID,
                root=root,
                expected_call_graph_ref=call.graph_ref,
                expected_call_graph_sha256=call.graph_sha256,
                expected_previous_evidence_ref=built.evidence_ref,
                expected_previous_evidence_sha256=built.evidence_sha256,
            )
        _write(root, "a.py", "class A:\n    def run(self):\n        return 2\n")
        with pytest.raises(RepositoryDispatchEvidenceError, match="not clean"):
            dispatch.build_evidence(
                project_id=PROJECT_ID,
                root=root,
                expected_call_graph_ref=call.graph_ref,
                expected_call_graph_sha256=call.graph_sha256,
                expected_previous_evidence_ref=built.evidence_ref,
                expected_previous_evidence_sha256=built.evidence_sha256,
            )
        _git(root, "restore", "a.py")
        evidence_path = artifacts.root / built.evidence_ref.removeprefix("artifact://")
        evidence_path.write_text("{}", encoding="utf-8")
        with pytest.raises(RepositoryDispatchEvidenceError, match="integrity verification"):
            dispatch.verified_active_evidence(
                project_id=PROJECT_ID,
                expected_evidence_ref=built.evidence_ref,
                expected_evidence_sha256=built.evidence_sha256,
            )
    finally:
        search.close()


def test_changed_call_graph_rebuild_matches_clean_derivation(tmp_path: Path) -> None:
    root, first_sha = _repository(
        tmp_path,
        {
            "a.py": (
                "class Base:\n"
                "    def run(self):\n"
                "        return 1\n\n"
                "def invoke(value: Base):\n"
                "    return value.run()\n"
            )
        },
    )
    services = _services(tmp_path / "incremental-state")
    clean_services = _services(tmp_path / "clean-state")
    _artifacts, search, indexes, dependencies, calls, dispatch = services
    try:
        first_index, first_dependency, first_call, first_evidence = _build(
            root, first_sha, services
        )
        _write(
            root,
            "a.py",
            (
                "class Base:\n"
                "    def run(self):\n"
                "        return 1\n\n"
                "class Child(Base):\n"
                "    def run(self):\n"
                "        return 2\n\n"
                "def invoke(value: Base):\n"
                "    return value.run()\n"
            ),
        )
        second_sha = _commit(root, "add an overriding subclass")
        second_index = indexes.index(
            project_id=PROJECT_ID,
            root=root,
            repository_url=REPOSITORY_URL,
            base_ref="main",
            base_sha=second_sha,
            expected_previous_snapshot_sha256=first_index.snapshot_sha256,
        )
        second_dependency = dependencies.build_graph(
            project_id=PROJECT_ID,
            expected_repository_snapshot_sha256=second_index.snapshot_sha256,
            expected_previous_graph_sha256=first_dependency.graph_sha256,
        )
        second_call = calls.build_graph(
            project_id=PROJECT_ID,
            root=root,
            expected_repository_snapshot_ref=second_index.snapshot_ref,
            expected_repository_snapshot_sha256=second_index.snapshot_sha256,
            expected_dependency_graph_ref=second_dependency.graph_ref,
            expected_dependency_graph_sha256=second_dependency.graph_sha256,
            expected_previous_call_graph_ref=first_call.graph_ref,
            expected_previous_call_graph_sha256=first_call.graph_sha256,
        )
        second_evidence = dispatch.build_evidence(
            project_id=PROJECT_ID,
            root=root,
            expected_call_graph_ref=second_call.graph_ref,
            expected_call_graph_sha256=second_call.graph_sha256,
            expected_previous_evidence_ref=first_evidence.evidence_ref,
            expected_previous_evidence_sha256=first_evidence.evidence_sha256,
        )
        _clean_index, _clean_dependency, _clean_call, clean = _build(
            root, second_sha, clean_services
        )
        assert second_evidence.evidence.classes == clean.evidence.classes
        assert second_evidence.evidence.bases == clean.evidence.bases
        assert second_evidence.evidence.dispatch_sites == clean.evidence.dispatch_sites
    finally:
        search.close()
        clean_services[1].close()


def test_exact_replay_restart_integrity_and_cascade_cleanup(tmp_path: Path) -> None:
    root, base_sha = _repository(
        tmp_path,
        {"a.py": "class A:\n    def run(self):\n        return self.run()\n"},
    )
    workspace_root = tmp_path / "workspace"
    workspace = ProductWorkspace.create(workspace_root, FakeModelProvider())
    beta_root, beta_sha = _repository(
        tmp_path / "beta",
        {"b.py": "class B:\n    def run(self):\n        return self.run()\n"},
    )
    services = (
        workspace.artifacts,
        workspace.search,
        workspace.repository_indexes,
        workspace.dependency_graphs,
        workspace.call_graphs,
        workspace.dispatch_evidence,
    )
    try:
        indexed, dependency, call, built = _build(root, base_sha, services)
        beta_index = workspace.repository_indexes.index(
            project_id="project-beta",
            root=beta_root,
            repository_url="https://example.test/project-beta.git",
            base_ref="main",
            base_sha=beta_sha,
            expected_previous_snapshot_sha256=None,
        )
        beta_dependency = workspace.dependency_graphs.build_graph(
            project_id="project-beta",
            expected_repository_snapshot_sha256=beta_index.snapshot_sha256,
            expected_previous_graph_sha256=None,
        )
        beta_call = workspace.call_graphs.build_graph(
            project_id="project-beta",
            root=beta_root,
            expected_repository_snapshot_ref=beta_index.snapshot_ref,
            expected_repository_snapshot_sha256=beta_index.snapshot_sha256,
            expected_dependency_graph_ref=beta_dependency.graph_ref,
            expected_dependency_graph_sha256=beta_dependency.graph_sha256,
            expected_previous_call_graph_ref=None,
            expected_previous_call_graph_sha256=None,
        )
        beta_evidence = workspace.dispatch_evidence.build_evidence(
            project_id="project-beta",
            root=beta_root,
            expected_call_graph_ref=beta_call.graph_ref,
            expected_call_graph_sha256=beta_call.graph_sha256,
            expected_previous_evidence_ref=None,
            expected_previous_evidence_sha256=None,
        )
        replayed = workspace.dispatch_evidence.build_evidence(
            project_id=PROJECT_ID,
            root=root,
            expected_call_graph_ref=call.graph_ref,
            expected_call_graph_sha256=call.graph_sha256,
            expected_previous_evidence_ref=built.evidence_ref,
            expected_previous_evidence_sha256=built.evidence_sha256,
        )
        assert replayed.replayed is True
    finally:
        workspace.close()
    reopened = ProductWorkspace.create(workspace_root, FakeModelProvider())
    try:
        state, evidence = reopened.dispatch_evidence.verified_active_evidence(
            project_id=PROJECT_ID,
            expected_evidence_ref=built.evidence_ref,
            expected_evidence_sha256=built.evidence_sha256,
        )
        assert evidence.call_graph_sha256 == call.graph_sha256
        assert state.repository_snapshot_sha256 == indexed.snapshot_sha256
        assert state.dependency_graph_sha256 == dependency.graph_sha256
        reopened.search.clear_namespace(reopened.repository_indexes.namespace(PROJECT_ID))
        assert (
            reopened.search.repository_dispatch_evidence_state(
                reopened.dispatch_evidence.namespace(PROJECT_ID)
            )
            is None
        )
        beta_state = reopened.search.repository_dispatch_evidence_state(
            reopened.dispatch_evidence.namespace("project-beta")
        )
        assert beta_state is not None
        assert beta_state.evidence_sha256 == beta_evidence.evidence_sha256
    finally:
        reopened.close()


@pytest.mark.parametrize(
    ("limits", "message"),
    [
        ({"max_source_bytes": 1}, "source-byte limit"),
        ({"max_classes": 1}, "class limit"),
        ({"max_bases": 1}, "base limit"),
        ({"max_sites": 1}, "site limit"),
        ({"max_candidates": 1}, "candidate limit"),
        ({"max_expression_bytes": 4}, "expression limit"),
        ({"evidence_max_bytes": 1}, "byte limit"),
    ],
)
def test_independent_bounds_fail_before_active_state(
    tmp_path: Path, limits: dict[str, int], message: str
) -> None:
    root, base_sha = _repository(
        tmp_path,
        {
            "a.py": (
                "class A:\n"
                "    def run(self):\n"
                "        self.run()\n"
                "        self.run()\n\n"
                "class B(A):\n"
                "    def run(self):\n"
                "        return 1\n\n"
                "class C(B):\n"
                "    pass\n"
            )
        },
    )
    services = _services(tmp_path / "state", **limits)
    try:
        with pytest.raises(RepositoryDispatchEvidenceError, match=message):
            _build(root, base_sha, services)
        assert (
            services[1].repository_dispatch_evidence_state(services[5].namespace(PROJECT_ID))
            is None
        )
    finally:
        services[1].close()


def test_state_transaction_rolls_back_and_exact_retry_succeeds(tmp_path: Path) -> None:
    root, base_sha = _repository(
        tmp_path,
        {"a.py": "class A:\n    def run(self):\n        return self.run()\n"},
    )
    services = _services(tmp_path / "state")
    _artifacts, search, indexes, dependencies, calls, dispatch = services
    try:
        indexed = indexes.index(
            project_id=PROJECT_ID,
            root=root,
            repository_url=REPOSITORY_URL,
            base_ref="main",
            base_sha=base_sha,
            expected_previous_snapshot_sha256=None,
        )
        dependency = dependencies.build_graph(
            project_id=PROJECT_ID,
            expected_repository_snapshot_sha256=indexed.snapshot_sha256,
            expected_previous_graph_sha256=None,
        )
        call = calls.build_graph(
            project_id=PROJECT_ID,
            root=root,
            expected_repository_snapshot_ref=indexed.snapshot_ref,
            expected_repository_snapshot_sha256=indexed.snapshot_sha256,
            expected_dependency_graph_ref=dependency.graph_ref,
            expected_dependency_graph_sha256=dependency.graph_sha256,
            expected_previous_call_graph_ref=None,
            expected_previous_call_graph_sha256=None,
        )
        search.connection.execute(
            """
            CREATE TRIGGER fail_dispatch_state
            BEFORE INSERT ON repository_dispatch_evidence_state
            BEGIN
                SELECT RAISE(ABORT, 'forced dispatch failure');
            END
            """
        )
        with pytest.raises(RepositoryDispatchEvidenceError, match="transaction failed"):
            dispatch.build_evidence(
                project_id=PROJECT_ID,
                root=root,
                expected_call_graph_ref=call.graph_ref,
                expected_call_graph_sha256=call.graph_sha256,
                expected_previous_evidence_ref=None,
                expected_previous_evidence_sha256=None,
            )
        assert search.repository_dispatch_evidence_state(dispatch.namespace(PROJECT_ID)) is None
        search.connection.execute("DROP TRIGGER fail_dispatch_state")
        search.connection.commit()
        retried = dispatch.build_evidence(
            project_id=PROJECT_ID,
            root=root,
            expected_call_graph_ref=call.graph_ref,
            expected_call_graph_sha256=call.graph_sha256,
            expected_previous_evidence_ref=None,
            expected_previous_evidence_sha256=None,
        )
        assert retried.evidence_sha256
    finally:
        search.close()


def test_call_graph_state_race_fails_before_dispatch_advancement(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, base_sha = _repository(
        tmp_path,
        {"a.py": "class A:\n    def run(self):\n        return self.run()\n"},
    )
    services = _services(tmp_path / "state")
    _artifacts, search, indexes, dependencies, calls, dispatch = services
    try:
        indexed = indexes.index(
            project_id=PROJECT_ID,
            root=root,
            repository_url=REPOSITORY_URL,
            base_ref="main",
            base_sha=base_sha,
            expected_previous_snapshot_sha256=None,
        )
        dependency = dependencies.build_graph(
            project_id=PROJECT_ID,
            expected_repository_snapshot_sha256=indexed.snapshot_sha256,
            expected_previous_graph_sha256=None,
        )
        call = calls.build_graph(
            project_id=PROJECT_ID,
            root=root,
            expected_repository_snapshot_ref=indexed.snapshot_ref,
            expected_repository_snapshot_sha256=indexed.snapshot_sha256,
            expected_dependency_graph_ref=dependency.graph_ref,
            expected_dependency_graph_sha256=dependency.graph_sha256,
            expected_previous_call_graph_ref=None,
            expected_previous_call_graph_sha256=None,
        )
        original_write = dispatch._write

        def race_call_state(evidence):
            result = original_write(evidence)
            search.connection.execute(
                """
                UPDATE repository_call_graph_state
                SET graph_ref = ?
                WHERE namespace = ?
                """,
                ("artifact://call-graphs/project-alpha/raced.json", calls.namespace(PROJECT_ID)),
            )
            search.connection.commit()
            return result

        monkeypatch.setattr(dispatch, "_write", race_call_state)
        with pytest.raises(RepositoryDispatchEvidenceError, match="call graph changed"):
            dispatch.build_evidence(
                project_id=PROJECT_ID,
                root=root,
                expected_call_graph_ref=call.graph_ref,
                expected_call_graph_sha256=call.graph_sha256,
                expected_previous_evidence_ref=None,
                expected_previous_evidence_sha256=None,
            )
        assert search.repository_dispatch_evidence_state(dispatch.namespace(PROJECT_ID)) is None
    finally:
        search.close()
