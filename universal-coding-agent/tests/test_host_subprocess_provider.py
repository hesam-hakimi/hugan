# ruff: noqa: I001

from __future__ import annotations

import os
import sys
import threading
import time
from pathlib import Path

import pytest
from pydantic import BaseModel

from universal_coding_agent.core.cancellation import (
    CancellationCoordinator,
    OwnedOperationKind,
)
from universal_coding_agent.core.models import ModelRequest
from universal_coding_agent.orchestration.structured_output import (
    StructuredOutputError,
    invoke_structured,
)
from universal_coding_agent.product.models import ControlState
from universal_coding_agent.product.task_control import TaskControlService
from universal_coding_agent.providers.base import ModelProviderError
from universal_coding_agent.providers.host_subprocess import (
    HOST_CLIENT_PATH_ENV,
    HOST_PYTHON_ENV,
    PAUSABLE_COMPLETION_FACTORY_ENV,
    HostSubprocessProvider,
    create_provider,
)


HOST_MODULE = """
from types import SimpleNamespace


class _Completions:
    def create(self, **kwargs):
        content = '{"status":"OK"}'
        return SimpleNamespace(
            model="actual-host-model",
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content=content),
                    finish_reason="stop",
                )
            ],
            usage=SimpleNamespace(
                completion_tokens=44,
                completion_tokens_details=SimpleNamespace(reasoning_tokens=7),
            ),
        )


class _Client:
    def __init__(self):
        self.chat = SimpleNamespace(completions=_Completions())


def create_client():
    return _Client()


def get_configured_model_or_deployment():
    return SimpleNamespace(deployment="host-deployment")
"""

HOST_INVOKE_MODULE = """
def invoke_text(prompt, max_output_tokens=8):
    assert max_output_tokens <= 64
    return "UCA_HOST_PROVIDER_OK"


def create_client():
    raise AttributeError("direct client must not be used by probe")
"""

DATACLASS_HOST_INVOKE_MODULE = """
from dataclasses import dataclass


@dataclass(frozen=True)
class HostConfig:
    name: str = "host"


def invoke_text(prompt, max_output_tokens=8):
    assert HostConfig().name == "host"
    return "UCA_HOST_PROVIDER_OK"
"""

BROKEN_INVOKE_MODULE = """
def invoke_text(prompt, max_output_tokens=8):
    raise AttributeError("private internal detail")
"""


PAUSABLE_HOST_MODULE = (
    HOST_MODULE
    + r"""
import os
import threading
import time

print("PRIVATE_SITE_STDOUT_MUST_NOT_BE_CONTROL_TRAFFIC")


class _PausableHandle:
    def __init__(self, client, kwargs):
        self._client = client
        self._kwargs = kwargs
        self._pause_requested = threading.Event()
        self._pause_acknowledged = threading.Event()
        self._cancel_requested = threading.Event()
        self._done = threading.Event()
        self._result = None
        self._error = None
        self._worker = threading.Thread(target=self._run, daemon=True)
        self._worker.start()

    def _run(self):
        progress = os.environ.get("UCA_SUBPROCESS_PROGRESS", "")
        try:
            for _ in range(300):
                while self._pause_requested.is_set() and not self._cancel_requested.is_set():
                    self._pause_acknowledged.set()
                    time.sleep(0.002)
                self._pause_acknowledged.clear()
                if self._cancel_requested.is_set():
                    return
                if progress:
                    with open(progress, "a", encoding="utf-8") as stream:
                        stream.write("x")
                time.sleep(0.002)
            self._result = self._client.chat.completions.create(**self._kwargs)
        except BaseException as exc:
            self._error = exc
        finally:
            self._pause_acknowledged.clear()
            self._done.set()

    def result(self):
        self._done.wait(timeout=10)
        if self._error is not None:
            raise self._error
        if self._cancel_requested.is_set():
            raise RuntimeError("cancelled")
        if self._result is None:
            raise RuntimeError("missing result")
        return self._result

    def pause(self):
        self._pause_requested.set()

    def resume(self):
        self._pause_requested.clear()

    def paused(self):
        return self._pause_acknowledged.is_set()

    def cancel(self):
        self._cancel_requested.set()
        self._pause_requested.clear()

    def done(self):
        return self._done.is_set()


def create_pausable_completion(client, **kwargs):
    return _PausableHandle(client, kwargs)
"""
)


SLOW_UNCONTROLLED_HOST_MODULE = HOST_MODULE.replace(
    'content = \'{"status":"OK"}\'',
    """
        import os
        import time
        from pathlib import Path
        Path(os.environ["UCA_SUBPROCESS_STARTED"]).write_text("started")
        time.sleep(0.5)
        content = '{"status":"OK"}'
        """,
)

UNACKNOWLEDGED_PAUSE_HOST_MODULE = PAUSABLE_HOST_MODULE.replace(
    "    def paused(self):\n        return self._pause_acknowledged.is_set()",
    "    def paused(self):\n        return False",
)

