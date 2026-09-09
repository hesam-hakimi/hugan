"""Pure complete recorded reads and bounded selection against real on-disk stores."""

import hashlib
import json
import sqlite3
import subprocess
import sys
import tracemalloc
from pathlib import Path

import pytest
from test_local_product_api import (
    PREFIX,
    PROGRAM,
    PROJECT,
    artifact,
    calls,
    database,
    fixture,
    free_port,
    journey,
    post,
    server,
    sql,
)

from universal_coding_agent.product.local_product_binding import LocalProductBinding
from universal_coding_agent.product.local_product_status import request_result, status
from universal_coding_agent.product.program_continuation_execution_store import (
    canonical,
    composed_read_budget,
    sha,
)
from universal_coding_agent.product.program_source_acceptance_v2_store import Reader


def bytes_snapshot(root):
    return {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in root.rglob("*")
        if p.is_file()
    }


def test_h11_fresh_pure_process_full_lineage_and_missing_stores_never_create(tmp_path):
    port = free_port()
    config = fixture(tmp_path, port)
    with server(tmp_path, port) as client:
        saved = journey(client, config, until="accept-44")
    public = saved["accept-44"]["payload"]
    full = {**public, "project_id": PROJECT, "program_id": PROGRAM}
    expected = saved["accept-44"]["raw"]
    code = r"""
import builtins,json,subprocess,sys
from pathlib import Path
real_import = builtins.__import__
blocked = ('universal_coding_agent.product.local_product_commands',
 'universal_coding_agent.product.local_product_first_phase',
 'universal_coding_agent.product.local_product_first_source',
 'universal_coding_agent.product.program_source_acceptance',
 'universal_coding_agent.product.program_source_acceptance_v2',
 'universal_coding_agent.product.program_continuation_dispatch',
 'universal_coding_agent.product.workspace','universal_coding_agent.safe_service',
 'universal_coding_agent.discovered_safe_service')
def guarded(name,*args,**kwargs):
    if name in blocked or name.startswith((
            'universal_coding_agent.providers.', 'langgraph', 'msgpack')):
        raise AssertionError('Effectful import or checkpoint decoder in recorded read: '+name)
    return real_import(name,*args,**kwargs)
builtins.__import__ = guarded
def fatal(*args,**kwargs): raise AssertionError('Process/Git effect in recorded read')
subprocess.Popen = subprocess.run = subprocess.check_output = fatal
from universal_coding_agent.product.local_product_status import (
    status,request_result,evidence,project_result)
payload=json.loads(sys.argv[2]); path=Path(sys.argv[1])
result=status(path,payload['project_id'],payload['program_id'])
assert result['accepted']['generation']==2
assert all(value is False for value in result['authority'].values())
assert project_result(path,payload['project_id'],enabled=False)['commands_enabled'] is False
code,raw=request_result(path,payload)
assert code==200
sys.stdout.buffer.write(raw)
"""
    with server(tmp_path, port, number=2):
        before = bytes_snapshot(tmp_path)
        result = subprocess.run(
            [sys.executable, "-c", code, str(database(tmp_path)), json.dumps(full)],
            capture_output=True,
            timeout=15,
        )
        assert result.returncode == 0, result.stderr.decode()
        assert result.stdout == expected
        assert bytes_snapshot(tmp_path) == before
    before = bytes_snapshot(tmp_path)
    with pytest.raises((ValueError, OSError, sqlite3.Error)):
        status(database(tmp_path), PROJECT, PROGRAM)
    assert bytes_snapshot(tmp_path) == before
    binding_sha = sql(tmp_path, "SELECT binding_sha256 FROM local_product_bindings_v1")[0][0]
    descriptor = json.loads(artifact(tmp_path, binding_sha))
    for pin in descriptor["stores"]:
        path = Path(pin[0])
        moved = path.with_name(path.name + ".retained-preimage")
        path.rename(moved)
        try:
            before = bytes_snapshot(tmp_path)
            with pytest.raises((ValueError, OSError, sqlite3.Error)):
                status(
                    database(tmp_path) if path.name != "programs.sqlite" else path, PROJECT, PROGRAM
                )
            with pytest.raises((ValueError, OSError, sqlite3.Error)):
                LocalProductBinding.load(tmp_path / "binding.json")
            assert not path.exists()
            assert bytes_snapshot(tmp_path) == before
        finally:
            moved.rename(path)
    with server(tmp_path, port, number=3):
        assert request_result(database(tmp_path), full)[1] == expected


