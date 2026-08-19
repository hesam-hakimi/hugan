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


def _structured_payload(*, old_text: str, new_text: str) -> dict:
    return {
        "summary": "Change the approved fixture answer.",
        "edits": [
            {
                "path": "app.py",
                "operation": "modify",
                "replacements": [
                    {
                        "old_text": old_text,
                        "new_text": new_text,
                    }
                ],
                "content": None,
            }
        ],
        "requested_test_profiles": ["python-check"],
        "assumptions": [],
    }


def test_safe_graph_requires_approval_and_retains_only_passing_change(tmp_path: Path) -> None:
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
        assert report["model_authored_patch"] is False
        assert report["canonical_patch_generated_by"] == "git"
        assert report["structured_edit_protocol"] == "v1"
        assert report["edit_repair_used"] is False
        assert report["stage_commit_push_pr_merge_deploy"] is False

        edit_proposal = service.artifacts.read_json(report["edit_proposal_ref"])
        assert edit_proposal["edits"][0]["path"] == "app.py"
        canonical_patch = service.artifacts.read_text(report["patch_ref"])
        assert canonical_patch.startswith("diff --git a/app.py b/app.py\n")

        sandbox = state_root / "sandboxes" / task.task_id / "repo"
        assert "return 43" in (sandbox / "app.py").read_text(encoding="utf-8")
        assert "return 42" in (source / "app.py").read_text(encoding="utf-8")
        assert _git(source, "status", "--porcelain") == ""
        assert _git(sandbox, "log", "-1", "--format=%s") == "fixture"
    finally:
        service.close()


def test_safe_graph_repairs_structured_edit_schema_without_requesting_patch_syntax(
    tmp_path: Path,
) -> None:
    source, base_sha = _source(tmp_path)

    def implementer(request):
        if request.metadata.get("schema_repair") == "true":
            return _structured_payload(
                old_text="def answer():\n    return 42\n",
                new_text="def answer():\n    return 43\n",
            )
        return {
            "summary": "Old raw patch shape must be rejected.",
            "unified_diff": (
                "diff --git a/app.py b/app.py\n"
                "--- a/app.py\n"
                "+++ b/app.py\n"
                "@@ -1,2 +1,2 @@\n"
                " def answer():\n"
                "-    return 42\n"
                "+    return 43\n"
            ),
            "changed_paths": ["app.py"],
            "requested_test_profiles": ["python-check"],
            "assumptions": [],
        }

    state_root = tmp_path / "state"
    service = SafeAgentService.create(
        state_root,
        FakeModelProvider(handlers={"implementer": implementer}),
        allow_local_sources=True,
    )
    task = _task(source, base_sha, "safe-task-structured-repair")
    try:
        service.run(task)
        final = service.resume(task.thread_id, True)
        assert final["status"] == "completed"
        validation = service.artifacts.read_json(final["implementer_validation_ref"])
        assert validation["repair_used"] is True
        assert len(validation["attempts"]) == 2
        assert validation["attempts"][0]["schema_valid"] is False
        assert validation["attempts"][1]["schema_valid"] is True
        report = service.artifacts.read_json(final["final_report_ref"])
        assert report["model_authored_patch"] is False
        assert report["patch_repair_used"] is False
        assert report["edit_repair_used"] is False
    finally:
        service.close()


def test_safe_graph_git_generates_valid_patch_for_markdown_like_insertions(tmp_path: Path) -> None:
    source, base_sha = _source(tmp_path)

    def implementer(_request):
        return _structured_payload(
            old_text="def answer():\n    return 42\n",
            new_text=(
                "## Amendment (2026-08-07): generated as file content\n"
                "def answer():\n"
                "    return 43\n"
            ),
        )

    state_root = tmp_path / "state"
    service = SafeAgentService.create(
        state_root,
        FakeModelProvider(handlers={"implementer": implementer}),
        allow_local_sources=True,
    )
    task = _task(source, base_sha, "safe-task-markdown-content")
    try:
        service.run(task)
        final = service.resume(task.thread_id, True)
        assert final["status"] == "completed"
        patch = service.artifacts.read_text(final["patch_ref"])
        assert "+## Amendment (2026-08-07): generated as file content" in patch
        validation = service.artifacts.read_json(final["patch_validation_ref"])
        assert validation["valid"] is True
        assert not validation["errors"]
    finally:
        service.close()


