from __future__ import annotations

import subprocess
import time
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from universal_coding_agent.core.safe_models import SafeModePolicy, TestProfile
from universal_coding_agent.product.models import (
    AcceptanceCriterion,
    PhaseStatus,
    ProgramStatus,
    RequirementContract,
    RequirementItem,
    RequirementStatus,
)
from universal_coding_agent.product.workspace import ProductWorkspace
from universal_coding_agent.providers.fake import FakeModelProvider
from universal_coding_agent.testlab.program_execution_live import (
    ProgramExecutionQualificationProvider,
)
from universal_coding_agent.web.app import ProductWebRuntime, create_product_app


class RecordingExecutionPort:
    def __init__(self, *, resume_status: str = "completed") -> None:
        self.resume_status = resume_status
        self.starts: list[dict[str, Any]] = []
        self.resumes: list[tuple[str, bool]] = []

    def start(self, **request: Any) -> dict[str, Any]:
        self.starts.append(request)
        return {"state": {"status": "awaiting_scope_approval"}}

    def resume(self, thread_id: str, approved: bool) -> dict[str, Any]:
        self.resumes.append((thread_id, approved))
        return {
            "status": self.resume_status,
            "scope_approved": approved,
            "reviewer_verdict": "PASS" if self.resume_status == "completed" else "FAIL",
            "final_report_ref": f"artifact://tasks/{thread_id}/safe-final-report.json",
        }


def _program_provider() -> FakeModelProvider:
    def program_planner(_request):
        return {
            "title": "Qualified multi-phase delivery",
            "objective": "Execute approved units in dependency order through Safe Mode.",
            "phases": [
                {
                    "phase_id": "phase-one",
                    "title": "Phase one",
                    "objective": "Complete the first approved delivery phase.",
                    "dependencies": [],
                    "slices": [
                        {
                            "slice_id": "slice-prepare",
                            "title": "Prepare contract",
                            "objective": "Prepare the first bounded contract change.",
                            "dependencies": [],
                            "acceptance_criteria": ["The preparation contract passes."],
                        },
                        {
                            "slice_id": "slice-apply",
                            "title": "Apply contract",
                            "objective": "Apply the second bounded contract change.",
                            "dependencies": ["slice-prepare"],
                            "acceptance_criteria": ["The application contract passes."],
                        },
                    ],
                    "acceptance_criteria": ["Every phase-one Safe unit passes."],
                },
                {
                    "phase_id": "phase-two",
                    "title": "Phase two",
                    "objective": "Complete the dependent delivery phase.",
                    "dependencies": ["phase-one"],
                    "slices": [
                        {
                            "slice_id": "slice-verify",
                            "title": "Verify contract",
                            "objective": "Verify the dependent bounded contract change.",
                            "dependencies": [],
                            "external_dependencies": [
                                "The durable phase-one report records successful completion."
                            ],
                            "acceptance_criteria": ["The verification contract passes."],
                        }
                    ],
                    "acceptance_criteria": ["The dependent Safe unit passes."],
                },
            ],
            "definition_of_done": [
                "Every phase report is durable and the source repository is preserved."
            ],
        }

    return FakeModelProvider(handlers={"program_planner": program_planner})


def _approved_program(workspace: ProductWorkspace, program_id: str) -> str:
    requirement = RequirementContract(
        alignment_id=f"{program_id}-requirement",
        version=1,
        title="Qualified Program execution",
        objective="Execute an approved multi-phase Program through explicit Safe checkpoints.",
        requirements=(
            RequirementItem(
                requirement_id="R-001",
                statement="Program units execute only after explicit operator actions.",
                category="safety",
            ),
        ),
        acceptance_criteria=(
            AcceptanceCriterion(
                criterion_id="AC-001",
                statement="Dependency order, durable reports, and safe stopping are preserved.",
                requirement_ids=("R-001",),
            ),
        ),
        status=RequirementStatus.APPROVED,
    )
    requirement_hash = requirement.canonical_hash()
    plan = workspace.programs.create_program(
        program_id=program_id,
        requirement=requirement,
        requirement_hash=requirement_hash,
    )
    workspace.programs.approve_program(program_id, plan.canonical_hash())
    return requirement_hash


def _policy() -> SafeModePolicy:
    return SafeModePolicy(
        profiles=(
            TestProfile(
                profile_id="qualified-contract",
                argv=("python", "-m", "pytest", "-q"),
            ),
        )
    )


def _execution_request(requirement_hash: str, source: Path) -> dict[str, Any]:
    return {
        "current_requirement_hash": requirement_hash,
        "repository": str(source),
        "ref": "main",
        "policy": _policy().model_dump(mode="json"),
        "test_profiles": ["qualified-contract"],
    }


