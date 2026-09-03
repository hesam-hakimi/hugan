from __future__ import annotations

import codecs
import hashlib
import hmac
import io
import json
import math
import os
import re
import selectors
import signal
import stat
import subprocess
import time
from bisect import bisect_right
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Annotated, Literal

from pydantic import FailFast, Field, field_validator, model_validator

from universal_coding_agent.core.models import FrozenModel
from universal_coding_agent.core.safe_models import (
    SafeModePolicy,
    TestProfile,
    normalize_repository_path,
)
from universal_coding_agent.product.call_graphs import (
    PythonCallGraph,
    PythonSymbol,
    RepositoryCallGraphError,
)
from universal_coding_agent.product.dispatch_evidence import (
    DISPATCH_EVIDENCE_POLICY_VERSION,
    PythonDispatchEvidence,
    RepositoryDispatchEvidenceError,
    RepositoryDispatchEvidenceService,
)
from universal_coding_agent.product.repository_indexes import (
    RepositoryIndexError,
    RepositoryIndexSnapshot,
    RepositorySnapshotFile,
)
from universal_coding_agent.product.search_service import (
    RepositoryCoverageEvidenceState,
    RepositoryCoverageEvidenceStateError,
    RepositoryDispatchEvidenceState,
    SearchService,
)
from universal_coding_agent.storage.artifacts import ArtifactStore

DEFAULT_COVERAGE_RUN_MAX_BYTES = 24_000_000
DEFAULT_COVERAGE_EVIDENCE_MAX_BYTES = 24_000_000
DEFAULT_COVERAGE_SOURCE_MAX_BYTES = 64_000_000
DEFAULT_COVERAGE_POLICY_MAX_BYTES = 1_000_000
DEFAULT_COVERAGE_PROFILE_MAX_BYTES = 64_000
DEFAULT_COVERAGE_MAX_PROFILES = 256
DEFAULT_COVERAGE_MAX_SCOPE_FILES = 100_000
DEFAULT_COVERAGE_MAX_TESTS = 200_000
DEFAULT_COVERAGE_MAX_FILES_PER_TEST = 10_000
DEFAULT_COVERAGE_MAX_FILE_OBSERVATIONS = 500_000
DEFAULT_COVERAGE_MAX_RANGES_PER_FILE = 100_000
DEFAULT_COVERAGE_MAX_RANGES = 2_000_000
DEFAULT_COVERAGE_MAX_JSON_ITEMS = 400_000
DEFAULT_COVERAGE_MAX_JSON_DEPTH = 64
DEFAULT_COVERAGE_MAX_LINES = 20_000_000
DEFAULT_COVERAGE_MAX_SYMBOL_BINDINGS = 2_000_000
DEFAULT_COVERAGE_MAX_SYMBOL_EVALUATIONS = 50_000_000
DEFAULT_COVERAGE_MAX_SYMBOL_OUTPUT_BYTES = 12_000_000
DEFAULT_COVERAGE_MAX_TEST_ID_BYTES = 8_192
DEFAULT_COVERAGE_GIT_TIMEOUT_SECONDS = 30.0
DEFAULT_COVERAGE_GIT_OUTPUT_MAX_BYTES = 1_000_000
COVERAGE_EVIDENCE_POLICY_VERSION = "1"
_PROJECT_ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")
_OBJECT_ID = re.compile(r"^[0-9a-f]{40,64}$")


class RepositoryCoverageEvidenceError(ValueError):
    """Coverage evidence cannot satisfy its bounded trusted-run contract."""


class CoverageLineRange(FrozenModel):
    start_line: int = Field(ge=1)
    end_line: int = Field(ge=1)

    @model_validator(mode="after")
    def validate_order(self) -> CoverageLineRange:
        if self.end_line < self.start_line:
            raise ValueError("coverage line range ends before it starts")
        return self


class CoverageScopeFile(FrozenModel):
    path: str = Field(min_length=1, max_length=4096)
    source_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @field_validator("path")
    @classmethod
    def validate_path(cls, value: str) -> str:
        return normalize_repository_path(value)


class TrustedCoverageFile(FrozenModel):
    path: str = Field(min_length=1, max_length=4096)
    source_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    ranges: Annotated[tuple[CoverageLineRange, ...], FailFast()] = Field(
        min_length=1,
        max_length=DEFAULT_COVERAGE_MAX_RANGES_PER_FILE,
    )

    @field_validator("path")
    @classmethod
    def validate_path(cls, value: str) -> str:
        return normalize_repository_path(value)

    @field_validator("ranges")
    @classmethod
    def validate_ranges(
        cls, values: tuple[CoverageLineRange, ...]
    ) -> tuple[CoverageLineRange, ...]:
        previous: CoverageLineRange | None = None
        for current in values:
            if previous is not None and (
                current.start_line,
                current.end_line,
            ) <= (previous.start_line, previous.end_line):
                raise ValueError("coverage line ranges must be unique and sorted")
            if previous is not None and current.start_line <= previous.end_line + 1:
                raise ValueError(
                    "coverage line ranges must be non-overlapping and canonically merged"
                )
            previous = current
        return values


class TrustedCoverageProfile(FrozenModel):
    profile_id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}$")
    profile_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    passed: bool
    returncode: int
    collection_complete: bool
    execution_complete: bool
    test_count: int = Field(ge=1)


class TrustedTestCoverage(FrozenModel):
    profile_id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}$")
    test_id: str = Field(min_length=1, max_length=8192)
    test_path: str = Field(min_length=1, max_length=4096)
    test_source_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    covered_files: Annotated[tuple[TrustedCoverageFile, ...], FailFast()] = Field(
        default=(),
        max_length=DEFAULT_COVERAGE_MAX_FILES_PER_TEST,
    )

    @field_validator("test_id")
    @classmethod
    def validate_test_id(cls, value: str) -> str:
        if value != value.strip() or any(ord(character) < 32 for character in value):
            raise ValueError("coverage test ID contains surrounding whitespace or controls")
        return value

    @field_validator("test_path")
    @classmethod
    def validate_test_path(cls, value: str) -> str:
        return normalize_repository_path(value)

    @field_validator("covered_files")
    @classmethod
    def validate_files(
        cls, values: tuple[TrustedCoverageFile, ...]
    ) -> tuple[TrustedCoverageFile, ...]:
        previous = ""
        for item in values:
            if item.path <= previous:
                raise ValueError("covered files must be unique and sorted")
            previous = item.path
        return values

    @model_validator(mode="after")
    def validate_identity(self) -> TrustedTestCoverage:
        if self.test_id != self.test_path and not self.test_id.startswith(
            f"{self.test_path}::"
        ):
            raise ValueError("coverage test ID is not bound to its tracked test path")
        return self


class TrustedCoverageRun(FrozenModel):
    """One host-attested normalized run receipt; hashes provide integrity, not trust."""

    schema_version: Literal["1"] = "1"
    producer: Literal["uca-trusted-test-coverage-v1"] = "uca-trusted-test-coverage-v1"
    context_format: Literal["test-id-line-ranges-v1"] = "test-id-line-ranges-v1"
    run_id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")
    project_id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")
    repository_url: str = Field(min_length=1, max_length=2048)
    base_ref: str = Field(min_length=1, max_length=256)
    base_sha: str = Field(pattern=r"^[0-9a-f]{40,64}$")
    tracked_source_clean_before: Literal[True] = True
    tracked_source_clean_after: Literal[True] = True
    source_tree_before_oid: str = Field(pattern=r"^[0-9a-f]{40,64}$")
    source_tree_after_oid: str = Field(pattern=r"^[0-9a-f]{40,64}$")
    repository_snapshot_ref: str = Field(pattern=r"^artifact://[a-zA-Z0-9._/-]+$")
    repository_snapshot_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    dependency_graph_ref: str = Field(pattern=r"^artifact://[a-zA-Z0-9._/-]+$")
    dependency_graph_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    call_graph_ref: str = Field(pattern=r"^artifact://[a-zA-Z0-9._/-]+$")
    call_graph_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    dispatch_evidence_ref: str = Field(pattern=r"^artifact://[a-zA-Z0-9._/-]+$")
    dispatch_evidence_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    trusted_test_policy_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    profiles: Annotated[tuple[TrustedCoverageProfile, ...], FailFast()] = Field(
        min_length=1,
        max_length=DEFAULT_COVERAGE_MAX_PROFILES,
    )
    coverage_scope: Annotated[tuple[CoverageScopeFile, ...], FailFast()] = Field(
        min_length=1,
        max_length=DEFAULT_COVERAGE_MAX_SCOPE_FILES,
    )
    tests: Annotated[tuple[TrustedTestCoverage, ...], FailFast()] = Field(
        min_length=1,
        max_length=DEFAULT_COVERAGE_MAX_TESTS,
    )
    unattributed_files: Annotated[tuple[TrustedCoverageFile, ...], FailFast()] = Field(
        default=(),
        max_length=DEFAULT_COVERAGE_MAX_SCOPE_FILES,
    )

    @model_validator(mode="after")
    def validate_run(self) -> TrustedCoverageRun:
        profile_ids = tuple(item.profile_id for item in self.profiles)
        if not _strictly_increasing(profile_ids):
            raise ValueError("coverage run profiles must be unique and sorted")
        scope_paths = tuple(item.path for item in self.coverage_scope)
        if not _strictly_increasing(scope_paths):
            raise ValueError("coverage scope files must be unique and sorted")
        test_keys = tuple(_test_key(item) for item in self.tests)
        if not _strictly_increasing(test_keys):
            raise ValueError("coverage tests must be unique and sorted")
        known_profiles = set(profile_ids)
        if any(item.profile_id not in known_profiles for item in self.tests):
            raise ValueError("coverage test references an unknown profile")
        tests_per_profile: dict[str, int] = defaultdict(int)
        for item in self.tests:
            tests_per_profile[item.profile_id] += 1
        if any(
            item.test_count != tests_per_profile[item.profile_id]
            for item in self.profiles
        ):
            raise ValueError("coverage profile test count does not match collected tests")
        known_scope = set(scope_paths)
        scope_sha256 = {item.path: item.source_sha256 for item in self.coverage_scope}
        if any(
            covered.path not in known_scope
            or covered.source_sha256 != scope_sha256[covered.path]
            for test in self.tests
            for covered in test.covered_files
        ):
            raise ValueError("test coverage does not match the declared scope")
        unattributed_paths = tuple(item.path for item in self.unattributed_files)
        if not _strictly_increasing(unattributed_paths):
            raise ValueError("unattributed coverage files must be unique and sorted")
        if any(
            item.path not in known_scope
            or item.source_sha256 != scope_sha256[item.path]
            for item in self.unattributed_files
        ):
            raise ValueError("unattributed coverage does not match the declared scope")
        return self

    def canonical_content(self) -> str:
        return _canonical_json(self.model_dump(mode="json"))

    def canonical_hash(self) -> str:
        return hashlib.sha256(self.canonical_content().encode("utf-8")).hexdigest()


