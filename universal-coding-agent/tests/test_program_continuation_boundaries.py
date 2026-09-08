"""Adversarial host, history, registration and legacy boundaries for the v3 consumer."""

from __future__ import annotations

import ast
import json
import os
import select
import sqlite3
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest
import test_program_continuation_dispatch as fixture

from universal_coding_agent.product.program_continuation_execution_store import (
    MAX_TOTAL,
    Reader,
    canonical,
    sha,
)

admitted = fixture.admitted


def owners(f):
    return f.workspace.lifecycle_reservations.connection.execute(
        "SELECT count(*) FROM lifecycle_worker_ownership"
    ).fetchone()[0]


@pytest.mark.parametrize("foundation", ["owned", "parked", "closed"])
def test_v08_d2a_records_are_inert_and_only_closed_history_allows_v3(tmp_path, foundation):
    operation, receipt = fixture.prepare(tmp_path, foundation=foundation)
    f = fixture.consumer(tmp_path)
    try:
        calls = (tmp_path / "calls.jsonl").read_bytes()
        if foundation == "closed":
            assert fixture.admit(f, operation, receipt)["state"] == "admitted"
        else:
            with pytest.raises(ValueError, match="d2a blocks v3"):
                fixture.admit(f, operation, receipt)
        assert (tmp_path / "calls.jsonl").read_bytes() == calls and owners(f) == 1
    finally:
        fixture.close(f)


@pytest.mark.parametrize("alias", ["main", "control", "lifecycle", "remote", "safe"])
def test_v11_replaced_original_store_inode_denies_before_a_fresh_claim(admitted, alias):
    f = admitted
    parked = fixture.dispatch(f, f.operation, f.admitted)
    path = Path(dict(zip(f.v3.db.aliases, f.v3.db.identities, strict=True))[alias][0])
    original = path.with_suffix(".original")
    path.rename(original)
    path.write_bytes(original.read_bytes())
    calls = (f.root / "calls.jsonl").read_bytes()
    try:
        with pytest.raises(ValueError, match="identity changed"):
            fixture.approve(f, f.operation, parked)
        assert calls == (f.root / "calls.jsonl").read_bytes() and owners(f) == 0
    finally:
        path.unlink()
        original.rename(path)


@pytest.mark.parametrize(
    "damage", ["request", "receipt", "response", "schema", "oversized", "head"]
)
def test_v10_missing_earlier_history_and_oversize_or_schema_drift_deny_effects(admitted, damage):
    f = admitted
    parked = fixture.dispatch(f, f.operation, f.admitted)
    db = f.store.connection
    if damage == "request":
        db.execute(
            "DELETE FROM program_source_continuation_requests_v3 WHERE request_id='admit-43'"
        )
    elif damage == "receipt":
        db.execute("DELETE FROM program_source_continuation_receipts_v3 WHERE sequence=1")
    elif damage in {"response", "oversized"}:
        digest = db.execute(
            "SELECT response_sha256 FROM program_source_continuation_requests_v3 "
            "WHERE request_id='admit-43'"
        ).fetchone()[0]
        if damage == "response":
            db.execute("DELETE FROM program_source_artifacts WHERE sha256=?", (digest,))
        else:
            db.execute(
                "UPDATE program_source_artifacts SET content=zeroblob(65537) WHERE sha256=?",
                (digest,),
            )
    elif damage == "schema":
        db.execute("ALTER TABLE program_source_continuation_heads_v3 ADD COLUMN unknown TEXT")
    else:
        db.execute("UPDATE program_source_continuation_heads_v3 SET state='unexpected'")
    calls = (f.root / "calls.jsonl").read_bytes()
    with pytest.raises(ValueError):
        fixture.approve(f, f.operation, parked)
    with pytest.raises(ValueError):
        f.v3.status(f.identity.program_id, f.operation)
    assert (f.root / "calls.jsonl").read_bytes() == calls and owners(f) == 0


def test_v10_blob_budget_is_checked_before_content_fetch(admitted):
    f = admitted
    raw = canonical(f.admitted)
    db = f.store.connection
    digest = sha(raw)
    queries = []
    db.set_trace_callback(queries.append)
    try:
        reader = Reader(db)
        reader.total = MAX_TOTAL - len(raw) + 1
        with pytest.raises(ValueError, match="aggregate"):
            reader.record(digest, f.admitted["schema"])
        assert not any("SELECT content FROM" in query for query in queries)
    finally:
        db.set_trace_callback(None)


