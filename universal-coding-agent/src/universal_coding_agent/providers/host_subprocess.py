from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

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

    def __post_init__(self) -> None:
        self.host_module_path = Path(self.host_module_path).expanduser().resolve()
        self.host_python = Path(self.host_python).expanduser().resolve()
        if not self.host_module_path.is_file():
            raise ModelProviderError("host_client_not_found", "host client module was not found")
        if not self.host_python.is_file():
            raise ModelProviderError(
                "host_python_not_found",
                "host Python interpreter was not found",
            )

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
        invoke_function_name=os.getenv(INVOKE_FUNCTION_ENV, "invoke_text").strip()
        or "invoke_text",
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
    )


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
