from __future__ import annotations

from typing import Protocol, runtime_checkable

from universal_coding_agent.core.models import (
    ModelCapabilities,
    ModelRequest,
    ModelResponse,
)


class ModelProviderError(RuntimeError):
    """Safe base error for provider failures."""

    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(message)


@runtime_checkable
class ModelProvider(Protocol):
    def probe(self) -> bool:
        """Return True only when the configured provider is callable."""

    def capabilities(self) -> ModelCapabilities:
        """Describe supported request/response capabilities."""

    def invoke(self, request: ModelRequest) -> ModelResponse:
        """Invoke one bounded role request."""
