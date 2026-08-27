from __future__ import annotations

import hashlib
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Event
from typing import Any

import pytest
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
    RETAINED_LEASE_PROGRAM_ARTIFACT_MAX_BYTES,
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
    monkeypatch,
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

        original_record_disposition = (
            workspace.programs.record_remote_operation_disposition
        )
        disposition_attempts = 0

        def fail_first_program_disposition(disposition):
            nonlocal disposition_attempts
            disposition_attempts += 1
            if disposition_attempts == 1:
                raise ValueError("injected Program disposition persistence failure")
            return original_record_disposition(disposition)

        monkeypatch.setattr(
            workspace.programs,
            "record_remote_operation_disposition",
            fail_first_program_disposition,
        )
        disposition_payload = {
            "outcome": "failed",
            "reason": "Remote state is unavailable; termination is not inferred.",
            "confirmed": True,
        }
        partial_disposition = client.post(
            f"/api/tasks/{binding.task_id}/remote-operation/dispose",
            json=disposition_payload,
        )
        assert partial_disposition.status_code == 400
        assert workspace.control.remote_operation_disposition(binding.task_id) is not None
        partial_binding = workspace.programs.execution_binding(binding.task_id)
        assert partial_binding.status is ProgramExecutionStatus.AWAITING_SCOPE_APPROVAL
        assert not partial_binding.remote_disposition_ref

        disposed = client.post(
            f"/api/tasks/{binding.task_id}/remote-operation/dispose",
            json=disposition_payload,
        )
        assert disposed.status_code == 200
        assert disposition_attempts == 2
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

        workspace.artifacts.write_json(
            persisted.phase_report_ref.removeprefix("artifact://"),
            {**report, "bindings": []},
        )
        repaired_report_disposition = client.post(
            f"/api/tasks/{binding.task_id}/remote-operation/dispose",
            json=disposition_payload,
        )
        assert repaired_report_disposition.status_code == 200
        repaired_report = workspace.artifacts.read_json(persisted.phase_report_ref)
        assert any(
            item["task_id"] == binding.task_id
            and item["remote_disposition_ref"] == persisted.remote_disposition_ref
            for item in repaired_report["bindings"]
        )

        inventory = client.get("/api/remote-operations/retained-leases?limit=25")
        assert inventory.status_code == 200
        assert inventory.headers["cache-control"] == "no-store"
        inventory_body = inventory.json()
        assert inventory_body["provider_calls_made"] == 0
        assert inventory_body["mutations_made"] is False
        assert inventory_body["opaque_provider_identifiers_exposed"] is False
        assert inventory_body["returned_count"] == 1
        inventory_item = inventory_body["items"][0]
        assert inventory_item["task_id"] == binding.task_id
        assert inventory_item["program_id"] == program_id
        assert inventory_item["phase_id"] == binding.phase_id
        assert inventory_item["slice_id"] == (binding.slice_id or "")
        assert inventory_item["eligible_for_retirement"] is True
        assert inventory_item["eligibility_reasons"] == []
        assert response_id not in inventory.text
        assert binding.thread_id not in inventory.text

        runtime._program_execution_runs[program_id] = {
            "busy": True,
            "task_id": binding.task_id,
        }
        busy_inventory = client.get("/api/remote-operations/retained-leases")
        assert busy_inventory.status_code == 200
        assert {
            reason["code"]
            for reason in busy_inventory.json()["items"][0]["eligibility_reasons"]
        } == {"local_worker_active"}
        runtime._program_execution_runs.pop(program_id)

        runtime._begin_program_control_action(program_id)
        try:
            program_control_inventory = client.get(
                "/api/remote-operations/retained-leases"
            )
            assert program_control_inventory.status_code == 200
            assert {
                reason["code"]
                for reason in program_control_inventory.json()["items"][0][
                    "eligibility_reasons"
                ]
            } == {"lifecycle_action_active"}
            with pytest.raises(ValueError, match="Program control action"):
                runtime._begin_remote_operation_action(binding.task_id)
            retirement_blocked_by_program_control = client.post(
                f"/api/tasks/{binding.task_id}/remote-operation/retire",
                json={
                    "disposition_audit_ref": disposition["audit_ref"],
                    "reason": "Program control reservation must win this race.",
                    "confirmed": True,
                },
            )
            assert retirement_blocked_by_program_control.status_code == 400
            assert workspace.remote_operations.private_lease(binding.task_id) is not None
        finally:
            runtime._end_program_control_action(program_id)

        workspace.artifacts.write_json(
            persisted.phase_report_ref.removeprefix("artifact://"),
            [],
        )
        malformed_report_inventory = client.get(
            "/api/remote-operations/retained-leases"
        )
        assert malformed_report_inventory.status_code == 200
        assert {
            reason["code"]
            for reason in malformed_report_inventory.json()["items"][0][
                "eligibility_reasons"
            ]
        } == {"program_evidence_incomplete"}
        malformed_report_retirement = client.post(
            f"/api/tasks/{binding.task_id}/remote-operation/retire",
            json={
                "disposition_audit_ref": disposition["audit_ref"],
                "reason": "Malformed Program evidence must fail closed.",
                "confirmed": True,
            },
        )
        assert malformed_report_retirement.status_code == 400
        assert workspace.remote_operations.private_lease(binding.task_id) is not None
        workspace.artifacts.write_json(
            persisted.phase_report_ref.removeprefix("artifact://"),
            repaired_report,
        )

        oversized_padding = "x" * RETAINED_LEASE_PROGRAM_ARTIFACT_MAX_BYTES
        workspace.artifacts.write_json(
            persisted.remote_disposition_ref.removeprefix("artifact://"),
            {**artifact, "oversized_padding": oversized_padding},
        )
        oversized_disposition_inventory = client.get(
            "/api/remote-operations/retained-leases"
        )
        assert oversized_disposition_inventory.status_code == 200
        oversized_disposition_body = oversized_disposition_inventory.json()
        assert oversized_disposition_body["provider_calls_made"] == 0
        assert oversized_disposition_body["mutations_made"] is False
        assert oversized_disposition_body["opaque_provider_identifiers_exposed"] is False
        assert {
            reason["code"]
            for reason in oversized_disposition_body["items"][0][
                "eligibility_reasons"
            ]
        } == {"program_evidence_oversized"}
        assert response_id not in oversized_disposition_inventory.text
        oversized_disposition_retirement = client.post(
            f"/api/tasks/{binding.task_id}/remote-operation/retire",
            json={
                "disposition_audit_ref": disposition["audit_ref"],
                "reason": "Oversized Program disposition evidence must fail closed.",
                "confirmed": True,
            },
        )
        assert oversized_disposition_retirement.status_code == 400
        assert workspace.remote_operations.private_lease(binding.task_id) is not None
        assert workspace.remote_operations.retirement(binding.task_id) is None
        workspace.artifacts.write_json(
            persisted.remote_disposition_ref.removeprefix("artifact://"),
            artifact,
        )

        workspace.artifacts.write_json(
            persisted.phase_report_ref.removeprefix("artifact://"),
            {**repaired_report, "oversized_padding": oversized_padding},
        )
        oversized_report_inventory = client.get(
            "/api/remote-operations/retained-leases"
        )
        assert oversized_report_inventory.status_code == 200
        oversized_report_body = oversized_report_inventory.json()
        assert oversized_report_body["provider_calls_made"] == 0
        assert oversized_report_body["mutations_made"] is False
        assert oversized_report_body["opaque_provider_identifiers_exposed"] is False
        assert {
            reason["code"]
            for reason in oversized_report_body["items"][0][
                "eligibility_reasons"
            ]
        } == {"program_evidence_oversized"}
        assert response_id not in oversized_report_inventory.text
        oversized_report_retirement = client.post(
            f"/api/tasks/{binding.task_id}/remote-operation/retire",
            json={
                "disposition_audit_ref": disposition["audit_ref"],
                "reason": "Oversized Program phase evidence must fail closed.",
                "confirmed": True,
            },
        )
        assert oversized_report_retirement.status_code == 400
        assert workspace.remote_operations.private_lease(binding.task_id) is not None
        assert workspace.remote_operations.retirement(binding.task_id) is None
        workspace.artifacts.write_json(
            persisted.phase_report_ref.removeprefix("artifact://"),
            repaired_report,
        )

        control_before_retirement = workspace.control.get_task(binding.task_id)
        binding_before_retirement = workspace.programs.execution_binding(binding.task_id)
        phase_before_retirement = workspace.programs.phase_status(
            program_id,
            binding.phase_id,
        )
        program_before_retirement = workspace.programs.status(program_id)
        report_before_retirement = workspace.artifacts.read_json(
            binding_before_retirement.phase_report_ref
        )
        assert report_before_retirement == repaired_report
        starts_before_retirement = tuple(executor.starts)
        resumes_before_retirement = tuple(executor.resumes)
        workspace.programs.connection.execute(
            "UPDATE program_executions SET remote_disposition_ref = '' WHERE task_id = ?",
            (binding.task_id,),
        )
        workspace.programs.connection.commit()
        missing_program_evidence = client.post(
            f"/api/tasks/{binding.task_id}/remote-operation/retire",
            json={
                "disposition_audit_ref": disposition["audit_ref"],
                "reason": "Retirement requires complete Program disposition evidence.",
                "confirmed": True,
            },
        )
        assert missing_program_evidence.status_code == 400
        assert workspace.remote_operations.private_lease(binding.task_id) is not None
        workspace.programs.connection.execute(
            "UPDATE program_executions SET remote_disposition_ref = ? WHERE task_id = ?",
            (binding_before_retirement.remote_disposition_ref, binding.task_id),
        )
        workspace.programs.connection.commit()

        runtime._begin_remote_operation_action(binding.task_id)
        try:
            program_controls = (
                    (
                        "approve",
                        {
                            "plan_hash": workspace.programs.plan(
                                program_id
                            ).canonical_hash()
                        },
                ),
                ("pause", {"reason": "Overlapping pause must be rejected."}),
                ("resume", None),
                ("cancel", {"reason": "Overlapping cancel must be rejected."}),
            )
            for action, payload in program_controls:
                url = f"/api/programs/{program_id}/{action}"
                response = (
                    client.post(url, json=payload)
                    if payload is not None
                    else client.post(url)
                )
                assert response.status_code == 400
        finally:
            runtime._end_remote_operation_action(binding.task_id)

        validation_finished = Event()
        release_retirement = Event()
        original_validate_retirement = runtime._validate_program_retirement_evidence

        def hold_after_program_validation(
            disposition_model,
            *,
            artifact_max_bytes=None,
        ):
            assert artifact_max_bytes == RETAINED_LEASE_PROGRAM_ARTIFACT_MAX_BYTES
            result = original_validate_retirement(
                disposition_model,
                artifact_max_bytes=artifact_max_bytes,
            )
            validation_finished.set()
            if not release_retirement.wait(timeout=5):
                raise AssertionError("retirement qualification barrier timed out")
            return result

        monkeypatch.setattr(
            runtime,
            "_validate_program_retirement_evidence",
            hold_after_program_validation,
        )
        with ThreadPoolExecutor(max_workers=1) as pool:
            retirement_future = pool.submit(
                client.post,
                f"/api/tasks/{binding.task_id}/remote-operation/retire",
                json={
                    "disposition_audit_ref": disposition["audit_ref"],
                    "reason": "The closed Program task no longer needs its private lease.",
                    "confirmed": True,
                },
            )
            assert validation_finished.wait(timeout=5)
            concurrent_program_control = client.post(
                f"/api/programs/{program_id}/cancel",
                json={
                    "reason": "Program control must not cross lease retirement."
                },
            )
            assert concurrent_program_control.status_code == 400
            assert workspace.programs.status(program_id) is ProgramStatus.BLOCKED
            release_retirement.set()
            retired = retirement_future.result(timeout=5)
        monkeypatch.setattr(
            runtime,
            "_validate_program_retirement_evidence",
            original_validate_retirement,
        )
        assert retired.status_code == 200
        retirement = retired.json()["remote_operation_lease_retirement"]
        assert retirement["program_id"] == program_id
        assert retirement["phase_id"] == binding.phase_id
        assert retirement["disposition_audit_ref"] == disposition["audit_ref"]
        assert retirement["private_lease_rows_retired"] == 1
        assert retirement["provider_calls_made"] == 0
        assert retirement["task_outcome_changes_made"] == 0
        assert retirement["program_outcome_changes_made"] == 0
        assert workspace.remote_operations.private_lease(binding.task_id) is None
        assert workspace.control.get_task(binding.task_id) == control_before_retirement
        assert (
            workspace.programs.execution_binding(binding.task_id)
            == binding_before_retirement
        )
        assert (
            workspace.programs.phase_status(program_id, binding.phase_id)
            is phase_before_retirement
        )
        assert workspace.programs.status(program_id) is program_before_retirement
        assert (
            workspace.artifacts.read_json(binding_before_retirement.phase_report_ref)
            == report_before_retirement
        )
        after_retirement = client.get(f"/api/programs/{program_id}/executions")
        after_binding = after_retirement.json()["bindings"][0]
        assert "remote_operation" not in after_binding
        assert after_binding["remote_operation_disposition"] == disposition
        assert after_binding["remote_operation_lease_retirement"] == retirement
        assert response_id not in after_retirement.text
        assert tuple(executor.starts) == starts_before_retirement
        assert tuple(executor.resumes) == resumes_before_retirement

        empty_inventory = client.get("/api/remote-operations/retained-leases")
        assert empty_inventory.status_code == 200
        assert empty_inventory.json()["items"] == []
        assert empty_inventory.json()["returned_count"] == 0

        repeated_disposition = client.post(
            f"/api/tasks/{binding.task_id}/remote-operation/dispose",
            json=disposition_payload,
        )
        assert repeated_disposition.status_code == 200
        assert repeated_disposition.json()["remote_operation_disposition"] == disposition
        assert workspace.remote_operations.private_lease(binding.task_id) is None

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


