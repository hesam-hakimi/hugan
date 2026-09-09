from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

from universal_coding_agent.source_control import (
    DraftPullRequestRequest,
    DraftPullRequestResult,
    GitSourceControlAdapter,
)
from universal_coding_agent.testlab.github_publication_live import (
    GitHubPublicationLiveConfig,
    _redacted_failure,
    _state_contains_secret,
    _validate_config,
    run_github_publication_live,
)

_FIXTURE_PATH = "universal-coding-agent/qualification/github-live-fixture.txt"


def _git(cwd: Path, *arguments: str, check: bool = True) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )
    if check and completed.returncode != 0:
        raise RuntimeError(completed.stderr or completed.stdout)
    return completed.stdout.strip()


@dataclass
class _DraftState:
    request: DraftPullRequestRequest | None = None
    calls: int = 0

    def ensure_draft(self, request: DraftPullRequestRequest) -> DraftPullRequestResult:
        self.calls += 1
        created = self.request is None
        if self.request is None:
            self.request = request
        elif self.request != request:
            raise AssertionError("Draft PR replay must preserve the exact request")
        return DraftPullRequestResult(
            provider="github",
            pull_request_id="101",
            url="https://github.example/qualification/repository/pull/101",
            base_branch=request.base_branch,
            base_sha=request.base_sha,
            head_branch=request.head_branch,
            head_sha=request.head_sha,
            created=created,
        )


def _fixture_repository(tmp_path: Path) -> tuple[Path, Path, str]:
    remote = tmp_path / "remote.git"
    remote.mkdir()
    _git(remote, "init", "--bare")

    source = tmp_path / "source"
    source.mkdir()
    _git(source, "init", "-b", "main")
    _git(source, "config", "user.name", "Qualification Test")
    _git(source, "config", "user.email", "qualification@example.test")
    fixture = source / _FIXTURE_PATH
    fixture.parent.mkdir(parents=True)
    fixture.write_text("UCA_GITHUB_LIVE_QUALIFICATION_FIXTURE=v1\n", encoding="utf-8")
    _git(source, "add", _FIXTURE_PATH)
    _git(source, "commit", "-m", "qualification fixture")
    base_sha = _git(source, "rev-parse", "HEAD")
    _git(source, "remote", "add", "origin", str(remote))
    _git(source, "push", "origin", "main")
    _git(remote, "symbolic-ref", "HEAD", "refs/heads/main")
    return source, remote, base_sha


def test_live_qualification_proves_isolated_publication_and_both_replays(
    tmp_path: Path,
) -> None:
    source, remote, base_sha = _fixture_repository(tmp_path)
    draft_state = _DraftState()

    def adapter_factory() -> GitSourceControlAdapter:
        return GitSourceControlAdapter(
            allow_local_repositories=True,
            draft_pr_creator=draft_state,
            adapter_identity="github-live-test-adapter",
            draft_pr_identity="github:test-account",
        )

    state_root = tmp_path / "state"
    state_root.mkdir()
    (state_root / "console.log").touch()
    secret = "github_live_test_token_that_must_not_persist"
    summary = run_github_publication_live(
        GitHubPublicationLiveConfig(
            state_root=state_root,
            source_root=source,
            repository_url=str(remote),
            base_branch="main",
            base_sha=base_sha,
            head_branch="uca/github-live-qualification-test-001",
        ),
        adapter_factory=adapter_factory,
        allow_local_sources=True,
        secret_values=(secret,),
    )

    assert summary["qualified"] is True
    assert summary["first_publication"]["result"]["push_performed"] is True
    assert summary["first_publication"]["result"]["draft_pr"]["created"] is True
    assert summary["adapter_replay"]["push_performed"] is False
    assert summary["adapter_replay"]["draft_pr"]["created"] is False
    assert summary["adapter_replay"]["reused"] is True
    assert summary["durable_restart_replay"]["replayed_receipt"] is True
    assert summary["remote_refs"] == {
        "added": ["refs/heads/uca/github-live-qualification-test-001"],
        "removed": [],
        "changed": [],
        "base_preserved": True,
        "tags_preserved": True,
        "only_expected_head_added": True,
    }
    assert summary["source"]["source_preserved"] is True
    assert all(value is False for value in summary["forbidden_effects"].values())
    assert draft_state.calls == 2
    assert _git(source, "status", "--porcelain") == ""
    assert _git(source, "rev-parse", "HEAD") == base_sha
    assert _git(remote, "rev-parse", "refs/heads/main") == base_sha
    assert _git(
        remote,
        "rev-parse",
        "refs/heads/uca/github-live-qualification-test-001",
    ) == summary["head_sha"]
    summary_text = (state_root / "github-publication-live-summary.json").read_text()
    assert secret not in summary_text
    assert not _state_contains_secret(state_root, (secret,))


