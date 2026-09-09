from __future__ import annotations

import subprocess
from pathlib import Path

from universal_coding_agent.core.safe_models import (
    ApprovedChangeManifest,
    ChangeOperation,
    ChangeScopeEntry,
    FileEdit,
    PatchProposal,
    StructuredEditProposal,
    TextReplacement,
)
from universal_coding_agent.safe.patching import SafeEditEngine, SafePatchEngine


def _git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _repository(tmp_path: Path) -> tuple[Path, str]:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-b", "main")
    _git(root, "config", "user.email", "test@example.test")
    _git(root, "config", "user.name", "Test")
    (root / "app.py").write_text("def answer():\n    return 42\n", encoding="utf-8")
    _git(root, "add", "app.py")
    _git(root, "commit", "-m", "fixture")
    return root, _git(root, "rev-parse", "HEAD")


def _manifest(base_sha: str) -> ApprovedChangeManifest:
    return ApprovedChangeManifest(
        base_sha=base_sha,
        plan_hash="b" * 64,
        allowed_changes=(
            ChangeScopeEntry(
                path="app.py",
                operation=ChangeOperation.MODIFY,
                purpose="Change the approved answer.",
            ),
        ),
        test_profiles=("python-check",),
        acceptance_criteria=("The approved file changes only.",),
    )


def _edit_proposal(old: str = "return 42", new: str = "return 43") -> StructuredEditProposal:
    return StructuredEditProposal(
        summary="Change the fixture answer.",
        edits=(
            FileEdit(
                path="app.py",
                operation=ChangeOperation.MODIFY,
                replacements=(TextReplacement(old_text=old, new_text=new),),
            ),
        ),
        requested_test_profiles=("python-check",),
    )


def _proposal(path: str = "app.py") -> PatchProposal:
    return PatchProposal(
        summary="Change the fixture answer.",
        unified_diff=(
            f"diff --git a/{path} b/{path}\n"
            f"--- a/{path}\n"
            f"+++ b/{path}\n"
            "@@ -1,2 +1,2 @@\n"
            " def answer():\n"
            "-    return 42\n"
            "+    return 43\n"
        ),
        changed_paths=(path,),
    )


def test_edit_engine_materializes_exact_change_and_git_generates_canonical_patch(
    tmp_path: Path,
) -> None:
    root, base_sha = _repository(tmp_path)
    edit_engine = SafeEditEngine()
    patch_engine = SafePatchEngine()
    manifest = _manifest(base_sha)
    proposal = _edit_proposal(
        old="def answer():\n    return 42\n",
        new="## Amendment (2026-08-07)\ndef answer():\n    return 43\n",
    )

    validation = edit_engine.validate(root, manifest, proposal)
    assert validation.valid is True
    applied = edit_engine.apply(root, manifest, proposal)
    assert applied.changed_paths == ("app.py",)

    canonical = patch_engine.capture_worktree_proposal(root, manifest, proposal)
    patch_validation = patch_engine.validate_materialized(root, manifest, canonical)

    assert patch_validation.valid is True
    assert canonical.unified_diff.startswith("diff --git a/app.py b/app.py\n")
    assert "+## Amendment (2026-08-07)" in canonical.unified_diff
    assert "@@" in canonical.unified_diff
    assert "return 43" in (root / "app.py").read_text(encoding="utf-8")
    assert edit_engine.restore(root, manifest, proposal.changed_paths) is True
    assert edit_engine.status_lines(root) == ()


def test_edit_engine_rejects_ambiguous_or_missing_exact_anchor_without_writes(
    tmp_path: Path,
) -> None:
    root, base_sha = _repository(tmp_path)
    (root / "app.py").write_text(
        "VALUE = 42\nVALUE = 42\n",
        encoding="utf-8",
    )
    _git(root, "add", "app.py")
    _git(root, "commit", "-m", "ambiguous fixture")
    base_sha = _git(root, "rev-parse", "HEAD")
    manifest = _manifest(base_sha)
    engine = SafeEditEngine()

    ambiguous = _edit_proposal(old="VALUE = 42", new="VALUE = 43")
    result = engine.validate(root, manifest, ambiguous)
    assert result.valid is False
    assert any("must occur once; found 2" in error for error in result.errors)
    assert engine.status_lines(root) == ()

    missing = _edit_proposal(old="VALUE = 99", new="VALUE = 43")
    result = engine.validate(root, manifest, missing)
    assert result.valid is False
    assert any("must occur once; found 0" in error for error in result.errors)
    assert engine.status_lines(root) == ()


