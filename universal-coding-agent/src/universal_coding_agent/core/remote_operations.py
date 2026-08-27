from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Literal, Protocol

from pydantic import Field, model_validator

from universal_coding_agent.core.models import FrozenModel


class RemoteOperationState(StrEnum):
    ACTIVE = "active"
    TERMINAL = "terminal"
    UNAVAILABLE = "unavailable"


class RemoteOperationAction(StrEnum):
    OBSERVE = "observe"
    CANCEL = "cancel"


class RemoteOperationDispositionOutcome(StrEnum):
    CANCELLED = "cancelled"
    FAILED = "failed"


class RemoteOperationLeaseRetirementEligibilityCode(StrEnum):
    """Stable fail-closed reasons returned by the read-only retention inventory."""

    LIFECYCLE_ACTION_ACTIVE = "lifecycle_action_active"
    LOCAL_WORKER_ACTIVE = "local_worker_active"
    ACTIVE_PRIVATE_LEASE = "active_private_lease"
    DISPOSITION_AUDIT_INVALID = "disposition_audit_invalid"
    LEASE_DISPOSITION_MISMATCH = "lease_disposition_mismatch"
    TASK_CONTROL_MISSING = "task_control_missing"
    TASK_CONTROL_STATE_MISMATCH = "task_control_state_mismatch"
    RETIREMENT_RECEIPT_CONFLICT = "retirement_receipt_conflict"
    RETIREMENT_RECEIPT_INVALID = "retirement_receipt_invalid"
    PROGRAM_BINDING_MISSING = "program_binding_missing"
    PROGRAM_BINDING_MISMATCH = "program_binding_mismatch"
    PROGRAM_EVIDENCE_INCOMPLETE = "program_evidence_incomplete"


@dataclass(frozen=True)
class PrivateRemoteOperationLease:
    """Private provider lease whose opaque identifier must never cross public surfaces."""

    task_id: str
    thread_id: str
    transport: str
    transport_scope: str
    operation_id: str = field(repr=False)
    operation_ref: str
    base_sha: str
    created_at: str
    updated_at: str
    last_status: str
    state: RemoteOperationState
    cancellation_requested: bool
    revision: int
    reconciliation_attempts: int
    cancel_requests: int
    last_action: RemoteOperationAction | None


class RemoteOperationSnapshot(FrozenModel):
    """Identifier-free durable state safe for APIs, reports, logs, and artifacts."""

    task_id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")
    thread_id: str = Field(default="", max_length=128)
    transport: str = Field(pattern=r"^[a-z][a-z0-9._-]{2,63}$")
    transport_scope: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    operation_ref: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    base_sha: str = Field(default="", max_length=64)
    created_at: str
    updated_at: str
    last_status: str = Field(min_length=1, max_length=64)
    state: RemoteOperationState
    cancellation_requested: bool
    revision: int = Field(ge=0)
    reconciliation_attempts: int = Field(ge=0)
    cancel_requests: int = Field(ge=0)
    last_action: RemoteOperationAction | None = None


class RemoteOperationDisposition(FrozenModel):
    """Durable operator disposition derived only from a redacted terminal lease."""

    schema_version: str = Field(default="1", pattern=r"^1$")
    audit_ref: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    task_id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")
    outcome: RemoteOperationDispositionOutcome
    reason: str = Field(min_length=1, max_length=2000)
    recorded_at: str
    program_id: str = Field(default="", max_length=128)
    phase_id: str = Field(default="", max_length=64)
    slice_id: str = Field(default="", max_length=64)
    transport: str = Field(pattern=r"^[a-z][a-z0-9._-]{2,63}$")
    transport_scope: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    operation_ref: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    base_sha: str = Field(default="", max_length=64)
    remote_state: Literal[
        RemoteOperationState.TERMINAL,
        RemoteOperationState.UNAVAILABLE,
    ]
    remote_status: str = Field(min_length=1, max_length=64)
    remote_revision: int = Field(ge=0)
    remote_updated_at: str
    provider_confirmed_cancelled: bool
    confirmed_by_operator: Literal[True]
    provider_calls_made: int = Field(default=0, ge=0, le=0)
    output_consumed: Literal[False] = False
    graph_resumed: Literal[False] = False
    program_phase_advanced: Literal[False] = False


