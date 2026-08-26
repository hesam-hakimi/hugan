from __future__ import annotations

import hashlib
import json
import stat
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from universal_coding_agent.core.remote_operations import (
    RemoteOperationAction,
    RemoteOperationState,
)
from universal_coding_agent.product.remote_operations import (
    SqliteRemoteOperationLeaseStore,
)
from universal_coding_agent.product.workspace import ProductWorkspace
from universal_coding_agent.providers.base import ModelProviderError
from universal_coding_agent.testlab.openai_responses import (
    OpenAIResponsesProvider,
    _OpenAIHTTPError,
)
from universal_coding_agent.web.app import ProductWebRuntime, create_product_app

_ENDPOINT = "https://example.test/v1/responses"
_TASK_ID = "restart-reconcile-task"
_RESPONSE_ID = "resp_private_restart_identifier"


def test_private_remote_operation_store_reopens_with_redacted_public_state(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "private-remote-operations.sqlite"
    store = SqliteRemoteOperationLeaseStore(database_path)
    private = _register(store)
    public = store.public_snapshot(_TASK_ID)

    assert private.operation_id == _RESPONSE_ID
    assert _RESPONSE_ID not in repr(private)
    assert public is not None
    public_json = json.dumps(public.model_dump(mode="json"), sort_keys=True)
    assert _RESPONSE_ID not in public_json
    assert public.operation_ref == _digest(_RESPONSE_ID)
    assert public.transport_scope == _digest(_ENDPOINT)
    assert public.base_sha == "a" * 40
    assert stat.S_IMODE(database_path.stat().st_mode) & 0o077 == 0
    store.close()

    reopened = SqliteRemoteOperationLeaseStore(database_path)
    try:
        assert reopened.public_snapshot(_TASK_ID) == public
        with pytest.raises(ValueError, match="different active"):
            reopened.register(
                task_id=_TASK_ID,
                thread_id="thread-restart-reconcile",
                transport="openai_responses",
                transport_scope=_digest(_ENDPOINT),
                operation_id="resp_different_private_identifier",
                base_sha="a" * 40,
                status="queued",
                state=RemoteOperationState.ACTIVE,
            )
        terminal = reopened.record_status(
            _TASK_ID,
            status="cancelled",
            state=RemoteOperationState.TERMINAL,
        )
        stale_active = reopened.record_status(
            _TASK_ID,
            status="in_progress",
            state=RemoteOperationState.ACTIVE,
        )
        assert stale_active == terminal
    finally:
        reopened.close()


def test_restart_read_is_offline_and_explicit_observe_cancel_is_bounded(
    tmp_path: Path,
    monkeypatch,
) -> None:
    database_path = tmp_path / "private-remote-operations.sqlite"
    first = SqliteRemoteOperationLeaseStore(database_path)
    _register(first)
    first.close()

    provider = OpenAIResponsesProvider(
        api_key="test-key",
        model="test-model",
        endpoint=_ENDPOINT,
        background_cancellation=True,
    )
    reopened = SqliteRemoteOperationLeaseStore(database_path)
    provider.bind_remote_operation_store(reopened)
    calls: list[tuple[str, str, float | None]] = []

    def request_json(*, method, endpoint, payload=None, timeout_seconds=None):
        calls.append((method, endpoint, timeout_seconds))
        status = "in_progress" if method == "GET" else "cancelled"
        return {
            "id": _RESPONSE_ID,
            "status": status,
            "model": "test-model",
        }

    monkeypatch.setattr(provider, "_request_json", request_json)

    recovered = provider.remote_operation_snapshot(_TASK_ID)
    assert recovered is not None
    assert recovered.state is RemoteOperationState.ACTIVE
    assert calls == []

    observed = provider.reconcile_remote_operation(
        _TASK_ID,
        RemoteOperationAction.OBSERVE,
    )
    assert observed.state is RemoteOperationState.ACTIVE
    assert observed.reconciliation_attempts == 1
    assert calls == [("GET", f"{_ENDPOINT}/{_RESPONSE_ID}", 10.0)]

    cancelled = provider.reconcile_remote_operation(
        _TASK_ID,
        RemoteOperationAction.CANCEL,
    )
    assert cancelled.state is RemoteOperationState.TERMINAL
    assert cancelled.last_status == "cancelled"
    assert cancelled.cancellation_requested is True
    assert cancelled.reconciliation_attempts == 2
    assert cancelled.cancel_requests == 1
    assert calls[-1] == (
        "POST",
        f"{_ENDPOINT}/{_RESPONSE_ID}/cancel",
        10.0,
    )

    repeated = provider.reconcile_remote_operation(
        _TASK_ID,
        RemoteOperationAction.CANCEL,
    )
    assert repeated == cancelled
    assert len(calls) == 2
    assert _RESPONSE_ID not in json.dumps(
        repeated.model_dump(mode="json"),
        sort_keys=True,
    )
    reopened.close()


def test_missing_remote_state_fails_closed_and_is_durable(
    tmp_path: Path,
    monkeypatch,
) -> None:
    store = SqliteRemoteOperationLeaseStore(
        tmp_path / "private-remote-operations.sqlite"
    )
    _register(store)
    provider = OpenAIResponsesProvider(
        api_key="test-key",
        model="test-model",
        endpoint=_ENDPOINT,
        background_cancellation=True,
    )
    provider.bind_remote_operation_store(store)

    def unavailable(**_kwargs):
        raise _OpenAIHTTPError(
            404,
            "openai_http_error",
            f"remote response {_RESPONSE_ID} was not found",
        )

    monkeypatch.setattr(provider, "_request_json", unavailable)

    with pytest.raises(ModelProviderError) as exc_info:
        provider.reconcile_remote_operation(
            _TASK_ID,
            RemoteOperationAction.OBSERVE,
        )

    assert exc_info.value.code == "remote_state_unavailable"
    assert _RESPONSE_ID not in str(exc_info.value)
    snapshot = store.public_snapshot(_TASK_ID)
    assert snapshot is not None
    assert snapshot.state is RemoteOperationState.UNAVAILABLE
    assert snapshot.last_status == "remote_state_unavailable"
    store.close()


def test_changed_transport_scope_fails_before_remote_work(tmp_path: Path) -> None:
    store = SqliteRemoteOperationLeaseStore(
        tmp_path / "private-remote-operations.sqlite"
    )
    _register(store)
    provider = OpenAIResponsesProvider(
        api_key="test-key",
        model="test-model",
        endpoint="https://different.example.test/v1/responses",
        background_cancellation=True,
    )
    provider.bind_remote_operation_store(store)

    with pytest.raises(ModelProviderError) as exc_info:
        provider.reconcile_remote_operation(
            _TASK_ID,
            RemoteOperationAction.CANCEL,
        )

    assert exc_info.value.code == "remote_operation_transport_mismatch"
    snapshot = store.public_snapshot(_TASK_ID)
    assert snapshot is not None
    assert snapshot.state is RemoteOperationState.ACTIVE
    assert snapshot.cancel_requests == 0
    store.close()


def test_product_api_recovers_without_network_and_requires_explicit_action(
    tmp_path: Path,
    monkeypatch,
) -> None:
    product_root = tmp_path / "product"
    first_provider = OpenAIResponsesProvider(
        api_key="test-key",
        model="test-model",
        endpoint=_ENDPOINT,
        background_cancellation=True,
    )
    first_workspace = ProductWorkspace.create(product_root, first_provider)
    first_workspace.control.ensure_task(_TASK_ID)
    _register(first_workspace.remote_operations)
    first_workspace.close()

    provider = OpenAIResponsesProvider(
        api_key="test-key",
        model="test-model",
        endpoint=_ENDPOINT,
        background_cancellation=True,
    )
    calls: list[tuple[str, str]] = []

    def request_json(*, method, endpoint, payload=None, timeout_seconds=None):
        calls.append((method, endpoint))
        return {
            "id": _RESPONSE_ID,
            "status": "cancelled",
            "model": "test-model",
        }

    monkeypatch.setattr(provider, "_request_json", request_json)
    reopened = ProductWorkspace.create(product_root, provider)
    runtime = ProductWebRuntime(
        workspace=reopened,
        state_root=tmp_path / "runtime",
    )

    with TestClient(create_product_app(runtime)) as client:
        status = client.get(f"/api/tasks/{_TASK_ID}")
        assert status.status_code == 200
        body = status.json()
        assert body["remote_operation"]["state"] == "active"
        assert body["remote_operation"]["recovered_pending"] is True
        assert body["remote_operation"]["requires_explicit_action"] is True
        assert calls == []
        assert _RESPONSE_ID not in status.text

        runtime._runs[_TASK_ID] = {"task_id": _TASK_ID, "busy": True}
        busy = client.post(
            f"/api/tasks/{_TASK_ID}/remote-operation/reconcile",
            json={"action": "cancel"},
        )
        assert busy.status_code == 400
        assert calls == []
        runtime._runs.pop(_TASK_ID)

        reconciled = client.post(
            f"/api/tasks/{_TASK_ID}/remote-operation/reconcile",
            json={"action": "cancel"},
        )
        assert reconciled.status_code == 200
        result = reconciled.json()["remote_operation"]
        assert result["state"] == "terminal"
        assert result["last_status"] == "cancelled"
        assert result["requires_explicit_action"] is False
        assert calls == [("POST", f"{_ENDPOINT}/{_RESPONSE_ID}/cancel")]
        assert _RESPONSE_ID not in reconciled.text


def _register(
    store: SqliteRemoteOperationLeaseStore,
):
    return store.register(
        task_id=_TASK_ID,
        thread_id="thread-restart-reconcile",
        transport="openai_responses",
        transport_scope=_digest(_ENDPOINT),
        operation_id=_RESPONSE_ID,
        base_sha="a" * 40,
        status="queued",
        state=RemoteOperationState.ACTIVE,
    )


def _digest(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()
