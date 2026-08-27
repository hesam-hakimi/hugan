from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any, Protocol

from universal_coding_agent.core.cancellation import CancellationCoordinator
from universal_coding_agent.core.models import ModelRequest
from universal_coding_agent.core.remote_operations import (
    RemoteOperationAction,
    RemoteOperationDisposition,
    RemoteOperationDispositionOutcome,
    RemoteOperationLeaseRetirement,
    RemoteOperationSnapshot,
    RemoteOperationState,
)
from universal_coding_agent.product.remote_operations import (
    SqliteRemoteOperationLeaseStore,
)
from universal_coding_agent.product.task_control import TaskControlService
from universal_coding_agent.product.workspace import ProductWorkspace
from universal_coding_agent.providers.base import ModelProviderError
from universal_coding_agent.safety.sanitizer import sanitize_text
from universal_coding_agent.testlab.openai_responses import OpenAIResponsesProvider
from universal_coding_agent.web.app import ProductWebRuntime

_TASK_ID = "pretransfer-openai-background-reconciliation-task"
_THREAD_ID = "pretransfer-openai-background-reconciliation-thread"
_SUMMARY_NAME = "background-reconciliation-live-summary.json"
_PRIVATE_DATABASE_NAME = "private-remote-operations.sqlite"


class RestartWorker(Protocol):
    returncode: int | None

    def poll(self) -> int | None: ...

    def terminate(self) -> None: ...

    def kill(self) -> None: ...

    def wait(self, timeout: float | None = None) -> int: ...


WorkerFactory = Callable[[Path, str, float], RestartWorker]


