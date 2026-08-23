from __future__ import annotations

import sqlite3
import subprocess
import sys
import threading
import time
from pathlib import Path

from pydantic import BaseModel

from universal_coding_agent.core.cancellation import (
    CancellationCoordinator,
    CancellationRequested,
    OwnedOperationKind,
)
from universal_coding_agent.core.models import ModelRequest, ModelResponse
from universal_coding_agent.core.safe_models import SafeModePolicy, TestProfile
from universal_coding_agent.orchestration.structured_output import (
    StructuredOutputError,
    invoke_structured,
)
from universal_coding_agent.product.task_control import TaskControlService
from universal_coding_agent.providers.host_chat import HostChatCompletionsProvider
from universal_coding_agent.providers.host_subprocess import HostSubprocessProvider
from universal_coding_agent.safe.testing import SafeTestRunner


def _wait_for(path: Path) -> None:
    deadline = time.monotonic() + 5
    while not path.exists():
        if time.monotonic() >= deadline:
            raise AssertionError(f"timed out waiting for {path.name}")
        time.sleep(0.01)


def test_cancel_terminates_owned_trusted_test_and_persists_report(tmp_path: Path) -> None:
    marker = tmp_path / "test-started"
    policy = SafeModePolicy(
        profiles=(
            TestProfile(
                profile_id="slow-trusted-test",
                argv=(
                    sys.executable,
                    "-c",
                    (
                        "from pathlib import Path; import time; "
                        "Path('test-started').write_text('started'); time.sleep(30)"
                    ),
                ),
                timeout_seconds=60,
            ),
        )
    )
    control = TaskControlService(tmp_path / "control.sqlite")
    signal = control.cancellation.signal("cancel-test-task")
    errors: list[BaseException] = []

    def run_test() -> None:
        try:
            SafeTestRunner().run_profiles(
                tmp_path,
                policy,
                ("slow-trusted-test",),
                cancellation=signal,
            )
        except BaseException as exc:  # captured for assertion in the parent thread
            errors.append(exc)

    worker = threading.Thread(target=run_test)
    worker.start()
    _wait_for(marker)
    control.cancel_task("cancel-test-task", reason="operator cancelled test")
    worker.join(timeout=5)

    report = control.cancellation_report("cancel-test-task")
    assert worker.is_alive() is False
    assert len(errors) == 1
    assert isinstance(errors[0], CancellationRequested)
    assert report is not None
    assert report.active_operation_kinds == ("test",)
    assert report.owned_processes_observed == 1
    assert report.owned_cancellable_operations_observed == 0
    assert report.terminate_requests == 1
    assert report.cancellable_operation_cancel_requests == 0
    assert report.processes_still_active == 0
    assert report.cancellable_operations_still_active == 0
    assert report.cooperative_fallback is False
    control.close()

    reopened = TaskControlService(tmp_path / "control.sqlite")
    persisted = reopened.cancellation_report("cancel-test-task")
    assert persisted == report
    reopened.close()


def test_cancel_terminates_owned_host_provider_process(tmp_path: Path, monkeypatch) -> None:
    marker = tmp_path / "provider-started"
    module = tmp_path / "host_client.py"
    module.write_text(
        """
import os
import time
from pathlib import Path
from types import SimpleNamespace

class _Completions:
    def create(self, **kwargs):
        Path(os.environ["UCA_CANCEL_MARKER"]).write_text("started")
        time.sleep(30)
        return SimpleNamespace(
            model="never-returned",
            choices=[SimpleNamespace(
                message=SimpleNamespace(content='{"status":"OK"}'),
                finish_reason="stop",
            )],
            usage=None,
        )

class _Client:
    def __init__(self):
        self.chat = SimpleNamespace(completions=_Completions())

def create_client():
    return _Client()

def get_configured_model_or_deployment():
    return SimpleNamespace(deployment="fixture")
""",
        encoding="utf-8",
    )
    monkeypatch.setenv("UCA_CANCEL_MARKER", str(marker))
    provider = HostSubprocessProvider(module, sys.executable)
    coordinator = CancellationCoordinator()
    signal = coordinator.signal("cancel-provider-task")
    errors: list[BaseException] = []

    def invoke() -> None:
        try:
            provider.invoke_cancellable(
                ModelRequest(
                    role="implementer",
                    system_prompt="Return JSON.",
                    user_prompt="Return status OK.",
                    response_schema={"type": "object"},
                ),
                signal,
            )
        except BaseException as exc:  # captured for assertion in the parent thread
            errors.append(exc)

    worker = threading.Thread(target=invoke)
    worker.start()
    _wait_for(marker)
    report = coordinator.cancel_task(
        "cancel-provider-task",
        reason="operator cancelled provider",
    )
    worker.join(timeout=5)

    assert worker.is_alive() is False
    assert len(errors) == 1
    assert isinstance(errors[0], CancellationRequested)
    assert report.owned_processes_observed == 1
    assert report.owned_cancellable_operations_observed == 0
    assert report.terminate_requests == 1
    assert report.processes_still_active == 0


