from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command

from universal_coding_agent.context.compiler import ContextCompiler
from universal_coding_agent.core.models import TaskRequest
from universal_coding_agent.orchestration.graph import GraphServices, ObserveGraph
from universal_coding_agent.providers.base import ModelProvider
from universal_coding_agent.repository.indexer import RepositoryIndexer
from universal_coding_agent.sandbox.git import GitSandboxManager
from universal_coding_agent.storage.artifacts import ArtifactStore


@dataclass
class AgentService:
    graph: Any
    connection: sqlite3.Connection
    artifacts: ArtifactStore

    @classmethod
    def create(cls, state_root: Path, provider: ModelProvider) -> "AgentService":
        state_root = state_root.resolve()
        os.environ.setdefault("LANGGRAPH_STRICT_MSGPACK", "true")
        state_root.mkdir(parents=True, exist_ok=True)
        artifacts = ArtifactStore(state_root / "artifacts")
        services = GraphServices(
            provider=provider,
            sandbox=GitSandboxManager(state_root),
            indexer=RepositoryIndexer(),
            context=ContextCompiler(),
            artifacts=artifacts,
        )
        connection = sqlite3.connect(state_root / "checkpoints.sqlite", check_same_thread=False)
        checkpointer = SqliteSaver(connection)
        graph = ObserveGraph(services).build(checkpointer=checkpointer)
        return cls(graph=graph, connection=connection, artifacts=artifacts)

    def close(self) -> None:
        self.connection.close()

    def run(self, task: TaskRequest) -> dict[str, Any]:
        config = {"configurable": {"thread_id": task.thread_id}}
        return self.graph.invoke({"task": task.model_dump(mode="json")}, config=config)

    def resume(self, thread_id: str, approved: bool) -> dict[str, Any]:
        config = {"configurable": {"thread_id": thread_id}}
        return self.graph.invoke(Command(resume={"approved": approved}), config=config)

    def state(self, thread_id: str) -> dict[str, Any]:
        config = {"configurable": {"thread_id": thread_id}}
        snapshot = self.graph.get_state(config)
        return {
            "values": snapshot.values,
            "next": list(snapshot.next),
            "metadata": snapshot.metadata,
            "created_at": snapshot.created_at,
        }
