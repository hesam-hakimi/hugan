from __future__ import annotations

import importlib.util
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any, Protocol, cast

from universal_coding_agent.core.cancellation import (
    CancellationRequested,
    CancellationSignal,
    OwnedOperationKind,
)
from universal_coding_agent.core.models import ModelCapabilities, ModelRequest, ModelResponse
from universal_coding_agent.providers.base import ModelProviderError

HOST_CLIENT_PATH_ENV = "UCA_HOST_CLIENT_PATH"
CLIENT_FACTORY_ENV = "UCA_HOST_CLIENT_FACTORY"
CONFIG_FACTORY_ENV = "UCA_HOST_MODEL_CONFIG_FACTORY"
DEPLOYMENT_ATTRIBUTE_ENV = "UCA_HOST_DEPLOYMENT_ATTRIBUTE"
PROBE_TOKENS_ENV = "UCA_HOST_PROBE_TOKENS"
JSON_MODE_ENV = "UCA_HOST_JSON_MODE"
CANCELLABLE_COMPLETION_FACTORY_ENV = "UCA_HOST_CANCELLABLE_COMPLETION_FACTORY"
PAUSABLE_COMPLETION_FACTORY_ENV = "UCA_HOST_PAUSABLE_COMPLETION_FACTORY"


class _HostCompletionHandle(Protocol):
    def result(self) -> Any:
        """Wait for and return the host completion result."""

    def cancel(self) -> None:
        """Request termination without blocking."""

    def done(self) -> bool:
        """Return without blocking whether the host operation has terminated."""


class _HostPausableCompletionHandle(_HostCompletionHandle, Protocol):
    def pause(self) -> None:
        """Request a cooperative pause without blocking."""

    def resume(self) -> None:
        """Request continuation without blocking."""

    def paused(self) -> bool:
        """Return without blocking whether the operation acknowledged its pause."""


