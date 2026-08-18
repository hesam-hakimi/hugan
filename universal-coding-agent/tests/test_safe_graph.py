from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from universal_coding_agent.core.models import RepositorySpec, ReviewResult, ReviewVerdict
from universal_coding_agent.core.safe_models import (
    ApprovedChangeManifest,
    ChangeOperation,
    ChangeScopeEntry,
    SafeModePolicy,
    SafeTaskRequest,
    TestProfile,
)
from universal_coding_agent.providers.fake import FakeModelProvider
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


def _task(source: Path, base_sha: str, task_id: str) -> SafeTaskRequest:
    manifest = ApprovedChangeManifest(
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
    policy = SafeModePolicy(
        profiles=(
            TestProfile(
                profile_id="python-check",
                argv=(
                    sys.executable,
                    "-c",
                    (
                        "from pathlib import Path; "
                        "assert 'return 43' in Path('app.py').read_text()"
                    ),
                ),
            ),
        )
    )
    return SafeTaskRequest(
        task_id=task_id,
        thread_id=task_id,
        title="Safe fixture change",
        objective="Change the approved fixture answer from 42 to 43.",
        repository=RepositorySpec(url=str(source), base_ref="main"),
        manifest=manifest,
        policy=policy,
    )


def test_safe_graph_requires_approval_and_retains_only_passing_patch(tmp_path: Path) -> None:
    source, base_sha = _source(tmp_path)
    state_root = tmp_path / "state"
    service = SafeAgentService.create(
        state_root,
        FakeModelProvider(),
        allow_local_sources=True,
    )
    task = _task(source, base_sha, "safe-task-pass")
    try:
        first = service.run(task)
        assert first["status"] in {"indexed", "awaiting_scope_approval"}
        snapshot = service.state(task.thread_id)
        assert snapshot["next"] == ["scope_approval"]

        final = service.resume(task.thread_id, True)
        assert final["status"] == "completed"
        assert final["reviewer_verdict"] == "PASS"
        assert final["rolled_back"] is False
        report = service.artifacts.read_json(final["final_report_ref"])
        assert report["sandbox_patch_retained"] is True
        assert report["stage_commit_push_pr_merge_deploy"] is False

        sandbox = state_root / "sandboxes" / task.task_id / "repo"
        assert "return 43" in (sandbox / "app.py").read_text(encoding="utf-8")
        assert "return 42" in (source / "app.py").read_text(encoding="utf-8")
        assert _git(source, "status", "--porcelain") == ""
        assert _git(sandbox, "log", "-1", "--format=%s") == "fixture"
    finally:
        service.close()


def test_safe_graph_rolls_back_when_reviewer_has_conditions(tmp_path: Path) -> None:
    source, base_sha = _source(tmp_path)

    def conditional_review(_request):
        return ReviewResult(
            verdict=ReviewVerdict.PASS_WITH_CONDITIONS,
            required_actions=("Add another test before acceptance.",),
            confidence="high",
        ).model_dump(mode="json")

    state_root = tmp_path / "state"
    service = SafeAgentService.create(
        state_root,
        FakeModelProvider(handlers={"reviewer": conditional_review}),
        allow_local_sources=True,
    )
    task = _task(source, base_sha, "safe-task-rollback")
    try:
        service.run(task)
        final = service.resume(task.thread_id, True)
        assert final["status"] == "blocked"
        assert final["reviewer_verdict"] == "PASS_WITH_CONDITIONS"
        assert final["rolled_back"] is True
        sandbox = state_root / "sandboxes" / task.task_id / "repo"
        assert "return 42" in (sandbox / "app.py").read_text(encoding="utf-8")
        assert _git(sandbox, "status", "--porcelain") == ""
    finally:
        service.close()
