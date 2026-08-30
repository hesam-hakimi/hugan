from __future__ import annotations

import hashlib
import subprocess
from dataclasses import dataclass, field, replace
from pathlib import Path

import pytest
from pydantic import ValidationError

from universal_coding_agent.core.models import RepositorySpec
from universal_coding_agent.core.safe_models import (
    ApprovedChangeManifest,
    ChangeOperation,
    ChangeScopeEntry,
    FileEdit,
    StructuredEditProposal,
    TextReplacement,
)
from universal_coding_agent.safe.patching import SafePatchEngine
from universal_coding_agent.source_control import (
    DraftPullRequestRequest,
    DraftPullRequestResult,
    ExactPublicationRequest,
    GitSourceControlAdapter,
    PublicationAction,
    PublicationPartialEffects,
    SourceControlAdapter,
    SourceControlPublicationError,
    load_source_control_adapter,
    publication_intent_sha256,
)


def _git(cwd: Path, *arguments: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )
    if check and result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)
    return result.stdout.strip()


@dataclass(frozen=True)
class _Fixture:
    remote: Path
    sandbox: Path
    sandboxes_root: Path
    base_sha: str
    repository: RepositorySpec
    manifest: ApprovedChangeManifest
    edit_proposal: StructuredEditProposal
    patch_text: str
    patch_sha256: str


def _fixture(tmp_path: Path) -> _Fixture:
    remote = tmp_path / "remote.git"
    remote.mkdir()
    _git(remote, "init", "--bare")

    seed = tmp_path / "seed"
    seed.mkdir()
    _git(seed, "init", "-b", "main")
    _git(seed, "config", "user.name", "Test")
    _git(seed, "config", "user.email", "test@example.test")
    (seed / "app.py").write_text("def answer():\n    return 42\n", encoding="utf-8")
    _git(seed, "add", "app.py")
    _git(seed, "commit", "-m", "fixture")
    base_sha = _git(seed, "rev-parse", "HEAD")
    _git(seed, "remote", "add", "origin", str(remote))
    _git(seed, "push", "origin", "main")
    _git(remote, "symbolic-ref", "HEAD", "refs/heads/main")

    sandboxes_root = tmp_path / "state" / "sandboxes"
    sandbox = sandboxes_root / "task-123" / "repo"
    sandbox.parent.mkdir(parents=True)
    _git(sandbox.parent, "clone", str(remote), str(sandbox))
    _git(sandbox, "checkout", "--detach", base_sha)
    (sandbox / "app.py").write_text("def answer():\n    return 43\n", encoding="utf-8")

    manifest = ApprovedChangeManifest(
        base_sha=base_sha,
        plan_hash="b" * 64,
        allowed_changes=(
            ChangeScopeEntry(
                path="app.py",
                operation=ChangeOperation.MODIFY,
                purpose="Apply the exact approved answer change.",
            ),
        ),
        acceptance_criteria=("The answer is 43.",),
        max_changed_files=1,
    )
    edit_proposal = StructuredEditProposal(
        summary="Change the answer.",
        edits=(
            FileEdit(
                path="app.py",
                operation=ChangeOperation.MODIFY,
                replacements=(TextReplacement(old_text="return 42", new_text="return 43"),),
            ),
        ),
    )
    patch = (
        SafePatchEngine()
        .capture_worktree_proposal(
            sandbox,
            manifest,
            edit_proposal,
        )
        .unified_diff
    )
    return _Fixture(
        remote=remote,
        sandbox=sandbox,
        sandboxes_root=sandboxes_root,
        base_sha=base_sha,
        repository=RepositorySpec(url=str(remote), base_ref="main"),
        manifest=manifest,
        edit_proposal=edit_proposal,
        patch_text=patch,
        patch_sha256=hashlib.sha256(patch.encode("utf-8")).hexdigest(),
    )


def _request(
    fixture: _Fixture,
    *,
    action: PublicationAction = PublicationAction.COMMIT,
    head_branch: str = "uca/task-123",
) -> ExactPublicationRequest:
    approval_sha256 = "a" * 64
    title = "Exact approved change" if action is PublicationAction.DRAFT_PR else ""
    body = "Publishes only the exact approved patch." if title else ""
    intent_sha256 = publication_intent_sha256(
        approval_sha256=approval_sha256,
        patch_sha256=fixture.patch_sha256,
        repository=fixture.repository,
        manifest=fixture.manifest,
        changed_paths=fixture.edit_proposal.changed_paths,
        head_branch=head_branch,
        action=action,
        commit_message="UCA: exact approved change",
        draft_pr_title=title,
        draft_pr_body=body,
        adapter_identity="git-source-control-v1",
        draft_pr_identity=("fixture-draft" if action is PublicationAction.DRAFT_PR else ""),
    )
    publication_id = hashlib.sha256(
        f"{approval_sha256}:{intent_sha256}".encode("ascii")
    ).hexdigest()
    return ExactPublicationRequest(
        publication_id=publication_id,
        approval_ref="artifact://tasks/task-123/publish-approval.json",
        approval_sha256=approval_sha256,
        patch_ref="artifact://tasks/task-123/proposed.patch",
        patch_sha256=fixture.patch_sha256,
        intent_sha256=intent_sha256,
        task_id="task-123",
        thread_id="thread-123",
        repository=fixture.repository,
        sandbox_path=str(fixture.sandbox),
        sandboxes_root=str(fixture.sandboxes_root),
        manifest=fixture.manifest,
        edit_proposal=fixture.edit_proposal,
        patch_text=fixture.patch_text,
        changed_paths=fixture.edit_proposal.changed_paths,
        head_branch=head_branch,
        action=action,
        adapter_identity="git-source-control-v1",
        draft_pr_identity=("fixture-draft" if action is PublicationAction.DRAFT_PR else ""),
        commit_message="UCA: exact approved change",
        draft_pr_title=title,
        draft_pr_body=body,
    )


