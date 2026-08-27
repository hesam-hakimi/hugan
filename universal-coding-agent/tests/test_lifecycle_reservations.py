from __future__ import annotations

import sqlite3
import stat
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from universal_coding_agent.product.lifecycle_reservations import (
    DurableLifecycleReservationStore,
)

_TASK_ID = "task-durable-reservation"
_PROGRAM_ID = "program-durable-reservation"


def test_remote_and_program_reservations_are_shared_across_store_instances(
    tmp_path: Path,
) -> None:
    database = tmp_path / "lifecycle.sqlite"
    first = DurableLifecycleReservationStore(database)
    second = DurableLifecycleReservationStore(database)
    try:
        remote_owner = first.reserve_remote_operation(
            _TASK_ID,
            program_id=_PROGRAM_ID,
        )
        with pytest.raises(ValueError, match="remote-operation lifecycle action"):
            second.reserve_program_control(
                _PROGRAM_ID,
                task_ids=(_TASK_ID,),
            )

        with pytest.raises(ValueError, match="ownership mismatch"):
            second.release_remote_operation(_TASK_ID, "0" * 32)
        assert second.snapshot().remote_task_ids == {_TASK_ID}

        second.release_remote_operation(_TASK_ID, remote_owner)
        program_owner = second.reserve_program_control(
            _PROGRAM_ID,
            task_ids=(_TASK_ID,),
        )
        with pytest.raises(ValueError, match="Program control action"):
            first.reserve_remote_operation(_TASK_ID, program_id=_PROGRAM_ID)
        first.release_program_control(_PROGRAM_ID, program_owner)
        assert first.snapshot().remote_task_ids == frozenset()
        assert first.snapshot().program_ids == frozenset()
    finally:
        first.close()
        second.close()


def test_interrupted_reservation_survives_restart_and_blocks(tmp_path: Path) -> None:
    database = tmp_path / "lifecycle.sqlite"
    first = DurableLifecycleReservationStore(database)
    owner = first.reserve_remote_operation(_TASK_ID, program_id=_PROGRAM_ID)
    first.close()

    reopened = DurableLifecycleReservationStore(database)
    try:
        assert reopened.snapshot().remote_task_ids == {_TASK_ID}
        with pytest.raises(ValueError, match="remote-operation lifecycle action"):
            reopened.reserve_program_control(
                _PROGRAM_ID,
                task_ids=(_TASK_ID,),
            )
        reopened.release_remote_operation(_TASK_ID, owner)
    finally:
        reopened.close()


def test_competing_cross_runtime_reservations_have_one_winner(tmp_path: Path) -> None:
    database = tmp_path / "lifecycle.sqlite"
    remote_store = DurableLifecycleReservationStore(database)
    program_store = DurableLifecycleReservationStore(database)

    def reserve_remote() -> tuple[str, str]:
        try:
            return (
                "remote",
                remote_store.reserve_remote_operation(
                    _TASK_ID,
                    program_id=_PROGRAM_ID,
                ),
            )
        except ValueError:
            return ("remote_rejected", "")

    def reserve_program() -> tuple[str, str]:
        try:
            return (
                "program",
                program_store.reserve_program_control(
                    _PROGRAM_ID,
                    task_ids=(_TASK_ID,),
                ),
            )
        except ValueError:
            return ("program_rejected", "")

    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            remote_future = executor.submit(reserve_remote)
            program_future = executor.submit(reserve_program)
            outcomes = {
                remote_future.result(),
                program_future.result(),
            }
        labels = {label for label, _owner in outcomes}
        assert labels in (
            {"remote", "program_rejected"},
            {"remote_rejected", "program"},
        )
        for label, owner in outcomes:
            if label == "remote":
                remote_store.release_remote_operation(_TASK_ID, owner)
            elif label == "program":
                program_store.release_program_control(_PROGRAM_ID, owner)
    finally:
        remote_store.close()
        program_store.close()


def test_invalid_persisted_reservation_fails_closed(tmp_path: Path) -> None:
    database = tmp_path / "lifecycle.sqlite"
    store = DurableLifecycleReservationStore(database)
    store.reserve_remote_operation(_TASK_ID, program_id=_PROGRAM_ID)
    store.connection.execute("PRAGMA ignore_check_constraints = ON")
    store.connection.execute("UPDATE lifecycle_reservations SET created_at = 'not-a-timestamp'")

    try:
        with pytest.raises(ValueError, match="reservation state is unavailable"):
            store.snapshot()
        with pytest.raises(ValueError, match="timestamp"):
            store.reserve_program_control(
                _PROGRAM_ID,
                task_ids=(_TASK_ID,),
            )
    finally:
        store.close()


def test_missing_reservation_schema_fails_closed(tmp_path: Path) -> None:
    store = DurableLifecycleReservationStore(tmp_path / "lifecycle.sqlite")
    store.connection.execute("DROP TABLE lifecycle_reservations")
    try:
        with pytest.raises(ValueError, match="reservation state is unavailable"):
            store.reserve_remote_operation(_TASK_ID, program_id=_PROGRAM_ID)
    finally:
        store.close()


def test_store_adds_schema_to_existing_product_database_directory(
    tmp_path: Path,
) -> None:
    database = tmp_path / "lifecycle.sqlite"
    connection = sqlite3.connect(database)
    connection.execute("CREATE TABLE existing_product_state (value TEXT NOT NULL)")
    connection.execute("INSERT INTO existing_product_state VALUES ('preserved')")
    connection.commit()
    connection.close()

    store = DurableLifecycleReservationStore(database)
    try:
        preserved = store.connection.execute("SELECT value FROM existing_product_state").fetchone()
        assert preserved == ("preserved",)
        assert store.snapshot().remote_task_ids == frozenset()
        assert stat.S_IMODE(database.stat().st_mode) == 0o600
    finally:
        store.close()