def test_runtime_lifecycle_reservations_serialize_across_reopened_workspaces(
    tmp_path: Path,
) -> None:
    product_root = tmp_path / "product"
    first_workspace = ProductWorkspace.create(product_root, _provider())
    program_id = "program-cross-runtime-reservation"
    requirement_hash = _approved_program(first_workspace, program_id)
    binding = first_workspace.programs.start_next_execution(
        program_id=program_id,
        current_requirement_hash=requirement_hash,
        repository=RepositorySpec(
            url="https://example.test/repository.git",
            base_ref="main",
        ),
        policy=_policy(),
        test_profiles=("trusted-contract",),
        executor=RecordingProgramExecutor(),
    )
    first_runtime = ProductWebRuntime(
        workspace=first_workspace,
        state_root=tmp_path / "runtime-first",
    )
    second_workspace = ProductWorkspace.create(product_root, _provider())
    second_runtime = ProductWebRuntime(
        workspace=second_workspace,
        state_root=tmp_path / "runtime-second",
    )

    try:
        first_runtime._begin_remote_operation_action(binding.task_id)
        with pytest.raises(ValueError, match="remote-operation lifecycle action"):
            second_runtime._begin_program_control_action(program_id)
        first_runtime._end_remote_operation_action(binding.task_id)

        second_runtime._begin_program_control_action(program_id)
        with pytest.raises(ValueError, match="Program control action"):
            first_runtime._begin_remote_operation_action(binding.task_id)
        second_runtime._end_program_control_action(program_id)
    finally:
        first_runtime.close()
        second_runtime.close()
