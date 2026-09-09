from __future__ import annotations

import json
import shutil
import subprocess
import sys
from dataclasses import dataclass, field, replace
from pathlib import Path

import pytest

from universal_coding_agent.core.models import RepositorySpec, ReviewVerdict
from universal_coding_agent.core.safe_models import (
    ApprovedChangeManifest,
    ChangeOperation,
    ChangeScopeEntry,
    SafeModePolicy,
    SafeReviewResult,
    SafeTaskRequest,
    TestExecutionResult,
    TestProfile,
)
from universal_coding_agent.providers.fake import FakeModelProvider
from universal_coding_agent.safe_service import SafeAgentService
from universal_coding_agent.source_control import (
    ExactPatchPublicationError,
    ExactPatchPublicationService,
    ExactPublicationRequest,
    GitSourceControlAdapter,
    PublicationAction,
    PublicationPartialEffects,
    SourceControlCapabilities,
    SourceControlPublicationError,
    SourceControlPublicationResult,
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
class _ApprovedFixture:
    state_root: Path
    remote: Path
    task_id: str
    base_sha: str
    patch_sha256: str
    approval_sha256: str
    sandbox: Path


def _approved_fixture(tmp_path: Path, *, task_id: str) -> _ApprovedFixture:
    remote = tmp_path / "remote.git"
    remote.mkdir()
    _git(remote, "init", "--bare")

    seed = tmp_path / "seed"
    seed.mkdir()
    _git(seed, "init", "-b", "main")
    _git(seed, "config", "user.name", "Test")
    _git(seed, "config", "user.email", "test@example.test")
    (seed / "app.py").write_text(
        "def answer():\n    return 42\n",
        encoding="utf-8",
    )
    _git(seed, "add", "app.py")
    _git(seed, "commit", "-m", "fixture")
    base_sha = _git(seed, "rev-parse", "HEAD")
    _git(seed, "remote", "add", "origin", str(remote))
    _git(seed, "push", "origin", "main")
    _git(remote, "symbolic-ref", "HEAD", "refs/heads/main")

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
                    ("from pathlib import Path; assert 'return 43' in Path('app.py').read_text()"),
                ),
            ),
        )
    )
    task = SafeTaskRequest(
        task_id=task_id,
        thread_id=task_id,
        title="Safe fixture change",
        objective="Change the approved fixture answer from 42 to 43.",
        repository=RepositorySpec(url=str(remote), base_ref="main"),
        manifest=manifest,
        policy=policy,
        require_publish_approval=True,
    )
    state_root = tmp_path / "state"
    service = SafeAgentService.create(
        state_root,
        FakeModelProvider(),
        allow_local_sources=True,
    )
    try:
        service.run(task)
        pending = service.resume(task.thread_id, True)
        validation = service.artifacts.read_json(pending["patch_validation_ref"])
        patch_sha256 = validation["patch_sha256"]
        final = service.resume_publish(
            task.thread_id,
            approved=True,
            patch_sha256=patch_sha256,
        )
        report = service.artifacts.read_json(final["final_report_ref"])
        assert final["status"] == "completed"
        assert report["publish_approved"] is True
        approval_sha256 = report["publish_approval_sha256"]
    finally:
        service.close()

    return _ApprovedFixture(
        state_root=state_root,
        remote=remote,
        task_id=task_id,
        base_sha=base_sha,
        patch_sha256=patch_sha256,
        approval_sha256=approval_sha256,
        sandbox=state_root / "sandboxes" / task_id / "repo",
    )


@dataclass
class _CountingAdapter:
    delegate: GitSourceControlAdapter
    calls: list[ExactPublicationRequest] = field(default_factory=list)

    def capabilities(self) -> SourceControlCapabilities:
        return self.delegate.capabilities()

    def publish_exact(
        self,
        request: ExactPublicationRequest,
    ) -> SourceControlPublicationResult:
        self.calls.append(request)
        return self.delegate.publish_exact(request)


@dataclass
class _CapabilityAdapter:
    fixed_capabilities: SourceControlCapabilities
    calls: int = 0

    def capabilities(self) -> SourceControlCapabilities:
        return self.fixed_capabilities

    def publish_exact(
        self,
        request: ExactPublicationRequest,
    ) -> SourceControlPublicationResult:
        self.calls += 1
        raise AssertionError(f"adapter must not be called for {request.action}")


