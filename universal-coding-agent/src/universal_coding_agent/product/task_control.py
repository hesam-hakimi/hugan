from __future__ import annotations

import sqlite3
from pathlib import Path

from universal_coding_agent.product.models import (
    ControlAction,
    ControlDecision,
    ControlEntityType,
    ControlRecord,
    ControlState,
)


class TaskControlService:
    """Persistent cooperative pause/resume/cancel state.

    Callers check at safe boundaries. Pause stops new work at the next boundary; cancel is
    terminal once observed. The record is independent of any UI or transport.
    """

    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path.resolve()
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.database_path, check_same_thread=False)
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS control_state (
                entity_type TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                state TEXT NOT NULL,
                reason TEXT NOT NULL,
                revision INTEGER NOT NULL,
                PRIMARY KEY (entity_type, entity_id)
            )
            """
        )
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()

    def ensure(
        self,
        entity_type: ControlEntityType,
        entity_id: str,
    ) -> ControlRecord:
        current = self.get(entity_type, entity_id)
        if current is not None:
            return current
        self.connection.execute(
            """
            INSERT INTO control_state(entity_type, entity_id, state, reason, revision)
            VALUES (?, ?, ?, '', 0)
            """,
            (entity_type.value, entity_id, ControlState.RUNNING.value),
        )
        self.connection.commit()
        return self.get_required(entity_type, entity_id)

    def get(
        self,
        entity_type: ControlEntityType,
        entity_id: str,
    ) -> ControlRecord | None:
        row = self.connection.execute(
            """
            SELECT state, reason, revision FROM control_state
            WHERE entity_type = ? AND entity_id = ?
            """,
            (entity_type.value, entity_id),
        ).fetchone()
        if row is None:
            return None
        return ControlRecord(
            entity_type=entity_type,
            entity_id=entity_id,
            state=ControlState(row[0]),
            reason=row[1],
            revision=row[2],
        )

    def get_required(
        self,
        entity_type: ControlEntityType,
        entity_id: str,
    ) -> ControlRecord:
        record = self.get(entity_type, entity_id)
        if record is None:
            raise KeyError(entity_id)
        return record

    def request_pause(
        self,
        entity_type: ControlEntityType,
        entity_id: str,
        *,
        reason: str = "",
    ) -> ControlRecord:
        record = self.ensure(entity_type, entity_id)
        if record.state in {ControlState.CANCELLED, ControlState.COMPLETED}:
            raise ValueError("terminal work cannot be paused")
        if record.state is ControlState.CANCEL_REQUESTED:
            return record
        return self._set(entity_type, entity_id, ControlState.PAUSE_REQUESTED, reason)

    def resume(
        self,
        entity_type: ControlEntityType,
        entity_id: str,
    ) -> ControlRecord:
        record = self.ensure(entity_type, entity_id)
        if record.state not in {ControlState.PAUSED, ControlState.PAUSE_REQUESTED}:
            raise ValueError("only paused work can be resumed")
        return self._set(entity_type, entity_id, ControlState.RUNNING, "")

    def request_cancel(
        self,
        entity_type: ControlEntityType,
        entity_id: str,
        *,
        reason: str = "",
    ) -> ControlRecord:
        record = self.ensure(entity_type, entity_id)
        if record.state in {ControlState.CANCELLED, ControlState.COMPLETED}:
            return record
        return self._set(entity_type, entity_id, ControlState.CANCEL_REQUESTED, reason)

    def checkpoint(
        self,
        entity_type: ControlEntityType,
        entity_id: str,
        *,
        safe_boundary: bool = True,
    ) -> ControlDecision:
        record = self.ensure(entity_type, entity_id)
        if record.state is ControlState.CANCEL_REQUESTED:
            record = self._set(
                entity_type,
                entity_id,
                ControlState.CANCELLED,
                record.reason,
            )
            return ControlDecision(action=ControlAction.CANCEL, record=record)
        if record.state is ControlState.CANCELLED:
            return ControlDecision(action=ControlAction.CANCEL, record=record)
        if record.state is ControlState.PAUSE_REQUESTED and safe_boundary:
            record = self._set(
                entity_type,
                entity_id,
                ControlState.PAUSED,
                record.reason,
            )
            return ControlDecision(action=ControlAction.PAUSE, record=record)
        if record.state is ControlState.PAUSED:
            return ControlDecision(action=ControlAction.PAUSE, record=record)
        return ControlDecision(action=ControlAction.CONTINUE, record=record)

    def mark_completed(
        self,
        entity_type: ControlEntityType,
        entity_id: str,
    ) -> ControlRecord:
        record = self.ensure(entity_type, entity_id)
        if record.state is ControlState.CANCELLED:
            return record
        return self._set(entity_type, entity_id, ControlState.COMPLETED, "")

    def _set(
        self,
        entity_type: ControlEntityType,
        entity_id: str,
        state: ControlState,
        reason: str,
    ) -> ControlRecord:
        record = self.ensure(entity_type, entity_id)
        self.connection.execute(
            """
            UPDATE control_state
            SET state = ?, reason = ?, revision = ?
            WHERE entity_type = ? AND entity_id = ?
            """,
            (
                state.value,
                reason[:2000],
                record.revision + 1,
                entity_type.value,
                entity_id,
            ),
        )
        self.connection.commit()
        return self.get_required(entity_type, entity_id)
