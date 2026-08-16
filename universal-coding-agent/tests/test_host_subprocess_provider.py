# ruff: noqa: I001

from __future__ import annotations

import sys

from universal_coding_agent.core.models import ModelRequest
from universal_coding_agent.providers.host_subprocess import HostSubprocessProvider


HOST_MODULE = '''
from types import SimpleNamespace


class _Completions:
    def create(self, **kwargs):
        content = '{"status":"OK"}'
        return SimpleNamespace(
            model="actual-host-model",
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content=content),
                    finish_reason="stop",
                )
            ],
            usage=SimpleNamespace(
                completion_tokens=44,
                completion_tokens_details=SimpleNamespace(reasoning_tokens=7),
            ),
        )


class _Client:
    def __init__(self):
        self.chat = SimpleNamespace(completions=_Completions())


def create_client():
    return _Client()


def get_configured_model_or_deployment():
    return SimpleNamespace(deployment="host-deployment")
'''

HOST_INVOKE_MODULE = '''
def invoke_text(prompt, max_output_tokens=8):
    assert max_output_tokens <= 64
    return "UCA_HOST_PROVIDER_OK"


def create_client():
    raise AttributeError("direct client must not be used by probe")
'''

BROKEN_INVOKE_MODULE = '''
def invoke_text(prompt, max_output_tokens=8):
    raise AttributeError("private internal detail")
'''


def _host_module(tmp_path, content=HOST_MODULE):
    path = tmp_path / "host_client.py"
    path.write_text(content, encoding="utf-8")
    return path


def test_subprocess_provider_probe_and_structured_invoke(tmp_path) -> None:
    provider = HostSubprocessProvider(
        host_module_path=_host_module(tmp_path),
        host_python=sys.executable,
    )
    details = provider.probe_details()
    assert details["ok"] is True
    assert provider.probe() is True

    response = provider.invoke(
        ModelRequest(
            role="qualification",
            system_prompt="Return JSON.",
            user_prompt="Return status OK.",
            response_schema={"type": "object"},
            max_output_tokens=512,
        )
    )
    assert response.structured == {"status": "OK"}
    assert response.actual_model == "actual-host-model"
    assert response.finish_reason == "stop"
    assert response.completion_tokens == 44
    assert response.reasoning_tokens == 7
    assert response.safe_diagnostics["requested_deployment"] == "host-deployment"


def test_probe_prefers_existing_host_invoke_contract(tmp_path) -> None:
    provider = HostSubprocessProvider(
        host_module_path=_host_module(tmp_path, HOST_INVOKE_MODULE),
        host_python=sys.executable,
    )
    details = provider.probe_details()
    assert details["ok"] is True
    assert details["content"] == "UCA_HOST_PROVIDER_OK"
    assert details["safe_diagnostics"]["transport"] == "host_invoke_function"


def test_probe_reports_safe_host_invoke_stage(tmp_path) -> None:
    provider = HostSubprocessProvider(
        host_module_path=_host_module(tmp_path, BROKEN_INVOKE_MODULE),
        host_python=sys.executable,
    )
    details = provider.probe_details()
    assert details["ok"] is False
    assert details["error_code"] == "host_invoke_function_failed"
    assert details["error_type"] == "AttributeError"
    assert details["error_stage"] == "invoke_host_function"
    assert "private internal detail" not in str(details)


def test_subprocess_provider_returns_safe_load_error(tmp_path) -> None:
    broken = tmp_path / "broken_client.py"
    broken.write_text("raise RuntimeError('private internal detail')\n", encoding="utf-8")
    provider = HostSubprocessProvider(
        host_module_path=broken,
        host_python=sys.executable,
    )
    details = provider.probe_details()
    assert details["ok"] is False
    assert details["error_code"] == "host_client_load_failed"
    assert details["error_type"] == "RuntimeError"
    assert details["error_stage"] == "load_host_module"
    assert "private internal detail" not in str(details)
