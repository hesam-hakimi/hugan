from __future__ import annotations

import pytest
from pydantic import ValidationError

from universal_coding_agent.core.models import RepositorySpec
from universal_coding_agent.core.safe_models import (
    ApprovedChangeManifest,
    ChangeOperation,
    ChangeScopeEntry,
    PatchProposal,
    SafeModePolicy,
    SafeTaskRequest,
    TestProfile,
)


def _manifest() -> ApprovedChangeManifest:
    return ApprovedChangeManifest(
        base_sha="a" * 40,
        plan_hash="b" * 64,
        allowed_changes=(
            ChangeScopeEntry(
                path="src/app.py",
                operation=ChangeOperation.MODIFY,
                purpose="Implement the approved contract.",
            ),
        ),
        test_profiles=("python-check",),
        acceptance_criteria=("Focused tests pass.",),
    )


def _policy() -> SafeModePolicy:
    return SafeModePolicy(
        profiles=(
            TestProfile(
                profile_id="python-check",
                argv=("python", "-c", "print('ok')"),
            ),
        )
    )


def test_manifest_has_stable_hash_and_exact_paths() -> None:
    manifest = _manifest()
    assert len(manifest.canonical_hash()) == 64
    assert manifest.allowed_path_map() == {"src/app.py": ChangeOperation.MODIFY}


def test_manifest_rejects_traversal_and_denied_paths() -> None:
    with pytest.raises(ValidationError):
        ChangeScopeEntry(
            path="../escape.py",
            operation=ChangeOperation.CREATE,
            purpose="unsafe",
        )
    with pytest.raises(ValidationError):
        ApprovedChangeManifest(
            base_sha="a" * 40,
            plan_hash="b" * 64,
            allowed_changes=(
                ChangeScopeEntry(
                    path=".git/config",
                    operation=ChangeOperation.MODIFY,
                    purpose="unsafe",
                ),
            ),
            acceptance_criteria=("never",),
        )


def test_safe_task_requires_human_approval_and_known_profiles() -> None:
    task = SafeTaskRequest(
        task_id="safe-task-1",
        thread_id="safe-thread-1",
        title="Safe task",
        objective="Apply the approved bounded patch.",
        repository=RepositorySpec(url="https://example.test/repo.git", base_ref="main"),
        manifest=_manifest(),
        policy=_policy(),
    )
    assert task.require_scope_approval is True

    with pytest.raises(ValidationError):
        SafeTaskRequest(
            task_id="safe-task-2",
            thread_id="safe-thread-2",
            title="Safe task",
            objective="Apply the approved bounded patch.",
            repository=RepositorySpec(
                url="https://example.test/repo.git",
                base_ref="main",
            ),
            manifest=_manifest(),
            policy=SafeModePolicy(),
        )


def test_patch_proposal_requires_git_style_headers_and_exact_paths() -> None:
    with pytest.raises(ValidationError, match="git-style"):
        PatchProposal(
            summary="Malformed ordinary unified diff.",
            unified_diff=(
                "--- app.py\n"
                "+++ app.py\n"
                "@@ -1 +1 @@\n"
                "-RETURN_VALUE = 42\n"
                "+RETURN_VALUE = 43\n"
            ),
            changed_paths=("app.py",),
        )

    proposal = PatchProposal(
        summary="Valid git-style patch.",
        unified_diff=(
            "diff --git a/app.py b/app.py\n"
            "--- a/app.py\n"
            "+++ b/app.py\n"
            "@@ -1 +1 @@\n"
            "-RETURN_VALUE = 42\n"
            "+RETURN_VALUE = 43\n"
        ),
        changed_paths=("app.py",),
    )
    assert proposal.changed_paths == ("app.py",)

    with pytest.raises(ValidationError, match="changed_paths"):
        PatchProposal(
            summary="Mismatched path declaration.",
            unified_diff=proposal.unified_diff,
            changed_paths=("other.py",),
        )


def test_patch_proposal_ignores_marker_like_hunk_content() -> None:
    proposal = PatchProposal(
        summary="Valid diff whose hunk content resembles file markers.",
        unified_diff=(
            "diff --git a/contracts.txt b/contracts.txt\n"
            "--- a/contracts.txt\n"
            "+++ b/contracts.txt\n"
            "@@ -1,2 +1,2 @@\n"
            "--- old SQL-style comment\n"
            "+++ new SQL-style comment\n"
        ),
        changed_paths=("contracts.txt",),
    )
    assert proposal.changed_paths == ("contracts.txt",)
