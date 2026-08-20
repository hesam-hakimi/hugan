from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from universal_coding_agent.core.models import ProjectFile, ProjectManifest
from universal_coding_agent.product.context_documents import DocumentValidationError
from universal_coding_agent.product.models import (
    ContextScope,
    ControlAction,
    ControlEntityType,
    ControlState,
    DocumentRole,
    PhaseResult,
    ProgramStatus,
    RequirementStatus,
)
from universal_coding_agent.product.workspace import ProductWorkspace
from universal_coding_agent.providers.fake import FakeModelProvider


def _provider() -> FakeModelProvider:
    def requirement_alignment(request):
        answered = "manager-only" in request.user_prompt
        return {
            "title": "Customer export",
            "objective": "Add a governed customer export.",
            "requirements": [
                {
                    "statement": "Authorized users can export active customers.",
                    "category": "functional",
                    "evidence_refs": ["services/customer_export.py"],
                },
                {
                    "statement": "Every successful export is audited.",
                    "category": "security",
                    "evidence_refs": ["audit/activity_log.py"],
                },
            ],
            "acceptance_criteria": [
                {
                    "statement": "An authorized export returns active customers only.",
                    "requirement_indexes": [0],
                },
                {
                    "statement": "A successful export emits exactly one audit event.",
                    "requirement_indexes": [1],
                },
            ],
            "constraints": ["Preserve existing public API contracts."],
            "exclusions": ["Do not change legacy export jobs."],
            "assumptions": [],
            "clarifications": []
            if answered
            else [
                {
                    "decision_key": "authorization_role",
                    "question": "Which role may export customers?",
                    "severity": "blocking",
                    "rationale": "Authorization behavior changes the security boundary.",
                    "options": ["manager-only", "all-authenticated"],
                    "recommended_answer": "manager-only",
                    "evidence_refs": ["security/entitlements.py"],
                }
            ],
        }

    def program_planner(_request):
        return {
            "title": "Customer export delivery",
            "objective": "Deliver the approved governed customer export in phases.",
            "phases": [
                {
                    "phase_id": "phase-1",
                    "title": "Authorization and contract",
                    "objective": "Implement and verify the authorization boundary.",
                    "dependencies": [],
                    "acceptance_criteria": ["Unauthorized callers are rejected."],
                    "stop_conditions": ["Authorization evidence is missing."],
                    "expected_components": ["security", "service"],
                },
                {
                    "phase_id": "phase-2",
                    "title": "Export and audit",
                    "objective": "Implement export behavior and auditing.",
                    "dependencies": ["phase-1"],
                    "acceptance_criteria": ["Export and audit tests pass."],
                    "stop_conditions": [],
                    "expected_components": ["service", "audit", "tests"],
                },
            ],
            "definition_of_done": [
                "All acceptance criteria pass.",
                "Reviewer returns PASS.",
            ],
        }

    return FakeModelProvider(
        handlers={
            "requirement_alignment": requirement_alignment,
            "program_planner": program_planner,
        }
    )


def _manifest(root: Path) -> ProjectManifest:
    files = []
    for relative in ("services/customer_export.py", "security/entitlements.py"):
        data = (root / relative).read_bytes()
        files.append(
            ProjectFile(
                path=relative,
                size=len(data),
                sha256=hashlib.sha256(data).hexdigest(),
                language="python",
                symbols=("FunctionDef:export_customers:1",),
                imports=("security.entitlements:require_export_permission",),
            )
        )
    return ProjectManifest(
        repository_url="https://example.test/repository.git",
        base_ref="main",
        base_sha="a" * 40,
        files=tuple(files),
        language_counts={"python": 2},
    )