@dataclass
class _PartialFailureAdapter:
    calls: int = 0

    def capabilities(self) -> SourceControlCapabilities:
        return SourceControlCapabilities(
            adapter_identity="git-source-control-v1",
            commit=True,
            push=True,
        )

    def publish_exact(
        self,
        request: ExactPublicationRequest,
    ) -> SourceControlPublicationResult:
        self.calls += 1
        raise SourceControlPublicationError(
            "remote_ref_conflict",
            stage="push",
            cause_type="GitCommandError",
            partial_effects=PublicationPartialEffects(
                commit_created=True,
                commit_sha="c" * 40,
                local_ref_attempted=True,
                local_ref_verified=True,
                local_ref_created=True,
                local_ref=f"refs/heads/{request.head_branch}",
                push_attempted=True,
            ),
        )


@dataclass
class _InterruptingAdapter:
    calls: int = 0

    def capabilities(self) -> SourceControlCapabilities:
        return SourceControlCapabilities(
            adapter_identity="git-source-control-v1",
            commit=True,
            push=True,
        )

    def publish_exact(
        self,
        request: ExactPublicationRequest,
    ) -> SourceControlPublicationResult:
        self.calls += 1
        raise KeyboardInterrupt


@dataclass
class _InterruptingDraftAdapter:
    draft_pr_identity: str
    calls: int = 0

    def capabilities(self) -> SourceControlCapabilities:
        return SourceControlCapabilities(
            adapter_identity="git-source-control-v1",
            draft_pr_identity=self.draft_pr_identity,
            commit=True,
            push=True,
            draft_pr=True,
        )

    def publish_exact(
        self,
        request: ExactPublicationRequest,
    ) -> SourceControlPublicationResult:
        self.calls += 1
        raise KeyboardInterrupt


@dataclass
class _InterruptAfterSuccessfulPushAdapter:
    delegate: GitSourceControlAdapter
    calls: int = 0

    def capabilities(self) -> SourceControlCapabilities:
        return self.delegate.capabilities()

    def publish_exact(
        self,
        request: ExactPublicationRequest,
    ) -> SourceControlPublicationResult:
        self.calls += 1
        self.delegate.publish_exact(request)
        raise KeyboardInterrupt


@dataclass
class _FabricatedResultAdapter:
    calls: int = 0

    def capabilities(self) -> SourceControlCapabilities:
        return SourceControlCapabilities(
            adapter_identity="fabricated-result-fixture",
            commit=True,
        )

    def publish_exact(
        self,
        request: ExactPublicationRequest,
    ) -> SourceControlPublicationResult:
        self.calls += 1
        return SourceControlPublicationResult(
            publication_id=request.publication_id,
            action=request.action,
            commit_sha="c" * 40,
            tree_sha="d" * 40,
            local_ref=f"refs/heads/{request.head_branch}",
            commit_created=True,
            local_ref_created=True,
        )


@dataclass
class _FabricatedPushResultAdapter:
    calls: int = 0

    def capabilities(self) -> SourceControlCapabilities:
        return SourceControlCapabilities(
            adapter_identity="fabricated-push-result-fixture",
            commit=True,
            push=True,
        )

    def publish_exact(
        self,
        request: ExactPublicationRequest,
    ) -> SourceControlPublicationResult:
        self.calls += 1
        return SourceControlPublicationResult(
            publication_id=request.publication_id,
            action=request.action,
            commit_sha="c" * 40,
            tree_sha="d" * 40,
            local_ref=f"refs/heads/{request.head_branch}",
            commit_created=True,
            local_ref_created=True,
            pushed=True,
            push_performed=True,
            remote_before_sha="",
            remote_after_sha="c" * 40,
        )


def _publish(
    service: ExactPatchPublicationService,
    fixture: _ApprovedFixture,
    *,
    action: PublicationAction = PublicationAction.COMMIT,
    head_branch: str | None = None,
) -> dict:
    return service.publish_exact(
        fixture.task_id,
        approval_sha256=fixture.approval_sha256,
        patch_sha256=fixture.patch_sha256,
        action=action,
        head_branch=head_branch or f"uca/{fixture.task_id}",
    )


def test_quality_evidence_accepts_canonical_paths_in_a_different_order() -> None:
    assert ExactPatchPublicationService._quality_evidence_valid(
        {
            "scope_intact": True,
            "actual_changed_paths": ["a.py", "z.py"],
        },
        (
            TestExecutionResult(
                profile_id="python-check",
                passed=True,
                returncode=0,
                duration_ms=1,
                output="pass",
            ),
        ),
        ("z.py", "a.py"),
        ("python-check",),
        SafeReviewResult(verdict=ReviewVerdict.PASS),
        "PASS",
    )


