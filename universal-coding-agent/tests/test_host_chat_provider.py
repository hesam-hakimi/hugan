from __future__ import annotations

import os
from pathlib import Path

from universal_coding_agent.core.models import ModelRequest
from universal_coding_agent.providers.host_chat import HostChatCompletionsProvider, create_provider


HOST_MODULE = '''
from types import SimpleNamespace


class _Completions:
    def create(self, **kwargs):
        content = '{"phase_id":"P1","title":"Plan","objective":"Inspect","requirements":[],"exclusions":[],"evidence":[],"slices":[],"architecture_decisions_required":[],"blockers":[],"final_acceptance_criteria":[]}'
        return SimpleNamespace(
            model="actual-model",
            choices=[SimpleNamespace(message=SimpleNamespace(content=content), finish_reason="stop")],
            usage=SimpleNamespace(
                completion_tokens=77,
                completion_tokens_details=SimpleNamespace(reasoning_tokens=11),
            ),
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


def test_create_provider_uses_environment(tmp_path: Path, monkeypatch) -> None:
    path = _write_host_module(tmp_path)
    monkeypatch.setenv("UCA_HOST_CLIENT_PATH", str(path))
    provider = create_provider()
    assert provider.host_module_path == path.resolve()
    assert provider.probe() is True


def test_create_provider_does_not_require_site_secrets(tmp_path: Path, monkeypatch) -> None:
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
