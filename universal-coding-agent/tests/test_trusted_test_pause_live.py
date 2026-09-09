from __future__ import annotations

from pathlib import Path

from test_trusted_test_pause import PAUSABLE_TEST_ADAPTER

from universal_coding_agent.safe.testing import SafeTestRunner
from universal_coding_agent.testlab.trusted_test_pause_live import (
    run_trusted_test_pause_live,
)


def test_trusted_test_pause_live_qualifies_adapter_lifecycle(
    tmp_path: Path,
    monkeypatch,
) -> None:
    module = tmp_path / "live_trusted_test_adapter.py"
    module.write_text(PAUSABLE_TEST_ADAPTER, encoding="utf-8")
    snapshot = {
        "head_sha": "a" * 40,
        "tree_sha": "b" * 40,
        "status": "",
    }
    monkeypatch.setattr(
        "universal_coding_agent.testlab.trusted_test_pause_live._source_snapshot",
        lambda _root: dict(snapshot),
    )
    runner = SafeTestRunner(
        adapter_module_path=module,
        pausable_factory_name="create_pausable_test",
    )

    summary = run_trusted_test_pause_live(
        tmp_path / "state",
        runner,
        source_root=tmp_path,
        stable_pause_seconds=0.05,
    )

    assert summary["qualified"] is True
    assert summary["paused_before_window"] is True
    assert summary["paused_after_window"] is True
    assert summary["done_before_window"] is False
    assert summary["done_after_window"] is False
    assert summary["test_succeeded"] is True
    assert summary["profile_completed"] is True
    assert summary["durable_report_reloaded"] is True
    assert summary["source"]["source_preserved"] is True
