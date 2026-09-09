from __future__ import annotations

import threading
import time
from pathlib import Path

from test_safe_control import _git, _source, _task
from test_trusted_test_pause import PAUSABLE_TEST_ADAPTER

from universal_coding_agent.product.models import ControlState
from universal_coding_agent.providers.fake import FakeModelProvider
from universal_coding_agent.safe.testing import SafeTestRunner
from universal_coding_agent.safe_service import SafeAgentService


def test_safe_service_actively_pauses_owned_trusted_test_and_preserves_source(
    tmp_path: Path,
) -> None:
    source, base_sha = _source(tmp_path)
    adapter = tmp_path / "service_trusted_test_adapter.py"
    adapter.write_text(
        PAUSABLE_TEST_ADAPTER.replace(
            "root = Path(self._cwd)",
            (
                "root = Path(__file__).parent / 'service-markers'\n"
                "            root.mkdir(exist_ok=True)"
            ),
        ),
        encoding="utf-8",
    )
    state_root = tmp_path / "state"
    runner = SafeTestRunner(
        adapter_module_path=adapter,
        pausable_factory_name="create_pausable_test",
    )
    service = SafeAgentService.create(
        state_root,
        FakeModelProvider(),
        allow_local_sources=True,
        test_runner=runner,
    )
    task = _task(source, base_sha, "safe-control-pausable-test")
    results: list[dict] = []
    errors: list[BaseException] = []
    try:
        service.run(task)

        def resume_scope() -> None:
            try:
                results.append(service.resume(task.thread_id, True))
            except BaseException as exc:
                errors.append(exc)

        worker = threading.Thread(target=resume_scope)
        worker.start()
        progress_path = tmp_path / "service-markers" / "adapter-progress"
        deadline = time.monotonic() + 5
        while not progress_path.is_file():
            if time.monotonic() >= deadline:
                raise AssertionError("timed out waiting for trusted-test adapter")
            time.sleep(0.005)

        paused = service.control.pause_task(
            task.task_id,
            reason="operator paused active trusted test",
        )
        report = service.control.pause_report(task.task_id)
        paused_progress = progress_path.read_text(encoding="utf-8")
        time.sleep(0.1)

        assert paused.state is ControlState.PAUSED
        assert progress_path.read_text(encoding="utf-8") == paused_progress
        assert report is not None
        assert report.active_operation_kinds == ("test",)
        assert report.active_pause_acknowledged is True

        assert service.control.resume_task(task.task_id).state is ControlState.RUNNING
        worker.join(timeout=5)

        assert worker.is_alive() is False
        assert errors == []
        assert len(results) == 1
        assert results[0]["status"] == "completed"
        assert "return 42" in (source / "app.py").read_text(encoding="utf-8")
        assert _git(source, "status", "--porcelain") == ""
    finally:
        service.close()
