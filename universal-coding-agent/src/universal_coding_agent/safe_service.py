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
from universal_coding_agent.core.safe_models import SafeTaskRequest
from universal_coding_agent.orchestration.safe_graph import SafeGraphServices
from universal_coding_agent.product.controlled_safe_graph import (
    ControlledSafeModeGraph,
    ControlledShardedLineAddressedSafeModeGraph,
)
from universal_coding_agent.product.remote_operations import (
    SqliteRemoteOperationLeaseStore,
)
from universal_coding_agent.product.task_control import TaskControlService
from universal_coding_agent.providers.base import (
    ModelProvider,
    RemoteOperationLeaseAwareProvider,
)
from universal_coding_agent.repository.indexer import RepositoryIndexer
from universal_coding_agent.safe.model_line_addressing import (
    ModelFacingLineAddressedEditEngine,
)
from universal_coding_agent.safe.patching import SafeEditEngine, SafePatchEngine
from universal_coding_agent.safe.testing import SafeTestRunner
from universal_coding_agent.sandbox.git import GitSandboxManager
from universal_coding_agent.storage.artifacts import ArtifactStore


@dataclass
class SafeAgentService:
    graph: Any
    connection: sqlite3.Connection
    artifacts: ArtifactStore
    control: TaskControlService
    remote_operations: SqliteRemoteOperationLeaseStore
    owns_control: bool = False
    owns_remote_operations: bool = False

    @classmethod
    def create(
        cls,
        state_root: Path,
        provider: ModelProvider,
        *,
        allow_local_sources: bool = False,
        control: TaskControlService | None = None,
        remote_operations: SqliteRemoteOperationLeaseStore | None = None,
    ) -> SafeAgentService:
        state_root = state_root.resolve()
        os.environ.setdefault("LANGGRAPH_STRICT_MSGPACK", "true")
        state_root.mkdir(parents=True, exist_ok=True)
        artifacts = ArtifactStore(state_root / "artifacts")
        owns_control = control is None
        control_service = control or TaskControlService(state_root / "task-control.sqlite")
        owns_remote_operations = remote_operations is None
        remote_operation_store = remote_operations or SqliteRemoteOperationLeaseStore(
            state_root / "private-remote-operations.sqlite"
        )
        if isinstance(provider, RemoteOperationLeaseAwareProvider):
            provider.bind_remote_operation_store(remote_operation_store)

        protocol = os.environ.get("UCA_SAFE_EDIT_PROTOCOL", "v1").strip().lower()
        if protocol in {"v2", "v2-line-addressed", "line-addressed"}:
            context = ShardedLineAddressedContextCompiler()
            edit_engine = ModelFacingLineAddressedEditEngine()
            graph_type = ControlledShardedLineAddressedSafeModeGraph
        elif protocol == "v1":
            context = SafeContextCompiler()
            edit_engine = SafeEditEngine()
            graph_type = ControlledSafeModeGraph
        else:
            if owns_control:
                control_service.close()
            if owns_remote_operations:
                remote_operation_store.close()
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
            cancellation=control_service.cancellation,
        )
        connection = sqlite3.connect(
            state_root / "safe-checkpoints.sqlite",
            check_same_thread=False,
        )
        graph = graph_type(services, control_service).build(
            checkpointer=SqliteSaver(connection)
        )
        return cls(
            graph=graph,
            connection=connection,
            artifacts=artifacts,
            control=control_service,
            remote_operations=remote_operation_store,
            owns_control=owns_control,
            owns_remote_operations=owns_remote_operations,
        )

    def close(self) -> None:
        self.connection.close()
        if self.owns_control:
            self.control.close()
        if self.owns_remote_operations:
            self.remote_operations.close()

    def run(self, task: SafeTaskRequest) -> dict[str, Any]:
        self.control.ensure_task(task.task_id)
        config = {"configurable": {"thread_id": task.thread_id}}
        return self.graph.invoke({"task": task.model_dump(mode="json")}, config=config)

    def resume(self, thread_id: str, approved: bool) -> dict[str, Any]:
        config = {"configurable": {"thread_id": thread_id}}
        return self.graph.invoke(Command(resume={"approved": approved}), config=config)

    def pause(self, thread_id: str, *, reason: str = "") -> dict[str, Any]:
        task_id = self._task_id(thread_id)
        return self.control.pause_task(task_id, reason=reason).model_dump(mode="json")

    def cancel(self, thread_id: str, *, reason: str = "") -> dict[str, Any]:
        task_id = self._task_id(thread_id)
        record = self.control.cancel_task(task_id, reason=reason)
        report = self.control.cancellation_report(task_id)
        payload = record.model_dump(mode="json")
        payload["cancellation_report"] = report.to_json() if report is not None else None
        return payload

    def resume_control(self, thread_id: str, *, action: str = "resume") -> dict[str, Any]:
        normalized = action.strip().lower()
        if normalized not in {"resume", "cancel"}:
            raise ValueError("control action must be resume or cancel")
        config = {"configurable": {"thread_id": thread_id}}
        return self.graph.invoke(Command(resume={"action": normalized}), config=config)

    def state(self, thread_id: str) -> dict[str, Any]:
        config = {"configurable": {"thread_id": thread_id}}
        snapshot = self.graph.get_state(config)
        values = snapshot.values
        task_id = None
        task_payload = values.get("task") if isinstance(values, dict) else None
        if isinstance(task_payload, dict):
            task_id = task_payload.get("task_id")
        record = self.control.get_task(task_id) if isinstance(task_id, str) else None
        control = record.model_dump(mode="json") if record is not None else None
        cancellation = (
            self.control.cancellation_report(task_id)
            if isinstance(task_id, str)
            else None
        )
        return {
            "values": values,
            "next": list(snapshot.next),
            "metadata": snapshot.metadata,
            "created_at": snapshot.created_at,
            "control": control,
            "cancellation_report": (
                cancellation.to_json() if cancellation is not None else None
            ),
        }

    def _task_id(self, thread_id: str) -> str:
        snapshot = self.state(thread_id)
        task_payload = snapshot["values"].get("task")
        if not isinstance(task_payload, dict) or not isinstance(
            task_payload.get("task_id"), str
        ):
            raise KeyError(f"task not found for thread: {thread_id}")
        return task_payload["task_id"]