UNACKNOWLEDGED_RESUME_HOST_MODULE = PAUSABLE_HOST_MODULE.replace(
    "    def resume(self):\n        self._pause_requested.clear()",
    "    def resume(self):\n        return None",
)

INVALID_PAUSABLE_HANDLE_MODULE = (
    HOST_MODULE
    + """
def create_pausable_completion(client, **kwargs):
    return object()
"""
)

FAILING_PAUSABLE_FACTORY_MODULE = (
    HOST_MODULE
    + """
def create_pausable_completion(client, **kwargs):
    raise RuntimeError("PRIVATE_FACTORY_SECRET")
"""
)

DELAYED_PAUSABLE_FACTORY_MODULE = PAUSABLE_HOST_MODULE.replace(
    "def create_pausable_completion(client, **kwargs):\n    return _PausableHandle(client, kwargs)",
    "def create_pausable_completion(client, **kwargs):\n"
    "    with open(os.environ['UCA_FACTORY_STARTED'], 'w', encoding='utf-8') as stream:\n"
    "        stream.write('started')\n"
    "    time.sleep(0.15)\n"
    "    return _PausableHandle(client, kwargs)",
)

COUNTED_CANCEL_HOST_MODULE = PAUSABLE_HOST_MODULE.replace(
    '        if self._cancel_requested.is_set():\n            raise RuntimeError("cancelled")',
    "        if self._cancel_requested.is_set():\n"
    "            time.sleep(0.1)\n"
    '            raise RuntimeError("cancelled")',
).replace(
    "    def cancel(self):\n"
    "        self._cancel_requested.set()\n"
    "        self._pause_requested.clear()",
    "    def cancel(self):\n"
    "        with open(os.environ['UCA_CANCEL_COUNT'], 'a', encoding='utf-8') as stream:\n"
    "            stream.write('x')\n"
    "        self._cancel_requested.set()\n"
    "        self._pause_requested.clear()",
)

OVERSIZED_RESULT_HOST_MODULE = PAUSABLE_HOST_MODULE.replace(
    "for _ in range(300):",
    "for _ in range(1):",
).replace(
    'content = \'{"status":"OK"}\'',
    'content = "x" * 1_100_000',
)

DESCENDANT_PAUSABLE_HOST_MODULE = (
    HOST_MODULE
    + r"""
import os
import subprocess
import sys
import threading
import time
from pathlib import Path


class _DescendantHandle:
    def __init__(self, client, kwargs):
        self._client = client
        self._kwargs = kwargs
        self._pause_requested = threading.Event()
        self._pause_acknowledged = threading.Event()
        self._cancel_requested = threading.Event()
        self._done = threading.Event()
        self._descendant = subprocess.Popen(
            [sys.executable, os.environ["UCA_DESCENDANT_SCRIPT"]]
        )
        self._worker = threading.Thread(target=self._run, daemon=True)
        self._worker.start()

    def _run(self):
        progress = Path(os.environ["UCA_SUBPROCESS_PROGRESS"])
        for _ in range(1000):
            while self._pause_requested.is_set() and not self._cancel_requested.is_set():
                self._pause_acknowledged.set()
                time.sleep(0.002)
            self._pause_acknowledged.clear()
            if self._cancel_requested.is_set():
                return
            with progress.open("a", encoding="utf-8") as stream:
                stream.write("x")
            time.sleep(0.002)
        self._done.set()

    def result(self):
        self._done.wait(timeout=10)
        if self._cancel_requested.is_set():
            raise RuntimeError("PRIVATE_CANCEL_DETAIL")
        return self._client.chat.completions.create(**self._kwargs)

    def pause(self):
        self._pause_requested.set()

    def resume(self):
        self._pause_requested.clear()

    def paused(self):
        return self._pause_acknowledged.is_set()

    def cancel(self):
        self._cancel_requested.set()
        self._pause_requested.clear()
        self._done.set()

    def done(self):
        return self._done.is_set()


def create_pausable_completion(client, **kwargs):
    return _DescendantHandle(client, kwargs)
"""
)


def _host_module(tmp_path, content=HOST_MODULE):
    path = tmp_path / "host_client.py"
    path.write_text(content, encoding="utf-8")
    return path


