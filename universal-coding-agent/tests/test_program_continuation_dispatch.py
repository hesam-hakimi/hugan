"""Real v3 consumer fixtures. Providers are deterministic; Git/graphs/tests/stores are real."""

from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest
from test_program_source_dispatch import accept, close, runtime

from universal_coding_agent.core.models import RepositorySpec
from universal_coding_agent.discovered_safe_service import DiscoveredSafeAgentService
from universal_coding_agent.product.program_continuation_dispatch import (
    ProgramContinuationDispatchService,
)
from universal_coding_agent.product.program_continuation_execution_store import canonical, sha


def prepare(root, *, object_format="sha1", protocol="v1", foundation=""):
    f = runtime(root, 42, create=True, object_format=object_format, protocol=protocol)
    port = DiscoveredSafeAgentService.create(
        root / "safe",
        f.provider,
        allow_local_sources=True,
        control=f.workspace.control,
        remote_operations=f.workspace.remote_operations,
    )
    program = f.identity.program_id
    bound = f.workspace.programs.start_next_execution(
        program_id=program,
        current_requirement_hash=f.identity.requirement_sha256,
        repository=RepositorySpec(url=str(f.source), base_ref="fixture"),
        policy=f.policy,
        test_profiles=tuple(f.policy.profile_map()),
        executor=port,
    )
    f.workspace.programs.continue_execution(
        program_id=program,
        task_id=bound.task_id,
        current_requirement_hash=f.identity.requirement_sha256,
        executor=port,
        approved=True,
    )
    _, accepted = accept(f, bound.task_id, "scope-and-source-43")
    first_owner = f.owner
    f.workspace.lifecycle_reservations.release_program_worker(program, first_owner)
    f.owner = f.workspace.lifecycle_reservations.reserve_program_worker(program)
    assert f.owner != first_owner
    if foundation:
        from universal_coding_agent.product.program_continuation_handoff import (
            SCHEMA,
            ProgramContinuationHandoffStore,
        )

        handoff = ProgramContinuationHandoffStore(
            f.workspace.programs, f.workspace.lifecycle_reservations, host_id="fixture-foundation"
        )
        source = f.store.current(program)
        descriptor = {
            "schema": SCHEMA,
            "program_id": program,
            "phase_id": "phase-2",
            "task_id": "",
            "thread_id": "",
            "requirement_sha256": f.identity.requirement_sha256,
            "plan_sha256": f.identity.plan_sha256,
            "source_generation": 1,
            "source_sha256": sha(f.store.source.snapshot_bytes(source)),
            "acceptance_receipt_sha256": sha(canonical(accepted)),
            "admission_sha256": "",
            "checkpoint_sha256": "",
            "result_sha256": "",
            "approval_core_sha256": "",
            "next_action": "foundation_only",
            "execution_authorized": False,
            "consumer_bound": False,
        }
        created = handoff.create(
            program,
            request_id="foundation-create",
            owner_token=f.owner,
            descriptor=canonical(descriptor),
        ).public
        if foundation != "owned":
            getattr(handoff, "park" if foundation == "parked" else "close")(
                program,
                request_id="foundation-stop",
                owner_token=f.owner,
                expected_epoch=0,
                expected_receipt_sha256=created["receipt_sha256"],
            )
            f.owner = f.workspace.lifecycle_reservations.reserve_program_worker(program)
    (root / "fixture.json").write_text(json.dumps({"owner": f.owner}))
    material = f.base.materialization.begin(
        program, owner_token=f.owner, acceptance_receipt_sha256=sha(canonical(accepted))
    )
    f.base.materialization.reconcile(material["operation_id"], owner_token=f.owner)
    base = f.base.begin(material["operation_id"], owner_token=f.owner)
    receipt = f.base.reconcile(base["operation_id"], owner_token=f.owner)
    close(f)
    return base["operation_id"], sha(canonical(receipt))


def consumer(root, *, protocol="v1"):
    f = runtime(root, 43, protocol=protocol)
    f.v3 = ProgramContinuationDispatchService(
        f.base,
        f.provider,
        lifecycle=f.workspace.lifecycle_reservations,
        transport_id="fixture-synchronous",
    )
    return f


def admit(f, operation, receipt):
    return f.v3.admit(
        f.identity.program_id,
        operation,
        request_id="admit-43",
        preparation_receipt_sha256=receipt,
        owner_token=f.owner,
    )


def dispatch(f, operation, admitted):
    return f.v3.dispatch(
        f.identity.program_id,
        operation,
        request_id="discover-43",
        admission_sha256=admitted["admission_sha256"],
        expected_epoch=admitted["epoch"],
        expected_receipt_sha256=admitted["receipt_sha256"],
        owner_token=f.owner,
    )


def approve(f, operation, parked, *, approved=True):
    return f.v3.approve_scope(
        f.identity.program_id,
        operation,
        request_id="scope-44",
        admission_sha256=parked["admission_sha256"],
        expected_epoch=parked["epoch"],
        expected_receipt_sha256=parked["receipt_sha256"],
        proposal_sha256=parked["proposal_sha256"],
        scope_sha256=parked["scope_sha256"],
        approval_id="approve-exact-44",
        approved=approved,
    )


