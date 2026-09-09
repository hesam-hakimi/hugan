from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path

import pytest
from test_program_execution import (
    RecordingDiscoveredSafeExecutor,
    _provider,
    _requirement,
    _start_next,
)

from universal_coding_agent.product.lifecycle_reservations import DurableLifecycleReservationStore
from universal_coding_agent.product.program_continuation_handoff import (
    MAX_RECORD_BYTES,
    SCHEMA,
    ProgramContinuationHandoffStore,
)
from universal_coding_agent.product.program_orchestrator import ProgramOrchestrator
from universal_coding_agent.product.search_service import SearchService
from universal_coding_agent.product.task_control import TaskControlService
from universal_coding_agent.storage.artifacts import ArtifactStore

PROGRAM = "program-execution"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


@contextmanager
def host(root, *, create=False, with_task=False):
    root = Path(root)
    control = TaskControlService(root / "control.sqlite")
    lifecycle = DurableLifecycleReservationStore(root / "lifecycle.sqlite")
    search = SearchService(root / "search.sqlite")
    programs = ProgramOrchestrator(
        root / "program.sqlite", ArtifactStore(root / "artifacts"), _provider(), search, control
    )
    try:
        if create:
            requirement = _requirement()
            plan = programs.create_program(
                program_id=PROGRAM,
                requirement=requirement,
                requirement_hash=requirement.canonical_hash(),
            )
            programs.approve_program(PROGRAM, plan.canonical_hash())
            if with_task:
                # Actual Program orchestration writes the execution/Task control
                # rows; the deterministic port does no provider, Git or Safe work.
                from types import SimpleNamespace

                _start_next(
                    SimpleNamespace(programs=programs),
                    PROGRAM,
                    requirement.canonical_hash(),
                    RecordingDiscoveredSafeExecutor(),
                )
        store = ProgramContinuationHandoffStore(programs, lifecycle, host_id="host-local")
        yield store
    finally:
        programs.close()
        control.close()
        lifecycle.close()
        search.close()


def descriptor(store):
    program = store.programs.connection.execute(
        "SELECT requirement_hash,plan_hash FROM programs WHERE program_id=?", (PROGRAM,)
    ).fetchone()
    execution = store.programs.connection.execute(
        "SELECT task_id,thread_id FROM program_executions WHERE program_id=?", (PROGRAM,)
    ).fetchone()
    return {
        "schema": SCHEMA,
        "program_id": PROGRAM,
        "phase_id": "phase-1",
        "task_id": execution[0] if execution else "",
        "thread_id": execution[1] if execution else "",
        "requirement_sha256": program[0],
        "plan_sha256": program[1],
        "source_generation": None,
        "source_sha256": "",
        "acceptance_receipt_sha256": "",
        "admission_sha256": "",
        "checkpoint_sha256": "",
        "result_sha256": "",
        "approval_core_sha256": "",
        "next_action": "foundation_only",
        "execution_authorized": False,
        "consumer_bound": False,
    }


def expected(result, request_id):
    public = result.public if hasattr(result, "public") else result
    return {
        "request_id": request_id,
        "expected_epoch": public["receipt"]["epoch"],
        "expected_receipt_sha256": public["receipt_sha256"],
    }


def claim_arguments(result, request_id="request-claim"):
    public = result.public if hasattr(result, "public") else result
    return {
        **expected(public, request_id),
        "descriptor_sha256": sha(canonical(public["receipt"]["descriptor"])),
        "proposal_sha256": public["proposal_sha256"],
        "confirmed": True,
    }


def create(store):
    token = store.lifecycle.reserve_program_worker(PROGRAM)
    result = store.create(
        PROGRAM,
        request_id="request-create",
        owner_token=token,
        descriptor=canonical(descriptor(store)),
    )
    return result, token


def park(store, result, token, request_id="request-park"):
    return store.park(PROGRAM, **expected(result, request_id), owner_token=token)


def owners(store):
    return store.lifecycle.connection.execute("SELECT * FROM lifecycle_worker_ownership").fetchall()


def protected(store):
    """All existing Program/control rows, including source and dispatch if present."""
    result = {}
    for name, service in (("program", store.programs), ("control", store.programs.control)):
        for (table,) in service.connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ):
            if not table.startswith("program_continuation_"):
                result[name, table] = service.connection.execute(
                    f'SELECT * FROM "{table}"'
                ).fetchall()
    return result