def test_text_documents_are_immutable_searchable_and_role_scoped(tmp_path: Path) -> None:
    workspace = ProductWorkspace.create(tmp_path / "state", _provider())
    try:
        document = workspace.upload_document(
            document_id="product-order-001",
            filename="product-order.md",
            content="# Export\nOnly active customers should be exported.\n",
            role=DocumentRole.REQUIREMENT,
            scope=ContextScope.PROGRAM,
            scope_id="program-export",
        )
        assert document.role is DocumentRole.REQUIREMENT
        hits = workspace.search.search("active customers")
        assert hits
        assert hits[0].metadata["role"] == "requirement"
        with pytest.raises(DocumentValidationError, match="already exists"):
            workspace.upload_document(
                document_id="product-order-001",
                filename="product-order.md",
                content="replacement",
                role=DocumentRole.REQUIREMENT,
                scope=ContextScope.PROGRAM,
                scope_id="program-export",
            )
        with pytest.raises(DocumentValidationError, match="sensitive credential"):
            workspace.upload_document(
                document_id="unsafe-log-001",
                filename="incident.log",
                content="Authorization: Bearer abcdefghijklmnopqrstuvwxyz123456",
                role=DocumentRole.ERROR_LOG,
                scope=ContextScope.TASK,
                scope_id="task-1",
            )
        with pytest.raises(DocumentValidationError, match="unsupported text document"):
            workspace.upload_document(
                document_id="binary-001",
                filename="screen.png",
                content=b"not-an-image",
                role=DocumentRole.REFERENCE,
                scope=ContextScope.TASK,
                scope_id="task-1",
            )
    finally:
        workspace.close()


def test_search_indexes_code_symbols_dependencies_and_documents(tmp_path: Path) -> None:
    repository = tmp_path / "repo"
    (repository / "services").mkdir(parents=True)
    (repository / "security").mkdir(parents=True)
    (repository / "services/customer_export.py").write_text(
        "def export_customers():\n    return 'active customers'\n",
        encoding="utf-8",
    )
    (repository / "security/entitlements.py").write_text(
        "def require_export_permission():\n    return 'manager'\n",
        encoding="utf-8",
    )
    workspace = ProductWorkspace.create(tmp_path / "state", _provider())
    try:
        count = workspace.index_repository(repository, _manifest(repository))
        assert count == 2
        hits = workspace.search.search("export_customers")
        assert hits
        assert hits[0].path == "services/customer_export.py"
        dependency_hits = workspace.search.search("require_export_permission")
        assert dependency_hits
        assert any(hit.path == "services/customer_export.py" for hit in dependency_hits)
    finally:
        workspace.close()


def test_requirement_alignment_blocks_on_missing_information_then_freezes_contract(
    tmp_path: Path,
) -> None:
    workspace = ProductWorkspace.create(tmp_path / "state", _provider())
    try:
        first = workspace.requirements.analyze(
            alignment_id="customer-export",
            title="Customer export",
            objective="Add customer export with authorization and auditing.",
        )
        assert first.contract.status is RequirementStatus.NEEDS_CLARIFICATION
        question = first.contract.clarifications[0]
        assert question.severity.value == "blocking"
        assert question.decision_key == "authorization_role"
        with pytest.raises(ValueError, match="clarification"):
            workspace.requirements.approve(first.contract)

        second = workspace.requirements.analyze(
            alignment_id="customer-export",
            title="Customer export",
            objective="Add customer export with authorization and auditing.",
            answers={"authorization_role": "manager-only"},
            previous=first.contract,
        )
        assert second.contract.status is RequirementStatus.READY_FOR_APPROVAL
        approved = workspace.requirements.approve(second.contract)
        assert approved.contract.status is RequirementStatus.APPROVED
        assert approved.requirement_hash == approved.contract.canonical_hash()
        assert [item.requirement_id for item in approved.contract.requirements] == [
            "R-001",
            "R-002",
        ]
        assert [item.criterion_id for item in approved.contract.acceptance_criteria] == [
            "AC-001",
            "AC-002",
        ]
    finally:
        workspace.close()


