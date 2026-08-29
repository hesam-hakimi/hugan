from __future__ import annotations

import importlib.util
import json
import os
import socket
import sys
import threading
import time
from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from typing import Any, TypeVar

_T = TypeVar("_T")
_CONTROL_FD_ENV = "UCA_HOST_SUBPROCESS_CONTROL_FD"
_PROTOCOL = "uca-host-subprocess-pause/1"
_MAX_FRAME_BYTES = 1_048_576
_HANDLE_STOP_SECONDS = 0.5


class _SafeBridgeError(Exception):
    def __init__(self, code: str, stage: str, cause_type: str) -> None:
        super().__init__(code)
        self.code = code
        self.stage = stage
        self.cause_type = cause_type


def _at_stage(
    stage: str,
    code: str,
    operation: Callable[[], _T],
) -> _T:
    try:
        return operation()
    except _SafeBridgeError:
        raise
    except Exception as exc:
        raise _SafeBridgeError(code, stage, type(exc).__name__) from exc


def _load_module(path: Path) -> ModuleType:
    module_name = f"_uca_host_subprocess_pause_{abs(hash(str(path)))}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("host_client_load_failed")
    module = importlib.util.module_from_spec(spec)
    parent = str(path.parent)
    if parent not in sys.path:
        sys.path.insert(0, parent)
    previous = sys.modules.get(module_name)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        if previous is None:
            sys.modules.pop(module_name, None)
        else:
            sys.modules[module_name] = previous
        raise
    return module


def _call_factory(module: ModuleType, name: str) -> Any:
    factory = getattr(module, name, None)
    if not callable(factory):
        raise RuntimeError("host_factory_missing")
    return factory()


def _deployment(module: ModuleType, request: dict[str, Any]) -> str:
    config = _call_factory(module, str(request["config_factory"]))
    attribute = str(request["deployment_attribute"])
    value = (
        config.get(attribute)
        if isinstance(config, dict)
        else getattr(
            config,
            attribute,
            None,
        )
    )
    deployment = str(value or "").strip()
    if not deployment:
        raise RuntimeError("host_deployment_missing")
    return deployment


def _require_handle(value: Any) -> Any:
    missing = [
        name
        for name in ("result", "cancel", "done", "pause", "resume", "paused")
        if not callable(getattr(value, name, None))
    ]
    if missing:
        raise _SafeBridgeError(
            "host_pausable_handle_invalid",
            "create_pausable_handle",
            "HandleContractError",
        )
    return value


def _looks_like_parameter_error(exc: Exception, parameter: str) -> bool:
    text = str(exc).lower()
    parameter_text = parameter.lower()
    return parameter_text in text and any(
        marker in text for marker in ("unsupported", "unknown", "unexpected", "invalid")
    )


def _message_text(message: Any) -> str:
    value = getattr(message, "content", "") if message is not None else ""
    if isinstance(value, str):
        return value
    if not isinstance(value, list):
        return ""
    parts: list[str] = []
    for item in value:
        text = item.get("text") if isinstance(item, dict) else getattr(item, "text", None)
        if isinstance(text, str):
            parts.append(text)
    return "".join(parts)


