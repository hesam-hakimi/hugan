from __future__ import annotations

import hashlib
import json
import os
import selectors
import shutil
import signal
import stat
import subprocess
import sys
import zlib
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

from universal_coding_agent.product import program_source_attestation as attestation_module
from universal_coding_agent.product.program_source_attestation import (
    ProgramGitSourceAttestationService,
    ProgramGitSourcePolicy,
)
from universal_coding_agent.product.program_source_transitions import (
    ProgramSourceError,
    ProgramSourceIdentity,
    ProgramSourcePolicy,
    ProgramSourceTransitionService,
)

REPOSITORY = hashlib.sha256(b"host-bound fixture repository").hexdigest()
REAL_GIT = shutil.which("git")


def git(root: Path, *args: str, data: bytes | None = None) -> bytes:
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
               GIT_AUTHOR_NAME="Fixture", GIT_AUTHOR_EMAIL="fixture@example.invalid",
               GIT_COMMITTER_NAME="Fixture", GIT_COMMITTER_EMAIL="fixture@example.invalid")
    return subprocess.run([REAL_GIT, "-C", str(root), *args], input=data, capture_output=True,
                          check=True, env=env, timeout=10).stdout


def repository(path: Path, object_format: str = "sha1") -> Path:
    path.mkdir()
    git(path, "init", "--initial-branch=fixture", f"--object-format={object_format}")
    return path


def blob(root: Path, data: bytes) -> str:
    return git(root, "hash-object", "-w", "--stdin", data=data).decode().strip()


def tree(root: Path, entries: list[tuple[bytes, bytes, str]], *, ordered: bool = True) -> str:
    if ordered:
        entries = sorted(entries, key=lambda e: e[1] + (b"/" if e[0] == b"40000" else b"\0"))
    raw = b"".join(mode + b" " + name + b"\0" + bytes.fromhex(oid)
                   for mode, name, oid in entries)
    return git(root, "hash-object", "-w", "-t", "tree", "--literally", "--stdin",
               data=raw).decode().strip()


def commit(root: Path, tree_sha: str) -> ProgramSourceIdentity:
    raw = (f"tree {tree_sha}\nauthor Fixture <fixture@example.invalid> 1 +0000\n"
           "committer Fixture <fixture@example.invalid> 1 +0000\n\nFixture\n").encode()
    oid = git(root, "hash-object", "-w", "-t", "commit", "--stdin", data=raw).decode().strip()
    git(root, "update-ref", "HEAD", oid)
    return ProgramSourceIdentity("program-fixture", REPOSITORY, "1" * 64, "2" * 64, oid, tree_sha)


def simple(root: Path, data: bytes = b"value = 42\r\n") -> ProgramSourceIdentity:
    return commit(root, tree(root, [(b"100644", b"value.py", blob(root, data))]))


def source_state(root: Path) -> tuple[tuple[str, int, bytes], ...]:
    # Includes HEAD, refs, index, config, and object bytes; excludes access-time metadata.
    return tuple((str(path.relative_to(root)), stat.S_IMODE(path.stat().st_mode), path.read_bytes())
                 for path in sorted(root.rglob("*")) if path.is_file())


def service(root: Path, **kwargs) -> ProgramGitSourceAttestationService:
    return ProgramGitSourceAttestationService(root, REPOSITORY, **kwargs)


