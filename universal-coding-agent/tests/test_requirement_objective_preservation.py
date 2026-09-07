from __future__ import annotations

import json
from pathlib import Path

import pytest

from universal_coding_agent.core.models import ModelRequest
from universal_coding_agent.product.models import RequirementContract, RequirementStatus
from universal_coding_agent.product.workspace import ProductWorkspace
from universal_coding_agent.providers.fake import FakeModelProvider

_LIVE_OBJECTIVE = (
    "Implement the attached customer export order using the existing application entry "
    "point and repository contracts. This is a multi-phase change. All technical "
    "contracts are present in the repository; only the authorization role is intentionally "
    "unspecified and must be clarified rather than inferred."
)
_MODEL_OBJECTIVE = "Implement the governed active-customer CSV export."


def _draft(*, clarify: bool = False, invalid_reference: bool = False) -> dict:
    return {
        "title": "Governed customer export",
        "objective": _MODEL_OBJECTIVE,
        "requirements": [{"statement": "Export access must be authorized."}],
        "acceptance_criteria": [
            {
                "statement": "Unauthorized callers are rejected.",
                "requirement_indexes": [4 if invalid_reference else 0],
            }
        ],
        "constraints": ["Preserve the existing entry point."],
        "exclusions": ["Do not modify legacy exports."],
        "assumptions": [],
        "clarifications": [
            {
                "decision_key": "authorization_role",
                "question": "Which role may export customers?",
                "severity": "blocking",
                "rationale": "The role determines the security boundary.",
            }
        ] if clarify else [],
    }


@pytest.mark.parametrize(
    "objective",
    [
        _LIVE_OBJECTIVE,
        "Deliver in three reviewed phases; release only after all three pass.",
        "Observe only. Never change source or publish a pull request.",
        "Retain rollback evidence and stop when the approved budget is exhausted.",
        "  Preserve exact spaces.\nDo not normalize the caller's objective.  ",
        "Preserve Unicode: caf\u00e9, \u2014, and \U0001f512.",
        "x",
        "x" * 8000,
    ],
)
def test_model_summary_cannot_replace_caller_objective(
    tmp_path: Path, objective: str,
) -> None:
    workspace = ProductWorkspace.create(
        tmp_path / "state",
        FakeModelProvider(handlers={"requirement_alignment": lambda _request: _draft()}),
    )
    try:
        result = workspace.requirements.analyze(
            alignment_id="objective-preservation", title="Export", objective=objective,
        )
        assert result.contract.objective == objective
        persisted = workspace.artifacts.read_json(result.contract_ref)
        assert persisted["objective"] == objective
        reloaded = RequirementContract.model_validate(persisted)
        assert reloaded.canonical_hash() == result.requirement_hash
        assert reloaded.objective == objective
        assert result.contract.constraints == ("Preserve the existing entry point.",)
        assert result.contract.exclusions == ("Do not modify legacy exports.",)
        assert result.contract.acceptance_criteria[0].requirement_ids == ("R-001",)
        assert result.contract.status is RequirementStatus.READY_FOR_APPROVAL
    finally:
        workspace.close()


def test_clarification_and_approval_preserve_objective_and_security_gate(tmp_path: Path) -> None:
    workspace = ProductWorkspace.create(
        tmp_path / "state",
        FakeModelProvider(
            handlers={"requirement_alignment": lambda _request: _draft(clarify=True)}
        ),
    )
    try:
        first = workspace.requirements.analyze(
            alignment_id="objective-clarification", title="Export", objective=_LIVE_OBJECTIVE,
        )
        assert first.contract.status is RequirementStatus.NEEDS_CLARIFICATION
        assert first.contract.objective == _LIVE_OBJECTIVE
        with pytest.raises(ValueError, match="clarification"):
            workspace.requirements.approve(first.contract)
        aligned = workspace.requirements.analyze(
            alignment_id="objective-clarification", title="Export", objective=_LIVE_OBJECTIVE,
            answers={"authorization_role": "manager"}, previous=first.contract,
        )
        assert aligned.contract.objective == _LIVE_OBJECTIVE
        approved = workspace.requirements.approve(aligned.contract)
        assert approved.contract.status is RequirementStatus.APPROVED
        assert approved.contract.objective == _LIVE_OBJECTIVE
        assert approved.contract.answers == {"authorization_role": "manager"}
        assert approved.requirement_hash == aligned.requirement_hash
        assert workspace.artifacts.read_json(approved.contract_ref)["objective"] == _LIVE_OBJECTIVE
        summary = workspace.artifacts.read_text(approved.context_ref)
        assert "## User objective\n" + _LIVE_OBJECTIVE in summary
        assert "authorization_role: manager" in summary
        assert first.contract.status is RequirementStatus.NEEDS_CLARIFICATION
    finally:
        workspace.close()