@pytest.mark.parametrize(
    "object_format,protocol", [("sha1", "v1"), ("sha256", "v2-line-addressed")]
)
def test_actual_scope_park_and_fresh_worker_to_terminal_unaccepted(
    tmp_path, object_format, protocol
):
    operation, receipt = prepare(tmp_path, object_format=object_format, protocol=protocol)
    f = consumer(tmp_path, protocol=protocol)
    try:
        admitted = admit(f, operation, receipt)
        parked = dispatch(f, operation, admitted)
        assert parked["state"] == "parked_scope"
        assert (
            f.workspace.lifecycle_reservations.connection.execute(
                "SELECT count(*) FROM lifecycle_worker_ownership"
            ).fetchone()[0]
            == 0
        )
        before = (tmp_path / "calls.jsonl").read_bytes()
        assert dispatch(f, operation, admitted) == parked
        assert (tmp_path / "calls.jsonl").read_bytes() == before
        result = approve(f, operation, parked)
        assert result["state"] == "closed" and result["terminal_status"] == "completed"
        assert result["epoch"] == 1
        assert f.store.current(f.identity.program_id).generation == 1
        assert (
            (f.base.filesystem.root / ("execution-" + operation) / "repo/app.py")
            .read_bytes()
            .endswith(b"return 44\n")
        )
        assert (f.source / "app.py").read_bytes().endswith(b"return 42\n")
        assert (
            f.workspace.lifecycle_reservations.connection.execute(
                "SELECT count(*) FROM lifecycle_worker_ownership"
            ).fetchone()[0]
            == 0
        )
        with pytest.raises(ValueError):
            accept(f, f.v3._row(operation)["task_id"], "forbidden-44")
    finally:
        close(f)


@pytest.fixture
def admitted(tmp_path):
    operation, receipt = prepare(tmp_path)
    f = consumer(tmp_path)
    f.operation, f.receipt = operation, receipt
    f.admitted = admit(f, operation, receipt)
    try:
        yield f
    finally:
        close(f)


@pytest.mark.parametrize("failure", ["reject", "tests", "review", "partial-write"])
def test_v09_actual_failures_and_known_partial_rollback_keep_source(admitted, monkeypatch, failure):
    f = admitted
    parked = dispatch(f, f.operation, f.admitted)
    repo = f.base.filesystem.root / ("execution-" + f.operation) / "repo"
    if failure == "review":
        f.provider._handlers["reviewer"] = lambda _: {
            "verdict": "FAIL",
            "required_actions": ["Reject fixture"],
            "confidence": "high",
        }
    if failure == "tests":
        old = f.provider._handlers["implementer"]

        def wrong(request):
            value = old(request)
            value["edits"][0]["replacements"][0]["new_text"] = "return 45"
            return value

        f.provider._handlers["implementer"] = wrong
    if failure == "partial-write":
        old_write = Path.write_bytes

        def partial(path, raw):
            if path == repo / "app.py" and b"return 44" in raw:
                old_write(path, raw[:12])
                raise OSError("Injected known partial write")
            return old_write(path, raw)

        monkeypatch.setattr(Path, "write_bytes", partial)
    result = approve(f, f.operation, parked, approved=failure != "reject")
    assert result["state"] == "closed" and result["terminal_status"] == "blocked"
    assert (repo / "app.py").read_bytes() == b"def answer():\n    return 43\n"
    assert f.store.current(f.identity.program_id).generation == 1
    assert (
        f.workspace.lifecycle_reservations.connection.execute(
            "SELECT count(*) FROM lifecycle_worker_ownership"
        ).fetchone()[0]
        == 0
    )


def _child(stage, root, *, object_format="sha1", protocol="v1", boundary=""):
    env = {
        **os.environ,
        "PYTHONPATH": os.pathsep.join(
            (str(Path(__file__).parents[1] / "src"), str(Path(__file__).parent))
        ),
    }
    return subprocess.run(
        [
            sys.executable,
            "-B",
            str(Path(__file__).resolve()),
            stage,
            str(root),
            object_format,
            protocol,
            boundary,
        ],
        env=env,
        text=True,
        capture_output=True,
        timeout=40,
    )


