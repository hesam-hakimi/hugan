from __future__ import annotations

import os
import threading
import time
from pathlib import Path

import pytest
from pydantic import BaseModel

from universal_coding_agent.core.cancellation import (
    CancellationCoordinator,
    OwnedOperationKind,
)
from universal_coding_agent.core.models import ModelRequest
from universal_coding_agent.orchestration.structured_output import invoke_structured
from universal_coding_agent.product.models import ControlState
from universal_coding_agent.product.task_control import TaskControlService
from universal_coding_agent.providers.base import ModelProviderError
from universal_coding_agent.providers.host_chat import (
    CANCELLABLE_COMPLETION_FACTORY_ENV,
    PAUSABLE_COMPLETION_FACTORY_ENV,
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


def test_host_provider_uses_owned_pausable_handle_for_active_pause(
    tmp_path: Path,
) -> None:
    path = tmp_path / "pausable_host_client.py"
    path.write_text(
        HOST_MODULE
        + """
import threading
from types import SimpleNamespace

LAST_HANDLE = None

class _Handle:
    def __init__(self):
        self._cancelled = False
        self._done = threading.Event()
        self._paused = threading.Event()
        self._released = threading.Event()
        self.source_marker = "preserved-source"

    def result(self):
        self._released.wait(timeout=5)
        if self._cancelled:
            raise RuntimeError("cancelled")
        self._done.set()
        choice = SimpleNamespace(
            message=SimpleNamespace(content='{"phase_id":"P2.2b"}'),
            finish_reason="stop",
        )
        return SimpleNamespace(model="fixture", choices=[choice], usage=None)

    def pause(self):
        self._paused.set()

    def resume(self):
        self._paused.clear()

    def paused(self):
        return self._paused.is_set()

    def cancel(self):
        self._cancelled = True
        self._paused.clear()
        self._released.set()
        self._done.set()

    def done(self):
        return self._done.is_set()

    def release(self):
        self._released.set()

def create_pausable_completion(**kwargs):
    global LAST_HANDLE
    LAST_HANDLE = _Handle()
    return LAST_HANDLE
""",
        encoding="utf-8",
    )
    provider = HostChatCompletionsProvider(
        path,
        pausable_completion_factory_name="create_pausable_completion",
    )
    control = TaskControlService(tmp_path / "pausable-host.sqlite")
    task_id = "pausable-host-chat"
    control.ensure_task(task_id)
    signal = control.cancellation.signal(task_id)

    class Payload(BaseModel):
        phase_id: str

    responses: list[Payload] = []
    errors: list[BaseException] = []

    def invoke() -> None:
        try:
            result = invoke_structured(
                provider,
                ModelRequest(
                    role="implementer",
                    system_prompt="Return JSON.",
                    user_prompt="Return the phase.",
                ),
                Payload,
                cancellation=signal,
            )
            responses.append(result.value)
        except BaseException as exc:  # captured for assertion in the parent thread
            errors.append(exc)

    module = provider._host_module()
    worker = threading.Thread(target=invoke)
    worker.start()
    assert _wait_until(lambda: module.LAST_HANDLE is not None)
    handle = module.LAST_HANDLE

    paused = control.pause_task(task_id, reason="operator requested active pause")
    pause_report = control.pause_report(task_id)
    marker_during_pause = handle.source_marker

    assert paused.state is ControlState.PAUSED
    assert handle.paused() is True
    assert marker_during_pause == "preserved-source"
    assert pause_report is not None
    assert pause_report.active_operation_kinds == ("provider",)
    assert pause_report.owned_pausable_operations_observed == 1
    assert pause_report.unsupported_active_operations_observed == 0
    assert pause_report.active_pause_acknowledged is True

    resumed = control.resume_task(task_id)
    resume_report = control.pause_report(task_id)
    assert resumed.state is ControlState.RUNNING
    assert handle.paused() is False
    assert resume_report is not None
    assert resume_report.active_resume_acknowledged is True

    handle.release()
    worker.join(timeout=5)
    assert worker.is_alive() is False
    assert errors == []
    assert responses[0].phase_id == "P2.2b"
    assert handle.source_marker == marker_during_pause
    control.close()


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


def test_create_provider_uses_explicit_pausable_factory_setting(
    tmp_path: Path,
    monkeypatch,
) -> None:
    path = _write_host_module(tmp_path)
    monkeypatch.setenv("UCA_HOST_CLIENT_PATH", str(path))
    monkeypatch.setenv(
        PAUSABLE_COMPLETION_FACTORY_ENV,
        "create_pausable_completion",
    )

    provider = create_provider()

    assert provider.pausable_completion_factory_name == "create_pausable_completion"


def test_host_provider_rejects_conflicting_control_factories(tmp_path: Path) -> None:
    with pytest.raises(ModelProviderError) as exc_info:
        HostChatCompletionsProvider(
            _write_host_module(tmp_path),
            cancellable_completion_factory_name="create_cancellable_completion",
            pausable_completion_factory_name="create_pausable_completion",
        )

    assert exc_info.value.code == "host_control_factory_conflict"


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
        with signal.operation(OwnedOperationKind.PROVIDER):
            provider.invoke_cancellable(
                ModelRequest(
                    role="planner",
                    system_prompt="Return JSON.",
                    user_prompt="Plan the task.",
                ),
                signal,
            )

    assert exc_info.value.code == "host_cancellable_handle_invalid"


def test_host_provider_rejects_invalid_pausable_handle(tmp_path: Path) -> None:
    path = tmp_path / "invalid_pausable_client.py"
    path.write_text(
        HOST_MODULE
        + """

class _IncompleteHandle:
    def result(self):
        return None

    def cancel(self):
        return None

    def done(self):
        return True

def create_pausable_completion(**kwargs):
    return _IncompleteHandle()
""",
        encoding="utf-8",
    )
    provider = HostChatCompletionsProvider(
        path,
        pausable_completion_factory_name="create_pausable_completion",
    )
    signal = CancellationCoordinator().signal("invalid-pausable-host-handle")

    with pytest.raises(ModelProviderError) as exc_info:
        with signal.operation(OwnedOperationKind.PROVIDER):
            provider.invoke_cancellable(
                ModelRequest(
                    role="planner",
                    system_prompt="Return JSON.",
                    user_prompt="Plan the task.",
                ),
                signal,
            )

    assert exc_info.value.code == "host_pausable_handle_invalid"


def test_host_provider_rejects_missing_pausable_factory(tmp_path: Path) -> None:
    provider = HostChatCompletionsProvider(
        _write_host_module(tmp_path),
        pausable_completion_factory_name="missing_factory",
    )
    signal = CancellationCoordinator().signal("missing-pausable-host-factory")

    with pytest.raises(ModelProviderError) as exc_info:
        provider.invoke_cancellable(
            ModelRequest(
                role="planner",
                system_prompt="Return JSON.",
                user_prompt="Plan the task.",
            ),
            signal,
        )

    assert exc_info.value.code == "host_pausable_factory_missing"


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


def _wait_until(predicate, timeout_seconds: float = 5.0) -> bool:
    event = threading.Event()
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if predicate():
            return True
        event.wait(0.01)
    return predicate()
