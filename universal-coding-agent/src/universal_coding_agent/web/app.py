from __future__ import annotations

import ipaddress
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from universal_coding_agent.core.models import RepositorySpec
from universal_coding_agent.core.remote_operations import (
    RemoteOperationAction,
    RemoteOperationDisposition,
    RemoteOperationDispositionOutcome,
    RemoteOperationLeaseRetirementEligibilityCode,
    RemoteOperationLeaseRetirementEligibilityReason,
    RemoteOperationState,
    RetainedRemoteOperationLeaseInventory,
    RetainedRemoteOperationLeaseInventoryItem,
)
from universal_coding_agent.core.safe_models import SafeModePolicy
from universal_coding_agent.product.context_documents import DocumentValidationError
from universal_coding_agent.product.models import (
    ContextScope,
    ControlState,
    DocumentRole,
    PhaseStatus,
    ProgramExecutionBinding,
    ProgramExecutionStatus,
    ProgramStatus,
    RequirementContract,
)
from universal_coding_agent.product.remote_operations import (
    RetainedRemoteOperationLeaseEvidence,
    retained_lease_matches_disposition,
    validate_remote_operation_disposition,
)
from universal_coding_agent.product.workspace import ProductWorkspace
from universal_coding_agent.providers.base import (
    ModelProviderError,
    RestartReconciliationModelProvider,
)
from universal_coding_agent.safety.sanitizer import sanitize_text
from universal_coding_agent.storage.artifacts import ArtifactSizeLimitExceeded

RETAINED_LEASE_PROGRAM_ARTIFACT_MAX_BYTES = 256 * 1024


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000)
    top_k: int = Field(default=20, ge=1, le=100)


class DocumentUploadRequest(BaseModel):
    document_id: str
    filename: str
    content: str
    role: DocumentRole
    scope: ContextScope
    scope_id: str


class RequirementAnalyzeRequest(BaseModel):
    alignment_id: str
    title: str
    objective: str
    answers: dict[str, str] = Field(default_factory=dict)
    previous: RequirementContract | None = None


class RequirementApproveRequest(BaseModel):
    contract: RequirementContract


class ProgramCreateRequest(BaseModel):
    program_id: str
    requirement: RequirementContract
    requirement_hash: str


class ProgramApproveRequest(BaseModel):
    plan_hash: str


class ProgramExecutionStartRequest(BaseModel):
    current_requirement_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    repository: str = Field(min_length=1, max_length=4000)
    ref: str = Field(min_length=1, max_length=512)
    policy: SafeModePolicy
    test_profiles: tuple[str, ...]


class ProgramExecutionContinueRequest(BaseModel):
    current_requirement_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    approved: bool


class ControlRequest(BaseModel):
    reason: str = ""


class ScopeDecisionRequest(BaseModel):
    approved: bool


class RemoteOperationReconcileRequest(BaseModel):
    action: RemoteOperationAction


class RemoteOperationDispositionRequest(BaseModel):
    outcome: RemoteOperationDispositionOutcome
    reason: str = Field(min_length=1, max_length=2000)
    confirmed: Literal[True]


class RemoteOperationLeaseRetirementRequest(BaseModel):
    disposition_audit_ref: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    reason: str = Field(min_length=1, max_length=2000)
    confirmed: Literal[True]


class SafeTaskStartRequest(BaseModel):
    task_id: str | None = None
    thread_id: str | None = None
    title: str = "Safe task"
    objective: str = Field(min_length=1, max_length=20_000)
    repository: str
    ref: str
    policy: SafeModePolicy
    test_profiles: tuple[str, ...]
    acceptance_criteria: tuple[str, ...] = ()


_RETIREMENT_ELIGIBILITY_MESSAGES = {
    RemoteOperationLeaseRetirementEligibilityCode.LIFECYCLE_ACTION_ACTIVE: (
        "Another local lifecycle action is active for this task."
    ),
    RemoteOperationLeaseRetirementEligibilityCode.LOCAL_WORKER_ACTIVE: (
        "A local standalone or Program worker is active for this task."
    ),
    RemoteOperationLeaseRetirementEligibilityCode.ACTIVE_PRIVATE_LEASE: (
        "The retained private lease still reports active remote state."
    ),
    RemoteOperationLeaseRetirementEligibilityCode.DISPOSITION_AUDIT_INVALID: (
        "The durable disposition audit reference does not match its canonical redacted evidence."
    ),
    RemoteOperationLeaseRetirementEligibilityCode.LEASE_DISPOSITION_MISMATCH: (
        "The retained lease no longer exactly matches the durable disposition evidence."
    ),
    RemoteOperationLeaseRetirementEligibilityCode.TASK_CONTROL_MISSING: (
        "The task has no durable task-control record."
    ),
    RemoteOperationLeaseRetirementEligibilityCode.TASK_CONTROL_STATE_MISMATCH: (
        "The terminal task-control state does not match the durable disposition outcome."
    ),
    RemoteOperationLeaseRetirementEligibilityCode.RETIREMENT_RECEIPT_CONFLICT: (
        "A retirement receipt already exists while the private lease row remains retained."
    ),
    RemoteOperationLeaseRetirementEligibilityCode.RETIREMENT_RECEIPT_INVALID: (
        "Existing retirement evidence failed its canonical redacted reference check."
    ),
    RemoteOperationLeaseRetirementEligibilityCode.PROGRAM_BINDING_MISSING: (
        "The disposition names a Program but no persisted execution binding exists."
    ),
    RemoteOperationLeaseRetirementEligibilityCode.PROGRAM_BINDING_MISMATCH: (
        "Persisted standalone or Program identity does not match the durable disposition."
    ),
    RemoteOperationLeaseRetirementEligibilityCode.PROGRAM_EVIDENCE_OVERSIZED: (
        "A Program disposition or phase-report artifact exceeds the bounded inventory read limit."
    ),
    RemoteOperationLeaseRetirementEligibilityCode.PROGRAM_EVIDENCE_INCOMPLETE: (
        "The terminal Program binding, artifact, phase report, phase state, or "
        "blocked Program state is incomplete or inconsistent."
    ),
}


