from __future__ import annotations

import json
import re
import sqlite3
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from universal_coding_agent.core.models import ProjectManifest
from universal_coding_agent.product.models import ContextDocument, SearchHit, SearchSourceType
from universal_coding_agent.storage.artifacts import ArtifactStore

_TOKEN = re.compile(r"[A-Za-z0-9_./:-]+")
_EXPLICIT_NAMESPACE_PREFIX = "explicit:"


class RepositorySearchIndexError(ValueError):
    """A repository search-index transition failed before partial state was exposed."""


class RepositoryDependencyGraphStateError(ValueError):
    """A repository dependency-graph state transition failed closed."""


class RepositoryCallGraphStateError(ValueError):
    """A repository call-graph state transition failed closed."""


@dataclass(frozen=True)
class RepositorySearchDocument:
    source_id: str
    path: str
    text: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class RepositorySearchIndexState:
    namespace: str
    project_id: str
    repository_url: str
    base_ref: str
    base_sha: str
    snapshot_ref: str
    snapshot_sha256: str
    policy_sha256: str


@dataclass(frozen=True)
class RepositoryDependencyGraphState:
    namespace: str
    project_id: str
    repository_url: str
    base_ref: str
    base_sha: str
    repository_snapshot_ref: str
    repository_snapshot_sha256: str
    graph_ref: str
    graph_sha256: str
    policy_sha256: str