def test_explicit_objective_revision_changes_hash_without_mutating_prior_contract(
    tmp_path: Path,
) -> None:
    workspace = ProductWorkspace.create(
        tmp_path / "state",
        FakeModelProvider(handlers={"requirement_alignment": lambda _request: _draft()}),
    )
    try:
        first = workspace.requirements.analyze(
            alignment_id="objective-revision", title="Export", objective=_LIVE_OBJECTIVE,
        )
        old_hash = first.requirement_hash
        revised_objective = "Deliver the export in four reviewable phases without publication."
        revised = workspace.requirements.analyze(
            alignment_id="objective-revision", title="Export", objective=revised_objective,
            previous=first.contract,
        )
        assert revised.contract.objective == revised_objective
        assert first.contract.objective == _LIVE_OBJECTIVE
        assert first.contract.canonical_hash() == old_hash
        assert revised.contract.version == first.contract.version + 1
        assert revised.requirement_hash != old_hash
        # Isolate the objective from the version change when proving hash binding.
        changed_objective_only = first.contract.model_copy(update={"objective": revised_objective})
        assert changed_objective_only.canonical_hash() != old_hash
        assert workspace.artifacts.read_json(first.contract_ref)["objective"] == _LIVE_OBJECTIVE
    finally:
        workspace.close()


def test_schema_repair_cannot_rewrite_caller_objective(tmp_path: Path) -> None:
    def alignment(request: ModelRequest) -> dict:
        return _draft(invalid_reference=request.metadata.get("schema_repair") != "true")

    workspace = ProductWorkspace.create(
        tmp_path / "state", FakeModelProvider(handlers={"requirement_alignment": alignment}),
    )
    try:
        result = workspace.requirements.analyze(
            alignment_id="objective-repair", title="Export", objective=_LIVE_OBJECTIVE,
        )
        assert result.contract.objective == _LIVE_OBJECTIVE
        diagnostics = workspace.artifacts.read_json(result.validation_ref)
        assert diagnostics["repair_used"] is True
        assert len(diagnostics["attempts"]) == 2
        assert result.contract.acceptance_criteria[0].requirement_ids == ("R-001",)
    finally:
        workspace.close()


def test_program_planner_receives_the_hash_bound_original_objective(tmp_path: Path) -> None:
    requests: list[ModelRequest] = []

    def planner(request: ModelRequest) -> dict:
        requests.append(request)
        return {
            "title": "Customer export delivery",
            "objective": "Deliver and qualify the export before release.",
            "phases": [
                {"phase_id": "phase-1", "title": "Contracts", "objective": "Review contracts."},
                {
                    "phase_id": "phase-2", "title": "Implementation",
                    "objective": "Implement against accepted contracts.",
                    "dependencies": ["phase-1"],
                },
            ],
            "definition_of_done": ["All phases reviewed before release."],
        }

    workspace = ProductWorkspace.create(
        tmp_path / "state",
        FakeModelProvider(handlers={
            "requirement_alignment": lambda _request: _draft(), "program_planner": planner,
        }),
    )
    try:
        aligned = workspace.requirements.analyze(
            alignment_id="objective-planner", title="Export", objective=_LIVE_OBJECTIVE,
        )
        approved = workspace.requirements.approve(aligned.contract)
        plan = workspace.programs.create_program(
            program_id="objective-program", requirement=approved.contract,
            requirement_hash=approved.requirement_hash,
        )
        assert len(requests) == 1
        assert json.dumps(_LIVE_OBJECTIVE, ensure_ascii=False) in requests[0].user_prompt
        assert requests[0].metadata["requirement_hash"] == approved.requirement_hash
        context = workspace.artifacts.read_text(
            "artifact://programs/objective-program/program-planner-context.md"
        )
        assert context == requests[0].user_prompt
        assert plan.requirement_hash == approved.requirement_hash
        assert len(plan.phases) == 2
        assert workspace.programs.status(plan.program_id).value == "awaiting_approval"
    finally:
        workspace.close()
