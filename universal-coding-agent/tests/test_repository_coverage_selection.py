from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pytest
from test_repository_coverage_evidence import (
    PROJECT_ID,
    _build_upstreams,
    _commit,
    _git,
    _policy,
    _record,
    _repository,
    _Services,
    _services,
    _trusted_run,
    _write_run,
)

from universal_coding_agent.product.coverage_evidence import (
    TrustedCoverageProfile,
    trusted_test_profile_sha256,
)
from universal_coding_agent.product.coverage_selection import (
    CoverageBackedTestSelection,
    CoverageCollectorIdentity,
    CoverageExecutionEnvironmentIdentity,
    CoverageProfileIdentity,
    CoverageSelectionDisposition,
    CoverageSelectionFallbackReason,
    CoverageSelectionRequiredIdentities,
    CoverageTestSelectionDisposition,
    CoverageTestSelectionFallbackReason,
    RepositoryCoverageSelectionError,
    RepositoryCoverageSelectionService,
    TrustedCoverageQualificationReceipt,
)
from universal_coding_agent.product.workspace import ProductWorkspace
from universal_coding_agent.providers.fake import FakeModelProvider


@dataclass
class _SelectionContext:
    root: Path
    state_root: Path
    base_sha: str
    services: object
    policy: object
    run: object
    recorded: object
    upstreams: object | None = None


def _run_for_every_profile(root, upstreams, policy):
    baseline = _trusted_run(root, upstreams, policy)
    tests = tuple(
        test.model_copy(update={"profile_id": profile.profile_id})
        for profile in sorted(policy.profiles, key=lambda item: item.profile_id)
        for test in baseline.tests
    )
    profiles = tuple(
        TrustedCoverageProfile(
            profile_id=profile.profile_id,
            profile_sha256=trusted_test_profile_sha256(profile),
            passed=True,
            returncode=0,
            collection_complete=True,
            execution_complete=True,
            test_count=len(baseline.tests),
        )
        for profile in sorted(policy.profiles, key=lambda item: item.profile_id)
    )
    return baseline.model_copy(
        update={"profiles": profiles, "tests": tests, "unattributed_files": ()}
    )


def _workspace_services(workspace: ProductWorkspace) -> _Services:
    return _Services(
        artifacts=workspace.artifacts,
        search=workspace.search,
        indexes=workspace.repository_indexes,
        dependencies=workspace.dependency_graphs,
        calls=workspace.call_graphs,
        dispatch=workspace.dispatch_evidence,
        coverage=workspace.coverage_evidence,
    )


@pytest.fixture
def selection_context(tmp_path: Path):
    root, base_sha = _repository(tmp_path)
    state_root = tmp_path / "state"
    services = _services(state_root)
    policy = _policy("focused", "integration")
    try:
        upstreams = _build_upstreams(root, base_sha, services)
        run = _run_for_every_profile(root, upstreams, policy)
        run_ref, run_sha256 = _write_run(services.artifacts, run)
        recorded = _record(
            services,
            root,
            upstreams,
            policy,
            run_ref,
            run_sha256,
        )
        yield _SelectionContext(
            root=root,
            state_root=state_root,
            base_sha=base_sha,
            services=services,
            policy=policy,
            run=run,
            recorded=recorded,
            upstreams=upstreams,
        )
    finally:
        services.search.close()


def _identity(
    context: _SelectionContext,
    profile_id: str,
    *,
    environment_id: str = "linux-python-3.13",
    environment_sha256: str = "a" * 64,
    collector_id: str = "coverage-py",
    collector_version: str = "7.10.6",
    collector_sha256: str = "b" * 64,
    configuration_sha256: str = "c" * 64,
    profile_sha256: str | None = None,
) -> CoverageProfileIdentity:
    profile = context.policy.profile_map()[profile_id]
    return CoverageProfileIdentity(
        profile_id=profile_id,
        profile_sha256=(
            profile_sha256 or trusted_test_profile_sha256(profile)
        ),
        execution_environment=CoverageExecutionEnvironmentIdentity(
            environment_id=environment_id,
            manifest_sha256=environment_sha256,
        ),
        collector=CoverageCollectorIdentity(
            collector_id=collector_id,
            collector_version=collector_version,
            collector_sha256=collector_sha256,
            configuration_sha256=configuration_sha256,
        ),
    )