def test_safe_graph_repairs_missing_exact_anchor_once_with_frozen_file_context(
    tmp_path: Path,
) -> None:
    source, base_sha = _source(tmp_path)
    implementer_requests = []

    def implementer(request):
        implementer_requests.append(request)
        if request.metadata.get("edit_repair") == "true":
            assert "exact replacement anchor in app.py must occur once; found 0" in request.user_prompt
            assert "def answer():\n    return 42\n" in request.user_prompt
            return _structured_payload(
                old_text="def answer():\n    return 42\n",
                new_text="def answer():\n    return 43\n",
            )
        return _structured_payload(old_text="return 99", new_text="return 43")

    state_root = tmp_path / "state"
    service = SafeAgentService.create(
        state_root,
        FakeModelProvider(handlers={"implementer": implementer}),
        allow_local_sources=True,
    )
    task = _task(source, base_sha, "safe-task-anchor-repair")
    try:
        service.run(task)
        final = service.resume(task.thread_id, True)
        assert final["status"] == "completed"
        report = service.artifacts.read_json(final["final_report_ref"])
        assert report["edit_repair_used"] is True
        assert report["initial_edit_proposal_ref"] != report["edit_proposal_ref"]
        assert report["edit_repair_context_ref"]
        assert report["edit_repair_validation_ref"]
        assert report["edit_repair_proposal_ref"] == report["edit_proposal_ref"]
        assert sum(
            request.metadata.get("edit_repair") == "true"
            for request in implementer_requests
        ) == 1
        sandbox = state_root / "sandboxes" / task.task_id / "repo"
        assert "return 43" in (sandbox / "app.py").read_text(encoding="utf-8")
        assert "return 42" in (source / "app.py").read_text(encoding="utf-8")
        assert _git(source, "status", "--porcelain") == ""
    finally:
        service.close()


def test_safe_graph_blocks_after_one_failed_exact_anchor_repair_without_mutation(
    tmp_path: Path,
) -> None:
    source, base_sha = _source(tmp_path)
    implementer_requests = []

    def implementer(request):
        implementer_requests.append(request)
        return _structured_payload(old_text="return 99", new_text="return 43")

    state_root = tmp_path / "state"
    service = SafeAgentService.create(
        state_root,
        FakeModelProvider(handlers={"implementer": implementer}),
        allow_local_sources=True,
    )
    task = _task(source, base_sha, "safe-task-anchor-repair-exhausted")
    try:
        service.run(task)
        final = service.resume(task.thread_id, True)
        assert final["status"] == "blocked"
        assert "edit:validation_failed" in final["safe_errors"]
        assert final.get("patch_ref") is None
        report = service.artifacts.read_json(final["final_report_ref"])
        assert report["edit_repair_used"] is True
        assert report["edit_repair_proposal_ref"]
        assert sum(
            request.metadata.get("edit_repair") == "true"
            for request in implementer_requests
        ) == 1
        sandbox = state_root / "sandboxes" / task.task_id / "repo"
        assert "return 42" in (sandbox / "app.py").read_text(encoding="utf-8")
        assert _git(sandbox, "status", "--porcelain") == ""
        assert _git(source, "status", "--porcelain") == ""
    finally:
        service.close()


def test_safe_graph_does_not_repair_non_anchor_scope_validation_failure(tmp_path: Path) -> None:
    source, base_sha = _source(tmp_path)
    implementer_requests = []

    def implementer(request):
        implementer_requests.append(request)
        return {
            "summary": "Attempt an unapproved path.",
            "edits": [
                {
                    "path": "other.py",
                    "operation": "modify",
                    "replacements": [
                        {"old_text": "old", "new_text": "new"}
                    ],
                    "content": None,
                }
            ],
            "requested_test_profiles": ["python-check"],
            "assumptions": [],
        }

    state_root = tmp_path / "state"
    service = SafeAgentService.create(
        state_root,
        FakeModelProvider(handlers={"implementer": implementer}),
        allow_local_sources=True,
    )
    task = _task(source, base_sha, "safe-task-no-scope-repair")
    try:
        service.run(task)
        final = service.resume(task.thread_id, True)
        assert final["status"] == "blocked"
        assert "edit:validation_failed" in final["safe_errors"]
        report = service.artifacts.read_json(final["final_report_ref"])
        assert report["edit_repair_used"] is False
        assert len(implementer_requests) == 1
        sandbox = state_root / "sandboxes" / task.task_id / "repo"
        assert _git(sandbox, "status", "--porcelain") == ""
        assert _git(source, "status", "--porcelain") == ""
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
        assert _git(source, "status", "--porcelain") == ""
    finally:
        service.close()