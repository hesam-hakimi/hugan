from __future__ import annotations

import errno
import json
import os
import sqlite3
import stat
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace

import pytest
from test_program_source_acceptance import (
    _accept,
    _git,
    _prepare,
    _service,
)
from test_program_source_acceptance import executed as executed

from universal_coding_agent.product.program_source_materialization import (
    ProgramSourceMaterializationService,
)
from universal_coding_agent.product.program_source_transitions import (
    ProgramSourceError,
    _canonical,
    _hash,
)
from universal_coding_agent.sandbox.owned_source import OwnedSourcePolicy


def _admitted(f, policy=None):
    accepted = _accept(f, _prepare(f))
    materializer = ProgramSourceMaterializationService(f.acceptance, policy)
    begin = materializer.begin(f.identity.program_id,
                               acceptance_receipt_sha256=_hash(_canonical(accepted)),
                               owner_token=f.owner)
    operation_id = begin["operation_id"]
    return SimpleNamespace(service=materializer, operation_id=operation_id, begin=begin,
                           accepted=accepted, f=f,
                           directory=materializer.filesystem.root / ("source-" + operation_id))


def _reconcile(m):
    return m.service.reconcile(m.operation_id, owner_token=m.f.owner)


def _allocate(m):
    m.service._allocate(m.operation_id, m.f.owner, m.service.filesystem.deadline())
    assert m.service.status(m.operation_id)["state"] == "allocated"


def _forbidden(*args, **kwargs):
    raise AssertionError("materialization must not invoke a provider, Git or project command")


@pytest.mark.parametrize("executed", [{"materialization_files": True}], indirect=True)
def test_actual_accepted_source_is_complete_exact_owned_and_separate_from_git(executed,
                                                                            monkeypatch):
    f = executed
    m = _admitted(f)
    assert not m.directory.exists()
    assert m.begin["state"] == "intent" and m.begin["completion_sha256"] is None
    before_bindings = f.workspace.programs.execution_bindings(f.identity.program_id)
    original_head = _git(f.source, "rev-parse", "HEAD")
    with monkeypatch.context() as patch:
        patch.setattr(f.provider, "invoke", _forbidden)
        patch.setattr(subprocess, "run", _forbidden)
        receipt = _reconcile(m)
        assert _reconcile(m) == receipt
        assert m.service.verify_complete(m.operation_id, owner_token=f.owner) == receipt
    assert receipt["materialization_complete"] is True
    assert receipt["automatic_execution"] is False
    assert receipt["derived_git_commit_sha"] is receipt["derived_git_tree_sha"] is None
    assert receipt["origin_base_sha"] == original_head
    assert receipt["origin_tree_sha"] == f.identity.origin_tree_sha
    assert receipt["source_sha256"] == m.accepted["source_sha256"]
    source = m.directory / "source"
    actual_paths = {str(path.relative_to(source)) for path in source.rglob("*") if path.is_file()}
    expected = f.acceptance.current(f.identity.program_id)
    assert actual_paths == {item.path for item in expected.files}
    for item in expected.files:
        path = source / item.path
        assert path.read_bytes() == item.content
        assert stat.S_IMODE(path.stat().st_mode) == (0o755 if item.mode == "100755" else 0o644)
        assert path.stat().st_nlink == 1
    assert (source / "nested" / "kept.txt").read_bytes() == b"CRLF\r\nno-final-LF"
    assert not (source / ".git").exists()
    assert stat.S_IMODE(m.directory.stat().st_mode) == 0o700
    assert f.owner not in json.dumps(receipt)
    assert f.workspace.programs.execution_bindings(f.identity.program_id) == before_bindings
    assert _git(f.source, "rev-parse", "HEAD") == original_head
    assert _git(f.source, "status", "--porcelain") == ""
    assert (f.source / "app.py").read_bytes() == b"def answer():\n    return 42\n"


