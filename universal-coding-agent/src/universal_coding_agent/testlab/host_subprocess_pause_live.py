from __future__ import annotations

import argparse
import json
import subprocess
import threading
import time
from pathlib import Path
from typing import Any

from universal_coding_agent.core.cancellation import OwnedOperationKind
from universal_coding_agent.core.models import ModelRequest
from universal_coding_agent.product.task_control import TaskControlService
from universal_coding_agent.providers.host_subprocess import HostSubprocessProvider
from universal_coding_agent.safety.sanitizer import sanitize_text

_TASK_ID = "pretransfer-host-subprocess-active-pause-task"
_SUMMARY_NAME = "host-subprocess-active-pause-live-summary.json"
_MINIMUM_STABLE_PAUSE_SECONDS = 1.5


def run_host_subprocess_pause_live(
    state_root: Path,
    provider: HostSubprocessProvider,
    *,
    source_root: Path,
    stable_pause_seconds: float = 1.5,
) -> dict[str, Any]:
    """Qualify one actual opt-in Host Subprocess pause/resume lifecycle."""

    if not _MINIMUM_STABLE_PAUSE_SECONDS <= stable_pause_seconds <= 5.0:
        raise ValueError("stable pause window must be between 1.5 and 5.0 seconds")
    state_root.mkdir(parents=True, exist_ok=True)
    source_before = _source_snapshot(source_root)
    control_path = state_root / "task-control.sqlite"
    control = TaskControlService(control_path)
    control.ensure_task(_TASK_ID)
    signal = control.cancellation.signal(_TASK_ID)
    responses: list[Any] = []
    errors: list[BaseException] = []

    def invoke() -> None:
        try:
            with signal.operation(OwnedOperationKind.PROVIDER):
                responses.append(
                    provider.invoke_cancellable(
                        ModelRequest(
                            role="pretransfer_host_subprocess_active_pause",
                            system_prompt=("Continue until the output budget is exhausted."),
                            user_prompt=(
                                "Write an extended numbered sequence with one short item per "
                                "line. Do not stop early."
                            ),
                            max_output_tokens=512,
                        ),
                        signal,
                    )
                )
        except BaseException as exc:  # captured for qualification evidence
            errors.append(exc)

    worker = threading.Thread(
        target=invoke,
        name="uca-host-subprocess-active-pause-live",
        daemon=True,
    )
    worker.start()
    _wait_for_owned_pausable(control, _TASK_ID, timeout_seconds=10)

    pause_started = time.monotonic()
    paused = control.pause_task(
        _TASK_ID,
        reason="live host-subprocess active-pause qualification",
    )
    pause_call_ms = (time.monotonic() - pause_started) * 1_000
    pause_report = control.pause_report(_TASK_ID)
    paused_before_window, done_before_window = _owned_pausable_state(
        control,
        _TASK_ID,
    )
    invocation_done_before_window = not worker.is_alive()
    time.sleep(stable_pause_seconds)
    paused_after_window, done_after_window = _owned_pausable_state(
        control,
        _TASK_ID,
    )
    invocation_done_after_window = not worker.is_alive()

    resume_started = time.monotonic()
    resumed = control.resume_task(_TASK_ID)
    resume_call_ms = (time.monotonic() - resume_started) * 1_000
    resume_report = control.pause_report(_TASK_ID)
    worker.join(timeout=30)
    if worker.is_alive():
        control.cancel_task(_TASK_ID, reason="live qualification timeout cleanup")
        worker.join(timeout=2)

    control.close()
    reopened = TaskControlService(control_path)
    try:
        persisted_report = reopened.pause_report(_TASK_ID)
    finally:
        reopened.close()
    source_after = _source_snapshot(source_root)
    source_preserved = source_before == source_after and not source_before["status"]
    resumed_to_completion = bool(
        resume_report
        and resume_report.active_resume_acknowledged
        and not worker.is_alive()
        and len(responses) == 1
        and not errors
    )
    qualified = bool(
        paused.state.value == "paused"
        and resumed.state.value == "running"
        and pause_report
        and pause_report.active_pause_acknowledged
        and pause_report.active_operation_kinds == ("provider",)
        and pause_report.owned_pausable_operations_observed == 1
        and pause_report.unsupported_active_operations_observed == 0
        and paused_before_window
        and paused_after_window
        and not done_before_window
        and not done_after_window
        and not invocation_done_before_window
        and not invocation_done_after_window
        and resume_report
        and resume_report.active_resume_acknowledged
        and persisted_report == resume_report
        and resumed_to_completion
        and source_preserved
    )
    summary = {
        "transport": "host_subprocess_pausable_bridge",
        "qualified": qualified,
        "pause_call_ms": round(pause_call_ms, 3),
        "resume_call_ms": round(resume_call_ms, 3),
        "stable_pause_window_ms": round(stable_pause_seconds * 1_000, 3),
        "paused_before_window": paused_before_window,
        "paused_after_window": paused_after_window,
        "done_before_window": done_before_window,
        "done_after_window": done_after_window,
        "invocation_done_before_window": invocation_done_before_window,
        "invocation_done_after_window": invocation_done_after_window,
        "invocation_finished": not worker.is_alive(),
        "invocation_succeeded": len(responses) == 1 and not errors,
        "resumed_to_completion": resumed_to_completion,
        "invocation_errors": [
            {
                "type": type(error).__name__,
                "message": sanitize_text(str(error))[:2_000],
            }
            for error in errors
        ],
        "pause_report": pause_report.to_json() if pause_report else None,
        "resume_report": resume_report.to_json() if resume_report else None,
        "durable_report_reloaded": persisted_report == resume_report,
        "source": {
            "head_sha": source_after["head_sha"],
            "tree_sha": source_after["tree_sha"],
            "source_preserved": source_preserved,
        },
    }
    summary = json.loads(json.dumps(summary, ensure_ascii=False))
    (state_root / _SUMMARY_NAME).write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return summary


