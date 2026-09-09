from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol

from universal_coding_agent.source_control.base import (
    DraftPullRequestRequest,
    DraftPullRequestResult,
    SourceControlAdapter,
)
from universal_coding_agent.source_control.git import GitSourceControlAdapter

_REPOSITORY = re.compile(
    r"^(?P<owner>[A-Za-z0-9](?:[A-Za-z0-9-]{0,38}))/(?P<repo>[A-Za-z0-9_.-]{1,100})$"
)
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:@/-]{0,127}$")
_SHA = re.compile(r"^[0-9a-f]{40,64}$")
_MAX_RESPONSE_BYTES = 1_000_000

GITHUB_TOKEN_ENV = "UCA_GITHUB_TOKEN"
GITHUB_REPOSITORY_ENV = "UCA_GITHUB_REPOSITORY"
GITHUB_ACCOUNT_IDENTITY_ENV = "UCA_GITHUB_ACCOUNT_IDENTITY"
GITHUB_API_URL_ENV = "UCA_GITHUB_API_URL"
GITHUB_WEB_URL_ENV = "UCA_GITHUB_WEB_URL"
GITHUB_TIMEOUT_ENV = "UCA_GITHUB_TIMEOUT_SECONDS"


class GitHubDraftPullRequestError(RuntimeError):
    """A bounded hosted-provider failure that never includes response or credential text."""

    def __init__(self, code: str, *, stage: str) -> None:
        self.code = code
        self.stage = stage
        super().__init__(f"GitHub Draft PR operation failed safely at {stage}: {code}")


@dataclass(frozen=True)
class GitHubApiResponse:
    status_code: int
    payload: object


class GitHubApiTransport(Protocol):
    def request_json(
        self,
        method: str,
        path: str,
        *,
        query: Mapping[str, str] | None = None,
        payload: Mapping[str, object] | None = None,
    ) -> GitHubApiResponse:
        """Perform one fixed GitHub JSON API operation."""


class UrllibGitHubApiTransport:
    """Small host-owned GitHub API transport with bounded, redacted failures."""

    def __init__(
        self,
        *,
        token: str,
        api_url: str = "https://api.github.com",
        timeout_seconds: int = 30,
    ) -> None:
        secret = token.strip()
        if not secret or any(
            ord(character) < 32 or ord(character) == 127 for character in secret
        ):
            raise ValueError("GitHub token is missing or invalid")
        if timeout_seconds < 1 or timeout_seconds > 300:
            raise ValueError("GitHub API timeout must be between 1 and 300 seconds")
        self._token = secret
        self.api_url = _validate_https_base_url(api_url, allow_path=True)
        self.timeout_seconds = timeout_seconds
        self._opener = urllib.request.build_opener(_RejectRedirectHandler())

    def request_json(
        self,
        method: str,
        path: str,
        *,
        query: Mapping[str, str] | None = None,
        payload: Mapping[str, object] | None = None,
    ) -> GitHubApiResponse:
        verb = method.upper()
        if verb not in {"GET", "POST"}:
            raise ValueError("GitHub transport supports only GET and POST")
        if not path.startswith("/") or "?" in path or "#" in path:
            raise ValueError("GitHub API path is invalid")
        encoded_query = urllib.parse.urlencode(dict(query or {}))
        url = f"{self.api_url}{path}"
        if encoded_query:
            url = f"{url}?{encoded_query}"
        body = None
        if payload is not None:
            body = json.dumps(
                dict(payload),
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            ).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=body,
            method=verb,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self._token}",
                "User-Agent": "universal-coding-agent-hosted-publication",
                "X-GitHub-Api-Version": "2022-11-28",
                **({"Content-Type": "application/json"} if body is not None else {}),
            },
        )
        try:
            with self._opener.open(request, timeout=self.timeout_seconds) as response:
                return GitHubApiResponse(
                    status_code=int(response.status),
                    payload=self._read_payload(response),
                )
        except urllib.error.HTTPError as exc:
            return GitHubApiResponse(
                status_code=int(exc.code),
                payload=self._read_payload(exc),
            )
        except (OSError, TimeoutError):
            raise GitHubDraftPullRequestError(
                "transport_failed",
                stage="github_api",
            ) from None

    @staticmethod
    def _read_payload(response) -> object:
        raw = response.read(_MAX_RESPONSE_BYTES + 1)
        if len(raw) > _MAX_RESPONSE_BYTES:
            raise GitHubDraftPullRequestError(
                "response_too_large",
                stage="github_api",
            )
        if not raw:
            return None
        try:
            return json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise GitHubDraftPullRequestError(
                "response_not_json",
                stage="github_api",
            ) from exc


