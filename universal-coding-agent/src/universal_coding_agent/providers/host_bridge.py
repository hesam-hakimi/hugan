from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

_SAFE_RUNTIME_ERROR_CODES = {
    "host_bridge_request_invalid",
    "host_bridge_unknown_action",
    "host_client_load_failed",
    "host_client_not_found",
    "host_deployment_missing",
    "host_factory_missing",
    "host_model_invoke_failed",
}


def _load_module(path: Path) -> ModuleType:
    module_name = f"_uca_host_bridge_{abs(hash(str(path)))}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("host_client_load_failed")
    module = importlib.util.module_from_spec(spec)
    parent = str(path.parent)
    if parent not in sys.path:
        sys.path.insert(0, parent)
    spec.loader.exec_module(module)
    return module


def _call_factory(module: ModuleType, name: str) -> Any:
    factory = getattr(module, name, None)
    if not callable(factory):
        raise RuntimeError("host_factory_missing")
    return factory()


def _deployment(module: ModuleType, request: dict[str, Any]) -> str:
    config = _call_factory(module, str(request["config_factory"]))
    attribute = str(request["deployment_attribute"])
    value = config.get(attribute) if isinstance(config, dict) else getattr(config, attribute, None)
    deployment = str(value or "").strip()
    if not deployment:
        raise RuntimeError("host_deployment_missing")
    return deployment


def _looks_like_parameter_error(exc: Exception, parameter: str) -> bool:
    text = str(exc).lower()
    parameter_text = parameter.lower()
    return parameter_text in text and any(
        marker in text for marker in ("unsupported", "unknown", "unexpected", "invalid")
    )


def _create_completion(
    client: Any,
    deployment: str,
    *,
    messages: list[dict[str, str]],
    max_output_tokens: int,
    use_json_mode: bool,
) -> tuple[Any, dict[str, str | bool]]:
    create = client.chat.completions.create
    base: dict[str, Any] = {"model": deployment, "messages": messages}
    if use_json_mode:
        base["response_format"] = {"type": "json_object"}

    last_error: Exception | None = None
    for token_parameter in ("max_completion_tokens", "max_tokens"):
        kwargs = dict(base)
        kwargs[token_parameter] = max_output_tokens
        try:
            return create(**kwargs), {
                "token_parameter": token_parameter,
                "json_mode_requested": use_json_mode,
                "json_mode_used": use_json_mode,
            }
        except Exception as exc:
            last_error = exc
            if _looks_like_parameter_error(exc, token_parameter):
                continue
            if use_json_mode and _looks_like_parameter_error(exc, "response_format"):
                fallback = dict(kwargs)
                fallback.pop("response_format", None)
                try:
                    return create(**fallback), {
                        "token_parameter": token_parameter,
                        "json_mode_requested": True,
                        "json_mode_used": False,
                    }
                except Exception as fallback_exc:
                    last_error = fallback_exc
            break
    if last_error is None:
        raise RuntimeError("host_model_invoke_failed")
    raise RuntimeError("host_model_invoke_failed") from last_error


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


def _run(request: dict[str, Any]) -> dict[str, Any]:
    path = Path(str(request["host_client_path"])).expanduser().resolve()
    if not path.is_file():
        raise RuntimeError("host_client_not_found")
    module = _load_module(path)
    client = _call_factory(module, str(request["client_factory"]))
    deployment = _deployment(module, request)

    action = str(request.get("action", ""))
    if action == "probe":
        messages = [
            {"role": "system", "content": "Reply briefly."},
            {"role": "user", "content": "Reply with OK."},
        ]
        max_output_tokens = int(request.get("max_output_tokens", 64))
        use_json_mode = False
    elif action == "invoke":
        system_prompt = str(request.get("system_prompt", ""))
        response_schema = request.get("response_schema")
        if isinstance(response_schema, dict):
            schema = json.dumps(response_schema, separators=(",", ":"), sort_keys=True)
            system_prompt += (
                "\n\nRequired JSON Schema (return one JSON object only):\n" + schema
            )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": str(request.get("user_prompt", ""))},
        ]
        max_output_tokens = int(request.get("max_output_tokens", 2400))
        use_json_mode = bool(response_schema) and bool(request.get("json_mode", True))
    else:
        raise RuntimeError("host_bridge_unknown_action")

    response, metadata = _create_completion(
        client,
        deployment,
        messages=messages,
        max_output_tokens=max_output_tokens,
        use_json_mode=use_json_mode,
    )
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
            "requested_deployment": deployment,
            "visible_content_length": len(content),
            **metadata,
        },
    }


def _safe_error_code(exc: Exception) -> str:
    if isinstance(exc, RuntimeError):
        code = str(exc).strip()
        if code in _SAFE_RUNTIME_ERROR_CODES:
            return code
    return "host_bridge_failed"


def main() -> int:
    try:
        request = json.loads(sys.stdin.read())
        if not isinstance(request, dict):
            raise RuntimeError("host_bridge_request_invalid")
        payload = _run(request)
    except Exception as exc:
        payload = {
            "ok": False,
            "error_code": _safe_error_code(exc),
            "error_type": type(exc).__name__,
        }
    sys.stdout.write(json.dumps(payload, separators=(",", ":")))
    sys.stdout.write("\n")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
