from __future__ import annotations

from pathlib import Path
from threading import Event, Thread
from typing import Any

import pytest

from universal_coding_agent.core.models import RepositorySpec
from universal_coding_agent.core.safe_models import SafeModePolicy, TestProfile
from universal_coding_agent.product.models import (
    AcceptanceCriterion,
    ControlEntityType,
    ControlState,
    PhaseStatus,
    ProgramExecutionStatus,
    ProgramStatus,
    RequirementContract,
    RequirementItem,
    RequirementStatus,
)
from universal_coding_agent.product.program_orchestrator import ProgramExecutionError
from universal_coding_agent.product.workspace import ProductWorkspace
from universal_coding_agent.providers.fake import FakeModelProvider


class RecordingDiscoveredSafeExecutor:
    def __init__(self, *, final_status: str = "completed") -> None:
        self.final_status = final_status
        self.starts: list[dict[str, Any]] = []
        self.resumes: list[tuple[str, bool]] = []

    def start(self, **request: Any) -> dict[str, Any]:
        self.starts.append(request)
        return {
            "state": {
                "status": "awaiting_scope_approval",
                "scope_approved": None,
            },
            "provenance_ref": "artifact://tasks/discovery/provenance.json",
        }

    def resume(self, thread_id: str, approved: bool) -> dict[str, Any]:
        self.resumes.append((thread_id, approved))
        if not approved or self.final_status != "completed":
            return {
                "status": "blocked",
                "scope_approved": approved,
                "safe_errors": ["tests:failed"] if approved else [],
                "final_report_ref": "artifact://tasks/final-report.json",
            }
        return {
            "status": "completed",
            "base_sha": "a" * 40,
            "scope_approved": True,
            "reviewer_verdict": "PASS",
            "tests_ref": "artifact://tasks/test-results.json",
            "review_ref": "artifact://tasks/review.json",
            "final_report_ref": "artifact://tasks/final-report.json",
        }


class MissingBaseEvidenceExecutor(RecordingDiscoveredSafeExecutor):
    def resume(self, thread_id: str, approved: bool) -> dict[str, Any]:
        result = super().resume(thread_id, approved)
        result.pop("base_sha", None)
        return result


def _provider() -> FakeModelProvider:
    def program_planner(_request):
        return {
            "title": "Bounded delivery",
            "objective": "Deliver three ordered Safe execution units.",
            "phases": [
                {
                    "phase_id": "phase-1",
                    "title": "Foundation",
                    "objective": "Deliver the foundation safely.",
                    "dependencies": [],
                    "slices": [
                        {
                            "slice_id": "slice-1",
                            "title": "First bounded change",
                            "objective": "Implement the first bounded change.",
                            "dependencies": [],
                            "acceptance_criteria": ["The first contract passes."],
                        },
                        {
                            "slice_id": "slice-2",
                            "title": "Second bounded change",
                            "objective": "Implement the dependent bounded change.",
                            "dependencies": ["slice-1"],
                            "acceptance_criteria": ["The dependent contract passes."],
                        },
                    ],
                    "acceptance_criteria": ["Foundation checks pass."],
                },
                {
                    "phase_id": "phase-2",
                    "title": "Integration",
                    "objective": "Integrate only after the foundation passes.",
                    "dependencies": ["phase-1"],
                    "slices": [
                        {
                            "slice_id": "slice-3",
                            "title": "Integration change",
                            "objective": "Implement the integration change.",
                            "dependencies": [],
                        }
                    ],
                    "acceptance_criteria": ["Integration checks pass."],
                },
            ],
            "definition_of_done": ["Every Safe unit completes."],
        }

    return FakeModelProvider(handlers={"program_planner": program_planner})


def _requirement() -> RequirementContract:
    return RequirementContract(
        alignment_id="program-execution-requirement",
        version=1,
        title="Bounded program execution",
        objective="Execute an approved program through bounded Safe units.",
        requirements=(
            RequirementItem(
                requirement_id="R-001",
                statement="Every unit uses the existing Safe boundary.",
                category="safety",
            ),
        ),
        acceptance_criteria=(
            AcceptanceCriterion(
                criterion_id="AC-001",
                statement="Dependencies pass before a later unit starts.",
                requirement_ids=("R-001",),
            ),
        ),
        status=RequirementStatus.APPROVED,
    )


