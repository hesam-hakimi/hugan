from __future__ import annotations

import os
from pathlib import Path

import pytest

from universal_coding_agent.core.cancellation import CancellationCoordinator
from universal_coding_agent.core.models import ModelRequest
from universal_coding_agent.providers.base import ModelProviderError
from universal_coding_agent.providers.host_chat import (
    CANCELLABLE_COMPLETION_FACTORY_ENV,
    HostChatCompletionsProvider,
    create_provider,
)

HOST_MODULE = '''
from types import SimpleNamespace


class _Completions:
    def create(self, **kwargs):
        content = '{"phase_id":"P1"}'
        message = SimpleNamespace(content=content)
        choice = SimpleNamespace(message=message, finish_reason="stop")
        details = SimpleNamespace(reasoning_tokens=11)
        usage = SimpleNamespace(completion_tokens=77, completion_tokens_details=details)
        return SimpleNamespace(
            model="actual-model",
            choices=[choice],
            usage=usage,
        )


class _Client:
    def __init__(self):
        self.chat = SimpleNamespace(completions=_Completions())


def create_client():
    return _Client()


def get_configured_model_or_deployment():
    return SimpleNamespace(deployment="configured-deployment")
'''


def _write_host_module(tmp_path: Path) -> Path:
    path = tmp_path / "host_client.py"
    path.write_text(HOST_MODULE, encoding="utf-8")
    return path


def test_host_provider_probe_and_invoke(tmp_path: Path) -> None:
    provider = HostChatCompletionsProvider(_write_host_module(tmp_path))
    assert provider.probe() is True

    response = provider.invoke(
        ModelRequest(
            role="planner",
            system_prompt="Return JSON.",
            user_prompt="Plan the task.",
            response_schema={"type": "object"},
            max_output_tokens=512,
        )
    )

    assert response.actual_model == "actual-model"
    assert response.finish_reason == "stop"
    assert response.completion_tokens == 77
    assert response.reasoning_tokens == 11
    assert response.structured is not None
    assert response.structured["phase_id"] == "P1"
    assert response.safe_diagnostics["requested_deployment"] == "configured-deployment"
    assert response.safe_diagnostics["cancellation_mode"] == "not_requested"


def test_host_provider_without_handle_uses_cooperative_cancellation_mode(
    tmp_path: Path,
) -> None:
    provider = HostChatCompletionsProvider(_write_host_module(tmp_path))
    signal = CancellationCoordinator().signal("cooperative-host-chat")

    response = provider.invoke_cancellable(
        ModelRequest(
            role="planner",
            system_prompt="Return JSON.",
            user_prompt="Plan the task.",
            response_schema={"type": "object"},
        ),
        signal,
    )

    assert response.safe_diagnostics["cancellation_mode"] == "cooperative"


def test_host_provider_uses_owned_cancellable_handle(tmp_path: Path) -> None:
    path = tmp_path / "cancellable_host_client.py"
    path.write_text(
        HOST_MODULE
        + """

class _Handle:
    def __init__(self, client, kwargs):
        self.client = client
        self.kwargs = kwargs
        self.completed = False

    def result(self):
        response = self.client.chat.completions.create(**self.kwargs)
        self.completed = True
        return response

    def cancel(self):
        self.completed = True

    def done(self):
        return self.completed

def create_cancellable_completion(client, **kwargs):
    return _Handle(client, kwargs)
""",
        encoding="utf-8",
    )
    provider = HostChatCompletionsProvider(
        path,
        cancellable_completion_factory_name="create_cancellable_completion",
    )
    signal = CancellationCoordinator().signal("owned-host-chat")

    response = provider.invoke_cancellable(
        ModelRequest(
            role="planner",
            system_prompt="Return JSON.",
            user_prompt="Plan the task.",
            response_schema={"type": "object"},
        ),
        signal,
    )

    assert response.structured == {"phase_id": "P1"}
    assert response.safe_diagnostics["cancellation_mode"] == "owned_handle"


def test_create_provider_uses_environment(tmp_path: Path, monkeypatch) -> None:
    path = _write_host_module(tmp_path)
    monkeypatch.setenv("UCA_HOST_CLIENT_PATH", str(path))
    provider = create_provider()
    assert provider.host_module_path == path.resolve()
    assert provider.probe() is True


def test_create_provider_uses_explicit_cancellable_factory_setting(
    tmp_path: Path,
    monkeypatch,
) -> None:
    path = _write_host_module(tmp_path)
    monkeypatch.setenv("UCA_HOST_CLIENT_PATH", str(path))
    monkeypatch.setenv(
        CANCELLABLE_COMPLETION_FACTORY_ENV,
        "create_cancellable_completion",
    )

    provider = create_provider()

    assert (
        provider.cancellable_completion_factory_name
        == "create_cancellable_completion"
    )


def test_host_provider_rejects_invalid_cancellable_handle(tmp_path: Path) -> None:
    path = tmp_path / "invalid_cancellable_client.py"
    path.write_text(
        HOST_MODULE
        + """

def create_cancellable_completion(**kwargs):
    return object()
""",
        encoding="utf-8",
    )
    provider = HostChatCompletionsProvider(
        path,
        cancellable_completion_factory_name="create_cancellable_completion",
    )
    signal = CancellationCoordinator().signal("invalid-host-handle")

    with pytest.raises(ModelProviderError) as exc_info:
        provider.invoke_cancellable(
            ModelRequest(
                role="planner",
                system_prompt="Return JSON.",
                user_prompt="Plan the task.",
            ),
            signal,
        )

    assert exc_info.value.code == "host_cancellable_handle_invalid"


def test_create_provider_does_not_require_site_secrets(
    tmp_path: Path,
    monkeypatch,
) -> None:
    path = _write_host_module(tmp_path)
    monkeypatch.setenv("UCA_HOST_CLIENT_PATH", str(path))
    monkeypatch.delenv("AZURE_OPENAI_API_KEY", raising=False)
    provider = create_provider()
    assert provider.capabilities().actual_model_identity is True


def test_host_provider_does_not_mutate_environment(tmp_path: Path) -> None:
    before = dict(os.environ)
    provider = HostChatCompletionsProvider(_write_host_module(tmp_path))
    provider.probe()
    assert dict(os.environ) == before