def test_cancel_terminates_owned_host_chat_handle_and_persists_report(
    tmp_path: Path,
    monkeypatch,
) -> None:
    marker = tmp_path / "host-chat-started"
    module = tmp_path / "host_chat_client.py"
    module.write_text(
        """
import os
import threading
from pathlib import Path
from types import SimpleNamespace

class _Completions:
    def create(self, **kwargs):
        raise AssertionError("direct completion path must not be used")

class _Client:
    def __init__(self):
        self.chat = SimpleNamespace(completions=_Completions())

class _Handle:
    def __init__(self):
        self._done = threading.Event()
        self._cancelled = False
        Path(os.environ["UCA_CANCEL_MARKER"]).write_text("started")

    def result(self):
        self._done.wait(timeout=30)
        if self._cancelled:
            raise RuntimeError("cancelled")
        choice = SimpleNamespace(
            message=SimpleNamespace(content='{"status":"late"}'),
            finish_reason="stop",
        )
        return SimpleNamespace(model="fixture", choices=[choice], usage=None)

    def cancel(self):
        self._cancelled = True
        self._done.set()

    def done(self):
        return self._done.is_set()

def create_client():
    return _Client()

def get_configured_model_or_deployment():
    return SimpleNamespace(deployment="fixture")

def create_cancellable_completion(**kwargs):
    return _Handle()
""",
        encoding="utf-8",
    )
    monkeypatch.setenv("UCA_CANCEL_MARKER", str(marker))
    provider = HostChatCompletionsProvider(
        module,
        cancellable_completion_factory_name="create_cancellable_completion",
    )
    control = TaskControlService(tmp_path / "host-chat-control.sqlite")
    signal = control.cancellation.signal("cancel-host-chat-task")
    errors: list[BaseException] = []

    class Payload(BaseModel):
        status: str

    def invoke() -> None:
        try:
            invoke_structured(
                provider,
                ModelRequest(
                    role="implementer",
                    system_prompt="Return JSON.",
                    user_prompt="Return status.",
                ),
                Payload,
                cancellation=signal,
            )
        except BaseException as exc:  # captured for assertion in the parent thread
            errors.append(exc)

    worker = threading.Thread(target=invoke)
    worker.start()
    _wait_for(marker)
    control.cancel_task("cancel-host-chat-task", reason="operator cancelled remote call")
    worker.join(timeout=5)

    report = control.cancellation_report("cancel-host-chat-task")
    assert worker.is_alive() is False
    assert len(errors) == 1
    assert isinstance(errors[0], StructuredOutputError)
    assert errors[0].code == "control_cancelled"  # type: ignore[union-attr]
    assert report is not None
    assert report.active_operation_kinds == ("provider",)
    assert report.owned_processes_observed == 0
    assert report.owned_cancellable_operations_observed == 1
    assert report.terminate_requests == 0
    assert report.kill_requests == 0
    assert report.cancellable_operation_cancel_requests == 1
    assert report.processes_still_active == 0
    assert report.cancellable_operations_still_active == 0
    assert report.cooperative_fallback is False
    control.close()

    reopened = TaskControlService(tmp_path / "host-chat-control.sqlite")
    assert reopened.cancellation_report("cancel-host-chat-task") == report
    reopened.close()


def test_cancelled_signal_prevents_new_owned_work(tmp_path: Path) -> None:
    coordinator = CancellationCoordinator()
    signal = coordinator.signal("cancel-before-work")
    report = coordinator.cancel_task("cancel-before-work", reason="stop")

    assert report.owned_processes_observed == 0
    try:
        with signal.operation(OwnedOperationKind.PROVIDER):
            raise AssertionError("cancelled work must not start")
    except CancellationRequested:
        pass


def test_in_process_provider_uses_cooperative_cancellation_fallback() -> None:
    started = threading.Event()
    release = threading.Event()

    class Payload(BaseModel):
        status: str

    class BlockingProvider:
        def invoke(self, _request: ModelRequest) -> ModelResponse:
            started.set()
            release.wait(timeout=5)
            return ModelResponse(structured={"status": "late"})

    coordinator = CancellationCoordinator()
    signal = coordinator.signal("cooperative-provider")
    errors: list[BaseException] = []

    def invoke() -> None:
        try:
            invoke_structured(
                BlockingProvider(),  # type: ignore[arg-type]
                ModelRequest(
                    role="implementer",
                    system_prompt="Return JSON.",
                    user_prompt="Return status.",
                ),
                Payload,
                cancellation=signal,
            )
        except BaseException as exc:  # captured for assertion in the parent thread
            errors.append(exc)

    worker = threading.Thread(target=invoke)
    worker.start()
    assert started.wait(timeout=5)
    report = coordinator.cancel_task("cooperative-provider", reason="stop")
    release.set()
    worker.join(timeout=5)

    assert worker.is_alive() is False
    assert len(errors) == 1
    assert isinstance(errors[0], StructuredOutputError)
    assert errors[0].code == "control_cancelled"  # type: ignore[union-attr]
    assert report.active_operation_kinds == ("provider",)
    assert report.owned_processes_observed == 0
    assert report.cooperative_fallback is True


