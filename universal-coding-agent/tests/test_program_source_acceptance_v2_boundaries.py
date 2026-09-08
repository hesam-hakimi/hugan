"""Remaining recorded-reader, authority and schema boundaries for acceptance v2."""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest
from test_program_continuation_dispatch import admit, approve, consumer, dispatch, prepare
from test_program_source_acceptance_v2 import counts, decide, preview, service
from test_program_source_acceptance_v2 import qualified as qualified
from test_program_source_dispatch import close


@pytest.mark.parametrize("damage", [False, True])
def test_a04_a12_closed_foundation_complete_history_is_required(tmp_path, damage):
    operation, receipt = prepare(tmp_path, foundation="closed")
    f = consumer(tmp_path)
    try:
        parked = dispatch(f, operation, admit(f, operation, receipt))
        completed = approve(f, operation, parked)
    finally:
        close(f)
    f = service(tmp_path)
    try:
        candidate = preview(f, operation, completed)
        if damage:
            f.store.connection.execute(
                "DELETE FROM program_continuation_requests WHERE rowid="
                "(SELECT min(rowid) FROM program_continuation_requests)"
            )
            with pytest.raises(ValueError):
                decide(f, candidate)
            assert counts(f) == (1, 0, 1)
        else:
            assert decide(f, candidate)["status"] == "accepted"
            status = f.acceptance2.source_transition_status(f.identity.program_id)
            assert status["generation"] == 2 and status["execution_authorized"] is False
    finally:
        close(f)


def test_a10_standalone_reads_are_inert_and_do_not_import_execution(qualified, tmp_path):
    f, operation, completed = qualified
    candidate = preview(f, operation, completed)
    accepted = decide(f, candidate)
    (tmp_path / "source" / "app.py").write_text("later filesystem drift\n")
    database = f.store.programs.database_path
    before = hashlib.sha256(database.read_bytes()).hexdigest()
    script = """
import json,sys
from pathlib import Path
from universal_coding_agent.product.program_source_acceptance_v2_status import (
    source_transition_status, request_result)
path, host, program = sys.argv[1:]
status = source_transition_status(Path(path), program)
result = request_result(Path(path), host, program, 'accept-44')
assert status['generation'] == 2 and result['status'] == 'accepted'
for key in ('source_bytes_verified','filesystem_verified','current_authority_verified',
            'execution_authorized','automatic_execution','materialization_ready'):
    assert status[key] is False
for name in sys.modules:
    assert name not in {
        'universal_coding_agent.safe_service',
        'universal_coding_agent.product.program_source_acceptance',
        'universal_coding_agent.product.program_orchestrator',
        'universal_coding_agent.product.program_continuation_dispatch'}
print(json.dumps(result, sort_keys=True))
"""
    child = subprocess.run(
        [
            sys.executable,
            "-c",
            script,
            str(database),
            f.acceptance2.host_sha256,
            f.identity.program_id,
        ],
        text=True,
        capture_output=True,
        timeout=10,
        env={**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parent.parent / "src")},
    )
    assert child.returncode == 0, child.stderr
    assert json.loads(child.stdout) == accepted
    assert hashlib.sha256(database.read_bytes()).hexdigest() == before
    from universal_coding_agent.product.program_source_acceptance_v2_status import (
        source_transition_status,
    )

    absent = tmp_path / "absent.sqlite"
    with pytest.raises(FileNotFoundError):
        source_transition_status(absent, f.identity.program_id)
    assert not absent.exists() and counts(f) == (2, 0, 2)


@pytest.mark.parametrize("alias", ["main", "control", "lifecycle", "safe", "remote"])
def test_a06_a11_changed_store_inode_denies_new_claim(qualified, alias):
    f, operation, completed = qualified
    path = Path(dict(zip(f.v3.db.aliases, f.v3.db.identities, strict=True))[alias][0])
    backup = path.with_suffix(".original")
    path.rename(backup)
    path.write_bytes(backup.read_bytes())
    try:
        with pytest.raises(ValueError, match="identity changed"):
            preview(f, operation, completed)
    finally:
        path.unlink()
        backup.rename(path)
    assert counts(f) == (1, 0, 1)