class GitHubDraftPullRequestCreator:
    """Create or reconcile one exact same-repository GitHub Draft PR."""

    def __init__(
        self,
        *,
        transport: GitHubApiTransport,
        repository_full_name: str,
        account_identity: str,
        api_url: str = "https://api.github.com",
        web_url: str = "https://github.com",
    ) -> None:
        owner, repository = _parse_repository_full_name(repository_full_name)
        identity = account_identity.strip()
        if _IDENTITY.fullmatch(identity) is None:
            raise ValueError("GitHub account identity is invalid")
        self.transport = transport
        self.repository_full_name = f"{owner}/{repository}"
        self.owner = owner
        self.repository = repository
        self.api_url = _validate_https_base_url(api_url, allow_path=True)
        self.web_url = _validate_https_base_url(web_url, allow_path=False)
        self.web_host = urllib.parse.urlsplit(self.web_url).hostname or ""
        api_host = urllib.parse.urlsplit(self.api_url).hostname or ""
        self.identity = f"github:{api_host}:{identity}"

    def ensure_draft(self, request: DraftPullRequestRequest) -> DraftPullRequestResult:
        if not isinstance(request, DraftPullRequestRequest):
            raise TypeError("ensure_draft requires a DraftPullRequestRequest")
        if _repository_from_url(request.repository.url) != (
            self.web_host.casefold(),
            self.repository_full_name.casefold(),
        ):
            self._fail("repository_identity_mismatch", "repository_preflight")

        self._require_ref(request.base_branch, request.base_sha, stage="base_preflight")
        self._require_ref(request.head_branch, request.head_sha, stage="head_preflight")
        existing = self._find_existing(request)
        if existing is not None:
            self._require_ref(request.base_branch, request.base_sha, stage="base_recheck")
            self._require_ref(request.head_branch, request.head_sha, stage="head_recheck")
            return self._result(existing, request, created=False)

        response = self.transport.request_json(
            "POST",
            self._pulls_path,
            payload={
                "base": request.base_branch,
                "body": request.body,
                "draft": True,
                "head": request.head_branch,
                "title": request.title,
            },
        )
        if response.status_code == 422:
            existing = self._find_existing(request)
            if existing is None:
                self._fail("draft_pr_create_conflict", "create_draft_pr")
            self._require_ref(request.base_branch, request.base_sha, stage="base_recheck")
            self._require_ref(request.head_branch, request.head_sha, stage="head_recheck")
            return self._result(existing, request, created=False)
        if response.status_code != 201 or not isinstance(response.payload, dict):
            self._fail("draft_pr_create_failed", "create_draft_pr")
        self._require_ref(request.base_branch, request.base_sha, stage="base_recheck")
        self._require_ref(request.head_branch, request.head_sha, stage="head_recheck")
        return self._result(response.payload, request, created=True)

    @property
    def _pulls_path(self) -> str:
        owner = urllib.parse.quote(self.owner, safe="")
        repository = urllib.parse.quote(self.repository, safe="")
        return f"/repos/{owner}/{repository}/pulls"

    def _require_ref(self, branch: str, expected_sha: str, *, stage: str) -> None:
        reference = urllib.parse.quote(f"heads/{branch}", safe="")
        response = self.transport.request_json(
            "GET",
            f"/repos/{urllib.parse.quote(self.owner, safe='')}/"
            f"{urllib.parse.quote(self.repository, safe='')}/git/ref/{reference}",
        )
        if response.status_code != 200 or not isinstance(response.payload, dict):
            self._fail("ref_lookup_failed", stage)
        object_payload = response.payload.get("object")
        actual_sha = object_payload.get("sha") if isinstance(object_payload, dict) else None
        if not isinstance(actual_sha, str) or _SHA.fullmatch(actual_sha) is None:
            self._fail("ref_response_invalid", stage)
        if actual_sha != expected_sha:
            self._fail("ref_sha_mismatch", stage)

    def _find_existing(self, request: DraftPullRequestRequest) -> dict[str, object] | None:
        response = self.transport.request_json(
            "GET",
            self._pulls_path,
            query={
                "base": request.base_branch,
                "head": f"{self.owner}:{request.head_branch}",
                "per_page": "100",
                "state": "all",
            },
        )
        if response.status_code != 200 or not isinstance(response.payload, list):
            self._fail("draft_pr_lookup_failed", "lookup_draft_pr")
        if any(not isinstance(item, dict) for item in response.payload):
            self._fail("draft_pr_lookup_invalid", "lookup_draft_pr")
        candidates = [item for item in response.payload if isinstance(item, dict)]
        if len(candidates) > 1:
            self._fail("draft_pr_lookup_ambiguous", "lookup_draft_pr")
        if not candidates:
            return None
        candidate = candidates[0]
        self._validate_pull_request(candidate, request)
        return candidate

    def _result(
        self,
        payload: Mapping[str, object],
        request: DraftPullRequestRequest,
        *,
        created: bool,
    ) -> DraftPullRequestResult:
        self._validate_pull_request(payload, request)
        number = payload.get("number")
        url = payload.get("html_url")
        if not isinstance(number, int) or number < 1 or not isinstance(url, str):
            self._fail("draft_pr_response_invalid", "verify_draft_pr")
        parsed_url = urllib.parse.urlsplit(url)
        expected_path = f"/{self.owner}/{self.repository}/pull/{number}"
        if (
            parsed_url.scheme != "https"
            or (parsed_url.hostname or "").casefold() != self.web_host.casefold()
            or parsed_url.path.casefold() != expected_path.casefold()
            or parsed_url.username
            or parsed_url.password
            or parsed_url.query
            or parsed_url.fragment
        ):
            self._fail("draft_pr_url_mismatch", "verify_draft_pr")
        return DraftPullRequestResult(
            provider="github",
            pull_request_id=str(number),
            url=url,
            base_branch=request.base_branch,
            base_sha=request.base_sha,
            head_branch=request.head_branch,
            head_sha=request.head_sha,
            created=created,
        )

    def _validate_pull_request(
        self,
        payload: Mapping[str, object],
        request: DraftPullRequestRequest,
    ) -> None:
        head = payload.get("head")
        base = payload.get("base")
        head_repository = head.get("repo") if isinstance(head, dict) else None
        base_repository = base.get("repo") if isinstance(base, dict) else None
        exact = (
            payload.get("draft") is True
            and payload.get("state") == "open"
            and payload.get("title") == request.title
            and payload.get("body") == request.body
            and isinstance(head, dict)
            and head.get("ref") == request.head_branch
            and head.get("sha") == request.head_sha
            and isinstance(base, dict)
            and base.get("ref") == request.base_branch
            and base.get("sha") == request.base_sha
            and isinstance(head_repository, dict)
            and str(head_repository.get("full_name", "")).casefold()
            == self.repository_full_name.casefold()
            and isinstance(base_repository, dict)
            and str(base_repository.get("full_name", "")).casefold()
            == self.repository_full_name.casefold()
        )
        if not exact:
            self._fail("draft_pr_intent_mismatch", "verify_draft_pr")

    @staticmethod
    def _fail(code: str, stage: str) -> None:
        raise GitHubDraftPullRequestError(code, stage=stage)


