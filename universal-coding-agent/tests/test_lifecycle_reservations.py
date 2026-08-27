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


def test_worker_ownership_is_shared_with_lifecycle_actions(tmp_path: Path) -> None:
    database = tmp_path / "lifecycle.sqlite"
    worker_store = DurableLifecycleReservationStore(database)
    action_store = DurableLifecycleReservationStore(database)
    try:
        task_owner = worker_store.reserve_standalone_worker(_TASK_ID)
        with pytest.raises(ValueError, match="local worker"):
            action_store.reserve_remote_operation(_TASK_ID)
        with pytest.raises(ValueError, match="ownership mismatch"):
            action_store.release_standalone_worker(_TASK_ID, "0" * 32)
        assert action_store.snapshot().worker_task_ids == {_TASK_ID}
        action_store.release_standalone_worker(_TASK_ID, task_owner)

        program_owner = action_store.reserve_program_worker(_PROGRAM_ID)
        with pytest.raises(ValueError, match="local worker"):
            worker_store.reserve_program_control(
                _PROGRAM_ID,
                task_ids=(_TASK_ID,),
            )
        with pytest.raises(ValueError, match="local worker"):
            worker_store.reserve_remote_operation(
                _TASK_ID,
                program_id=_PROGRAM_ID,
            )
        assert worker_store.snapshot().worker_program_ids == {_PROGRAM_ID}
        worker_store.release_program_worker(_PROGRAM_ID, program_owner)
    finally:
        worker_store.close()
        action_store.close()


def test_interrupted_worker_ownership_survives_restart_and_blocks(
    tmp_path: Path,
) -> None:
    database = tmp_path / "lifecycle.sqlite"
    first = DurableLifecycleReservationStore(database)
    owner = first.reserve_program_worker(_PROGRAM_ID)
    first.close()

    reopened = DurableLifecycleReservationStore(database)
    try:
        assert reopened.snapshot().worker_program_ids == {_PROGRAM_ID}
        with pytest.raises(ValueError, match="local worker"):
            reopened.reserve_program_control(_PROGRAM_ID, task_ids=(_TASK_ID,))
        reopened.release_program_worker(_PROGRAM_ID, owner)
    finally:
        reopened.close()


def test_competing_worker_and_lifecycle_action_have_one_winner(
    tmp_path: Path,
) -> None:
    database = tmp_path / "lifecycle.sqlite"
    worker_store = DurableLifecycleReservationStore(database)
    action_store = DurableLifecycleReservationStore(database)

    def reserve_worker() -> tuple[str, str]:
        try:
            return "worker", worker_store.reserve_program_worker(_PROGRAM_ID)
        except ValueError:
            return "worker_rejected", ""

    def reserve_action() -> tuple[str, str]:
        try:
            return (
                "action",
                action_store.reserve_program_control(
                    _PROGRAM_ID,
                    task_ids=(_TASK_ID,),
                ),
            )
        except ValueError:
            return "action_rejected", ""

    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            worker_future = executor.submit(reserve_worker)
            action_future = executor.submit(reserve_action)
            outcomes = {
                worker_future.result(),
                action_future.result(),
            }
        labels = {label for label, _owner in outcomes}
        assert labels in (
            {"worker", "action_rejected"},
            {"worker_rejected", "action"},
        )
        for label, owner in outcomes:
            if label == "worker":
                worker_store.release_program_worker(_PROGRAM_ID, owner)
            elif label == "action":
                action_store.release_program_control(_PROGRAM_ID, owner)
    finally:
        worker_store.close()
        action_store.close()


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


def test_invalid_persisted_worker_ownership_fails_closed(tmp_path: Path) -> None:
    database = tmp_path / "lifecycle.sqlite"
    store = DurableLifecycleReservationStore(database)
    store.reserve_standalone_worker(_TASK_ID)
    store.connection.execute("PRAGMA ignore_check_constraints = ON")
    store.connection.execute(
        "UPDATE lifecycle_worker_ownership SET created_at = 'not-a-timestamp'"
    )

    try:
        with pytest.raises(ValueError, match="reservation state is unavailable"):
            store.snapshot()
        with pytest.raises(ValueError, match="timestamp"):
            store.reserve_remote_operation(_TASK_ID)
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


