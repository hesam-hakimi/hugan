from __future__ import annotations

import json
import os
import queue
import signal
import socket
import subprocess
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from universal_coding_agent.core.cancellation import (
    CancellationSignal,
    OwnedOperationKind,
)
from universal_coding_agent.core.models import ModelCapabilities, ModelRequest, ModelResponse
from universal_coding_agent.providers.base import ModelProviderError

HOST_CLIENT_PATH_ENV = "UCA_HOST_CLIENT_PATH"
HOST_PYTHON_ENV = "UCA_HOST_PYTHON"
INVOKE_FUNCTION_ENV = "UCA_HOST_INVOKE_FUNCTION"
CLIENT_FACTORY_ENV = "UCA_HOST_CLIENT_FACTORY"
CONFIG_FACTORY_ENV = "UCA_HOST_MODEL_CONFIG_FACTORY"
DEPLOYMENT_ATTRIBUTE_ENV = "UCA_HOST_DEPLOYMENT_ATTRIBUTE"
PROBE_TOKENS_ENV = "UCA_HOST_PROBE_TOKENS"
JSON_MODE_ENV = "UCA_HOST_JSON_MODE"
TIMEOUT_ENV = "UCA_HOST_BRIDGE_TIMEOUT_SECONDS"
PAUSABLE_COMPLETION_FACTORY_ENV = "UCA_HOST_SUBPROCESS_PAUSABLE_COMPLETION_FACTORY"

_CONTROL_FD_ENV = "UCA_HOST_SUBPROCESS_CONTROL_FD"
_CONTROL_PROTOCOL = "uca-host-subprocess-pause/1"
_MAX_CONTROL_FRAME_BYTES = 1_048_576
_PROCESS_STOP_SECONDS = 1.0
_PROCESS_KILL_SECONDS = 0.25