def _process_stage(stage, root, object_format, protocol, crash):
    if stage == "prepare":
        operation, receipt = prepare(root, object_format=object_format, protocol=protocol)
        (root / "operation.json").write_text(
            json.dumps({"operation": operation, "receipt": receipt})
        )
        return
    saved = json.loads((root / "operation.json").read_text())
    operation = saved["operation"]
    if stage == "read":
        from universal_coding_agent.product.program_continuation_execution_store import (
            request_result,
            status,
        )

        program_path = root / "product" / "programs.sqlite"
        # Resolve the actual Program filename from the trusted fixture host.
        program_path = next((root / "product").glob("*program*.sqlite"))
        parked = json.loads((root / "parked.json").read_text())
        result = request_result(program_path, "cumulative-program", "discover-43")
        assert result == parked
        assert status(program_path, "cumulative-program", operation)["state"] == "parked_scope"
        return
    f = consumer(root, protocol=protocol)
    try:
        if crash in {"before_discovery_provider", "after_discovery_provider"}:
            original = f.provider._handlers["solution_discovery"]

            def killed_discovery(request):
                if crash == "before_discovery_provider":
                    os._exit(73)
                original(request)
                os._exit(73)

            f.provider._handlers["solution_discovery"] = killed_discovery
        if crash == "during_apply_write":
            original_write = Path.write_bytes

            def killed_write(path, raw):
                if path.name == "app.py" and b"return 44" in raw:
                    original_write(path, raw[:12])
                    os._exit(73)
                return original_write(path, raw)

            Path.write_bytes = killed_write

        def boundary(name):
            if ":" in crash:
                phase, point = crash.split(":", 1)
                try:
                    state = f.v3._row(operation)["state"]
                except ValueError:
                    state = "absent"
                if (
                    name == point
                    and state
                    in {
                        "scope": {"safe_started", "parked_scope"},
                        "terminal": {"resume_started", "closed"},
                    }[phase]
                ):
                    os._exit(73)
            if name == crash:
                os._exit(73)
            if (
                crash in {"admission_commit", "park_commit", "closed_commit"}
                and name == "after_commit"
            ):
                expected = {
                    "admission_commit": "admitted",
                    "park_commit": "parked_scope",
                    "closed_commit": "closed",
                }[crash]
                try:
                    row = f.v3._row(operation)
                except ValueError:
                    return
                if row["state"] == expected:
                    os._exit(73)

        f.v3.db.boundary = boundary
        if stage in {"admit", "park"}:
            initial = admit(f, operation, saved["receipt"])
            if stage == "admit":
                return
            parked = dispatch(f, operation, initial)
            (root / "parked.json").write_bytes(canonical(parked))
        elif stage == "resume":
            parked = json.loads((root / "parked.json").read_text())
            result = approve(f, operation, parked)
            (root / "closed.json").write_bytes(canonical(result))
    finally:
        close(f)


@pytest.mark.parametrize(
    "object_format,protocol", [("sha1", "v1"), ("sha256", "v2-line-addressed")]
)
def test_v01_real_process_exit_after_scope_and_restart_once(tmp_path, object_format, protocol):
    for stage in ("prepare", "park", "read", "resume"):
        result = _child(stage, tmp_path, object_format=object_format, protocol=protocol)
        assert result.returncode == 0, result.stdout + result.stderr
    f = consumer(tmp_path, protocol=protocol)
    try:
        operation = json.loads((tmp_path / "operation.json").read_text())["operation"]
        parked = json.loads((tmp_path / "parked.json").read_text())
        closed = json.loads((tmp_path / "closed.json").read_text())
        assert closed["terminal_status"] == "completed" and closed["epoch"] == 1
        calls = (tmp_path / "calls.jsonl").read_bytes()
        assert approve(f, operation, parked) == closed
        assert (tmp_path / "calls.jsonl").read_bytes() == calls
        events = [json.loads(line) for line in calls.splitlines()]
        for role in ("solution_discovery", "implementer", "reviewer"):
            assert len([e for e in events if e["role"] == role and e["expected"] == 43]) == 1
        source = f.store.current(f.identity.program_id)
        assert source.generation == 1
        assert next(x.content for x in source.files if x.path == "app.py").endswith(b"return 43\n")
        assert (
            f.store.connection.execute("SELECT count(*) FROM program_source_candidates").fetchone()[
                0
            ]
            == 1
        )
        assert (
            f.store.connection.execute(
                "SELECT count(*) FROM program_source_acceptances"
            ).fetchone()[0]
            == 1
        )
        repo = f.base.filesystem.root / ("execution-" + operation) / "repo"
        assert (repo / "app.py").read_bytes().endswith(b"return 44\n")
        for item in source.files:
            original = (f.source / item.path).read_bytes()
            assert original == (
                b"def answer():\n    return 42\n" if item.path == "app.py" else item.content
            )
            if item.path != "app.py":
                assert (repo / item.path).read_bytes() == item.content
                assert bool((repo / item.path).stat().st_mode & 0o111) == bool(
                    (f.source / item.path).stat().st_mode & 0o111
                )
    finally:
        close(f)