@pytest.fixture
def runtime(tmp_path):
    with host(tmp_path, create=True, with_task=True) as store:
        yield store


def test_atomic_handoff_preserves_existing_rows_and_redacts_every_public_result(runtime):
    before = protected(runtime)
    initial, token = create(runtime)
    original = owners(runtime)[0]
    assert protected(runtime) == before
    assert initial.owner_token is None
    parked = park(runtime, initial, token)
    assert not owners(runtime)
    assert protected(runtime) == before
    claimed = runtime.claim(PROGRAM, **claim_arguments(parked))
    assert claimed.owner_token and claimed.owner_token != token
    assert owners(runtime)[0] != original
    assert claimed.public["receipt"]["epoch"] == 1
    assert protected(runtime) == before
    replay = runtime.claim(PROGRAM, **claim_arguments(parked))
    assert replay.public == claimed.public and replay.owner_token is None
    assert runtime.request_result(PROGRAM, "request-claim") == claimed.public
    assert len(owners(runtime)) == 1
    closed = runtime.close(
        PROGRAM, **expected(claimed, "request-close"), owner_token=claimed.owner_token
    )
    assert not owners(runtime) and protected(runtime) == before
    assert (
        runtime.close(
            PROGRAM, **expected(claimed, "request-close"), owner_token=claimed.owner_token
        ).public
        == closed.public
    )
    status = runtime.status(PROGRAM)
    assert status["state"] == "closed" and status["blockers"] == []
    assert [r["receipt"]["sequence"] for r in status["receipts"]] == [1, 2, 3, 4]
    for public in (initial.public, parked.public, claimed.public, closed.public, status):
        assert public["execution_authorized"] is False and public["consumer_bound"] is False
        assert token not in json.dumps(public) and claimed.owner_token not in json.dumps(public)
    assert token not in repr(initial) and claimed.owner_token not in repr(claimed)
    raw = b"".join(
        row[0]
        for row in runtime.programs.connection.execute(
            "SELECT content FROM program_continuation_receipts"
        )
    )
    assert token.encode() not in raw and claimed.owner_token.encode() not in raw


def test_status_and_unknown_request_are_read_only_and_do_not_initialize(runtime):
    def files():
        return {path: path.read_bytes() for path in runtime.paths}

    before, rows = files(), protected(runtime)
    assert runtime.status(PROGRAM)["state"] == "uninitialized"
    unknown = runtime.request_result(PROGRAM, "request-unknown")
    assert unknown["request_status"] == "unknown" and unknown["diagnosis_required"]
    assert files() == before and protected(runtime) == rows
    initial, token = create(runtime)
    park(runtime, initial, token)
    before, rows = files(), protected(runtime)
    runtime.status(PROGRAM, limit=1)
    runtime.request_result(PROGRAM, "request-park")
    assert files() == before and protected(runtime) == rows


CHILD = r"""
import json, os, sys
from test_program_continuation_handoff import host, PROGRAM
configuration = json.loads(sys.stdin.readline())
with host(configuration["root"]) as store:
    print("ready", flush=True)
    command = json.loads(sys.stdin.readline())
    def boundary(name):
        if name == configuration.get("crash"):
            os._exit(73)
    store._boundary = boundary
    if "descriptor" in command:
        command["descriptor"] = command["descriptor"].encode()
    try:
        result = getattr(store, configuration["action"])(PROGRAM, **command)
        print(json.dumps({"public": result.public, "private": result.owner_token}), flush=True)
    except ValueError as error:
        print(json.dumps({"error": str(error)}), flush=True)
"""


def process(store, action, arguments, crash=""):
    environment = {
        **os.environ,
        "PYTHONPATH": os.pathsep.join(
            (str(Path(__file__).resolve().parent), str(Path(__file__).resolve().parents[1] / "src"))
        ),
    }
    child = subprocess.Popen(
        [sys.executable, "-c", CHILD],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=environment,
    )
    configuration = {"root": str(store.paths[0].parent), "action": action, "crash": crash}
    child.stdin.write(json.dumps(configuration) + "\n")
    child.stdin.flush()
    assert child.stdout.readline().strip() == "ready"
    return child, json.dumps(arguments) + "\n"


def finish(child, command, *, expected_code=0):
    stdout, stderr = child.communicate(command, timeout=30)
    assert child.returncode == expected_code, stderr
    return json.loads(stdout) if stdout else None


