from __future__ import annotations

import sys
import threading
import time
from pathlib import Path

import pytest

from universal_coding_agent.core.cancellation import (
    CancellationCoordinator,
    CancellationRequested,
)
from universal_coding_agent.core.safe_models import SafeModePolicy, TestProfile
from universal_coding_agent.product.models import ControlState
from universal_coding_agent.product.task_control import TaskControlService
from universal_coding_agent.safe.testing import (
    TRUSTED_TEST_ADAPTER_PATH_ENV,
    TRUSTED_TEST_PAUSABLE_FACTORY_ENV,
    SafeTestRunner,
)

PAUSABLE_TEST_ADAPTER = r'''
import subprocess
import threading
import time
from pathlib import Path
from types import SimpleNamespace


class _Handle:
    def __init__(self, *, argv, cwd, env, timeout_seconds):
        self._argv = list(argv)
        self._cwd = cwd
        self._env = env
        self._timeout_seconds = timeout_seconds
        self._condition = threading.Condition()
        self._pause_requested = False
        self._pause_acknowledged = False
        self._cancel_requested = False
        self._done = threading.Event()
        self._result = None
        self._error = None
        self._thread = threading.Thread(target=self._run)
        self._thread.start()

    def _run(self):
        try:
            root = Path(self._cwd)
            root.joinpath("adapter-started").write_text("started")
            for progress in range(1, 31):
                with self._condition:
                    while self._pause_requested and not self._cancel_requested:
                        self._pause_acknowledged = True
                        self._condition.notify_all()
                        self._condition.wait()
                    self._pause_acknowledged = False
                    if self._cancel_requested:
                        return
                root.joinpath("adapter-progress").write_text(str(progress))
                time.sleep(0.01)
            completed = subprocess.run(
                self._argv,
                cwd=self._cwd,
                env=self._env,
                capture_output=True,
                text=True,
                timeout=self._timeout_seconds,
                check=False,
            )
            self._result = SimpleNamespace(
                returncode=completed.returncode,
                stdout=completed.stdout,
                stderr=completed.stderr,
            )
        except BaseException as exc:
            self._error = exc
        finally:
            self._done.set()
            with self._condition:
                self._condition.notify_all()

    def result(self, *, timeout_seconds):
        if not self._done.wait(timeout=timeout_seconds):
            self.cancel()
            raise TimeoutError("trusted test timed out")
        if self._cancel_requested:
            raise RuntimeError("trusted test cancelled")
        if self._error is not None:
            raise self._error
        return self._result

    def pause(self):
        with self._condition:
            self._pause_requested = True
            self._condition.notify_all()

    def resume(self):
        with self._condition:
            self._pause_requested = False
            self._pause_acknowledged = False
            self._condition.notify_all()

    def paused(self):
        with self._condition:
            return self._pause_acknowledged

    def cancel(self):
        with self._condition:
            self._cancel_requested = True
            self._pause_requested = False
            self._pause_acknowledged = False
            self._condition.notify_all()
        self._done.set()

    def done(self):
        return self._done.is_set()


def create_pausable_test(**kwargs):
    return _Handle(**kwargs)
'''


def _write_adapter(tmp_path: Path, source: str = PAUSABLE_TEST_ADAPTER) -> Path:
    path = tmp_path / "trusted_test_adapter.py"
    path.write_text(source, encoding="utf-8")
    return path


def _policy() -> SafeModePolicy:
    return SafeModePolicy(
        profiles=(
            TestProfile(
                profile_id="cooperative-test",
                argv=(
                    sys.executable,
                    "-c",
                    "from pathlib import Path; Path('profile-ran').write_text('yes')",
                ),
                timeout_seconds=10,
            ),
        )
    )


def _wait_for_progress(path: Path, minimum: int = 3) -> int:
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        try:
            value = int(path.read_text(encoding="utf-8"))
        except (FileNotFoundError, ValueError):
            value = 0
        if value >= minimum:
            return value
        time.sleep(0.005)
    raise AssertionError("timed out waiting for trusted-test adapter progress")


def test_owned_pausable_trusted_test_stops_progress_and_resumes(
    tmp_path: Path,
) -> None:
    coordinator = CancellationCoordinator(
        pause_ack_timeout_seconds=0.2,
        control_poll_interval_seconds=0.001,
    )
    control = TaskControlService(tmp_path / "control.sqlite", cancellation=coordinator)
    task_id = "pausable-trusted-test"
    control.ensure_task(task_id)
    runner = SafeTestRunner(
        adapter_module_path=_write_adapter(tmp_path),
        pausable_factory_name="create_pausable_test",
    )
    results = []
    errors: list[BaseException] = []

    def run_test() -> None:
        try:
            results.extend(
                runner.run_profiles(
                    tmp_path,
                    _policy(),
                    ("cooperative-test",),
                    cancellation=control.cancellation.signal(task_id),
                )
            )
        except BaseException as exc:
            errors.append(exc)

    worker = threading.Thread(target=run_test)
    worker.start()
    progress_path = tmp_path / "adapter-progress"
    _wait_for_progress(progress_path)

    paused = control.pause_task(task_id, reason="pause trusted test")
    pause_report = control.pause_report(task_id)
    paused_progress = int(progress_path.read_text(encoding="utf-8"))
    time.sleep(0.1)

    assert paused.state is ControlState.PAUSED
    assert int(progress_path.read_text(encoding="utf-8")) == paused_progress
    assert pause_report is not None
    assert pause_report.active_operation_kinds == ("test",)
    assert pause_report.owned_pausable_operations_observed == 1
    assert pause_report.unsupported_active_operations_observed == 0
    assert pause_report.active_pause_acknowledged is True

    resumed = control.resume_task(task_id)
    resumed_report = control.pause_report(task_id)
    worker.join(timeout=5)

    assert resumed.state is ControlState.RUNNING
    assert resumed_report is not None
    assert resumed_report.active_resume_acknowledged is True
    assert worker.is_alive() is False
    assert errors == []
    assert len(results) == 1
    assert results[0].passed is True
    assert (tmp_path / "profile-ran").read_text(encoding="utf-8") == "yes"
    control.close()


