from __future__ import annotations

import hashlib
import json
import sqlite3
import stat
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier, Event

import pytest
from fastapi.testclient import TestClient

from universal_coding_agent.core.remote_operations import (
    RemoteOperationAction,
    RemoteOperationDispositionOutcome,
    RemoteOperationState,
)
from universal_coding_agent.core.safe_models import SafeModePolicy
from universal_coding_agent.product.models import ControlState
from universal_coding_agent.product.remote_operations import (
    SqliteRemoteOperationLeaseStore,
)
from universal_coding_agent.product.task_control import TaskControlService
from universal_coding_agent.product.workspace import ProductWorkspace
from universal_coding_agent.providers.base import ModelProviderError
from universal_coding_agent.testlab.openai_responses import (
    OpenAIResponsesProvider,
    _OpenAIHTTPError,
)
from universal_coding_agent.web.app import (
    ProductWebRuntime,
    SafeTaskStartRequest,
    create_product_app,
)

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
    assert provider._remote_operation_store is not None
    assert not hasattr(provider._remote_operation_store, "retire")
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

        with pytest.raises(ValueError, match="remote-operation task identity"):
            runtime.start_safe_task(
                SafeTaskStartRequest(
                    task_id=_TASK_ID,
                    objective="Task identity reuse must stop before discovery or provider work.",
                    repository=str(tmp_path / "unused-source"),
                    ref="main",
                    policy=SafeModePolicy(),
                    test_profiles=(),
                )
            )
        assert calls == []

        active_disposition = client.post(
            f"/api/tasks/{_TASK_ID}/remote-operation/dispose",
            json={
                "outcome": "failed",
                "reason": "Operator cannot establish a terminal remote state.",
                "confirmed": True,
            },
        )
        assert active_disposition.status_code == 400
        assert calls == []

        pre_disposition_retirement = client.post(
            f"/api/tasks/{_TASK_ID}/remote-operation/retire",
            json={
                "disposition_audit_ref": _digest("missing-disposition"),
                "reason": "Retirement requires durable disposition evidence.",
                "confirmed": True,
            },
        )
        assert pre_disposition_retirement.status_code == 400
        assert reopened.remote_operations.private_lease(_TASK_ID) is not None
        assert calls == []

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

        missing_confirmation = client.post(
            f"/api/tasks/{_TASK_ID}/remote-operation/dispose",
            json={
                "outcome": "cancelled",
                "reason": "Provider reported terminal cancellation.",
                "confirmed": False,
            },
        )
        assert missing_confirmation.status_code == 422

        runtime._runs[_TASK_ID] = {"task_id": _TASK_ID, "busy": True}
        busy_disposition = client.post(
            f"/api/tasks/{_TASK_ID}/remote-operation/dispose",
            json={
                "outcome": "cancelled",
                "reason": "Provider reported terminal cancellation.",
                "confirmed": True,
            },
        )
        assert busy_disposition.status_code == 400
        runtime._runs.pop(_TASK_ID)

        disposed = client.post(
            f"/api/tasks/{_TASK_ID}/remote-operation/dispose",
            json={
                "outcome": "cancelled",
                "reason": "Provider reported terminal cancellation.",
                "confirmed": True,
            },
        )
        assert disposed.status_code == 200
        evidence = disposed.json()["remote_operation_disposition"]
        assert evidence["outcome"] == "cancelled"
        assert evidence["remote_state"] == "terminal"
        assert evidence["provider_confirmed_cancelled"] is True
        assert evidence["provider_calls_made"] == 0
        assert evidence["output_consumed"] is False
        assert evidence["graph_resumed"] is False
        assert evidence["program_phase_advanced"] is False
        assert evidence["audit_ref"].startswith("sha256:")
        assert calls == [("POST", f"{_ENDPOINT}/{_RESPONSE_ID}/cancel")]
        assert _RESPONSE_ID not in disposed.text

        repeated = client.post(
            f"/api/tasks/{_TASK_ID}/remote-operation/dispose",
            json={
                "outcome": "cancelled",
                "reason": "Provider reported terminal cancellation.",
                "confirmed": True,
            },
        )
        assert repeated.status_code == 200
        assert repeated.json()["remote_operation_disposition"] == evidence

        conflict = client.post(
            f"/api/tasks/{_TASK_ID}/remote-operation/dispose",
            json={
                "outcome": "failed",
                "reason": "Conflicting replacement.",
                "confirmed": True,
            },
        )
        assert conflict.status_code == 400

        final_status = client.get(f"/api/tasks/{_TASK_ID}")
        assert final_status.status_code == 200
        assert final_status.json()["status"] == "cancelled"
        assert final_status.json()["control"]["state"] == "cancelled"
        assert (
            final_status.json()["remote_operation"][
                "requires_explicit_disposition"
            ]
            is False
        )
        assert "remote_operation_lease_retirement" not in final_status.json()
        control_before_retirement = reopened.control.get_task(_TASK_ID)

        missing_retirement_confirmation = client.post(
            f"/api/tasks/{_TASK_ID}/remote-operation/retire",
            json={
                "disposition_audit_ref": evidence["audit_ref"],
                "reason": "The retained private identifier is no longer needed.",
                "confirmed": False,
            },
        )
        assert missing_retirement_confirmation.status_code == 422

        wrong_retirement_audit = client.post(
            f"/api/tasks/{_TASK_ID}/remote-operation/retire",
            json={
                "disposition_audit_ref": _digest("wrong-disposition-audit"),
                "reason": "The retained private identifier is no longer needed.",
                "confirmed": True,
            },
        )
        assert wrong_retirement_audit.status_code == 400
        assert reopened.remote_operations.private_lease(_TASK_ID) is not None

        runtime._runs[_TASK_ID] = {"task_id": _TASK_ID, "busy": True}
        busy_retirement = client.post(
            f"/api/tasks/{_TASK_ID}/remote-operation/retire",
            json={
                "disposition_audit_ref": evidence["audit_ref"],
                "reason": "The retained private identifier is no longer needed.",
                "confirmed": True,
            },
        )
        assert busy_retirement.status_code == 400
        runtime._runs[_TASK_ID]["busy"] = False

        runtime._remote_operation_actions.add(_TASK_ID)
        lifecycle_action_retirement = client.post(
            f"/api/tasks/{_TASK_ID}/remote-operation/retire",
            json={
                "disposition_audit_ref": evidence["audit_ref"],
                "reason": "Retirement cannot overlap another lifecycle action.",
                "confirmed": True,
            },
        )
        assert lifecycle_action_retirement.status_code == 400
        assert reopened.remote_operations.private_lease(_TASK_ID) is not None
        assert reopened.remote_operations.retirement(_TASK_ID) is None
        runtime._remote_operation_actions.discard(_TASK_ID)

        retired = client.post(
            f"/api/tasks/{_TASK_ID}/remote-operation/retire",
            json={
                "disposition_audit_ref": evidence["audit_ref"],
                "reason": "The retained private identifier is no longer needed.",
                "confirmed": True,
            },
        )
        assert retired.status_code == 200
        retirement = retired.json()["remote_operation_lease_retirement"]
        assert retirement["disposition_audit_ref"] == evidence["audit_ref"]
        assert retirement["private_lease_rows_retired"] == 1
        assert retirement["private_identifier_retained_in_active_store"] is False
        assert retirement["provider_calls_made"] == 0
        assert retirement["task_outcome_changes_made"] == 0
        assert retirement["program_outcome_changes_made"] == 0
        assert calls == [("POST", f"{_ENDPOINT}/{_RESPONSE_ID}/cancel")]
        assert reopened.control.get_task(_TASK_ID) == control_before_retirement

        repeated_retirement = client.post(
            f"/api/tasks/{_TASK_ID}/remote-operation/retire",
            json={
                "disposition_audit_ref": evidence["audit_ref"],
                "reason": "The retained private identifier is no longer needed.",
                "confirmed": True,
            },
        )
        assert repeated_retirement.status_code == 200
        assert (
            repeated_retirement.json()["remote_operation_lease_retirement"]
            == retirement
        )

        conflicting_retirement = client.post(
            f"/api/tasks/{_TASK_ID}/remote-operation/retire",
            json={
                "disposition_audit_ref": evidence["audit_ref"],
                "reason": "Conflicting retirement replacement.",
                "confirmed": True,
            },
        )
        assert conflicting_retirement.status_code == 400

        repeated_disposition_after_retirement = client.post(
            f"/api/tasks/{_TASK_ID}/remote-operation/dispose",
            json={
                "outcome": "cancelled",
                "reason": "Provider reported terminal cancellation.",
                "confirmed": True,
            },
        )
        assert repeated_disposition_after_retirement.status_code == 200
        assert (
            repeated_disposition_after_retirement.json()[
                "remote_operation_disposition"
            ]
            == evidence
        )

        retired_status = client.get(f"/api/tasks/{_TASK_ID}")
        assert retired_status.status_code == 200
        retired_body = retired_status.json()
        assert "remote_operation" not in retired_body
        assert retired_body["remote_operation_disposition"] == evidence
        assert retired_body["remote_operation_lease_retirement"] == retirement
        assert _RESPONSE_ID not in retired_status.text

    durable = ProductWorkspace.create(product_root, provider)
    try:
        disposition = durable.control.remote_operation_disposition(_TASK_ID)
        assert disposition is not None
        assert disposition.outcome is RemoteOperationDispositionOutcome.CANCELLED
        assert disposition.provider_confirmed_cancelled is True
        assert durable.control.get_task(_TASK_ID).state is ControlState.CANCELLED
        assert durable.remote_operations.private_lease(_TASK_ID) is None
        assert durable.remote_operations.public_snapshot(_TASK_ID) is None
        assert durable.remote_operations.retirement(_TASK_ID) is not None
    finally:
        durable.close()


