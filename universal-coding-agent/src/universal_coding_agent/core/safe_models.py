from __future__ import annotations

import hashlib
import json
import re
from enum import StrEnum
from pathlib import PurePosixPath
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from universal_coding_agent.core.models import RepositorySpec, ReviewVerdict, TaskMode

_SHA = re.compile(r"^[0-9a-f]{40,64}$")
_HASH = re.compile(r"^[0-9a-f]{64}$")
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{1,63}$")
_DEFAULT_DENIED_PREFIXES = (
    ".git",
    ".ssh",
    ".env",
    ".venv",
    "venv",
    "node_modules",
    "secrets",
    "credentials",
)


class FrozenSafeModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ChangeOperation(StrEnum):
    CREATE = "create"
    MODIFY = "modify"


class ChangeScopeEntry(FrozenSafeModel):
    path: str = Field(min_length=1, max_length=1024)
    operation: ChangeOperation
    purpose: str = Field(min_length=1, max_length=2000)

    @field_validator("path")
    @classmethod
    def validate_path(cls, value: str) -> str:
        return normalize_repository_path(value)


class ApprovedChangeManifest(FrozenSafeModel):
    manifest_version: str = Field(default="1", pattern=r"^1$")
    base_sha: str
    plan_hash: str
    allowed_changes: tuple[ChangeScopeEntry, ...] = Field(min_length=1, max_length=64)
    denied_prefixes: tuple[str, ...] = _DEFAULT_DENIED_PREFIXES
    test_profiles: tuple[str, ...] = ()
    acceptance_criteria: tuple[str, ...] = Field(min_length=1)
    max_patch_bytes: int = Field(default=200_000, ge=1_024, le=2_000_000)
    max_changed_files: int = Field(default=16, ge=1, le=64)

    @field_validator("base_sha")
    @classmethod
    def validate_base_sha(cls, value: str) -> str:
        value = value.strip().lower()
        if not _SHA.fullmatch(value):
            raise ValueError("base_sha must be a 40-64 character lowercase hex SHA")
        return value

    @field_validator("plan_hash")
    @classmethod
    def validate_plan_hash(cls, value: str) -> str:
        value = value.strip().lower()
        if not _HASH.fullmatch(value):
            raise ValueError("plan_hash must be a 64 character lowercase hex hash")
        return value

    @field_validator("denied_prefixes")
    @classmethod
    def validate_denied_prefixes(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(normalize_repository_prefix(item) for item in values)
        if len(normalized) != len(set(normalized)):
            raise ValueError("denied_prefixes must be unique")
        return normalized

    @field_validator("test_profiles")
    @classmethod
    def validate_test_profiles(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(item.strip() for item in values)
        if any(not _ID.fullmatch(item) for item in normalized):
            raise ValueError("test profile IDs contain unsupported characters")
        if len(normalized) != len(set(normalized)):
            raise ValueError("test profile IDs must be unique")
        return normalized

    @model_validator(mode="after")
    def validate_scope(self) -> ApprovedChangeManifest:
        paths = [item.path for item in self.allowed_changes]
        if len(paths) != len(set(paths)):
            raise ValueError("allowed change paths must be unique")
        if len(paths) > self.max_changed_files:
            raise ValueError("allowed changes exceed max_changed_files")
        for path in paths:
            if any(path_is_within_prefix(path, prefix) for prefix in self.denied_prefixes):
                raise ValueError(f"allowed path is denied by policy: {path}")
        return self

    def canonical_hash(self) -> str:
        payload = self.model_dump(mode="json")
        encoded = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def allowed_path_map(self) -> dict[str, ChangeOperation]:
        return {item.path: item.operation for item in self.allowed_changes}


class TestProfile(FrozenSafeModel):
    __test__: ClassVar[bool] = False

    profile_id: str
    argv: tuple[str, ...] = Field(min_length=1, max_length=64)
    cwd: str = "."
    timeout_seconds: int = Field(default=300, ge=1, le=1800)
    output_limit: int = Field(default=20_000, ge=1_000, le=200_000)

    @field_validator("profile_id")
    @classmethod
    def validate_profile_id(cls, value: str) -> str:
        value = value.strip()
        if not _ID.fullmatch(value):
            raise ValueError("profile_id contains unsupported characters")
        return value

    @field_validator("argv")
    @classmethod
    def validate_argv(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(item.strip() for item in values)
        if any(not item or any(ord(char) < 32 for char in item) for item in normalized):
            raise ValueError("test argv contains an empty value or control character")
        return normalized

    @field_validator("cwd")
    @classmethod
    def validate_cwd(cls, value: str) -> str:
        value = value.strip().replace("\\", "/")
        if value == ".":
            return value
        return normalize_repository_path(value)


class SafeModePolicy(FrozenSafeModel):
    policy_version: str = Field(default="1", pattern=r"^1$")
    profiles: tuple[TestProfile, ...] = ()

    @model_validator(mode="after")
    def validate_profiles(self) -> SafeModePolicy:
        ids = [item.profile_id for item in self.profiles]
        if len(ids) != len(set(ids)):
            raise ValueError("policy profile IDs must be unique")
        return self

    def profile_map(self) -> dict[str, TestProfile]:
        return {item.profile_id: item for item in self.profiles}


class SafeTaskRequest(FrozenSafeModel):
    task_id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")
    thread_id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")
    title: str = Field(min_length=1, max_length=200)
    objective: str = Field(min_length=1, max_length=50_000)
    repository: RepositorySpec
    manifest: ApprovedChangeManifest
    policy: SafeModePolicy = Field(default_factory=SafeModePolicy)
    mode: TaskMode = TaskMode.SAFE
    require_scope_approval: bool = True
    metadata: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_safe_task(self) -> SafeTaskRequest:
        if self.mode is not TaskMode.SAFE:
            raise ValueError("safe task mode must be safe")
        if not self.require_scope_approval:
            raise ValueError("safe tasks require explicit human scope approval")
        policy_ids = set(self.policy.profile_map())
        unknown_profiles = set(self.manifest.test_profiles) - policy_ids
        if unknown_profiles:
            raise ValueError(
                f"manifest references unknown test profiles: {sorted(unknown_profiles)}"
            )
        return self


class PatchProposal(FrozenSafeModel):
    summary: str = Field(min_length=1, max_length=4000)
    unified_diff: str = Field(min_length=1, max_length=2_000_000)
    changed_paths: tuple[str, ...] = Field(min_length=1, max_length=64)
    requested_test_profiles: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()

    @field_validator("changed_paths")
    @classmethod
    def validate_changed_paths(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(normalize_repository_path(item) for item in values)
        if len(normalized) != len(set(normalized)):
            raise ValueError("changed_paths must be unique")
        return normalized

    @field_validator("requested_test_profiles")
    @classmethod
    def validate_requested_profiles(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(item.strip() for item in values)
        if any(not _ID.fullmatch(item) for item in normalized):
            raise ValueError("requested test profile IDs contain unsupported characters")
        if len(normalized) != len(set(normalized)):
            raise ValueError("requested test profile IDs must be unique")
        return normalized


class PatchValidationResult(FrozenSafeModel):
    valid: bool
    patch_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    changed_paths: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()


class TestExecutionResult(FrozenSafeModel):
    __test__: ClassVar[bool] = False

    profile_id: str
    passed: bool
    returncode: int
    duration_ms: int = Field(ge=0)
    output: str


class SafeReviewResult(FrozenSafeModel):
    verdict: ReviewVerdict
    requirement_findings: tuple[str, ...] = ()
    scope_findings: tuple[str, ...] = ()
    security_findings: tuple[str, ...] = ()
    test_findings: tuple[str, ...] = ()
    required_actions: tuple[str, ...] = ()
    confidence: str = Field(default="medium", pattern=r"^(low|medium|high)$")


def normalize_repository_path(value: str) -> str:
    raw = value.strip().replace("\\", "/")
    if not raw or any(ord(char) < 32 for char in raw):
        raise ValueError("repository path is empty or contains control characters")
    path = PurePosixPath(raw)
    if path.is_absolute() or raw.startswith("/") or ".." in path.parts:
        raise ValueError("repository path must be relative and contained")
    if any(part in {"", "."} for part in path.parts):
        raise ValueError("repository path must be canonical")
    normalized = path.as_posix()
    if normalized.startswith(".git/") or normalized == ".git":
        raise ValueError("repository path may not target .git")
    return normalized


def normalize_repository_prefix(value: str) -> str:
    raw = value.strip().replace("\\", "/").rstrip("/")
    if raw in {".git", ".ssh", ".env", ".venv", "venv", "node_modules", "secrets", "credentials"}:
        return raw
    return normalize_repository_path(raw)


def path_is_within_prefix(path: str, prefix: str) -> bool:
    return path == prefix or path.startswith(prefix + "/")


def safe_json(value: Any) -> str:
    return json.dumps(value, separators=(",", ":"), sort_keys=True, ensure_ascii=False)
