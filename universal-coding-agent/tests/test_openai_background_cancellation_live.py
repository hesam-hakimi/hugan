from __future__ import annotations

import subprocess
from pathlib import Path

from universal_coding_agent.testlab.openai_background_cancellation_live import (
    run_openai_background_cancellation_live,
)
from universal_coding_agent.testlab.openai_responses import (
    OpenAIBackgroundLifecycleRecorder,
    OpenAIResponsesProvider,
)


def test_live_background_cancellation_observes_cancelled_and_persists_report(
    tmp_path: Path,
    monkeypatch,
) -> None:
    source = _source_fixture(tmp_path / "source")
    recorder = OpenAIBackgroundLifecycleRecorder()
    provider = OpenAIResponsesProvider(
        api_key="test-key",
        model="test-model",
        endpoint="https://example.test/v1/responses",
        timeout_seconds=1,
        background_cancellation=True,
        background_lifecycle_recorder=recorder,
    )
    cancel_returned = False

    def request_json(*, method, endpoint, payload=None, timeout_seconds=None):
        nonlocal cancel_returned
        if method == "POST" and endpoint == provider.endpoint:
            assert payload["background"] is True
            assert payload["store"] is False
            return {
                "id": "resp_live_cancel",
                "status": "queued",
                "model": "test-model",
            }
        if method == "POST" and endpoint.endswith("/resp_live_cancel/cancel"):
            cancel_returned = True
            return {
                "id": "resp_live_cancel",
                "status": "in_progress",
                "model": "test-model",
            }
        if method == "GET" and endpoint.endswith("/resp_live_cancel"):
            assert cancel_returned
            return {
                "id": "resp_live_cancel",
                "status": "cancelled",
                "model": "test-model",
            }
        raise AssertionError(f"unexpected lifecycle request: {method} {endpoint}")

    monkeypatch.setattr(provider, "_request_json", request_json)
    monkeypatch.setattr(
        "universal_coding_agent.testlab.openai_responses._BACKGROUND_CANCEL_POLL_INTERVAL_SECONDS",
        0.001,
    )

    summary = run_openai_background_cancellation_live(
        tmp_path / "state",
        provider,
        recorder,
        source_root=source,
    )

    assert summary["qualified"] is True
    assert summary["lifecycle"] == {
        "handle_started": True,
        "response_id_observed": True,
        "actual_model": "test-model",
        "initial_status": "queued",
        "cancel_dispatched": True,
        "cancel_response_status": "in_progress",
        "terminal_status": "cancelled",
        "terminal_confirmed": True,
    }
    assert summary["invocation_finished"] is True
    assert summary["invocation_cancelled"] is True
    assert summary["cancellation_report"][
        "owned_cancellable_operations_observed"
    ] == 1
    assert summary["cancellation_report"][
        "cancellable_operation_cancel_requests"
    ] == 1
    assert summary["durable_report_reloaded"] is True
    assert summary["source"]["source_preserved"] is True


def test_live_background_cancellation_fails_closed_if_create_is_terminal(
    tmp_path: Path,
    monkeypatch,
) -> None:
    source = _source_fixture(tmp_path / "source")
    recorder = OpenAIBackgroundLifecycleRecorder()
    provider = OpenAIResponsesProvider(
        api_key="test-key",
        model="test-model",
        endpoint="https://example.test/v1/responses",
        timeout_seconds=1,
        background_cancellation=True,
        background_lifecycle_recorder=recorder,
    )

    def request_json(*, method, endpoint, payload=None, timeout_seconds=None):
        assert method == "POST"
        assert endpoint == provider.endpoint
        return {
            "id": "resp_completed_before_cancel",
            "status": "completed",
            "model": "test-model",
            "output": [
                {
                    "type": "message",
                    "content": [{"type": "output_text", "text": "completed"}],
                }
            ],
        }

    monkeypatch.setattr(provider, "_request_json", request_json)

    summary = run_openai_background_cancellation_live(
        tmp_path / "state",
        provider,
        recorder,
        source_root=source,
    )

    assert summary["qualified"] is False
    assert summary["lifecycle"]["terminal_status"] == "completed"
    assert summary["lifecycle"]["cancel_dispatched"] is False
    assert summary["source"]["source_preserved"] is True


def test_live_workflow_aggregates_background_cancellation_outcome() -> None:
    repository_root = Path(__file__).resolve().parents[2]
    workflow = (repository_root / ".github/workflows/pretransfer-live-openai.yml").read_text(
        encoding="utf-8"
    )

    assert "id: cancellation" in workflow
    assert "UCA_OPENAI_BACKGROUND_CANCELLATION=1" in workflow
    assert "CANCELLATION_OUTCOME=${{ steps.cancellation.outcome }}" in workflow
    assert 'test "${{ steps.cancellation.outcome }}" = "success"' in workflow


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