def _fake_protocol_python(
    tmp_path: Path,
    *,
    send_ready: bool,
    linger_seconds: float = 0.0,
) -> Path:
    path = tmp_path / "fake-host-python"
    path.write_text(
        f"""#!/usr/bin/env python3
import json
import os
import socket
import time
from pathlib import Path

control = socket.socket(fileno=int(os.environ["UCA_HOST_SUBPROCESS_CONTROL_FD"]))
stream = control.makefile("rb", buffering=0)
json.loads(stream.readline())
sequence = 1


def emit(kind, **fields):
    global sequence
    frame = {{
        "protocol": "uca-host-subprocess-pause/1",
        "sequence": sequence,
        "kind": kind,
        **fields,
    }}
    sequence += 1
    control.sendall(json.dumps(frame, separators=(",", ":")).encode() + b"\\n")


if {send_ready!r}:
    emit("ready")
emit(
    "result",
    payload={{
        "ok": True,
        "content": '{{"status":"OK"}}',
        "safe_diagnostics": {{}},
    }},
)
emit("terminal", state="completed")
terminal_marker = os.environ.get("UCA_FAKE_TERMINAL_MARKER", "")
if terminal_marker:
    Path(terminal_marker).write_text("terminal", encoding="utf-8")
time.sleep({linger_seconds!r})
exit_marker = os.environ.get("UCA_FAKE_EXIT_MARKER", "")
if exit_marker:
    Path(exit_marker).write_text("exiting", encoding="utf-8")
""",
        encoding="utf-8",
    )
    path.chmod(0o700)
    return path


def _wait_until(predicate, *, timeout_seconds: float = 5.0) -> None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.005)
    raise AssertionError("condition was not reached before the bounded deadline")


def _progress_size(path: Path) -> int:
    try:
        return path.stat().st_size
    except FileNotFoundError:
        return 0


def _wait_until_file_stable(
    path: Path,
    *,
    stable_seconds: float = 0.1,
    timeout_seconds: float = 3.0,
) -> int:
    deadline = time.monotonic() + timeout_seconds
    stable_since = time.monotonic()
    previous = _progress_size(path)
    while time.monotonic() < deadline:
        time.sleep(0.01)
        current = _progress_size(path)
        if current != previous:
            previous = current
            stable_since = time.monotonic()
        elif time.monotonic() - stable_since >= stable_seconds:
            return current
    raise AssertionError("file progress did not stop before the bounded deadline")


class _StatusPayload(BaseModel):
    status: str


def _model_request() -> ModelRequest:
    return ModelRequest(
        role="qualification",
        system_prompt="Return JSON.",
        user_prompt="Return status OK.",
        response_schema={"type": "object"},
        max_output_tokens=512,
    )


def _start_structured_invoke(
    provider: HostSubprocessProvider,
    signal,
) -> tuple[
    threading.Thread,
    list[_StatusPayload],
    list[BaseException],
]:
    responses: list[_StatusPayload] = []
    errors: list[BaseException] = []

    def invoke() -> None:
        try:
            response = invoke_structured(
                provider,
                _model_request(),
                _StatusPayload,
                cancellation=signal,
                max_repair_attempts=0,
            )
            responses.append(response.value)
        except BaseException as exc:  # captured for assertion in the parent thread
            errors.append(exc)

    worker = threading.Thread(target=invoke)
    worker.start()
    return worker, responses, errors


def test_subprocess_provider_probe_and_structured_invoke(tmp_path) -> None:
    provider = HostSubprocessProvider(
        host_module_path=_host_module(tmp_path),
        host_python=sys.executable,
    )
    details = provider.probe_details()
    assert details["ok"] is True
    assert provider.probe() is True

    response = provider.invoke(
        ModelRequest(
            role="qualification",
            system_prompt="Return JSON.",
            user_prompt="Return status OK.",
            response_schema={"type": "object"},
            max_output_tokens=512,
        )
    )
    assert response.structured == {"status": "OK"}
    assert response.actual_model == "actual-host-model"
    assert response.finish_reason == "stop"
    assert response.completion_tokens == 44
    assert response.reasoning_tokens == 7
    assert response.safe_diagnostics["requested_deployment"] == "host-deployment"


def test_probe_prefers_existing_host_invoke_contract(tmp_path) -> None:
    provider = HostSubprocessProvider(
        host_module_path=_host_module(tmp_path, HOST_INVOKE_MODULE),
        host_python=sys.executable,
    )
    details = provider.probe_details()
    assert details["ok"] is True
    assert details["content"] == "UCA_HOST_PROVIDER_OK"
    assert details["safe_diagnostics"]["transport"] == "host_invoke_function"


def test_probe_loads_dataclass_host_module(tmp_path) -> None:
    provider = HostSubprocessProvider(
        host_module_path=_host_module(tmp_path, DATACLASS_HOST_INVOKE_MODULE),
        host_python=sys.executable,
    )
    details = provider.probe_details()
    assert details["ok"] is True
    assert details["content"] == "UCA_HOST_PROVIDER_OK"


def test_probe_reports_safe_host_invoke_stage(tmp_path) -> None:
    provider = HostSubprocessProvider(
        host_module_path=_host_module(tmp_path, BROKEN_INVOKE_MODULE),
        host_python=sys.executable,
    )
    details = provider.probe_details()
    assert details["ok"] is False
    assert details["error_code"] == "host_invoke_function_failed"
    assert details["error_type"] == "AttributeError"
    assert details["error_stage"] == "invoke_host_function"
    assert "private internal detail" not in str(details)