class CoveredFileEvidence(FrozenModel):
    path: str = Field(min_length=1, max_length=4096)
    source_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    ranges: Annotated[tuple[CoverageLineRange, ...], FailFast()] = Field(
        min_length=1,
        max_length=DEFAULT_COVERAGE_MAX_RANGES_PER_FILE,
    )
    covered_symbol_ids: Annotated[tuple[str, ...], FailFast()] = Field(
        default=(),
        max_length=DEFAULT_COVERAGE_MAX_SYMBOL_BINDINGS,
    )

    @field_validator("path")
    @classmethod
    def validate_path(cls, value: str) -> str:
        return normalize_repository_path(value)

    @field_validator("ranges")
    @classmethod
    def validate_ranges(
        cls, values: tuple[CoverageLineRange, ...]
    ) -> tuple[CoverageLineRange, ...]:
        TrustedCoverageFile.validate_ranges(values)
        return values

    @field_validator("covered_symbol_ids")
    @classmethod
    def validate_symbols(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        if not _strictly_increasing(values):
            raise ValueError("covered symbol IDs must be unique and sorted")
        return values


class TestCoverageEvidence(FrozenModel):
    profile_id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}$")
    test_id: str = Field(min_length=1, max_length=8192)
    test_path: str = Field(min_length=1, max_length=4096)
    test_source_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    covered_files: Annotated[tuple[CoveredFileEvidence, ...], FailFast()] = Field(
        default=(),
        max_length=DEFAULT_COVERAGE_MAX_FILES_PER_TEST,
    )

    @field_validator("test_id")
    @classmethod
    def validate_test_id(cls, value: str) -> str:
        return TrustedTestCoverage.validate_test_id(value)

    @field_validator("test_path")
    @classmethod
    def validate_test_path(cls, value: str) -> str:
        return normalize_repository_path(value)

    @field_validator("covered_files")
    @classmethod
    def validate_files(
        cls, values: tuple[CoveredFileEvidence, ...]
    ) -> tuple[CoveredFileEvidence, ...]:
        previous = ""
        for item in values:
            if item.path <= previous:
                raise ValueError("covered evidence files must be unique and sorted")
            previous = item.path
        return values

    @model_validator(mode="after")
    def validate_identity(self) -> TestCoverageEvidence:
        if self.test_id != self.test_path and not self.test_id.startswith(
            f"{self.test_path}::"
        ):
            raise ValueError("coverage evidence test ID is not bound to its test path")
        return self


class RepositoryCoverageEvidence(FrozenModel):
    schema_version: Literal["1"] = "1"
    project_id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")
    repository_url: str = Field(min_length=1, max_length=2048)
    base_ref: str = Field(min_length=1, max_length=256)
    base_sha: str = Field(pattern=r"^[0-9a-f]{40,64}$")
    source_tree_oid: str = Field(pattern=r"^[0-9a-f]{40,64}$")
    namespace: str = Field(
        pattern=r"^explicit:repository-coverage-evidence:[a-zA-Z0-9._-]+$"
    )
    repository_snapshot_ref: str = Field(pattern=r"^artifact://[a-zA-Z0-9._/-]+$")
    repository_snapshot_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    dependency_graph_ref: str = Field(pattern=r"^artifact://[a-zA-Z0-9._/-]+$")
    dependency_graph_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    call_graph_ref: str = Field(pattern=r"^artifact://[a-zA-Z0-9._/-]+$")
    call_graph_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    dispatch_evidence_ref: str = Field(pattern=r"^artifact://[a-zA-Z0-9._/-]+$")
    dispatch_evidence_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    trusted_run_ref: str = Field(pattern=r"^artifact://[a-zA-Z0-9._/-]+$")
    trusted_run_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    test_run_id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")
    trusted_test_policy_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    policy_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    symbol_mapping: Literal["python-call-graph-span-intersection-v1"] = (
        "python-call-graph-span-intersection-v1"
    )
    previous_evidence_ref: str | None = Field(
        default=None, pattern=r"^artifact://[a-zA-Z0-9._/-]+$"
    )
    previous_evidence_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    profiles: Annotated[tuple[TrustedCoverageProfile, ...], FailFast()] = Field(
        min_length=1,
        max_length=DEFAULT_COVERAGE_MAX_PROFILES,
    )
    coverage_scope: Annotated[tuple[CoverageScopeFile, ...], FailFast()] = Field(
        min_length=1,
        max_length=DEFAULT_COVERAGE_MAX_SCOPE_FILES,
    )
    tests: Annotated[tuple[TestCoverageEvidence, ...], FailFast()] = Field(
        min_length=1,
        max_length=DEFAULT_COVERAGE_MAX_TESTS,
    )
    unattributed_files: Annotated[tuple[CoveredFileEvidence, ...], FailFast()] = Field(
        default=(),
        max_length=DEFAULT_COVERAGE_MAX_SCOPE_FILES,
    )

    @model_validator(mode="after")
    def validate_evidence(self) -> RepositoryCoverageEvidence:
        if self.namespace != f"explicit:repository-coverage-evidence:{self.project_id}":
            raise ValueError("coverage-evidence namespace does not match project identity")
        if (self.previous_evidence_ref is None) != (self.previous_evidence_sha256 is None):
            raise ValueError("coverage-evidence predecessor reference and hash must be paired")
        profile_ids = tuple(item.profile_id for item in self.profiles)
        if not _strictly_increasing(profile_ids):
            raise ValueError("coverage-evidence profiles must be unique and sorted")
        scope_paths = tuple(item.path for item in self.coverage_scope)
        if not _strictly_increasing(scope_paths):
            raise ValueError("coverage-evidence scope must be unique and sorted")
        test_keys = tuple(_evidence_test_key(item) for item in self.tests)
        if not _strictly_increasing(test_keys):
            raise ValueError("coverage-evidence tests must be unique and sorted")
        known_profiles = set(profile_ids)
        if any(item.profile_id not in known_profiles for item in self.tests):
            raise ValueError("coverage evidence references an unknown profile")
        known_scope = set(scope_paths)
        scope_sha256 = {item.path: item.source_sha256 for item in self.coverage_scope}
        if any(
            covered.path not in known_scope
            or covered.source_sha256 != scope_sha256[covered.path]
            for test in self.tests
            for covered in test.covered_files
        ):
            raise ValueError("coverage evidence does not match its scope")
        unattributed_paths = tuple(item.path for item in self.unattributed_files)
        if not _strictly_increasing(unattributed_paths):
            raise ValueError("unattributed coverage evidence must be unique and sorted")
        if any(
            item.path not in known_scope
            or item.source_sha256 != scope_sha256[item.path]
            for item in self.unattributed_files
        ):
            raise ValueError("unattributed evidence does not match its scope")
        tests_per_profile: dict[str, int] = defaultdict(int)
        for item in self.tests:
            tests_per_profile[item.profile_id] += 1
        if any(
            item.test_count != tests_per_profile[item.profile_id]
            for item in self.profiles
        ):
            raise ValueError("coverage-evidence profile test count does not match its tests")
        return self

    def canonical_content(self) -> str:
        return _canonical_json(self.model_dump(mode="json"))

    def canonical_hash(self) -> str:
        return hashlib.sha256(self.canonical_content().encode("utf-8")).hexdigest()


class RepositoryCoverageEvidenceResult(FrozenModel):
    evidence_ref: str = Field(pattern=r"^artifact://[a-zA-Z0-9._/-]+$")
    evidence_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    evidence: RepositoryCoverageEvidence
    replayed: bool = False


