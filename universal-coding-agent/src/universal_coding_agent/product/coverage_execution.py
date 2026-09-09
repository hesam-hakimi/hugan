from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import sqlite3
import subprocess
from enum import StrEnum
from pathlib import Path
from threading import RLock
from typing import Any, Literal

from pydantic import Field, ValidationError, field_validator, model_validator

from universal_coding_agent.core.cancellation import (
    CancellationRequested,
    CancellationSignal,
    PauseRequested,
)
from universal_coding_agent.core.models import FrozenModel, RepositorySpec
from universal_coding_agent.core.safe_models import SafeModePolicy, TestExecutionResult
from universal_coding_agent.product.coverage_evidence import (
    trusted_test_policy_sha256,
    trusted_test_profile_sha256,
)
from universal_coding_agent.product.coverage_selection import (
    CoverageBackedTestSelection,
    CoverageTestSelectionDisposition,
    CoverageTestSelectionFallbackReason,
    RepositoryCoverageSelectionError,
    RepositoryCoverageSelectionService,
)
from universal_coding_agent.safe.testing import (
    SafeTestRunner,
    validate_selected_test_ids,
)
from universal_coding_agent.sandbox.git import (
    GitSandboxManager,
    SandboxCheckoutState,
)
from universal_coding_agent.storage.artifacts import ArtifactStore

DEFAULT_COVERAGE_EXECUTION_PLAN_MAX_BYTES = 4_000_000
DEFAULT_COVERAGE_EXECUTION_APPROVAL_MAX_BYTES = 64_000
DEFAULT_COVERAGE_EXECUTION_RESULT_MAX_BYTES = 16_000_000
DEFAULT_COVERAGE_EXECUTION_MAX_PROFILES = 256
DEFAULT_COVERAGE_EXECUTION_MAX_SELECTED_TESTS = 100_000
DEFAULT_COVERAGE_EXECUTION_MAX_TOTAL_OUTPUT_CHARS = 2_000_000
DEFAULT_COVERAGE_EXECUTION_MAX_JSON_ITEMS = 250_000
DEFAULT_COVERAGE_EXECUTION_MAX_JSON_DEPTH = 16
COVERAGE_EXECUTION_POLICY_VERSION = "1"

_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{2,127}$")
_PROFILE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_OBJECT_ID = re.compile(r"^[0-9a-f]{40,64}$")


class RepositoryCoverageTestExecutionError(ValueError):
    """Approved selected-test execution cannot satisfy its safety contract."""


class CoverageTestExecutionMode(StrEnum):
    SELECTED_TESTS = "SELECTED_TESTS"
    FULL_PROFILE = "FULL_PROFILE"


class CoverageExecutionFallbackReason(StrEnum):
    SELECTION_FULL_PROFILE_FALLBACK = "selection_full_profile_fallback"
    PROFILE_NOT_SELECTION_CAPABLE = "profile_not_selection_capable"


class CoverageTestExecutionOutcome(StrEnum):
    PASSED = "PASSED"
    TEST_FAILED = "TEST_FAILED"
    SOURCE_DRIFT = "SOURCE_DRIFT"
    CANCELLED = "CANCELLED"
    EXECUTION_ERROR = "EXECUTION_ERROR"
    BLOCKED = "BLOCKED"


class CoverageTestExecutionFailureCode(StrEnum):
    BASE_SHA_DRIFT = "base_sha_drift"
    SOURCE_TREE_DRIFT = "source_tree_drift"
    TRACKED_WORKTREE_DIRTY = "tracked_worktree_dirty"
    TRUSTED_TEST_CANCELLED = "trusted_test_cancelled"
    TRUSTED_TEST_CONTROL_STOPPED = "trusted_test_control_stopped"
    TRUSTED_TEST_TIMEOUT = "trusted_test_timeout"
    TRUSTED_TEST_EXECUTION_ERROR = "trusted_test_execution_error"
    TEST_PROFILE_FAILED = "test_profile_failed"
    SOURCE_CHANGED_DURING_EXECUTION = "source_changed_during_execution"
    SANDBOX_VERIFICATION_FAILED = "sandbox_verification_failed"
    ROLLBACK_FAILED = "rollback_failed"


class CoverageTestExecutionPolicy(FrozenModel):
    """Operator-owned opt-in for profiles that accept positional test IDs."""

    schema_version: Literal["1"] = "1"
    selected_test_profile_ids: tuple[str, ...] = Field(
        default=(), max_length=DEFAULT_COVERAGE_EXECUTION_MAX_PROFILES
    )

    @field_validator("selected_test_profile_ids")
    @classmethod
    def validate_profile_ids(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        if values != tuple(sorted(set(values))):
            raise ValueError("selection-capable profile IDs must be unique and sorted")
        if any(_PROFILE_ID.fullmatch(value) is None for value in values):
            raise ValueError("selection-capable profile ID is invalid")
        return values

    def canonical_content(self) -> str:
        return _canonical_json(self.model_dump(mode="json"))

    def canonical_hash(self) -> str:
        return hashlib.sha256(self.canonical_content().encode("utf-8")).hexdigest()


class CoverageTestExecutionProfilePlan(FrozenModel):
    profile_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
    profile_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    mode: CoverageTestExecutionMode
    test_ids: tuple[str, ...] = Field(
        default=(), max_length=DEFAULT_COVERAGE_EXECUTION_MAX_SELECTED_TESTS
    )

    @field_validator("test_ids")
    @classmethod
    def validate_test_ids(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        if values:
            validate_selected_test_ids(values)
        return values

    @model_validator(mode="after")
    def validate_mode(self) -> CoverageTestExecutionProfilePlan:
        if self.mode is CoverageTestExecutionMode.SELECTED_TESTS and not self.test_ids:
            raise ValueError("selected-test execution requires test IDs")
        if self.mode is CoverageTestExecutionMode.FULL_PROFILE and self.test_ids:
            raise ValueError("full-profile execution cannot contain selected test IDs")
        return self


class CoverageTestCheckoutEvidence(FrozenModel):
    head_sha: str = Field(pattern=r"^[0-9a-f]{40,64}$")
    source_tree_oid: str = Field(pattern=r"^[0-9a-f]{40,64}$")
    tracked_worktree_clean: bool
    exact_snapshot_verified: bool


class CoverageTestExecutionPlan(FrozenModel):
    """Exact immutable execution intent; this artifact grants no execution authority."""

    schema_version: Literal["1"] = "1"
    plan_format: Literal["coverage-test-execution-plan-v1"] = (
        "coverage-test-execution-plan-v1"
    )
    execution_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]{2,127}$")
    project_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]{2,127}$")
    repository_url: str = Field(min_length=1, max_length=2048)
    base_ref: str = Field(min_length=1, max_length=256)
    target_base_sha: str = Field(pattern=r"^[0-9a-f]{40,64}$")
    source_tree_oid: str = Field(pattern=r"^[0-9a-f]{40,64}$")
    sandbox_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]{2,127}$")
    selection_ref: str = Field(pattern=r"^artifact://[A-Za-z0-9._/-]+$")
    selection_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    target_snapshot_ref: str = Field(pattern=r"^artifact://[A-Za-z0-9._/-]+$")
    target_snapshot_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    selection_disposition: CoverageTestSelectionDisposition
    selection_fallback_reasons: tuple[CoverageTestSelectionFallbackReason, ...] = ()
    trusted_test_policy_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    execution_policy_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    service_policy_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    execution_mode: CoverageTestExecutionMode
    fallback_reasons: tuple[CoverageExecutionFallbackReason, ...] = ()
    profiles: tuple[CoverageTestExecutionProfilePlan, ...] = Field(
        min_length=1, max_length=DEFAULT_COVERAGE_EXECUTION_MAX_PROFILES
    )
    requires_explicit_human_approval: Literal[True] = True
    authorizes_execution: Literal[False] = False
    trusted_profile_argv_only: Literal[True] = True
    shell_disabled: Literal[True] = True

    @field_validator("selection_fallback_reasons")
    @classmethod
    def validate_selection_fallback_reasons(
        cls, values: tuple[CoverageTestSelectionFallbackReason, ...]
    ) -> tuple[CoverageTestSelectionFallbackReason, ...]:
        if values != tuple(sorted(set(values), key=lambda item: item.value)):
            raise ValueError("selection fallback reasons must be unique and sorted")
        return values

    @field_validator("fallback_reasons")
    @classmethod
    def validate_fallback_reasons(
        cls, values: tuple[CoverageExecutionFallbackReason, ...]
    ) -> tuple[CoverageExecutionFallbackReason, ...]:
        if values != tuple(sorted(set(values), key=lambda item: item.value)):
            raise ValueError("execution fallback reasons must be unique and sorted")
        return values

    @field_validator("profiles")
    @classmethod
    def validate_profiles(
        cls, values: tuple[CoverageTestExecutionProfilePlan, ...]
    ) -> tuple[CoverageTestExecutionProfilePlan, ...]:
        profile_ids = tuple(item.profile_id for item in values)
        if profile_ids != tuple(sorted(set(profile_ids))):
            raise ValueError("execution-plan profiles must be unique and sorted")
        return values

    @model_validator(mode="after")
    def validate_contract(self) -> CoverageTestExecutionPlan:
        if self.sandbox_id != self.execution_id:
            raise ValueError("execution plan sandbox must match execution identity")
        profile_modes = {item.mode for item in self.profiles}
        if profile_modes != {self.execution_mode}:
            raise ValueError("every execution-plan profile must use the plan mode")
        if self.execution_mode is CoverageTestExecutionMode.SELECTED_TESTS:
            if self.fallback_reasons:
                raise ValueError("selected-test execution cannot contain fallback reasons")
            if self.selection_disposition is not CoverageTestSelectionDisposition.SELECTED:
                raise ValueError("selected-test execution requires a selected-test artifact")
        elif not self.fallback_reasons:
            raise ValueError("full-profile execution requires a fallback reason")
        if (
            self.selection_disposition
            is CoverageTestSelectionDisposition.FULL_PROFILE_FALLBACK
        ) != bool(self.selection_fallback_reasons):
            raise ValueError("selection disposition and fallback reasons conflict")
        return self

    def canonical_content(self) -> str:
        return _canonical_json(self.model_dump(mode="json"))

    def canonical_hash(self) -> str:
        return hashlib.sha256(self.canonical_content().encode("utf-8")).hexdigest()


