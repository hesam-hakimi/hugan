from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from universal_coding_agent.core.remote_operations import RemoteOperationState
from universal_coding_agent.product.remote_operations import (
    SqliteRemoteOperationLeaseStore,
)
from universal_coding_agent.testlab.openai_background_reconciliation_live import (
    run_openai_background_reconciliation_live,
)
from universal_coding_agent.testlab.openai_responses import OpenAIResponsesProvider

_TASK_ID = "pretransfer-openai-background-reconciliation-task"
_UNDISPOSED_TASK_ID = "pretransfer-undisposed-background-task"
_UNDISPOSED_RESPONSE_ID = "resp_private_undisposed"


class FakeRestartWorker:
    def __init__(self) -> None:
        self.returncode: int | None = None

    def poll(self) -> int | None:
        return self.returncode

    def terminate(self) -> None:
        self.returncode = -15

    def kill(self) -> None:
        self.returncode = -9

    def wait(self, timeout: float | None = None) -> int:
        del timeout
        assert self.returncode is not None
        return self.returncode


def test_restart_reconciliation_live_scenario_is_explicit_and_redacted(
    tmp_path: Path,
    monkeypatch,
) -> None:
    source = _source_fixture(tmp_path / "source")
    endpoint = "https://example.test/v1/responses"
    response_id = "resp_private_live_restart"
    provider = OpenAIResponsesProvider(
        api_key="test-key",
        model="test-model",
        endpoint=endpoint,
        timeout_seconds=10,
        background_cancellation=True,
    )
    requests: list[str] = []

    def request_json(*, method, endpoint, payload=None, timeout_seconds=None):
        del endpoint, payload, timeout_seconds
        requests.append(method)
        return {
            "id": response_id,
            "status": "in_progress" if method == "GET" else "cancelled",
            "model": "test-model",
        }

    monkeypatch.setattr(provider, "_request_json", request_json)

    def worker_factory(state_root: Path, base_sha: str, timeout_seconds: float):
        del timeout_seconds
        store = SqliteRemoteOperationLeaseStore(
            state_root / "private-remote-operations.sqlite"
        )
        try:
            store.register(
                task_id=_TASK_ID,
                thread_id="pretransfer-openai-background-reconciliation-thread",
                transport="openai_responses",
                transport_scope=(
                    "sha256:"
                    + hashlib.sha256(endpoint.encode("utf-8")).hexdigest()
                ),
                operation_id=response_id,
                base_sha=base_sha,
                status="queued",
                state=RemoteOperationState.ACTIVE,
            )
            store.register(
                task_id=_UNDISPOSED_TASK_ID,
                thread_id="pretransfer-undisposed-background-thread",
                transport="openai_responses",
                transport_scope=(
                    "sha256:"
                    + hashlib.sha256(endpoint.encode("utf-8")).hexdigest()
                ),
                operation_id=_UNDISPOSED_RESPONSE_ID,
                base_sha=base_sha,
                status="queued",
                state=RemoteOperationState.ACTIVE,
            )
        finally:
            store.close()
        return FakeRestartWorker()

    summary = run_openai_background_reconciliation_live(
        tmp_path / "state",
        provider,
        source_root=source,
        timeout_seconds=10,
        worker_factory=worker_factory,
    )

    assert summary["qualified"] is True
    assert summary["automatic_provider_calls_after_restart"] == 0
    assert summary["explicit_observe_calls"] == 1
    assert summary["explicit_cancel_calls"] == 1
    assert summary["terminal_cancelled"] is True
    assert summary["durable_terminal_reloaded"] is True
    assert summary["provider_calls_during_disposition"] == 0
    assert summary["disposition_matches_remote"] is True
    assert summary["durable_disposition_reloaded"] is True
    assert summary["provider_calls_during_inventory"] == 0
    assert summary["inventory_eligible"] is True
    assert summary["inventory_private_fields_absent"] is True
    inventory = summary["retained_lease_inventory_before_retirement"]
    assert inventory["returned_count"] == 1
    assert inventory["items"][0]["task_id"] == _TASK_ID
    assert inventory["items"][0]["eligible_for_retirement"] is True
    assert inventory["items"][0]["eligibility_reasons"] == []
    assert summary["provider_calls_during_retirement"] == 0
    assert summary["retirement_matches_disposition"] is True
    assert summary["private_lease_absent_after_retirement"] is True
    assert summary["durable_private_lease_absent"] is True
    assert summary["durable_retirement_reloaded"] is True
    assert summary["disposition_preserved_after_retirement"] is True
    assert summary["private_identifier_absent_from_active_database"] is True
    assert summary["provider_calls_during_post_retirement_inventory"] == 0
    assert summary["inventory_empty_after_retirement"] is True
    post_retirement_inventory = summary[
        "retained_lease_inventory_after_retirement"
    ]
    assert post_retirement_inventory["items"] == []
    assert post_retirement_inventory["returned_count"] == 0
    assert post_retirement_inventory["scanned_count"] == 1
    disposition = summary["durable_terminal_disposition"]
    assert disposition["outcome"] == "cancelled"
    assert disposition["provider_confirmed_cancelled"] is True
    assert disposition["output_consumed"] is False
    assert disposition["graph_resumed"] is False
    assert disposition["program_phase_advanced"] is False
    retirement = summary["durable_private_lease_retirement"]
    assert retirement["disposition_audit_ref"] == disposition["audit_ref"]
    assert retirement["private_lease_rows_retired"] == 1
    assert retirement["private_identifier_retained_in_active_store"] is False
    assert retirement["provider_calls_made"] == 0
    assert retirement["task_outcome_changes_made"] == 0
    assert retirement["program_outcome_changes_made"] == 0
    assert summary["identity_and_base_bound"] is True
    assert summary["private_identifier_fields_absent"] is True
    assert summary["source"]["source_preserved"] is True
    assert requests == ["GET", "POST"]
    serialized = json.dumps(summary, sort_keys=True)
    assert response_id not in serialized
    assert _UNDISPOSED_RESPONSE_ID not in serialized
    assert "operation_id" not in serialized
    assert "response_id" not in serialized

    private_database = tmp_path / "state" / "private-remote-operations.sqlite"
    private_store = SqliteRemoteOperationLeaseStore(private_database)
    try:
        assert private_store.private_lease(_TASK_ID) is None
        assert private_store.public_snapshot(_TASK_ID) is None
        assert private_store.retirement(_TASK_ID) is not None
        assert private_store.private_lease(_UNDISPOSED_TASK_ID) is not None
    finally:
        private_store.close()
    assert response_id.encode("utf-8") not in private_database.read_bytes()


def test_live_workflow_runs_restart_reconciliation_without_uploading_private_lease(
) -> None:
    repository_root = Path(__file__).resolve().parents[2]
    workflow = (
        repository_root / ".github/workflows/pretransfer-live-openai.yml"
    ).read_text(encoding="utf-8")

    assert "openai_background_reconciliation_live" in workflow
    assert "background-reconciliation-live-summary.json" in workflow
    assert "private-remote-operations.sqlite" not in workflow
    assert "CANCELLATION_OUTCOME=${{ steps.cancellation.outcome }}" in workflow


def _source_fixture(path: Path) -> Path:
    path.mkdir()
    (path / "README.md").write_text("qualification fixture\n", encoding="utf-8")
    _git(path, "init", "-b", "main")
    _git(path, "config", "user.email", "uca-test@example.test")
    _git(path, "config", "user.name", "UCA Test")
    _git(path, "add", "README.md")
    _git(path, "commit", "-m", "qualification fixture")
    return path


def _git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()