class RepositoryCoverageEvidenceService:
    """Record host-attested line contexts without executing or selecting tests."""

    def __init__(
        self,
        artifacts: ArtifactStore,
        search: SearchService,
        dispatch_evidence: RepositoryDispatchEvidenceService,
        *,
        run_max_bytes: int = DEFAULT_COVERAGE_RUN_MAX_BYTES,
        evidence_max_bytes: int = DEFAULT_COVERAGE_EVIDENCE_MAX_BYTES,
        max_source_bytes: int = DEFAULT_COVERAGE_SOURCE_MAX_BYTES,
        policy_max_bytes: int = DEFAULT_COVERAGE_POLICY_MAX_BYTES,
        profile_max_bytes: int = DEFAULT_COVERAGE_PROFILE_MAX_BYTES,
        max_profiles: int = DEFAULT_COVERAGE_MAX_PROFILES,
        max_scope_files: int = DEFAULT_COVERAGE_MAX_SCOPE_FILES,
        max_tests: int = DEFAULT_COVERAGE_MAX_TESTS,
        max_files_per_test: int = DEFAULT_COVERAGE_MAX_FILES_PER_TEST,
        max_file_observations: int = DEFAULT_COVERAGE_MAX_FILE_OBSERVATIONS,
        max_ranges_per_file: int = DEFAULT_COVERAGE_MAX_RANGES_PER_FILE,
        max_ranges: int = DEFAULT_COVERAGE_MAX_RANGES,
        max_json_items: int = DEFAULT_COVERAGE_MAX_JSON_ITEMS,
        max_json_depth: int = DEFAULT_COVERAGE_MAX_JSON_DEPTH,
        max_covered_lines: int = DEFAULT_COVERAGE_MAX_LINES,
        max_symbol_bindings: int = DEFAULT_COVERAGE_MAX_SYMBOL_BINDINGS,
        max_symbol_evaluations: int = DEFAULT_COVERAGE_MAX_SYMBOL_EVALUATIONS,
        max_symbol_output_bytes: int = DEFAULT_COVERAGE_MAX_SYMBOL_OUTPUT_BYTES,
        max_test_id_bytes: int = DEFAULT_COVERAGE_MAX_TEST_ID_BYTES,
        git_timeout_seconds: float = DEFAULT_COVERAGE_GIT_TIMEOUT_SECONDS,
        git_output_max_bytes: int = DEFAULT_COVERAGE_GIT_OUTPUT_MAX_BYTES,
    ) -> None:
        integer_limits = (
            run_max_bytes,
            evidence_max_bytes,
            max_source_bytes,
            policy_max_bytes,
            profile_max_bytes,
            max_profiles,
            max_scope_files,
            max_tests,
            max_files_per_test,
            max_file_observations,
            max_ranges_per_file,
            max_ranges,
            max_json_items,
            max_json_depth,
            max_covered_lines,
            max_symbol_bindings,
            max_symbol_evaluations,
            max_symbol_output_bytes,
            max_test_id_bytes,
            git_output_max_bytes,
        )
        if any(type(limit) is not int for limit in integer_limits):
            raise ValueError("repository coverage-evidence limits must be integers")
        if (
            isinstance(git_timeout_seconds, bool)
            or not isinstance(git_timeout_seconds, (int, float))
            or not math.isfinite(git_timeout_seconds)
        ):
            raise ValueError("coverage Git timeout must be a finite number")
        if any(limit < 1 for limit in (*integer_limits, git_timeout_seconds)):
            raise ValueError("repository coverage-evidence limits must be positive")
        if max_test_id_bytes > 8192:
            raise ValueError("coverage test-ID byte limit cannot exceed the schema limit")
        schema_limits = (
            (max_profiles, DEFAULT_COVERAGE_MAX_PROFILES),
            (max_scope_files, DEFAULT_COVERAGE_MAX_SCOPE_FILES),
            (max_tests, DEFAULT_COVERAGE_MAX_TESTS),
            (max_files_per_test, DEFAULT_COVERAGE_MAX_FILES_PER_TEST),
            (max_ranges_per_file, DEFAULT_COVERAGE_MAX_RANGES_PER_FILE),
        )
        if any(configured > maximum for configured, maximum in schema_limits):
            raise ValueError("coverage limit cannot exceed its schema maximum")
        self.artifacts = artifacts
        self.search = search
        self.dispatch_evidence = dispatch_evidence
        self.call_graphs = dispatch_evidence.call_graphs
        self.repository_indexes = self.call_graphs.repository_indexes
        self.run_max_bytes = run_max_bytes
        self.evidence_max_bytes = evidence_max_bytes
        self.max_source_bytes = max_source_bytes
        self.policy_max_bytes = policy_max_bytes
        self.profile_max_bytes = profile_max_bytes
        self.max_profiles = max_profiles
        self.max_scope_files = max_scope_files
        self.max_tests = max_tests
        self.max_files_per_test = max_files_per_test
        self.max_file_observations = max_file_observations
        self.max_ranges_per_file = max_ranges_per_file
        self.max_ranges = max_ranges
        self.max_json_items = max_json_items
        self.max_json_depth = max_json_depth
        self.max_covered_lines = max_covered_lines
        self.max_symbol_bindings = max_symbol_bindings
        self.max_symbol_evaluations = max_symbol_evaluations
        self.max_symbol_output_bytes = max_symbol_output_bytes
        self.max_test_id_bytes = max_test_id_bytes
        self.git_timeout_seconds = git_timeout_seconds
        self.git_output_max_bytes = git_output_max_bytes

    @staticmethod
    def namespace(project_id: str) -> str:
        return f"explicit:repository-coverage-evidence:{project_id}"

    def record_trusted_run(
        self,
        *,
        project_id: str,
        root: Path,
        trusted_test_policy: SafeModePolicy,
        trusted_run_ref: str,
        trusted_run_sha256: str,
        expected_dispatch_evidence_ref: str,
        expected_dispatch_evidence_sha256: str,
        expected_previous_evidence_ref: str | None,
        expected_previous_evidence_sha256: str | None,
    ) -> RepositoryCoverageEvidenceResult:
        self._validate_project_id(project_id)
        self._verify_trusted_policy_bounds(trusted_test_policy)
        self._validate_predecessor_pair(
            expected_previous_evidence_ref, expected_previous_evidence_sha256
        )
        dispatch_state, _dispatch = self._verified_dispatch(
            project_id,
            expected_dispatch_evidence_ref,
            expected_dispatch_evidence_sha256,
        )
        call_graph = self._verified_call_graph(
            project_id,
            dispatch_state.call_graph_ref,
            dispatch_state.call_graph_sha256,
        )
        snapshot = self._verified_snapshot(
            project_id,
            dispatch_state.repository_snapshot_ref,
            dispatch_state.repository_snapshot_sha256,
        )
        git_deadline = time.monotonic() + self.git_timeout_seconds
        self._verify_clean_base(root, snapshot.base_sha, deadline=git_deadline)
        source_tree_oid = self._source_tree_oid(
            root,
            snapshot.base_sha,
            deadline=git_deadline,
        )
        run = self._load_run(trusted_run_ref, trusted_run_sha256)
        self._validate_run(
            run,
            project_id=project_id,
            trusted_test_policy=trusted_test_policy,
            dispatch_state=dispatch_state,
            snapshot=snapshot,
            source_tree_oid=source_tree_oid,
            root=root,
            git_deadline=git_deadline,
        )

        namespace = self.namespace(project_id)
        active = self.search.repository_coverage_evidence_state(namespace)
        previous: RepositoryCoverageEvidence | None = None
        if active is None:
            if expected_previous_evidence_sha256 is not None:
                raise RepositoryCoverageEvidenceError(
                    "expected predecessor coverage evidence does not exist"
                )
        else:
            if (
                active.evidence_ref != expected_previous_evidence_ref
                or active.evidence_sha256 != expected_previous_evidence_sha256
            ):
                raise RepositoryCoverageEvidenceError(
                    "expected predecessor does not match active coverage evidence"
                )
            previous = self._load_active(active)
            self._verify_compatibility(previous, project_id, trusted_test_policy)
            if self._is_exact_replay(
                active,
                dispatch_state=dispatch_state,
                source_tree_oid=source_tree_oid,
                trusted_run_ref=trusted_run_ref,
                trusted_run_sha256=trusted_run_sha256,
                trusted_test_policy=trusted_test_policy,
            ):
                tests, unattributed = self._derive_mappings(run, call_graph)
                if (
                    previous.test_run_id != run.run_id
                    or previous.profiles != run.profiles
                    or previous.coverage_scope != run.coverage_scope
                    or previous.tests != tests
                    or previous.unattributed_files != unattributed
                ):
                    raise RepositoryCoverageEvidenceError(
                        "active coverage evidence no longer matches its trusted run"
                    )
                verified_run = self._load_run(trusted_run_ref, trusted_run_sha256)
                verified_previous = self._load_active(active)
                if verified_run != run or verified_previous != previous:
                    raise RepositoryCoverageEvidenceError(
                        "coverage artifacts changed during exact replay"
                    )
                self._validate_run(
                    verified_run,
                    project_id=project_id,
                    trusted_test_policy=trusted_test_policy,
                    dispatch_state=dispatch_state,
                    snapshot=snapshot,
                    source_tree_oid=source_tree_oid,
                    root=root,
                    git_deadline=git_deadline,
                )
                self._verify_clean_base(
                    root,
                    snapshot.base_sha,
                    deadline=git_deadline,
                )
                if (
                    self._source_tree_oid(
                        root,
                        snapshot.base_sha,
                        deadline=git_deadline,
                    )
                    != source_tree_oid
                ):
                    raise RepositoryCoverageEvidenceError(
                        "repository source tree changed during coverage verification"
                    )
                try:
                    self.search.apply_repository_coverage_evidence_state(
                        state=active,
                        expected_previous_evidence_ref=active.evidence_ref,
                        expected_previous_evidence_sha256=active.evidence_sha256,
                    )
                except RepositoryCoverageEvidenceStateError as exc:
                    raise RepositoryCoverageEvidenceError(str(exc)) from exc
                return RepositoryCoverageEvidenceResult(
                    evidence_ref=active.evidence_ref,
                    evidence_sha256=active.evidence_sha256,
                    evidence=verified_previous,
                    replayed=True,
                )

        tests, unattributed = self._derive_mappings(run, call_graph)
        try:
            evidence = RepositoryCoverageEvidence(
                project_id=project_id,
                repository_url=snapshot.repository_url,
                base_ref=snapshot.base_ref,
                base_sha=snapshot.base_sha,
                source_tree_oid=source_tree_oid,
                namespace=namespace,
                repository_snapshot_ref=dispatch_state.repository_snapshot_ref,
                repository_snapshot_sha256=dispatch_state.repository_snapshot_sha256,
                dependency_graph_ref=dispatch_state.dependency_graph_ref,
                dependency_graph_sha256=dispatch_state.dependency_graph_sha256,
                call_graph_ref=dispatch_state.call_graph_ref,
                call_graph_sha256=dispatch_state.call_graph_sha256,
                dispatch_evidence_ref=dispatch_state.evidence_ref,
                dispatch_evidence_sha256=dispatch_state.evidence_sha256,
                trusted_run_ref=trusted_run_ref,
                trusted_run_sha256=trusted_run_sha256,
                test_run_id=run.run_id,
                trusted_test_policy_sha256=trusted_test_policy_sha256(
                    trusted_test_policy
                ),
                policy_sha256=self._policy_sha256(),
                previous_evidence_ref=active.evidence_ref if active else None,
                previous_evidence_sha256=active.evidence_sha256 if active else None,
                profiles=run.profiles,
                coverage_scope=run.coverage_scope,
                tests=tests,
                unattributed_files=unattributed,
            )
        except ValueError as exc:
            raise RepositoryCoverageEvidenceError(
                "repository coverage evidence failed canonical validation"
            ) from exc
        evidence_ref, evidence_sha256 = self._write(evidence)
        verified_run = self._load_run(trusted_run_ref, trusted_run_sha256)
        if verified_run != run:
            raise RepositoryCoverageEvidenceError(
                "trusted coverage run changed during coverage recording"
            )
        verified_evidence = self._load(evidence_ref, evidence_sha256)
        if verified_evidence != evidence:
            raise RepositoryCoverageEvidenceError(
                "coverage evidence changed during coverage recording"
            )
        self._validate_run(
            verified_run,
            project_id=project_id,
            trusted_test_policy=trusted_test_policy,
            dispatch_state=dispatch_state,
            snapshot=snapshot,
            source_tree_oid=source_tree_oid,
            root=root,
            git_deadline=git_deadline,
        )
        self._verify_clean_base(root, snapshot.base_sha, deadline=git_deadline)
        if (
            self._source_tree_oid(
                root,
                snapshot.base_sha,
                deadline=git_deadline,
            )
            != source_tree_oid
        ):
            raise RepositoryCoverageEvidenceError(
                "repository source tree changed during coverage recording"
            )
        state = RepositoryCoverageEvidenceState(
            namespace=namespace,
            project_id=project_id,
            repository_url=snapshot.repository_url,
            base_ref=snapshot.base_ref,
            base_sha=snapshot.base_sha,
            source_tree_oid=source_tree_oid,
            repository_snapshot_ref=dispatch_state.repository_snapshot_ref,
            repository_snapshot_sha256=dispatch_state.repository_snapshot_sha256,
            dependency_graph_ref=dispatch_state.dependency_graph_ref,
            dependency_graph_sha256=dispatch_state.dependency_graph_sha256,
            call_graph_ref=dispatch_state.call_graph_ref,
            call_graph_sha256=dispatch_state.call_graph_sha256,
            dispatch_evidence_ref=dispatch_state.evidence_ref,
            dispatch_evidence_sha256=dispatch_state.evidence_sha256,
            trusted_run_ref=trusted_run_ref,
            trusted_run_sha256=trusted_run_sha256,
            test_run_id=run.run_id,
            trusted_test_policy_sha256=trusted_test_policy_sha256(trusted_test_policy),
            evidence_ref=evidence_ref,
            evidence_sha256=evidence_sha256,
            policy_sha256=evidence.policy_sha256,
        )
        try:
            self.search.apply_repository_coverage_evidence_state(
                state=state,
                expected_previous_evidence_ref=expected_previous_evidence_ref,
                expected_previous_evidence_sha256=expected_previous_evidence_sha256,
            )
        except RepositoryCoverageEvidenceStateError as exc:
            raise RepositoryCoverageEvidenceError(str(exc)) from exc
        return RepositoryCoverageEvidenceResult(
            evidence_ref=evidence_ref,
            evidence_sha256=evidence_sha256,
            evidence=verified_evidence,
        )

    def verified_active_evidence(
        self,
        *,
        project_id: str,
        trusted_test_policy: SafeModePolicy,
        expected_evidence_ref: str,
        expected_evidence_sha256: str,
    ) -> tuple[RepositoryCoverageEvidenceState, RepositoryCoverageEvidence]:
        self._validate_project_id(project_id)
        self._verify_trusted_policy_bounds(trusted_test_policy)
        state = self.search.repository_coverage_evidence_state(self.namespace(project_id))
        if state is None:
            raise RepositoryCoverageEvidenceError(
                "active repository coverage evidence does not exist"
            )
        if state.evidence_ref != expected_evidence_ref or not hmac.compare_digest(
            state.evidence_sha256, expected_evidence_sha256
        ):
            raise RepositoryCoverageEvidenceError(
                "active coverage-evidence reference or hash does not match"
            )
        dispatch_state, _dispatch = self._verified_dispatch(
            project_id,
            state.dispatch_evidence_ref,
            state.dispatch_evidence_sha256,
        )
        call_graph = self._verified_call_graph(
            project_id, state.call_graph_ref, state.call_graph_sha256
        )
        snapshot = self._verified_snapshot(
            project_id,
            state.repository_snapshot_ref,
            state.repository_snapshot_sha256,
        )
        run = self._load_run(state.trusted_run_ref, state.trusted_run_sha256)
        self._validate_run(
            run,
            project_id=project_id,
            trusted_test_policy=trusted_test_policy,
            dispatch_state=dispatch_state,
            snapshot=snapshot,
            source_tree_oid=state.source_tree_oid,
            root=None,
            git_deadline=None,
        )
        evidence = self._load_active(state)
        self._verify_compatibility(evidence, project_id, trusted_test_policy)
        tests, unattributed = self._derive_mappings(run, call_graph)
        if (
            evidence.test_run_id != run.run_id
            or evidence.profiles != run.profiles
            or evidence.coverage_scope != run.coverage_scope
            or evidence.tests != tests
            or evidence.unattributed_files != unattributed
        ):
            raise RepositoryCoverageEvidenceError(
                "coverage evidence does not match its trusted run and call graph"
            )
        return state, evidence

    def _verified_dispatch(
        self, project_id: str, reference: str, sha256: str
    ) -> tuple[RepositoryDispatchEvidenceState, PythonDispatchEvidence]:
        try:
            return self.dispatch_evidence.verified_active_evidence(
                project_id=project_id,
                expected_evidence_ref=reference,
                expected_evidence_sha256=sha256,
            )
        except RepositoryDispatchEvidenceError as exc:
            raise RepositoryCoverageEvidenceError(str(exc)) from exc

    def _verified_call_graph(
        self, project_id: str, reference: str, sha256: str
    ) -> PythonCallGraph:
        try:
            _state, graph = self.call_graphs.verified_active_graph(
                project_id=project_id,
                expected_graph_ref=reference,
                expected_graph_sha256=sha256,
            )
        except RepositoryCallGraphError as exc:
            raise RepositoryCoverageEvidenceError(str(exc)) from exc
        return graph

    def _verified_snapshot(
        self, project_id: str, reference: str, sha256: str
    ) -> RepositoryIndexSnapshot:
        try:
            state, snapshot = self.repository_indexes.verified_active_snapshot(
                project_id, expected_snapshot_sha256=sha256
            )
        except RepositoryIndexError as exc:
            raise RepositoryCoverageEvidenceError(str(exc)) from exc
        if state.snapshot_ref != reference:
            raise RepositoryCoverageEvidenceError(
                "active repository snapshot reference does not match coverage provenance"
            )
        return snapshot

    def _validate_run(
        self,
        run: TrustedCoverageRun,
        *,
        project_id: str,
        trusted_test_policy: SafeModePolicy,
        dispatch_state: RepositoryDispatchEvidenceState,
        snapshot: RepositoryIndexSnapshot,
        source_tree_oid: str,
        root: Path | None,
        git_deadline: float | None,
    ) -> None:
        expected_upstream = (
            project_id,
            snapshot.repository_url,
            snapshot.base_ref,
            snapshot.base_sha,
            dispatch_state.repository_snapshot_ref,
            dispatch_state.repository_snapshot_sha256,
            dispatch_state.dependency_graph_ref,
            dispatch_state.dependency_graph_sha256,
            dispatch_state.call_graph_ref,
            dispatch_state.call_graph_sha256,
            dispatch_state.evidence_ref,
            dispatch_state.evidence_sha256,
        )
        actual_upstream = (
            run.project_id,
            run.repository_url,
            run.base_ref,
            run.base_sha,
            run.repository_snapshot_ref,
            run.repository_snapshot_sha256,
            run.dependency_graph_ref,
            run.dependency_graph_sha256,
            run.call_graph_ref,
            run.call_graph_sha256,
            run.dispatch_evidence_ref,
            run.dispatch_evidence_sha256,
        )
        if actual_upstream != expected_upstream:
            raise RepositoryCoverageEvidenceError(
                "trusted coverage run does not match the exact active upstream chain"
            )
        if (
            run.source_tree_before_oid != source_tree_oid
            or run.source_tree_after_oid != source_tree_oid
        ):
            raise RepositoryCoverageEvidenceError(
                "trusted coverage run source tree does not match before and after execution"
            )
        expected_policy_sha256 = trusted_test_policy_sha256(trusted_test_policy)
        if not hmac.compare_digest(
            run.trusted_test_policy_sha256, expected_policy_sha256
        ):
            raise RepositoryCoverageEvidenceError(
                "trusted coverage run test policy does not match"
            )
        if len(run.profiles) > self.max_profiles:
            raise RepositoryCoverageEvidenceError(
                "trusted coverage run exceeds its profile limit"
            )
        trusted_profiles = trusted_test_policy.profile_map()
        for result in run.profiles:
            profile = trusted_profiles.get(result.profile_id)
            if profile is None:
                raise RepositoryCoverageEvidenceError(
                    "coverage run references a profile outside the trusted test policy"
                )
            if not hmac.compare_digest(
                result.profile_sha256, trusted_test_profile_sha256(profile)
            ):
                raise RepositoryCoverageEvidenceError(
                    "coverage run test profile digest does not match trusted policy"
                )
            if (
                not result.passed
                or result.returncode != 0
                or not result.collection_complete
                or not result.execution_complete
            ):
                raise RepositoryCoverageEvidenceError(
                    "coverage run profile did not pass and complete"
                )
        if len(run.coverage_scope) > self.max_scope_files:
            raise RepositoryCoverageEvidenceError(
                "trusted coverage run exceeds its scope-file limit"
            )
        if len(run.tests) > self.max_tests:
            raise RepositoryCoverageEvidenceError(
                "trusted coverage run exceeds its test limit"
            )
        snapshot_files = {item.path: item for item in snapshot.files}
        scope_paths: set[str] = set()
        for item in run.coverage_scope:
            source = snapshot_files.get(item.path)
            if source is None or not hmac.compare_digest(
                source.project_file.sha256, item.source_sha256
            ):
                raise RepositoryCoverageEvidenceError(
                    "coverage scope does not match a tracked snapshot file"
                )
            if source.git_mode not in {"100644", "100755"}:
                raise RepositoryCoverageEvidenceError(
                    "coverage scope references an unsupported file mode"
                )
            scope_paths.add(item.path)

        attributed_file_observations = sum(
            len(item.covered_files) for item in run.tests
        )
        if attributed_file_observations < 1:
            raise RepositoryCoverageEvidenceError(
                "trusted coverage run contains no per-test line coverage evidence"
            )
        file_observations = len(run.unattributed_files)
        total_ranges = sum(len(item.ranges) for item in run.unattributed_files)
        total_lines = sum(_range_line_count(item.ranges) for item in run.unattributed_files)
        observed_files = list(run.unattributed_files)
        for test in run.tests:
            if len(test.test_id.encode("utf-8")) > self.max_test_id_bytes:
                raise RepositoryCoverageEvidenceError(
                    "trusted coverage run exceeds its test-ID byte limit"
                )
            test_source = snapshot_files.get(test.test_path)
            if (
                test_source is None
                or not test_source.project_file.is_test
                or test_source.git_mode not in {"100644", "100755"}
                or not hmac.compare_digest(
                    test_source.project_file.sha256, test.test_source_sha256
                )
            ):
                raise RepositoryCoverageEvidenceError(
                    "coverage test identity does not match a tracked test file"
                )
            if len(test.covered_files) > self.max_files_per_test:
                raise RepositoryCoverageEvidenceError(
                    "trusted coverage run exceeds its per-test file limit"
                )
            file_observations += len(test.covered_files)
            total_ranges += sum(len(item.ranges) for item in test.covered_files)
            total_lines += sum(
                _range_line_count(item.ranges) for item in test.covered_files
            )
            observed_files.extend(test.covered_files)
        if file_observations > self.max_file_observations:
            raise RepositoryCoverageEvidenceError(
                "trusted coverage run exceeds its file-observation limit"
            )
        if total_ranges > self.max_ranges:
            raise RepositoryCoverageEvidenceError(
                "trusted coverage run exceeds its line-range limit"
            )
        if total_lines > self.max_covered_lines:
            raise RepositoryCoverageEvidenceError(
                "trusted coverage run exceeds its covered-line limit"
            )
        for item in observed_files:
            if item.path not in scope_paths:
                raise RepositoryCoverageEvidenceError(
                    "coverage observation falls outside the declared scope"
                )
            if len(item.ranges) > self.max_ranges_per_file:
                raise RepositoryCoverageEvidenceError(
                    "trusted coverage run exceeds its per-file range limit"
                )
            source = snapshot_files.get(item.path)
            if source is None or not hmac.compare_digest(
                source.project_file.sha256, item.source_sha256
            ):
                raise RepositoryCoverageEvidenceError(
                    "coverage observation source does not match the snapshot"
                )
        if root is not None:
            self._verify_observed_source(
                root,
                run.base_sha,
                snapshot_files,
                observed_files,
                tuple(item.path for item in run.coverage_scope),
                tuple(item.test_path for item in run.tests),
                git_deadline,
            )

    def _verify_observed_source(
        self,
        root: Path,
        base_sha: str,
        snapshot_files: dict[str, RepositorySnapshotFile],
        observed_files: list[TrustedCoverageFile],
        scope_paths: tuple[str, ...],
        test_paths: tuple[str, ...],
        git_deadline: float | None,
    ) -> None:
        try:
            root = root.resolve(strict=True)
        except (OSError, RuntimeError) as exc:
            raise RepositoryCoverageEvidenceError(
                "coverage repository root cannot be resolved"
            ) from exc
        ranges_by_path: dict[str, list[CoverageLineRange]] = defaultdict(list)
        for item in observed_files:
            ranges_by_path[item.path].extend(item.ranges)
        required_paths = set(ranges_by_path) | set(scope_paths) | set(test_paths)
        if not required_paths.issubset(snapshot_files):
            raise RepositoryCoverageEvidenceError(
                "coverage source is missing from the repository snapshot"
            )
        paths = tuple(sorted(snapshot_files))
        base_entries = self._base_tree_entries(
            root,
            base_sha,
            paths,
            deadline=git_deadline,
        )
        total_source_bytes = 0
        for path in paths:
            snapshot_file = snapshot_files[path]
            if snapshot_file.git_mode not in {"100644", "100755"}:
                raise RepositoryCoverageEvidenceError(
                    "coverage source references an unsupported file mode"
                )
            base_entry = base_entries.get(path)
            if base_entry != (snapshot_file.git_mode, snapshot_file.git_blob_oid):
                raise RepositoryCoverageEvidenceError(
                    "coverage source does not match the exact Base tree entry"
                )
            source_path = root / path
            try:
                resolved_source = source_path.resolve(strict=True)
            except (OSError, RuntimeError) as exc:
                raise RepositoryCoverageEvidenceError(
                    "coverage source cannot be resolved"
                ) from exc
            if (
                resolved_source != source_path.absolute()
                or resolved_source == root
                or root not in resolved_source.parents
            ):
                raise RepositoryCoverageEvidenceError(
                    "coverage source is not a contained regular file"
                )
            open_flags = os.O_RDONLY
            open_flags |= getattr(os, "O_CLOEXEC", 0)
            open_flags |= getattr(os, "O_NOFOLLOW", 0)
            open_flags |= getattr(os, "O_NONBLOCK", 0)
            open_flags |= getattr(os, "O_BINARY", 0)
            descriptor: int | None = None
            try:
                descriptor = os.open(source_path, open_flags)
                source_stat = os.fstat(descriptor)
            except OSError as exc:
                if descriptor is not None:
                    os.close(descriptor)
                raise RepositoryCoverageEvidenceError(
                    "coverage source cannot be opened safely"
                ) from exc
            if not stat.S_ISREG(source_stat.st_mode):
                os.close(descriptor)
                raise RepositoryCoverageEvidenceError(
                    "coverage source is not a contained regular file"
                )
            live_executable = bool(source_stat.st_mode & stat.S_IXUSR)
            if live_executable != (snapshot_file.git_mode == "100755"):
                os.close(descriptor)
                raise RepositoryCoverageEvidenceError(
                    "coverage source executable mode does not match the exact Base"
                )
            project_file = snapshot_file.project_file
            if source_stat.st_size != project_file.size:
                os.close(descriptor)
                raise RepositoryCoverageEvidenceError(
                    "coverage source drifted from the repository snapshot"
                )
            if project_file.size > self.max_source_bytes - total_source_bytes:
                os.close(descriptor)
                raise RepositoryCoverageEvidenceError(
                    "coverage evidence exceeds its source-byte limit"
                )
            try:
                with os.fdopen(descriptor, "rb") as stream:
                    descriptor = None
                    data = stream.read(project_file.size + 1)
            except OSError as exc:
                if descriptor is not None:
                    os.close(descriptor)
                raise RepositoryCoverageEvidenceError(
                    "coverage source cannot be read"
                ) from exc
            total_source_bytes += len(data)
            if len(data) != project_file.size or not hmac.compare_digest(
                hashlib.sha256(data).hexdigest(), project_file.sha256
            ):
                raise RepositoryCoverageEvidenceError(
                    "coverage source drifted from the repository snapshot"
                )
            if not hmac.compare_digest(
                _git_blob_oid(data, snapshot_file.git_blob_oid),
                snapshot_file.git_blob_oid,
            ):
                raise RepositoryCoverageEvidenceError(
                    "coverage source bytes do not match the exact Base Git blob"
                )
            if path in ranges_by_path:
                try:
                    line_count = _utf8_line_count(data)
                except UnicodeDecodeError as exc:
                    raise RepositoryCoverageEvidenceError(
                        "coverage source is not UTF-8 text"
                    ) from exc
                if any(
                    item.end_line > line_count for item in ranges_by_path[path]
                ):
                    raise RepositoryCoverageEvidenceError(
                        "coverage observation line falls outside its source file"
                    )
        self._verify_index_visibility(
            root,
            snapshot_files,
            deadline=git_deadline,
        )

    def _base_tree_entries(
        self,
        root: Path,
        base_sha: str,
        paths: tuple[str, ...],
        *,
        deadline: float | None,
    ) -> dict[str, tuple[str, str]]:
        entries: dict[str, tuple[str, str]] = {}
        pending: list[str] = []
        pending_bytes = 0

        def load_pending() -> None:
            if not pending:
                return
            try:
                process = self._run_git(
                    root,
                    (
                        "ls-tree",
                        "-z",
                        "--full-tree",
                        base_sha,
                        "--",
                        *(f":(literal){path}" for path in pending),
                    ),
                    deadline=deadline,
                )
            except RepositoryCoverageEvidenceError as exc:
                raise RepositoryCoverageEvidenceError(
                    "exact Base tree-entry verification failed"
                ) from exc
            for raw_entry in process.stdout.split(b"\0"):
                if not raw_entry:
                    continue
                try:
                    raw_metadata, raw_path = raw_entry.split(b"\t", 1)
                    mode, object_type, object_id = raw_metadata.decode("ascii").split(
                        " ", 2
                    )
                    path = raw_path.decode("utf-8", errors="strict")
                except (UnicodeDecodeError, ValueError) as exc:
                    raise RepositoryCoverageEvidenceError(
                        "exact Base tree metadata is malformed"
                    ) from exc
                if (
                    object_type != "blob"
                    or not _OBJECT_ID.fullmatch(object_id)
                    or path in entries
                ):
                    raise RepositoryCoverageEvidenceError(
                        "exact Base tree metadata is incompatible"
                    )
                entries[path] = (mode, object_id)

        for path in paths:
            literal_path = f":(literal){path}"
            path_bytes = len(literal_path.encode("utf-8")) + 1
            if pending and (len(pending) >= 128 or pending_bytes + path_bytes > 65_536):
                load_pending()
                pending = []
                pending_bytes = 0
            pending.append(path)
            pending_bytes += path_bytes
        load_pending()
        if set(entries) != set(paths):
            raise RepositoryCoverageEvidenceError(
                "coverage source is missing from the exact Base tree"
            )
        return entries

    def _derive_mappings(
        self, run: TrustedCoverageRun, call_graph: PythonCallGraph
    ) -> tuple[tuple[TestCoverageEvidence, ...], tuple[CoveredFileEvidence, ...]]:
        symbols_by_path: dict[str, list[PythonSymbol]] = defaultdict(list)
        for symbol in call_graph.symbols:
            symbols_by_path[symbol.path].append(symbol)
        symbol_bindings = 0
        symbol_evaluations = 0
        symbol_output_bytes = 0
        cached_symbol_ids: dict[
            tuple[str, tuple[CoverageLineRange, ...]], tuple[str, ...]
        ] = {}
        cached_symbol_output_bytes: dict[tuple[str, ...], int] = {}

        def covered_file(item: TrustedCoverageFile) -> CoveredFileEvidence:
            nonlocal symbol_bindings, symbol_evaluations, symbol_output_bytes
            cache_key = (item.path, item.ranges)
            symbol_ids = cached_symbol_ids.get(cache_key)
            if symbol_ids is None:
                candidates = symbols_by_path.get(item.path, ())
                symbol_evaluations += len(candidates)
                if symbol_evaluations > self.max_symbol_evaluations:
                    raise RepositoryCoverageEvidenceError(
                        "coverage evidence exceeds its symbol-evaluation limit"
                    )
                range_starts = tuple(value.start_line for value in item.ranges)
                symbol_ids = tuple(
                    sorted(
                        symbol.symbol_id
                        for symbol in candidates
                        if _ranges_overlap_span(
                            item.ranges,
                            range_starts,
                            symbol.line,
                            symbol.end_line,
                        )
                    )
                )
                cached_symbol_ids[cache_key] = symbol_ids
            symbol_bindings += len(symbol_ids)
            if symbol_bindings > self.max_symbol_bindings:
                raise RepositoryCoverageEvidenceError(
                    "coverage evidence exceeds its symbol-binding limit"
                )
            emitted_bytes = cached_symbol_output_bytes.get(symbol_ids)
            if emitted_bytes is None:
                emitted_bytes = sum(
                    len(_canonical_json(symbol_id).encode("utf-8")) + 1
                    for symbol_id in symbol_ids
                )
                cached_symbol_output_bytes[symbol_ids] = emitted_bytes
            symbol_output_bytes += emitted_bytes
            if symbol_output_bytes > self.max_symbol_output_bytes:
                raise RepositoryCoverageEvidenceError(
                    "coverage evidence exceeds its symbol-output byte limit"
                )
            return CoveredFileEvidence(
                path=item.path,
                source_sha256=item.source_sha256,
                ranges=item.ranges,
                covered_symbol_ids=symbol_ids,
            )

        tests = tuple(
            TestCoverageEvidence(
                profile_id=test.profile_id,
                test_id=test.test_id,
                test_path=test.test_path,
                test_source_sha256=test.test_source_sha256,
                covered_files=tuple(covered_file(item) for item in test.covered_files),
            )
            for test in run.tests
        )
        unattributed = tuple(covered_file(item) for item in run.unattributed_files)
        return tests, unattributed

    def _write(self, evidence: RepositoryCoverageEvidence) -> tuple[str, str]:
        content, digest = _bounded_canonical_json(
            evidence.model_dump(mode="json"),
            max_bytes=self.evidence_max_bytes,
            error_message="repository coverage evidence exceeds its byte limit",
        )
        reference = self.artifacts.write_text(
            f"coverage-evidence/{evidence.project_id}/{evidence.base_sha}/evidence-{digest}.json",
            content,
            "application/json",
        )
        if not hmac.compare_digest(reference.sha256, digest):
            raise RepositoryCoverageEvidenceError(
                "repository coverage-evidence artifact hash mismatch"
            )
        return reference.uri, digest

    def _load_run(self, reference: str, expected_sha256: str) -> TrustedCoverageRun:
        try:
            content = self.artifacts.read_text_bounded_verified(
                reference,
                expected_sha256=expected_sha256,
                max_bytes=self.run_max_bytes,
            )
            self._preflight_json(content, context="trusted coverage run")
            run = TrustedCoverageRun.model_validate_json(content)
        except RepositoryCoverageEvidenceError:
            raise
        except (OSError, UnicodeError, ValueError) as exc:
            raise RepositoryCoverageEvidenceError(
                "trusted coverage run failed bounded integrity verification"
            ) from exc
        if not hmac.compare_digest(run.canonical_hash(), expected_sha256):
            raise RepositoryCoverageEvidenceError(
                "trusted coverage run canonical hash does not match"
            )
        return run

    def _load(
        self, reference: str, expected_sha256: str
    ) -> RepositoryCoverageEvidence:
        try:
            content = self.artifacts.read_text_bounded_verified(
                reference,
                expected_sha256=expected_sha256,
                max_bytes=self.evidence_max_bytes,
            )
            self._preflight_json(content, context="coverage evidence")
            evidence = RepositoryCoverageEvidence.model_validate_json(content)
        except RepositoryCoverageEvidenceError:
            raise
        except (OSError, UnicodeError, ValueError) as exc:
            raise RepositoryCoverageEvidenceError(
                "coverage evidence failed bounded integrity verification"
            ) from exc
        if not hmac.compare_digest(evidence.canonical_hash(), expected_sha256):
            raise RepositoryCoverageEvidenceError(
                "coverage-evidence canonical hash mismatch"
            )
        return evidence

    def _preflight_json(self, content: str, *, context: str) -> None:
        _preflight_coverage_json(
            content,
            context=context,
            max_profiles=self.max_profiles,
            max_scope_files=self.max_scope_files,
            max_tests=self.max_tests,
            max_files_per_test=self.max_files_per_test,
            max_file_observations=self.max_file_observations,
            max_ranges_per_file=self.max_ranges_per_file,
            max_ranges=self.max_ranges,
            max_json_items=self.max_json_items,
            max_json_depth=self.max_json_depth,
        )

    def _load_active(
        self, state: RepositoryCoverageEvidenceState
    ) -> RepositoryCoverageEvidence:
        evidence = self._load(state.evidence_ref, state.evidence_sha256)
        expected = (
            state.namespace,
            state.project_id,
            state.repository_url,
            state.base_ref,
            state.base_sha,
            state.source_tree_oid,
            state.repository_snapshot_ref,
            state.repository_snapshot_sha256,
            state.dependency_graph_ref,
            state.dependency_graph_sha256,
            state.call_graph_ref,
            state.call_graph_sha256,
            state.dispatch_evidence_ref,
            state.dispatch_evidence_sha256,
            state.trusted_run_ref,
            state.trusted_run_sha256,
            state.test_run_id,
            state.trusted_test_policy_sha256,
            state.policy_sha256,
        )
        actual = (
            evidence.namespace,
            evidence.project_id,
            evidence.repository_url,
            evidence.base_ref,
            evidence.base_sha,
            evidence.source_tree_oid,
            evidence.repository_snapshot_ref,
            evidence.repository_snapshot_sha256,
            evidence.dependency_graph_ref,
            evidence.dependency_graph_sha256,
            evidence.call_graph_ref,
            evidence.call_graph_sha256,
            evidence.dispatch_evidence_ref,
            evidence.dispatch_evidence_sha256,
            evidence.trusted_run_ref,
            evidence.trusted_run_sha256,
            evidence.test_run_id,
            evidence.trusted_test_policy_sha256,
            evidence.policy_sha256,
        )
        if actual != expected:
            raise RepositoryCoverageEvidenceError(
                "active coverage-evidence state does not match artifact provenance"
            )
        return evidence

    def _verify_compatibility(
        self,
        evidence: RepositoryCoverageEvidence,
        project_id: str,
        trusted_test_policy: SafeModePolicy,
    ) -> None:
        if evidence.project_id != project_id or evidence.namespace != self.namespace(project_id):
            raise RepositoryCoverageEvidenceError(
                "coverage-evidence project scope does not match"
            )
        if not hmac.compare_digest(evidence.policy_sha256, self._policy_sha256()):
            raise RepositoryCoverageEvidenceError(
                "coverage-evidence policy does not match"
            )
        if not hmac.compare_digest(
            evidence.trusted_test_policy_sha256,
            trusted_test_policy_sha256(trusted_test_policy),
        ):
            raise RepositoryCoverageEvidenceError(
                "coverage-evidence trusted test policy does not match"
            )

    def _is_exact_replay(
        self,
        state: RepositoryCoverageEvidenceState,
        *,
        dispatch_state: RepositoryDispatchEvidenceState,
        source_tree_oid: str,
        trusted_run_ref: str,
        trusted_run_sha256: str,
        trusted_test_policy: SafeModePolicy,
    ) -> bool:
        return (
            state.repository_snapshot_ref == dispatch_state.repository_snapshot_ref
            and hmac.compare_digest(
                state.repository_snapshot_sha256,
                dispatch_state.repository_snapshot_sha256,
            )
            and state.dependency_graph_ref == dispatch_state.dependency_graph_ref
            and hmac.compare_digest(
                state.dependency_graph_sha256, dispatch_state.dependency_graph_sha256
            )
            and state.call_graph_ref == dispatch_state.call_graph_ref
            and hmac.compare_digest(
                state.call_graph_sha256, dispatch_state.call_graph_sha256
            )
            and state.dispatch_evidence_ref == dispatch_state.evidence_ref
            and hmac.compare_digest(
                state.dispatch_evidence_sha256, dispatch_state.evidence_sha256
            )
            and state.source_tree_oid == source_tree_oid
            and state.trusted_run_ref == trusted_run_ref
            and hmac.compare_digest(state.trusted_run_sha256, trusted_run_sha256)
            and hmac.compare_digest(state.policy_sha256, self._policy_sha256())
            and hmac.compare_digest(
                state.trusted_test_policy_sha256,
                trusted_test_policy_sha256(trusted_test_policy),
            )
        )

    def _verify_trusted_policy_bounds(self, policy: SafeModePolicy) -> None:
        if len(policy.profiles) > self.max_profiles:
            raise RepositoryCoverageEvidenceError(
                "trusted test policy exceeds its profile limit"
            )
        total_profile_bytes = 0
        for profile in policy.profiles:
            approximate_characters = (
                len(profile.profile_id)
                + len(profile.cwd)
                + sum(len(argument) for argument in profile.argv)
            )
            if approximate_characters > self.profile_max_bytes:
                raise RepositoryCoverageEvidenceError(
                    "trusted test profile exceeds its byte limit"
                )
            profile_bytes = len(
                _canonical_json(profile.model_dump(mode="json")).encode("utf-8")
            )
            if profile_bytes > self.profile_max_bytes:
                raise RepositoryCoverageEvidenceError(
                    "trusted test profile exceeds its byte limit"
                )
            total_profile_bytes += profile_bytes
            if total_profile_bytes > self.policy_max_bytes:
                raise RepositoryCoverageEvidenceError(
                    "trusted test policy exceeds its byte limit"
                )
        policy_bytes = len(
            _canonical_json(policy.model_dump(mode="json")).encode("utf-8")
        )
        if policy_bytes > self.policy_max_bytes:
            raise RepositoryCoverageEvidenceError(
                "trusted test policy exceeds its byte limit"
            )

    def _verify_clean_base(
        self,
        root: Path,
        base_sha: str,
        *,
        deadline: float | None,
    ) -> None:
        try:
            head = self._run_git(
                root,
                ("rev-parse", "HEAD"),
                deadline=deadline,
            ).stdout.decode("ascii").strip()
        except (UnicodeDecodeError, RepositoryCoverageEvidenceError) as exc:
            raise RepositoryCoverageEvidenceError(
                "repository HEAD verification failed"
            ) from exc
        if head != base_sha:
            raise RepositoryCoverageEvidenceError(
                "repository HEAD does not match the requested Base SHA"
            )

    def _verify_index_visibility(
        self,
        root: Path,
        snapshot_files: dict[str, RepositorySnapshotFile],
        *,
        deadline: float | None,
    ) -> None:
        staged = self._run_git(
            root,
            ("ls-files", "-v", "-s", "-z", "--"),
            deadline=deadline,
        )
        visible_paths: set[str] = set()
        staged_entries: dict[str, tuple[str, str]] = {}
        for raw_entry in staged.stdout.split(b"\0"):
            if not raw_entry:
                continue
            try:
                raw_metadata, raw_path = raw_entry.split(b"\t", 1)
                tag, mode, object_id, stage = raw_metadata.decode("ascii").split(
                    " ", 3
                )
                path = raw_path.decode("utf-8", errors="strict")
            except (UnicodeDecodeError, ValueError) as exc:
                raise RepositoryCoverageEvidenceError(
                    "tracked index entry metadata is malformed"
                ) from exc
            if tag != "H" or path in visible_paths:
                raise RepositoryCoverageEvidenceError(
                    "tracked index visibility flags are not permitted"
                )
            visible_paths.add(path)
            if (
                stage != "0"
                or mode not in {"100644", "100755"}
                or not _OBJECT_ID.fullmatch(object_id)
                or path in staged_entries
            ):
                raise RepositoryCoverageEvidenceError(
                    "tracked index contains an unsupported entry"
                )
            staged_entries[path] = (mode, object_id)
        if visible_paths != set(staged_entries):
            raise RepositoryCoverageEvidenceError(
                "tracked index visibility metadata does not match its entries"
            )
        if set(staged_entries) != set(snapshot_files):
            raise RepositoryCoverageEvidenceError(
                "tracked index contains a path outside the active snapshot"
            )
        if any(
            staged_entries[path]
            != (snapshot_file.git_mode, snapshot_file.git_blob_oid)
            for path, snapshot_file in snapshot_files.items()
        ):
            raise RepositoryCoverageEvidenceError(
                "tracked index entry does not match the active snapshot"
            )

    def _source_tree_oid(
        self,
        root: Path,
        base_sha: str,
        *,
        deadline: float | None,
    ) -> str:
        try:
            process = self._run_git(
                root,
                ("rev-parse", f"{base_sha}^{{tree}}"),
                deadline=deadline,
            )
            value = process.stdout.decode("ascii").strip()
        except (UnicodeDecodeError, RepositoryCoverageEvidenceError) as exc:
            raise RepositoryCoverageEvidenceError(
                "repository source-tree verification failed"
            ) from exc
        if not _OBJECT_ID.fullmatch(value):
            raise RepositoryCoverageEvidenceError(
                "repository source-tree object ID is invalid"
            )
        return value

    def _run_git(
        self,
        root: Path,
        arguments: tuple[str, ...],
        *,
        allowed_returncodes: tuple[int, ...] = (0,),
        deadline: float | None = None,
    ) -> subprocess.CompletedProcess[bytes]:
        command_deadline = time.monotonic() + self.git_timeout_seconds
        if deadline is not None:
            if deadline <= time.monotonic():
                raise RepositoryCoverageEvidenceError(
                    "bounded Git verification exceeded its operation deadline"
                )
            command_deadline = min(command_deadline, deadline)
        try:
            resolved_root = root.resolve()
            environment = {
                "PATH": os.environ.get("PATH", ""),
                "HOME": os.environ.get("HOME", ""),
                "GIT_TERMINAL_PROMPT": "0",
                "GIT_CONFIG_NOSYSTEM": "1",
                "GIT_CONFIG_SYSTEM": os.devnull,
                "GIT_CONFIG_GLOBAL": os.devnull,
                "GIT_NO_REPLACE_OBJECTS": "1",
                "GIT_NO_LAZY_FETCH": "1",
                "GIT_OPTIONAL_LOCKS": "0",
                "GIT_PAGER": "cat",
                "PAGER": "cat",
                "LC_ALL": "C",
            }
            command = [
                "git",
                "--no-replace-objects",
                "-c",
                "core.hooksPath=/dev/null",
                "-c",
                "credential.helper=",
                "-c",
                "credential.interactive=never",
                "-c",
                "protocol.ext.allow=never",
                "-c",
                "protocol.allow=never",
                "-c",
                "core.fsmonitor=false",
                "-c",
                "diff.external=",
                "-C",
                str(resolved_root),
                *arguments,
            ]
            process = subprocess.Popen(
                command,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
                start_new_session=os.name == "posix",
                env=environment,
            )
        except (OSError, RuntimeError, ValueError) as exc:
            raise RepositoryCoverageEvidenceError(
                "bounded Git verification failed"
            ) from exc
        if process.stdout is None or process.stderr is None:
            process.kill()
            raise RepositoryCoverageEvidenceError("bounded Git verification failed")

        def kill_process_group() -> None:
            try:
                if os.name == "posix":
                    os.killpg(process.pid, signal.SIGKILL)
                else:
                    process.kill()
            except OSError:
                pass

        selector: selectors.BaseSelector | None = None
        stdout = bytearray()
        stderr = bytearray()
        overflow = False
        timed_out = False
        try:
            selector = selectors.DefaultSelector()
            streams = {
                process.stdout: stdout,
                process.stderr: stderr,
            }
            for stream in streams:
                os.set_blocking(stream.fileno(), False)
                selector.register(stream, selectors.EVENT_READ)
            while selector.get_map():
                remaining = command_deadline - time.monotonic()
                if remaining <= 0:
                    timed_out = True
                    kill_process_group()
                    break
                events = selector.select(timeout=remaining)
                if not events:
                    timed_out = True
                    kill_process_group()
                    break
                for key, _mask in events:
                    try:
                        chunk = os.read(key.fd, 65_536)
                    except BlockingIOError:
                        continue
                    if not chunk:
                        selector.unregister(key.fileobj)
                        continue
                    output = streams[key.fileobj]
                    available = self.git_output_max_bytes - len(stdout) - len(stderr)
                    if len(chunk) > available:
                        output.extend(chunk[:available])
                        overflow = True
                        kill_process_group()
                        break
                    output.extend(chunk)
                if overflow:
                    break
            if not timed_out and not overflow:
                remaining = command_deadline - time.monotonic()
                if remaining <= 0:
                    timed_out = True
                    kill_process_group()
                else:
                    try:
                        process.wait(timeout=remaining)
                    except subprocess.TimeoutExpired:
                        timed_out = True
                        kill_process_group()
            if timed_out:
                raise RepositoryCoverageEvidenceError("bounded Git verification failed")
            if deadline is not None and time.monotonic() > deadline:
                raise RepositoryCoverageEvidenceError(
                    "bounded Git verification exceeded its operation deadline"
                )
            if overflow:
                raise RepositoryCoverageEvidenceError(
                    "bounded Git verification exceeded its output limit"
                )
            if process.returncode not in allowed_returncodes:
                raise RepositoryCoverageEvidenceError("bounded Git verification failed")
            return subprocess.CompletedProcess(
                command,
                process.returncode,
                stdout=bytes(stdout),
                stderr=bytes(stderr),
            )
        except RepositoryCoverageEvidenceError:
            raise
        except (OSError, RuntimeError, ValueError) as exc:
            kill_process_group()
            raise RepositoryCoverageEvidenceError(
                "bounded Git verification failed"
            ) from exc
        finally:
            if process.poll() is None:
                kill_process_group()
            try:
                process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                kill_process_group()
            if selector is not None:
                try:
                    selector.close()
                except OSError:
                    pass
            for stream in (process.stdout, process.stderr):
                try:
                    stream.close()
                except OSError:
                    pass

    def _policy_sha256(self) -> str:
        return hashlib.sha256(
            _canonical_json(
                {
                    "schema_version": "1",
                    "coverage_evidence_policy_version": COVERAGE_EVIDENCE_POLICY_VERSION,
                    "dispatch_evidence_policy_version": DISPATCH_EVIDENCE_POLICY_VERSION,
                    "receipt_format": "uca-trusted-test-coverage-v1",
                    "context_format": "test-id-line-ranges-v1",
                    "symbol_mapping": "python-call-graph-span-intersection-v1",
                    "run_max_bytes": self.run_max_bytes,
                    "evidence_max_bytes": self.evidence_max_bytes,
                    "max_source_bytes": self.max_source_bytes,
                    "policy_max_bytes": self.policy_max_bytes,
                    "profile_max_bytes": self.profile_max_bytes,
                    "max_profiles": self.max_profiles,
                    "max_scope_files": self.max_scope_files,
                    "max_tests": self.max_tests,
                    "max_files_per_test": self.max_files_per_test,
                    "max_file_observations": self.max_file_observations,
                    "max_ranges_per_file": self.max_ranges_per_file,
                    "max_ranges": self.max_ranges,
                    "max_json_items": self.max_json_items,
                    "max_json_depth": self.max_json_depth,
                    "max_covered_lines": self.max_covered_lines,
                    "max_symbol_bindings": self.max_symbol_bindings,
                    "max_symbol_evaluations": self.max_symbol_evaluations,
                    "max_symbol_output_bytes": self.max_symbol_output_bytes,
                    "max_test_id_bytes": self.max_test_id_bytes,
                    "git_timeout_seconds": self.git_timeout_seconds,
                    "git_output_max_bytes": self.git_output_max_bytes,
                }
            ).encode("utf-8")
        ).hexdigest()

    @staticmethod
    def _validate_project_id(project_id: str) -> None:
        if not _PROJECT_ID.fullmatch(project_id):
            raise RepositoryCoverageEvidenceError("project ID is invalid")

    @staticmethod
    def _validate_predecessor_pair(reference: str | None, sha256: str | None) -> None:
        if (reference is None) != (sha256 is None):
            raise RepositoryCoverageEvidenceError(
                "expected coverage-evidence predecessor reference and hash must be paired"
            )