def _retirement_eligibility_reason(
    code: RemoteOperationLeaseRetirementEligibilityCode,
) -> RemoteOperationLeaseRetirementEligibilityReason:
    return RemoteOperationLeaseRetirementEligibilityReason(
        code=code,
        message=_RETIREMENT_ELIGIBILITY_MESSAGES[code],
    )


@dataclass
class ProductWebRuntime:
    workspace: ProductWorkspace
    state_root: Path
    allow_local_sources: bool = False
    executor: ThreadPoolExecutor = field(
        default_factory=lambda: ThreadPoolExecutor(
            max_workers=1,
            thread_name_prefix="uca-web",
        )
    )
    _runs: dict[str, dict[str, Any]] = field(default_factory=dict)
    _program_execution_runs: dict[str, dict[str, Any]] = field(default_factory=dict)
    _remote_operation_actions: set[str] = field(default_factory=set)
    _program_control_actions: set[str] = field(default_factory=set)
    _lock: threading.RLock = field(default_factory=threading.RLock)

    def close(self) -> None:
        self.executor.shutdown(wait=False, cancel_futures=True)
        self.workspace.close()

    def start_safe_task(self, request: SafeTaskStartRequest) -> dict[str, Any]:
        task_id = request.task_id or f"safe-ui-{uuid.uuid4().hex[:16]}"
        thread_id = request.thread_id or task_id
        with self._lock:
            if task_id in self._remote_operation_actions:
                raise ValueError("remote-operation lifecycle action is active")
            if self.workspace.control.remote_operation_disposition(task_id) is not None:
                raise ValueError("disposed task identity cannot be reused")
            if (
                self.workspace.remote_operations.public_snapshot(task_id) is not None
                or self.workspace.remote_operations.retirement(task_id) is not None
            ):
                raise ValueError("remote-operation task identity cannot be reused")
            if task_id in self._runs:
                raise ValueError(f"task already exists: {task_id}")
            self.workspace.control.ensure_task(task_id)
            self._runs[task_id] = {
                "task_id": task_id,
                "thread_id": thread_id,
                "title": request.title,
                "status": "queued",
                "busy": True,
            }
        self.executor.submit(self._start_safe_worker, task_id, thread_id, request)
        return self.task_status(task_id)

    def task_status(self, task_id: str) -> dict[str, Any]:
        with self._lock:
            record = dict(self._runs.get(task_id, {}))
            runtime_record_exists = task_id in self._runs
        control = self.workspace.control.get_task(task_id)
        disposition = self.workspace.control.remote_operation_disposition(task_id)
        if not record and control is None and disposition is None:
            raise KeyError(task_id)
        record.setdefault("task_id", task_id)
        if control is not None:
            record["control"] = control.model_dump(mode="json")
        cancellation = self.workspace.control.cancellation_report(task_id)
        if cancellation is not None:
            record["cancellation_report"] = cancellation.to_json()
        remote_operation = self.workspace.remote_operations.public_snapshot(task_id)
        if remote_operation is not None:
            record.setdefault("thread_id", remote_operation.thread_id)
            record["remote_operation"] = self._remote_operation_snapshot(
                remote_operation.model_dump(mode="json"),
                busy=bool(record.get("busy", False)),
                recovered=not runtime_record_exists,
                disposed=disposition is not None,
            )
        if disposition is not None:
            record["status"] = disposition.outcome.value
            record["busy"] = False
            record["remote_operation_disposition"] = disposition.model_dump(mode="json")
        retirement = self.workspace.remote_operations.retirement(task_id)
        if retirement is not None:
            record["remote_operation_lease_retirement"] = retirement.model_dump(
                mode="json"
            )
        return record

    def retained_remote_operation_lease_inventory(
        self,
        *,
        after_task_id: str = "",
        limit: int = 25,
    ) -> RetainedRemoteOperationLeaseInventory:
        """Return one bounded advisory page without provider work or state mutation."""

        if limit < 1 or limit > 100:
            raise ValueError("retained lease inventory limit must be between 1 and 100")
        page_with_sentinel = self.workspace.remote_operations.retained_lease_page(
            after_task_id=after_task_id,
            limit=limit + 1,
        )
        has_more = len(page_with_sentinel) > limit
        page = page_with_sentinel[:limit]
        next_after_task_id = page[-1].task_id if has_more and page else ""

        with self._lock:
            active_actions = frozenset(self._remote_operation_actions)
            active_program_controls = frozenset(self._program_control_actions)
            busy_standalone_tasks = frozenset(
                task_id
                for task_id, record in self._runs.items()
                if record.get("busy")
            )
            program_runs = {
                program_id: dict(record)
                for program_id, record in self._program_execution_runs.items()
            }

        items: list[RetainedRemoteOperationLeaseInventoryItem] = []
        for lease in page:
            disposition = self.workspace.control.remote_operation_disposition(
                lease.task_id
            )
            if disposition is None:
                continue
            items.append(
                self._retained_remote_operation_lease_inventory_item(
                    lease,
                    disposition,
                    active_actions=active_actions,
                    active_program_controls=active_program_controls,
                    busy_standalone_tasks=busy_standalone_tasks,
                    program_runs=program_runs,
                )
            )

        inventory = RetainedRemoteOperationLeaseInventory(
            generated_at=datetime.now(UTC).isoformat(),
            items=tuple(items),
            returned_count=len(items),
            scanned_count=len(page),
            has_more=has_more,
            next_after_task_id=next_after_task_id,
        )
        return inventory

    def _retained_remote_operation_lease_inventory_item(
        self,
        lease: RetainedRemoteOperationLeaseEvidence,
        disposition: RemoteOperationDisposition,
        *,
        active_actions: frozenset[str],
        active_program_controls: frozenset[str],
        busy_standalone_tasks: frozenset[str],
        program_runs: dict[str, dict[str, Any]],
    ) -> RetainedRemoteOperationLeaseInventoryItem:
        reason_codes: list[RemoteOperationLeaseRetirementEligibilityCode] = []

        def block(code: RemoteOperationLeaseRetirementEligibilityCode) -> None:
            if code not in reason_codes:
                reason_codes.append(code)

        if lease.task_id in active_actions:
            block(
                RemoteOperationLeaseRetirementEligibilityCode.LIFECYCLE_ACTION_ACTIVE
            )
        if lease.task_id in busy_standalone_tasks:
            block(RemoteOperationLeaseRetirementEligibilityCode.LOCAL_WORKER_ACTIVE)
        if lease.state is RemoteOperationState.ACTIVE:
            block(RemoteOperationLeaseRetirementEligibilityCode.ACTIVE_PRIVATE_LEASE)
        try:
            validate_remote_operation_disposition(disposition)
        except ValueError:
            block(
                RemoteOperationLeaseRetirementEligibilityCode.DISPOSITION_AUDIT_INVALID
            )
        if not retained_lease_matches_disposition(lease, disposition):
            block(
                RemoteOperationLeaseRetirementEligibilityCode.LEASE_DISPOSITION_MISMATCH
            )

        control = self.workspace.control.get_task(lease.task_id)
        if control is None:
            block(RemoteOperationLeaseRetirementEligibilityCode.TASK_CONTROL_MISSING)
        else:
            expected_control = (
                ControlState.CANCELLED
                if disposition.outcome
                is RemoteOperationDispositionOutcome.CANCELLED
                else ControlState.FAILED
            )
            if control.state is not expected_control:
                block(
                    RemoteOperationLeaseRetirementEligibilityCode.TASK_CONTROL_STATE_MISMATCH
                )

        if lease.retirement_present:
            try:
                retirement = self.workspace.remote_operations.retirement(lease.task_id)
            except ValueError:
                block(
                    RemoteOperationLeaseRetirementEligibilityCode.RETIREMENT_RECEIPT_INVALID
                )
            else:
                if retirement is None:
                    raise ValueError(
                        "retained lease page and retirement evidence are inconsistent"
                    )
                block(
                    RemoteOperationLeaseRetirementEligibilityCode.RETIREMENT_RECEIPT_CONFLICT
                )

        try:
            binding = self.workspace.programs.execution_binding(lease.task_id)
        except KeyError:
            binding = None
        if binding is not None:
            program_id = binding.program_id
            phase_id = binding.phase_id
            slice_id = binding.slice_id or ""
        else:
            program_id = ""
            phase_id = ""
            slice_id = ""

        program_run = program_runs.get(program_id, {}) if program_id else {}
        if program_id in active_program_controls:
            block(
                RemoteOperationLeaseRetirementEligibilityCode.LIFECYCLE_ACTION_ACTIVE
            )
        if program_run.get("busy"):
            runtime_task_id = str(program_run.get("task_id", ""))
            if not runtime_task_id or runtime_task_id == lease.task_id:
                block(RemoteOperationLeaseRetirementEligibilityCode.LOCAL_WORKER_ACTIVE)

        try:
            self._validate_program_retirement_evidence(
                disposition,
                artifact_max_bytes=RETAINED_LEASE_PROGRAM_ARTIFACT_MAX_BYTES,
            )
        except ArtifactSizeLimitExceeded:
            block(
                RemoteOperationLeaseRetirementEligibilityCode.PROGRAM_EVIDENCE_OVERSIZED
            )
        except (FileNotFoundError, KeyError, ValueError) as exc:
            message = str(exc)
            if message == "Program disposition has no persisted execution binding":
                block(
                    RemoteOperationLeaseRetirementEligibilityCode.PROGRAM_BINDING_MISSING
                )
            elif message in {
                "standalone disposition conflicts with a Program binding",
                "standalone disposition has Program phase or slice identity",
                "Program binding does not match the durable disposition",
            }:
                block(
                    RemoteOperationLeaseRetirementEligibilityCode.PROGRAM_BINDING_MISMATCH
                )
            else:
                block(
                    RemoteOperationLeaseRetirementEligibilityCode.PROGRAM_EVIDENCE_INCOMPLETE
                )

        reasons = tuple(_retirement_eligibility_reason(code) for code in reason_codes)
        return RetainedRemoteOperationLeaseInventoryItem(
            task_id=lease.task_id,
            program_id=program_id,
            phase_id=phase_id,
            slice_id=slice_id,
            transport=lease.transport,
            remote_state=lease.state,
            remote_status=lease.last_status,
            remote_revision=lease.revision,
            remote_updated_at=lease.updated_at,
            disposition_audit_ref=disposition.audit_ref,
            disposition_outcome=disposition.outcome,
            disposition_recorded_at=disposition.recorded_at,
            eligible_for_retirement=not reasons,
            eligibility_reasons=reasons,
        )

    def reconcile_remote_operation(
        self,
        task_id: str,
        action: RemoteOperationAction,
    ) -> dict[str, Any]:
        if self.workspace.control.get_task(task_id) is None:
            raise KeyError(task_id)
        if self.workspace.control.remote_operation_disposition(task_id) is not None:
            raise ValueError("disposed remote operation cannot be reconciled")
        provider = self.workspace.provider
        if not isinstance(provider, RestartReconciliationModelProvider):
            raise ValueError(
                "configured provider does not support restart reconciliation"
            )
        self._begin_remote_operation_action(task_id)
        try:
            snapshot = provider.reconcile_remote_operation(task_id, action)
            return {
                "task_id": task_id,
                "action": action.value,
                "remote_operation": self._remote_operation_snapshot(
                    snapshot.model_dump(mode="json"),
                    busy=False,
                    recovered=task_id not in self._runs,
                    disposed=False,
                ),
            }
        finally:
            self._end_remote_operation_action(task_id)

    def dispose_remote_operation(
        self,
        task_id: str,
        outcome: RemoteOperationDispositionOutcome,
        *,
        reason: str,
        confirmed: bool,
    ) -> dict[str, Any]:
        """Persist terminal local disposition without making a provider request."""

        existing = self.workspace.control.remote_operation_disposition(task_id)
        if existing is not None:
            normalized_reason = reason.strip()
            if not confirmed:
                raise ValueError(
                    "remote-operation disposition requires explicit confirmation"
                )
            if existing.outcome is not outcome or existing.reason != normalized_reason:
                raise ValueError("remote-operation disposition is immutable")
            self._begin_remote_operation_action(task_id)
            try:
                self._complete_existing_disposition(existing)
                return self._disposition_result(existing)
            finally:
                self._end_remote_operation_action(task_id)

        self._begin_remote_operation_action(task_id)
        try:
            return self._dispose_remote_operation(
                task_id,
                outcome,
                reason=reason,
                confirmed=confirmed,
            )
        finally:
            self._end_remote_operation_action(task_id)

    def _dispose_remote_operation(
        self,
        task_id: str,
        outcome: RemoteOperationDispositionOutcome,
        *,
        reason: str,
        confirmed: bool,
    ) -> dict[str, Any]:
        with self._lock:
            if self.workspace.control.get_task(task_id) is None:
                raise KeyError(task_id)
            snapshot = self.workspace.remote_operations.public_snapshot(task_id)
            if snapshot is None:
                raise ValueError("task has no durable remote-operation lease")
            if snapshot.state is RemoteOperationState.ACTIVE:
                raise ValueError(
                    "active remote-operation lease requires explicit observe or cancel"
                )

            try:
                binding = self.workspace.programs.execution_binding(task_id)
            except KeyError:
                binding = None
            disposition = self.workspace.control.record_remote_operation_disposition(
                snapshot,
                outcome,
                reason=reason,
                confirmed=confirmed,
                program_id=binding.program_id if binding is not None else "",
                phase_id=binding.phase_id if binding is not None else "",
                slice_id=(binding.slice_id or "") if binding is not None else "",
            )
            if binding is not None:
                self.workspace.programs.record_remote_operation_disposition(disposition)
            run = self._runs.get(task_id)
            if run is not None:
                run.update(status=outcome.value, busy=False)

            return self._disposition_result(disposition)

    def retire_remote_operation_lease(
        self,
        task_id: str,
        *,
        disposition_audit_ref: str,
        reason: str,
        confirmed: bool,
    ) -> dict[str, Any]:
        """Retire local opaque lease persistence without contacting the provider."""

        if self.workspace.control.get_task(task_id) is None:
            raise KeyError(task_id)
        disposition = self.workspace.control.remote_operation_disposition(task_id)
        if disposition is None:
            raise ValueError(
                "private lease retirement requires a durable remote disposition"
            )
        if disposition.audit_ref != disposition_audit_ref:
            raise ValueError("private lease retirement disposition audit mismatch")

        self._begin_remote_operation_action(task_id)
        try:
            control = self.workspace.control.get_task(task_id)
            if control is None:
                raise KeyError(task_id)
            expected_control = (
                ControlState.CANCELLED
                if disposition.outcome is RemoteOperationDispositionOutcome.CANCELLED
                else ControlState.FAILED
            )
            if control.state is not expected_control:
                raise ValueError(
                    "task control state does not match the durable disposition"
                )
            self._validate_program_retirement_evidence(disposition)
            retirement = self.workspace.remote_operations.retire(
                disposition,
                reason=reason,
                confirmed=confirmed,
            )
            return {
                "task_id": task_id,
                "outcome": disposition.outcome.value,
                "program_id": disposition.program_id,
                "remote_operation_disposition": disposition.model_dump(mode="json"),
                "remote_operation_lease_retirement": retirement.model_dump(
                    mode="json"
                ),
            }
        finally:
            self._end_remote_operation_action(task_id)

    @staticmethod
    def _disposition_result(
        disposition: RemoteOperationDisposition,
    ) -> dict[str, Any]:
        return {
            "task_id": disposition.task_id,
            "outcome": disposition.outcome.value,
            "program_id": disposition.program_id,
            "remote_operation_disposition": disposition.model_dump(mode="json"),
        }

    def _complete_existing_disposition(
        self,
        disposition: RemoteOperationDisposition,
    ) -> None:
        try:
            self.workspace.programs.execution_binding(disposition.task_id)
        except KeyError:
            if disposition.program_id:
                raise ValueError(
                    "Program disposition has no persisted execution binding"
                ) from None
            return
        if not disposition.program_id:
            raise ValueError("standalone disposition conflicts with a Program binding")
        self.workspace.programs.record_remote_operation_disposition(disposition)
        self._validate_program_retirement_evidence(disposition)

    def _validate_program_retirement_evidence(
        self,
        disposition: RemoteOperationDisposition,
        *,
        artifact_max_bytes: int | None = None,
    ) -> tuple[Any, ...] | None:
        try:
            binding = self.workspace.programs.execution_binding(disposition.task_id)
        except KeyError:
            if disposition.program_id:
                raise ValueError(
                    "Program disposition has no persisted execution binding"
                ) from None
            if disposition.phase_id or disposition.slice_id:
                raise ValueError(
                    "standalone disposition has Program phase or slice identity"
                ) from None
            return None
        if not disposition.program_id:
            raise ValueError("standalone disposition conflicts with a Program binding")
        if (
            binding.program_id != disposition.program_id
            or binding.phase_id != disposition.phase_id
            or (binding.slice_id or "") != disposition.slice_id
        ):
            raise ValueError("Program binding does not match the durable disposition")
        expected_binding = (
            ProgramExecutionStatus.CANCELLED
            if disposition.outcome is RemoteOperationDispositionOutcome.CANCELLED
            else ProgramExecutionStatus.FAILED
        )
        expected_phase = (
            PhaseStatus.CANCELLED
            if disposition.outcome is RemoteOperationDispositionOutcome.CANCELLED
            else PhaseStatus.FAILED
        )
        if binding.status is not expected_binding or not binding.remote_disposition_ref:
            raise ValueError("Program binding has no matching terminal disposition")
        artifact = self._read_program_evidence_artifact(
            binding.remote_disposition_ref,
            artifact_max_bytes=artifact_max_bytes,
        )
        if artifact != disposition.model_dump(mode="json"):
            raise ValueError("Program disposition artifact does not match task control")
        phase_status = self.workspace.programs.phase_status(
            binding.program_id,
            binding.phase_id,
        )
        program_status = self.workspace.programs.status(binding.program_id)
        if phase_status is not expected_phase or program_status is not ProgramStatus.BLOCKED:
            raise ValueError("Program terminal state does not match the disposition")
        if not binding.phase_report_ref:
            raise ValueError("Program disposition has no durable phase report")
        phase_report = self._read_program_evidence_artifact(
            binding.phase_report_ref,
            artifact_max_bytes=artifact_max_bytes,
        )
        if not isinstance(phase_report, dict):
            raise ValueError("Program phase report does not match the disposition")
        reported_bindings = phase_report.get("bindings")
        if (
            phase_report.get("program_id") != binding.program_id
            or phase_report.get("requirement_hash") != binding.requirement_hash
            or phase_report.get("phase_id") != binding.phase_id
            or phase_report.get("phase_status") != expected_phase.value
            or phase_report.get("program_status") != ProgramStatus.BLOCKED.value
            or not isinstance(reported_bindings, list)
            or binding.model_dump(mode="json") not in reported_bindings
        ):
            raise ValueError("Program phase report does not match the disposition")
        return binding, phase_status, program_status, phase_report

    def _read_program_evidence_artifact(
        self,
        reference: str,
        *,
        artifact_max_bytes: int | None,
    ) -> Any:
        if artifact_max_bytes is None:
            return self.workspace.artifacts.read_json(reference)
        return self.workspace.artifacts.read_json_bounded(
            reference,
            max_bytes=artifact_max_bytes,
        )

    def _begin_remote_operation_action(self, task_id: str) -> None:
        try:
            binding = self.workspace.programs.execution_binding(task_id)
        except KeyError:
            binding = None
        with self._lock:
            if task_id in self._remote_operation_actions:
                raise ValueError("remote-operation lifecycle action is already active")
            if binding is not None and binding.program_id in self._program_control_actions:
                raise ValueError("Program control action is already active")
            standalone = self._runs.get(task_id)
            if standalone is not None and standalone.get("busy"):
                raise ValueError(
                    "remote-operation action requires no active local worker"
                )
            if binding is not None:
                runtime = self._program_execution_runs.get(binding.program_id)
                if runtime is not None and runtime.get("busy"):
                    runtime_task_id = str(runtime.get("task_id", ""))
                    if not runtime_task_id or runtime_task_id == task_id:
                        raise ValueError(
                            "remote-operation action requires no active Program worker"
                        )
            self._remote_operation_actions.add(task_id)

    def _end_remote_operation_action(self, task_id: str) -> None:
        with self._lock:
            self._remote_operation_actions.discard(task_id)

    def _begin_program_control_action(self, program_id: str) -> None:
        bindings = self.workspace.programs.execution_bindings(program_id)
        with self._lock:
            if program_id in self._program_control_actions:
                raise ValueError("Program control action is already active")
            if any(
                binding.task_id in self._remote_operation_actions
                for binding in bindings
            ):
                raise ValueError("remote-operation lifecycle action is active")
            self._program_control_actions.add(program_id)

    def _end_program_control_action(self, program_id: str) -> None:
        with self._lock:
            self._program_control_actions.discard(program_id)

    def scope_decision(self, task_id: str, approved: bool) -> dict[str, Any]:
        with self._lock:
            if task_id in self._remote_operation_actions:
                raise ValueError("remote-operation lifecycle action is active")
            if self.workspace.control.remote_operation_disposition(task_id) is not None:
                raise ValueError("disposed task cannot resume Safe work")
            if self.workspace.remote_operations.public_snapshot(task_id) is not None:
                raise ValueError(
                    "remote operation requires explicit reconciliation and disposition"
                )
            record = self._runs.get(task_id)
            if record is None:
                raise KeyError(task_id)
            if record.get("busy"):
                raise ValueError("task is currently executing")
            thread_id = str(record["thread_id"])
            record["busy"] = True
            record["status"] = "scope_approved" if approved else "scope_rejected"
        self.executor.submit(self._resume_safe_worker, task_id, thread_id, approved)
        return self.task_status(task_id)

    def pause_task(self, task_id: str, reason: str = "") -> dict[str, Any]:
        self._require_run(task_id)
        self.workspace.control.pause_task(task_id, reason=reason)
        return self.task_status(task_id)

    def resume_task(self, task_id: str) -> dict[str, Any]:
        self._require_run(task_id)
        self.workspace.control.resume_task(task_id)
        return self.task_status(task_id)

    def cancel_task(self, task_id: str, reason: str = "") -> dict[str, Any]:
        self._require_run(task_id)
        self.workspace.control.cancel_task(task_id, reason=reason)
        return self.task_status(task_id)

    def control_program(
        self,
        program_id: str,
        action: Literal["approve", "pause", "resume", "cancel"],
        *,
        reason: str = "",
        plan_hash: str = "",
    ) -> None:
        """Serialize Program controls with disposition-bound lease retirement."""

        self._begin_program_control_action(program_id)
        try:
            if action == "approve":
                self.workspace.programs.approve_program(program_id, plan_hash)
            elif action == "pause":
                self.workspace.programs.pause(program_id, reason=reason)
                self.workspace.programs.ready_phases(program_id)
            elif action == "resume":
                self.workspace.programs.resume(program_id)
            else:
                self.workspace.programs.cancel(program_id, reason=reason)
        finally:
            self._end_program_control_action(program_id)

    def program_execution_status(self, program_id: str) -> dict[str, Any]:
        program_status = self.workspace.programs.status(program_id)
        bindings = self.workspace.programs.execution_bindings(program_id)
        with self._lock:
            runtime_record = dict(self._program_execution_runs.get(program_id, {}))
        pending = tuple(
            binding
            for binding in bindings
            if binding.status
            in {
                ProgramExecutionStatus.STARTING,
                ProgramExecutionStatus.AWAITING_SCOPE_APPROVAL,
                ProgramExecutionStatus.RUNNING,
            }
        )
        return {
            "program_id": program_id,
            "program_status": program_status.value,
            "runtime": {
                "busy": bool(runtime_record.get("busy", False)),
                "action": str(runtime_record.get("action", "")),
                "task_id": str(runtime_record.get("task_id", "")),
                "status": str(runtime_record.get("status", "idle")),
                "recovered_pending": bool(pending and not runtime_record),
                "requires_explicit_action": bool(pending),
                "error_type": str(runtime_record.get("error_type", "")),
                "error": str(runtime_record.get("error", "")),
            },
            "bindings": [
                self._program_execution_binding_snapshot(
                    binding,
                    runtime_record=runtime_record,
                )
                for binding in bindings
            ],
        }

    def start_next_program_execution(
        self,
        program_id: str,
        request: ProgramExecutionStartRequest,
    ) -> dict[str, Any]:
        self.workspace.programs.plan(program_id)
        bindings = self.workspace.programs.execution_bindings(program_id)
        with self._lock:
            if any(
                binding.task_id in self._remote_operation_actions
                for binding in bindings
            ):
                raise ValueError("remote-operation lifecycle action is active")
            current = self._program_execution_runs.get(program_id)
            if current is not None and current.get("busy"):
                raise ValueError("program execution is currently busy")
            self._program_execution_runs[program_id] = {
                "busy": True,
                "action": "start_next",
                "task_id": "",
                "status": "queued",
            }
        try:
            self.executor.submit(
                self._start_program_execution_worker,
                program_id,
                request,
            )
        except Exception:
            self._set_program_execution_run(
                program_id,
                busy=False,
                status="failed",
            )
            raise
        return self.program_execution_status(program_id)

    def continue_program_execution(
        self,
        program_id: str,
        task_id: str,
        request: ProgramExecutionContinueRequest,
    ) -> dict[str, Any]:
        with self._lock:
            binding = self.workspace.programs.execution_binding(task_id)
            if binding.program_id != program_id:
                raise ValueError("execution binding belongs to another program")
            if binding.status not in {
                ProgramExecutionStatus.STARTING,
                ProgramExecutionStatus.AWAITING_SCOPE_APPROVAL,
                ProgramExecutionStatus.RUNNING,
            }:
                raise ValueError("execution binding is not awaiting an explicit action")
            if task_id in self._remote_operation_actions:
                raise ValueError("remote-operation lifecycle action is active")
            if self.workspace.control.remote_operation_disposition(task_id) is not None:
                raise ValueError("disposed execution binding cannot continue")
            if self.workspace.remote_operations.public_snapshot(task_id) is not None:
                raise ValueError(
                    "remote operation requires explicit reconciliation and disposition"
                )
            current = self._program_execution_runs.get(program_id)
            if current is not None and current.get("busy"):
                raise ValueError("program execution is currently busy")
            self._program_execution_runs[program_id] = {
                "busy": True,
                "action": "continue",
                "task_id": task_id,
                "status": "queued",
            }
        try:
            self.executor.submit(
                self._continue_program_execution_worker,
                program_id,
                task_id,
                request,
            )
        except Exception:
            self._set_program_execution_run(
                program_id,
                busy=False,
                status="failed",
            )
            raise
        return self.program_execution_status(program_id)

    def _require_run(self, task_id: str) -> None:
        with self._lock:
            if task_id not in self._runs:
                raise KeyError(task_id)
            if task_id in self._remote_operation_actions:
                raise ValueError("remote-operation lifecycle action is active")
            if self.workspace.control.remote_operation_disposition(task_id) is not None:
                raise ValueError("disposed task is terminal")

    def _start_safe_worker(
        self,
        task_id: str,
        thread_id: str,
        request: SafeTaskStartRequest,
    ) -> None:
        try:
            control = self.workspace.control.task_action(task_id)
            if control.value == "cancel":
                self._set_run(task_id, status="cancelled", busy=False)
                return
            if control.value == "pause":
                self._set_run(task_id, status="paused", busy=False)
                return
            service = self.workspace.discovered_safe(
                state_root=self.state_root / "safe",
                allow_local_sources=self.allow_local_sources,
            )
            result = service.start(
                task_id=task_id,
                thread_id=thread_id,
                title=request.title,
                objective=request.objective,
                repository=RepositorySpec(
                    url=request.repository,
                    base_ref=request.ref,
                ),
                policy=request.policy,
                test_profiles=request.test_profiles,
                acceptance_criteria=request.acceptance_criteria,
            )
            state = result.get("state", {})
            self._set_run(
                task_id,
                status=str(state.get("status", "awaiting_scope_approval")),
                busy=False,
                result=result,
            )
        except Exception as exc:  # execution errors become bounded task state
            self._set_run(
                task_id,
                status="failed",
                busy=False,
                error_type=type(exc).__name__,
                error=sanitize_text(str(exc))[:2000],
            )

    def _resume_safe_worker(self, task_id: str, thread_id: str, approved: bool) -> None:
        try:
            service = self.workspace.discovered_safe(
                state_root=self.state_root / "safe",
                allow_local_sources=self.allow_local_sources,
            )
            result = service.resume(thread_id, approved)
            self._set_run(
                task_id,
                status=str(result.get("status", "completed")),
                busy=False,
                result=result,
            )
        except Exception as exc:
            self._set_run(
                task_id,
                status="failed",
                busy=False,
                error_type=type(exc).__name__,
                error=sanitize_text(str(exc))[:2000],
            )

    def _start_program_execution_worker(
        self,
        program_id: str,
        request: ProgramExecutionStartRequest,
    ) -> None:
        try:
            binding = self.workspace.start_next_program_execution(
                program_id=program_id,
                current_requirement_hash=request.current_requirement_hash,
                repository=RepositorySpec(
                    url=request.repository,
                    base_ref=request.ref,
                ),
                policy=request.policy,
                test_profiles=request.test_profiles,
                state_root=self.state_root / "safe",
                allow_local_sources=self.allow_local_sources,
            )
            self._set_program_execution_run(
                program_id,
                busy=False,
                task_id=binding.task_id,
                status=binding.status.value,
                error_type="",
                error="",
            )
        except Exception as exc:
            self._set_program_execution_run(
                program_id,
                busy=False,
                status="failed",
                error_type=type(exc).__name__,
                error=sanitize_text(str(exc))[:2000],
            )

    def _continue_program_execution_worker(
        self,
        program_id: str,
        task_id: str,
        request: ProgramExecutionContinueRequest,
    ) -> None:
        try:
            binding = self.workspace.continue_program_execution(
                program_id=program_id,
                task_id=task_id,
                current_requirement_hash=request.current_requirement_hash,
                approved=request.approved,
                state_root=self.state_root / "safe",
                allow_local_sources=self.allow_local_sources,
            )
            self._set_program_execution_run(
                program_id,
                busy=False,
                task_id=binding.task_id,
                status=binding.status.value,
                error_type="",
                error="",
            )
        except Exception as exc:
            self._set_program_execution_run(
                program_id,
                busy=False,
                status="failed",
                error_type=type(exc).__name__,
                error=sanitize_text(str(exc))[:2000],
            )

    def _set_run(self, task_id: str, **changes: Any) -> None:
        with self._lock:
            record = self._runs.setdefault(task_id, {"task_id": task_id})
            record.update(changes)

    def _set_program_execution_run(self, program_id: str, **changes: Any) -> None:
        with self._lock:
            record = self._program_execution_runs.setdefault(program_id, {})
            record.update(changes)

    def _program_execution_binding_snapshot(
        self,
        binding: ProgramExecutionBinding,
        *,
        runtime_record: dict[str, Any],
    ) -> dict[str, Any]:
        snapshot = binding.model_dump(mode="json")
        control = self.workspace.control.get_task(binding.task_id)
        if control is not None:
            snapshot["control"] = control.model_dump(mode="json")
        cancellation = self.workspace.control.cancellation_report(binding.task_id)
        if cancellation is not None:
            snapshot["cancellation_report"] = cancellation.to_json()
        remote_operation = self.workspace.remote_operations.public_snapshot(
            binding.task_id
        )
        disposition = self.workspace.control.remote_operation_disposition(binding.task_id)
        if remote_operation is not None:
            runtime_task_id = str(runtime_record.get("task_id", ""))
            matching_runtime = bool(
                runtime_record
                and (not runtime_task_id or runtime_task_id == binding.task_id)
            )
            snapshot["remote_operation"] = self._remote_operation_snapshot(
                remote_operation.model_dump(mode="json"),
                busy=bool(matching_runtime and runtime_record.get("busy", False)),
                recovered=not matching_runtime,
                disposed=disposition is not None,
            )
        if disposition is not None:
            snapshot["remote_operation_disposition"] = disposition.model_dump(
                mode="json"
            )
        retirement = self.workspace.remote_operations.retirement(binding.task_id)
        if retirement is not None:
            snapshot["remote_operation_lease_retirement"] = retirement.model_dump(
                mode="json"
            )
        return snapshot

    @staticmethod
    def _remote_operation_snapshot(
        snapshot: dict[str, Any],
        *,
        busy: bool,
        recovered: bool,
        disposed: bool,
    ) -> dict[str, Any]:
        active = snapshot.get("state") == RemoteOperationState.ACTIVE.value
        snapshot["recovered_pending"] = bool(active and recovered)
        snapshot["requires_explicit_action"] = bool(active and not busy and not disposed)
        snapshot["requires_explicit_disposition"] = bool(
            not active and not busy and not disposed
        )
        return snapshot


