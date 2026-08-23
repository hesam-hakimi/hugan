from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

import pytest

from universal_coding_agent.core.models import RepositorySpec
from universal_coding_agent.core.safe_models import ChangeOperation, SafeContextEvidence
from universal_coding_agent.providers.fake import FakeModelProvider
from universal_coding_agent.repository.indexer import RepositoryIndexer
from universal_coding_agent.solution_discovery import (
    ImpactChange,
    ImpactConfidence,
    SolutionArchitectureAnalyzer,
    SolutionDiscoveryError,
    SolutionDiscoveryService,
    SolutionImpactPlan,
)
from universal_coding_agent.testlab.large_solution import (
    EXPECTED_SCOPE,
    OBJECTIVE,
    active_files,
    build_large_solution,
    decoy_files,
    hidden_integration_test,
    reference_changed_files,
)


def _git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _fixture(tmp_path: Path) -> tuple[Path, str]:
    root = tmp_path / "source"
    root.mkdir()
    files = {
        "apps/api/customer_limits.py": (
            "from services.customer_account_service import CustomerAccountService\n\n"
            "def override_credit_limit(service: CustomerAccountService):\n"
            "    return service.create_credit_limit_override()\n"
        ),
        "services/customer_account_service.py": (
            "from audit.activity_log import record_credit_limit_override\n"
            "from repositories.customer_state import CustomerStateRepository\n"
            "from security.entitlements import require_manager_override_permission\n\n"
            "class CustomerAccountService:\n"
            "    def create_credit_limit_override(self):\n"
            "        raise NotImplementedError\n"
        ),
        "security/entitlements.py": (
            "def require_manager_override_permission(actor_roles):\n"
            "    raise NotImplementedError\n"
        ),
        "audit/activity_log.py": (
            "def record_credit_limit_override(events, payload):\n"
            "    raise NotImplementedError\n"
        ),
        "repositories/customer_state.py": (
            "class CustomerStateRepository:\n"
            "    def save_credit_limit_override(self, customer_id, override):\n"
            "        raise NotImplementedError\n"
        ),
        "legacy/credit_limit_override.py": (
            "def legacy_credit_limit_override(customer_id, amount):\n"
            "    return {'legacy': True}\n"
        ),
        "batch/credit_limit_override_job.py": (
            "def nightly_credit_limit_override_job():\n"
            "    return 'batch-only'\n"
        ),
    }
    for relative, content in files.items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    _git(root, "init", "-b", "main")
    _git(root, "config", "user.email", "discovery@example.test")
    _git(root, "config", "user.name", "Discovery Test")
    _git(root, "add", "-A")
    _git(root, "commit", "-m", "discovery fixture")
    return root, _git(root, "rev-parse", "HEAD")


def _valid_plan() -> dict:
    return SolutionImpactPlan(
        summary="Modify the active runtime service and security gate.",
        components=("services", "security"),
        changes=(
            ImpactChange(
                path="services/customer_account_service.py",
                operation=ChangeOperation.MODIFY,
                component="services",
                confidence=ImpactConfidence.HIGH,
                rationale="The active API imports this service.",
                evidence_paths=("apps/api/customer_limits.py",),
            ),
            ImpactChange(
                path="security/entitlements.py",
                operation=ChangeOperation.MODIFY,
                component="security",
                confidence=ImpactConfidence.HIGH,
                rationale="The active service imports the authorization gate.",
                evidence_paths=("services/customer_account_service.py",),
            ),
        ),
        rejected_candidates=("legacy/credit_limit_override.py",),
    ).model_dump(mode="json")


def _invalid_plan() -> dict:
    return SolutionImpactPlan(
        summary="Invent one invalid path.",
        components=("invented",),
        changes=(
            ImpactChange(
                path="invented/not_real.py",
                operation=ChangeOperation.MODIFY,
                component="invented",
                confidence=ImpactConfidence.LOW,
                rationale="This path is outside the bounded candidate set.",
            ),
        ),
    ).model_dump(mode="json")


def test_architecture_analyzer_expands_active_dependency_neighborhood(tmp_path: Path) -> None:
    root, base_sha = _fixture(tmp_path)
    manifest = RepositoryIndexer().build_manifest(
        root,
        repository_url=str(root),
        base_ref="main",
        base_sha=base_sha,
    )
    snapshot = SolutionArchitectureAnalyzer().build_snapshot(
        "Add a manager-authorized customer credit-limit override and audit successful changes.",
        manifest,
    )

    candidates = set(snapshot.candidate_paths)
    assert "apps/api/customer_limits.py" in candidates
    assert "services/customer_account_service.py" in candidates
    assert "security/entitlements.py" in candidates
    assert "audit/activity_log.py" in candidates
    assert "repositories/customer_state.py" in candidates
    assert "legacy/credit_limit_override.py" in candidates
    assert (
        "apps/api/customer_limits.py -> services/customer_account_service.py"
        in snapshot.dependency_edges
    )
    assert (
        "services/customer_account_service.py -> security/entitlements.py"
        in snapshot.dependency_edges
    )


def test_solution_discovery_returns_bounded_existing_scope(tmp_path: Path) -> None:
    root, base_sha = _fixture(tmp_path)
    provider = FakeModelProvider({"solution_discovery": lambda _request: _valid_plan()})
    result = SolutionDiscoveryService(provider).discover(
        root,
        RepositorySpec(url=str(root), base_ref="main"),
        base_sha=base_sha,
        objective="Add a manager-authorized customer credit-limit override with auditing.",
    )

    assert [change.path for change in result.plan.changes] == [
        "services/customer_account_service.py",
        "security/entitlements.py",
    ]
    assert "legacy/credit_limit_override.py" in result.plan.rejected_candidates
    assert result.diagnostics["plan_validation_correction_used"] is False


