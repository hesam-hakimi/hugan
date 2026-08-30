from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

import pytest

from universal_coding_agent.core.cancellation import CancellationCoordinator
from universal_coding_agent.core.models import ModelRequest
from universal_coding_agent.core.safe_models import StructuredEditProposal
from universal_coding_agent.product.remote_operations import (
    SqliteRemoteOperationLeaseStore,
)
from universal_coding_agent.providers.base import ModelProviderError
from universal_coding_agent.testlab.live import _provider_preflight
from universal_coding_agent.testlab.openai_responses import (
    OPENAI_BACKGROUND_CANCELLATION_ENV,
    OpenAIBackgroundLifecycleRecorder,
    OpenAIResponsesProvider,
    _openai_strict_schema,
)


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
        background_cancellation=True,
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
    assert "background" not in captured
    assert captured["text"]["format"]["type"] == "json_schema"
    assert captured["text"]["format"]["strict"] is True
    assert response.structured == {"answer": 43}
    assert response.actual_model == "test-model-resolved"
    assert response.completion_tokens == 12
    assert response.reasoning_tokens == 3
    assert response.safe_diagnostics["response_ref"] == (
        "sha256:" + hashlib.sha256(b"resp_test").hexdigest()
    )
    assert "response_id" not in response.safe_diagnostics


def test_openai_strict_schema_requires_every_object_property_recursively() -> None:
    lowered = _openai_strict_schema(StructuredEditProposal.model_json_schema())

    assert lowered["required"] == list(lowered["properties"])
    assert lowered["additionalProperties"] is False
    file_edit = lowered["$defs"]["FileEdit"]
    replacement = lowered["$defs"]["TextReplacement"]
    assert file_edit["required"] == list(file_edit["properties"])
    assert replacement["required"] == list(replacement["properties"])
    assert file_edit["additionalProperties"] is False
    assert replacement["additionalProperties"] is False


def test_openai_strict_schema_removes_generation_unsupported_constraints() -> None:
    lowered = _openai_strict_schema(
        {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "default": "fixture",
                    "minLength": 1,
                    "maxLength": 20,
                    "pattern": "^[a-z]+$",
                },
                "items": {
                    "type": "array",
                    "default": [],
                    "minItems": 0,
                    "maxItems": 3,
                    "items": {"type": "integer", "minimum": 0},
                },
            },
            "required": ["name"],
        }
    )

    assert lowered["required"] == ["name", "items"]
    assert lowered["additionalProperties"] is False
    assert lowered["properties"]["name"] == {"type": "string"}
    assert lowered["properties"]["items"] == {
        "type": "array",
        "items": {"type": "integer"},
    }