@pytest.mark.parametrize(
    "drift",
    [
        "namespace",
        "extra-write",
        "error",
        "resume",
        "write-task",
        "scope",
        "checkpoint-task",
        "unsupported-boundary",
    ],
)
def test_v03_actual_checkpoint_shape_corruption_cannot_seal(admitted, drift):
    f = admitted

    def fault(name):
        if name != "after_outer_return":
            return
        thread = f.v3._row(f.operation)["thread_id"]
        db = f.safe.connection
        checkpoint = db.execute(
            "SELECT * FROM checkpoints WHERE thread_id=? ORDER BY checkpoint_id DESC LIMIT 1",
            (thread,),
        ).fetchone()
        if drift == "namespace":
            db.execute(
                "INSERT INTO checkpoints SELECT thread_id,'extra',checkpoint_id,"
                "parent_checkpoint_id,"
                "type,checkpoint,metadata FROM checkpoints WHERE thread_id=?",
                (thread,),
            )
        elif drift == "extra-write":
            db.execute(
                "INSERT INTO writes SELECT thread_id,checkpoint_ns,checkpoint_id,task_id,999,"
                "channel,type,value FROM writes WHERE thread_id=? AND checkpoint_id=?",
                (thread, checkpoint[2]),
            )
        elif drift in {"error", "resume", "write-task"}:
            column = "task_id" if drift == "write-task" else "channel"
            value = "wrong-task" if drift == "write-task" else "__" + drift + "__"
            db.execute(f"UPDATE writes SET {column}=? WHERE thread_id=?", (value, thread))
        else:
            kind, raw = db.execute(
                "SELECT type,checkpoint FROM checkpoints WHERE thread_id=? "
                "ORDER BY checkpoint_id DESC LIMIT 1",
                (thread,),
            ).fetchone()
            serde = f.safe.graph.checkpointer.serde
            value = serde.loads_typed((kind, raw))
            values = value["channel_values"]
            if drift == "scope":
                values["scope_hash"] = "f" * 64
            elif drift == "checkpoint-task":
                values["task"]["task_id"] = "other-task"
            else:
                values["status"] = "awaiting_publish_approval"
            kind, raw = serde.dumps_typed(value)
            db.execute(
                "UPDATE checkpoints SET type=?,checkpoint=? WHERE thread_id=? AND checkpoint_id=?",
                (kind, raw, thread, checkpoint[2]),
            )
        db.commit()

    f.v3.db.boundary = fault
    with pytest.raises((ValueError, RuntimeError)):
        dispatch(f, f.operation, f.admitted)
    assert f.v3.status(f.identity.program_id, f.operation)["state"] == "recovery_required"
    assert (
        f.workspace.lifecycle_reservations.connection.execute(
            "SELECT count(*) FROM lifecycle_worker_ownership"
        ).fetchone()[0]
        == 1
    )
    assert f.store.current(f.identity.program_id).generation == 1


def test_v02_return_is_required_even_with_valid_scope_checkpoint(admitted):
    from universal_coding_agent.core.cancellation import OwnedOperationKind

    f = admitted
    observations = []

    def fault(name):
        if name == "after_outer_return":
            with pytest.raises(ValueError, match="positively settled"):
                f.v3._seal(f.v3._live[f.operation])
            observations.append(name)

    f.v3.db.boundary = fault
    parked = dispatch(f, f.operation, f.admitted)
    assert observations and parked["state"] == "parked_scope"
    live = f.v3._live[f.operation]
    with pytest.raises(ValueError, match="revoked"):
        live.node("implement", {}, lambda _: None)
    with pytest.raises(RuntimeError, match="registration context"):
        with f.safe.control.cancellation.signal(live._context.task_id).operation(
            OwnedOperationKind.PROVIDER
        ):
            pytest.fail("revoked registration was admitted")


@pytest.mark.parametrize(
    "alias,pragma",
    [
        ("control", "journal_mode=WAL"),
        ("main", "synchronous=OFF"),
        ("lifecycle", "journal_mode=WAL"),
        ("safe", "synchronous=OFF"),
        ("remote", "synchronous=OFF"),
    ],
)
def test_v11_reject_unsupported_durability_before_effects(admitted, alias, pragma):
    f = admitted
    before = (f.root / "calls.jsonl").read_bytes()
    f.store.connection.execute(f"PRAGMA {alias}.{pragma}")
    with pytest.raises(ValueError, match="durable"):
        dispatch(f, f.operation, f.admitted)
    assert (f.root / "calls.jsonl").read_bytes() == before
    assert f.v3._row(f.operation)["state"] == "admitted"


def test_v11_authorizer_denies_unrelated_tables_and_read_only_attachments(admitted):
    f = admitted
    for sql in (
        "UPDATE program_source_heads SET generation=99",
        "DELETE FROM program_source_candidates",
        "DELETE FROM program_source_acceptances",
        "DELETE FROM control.pause_reports",
        "DELETE FROM lifecycle.lifecycle_recovery_receipts",
        "DELETE FROM safe.checkpoints",
        "DELETE FROM remote.remote_operation_leases",
        "CREATE TABLE forbidden(x)",
        "DROP TABLE program_source_continuation_heads_v3",
    ):
        with pytest.raises(sqlite3.DatabaseError):
            with f.v3.db.transaction():
                f.store.connection.execute(sql)
    assert f.store.current(f.identity.program_id).generation == 1


