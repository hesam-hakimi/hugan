from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from universal_coding_agent.core.models import RepositorySpec
from universal_coding_agent.core.safe_models import SafeModePolicy, TestProfile
from universal_coding_agent.discovered_safe_service import (
    DiscoveredSafeAgentService,
    DiscoveredSafeStartError,
)
from universal_coding_agent.providers.fake import FakeModelProvider
from universal_coding_agent.solution_discovery import (
    ImpactChange,
    ImpactConfidence,
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


def _repository(tmp_path: Path) -> tuple[Path, str]:
    root = tmp_path / "source"
    (root / "apps" / "api").mkdir(parents=True)
    (root / "services").mkdir()
    (root / "domain").mkdir()
    (root / "legacy").mkdir()
    (root / "apps" / "api" / "limits.py").write_text(
        "from services.limit_service import create_override\n",
        encoding="utf-8",
    )
    (root / "services" / "limit_service.py").write_text(
        "from domain.limit_rules import validate_override\n\n"
        "def create_override(amount: int) -> None:\n"
        "    validate_override(amount)\n",
        encoding="utf-8",
    )
    (root / "domain" / "limit_rules.py").write_text(
        "def validate_override(amount: int) -> None:\n"
        "    return None\n",
        encoding="utf-8",
    )
    (root / "legacy" / "credit_limit_override.py").write_text(
        "def old_override(amount):\n"
        "    return amount\n",
        encoding="utf-8",
    )
    _git(root, "init", "-b", "main")
    _git(root, "config", "user.email", "discovered-safe@example.test")
    _git(root, "config", "user.name", "Discovered Safe Test")
    _git(root, "add", "-A")
    _git(root, "commit", "-m", "fixture")
    return root, _git(root, "rev-parse", "HEAD")


def _provider() -> FakeModelProvider:
    def discover(_request):
        return SolutionImpactPlan(
            summary="Use the active service and domain rule, not legacy code.",
            components=("services", "domain"),
            changes=(
                ImpactChange(
                    path="services/limit_service.py",
                    component="services",
                    confidence=ImpactConfidence.HIGH,
                    rationale="The active API imports this runtime service.",
                    evidence_paths=("apps/api/limits.py",),
                ),
                ImpactChange(
                    path="domain/limit_rules.py",
                    component="domain",
                    confidence=ImpactConfidence.HIGH,
                    rationale="The active runtime service imports this domain rule.",
                    evidence_paths=("services/limit_service.py",),
                ),
            ),
            rejected_candidates=("legacy/credit_limit_override.py",),
        ).model_dump(mode="json")

    return FakeModelProvider({"solution_discovery": discover})


def _policy() -> SafeModePolicy:
    return SafeModePolicy(
        profiles=(
            TestProfile(
                profile_id="active-contract",
                argv=(sys.executable, "-c", "print('fixed trusted profile')"),
            ),
        )
    )


def test_discovered_safe_stops_at_existing_scope_approval_before_implementation(
    tmp_path: Path,
    monkeypatch,
) -> None:
    source, source_sha = _repository(tmp_path)
    source_status = _git(source, "status", "--porcelain")
    state_root = tmp_path / "state"
    provider = _provider()
    monkeypatch.setenv("UCA_SAFE_EDIT_PROTOCOL", "v2-line-addressed")
    service = DiscoveredSafeAgentService.create(
        state_root,
        provider,
        allow_local_sources=True,
    )

    result = service.start(
        task_id="discovered-safe-task",
        thread_id="discovered-safe-thread",
        title="Discovered Safe",
        objective="Add the active customer credit-limit override validation.",
        repository=RepositorySpec(url=str(source), base_ref="main"),
        policy=_policy(),
        test_profiles=("active-contract",),
        acceptance_criteria=("Use the active service and domain rule only.",),
    )
    state = service.state("discovered-safe-thread")

    assert state["values"]["status"] == "awaiting_scope_approval"
    assert state["next"] == ["scope_approval"]
    assert state["values"].get("edit_proposal_ref") is None
    assert state["values"].get("patch_proposal_ref") is None
    manifest = state["values"]["task"]["manifest"]
    assert {item["path"] for item in manifest["allowed_changes"]} == {
        "services/limit_service.py",
        "domain/limit_rules.py",
    }
    assert manifest["test_profiles"] == ["active-contract"]
    assert result["base_sha"] == source_sha
    assert result["scope_hash"] == state["values"]["scope_hash"]
    assert _git(source, "rev-parse", "HEAD") == source_sha
    assert _git(source, "status", "--porcelain") == source_status == ""

    task_root = state_root / "artifacts" / "tasks" / "discovered-safe-task"
    assert (task_root / "solution-discovery-snapshot.json").is_file()
    assert (task_root / "solution-impact-plan.json").is_file()
    assert (task_root / "discovered-change-manifest.json").is_file()
    provenance = json.loads(
        (task_root / "solution-discovery-provenance.json").read_text(encoding="utf-8")
    )
    assert provenance["edit_authority_granted"] is False
    assert provenance["base_sha"] == source_sha
    assert [request.role for request in provider.requests] == ["solution_discovery"]


def test_discovered_safe_rejects_untrusted_test_profile_before_discovery(
    tmp_path: Path,
) -> None:
    source, _ = _repository(tmp_path)
    provider = _provider()
    service = DiscoveredSafeAgentService.create(
        tmp_path / "state",
        provider,
        allow_local_sources=True,
    )

    with pytest.raises(DiscoveredSafeStartError, match="not present in trusted policy"):
        service.start(
            task_id="unknown-profile-task",
            thread_id="unknown-profile-thread",
            title="Unknown profile",
            objective="Change active credit-limit behavior.",
            repository=RepositorySpec(url=str(source), base_ref="main"),
            policy=_policy(),
            test_profiles=("invented-profile",),
        )

    assert provider.requests == []