def _remote_ref(remote: Path, branch: str) -> str:
    return _git(remote, "rev-parse", "--verify", f"refs/heads/{branch}", check=False)


def test_git_adapter_commits_only_the_exact_patch_to_a_local_feature_ref(
    tmp_path: Path,
) -> None:
    fixture = _fixture(tmp_path)
    request = _request(fixture)
    adapter = GitSourceControlAdapter(allow_local_repositories=True)

    assert isinstance(adapter, SourceControlAdapter)
    result = adapter.publish_exact(request)

    assert result.action is PublicationAction.COMMIT
    assert result.commit_created is True
    assert result.local_ref_created is True
    assert result.pushed is False
    assert result.local_ref == "refs/heads/uca/task-123"
    assert _git(fixture.sandbox, "rev-parse", result.local_ref) == result.commit_sha
    assert (
        _git(fixture.sandbox, "rev-list", "--parents", "-n", "1", result.commit_sha)
        == f"{result.commit_sha} {fixture.base_sha}"
    )
    committed_patch = _git(
        fixture.sandbox,
        "diff",
        "--no-ext-diff",
        "--no-color",
        "--full-index",
        fixture.base_sha,
        result.commit_sha,
        "--",
        "app.py",
    )
    assert committed_patch + "\n" == fixture.patch_text
    assert _git(fixture.sandbox, "rev-parse", "HEAD") == fixture.base_sha
    assert _git(fixture.sandbox, "diff", "--cached", "--name-only") == ""
    assert _git(fixture.sandbox, "status", "--porcelain") == "M app.py"
    assert _remote_ref(fixture.remote, "uca/task-123") == ""

    repeated = adapter.publish_exact(request)
    assert repeated.commit_sha == result.commit_sha
    assert repeated.commit_created is False
    assert repeated.local_ref_created is False
    assert repeated.reused is True


def test_git_adapter_pushes_new_feature_branch_without_updating_base(
    tmp_path: Path,
) -> None:
    fixture = _fixture(tmp_path)
    request = _request(fixture, action=PublicationAction.PUSH)

    class _RecordingAdapter(GitSourceControlAdapter):
        push_arguments: list[str] | None = None

        def _run(self, root: Path, arguments: list[str], **kwargs):
            if arguments[:1] == ["push"]:
                self.push_arguments = list(arguments)
            return super()._run(root, arguments, **kwargs)

    adapter = _RecordingAdapter(allow_local_repositories=True)

    result = adapter.publish_exact(request)

    assert result.pushed is True
    assert result.push_performed is True
    assert result.remote_before_sha == ""
    assert result.remote_after_sha == result.commit_sha
    assert adapter.push_arguments is not None
    assert (
        "--force-with-lease=refs/heads/uca/task-123:"
        in adapter.push_arguments
    )
    assert f"{result.commit_sha}:refs/heads/uca/task-123" in adapter.push_arguments
    assert not any(argument.startswith("+") for argument in adapter.push_arguments)
    assert _remote_ref(fixture.remote, "uca/task-123") == result.commit_sha
    assert _remote_ref(fixture.remote, "main") == fixture.base_sha

    repeated = adapter.publish_exact(request)
    assert repeated.commit_sha == result.commit_sha
    assert repeated.remote_before_sha == result.commit_sha
    assert repeated.remote_after_sha == result.commit_sha
    assert repeated.commit_created is False
    assert repeated.local_ref_created is False
    assert repeated.push_performed is False
    assert repeated.reused is True


def test_git_adapter_rejects_feature_ref_parked_at_approved_base(
    tmp_path: Path,
) -> None:
    fixture = _fixture(tmp_path)
    _git(
        fixture.remote,
        "update-ref",
        "refs/heads/uca/task-123",
        fixture.base_sha,
    )

    with pytest.raises(SourceControlPublicationError) as captured:
        GitSourceControlAdapter(allow_local_repositories=True).publish_exact(
            _request(fixture, action=PublicationAction.PUSH)
        )

    assert captured.value.code == "remote_ref_diverged"
    assert captured.value.stage == "sandbox_preflight"
    assert captured.value.partial_effects.push_attempted is False
    assert _remote_ref(fixture.remote, "uca/task-123") == fixture.base_sha
    assert _remote_ref(fixture.remote, "main") == fixture.base_sha