def test_quality_evidence_requires_every_fixed_profile_to_exit_zero() -> None:
    base_payload = {
        "scope_intact": True,
        "actual_changed_paths": ["app.py"],
    }
    review = SafeReviewResult(verdict=ReviewVerdict.PASS)

    assert not ExactPatchPublicationService._quality_evidence_valid(
        base_payload,
        (),
        ("app.py",),
        ("python-check",),
        review,
        "PASS",
    )
    assert not ExactPatchPublicationService._quality_evidence_valid(
        base_payload,
        (
            TestExecutionResult(
                profile_id="python-check",
                passed=True,
                returncode=1,
                duration_ms=1,
                output="inconsistent evidence",
            ),
        ),
        ("app.py",),
        ("python-check",),
        review,
        "PASS",
    )


def test_exact_publication_commits_approved_patch_and_replays_after_restart(
    tmp_path: Path,
) -> None:
    fixture = _approved_fixture(tmp_path, task_id="publish-success")
    adapter = _CountingAdapter(GitSourceControlAdapter(allow_local_repositories=True))
    service = ExactPatchPublicationService(fixture.state_root, adapter)
    try:
        receipt = _publish(service, fixture)

        assert receipt["status"] == "completed"
        assert receipt["qualified"] is True
        assert receipt["replayed_receipt"] is False
        assert receipt["attempts"] == 1
        assert receipt["approval_sha256"] == fixture.approval_sha256
        assert receipt["patch_sha256"] == fixture.patch_sha256
        assert receipt["action"] == "commit"
        assert receipt["push_verified"] is False
        assert receipt["source_repository_modified"] is False
        assert receipt["merge_performed"] is False
        assert receipt["deployment_performed"] is False
        assert len(adapter.calls) == 1

        result = receipt["result"]
        commit_sha = result["commit_sha"]
        local_ref = f"refs/heads/uca/{fixture.task_id}"
        assert result["local_ref"] == local_ref
        assert _git(fixture.sandbox, "rev-parse", local_ref) == commit_sha
        assert (
            _git(fixture.sandbox, "rev-list", "--parents", "-n", "1", commit_sha)
            == f"{commit_sha} {fixture.base_sha}"
        )
        committed_patch = _git(
            fixture.sandbox,
            "diff",
            "--no-ext-diff",
            "--no-color",
            "--full-index",
            fixture.base_sha,
            commit_sha,
            "--",
            "app.py",
        )
        assert committed_patch + "\n" == adapter.calls[0].patch_text
        assert _git(fixture.sandbox, "rev-parse", "HEAD") == fixture.base_sha
        assert _git(fixture.sandbox, "diff", "--cached", "--name-only") == ""
        assert _git(fixture.sandbox, "status", "--porcelain") == "M app.py"
        assert (
            _git(
                fixture.remote,
                "rev-parse",
                "--verify",
                local_ref,
                check=False,
            )
            == ""
        )
        first_receipt_sha256 = receipt["publication_receipt_sha256"]
    finally:
        service.close()

    shutil.rmtree(fixture.sandbox)
    (
        fixture.state_root / "artifacts" / "tasks" / fixture.task_id / "publish-approval.json"
    ).unlink()

    restarted_adapter = _CountingAdapter(GitSourceControlAdapter(allow_local_repositories=True))
    restarted = ExactPatchPublicationService(fixture.state_root, restarted_adapter)
    try:
        replayed = _publish(restarted, fixture)

        assert replayed["status"] == "completed"
        assert replayed["replayed_receipt"] is True
        assert replayed["attempts"] == 1
        assert replayed["publication_receipt_sha256"] == first_receipt_sha256
        assert replayed["result"] == receipt["result"]
        assert restarted_adapter.calls == []

        with pytest.raises(ExactPatchPublicationError) as captured:
            _publish(restarted, fixture, head_branch="uca/conflicting-after-completion")
        assert captured.value.code == "publication_intent_conflict"
        assert restarted_adapter.calls == []
    finally:
        restarted.close()


def test_exact_publication_rejects_conflicting_branch_for_consumed_approval(
    tmp_path: Path,
) -> None:
    fixture = _approved_fixture(tmp_path, task_id="publish-conflict")
    adapter = _CountingAdapter(GitSourceControlAdapter(allow_local_repositories=True))
    service = ExactPatchPublicationService(fixture.state_root, adapter)
    try:
        _publish(service, fixture)

        with pytest.raises(ExactPatchPublicationError) as captured:
            _publish(service, fixture, head_branch="uca/conflicting-intent")

        assert captured.value.code == "publication_intent_conflict"
        assert len(adapter.calls) == 1
    finally:
        service.close()


