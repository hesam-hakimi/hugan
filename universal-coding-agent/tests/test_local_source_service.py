import subprocess
from pathlib import Path

from universal_coding_agent.core.models import RepositorySpec, TaskRequest
from universal_coding_agent.providers.fake import FakeModelProvider
from universal_coding_agent.service import AgentService


def _git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def test_agent_service_can_explicitly_use_local_source(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    _git(source, "init", "-b", "main")
    _git(source, "config", "user.email", "test@example.invalid")
    _git(source, "config", "user.name", "Test")
    (source / "README.md").write_text("# fixture\n", encoding="utf-8")
    (source / "app.py").write_text("def answer():\n    return 42\n", encoding="utf-8")
    _git(source, "add", "README.md", "app.py")
    _git(source, "commit", "-m", "fixture")

    task = TaskRequest(
        task_id="local-source-task",
        thread_id="local-source-thread",
        title="local source smoke",
        objective="Inspect the repository and produce a read-only plan.",
        repository=RepositorySpec(url=str(source), base_ref="main"),
    )

    service = AgentService.create(
        tmp_path / "state",
        FakeModelProvider(),
        allow_local_sources=True,
    )
    try:
        result = service.run(task)
        report = service.artifacts.read_json(result["final_report_ref"])
    finally:
        service.close()

    assert result["status"] == "completed"
    assert result["reviewer_verdict"] == "PASS"
    assert report["status"] == "completed"
    assert report["source_changes"] == []
    assert report["commit_push_pr_merge_deploy"] is False
    assert _git(source, "status", "--porcelain") == ""
