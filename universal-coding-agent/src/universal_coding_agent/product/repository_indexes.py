from __future__ import annotations

import hashlib
import hmac
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from universal_coding_agent.core.models import FrozenModel, ProjectFile, ProjectManifest
from universal_coding_agent.product.models import SearchHit, SearchSourceType
from universal_coding_agent.product.search_service import (
    RepositorySearchDocument,
    RepositorySearchIndexError,
    RepositorySearchIndexState,
    SearchService,
)
from universal_coding_agent.repository.indexer import (
    DEFAULT_DENY_PATTERNS,
    INDEX_POLICY_VERSION,
    RepositoryIndexer,
    RepositoryIndexingError,
)
from universal_coding_agent.storage.artifacts import ArtifactStore

DEFAULT_REPOSITORY_SNAPSHOT_MAX_BYTES = 8_000_000
_PROJECT_ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")


class RepositoryIndexError(ValueError):
    """An incremental repository index cannot satisfy its provenance contract."""


class RepositoryIndexRename(FrozenModel):
    old_path: str = Field(min_length=1, max_length=4096)
    new_path: str = Field(min_length=1, max_length=4096)


class RepositoryIndexDelta(FrozenModel):
    added_paths: tuple[str, ...] = ()
    modified_paths: tuple[str, ...] = ()
    deleted_paths: tuple[str, ...] = ()
    renamed_paths: tuple[RepositoryIndexRename, ...] = ()
    reused_paths: tuple[str, ...] = ()


class RepositorySnapshotFile(FrozenModel):
    path: str = Field(min_length=1, max_length=4096)
    git_mode: str = Field(pattern=r"^[0-9]{6}$")
    git_blob_oid: str = Field(pattern=r"^[0-9a-f]{40,64}$")
    project_file: ProjectFile

    @model_validator(mode="after")
    def validate_matching_path(self) -> RepositorySnapshotFile:
        if self.path != self.project_file.path:
            raise ValueError("repository snapshot paths do not match")
        return self


class RepositoryIndexSnapshot(FrozenModel):
    schema_version: Literal["1"] = "1"
    project_id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")
    repository_url: str = Field(min_length=1, max_length=2048)
    base_ref: str = Field(min_length=1, max_length=256)
    base_sha: str = Field(pattern=r"^[0-9a-f]{40,64}$")
    namespace: str = Field(pattern=r"^explicit:repository-index:[a-zA-Z0-9._-]+$")
    policy_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    max_file_bytes: int = Field(ge=1)
    chunk_chars: int = Field(ge=1)
    chunk_overlap: int = Field(ge=0)
    previous_snapshot_ref: str | None = Field(
        default=None, pattern=r"^artifact://[a-zA-Z0-9._/-]+$"
    )
    previous_snapshot_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    files: tuple[RepositorySnapshotFile, ...] = ()
    delta: RepositoryIndexDelta

    @model_validator(mode="after")
    def validate_snapshot(self) -> RepositoryIndexSnapshot:
        if self.namespace != f"explicit:repository-index:{self.project_id}":
            raise ValueError("repository snapshot namespace does not match project identity")
        if (self.previous_snapshot_ref is None) != (self.previous_snapshot_sha256 is None):
            raise ValueError("repository predecessor reference and hash must be paired")
        paths = tuple(item.path for item in self.files)
        if paths != tuple(sorted(paths)) or len(paths) != len(set(paths)):
            raise ValueError("repository snapshot files must be unique and sorted")
        return self

    def canonical_content(self) -> str:
        return _canonical_json(self.model_dump(mode="json"))

    def canonical_hash(self) -> str:
        return hashlib.sha256(self.canonical_content().encode("utf-8")).hexdigest()

    def manifest(self) -> ProjectManifest:
        project_files = tuple(item.project_file for item in self.files)
        language_counts = Counter(item.language for item in project_files)
        instructions: list[str] = []
        architecture: list[str] = []
        tests: list[str] = []
        for item in project_files:
            lower = item.path.lower()
            name = Path(item.path).name.lower()
            if name == "agents.md" or name.startswith("readme"):
                instructions.append(item.path)
            if "/adr/" in f"/{lower}" or "architecture" in lower:
                architecture.append(item.path)
            if item.is_test:
                tests.append(item.path)
        return ProjectManifest(
            repository_url=self.repository_url,
            base_ref=self.base_ref,
            base_sha=self.base_sha,
            files=project_files,
            instruction_paths=tuple(sorted(instructions)),
            architecture_paths=tuple(sorted(architecture)),
            test_paths=tuple(sorted(tests)),
            language_counts=dict(sorted(language_counts.items())),
        )


