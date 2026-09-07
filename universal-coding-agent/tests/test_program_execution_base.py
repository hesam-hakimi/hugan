from __future__ import annotations

import json
import os
import sqlite3
import stat
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace

import pytest
from test_program_source_acceptance import _git, _service
from test_program_source_acceptance import executed as executed
from test_program_source_materialization import _admitted, _forbidden, _reconcile

from universal_coding_agent.product.program_execution_base import ProgramExecutionBaseService
from universal_coding_agent.product.program_source_materialization import (
    ProgramSourceMaterializationService,
)
from universal_coding_agent.product.program_source_transitions import ProgramSourceError
from universal_coding_agent.sandbox.owned_source import OwnedSourcePolicy

pytestmark = pytest.mark.parametrize("executed", [
    {"open_program": True, "materialization_files": True},
    {"open_program": True, "materialization_files": True, "object_format": "sha256"},
], indirect=True)


@pytest.fixture
def ready(executed):
    f = executed
    material = _admitted(f)
    source_receipt = _reconcile(material)
    service = ProgramExecutionBaseService(material.service)
    intent = service.begin(material.operation_id, owner_token=f.owner)
    operation_id = intent["operation_id"]
    return SimpleNamespace(f=f, material=material, source_receipt=source_receipt,
                           service=service, intent=intent, operation_id=operation_id,
                           directory=service.filesystem.root / ("execution-" + operation_id))


def _finish(e):
    return e.service.reconcile(e.operation_id, owner_token=e.f.owner)


def test_actual_accepted_43_builds_real_isolated_git_without_dispatch(ready, monkeypatch):
    e, f = ready, ready.f
    before = f.workspace.programs.execution_bindings(f.identity.program_id)
    assert not e.directory.exists()
    with monkeypatch.context() as patch:
        patch.setattr(f.provider, "invoke", _forbidden)
        receipt = _finish(e)
        assert _finish(e) == receipt
        assert e.service.verify_complete(e.operation_id, owner_token=f.owner) == receipt
    repo = e.directory / "repo"
    assert _git(repo, "rev-parse", "HEAD") == receipt["derived_git_commit_sha"]
    assert _git(repo, "rev-parse", "HEAD^{tree}") == receipt["derived_git_tree_sha"]
    assert _git(repo, "rev-list", "--parents", "HEAD") == receipt["derived_git_commit_sha"]
    assert _git(repo, "remote") == ""
    # Optional index refresh changes its bytes, so use the exact isolated read policy.
    assert subprocess.run(["git", "status", "--porcelain=v1"], cwd=repo,
                          env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"}, capture_output=True,
                          check=True).stdout == b""
    assert _git(repo, "fsck", "--full", "--strict") == ""
    for item in f.acceptance.current(f.identity.program_id).files:
        path = repo / item.path
        assert path.read_bytes() == item.content
        assert stat.S_IMODE(path.stat().st_mode) == (0o755 if item.mode == "100755" else 0o644)
        assert path.stat().st_ino != (e.material.directory / "source" / item.path).stat().st_ino
    assert (repo / "app.py").read_bytes() == b"def answer():\n    return 43\n"
    assert receipt["origin_base_sha"] == f.identity.origin_base_sha
    assert receipt["origin_base_sha"] != receipt["derived_git_commit_sha"]
    assert receipt["origin_tree_sha"] != receipt["derived_git_tree_sha"]
    assert receipt["source_sha256"] == e.source_receipt["source_sha256"]
    assert receipt["derived_git_parents"] == []
    assert receipt["generation"] == 1 and receipt["phase_id"] == "phase-2"
    assert not receipt["dispatch_authorized"] and not receipt["cross_phase_source_handoff"]
    assert not receipt["automatic_execution"]
    assert f.owner not in json.dumps(receipt)
    assert f.workspace.programs.execution_bindings(f.identity.program_id) == before
    assert e.material.service.verify_complete(e.material.operation_id,
                                              owner_token=f.owner) == e.source_receipt
    assert (f.source / "app.py").read_bytes().endswith(b"return 42\n")
    assert _git(f.source, "status", "--porcelain") == ""


@pytest.mark.parametrize("bad", ["owner", "source", "receipt", "host", "phase", "bound",
                                  "control", "generation", "plan"])