def test_cancel_escalates_when_owned_process_ignores_termination(tmp_path: Path) -> None:
    marker = tmp_path / "ignoring-process-started"
    coordinator = CancellationCoordinator()
    signal = coordinator.signal("kill-escalation")
    errors: list[BaseException] = []

    def start_process() -> subprocess.Popen[str]:
        return subprocess.Popen(
            (
                sys.executable,
                "-c",
                (
                    "import signal, time; from pathlib import Path; "
                    "signal.signal(signal.SIGTERM, signal.SIG_IGN); "
                    f"Path({str(marker)!r}).write_text('started'); time.sleep(30)"
                ),
            ),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
        )

    def wait_for_process() -> None:
        try:
            with signal.operation(OwnedOperationKind.TEST):
                with signal.owned_process(
                    OwnedOperationKind.TEST,
                    start_process,
                ) as process:
                    process.communicate(timeout=60)
        except BaseException as exc:  # captured for assertion in the parent thread
            errors.append(exc)

    worker = threading.Thread(target=wait_for_process)
    worker.start()
    _wait_for(marker)
    report = coordinator.cancel_task("kill-escalation", reason="force stop")
    worker.join(timeout=5)

    assert worker.is_alive() is False
    assert len(errors) == 1
    assert isinstance(errors[0], CancellationRequested)
    assert report.terminate_requests == 1
    assert report.kill_requests == 1
    assert report.processes_still_active == 0


def test_unresponsive_owned_cancellable_operation_is_reported_active() -> None:
    started = threading.Event()
    release = threading.Event()
    coordinator = CancellationCoordinator()
    signal = coordinator.signal("unresponsive-cancellable")
    errors: list[BaseException] = []

    class UnresponsiveOperation:
        def result(self) -> None:
            started.set()
            release.wait(timeout=5)

        def cancel(self) -> None:
            return

        def done(self) -> bool:
            return release.is_set()

    operation = UnresponsiveOperation()

    def invoke() -> None:
        try:
            with signal.operation(OwnedOperationKind.PROVIDER):
                with signal.owned_cancellable_operation(
                    OwnedOperationKind.PROVIDER,
                    lambda: operation,
                ):
                    operation.result()
        except BaseException as exc:  # captured for assertion in the parent thread
            errors.append(exc)

    worker = threading.Thread(target=invoke)
    worker.start()
    assert started.wait(timeout=5)
    report = coordinator.cancel_task("unresponsive-cancellable", reason="stop")

    assert report.owned_cancellable_operations_observed == 1
    assert report.cancellable_operation_cancel_requests == 1
    assert report.cancellable_operations_still_active == 1
    assert report.cooperative_fallback is False

    release.set()
    worker.join(timeout=5)
    assert worker.is_alive() is False
    assert len(errors) == 1
    assert isinstance(errors[0], CancellationRequested)


def test_task_control_migrates_p12a_cancellation_report_schema(tmp_path: Path) -> None:
    database = tmp_path / "legacy-control.sqlite"
    connection = sqlite3.connect(database)
    connection.execute(
        """
        CREATE TABLE cancellation_reports (
            task_id TEXT PRIMARY KEY,
            reason TEXT NOT NULL,
            active_operation_kinds TEXT NOT NULL,
            owned_processes_observed INTEGER NOT NULL,
            terminate_requests INTEGER NOT NULL,
            kill_requests INTEGER NOT NULL,
            processes_still_active INTEGER NOT NULL,
            cooperative_fallback INTEGER NOT NULL
        )
        """
    )
    connection.commit()
    connection.close()

    control = TaskControlService(database)
    control.cancel_task("migrated-task", reason="migration check")
    report = control.cancellation_report("migrated-task")
    columns = {
        str(row[1])
        for row in control.connection.execute(
            "PRAGMA table_info(cancellation_reports)"
        ).fetchall()
    }

    assert report is not None
    assert report.owned_cancellable_operations_observed == 0
    assert report.cancellable_operation_cancel_requests == 0
    assert report.cancellable_operations_still_active == 0
    assert {
        "owned_cancellable_operations_observed",
        "cancellable_operation_cancel_requests",
        "cancellable_operations_still_active",
    }.issubset(columns)
    control.close()
