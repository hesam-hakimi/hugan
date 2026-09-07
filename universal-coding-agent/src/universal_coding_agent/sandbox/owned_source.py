"""Private, descriptor-relative source staging. No Git, execution, or deletion.

The caller is the trusted Program materializer, never an HTTP/model path input.
POSIX no-follow descriptors prevent link traversal; the same-UID host remains
trusted. The deadline is checked around bounded I/O, not a kernel I/O watchdog.
"""

from __future__ import annotations

import os
import stat
import time
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path

from universal_coding_agent.product.program_source_transitions import (
    ProgramSourceError,
    ProgramSourceSnapshot,
    _canonical,
    _hash,
    _require,
)


@dataclass(frozen=True)
class OwnedSourcePolicy:
    max_entries: int = 40_000
    max_metadata_bytes: int = 8_000_000
    operation_seconds: int = 60

    def __post_init__(self):
        for value, maximum in ((self.max_entries, 40_000),
                               (self.max_metadata_bytes, 8_000_000),
                               (self.operation_seconds, 300)):
            _require(type(value) is int and 0 < value <= maximum,
                     "invalid owned source policy bound")

    def canonical_hash(self):
        return _hash(_canonical({"schema": "uca-owned-source-policy-1", **asdict(self)}))


def _identity(info):
    return [info.st_dev, info.st_ino, info.st_uid, stat.S_IMODE(info.st_mode)]


def _stamp(info):
    return [*_identity(info), info.st_mode, info.st_size, info.st_nlink,
            info.st_mtime_ns, info.st_ctime_ns]