@dataclass
class HostChatCompletionsProvider:
    """Adapt a site-owned client with optional explicit completion-handle ownership."""

    host_module_path: Path
    client_factory_name: str = "create_client"
    config_factory_name: str = "get_configured_model_or_deployment"
    deployment_attribute: str = "deployment"
    json_mode: bool = True
    cancellable_completion_factory_name: str | None = None
    pausable_completion_factory_name: str | None = None

    def __post_init__(self) -> None:
        self.host_module_path = self.host_module_path.expanduser().resolve()
        if not self.host_module_path.is_file():
            raise ModelProviderError("host_client_not_found", "host client module was not found")
        if (
            self.cancellable_completion_factory_name
            and self.pausable_completion_factory_name
        ):
            raise ModelProviderError(
                "host_control_factory_conflict",
                "configure exactly one host completion control factory",
            )
        self._module: ModuleType | None = None

    def capabilities(self) -> ModelCapabilities:
        return ModelCapabilities(
            structured_output=False,
            tool_calls=False,
            reasoning_tokens=True,
            actual_model_identity=True,
        )

    def probe(self) -> bool:
        try:
            module = self._host_module()
            client = self._call_factory(module, self.client_factory_name)
            deployment = self._deployment(module)
            response, _ = self._create_completion(
                module,
                client,
                deployment,
                messages=[
                    {"role": "system", "content": "Reply briefly."},
                    {"role": "user", "content": "Reply with OK."},
                ],
                max_output_tokens=max(16, int(os.getenv(PROBE_TOKENS_ENV, "64"))),
                use_json_mode=False,
            )
            return bool(getattr(response, "choices", None))
        except Exception:
            return False

    def invoke(self, request: ModelRequest) -> ModelResponse:
        return self._invoke(request)

    def invoke_cancellable(
        self,
        request: ModelRequest,
        cancellation: CancellationSignal,
    ) -> ModelResponse:
        cancellation.raise_if_cancelled()
        response = self._invoke(request, cancellation=cancellation)
        cancellation.raise_if_cancelled()
        return response

    def _invoke(
        self,
        request: ModelRequest,
        *,
        cancellation: CancellationSignal | None = None,
    ) -> ModelResponse:
        try:
            module = self._host_module()
            client = self._call_factory(module, self.client_factory_name)
            deployment = self._deployment(module)
            system_prompt = request.system_prompt
            if request.response_schema:
                schema = json.dumps(
                    request.response_schema,
                    separators=(",", ":"),
                    sort_keys=True,
                )
                schema_heading = "Required JSON Schema (return one JSON object only):"
                system_prompt = f"{system_prompt}\n\n{schema_heading}\n{schema}"
            response, request_metadata = self._create_completion(
                module,
                client,
                deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": request.user_prompt},
                ],
                max_output_tokens=request.max_output_tokens,
                use_json_mode=bool(request.response_schema) and self.json_mode,
                cancellation=cancellation,
            )
        except CancellationRequested:
            raise
        except ModelProviderError:
            raise
        except Exception as exc:
            raise ModelProviderError(
                "host_model_invoke_failed",
                f"host model invocation failed safely: {type(exc).__name__}",
            ) from None

        choice = response.choices[0] if getattr(response, "choices", None) else None
        message = getattr(choice, "message", None)
        content = _message_text(message)
        usage = getattr(response, "usage", None)
        completion_tokens = _non_negative_int(getattr(usage, "completion_tokens", None))
        details = getattr(usage, "completion_tokens_details", None)
        reasoning_tokens = _non_negative_int(getattr(details, "reasoning_tokens", None))
        structured = _try_json_object(content)
        actual_model = _optional_text(getattr(response, "model", None))
        finish_reason = _optional_text(getattr(choice, "finish_reason", None))
        diagnostics: dict[str, str | int | bool | None] = {
            "provider": "host_chat_completions",
            "requested_deployment": deployment,
            "visible_content_length": len(content),
            "token_parameter": request_metadata["token_parameter"],
            "json_mode_requested": request_metadata["json_mode_requested"],
            "json_mode_used": request_metadata["json_mode_used"],
            "cancellation_mode": request_metadata["cancellation_mode"],
        }
        return ModelResponse(
            content=content,
            structured=structured,
            actual_model=actual_model,
            finish_reason=finish_reason,
            completion_tokens=completion_tokens,
            reasoning_tokens=reasoning_tokens,
            safe_diagnostics=diagnostics,
        )

    def _host_module(self) -> ModuleType:
        if self._module is not None:
            return self._module
        module_name = f"_uca_host_client_{abs(hash(str(self.host_module_path)))}"
        spec = importlib.util.spec_from_file_location(module_name, self.host_module_path)
        if spec is None or spec.loader is None:
            raise ModelProviderError("host_client_load_failed", "host client module could not load")
        module = importlib.util.module_from_spec(spec)
        parent = str(self.host_module_path.parent)
        inserted = parent not in sys.path
        if inserted:
            sys.path.insert(0, parent)
        try:
            spec.loader.exec_module(module)
        except Exception as exc:
            raise ModelProviderError(
                "host_client_load_failed",
                f"host client module failed to load safely: {type(exc).__name__}",
            ) from None
        finally:
            if inserted and sys.path and sys.path[0] == parent:
                sys.path.pop(0)
        self._module = module
        return module

    @staticmethod
    def _call_factory(module: ModuleType, name: str) -> Any:
        factory = getattr(module, name, None)
        if not callable(factory):
            raise ModelProviderError("host_factory_missing", "required host factory is unavailable")
        return factory()

    def _deployment(self, module: ModuleType) -> str:
        config = self._call_factory(module, self.config_factory_name)
        if isinstance(config, dict):
            value = config.get(self.deployment_attribute)
        else:
            value = getattr(config, self.deployment_attribute, None)
        deployment = str(value or "").strip()
        if not deployment:
            raise ModelProviderError("host_deployment_missing", "host deployment is unavailable")
        return deployment

    def _create_completion(
        self,
        module: ModuleType,
        client: Any,
        deployment: str,
        *,
        messages: list[dict[str, str]],
        max_output_tokens: int,
        use_json_mode: bool,
        cancellation: CancellationSignal | None = None,
    ) -> tuple[Any, dict[str, str | bool]]:
        base: dict[str, Any] = {"model": deployment, "messages": messages}
        if use_json_mode:
            base["response_format"] = {"type": "json_object"}

        token_candidates = ("max_completion_tokens", "max_tokens")
        last_error: Exception | None = None
        for token_parameter in token_candidates:
            kwargs = dict(base)
            kwargs[token_parameter] = max_output_tokens
            try:
                response, cancellation_mode = self._call_completion(
                    module,
                    client,
                    kwargs,
                    cancellation=cancellation,
                )
                return response, {
                    "token_parameter": token_parameter,
                    "json_mode_requested": use_json_mode,
                    "json_mode_used": use_json_mode,
                    "cancellation_mode": cancellation_mode,
                }
            except (CancellationRequested, ModelProviderError):
                raise
            except Exception as exc:
                last_error = exc
                if not _looks_like_parameter_error(exc, token_parameter):
                    if use_json_mode and _looks_like_parameter_error(exc, "response_format"):
                        fallback = dict(kwargs)
                        fallback.pop("response_format", None)
                        try:
                            response, cancellation_mode = self._call_completion(
                                module,
                                client,
                                fallback,
                                cancellation=cancellation,
                            )
                            return response, {
                                "token_parameter": token_parameter,
                                "json_mode_requested": True,
                                "json_mode_used": False,
                                "cancellation_mode": cancellation_mode,
                            }
                        except (CancellationRequested, ModelProviderError):
                            raise
                        except Exception as fallback_exc:
                            last_error = fallback_exc
                    break
        if last_error is None:
            raise ModelProviderError("host_model_invoke_failed", "host model invocation failed")
        raise ModelProviderError(
            "host_model_invoke_failed",
            f"host model request failed safely: {type(last_error).__name__}",
        ) from None

    def _call_completion(
        self,
        module: ModuleType,
        client: Any,
        kwargs: dict[str, Any],
        *,
        cancellation: CancellationSignal | None,
    ) -> tuple[Any, str]:
        if cancellation is None:
            return client.chat.completions.create(**kwargs), "not_requested"

        cancellation.raise_if_cancelled()
        pausable_factory_name = self.pausable_completion_factory_name
        if pausable_factory_name:
            factory = getattr(module, pausable_factory_name, None)
            if not callable(factory):
                raise ModelProviderError(
                    "host_pausable_factory_missing",
                    "configured host pausable completion factory is unavailable",
                )

            def start_pausable_operation() -> _HostPausableCompletionHandle:
                value = factory(client=client, **kwargs)
                return _require_pausable_completion_handle(value)

            with cancellation.owned_pausable_operation(
                OwnedOperationKind.PROVIDER,
                start_pausable_operation,
            ) as operation:
                handle = cast(_HostPausableCompletionHandle, operation)
                response = _await_completion_handle(handle)
                return response, "owned_pausable_handle"

        factory_name = self.cancellable_completion_factory_name
        if not factory_name:
            response = client.chat.completions.create(**kwargs)
            cancellation.raise_if_cancelled()
            return response, "cooperative"

        factory = getattr(module, factory_name, None)
        if not callable(factory):
            raise ModelProviderError(
                "host_cancellable_factory_missing",
                "configured host cancellable completion factory is unavailable",
            )

        def start_operation() -> _HostCompletionHandle:
            value = factory(client=client, **kwargs)
            return _require_completion_handle(value)

        with cancellation.owned_cancellable_operation(
            OwnedOperationKind.PROVIDER,
            start_operation,
        ) as operation:
            handle = cast(_HostCompletionHandle, operation)
            response = _await_completion_handle(handle)
            return response, "owned_handle"