def test_requirement_alignment_accepts_legacy_question_id_answers(tmp_path: Path) -> None:
    workspace = ProductWorkspace.create(tmp_path / "state", _provider())
    try:
        first = workspace.requirements.analyze(
            alignment_id="legacy-answer",
            title="Customer export",
            objective="Add customer export with authorization and auditing.",
        )
        second = workspace.requirements.analyze(
            alignment_id="legacy-answer",
            title="Customer export",
            objective="Add customer export with authorization and auditing.",
            answers={"Q-001": "manager-only"},
            previous=first.contract,
        )
        assert second.contract.status is RequirementStatus.READY_FOR_APPROVAL
        assert second.contract.clarifications[0].decision_key == "authorization_role"
    finally:
        workspace.close()


def test_rephrased_clarification_reuses_stable_decision_key(tmp_path: Path) -> None:
    calls = 0

    def requirement_alignment(request):
        nonlocal calls
        calls += 1
        question = (
            "Which role may export customers?"
            if calls == 1
            else "Which entitlement is authorized to download the customer CSV?"
        )
        return {
            "title": "Customer export",
            "objective": "Add a governed customer export.",
            "requirements": [
                {
                    "statement": "Only an approved role can export customers.",
                    "category": "security",
                    "evidence_refs": ["security/entitlements.py"],
                }
            ],
            "acceptance_criteria": [
                {
                    "statement": "Unauthorized callers are rejected.",
                    "requirement_indexes": [0],
                }
            ],
            "constraints": [],
            "exclusions": [],
            "assumptions": [],
            "clarifications": [
                {
                    "decision_key": "authorization_role",
                    "question": question,
                    "severity": "blocking",
                    "rationale": "This changes the security boundary.",
                    "options": ["manager-only"],
                    "recommended_answer": "manager-only",
                    "evidence_refs": ["security/entitlements.py"],
                }
            ],
        }

    workspace = ProductWorkspace.create(
        tmp_path / "state",
        FakeModelProvider(handlers={"requirement_alignment": requirement_alignment}),
    )
    try:
        first = workspace.requirements.analyze(
            alignment_id="stable-decision",
            title="Customer export",
            objective="Add a governed customer export.",
        )
        second = workspace.requirements.analyze(
            alignment_id="stable-decision",
            title="Customer export",
            objective="Add a governed customer export.",
            answers={"authorization_role": "manager-only"},
            previous=first.contract,
        )
        assert second.contract.status is RequirementStatus.READY_FOR_APPROVAL
        assert len(second.contract.clarifications) == 1
        assert second.contract.clarifications[0].question_id == "Q-001"
        assert second.contract.clarifications[0].decision_key == "authorization_role"
    finally:
        workspace.close()


def test_new_decision_key_remains_blocking_after_prior_answer(tmp_path: Path) -> None:
    calls = 0

    def requirement_alignment(_request):
        nonlocal calls
        calls += 1
        clarifications = [
            {
                "decision_key": "authorization_role",
                "question": "Which role may export customers?",
                "severity": "blocking",
                "rationale": "This changes the security boundary.",
                "options": ["manager-only"],
                "recommended_answer": "manager-only",
                "evidence_refs": [],
            }
        ]
        if calls > 1:
            clarifications.append(
                {
                    "decision_key": "retention_policy",
                    "question": "How long must generated exports be retained?",
                    "severity": "material",
                    "rationale": "Retention changes data lifecycle behavior.",
                    "options": ["no-storage", "24-hours"],
                    "recommended_answer": "no-storage",
                    "evidence_refs": [],
                }
            )
        return {
            "title": "Customer export",
            "objective": "Add a governed customer export.",
            "requirements": [
                {
                    "statement": "Export access is governed.",
                    "category": "security",
                    "evidence_refs": [],
                }
            ],
            "acceptance_criteria": [],
            "constraints": [],
            "exclusions": [],
            "assumptions": [],
            "clarifications": clarifications,
        }

    workspace = ProductWorkspace.create(
        tmp_path / "state",
        FakeModelProvider(handlers={"requirement_alignment": requirement_alignment}),
    )
    try:
        first = workspace.requirements.analyze(
            alignment_id="new-decision",
            title="Customer export",
            objective="Add a governed customer export.",
        )
        second = workspace.requirements.analyze(
            alignment_id="new-decision",
            title="Customer export",
            objective="Add a governed customer export.",
            answers={"authorization_role": "manager-only"},
            previous=first.contract,
        )
        assert second.contract.status is RequirementStatus.NEEDS_CLARIFICATION
        assert [item.decision_key for item in second.contract.clarifications] == [
            "authorization_role",
            "retention_policy",
        ]
    finally:
        workspace.close()