def test_fresh_process_claim_and_close_and_competing_claims(runtime):
    before = protected(runtime)
    initial, token = create(runtime)
    parker, command = process(
        runtime, "park", {**expected(initial, "request-park"), "owner_token": token}
    )
    parked = finish(parker, command)["public"]
    first, first_command = process(runtime, "claim", claim_arguments(parked, "request-first"))
    second, second_command = process(runtime, "claim", claim_arguments(parked, "request-second"))
    first.stdin.write(first_command)
    first.stdin.flush()
    second.stdin.write(second_command)
    second.stdin.flush()
    results = [finish(first, ""), finish(second, "")]
    winners = [r for r in results if "public" in r]
    assert len(winners) == 1 and len(owners(runtime)) == 1
    assert sum("error" in r for r in results) == 1
    winner = winners[0]
    assert winner["private"] != token
    child, command = process(
        runtime,
        "close",
        {**expected(winner["public"], "request-close"), "owner_token": winner["private"]},
    )
    assert finish(child, command)["public"]["receipt"]["state"] == "closed"
    assert not owners(runtime) and protected(runtime) == before


CRASH_CASES = [
    (action, boundary)
    for action in ("create", "park", "claim", "close")
    for boundary in (
        "after_receipt",
        "after_request",
        "after_head",
        "before_commit",
        "after_commit",
        "after_worker",
    )
    if action != "create" or boundary != "after_worker"
]


@pytest.mark.parametrize(("action", "boundary"), CRASH_CASES)
@pytest.mark.parametrize("control_mode", ["DELETE", "WAL"])
def test_process_death_at_real_transaction_boundaries(runtime, action, boundary, control_mode):
    runtime.programs.control.connection.execute("PRAGMA journal_mode=" + control_mode)
    if action == "create":
        token = runtime.lifecycle.reserve_program_worker(PROGRAM)
        arguments = {
            "request_id": "request-create",
            "owner_token": token,
            "descriptor": canonical(descriptor(runtime)).decode(),
        }
    else:
        initial, token = create(runtime)
        if action == "claim":
            stopped = park(runtime, initial, token)
            arguments = claim_arguments(stopped)
        else:
            arguments = {**expected(initial, "request-" + action), "owner_token": token}
    before, old_owner = protected(runtime), owners(runtime)
    old_status = runtime.status(PROGRAM)
    child, command = process(runtime, action, arguments, boundary)
    finish(child, command, expected_code=73)
    # Reopen actual stores in a new process and in a fresh host; SQLite performs
    # hot/super-journal recovery. Observe BOTH databases, not just the head row.
    with host(runtime.paths[0].parent) as reopened:
        status = reopened.status(PROGRAM)
        recorded = reopened.request_result(PROGRAM, "request-" + action)
        if boundary != "after_commit":
            assert owners(reopened) == old_owner and status == old_status
            assert recorded["request_status"] == "unknown"
        else:
            assert recorded["request_status"] == "completed"
            if action in {"park", "close"}:
                assert not owners(reopened)
            elif action == "claim":
                assert len(owners(reopened)) == 1 and owners(reopened) != old_owner
                replay = reopened.claim(PROGRAM, **arguments)
                assert replay.public == recorded and replay.owner_token is None
                with pytest.raises(ValueError):
                    reopened.claim(PROGRAM, **{**arguments, "request_id": "request-new"})
            else:
                assert owners(reopened) == old_owner
            retry = {**arguments}
            if "descriptor" in retry:
                retry["descriptor"] = retry["descriptor"].encode()
            replay = getattr(reopened, action)(PROGRAM, **retry)
            assert replay.public == recorded and replay.owner_token is None
        assert protected(reopened) == before


@pytest.mark.parametrize("conflict", ["remote-program", "remote-task", "control", "standalone"])
def test_claim_excludes_actual_lifecycle_actions_and_task_workers(runtime, conflict):
    initial, token = create(runtime)
    stopped = park(runtime, initial, token)
    task = descriptor(runtime)["task_id"]
    if conflict == "remote-program":
        runtime.lifecycle.reserve_remote_operation("task-other", program_id=PROGRAM)
    elif conflict == "remote-task":
        runtime.lifecycle.reserve_remote_operation(task)
    elif conflict == "control":
        runtime.lifecycle.reserve_program_control(PROGRAM, task_ids=(task,))
    else:
        runtime.lifecycle.reserve_standalone_worker(task)
    before = owners(runtime), protected(runtime)
    with pytest.raises(ValueError, match="active"):
        runtime.claim(PROGRAM, **claim_arguments(stopped))
    assert (owners(runtime), protected(runtime)) == before
    assert runtime.status(PROGRAM)["blockers"]