@dataclass(frozen=True)
class RepositoryCallGraphState:
    namespace: str
    project_id: str
    repository_url: str
    base_ref: str
    base_sha: str
    repository_snapshot_ref: str
    repository_snapshot_sha256: str
    dependency_graph_ref: str
    dependency_graph_sha256: str
    graph_ref: str
    graph_sha256: str
    policy_sha256: str


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
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS repository_index_state (
                namespace TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                repository_url TEXT NOT NULL,
                base_ref TEXT NOT NULL,
                base_sha TEXT NOT NULL,
                snapshot_ref TEXT NOT NULL,
                snapshot_sha256 TEXT NOT NULL,
                policy_sha256 TEXT NOT NULL
            )
            """
        )
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS repository_dependency_graph_state (
                namespace TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                repository_url TEXT NOT NULL,
                base_ref TEXT NOT NULL,
                base_sha TEXT NOT NULL,
                repository_snapshot_ref TEXT NOT NULL,
                repository_snapshot_sha256 TEXT NOT NULL,
                graph_ref TEXT NOT NULL,
                graph_sha256 TEXT NOT NULL,
                policy_sha256 TEXT NOT NULL
            )
            """
        )
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS repository_call_graph_state (
                namespace TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                repository_url TEXT NOT NULL,
                base_ref TEXT NOT NULL,
                base_sha TEXT NOT NULL,
                repository_snapshot_ref TEXT NOT NULL,
                repository_snapshot_sha256 TEXT NOT NULL,
                dependency_graph_ref TEXT NOT NULL,
                dependency_graph_sha256 TEXT NOT NULL,
                graph_ref TEXT NOT NULL,
                graph_sha256 TEXT NOT NULL,
                policy_sha256 TEXT NOT NULL
            )
            """
        )
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()

    def clear_namespace(self, namespace: str) -> None:
        try:
            self.connection.execute("BEGIN IMMEDIATE")
            self.connection.execute(
                """
                DELETE FROM repository_call_graph_state
                WHERE namespace = ?
                   OR project_id IN (
                    SELECT project_id FROM repository_index_state WHERE namespace = ?
                    UNION
                    SELECT project_id FROM repository_dependency_graph_state WHERE namespace = ?
                )
                """,
                (namespace, namespace, namespace),
            )
            self.connection.execute(
                """
                DELETE FROM repository_dependency_graph_state
                WHERE namespace = ?
                   OR project_id IN (
                    SELECT project_id FROM repository_index_state WHERE namespace = ?
                )
                """,
                (namespace, namespace),
            )
            self.connection.execute("DELETE FROM search_records WHERE namespace = ?", (namespace,))
            self.connection.execute(
                "DELETE FROM repository_index_state WHERE namespace = ?", (namespace,)
            )
            self.connection.commit()
        except sqlite3.DatabaseError:
            self.connection.rollback()
            raise

    def repository_index_state(self, namespace: str) -> RepositorySearchIndexState | None:
        row = self.connection.execute(
            """
            SELECT namespace, project_id, repository_url, base_ref, base_sha,
                   snapshot_ref, snapshot_sha256, policy_sha256
            FROM repository_index_state
            WHERE namespace = ?
            """,
            (namespace,),
        ).fetchone()
        return RepositorySearchIndexState(*row) if row is not None else None

    def repository_dependency_graph_state(
        self, namespace: str
    ) -> RepositoryDependencyGraphState | None:
        row = self.connection.execute(
            """
            SELECT namespace, project_id, repository_url, base_ref, base_sha,
                   repository_snapshot_ref, repository_snapshot_sha256,
                   graph_ref, graph_sha256, policy_sha256
            FROM repository_dependency_graph_state
            WHERE namespace = ?
            """,
            (namespace,),
        ).fetchone()
        return RepositoryDependencyGraphState(*row) if row is not None else None

    def repository_call_graph_state(
        self, namespace: str
    ) -> RepositoryCallGraphState | None:
        row = self.connection.execute(
            """
            SELECT namespace, project_id, repository_url, base_ref, base_sha,
                   repository_snapshot_ref, repository_snapshot_sha256,
                   dependency_graph_ref, dependency_graph_sha256,
                   graph_ref, graph_sha256, policy_sha256
            FROM repository_call_graph_state
            WHERE namespace = ?
            """,
            (namespace,),
        ).fetchone()
        return RepositoryCallGraphState(*row) if row is not None else None

    def apply_repository_call_graph_state(
        self,
        *,
        state: RepositoryCallGraphState,
        expected_previous_graph_ref: str | None,
        expected_previous_graph_sha256: str | None,
    ) -> None:
        expected_namespace = f"explicit:repository-call-graph:{state.project_id}"
        if state.namespace != expected_namespace:
            raise RepositoryCallGraphStateError(
                "repository call graphs require an explicit project namespace"
            )
        if (expected_previous_graph_ref is None) != (
            expected_previous_graph_sha256 is None
        ):
            raise RepositoryCallGraphStateError(
                "repository call-graph predecessor reference and hash must be paired"
            )
        repository_namespace = f"explicit:repository-index:{state.project_id}"
        dependency_namespace = (
            f"explicit:repository-dependency-graph:{state.project_id}"
        )
        try:
            self.connection.execute("BEGIN IMMEDIATE")
            repository_row = self.connection.execute(
                """
                SELECT project_id, repository_url, base_ref, base_sha,
                       snapshot_ref, snapshot_sha256
                FROM repository_index_state
                WHERE namespace = ?
                """,
                (repository_namespace,),
            ).fetchone()
            expected_repository = (
                state.project_id,
                state.repository_url,
                state.base_ref,
                state.base_sha,
                state.repository_snapshot_ref,
                state.repository_snapshot_sha256,
            )
            if repository_row != expected_repository:
                raise RepositoryCallGraphStateError(
                    "active repository snapshot changed before call-graph state advancement"
                )

            dependency_row = self.connection.execute(
                """
                SELECT project_id, repository_url, base_ref, base_sha,
                       repository_snapshot_ref, repository_snapshot_sha256,
                       graph_ref, graph_sha256
                FROM repository_dependency_graph_state
                WHERE namespace = ?
                """,
                (dependency_namespace,),
            ).fetchone()
            expected_dependency = (
                state.project_id,
                state.repository_url,
                state.base_ref,
                state.base_sha,
                state.repository_snapshot_ref,
                state.repository_snapshot_sha256,
                state.dependency_graph_ref,
                state.dependency_graph_sha256,
            )
            if dependency_row != expected_dependency:
                raise RepositoryCallGraphStateError(
                    "active dependency graph changed before call-graph state advancement"
                )

            current_row = self.connection.execute(
                """
                SELECT namespace, project_id, repository_url, base_ref, base_sha,
                       repository_snapshot_ref, repository_snapshot_sha256,
                       dependency_graph_ref, dependency_graph_sha256,
                       graph_ref, graph_sha256, policy_sha256
                FROM repository_call_graph_state
                WHERE namespace = ?
                """,
                (state.namespace,),
            ).fetchone()
            current = (
                RepositoryCallGraphState(*current_row)
                if current_row is not None
                else None
            )
            if current is None and expected_previous_graph_sha256 is not None:
                raise RepositoryCallGraphStateError(
                    "expected predecessor repository call graph does not exist"
                )
            if current is not None:
                if (
                    expected_previous_graph_ref != current.graph_ref
                    or expected_previous_graph_sha256 != current.graph_sha256
                ):
                    raise RepositoryCallGraphStateError(
                        "repository call-graph predecessor does not match active state"
                    )
                if current == state:
                    self.connection.commit()
                    return

            self.connection.execute(
                """
                INSERT OR REPLACE INTO repository_call_graph_state (
                    namespace, project_id, repository_url, base_ref, base_sha,
                    repository_snapshot_ref, repository_snapshot_sha256,
                    dependency_graph_ref, dependency_graph_sha256,
                    graph_ref, graph_sha256, policy_sha256
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    state.namespace,
                    state.project_id,
                    state.repository_url,
                    state.base_ref,
                    state.base_sha,
                    state.repository_snapshot_ref,
                    state.repository_snapshot_sha256,
                    state.dependency_graph_ref,
                    state.dependency_graph_sha256,
                    state.graph_ref,
                    state.graph_sha256,
                    state.policy_sha256,
                ),
            )
            self.connection.commit()
        except RepositoryCallGraphStateError:
            self.connection.rollback()
            raise
        except sqlite3.DatabaseError as exc:
            self.connection.rollback()
            raise RepositoryCallGraphStateError(
                "repository call-graph state transaction failed"
            ) from exc

    def apply_repository_dependency_graph_state(
        self,
        *,
        state: RepositoryDependencyGraphState,
        expected_previous_graph_sha256: str | None,
    ) -> None:
        expected_namespace = (
            f"explicit:repository-dependency-graph:{state.project_id}"
        )
        if state.namespace != expected_namespace:
            raise RepositoryDependencyGraphStateError(
                "repository dependency graphs require an explicit project namespace"
            )
        repository_namespace = f"explicit:repository-index:{state.project_id}"
        try:
            self.connection.execute("BEGIN IMMEDIATE")
            repository_row = self.connection.execute(
                """
                SELECT project_id, repository_url, base_ref, base_sha,
                       snapshot_ref, snapshot_sha256
                FROM repository_index_state
                WHERE namespace = ?
                """,
                (repository_namespace,),
            ).fetchone()
            expected_repository = (
                state.project_id,
                state.repository_url,
                state.base_ref,
                state.base_sha,
                state.repository_snapshot_ref,
                state.repository_snapshot_sha256,
            )
            if repository_row != expected_repository:
                raise RepositoryDependencyGraphStateError(
                    "active repository snapshot changed before graph state advancement"
                )

            current_row = self.connection.execute(
                """
                SELECT namespace, project_id, repository_url, base_ref, base_sha,
                       repository_snapshot_ref, repository_snapshot_sha256,
                       graph_ref, graph_sha256, policy_sha256
                FROM repository_dependency_graph_state
                WHERE namespace = ?
                """,
                (state.namespace,),
            ).fetchone()
            current = (
                RepositoryDependencyGraphState(*current_row)
                if current_row is not None
                else None
            )
            if current is None and expected_previous_graph_sha256 is not None:
                raise RepositoryDependencyGraphStateError(
                    "expected predecessor dependency graph does not exist"
                )
            if current is not None:
                if expected_previous_graph_sha256 != current.graph_sha256:
                    raise RepositoryDependencyGraphStateError(
                        "dependency graph predecessor does not match active state"
                    )
                if current == state:
                    self.connection.commit()
                    return

            self.connection.execute(
                """
                INSERT OR REPLACE INTO repository_dependency_graph_state (
                    namespace, project_id, repository_url, base_ref, base_sha,
                    repository_snapshot_ref, repository_snapshot_sha256,
                    graph_ref, graph_sha256, policy_sha256
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    state.namespace,
                    state.project_id,
                    state.repository_url,
                    state.base_ref,
                    state.base_sha,
                    state.repository_snapshot_ref,
                    state.repository_snapshot_sha256,
                    state.graph_ref,
                    state.graph_sha256,
                    state.policy_sha256,
                ),
            )
            self.connection.commit()
        except RepositoryDependencyGraphStateError:
            self.connection.rollback()
            raise
        except sqlite3.DatabaseError as exc:
            self.connection.rollback()
            raise RepositoryDependencyGraphStateError(
                "dependency graph state transaction failed"
            ) from exc

    def apply_repository_delta(
        self,
        *,
        state: RepositorySearchIndexState,
        expected_previous_snapshot_sha256: str | None,
        remove_source_ids: tuple[str, ...],
        upserts: tuple[RepositorySearchDocument, ...],
    ) -> int:
        if not state.namespace.startswith("explicit:repository-index:"):
            raise RepositorySearchIndexError(
                "incremental repository indexes require an explicit project namespace"
            )
        ordered_removals = tuple(sorted(set(remove_source_ids)))
        ordered_upserts = tuple(sorted(upserts, key=lambda item: item.source_id))
        source_ids = [item.source_id for item in ordered_upserts]
        if len(source_ids) != len(set(source_ids)):
            raise RepositorySearchIndexError(
                "repository search delta contains duplicate source identifiers"
            )
        if any(not item.source_id or not item.path for item in ordered_upserts):
            raise RepositorySearchIndexError(
                "repository search delta contains an empty source identifier or path"
            )

        try:
            self.connection.execute("BEGIN IMMEDIATE")
            current_row = self.connection.execute(
                """
                SELECT namespace, project_id, repository_url, base_ref, base_sha,
                       snapshot_ref, snapshot_sha256, policy_sha256
                FROM repository_index_state
                WHERE namespace = ?
                """,
                (state.namespace,),
            ).fetchone()
            current = RepositorySearchIndexState(*current_row) if current_row is not None else None
            if current is None and expected_previous_snapshot_sha256 is not None:
                raise RepositorySearchIndexError(
                    "expected predecessor repository index does not exist"
                )
            if current is not None:
                if expected_previous_snapshot_sha256 != current.snapshot_sha256:
                    raise RepositorySearchIndexError(
                        "repository index predecessor does not match active state"
                    )
                if current == state:
                    self.connection.commit()
                    return 0

            for source_id in sorted(set(ordered_removals) | set(source_ids)):
                self.connection.execute(
                    "DELETE FROM search_records WHERE namespace = ? AND source_id = ?",
                    (state.namespace, source_id),
                )

            chunk_count = 0
            for document in ordered_upserts:
                chunk_count += self._index_text_without_commit(
                    namespace=state.namespace,
                    source_type=SearchSourceType.CODE,
                    source_id=document.source_id,
                    path=document.path,
                    text=document.text,
                    metadata=document.metadata,
                )

            self.connection.execute(
                """
                INSERT OR REPLACE INTO repository_index_state (
                    namespace, project_id, repository_url, base_ref, base_sha,
                    snapshot_ref, snapshot_sha256, policy_sha256
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    state.namespace,
                    state.project_id,
                    state.repository_url,
                    state.base_ref,
                    state.base_sha,
                    state.snapshot_ref,
                    state.snapshot_sha256,
                    state.policy_sha256,
                ),
            )
            self.connection.commit()
            return chunk_count
        except RepositorySearchIndexError:
            self.connection.rollback()
            raise
        except sqlite3.DatabaseError as exc:
            self.connection.rollback()
            raise RepositorySearchIndexError("repository search-index transaction failed") from exc

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
        count = self._index_text_without_commit(
            namespace=namespace,
            source_type=source_type,
            source_id=source_id,
            path=path,
            text=text,
            metadata=metadata,
        )
        self.connection.commit()
        return count

    def _index_text_without_commit(
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
