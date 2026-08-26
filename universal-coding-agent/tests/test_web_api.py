from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from universal_coding_agent.core.models import RepositorySpec
from universal_coding_agent.core.remote_operations import RemoteOperationState
from universal_coding_agent.core.safe_models import SafeModePolicy, TestProfile
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
from universal_coding_agent.web.app import (
    ProductWebRuntime,
    create_product_app,
    is_loopback_host,
)


class RecordingProgramExecutor:
    def __init__(self) -> None:
        self.starts: list[dict[str, Any]] = []
        self.resumes: list[tuple[str, bool]] = []

    def start(self, **request: Any) -> dict[str, Any]:
        self.starts.append(request)
        return {"state": {"status": "awaiting_scope_approval"}}

    def resume(self, thread_id: str, approved: bool) -> dict[str, Any]:
        self.resumes.append((thread_id, approved))
        return {
            "status": "completed",
            "base_sha": "d" * 40,
            "scope_approved": approved,
            "reviewer_verdict": "PASS",
            "tests_ref": "artifact://tasks/program/test-results.json",
            "review_ref": "artifact://tasks/program/safe-review.json",
            "final_report_ref": "artifact://tasks/program/final-report.json",
        }


def _provider() -> FakeModelProvider:
    def requirement_alignment(request):
        answered = '"authorization_role": "manager"' in request.user_prompt
        return {
            "title": "Customer export",
            "objective": "Create a governed customer export.",
            "requirements": [
                {
                    "statement": "Authorized users can export active customers.",
                    "category": "functional",
                    "evidence_refs": [],
                }
            ],
            "acceptance_criteria": [
                {
                    "statement": "Only authorized users can export active customers.",
                    "requirement_indexes": [0],
                }
            ],
            "constraints": [],
            "exclusions": [],
            "assumptions": [],
            "clarifications": []
            if answered
            else [
                {
                    "decision_key": "authorization_role",
                    "question": "Which role may export customers?",
                    "severity": "blocking",
                    "rationale": "The role defines a security boundary.",
                    "options": ["manager", "analyst"],
                    "recommended_answer": "",
                    "evidence_refs": [],
                }
            ],
        }

    def program_planner(_request):
        return {
            "title": "Customer export delivery",
            "objective": "Deliver the approved export safely.",
            "phases": [
                {
                    "phase_id": "phase-1",
                    "title": "Authorization and export",
                    "objective": (
                        "Implement the approved authorization and export contract."
                    ),
                    "dependencies": [],
                    "slices": [],
                    "acceptance_criteria": [
                        "Approved authorization behavior is tested."
                    ],
                    "stop_conditions": ["Authorization evidence changes."],
                    "expected_components": ["security", "service", "tests"],
                }
            ],
            "definition_of_done": ["Acceptance criteria pass."],
        }

    return FakeModelProvider(
        handlers={
            "requirement_alignment": requirement_alignment,
            "program_planner": program_planner,
        }
    )


def _client(tmp_path):
    workspace = ProductWorkspace.create(tmp_path / "product", _provider())
    runtime = ProductWebRuntime(
        workspace=workspace,
        state_root=tmp_path / "runtime",
    )
    return TestClient(create_product_app(runtime))


def _policy() -> SafeModePolicy:
    return SafeModePolicy(
        profiles=(
            TestProfile(
                profile_id="trusted-contract",
                argv=("python", "-m", "pytest", "-q"),
            ),
        )
    )