@pytest.mark.parametrize("bad", ["owner", "program", "receipt", "initial", "policy", "destination"])
def test_actual_admission_rejects_wrong_authority_and_arbitrary_destination(executed, bad):
    f = executed
    m = _admitted(f)
    arguments = {"acceptance_receipt_sha256": _hash(_canonical(m.accepted)), "owner_token": f.owner}
    program = f.identity.program_id
    if bad == "owner":
        arguments["owner_token"] = "f" * 32
    elif bad == "program":
        program = "another-program"
    elif bad == "receipt":
        arguments["acceptance_receipt_sha256"] = "f" * 64
    elif bad == "initial":
        arguments["acceptance_receipt_sha256"] = f.acceptance._head(program)[
            "initial_receipt_sha256"]
    elif bad == "destination":
        arguments["destination"] = str(f.source)
    else:
        other = ProgramSourceMaterializationService(f.acceptance,
                                                    OwnedSourcePolicy(operation_seconds=61))
        with pytest.raises(ProgramSourceError, match="host policy"):
            other.reconcile(m.operation_id, owner_token=f.owner)
        return
    with pytest.raises((ProgramSourceError, TypeError)):
        m.service.begin(program, **arguments)
    assert not m.directory.exists()


@pytest.mark.parametrize("kind", ["directory", "symlink", "file", "copied-marker"])
def test_unrecorded_existing_destination_is_never_adopted_or_deleted(executed, kind):
    f = executed
    m = _admitted(f)
    if kind == "symlink":
        m.directory.symlink_to(f.source, target_is_directory=True)
    elif kind == "file":
        m.directory.write_bytes(b"owner work")
    else:
        m.directory.mkdir(mode=0o700)
        if kind == "copied-marker":
            row = m.service._row(m.operation_id)
            (m.directory / ".uca-owner.json").write_bytes(m.service._marker(row))
    with pytest.raises(ProgramSourceError):
        _reconcile(m)
    assert m.service.status(m.operation_id)["state"] == "intent"
    receipt = m.service.abandon(m.operation_id, owner_token=f.owner, reason="Ambiguous allocation")
    assert receipt["filesystem_cleanup"] is False and m.directory.exists()
    assert m.service.abandon(m.operation_id, owner_token=f.owner,
                             reason="Ambiguous allocation") == receipt
    with pytest.raises(ProgramSourceError):
        m.service.abandon(m.operation_id, owner_token=f.owner, reason="Different replay")
    assert (f.source / "app.py").read_bytes().endswith(b"return 42\n")
    replacement = m.service.begin(f.identity.program_id,
                                  acceptance_receipt_sha256=_hash(_canonical(m.accepted)),
                                  owner_token=f.owner)
    assert replacement["operation_id"] != m.operation_id
    assert m.service.reconcile(replacement["operation_id"], owner_token=f.owner)[
        "materialization_complete"]
    assert m.directory.exists()


@pytest.mark.parametrize("stage", ["allocated", "complete"])
@pytest.mark.parametrize("drift", ["bytes", "missing", "extra", "mode", "symlink", "hardlink",
                                    "same-bytes-inode", "marker", "source-directory"])
