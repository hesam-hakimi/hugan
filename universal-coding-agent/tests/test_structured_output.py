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
    assert result.diagnostics["budget_retry_used"] is False
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
    assert captured.value.diagnostics["budget_retry_used"] is False
    assert len(captured.value.diagnostics["attempts"]) == 2
    assert len(provider.requests) == 2


def test_structured_output_retries_truncated_output_with_larger_budget() -> None:
    provider = SequenceProvider(
        responses=[
            ModelResponse(
                content='{"phase_id":"P2C","title":"Phase 2C',
                actual_model="test-model",
                finish_reason="length",
                completion_tokens=512,
            ),
            ModelResponse(
                structured=_repaired_plan(),
                actual_model="test-model",
                finish_reason="stop",
                completion_tokens=700,
            ),
        ]
    )

    result = invoke_structured(provider, _request(), PhasePlan)

    assert result.repair_used is False
    assert result.diagnostics["budget_retry_used"] is True
    assert len(provider.requests) == 2
    assert provider.requests[0].max_output_tokens == 512
    assert provider.requests[1].max_output_tokens == 1024
    assert provider.requests[1].metadata["output_budget_retry"] == "true"
    assert provider.requests[1].metadata["previous_max_output_tokens"] == "512"
    assert result.diagnostics["attempts"][0]["failure_kind"] == "output_budget_exhausted"
    assert result.diagnostics["attempts"][0]["schema_valid"] is False
    assert result.diagnostics["attempts"][1]["schema_valid"] is True


def test_structured_output_does_not_schema_repair_truncated_json() -> None:
    provider = SequenceProvider(
        responses=[
            ModelResponse(
                content='{"phase_id":"P2C","title":"Phase 2C',
                finish_reason="length",
                completion_tokens=512,
            ),
            ModelResponse(
                content='{"phase_id":"P2C","title":"Phase 2C',
                finish_reason="length",
                completion_tokens=1024,
            ),
        ]
    )

    with pytest.raises(StructuredOutputError) as captured:
        invoke_structured(provider, _request(), PhasePlan)

    assert captured.value.code == "model_output_budget_exhausted"
    assert captured.value.diagnostics["repair_used"] is False
    assert captured.value.diagnostics["budget_retry_used"] is True
    assert len(provider.requests) == 2
    assert "schema_repair" not in provider.requests[1].metadata
    assert provider.requests[1].max_output_tokens == 1024
    assert all(
        item["failure_kind"] == "output_budget_exhausted"
        for item in captured.value.diagnostics["attempts"]
    )
