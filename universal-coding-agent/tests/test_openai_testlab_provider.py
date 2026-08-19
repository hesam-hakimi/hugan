from __future__ import annotations

import pytest

from universal_coding_agent.core.models import ModelRequest
from universal_coding_agent.providers.base import ModelProviderError
from universal_coding_agent.testlab.openai_responses import OpenAIResponsesProvider


def test_openai_testlab_provider_uses_responses_structured_output() -> None:
    captured = {}

    def transport(payload):
        captured.update(payload)
        return {
            "id": "resp_test",
            "status": "completed",
            "model": "test-model-resolved",
            "output": [
                {
                    "type": "message",
                    "content": [
                        {
                            "type": "output_text",
                            "text": '{"answer":43}',
                        }
                    ],
                }
            ],
            "usage": {
                "output_tokens": 12,
                "output_tokens_details": {"reasoning_tokens": 3},
            },
        }

    provider = OpenAIResponsesProvider(
        api_key="test-key",
        model="test-model",
        transport=transport,
    )
    response = provider.invoke(
        ModelRequest(
            role="implementer",
            system_prompt="Return structured output.",
            user_prompt="Return answer 43.",
            response_schema={
                "type": "object",
                "properties": {"answer": {"type": "integer"}},
                "required": ["answer"],
                "additionalProperties": False,
            },
            max_output_tokens=512,
        )
    )

    assert captured["model"] == "test-model"
    assert captured["store"] is False
    assert captured["text"]["format"]["type"] == "json_schema"
    assert captured["text"]["format"]["strict"] is True
    assert response.structured == {"answer": 43}
    assert response.actual_model == "test-model-resolved"
    assert response.completion_tokens == 12
    assert response.reasoning_tokens == 3
    assert response.safe_diagnostics["response_id"] == "resp_test"


def test_openai_testlab_provider_requires_environment_configuration(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("UCA_OPENAI_MODEL", raising=False)

    with pytest.raises(ModelProviderError) as exc_info:
        OpenAIResponsesProvider.from_env()

    assert exc_info.value.code == "openai_configuration_missing"


def test_openai_testlab_provider_rejects_non_json_structured_output() -> None:
    def transport(_payload):
        return {
            "id": "resp_invalid",
            "status": "completed",
            "model": "test-model",
            "output": [
                {
                    "type": "message",
                    "content": [{"type": "output_text", "text": "not-json"}],
                }
            ],
        }

    provider = OpenAIResponsesProvider(
        api_key="test-key",
        model="test-model",
        transport=transport,
    )

    with pytest.raises(ModelProviderError) as exc_info:
        provider.invoke(
            ModelRequest(
                role="reviewer",
                system_prompt="Return structured output.",
                user_prompt="Review.",
                response_schema={"type": "object"},
            )
        )

    assert exc_info.value.code == "openai_invalid_structured_output"
