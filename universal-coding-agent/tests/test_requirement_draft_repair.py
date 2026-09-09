from __future__ import annotations

import pytest

from universal_coding_agent.product.models import RequirementDraft, RequirementStatus
from universal_coding_agent.product.workspace import ProductWorkspace
from universal_coding_agent.providers.fake import FakeModelProvider


def _draft_payload(requirement_index: int) -> dict:
    return {
        "title": "Customer export",
        "objective": "Deliver a governed export.",
        "requirements": [
            {
                "statement": "The export returns active customers.",
                "category": "functional",
                "evidence_refs": [],
            }
        ],
        "acceptance_criteria": [
            {
                "statement": "Only active customers are returned.",
                "requirement_indexes": [requirement_index],
            }
        ],
        "constraints": [],
        "exclusions": [],
        "assumptions": [],
        "clarifications": [],
    }


def test_requirement_draft_rejects_unknown_acceptance_reference() -> None:
    with pytest.raises(ValueError, match="unknown requirement indexes"):
        RequirementDraft.model_validate(_draft_payload(3))


def test_requirement_alignment_repairs_acceptance_cross_reference(tmp_path) -> None:
    def requirement_alignment(request):
        repaired = request.metadata.get("schema_repair") == "true"
        return _draft_payload(0 if repaired else 4)

    workspace = ProductWorkspace.create(
        tmp_path / "state",
        FakeModelProvider(handlers={"requirement_alignment": requirement_alignment}),
    )
    try:
        result = workspace.requirements.analyze(
            alignment_id="acceptance-repair",
            title="Customer export",
            objective="Deliver a governed customer export.",
        )
        assert result.contract.status is RequirementStatus.READY_FOR_APPROVAL
        assert result.contract.acceptance_criteria[0].requirement_ids == ("R-001",)
        validation = workspace.artifacts.read_json(result.validation_ref)
        assert validation["repair_used"] is True
        assert len(validation["attempts"]) == 2
        assert validation["attempts"][0]["schema_valid"] is False
        assert validation["attempts"][1]["schema_valid"] is True
    finally:
        workspace.close()
