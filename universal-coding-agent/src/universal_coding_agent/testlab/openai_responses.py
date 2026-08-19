from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from collections.abc import Callable
from typing import Any

from universal_coding_agent.core.models import (
    ModelCapabilities,
    ModelRequest,
    ModelResponse,
)
from universal_coding_agent.providers.base import ModelProviderError
from universal_coding_agent.safety.sanitizer import sanitize_text

Transport = Callable[[dict[str, Any]], dict[str, Any]]
_SCHEMA_NAME = re.compile(r"[^A-Za-z0-9_-]+")


class OpenAIResponsesProvider:
    """Opt-in OpenAI Responses API provider used only by the pre-transfer test lab."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        endpoint: str = "https://api.openai.com/v1/responses",
        timeout_seconds: int = 180,
        transport: Transport | None = None,
    ) -> None:
        api_key = api_key.strip()
        model = model.strip()
        if not api_key:
            raise ValueError("api_key must not be empty")
        if not model:
            raise ValueError("model must not be empty")
        self.api_key = api_key
        self.model = model
        self.endpoint = endpoint
        self.timeout_seconds = timeout_seconds
        self._transport = transport

    @classmethod
    def from_env(cls) -> OpenAIResponsesProvider:
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
        return cls(api_key=api_key, model=model)

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
                    "schema": request.response_schema,
                    "strict": True,
                }
            }

        data = self._send(payload)
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
        return ModelResponse(
            content=output_text,
            structured=structured,
            actual_model=str(data.get("model") or self.model),
            finish_reason=finish_reason,
            completion_tokens=_optional_nonnegative_int(usage.get("output_tokens")),
            reasoning_tokens=_optional_nonnegative_int(output_details.get("reasoning_tokens")),
            safe_diagnostics={
                "provider": "openai_responses",
                "response_id": response_id,
                "store": False,
            },
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

        request = urllib.request.Request(
            self.endpoint,
            data=json.dumps(payload, separators=(",", ":")).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
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