@pytest.mark.parametrize("object_format", ["sha1", "sha256"])
def test_complete_canonical_source_preserves_dirty_checkout_and_replays_in_new_process(
    tmp_path: Path, object_format: str,
) -> None:
    root = repository(tmp_path / "repository", object_format)
    binary = bytes(range(256)) + b"\0\r\n"
    nested = tree(root, [(b"100755", b"run.sh", blob(root, b"#!/bin/sh\nexit 0\n"))])
    identity = commit(root, tree(root, [
        (b"100644", b"value.py", blob(root, b"value = 42\r\n")),
        (b"100644", b"binary.dat", blob(root, binary)),
        (b"40000", b"bin", nested),
        (b"100644", b".gitattributes", blob(root, b"*.py text eol=lf filter=tripwire\n")),
    ]))
    git(root, "read-tree", "--reset", "-u", identity.origin_base_sha)
    (root / "value.py").write_bytes(b"staged owner change\n")
    git(root, "add", "value.py")
    (root / "value.py").write_bytes(b"unstaged owner change\r\n")
    (root / "owner note.txt").write_bytes(b"unrelated untracked source")
    git(root, "config", "core.autocrlf", "true")
    sentinel = tmp_path / "executed"
    git(root, "config", "filter.tripwire.smudge", f"touch {sentinel}")
    git(root, "config", "core.fsmonitor", f"touch {sentinel}")
    before = source_state(root)
    result = service(root).attest(identity)
    files = {item.path: item for item in result.snapshot.files}
    assert set(files) == {".gitattributes", "bin/run.sh", "binary.dat", "value.py"}
    assert files["value.py"].content == b"value = 42\r\n"
    assert files["binary.dat"].content == binary
    assert files["bin/run.sh"].mode == "100755"
    assert result.object_format == object_format
    assert result.snapshot.generation == 0 and result.snapshot.predecessor_sha256 is None
    assert result.snapshot_sha256 == ProgramSourceTransitionService().snapshot_hash(result.snapshot)
    assert result.snapshot_sha256 != identity.origin_tree_sha
    payload = json.loads(result.receipt_bytes())
    assert payload["file_count"] == 4
    assert payload["identity"]["origin_base_sha"] == identity.origin_base_sha
    assert payload["identity"]["origin_tree_sha"] == identity.origin_tree_sha
    assert all(entry.content_sha256 == hashlib.sha256(files[entry.path].content).hexdigest()
               for entry in result.inventory)
    script = """
import json, sys
from pathlib import Path
from universal_coding_agent.product.program_source_attestation import (
    ProgramGitSourceAttestationService,
)
from universal_coding_agent.product.program_source_transitions import ProgramSourceIdentity
data = json.loads(sys.stdin.read())
identity = ProgramSourceIdentity(**data['identity'])
service = ProgramGitSourceAttestationService(Path(data['root']), identity.repository_sha256)
result = service.attest(identity)
print(result.canonical_hash())
"""
    replay = subprocess.run([sys.executable, "-c", script], input=json.dumps({
        "root": str(root), "identity": payload["identity"],
    }), text=True, capture_output=True, check=True, timeout=15)
    assert replay.stdout.strip() == result.canonical_hash()
    assert source_state(root) == before
    assert not sentinel.exists()


@pytest.mark.parametrize("nested", [False, True])
def test_empty_trees_are_traversed_without_inventing_files(tmp_path: Path, nested: bool) -> None:
    root = repository(tmp_path / "repo")
    empty = tree(root, [])
    identity = commit(root, tree(root, [(b"40000", b"empty", empty)]) if nested else empty)
    before = source_state(root)
    result = service(root).attest(identity)
    assert result.snapshot.files == result.inventory == ()
    assert source_state(root) == before


@pytest.mark.parametrize("layout", ["bare", "linked"])
def test_explicit_repository_layouts_preserve_origin(tmp_path: Path, layout: str) -> None:
    root = repository(tmp_path / "repo")
    identity = simple(root)
    target = tmp_path / "other"
    if layout == "bare":
        git(root, "clone", "--bare", str(root), str(target))
    else:
        git(root, "worktree", "add", "--detach", str(target), identity.origin_base_sha)
    before = source_state(root), source_state(target)
    assert service(target).attest(identity).snapshot.files[0].content == b"value = 42\r\n"
    assert (source_state(root), source_state(target)) == before


@pytest.mark.parametrize("kind", ["repository", "format", "tree", "commit-type", "missing-commit"])
def test_incorrect_identity_is_rejected(tmp_path: Path, kind: str) -> None:
    root = repository(tmp_path / "repo")
    identity = simple(root)
    if kind == "repository":
        identity = replace(identity, repository_sha256="3" * 64)
    elif kind == "format":
        identity = replace(identity, origin_base_sha="3" * 64, origin_tree_sha="4" * 64)
    elif kind == "tree":
        identity = replace(identity, origin_tree_sha="3" * 40)
    elif kind == "commit-type":
        identity = replace(identity, origin_base_sha=blob(root, b"not a commit"))
    else:
        identity = replace(identity, origin_base_sha="3" * 40)
    before = source_state(root)
    with pytest.raises(ProgramSourceError):
        service(root).attest(identity)
    assert source_state(root) == before


@pytest.mark.parametrize("name", [b"..", b".git", b"CON.txt", b"a/b", b"a\\b", b"trailing.",
                                  b"bad name", b"\xc3\xa9.py", b"a" * 256])
