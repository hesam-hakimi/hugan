from __future__ import annotations

import urllib.error
from dataclasses import dataclass, field

import pytest

from universal_coding_agent.core.models import RepositorySpec
from universal_coding_agent.source_control import DraftPullRequestRequest
from universal_coding_agent.source_control.github import (
    GITHUB_ACCOUNT_IDENTITY_ENV,
    GITHUB_REPOSITORY_ENV,
    GITHUB_TOKEN_ENV,
    GitHubApiResponse,
    GitHubDraftPullRequestCreator,
    GitHubDraftPullRequestError,
    UrllibGitHubApiTransport,
    create_adapter,
)

BASE_SHA = "a" * 40
HEAD_SHA = "b" * 40
PUBLICATION_ID = "c" * 64


@dataclass
class _FakeGitHubTransport:
    base_sha: str = BASE_SHA
    head_sha: str = HEAD_SHA
    pulls: list[dict[str, object]] = field(default_factory=list)
    create_status: int = 201
    calls: list[tuple[str, str, dict[str, str], dict[str, object]]] = field(
        default_factory=list
    )

    def request_json(
        self,
        method: str,
        path: str,
        *,
        query=None,
        payload=None,
    ) -> GitHubApiResponse:
        query_dict = dict(query or {})
        payload_dict = dict(payload or {})
        self.calls.append((method, path, query_dict, payload_dict))
        if "/git/ref/heads%2Fmain" in path:
            return GitHubApiResponse(200, {"object": {"sha": self.base_sha}})
        if "/git/ref/heads%2Fuca%2Ftask-123" in path:
            return GitHubApiResponse(200, {"object": {"sha": self.head_sha}})
        if method == "GET" and path.endswith("/pulls"):
            return GitHubApiResponse(200, list(self.pulls))
        if method == "POST" and path.endswith("/pulls"):
            if self.create_status == 201:
                created = _pull_payload()
                self.pulls = [created]
                return GitHubApiResponse(201, created)
            return GitHubApiResponse(self.create_status, {"message": "redacted"})
        raise AssertionError(f"unexpected fake GitHub request: {method} {path}")


def _request(*, repository_url: str = "https://github.com/hesam-hakimi/hugan.git"):
    return DraftPullRequestRequest(
        publication_id=PUBLICATION_ID,
        repository=RepositorySpec(url=repository_url, base_ref="main"),
        base_branch="main",
        base_sha=BASE_SHA,
        head_branch="uca/task-123",
        head_sha=HEAD_SHA,
        title="P2.3c qualification",
        body="Exact approved publication.",
    )


def _pull_payload(**updates: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "base": {
            "ref": "main",
            "repo": {"full_name": "hesam-hakimi/hugan"},
            "sha": BASE_SHA,
        },
        "body": "Exact approved publication.",
        "draft": True,
        "head": {
            "ref": "uca/task-123",
            "repo": {"full_name": "hesam-hakimi/hugan"},
            "sha": HEAD_SHA,
        },
        "html_url": "https://github.com/hesam-hakimi/hugan/pull/17",
        "number": 17,
        "state": "open",
        "title": "P2.3c qualification",
    }
    payload.update(updates)
    return payload


def _creator(transport: _FakeGitHubTransport) -> GitHubDraftPullRequestCreator:
    return GitHubDraftPullRequestCreator(
        transport=transport,
        repository_full_name="hesam-hakimi/hugan",
        account_identity="installation-100",
    )


@pytest.mark.parametrize(
    "repository_url",
    [
        "https://github.com/hesam-hakimi/hugan.git",
        "git@github.com:hesam-hakimi/hugan.git",
        "ssh://git@github.com/hesam-hakimi/hugan.git",
    ],
)
def test_github_creator_creates_only_the_exact_draft(
    repository_url: str,
) -> None:
    transport = _FakeGitHubTransport()

    result = _creator(transport).ensure_draft(_request(repository_url=repository_url))

    assert result.provider == "github"
    assert result.created is True
    assert result.draft is True
    assert result.base_sha == BASE_SHA
    assert result.head_sha == HEAD_SHA
    post = [call for call in transport.calls if call[0] == "POST"]
    assert post == [
        (
            "POST",
            "/repos/hesam-hakimi/hugan/pulls",
            {},
            {
                "base": "main",
                "body": "Exact approved publication.",
                "draft": True,
                "head": "uca/task-123",
                "title": "P2.3c qualification",
            },
        )
    ]


def test_github_creator_reuses_one_exact_open_draft() -> None:
    transport = _FakeGitHubTransport(pulls=[_pull_payload()])

    result = _creator(transport).ensure_draft(_request())

    assert result.created is False
    assert result.pull_request_id == "17"
    assert all(call[0] != "POST" for call in transport.calls)