def _wait_for_owned_pausable(
    control: TaskControlService,
    task_id: str,
    *,
    timeout_seconds: float,
) -> None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        states = _owned_pausable_states(control, task_id)
        if len(states) == 1 and states[0][1] is False:
            return
        time.sleep(0.01)
    raise TimeoutError("host-subprocess pausable handle was not observed")


def _owned_pausable_state(
    control: TaskControlService,
    task_id: str,
) -> tuple[bool, bool]:
    states = _owned_pausable_states(control, task_id)
    if len(states) != 1:
        return False, True
    return states[0]


def _owned_pausable_states(
    control: TaskControlService,
    task_id: str,
) -> list[tuple[bool, bool]]:
    """Observe exact coordinator-owned handles without inspecting provider output."""

    coordinator = control.cancellation
    with coordinator._lock:
        owned = tuple(coordinator._pausables.get(task_id, ()))
    states: list[tuple[bool, bool]] = []
    for item in owned:
        try:
            states.append((bool(item.operation.paused()), bool(item.operation.done())))
        except Exception:
            states.append((False, True))
    return states


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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state-root", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--host-client-path", type=Path, required=True)
    parser.add_argument("--host-python", type=Path, required=True)
    parser.add_argument("--pausable-factory", required=True)
    parser.add_argument("--stable-pause-seconds", type=float, default=1.5)
    args = parser.parse_args()
    if not _MINIMUM_STABLE_PAUSE_SECONDS <= args.stable_pause_seconds <= 5.0:
        parser.error("--stable-pause-seconds must be between 1.5 and 5.0")
    provider = HostSubprocessProvider(
        args.host_client_path,
        args.host_python,
        pausable_completion_factory_name=args.pausable_factory,
    )
    summary = run_host_subprocess_pause_live(
        args.state_root,
        provider,
        source_root=args.source_root,
        stable_pause_seconds=args.stable_pause_seconds,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    if not summary["qualified"]:
        raise SystemExit("HOST_SUBPROCESS_ACTIVE_PAUSE_LIVE_FAILED")
    print("HOST_SUBPROCESS_ACTIVE_PAUSE_LIVE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
