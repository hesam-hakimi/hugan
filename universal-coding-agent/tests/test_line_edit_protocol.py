from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from universal_coding_agent.core.models import RepositorySpec
from universal_coding_agent.core.safe_models import (
    ApprovedChangeManifest,
    ChangeOperation,
    ChangeScopeEntry,
    FileEdit,
    SafeModePolicy,
    SafeTaskRequest,
    StructuredEditProposal,
    TestProfile,
    TextReplacement,
)
from universal_coding_agent.providers.fake import FakeModelProvider
from universal_coding_agent.safe.line_editing import LineAddressedEditEngine, line_id
from universal_coding_agent.safe_service import SafeAgentService


def _git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _source(tmp_path: Path) -> tuple[Path, str]:
    source = tmp_path / "source"
    source.mkdir()
    _git(source, "init", "-b", "main")
    _git(source, "config", "user.email", "test@example.test")
    _git(source, "config", "user.name", "Test")
    (source / "app.py").write_text("def answer():\n    return 42\n", encoding="utf-8")
    _git(source, "add", "app.py")
    _git(source, "commit", "-m", "fixture")
    return source, _git(source, "rev-parse", "HEAD")


def _manifest(base_sha: str) -> ApprovedChangeManifest:
    return ApprovedChangeManifest(
        base_sha=base_sha,
        plan_hash="b" * 64,
        allowed_changes=(
            ChangeScopeEntry(
                path="app.py",
                operation=ChangeOperation.MODIFY,
                purpose="Apply the approved fixture change.",
            ),
        ),
        test_profiles=("python-check",),
        acceptance_criteria=("The approved answer is 43.",),
    )


def _proposal(token: str) -> StructuredEditProposal:
    return StructuredEditProposal(
        summary="Change the approved fixture answer with a line address.",
        edits=(
            FileEdit(
                path="app.py",
                operation=ChangeOperation.MODIFY,
                replacements=(
                    TextReplacement(old_text=token, new_text="    return 43\n"),
                ),
            ),
        ),
        requested_test_profiles=("python-check",),
    )


def test_line_addressed_engine_materializes_verified_range(tmp_path: Path) -> None:
    source, base_sha = _source(tmp_path)
    token_id = line_id(2, "    return 42\n")
    proposal = _proposal(f"@range:{token_id}..{token_id}")
    engine = LineAddressedEditEngine()

    validation = engine.validate(source, _manifest(base_sha), proposal)
    assert validation.valid is True

    result = engine.apply(source, _manifest(base_sha), proposal)
    assert result.changed_paths == ("app.py",)
    assert (source / "app.py").read_text(encoding="utf-8") == "def answer():\n    return 43\n"


def test_line_addressed_engine_rejects_fingerprint_mismatch_without_writing(
    tmp_path: Path,
) -> None:
    source, base_sha = _source(tmp_path)
    proposal = _proposal("@range:L000002-0000000000000000..L000002-0000000000000000")
    engine = LineAddressedEditEngine()

    validation = engine.validate(source, _manifest(base_sha), proposal)
    assert validation.valid is False
    assert "fingerprint mismatch" in validation.errors[0]
    assert (source / "app.py").read_text(encoding="utf-8") == "def answer():\n    return 42\n"


def test_line_addressed_engine_supports_complete_line_insertion(tmp_path: Path) -> None:
    source, base_sha = _source(tmp_path)
    anchor = line_id(2, "    return 42\n")
    proposal = StructuredEditProposal(
        summary="Insert one approved complete line.",
        edits=(
            FileEdit(
                path="app.py",
                operation=ChangeOperation.MODIFY,
                replacements=(
                    TextReplacement(
                        old_text=f"@after:{anchor}",
                        new_text="\n# deterministic follow-up\n",
                    ),
                ),
            ),
        ),
        requested_test_profiles=("python-check",),
    )
    engine = LineAddressedEditEngine()

    validation = engine.validate(source, _manifest(base_sha), proposal)
    assert validation.valid is True
    engine.apply(source, _manifest(base_sha), proposal)
    assert "# deterministic follow-up" in (source / "app.py").read_text(encoding="utf-8")


def test_safe_service_v2_runs_line_addressed_edits_end_to_end(
    tmp_path: Path,
    monkeypatch,
) -> None:
    source, base_sha = _source(tmp_path)
    token_id = line_id(2, "    return 42\n")

    def implementer(_request):
        return _proposal(f"@range:{token_id}..{token_id}").model_dump(mode="json")

    policy = SafeModePolicy(
        profiles=(
            TestProfile(
                profile_id="python-check",
                argv=(
                    sys.executable,
                    "-c",
                    "from pathlib import Path; assert 'return 43' in Path('app.py').read_text()",
                ),
            ),
        )
    )
    task = SafeTaskRequest(
        task_id="safe-line-v2-task",
        thread_id="safe-line-v2-thread",
        title="Line-addressed fixture change",
        objective="Change the approved fixture answer from 42 to 43.",
        repository=RepositorySpec(url=str(source), base_ref="main"),
        manifest=_manifest(base_sha),
        policy=policy,
    )

    monkeypatch.setenv("UCA_SAFE_EDIT_PROTOCOL", "v2-line-addressed")
    state_root = tmp_path / "state"
    service = SafeAgentService.create(
        state_root,
        FakeModelProvider(handlers={"implementer": implementer}),
        allow_local_sources=True,
    )
    try:
        service.run(task)
        assert service.state(task.thread_id)["next"] == ["scope_approval"]
        final = service.resume(task.thread_id, True)
        assert final["status"] == "completed"
        report = service.artifacts.read_json(final["final_report_ref"])
        assert report["structured_edit_protocol"] == "v2-line-addressed"
        assert report["line_addressed_edits"] is True
        assert report["semantic_anchor_repair_enabled"] is False
        assert report["canonical_patch_generated_by"] == "git"
        assert report["reviewer_verdict"] == "PASS"
        assert report["sandbox_patch_retained"] is True
        sandbox = state_root / "sandboxes" / task.task_id / "repo"
        assert "return 43" in (sandbox / "app.py").read_text(encoding="utf-8")
        assert "return 42" in (source / "app.py").read_text(encoding="utf-8")
        assert _git(source, "status", "--porcelain") == ""
    finally:
        service.close()