def _identities(
    context: _SelectionContext,
    profile_ids: tuple[str, ...],
) -> CoverageSelectionRequiredIdentities:
    return CoverageSelectionRequiredIdentities(
        profiles=tuple(
            sorted(
                (_identity(context, profile_id) for profile_id in profile_ids),
                key=lambda item: item.profile_id,
            )
        )
    )


def _qualification(
    context: _SelectionContext,
    identities: CoverageSelectionRequiredIdentities,
) -> TrustedCoverageQualificationReceipt:
    evidence = context.recorded.evidence
    return TrustedCoverageQualificationReceipt(
        project_id=PROJECT_ID,
        repository_url=evidence.repository_url,
        base_ref=evidence.base_ref,
        base_sha=evidence.base_sha,
        source_tree_oid=evidence.source_tree_oid,
        coverage_evidence_ref=context.recorded.evidence_ref,
        coverage_evidence_sha256=context.recorded.evidence_sha256,
        trusted_run_ref=evidence.trusted_run_ref,
        trusted_run_sha256=evidence.trusted_run_sha256,
        test_run_id=evidence.test_run_id,
        trusted_test_policy_sha256=evidence.trusted_test_policy_sha256,
        profile_identities=identities.profiles,
    )


def _write_qualification(context: _SelectionContext, receipt):
    digest = receipt.canonical_hash()
    reference = context.services.artifacts.write_text(
        f"coverage-qualifications/{PROJECT_ID}/receipt-{digest}.json",
        receipt.canonical_content(),
        "application/json",
    )
    assert reference.sha256 == digest
    return reference.uri, digest


def _assess(
    context: _SelectionContext,
    *,
    requested_profile_ids: tuple[str, ...] = ("focused", "integration"),
    required_identities: CoverageSelectionRequiredIdentities | None = None,
    qualification_ref: str | None = None,
    qualification_sha256: str | None = None,
    expected_base_sha: str | None = None,
    service: RepositoryCoverageSelectionService | None = None,
):
    selector = service or RepositoryCoverageSelectionService(
        context.services.artifacts,
        context.services.coverage,
    )
    return selector.assess_eligibility(
        project_id=PROJECT_ID,
        expected_base_sha=expected_base_sha or context.base_sha,
        trusted_test_policy=context.policy,
        requested_profile_ids=requested_profile_ids,
        expected_coverage_evidence_ref=context.recorded.evidence_ref,
        expected_coverage_evidence_sha256=context.recorded.evidence_sha256,
        required_identities=required_identities,
        qualification_ref=qualification_ref,
        qualification_sha256=qualification_sha256,
    )


def test_exact_identities_produce_advisory_eligibility_without_execution(
    selection_context: _SelectionContext,
) -> None:
    identities = _identities(selection_context, ("focused", "integration"))
    qualification_ref, qualification_sha256 = _write_qualification(
        selection_context,
        _qualification(selection_context, identities),
    )
    head_before = _git(selection_context.root, "rev-parse", "HEAD")
    tree_before = _git(selection_context.root, "rev-parse", "HEAD^{tree}")
    active_before = selection_context.services.search.repository_coverage_evidence_state(
        selection_context.services.coverage.namespace(PROJECT_ID)
    )

    result = _assess(
        selection_context,
        required_identities=identities,
        qualification_ref=qualification_ref,
        qualification_sha256=qualification_sha256,
    )

    assert result.advisory.disposition is CoverageSelectionDisposition.ELIGIBLE
    assert result.advisory.fallback_profile_ids == ()
    assert result.advisory.fallback_reasons == ()
    assert result.advisory.selects_test_ids is False
    assert result.advisory.authorizes_execution is False
    assert result.advisory.claims_minimality is False
    assert result.advisory.required_identities_sha256 == identities.canonical_hash()
    assert _git(selection_context.root, "rev-parse", "HEAD") == head_before
    assert _git(selection_context.root, "rev-parse", "HEAD^{tree}") == tree_before
    assert _git(selection_context.root, "status", "--porcelain") == ""
    assert (
        selection_context.services.search.repository_coverage_evidence_state(
            selection_context.services.coverage.namespace(PROJECT_ID)
        )
        == active_before
    )