def test_completed_replay_fails_closed_on_corrupted_durable_receipt(
    tmp_path: Path,
) -> None:
    fixture = _approved_fixture(tmp_path, task_id="publish-receipt-integrity")
    adapter = _CountingAdapter(GitSourceControlAdapter(allow_local_repositories=True))
    service = ExactPatchPublicationService(fixture.state_root, adapter)
    try:
        completed = _publish(service, fixture)
        stored = service.store.get_required(completed["publication_id"])
        corrupted = dict(stored.receipt or {})
        corrupted["qualified"] = False
        service.store.connection.execute(
            """
            UPDATE source_control_publications
            SET receipt_json = ?
            WHERE publication_id = ?
            """,
            (json.dumps(corrupted, sort_keys=True), stored.publication_id),
        )
        service.store.connection.commit()
    finally:
        service.close()

    shutil.rmtree(fixture.sandbox)
    replay_adapter = _CountingAdapter(
        GitSourceControlAdapter(allow_local_repositories=True)
    )
    replay = ExactPatchPublicationService(fixture.state_root, replay_adapter)
    try:
        with pytest.raises(ExactPatchPublicationError) as captured:
            _publish(replay, fixture)

        assert captured.value.code == "publication_receipt_invalid"
        assert replay_adapter.calls == []
    finally:
        replay.close()


def test_completed_replay_rejects_nested_result_corruption_even_if_attempt_matches(
    tmp_path: Path,
) -> None:
    fixture = _approved_fixture(tmp_path, task_id="publish-nested-receipt-integrity")
    service = ExactPatchPublicationService(
        fixture.state_root,
        _CountingAdapter(GitSourceControlAdapter(allow_local_repositories=True)),
    )
    try:
        completed = _publish(service, fixture)
        stored = service.store.get_required(completed["publication_id"])
        corrupted = dict(stored.receipt or {})
        corrupted["result"] = {}
        encoded = json.dumps(corrupted, separators=(",", ":"), sort_keys=True)
        service.store.connection.execute(
            """
            UPDATE source_control_publications
            SET receipt_json = ?
            WHERE publication_id = ?
            """,
            (encoded, stored.publication_id),
        )
        service.store.connection.execute(
            """
            UPDATE source_control_publication_attempts
            SET receipt_json = ?
            WHERE publication_id = ? AND attempt = ?
            """,
            (encoded, stored.publication_id, stored.attempts),
        )
        service.store.connection.commit()
    finally:
        service.close()

    shutil.rmtree(fixture.sandbox)
    replay_adapter = _CountingAdapter(
        GitSourceControlAdapter(allow_local_repositories=True)
    )
    replay = ExactPatchPublicationService(fixture.state_root, replay_adapter)
    try:
        with pytest.raises(ExactPatchPublicationError) as captured:
            _publish(replay, fixture)

        assert captured.value.code == "publication_receipt_invalid"
        assert replay_adapter.calls == []
    finally:
        replay.close()


@pytest.mark.parametrize(
    ("repository", "expected_code", "head_branch"),
    [
        (
            RepositorySpec(url="relative/remote.git", base_ref="main"),
            "approval_relative_repository_forbidden",
            "uca/relative",
        ),
        (
            RepositorySpec(url="/tmp/remote.git", base_ref="HEAD"),
            "approval_base_branch_invalid",
            "main",
        ),
    ],
)
def test_publication_service_rejects_ambiguous_repository_authority(
    tmp_path: Path,
    repository: RepositorySpec,
    expected_code: str,
    head_branch: str,
) -> None:
    fixture = _approved_fixture(tmp_path, task_id=f"authority-{expected_code}")
    adapter = _CountingAdapter(GitSourceControlAdapter(allow_local_repositories=True))
    service = ExactPatchPublicationService(fixture.state_root, adapter)
    try:
        approval_ref = (
            f"artifact://tasks/{fixture.task_id}/publish-approval.json"
        )
        approval = service.artifacts.read_json(approval_ref)
        approval["repository"] = repository.model_dump(mode="json")
        rewritten = service.artifacts.write_json(
            f"tasks/{fixture.task_id}/publish-approval.json",
            approval,
        )
        altered = replace(fixture, approval_sha256=rewritten.sha256)

        with pytest.raises(ExactPatchPublicationError) as captured:
            _publish(service, altered, action=PublicationAction.PUSH, head_branch=head_branch)

        assert captured.value.code == expected_code
        assert adapter.calls == []
        assert _git(fixture.remote, "rev-parse", "refs/heads/main") == fixture.base_sha
    finally:
        service.close()


