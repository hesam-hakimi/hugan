from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from universal_coding_agent.core.models import (
    ModelCapabilities,
    ModelRequest,
    ModelResponse,
    PhasePlan,
)
from universal_coding_agent.orchestration.structured_output import (
    StructuredOutputError,
    invoke_structured,
)


@dataclass
class SequenceProvider:
    responses: list[ModelResponse]
    requests: list[ModelRequest] = field(default_factory=list)

    def probe(self) -> bool:
        return True

    def capabilities(self) -> ModelCapabilities:
        return ModelCapabilities(structured_output=True)

    def invoke(self, request: ModelRequest) -> ModelResponse:
        self.requests.append(request)
        return self.responses.pop(0)


def _request() -> ModelRequest:
    return ModelRequest(
        role="planner",
        system_prompt="Return a phase plan.",
        user_prompt="Inspect the phase.",
        response_schema=PhasePlan.model_json_schema(),
        max_output_tokens=512,
    )


def _invalid_plan() -> dict[str, object]:
    return {
        "phase_id": "P2C",
        "title": "Phase 2C",
        "objective": "Remediate the phase.",
        "slices": [
            {
                "slice_id": "S1",
                "title": "Schema validation",
                "objective": "Validate schema membership.",
                "dependencies": ["Phase 2B canonical schema specification"],
            }
        ],
    }


def _repaired_plan() -> dict[str, object]:
    return {
        "phase_id": "P2C",
        "title": "Phase 2C",
        "objective": "Remediate the phase.",
        "slices": [
            {
                "slice_id": "S1",
                "title": "Schema validation",
                "objective": "Validate schema membership.",
                "dependencies": [],
                "external_dependencies": ["Phase 2B canonical schema specification"],
            }
        ],
    }


def test_structured_output_repairs_external_dependency_once() -> None:
    provider = SequenceProvider(
        responses=[
            ModelResponse(structured=_invalid_plan(), actual_model="test-model"),
            ModelResponse(structured=_repaired_plan(), actual_model="test-model"),
        ]
    )

    result = invoke_structured(
        provider,
        _request(),
        PhasePlan,
        repair_guidance=(
            "Use dependencies only for exact slice IDs and external_dependencies "
            "for prior-phase prerequisites."
        ),
    )

    assert result.repair_used is True
    assert result.value.slices[0].dependencies == ()
    assert result.value.slices[0].external_dependencies == (
        "Phase 2B canonical schema specification",
    )
    assert len(provider.requests) == 2
    assert provider.requests[1].metadata["schema_repair"] == "true"
    assert "external_dependencies" in provider.requests[1].user_prompt
    assert result.diagnostics["attempts"][0]["schema_valid"] is False
    assert result.diagnostics["attempts"][1]["schema_valid"] is True


def test_structured_output_fails_closed_after_one_repair() -> None:
    provider = SequenceProvider(
        responses=[
            ModelResponse(structured=_invalid_plan()),
            ModelResponse(structured=_invalid_plan()),
        ]
    )

    with pytest.raises(StructuredOutputError) as captured:
        invoke_structured(provider, _request(), PhasePlan)

    assert captured.value.code == "model_schema_invalid"
    assert captured.value.diagnostics["repair_used"] is True
    assert len(captured.value.diagnostics["attempts"]) == 2
    assert len(provider.requests) == 2
