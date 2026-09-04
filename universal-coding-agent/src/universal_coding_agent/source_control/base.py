from __future__ import annotations

import hashlib
import json
import re
import urllib.parse
from enum import StrEnum
from typing import Literal, Protocol, runtime_checkable

from pydantic import Field, field_validator, model_validator

from universal_coding_agent.core.models import FrozenModel, RepositorySpec
from universal_coding_agent.core.safe_models import (
    ApprovedChangeManifest,
    StructuredEditProposal,
    normalize_repository_path,
)

_HASH = re.compile(r"^[0-9a-f]{64}$")
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{2,127}$")
_BRANCH_COMPONENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def _credential_free_https_url(value: str, *, label: str) -> str:
    parsed = urllib.parse.urlsplit(value.strip())
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or not parsed.path
        or parsed.path == "/"
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError(f"{label} must be credential-free HTTPS")
    return urllib.parse.urlunsplit(parsed)


class PublicationAction(StrEnum):
    COMMIT = "commit"
    PUSH = "push"
    DRAFT_PR = "draft_pr"


class SourceControlCapabilities(FrozenModel):
    adapter_identity: str = Field(
        min_length=1,
        max_length=256,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9._:/@-]{0,255}$",
    )
    draft_pr_identity: str = Field(
        default="",
        max_length=256,
        pattern=r"^$|^[A-Za-z0-9][A-Za-z0-9._:/@-]{0,255}$",
    )
    commit: bool = False
    push: bool = False
    draft_pr: bool = False

    @model_validator(mode="after")
    def validate_hierarchy(self) -> SourceControlCapabilities:
        if self.draft_pr and not self.push:
            raise ValueError("draft PR capability requires push capability")
        if self.push and not self.commit:
            raise ValueError("push capability requires commit capability")
        if self.draft_pr and not self.draft_pr_identity:
            raise ValueError("draft PR capability requires a stable creator identity")
        if not self.draft_pr and self.draft_pr_identity:
            raise ValueError("draft PR identity requires draft PR capability")
        return self


def validate_head_branch(value: str) -> str:
    branch = value.strip()
    if branch.startswith("refs/heads/"):
        branch = branch.removeprefix("refs/heads/")
    if not branch or len(branch) > 240:
        raise ValueError("head branch must be between 1 and 240 characters")
    if any(ord(character) < 32 or ord(character) == 127 for character in branch):
        raise ValueError("head branch contains control characters")
    if (
        branch.startswith(("-", ".", "/"))
        or branch.endswith((".", "/"))
        or "//" in branch
        or ".." in branch
        or "@{" in branch
        or "\\" in branch
        or branch.endswith(".lock")
    ):
        raise ValueError("head branch is not a safe branch name")
    components = branch.split("/")
    if any(
        component.endswith(".lock") or not _BRANCH_COMPONENT.fullmatch(component)
        for component in components
    ):
        raise ValueError("head branch contains unsupported characters")
    return branch


def normalize_base_branch(value: str) -> str:
    normalized = value.strip()
    for prefix in ("refs/heads/", "refs/remotes/origin/", "origin/"):
        if normalized.startswith(prefix):
            return normalized.removeprefix(prefix)
    return normalized


def validate_base_branch(value: str) -> str:
    """Return the canonical branch name for an approved base ref.

    Pseudo-refs such as ``HEAD`` and arbitrary tag/SHA inputs must not be treated as
    branch authority. The repository preflight additionally proves that this name
    resolves through a local or origin-tracking branch at the approved base SHA.
    """

    base_branch = normalize_base_branch(value)
    if base_branch in {
        "HEAD",
        "FETCH_HEAD",
        "ORIG_HEAD",
        "MERGE_HEAD",
        "CHERRY_PICK_HEAD",
        "REBASE_HEAD",
    }:
        raise ValueError("base ref must name a branch, not a Git pseudo-ref")
    if value.strip().startswith("refs/") and not value.strip().startswith(
        ("refs/heads/", "refs/remotes/origin/")
    ):
        raise ValueError("base ref must name a local or origin-tracking branch")
    return validate_head_branch(base_branch)