def trusted_test_policy_sha256(policy: SafeModePolicy) -> str:
    return hashlib.sha256(
        _canonical_json(policy.model_dump(mode="json")).encode("utf-8")
    ).hexdigest()


def trusted_test_profile_sha256(profile: TestProfile) -> str:
    return hashlib.sha256(
        _canonical_json(profile.model_dump(mode="json")).encode("utf-8")
    ).hexdigest()


@dataclass
class _JsonFrame:
    kind: Literal["object", "array"]
    label: str | None = None
    schema: str | None = None
    item_schema: str | None = None
    pending_key: str | None = None
    seen_keys: set[str] = field(default_factory=set)
    count: int = 0
    expecting_value: bool = True


_JSON_SCALAR_ITEMS = "scalar-items"
_COVERAGE_JSON_FIELDS: dict[str, dict[str, str | None]] = {
    "trusted_run": {
        "schema_version": None,
        "producer": None,
        "context_format": None,
        "run_id": None,
        "project_id": None,
        "repository_url": None,
        "base_ref": None,
        "base_sha": None,
        "tracked_source_clean_before": None,
        "tracked_source_clean_after": None,
        "source_tree_before_oid": None,
        "source_tree_after_oid": None,
        "repository_snapshot_ref": None,
        "repository_snapshot_sha256": None,
        "dependency_graph_ref": None,
        "dependency_graph_sha256": None,
        "call_graph_ref": None,
        "call_graph_sha256": None,
        "dispatch_evidence_ref": None,
        "dispatch_evidence_sha256": None,
        "trusted_test_policy_sha256": None,
        "profiles": "profile",
        "coverage_scope": "scope_file",
        "tests": "trusted_test",
        "unattributed_files": "trusted_file",
    },
    "coverage_evidence": {
        "schema_version": None,
        "project_id": None,
        "repository_url": None,
        "base_ref": None,
        "base_sha": None,
        "source_tree_oid": None,
        "namespace": None,
        "repository_snapshot_ref": None,
        "repository_snapshot_sha256": None,
        "dependency_graph_ref": None,
        "dependency_graph_sha256": None,
        "call_graph_ref": None,
        "call_graph_sha256": None,
        "dispatch_evidence_ref": None,
        "dispatch_evidence_sha256": None,
        "trusted_run_ref": None,
        "trusted_run_sha256": None,
        "test_run_id": None,
        "trusted_test_policy_sha256": None,
        "policy_sha256": None,
        "symbol_mapping": None,
        "previous_evidence_ref": None,
        "previous_evidence_sha256": None,
        "profiles": "profile",
        "coverage_scope": "scope_file",
        "tests": "evidence_test",
        "unattributed_files": "evidence_file",
    },
    "profile": {
        "profile_id": None,
        "profile_sha256": None,
        "passed": None,
        "returncode": None,
        "collection_complete": None,
        "execution_complete": None,
        "test_count": None,
    },
    "scope_file": {"path": None, "source_sha256": None},
    "trusted_test": {
        "profile_id": None,
        "test_id": None,
        "test_path": None,
        "test_source_sha256": None,
        "covered_files": "trusted_file",
    },
    "evidence_test": {
        "profile_id": None,
        "test_id": None,
        "test_path": None,
        "test_source_sha256": None,
        "covered_files": "evidence_file",
    },
    "trusted_file": {
        "path": None,
        "source_sha256": None,
        "ranges": "line_range",
    },
    "evidence_file": {
        "path": None,
        "source_sha256": None,
        "ranges": "line_range",
        "covered_symbol_ids": _JSON_SCALAR_ITEMS,
    },
    "line_range": {"start_line": None, "end_line": None},
}
_COVERAGE_JSON_REQUIRED_FIELDS = {
    "trusted_run": frozenset(
        {
            "run_id",
            "project_id",
            "repository_url",
            "base_ref",
            "base_sha",
            "source_tree_before_oid",
            "source_tree_after_oid",
            "repository_snapshot_ref",
            "repository_snapshot_sha256",
            "dependency_graph_ref",
            "dependency_graph_sha256",
            "call_graph_ref",
            "call_graph_sha256",
            "dispatch_evidence_ref",
            "dispatch_evidence_sha256",
            "trusted_test_policy_sha256",
            "profiles",
            "coverage_scope",
            "tests",
        }
    ),
    "coverage_evidence": frozenset(
        {
            "project_id",
            "repository_url",
            "base_ref",
            "base_sha",
            "source_tree_oid",
            "namespace",
            "repository_snapshot_ref",
            "repository_snapshot_sha256",
            "dependency_graph_ref",
            "dependency_graph_sha256",
            "call_graph_ref",
            "call_graph_sha256",
            "dispatch_evidence_ref",
            "dispatch_evidence_sha256",
            "trusted_run_ref",
            "trusted_run_sha256",
            "test_run_id",
            "trusted_test_policy_sha256",
            "policy_sha256",
            "profiles",
            "coverage_scope",
            "tests",
        }
    ),
    "profile": frozenset(_COVERAGE_JSON_FIELDS["profile"]),
    "scope_file": frozenset(_COVERAGE_JSON_FIELDS["scope_file"]),
    "trusted_test": frozenset(
        {"profile_id", "test_id", "test_path", "test_source_sha256"}
    ),
    "evidence_test": frozenset(
        {"profile_id", "test_id", "test_path", "test_source_sha256"}
    ),
    "trusted_file": frozenset(_COVERAGE_JSON_FIELDS["trusted_file"]),
    "evidence_file": frozenset({"path", "source_sha256", "ranges"}),
    "line_range": frozenset(_COVERAGE_JSON_FIELDS["line_range"]),
}