def test_whole_tree_drift_rejects_recovery_or_use(executed, stage, drift):
    f = executed
    m = _admitted(f)
    if stage == "complete":
        _reconcile(m)
    else:
        _allocate(m)
        # Stage through the actual filesystem implementation but do not commit a receipt.
        row, intent, snapshot = m.service._load(m.operation_id, f.owner)
        with m.service.filesystem.root_handle(intent["root_chain"]) as (root, _):
            m.service.filesystem.inspect(
                root, m.directory.name, m.service._marker(row),
                json.loads(f.acceptance._get(row["allocation_sha256"])),
                m.service.filesystem.layout(snapshot), m.service.filesystem.deadline(), fill=True)
    path = m.directory / "source" / "unchanged.bin"
    if drift == "bytes":
        path.write_bytes(b"bad\0")  # Same length as the accepted binary.
    elif drift == "missing":
        path.unlink()
    elif drift == "extra":
        (m.directory / "source" / "extra.txt").write_bytes(b"extra")
    elif drift == "mode":
        path.chmod(0o755)
    elif drift in {"symlink", "hardlink"}:
        path.unlink()
        if drift == "symlink":
            path.symlink_to(f.source / "unchanged.bin")
        else:
            os.link(f.source / "unchanged.bin", path)
    elif drift == "same-bytes-inode":
        path.rename(path.with_name("outside-copy"))
        path.write_bytes(b"\0\xff\r\n")
        path.with_name("outside-copy").rename(f.tmp_path / "retained-copy")
    elif drift == "marker":
        (m.directory / ".uca-owner.json").write_bytes(b"{}")
    else:
        (m.directory / "source").rename(m.directory / "substituted")
        (m.directory / "source").mkdir(mode=0o700)
    # Missing exact files in an incomplete allocation are explicitly recoverable;
    # no completed receipt permits either missing bytes or replacement inodes.
    if stage == "allocated" and drift in {"missing", "same-bytes-inode"}:
        assert _reconcile(m)["materialization_complete"]
    else:
        with pytest.raises(ProgramSourceError):
            _reconcile(m)
    expected_state = ("complete" if stage == "allocated" and drift in
                      {"missing", "same-bytes-inode"} else stage)
    assert m.service.status(m.operation_id)["state"] == expected_state


@pytest.mark.parametrize("executed", [{"open_program": True}], indirect=True)
@pytest.mark.parametrize("action", ["pause", "cancel", "realign", "pause-resume", "owner", "head"])
def test_owner_control_and_generation_revalidated_before_completion(executed, action):
    f = executed
    m = _admitted(f)
    _allocate(m)
    if action == "realign":
        f.workspace.programs.require_realign(f.identity.program_id, "f" * 64)
    elif action == "cancel":
        f.workspace.programs.cancel(f.identity.program_id, reason="Fixture cancellation")
    elif action == "owner":
        f.workspace.lifecycle_reservations.release_program_worker(f.identity.program_id, f.owner)
        new_owner = f.workspace.lifecycle_reservations.reserve_program_worker(f.identity.program_id)
        with pytest.raises(ProgramSourceError, match="owner"):
            m.service.reconcile(m.operation_id, owner_token=new_owner)
    elif action == "head":
        f.acceptance.connection.execute(
            "UPDATE program_source_heads SET generation = generation + 1")
    else:
        f.workspace.programs.pause(f.identity.program_id, reason="Fixture pause")
        if action == "pause-resume":
            f.workspace.programs.resume(f.identity.program_id)
    with pytest.raises(ProgramSourceError):
        _reconcile(m)
    assert m.service.status(m.operation_id)["state"] == "allocated"
    assert list((m.directory / "source").iterdir()) == []


@pytest.mark.parametrize("failure", ["partial-write", "zero-write", "ENOSPC", "fsync", "database"])
def test_failures_leave_no_completion_and_do_not_overwrite_partial_bytes(executed, monkeypatch,
                                                                         failure):
    f = executed
    m = _admitted(f)
    _allocate(m)
    original_write = os.write
    calls = 0

    def fail_write(fd, content):
        nonlocal calls
        calls += 1
        if failure == "zero-write":
            return 0
        if failure == "partial-write" and calls == 1:
            return original_write(fd, content[:3])
        raise OSError(errno.ENOSPC, "Injected filesystem exhaustion")

    with monkeypatch.context() as patch:
        if failure in {"partial-write", "zero-write", "ENOSPC"}:
            patch.setattr(os, "write", fail_write)
        elif failure == "fsync":
            patch.setattr(os, "fsync", lambda fd: (_ for _ in ()).throw(
                OSError(errno.EIO, "Injected fsync failure")))
        else:
            f.acceptance.connection.execute("""CREATE TEMP TRIGGER reject_materialization
                BEFORE UPDATE ON program_source_materializations WHEN NEW.state = 'complete'
                BEGIN SELECT RAISE(ABORT, 'Injected completion failure'); END""")
        with pytest.raises(ProgramSourceError):
            _reconcile(m)
    assert m.service.status(m.operation_id)["state"] == "allocated"
    assert m.service.status(m.operation_id)["completion_sha256"] is None
    if failure == "database":
        f.acceptance.connection.execute("DROP TRIGGER reject_materialization")
    if failure in {"partial-write", "zero-write", "ENOSPC"}:
        before = (m.directory / "source" / "app.py").read_bytes()
        with pytest.raises(ProgramSourceError):
            _reconcile(m)
        assert (m.directory / "source" / "app.py").read_bytes() == before
    else:
        assert _reconcile(m)["materialization_complete"]