def test_explicit_reservation_recovery_is_atomic_redacted_and_restart_safe(
    tmp_path: Path,
) -> None:
    database = tmp_path / "lifecycle.sqlite"
    first = DurableLifecycleReservationStore(database)
    owner = first.reserve_remote_operation(_TASK_ID, program_id=_PROGRAM_ID)
    candidates, receipts = first.recovery_snapshot()
    assert receipts == ()
    candidate = candidates[0]
    assert candidate.target_type == "reservation"
    assert candidate.target_kind == "remote_operation"
    assert owner not in repr(candidate)

    receipt = first.recover(
        target_type=candidate.target_type,
        target_kind=candidate.target_kind,
        scope_id=candidate.scope_id,
        recovery_ref=candidate.recovery_ref,
        reason="Operator verified the interrupted runtime is no longer running.",
        confirmed=True,
    )
    assert receipt.audit_ref.startswith("sha256:")
    assert owner not in repr(receipt)
    assert first.snapshot().remote_task_ids == frozenset()
    first.close()

    reopened = DurableLifecycleReservationStore(database)
    try:
        candidates, receipts = reopened.recovery_snapshot()
        assert candidates == ()
        assert receipts == (receipt,)
        assert owner not in repr(receipts)
    finally:
        reopened.close()


def test_worker_recovery_exact_retry_is_idempotent_and_immutable(tmp_path: Path) -> None:
    store = DurableLifecycleReservationStore(tmp_path / "lifecycle.sqlite")
    store.reserve_program_worker(_PROGRAM_ID)
    candidate = store.recovery_snapshot()[0][0]
    arguments = {
        "target_type": candidate.target_type,
        "target_kind": candidate.target_kind,
        "scope_id": candidate.scope_id,
        "recovery_ref": candidate.recovery_ref,
        "reason": "The worker process was explicitly verified stopped.",
        "confirmed": True,
    }
    try:
        first = store.recover(**arguments)
        assert store.recover(**arguments) == first
        with pytest.raises(ValueError, match="immutable"):
            store.recover(**{**arguments, "reason": "Different reason."})
        assert store.snapshot().worker_program_ids == frozenset()
        assert len(store.recovery_snapshot()[1]) == 1
    finally:
        store.close()


def test_recovery_requires_confirmation_and_exact_current_target(tmp_path: Path) -> None:
    store = DurableLifecycleReservationStore(tmp_path / "lifecycle.sqlite")
    store.reserve_standalone_worker(_TASK_ID)
    candidate = store.recovery_snapshot()[0][0]
    try:
        with pytest.raises(ValueError, match="explicit confirmation"):
            store.recover(
                target_type=candidate.target_type,
                target_kind=candidate.target_kind,
                scope_id=candidate.scope_id,
                recovery_ref=candidate.recovery_ref,
                reason="Verified stopped.",
                confirmed=False,
            )
        with pytest.raises(ValueError, match="target changed"):
            store.recover(
                target_type=candidate.target_type,
                target_kind=candidate.target_kind,
                scope_id=candidate.scope_id,
                recovery_ref="sha256:" + "0" * 64,
                reason="Verified stopped.",
                confirmed=True,
            )
        assert store.snapshot().worker_task_ids == {_TASK_ID}
        assert store.recovery_snapshot()[1] == ()
    finally:
        store.close()


def test_recovery_receipt_insert_rolls_back_when_exact_delete_fails(tmp_path: Path) -> None:
    store = DurableLifecycleReservationStore(tmp_path / "lifecycle.sqlite")
    store.reserve_program_control(_PROGRAM_ID, task_ids=())
    candidate = store.recovery_snapshot()[0][0]
    store.connection.execute(
        """
        CREATE TRIGGER block_recovery_delete
        BEFORE DELETE ON lifecycle_reservations
        BEGIN SELECT RAISE(ABORT, 'blocked'); END
        """
    )
    try:
        with pytest.raises(ValueError, match="state is unavailable"):
            store.recover(
                target_type=candidate.target_type,
                target_kind=candidate.target_kind,
                scope_id=candidate.scope_id,
                recovery_ref=candidate.recovery_ref,
                reason="Verified stopped.",
                confirmed=True,
            )
        assert store.snapshot().program_ids == {_PROGRAM_ID}
        assert store.recovery_snapshot()[1] == ()
    finally:
        store.close()


def test_corrupt_recovery_receipt_fails_closed(tmp_path: Path) -> None:
    store = DurableLifecycleReservationStore(tmp_path / "lifecycle.sqlite")
    store.reserve_standalone_worker(_TASK_ID)
    candidate = store.recovery_snapshot()[0][0]
    store.recover(
        target_type=candidate.target_type,
        target_kind=candidate.target_kind,
        scope_id=candidate.scope_id,
        recovery_ref=candidate.recovery_ref,
        reason="Verified stopped.",
        confirmed=True,
    )
    store.connection.execute(
        "UPDATE lifecycle_recovery_receipts SET reason = 'tampered'"
    )
    try:
        with pytest.raises(ValueError, match="recovery state is unavailable"):
            store.recovery_snapshot()
    finally:
        store.close()
