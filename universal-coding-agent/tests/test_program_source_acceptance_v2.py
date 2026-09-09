"""A01–A12: actual two-phase fixtures and bounded source acceptance failures."""

from __future__ import annotations

import json
import os
import signal
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

import pytest
from test_program_continuation_dispatch import admit, approve, consumer, dispatch, prepare
from test_program_source_dispatch import close

from universal_coding_agent.product.program_source_acceptance_v2 import (
    ProgramSourceAcceptanceV2Service,
)


def service(root, *, protocol="v1"):
    f = consumer(root, protocol=protocol)
    f.acceptance2 = ProgramSourceAcceptanceV2Service(f.v3)
    return f


def preview(f, operation, terminal, request_id="preview-44"):
    head = f.store.current(f.identity.program_id)
    return f.acceptance2.preview_source_transition(
        f.identity.program_id,
        operation,
        request_id=request_id,
        terminal_receipt_sha256=terminal["receipt_sha256"],
        before_sha256=f.store.source.snapshot_hash(head),
        generation=head.generation,
    )


def decide(f, result, *, approved=True, request_id="accept-44", **changes):
    candidate = result["candidate"]
    args = {
        k: candidate[k]
        for k in (
            "revision",
            "core_sha256",
            "transition_sha256",
            "before_sha256",
            "generation",
            "predecessor_receipt_sha256",
            "terminal_receipt_sha256",
        )
    }
    args.update(
        candidate_sha256=result["candidate_sha256"],
        request_id=request_id,
        approval_id="source-44",
        approved=approved,
    )
    args.update(changes)
    return f.acceptance2.decide_source_transition(
        candidate["program_id"], candidate["operation_id"], **args
    )


def terminal(root, *, object_format="sha1", protocol="v1"):
    operation, receipt = prepare(root, object_format=object_format, protocol=protocol)
    f = consumer(root, protocol=protocol)
    try:
        parked = dispatch(f, operation, admit(f, operation, receipt))
    finally:
        close(f)
    f = consumer(root, protocol=protocol)
    try:
        completed = approve(f, operation, parked)
        assert completed["terminal_status"] == "completed"
    finally:
        close(f)
    return operation, completed


def child(root, action, *, protocol="v1", object_format="sha1", crash="", request=""):
    """An actual OS invocation; only fixture input/output JSON crosses the boundary."""
    return subprocess.run(
        [
            sys.executable,
            str(Path(__file__).resolve()),
            str(root),
            action,
            protocol,
            object_format,
            crash,
            request,
        ],
        env={
            **os.environ,
            "PYTHONPATH": os.pathsep.join(
                (
                    str(Path(__file__).resolve().parent.parent / "src"),
                    str(Path(__file__).resolve().parent),
                )
            ),
        },
        text=True,
        capture_output=True,
        timeout=60,
    )


def child_main():
    root, action, protocol, object_format, crash, request = sys.argv[1:]
    root = Path(root)
    if action == "park":
        operation, receipt = prepare(root, object_format=object_format, protocol=protocol)
        f = consumer(root, protocol=protocol)
        try:
            result = dispatch(f, operation, admit(f, operation, receipt))
        finally:
            close(f)
    else:
        f = service(root, protocol=protocol)
        try:
            if crash:

                def boundary(name):
                    if name == crash:
                        (root / "crash-ready").write_text(name)
                        while True:
                            signal.pause()

                f.acceptance2.db.boundary = boundary
            if request:
                print("ready", flush=True)
                sys.stdin.readline()
            if action == "terminal":
                parked = json.loads((root / "result-park.json").read_text())
                result = approve(f, parked["operation_id"], parked)
            elif action == "preview":
                terminal = json.loads((root / "result-terminal.json").read_text())
                result = preview(
                    f, terminal["operation_id"], terminal, request_id=request or "preview-44"
                )
            elif action == "legacy":
                prepared = json.loads((root / "result-preview.json").read_text())
                result = f.store.accept(
                    prepared["candidate_sha256"],
                    approved_transition_sha256=prepared["candidate"]["transition_sha256"],
                    approval_id="legacy-race",
                    owner_token=f.owner,
                )
            else:
                prepared = json.loads((root / "result-preview.json").read_text())
                result = decide(
                    f, prepared, approved=action != "reject", request_id=request or "accept-44"
                )
        finally:
            close(f)
    (root / ("result-" + action + ("-" + request if request else "") + ".json")).write_text(
        json.dumps(result)
    )


