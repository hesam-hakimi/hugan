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
    RemoteOperationSnapshot,
    RemoteOperationState,
)
from universal_coding_agent.product.remote_operations import (
    SqliteRemoteOperationLeaseStore,
)
from universal_coding_agent.providers.base import ModelProviderError
from universal_coding_agent.safety.sanitizer import sanitize_text
from universal_coding_agent.testlab.openai_responses import OpenAIResponsesProvider

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
    provider.bind_remote_operation_store(reopened)
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

    source_after = _source_snapshot(source_root)
    source_preserved = source_before == source_after and not source_before["status"]
    created_json = _snapshot_json(created_snapshot)
    recovered_json = _snapshot_json(recovered_snapshot)
    observed_json = _snapshot_json(observed_snapshot)
    cancelled_json = _snapshot_json(cancelled_snapshot)
    terminal_json = _snapshot_json(terminal_snapshot)
    durable_json = _snapshot_json(durable_snapshot)
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
        and not errors
        and identifier_fields_absent
        and source_preserved
    )
    _write_json(state_root / _SUMMARY_NAME, summary)
    return summary


def _worker_main(state_root: Path, base_sha: str, timeout_seconds: float) -> int:
    store = SqliteRemoteOperationLeaseStore(state_root / _PRIVATE_DATABASE_NAME)
    provider = OpenAIResponsesProvider.from_env(timeout_seconds=timeout_seconds)
    provider.bind_remote_operation_store(store)
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
