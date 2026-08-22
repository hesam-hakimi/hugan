from __future__ import annotations

from typing import Any

from langgraph.types import interrupt

from universal_coding_agent.core.models import TaskStatus
from universal_coding_agent.core.safe_models import SafeTaskRequest
from universal_coding_agent.orchestration.safe_graph import SafeGraphState, SafeModeGraph
from universal_coding_agent.orchestration.safe_graph_v2_sharded import (
    ShardedLineAddressedSafeModeGraph,
)
from universal_coding_agent.product.models import ControlAction
from universal_coding_agent.product.task_control import TaskControlService


class _ControlledSafeMixin:
    def __init__(self, services: Any, control: TaskControlService) -> None:
        super().__init__(services)
        self.control = control

    def _control_gate(self, state: SafeGraphState, stage: str) -> dict[str, Any] | None:
        task = SafeTaskRequest.model_validate(state["task"])
        decision = self.control.task_action(task.task_id)
        if decision is ControlAction.CANCEL:
            return {
                "status": TaskStatus.BLOCKED.value,
                "safe_errors": ["control:cancelled"],
                "events": [self._event("control", f"cancelled before {stage}")],
            }
        if decision is not ControlAction.PAUSE:
            return None

        resume_value = interrupt(
            {
                "type": "task_control_pause",
                "task_id": task.task_id,
                "thread_id": task.thread_id,
                "stage": stage,
                "action_required": "resume_or_cancel",
            }
        )
        requested_action = (
            str(resume_value.get("action", "resume")).strip().lower()
            if isinstance(resume_value, dict)
            else "resume"
        )
        if requested_action == "cancel":
            self.control.cancel_task(task.task_id, reason="cancelled while paused")
            self.control.task_action(task.task_id)
            return {
                "status": TaskStatus.BLOCKED.value,
                "safe_errors": ["control:cancelled"],
                "events": [self._event("control", f"cancelled while paused before {stage}")],
            }
        self.control.resume_task(task.task_id)
        return None

    def prepare_sandbox(self, state: SafeGraphState) -> dict[str, Any]:
        gate = self._control_gate(state, "sandbox")
        return gate if gate is not None else super().prepare_sandbox(state)

    def implement(self, state: SafeGraphState) -> dict[str, Any]:
        gate = self._control_gate(state, "implement")
        return gate if gate is not None else super().implement(state)

    def apply_edits(self, state: SafeGraphState) -> dict[str, Any]:
        gate = self._control_gate(state, "apply_edits")
        return gate if gate is not None else super().apply_edits(state)

    def validate_patch(self, state: SafeGraphState) -> dict[str, Any]:
        gate = self._control_gate(state, "validate_patch")
        return gate if gate is not None else super().validate_patch(state)

    def run_tests(self, state: SafeGraphState) -> dict[str, Any]:
        gate = self._control_gate(state, "tests")
        return gate if gate is not None else super().run_tests(state)

    def review(self, state: SafeGraphState) -> dict[str, Any]:
        gate = self._control_gate(state, "review")
        return gate if gate is not None else super().review(state)

    def finalize(self, state: SafeGraphState) -> dict[str, Any]:
        task = SafeTaskRequest.model_validate(state["task"])
        decision = self.control.task_action(task.task_id)
        controlled_state: SafeGraphState = dict(state)
        if decision is ControlAction.PAUSE:
            resume_value = interrupt(
                {
                    "type": "task_control_pause",
                    "task_id": task.task_id,
                    "thread_id": task.thread_id,
                    "stage": "finalize",
                    "action_required": "resume_or_cancel",
                }
            )
            requested_action = (
                str(resume_value.get("action", "resume")).strip().lower()
                if isinstance(resume_value, dict)
                else "resume"
            )
            if requested_action == "cancel":
                self.control.cancel_task(task.task_id, reason="cancelled while paused")
                self.control.task_action(task.task_id)
                controlled_state["safe_errors"] = [
                    *state.get("safe_errors", []),
                    "control:cancelled",
                ]
            else:
                self.control.resume_task(task.task_id)
        elif decision is ControlAction.CANCEL:
            controlled_state["safe_errors"] = [
                *state.get("safe_errors", []),
                "control:cancelled",
            ]

        result = super().finalize(controlled_state)
        if result.get("status") == TaskStatus.COMPLETED.value:
            self.control.complete_task(task.task_id)
        return result


class ControlledSafeModeGraph(_ControlledSafeMixin, SafeModeGraph):
    pass


class ControlledShardedLineAddressedSafeModeGraph(
    _ControlledSafeMixin,
    ShardedLineAddressedSafeModeGraph,
):
    pass