def test_current_authority_is_required_before_allocation(ready, bad):
    e, f = ready, ready.f
    token = f.owner
    if bad == "owner":
        token = "f" * 32
    elif bad == "source":
        (e.material.directory / "source" / "app.py").write_bytes(b"bad")
    elif bad == "receipt":
        f.acceptance.connection.execute("UPDATE program_source_heads SET receipt_sha256 = ?",
                                        ("f" * 64,))
    elif bad == "host":
        e.service = ProgramExecutionBaseService(e.material.service,
                                               OwnedSourcePolicy(operation_seconds=61))
    elif bad == "phase":
        f.workspace.programs.connection.execute(
            "UPDATE program_phases SET status = 'running' WHERE phase_id = 'phase-2'")
        f.workspace.programs.connection.commit()
    elif bad == "bound":
        task, thread = f.workspace.programs._execution_ids(f.identity.program_id, "phase-2", None)
        from universal_coding_agent.product.models import ProgramExecutionBinding
        f.workspace.programs._insert_execution(ProgramExecutionBinding(
            program_id=f.identity.program_id, phase_id="phase-2", task_id=task,
            thread_id=thread, requirement_hash=f.identity.requirement_sha256, status="starting"))
    elif bad == "control":
        f.workspace.programs.pause(f.identity.program_id)
        f.workspace.programs.resume(f.identity.program_id)
    elif bad == "generation":
        f.acceptance.connection.execute("UPDATE program_source_heads SET generation = 2")
    else:
        path = f.workspace.programs.artifacts.root / "programs/source-program/program-plan.json"
        raw = json.loads(path.read_text())
        raw["phases"][1]["dependencies"] = []
        path.write_text(json.dumps(raw))
    with pytest.raises((ProgramSourceError, ValueError)):
        e.service.reconcile(e.operation_id, owner_token=token)
    assert not e.directory.exists()


@pytest.mark.parametrize("path,drift", [
    (path, drift) for path in ("app.py", ".git/HEAD", ".git/config", ".git/index",
                               ".git/objects", "nested")
    for drift in ("bytes", "symlink", "same-inode-bytes")
    if not (drift == "same-inode-bytes" and path in (".git/objects", "nested"))
])
def test_completed_source_and_git_proof_reject_tampering(ready, path, drift):
    e = ready
    _finish(e)
    target = e.directory / "repo" / path
    if drift == "same-inode-bytes":
        target.write_bytes(target.read_bytes())
    else:
        parked = e.f.tmp_path / "parked-execution-file"
        target.rename(parked)
        if drift == "symlink":
            target.symlink_to(parked, target_is_directory=parked.is_dir())
        elif parked.is_dir():
            target.mkdir(mode=0o700)
        else:
            target.write_bytes(parked.read_bytes())
    with pytest.raises(ProgramSourceError):
        e.service.verify_complete(e.operation_id, owner_token=e.f.owner)
    assert e.material.service.verify_complete(e.material.operation_id,
                                              owner_token=e.f.owner) == e.source_receipt


@pytest.mark.parametrize("path", [".git/objects/info/alternates", ".git/info/grafts",
                                  ".git/refs/replace/forged", "extra.txt"])
def test_extra_git_redirection_or_source_is_rejected_before_git(ready, monkeypatch, path):
    e = ready
    _finish(e)
    target = e.directory / "repo" / path
    target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    target.write_text("malicious content")
    monkeypatch.setattr(e.service, "_verify_git", _forbidden)
    with pytest.raises(ProgramSourceError):
        e.service.verify_complete(e.operation_id, owner_token=e.f.owner)


def test_allocation_ambiguity_is_preserved_and_explicit_abandonment_allows_new_intent(ready):
    e = ready
    e.directory.mkdir(mode=0o700)
    with pytest.raises(ProgramSourceError):
        _finish(e)
    assert e.service.status(e.operation_id)["state"] == "intent"
    abandoned = e.service.abandon(e.operation_id, owner_token=e.f.owner, reason="Ambiguous mkdir")
    assert not abandoned["filesystem_cleanup"] and e.directory.exists()
    assert e.service.abandon(e.operation_id, owner_token=e.f.owner,
                             reason="Ambiguous mkdir") == abandoned
    replacement = e.service.begin(e.material.operation_id, owner_token=e.f.owner)
    assert replacement["operation_id"] != e.operation_id
    assert e.service.reconcile(replacement["operation_id"], owner_token=e.f.owner)[
        "execution_base_complete"]


