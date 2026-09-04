from __future__ import annotations

from pathlib import Path

import pytest

from universal_coding_agent.product.context_documents import ContextDocumentService
from universal_coding_agent.product.knowledge_packs import (
    KnowledgePackStatus,
    KnowledgePackValidationError,
    ProjectKnowledgePackService,
)
from universal_coding_agent.product.models import ContextScope, DocumentRole
from universal_coding_agent.product.search_service import SearchService
from universal_coding_agent.storage.artifacts import ArtifactStore


def _services(tmp_path: Path):
    artifacts = ArtifactStore(tmp_path / "artifacts")
    documents = ContextDocumentService(tmp_path / "documents.sqlite", artifacts)
    search = SearchService(tmp_path / "search.sqlite")
    packs = ProjectKnowledgePackService(
        tmp_path / "knowledge-packs.sqlite",
        artifacts,
        documents,
        search,
    )
    return artifacts, documents, search, packs


def _document(
    documents: ContextDocumentService,
    *,
    document_id: str,
    project_id: str = "project-alpha",
    content: str = "The service must preserve approved behavior.\n",
):
    return documents.ingest(
        document_id=document_id,
        filename=f"{document_id}.md",
        content=content,
        role=DocumentRole.ARCHITECTURE,
        scope=ContextScope.PROGRAM,
        scope_id=project_id,
    )


def test_pack_requires_explicit_hash_bound_acceptance_and_indexes_deterministically(
    tmp_path: Path,
) -> None:
    _artifacts, documents, search, packs = _services(tmp_path)
    try:
        _document(documents, document_id="architecture-001")
        _document(
            documents,
            document_id="requirements-001",
            content="The project requires deterministic accepted knowledge.\n",
        )
        draft = packs.create_draft(
            pack_id="project-alpha-core",
            project_id="project-alpha",
            version=1,
            title="Project Alpha core knowledge",
            document_ids=("requirements-001", "architecture-001"),
        )

        assert draft.status is KnowledgePackStatus.DRAFT
        assert tuple(item.document_id for item in draft.manifest.documents) == (
            "architecture-001",
            "requirements-001",
        )
        with pytest.raises(KnowledgePackValidationError, match="explicit"):
            packs.accept(
                pack_id="project-alpha-core",
                version=1,
                expected_manifest_sha256=draft.manifest_sha256,
                confirmed=False,
            )
        with pytest.raises(KnowledgePackValidationError, match="hash mismatch"):
            packs.accept(
                pack_id="project-alpha-core",
                version=1,
                expected_manifest_sha256="0" * 64,
                confirmed=True,
            )

        accepted = packs.accept(
            pack_id="project-alpha-core",
            version=1,
            expected_manifest_sha256=draft.manifest_sha256,
            confirmed=True,
        )
        assert accepted.status is KnowledgePackStatus.ACCEPTED
        assert accepted.acceptance_ref.startswith("artifact://")

        first_count = packs.index_accepted(
            pack_id="project-alpha-core",
            version=1,
            expected_manifest_sha256=draft.manifest_sha256,
        )
        second_count = packs.index_accepted(
            pack_id="project-alpha-core",
            version=1,
            expected_manifest_sha256=draft.manifest_sha256,
        )
        assert first_count == second_count == 2
        hits = search.search(
            "deterministic accepted knowledge",
            namespaces=("knowledge-pack:project-alpha-core:v1",),
        )
        assert hits
        assert hits[0].source_id == "requirements-001"
        assert packs.get("project-alpha-core", 1).indexed is True
    finally:
        packs.close()
        search.close()
        documents.close()


def test_pack_rejects_cross_project_documents_and_duplicates(tmp_path: Path) -> None:
    _artifacts, documents, search, packs = _services(tmp_path)
    try:
        _document(
            documents,
            document_id="other-project-001",
            project_id="project-beta",
        )
        with pytest.raises(KnowledgePackValidationError, match="outside"):
            packs.create_draft(
                pack_id="project-alpha-core",
                project_id="project-alpha",
                version=1,
                title="Project Alpha core knowledge",
                document_ids=("other-project-001",),
            )

        _document(documents, document_id="architecture-001")
        with pytest.raises(KnowledgePackValidationError, match="unique"):
            packs.create_draft(
                pack_id="project-alpha-core",
                project_id="project-alpha",
                version=1,
                title="Project Alpha core knowledge",
                document_ids=("architecture-001", "architecture-001"),
            )
    finally:
        packs.close()
        search.close()
        documents.close()