@pytest.mark.parametrize("where", ["guard", "program", "control", "lifecycle", "safe", "remote"])
def test_v11_unexpected_triggers_cannot_write_unrelated_rows(admitted, where):
    f = admitted
    db = f.store.connection
    alias, table = {
        "guard": ("safe", "uca_source_dispatch_tasks_v3_guard"),
        "program": ("main", "program_source_continuation_heads_v3"),
        "control": ("control", "control_state"),
        "lifecycle": ("lifecycle", "lifecycle_worker_ownership"),
        "safe": ("safe", "checkpoints"),
        "remote": ("remote", "remote_operation_leases"),
    }[where]
    db.execute(f"CREATE TABLE {alias}.unrelated_probe(value TEXT)")
    db.execute(
        f"CREATE TRIGGER {alias}.unexpected_v3_probe AFTER INSERT ON {table} "
        "BEGIN INSERT INTO unrelated_probe VALUES ('mutated'); END"
    )
    if where == "guard":
        intent = f.v3._admission(f.v3._row(f.operation))
        with pytest.raises(ValueError, match="trigger"):
            f.v3._persist_guard(intent)
    elif where in {"safe", "remote"}:
        with f.v3.db.transaction():
            with pytest.raises(sqlite3.DatabaseError):
                db.execute(f"UPDATE {alias}.{table} SET rowid=rowid")
    else:
        with pytest.raises(ValueError, match="trigger"):
            fixture.dispatch(f, f.operation, f.admitted)
    assert db.execute(f"SELECT count(*) FROM {alias}.unrelated_probe").fetchone()[0] == 0
    assert owners(f) == 1


def test_v02_registration_racing_the_commit_waits_and_is_revoked(admitted):
    from universal_coding_agent.core.cancellation import OwnedOperationKind

    f = admitted
    started, done, result, threads = threading.Event(), threading.Event(), [], []

    def late(signal):
        started.set()
        try:
            with signal.operation(OwnedOperationKind.PROVIDER):
                result.append("entered")
        except RuntimeError:
            result.append("revoked")
        finally:
            done.set()

    def boundary(name):
        if name != "before_commit" or f.v3._row(f.operation)["state"] != "parked_scope":
            return
        live = f.v3._live[f.operation]
        signal = f.safe.control.cancellation.signal(live._context.task_id)
        thread = threading.Thread(target=late, args=(signal,))
        threads.append(thread)
        thread.start()
        assert started.wait(1)
        assert not done.wait(0.05), "registration crossed the settlement barrier"

    f.v3.db.boundary = boundary
    assert fixture.dispatch(f, f.operation, f.admitted)["state"] == "parked_scope"
    for thread in threads:
        thread.join(timeout=2)
    assert done.is_set() and result == ["revoked"] and owners(f) == 0


def test_v08_late_real_adapter_callbacks_and_reconstructed_adapters_have_no_authority(admitted):
    from universal_coding_agent.product.program_continuation_execution_adapter import (
        ContinuationSafeExecution,
    )

    f = admitted
    fixture.dispatch(f, f.operation, f.admitted)
    live = f.v3._live[f.operation]
    task = live.task()
    for action in (
        lambda: live.prepare(task.task_id, task.repository),
        lambda: live.read_only_git_checks(Path("/")),
        live.discovery_indexer,
        lambda: live.node("scope_approval", {}, lambda _: {}),
        lambda: live.entry(task.thread_id, task.task_id, "run"),
        live._drive,
    ):
        with pytest.raises((ValueError, RuntimeError)):
            action()
    recreated = ContinuationSafeExecution(f.v3, f.operation, f.owner, live.payload)
    with pytest.raises(ValueError, match="reconstructed"):
        recreated._drive()

    class Subclass(ContinuationSafeExecution):
        pass

    from universal_coding_agent.safe_service import SafeAgentService

    for wrong in (object(), Subclass(f.v3, f.operation, f.owner, live.payload)):
        with pytest.raises(ValueError):
            SafeAgentService.create(
                f.root / "safe",
                f.provider,
                control=f.safe.control,
                remote_operations=f.safe.remote_operations,
                execution_adapter=wrong,
            )
    assert owners(f) == 0