class RemoteOperationLeaseRetirement(FrozenModel):
    """Redacted receipt proving explicit retirement of one private lease row."""

    schema_version: str = Field(default="1", pattern=r"^1$")
    retirement_ref: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    task_id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")
    disposition_audit_ref: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    disposition_outcome: RemoteOperationDispositionOutcome
    program_id: str = Field(default="", max_length=128)
    phase_id: str = Field(default="", max_length=64)
    slice_id: str = Field(default="", max_length=64)
    reason: str = Field(min_length=1, max_length=2000)
    retired_at: str
    transport: str = Field(pattern=r"^[a-z][a-z0-9._-]{2,63}$")
    transport_scope: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    operation_ref: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    base_sha: str = Field(default="", max_length=64)
    remote_state: Literal[
        RemoteOperationState.TERMINAL,
        RemoteOperationState.UNAVAILABLE,
    ]
    remote_status: str = Field(min_length=1, max_length=64)
    remote_revision: int = Field(ge=0)
    remote_updated_at: str
    confirmed_by_operator: Literal[True]
    private_lease_rows_retired: int = Field(default=1, ge=1, le=1)
    private_identifier_retained_in_active_store: Literal[False] = False
    provider_calls_made: int = Field(default=0, ge=0, le=0)
    output_consumed: Literal[False] = False
    graph_resumed: Literal[False] = False
    task_outcome_changes_made: int = Field(default=0, ge=0, le=0)
    program_outcome_changes_made: int = Field(default=0, ge=0, le=0)
    program_phase_advanced: Literal[False] = False


class RemoteOperationLeaseRetirementEligibilityReason(FrozenModel):
    """One operator-safe reason why the existing retirement action would be blocked."""

    code: RemoteOperationLeaseRetirementEligibilityCode
    message: str = Field(min_length=1, max_length=500)


class RetainedRemoteOperationLeaseInventoryItem(FrozenModel):
    """Allow-listed summary for one retained private lease with disposition evidence."""

    schema_version: str = Field(default="1", pattern=r"^1$")
    task_id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")
    program_id: str = Field(default="", max_length=128)
    phase_id: str = Field(default="", max_length=64)
    slice_id: str = Field(default="", max_length=64)
    transport: str = Field(pattern=r"^[a-z][a-z0-9._-]{2,63}$")
    remote_state: RemoteOperationState
    remote_status: str = Field(min_length=1, max_length=64)
    remote_revision: int = Field(ge=0)
    remote_updated_at: str
    disposition_audit_ref: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    disposition_outcome: RemoteOperationDispositionOutcome
    disposition_recorded_at: str
    retained_private_lease: Literal[True] = True
    eligible_for_retirement: bool
    eligibility_reasons: tuple[RemoteOperationLeaseRetirementEligibilityReason, ...] = ()
    preview_is_advisory: Literal[True] = True
    action_revalidation_required: Literal[True] = True

    @model_validator(mode="after")
    def validate_eligibility(self) -> RetainedRemoteOperationLeaseInventoryItem:
        if self.eligible_for_retirement and self.eligibility_reasons:
            raise ValueError("eligible inventory item cannot contain blocking reasons")
        if not self.eligible_for_retirement and not self.eligibility_reasons:
            raise ValueError("ineligible inventory item requires at least one reason")
        return self


class RetainedRemoteOperationLeaseInventory(FrozenModel):
    """Bounded GET-only inventory page; it never reserves or changes lifecycle state."""

    schema_version: str = Field(default="1", pattern=r"^1$")
    generated_at: str
    items: tuple[RetainedRemoteOperationLeaseInventoryItem, ...] = ()
    returned_count: int = Field(ge=0, le=100)
    scanned_count: int = Field(ge=0, le=100)
    has_more: bool
    next_after_task_id: str = Field(
        default="",
        max_length=128,
        pattern=r"^$|^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$",
    )
    read_only: Literal[True] = True
    provider_calls_made: int = Field(default=0, ge=0, le=0)
    mutations_made: Literal[False] = False
    opaque_provider_identifiers_exposed: Literal[False] = False

    @model_validator(mode="after")
    def validate_page(self) -> RetainedRemoteOperationLeaseInventory:
        if self.returned_count != len(self.items):
            raise ValueError("inventory returned count does not match items")
        if self.returned_count > self.scanned_count:
            raise ValueError("inventory cannot return more rows than it scanned")
        if self.has_more != bool(self.next_after_task_id):
            raise ValueError("inventory continuation state is inconsistent")
        return self


class RemoteOperationLeaseStore(Protocol):
    """Private persistence boundary used by explicitly lease-aware providers."""

    def register(
        self,
        *,
        task_id: str,
        thread_id: str,
        transport: str,
        transport_scope: str,
        operation_id: str,
        base_sha: str,
        status: str,
        state: RemoteOperationState,
    ) -> PrivateRemoteOperationLease: ...

    def private_lease(self, task_id: str) -> PrivateRemoteOperationLease | None: ...

    def public_snapshot(self, task_id: str) -> RemoteOperationSnapshot | None: ...

    def record_action(
        self,
        task_id: str,
        action: RemoteOperationAction,
        *,
        reconciliation: bool,
    ) -> PrivateRemoteOperationLease: ...

    def record_status(
        self,
        task_id: str,
        *,
        status: str,
        state: RemoteOperationState,
    ) -> PrivateRemoteOperationLease: ...

    def mark_unavailable(
        self,
        task_id: str,
        *,
        status: str = "remote_state_unavailable",
    ) -> PrivateRemoteOperationLease: ...