class RepositoryIndexResult(FrozenModel):
    snapshot_ref: str = Field(pattern=r"^artifact://[a-zA-Z0-9._/-]+$")
    snapshot_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    snapshot: RepositoryIndexSnapshot
    manifest: ProjectManifest
    indexed_chunk_count: int = Field(ge=0)
    replayed: bool = False


class RepositoryIndexService:
    """Persist and atomically advance one explicit repository index per project."""

    def __init__(
        self,
        artifacts: ArtifactStore,
        search: SearchService,
        *,
        indexer: RepositoryIndexer | None = None,
        snapshot_max_bytes: int = DEFAULT_REPOSITORY_SNAPSHOT_MAX_BYTES,
    ) -> None:
        if snapshot_max_bytes < 1:
            raise ValueError("repository snapshot byte limit must be positive")
        self.artifacts = artifacts
        self.search = search
        self.indexer = indexer or RepositoryIndexer()
        self.snapshot_max_bytes = snapshot_max_bytes

    def index(
        self,
        *,
        project_id: str,
        root: Path,
        repository_url: str,
        base_ref: str,
        base_sha: str,
        expected_previous_snapshot_sha256: str | None,
    ) -> RepositoryIndexResult:
        if not _PROJECT_ID.fullmatch(project_id):
            raise RepositoryIndexError("project ID is invalid")
        root = root.resolve()
        namespace = self.namespace(project_id)
        policy_sha256 = self._policy_sha256()
        try:
            self.indexer.verify_clean_base(root, base_sha=base_sha)
        except (RepositoryIndexingError, subprocess.SubprocessError) as exc:
            raise RepositoryIndexError(str(exc)) from exc

        active_state = self.search.repository_index_state(namespace)
        previous: RepositoryIndexSnapshot | None = None
        if active_state is None:
            if expected_previous_snapshot_sha256 is not None:
                raise RepositoryIndexError("expected predecessor repository index does not exist")
        else:
            if expected_previous_snapshot_sha256 != active_state.snapshot_sha256:
                raise RepositoryIndexError(
                    "expected predecessor does not match the active repository index"
                )
            previous = self._load_active_snapshot(active_state)
            self._verify_compatible_previous(
                previous,
                project_id=project_id,
                repository_url=repository_url,
                base_ref=base_ref,
                policy_sha256=policy_sha256,
            )
            if previous.base_sha == base_sha:
                return RepositoryIndexResult(
                    snapshot_ref=active_state.snapshot_ref,
                    snapshot_sha256=active_state.snapshot_sha256,
                    snapshot=previous,
                    manifest=previous.manifest(),
                    indexed_chunk_count=0,
                    replayed=True,
                )
            try:
                self.indexer.verify_ancestor(
                    root,
                    ancestor_sha=previous.base_sha,
                    descendant_sha=base_sha,
                )
            except (RepositoryIndexingError, subprocess.SubprocessError) as exc:
                raise RepositoryIndexError(str(exc)) from exc

        snapshot = self._build_snapshot(
            project_id=project_id,
            root=root,
            repository_url=repository_url,
            base_ref=base_ref,
            base_sha=base_sha,
            namespace=namespace,
            policy_sha256=policy_sha256,
            previous=previous,
            previous_ref=active_state.snapshot_ref if active_state else None,
            previous_sha256=active_state.snapshot_sha256 if active_state else None,
        )
        content = snapshot.canonical_content()
        if len(content.encode("utf-8")) > self.snapshot_max_bytes:
            raise RepositoryIndexError("repository index snapshot exceeds its byte limit")
        snapshot_sha256 = snapshot.canonical_hash()
        reference = self.artifacts.write_text(
            (f"repository-indexes/{project_id}/{base_sha}/snapshot-{snapshot_sha256}.json"),
            content,
            "application/json",
        )
        if not hmac.compare_digest(reference.sha256, snapshot_sha256):
            raise RepositoryIndexError("repository snapshot artifact hash mismatch")

        changed_paths = (
            set(snapshot.delta.added_paths)
            | set(snapshot.delta.modified_paths)
            | {item.new_path for item in snapshot.delta.renamed_paths}
        )
        remove_source_ids = tuple(
            sorted(
                changed_paths
                | set(snapshot.delta.deleted_paths)
                | {item.old_path for item in snapshot.delta.renamed_paths}
            )
        )
        current_files = {item.path: item for item in snapshot.files}
        upserts = tuple(
            document
            for path in sorted(changed_paths)
            if (document := self._search_document(root, current_files[path])) is not None
        )
        try:
            self.indexer.verify_clean_base(root, base_sha=base_sha)
            indexed_chunk_count = self.search.apply_repository_delta(
                state=RepositorySearchIndexState(
                    namespace=namespace,
                    project_id=project_id,
                    repository_url=repository_url,
                    base_ref=base_ref,
                    base_sha=base_sha,
                    snapshot_ref=reference.uri,
                    snapshot_sha256=snapshot_sha256,
                    policy_sha256=policy_sha256,
                ),
                expected_previous_snapshot_sha256=expected_previous_snapshot_sha256,
                remove_source_ids=remove_source_ids,
                upserts=upserts,
            )
        except (RepositoryIndexingError, RepositorySearchIndexError) as exc:
            raise RepositoryIndexError(str(exc)) from exc

        verified = self._load_snapshot(reference.uri, snapshot_sha256)
        return RepositoryIndexResult(
            snapshot_ref=reference.uri,
            snapshot_sha256=snapshot_sha256,
            snapshot=verified,
            manifest=verified.manifest(),
            indexed_chunk_count=indexed_chunk_count,
        )

    def search_project(
        self, project_id: str, query: str, *, top_k: int = 20
    ) -> tuple[SearchHit, ...]:
        if not _PROJECT_ID.fullmatch(project_id):
            raise RepositoryIndexError("project ID is invalid")
        return self.search.search(
            query,
            top_k=top_k,
            namespaces=(self.namespace(project_id),),
            source_types=(SearchSourceType.CODE,),
        )

    @staticmethod
    def namespace(project_id: str) -> str:
        return f"explicit:repository-index:{project_id}"

    def _build_snapshot(
        self,
        *,
        project_id: str,
        root: Path,
        repository_url: str,
        base_ref: str,
        base_sha: str,
        namespace: str,
        policy_sha256: str,
        previous: RepositoryIndexSnapshot | None,
        previous_ref: str | None,
        previous_sha256: str | None,
    ) -> RepositoryIndexSnapshot:
        previous_files = {item.path: item for item in previous.files} if previous else {}
        current_files: dict[str, RepositorySnapshotFile] = {}
        try:
            tracked = self.indexer.tracked_files(root)
            for item in tracked:
                if self.indexer.is_denied(item.path):
                    continue
                prior = previous_files.get(item.path)
                if (
                    prior is not None
                    and prior.git_mode == item.git_mode
                    and prior.git_blob_oid == item.git_blob_oid
                ):
                    current_files[item.path] = prior
                    continue
                project_file = self.indexer.project_file(root, item.path)
                if project_file is None:
                    continue
                current_files[item.path] = RepositorySnapshotFile(
                    path=item.path,
                    git_mode=item.git_mode,
                    git_blob_oid=item.git_blob_oid,
                    project_file=project_file,
                )
        except (OSError, RepositoryIndexingError, subprocess.SubprocessError) as exc:
            raise RepositoryIndexError("repository snapshot construction failed") from exc

        delta = _delta(previous_files, current_files)
        return RepositoryIndexSnapshot(
            project_id=project_id,
            repository_url=repository_url,
            base_ref=base_ref,
            base_sha=base_sha,
            namespace=namespace,
            policy_sha256=policy_sha256,
            max_file_bytes=self.indexer.max_file_bytes,
            chunk_chars=self.search.chunk_chars,
            chunk_overlap=self.search.chunk_overlap,
            previous_snapshot_ref=previous_ref,
            previous_snapshot_sha256=previous_sha256,
            files=tuple(current_files[path] for path in sorted(current_files)),
            delta=delta,
        )

    def _load_active_snapshot(self, state: RepositorySearchIndexState) -> RepositoryIndexSnapshot:
        snapshot = self._load_snapshot(state.snapshot_ref, state.snapshot_sha256)
        if (
            snapshot.namespace != state.namespace
            or snapshot.project_id != state.project_id
            or snapshot.repository_url != state.repository_url
            or snapshot.base_ref != state.base_ref
            or snapshot.base_sha != state.base_sha
            or snapshot.policy_sha256 != state.policy_sha256
        ):
            raise RepositoryIndexError(
                "active repository index state does not match snapshot provenance"
            )
        return snapshot

    def _load_snapshot(self, reference: str, expected_sha256: str) -> RepositoryIndexSnapshot:
        try:
            content = self.artifacts.read_text_bounded_verified(
                reference,
                expected_sha256=expected_sha256,
                max_bytes=self.snapshot_max_bytes,
            )
            snapshot = RepositoryIndexSnapshot.model_validate_json(content)
        except (OSError, UnicodeError, ValueError) as exc:
            raise RepositoryIndexError("repository index snapshot verification failed") from exc
        if not hmac.compare_digest(snapshot.canonical_hash(), expected_sha256):
            raise RepositoryIndexError("repository index snapshot canonical hash mismatch")
        return snapshot

    def _verify_compatible_previous(
        self,
        snapshot: RepositoryIndexSnapshot,
        *,
        project_id: str,
        repository_url: str,
        base_ref: str,
        policy_sha256: str,
    ) -> None:
        if snapshot.project_id != project_id:
            raise RepositoryIndexError("repository index project scope does not match")
        if snapshot.repository_url != repository_url or snapshot.base_ref != base_ref:
            raise RepositoryIndexError("repository index source identity does not match")
        if not hmac.compare_digest(snapshot.policy_sha256, policy_sha256):
            raise RepositoryIndexError("repository index policy does not match")

    def _policy_sha256(self) -> str:
        payload = _canonical_json(
            {
                "schema_version": "1",
                "index_policy_version": INDEX_POLICY_VERSION,
                "deny_patterns": list(DEFAULT_DENY_PATTERNS),
                "max_file_bytes": self.indexer.max_file_bytes,
                "chunk_chars": self.search.chunk_chars,
                "chunk_overlap": self.search.chunk_overlap,
            }
        ).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    @staticmethod
    def _search_document(
        root: Path, item: RepositorySnapshotFile
    ) -> RepositorySearchDocument | None:
        path = (root / item.path).resolve()
        if path != root and root not in path.parents:
            raise RepositoryIndexError("repository search path escapes the source root")
        try:
            data = path.read_bytes()
        except OSError as exc:
            raise RepositoryIndexError("repository search source cannot be read") from exc
        project_file = item.project_file
        if len(data) != project_file.size or not hmac.compare_digest(
            hashlib.sha256(data).hexdigest(), project_file.sha256
        ):
            raise RepositoryIndexError("repository search source drifted after snapshot")
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            return None
        return RepositorySearchDocument(
            source_id=item.path,
            path=item.path,
            text=text,
            metadata={
                "language": project_file.language,
                "is_test": project_file.is_test,
                "symbols": list(project_file.symbols),
                "imports": list(project_file.imports),
                "sha256": project_file.sha256,
                "git_mode": item.git_mode,
                "git_blob_oid": item.git_blob_oid,
            },
        )


