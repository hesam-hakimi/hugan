from __future__ import annotations

import hashlib
import hmac
import json
import re
from enum import StrEnum
from typing import Any, Literal

from pydantic import Field, field_validator, model_validator

from universal_coding_agent.core.models import FrozenModel
from universal_coding_agent.core.safe_models import SafeModePolicy
from universal_coding_agent.product.coverage_evidence import (
    DEFAULT_COVERAGE_MAX_PROFILES,
    RepositoryCoverageEvidence,
    RepositoryCoverageEvidenceError,
    RepositoryCoverageEvidenceService,
    TrustedCoverageRun,
    trusted_test_policy_sha256,
    trusted_test_profile_sha256,
)
from universal_coding_agent.storage.artifacts import ArtifactStore

DEFAULT_COVERAGE_QUALIFICATION_MAX_BYTES = 512_000
DEFAULT_COVERAGE_SELECTION_ADVISORY_MAX_BYTES = 512_000
DEFAULT_COVERAGE_SELECTION_MAX_JSON_ITEMS = 8_192
DEFAULT_COVERAGE_SELECTION_MAX_JSON_DEPTH = 16
COVERAGE_SELECTION_POLICY_VERSION = "1"
_PROJECT_ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")
_OBJECT_ID = re.compile(r"^[0-9a-f]{40,64}$")


class RepositoryCoverageSelectionError(ValueError):
    """Coverage eligibility cannot satisfy its bounded provenance contract."""


class CoverageSelectionDisposition(StrEnum):
    ELIGIBLE = "ELIGIBLE"
    FULL_PROFILE_FALLBACK = "FULL_PROFILE_FALLBACK"


class CoverageSelectionFallbackReason(StrEnum):
    QUALIFICATION_MISSING = "qualification_missing"
    REQUIRED_IDENTITY_MISSING = "required_identity_missing"
    COVERAGE_PROFILE_MISSING = "coverage_profile_missing"
    QUALIFIED_IDENTITY_MISSING = "qualified_identity_missing"
    REQUIRED_PROFILE_MISMATCH = "required_profile_mismatch"
    EXECUTION_ENVIRONMENT_MISMATCH = "execution_environment_mismatch"
    COLLECTOR_IDENTITY_MISMATCH = "collector_identity_mismatch"
    COLLECTOR_CONFIGURATION_MISMATCH = "collector_configuration_mismatch"


class CoverageExecutionEnvironmentIdentity(FrozenModel):
    identity_format: Literal["execution-environment-manifest-sha256-v1"] = (
        "execution-environment-manifest-sha256-v1"
    )
    environment_id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}$")
    manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class CoverageCollectorIdentity(FrozenModel):
    identity_format: Literal["coverage-collector-config-sha256-v1"] = (
        "coverage-collector-config-sha256-v1"
    )
    collector_id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}$")
    collector_version: str = Field(min_length=1, max_length=256)
    collector_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    configuration_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @field_validator("collector_version")
    @classmethod
    def validate_version(cls, value: str) -> str:
        if value != value.strip() or any(ord(character) < 32 for character in value):
            raise ValueError(
                "coverage collector version contains surrounding whitespace or controls"
            )
        return value


class CoverageProfileIdentity(FrozenModel):
    profile_id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}$")
    profile_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    execution_environment: CoverageExecutionEnvironmentIdentity
    collector: CoverageCollectorIdentity

    def canonical_hash(self) -> str:
        return hashlib.sha256(
            _canonical_json(self.model_dump(mode="json")).encode("utf-8")
        ).hexdigest()


class CoverageSelectionRequiredIdentities(FrozenModel):
    schema_version: Literal["1"] = "1"
    profiles: tuple[CoverageProfileIdentity, ...] = Field(
        default=(), max_length=DEFAULT_COVERAGE_MAX_PROFILES
    )

    @field_validator("profiles")
    @classmethod
    def validate_profiles(
        cls, values: tuple[CoverageProfileIdentity, ...]
    ) -> tuple[CoverageProfileIdentity, ...]:
        _validate_profile_identity_order(values, context="required coverage identities")
        return values

    def canonical_content(self) -> str:
        return _canonical_json(self.model_dump(mode="json"))

    def canonical_hash(self) -> str:
        return hashlib.sha256(self.canonical_content().encode("utf-8")).hexdigest()