def test_v04_two_actual_process_claims_can_invoke_only_one_fresh_worker(admitted):
    f = admitted
    parked = fixture.dispatch(f, f.operation, f.admitted)
    code = """
import json,sys
from pathlib import Path
from test_program_continuation_dispatch import consumer,close
f=consumer(Path(sys.argv[1]))
print('ready',flush=True)
line=sys.stdin.readline()
p=json.loads(line)
try:
    result=f.v3.approve_scope(f.identity.program_id,sys.argv[2],request_id=sys.argv[3],
        admission_sha256=p['admission_sha256'],expected_epoch=p['epoch'],
        expected_receipt_sha256=p['receipt_sha256'],proposal_sha256=p['proposal_sha256'],
        scope_sha256=p['scope_sha256'],approval_id='race-scope-44',approved=True)
    print(json.dumps(result),flush=True)
except (ValueError,RuntimeError) as exc:
    print(json.dumps({'blocked':type(exc).__name__}),flush=True)
finally:
    close(f)
"""
    children = []
    try:
        for request in ("claim-left", "claim-right"):
            child = subprocess.Popen(
                [sys.executable, "-B", "-c", code, str(f.root), f.operation, request],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env={
                    **os.environ,
                    "PYTHONPATH": os.pathsep.join(
                        (str(Path(__file__).parents[1] / "src"), str(Path(__file__).parent))
                    ),
                },
            )
            children.append(child)
            assert select.select([child.stdout], [], [], 5)[0]
            assert child.stdout.readline().strip() == "ready", child.stderr.read()
        for child in children:
            child.stdin.write(json.dumps(parked) + "\n")
            child.stdin.flush()
        results = []
        for child in children:
            assert select.select([child.stdout], [], [], 20)[0]
            results.append(json.loads(child.stdout.readline()))
            child.wait(timeout=5)
            assert child.returncode == 0, child.stderr.read()
        assert sum(r.get("terminal_status") == "completed" for r in results) == 1
        assert sum("blocked" in r for r in results) == 1
        events = [json.loads(line) for line in (f.root / "calls.jsonl").read_text().splitlines()]
        assert sum(e["role"] == "implementer" and e["expected"] == 43 for e in events) == 1
        assert owners(f) == 0 and f.store.current(f.identity.program_id).generation == 1
    finally:
        for child in children:
            if child.poll() is None:
                child.kill()
            child.wait(timeout=5)


def test_v12_v3_frozen_filesystem_proof_matches_the_separate_accepted_c2_proof():
    from universal_coding_agent.product import (
        program_continuation_dispatch,
        program_source_dispatch,
    )

    def proof(module):
        tree = ast.parse(Path(module.__file__).read_text())
        return ast.dump(
            next(
                node
                for node in ast.walk(tree)
                if isinstance(node, ast.FunctionDef) and node.name == "_verify_files"
            )
        )

    assert proof(program_continuation_dispatch) == proof(program_source_dispatch)


