from __future__ import annotations

import threading
from pathlib import Path

import pytest

from universal_coding_agent.core.cancellation import (
    CancellationCoordinator,
    CancellationRequested,
    OwnedOperationKind,
    PauseRequested,
)
from universal_coding_agent.product.models import ControlAction, ControlState
from universal_coding_agent.product.task_control import TaskControlService


class _PausableOperation:
    def __init__(self) -> None:
        self.pause_requests = 0
        self.resume_requests = 0
        self.cancel_requests = 0
        self._paused = threading.Event()
        self._done = threading.Event()

    def pause(self) -> None:
        self.pause_requests += 1
        self._paused.set()

    def resume(self) -> None:
        self.resume_requests += 1
        self._paused.clear()

    def cancel(self) -> None:
        self.cancel_requests += 1
        self._paused.clear()
        self._done.set()

    def paused(self) -> bool:
        return self._paused.is_set()

    def done(self) -> bool:
        return self._done.is_set()

    def finish(self) -> None:
        self._done.set()

    def wait(self) -> None:
        self._done.wait(timeout=5)


class _UnresponsiveResumeOperation(_PausableOperation):
    def resume(self) -> None:
        self.resume_requests += 1


class _DelayedPauseOperation(_PausableOperation):
    def __init__(self) -> None:
        super().__init__()
        self.pause_called = threading.Event()

    def pause(self) -> None:
        self.pause_requests += 1
        self.pause_called.set()


class _DelayedResumeOperation(_PausableOperation):
    def __init__(self) -> None:
        super().__init__()
        self.resume_called = threading.Event()

    def resume(self) -> None:
        self.resume_requests += 1
        self.resume_called.set()

    def acknowledge_resume(self) -> None:
        self._paused.clear()


def _start_pausable_worker(
    control: TaskControlService,
    task_id: str,
    operation: _PausableOperation,
) -> tuple[threading.Thread, threading.Event, list[BaseException]]:
    started = threading.Event()
    errors: list[BaseException] = []
    signal = control.cancellation.signal(task_id)

    def invoke() -> None:
        try:
            with signal.operation(OwnedOperationKind.PROVIDER):
                with signal.owned_pausable_operation(
                    OwnedOperationKind.PROVIDER,
                    lambda: operation,
                ):
                    started.set()
                    operation.wait()
        except BaseException as exc:  # captured for assertion in the parent thread
            errors.append(exc)

    worker = threading.Thread(target=invoke)
    worker.start()
    assert started.wait(timeout=5)
    return worker, started, errors


def test_owned_pausable_operation_acknowledges_pause_and_resume_durably(
    tmp_path: Path,
) -> None:
    database = tmp_path / "active-pause.sqlite"
    coordinator = CancellationCoordinator(
        pause_ack_timeout_seconds=0.05,
        control_poll_interval_seconds=0.001,
    )
    control = TaskControlService(database, cancellation=coordinator)
    task_id = "active-pause-task"
    control.ensure_task(task_id)
    operation = _PausableOperation()
    worker, _, errors = _start_pausable_worker(control, task_id, operation)

    paused = control.pause_task(task_id, reason="operator requested pause")
    report = control.pause_report(task_id)

    assert paused.state is ControlState.PAUSED
    assert operation.paused() is True
    assert report is not None
    assert report.active_operation_kinds == ("provider",)
    assert report.owned_pausable_operations_observed == 1
    assert report.unsupported_active_operations_observed == 0
    assert report.pause_requests == 1
    assert report.pause_acknowledgements == 1
    assert report.pausable_operations_still_unpaused == 0
    assert report.cooperative_fallback is False
    assert report.active_pause_acknowledged is True
    assert report.safe_boundary_reached is False
    with pytest.raises(PauseRequested, match="task active pause acknowledged"):
        with control.cancellation.signal(task_id).operation(
            OwnedOperationKind.PROVIDER
        ):
            raise AssertionError("new owned work must not start during active pause")

    resumed = control.resume_task(task_id)
    resumed_report = control.pause_report(task_id)

    assert resumed.state is ControlState.RUNNING
    assert operation.paused() is False
    assert operation.resume_requests == 1
    assert resumed_report is not None
    assert resumed_report.resume_requests == 1
    assert resumed_report.resume_acknowledgements == 1
    assert resumed_report.pausable_operations_still_paused == 0
    assert resumed_report.pausable_operations_missing_on_resume == 0
    assert resumed_report.active_resume_acknowledged is True

    operation.finish()
    worker.join(timeout=5)
    assert worker.is_alive() is False
    assert errors == []
    control.close()

    reopened = TaskControlService(database)
    assert reopened.pause_report(task_id) == resumed_report
    reopened.close()


