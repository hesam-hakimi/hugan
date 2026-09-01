from __future__ import annotations

import json
import re
import sqlite3
from collections.abc import Callable
from pathlib import Path
from typing import Any

from universal_coding_agent.core.models import ProjectManifest
from universal_coding_agent.product.models import ContextDocument, SearchHit, SearchSourceType
from universal_coding_agent.storage.artifacts import ArtifactStore

_TOKEN = re.compile(r"[A-Za-z0-9_./:-]+")
_EXPLICIT_NAMESPACE_PREFIX = "explicit:"


class SearchService:
    """Persistent hybrid search over code, uploaded text, decisions, and artifacts.

    The deterministic baseline combines path, exact phrase, token, symbol, and dependency
    evidence. An optional semantic ranker can be injected later without changing callers.
    """

    def __init__(
        self,
        database_path: Path,
        *,
        semantic_ranker: Callable[[str, list[str]], list[float]] | None = None,
        chunk_chars: int = 4000,
        chunk_overlap: int = 400,
    ) -> None:
        self.database_path = database_path.resolve()
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.semantic_ranker = semantic_ranker
        self.chunk_chars = chunk_chars
        self.chunk_overlap = min(chunk_overlap, max(0, chunk_chars - 1))
        self.connection = sqlite3.connect(self.database_path, check_same_thread=False)
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS search_records (
                record_id TEXT PRIMARY KEY,
                namespace TEXT NOT NULL,
                source_type TEXT NOT NULL,
                source_id TEXT NOT NULL,
                path TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata_json TEXT NOT NULL
            )
            """
        )
        self.connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_search_namespace ON search_records(namespace)"
        )
        self.connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_search_path ON search_records(path)"
        )
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()

    def clear_namespace(self, namespace: str) -> None:
        self.connection.execute("DELETE FROM search_records WHERE namespace = ?", (namespace,))
        self.connection.commit()

    def index_repository(
        self,
        root: Path,
        manifest: ProjectManifest,
        *,
        namespace: str = "repository",
    ) -> int:
        root = root.resolve()
        self.clear_namespace(namespace)
        count = 0
        for project_file in manifest.files:
            path = (root / project_file.path).resolve()
            if path != root and root not in path.parents:
                continue
            if not path.is_file():
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            metadata = {
                "language": project_file.language,
                "is_test": project_file.is_test,
                "symbols": list(project_file.symbols),
                "imports": list(project_file.imports),
                "sha256": project_file.sha256,
            }
            count += self.index_text(
                namespace=namespace,
                source_type=SearchSourceType.CODE,
                source_id=project_file.path,
                path=project_file.path,
                text=text,
                metadata=metadata,
            )
        return count

    def index_document(
        self,
        document: ContextDocument,
        artifacts: ArtifactStore,
        *,
        namespace: str = "documents",
    ) -> int:
        text = artifacts.read_text(document.content_ref)
        metadata = {
            "document_id": document.document_id,
            "filename": document.filename,
            "role": document.role.value,
            "scope": document.scope.value,
            "scope_id": document.scope_id,
            "sha256": document.sha256,
        }
        self.connection.execute(
            "DELETE FROM search_records WHERE namespace = ? AND source_id = ?",
            (namespace, document.document_id),
        )
        self.connection.commit()
        return self.index_text(
            namespace=namespace,
            source_type=SearchSourceType.DOCUMENT,
            source_id=document.document_id,
            path=document.filename,
            text=text,
            metadata=metadata,
        )

    def index_text(
        self,
        *,
        namespace: str,
        source_type: SearchSourceType,
        source_id: str,
        path: str,
        text: str,
        metadata: dict[str, Any] | None = None,
    ) -> int:
        chunks = self._chunks(text)
        for index, chunk in enumerate(chunks):
            record_id = f"{namespace}:{source_type.value}:{source_id}:{index:06d}"
            self.connection.execute(
                """
                INSERT OR REPLACE INTO search_records (
                    record_id, namespace, source_type, source_id, path, content, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record_id,
                    namespace,
                    source_type.value,
                    source_id,
                    path,
                    chunk,
                    json.dumps(metadata or {}, sort_keys=True, ensure_ascii=False),
                ),
            )
        self.connection.commit()
        return len(chunks)

    def search(
        self,
        query: str,
        *,
        top_k: int = 20,
        namespaces: tuple[str, ...] = (),
        source_types: tuple[SearchSourceType, ...] = (),
    ) -> tuple[SearchHit, ...]:
        normalized_query = query.strip()
        if not normalized_query:
            return ()
        rows = self._candidate_rows(namespaces, source_types)
        tokens = tuple(dict.fromkeys(token.lower() for token in _TOKEN.findall(normalized_query)))
        query_lower = normalized_query.lower()
        scored: list[tuple[float, tuple[Any, ...], dict[str, Any]]] = []
        semantic_texts: list[str] = []
        staged: list[tuple[tuple[Any, ...], dict[str, Any], float]] = []
        for row in rows:
            metadata = json.loads(row[6])
            path_lower = row[4].lower()
            content_lower = row[5].lower()
            symbol_text = " ".join(metadata.get("symbols", [])).lower()
            import_text = " ".join(metadata.get("imports", [])).lower()
            score = 0.0
            if query_lower in content_lower:
                score += 8.0
            if query_lower in path_lower:
                score += 10.0
            for token in tokens:
                score += content_lower.count(token) * 1.0
                score += path_lower.count(token) * 4.0
                score += symbol_text.count(token) * 6.0
                score += import_text.count(token) * 3.0
            if score <= 0:
                continue
            staged.append((row, metadata, score))
            semantic_texts.append(f"{row[4]}\n{row[5]}")

        semantic_scores = (
            self.semantic_ranker(normalized_query, semantic_texts)
            if self.semantic_ranker and semantic_texts
            else [0.0] * len(staged)
        )
        if len(semantic_scores) != len(staged):
            raise ValueError("semantic ranker returned an unexpected score count")
        for (row, metadata, base_score), semantic_score in zip(
            staged, semantic_scores, strict=True
        ):
            scored.append((base_score + max(0.0, float(semantic_score)), row, metadata))
        scored.sort(key=lambda item: (-item[0], item[1][4], item[1][0]))
        return tuple(
            SearchHit(
                record_id=row[0],
                source_type=SearchSourceType(row[2]),
                source_id=row[3],
                path=row[4],
                score=score,
                excerpt=self._excerpt(row[5], tokens),
                metadata=metadata,
            )
            for score, row, metadata in scored[:top_k]
        )

    def _candidate_rows(
        self,
        namespaces: tuple[str, ...],
        source_types: tuple[SearchSourceType, ...],
    ) -> list[tuple[Any, ...]]:
        clauses: list[str] = []
        params: list[str] = []
        if namespaces:
            clauses.append("namespace IN (" + ",".join("?" for _ in namespaces) + ")")
            params.extend(namespaces)
        else:
            clauses.append("namespace NOT LIKE ?")
            params.append(f"{_EXPLICIT_NAMESPACE_PREFIX}%")
        if source_types:
            clauses.append("source_type IN (" + ",".join("?" for _ in source_types) + ")")
            params.extend(item.value for item in source_types)
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        return self.connection.execute(
            "SELECT record_id, namespace, source_type, source_id, path, content, metadata_json "
            f"FROM search_records{where}",
            params,
        ).fetchall()

    def _chunks(self, text: str) -> tuple[str, ...]:
        if not text:
            return ("",)
        chunks: list[str] = []
        start = 0
        while start < len(text):
            end = min(len(text), start + self.chunk_chars)
            chunks.append(text[start:end])
            if end == len(text):
                break
            start = end - self.chunk_overlap
        return tuple(chunks)

    @staticmethod
    def _excerpt(content: str, tokens: tuple[str, ...], *, limit: int = 800) -> str:
        lower = content.lower()
        positions = [lower.find(token) for token in tokens if lower.find(token) >= 0]
        start = max(0, (min(positions) if positions else 0) - 160)
        return content[start : start + limit].strip()