class TrustedCoverageQualificationReceipt(FrozenModel):
    """Host-attested runtime identities bound to one exact v1 coverage run."""

    schema_version: Literal["1"] = "1"
    producer: Literal["uca-trusted-coverage-qualification-v1"] = (
        "uca-trusted-coverage-qualification-v1"
    )
    attestation: Literal["host-attested"] = "host-attested"
    project_id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")
    repository_url: str = Field(min_length=1, max_length=2048)
    base_ref: str = Field(min_length=1, max_length=256)
    base_sha: str = Field(pattern=r"^[0-9a-f]{40,64}$")
    source_tree_oid: str = Field(pattern=r"^[0-9a-f]{40,64}$")
    coverage_evidence_ref: str = Field(pattern=r"^artifact://[a-zA-Z0-9._/-]+$")
    coverage_evidence_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    trusted_run_ref: str = Field(pattern=r"^artifact://[a-zA-Z0-9._/-]+$")
    trusted_run_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    test_run_id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")
    trusted_test_policy_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    profile_identities: tuple[CoverageProfileIdentity, ...] = Field(
        default=(), max_length=DEFAULT_COVERAGE_MAX_PROFILES
    )

    @field_validator("profile_identities")
    @classmethod
    def validate_profile_identities(
        cls, values: tuple[CoverageProfileIdentity, ...]
    ) -> tuple[CoverageProfileIdentity, ...]:
        _validate_profile_identity_order(values, context="coverage qualification")
        return values

    def canonical_content(self) -> str:
        return _canonical_json(self.model_dump(mode="json"))

    def canonical_hash(self) -> str:
        return hashlib.sha256(self.canonical_content().encode("utf-8")).hexdigest()


class CoverageSelectionAdvisory(FrozenModel):
    """Identity eligibility only; this artifact never selects or executes tests."""

    schema_version: Literal["1"] = "1"
    advisory_format: Literal["coverage-identity-eligibility-v1"] = (
        "coverage-identity-eligibility-v1"
    )
    project_id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")
    repository_url: str = Field(min_length=1, max_length=2048)
    base_ref: str = Field(min_length=1, max_length=256)
    base_sha: str = Field(pattern=r"^[0-9a-f]{40,64}$")
    source_tree_oid: str = Field(pattern=r"^[0-9a-f]{40,64}$")
    coverage_evidence_ref: str = Field(pattern=r"^artifact://[a-zA-Z0-9._/-]+$")
    coverage_evidence_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    trusted_run_ref: str = Field(pattern=r"^artifact://[a-zA-Z0-9._/-]+$")
    trusted_run_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    test_run_id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")
    trusted_test_policy_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    qualification_ref: str | None = Field(default=None, pattern=r"^artifact://[a-zA-Z0-9._/-]+$")
    qualification_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    required_identities_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    policy_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    requested_profile_ids: tuple[str, ...] = Field(
        min_length=1, max_length=DEFAULT_COVERAGE_MAX_PROFILES
    )
    disposition: CoverageSelectionDisposition
    fallback_profile_ids: tuple[str, ...] = Field(
        default=(), max_length=DEFAULT_COVERAGE_MAX_PROFILES
    )
    fallback_reasons: tuple[CoverageSelectionFallbackReason, ...] = ()
    selects_test_ids: Literal[False] = False
    authorizes_execution: Literal[False] = False
    claims_minimality: Literal[False] = False

    @field_validator("requested_profile_ids", "fallback_profile_ids")
    @classmethod
    def validate_profile_ids(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        if len(values) != len(set(values)):
            raise ValueError("coverage advisory profile IDs must be unique")
        if any(
            re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}", value) is None for value in values
        ):
            raise ValueError("coverage advisory profile ID is invalid")
        return values

    @field_validator("fallback_reasons")
    @classmethod
    def validate_reasons(
        cls, values: tuple[CoverageSelectionFallbackReason, ...]
    ) -> tuple[CoverageSelectionFallbackReason, ...]:
        if values != tuple(sorted(set(values), key=lambda item: item.value)):
            raise ValueError("coverage fallback reasons must be unique and sorted")
        return values

    @model_validator(mode="after")
    def validate_disposition(self) -> CoverageSelectionAdvisory:
        qualification_present = self.qualification_ref is not None
        if qualification_present != (self.qualification_sha256 is not None):
            raise ValueError("coverage qualification reference and hash must be paired")
        if self.disposition is CoverageSelectionDisposition.ELIGIBLE:
            if not qualification_present:
                raise ValueError("eligible coverage requires a qualification receipt")
            if self.fallback_profile_ids or self.fallback_reasons:
                raise ValueError("eligible coverage cannot contain fallback data")
        elif self.fallback_profile_ids != self.requested_profile_ids or not self.fallback_reasons:
            raise ValueError(
                "full-profile fallback must preserve every requested profile and a reason"
            )
        return self

    def canonical_content(self) -> str:
        return _canonical_json(self.model_dump(mode="json"))

    def canonical_hash(self) -> str:
        return hashlib.sha256(self.canonical_content().encode("utf-8")).hexdigest()