def test_legacy_v1_without_qualification_falls_back_every_requested_profile(
    selection_context: _SelectionContext,
) -> None:
    identities = _identities(selection_context, ("focused", "integration"))

    result = _assess(selection_context, required_identities=identities)

    assert result.advisory.disposition is (
        CoverageSelectionDisposition.FULL_PROFILE_FALLBACK
    )
    assert result.advisory.requested_profile_ids == ("focused", "integration")
    assert result.advisory.fallback_profile_ids == ("focused", "integration")
    assert result.advisory.fallback_reasons == (
        CoverageSelectionFallbackReason.QUALIFICATION_MISSING,
    )


def test_missing_required_identity_falls_back_without_selectors(
    selection_context: _SelectionContext,
) -> None:
    qualified_identities = _identities(
        selection_context, ("focused", "integration")
    )
    qualification_ref, qualification_sha256 = _write_qualification(
        selection_context,
        _qualification(selection_context, qualified_identities),
    )

    result = _assess(
        selection_context,
        required_identities=CoverageSelectionRequiredIdentities(
            profiles=(_identity(selection_context, "focused"),)
        ),
        qualification_ref=qualification_ref,
        qualification_sha256=qualification_sha256,
    )

    assert result.advisory.fallback_profile_ids == ("focused", "integration")
    assert result.advisory.fallback_reasons == (
        CoverageSelectionFallbackReason.REQUIRED_IDENTITY_MISSING,
    )
    assert result.advisory.selects_test_ids is False


def test_missing_qualified_identity_falls_back_all_requested_profiles(
    selection_context: _SelectionContext,
) -> None:
    required = _identities(selection_context, ("focused", "integration"))
    qualified = CoverageSelectionRequiredIdentities(
        profiles=(_identity(selection_context, "focused"),)
    )
    qualification_ref, qualification_sha256 = _write_qualification(
        selection_context,
        _qualification(selection_context, qualified),
    )

    result = _assess(
        selection_context,
        required_identities=required,
        qualification_ref=qualification_ref,
        qualification_sha256=qualification_sha256,
    )

    assert result.advisory.fallback_profile_ids == ("focused", "integration")
    assert result.advisory.fallback_reasons == (
        CoverageSelectionFallbackReason.QUALIFIED_IDENTITY_MISSING,
    )


def test_requested_profile_missing_from_coverage_forces_full_fallback(
    selection_context: _SelectionContext,
    tmp_path: Path,
) -> None:
    services = _services(tmp_path / "partial-state")
    try:
        upstreams = _build_upstreams(
            selection_context.root,
            selection_context.base_sha,
            services,
        )
        run = _trusted_run(selection_context.root, upstreams, selection_context.policy)
        run_ref, run_sha256 = _write_run(services.artifacts, run)
        recorded = _record(
            services,
            selection_context.root,
            upstreams,
            selection_context.policy,
            run_ref,
            run_sha256,
        )
        context = _SelectionContext(
            root=selection_context.root,
            state_root=tmp_path / "partial-state",
            base_sha=selection_context.base_sha,
            services=services,
            policy=selection_context.policy,
            run=run,
            recorded=recorded,
        )
        required = _identities(context, ("focused", "integration"))
        qualified = CoverageSelectionRequiredIdentities(
            profiles=(_identity(context, "focused"),)
        )
        qualification_ref, qualification_sha256 = _write_qualification(
            context,
            _qualification(context, qualified),
        )

        result = _assess(
            context,
            required_identities=required,
            qualification_ref=qualification_ref,
            qualification_sha256=qualification_sha256,
        )

        assert result.advisory.fallback_profile_ids == ("focused", "integration")
        assert CoverageSelectionFallbackReason.COVERAGE_PROFILE_MISSING in (
            result.advisory.fallback_reasons
        )
    finally:
        services.search.close()