@pytest.mark.parametrize("failure", ["write", "fsync", "database", "git", "deadline"])
def test_partial_failures_never_produce_a_completed_base(ready, monkeypatch, failure):
    e = ready
    e.service._allocate(e.operation_id, e.f.owner, e.service.filesystem.deadline())
    with monkeypatch.context() as patch:
        if failure == "write":
            write = os.write
            def partial(fd, content):
                write(fd, content[:3])
                raise OSError("Injected partial write")
            patch.setattr(os, "write", partial)
        elif failure == "fsync":
            def sync(fd):
                raise OSError("Injected fsync failure")
            patch.setattr(os, "fsync", sync)
        elif failure == "database":
            e.f.acceptance.connection.execute("""CREATE TEMP TRIGGER reject_base_completion
                BEFORE UPDATE ON program_execution_bases WHEN NEW.state = 'complete'
                BEGIN SELECT RAISE(ABORT, 'Injected completion failure'); END""")
        elif failure == "git":
            def git(*args):
                raise ProgramSourceError("Injected Git verification failure")
            patch.setattr(e.service, "_verify_git", git)
        else:
            patch.setattr(e.service.filesystem, "deadline", lambda: -1)
        with pytest.raises(ProgramSourceError):
            _finish(e)
    assert e.service.status(e.operation_id)["state"] == "allocated"
    assert e.service.status(e.operation_id)["completion_sha256"] is None
    if failure == "database":
        e.f.acceptance.connection.execute("DROP TRIGGER reject_base_completion")
    if failure == "write":
        with pytest.raises(ProgramSourceError):
            _finish(e)
    else:
        assert _finish(e)["execution_base_complete"]


def test_concurrent_begin_and_finish_return_one_allocation_and_receipt(ready):
    e = ready
    store = _service(e.f.workspace, e.f.safe, e.f.source, e.f.policy)
    other = ProgramExecutionBaseService(ProgramSourceMaterializationService(store))
    try:
        with ThreadPoolExecutor(2) as pool:
            values = [pool.submit(s.begin, e.material.operation_id, owner_token=e.f.owner)
                      for s in (e.service, other)]
            assert [v.result(timeout=20) for v in values] == [e.intent, e.intent]
        with ThreadPoolExecutor(2) as pool:
            values = [pool.submit(s.reconcile, e.operation_id, owner_token=e.f.owner)
                      for s in (e.service, other)]
            receipts = [v.result(timeout=20) for v in values]
            assert receipts[0] == receipts[1]
        assert len(list(e.service.filesystem.root.glob("execution-*"))) == 1
    finally:
        store.close()


def test_completion_excludes_other_authority_writers(ready, monkeypatch):
    e = ready
    verify = e.service._verify_git
    seen = []
    def locked(*args):
        for path in (e.f.workspace.programs.database_path, e.f.workspace.control.database_path,
                     e.f.workspace.lifecycle_reservations.database_path):
            with sqlite3.connect(path, timeout=0.01, isolation_level=None) as connection:
                with pytest.raises(sqlite3.OperationalError, match="locked"):
                    connection.execute("BEGIN IMMEDIATE")
                seen.append(path)
        return verify(*args)
    monkeypatch.setattr(e.service, "_verify_git", locked)
    assert _finish(e)["execution_base_complete"]
    assert len(seen) == 3


