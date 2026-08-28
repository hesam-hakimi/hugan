from __future__ import annotations

import sqlite3
import stat
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from universal_coding_agent.product.lifecycle_reservations import (
    _RECEIPT_PAGE_QUERY,
    _RESERVATION_CANDIDATE_PAGE_QUERY,
    _WORKER_CANDIDATE_PAGE_QUERY,
    LIFECYCLE_RECOVERY_RECEIPT_INDEX,
    LIFECYCLE_RECOVERY_RESERVATION_CANDIDATE_INDEX,
    LIFECYCLE_RECOVERY_WORKER_CANDIDATE_INDEX,
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


def test_concurrent_store_open_attests_all_recovery_pagination_indexes(
    tmp_path: Path,
) -> None:
    database = tmp_path / "lifecycle.sqlite"

    def open_store() -> tuple[tuple[str, ...], ...]:
        store = DurableLifecycleReservationStore(database)
        try:
            return tuple(
                tuple(
                    row[0]
                    for row in store.connection.execute(
                        "SELECT name FROM pragma_index_info(?) ORDER BY seqno",
                        (index,),
                    ).fetchall()
                )
                for index in (
                    LIFECYCLE_RECOVERY_RESERVATION_CANDIDATE_INDEX,
                    LIFECYCLE_RECOVERY_WORKER_CANDIDATE_INDEX,
                    LIFECYCLE_RECOVERY_RECEIPT_INDEX,
                )
            )
        finally:
            store.close()

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(open_store) for _ in range(2)]
        results = [future.result() for future in futures]

    assert results == [
        (
            ("reservation_kind", "scope_id"),
            ("worker_kind", "scope_id"),
            ("recovered_at", "recovery_ref"),
        ),
        (
            ("reservation_kind", "scope_id"),
            ("worker_kind", "scope_id"),
            ("recovered_at", "recovery_ref"),
        ),
    ]


def test_store_fails_closed_for_wrong_receipt_pagination_index(tmp_path: Path) -> None:
    database = tmp_path / "lifecycle.sqlite"
    store = DurableLifecycleReservationStore(database)
    store.close()
    connection = sqlite3.connect(database)
    connection.execute(f"DROP INDEX {LIFECYCLE_RECOVERY_RECEIPT_INDEX}")
    connection.execute(
        f"""
        CREATE INDEX {LIFECYCLE_RECOVERY_RECEIPT_INDEX}
        ON lifecycle_recovery_receipts(audit_ref)
        """
    )
    connection.close()

    with pytest.raises(ValueError, match="pagination index is unavailable"):
        DurableLifecycleReservationStore(database)


@pytest.mark.parametrize(
    ("index", "table"),
    [
        (
            LIFECYCLE_RECOVERY_RESERVATION_CANDIDATE_INDEX,
            "lifecycle_reservations",
        ),
        (
            LIFECYCLE_RECOVERY_WORKER_CANDIDATE_INDEX,
            "lifecycle_worker_ownership",
        ),
    ],
)
def test_store_fails_closed_for_wrong_candidate_pagination_index(
    tmp_path: Path,
    index: str,
    table: str,
) -> None:
    database = tmp_path / "lifecycle.sqlite"
    store = DurableLifecycleReservationStore(database)
    store.close()
    connection = sqlite3.connect(database)
    connection.execute(f"DROP INDEX {index}")
    connection.execute(f"CREATE INDEX {index} ON {table}(task_id)")
    connection.close()

    with pytest.raises(ValueError, match="candidate pagination indexes are unavailable"):
        DurableLifecycleReservationStore(database)


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