@pytest.mark.parametrize(
    "change",
    [
        "requirement",
        "plan",
        "phase",
        "execution",
        "program-control",
        "task-control",
        "pause",
        "cancel",
        "realign",
        "source",
        "v2",
    ],
)
def test_actual_semantic_changes_invalidate_parked_proposal(runtime, change):
    initial, token = create(runtime)
    stopped = park(runtime, initial, token)
    programs, control = runtime.programs, runtime.programs.control
    if change in {"requirement", "plan"}:
        field = "requirement_hash" if change == "requirement" else "plan_hash"
        programs.connection.execute(f"UPDATE programs SET {field}=?", ("e" * 64,))
        programs.connection.commit()
    elif change in {"phase", "execution"}:
        table = "program_phases" if change == "phase" else "program_executions"
        programs.connection.execute(f"UPDATE {table} SET result_ref='artifact://changed/result'")
        programs.connection.commit()
    elif change in {"program-control", "task-control"}:
        entity = "program" if change == "program-control" else "task"
        control.connection.execute(
            "UPDATE control_state SET revision=revision+1 WHERE entity_type=?", (entity,)
        )
        control.connection.commit()
    elif change == "pause":
        programs.pause(PROGRAM, reason="explicit pause")
    elif change == "cancel":
        programs.cancel(PROGRAM, reason="explicit cancellation")
    elif change == "realign":
        programs.require_realign(PROGRAM, "d" * 64)
    elif change == "source":
        source_head(runtime)
    else:
        control.connection.execute(
            "INSERT INTO uca_source_dispatch_tasks VALUES (?, ?, ?, ?)",
            (descriptor(runtime)["task_id"], descriptor(runtime)["thread_id"], "e" * 64, "f" * 64),
        )
        control.connection.commit()
    before = protected(runtime)
    with pytest.raises(ValueError):
        runtime.claim(PROGRAM, **claim_arguments(stopped))
    assert not owners(runtime) and protected(runtime) == before
    assert "semantic_inputs_changed" in runtime.status(PROGRAM)["blockers"]


def source_head(store):
    # Exact existing acceptance head schema. Its hashes are metadata references;
    # this test deliberately does not pretend to prove source bytes or acceptance.
    connection = store.programs.connection
    connection.execute("""CREATE TABLE program_source_heads (
        program_id TEXT PRIMARY KEY, generation INTEGER NOT NULL,
        source_sha256 TEXT NOT NULL, host_sha256 TEXT NOT NULL,
        initial_receipt_sha256 TEXT NOT NULL, receipt_sha256 TEXT NOT NULL)""")
    connection.execute(
        "INSERT INTO program_source_heads VALUES (?, 1, ?, ?, ?, ?)",
        (PROGRAM, "a" * 64, "b" * 64, "c" * 64, "d" * 64),
    )
    connection.commit()


def test_source_descriptor_binds_actual_generation_and_acceptance_head(runtime):
    source_head(runtime)
    token = runtime.lifecycle.reserve_program_worker(PROGRAM)
    description = {
        **descriptor(runtime),
        "source_generation": 1,
        "source_sha256": "a" * 64,
        "acceptance_receipt_sha256": "d" * 64,
    }
    before = protected(runtime)
    initial = runtime.create(
        PROGRAM, request_id="request-create", owner_token=token, descriptor=canonical(description)
    )
    stopped = park(runtime, initial, token)
    assert protected(runtime) == before
    runtime.programs.connection.execute("UPDATE program_source_heads SET generation=2")
    runtime.programs.connection.commit()
    with pytest.raises(ValueError):
        runtime.claim(PROGRAM, **claim_arguments(stopped))
    assert not owners(runtime)


