from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from universal_coding_agent.core.models import RepositorySpec, ReviewVerdict
from universal_coding_agent.core.safe_models import (
    ApprovedChangeManifest,
    ChangeOperation,
    ChangeScopeEntry,
    FileEdit,
    SafeModePolicy,
    SafeReviewResult,
    SafeTaskRequest,
    StructuredEditProposal,
    TestProfile,
    TextReplacement,
)
from universal_coding_agent.providers.fake import FakeModelProvider
from universal_coding_agent.safe.line_editing import line_id
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


def test_v2_shards_files_and_corrects_one_invalid_address_once(
    tmp_path: Path,
    monkeypatch,
) -> None:
    source = tmp_path / "source"
    source.mkdir()
    _git(source, "init", "-b", "main")
    _git(source, "config", "user.email", "test@example.test")
    _git(source, "config", "user.name", "Test")
    (source / "app.py").write_text("VALUE = 42\n", encoding="utf-8")
    (source / "notes.md").write_text("Status: old\n", encoding="utf-8")
    _git(source, "add", "app.py", "notes.md")
    _git(source, "commit", "-m", "fixture")
    base_sha = _git(source, "rev-parse", "HEAD")

    app_token = line_id(1, "VALUE = 42\n")
    notes_token = line_id(1, "Status: old\n")
    phases: list[tuple[str, str]] = []

    def implementer(request):
        target = str(request.metadata.get("target_path"))
        phase = str(request.metadata.get("shard_phase"))
        phases.append((target, phase))
        if target == "app.py":
            proposal = StructuredEditProposal(
                summary="Update the approved app constant.",
                edits=(
                    FileEdit(
                        path="app.py",
                        operation=ChangeOperation.MODIFY,
                        replacements=(
                            TextReplacement(
                                old_text=f"@range:{app_token}..{app_token}",
                                new_text="VALUE = 43\n",
                            ),
                        ),
                    ),
                ),
                requested_test_profiles=("python-check",),
            )
            return proposal.model_dump(mode="json")
        if target == "notes.md" and phase == "initial":
            proposal = StructuredEditProposal(
                summary="Return one deliberately invalid address for correction.",
                edits=(
                    FileEdit(
                        path="notes.md",
                        operation=ChangeOperation.MODIFY,
                        replacements=(
                            TextReplacement(
                                old_text=(
                                    "@range:L002994-0000000000000000.."
                                    "L002994-0000000000000000"
                                ),
                                new_text="Status: new\n",
                            ),
                        ),
                    ),
                ),
                requested_test_profiles=("python-check",),
            )
            return proposal.model_dump(mode="json")
        if target == "notes.md" and phase == "address_correction":
            proposal = StructuredEditProposal(
                summary="Correct the notes address using the assigned file token.",
                edits=(
                    FileEdit(
                        path="notes.md",
                        operation=ChangeOperation.MODIFY,
                        replacements=(
                            TextReplacement(
                                old_text=f"@range:{notes_token}..{notes_token}",
                                new_text="Status: new\n",
                            ),
                        ),
                    ),
                ),
                requested_test_profiles=("python-check",),
            )
            return proposal.model_dump(mode="json")
        raise AssertionError(f"unexpected implementer shard: {target=} {phase=}")

    def reviewer(_request):
        return SafeReviewResult(
            verdict=ReviewVerdict.PASS,
            requirement_findings=("Both approved file shards satisfy the task.",),
            confidence="high",
        ).model_dump(mode="json")

    manifest = ApprovedChangeManifest(
        base_sha=base_sha,
        plan_hash="c" * 64,
        allowed_changes=(
            ChangeScopeEntry(
                path="app.py",
                operation=ChangeOperation.MODIFY,
                purpose="Update the approved constant.",
            ),
            ChangeScopeEntry(
                path="notes.md",
                operation=ChangeOperation.MODIFY,
                purpose="Update the approved status documentation.",
            ),
        ),
        test_profiles=("python-check",),
        acceptance_criteria=("Both approved files contain their new values.",),
        max_changed_files=2,
    )
    policy = SafeModePolicy(
        profiles=(
            TestProfile(
                profile_id="python-check",
                argv=(
                    sys.executable,
                    "-c",
                    (
                        "from pathlib import Path; "
                        "assert Path('app.py').read_text() == 'VALUE = 43\\n'; "
                        "assert Path('notes.md').read_text() == 'Status: new\\n'"
                    ),
                ),
            ),
        )
    )
    task = SafeTaskRequest(
        task_id="safe-sharded-v2-task",
        thread_id="safe-sharded-v2-thread",
        title="Sharded line-addressed edit qualification",
        objective="Update exactly the two approved files.",
        repository=RepositorySpec(url=str(source), base_ref="main"),
        manifest=manifest,
        policy=policy,
    )

    monkeypatch.setenv("UCA_SAFE_EDIT_PROTOCOL", "v2-line-addressed")
    state_root = tmp_path / "state"
    service = SafeAgentService.create(
        state_root,
        FakeModelProvider(handlers={"implementer": implementer, "reviewer": reviewer}),
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
        assert report["file_sharded_implementer"] is True
        assert report["reviewer_verdict"] == "PASS"
        diagnostics = service.artifacts.read_json(report["implementer_validation_ref"])
        assert diagnostics["sharded"] is True
        assert diagnostics["address_correction_used"] is True
        assert phases == [
            ("app.py", "initial"),
            ("notes.md", "initial"),
            ("notes.md", "address_correction"),
        ]
        sandbox = state_root / "sandboxes" / task.task_id / "repo"
        assert (sandbox / "app.py").read_text(encoding="utf-8") == "VALUE = 43\n"
        assert (sandbox / "notes.md").read_text(encoding="utf-8") == "Status: new\n"
        assert (source / "app.py").read_text(encoding="utf-8") == "VALUE = 42\n"
        assert (source / "notes.md").read_text(encoding="utf-8") == "Status: old\n"
        assert _git(source, "status", "--porcelain") == ""
    finally:
        service.close()