@pytest.mark.parametrize("until", ["initialize-42", "accept-44"])
def test_h11_h12_unknown_or_partial_namespaces_deny_http_and_replay(tmp_path, until):
    port = free_port()
    config = fixture(tmp_path, port)
    with server(tmp_path, port) as client:
        saved = journey(client, config, until=until)
        payload = saved[until]["payload"]
        statements = [
            (
                "CREATE TABLE program_source_continuation_heads_v99 (program_id TEXT)",
                "DROP TABLE program_source_continuation_heads_v99",
            ),
            ("CREATE VIEW program_source_unknown AS SELECT 1", "DROP VIEW program_source_unknown"),
            (
                "CREATE TRIGGER unknown_source_trigger AFTER INSERT ON program_source_heads "
                "BEGIN SELECT 1; END",
                "DROP TRIGGER unknown_source_trigger",
            ),
        ]
        for mutate, restore in statements:
            sql(tmp_path, mutate)
            try:
                assert client.get(PREFIX).status_code == 409
                assert post(client, payload).status_code == 409
            finally:
                sql(tmp_path, restore)
        name = "program_source_continuation_requests_v3"
        found = sql(tmp_path, "SELECT sql FROM sqlite_master WHERE name=?", (name,))
        if not found:
            sql(tmp_path, f"CREATE TABLE {name} (program_id TEXT)")
            try:
                assert client.get(PREFIX).status_code == 409
                assert post(client, payload).status_code == 409
            finally:
                sql(tmp_path, f"DROP TABLE {name}")
        else:
            statement = found[0][0]
            rows = sql(tmp_path, f"SELECT * FROM {name}")
            sql(tmp_path, f"DROP TABLE {name}")
            try:
                assert client.get(PREFIX).status_code == 409
                assert post(client, payload).status_code == 409
            finally:
                sql(tmp_path, statement)
                for row in rows:
                    sql(tmp_path, f"INSERT INTO {name} VALUES ({','.join('?' for _ in row)})", row)
        sql(tmp_path, "UPDATE local_product_heads_v1 SET next_sequence=100000")
        try:
            tracemalloc.start()
            with pytest.raises(ValueError):
                status(database(tmp_path), PROJECT, PROGRAM)
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            assert peak < 1_048_576
        finally:
            sql(tmp_path, "UPDATE local_product_heads_v1 SET next_sequence=?", (len(saved),))
        assert post(client, payload).content == saved[until]["raw"]


def test_h12_composed_metadata_budget_and_sql_selected_growth(tmp_path):
    path = tmp_path / "bounded.sqlite"
    with sqlite3.connect(path) as db:
        db.execute("PRAGMA journal_mode=WAL")
        db.execute(
            "CREATE TABLE program_source_artifacts (sha256 TEXT PRIMARY KEY, content BLOB NOT NULL)"
        )
        values = [canonical({"index": i, "padding": "x" * 60_000}) for i in range(18)]
        db.executemany(
            "INSERT INTO program_source_artifacts VALUES (?,?)", [(sha(raw), raw) for raw in values]
        )
    with composed_read_budget(), sqlite3.connect(path) as db:
        for raw in values[:17]:
            assert Reader(db).raw(sha(raw)) == raw
        with pytest.raises(ValueError, match="aggregate"):
            Reader(db).raw(sha(values[17]))
        with pytest.raises(ValueError, match="cached"):
            Reader(db).raw(sha(values[0]), maximum=32)

    class RacingConnection(sqlite3.Connection):
        grew = False

        def execute(self, statement, args=()):
            if not self.grew and "THEN substr(content,1,?)" in statement:
                self.grew = True
                writer = (
                    "import sqlite3,sys; c=sqlite3.connect(sys.argv[1]); "
                    "c.execute('UPDATE program_source_artifacts "
                    "SET content=zeroblob(10000000) "
                    "WHERE sha256=?',(sys.argv[2],)); c.commit()"
                )
                completed = subprocess.run(
                    [sys.executable, "-c", writer, str(path), sha(values[0])],
                    capture_output=True,
                    timeout=10,
                )
                assert completed.returncode == 0, completed.stderr
            return super().execute(statement, args)

    with sqlite3.connect(path, isolation_level=None, factory=RacingConnection) as db:
        tracemalloc.start()
        with pytest.raises(ValueError, match="bytes differ"):
            Reader(db).raw(sha(values[0]))
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        assert db.grew and peak < 1_048_576