def _preflight_coverage_json(
    content: str,
    *,
    context: str,
    max_profiles: int,
    max_scope_files: int,
    max_tests: int,
    max_files_per_test: int,
    max_file_observations: int,
    max_ranges_per_file: int,
    max_ranges: int,
    max_json_items: int,
    max_json_depth: int,
) -> None:
    """Count hostile JSON structures before allocating nested Pydantic models."""

    stack: list[_JsonFrame] = []
    aggregate_counts: defaultdict[str, int] = defaultdict(int)
    json_items = 0
    root_schema = (
        "trusted_run" if context == "trusted coverage run" else "coverage_evidence"
    )

    def fail_shape() -> None:
        raise RepositoryCoverageEvidenceError(
            f"{context} contains an incompatible JSON member shape"
        )

    def consume_scalar(frame: _JsonFrame) -> None:
        if frame.kind != "object" or frame.pending_key is None or frame.schema is None:
            fail_shape()
        if _COVERAGE_JSON_FIELDS[frame.schema][frame.pending_key] is not None:
            fail_shape()
        frame.pending_key = None

    def add_array_item(frame: _JsonFrame, first_character: str) -> None:
        nonlocal json_items
        frame.count += 1
        frame.expecting_value = False
        json_items += 1
        if json_items > max_json_items:
            raise RepositoryCoverageEvidenceError(
                f"{context} exceeds its structural-item limit"
            )
        if frame.item_schema == _JSON_SCALAR_ITEMS:
            if first_character in "{[":
                fail_shape()
        elif first_character != "{":
            fail_shape()
        label = frame.label
        if label is None:
            return
        aggregate_counts[label] += 1
        count = aggregate_counts[label]
        if label == "profiles" and count > max_profiles:
            raise RepositoryCoverageEvidenceError(
                f"{context} exceeds its profile limit"
            )
        if label == "coverage_scope" and count > max_scope_files:
            raise RepositoryCoverageEvidenceError(
                f"{context} exceeds its scope-file limit"
            )
        if label == "tests" and count > max_tests:
            raise RepositoryCoverageEvidenceError(f"{context} exceeds its test limit")
        if label == "covered_files":
            if frame.count > max_files_per_test:
                raise RepositoryCoverageEvidenceError(
                    f"{context} exceeds its per-test file limit"
                )
            if count + aggregate_counts["unattributed_files"] > max_file_observations:
                raise RepositoryCoverageEvidenceError(
                    f"{context} exceeds its file-observation limit"
                )
        if label == "unattributed_files":
            if count > max_scope_files:
                raise RepositoryCoverageEvidenceError(
                    f"{context} exceeds its scope-file limit"
                )
            if count + aggregate_counts["covered_files"] > max_file_observations:
                raise RepositoryCoverageEvidenceError(
                    f"{context} exceeds its file-observation limit"
                )
        if label == "ranges":
            if frame.count > max_ranges_per_file:
                raise RepositoryCoverageEvidenceError(
                    f"{context} exceeds its per-file range limit"
                )
            if count > max_ranges:
                raise RepositoryCoverageEvidenceError(
                    f"{context} exceeds its line-range limit"
                )

    index = 0
    length = len(content)
    while index < length:
        character = content[index]
        if character in " \t\r\n":
            index += 1
            continue
        if (
            stack
            and stack[-1].kind == "array"
            and stack[-1].expecting_value
            and character != "]"
        ):
            add_array_item(stack[-1], character)
        if character == '"':
            end = _json_string_end(content, index)
            lookahead = end
            while lookahead < length and content[lookahead] in " \t\r\n":
                lookahead += 1
            if (
                stack
                and stack[-1].kind == "object"
                and lookahead < length
                and content[lookahead] == ":"
            ):
                frame = stack[-1]
                if frame.pending_key is not None or frame.schema is None:
                    fail_shape()
                if end - index > 258:
                    raise RepositoryCoverageEvidenceError(
                        f"{context} contains an oversized JSON field name"
                    )
                try:
                    key = json.loads(content[index:end])
                except (TypeError, ValueError) as exc:
                    raise RepositoryCoverageEvidenceError(
                        f"{context} contains malformed JSON structure"
                    ) from exc
                json_items += 1
                if json_items > max_json_items:
                    raise RepositoryCoverageEvidenceError(
                        f"{context} exceeds its structural-item limit"
                    )
                fields = _COVERAGE_JSON_FIELDS[frame.schema]
                if key not in fields:
                    raise RepositoryCoverageEvidenceError(
                        f"{context} contains an unexpected JSON field"
                    )
                if key in frame.seen_keys:
                    raise RepositoryCoverageEvidenceError(
                        f"{context} contains a duplicate JSON field"
                    )
                frame.seen_keys.add(key)
                frame.pending_key = key
            elif stack and stack[-1].kind == "object":
                consume_scalar(stack[-1])
            index = end
            continue
        if character in "{[":
            if len(stack) >= max_json_depth:
                raise RepositoryCoverageEvidenceError(
                    f"{context} exceeds its JSON-depth limit"
                )
            if character == "{":
                if not stack:
                    schema = root_schema
                elif stack[-1].kind == "array":
                    schema = stack[-1].item_schema
                    if schema in {None, _JSON_SCALAR_ITEMS}:
                        fail_shape()
                else:
                    fail_shape()
                stack.append(_JsonFrame(kind="object", schema=schema))
            else:
                if not stack or stack[-1].kind != "object":
                    fail_shape()
                parent = stack[-1]
                if parent.pending_key is None or parent.schema is None:
                    fail_shape()
                label = parent.pending_key
                item_schema = _COVERAGE_JSON_FIELDS[parent.schema][label]
                if item_schema is None:
                    fail_shape()
                parent.pending_key = None
                stack.append(
                    _JsonFrame(
                        kind="array",
                        label=label,
                        item_schema=item_schema,
                    )
                )
        elif character == ",":
            if stack and stack[-1].kind == "array":
                if stack[-1].expecting_value or stack[-1].count == 0:
                    fail_shape()
                stack[-1].expecting_value = True
            elif stack:
                if stack[-1].pending_key is not None:
                    fail_shape()
            else:
                fail_shape()
        elif character == "]":
            if not stack or stack[-1].kind != "array":
                raise RepositoryCoverageEvidenceError(
                    f"{context} contains malformed JSON structure"
                )
            if stack[-1].count and stack[-1].expecting_value:
                fail_shape()
            stack.pop()
        elif character == "}":
            if not stack or stack[-1].kind != "object":
                raise RepositoryCoverageEvidenceError(
                    f"{context} contains malformed JSON structure"
                )
            frame = stack.pop()
            if frame.pending_key is not None or frame.schema is None:
                fail_shape()
            required = _COVERAGE_JSON_REQUIRED_FIELDS[frame.schema]
            if not required.issubset(frame.seen_keys):
                raise RepositoryCoverageEvidenceError(
                    f"{context} is missing a required JSON field"
                )
        elif character not in ":":
            if stack and stack[-1].kind == "object":
                consume_scalar(stack[-1])
            while index + 1 < length and content[index + 1] not in " \t\r\n,]}":
                index += 1
        index += 1
    if stack:
        raise RepositoryCoverageEvidenceError(
            f"{context} contains malformed JSON structure"
        )


