from __future__ import annotations

import re
from pathlib import Path

_LOOSE_OBJECT_DIRECTORY = re.compile(r"^[0-9a-f]{2}$")
_HEAD_REF_PREFIX = "refs/heads/"


def git_metadata_paths_are_safe(
    sandbox: Path,
    *,
    local_ref: str = "",
) -> bool:
    """Return whether Git metadata used by publication is real and sandbox-local."""

    git_dir = sandbox / ".git"
    try:
        if not _real_directory(git_dir, required=True):
            return False
        common_dir_file = git_dir / "commondir"
        if common_dir_file.exists() or common_dir_file.is_symlink():
            return False
        if not _real_directory(git_dir / "objects", required=True):
            return False
        if not _real_directory(git_dir / "refs", required=True):
            return False
        if not _real_directory(git_dir / "refs" / "heads", required=True):
            return False

        for relative in (
            ("objects", "info"),
            ("objects", "pack"),
            ("info",),
            ("logs",),
            ("logs", "refs"),
            ("logs", "refs", "heads"),
        ):
            if not _real_directory(git_dir.joinpath(*relative), required=False):
                return False

        for name in ("HEAD", "index", "packed-refs"):
            if not _real_file(git_dir / name, required=name == "HEAD"):
                return False

        objects = git_dir / "objects"
        for child in objects.iterdir():
            if _LOOSE_OBJECT_DIRECTORY.fullmatch(child.name) and not _real_directory(
                child,
                required=True,
            ):
                return False

        if local_ref:
            if not local_ref.startswith(_HEAD_REF_PREFIX):
                return False
            branch = local_ref.removeprefix(_HEAD_REF_PREFIX)
            if not branch or not _safe_ref_path(git_dir / "refs" / "heads", branch):
                return False
            if not _safe_ref_path(
                git_dir / "logs" / "refs" / "heads",
                branch,
                root_optional=True,
            ):
                return False
    except OSError:
        return False
    return True


def _real_directory(path: Path, *, required: bool) -> bool:
    if path.is_symlink():
        return False
    if not path.exists():
        return not required
    return path.is_dir()


def _real_file(path: Path, *, required: bool) -> bool:
    if path.is_symlink():
        return False
    if not path.exists():
        return not required
    return path.is_file() and path.stat(follow_symlinks=False).st_nlink == 1


def _safe_ref_path(root: Path, branch: str, *, root_optional: bool = False) -> bool:
    if not _real_directory(root, required=not root_optional):
        return False
    if not root.exists():
        return True
    current = root
    parts = branch.split("/")
    for index, part in enumerate(parts):
        current = current / part
        if current.is_symlink():
            return False
        if not current.exists():
            return True
        if index == len(parts) - 1:
            return _real_file(current, required=True)
        if not current.is_dir():
            return False
    return True
