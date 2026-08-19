from __future__ import annotations

from pathlib import Path

import pytest

from universal_coding_agent.testlab.synthetic import (
    failure_scenarios,
    run_synthetic_scenario,
    success_scenarios,
)


@pytest.mark.parametrize("scenario", success_scenarios(), ids=lambda item: item.scenario_id)
def test_pretransfer_success_scenarios(
    tmp_path: Path,
    scenario,
) -> None:
    result = run_synthetic_scenario(tmp_path, scenario)

    assert result.report["status"] == "completed"
    assert result.report["structured_edit_protocol"] == "v2-line-addressed"
    assert result.report["line_addressed_edits"] is True
    assert result.report["file_sharded_implementer"] is True
    assert result.report["source_repository_modified"] is False
    assert result.report["reviewer_verdict"] == "PASS"
    assert result.report["sandbox_patch_retained"] is True
    assert result.source_head_after == result.source_head_before
    assert result.source_status_after == ""

    for path, expected in result.expected_files.items():
        assert (result.sandbox / path).read_text(encoding="utf-8") == expected
        if path in scenario.initial_files:
            assert (result.source / path).read_text(encoding="utf-8") == scenario.initial_files[path]
        else:
            assert not (result.source / path).exists()

    if scenario.scenario_id == "address-correction":
        assert ("app.py", "initial") in result.phases
        assert ("app.py", "address_correction") in result.phases


@pytest.mark.parametrize("scenario", failure_scenarios(), ids=lambda item: item.scenario_id)
def test_pretransfer_failure_scenarios_fail_closed(
    tmp_path: Path,
    scenario,
) -> None:
    result = run_synthetic_scenario(tmp_path, scenario)

    assert result.report["status"] == scenario.expected_status
    assert result.report["source_repository_modified"] is False
    assert result.source_head_after == result.source_head_before
    assert result.source_status_after == ""

    if scenario.expected_safe_error is not None:
        assert scenario.expected_safe_error in result.report["safe_errors"]

    for path, original in scenario.initial_files.items():
        assert (result.source / path).read_text(encoding="utf-8") == original

    if scenario.scenario_id in {"invalid-address", "wrong-path"}:
        assert result.report["patch_ref"] is None
        assert result.report["tests_ref"] is None
        assert result.report["reviewer_verdict"] is None

    if scenario.scenario_id == "test-failure":
        assert result.report["rolled_back"] is True
        assert result.report["reviewer_verdict"] is None

    if scenario.scenario_id == "reviewer-fail":
        assert result.report["reviewer_verdict"] == "FAIL"
        assert result.report["rolled_back"] is True
