from __future__ import annotations

import hashlib
import os
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from universal_coding_agent.core.safe_models import (
    ApprovedChangeManifest,
    ChangeOperation,
    EditValidationResult,
    PatchProposal,
    PatchValidationResult,
    StructuredEditProposal,
    normalize_repository_path,
)
from universal_coding_agent.safety.sanitizer import sanitize_text

_DIFF_HEADER = re.compile(r"^diff --git a/([^\s]+) b/([^\s]+)$")
_SHA = re.compile(r"^[0-9a-f]{40,64}$")
_FORBIDDEN_MARKERS = (
    "GIT binary patch",
    "Binary files ",
    "rename from ",
    "rename to ",
    "copy from ",
    "copy to ",
    "deleted file mode ",
    "old mode 120000",
    "new mode 120000",
)
_GIT_APPLY_DIAGNOSTIC_LIMIT = 4_000


@dataclass(frozen=True)
class EditApplyResult:
    changed_paths: tuple[str, ...]
    status_lines: tuple[str, ...]


@dataclass(frozen=True)
class PatchApplyResult:
    patch_sha256: str
    changed_paths: tuple[str, ...]
    status_lines: tuple[str, ...]


class SafeEditEngine:
    """Materialize exact structured text edits inside an isolated clean sandbox."""

    def __init__(self, *, git_binary: str = "git", timeout_seconds: int = 300) -> None:
        self.git_binary = git_binary
        self.timeout_seconds = timeout_seconds

    def validate(
        self,
        sandbox: Path,
        manifest: ApprovedChangeManifest,
        proposal: StructuredEditProposal,
    ) -> EditValidationResult:
        root = sandbox.resolve()
        errors: list[str] = []
        paths = proposal.changed_paths

        if len(paths) > manifest.max_changed_files:
            errors.append("structured edits exceed max_changed_files")

        requested = set(proposal.requested_test_profiles)
        approved_profiles = set(manifest.test_profiles)
        if not requested.issubset(approved_profiles):
            errors.append("structured edits requested an unapproved test profile")

        head = self._git(root, ["rev-parse", "HEAD"], check=False)
        current_sha = head.stdout.strip()
        if head.returncode != 0 or not _SHA.fullmatch(current_sha):
            errors.append("unable to read sandbox HEAD")
        elif current_sha != manifest.base_sha:
            errors.append("sandbox HEAD does not match approved base_sha")

        status = self._git(root, ["status", "--porcelain=v1", "-uall"], check=False)
        if status.returncode != 0 or status.stdout.strip():
            errors.append("sandbox must be clean before structured edit validation")

        allowed = manifest.allowed_path_map()
        for edit in proposal.edits:
            if edit.path not in allowed:
                errors.append(f"structured edit path is outside approved scope: {edit.path}")
                continue
            if edit.operation is not allowed[edit.path]:
                errors.append(
                    f"structured edit operation for {edit.path} is {edit.operation.value}, "
                    f"expected {allowed[edit.path].value}"
                )
                continue

            raw_path = root / edit.path
            try:
                destination = self._contained_path(root, edit.path)
            except ValueError as exc:
                errors.append(str(exc))
                continue
            if self._contains_symlink_component(root, edit.path):
                errors.append(f"approved edit path contains a symlink component: {edit.path}")
                continue

            if edit.operation is ChangeOperation.MODIFY:
                if not raw_path.is_file() or destination != raw_path.resolve():
                    errors.append(f"modify target does not exist as a regular file: {edit.path}")
                    continue
                try:
                    content = self._read_utf8(raw_path)
                except (OSError, UnicodeDecodeError):
                    errors.append(f"modify target is not readable UTF-8 text: {edit.path}")
                    continue
                errors.extend(self._replacement_errors(edit.path, content, edit.replacements))
            else:
                if raw_path.exists():
                    errors.append(f"create target already exists: {edit.path}")
                    continue
                parent = raw_path.parent
                try:
                    resolved_parent = parent.resolve()
                except OSError:
                    errors.append(f"create parent cannot be resolved: {edit.path}")
                    continue
                if resolved_parent != root and root not in resolved_parent.parents:
                    errors.append(f"create parent escapes sandbox: {edit.path}")
                elif not parent.is_dir():
                    errors.append(f"create parent directory does not exist: {edit.path}")
                elif self._contains_symlink_component(
                    root,
                    PurePosixPath(edit.path).parent.as_posix(),
                ):
                    errors.append(f"create parent contains a symlink component: {edit.path}")

        return EditValidationResult(
            valid=not errors,
            changed_paths=paths,
            errors=tuple(errors),
        )

    def apply(
        self,
        sandbox: Path,
        manifest: ApprovedChangeManifest,
        proposal: StructuredEditProposal,
    ) -> EditApplyResult:
        validation = self.validate(sandbox, manifest, proposal)
        if not validation.valid:
            raise ValueError("structured edit validation failed: " + "; ".join(validation.errors))

        root = sandbox.resolve()
        rendered: list[tuple[Path, bytes]] = []
        for edit in proposal.edits:
            path = root / edit.path
            if edit.operation is ChangeOperation.MODIFY:
                content = self._read_utf8(path)
                spans = self._replacement_spans(edit.path, content, edit.replacements)
                updated = content
                for start, end, replacement in sorted(
                    spans,
                    key=lambda item: item[0],
                    reverse=True,
                ):
                    updated = updated[:start] + replacement.new_text + updated[end:]
                rendered.append((path, updated.encode("utf-8")))
            else:
                rendered.append((path, (edit.content or "").encode("utf-8")))

        try:
            for path, payload in rendered:
                path.write_bytes(payload)
        except OSError as exc:
            self.restore(sandbox, manifest, proposal.changed_paths)
            raise RuntimeError("structured edit write failed") from exc

        status_lines = self.status_lines(root)
        actual_paths = tuple(sorted(status_path(line) for line in status_lines))
        expected_paths = tuple(sorted(proposal.changed_paths))
        if actual_paths != expected_paths:
            self.restore(sandbox, manifest, proposal.changed_paths)
            raise RuntimeError("structured edits changed paths outside the proposal")

        diff_check = self._git(
            root,
            ["-c", "core.whitespace=cr-at-eol", "diff", "--check"],
            check=False,
        )
        if diff_check.returncode != 0:
            self.restore(sandbox, manifest, proposal.changed_paths)
            raise RuntimeError("structured edits failed git diff --check")

        return EditApplyResult(
            changed_paths=proposal.changed_paths,
            status_lines=status_lines,
        )

    def restore(
        self,
        sandbox: Path,
        manifest: ApprovedChangeManifest,
        changed_paths: tuple[str, ...],
    ) -> bool:
        root = sandbox.resolve()
        allowed = manifest.allowed_path_map()
        ok = True
        for path in changed_paths:
            operation = allowed.get(path)
            if operation is ChangeOperation.MODIFY:
                result = self._git(
                    root,
                    ["restore", "--worktree", "--source", "HEAD", "--", path],
                    check=False,
                )
                ok = ok and result.returncode == 0
            elif operation is ChangeOperation.CREATE:
                target = root / path
                try:
                    if target.exists() or target.is_symlink():
                        target.unlink()
                except OSError:
                    ok = False
            else:
                ok = False
        try:
            remaining = set(status_path(line) for line in self.status_lines(root))
        except (RuntimeError, ValueError):
            return False
        return ok and not (remaining & set(changed_paths))

    def status_lines(self, sandbox: Path) -> tuple[str, ...]:
        result = self._git(
            sandbox.resolve(),
            ["status", "--porcelain=v1", "-uall"],
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError("unable to read sandbox status")
        return tuple(line for line in result.stdout.splitlines() if line.strip())

    @staticmethod
    def _read_utf8(path: Path) -> str:
        return path.read_bytes().decode("utf-8")

    @classmethod
    def _replacement_errors(cls, path: str, content: str, replacements) -> list[str]:
        try:
            cls._replacement_spans(path, content, replacements)
        except ValueError as exc:
            return [str(exc)]
        return []

    @staticmethod
    def _replacement_spans(path: str, content: str, replacements):
        spans = []
        seen_old_text: set[str] = set()
        for replacement in replacements:
            if replacement.old_text in seen_old_text:
                raise ValueError(f"duplicate exact replacement anchor in {path}")
            seen_old_text.add(replacement.old_text)
            count = content.count(replacement.old_text)
            if count != 1:
                raise ValueError(
                    f"exact replacement anchor in {path} must occur once; found {count}"
                )
            start = content.index(replacement.old_text)
            spans.append((start, start + len(replacement.old_text), replacement))

        ordered = sorted(spans, key=lambda item: item[0])
        for previous, current in zip(ordered, ordered[1:], strict=False):
            if previous[1] > current[0]:
                raise ValueError(f"structured replacements overlap in {path}")
        return spans

    @staticmethod
    def _contained_path(root: Path, relative: str) -> Path:
        path = (root / relative).resolve()
        if path != root and root not in path.parents:
            raise ValueError("approved path escapes sandbox")
        return path

    @staticmethod
    def _contains_symlink_component(root: Path, relative: str) -> bool:
        if relative in {"", "."}:
            return False
        cursor = root
        for part in PurePosixPath(relative).parts:
            cursor = cursor / part
            if cursor.is_symlink():
                return True
        return False

    def _git(self, root: Path, arguments: list[str], *, check: bool = True):
        environment = {
            "PATH": os.environ.get("PATH", ""),
            "HOME": os.environ.get("HOME", ""),
            "GIT_TERMINAL_PROMPT": "0",
        }
        process = subprocess.run(
            [self.git_binary, "-C", str(root), *arguments],
            check=False,
            capture_output=True,
            text=True,
            timeout=self.timeout_seconds,
            shell=False,
            env=environment,
        )
        if check and process.returncode != 0:
            raise RuntimeError("fixed git operation failed")
        return process


class SafePatchEngine:
    """Validate canonical Git diffs and retain legacy patch-apply support."""

    def __init__(self, *, git_binary: str = "git", timeout_seconds: int = 300) -> None:
        self.git_binary = git_binary
        self.timeout_seconds = timeout_seconds

    def capture_worktree_proposal(
        self,
        sandbox: Path,
        manifest: ApprovedChangeManifest,
        edit_proposal: StructuredEditProposal,
    ) -> PatchProposal:
        root = sandbox.resolve()
        status_lines = self.status_lines(root)
        actual_paths = tuple(sorted(status_path(line) for line in status_lines))
        expected_paths = tuple(sorted(edit_proposal.changed_paths))
        if actual_paths != expected_paths:
            raise RuntimeError("worktree paths do not match structured edit proposal")

        sections: list[str] = []
        edit_by_path = {item.path: item for item in edit_proposal.edits}
        ordered_paths = [
            item.path for item in manifest.allowed_changes if item.path in edit_by_path
        ]
        for path in ordered_paths:
            operation = edit_by_path[path].operation
            if operation is ChangeOperation.MODIFY:
                result = self._git(
                    root,
                    ["diff", "--no-ext-diff", "--no-color", "--full-index", "--", path],
                    check=False,
                )
                if result.returncode != 0 or not result.stdout:
                    raise RuntimeError(f"unable to generate Git diff for modified path: {path}")
                sections.append(result.stdout)
            else:
                result = self._git(
                    root,
                    [
                        "diff",
                        "--no-index",
                        "--no-color",
                        "--full-index",
                        "--",
                        "/dev/null",
                        path,
                    ],
                    check=False,
                )
                if result.returncode not in {0, 1} or not result.stdout:
                    raise RuntimeError(f"unable to generate Git diff for created path: {path}")
                sections.append(result.stdout)

        unified_diff = "".join(
            section if section.endswith("\n") else section + "\n" for section in sections
        )
        return PatchProposal(
            summary=edit_proposal.summary,
            unified_diff=unified_diff,
            changed_paths=tuple(ordered_paths),
            requested_test_profiles=edit_proposal.requested_test_profiles,
            assumptions=edit_proposal.assumptions,
        )

    def validate_materialized(
        self,
        sandbox: Path,
        manifest: ApprovedChangeManifest,
        proposal: PatchProposal,
    ) -> PatchValidationResult:
        root = sandbox.resolve()
        errors: list[str] = []
        patch_bytes = proposal.unified_diff.encode("utf-8")
        patch_sha = hashlib.sha256(patch_bytes).hexdigest()

        if len(patch_bytes) > manifest.max_patch_bytes:
            errors.append("patch exceeds max_patch_bytes")

        try:
            changed_paths, operations = parse_unified_diff(proposal.unified_diff)
        except ValueError as exc:
            return PatchValidationResult(
                valid=False,
                patch_sha256=patch_sha,
                errors=(str(exc),),
            )

        if set(proposal.changed_paths) != set(changed_paths):
            errors.append("proposal changed_paths do not exactly match the patch path set")
        if len(changed_paths) > manifest.max_changed_files:
            errors.append("patch exceeds max_changed_files")

        allowed = manifest.allowed_path_map()
        for path in changed_paths:
            if path not in allowed:
                errors.append(f"patch path is outside approved scope: {path}")
                continue
            if operations[path] is not allowed[path]:
                errors.append(
                    f"patch operation for {path} is {operations[path].value}, "
                    f"expected {allowed[path].value}"
                )

        requested = set(proposal.requested_test_profiles)
        if not requested.issubset(set(manifest.test_profiles)):
            errors.append("proposal requested an unapproved test profile")

        head = self._git(root, ["rev-parse", "HEAD"], check=False)
        current_sha = head.stdout.strip()
        if head.returncode != 0 or not _SHA.fullmatch(current_sha):
            errors.append("unable to read sandbox HEAD")
        elif current_sha != manifest.base_sha:
            errors.append("sandbox HEAD does not match approved base_sha")

        try:
            status_lines = self.status_lines(root)
            actual_paths = tuple(sorted(status_path(line) for line in status_lines))
        except (RuntimeError, ValueError) as exc:
            errors.append(str(exc))
            actual_paths = ()
        if actual_paths != tuple(sorted(changed_paths)):
            errors.append("materialized worktree paths do not exactly match the canonical patch")

        diff_check = self._git(
            root,
            ["-c", "core.whitespace=cr-at-eol", "diff", "--check"],
            check=False,
        )
        if diff_check.returncode != 0:
            errors.append("materialized worktree failed git diff --check")

        return PatchValidationResult(
            valid=not errors,
            patch_sha256=patch_sha,
            changed_paths=changed_paths,
            errors=tuple(errors),
        )

    def validate(
        self,
        sandbox: Path,
        manifest: ApprovedChangeManifest,
        proposal: PatchProposal,
    ) -> PatchValidationResult:
        root = sandbox.resolve()
        errors: list[str] = []
        patch_bytes = proposal.unified_diff.encode("utf-8")
        patch_sha = hashlib.sha256(patch_bytes).hexdigest()

        if len(patch_bytes) > manifest.max_patch_bytes:
            errors.append("patch exceeds max_patch_bytes")

        try:
            changed_paths, operations = parse_unified_diff(proposal.unified_diff)
        except ValueError as exc:
            return PatchValidationResult(
                valid=False,
                patch_sha256=patch_sha,
                errors=(str(exc),),
            )

        if set(proposal.changed_paths) != set(changed_paths):
            errors.append("proposal changed_paths do not exactly match the patch path set")
        if len(changed_paths) > manifest.max_changed_files:
            errors.append("patch exceeds max_changed_files")

        allowed = manifest.allowed_path_map()
        for path in changed_paths:
            if path not in allowed:
                errors.append(f"patch path is outside approved scope: {path}")
                continue
            if operations[path] is not allowed[path]:
                errors.append(
                    f"patch operation for {path} is {operations[path].value}, "
                    f"expected {allowed[path].value}"
                )
                continue
            destination = self._contained_path(root, path)
            if destination.is_symlink():
                errors.append(f"approved path is a symlink: {path}")
            if operations[path] is ChangeOperation.MODIFY and not destination.is_file():
                errors.append(f"modify target does not exist as a regular file: {path}")
            if operations[path] is ChangeOperation.CREATE and destination.exists():
                errors.append(f"create target already exists: {path}")

        requested = set(proposal.requested_test_profiles)
        approved_profiles = set(manifest.test_profiles)
        if not requested.issubset(approved_profiles):
            errors.append("proposal requested an unapproved test profile")

        head = self._git(root, ["rev-parse", "HEAD"], check=False)
        current_sha = head.stdout.strip()
        if head.returncode != 0 or not _SHA.fullmatch(current_sha):
            errors.append("unable to read sandbox HEAD")
        elif current_sha != manifest.base_sha:
            errors.append("sandbox HEAD does not match approved base_sha")

        status = self._git(root, ["status", "--porcelain=v1", "-uall"], check=False)
        if status.returncode != 0 or status.stdout.strip():
            errors.append("sandbox must be clean before patch validation")

        if not errors:
            patch_path = self._write_temporary_patch(root, proposal.unified_diff)
            try:
                result = self._git(
                    root,
                    [
                        "apply",
                        "--check",
                        "--verbose",
                        "--whitespace=error",
                        "--recount",
                        str(patch_path),
                    ],
                    check=False,
                )
                if result.returncode != 0:
                    diagnostic = _bounded_git_diagnostic(result.stdout, result.stderr)
                    message = "git apply --check rejected the proposed patch"
                    if diagnostic:
                        message += f": {diagnostic}"
                    errors.append(message)
            finally:
                patch_path.unlink(missing_ok=True)

        return PatchValidationResult(
            valid=not errors,
            patch_sha256=patch_sha,
            changed_paths=changed_paths,
            errors=tuple(errors),
        )

    def apply(
        self,
        sandbox: Path,
        manifest: ApprovedChangeManifest,
        proposal: PatchProposal,
    ) -> PatchApplyResult:
        validation = self.validate(sandbox, manifest, proposal)
        if not validation.valid:
            raise ValueError("patch validation failed: " + "; ".join(validation.errors))

        root = sandbox.resolve()
        patch_path = self._write_temporary_patch(root, proposal.unified_diff)
        try:
            self._git(
                root,
                ["apply", "--whitespace=error", "--recount", str(patch_path)],
            )
        finally:
            patch_path.unlink(missing_ok=True)

        diff_check = self._git(
            root,
            ["-c", "core.whitespace=cr-at-eol", "diff", "--check"],
            check=False,
        )
        if diff_check.returncode != 0:
            raise RuntimeError("applied patch failed git diff --check")

        status_lines = self.status_lines(root)
        actual_paths = tuple(sorted(status_path(line) for line in status_lines))
        if actual_paths != tuple(sorted(validation.changed_paths)):
            raise RuntimeError("applied patch changed paths outside the validated proposal")

        return PatchApplyResult(
            patch_sha256=validation.patch_sha256,
            changed_paths=validation.changed_paths,
            status_lines=status_lines,
        )

    def rollback(self, sandbox: Path, proposal: PatchProposal) -> bool:
        root = sandbox.resolve()
        if not self.status_lines(root):
            return True
        patch_path = self._write_temporary_patch(root, proposal.unified_diff)
        try:
            check = self._git(
                root,
                ["apply", "-R", "--check", "--recount", str(patch_path)],
                check=False,
            )
            if check.returncode != 0:
                return False
            applied = self._git(
                root,
                ["apply", "-R", "--recount", str(patch_path)],
                check=False,
            )
            if applied.returncode != 0:
                return False
        finally:
            patch_path.unlink(missing_ok=True)
        return not self.status_lines(root)

    def verify_changed_paths(
        self,
        sandbox: Path,
        approved_paths: tuple[str, ...],
    ) -> tuple[bool, tuple[str, ...]]:
        lines = self.status_lines(sandbox.resolve())
        actual = tuple(sorted(status_path(line) for line in lines))
        allowed = set(approved_paths)
        return set(actual).issubset(allowed), actual

    def status_lines(self, sandbox: Path) -> tuple[str, ...]:
        result = self._git(
            sandbox.resolve(),
            ["status", "--porcelain=v1", "-uall"],
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError("unable to read sandbox status")
        return tuple(line for line in result.stdout.splitlines() if line.strip())

    def _write_temporary_patch(self, sandbox: Path, value: str) -> Path:
        descriptor, name = tempfile.mkstemp(
            prefix="uca-safe-",
            suffix=".patch",
            dir=sandbox.parent,
        )
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(value)
        return Path(name)

    def _git(self, root: Path, arguments: list[str], *, check: bool = True):
        environment = {
            "PATH": os.environ.get("PATH", ""),
            "HOME": os.environ.get("HOME", ""),
            "GIT_TERMINAL_PROMPT": "0",
        }
        process = subprocess.run(
            [self.git_binary, "-C", str(root), *arguments],
            check=False,
            capture_output=True,
            text=True,
            timeout=self.timeout_seconds,
            shell=False,
            env=environment,
        )
        if check and process.returncode != 0:
            raise RuntimeError("fixed git operation failed")
        return process

    @staticmethod
    def _contained_path(root: Path, relative: str) -> Path:
        path = (root / relative).resolve()
        if path != root and root not in path.parents:
            raise ValueError("approved path escapes sandbox")
        return path


def _bounded_git_diagnostic(stdout: str, stderr: str) -> str:
    combined = "\n".join(part.strip() for part in (stderr, stdout) if part.strip())
    if not combined:
        return ""
    sanitized = sanitize_text(combined).replace("\x00", "")
    return sanitized[:_GIT_APPLY_DIAGNOSTIC_LIMIT]


def patch_validation_allows_applicability_repair(result: PatchValidationResult) -> bool:
    """Legacy raw-patch repair gate retained for compatibility; new Safe Mode does not use it."""

    return (
        not result.valid
        and len(result.errors) == 1
        and result.errors[0].startswith("git apply --check rejected the proposed patch")
    )


def parse_unified_diff(value: str) -> tuple[tuple[str, ...], dict[str, ChangeOperation]]:
    if not value.endswith("\n"):
        raise ValueError("unified diff must end with a newline")
    if any(marker in value for marker in _FORBIDDEN_MARKERS):
        raise ValueError(
            "patch contains a forbidden binary, rename, copy, delete, or symlink marker"
        )

    lines = value.splitlines()
    if not lines or not lines[0].startswith("diff --git "):
        raise ValueError("patch must use git-style unified diff sections")

    paths: list[str] = []
    operations: dict[str, ChangeOperation] = {}
    index = 0
    while index < len(lines):
        header = _DIFF_HEADER.fullmatch(lines[index])
        if header is None:
            raise ValueError("unexpected content outside a diff section")
        old_path = normalize_repository_path(header.group(1))
        new_path = normalize_repository_path(header.group(2))
        if old_path != new_path:
            raise ValueError("rename and copy patches are not supported")
        path = new_path
        if path in operations:
            raise ValueError(f"patch contains duplicate file section: {path}")

        index += 1
        section: list[str] = []
        while index < len(lines) and not lines[index].startswith("diff --git "):
            section.append(lines[index])
            index += 1

        first_hunk_index = next(
            (position for position, line in enumerate(section) if line.startswith("@@ ")),
            None,
        )
        if first_hunk_index is None:
            raise ValueError(f"patch section contains no hunks: {path}")
        metadata_prefix = section[:first_hunk_index]
        old_marker = next((line for line in metadata_prefix if line.startswith("--- ")), None)
        new_marker = next((line for line in metadata_prefix if line.startswith("+++ ")), None)
        if old_marker is None or new_marker is None:
            raise ValueError(f"patch section lacks file markers: {path}")

        is_create = "new file mode " in "\n".join(metadata_prefix)
        if is_create:
            if old_marker != "--- /dev/null" or new_marker != f"+++ b/{path}":
                raise ValueError(f"invalid create patch markers: {path}")
            operation = ChangeOperation.CREATE
        else:
            if old_marker != f"--- a/{path}" or new_marker != f"+++ b/{path}":
                raise ValueError(f"invalid modify patch markers: {path}")
            operation = ChangeOperation.MODIFY

        paths.append(path)
        operations[path] = operation

    if not paths:
        raise ValueError("patch contains no changed files")
    return tuple(paths), operations


def status_path(line: str) -> str:
    if len(line) < 4:
        raise ValueError("invalid porcelain status line")
    raw = line[3:].strip()
    if " -> " in raw or raw.startswith('"'):
        raise ValueError("renamed or quoted status paths are not supported")
    return normalize_repository_path(raw)
