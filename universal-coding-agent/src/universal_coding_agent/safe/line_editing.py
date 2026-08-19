from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

from universal_coding_agent.core.safe_models import (
    ApprovedChangeManifest,
    ChangeOperation,
    EditValidationResult,
    StructuredEditProposal,
)
from universal_coding_agent.safe.patching import EditApplyResult, SafeEditEngine, status_path

_FINGERPRINT_LENGTH = 16
_LINE_ID = r"L(?P<line>[1-9][0-9]{0,5})-(?P<fingerprint>[0-9a-f]{16})"
_RANGE = re.compile(rf"^@range:(?P<start>{_LINE_ID})\.\.(?P<end>{_LINE_ID})$")
_BEFORE = re.compile(rf"^@before:(?P<anchor>{_LINE_ID})$")
_AFTER = re.compile(rf"^@after:(?P<anchor>{_LINE_ID})$")


@dataclass(frozen=True)
class _Address:
    line: int
    fingerprint: str


@dataclass(frozen=True)
class _ResolvedReplacement:
    start: int
    end: int
    new_text: str
    token: str
    insertion: bool


def logical_line_body(value: str) -> str:
    if value.endswith("\r\n"):
        return value[:-2]
    if value.endswith("\n") or value.endswith("\r"):
        return value[:-1]
    return value


def line_fingerprint(value: str) -> str:
    body = logical_line_body(value)
    return hashlib.sha256(body.encode("utf-8")).hexdigest()[:_FINGERPRINT_LENGTH]


def line_id(line_number: int, value: str) -> str:
    return f"L{line_number:06d}-{line_fingerprint(value)}"