def test_unavailable_remote_operation_can_close_failed_without_termination_claim(
    tmp_path: Path,
) -> None:
    workspace = ProductWorkspace.create(
        tmp_path / "product",
        OpenAIResponsesProvider(
            api_key="test-key",
            model="test-model",
            endpoint=_ENDPOINT,
            background_cancellation=True,
        ),
    )
    workspace.control.ensure_task(_TASK_ID)
    _register(workspace.remote_operations)
    workspace.remote_operations.mark_unavailable(_TASK_ID)
    snapshot = workspace.remote_operations.public_snapshot(_TASK_ID)
    assert snapshot is not None

    disposition = workspace.control.record_remote_operation_disposition(
        snapshot,
        RemoteOperationDispositionOutcome.FAILED,
        reason="Remote lifecycle state is unavailable; termination is not inferred.",
        confirmed=True,
    )

    assert disposition.outcome is RemoteOperationDispositionOutcome.FAILED
    assert disposition.remote_state is RemoteOperationState.UNAVAILABLE
    assert disposition.provider_confirmed_cancelled is False
    assert disposition.provider_calls_made == 0
    assert workspace.control.get_task(_TASK_ID).state is ControlState.FAILED
    workspace.close()


def test_private_lease_retirement_is_explicit_atomic_redacted_and_idempotent(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "private-remote-operations.sqlite"
    store = SqliteRemoteOperationLeaseStore(database_path)
    _register(store)
    store.record_status(
        _TASK_ID,
        status="cancelled",
        state=RemoteOperationState.TERMINAL,
    )
    snapshot = store.public_snapshot(_TASK_ID)
    assert snapshot is not None
    control = TaskControlService(tmp_path / "control.sqlite")
    control.ensure_task(_TASK_ID)
    disposition = control.record_remote_operation_disposition(
        snapshot,
        RemoteOperationDispositionOutcome.CANCELLED,
        reason="Provider reported terminal cancellation.",
        confirmed=True,
    )

    assert store.retirement(_TASK_ID) is None
    assert store.private_lease(_TASK_ID) is not None
    with pytest.raises(ValueError, match="explicit confirmation"):
        store.retire(
            disposition,
            reason="Private provider identifier is no longer needed.",
            confirmed=False,
        )
    assert store.private_lease(_TASK_ID) is not None

    retirement = store.retire(
        disposition,
        reason="Private provider identifier is no longer needed.",
        confirmed=True,
    )
    assert retirement.retirement_ref.startswith("sha256:")
    assert retirement.disposition_audit_ref == disposition.audit_ref
    assert retirement.disposition_outcome is disposition.outcome
    assert retirement.private_lease_rows_retired == 1
    assert retirement.private_identifier_retained_in_active_store is False
    assert retirement.provider_calls_made == 0
    assert retirement.output_consumed is False
    assert retirement.graph_resumed is False
    assert retirement.task_outcome_changes_made == 0
    assert retirement.program_outcome_changes_made == 0
    assert retirement.program_phase_advanced is False
    assert store.private_lease(_TASK_ID) is None
    assert store.public_snapshot(_TASK_ID) is None
    assert store.retirement(_TASK_ID) == retirement
    assert _RESPONSE_ID not in json.dumps(
        retirement.model_dump(mode="json"),
        sort_keys=True,
    )
    assert _RESPONSE_ID.encode("utf-8") not in database_path.read_bytes()

    repeated = store.retire(
        disposition,
        reason="Private provider identifier is no longer needed.",
        confirmed=True,
    )
    assert repeated == retirement
    with pytest.raises(ValueError, match="immutable"):
        store.retire(
            disposition,
            reason="Conflicting retirement reason.",
            confirmed=True,
        )
    with pytest.raises(ValueError, match="cannot be reused"):
        _register(store)
    store.close()
    control.close()

    reopened = SqliteRemoteOperationLeaseStore(database_path)
    try:
        assert reopened.private_lease(_TASK_ID) is None
        assert reopened.public_snapshot(_TASK_ID) is None
        assert reopened.retirement(_TASK_ID) == retirement
    finally:
        reopened.close()


def test_private_lease_retirement_rejects_drift_without_deleting_lease(
    tmp_path: Path,
) -> None:
    store = SqliteRemoteOperationLeaseStore(
        tmp_path / "private-remote-operations.sqlite"
    )
    _register(store)
    store.record_status(
        _TASK_ID,
        status="cancelled",
        state=RemoteOperationState.TERMINAL,
    )
    snapshot = store.public_snapshot(_TASK_ID)
    assert snapshot is not None
    control = TaskControlService(tmp_path / "control.sqlite")
    control.ensure_task(_TASK_ID)
    disposition = control.record_remote_operation_disposition(
        snapshot,
        RemoteOperationDispositionOutcome.CANCELLED,
        reason="Provider reported terminal cancellation.",
        confirmed=True,
    )
    store.connection.execute(
        "UPDATE remote_operation_leases SET revision = revision + 1 WHERE task_id = ?",
        (_TASK_ID,),
    )
    store.connection.commit()

    with pytest.raises(ValueError, match="does not match"):
        store.retire(
            disposition,
            reason="Retirement must reject drift.",
            confirmed=True,
        )
    assert store.private_lease(_TASK_ID) is not None
    assert store.retirement(_TASK_ID) is None
    store.close()
    control.close()


def test_private_lease_retirement_rolls_back_tombstone_when_delete_fails(
    tmp_path: Path,
) -> None:
    store, control, disposition = _disposed_private_lease(tmp_path)
    store.connection.execute(
        """
        CREATE TRIGGER reject_qualification_lease_delete
        BEFORE DELETE ON remote_operation_leases
        BEGIN
            SELECT RAISE(ABORT, 'injected delete failure');
        END
        """
    )
    store.connection.commit()

    with pytest.raises(sqlite3.IntegrityError, match="injected delete failure"):
        store.retire(
            disposition,
            reason="Atomic retirement must roll back after an injected failure.",
            confirmed=True,
        )

    assert store.private_lease(_TASK_ID) is not None
    assert store.retirement(_TASK_ID) is None
    store.close()
    control.close()


def test_concurrent_exact_private_lease_retirement_is_idempotent(
    tmp_path: Path,
) -> None:
    first, control, disposition = _disposed_private_lease(tmp_path)
    database_path = first.database_path
    second = SqliteRemoteOperationLeaseStore(database_path)
    reason = "Concurrent exact retirement must resolve to one durable receipt."

    with ThreadPoolExecutor(max_workers=2) as executor:
        receipts = tuple(
            executor.map(
                lambda store: store.retire(
                    disposition,
                    reason=reason,
                    confirmed=True,
                ),
                (first, second),
            )
        )

    assert receipts[0] == receipts[1]
    assert first.private_lease(_TASK_ID) is None
    assert second.private_lease(_TASK_ID) is None
    assert first.retirement(_TASK_ID) == receipts[0]
    assert second.retirement(_TASK_ID) == receipts[0]
    first.close()
    second.close()
    control.close()


def test_existing_private_lease_database_gets_additive_retirement_schema(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "private-remote-operations.sqlite"
    original = SqliteRemoteOperationLeaseStore(database_path)
    lease = _register(original)
    original.connection.execute("DROP TRIGGER reject_retired_remote_operation_lease")
    original.connection.execute("DROP TABLE remote_operation_lease_retirements")
    original.connection.commit()
    original.close()

    migrated = SqliteRemoteOperationLeaseStore(database_path)
    try:
        assert migrated.private_lease(_TASK_ID) == lease
        assert migrated.retirement(_TASK_ID) is None
        tables = {
            str(row[0])
            for row in migrated.connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }
        assert "remote_operation_lease_retirements" in tables
        triggers = {
            str(row[0])
            for row in migrated.connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'trigger'"
            ).fetchall()
        }
        assert "reject_retired_remote_operation_lease" in triggers
    finally:
        migrated.close()


@pytest.mark.parametrize("tamper", ["reference", "reason"])
def test_private_lease_retirement_receipt_hash_fails_closed_after_tampering(
    tmp_path: Path,
    tamper: str,
) -> None:
    store, control, disposition = _disposed_private_lease(tmp_path)
    store.retire(
        disposition,
        reason="Receipt integrity must survive restart and reload.",
        confirmed=True,
    )
    if tamper == "reference":
        store.connection.execute(
            """
            UPDATE remote_operation_lease_retirements SET retirement_ref = ?
            WHERE task_id = ?
            """,
            (f"sha256:{'f' * 64}", _TASK_ID),
        )
    else:
        store.connection.execute(
            """
            UPDATE remote_operation_lease_retirements SET reason = ?
            WHERE task_id = ?
            """,
            ("Tampered retirement reason.", _TASK_ID),
        )
    store.connection.commit()

    with pytest.raises(ValueError, match="retirement reference is invalid"):
        store.retirement(_TASK_ID)
    store.close()
    control.close()


def test_register_and_retire_race_cannot_delete_a_replacement_lease(
    tmp_path: Path,
) -> None:
    retiring_store, control, disposition = _disposed_private_lease(tmp_path)
    registering_store = SqliteRemoteOperationLeaseStore(retiring_store.database_path)
    barrier = Barrier(2)
    replacement_id = "resp_private_replacement_identifier"

    def attempt_retirement() -> str:
        barrier.wait()
        try:
            retiring_store.retire(
                disposition,
                reason="Race-safe retirement must bind the exact disposed lease.",
                confirmed=True,
            )
        except (ValueError, sqlite3.DatabaseError):
            return "retirement_rejected"
        return "retired"

    def attempt_registration() -> str:
        barrier.wait()
        try:
            registering_store.register(
                task_id=_TASK_ID,
                thread_id="thread-restart-reconcile",
                transport="openai_responses",
                transport_scope=_digest(_ENDPOINT),
                operation_id=replacement_id,
                base_sha="a" * 40,
                status="cancelled",
                state=RemoteOperationState.TERMINAL,
            )
        except (ValueError, sqlite3.DatabaseError):
            registering_store.connection.rollback()
            return "registration_rejected"
        return "registered"

    with ThreadPoolExecutor(max_workers=2) as executor:
        retirement_future = executor.submit(attempt_retirement)
        registration_future = executor.submit(attempt_registration)
        resolved = {retirement_future.result(), registration_future.result()}

    lease = retiring_store.private_lease(_TASK_ID)
    receipt = retiring_store.retirement(_TASK_ID)
    assert resolved in (
        {"retired", "registration_rejected"},
        {"retirement_rejected", "registered"},
    )
    if receipt is not None:
        assert lease is None
        assert resolved == {"retired", "registration_rejected"}
    else:
        assert lease is not None
        assert lease.operation_ref == _digest(replacement_id)
        assert resolved == {"retirement_rejected", "registered"}
    retiring_store.close()
    registering_store.close()
    control.close()


def test_worker_start_and_remote_lifecycle_reservation_are_mutually_exclusive(
    tmp_path: Path,
) -> None:
    class NoopExecutor:
        def __init__(self) -> None:
            self.submissions = 0

        def submit(self, *_args, **_kwargs):
            self.submissions += 1
            return None

        def shutdown(self, **_kwargs) -> None:
            return None

    workspace = ProductWorkspace.create(
        tmp_path / "product",
        OpenAIResponsesProvider(
            api_key="test-key",
            model="test-model",
            endpoint=_ENDPOINT,
            background_cancellation=True,
        ),
    )
    workspace.control.ensure_task(_TASK_ID)
    executor = NoopExecutor()
    runtime = ProductWebRuntime(
        workspace=workspace,
        state_root=tmp_path / "runtime",
        executor=executor,
    )
    runtime._runs[_TASK_ID] = {
        "task_id": _TASK_ID,
        "thread_id": "thread-restart-reconcile",
        "busy": False,
        "status": "awaiting_scope_approval",
    }
    barrier = Barrier(2)
    scope_finished = Event()

    def reserve_lifecycle() -> str:
        barrier.wait()
        try:
            runtime._begin_remote_operation_action(_TASK_ID)
        except ValueError:
            return "lifecycle_rejected"
        scope_finished.wait(timeout=2)
        runtime._end_remote_operation_action(_TASK_ID)
        return "lifecycle_reserved"

    def start_worker() -> str:
        barrier.wait()
        try:
            runtime.scope_decision(_TASK_ID, True)
        except ValueError:
            return "worker_rejected"
        finally:
            scope_finished.set()
        return "worker_started"

    with ThreadPoolExecutor(max_workers=2) as pool:
        lifecycle_future = pool.submit(reserve_lifecycle)
        worker_future = pool.submit(start_worker)
        outcomes = {lifecycle_future.result(), worker_future.result()}

    assert outcomes in (
        {"lifecycle_reserved", "worker_rejected"},
        {"lifecycle_rejected", "worker_started"},
    )
    assert executor.submissions == int("worker_started" in outcomes)
    runtime.close()


def _disposed_private_lease(tmp_path: Path):
    store = SqliteRemoteOperationLeaseStore(
        tmp_path / "private-remote-operations.sqlite"
    )
    _register(store)
    store.record_status(
        _TASK_ID,
        status="cancelled",
        state=RemoteOperationState.TERMINAL,
    )
    snapshot = store.public_snapshot(_TASK_ID)
    assert snapshot is not None
    control = TaskControlService(tmp_path / "control.sqlite")
    control.ensure_task(_TASK_ID)
    disposition = control.record_remote_operation_disposition(
        snapshot,
        RemoteOperationDispositionOutcome.CANCELLED,
        reason="Provider reported terminal cancellation.",
        confirmed=True,
    )
    return store, control, disposition


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
