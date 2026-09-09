from __future__ import annotations

import hashlib
import subprocess

import pytest

from universal_coding_agent.core.safe_models import ApprovedChangeManifest, ChangeScopeEntry
from universal_coding_agent.product.program_source_patch import verified_patch_edits
from universal_coding_agent.product.program_source_transitions import (
    ProgramSourceError,
    ProgramSourceFile,
    ProgramSourceIdentity,
    ProgramSourcePolicy,
    ProgramSourceSnapshot,
)


def _sha(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data,
                        usedforsecurity=False).hexdigest()


def _inputs(old, *, creating=False, mode="100644"):
    snapshot = ProgramSourceSnapshot(
        ProgramSourceIdentity("program-fixture", "1" * 64, "2" * 64, "3" * 64,
                              "a" * 40, "b" * 40),
        () if creating else (ProgramSourceFile("app.py", old, mode),))
    manifest = ApprovedChangeManifest(
        base_sha="a" * 40, plan_hash="d" * 64,
        allowed_changes=(ChangeScopeEntry(path="app.py",
                                          operation="create" if creating else "modify",
                                          purpose="Exact byte grammar fixture"),),
        acceptance_criteria=("The exact patch bytes apply.",))
    return snapshot, manifest


@pytest.mark.parametrize("old,new,creating,executable", [
    (b"42\n", b"43\n", False, False),
    (b"42\r\n", b"43\r\n", False, False),
    (b"42", b"43", False, False),
    (b"42\n", b"43", False, False),
    (b"42", b"43\n", False, True),
    (b"", b"new\n", True, False),
    (b"", b"new", True, True),
    (b"", b"", True, False),
    (b"\n".join(str(i).encode() for i in range(25)) + b"\n",
     b"first\n" + b"\n".join(str(i).encode() for i in range(1, 24)) + b"\nlast\n",
     False, False),
])
def test_real_git_text_patch_preserves_exact_bytes_modes_and_hunks(
    tmp_path, old, new, creating, executable,
):
    def git(*args, code=0):
        result = subprocess.run(["git", *args], cwd=tmp_path, capture_output=True, timeout=10)
        assert result.returncode == code, result.stderr
        return result.stdout

    git("init", "-b", "fixture")
    git("config", "user.name", "Fixture")
    git("config", "user.email", "fixture@example.test")
    file = tmp_path / "app.py"
    mode = "100755" if executable else "100644"
    if not creating:
        file.write_bytes(old)
        file.chmod(0o755 if executable else 0o644)
        git("add", "app.py")
        git("commit", "-m", "Preimage fixture")
    file.write_bytes(new)
    file.chmod(0o755 if executable else 0o644)
    arguments = ("diff", "--full-index", "--no-ext-diff", "--no-textconv", "--no-color")
    patch = (git(*arguments, "--no-index", "--", "/dev/null", "app.py", code=1)
             if creating else git(*arguments, "--", "app.py"))
    before, manifest = _inputs(old, creating=creating, mode=mode)
    edits = verified_patch_edits(before, patch, manifest, ProgramSourcePolicy())
    assert len(edits) == 1
    assert edits[0].replacement == ProgramSourceFile("app.py", new, mode)
    assert edits[0].expected_fingerprint == (None if creating else before.files[0].fingerprint())


def _patch():
    return (f"diff --git a/app.py b/app.py\nindex {_sha(b'42' + bytes([10]))}.."
            f"{_sha(b'43' + bytes([10]))} 100644\n--- a/app.py\n+++ b/app.py\n"
            "@@ -1 +1 @@\n-42\n+43\n").encode()


@pytest.mark.parametrize("damage", [
    lambda patch: patch.replace(b"a/app.py", b"a/other.py"),
    lambda patch: patch.replace(b"b/app.py", b"b/../app.py"),
    lambda patch: patch.replace(b"100644", b"100755"),
    lambda patch: patch.replace(b"-42", b"-41"),
    lambda patch: patch.replace(b"+43", b"+44"),
    lambda patch: patch.replace(b"@@ -1 +1 @@", b"@@ -2 +1 @@"),
    lambda patch: patch.replace(b"@@ -1 +1 @@", b"@@ -1,2 +1 @@"),
    lambda patch: patch.replace(b"@@ -1 +1 @@", b"@@ -1 +1,2 @@"),
    lambda patch: patch.replace(_sha(b"42\n").encode(), b"0" * 40),
    lambda patch: patch.replace(_sha(b"43\n").encode(), b"0" * 40),
    lambda patch: patch.replace(_sha(b"43\n").encode(), _sha(b"43\n")[:7].encode()),
    lambda patch: patch + patch,
    lambda patch: patch + b"trailing garbage\n",
    lambda patch: patch.replace(b"+43\n", b"+43\0\n"),
    lambda patch: patch[:-1],
])
def test_malformed_or_misbound_patch_cannot_inherit_valid_blob_identities(damage):
    before, manifest = _inputs(b"42\n")
    with pytest.raises((ProgramSourceError, UnicodeError)):
        verified_patch_edits(before, damage(_patch()), manifest, ProgramSourcePolicy())


def test_nonfinal_no_newline_marker_rejected_even_with_matching_full_result_blob():
    patch = (f"diff --git a/app.py b/app.py\nindex {_sha(b'x' + bytes([10]))}.."
             f"{_sha(b'ab' + bytes([10]))} 100644\n--- a/app.py\n+++ b/app.py\n"
             "@@ -1 +1,2 @@\n-x\n+a\n\\ No newline at end of file\n+b\n").encode()
    before, manifest = _inputs(b"x\n")
    with pytest.raises(ProgramSourceError, match="no-newline"):
        verified_patch_edits(before, patch, manifest, ProgramSourcePolicy())