def _non_negative_int(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return None
    return value


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


class _ControlSession:
    def __init__(self, control: socket.socket, stream: Any) -> None:
        self._control = control
        self._stream = stream
        self._send_lock = threading.Lock()
        self._state_lock = threading.RLock()
        self._stop = threading.Event()
        self._cancelled = threading.Event()
        self._next_outbound_sequence = 1
        self._expected_inbound_sequence = 2
        self._handle: Any = None
        self._desired_pause = False
        self._pause_sequence: int | None = None
        self._resume_sequence: int | None = None
        self._pause_applied: int | None = None
        self._resume_applied: int | None = None
        self._pause_acknowledged: int | None = None
        self._resume_acknowledged: int | None = None
        self._cancel_applied = False
        self._control_seen = False
        self._reader = threading.Thread(
            target=self._read_controls,
            name="uca-host-subprocess-child-control-reader",
            daemon=True,
        )
        self._monitor = threading.Thread(
            target=self._monitor_handle,
            name="uca-host-subprocess-child-control-monitor",
            daemon=True,
        )

    @property
    def cancelled(self) -> bool:
        return self._cancelled.is_set()

    @property
    def control_seen(self) -> bool:
        with self._state_lock:
            return self._control_seen

    def start(self) -> None:
        self._reader.start()
        self._monitor.start()

    def stop(self) -> None:
        self._stop.set()

    def set_handle(self, handle: Any) -> None:
        with self._state_lock:
            self._handle = handle
            self._pause_applied = None
            self._resume_applied = None
            self._pause_acknowledged = None
            self._resume_acknowledged = None
            self._cancel_applied = False
        self.emit("ready")

    def clear_handle(self, handle: Any) -> None:
        with self._state_lock:
            if self._handle is handle:
                self._handle = None

    def emit(self, kind: str, **fields: Any) -> None:
        with self._send_lock:
            frame = {
                "protocol": _PROTOCOL,
                "sequence": self._next_outbound_sequence,
                "kind": kind,
                **fields,
            }
            encoded = json.dumps(frame, separators=(",", ":")).encode("utf-8") + b"\n"
            if len(encoded) > _MAX_FRAME_BYTES:
                raise _SafeBridgeError(
                    "host_subprocess_pause_frame_too_large",
                    "control_write",
                    "ControlFrameError",
                )
            try:
                self._control.sendall(encoded)
            except OSError as exc:
                self._stop.set()
                raise _SafeBridgeError(
                    "host_subprocess_pause_control_failed",
                    "control_write",
                    type(exc).__name__,
                ) from exc
            self._next_outbound_sequence += 1

    def _read_controls(self) -> None:
        try:
            while not self._stop.is_set():
                frame = _read_frame(self._stream)
                if frame is None:
                    self._cancelled.set()
                    self._cancel_active_handle()
                    return
                self._accept_control(frame)
        except _SafeBridgeError:
            self._cancelled.set()
            self._cancel_active_handle()
            self._stop.set()

    def _accept_control(self, value: Any) -> None:
        if not isinstance(value, dict) or set(value) != {
            "protocol",
            "sequence",
            "kind",
        }:
            raise _SafeBridgeError(
                "host_subprocess_pause_protocol_invalid",
                "control_read",
                "ControlProtocolError",
            )
        sequence = value.get("sequence")
        kind = value.get("kind")
        if (
            value.get("protocol") != _PROTOCOL
            or isinstance(sequence, bool)
            or not isinstance(sequence, int)
            or sequence != self._expected_inbound_sequence
            or kind not in {"pause", "resume", "cancel"}
        ):
            raise _SafeBridgeError(
                "host_subprocess_pause_protocol_invalid",
                "control_read",
                "ControlProtocolError",
            )
        self._expected_inbound_sequence += 1
        with self._state_lock:
            self._control_seen = True
            if kind == "pause":
                self._desired_pause = True
                self._pause_sequence = sequence
            elif kind == "resume":
                self._desired_pause = False
                self._resume_sequence = sequence
            else:
                self._desired_pause = False
                self._cancelled.set()

    def _monitor_handle(self) -> None:
        while not self._stop.is_set():
            with self._state_lock:
                handle = self._handle
                desired_pause = self._desired_pause
                pause_sequence = self._pause_sequence
                resume_sequence = self._resume_sequence
                pause_applied = self._pause_applied
                resume_applied = self._resume_applied
                pause_acknowledged = self._pause_acknowledged
                resume_acknowledged = self._resume_acknowledged
            if handle is not None:
                try:
                    if self._cancelled.is_set():
                        self._cancel_handle(handle)
                    elif not bool(handle.done()):
                        if desired_pause and pause_sequence is not None:
                            if pause_applied != pause_sequence:
                                handle.pause()
                                with self._state_lock:
                                    self._pause_applied = pause_sequence
                            paused_now = bool(handle.paused())
                            live_now = not bool(handle.done())
                            with self._state_lock:
                                pause_still_current = bool(
                                    self._handle is handle
                                    and self._desired_pause
                                    and self._pause_sequence == pause_sequence
                                )
                            if (
                                paused_now
                                and live_now
                                and pause_still_current
                                and pause_acknowledged != pause_sequence
                            ):
                                self.emit(
                                    "pause_ack",
                                    command_sequence=pause_sequence,
                                )
                                with self._state_lock:
                                    self._pause_acknowledged = pause_sequence
                        elif resume_sequence is not None:
                            if resume_applied != resume_sequence:
                                handle.resume()
                                with self._state_lock:
                                    self._resume_applied = resume_sequence
                            resumed_now = not bool(handle.paused())
                            live_now = not bool(handle.done())
                            with self._state_lock:
                                resume_still_current = bool(
                                    self._handle is handle
                                    and not self._desired_pause
                                    and self._resume_sequence == resume_sequence
                                )
                            if (
                                resumed_now
                                and live_now
                                and resume_still_current
                                and resume_acknowledged != resume_sequence
                            ):
                                self.emit(
                                    "resume_ack",
                                    command_sequence=resume_sequence,
                                )
                                with self._state_lock:
                                    self._resume_acknowledged = resume_sequence
                except Exception:
                    self._cancelled.set()
                    self._cancel_active_handle()
                    self._stop.set()
                    return
            time.sleep(0.005)

    def _cancel_active_handle(self) -> None:
        with self._state_lock:
            handle = self._handle
        if handle is None:
            return
        self._cancel_handle(handle)

    def _cancel_handle(self, handle: Any) -> None:
        with self._state_lock:
            if self._handle is not handle or self._cancel_applied:
                return
            self._cancel_applied = True
        try:
            handle.cancel()
        except Exception:
            pass


def _read_frame(stream: Any) -> dict[str, Any] | None:
    raw = stream.readline(_MAX_FRAME_BYTES + 1)
    if not raw:
        return None
    if len(raw) > _MAX_FRAME_BYTES or not raw.endswith(b"\n"):
        raise _SafeBridgeError(
            "host_subprocess_pause_frame_invalid",
            "control_read",
            "ControlFrameError",
        )
    try:
        value = json.loads(raw)
    except (TypeError, ValueError) as exc:
        raise _SafeBridgeError(
            "host_subprocess_pause_frame_invalid",
            "control_read",
            "ControlFrameError",
        ) from exc
    if not isinstance(value, dict):
        raise _SafeBridgeError(
            "host_subprocess_pause_frame_invalid",
            "control_read",
            "ControlFrameError",
        )
    return value


def _emit_bootstrap_failure(
    control: socket.socket,
    error: _SafeBridgeError,
) -> None:
    frames = (
        {
            "protocol": _PROTOCOL,
            "sequence": 1,
            "kind": "error",
            "error_code": error.code,
            "error_type": error.cause_type,
            "error_stage": error.stage,
        },
        {
            "protocol": _PROTOCOL,
            "sequence": 2,
            "kind": "terminal",
            "state": "failed",
        },
    )
    try:
        for frame in frames:
            encoded = json.dumps(frame, separators=(",", ":")).encode("utf-8") + b"\n"
            if len(encoded) > _MAX_FRAME_BYTES:
                return
            control.sendall(encoded)
    except OSError:
        pass


def _validate_start(frame: dict[str, Any]) -> dict[str, Any]:
    if set(frame) != {"protocol", "sequence", "kind", "payload"}:
        raise _SafeBridgeError(
            "host_subprocess_pause_protocol_invalid",
            "start",
            "ControlProtocolError",
        )
    payload = frame.get("payload")
    sequence = frame.get("sequence")
    if (
        frame.get("protocol") != _PROTOCOL
        or isinstance(sequence, bool)
        or sequence != 1
        or frame.get("kind") != "start"
        or not isinstance(payload, dict)
    ):
        raise _SafeBridgeError(
            "host_subprocess_pause_protocol_invalid",
            "start",
            "ControlProtocolError",
        )
    expected = {
        "action",
        "system_prompt",
        "user_prompt",
        "response_schema",
        "max_output_tokens",
        "json_mode",
        "host_client_path",
        "invoke_function",
        "client_factory",
        "config_factory",
        "deployment_attribute",
        "pausable_completion_factory",
    }
    if set(payload) != expected or payload.get("action") != "invoke":
        raise _SafeBridgeError(
            "host_subprocess_pause_request_invalid",
            "start",
            "ControlProtocolError",
        )
    text_fields = (
        "system_prompt",
        "user_prompt",
        "host_client_path",
        "invoke_function",
        "client_factory",
        "config_factory",
        "deployment_attribute",
        "pausable_completion_factory",
    )
    if not all(isinstance(payload.get(name), str) for name in text_fields):
        raise _SafeBridgeError(
            "host_subprocess_pause_request_invalid",
            "start",
            "ControlProtocolError",
        )
    max_tokens = payload.get("max_output_tokens")
    if (
        isinstance(max_tokens, bool)
        or not isinstance(max_tokens, int)
        or not 1 <= max_tokens <= 1_000_000
        or not isinstance(payload.get("json_mode"), bool)
        or payload.get("response_schema") is not None
        and not isinstance(payload.get("response_schema"), dict)
    ):
        raise _SafeBridgeError(
            "host_subprocess_pause_request_invalid",
            "start",
            "ControlProtocolError",
        )
    return payload


def _await_attempt(
    session: _ControlSession,
    factory: Callable[..., Any],
    client: Any,
    kwargs: dict[str, Any],
) -> Any:
    handle = _at_stage(
        "create_pausable_handle",
        "host_pausable_factory_failed",
        lambda: _require_handle(factory(client=client, **kwargs)),
    )
    session.set_handle(handle)
    try:
        return handle.result()
    except Exception:
        try:
            active = not bool(handle.done())
        except Exception:
            active = True
        if active:
            session._cancel_handle(handle)
            deadline = time.monotonic() + _HANDLE_STOP_SECONDS
            stopped = False
            while time.monotonic() < deadline:
                try:
                    if bool(handle.done()):
                        stopped = True
                        break
                except Exception:
                    break
                time.sleep(0.005)
            if not stopped:
                raise _SafeBridgeError(
                    "host_pausable_handle_still_active",
                    "await_pausable_handle",
                    "HandleLifecycleError",
                ) from None
        raise
    finally:
        session.clear_handle(handle)


def _create_completion(
    session: _ControlSession,
    module: ModuleType,
    client: Any,
    deployment: str,
    *,
    messages: list[dict[str, str]],
    max_output_tokens: int,
    use_json_mode: bool,
    factory_name: str,
) -> tuple[Any, dict[str, str | bool]]:
    factory = getattr(module, factory_name, None)
    if not callable(factory):
        raise _SafeBridgeError(
            "host_pausable_factory_missing",
            "create_pausable_handle",
            "FactoryMissingError",
        )
    base: dict[str, Any] = {"model": deployment, "messages": messages}
    if use_json_mode:
        base["response_format"] = {"type": "json_object"}
    last_error: Exception | None = None
    for token_parameter in ("max_completion_tokens", "max_tokens"):
        kwargs = dict(base)
        kwargs[token_parameter] = max_output_tokens
        try:
            return _await_attempt(session, factory, client, kwargs), {
                "token_parameter": token_parameter,
                "json_mode_requested": use_json_mode,
                "json_mode_used": use_json_mode,
            }
        except _SafeBridgeError:
            raise
        except Exception as exc:
            last_error = exc
            if session.cancelled:
                raise
            if session.control_seen:
                break
            if _looks_like_parameter_error(exc, token_parameter):
                continue
            if use_json_mode and _looks_like_parameter_error(exc, "response_format"):
                fallback = dict(kwargs)
                fallback.pop("response_format", None)
                try:
                    return _await_attempt(session, factory, client, fallback), {
                        "token_parameter": token_parameter,
                        "json_mode_requested": True,
                        "json_mode_used": False,
                    }
                except _SafeBridgeError:
                    raise
                except Exception as fallback_exc:
                    last_error = fallback_exc
            break
    cause_type = type(last_error).__name__ if last_error is not None else "RuntimeError"
    raise _SafeBridgeError(
        "host_model_invoke_failed",
        "await_pausable_handle",
        cause_type,
    )


def _run(request: dict[str, Any], session: _ControlSession) -> dict[str, Any]:
    path = Path(str(request["host_client_path"])).expanduser().resolve()
    if not path.is_file():
        raise _SafeBridgeError(
            "host_client_not_found",
            "load_host_module",
            "FileNotFoundError",
        )
    module = _at_stage(
        "load_host_module",
        "host_client_load_failed",
        lambda: _load_module(path),
    )
    client = _at_stage(
        "create_host_client",
        "host_client_factory_failed",
        lambda: _call_factory(module, str(request["client_factory"])),
    )
    deployment = _at_stage(
        "resolve_host_deployment",
        "host_model_config_failed",
        lambda: _deployment(module, request),
    )
    system_prompt = str(request["system_prompt"])
    response_schema = request.get("response_schema")
    if isinstance(response_schema, dict):
        schema = json.dumps(response_schema, separators=(",", ":"), sort_keys=True)
        system_prompt += "\n\nRequired JSON Schema (return one JSON object only):\n" + schema
    response, metadata = _create_completion(
        session,
        module,
        client,
        deployment,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": str(request["user_prompt"])},
        ],
        max_output_tokens=int(request["max_output_tokens"]),
        use_json_mode=bool(response_schema) and bool(request["json_mode"]),
        factory_name=str(request["pausable_completion_factory"]),
    )
    if session.cancelled:
        raise RuntimeError("cancelled")

    def build_payload() -> dict[str, Any]:
        choice = response.choices[0] if getattr(response, "choices", None) else None
        message = getattr(choice, "message", None)
        usage = getattr(response, "usage", None)
        details = getattr(usage, "completion_tokens_details", None)
        content = _message_text(message)
        return {
            "ok": True,
            "content": content,
            "actual_model": _optional_text(getattr(response, "model", None)),
            "finish_reason": _optional_text(getattr(choice, "finish_reason", None)),
            "completion_tokens": _non_negative_int(getattr(usage, "completion_tokens", None)),
            "reasoning_tokens": _non_negative_int(getattr(details, "reasoning_tokens", None)),
            "safe_diagnostics": {
                "provider": "host_subprocess",
                "transport": "host_subprocess_pausable_bridge",
                "requested_deployment": deployment,
                "visible_content_length": len(content),
                **metadata,
            },
        }

    return _at_stage(
        "read_host_response",
        "host_response_invalid",
        build_payload,
    )