@pytest.mark.parametrize("action", ["pause", "cancel", "recover"])
def test_v04_real_control_and_recovery_apis_are_excluded_at_action_commits(admitted, action):
    f = admitted
    code = """
import sqlite3,sys
from pathlib import Path
from universal_coding_agent.product.task_control import TaskControlService
from universal_coding_agent.product.lifecycle_reservations import DurableLifecycleReservationStore
from universal_coding_agent.product.models import ControlEntityType
action=sys.argv[1]
factory=DurableLifecycleReservationStore if action=='recover' else TaskControlService
store=factory(Path(sys.argv[2]))
store.connection.execute('PRAGMA busy_timeout=60')
candidate=None
print('ready',flush=True)
for line in sys.stdin:
    try:
        if action=='recover':
            visible=store.recovery_snapshot()[0]
            if visible:
                candidate=visible[0]
            assert candidate is not None
            store.recover(target_type=candidate.target_type,target_kind=candidate.target_kind,
                scope_id=candidate.scope_id,recovery_ref=candidate.recovery_ref,
                reason='Concurrent fixture recovery',confirmed=True)
        else:
            getattr(store,'request_'+action)(ControlEntityType.PROGRAM,sys.argv[3],
                reason='Concurrent fixture control')
    except (sqlite3.OperationalError,ValueError) as exc:
        cause=exc.__cause__ if isinstance(exc,ValueError) else exc
        assert isinstance(cause,sqlite3.OperationalError) and 'locked' in str(cause),str(exc)
        store.connection.rollback()
        print('blocked',flush=True)
    else:
        print('committed',flush=True)
store.close()
"""
    pin = f.v3.db.identities[2 if action == "recover" else 1]
    child = subprocess.Popen(
        [sys.executable, "-B", "-c", code, action, pin[0], f.identity.program_id],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    observed = []
    try:
        assert select.select([child.stdout], [], [], 5)[0]
        assert child.stdout.readline().strip() == "ready", child.stderr.read()

        def boundary(name):
            if name != "before_commit":
                return
            if f.v3._row(f.operation)["state"] in {"parked_scope", "closed"}:
                return
            child.stdin.write("try\n")
            child.stdin.flush()
            assert select.select([child.stdout], [], [], 3)[0]
            assert child.stdout.readline().strip() == "blocked"
            observed.append(name)

        f.v3.db.boundary = boundary
        parked = fixture.dispatch(f, f.operation, f.admitted)
        assert fixture.approve(f, f.operation, parked)["terminal_status"] == "completed"
        assert len(observed) >= 20 and owners(f) == 0
    finally:
        child.stdin.close()
        child.wait(timeout=5)
        assert child.returncode == 0, child.stderr.read()


@pytest.mark.parametrize("boundary", ["after_guard", "after_arm"])
def test_v06_failed_grants_retain_owner_and_require_exact_original_preparation(tmp_path, boundary):
    operation, receipt = fixture.prepare(tmp_path)
    f = fixture.consumer(tmp_path)
    try:

        def fault(name):
            if name == boundary:
                raise OSError("reversible explicit grant fault")

        f.v3.db.boundary = fault
        if boundary == "after_guard":
            with pytest.raises(OSError):
                fixture.admit(f, operation, receipt)
            with pytest.raises(ValueError):
                f.dispatch.admit(operation, preparation_receipt_sha256=receipt, owner_token=f.owner)
            f.v3.db.boundary = lambda _: None
            admitted_result = fixture.admit(f, operation, receipt)
        else:
            admitted_result = fixture.admit(f, operation, receipt)
            with pytest.raises(OSError):
                fixture.dispatch(f, operation, admitted_result)
            context = f.safe.control.cancellation._invocations[f.v3._row(operation)["task_id"]]
            assert context.revoked
            f.v3.db.boundary = lambda _: None
        assert owners(f) == 1
        assert fixture.dispatch(f, operation, admitted_result)["state"] == "parked_scope"
    finally:
        fixture.close(f)


@pytest.mark.parametrize("damage", ["serialization", "extension", "header", "pending-count"])
def test_v03_encoded_checkpoint_negatives_are_rejected_before_graph_decoding(admitted, damage):
    import ormsgpack

    f = admitted

    def boundary(name):
        if name != "after_outer_return":
            return
        thread = f.v3._row(f.operation)["thread_id"]
        db = f.safe.connection
        if damage == "serialization":
            db.execute("UPDATE checkpoints SET type='pickle' WHERE thread_id=?", (thread,))
        elif damage == "extension":
            raw = ormsgpack.packb(ormsgpack.Ext(2, ormsgpack.packb(["untrusted", "Callback", {}])))
            db.execute("UPDATE writes SET value=? WHERE thread_id=?", (raw, thread))
        elif damage == "header":
            db.execute("UPDATE writes SET channel=? WHERE thread_id=?", ("x" * 65537, thread))
        else:
            checkpoint = db.execute(
                "SELECT max(checkpoint_id) FROM checkpoints WHERE thread_id=?", (thread,)
            ).fetchone()[0]
            for i in range(129):
                db.execute(
                    "INSERT INTO writes SELECT thread_id,checkpoint_ns,checkpoint_id,task_id,?,"
                    "channel,type,value FROM writes WHERE thread_id=? "
                    "AND checkpoint_id=? AND idx=-3",
                    (i, thread, checkpoint),
                )
        db.commit()

    f.v3.db.boundary = boundary
    with pytest.raises((ValueError, ormsgpack.MsgpackDecodeError)):
        fixture.dispatch(f, f.operation, f.admitted)
    assert owners(f) == 1 and f.store.current(f.identity.program_id).generation == 1


def test_v09_unattributable_partial_apply_cannot_be_rolled_back_or_closed(admitted, monkeypatch):
    f = admitted
    parked = fixture.dispatch(f, f.operation, f.admitted)
    repo = f.base.filesystem.root / ("execution-" + f.operation) / "repo"
    original = Path.write_bytes

    def partial(path, raw):
        if path == repo / "app.py" and b"return 44" in raw:
            original(path, raw[:12])
            # The live edit attempt cannot attribute a second file's drift.
            other = next(p for p in repo.iterdir() if p.is_file() and p.name != "app.py")
            original(other, b"unattributable external drift")
            raise OSError("ambiguous external mutation during apply")
        return original(path, raw)

    monkeypatch.setattr(Path, "write_bytes", partial)
    with pytest.raises(ValueError):
        fixture.approve(f, f.operation, parked)
    assert owners(f) == 1 and f.v3._row(f.operation)["state"] == "resume_started"
    assert (f.source / "app.py").read_bytes().endswith(b"return 42\n")
    assert f.store.current(f.identity.program_id).generation == 1


@pytest.mark.parametrize("marker", ["root", "table", "table-and-row"])
def test_v08_missing_checkpoint_root_and_control_binding_never_fall_through(admitted, marker):
    f = admitted
    fixture.dispatch(f, f.operation, f.admitted)
    task = f.v3._live[f.operation].task()
    if marker == "root":
        f.safe.connection.execute(
            "DELETE FROM uca_source_dispatch_tasks_v3_guard WHERE guard_key='root'"
        )
    else:
        f.safe.connection.execute("DROP TABLE uca_source_dispatch_tasks_v3_guard")
    f.safe.connection.commit()
    if marker == "table-and-row":
        f.safe.control.connection.execute("DELETE FROM uca_source_dispatch_tasks_v3")
        f.safe.control.connection.commit()
    with pytest.raises(ValueError, match="guard|root|source-aware"):
        f.safe.resume(task.thread_id, True)
    assert owners(f) == 0


@pytest.mark.parametrize("remote", ["lease", "retirement", "unavailable"])
def test_v07_any_remote_history_or_unavailable_store_blocks_scope_claim(admitted, remote):
    from universal_coding_agent.core.remote_operations import RemoteOperationState

    f = admitted
    parked = fixture.dispatch(f, f.operation, f.admitted)
    row = f.v3._row(f.operation)
    store = f.safe.remote_operations
    if remote == "lease":
        store.register(
            task_id=row["task_id"],
            thread_id=row["thread_id"],
            transport="fixture",
            transport_scope="sha256:" + "b" * 64,
            operation_id="remote-fixture",
            base_sha="a" * 40,
            status="running",
            state=RemoteOperationState.ACTIVE,
        )
    elif remote == "retirement":
        columns = store.connection.execute(
            "PRAGMA table_info(remote_operation_lease_retirements)"
        ).fetchall()
        values = [
            row["task_id"] if c[1] == "task_id" else 0 if c[2] == "INTEGER" else "fixture"
            for c in columns
        ]
        store.connection.execute(
            "INSERT INTO remote_operation_lease_retirements VALUES ("
            + ",".join("?" for _ in values)
            + ")",
            values,
        )
        store.connection.commit()
    else:
        store.connection.close()
    calls = (f.root / "calls.jsonl").read_bytes()
    with pytest.raises((ValueError, sqlite3.DatabaseError)):
        fixture.approve(f, f.operation, parked)
    assert calls == (f.root / "calls.jsonl").read_bytes() and owners(f) == 0


def test_v02_discovery_callback_return_is_not_outer_settlement(admitted):
    f = admitted
    observed = []

    def boundary(name):
        if name == "after_discovery":
            live = f.v3._live[f.operation]
            with pytest.raises(ValueError, match="positively settled"):
                f.v3._seal(live)
            observed.append(name)

    f.v3.db.boundary = boundary
    assert fixture.dispatch(f, f.operation, f.admitted)["state"] == "parked_scope"
    assert observed == ["after_discovery"]


@pytest.mark.parametrize("damage", ["request", "receipt", "orphan", "oversized", "head"])
def test_v08_closed_d2a_requires_complete_bounded_history(tmp_path, damage):
    operation, receipt = fixture.prepare(tmp_path, foundation="closed")
    f = fixture.consumer(tmp_path)
    try:
        db = f.workspace.programs.connection
        if damage == "request":
            db.execute(
                "DELETE FROM program_continuation_requests WHERE request_id='foundation-create'"
            )
        elif damage == "receipt":
            db.execute("DELETE FROM program_continuation_receipts WHERE sequence=1")
        elif damage == "oversized":
            db.execute(
                "UPDATE program_continuation_receipts SET content=zeroblob(65537) WHERE sequence=1"
            )
        elif damage == "head":
            db.execute("DELETE FROM program_continuation_heads")
        else:
            db.execute(
                "INSERT INTO program_continuation_requests SELECT host_sha256,program_id,"
                "'orphan-request',request_sha256,action,epoch,status,receipt_sha256 "
                "FROM program_continuation_requests LIMIT 1"
            )
        db.commit()
        calls = (tmp_path / "calls.jsonl").read_bytes()
        with pytest.raises(ValueError):
            fixture.admit(f, operation, receipt)
        assert (tmp_path / "calls.jsonl").read_bytes() == calls and owners(f) == 1
        assert not db.execute("SELECT 1 FROM program_source_dispatches_v3").fetchall()
    finally:
        fixture.close(f)


@pytest.mark.parametrize(
    "stage,remove_locator", [("admitted", False), ("parked", False), ("parked", True)]
)
def test_v08_fresh_raw_safe_denies_surviving_v3_after_both_namespaces_lost(
    admitted,
    stage,
    remove_locator,
):
    from universal_coding_agent.product.program_source_routing import LOCATOR

    f = admitted
    if stage == "parked":
        fixture.dispatch(f, f.operation, f.admitted)
    row = f.v3._row(f.operation)
    f.safe.connection.execute("DROP TABLE uca_source_dispatch_tasks_v3_guard")
    f.safe.connection.commit()
    f.safe.control.connection.execute("DROP TABLE uca_source_dispatch_tasks_v3")
    f.safe.control.connection.commit()
    if remove_locator:
        (f.safe.artifacts.root.parent / LOCATOR).unlink()
    calls = (f.root / "calls.jsonl").read_bytes()
    expected_owners = owners(f)
    code = """
import sys
from pathlib import Path
from test_program_source_dispatch import runtime,close
f=runtime(Path(sys.argv[1]),43)
try:
    try:
        f.safe.resume(sys.argv[2],True)
    except ValueError:
        print('denied')
    else:
        raise AssertionError('raw Safe invoked a v3 checkpoint')
finally:
    close(f)
"""
    child = subprocess.run(
        [sys.executable, "-B", "-c", code, str(f.root), row["thread_id"]],
        capture_output=True,
        text=True,
        timeout=20,
        env={
            **os.environ,
            "PYTHONPATH": os.pathsep.join(
                (str(Path(__file__).parents[1] / "src"), str(Path(__file__).parent))
            ),
        },
    )
    assert child.returncode == 0, child.stderr
    assert child.stdout.strip() == "denied"
    assert calls == (f.root / "calls.jsonl").read_bytes() and owners(f) == expected_owners
    assert f.v3._row(f.operation)["state"] == ("parked_scope" if stage == "parked" else "admitted")


@pytest.mark.parametrize("damage", ["missing", "partial", "oversized", "symlink", "drift"])
def test_v08_root_locator_damage_blocks_raw_and_explicit_claim(admitted, damage):
    from universal_coding_agent.product.program_source_routing import LOCATOR

    f = admitted
    parked = fixture.dispatch(f, f.operation, f.admitted)
    path = f.safe.artifacts.root.parent / LOCATOR
    original = path.read_bytes()
    if damage == "missing":
        path.unlink()
    elif damage == "partial":
        path.write_bytes(original[:20])
    elif damage == "oversized":
        path.write_bytes(b" " * 65537)
    elif damage == "symlink":
        replacement = path.with_suffix(".probe")
        replacement.write_bytes(original)
        path.unlink()
        path.symlink_to(replacement)
    else:
        record = json.loads(original)
        record["host_sha256"] = "a" * 64
        path.write_bytes(canonical(record))
    calls = (f.root / "calls.jsonl").read_bytes()
    with pytest.raises((ValueError, OSError)):
        f.safe.resume(f.v3._row(f.operation)["thread_id"], True)
    with pytest.raises((ValueError, OSError)):
        fixture.approve(f, f.operation, parked)
    assert calls == (f.root / "calls.jsonl").read_bytes() and owners(f) == 0


def test_v08_copied_v3_task_metadata_cannot_enter_raw_safe_with_fresh_ids(admitted):
    f = admitted
    fixture.dispatch(f, f.operation, f.admitted)
    task = (
        f.v3._live[f.operation]
        .task()
        .model_copy(update={"task_id": "copied-v3-task", "thread_id": "copied-v3-thread"})
    )
    calls = (f.root / "calls.jsonl").read_bytes()
    with pytest.raises(ValueError, match="explicit versioned"):
        f.safe.run(task)
    assert calls == (f.root / "calls.jsonl").read_bytes() and owners(f) == 0


@pytest.mark.parametrize(
    "damage",
    [
        "unknown",
        "missing",
        "null",
        "claimed-v2",
        "metadata-removed",
        "lineage-unknown",
        "extension",
    ],
)
def test_v08_unknown_or_missing_version_never_erases_surviving_source_affinity(admitted, damage):
    from universal_coding_agent.product.program_source_routing import LOCATOR

    f = admitted
    fixture.dispatch(f, f.operation, f.admitted)
    row = f.v3._row(f.operation)
    db = f.safe.connection
    cp, encoding, raw = db.execute(
        "SELECT checkpoint_id,type,checkpoint FROM checkpoints WHERE thread_id=? "
        "ORDER BY checkpoint_id DESC LIMIT 1",
        (row["thread_id"],),
    ).fetchone()
    serde = f.safe.graph.checkpointer.serde
    value = serde.loads_typed((encoding, raw))
    task = value["channel_values"]["task"]
    if damage in {"metadata-removed", "lineage-unknown"}:
        task["metadata"] = {}
        if damage == "lineage-unknown":
            task["context_evidence"][0]["context_type"] = "accepted_source_lineage_99"
    elif damage == "missing":
        del task["metadata"]["execution_schema"]
    elif damage == "extension":
        import ormsgpack

        task["metadata"]["execution_schema"] = ormsgpack.Ext(99, b"uca-program-source-dispatch-3")
    else:
        task["metadata"]["execution_schema"] = {
            "unknown": "uca-program-source-dispatch-99",
            "null": None,
            "claimed-v2": "uca-program-source-dispatch-2",
        }[damage]
    if damage == "extension":
        encoding, raw = "msgpack", ormsgpack.packb(value)
    else:
        encoding, raw = serde.dumps_typed(value)
    db.execute(
        "UPDATE checkpoints SET type=?,checkpoint=? WHERE thread_id=? AND checkpoint_id=?",
        (encoding, raw, row["thread_id"], cp),
    )
    db.execute("DROP TABLE uca_source_dispatch_tasks_v3_guard")
    db.commit()
    f.safe.control.connection.execute("DROP TABLE uca_source_dispatch_tasks_v3")
    f.safe.control.connection.commit()
    (f.safe.artifacts.root.parent / LOCATOR).unlink()
    calls = (f.root / "calls.jsonl").read_bytes()
    # Each raw route uses a genuinely new host process with no live v3 capability.
    # The discovery attempt also uses fresh ids but retained source evidence.
    code = """
import sys
from pathlib import Path
from test_program_source_dispatch import runtime,close
from universal_coding_agent.core.safe_models import SafeTaskRequest
from universal_coding_agent.discovered_safe_service import DiscoveredSafeAgentService
f=runtime(Path(sys.argv[1]),43)
try:
    routes=[lambda:f.safe.resume(sys.argv[2],True),
            lambda:f.safe.resume_publish(sys.argv[2],approved=True,patch_sha256="a"*64),
            lambda:f.safe.resume_control(sys.argv[2])]
    for route in routes:
        try:route()
        except (ValueError,RuntimeError):pass
        else:raise AssertionError('raw checkpoint route executed')
    # Obtain the immutable original task as plain JSON, without decoding the
    # deliberately corrupted live checkpoint.
    import json
    raw=f.store.connection.execute('SELECT a.content FROM program_source_artifacts a '
        'JOIN program_source_continuation_heads_v3 h ON a.sha256=h.task_sha256 '
        'WHERE h.operation_id=?',(sys.argv[3],)).fetchone()[0]
    task=SafeTaskRequest.model_validate(json.loads(raw))
    task=task.model_copy(update={'task_id':'copied-source-task','thread_id':'copied-source-thread'})
    port=DiscoveredSafeAgentService.create(Path(sys.argv[1])/'safe',f.provider,
        allow_local_sources=True,control=f.safe.control,remote_operations=f.safe.remote_operations)
    routes=[lambda:f.safe.run(task),lambda:port.start(task_id=task.task_id,thread_id=task.thread_id,
        title=task.title,objective=task.objective,repository=task.repository,policy=task.policy,
        test_profiles=task.manifest.test_profiles,accepted_evidence=task.context_evidence)]
    for route in routes:
        try:route()
        except (ValueError,RuntimeError):pass
        else:raise AssertionError('copied source metadata executed')
    print('five routes denied')
finally:close(f)
"""
    child = subprocess.run(
        [sys.executable, "-B", "-c", code, str(f.root), row["thread_id"], f.operation],
        capture_output=True,
        text=True,
        timeout=20,
        env={
            **os.environ,
            "PYTHONPATH": os.pathsep.join(
                (str(Path(__file__).parents[1] / "src"), str(Path(__file__).parent))
            ),
        },
    )
    assert child.returncode == 0, child.stderr
    assert child.stdout.strip() == "five routes denied"
    assert calls == (f.root / "calls.jsonl").read_bytes() and owners(f) == 0
    assert f.v3._row(f.operation)["state"] == "parked_scope"


def test_v10_actual_wal_growth_between_route_header_and_retrieval_never_decodes(
    admitted, monkeypatch
):
    import ormsgpack

    from universal_coding_agent.product.program_source_routing import checkpoint_has_source_marker

    f = admitted
    fixture.dispatch(f, f.operation, f.admitted)
    thread = f.v3._row(f.operation)["thread_id"]
    checkpoint = f.safe.connection.execute(
        "SELECT checkpoint_id FROM checkpoints WHERE thread_id=? "
        "ORDER BY checkpoint_id DESC LIMIT 1",
        (thread,),
    ).fetchone()[0]
    writes, decoded = [], []
    unpack = ormsgpack.unpackb

    def observe(raw, *args, **kwargs):
        decoded.append(len(raw))
        return unpack(raw, *args, **kwargs)

    def race(sql):
        if sql.startswith("SELECT substr(checkpoint,1,16000001)") and not writes:
            code = """
import sqlite3,sys
with sqlite3.connect(sys.argv[1],timeout=0.3) as db:
    db.execute('UPDATE checkpoints SET checkpoint=zeroblob(16000001) '
               'WHERE thread_id=? AND checkpoint_id=?',(sys.argv[2],sys.argv[3]))
print('committed')
"""
            writes.append(
                subprocess.run(
                    [
                        sys.executable,
                        "-B",
                        "-c",
                        code,
                        f.v3.db.identities[4][0],
                        thread,
                        checkpoint,
                    ],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
            )

    monkeypatch.setattr(ormsgpack, "unpackb", observe)
    f.safe.connection.set_trace_callback(race)
    try:
        with pytest.raises(ValueError, match="changed"):
            checkpoint_has_source_marker(f.safe, thread)
    finally:
        f.safe.connection.set_trace_callback(None)
    assert len(writes) == 1 and writes[0].returncode == 0, writes
    assert writes[0].stdout.strip() == "committed" and decoded == []
    assert f.v3._row(f.operation)["state"] == "parked_scope" and owners(f) == 0


def test_v02_new_invocation_wait_is_bounded_under_a_real_unrelated_factory(admitted):
    from universal_coding_agent.core.cancellation import OwnedOperationKind

    f = admitted
    entered, release = threading.Event(), threading.Event()

    class Handle:
        def done(self):
            return True

        def cancel(self):
            pass

    def factory():
        entered.set()
        assert release.wait(15)
        return Handle()

    def hold():
        signal = f.safe.control.cancellation.signal("unrelated-owned-task")
        with signal.owned_cancellable_operation(OwnedOperationKind.PROVIDER, factory):
            pass

    holder = threading.Thread(target=hold)
    holder.start()
    try:
        assert entered.wait(3)
        calls = (f.root / "calls.jsonl").read_bytes()
        started = time.monotonic()
        with pytest.raises(RuntimeError, match="context is busy"):
            fixture.dispatch(f, f.operation, f.admitted)
        assert time.monotonic() - started < 4
        assert calls == (f.root / "calls.jsonl").read_bytes() and owners(f) == 1
        assert f.v3._row(f.operation)["state"] == "admitted"
        with sqlite3.connect(f.v3.db.identities[1][0], timeout=0.1) as db:
            db.execute("BEGIN IMMEDIATE")
            db.rollback()
    finally:
        release.set()
        holder.join(3)
    assert not holder.is_alive()
    assert fixture.dispatch(f, f.operation, f.admitted)["state"] == "parked_scope"


def test_v02_revocation_precedes_a_bounded_contended_registry_wait(admitted):
    f = admitted
    coordinator = f.safe.control.cancellation
    context = coordinator._new_invocation("revoke-probe-task")
    entered, release = threading.Event(), threading.Event()

    def hold():
        with coordinator._lock:
            entered.set()
            assert release.wait(10)

    holder = threading.Thread(target=hold)
    holder.start()
    try:
        assert entered.wait(3)
        started = time.monotonic()
        with pytest.raises(RuntimeError, match="context is busy"):
            coordinator._revoke_invocation(context)
        assert time.monotonic() - started < 4 and context.revoked
    finally:
        release.set()
        holder.join(3)
    with pytest.raises(RuntimeError, match="revoked"):
        with coordinator._invocation_context(context):
            pytest.fail("revoked context was reactivated")
    with coordinator._settlement_barrier(context):
        assert not any(coordinator._registration_snapshot(context.task_id).values())


@pytest.mark.parametrize("mode", ["delete", "wal"])
@pytest.mark.parametrize("target", ["safe", "remote", "guard"])
def test_v11_scoped_authorizers_deny_mutating_pragmas_and_keep_read_introspection(
    admitted,
    mode,
    target,
):
    f = admitted
    alias = "safe" if target == "guard" else target
    db = f.store.connection
    original = f.safe.connection if alias == "safe" else f.safe.remote_operations.connection
    if alias == "safe":
        db.execute("DETACH DATABASE safe")
        original.execute(f"PRAGMA journal_mode={mode}")
        db.execute("ATTACH DATABASE ? AS safe", (f.v3.db.identities[4][0],))
    else:
        original.execute(f"PRAGMA journal_mode={mode}")
    db.execute(f"PRAGMA {alias}.journal_mode={mode}")
    original.execute("PRAGMA synchronous=FULL")
    db.execute(f"PRAGMA {alias}.synchronous=FULL")
    before = original.execute("PRAGMA user_version").fetchone()[0]
    transaction = f.v3.db.guard_transaction if target == "guard" else f.v3.db.transaction
    connection = original if target == "guard" else db
    prefix = "main" if target == "guard" else alias
    with transaction():
        assert connection.execute(f"PRAGMA {prefix}.user_version").fetchone()[0] == before
        assert connection.execute(f"PRAGMA {prefix}.table_info(sqlite_master)").fetchall()
        for pragma in (
            "user_version=73",
            "application_id=73",
            "schema_version=73",
            "writable_schema=ON",
            "wal_checkpoint(TRUNCATE)",
            "optimize",
        ):
            with pytest.raises(sqlite3.DatabaseError, match="authorized"):
                connection.execute(f"PRAGMA {prefix}.{pragma}")
    assert original.execute("PRAGMA user_version").fetchone()[0] == before
    assert owners(f) == 1