def _policy() -> SafeModePolicy:
    return SafeModePolicy(
        profiles=(
            TestProfile(
                profile_id="trusted-contract",
                argv=("python", "-m", "pytest", "-q"),
            ),
        )
    )


def _approved_workspace(tmp_path: Path) -> tuple[ProductWorkspace, str, str]:
    workspace = ProductWorkspace.create(tmp_path / "state", _provider())
    requirement = _requirement()
    requirement_hash = requirement.canonical_hash()
    plan = workspace.programs.create_program(
        program_id="program-execution",
        requirement=requirement,
        requirement_hash=requirement_hash,
    )
    workspace.programs.approve_program(plan.program_id, plan.canonical_hash())
    return workspace, plan.program_id, requirement_hash


def _start_next(
    workspace: ProductWorkspace,
    program_id: str,
    requirement_hash: str,
    executor: RecordingDiscoveredSafeExecutor,
):
    return workspace.programs.start_next_execution(
        program_id=program_id,
        current_requirement_hash=requirement_hash,
        repository=RepositorySpec(
            url="https://example.test/repository.git",
            base_ref="main",
        ),
        policy=_policy(),
        test_profiles=("trusted-contract",),
        executor=executor,
    )


def test_start_next_execution_is_single_unit_idempotent_and_durable(
    tmp_path: Path,
) -> None:
    workspace, program_id, requirement_hash = _approved_workspace(tmp_path)
    executor = RecordingDiscoveredSafeExecutor()
    try:
        binding = _start_next(workspace, program_id, requirement_hash, executor)
        repeated = _start_next(workspace, program_id, requirement_hash, executor)

        assert binding == repeated
        assert binding.phase_id == "phase-1"
        assert binding.slice_id == "slice-1"
        assert binding.requirement_hash == requirement_hash
        assert binding.status is ProgramExecutionStatus.AWAITING_SCOPE_APPROVAL
        assert len(executor.starts) == 1
        assert executor.starts[0]["objective"] == "Implement the first bounded change."
        assert executor.starts[0]["test_profiles"] == ("trusted-contract",)
        report = workspace.artifacts.read_json(binding.phase_report_ref)
        assert report["phase_id"] == "phase-1"
        assert report["bindings"][0]["task_id"] == binding.task_id
    finally:
        workspace.close()

    reopened = ProductWorkspace.create(tmp_path / "state", _provider())
    try:
        assert reopened.programs.execution_binding(binding.task_id) == binding
        assert reopened.programs.execution_bindings(program_id) == (binding,)
    finally:
        reopened.close()


def test_completed_safe_units_unlock_slices_and_dependent_phases(tmp_path: Path) -> None:
    workspace, program_id, requirement_hash = _approved_workspace(tmp_path)
    executor = RecordingDiscoveredSafeExecutor()
    try:
        first = _start_next(workspace, program_id, requirement_hash, executor)
        first = workspace.programs.continue_execution(
            program_id=program_id,
            task_id=first.task_id,
            current_requirement_hash=requirement_hash,
            executor=executor,
            approved=True,
        )
        assert first.status is ProgramExecutionStatus.COMPLETED
        assert workspace.programs.phase_status(program_id, "phase-1") is PhaseStatus.RUNNING

        second = _start_next(workspace, program_id, requirement_hash, executor)
        assert second.slice_id == "slice-2"
        second = workspace.programs.continue_execution(
            program_id=program_id,
            task_id=second.task_id,
            current_requirement_hash=requirement_hash,
            executor=executor,
            approved=True,
        )
        assert second.status is ProgramExecutionStatus.COMPLETED
        assert workspace.programs.phase_status(program_id, "phase-1") is PhaseStatus.COMPLETED

        third = _start_next(workspace, program_id, requirement_hash, executor)
        assert third.phase_id == "phase-2"
        assert third.slice_id == "slice-3"
        assert third.expected_base_sha == "a" * 40
        assert third.accepted_evidence_ref.startswith("artifact://programs/")
        assert len(third.accepted_evidence_hash) == 64
        accepted = executor.starts[-1]["accepted_evidence"]
        assert len(accepted) == 1
        assert accepted[0].source_ref == third.accepted_evidence_ref
        assert accepted[0].sha256 == third.accepted_evidence_hash
        assert executor.starts[-1]["expected_base_sha"] == "a" * 40
        evidence_payload = workspace.artifacts.read_json(third.accepted_evidence_ref)
        assert evidence_payload["target_phase_id"] == "phase-2"
        assert evidence_payload["dependency_phase_ids"] == ["phase-1"]
        assert evidence_payload["phases"][0]["reviewer_verdict"] == "PASS"
        assert len(evidence_payload["phases"][0]["result_sha256"]) == 64
        assert len(evidence_payload["phases"][0]["summary_sha256"]) == 64
        assert len(evidence_payload["phases"][0]["phase_report_sha256"]) == 64
        assert len(evidence_payload["phases"][0]["executions"]) == 2
        assert all(
            len(item["result_sha256"]) == 64
            for item in evidence_payload["phases"][0]["executions"]
        )
        assert [call["objective"] for call in executor.starts] == [
            "Implement the first bounded change.",
            "Implement the dependent bounded change.",
            "Implement the integration change.",
        ]
        report = workspace.artifacts.read_json(second.phase_report_ref)
        assert report["phase_status"] == "completed"
    finally:
        workspace.close()


