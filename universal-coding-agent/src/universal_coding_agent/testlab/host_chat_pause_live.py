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
from universal_coding_agent.providers.host_chat import HostChatCompletionsProvider
from universal_coding_agent.safety.sanitizer import sanitize_text

_TASK_ID = "pretransfer-host-chat-active-pause-task"
_SUMMARY_NAME = "host-chat-active-pause-live-summary.json"


def run_host_chat_pause_live(
    state_root: Path,
    provider: HostChatCompletionsProvider,
    *,
    source_root: Path,
    stable_pause_seconds: float = 1.5,
) -> dict[str, Any]:
    """Qualify one actual opt-in Host Chat pause/resume lifecycle."""

    state_root.mkdir(parents=True, exist_ok=True)
    source_before = _source_snapshot(source_root)
    module = provider._host_module()
    factory_name = provider.pausable_completion_factory_name
    factory = getattr(module, factory_name or "", None)
    if not callable(factory):
        raise RuntimeError("configured host pausable completion factory is unavailable")

    handle_ready = threading.Event()
    observed: dict[str, Any] = {}

    def observed_factory(**kwargs: Any) -> Any:
        handle = factory(**kwargs)
        observed["handle"] = handle
        handle_ready.set()
        return handle

    setattr(module, factory_name, observed_factory)
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
                            role="pretransfer_host_chat_active_pause",
                            system_prompt="Continue until the output budget is exhausted.",
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
        name="uca-host-chat-active-pause-live",
        daemon=True,
    )
    worker.start()
    if not handle_ready.wait(timeout=10):
        raise TimeoutError("host pausable handle was not observed")

    pause_started = time.monotonic()
    paused = control.pause_task(_TASK_ID, reason="live active-pause qualification")
    pause_call_ms = (time.monotonic() - pause_started) * 1_000
    pause_report = control.pause_report(_TASK_ID)
    handle = observed["handle"]
    paused_before_window = bool(handle.paused())
    time.sleep(stable_pause_seconds)
    paused_after_window = bool(handle.paused())

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
    qualified = bool(
        paused.state.value == "paused"
        and resumed.state.value == "running"
        and pause_report
        and pause_report.active_pause_acknowledged
        and pause_report.owned_pausable_operations_observed == 1
        and pause_report.unsupported_active_operations_observed == 0
        and paused_before_window
        and paused_after_window
        and resume_report
        and resume_report.active_resume_acknowledged
        and persisted_report == resume_report
        and not worker.is_alive()
        and len(responses) == 1
        and not errors
        and source_preserved
    )
    summary = {
        "provider": "host_chat_completions",
        "qualified": qualified,
        "pause_call_ms": round(pause_call_ms, 3),
        "resume_call_ms": round(resume_call_ms, 3),
        "stable_pause_window_ms": round(stable_pause_seconds * 1_000, 3),
        "paused_before_window": paused_before_window,
        "paused_after_window": paused_after_window,
        "invocation_finished": not worker.is_alive(),
        "invocation_succeeded": len(responses) == 1 and not errors,
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
    (state_root / _SUMMARY_NAME).write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return summary


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
    parser.add_argument("--pausable-factory", required=True)
    parser.add_argument("--stable-pause-seconds", type=float, default=1.5)
    args = parser.parse_args()
    if not 0.5 <= args.stable_pause_seconds <= 5.0:
        parser.error("--stable-pause-seconds must be between 0.5 and 5.0")
    provider = HostChatCompletionsProvider(
        args.host_client_path,
        pausable_completion_factory_name=args.pausable_factory,
    )
    summary = run_host_chat_pause_live(
        args.state_root,
        provider,
        source_root=args.source_root,
        stable_pause_seconds=args.stable_pause_seconds,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    if not summary["qualified"]:
        raise SystemExit("HOST_CHAT_ACTIVE_PAUSE_LIVE_FAILED")
    print("HOST_CHAT_ACTIVE_PAUSE_LIVE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