_PROCESS = """
import json, os, sys
from pathlib import Path
from universal_coding_agent.product.workspace import ProductWorkspace
from universal_coding_agent.product.program_source_acceptance import ProgramSourceAcceptanceService
from universal_coding_agent.product.program_source_attestation import (
    ProgramGitSourceAttestationService)
from universal_coding_agent.product.program_source_materialization import (
    ProgramSourceMaterializationService)
from universal_coding_agent.product.program_execution_base import ProgramExecutionBaseService
from universal_coding_agent.core.safe_models import SafeModePolicy
from universal_coding_agent.providers.fake import FakeModelProvider
from universal_coding_agent.safe_service import SafeAgentService
p = json.load(sys.stdin)
def forbidden(*args, **kwargs):
    raise AssertionError('No provider or filesystem work during reload')
provider = FakeModelProvider()
provider.invoke = forbidden
workspace = ProductWorkspace.create(Path(p['root']), provider)
safe = SafeAgentService.create(Path(p['safe_root']), provider, control=workspace.control,
    remote_operations=workspace.remote_operations, allow_local_sources=True)
store = ProgramSourceAcceptanceService(programs=workspace.programs,
    lifecycle=workspace.lifecycle_reservations, safe=safe,
    attestor=ProgramGitSourceAttestationService(Path(p['source']), p['repository_sha256']),
    repository_url=p['source'], trusted_policy=SafeModePolicy.model_validate(p['policy']))
material = ProgramSourceMaterializationService(store)
m = ProgramExecutionBaseService(material)
crash, operation_id = p['crash'], p['operation_id']
def die(*args, **kwargs):
    os._exit(73)
if crash == 'intent-commit':
    m._allocate = die
elif crash == 'mkdir':
    mkdir = os.mkdir
    def crash_mkdir(name, *args, **kwargs):
        mkdir(name, *args, **kwargs)
        if name == 'execution-' + operation_id:
            die()
    os.mkdir = crash_mkdir
elif crash in ('allocation-update', 'completion-update'):
    state = 'allocated' if crash == 'allocation-update' else 'complete'
    store.connection.create_function('die', 0, die)
    store.connection.execute("CREATE TEMP TRIGGER execution_base_crash "
        "AFTER UPDATE ON program_execution_bases WHEN NEW.state = '" + state +
        "' BEGIN SELECT die(); END")
elif crash == 'allocated-commit':
    m._finish = die
elif crash in ('partial-object', 'object-fsync'):
    write = m.filesystem._write_new
    def crash_write(parent, name, content, mode, deadline):
        is_object = len(name) in (38, 62) and all(c in '0123456789abcdef' for c in name)
        if is_object and crash == 'partial-object':
            fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                         0o600, dir_fd=parent)
            os.write(fd, content[:3])
            die()
        result = write(parent, name, content, mode, deadline)
        if is_object:
            die()
        return result
    m.filesystem._write_new = crash_write
elif crash == 'git-verified':
    verify = m._verify_git
    def crash_verify(*args):
        verify(*args)
        die()
    m._verify_git = crash_verify
if p['action'] == 'read':
    m.filesystem.root_handle = material.filesystem.root_handle = forbidden
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


def _process(e, *, action="read", crash=""):
    f = e.f
    payload = {"root": str(f.workspace.root), "safe_root": str(f.safe.artifacts.root.parent),
               "source": str(f.source), "repository_sha256": f.identity.repository_sha256,
               "policy": f.policy.model_dump(mode="json"), "operation_id": e.operation_id,
               "owner": f.owner, "action": action, "crash": crash}
    return subprocess.run([sys.executable, "-c", _PROCESS], input=json.dumps(payload),
                          capture_output=True, text=True, timeout=30)


@pytest.mark.parametrize("crash,state,recoverable", [
    ("intent-commit", "intent", True), ("mkdir", "intent", False),
    ("allocation-update", "intent", False), ("allocated-commit", "allocated", True),
    ("partial-object", "allocated", False), ("object-fsync", "allocated", True),
    ("git-verified", "allocated", True), ("completion-update", "allocated", True),
    ("completion-commit", "complete", True),
])
def test_real_process_death_and_explicit_new_process_recovery(ready, crash, state, recoverable):
    e = ready
    result = _process(e, action="reconcile", crash=crash)
    assert result.returncode == 73, result.stderr
    read = _process(e)
    assert read.returncode == 0, read.stderr
    assert json.loads(read.stdout)["state"] == state
    result = _process(e, action="reconcile")
    if recoverable:
        assert result.returncode == 0, result.stderr
        receipt = json.loads(result.stdout)
        assert receipt["execution_base_complete"] and not receipt["dispatch_authorized"]
        assert _finish(e) == receipt
    else:
        assert result.returncode != 0
        assert e.service.status(e.operation_id)["state"] == state
        assert e.service.status(e.operation_id)["completion_sha256"] is None
    assert e.material.service.verify_complete(e.material.operation_id,
                                              owner_token=e.f.owner) == e.source_receipt
