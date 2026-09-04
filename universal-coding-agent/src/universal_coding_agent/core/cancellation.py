from __future__ import annotations

import os
import signal
import subprocess
import time
from collections.abc import Callable, Iterable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import asdict, dataclass
from enum import StrEnum
from threading import Event, RLock
from typing import Any, Protocol


class CancellationRequested(RuntimeError):
    """Raised when cancelled work reaches a cooperative checkpoint."""


class PauseRequested(RuntimeError):
    """Raised before new pausable work starts while a task pause is latched."""


class OwnedOperationKind(StrEnum):
    PROVIDER = "provider"
    TEST = "test"


class OwnedCancellableOperation(Protocol):
    """One trusted operation whose cancellation hook returns without blocking."""

    def cancel(self) -> None:
        """Request termination of the owned operation."""

    def done(self) -> bool:
        """Return without blocking whether the owned operation has terminated."""


class OwnedPausableOperation(OwnedCancellableOperation, Protocol):
    """One trusted owned handle with non-blocking pause lifecycle hooks."""

    def pause(self) -> None:
        """Request a cooperative pause without blocking."""

    def resume(self) -> None:
        """Request continuation without blocking."""

    def paused(self) -> bool:
        """Return without blocking whether the operation acknowledged its pause."""


@dataclass(frozen=True)
class CancellationReport:
    task_id: str
    reason: str
    active_operation_kinds: tuple[str, ...]
    owned_processes_observed: int
    owned_cancellable_operations_observed: int
    terminate_requests: int
    kill_requests: int
    cancellable_operation_cancel_requests: int
    processes_still_active: int
    cancellable_operations_still_active: int
    cooperative_fallback: bool

    def to_json(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PauseReport:
    """Redacted evidence for one task-scoped active-pause attempt."""

    task_id: str
    reason: str
    active_operation_kinds: tuple[str, ...]
    owned_pausable_operations_observed: int
    unsupported_active_operations_observed: int
    pause_requests: int
    pause_acknowledgements: int
    pausable_operations_still_unpaused: int
    cooperative_fallback: bool
    active_pause_acknowledged: bool
    safe_boundary_reached: bool = False
    resume_requests: int = 0
    resume_acknowledgements: int = 0
    pausable_operations_still_paused: int = 0
    pausable_operations_missing_on_resume: int = 0
    active_resume_acknowledged: bool = False

    def to_json(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PauseResumeResult:
    """Bounded in-runtime result for resuming the exact paused owned handles."""

    task_id: str
    owned_pausable_operations_observed: int
    resume_requests: int
    resume_acknowledgements: int
    pausable_operations_still_paused: int
    pausable_operations_missing_on_resume: int
    active_resume_acknowledged: bool


@dataclass(frozen=True, eq=False)
class _OwnedOperation:
    kind: OwnedOperationKind


@dataclass(frozen=True)
class _OwnedProcess:
    kind: OwnedOperationKind
    process: subprocess.Popen[str]


@dataclass(frozen=True)
class _OwnedCancellable:
    kind: OwnedOperationKind
    operation: OwnedCancellableOperation


@dataclass(frozen=True, eq=False)
class _OwnedPausable:
    kind: OwnedOperationKind
    operation: OwnedPausableOperation
    owner: _OwnedOperation


class CancellationSignal:
    """Task-scoped signal for explicitly registered processes and cancellation handles."""

    def __init__(self, coordinator: CancellationCoordinator, task_id: str) -> None:
        self._coordinator = coordinator
        self.task_id = task_id
        self._operation_stack: ContextVar[tuple[_OwnedOperation, ...]] = ContextVar(
            f"uca_owned_operation_stack_{id(self)}",
            default=(),
        )

    @property
    def cancelled(self) -> bool:
        return self._coordinator.is_cancelled(self.task_id)

    @property
    def pause_requested(self) -> bool:
        return self._coordinator.is_pause_requested(self.task_id)

    def raise_if_cancelled(self) -> None:
        if self.cancelled:
            raise CancellationRequested("task cancellation requested")

    @contextmanager
    def operation(self, kind: OwnedOperationKind) -> Iterator[None]:
        owned = self._coordinator._begin_operation(self.task_id, kind)
        stack_token = self._operation_stack.set(
            (*self._operation_stack.get(), owned)
        )
        try:
            self.raise_if_cancelled()
            yield
            self.raise_if_cancelled()
        finally:
            self._operation_stack.reset(stack_token)
            self._coordinator._end_operation(self.task_id, owned)

    @contextmanager
    def owned_process(
        self,
        kind: OwnedOperationKind,
        factory: Callable[[], subprocess.Popen[str]],
    ) -> Iterator[subprocess.Popen[str]]:
        owned = self._coordinator._start_process(self.task_id, kind, factory)
        try:
            yield owned.process
            self.raise_if_cancelled()
        finally:
            self._coordinator._unregister_process(self.task_id, owned)

    @contextmanager
    def owned_cancellable_operation(
        self,
        kind: OwnedOperationKind,
        factory: Callable[[], OwnedCancellableOperation],
    ) -> Iterator[OwnedCancellableOperation]:
        """Register one explicitly owned in-process or remote operation handle."""

        owned = self._coordinator._start_cancellable(self.task_id, kind, factory)
        try:
            yield owned.operation
            self.raise_if_cancelled()
        except BaseException:
            self.raise_if_cancelled()
            raise
        finally:
            self._coordinator._unregister_cancellable(self.task_id, owned)

    @contextmanager
    def owned_pausable_operation(
        self,
        kind: OwnedOperationKind,
        factory: Callable[[], OwnedPausableOperation],
    ) -> Iterator[OwnedPausableOperation]:
        """Register one explicitly owned, cancellable, and pausable handle."""

        operation_stack = self._operation_stack.get()
        if not operation_stack or operation_stack[-1].kind is not kind:
            raise RuntimeError(
                "owned pausable operation requires a matching active operation"
            )
        owned = self._coordinator._start_pausable(
            self.task_id,
            kind,
            operation_stack[-1],
            factory,
        )
        try:
            yield owned.operation
            self.raise_if_cancelled()
        except BaseException:
            self.raise_if_cancelled()
            raise
        finally:
            self._coordinator._unregister_pausable(self.task_id, owned)


class CancellationCoordinator:
    """Coordinate cooperative control of explicitly owned work."""

    def __init__(
        self,
        *,
        pause_ack_timeout_seconds: float = 1.0,
        control_poll_interval_seconds: float = 0.01,
    ) -> None:
        if pause_ack_timeout_seconds <= 0:
            raise ValueError("pause acknowledgement timeout must be positive")
        if control_poll_interval_seconds <= 0:
            raise ValueError("control poll interval must be positive")
        self._lock = RLock()
        self._events: dict[str, Event] = {}
        self._pause_events: dict[str, Event] = {}
        self._operations: dict[str, list[_OwnedOperation]] = {}
        self._processes: dict[str, list[_OwnedProcess]] = {}
        self._cancellables: dict[
            str,
            list[_OwnedCancellable | _OwnedPausable],
        ] = {}
        self._pausables: dict[str, list[_OwnedPausable]] = {}
        self._paused_pausables: dict[str, tuple[_OwnedPausable, ...]] = {}
        self._pause_ack_timeout_seconds = pause_ack_timeout_seconds
        self._control_poll_interval_seconds = control_poll_interval_seconds

    def signal(self, task_id: str) -> CancellationSignal:
        with self._lock:
            self._events.setdefault(task_id, Event())
        return CancellationSignal(self, task_id)

    def is_cancelled(self, task_id: str) -> bool:
        with self._lock:
            event = self._events.get(task_id)
            return bool(event and event.is_set())

    def is_pause_requested(self, task_id: str) -> bool:
        with self._lock:
            event = self._pause_events.get(task_id)
            return bool(event and event.is_set())

    def pause_task(self, task_id: str, *, reason: str = "") -> PauseReport:
        """Request pause only from currently registered trusted pausable handles."""

        with self._lock:
            cancel_event = self._events.setdefault(task_id, Event())
            pause_event = self._pause_events.setdefault(task_id, Event())
            cancelled = cancel_event.is_set()
            if cancelled:
                pause_event.clear()
            else:
                pause_event.set()
            operations = tuple(self._operations.get(task_id, ()))
            registered_pausables = tuple(self._pausables.get(task_id, ()))
            pausables = tuple(
                owned
                for owned in registered_pausables
                if _pausable_active(owned.operation)
            )
            active_processes = sum(
                owned.process.poll() is None
                for owned in self._processes.get(task_id, ())
            )
            active_non_pausable_handles = sum(
                _cancellable_active(owned.operation)
                for owned in self._cancellables.get(task_id, ())
                if not isinstance(owned, _OwnedPausable)
            )

        uncovered_operations = sum(
            not any(owned.owner is operation for owned in pausables)
            for operation in operations
        )
        orphaned_pausables = sum(
            not any(owned.owner is operation for operation in operations)
            for owned in pausables
        )
        unsupported = max(
            uncovered_operations + orphaned_pausables,
            active_processes + active_non_pausable_handles,
        )
        pause_requests = 0
        if not cancelled:
            for owned in pausables:
                if _pausable_pause_status(owned.operation) is not True:
                    _pause_pausable(owned.operation)
                    pause_requests += 1

        deadline = time.monotonic() + self._pause_ack_timeout_seconds
        while not cancelled and any(
            _pausable_active(owned.operation)
            and _pausable_pause_status(owned.operation) is not True
            for owned in pausables
        ):
            if time.monotonic() >= deadline:
                break
            time.sleep(self._control_poll_interval_seconds)
            cancelled = self.is_cancelled(task_id)

        with self._lock:
            current_operations = tuple(self._operations.get(task_id, ()))
            current_pausables = tuple(
                owned
                for owned in self._pausables.get(task_id, ())
                if _pausable_active(owned.operation)
            )
            current_active_processes = sum(
                owned.process.poll() is None
                for owned in self._processes.get(task_id, ())
            )
            current_active_non_pausable_handles = sum(
                _cancellable_active(owned.operation)
                for owned in self._cancellables.get(task_id, ())
                if not isinstance(owned, _OwnedPausable)
            )
            cancelled = cancel_event.is_set()
            registrations_unchanged = _same_owned_registrations(
                operations,
                current_operations,
            ) and _same_owned_registrations(pausables, current_pausables)
            current_uncovered_operations = sum(
                not any(owned.owner is operation for owned in current_pausables)
                for operation in current_operations
            )
            current_orphaned_pausables = sum(
                not any(
                    owned.owner is operation for operation in current_operations
                )
                for owned in current_pausables
            )
            unsupported = max(
                unsupported,
                current_uncovered_operations + current_orphaned_pausables,
                current_active_processes + current_active_non_pausable_handles,
            )
            if not registrations_unchanged and (operations or pausables):
                unsupported = max(unsupported, 1)

            acknowledgements = 0
            still_unpaused = 0
            for owned in pausables:
                if not _pausable_active(owned.operation):
                    continue
                if _pausable_pause_status(owned.operation) is True:
                    acknowledgements += 1
                else:
                    still_unpaused += 1

            active_pause_acknowledged = bool(
                operations
                and pausables
                and not cancelled
                and pause_event.is_set()
                and registrations_unchanged
                and unsupported == 0
                and acknowledgements == len(pausables)
                and still_unpaused == 0
            )
            if active_pause_acknowledged:
                self._paused_pausables[task_id] = pausables
            else:
                self._paused_pausables.pop(task_id, None)
                if cancelled:
                    pause_event.clear()

        return PauseReport(
            task_id=task_id,
            reason=reason[:2000],
            active_operation_kinds=tuple(
                sorted({item.kind.value for item in operations})
            ),
            owned_pausable_operations_observed=len(pausables),
            unsupported_active_operations_observed=unsupported,
            pause_requests=pause_requests,
            pause_acknowledgements=acknowledgements,
            pausable_operations_still_unpaused=still_unpaused,
            cooperative_fallback=bool(operations) and not active_pause_acknowledged,
            active_pause_acknowledged=active_pause_acknowledged,
        )

    def resume_task(self, task_id: str) -> PauseResumeResult:
        """Resume only the exact in-runtime handles that acknowledged the pause."""

        with self._lock:
            paused = tuple(self._paused_pausables.get(task_id, ()))

        observed = len(paused)
        resume_requests = 0
        for owned in paused:
            with self._lock:
                registered = _identity_contains(
                    self._pausables.get(task_id, ()),
                    owned,
                )
                cancel_event = self._events.get(task_id)
                cancelled = bool(cancel_event and cancel_event.is_set())
            if not registered or cancelled or not _pausable_active(owned.operation):
                continue
            if _pausable_pause_status(owned.operation) is True:
                _resume_pausable(owned.operation)
                resume_requests += 1

        deadline = time.monotonic() + self._pause_ack_timeout_seconds
        while True:
            with self._lock:
                current_registered = tuple(self._pausables.get(task_id, ()))
                cancel_event = self._events.get(task_id)
                cancelled = bool(cancel_event and cancel_event.is_set())
                still_waiting = any(
                    _identity_contains(current_registered, owned)
                    and _pausable_pause_status(owned.operation) is not False
                    for owned in paused
                )
            if cancelled or not still_waiting or time.monotonic() >= deadline:
                break
            time.sleep(self._control_poll_interval_seconds)

        with self._lock:
            current_registered = tuple(self._pausables.get(task_id, ()))
            cancel_event = self._events.get(task_id)
            cancelled = bool(cancel_event and cancel_event.is_set())
            missing = sum(
                not _identity_contains(current_registered, owned) for owned in paused
            )
            acknowledgements = 0
            still_paused = 0
            for owned in paused:
                if not _identity_contains(current_registered, owned):
                    continue
                if _pausable_pause_status(owned.operation) is False:
                    acknowledgements += 1
                else:
                    still_paused += 1
            active_resume_acknowledged = bool(
                observed
                and not cancelled
                and missing == 0
                and acknowledgements == observed
                and still_paused == 0
            )
            if active_resume_acknowledged:
                pause_event = self._pause_events.get(task_id)
                if pause_event is not None:
                    pause_event.clear()
                self._paused_pausables.pop(task_id, None)

        return PauseResumeResult(
            task_id=task_id,
            owned_pausable_operations_observed=observed,
            resume_requests=resume_requests,
            resume_acknowledgements=acknowledgements,
            pausable_operations_still_paused=still_paused,
            pausable_operations_missing_on_resume=missing,
            active_resume_acknowledged=active_resume_acknowledged,
        )

    def clear_pause(self, task_id: str) -> None:
        with self._lock:
            event = self._pause_events.get(task_id)
            if event is not None:
                event.clear()
            self._paused_pausables.pop(task_id, None)

    def cancel_task(self, task_id: str, *, reason: str = "") -> CancellationReport:
        with self._lock:
            event = self._events.setdefault(task_id, Event())
            event.set()
            pause_event = self._pause_events.get(task_id)
            if pause_event is not None:
                pause_event.clear()
            self._paused_pausables.pop(task_id, None)
            operations = tuple(self._operations.get(task_id, ()))
            processes = tuple(self._processes.get(task_id, ()))
            cancellables = tuple(self._cancellables.get(task_id, ()))

        terminate_requests = 0
        for owned in processes:
            if owned.process.poll() is None:
                _signal_process(owned.process, signal.SIGTERM)
                terminate_requests += 1

        cancellable_cancel_requests = 0
        for owned in cancellables:
            if _cancellable_active(owned.operation):
                _cancel_cancellable(owned.operation)
                cancellable_cancel_requests += 1

        deadline = time.monotonic() + 1.0
        while _owned_work_active(processes, cancellables):
            if time.monotonic() >= deadline:
                break
            time.sleep(0.01)

        kill_requests = 0
        for owned in processes:
            if owned.process.poll() is None:
                _signal_process(owned.process, signal.SIGKILL)
                kill_requests += 1

        reap_deadline = time.monotonic() + 0.25
        while _owned_work_active(processes, cancellables):
            if time.monotonic() >= reap_deadline:
                break
            time.sleep(0.01)

        return CancellationReport(
            task_id=task_id,
            reason=reason[:2000],
            active_operation_kinds=tuple(
                sorted({item.kind.value for item in operations})
            ),
            owned_processes_observed=len(processes),
            owned_cancellable_operations_observed=len(cancellables),
            terminate_requests=terminate_requests,
            kill_requests=kill_requests,
            cancellable_operation_cancel_requests=cancellable_cancel_requests,
            processes_still_active=sum(item.process.poll() is None for item in processes),
            cancellable_operations_still_active=sum(
                _cancellable_active(item.operation) for item in cancellables
            ),
            cooperative_fallback=(
                bool(operations) and not processes and not cancellables
            ),
        )

    def _begin_operation(
        self,
        task_id: str,
        kind: OwnedOperationKind,
    ) -> _OwnedOperation:
        with self._lock:
            event = self._events.setdefault(task_id, Event())
            if event.is_set():
                raise CancellationRequested("task cancellation requested")
            if task_id in self._paused_pausables:
                raise PauseRequested("task active pause acknowledged")
            owned = _OwnedOperation(kind=kind)
            self._operations.setdefault(task_id, []).append(owned)
            return owned

    def _end_operation(self, task_id: str, owned: _OwnedOperation) -> None:
        with self._lock:
            operations = self._operations.get(task_id, [])
            if _identity_contains(operations, owned):
                operations.remove(owned)
            if not operations:
                self._operations.pop(task_id, None)

    def _start_process(
        self,
        task_id: str,
        kind: OwnedOperationKind,
        factory: Callable[[], subprocess.Popen[str]],
    ) -> _OwnedProcess:
        with self._lock:
            event = self._events.setdefault(task_id, Event())
            if event.is_set():
                raise CancellationRequested("task cancellation requested")
            if task_id in self._paused_pausables:
                raise PauseRequested("task active pause acknowledged")
            owned = _OwnedProcess(kind=kind, process=factory())
            self._processes.setdefault(task_id, []).append(owned)
            return owned

    def _unregister_process(self, task_id: str, owned: _OwnedProcess) -> None:
        with self._lock:
            processes = self._processes.get(task_id, [])
            if owned in processes:
                processes.remove(owned)
            if not processes:
                self._processes.pop(task_id, None)

    def _start_cancellable(
        self,
        task_id: str,
        kind: OwnedOperationKind,
        factory: Callable[[], OwnedCancellableOperation],
    ) -> _OwnedCancellable:
        with self._lock:
            event = self._events.setdefault(task_id, Event())
            if event.is_set():
                raise CancellationRequested("task cancellation requested")
            if task_id in self._paused_pausables:
                raise PauseRequested("task active pause acknowledged")
            owned = _OwnedCancellable(kind=kind, operation=factory())
            self._cancellables.setdefault(task_id, []).append(owned)
            return owned

    def _start_pausable(
        self,
        task_id: str,
        kind: OwnedOperationKind,
        owner: _OwnedOperation,
        factory: Callable[[], OwnedPausableOperation],
    ) -> _OwnedPausable:
        with self._lock:
            cancel_event = self._events.setdefault(task_id, Event())
            if cancel_event.is_set():
                raise CancellationRequested("task cancellation requested")
            pause_event = self._pause_events.setdefault(task_id, Event())
            if pause_event.is_set():
                raise PauseRequested("task pause requested")
            if not _identity_contains(self._operations.get(task_id, ()), owner):
                raise RuntimeError("owned pausable operation lost its active owner")
            operation = factory()
            if not _valid_pausable(operation):
                _cancel_cancellable(operation)
                raise TypeError("owned pausable operation has an invalid control contract")
            owned = _OwnedPausable(kind=kind, operation=operation, owner=owner)
            self._cancellables.setdefault(task_id, []).append(owned)
            self._pausables.setdefault(task_id, []).append(owned)
            return owned

    def _unregister_cancellable(
        self,
        task_id: str,
        owned: _OwnedCancellable,
    ) -> None:
        with self._lock:
            cancellables = self._cancellables.get(task_id, [])
            if owned in cancellables:
                cancellables.remove(owned)
            if not cancellables:
                self._cancellables.pop(task_id, None)

    def _unregister_pausable(
        self,
        task_id: str,
        owned: _OwnedPausable,
    ) -> None:
        with self._lock:
            pausables = self._pausables.get(task_id, [])
            if owned in pausables:
                pausables.remove(owned)
            if not pausables:
                self._pausables.pop(task_id, None)
            cancellables = self._cancellables.get(task_id, [])
            if owned in cancellables:
                cancellables.remove(owned)
            if not cancellables:
                self._cancellables.pop(task_id, None)


def _signal_process(process: subprocess.Popen[str], requested: signal.Signals) -> None:
    try:
        if os.name == "posix":
            os.killpg(process.pid, requested)
        elif requested is signal.SIGTERM:
            process.terminate()
        else:
            process.kill()
    except (OSError, ProcessLookupError):
        return


def _cancellable_active(operation: OwnedCancellableOperation) -> bool:
    try:
        return not operation.done()
    except Exception:
        return True


def _cancel_cancellable(operation: OwnedCancellableOperation) -> None:
    try:
        operation.cancel()
    except Exception:
        return


def _valid_pausable(operation: object) -> bool:
    return all(
        callable(getattr(operation, name, None))
        for name in ("cancel", "done", "pause", "resume", "paused")
    )


def _pausable_active(operation: OwnedPausableOperation) -> bool:
    return _cancellable_active(operation)


def _pausable_pause_status(operation: OwnedPausableOperation) -> bool | None:
    try:
        return bool(operation.paused())
    except Exception:
        return None


def _pause_pausable(operation: OwnedPausableOperation) -> None:
    try:
        operation.pause()
    except Exception:
        return


def _resume_pausable(operation: OwnedPausableOperation) -> None:
    try:
        operation.resume()
    except Exception:
        return


def _identity_contains(items: Iterable[object], expected: object) -> bool:
    return any(item is expected for item in items)


def _same_owned_registrations(
    expected: tuple[object, ...],
    current: tuple[object, ...],
) -> bool:
    return len(expected) == len(current) and all(
        left is right for left, right in zip(expected, current, strict=True)
    )


def _owned_work_active(
    processes: tuple[_OwnedProcess, ...],
    cancellables: tuple[_OwnedCancellable | _OwnedPausable, ...],
) -> bool:
    return any(item.process.poll() is None for item in processes) or any(
        _cancellable_active(item.operation) for item in cancellables
    )
