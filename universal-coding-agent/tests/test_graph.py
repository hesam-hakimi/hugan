import sqlite3
import subprocess
from pathlib import Path
from typing import Any

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command

from universal_coding_agent.context.compiler import ContextCompiler
from universal_coding_agent.core.models import RepositorySpec, TaskRequest
from universal_coding_agent.orchestration.graph import GraphServices, ObserveGraph
from universal_coding_agent.providers.fake import FakeModelProvider
from universal_coding_agent.repository.indexer import RepositoryIndexer
from universal_coding_agent.sandbox.git import GitSandboxManager
from universal_coding_agent.storage.artifacts import ArtifactStore


def _git(*args: str, cwd: Path) -> None:
    subprocess.run(args, cwd=cwd, check=True, capture_output=True)


def _source_repository(tmp_path: Path) -> Path:
    source = tmp_path / "source"
    source.mkdir()
    _git("git", "init", "-b", "main", cwd=source)
    _git("git", "config", "user.email", "test@example.test", cwd=source)
    _git("git", "config", "user.name", "Test", cwd=source)
    (source / "AGENTS.md").write_text("Read-only qualification.\n", encoding="utf-8")
    (source / "app.py").write_text("def answer():\n    return 42\n", encoding="utf-8")
    (source / "test_app.py").write_text(
        "def test_answer():\n    assert True\n",
        encoding="utf-8",
    )
    _git("git", "add", ".", cwd=source)
    _git("git", "commit", "-m", "fixture", cwd=source)
    return source


def _graph(
    tmp_path: Path,
    provider: FakeModelProvider,
) -> tuple[Any, sqlite3.Connection, ArtifactStore]:
    state_root = tmp_path / "state"
    artifacts = ArtifactStore(state_root / "artifacts")
    services = GraphServices(
        provider=provider,
        sandbox=GitSandboxManager(state_root, allow_local_sources=True),
        indexer=RepositoryIndexer(),
        context=ContextCompiler(),
        artifacts=artifacts,
    )
    connection = sqlite3.connect(state_root / "checkpoints.sqlite", check_same_thread=False)
    graph = ObserveGraph(services).build(checkpointer=SqliteSaver(connection))
    return graph, connection, artifacts


def test_observe_graph_pauses_and_resumes_without_source_changes(tmp_path: Path) -> None:
    source = _source_repository(tmp_path)
    graph, connection, _ = _graph(tmp_path, FakeModelProvider())
    task = TaskRequest(
        task_id="task-graph-123",
        thread_id="thread-graph-123",
        title="qualify",
        objective="Inspect the project and build a phased plan.",
        repository=RepositorySpec(url=str(source), base_ref="main"),
        require_plan_approval=True,
    )
    config = {"configurable": {"thread_id": task.thread_id}}
    first = graph.invoke({"task": task.model_dump(mode="json")}, config=config)
    assert first["status"] == "awaiting_plan_approval"
    snapshot = graph.get_state(config)
    assert snapshot.next == ("approval",)

    final = graph.invoke(Command(resume={"approved": True}), config=config)
    assert final["status"] == "completed"
    assert final["reviewer_verdict"] == "PASS"
    assert final["final_report_ref"].startswith("artifact://")
    source_status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=source,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    assert source_status == ""
    connection.close()


def test_observe_graph_repairs_invalid_planner_dependency(tmp_path: Path) -> None:
    source = _source_repository(tmp_path)

    def planner(request) -> dict[str, object]:
        if request.metadata.get("schema_repair") == "true":
            return {
                "phase_id": "P2C",
                "title": "Phase 2C",
                "objective": "Remediate schema validation.",
                "slices": [
                    {
                        "slice_id": "S1",
                        "title": "Schema validation",
                        "objective": "Validate schema membership.",
                        "dependencies": [],
                        "external_dependencies": [
                            "Phase 2B canonical schema specification"
                        ],
                    }
                ],
            }
        return {
            "phase_id": "P2C",
            "title": "Phase 2C",
            "objective": "Remediate schema validation.",
            "slices": [
                {
                    "slice_id": "S1",
                    "title": "Schema validation",
                    "objective": "Validate schema membership.",
                    "dependencies": ["Phase 2B canonical schema specification"],
                }
            ],
        }

    graph, connection, artifacts = _graph(
        tmp_path,
        FakeModelProvider(handlers={"planner": planner}),
    )
    task = TaskRequest(
        task_id="task-repair-123",
        thread_id="thread-repair-123",
        title="qualify",
        objective="Inspect Phase 2C and build a phased plan.",
        repository=RepositorySpec(url=str(source), base_ref="main"),
    )
    config = {"configurable": {"thread_id": task.thread_id}}
    final = graph.invoke({"task": task.model_dump(mode="json")}, config=config)

    assert final["status"] == "completed"
    validation = artifacts.read_json(final["planner_validation_ref"])
    assert validation["repair_used"] is True
    plan = artifacts.read_json(final["plan_ref"])
    assert plan["slices"][0]["dependencies"] == []
    assert plan["slices"][0]["external_dependencies"] == [
        "Phase 2B canonical schema specification"
    ]
    connection.close()