def test_exact_request_reuse_epoch_owner_and_confirmation(runtime):
    initial, token = create(runtime)
    with pytest.raises(ValueError, match="different content"):
        runtime.create(
            PROGRAM,
            request_id="request-create",
            owner_token="f" * 32,
            descriptor=canonical(descriptor(runtime)),
        )
    for changes in (
        {"owner_token": "f" * 32},
        {"expected_epoch": 1},
        {"expected_receipt_sha256": "f" * 64},
    ):
        with pytest.raises(ValueError):
            runtime.park(
                PROGRAM, **{**expected(initial, "request-bad"), "owner_token": token, **changes}
            )
    stopped = park(runtime, initial, token)
    for changes in (
        {"confirmed": False},
        {"confirmed": 1},
        {"expected_epoch": True},
        {"proposal_sha256": "e" * 64},
        {"descriptor_sha256": "f" * 64},
    ):
        with pytest.raises(ValueError):
            runtime.claim(PROGRAM, **{**claim_arguments(stopped), **changes})
    claimed = runtime.claim(PROGRAM, **claim_arguments(stopped))
    before = owners(runtime)
    with pytest.raises(ValueError):
        runtime.close(PROGRAM, **expected(claimed, "request-close"), owner_token=token)
    with pytest.raises(ValueError, match="different content"):
        runtime.claim(PROGRAM, **{**claim_arguments(stopped), "proposal_sha256": "e" * 64})
    assert owners(runtime) == before


def test_administrative_recovery_leaves_blocker_and_never_rebinds(runtime):
    initial, token = create(runtime)
    candidate = runtime.lifecycle.recovery_snapshot()[0][0]
    runtime.lifecycle.recover(
        target_type=candidate.target_type,
        target_kind=candidate.target_kind,
        scope_id=candidate.scope_id,
        recovery_ref=candidate.recovery_ref,
        reason="explicit crashed-owner diagnosis",
        confirmed=True,
    )
    assert not owners(runtime)
    status = runtime.status(PROGRAM)
    assert status["state"] == "owned" and status["blockers"] == ["recovery_required"]
    assert runtime.request_result(PROGRAM, "request-create") == initial.public
    with pytest.raises(ValueError):
        park(runtime, initial, token)
    fresh = runtime.lifecycle.reserve_program_worker(PROGRAM)
    with pytest.raises(ValueError, match="owner witness"):
        park(runtime, initial, fresh)
    assert runtime.status(PROGRAM)["blockers"] == ["recovery_required"]


@pytest.mark.parametrize(
    "bad", ["missing", "bytes", "duplicate", "unknown", "types", "head", "request", "predecessor"]
)
def test_receipt_and_request_corruption_fails_closed(runtime, bad):
    initial, token = create(runtime)
    stopped = park(runtime, initial, token)
    connection = runtime.programs.connection
    digest = stopped.public["receipt_sha256"]
    if bad == "missing":
        connection.execute(
            "DELETE FROM program_continuation_receipts WHERE receipt_sha256=?",
            (initial.public["receipt_sha256"],),
        )
    elif bad == "head":
        connection.execute("UPDATE program_continuation_heads SET epoch=9")
    elif bad == "request":
        connection.execute("UPDATE program_continuation_requests SET request_sha256=?", ("a" * 64,))
    else:
        receipt = stopped.public["receipt"]
        if bad == "bytes":
            content = b"{}"
        elif bad == "duplicate":
            content = b'{"schema":"duplicate",' + canonical(receipt)[1:]
        else:
            if bad == "unknown":
                receipt["success"] = True
            elif bad == "types":
                receipt["epoch"] = False
            else:
                receipt["predecessor_sha256"] = "a" * 64
            content = canonical(receipt)
        new_digest = sha(content)
        connection.execute(
            "UPDATE program_continuation_receipts SET content=?,receipt_sha256=? "
            "WHERE receipt_sha256=?",
            (content, new_digest, digest),
        )
        connection.execute("UPDATE program_continuation_heads SET receipt_sha256=?", (new_digest,))
        connection.execute(
            "UPDATE program_continuation_requests SET receipt_sha256=? "
            "WHERE request_id='request-park'",
            (new_digest,),
        )
    connection.commit()
    with pytest.raises(ValueError):
        runtime.status(PROGRAM)
    with pytest.raises(ValueError):
        runtime.claim(PROGRAM, **claim_arguments(stopped))
    assert not owners(runtime)