def _wait_for_execution(
    client: TestClient,
    program_id: str,
    *,
    binding_count: int,
    binding_status: str | None = None,
    runtime_status: str | None = None,
) -> dict[str, Any]:
    for _ in range(300):
        response = client.get(f"/api/programs/{program_id}/executions")
        assert response.status_code == 200
        body = response.json()
        bindings = body["bindings"]
        binding_matches = binding_status is None or (
            len(bindings) == binding_count
            and bindings[-1]["status"] == binding_status
        )
        runtime_matches = runtime_status is None or (
            body["runtime"]["status"] == runtime_status
        )
        if (
            len(bindings) == binding_count
            and binding_matches
            and runtime_matches
            and not body["runtime"]["busy"]
        ):
            return body
        time.sleep(0.01)
    raise AssertionError(
        f"program execution did not reach bindings={binding_count}, "
        f"binding_status={binding_status}, runtime_status={runtime_status}"
    )


def _post_continue(
    client: TestClient,
    program_id: str,
    task_id: str,
    requirement_hash: str,
) -> None:
    response = client.post(
        f"/api/programs/{program_id}/executions/{task_id}/continue",
        json={
            "current_requirement_hash": requirement_hash,
            "approved": True,
        },
    )
    assert response.status_code == 202


def _git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _source_repository(root: Path) -> tuple[Path, str]:
    source = root / "source"
    source.mkdir()
    (source / "app.py").write_text("VALUE = 'unchanged'\n", encoding="utf-8")
    _git(source, "init", "-b", "main")
    _git(source, "config", "user.email", "program-qualification@example.test")
    _git(source, "config", "user.name", "Program Qualification")
    _git(source, "add", "app.py")
    _git(source, "commit", "-m", "fixture")
    return source, _git(source, "rev-parse", "HEAD")


def test_live_scope_selector_uses_only_the_requirement_section() -> None:
    prompt = (
        "# Requirement\n"
        "Change only features/alpha.py.\n\n"
        "# Repository summary\n"
        "Candidate decoy: features/beta.py\n"
    )

    assert ProgramExecutionQualificationProvider._target_path(prompt) == (
        "features/alpha.py"
    )


def test_multiphase_program_api_recovers_and_executes_dependency_order(
    tmp_path: Path,
) -> None:
    source, source_sha = _source_repository(tmp_path)
    product_root = tmp_path / "product"
    program_id = "program-multiphase-qualification"
    first_workspace = ProductWorkspace.create(product_root, _program_provider())
    requirement_hash = _approved_program(first_workspace, program_id)
    first_executor = RecordingExecutionPort()
    first_workspace.discovered_safe = lambda **_kwargs: first_executor  # type: ignore[method-assign]
    first_runtime = ProductWebRuntime(
        workspace=first_workspace,
        state_root=tmp_path / "runtime",
        allow_local_sources=True,
    )

    with TestClient(create_product_app(first_runtime)) as client:
        started = client.post(
            f"/api/programs/{program_id}/executions/start-next",
            json=_execution_request(requirement_hash, source),
        )
        assert started.status_code == 202
        awaiting = _wait_for_execution(
            client,
            program_id,
            binding_count=1,
            binding_status="awaiting_scope_approval",
        )
        first_binding = awaiting["bindings"][0]
        assert first_binding["phase_id"] == "phase-one"
        assert first_binding["slice_id"] == "slice-prepare"
        assert first_executor.resumes == []

    assert len(first_executor.starts) == 1
    reopened = ProductWorkspace.create(product_root, _program_provider())
    recovered_executor = RecordingExecutionPort()
    reopened.discovered_safe = lambda **_kwargs: recovered_executor  # type: ignore[method-assign]
    recovered_runtime = ProductWebRuntime(
        workspace=reopened,
        state_root=tmp_path / "runtime",
        allow_local_sources=True,
    )

    with TestClient(create_product_app(recovered_runtime)) as client:
        recovered = client.get(f"/api/programs/{program_id}/executions")
        assert recovered.status_code == 200
        recovered_body = recovered.json()
        assert recovered_body["runtime"]["recovered_pending"] is True
        assert recovered_body["runtime"]["requires_explicit_action"] is True
        assert recovered_executor.starts == []
        assert recovered_executor.resumes == []

        _post_continue(
            client,
            program_id,
            first_binding["task_id"],
            requirement_hash,
        )
        _wait_for_execution(
            client,
            program_id,
            binding_count=1,
            binding_status="completed",
        )

        for expected_count, expected_phase, expected_slice in (
            (2, "phase-one", "slice-apply"),
            (3, "phase-two", "slice-verify"),
        ):
            response = client.post(
                f"/api/programs/{program_id}/executions/start-next",
                json=_execution_request(requirement_hash, source),
            )
            assert response.status_code == 202
            next_unit = _wait_for_execution(
                client,
                program_id,
                binding_count=expected_count,
                binding_status="awaiting_scope_approval",
            )
            binding = next_unit["bindings"][-1]
            assert binding["phase_id"] == expected_phase
            assert binding["slice_id"] == expected_slice
            _post_continue(
                client,
                program_id,
                binding["task_id"],
                requirement_hash,
            )
            final = _wait_for_execution(
                client,
                program_id,
                binding_count=expected_count,
                binding_status="completed",
            )

        assert final["program_status"] == "completed"
        assert reopened.programs.status(program_id) is ProgramStatus.COMPLETED
        assert reopened.programs.phase_status(program_id, "phase-one") is (
            PhaseStatus.COMPLETED
        )
        assert reopened.programs.phase_status(program_id, "phase-two") is (
            PhaseStatus.COMPLETED
        )
        assert [item["phase_id"] for item in final["bindings"]] == [
            "phase-one",
            "phase-one",
            "phase-two",
        ]
        assert [item["slice_id"] for item in final["bindings"]] == [
            "slice-prepare",
            "slice-apply",
            "slice-verify",
        ]
        phase_refs = {
            item["phase_id"]: item["phase_report_ref"] for item in final["bindings"]
        }
        assert len(phase_refs) == 2
        assert len(set(phase_refs.values())) == 2
        phase_one_report = reopened.artifacts.read_json(phase_refs["phase-one"])
        phase_two_report = reopened.artifacts.read_json(phase_refs["phase-two"])
        assert phase_one_report["phase_status"] == "completed"
        assert phase_two_report["phase_status"] == "completed"
        assert len(phase_one_report["bindings"]) == 2
        assert len(phase_two_report["bindings"]) == 1

    assert len(recovered_executor.starts) == 2
    assert len(recovered_executor.resumes) == 3
    assert _git(source, "rev-parse", "HEAD") == source_sha
    assert _git(source, "status", "--porcelain") == ""