def _json_string_end(content: str, start: int) -> int:
    index = start + 1
    while index < len(content):
        character = content[index]
        if character == '"':
            return index + 1
        if ord(character) < 32:
            break
        if character == "\\":
            index += 1
            if index >= len(content):
                break
        index += 1
    raise RepositoryCoverageEvidenceError(
        "coverage JSON contains an unterminated string"
    )


def _strictly_increasing(
    values: tuple[str, ...] | tuple[tuple[str, str], ...],
) -> bool:
    return all(left < right for left, right in zip(values, values[1:], strict=False))


def _range_line_count(ranges: tuple[CoverageLineRange, ...]) -> int:
    return sum(item.end_line - item.start_line + 1 for item in ranges)


def _utf8_line_count(data: bytes) -> int:
    decoder = codecs.getincrementaldecoder("utf-8")(errors="strict")
    line_count = 0
    saw_character = False
    last_was_boundary = False
    pending_carriage_return = False
    boundaries = frozenset(
        ("\n", "\r", "\v", "\f", "\x1c", "\x1d", "\x1e", "\x85", "\u2028", "\u2029")
    )

    for offset in range(0, len(data), 65_536):
        decoded = decoder.decode(memoryview(data)[offset : offset + 65_536], final=False)
        for character in decoded:
            saw_character = True
            if pending_carriage_return and character == "\n":
                pending_carriage_return = False
                last_was_boundary = True
                continue
            pending_carriage_return = False
            if character in boundaries:
                line_count += 1
                last_was_boundary = True
                pending_carriage_return = character == "\r"
            else:
                last_was_boundary = False
    decoder.decode(b"", final=True)
    if saw_character and not last_was_boundary:
        line_count += 1
    return line_count