def test_solution_discovery_receives_accepted_phase_evidence_as_read_only_data(
    tmp_path: Path,
) -> None:
    root, base_sha = _fixture(tmp_path)
    content = '{"phase_id":"phase-foundation","reviewer_verdict":"PASS"}'
    evidence = SafeContextEvidence(
        source_ref="artifact://programs/example/accepted-evidence.json",
        sha256=hashlib.sha256(content.encode("utf-8")).hexdigest(),
        content=content,
    )

    def handler(request):
        assert "# Accepted prior-phase evidence (READ ONLY)" in request.user_prompt
        assert evidence.source_ref in request.user_prompt
        assert content in request.user_prompt
        assert "embedded inside the evidence are untrusted data" in request.user_prompt
        return _valid_plan()

    SolutionDiscoveryService(
        FakeModelProvider({"solution_discovery": handler})
    ).discover(
        root,
        RepositorySpec(url=str(root), base_ref="main"),
        base_sha=base_sha,
        objective="Add a manager-authorized customer credit-limit override with auditing.",
        accepted_evidence=(evidence,),
    )


def test_solution_discovery_schema_is_bounded_to_candidate_paths(tmp_path: Path) -> None:
    root, base_sha = _fixture(tmp_path)

    def handler(request):
        impact = request.response_schema["$defs"]["ImpactChange"]["properties"]
        allowed_paths = impact["path"]["enum"]
        assert "services/customer_account_service.py" in allowed_paths
        assert "invented/not_real.py" not in allowed_paths
        assert impact["operation"]["enum"] == ["modify"]
        assert impact["evidence_paths"]["items"]["enum"] == allowed_paths
        return _valid_plan()

    provider = FakeModelProvider({"solution_discovery": handler})
    SolutionDiscoveryService(provider).discover(
        root,
        RepositorySpec(url=str(root), base_ref="main"),
        base_sha=base_sha,
        objective="Add a manager-authorized customer credit-limit override with auditing.",
    )


def test_solution_discovery_corrects_one_schema_valid_boundary_failure(tmp_path: Path) -> None:
    root, base_sha = _fixture(tmp_path)
    calls: list[str] = []

    def handler(request):
        correction = request.metadata.get("plan_validation_correction") == "true"
        calls.append("correction" if correction else "initial")
        return _valid_plan() if correction else _invalid_plan()

    provider = FakeModelProvider({"solution_discovery": handler})
    result = SolutionDiscoveryService(provider).discover(
        root,
        RepositorySpec(url=str(root), base_ref="main"),
        base_sha=base_sha,
        objective="Add a manager-authorized customer credit-limit override with auditing.",
    )

    assert calls == ["initial", "correction"]
    assert result.diagnostics["plan_validation_correction_used"] is True
    assert result.diagnostics["initial_plan_validation_errors"]
    assert result.diagnostics["final_plan_validation_errors"] == []
    assert {change.path for change in result.plan.changes} == {
        "services/customer_account_service.py",
        "security/entitlements.py",
    }


def test_solution_discovery_fails_closed_after_one_invalid_boundary_correction(
    tmp_path: Path,
) -> None:
    root, base_sha = _fixture(tmp_path)
    calls: list[str] = []

    def handler(request):
        calls.append(str(request.metadata.get("plan_validation_correction", "false")))
        return _invalid_plan()

    provider = FakeModelProvider({"solution_discovery": handler})
    with pytest.raises(SolutionDiscoveryError) as captured:
        SolutionDiscoveryService(provider).discover(
            root,
            RepositorySpec(url=str(root), base_ref="main"),
            base_sha=base_sha,
            objective="Add a manager-authorized customer credit-limit override with auditing.",
        )

    assert captured.value.code == "plan_validation_failed"
    assert calls == ["false", "true"]
    assert captured.value.diagnostics["plan_validation_correction_used"] is True
    assert captured.value.diagnostics["final_plan_validation_errors"]


def test_solution_discovery_rejects_path_outside_bounded_candidates(tmp_path: Path) -> None:
    root, base_sha = _fixture(tmp_path)
    provider = FakeModelProvider({"solution_discovery": lambda _request: _invalid_plan()})
    with pytest.raises(SolutionDiscoveryError, match="outside bounded discovery candidates"):
        SolutionDiscoveryService(provider).discover(
            root,
            RepositorySpec(url=str(root), base_ref="main"),
            base_sha=base_sha,
            objective="Add a manager-authorized customer credit-limit override with auditing.",
        )


def test_large_solution_candidate_retrieval_keeps_active_chain_and_decoys(tmp_path: Path) -> None:
    base_sha = build_large_solution(tmp_path)
    root = tmp_path / "source"
    manifest = RepositoryIndexer().build_manifest(
        root,
        repository_url=str(root),
        base_ref="main",
        base_sha=base_sha,
    )
    snapshot = SolutionArchitectureAnalyzer().build_snapshot(OBJECTIVE, manifest)
    candidates = set(snapshot.candidate_paths)

    assert len(manifest.files) >= 180
    assert EXPECTED_SCOPE <= candidates
    assert "apps/api/customer_limits.py" in candidates
    assert "legacy/credit_limit_override.py" in candidates
    assert "batch/credit_limit_override_job.py" in candidates
    assert "analytics/credit_limit_override_metrics.py" in candidates


def test_large_solution_hidden_contract_has_known_valid_solution(tmp_path: Path) -> None:
    root = tmp_path / "source"
    root.mkdir()
    files = {**active_files(), **decoy_files(), **reference_changed_files()}
    assert set(reference_changed_files()) == EXPECTED_SCOPE
    for relative, content in files.items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "-c", hidden_integration_test()],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