class OwnedSourceTree:
    def __init__(self, root: Path, policy: OwnedSourcePolicy):
        _require(os.name == "posix" and hasattr(os, "O_NOFOLLOW")
                 and hasattr(os, "O_DIRECTORY") and os.open in os.supports_dir_fd
                 and os.mkdir in os.supports_dir_fd and os.scandir in os.supports_fd,
                 "descriptor-based owned source materialization is unavailable")
        _require(root.is_absolute() and ".." not in root.parts and len(root.parts) <= 128,
                 "invalid host sandbox root")
        self.root, self.policy = root, policy
        self.directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC

    def deadline(self):
        return time.monotonic() + self.policy.operation_seconds

    @staticmethod
    def check_time(deadline):
        _require(time.monotonic() <= deadline, "owned source operation deadline exceeded")

    @contextmanager
    def root_handle(self, expected=None):
        """Open every absolute component without following links, including on reload."""
        fd = os.open("/", self.directory_flags)
        try:
            chain = [_identity(os.fstat(fd))]
            for component in self.root.parts[1:]:
                next_fd = os.open(component, self.directory_flags, dir_fd=fd)
                os.close(fd)
                fd = next_fd
                chain.append(_identity(os.fstat(fd)))
            info = os.fstat(fd)
            _require(info.st_uid == os.geteuid() and not info.st_mode & 0o022,
                     "sandbox root must be owned and not writable by other users")
            _require(expected is None or chain == expected, "sandbox root identity changed")
            yield fd, chain
        except OSError as exc:
            raise ProgramSourceError("owned source root or filesystem operation rejected") from exc
        finally:
            os.close(fd)

    def anchor(self, chain):
        with self.root_handle(chain):
            pass

    @contextmanager
    def directory(self, parent, name, expected=None):
        fd = os.open(name, self.directory_flags, dir_fd=parent)
        try:
            before = os.fstat(fd)
            _require(before.st_uid == os.geteuid() and stat.S_IMODE(before.st_mode) == 0o700
                     and before.st_dev == os.fstat(parent).st_dev,
                     "source directory ownership or mode differs")
            _require(expected is None or _identity(before) == expected,
                     "source directory identity changed")
            yield fd
            current = os.stat(name, dir_fd=parent, follow_symlinks=False)
            _require(stat.S_ISDIR(current.st_mode) and _identity(current) == _identity(before),
                     "source parent or directory was substituted")
        finally:
            os.close(fd)

    def _write_new(self, parent, name, content, mode, deadline):
        self.check_time(deadline)
        fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
                     | os.O_CLOEXEC | os.O_NONBLOCK, 0o600, dir_fd=parent)
        try:
            view = memoryview(content)
            while view:
                self.check_time(deadline)
                written = os.write(fd, view[:65_536])
                _require(written > 0, "source write made no progress")
                view = view[written:]
            os.fchmod(fd, mode)
            os.fsync(fd)
            self.check_time(deadline)
            self._read_exact(parent, name, content, mode, deadline,
                             expected_identity=_identity(os.fstat(fd)))
        finally:
            os.close(fd)

    def _read_exact(self, parent, name, content, mode, deadline, expected_identity=None,
                    *, sync=False):
        self.check_time(deadline)
        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK,
                     dir_fd=parent)
        try:
            before = os.fstat(fd)
            _require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1
                     and before.st_uid == os.geteuid() and before.st_dev == os.fstat(parent).st_dev
                     and stat.S_IMODE(before.st_mode) == mode and before.st_size == len(content),
                     "source file type, ownership, links, mode or size differs")
            _require(expected_identity is None or _identity(before) == expected_identity,
                     "source file was substituted during write")
            offset = 0
            while offset < len(content):
                self.check_time(deadline)
                chunk = os.read(fd, min(65_536, len(content) - offset))
                _require(bool(chunk) and chunk == content[offset:offset + len(chunk)],
                         "source bytes differ")
                offset += len(chunk)
            _require(os.read(fd, 1) == b"", "source file grew")
            if sync:
                # A crash may leave exact cached bytes before their first fsync.
                os.fsync(fd)
            after = os.fstat(fd)
            linked = os.stat(name, dir_fd=parent, follow_symlinks=False)
            _require(_stamp(before) == _stamp(after) == _stamp(linked),
                     "source file changed during verification")
            self.check_time(deadline)
            return _stamp(after)
        finally:
            os.close(fd)

    def layout(self, snapshot: ProgramSourceSnapshot):
        """Bound directories and path metadata before allocating any destination."""
        tree = {}
        entries, metadata = 0, 0
        for item in snapshot.files:
            node, parts = tree, item.path.split("/")
            for index, part in enumerate(parts):
                if part not in node:
                    entries += 1
                    metadata += len("/".join(parts[:index + 1])) + 256
                    _require(entries <= self.policy.max_entries
                             and metadata <= self.policy.max_metadata_bytes,
                             "source directory or metadata budget exceeded")
                    node[part] = {} if index < len(parts) - 1 else item
                node = node[part]
        return tree

    def allocate(self, root_fd, name, marker, deadline):
        """Exclusive allocation only. An unrecorded existing name is never adopted."""
        self.check_time(deadline)
        os.mkdir(name, 0o700, dir_fd=root_fd)
        with self.directory(root_fd, name) as operation:
            self._write_new(operation, ".uca-owner.json", marker, 0o600, deadline)
            os.mkdir("source", 0o700, dir_fd=operation)
            with self.directory(operation, "source") as source:
                os.fsync(source)
                allocation = {"operation": _identity(os.fstat(operation)),
                              "source": _identity(os.fstat(source))}
            os.fsync(operation)
        os.fsync(root_fd)
        self.check_time(deadline)
        return allocation

    @staticmethod
    def _names(fd, expected, *, complete):
        # Iterate rather than listdir: an unexpected/massive directory fails at
        # the first extra entry without an unbounded allocation.
        seen = set()
        with os.scandir(fd) as entries:
            for entry in entries:
                _require(entry.name in expected and entry.name not in seen,
                         "unexpected source tree entry")
                seen.add(entry.name)
        _require(not complete or seen == set(expected), "source tree entry is missing")
        return seen

    def _walk(self, fd, tree, deadline, *, fill, prefix=""):
        present = self._names(fd, tree, complete=not fill)
        for name, node in tree.items():
            self.check_time(deadline)
            if isinstance(node, dict):
                if name not in present:
                    os.mkdir(name, 0o700, dir_fd=fd)
                with self.directory(fd, name) as child:
                    self._walk(child, node, deadline, fill=fill, prefix=f"{prefix}{name}/")
            else:
                mode = 0o755 if node.mode == "100755" else 0o644
                if name not in present:
                    self._write_new(fd, name, node.content, mode, deadline)
                else:
                    self._read_exact(fd, name, node.content, mode, deadline, sync=fill)
            if fill:
                os.fsync(fd)
        self._names(fd, tree, complete=True)

    def _proof(self, fd, tree, deadline, prefix=""):
        before = os.fstat(fd)
        self._names(fd, tree, complete=True)
        proof = {prefix: _stamp(before)}
        for name, node in tree.items():
            self.check_time(deadline)
            path = f"{prefix}{name}"
            if isinstance(node, dict):
                with self.directory(fd, name) as child:
                    proof.update(self._proof(child, node, deadline, path + "/"))
            else:
                mode = 0o755 if node.mode == "100755" else 0o644
                proof[path] = self._read_exact(fd, name, node.content, mode, deadline)
        self._names(fd, tree, complete=True)
        _require(_stamp(before) == _stamp(os.fstat(fd)),
                 "source directory changed during verification")
        return proof

    def inspect(self, root_fd, name, marker, allocation, tree, deadline, *, fill=False):
        """No existing bytes are overwritten, including during explicit recovery."""
        with self.directory(root_fd, name, allocation["operation"]) as operation:
            self._names(operation, {".uca-owner.json", "source"}, complete=True)
            owner = self._read_exact(operation, ".uca-owner.json", marker, 0o600, deadline)
            with self.directory(operation, "source", allocation["source"]) as source:
                if fill:
                    self._walk(source, tree, deadline, fill=True)
                    os.fsync(source)
                    os.fsync(operation)
                    os.fsync(root_fd)
                proof = self._proof(source, tree, deadline)
            self._names(operation, {".uca-owner.json", "source"}, complete=True)
            _require(owner == self._read_exact(operation, ".uca-owner.json", marker,
                                               0o600, deadline), "ownership marker changed")
            raw = _canonical({"owner": owner, "entries": proof,
                              "operation": _stamp(os.fstat(operation))})
            _require(len(raw) <= self.policy.max_metadata_bytes,
                     "source verification metadata budget exceeded")
            self.check_time(deadline)
            return raw
