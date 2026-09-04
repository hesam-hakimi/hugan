from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any

_PROBE_SENTINEL = "UCA_HOST_PROVIDER_OK"


def invoke_text(prompt: str, max_output_tokens: int = 8) -> str:
    del prompt, max_output_tokens
    return _PROBE_SENTINEL


class _Completions:
    def create(self, **kwargs: Any) -> Any:
        messages = kwargs.get("messages") or []
        system_prompt = "\n".join(
            str(item.get("content") or "")
            for item in messages
            if isinstance(item, dict) and item.get("role") == "system"
        ).lower()

        if "bounded code implementer" in system_prompt:
            payload: dict[str, Any] = {
                "summary": "Change the approved fixture constant from 42 to 43.",
                "edits": [
                    {
                        "path": "app.py",
                        "operation": "modify",
                        "replacements": [
                            {
                                "old_text": "RETURN_VALUE = 42",
                                "new_text": "RETURN_VALUE = 43",
                            }
                        ],
                        "content": None,
                    }
                ],
                "requested_test_profiles": ["python-check"],
                "assumptions": [],
            }
        elif "independent safe mode reviewer" in system_prompt:
            payload = {
                "verdict": "PASS",
                "requirement_findings": [
                    "The approved one-line fixture change is implemented exactly."
                ],
                "scope_findings": ["Only app.py changed inside the approved sandbox."],
                "security_findings": ["No publication or out-of-scope action occurred."],
                "test_findings": ["The approved focused test profile passed."],
                "required_actions": [],
                "confidence": "high",
            }
        else:
            payload = {"status": "OK"}

        content = json.dumps(payload, separators=(",", ":"), sort_keys=True)
        return SimpleNamespace(
            model="ci-host-safe-model",
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content=content),
                    finish_reason="stop",
                )
            ],
            usage=SimpleNamespace(
                completion_tokens=max(1, len(content) // 4),
                completion_tokens_details=SimpleNamespace(reasoning_tokens=0),
            ),
        )


class _Client:
    def __init__(self) -> None:
        self.chat = SimpleNamespace(completions=_Completions())


def create_client() -> _Client:
    return _Client()


def get_configured_model_or_deployment() -> Any:
    return SimpleNamespace(deployment="ci-host-safe-deployment")