@pytest.mark.parametrize(
    "stage,boundary,expected",
    [
        ("admit", "before_guard", "absent"),
        ("admit", "after_root_locator", "absent"),
        ("admit", "after_guard", "absent"),
        ("admit", "after_admission", "absent"),
        ("admit", "after_receipt", "absent"),
        ("admit", "admission_commit", "admitted"),
        ("park", "after_arm", "admitted"),
        ("park", "after_claim", "discovery_started"),
        ("park", "before_discovery_provider", "discovery_started"),
        ("park", "after_discovery_provider", "discovery_started"),
        ("park", "after_discovery", "discovery_started"),
        ("park", "after_node_sandbox", "safe_started"),
        ("park", "after_node_index", "safe_started"),
        ("park", "after_outer_return", "safe_started"),
        ("park", "before_settlement", "safe_started"),
        ("park", "scope:after_worker_release", "safe_started"),
        ("park", "scope:after_request_completion", "safe_started"),
        ("park", "park_commit", "parked_scope"),
        ("resume", "after_fresh_worker", "parked_scope"),
        ("resume", "after_arm", "parked_scope"),
        ("resume", "after_claim", "resume_started"),
        ("resume", "after_node_scope_approval", "resume_started"),
        ("resume", "after_node_implement", "resume_started"),
        ("resume", "after_node_apply_edits", "resume_started"),
        ("resume", "during_apply_write", "resume_started"),
        ("resume", "after_node_tests", "resume_started"),
        ("resume", "after_node_review", "resume_started"),
        ("resume", "after_node_finalize", "resume_started"),
        ("resume", "after_outer_return", "resume_started"),
        ("resume", "terminal:after_worker_release", "resume_started"),
        ("resume", "closed_commit", "closed"),
    ],
)
def test_v05_real_process_death_never_reconstructs_invocation(tmp_path, stage, boundary, expected):
    operation, receipt = prepare(tmp_path)
    (tmp_path / "operation.json").write_text(
        json.dumps({"operation": operation, "receipt": receipt})
    )
    if stage == "resume":
        parked_process = _child("park", tmp_path)
        assert parked_process.returncode == 0, parked_process.stderr
    killed = _child(stage, tmp_path, boundary=boundary)
    assert killed.returncode == 73, killed.stdout + killed.stderr
    f = consumer(tmp_path)
    try:
        row = f.store.connection.execute(
            "SELECT state FROM program_source_continuation_heads_v3 WHERE operation_id=?",
            (operation,),
        ).fetchone()
        actual = row[0] if row else "absent"
        assert actual == expected
        assert f.store.current(f.identity.program_id).generation == 1
        assert (f.source / "app.py").read_bytes() == b"def answer():\n    return 42\n"
        owners = f.workspace.lifecycle_reservations.connection.execute(
            "SELECT count(*) FROM lifecycle_worker_ownership"
        ).fetchone()[0]
        assert owners == (0 if actual in {"parked_scope", "closed"} else 1)
        executions = f.store.connection.execute(
            "SELECT count(*) FROM program_executions WHERE phase_id='phase-2'"
        ).fetchone()[0]
        registry = f.store.connection.execute(
            "SELECT count(*) FROM control.uca_source_dispatch_tasks_v3"
        ).fetchone()[0]
        assert executions == registry == (actual != "absent")
        calls = (tmp_path / "calls.jsonl").read_bytes()
        if actual not in {"absent", "admitted", "parked_scope", "closed"}:
            assert f.v3.status(f.identity.program_id, operation)["state"] == "recovery_required"
            with pytest.raises(ValueError, match="original live return"):
                f.v3.reconcile(
                    f.identity.program_id,
                    operation,
                    request_id="scope-44" if stage == "resume" else "discover-43",
                )
        assert (tmp_path / "calls.jsonl").read_bytes() == calls
        assert (
            f.store.connection.execute(
                "SELECT count(*) FROM program_source_acceptances"
            ).fetchone()[0]
            == 1
        )
    finally:
        close(f)