@pytest.mark.parametrize(
    "update",
    [
        {"draft": False},
        {"body": "different intent"},
        {"title": "different title"},
        {"state": "closed"},
        {
            "head": {
                "ref": "uca/task-123",
                "repo": {"full_name": "hesam-hakimi/hugan"},
                "sha": "d" * 40,
            }
        },
    ],
)
def test_github_creator_rejects_conflicting_existing_pull_request(
    update: dict[str, object],
) -> None:
    transport = _FakeGitHubTransport(pulls=[_pull_payload(**update)])

    with pytest.raises(GitHubDraftPullRequestError) as captured:
        _creator(transport).ensure_draft(_request())

    assert captured.value.code == "draft_pr_intent_mismatch"
    assert all(call[0] != "POST" for call in transport.calls)


def test_github_creator_reconciles_create_race_only_to_exact_draft() -> None:
    class _RacingTransport(_FakeGitHubTransport):
        def request_json(self, method, path, *, query=None, payload=None):
            response = super().request_json(
                method,
                path,
                query=query,
                payload=payload,
            )
            if method == "POST":
                self.pulls = [_pull_payload()]
            return response

    transport = _RacingTransport(create_status=422)

    result = _creator(transport).ensure_draft(_request())

    assert result.created is False
    assert result.pull_request_id == "17"


@pytest.mark.parametrize(
    ("field_name", "value", "expected_stage"),
    [
        ("base_sha", "d" * 40, "base_preflight"),
        ("head_sha", "d" * 40, "head_preflight"),
    ],
)
def test_github_creator_fails_closed_on_ref_drift(
    field_name: str,
    value: str,
    expected_stage: str,
) -> None:
    transport = _FakeGitHubTransport(**{field_name: value})

    with pytest.raises(GitHubDraftPullRequestError) as captured:
        _creator(transport).ensure_draft(_request())

    assert captured.value.code == "ref_sha_mismatch"
    assert captured.value.stage == expected_stage
    assert all(call[0] != "POST" for call in transport.calls)


def test_github_creator_rechecks_both_refs_after_creation() -> None:
    class _BaseDriftAfterCreate(_FakeGitHubTransport):
        def request_json(self, method, path, *, query=None, payload=None):
            response = super().request_json(
                method,
                path,
                query=query,
                payload=payload,
            )
            if method == "POST":
                self.base_sha = "d" * 40
            return response

    with pytest.raises(GitHubDraftPullRequestError) as captured:
        _creator(_BaseDriftAfterCreate()).ensure_draft(_request())

    assert captured.value.code == "ref_sha_mismatch"
    assert captured.value.stage == "base_recheck"


def test_github_creator_rejects_unconfigured_repository_without_api_call() -> None:
    transport = _FakeGitHubTransport()

    with pytest.raises(GitHubDraftPullRequestError) as captured:
        _creator(transport).ensure_draft(
            _request(repository_url="https://github.com/hesam-hakimi/other.git")
        )

    assert captured.value.code == "repository_identity_mismatch"
    assert transport.calls == []


def test_github_creator_rejects_ambiguous_existing_drafts() -> None:
    transport = _FakeGitHubTransport(pulls=[_pull_payload(), _pull_payload(number=18)])

    with pytest.raises(GitHubDraftPullRequestError) as captured:
        _creator(transport).ensure_draft(_request())

    assert captured.value.code == "draft_pr_lookup_ambiguous"


def test_github_transport_redacts_network_failure(monkeypatch) -> None:
    secret = "super-secret-token"
    transport = UrllibGitHubApiTransport(token=secret)

    def _fail(*_args, **_kwargs):
        raise urllib.error.URLError(f"connection failed with {secret}")

    monkeypatch.setattr(transport._opener, "open", _fail)

    with pytest.raises(GitHubDraftPullRequestError) as captured:
        transport.request_json("GET", "/repos/hesam-hakimi/hugan")

    assert captured.value.code == "transport_failed"
    assert secret not in str(captured.value)
    assert captured.value.__cause__ is None


def test_github_factory_is_explicit_and_binds_stable_identities(monkeypatch) -> None:
    for name in (
        GITHUB_TOKEN_ENV,
        GITHUB_REPOSITORY_ENV,
        GITHUB_ACCOUNT_IDENTITY_ENV,
    ):
        monkeypatch.delenv(name, raising=False)
    with pytest.raises(RuntimeError, match=GITHUB_TOKEN_ENV):
        create_adapter()

    monkeypatch.setenv(GITHUB_TOKEN_ENV, "host-owned-secret")
    monkeypatch.setenv(GITHUB_REPOSITORY_ENV, "hesam-hakimi/hugan")
    monkeypatch.setenv(GITHUB_ACCOUNT_IDENTITY_ENV, "installation-100")

    adapter = create_adapter()
    capabilities = adapter.capabilities()

    assert capabilities.adapter_identity == "github-git:api.github.com:installation-100"
    assert capabilities.draft_pr_identity == "github:api.github.com:installation-100"
    assert capabilities.commit is True
    assert capabilities.push is True
    assert capabilities.draft_pr is True
    assert "host-owned-secret" not in repr(adapter.__dict__)