def test_edit_engine_rejects_overlapping_replacements(tmp_path: Path) -> None:
    root, base_sha = _repository(tmp_path)
    proposal = StructuredEditProposal(
        summary="Overlapping anchors are unsafe.",
        edits=(
            FileEdit(
                path="app.py",
                operation=ChangeOperation.MODIFY,
                replacements=(
                    TextReplacement(
                        old_text="def answer():\n    return 42",
                        new_text="def answer():\n    return 43",
                    ),
                    TextReplacement(old_text="return 42", new_text="return 44"),
                ),
            ),
        ),
        requested_test_profiles=("python-check",),
    )

    result = SafeEditEngine().validate(root, _manifest(base_sha), proposal)
    assert result.valid is False
    assert any("overlap" in error for error in result.errors)


def test_edit_engine_create_requires_existing_parent_and_rolls_back(tmp_path: Path) -> None:
    root, base_sha = _repository(tmp_path)
    (root / "docs").mkdir()
    manifest = ApprovedChangeManifest(
        base_sha=base_sha,
        plan_hash="b" * 64,
        allowed_changes=(
            ChangeScopeEntry(
                path="docs/new.md",
                operation=ChangeOperation.CREATE,
                purpose="Create approved documentation.",
            ),
        ),
        acceptance_criteria=("Only approved documentation is created.",),
    )
    proposal = StructuredEditProposal(
        summary="Create approved documentation.",
        edits=(
            FileEdit(
                path="docs/new.md",
                operation=ChangeOperation.CREATE,
                content="# Safe documentation\n",
            ),
        ),
    )
    edit_engine = SafeEditEngine()
    patch_engine = SafePatchEngine()

    assert edit_engine.validate(root, manifest, proposal).valid is True
    edit_engine.apply(root, manifest, proposal)
    canonical = patch_engine.capture_worktree_proposal(root, manifest, proposal)
    assert "new file mode" in canonical.unified_diff
    assert "--- /dev/null" in canonical.unified_diff
    assert patch_engine.validate_materialized(root, manifest, canonical).valid is True
    assert edit_engine.restore(root, manifest, proposal.changed_paths) is True
    assert not (root / "docs/new.md").exists()

    missing_parent = StructuredEditProposal(
        summary="Missing parent must fail.",
        edits=(
            FileEdit(
                path="missing/new.md",
                operation=ChangeOperation.CREATE,
                content="text\n",
            ),
        ),
    )
    missing_manifest = ApprovedChangeManifest(
        base_sha=base_sha,
        plan_hash="b" * 64,
        allowed_changes=(
            ChangeScopeEntry(
                path="missing/new.md",
                operation=ChangeOperation.CREATE,
                purpose="Should be blocked.",
            ),
        ),
        acceptance_criteria=("Parent must already exist.",),
    )
    result = edit_engine.validate(root, missing_manifest, missing_parent)
    assert result.valid is False
    assert any("parent directory does not exist" in error for error in result.errors)


def test_edit_engine_preserves_crlf_when_replacement_is_exact(tmp_path: Path) -> None:
    root, _ = _repository(tmp_path)
    (root / "app.py").write_bytes(b"def answer():\r\n    return 42\r\n")
    _git(root, "add", "app.py")
    _git(root, "commit", "-m", "crlf fixture")
    base_sha = _git(root, "rev-parse", "HEAD")
    proposal = _edit_proposal(
        old="def answer():\r\n    return 42\r\n",
        new="def answer():\r\n    return 43\r\n",
    )

    engine = SafeEditEngine()
    engine.apply(root, _manifest(base_sha), proposal)
    assert (root / "app.py").read_bytes() == b"def answer():\r\n    return 43\r\n"
    assert engine.restore(root, _manifest(base_sha), proposal.changed_paths) is True


def test_edit_engine_rejects_out_of_scope_edit(tmp_path: Path) -> None:
    root, base_sha = _repository(tmp_path)
    proposal = StructuredEditProposal(
        summary="Out of scope.",
        edits=(
            FileEdit(
                path="other.py",
                operation=ChangeOperation.CREATE,
                content="VALUE = 1\n",
            ),
        ),
    )
    result = SafeEditEngine().validate(root, _manifest(base_sha), proposal)
    assert result.valid is False
    assert any("outside approved scope" in error for error in result.errors)
    assert SafeEditEngine().status_lines(root) == ()


