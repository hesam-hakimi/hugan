from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path
from threading import Thread
from typing import Any

from universal_coding_agent.core.cancellation import (
    CancellationRequested,
    OwnedOperationKind,
)
from universal_coding_agent.core.models import ModelRequest
from universal_coding_agent.product.remote_operations import (
    SqliteRemoteOperationLeaseStore,
)
from universal_coding_agent.product.task_control import TaskControlService
from universal_coding_agent.providers.base import ModelProviderError
from universal_coding_agent.safety.sanitizer import sanitize_text
from universal_coding_agent.testlab.openai_responses import (
    OpenAIBackgroundLifecycleRecorder,
    OpenAIResponsesProvider,
)

_TASK_ID = "pretransfer-openai-background-cancellation-task"
_SUMMARY_NAME = "background-cancellation-live-summary.json"


def run_openai_background_cancellation_live(
    state_root: Path,
    provider: OpenAIResponsesProvider,
    recorder: OpenAIBackgroundLifecycleRecorder,
    *,
    source_root: Path,
) -> dict[str, Any]:
    """Qualify one actual owned OpenAI background cancellation lifecycle."""

    state_root.mkdir(parents=True, exist_ok=True)
    source_before = _source_snapshot(source_root)
    errors: list[BaseException] = []
    report = None
    persisted_report = None
    worker: Thread | None = None
    control_path = state_root / "task-control.sqlite"
    control = TaskControlService(control_path)
    remote_operations = SqliteRemoteOperationLeaseStore(
        state_root / "private-remote-operations.sqlite"
    )
    provider.bind_remote_operation_store(remote_operations.provider_store())

    if provider.background_cancellation:
        signal = control.cancellation.signal(_TASK_ID)

        def invoke() -> None:
            try:
                with signal.operation(OwnedOperationKind.PROVIDER):
                    provider.invoke_cancellable(
                        ModelRequest(
                            role="pretransfer_background_cancellation",
                            system_prompt=(
                                "Produce the requested long-form technical analysis. Do not use "
                                "tools or external data."
                            ),
                            user_prompt=(
                                "Write a detailed multi-section analysis of deterministic software "
                                "testing strategies. Include many concrete examples and continue "
                                "until the available output budget is used."
                            ),
                            max_output_tokens=4_096,
                        ),
                        signal,
                    )
            except BaseException as exc:  # captured for qualification evidence
                errors.append(exc)

        worker = Thread(
            target=invoke,
            name="uca-openai-background-cancellation-live",
            daemon=True,
        )
        worker.start()
        recorder.wait_for_handle(min(5.0, provider.timeout_seconds))
        control.cancel_task(
            _TASK_ID,
            reason="live qualification requested owned OpenAI response cancellation",
        )
        report = control.cancellation_report(_TASK_ID)
        worker.join(timeout=provider.timeout_seconds + 1.0)

    remote_snapshot = remote_operations.public_snapshot(_TASK_ID)
    control.close()
    remote_operations.close()
    reopened = TaskControlService(control_path)
    try:
        persisted_report = reopened.cancellation_report(_TASK_ID)
    finally:
        reopened.close()

    lifecycle = recorder.snapshot()
    source_after = _source_snapshot(source_root)
    source_preserved = source_before == source_after and not source_before["status"]
    invocation_finished = worker is not None and not worker.is_alive()
    invocation_cancelled = (
        len(errors) == 1 and isinstance(errors[0], CancellationRequested)
    )
    report_json = report.to_json() if report is not None else None
    persisted_report_json = (
        persisted_report.to_json() if persisted_report is not None else None
    )
    durable_report_reloaded = report_json is not None and report_json == persisted_report_json
    report_qualified = bool(
        report
        and report.active_operation_kinds == (OwnedOperationKind.PROVIDER.value,)
        and report.owned_processes_observed == 0
        and report.owned_cancellable_operations_observed == 1
        and report.terminate_requests == 0
        and report.kill_requests == 0
        and report.cancellable_operation_cancel_requests == 1
        and report.processes_still_active == 0
        and report.cancellable_operations_still_active in {0, 1}
        and report.cooperative_fallback is False
    )
    remote_operation_json = (
        remote_snapshot.model_dump(mode="json")
        if remote_snapshot is not None
        else None
    )
    remote_operation_qualified = bool(
        remote_snapshot
        and remote_snapshot.state.value == "terminal"
        and remote_snapshot.last_status == "cancelled"
        and remote_snapshot.cancellation_requested
        and remote_snapshot.cancel_requests == 1
    )
    qualified = bool(
        provider.background_cancellation
        and lifecycle.handle_started
        and lifecycle.response_id_observed
        and lifecycle.initial_status in {"queued", "in_progress"}
        and lifecycle.cancel_dispatched
        and lifecycle.terminal_status == "cancelled"
        and lifecycle.terminal_confirmed
        and invocation_finished
        and invocation_cancelled
        and report_qualified
        and remote_operation_qualified
        and durable_report_reloaded
        and source_preserved
    )
    summary = {
        "provider": "openai_responses",
        "model": provider.model,
        "qualified": qualified,
        "background_cancellation_enabled": provider.background_cancellation,
        "lifecycle": lifecycle.to_json(),
        "invocation_finished": invocation_finished,
        "invocation_cancelled": invocation_cancelled,
        "invocation_errors": [_safe_error(error) for error in errors],
        "cancellation_report": report_json,
        "cancellation_report_qualified": report_qualified,
        "remote_operation": remote_operation_json,
        "remote_operation_qualified": remote_operation_qualified,
        "durable_report_reloaded": durable_report_reloaded,
        "source": {
            "head_sha": source_after["head_sha"],
            "tree_sha": source_after["tree_sha"],
            "source_preserved": source_preserved,
        },
    }
    _write_summary(state_root, summary)
    return summary


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


def _write_summary(state_root: Path, summary: dict[str, Any]) -> None:
    (state_root / _SUMMARY_NAME).write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state-root", type=Path, required=True)
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

    recorder = OpenAIBackgroundLifecycleRecorder()
    provider = OpenAIResponsesProvider.from_env(
        timeout_seconds=args.timeout_seconds,
        background_lifecycle_recorder=recorder,
    )
    source_root = args.source_root or Path(
        _git(Path.cwd(), "rev-parse", "--show-toplevel")
    )
    summary = run_openai_background_cancellation_live(
        args.state_root,
        provider,
        recorder,
        source_root=source_root,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"OPENAI_BACKGROUND_CANCELLATION_LIVE_SUMMARY={args.state_root / _SUMMARY_NAME}")
    if not summary["source"]["source_preserved"]:
        return 3
    if not summary["qualified"]:
        return 2
    print("OPENAI_BACKGROUND_CANCELLATION_LIVE_QUALIFICATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