def test_cancel_supersedes_acknowledged_trusted_test_pause(tmp_path: Path) -> None:
    coordinator = CancellationCoordinator(
        pause_ack_timeout_seconds=0.2,
        control_poll_interval_seconds=0.001,
    )
    control = TaskControlService(tmp_path / "cancel.sqlite", cancellation=coordinator)
    task_id = "cancel-pausable-trusted-test"
    control.ensure_task(task_id)
    runner = SafeTestRunner(
        adapter_module_path=_write_adapter(tmp_path),
        pausable_factory_name="create_pausable_test",
    )
    errors: list[BaseException] = []

    def run_test() -> None:
        try:
            runner.run_profiles(
                tmp_path,
                _policy(),
                ("cooperative-test",),
                cancellation=control.cancellation.signal(task_id),
            )
        except BaseException as exc:
            errors.append(exc)

    worker = threading.Thread(target=run_test)
    worker.start()
    _wait_for_progress(tmp_path / "adapter-progress")
    assert control.pause_task(task_id).state is ControlState.PAUSED

    cancelled = control.cancel_task(task_id, reason="cancel supersedes pause")
    worker.join(timeout=5)
    report = control.cancellation_report(task_id)

    assert cancelled.state is ControlState.CANCEL_REQUESTED
    assert worker.is_alive() is False
    assert len(errors) == 1
    assert isinstance(errors[0], CancellationRequested)
    assert report is not None
    assert report.active_operation_kinds == ("test",)
    assert report.owned_processes_observed == 0
    assert report.owned_cancellable_operations_observed == 1
    assert report.cancellable_operation_cancel_requests == 1
    assert report.cancellable_operations_still_active == 0
    control.close()


def test_trusted_test_adapter_environment_requires_complete_configuration(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(TRUSTED_TEST_ADAPTER_PATH_ENV, str(_write_adapter(tmp_path)))
    monkeypatch.delenv(TRUSTED_TEST_PAUSABLE_FACTORY_ENV, raising=False)

    with pytest.raises(ValueError, match="configuration is incomplete"):
        SafeTestRunner.from_environment()


def test_trusted_test_adapter_loads_complete_environment_configuration(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = _write_adapter(tmp_path)
    monkeypatch.setenv(TRUSTED_TEST_ADAPTER_PATH_ENV, str(path))
    monkeypatch.setenv(
        TRUSTED_TEST_PAUSABLE_FACTORY_ENV,
        "create_pausable_test",
    )

    runner = SafeTestRunner.from_environment()

    assert runner.adapter_module_path == path.resolve()
    assert runner.pausable_factory_name == "create_pausable_test"


def test_trusted_test_adapter_rejects_invalid_handle(tmp_path: Path) -> None:
    path = _write_adapter(
        tmp_path,
        """
class InvalidHandle:
    def cancel(self):
        pass

def create_pausable_test(**kwargs):
    return InvalidHandle()
""",
    )
    runner = SafeTestRunner(
        adapter_module_path=path,
        pausable_factory_name="create_pausable_test",
    )
    signal = CancellationCoordinator().signal("invalid-test-handle")

    with pytest.raises(RuntimeError, match="invalid handle"):
        runner.run_profiles(
            tmp_path,
            _policy(),
            ("cooperative-test",),
            cancellation=signal,
        )


def test_trusted_test_adapter_rejects_invalid_result(tmp_path: Path) -> None:
    path = _write_adapter(
        tmp_path,
        """
from types import SimpleNamespace

class InvalidResultHandle:
    def __init__(self):
        self._done = False

    def result(self, *, timeout_seconds):
        self._done = True
        return SimpleNamespace(returncode="zero", stdout="", stderr="")

    def cancel(self):
        self._done = True

    def done(self):
        return self._done

    def pause(self):
        pass

    def resume(self):
        pass

    def paused(self):
        return False

def create_pausable_test(**kwargs):
    return InvalidResultHandle()
""",
    )
    runner = SafeTestRunner(
        adapter_module_path=path,
        pausable_factory_name="create_pausable_test",
    )

    with pytest.raises(RuntimeError, match="invalid result"):
        runner.run_profiles(
            tmp_path,
            _policy(),
            ("cooperative-test",),
            cancellation=CancellationCoordinator().signal("invalid-test-result"),
        )