def test_unsupported_active_operation_remains_safe_boundary_only(
    tmp_path: Path,
) -> None:
    control = TaskControlService(tmp_path / "cooperative-pause.sqlite")
    task_id = "cooperative-pause-task"
    control.ensure_task(task_id)
    started = threading.Event()
    release = threading.Event()
    signal = control.cancellation.signal(task_id)

    def invoke() -> None:
        with signal.operation(OwnedOperationKind.PROVIDER):
            started.set()
            release.wait(timeout=5)

    worker = threading.Thread(target=invoke)
    worker.start()
    assert started.wait(timeout=5)

    requested = control.pause_task(task_id, reason="safe-boundary fallback")
    report = control.pause_report(task_id)

    assert requested.state is ControlState.PAUSE_REQUESTED
    assert report is not None
    assert report.active_operation_kinds == ("provider",)
    assert report.owned_pausable_operations_observed == 0
    assert report.unsupported_active_operations_observed == 1
    assert report.pause_requests == 0
    assert report.active_pause_acknowledged is False
    assert report.cooperative_fallback is True

    release.set()
    worker.join(timeout=5)
    decision = control.task_action(task_id)
    boundary_report = control.pause_report(task_id)

    assert decision is ControlAction.PAUSE
    assert control.get_task(task_id).state is ControlState.PAUSED  # type: ignore[union-attr]
    assert boundary_report is not None
    assert boundary_report.safe_boundary_reached is True
    assert control.resume_task(task_id).state is ControlState.RUNNING
    control.close()


def test_active_pause_resume_fails_closed_after_runtime_restart(tmp_path: Path) -> None:
    database = tmp_path / "restart-pause.sqlite"
    first = TaskControlService(database)
    task_id = "restart-active-pause"
    first.ensure_task(task_id)
    operation = _PausableOperation()
    worker, _, errors = _start_pausable_worker(first, task_id, operation)

    assert first.pause_task(task_id).state is ControlState.PAUSED
    first.close()

    reopened = TaskControlService(database)
    with pytest.raises(
        ValueError,
        match="active pause resume was not acknowledged by its owned runtime handle",
    ):
        reopened.resume_task(task_id)

    report = reopened.pause_report(task_id)
    assert reopened.get_task(task_id).state is ControlState.PAUSED  # type: ignore[union-attr]
    assert report is not None
    assert report.pausable_operations_missing_on_resume == 1
    assert report.active_resume_acknowledged is False
    reopened.close()

    operation.finish()
    worker.join(timeout=5)
    assert worker.is_alive() is False
    assert errors == []


def test_unacknowledged_resume_keeps_active_pause_fail_closed(tmp_path: Path) -> None:
    coordinator = CancellationCoordinator(
        pause_ack_timeout_seconds=0.02,
        control_poll_interval_seconds=0.001,
    )
    control = TaskControlService(
        tmp_path / "unacknowledged-resume.sqlite",
        cancellation=coordinator,
    )
    task_id = "unacknowledged-resume"
    control.ensure_task(task_id)
    operation = _UnresponsiveResumeOperation()
    worker, _, errors = _start_pausable_worker(control, task_id, operation)

    assert control.pause_task(task_id).state is ControlState.PAUSED
    with pytest.raises(
        ValueError,
        match="active pause resume was not acknowledged by its owned runtime handle",
    ):
        control.resume_task(task_id)

    report = control.pause_report(task_id)
    assert control.get_task(task_id).state is ControlState.PAUSED  # type: ignore[union-attr]
    assert report is not None
    assert report.resume_requests == 1
    assert report.resume_acknowledgements == 0
    assert report.pausable_operations_still_paused == 1
    assert report.active_resume_acknowledged is False

    control.cancel_task(task_id, reason="cancel stalled pause")
    worker.join(timeout=5)
    assert worker.is_alive() is False
    assert len(errors) == 1
    assert isinstance(errors[0], CancellationRequested)
    control.close()


