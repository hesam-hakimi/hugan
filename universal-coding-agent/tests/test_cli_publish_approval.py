import json
from pathlib import Path

from universal_coding_agent import cli
from universal_coding_agent.cli import main, parser


def test_safe_cli_can_require_exact_publish_approval() -> None:
    arguments = parser().parse_args(
        [
            "safe",
            "--repository",
            "https://example.test/repository.git",
            "--ref",
            "main",
            "--task-file",
            "task.md",
            "--scope-file",
            "scope.json",
            "--policy-file",
            "policy.json",
            "--require-publish-approval",
        ]
    )

    assert arguments.require_publish_approval is True


def test_safe_publish_resume_requires_exact_patch_hash_argument() -> None:
    arguments = parser().parse_args(
        [
            "safe-publish-resume",
            "--thread-id",
            "safe-task-123",
            "--decision",
            "approve",
            "--patch-sha256",
            "a" * 64,
        ]
    )

    assert arguments.command == "safe-publish-resume"
    assert arguments.decision == "approve"
    assert arguments.patch_sha256 == "a" * 64


def test_safe_source_publish_parses_one_bounded_exact_publication() -> None:
    arguments = parser().parse_args(
        [
            "--state-root",
            "/tmp/uca-state",
            "--source-control-factory",
            "trusted_source_control:create_adapter",
            "safe-source-publish",
            "--task-id",
            "safe-task-123",
            "--approval-sha256",
            "a" * 64,
            "--patch-sha256",
            "b" * 64,
            "--action",
            "draft_pr",
            "--head-branch",
            "uca/safe-task-123",
        ]
    )

    assert arguments.command == "safe-source-publish"
    assert arguments.state_root == Path("/tmp/uca-state")
    assert arguments.source_control_factory == "trusted_source_control:create_adapter"
    assert arguments.task_id == "safe-task-123"
    assert arguments.approval_sha256 == "a" * 64
    assert arguments.patch_sha256 == "b" * 64
    assert arguments.action == "draft_pr"
    assert arguments.head_branch == "uca/safe-task-123"


def test_safe_source_publish_does_not_load_a_model_provider(
    monkeypatch,
    tmp_path: Path,
    capsys,
) -> None:
    adapter = object()
    calls: dict[str, object] = {}

    class _PublicationService:
        def __init__(self, state_root: Path, configured_adapter: object) -> None:
            calls["state_root"] = state_root
            calls["adapter"] = configured_adapter

        def publish_exact(self, task_id: str, **kwargs) -> dict[str, object]:
            calls["task_id"] = task_id
            calls["arguments"] = kwargs
            return {"status": "completed", "qualified": True}

        def close(self) -> None:
            calls["closed"] = True

    def _provider_must_not_load(_factory):
        raise AssertionError("safe-source-publish must not load a model provider")

    monkeypatch.setattr(cli, "load_provider", _provider_must_not_load)
    monkeypatch.setattr(cli, "load_source_control_adapter", lambda _factory: adapter)
    monkeypatch.setattr(cli, "ExactPatchPublicationService", _PublicationService)

    exit_code = main(
        [
            "--state-root",
            str(tmp_path),
            "--source-control-factory",
            "fixture:create",
            "safe-source-publish",
            "--task-id",
            "safe-task-123",
            "--approval-sha256",
            "a" * 64,
            "--patch-sha256",
            "b" * 64,
            "--action",
            "push",
            "--head-branch",
            "uca/safe-task-123",
        ]
    )

    assert exit_code == 0
    assert calls == {
        "state_root": tmp_path,
        "adapter": adapter,
        "task_id": "safe-task-123",
        "arguments": {
            "approval_sha256": "a" * 64,
            "patch_sha256": "b" * 64,
            "action": "push",
            "head_branch": "uca/safe-task-123",
        },
        "closed": True,
    }
    assert '"status": "completed"' in capsys.readouterr().out


def test_safe_source_publish_missing_adapter_fails_with_redacted_json(
    monkeypatch,
    tmp_path: Path,
    capsys,
) -> None:
    monkeypatch.delenv("UCA_SOURCE_CONTROL_ADAPTER_FACTORY", raising=False)

    def _provider_must_not_load(_factory):
        raise AssertionError("safe-source-publish must not load a model provider")

    monkeypatch.setattr(cli, "load_provider", _provider_must_not_load)

    exit_code = main(
        [
            "--state-root",
            str(tmp_path),
            "safe-source-publish",
            "--task-id",
            "safe-task-123",
            "--approval-sha256",
            "a" * 64,
            "--patch-sha256",
            "b" * 64,
            "--action",
            "commit",
            "--head-branch",
            "uca/safe-task-123",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert "Traceback" not in captured.err
    assert json.loads(captured.err) == {
        "status": "blocked",
        "qualified": False,
        "error": {
            "code": "source_control_adapter_unavailable",
            "cause_type": "RuntimeError",
        },
    }