def test_live_qualification_fails_closed_for_dirty_source(tmp_path: Path) -> None:
    source, remote, base_sha = _fixture_repository(tmp_path)
    (source / "dirty.txt").write_text("not approved\n", encoding="utf-8")

    def forbidden_factory():
        raise AssertionError("adapter must not be created for a dirty source")

    summary = run_github_publication_live(
        GitHubPublicationLiveConfig(
            state_root=tmp_path / "state",
            source_root=source,
            repository_url=str(remote),
            base_branch="main",
            base_sha=base_sha,
            head_branch="uca/github-live-qualification-dirty",
        ),
        adapter_factory=forbidden_factory,
        allow_local_sources=True,
    )

    assert summary["qualified"] is False
    assert summary["failure"] == {"type": "RuntimeError"}
    assert _git(
        remote,
        "show-ref",
        "--verify",
        "refs/heads/uca/github-live-qualification-dirty",
        check=False,
    ) == ""


def test_live_config_requires_github_ssh_agent_and_isolated_head(
    tmp_path: Path,
    monkeypatch,
) -> None:
    source, _remote, base_sha = _fixture_repository(tmp_path)
    monkeypatch.setenv("UCA_GITHUB_REPOSITORY", "example/repository")
    monkeypatch.setenv("SSH_AUTH_SOCK", "/tmp/qualification-agent.sock")
    base = GitHubPublicationLiveConfig(
        state_root=tmp_path / "state",
        source_root=source,
        repository_url="git@github.com:example/repository.git",
        base_branch="main",
        base_sha=base_sha,
        head_branch="uca/github-live-qualification-20260830T000000Z",
    )

    validated = _validate_config(base, allow_local_sources=False)

    assert validated.repository_url == "git@github.com:example/repository.git"

    invalid_url = base.__class__(**{**base.__dict__, "repository_url": "https://github.com/x/y"})
    invalid_head = base.__class__(**{**base.__dict__, "head_branch": "feature/not-isolated"})
    for invalid in (invalid_url, invalid_head):
        try:
            _validate_config(invalid, allow_local_sources=False)
        except ValueError:
            pass
        else:
            raise AssertionError("unsafe live configuration was accepted")


def test_failure_evidence_and_state_scan_do_not_echo_secret(tmp_path: Path) -> None:
    secret = "github_secret_value_for_redaction_test"
    failure = _redacted_failure(RuntimeError(f"provider said {secret}"))

    assert secret not in json.dumps(failure)
    assert failure == {"type": "RuntimeError"}

    state_root = tmp_path / "state"
    state_root.mkdir()
    (state_root / "chunked.bin").write_bytes(b"prefix" + secret.encode() + b"suffix")
    assert _state_contains_secret(state_root, (secret,))


def test_invalid_overlapping_state_root_never_writes_into_source(tmp_path: Path) -> None:
    source, remote, base_sha = _fixture_repository(tmp_path)
    before = _git(source, "status", "--porcelain")

    summary = run_github_publication_live(
        GitHubPublicationLiveConfig(
            state_root=source,
            source_root=source,
            repository_url=str(remote),
            base_branch="main",
            base_sha=base_sha,
            head_branch="uca/github-live-qualification-overlap",
        ),
        adapter_factory=lambda: (_ for _ in ()).throw(AssertionError("unreachable")),
        allow_local_sources=True,
    )

    assert summary["qualified"] is False
    assert summary["failure"] == {"type": "ValueError"}
    assert not (source / "github-publication-live-summary.json").exists()
    assert _git(source, "status", "--porcelain") == before == ""