def test_subprocess_provider_returns_safe_load_error(tmp_path) -> None:
    broken = tmp_path / "broken_client.py"
    broken.write_text("raise RuntimeError('private internal detail')\n", encoding="utf-8")
    provider = HostSubprocessProvider(
        host_module_path=broken,
        host_python=sys.executable,
    )
    details = provider.probe_details()
    assert details["ok"] is False
    assert details["error_code"] == "host_client_load_failed"
    assert details["error_type"] == "RuntimeError"
    assert details["error_stage"] == "load_host_module"
    assert "private internal detail" not in str(details)


def test_unconfigured_subprocess_pause_remains_safe_boundary_only(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    started = tmp_path / "uncontrolled-started"
    monkeypatch.setenv("UCA_SUBPROCESS_STARTED", str(started))
    provider = HostSubprocessProvider(
        host_module_path=_host_module(tmp_path, SLOW_UNCONTROLLED_HOST_MODULE),
        host_python=sys.executable,
    )
    control = TaskControlService(tmp_path / "uncontrolled-pause.sqlite")
    task_id = "unconfigured-host-subprocess-pause"
    control.ensure_task(task_id)
    worker, responses, errors = _start_structured_invoke(
        provider,
        control.cancellation.signal(task_id),
    )
    _wait_until(started.exists)

    pause_record = control.pause_task(task_id, reason="safe-boundary fallback")
    report = control.pause_report(task_id)

    assert pause_record.state is ControlState.PAUSE_REQUESTED
    assert report is not None
    assert report.active_operation_kinds == ("provider",)
    assert report.owned_pausable_operations_observed == 0
    assert report.unsupported_active_operations_observed == 1
    assert report.pause_requests == 0
    assert report.pause_acknowledgements == 0
    assert report.cooperative_fallback is True
    assert report.active_pause_acknowledged is False

    assert control.resume_task(task_id).state is ControlState.RUNNING
    worker.join(timeout=5)
    assert worker.is_alive() is False
    assert errors == []
    assert [response.status for response in responses] == ["OK"]
    control.close()


def test_opt_in_subprocess_handle_pauses_progress_and_resumes_exactly_once(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    progress = tmp_path / "pausable-progress"
    monkeypatch.setenv("UCA_SUBPROCESS_PROGRESS", str(progress))
    provider = HostSubprocessProvider(
        host_module_path=_host_module(tmp_path, PAUSABLE_HOST_MODULE),
        host_python=sys.executable,
        pausable_completion_factory_name="create_pausable_completion",
    )
    database = tmp_path / "pausable-subprocess.sqlite"
    coordinator = CancellationCoordinator(
        pause_ack_timeout_seconds=1.0,
        control_poll_interval_seconds=0.005,
    )
    control = TaskControlService(database, cancellation=coordinator)
    task_id = "pausable-host-subprocess"
    control.ensure_task(task_id)
    worker, responses, errors = _start_structured_invoke(
        provider,
        control.cancellation.signal(task_id),
    )
    _wait_until(lambda: _progress_size(progress) >= 8)

    pause_record = control.pause_task(task_id, reason="active subprocess pause")
    pause_report = control.pause_report(task_id)
    paused_progress = _progress_size(progress)
    time.sleep(0.075)

    assert pause_record.state is ControlState.PAUSED
    assert paused_progress >= 8
    assert _progress_size(progress) == paused_progress
    assert pause_report is not None
    assert pause_report.active_operation_kinds == ("provider",)
    assert pause_report.owned_pausable_operations_observed == 1
    assert pause_report.unsupported_active_operations_observed == 0
    assert pause_report.pause_requests == 1
    assert pause_report.pause_acknowledgements == 1
    assert pause_report.pausable_operations_still_unpaused == 0
    assert pause_report.cooperative_fallback is False
    assert pause_report.active_pause_acknowledged is True

    assert control.resume_task(task_id).state is ControlState.RUNNING
    resume_report = control.pause_report(task_id)
    _wait_until(lambda: _progress_size(progress) > paused_progress)
    worker.join(timeout=5)

    assert resume_report is not None
    assert resume_report.resume_requests == 1
    assert resume_report.resume_acknowledgements == 1
    assert resume_report.pausable_operations_still_paused == 0
    assert resume_report.pausable_operations_missing_on_resume == 0
    assert resume_report.active_resume_acknowledged is True
    assert worker.is_alive() is False
    assert errors == []
    assert [response.status for response in responses] == ["OK"]
    control.close()

    reopened = TaskControlService(database)
    assert reopened.pause_report(task_id) == resume_report
    reopened.close()


def test_subprocess_pause_requested_before_child_ready_is_latched(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    factory_started = tmp_path / "factory-started"
    progress = tmp_path / "pause-before-ready-progress"
    monkeypatch.setenv("UCA_FACTORY_STARTED", str(factory_started))
    monkeypatch.setenv("UCA_SUBPROCESS_PROGRESS", str(progress))
    provider = HostSubprocessProvider(
        host_module_path=_host_module(tmp_path, DELAYED_PAUSABLE_FACTORY_MODULE),
        host_python=sys.executable,
        pausable_completion_factory_name="create_pausable_completion",
    )
    control = TaskControlService(tmp_path / "pause-before-ready.sqlite")
    task_id = "pause-before-subprocess-ready"
    control.ensure_task(task_id)
    worker, responses, errors = _start_structured_invoke(
        provider,
        control.cancellation.signal(task_id),
    )
    _wait_until(factory_started.exists)

    pause_record = control.pause_task(task_id, reason="pause before child ready")
    report = control.pause_report(task_id)

    assert pause_record.state is ControlState.PAUSED
    assert report is not None
    assert report.owned_pausable_operations_observed == 1
    assert report.pause_acknowledgements == 1
    assert report.active_pause_acknowledged is True
    assert control.resume_task(task_id).state is ControlState.RUNNING
    worker.join(timeout=5)
    assert worker.is_alive() is False
    assert errors == []
    assert [response.status for response in responses] == ["OK"]
    control.close()


def test_create_provider_uses_explicit_subprocess_pausable_factory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = _host_module(tmp_path, PAUSABLE_HOST_MODULE)
    monkeypatch.setenv(HOST_CLIENT_PATH_ENV, str(path))
    monkeypatch.setenv(HOST_PYTHON_ENV, sys.executable)
    monkeypatch.setenv(
        PAUSABLE_COMPLETION_FACTORY_ENV,
        "create_pausable_completion",
    )

    provider = create_provider()

    assert provider.host_module_path == path.resolve()
    assert provider.host_python == Path(sys.executable).resolve()
    assert provider.pausable_completion_factory_name == "create_pausable_completion"


def test_create_provider_maps_blank_subprocess_pausable_factory_to_none(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = _host_module(tmp_path)
    monkeypatch.setenv(HOST_CLIENT_PATH_ENV, str(path))
    monkeypatch.setenv(HOST_PYTHON_ENV, sys.executable)
    monkeypatch.setenv(PAUSABLE_COMPLETION_FACTORY_ENV, "   ")

    provider = create_provider()

    assert provider.pausable_completion_factory_name is None


@pytest.mark.parametrize(
    ("module_source", "expected_code"),
    [
        (HOST_MODULE, "host_pausable_factory_missing"),
        (INVALID_PAUSABLE_HANDLE_MODULE, "host_pausable_handle_invalid"),
    ],
)
def test_opt_in_subprocess_control_contract_failures_are_fail_closed(
    tmp_path: Path,
    module_source: str,
    expected_code: str,
) -> None:
    provider = HostSubprocessProvider(
        host_module_path=_host_module(tmp_path, module_source),
        host_python=sys.executable,
        pausable_completion_factory_name="create_pausable_completion",
    )
    signal = CancellationCoordinator().signal("invalid-pausable-subprocess")

    with signal.operation(OwnedOperationKind.PROVIDER):
        with pytest.raises(ModelProviderError) as exc_info:
            provider.invoke_cancellable(_model_request(), signal)

    assert exc_info.value.code == expected_code
    assert "host_client.py" not in str(exc_info.value)


def test_subprocess_pausable_factory_error_is_redacted(tmp_path: Path) -> None:
    provider = HostSubprocessProvider(
        host_module_path=_host_module(tmp_path, FAILING_PAUSABLE_FACTORY_MODULE),
        host_python=sys.executable,
        pausable_completion_factory_name="create_pausable_completion",
    )
    signal = CancellationCoordinator().signal("failing-pausable-factory")

    with signal.operation(OwnedOperationKind.PROVIDER):
        with pytest.raises(ModelProviderError) as exc_info:
            provider.invoke_cancellable(_model_request(), signal)

    assert "PRIVATE_FACTORY_SECRET" not in str(exc_info.value)
    assert "PRIVATE_FACTORY_SECRET" not in repr(exc_info.value)


def test_subprocess_pause_protocol_mismatch_fails_closed_and_redacted(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = HostSubprocessProvider(
        host_module_path=_host_module(tmp_path, PAUSABLE_HOST_MODULE),
        host_python=sys.executable,
        pausable_completion_factory_name="create_pausable_completion",
    )
    monkeypatch.setattr(
        "universal_coding_agent.providers.host_subprocess._CONTROL_PROTOCOL",
        "malformed-private-protocol",
    )
    signal = CancellationCoordinator().signal("malformed-subprocess-protocol")

    with signal.operation(OwnedOperationKind.PROVIDER):
        with pytest.raises(ModelProviderError) as exc_info:
            provider.invoke_cancellable(_model_request(), signal)

    assert exc_info.value.code == "host_subprocess_pause_protocol_invalid"
    assert "malformed-private-protocol" not in str(exc_info.value)


def test_subprocess_result_before_ready_fails_closed(tmp_path: Path) -> None:
    provider = HostSubprocessProvider(
        host_module_path=_host_module(tmp_path),
        host_python=_fake_protocol_python(tmp_path, send_ready=False),
        pausable_completion_factory_name="create_pausable_completion",
    )
    signal = CancellationCoordinator().signal("result-before-ready")

    with signal.operation(OwnedOperationKind.PROVIDER):
        with pytest.raises(ModelProviderError) as exc_info:
            provider.invoke_cancellable(_model_request(), signal)

    assert exc_info.value.code == "host_subprocess_pause_protocol_invalid"


def test_subprocess_terminal_waits_for_actual_child_exit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    terminal_marker = tmp_path / "terminal-sent"
    exit_marker = tmp_path / "child-exiting"
    monkeypatch.setenv("UCA_FAKE_TERMINAL_MARKER", str(terminal_marker))
    monkeypatch.setenv("UCA_FAKE_EXIT_MARKER", str(exit_marker))
    provider = HostSubprocessProvider(
        host_module_path=_host_module(tmp_path),
        host_python=_fake_protocol_python(
            tmp_path,
            send_ready=True,
            linger_seconds=0.4,
        ),
        pausable_completion_factory_name="create_pausable_completion",
    )
    signal = CancellationCoordinator().signal("terminal-before-child-exit")

    started = time.monotonic()
    with signal.operation(OwnedOperationKind.PROVIDER):
        response = provider.invoke_cancellable(_model_request(), signal)
    elapsed = time.monotonic() - started

    assert terminal_marker.is_file()
    assert exit_marker.is_file()
    assert elapsed >= 0.35
    assert response.structured == {"status": "OK"}


def test_oversized_subprocess_control_request_fails_before_child_start(
    tmp_path: Path,
) -> None:
    provider = HostSubprocessProvider(
        host_module_path=_host_module(tmp_path, PAUSABLE_HOST_MODULE),
        host_python=sys.executable,
        pausable_completion_factory_name="create_pausable_completion",
    )
    signal = CancellationCoordinator().signal("oversized-subprocess-control-frame")
    request = _model_request().model_copy(
        update={"user_prompt": "PRIVATE_OVERSIZED_PROMPT" * 60_000}
    )

    with signal.operation(OwnedOperationKind.PROVIDER):
        with pytest.raises(ModelProviderError) as exc_info:
            provider.invoke_cancellable(request, signal)

    assert exc_info.value.code == "host_subprocess_pause_frame_too_large"
    assert "PRIVATE_OVERSIZED_PROMPT" not in str(exc_info.value)


def test_oversized_subprocess_result_preserves_safe_error_sequence(
    tmp_path: Path,
) -> None:
    provider = HostSubprocessProvider(
        host_module_path=_host_module(tmp_path, OVERSIZED_RESULT_HOST_MODULE),
        host_python=sys.executable,
        pausable_completion_factory_name="create_pausable_completion",
    )
    signal = CancellationCoordinator().signal("oversized-subprocess-result")

    with signal.operation(OwnedOperationKind.PROVIDER):
        with pytest.raises(ModelProviderError) as exc_info:
            provider.invoke_cancellable(_model_request(), signal)

    assert exc_info.value.code == "host_subprocess_pause_frame_too_large"
    assert "x" * 1_000 not in str(exc_info.value)


def test_unacknowledged_subprocess_pause_times_out_fail_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    progress = tmp_path / "unacknowledged-pause-progress"
    monkeypatch.setenv("UCA_SUBPROCESS_PROGRESS", str(progress))
    provider = HostSubprocessProvider(
        host_module_path=_host_module(tmp_path, UNACKNOWLEDGED_PAUSE_HOST_MODULE),
        host_python=sys.executable,
        pausable_completion_factory_name="create_pausable_completion",
    )
    coordinator = CancellationCoordinator(
        pause_ack_timeout_seconds=0.05,
        control_poll_interval_seconds=0.002,
    )
    control = TaskControlService(
        tmp_path / "unacknowledged-subprocess-pause.sqlite",
        cancellation=coordinator,
    )
    task_id = "unacknowledged-host-subprocess-pause"
    control.ensure_task(task_id)
    worker, _, errors = _start_structured_invoke(
        provider,
        control.cancellation.signal(task_id),
    )
    _wait_until(lambda: _progress_size(progress) >= 5)

    pause_record = control.pause_task(task_id, reason="pause acknowledgement timeout")
    report = control.pause_report(task_id)

    assert pause_record.state is ControlState.PAUSE_REQUESTED
    assert report is not None
    assert report.owned_pausable_operations_observed == 1
    assert report.unsupported_active_operations_observed == 0
    assert report.pause_requests == 1
    assert report.pause_acknowledgements == 0
    assert report.pausable_operations_still_unpaused == 1
    assert report.cooperative_fallback is True
    assert report.active_pause_acknowledged is False

    control.cancel_task(task_id, reason="cancel timed-out pause")
    worker.join(timeout=5)
    assert worker.is_alive() is False
    assert len(errors) == 1
    assert isinstance(errors[0], StructuredOutputError)
    assert errors[0].code == "control_cancelled"
    control.close()


def test_unacknowledged_subprocess_resume_stays_paused_fail_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    progress = tmp_path / "unacknowledged-resume-progress"
    monkeypatch.setenv("UCA_SUBPROCESS_PROGRESS", str(progress))
    provider = HostSubprocessProvider(
        host_module_path=_host_module(tmp_path, UNACKNOWLEDGED_RESUME_HOST_MODULE),
        host_python=sys.executable,
        pausable_completion_factory_name="create_pausable_completion",
    )
    coordinator = CancellationCoordinator(
        pause_ack_timeout_seconds=0.05,
        control_poll_interval_seconds=0.002,
    )
    control = TaskControlService(
        tmp_path / "unacknowledged-subprocess-resume.sqlite",
        cancellation=coordinator,
    )
    task_id = "unacknowledged-host-subprocess-resume"
    control.ensure_task(task_id)
    worker, _, errors = _start_structured_invoke(
        provider,
        control.cancellation.signal(task_id),
    )
    _wait_until(lambda: _progress_size(progress) >= 5)
    assert control.pause_task(task_id).state is ControlState.PAUSED
    paused_progress = _progress_size(progress)

    with pytest.raises(
        ValueError,
        match="active pause resume was not acknowledged",
    ):
        control.resume_task(task_id)

    report = control.pause_report(task_id)
    time.sleep(0.05)
    assert control.get_task(task_id).state is ControlState.PAUSED  # type: ignore[union-attr]
    assert _progress_size(progress) == paused_progress
    assert report is not None
    assert report.resume_requests == 1
    assert report.resume_acknowledgements == 0
    assert report.pausable_operations_still_paused == 1
    assert report.active_resume_acknowledged is False

    control.cancel_task(task_id, reason="cancel stalled resume")
    worker.join(timeout=5)
    assert worker.is_alive() is False
    assert len(errors) == 1
    assert isinstance(errors[0], StructuredOutputError)
    assert errors[0].code == "control_cancelled"
    control.close()


def test_subprocess_cancel_is_forwarded_to_child_handle_exactly_once(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    progress = tmp_path / "single-cancel-progress"
    cancel_count = tmp_path / "cancel-count"
    monkeypatch.setenv("UCA_SUBPROCESS_PROGRESS", str(progress))
    monkeypatch.setenv("UCA_CANCEL_COUNT", str(cancel_count))
    provider = HostSubprocessProvider(
        host_module_path=_host_module(tmp_path, COUNTED_CANCEL_HOST_MODULE),
        host_python=sys.executable,
        pausable_completion_factory_name="create_pausable_completion",
    )
    control = TaskControlService(tmp_path / "single-subprocess-cancel.sqlite")
    task_id = "single-host-subprocess-cancel"
    control.ensure_task(task_id)
    worker, _, errors = _start_structured_invoke(
        provider,
        control.cancellation.signal(task_id),
    )
    _wait_until(lambda: _progress_size(progress) >= 5)

    control.cancel_task(task_id, reason="single child cancellation")
    worker.join(timeout=5)

    assert worker.is_alive() is False
    assert _progress_size(cancel_count) == 1
    assert len(errors) == 1
    assert isinstance(errors[0], StructuredOutputError)
    assert errors[0].code == "control_cancelled"
    control.close()


def test_cancel_wins_while_subprocess_pause_acknowledgement_is_pending(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    progress = tmp_path / "pending-pause-progress"
    monkeypatch.setenv("UCA_SUBPROCESS_PROGRESS", str(progress))
    provider = HostSubprocessProvider(
        host_module_path=_host_module(tmp_path, UNACKNOWLEDGED_PAUSE_HOST_MODULE),
        host_python=sys.executable,
        pausable_completion_factory_name="create_pausable_completion",
    )
    coordinator = CancellationCoordinator(
        pause_ack_timeout_seconds=0.5,
        control_poll_interval_seconds=0.002,
    )
    control = TaskControlService(
        tmp_path / "cancel-pending-subprocess-pause.sqlite",
        cancellation=coordinator,
    )
    task_id = "cancel-pending-host-subprocess-pause"
    control.ensure_task(task_id)
    worker, _, worker_errors = _start_structured_invoke(
        provider,
        control.cancellation.signal(task_id),
    )
    _wait_until(lambda: _progress_size(progress) >= 5)
    pause_records: list[ControlState] = []
    pause_errors: list[BaseException] = []

    def pause() -> None:
        try:
            pause_records.append(control.pause_task(task_id).state)
        except BaseException as exc:  # captured for assertion in the parent thread
            pause_errors.append(exc)

    pause_worker = threading.Thread(target=pause)
    pause_worker.start()
    _wait_until(lambda: coordinator.is_pause_requested(task_id) and _progress_size(progress) >= 5)

    assert control.cancel_task(task_id).state is ControlState.CANCEL_REQUESTED
    pause_worker.join(timeout=5)
    worker.join(timeout=5)
    report = control.pause_report(task_id)

    assert pause_worker.is_alive() is False
    assert worker.is_alive() is False
    assert pause_errors == []
    assert pause_records == [ControlState.CANCEL_REQUESTED]
    assert report is not None
    assert report.active_pause_acknowledged is False
    assert coordinator.is_pause_requested(task_id) is False
    assert len(worker_errors) == 1
    assert isinstance(worker_errors[0], StructuredOutputError)
    assert worker_errors[0].code == "control_cancelled"
    control.close()


@pytest.mark.skipif(os.name != "posix", reason="process-group ownership is POSIX-only")
def test_cancel_while_subprocess_is_paused_cleans_descendant_process_group(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    progress = tmp_path / "descendant-progress"
    descendant_heartbeat = tmp_path / "descendant-heartbeat"
    descendant_stop = tmp_path / "descendant-stop"
    descendant_script = tmp_path / "descendant.py"
    descendant_script.write_text(
        """
import os
import signal
import time
from pathlib import Path

signal.signal(signal.SIGTERM, signal.SIG_IGN)
heartbeat = Path(os.environ["UCA_DESCENDANT_HEARTBEAT"])
stop = Path(os.environ["UCA_DESCENDANT_STOP"])
while not stop.exists():
    with heartbeat.open("a", encoding="utf-8") as stream:
        stream.write("x")
    time.sleep(0.01)
""",
        encoding="utf-8",
    )
    monkeypatch.setenv("UCA_SUBPROCESS_PROGRESS", str(progress))
    monkeypatch.setenv("UCA_DESCENDANT_HEARTBEAT", str(descendant_heartbeat))
    monkeypatch.setenv("UCA_DESCENDANT_STOP", str(descendant_stop))
    monkeypatch.setenv("UCA_DESCENDANT_SCRIPT", str(descendant_script))
    provider = HostSubprocessProvider(
        host_module_path=_host_module(tmp_path, DESCENDANT_PAUSABLE_HOST_MODULE),
        host_python=sys.executable,
        pausable_completion_factory_name="create_pausable_completion",
    )
    control = TaskControlService(tmp_path / "cancel-paused-subprocess.sqlite")
    task_id = "cancel-paused-host-subprocess"
    control.ensure_task(task_id)
    worker, _, errors = _start_structured_invoke(
        provider,
        control.cancellation.signal(task_id),
    )
    try:
        _wait_until(lambda: _progress_size(descendant_heartbeat) >= 5)
        _wait_until(lambda: _progress_size(progress) >= 5)

        assert control.pause_task(task_id).state is ControlState.PAUSED
        paused_progress = _progress_size(progress)
        heartbeat_at_pause = _progress_size(descendant_heartbeat)
        time.sleep(0.05)
        assert _progress_size(progress) == paused_progress
        assert _progress_size(descendant_heartbeat) > heartbeat_at_pause

        assert (
            control.cancel_task(task_id, reason="cancel paused subprocess").state
            is ControlState.CANCEL_REQUESTED
        )
        worker.join(timeout=5)
        stopped_heartbeat = _wait_until_file_stable(descendant_heartbeat)
        time.sleep(0.05)
        assert _progress_size(descendant_heartbeat) == stopped_heartbeat
        cancellation_report = control.cancellation_report(task_id)

        assert worker.is_alive() is False
        assert len(errors) == 1
        assert isinstance(errors[0], StructuredOutputError)
        assert errors[0].code == "control_cancelled"
        assert "PRIVATE_CANCEL_DETAIL" not in str(errors[0].diagnostics)
        assert cancellation_report is not None
        assert cancellation_report.active_operation_kinds == ("provider",)
        assert cancellation_report.owned_processes_observed == 0
        assert cancellation_report.owned_cancellable_operations_observed == 1
        assert cancellation_report.cancellable_operation_cancel_requests == 1
        assert cancellation_report.cancellable_operations_still_active == 0
        assert cancellation_report.cooperative_fallback is False
    finally:
        descendant_stop.write_text("stop", encoding="utf-8")
        if worker.is_alive():
            control.cancel_task(task_id, reason="test cleanup")
            worker.join(timeout=5)
        control.close()