def create_product_app(
    runtime: ProductWebRuntime,
    *,
    ui_dist: Path | None = None,
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        yield
        runtime.close()

    app = FastAPI(
        title="Universal Coding Agent Control API",
        version="0.1.0",
        lifespan=lifespan,
    )

    @app.exception_handler(DocumentValidationError)
    async def document_error(_request: Request, exc: DocumentValidationError):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )

    @app.exception_handler(KeyError)
    async def key_error(_request: Request, exc: KeyError):
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc.args[0])},
        )

    @app.exception_handler(ValueError)
    async def value_error(_request: Request, exc: ValueError):
        return JSONResponse(
            status_code=400,
            content={"detail": sanitize_text(str(exc))[:2000]},
        )

    @app.exception_handler(ModelProviderError)
    async def provider_error(_request: Request, exc: ModelProviderError):
        return JSONResponse(
            status_code=409,
            content={
                "detail": {
                    "code": exc.code,
                    "message": sanitize_text(str(exc))[:2000],
                }
            },
        )

    @app.get("/api/health")
    def health() -> dict[str, Any]:
        return {
            "status": "ok",
            "api": "uca-product-control",
            "browser_credentials": False,
            "allow_local_sources": runtime.allow_local_sources,
        }

    @app.get(
        "/api/remote-operations/retained-leases",
        response_model=RetainedRemoteOperationLeaseInventory,
    )
    def retained_remote_operation_leases(
        response: Response,
        after_task_id: str = Query(
            default="",
            max_length=128,
            pattern=r"^$|^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$",
        ),
        limit: int = Query(default=25, ge=1, le=100),
    ) -> RetainedRemoteOperationLeaseInventory:
        response.headers["Cache-Control"] = "no-store"
        return runtime.retained_remote_operation_lease_inventory(
            after_task_id=after_task_id,
            limit=limit,
        )

    @app.post("/api/search")
    def search(request: SearchRequest) -> dict[str, Any]:
        hits = runtime.workspace.search.search(request.query, top_k=request.top_k)
        return {"hits": [item.model_dump(mode="json") for item in hits]}

    @app.get("/api/documents")
    def list_documents(scope_id: str | None = None) -> dict[str, Any]:
        documents = runtime.workspace.documents.list(scope_id=scope_id)
        return {
            "documents": [
                item.model_dump(mode="json")
                for item in documents
            ]
        }

    @app.post("/api/documents", status_code=201)
    def upload_document(request: DocumentUploadRequest) -> dict[str, Any]:
        document = runtime.workspace.upload_document(
            document_id=request.document_id,
            filename=request.filename,
            content=request.content,
            role=request.role,
            scope=request.scope,
            scope_id=request.scope_id,
        )
        return document.model_dump(mode="json")

    @app.post("/api/requirements/analyze")
    def analyze_requirement(request: RequirementAnalyzeRequest) -> dict[str, Any]:
        result = runtime.workspace.requirements.analyze(
            alignment_id=request.alignment_id,
            title=request.title,
            objective=request.objective,
            answers=request.answers,
            previous=request.previous,
        )
        return result.model_dump(mode="json")

    @app.post("/api/requirements/approve")
    def approve_requirement(request: RequirementApproveRequest) -> dict[str, Any]:
        result = runtime.workspace.requirements.approve(request.contract)
        return result.model_dump(mode="json")

    @app.post("/api/programs", status_code=201)
    def create_program(request: ProgramCreateRequest) -> dict[str, Any]:
        plan = runtime.workspace.programs.create_program(
            program_id=request.program_id,
            requirement=request.requirement,
            requirement_hash=request.requirement_hash,
        )
        return _program_snapshot(runtime.workspace, plan.program_id)

    @app.get("/api/programs/{program_id}")
    def program_status(program_id: str) -> dict[str, Any]:
        return _program_snapshot(runtime.workspace, program_id)

    @app.post("/api/programs/{program_id}/approve")
    def approve_program(
        program_id: str,
        request: ProgramApproveRequest,
    ) -> dict[str, Any]:
        runtime.control_program(
            program_id,
            "approve",
            plan_hash=request.plan_hash,
        )
        return _program_snapshot(runtime.workspace, program_id)

    @app.post("/api/programs/{program_id}/pause")
    def pause_program(
        program_id: str,
        request: ControlRequest,
    ) -> dict[str, Any]:
        runtime.control_program(program_id, "pause", reason=request.reason)
        return _program_snapshot(runtime.workspace, program_id)

    @app.post("/api/programs/{program_id}/resume")
    def resume_program(program_id: str) -> dict[str, Any]:
        runtime.control_program(program_id, "resume")
        return _program_snapshot(runtime.workspace, program_id)

    @app.post("/api/programs/{program_id}/cancel")
    def cancel_program(
        program_id: str,
        request: ControlRequest,
    ) -> dict[str, Any]:
        runtime.control_program(program_id, "cancel", reason=request.reason)
        return _program_snapshot(runtime.workspace, program_id)

    @app.get("/api/programs/{program_id}/executions")
    def program_execution_status(program_id: str) -> dict[str, Any]:
        return runtime.program_execution_status(program_id)

    @app.post("/api/programs/{program_id}/executions/start-next", status_code=202)
    def start_next_program_execution(
        program_id: str,
        request: ProgramExecutionStartRequest,
    ) -> dict[str, Any]:
        if not request.test_profiles:
            raise HTTPException(
                status_code=422,
                detail="at least one trusted test profile is required",
            )
        return runtime.start_next_program_execution(program_id, request)

    @app.post(
        "/api/programs/{program_id}/executions/{task_id}/continue",
        status_code=202,
    )
    def continue_program_execution(
        program_id: str,
        task_id: str,
        request: ProgramExecutionContinueRequest,
    ) -> dict[str, Any]:
        return runtime.continue_program_execution(program_id, task_id, request)

    @app.post("/api/tasks/safe", status_code=202)
    def start_safe_task(request: SafeTaskStartRequest) -> dict[str, Any]:
        if not request.test_profiles:
            raise HTTPException(
                status_code=422,
                detail="at least one trusted test profile is required",
            )
        return runtime.start_safe_task(request)

    @app.get("/api/tasks/{task_id}")
    def task_status(task_id: str) -> dict[str, Any]:
        return runtime.task_status(task_id)

    @app.post("/api/tasks/{task_id}/scope-decision", status_code=202)
    def scope_decision(
        task_id: str,
        request: ScopeDecisionRequest,
    ) -> dict[str, Any]:
        return runtime.scope_decision(task_id, request.approved)

    @app.post("/api/tasks/{task_id}/pause")
    def pause_task(task_id: str, request: ControlRequest) -> dict[str, Any]:
        return runtime.pause_task(task_id, request.reason)

    @app.post("/api/tasks/{task_id}/resume")
    def resume_task(task_id: str) -> dict[str, Any]:
        return runtime.resume_task(task_id)

    @app.post("/api/tasks/{task_id}/cancel")
    def cancel_task(task_id: str, request: ControlRequest) -> dict[str, Any]:
        return runtime.cancel_task(task_id, request.reason)

    @app.post("/api/tasks/{task_id}/remote-operation/reconcile")
    def reconcile_remote_operation(
        task_id: str,
        request: RemoteOperationReconcileRequest,
    ) -> dict[str, Any]:
        return runtime.reconcile_remote_operation(task_id, request.action)

    @app.post("/api/tasks/{task_id}/remote-operation/dispose")
    def dispose_remote_operation(
        task_id: str,
        request: RemoteOperationDispositionRequest,
    ) -> dict[str, Any]:
        return runtime.dispose_remote_operation(
            task_id,
            request.outcome,
            reason=request.reason,
            confirmed=request.confirmed,
        )

    @app.post("/api/tasks/{task_id}/remote-operation/retire")
    def retire_remote_operation_lease(
        task_id: str,
        request: RemoteOperationLeaseRetirementRequest,
    ) -> dict[str, Any]:
        return runtime.retire_remote_operation_lease(
            task_id,
            disposition_audit_ref=request.disposition_audit_ref,
            reason=request.reason,
            confirmed=request.confirmed,
        )

    resolved_ui = ui_dist.resolve() if ui_dist is not None else None
    if resolved_ui is not None and resolved_ui.is_dir():
        app.mount(
            "/",
            StaticFiles(directory=resolved_ui, html=True),
            name="ui",
        )
    else:

        @app.get("/")
        def api_root() -> dict[str, str]:
            return {
                "service": "Universal Coding Agent Control API",
                "ui": "not-built",
                "hint": "build web/ and restart with --ui-dist web/dist",
            }

    return app


def is_loopback_host(host: str) -> bool:
    if host.strip().lower() == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def _program_snapshot(
    workspace: ProductWorkspace,
    program_id: str,
) -> dict[str, Any]:
    plan = workspace.programs.plan(program_id)
    return {
        "program_id": program_id,
        "status": workspace.programs.status(program_id).value,
        "plan_hash": plan.canonical_hash(),
        "plan": plan.model_dump(mode="json"),
        "phases": [
            {
                "phase_id": phase.phase_id,
                "title": phase.title,
                "status": workspace.programs.phase_status(
                    program_id,
                    phase.phase_id,
                ).value,
                "dependencies": list(phase.dependencies),
            }
            for phase in plan.phases
        ],
    }