def test_program_orchestration_is_phased_documented_pausable_and_hash_bound(
    tmp_path: Path,
) -> None:
    workspace = ProductWorkspace.create(tmp_path / "state", _provider())
    try:
        first = workspace.requirements.analyze(
            alignment_id="customer-export",
            title="Customer export",
            objective="Add customer export with authorization and auditing.",
        )
        aligned = workspace.requirements.analyze(
            alignment_id="customer-export",
            title="Customer export",
            objective="Add customer export with authorization and auditing.",
            answers={"authorization_role": "manager-only"},
            previous=first.contract,
        )
        approved = workspace.requirements.approve(aligned.contract)
        plan = workspace.programs.create_program(
            program_id="program-customer-export",
            requirement=approved.contract,
            requirement_hash=approved.requirement_hash,
        )
        assert workspace.programs.status(plan.program_id) is ProgramStatus.AWAITING_APPROVAL
        workspace.programs.approve_program(plan.program_id, plan.canonical_hash())
        assert [item.phase_id for item in workspace.programs.ready_phases(plan.program_id)] == [
            "phase-1"
        ]

        workspace.programs.pause(plan.program_id, reason="operator requested review")
        assert workspace.programs.ready_phases(plan.program_id) == ()
        control = workspace.control.get_required(ControlEntityType.PROGRAM, plan.program_id)
        assert control.state is ControlState.PAUSED
        workspace.programs.resume(plan.program_id)

        workspace.programs.start_phase(plan.program_id, "phase-1")
        summary_ref = workspace.programs.complete_phase(
            plan.program_id,
            PhaseResult(
                phase_id="phase-1",
                summary="Authorization boundary implemented and verified.",
                changed_paths=("security/entitlements.py",),
                decisions=("Manager role is required.",),
                tests=("authorization-contract: PASS",),
                reviewer_verdict="PASS",
            ),
        )
        summary = workspace.artifacts.read_text(summary_ref)
        assert "Status: COMPLETED" in summary
        assert "Manager role is required" in summary
        phase_hits = workspace.search.search("Manager role is required")
        assert any(hit.metadata.get("phase_id") == "phase-1" for hit in phase_hits)
        assert [item.phase_id for item in workspace.programs.ready_phases(plan.program_id)] == [
            "phase-2"
        ]
        assert workspace.programs.require_realign(plan.program_id, "b" * 64)
        assert workspace.programs.status(plan.program_id) is ProgramStatus.REALIGNMENT_REQUIRED
    finally:
        workspace.close()


def test_task_control_cancel_is_terminal_at_safe_boundary(tmp_path: Path) -> None:
    workspace = ProductWorkspace.create(tmp_path / "state", _provider())
    try:
        record = workspace.control.ensure(ControlEntityType.TASK, "task-123")
        assert record.state is ControlState.RUNNING
        workspace.control.request_cancel(
            ControlEntityType.TASK,
            "task-123",
            reason="user stopped the task",
        )
        decision = workspace.control.checkpoint(ControlEntityType.TASK, "task-123")
        assert decision.action is ControlAction.CANCEL
        assert decision.record.state is ControlState.CANCELLED
        with pytest.raises(ValueError, match="terminal"):
            workspace.control.request_pause(ControlEntityType.TASK, "task-123")
    finally:
        workspace.close()
