from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from dataclasses import asdict, dataclass
from threading import Event, Lock, Thread
from typing import Any

from universal_coding_agent.core.cancellation import (
    CancellationSignal,
    OwnedOperationKind,
)
from universal_coding_agent.core.models import (
    ModelCapabilities,
    ModelRequest,
    ModelResponse,
)
from universal_coding_agent.providers.base import ModelProviderError
from universal_coding_agent.safety.sanitizer import sanitize_text

Transport = Callable[[dict[str, Any]], dict[str, Any]]
OPENAI_BACKGROUND_CANCELLATION_ENV = "UCA_OPENAI_BACKGROUND_CANCELLATION"
_SCHEMA_NAME = re.compile(r"[^A-Za-z0-9_-]+")
_BACKGROUND_POLL_INTERVAL_SECONDS = 2.0
_BACKGROUND_CANCEL_POLL_INTERVAL_SECONDS = 0.25
_BACKGROUND_ACTIVE_STATUSES = frozenset({"in_progress", "queued"})
_BACKGROUND_TERMINAL_STATUSES = frozenset(
    {"cancelled", "completed", "failed", "incomplete"}
)
_SCHEMA_GENERATION_ONLY_KEYWORDS = frozenset(
    {
        "default",
        "examples",
        "format",
        "maxItems",
        "maxLength",
        "maximum",
        "minItems",
        "minLength",
        "minimum",
        "multipleOf",
        "pattern",
    }
)


@dataclass(frozen=True)
class OpenAIBackgroundLifecycleSnapshot:
    handle_started: bool
    response_id_observed: bool
    actual_model: str | None
    initial_status: str | None
    cancel_dispatched: bool
    cancel_response_status: str | None
    terminal_status: str | None
    terminal_confirmed: bool

    def to_json(self) -> dict[str, Any]:
        return asdict(self)