@pytest.mark.parametrize(
    ("identity_update", "reason"),
    (
        (
            {"execution_environment": CoverageExecutionEnvironmentIdentity(
                environment_id="linux-python-3.13", manifest_sha256="d" * 64
            )},
            CoverageSelectionFallbackReason.EXECUTION_ENVIRONMENT_MISMATCH,
        ),
        (
            {"collector": CoverageCollectorIdentity(
                collector_id="coverage-py",
                collector_version="7.11.0",
                collector_sha256="b" * 64,
                configuration_sha256="c" * 64,
            )},
            CoverageSelectionFallbackReason.COLLECTOR_IDENTITY_MISMATCH,
        ),
        (
            {"collector": CoverageCollectorIdentity(
                collector_id="coverage-py",
                collector_version="7.10.6",
                collector_sha256="b" * 64,
                configuration_sha256="d" * 64,
            )},
            CoverageSelectionFallbackReason.COLLECTOR_CONFIGURATION_MISMATCH,
        ),
    ),
)
def test_identity_drift_falls_back_all_profiles(
    selection_context: _SelectionContext,
    identity_update: dict[str, object],
    reason: CoverageSelectionFallbackReason,
) -> None:
    qualified = _identities(selection_context, ("focused", "integration"))
    qualification_ref, qualification_sha256 = _write_qualification(
        selection_context,
        _qualification(selection_context, qualified),
    )
    focused = _identity(selection_context, "focused").model_copy(
        update=identity_update
    )
    required = CoverageSelectionRequiredIdentities(
        profiles=(focused, _identity(selection_context, "integration"))
    )

    result = _assess(
        selection_context,
        required_identities=required,
        qualification_ref=qualification_ref,
        qualification_sha256=qualification_sha256,
    )

    assert result.advisory.disposition is (
        CoverageSelectionDisposition.FULL_PROFILE_FALLBACK
    )
    assert result.advisory.fallback_profile_ids == ("focused", "integration")
    assert reason in result.advisory.fallback_reasons


def test_required_profile_digest_mismatch_is_conservative_fallback(
    selection_context: _SelectionContext,
) -> None:
    qualified = _identities(selection_context, ("focused", "integration"))
    qualification_ref, qualification_sha256 = _write_qualification(
        selection_context,
        _qualification(selection_context, qualified),
    )
    required = CoverageSelectionRequiredIdentities(
        profiles=(
            _identity(selection_context, "focused", profile_sha256="d" * 64),
            _identity(selection_context, "integration"),
        )
    )

    result = _assess(
        selection_context,
        required_identities=required,
        qualification_ref=qualification_ref,
        qualification_sha256=qualification_sha256,
    )

    assert CoverageSelectionFallbackReason.REQUIRED_PROFILE_MISMATCH in (
        result.advisory.fallback_reasons
    )
    assert result.advisory.fallback_profile_ids == ("focused", "integration")


def test_qualification_provenance_or_profile_conflict_hard_fails(
    selection_context: _SelectionContext,
) -> None:
    identities = _identities(selection_context, ("focused", "integration"))
    receipt = _qualification(selection_context, identities)
    conflicts = (
        receipt.model_copy(update={"base_sha": "d" * 40}),
        receipt.model_copy(
            update={
                "profile_identities": (
                    identities.profiles[0].model_copy(
                        update={"profile_sha256": "d" * 64}
                    ),
                    identities.profiles[1],
                )
            }
        ),
    )
    for conflict in conflicts:
        qualification_ref, qualification_sha256 = _write_qualification(
            selection_context, conflict
        )
        with pytest.raises(RepositoryCoverageSelectionError, match="conflicts"):
            _assess(
                selection_context,
                required_identities=identities,
                qualification_ref=qualification_ref,
                qualification_sha256=qualification_sha256,
            )


@pytest.mark.parametrize("malformation", ("noncanonical", "duplicate", "unknown"))
def test_malformed_qualification_hard_fails(
    selection_context: _SelectionContext,
    malformation: str,
) -> None:
    identities = _identities(selection_context, ("focused", "integration"))
    receipt = _qualification(selection_context, identities)
    if malformation == "noncanonical":
        content = json.dumps(receipt.model_dump(mode="json"), indent=2)
    elif malformation == "duplicate":
        content = '{"schema_version":"1","schema_version":"1"}'
    else:
        value = receipt.model_dump(mode="json")
        value["unexpected"] = True
        content = json.dumps(value, separators=(",", ":"), sort_keys=True)
    reference = selection_context.services.artifacts.write_text(
        f"malformed/{malformation}.json", content, "application/json"
    )

    with pytest.raises(RepositoryCoverageSelectionError):
        _assess(
            selection_context,
            required_identities=identities,
            qualification_ref=reference.uri,
            qualification_sha256=reference.sha256,
        )


