from __future__ import annotations

import subprocess
import sys
from pathlib import Path

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