def test_concurrent_connections_replay_one_owned_allocation_and_receipt(executed):
    f = executed
    m = _admitted(f)
    second_acceptance = _service(f.workspace, f.safe, f.source, f.policy)
    second = ProgramSourceMaterializationService(second_acceptance)
    try:
        with ThreadPoolExecutor(2) as pool:
            results = [pool.submit(service.reconcile, m.operation_id, owner_token=f.owner)
                       for service in (m.service, second)]
            receipts = [result.result(timeout=20) for result in results]
        assert receipts[0] == receipts[1]
        assert second_acceptance.connection.execute(
            "SELECT count(*) FROM program_source_materializations").fetchone()[0] == 1
        assert len(list(m.service.filesystem.root.glob("source-*"))) == 1
    finally:
        second_acceptance.close()


def test_completion_holds_existing_lifecycle_control_and_source_writers(executed, monkeypatch):
    f = executed
    m = _admitted(f)
    _allocate(m)
    inspect = m.service.filesystem.inspect
    checked = []

    def check(*args, **kwargs):
        for path in (f.workspace.programs.database_path, f.workspace.control.database_path,
                     f.workspace.lifecycle_reservations.database_path):
            with sqlite3.connect(path, timeout=0.01, isolation_level=None) as connection:
                with pytest.raises(sqlite3.OperationalError, match="locked"):
                    connection.execute("BEGIN IMMEDIATE")
                checked.append(path)
        return inspect(*args, **kwargs)

    monkeypatch.setattr(m.service.filesystem, "inspect", check)
    assert _reconcile(m)["materialization_complete"]
    assert len(checked) == 6


@pytest.mark.parametrize("executed", [{"materialization_files": True}], indirect=True)
@pytest.mark.parametrize("where", ["root", "operation", "source", "nested"])
def test_substituted_parent_cannot_redirect_materialization(executed, monkeypatch, where):
    f = executed
    m = _admitted(f)
    _allocate(m)
    outside = f.tmp_path / "outside"
    outside.mkdir()
    source = m.directory / "source"
    if where == "nested":
        (source / "nested").mkdir(mode=0o700)
    parent = {"root": m.service.filesystem.root, "operation": m.directory,
              "source": source, "nested": source / "nested"}[where]
    parked = f.tmp_path / ("parked-" + where)
    parent.rename(parked)
    parent.symlink_to(outside, target_is_directory=True)
    with pytest.raises(ProgramSourceError):
        _reconcile(m)
    assert list(outside.iterdir()) == []
    assert m.service.status(m.operation_id)["state"] == "allocated"


def test_root_substitution_during_write_blocks_completion_without_following_link(executed,
                                                                                monkeypatch):
    f = executed
    m = _admitted(f)
    _allocate(m)
    root = m.service.filesystem.root
    outside = f.tmp_path / "outside"
    outside.mkdir()
    write = m.service.filesystem._write_new
    swapped = False

    def swap(*args, **kwargs):
        nonlocal swapped
        if not swapped:
            root.rename(f.tmp_path / "parked-root")
            root.symlink_to(outside, target_is_directory=True)
            swapped = True
        return write(*args, **kwargs)

    monkeypatch.setattr(m.service.filesystem, "_write_new", swap)
    with pytest.raises(ProgramSourceError):
        _reconcile(m)
    assert list(outside.iterdir()) == []
    assert m.service.status(m.operation_id)["state"] == "allocated"