@pytest.mark.parametrize("kind", ["operation", "process", "cancellable", "pausable", "paused"])
def test_v02_registered_work_blocks_seal_until_original_live_context_is_empty(admitted, kind):
    from universal_coding_agent.core.cancellation import OwnedOperationKind

    f, held = admitted, {}
    coordinator = f.safe.control.cancellation
    old = f.provider._handlers["solution_discovery"]

    class Handle:
        def cancel(self):
            pass

        def done(self):
            return True

        def pause(self):
            pass

        def resume(self):
            pass

        def paused(self):
            return True

    def hold(request):
        live = f.v3._live[f.operation]
        task = live._context.task_id
        held["signal"] = coordinator.signal(task)
        if kind in {"operation", "pausable", "paused"}:
            held["operation"] = coordinator._begin_operation(
                task, OwnedOperationKind.PROVIDER, registration_context=live._context
            )
        if kind == "process":
            held["process"] = coordinator._start_process(
                task,
                OwnedOperationKind.PROVIDER,
                lambda: subprocess.Popen(
                    [sys.executable, "-c", "import sys; sys.stdin.read()"],
                    stdin=subprocess.PIPE,
                    start_new_session=True,
                ),
                registration_context=live._context,
            )
        if kind == "cancellable":
            held["cancellable"] = coordinator._start_cancellable(
                task, OwnedOperationKind.PROVIDER, Handle, registration_context=live._context
            )
        if kind in {"pausable", "paused"}:
            held["pausable"] = coordinator._start_pausable(
                task,
                OwnedOperationKind.PROVIDER,
                held["operation"],
                Handle,
                registration_context=live._context,
            )
            if kind == "paused":
                coordinator._paused_pausables[task] = (held["pausable"],)
        return old(request)

    f.provider._handlers["solution_discovery"] = hold
    try:
        with pytest.raises(RuntimeError, match="outstanding owned registrations"):
            dispatch(f, f.operation, f.admitted)
        assert (
            f.workspace.lifecycle_reservations.connection.execute(
                "SELECT count(*) FROM lifecycle_worker_ownership"
            ).fetchone()[0]
            == 1
        )
        calls = (f.root / "calls.jsonl").read_bytes()
        with pytest.raises(RuntimeError, match="revoked"):
            with held["signal"].operation(OwnedOperationKind.PROVIDER):
                pytest.fail("late v3 registration succeeded")
    finally:
        task = f.v3._live[f.operation]._context.task_id
        if "process" in held:
            held["process"].process.communicate(timeout=5)
            coordinator._unregister_process(task, held["process"])
        if "cancellable" in held:
            coordinator._unregister_cancellable(task, held["cancellable"])
        if "pausable" in held:
            coordinator._unregister_pausable(task, held["pausable"])
        if "operation" in held:
            coordinator._end_operation(task, held["operation"])
        coordinator._paused_pausables.pop(task, None)
    result = f.v3.reconcile(f.identity.program_id, f.operation, request_id="discover-43")
    assert result["state"] == "parked_scope"
    assert (f.root / "calls.jsonl").read_bytes() == calls


@pytest.mark.parametrize(
    "drift",
    [
        "pause-resume",
        "cancel",
        "requirement",
        "plan-row",
        "plan-file",
        "head",
        "source-receipt",
        "preparation",
        "materialization",
        "git",
        "retained",
        "inode",
        "policy",
        "administrative-recovery",
    ],
)
def test_v07_parked_proposal_rejects_drift_without_refresh_or_new_worker(admitted, drift):
    f = admitted
    parked = dispatch(f, f.operation, f.admitted)
    calls = (f.root / "calls.jsonl").read_bytes()
    program = f.identity.program_id
    repo = f.base.filesystem.root / ("execution-" + f.operation) / "repo"
    db = f.store.connection
    if drift == "pause-resume":
        f.workspace.programs.pause(program)
        f.workspace.programs.resume(program)
    elif drift == "cancel":
        f.workspace.programs.cancel(program)
    elif drift in {"requirement", "plan-row"}:
        field = "requirement_hash" if drift == "requirement" else "plan_hash"
        db.execute(f"UPDATE programs SET {field}=? WHERE program_id=?", ("f" * 64, program))
    elif drift == "plan-file":
        f.workspace.programs.artifacts.write_json(f"programs/{program}/program-plan.json", {})
    elif drift == "head":
        db.execute("UPDATE program_source_heads SET generation=2")
    elif drift == "source-receipt":
        db.execute("UPDATE program_source_heads SET receipt_sha256=?", ("f" * 64,))
    elif drift == "preparation":
        db.execute("UPDATE program_execution_bases SET completion_sha256=?", ("f" * 64,))
    elif drift == "materialization":
        db.execute("UPDATE program_source_materializations SET completion_sha256=?", ("f" * 64,))
    elif drift == "git":
        (repo / ".git/HEAD").write_bytes(b"f" * 40 + b"\n")
    elif drift == "retained":
        (repo / "binary.bin").write_bytes(b"wrong")
    elif drift == "inode":
        data = (repo / "binary.bin").read_bytes()
        (repo / "binary.bin").rename(repo / "replaced.bin")
        (repo / "binary.bin").write_bytes(data)
        (repo / "replaced.bin").unlink()
    elif drift == "policy":
        f.store.trusted_policy = f.policy.model_copy(update={"profiles": f.policy.profiles[:1]})
    else:
        lifecycle = f.workspace.lifecycle_reservations
        lifecycle.reserve_program_worker(program)
        candidate = lifecycle.recovery_snapshot()[0][0]
        lifecycle.recover(
            target_type=candidate.target_type,
            target_kind=candidate.target_kind,
            scope_id=candidate.scope_id,
            recovery_ref=candidate.recovery_ref,
            reason="Fixture exact administrative recovery",
            confirmed=True,
        )
    with pytest.raises((ValueError, OSError)):
        approve(f, f.operation, parked)
    assert (f.root / "calls.jsonl").read_bytes() == calls
    assert (
        f.workspace.lifecycle_reservations.connection.execute(
            "SELECT count(*) FROM lifecycle_worker_ownership"
        ).fetchone()[0]
        == 0
    )


