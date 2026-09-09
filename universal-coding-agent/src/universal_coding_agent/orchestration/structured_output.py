from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ValidationError

from universal_coding_agent.core.cancellation import (
    CancellationRequested,
    CancellationSignal,
    OwnedOperationKind,
)
from universal_coding_agent.core.models import ModelRequest, ModelResponse
from universal_coding_agent.providers.base import (
    CancellableModelProvider,
    ModelProvider,
    ModelProviderError,
)
from universal_coding_agent.safety.sanitizer import sanitize_text

_ModelT = TypeVar("_ModelT", bound=BaseModel)

_TRUNCATION_FINISH_REASONS = frozenset(
    {
        "length",
        "max_tokens",
        "max_output_tokens",
        "token_limit",
    }
)
_MAX_MODEL_OUTPUT_TOKENS = 32_000


class StructuredOutputError(RuntimeError):
    """Safe failure raised after bounded structured-output recovery is exhausted."""

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
    max_budget_retries: int = 1,
    cancellation: CancellationSignal | None = None,
) -> StructuredOutputResult[_ModelT]:
    """Invoke one role with bounded output-budget retry and schema repair.

    Output truncation is not a schema defect. When the provider explicitly reports
    a length/token-limit finish reason, retry the same logical request once with a
    doubled server-controlled output budget before attempting any schema repair.
    Schema repair remains separately bounded and is used only for complete model
    responses that fail JSON/schema validation.
    """

    if max_repair_attempts < 0 or max_repair_attempts > 2:
        raise ValueError("max_repair_attempts must be between 0 and 2")
    if max_budget_retries < 0 or max_budget_retries > 2:
        raise ValueError("max_budget_retries must be between 0 and 2")

    attempts: list[dict[str, Any]] = []
    current_request = request
    original_role = request.role
    repair_attempts_used = 0
    budget_retries_used = 0

    while True:
        attempt_index = len(attempts)
        response = _invoke_provider(
            provider,
            current_request,
            attempt_index,
            cancellation=cancellation,
        )
        raw_output = _raw_output(response)

        if _output_was_truncated(response):
            issue = _truncation_issue(response, current_request)
            attempts.append(
                _attempt_diagnostics(
                    attempt_index,
                    response,
                    raw_output,
                    issue,
                    failure_kind="output_budget_exhausted",
                )
            )
            if budget_retries_used >= max_budget_retries:
                raise StructuredOutputError(
                    "model_output_budget_exhausted",
                    {
                        "role": original_role,
                        "repair_used": repair_attempts_used > 0,
                        "budget_retry_used": budget_retries_used > 0,
                        "attempts": attempts,
                    },
                )
            next_budget = min(
                current_request.max_output_tokens * 2,
                _MAX_MODEL_OUTPUT_TOKENS,
            )
            if next_budget <= current_request.max_output_tokens:
                raise StructuredOutputError(
                    "model_output_budget_exhausted",
                    {
                        "role": original_role,
                        "repair_used": repair_attempts_used > 0,
                        "budget_retry_used": budget_retries_used > 0,
                        "attempts": attempts,
                    },
                )
            budget_retries_used += 1
            current_request = _budget_retry_request(
                current_request,
                next_budget=next_budget,
                budget_retry=budget_retries_used,
            )
            continue

        try:
            payload = _single_json_object(response)
            value = model_type.model_validate(payload)
        except (ValidationError, ValueError, TypeError) as exc:
            issue = _validation_issue(exc)
            attempts.append(
                _attempt_diagnostics(
                    attempt_index,
                    response,
                    raw_output,
                    issue,
                    failure_kind="schema_invalid",
                )
            )
            if repair_attempts_used >= max_repair_attempts:
                raise StructuredOutputError(
                    "model_schema_invalid",
                    {
                        "role": original_role,
                        "repair_used": repair_attempts_used > 0,
                        "budget_retry_used": budget_retries_used > 0,
                        "attempts": attempts,
                    },
                ) from exc
            repair_attempts_used += 1
            current_request = _repair_request(
                current_request,
                raw_output=raw_output,
                validation_issue=issue,
                schema=model_type.model_json_schema(),
                repair_guidance=repair_guidance,
                repair_attempt=repair_attempts_used,
            )
            continue

        attempts.append(
            _attempt_diagnostics(
                attempt_index,
                response,
                raw_output,
                None,
                failure_kind=None,
            )
        )
        return StructuredOutputResult(
            value=value,
            repair_used=repair_attempts_used > 0,
            diagnostics={
                "role": original_role,
                "repair_used": repair_attempts_used > 0,
                "budget_retry_used": budget_retries_used > 0,
                "attempts": attempts,
            },
        )