@pytest.mark.parametrize(
    "bad",
    [
        "too-large",
        "depth",
        "duplicate",
        "unknown",
        "schema",
        "bool",
        "int",
        "float",
        "id",
        "hash",
        "effect",
        "noncanonical",
    ],
)
def test_bounded_strict_descriptor_rejects_before_state_mutation(runtime, bad):
    description = descriptor(runtime)
    if bad == "too-large":
        data = b" " * (MAX_RECORD_BYTES + 1)
    elif bad == "depth":
        data = b'{"schema":' + b"[" * 100 + b"0" + b"]" * 100 + b"}"
    elif bad == "duplicate":
        data = b'{"schema":"duplicate",' + canonical(description)[1:]
    elif bad == "noncanonical":
        data = json.dumps(description).encode()
    else:
        key, value = {
            "unknown": ("outcome", "succeeded"),
            "schema": ("schema", "uca-program-source-dispatch-3"),
            "bool": ("source_generation", True),
            "int": ("source_generation", "1"),
            "float": ("source_generation", 1.0),
            "id": ("task_id", "x" * 129),
            "hash": ("plan_sha256", "A" * 64),
            "effect": ("execution_authorized", True),
        }[bad]
        description[key] = value
        data = canonical(description)
    before = protected(runtime)
    token = runtime.lifecycle.reserve_program_worker(PROGRAM)
    with pytest.raises(ValueError):
        runtime.create(PROGRAM, request_id="request-create", owner_token=token, descriptor=data)
    assert runtime.status(PROGRAM)["state"] == "uninitialized"
    assert len(owners(runtime)) == 1 and protected(runtime) == before


@pytest.mark.parametrize(
    ("index", "pragma"),
    [
        (index, pragma)
        for index in (0, 2)
        for pragma in (
            "journal_mode=WAL",
            "journal_mode=OFF",
            "journal_mode=MEMORY",
            "synchronous=0",
            "synchronous=1",
        )
    ],
)
def test_incompatible_writer_durability_fails_without_changing_settings(runtime, index, pragma):
    initial, token = create(runtime)
    runtime.stores[index].connection.execute("PRAGMA " + pragma)
    before = owners(runtime), protected(runtime)
    with pytest.raises(ValueError, match="rollback journals"):
        park(runtime, initial, token)
    assert (owners(runtime), protected(runtime)) == before
    key, value = pragma.split("=")
    observed = runtime.stores[index].connection.execute("PRAGMA " + key).fetchone()[0]
    assert str(observed).lower() == value.lower()


def test_host_and_replaced_database_are_not_rebound(runtime, tmp_path):
    initial, token = create(runtime)
    wrong = ProgramContinuationHandoffStore(
        runtime.programs, runtime.lifecycle, host_id="wrong-host"
    )
    with pytest.raises(ValueError, match="host"):
        wrong.status(PROGRAM)
    path = runtime.paths[2]
    data = path.read_bytes()
    path.rename(tmp_path / "old-lifecycle.sqlite")
    path.write_bytes(data)
    with pytest.raises(ValueError, match="identity changed"):
        runtime.status(PROGRAM)
    with pytest.raises(ValueError, match="identity changed"):
        park(runtime, initial, token)


def test_metadata_bounds_pagination_and_in_progress_diagnosis(runtime):
    initial, token = create(runtime)
    stopped = park(runtime, initial, token)
    first = runtime.status(PROGRAM, limit=1)
    assert len(first["receipts"]) == 1 and first["next_sequence"] == 1
    second = runtime.status(PROGRAM, after_sequence=1, limit=1)
    assert len(second["receipts"]) == 1 and second["next_sequence"] is None
    for limit in (0, True, 101):
        with pytest.raises(ValueError):
            runtime.status(PROGRAM, limit=limit)
    connection = runtime.programs.connection
    connection.execute(
        "INSERT INTO program_continuation_requests VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (runtime.host_sha256, PROGRAM, "request-inflight", "a" * 64, "claim", 1, "in_progress", ""),
    )
    connection.commit()
    result = runtime.request_result(PROGRAM, "request-inflight")
    assert result["request_status"] == "in_progress" and result["diagnosis_required"]
    with pytest.raises(ValueError):
        runtime.claim(PROGRAM, **claim_arguments(stopped, "request-inflight"))
    connection.execute(
        "UPDATE program_continuation_receipts SET content=zeroblob(?) WHERE receipt_sha256=?",
        (MAX_RECORD_BYTES + 1, stopped.public["receipt_sha256"]),
    )
    connection.commit()
    with pytest.raises(ValueError, match="byte bound"):
        runtime.status(PROGRAM)


