"""Independent host processes exercise the real HTTP command ownership boundary."""

import json
import sqlite3
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, wait
from pathlib import Path

import httpx
import pytest
from test_local_product_api import (
    PREFIX,
    PROGRAM,
    action_fields,
    arm,
    artifact,
    calls,
    fixture,
    free_port,
    journey,
    post,
    request_payload,
    server,
    sql,
)


def await_boundary(root):
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        if (root / "fault-hit").exists():
            return
        time.sleep(0.02)
    pytest.fail("Real host did not reach the requested finite boundary")


def test_h07_all_nine_commands_two_host_processes_exact_replay(tmp_path):
    port = free_port()
    config = fixture(tmp_path, port)
    saved = {}
    actions = (
        ("initialize_source", "initialize-42"),
        ("start_first_phase", "discover-42"),
        ("decide_first_scope", "scope-43"),
        ("preview_first_source", "preview-43"),
        ("decide_first_source", "accept-43"),
        ("start_continuation", "discover-43"),
        ("decide_continuation_scope", "scope-44"),
        ("preview_final_source", "preview-44"),
        ("decide_final_source", "accept-44"),
    )
    # Both listeners use the identical immutable canonical Host/Origin. The
    # separate TCP ports let the test address each independent process exactly.
    with (
        server(tmp_path, port) as first,
        server(tmp_path, port, number=2, listen_port=free_port()) as second,
    ):
        assert first.fixture_process.pid != second.fixture_process.pid
        with ThreadPoolExecutor(max_workers=1) as executor:
            for index, (action, request) in enumerate(actions):
                owner, observer = (first, second) if index % 2 == 0 else (second, first)
                fields = action_fields(action, saved, config)
                if "approval_id" in fields:
                    fields["approval_id"] = "approve-" + request
                payload = request_payload(owner, action, request, **fields)
                (tmp_path / "fault-hit").unlink(missing_ok=True)
                (tmp_path / "fault-release").unlink(missing_ok=True)
                arm(tmp_path, action, "after_response", mode="block")
                future = executor.submit(post, owner, payload)
                try:
                    await_boundary(tmp_path)
                    before = calls(tmp_path)
                    pending = post(observer, payload)
                    assert pending.status_code == 202, pending.text
                    assert observer.get(PREFIX + "/requests/" + request).content == pending.content
                    assert (
                        post(observer, {**payload, "request_id": "bypass-" + request}).status_code
                        == 409
                    )
                    assert post(observer, {**payload, "expected_revision": 99}).status_code == 409
                    assert calls(tmp_path) == before
                finally:
                    (tmp_path / "fault-release").write_text("release")
                result = future.result(timeout=30)
                assert result.status_code == 200, result.text
                assert post(observer, payload).content == result.content
                saved[request] = {
                    "payload": payload,
                    "response": result.json(),
                    "raw": result.content,
                }
    assert sql(tmp_path, "SELECT generation FROM program_source_heads") == [(2,)]
    assert len(sql(tmp_path, "SELECT * FROM local_product_requests_v1")) == 9
    roles = [json.loads(line)["role"] for line in calls(tmp_path).splitlines()]
    assert (
        roles.count("solution_discovery")
        == roles.count("implementer")
        == roles.count("reviewer")
        == 2
    )
    assert (tmp_path / "actual-applies.jsonl").read_text().splitlines() == ["applied"] * 2
    assert (
        sorted((tmp_path / "trusted-tests.jsonl").read_text().splitlines())
        == ["increment"] * 2 + ["preserved"] * 2
    )


@pytest.mark.parametrize(
    "action,until", [("start_first_phase", "initialize-42"), ("decide_first_scope", "discover-42")]
)
def test_h08_external_kill_after_actual_return_does_not_adopt_checkpoint(tmp_path, action, until):
    port = free_port()
    config = fixture(tmp_path, port)
    with server(tmp_path, port) as client, ThreadPoolExecutor(max_workers=1) as executor:
        saved = journey(client, config, until=until)
        payload = request_payload(
            client, action, "externally-killed", **action_fields(action, saved, config)
        )
        arm(tmp_path, action, "first_outer_returned", mode="block")
        future = executor.submit(post, client, payload)
        await_boundary(tmp_path)
        client.fixture_process.kill()
        with pytest.raises(httpx.TransportError):
            future.result(timeout=10)
    before = calls(tmp_path)
    assert sql(tmp_path, "SELECT status FROM program_executions") == [
        ("completed" if action == "decide_first_scope" else "awaiting_scope_approval",)
    ]
    # Even administrative removal of the dead worker does not clear the claim.
    worker_db = tmp_path / "product" / "lifecycle-reservations.sqlite"
    code = (
        "import sqlite3,sys; c=sqlite3.connect(sys.argv[1]); "
        "c.execute('DELETE FROM lifecycle_worker_ownership'); c.commit()"
    )
    removed = subprocess.run(
        [sys.executable, "-c", code, str(worker_db)], capture_output=True, text=True
    )
    assert removed.returncode == 0, removed.stderr
    with server(tmp_path, port, number=2) as client:
        assert post(client, payload).status_code == 202
        assert post(client, {**payload, "request_id": "new-owner-cannot-adopt"}).status_code == 409
        assert sql(tmp_path, "SELECT generation FROM program_source_heads") == [(0,)]
        assert calls(tmp_path) == before


