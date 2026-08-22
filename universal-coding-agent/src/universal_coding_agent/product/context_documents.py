from __future__ import annotations

import hashlib
import re
import sqlite3
from pathlib import Path

from universal_coding_agent.product.models import ContextDocument, ContextScope, DocumentRole
from universal_coding_agent.storage.artifacts import ArtifactStore

_ALLOWED_SUFFIXES = {
    ".txt": "text/plain",
    ".md": "text/markdown",
    ".log": "text/plain",
    ".json": "application/json",
    ".yaml": "application/yaml",
    ".yml": "application/yaml",
    ".xml": "application/xml",
    ".csv": "text/csv",
    ".sql": "text/x-sql",
    ".py": "text/x-python",
    ".ts": "text/typescript",
    ".tsx": "text/typescript",
    ".js": "text/javascript",
    ".jsx": "text/javascript",
    ".java": "text/x-java-source",
    ".cs": "text/plain",
    ".sh": "text/x-shellscript",
    ".ps1": "text/plain",
    ".tf": "text/plain",
    ".properties": "text/plain",
    ".ini": "text/plain",
    ".conf": "text/plain",
}

_SECRET_PATTERNS = (
    ("private_key", re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")),
    ("openai_key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    (
        "bearer_token",
        re.compile(r"(?i)authorization\s*:\s*bearer\s+[A-Za-z0-9._~+/-]{16,}"),
    ),
)


class DocumentValidationError(ValueError):
    pass


class ContextDocumentService:
    """Immutable, text-only context-document ingestion.

    Uploaded content is data by default. The role controls how downstream services may use
    it; an error log or reference document is never silently promoted to an instruction.
    """

    def __init__(
        self,
        database_path: Path,
        artifacts: ArtifactStore,
        *,
        max_bytes: int = 10_000_000,
    ) -> None:
        self.database_path = database_path.resolve()
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.artifacts = artifacts
        self.max_bytes = max_bytes
        self.connection = sqlite3.connect(self.database_path, check_same_thread=False)
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS context_documents (
                document_id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                role TEXT NOT NULL,
                scope TEXT NOT NULL,
                scope_id TEXT NOT NULL,
                sha256 TEXT NOT NULL,
                size INTEGER NOT NULL,
                media_type TEXT NOT NULL,
                content_ref TEXT NOT NULL,
                metadata_ref TEXT NOT NULL
            )
            """
        )
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()

    def ingest(
        self,
        *,
        document_id: str,
        filename: str,
        content: bytes | str,
        role: DocumentRole,
        scope: ContextScope,
        scope_id: str,
    ) -> ContextDocument:
        if self.get(document_id) is not None:
            raise DocumentValidationError(f"document already exists: {document_id}")
        suffix = Path(filename).suffix.lower()
        media_type = _ALLOWED_SUFFIXES.get(suffix)
        if media_type is None:
            raise DocumentValidationError(f"unsupported text document type: {suffix or '<none>'}")
        raw = content.encode("utf-8") if isinstance(content, str) else content
        if len(raw) > self.max_bytes:
            raise DocumentValidationError("document exceeds the configured text size limit")
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise DocumentValidationError("document must be valid UTF-8 text") from exc
        self._validate_text(text)
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        safe_id = self._safe_id(document_id)
        content_ref = self.artifacts.write_text(
            f"documents/{safe_id}/content.txt",
            text,
            media_type,
        )
        metadata_payload = {
            "document_id": document_id,
            "filename": filename,
            "role": role.value,
            "scope": scope.value,
            "scope_id": scope_id,
            "sha256": digest,
            "size": len(text.encode("utf-8")),
            "media_type": media_type,
            "content_ref": content_ref.uri,
        }
        metadata_ref = self.artifacts.write_json(
            f"documents/{safe_id}/metadata.json",
            metadata_payload,
        )
        document = ContextDocument(
            **metadata_payload,
            metadata_ref=metadata_ref.uri,
        )
        self.connection.execute(
            """
            INSERT INTO context_documents (
                document_id, filename, role, scope, scope_id, sha256, size,
                media_type, content_ref, metadata_ref
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                document.document_id,
                document.filename,
                document.role.value,
                document.scope.value,
                document.scope_id,
                document.sha256,
                document.size,
                document.media_type,
                document.content_ref,
                document.metadata_ref,
            ),
        )
        self.connection.commit()
        return document

    def get(self, document_id: str) -> ContextDocument | None:
        row = self.connection.execute(
            """
            SELECT document_id, filename, role, scope, scope_id, sha256, size,
                   media_type, content_ref, metadata_ref
            FROM context_documents WHERE document_id = ?
            """,
            (document_id,),
        ).fetchone()
        if row is None:
            return None
        return ContextDocument(
            document_id=row[0],
            filename=row[1],
            role=DocumentRole(row[2]),
            scope=ContextScope(row[3]),
            scope_id=row[4],
            sha256=row[5],
            size=row[6],
            media_type=row[7],
            content_ref=row[8],
            metadata_ref=row[9],
        )

    def list(self, *, scope_id: str | None = None) -> tuple[ContextDocument, ...]:
        if scope_id is None:
            rows = self.connection.execute(
                "SELECT document_id FROM context_documents ORDER BY document_id"
            ).fetchall()
        else:
            rows = self.connection.execute(
                """
                SELECT document_id FROM context_documents
                WHERE scope_id = ? ORDER BY document_id
                """,
                (scope_id,),
            ).fetchall()
        return tuple(document for row in rows if (document := self.get(row[0])) is not None)

    def read_text(self, document_id: str) -> str:
        document = self.get(document_id)
        if document is None:
            raise KeyError(document_id)
        return self.artifacts.read_text(document.content_ref)

    @staticmethod
    def _safe_id(document_id: str) -> str:
        if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}", document_id):
            raise DocumentValidationError("invalid document_id")
        return document_id

    @staticmethod
    def _validate_text(text: str) -> None:
        if "\x00" in text:
            raise DocumentValidationError("binary/NUL content is not accepted")
        unsupported_controls = [
            char for char in text if ord(char) < 32 and char not in {"\n", "\r", "\t"}
        ]
        if unsupported_controls:
            raise DocumentValidationError("document contains unsupported control characters")
        findings = [name for name, pattern in _SECRET_PATTERNS if pattern.search(text)]
        if findings:
            raise DocumentValidationError(
                "document contains sensitive credential material: " + ", ".join(findings)
            )