def test_git_adapter_failure_after_staging_never_dirties_real_index(
    tmp_path: Path,
) -> None:
    fixture = _fixture(tmp_path)

    class _FailAtWriteTreeAdapter(GitSourceControlAdapter):
        def _run(self, root: Path, arguments: list[str], **kwargs):
            if arguments == ["write-tree"]:
                raise RuntimeError("simulated process loss after temporary staging")
            return super()._run(root, arguments, **kwargs)

    adapter = _FailAtWriteTreeAdapter(allow_local_repositories=True)
    with pytest.raises(SourceControlPublicationError) as captured:
        adapter.publish_exact(_request(fixture))

    assert captured.value.code == "adapter_operation_failed"
    assert captured.value.stage == "commit"
    assert _git(fixture.sandbox, "diff", "--cached", "--name-only") == ""
    assert _git(fixture.sandbox, "status", "--porcelain") == "M app.py"


def test_git_adapter_blocks_a_divergent_remote_feature_ref_without_force(
    tmp_path: Path,
) -> None:
    fixture = _fixture(tmp_path)
    competitor = tmp_path / "competitor"
    _git(tmp_path, "clone", str(fixture.remote), str(competitor))
    _git(competitor, "config", "user.name", "Competing User")
    _git(competitor, "config", "user.email", "competing@example.test")
    _git(competitor, "switch", "-c", "uca/task-123")
    (competitor / "other.txt").write_text("competing\n", encoding="utf-8")
    _git(competitor, "add", "other.txt")
    _git(competitor, "commit", "-m", "competing change")
    competing_sha = _git(competitor, "rev-parse", "HEAD")
    _git(competitor, "push", "origin", "uca/task-123")

    adapter = GitSourceControlAdapter(allow_local_repositories=True)
    with pytest.raises(SourceControlPublicationError) as captured:
        adapter.publish_exact(_request(fixture, action=PublicationAction.PUSH))

    assert captured.value.code == "remote_ref_diverged"
    assert captured.value.stage == "sandbox_preflight"
    assert captured.value.partial_effects.push_attempted is False
    assert _remote_ref(fixture.remote, "uca/task-123") == competing_sha
    assert _remote_ref(fixture.remote, "main") == fixture.base_sha


def test_git_adapter_never_overwrites_a_racing_remote_feature_update(
    tmp_path: Path,
) -> None:
    fixture = _fixture(tmp_path)
    competitor = tmp_path / "racing-competitor"
    _git(tmp_path, "clone", str(fixture.remote), str(competitor))
    _git(competitor, "config", "user.name", "Racing User")
    _git(competitor, "config", "user.email", "racing@example.test")
    _git(competitor, "switch", "-c", "uca/task-123")
    (competitor / "racing.txt").write_text("racing\n", encoding="utf-8")
    _git(competitor, "add", "racing.txt")
    _git(competitor, "commit", "-m", "racing change")
    racing_sha = _git(competitor, "rev-parse", "HEAD")

    class _RacingAdapter(GitSourceControlAdapter):
        raced = False

        def _run(self, root: Path, arguments: list[str], **kwargs):
            if arguments[:1] == ["push"] and not self.raced:
                self.raced = True
                _git(competitor, "push", "origin", "uca/task-123")
            return super()._run(root, arguments, **kwargs)

    with pytest.raises(SourceControlPublicationError) as captured:
        _RacingAdapter(allow_local_repositories=True).publish_exact(
            _request(fixture, action=PublicationAction.PUSH)
        )

    assert captured.value.code == "adapter_operation_failed"
    assert captured.value.stage == "push"
    assert captured.value.partial_effects.push_attempted is True
    assert _remote_ref(fixture.remote, "uca/task-123") == racing_sha
    assert _remote_ref(fixture.remote, "main") == fixture.base_sha


def test_git_adapter_rejects_symbolic_local_feature_ref_without_touching_base(
    tmp_path: Path,
) -> None:
    fixture = _fixture(tmp_path)
    _git(
        fixture.sandbox,
        "symbolic-ref",
        "refs/heads/uca/task-123",
        "refs/heads/main",
    )

    with pytest.raises(SourceControlPublicationError) as captured:
        GitSourceControlAdapter(allow_local_repositories=True).publish_exact(
            _request(fixture)
        )

    assert captured.value.code == "symbolic_head_branch_forbidden"
    assert _git(fixture.sandbox, "rev-parse", "refs/heads/main") == fixture.base_sha