class RepositoryCoverageSelectionResult(FrozenModel):
    advisory_ref: str = Field(pattern=r"^artifact://[a-zA-Z0-9._/-]+$")
    advisory_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    advisory: CoverageSelectionAdvisory


class RepositoryCoverageSelectionService:
    """Issue bounded advisory eligibility without selecting or running any test."""

    def __init__(
        self,
        artifacts: ArtifactStore,
        coverage_evidence: RepositoryCoverageEvidenceService,
        *,
        qualification_max_bytes: int = DEFAULT_COVERAGE_QUALIFICATION_MAX_BYTES,
        advisory_max_bytes: int = DEFAULT_COVERAGE_SELECTION_ADVISORY_MAX_BYTES,
        max_profiles: int = DEFAULT_COVERAGE_MAX_PROFILES,
        max_json_items: int = DEFAULT_COVERAGE_SELECTION_MAX_JSON_ITEMS,
        max_json_depth: int = DEFAULT_COVERAGE_SELECTION_MAX_JSON_DEPTH,
    ) -> None:
        limits = (
            qualification_max_bytes,
            advisory_max_bytes,
            max_profiles,
            max_json_items,
            max_json_depth,
        )
        if any(type(limit) is not int for limit in limits):
            raise ValueError("coverage-selection limits must be integers")
        if any(limit < 1 for limit in limits):
            raise ValueError("coverage-selection limits must be positive")
        if max_profiles > DEFAULT_COVERAGE_MAX_PROFILES:
            raise ValueError("coverage-selection profile limit exceeds its schema maximum")
        self.artifacts = artifacts
        self.coverage_evidence = coverage_evidence
        self.qualification_max_bytes = qualification_max_bytes
        self.advisory_max_bytes = advisory_max_bytes
        self.max_profiles = max_profiles
        self.max_json_items = max_json_items
        self.max_json_depth = max_json_depth

    def assess_eligibility(
        self,
        *,
        project_id: str,
        expected_base_sha: str,
        trusted_test_policy: SafeModePolicy,
        requested_profile_ids: tuple[str, ...],
        expected_coverage_evidence_ref: str,
        expected_coverage_evidence_sha256: str,
        required_identities: CoverageSelectionRequiredIdentities | None,
        qualification_ref: str | None,
        qualification_sha256: str | None,
    ) -> RepositoryCoverageSelectionResult:
        self._validate_request(
            project_id=project_id,
            expected_base_sha=expected_base_sha,
            trusted_test_policy=trusted_test_policy,
            requested_profile_ids=requested_profile_ids,
            required_identities=required_identities,
            qualification_ref=qualification_ref,
            qualification_sha256=qualification_sha256,
        )
        try:
            historical = self.coverage_evidence.verified_historical_evidence(
                project_id=project_id,
                trusted_test_policy=trusted_test_policy,
                expected_evidence_ref=expected_coverage_evidence_ref,
                expected_evidence_sha256=expected_coverage_evidence_sha256,
            )
            evidence = historical.evidence
            run = historical.run
        except RepositoryCoverageEvidenceError as exc:
            raise RepositoryCoverageSelectionError(str(exc)) from exc
        except (AttributeError, TypeError, ValueError) as exc:
            raise RepositoryCoverageSelectionError(
                "historical coverage evidence failed verification"
            ) from exc
        if not isinstance(evidence, RepositoryCoverageEvidence) or not isinstance(
            run, TrustedCoverageRun
        ):
            raise RepositoryCoverageSelectionError(
                "historical coverage evidence returned an invalid result"
            )
        self._verify_historical_binding(
            project_id=project_id,
            expected_base_sha=expected_base_sha,
            trusted_test_policy=trusted_test_policy,
            expected_evidence_sha256=expected_coverage_evidence_sha256,
            evidence=evidence,
            run=run,
        )

        qualification: TrustedCoverageQualificationReceipt | None = None
        if qualification_ref is not None and qualification_sha256 is not None:
            qualification = self._load_qualification(qualification_ref, qualification_sha256)
            self._verify_qualification(
                qualification,
                evidence=evidence,
                run=run,
                evidence_ref=expected_coverage_evidence_ref,
                evidence_sha256=expected_coverage_evidence_sha256,
            )

        reasons = self._fallback_reasons(
            trusted_test_policy=trusted_test_policy,
            requested_profile_ids=requested_profile_ids,
            run=run,
            qualification=qualification,
            required_identities=required_identities,
        )
        disposition = (
            CoverageSelectionDisposition.FULL_PROFILE_FALLBACK
            if reasons
            else CoverageSelectionDisposition.ELIGIBLE
        )
        requirements = required_identities or CoverageSelectionRequiredIdentities()
        advisory = CoverageSelectionAdvisory(
            project_id=project_id,
            repository_url=evidence.repository_url,
            base_ref=evidence.base_ref,
            base_sha=evidence.base_sha,
            source_tree_oid=evidence.source_tree_oid,
            coverage_evidence_ref=expected_coverage_evidence_ref,
            coverage_evidence_sha256=expected_coverage_evidence_sha256,
            trusted_run_ref=evidence.trusted_run_ref,
            trusted_run_sha256=evidence.trusted_run_sha256,
            test_run_id=evidence.test_run_id,
            trusted_test_policy_sha256=evidence.trusted_test_policy_sha256,
            qualification_ref=qualification_ref,
            qualification_sha256=qualification_sha256,
            required_identities_sha256=requirements.canonical_hash(),
            policy_sha256=self._policy_sha256(),
            requested_profile_ids=requested_profile_ids,
            disposition=disposition,
            fallback_profile_ids=(requested_profile_ids if reasons else ()),
            fallback_reasons=reasons,
        )
        return self._write_advisory(advisory)

    def verified_advisory(
        self,
        advisory_ref: str,
        advisory_sha256: str,
    ) -> CoverageSelectionAdvisory:
        advisory = self._load_advisory(advisory_ref, advisory_sha256)
        if not hmac.compare_digest(advisory.policy_sha256, self._policy_sha256()):
            raise RepositoryCoverageSelectionError(
                "coverage-selection advisory policy does not match"
            )
        return advisory

    def _validate_request(
        self,
        *,
        project_id: str,
        expected_base_sha: str,
        trusted_test_policy: SafeModePolicy,
        requested_profile_ids: tuple[str, ...],
        required_identities: CoverageSelectionRequiredIdentities | None,
        qualification_ref: str | None,
        qualification_sha256: str | None,
    ) -> None:
        if _PROJECT_ID.fullmatch(project_id) is None:
            raise RepositoryCoverageSelectionError("project ID is invalid")
        if _OBJECT_ID.fullmatch(expected_base_sha) is None:
            raise RepositoryCoverageSelectionError("expected Base SHA is invalid")
        if (qualification_ref is None) != (qualification_sha256 is None):
            raise RepositoryCoverageSelectionError(
                "coverage qualification reference and hash must be paired"
            )
        if not requested_profile_ids:
            raise RepositoryCoverageSelectionError(
                "coverage eligibility requires at least one requested profile"
            )
        if len(requested_profile_ids) > self.max_profiles:
            raise RepositoryCoverageSelectionError(
                "coverage eligibility exceeds its requested-profile limit"
            )
        if len(requested_profile_ids) != len(set(requested_profile_ids)):
            raise RepositoryCoverageSelectionError("requested coverage profile IDs must be unique")
        policy_profiles = trusted_test_policy.profile_map()
        if any(profile_id not in policy_profiles for profile_id in requested_profile_ids):
            raise RepositoryCoverageSelectionError(
                "requested coverage profile is outside the trusted test policy"
            )
        if required_identities is not None:
            if len(required_identities.profiles) > self.max_profiles:
                raise RepositoryCoverageSelectionError(
                    "required coverage identities exceed the profile limit"
                )
            requested = set(requested_profile_ids)
            if any(item.profile_id not in requested for item in required_identities.profiles):
                raise RepositoryCoverageSelectionError(
                    "required coverage identity is outside the requested profiles"
                )

    def _verify_historical_binding(
        self,
        *,
        project_id: str,
        expected_base_sha: str,
        trusted_test_policy: SafeModePolicy,
        expected_evidence_sha256: str,
        evidence: RepositoryCoverageEvidence,
        run: TrustedCoverageRun,
    ) -> None:
        policy_sha256 = trusted_test_policy_sha256(trusted_test_policy)
        actual = (
            evidence.project_id,
            evidence.repository_url,
            evidence.base_ref,
            evidence.base_sha,
            evidence.source_tree_oid,
            evidence.test_run_id,
            evidence.trusted_test_policy_sha256,
            run.project_id,
            run.repository_url,
            run.base_ref,
            run.base_sha,
            run.source_tree_before_oid,
            run.source_tree_after_oid,
            run.run_id,
            run.trusted_test_policy_sha256,
            run.repository_snapshot_ref,
            run.repository_snapshot_sha256,
            run.dependency_graph_ref,
            run.dependency_graph_sha256,
            run.call_graph_ref,
            run.call_graph_sha256,
            run.dispatch_evidence_ref,
            run.dispatch_evidence_sha256,
        )
        expected = (
            project_id,
            evidence.repository_url,
            evidence.base_ref,
            expected_base_sha,
            evidence.source_tree_oid,
            run.run_id,
            policy_sha256,
            project_id,
            evidence.repository_url,
            evidence.base_ref,
            expected_base_sha,
            evidence.source_tree_oid,
            evidence.source_tree_oid,
            evidence.test_run_id,
            policy_sha256,
            evidence.repository_snapshot_ref,
            evidence.repository_snapshot_sha256,
            evidence.dependency_graph_ref,
            evidence.dependency_graph_sha256,
            evidence.call_graph_ref,
            evidence.call_graph_sha256,
            evidence.dispatch_evidence_ref,
            evidence.dispatch_evidence_sha256,
        )
        if actual != expected:
            raise RepositoryCoverageSelectionError(
                "historical coverage provenance conflicts with the eligibility request"
            )
        if not hmac.compare_digest(evidence.canonical_hash(), expected_evidence_sha256):
            raise RepositoryCoverageSelectionError(
                "historical coverage evidence canonical hash does not match"
            )
        if not hmac.compare_digest(run.canonical_hash(), evidence.trusted_run_sha256):
            raise RepositoryCoverageSelectionError(
                "historical coverage run canonical hash does not match"
            )

    def _verify_qualification(
        self,
        qualification: TrustedCoverageQualificationReceipt,
        *,
        evidence: RepositoryCoverageEvidence,
        run: TrustedCoverageRun,
        evidence_ref: str,
        evidence_sha256: str,
    ) -> None:
        actual = (
            qualification.project_id,
            qualification.repository_url,
            qualification.base_ref,
            qualification.base_sha,
            qualification.source_tree_oid,
            qualification.coverage_evidence_ref,
            qualification.coverage_evidence_sha256,
            qualification.trusted_run_ref,
            qualification.trusted_run_sha256,
            qualification.test_run_id,
            qualification.trusted_test_policy_sha256,
        )
        expected = (
            evidence.project_id,
            evidence.repository_url,
            evidence.base_ref,
            evidence.base_sha,
            evidence.source_tree_oid,
            evidence_ref,
            evidence_sha256,
            evidence.trusted_run_ref,
            evidence.trusted_run_sha256,
            evidence.test_run_id,
            evidence.trusted_test_policy_sha256,
        )
        if actual != expected:
            raise RepositoryCoverageSelectionError(
                "coverage qualification conflicts with its exact evidence provenance"
            )
        run_profiles = {item.profile_id: item for item in run.profiles}
        for identity in qualification.profile_identities:
            profile = run_profiles.get(identity.profile_id)
            if profile is None or not hmac.compare_digest(
                identity.profile_sha256, profile.profile_sha256
            ):
                raise RepositoryCoverageSelectionError(
                    "coverage qualification identity conflicts with its exact run profile"
                )

    def _fallback_reasons(
        self,
        *,
        trusted_test_policy: SafeModePolicy,
        requested_profile_ids: tuple[str, ...],
        run: TrustedCoverageRun,
        qualification: TrustedCoverageQualificationReceipt | None,
        required_identities: CoverageSelectionRequiredIdentities | None,
    ) -> tuple[CoverageSelectionFallbackReason, ...]:
        reasons: set[CoverageSelectionFallbackReason] = set()
        if qualification is None:
            reasons.add(CoverageSelectionFallbackReason.QUALIFICATION_MISSING)
        if required_identities is None:
            reasons.add(CoverageSelectionFallbackReason.REQUIRED_IDENTITY_MISSING)
        run_profiles = {item.profile_id: item for item in run.profiles}
        qualified = (
            {item.profile_id: item for item in qualification.profile_identities}
            if qualification is not None
            else {}
        )
        required = (
            {item.profile_id: item for item in required_identities.profiles}
            if required_identities is not None
            else {}
        )
        policy_profiles = trusted_test_policy.profile_map()
        for profile_id in requested_profile_ids:
            run_profile = run_profiles.get(profile_id)
            if run_profile is None:
                reasons.add(CoverageSelectionFallbackReason.COVERAGE_PROFILE_MISSING)
            qualified_identity = qualified.get(profile_id)
            if qualification is not None and qualified_identity is None:
                reasons.add(CoverageSelectionFallbackReason.QUALIFIED_IDENTITY_MISSING)
            required_identity = required.get(profile_id)
            if required_identities is not None and required_identity is None:
                reasons.add(CoverageSelectionFallbackReason.REQUIRED_IDENTITY_MISSING)
            if required_identity is None:
                continue
            expected_profile_sha256 = trusted_test_profile_sha256(policy_profiles[profile_id])
            if not hmac.compare_digest(required_identity.profile_sha256, expected_profile_sha256):
                reasons.add(CoverageSelectionFallbackReason.REQUIRED_PROFILE_MISMATCH)
            if qualified_identity is None:
                continue
            if hmac.compare_digest(
                required_identity.canonical_hash(),
                qualified_identity.canonical_hash(),
            ):
                continue
            if not hmac.compare_digest(
                required_identity.profile_sha256,
                qualified_identity.profile_sha256,
            ):
                reasons.add(CoverageSelectionFallbackReason.REQUIRED_PROFILE_MISMATCH)
            if required_identity.execution_environment != (
                qualified_identity.execution_environment
            ):
                reasons.add(CoverageSelectionFallbackReason.EXECUTION_ENVIRONMENT_MISMATCH)
            if (
                required_identity.collector.collector_id,
                required_identity.collector.collector_version,
                required_identity.collector.collector_sha256,
            ) != (
                qualified_identity.collector.collector_id,
                qualified_identity.collector.collector_version,
                qualified_identity.collector.collector_sha256,
            ):
                reasons.add(CoverageSelectionFallbackReason.COLLECTOR_IDENTITY_MISMATCH)
            if not hmac.compare_digest(
                required_identity.collector.configuration_sha256,
                qualified_identity.collector.configuration_sha256,
            ):
                reasons.add(CoverageSelectionFallbackReason.COLLECTOR_CONFIGURATION_MISMATCH)
        return tuple(sorted(reasons, key=lambda item: item.value))

    def _write_advisory(
        self, advisory: CoverageSelectionAdvisory
    ) -> RepositoryCoverageSelectionResult:
        content = advisory.canonical_content()
        if len(content.encode("utf-8")) > self.advisory_max_bytes:
            raise RepositoryCoverageSelectionError(
                "coverage-selection advisory exceeds its byte limit"
            )
        digest = advisory.canonical_hash()
        reference = self.artifacts.write_text(
            (
                f"coverage-selection/{advisory.project_id}/{advisory.base_sha}/"
                f"advisory-{digest}.json"
            ),
            content,
            "application/json",
        )
        if not hmac.compare_digest(reference.sha256, digest):
            raise RepositoryCoverageSelectionError(
                "coverage-selection advisory artifact hash mismatch"
            )
        verified = self._load_advisory(reference.uri, digest)
        if verified != advisory:
            raise RepositoryCoverageSelectionError(
                "coverage-selection advisory changed during recording"
            )
        return RepositoryCoverageSelectionResult(
            advisory_ref=reference.uri,
            advisory_sha256=digest,
            advisory=verified,
        )

    def _load_qualification(
        self, reference: str, expected_sha256: str
    ) -> TrustedCoverageQualificationReceipt:
        value = self._load_bounded_json(
            reference,
            expected_sha256,
            max_bytes=self.qualification_max_bytes,
            context="coverage qualification",
        )
        try:
            receipt = TrustedCoverageQualificationReceipt.model_validate(value)
        except ValueError as exc:
            raise RepositoryCoverageSelectionError(
                "coverage qualification failed bounded validation"
            ) from exc
        if not hmac.compare_digest(receipt.canonical_hash(), expected_sha256):
            raise RepositoryCoverageSelectionError(
                "coverage qualification canonical hash does not match"
            )
        if len(receipt.profile_identities) > self.max_profiles:
            raise RepositoryCoverageSelectionError(
                "coverage qualification exceeds its profile limit"
            )
        return receipt

    def _load_advisory(self, reference: str, expected_sha256: str) -> CoverageSelectionAdvisory:
        value = self._load_bounded_json(
            reference,
            expected_sha256,
            max_bytes=self.advisory_max_bytes,
            context="coverage-selection advisory",
        )
        try:
            advisory = CoverageSelectionAdvisory.model_validate(value)
        except ValueError as exc:
            raise RepositoryCoverageSelectionError(
                "coverage-selection advisory failed bounded validation"
            ) from exc
        if not hmac.compare_digest(advisory.canonical_hash(), expected_sha256):
            raise RepositoryCoverageSelectionError(
                "coverage-selection advisory canonical hash does not match"
            )
        if (
            len(advisory.requested_profile_ids) > self.max_profiles
            or len(advisory.fallback_profile_ids) > self.max_profiles
        ):
            raise RepositoryCoverageSelectionError(
                "coverage-selection advisory exceeds its profile limit"
            )
        return advisory

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
        except RepositoryCoverageSelectionError:
            raise
        except (OSError, UnicodeError, ValueError, RecursionError) as exc:
            raise RepositoryCoverageSelectionError(
                f"{context} failed bounded integrity verification"
            ) from exc
        if not isinstance(value, dict):
            raise RepositoryCoverageSelectionError(f"{context} must contain one JSON object")
        return value

    def _policy_sha256(self) -> str:
        return hashlib.sha256(
            _canonical_json(
                {
                    "schema_version": "1",
                    "coverage_selection_policy_version": (COVERAGE_SELECTION_POLICY_VERSION),
                    "qualification_format": ("uca-trusted-coverage-qualification-v1"),
                    "advisory_format": "coverage-identity-eligibility-v1",
                    "compatibility": "exact-per-profile-canonical-digest-v1",
                    "fallback": "full-requested-trusted-profiles-v1",
                    "qualification_max_bytes": self.qualification_max_bytes,
                    "advisory_max_bytes": self.advisory_max_bytes,
                    "max_profiles": self.max_profiles,
                    "max_json_items": self.max_json_items,
                    "max_json_depth": self.max_json_depth,
                }
            ).encode("utf-8")
        ).hexdigest()


def _validate_profile_identity_order(
    values: tuple[CoverageProfileIdentity, ...], *, context: str
) -> None:
    profile_ids = tuple(item.profile_id for item in values)
    if profile_ids != tuple(sorted(set(profile_ids))):
        raise ValueError(f"{context} profiles must be unique and sorted")


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
                raise RepositoryCoverageSelectionError(
                    "coverage-selection JSON exceeds its depth limit"
                )
        elif character in "]}":
            expected = "[" if character == "]" else "{"
            if not stack or stack.pop() != expected:
                raise RepositoryCoverageSelectionError(
                    "coverage-selection JSON structure is malformed"
                )
        elif character in ",:":
            structural_items += 1
        if structural_items > max_items:
            raise RepositoryCoverageSelectionError(
                "coverage-selection JSON exceeds its structural-item limit"
            )
    if in_string or escaped or stack:
        raise RepositoryCoverageSelectionError("coverage-selection JSON structure is malformed")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("coverage-selection JSON contains a duplicate field")
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