def test_unsupported_paths_fail_closed(tmp_path: Path, name: bytes) -> None:
    root = repository(tmp_path / "repo")
    identity = commit(root, tree(root, [(b"100644", name, blob(root, b"42"))]))
    with pytest.raises(ProgramSourceError):
        service(root).attest(identity)


@pytest.mark.parametrize("kind", ["symlink", "submodule", "mode", "case", "directory-case",
                                  "duplicate", "file-directory", "order", "truncated"])
def test_unsupported_or_malformed_tree_inventory_is_never_partially_attested(
    tmp_path: Path, kind: str,
) -> None:
    root = repository(tmp_path / "repo")
    content = blob(root, b"42")
    entries = [(b"100644", b"safe.py", content)]
    if kind in ("symlink", "submodule", "mode"):
        mode = {"symlink": b"120000", "submodule": b"160000", "mode": b"100600"}[kind]
        entries.append((mode, b"unsafe", content))
    elif kind == "case":
        entries.append((b"100644", b"SAFE.py", content))
    elif kind == "directory-case":
        empty = tree(root, [])
        entries.extend([(b"40000", b"Dir", empty), (b"40000", b"dir", empty)])
    elif kind == "duplicate":
        entries += entries
    elif kind == "file-directory":
        entries.append((b"40000", b"safe.py", tree(root, [])))
    elif kind == "order":
        entries.append((b"100644", b"a.py", content))
    raw_tree = tree(root, entries, ordered=kind != "order")
    if kind == "truncated":
        raw_tree = git(root, "hash-object", "-w", "-t", "tree", "--literally", "--stdin",
                       data=b"100644 a\0broken").decode().strip()
    identity = commit(root, raw_tree)
    with pytest.raises(ProgramSourceError):
        service(root).attest(identity)


@pytest.mark.parametrize("kind", ["missing-tree", "wrong-tree-type", "missing-blob",
                                  "corrupt-blob"])
def test_missing_or_corrupt_objects_fail_closed(tmp_path: Path, kind: str) -> None:
    root = repository(tmp_path / "repo")
    content = blob(root, b"42")
    root_tree = tree(root, [(b"100644", b"value.py", content)])
    if kind == "missing-tree":
        root_tree = "3" * 40
    elif kind == "wrong-tree-type":
        root_tree = content
    identity = commit(root, root_tree)
    path = root / ".git/objects" / content[:2] / content[2:]
    if kind == "missing-blob":
        path.unlink()
    elif kind == "corrupt-blob":
        path.chmod(0o600)
        path.write_bytes(zlib.compress(b"blob 2\0xx"))
    with pytest.raises(ProgramSourceError):
        service(root).attest(identity)