def run_openai_background_reconciliation_live(
    state_root: Path,
    provider: OpenAIResponsesProvider,
    *,
    source_root: Path,
    timeout_seconds: float,
    worker_factory: WorkerFactory | None = None,
) -> dict[str, Any]:
    """Qualify restart recovery followed only by explicit remote observe/cancel calls."""

    state_root.mkdir(parents=True, exist_ok=True)
    source_before = _source_snapshot(source_root)
    private_database = state_root / _PRIVATE_DATABASE_NAME
    bootstrap_store = SqliteRemoteOperationLeaseStore(private_database)
    if bootstrap_store.public_snapshot(_TASK_ID) is not None:
        bootstrap_store.close()
        raise ValueError("restart reconciliation qualification requires a fresh state root")
    bootstrap_store.close()
    factory = worker_factory or _start_worker
    worker = factory(state_root, source_before["head_sha"], timeout_seconds)
    created_snapshot = _wait_for_active_lease(
        private_database,
        worker,
        timeout_seconds=min(15.0, timeout_seconds),
    )
    worker_terminated, worker_killed = _terminate_worker(worker)

    errors: list[BaseException] = []
    request_events: list[str] = []
    recovered_snapshot: RemoteOperationSnapshot | None = None
    observed_snapshot: RemoteOperationSnapshot | None = None
    cancelled_snapshot: RemoteOperationSnapshot | None = None
    terminal_snapshot: RemoteOperationSnapshot | None = None
    automatic_provider_calls = -1
    explicit_observe_calls = 0
    explicit_cancel_calls = 0

    reopened = SqliteRemoteOperationLeaseStore(private_database)
    provider.bind_remote_operation_store(reopened.provider_store())
    original_request_json = provider._request_json

    def counted_request_json(
        *,
        method: str,
        endpoint: str,
        payload: dict[str, Any] | None = None,
        timeout_seconds: float | None = None,
    ) -> dict[str, Any]:
        request_events.append(method)
        return original_request_json(
            method=method,
            endpoint=endpoint,
            payload=payload,
            timeout_seconds=timeout_seconds,
        )

    provider._request_json = counted_request_json
    try:
        recovered_snapshot = provider.remote_operation_snapshot(_TASK_ID)
        automatic_provider_calls = len(request_events)
        if (
            recovered_snapshot is not None
            and recovered_snapshot.state is RemoteOperationState.ACTIVE
        ):
            observed_snapshot = provider.reconcile_remote_operation(
                _TASK_ID,
                RemoteOperationAction.OBSERVE,
            )
            explicit_observe_calls += 1
            if observed_snapshot.state is RemoteOperationState.ACTIVE:
                cancelled_snapshot = provider.reconcile_remote_operation(
                    _TASK_ID,
                    RemoteOperationAction.CANCEL,
                )
                explicit_cancel_calls += 1
                terminal_snapshot = cancelled_snapshot
                deadline = time.monotonic() + min(30.0, timeout_seconds)
                while (
                    terminal_snapshot.state is RemoteOperationState.ACTIVE
                    and time.monotonic() < deadline
                ):
                    time.sleep(0.25)
                    terminal_snapshot = provider.reconcile_remote_operation(
                        _TASK_ID,
                        RemoteOperationAction.OBSERVE,
                    )
                    explicit_observe_calls += 1
            else:
                terminal_snapshot = observed_snapshot
    except BaseException as exc:
        errors.append(exc)
    finally:
        cleanup = reopened.public_snapshot(_TASK_ID)
        if cleanup is not None and cleanup.state is RemoteOperationState.ACTIVE:
            try:
                provider.reconcile_remote_operation(
                    _TASK_ID,
                    RemoteOperationAction.CANCEL,
                )
                explicit_cancel_calls += 1
            except BaseException as exc:
                errors.append(exc)
        reopened.close()

    durable_store = SqliteRemoteOperationLeaseStore(private_database)
    try:
        durable_snapshot = durable_store.public_snapshot(_TASK_ID)
    finally:
        durable_store.close()

    disposition: RemoteOperationDisposition | None = None
    durable_disposition: RemoteOperationDisposition | None = None
    provider_calls_during_disposition = -1
    calls_before_disposition = len(request_events)
    task_control_path = state_root / "control.sqlite"
    task_control = TaskControlService(task_control_path)
    try:
        task_control.ensure_task(_TASK_ID)
        if durable_snapshot is not None:
            disposition = task_control.record_remote_operation_disposition(
                durable_snapshot,
                RemoteOperationDispositionOutcome.CANCELLED,
                reason="Live qualification confirmed terminal remote cancellation.",
                confirmed=True,
            )
        provider_calls_during_disposition = (
            len(request_events) - calls_before_disposition
        )
    except BaseException as exc:
        errors.append(exc)
    finally:
        task_control.close()

    reopened_control = TaskControlService(task_control_path)
    try:
        durable_disposition = reopened_control.remote_operation_disposition(_TASK_ID)
    finally:
        reopened_control.close()

    retained_inventory_before_retirement: dict[str, Any] | None = None
    provider_calls_during_inventory = -1
    inventory_eligible = False
    inventory_private_fields_absent = False
    private_identifier = ""
    lifecycle_reservation_owner = ""
    calls_before_inventory = len(request_events)
    inventory_workspace = ProductWorkspace.create(state_root, provider)
    inventory_runtime = ProductWebRuntime(
        workspace=inventory_workspace,
        state_root=state_root / "inventory-runtime",
    )
    try:
        inventory_private_lease = inventory_workspace.remote_operations.private_lease(
            _TASK_ID
        )
        if inventory_private_lease is not None:
            private_identifier = inventory_private_lease.operation_id
        retained_inventory_before_retirement = (
            inventory_runtime.retained_remote_operation_lease_inventory(
                limit=25,
            ).model_dump(mode="json")
        )
        items = retained_inventory_before_retirement["items"]
        inventory_eligible = bool(
            len(items) == 1
            and items[0]["task_id"] == _TASK_ID
            and items[0]["eligible_for_retirement"]
            and not items[0]["eligibility_reasons"]
            and items[0]["preview_is_advisory"]
            and items[0]["action_revalidation_required"]
        )
        inventory_private_fields_absent = bool(
            not _contains_field(
                retained_inventory_before_retirement,
                {
                    "operation_id",
                    "response_id",
                    "thread_id",
                    "operation_ref",
                    "transport_scope",
                    "base_sha",
                    "reason",
                    "retirement_ref",
                },
            )
            and (
                not private_identifier
                or private_identifier
                not in json.dumps(retained_inventory_before_retirement, sort_keys=True)
            )
        )
        provider_calls_during_inventory = len(request_events) - calls_before_inventory
        lifecycle_reservation_owner = (
            inventory_runtime.workspace.lifecycle_reservations.reserve_remote_operation(
                _TASK_ID
            )
        )
    except BaseException as exc:
        errors.append(exc)
    finally:
        inventory_runtime.close()

    durable_lifecycle_reservation_reloaded = False
    conflicting_lifecycle_action_blocked_after_restart = False
    provider_calls_during_lifecycle_reservation_restart = -1
    calls_before_lifecycle_reservation_restart = len(request_events)
    reservation_recovery_workspace = ProductWorkspace.create(state_root, provider)
    try:
        durable_lifecycle_reservation_reloaded = bool(
            _TASK_ID
            in reservation_recovery_workspace.lifecycle_reservations.snapshot().remote_task_ids
        )
        try:
            reservation_recovery_workspace.lifecycle_reservations.reserve_remote_operation(
                _TASK_ID
            )
        except ValueError:
            conflicting_lifecycle_action_blocked_after_restart = True
        if lifecycle_reservation_owner:
            reservation_recovery_workspace.lifecycle_reservations.release_remote_operation(
                _TASK_ID,
                lifecycle_reservation_owner,
            )
        provider_calls_during_lifecycle_reservation_restart = (
            len(request_events) - calls_before_lifecycle_reservation_restart
        )
    except BaseException as exc:
        errors.append(exc)
    finally:
        reservation_recovery_workspace.close()

    retirement: RemoteOperationLeaseRetirement | None = None
    durable_retirement: RemoteOperationLeaseRetirement | None = None
    disposition_after_retirement: RemoteOperationDisposition | None = None
    provider_calls_during_retirement = -1
    private_lease_absent_after_retirement = False
    durable_private_lease_absent = False
    private_identifier_absent_from_active_database = False
    calls_before_retirement = len(request_events)
    retirement_store = SqliteRemoteOperationLeaseStore(private_database)
    try:
        private_lease = retirement_store.private_lease(_TASK_ID)
        if private_lease is not None:
            private_identifier = private_lease.operation_id
        if durable_disposition is not None:
            retirement = retirement_store.retire(
                durable_disposition,
                reason="Live qualification explicitly retired the local private lease.",
                confirmed=True,
            )
            private_lease_absent_after_retirement = bool(
                retirement_store.private_lease(_TASK_ID) is None
                and retirement_store.public_snapshot(_TASK_ID) is None
            )
        provider_calls_during_retirement = (
            len(request_events) - calls_before_retirement
        )
    except BaseException as exc:
        errors.append(exc)
    finally:
        retirement_store.close()

    if private_identifier:
        private_identifier_absent_from_active_database = (
            private_identifier.encode("utf-8") not in private_database.read_bytes()
        )

    reopened_retirement_store = SqliteRemoteOperationLeaseStore(private_database)
    try:
        durable_retirement = reopened_retirement_store.retirement(_TASK_ID)
        durable_private_lease_absent = bool(
            reopened_retirement_store.private_lease(_TASK_ID) is None
            and reopened_retirement_store.public_snapshot(_TASK_ID) is None
        )
    finally:
        reopened_retirement_store.close()

    control_after_retirement = TaskControlService(task_control_path)
    try:
        disposition_after_retirement = (
            control_after_retirement.remote_operation_disposition(_TASK_ID)
        )
    finally:
        control_after_retirement.close()

    retained_inventory_after_retirement: dict[str, Any] | None = None
    provider_calls_during_post_retirement_inventory = -1
    inventory_empty_after_retirement = False
    calls_before_post_retirement_inventory = len(request_events)
    post_retirement_workspace = ProductWorkspace.create(state_root, provider)
    post_retirement_runtime = ProductWebRuntime(
        workspace=post_retirement_workspace,
        state_root=state_root / "post-retirement-inventory-runtime",
    )
    try:
        retained_inventory_after_retirement = (
            post_retirement_runtime.retained_remote_operation_lease_inventory(
                limit=25,
            ).model_dump(mode="json")
        )
        inventory_empty_after_retirement = bool(
            retained_inventory_after_retirement["items"] == []
            and retained_inventory_after_retirement["returned_count"] == 0
        )
        provider_calls_during_post_retirement_inventory = (
            len(request_events) - calls_before_post_retirement_inventory
        )
    except BaseException as exc:
        errors.append(exc)
    finally:
        post_retirement_runtime.close()

    source_after = _source_snapshot(source_root)
    source_preserved = source_before == source_after and not source_before["status"]
    created_json = _snapshot_json(created_snapshot)
    recovered_json = _snapshot_json(recovered_snapshot)
    observed_json = _snapshot_json(observed_snapshot)
    cancelled_json = _snapshot_json(cancelled_snapshot)
    terminal_json = _snapshot_json(terminal_snapshot)
    durable_json = _snapshot_json(durable_snapshot)
    disposition_json = _disposition_json(disposition)
    durable_disposition_json = _disposition_json(durable_disposition)
    retirement_json = _retirement_json(retirement)
    durable_retirement_json = _retirement_json(durable_retirement)
    stable_reference = bool(
        created_snapshot
        and recovered_snapshot
        and durable_snapshot
        and created_snapshot.operation_ref
        == recovered_snapshot.operation_ref
        == durable_snapshot.operation_ref
    )
    identity_and_base_bound = bool(
        created_snapshot
        and recovered_snapshot
        and durable_snapshot
        and created_snapshot.task_id == _TASK_ID
        and created_snapshot.thread_id == _THREAD_ID
        and created_snapshot.base_sha == source_before["head_sha"]
        and created_snapshot.transport == "openai_responses"
        and created_snapshot.transport_scope
        == recovered_snapshot.transport_scope
        == durable_snapshot.transport_scope
    )
    terminal_cancelled = bool(
        terminal_snapshot
        and terminal_snapshot.state is RemoteOperationState.TERMINAL
        and terminal_snapshot.last_status == "cancelled"
        and terminal_snapshot.cancellation_requested
    )
    durable_terminal_reloaded = bool(
        terminal_snapshot
        and durable_snapshot
        and terminal_snapshot == durable_snapshot
    )
    disposition_matches_remote = bool(
        disposition
        and durable_snapshot
        and disposition.outcome is RemoteOperationDispositionOutcome.CANCELLED
        and disposition.operation_ref == durable_snapshot.operation_ref
        and disposition.remote_revision == durable_snapshot.revision
        and disposition.remote_state is RemoteOperationState.TERMINAL
        and disposition.remote_status == "cancelled"
        and disposition.provider_confirmed_cancelled
        and disposition.confirmed_by_operator
        and disposition.provider_calls_made == 0
        and not disposition.output_consumed
        and not disposition.graph_resumed
        and not disposition.program_phase_advanced
    )
    durable_disposition_reloaded = bool(
        disposition and durable_disposition and disposition == durable_disposition
    )
    retirement_matches_disposition = bool(
        retirement
        and durable_disposition
        and retirement.task_id == durable_disposition.task_id
        and retirement.disposition_audit_ref == durable_disposition.audit_ref
        and retirement.disposition_outcome is durable_disposition.outcome
        and retirement.transport == durable_disposition.transport
        and retirement.transport_scope == durable_disposition.transport_scope
        and retirement.operation_ref == durable_disposition.operation_ref
        and retirement.base_sha == durable_disposition.base_sha
        and retirement.remote_state is durable_disposition.remote_state
        and retirement.remote_status == durable_disposition.remote_status
        and retirement.remote_revision == durable_disposition.remote_revision
        and retirement.remote_updated_at == durable_disposition.remote_updated_at
        and retirement.confirmed_by_operator
        and retirement.private_lease_rows_retired == 1
        and not retirement.private_identifier_retained_in_active_store
        and retirement.provider_calls_made == 0
        and not retirement.output_consumed
        and not retirement.graph_resumed
        and retirement.task_outcome_changes_made == 0
        and retirement.program_outcome_changes_made == 0
        and not retirement.program_phase_advanced
    )
    durable_retirement_reloaded = bool(
        retirement and durable_retirement and retirement == durable_retirement
    )
    disposition_preserved_after_retirement = bool(
        durable_disposition
        and disposition_after_retirement
        and durable_disposition == disposition_after_retirement
    )
    summary = {
        "provider": "openai_responses",
        "model": provider.model,
        "qualified": False,
        "background_cancellation_enabled": provider.background_cancellation,
        "restart_worker": {
            "lease_observed_before_restart": bool(created_snapshot),
            "local_process_terminated": worker_terminated,
            "local_process_killed_after_grace": worker_killed,
        },
        "created_operation": created_json,
        "recovered_operation": recovered_json,
        "explicit_observe_result": observed_json,
        "explicit_cancel_result": cancelled_json,
        "terminal_operation": terminal_json,
        "durable_operation": durable_json,
        "automatic_provider_calls_after_restart": automatic_provider_calls,
        "explicit_observe_calls": explicit_observe_calls,
        "explicit_cancel_calls": explicit_cancel_calls,
        "stable_operation_reference": stable_reference,
        "identity_and_base_bound": identity_and_base_bound,
        "terminal_cancelled": terminal_cancelled,
        "durable_terminal_reloaded": durable_terminal_reloaded,
        "explicit_terminal_disposition": disposition_json,
        "durable_terminal_disposition": durable_disposition_json,
        "provider_calls_during_disposition": provider_calls_during_disposition,
        "disposition_matches_remote": disposition_matches_remote,
        "durable_disposition_reloaded": durable_disposition_reloaded,
        "retained_lease_inventory_before_retirement": (
            retained_inventory_before_retirement
        ),
        "provider_calls_during_inventory": provider_calls_during_inventory,
        "inventory_eligible": inventory_eligible,
        "inventory_private_fields_absent": inventory_private_fields_absent,
        "durable_lifecycle_reservation_reloaded": (
            durable_lifecycle_reservation_reloaded
        ),
        "conflicting_lifecycle_action_blocked_after_restart": (
            conflicting_lifecycle_action_blocked_after_restart
        ),
        "provider_calls_during_lifecycle_reservation_restart": (
            provider_calls_during_lifecycle_reservation_restart
        ),
        "explicit_private_lease_retirement": retirement_json,
        "durable_private_lease_retirement": durable_retirement_json,
        "provider_calls_during_retirement": provider_calls_during_retirement,
        "retirement_matches_disposition": retirement_matches_disposition,
        "private_lease_absent_after_retirement": (
            private_lease_absent_after_retirement
        ),
        "durable_private_lease_absent": durable_private_lease_absent,
        "durable_retirement_reloaded": durable_retirement_reloaded,
        "disposition_preserved_after_retirement": (
            disposition_preserved_after_retirement
        ),
        "private_identifier_absent_from_active_database": (
            private_identifier_absent_from_active_database
        ),
        "retained_lease_inventory_after_retirement": (
            retained_inventory_after_retirement
        ),
        "provider_calls_during_post_retirement_inventory": (
            provider_calls_during_post_retirement_inventory
        ),
        "inventory_empty_after_retirement": inventory_empty_after_retirement,
        "errors": [_safe_error(error) for error in errors],
        "source": {
            "head_sha": source_after["head_sha"],
            "tree_sha": source_after["tree_sha"],
            "source_preserved": source_preserved,
        },
    }
    identifier_fields_absent = not _contains_private_identifier_field(summary)
    summary["private_identifier_fields_absent"] = identifier_fields_absent
    summary["qualified"] = bool(
        provider.background_cancellation
        and created_snapshot
        and created_snapshot.state is RemoteOperationState.ACTIVE
        and worker_terminated
        and recovered_snapshot
        and recovered_snapshot.state is RemoteOperationState.ACTIVE
        and automatic_provider_calls == 0
        and explicit_observe_calls >= 1
        and explicit_cancel_calls == 1
        and stable_reference
        and identity_and_base_bound
        and terminal_cancelled
        and durable_terminal_reloaded
        and provider_calls_during_disposition == 0
        and disposition_matches_remote
        and durable_disposition_reloaded
        and provider_calls_during_inventory == 0
        and inventory_eligible
        and inventory_private_fields_absent
        and durable_lifecycle_reservation_reloaded
        and conflicting_lifecycle_action_blocked_after_restart
        and provider_calls_during_lifecycle_reservation_restart == 0
        and provider_calls_during_retirement == 0
        and retirement_matches_disposition
        and private_lease_absent_after_retirement
        and durable_private_lease_absent
        and durable_retirement_reloaded
        and disposition_preserved_after_retirement
        and private_identifier_absent_from_active_database
        and provider_calls_during_post_retirement_inventory == 0
        and inventory_empty_after_retirement
        and not errors
        and identifier_fields_absent
        and source_preserved
    )
    _write_json(state_root / _SUMMARY_NAME, summary)
    return summary