def test_recovery_pages_use_independent_stable_keysets(tmp_path: Path) -> None:
    store = DurableLifecycleReservationStore(tmp_path / "lifecycle.sqlite")
    try:
        for index in range(6):
            store.reserve_standalone_worker(f"task-page-{index:03d}")

        initial = store.recovery_page(candidate_limit=6, receipt_limit=0)
        for candidate in initial.candidates[:4]:
            store.recover(
                target_type=candidate.target_type,
                target_kind=candidate.target_kind,
                scope_id=candidate.scope_id,
                recovery_ref=candidate.recovery_ref,
                reason=f"Verified stopped for {candidate.scope_id}.",
                confirmed=True,
            )

        first = store.recovery_page(candidate_limit=1, receipt_limit=2)
        assert len(first.candidates) == 1
        assert len(first.receipts) == 2
        assert first.candidate_has_more is True
        assert first.receipt_has_more is True
        assert first.next_candidate_key is not None
        assert first.next_receipt_key is not None

        second_candidates = store.recovery_page(
            candidate_after=first.next_candidate_key,
            candidate_limit=1,
            receipt_limit=0,
        )
        second_receipts = store.recovery_page(
            receipt_after=first.next_receipt_key,
            candidate_limit=0,
            receipt_limit=2,
        )
        candidate_refs = [
            *(candidate.recovery_ref for candidate in first.candidates),
            *(candidate.recovery_ref for candidate in second_candidates.candidates),
        ]
        receipt_refs = [
            *(receipt.recovery_ref for receipt in first.receipts),
            *(receipt.recovery_ref for receipt in second_receipts.receipts),
        ]
        assert len(candidate_refs) == len(set(candidate_refs)) == 2
        assert len(receipt_refs) == len(set(receipt_refs)) == 4
        assert second_candidates.candidate_has_more is False
        assert second_candidates.receipts == ()
        assert second_receipts.receipt_has_more is False
        assert second_receipts.candidates == ()
    finally:
        store.close()


def test_candidate_page_queries_use_indexes_and_preserve_cross_stream_order(
    tmp_path: Path,
) -> None:
    database = tmp_path / "lifecycle.sqlite"
    store = DurableLifecycleReservationStore(database)
    try:
        for index in range(2):
            store.reserve_program_control(
                f"program-indexed-reservation-{index:03d}",
                task_ids=(),
            )
            store.reserve_remote_operation(f"task-indexed-reservation-{index:03d}")
            store.reserve_program_worker(f"program-indexed-worker-{index:03d}")
            store.reserve_standalone_worker(f"task-indexed-worker-{index:03d}")

        expected_keys = [
            ("reservation", "program_control", "program-indexed-reservation-000"),
            ("reservation", "program_control", "program-indexed-reservation-001"),
            ("reservation", "remote_operation", "task-indexed-reservation-000"),
            ("reservation", "remote_operation", "task-indexed-reservation-001"),
            ("worker_ownership", "program_execution", "program-indexed-worker-000"),
            ("worker_ownership", "program_execution", "program-indexed-worker-001"),
            ("worker_ownership", "standalone_task", "task-indexed-worker-000"),
            ("worker_ownership", "standalone_task", "task-indexed-worker-001"),
        ]
        collected_keys: list[tuple[str, str, str]] = []
        page_sizes: list[int] = []
        candidate_after = None
        while True:
            page = store.recovery_page(
                candidate_after=candidate_after,
                candidate_limit=3,
                receipt_limit=0,
            )
            collected_keys.extend(
                (candidate.target_type, candidate.target_kind, candidate.scope_id)
                for candidate in page.candidates
            )
            page_sizes.append(len(page.candidates))
            if not page.candidate_has_more:
                assert page.next_candidate_key is None
                break
            assert page.next_candidate_key is not None
            candidate_after = page.next_candidate_key

        reservation_plan = store.connection.execute(
            f"EXPLAIN QUERY PLAN {_RESERVATION_CANDIDATE_PAGE_QUERY}",
            ("", "", 4),
        ).fetchall()
        worker_plan = store.connection.execute(
            f"EXPLAIN QUERY PLAN {_WORKER_CANDIDATE_PAGE_QUERY}",
            ("", "", 4),
        ).fetchall()
        reservation_details = [row[3] for row in reservation_plan]
        worker_details = [row[3] for row in worker_plan]

        assert collected_keys == expected_keys
        assert page_sizes == [3, 3, 2]
        assert len(collected_keys) == len(set(collected_keys))
        assert any(
            f"USING INDEX {LIFECYCLE_RECOVERY_RESERVATION_CANDIDATE_INDEX}"
            in detail
            for detail in reservation_details
        )
        assert any(
            f"USING INDEX {LIFECYCLE_RECOVERY_WORKER_CANDIDATE_INDEX}" in detail
            for detail in worker_details
        )
        assert not any("SCAN lifecycle_reservations" in detail for detail in reservation_details)
        assert not any(
            "SCAN lifecycle_worker_ownership" in detail for detail in worker_details
        )
        assert not any("USE TEMP B-TREE" in detail for detail in reservation_details)
        assert not any("USE TEMP B-TREE" in detail for detail in worker_details)
    finally:
        store.close()

    legacy_connection = sqlite3.connect(database)
    legacy_connection.execute(
        f"DROP INDEX {LIFECYCLE_RECOVERY_RESERVATION_CANDIDATE_INDEX}"
    )
    legacy_connection.execute(
        f"DROP INDEX {LIFECYCLE_RECOVERY_WORKER_CANDIDATE_INDEX}"
    )
    legacy_connection.close()
    reopened = DurableLifecycleReservationStore(database)
    try:
        page = reopened.recovery_page(candidate_limit=3, receipt_limit=0)
        assert [
            (candidate.target_type, candidate.target_kind, candidate.scope_id)
            for candidate in page.candidates
        ] == expected_keys[:3]
        assert page.candidate_has_more is True
        assert page.next_candidate_key == expected_keys[2]
    finally:
        reopened.close()