def test_qualification_tamper_and_oversize_hard_fail(
    selection_context: _SelectionContext,
) -> None:
    identities = _identities(selection_context, ("focused", "integration"))
    receipt = _qualification(selection_context, identities)
    qualification_ref, qualification_sha256 = _write_qualification(
        selection_context, receipt
    )
    path = selection_context.services.artifacts.root / qualification_ref.removeprefix(
        "artifact://"
    )
    path.write_text("{}", encoding="utf-8")
    with pytest.raises(RepositoryCoverageSelectionError, match="integrity"):
        _assess(
            selection_context,
            required_identities=identities,
            qualification_ref=qualification_ref,
            qualification_sha256=qualification_sha256,
        )

    qualification_ref, qualification_sha256 = _write_qualification(
        selection_context, receipt
    )
    too_small = RepositoryCoverageSelectionService(
        selection_context.services.artifacts,
        selection_context.services.coverage,
        qualification_max_bytes=len(receipt.canonical_content().encode("utf-8")) - 1,
    )
    with pytest.raises(RepositoryCoverageSelectionError, match="integrity"):
        _assess(
            selection_context,
            required_identities=identities,
            qualification_ref=qualification_ref,
            qualification_sha256=qualification_sha256,
            service=too_small,
        )


def test_profile_json_and_advisory_bounds_fail_closed(
    selection_context: _SelectionContext,
) -> None:
    identities = _identities(selection_context, ("focused", "integration"))
    qualification_ref, qualification_sha256 = _write_qualification(
        selection_context,
        _qualification(selection_context, identities),
    )
    limits = (
        RepositoryCoverageSelectionService(
            selection_context.services.artifacts,
            selection_context.services.coverage,
            max_profiles=1,
        ),
        RepositoryCoverageSelectionService(
            selection_context.services.artifacts,
            selection_context.services.coverage,
            max_json_depth=1,
        ),
        RepositoryCoverageSelectionService(
            selection_context.services.artifacts,
            selection_context.services.coverage,
            max_json_items=1,
        ),
        RepositoryCoverageSelectionService(
            selection_context.services.artifacts,
            selection_context.services.coverage,
            advisory_max_bytes=1,
        ),
    )
    for service in limits:
        with pytest.raises(RepositoryCoverageSelectionError):
            _assess(
                selection_context,
                required_identities=identities,
                qualification_ref=qualification_ref,
                qualification_sha256=qualification_sha256,
                service=service,
            )


def test_advisory_is_content_addressed_replayable_and_policy_bound(
    selection_context: _SelectionContext,
) -> None:
    identities = _identities(selection_context, ("focused", "integration"))
    qualification_ref, qualification_sha256 = _write_qualification(
        selection_context,
        _qualification(selection_context, identities),
    )
    service = RepositoryCoverageSelectionService(
        selection_context.services.artifacts,
        selection_context.services.coverage,
    )
    first = _assess(
        selection_context,
        required_identities=identities,
        qualification_ref=qualification_ref,
        qualification_sha256=qualification_sha256,
        service=service,
    )
    second = _assess(
        selection_context,
        required_identities=identities,
        qualification_ref=qualification_ref,
        qualification_sha256=qualification_sha256,
        service=service,
    )

    assert second == first
    assert service.verified_advisory(
        first.advisory_ref, first.advisory_sha256
    ) == first.advisory
    drifted = RepositoryCoverageSelectionService(
        selection_context.services.artifacts,
        selection_context.services.coverage,
        max_json_depth=15,
    )
    with pytest.raises(RepositoryCoverageSelectionError, match="policy"):
        drifted.verified_advisory(first.advisory_ref, first.advisory_sha256)


def test_advisory_tamper_hard_fails_verification(
    selection_context: _SelectionContext,
) -> None:
    result = _assess(selection_context)
    path = selection_context.services.artifacts.root / result.advisory_ref.removeprefix(
        "artifact://"
    )
    path.write_text("{}", encoding="utf-8")

    with pytest.raises(RepositoryCoverageSelectionError, match="integrity"):
        RepositoryCoverageSelectionService(
            selection_context.services.artifacts,
            selection_context.services.coverage,
        ).verified_advisory(result.advisory_ref, result.advisory_sha256)