def test_local_ref_cas_does_not_dereference_a_racing_symbolic_ref(
    tmp_path: Path,
) -> None:
    fixture = _fixture(tmp_path)

    class _RacingSymbolicLocalRefAdapter(GitSourceControlAdapter):
        raced = False

        def _run(self, root: Path, arguments: list[str], **kwargs):
            if arguments[:2] == ["update-ref", "--no-deref"] and not self.raced:
                self.raced = True
                _git(
                    fixture.sandbox,
                    "symbolic-ref",
                    "refs/heads/uca/task-123",
                    "refs/heads/main",
                )
            return super()._run(root, arguments, **kwargs)

    with pytest.raises(SourceControlPublicationError) as captured:
        _RacingSymbolicLocalRefAdapter(allow_local_repositories=True).publish_exact(
            _request(fixture)
        )

    assert captured.value.code == "adapter_operation_failed"
    assert captured.value.stage == "commit"
    assert _git(fixture.sandbox, "rev-parse", "refs/heads/main") == fixture.base_sha


def test_local_ref_reuse_requires_a_direct_ref_under_race(
    tmp_path: Path,
) -> None:
    fixture = _fixture(tmp_path)
    request = _request(fixture)
    exact = GitSourceControlAdapter(allow_local_repositories=True).publish_exact(request)
    _git(
        fixture.sandbox,
        "update-ref",
        "refs/heads/exact-target",
        exact.commit_sha,
    )

    class _RacingReuseAdapter(GitSourceControlAdapter):
        raced = False

        def _run(self, root: Path, arguments: list[str], **kwargs):
            if (
                arguments[:2] == ["update-ref", "--no-deref"]
                and arguments[-2:] == [exact.commit_sha, exact.commit_sha]
                and not self.raced
            ):
                self.raced = True
                _git(
                    fixture.sandbox,
                    "symbolic-ref",
                    "refs/heads/uca/task-123",
                    "refs/heads/exact-target",
                )
            return super()._run(root, arguments, **kwargs)

    result = _RacingReuseAdapter(allow_local_repositories=True).publish_exact(request)

    assert result.commit_sha == exact.commit_sha
    assert result.reused is True
    assert (
        _git(
            fixture.sandbox,
            "symbolic-ref",
            "-q",
            "refs/heads/uca/task-123",
            check=False,
        )
        == ""
    )
    assert _git(fixture.sandbox, "rev-parse", "refs/heads/main") == fixture.base_sha
    assert _git(fixture.sandbox, "rev-parse", "refs/heads/exact-target") == exact.commit_sha


def test_git_adapter_rejects_symbolic_remote_feature_ref_without_touching_base(
    tmp_path: Path,
) -> None:
    fixture = _fixture(tmp_path)
    _git(
        fixture.remote,
        "symbolic-ref",
        "refs/heads/uca/task-123",
        "refs/heads/main",
    )

    with pytest.raises(SourceControlPublicationError):
        GitSourceControlAdapter(allow_local_repositories=True).publish_exact(
            _request(fixture, action=PublicationAction.PUSH)
        )

    assert _remote_ref(fixture.remote, "main") == fixture.base_sha


def test_remote_creation_lease_rejects_a_racing_symbolic_ref(
    tmp_path: Path,
) -> None:
    fixture = _fixture(tmp_path)

    class _RacingSymbolicRemoteRefAdapter(GitSourceControlAdapter):
        raced = False

        def _run(self, root: Path, arguments: list[str], **kwargs):
            if arguments[:1] == ["push"] and not self.raced:
                self.raced = True
                _git(
                    fixture.remote,
                    "symbolic-ref",
                    "refs/heads/uca/task-123",
                    "refs/heads/main",
                )
            return super()._run(root, arguments, **kwargs)

    with pytest.raises(SourceControlPublicationError) as captured:
        _RacingSymbolicRemoteRefAdapter(allow_local_repositories=True).publish_exact(
            _request(fixture, action=PublicationAction.PUSH)
        )

    assert captured.value.code == "adapter_operation_failed"
    assert captured.value.stage == "push"
    assert captured.value.partial_effects.push_attempted is True
    assert _remote_ref(fixture.remote, "main") == fixture.base_sha


def test_git_adapter_rejects_local_url_rewrite_configuration(
    tmp_path: Path,
) -> None:
    fixture = _fixture(tmp_path)
    alternate = tmp_path / "alternate.git"
    alternate.mkdir()
    _git(alternate, "init", "--bare")
    _git(
        fixture.sandbox,
        "config",
        f"url.{alternate}.insteadOf",
        str(fixture.remote),
    )

    with pytest.raises(SourceControlPublicationError) as captured:
        GitSourceControlAdapter(allow_local_repositories=True).publish_exact(
            _request(fixture, action=PublicationAction.PUSH)
        )

    assert captured.value.code == "sandbox_git_config_unsafe"
    assert _remote_ref(fixture.remote, "uca/task-123") == ""
    assert _remote_ref(alternate, "uca/task-123") == ""


