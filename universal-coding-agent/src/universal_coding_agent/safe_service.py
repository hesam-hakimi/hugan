from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command

from universal_coding_agent.context.safe_compiler import SafeContextCompiler
from universal_coding_agent.context.sharded_line_edit_compiler import (
    ShardedLineAddressedContextCompiler,
)
from universal_coding_agent.orchestration.safe_graph import SafeGraphServices, SafeModeGraph
from universal_coding_agent.orchestration.safe_graph_v2_sharded import (
    ShardedLineAddressedSafeModeGraph,
)
from universal_coding_agent.providers.base import ModelProvider
from universal_coding_agent.repository.indexer import RepositoryIndexer
from universal_coding_agent.safe.line_editing import LineAddressedEditEngine
from universal_coding_agent.safe.patching import SafeEditEngine, SafePatchEngine
from universal_coding_agent.safe.testing import SafeTestRunner
from universal_coding_agent.sandbox.git import GitSandboxManager
from universal_coding_agent.storage.artifacts import ArtifactStore


@dataclass
class SafeAgentService:
    graph: Any
    connection: sqlite3.Connection
    artifacts: ArtifactStore

    @classmethod
    def create(
        cls,
        state_root: Path,
        provider: ModelProvider,
        *,
        allow_local_sources: bool = False,
    ) -> SafeAgentService:
        state_root = state_root.resolve()
        os.environ.setdefault("LANGGRAPH_STRICT_MSGPACK", "true")
        state_root.mkdir(parents=True, exist_ok=True)
        artifacts = ArtifactStore(state_root / "artifacts")

        protocol = os.environ.get("UCA_SAFE_EDIT_PROTOCOL", "v1").strip().lower()
        if protocol in {"v2", "v2-line-addressed", "line-addressed"}:
            context = ShardedLineAddressedContextCompiler()
            edit_engine = LineAddressedEditEngine()
            graph_type = ShardedLineAddressedSafeModeGraph
        elif protocol == "v1":
            context = SafeContextCompiler()
            edit_engine = SafeEditEngine()
            graph_type = SafeModeGraph
        else:
            raise ValueError(
                "UCA_SAFE_EDIT_PROTOCOL must be v1 or v2-line-addressed"
            )

        services = SafeGraphServices(
            provider=provider,
            sandbox=GitSandboxManager(
                state_root,
                allow_local_sources=allow_local_sources,
            ),
            indexer=RepositoryIndexer(),
            context=context,
            artifacts=artifacts,
            edit_engine=edit_engine,
            patch_engine=SafePatchEngine(),
            test_runner=SafeTestRunner(),
        )
        connection = sqlite3.connect(
            state_root / "safe-checkpoints.sqlite",
            check_same_thread=False,
        )
        graph = graph_type(services).build(checkpointer=SqliteSaver(connection))
        return cls(graph=graph, connection=connection, artifacts=artifacts)

    def close(self) -> None:
        self.connection.close()

    def run(self, task) -> dict[str, Any]:
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