def _worker_main(state_root: Path, base_sha: str, timeout_seconds: float) -> int:
    store = SqliteRemoteOperationLeaseStore(state_root / _PRIVATE_DATABASE_NAME)
    provider = OpenAIResponsesProvider.from_env(timeout_seconds=timeout_seconds)
    provider.bind_remote_operation_store(store.provider_store())
    signal = CancellationCoordinator().signal(_TASK_ID)
    try:
        provider.invoke_cancellable(
            ModelRequest(
                role="pretransfer_background_reconciliation",
                system_prompt=(
                    "Produce the requested long-form technical analysis. Do not use tools "
                    "or external data."
                ),
                user_prompt=(
                    "Write a detailed, multi-section analysis of deterministic software "
                    "verification strategies. Include many concrete examples and continue "
                    "until the available output budget is used."
                ),
                max_output_tokens=16_000,
                metadata={
                    "task_id": _TASK_ID,
                    "thread_id": _THREAD_ID,
                    "base_sha": base_sha,
                },
            ),
            signal,
        )
    except BaseException:
        return 2
    finally:
        store.close()
    return 0


def _start_worker(
    state_root: Path,
    base_sha: str,
    timeout_seconds: float,
) -> RestartWorker:
    return subprocess.Popen(
        [
            sys.executable,
            "-m",
            "universal_coding_agent.testlab.openai_background_reconciliation_live",
            "--worker",
            "--state-root",
            str(state_root),
            "--base-sha",
            base_sha,
            "--timeout-seconds",
            str(timeout_seconds),
        ],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


def _wait_for_active_lease(
    database_path: Path,
    worker: RestartWorker,
    *,
    timeout_seconds: float,
) -> RemoteOperationSnapshot | None:
    deadline = time.monotonic() + timeout_seconds
    store = SqliteRemoteOperationLeaseStore(database_path)
    try:
        while time.monotonic() < deadline:
            snapshot = store.public_snapshot(_TASK_ID)
            if snapshot is not None:
                if snapshot.state is RemoteOperationState.ACTIVE:
                    return snapshot
                return None
            if worker.poll() is not None:
                return None
            time.sleep(0.05)
    finally:
        store.close()
    return None


def _terminate_worker(worker: RestartWorker) -> tuple[bool, bool]:
    if worker.poll() is not None:
        return False, False
    killed = False
    worker.terminate()
    try:
        worker.wait(timeout=5.0)
    except subprocess.TimeoutExpired:
        killed = True
        worker.kill()
        worker.wait(timeout=2.0)
    return worker.poll() is not None, killed


def _snapshot_json(
    snapshot: RemoteOperationSnapshot | None,
) -> dict[str, Any] | None:
    return snapshot.model_dump(mode="json") if snapshot is not None else None


def _disposition_json(
    disposition: RemoteOperationDisposition | None,
) -> dict[str, Any] | None:
    return disposition.model_dump(mode="json") if disposition is not None else None


def _retirement_json(
    retirement: RemoteOperationLeaseRetirement | None,
) -> dict[str, Any] | None:
    return retirement.model_dump(mode="json") if retirement is not None else None


def _contains_private_identifier_field(value: Any) -> bool:
    if isinstance(value, dict):
        return any(
            key in {"operation_id", "response_id"}
            or _contains_private_identifier_field(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return any(_contains_private_identifier_field(item) for item in value)
    return False


def _contains_field(value: Any, names: set[str]) -> bool:
    if isinstance(value, dict):
        return any(
            key in names or _contains_field(item, names)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return any(_contains_field(item, names) for item in value)
    return False


def _safe_error(error: BaseException) -> dict[str, str]:
    result = {
        "type": type(error).__name__,
        "message": sanitize_text(str(error))[:2_000],
    }
    if isinstance(error, ModelProviderError):
        result["code"] = error.code
    return result


def _source_snapshot(source_root: Path) -> dict[str, str]:
    root = source_root.resolve()
    return {
        "head_sha": _git(root, "rev-parse", "HEAD"),
        "tree_sha": _git(root, "rev-parse", "HEAD^{tree}"),
        "status": _git(root, "status", "--porcelain"),
    }


def _git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state-root", type=Path, required=True)
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--base-sha", default="", help=argparse.SUPPRESS)
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=float(
            os.environ.get("UCA_OPENAI_BACKGROUND_CANCEL_TIMEOUT_SECONDS", "45")
        ),
    )
    parser.add_argument("--source-root", type=Path)
    args = parser.parse_args()
    if not 5.0 <= args.timeout_seconds <= 120.0:
        parser.error("--timeout-seconds must be between 5 and 120")
    if args.worker:
        if not 40 <= len(args.base_sha) <= 64:
            parser.error("--base-sha is required for the restart worker")
        return _worker_main(args.state_root, args.base_sha, args.timeout_seconds)

    provider = OpenAIResponsesProvider.from_env(timeout_seconds=args.timeout_seconds)
    source_root = args.source_root or Path(
        _git(Path.cwd(), "rev-parse", "--show-toplevel")
    )
    summary = run_openai_background_reconciliation_live(
        args.state_root,
        provider,
        source_root=source_root,
        timeout_seconds=args.timeout_seconds,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"OPENAI_BACKGROUND_RECONCILIATION_LIVE_SUMMARY={args.state_root / _SUMMARY_NAME}")
    if not summary["source"]["source_preserved"]:
        return 3
    if not summary["qualified"]:
        return 2
    print("OPENAI_BACKGROUND_RECONCILIATION_LIVE_QUALIFICATION_PASS")
    print("REMOTE_OPERATION_LEASE_RETIREMENT_LIVE_QUALIFICATION_PASS")
    print("RETAINED_LEASE_INVENTORY_LIVE_QUALIFICATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