@pytest.mark.parametrize("bound", ["entries", "metadata", "time"])
def test_host_resource_bounds_fail_closed_without_receipt(executed, monkeypatch, bound):
    f = executed
    if bound == "time":
        m = _admitted(f)
        monkeypatch.setattr(m.service.filesystem, "deadline", lambda: -1)
        with pytest.raises(ProgramSourceError, match="deadline"):
            _reconcile(m)
        assert not m.directory.exists()
    else:
        policy = OwnedSourcePolicy(**({"max_entries": 1} if bound == "entries"
                                       else {"max_metadata_bytes": 100}))
        with pytest.raises(ProgramSourceError, match="budget"):
            _admitted(f, policy)
        assert list((f.safe.artifacts.root.parent / "sandboxes").glob("source-*")) == []


_PROCESS = """
import json, os, sys
from pathlib import Path
from universal_coding_agent.product.workspace import ProductWorkspace
from universal_coding_agent.product.program_source_acceptance import ProgramSourceAcceptanceService
from universal_coding_agent.product.program_source_attestation import (
    ProgramGitSourceAttestationService)
from universal_coding_agent.product.program_source_materialization import (
    ProgramSourceMaterializationService)
from universal_coding_agent.core.safe_models import SafeModePolicy
from universal_coding_agent.providers.fake import FakeModelProvider
from universal_coding_agent.safe_service import SafeAgentService
p = json.load(sys.stdin)
def forbidden(*args, **kwargs):
    raise AssertionError('reload/recovery must never invoke a provider')
provider = FakeModelProvider()
provider.invoke = forbidden
workspace = ProductWorkspace.create(Path(p['root']), provider)
safe = SafeAgentService.create(Path(p['safe_root']), provider, control=workspace.control,
    remote_operations=workspace.remote_operations, allow_local_sources=True)
store = ProgramSourceAcceptanceService(programs=workspace.programs,
    lifecycle=workspace.lifecycle_reservations, safe=safe,
    attestor=ProgramGitSourceAttestationService(Path(p['source']), p['repository_sha256']),
    repository_url=p['source'], trusted_policy=SafeModePolicy.model_validate(p['policy']))
m = ProgramSourceMaterializationService(store)
crash, operation_id = p['crash'], p['operation_id']
def die(*args, **kwargs):
    os._exit(73)
if crash == 'intent-commit':
    m._allocate = die
elif crash == 'mkdir':
    mkdir = os.mkdir
    def crash_mkdir(name, *args, **kwargs):
        mkdir(name, *args, **kwargs)
        if name == 'source-' + operation_id:
            die()
    os.mkdir = crash_mkdir
elif crash in ('allocation-update', 'completion-update'):
    state = 'allocated' if crash == 'allocation-update' else 'complete'
    store.connection.create_function('die', 0, die)
    store.connection.execute("CREATE TEMP TRIGGER source_materialization_crash "
        "AFTER UPDATE ON program_source_materializations WHEN NEW.state = '" + state +
        "' BEGIN SELECT die(); END")
elif crash == 'allocated-commit':
    m._finish = die
elif crash in ('file-write', 'file-fsync'):
    write = m.filesystem._write_new
    def crash_write(parent, name, content, mode, deadline):
        if name == 'app.py' and crash == 'file-write':
            fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                         0o600, dir_fd=parent)
            os.write(fd, content[:3])
            die()
        result = write(parent, name, content, mode, deadline)
        if name == 'app.py':
            die()
        return result
    m.filesystem._write_new = crash_write
elif crash == 'tree-verified':
    inspect = m.filesystem.inspect
    def crash_inspect(*args, **kwargs):
        result = inspect(*args, **kwargs)
        if kwargs.get('fill'):
            die()
        return result
    m.filesystem.inspect = crash_inspect
if p['action'] == 'read':
    m.filesystem.root_handle = forbidden
    print(json.dumps(m.status(operation_id)))
else:
    result = m.reconcile(operation_id, owner_token=p['owner'])
    if crash == 'completion-commit':
        die()
    print(json.dumps(result))
store.close()
safe.close()
workspace.close()
"""