class LineAddressedEditEngine(SafeEditEngine):
    """Materialize line-addressed edits against an immutable Git base.

    Protocol v2 deliberately removes model-authored exact old-text anchors. The model selects
    deterministic line IDs emitted by the context compiler; the control plane verifies each line
    number and fingerprint against the frozen sandbox before any write occurs.
    """

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
        if head.returncode != 0 or current_sha != manifest.base_sha:
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
                try:
                    self._resolve_replacements(edit.path, content, edit.replacements)
                except ValueError as exc:
                    errors.append(str(exc))
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
                elif self._contains_symlink_component(root, parent.relative_to(root).as_posix()):
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
            raise ValueError("line-addressed edit validation failed: " + "; ".join(validation.errors))

        root = sandbox.resolve()
        rendered: list[tuple[Path, bytes]] = []
        for edit in proposal.edits:
            path = root / edit.path
            if edit.operation is ChangeOperation.MODIFY:
                content = self._read_utf8(path)
                resolved = self._resolve_replacements(edit.path, content, edit.replacements)
                updated = content
                for item in sorted(resolved, key=lambda value: value.start, reverse=True):
                    updated = updated[: item.start] + item.new_text + updated[item.end :]
                rendered.append((path, updated.encode("utf-8")))
            else:
                rendered.append((path, (edit.content or "").encode("utf-8")))

        try:
            for path, payload in rendered:
                path.write_bytes(payload)
        except OSError as exc:
            self.restore(sandbox, manifest, proposal.changed_paths)
            raise RuntimeError("line-addressed edit write failed") from exc

        status_lines = self.status_lines(root)
        actual_paths = tuple(sorted(status_path(line) for line in status_lines))
        expected_paths = tuple(sorted(proposal.changed_paths))
        if actual_paths != expected_paths:
            self.restore(sandbox, manifest, proposal.changed_paths)
            raise RuntimeError("line-addressed edits changed paths outside the proposal")

        diff_check = self._git(
            root,
            ["-c", "core.whitespace=cr-at-eol", "diff", "--check"],
            check=False,
        )
        if diff_check.returncode != 0:
            self.restore(sandbox, manifest, proposal.changed_paths)
            raise RuntimeError("line-addressed edits failed git diff --check")

        return EditApplyResult(
            changed_paths=proposal.changed_paths,
            status_lines=status_lines,
        )

    @classmethod
    def _resolve_replacements(cls, path: str, content: str, replacements) -> tuple[_ResolvedReplacement, ...]:
        lines = content.splitlines(keepends=True)
        if not lines:
            raise ValueError(f"line-addressed modify target is empty: {path}")

        offsets = [0]
        for line in lines:
            offsets.append(offsets[-1] + len(line))

        resolved: list[_ResolvedReplacement] = []
        seen_tokens: set[str] = set()
        for replacement in replacements:
            token = replacement.old_text.strip()
            if token in seen_tokens:
                raise ValueError(f"duplicate line-address token in {path}: {token}")
            seen_tokens.add(token)

            range_match = _RANGE.fullmatch(token)
            before_match = _BEFORE.fullmatch(token)
            after_match = _AFTER.fullmatch(token)
            if not (range_match or before_match or after_match):
                raise ValueError(
                    f"invalid line-address token in {path}: expected @range, @before, or @after"
                )

            if range_match:
                start = cls._parse_address(range_match.group("start"))
                end = cls._parse_address(range_match.group("end"))
                cls._verify_address(path, lines, start)
                cls._verify_address(path, lines, end)
                if end.line < start.line:
                    raise ValueError(f"line-address range is reversed in {path}: {token}")
                start_offset = offsets[start.line - 1]
                end_offset = offsets[end.line]
                original = content[start_offset:end_offset]
                if replacement.new_text == original:
                    raise ValueError(f"line-addressed replacement is a no-op in {path}: {token}")
                expected_eol = cls._ending(lines[end.line - 1])
                if expected_eol and not replacement.new_text.endswith(expected_eol):
                    raise ValueError(
                        f"line-addressed replacement must preserve the ending of the final line in {path}: {token}"
                    )
                resolved.append(
                    _ResolvedReplacement(
                        start=start_offset,
                        end=end_offset,
                        new_text=replacement.new_text,
                        token=token,
                        insertion=False,
                    )
                )
                continue

            match = before_match or after_match
            assert match is not None
            address = cls._parse_address(match.group("anchor"))
            cls._verify_address(path, lines, address)
            if not replacement.new_text:
                raise ValueError(f"line-addressed insertion is empty in {path}: {token}")
            expected_eol = cls._ending(lines[address.line - 1]) or cls._dominant_ending(lines)
            if expected_eol and not replacement.new_text.endswith(expected_eol):
                raise ValueError(
                    f"line-addressed insertion must end with the file line ending in {path}: {token}"
                )
            point = offsets[address.line - 1] if before_match else offsets[address.line]
            resolved.append(
                _ResolvedReplacement(
                    start=point,
                    end=point,
                    new_text=replacement.new_text,
                    token=token,
                    insertion=True,
                )
            )

        cls._reject_conflicts(path, resolved)
        return tuple(resolved)

    @staticmethod
    def _parse_address(value: str) -> _Address:
        match = re.fullmatch(_LINE_ID, value)
        if match is None:
            raise ValueError("invalid line address")
        return _Address(line=int(match.group("line")), fingerprint=match.group("fingerprint"))

    @staticmethod
    def _verify_address(path: str, lines: list[str], address: _Address) -> None:
        if address.line < 1 or address.line > len(lines):
            raise ValueError(f"line address is outside {path}: line {address.line}")
        actual = line_fingerprint(lines[address.line - 1])
        if actual != address.fingerprint:
            raise ValueError(
                f"line address fingerprint mismatch in {path}: line {address.line}"
            )

    @staticmethod
    def _reject_conflicts(path: str, items: list[_ResolvedReplacement]) -> None:
        for index, left in enumerate(items):
            for right in items[index + 1 :]:
                if left.insertion and right.insertion:
                    conflict = left.start == right.start
                elif left.insertion:
                    conflict = right.start <= left.start <= right.end
                elif right.insertion:
                    conflict = left.start <= right.start <= left.end
                else:
                    conflict = left.start < right.end and right.start < left.end
                if conflict:
                    raise ValueError(
                        f"line-addressed edits overlap or have ambiguous ordering in {path}"
                    )

    @staticmethod
    def _ending(value: str) -> str:
        if value.endswith("\r\n"):
            return "\r\n"
        if value.endswith("\n"):
            return "\n"
        if value.endswith("\r"):
            return "\r"
        return ""

    @classmethod
    def _dominant_ending(cls, lines: list[str]) -> str:
        endings = [cls._ending(line) for line in lines]
        for candidate in ("\r\n", "\n", "\r"):
            if candidate in endings:
                return candidate
        return ""