def test_network_client_ignores_url_rewrite_added_after_preflight(
    tmp_path: Path,
) -> None:
    fixture = _fixture(tmp_path)
    alternate = tmp_path / "alternate.git"
    alternate.mkdir()
    _git(alternate, "init", "--bare")

    class _ConfigRaceAdapter(GitSourceControlAdapter):
        injected = False

        def _run(self, root: Path, arguments: list[str], **kwargs):
            result = super()._run(root, arguments, **kwargs)
            if arguments[:2] == ["config", "--file"] and not self.injected:
                self.injected = True
                _git(
                    fixture.sandbox,
                    "config",
                    f"url.{alternate}.insteadOf",
                    str(fixture.remote),
                )
            return result

    result = _ConfigRaceAdapter(allow_local_repositories=True).publish_exact(
        _request(fixture, action=PublicationAction.PUSH)
    )

    assert result.pushed is True
    assert _remote_ref(fixture.remote, "uca/task-123") == result.commit_sha
    assert _remote_ref(alternate, "uca/task-123") == ""


def test_git_adapter_rejects_non_origin_remote_configuration(
    tmp_path: Path,
) -> None:
    fixture = _fixture(tmp_path)
    _git(fixture.sandbox, "config", "remote.alias.url", str(fixture.remote))

    with pytest.raises(SourceControlPublicationError) as captured:
        GitSourceControlAdapter(allow_local_repositories=True).publish_exact(
            _request(fixture, action=PublicationAction.PUSH)
        )

    assert captured.value.code == "sandbox_git_config_unsafe"
    assert _remote_ref(fixture.remote, "uca/task-123") == ""


def test_git_adapter_rejects_common_git_directory_override(
    tmp_path: Path,
) -> None:
    fixture = _fixture(tmp_path)
    (fixture.sandbox / ".git" / "commondir").write_text(".\n", encoding="ascii")

    with pytest.raises(SourceControlPublicationError) as captured:
        GitSourceControlAdapter(allow_local_repositories=True).publish_exact(
            _request(fixture)
        )

    assert captured.value.code == "sandbox_git_metadata_unsafe"
    assert captured.value.partial_effects.commit_created is False


def test_git_adapter_rejects_symlinked_feature_ref_parent(
    tmp_path: Path,
) -> None:
    fixture = _fixture(tmp_path)
    external = tmp_path / "external-refs"
    external.mkdir()
    (fixture.sandbox / ".git" / "refs" / "heads" / "uca").symlink_to(
        external,
        target_is_directory=True,
    )

    with pytest.raises(SourceControlPublicationError) as captured:
        GitSourceControlAdapter(allow_local_repositories=True).publish_exact(
            _request(fixture)
        )

    assert captured.value.code == "sandbox_git_metadata_unsafe"
    assert list(external.iterdir()) == []
    assert _git(fixture.sandbox, "rev-parse", "HEAD") == fixture.base_sha


def test_git_adapter_rejects_symlinked_loose_object_directory(
    tmp_path: Path,
) -> None:
    fixture = _fixture(tmp_path)
    objects = fixture.sandbox / ".git" / "objects"
    fanout = next(
        objects / f"{value:02x}"
        for value in range(256)
        if not (objects / f"{value:02x}").exists()
    )
    external = tmp_path / "external-objects"
    external.mkdir()
    fanout.symlink_to(external, target_is_directory=True)

    with pytest.raises(SourceControlPublicationError) as captured:
        GitSourceControlAdapter(allow_local_repositories=True).publish_exact(
            _request(fixture)
        )

    assert captured.value.code == "sandbox_git_metadata_unsafe"
    assert list(external.iterdir()) == []
    assert _git(fixture.sandbox, "rev-parse", "HEAD") == fixture.base_sha


def test_private_git_dir_ignores_common_directory_added_during_ref_update(
    tmp_path: Path,
) -> None:
    fixture = _fixture(tmp_path)
    external = tmp_path / "external.git"
    _git(tmp_path, "clone", "--bare", str(fixture.remote), str(external))

    class _CommonDirectoryRaceAdapter(GitSourceControlAdapter):
        injected = False

        def _run(self, root: Path, arguments: list[str], **kwargs):
            if arguments[:2] == ["update-ref", "--no-deref"] and not self.injected:
                self.injected = True
                (fixture.sandbox / ".git" / "commondir").write_text(
                    str(external) + "\n",
                    encoding="utf-8",
                )
            return super()._run(root, arguments, **kwargs)

    with pytest.raises(SourceControlPublicationError) as captured:
        _CommonDirectoryRaceAdapter(allow_local_repositories=True).publish_exact(
            _request(fixture)
        )

    assert captured.value.code == "adapter_operation_failed"
    assert captured.value.stage == "commit"
    assert captured.value.partial_effects.commit_created is True
    assert _remote_ref(external, "uca/task-123") == ""
    assert not (
        fixture.sandbox / ".git" / "refs" / "heads" / "uca" / "task-123"
    ).exists()