def test_excessive_existing_rows_and_fields_fail_before_materialization(runtime):
    initial, token = create(runtime)
    stopped = park(runtime, initial, token)
    connection = runtime.programs.connection
    connection.executemany(
        "INSERT INTO program_phases VALUES (?, ?, 'pending', '', '')",
        [(PROGRAM, f"phase-extra-{index}") for index in range(100)],
    )
    connection.commit()
    with pytest.raises(ValueError, match="row set"):
        runtime.claim(PROGRAM, **claim_arguments(stopped))
    connection.execute("DELETE FROM program_phases WHERE phase_id LIKE 'phase-extra-%'")
    connection.execute("UPDATE program_phases SET summary_ref=?", ("x" * (2 * MAX_RECORD_BYTES),))
    connection.commit()
    with pytest.raises(ValueError, match="byte bound"):
        runtime.status(PROGRAM)
    assert not owners(runtime)


def test_real_aggregate_budget_precedes_large_execution_materialization(runtime):
    initial, token = create(runtime)
    stopped = park(runtime, initial, token)
    connection = runtime.programs.connection
    cursor = connection.execute("SELECT * FROM program_executions LIMIT 1")
    fields = [column[0] for column in cursor.description]
    template = dict(zip(fields, cursor.fetchone(), strict=True))
    for index in range(60):
        row = {
            **template,
            "task_id": f"task-extra-{index}",
            "thread_id": f"thread-extra-{index}",
            "unit_key": f"unit-extra-{index}",
        }
        for field in (
            "result_ref",
            "phase_report_ref",
            "error_ref",
            "accepted_evidence_ref",
            "remote_disposition_ref",
        ):
            row[field] = "x" * 4096
        connection.execute(
            "INSERT INTO program_executions ("
            + ",".join(fields)
            + ") VALUES ("
            + ",".join("?" for _ in fields)
            + ")",
            tuple(row.values()),
        )
    connection.commit()
    with pytest.raises(ValueError, match="aggregate"):
        runtime.claim(PROGRAM, **claim_arguments(stopped))
    assert not owners(runtime)


def test_current_control_store_binding_and_task_conflicts_are_rechecked(runtime, tmp_path):
    initial, token = create(runtime)
    task_id = descriptor(runtime)["task_id"]
    runtime.lifecycle.reserve_standalone_worker(task_id)
    before = owners(runtime)
    with pytest.raises(ValueError, match="ownership differs"):
        park(runtime, initial, token)
    assert owners(runtime) == before
    original = runtime.programs.control
    other = TaskControlService(tmp_path / "other-control.sqlite")
    try:
        runtime.programs.control = other
        with pytest.raises(ValueError, match="host store binding"):
            runtime.status(PROGRAM)
    finally:
        runtime.programs.control = original
        other.close()


def test_mutation_validates_older_chain_and_triggers_cannot_change_program_rows(runtime):
    initial, token = create(runtime)
    stopped = park(runtime, initial, token)
    claimed = runtime.claim(PROGRAM, **claim_arguments(stopped))
    stopped = park(runtime, claimed, claimed.owner_token, "request-park-again")
    connection = runtime.programs.connection
    connection.execute(
        "DELETE FROM program_continuation_receipts WHERE receipt_sha256=?",
        (initial.public["receipt_sha256"],),
    )
    connection.commit()
    with pytest.raises(ValueError, match="receipt is missing"):
        runtime.claim(PROGRAM, **claim_arguments(stopped, "request-claim-again"))
    assert not owners(runtime)
    # Restore the exact immutable initial bytes, then inject an unsolicited SQL
    # trigger. Even a valid next transition may only write its allowlisted tables.
    connection.execute(
        "INSERT INTO program_continuation_receipts VALUES (?, ?, 1, ?)",
        (initial.public["receipt_sha256"], PROGRAM, canonical(initial.public["receipt"])),
    )
    connection.execute("""CREATE TRIGGER forbidden_effect AFTER INSERT
        ON program_continuation_receipts BEGIN
        UPDATE program_phases SET status='completed'; END""")
    connection.commit()
    before = protected(runtime)
    with pytest.raises(ValueError, match="explicit diagnosis"):
        runtime.claim(PROGRAM, **claim_arguments(stopped, "request-claim-again"))
    assert protected(runtime) == before and not owners(runtime)


