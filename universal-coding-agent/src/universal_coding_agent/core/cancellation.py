from __future__ import annotations

import os
import signal
import subprocess
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from enum import StrEnum
from threading import Event, RLock
from typing import Any


class CancellationRequested(RuntimeError):
    """Raised when cancelled work reaches a cooperative checkpoint."""


class OwnedOperationKind(StrEnum):
    PROVIDER = "provider"
    TEST = "test"


@dataclass(frozen=True)
class CancellationReport:
    task_id: str
    reason: str
    active_operation_kinds: tuple[str, ...]
    owned_processes_observed: int
    terminate_requests: int
    kill_requests: int
    processes_still_active: int
    cooperative_fallback: bool

    def to_json(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class _OwnedProcess:
    kind: OwnedOperationKind
    process: subprocess.Popen[str]


class CancellationSignal:
    """Task-scoped signal that can own only explicitly registered child processes."""

    def __init__(self, coordinator: CancellationCoordinator, task_id: str) -> None:
        self._coordinator = coordinator
        self.task_id = task_id

    @property
    def cancelled(self) -> bool:
        return self._coordinator.is_cancelled(self.task_id)

    def raise_if_cancelled(self) -> None:
        if self.cancelled:
            raise CancellationRequested("task cancellation requested")

    @contextmanager
    def operation(self, kind: OwnedOperationKind) -> Iterator[None]:
        self._coordinator._begin_operation(self.task_id, kind)
        try:
            self.raise_if_cancelled()
            yield
            self.raise_if_cancelled()
        finally:
            self._coordinator._end_operation(self.task_id, kind)

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


class CancellationCoordinator:
    """Coordinate cooperative checks and termination of UCA-owned child processes."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._events: dict[str, Event] = {}
        self._operations: dict[str, list[OwnedOperationKind]] = {}
        self._processes: dict[str, list[_OwnedProcess]] = {}

    def signal(self, task_id: str) -> CancellationSignal:
        with self._lock:
            self._events.setdefault(task_id, Event())
        return CancellationSignal(self, task_id)

    def is_cancelled(self, task_id: str) -> bool:
        with self._lock:
            event = self._events.get(task_id)
            return bool(event and event.is_set())

    def cancel_task(self, task_id: str, *, reason: str = "") -> CancellationReport:
        with self._lock:
            event = self._events.setdefault(task_id, Event())
            event.set()
            operations = tuple(self._operations.get(task_id, ()))
            processes = tuple(self._processes.get(task_id, ()))

        terminate_requests = 0
        for owned in processes:
            if owned.process.poll() is None:
                _signal_process(owned.process, signal.SIGTERM)
                terminate_requests += 1

        deadline = time.monotonic() + 1.0
        while any(item.process.poll() is None for item in processes):
            if time.monotonic() >= deadline:
                break
            time.sleep(0.01)

        kill_requests = 0
        for owned in processes:
            if owned.process.poll() is None:
                _signal_process(owned.process, signal.SIGKILL)
                kill_requests += 1

        reap_deadline = time.monotonic() + 0.25
        while any(item.process.poll() is None for item in processes):
            if time.monotonic() >= reap_deadline:
                break
            time.sleep(0.01)

        return CancellationReport(
            task_id=task_id,
            reason=reason[:2000],
            active_operation_kinds=tuple(sorted({item.value for item in operations})),
            owned_processes_observed=len(processes),
            terminate_requests=terminate_requests,
            kill_requests=kill_requests,
            processes_still_active=sum(item.process.poll() is None for item in processes),
            cooperative_fallback=bool(operations) and not processes,
        )

    def _begin_operation(self, task_id: str, kind: OwnedOperationKind) -> None:
        with self._lock:
            self._events.setdefault(task_id, Event())
            self._operations.setdefault(task_id, []).append(kind)

    def _end_operation(self, task_id: str, kind: OwnedOperationKind) -> None:
        with self._lock:
            operations = self._operations.get(task_id, [])
            if kind in operations:
                operations.remove(kind)
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
