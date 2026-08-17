from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ValidationError

from universal_coding_agent.core.models import ModelRequest, ModelResponse
from universal_coding_agent.providers.base import ModelProvider, ModelProviderError
from universal_coding_agent.safety.sanitizer import sanitize_text

_ModelT = TypeVar("_ModelT", bound=BaseModel)


class StructuredOutputError(RuntimeError):
    """Safe failure raised after bounded structured-output repair is exhausted."""

    def __init__(self, code: str, diagnostics: dict[str, Any]):
        self.code = code
        self.diagnostics = diagnostics
        super().__init__(code)


@dataclass(frozen=True)
class StructuredOutputResult(Generic[_ModelT]):
    value: _ModelT
    repair_used: bool
    diagnostics: dict[str, Any]


def invoke_structured(
    provider: ModelProvider,
    request: ModelRequest,
    model_type: type[_ModelT],
    *,
    repair_guidance: str = "",
    max_repair_attempts: int = 1,
) -> StructuredOutputResult[_ModelT]:
    """Invoke one role and perform at most one schema-only correction round."""

    if max_repair_attempts < 0 or max_repair_attempts > 2:
        raise ValueError("max_repair_attempts must be between 0 and 2")

    attempts: list[dict[str, Any]] = []
    current_request = request
    original_role = request.role

    for attempt_index in range(max_repair_attempts + 1):
        response = _invoke_provider(provider, current_request, attempt_index)
        raw_output = _raw_output(response)
        try:
            payload = _single_json_object(response)
            value = model_type.model_validate(payload)
        except (ValidationError, ValueError, TypeError, json.JSONDecodeError) as exc:
            issue = _validation_issue(exc)
            attempts.append(_attempt_diagnostics(attempt_index, response, raw_output, issue))
            if attempt_index >= max_repair_attempts:
                raise StructuredOutputError(
                    "model_schema_invalid",
                    {
                        "role": original_role,
                        "repair_used": attempt_index > 0,
                        "attempts": attempts,
                    },
                ) from exc
            current_request = _repair_request(
                request,
                raw_output=raw_output,
                validation_issue=issue,
                schema=model_type.model_json_schema(),
                repair_guidance=repair_guidance,
                repair_attempt=attempt_index + 1,
            )
            continue

        attempts.append(_attempt_diagnostics(attempt_index, response, raw_output, None))
        return StructuredOutputResult(
            value=value,
            repair_used=attempt_index > 0,
            diagnostics={
                "role": original_role,
                "repair_used": attempt_index > 0,
                "attempts": attempts,
            },
        )

    raise AssertionError("structured-output loop terminated unexpectedly")


def _invoke_provider(
    provider: ModelProvider,
    request: ModelRequest,
    attempt_index: int,
) -> ModelResponse:
    try:
        return provider.invoke(request)
    except ModelProviderError as exc:
        raise StructuredOutputError(
            exc.code,
            {
                "role": request.role,
                "repair_used": attempt_index > 0,
                "stage": "provider_invoke",
                "error_type": type(exc).__name__,
            },
        ) from exc
    except Exception as exc:
        raise StructuredOutputError(
            "model_provider_failed",
            {
                "role": request.role,
                "repair_used": attempt_index > 0,
                "stage": "provider_invoke",
                "error_type": type(exc).__name__,
            },
        ) from exc


def _single_json_object(response: ModelResponse) -> dict[str, Any]:
    if response.structured is not None:
        if not isinstance(response.structured, dict):
            raise ValueError("structured model output must be one JSON object")
        return response.structured

    text = response.content.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3 and lines[-1].strip() == "```":
            text = "\n".join(lines[1:-1])
            if text.lstrip().startswith("json"):
                text = text.lstrip()[4:].lstrip("\n")

    decoder = json.JSONDecoder()
    payload, end = decoder.raw_decode(text.lstrip())
    if text.lstrip()[end:].strip():
        raise ValueError("model returned trailing content after the JSON object")
    if not isinstance(payload, dict):
        raise ValueError("model output must be one JSON object")
    return payload


def _raw_output(response: ModelResponse) -> str:
    if response.structured is not None:
        return json.dumps(
            response.structured,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
    return response.content


def _validation_issue(exc: Exception) -> str:
    if isinstance(exc, ValidationError):
        value: Any = exc.errors(include_url=False, include_input=False)
        text = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    else:
        text = f"{type(exc).__name__}: {exc}"
    return sanitize_text(text)[:12_000]


def _attempt_diagnostics(
    attempt_index: int,
    response: ModelResponse,
    raw_output: str,
    validation_issue: str | None,
) -> dict[str, Any]:
    diagnostics: dict[str, Any] = {
        "attempt": attempt_index + 1,
        "actual_model": response.actual_model,
        "finish_reason": response.finish_reason,
        "completion_tokens": response.completion_tokens,
        "reasoning_tokens": response.reasoning_tokens,
        "output_chars": len(raw_output),
        "output_sha256": hashlib.sha256(raw_output.encode("utf-8")).hexdigest(),
        "schema_valid": validation_issue is None,
    }
    if validation_issue is not None:
        diagnostics["validation_issue"] = validation_issue
    return diagnostics


def _repair_request(
    original: ModelRequest,
    *,
    raw_output: str,
    validation_issue: str,
    schema: dict[str, Any],
    repair_guidance: str,
    repair_attempt: int,
) -> ModelRequest:
    schema_text = json.dumps(schema, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    guidance = repair_guidance.strip()
    user_prompt = (
        "Correct the JSON object below so that it satisfies the supplied JSON Schema.\n"
        "Preserve the original facts, evidence, scope, identifiers, and intent.\n"
        "Do not invent new evidence or silently remove unresolved prerequisites.\n"
        "Return exactly one corrected JSON object and no Markdown.\n\n"
        f"Validation issue:\n{validation_issue}\n\n"
    )
    if guidance:
        user_prompt += f"Role-specific correction rules:\n{guidance}\n\n"
    user_prompt += f"JSON Schema:\n{schema_text}\n\nOriginal JSON output:\n{raw_output}"

    metadata = dict(original.metadata)
    metadata.update(
        {
            "schema_repair": "true",
            "repair_attempt": str(repair_attempt),
            "repair_for_role": original.role,
        }
    )
    return ModelRequest(
        role=original.role,
        system_prompt=(
            "You are a deterministic JSON contract repairer. Correct structure and types only. "
            "Return exactly one JSON object matching the supplied schema."
        ),
        user_prompt=user_prompt,
        response_schema=schema,
        max_output_tokens=original.max_output_tokens,
        metadata=metadata,
    )