class OpenAIBackgroundLifecycleRecorder:
    """Thread-safe, identifier-free evidence for one trusted live lifecycle probe."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._handle_started = Event()
        self._response_id_observed = False
        self._actual_model: str | None = None
        self._initial_status: str | None = None
        self._cancel_dispatched = False
        self._cancel_response_status: str | None = None
        self._terminal_status: str | None = None
        self._terminal_confirmed = False

    def wait_for_handle(self, timeout_seconds: float) -> bool:
        return self._handle_started.wait(timeout_seconds)

    def snapshot(self) -> OpenAIBackgroundLifecycleSnapshot:
        with self._lock:
            return OpenAIBackgroundLifecycleSnapshot(
                handle_started=self._handle_started.is_set(),
                response_id_observed=self._response_id_observed,
                actual_model=self._actual_model,
                initial_status=self._initial_status,
                cancel_dispatched=self._cancel_dispatched,
                cancel_response_status=self._cancel_response_status,
                terminal_status=self._terminal_status,
                terminal_confirmed=self._terminal_confirmed,
            )

    def _record_handle_started(self) -> None:
        self._handle_started.set()

    def _record_created(self, response_id: str, status: str, actual_model: str) -> None:
        with self._lock:
            self._response_id_observed = bool(response_id)
            self._actual_model = actual_model
            self._initial_status = status

    def _record_cancel_dispatched(self, status: str, actual_model: str) -> None:
        with self._lock:
            self._cancel_dispatched = True
            self._cancel_response_status = status
            self._actual_model = actual_model

    def _record_terminal(self, status: str, actual_model: str) -> None:
        with self._lock:
            self._terminal_status = status
            self._terminal_confirmed = True
            self._actual_model = actual_model


class OpenAIResponsesProvider:
    """Opt-in OpenAI Responses API provider used only by the pre-transfer test lab."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        endpoint: str = "https://api.openai.com/v1/responses",
        timeout_seconds: float = 180,
        transport: Transport | None = None,
        background_cancellation: bool = False,
        background_lifecycle_recorder: OpenAIBackgroundLifecycleRecorder | None = None,
    ) -> None:
        api_key = api_key.strip()
        model = model.strip()
        if not api_key:
            raise ValueError("api_key must not be empty")
        if not model:
            raise ValueError("model must not be empty")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self.api_key = api_key
        self.model = model
        self.endpoint = endpoint
        self.timeout_seconds = timeout_seconds
        self._transport = transport
        self.background_cancellation = background_cancellation
        self.background_lifecycle_recorder = background_lifecycle_recorder

    @classmethod
    def from_env(
        cls,
        *,
        timeout_seconds: float = 180,
        background_lifecycle_recorder: OpenAIBackgroundLifecycleRecorder | None = None,
    ) -> OpenAIResponsesProvider:
        api_key = os.environ.get("OPENAI_API_KEY", "").strip()
        model = os.environ.get("UCA_OPENAI_MODEL", "").strip()
        if not api_key:
            raise ModelProviderError(
                "openai_configuration_missing",
                "OPENAI_API_KEY is required for live pre-transfer qualification",
            )
        if not model:
            raise ModelProviderError(
                "openai_configuration_missing",
                "UCA_OPENAI_MODEL is required for live pre-transfer qualification",
            )
        return cls(
            api_key=api_key,
            model=model,
            timeout_seconds=timeout_seconds,
            background_cancellation=_background_cancellation_enabled(
                os.environ.get(OPENAI_BACKGROUND_CANCELLATION_ENV)
            ),
            background_lifecycle_recorder=background_lifecycle_recorder,
        )

    def capabilities(self) -> ModelCapabilities:
        return ModelCapabilities(
            structured_output=True,
            tool_calls=False,
            reasoning_tokens=True,
            actual_model_identity=True,
        )

    def probe(self) -> bool:
        request = ModelRequest(
            role="probe",
            system_prompt="Return exactly the requested text.",
            user_prompt="Return UCA_OPENAI_PROVIDER_OK.",
            max_output_tokens=128,
        )
        try:
            response = self.invoke(request)
        except ModelProviderError:
            return False
        return bool(response.content.strip())

    def invoke(self, request: ModelRequest) -> ModelResponse:
        payload = self._payload(request)
        data = self._send(payload)
        return self._response(request, data)

    def invoke_cancellable(
        self,
        request: ModelRequest,
        cancellation: CancellationSignal,
    ) -> ModelResponse:
        cancellation.raise_if_cancelled()
        payload = self._payload(request)
        if not self.background_cancellation:
            data = self._send(payload)
            cancellation.raise_if_cancelled()
            return self._response(
                request,
                data,
                cancellation_mode="cooperative",
            )
        if self._transport is not None:
            raise ModelProviderError(
                "openai_background_transport_unsupported",
                "configured test transport does not own the OpenAI background lifecycle",
            )

        payload["background"] = True

        def start_operation() -> _OpenAIBackgroundResponseHandle:
            return _OpenAIBackgroundResponseHandle(self, payload)

        with cancellation.owned_cancellable_operation(
            OwnedOperationKind.PROVIDER,
            start_operation,
        ) as operation:
            handle = operation
            if not isinstance(handle, _OpenAIBackgroundResponseHandle):
                raise ModelProviderError(
                    "openai_background_handle_invalid",
                    "OpenAI background lifecycle returned an invalid owned handle",
                )
            data = handle.result()
            if not handle.done():
                raise ModelProviderError(
                    "openai_background_state_unconfirmed",
                    "OpenAI background response termination was not confirmed",
                )

        return self._response(
            request,
            data,
            cancellation_mode="owned_background_handle",
        )

    def _payload(self, request: ModelRequest) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self.model,
            "instructions": request.system_prompt,
            "input": request.user_prompt,
            "max_output_tokens": request.max_output_tokens,
            "store": False,
        }
        if request.response_schema is not None:
            payload["text"] = {
                "format": {
                    "type": "json_schema",
                    "name": _schema_name(request.role),
                    "schema": _openai_strict_schema(request.response_schema),
                    "strict": True,
                }
            }
        return payload

    def _response(
        self,
        request: ModelRequest,
        data: dict[str, Any],
        *,
        cancellation_mode: str | None = None,
    ) -> ModelResponse:
        output_text = _output_text(data)
        if not output_text:
            raise ModelProviderError(
                "openai_empty_output",
                "OpenAI Responses API returned no output text",
            )

        structured: dict[str, Any] | None = None
        if request.response_schema is not None:
            try:
                decoded = json.loads(output_text)
            except json.JSONDecodeError as exc:
                raise ModelProviderError(
                    "openai_invalid_structured_output",
                    "OpenAI Responses API returned non-JSON structured output",
                ) from exc
            if not isinstance(decoded, dict):
                raise ModelProviderError(
                    "openai_invalid_structured_output",
                    "OpenAI Responses API structured output was not one JSON object",
                )
            structured = decoded

        usage = data.get("usage") if isinstance(data.get("usage"), dict) else {}
        output_details = (
            usage.get("output_tokens_details")
            if isinstance(usage.get("output_tokens_details"), dict)
            else {}
        )
        status = str(data.get("status") or "").strip().lower()
        finish_reason = None
        if status == "incomplete":
            details = data.get("incomplete_details")
            if isinstance(details, dict):
                finish_reason = str(details.get("reason") or "incomplete")
            else:
                finish_reason = "incomplete"
        elif status:
            finish_reason = status

        response_id = str(data.get("id") or "")
        diagnostics: dict[str, str | int | bool | None] = {
            "provider": "openai_responses",
            "response_id": response_id,
            "store": False,
        }
        if cancellation_mode is not None:
            diagnostics["cancellation_mode"] = cancellation_mode
        if cancellation_mode == "owned_background_handle":
            diagnostics["background"] = True
            diagnostics["temporary_background_retention"] = True

        return ModelResponse(
            content=output_text,
            structured=structured,
            actual_model=str(data.get("model") or self.model),
            finish_reason=finish_reason,
            completion_tokens=_optional_nonnegative_int(usage.get("output_tokens")),
            reasoning_tokens=_optional_nonnegative_int(output_details.get("reasoning_tokens")),
            safe_diagnostics=diagnostics,
        )

    def _send(self, payload: dict[str, Any]) -> dict[str, Any]:
        if self._transport is not None:
            value = self._transport(payload)
            if not isinstance(value, dict):
                raise ModelProviderError(
                    "openai_response_invalid",
                    "test transport returned a non-object response",
                )
            return value

        return self._request_json(
            method="POST",
            endpoint=self.endpoint,
            payload=payload,
        )

    def _request_json(
        self,
        *,
        method: str,
        endpoint: str,
        payload: dict[str, Any] | None = None,
        timeout_seconds: float | None = None,
    ) -> dict[str, Any]:
        body = (
            json.dumps(payload, separators=(",", ":")).encode()
            if payload is not None
            else None
        )
        request_timeout = self.timeout_seconds if timeout_seconds is None else timeout_seconds
        request = urllib.request.Request(
            endpoint,
            data=body,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method=method,
        )
        try:
            with urllib.request.urlopen(request, timeout=request_timeout) as response:
                raw = response.read()
        except urllib.error.HTTPError as exc:
            try:
                detail = exc.read().decode("utf-8", errors="replace")
            except Exception:
                detail = ""
            safe_detail = sanitize_text(detail)[:2_000]
            raise ModelProviderError(
                "openai_http_error",
                f"OpenAI Responses API HTTP {exc.code}: {safe_detail}",
            ) from exc
        except urllib.error.URLError as exc:
            raise ModelProviderError(
                "openai_transport_error",
                f"OpenAI Responses API transport failed: {type(exc.reason).__name__}",
            ) from exc
        except TimeoutError as exc:
            raise ModelProviderError(
                "openai_transport_timeout",
                "OpenAI Responses API request timed out",
            ) from exc

        try:
            decoded = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ModelProviderError(
                "openai_response_invalid",
                "OpenAI Responses API returned an invalid JSON response",
            ) from exc
        if not isinstance(decoded, dict):
            raise ModelProviderError(
                "openai_response_invalid",
                "OpenAI Responses API response was not one JSON object",
            )
        return decoded