def test_cancel_takes_precedence_over_acknowledged_active_pause(tmp_path: Path) -> None:
    control = TaskControlService(tmp_path / "cancel-paused.sqlite")
    task_id = "cancel-paused-task"
    control.ensure_task(task_id)
    operation = _PausableOperation()
    worker, _, errors = _start_pausable_worker(control, task_id, operation)

    assert control.pause_task(task_id).state is ControlState.PAUSED
    cancelled = control.cancel_task(task_id, reason="operator cancelled paused work")

    assert cancelled.state is ControlState.CANCEL_REQUESTED
    assert operation.cancel_requests == 1
    with pytest.raises(ValueError, match="only paused work can be resumed"):
        control.resume_task(task_id)
    assert control.task_action(task_id) is ControlAction.CANCEL
    worker.join(timeout=5)
    assert worker.is_alive() is False
    assert len(errors) == 1
    assert isinstance(errors[0], CancellationRequested)
    control.close()


def test_cancel_wins_while_active_pause_acknowledgement_is_pending(
    tmp_path: Path,
) -> None:
    coordinator = CancellationCoordinator(
        pause_ack_timeout_seconds=0.2,
        control_poll_interval_seconds=0.001,
    )
    control = TaskControlService(
        tmp_path / "cancel-pending-pause.sqlite",
        cancellation=coordinator,
    )
    task_id = "cancel-pending-pause"
    control.ensure_task(task_id)
    operation = _DelayedPauseOperation()
    worker, _, worker_errors = _start_pausable_worker(control, task_id, operation)
    pause_results: list[ControlState] = []
    pause_errors: list[BaseException] = []

    def request_pause() -> None:
        try:
            pause_results.append(control.pause_task(task_id).state)
        except BaseException as exc:  # captured for assertion in the parent thread
            pause_errors.append(exc)

    pause_worker = threading.Thread(target=request_pause)
    pause_worker.start()
    assert operation.pause_called.wait(timeout=5)

    assert control.cancel_task(task_id).state is ControlState.CANCEL_REQUESTED
    pause_worker.join(timeout=5)
    worker.join(timeout=5)

    report = control.pause_report(task_id)
    assert pause_worker.is_alive() is False
    assert worker.is_alive() is False
    assert pause_results == [ControlState.CANCEL_REQUESTED]
    assert pause_errors == []
    assert report is not None
    assert report.active_pause_acknowledged is False
    assert coordinator.is_pause_requested(task_id) is False
    assert operation.cancel_requests == 1
    assert len(worker_errors) == 1
    assert isinstance(worker_errors[0], CancellationRequested)
    control.close()


def test_safe_boundary_race_is_persisted_before_resume(tmp_path: Path) -> None:
    coordinator = CancellationCoordinator(
        pause_ack_timeout_seconds=0.2,
        control_poll_interval_seconds=0.001,
    )
    control = TaskControlService(
        tmp_path / "pause-boundary-race.sqlite",
        cancellation=coordinator,
    )
    task_id = "pause-boundary-race"
    control.ensure_task(task_id)
    operation = _DelayedPauseOperation()
    worker, _, worker_errors = _start_pausable_worker(control, task_id, operation)
    pause_results: list[ControlState] = []

    pause_worker = threading.Thread(
        target=lambda: pause_results.append(control.pause_task(task_id).state)
    )
    pause_worker.start()
    assert operation.pause_called.wait(timeout=5)

    operation.finish()
    worker.join(timeout=5)
    assert control.task_action(task_id) is ControlAction.PAUSE
    pause_worker.join(timeout=5)

    report = control.pause_report(task_id)
    assert worker.is_alive() is False
    assert pause_worker.is_alive() is False
    assert worker_errors == []
    assert pause_results == [ControlState.PAUSED]
    assert report is not None
    assert report.active_pause_acknowledged is False
    assert report.safe_boundary_reached is True
    assert control.resume_task(task_id).state is ControlState.RUNNING
    control.close()