@pytest.mark.parametrize("evidence_name", ["test-results.json", "safe-review.json"])
def test_publication_rejects_tampered_quality_evidence_before_adapter(
    tmp_path: Path,
    evidence_name: str,
) -> None:
    fixture = _approved_fixture(tmp_path, task_id=f"quality-{evidence_name[:-5]}")
    evidence_path = (
        fixture.state_root / "artifacts" / "tasks" / fixture.task_id / evidence_name
    )
    evidence_path.write_text("{}", encoding="utf-8")
    adapter = _CountingAdapter(GitSourceControlAdapter(allow_local_repositories=True))
    service = ExactPatchPublicationService(fixture.state_root, adapter)
    try:
        with pytest.raises(ExactPatchPublicationError) as captured:
            _publish(service, fixture)

        assert captured.value.code == "approved_evidence_invalid"
        assert adapter.calls == []
    finally:
        service.close()


def test_publication_rejects_unsafe_sandbox_git_config_before_adapter(
    tmp_path: Path,
) -> None:
    fixture = _approved_fixture(tmp_path, task_id="unsafe-git-config")
    alternate = tmp_path / "alternate.git"
    alternate.mkdir()
    _git(alternate, "init", "--bare")
    _git(
        fixture.sandbox,
        "config",
        f"url.{alternate}.insteadOf",
        str(fixture.remote),
    )
    adapter = _CountingAdapter(GitSourceControlAdapter(allow_local_repositories=True))
    service = ExactPatchPublicationService(fixture.state_root, adapter)
    try:
        with pytest.raises(ExactPatchPublicationError) as captured:
            _publish(service, fixture, action=PublicationAction.PUSH)

        assert captured.value.code == "sandbox_git_config_unsafe"
        assert adapter.calls == []
        assert service.store.connection.execute(
            "SELECT COUNT(*) FROM source_control_publications"
        ).fetchone()[0] == 0
    finally:
        service.close()


@pytest.mark.parametrize("tamper_payload", [False, True])
def test_exact_publication_rejects_wrong_or_tampered_approval_hash(
    tmp_path: Path,
    tamper_payload: bool,
) -> None:
    fixture = _approved_fixture(
        tmp_path,
        task_id=f"publish-approval-integrity-{int(tamper_payload)}",
    )
    adapter = _CountingAdapter(GitSourceControlAdapter(allow_local_repositories=True))
    if tamper_payload:
        approval_path = (
            fixture.state_root / "artifacts" / "tasks" / fixture.task_id / "publish-approval.json"
        )
        approval = json.loads(approval_path.read_text(encoding="utf-8"))
        approval["approved"] = False
        approval_path.write_text(
            json.dumps(approval, sort_keys=True),
            encoding="utf-8",
        )
        approval_sha256 = fixture.approval_sha256
    else:
        approval_sha256 = "0" * 64

    service = ExactPatchPublicationService(fixture.state_root, adapter)
    try:
        with pytest.raises(ExactPatchPublicationError) as captured:
            service.publish_exact(
                fixture.task_id,
                approval_sha256=approval_sha256,
                patch_sha256=fixture.patch_sha256,
                action=PublicationAction.COMMIT,
                head_branch=f"uca/{fixture.task_id}",
            )

        assert captured.value.code == "approval_integrity_invalid"
        assert adapter.calls == []
    finally:
        service.close()


def test_exact_publication_rejects_worktree_drift_before_adapter_call(
    tmp_path: Path,
) -> None:
    fixture = _approved_fixture(tmp_path, task_id="publish-worktree-drift")
    (fixture.sandbox / "app.py").write_text(
        "def answer():\n    return 44\n",
        encoding="utf-8",
    )
    adapter = _CountingAdapter(GitSourceControlAdapter(allow_local_repositories=True))
    service = ExactPatchPublicationService(fixture.state_root, adapter)
    try:
        with pytest.raises(ExactPatchPublicationError) as captured:
            _publish(service, fixture)

        assert captured.value.code in {
            "materialized_patch_drift",
            "materialized_patch_invalid",
        }
        assert adapter.calls == []
        assert (
            service.store.connection.execute(
                "SELECT COUNT(*) FROM source_control_publications"
            ).fetchone()[0]
            == 0
        )
    finally:
        service.close()


def test_exact_publication_requires_action_capability_before_reservation(
    tmp_path: Path,
) -> None:
    fixture = _approved_fixture(tmp_path, task_id="publish-no-push")
    adapter = _CapabilityAdapter(
        SourceControlCapabilities(
            adapter_identity="commit-only-fixture",
            commit=True,
            push=False,
            draft_pr=False,
        )
    )
    service = ExactPatchPublicationService(fixture.state_root, adapter)
    try:
        with pytest.raises(ExactPatchPublicationError) as captured:
            _publish(service, fixture, action=PublicationAction.PUSH)

        assert captured.value.code == "adapter_push_unsupported"
        assert adapter.calls == 0
        assert (
            service.store.connection.execute(
                "SELECT COUNT(*) FROM source_control_publications"
            ).fetchone()[0]
            == 0
        )
    finally:
        service.close()


