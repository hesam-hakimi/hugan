"""Opt-in accounting for a single source acceptance capture, never authority.

No execution service imports and no active default. Reservations are made before
payload reads; short reads refund unused capacity. Repeated reads count again.
"""

from __future__ import annotations

import os
import stat
import time
from contextlib import contextmanager
from contextvars import ContextVar
from hashlib import sha256
from pathlib import Path

_ACTIVE = ContextVar("uca_source_capture_budget", default=None)
MAX_CAPTURE = 256_000_000


def current():
    return _ACTIVE.get()


def charge(size):
    budget = current()
    if budget is not None:
        budget.charge(size)


def read(fd, size):
    budget = current()
    if budget is None:
        return os.read(fd, size)
    budget.charge(size)
    raw = os.read(fd, size)
    budget.remaining += size - len(raw)
    return raw


def stamp(info):
    return [
        info.st_dev,
        info.st_ino,
        info.st_mode,
        info.st_uid,
        info.st_gid,
        info.st_size,
        info.st_nlink,
        info.st_mtime_ns,
        info.st_ctime_ns,
    ]


class CaptureBudget:
    def __init__(self, maximum=MAX_CAPTURE, seconds=120):
        if type(maximum) is not int or not 0 < maximum <= MAX_CAPTURE:
            raise ValueError("invalid source capture budget")
        self.remaining = maximum
        self.deadline = time.monotonic() + seconds
        self.files = {}
        self.locations = {}
        self.children = set()

    def charge(self, size):
        if (
            type(size) is not int
            or size < 0
            or size > self.remaining
            or time.monotonic() >= self.deadline
        ):
            raise ValueError("source capture cumulative byte/time budget exceeded")
        self.remaining -= size

    @contextmanager
    def activate(self):
        if current() is not None:
            raise ValueError("nested source capture budget")
        token = _ACTIVE.set(self)
        try:
            yield self
        finally:
            _ACTIVE.reset(token)

    def read_artifact(self, root, relative, maximum, *, git_object=False):
        """Walk every parent without following links; retain exact file identity."""
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_NONBLOCK
        parent = os.open(root, flags)
        chain = [stamp(os.fstat(parent))]
        try:
            parts = relative.parts
            for part in parts[:-1]:
                child = os.open(part, flags, dir_fd=parent)
                os.close(parent)
                parent = child
                chain.append(stamp(os.fstat(parent)))
            fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
            try:
                before = os.fstat(fd)
                if (
                    not stat.S_ISREG(before.st_mode)
                    or (before.st_nlink != 1 and not git_object)
                    or before.st_uid != os.geteuid()
                    or before.st_size > maximum
                ):
                    raise ValueError("source evidence file type/owner/size differs")
                raw = read(fd, before.st_size + 1)
                after = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
                if (
                    len(raw) != before.st_size
                    or stamp(before) != stamp(os.fstat(fd))
                    or stamp(before) != stamp(after)
                ):
                    raise ValueError("source evidence changed during read")
                observation = {
                    "chain": chain,
                    "file": stamp(before),
                    "sha256": sha256(raw).hexdigest(),
                }
                name = str(root / relative)
                self.locations[name] = (root, relative, maximum, git_object)
                previous = self.files.setdefault(name, observation)
                if previous != observation:
                    raise ValueError("source evidence identity changed during capture")
                return raw
            finally:
                os.close(fd)
        finally:
            os.close(parent)

    def settled(self):
        self.charge(0)
        if self.children:
            raise ValueError("source capture retains an unsettled Git child")

    def inventory(self, root):
        """Stream a bounded origin inventory; never materialize an unbounded directory list."""
        result, count = {}, 0
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_NONBLOCK

        def walk(fd, relative, depth):
            nonlocal count
            self.charge(0)
            if depth > 64:
                raise ValueError("origin path depth exceeded")
            before = stamp(os.fstat(fd))
            with os.scandir(fd) as entries:
                for entry in entries:
                    count += 1
                    if count > 20_000:
                        raise ValueError("origin inventory count exceeded")
                    path = relative / entry.name
                    info = entry.stat(follow_symlinks=False)
                    if stat.S_ISDIR(info.st_mode):
                        child = os.open(entry.name, flags, dir_fd=fd)
                        try:
                            if stamp(os.fstat(child)) != stamp(info):
                                raise ValueError("origin directory replaced")
                            walk(child, path, depth + 1)
                        finally:
                            os.close(child)
                    else:
                        raw = self.read_artifact(
                            root, path, 1_000_000, git_object=path.parts[:2] == (".git", "objects")
                        )
                        result[str(path)] = sha256(raw).hexdigest()
            if before != stamp(os.fstat(fd)):
                raise ValueError("origin directory changed during inventory")
            result[str(relative)] = before

        fd = os.open(root, flags)
        try:
            walk(fd, Path("."), 0)
        finally:
            os.close(fd)
        return result

    def recheck_files(self):
        # Reuse the immutable read observations; compare before final SQLite commit.
        for name, observed in tuple(self.files.items()):
            root, relative, maximum, git_object = self.locations[name]
            raw = self.read_artifact(root, relative, maximum, git_object=git_object)
            current_file = self.files[name]["file"]
            if current_file != observed["file"] or sha256(raw).hexdigest() != observed["sha256"]:
                raise ValueError("captured artifact changed before commit")