def test_concurrent_active_resume_attempt_fails_closed(tmp_path: Path) -> None:
    coordinator = CancellationCoordinator(
        pause_ack_timeout_seconds=0.2,
        control_poll_interval_seconds=0.001,
    )
    control = TaskControlService(
        tmp_path / "concurrent-resume.sqlite",
        cancellation=coordinator,
    )
    task_id = "concurrent-resume"
    control.ensure_task(task_id)
    operation = _DelayedResumeOperation()
    worker, _, worker_errors = _start_pausable_worker(control, task_id, operation)
    resume_results: list[ControlState] = []
    resume_errors: list[BaseException] = []

    assert control.pause_task(task_id).state is ControlState.PAUSED

    def resume() -> None:
        try:
            resume_results.append(control.resume_task(task_id).state)
        except BaseException as exc:  # captured for assertion in the parent thread
            resume_errors.append(exc)

    resume_worker = threading.Thread(target=resume)
    resume_worker.start()
    assert operation.resume_called.wait(timeout=5)
    with pytest.raises(ValueError, match="transition is already in progress"):
        control.resume_task(task_id)
    operation.acknowledge_resume()
    resume_worker.join(timeout=5)

    assert resume_worker.is_alive() is False
    assert resume_results == [ControlState.RUNNING]
    assert resume_errors == []
    operation.finish()
    worker.join(timeout=5)
    assert worker.is_alive() is False
    assert worker_errors == []
    control.close()


def test_pause_latch_prevents_new_pausable_work_before_factory_runs() -> None:
    coordinator = CancellationCoordinator()
    task_id = "pause-before-owned-work"
    signal = coordinator.signal(task_id)
    factory_called = False

    coordinator.pause_task(task_id, reason="pause before start")

    def factory() -> _PausableOperation:
        nonlocal factory_called
        factory_called = True
        return _PausableOperation()

    with pytest.raises(PauseRequested, match="task pause requested"):
        with signal.operation(OwnedOperationKind.PROVIDER):
            with signal.owned_pausable_operation(
                OwnedOperationKind.PROVIDER,
                factory,
            ):
                raise AssertionError("paused work must not start")
    assert factory_called is False


def test_invalid_pausable_handle_is_rejected_and_best_effort_cancelled() -> None:
    coordinator = CancellationCoordinator()
    signal = coordinator.signal("invalid-pausable-handle")

    class InvalidHandle:
        def __init__(self) -> None:
            self.cancelled = False

        def cancel(self) -> None:
            self.cancelled = True

        def done(self) -> bool:
            return False

    handle = InvalidHandle()
    with pytest.raises(TypeError, match="invalid control contract"):
        with signal.operation(OwnedOperationKind.PROVIDER):
            with signal.owned_pausable_operation(
                OwnedOperationKind.PROVIDER,
                lambda: handle,  # type: ignore[return-value]
            ):
                raise AssertionError("invalid handle must not be registered")
    assert handle.cancelled is True


def test_pausable_handle_requires_the_matching_active_operation() -> None:
    coordinator = CancellationCoordinator()
    signal = coordinator.signal("unowned-pausable-handle")
    factory_called = False

    def factory() -> _PausableOperation:
        nonlocal factory_called
        factory_called = True
        return _PausableOperation()

    with pytest.raises(RuntimeError, match="requires a matching active operation"):
        with signal.owned_pausable_operation(OwnedOperationKind.PROVIDER, factory):
            raise AssertionError("unowned pausable work must not start")
    with pytest.raises(RuntimeError, match="requires a matching active operation"):
        with signal.operation(OwnedOperationKind.TEST):
            with signal.owned_pausable_operation(
                OwnedOperationKind.PROVIDER,
                factory,
            ):
                raise AssertionError("mismatched pausable work must not start")
    assert factory_called is False