def test_receipt_page_query_uses_composite_index_without_temporary_sort(
    tmp_path: Path,
) -> None:
    database = tmp_path / "lifecycle.sqlite"
    store = DurableLifecycleReservationStore(database)
    try:
        for index in range(8):
            store.reserve_standalone_worker(f"task-indexed-receipt-{index:03d}")
            candidate = store.recovery_page(
                candidate_limit=1,
                receipt_limit=0,
            ).candidates[0]
            store.recover(
                target_type=candidate.target_type,
                target_kind=candidate.target_kind,
                scope_id=candidate.scope_id,
                recovery_ref=candidate.recovery_ref,
                reason=f"Verified stopped for {candidate.scope_id}.",
                confirmed=True,
            )

        metadata = store.connection.execute(
            """
            SELECT name, "unique", partial
            FROM pragma_index_list(?)
            WHERE name = ?
            """,
            (
                "lifecycle_recovery_receipts",
                LIFECYCLE_RECOVERY_RECEIPT_INDEX,
            ),
        ).fetchall()
        columns = store.connection.execute(
            "SELECT name FROM pragma_index_info(?) ORDER BY seqno",
            (LIFECYCLE_RECOVERY_RECEIPT_INDEX,),
        ).fetchall()
        plan = store.connection.execute(
            f"EXPLAIN QUERY PLAN {_RECEIPT_PAGE_QUERY}",
            ("", "", 3),
        ).fetchall()
        details = [row[3] for row in plan]

        assert metadata == [(LIFECYCLE_RECOVERY_RECEIPT_INDEX, 0, 0)]
        assert columns == [("recovered_at",), ("recovery_ref",)]
        assert any(
            f"USING INDEX {LIFECYCLE_RECOVERY_RECEIPT_INDEX}" in detail
            for detail in details
        )
        assert not any("SCAN lifecycle_recovery_receipts" in detail for detail in details)
        assert not any("USE TEMP B-TREE" in detail for detail in details)
        assert len(store.recovery_page(candidate_limit=0, receipt_limit=2).receipts) == 2
    finally:
        store.close()

    legacy_connection = sqlite3.connect(database)
    legacy_connection.execute(f"DROP INDEX {LIFECYCLE_RECOVERY_RECEIPT_INDEX}")
    legacy_connection.close()
    reopened = DurableLifecycleReservationStore(database)
    try:
        page = reopened.recovery_page(candidate_limit=0, receipt_limit=2)
        assert len(page.receipts) == 2
        assert page.receipt_has_more is True
        assert page.next_receipt_key is not None
    finally:
        reopened.close()