def test_safe_failure_blocks_program_and_prevents_later_work(tmp_path: Path) -> None:
    workspace, program_id, requirement_hash = _approved_workspace(tmp_path)
    executor = RecordingDiscoveredSafeExecutor(final_status="blocked")
    try:
        binding = _start_next(workspace, program_id, requirement_hash, executor)
        failed = workspace.programs.continue_execution(
            program_id=program_id,
            task_id=binding.task_id,
            current_requirement_hash=requirement_hash,
            executor=executor,
            approved=True,
        )

        assert failed.status is ProgramExecutionStatus.FAILED
        assert workspace.programs.phase_status(program_id, "phase-1") is PhaseStatus.FAILED
        assert workspace.programs.status(program_id) is ProgramStatus.BLOCKED
        with pytest.raises(ProgramExecutionError, match="not running"):
            _start_next(workspace, program_id, requirement_hash, executor)
        assert len(executor.starts) == 1
    finally:
        workspace.close()


def test_dependent_phase_fails_closed_before_provider_when_evidence_is_incomplete(
    tmp_path: Path,
) -> None:
    workspace, program_id, requirement_hash = _approved_workspace(tmp_path)
    executor = MissingBaseEvidenceExecutor()
    try:
        for _ in range(2):
            binding = _start_next(workspace, program_id, requirement_hash, executor)
            workspace.programs.continue_execution(
                program_id=program_id,
                task_id=binding.task_id,
                current_requirement_hash=requirement_hash,
                executor=executor,
                approved=True,
            )

        with pytest.raises(ProgramExecutionError, match="evidence is invalid"):
            _start_next(workspace, program_id, requirement_hash, executor)

        assert len(executor.starts) == 2
        assert workspace.programs.phase_status(program_id, "phase-2") is PhaseStatus.PENDING
        assert len(workspace.programs.execution_bindings(program_id)) == 2
    finally:
        workspace.close()


def test_requirement_drift_pauses_bound_task_and_refuses_resume(tmp_path: Path) -> None:
    workspace, program_id, requirement_hash = _approved_workspace(tmp_path)
    executor = RecordingDiscoveredSafeExecutor()
    try:
        binding = _start_next(workspace, program_id, requirement_hash, executor)
        with pytest.raises(ProgramExecutionError, match="requirement realignment"):
            workspace.programs.continue_execution(
                program_id=program_id,
                task_id=binding.task_id,
                current_requirement_hash="b" * 64,
                executor=executor,
                approved=True,
            )

        assert workspace.programs.status(program_id) is ProgramStatus.REALIGNMENT_REQUIRED
        task_control = workspace.control.get_required(
            ControlEntityType.TASK,
            binding.task_id,
        )
        assert task_control.state is ControlState.PAUSE_REQUESTED
        assert executor.resumes == []
    finally:
        workspace.close()