@dataclass
class HostSubprocessProvider:
    """Run a site-owned model adapter in its own Python environment."""

    host_module_path: Path | str
    host_python: Path | str
    invoke_function_name: str = "invoke_text"
    client_factory_name: str = "create_client"
    config_factory_name: str = "get_configured_model_or_deployment"
    deployment_attribute: str = "deployment"
    json_mode: bool = True
    pausable_completion_factory_name: str | None = None

    def __post_init__(self) -> None:
        self.host_module_path = Path(self.host_module_path).expanduser().resolve()
        # Keep the interpreter's final symlink intact.  Virtual environments use
        # that executable path to discover their adjacent ``pyvenv.cfg``; resolving
        # it to the base interpreter silently drops the site's installed packages.
        host_python = Path(self.host_python).expanduser()
        self.host_python = host_python.parent.resolve() / host_python.name
        if not self.host_module_path.is_file():
            raise ModelProviderError("host_client_not_found", "host client module was not found")
        if not self.host_python.is_file():
            raise ModelProviderError(
                "host_python_not_found",
                "host Python interpreter was not found",
            )
        factory_name = str(self.pausable_completion_factory_name or "").strip()
        self.pausable_completion_factory_name = factory_name or None

    def capabilities(self) -> ModelCapabilities:
        return ModelCapabilities(
            structured_output=False,
            tool_calls=False,
            reasoning_tokens=True,
            actual_model_identity=True,
        )

    def probe_details(self) -> dict[str, Any]:
        return self._call_bridge(
            {
                "action": "probe",
                "max_output_tokens": max(8, int(os.getenv(PROBE_TOKENS_ENV, "16"))),
            },
            raise_on_error=False,
        )

    def probe(self) -> bool:
        return bool(self.probe_details().get("ok"))

    def invoke(self, request: ModelRequest) -> ModelResponse:
        return self._invoke(request)

    def invoke_cancellable(
        self,
        request: ModelRequest,
        cancellation: CancellationSignal,
    ) -> ModelResponse:
        return self._invoke(request, cancellation=cancellation)

    def _invoke(
        self,
        request: ModelRequest,
        *,
        cancellation: CancellationSignal | None = None,
    ) -> ModelResponse:
        payload = self._call_bridge(
            {
                "action": "invoke",
                "system_prompt": request.system_prompt,
                "user_prompt": request.user_prompt,
                "response_schema": request.response_schema,
                "max_output_tokens": request.max_output_tokens,
                "json_mode": self.json_mode,
            },
            cancellation=cancellation,
        )
        content = str(payload.get("content") or "")
        structured = _try_json_object(content)
        diagnostics = payload.get("safe_diagnostics")
        if not isinstance(diagnostics, dict):
            diagnostics = {}
        return ModelResponse(
            content=content,
            structured=structured,
            actual_model=_optional_text(payload.get("actual_model")),
            finish_reason=_optional_text(payload.get("finish_reason")),
            completion_tokens=_non_negative_int(payload.get("completion_tokens")),
            reasoning_tokens=_non_negative_int(payload.get("reasoning_tokens")),
            safe_diagnostics={
                str(key): value
                for key, value in diagnostics.items()
                if isinstance(value, (str, int, bool)) or value is None
            },
        )

    def _call_bridge(
        self,
        request: dict[str, Any],
        *,
        raise_on_error: bool = True,
        cancellation: CancellationSignal | None = None,
    ) -> dict[str, Any]:
        bridge = Path(__file__).with_name("host_bridge.py").resolve()
        payload = {
            **request,
            "host_client_path": str(self.host_module_path),
            "invoke_function": self.invoke_function_name,
            "client_factory": self.client_factory_name,
            "config_factory": self.config_factory_name,
            "deployment_attribute": self.deployment_attribute,
        }
        timeout = float(os.getenv(TIMEOUT_ENV, "120"))
        if cancellation is not None:
            cancellation.raise_if_cancelled()
        if (
            cancellation is not None
            and request.get("action") == "invoke"
            and self.pausable_completion_factory_name
        ):
            controlled_payload = {
                **payload,
                "pausable_completion_factory": self.pausable_completion_factory_name,
            }

            def start_pausable_bridge() -> _HostSubprocessPausableHandle:
                return _HostSubprocessPausableHandle(
                    self.host_python,
                    controlled_payload,
                    timeout_seconds=timeout,
                )

            with cancellation.owned_pausable_operation(
                OwnedOperationKind.PROVIDER,
                start_pausable_bridge,
            ) as operation:
                handle = cast(_HostSubprocessPausableHandle, operation)
                return handle.result()
        encoded = json.dumps(payload, separators=(",", ":"))

        def start_bridge() -> subprocess.Popen[str]:
            return subprocess.Popen(
                [str(self.host_python), str(bridge)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                start_new_session=True,
            )

        if cancellation is None:
            process = start_bridge()
            try:
                stdout, _stderr = process.communicate(encoded, timeout=timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate()
                raise
        else:
            with cancellation.owned_process(
                OwnedOperationKind.PROVIDER,
                start_bridge,
            ) as process:
                try:
                    stdout, _stderr = process.communicate(encoded, timeout=timeout)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.communicate()
                    raise
        try:
            result = json.loads(stdout)
        except (TypeError, ValueError):
            result = {
                "ok": False,
                "error_code": "host_bridge_output_invalid",
                "error_type": "BridgeOutputError",
                "error_stage": "bridge_output",
            }
        if not isinstance(result, dict):
            result = {
                "ok": False,
                "error_code": "host_bridge_output_invalid",
                "error_type": "BridgeOutputError",
                "error_stage": "bridge_output",
            }
        if not result.get("ok") and raise_on_error:
            code = str(result.get("error_code") or "host_bridge_failed")
            error_type = str(result.get("error_type") or "unknown")
            error_stage = str(result.get("error_stage") or "unknown")
            message = f"host bridge failed safely at {error_stage}: {error_type}"
            raise ModelProviderError(code, message)
        return result


def create_provider() -> HostSubprocessProvider:
    path_value = os.getenv(HOST_CLIENT_PATH_ENV, "").strip()
    python_value = os.getenv(HOST_PYTHON_ENV, "").strip()
    if not path_value:
        raise ModelProviderError(
            "host_client_path_missing",
            f"set {HOST_CLIENT_PATH_ENV} to the existing site-owned client module",
        )
    if not python_value:
        raise ModelProviderError(
            "host_python_missing",
            f"set {HOST_PYTHON_ENV} to the site's Python interpreter",
        )
    return HostSubprocessProvider(
        host_module_path=path_value,
        host_python=python_value,
        invoke_function_name=os.getenv(INVOKE_FUNCTION_ENV, "invoke_text").strip() or "invoke_text",
        client_factory_name=os.getenv(CLIENT_FACTORY_ENV, "create_client").strip()
        or "create_client",
        config_factory_name=(
            os.getenv(CONFIG_FACTORY_ENV, "get_configured_model_or_deployment").strip()
            or "get_configured_model_or_deployment"
        ),
        deployment_attribute=(
            os.getenv(DEPLOYMENT_ATTRIBUTE_ENV, "deployment").strip() or "deployment"
        ),
        json_mode=_truthy(os.getenv(JSON_MODE_ENV, "1")),
        pausable_completion_factory_name=(
            os.getenv(PAUSABLE_COMPLETION_FACTORY_ENV, "").strip() or None
        ),
    )


class _HostSubprocessPausableHandle:
    """Own one controlled child without treating process suspension as pause."""

    def __init__(
        self,
        host_python: Path,
        request: dict[str, Any],
        *,
        timeout_seconds: float,
    ) -> None:
        if os.name != "posix":
            raise ModelProviderError(
                "host_subprocess_pause_unsupported",
                "host subprocess active pause requires a POSIX control channel",
            )
        if timeout_seconds <= 0:
            raise ModelProviderError(
                "host_bridge_timeout_invalid",
                "host bridge timeout must be positive",
            )
        start_frame = _encode_control_frame(
            {
                "protocol": _CONTROL_PROTOCOL,
                "sequence": 1,
                "kind": "start",
                "payload": request,
            }
        )
        bridge = Path(__file__).with_name("host_subprocess_pause_bridge.py").resolve()
        parent_socket, child_socket = socket.socketpair()
        try:
            child_fd = child_socket.fileno()
            process = subprocess.Popen(
                [str(host_python), str(bridge)],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env={
                    **os.environ,
                    "PYTHONDONTWRITEBYTECODE": "1",
                    _CONTROL_FD_ENV: str(child_fd),
                },
                pass_fds=(child_fd,),
                start_new_session=True,
            )
        except BaseException:
            parent_socket.close()
            child_socket.close()
            raise
        child_socket.close()
        self._process = process
        self._socket = parent_socket
        self._timeout_seconds = timeout_seconds
        self._commands: queue.SimpleQueue[bytes | None] = queue.SimpleQueue()
        self._lock = threading.RLock()
        self._done = threading.Event()
        self._paused = threading.Event()
        self._cancel_requested = threading.Event()
        self._result_payload: dict[str, Any] | None = None
        self._error: tuple[str, str, str] | None = None
        self._terminal_state: str | None = None
        self._next_sequence = 2
        self._expected_child_sequence = 1
        self._ready_count = 0
        self._exit_watcher_started = False
        self._desired_pause = False
        self._last_pause_sequence: int | None = None
        self._last_resume_sequence: int | None = None
        self._writer = threading.Thread(
            target=self._write_frames,
            name="uca-host-subprocess-control-writer",
            daemon=True,
        )
        self._reader = threading.Thread(
            target=self._read_frames,
            name="uca-host-subprocess-control-reader",
            daemon=True,
        )
        self._writer.start()
        self._reader.start()
        self._commands.put(start_frame)

    def result(self) -> dict[str, Any]:
        if not self._done.wait(timeout=self._timeout_seconds):
            self.cancel()
            stopped = self._done.wait(timeout=_PROCESS_STOP_SECONDS + _PROCESS_KILL_SECONDS + 0.5)
            if not stopped:
                self._terminate_process()
            with self._lock:
                if self._process.poll() is None:
                    self._finish_when_process_exits()
                else:
                    self._done.set()
            self._close_socket()
            raise ModelProviderError(
                "host_subprocess_pause_timeout",
                "host subprocess pause bridge timed out safely",
            )
        self._reap_child()
        with self._lock:
            error = self._error
            payload = self._result_payload
        if error is not None:
            code, error_type, stage = error
            raise ModelProviderError(
                code,
                f"host subprocess pause bridge failed safely at {stage}: {error_type}",
            )
        if payload is None:
            raise ModelProviderError(
                "host_subprocess_pause_result_missing",
                "host subprocess pause bridge returned no result",
            )
        return payload

    def pause(self) -> None:
        with self._lock:
            if self._done.is_set() or self._cancel_requested.is_set():
                return
            self._desired_pause = True
            sequence = self._queue_action_locked("pause")
            self._last_pause_sequence = sequence

    def resume(self) -> None:
        with self._lock:
            if self._done.is_set() or self._cancel_requested.is_set():
                return
            self._desired_pause = False
            sequence = self._queue_action_locked("resume")
            self._last_resume_sequence = sequence

    def paused(self) -> bool:
        return self._paused.is_set()

    def cancel(self) -> None:
        with self._lock:
            if self._done.is_set() or self._cancel_requested.is_set():
                return
            self._cancel_requested.set()
            self._desired_pause = False
            self._paused.clear()
            self._queue_action_locked("cancel")
        threading.Thread(
            target=self._cancel_watchdog,
            name="uca-host-subprocess-cancel-watchdog",
            daemon=True,
        ).start()

    def done(self) -> bool:
        return self._done.is_set()

    def _queue_action_locked(self, kind: str) -> int:
        sequence = self._next_sequence
        self._next_sequence += 1
        self._commands.put(
            _encode_control_frame(
                {
                    "protocol": _CONTROL_PROTOCOL,
                    "sequence": sequence,
                    "kind": kind,
                }
            )
        )
        return sequence

    def _write_frames(self) -> None:
        while True:
            frame = self._commands.get()
            if frame is None:
                return
            try:
                self._socket.sendall(frame)
            except OSError:
                if not self._done.is_set():
                    self._fail(
                        "host_subprocess_pause_control_failed",
                        "ControlChannelError",
                        "control_write",
                    )
                return

    def _read_frames(self) -> None:
        try:
            stream = self._socket.makefile("rb", buffering=0)
            while not self._done.is_set():
                raw = stream.readline(_MAX_CONTROL_FRAME_BYTES + 1)
                if not raw:
                    if not self._done.is_set():
                        self._fail(
                            "host_subprocess_pause_eof",
                            "ControlChannelError",
                            "control_read",
                        )
                    return
                if len(raw) > _MAX_CONTROL_FRAME_BYTES or not raw.endswith(b"\n"):
                    self._fail(
                        "host_subprocess_pause_frame_invalid",
                        "ControlFrameError",
                        "control_read",
                    )
                    return
                try:
                    frame = json.loads(raw)
                except (TypeError, ValueError):
                    self._fail(
                        "host_subprocess_pause_frame_invalid",
                        "ControlFrameError",
                        "control_read",
                    )
                    return
                if not self._accept_child_frame(frame):
                    return
        except OSError:
            if not self._done.is_set():
                self._fail(
                    "host_subprocess_pause_control_failed",
                    "ControlChannelError",
                    "control_read",
                )

    def _accept_child_frame(self, value: Any) -> bool:
        if not isinstance(value, dict):
            return self._protocol_failure()
        protocol = value.get("protocol")
        sequence = value.get("sequence")
        kind = value.get("kind")
        with self._lock:
            if (
                protocol != _CONTROL_PROTOCOL
                or isinstance(sequence, bool)
                or not isinstance(sequence, int)
                or sequence != self._expected_child_sequence
                or not isinstance(kind, str)
            ):
                return self._protocol_failure_locked()
            self._expected_child_sequence += 1
            if kind == "ready" and set(value) == {"protocol", "sequence", "kind"}:
                if self._result_payload is not None or self._error is not None:
                    return self._protocol_failure_locked()
                self._ready_count += 1
                return True
            if kind in {"pause_ack", "resume_ack"} and set(value) == {
                "protocol",
                "sequence",
                "kind",
                "command_sequence",
            }:
                command_sequence = value.get("command_sequence")
                if isinstance(command_sequence, bool) or not isinstance(command_sequence, int):
                    return self._protocol_failure_locked()
                if (
                    self._ready_count == 0
                    or self._result_payload is not None
                    or self._error is not None
                ):
                    return self._protocol_failure_locked()
                if (
                    kind == "pause_ack"
                    and self._desired_pause
                    and command_sequence == self._last_pause_sequence
                ):
                    self._paused.set()
                    return True
                if (
                    kind == "resume_ack"
                    and not self._desired_pause
                    and command_sequence == self._last_resume_sequence
                ):
                    self._paused.clear()
                    return True
                return self._protocol_failure_locked()
            if kind == "result" and set(value) == {
                "protocol",
                "sequence",
                "kind",
                "payload",
            }:
                payload = value.get("payload")
                if (
                    not isinstance(payload, dict)
                    or self._ready_count == 0
                    or self._result_payload is not None
                    or self._error is not None
                ):
                    return self._protocol_failure_locked()
                self._result_payload = payload
                return True
            if kind == "error" and set(value) == {
                "protocol",
                "sequence",
                "kind",
                "error_code",
                "error_type",
                "error_stage",
            }:
                fields = (
                    value.get("error_code"),
                    value.get("error_type"),
                    value.get("error_stage"),
                )
                if not all(isinstance(item, str) and 0 < len(item) <= 128 for item in fields):
                    return self._protocol_failure_locked()
                if self._error is not None or self._result_payload is not None:
                    return self._protocol_failure_locked()
                self._error = cast(tuple[str, str, str], fields)
                return True
            if kind == "terminal" and set(value) == {
                "protocol",
                "sequence",
                "kind",
                "state",
            }:
                state = value.get("state")
                if state not in {"completed", "cancelled", "failed"}:
                    return self._protocol_failure_locked()
                if state == "completed" and self._result_payload is None:
                    return self._protocol_failure_locked()
                if state == "failed" and self._error is None:
                    return self._protocol_failure_locked()
                if state == "completed" and self._error is not None:
                    return self._protocol_failure_locked()
                if state == "failed" and self._result_payload is not None:
                    return self._protocol_failure_locked()
                if state == "cancelled" and not self._cancel_requested.is_set():
                    return self._protocol_failure_locked()
                if state != "cancelled" and self._cancel_requested.is_set():
                    return self._protocol_failure_locked()
                if state == "cancelled" and (
                    self._result_payload is not None or self._error is not None
                ):
                    return self._protocol_failure_locked()
                self._terminal_state = state
                self._paused.clear()
                if state == "cancelled":
                    self._terminate_process()
                if self._process.poll() is None:
                    self._finish_when_process_exits()
                    self._commands.put(None)
                    return False
                self._validate_terminal_exit_locked(self._process.returncode)
                self._done.set()
                self._commands.put(None)
                return False
            return self._protocol_failure_locked()

    def _protocol_failure(self) -> bool:
        with self._lock:
            return self._protocol_failure_locked()

    def _protocol_failure_locked(self) -> bool:
        self._fail_locked(
            "host_subprocess_pause_protocol_invalid",
            "ControlProtocolError",
            "control_read",
        )
        return False

    def _fail(self, code: str, error_type: str, stage: str) -> None:
        with self._lock:
            self._fail_locked(code, error_type, stage)

    def _fail_locked(self, code: str, error_type: str, stage: str) -> None:
        if self._done.is_set():
            return
        self._error = (code, error_type, stage)
        self._result_payload = None
        self._paused.clear()
        self._commands.put(None)
        self._terminate_process()
        if self._process.poll() is None:
            self._finish_when_process_exits()
        else:
            self._done.set()

    def _cancel_watchdog(self) -> None:
        if self._done.wait(timeout=_PROCESS_STOP_SECONDS):
            return
        self._terminate_process()
        with self._lock:
            if self._process.poll() is None:
                self._finish_when_process_exits()
            else:
                self._done.set()
        self._close_socket()

    def _terminate_process(self) -> None:
        try:
            os.killpg(self._process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            self._process.wait(timeout=_PROCESS_KILL_SECONDS)
        except subprocess.TimeoutExpired:
            pass
        try:
            os.killpg(self._process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        self._wait_for_process_exit()

    def _wait_for_process_exit(self) -> bool:
        try:
            self._process.wait(timeout=_PROCESS_KILL_SECONDS)
        except subprocess.TimeoutExpired:
            return False
        return True

    def _finish_when_process_exits(self) -> None:
        with self._lock:
            if self._exit_watcher_started:
                return
            self._exit_watcher_started = True

        def wait_and_finish() -> None:
            returncode = self._process.wait()
            with self._lock:
                self._validate_terminal_exit_locked(returncode)
                self._done.set()
                self._commands.put(None)
            self._close_socket()

        threading.Thread(
            target=wait_and_finish,
            name="uca-host-subprocess-exit-watcher",
            daemon=True,
        ).start()

    def _validate_terminal_exit_locked(self, returncode: int) -> None:
        if self._terminal_state == "completed" and returncode != 0:
            self._result_payload = None
            self._error = (
                "host_subprocess_pause_terminal_exit_invalid",
                "ChildLifecycleError",
                "terminal_exit",
            )
        elif self._terminal_state == "failed" and returncode == 0:
            self._error = (
                "host_subprocess_pause_terminal_exit_invalid",
                "ChildLifecycleError",
                "terminal_exit",
            )

    def _reap_child(self) -> None:
        try:
            self._process.wait(timeout=_PROCESS_KILL_SECONDS)
        except subprocess.TimeoutExpired:
            self._terminate_process()
        self._close_socket()

    def _close_socket(self) -> None:
        try:
            self._socket.close()
        except OSError:
            pass


def _encode_control_frame(frame: dict[str, Any]) -> bytes:
    encoded = json.dumps(frame, separators=(",", ":")).encode("utf-8") + b"\n"
    if len(encoded) > _MAX_CONTROL_FRAME_BYTES:
        raise ModelProviderError(
            "host_subprocess_pause_frame_too_large",
            "host subprocess pause control frame exceeded its byte limit",
        )
    return encoded


def _try_json_object(value: str) -> dict[str, Any] | None:
    try:
        payload = json.loads(value)
    except (TypeError, ValueError):
        return None
    return payload if isinstance(payload, dict) else None


def _non_negative_int(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return None
    return value


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() not in {"", "0", "false", "no", "off"}
