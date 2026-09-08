"""Recorded Product visibility against the real cumulative Program fixture."""

from __future__ import annotations

import json
import os
import subprocess
import sys

import pytest
from fastapi.testclient import TestClient
from test_program_source_dispatch import accept, close, first_phase, process, runtime
from test_program_source_dispatch import admitted as admitted
from test_web_api import (
    RecordingProgramExecutor,
    _approved_program,
    _policy,
    _program_execution_request,
    _provider,
)

from universal_coding_agent.core.models import RepositorySpec
from universal_coding_agent.core.remote_operations import (
    RemoteOperationDispositionOutcome,
    RemoteOperationState,
)
from universal_coding_agent.product import program_source_status as status_module
from universal_coding_agent.product.program_source_status import (
    ProgramSourceStatusError,
    program_source_status,
    require_legacy_program_route,
)
from universal_coding_agent.product.program_source_transitions import _canonical, _hash
from universal_coding_agent.product.workspace import ProductWorkspace
from universal_coding_agent.web.app import ProductWebRuntime, create_product_app


def fingerprint(root):
    return {str(p.relative_to(root)): _hash(p.read_bytes())
            for p in root.rglob("*") if p.is_file()}


def read(f, *, fresh=False):
    before = fingerprint(f.root)
    path, program = f.workspace.programs.database_path, f.identity.program_id
    if fresh:
        completed = subprocess.run(
            [sys.executable, "-B", "-c", """
import json, sys
from pathlib import Path
from universal_coding_agent.product.program_source_status import program_source_status
result = program_source_status(Path(sys.argv[1]), sys.argv[2])
assert 'universal_coding_agent.safe_service' not in sys.modules
assert 'universal_coding_agent.product.program_source_dispatch' not in sys.modules
print(json.dumps(result))
""", str(path), program],
            capture_output=True, text=True, timeout=15, check=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        result = json.loads(completed.stdout)
    else:
        result = program_source_status(path, program)
    # Includes origin Git, provider log, artifacts and SQLite contents. Reads do
    # not construct stores, create tables/files, reconcile or invoke providers.
    assert fingerprint(f.root) == before
    public = json.dumps(result)
    assert str(f.root) not in public and f.owner not in public
    assert all(key not in public for key in (
        "owner_token", "invocation", "capability", "repository_url", '"binding"',
    ))
    assert result["automatic_execution"] is False
    assert result["filesystem_verified"] is False
    assert result["source_bytes_verified"] is False
    assert result["current_authority_verified"] is False
    return result


def test_actual_42_43_44_history_and_terminal_acceptance_are_distinct(tmp_path):
    f = runtime(tmp_path, 42, create=True)
    try:
        initial = read(f)
        assert initial["accepted"]["generation"] == 0
        assert initial["dispatches"] == []
        require_legacy_program_route(f.workspace.programs.database_path, f.identity.program_id)
        operation = first_phase(f)
        admitted_status = read(f, fresh=True)
        assert admitted_status["accepted"]["generation"] == 1
        assert admitted_status["dispatches"][0]["state"] == "admitted"
    finally:
        close(f)
    f = runtime(tmp_path, 43)
    try:
        started = f.dispatch.dispatch(operation, owner_token=f.owner)
        pending = read(f, fresh=True)
        assert pending["dispatches"][0]["state"] == "awaiting_scope_approval"
        task = f.dispatch._json(started["task_sha256"])
        scope = f.safe.state(task["thread_id"])["values"]["scope_hash"]
        final = f.dispatch.approve_scope(
            operation, owner_token=f.owner, scope_sha256=scope,
            approved=True, approval_id="visibility-scope-44",
        )
        terminal = read(f)
        assert terminal["accepted"]["generation"] == 1
        assert terminal["dispatches"][0]["state"] == "terminal"
        assert terminal["dispatches"][0]["source_accepted"] is False
        accept(f, final["task_id"], "visibility-accept-44")
        accepted = read(f, fresh=True)
        assert accepted["accepted"]["generation"] == 2
        assert accepted["dispatches"][0]["source_accepted"] is True
        assert [x["generation"] for x in accepted["lineage"]] == [0, 1, 2]
        assert len({x["source_sha256"] for x in accepted["lineage"]}) == 3
        assert accepted["origin"] == initial["origin"]
        assert accepted["matches_current_plan"] is True
        dispatch = accepted["dispatches"][0]
        assert dispatch["derived_git_commit_sha"] != accepted["origin"]["git_commit_sha"]
        assert dispatch["source_sha256"] == accepted["lineage"][1]["source_sha256"]
        assert accepted["lineage"][2]["predecessor_sha256"] == dispatch["source_sha256"]
        assert (f.source / "app.py").read_bytes().endswith(b"return 42\n")
    finally:
        close(f)


def test_unrelated_program_does_not_inherit_source_history(admitted):
    f = admitted
    _approved_program(f.workspace, "unrelated-program")
    unrelated = program_source_status(f.workspace.programs.database_path, "unrelated-program")
    assert unrelated["status"] == "uninitialized"
    assert unrelated["lineage"] == unrelated["dispatches"] == []
    require_legacy_program_route(f.workspace.programs.database_path, "unrelated-program")


def test_prepared_source_blocks_legacy_start_without_granting_dispatch(tmp_path):
    f = runtime(tmp_path, 42, create=True)
    try:
        first_phase(f, admit=False)
        status = read(f)
        assert status["accepted"]["generation"] == 1 and status["dispatches"] == []
        with pytest.raises(ValueError, match="host service"):
            require_legacy_program_route(f.workspace.programs.database_path, f.identity.program_id)
    finally:
        close(f)


@pytest.mark.parametrize("case", [
    "missing", "hash", "oversized", "field", "generation", "head-source",
    "receipt-task", "candidate-program", "state", "execution-base", "admission-program",
    "admission-task", "admission-phase", "admission-host", "admission-source",
    "admission-receipt", "admission-operation", "admission-boolean", "rows", "budget",
    "missing-dispatch-table", "missing-dispatch-row", "missing-execution", "missing-base",
    "missing-dispatch-and-base", "missing-both-tables",
])
def test_corrupt_or_excessive_metadata_never_falls_back_to_legacy(admitted, monkeypatch, case):
    f, con = admitted, admitted.store.connection
    head = con.execute("SELECT * FROM program_source_heads").fetchone()
    digest = head["initial_receipt_sha256"]
    with con:
        if case == "missing":
            con.execute("DELETE FROM program_source_artifacts WHERE sha256=?", (digest,))
        elif case in {"hash", "oversized"}:
            content = b"bad" if case == "hash" else b"x" * (status_module.MAX_METADATA_BYTES + 1)
            con.execute("UPDATE program_source_artifacts SET content=? WHERE sha256=?",
                        (content, digest))
        elif case == "field":
            con.execute("UPDATE program_source_heads SET receipt_sha256=?", ("f" * 129,))
        elif case == "generation":
            con.execute("UPDATE program_source_heads SET generation=3")
        elif case == "head-source":
            con.execute("UPDATE program_source_heads SET source_sha256=?", ("f" * 64,))
        elif case == "receipt-task":
            con.execute("UPDATE program_source_acceptances SET task_id='other-task'")
        elif case == "candidate-program":
            con.execute("UPDATE program_source_candidates SET program_id='other-program'")
        elif case == "state":
            con.execute("UPDATE program_source_dispatches SET state='unknown'")
        elif case == "missing-dispatch-table":
            con.execute("DROP TABLE program_source_dispatches")
        elif case == "missing-dispatch-row":
            con.execute("DELETE FROM program_source_dispatches")
        elif case == "missing-execution":
            con.execute("DELETE FROM program_executions WHERE phase_id='phase-2'")
        elif case == "missing-base":
            con.execute("DELETE FROM program_execution_bases")
        elif case == "missing-dispatch-and-base":
            con.execute("DELETE FROM program_source_dispatches")
            con.execute("DELETE FROM program_execution_bases")
        elif case == "missing-both-tables":
            con.execute("DROP TABLE program_source_dispatches")
            con.execute("DROP TABLE program_execution_bases")
        elif case == "execution-base":
            con.execute("UPDATE program_executions SET expected_base_sha=?", ("f" * 40,))
        elif case.startswith("admission-"):
            row = con.execute("SELECT admission_sha256 FROM program_source_dispatches").fetchone()
            admission = f.dispatch._json(row[0])
            field, value = {
                "program": ("program_id", "other-program"),
                "task": ("task_id", "other-task"),
                "phase": ("phase_id", "other-phase"),
                "host": ("host_sha256", "f" * 64),
                "source": ("source_sha256", "f" * 64),
                "receipt": ("acceptance_receipt_sha256", "f" * 64),
                "operation": ("operation_id", "f" * 32),
                "boolean": ("generation", True),
            }[case.removeprefix("admission-")]
            admission[field] = value
            raw = _canonical(admission)
            con.execute("INSERT INTO program_source_artifacts VALUES (?, ?)", (_hash(raw), raw))
            con.execute("UPDATE program_source_dispatches SET admission_sha256=?", (_hash(raw),))
        elif case == "rows":
            for i in range(status_module.MAX_RECORDS):
                con.execute("INSERT INTO program_source_acceptances VALUES (?, ?, ?, ?, ?)",
                            (f"{i:064x}", "a" * 64, "b" * 64,
                             f.identity.program_id, f"extra-task-{i}"))
        elif case == "budget":
            monkeypatch.setattr(status_module, "MAX_TOTAL_METADATA_BYTES", 1)
    before = fingerprint(f.root)
    with pytest.raises(ProgramSourceStatusError, match="metadata is unavailable"):
        require_legacy_program_route(f.workspace.programs.database_path, f.identity.program_id)
    assert fingerprint(f.root) == before


def test_missing_database_is_not_created(tmp_path):
    missing = tmp_path / "missing.sqlite3"
    with pytest.raises(ProgramSourceStatusError):
        program_source_status(missing, "program-1")
    assert not missing.exists()


@pytest.mark.parametrize("metadata", ["valid", "terminal-pending", "missing-both"])
def test_actual_http_reads_and_rejects_v2_routes_without_touching_ownership(admitted, metadata):
    f = admitted
    started = f.dispatch.dispatch(f.operation, owner_token=f.owner)
    with f.store.connection as con:
        if metadata == "terminal-pending":
            con.execute("UPDATE program_source_dispatches SET state='terminal'")
        elif metadata == "missing-both":
            con.execute("DELETE FROM program_source_dispatches")
            con.execute("DELETE FROM program_execution_bases")
    web = ProductWebRuntime(f.workspace, f.root / "web")
    client = TestClient(create_product_app(web))
    prefix = f"/api/programs/{f.identity.program_id}/executions"
    before = fingerprint(f.root)
    try:
        response = client.get(prefix)
        if metadata == "valid":
            assert response.status_code == 200
            assert response.headers["cache-control"] == "no-store"
            assert response.json()["source"]["dispatches"][0]["state"] == "awaiting_scope_approval"
        else:
            assert response.status_code == 400
            assert response.json()["detail"] == "recorded Program source metadata is unavailable"
        for route, payload in (
            ("/start-next", _program_execution_request(f.identity.requirement_sha256)),
            (f"/{started['task_id']}/continue",
             {"current_requirement_hash": f.identity.requirement_sha256, "approved": True}),
        ):
            rejected = client.post(prefix + route, json=payload)
            assert rejected.status_code == 400
            assert ("host service" if metadata == "valid" else "metadata is unavailable") in (
                rejected.json()["detail"]
            )
        assert web._program_worker_tokens == {}
        assert fingerprint(f.root) == before
    finally:
        client.close()
        web.executor.shutdown()


@pytest.mark.parametrize("state,status,safe", [
    ("terminal", "starting", ""),
    ("terminal", "failed", "awaiting_scope_approval"),
    ("terminal", "completed", "blocked"),
    ("admitted", "completed", "completed"),
    ("awaiting_scope_approval", "starting", ""),
    ("resume_started", "failed", "awaiting_scope_approval"),
])
def test_recognized_but_inconsistent_dispatch_execution_states_reject(
    admitted, state, status, safe,
):
    f = admitted
    with f.store.connection as con:
        con.execute("UPDATE program_source_dispatches SET state=?", (state,))
        con.execute(
            "UPDATE program_executions SET status=?, safe_status=? WHERE phase_id='phase-2'",
            (status, safe),
        )
    before = fingerprint(f.root)
    with pytest.raises(ProgramSourceStatusError):
        program_source_status(f.workspace.programs.database_path, f.identity.program_id)
    assert fingerprint(f.root) == before


@pytest.mark.parametrize("crash,state", [
    ("discovery", "discovery_started"), ("discovery-result", "discovered"),
    ("scope-checkpoint", "safe_started"), ("terminal-checkpoint", "resume_started"),
])
def test_actual_inflight_dispatch_keeps_prior_program_result_readable(admitted, crash, state):
    f = admitted
    (f.root / "operation.txt").write_text(f.operation)
    action = "dispatch"
    if state == "resume_started":
        process(f.root, "dispatch")
        action = "approve"
    process(f.root, action, crash, expected=73)
    assert read(f, fresh=True)["dispatches"][0]["state"] == state


@pytest.mark.parametrize("outcome", [
    "cancel", "remote-cancelled", "remote-failed", "scope-rejected",
])
def test_actual_stopped_execution_remains_readable_without_advancing_dispatch(admitted, outcome):
    f = admitted
    started = f.dispatch.dispatch(f.operation, owner_token=f.owner)
    if outcome == "cancel":
        f.workspace.programs.cancel(f.identity.program_id)
    elif outcome.startswith("remote-"):
        status = outcome.removeprefix("remote-")
        f.workspace.remote_operations.register(
            task_id=started["task_id"], thread_id=started["thread_id"],
            transport="openai_responses", transport_scope=f"sha256:{'a' * 64}",
            operation_id="visibility-disposition", base_sha="b" * 40,
            status=status, state=RemoteOperationState.TERMINAL,
        )
        snapshot = f.workspace.remote_operations.public_snapshot(started["task_id"])
        disposition = f.workspace.control.record_remote_operation_disposition(
            snapshot, RemoteOperationDispositionOutcome(status),
            reason="Recorded terminal provider result", confirmed=True,
            program_id=f.identity.program_id, phase_id="phase-2", slice_id="",
        )
        f.workspace.programs.record_remote_operation_disposition(disposition)
    else:
        task = f.dispatch._json(started["task_sha256"])
        scope = f.safe.state(task["thread_id"])["values"]["scope_hash"]
        f.dispatch.approve_scope(f.operation, owner_token=f.owner, scope_sha256=scope,
                                 approved=False, approval_id="visibility-rejected")
    status = read(f, fresh=True)
    assert status["dispatches"][0]["state"] == (
        "terminal" if outcome == "scope-rejected" else "awaiting_scope_approval"
    )
    assert status["dispatches"][0]["source_accepted"] is False
    # The original root execution is still classifiable as v1 after source advancement.
    root_task = status["lineage"][1]["task_id"]
    require_legacy_program_route(
        f.workspace.programs.database_path, f.identity.program_id, root_task,
    )


@pytest.mark.parametrize("action", ["start-next", "continue"])
def test_queued_legacy_worker_rechecks_metadata_and_releases_only_its_ownership(tmp_path, action):
    queued = []

    class Queue:
        def submit(self, function, *args):
            queued.append((function, args))

        def shutdown(self, **kwargs):
            pass

    workspace = ProductWorkspace.create(tmp_path / "product", _provider())
    program = "program-queued-source"
    requirement = _approved_program(workspace, program)
    executor = RecordingProgramExecutor()
    route = "start-next"
    request = _program_execution_request(requirement)
    if action == "continue":
        binding = workspace.programs.start_next_execution(
            program_id=program, current_requirement_hash=requirement,
            repository=RepositorySpec(url="https://example.test/repo.git", base_ref="fixture"),
            policy=_policy(), test_profiles=("trusted-contract",), executor=executor,
        )
        route = f"{binding.task_id}/continue"
        request = {"current_requirement_hash": requirement, "approved": True}
    web = ProductWebRuntime(workspace, tmp_path / "web", executor=Queue())
    with TestClient(create_product_app(web)) as client:
        response = client.post(f"/api/programs/{program}/executions/{route}", json=request)
        assert response.status_code == 202
        assert web._program_worker_tokens[program]
        # The request-time read passed. A later partial store must still block
        # the queued worker before constructing an execution service/provider.
        with workspace.programs.connection:
            workspace.programs.connection.execute("CREATE TABLE program_source_heads (bad TEXT)")
        function, args = queued.pop()
        function(*args)
        assert not web._program_worker_tokens
        assert web._program_execution_runs[program]["error_type"] == "ProgramSourceStatusError"
        assert executor.resumes == []
        assert len(executor.starts) == (1 if action == "continue" else 0)
        # Release succeeded: a subsequent worker may reserve and release normally.
        owner = workspace.lifecycle_reservations.reserve_program_worker(program)
        workspace.lifecycle_reservations.release_program_worker(program, owner)