@pytest.mark.parametrize(
    "removed",
    [
        (),
        ("guard",),
        ("registry",),
        ("admission",),
        ("head",),
        ("preparation",),
        ("guard", "registry"),
        ("guard", "registry", "admission"),
        ("guard", "registry", "admission", "head", "preparation"),
    ],
)
def test_v08_surviving_markers_never_route_to_legacy(admitted, removed):
    from universal_coding_agent.core.safe_models import SafeTaskRequest
    from universal_coding_agent.product.program_source_status import program_source_status

    f = admitted
    parked = dispatch(f, f.operation, f.admitted)
    row = f.v3._row(f.operation)
    task = SafeTaskRequest.model_validate(f.v3._json(row["task_sha256"]))
    calls = (f.root / "calls.jsonl").read_bytes()
    for marker in removed:
        alias, name, column = {
            "guard": ("safe", "uca_source_dispatch_tasks_v3_guard", "guard_key"),
            "registry": ("control", "uca_source_dispatch_tasks_v3", "task_id"),
            "admission": ("main", "program_source_dispatches_v3", "operation_id"),
            "head": ("main", "program_source_continuation_heads_v3", "operation_id"),
            "preparation": ("main", "program_execution_bases", "operation_id"),
        }[marker]
        f.store.connection.execute(
            f"DELETE FROM {alias}.{name} WHERE {column}=?",
            (task.task_id if marker == "registry" else f.operation,),
        )
    port = DiscoveredSafeAgentService.create(
        f.root / "safe",
        f.provider,
        allow_local_sources=True,
        control=f.workspace.control,
        remote_operations=f.workspace.remote_operations,
    )
    for action in (
        lambda: f.safe.run(task),
        lambda: f.safe.resume(task.thread_id, True),
        lambda: f.safe.resume_control(task.thread_id),
        lambda: f.safe.resume_publish(task.thread_id, approved=True, patch_sha256="f" * 64),
        lambda: port.start(
            task_id=task.task_id,
            thread_id=task.thread_id,
            title=task.title,
            objective=task.objective,
            repository=task.repository,
            policy=task.policy,
            test_profiles=tuple(f.policy.profile_map()),
        ),
        lambda: f.dispatch.admit(
            f.operation, preparation_receipt_sha256=f.receipt, owner_token=f.owner
        ),
        lambda: f.store.prepare(
            f.identity.program_id,
            task.task_id,
            owner_token=f.owner,
            expected_source_sha256=parked["admission_sha256"],
            expected_generation=1,
        ),
        lambda: program_source_status(f.workspace.programs.database_path, f.identity.program_id),
        lambda: f.workspace.programs.continue_execution(
            program_id=f.identity.program_id,
            task_id=task.task_id,
            current_requirement_hash=f.identity.requirement_sha256,
            executor=port,
            approved=True,
        ),
    ):
        with pytest.raises(ValueError):
            action()
    assert (f.root / "calls.jsonl").read_bytes() == calls


def test_v06_pending_duplicate_and_reversible_seal_failure_do_not_repeat_work(admitted):
    f = admitted
    observed = []

    def fault(name):
        if name == "after_outer_return":
            duplicate = dispatch(f, f.operation, f.admitted)
            assert duplicate["request_status"] == "pending"
        if name == "before_settlement" and not observed:
            observed.append(name)
            raise OSError("reversible result recording failure")

    f.v3.db.boundary = fault
    with pytest.raises(OSError, match="recording"):
        dispatch(f, f.operation, f.admitted)
    before = (f.root / "calls.jsonl").read_bytes()
    result = f.v3.reconcile(f.identity.program_id, f.operation, request_id="discover-43")
    assert result["state"] == "parked_scope"
    assert dispatch(f, f.operation, f.admitted) == result
    assert (f.root / "calls.jsonl").read_bytes() == before
    wrong = {**f.admitted, "receipt_sha256": "f" * 64}
    with pytest.raises(ValueError, match="content differs"):
        dispatch(f, f.operation, wrong)