def main() -> int:
    fd_value = os.getenv(_CONTROL_FD_ENV, "").strip()
    try:
        fd = int(fd_value)
    except ValueError:
        return 2
    control = socket.socket(fileno=fd)
    stream = control.makefile("rb", buffering=0)
    session: _ControlSession | None = None
    succeeded = False
    try:
        start = _read_frame(stream)
        if start is None:
            raise _SafeBridgeError(
                "host_subprocess_pause_eof",
                "start",
                "ControlChannelError",
            )
        request = _validate_start(start)
        session = _ControlSession(control, stream)
        session.start()
        payload = _run(request, session)
        if session.cancelled:
            session.emit("terminal", state="cancelled")
            return 0
        session.emit("result", payload=payload)
        session.emit("terminal", state="completed")
        succeeded = True
        return 0
    except _SafeBridgeError as exc:
        if session is None:
            _emit_bootstrap_failure(control, exc)
        else:
            try:
                if session.cancelled:
                    session.emit("terminal", state="cancelled")
                else:
                    session.emit(
                        "error",
                        error_code=exc.code,
                        error_type=exc.cause_type,
                        error_stage=exc.stage,
                    )
                    session.emit("terminal", state="failed")
            except _SafeBridgeError:
                pass
        return 1
    except Exception as exc:
        if session is not None:
            try:
                if session.cancelled:
                    session.emit("terminal", state="cancelled")
                else:
                    session.emit(
                        "error",
                        error_code="host_subprocess_pause_bridge_failed",
                        error_type=type(exc).__name__,
                        error_stage="bridge",
                    )
                    session.emit("terminal", state="failed")
            except _SafeBridgeError:
                pass
        return 1
    finally:
        if session is not None:
            session.stop()
        try:
            stream.close()
        except OSError:
            pass
        try:
            control.close()
        except OSError:
            pass
        if not succeeded and session is not None:
            session.stop()


if __name__ == "__main__":
    raise SystemExit(main())