class CoverageTestExecutionPlanResult(FrozenModel):
    plan_ref: str = Field(pattern=r"^artifact://[A-Za-z0-9._/-]+$")
    plan_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    plan: CoverageTestExecutionPlan
    replayed: bool = False


class CoverageTestExecutionApprovalReceipt(FrozenModel):
    schema_version: Literal["1"] = "1"
    approval_format: Literal["coverage-test-execution-human-approval-v1"] = (
        "coverage-test-execution-human-approval-v1"
    )
    execution_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]{2,127}$")
    project_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]{2,127}$")
    plan_ref: str = Field(pattern=r"^artifact://[A-Za-z0-9._/-]+$")
    plan_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    confirmed_plan_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    selection_ref: str = Field(pattern=r"^artifact://[A-Za-z0-9._/-]+$")
    selection_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    target_base_sha: str = Field(pattern=r"^[0-9a-f]{40,64}$")
    source_tree_oid: str = Field(pattern=r"^[0-9a-f]{40,64}$")
    trusted_test_policy_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    execution_policy_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    service_policy_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    explicit_human_confirmation: Literal[True] = True
    authorizes_execution: Literal[True] = True

    @model_validator(mode="after")
    def validate_confirmation(self) -> CoverageTestExecutionApprovalReceipt:
        if not hmac.compare_digest(self.plan_sha256, self.confirmed_plan_sha256):
            raise ValueError("approval confirmation does not match the execution plan")
        return self

    def canonical_content(self) -> str:
        return _canonical_json(self.model_dump(mode="json"))

    def canonical_hash(self) -> str:
        return hashlib.sha256(self.canonical_content().encode("utf-8")).hexdigest()


class CoverageTestExecutionApprovalResult(FrozenModel):
    approval_ref: str = Field(pattern=r"^artifact://[A-Za-z0-9._/-]+$")
    approval_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    approval: CoverageTestExecutionApprovalReceipt
    replayed: bool = False


class CoverageTestExecutionReceipt(FrozenModel):
    schema_version: Literal["1"] = "1"
    receipt_format: Literal["coverage-test-execution-result-v1"] = (
        "coverage-test-execution-result-v1"
    )
    execution_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]{2,127}$")
    project_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]{2,127}$")
    plan_ref: str = Field(pattern=r"^artifact://[A-Za-z0-9._/-]+$")
    plan_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    approval_ref: str = Field(pattern=r"^artifact://[A-Za-z0-9._/-]+$")
    approval_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    selection_ref: str = Field(pattern=r"^artifact://[A-Za-z0-9._/-]+$")
    selection_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    target_base_sha: str = Field(pattern=r"^[0-9a-f]{40,64}$")
    source_tree_oid: str = Field(pattern=r"^[0-9a-f]{40,64}$")
    trusted_test_policy_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    execution_policy_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    service_policy_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    execution_mode: CoverageTestExecutionMode
    outcome: CoverageTestExecutionOutcome
    profile_results: tuple[TestExecutionResult, ...] = Field(
        default=(), max_length=DEFAULT_COVERAGE_EXECUTION_MAX_PROFILES
    )
    failure_codes: tuple[CoverageTestExecutionFailureCode, ...] = ()
    before_checkout: CoverageTestCheckoutEvidence | None = None
    after_checkout: CoverageTestCheckoutEvidence | None = None
    rollback_checkout: CoverageTestCheckoutEvidence | None = None
    execution_complete: bool
    all_tests_passed: bool
    source_preserved: bool
    rollback_attempted: bool
    rollback_succeeded: bool
    approved_plan_executed: Literal[True] = True
    shell_disabled: Literal[True] = True

    @field_validator("profile_results")
    @classmethod
    def validate_profile_results(
        cls, values: tuple[TestExecutionResult, ...]
    ) -> tuple[TestExecutionResult, ...]:
        profile_ids = tuple(item.profile_id for item in values)
        if profile_ids != tuple(sorted(set(profile_ids))):
            raise ValueError("execution result profiles must be unique and sorted")
        return values

    @field_validator("failure_codes")
    @classmethod
    def validate_failure_codes(
        cls, values: tuple[CoverageTestExecutionFailureCode, ...]
    ) -> tuple[CoverageTestExecutionFailureCode, ...]:
        if values != tuple(sorted(set(values), key=lambda item: item.value)):
            raise ValueError("execution failure codes must be unique and sorted")
        return values

    @model_validator(mode="after")
    def validate_outcome(self) -> CoverageTestExecutionReceipt:
        if self.all_tests_passed and not self.execution_complete:
            raise ValueError("incomplete execution cannot report all tests passed")
        if self.all_tests_passed and any(not item.passed for item in self.profile_results):
            raise ValueError("failed profile conflicts with all-tests-passed evidence")
        if self.rollback_checkout is not None and not self.rollback_attempted:
            raise ValueError("rollback evidence requires a rollback attempt")
        if self.rollback_succeeded and self.rollback_checkout is None:
            raise ValueError("successful rollback requires verified rollback evidence")
        if self.rollback_attempted and self.source_preserved:
            raise ValueError("source-preserved execution cannot require rollback")
        if self.outcome is CoverageTestExecutionOutcome.PASSED:
            if not (
                self.execution_complete
                and self.all_tests_passed
                and self.source_preserved
                and not self.failure_codes
            ):
                raise ValueError("passed outcome requires complete clean evidence")
        else:
            if not self.failure_codes:
                raise ValueError("non-passing execution requires a failure code")
            if self.outcome is CoverageTestExecutionOutcome.BLOCKED:
                blocking_codes = {
                    CoverageTestExecutionFailureCode.BASE_SHA_DRIFT,
                    CoverageTestExecutionFailureCode.SOURCE_TREE_DRIFT,
                    CoverageTestExecutionFailureCode.TRACKED_WORKTREE_DIRTY,
                    CoverageTestExecutionFailureCode.SANDBOX_VERIFICATION_FAILED,
                }
                if (
                    self.execution_complete
                    or self.all_tests_passed
                    or self.source_preserved
                    or self.rollback_attempted
                    or self.profile_results
                    or not blocking_codes.intersection(self.failure_codes)
                ):
                    raise ValueError("blocked outcome conflicts with execution evidence")
            elif self.outcome is CoverageTestExecutionOutcome.SOURCE_DRIFT:
                if (
                    self.source_preserved
                    or not self.rollback_attempted
                    or CoverageTestExecutionFailureCode.SOURCE_CHANGED_DURING_EXECUTION
                    not in self.failure_codes
                ):
                    raise ValueError("source-drift outcome conflicts with checkout evidence")
            elif self.outcome is CoverageTestExecutionOutcome.CANCELLED:
                cancellation_codes = {
                    CoverageTestExecutionFailureCode.TRUSTED_TEST_CANCELLED,
                    CoverageTestExecutionFailureCode.TRUSTED_TEST_CONTROL_STOPPED,
                }
                if (
                    self.execution_complete
                    or self.all_tests_passed
                    or not self.source_preserved
                    or not cancellation_codes.intersection(self.failure_codes)
                ):
                    raise ValueError("cancelled outcome conflicts with execution evidence")
            elif self.outcome is CoverageTestExecutionOutcome.EXECUTION_ERROR:
                execution_error_codes = {
                    CoverageTestExecutionFailureCode.TRUSTED_TEST_TIMEOUT,
                    CoverageTestExecutionFailureCode.TRUSTED_TEST_EXECUTION_ERROR,
                }
                if (
                    self.execution_complete
                    or self.all_tests_passed
                    or not self.source_preserved
                    or not execution_error_codes.intersection(self.failure_codes)
                ):
                    raise ValueError(
                        "execution-error outcome conflicts with execution evidence"
                    )
            elif (
                not self.execution_complete
                or self.all_tests_passed
                or not self.source_preserved
                or CoverageTestExecutionFailureCode.TEST_PROFILE_FAILED
                not in self.failure_codes
                or not any(not item.passed for item in self.profile_results)
            ):
                raise ValueError("test-failed outcome conflicts with profile evidence")
        return self

    def canonical_content(self) -> str:
        return _canonical_json(self.model_dump(mode="json"))

    def canonical_hash(self) -> str:
        return hashlib.sha256(self.canonical_content().encode("utf-8")).hexdigest()