def create_adapter() -> SourceControlAdapter:
    """Create the explicitly configured, host-owned GitHub publication adapter."""

    token = _required_environment(GITHUB_TOKEN_ENV)
    repository = _required_environment(GITHUB_REPOSITORY_ENV)
    account_identity = _required_environment(GITHUB_ACCOUNT_IDENTITY_ENV)
    api_url = os.getenv(GITHUB_API_URL_ENV, "https://api.github.com").strip()
    web_url = os.getenv(GITHUB_WEB_URL_ENV, "https://github.com").strip()
    timeout = _environment_timeout()
    transport = UrllibGitHubApiTransport(
        token=token,
        api_url=api_url,
        timeout_seconds=timeout,
    )
    creator = GitHubDraftPullRequestCreator(
        transport=transport,
        repository_full_name=repository,
        account_identity=account_identity,
        api_url=api_url,
        web_url=web_url,
    )
    return GitSourceControlAdapter(
        timeout_seconds=timeout,
        draft_pr_creator=creator,
        adapter_identity=f"github-git:{urllib.parse.urlsplit(api_url).hostname}:{account_identity}",
        draft_pr_identity=creator.identity,
    )


def _required_environment(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is required for the GitHub source-control adapter")
    return value


def _environment_timeout() -> int:
    raw = os.getenv(GITHUB_TIMEOUT_ENV, "30").strip()
    try:
        timeout = int(raw)
    except ValueError as exc:
        raise RuntimeError(f"{GITHUB_TIMEOUT_ENV} must be an integer") from exc
    if timeout < 1 or timeout > 300:
        raise RuntimeError(f"{GITHUB_TIMEOUT_ENV} must be between 1 and 300")
    return timeout


def _parse_repository_full_name(value: str) -> tuple[str, str]:
    match = _REPOSITORY.fullmatch(value.strip())
    if match is None or match.group("repo").endswith(".git"):
        raise ValueError("GitHub repository must use owner/name format")
    return match.group("owner"), match.group("repo")


def _repository_from_url(value: str) -> tuple[str, str]:
    raw = value.strip()
    if raw.startswith("git@"):
        match = re.fullmatch(
            r"git@(?P<host>[A-Za-z0-9.-]+):(?P<path>[^?#]+)",
            raw,
        )
        if match is None:
            return "", ""
        host = match.group("host")
        path = match.group("path")
    else:
        parsed = urllib.parse.urlsplit(raw)
        if parsed.scheme not in {"https", "ssh"} or not parsed.hostname:
            return "", ""
        if parsed.scheme == "https" and (parsed.username or parsed.password):
            return "", ""
        if parsed.scheme == "ssh" and parsed.username != "git":
            return "", ""
        if parsed.query or parsed.fragment:
            return "", ""
        host = parsed.hostname
        path = parsed.path.lstrip("/")
    if path.endswith(".git"):
        path = path[:-4]
    try:
        owner, repository = _parse_repository_full_name(path)
    except ValueError:
        return "", ""
    return host.casefold(), f"{owner}/{repository}".casefold()


def _validate_https_base_url(value: str, *, allow_path: bool) -> str:
    parsed = urllib.parse.urlsplit(value.strip())
    path = parsed.path.rstrip("/")
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
        or (path and not allow_path)
    ):
        raise ValueError("GitHub base URL must be credential-free HTTPS")
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, path, "", ""))


class _RejectRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, file_pointer, code, message, headers, new_url):
        return None