def publication_intent_sha256(
    *,
    approval_sha256: str,
    patch_sha256: str,
    repository: RepositorySpec,
    manifest: ApprovedChangeManifest,
    changed_paths: tuple[str, ...],
    head_branch: str,
    action: PublicationAction,
    commit_message: str,
    draft_pr_title: str = "",
    draft_pr_body: str = "",
    adapter_identity: str,
    draft_pr_identity: str = "",
) -> str:
    """Hash the complete bounded source-control intent using canonical JSON."""

    payload = {
        "action": action.value,
        "adapter_identity": adapter_identity,
        "approval_sha256": approval_sha256,
        "base_ref": repository.base_ref,
        "base_sha": manifest.base_sha,
        "changed_paths": list(changed_paths),
        "commit_message": commit_message,
        "draft_pr_body": draft_pr_body,
        "draft_pr_title": draft_pr_title,
        "draft_pr_identity": draft_pr_identity,
        "head_branch": validate_head_branch(head_branch),
        "patch_sha256": patch_sha256,
        "repository_url": repository.url,
    }
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class ExactPublicationRequest(FrozenModel):
    publication_id: str = Field(pattern=r"^[0-9a-f]{64}$")
    approval_ref: str = Field(pattern=r"^artifact://[a-zA-Z0-9._/-]+$")
    approval_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    patch_ref: str = Field(pattern=r"^artifact://[a-zA-Z0-9._/-]+$")
    patch_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    intent_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    task_id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")
    thread_id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")
    repository: RepositorySpec
    sandbox_path: str = Field(min_length=1, max_length=4096)
    sandboxes_root: str = Field(min_length=1, max_length=4096)
    manifest: ApprovedChangeManifest
    edit_proposal: StructuredEditProposal
    patch_text: str = Field(min_length=1, max_length=2_000_000)
    changed_paths: tuple[str, ...] = Field(min_length=1, max_length=64)
    head_branch: str = Field(min_length=1, max_length=240)
    action: PublicationAction
    adapter_identity: str = Field(
        min_length=1,
        max_length=256,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9._:/@-]{0,255}$",
    )
    draft_pr_identity: str = Field(
        default="",
        max_length=256,
        pattern=r"^$|^[A-Za-z0-9][A-Za-z0-9._:/@-]{0,255}$",
    )
    commit_message: str = Field(min_length=1, max_length=500)
    draft_pr_title: str = Field(default="", max_length=200)
    draft_pr_body: str = Field(default="", max_length=20_000)

    @field_validator("sandbox_path", "sandboxes_root")
    @classmethod
    def validate_paths(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized or "\x00" in normalized:
            raise ValueError("source-control paths must be non-empty and NUL-free")
        return normalized

    @field_validator("changed_paths")
    @classmethod
    def validate_changed_paths(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(normalize_repository_path(value) for value in values)
        if len(normalized) != len(set(normalized)):
            raise ValueError("publication changed paths must be unique")
        return normalized

    @field_validator("head_branch")
    @classmethod
    def validate_branch(cls, value: str) -> str:
        return validate_head_branch(value)

    @field_validator("commit_message", "draft_pr_title", "draft_pr_body")
    @classmethod
    def no_nul(cls, value: str) -> str:
        if "\x00" in value:
            raise ValueError("publication metadata may not contain NUL bytes")
        return value.strip()

    @model_validator(mode="after")
    def validate_exact_binding(self) -> ExactPublicationRequest:
        patch_digest = hashlib.sha256(self.patch_text.encode("utf-8")).hexdigest()
        if patch_digest != self.patch_sha256:
            raise ValueError("publication patch text does not match patch_sha256")
        if tuple(self.edit_proposal.changed_paths) != self.changed_paths:
            raise ValueError("publication paths do not match the structured edit proposal")
        if set(self.changed_paths) - set(self.manifest.allowed_path_map()):
            raise ValueError("publication paths exceed the approved manifest")
        base_branch = validate_base_branch(self.repository.base_ref)
        if self.head_branch == base_branch:
            raise ValueError("publication head branch must differ from the base branch")
        if self.action is PublicationAction.DRAFT_PR:
            if (
                not self.draft_pr_title
                or not self.draft_pr_body
                or not self.draft_pr_identity
            ):
                raise ValueError("draft PR publication requires fixed title and body metadata")
        elif self.draft_pr_title or self.draft_pr_body or self.draft_pr_identity:
            raise ValueError("draft PR metadata is allowed only for draft PR publication")
        expected_intent = publication_intent_sha256(
            approval_sha256=self.approval_sha256,
            patch_sha256=self.patch_sha256,
            repository=self.repository,
            manifest=self.manifest,
            changed_paths=self.changed_paths,
            head_branch=self.head_branch,
            action=self.action,
            commit_message=self.commit_message,
            draft_pr_title=self.draft_pr_title,
            draft_pr_body=self.draft_pr_body,
            adapter_identity=self.adapter_identity,
            draft_pr_identity=self.draft_pr_identity,
        )
        if self.intent_sha256 != expected_intent:
            raise ValueError("publication intent hash does not match the bounded intent")
        expected_publication_id = hashlib.sha256(
            f"{self.approval_sha256}:{self.intent_sha256}".encode("ascii")
        ).hexdigest()
        if self.publication_id != expected_publication_id:
            raise ValueError("publication ID does not match approval and intent hashes")
        return self


class DraftPullRequestRequest(FrozenModel):
    publication_id: str = Field(pattern=r"^[0-9a-f]{64}$")
    repository: RepositorySpec
    base_branch: str = Field(min_length=1, max_length=240)
    base_sha: str = Field(pattern=r"^[0-9a-f]{40,64}$")
    head_branch: str = Field(min_length=1, max_length=240)
    head_sha: str = Field(pattern=r"^[0-9a-f]{40,64}$")
    title: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1, max_length=20_000)

    @field_validator("head_branch")
    @classmethod
    def validate_head(cls, value: str) -> str:
        return validate_head_branch(value)

    @field_validator("base_branch")
    @classmethod
    def validate_base(cls, value: str) -> str:
        return validate_head_branch(normalize_base_branch(value))


class DraftPullRequestResult(FrozenModel):
    provider: str = Field(min_length=1, max_length=64)
    pull_request_id: str = Field(min_length=1, max_length=256)
    url: str = Field(min_length=1, max_length=4096)
    draft: Literal[True] = True
    base_branch: str = Field(min_length=1, max_length=240)
    base_sha: str = Field(
        default="",
        pattern=r"^$|^[0-9a-f]{40,64}$",
        description="Approved base SHA; empty only when reading a pre-P2.3c receipt.",
    )
    head_branch: str = Field(min_length=1, max_length=240)
    head_sha: str = Field(pattern=r"^[0-9a-f]{40,64}$")
    created: bool

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        return _credential_free_https_url(value, label="Draft PR URL")


class PublicationPartialEffects(FrozenModel):
    commit_created: bool = False
    commit_sha: str = Field(default="", pattern=r"^$|^[0-9a-f]{40,64}$")
    local_ref_attempted: bool = Field(
        default=False,
        description="A local feature-ref compare-and-swap was attempted.",
    )
    local_ref_verified: bool = Field(
        default=False,
        description="The local feature ref was verified at the exact commit.",
    )
    local_ref_created: bool = False
    local_ref_updated: bool = False
    local_ref: str = ""
    push_attempted: bool = Field(
        default=False,
        description="A remote mutation command was attempted.",
    )
    push_verified: bool = Field(
        default=False,
        description="The exact remote ref was verified, including an idempotent no-op.",
    )
    remote_sha: str = Field(default="", pattern=r"^$|^[0-9a-f]{40,64}$")
    draft_pr_attempted: bool = False
    draft_pr_created: bool = False
    draft_pr_url: str = Field(default="", max_length=4096)

    @field_validator("draft_pr_url")
    @classmethod
    def validate_draft_pr_url(cls, value: str) -> str:
        if not value:
            return ""
        return _credential_free_https_url(value, label="partial Draft PR URL")

    @model_validator(mode="after")
    def validate_effect_relationships(self) -> PublicationPartialEffects:
        if self.local_ref_created and self.local_ref_updated:
            raise ValueError("a local ref cannot be both created and updated")
        if self.commit_created and not self.commit_sha:
            raise ValueError("a created commit requires its SHA")
        if self.local_ref_verified and not self.local_ref_attempted:
            raise ValueError("a verified local ref requires an attempted operation")
        if (self.local_ref_created or self.local_ref_updated) and not (
            self.local_ref_attempted and self.local_ref_verified
        ):
            raise ValueError("a local-ref mutation requires verified attempted state")
        if self.local_ref_attempted and (
            not self.local_ref or not self.commit_sha
        ):
            raise ValueError("a local-ref attempt requires its ref and commit SHA")
        if self.local_ref and not self.commit_sha:
            raise ValueError("a local ref requires its commit SHA")
        if self.push_verified != bool(self.remote_sha):
            raise ValueError("verified remote state requires exactly one remote SHA")
        if self.draft_pr_url and not self.draft_pr_attempted:
            raise ValueError("a Draft PR URL requires an attempted Draft PR operation")
        if self.draft_pr_created and (
            not self.draft_pr_attempted or not self.draft_pr_url
        ):
            raise ValueError("a created Draft PR requires its attempt and URL")
        return self


class SourceControlPublicationResult(FrozenModel):
    publication_id: str = Field(pattern=r"^[0-9a-f]{64}$")
    action: PublicationAction
    commit_sha: str = Field(pattern=r"^[0-9a-f]{40,64}$")
    tree_sha: str = Field(pattern=r"^[0-9a-f]{40,64}$")
    local_ref: str = Field(min_length=1, max_length=512)
    commit_created: bool = False
    local_ref_created: bool = False
    local_ref_updated: bool = False
    pushed: bool = Field(
        default=False,
        description="The exact remote ref was verified, including an idempotent no-op.",
    )
    push_performed: bool = Field(
        default=False,
        description="A remote mutation command was performed by this attempt.",
    )
    remote_before_sha: str = Field(default="", pattern=r"^$|^[0-9a-f]{40,64}$")
    remote_after_sha: str = Field(default="", pattern=r"^$|^[0-9a-f]{40,64}$")
    draft_pr: DraftPullRequestResult | None = None
    reused: bool = False

    @model_validator(mode="after")
    def validate_effect_relationships(self) -> SourceControlPublicationResult:
        if self.local_ref_created and self.local_ref_updated:
            raise ValueError("a local ref cannot be both created and updated")
        if self.push_performed and not self.pushed:
            raise ValueError("a performed push requires verified remote state")
        if self.pushed:
            if self.remote_after_sha != self.commit_sha:
                raise ValueError("verified remote state must equal the exact commit")
        elif self.remote_before_sha or self.remote_after_sha:
            raise ValueError("remote SHAs require verified remote state")
        if self.reused and (
            self.commit_created
            or self.local_ref_created
            or self.local_ref_updated
            or self.push_performed
            or (self.draft_pr is not None and self.draft_pr.created)
        ):
            raise ValueError("a reused publication cannot report a new mutation")
        return self


class SourceControlPublicationError(RuntimeError):
    """A redacted typed source-control failure with explicit partial-effect state."""

    def __init__(
        self,
        code: str,
        *,
        stage: str,
        cause_type: str = "",
        partial_effects: PublicationPartialEffects | None = None,
    ) -> None:
        if not _ID.fullmatch(code.replace(":", "_")):
            raise ValueError("source-control error code is invalid")
        if not _ID.fullmatch(stage.replace(":", "_")):
            raise ValueError("source-control error stage is invalid")
        self.code = code
        self.stage = stage
        self.cause_type = cause_type[:128]
        self.partial_effects = partial_effects or PublicationPartialEffects()
        super().__init__(f"source-control publication failed safely at {stage}: {code}")


@runtime_checkable
class DraftPullRequestCreator(Protocol):
    def ensure_draft(self, request: DraftPullRequestRequest) -> DraftPullRequestResult:
        """Return an existing exact Draft PR or create it idempotently."""


@runtime_checkable
class SourceControlAdapter(Protocol):
    def capabilities(self) -> SourceControlCapabilities:
        """Return fixed source-control capabilities before any side effect."""

    def publish_exact(
        self,
        request: ExactPublicationRequest,
    ) -> SourceControlPublicationResult:
        """Publish only the exact independently approved request."""
