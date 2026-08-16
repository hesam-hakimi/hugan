from __future__ import annotations

from collections.abc import Callable
from typing import Any

from universal_coding_agent.core.models import (
    ModelCapabilities,
    ModelRequest,
    ModelResponse,
    PhasePlan,
    ReviewResult,
    ReviewVerdict,
    SlicePlan,
)


class FakeModelProvider:
    """Deterministic provider used by tests and local demonstrations."""

    def __init__(
        self,
        handlers: dict[str, Callable[[ModelRequest], dict[str, Any]]] | None = None,
    ) -> None:
        self._handlers = handlers or {}

    def probe(self) -> bool:
        return True

    def capabilities(self) -> ModelCapabilities:
        return ModelCapabilities(structured_output=True, actual_model_identity=True)

    def invoke(self, request: ModelRequest) -> ModelResponse:
        if request.role in self._handlers:
            payload = self._handlers[request.role](request)
        elif request.role == "planner":
            payload = PhasePlan(
                phase_id="phase-observe",
                title="Observe qualification",
                objective="Inspect the repository and produce an evidence-backed plan.",
                requirements=("Preserve repository state",),
                slices=(
                    SlicePlan(
                        slice_id="S0",
                        title="Evidence discovery",
                        objective="Read instructions, architecture, source, and tests.",
                        acceptance_criteria=("Evidence references are present",),
                        recommended_checks=("git-diff-check",),
                    ),
                ),
                final_acceptance_criteria=("Independent reviewer returns a verdict",),
            ).model_dump(mode="json")
        elif request.role == "reviewer":
            payload = ReviewResult(
                verdict=ReviewVerdict.PASS,
                requirement_findings=("The plan is bounded and read-only.",),
                confidence="high",
            ).model_dump(mode="json")
        else:
            payload = {"status": "ok"}
        return ModelResponse(structured=payload, actual_model="fake-model", finish_reason="stop")


def create_provider() -> FakeModelProvider:
    """Return the deterministic provider used by bootstrap and smoke tests."""

    return FakeModelProvider()
