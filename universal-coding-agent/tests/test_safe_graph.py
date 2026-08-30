from __future__ import annotations

import hashlib
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
        assert report["publish_approval_required"] is False
        assert report["publish_approved"] is None
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


def test_safe_graph_binds_publish_approval_to_exact_retained_patch(tmp_path: Path) -> None:
    source, base_sha = _source(tmp_path)
    state_root = tmp_path / "state"
    service = SafeAgentService.create(
        state_root,
        FakeModelProvider(),
        allow_local_sources=True,
    )
    task = _task(source, base_sha, "safe-task-publish-approved").model_copy(
        update={"require_publish_approval": True}
    )
    try:
        service.run(task)
        pending = service.resume(task.thread_id, True)
        assert pending["status"] == "reviewing"
        assert service.state(task.thread_id)["next"] == ["publish_approval"]

        validation = service.artifacts.read_json(pending["patch_validation_ref"])
        patch_sha256 = validation["patch_sha256"]
        final = service.resume_publish(
            task.thread_id,
            approved=True,
            patch_sha256=patch_sha256,
        )

        assert final["status"] == "completed"
        assert final["publish_approved"] is True
        assert final["publish_patch_sha256"] == patch_sha256
        report = service.artifacts.read_json(final["final_report_ref"])
        approval = service.artifacts.read_json(report["publish_approval_ref"])
        assert report["publish_approval_required"] is True
        assert report["publish_approved"] is True
        assert report["publish_patch_sha256"] == patch_sha256
        assert report["publish_approval_sha256"]
        assert approval["approved"] is True
        assert approval["binding_valid"] is True
        assert approval["schema_version"] == "2"
        assert approval["task_id"] == task.task_id
        assert approval["thread_id"] == task.thread_id
        assert approval["decision_received"] is True
        assert approval["repository"] == task.repository.model_dump(mode="json")
        assert approval["base_sha"] == base_sha
        assert approval["patch_sha256"] == patch_sha256
        assert approval["confirmed_patch_sha256"] == patch_sha256
        assert approval["source_control_side_effects"] is False
        approval_path = (
            state_root
            / "artifacts"
            / report["publish_approval_ref"].removeprefix("artifact://")
        )
        assert hashlib.sha256(approval_path.read_bytes()).hexdigest() == report[
            "publish_approval_sha256"
        ]
        assert report["stage_commit_push_pr_merge_deploy"] is False
        assert _git(source, "status", "--porcelain") == ""
    finally:
        service.close()


def test_safe_graph_records_exact_publish_rejection_without_source_control(
    tmp_path: Path,
) -> None:
    source, base_sha = _source(tmp_path)
    state_root = tmp_path / "state"
    service = SafeAgentService.create(
        state_root,
        FakeModelProvider(),
        allow_local_sources=True,
    )
    task = _task(source, base_sha, "safe-task-publish-rejected").model_copy(
        update={"require_publish_approval": True}
    )
    try:
        service.run(task)
        pending = service.resume(task.thread_id, True)
        validation = service.artifacts.read_json(pending["patch_validation_ref"])
        final = service.resume_publish(
            task.thread_id,
            approved=False,
            patch_sha256=validation["patch_sha256"],
        )

        assert final["status"] == "completed"
        assert final["publish_approved"] is False
        report = service.artifacts.read_json(final["final_report_ref"])
        approval = service.artifacts.read_json(report["publish_approval_ref"])
        assert approval["approved"] is False
        assert approval["binding_valid"] is True
        assert report["sandbox_patch_retained"] is True
        assert report["stage_commit_push_pr_merge_deploy"] is False
        assert _git(source, "status", "--porcelain") == ""
    finally:
        service.close()


def test_safe_graph_fails_closed_on_publish_patch_hash_mismatch(tmp_path: Path) -> None:
    source, base_sha = _source(tmp_path)
    state_root = tmp_path / "state"
    service = SafeAgentService.create(
        state_root,
        FakeModelProvider(),
        allow_local_sources=True,
    )
    task = _task(source, base_sha, "safe-task-publish-hash-mismatch").model_copy(
        update={"require_publish_approval": True}
    )
    try:
        service.run(task)
        service.resume(task.thread_id, True)
        final = service.resume_publish(
            task.thread_id,
            approved=True,
            patch_sha256="0" * 64,
        )

        assert final["status"] == "blocked"
        assert final["publish_approved"] is False
        assert final["rolled_back"] is True
        assert "publish_approval:binding_mismatch" in final["safe_errors"]
        report = service.artifacts.read_json(final["final_report_ref"])
        approval = service.artifacts.read_json(report["publish_approval_ref"])
        assert approval["approved"] is False
        assert approval["binding_valid"] is False
        assert report["sandbox_patch_retained"] is False
        assert _git(source, "status", "--porcelain") == ""
    finally:
        service.close()


