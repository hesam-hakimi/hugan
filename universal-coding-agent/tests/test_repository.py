import subprocess
from pathlib import Path

from universal_coding_agent.core.models import RepositorySpec
from universal_coding_agent.repository.indexer import RepositoryIndexer
from universal_coding_agent.sandbox.git import GitSandboxManager


def _run(*args: str, cwd: Path) -> None:
    subprocess.run(args, cwd=cwd, check=True, capture_output=True)


def test_indexer_excludes_secrets_and_extracts_python_symbols(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _run("git", "init", cwd=repo)
    _run("git", "config", "user.email", "test@example.test", cwd=repo)
    _run("git", "config", "user.name", "Test", cwd=repo)
    (repo / "app.py").write_text(
        "import json\n\ndef hello():\n    return json.dumps({})\n",
        encoding="utf-8",
    )
    (repo / ".env").write_text("SECRET=never-read", encoding="utf-8")
    _run("git", "add", "app.py", ".env", cwd=repo)
    _run("git", "commit", "-m", "fixture", cwd=repo)
    sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip()
    manifest = RepositoryIndexer().build_manifest(
        repo, repository_url=str(repo), base_ref="main", base_sha=sha
    )
    assert [item.path for item in manifest.files] == ["app.py"]
    assert any("hello" in symbol for symbol in manifest.files[0].symbols)


def test_sandbox_clones_local_fixture_without_touching_source(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    _run("git", "init", "-b", "main", cwd=source)
    _run("git", "config", "user.email", "test@example.test", cwd=source)
    _run("git", "config", "user.name", "Test", cwd=source)
    (source / "README.md").write_text("fixture\n", encoding="utf-8")
    _run("git", "add", "README.md", cwd=source)
    _run("git", "commit", "-m", "fixture", cwd=source)
    manager = GitSandboxManager(tmp_path / "state", allow_local_sources=True)
    info = manager.prepare(
        "task-123",
        repository=RepositorySpec(url=str(source), base_ref="main"),
    )
    assert info.clean
    assert Path(info.path).is_dir()
    assert (
        subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=source,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        == ""
    )