def _invoke_provider(
    provider: ModelProvider,
    request: ModelRequest,
    attempt_index: int,
    *,
    cancellation: CancellationSignal | None = None,
) -> ModelResponse:
    try:
        if cancellation is None:
            return provider.invoke(request)
        with cancellation.operation(OwnedOperationKind.PROVIDER):
            if isinstance(provider, CancellableModelProvider):
                return provider.invoke_cancellable(request, cancellation)
            return provider.invoke(request)
    except CancellationRequested as exc:
        raise StructuredOutputError(
            "control_cancelled",
            {
                "role": request.role,
                "repair_used": request.metadata.get("schema_repair") == "true",
                "budget_retry_used": request.metadata.get("output_budget_retry") == "true",
                "stage": "provider_invoke",
                "error_type": type(exc).__name__,
            },
        ) from exc
    except ModelProviderError as exc:
        raise StructuredOutputError(
            exc.code,
            {
                "role": request.role,
                "repair_used": request.metadata.get("schema_repair") == "true",
                "budget_retry_used": request.metadata.get("output_budget_retry") == "true",
                "stage": "provider_invoke",
                "error_type": type(exc).__name__,
            },
        ) from exc
    except Exception as exc:
        raise StructuredOutputError(
            "model_provider_failed",
            {
                "role": request.role,
                "repair_used": request.metadata.get("schema_repair") == "true",
                "budget_retry_used": request.metadata.get("output_budget_retry") == "true",
                "stage": "provider_invoke",
                "error_type": type(exc).__name__,
            },
        ) from exc


def _output_was_truncated(response: ModelResponse) -> bool:
    reason = (response.finish_reason or "").strip().lower()
    return reason in _TRUNCATION_FINISH_REASONS


def _truncation_issue(response: ModelResponse, request: ModelRequest) -> str:
    reason = (response.finish_reason or "unknown").strip()
    completion_tokens = response.completion_tokens
    return sanitize_text(
        "model output was truncated before JSON validation "
        f"(finish_reason={reason}, completion_tokens={completion_tokens}, "
        f"requested_max_output_tokens={request.max_output_tokens})"
    )


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
            default=str,
        )
    return response.content


def _validation_issue(exc: Exception) -> str:
    if isinstance(exc, ValidationError):
        value: Any = exc.errors(include_url=False, include_input=False)
        text = json.dumps(
            value,
            ensure_ascii=False,
            separators=(",", ":"),
            default=str,
        )
    else:
        text = f"{type(exc).__name__}: {exc}"
    return sanitize_text(text)[:12_000]


def _attempt_diagnostics(
    attempt_index: int,
    response: ModelResponse,
    raw_output: str,
    validation_issue: str | None,
    *,
    failure_kind: str | None,
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
    if failure_kind is not None:
        diagnostics["failure_kind"] = failure_kind
    if validation_issue is not None:
        diagnostics["validation_issue"] = validation_issue
    return diagnostics


def _budget_retry_request(
    current: ModelRequest,
    *,
    next_budget: int,
    budget_retry: int,
) -> ModelRequest:
    metadata = dict(current.metadata)
    metadata.update(
        {
            "output_budget_retry": "true",
            "output_budget_retry_attempt": str(budget_retry),
            "previous_max_output_tokens": str(current.max_output_tokens),
        }
    )
    return ModelRequest(
        role=current.role,
        system_prompt=current.system_prompt,
        user_prompt=current.user_prompt,
        response_schema=current.response_schema,
        max_output_tokens=next_budget,
        metadata=metadata,
    )


def _repair_request(
    original: ModelRequest,
    *,
    raw_output: str,
    validation_issue: str,
    schema: dict[str, Any],
    repair_guidance: str,
    repair_attempt: int,
) -> ModelRequest:
    schema_text = json.dumps(
        schema,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
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