def test_exact_publication_preserves_partial_failure_and_reconciles_exact_retry(
    tmp_path: Path,
) -> None:
    fixture = _approved_fixture(tmp_path, task_id="publish-partial-failure")
    adapter = _PartialFailureAdapter()
    service = ExactPatchPublicationService(fixture.state_root, adapter)
    try:
        failed = _publish(service, fixture, action=PublicationAction.PUSH)

        assert failed["status"] == "failed"
        assert failed["qualified"] is False
        assert failed["error"] == {
            "code": "remote_ref_conflict",
            "stage": "push",
            "cause_type": "GitCommandError",
        }
        assert failed["partial_effects"] == {
            "commit_created": True,
            "commit_sha": "c" * 40,
            "local_ref_attempted": True,
            "local_ref_verified": True,
            "local_ref_created": True,
            "local_ref_updated": False,
            "local_ref": f"refs/heads/uca/{fixture.task_id}",
            "push_attempted": True,
            "push_verified": False,
            "remote_sha": "",
            "draft_pr_attempted": False,
            "draft_pr_created": False,
            "draft_pr_url": "",
        }
        assert failed["source_repository_modified"] is None
        assert failed["side_effects_indeterminate"] is True
        assert failed["effect_attribution_indeterminate"] is True
        assert failed["retryable"] is True
        assert failed["reconciliation_required"] is True
        assert failed["replayed_receipt"] is False
        assert adapter.calls == 1
        assert failed["attempt"] == 1
        first_attempt_ref = failed["publication_attempt_ref"]
        publication_id = failed["publication_id"]
        assert service.store.get_required(publication_id).status == "planned"
        assert len(service.store.attempt_receipts(publication_id)) == 1

        retried = _publish(service, fixture, action=PublicationAction.PUSH)

        assert retried["status"] == "failed"
        assert retried["replayed_receipt"] is False
        assert retried["attempt"] == 2
        assert retried["attempts"] == 2
        assert retried["publication_attempt_ref"] != first_attempt_ref
        assert adapter.calls == 2
        assert len(service.store.attempt_receipts(publication_id)) == 2
    finally:
        service.close()

    recovered_adapter = _CountingAdapter(GitSourceControlAdapter(allow_local_repositories=True))
    recovered = ExactPatchPublicationService(fixture.state_root, recovered_adapter)
    try:
        completed = _publish(recovered, fixture, action=PublicationAction.PUSH)

        assert completed["status"] == "completed"
        assert completed["attempt"] == 3
        assert completed["attempts"] == 3
        assert completed["replayed_receipt"] is False
        assert completed["push_verified"] is True
        assert completed["source_repository_modified"] is True
        assert len(recovered_adapter.calls) == 1
        assert len(recovered.store.attempt_receipts(publication_id)) == 3

        replayed = _publish(recovered, fixture, action=PublicationAction.PUSH)
        assert replayed["status"] == "completed"
        assert replayed["attempts"] == 3
        assert replayed["replayed_receipt"] is True
        assert len(recovered_adapter.calls) == 1
    finally:
        recovered.close()


def test_local_ref_post_success_fault_is_indeterminate_and_reconciles(
    tmp_path: Path,
) -> None:
    fixture = _approved_fixture(tmp_path, task_id="publish-local-ref-fault")

    class _PostSuccessFaultAdapter(GitSourceControlAdapter):
        faulted = False

        def _run(self, root: Path, arguments: list[str], **kwargs):
            result = super()._run(root, arguments, **kwargs)
            if arguments[:2] == ["update-ref", "--no-deref"] and not self.faulted:
                self.faulted = True
                raise RuntimeError("fault after local ref update")
            return result

    service = ExactPatchPublicationService(
        fixture.state_root,
        _PostSuccessFaultAdapter(allow_local_repositories=True),
    )
    try:
        failed = _publish(service, fixture)

        assert failed["status"] == "failed"
        assert failed["side_effects_indeterminate"] is True
        assert failed["effect_attribution_indeterminate"] is False
        assert failed["source_repository_modified"] is False
        effects = failed["partial_effects"]
        assert effects["commit_created"] is True
        assert effects["local_ref_attempted"] is True
        assert effects["local_ref_verified"] is False
        assert effects["local_ref_created"] is False
        assert effects["local_ref_updated"] is False
        assert _git(
            fixture.sandbox,
            "rev-parse",
            f"refs/heads/uca/{fixture.task_id}",
        ) == effects["commit_sha"]
    finally:
        service.close()

    recovered = ExactPatchPublicationService(
        fixture.state_root,
        GitSourceControlAdapter(allow_local_repositories=True),
    )
    try:
        completed = _publish(recovered, fixture)

        assert completed["status"] == "completed"
        assert completed["attempts"] == 2
        assert completed["result"]["reused"] is True
        assert completed["reconciliation_required"] is False
    finally:
        recovered.close()