def test_h10_independent_http_control_cannot_take_the_live_worker(tmp_path):
    port = free_port()
    config = fixture(tmp_path, port)
    with server(tmp_path, port) as owner:
        saved = journey(owner, config, until="initialize-42")
        payload = request_payload(
            owner,
            "start_first_phase",
            "control-race",
            **action_fields("start_first_phase", saved, config),
        )
        with (
            server(tmp_path, port, number=2, listen_port=free_port()) as control,
            ThreadPoolExecutor(max_workers=1) as executor,
        ):
            arm(tmp_path, "start_first_phase", "first_outer_returned", mode="block")
            future = executor.submit(post, owner, payload)
            try:
                await_boundary(tmp_path)
                route = "/api/programs/" + PROGRAM
                response = control.post(
                    route + "/pause", json={"reason": "Independent public control race"}
                )
                assert response.status_code == 400, response.text
                response = control.post(route + "/resume", json={})
                assert response.status_code == 400, response.text
            finally:
                (tmp_path / "fault-release").write_text("release")
            result = future.result(timeout=10)
            assert result.status_code == 200, result.text
            assert post(control, payload).content == result.content
            assert sql(tmp_path, "SELECT pending_request_id FROM local_product_heads_v1") == [
                (None,)
            ]
            assert sql(tmp_path, "SELECT generation FROM program_source_heads") == [(0,)]


@pytest.mark.parametrize(
    "action,until",
    [
        ("initialize_source", None),
        ("decide_first_source", "preview-43"),
        ("decide_final_source", "preview-44"),
    ],
)
def test_h10_atomic_completion_excludes_real_controls_recovery_worker_and_wal_writers(
    tmp_path, action, until
):
    port = free_port()
    config = fixture(tmp_path, port)
    remote_path = tmp_path / "product" / "private-remote-operations.sqlite"
    assert remote_path.is_file()
    with sqlite3.connect(remote_path) as remote:
        assert remote.execute("PRAGMA journal_mode=WAL").fetchone()[0] == "wal"
    lifecycle_path = tmp_path / "product" / "lifecycle-reservations.sqlite"
    worker_code = r"""
import json,sys
from pathlib import Path
from universal_coding_agent.product.lifecycle_reservations import DurableLifecycleReservationStore
store=DurableLifecycleReservationStore(Path(sys.argv[1]))
store.connection.execute('PRAGMA busy_timeout=100')
print('ready',flush=True); sys.stdin.readline()
try:
    store.reserve_program_worker(sys.argv[2])
    print('unexpected-owner',flush=True)
except Exception as exc:
    print(json.dumps({'error':str(exc),'cause':type(exc.__cause__).__name__}),flush=True)
finally:
    store.close()
"""
    with (
        server(tmp_path, port) as owner,
        server(tmp_path, port, number=2, listen_port=free_port()) as control,
        ThreadPoolExecutor(max_workers=6) as executor,
    ):
        saved = journey(owner, config, until=until) if until else {}
        payload = request_payload(
            owner, action, "atomic-writers", **action_fields(action, saved, config)
        )
        binding_sha = sql(tmp_path, "SELECT binding_sha256 FROM local_product_bindings_v1")[0][0]
        descriptor = json.loads(artifact(tmp_path, binding_sha))
        safe_path = Path(descriptor["stores"][4][0])
        worker = subprocess.Popen(
            [sys.executable, "-u", "-c", worker_code, str(lifecycle_path), PROGRAM],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        assert worker.stdout.readline().strip() == "ready"
        arm(tmp_path, action, "after_response", mode="block")
        effect = executor.submit(post, owner, payload)
        try:
            await_boundary(tmp_path)
            before = calls(tmp_path)
            pending = post(control, payload)
            assert pending.status_code == 202, pending.text
            candidates = control.get("/api/admin/lifecycle-recovery").json()["candidates"]
            candidate = next(c for c in candidates if c["target_type"] == "worker_ownership")
            recovery = {
                k: candidate[k] for k in ("target_type", "target_kind", "scope_id", "recovery_ref")
            }
            recovery.update(
                reason="Fixture adversarial premature recovery confirmation", confirmed=True
            )
            controls = [
                executor.submit(
                    control.post,
                    "/api/programs/" + PROGRAM + "/" + verb,
                    json={"reason": "Fixture concurrent control"} if verb != "resume" else {},
                )
                for verb in ("pause", "resume", "cancel")
            ]
            controls.append(
                executor.submit(control.post, "/api/admin/lifecycle-recovery", json=recovery)
            )
            worker.stdin.write("attempt\n")
            worker.stdin.flush()
            assert json.loads(worker.stdout.readline()) == {
                "error": "durable lifecycle reservation state is unavailable",
                "cause": "OperationalError",
            }
            assert worker.wait(timeout=5) == 0, worker.stderr.read()
            writer_code = (
                "import sqlite3,sys; c=sqlite3.connect(sys.argv[1],timeout=0.1); "
                "assert c.execute('PRAGMA journal_mode').fetchone()[0]=='wal'; "
                "c.execute('BEGIN IMMEDIATE'); c.rollback()"
            )
            for path in (safe_path, remote_path):
                writer = subprocess.run(
                    [sys.executable, "-c", writer_code, str(path)], capture_output=True, timeout=5
                )
                assert writer.returncode != 0 and b"database is locked" in writer.stderr
            done, pending_controls = wait(controls, timeout=60)
            assert not pending_controls, (
                f"{len(pending_controls)} of {len(controls)} control requests "
                "did not finish within the aggregate deadline"
            )
            assert done == set(controls)
            for future in controls:
                response = future.result(timeout=15)
                assert response.status_code in {400, 500}, response.text
            assert calls(tmp_path) == before
        finally:
            (tmp_path / "fault-release").write_text("release")
            if worker.poll() is None:
                worker.kill()
                worker.wait(timeout=5)
        result = effect.result(timeout=15)
        assert result.status_code == 200, result.text
        assert post(control, payload).content == result.content
        assert sql(tmp_path, "SELECT pending_request_id FROM local_product_heads_v1") == [(None,)]