def test_h11_read_guard_keeps_existing_wal_during_last_writer_close(tmp_path):
    from universal_coding_agent.product.local_product_status import READ_URI, read_guard

    path = tmp_path / "guarded.sqlite"
    code = (
        "import sqlite3,sys; c=sqlite3.connect(sys.argv[1]); "
        "c.execute('PRAGMA journal_mode=WAL'); c.execute('CREATE TABLE t(x)'); "
        "c.execute('INSERT INTO t VALUES (43)'); c.commit(); print('ready',flush=True); "
        "sys.stdin.readline(); c.close(); print('closed',flush=True)"
    )
    process = subprocess.Popen(
        [sys.executable, "-u", "-c", code, str(path)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    )
    try:
        assert process.stdout.readline().strip() == "ready"
        with read_guard(path):
            paths = [path, Path(str(path) + "-wal"), Path(str(path) + "-shm")]
            before = {p: p.read_bytes() for p in paths}
            process.stdin.write("close\n")
            process.stdin.flush()
            assert process.stdout.readline().strip() == "closed"
            assert process.wait(timeout=5) == 0
            assert Path(str(path) + "-wal").is_file()
            assert Path(str(path) + "-shm").is_file()
            with sqlite3.connect(path.as_uri() + READ_URI, uri=True) as db:
                assert db.execute("SELECT x FROM t").fetchall() == [(43,)]
            assert {p: p.read_bytes() for p in paths} == before
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=5)


def test_h11_http_after_external_safe_wal_write_is_byte_pure_and_v3_counter_is_bounded(tmp_path):
    port = free_port()
    config = fixture(tmp_path, port)
    with server(tmp_path, port) as client:
        saved = journey(client, config, until="discover-43")
        binding_sha = sql(tmp_path, "SELECT binding_sha256 FROM local_product_bindings_v1")[0][0]
        descriptor = json.loads(artifact(tmp_path, binding_sha))
        safe = Path(descriptor["stores"][4][0])
        with sqlite3.connect(safe) as writer:
            writer.execute("CREATE TABLE unrelated_read_observation (n INTEGER)")
            writer.execute("INSERT INTO unrelated_read_observation VALUES (43)")
            writer.commit()
            paths = [safe, Path(str(safe) + "-wal"), Path(str(safe) + "-shm")]
            before = {p: p.read_bytes() for p in paths}
            provider_before = calls(tmp_path)
            response = client.get(PREFIX)
            assert response.status_code == 200, response.text
            assert (
                post(client, saved["discover-43"]["payload"]).content == saved["discover-43"]["raw"]
            )
            assert {p: p.read_bytes() for p in paths} == before
            assert calls(tmp_path) == provider_before
        original = sql(tmp_path, "SELECT sequence FROM program_source_continuation_heads_v3")[0][0]
        sql(tmp_path, "UPDATE program_source_continuation_heads_v3 SET sequence=100000")
        try:
            tracemalloc.start()
            with pytest.raises(ValueError):
                status(database(tmp_path), PROJECT, PROGRAM)
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            assert peak < 1_048_576
            assert client.get(PREFIX).status_code == 409
        finally:
            sql(tmp_path, "UPDATE program_source_continuation_heads_v3 SET sequence=?", (original,))
        assert client.get(PREFIX).status_code == 200


def test_h11_observer_exit_preserves_another_connection_posix_reservation(tmp_path):
    from universal_coding_agent.product.local_product_status import read_guard

    path = tmp_path / "reserved.sqlite"
    writer = sqlite3.connect(path)
    writer.execute("CREATE TABLE t(x)")
    writer.commit()
    writer.execute("BEGIN IMMEDIATE")
    try:
        with read_guard(path):
            pass
        code = (
            "import sqlite3,sys; c=sqlite3.connect(sys.argv[1],timeout=0.05); "
            "c.execute('BEGIN IMMEDIATE'); c.rollback()"
        )
        contender = subprocess.run([sys.executable, "-c", code, str(path)], capture_output=True)
        assert contender.returncode != 0 and b"database is locked" in contender.stderr
    finally:
        writer.rollback()
        writer.close()
    contender = subprocess.run([sys.executable, "-c", code, str(path)], capture_output=True)
    assert contender.returncode == 0, contender.stderr