def test_safe_graph_publish_approval_survives_service_restart(tmp_path: Path) -> None:
    source, base_sha = _source(tmp_path)
    state_root = tmp_path / "state"
    task = _task(source, base_sha, "safe-task-publish-restart").model_copy(
        update={"require_publish_approval": True}
    )
    first = SafeAgentService.create(
        state_root,
        FakeModelProvider(),
        allow_local_sources=True,
    )
    first.run(task)
    pending = first.resume(task.thread_id, True)
    patch_sha256 = first.artifacts.read_json(pending["patch_validation_ref"])[
        "patch_sha256"
    ]
    first.close()

    recovered = SafeAgentService.create(
        state_root,
        FakeModelProvider(),
        allow_local_sources=True,
    )
    try:
        assert recovered.state(task.thread_id)["next"] == ["publish_approval"]
        final = recovered.resume_publish(
            task.thread_id,
            approved=True,
            patch_sha256=patch_sha256,
        )
        assert final["status"] == "completed"
        assert final["publish_approved"] is True
        assert _git(source, "status", "--porcelain") == ""
    finally:
        recovered.close()


def test_safe_graph_fails_closed_when_materialized_patch_drifts_before_approval(
    tmp_path: Path,
) -> None:
    source, base_sha = _source(tmp_path)
    state_root = tmp_path / "state"
    service = SafeAgentService.create(
        state_root,
        FakeModelProvider(),
        allow_local_sources=True,
    )
    task = _task(source, base_sha, "safe-task-publish-worktree-drift").model_copy(
        update={"require_publish_approval": True}
    )
    try:
        service.run(task)
        pending = service.resume(task.thread_id, True)
        patch_sha256 = service.artifacts.read_json(pending["patch_validation_ref"])[
            "patch_sha256"
        ]
        sandbox = state_root / "sandboxes" / task.task_id / "repo"
        (sandbox / "app.py").write_text(
            "def answer():\n    return 44\n",
            encoding="utf-8",
        )

        final = service.resume_publish(
            task.thread_id,
            approved=True,
            patch_sha256=patch_sha256,
        )

        assert final["status"] == "blocked"
        assert final["publish_approved"] is False
        assert final["rolled_back"] is True
        assert "publish_approval:materialized_patch_drift" in final["safe_errors"]
        report = service.artifacts.read_json(final["final_report_ref"])
        approval = service.artifacts.read_json(report["publish_approval_ref"])
        assert approval["decision_received"] is False
        assert approval["binding_valid"] is False
        assert _git(sandbox, "status", "--porcelain") == ""
        assert _git(source, "status", "--porcelain") == ""
    finally:
        service.close()


def test_safe_graph_cancellation_precedes_pending_publish_approval(tmp_path: Path) -> None:
    source, base_sha = _source(tmp_path)
    state_root = tmp_path / "state"
    service = SafeAgentService.create(
        state_root,
        FakeModelProvider(),
        allow_local_sources=True,
    )
    task = _task(source, base_sha, "safe-task-publish-cancelled").model_copy(
        update={"require_publish_approval": True}
    )
    try:
        service.run(task)
        pending = service.resume(task.thread_id, True)
        patch_sha256 = service.artifacts.read_json(pending["patch_validation_ref"])[
            "patch_sha256"
        ]
        service.cancel(task.thread_id, reason="operator cancelled before publication")

        final = service.resume_publish(
            task.thread_id,
            approved=True,
            patch_sha256=patch_sha256,
        )

        assert final["status"] == "blocked"
        assert final.get("publish_approved") is None
        assert final["rolled_back"] is True
        assert "control:cancelled" in final["safe_errors"]
        report = service.artifacts.read_json(final["final_report_ref"])
        assert report["publish_approval_ref"] is None
        assert report["publish_approved"] is None
        assert _git(source, "status", "--porcelain") == ""
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
            assert (
                "exact replacement anchor in app.py must occur once; found 0"
                in request.user_prompt
            )
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
