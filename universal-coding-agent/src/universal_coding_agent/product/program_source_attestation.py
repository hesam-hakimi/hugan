"""Read-only, bounded Git-object attestation for initial Program source snapshots.

The host configures the repository binding. A returned digest is not a signature,
Safe PASS, transition approval, persisted acceptance, or sandbox authorization.
"""

from __future__ import annotations

import hashlib
import os
import re
import selectors
import signal
import stat
import subprocess
import time
from dataclasses import asdict, dataclass, replace
from pathlib import Path

from universal_coding_agent.core.safe_models import ApprovedChangeManifest, StructuredEditProposal
from universal_coding_agent.product.program_source_transitions import (
    ProgramSourceError,
    ProgramSourceFile,
    ProgramSourceIdentity,
    ProgramSourcePolicy,
    ProgramSourceSnapshot,
    ProgramSourceTransitionService,
    _canonical,
    _digest,
    _hash,
    _path,
    _require,
)


@dataclass(frozen=True, slots=True)
class ProgramGitSourcePolicy:
    max_tree_entries: int = 40_000
    max_tree_bytes: int = 8_000_000
    max_commit_bytes: int = 1_000_000
    max_git_output_bytes: int = 32_000_000
    git_timeout_seconds: int = 10
    operation_timeout_seconds: int = 60

    def __post_init__(self) -> None:
        for name, value in asdict(self).items():
            ceiling = 300 if name.endswith("seconds") else 64_000_000
            if name == "max_tree_entries":
                ceiling = 200_000
            _require(type(value) is int and 0 < value <= ceiling,
                     "invalid bounded Git-source policy")


@dataclass(frozen=True, slots=True)
class ProgramGitSourceInventoryEntry:
    path: str
    mode: str
    blob_sha: str
    size_bytes: int
    content_sha256: str


@dataclass(frozen=True, slots=True)
class ProgramGitSourceAttestation:
    """Result of a trusted host call; constructing or hashing this DTO grants no authority."""

    snapshot: ProgramSourceSnapshot
    snapshot_sha256: str
    object_format: str
    host_binding_sha256: str
    policy_sha256: str
    inventory: tuple[ProgramGitSourceInventoryEntry, ...]
    inventory_sha256: str

    def receipt_bytes(self) -> bytes:
        return _canonical({
            "schema": "uca-program-git-source-attestation-1",
            "identity": asdict(self.snapshot.identity),
            "snapshot_sha256": self.snapshot_sha256,
            "object_format": self.object_format,
            "host_binding_sha256": self.host_binding_sha256,
            "policy_sha256": self.policy_sha256,
            "inventory_sha256": self.inventory_sha256,
            "file_count": len(self.inventory),
            "total_bytes": sum(item.size_bytes for item in self.inventory),
        })

    def canonical_hash(self) -> str:
        return _hash(self.receipt_bytes())


@dataclass(slots=True)
class _GitBudget:
    deadline: float
    output_remaining: int