def test_patch_engine_validates_applies_and_rolls_back(tmp_path: Path) -> None:
    root, base_sha = _repository(tmp_path)
    engine = SafePatchEngine()
    proposal = _proposal()

    validation = engine.validate(root, _manifest(base_sha), proposal)
    assert validation.valid is True
    assert validation.changed_paths == ("app.py",)

    applied = engine.apply(root, _manifest(base_sha), proposal)
    assert applied.changed_paths == ("app.py",)
    assert (root / "app.py").read_text(encoding="utf-8").endswith("return 43\n")
    assert engine.rollback(root, proposal) is True
    assert (root / "app.py").read_text(encoding="utf-8").endswith("return 42\n")
    assert engine.status_lines(root) == ()


def test_patch_engine_accepts_reordered_changed_path_declaration(tmp_path: Path) -> None:
    root, _ = _repository(tmp_path)
    (root / "other.py").write_text("VALUE = 1\n", encoding="utf-8")
    _git(root, "add", "other.py")
    _git(root, "commit", "-m", "add other")
    base_sha = _git(root, "rev-parse", "HEAD")

    manifest = ApprovedChangeManifest(
        base_sha=base_sha,
        plan_hash="b" * 64,
        allowed_changes=(
            ChangeScopeEntry(
                path="app.py",
                operation=ChangeOperation.MODIFY,
                purpose="Change app.",
            ),
            ChangeScopeEntry(
                path="other.py",
                operation=ChangeOperation.MODIFY,
                purpose="Change other.",
            ),
        ),
        acceptance_criteria=("Both approved files change.",),
    )
    proposal = PatchProposal(
        summary="Change two approved files.",
        unified_diff=(
            "diff --git a/app.py b/app.py\n"
            "--- a/app.py\n"
            "+++ b/app.py\n"
            "@@ -1,2 +1,2 @@\n"
            " def answer():\n"
            "-    return 42\n"
            "+    return 43\n"
            "diff --git a/other.py b/other.py\n"
            "--- a/other.py\n"
            "+++ b/other.py\n"
            "@@ -1 +1 @@\n"
            "-VALUE = 1\n"
            "+VALUE = 2\n"
        ),
        changed_paths=("other.py", "app.py"),
    )

    validation = SafePatchEngine().validate(root, manifest, proposal)

    assert validation.valid is True
    assert validation.changed_paths == ("app.py", "other.py")


def test_patch_engine_rejects_out_of_scope_path(tmp_path: Path) -> None:
    root, _ = _repository(tmp_path)
    (root / "other.py").write_text("def answer():\n    return 42\n", encoding="utf-8")
    _git(root, "add", "other.py")
    _git(root, "commit", "-m", "other")
    latest_sha = _git(root, "rev-parse", "HEAD")

    result = SafePatchEngine().validate(root, _manifest(latest_sha), _proposal("other.py"))
    assert result.valid is False
    assert any("outside approved scope" in error for error in result.errors)


def test_patch_engine_rejects_delete_and_binary_markers(tmp_path: Path) -> None:
    root, base_sha = _repository(tmp_path)
    manifest = _manifest(base_sha)
    delete = PatchProposal(
        summary="unsafe",
        unified_diff=(
            "diff --git a/app.py b/app.py\n"
            "deleted file mode 100644\n"
            "--- a/app.py\n"
            "+++ /dev/null\n"
            "@@ -1,2 +0,0 @@\n"
            "-def answer():\n"
            "-    return 42\n"
        ),
        changed_paths=("app.py",),
    )
    result = SafePatchEngine().validate(root, manifest, delete)
    assert result.valid is False
    assert any("forbidden" in error for error in result.errors)


def test_patch_engine_surfaces_bounded_git_apply_diagnostics(tmp_path: Path) -> None:
    root, base_sha = _repository(tmp_path)
    mismatched = PatchProposal(
        summary="Use stale context so git apply rejects the patch.",
        unified_diff=(
            "diff --git a/app.py b/app.py\n"
            "--- a/app.py\n"
            "+++ b/app.py\n"
            "@@ -1,2 +1,2 @@\n"
            " def answer():\n"
            "-    return 99\n"
            "+    return 43\n"
        ),
        changed_paths=("app.py",),
    )

    result = SafePatchEngine().validate(root, _manifest(base_sha), mismatched)

    assert result.valid is False
    error = "\n".join(result.errors)
    assert "git apply --check rejected the proposed patch" in error
    assert "app.py" in error
    assert len(error) < 5_000