def test_openai_testlab_provider_requires_environment_configuration(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("UCA_OPENAI_MODEL", raising=False)

    with pytest.raises(ModelProviderError) as exc_info:
        OpenAIResponsesProvider.from_env()

    assert exc_info.value.code == "openai_configuration_missing"


def test_openai_testlab_provider_reads_background_cancellation_opt_in(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("UCA_OPENAI_MODEL", "test-model")
    monkeypatch.setenv(OPENAI_BACKGROUND_CANCELLATION_ENV, "true")

    recorder = OpenAIBackgroundLifecycleRecorder()
    provider = OpenAIResponsesProvider.from_env(
        timeout_seconds=9,
        background_lifecycle_recorder=recorder,
    )

    assert provider.background_cancellation is True
    assert provider.timeout_seconds == 9
    assert provider.background_lifecycle_recorder is recorder


def test_openai_testlab_provider_rejects_ambiguous_background_opt_in(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("UCA_OPENAI_MODEL", "test-model")
    monkeypatch.setenv(OPENAI_BACKGROUND_CANCELLATION_ENV, "tru")

    with pytest.raises(ModelProviderError) as exc_info:
        OpenAIResponsesProvider.from_env()

    assert exc_info.value.code == "openai_configuration_invalid"


def test_openai_cancellable_invoke_is_cooperative_without_opt_in() -> None:
    captured = {}

    def transport(payload):
        captured.update(payload)
        return {
            "id": "resp_cooperative",
            "status": "completed",
            "model": "test-model",
            "output": [
                {
                    "type": "message",
                    "content": [{"type": "output_text", "text": "done"}],
                }
            ],
        }

    provider = OpenAIResponsesProvider(
        api_key="test-key",
        model="test-model",
        transport=transport,
    )
    signal = CancellationCoordinator().signal("openai-cooperative")

    response = provider.invoke_cancellable(
        ModelRequest(
            role="implementer",
            system_prompt="Return text.",
            user_prompt="Return done.",
        ),
        signal,
    )

    assert "background" not in captured
    assert response.safe_diagnostics["cancellation_mode"] == "cooperative"


def test_openai_background_handle_completes_through_remote_lifecycle(
    tmp_path: Path,
    monkeypatch,
) -> None:
    calls = []
    provider = OpenAIResponsesProvider(
        api_key="test-key",
        model="test-model",
        endpoint="https://example.test/v1/responses",
        background_cancellation=True,
    )
    store = _bind_private_store(provider, tmp_path)

    def request_json(*, method, endpoint, payload=None, timeout_seconds=None):
        calls.append((method, endpoint, dict(payload or {})))
        if method == "POST" and endpoint == provider.endpoint:
            return {
                "id": "resp_background",
                "status": "queued",
                "model": "test-model",
            }
        if method == "GET" and endpoint.endswith("/resp_background"):
            return {
                "id": "resp_background",
                "status": "completed",
                "model": "test-model-resolved",
                "output": [
                    {
                        "type": "message",
                        "content": [{"type": "output_text", "text": "done"}],
                    }
                ],
            }
        raise AssertionError(f"unexpected lifecycle request: {method} {endpoint}")

    monkeypatch.setattr(provider, "_request_json", request_json)
    monkeypatch.setattr(
        "universal_coding_agent.testlab.openai_responses._BACKGROUND_POLL_INTERVAL_SECONDS",
        0.001,
    )
    signal = CancellationCoordinator().signal("openai-background-completion")

    response = provider.invoke_cancellable(
        ModelRequest(
            role="implementer",
            system_prompt="Return text.",
            user_prompt="Return done.",
            metadata={
                "task_id": "openai-background-completion",
                "base_sha": "a" * 40,
            },
        ),
        signal,
    )

    assert calls[0][0:2] == ("POST", provider.endpoint)
    assert calls[0][2]["background"] is True
    assert calls[0][2]["store"] is False
    assert calls[1][0] == "GET"
    assert response.content == "done"
    assert response.safe_diagnostics["cancellation_mode"] == "owned_background_handle"
    assert response.safe_diagnostics["background"] is True
    assert response.safe_diagnostics["temporary_background_retention"] is True
    snapshot = store.public_snapshot("openai-background-completion")
    assert snapshot is not None
    assert snapshot.state.value == "terminal"
    assert snapshot.last_status == "completed"
    assert snapshot.base_sha == "a" * 40
    assert "resp_background" not in json.dumps(snapshot.model_dump(mode="json"))
    store.close()


def test_openai_background_handle_fails_closed_for_unknown_remote_state(
    tmp_path: Path,
    monkeypatch,
) -> None:
    provider = OpenAIResponsesProvider(
        api_key="test-key",
        model="test-model",
        background_cancellation=True,
    )
    store = _bind_private_store(provider, tmp_path)

    def request_json(*, method, endpoint, payload=None, timeout_seconds=None):
        return {
            "id": "resp_unknown",
            "status": "unknown",
            "model": "test-model",
        }

    monkeypatch.setattr(provider, "_request_json", request_json)
    signal = CancellationCoordinator().signal("openai-background-unknown")

    with pytest.raises(ModelProviderError) as exc_info:
        provider.invoke_cancellable(
            ModelRequest(
                role="implementer",
                system_prompt="Return text.",
                user_prompt="Return done.",
            ),
            signal,
        )

    assert exc_info.value.code == "openai_background_state_unconfirmed"
    snapshot = store.public_snapshot("openai-background-unknown")
    assert snapshot is not None
    assert snapshot.state.value == "unavailable"
    store.close()


def test_openai_background_handle_fails_closed_for_response_id_drift(
    tmp_path: Path,
    monkeypatch,
) -> None:
    provider = OpenAIResponsesProvider(
        api_key="test-key",
        model="test-model",
        background_cancellation=True,
    )
    store = _bind_private_store(provider, tmp_path)

    def request_json(*, method, endpoint, payload=None, timeout_seconds=None):
        if method == "POST":
            return {
                "id": "resp_expected",
                "status": "queued",
                "model": "test-model",
            }
        return {
            "id": "resp_different",
            "status": "completed",
            "model": "test-model",
            "output": [],
        }

    monkeypatch.setattr(provider, "_request_json", request_json)
    monkeypatch.setattr(
        "universal_coding_agent.testlab.openai_responses._BACKGROUND_POLL_INTERVAL_SECONDS",
        0.001,
    )
    signal = CancellationCoordinator().signal("openai-background-id-drift")

    with pytest.raises(ModelProviderError) as exc_info:
        provider.invoke_cancellable(
            ModelRequest(
                role="implementer",
                system_prompt="Return text.",
                user_prompt="Return done.",
            ),
            signal,
        )

    assert exc_info.value.code == "openai_background_state_unconfirmed"
    snapshot = store.public_snapshot("openai-background-id-drift")
    assert snapshot is not None
    assert snapshot.state.value == "active"
    store.close()


def test_openai_background_handle_has_bounded_lifecycle_timeout(
    tmp_path: Path,
    monkeypatch,
) -> None:
    provider = OpenAIResponsesProvider(
        api_key="test-key",
        model="test-model",
        timeout_seconds=0.05,
        background_cancellation=True,
    )
    store = _bind_private_store(provider, tmp_path)

    def request_json(*, method, endpoint, payload=None, timeout_seconds=None):
        return {
            "id": "resp_never_terminal",
            "status": "queued" if method == "POST" else "in_progress",
            "model": "test-model",
        }

    monkeypatch.setattr(provider, "_request_json", request_json)
    monkeypatch.setattr(
        "universal_coding_agent.testlab.openai_responses._BACKGROUND_POLL_INTERVAL_SECONDS",
        0.005,
    )
    signal = CancellationCoordinator().signal("openai-background-timeout")
    started = time.monotonic()

    with pytest.raises(ModelProviderError) as exc_info:
        provider.invoke_cancellable(
            ModelRequest(
                role="implementer",
                system_prompt="Return text.",
                user_prompt="Return done.",
            ),
            signal,
        )

    assert exc_info.value.code == "openai_background_timeout"
    assert time.monotonic() - started < 0.5
    snapshot = store.public_snapshot("openai-background-timeout")
    assert snapshot is not None
    assert snapshot.state.value == "active"
    store.close()


def test_openai_background_opt_in_rejects_foreground_only_test_transport() -> None:
    provider = OpenAIResponsesProvider(
        api_key="test-key",
        model="test-model",
        transport=lambda _payload: {},
        background_cancellation=True,
    )
    signal = CancellationCoordinator().signal("openai-background-test-transport")

    with pytest.raises(ModelProviderError) as exc_info:
        provider.invoke_cancellable(
            ModelRequest(
                role="implementer",
                system_prompt="Return text.",
                user_prompt="Return done.",
            ),
            signal,
        )

    assert exc_info.value.code == "openai_background_transport_unsupported"


def test_openai_background_opt_in_requires_private_lease_before_provider_work(
    monkeypatch,
) -> None:
    provider = OpenAIResponsesProvider(
        api_key="test-key",
        model="test-model",
        background_cancellation=True,
    )
    calls = 0

    def request_json(**_kwargs):
        nonlocal calls
        calls += 1
        return {}

    monkeypatch.setattr(provider, "_request_json", request_json)
    signal = CancellationCoordinator().signal("openai-background-no-store")

    with pytest.raises(ModelProviderError) as exc_info:
        provider.invoke_cancellable(
            ModelRequest(
                role="implementer",
                system_prompt="Return text.",
                user_prompt="Return done.",
            ),
            signal,
        )

    assert exc_info.value.code == "remote_operation_store_missing"
    assert calls == 0


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


def test_live_provider_preflight_checks_text_and_real_structured_schema() -> None:
    payloads = []

    def transport(payload):
        payloads.append(payload)
        if len(payloads) == 1:
            text = "UCA_OPENAI_PROVIDER_OK"
        else:
            text = json.dumps(
                {
                    "summary": "preflight",
                    "edits": [
                        {
                            "path": "app.py",
                            "operation": "modify",
                            "replacements": [
                                {
                                    "old_text": "@range:A000001..A000001",
                                    "new_text": "VALUE = 43\n",
                                }
                            ],
                            "content": None,
                        }
                    ],
                    "requested_test_profiles": ["live-check"],
                    "assumptions": [],
                }
            )
        return {
            "id": f"resp_{len(payloads)}",
            "status": "completed",
            "model": "test-model",
            "output": [
                {
                    "type": "message",
                    "content": [{"type": "output_text", "text": text}],
                }
            ],
        }

    provider = OpenAIResponsesProvider(
        api_key="test-key",
        model="test-model",
        transport=transport,
    )

    result = _provider_preflight(provider)

    assert result["ok"] is True
    assert [stage["stage"] for stage in result["stages"]] == [
        "text_response",
        "structured_schema",
    ]
    assert "text" not in payloads[0]
    assert payloads[1]["text"]["format"]["type"] == "json_schema"
    sent_schema = payloads[1]["text"]["format"]["schema"]
    assert sent_schema["required"] == list(sent_schema["properties"])


def test_live_provider_preflight_reports_safe_structured_http_failure() -> None:
    calls = 0

    def transport(_payload):
        nonlocal calls
        calls += 1
        if calls == 1:
            return {
                "id": "resp_text",
                "status": "completed",
                "model": "test-model",
                "output": [
                    {
                        "type": "message",
                        "content": [
                            {"type": "output_text", "text": "UCA_OPENAI_PROVIDER_OK"}
                        ],
                    }
                ],
            }
        raise ModelProviderError(
            "openai_http_error",
            "OpenAI Responses API HTTP 400: invalid schema",
        )

    provider = OpenAIResponsesProvider(
        api_key="test-key",
        model="test-model",
        transport=transport,
    )

    result = _provider_preflight(provider)

    assert result["ok"] is False
    assert result["failed_stage"] == "structured_schema"
    assert result["error"]["code"] == "openai_http_error"
    assert "invalid schema" in result["error"]["message"]


def _bind_private_store(
    provider: OpenAIResponsesProvider,
    tmp_path: Path,
) -> SqliteRemoteOperationLeaseStore:
    store = SqliteRemoteOperationLeaseStore(
        tmp_path / "private-remote-operations.sqlite"
    )
    provider.bind_remote_operation_store(store)
    return store