def test_historical_eligibility_replays_after_active_pointer_clear_and_restart(
    selection_context: _SelectionContext,
) -> None:
    identities = _identities(selection_context, ("focused", "integration"))
    qualification_ref, qualification_sha256 = _write_qualification(
        selection_context,
        _qualification(selection_context, identities),
    )
    selection_context.services.search.clear_namespace(
        selection_context.services.coverage.namespace(PROJECT_ID)
    )
    original_services = selection_context.services
    original_services.search.close()
    restarted = _services(selection_context.state_root)
    selection_context.services = restarted
    try:
        result = _assess(
            selection_context,
            required_identities=identities,
            qualification_ref=qualification_ref,
            qualification_sha256=qualification_sha256,
        )
        assert result.advisory.disposition is CoverageSelectionDisposition.ELIGIBLE
    finally:
        restarted.search.close()
        selection_context.services = original_services


def test_product_workspace_restart_replays_same_advisory(tmp_path: Path) -> None:
    root, base_sha = _repository(tmp_path)
    state_root = tmp_path / "workspace"
    workspace = ProductWorkspace.create(state_root, FakeModelProvider())
    policy = _policy("focused", "integration")
    try:
        services = _workspace_services(workspace)
        upstreams = _build_upstreams(root, base_sha, services)
        run = _run_for_every_profile(root, upstreams, policy)
        run_ref, run_sha256 = _write_run(workspace.artifacts, run)
        recorded = _record(
            services,
            root,
            upstreams,
            policy,
            run_ref,
            run_sha256,
        )
        context = _SelectionContext(
            root=root,
            state_root=state_root,
            base_sha=base_sha,
            services=services,
            policy=policy,
            run=run,
            recorded=recorded,
        )
        identities = _identities(context, ("focused", "integration"))
        qualification_ref, qualification_sha256 = _write_qualification(
            context,
            _qualification(context, identities),
        )
        first = _assess(
            context,
            required_identities=identities,
            qualification_ref=qualification_ref,
            qualification_sha256=qualification_sha256,
            service=workspace.coverage_selection,
        )
    finally:
        workspace.close()

    restarted = ProductWorkspace.create(state_root, FakeModelProvider())
    try:
        context.services = _workspace_services(restarted)
        second = _assess(
            context,
            required_identities=identities,
            qualification_ref=qualification_ref,
            qualification_sha256=qualification_sha256,
            service=restarted.coverage_selection,
        )
        assert second == first
    finally:
        restarted.close()


@pytest.mark.parametrize(
    "request_update",
    (
        {"requested_profile_ids": ()},
        {"requested_profile_ids": ("focused", "focused")},
        {"requested_profile_ids": ("unknown",)},
        {"expected_base_sha": "d" * 40},
        {"qualification_ref": "artifact://missing.json"},
    ),
)
def test_invalid_request_or_base_provenance_hard_fails(
    selection_context: _SelectionContext,
    request_update: dict[str, object],
) -> None:
    with pytest.raises(RepositoryCoverageSelectionError):
        _assess(selection_context, **request_update)


def test_identity_inventory_must_be_canonical_and_request_scoped(
    selection_context: _SelectionContext,
) -> None:
    focused = _identity(selection_context, "focused")
    integration = _identity(selection_context, "integration")
    with pytest.raises(ValueError, match="unique and sorted"):
        CoverageSelectionRequiredIdentities(
            profiles=(integration, focused)
        )
    with pytest.raises(RepositoryCoverageSelectionError, match="outside"):
        _assess(
            selection_context,
            requested_profile_ids=("focused",),
            required_identities=CoverageSelectionRequiredIdentities(
                profiles=(focused, integration)
            ),
        )


@pytest.mark.parametrize(
    ("limit_name", "limit_value"),
    (
        ("qualification_max_bytes", 511_999),
        ("advisory_max_bytes", 511_999),
        ("max_profiles", 255),
        ("max_json_items", 8_191),
        ("max_json_depth", 15),
    ),
)
def test_every_eligibility_limit_changes_policy_digest(
    tmp_path: Path,
    limit_name: str,
    limit_value: int,
) -> None:
    artifacts = _services(tmp_path / "state")
    try:
        baseline = RepositoryCoverageSelectionService(
            artifacts.artifacts, artifacts.coverage
        )
        changed = RepositoryCoverageSelectionService(
            artifacts.artifacts,
            artifacts.coverage,
            **{limit_name: limit_value},
        )
        assert changed._policy_sha256() != baseline._policy_sha256()
    finally:
        artifacts.search.close()