@pytest.mark.parametrize(
    ("arguments", "message"),
    [
        ({"candidate_limit": -1}, "candidate limit"),
        ({"candidate_limit": 101}, "candidate limit"),
        ({"candidate_limit": True}, "candidate limit"),
        ({"receipt_limit": -1}, "receipt limit"),
        ({"receipt_limit": 101}, "receipt limit"),
        ({"receipt_limit": False}, "receipt limit"),
        ({"candidate_after": ("reservation", "bad", "task-valid")}, "candidate cursor"),
        (
            {"candidate_after": ["reservation", "remote_operation", "task-valid"]},
            "candidate cursor",
        ),
        ({"receipt_after": ("not-a-time", "sha256:" + "0" * 64)}, "receipt cursor"),
        (
            {
                "receipt_after": [
                    "2026-01-01T00:00:00+00:00",
                    "sha256:" + "0" * 64,
                ]
            },
            "receipt cursor",
        ),
    ],
)
def test_recovery_page_rejects_invalid_limits_and_keys(
    tmp_path: Path,
    arguments: dict[str, object],
    message: str,
) -> None:
    store = DurableLifecycleReservationStore(tmp_path / "lifecycle.sqlite")
    try:
        with pytest.raises(ValueError, match=message):
            store.recovery_page(**arguments)  # type: ignore[arg-type]
    finally:
        store.close()


def test_compatibility_snapshot_fails_closed_above_hard_limit(tmp_path: Path) -> None:
    store = DurableLifecycleReservationStore(tmp_path / "lifecycle.sqlite")
    try:
        for index in range(101):
            store.reserve_standalone_worker(f"task-snapshot-{index:03d}")
        with pytest.raises(ValueError, match="exceeds bounded limit"):
            store.recovery_snapshot()
        page = store.recovery_page(candidate_limit=100, receipt_limit=0)
        assert len(page.candidates) == 100
        assert page.candidate_has_more is True
        assert page.next_candidate_key is not None
    finally:
        store.close()


def test_recovery_page_fails_closed_for_oversized_unreturned_row(tmp_path: Path) -> None:
    store = DurableLifecycleReservationStore(tmp_path / "lifecycle.sqlite")
    try:
        store.reserve_standalone_worker("task-bounded-001")
        store.reserve_standalone_worker("task-bounded-002")
        store.connection.execute(
            "UPDATE lifecycle_worker_ownership SET created_at = ? WHERE scope_id = ?",
            ("x" * 65, "task-bounded-002"),
        )
        with pytest.raises(ValueError, match="recovery state is unavailable"):
            store.recovery_page(candidate_limit=1, receipt_limit=0)
    finally:
        store.close()


def test_recovery_and_paged_reads_fail_closed_for_oversized_receipt(
    tmp_path: Path,
) -> None:
    store = DurableLifecycleReservationStore(tmp_path / "lifecycle.sqlite")
    try:
        store.reserve_standalone_worker(_TASK_ID)
        candidate = store.recovery_page(candidate_limit=1, receipt_limit=0).candidates[0]
        receipt = store.recover(
            target_type=candidate.target_type,
            target_kind=candidate.target_kind,
            scope_id=candidate.scope_id,
            recovery_ref=candidate.recovery_ref,
            reason="Verified stopped.",
            confirmed=True,
        )
        store.connection.execute(
            "UPDATE lifecycle_recovery_receipts SET reason = ? WHERE recovery_ref = ?",
            ("x" * 2001, receipt.recovery_ref),
        )
        with pytest.raises(ValueError, match="recovery state is unavailable"):
            store.recovery_page(candidate_limit=0, receipt_limit=1)
        with pytest.raises(ValueError, match="field exceeds configured bounds"):
            store.recover(
                target_type=receipt.target_type,
                target_kind=receipt.target_kind,
                scope_id=receipt.scope_id,
                recovery_ref=receipt.recovery_ref,
                reason=receipt.reason,
                confirmed=True,
            )
    finally:
        store.close()
