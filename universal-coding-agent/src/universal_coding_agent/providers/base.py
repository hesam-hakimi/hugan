from __future__ import annotations

from typing import Protocol, runtime_checkable

from universal_coding_agent.core.cancellation import CancellationSignal
from universal_coding_agent.core.models import (
    ModelCapabilities,
    ModelRequest,
    ModelResponse,
)
from universal_coding_agent.core.remote_operations import (
    RemoteOperationAction,
    RemoteOperationLeaseStore,
    RemoteOperationSnapshot,
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


@runtime_checkable
class CancellableModelProvider(Protocol):
    def invoke_cancellable(
        self,
        request: ModelRequest,
        cancellation: CancellationSignal,
    ) -> ModelResponse:
        """Invoke while exposing cancellation to provider-owned work."""


@runtime_checkable
class RemoteOperationLeaseAwareProvider(Protocol):
    def bind_remote_operation_store(self, store: RemoteOperationLeaseStore) -> None:
        """Bind private persistence before starting any leased remote operation."""


@runtime_checkable
class RestartReconciliationModelProvider(Protocol):
    def remote_operation_snapshot(
        self,
        task_id: str,
    ) -> RemoteOperationSnapshot | None:
        """Read identifier-free persisted state without contacting the provider."""

    def reconcile_remote_operation(
        self,
        task_id: str,
        action: RemoteOperationAction,
    ) -> RemoteOperationSnapshot:
        """Perform one explicit, bounded remote observe or cancel action."""
