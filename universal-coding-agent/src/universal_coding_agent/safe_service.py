from __future__ import annotations

import os
import re
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
    execution_adapter: Any = None

    @classmethod
    def create(
        cls,
        state_root: Path,
        provider: ModelProvider,
        *,
        allow_local_sources: bool = False,
        control: TaskControlService | None = None,
        remote_operations: SqliteRemoteOperationLeaseStore | None = None,
        test_runner: SafeTestRunner | None = None,
        execution_adapter: Any = None,
    ) -> SafeAgentService:
        state_root = state_root.resolve()
        os.environ.setdefault("LANGGRAPH_STRICT_MSGPACK", "true")
        state_root.mkdir(parents=True, exist_ok=True)
        selected_test_runner = test_runner or SafeTestRunner.from_environment()
        artifacts = ArtifactStore(state_root / "artifacts")
        owns_control = control is None
        control_service = control or TaskControlService(state_root / "task-control.sqlite")
        owns_remote_operations = remote_operations is None
        remote_operation_store = remote_operations or SqliteRemoteOperationLeaseStore(
            state_root / "private-remote-operations.sqlite"
        )
        if isinstance(provider, RemoteOperationLeaseAwareProvider):
            provider.bind_remote_operation_store(remote_operation_store.provider_store())

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
            test_runner=selected_test_runner,
            cancellation=control_service.cancellation,
        )
        if execution_adapter is not None:
            from universal_coding_agent.product.program_continuation_execution_adapter import (
                ContinuationSafeExecution,
            )
            from universal_coding_agent.product.program_source_dispatch import AdmittedSafeExecution
            if type(execution_adapter) not in {AdmittedSafeExecution, ContinuationSafeExecution}:
                raise ValueError("Safe execution requires an exact stored admission adapter")
            services = execution_adapter.bind_services(services, state_root, protocol)
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
            execution_adapter=execution_adapter,
        )

    def close(self) -> None:
        self.connection.close()
        if self.owns_control:
            self.control.close()
        if self.owns_remote_operations:
            self.remote_operations.close()

    def run(self, task: SafeTaskRequest) -> dict[str, Any]:
        self._execution_gate(task.thread_id, task.task_id, action="run",
                             execution_schema=task.metadata.get("execution_schema"))
        self.control.ensure_task(task.task_id)
        config = {"configurable": {"thread_id": task.thread_id}}
        return self.graph.invoke({"task": task.model_dump(mode="json")}, config=config)

    def _execution_gate(self, thread_id: str, task_id: str | None = None, *, action="run",
                        execution_schema=None) -> None:
        self.verify_source_dispatch_control()
        from universal_coding_agent.product.program_continuation_execution_adapter import (
            ContinuationSafeExecution,
        )
        from universal_coding_agent.product.program_source_routing import safe_v3_route
        with self.control._lock:
            row = self.control.connection.execute("""SELECT task_id FROM uca_source_dispatch_tasks
                WHERE thread_id = ? OR task_id = ?""", (thread_id, task_id or "")).fetchone()
            v3 = safe_v3_route(self, thread_id, task_id)
            v3 |= execution_schema == "uca-program-source-dispatch-3"
        if v3 or type(self.execution_adapter) is ContinuationSafeExecution:
            if (
                not v3 or row is not None
                or type(self.execution_adapter) is not ContinuationSafeExecution
            ):
                raise ValueError("source-aware task requires explicit v3 continuation API")
            self.execution_adapter.entry(thread_id, task_id, action)
            return
        if row is not None or self.execution_adapter is not None:
            if self.execution_adapter is None:
                raise ValueError("source-aware task requires explicit v2 execution API")
            self.execution_adapter.entry(thread_id, task_id)

    def _source_dispatch_control_identity(self) -> tuple[str, int, int]:
        with self.control._lock:
            filename = self.control.connection.execute("PRAGMA database_list").fetchone()[2]
        if not filename:
            raise ValueError("source-aware execution requires a durable control database")
        path = Path(filename).resolve(strict=True)
        info = path.stat()
        return str(path), info.st_dev, info.st_ino

    def bind_source_dispatch_control(self) -> None:
        """Pin the checkpoint root before admission, in a separate durable transaction.

        This host binding is not an admission. Program/control remain the only databases
        written atomically when an admission or result is committed.
        """
        identity = self._source_dispatch_control_identity()
        with self.connection:
            self.connection.execute("""CREATE TABLE IF NOT EXISTS uca_source_dispatch_control (
                singleton INTEGER PRIMARY KEY CHECK(singleton = 1),
                control_path TEXT NOT NULL, control_device INTEGER NOT NULL,
                control_inode INTEGER NOT NULL)""")
            self.connection.execute(
                "INSERT OR IGNORE INTO uca_source_dispatch_control VALUES (1, ?, ?, ?)", identity
            )
            self.verify_source_dispatch_control(required=True)

    def verify_source_dispatch_control(self, *, required: bool = False) -> None:
        present = self.connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' "
            "AND name = 'uca_source_dispatch_control'"
        ).fetchone()
        if present is None:
            if required:
                raise ValueError("source-aware checkpoint control binding is missing")
            return
        row = self.connection.execute(
            "SELECT control_path, control_device, control_inode "
            "FROM uca_source_dispatch_control WHERE singleton = 1"
        ).fetchone()
        if row is None or tuple(row) != self._source_dispatch_control_identity():
            raise ValueError("source-aware checkpoint root requires its bound control database")

    def resume(self, thread_id: str, approved: bool) -> dict[str, Any]:
        self._execution_gate(thread_id, action="resume")
        config = {"configurable": {"thread_id": thread_id}}
        return self.graph.invoke(Command(resume={"approved": approved}), config=config)

    def resume_publish(
        self,
        thread_id: str,
        *,
        approved: bool,
        patch_sha256: str,
    ) -> dict[str, Any]:
        self._execution_gate(thread_id, action="publish")
        normalized_hash = patch_sha256.strip().lower()
        if re.fullmatch(r"[0-9a-f]{64}", normalized_hash) is None:
            raise ValueError("publish approval requires an exact SHA-256 patch hash")
        snapshot = self.state(thread_id)
        if snapshot["next"] != ["publish_approval"]:
            raise RuntimeError("task is not awaiting publish approval")
        config = {"configurable": {"thread_id": thread_id}}
        return self.graph.invoke(
            Command(
                resume={
                    "approved": approved,
                    "patch_sha256": normalized_hash,
                }
            ),
            config=config,
        )

    def pause(self, thread_id: str, *, reason: str = "") -> dict[str, Any]:
        self.verify_source_dispatch_control()
        task_id = self._task_id(thread_id)
        return self.control.pause_task(task_id, reason=reason).model_dump(mode="json")

    def cancel(self, thread_id: str, *, reason: str = "") -> dict[str, Any]:
        self.verify_source_dispatch_control()
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
        self._execution_gate(thread_id, action="control")
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