class CoverageTestExecutionResult(FrozenModel):
    result_ref: str = Field(pattern=r"^artifact://[A-Za-z0-9._/-]+$")
    result_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    receipt: CoverageTestExecutionReceipt
    replayed: bool = False


class _ExecutionStatus(StrEnum):
    PREPARING = "preparing"
    PREPARED = "prepared"
    APPROVED = "approved"
    RUNNING = "running"
    COMPLETED = "completed"
    PREPARATION_FAILED = "preparation_failed"


class _ExecutionState(FrozenModel):
    execution_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]{2,127}$")
    project_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]{2,127}$")
    request_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    status: _ExecutionStatus
    plan_ref: str = Field(default="", pattern=r"^$|^artifact://[A-Za-z0-9._/-]+$")
    plan_sha256: str = Field(default="", pattern=r"^$|^[0-9a-f]{64}$")
    approval_ref: str = Field(default="", pattern=r"^$|^artifact://[A-Za-z0-9._/-]+$")
    approval_sha256: str = Field(default="", pattern=r"^$|^[0-9a-f]{64}$")
    result_ref: str = Field(default="", pattern=r"^$|^artifact://[A-Za-z0-9._/-]+$")
    result_sha256: str = Field(default="", pattern=r"^$|^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_shape(self) -> _ExecutionState:
        pairs = (
            bool(self.plan_ref) == bool(self.plan_sha256),
            bool(self.approval_ref) == bool(self.approval_sha256),
            bool(self.result_ref) == bool(self.result_sha256),
        )
        if not all(pairs):
            raise ValueError("execution-state artifact references are incomplete")
        if self.status in {_ExecutionStatus.PREPARING, _ExecutionStatus.PREPARATION_FAILED}:
            if self.plan_ref or self.approval_ref or self.result_ref:
                raise ValueError("unprepared execution state contains artifact references")
        else:
            if not self.plan_ref:
                raise ValueError("prepared execution state is missing its plan")
            if self.status is _ExecutionStatus.PREPARED and self.approval_ref:
                raise ValueError("unapproved execution state contains an approval")
            if self.status in {
                _ExecutionStatus.APPROVED,
                _ExecutionStatus.RUNNING,
                _ExecutionStatus.COMPLETED,
            } and not self.approval_ref:
                raise ValueError("approved execution state is missing its approval")
            if self.status is _ExecutionStatus.COMPLETED and not self.result_ref:
                raise ValueError("completed execution state is missing its result")
            if self.status is not _ExecutionStatus.COMPLETED and self.result_ref:
                raise ValueError("unfinished execution state contains a result")
        return self


class RepositoryCoverageTestExecutionService:
    """Prepare, approve, and execute one exact selection in an isolated sandbox."""

    _STATE_COLUMNS = (
        "execution_id",
        "project_id",
        "request_sha256",
        "status",
        "plan_ref",
        "plan_sha256",
        "approval_ref",
        "approval_sha256",
        "result_ref",
        "result_sha256",
    )

    def __init__(
        self,
        database_path: Path,
        artifacts: ArtifactStore,
        coverage_selection: RepositoryCoverageSelectionService,
        sandbox_manager: GitSandboxManager,
        *,
        test_runner: SafeTestRunner | None = None,
        plan_max_bytes: int = DEFAULT_COVERAGE_EXECUTION_PLAN_MAX_BYTES,
        approval_max_bytes: int = DEFAULT_COVERAGE_EXECUTION_APPROVAL_MAX_BYTES,
        result_max_bytes: int = DEFAULT_COVERAGE_EXECUTION_RESULT_MAX_BYTES,
        max_profiles: int = DEFAULT_COVERAGE_EXECUTION_MAX_PROFILES,
        max_selected_tests: int = DEFAULT_COVERAGE_EXECUTION_MAX_SELECTED_TESTS,
        max_total_output_chars: int = DEFAULT_COVERAGE_EXECUTION_MAX_TOTAL_OUTPUT_CHARS,
        max_json_items: int = DEFAULT_COVERAGE_EXECUTION_MAX_JSON_ITEMS,
        max_json_depth: int = DEFAULT_COVERAGE_EXECUTION_MAX_JSON_DEPTH,
    ) -> None:
        limits = (
            plan_max_bytes,
            approval_max_bytes,
            result_max_bytes,
            max_profiles,
            max_selected_tests,
            max_total_output_chars,
            max_json_items,
            max_json_depth,
        )
        if any(type(limit) is not int or limit < 1 for limit in limits):
            raise ValueError("coverage-test execution limits must be positive integers")
        if max_profiles > DEFAULT_COVERAGE_EXECUTION_MAX_PROFILES:
            raise ValueError("coverage-test execution profile limit exceeds schema maximum")
        if max_selected_tests > DEFAULT_COVERAGE_EXECUTION_MAX_SELECTED_TESTS:
            raise ValueError("selected-test execution limit exceeds schema maximum")
        self.database_path = database_path.resolve()
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.artifacts = artifacts
        self.coverage_selection = coverage_selection
        self.sandbox_manager = sandbox_manager
        self.test_runner = test_runner
        self.plan_max_bytes = plan_max_bytes
        self.approval_max_bytes = approval_max_bytes
        self.result_max_bytes = result_max_bytes
        self.max_profiles = max_profiles
        self.max_selected_tests = max_selected_tests
        self.max_total_output_chars = max_total_output_chars
        self.max_json_items = max_json_items
        self.max_json_depth = max_json_depth
        self._lock = RLock()
        self.connection = sqlite3.connect(
            self.database_path,
            check_same_thread=False,
            isolation_level=None,
        )
        try:
            os.chmod(self.database_path, 0o600)
        except OSError:
            pass
        self.connection.row_factory = sqlite3.Row
        self._initialize_database()

    def close(self) -> None:
        self.connection.close()

    def prepare_execution(
        self,
        *,
        execution_id: str,
        project_id: str,
        repository: RepositorySpec,
        trusted_test_policy: SafeModePolicy,
        execution_policy: CoverageTestExecutionPolicy,
        selection_ref: str,
        selection_sha256: str,
    ) -> CoverageTestExecutionPlanResult:
        self._validate_ids(execution_id=execution_id, project_id=project_id)
        selection = self._verified_selection(selection_ref, selection_sha256)
        policy_sha256 = trusted_test_policy_sha256(trusted_test_policy)
        execution_policy_sha256 = execution_policy.canonical_hash()
        self._validate_prepare_inputs(
            project_id=project_id,
            repository=repository,
            trusted_test_policy=trusted_test_policy,
            execution_policy=execution_policy,
            selection=selection,
            policy_sha256=policy_sha256,
        )
        request_sha256 = self._request_sha256(
            execution_id=execution_id,
            project_id=project_id,
            repository=repository,
            selection_ref=selection_ref,
            selection_sha256=selection_sha256,
            trusted_test_policy_sha256=policy_sha256,
            execution_policy_sha256=execution_policy_sha256,
        )
        with self._lock:
            self.connection.execute("BEGIN IMMEDIATE")
            try:
                existing = self._state(execution_id)
                if existing is not None:
                    self.connection.commit()
                    return self._replay_plan(
                        existing,
                        request_sha256=request_sha256,
                        selection=selection,
                        trusted_test_policy=trusted_test_policy,
                        execution_policy=execution_policy,
                    )
                self.connection.execute(
                    """
                    INSERT INTO coverage_test_executions (
                        execution_id, project_id, request_sha256, status,
                        plan_ref, plan_sha256, approval_ref, approval_sha256,
                        result_ref, result_sha256
                    ) VALUES (?, ?, ?, ?, '', '', '', '', '', '')
                    """,
                    (
                        execution_id,
                        project_id,
                        request_sha256,
                        _ExecutionStatus.PREPARING.value,
                    ),
                )
                self.connection.commit()
            except BaseException:
                self.connection.rollback()
                raise

        try:
            sandbox = self.sandbox_manager.prepare(execution_id, repository)
            checkout = self.sandbox_manager.inspect_checkout(Path(sandbox.path))
            if (
                sandbox.repository_url != selection.repository_url
                or sandbox.base_ref != selection.base_ref
                or sandbox.base_sha != selection.target_base_sha
                or checkout.head_sha != selection.target_base_sha
                or not checkout.tracked_worktree_clean
            ):
                raise RepositoryCoverageTestExecutionError(
                    "prepared sandbox does not match the selected exact Base"
                )
            verified_tree_oid = (
                self.coverage_selection.coverage_evidence.verify_exact_snapshot_source(
                    project_id=project_id,
                    root=Path(sandbox.path),
                    expected_snapshot_ref=selection.target_snapshot_ref,
                    expected_snapshot_sha256=selection.target_snapshot_sha256,
                )
            )
            if checkout.source_tree_oid != verified_tree_oid:
                raise RepositoryCoverageTestExecutionError(
                    "prepared sandbox does not match the selected exact Base"
                )
            plan = self._build_plan(
                execution_id=execution_id,
                project_id=project_id,
                selection_ref=selection_ref,
                selection_sha256=selection_sha256,
                selection=selection,
                trusted_test_policy=trusted_test_policy,
                execution_policy=execution_policy,
                checkout=checkout,
            )
            recorded = self._write_plan(plan)
        except BaseException as exc:
            self._mark_preparation_failed(execution_id, request_sha256)
            if isinstance(exc, RepositoryCoverageTestExecutionError):
                raise
            raise RepositoryCoverageTestExecutionError(
                "coverage-test execution preparation failed safely"
            ) from exc

        with self._lock:
            self.connection.execute("BEGIN IMMEDIATE")
            try:
                cursor = self.connection.execute(
                    """
                    UPDATE coverage_test_executions
                    SET status = ?, plan_ref = ?, plan_sha256 = ?
                    WHERE execution_id = ? AND request_sha256 = ? AND status = ?
                    """,
                    (
                        _ExecutionStatus.PREPARED.value,
                        recorded.plan_ref,
                        recorded.plan_sha256,
                        execution_id,
                        request_sha256,
                        _ExecutionStatus.PREPARING.value,
                    ),
                )
                if cursor.rowcount != 1:
                    raise RepositoryCoverageTestExecutionError(
                        "execution-plan state changed during preparation"
                    )
                self.connection.commit()
            except BaseException:
                self.connection.rollback()
                raise
        return recorded

    def approve_execution(
        self,
        *,
        execution_id: str,
        expected_plan_ref: str,
        expected_plan_sha256: str,
        confirmed_plan_sha256: str,
        confirmed: bool,
    ) -> CoverageTestExecutionApprovalResult:
        if confirmed is not True:
            raise RepositoryCoverageTestExecutionError(
                "explicit human confirmation of the execution plan is required"
            )
        plan = self.verified_plan(expected_plan_ref, expected_plan_sha256)
        if plan.execution_id != execution_id or not hmac.compare_digest(
            plan.canonical_hash(), confirmed_plan_sha256
        ):
            raise RepositoryCoverageTestExecutionError(
                "execution-plan approval confirmation does not match"
            )
        self._verified_selection_for_plan(plan)
        approval = CoverageTestExecutionApprovalReceipt(
            execution_id=plan.execution_id,
            project_id=plan.project_id,
            plan_ref=expected_plan_ref,
            plan_sha256=expected_plan_sha256,
            confirmed_plan_sha256=confirmed_plan_sha256,
            selection_ref=plan.selection_ref,
            selection_sha256=plan.selection_sha256,
            target_base_sha=plan.target_base_sha,
            source_tree_oid=plan.source_tree_oid,
            trusted_test_policy_sha256=plan.trusted_test_policy_sha256,
            execution_policy_sha256=plan.execution_policy_sha256,
            service_policy_sha256=plan.service_policy_sha256,
        )
        recorded = self._write_approval(approval)
        with self._lock:
            self.connection.execute("BEGIN IMMEDIATE")
            try:
                state = self._required_state(execution_id)
                self._verify_state_plan(
                    state,
                    plan,
                    expected_plan_ref,
                    expected_plan_sha256,
                )
                if state.status in {
                    _ExecutionStatus.APPROVED,
                    _ExecutionStatus.RUNNING,
                    _ExecutionStatus.COMPLETED,
                }:
                    if (
                        state.approval_ref != recorded.approval_ref
                        or not hmac.compare_digest(
                            state.approval_sha256, recorded.approval_sha256
                        )
                    ):
                        raise RepositoryCoverageTestExecutionError(
                            "execution already has a different approval"
                        )
                    self.connection.commit()
                    return recorded.model_copy(update={"replayed": True})
                if state.status is not _ExecutionStatus.PREPARED:
                    raise RepositoryCoverageTestExecutionError(
                        "execution is not awaiting approval"
                    )
                cursor = self.connection.execute(
                    """
                    UPDATE coverage_test_executions
                    SET status = ?, approval_ref = ?, approval_sha256 = ?
                    WHERE execution_id = ? AND status = ?
                      AND plan_ref = ? AND plan_sha256 = ?
                    """,
                    (
                        _ExecutionStatus.APPROVED.value,
                        recorded.approval_ref,
                        recorded.approval_sha256,
                        execution_id,
                        _ExecutionStatus.PREPARED.value,
                        expected_plan_ref,
                        expected_plan_sha256,
                    ),
                )
                if cursor.rowcount != 1:
                    raise RepositoryCoverageTestExecutionError(
                        "execution approval state changed concurrently"
                    )
                self.connection.commit()
            except BaseException:
                self.connection.rollback()
                raise
        return recorded

    def execute_approved(
        self,
        *,
        execution_id: str,
        expected_plan_ref: str,
        expected_plan_sha256: str,
        expected_approval_ref: str,
        expected_approval_sha256: str,
        trusted_test_policy: SafeModePolicy,
        execution_policy: CoverageTestExecutionPolicy,
        cancellation: CancellationSignal | None = None,
    ) -> CoverageTestExecutionResult:
        plan = self.verified_plan(expected_plan_ref, expected_plan_sha256)
        approval = self.verified_approval(
            expected_approval_ref,
            expected_approval_sha256,
        )
        if plan.execution_id != execution_id:
            raise RepositoryCoverageTestExecutionError(
                "execution identity does not match the approved plan"
            )
        self._verify_approval_binding(approval, plan)
        selection = self._verified_selection_for_plan(plan)
        self._verify_execution_inputs(
            plan=plan,
            selection=selection,
            trusted_test_policy=trusted_test_policy,
            execution_policy=execution_policy,
        )

        with self._lock:
            self.connection.execute("BEGIN IMMEDIATE")
            try:
                state = self._required_state(execution_id)
                self._verify_state_plan(
                    state,
                    plan,
                    expected_plan_ref,
                    expected_plan_sha256,
                )
                self._verify_state_approval(
                    state,
                    expected_approval_ref,
                    expected_approval_sha256,
                )
                if state.status is _ExecutionStatus.COMPLETED:
                    self.connection.commit()
                    result = self._result_from_state(state)
                    return result.model_copy(update={"replayed": True})
                if state.status is _ExecutionStatus.RUNNING:
                    raise RepositoryCoverageTestExecutionError(
                        "execution is already running or requires explicit recovery"
                    )
                if state.status is not _ExecutionStatus.APPROVED:
                    raise RepositoryCoverageTestExecutionError(
                        "execution does not have an unconsumed approval"
                    )
                cursor = self.connection.execute(
                    """
                    UPDATE coverage_test_executions SET status = ?
                    WHERE execution_id = ? AND status = ?
                      AND plan_ref = ? AND plan_sha256 = ?
                      AND approval_ref = ? AND approval_sha256 = ?
                    """,
                    (
                        _ExecutionStatus.RUNNING.value,
                        execution_id,
                        _ExecutionStatus.APPROVED.value,
                        expected_plan_ref,
                        expected_plan_sha256,
                        expected_approval_ref,
                        expected_approval_sha256,
                    ),
                )
                if cursor.rowcount != 1:
                    raise RepositoryCoverageTestExecutionError(
                        "execution approval was consumed concurrently"
                    )
                self.connection.commit()
            except BaseException:
                self.connection.rollback()
                raise

        receipt = self._run_approved_plan(
            plan=plan,
            approval=approval,
            trusted_test_policy=trusted_test_policy,
            cancellation=cancellation,
        )
        recorded = self._write_result(receipt)
        with self._lock:
            self.connection.execute("BEGIN IMMEDIATE")
            try:
                cursor = self.connection.execute(
                    """
                    UPDATE coverage_test_executions
                    SET status = ?, result_ref = ?, result_sha256 = ?
                    WHERE execution_id = ? AND status = ?
                      AND plan_ref = ? AND plan_sha256 = ?
                      AND approval_ref = ? AND approval_sha256 = ?
                    """,
                    (
                        _ExecutionStatus.COMPLETED.value,
                        recorded.result_ref,
                        recorded.result_sha256,
                        execution_id,
                        _ExecutionStatus.RUNNING.value,
                        expected_plan_ref,
                        expected_plan_sha256,
                        expected_approval_ref,
                        expected_approval_sha256,
                    ),
                )
                if cursor.rowcount != 1:
                    raise RepositoryCoverageTestExecutionError(
                        "execution result state changed before finalization"
                    )
                self.connection.commit()
            except BaseException:
                self.connection.rollback()
                raise
        return recorded

    def verified_plan(
        self, plan_ref: str, plan_sha256: str
    ) -> CoverageTestExecutionPlan:
        value = self._load_bounded_json(
            plan_ref,
            plan_sha256,
            max_bytes=self.plan_max_bytes,
            context="coverage-test execution plan",
        )
        try:
            plan = CoverageTestExecutionPlan.model_validate(value)
        except ValidationError as exc:
            raise RepositoryCoverageTestExecutionError(
                "coverage-test execution plan failed bounded validation"
            ) from exc
        if not hmac.compare_digest(plan.canonical_hash(), plan_sha256):
            raise RepositoryCoverageTestExecutionError(
                "coverage-test execution plan canonical hash does not match"
            )
        if not hmac.compare_digest(plan.service_policy_sha256, self._policy_sha256()):
            raise RepositoryCoverageTestExecutionError(
                "coverage-test execution service policy does not match"
            )
        if len(plan.profiles) > self.max_profiles or sum(
            len(item.test_ids) for item in plan.profiles
        ) > self.max_selected_tests:
            raise RepositoryCoverageTestExecutionError(
                "coverage-test execution plan exceeds configured limits"
            )
        return plan

    def verified_approval(
        self, approval_ref: str, approval_sha256: str
    ) -> CoverageTestExecutionApprovalReceipt:
        value = self._load_bounded_json(
            approval_ref,
            approval_sha256,
            max_bytes=self.approval_max_bytes,
            context="coverage-test execution approval",
        )
        try:
            approval = CoverageTestExecutionApprovalReceipt.model_validate(value)
        except ValidationError as exc:
            raise RepositoryCoverageTestExecutionError(
                "coverage-test execution approval failed bounded validation"
            ) from exc
        if not hmac.compare_digest(approval.canonical_hash(), approval_sha256):
            raise RepositoryCoverageTestExecutionError(
                "coverage-test execution approval canonical hash does not match"
            )
        if not hmac.compare_digest(
            approval.service_policy_sha256, self._policy_sha256()
        ):
            raise RepositoryCoverageTestExecutionError(
                "coverage-test execution approval policy does not match"
            )
        return approval

    def verified_result(
        self, result_ref: str, result_sha256: str
    ) -> CoverageTestExecutionReceipt:
        value = self._load_bounded_json(
            result_ref,
            result_sha256,
            max_bytes=self.result_max_bytes,
            context="coverage-test execution result",
        )
        try:
            receipt = CoverageTestExecutionReceipt.model_validate(value)
        except ValidationError as exc:
            raise RepositoryCoverageTestExecutionError(
                "coverage-test execution result failed bounded validation"
            ) from exc
        if not hmac.compare_digest(receipt.canonical_hash(), result_sha256):
            raise RepositoryCoverageTestExecutionError(
                "coverage-test execution result canonical hash does not match"
            )
        if not hmac.compare_digest(receipt.service_policy_sha256, self._policy_sha256()):
            raise RepositoryCoverageTestExecutionError(
                "coverage-test execution result policy does not match"
            )
        plan = self.verified_plan(receipt.plan_ref, receipt.plan_sha256)
        approval = self.verified_approval(
            receipt.approval_ref,
            receipt.approval_sha256,
        )
        self._verify_approval_binding(approval, plan)
        self._verify_result_binding(receipt, plan)
        return receipt

    def _initialize_database(self) -> None:
        with self._lock:
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS coverage_test_executions (
                    execution_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    request_sha256 TEXT NOT NULL,
                    status TEXT NOT NULL,
                    plan_ref TEXT NOT NULL,
                    plan_sha256 TEXT NOT NULL,
                    approval_ref TEXT NOT NULL,
                    approval_sha256 TEXT NOT NULL,
                    result_ref TEXT NOT NULL,
                    result_sha256 TEXT NOT NULL
                )
                """
            )
            columns = tuple(
                row[1]
                for row in self.connection.execute(
                    "PRAGMA table_info(coverage_test_executions)"
                )
            )
            if columns != self._STATE_COLUMNS:
                raise RepositoryCoverageTestExecutionError(
                    "coverage-test execution state schema is incompatible"
                )

    def _build_plan(
        self,
        *,
        execution_id: str,
        project_id: str,
        selection_ref: str,
        selection_sha256: str,
        selection: CoverageBackedTestSelection,
        trusted_test_policy: SafeModePolicy,
        execution_policy: CoverageTestExecutionPolicy,
        checkout: SandboxCheckoutState,
    ) -> CoverageTestExecutionPlan:
        requested = selection.requested_profile_ids
        selection_capable = set(execution_policy.selected_test_profile_ids)
        fallback_reasons: tuple[CoverageExecutionFallbackReason, ...]
        if (
            selection.disposition is CoverageTestSelectionDisposition.SELECTED
            and set(requested).issubset(selection_capable)
        ):
            mode = CoverageTestExecutionMode.SELECTED_TESTS
            fallback_reasons = ()
        elif selection.disposition is CoverageTestSelectionDisposition.SELECTED:
            mode = CoverageTestExecutionMode.FULL_PROFILE
            fallback_reasons = (
                CoverageExecutionFallbackReason.PROFILE_NOT_SELECTION_CAPABLE,
            )
        else:
            mode = CoverageTestExecutionMode.FULL_PROFILE
            fallback_reasons = (
                CoverageExecutionFallbackReason.SELECTION_FULL_PROFILE_FALLBACK,
            )

        profiles = trusted_test_policy.profile_map()
        selected = {item.profile_id: item.test_ids for item in selection.selected_profiles}
        profile_plans = tuple(
            CoverageTestExecutionProfilePlan(
                profile_id=profile_id,
                profile_sha256=trusted_test_profile_sha256(profiles[profile_id]),
                mode=mode,
                test_ids=(
                    validate_selected_test_ids(selected[profile_id])
                    if mode is CoverageTestExecutionMode.SELECTED_TESTS
                    else ()
                ),
            )
            for profile_id in requested
        )
        return CoverageTestExecutionPlan(
            execution_id=execution_id,
            project_id=project_id,
            repository_url=selection.repository_url,
            base_ref=selection.base_ref,
            target_base_sha=selection.target_base_sha,
            source_tree_oid=checkout.source_tree_oid,
            sandbox_id=execution_id,
            selection_ref=selection_ref,
            selection_sha256=selection_sha256,
            target_snapshot_ref=selection.target_snapshot_ref,
            target_snapshot_sha256=selection.target_snapshot_sha256,
            selection_disposition=selection.disposition,
            selection_fallback_reasons=selection.fallback_reasons,
            trusted_test_policy_sha256=trusted_test_policy_sha256(
                trusted_test_policy
            ),
            execution_policy_sha256=execution_policy.canonical_hash(),
            service_policy_sha256=self._policy_sha256(),
            execution_mode=mode,
            fallback_reasons=fallback_reasons,
            profiles=profile_plans,
        )

    def _run_approved_plan(
        self,
        *,
        plan: CoverageTestExecutionPlan,
        approval: CoverageTestExecutionApprovalReceipt,
        trusted_test_policy: SafeModePolicy,
        cancellation: CancellationSignal | None,
    ) -> CoverageTestExecutionReceipt:
        sandbox_path = self.sandbox_manager.sandbox_path(plan.sandbox_id)
        failure_codes: set[CoverageTestExecutionFailureCode] = set()
        before = self._inspect_checkout(
            sandbox_path,
            plan,
            failure_codes,
            verify_exact_snapshot=True,
        )
        before_matches = self._checkout_matches_plan(before, plan, failure_codes)
        profile_results: list[TestExecutionResult] = []
        execution_error = False
        cancelled = False
        if before_matches:
            try:
                runner = self.test_runner or SafeTestRunner.from_environment()
            except Exception:
                failure_codes.add(
                    CoverageTestExecutionFailureCode.TRUSTED_TEST_EXECUTION_ERROR
                )
                runner = None
                execution_error = True
            for profile in plan.profiles:
                if runner is None:
                    break
                try:
                    if profile.mode is CoverageTestExecutionMode.SELECTED_TESTS:
                        result = runner.run_selected_profiles(
                            sandbox_path,
                            trusted_test_policy,
                            (profile.profile_id,),
                            {profile.profile_id: profile.test_ids},
                            cancellation=cancellation,
                        )
                    else:
                        result = runner.run_profiles(
                            sandbox_path,
                            trusted_test_policy,
                            (profile.profile_id,),
                            cancellation=cancellation,
                        )
                    if len(result) != 1 or result[0].profile_id != profile.profile_id:
                        raise RuntimeError(
                            "trusted test runner returned unexpected profile evidence"
                        )
                    profile_results.append(result[0])
                    if not result[0].passed:
                        failure_codes.add(
                            CoverageTestExecutionFailureCode.TEST_PROFILE_FAILED
                        )
                    intermediate = self._inspect_checkout(
                        sandbox_path,
                        plan,
                        failure_codes,
                        verify_exact_snapshot=False,
                    )
                    if not self._checkout_matches_plan(
                        intermediate,
                        plan,
                        set(),
                        require_exact_snapshot=False,
                    ):
                        failure_codes.add(
                            CoverageTestExecutionFailureCode.SOURCE_CHANGED_DURING_EXECUTION
                        )
                        break
                except CancellationRequested:
                    failure_codes.add(
                        CoverageTestExecutionFailureCode.TRUSTED_TEST_CANCELLED
                    )
                    cancelled = True
                    break
                except PauseRequested:
                    failure_codes.add(
                        CoverageTestExecutionFailureCode.TRUSTED_TEST_CONTROL_STOPPED
                    )
                    cancelled = True
                    break
                except subprocess.TimeoutExpired:
                    failure_codes.add(
                        CoverageTestExecutionFailureCode.TRUSTED_TEST_TIMEOUT
                    )
                    execution_error = True
                    break
                except Exception:
                    failure_codes.add(
                        CoverageTestExecutionFailureCode.TRUSTED_TEST_EXECUTION_ERROR
                    )
                    execution_error = True
                    break

        after = self._inspect_checkout(
            sandbox_path,
            plan,
            failure_codes,
            verify_exact_snapshot=True,
        )
        after_matches = self._checkout_matches_plan(after, plan, set())
        source_preserved = before_matches and after_matches
        rollback_attempted = False
        rollback_succeeded = False
        rollback: CoverageTestCheckoutEvidence | None = None
        if before_matches and not after_matches:
            failure_codes.add(
                CoverageTestExecutionFailureCode.SOURCE_CHANGED_DURING_EXECUTION
            )
            rollback_attempted = True
            try:
                self.sandbox_manager.restore_tracked_checkout(
                    sandbox_path,
                    expected_base_sha=plan.target_base_sha,
                )
                rollback = self._inspect_checkout(
                    sandbox_path,
                    plan,
                    failure_codes,
                    verify_exact_snapshot=True,
                )
                rollback_succeeded = self._checkout_matches_plan(
                    rollback, plan, set()
                )
                if not rollback_succeeded:
                    failure_codes.add(CoverageTestExecutionFailureCode.ROLLBACK_FAILED)
            except Exception:
                failure_codes.add(CoverageTestExecutionFailureCode.ROLLBACK_FAILED)

        execution_complete = before_matches and not execution_error and not cancelled and (
            len(profile_results) == len(plan.profiles)
        )
        all_tests_passed = execution_complete and all(
            item.passed for item in profile_results
        )
        if not before_matches:
            outcome = CoverageTestExecutionOutcome.BLOCKED
        elif not source_preserved:
            outcome = CoverageTestExecutionOutcome.SOURCE_DRIFT
        elif cancelled:
            outcome = CoverageTestExecutionOutcome.CANCELLED
        elif execution_error:
            outcome = CoverageTestExecutionOutcome.EXECUTION_ERROR
        elif not all_tests_passed:
            outcome = CoverageTestExecutionOutcome.TEST_FAILED
        else:
            outcome = CoverageTestExecutionOutcome.PASSED

        return CoverageTestExecutionReceipt(
            execution_id=plan.execution_id,
            project_id=plan.project_id,
            plan_ref=approval.plan_ref,
            plan_sha256=approval.plan_sha256,
            approval_ref=self._approval_ref(approval),
            approval_sha256=approval.canonical_hash(),
            selection_ref=plan.selection_ref,
            selection_sha256=plan.selection_sha256,
            target_base_sha=plan.target_base_sha,
            source_tree_oid=plan.source_tree_oid,
            trusted_test_policy_sha256=plan.trusted_test_policy_sha256,
            execution_policy_sha256=plan.execution_policy_sha256,
            service_policy_sha256=plan.service_policy_sha256,
            execution_mode=plan.execution_mode,
            outcome=outcome,
            profile_results=tuple(profile_results),
            failure_codes=tuple(sorted(failure_codes, key=lambda item: item.value)),
            before_checkout=before,
            after_checkout=after,
            rollback_checkout=rollback,
            execution_complete=execution_complete,
            all_tests_passed=all_tests_passed,
            source_preserved=source_preserved,
            rollback_attempted=rollback_attempted,
            rollback_succeeded=rollback_succeeded,
        )

    def _approval_ref(self, approval: CoverageTestExecutionApprovalReceipt) -> str:
        digest = approval.canonical_hash()
        return (
            f"artifact://coverage-test-execution/{approval.project_id}/"
            f"{approval.execution_id}/approval-{digest}.json"
        )

    def _inspect_checkout(
        self,
        sandbox_path: Path,
        plan: CoverageTestExecutionPlan,
        failure_codes: set[CoverageTestExecutionFailureCode],
        *,
        verify_exact_snapshot: bool,
    ) -> CoverageTestCheckoutEvidence | None:
        try:
            state = self.sandbox_manager.inspect_checkout(sandbox_path)
        except Exception:
            failure_codes.add(
                CoverageTestExecutionFailureCode.SANDBOX_VERIFICATION_FAILED
            )
            return None
        exact_snapshot_verified = not verify_exact_snapshot
        if verify_exact_snapshot:
            try:
                source_tree_oid = (
                    self.coverage_selection.coverage_evidence.verify_exact_snapshot_source(
                        project_id=plan.project_id,
                        root=sandbox_path,
                        expected_snapshot_ref=plan.target_snapshot_ref,
                        expected_snapshot_sha256=plan.target_snapshot_sha256,
                    )
                )
                if source_tree_oid != state.source_tree_oid:
                    raise RepositoryCoverageTestExecutionError(
                        "sandbox tree conflicts with exact snapshot verification"
                    )
                exact_snapshot_verified = True
            except Exception:
                failure_codes.add(
                    CoverageTestExecutionFailureCode.SANDBOX_VERIFICATION_FAILED
                )
        return _checkout_evidence(
            state,
            exact_snapshot_verified=exact_snapshot_verified,
        )

    def _checkout_matches_plan(
        self,
        checkout: CoverageTestCheckoutEvidence | None,
        plan: CoverageTestExecutionPlan,
        failure_codes: set[CoverageTestExecutionFailureCode],
        *,
        require_exact_snapshot: bool = True,
    ) -> bool:
        if checkout is None:
            return False
        matches = True
        if checkout.head_sha != plan.target_base_sha:
            failure_codes.add(CoverageTestExecutionFailureCode.BASE_SHA_DRIFT)
            matches = False
        if checkout.source_tree_oid != plan.source_tree_oid:
            failure_codes.add(CoverageTestExecutionFailureCode.SOURCE_TREE_DRIFT)
            matches = False
        if not checkout.tracked_worktree_clean:
            failure_codes.add(CoverageTestExecutionFailureCode.TRACKED_WORKTREE_DIRTY)
            matches = False
        if require_exact_snapshot and not checkout.exact_snapshot_verified:
            matches = False
        return matches

    def _validate_prepare_inputs(
        self,
        *,
        project_id: str,
        repository: RepositorySpec,
        trusted_test_policy: SafeModePolicy,
        execution_policy: CoverageTestExecutionPolicy,
        selection: CoverageBackedTestSelection,
        policy_sha256: str,
    ) -> None:
        if (
            selection.project_id != project_id
            or selection.repository_url != repository.url
            or selection.base_ref != repository.base_ref
        ):
            raise RepositoryCoverageTestExecutionError(
                "selection provenance conflicts with the execution request"
            )
        if not hmac.compare_digest(
            selection.trusted_test_policy_sha256, policy_sha256
        ):
            raise RepositoryCoverageTestExecutionError(
                "selection trusted-test policy does not match"
            )
        profiles = trusted_test_policy.profile_map()
        if any(
            profile_id not in profiles
            for profile_id in selection.requested_profile_ids
        ):
            raise RepositoryCoverageTestExecutionError(
                "selection references a profile outside the trusted policy"
            )
        if any(
            profile_id not in profiles
            for profile_id in execution_policy.selected_test_profile_ids
        ):
            raise RepositoryCoverageTestExecutionError(
                "execution policy references a profile outside the trusted policy"
            )
        if len(selection.requested_profile_ids) > self.max_profiles:
            raise RepositoryCoverageTestExecutionError(
                "execution request exceeds its profile limit"
            )
        if sum(
            profiles[profile_id].output_limit
            for profile_id in selection.requested_profile_ids
        ) > self.max_total_output_chars:
            raise RepositoryCoverageTestExecutionError(
                "trusted profile outputs exceed the aggregate execution limit"
            )
        if sum(
            len(item.test_ids) for item in selection.selected_profiles
        ) > self.max_selected_tests:
            raise RepositoryCoverageTestExecutionError(
                "selection exceeds the execution selected-test limit"
            )

    def _verify_execution_inputs(
        self,
        *,
        plan: CoverageTestExecutionPlan,
        selection: CoverageBackedTestSelection,
        trusted_test_policy: SafeModePolicy,
        execution_policy: CoverageTestExecutionPolicy,
    ) -> None:
        policy_sha256 = trusted_test_policy_sha256(trusted_test_policy)
        if not hmac.compare_digest(plan.trusted_test_policy_sha256, policy_sha256):
            raise RepositoryCoverageTestExecutionError(
                "trusted-test policy drifted after approval"
            )
        if not hmac.compare_digest(
            plan.execution_policy_sha256, execution_policy.canonical_hash()
        ):
            raise RepositoryCoverageTestExecutionError(
                "selected-test execution policy drifted after approval"
            )
        selection_capable = set(execution_policy.selected_test_profile_ids)
        if selection.disposition is CoverageTestSelectionDisposition.SELECTED and set(
            selection.requested_profile_ids
        ).issubset(selection_capable):
            expected_mode = CoverageTestExecutionMode.SELECTED_TESTS
            expected_fallback_reasons: tuple[CoverageExecutionFallbackReason, ...] = ()
        elif selection.disposition is CoverageTestSelectionDisposition.SELECTED:
            expected_mode = CoverageTestExecutionMode.FULL_PROFILE
            expected_fallback_reasons = (
                CoverageExecutionFallbackReason.PROFILE_NOT_SELECTION_CAPABLE,
            )
        else:
            expected_mode = CoverageTestExecutionMode.FULL_PROFILE
            expected_fallback_reasons = (
                CoverageExecutionFallbackReason.SELECTION_FULL_PROFILE_FALLBACK,
            )
        if (
            plan.execution_mode is not expected_mode
            or plan.fallback_reasons != expected_fallback_reasons
        ):
            raise RepositoryCoverageTestExecutionError(
                "execution mode conflicts with the approved execution policy"
            )
        profiles = trusted_test_policy.profile_map()
        if tuple(item.profile_id for item in plan.profiles) != (
            selection.requested_profile_ids
        ):
            raise RepositoryCoverageTestExecutionError(
                "execution profiles conflict with the selection"
            )
        for profile in plan.profiles:
            trusted = profiles.get(profile.profile_id)
            if trusted is None or not hmac.compare_digest(
                profile.profile_sha256, trusted_test_profile_sha256(trusted)
            ):
                raise RepositoryCoverageTestExecutionError(
                    "trusted test profile drifted after approval"
                )
        if plan.execution_mode is CoverageTestExecutionMode.SELECTED_TESTS and any(
            profile.profile_id not in execution_policy.selected_test_profile_ids
            for profile in plan.profiles
        ):
            raise RepositoryCoverageTestExecutionError(
                "selected-test profile capability drifted after approval"
            )

    def _verified_selection(
        self, selection_ref: str, selection_sha256: str
    ) -> CoverageBackedTestSelection:
        try:
            return self.coverage_selection.verified_test_selection(
                selection_ref, selection_sha256
            )
        except RepositoryCoverageSelectionError as exc:
            raise RepositoryCoverageTestExecutionError(
                "coverage-backed test selection failed verification"
            ) from exc

    def _verified_selection_for_plan(
        self, plan: CoverageTestExecutionPlan
    ) -> CoverageBackedTestSelection:
        selection = self._verified_selection(
            plan.selection_ref, plan.selection_sha256
        )
        expected = (
            plan.project_id,
            plan.repository_url,
            plan.base_ref,
            plan.target_base_sha,
            plan.target_snapshot_ref,
            plan.target_snapshot_sha256,
            plan.selection_disposition,
            plan.selection_fallback_reasons,
            tuple(item.profile_id for item in plan.profiles),
        )
        actual = (
            selection.project_id,
            selection.repository_url,
            selection.base_ref,
            selection.target_base_sha,
            selection.target_snapshot_ref,
            selection.target_snapshot_sha256,
            selection.disposition,
            selection.fallback_reasons,
            selection.requested_profile_ids,
        )
        if actual != expected:
            raise RepositoryCoverageTestExecutionError(
                "execution plan conflicts with its selection artifact"
            )
        if plan.execution_mode is CoverageTestExecutionMode.SELECTED_TESTS:
            selected = {
                item.profile_id: item.test_ids for item in selection.selected_profiles
            }
            if any(
                selected.get(profile.profile_id) != profile.test_ids
                for profile in plan.profiles
            ):
                raise RepositoryCoverageTestExecutionError(
                    "execution plan selected tests conflict with the selection"
                )
        return selection

    def _verify_approval_binding(
        self,
        approval: CoverageTestExecutionApprovalReceipt,
        plan: CoverageTestExecutionPlan,
    ) -> None:
        expected = (
            plan.execution_id,
            plan.project_id,
            plan.canonical_hash(),
            plan.selection_ref,
            plan.selection_sha256,
            plan.target_base_sha,
            plan.source_tree_oid,
            plan.trusted_test_policy_sha256,
            plan.execution_policy_sha256,
            plan.service_policy_sha256,
        )
        actual = (
            approval.execution_id,
            approval.project_id,
            approval.plan_sha256,
            approval.selection_ref,
            approval.selection_sha256,
            approval.target_base_sha,
            approval.source_tree_oid,
            approval.trusted_test_policy_sha256,
            approval.execution_policy_sha256,
            approval.service_policy_sha256,
        )
        if actual != expected:
            raise RepositoryCoverageTestExecutionError(
                "execution approval conflicts with the exact plan"
            )

    def _verify_result_binding(
        self,
        receipt: CoverageTestExecutionReceipt,
        plan: CoverageTestExecutionPlan,
    ) -> None:
        expected = (
            plan.execution_id,
            plan.project_id,
            plan.selection_ref,
            plan.selection_sha256,
            plan.target_base_sha,
            plan.source_tree_oid,
            plan.trusted_test_policy_sha256,
            plan.execution_policy_sha256,
            plan.service_policy_sha256,
            plan.execution_mode,
        )
        actual = (
            receipt.execution_id,
            receipt.project_id,
            receipt.selection_ref,
            receipt.selection_sha256,
            receipt.target_base_sha,
            receipt.source_tree_oid,
            receipt.trusted_test_policy_sha256,
            receipt.execution_policy_sha256,
            receipt.service_policy_sha256,
            receipt.execution_mode,
        )
        if actual != expected:
            raise RepositoryCoverageTestExecutionError(
                "execution result conflicts with the exact plan"
            )
        planned_ids = tuple(item.profile_id for item in plan.profiles)
        result_ids = tuple(item.profile_id for item in receipt.profile_results)
        if result_ids != planned_ids[: len(result_ids)]:
            raise RepositoryCoverageTestExecutionError(
                "execution result profile order conflicts with the plan"
            )
        if receipt.execution_complete and result_ids != planned_ids:
            raise RepositoryCoverageTestExecutionError(
                "complete execution result is missing a planned profile"
            )

    def _write_plan(
        self, plan: CoverageTestExecutionPlan
    ) -> CoverageTestExecutionPlanResult:
        content = plan.canonical_content()
        if len(content.encode("utf-8")) > self.plan_max_bytes:
            raise RepositoryCoverageTestExecutionError(
                "coverage-test execution plan exceeds its byte limit"
            )
        digest = plan.canonical_hash()
        reference = self.artifacts.write_text(
            (
                f"coverage-test-execution/{plan.project_id}/{plan.execution_id}/"
                f"plan-{digest}.json"
            ),
            content,
            "application/json",
        )
        if not hmac.compare_digest(reference.sha256, digest):
            raise RepositoryCoverageTestExecutionError(
                "coverage-test execution plan artifact hash mismatch"
            )
        verified = self.verified_plan(reference.uri, digest)
        if verified != plan:
            raise RepositoryCoverageTestExecutionError(
                "coverage-test execution plan changed while recording"
            )
        return CoverageTestExecutionPlanResult(
            plan_ref=reference.uri,
            plan_sha256=digest,
            plan=verified,
        )

    def _write_approval(
        self, approval: CoverageTestExecutionApprovalReceipt
    ) -> CoverageTestExecutionApprovalResult:
        content = approval.canonical_content()
        if len(content.encode("utf-8")) > self.approval_max_bytes:
            raise RepositoryCoverageTestExecutionError(
                "coverage-test execution approval exceeds its byte limit"
            )
        digest = approval.canonical_hash()
        reference = self.artifacts.write_text(
            (
                f"coverage-test-execution/{approval.project_id}/"
                f"{approval.execution_id}/approval-{digest}.json"
            ),
            content,
            "application/json",
        )
        if not hmac.compare_digest(reference.sha256, digest):
            raise RepositoryCoverageTestExecutionError(
                "coverage-test execution approval artifact hash mismatch"
            )
        verified = self.verified_approval(reference.uri, digest)
        self._verify_approval_binding(
            verified,
            self.verified_plan(verified.plan_ref, verified.plan_sha256),
        )
        return CoverageTestExecutionApprovalResult(
            approval_ref=reference.uri,
            approval_sha256=digest,
            approval=verified,
        )

    def _write_result(
        self, receipt: CoverageTestExecutionReceipt
    ) -> CoverageTestExecutionResult:
        content = receipt.canonical_content()
        if len(content.encode("utf-8")) > self.result_max_bytes:
            raise RepositoryCoverageTestExecutionError(
                "coverage-test execution result exceeds its byte limit"
            )
        digest = receipt.canonical_hash()
        reference = self.artifacts.write_text(
            (
                f"coverage-test-execution/{receipt.project_id}/"
                f"{receipt.execution_id}/result-{digest}.json"
            ),
            content,
            "application/json",
        )
        if not hmac.compare_digest(reference.sha256, digest):
            raise RepositoryCoverageTestExecutionError(
                "coverage-test execution result artifact hash mismatch"
            )
        verified = self.verified_result(reference.uri, digest)
        if verified != receipt:
            raise RepositoryCoverageTestExecutionError(
                "coverage-test execution result changed while recording"
            )
        return CoverageTestExecutionResult(
            result_ref=reference.uri,
            result_sha256=digest,
            receipt=verified,
        )

    def _replay_plan(
        self,
        state: _ExecutionState,
        *,
        request_sha256: str,
        selection: CoverageBackedTestSelection,
        trusted_test_policy: SafeModePolicy,
        execution_policy: CoverageTestExecutionPolicy,
    ) -> CoverageTestExecutionPlanResult:
        if not hmac.compare_digest(state.request_sha256, request_sha256):
            raise RepositoryCoverageTestExecutionError(
                "execution identity already belongs to a different request"
            )
        if not state.plan_ref:
            raise RepositoryCoverageTestExecutionError(
                "execution preparation is incomplete and requires explicit recovery"
            )
        plan = self.verified_plan(state.plan_ref, state.plan_sha256)
        self._verify_state_plan(state, plan, state.plan_ref, state.plan_sha256)
        bound_selection = self._verified_selection_for_plan(plan)
        if bound_selection != selection:
            raise RepositoryCoverageTestExecutionError(
                "replayed execution selection does not match"
            )
        self._verify_execution_inputs(
            plan=plan,
            selection=selection,
            trusted_test_policy=trusted_test_policy,
            execution_policy=execution_policy,
        )
        return CoverageTestExecutionPlanResult(
            plan_ref=state.plan_ref,
            plan_sha256=state.plan_sha256,
            plan=plan,
            replayed=True,
        )

    def _result_from_state(
        self, state: _ExecutionState
    ) -> CoverageTestExecutionResult:
        receipt = self.verified_result(state.result_ref, state.result_sha256)
        if (
            state.execution_id != receipt.execution_id
            or state.project_id != receipt.project_id
        ):
            raise RepositoryCoverageTestExecutionError(
                "completed execution state scope does not match its result"
            )
        return CoverageTestExecutionResult(
            result_ref=state.result_ref,
            result_sha256=state.result_sha256,
            receipt=receipt,
        )

    def _mark_preparation_failed(
        self, execution_id: str, request_sha256: str
    ) -> None:
        with self._lock:
            try:
                self.connection.execute("BEGIN IMMEDIATE")
                self.connection.execute(
                    """
                    UPDATE coverage_test_executions SET status = ?
                    WHERE execution_id = ? AND request_sha256 = ? AND status = ?
                    """,
                    (
                        _ExecutionStatus.PREPARATION_FAILED.value,
                        execution_id,
                        request_sha256,
                        _ExecutionStatus.PREPARING.value,
                    ),
                )
                self.connection.commit()
            except BaseException:
                self.connection.rollback()

    def _state(self, execution_id: str) -> _ExecutionState | None:
        row = self.connection.execute(
            """
            SELECT execution_id, project_id, request_sha256, status,
                   plan_ref, plan_sha256, approval_ref, approval_sha256,
                   result_ref, result_sha256
            FROM coverage_test_executions WHERE execution_id = ?
            """,
            (execution_id,),
        ).fetchone()
        if row is None:
            return None
        try:
            return _ExecutionState.model_validate(dict(row))
        except ValidationError as exc:
            raise RepositoryCoverageTestExecutionError(
                "coverage-test execution state failed validation"
            ) from exc

    def _required_state(self, execution_id: str) -> _ExecutionState:
        state = self._state(execution_id)
        if state is None:
            raise RepositoryCoverageTestExecutionError(
                "coverage-test execution state was not found"
            )
        return state

    @staticmethod
    def _verify_state_plan(
        state: _ExecutionState,
        plan: CoverageTestExecutionPlan,
        plan_ref: str,
        plan_sha256: str,
    ) -> None:
        if (
            state.execution_id != plan.execution_id
            or state.project_id != plan.project_id
            or state.plan_ref != plan_ref
            or not hmac.compare_digest(state.plan_sha256, plan_sha256)
        ):
            raise RepositoryCoverageTestExecutionError(
                "execution state does not match the expected plan"
            )

    @staticmethod
    def _verify_state_approval(
        state: _ExecutionState, approval_ref: str, approval_sha256: str
    ) -> None:
        if state.approval_ref != approval_ref or not hmac.compare_digest(
            state.approval_sha256, approval_sha256
        ):
            raise RepositoryCoverageTestExecutionError(
                "execution state does not match the expected approval"
            )

    def _request_sha256(
        self,
        *,
        execution_id: str,
        project_id: str,
        repository: RepositorySpec,
        selection_ref: str,
        selection_sha256: str,
        trusted_test_policy_sha256: str,
        execution_policy_sha256: str,
    ) -> str:
        return hashlib.sha256(
            _canonical_json(
                {
                    "schema_version": "1",
                    "execution_id": execution_id,
                    "project_id": project_id,
                    "repository": repository.model_dump(mode="json"),
                    "selection_ref": selection_ref,
                    "selection_sha256": selection_sha256,
                    "trusted_test_policy_sha256": trusted_test_policy_sha256,
                    "execution_policy_sha256": execution_policy_sha256,
                    "service_policy_sha256": self._policy_sha256(),
                }
            ).encode("utf-8")
        ).hexdigest()

    def _policy_sha256(self) -> str:
        return hashlib.sha256(
            _canonical_json(
                {
                    "schema_version": "1",
                    "coverage_execution_policy_version": (
                        COVERAGE_EXECUTION_POLICY_VERSION
                    ),
                    "plan_format": "coverage-test-execution-plan-v1",
                    "approval_format": (
                        "coverage-test-execution-human-approval-v1"
                    ),
                    "receipt_format": "coverage-test-execution-result-v1",
                    "selected_test_arguments": "validated-positional-append-v1",
                    "fallback": "complete-requested-profile-v1",
                    "source_preservation": "exact-snapshot-and-tracked-reset-v1",
                    "approval_consumption": "one-shot-durable-v1",
                    "indeterminate_running_recovery": "explicit-required-v1",
                    "plan_max_bytes": self.plan_max_bytes,
                    "approval_max_bytes": self.approval_max_bytes,
                    "result_max_bytes": self.result_max_bytes,
                    "max_profiles": self.max_profiles,
                    "max_selected_tests": self.max_selected_tests,
                    "max_total_output_chars": self.max_total_output_chars,
                    "max_json_items": self.max_json_items,
                    "max_json_depth": self.max_json_depth,
                }
            ).encode("utf-8")
        ).hexdigest()

    def _load_bounded_json(
        self,
        reference: str,
        expected_sha256: str,
        *,
        max_bytes: int,
        context: str,
    ) -> dict[str, Any]:
        try:
            content = self.artifacts.read_text_bounded_verified(
                reference,
                expected_sha256=expected_sha256,
                max_bytes=max_bytes,
            )
            _preflight_json(
                content,
                max_items=self.max_json_items,
                max_depth=self.max_json_depth,
            )
            value = json.loads(
                content,
                object_pairs_hook=_unique_object,
                parse_constant=_reject_json_constant,
            )
        except RepositoryCoverageTestExecutionError:
            raise
        except (OSError, UnicodeError, ValueError, RecursionError) as exc:
            raise RepositoryCoverageTestExecutionError(
                f"{context} failed bounded integrity verification"
            ) from exc
        if not isinstance(value, dict):
            raise RepositoryCoverageTestExecutionError(
                f"{context} must contain one JSON object"
            )
        return value

    @staticmethod
    def _validate_ids(*, execution_id: str, project_id: str) -> None:
        if _ID.fullmatch(execution_id) is None:
            raise RepositoryCoverageTestExecutionError("execution ID is invalid")
        if _ID.fullmatch(project_id) is None:
            raise RepositoryCoverageTestExecutionError("project ID is invalid")


def _checkout_evidence(
    state: SandboxCheckoutState,
    *,
    exact_snapshot_verified: bool,
) -> CoverageTestCheckoutEvidence:
    return CoverageTestCheckoutEvidence(
        head_sha=state.head_sha,
        source_tree_oid=state.source_tree_oid,
        tracked_worktree_clean=state.tracked_worktree_clean,
        exact_snapshot_verified=exact_snapshot_verified,
    )


def _preflight_json(content: str, *, max_items: int, max_depth: int) -> None:
    stack: list[str] = []
    in_string = False
    escaped = False
    structural_items = 0
    for character in content:
        if in_string:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
            continue
        if character == '"':
            in_string = True
            continue
        if character in "[{":
            stack.append(character)
            structural_items += 1
            if len(stack) > max_depth:
                raise RepositoryCoverageTestExecutionError(
                    "coverage-test execution JSON exceeds its depth limit"
                )
        elif character in "]}":
            expected = "[" if character == "]" else "{"
            if not stack or stack.pop() != expected:
                raise RepositoryCoverageTestExecutionError(
                    "coverage-test execution JSON structure is malformed"
                )
        elif character in ",:":
            structural_items += 1
        if structural_items > max_items:
            raise RepositoryCoverageTestExecutionError(
                "coverage-test execution JSON exceeds its structural-item limit"
            )
    if in_string or escaped or stack:
        raise RepositoryCoverageTestExecutionError(
            "coverage-test execution JSON structure is malformed"
        )


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("coverage-test execution JSON contains a duplicate field")
        value[key] = item
    return value


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"unsupported JSON constant: {value}")


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        separators=(",", ":"),
        sort_keys=True,
        ensure_ascii=False,
    )
