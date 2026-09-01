from __future__ import annotations

from pathlib import Path

import pytest

from universal_coding_agent.product.project_decisions import (
    ProjectDecisionService,
    ProjectDecisionStatus,
    ProjectDecisionValidationError,
)
from universal_coding_agent.product.search_service import SearchService
from universal_coding_agent.product.workspace import ProductWorkspace
from universal_coding_agent.providers.fake import FakeModelProvider
from universal_coding_agent.storage.artifacts import ArtifactStore


def _service(
    tmp_path: Path,
    *,
    max_decision_bytes: int = 64_000,
) -> tuple[ArtifactStore, SearchService, ProjectDecisionService]:
    artifacts = ArtifactStore(tmp_path / "artifacts")
    search = SearchService(tmp_path / "search.sqlite")
    decisions = ProjectDecisionService(
        tmp_path / "project-decisions.sqlite",
        artifacts,
        search,
        max_decision_bytes=max_decision_bytes,
    )
    return artifacts, search, decisions


def _draft(
    decisions: ProjectDecisionService,
    *,
    project_id: str = "project-alpha",
    decision_id: str = "adr-001-database",
    version: int = 1,
    supersedes_version: int | None = None,
    decision: str = "Use SQLite for the local durable control plane.",
):
    return decisions.create_draft(
        project_id=project_id,
        decision_id=decision_id,
        version=version,
        supersedes_version=supersedes_version,
        title="Select the local durable database",
        context="The local control plane needs restart-safe state.",
        decision=decision,
        rationale="SQLite provides bounded local durability without a service dependency.",
        alternatives=("Use only process memory.", "Require an external database."),
        consequences=("Single-host write concurrency remains bounded.",),
    )


def _accept(decisions: ProjectDecisionService, draft):
    return decisions.accept(
        project_id=draft.manifest.project_id,
        decision_id=draft.manifest.decision_id,
        version=draft.manifest.version,
        expected_manifest_sha256=draft.manifest_sha256,
        confirmed=True,
    )


def test_decision_requires_explicit_hash_bound_acceptance_and_indexes_only_after_acceptance(
    tmp_path: Path,
) -> None:
    _artifacts, search, decisions = _service(tmp_path)
    try:
        draft = _draft(decisions)

        assert draft.status is ProjectDecisionStatus.DRAFT
        assert decisions.search_accepted(project_id="project-alpha", query="SQLite") == ()
        with pytest.raises(ProjectDecisionValidationError, match="explicit"):
            decisions.accept(
                project_id="project-alpha",
                decision_id="adr-001-database",
                version=1,
                expected_manifest_sha256=draft.manifest_sha256,
                confirmed=False,
            )
        with pytest.raises(ProjectDecisionValidationError, match="hash mismatch"):
            decisions.accept(
                project_id="project-alpha",
                decision_id="adr-001-database",
                version=1,
                expected_manifest_sha256="0" * 64,
                confirmed=True,
            )

        accepted = _accept(decisions, draft)
        assert accepted.status is ProjectDecisionStatus.ACCEPTED
        assert accepted.acceptance_ref.startswith("artifact://")
        assert accepted.acceptance_sha256
        first_count = decisions.index_accepted(
            project_id="project-alpha",
            decision_id="adr-001-database",
            version=1,
            expected_manifest_sha256=draft.manifest_sha256,
        )
        second_count = decisions.index_accepted(
            project_id="project-alpha",
            decision_id="adr-001-database",
            version=1,
            expected_manifest_sha256=draft.manifest_sha256,
        )

        assert first_count == second_count == 1
        hits = decisions.search_accepted(project_id="project-alpha", query="SQLite")
        assert len(hits) == 1
        assert hits[0].source_id == "adr-001-database"
        assert hits[0].metadata["manifest_sha256"] == draft.manifest_sha256
        assert decisions.get("project-alpha", "adr-001-database", 1).indexed is True
    finally:
        decisions.close()
        search.close()


def test_new_version_must_supersede_latest_accepted_version_and_replaces_index(
    tmp_path: Path,
) -> None:
    _artifacts, search, decisions = _service(tmp_path)
    try:
        first = _draft(decisions)
        with pytest.raises(ProjectDecisionValidationError, match="latest accepted"):
            _draft(decisions, version=2, supersedes_version=1)
        _accept(decisions, first)
        decisions.index_accepted(
            project_id="project-alpha",
            decision_id="adr-001-database",
            version=1,
            expected_manifest_sha256=first.manifest_sha256,
        )

        second = _draft(
            decisions,
            version=2,
            supersedes_version=1,
            decision="Use PostgreSQL for the durable control plane.",
        )
        _accept(decisions, second)
        with pytest.raises(ProjectDecisionValidationError, match="latest accepted"):
            decisions.index_accepted(
                project_id="project-alpha",
                decision_id="adr-001-database",
                version=1,
                expected_manifest_sha256=first.manifest_sha256,
            )
        decisions.index_accepted(
            project_id="project-alpha",
            decision_id="adr-001-database",
            version=2,
            expected_manifest_sha256=second.manifest_sha256,
        )

        hits = decisions.search_accepted(project_id="project-alpha", query="PostgreSQL")
        assert len(hits) == 1
        assert hits[0].metadata["version"] == 2
        assert decisions.get("project-alpha", "adr-001-database", 1).indexed is False
        assert decisions.get("project-alpha", "adr-001-database", 2).indexed is True
    finally:
        decisions.close()
        search.close()