def test_new_version_must_supersede_latest_accepted_version(tmp_path: Path) -> None:
    _artifacts, documents, search, packs = _services(tmp_path)
    try:
        _document(documents, document_id="architecture-001")
        first = packs.create_draft(
            pack_id="project-alpha-core",
            project_id="project-alpha",
            version=1,
            title="Project Alpha core knowledge",
            document_ids=("architecture-001",),
        )
        with pytest.raises(KnowledgePackValidationError, match="latest accepted"):
            packs.create_draft(
                pack_id="project-alpha-core",
                project_id="project-alpha",
                version=2,
                title="Project Alpha core knowledge v2",
                document_ids=("architecture-001",),
                supersedes_version=1,
            )

        packs.accept(
            pack_id="project-alpha-core",
            version=1,
            expected_manifest_sha256=first.manifest_sha256,
            confirmed=True,
        )
        _document(
            documents,
            document_id="decision-002",
            content="ADR-002 selects immutable knowledge packs.\n",
        )
        second = packs.create_draft(
            pack_id="project-alpha-core",
            project_id="project-alpha",
            version=2,
            title="Project Alpha core knowledge v2",
            document_ids=("architecture-001", "decision-002"),
            supersedes_version=1,
        )
        assert second.manifest.supersedes_version == 1
        assert second.status is KnowledgePackStatus.DRAFT
    finally:
        packs.close()
        search.close()
        documents.close()


def test_accepted_pack_fails_closed_when_content_drifts(tmp_path: Path) -> None:
    artifacts, documents, search, packs = _services(tmp_path)
    try:
        _document(documents, document_id="architecture-001")
        draft = packs.create_draft(
            pack_id="project-alpha-core",
            project_id="project-alpha",
            version=1,
            title="Project Alpha core knowledge",
            document_ids=("architecture-001",),
        )
        packs.accept(
            pack_id="project-alpha-core",
            version=1,
            expected_manifest_sha256=draft.manifest_sha256,
            confirmed=True,
        )

        content_path = artifacts.root / "documents/architecture-001/content.txt"
        content_path.write_text("tampered\n", encoding="utf-8")
        with pytest.raises(KnowledgePackValidationError, match="integrity"):
            packs.accepted("project-alpha-core", 1)
        with pytest.raises(KnowledgePackValidationError, match="integrity"):
            packs.index_accepted(
                pack_id="project-alpha-core",
                version=1,
                expected_manifest_sha256=draft.manifest_sha256,
            )
    finally:
        packs.close()
        search.close()
        documents.close()


def test_acceptance_is_idempotent_and_survives_restart(tmp_path: Path) -> None:
    artifacts, documents, search, packs = _services(tmp_path)
    _document(documents, document_id="architecture-001")
    draft = packs.create_draft(
        pack_id="project-alpha-core",
        project_id="project-alpha",
        version=1,
        title="Project Alpha core knowledge",
        document_ids=("architecture-001",),
    )
    first = packs.accept(
        pack_id="project-alpha-core",
        version=1,
        expected_manifest_sha256=draft.manifest_sha256,
        confirmed=True,
    )
    second = packs.accept(
        pack_id="project-alpha-core",
        version=1,
        expected_manifest_sha256=draft.manifest_sha256,
        confirmed=True,
    )
    assert second == first
    packs.close()
    search.close()
    documents.close()

    reopened_documents = ContextDocumentService(tmp_path / "documents.sqlite", artifacts)
    reopened_search = SearchService(tmp_path / "search.sqlite")
    reopened = ProjectKnowledgePackService(
        tmp_path / "knowledge-packs.sqlite",
        artifacts,
        reopened_documents,
        reopened_search,
    )
    try:
        record = reopened.accepted("project-alpha-core", 1)
        assert record == first
        assert reopened.list(project_id="project-alpha", accepted_only=True) == (first,)
    finally:
        reopened.close()
        reopened_search.close()
        reopened_documents.close()