def test_git_adapter_rejects_replacement_refs_before_commit_reuse(
    tmp_path: Path,
) -> None:
    fixture = _fixture(tmp_path)
    request = _request(fixture)
    exact = GitSourceControlAdapter(allow_local_repositories=True).publish_exact(request)
    tree_sha = _git(fixture.sandbox, "rev-parse", f"{exact.commit_sha}^{{tree}}")
    unapproved_sha = _git(
        fixture.sandbox,
        "-c",
        "user.name=Unapproved",
        "-c",
        "user.email=unapproved@example.test",
        "commit-tree",
        tree_sha,
        "-p",
        fixture.base_sha,
        "-m",
        "not the approved message",
    )
    _git(fixture.sandbox, "replace", unapproved_sha, exact.commit_sha)
    _git(
        fixture.sandbox,
        "update-ref",
        "refs/heads/uca/task-123",
        unapproved_sha,
        exact.commit_sha,
    )

    with pytest.raises(SourceControlPublicationError) as captured:
        GitSourceControlAdapter(allow_local_repositories=True).publish_exact(request)

    assert captured.value.code == "sandbox_git_history_override_forbidden"
    assert captured.value.partial_effects.commit_created is False
    assert _remote_ref(fixture.remote, "uca/task-123") == ""


@pytest.mark.parametrize("metadata_name", ["info/grafts", "shallow"])
def test_git_adapter_rejects_legacy_history_override_metadata(
    tmp_path: Path,
    metadata_name: str,
) -> None:
    fixture = _fixture(tmp_path)
    metadata_path = fixture.sandbox / ".git" / metadata_name
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(f"{fixture.base_sha}\n", encoding="ascii")

    with pytest.raises(SourceControlPublicationError) as captured:
        GitSourceControlAdapter(allow_local_repositories=True).publish_exact(
            _request(fixture)
        )

    assert captured.value.code == "sandbox_git_history_override_forbidden"
    assert captured.value.partial_effects.commit_created is False


def test_base_ref_drift_during_push_is_detected_without_restoring_base(
    tmp_path: Path,
) -> None:
    fixture = _fixture(tmp_path)

    class _DeleteBaseBeforePushAdapter(GitSourceControlAdapter):
        def _run(self, root: Path, arguments: list[str], **kwargs):
            if arguments[:1] == ["push"]:
                _git(fixture.remote, "update-ref", "-d", "refs/heads/main")
            return super()._run(root, arguments, **kwargs)

    with pytest.raises(SourceControlPublicationError) as captured:
        _DeleteBaseBeforePushAdapter(allow_local_repositories=True).publish_exact(
            _request(fixture, action=PublicationAction.PUSH)
        )

    assert captured.value.code == "remote_base_ref_drift"
    assert captured.value.partial_effects.push_attempted is True
    assert _remote_ref(fixture.remote, "main") == ""


@pytest.mark.parametrize(
    "branch",
    ["main", "-unsafe", "feature//unsafe", "feature.lock", "uca.lock/feature"],
)
def test_publication_request_rejects_base_or_invalid_head_branch(
    tmp_path: Path,
    branch: str,
) -> None:
    fixture = _fixture(tmp_path)

    with pytest.raises((ValidationError, ValueError)):
        _request(fixture, head_branch=branch)


def test_publication_request_rejects_pseudo_base_alias_for_real_base_branch(
    tmp_path: Path,
) -> None:
    fixture = _fixture(tmp_path)
    aliased = replace(
        fixture,
        repository=RepositorySpec(url=str(fixture.remote), base_ref="HEAD"),
    )

    with pytest.raises((ValidationError, ValueError), match="pseudo-ref"):
        _request(aliased, action=PublicationAction.PUSH, head_branch="main")


def test_git_adapter_rejects_relative_local_repository_before_any_effect(
    tmp_path: Path,
    monkeypatch,
) -> None:
    fixture = _fixture(tmp_path)
    monkeypatch.chdir(tmp_path)
    relative = replace(
        fixture,
        repository=RepositorySpec(url="remote.git", base_ref="main"),
    )
    request = _request(relative)
    adapter = GitSourceControlAdapter(allow_local_repositories=True)

    with pytest.raises(SourceControlPublicationError) as captured:
        adapter.publish_exact(request)

    assert captured.value.code == "local_repository_not_absolute"
    assert captured.value.partial_effects.commit_created is False


def test_existing_feature_ref_at_base_is_updated_not_reported_as_created(
    tmp_path: Path,
) -> None:
    fixture = _fixture(tmp_path)
    _git(
        fixture.sandbox,
        "update-ref",
        "refs/heads/uca/task-123",
        fixture.base_sha,
    )

    result = GitSourceControlAdapter(allow_local_repositories=True).publish_exact(
        _request(fixture)
    )

    assert result.local_ref_created is False
    assert result.local_ref_updated is True
    assert _git(fixture.sandbox, "rev-parse", result.local_ref) == result.commit_sha