def test_push_retry_after_local_ref_fault_has_known_remote_effect(
    tmp_path: Path,
) -> None:
    fixture = _approved_fixture(tmp_path, task_id="publish-local-ref-push-fault")

    class _PostSuccessFaultAdapter(GitSourceControlAdapter):
        faulted = False

        def _run(self, root: Path, arguments: list[str], **kwargs):
            result = super()._run(root, arguments, **kwargs)
            if arguments[:2] == ["update-ref", "--no-deref"] and not self.faulted:
                self.faulted = True
                raise RuntimeError("fault after local ref update")
            return result

    service = ExactPatchPublicationService(
        fixture.state_root,
        _PostSuccessFaultAdapter(allow_local_repositories=True),
    )
    try:
        failed = _publish(service, fixture, action=PublicationAction.PUSH)

        assert failed["status"] == "failed"
        assert failed["partial_effects"]["local_ref_attempted"] is True
        assert failed["partial_effects"]["local_ref_verified"] is False
        assert failed["partial_effects"]["push_attempted"] is False
        assert failed["side_effects_indeterminate"] is True
        assert failed["effect_attribution_indeterminate"] is False
        assert failed["source_repository_modified"] is False
        assert _git(
            fixture.remote,
            "show-ref",
            "--verify",
            f"refs/heads/uca/{fixture.task_id}",
            check=False,
        ) == ""
    finally:
        service.close()

    recovered = ExactPatchPublicationService(
        fixture.state_root,
        GitSourceControlAdapter(allow_local_repositories=True),
    )
    try:
        completed = _publish(recovered, fixture, action=PublicationAction.PUSH)

        assert completed["status"] == "completed"
        assert completed["attempts"] == 2
        assert completed["reconciled_existing_effects"] is True
        assert completed["effect_attribution_indeterminate"] is False
        assert completed["source_repository_modified"] is True
        assert completed["result"]["commit_created"] is False
        assert completed["result"]["push_performed"] is True

        replayed = _publish(recovered, fixture, action=PublicationAction.PUSH)
        assert replayed["replayed_receipt"] is True
        assert replayed["effect_attribution_indeterminate"] is False
        assert replayed["source_repository_modified"] is True
    finally:
        recovered.close()


def test_interruption_leaves_planned_intent_for_exact_reconciliation(
    tmp_path: Path,
) -> None:
    fixture = _approved_fixture(tmp_path, task_id="publish-interrupted")
    interrupted_adapter = _InterruptingAdapter()
    service = ExactPatchPublicationService(fixture.state_root, interrupted_adapter)
    try:
        with pytest.raises(KeyboardInterrupt):
            _publish(service, fixture)

        record = service.store.connection.execute(
            "SELECT status, attempts, receipt_json FROM source_control_publications"
        ).fetchone()
        assert record == ("planned", 1, None)
        assert interrupted_adapter.calls == 1
    finally:
        service.close()

    recovered_adapter = _CountingAdapter(GitSourceControlAdapter(allow_local_repositories=True))
    recovered = ExactPatchPublicationService(fixture.state_root, recovered_adapter)
    try:
        completed = _publish(recovered, fixture)
        assert completed["status"] == "completed"
        assert completed["attempt"] == 2
        assert completed["attempts"] == 2
        assert len(recovered_adapter.calls) == 1
        attempts = recovered.store.attempt_receipts(completed["publication_id"])
        assert [item["status"] for item in attempts] == ["interrupted", "completed"]
        assert attempts[0]["side_effects_indeterminate"] is True
        persisted_interruption = recovered.artifacts.read_json(
            f"artifact://tasks/{fixture.task_id}/"
            "source-control-publication-attempt-0001.json"
        )
        assert persisted_interruption == attempts[0]
    finally:
        recovered.close()


def test_planned_retry_rejects_changed_adapter_identity(
    tmp_path: Path,
) -> None:
    fixture = _approved_fixture(tmp_path, task_id="publish-adapter-identity")
    interrupted = ExactPatchPublicationService(fixture.state_root, _InterruptingAdapter())
    try:
        with pytest.raises(KeyboardInterrupt):
            _publish(interrupted, fixture, action=PublicationAction.PUSH)
    finally:
        interrupted.close()

    changed_adapter = _CountingAdapter(
        GitSourceControlAdapter(
            allow_local_repositories=True,
            adapter_identity="different-git-account-v1",
        )
    )
    retry = ExactPatchPublicationService(fixture.state_root, changed_adapter)
    try:
        with pytest.raises(ExactPatchPublicationError) as captured:
            _publish(retry, fixture, action=PublicationAction.PUSH)

        assert captured.value.code == "publication_intent_conflict"
        assert changed_adapter.calls == []
    finally:
        retry.close()


