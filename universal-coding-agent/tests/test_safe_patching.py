from __future__ import annotations

import subprocess
from pathlib import Path

from universal_coding_agent.core.safe_models import (
    ApprovedChangeManifest,
    ChangeOperation,
    ChangeScopeEntry,
    PatchProposal,
)
from universal_coding_agent.safe.patching import SafePatchEngine


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
        acceptance_criteria=("The approved file changes only.",),
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


def test_patch_engine_rejects_out_of_scope_path(tmp_path: Path) -> None:
    root, base_sha = _repository(tmp_path)
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
