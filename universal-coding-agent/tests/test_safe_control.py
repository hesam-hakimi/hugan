from __future__ import annotations

import subprocess
import sys
import threading
import time
from pathlib import Path

from universal_coding_agent.core.models import RepositorySpec
from universal_coding_agent.core.safe_models import (
    ApprovedChangeManifest,
    ChangeOperation,
    ChangeScopeEntry,
    SafeModePolicy,
    SafeTaskRequest,
    TestProfile,
)
from universal_coding_agent.product.models import ControlState
from universal_coding_agent.providers.fake import FakeModelProvider
from universal_coding_agent.safe_service import SafeAgentService


def _git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _source(tmp_path: Path) -> tuple[Path, str]:
    source = tmp_path / "source"
    source.mkdir()
    _git(source, "init", "-b", "main")
    _git(source, "config", "user.email", "test@example.test")
    _git(source, "config", "user.name", "Safe Control Test")
    (source / "app.py").write_text("def answer():\n    return 42\n", encoding="utf-8")
    _git(source, "add", "app.py")
    _git(source, "commit", "-m", "fixture")
    return source, _git(source, "rev-parse", "HEAD")


def _task(source: Path, base_sha: str, task_id: str) -> SafeTaskRequest:
    return SafeTaskRequest(
        task_id=task_id,
        thread_id=f"{task_id}-thread",
        title="Controlled Safe Mode fixture",
        objective="Change the approved answer from 42 to 43.",
        repository=RepositorySpec(url=str(source), base_ref="main"),
        manifest=ApprovedChangeManifest(
            base_sha=base_sha,
            plan_hash="b" * 64,
            allowed_changes=(
                ChangeScopeEntry(
                    path="app.py",
                    operation=ChangeOperation.MODIFY,
                    purpose="Apply the approved fixture change.",
                ),
            ),
            test_profiles=("python-check",),
            acceptance_criteria=("The approved answer is 43.",),
        ),
        policy=SafeModePolicy(
            profiles=(
                TestProfile(
                    profile_id="python-check",
                    argv=(
                        sys.executable,
                        "-c",
                        (
                            "from pathlib import Path; "
                            "assert 'return 43' in Path('app.py').read_text()"
                        ),
                    ),
                ),
            )
        ),
    )


def test_cancel_after_scope_approval_prevents_implementer_and_writes(tmp_path: Path) -> None:
    source, base_sha = _source(tmp_path)
    implementer_called = False

    def implementer(_request):
        nonlocal implementer_called
        implementer_called = True
        raise AssertionError("implementer must not run after cancellation")

    state_root = tmp_path / "state"
    service = SafeAgentService.create(
        state_root,
        FakeModelProvider(handlers={"implementer": implementer}),
        allow_local_sources=True,
    )
    task = _task(source, base_sha, "safe-control-cancel")
    try:
        service.run(task)
        service.cancel(task.thread_id, reason="operator stopped task")
        final = service.resume(task.thread_id, True)
        report = service.artifacts.read_json(final["final_report_ref"])
        control = service.control.get_task(task.task_id)

        assert final["status"] == "blocked"
        assert "control:cancelled" in report["safe_errors"]
        assert implementer_called is False
        assert control is not None
        assert control.state is ControlState.CANCELLED
        sandbox = state_root / "sandboxes" / task.task_id / "repo"
        assert "return 42" in (sandbox / "app.py").read_text(encoding="utf-8")
        assert "return 42" in (source / "app.py").read_text(encoding="utf-8")
        assert _git(source, "status", "--porcelain") == ""
    finally:
        service.close()


def test_pause_before_implementation_requires_explicit_resume(tmp_path: Path) -> None:
    source, base_sha = _source(tmp_path)
    state_root = tmp_path / "state"
    service = SafeAgentService.create(
        state_root,
        FakeModelProvider(),
        allow_local_sources=True,
    )
    task = _task(source, base_sha, "safe-control-pause")
    try:
        service.run(task)
        service.pause(task.thread_id, reason="review requested")
        service.resume(task.thread_id, True)

        paused = service.state(task.thread_id)
        assert paused["next"] == ["implement"]
        assert paused["control"] is not None
        assert paused["control"]["state"] == "paused"
        sandbox = state_root / "sandboxes" / task.task_id / "repo"
        assert "return 42" in (sandbox / "app.py").read_text(encoding="utf-8")

        final = service.resume_control(task.thread_id, action="resume")
        assert final["status"] == "completed"
        assert final["reviewer_verdict"] == "PASS"
        control = service.control.get_task(task.task_id)
        assert control is not None
        assert control.state is ControlState.COMPLETED
        assert "return 43" in (sandbox / "app.py").read_text(encoding="utf-8")
        assert "return 42" in (source / "app.py").read_text(encoding="utf-8")
        assert _git(source, "status", "--porcelain") == ""
    finally:
        service.close()


def test_cancel_during_trusted_tests_terminates_process_and_preserves_source(
    tmp_path: Path,
) -> None:
    source, base_sha = _source(tmp_path)
    state_root = tmp_path / "state"
    service = SafeAgentService.create(
        state_root,
        FakeModelProvider(),
        allow_local_sources=True,
    )
    task = _task(source, base_sha, "safe-control-active-test")
    task = task.model_copy(
        update={
            "policy": SafeModePolicy(
                profiles=(
                    TestProfile(
                        profile_id="python-check",
                        argv=(
                            sys.executable,
                            "-c",
                            (
                                "from pathlib import Path; import time; "
                                "assert 'return 43' in Path('app.py').read_text(); "
                                "Path('test-started').write_text('started'); "
                                "time.sleep(30)"
                            ),
                        ),
                        timeout_seconds=60,
                    ),
                )
            )
        }
    )
    results: list[dict] = []
    errors: list[BaseException] = []
    try:
        service.run(task)

        def resume_scope() -> None:
            try:
                results.append(service.resume(task.thread_id, True))
            except BaseException as exc:  # captured for assertion in the parent thread
                errors.append(exc)

        worker = threading.Thread(target=resume_scope)
        worker.start()
        marker = state_root / "sandboxes" / task.task_id / "repo" / "test-started"
        deadline = time.monotonic() + 5
        while not marker.exists():
            if time.monotonic() >= deadline:
                raise AssertionError("timed out waiting for trusted test process")
            time.sleep(0.01)

        service.control.cancel_task(task.task_id, reason="operator stopped active test")
        worker.join(timeout=5)

        assert worker.is_alive() is False
        assert errors == []
        assert len(results) == 1
        final = results[0]
        report = service.artifacts.read_json(final["final_report_ref"])
        cancellation = service.control.cancellation_report(task.task_id)
        assert final["status"] == "blocked"
        assert "control:cancelled" in report["safe_errors"]
        assert cancellation is not None
        assert cancellation.active_operation_kinds == ("test",)
        assert cancellation.owned_processes_observed == 1
        assert cancellation.terminate_requests == 1
        assert cancellation.processes_still_active == 0
        assert "return 42" in (source / "app.py").read_text(encoding="utf-8")
        assert _git(source, "status", "--porcelain") == ""
    finally:
        service.close()
