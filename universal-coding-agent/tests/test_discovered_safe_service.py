from __future__ import annotations

import json
import re
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
from universal_coding_agent.product.models import (
    AcceptanceCriterion,
    PhaseStatus,
    ProgramExecutionStatus,
    ProgramStatus,
    RequirementContract,
    RequirementItem,
    RequirementStatus,
)
from universal_coding_agent.product.workspace import ProductWorkspace
from universal_coding_agent.providers.fake import FakeModelProvider
from universal_coding_agent.solution_discovery import (
    ImpactChange,
    ImpactConfidence,
    SolutionDiscoveryError,
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
        "def create_override(amount: int, expires_at: str) -> None:\n"
        "    validate_override(amount)\n",
        encoding="utf-8",
    )
    (root / "domain" / "limit_rules.py").write_text(
        "def validate_override(amount: int, expires_at: str) -> None:\n"
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


def _discovery_plan() -> dict:
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


def _provider() -> tuple[FakeModelProvider, list[str]]:
    calls: list[str] = []

    def discover(request):
        calls.append(request.role)
        return _discovery_plan()

    return FakeModelProvider({"solution_discovery": discover}), calls


def _full_provider() -> tuple[FakeModelProvider, list[str]]:
    calls: list[str] = []

    def discover(request):
        calls.append(request.role)
        return _discovery_plan()

    def implement(request):
        calls.append(request.role)
        target_path = str(request.metadata.get("target_path"))
        if target_path == "services/limit_service.py":
            assert (
                "def validate_override(amount: int, expires_at: str) -> None:"
                in request.user_prompt
            )
            address = _address_for_line(
                request.user_prompt,
                "    validate_override(amount)",
            )
            new_text = "    validate_override(amount, expires_at)\n"
        elif target_path == "domain/limit_rules.py":
            address = _address_for_line(request.user_prompt, "    return None")
            new_text = (
                "    if amount <= 0:\n"
                "        raise ValueError(\"amount must be positive\")\n"
            )
        else:
            raise AssertionError(f"unexpected implementer target: {target_path}")
        return {
            "summary": f"Implement approved contract in {target_path}.",
            "edits": [
                {
                    "path": target_path,
                    "operation": "modify",
                    "replacements": [
                        {
                            "old_text": f"@range:{address}..{address}",
                            "new_text": new_text,
                        }
                    ],
                    "content": None,
                }
            ],
            "requested_test_profiles": ["active-contract"],
            "assumptions": [],
        }

    def review(request):
        calls.append(request.role)
        return {
            "verdict": "PASS",
            "requirement_findings": [],
            "scope_findings": [],
            "security_findings": [],
            "test_findings": [],
            "required_actions": [],
            "confidence": "high",
        }

    return (
        FakeModelProvider(
            {
                "solution_discovery": discover,
                "implementer": implement,
                "reviewer": review,
            }
        ),
        calls,
    )


def _address_for_line(prompt: str, source_line: str) -> str:
    match = re.search(
        rf"(?m)^(A[0-9]{{6}}) \| {re.escape(source_line)}$",
        prompt,
    )
    if match is None:
        raise AssertionError(f"model line ref not found for: {source_line!r}")
    return match.group(1)


def _policy() -> SafeModePolicy:
    return SafeModePolicy(
        profiles=(
            TestProfile(
                profile_id="active-contract",
                argv=(sys.executable, "-c", "print('fixed trusted profile')"),
            ),
        )
    )


def _behavior_policy(tmp_path: Path) -> SafeModePolicy:
    checker = tmp_path / "active_contract_check.py"
    checker.write_text(
        "import os\n"
        "import sys\n\n"
        "sys.path.insert(0, os.getcwd())\n\n"
        "from domain.limit_rules import validate_override\n"
        "from services.limit_service import create_override\n\n"
        "create_override(5, '2027-01-01T00:00:00Z')\n"
        "try:\n"
        "    validate_override(0, '2027-01-01T00:00:00Z')\n"
        "except ValueError:\n"
        "    pass\n"
        "else:\n"
        "    raise AssertionError('non-positive amount must be rejected')\n",
        encoding="utf-8",
    )
    return SafeModePolicy(
        profiles=(
            TestProfile(
                profile_id="active-contract",
                argv=(sys.executable, str(checker)),
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
    provider, calls = _provider()
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
    assert calls == ["solution_discovery"]


def test_discovered_safe_completes_after_approval_with_dependency_contracts(
    tmp_path: Path,
    monkeypatch,
) -> None:
    source, source_sha = _repository(tmp_path)
    state_root = tmp_path / "state"
    provider, calls = _full_provider()
    monkeypatch.setenv("UCA_SAFE_EDIT_PROTOCOL", "v2-line-addressed")
    service = DiscoveredSafeAgentService.create(
        state_root,
        provider,
        allow_local_sources=True,
    )

    service.start(
        task_id="discovered-safe-e2e-task",
        thread_id="discovered-safe-e2e-thread",
        title="Discovered Safe end to end",
        objective=(
            "Use the active service and domain rule so credit-limit overrides validate both the "
            "amount and expires_at contract, and reject non-positive amounts."
        ),
        repository=RepositorySpec(url=str(source), base_ref="main"),
        policy=_behavior_policy(tmp_path),
        test_profiles=("active-contract",),
        acceptance_criteria=(
            "The service passes amount and expires_at to the active domain validator.",
            "The active domain validator rejects non-positive amounts.",
        ),
    )
    before = service.state("discovered-safe-e2e-thread")
    assert before["next"] == ["scope_approval"]
    assert before["values"].get("edit_proposal_ref") is None

    final = service.resume("discovered-safe-e2e-thread", True)
    task_root = state_root / "artifacts" / "tasks" / "discovered-safe-e2e-task"
    report = json.loads((task_root / "safe-final-report.json").read_text(encoding="utf-8"))
    tests = json.loads((task_root / "test-results.json").read_text(encoding="utf-8"))
    sandbox = state_root / "sandboxes" / "discovered-safe-e2e-task" / "repo"

    assert final["status"] == "completed"
    assert report["status"] == "completed"
    assert report["reviewer_verdict"] == "PASS"
    assert report["safe_errors"] == []
    assert report["source_repository_modified"] is False
    assert report["sandbox_patch_retained"] is True
    assert tests["scope_intact"] is True
    assert all(item["passed"] for item in tests["results"])
    assert "validate_override(amount, expires_at)" in (
        sandbox / "services" / "limit_service.py"
    ).read_text(encoding="utf-8")
    assert "amount <= 0" in (sandbox / "domain" / "limit_rules.py").read_text(
        encoding="utf-8"
    )
    assert _git(source, "rev-parse", "HEAD") == source_sha
    assert _git(source, "status", "--porcelain") == ""
    assert calls == [
        "solution_discovery",
        "implementer",
        "implementer",
        "reviewer",
    ]


def test_discovered_safe_persists_discovery_failure_diagnostics(
    tmp_path: Path,
    monkeypatch,
) -> None:
    source, source_sha = _repository(tmp_path)
    state_root = tmp_path / "state"
    calls: list[str] = []

    def invalid_discovery(request):
        calls.append(str(request.metadata.get("plan_validation_correction", "false")))
        return SolutionImpactPlan(
            summary="Return an invalid out-of-bound path.",
            components=("invented",),
            changes=(
                ImpactChange(
                    path="invented/not_real.py",
                    component="invented",
                    confidence=ImpactConfidence.LOW,
                    rationale="This must fail closed.",
                ),
            ),
        ).model_dump(mode="json")

    provider = FakeModelProvider({"solution_discovery": invalid_discovery})
    monkeypatch.setenv("UCA_SAFE_EDIT_PROTOCOL", "v2-line-addressed")
    service = DiscoveredSafeAgentService.create(
        state_root,
        provider,
        allow_local_sources=True,
    )

    with pytest.raises(SolutionDiscoveryError) as captured:
        service.start(
            task_id="discovered-safe-failure-task",
            thread_id="discovered-safe-failure-thread",
            title="Discovery failure diagnostics",
            objective="Use only the active credit-limit runtime path.",
            repository=RepositorySpec(url=str(source), base_ref="main"),
            policy=_policy(),
            test_profiles=("active-contract",),
        )

    assert captured.value.code == "plan_validation_failed"
    assert calls == ["false", "true"]
    failure_path = (
        state_root
        / "artifacts"
        / "tasks"
        / "discovered-safe-failure-task"
        / "solution-discovery-failure.json"
    )
    failure = json.loads(failure_path.read_text(encoding="utf-8"))
    assert failure["code"] == "plan_validation_failed"
    assert failure["edit_authority_granted"] is False
    assert failure["base_sha"] == source_sha
    assert all(item["passed"] for item in failure["read_only_checks"])
    assert failure["diagnostics"]["plan_validation_correction_used"] is True
    assert _git(source, "rev-parse", "HEAD") == source_sha
    assert _git(source, "status", "--porcelain") == ""


def test_discovered_safe_rejects_untrusted_test_profile_before_discovery(
    tmp_path: Path,
) -> None:
    source, _ = _repository(tmp_path)
    provider, calls = _provider()
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

    assert calls == []


def test_program_execution_uses_discovered_safe_end_to_end_and_preserves_source(
    tmp_path: Path,
    monkeypatch,
) -> None:
    source, source_sha = _repository(tmp_path)
    source_status = _git(source, "status", "--porcelain")
    provider, calls = _full_provider()
    workspace = ProductWorkspace.create(tmp_path / "workspace", provider)
    requirement = RequirementContract(
        alignment_id="discovered-safe-program",
        version=1,
        title="Validated credit-limit overrides",
        objective="Validate the active credit-limit override contract.",
        requirements=(
            RequirementItem(
                requirement_id="R-001",
                statement="The active override path validates amount and expiry.",
                category="functional",
            ),
        ),
        acceptance_criteria=(
            AcceptanceCriterion(
                criterion_id="AC-001",
                statement="The approved active contract test passes.",
                requirement_ids=("R-001",),
            ),
        ),
        status=RequirementStatus.APPROVED,
    )

    def program_planner(_request):
        return {
            "title": "Credit-limit override delivery",
            "objective": "Deliver the approved active-path change.",
            "phases": [
                {
                    "phase_id": "phase-1",
                    "title": "Active-path contract",
                    "objective": "Implement the approved active-path contract.",
                    "dependencies": [],
                    "slices": [
                        {
                            "slice_id": "slice-1",
                            "title": "Active-path implementation",
                            "objective": (
                                "Use the active service and domain rule so credit-limit "
                                "overrides validate amount and expires_at and reject "
                                "non-positive amounts."
                            ),
                            "dependencies": [],
                            "acceptance_criteria": [
                                "The active service passes amount and expires_at.",
                                "The active rule rejects non-positive amounts.",
                            ],
                        }
                    ],
                    "acceptance_criteria": ["The trusted active-contract profile passes."],
                }
            ],
            "definition_of_done": ["The independent reviewer returns PASS."],
        }

    workspace.programs.provider = FakeModelProvider(
        handlers={"program_planner": program_planner}
    )
    requirement_hash = requirement.canonical_hash()
    plan = workspace.programs.create_program(
        program_id="discovered-safe-program",
        requirement=requirement,
        requirement_hash=requirement_hash,
    )
    workspace.programs.approve_program(plan.program_id, plan.canonical_hash())
    monkeypatch.setenv("UCA_SAFE_EDIT_PROTOCOL", "v2-line-addressed")
    try:
        binding = workspace.start_next_program_execution(
            program_id=plan.program_id,
            current_requirement_hash=requirement_hash,
            repository=RepositorySpec(url=str(source), base_ref="main"),
            policy=_behavior_policy(tmp_path),
            test_profiles=("active-contract",),
            allow_local_sources=True,
        )
        assert binding.status is ProgramExecutionStatus.AWAITING_SCOPE_APPROVAL
        completed = workspace.continue_program_execution(
            program_id=plan.program_id,
            task_id=binding.task_id,
            current_requirement_hash=requirement_hash,
            approved=True,
            allow_local_sources=True,
        )

        assert completed.status is ProgramExecutionStatus.COMPLETED
        assert workspace.programs.phase_status(plan.program_id, "phase-1") is (
            PhaseStatus.COMPLETED
        )
        assert workspace.programs.status(plan.program_id) is ProgramStatus.COMPLETED
        report = workspace.artifacts.read_json(completed.phase_report_ref)
        assert report["phase_status"] == "completed"
        assert report["bindings"][0]["thread_id"] == completed.thread_id
        assert calls == ["solution_discovery", "implementer", "implementer", "reviewer"]
        assert _git(source, "rev-parse", "HEAD") == source_sha
        assert _git(source, "status", "--porcelain") == source_status == ""
    finally:
        workspace.close()