def test_program_api_stops_new_work_after_safe_failure_or_requirement_drift(
    tmp_path: Path,
) -> None:
    source, _ = _source_repository(tmp_path)
    workspace = ProductWorkspace.create(tmp_path / "product", _program_provider())
    failed_program = "program-safe-failure-qualification"
    drift_program = "program-drift-qualification"
    failed_hash = _approved_program(workspace, failed_program)
    drift_hash = _approved_program(workspace, drift_program)
    executor = RecordingExecutionPort(resume_status="failed")
    workspace.discovered_safe = lambda **_kwargs: executor  # type: ignore[method-assign]
    runtime = ProductWebRuntime(
        workspace=workspace,
        state_root=tmp_path / "runtime",
        allow_local_sources=True,
    )

    with TestClient(create_product_app(runtime)) as client:
        started = client.post(
            f"/api/programs/{failed_program}/executions/start-next",
            json=_execution_request(failed_hash, source),
        )
        assert started.status_code == 202
        awaiting = _wait_for_execution(
            client,
            failed_program,
            binding_count=1,
            binding_status="awaiting_scope_approval",
        )
        _post_continue(
            client,
            failed_program,
            awaiting["bindings"][0]["task_id"],
            failed_hash,
        )
        failed = _wait_for_execution(
            client,
            failed_program,
            binding_count=1,
            binding_status="failed",
        )
        assert failed["program_status"] == "blocked"
        assert workspace.programs.phase_status(failed_program, "phase-one") is (
            PhaseStatus.FAILED
        )

        rejected_new_work = client.post(
            f"/api/programs/{failed_program}/executions/start-next",
            json=_execution_request(failed_hash, source),
        )
        assert rejected_new_work.status_code == 202
        stopped = _wait_for_execution(
            client,
            failed_program,
            binding_count=1,
            binding_status="failed",
            runtime_status="failed",
        )
        assert stopped["runtime"]["error_type"] == "ProgramExecutionError"
        assert len(executor.starts) == 1
        assert len(executor.resumes) == 1

        drift_request = _execution_request("f" * 64, source)
        assert drift_request["current_requirement_hash"] != drift_hash
        drifted = client.post(
            f"/api/programs/{drift_program}/executions/start-next",
            json=drift_request,
        )
        assert drifted.status_code == 202
        drift_stopped = _wait_for_execution(
            client,
            drift_program,
            binding_count=0,
            runtime_status="failed",
        )
        assert drift_stopped["program_status"] == "realignment_required"
        assert drift_stopped["runtime"]["error_type"] == "ProgramExecutionError"
        assert workspace.programs.status(drift_program) is (
            ProgramStatus.REALIGNMENT_REQUIRED
        )
        assert len(executor.starts) == 1
        assert len(executor.resumes) == 1