def test_git_adapter_blocks_worktree_or_index_drift_before_commit(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    request = _request(fixture)
    adapter = GitSourceControlAdapter(allow_local_repositories=True)
    (fixture.sandbox / "app.py").write_text(
        "def answer():\n    return 44\n",
        encoding="utf-8",
    )

    with pytest.raises(SourceControlPublicationError) as worktree_error:
        adapter.publish_exact(request)

    assert worktree_error.value.code == "materialized_patch_mismatch"
    assert (
        _git(
            fixture.sandbox,
            "show-ref",
            "--verify",
            "refs/heads/uca/task-123",
            check=False,
        )
        == ""
    )

    (fixture.sandbox / "app.py").write_text(
        "def answer():\n    return 43\n",
        encoding="utf-8",
    )
    _git(fixture.sandbox, "add", "app.py")
    with pytest.raises(SourceControlPublicationError) as index_error:
        adapter.publish_exact(request)

    assert index_error.value.code == "sandbox_index_not_clean"


class _InterruptAfterTemporaryStagingAdapter(GitSourceControlAdapter):
    def _run(self, root: Path, arguments: list[str], **kwargs):
        result = super()._run(root, arguments, **kwargs)
        if arguments == ["write-tree"]:
            raise KeyboardInterrupt
        return result


def test_interruption_after_staging_never_mutates_the_sandbox_index(
    tmp_path: Path,
) -> None:
    fixture = _fixture(tmp_path)
    request = _request(fixture)
    interrupted = _InterruptAfterTemporaryStagingAdapter(allow_local_repositories=True)

    with pytest.raises(KeyboardInterrupt):
        interrupted.publish_exact(request)

    assert _git(fixture.sandbox, "diff", "--cached", "--name-only") == ""
    assert _git(fixture.sandbox, "status", "--porcelain") == "M app.py"

    recovered = GitSourceControlAdapter(allow_local_repositories=True)
    result = recovered.publish_exact(request)
    assert result.commit_sha == _git(
        fixture.sandbox,
        "rev-parse",
        "refs/heads/uca/task-123",
    )


def test_failure_after_local_ref_update_reports_known_partial_effects(
    tmp_path: Path,
) -> None:
    fixture = _fixture(tmp_path)

    class _DirtyIndexAfterRefAdapter(GitSourceControlAdapter):
        def _run(self, root: Path, arguments: list[str], **kwargs):
            result = super()._run(root, arguments, **kwargs)
            if arguments[:1] == ["update-ref"]:
                _git(root, "add", "app.py")
            return result

    with pytest.raises(SourceControlPublicationError) as captured:
        _DirtyIndexAfterRefAdapter(allow_local_repositories=True).publish_exact(
            _request(fixture)
        )

    assert captured.value.code == "sandbox_index_not_clean"
    assert captured.value.stage == "commit"
    assert captured.value.partial_effects.commit_created is True
    assert captured.value.partial_effects.local_ref_created is True
    assert captured.value.partial_effects.local_ref == "refs/heads/uca/task-123"


@dataclass
class _DraftCreator:
    requests: list[DraftPullRequestRequest] = field(default_factory=list)

    def ensure_draft(self, request: DraftPullRequestRequest) -> DraftPullRequestResult:
        self.requests.append(request)
        return DraftPullRequestResult(
            provider="fixture",
            pull_request_id="17",
            url="https://example.test/pull/17",
            base_branch=request.base_branch,
            head_branch=request.head_branch,
            head_sha=request.head_sha,
            created=True,
        )


@dataclass
class _MismatchedDraftCreator:
    def ensure_draft(self, request: DraftPullRequestRequest) -> DraftPullRequestResult:
        return DraftPullRequestResult(
            provider="fixture",
            pull_request_id="18",
            url="https://example.test/pull/18",
            base_branch=request.base_branch,
            head_branch="uca/wrong-head",
            head_sha=request.head_sha,
            created=True,
        )


def test_git_adapter_creates_only_an_exact_optional_draft_pr(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    creator = _DraftCreator()
    adapter = GitSourceControlAdapter(
        allow_local_repositories=True,
        draft_pr_creator=creator,
        draft_pr_identity="fixture-draft",
    )

    result = adapter.publish_exact(_request(fixture, action=PublicationAction.DRAFT_PR))

    assert result.pushed is True
    assert result.draft_pr is not None
    assert result.draft_pr.draft is True
    assert result.draft_pr.head_sha == result.commit_sha
    assert len(creator.requests) == 1
    assert creator.requests[0].base_branch == "main"
    assert creator.requests[0].head_branch == "uca/task-123"


@pytest.mark.parametrize("action", [PublicationAction.COMMIT, PublicationAction.PUSH])
def test_draft_capable_adapter_can_execute_non_draft_actions(
    tmp_path: Path,
    action: PublicationAction,
) -> None:
    fixture = _fixture(tmp_path)
    creator = _DraftCreator()
    adapter = GitSourceControlAdapter(
        allow_local_repositories=True,
        draft_pr_creator=creator,
        draft_pr_identity="fixture-draft",
    )

    result = adapter.publish_exact(_request(fixture, action=action))

    assert result.action is action
    assert result.draft_pr is None
    assert creator.requests == []


def test_draft_pr_binding_failure_preserves_known_partial_effects(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    adapter = GitSourceControlAdapter(
        allow_local_repositories=True,
        draft_pr_creator=_MismatchedDraftCreator(),
        draft_pr_identity="fixture-draft",
    )

    with pytest.raises(SourceControlPublicationError) as captured:
        adapter.publish_exact(_request(fixture, action=PublicationAction.DRAFT_PR))

    assert captured.value.code == "draft_pr_result_mismatch"
    assert captured.value.partial_effects.push_verified is True
    assert captured.value.partial_effects.draft_pr_created is True
    assert captured.value.partial_effects.draft_pr_url == "https://example.test/pull/18"


def test_draft_pr_creation_is_not_reported_as_a_fully_reused_action(
    tmp_path: Path,
) -> None:
    fixture = _fixture(tmp_path)
    GitSourceControlAdapter(allow_local_repositories=True).publish_exact(
        _request(fixture, action=PublicationAction.PUSH)
    )
    adapter = GitSourceControlAdapter(
        allow_local_repositories=True,
        draft_pr_creator=_DraftCreator(),
        draft_pr_identity="fixture-draft",
    )

    result = adapter.publish_exact(_request(fixture, action=PublicationAction.DRAFT_PR))

    assert result.commit_created is False
    assert result.push_performed is False
    assert result.draft_pr is not None and result.draft_pr.created is True
    assert result.reused is False


@pytest.mark.parametrize(
    "url",
    [
        "https://token@example.test/pull/1",
        "https://example.test/pull/1?token=secret",
        "http://example.test/pull/1",
    ],
)
def test_draft_pr_result_rejects_credential_bearing_or_non_https_url(url: str) -> None:
    with pytest.raises(ValidationError):
        DraftPullRequestResult(
            provider="fixture",
            pull_request_id="19",
            url=url,
            base_branch="main",
            head_branch="uca/task-123",
            head_sha="a" * 40,
            created=True,
        )


def test_partial_effects_reject_credential_bearing_draft_pr_url() -> None:
    with pytest.raises(ValidationError):
        PublicationPartialEffects(
            draft_pr_attempted=True,
            draft_pr_url="https://token@example.test/pull/20",
        )


@pytest.mark.parametrize(
    "effects",
    [
        {"commit_created": True},
        {"local_ref_attempted": True},
        {"local_ref_verified": True},
        {"local_ref_created": True, "local_ref_updated": True},
        {"push_verified": True},
        {"remote_sha": "a" * 40},
        {"draft_pr_created": True},
    ],
)
def test_partial_effects_reject_contradictory_state(effects: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        PublicationPartialEffects.model_validate(effects)


def test_draft_pr_without_creator_blocks_before_any_source_control_effect(
    tmp_path: Path,
) -> None:
    fixture = _fixture(tmp_path)
    adapter = GitSourceControlAdapter(allow_local_repositories=True)

    with pytest.raises(SourceControlPublicationError) as captured:
        adapter.publish_exact(_request(fixture, action=PublicationAction.DRAFT_PR))

    assert captured.value.code == "draft_pr_capability_unavailable"
    assert captured.value.partial_effects.commit_created is False
    assert _remote_ref(fixture.remote, "uca/task-123") == ""
    assert (
        _git(
            fixture.sandbox,
            "show-ref",
            "--verify",
            "refs/heads/uca/task-123",
            check=False,
        )
        == ""
    )


def test_local_repository_requires_explicit_adapter_authorization(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)

    with pytest.raises(SourceControlPublicationError) as captured:
        GitSourceControlAdapter().publish_exact(_request(fixture))

    assert captured.value.code == "local_repository_not_allowed"
    assert captured.value.partial_effects.commit_created is False
    assert _remote_ref(fixture.remote, "uca/task-123") == ""


def test_external_source_control_loader_is_default_disabled(monkeypatch) -> None:
    monkeypatch.delenv("UCA_SOURCE_CONTROL_ADAPTER_FACTORY", raising=False)

    with pytest.raises(RuntimeError, match="disabled"):
        load_source_control_adapter()


@pytest.mark.parametrize(
    "identity",
    ["identity with spaces", "identity\nwith-control", "identity=unsafe"],
)
def test_git_adapter_rejects_unsafe_stable_identity(identity: str) -> None:
    with pytest.raises(ValueError, match="adapter identity"):
        GitSourceControlAdapter(adapter_identity=identity)