@pytest.mark.parametrize("limit_value", (0, -1, True, 1.5))
def test_nonpositive_boolean_or_nonintegral_limits_reject(
    tmp_path: Path,
    limit_value: object,
) -> None:
    services = _services(tmp_path / "state")
    try:
        with pytest.raises(ValueError):
            RepositoryCoverageSelectionService(
                services.artifacts,
                services.coverage,
                max_json_depth=limit_value,
            )
    finally:
        services.search.close()


def _eligibility_for_selector(context: _SelectionContext, *, eligible: bool = True):
    if not eligible:
        return _assess(context)
    identities = _identities(context, ("focused", "integration"))
    qualification_ref, qualification_sha256 = _write_qualification(
        context,
        _qualification(context, identities),
    )
    return _assess(
        context,
        required_identities=identities,
        qualification_ref=qualification_ref,
        qualification_sha256=qualification_sha256,
    )


def _advance_selector_target(
    context: _SelectionContext,
    *,
    path: str = "src/pkg/core.py",
    content: str = (
        "def leaf(value: int):\n"
        "    return value + 2\n"
        "\n"
        "class Worker:\n"
        "    def run(self):\n"
        "        return leaf(1)\n"
    ),
    previous=None,
):
    target = context.root / path
    target.write_text(content, encoding="utf-8")
    base_sha = _commit(context.root, "advance selector target")
    upstreams = _build_upstreams(
        context.root,
        base_sha,
        context.services,
        previous=previous or context.upstreams,
    )
    return base_sha, upstreams


def _select_target(
    context: _SelectionContext,
    eligibility,
    base_sha: str,
    upstreams,
):
    service = RepositoryCoverageSelectionService(
        context.services.artifacts,
        context.services.coverage,
        context.services.dispatch,
    )
    return service.select_tests(
        project_id=PROJECT_ID,
        expected_target_base_sha=base_sha,
        trusted_test_policy=context.policy,
        requested_profile_ids=("focused", "integration"),
        eligibility_advisory_ref=eligibility.advisory_ref,
        eligibility_advisory_sha256=eligibility.advisory_sha256,
        expected_target_dispatch_evidence_ref=upstreams.dispatch.evidence_ref,
        expected_target_dispatch_evidence_sha256=upstreams.dispatch.evidence_sha256,
    )


def test_direct_successor_selects_hash_bound_tests_without_execution(
    selection_context: _SelectionContext,
) -> None:
    eligibility = _eligibility_for_selector(selection_context)
    base_sha, upstreams = _advance_selector_target(selection_context)

    result = _select_target(selection_context, eligibility, base_sha, upstreams)

    assert result.selection.disposition is CoverageTestSelectionDisposition.SELECTED
    assert tuple(item.profile_id for item in result.selection.selected_profiles) == (
        "focused",
        "integration",
    )
    assert all(
        item.test_ids
        == (
            "tests/test_core.py::test_leaf",
            "tests/test_core.py::test_worker",
        )
        for item in result.selection.selected_profiles
    )
    assert result.selection.authorizes_execution is False
    assert result.selection.claims_minimality is False
    assert result.selection.changed_paths == ("src/pkg/core.py",)
    assert result.selection.affected_paths == (
        "src/pkg/core.py",
        "tests/test_core.py",
    )
    assert RepositoryCoverageSelectionService(
        selection_context.services.artifacts,
        selection_context.services.coverage,
        selection_context.services.dispatch,
    ).verified_test_selection(
        result.selection_ref, result.selection_sha256
    ) == result.selection


def test_unsupported_non_python_change_falls_back_every_profile(
    selection_context: _SelectionContext,
) -> None:
    eligibility = _eligibility_for_selector(selection_context)
    base_sha, upstreams = _advance_selector_target(
        selection_context,
        path="notes.txt",
        content="changed non-Python evidence\n",
    )

    result = _select_target(selection_context, eligibility, base_sha, upstreams)

    assert result.selection.disposition is (
        CoverageTestSelectionDisposition.FULL_PROFILE_FALLBACK
    )
    assert result.selection.fallback_profile_ids == ("focused", "integration")
    assert CoverageTestSelectionFallbackReason.UNSUPPORTED_CHANGE in (
        result.selection.fallback_reasons
    )
    assert result.selection.selected_profiles == ()