def _git_blob_oid(data: bytes, expected_oid: str) -> str:
    if len(expected_oid) == 40:
        digest = hashlib.new("sha1", usedforsecurity=False)
    elif len(expected_oid) == 64:
        digest = hashlib.sha256()
    else:
        raise RepositoryCoverageEvidenceError("Git blob object ID is invalid")
    digest.update(f"blob {len(data)}\0".encode("ascii"))
    digest.update(data)
    return digest.hexdigest()


def _ranges_overlap_span(
    ranges: tuple[CoverageLineRange, ...],
    range_starts: tuple[int, ...],
    start_line: int,
    end_line: int,
) -> bool:
    index = bisect_right(range_starts, end_line) - 1
    return index >= 0 and ranges[index].end_line >= start_line


def _test_key(item: TrustedTestCoverage) -> tuple[str, str]:
    return item.profile_id, item.test_id


def _evidence_test_key(item: TestCoverageEvidence) -> tuple[str, str]:
    return item.profile_id, item.test_id


def _bounded_canonical_json(
    value: object,
    *,
    max_bytes: int,
    error_message: str,
) -> tuple[str, str]:
    buffer = io.StringIO()
    digest = hashlib.sha256()
    total_bytes = 0
    encoder = json.JSONEncoder(
        separators=(",", ":"),
        sort_keys=True,
        ensure_ascii=False,
    )
    for chunk in encoder.iterencode(value):
        encoded = chunk.encode("utf-8")
        total_bytes += len(encoded)
        if total_bytes > max_bytes:
            raise RepositoryCoverageEvidenceError(error_message)
        buffer.write(chunk)
        digest.update(encoded)
    return buffer.getvalue(), digest.hexdigest()


def _canonical_json(value: object) -> str:
    return json.dumps(value, separators=(",", ":"), sort_keys=True, ensure_ascii=False)