class _OpenAIBackgroundResponseHandle:
    """Own one opt-in OpenAI background response lifecycle."""

    def __init__(
        self,
        provider: OpenAIResponsesProvider,
        payload: dict[str, Any],
    ) -> None:
        self._provider = provider
        self._payload = dict(payload)
        self._deadline = time.monotonic() + provider.timeout_seconds
        self._cancel_requested = Event()
        self._terminal_confirmed = Event()
        self._worker_finished = Event()
        self._result: dict[str, Any] | None = None
        self._error: Exception | None = None
        self._worker = Thread(
            target=self._run,
            name="uca-openai-background-response",
            daemon=True,
        )
        if self._provider.background_lifecycle_recorder is not None:
            self._provider.background_lifecycle_recorder._record_handle_started()
        self._worker.start()

    def result(self) -> dict[str, Any]:
        self._worker_finished.wait()
        if self._error is not None:
            raise self._error
        if self._result is None:
            raise ModelProviderError(
                "openai_background_response_invalid",
                "OpenAI background lifecycle returned no response",
            )
        return self._result

    def cancel(self) -> None:
        """Latch one non-blocking request for the owned worker to cancel remotely."""

        self._cancel_requested.set()

    def done(self) -> bool:
        """Report only a remotely observed terminal response status."""

        return self._terminal_confirmed.is_set()

    def _run(self) -> None:
        try:
            self._run_lifecycle()
        except Exception as exc:
            self._error = exc
        finally:
            self._worker_finished.set()

    def _run_lifecycle(self) -> None:
        data = self._request_json(
            method="POST",
            endpoint=self._provider.endpoint,
            payload=self._payload,
        )
        response_id = _background_response_id(data)
        status = _background_status(data)
        recorder = self._provider.background_lifecycle_recorder
        if recorder is not None:
            recorder._record_created(
                response_id,
                status,
                str(data.get("model") or self._provider.model),
            )
        if status in _BACKGROUND_TERMINAL_STATUSES:
            self._record_terminal(data)
            return
        if status not in _BACKGROUND_ACTIVE_STATUSES:
            raise ModelProviderError(
                "openai_background_state_unconfirmed",
                "OpenAI background response returned an unknown lifecycle status",
            )

        cancel_dispatched = False
        response_endpoint = (
            f"{self._provider.endpoint.rstrip('/')}"
            f"/{urllib.parse.quote(response_id, safe='')}"
        )
        while True:
            cancel_request = False
            if self._cancel_requested.is_set() and not cancel_dispatched:
                data = self._request_json(
                    method="POST",
                    endpoint=f"{response_endpoint}/cancel",
                )
                cancel_dispatched = True
                cancel_request = True
            else:
                if cancel_dispatched:
                    poll_delay = min(
                        _BACKGROUND_CANCEL_POLL_INTERVAL_SECONDS,
                        self._remaining_seconds(),
                    )
                    time.sleep(poll_delay)
                else:
                    poll_delay = min(
                        _BACKGROUND_POLL_INTERVAL_SECONDS,
                        self._remaining_seconds(),
                    )
                    if self._cancel_requested.wait(poll_delay):
                        continue
                data = self._request_json(
                    method="GET",
                    endpoint=response_endpoint,
                )

            _validate_background_response_id(data, response_id)
            status = _background_status(data)
            if cancel_request and recorder is not None:
                recorder._record_cancel_dispatched(
                    status,
                    str(data.get("model") or self._provider.model),
                )
            if status in _BACKGROUND_TERMINAL_STATUSES:
                self._record_terminal(data)
                return
            if status not in _BACKGROUND_ACTIVE_STATUSES:
                raise ModelProviderError(
                    "openai_background_state_unconfirmed",
                    "OpenAI background response returned an unknown lifecycle status",
                )

    def _request_json(
        self,
        *,
        method: str,
        endpoint: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        remaining = self._remaining_seconds()
        try:
            return self._provider._request_json(
                method=method,
                endpoint=endpoint,
                payload=payload,
                timeout_seconds=remaining,
            )
        except ModelProviderError as exc:
            if time.monotonic() >= self._deadline:
                raise _background_timeout_error() from exc
            raise

    def _remaining_seconds(self) -> float:
        remaining = self._deadline - time.monotonic()
        if remaining <= 0:
            raise _background_timeout_error()
        return remaining

    def _record_terminal(self, data: dict[str, Any]) -> None:
        status = _background_status(data)
        self._result = data
        if self._provider.background_lifecycle_recorder is not None:
            self._provider.background_lifecycle_recorder._record_terminal(
                status,
                str(data.get("model") or self._provider.model),
            )
        self._terminal_confirmed.set()


def _background_response_id(data: dict[str, Any]) -> str:
    response_id = str(data.get("id") or "").strip()
    if not response_id:
        raise ModelProviderError(
            "openai_background_response_invalid",
            "OpenAI background response omitted its lifecycle identifier",
        )
    return response_id


def _validate_background_response_id(
    data: dict[str, Any],
    expected_response_id: str,
) -> None:
    if _background_response_id(data) != expected_response_id:
        raise ModelProviderError(
            "openai_background_state_unconfirmed",
            "OpenAI background lifecycle returned a different response identifier",
        )


def _background_status(data: dict[str, Any]) -> str:
    status = str(data.get("status") or "").strip().lower()
    if not status:
        raise ModelProviderError(
            "openai_background_response_invalid",
            "OpenAI background response omitted its lifecycle status",
        )
    return status


def _background_timeout_error() -> ModelProviderError:
    return ModelProviderError(
        "openai_background_timeout",
        "OpenAI background response exceeded its bounded lifecycle timeout",
    )


def _openai_strict_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Lower a Pydantic schema to the strict Structured Outputs generation subset.

    Core Pydantic validation remains authoritative after the model response. This adapter only
    changes the provider-facing generation grammar: object fields are made explicit/required,
    additional properties are forbidden, and validation-only constraints/defaults that are not
    needed to describe the JSON shape are removed.
    """

    lowered = _lower_schema_node(schema)
    if not isinstance(lowered, dict):
        raise TypeError("response schema must lower to one JSON object")
    return lowered


def _lower_schema_node(value: Any) -> Any:
    if isinstance(value, list):
        return [_lower_schema_node(item) for item in value]
    if not isinstance(value, dict):
        return value

    lowered = {
        key: _lower_schema_node(item)
        for key, item in value.items()
        if key not in _SCHEMA_GENERATION_ONLY_KEYWORDS
    }
    properties = lowered.get("properties")
    if isinstance(properties, dict):
        lowered["required"] = list(properties)
        lowered["additionalProperties"] = False
    return lowered


def _schema_name(role: str) -> str:
    value = _SCHEMA_NAME.sub("_", role).strip("_") or "response"
    return f"uca_{value}"[:64]


def _output_text(payload: dict[str, Any]) -> str:
    chunks: list[str] = []
    output = payload.get("output")
    if not isinstance(output, list):
        return ""
    for item in output:
        if not isinstance(item, dict) or item.get("type") != "message":
            continue
        content = item.get("content")
        if not isinstance(content, list):
            continue
        for part in content:
            if not isinstance(part, dict) or part.get("type") != "output_text":
                continue
            text = part.get("text")
            if isinstance(text, str):
                chunks.append(text)
    return "".join(chunks)


def _optional_nonnegative_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int) and value >= 0:
        return value
    return None


def _background_cancellation_enabled(value: str | None) -> bool:
    normalized = str(value or "").strip().lower()
    if normalized in {"", "0", "false", "no", "off"}:
        return False
    if normalized in {"1", "true", "yes", "on"}:
        return True
    raise ModelProviderError(
        "openai_configuration_invalid",
        f"{OPENAI_BACKGROUND_CANCELLATION_ENV} must be an explicit boolean value",
    )