def create_provider() -> HostChatCompletionsProvider:
    path_value = os.getenv(HOST_CLIENT_PATH_ENV, "").strip()
    if not path_value:
        raise ModelProviderError(
            "host_client_path_missing",
            f"set {HOST_CLIENT_PATH_ENV} to the existing site-owned client module",
        )
    client_factory = os.getenv(CLIENT_FACTORY_ENV, "create_client").strip() or "create_client"
    config_factory = (
        os.getenv(CONFIG_FACTORY_ENV, "get_configured_model_or_deployment").strip()
        or "get_configured_model_or_deployment"
    )
    deployment_attribute = (
        os.getenv(DEPLOYMENT_ATTRIBUTE_ENV, "deployment").strip() or "deployment"
    )
    cancellable_factory = (
        os.getenv(CANCELLABLE_COMPLETION_FACTORY_ENV, "").strip() or None
    )
    pausable_factory = (
        os.getenv(PAUSABLE_COMPLETION_FACTORY_ENV, "").strip() or None
    )
    return HostChatCompletionsProvider(
        host_module_path=Path(path_value),
        client_factory_name=client_factory,
        config_factory_name=config_factory,
        deployment_attribute=deployment_attribute,
        json_mode=_truthy(os.getenv(JSON_MODE_ENV, "1")),
        cancellable_completion_factory_name=cancellable_factory,
        pausable_completion_factory_name=pausable_factory,
    )


def _message_text(message: Any) -> str:
    value = getattr(message, "content", "") if message is not None else ""
    if isinstance(value, str):
        return value
    if not isinstance(value, list):
        return ""
    parts: list[str] = []
    for item in value:
        if isinstance(item, dict):
            text = item.get("text")
        else:
            text = getattr(item, "text", None)
        if isinstance(text, str):
            parts.append(text)
    return "".join(parts)


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


def _looks_like_parameter_error(exc: Exception, parameter: str) -> bool:
    text = str(exc).lower()
    parameter_text = parameter.lower()
    return parameter_text in text and any(
        marker in text for marker in ("unsupported", "unknown", "unexpected", "invalid")
    )


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() not in {"", "0", "false", "no", "off"}


def _require_completion_handle(value: Any) -> _HostCompletionHandle:
    if not all(callable(getattr(value, name, None)) for name in ("result", "cancel", "done")):
        raise ModelProviderError(
            "host_cancellable_handle_invalid",
            "host cancellable completion factory returned an invalid handle",
        )
    return cast(_HostCompletionHandle, value)


def _require_pausable_completion_handle(value: Any) -> _HostPausableCompletionHandle:
    required = ("result", "cancel", "done", "pause", "resume", "paused")
    if not all(callable(getattr(value, name, None)) for name in required):
        _cancel_handle(cast(_HostCompletionHandle, value))
        raise ModelProviderError(
            "host_pausable_handle_invalid",
            "host pausable completion factory returned an invalid handle",
        )
    return cast(_HostPausableCompletionHandle, value)


def _await_completion_handle(handle: _HostCompletionHandle) -> Any:
    completed = False
    try:
        response = handle.result()
        completed = _handle_done(handle)
    finally:
        if not _handle_done(handle):
            _cancel_handle(handle)
    if not completed:
        raise ModelProviderError(
            "host_cancellable_handle_incomplete",
            "host completion handle returned before termination",
        )
    return response


def _handle_done(handle: _HostCompletionHandle) -> bool:
    try:
        return bool(handle.done())
    except Exception:
        return False


def _cancel_handle(handle: _HostCompletionHandle) -> None:
    try:
        handle.cancel()
    except Exception:
        return