def test_project_scoped_decision_ids_and_search_do_not_cross_projects(
    tmp_path: Path,
) -> None:
    _artifacts, search, decisions = _service(tmp_path)
    try:
        alpha = _draft(decisions, decision="Use the AlphaOnlyMarker contract.")
        beta = _draft(
            decisions,
            project_id="project-beta",
            decision="Use the BetaOnlyMarker contract.",
        )
        _accept(decisions, alpha)
        _accept(decisions, beta)
        decisions.index_accepted(
            project_id="project-alpha",
            decision_id=alpha.manifest.decision_id,
            version=1,
            expected_manifest_sha256=alpha.manifest_sha256,
        )
        decisions.index_accepted(
            project_id="project-beta",
            decision_id=beta.manifest.decision_id,
            version=1,
            expected_manifest_sha256=beta.manifest_sha256,
        )

        assert decisions.search_accepted(project_id="project-alpha", query="BetaOnlyMarker") == ()
        assert search.search("AlphaOnlyMarker") == ()
        assert search.search("BetaOnlyMarker") == ()
        alpha_hits = decisions.search_accepted(project_id="project-alpha", query="AlphaOnlyMarker")
        assert len(alpha_hits) == 1
        assert alpha_hits[0].metadata["project_id"] == "project-alpha"
        assert decisions.get("project-alpha", "adr-001-database", 1) != decisions.get(
            "project-beta", "adr-001-database", 1
        )
    finally:
        decisions.close()
        search.close()


def test_acceptance_is_idempotent_and_survives_restart(tmp_path: Path) -> None:
    artifacts, search, decisions = _service(tmp_path)
    draft = _draft(decisions)
    first = _accept(decisions, draft)
    second = _accept(decisions, draft)
    assert second == first
    decisions.close()
    search.close()

    reopened_search = SearchService(tmp_path / "search.sqlite")
    reopened = ProjectDecisionService(
        tmp_path / "project-decisions.sqlite",
        artifacts,
        reopened_search,
    )
    try:
        assert reopened.accepted("project-alpha", "adr-001-database", 1) == first
        assert reopened.list(project_id="project-alpha", accepted_only=True) == (first,)
    finally:
        reopened.close()
        reopened_search.close()


def test_manifest_drift_and_oversize_fail_closed_before_indexing(tmp_path: Path) -> None:
    artifacts, search, decisions = _service(tmp_path)
    try:
        draft = _draft(decisions)
        _accept(decisions, draft)
        manifest_path = (
            artifacts.root / "project-decisions/project-alpha/adr-001-database/v1/manifest.json"
        )
        manifest_path.write_text("{}", encoding="utf-8")

        with pytest.raises(ProjectDecisionValidationError, match="integrity"):
            decisions.accepted("project-alpha", "adr-001-database", 1)
        with pytest.raises(ProjectDecisionValidationError, match="integrity"):
            decisions.index_accepted(
                project_id="project-alpha",
                decision_id="adr-001-database",
                version=1,
                expected_manifest_sha256=draft.manifest_sha256,
            )
        assert decisions.search_accepted(project_id="project-alpha", query="SQLite") == ()
    finally:
        decisions.close()
        search.close()

    _artifacts, bounded_search, bounded = _service(
        tmp_path / "bounded",
        max_decision_bytes=64,
    )
    try:
        with pytest.raises(ProjectDecisionValidationError, match="byte limit"):
            _draft(bounded)
        assert bounded.list(project_id="project-alpha") == ()
    finally:
        bounded.close()
        bounded_search.close()


def test_acceptance_receipt_drift_fails_closed(tmp_path: Path) -> None:
    artifacts, search, decisions = _service(tmp_path)
    try:
        draft = _draft(decisions)
        accepted = _accept(decisions, draft)
        receipt_path = (
            artifacts.root / "project-decisions/project-alpha/adr-001-database/v1/acceptance.json"
        )
        receipt_path.write_text("{}", encoding="utf-8")

        with pytest.raises(ProjectDecisionValidationError, match="acceptance"):
            decisions.accepted("project-alpha", "adr-001-database", 1)
        assert accepted.acceptance_sha256
    finally:
        decisions.close()
        search.close()


def test_product_workspace_exposes_and_reopens_project_decisions(tmp_path: Path) -> None:
    root = tmp_path / "workspace"
    first = ProductWorkspace.create(root, FakeModelProvider())
    draft = _draft(first.project_decisions)
    accepted = _accept(first.project_decisions, draft)
    first.close()

    reopened = ProductWorkspace.create(root, FakeModelProvider())
    try:
        assert (
            reopened.project_decisions.accepted("project-alpha", "adr-001-database", 1) == accepted
        )
    finally:
        reopened.close()