def _process(m, *, action="read", crash=""):
    f = m.f
    payload = {"root": str(f.workspace.root), "safe_root": str(f.safe.artifacts.root.parent),
               "source": str(f.source), "repository_sha256": f.identity.repository_sha256,
               "policy": f.policy.model_dump(mode="json"), "operation_id": m.operation_id,
               "owner": f.owner, "action": action, "crash": crash}
    return subprocess.run([sys.executable, "-c", _PROCESS], input=json.dumps(payload),
                          capture_output=True, text=True, timeout=20)


@pytest.mark.parametrize("crash,state,recoverable", [
    ("intent-commit", "intent", True),
    ("mkdir", "intent", False),
    ("allocation-update", "intent", False),
    ("allocated-commit", "allocated", True),
    ("file-write", "allocated", False),
    ("file-fsync", "allocated", True),
    ("tree-verified", "allocated", True),
    ("completion-update", "allocated", True),
    ("completion-commit", "complete", True),
])
def test_real_process_death_read_only_reload_and_explicit_recovery(executed, crash, state,
                                                                  recoverable):
    f = executed
    m = _admitted(f)
    bindings = f.workspace.programs.execution_bindings(f.identity.program_id)
    killed = _process(m, action="reconcile", crash=crash)
    assert killed.returncode == 73, killed.stderr
    before = m.service.status(m.operation_id)
    assert before["state"] == state
    if state != "complete":
        assert before["completion_sha256"] is None
    reload = _process(m)
    assert reload.returncode == 0, reload.stderr
    assert json.loads(reload.stdout) == before == m.service.status(m.operation_id)
    assert f.workspace.programs.execution_bindings(f.identity.program_id) == bindings
    assert f.acceptance.current(f.identity.program_id).generation == 1
    resumed = _process(m, action="reconcile")
    if recoverable:
        assert resumed.returncode == 0, resumed.stderr
        receipt = json.loads(resumed.stdout)
        assert receipt == m.service.verify_complete(m.operation_id, owner_token=f.owner)
        assert _reconcile(m) == receipt
    else:
        assert resumed.returncode != 0
        assert m.service.status(m.operation_id) == before
        assert m.directory.exists()
        receipt = m.service.abandon(m.operation_id, owner_token=f.owner,
                                     reason="Explicit crash recovery abandonment")
        assert receipt["filesystem_cleanup"] is False
        assert m.directory.exists()
        read = _process(m)
        assert read.returncode == 0 and json.loads(read.stdout)["state"] == "abandoned"


def test_failed_new_materialization_preserves_previous_complete_source(executed, monkeypatch):
    f = executed
    m = _admitted(f)
    first = _reconcile(m)
    other = ProgramSourceMaterializationService(f.acceptance,
                                                OwnedSourcePolicy(operation_seconds=61))
    begin = other.begin(f.identity.program_id,
                        acceptance_receipt_sha256=_hash(_canonical(m.accepted)),
                        owner_token=f.owner)
    with monkeypatch.context() as patch:
        patch.setattr(other.filesystem, "_write_new", lambda *a, **k: (_ for _ in ()).throw(
            OSError(errno.ENOSPC, "Injected new allocation failure")))
        with pytest.raises(ProgramSourceError):
            other.reconcile(begin["operation_id"], owner_token=f.owner)
    assert m.service.verify_complete(m.operation_id, owner_token=f.owner) == first
    assert (m.directory / "source" / "app.py").read_bytes().endswith(b"return 43\n")


def test_repeated_content_reads_preserve_complete_verification(executed):
    f = executed
    m = _admitted(f)
    receipt = _reconcile(m)
    path = m.directory / "source" / "unchanged.bin"
    # Ordinary reads must not invalidate the receipt solely through access time.
    assert path.read_bytes() == b"\0\xff\r\n"
    assert m.service.verify_complete(m.operation_id, owner_token=f.owner) == receipt