class ProgramGitSourceAttestationService:
    """Attest full immutable Git source without reading checkout file contents.

    Only a trusted host may construct the repository-to-directory binding. The
    adapter authenticates Git object bytes against that binding, not a remote
    account or arbitrary caller-supplied repository name. POSIX is required for
    bounded pipe handling and termination of the owned process group.
    """

    def __init__(
        self,
        repository_root: Path,
        repository_sha256: str,
        *,
        source_policy: ProgramSourcePolicy | None = None,
        git_policy: ProgramGitSourcePolicy | None = None,
    ) -> None:
        _require(os.name == "posix", "bounded Git-source attestation requires POSIX")
        _digest(repository_sha256)
        self.source = ProgramSourceTransitionService(source_policy)
        self.policy = git_policy if git_policy is not None else ProgramGitSourcePolicy()
        _require(type(self.policy) is ProgramGitSourcePolicy, "invalid Git-source policy")
        try:
            self.root = repository_root.resolve(strict=True)
            _require(self.root.is_dir() and "\n" not in str(self.root)
                     and "\r" not in str(self.root), "invalid repository directory")
            self.root_identity = self._directory_identity(self.root)
        except (OSError, RuntimeError, AttributeError) as exc:
            raise ProgramSourceError("repository directory is unavailable") from exc
        self.repository_sha256 = repository_sha256
        self.host_binding_sha256 = _hash(_canonical({
            "repository_sha256": repository_sha256, "root": str(self.root),
        }))
        self.policy_sha256 = _hash(_canonical({
            "schema": "uca-program-git-source-policy-1",
            "git": asdict(self.policy), "source_policy_sha256": self.source.policy.canonical_hash(),
        }))

    def attest(self, identity: ProgramSourceIdentity) -> ProgramGitSourceAttestation:
        try:
            return self._attest(identity)
        except ProgramSourceError:
            raise
        except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as exc:
            raise ProgramSourceError("Git-source attestation failed") from exc

    def attest_execution_base(
        self, origin: ProgramSourceIdentity, commit_sha: str,
    ) -> ProgramGitSourceAttestation:
        """Attest a distinct execution commit; never replace the Program's origin.

        The fixed tree lookup and complete object proof share one operation budget.
        The returned identity names this execution Base; callers compare full files
        separately while preserving their durable origin identity.
        """
        _require(type(origin) is ProgramSourceIdentity, "invalid source identity")
        _require(origin.repository_sha256 == self.repository_sha256,
                 "execution repository host binding differs")
        _require(isinstance(commit_sha, str)
                 and re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", commit_sha) is not None,
                 "invalid immutable execution commit")
        budget = _GitBudget(time.monotonic() + self.policy.operation_timeout_seconds,
                            self.policy.max_git_output_bytes)
        try:
            tree = self._run(("rev-parse", "--verify", f"{commit_sha}^{{tree}}"), b"", budget)
            _require(tree.endswith(b"\n") and tree.count(b"\n") == 1,
                     "invalid execution tree response")
            identity = replace(origin, origin_base_sha=commit_sha,
                               origin_tree_sha=tree[:-1].decode("ascii"))
            return self._attest(identity, budget=budget)
        except ProgramSourceError:
            raise
        except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as exc:
            raise ProgramSourceError("execution Git-source attestation failed") from exc

    def _attest(self, identity: ProgramSourceIdentity,
                *, budget: _GitBudget | None = None) -> ProgramGitSourceAttestation:
        _require(type(identity) is ProgramSourceIdentity, "invalid source identity")
        _require(identity.repository_sha256 == self.repository_sha256,
                 "source repository differs from trusted host binding")
        if budget is None:
            budget = _GitBudget(time.monotonic() + self.policy.operation_timeout_seconds,
                                self.policy.max_git_output_bytes)
        anchor = self._anchor(budget)
        object_format = anchor[0]
        oid_bytes = 20 if object_format == "sha1" else 32
        _require(len(identity.origin_base_sha) == oid_bytes * 2,
                 "origin Git object format differs from repository")
        commit = self._objects((identity.origin_base_sha,), "commit",
                               self.policy.max_commit_bytes, budget)[identity.origin_base_sha]
        header, separator, _body = commit.partition(b"\n\n")
        expected_tree = b"tree " + identity.origin_tree_sha.encode("ascii")
        headers = header.split(b"\n")
        _require(bool(separator) and headers[0] == expected_tree
                 and sum(line.startswith(b"tree ") for line in headers) == 1,
                 "commit does not bind the expected origin tree")

        pending = [("", identity.origin_tree_sha)]
        tracked: list[tuple[str, str, str]] = []
        tree_bytes = 0
        entry_count = 0
        while pending:
            self._deadline(budget)
            sizes = self._object_sizes(tuple(sorted({oid for _, oid in pending})), "tree",
                                       self.policy.max_tree_bytes - tree_bytes, budget)
            _require(sum(sizes[oid] for _, oid in pending)
                     <= self.policy.max_tree_bytes - tree_bytes,
                     "complete tree metadata byte limit exceeded")
            trees = self._object_contents(sizes, "tree", budget)
            following = []
            for prefix, oid in pending:
                raw = trees[oid]
                tree_bytes += len(raw)
                _require(tree_bytes <= self.policy.max_tree_bytes,
                         "complete tree metadata byte limit exceeded")
                offset = 0
                previous_key = b""
                names: set[str] = set()
                while offset < len(raw):
                    self._deadline(budget)
                    entry_count += 1
                    _require(entry_count <= self.policy.max_tree_entries,
                             "complete tree entry count exceeded")
                    end = raw.find(b"\0", offset)
                    _require(end >= 0 and end + 1 + oid_bytes <= len(raw),
                             "truncated Git tree entry")
                    metadata = raw[offset:end].split(b" ")
                    _require(len(metadata) == 2, "malformed Git tree entry")
                    mode_bytes, name_bytes = metadata
                    _require(mode_bytes in (b"40000", b"100644", b"100755"),
                             "unsupported Git source mode")
                    try:
                        name = name_bytes.decode("ascii")
                    except UnicodeDecodeError as exc:
                        raise ProgramSourceError("unsupported portable Git source path") from exc
                    _require("/" not in name, "Git tree entry contains a path separator")
                    path = prefix + name
                    # Use the existing P3.5a path contract for directories as well as files.
                    ProgramSourceFile(path, b"")
                    _require(name.lower() not in names, "portable Git tree name collision")
                    names.add(name.lower())
                    is_tree = mode_bytes == b"40000"
                    key = name_bytes + (b"/" if is_tree else b"\0")
                    _require(key > previous_key, "noncanonical Git tree entry order")
                    previous_key = key
                    child = raw[end + 1:end + 1 + oid_bytes].hex()
                    offset = end + 1 + oid_bytes
                    if is_tree:
                        following.append((path + "/", child))
                    else:
                        _require(len(tracked) < self.source.policy.max_files,
                                 "complete source file count exceeded")
                        tracked.append((path, mode_bytes.decode("ascii"), child))
            pending = following

        tracked.sort()
        blob_ids = tuple(sorted({oid for _, _, oid in tracked}))
        sizes = self._object_sizes(blob_ids, "blob", self.source.policy.max_file_bytes, budget)
        _require(sum(sizes[oid] for _, _, oid in tracked) <= self.source.policy.max_total_bytes,
                 "complete source content byte limit exceeded")
        blobs = self._object_contents(sizes, "blob", budget)
        files = []
        inventory = []
        for path, mode, oid in tracked:
            self._deadline(budget)
            content = blobs[oid]
            # Reject current/legacy LFS pointer candidates, including malformed versions.
            # No filter, smudge, network fetch, or expanded-payload claim is permitted.
            _require(not self._lfs_candidate(content), "Git LFS pointer payload is unsupported")
            files.append(ProgramSourceFile(path, content, mode))
            inventory.append(ProgramGitSourceInventoryEntry(path, mode, oid, len(content),
                                                            _hash(content)))
        snapshot = ProgramSourceSnapshot(identity, tuple(files))
        snapshot_sha256 = self.source.snapshot_hash(snapshot)
        inventory_sha256 = _hash(_canonical({
            "schema": "uca-program-git-source-inventory-1",
            "files": [asdict(item) for item in inventory],
        }))
        _require(self._anchor(budget) == anchor, "repository anchor changed during attestation")
        self._deadline(budget)
        return ProgramGitSourceAttestation(snapshot, snapshot_sha256, object_format,
                                           self.host_binding_sha256, self.policy_sha256,
                                           tuple(inventory), inventory_sha256)

    @staticmethod
    def _lfs_candidate(content: bytes) -> bool:
        # Leading BOM/whitespace and legacy endpoints are deliberately conservative rejects.
        probe = content[:4096].lstrip(b"\xef\xbb\xbf \t\r\n")
        return (probe.startswith(b"version ") and
                (b"git-lfs" in probe or b"hawser.github.com" in probe or b"git-media.io" in probe
                 or b"oid sha256:" in probe)) or probe.startswith(b"oid sha256:")

    @staticmethod
    def _directory_identity(path: Path) -> tuple[int, int]:
        value = path.stat()
        _require(path.is_dir(), "repository directory is unavailable")
        return value.st_dev, value.st_ino

    def _anchor(self, budget: _GitBudget) -> tuple[str, str, tuple[int, int]]:
        _require(self.root.resolve(strict=True) == self.root
                 and self._directory_identity(self.root) == self.root_identity,
                 "trusted repository directory changed")
        object_format = self._run(("rev-parse", "--show-object-format"), b"", budget)
        _require(object_format in (b"sha1\n", b"sha256\n"), "unsupported Git object format")
        git_dir_output = self._run(("rev-parse", "--absolute-git-dir"), b"", budget)
        _require(git_dir_output.endswith(b"\n") and git_dir_output.count(b"\n") == 1,
                 "invalid Git directory output")
        git_dir = Path(os.fsdecode(git_dir_output[:-1])).resolve(strict=True)
        bare = self._run(("rev-parse", "--is-bare-repository"), b"", budget)
        _require(bare in (b"true\n", b"false\n"), "invalid repository layout")
        top = git_dir if bare == b"true\n" else Path(os.fsdecode(
            self._run(("rev-parse", "--show-toplevel"), b"", budget).removesuffix(b"\n")
        )).resolve(strict=True)
        _require(top == self.root, "host binding must name the exact repository root")
        return (object_format.decode("ascii").strip(), str(git_dir),
                self._directory_identity(git_dir))

    def _objects(self, ids: tuple[str, ...], kind: str, maximum: int,
                 budget: _GitBudget) -> dict[str, bytes]:
        return self._object_contents(self._object_sizes(ids, kind, maximum, budget), kind, budget)

    def _object_sizes(self, ids: tuple[str, ...], kind: str, maximum: int,
                      budget: _GitBudget) -> dict[str, int]:
        if not ids:
            return {}
        output = self._run(("cat-file", "--batch-check"),
                           ("\n".join(ids) + "\n").encode("ascii"), budget)
        lines = output.split(b"\n")
        _require(len(lines) == len(ids) + 1 and lines[-1] == b"",
                 "incomplete Git object inventory")
        sizes = {}
        for oid, line in zip(ids, lines[:-1], strict=True):
            match = re.fullmatch(oid.encode("ascii") + b" " + kind.encode("ascii")
                                 + rb" (0|[1-9][0-9]{0,9})", line)
            _require(match is not None, "missing or wrong-type Git object")
            size = int(match[1])
            _require(size <= maximum, "Git object byte limit exceeded")
            sizes[oid] = size
        _require(sum(sizes.values()) <= budget.output_remaining,
                 "Git object inventory exceeds remaining output budget")
        return sizes

    def _object_contents(self, sizes: dict[str, int], kind: str,
                         budget: _GitBudget) -> dict[str, bytes]:
        if not sizes:
            return {}
        output = self._run(("cat-file", "--batch"),
                           ("\n".join(sizes) + "\n").encode("ascii"), budget)
        offset = 0
        result = {}
        for oid, size in sizes.items():
            self._deadline(budget)
            header = f"{oid} {kind} {size}\n".encode("ascii")
            _require(output[offset:offset + len(header)] == header,
                     "Git object header changed or was truncated")
            start = offset + len(header)
            offset = start + size
            _require(output[offset:offset + 1] == b"\n", "truncated Git object contents")
            content = output[start:offset]
            offset += 1
            framed = f"{kind} {size}\0".encode("ascii") + content
            digest = (hashlib.sha1(framed, usedforsecurity=False) if len(oid) == 40
                      else hashlib.sha256(framed)).hexdigest()
            _require(digest == oid, "Git object content hash mismatch")
            result[oid] = content
        _require(offset == len(output), "unexpected trailing Git object output")
        return result

    @staticmethod
    def _deadline(budget: _GitBudget) -> None:
        _require(time.monotonic() < budget.deadline, "Git-source operation deadline exceeded")

    def verify_retained_patch(self, manifest: ApprovedChangeManifest,
                              edits: StructuredEditProposal, patch: bytes) -> None:
        """Read an already owned execution through the same bounded, no-transport runner."""
        budget = _GitBudget(time.monotonic() + self.policy.operation_timeout_seconds,
                            self.policy.max_git_output_bytes)
        anchor = self._anchor(budget)
        # Clean/process filters can execute even when external diff/textconv are disabled.
        filters = self._run(("config", "--includes", "--name-only", "--get-regexp", r"^filter\."),
                            b"", budget, expected_returncodes=(0, 1))
        _require(not filters, "external Git filters are unsupported during source admission")
        _require(self._run(("rev-parse", "HEAD"), b"", budget)
                 == manifest.base_sha.encode() + b"\n", "retained Safe HEAD drifted")
        status = self._run(("status", "--porcelain=v1", "-z", "-uall"), b"", budget)
        entries = status.split(b"\0")
        _require(entries[-1] == b"", "invalid retained source status")
        paths = []
        for entry in entries[:-1]:
            _require(entry[:3] in (b" M ", b"?? "), "unsupported staged/renamed source change")
            path = entry[3:].decode("ascii")
            _path(path)
            _require(path in manifest.allowed_path_map(),
                     "retained source is outside approved scope")
            paths.append(path)
        _require(sorted(paths) == sorted(edits.changed_paths), "retained source path set differs")
        chunks = []
        for edit in manifest.allowed_changes:
            if edit.path not in edits.changed_paths:
                continue
            _path(edit.path)
            arguments = ("diff", "--no-ext-diff", "--no-textconv", "--no-color", "--full-index")
            if edit.operation.value == "create":
                chunk = self._run((*arguments, "--no-index", "--", "/dev/null", edit.path),
                                  b"", budget, expected_returncodes=(1,))
            else:
                chunk = self._run((*arguments, "--", edit.path), b"", budget)
            chunks.append(chunk)
            _require(sum(map(len, chunks)) <= manifest.max_patch_bytes,
                     "retained patch exceeds approved byte bound")
        _require(b"".join(chunks) == patch, "retained Safe source drifted after qualification")
        self._run(("-c", "core.whitespace=cr-at-eol", "diff", "--check"), b"", budget)
        _require(self._anchor(budget) == anchor, "retained source directory changed")

    def verify_retained_files(self, files: tuple[ProgramSourceFile, ...]) -> None:
        """Check complete retained bytes despite index flags or checkout normalization.

        Every parent and file is opened without following symlinks. This reads the
        existing Safe checkout; it neither creates nor authorizes a new sandbox.
        """
        self.source._check_files(files)
        deadline = time.monotonic() + self.policy.operation_timeout_seconds
        directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
        root_fd = os.open(self.root, directory_flags)
        try:
            root_stat = os.fstat(root_fd)
            _require((root_stat.st_dev, root_stat.st_ino) == self.root_identity,
                     "retained source root changed")
            for expected in files:
                _require(time.monotonic() < deadline, "retained source read deadline exceeded")
                _path(expected.path)
                parent = os.dup(root_fd)
                try:
                    parts = expected.path.split("/")
                    for part in parts[:-1]:
                        child = os.open(part, directory_flags, dir_fd=parent)
                        os.close(parent)
                        parent = child
                    descriptor = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                                         dir_fd=parent)
                    with os.fdopen(descriptor, "rb") as handle:
                        start = os.fstat(handle.fileno())
                        mode = "100755" if start.st_mode & stat.S_IXUSR else "100644"
                        _require(stat.S_ISREG(start.st_mode) and mode == expected.mode
                                 and start.st_size == len(expected.content),
                                 "retained source file type, mode or size differs")
                        content = handle.read(len(expected.content) + 1)
                        finish = os.fstat(handle.fileno())
                        stable = ("st_dev", "st_ino", "st_mode", "st_size",
                                  "st_mtime_ns", "st_ctime_ns")
                        _require(content == expected.content and all(
                            getattr(start, key) == getattr(finish, key) for key in stable),
                                 "complete retained source bytes differ")
                finally:
                    os.close(parent)
            _require(self._directory_identity(self.root) == self.root_identity
                     and self.root.resolve(strict=True) == self.root,
                     "retained source root changed")
        except OSError as exc:
            raise ProgramSourceError("complete retained source read failed") from exc
        finally:
            os.close(root_fd)

    def _run(self, arguments: tuple[str, ...], request: bytes, budget: _GitBudget,
             *, expected_returncodes: tuple[int, ...] = (0,)) -> bytes:
        return self._run_result(
            arguments, request, budget, expected_returncodes=expected_returncodes
        ).stdout

    def _run_result(self, arguments: tuple[str, ...], request: bytes, budget: _GitBudget,
                    *, expected_returncodes: tuple[int, ...] = (0,)):
        """Fixed Git operations with concurrent bounded stdin/stdout/stderr and no shell."""
        self._deadline(budget)
        _require(budget.output_remaining > 0, "Git output budget exhausted")
        deadline = min(budget.deadline, time.monotonic() + self.policy.git_timeout_seconds)
        environment = {
            "PATH": os.environ.get("PATH", ""), "LC_ALL": "C",
            "GIT_TERMINAL_PROMPT": "0", "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_SYSTEM": os.devnull, "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_NO_REPLACE_OBJECTS": "1", "GIT_NO_LAZY_FETCH": "1",
            "GIT_OPTIONAL_LOCKS": "0", "GIT_ALLOW_PROTOCOL": "",
        }
        command = [
            "git", "--no-replace-objects", "--no-lazy-fetch",
            "-c", f"core.hooksPath={os.devnull}",
            "-c", "credential.helper=", "-c", "credential.interactive=never",
            "-c", "protocol.allow=never", "-c", "protocol.ext.allow=never",
            "-c", "core.fsmonitor=false", "-c", "diff.external=",
            "-c", "diff.autoRefreshIndex=false",
            "-C", str(self.root), *arguments,
        ]
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, shell=False, start_new_session=True,
                                   env=environment)
        stdout = bytearray()
        streams = (process.stdin, process.stdout, process.stderr)
        try:
            with selectors.DefaultSelector() as selector:
                for stream, event, label in zip(streams, (selectors.EVENT_WRITE,
                       selectors.EVENT_READ, selectors.EVENT_READ), ("in", "out", "err"),
                       strict=True):
                    os.set_blocking(stream.fileno(), False)
                    if label == "in" and not request:
                        stream.close()
                    else:
                        selector.register(stream, event, label)
                sent = 0
                while selector.get_map():
                    remaining = deadline - time.monotonic()
                    _require(remaining > 0, "Git command deadline exceeded")
                    events = selector.select(remaining)
                    _require(bool(events), "Git command deadline exceeded")
                    for key, _mask in events:
                        try:
                            if key.data == "in":
                                sent += os.write(key.fd, request[sent:sent + 65_536])
                                if sent == len(request):
                                    selector.unregister(key.fileobj)
                                    key.fileobj.close()
                            else:
                                chunk = os.read(key.fd, 65_536)
                                if not chunk:
                                    selector.unregister(key.fileobj)
                                    continue
                                _require(len(chunk) <= budget.output_remaining,
                                         "Git output byte limit exceeded")
                                budget.output_remaining -= len(chunk)
                                if key.data == "out":
                                    stdout.extend(chunk)
                        except BlockingIOError:
                            continue
                remaining = deadline - time.monotonic()
                _require(remaining > 0, "Git command deadline exceeded")
                process.wait(timeout=remaining)
                _require(process.returncode in expected_returncodes, "Git source read failed")
                self._deadline(budget)
                return subprocess.CompletedProcess(command, process.returncode, bytes(stdout), b"")
        finally:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            for stream in streams:
                stream.close()
            process.wait(timeout=1)