@pytest.mark.parametrize(
    "object_format,protocol", [("sha1", "v1"), ("sha256", "v2-line-addressed")]
)
def test_a01_a02_real_os_restart_at_every_handoff(tmp_path, object_format, protocol):
    for action in ("park", "terminal", "preview", "accept"):
        result = child(tmp_path, action, protocol=protocol, object_format=object_format)
        assert result.returncode == 0, result.stderr
    f = service(tmp_path, protocol=protocol)
    try:
        prepared = json.loads((tmp_path / "result-preview.json").read_text())
        accepted = json.loads((tmp_path / "result-accept.json").read_text())
        pw = json.loads(f.store._get(prepared["witness_sha256"]))
        aw = json.loads(f.store._get(accepted["witness_sha256"]))
        assert pw["owner_sha256"] != aw["owner_sha256"]
        assert pw["core_sha256"] == aw["core_sha256"] == prepared["candidate"]["core_sha256"]
        assert "owner_token" not in json.dumps((prepared, accepted, pw, aw))
        assert f.store.current(f.identity.program_id).generation == 2
    finally:
        close(f)


@pytest.fixture
def qualified(tmp_path):
    operation, completed = terminal(tmp_path)
    f = service(tmp_path)
    try:
        yield f, operation, completed
    finally:
        close(f)


def counts(f):
    return (
        f.store.current(f.identity.program_id).generation,
        f.workspace.lifecycle_reservations.connection.execute(
            "SELECT count(*) FROM lifecycle_worker_ownership"
        ).fetchone()[0],
        f.store.connection.execute("SELECT count(*) FROM program_source_acceptances").fetchone()[0],
    )


def test_a03_a10_exact_replay_conflict_rejection_and_later_drift(qualified, tmp_path):
    f, operation, completed = qualified
    prepared = preview(f, operation, completed)
    assert preview(f, operation, completed) == prepared
    with pytest.raises(ValueError):
        preview(f, operation, completed, request_id="another-preview")
    with pytest.raises(ValueError):
        decide(f, prepared, core_sha256="0" * 64)
    assert counts(f) == (1, 0, 1)
    rejected = decide(f, prepared, approved=False)
    assert rejected["status"] == "rejected" and counts(f) == (1, 0, 1)
    with pytest.raises(ValueError):
        decide(f, prepared, approved=True)
    with pytest.raises(ValueError):
        decide(f, prepared, approved=True, request_id="new-decision")
    (tmp_path / "source" / "app.py").write_text("drift after historical rejection\n")
    assert decide(f, prepared, approved=False) == rejected
    assert preview(f, operation, completed) == prepared
    assert f.acceptance2.source_transition_status(f.identity.program_id)["generation"] == 1


@pytest.mark.parametrize(
    "field",
    [
        "candidate_sha256",
        "revision",
        "core_sha256",
        "transition_sha256",
        "before_sha256",
        "generation",
        "predecessor_receipt_sha256",
        "terminal_receipt_sha256",
        "approved",
    ],
)
def test_a03_every_exact_decision_binding_denies_before_claim(qualified, field):
    f, operation, completed = qualified
    prepared = preview(f, operation, completed)
    value = 2 if field in {"revision", "generation"} else (1 if field == "approved" else "0" * 64)
    with pytest.raises(ValueError):
        decide(f, prepared, **{field: value})
    assert counts(f) == (1, 0, 1)