CONTROL_WRITER = r"""
import json, sqlite3, sys
from pathlib import Path
from universal_coding_agent.product.models import ControlEntityType
from universal_coding_agent.product.task_control import TaskControlService
control = TaskControlService(Path(sys.argv[1]))
control.connection.execute("PRAGMA busy_timeout=150")
print("ready", flush=True)
sys.stdin.readline()
try:
    control.request_pause(ControlEntityType.PROGRAM, "program-execution", reason="concurrent pause")
    print(json.dumps({"committed": True}), flush=True)
except sqlite3.OperationalError as error:
    print(json.dumps({"committed": False, "error": str(error)}), flush=True)
finally:
    control.close()
"""


@pytest.mark.parametrize("mode", ["DELETE", "WAL"])
@pytest.mark.parametrize("action", ["create", "park", "claim", "close"])
def test_every_handoff_commit_excludes_real_concurrent_control_writers(runtime, mode, action):
    from universal_coding_agent.product.models import ControlEntityType

    control = runtime.programs.control
    control.connection.execute("PRAGMA journal_mode=" + mode)
    if action == "create":
        token = runtime.lifecycle.reserve_program_worker(PROGRAM)
        arguments = {
            "request_id": "request-create",
            "owner_token": token,
            "descriptor": canonical(descriptor(runtime)),
        }
    else:
        initial, token = create(runtime)
        if action == "claim":
            stopped = park(runtime, initial, token)
            arguments = claim_arguments(stopped)
        else:
            arguments = {**expected(initial, "request-" + action), "owner_token": token}
    # Construct the competing actual service BEFORE the handoff starts, so a
    # constructor/schema lock cannot accidentally stand in for the control CAS.
    child = subprocess.Popen(
        [sys.executable, "-c", CONTROL_WRITER, str(runtime.paths[1])],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert child.stdout.readline().strip() == "ready"
    observations = []

    def boundary(name):
        if name == "before_commit":
            stdout, stderr = child.communicate("pause\n", timeout=10)
            assert child.returncode == 0, stderr
            observations.append(json.loads(stdout))

    runtime._boundary = boundary
    before = protected(runtime)
    try:
        result = getattr(runtime, action)(PROGRAM, **arguments)
    finally:
        if child.poll() is None:
            child.kill()
            child.communicate()
        runtime._boundary = lambda _name: None
    assert observations == [{"committed": False, "error": "database is locked"}]
    assert protected(runtime) == before
    assert runtime.status(PROGRAM)["blockers"] == []
    assert control.connection.execute("PRAGMA journal_mode").fetchone()[0] == mode.lower()
    # Lock exclusion ends at the commit boundary, not by disabling Program control.
    control.request_pause(ControlEntityType.PROGRAM, PROGRAM, reason="explicit later pause")
    assert "semantic_inputs_changed" in runtime.status(PROGRAM)["blockers"]
    assert runtime.request_result(PROGRAM, "request-" + action) == result.public


def test_import_has_no_effectful_modules_and_control_checkpoint_bytes_are_unchanged(
    runtime, tmp_path
):
    # The actual SQLite checkpointer remains completely outside this foundation.
    from langgraph.checkpoint.sqlite import SqliteSaver

    checkpoint_path = tmp_path / "checkpoint.sqlite"
    with sqlite3.connect(checkpoint_path) as connection:
        SqliteSaver(connection).setup()
    before = checkpoint_path.read_bytes()
    initial, token = create(runtime)
    stopped = park(runtime, initial, token)
    claimed = runtime.claim(PROGRAM, **claim_arguments(stopped))
    runtime.close(PROGRAM, **expected(claimed, "request-close"), owner_token=claimed.owner_token)
    assert checkpoint_path.read_bytes() == before
    probe = """
import sys
import universal_coding_agent.product.program_continuation_handoff
for name in sys.modules:
    assert not any(part in name for part in (
        'safe_service', 'solution_discovery', 'program_source_dispatch', 'program_orchestrator',
        'providers.', 'sandbox.', 'subprocess', 'web.app'))
print('provider-free import PASS')
"""
    result = subprocess.run(
        [sys.executable, "-c", probe], check=True, capture_output=True, text=True
    )
    assert result.stdout.strip() == "provider-free import PASS"
