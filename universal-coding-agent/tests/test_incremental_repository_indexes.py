from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from universal_coding_agent.product.repository_indexes import (
    RepositoryIndexError,
    RepositoryIndexService,
)
from universal_coding_agent.product.search_service import SearchService
from universal_coding_agent.product.workspace import ProductWorkspace
from universal_coding_agent.providers.fake import FakeModelProvider
from universal_coding_agent.repository.indexer import RepositoryIndexer
from universal_coding_agent.storage.artifacts import ArtifactStore


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _write(root: Path, relative: str, content: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _commit(root: Path, message: str) -> str:
    _git(root, "add", "-A")
    _git(root, "commit", "-m", message)
    return _git(root, "rev-parse", "HEAD")


def _repository(tmp_path: Path) -> tuple[Path, str]:
    root = tmp_path / "source"
    root.mkdir()
    _git(root, "init", "-b", "main")
    _git(root, "config", "user.email", "index@example.test")
    _git(root, "config", "user.name", "Index Test")
    _write(root, "README.md", "Repository index fixture.\n")
    _commit(root, "initial fixture")
    _write(root, "app.py", "def alpha():\n    return 'ALPHA_TOKEN_OLD'\n")
    _write(root, "unchanged.py", "UNCHANGED_TOKEN = True\n")
    _write(root, "docs/guide.md", "GUIDE_RENAME_TOKEN\n")
    _write(root, "delete_me.py", "DELETE_TOKEN = True\n")
    _write(root, ".env", "SECRET_MUST_NOT_BE_INDEXED=1\n")
    return root, _commit(root, "tracked fixture")


def _service(
    tmp_path: Path,
    *,
    max_file_bytes: int = 2_000_000,
    chunk_chars: int = 4000,
    snapshot_max_bytes: int = 8_000_000,
) -> tuple[ArtifactStore, SearchService, RepositoryIndexService]:
    artifacts = ArtifactStore(tmp_path / "artifacts")
    search = SearchService(
        tmp_path / "search.sqlite",
        chunk_chars=chunk_chars,
    )
    service = RepositoryIndexService(
        artifacts,
        search,
        indexer=RepositoryIndexer(max_file_bytes=max_file_bytes),
        snapshot_max_bytes=snapshot_max_bytes,
    )
    return artifacts, search, service


def _index(
    service: RepositoryIndexService,
    root: Path,
    base_sha: str,
    previous_sha256: str | None,
):
    return service.index(
        project_id="project-alpha",
        root=root,
        repository_url="https://example.test/project-alpha.git",
        base_ref="main",
        base_sha=base_sha,
        expected_previous_snapshot_sha256=previous_sha256,
    )


def test_incremental_index_applies_add_modify_delete_and_rename_as_full_equivalent(
    tmp_path: Path,
) -> None:
    root, first_sha = _repository(tmp_path)
    _artifacts, search, service = _service(tmp_path / "state")
    try:
        first = _index(service, root, first_sha, None)
        assert set(first.snapshot.delta.added_paths) == {
            "README.md",
            "app.py",
            "delete_me.py",
            "docs/guide.md",
            "unchanged.py",
        }
        assert ".env" not in {item.path for item in first.snapshot.files}
        assert service.search_project("project-alpha", "ALPHA_TOKEN_OLD")
        assert search.search("ALPHA_TOKEN_OLD") == ()

        _write(root, "app.py", "def alpha():\n    return 'ALPHA_TOKEN_NEW'\n")
        _git(root, "mv", "docs/guide.md", "docs/runbook.md")
        _git(root, "rm", "delete_me.py")
        _write(root, "new.py", "NEW_INDEX_TOKEN = True\n")
        second_sha = _commit(root, "change indexed files")

        second = _index(service, root, second_sha, first.snapshot_sha256)
        assert second.snapshot.delta.added_paths == ("new.py",)
        assert second.snapshot.delta.modified_paths == ("app.py",)
        assert second.snapshot.delta.deleted_paths == ("delete_me.py",)
        assert [(item.old_path, item.new_path) for item in second.snapshot.delta.renamed_paths] == [
            ("docs/guide.md", "docs/runbook.md")
        ]
        assert set(second.snapshot.delta.reused_paths) == {
            "README.md",
            "unchanged.py",
        }

        full = RepositoryIndexer().build_manifest(
            root,
            repository_url="https://example.test/project-alpha.git",
            base_ref="main",
            base_sha=second_sha,
        )
        assert second.manifest == full
        assert service.search_project("project-alpha", "ALPHA_TOKEN_OLD") == ()
        assert service.search_project("project-alpha", "ALPHA_TOKEN_NEW")
        assert service.search_project("project-alpha", "DELETE_TOKEN") == ()
        renamed = service.search_project("project-alpha", "GUIDE_RENAME_TOKEN")
        assert [item.path for item in renamed] == ["docs/runbook.md"]
        assert service.search_project("project-alpha", "NEW_INDEX_TOKEN")
    finally:
        search.close()


def test_incremental_index_reuses_every_file_without_content_processing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, first_sha = _repository(tmp_path)
    _artifacts, search, service = _service(tmp_path / "state")
    try:
        first = _index(service, root, first_sha, None)
        _git(root, "commit", "--allow-empty", "-m", "metadata-only base")
        second_sha = _git(root, "rev-parse", "HEAD")

        def unexpected_content_read(*_args, **_kwargs):
            raise AssertionError("unchanged files must not be reprocessed")

        monkeypatch.setattr(service.indexer, "project_file", unexpected_content_read)
        second = _index(service, root, second_sha, first.snapshot_sha256)

        assert second.indexed_chunk_count == 0
        assert second.snapshot.delta.added_paths == ()
        assert second.snapshot.delta.modified_paths == ()
        assert second.snapshot.delta.deleted_paths == ()
        assert second.snapshot.delta.renamed_paths == ()
        assert len(second.snapshot.delta.reused_paths) == len(first.snapshot.files)
    finally:
        search.close()


def test_repository_index_survives_workspace_restart_and_replays_exact_base(
    tmp_path: Path,
) -> None:
    root, base_sha = _repository(tmp_path)
    workspace_root = tmp_path / "workspace"
    workspace = ProductWorkspace.create(workspace_root, FakeModelProvider({}))
    try:
        first = _index(workspace.repository_indexes, root, base_sha, None)
    finally:
        workspace.close()

    reopened = ProductWorkspace.create(workspace_root, FakeModelProvider({}))
    try:
        replay = _index(
            reopened.repository_indexes,
            root,
            base_sha,
            first.snapshot_sha256,
        )
        assert replay.replayed is True
        assert replay.snapshot_ref == first.snapshot_ref
        assert replay.snapshot_sha256 == first.snapshot_sha256
        assert reopened.repository_indexes.search_project("project-alpha", "UNCHANGED_TOKEN")
    finally:
        reopened.close()


def test_predecessor_hash_source_identity_artifact_and_worktree_drift_fail_closed(
    tmp_path: Path,
) -> None:
    root, base_sha = _repository(tmp_path)
    artifacts, search, service = _service(tmp_path / "state")
    try:
        first = _index(service, root, base_sha, None)
        with pytest.raises(RepositoryIndexError, match="expected predecessor"):
            _index(service, root, base_sha, "f" * 64)
        assert (
            search.repository_index_state(service.namespace("project-alpha")).snapshot_sha256
            == first.snapshot_sha256
        )

        _write(root, "app.py", "tracked drift\n")
        with pytest.raises(RepositoryIndexError, match="not clean"):
            _index(service, root, base_sha, first.snapshot_sha256)
        _git(root, "restore", "app.py")

        with pytest.raises(RepositoryIndexError, match="source identity"):
            service.index(
                project_id="project-alpha",
                root=root,
                repository_url="https://example.test/different.git",
                base_ref="main",
                base_sha=base_sha,
                expected_previous_snapshot_sha256=first.snapshot_sha256,
            )

        snapshot_path = artifacts.root / first.snapshot_ref.removeprefix("artifact://")
        snapshot_path.write_text("{}", encoding="utf-8")
        with pytest.raises(RepositoryIndexError, match="verification"):
            _index(service, root, base_sha, first.snapshot_sha256)
    finally:
        search.close()


def test_policy_drift_fails_closed_against_an_intact_active_snapshot(
    tmp_path: Path,
) -> None:
    root, base_sha = _repository(tmp_path)
    _artifacts, search, service = _service(tmp_path / "state")
    try:
        first = _index(service, root, base_sha, None)
    finally:
        search.close()

    _artifacts, changed_search, changed_policy = _service(tmp_path / "state", chunk_chars=2000)
    try:
        with pytest.raises(RepositoryIndexError, match="policy"):
            _index(changed_policy, root, base_sha, first.snapshot_sha256)
        state = changed_search.repository_index_state(changed_policy.namespace("project-alpha"))
        assert state is not None
        assert state.snapshot_sha256 == first.snapshot_sha256
    finally:
        changed_search.close()


def test_non_ancestor_base_fails_without_advancing_active_state(tmp_path: Path) -> None:
    root, first_sha = _repository(tmp_path)
    _artifacts, search, service = _service(tmp_path / "state")
    try:
        first = _index(service, root, first_sha, None)
        parent = _git(root, "rev-parse", f"{first_sha}^")
        _git(root, "switch", "-c", "divergent", parent)
        _write(root, "divergent.py", "DIVERGENT_TOKEN = True\n")
        divergent_sha = _commit(root, "divergent history")

        with pytest.raises(RepositoryIndexError, match="not an ancestor"):
            _index(service, root, divergent_sha, first.snapshot_sha256)
        state = search.repository_index_state(service.namespace("project-alpha"))
        assert state is not None
        assert state.snapshot_sha256 == first.snapshot_sha256
        assert state.base_sha == first_sha
    finally:
        search.close()


def test_repository_search_delta_rolls_back_atomically_and_can_retry(
    tmp_path: Path,
) -> None:
    root, first_sha = _repository(tmp_path)
    _artifacts, search, service = _service(tmp_path / "state")
    try:
        first = _index(service, root, first_sha, None)
        _write(root, "app.py", "def alpha():\n    return 'TRANSACTION_NEW_TOKEN'\n")
        second_sha = _commit(root, "transaction fixture")
        namespace = service.namespace("project-alpha")
        search.connection.execute(
            f"""
            CREATE TRIGGER reject_repository_delta
            BEFORE INSERT ON search_records
            WHEN NEW.namespace = '{namespace}' AND NEW.path = 'app.py'
            BEGIN
                SELECT RAISE(ABORT, 'injected repository-index failure');
            END
            """
        )
        search.connection.commit()

        with pytest.raises(RepositoryIndexError, match="transaction failed"):
            _index(service, root, second_sha, first.snapshot_sha256)

        state = search.repository_index_state(namespace)
        assert state is not None
        assert state.snapshot_sha256 == first.snapshot_sha256
        assert service.search_project("project-alpha", "ALPHA_TOKEN_OLD")
        assert service.search_project("project-alpha", "TRANSACTION_NEW_TOKEN") == ()

        search.connection.execute("DROP TRIGGER reject_repository_delta")
        search.connection.commit()
        retried = _index(service, root, second_sha, first.snapshot_sha256)
        assert retried.snapshot_sha256 != first.snapshot_sha256
        assert service.search_project("project-alpha", "ALPHA_TOKEN_OLD") == ()
        assert service.search_project("project-alpha", "TRANSACTION_NEW_TOKEN")
    finally:
        search.close()


def test_oversize_and_non_utf8_transitions_remove_stale_search_content(
    tmp_path: Path,
) -> None:
    root = tmp_path / "source"
    root.mkdir()
    _git(root, "init", "-b", "main")
    _git(root, "config", "user.email", "index@example.test")
    _git(root, "config", "user.name", "Index Test")
    _write(root, "visible.txt", "VISIBLE_SMALL_TOKEN\n")
    _write(root, "binary.txt", "BINARY_TEXT_TOKEN\n")
    _write(root, ".env", "HIDDEN_SECRET_TOKEN=1\n")
    first_sha = _commit(root, "small file")
    _artifacts, search, service = _service(
        tmp_path / "state",
        max_file_bytes=32,
    )
    try:
        first = _index(service, root, first_sha, None)
        assert service.search_project("project-alpha", "VISIBLE_SMALL_TOKEN")
        assert service.search_project("project-alpha", "BINARY_TEXT_TOKEN")
        assert service.search_project("project-alpha", "HIDDEN_SECRET_TOKEN") == ()

        _write(root, "visible.txt", "X" * 64)
        (root / "binary.txt").write_bytes(b"\xff\xfe\x00")
        second_sha = _commit(root, "oversize file")
        second = _index(service, root, second_sha, first.snapshot_sha256)
        assert second.snapshot.delta.deleted_paths == ("visible.txt",)
        assert second.snapshot.delta.modified_paths == ("binary.txt",)
        assert service.search_project("project-alpha", "VISIBLE_SMALL_TOKEN") == ()
        assert service.search_project("project-alpha", "BINARY_TEXT_TOKEN") == ()

        (root / "visible.txt").write_bytes(b"\xff\xfe\x00")
        third_sha = _commit(root, "non utf8 file")
        third = _index(service, root, third_sha, second.snapshot_sha256)
        assert third.snapshot.delta.added_paths == ("visible.txt",)
        assert "visible.txt" in {item.path for item in third.snapshot.files}
        assert service.search_project("project-alpha", "VISIBLE_SMALL_TOKEN") == ()
    finally:
        search.close()


def test_deny_policy_transitions_remove_and_add_only_currently_eligible_content(
    tmp_path: Path,
) -> None:
    root = tmp_path / "source"
    root.mkdir()
    _git(root, "init", "-b", "main")
    _git(root, "config", "user.email", "index@example.test")
    _git(root, "config", "user.name", "Index Test")
    _write(root, "visible.txt", "VISIBLE_BEFORE_DENY_TOKEN\n")
    _write(root, ".env", "HIDDEN_BEFORE_REVEAL_TOKEN=1\n")
    first_sha = _commit(root, "deny transition fixture")
    _artifacts, search, service = _service(tmp_path / "state")
    try:
        first = _index(service, root, first_sha, None)
        assert service.search_project("project-alpha", "VISIBLE_BEFORE_DENY_TOKEN")
        assert service.search_project("project-alpha", "HIDDEN_BEFORE_REVEAL_TOKEN") == ()

        _git(root, "mv", "visible.txt", "secret.key")
        _git(root, "mv", ".env", "revealed.txt")
        second_sha = _commit(root, "cross deny boundary")
        second = _index(service, root, second_sha, first.snapshot_sha256)

        assert second.snapshot.delta.added_paths == ("revealed.txt",)
        assert second.snapshot.delta.deleted_paths == ("visible.txt",)
        assert second.snapshot.delta.renamed_paths == ()
        assert service.search_project("project-alpha", "VISIBLE_BEFORE_DENY_TOKEN") == ()
        assert service.search_project("project-alpha", "HIDDEN_BEFORE_REVEAL_TOKEN")
    finally:
        search.close()


def test_snapshot_byte_limit_fails_before_active_index_creation(tmp_path: Path) -> None:
    root, base_sha = _repository(tmp_path)
    _artifacts, search, service = _service(
        tmp_path / "state",
        snapshot_max_bytes=100,
    )
    try:
        with pytest.raises(RepositoryIndexError, match="byte limit"):
            _index(service, root, base_sha, None)
        assert search.repository_index_state(service.namespace("project-alpha")) is None
        assert service.search_project("project-alpha", "ALPHA_TOKEN_OLD") == ()
    finally:
        search.close()