def _delta(
    previous: dict[str, RepositorySnapshotFile],
    current: dict[str, RepositorySnapshotFile],
) -> RepositoryIndexDelta:
    previous_paths = set(previous)
    current_paths = set(current)
    reused = {path for path in previous_paths & current_paths if previous[path] == current[path]}
    modified = (previous_paths & current_paths) - reused
    added = current_paths - previous_paths
    deleted = previous_paths - current_paths

    renamed: list[RepositoryIndexRename] = []
    remaining_added = set(added)
    remaining_deleted = set(deleted)
    added_by_identity: dict[tuple[str, str], list[str]] = {}
    for path in sorted(added):
        item = current[path]
        identity = (item.project_file.sha256, item.git_mode)
        added_by_identity.setdefault(identity, []).append(path)
    for old_path in sorted(deleted):
        old = previous[old_path]
        identity = (old.project_file.sha256, old.git_mode)
        candidates = added_by_identity.get(identity, [])
        if not candidates:
            continue
        new_path = candidates.pop(0)
        remaining_deleted.remove(old_path)
        remaining_added.remove(new_path)
        renamed.append(RepositoryIndexRename(old_path=old_path, new_path=new_path))

    return RepositoryIndexDelta(
        added_paths=tuple(sorted(remaining_added)),
        modified_paths=tuple(sorted(modified)),
        deleted_paths=tuple(sorted(remaining_deleted)),
        renamed_paths=tuple(renamed),
        reused_paths=tuple(sorted(reused)),
    )


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        separators=(",", ":"),
        sort_keys=True,
        ensure_ascii=False,
    )