@pytest.mark.parametrize(
    "target",
    [
        "old_request",
        "park_request",
        "terminal_request",
        "old_receipt",
        "terminal_receipt",
        "authority",
        "settlement",
        "first_approval",
        "first_candidate",
        "base_intent",
        "material_completion",
        "registry",
        "safe_guard",
        "root_locator",
    ],
)
def test_a04_full_historical_proof_missing_parts_deny(qualified, tmp_path, target):
    f, operation, completed = qualified
    db = f.store.connection
    row = f.v3._row(operation)
    admission = f.v3._admission(row)
    if target.endswith("request"):
        request = {
            "old_request": "admit-43",
            "park_request": "discover-43",
            "terminal_request": "scope-44",
        }[target]
        db.execute(
            "DELETE FROM program_source_continuation_requests_v3 WHERE request_id=?", (request,)
        )
    elif target in {"old_receipt", "terminal_receipt"}:
        db.execute(
            "DELETE FROM program_source_continuation_receipts_v3 WHERE sequence=?",
            (1 if target == "old_receipt" else 3,),
        )
    elif target == "registry":
        db.execute("DELETE FROM control.uca_source_dispatch_tasks_v3")
    elif target == "safe_guard":
        db.execute("DELETE FROM safe.uca_source_dispatch_tasks_v3_guard")
    elif target == "root_locator":
        (tmp_path / "safe" / "source-dispatch-v3-root.json").unlink()
    else:
        first = json.loads(f.store._get(admission["acceptance_receipt_sha256"]))
        digest = {
            "authority": row["authority_sha256"],
            "settlement": row["settlement_sha256"],
            "first_approval": first["approval_sha256"],
            "first_candidate": first["candidate_sha256"],
            "base_intent": admission["preparation_row"]["intent_sha256"],
            "material_completion": admission["materialization_row"]["completion_sha256"],
        }[target]
        db.execute("DELETE FROM program_source_artifacts WHERE sha256=?", (digest,))
    with pytest.raises((ValueError, OSError, sqlite3.Error)):
        preview(f, operation, completed)
    assert counts(f) == (1, 0, 1)


@pytest.mark.parametrize(
    "target",
    [
        "tests",
        "review",
        "provenance",
        "final_report",
        "scope",
        "patch",
        "validation",
        "program_report",
        "phase_result",
        "retained",
        "origin",
    ],
)
def test_a05_actual_evidence_is_recaptured_after_preview(qualified, tmp_path, target):
    f, operation, completed = qualified
    prepared = preview(f, operation, completed)
    row = f.v3._row(operation)
    state = f.store.safe.graph.get_state({"configurable": {"thread_id": row["thread_id"]}}).values
    if target == "retained":
        path = Path(state["sandbox_path"]) / "app.py"
    elif target == "origin":
        path = tmp_path / "source" / "app.py"
    elif target in {"program_report", "phase_result"}:
        prefix = f.v3._result_prefix(f.identity.program_id, row["phase_id"], row["task_id"], state)
        path = (
            f.store.programs.artifacts.root
            / prefix
            / ("phase-execution-report.json" if target == "program_report" else "phase-result.json")
        )
    else:
        key = {
            "tests": "tests_ref",
            "review": "review_ref",
            "provenance": "review_provenance_ref",
            "final_report": "final_report_ref",
            "scope": "scope_approval_ref",
            "patch": "patch_ref",
            "validation": "patch_validation_ref",
        }[target]
        path = f.store.safe.artifacts._path_for(state[key])
    path.write_bytes(path.read_bytes() + b"\nchanged\n")
    with pytest.raises((ValueError, OSError)):
        decide(f, prepared)
    assert counts(f) == (1, 1, 1)


@pytest.mark.parametrize("target", ["control", "checkpoint", "source", "retained"])
def test_a06_writer_wins_after_capture_blocks_final_commit(qualified, target):
    f, operation, completed = qualified
    prepared = preview(f, operation, completed)
    row = f.v3._row(operation)

    def boundary(name):
        if name != "capture_returned":
            return
        if target == "control":
            connection = f.workspace.control.connection
            connection.execute(
                "UPDATE control_state SET revision=revision+1 WHERE entity_type='program'"
            )
            connection.commit()
        elif target == "checkpoint":
            f.store.safe.connection.execute(
                "UPDATE checkpoints SET metadata=? WHERE thread_id=?", (b"{}", row["thread_id"])
            )
            f.store.safe.connection.commit()
        elif target == "source":
            f.workspace.programs.connection.execute(
                "UPDATE program_source_heads SET receipt_sha256=?", ("0" * 64,)
            )
            f.workspace.programs.connection.commit()
        else:
            path = f.v3.preparation.filesystem.root / ("execution-" + operation) / "repo" / "app.py"
            path.write_bytes(path.read_bytes() + b"\n")

    f.acceptance2.db.boundary = boundary
    with pytest.raises((ValueError, OSError)):
        decide(f, prepared)
    assert counts(f) == (1, 1, 1)