def _approved_program(workspace: ProductWorkspace, program_id: str) -> str:
    requirement = RequirementContract(
        alignment_id=f"{program_id}-requirement",
        version=1,
        title="Program execution API",
        objective="Execute one approved program unit through Safe Mode.",
        requirements=(
            RequirementItem(
                requirement_id="R-001",
                statement="Execution requires an explicit API action.",
                category="safety",
            ),
        ),
        acceptance_criteria=(
            AcceptanceCriterion(
                criterion_id="AC-001",
                statement="Restart recovery does not start provider work.",
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


def _program_execution_request(requirement_hash: str) -> dict[str, Any]:
    return {
        "current_requirement_hash": requirement_hash,
        "repository": "https://example.test/repository.git",
        "ref": "main",
        "policy": _policy().model_dump(mode="json"),
        "test_profiles": ["trusted-contract"],
    }


def _wait_for_program_execution(
    client: TestClient,
    program_id: str,
    expected_status: str,
) -> dict[str, Any]:
    for _ in range(200):
        response = client.get(f"/api/programs/{program_id}/executions")
        assert response.status_code == 200
        body = response.json()
        bindings = body["bindings"]
        if (
            bindings
            and bindings[-1]["status"] == expected_status
            and not body["runtime"]["busy"]
        ):
            return body
        time.sleep(0.01)
    raise AssertionError(f"program execution did not reach {expected_status}")


def test_health_document_upload_and_search(tmp_path) -> None:
    with _client(tmp_path) as client:
        health = client.get("/api/health")
        assert health.status_code == 200
        assert health.json()["browser_credentials"] is False

        uploaded = client.post(
            "/api/documents",
            json={
                "document_id": "product-order-001",
                "filename": "product-order.md",
                "content": "Export active customers and emit one audit event.",
                "role": "requirement",
                "scope": "program",
                "scope_id": "program-export",
            },
        )
        assert uploaded.status_code == 201
        assert uploaded.json()["role"] == "requirement"

        search = client.post(
            "/api/search",
            json={"query": "audit event", "top_k": 10},
        )
        assert search.status_code == 200
        assert search.json()["hits"][0]["path"] == "product-order.md"

        documents = client.get(
            "/api/documents",
            params={"scope_id": "program-export"},
        )
        assert documents.status_code == 200
        assert len(documents.json()["documents"]) == 1


def test_requirement_program_and_program_controls_are_api_backed(tmp_path) -> None:
    with _client(tmp_path) as client:
        first = client.post(
            "/api/requirements/analyze",
            json={
                "alignment_id": "customer-export",
                "title": "Customer export",
                "objective": "Add customer export with authorization.",
                "answers": {},
            },
        )
        assert first.status_code == 200
        first_body = first.json()
        assert first_body["contract"]["status"] == "needs_clarification"
        clarification = first_body["contract"]["clarifications"][0]
        assert clarification["decision_key"] == "authorization_role"

        aligned = client.post(
            "/api/requirements/analyze",
            json={
                "alignment_id": "customer-export",
                "title": "Customer export",
                "objective": "Add customer export with authorization.",
                "answers": {"authorization_role": "manager"},
                "previous": first_body["contract"],
            },
        )
        assert aligned.status_code == 200
        aligned_body = aligned.json()
        assert aligned_body["contract"]["status"] == "ready_for_approval"

        approved = client.post(
            "/api/requirements/approve",
            json={"contract": aligned_body["contract"]},
        )
        assert approved.status_code == 200
        approved_body = approved.json()
        assert approved_body["contract"]["status"] == "approved"

        created = client.post(
            "/api/programs",
            json={
                "program_id": "program-customer-export",
                "requirement": approved_body["contract"],
                "requirement_hash": approved_body["requirement_hash"],
            },
        )
        assert created.status_code == 201
        created_body = created.json()
        assert created_body["status"] == "awaiting_approval"

        approved_program = client.post(
            "/api/programs/program-customer-export/approve",
            json={"plan_hash": created_body["plan_hash"]},
        )
        assert approved_program.status_code == 200
        assert approved_program.json()["status"] == "running"

        paused = client.post(
            "/api/programs/program-customer-export/pause",
            json={"reason": "operator review"},
        )
        assert paused.status_code == 200
        assert paused.json()["status"] == "paused"

        resumed = client.post(
            "/api/programs/program-customer-export/resume"
        )
        assert resumed.status_code == 200
        assert resumed.json()["status"] == "running"

        cancelled = client.post(
            "/api/programs/program-customer-export/cancel",
            json={"reason": "operator cancelled delivery"},
        )
        assert cancelled.status_code == 200
        assert cancelled.json()["status"] == "cancelled"


def test_program_execution_api_requires_explicit_start_and_continue(
    tmp_path: Path,
    monkeypatch,
) -> None:
    workspace = ProductWorkspace.create(tmp_path / "product", _provider())
    program_id = "program-api-execution"
    requirement_hash = _approved_program(workspace, program_id)
    executor = RecordingProgramExecutor()
    monkeypatch.setattr(workspace, "discovered_safe", lambda **_kwargs: executor)
    runtime = ProductWebRuntime(
        workspace=workspace,
        state_root=tmp_path / "runtime",
    )

    with TestClient(create_product_app(runtime)) as client:
        initial = client.get(f"/api/programs/{program_id}/executions")
        assert initial.status_code == 200
        assert initial.json()["bindings"] == []
        assert initial.json()["runtime"]["requires_explicit_action"] is False
        assert executor.starts == []

        invalid = _program_execution_request(requirement_hash)
        invalid["test_profiles"] = []
        rejected = client.post(
            f"/api/programs/{program_id}/executions/start-next",
            json=invalid,
        )
        assert rejected.status_code == 422
        assert executor.starts == []

        started = client.post(
            f"/api/programs/{program_id}/executions/start-next",
            json=_program_execution_request(requirement_hash),
        )
        assert started.status_code == 202
        awaiting = _wait_for_program_execution(
            client,
            program_id,
            "awaiting_scope_approval",
        )
        binding = awaiting["bindings"][0]
        assert awaiting["runtime"]["requires_explicit_action"] is True
        assert awaiting["runtime"]["recovered_pending"] is False
        assert len(executor.starts) == 1
        assert executor.resumes == []

        continued = client.post(
            (
                f"/api/programs/{program_id}/executions/"
                f"{binding['task_id']}/continue"
            ),
            json={
                "current_requirement_hash": requirement_hash,
                "approved": True,
            },
        )
        assert continued.status_code == 202
        completed = _wait_for_program_execution(client, program_id, "completed")
        assert completed["program_status"] == "completed"
        assert completed["runtime"]["requires_explicit_action"] is False
        assert executor.resumes == [(binding["thread_id"], True)]
        assert completed["bindings"][0]["phase_report_ref"].endswith(
            "/phase-execution-report.json"
        )

        terminal = client.post(
            (
                f"/api/programs/{program_id}/executions/"
                f"{binding['task_id']}/continue"
            ),
            json={
                "current_requirement_hash": requirement_hash,
                "approved": True,
            },
        )
        assert terminal.status_code == 400


def test_program_execution_api_recovers_binding_without_automatic_work(
    tmp_path: Path,
    monkeypatch,
) -> None:
    product_root = tmp_path / "product"
    first_workspace = ProductWorkspace.create(product_root, _provider())
    program_id = "program-api-restart"
    requirement_hash = _approved_program(first_workspace, program_id)
    first_executor = RecordingProgramExecutor()
    binding = first_workspace.programs.start_next_execution(
        program_id=program_id,
        current_requirement_hash=requirement_hash,
        repository=RepositorySpec(
            url="https://example.test/repository.git",
            base_ref="main",
        ),
        policy=_policy(),
        test_profiles=("trusted-contract",),
        executor=first_executor,
    )
    first_workspace.close()
    assert len(first_executor.starts) == 1

    reopened = ProductWorkspace.create(product_root, _provider())
    recovered_executor = RecordingProgramExecutor()
    monkeypatch.setattr(
        reopened,
        "discovered_safe",
        lambda **_kwargs: recovered_executor,
    )
    runtime = ProductWebRuntime(
        workspace=reopened,
        state_root=tmp_path / "runtime",
    )

    with TestClient(create_product_app(runtime)) as client:
        recovered = client.get(f"/api/programs/{program_id}/executions")
        assert recovered.status_code == 200
        recovered_body = recovered.json()
        assert recovered_body["bindings"][0]["task_id"] == binding.task_id
        assert recovered_body["runtime"]["recovered_pending"] is True
        assert recovered_body["runtime"]["requires_explicit_action"] is True
        assert recovered_executor.starts == []
        assert recovered_executor.resumes == []

        idempotent_start = client.post(
            f"/api/programs/{program_id}/executions/start-next",
            json=_program_execution_request(requirement_hash),
        )
        assert idempotent_start.status_code == 202
        still_awaiting = _wait_for_program_execution(
            client,
            program_id,
            "awaiting_scope_approval",
        )
        assert still_awaiting["bindings"][0]["task_id"] == binding.task_id
        assert recovered_executor.starts == []
        assert recovered_executor.resumes == []

        explicit_continue = client.post(
            (
                f"/api/programs/{program_id}/executions/"
                f"{binding.task_id}/continue"
            ),
            json={
                "current_requirement_hash": requirement_hash,
                "approved": True,
            },
        )
        assert explicit_continue.status_code == 202
        completed = _wait_for_program_execution(client, program_id, "completed")
        assert completed["program_status"] == "completed"
        assert recovered_executor.resumes == [(binding.thread_id, True)]


def test_program_execution_binding_exposes_only_redacted_remote_operation(
    tmp_path: Path,
) -> None:
    workspace = ProductWorkspace.create(tmp_path / "product", _provider())
    program_id = "program-api-remote-recovery"
    requirement_hash = _approved_program(workspace, program_id)
    executor = RecordingProgramExecutor()
    binding = workspace.programs.start_next_execution(
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
    response_id = "resp_private_program_binding"
    endpoint = "https://example.test/v1/responses"
    workspace.remote_operations.register(
        task_id=binding.task_id,
        thread_id=binding.thread_id,
        transport="openai_responses",
        transport_scope=(
            "sha256:" + hashlib.sha256(endpoint.encode("utf-8")).hexdigest()
        ),
        operation_id=response_id,
        base_sha="d" * 40,
        status="in_progress",
        state=RemoteOperationState.ACTIVE,
    )
    runtime = ProductWebRuntime(
        workspace=workspace,
        state_root=tmp_path / "runtime",
    )

    with TestClient(create_product_app(runtime)) as client:
        recovered = client.get(f"/api/programs/{program_id}/executions")
        assert recovered.status_code == 200
        remote = recovered.json()["bindings"][0]["remote_operation"]
        assert remote["state"] == "active"
        assert remote["recovered_pending"] is True
        assert remote["requires_explicit_action"] is True
        assert remote["requires_explicit_disposition"] is False
        assert response_id not in recovered.text

        active_disposition = client.post(
            f"/api/tasks/{binding.task_id}/remote-operation/dispose",
            json={
                "outcome": "failed",
                "reason": "Interrupted Program binding requires explicit closure.",
                "confirmed": True,
            },
        )
        assert active_disposition.status_code == 400

        workspace.remote_operations.mark_unavailable(binding.task_id)
        terminal = client.get(f"/api/programs/{program_id}/executions")
        terminal_remote = terminal.json()["bindings"][0]["remote_operation"]
        assert terminal_remote["state"] == "unavailable"
        assert terminal_remote["requires_explicit_disposition"] is True

        runtime._program_execution_runs[program_id] = {
            "busy": True,
            "task_id": binding.task_id,
        }
        busy_disposition = client.post(
            f"/api/tasks/{binding.task_id}/remote-operation/dispose",
            json={
                "outcome": "failed",
                "reason": "Program worker is still active.",
                "confirmed": True,
            },
        )
        assert busy_disposition.status_code == 400
        runtime._program_execution_runs.pop(program_id)

        disposed = client.post(
            f"/api/tasks/{binding.task_id}/remote-operation/dispose",
            json={
                "outcome": "failed",
                "reason": "Remote state is unavailable; termination is not inferred.",
                "confirmed": True,
            },
        )
        assert disposed.status_code == 200
        disposition = disposed.json()["remote_operation_disposition"]
        assert disposition["program_id"] == program_id
        assert disposition["phase_id"] == binding.phase_id
        assert disposition["provider_confirmed_cancelled"] is False
        assert disposition["provider_calls_made"] == 0

        final = client.get(f"/api/programs/{program_id}/executions")
        final_body = final.json()
        final_binding = final_body["bindings"][0]
        assert final_body["program_status"] == "blocked"
        assert final_body["runtime"]["requires_explicit_action"] is False
        assert final_binding["status"] == "failed"
        assert final_binding["control"]["state"] == "failed"
        assert final_binding["remote_disposition_ref"].startswith("artifact://")
        assert final_binding["remote_operation_disposition"] == disposition
        assert (
            final_binding["remote_operation"]["requires_explicit_disposition"]
            is False
        )
        assert response_id not in final.text
        assert executor.resumes == []

        persisted = workspace.programs.execution_binding(binding.task_id)
        assert persisted.status is ProgramExecutionStatus.FAILED
        assert persisted.remote_disposition_ref.startswith("artifact://")
        assert workspace.programs.phase_status(
            program_id,
            binding.phase_id,
        ) is PhaseStatus.FAILED
        assert workspace.programs.status(program_id) is ProgramStatus.BLOCKED
        artifact = workspace.artifacts.read_json(persisted.remote_disposition_ref)
        assert artifact["audit_ref"] == disposition["audit_ref"]
        report = workspace.artifacts.read_json(persisted.phase_report_ref)
        assert report["phase_status"] == "failed"
        assert report["program_status"] == "blocked"

        blocked_continue = client.post(
            f"/api/programs/{program_id}/executions/{binding.task_id}/continue",
            json={
                "current_requirement_hash": requirement_hash,
                "approved": True,
            },
        )
        assert blocked_continue.status_code == 400
        assert executor.resumes == []


def test_unknown_task_control_is_not_silently_created(tmp_path) -> None:
    with _client(tmp_path) as client:
        response = client.post(
            "/api/tasks/unknown-task/pause",
            json={"reason": "test"},
        )
        assert response.status_code == 404


def test_ui_binding_is_loopback_by_default() -> None:
    assert is_loopback_host("127.0.0.1")
    assert is_loopback_host("::1")
    assert is_loopback_host("localhost")
    assert not is_loopback_host("0.0.0.0")
    assert not is_loopback_host("192.168.1.25")
