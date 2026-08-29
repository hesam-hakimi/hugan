from __future__ import annotations

import json
import sys
from pathlib import Path

from universal_coding_agent.providers.host_subprocess import HostSubprocessProvider
from universal_coding_agent.testlab.host_subprocess_pause_live import (
    run_host_subprocess_pause_live,
)


def test_host_subprocess_pause_live_qualifies_real_bridge_lifecycle(
    tmp_path: Path,
    monkeypatch,
) -> None:
    module = tmp_path / "live_host_subprocess_client.py"
    module.write_text(
        """
import threading
import time
from types import SimpleNamespace

class _Completions:
    def create(self, **kwargs):
        raise AssertionError("direct completion path must not be used")

class _Client:
    def __init__(self):
        self.chat = SimpleNamespace(completions=_Completions())

class _Handle:
    def __init__(self):
        self._cancelled = False
        self._done = False
        self._paused = threading.Event()

    def result(self):
        for _ in range(500):
            while self._paused.is_set() and not self._cancelled:
                time.sleep(0.001)
            if self._cancelled:
                raise RuntimeError("cancelled")
            time.sleep(0.002)
        self._done = True
        choice = SimpleNamespace(
            message=SimpleNamespace(content="PRIVATE_FIXTURE_RESPONSE"),
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
        self._done = True

    def done(self):
        return self._done

def create_client():
    return _Client()

def get_configured_model_or_deployment():
    return SimpleNamespace(deployment="fixture")

def create_pausable_completion(**kwargs):
    return _Handle()
""",
        encoding="utf-8",
    )
    snapshot = {
        "head_sha": "a" * 40,
        "tree_sha": "b" * 40,
        "status": "",
    }
    monkeypatch.setattr(
        "universal_coding_agent.testlab.host_subprocess_pause_live._source_snapshot",
        lambda _root: dict(snapshot),
    )
    provider = HostSubprocessProvider(
        module,
        sys.executable,
        pausable_completion_factory_name="create_pausable_completion",
    )

    state_root = tmp_path / "state"
    summary = run_host_subprocess_pause_live(
        state_root,
        provider,
        source_root=tmp_path,
        stable_pause_seconds=1.5,
    )

    assert summary["qualified"] is True
    assert summary["transport"] == "host_subprocess_pausable_bridge"
    assert summary["paused_before_window"] is True
    assert summary["paused_after_window"] is True
    assert summary["done_before_window"] is False
    assert summary["done_after_window"] is False
    assert summary["invocation_done_before_window"] is False
    assert summary["invocation_done_after_window"] is False
    assert summary["invocation_succeeded"] is True
    assert summary["resumed_to_completion"] is True
    assert summary["durable_report_reloaded"] is True
    assert summary["source"]["source_preserved"] is True
    evidence = (state_root / "host-subprocess-active-pause-live-summary.json").read_text(
        encoding="utf-8"
    )
    assert json.loads(evidence) == summary
    assert "PRIVATE_FIXTURE_RESPONSE" not in evidence
    assert "Write an extended numbered sequence" not in evidence
