from __future__ import annotations

from fastapi.testclient import TestClient

from universal_coding_agent.product.workspace import ProductWorkspace
from universal_coding_agent.providers.fake import FakeModelProvider
from universal_coding_agent.web.app import (
    ProductWebRuntime,
    create_product_app,
    is_loopback_host,
)


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
