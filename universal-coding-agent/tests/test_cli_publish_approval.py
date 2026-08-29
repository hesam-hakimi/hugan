from universal_coding_agent.cli import parser


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