def test_coverage_gap_falls_back_every_profile(
    selection_context: _SelectionContext,
) -> None:
    eligibility = _eligibility_for_selector(selection_context)
    base_sha, upstreams = _advance_selector_target(
        selection_context,
        path="src/pkg/__init__.py",
        content="PACKAGE_VERSION = 2\n",
    )

    result = _select_target(selection_context, eligibility, base_sha, upstreams)

    assert CoverageTestSelectionFallbackReason.COVERAGE_GAP in (
        result.selection.fallback_reasons
    )
    assert result.selection.fallback_profile_ids == ("focused", "integration")


def test_unresolved_call_in_affected_source_falls_back_every_profile(
    selection_context: _SelectionContext,
) -> None:
    eligibility = _eligibility_for_selector(selection_context)
    base_sha, upstreams = _advance_selector_target(
        selection_context,
        content=(
            "def leaf(value: int):\n"
            "    return unresolved_runtime_call(value)\n"
            "\n"
            "class Worker:\n"
            "    def run(self):\n"
            "        return leaf(1)\n"
        ),
    )

    result = _select_target(selection_context, eligibility, base_sha, upstreams)

    assert CoverageTestSelectionFallbackReason.INCOMPLETE_STATIC_EVIDENCE in (
        result.selection.fallback_reasons
    )
    assert result.selection.selected_profiles == ()


def test_ineligible_history_preserves_full_profile_fallback(
    selection_context: _SelectionContext,
) -> None:
    eligibility = _eligibility_for_selector(selection_context, eligible=False)
    base_sha, upstreams = _advance_selector_target(selection_context)

    result = _select_target(selection_context, eligibility, base_sha, upstreams)

    assert CoverageTestSelectionFallbackReason.ELIGIBILITY_FALLBACK in (
        result.selection.fallback_reasons
    )
    assert result.selection.fallback_profile_ids == ("focused", "integration")


def test_non_direct_target_predecessor_hard_fails(
    selection_context: _SelectionContext,
) -> None:
    eligibility = _eligibility_for_selector(selection_context)
    first_sha, first = _advance_selector_target(selection_context)
    assert first_sha
    second_path = selection_context.root / "src/pkg/core.py"
    second_path.write_text(second_path.read_text().replace("+ 2", "+ 3"))
    second_sha = _commit(selection_context.root, "advance selector target again")
    second = _build_upstreams(
        selection_context.root,
        second_sha,
        selection_context.services,
        previous=first,
    )

    with pytest.raises(RepositoryCoverageSelectionError, match="direct successor"):
        _select_target(selection_context, eligibility, second_sha, second)


def test_test_selection_tamper_and_policy_drift_fail_closed(
    selection_context: _SelectionContext,
) -> None:
    eligibility = _eligibility_for_selector(selection_context)
    base_sha, upstreams = _advance_selector_target(selection_context)
    result = _select_target(selection_context, eligibility, base_sha, upstreams)
    path = selection_context.services.artifacts.root / result.selection_ref.removeprefix(
        "artifact://"
    )
    original = path.read_text(encoding="utf-8")
    path.write_text("{}", encoding="utf-8")
    service = RepositoryCoverageSelectionService(
        selection_context.services.artifacts,
        selection_context.services.coverage,
        selection_context.services.dispatch,
    )
    with pytest.raises(RepositoryCoverageSelectionError, match="integrity"):
        service.verified_test_selection(result.selection_ref, result.selection_sha256)

    path.write_text(original, encoding="utf-8")
    drifted = RepositoryCoverageSelectionService(
        selection_context.services.artifacts,
        selection_context.services.coverage,
        selection_context.services.dispatch,
        max_selected_tests=99_999,
    )
    with pytest.raises(RepositoryCoverageSelectionError, match="policy"):
        drifted.verified_test_selection(result.selection_ref, result.selection_sha256)


def test_selector_models_reject_noncanonical_or_executable_claims() -> None:
    assert CoverageBackedTestSelection.__name__ == "CoverageBackedTestSelection"
    with pytest.raises(ValueError):
        CoverageBackedTestSelection.model_validate(
            {
                "schema_version": "1",
                "selection_format": "coverage-backed-test-selection-v1",
                "authorizes_execution": True,
            }
        )
