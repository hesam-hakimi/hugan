"""Apply a bounded canonical Git text patch to immutable bytes, without Git writes."""

from __future__ import annotations

import hashlib
import re

from universal_coding_agent.core.safe_models import ApprovedChangeManifest
from universal_coding_agent.product.program_source_transitions import (
    ProgramSourceEdit,
    ProgramSourceFile,
    ProgramSourcePolicy,
    ProgramSourceSnapshot,
    _path,
    _require,
)


def _lines(data: bytes) -> list[bytes]:
    # bytes.splitlines also splits CR; Git hunks delimit lines with LF only.
    parts = data.split(b"\n")
    return [part + b"\n" for part in parts[:-1]] + ([parts[-1]] if parts[-1] else [])


def _blob(data: bytes, width: int) -> str:
    algorithm = "sha1" if width == 40 else "sha256"
    return hashlib.new(algorithm, b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def verified_patch_edits(
    before: ProgramSourceSnapshot, patch: bytes, manifest: ApprovedChangeManifest,
    policy: ProgramSourcePolicy,
) -> tuple[ProgramSourceEdit, ...]:
    """Reject unsupported representations instead of delegating patch authority to Git."""
    _require(type(patch) is bytes and 0 < len(patch) <= manifest.max_patch_bytes,
             "patch exceeds its approved byte bound")
    patch.decode("utf-8")
    _require(b"\0" not in patch and patch.endswith(b"\n"), "unsupported patch encoding")
    source = {item.path: item for item in before.files}
    scope = manifest.allowed_path_map()
    lines = _lines(patch)
    width = len(manifest.base_sha)
    _require(width in (40, 64), "unsupported Git object identity")
    edits: dict[str, ProgramSourceEdit] = {}
    cursor = 0
    while cursor < len(lines):
        header = re.fullmatch(rb"diff --git a/([^\s]+) b/([^\s]+)\n", lines[cursor])
        _require(header is not None and header[1] == header[2], "unsupported patch path")
        path = header[1].decode("ascii")
        _path(path)
        _require(path in scope and path not in edits, "duplicate or unapproved patch path")
        cursor += 1
        old = source.get(path)
        creating = scope[path].value == "create"
        _require(creating == (old is None), "patch operation disagrees with source preimage")
        mode = old.mode if old else "100644"
        if creating:
            _require(cursor < len(lines) and lines[cursor] in (
                b"new file mode 100644\n", b"new file mode 100755\n"),
                "missing new-file mode")
            mode = lines[cursor].split()[3].decode().strip()
            cursor += 1
        _require(cursor < len(lines), "missing full Git blob identity")
        index = re.fullmatch(rb"index ([0-9a-f]+)\.\.([0-9a-f]+)(?: (100644|100755))?\n",
                             lines[cursor])
        _require(index is not None and len(index[1]) == width and len(index[2]) == width,
                 "patch needs full Git blob identities")
        _require((creating and index[3] is None) or (
            not creating and index[3] == mode.encode()), "unsupported source mode transition")
        old_bytes = old.content if old else b""
        old_bytes.decode("utf-8")
        _require(b"\0" not in old_bytes, "binary source edit is unsupported")
        expected_old = "0" * width if creating else _blob(old_bytes, width)
        _require(index[1].decode() == expected_old, "patch blob preimage differs")
        cursor += 1
        preimage = _lines(old_bytes)
        output: list[bytes] = []
        consumed = 0
        if cursor < len(lines) and lines[cursor].startswith(b"--- "):
            old_path = b"/dev/null" if creating else b"a/" + path.encode()
            _require(lines[cursor] == b"--- " + old_path + b"\n"
                     and cursor + 1 < len(lines)
                     and lines[cursor + 1] == b"+++ b/" + path.encode() + b"\n",
                     "patch marker paths differ")
            cursor += 2
            hunks = 0
            while cursor < len(lines) and lines[cursor].startswith(b"@@ "):
                hunk = re.fullmatch(rb"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@[^\n]*\n",
                                    lines[cursor])
                _require(hunk is not None, "invalid hunk header")
                old_start, old_count = int(hunk[1]), int(hunk[2] or b"1")
                new_start, new_count = int(hunk[3]), int(hunk[4] or b"1")
                offset = old_start - 1 if old_count else old_start
                _require(consumed <= offset <= len(preimage), "overlapping or stale hunk")
                output.extend(preimage[consumed:offset])
                _require((new_start - 1 if new_count else new_start) == len(output),
                         "inconsistent result hunk coordinates")
                consumed = offset
                seen_old = seen_new = 0
                cursor += 1
                while cursor < len(lines) and lines[cursor][:1] in (b" ", b"+", b"-"):
                    tag, content = lines[cursor][:1], lines[cursor][1:]
                    cursor += 1
                    if cursor < len(lines) and lines[cursor] == b"\\ No newline at end of file\n":
                        _require(content.endswith(b"\n"), "invalid no-newline marker")
                        content = content[:-1]
                        cursor += 1
                    if tag != b"+":
                        _require(consumed < len(preimage) and preimage[consumed] == content,
                                 "hunk preimage differs")
                        consumed += 1
                        seen_old += 1
                    if tag != b"-":
                        output.append(content)
                        seen_new += 1
                    _require(seen_old <= old_count and seen_new <= new_count,
                             "hunk exceeds declared line counts")
                _require((seen_old, seen_new) == (old_count, new_count),
                         "incomplete hunk counts")
                hunks += 1
            _require(hunks > 0, "patch has no content hunks")
        output.extend(preimage[consumed:])
        _require(all(line.endswith(b"\n") for line in output[:-1]),
                 "no-newline marker precedes another result line")
        content = b"".join(output)
        _require(len(content) <= policy.max_file_bytes, "patched file exceeds policy")
        _require(index[2].decode() == _blob(content, width), "patch result blob differs")
        _require(creating or content != old_bytes, "patch does not change source")
        edits[path] = ProgramSourceEdit(path, old.fingerprint() if old else None,
                                        ProgramSourceFile(path, content, mode))
        _require(len(edits) <= policy.max_changes, "too many source changes")
    _require(bool(edits), "patch has no source edits")
    return tuple(edits[path] for path in sorted(edits))
