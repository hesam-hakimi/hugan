from __future__ import annotations

import subprocess
from pathlib import Path

from universal_coding_agent.context.sharded_line_edit_compiler import (
    ShardedLineAddressedContextCompiler,
)
from universal_coding_agent.core.safe_models import (
    ApprovedChangeManifest,
    ChangeOperation,
    ChangeScopeEntry,
    FileEdit,
    SafeTaskRequest,
    StructuredEditProposal,
    TextReplacement,
)
from universal_coding_agent.core.models import RepositorySpec
from universal_coding_agent.safe.model_line_addressing import (
    ModelFacingLineAddressedEditEngine,
)


def _git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _fixture(tmp_path: Path) -> tuple[Path, str, ApprovedChangeManifest, SafeTaskRequest]:
    source = tmp_path / "source"
    source.mkdir()
    _git(source, "init", "-b", "main")
    _git(source, "config", "user.email", "test@example.test")
    _git(source, "config", "user.name", "Test")
    (source / "app.py").write_text("VALUE = 42\n\n", encoding="utf-8")
    _git(source, "add", "app.py")
    _git(source, "commit", "-m", "fixture")
    base_sha = _git(source, "rev-parse", "HEAD")
    manifest = ApprovedChangeManifest(
        base_sha=base_sha,
        plan_hash="a" * 64,
        allowed_changes=(
            ChangeScopeEntry(
                path="app.py",
                operation=ChangeOperation.MODIFY,
                purpose="Update the approved constant.",
            ),
        ),
        acceptance_criteria=("The approved constant is updated.",),
    )
    task = SafeTaskRequest(
        task_id="model-line-ref-task",
        thread_id="model-line-ref-thread",
        title="Model line ref qualification",
        objective="Update only the approved file.",
        repository=RepositorySpec(url=str(source), base_ref="main"),
        manifest=manifest,
    )
    return source, base_sha, manifest, task


def test_model_facing_alias_is_expanded_to_trusted_line_id(tmp_path: Path) -> None:
    source, _, manifest, _ = _fixture(tmp_path)
    proposal = StructuredEditProposal(
        summary="Update using a compact model-facing line ref.",
        edits=(
            FileEdit(
                path="app.py",
                operation=ChangeOperation.MODIFY,
                replacements=(
                    TextReplacement(
                        old_text="@range:A000001..A000001",
                        new_text="VALUE = 43\n",
                    ),
                ),
            ),
        ),
    )
    engine = ModelFacingLineAddressedEditEngine()

    validation = engine.validate(source, manifest, proposal)
    assert validation.valid is True
    engine.apply(source, manifest, proposal)
    assert (source / "app.py").read_text(encoding="utf-8") == "VALUE = 43\n\n"


def test_model_facing_alias_rejects_out_of_range_line(tmp_path: Path) -> None:
    source, _, manifest, _ = _fixture(tmp_path)
    proposal = StructuredEditProposal(
        summary="Reject an invalid compact model-facing line ref.",
        edits=(
            FileEdit(
                path="app.py",
                operation=ChangeOperation.MODIFY,
                replacements=(
                    TextReplacement(
                        old_text="@after:A999999",
                        new_text="# invalid\n",
                    ),
                ),
            ),
        ),
    )
    engine = ModelFacingLineAddressedEditEngine()

    validation = engine.validate(source, manifest, proposal)
    assert validation.valid is False
    assert "model line reference is outside app.py" in validation.errors[0]
    assert (source / "app.py").read_text(encoding="utf-8") == "VALUE = 42\n\n"


def test_sharded_context_exposes_aliases_not_fingerprints(tmp_path: Path) -> None:
    source, _, _, task = _fixture(tmp_path)
    compiler = ShardedLineAddressedContextCompiler()

    rendered = compiler._line_addressed_file_state(source, task)

    assert "A000001 | VALUE = 42" in rendered
    assert "A000002 | " in rendered
    assert "L000001-" not in rendered
    assert "e3b0c44298fc1c14" not in rendered
