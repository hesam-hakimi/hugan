from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from universal_coding_agent.testlab.hard_reasoning import (
    hard_initial_files,
    hard_reference_files,
    hard_test_script,
)


def _write_fixture(root: Path, files: dict[str, str]) -> None:
    for relative, content in files.items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def _run_hidden_contract(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-c", hard_test_script()],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )


def test_hard_reasoning_initial_fixture_is_not_already_correct(tmp_path: Path) -> None:
    _write_fixture(tmp_path, hard_initial_files())

    result = _run_hidden_contract(tmp_path)

    assert result.returncode != 0


def test_hard_reasoning_contract_has_a_known_valid_solution(tmp_path: Path) -> None:
    _write_fixture(tmp_path, hard_reference_files())

    result = _run_hidden_contract(tmp_path)

    assert result.returncode == 0, result.stderr


def test_hard_reasoning_accepts_equivalent_version_wording(tmp_path: Path) -> None:
    files = hard_reference_files()
    files["docs/cdc_contract.md"] = files["docs/cdc_contract.md"].replace(
        "Candidate versions less than or equal to stored versions are stale and ignored.",
        "Winning candidates mutate stored state only when strictly newer; "
        "equal or older versions are ignored.",
    )
    _write_fixture(tmp_path, files)

    result = _run_hidden_contract(tmp_path)

    assert result.returncode == 0, result.stderr


def test_hard_reasoning_requires_stored_version_documentation(tmp_path: Path) -> None:
    files = hard_reference_files()
    files["docs/cdc_contract.md"] = files["docs/cdc_contract.md"].replace(
        "- Candidate versions less than or equal to stored versions are stale and ignored.\n",
        "",
    )
    _write_fixture(tmp_path, files)

    result = _run_hidden_contract(tmp_path)

    assert result.returncode != 0
    assert "AssertionError" in result.stderr


@pytest.mark.parametrize("comparison", ["<", "=="])
def test_hard_reasoning_rejects_equal_or_older_state_mutations(
    tmp_path: Path, comparison: str
) -> None:
    files = hard_reference_files()
    files["cdc_engine.py"] = files["cdc_engine.py"].replace(
        "candidate_version <= version_of(current)",
        f"candidate_version {comparison} version_of(current)",
    )
    files["docs/cdc_contract.md"] = files["docs/cdc_contract.md"].replace(
        "less than or equal to stored versions are stale and ignored",
        "equal or older than stored versions are ignored",
    )
    _write_fixture(tmp_path, files)

    result = _run_hidden_contract(tmp_path)

    assert result.returncode != 0
    assert "AssertionError" in result.stderr