def test_program_pause_and_cancel_prevent_new_execution(tmp_path: Path) -> None:
    workspace, program_id, requirement_hash = _approved_workspace(tmp_path)
    executor = RecordingDiscoveredSafeExecutor()
    try:
        workspace.programs.pause(program_id, reason="operator checkpoint")
        with pytest.raises(ProgramExecutionError, match="paused"):
            _start_next(workspace, program_id, requirement_hash, executor)
        assert executor.starts == []

        workspace.programs.resume(program_id)
        binding = _start_next(workspace, program_id, requirement_hash, executor)
        workspace.programs.cancel(program_id, reason="operator cancelled")

        assert workspace.programs.status(program_id) is ProgramStatus.CANCELLED
        assert workspace.programs.execution_binding(binding.task_id).status is (
            ProgramExecutionStatus.CANCELLED
        )
        task_control = workspace.control.get_required(
            ControlEntityType.TASK,
            binding.task_id,
        )
        assert task_control.state is ControlState.CANCEL_REQUESTED
        with pytest.raises(ProgramExecutionError, match="not running"):
            _start_next(workspace, program_id, requirement_hash, executor)
        assert len(executor.starts) == 1
    finally:
        workspace.close()


def test_workspace_connects_program_execution_to_discovered_safe_port(
    tmp_path: Path,
    monkeypatch,
) -> None:
    workspace, program_id, requirement_hash = _approved_workspace(tmp_path)
    executor = RecordingDiscoveredSafeExecutor()
    monkeypatch.setattr(workspace, "discovered_safe", lambda **_kwargs: executor)
    try:
        binding = workspace.start_next_program_execution(
            program_id=program_id,
            current_requirement_hash=requirement_hash,
            repository=RepositorySpec(
                url="https://example.test/repository.git",
                base_ref="main",
            ),
            policy=_policy(),
            test_profiles=("trusted-contract",),
        )
        completed = workspace.continue_program_execution(
            program_id=program_id,
            task_id=binding.task_id,
            current_requirement_hash=requirement_hash,
            approved=True,
        )

        assert binding.status is ProgramExecutionStatus.AWAITING_SCOPE_APPROVAL
        assert completed.status is ProgramExecutionStatus.COMPLETED
        assert executor.resumes == [(binding.thread_id, True)]
    finally:
        workspace.close()


def test_program_execution_rejects_untrusted_test_profile_before_binding(
    tmp_path: Path,
) -> None:
    workspace, program_id, requirement_hash = _approved_workspace(tmp_path)
    executor = RecordingDiscoveredSafeExecutor()
    try:
        with pytest.raises(ProgramExecutionError, match="trusted policy"):
            workspace.programs.start_next_execution(
                program_id=program_id,
                current_requirement_hash=requirement_hash,
                repository=RepositorySpec(
                    url="https://example.test/repository.git",
                    base_ref="main",
                ),
                policy=_policy(),
                test_profiles=("untrusted-profile",),
                executor=executor,
            )

        assert workspace.programs.execution_bindings(program_id) == ()
        assert workspace.programs.phase_status(program_id, "phase-1") is PhaseStatus.PENDING
        assert executor.starts == []
    finally:
        workspace.close()


def test_program_reads_share_the_execution_connection_lock(tmp_path: Path) -> None:
    workspace, program_id, requirement_hash = _approved_workspace(tmp_path)
    binding = _start_next(
        workspace,
        program_id,
        requirement_hash,
        RecordingDiscoveredSafeExecutor(),
    )
    started = Event()
    completed = Event()
    errors: list[BaseException] = []
    results: dict[str, Any] = {}

    def read_program_state() -> None:
        started.set()
        try:
            results["plan"] = workspace.programs.plan(program_id)
            results["status"] = workspace.programs.status(program_id)
            results["phase_status"] = workspace.programs.phase_status(
                program_id,
                "phase-1",
            )
            results["binding"] = workspace.programs.execution_binding(binding.task_id)
            results["bindings"] = workspace.programs.execution_bindings(program_id)
        except BaseException as exc:
            errors.append(exc)
        finally:
            completed.set()

    reader = Thread(target=read_program_state, daemon=True)
    try:
        with workspace.programs._lock:
            reader.start()
            assert started.wait(timeout=1)
            assert not completed.wait(timeout=0.1)

        reader.join(timeout=1)
        assert not reader.is_alive()
        assert errors == []
        assert results["plan"].program_id == program_id
        assert results["status"] is ProgramStatus.RUNNING
        assert results["phase_status"] is PhaseStatus.RUNNING
        assert results["binding"] == binding
        assert results["bindings"] == (binding,)
    finally:
        reader.join(timeout=1)
        workspace.close()
