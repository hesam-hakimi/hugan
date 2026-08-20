from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from universal_coding_agent.core.models import RepositorySpec
from universal_coding_agent.core.safe_models import ChangeOperation
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

    def handler(_request):
        return SolutionImpactPlan(
            summary="Modify the active runtime service and its supporting components.",
            components=("services", "security", "audit", "repositories"),
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

    provider = FakeModelProvider({"solution_discovery": handler})
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


def test_solution_discovery_rejects_path_outside_bounded_candidates(tmp_path: Path) -> None:
    root, base_sha = _fixture(tmp_path)

    def handler(_request):
        return SolutionImpactPlan(
            summary="Invent an invalid path.",
            components=("invented",),
            changes=(
                ImpactChange(
                    path="invented/not_real.py",
                    operation=ChangeOperation.MODIFY,
                    component="invented",
                    confidence=ImpactConfidence.LOW,
                    rationale="This path does not exist and must be rejected.",
                ),
            ),
        ).model_dump(mode="json")

    provider = FakeModelProvider({"solution_discovery": handler})
    with pytest.raises(SolutionDiscoveryError, match="outside bounded discovery candidates"):
        SolutionDiscoveryService(provider).discover(
            root,
            RepositorySpec(url=str(root), base_ref="main"),
            base_sha=base_sha,
            objective="Add a manager-authorized customer credit-limit override with auditing.",
        )
