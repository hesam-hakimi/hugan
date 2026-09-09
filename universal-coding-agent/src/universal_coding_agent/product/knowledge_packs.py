from __future__ import annotations

import hashlib
import hmac
import json
import re
import sqlite3
from enum import StrEnum
from pathlib import Path

from pydantic import Field, model_validator

from universal_coding_agent.core.models import FrozenModel
from universal_coding_agent.product.context_documents import ContextDocumentService
from universal_coding_agent.product.models import ContextDocument, ContextScope, DocumentRole
from universal_coding_agent.product.search_service import SearchService
from universal_coding_agent.storage.artifacts import ArtifactStore

_PACK_ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")


class KnowledgePackValidationError(ValueError):
    pass


class KnowledgePackStatus(StrEnum):
    DRAFT = "draft"
    ACCEPTED = "accepted"


class KnowledgePackDocument(FrozenModel):
    document_id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    role: DocumentRole
    scope: ContextScope
    scope_id: str = Field(min_length=1, max_length=128)


class ProjectKnowledgePackManifest(FrozenModel):
    schema_version: str = Field(default="1", pattern=r"^1$")
    pack_id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")
    project_id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")
    version: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=200)
    supersedes_version: int | None = Field(default=None, ge=1)
    documents: tuple[KnowledgePackDocument, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_documents(self) -> ProjectKnowledgePackManifest:
        document_ids = tuple(item.document_id for item in self.documents)
        if document_ids != tuple(sorted(document_ids)):
            raise ValueError("knowledge-pack documents must use deterministic document-id order")
        if len(document_ids) != len(set(document_ids)):
            raise ValueError("knowledge-pack document IDs must be unique")
        mismatched = [
            item.document_id for item in self.documents if item.scope_id != self.project_id
        ]
        if mismatched:
            raise ValueError("knowledge-pack documents must be bound to the project scope")
        if self.version == 1 and self.supersedes_version is not None:
            raise ValueError("knowledge-pack version 1 cannot supersede another version")
        if self.version > 1 and self.supersedes_version != self.version - 1:
            raise ValueError("knowledge-pack versions must supersede the immediately prior version")
        return self

    def canonical_hash(self) -> str:
        payload = json.dumps(
            self.model_dump(mode="json"),
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()


class ProjectKnowledgePackRecord(FrozenModel):
    manifest: ProjectKnowledgePackManifest
    manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    manifest_ref: str = Field(pattern=r"^artifact://[a-zA-Z0-9._/-]+$")
    status: KnowledgePackStatus
    acceptance_ref: str = Field(
        default="",
        pattern=r"^$|^artifact://[a-zA-Z0-9._/-]+$",
    )
    indexed: bool = False


class ProjectKnowledgePackService:
    """Versioned, explicitly accepted project knowledge with provenance-preserving reads."""

    def __init__(
        self,
        database_path: Path,
        artifacts: ArtifactStore,
        documents: ContextDocumentService,
        search: SearchService,
        *,
        max_document_bytes: int = 10_000_000,
    ) -> None:
        self.database_path = database_path.resolve()
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.artifacts = artifacts
        self.documents = documents
        self.search = search
        self.max_document_bytes = max_document_bytes
        self.connection = sqlite3.connect(self.database_path, check_same_thread=False)
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS project_knowledge_packs (
                pack_id TEXT NOT NULL,
                version INTEGER NOT NULL,
                project_id TEXT NOT NULL,
                manifest_json TEXT NOT NULL,
                manifest_sha256 TEXT NOT NULL,
                manifest_ref TEXT NOT NULL,
                status TEXT NOT NULL,
                acceptance_ref TEXT NOT NULL,
                indexed INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (pack_id, version)
            )
            """
        )
        self.connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_project_knowledge_packs_project
            ON project_knowledge_packs(project_id, pack_id, version)
            """
        )
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()

    def create_draft(
        self,
        *,
        pack_id: str,
        project_id: str,
        version: int,
        title: str,
        document_ids: tuple[str, ...],
        supersedes_version: int | None = None,
    ) -> ProjectKnowledgePackRecord:
        if _PACK_ID.fullmatch(pack_id) is None:
            raise KnowledgePackValidationError("invalid knowledge-pack ID")
        unique_ids = tuple(sorted(set(document_ids)))
        if not unique_ids:
            raise KnowledgePackValidationError("knowledge pack requires at least one document")
        if len(unique_ids) != len(document_ids):
            raise KnowledgePackValidationError("knowledge-pack document IDs must be unique")
        bindings = tuple(self._binding(document_id, project_id) for document_id in unique_ids)
        manifest = ProjectKnowledgePackManifest(
            pack_id=pack_id,
            project_id=project_id,
            version=version,
            title=title,
            supersedes_version=supersedes_version,
            documents=bindings,
        )
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            if self._get_row(pack_id, version) is not None:
                raise KnowledgePackValidationError("knowledge-pack version already exists")
            previous = self.connection.execute(
                """
                SELECT version, status FROM project_knowledge_packs
                WHERE pack_id = ? ORDER BY version DESC LIMIT 1
                """,
                (pack_id,),
            ).fetchone()
            if version == 1:
                if previous is not None:
                    raise KnowledgePackValidationError(
                        "knowledge-pack version 1 requires a new pack ID"
                    )
            elif (
                previous is None
                or int(previous[0]) != version - 1
                or previous[1] != KnowledgePackStatus.ACCEPTED.value
                or supersedes_version != int(previous[0])
            ):
                raise KnowledgePackValidationError(
                    "new knowledge-pack version must supersede the latest accepted version"
                )
            manifest_sha256 = manifest.canonical_hash()
            manifest_ref = self.artifacts.write_json(
                f"knowledge-packs/{pack_id}/v{version}/manifest.json",
                manifest.model_dump(mode="json"),
            )
            self.connection.execute(
                """
                INSERT INTO project_knowledge_packs (
                    pack_id, version, project_id, manifest_json, manifest_sha256,
                    manifest_ref, status, acceptance_ref, indexed
                ) VALUES (?, ?, ?, ?, ?, ?, ?, '', 0)
                """,
                (
                    pack_id,
                    version,
                    project_id,
                    manifest.model_dump_json(),
                    manifest_sha256,
                    manifest_ref.uri,
                    KnowledgePackStatus.DRAFT.value,
                ),
            )
            self.connection.commit()
        except BaseException:
            self.connection.rollback()
            raise
        return self.get(pack_id, version)

    def accept(
        self,
        *,
        pack_id: str,
        version: int,
        expected_manifest_sha256: str,
        confirmed: bool,
    ) -> ProjectKnowledgePackRecord:
        if not confirmed:
            raise KnowledgePackValidationError("explicit knowledge-pack acceptance is required")
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            record = self._record(pack_id, version)
            if not hmac.compare_digest(record.manifest_sha256, expected_manifest_sha256):
                raise KnowledgePackValidationError("knowledge-pack manifest hash mismatch")
            if record.status is KnowledgePackStatus.ACCEPTED:
                self.connection.commit()
                return record
            self._verify_documents(record.manifest)
            acceptance_ref = self.artifacts.write_json(
                f"knowledge-packs/{pack_id}/v{version}/acceptance.json",
                {
                    "pack_id": pack_id,
                    "project_id": record.manifest.project_id,
                    "version": version,
                    "manifest_sha256": record.manifest_sha256,
                    "document_sha256": {
                        item.document_id: item.sha256
                        for item in record.manifest.documents
                    },
                    "confirmed": True,
                },
            )
            self.connection.execute(
                """
                UPDATE project_knowledge_packs
                SET status = ?, acceptance_ref = ?
                WHERE pack_id = ? AND version = ? AND status = ?
                """,
                (
                    KnowledgePackStatus.ACCEPTED.value,
                    acceptance_ref.uri,
                    pack_id,
                    version,
                    KnowledgePackStatus.DRAFT.value,
                ),
            )
            self.connection.commit()
        except BaseException:
            self.connection.rollback()
            raise
        return self.get(pack_id, version)

    def accepted(self, pack_id: str, version: int) -> ProjectKnowledgePackRecord:
        record = self._record(pack_id, version)
        if record.status is not KnowledgePackStatus.ACCEPTED:
            raise KnowledgePackValidationError("knowledge-pack version is not accepted")
        self._verify_documents(record.manifest)
        return record

    def index_accepted(
        self,
        *,
        pack_id: str,
        version: int,
        expected_manifest_sha256: str,
    ) -> int:
        record = self.accepted(pack_id, version)
        if not hmac.compare_digest(record.manifest_sha256, expected_manifest_sha256):
            raise KnowledgePackValidationError("knowledge-pack manifest hash mismatch")
        namespace = self._namespace(pack_id, version)
        self.search.clear_namespace(namespace)
        count = 0
        for binding in record.manifest.documents:
            document = self.documents.get(binding.document_id)
            if document is None:
                raise KnowledgePackValidationError("knowledge-pack document is unavailable")
            count += self.search.index_document(
                document,
                self.artifacts,
                namespace=namespace,
            )
        self.connection.execute(
            """
            UPDATE project_knowledge_packs SET indexed = 1
            WHERE pack_id = ? AND version = ? AND status = ?
            """,
            (pack_id, version, KnowledgePackStatus.ACCEPTED.value),
        )
        self.connection.commit()
        return count

    def get(self, pack_id: str, version: int) -> ProjectKnowledgePackRecord:
        return self._record(pack_id, version)

    def list(
        self,
        *,
        project_id: str | None = None,
        accepted_only: bool = False,
    ) -> tuple[ProjectKnowledgePackRecord, ...]:
        clauses: list[str] = []
        parameters: list[str] = []
        if project_id is not None:
            clauses.append("project_id = ?")
            parameters.append(project_id)
        if accepted_only:
            clauses.append("status = ?")
            parameters.append(KnowledgePackStatus.ACCEPTED.value)
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        rows = self.connection.execute(
            "SELECT pack_id, version FROM project_knowledge_packs"
            f"{where} ORDER BY project_id, pack_id, version",
            parameters,
        ).fetchall()
        return tuple(self._record(str(row[0]), int(row[1])) for row in rows)

    def _binding(self, document_id: str, project_id: str) -> KnowledgePackDocument:
        document = self.documents.get(document_id)
        if document is None:
            raise KnowledgePackValidationError(
                f"knowledge-pack document does not exist: {document_id}"
            )
        if document.scope_id != project_id:
            raise KnowledgePackValidationError(
                "knowledge-pack document is outside the project scope"
            )
        self._verify_document(document)
        return KnowledgePackDocument(
            document_id=document.document_id,
            sha256=document.sha256,
            role=document.role,
            scope=document.scope,
            scope_id=document.scope_id,
        )

    def _verify_documents(self, manifest: ProjectKnowledgePackManifest) -> None:
        for binding in manifest.documents:
            document = self.documents.get(binding.document_id)
            if document is None:
                raise KnowledgePackValidationError(
                    f"knowledge-pack document is unavailable: {binding.document_id}"
                )
            if (
                document.sha256 != binding.sha256
                or document.role is not binding.role
                or document.scope is not binding.scope
                or document.scope_id != binding.scope_id
            ):
                raise KnowledgePackValidationError(
                    "knowledge-pack document provenance no longer matches"
                )
            self._verify_document(document)

    def _verify_document(self, document: ContextDocument) -> None:
        try:
            text = self.artifacts.read_text_bounded_verified(
                document.content_ref,
                expected_sha256=document.sha256,
                max_bytes=self.max_document_bytes,
            )
        except (OSError, UnicodeError, ValueError) as exc:
            raise KnowledgePackValidationError(
                "knowledge-pack document content failed integrity verification"
            ) from exc
        if hashlib.sha256(text.encode("utf-8")).hexdigest() != document.sha256:
            raise KnowledgePackValidationError(
                "knowledge-pack document text encoding changed"
            )

    def _record(self, pack_id: str, version: int) -> ProjectKnowledgePackRecord:
        row = self._get_row(pack_id, version)
        if row is None:
            raise KeyError(f"{pack_id}:v{version}")
        return ProjectKnowledgePackRecord(
            manifest=ProjectKnowledgePackManifest.model_validate_json(row[0]),
            manifest_sha256=row[1],
            manifest_ref=row[2],
            status=KnowledgePackStatus(row[3]),
            acceptance_ref=row[4],
            indexed=bool(row[5]),
        )

    def _get_row(self, pack_id: str, version: int):
        return self.connection.execute(
            """
            SELECT manifest_json, manifest_sha256, manifest_ref, status,
                   acceptance_ref, indexed
            FROM project_knowledge_packs
            WHERE pack_id = ? AND version = ?
            """,
            (pack_id, version),
        ).fetchone()

    @staticmethod
    def _namespace(pack_id: str, version: int) -> str:
        return f"knowledge-pack:{pack_id}:v{version}"