@pytest.mark.parametrize("alias", ["control", "safe", "remote"])
def test_a06_wal_writers_excluded_through_commit(qualified, alias):
    f, operation, completed = qualified
    index = {"control": 1, "safe": 4, "remote": 3}[alias]
    path = f.v3.db.identities[index][0]
    with sqlite3.connect(path, isolation_level=None) as writer:
        writer.execute("PRAGMA journal_mode=WAL")
    observations = []

    def boundary(name):
        if name not in {"final_before_commit", "after_worker_release"}:
            return
        with sqlite3.connect(path, isolation_level=None, timeout=0.01) as writer:
            with pytest.raises(sqlite3.OperationalError, match="locked"):
                writer.execute("BEGIN IMMEDIATE")
            observations.append(name)

    f.acceptance2.db.boundary = boundary
    prepared = preview(f, operation, completed)
    assert decide(f, prepared)["status"] == "accepted"
    assert observations == ["after_worker_release", "final_before_commit"] * 2


def launch(root, action, *, crash="", request=""):
    return subprocess.Popen(
        [
            sys.executable,
            str(Path(__file__).resolve()),
            str(root),
            action,
            "v1",
            "sha1",
            crash,
            request,
        ],
        env={
            **os.environ,
            "PYTHONPATH": os.pathsep.join(
                (
                    str(Path(__file__).resolve().parent.parent / "src"),
                    str(Path(__file__).resolve().parent),
                )
            ),
        },
        text=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


@pytest.mark.parametrize(
    "action,boundary",
    [
        ("preview", "claim_before_commit"),
        ("preview", "claim_after_commit"),
        ("preview", "capture_before_commit"),
        ("preview", "capture_returned"),
        ("preview", "after_response"),
        ("preview", "after_worker_release"),
        ("preview", "final_before_commit"),
        ("preview", "final_after_commit"),
        ("accept", "claim_before_commit"),
        ("accept", "claim_after_commit"),
        ("accept", "capture_before_commit"),
        ("accept", "capture_returned"),
        ("accept", "after_source_head"),
        ("accept", "after_response"),
        ("accept", "after_worker_release"),
        ("accept", "final_before_commit"),
        ("accept", "final_after_commit"),
        ("reject", "after_worker_release"),
        ("reject", "final_after_commit"),
    ],
)
def test_a08_external_sigkill_has_atomic_source_request_and_release(
    qualified, tmp_path, action, boundary
):
    f, operation, completed = qualified
    (tmp_path / "result-terminal.json").write_text(json.dumps(completed))
    if action != "preview":
        (tmp_path / "result-preview.json").write_text(json.dumps(preview(f, operation, completed)))
    process = launch(tmp_path, action, crash=boundary)
    try:
        deadline = time.monotonic() + 20
        while not (tmp_path / "crash-ready").exists() and process.poll() is None:
            assert time.monotonic() < deadline, "child did not reach external termination boundary"
            time.sleep(0.01)
        assert process.poll() is None, process.communicate(timeout=2)
        process.kill()
        process.communicate(timeout=5)
        assert process.returncode == -signal.SIGKILL
    finally:
        if process.poll() is None:
            process.kill()
            process.communicate(timeout=5)
    committed = boundary == "final_after_commit"
    expected_generation = 2 if committed and action == "accept" else 1
    claimed = boundary != "claim_before_commit"
    assert counts(f) == (expected_generation, int(claimed and not committed), expected_generation)
    request_id = "preview-44" if action == "preview" else "accept-44"
    if committed:
        # New OS process, immutable exact replay after response was lost.
        result = child(tmp_path, action)
        assert result.returncode == 0, result.stderr
        assert counts(f) == (expected_generation, 0, expected_generation)
    elif claimed:
        result = child(tmp_path, action)
        assert result.returncode != 0
        assert "pending source request" in result.stderr
        assert counts(f) == (1, 1, 1)
        status = f.acceptance2.source_transition_status(f.identity.program_id)
        assert {"request_id": request_id, "status": "pending"} in status["requests"]


@pytest.mark.parametrize(
    "actions",
    [("preview", "preview"), ("accept", "accept"), ("accept", "reject"), ("accept", "legacy")],
)
def test_a07_independent_processes_compete_for_one_task(qualified, tmp_path, actions):
    f, operation, completed = qualified
    (tmp_path / "result-terminal.json").write_text(json.dumps(completed))
    if actions[0] != "preview":
        (tmp_path / "result-preview.json").write_text(json.dumps(preview(f, operation, completed)))
    processes = [
        launch(tmp_path, action, request="race-" + str(i)) for i, action in enumerate(actions)
    ]
    try:
        for process in processes:
            assert process.stdout.readline().strip() == "ready"
        for process in processes:
            process.stdin.write("go\n")
            process.stdin.flush()
        outputs = [process.communicate(timeout=30) for process in processes]
        assert sorted(process.returncode == 0 for process in processes) == [False, True], outputs
        generation, workers, receipts = counts(f)
        assert workers == 0 and generation == receipts
        assert generation in ({1} if actions[0] == "preview" else {1, 2})
        assert (
            f.store.connection.execute(
                "SELECT count(*) FROM program_source_candidates_v2"
            ).fetchone()[0]
            == 1
        )
        assert f.store.connection.execute(
            "SELECT count(*) FROM program_source_decisions_v2"
        ).fetchone()[0] == int(actions[0] != "preview")
    finally:
        for process in processes:
            if process.poll() is None:
                process.kill()
                process.communicate(timeout=5)


@pytest.mark.parametrize(
    "case",
    [
        "oversize_checkpoint",
        "checkpoint_type",
        "checkpoint_id",
        "pending_write",
        "metadata_depth",
        "metadata_duplicate",
        "metadata_noncanonical",
        "metadata_aggregate",
        "history_rows",
        "capture_budget",
        "symlink",
        "extra_path",
        "origin_link_count",
    ],
)
def test_a09_a11_selected_bounds_and_filesystem_denials(qualified, tmp_path, case, monkeypatch):
    f, operation, completed = qualified
    from universal_coding_agent.product.program_source_capture_budget import CaptureBudget

    row = f.v3._row(operation)
    db = f.store.connection
    if case.startswith("metadata") or case == "history_rows":
        with f.acceptance2.db.transaction() as reader:
            if case == "history_rows":
                with pytest.raises(ValueError):
                    reader.rows("program_source_artifacts", ("sha256",), limit=1)
                return
            raw = {
                "metadata_depth": b'{"a":' * 9 + b"0" + b"}" * 9,
                "metadata_duplicate": b'{"a":1,"a":2}',
                "metadata_noncanonical": b'{ "a": 1 }',
                "metadata_aggregate": b"{}",
            }[case]
            digest = f.store._put(raw)
            if case == "metadata_aggregate":
                reader.total = 1_048_576
            with pytest.raises(ValueError):
                reader.metadata(digest)
        return
    if case == "capture_budget":
        monkeypatch.setattr(
            "universal_coding_agent.product.program_source_acceptance_v2.CaptureBudget",
            lambda: CaptureBudget(maximum=1024),
        )
    elif case in {"oversize_checkpoint", "checkpoint_type", "checkpoint_id"}:
        column, value = {
            "oversize_checkpoint": ("checkpoint", b"x" * 16_000_001),
            "checkpoint_type": ("checkpoint", "text checkpoint"),
            "checkpoint_id": ("checkpoint_id", "z" * 129),
        }[case]
        db.execute(
            f"UPDATE safe.checkpoints SET {column}=? WHERE thread_id=? AND checkpoint_id="
            "(SELECT max(checkpoint_id) FROM safe.checkpoints WHERE thread_id=?)",
            (value, row["thread_id"], row["thread_id"]),
        )
        monkeypatch.setattr(
            f.store.safe.graph, "get_state", lambda *a, **k: pytest.fail("decoder called")
        )
    elif case == "pending_write":
        db.execute(
            "INSERT INTO safe.writes"
            "(thread_id,checkpoint_ns,checkpoint_id,task_id,idx,channel,type,value) "
            "SELECT thread_id,'',checkpoint_id,'pending-test',0,'messages','msgpack',x'80' "
            "FROM safe.checkpoints WHERE thread_id=? ORDER BY checkpoint_id DESC LIMIT 1",
            (row["thread_id"],),
        )
    else:
        prepared = preview(f, operation, completed)
        source = tmp_path / "source"
        if case == "symlink":
            original = source / "app.py"
            original.rename(source / "actual.py")
            original.symlink_to("actual.py")
        elif case == "extra_path":
            (source / "extra.txt").write_text("unexpected")
        else:
            path = next(p for p in (source / ".git" / "objects").glob("*/*") if p.is_file())
            os.link(path, tmp_path / "extra-link")
        with pytest.raises((ValueError, OSError)):
            decide(f, prepared)
        assert counts(f) == (1, 1, 1)
        return
    with pytest.raises((ValueError, OSError)):
        preview(f, operation, completed)
    assert counts(f)[0::2] == (1, 1)


@pytest.mark.parametrize(
    "statement",
    [
        "PRAGMA safe.user_version=44",
        "PRAGMA control.application_id=44",
        "PRAGMA remote.journal_mode=DELETE",
        "UPDATE programs SET status='running'",
        "DELETE FROM program_source_artifacts",
        "UPDATE control.control_state SET revision=99",
        "CREATE TABLE injected(x)",
        "DROP TABLE program_source_acceptances",
    ],
)
def test_a11_acceptance_authorizer_denies_extra_effects(qualified, statement):
    f, _, _ = qualified
    with f.acceptance2.db.transaction():
        with pytest.raises(sqlite3.DatabaseError):
            f.store.connection.execute(statement)
    assert counts(f) == (1, 0, 1)


@pytest.mark.parametrize("phase", ["before_claim", "after_preview", "after_acceptance"])
def test_a12_old_routes_never_accept_candidate_two_or_materialize_receipt_two(qualified, phase):
    f, operation, completed = qualified
    if phase == "before_claim":
        owner = f.workspace.lifecycle_reservations.reserve_program_worker(f.identity.program_id)
        try:
            source = f.store.current(f.identity.program_id)
            with pytest.raises(ValueError):
                f.store.prepare(
                    f.identity.program_id,
                    task_id=f.v3._row(operation)["task_id"],
                    owner_token=owner,
                    expected_source_sha256=f.store.source.snapshot_hash(source),
                    expected_generation=1,
                )
        finally:
            f.workspace.lifecycle_reservations.release_program_worker(f.identity.program_id, owner)
    else:
        prepared = preview(f, operation, completed)
        accepted = decide(f, prepared) if phase == "after_acceptance" else None
        owner = f.workspace.lifecycle_reservations.reserve_program_worker(f.identity.program_id)
        try:
            with pytest.raises(ValueError):
                f.store.accept(
                    prepared["candidate_sha256"],
                    approved_transition_sha256=prepared["candidate"]["transition_sha256"],
                    approval_id="old-route",
                    owner_token=owner,
                )
            if accepted:
                with pytest.raises(ValueError):
                    f.base.materialization.begin(
                        f.identity.program_id,
                        acceptance_receipt_sha256=accepted["receipt_sha256"],
                        owner_token=owner,
                    )
        finally:
            f.workspace.lifecycle_reservations.release_program_worker(f.identity.program_id, owner)


@pytest.mark.parametrize(
    "object_format,protocol", [("sha1", "v1"), ("sha256", "v2-line-addressed")]
)
def test_a01_actual_completed_44_accepts_generation_two(tmp_path, object_format, protocol):
    operation, completed = terminal(tmp_path, object_format=object_format, protocol=protocol)
    f = service(tmp_path, protocol=protocol)
    try:
        calls = (tmp_path / "calls.jsonl").read_bytes()
        prepared = preview(f, operation, completed)
        assert f.store.current(f.identity.program_id).generation == 1
        assert not f.workspace.lifecycle_reservations.connection.execute(
            "SELECT * FROM lifecycle_worker_ownership"
        ).fetchall()
        close(f)
        f = service(tmp_path, protocol=protocol)
        accepted = decide(f, prepared)
        assert accepted["status"] == "accepted"
        assert f.store.current(f.identity.program_id).generation == 2
        assert b"return 44" in next(
            x.content for x in f.store.current(f.identity.program_id).files if x.path == "app.py"
        )
        assert (tmp_path / "calls.jsonl").read_bytes() == calls
        assert not f.workspace.lifecycle_reservations.connection.execute(
            "SELECT * FROM lifecycle_worker_ownership"
        ).fetchall()
        assert decide(f, prepared) == accepted
        status = f.acceptance2.source_transition_status(f.identity.program_id)
        assert status["generation"] == 2
        assert [r["schema"] for r in status["lineage"]] == [
            "uca-source-acceptance-receipt-1",
            "uca-source-acceptance-receipt-2",
        ]
        assert status["current_authority_verified"] is False
    finally:
        close(f)


@pytest.mark.parametrize("failure", ["scope", "tests", "review", "conditional"])
def test_a09_actual_unqualified_execution_never_admits_source_preview(tmp_path, failure):
    operation, receipt = prepare(tmp_path)
    f = consumer(tmp_path)
    try:
        parked = dispatch(f, operation, admit(f, operation, receipt))
        if failure == "tests":
            original = f.provider._handlers["implementer"]

            def incorrect(request):
                result = original(request)
                result["edits"][0]["replacements"][0]["new_text"] = "return 99"
                return result

            f.provider._handlers["implementer"] = incorrect
        elif failure in {"review", "conditional"}:
            f.provider._handlers["reviewer"] = lambda _: {
                "verdict": "FAIL" if failure == "review" else "PASS_WITH_CONDITIONS",
                "required_actions": ["Do not accept this fixture."],
                "confidence": "high",
            }
        completed = approve(f, operation, parked, approved=failure != "scope")
        assert completed["terminal_status"] != "completed"
        f.acceptance2 = ProgramSourceAcceptanceV2Service(f.v3)
        with pytest.raises(ValueError):
            preview(f, operation, completed)
        assert counts(f) == (1, 0, 1)
        assert (
            b"return 43"
            in (
                f.v3.preparation.filesystem.root / ("execution-" + operation) / "repo" / "app.py"
            ).read_bytes()
        )
    finally:
        close(f)


@pytest.mark.parametrize("target", ["worker", "handle", "remote", "policy", "plan", "recovery"])
def test_a02_a06_a09_current_exclusions_and_drift(qualified, target):
    f, operation, completed = qualified
    prepared = preview(f, operation, completed)
    task = f.v3._row(operation)["task_id"]
    token = None
    if target in {"worker", "recovery"}:
        token = f.workspace.lifecycle_reservations.reserve_program_worker(f.identity.program_id)
        if target == "recovery":
            recovery = f.workspace.lifecycle_reservations.recovery_snapshot()[0][0]
            f.workspace.lifecycle_reservations.recover(
                target_type=recovery.target_type,
                target_kind=recovery.target_kind,
                scope_id=recovery.scope_id,
                recovery_ref=recovery.recovery_ref,
                reason="Explicit fixture recovery after owner loss.",
                confirmed=True,
            )
            token = None
    elif target == "handle":
        f.store.safe.control.cancellation._processes[task] = {object()}
    elif target == "remote":
        f.store.connection.execute(
            """INSERT INTO remote.remote_operation_leases VALUES
            (?,?, 'fixture','fixture','fixture','opaque-ref','base','now','now',
            'running','running',0,0,0,0,'start')""",
            (task, f.v3._row(operation)["thread_id"]),
        )
    elif target == "policy":
        f.store.trusted_policy = f.store.trusted_policy.model_copy(update={"profiles": ()})
    elif target == "plan":
        f.store.connection.execute("UPDATE programs SET plan_hash=?", ("0" * 64,))
    try:
        with pytest.raises(ValueError):
            decide(f, prepared)
        assert counts(f) == (1, int(target == "worker"), 1)
    finally:
        if token:
            f.workspace.lifecycle_reservations.release_program_worker(f.identity.program_id, token)
        if target == "handle":
            f.store.safe.control.cancellation._processes.pop(task)


@pytest.mark.parametrize(
    "boundary",
    ["after_source_head", "after_response", "after_worker_release", "final_before_commit"],
)
def test_a06_filesystem_drift_at_final_writes_rolls_back_every_effect(qualified, boundary):
    f, operation, completed = qualified
    prepared = preview(f, operation, completed)
    original = f.store.attestor.root / "app.py"

    def change(name):
        if name == boundary:
            original.write_bytes(original.read_bytes() + b"\nlate drift\n")

    f.acceptance2.db.boundary = change
    with pytest.raises(ValueError):
        decide(f, prepared)
    assert counts(f) == (1, 1, 1)
    assert (
        f.store.connection.execute("SELECT count(*) FROM program_source_decisions_v2").fetchone()[0]
        == 0
    )


def test_a01_host_composition_returns_at_each_explicit_action(tmp_path):
    from test_program_source_dispatch import runtime

    from universal_coding_agent.core.models import RepositorySpec
    from universal_coding_agent.discovered_safe_service import DiscoveredSafeAgentService
    from universal_coding_agent.product.program_continuation_dispatch import (
        ProgramContinuationDispatchService,
    )
    from universal_coding_agent.product.program_source_transition_host import (
        ProgramSourceTransitionHost,
    )

    f = runtime(tmp_path, 42, create=True)
    try:
        f.workspace.lifecycle_reservations.release_program_worker(f.identity.program_id, f.owner)
        port = DiscoveredSafeAgentService.create(
            tmp_path / "safe",
            f.provider,
            allow_local_sources=True,
            control=f.workspace.control,
            remote_operations=f.workspace.remote_operations,
        )
        v3 = ProgramContinuationDispatchService(
            f.base,
            f.provider,
            lifecycle=f.workspace.lifecycle_reservations,
            transport_id="fixture-synchronous",
        )
        host = ProgramSourceTransitionHost(
            v3,
            first_phase_executor=port,
            repository=RepositorySpec(url=str(f.source), base_ref="fixture"),
        )
        program = f.identity.program_id
        first = host.start_first_phase(program)
        assert f.store.current(program).generation == 0
        host.decide_first_phase_scope(program, first.task_id, approved=True)
        before = f.store.current(program)
        proposal = host.preview_first_phase_source(
            program, first.task_id, before_sha256=f.store.source.snapshot_hash(before), generation=0
        )
        first_receipt = host.accept_first_phase_source(
            program,
            candidate_sha256=proposal["candidate_sha256"],
            transition_sha256=proposal["transition_sha256"],
            approval_id="explicit-source-43",
        )
        assert counts(f) == (1, 0, 1)
    finally:
        close(f)
    f = consumer(tmp_path)
    try:
        host = ProgramSourceTransitionHost(f.v3, first_phase_executor=None, repository=None)
        from universal_coding_agent.product.program_continuation_execution_store import (
            canonical,
            sha,
        )

        admitted = host.prepare_continuation(
            program,
            acceptance_receipt_sha256=sha(canonical(first_receipt)),
            request_id="admit-host",
        )
        assert admitted["state"] == "admitted" and counts(f) == (1, 1, 1)
        parked = host.dispatch_continuation(
            program,
            admitted["operation_id"],
            request_id="dispatch-host",
            admission_sha256=admitted["admission_sha256"],
            expected_epoch=admitted["epoch"],
            expected_receipt_sha256=admitted["receipt_sha256"],
        )
        assert parked["state"] == "parked_scope" and counts(f) == (1, 0, 1)
    finally:
        close(f)
    f = service(tmp_path)
    try:
        host = ProgramSourceTransitionHost(f.v3, first_phase_executor=None, repository=None)
        completed = host.decide_continuation_scope(
            program,
            parked["operation_id"],
            request_id="scope-host",
            admission_sha256=parked["admission_sha256"],
            expected_epoch=parked["epoch"],
            expected_receipt_sha256=parked["receipt_sha256"],
            proposal_sha256=parked["proposal_sha256"],
            scope_sha256=parked["scope_sha256"],
            approval_id="scope-44",
            approved=True,
        )
        assert completed["terminal_status"] == "completed" and counts(f) == (1, 0, 1)
        prepared = host.preview_source_transition(
            program,
            parked["operation_id"],
            request_id="preview-host",
            terminal_receipt_sha256=completed["receipt_sha256"],
            before_sha256=f.store.source.snapshot_hash(f.store.current(program)),
            generation=1,
        )
        assert counts(f) == (1, 0, 1)
        assert decide(f, prepared)["status"] == "accepted" and counts(f) == (2, 0, 2)
    finally:
        close(f)


if __name__ == "__main__":
    child_main()