@pytest.mark.parametrize(
    "alias,journal",
    [
        ("main", "delete"),
        ("control", "delete"),
        ("lifecycle", "delete"),
        ("safe", "delete"),
        ("safe", "wal"),
        ("remote", "delete"),
        ("remote", "wal"),
    ],
)
def test_v04_actual_process_writers_are_excluded_through_every_consumer_commit(
    admitted, alias, journal
):
    import select

    f = admitted
    if alias == "safe":
        # SqliteSaver initializes WAL. Changing back to DELETE needs its other
        # idle attachment closed; restore that exact attachment before any action.
        path = f.v3.db.identities[4][0]
        f.store.connection.execute("DETACH DATABASE safe")
        f.safe.connection.execute(f"PRAGMA journal_mode={journal}")
        f.store.connection.execute("ATTACH DATABASE ? AS safe", (path,))
    else:
        f.store.connection.execute(f"PRAGMA {alias}.journal_mode={journal}")
    paths = dict(zip(f.v3.db.aliases, f.v3.db.identities, strict=True))
    sql = {
        "main": "UPDATE program_source_heads SET generation=generation+1",
        "control": "UPDATE control_state SET revision=revision+1,state='pause_requested'",
        "lifecycle": "DELETE FROM lifecycle_worker_ownership",
        "safe": "UPDATE checkpoints SET metadata=metadata",
        "remote": "UPDATE remote_operation_leases SET revision=revision+1",
    }[alias]
    code = """
import sqlite3,sys
db=sqlite3.connect(sys.argv[1],isolation_level=None,timeout=0.08)
print('ready',flush=True)
for line in sys.stdin:
    try:
        db.execute(sys.argv[2])
    except sqlite3.OperationalError as exc:
        assert 'locked' in str(exc),str(exc)
        print('blocked',flush=True)
    else:
        print('committed',flush=True)
db.close()
"""
    child = subprocess.Popen(
        [sys.executable, "-B", "-c", code, paths[alias][0], sql],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    observations = []
    try:
        assert select.select([child.stdout], [], [], 3)[0]
        assert child.stdout.readline().strip() == "ready"

        def fault(name):
            if name != "before_commit":
                return
            child.stdin.write("write\n")
            child.stdin.flush()
            assert select.select([child.stdout], [], [], 3)[0], "writer timed out"
            observed = child.stdout.readline().strip()
            assert observed == "blocked"
            observations.append(observed)

        f.v3.db.boundary = fault
        parked = dispatch(f, f.operation, f.admitted)
        completed = approve(f, f.operation, parked)
        assert completed["terminal_status"] == "completed"
        assert len(observations) >= 20
        assert f.store.current(f.identity.program_id).generation == 1
    finally:
        child.stdin.close()
        child.wait(timeout=5)
        assert child.returncode == 0, child.stderr.read()


def test_v10_standalone_read_only_import_and_read_leave_all_stores_unchanged(admitted):
    f = admitted
    parked = dispatch(f, f.operation, f.admitted)
    paths = [Path(pin[0]) for pin in f.v3.db.identities]
    before = [path.read_bytes() for path in paths]
    calls = (f.root / "calls.jsonl").read_bytes()
    code = """
import json,sys
from pathlib import Path
from universal_coding_agent.product.program_continuation_execution_store import (
    request_result,status,
)
assert not any(name in sys.modules for name in (
 'universal_coding_agent.safe_service',
 'universal_coding_agent.product.program_continuation_dispatch',
 'universal_coding_agent.product.program_source_acceptance',
 'universal_coding_agent.product.program_orchestrator',
 'universal_coding_agent.providers.fake'))
result=request_result(Path(sys.argv[1]),sys.argv[2],'discover-43')
view=status(Path(sys.argv[1]),sys.argv[2],sys.argv[3],limit=1)
assert view['current_authority_verified'] is False and len(view['receipts']) == 1
assert view['next_sequence'] == 1
print(json.dumps(result,sort_keys=True))
"""
    done = subprocess.run(
        [sys.executable, "-B", "-c", code, str(paths[0]), f.identity.program_id, f.operation],
        text=True,
        capture_output=True,
        timeout=10,
        env={**os.environ, "PYTHONPATH": str(Path(__file__).parents[1] / "src")},
    )
    assert done.returncode == 0, done.stderr
    assert json.loads(done.stdout) == parked
    assert [path.read_bytes() for path in paths] == before
    assert (f.root / "calls.jsonl").read_bytes() == calls


@pytest.mark.parametrize(
    "malformed",
    [
        "extra",
        "missing",
        "duplicate",
        "depth",
        "scalar",
        "float",
        "encoding",
        "flags",
        "state",
        "epoch",
    ],
)
def test_v10_strict_metadata_records_reject_malformed_input(admitted, malformed):
    from universal_coding_agent.product.program_continuation_execution_store import parse_record

    value = dict(admitted.admitted)
    if malformed == "extra":
        value["owner_token"] = "never-allowed"
    elif malformed == "missing":
        del value["consumer_bound"]
    elif malformed == "scalar":
        value["request_id"] = "a" * 4097
    elif malformed == "float":
        value["epoch"] = 0.0
    elif malformed == "flags":
        value["execution_authorized"] = True
    elif malformed == "state":
        value["state"] = "ready_to_execute"
    elif malformed == "epoch":
        value["epoch"] = True
    raw = canonical(value)
    if malformed == "duplicate":
        raw = b'{"schema":"unknown",' + raw[1:]
    elif malformed == "depth":
        raw = b"[" * 100 + b"0" + b"]" * 100
    elif malformed == "encoding":
        raw = raw + b"\n"
    with pytest.raises(ValueError):
        parse_record(raw, admitted.admitted["schema"])


if __name__ == "__main__":
    _process_stage(sys.argv[1], Path(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5])