def test_replace_objects_and_inherited_git_overrides_cannot_substitute_source(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = repository(tmp_path / "repo")
    first = simple(root, b"42")
    first_blob = blob(root, b"42")
    second = simple(root, b"43")
    git(root, "replace", first.origin_base_sha, second.origin_base_sha)
    git(root, "replace", first_blob, blob(root, b"43"))
    decoy = repository(tmp_path / "decoy")
    simple(decoy, b"99")
    monkeypatch.setenv("GIT_DIR", str(decoy / ".git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(decoy))
    monkeypatch.setenv("GIT_CONFIG_COUNT", "1")
    monkeypatch.setenv("GIT_CONFIG_KEY_0", "core.bare")
    monkeypatch.setenv("GIT_CONFIG_VALUE_0", "true")
    before = source_state(root), source_state(decoy)
    assert service(root).attest(first).snapshot.files[0].content == b"42"
    assert (source_state(root), source_state(decoy)) == before


@pytest.mark.parametrize("content", [
    b"version https://git-lfs.github.com/spec/v1\noid sha256:" + b"a" * 64 + b"\nsize 42\n",
    b"version https://hawser.github.com/spec/v1\noid sha256:" + b"a" * 64 + b"\nsize 42\n",
    b"version https://unknown.invalid/spec\noid sha256:broken\n",
    b"\xef\xbb\xbf version https://git-lfs.github.com/spec/v1\nmalformed\n",
    b"oid sha256:broken\nsize 42\n",
])
def test_lfs_pointer_candidates_require_a_separate_payload_contract(
    tmp_path: Path, content: bytes,
) -> None:
    root = repository(tmp_path / "repo")
    identity = simple(root, content)
    with pytest.raises(ProgramSourceError, match="LFS"):
        service(root).attest(identity)


@pytest.mark.parametrize("source_policy,git_policy", [
    (ProgramSourcePolicy(max_files=1), ProgramGitSourcePolicy()),
    (ProgramSourcePolicy(max_file_bytes=3), ProgramGitSourcePolicy()),
    (ProgramSourcePolicy(max_total_bytes=10), ProgramGitSourcePolicy()),
    (ProgramSourcePolicy(max_artifact_bytes=10), ProgramGitSourcePolicy()),
    (ProgramSourcePolicy(), ProgramGitSourcePolicy(max_tree_entries=1)),
    (ProgramSourcePolicy(), ProgramGitSourcePolicy(max_tree_bytes=1)),
    (ProgramSourcePolicy(), ProgramGitSourcePolicy(max_commit_bytes=1)),
    (ProgramSourcePolicy(), ProgramGitSourcePolicy(max_git_output_bytes=10)),
])
def test_each_source_and_git_size_bound_rejects_without_source_changes(
    tmp_path: Path, source_policy: ProgramSourcePolicy, git_policy: ProgramGitSourcePolicy,
) -> None:
    root = repository(tmp_path / "repo")
    oid = blob(root, b"12345678")
    identity = commit(root, tree(root, [(b"100644", b"a", oid), (b"100644", b"b", oid)]))
    before = source_state(root)
    with pytest.raises(ProgramSourceError):
        service(root, source_policy=source_policy, git_policy=git_policy).attest(identity)
    assert source_state(root) == before


@pytest.mark.parametrize("field", list(ProgramGitSourcePolicy.__dataclass_fields__))
@pytest.mark.parametrize("value", [0, -1, True, 1.5, 64_000_001])
def test_git_policy_admission_bounds(field: str, value: object) -> None:
    with pytest.raises(ProgramSourceError):
        ProgramGitSourcePolicy(**{field: value})


def wrapper(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, body: str) -> None:
    directory = tmp_path / "tools"
    directory.mkdir()
    executable = directory / "git"
    executable.write_text(f"#!{sys.executable}\nimport os, sys, subprocess, time\n"
                          + body + f"\nos.execv({REAL_GIT!r}, [{REAL_GIT!r}, *sys.argv[1:]])\n")
    executable.chmod(0o755)
    monkeypatch.setenv("PATH", str(directory) + os.pathsep + os.environ["PATH"])


@pytest.mark.parametrize("fault", ["truncated", "trailing", "header", "stderr-overflow"])
def test_real_process_output_faults_fail_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, fault: str,
) -> None:
    root = repository(tmp_path / "repo")
    identity = simple(root)
    operation = {
        "truncated": "data = data[:-1]",
        "trailing": "data += b'unexpected'",
        "header": "data = b'x' + data[1:]",
        "stderr-overflow": "os.write(2, b'x' * 100000)",
    }[fault]
    wrapper(tmp_path, monkeypatch, f"""
if sys.argv[-1] == '--batch':
    data = subprocess.run([{REAL_GIT!r}, *sys.argv[1:]], input=sys.stdin.buffer.read(),
                          stdout=subprocess.PIPE, check=True).stdout
    {operation}
    sys.stdout.buffer.write(data)
    sys.exit(0)
""")
    with pytest.raises(ProgramSourceError):
        policy = ProgramGitSourcePolicy(max_git_output_bytes=50000)
        service(root, git_policy=policy).attest(identity)


@pytest.mark.parametrize("kind", ["command", "operation"])
def test_owned_git_process_deadlines(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                                    kind: str) -> None:
    root = repository(tmp_path / "repo")
    identity = simple(root)
    wrapper(tmp_path, monkeypatch, "time.sleep(2)" if kind == "command" else "time.sleep(0.2)")
    policy = ProgramGitSourcePolicy(git_timeout_seconds=1 if kind == "command" else 2,
                                    operation_timeout_seconds=5 if kind == "command" else 1)
    before = source_state(root)
    with pytest.raises(ProgramSourceError, match="deadline"):
        service(root, git_policy=policy).attest(identity)
    assert source_state(root) == before


def test_root_binding_and_policy_identity(tmp_path: Path) -> None:
    root = repository(tmp_path / "repo")
    identity = simple(root)
    nested = root / "nested"
    nested.mkdir()
    with pytest.raises(ProgramSourceError, match="exact repository root"):
        service(nested).attest(identity)
    ordinary = service(root).attest(identity)
    bounded = service(root, git_policy=ProgramGitSourcePolicy(max_tree_entries=10)).attest(identity)
    assert ordinary.snapshot_sha256 == bounded.snapshot_sha256
    assert ordinary.policy_sha256 != bounded.policy_sha256
    assert ordinary.canonical_hash() != bounded.canonical_hash()
    pinned = service(root)
    root.rename(tmp_path / "moved")
    root.mkdir()
    with pytest.raises(ProgramSourceError, match="changed"):
        pinned.attest(identity)


def test_platform_and_lazy_export(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from universal_coding_agent.product import ProgramGitSourceAttestationService as exported

    assert exported is ProgramGitSourceAttestationService
    monkeypatch.setattr(attestation_module, "os", SimpleNamespace(name="nt"))
    with pytest.raises(ProgramSourceError, match="POSIX"):
        service(tmp_path)


@pytest.mark.parametrize("depth,segment", [(65, b"d"), (6, b"d" * 200)])
def test_complete_traversal_preserves_path_depth_and_length_limits(
    tmp_path: Path, depth: int, segment: bytes,
) -> None:
    root = repository(tmp_path / "repo")
    oid = tree(root, [(b"100644", b"value.py", blob(root, b"42"))])
    for _ in range(depth):
        oid = tree(root, [(b"40000", segment, oid)])
    identity = commit(root, oid)
    with pytest.raises(ProgramSourceError, match="path"):
        service(root).attest(identity)


def test_reused_subtrees_count_at_each_traversed_path(tmp_path: Path) -> None:
    root = repository(tmp_path / "repo")
    subtree = tree(root, [(b"100644", b"value.py", blob(root, b"42"))])
    root_tree = tree(root, [(b"40000", b"a", subtree), (b"40000", b"b", subtree)])
    identity = commit(root, root_tree)
    budget = sum(int(git(root, "cat-file", "-s", oid)) for oid in (root_tree, subtree))
    with pytest.raises(ProgramSourceError, match="metadata byte"):
        service(root, git_policy=ProgramGitSourcePolicy(max_tree_bytes=budget)).attest(identity)
    assert len(service(root).attest(identity).snapshot.files) == 2


@pytest.mark.parametrize("fault", ["metadata-truncated", "metadata-oversized", "command-failure"])
def test_metadata_faults_and_failed_commands_do_not_create_receipts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, fault: str,
) -> None:
    root = repository(tmp_path / "repo")
    identity = simple(root)
    transform = ("data = data[:-1]" if fault == "metadata-truncated" else
                 "data = data.rsplit(b' ', 1)[0] + b' 999999999999999999999\\n'")
    body = "sys.exit(17)" if fault == "command-failure" else f"""
if sys.argv[-1] == '--batch-check':
    data = subprocess.run([{REAL_GIT!r}, *sys.argv[1:]], input=sys.stdin.buffer.read(),
                          stdout=subprocess.PIPE, check=True).stdout
    {transform}
    sys.stdout.buffer.write(data)
    sys.exit(0)
"""
    wrapper(tmp_path, monkeypatch, body)
    with pytest.raises(ProgramSourceError):
        service(root).attest(identity)


def wait_for_fixture_exit(liveness_reader: int, timeout: float) -> bool:
    # The fixture's child exclusively holds this pipe open for its entire sleep.
    # EOF observes exit without assuming synchronous signals or a matching /proc namespace.
    with selectors.DefaultSelector() as selector:
        selector.register(liveness_reader, selectors.EVENT_READ)
        if not selector.select(timeout):
            return False
        assert os.read(liveness_reader, 1) == b""
        return True


@pytest.mark.parametrize("suppress_group_signal", [False, True])
def test_deadline_terminates_an_owned_descendant_after_its_parent_exits(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, suppress_group_signal: bool,
) -> None:
    root = repository(tmp_path / "repo")
    identity = simple(root)
    marker = tmp_path / "descendant-pid"
    liveness = tmp_path / "liveness"
    os.mkfifo(liveness, 0o600)
    reader = os.open(liveness, os.O_RDONLY | os.O_NONBLOCK)
    wrapper(tmp_path, monkeypatch, f"""
pid = os.fork()
if pid:
    sys.exit(0)
writer = open({str(liveness)!r}, 'wb', buffering=0)
with open({str(marker)!r}, 'w') as output:
    output.write(str(os.getpid()))
time.sleep(30)
""")
    with monkeypatch.context() as control:
        if suppress_group_signal:
            control.setattr(attestation_module.os, "killpg", lambda _pid, _sig: None)
        with pytest.raises(ProgramSourceError, match="deadline"):
            service(root, git_policy=ProgramGitSourcePolicy(git_timeout_seconds=1)).attest(identity)
    pid = int(marker.read_text())
    # Signal delivery and orphan reaping are asynchronous. Keep the termination
    # assertion, allowing only a bounded observation interval after the deadline.
    # The mutation control proves that a still-running child is never accepted.
    terminated = wait_for_fixture_exit(reader, 0.05 if suppress_group_signal else 1)
    try:
        assert terminated is not suppress_group_signal
    finally:
        if not terminated:
            os.kill(pid, signal.SIGKILL)
            assert wait_for_fixture_exit(reader, 1)
        os.close(reader)


@pytest.mark.parametrize("transport", ["file", "ssh-command"])
def test_missing_promisor_blob_cannot_fetch_execute_transport_or_change_source(
    tmp_path: Path, transport: str,
) -> None:
    origin = repository(tmp_path / "origin")
    identity = simple(origin, b"canonical payload missing from the partial clone")
    missing = blob(origin, b"canonical payload missing from the partial clone")
    root = tmp_path / "partial"
    git(origin, "clone", "--no-checkout", "--no-hardlinks", str(origin), str(root))
    git(root, "config", "remote.origin.promisor", "true")
    git(root, "config", "remote.origin.partialclonefilter", "blob:none")
    git(root, "config", "protocol.file.allow", "always")
    git(root, "config", "protocol.ssh.allow", "always")
    transport_marker = tmp_path / "transport-executed"
    if transport == "ssh-command":
        command = tmp_path / "fixture-ssh"
        command.write_text(f"#!{sys.executable}\nfrom pathlib import Path\n"
                           f"Path({str(transport_marker)!r}).write_text('executed')\n"
                           "raise SystemExit(97)\n")
        command.chmod(0o755)
        git(root, "config", "core.sshCommand", str(command))
        git(root, "remote", "set-url", "origin", "ssh://fixture.invalid/source")
    missing_path = root / ".git/objects" / missing[:2] / missing[2:]
    assert missing_path.is_file()
    missing_path.unlink()
    before = source_state(root), source_state(origin)
    with pytest.raises(ProgramSourceError, match="missing or wrong-type"):
        service(root).attest(identity)
    assert not missing_path.exists()
    assert not transport_marker.exists()
    assert (source_state(root), source_state(origin)) == before


def test_unsupported_no_lazy_fetch_capability_rejects_on_first_command(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = repository(tmp_path / "repo")
    identity = simple(root)
    commands = tmp_path / "commands"
    wrapper(tmp_path, monkeypatch, f"""
with open({str(commands)!r}, 'a') as output:
    output.write(repr(sys.argv[1:]) + '\\n')
if '--no-lazy-fetch' in sys.argv:
    sys.stderr.write('unknown option: --no-lazy-fetch\\n')
    sys.exit(129)
""")
    before = source_state(root)
    with pytest.raises(ProgramSourceError, match="Git source read failed"):
        service(root).attest(identity)
    observed = commands.read_text().splitlines()
    assert len(observed) == 1
    assert "--no-lazy-fetch" in observed[0] and "cat-file" not in observed[0]
    assert source_state(root) == before


def test_transport_allowlist_overrides_repository_protocol_allow_configuration(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = repository(tmp_path / "repo")
    identity = simple(root)
    origin = repository(tmp_path / "origin")
    simple(origin)
    git(root, "config", "protocol.file.allow", "always")
    proof = tmp_path / "transport-denied"
    # The fixture explicitly attempts a read-only local transport in the adapter's
    # actual child environment; per-protocol allow=always must still be denied.
    wrapper(tmp_path, monkeypatch, f"""
assert os.environ.get('GIT_ALLOW_PROTOCOL') == ''
attempt = subprocess.run([{REAL_GIT!r}, '-C', {str(root)!r}, 'ls-remote', {str(origin)!r}],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
assert attempt.returncode != 0 and b'transport' in attempt.stderr
with open({str(proof)!r}, 'w') as output:
    output.write('denied')
""")
    before = source_state(root), source_state(origin)
    assert service(root).attest(identity).snapshot.files[0].content == b"value = 42\r\n"
    assert proof.read_text() == "denied"
    assert (source_state(root), source_state(origin)) == before