def test_planned_draft_retry_rejects_changed_creator_identity(
    tmp_path: Path,
) -> None:
    fixture = _approved_fixture(tmp_path, task_id="publish-draft-identity")
    first_adapter = _InterruptingDraftAdapter("github:installation-100")
    interrupted = ExactPatchPublicationService(fixture.state_root, first_adapter)
    try:
        with pytest.raises(KeyboardInterrupt):
            _publish(interrupted, fixture, action=PublicationAction.DRAFT_PR)
    finally:
        interrupted.close()

    changed_adapter = _CapabilityAdapter(
        SourceControlCapabilities(
            adapter_identity="git-source-control-v1",
            draft_pr_identity="github:installation-200",
            commit=True,
            push=True,
            draft_pr=True,
        )
    )
    retry = ExactPatchPublicationService(fixture.state_root, changed_adapter)
    try:
        with pytest.raises(ExactPatchPublicationError) as captured:
            _publish(retry, fixture, action=PublicationAction.DRAFT_PR)

        assert captured.value.code == "publication_intent_conflict"
        assert changed_adapter.calls == 0
    finally:
        retry.close()


def test_retry_after_unrecorded_success_marks_effect_attribution_unknown(
    tmp_path: Path,
) -> None:
    fixture = _approved_fixture(tmp_path, task_id="publish-post-push-interrupt")
    interrupted_adapter = _InterruptAfterSuccessfulPushAdapter(
        GitSourceControlAdapter(allow_local_repositories=True)
    )
    service = ExactPatchPublicationService(fixture.state_root, interrupted_adapter)
    try:
        with pytest.raises(KeyboardInterrupt):
            _publish(service, fixture, action=PublicationAction.PUSH)

        assert _git(
            fixture.remote,
            "rev-parse",
            f"refs/heads/uca/{fixture.task_id}",
        )
        assert service.store.connection.execute(
            "SELECT status, attempts, receipt_json FROM source_control_publications"
        ).fetchone() == ("planned", 1, None)
    finally:
        service.close()

    recovered = ExactPatchPublicationService(
        fixture.state_root,
        _CountingAdapter(GitSourceControlAdapter(allow_local_repositories=True)),
    )
    try:
        completed = _publish(recovered, fixture, action=PublicationAction.PUSH)

        assert completed["status"] == "completed"
        assert completed["attempts"] == 2
        assert completed["reconciled_existing_effects"] is True
        assert completed["effect_attribution_indeterminate"] is True
        assert completed["source_repository_modified"] is None
        assert completed["result"]["commit_created"] is False
        assert completed["result"]["push_performed"] is False
    finally:
        recovered.close()


def test_fabricated_adapter_result_cannot_complete_publication(
    tmp_path: Path,
) -> None:
    fixture = _approved_fixture(tmp_path, task_id="publish-fabricated-result")
    adapter = _FabricatedResultAdapter()
    service = ExactPatchPublicationService(fixture.state_root, adapter)
    try:
        failed = _publish(service, fixture)

        assert failed["status"] == "failed"
        assert failed["qualified"] is False
        assert failed["error"]["code"] in {
            "adapter_result_repository_mismatch",
            "adapter_result_repository_verification_failed",
        }
        assert failed["side_effects_indeterminate"] is True
        assert failed["reconciliation_required"] is True
        assert service.store.get_required(failed["publication_id"]).status == "planned"
        assert adapter.calls == 1
    finally:
        service.close()


def test_unverified_fabricated_push_cannot_claim_remote_modification(
    tmp_path: Path,
) -> None:
    fixture = _approved_fixture(tmp_path, task_id="publish-fabricated-push-result")
    adapter = _FabricatedPushResultAdapter()
    service = ExactPatchPublicationService(fixture.state_root, adapter)
    try:
        failed = _publish(service, fixture, action=PublicationAction.PUSH)

        assert failed["status"] == "failed"
        assert failed["side_effects_indeterminate"] is True
        assert failed["effect_attribution_indeterminate"] is True
        assert failed["source_repository_modified"] is None
        assert failed["partial_effects_attribution_trusted"] is False
        assert failed["partial_effects"]["push_attempted"] is True
        assert failed["partial_effects"]["push_verified"] is True
        assert _git(
            fixture.remote,
            "show-ref",
            "--verify",
            f"refs/heads/uca/{fixture.task_id}",
            check=False,
        ) == ""
        assert adapter.calls == 1
    finally:
        service.close()