@pytest.mark.parametrize("lock", ["registration", "program", "sql"])
def test_a11_lock_contention_is_bounded_before_claim(qualified, lock):
    f, operation, completed = qualified
    ready, release = threading.Event(), threading.Event()

    def hold():
        if lock == "sql":
            with sqlite3.connect(f.store.programs.database_path, isolation_level=None) as db:
                db.execute("BEGIN IMMEDIATE")
                ready.set()
                release.wait(10)
                db.rollback()
        else:
            mutex = (
                f.store.safe.control.cancellation._lock
                if lock == "registration"
                else f.workspace.programs._lock
            )
            with mutex:
                ready.set()
                release.wait(10)

    thread = threading.Thread(target=hold)
    thread.start()
    assert ready.wait(2)
    started = time.monotonic()
    try:
        with pytest.raises((ValueError, sqlite3.OperationalError)):
            preview(f, operation, completed)
        assert time.monotonic() - started < 7
    finally:
        release.set()
        thread.join(timeout=2)
    assert counts(f) == (1, 0, 1)


@pytest.mark.parametrize(
    "target", ["source_unique", "candidate_index", "request_index", "trigger", "view"]
)
def test_a11_changed_ledger_schema_or_indexes_deny(qualified, target):
    f, operation, completed = qualified
    db = f.store.connection
    if target == "source_unique":
        db.execute("ALTER TABLE program_source_acceptances RENAME TO accepted_original")
        db.execute("CREATE TABLE program_source_acceptances AS SELECT * FROM accepted_original")
    elif target in {"candidate_index", "request_index"}:
        table = (
            "program_source_candidates_v2"
            if target == "candidate_index"
            else "program_source_requests_v2"
        )
        db.execute(f"CREATE INDEX unexpected_source_index ON {table}(program_id)")
    elif target == "trigger":
        db.execute(
            "CREATE TRIGGER unexpected_source_trigger AFTER INSERT ON program_source_artifacts "
            "BEGIN UPDATE programs SET status='running'; END"
        )
    else:
        db.execute("ALTER TABLE program_source_candidates_v2 RENAME TO old_candidates")
        db.execute("CREATE VIEW program_source_candidates_v2 AS SELECT * FROM old_candidates")
    with pytest.raises((ValueError, sqlite3.DatabaseError)):
        preview(f, operation, completed)
    assert (
        f.workspace.lifecycle_reservations.connection.execute(
            "SELECT count(*) FROM lifecycle_worker_ownership"
        ).fetchone()[0]
        == 0
    )


def test_a11_capture_budget_includes_repeated_file_reads_and_child_settlement(tmp_path):
    from universal_coding_agent.product.program_source_capture_budget import CaptureBudget

    path = tmp_path / "bounded.txt"
    path.write_bytes(b"12345")
    budget = CaptureBudget(maximum=11)
    with budget.activate():
        assert budget.read_artifact(tmp_path, Path("bounded.txt"), 5) == b"12345"
        assert budget.read_artifact(tmp_path, Path("bounded.txt"), 5) == b"12345"
        with pytest.raises(ValueError, match="budget"):
            budget.read_artifact(tmp_path, Path("bounded.txt"), 5)
    budget = CaptureBudget(seconds=-1)
    with pytest.raises(ValueError, match="time budget"):
        budget.settled()
    budget = CaptureBudget()
    budget.children.add(123)
    with pytest.raises(ValueError, match="unsettled"):
        budget.settled()


@pytest.mark.parametrize("limit", ["capture", "output", "deadline"])
def test_a11_actual_read_only_git_child_is_bounded_and_settled(qualified, limit):
    f, _, _ = qualified
    from universal_coding_agent.product.program_source_attestation import _GitBudget
    from universal_coding_agent.product.program_source_capture_budget import CaptureBudget

    budget = CaptureBudget(maximum=32 if limit == "capture" else 256_000_000)
    git_budget = _GitBudget(
        time.monotonic() + (-1 if limit == "deadline" else 5), 1 if limit == "output" else 1_000_000
    )
    with budget.activate():
        with pytest.raises(ValueError):
            f.store.attestor._run(("rev-parse", "HEAD"), b"", git_budget)
        assert not budget.children
    assert counts(f) == (1, 0, 1)
