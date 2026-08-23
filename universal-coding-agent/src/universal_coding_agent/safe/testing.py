from __future__ import annotations

import os
import subprocess
import time
from functools import partial
from pathlib import Path

from universal_coding_agent.core.cancellation import (
    CancellationSignal,
    OwnedOperationKind,
)
from universal_coding_agent.core.safe_models import (
    SafeModePolicy,
    TestExecutionResult,
    normalize_repository_path,
)
from universal_coding_agent.safety.sanitizer import sanitize_text


class SafeTestRunner:
    """Run only operator-defined argv profiles with shell disabled."""

    def run_profiles(
        self,
        sandbox: Path,
        policy: SafeModePolicy,
        profile_ids: tuple[str, ...],
        *,
        cancellation: CancellationSignal | None = None,
    ) -> tuple[TestExecutionResult, ...]:
        root = sandbox.resolve()
        profiles = policy.profile_map()
        results: list[TestExecutionResult] = []
        for profile_id in profile_ids:
            if cancellation is not None:
                cancellation.raise_if_cancelled()
            profile = profiles.get(profile_id)
            if profile is None:
                raise ValueError(f"unknown test profile: {profile_id}")
            cwd = (
                root
                if profile.cwd == "."
                else (root / normalize_repository_path(profile.cwd)).resolve()
            )
            if cwd != root and root not in cwd.parents:
                raise ValueError("test working directory escapes sandbox")
            if not cwd.is_dir():
                raise ValueError(f"test working directory does not exist: {profile.cwd}")

            environment = {
                "PATH": os.environ.get("PATH", ""),
                "HOME": os.environ.get("HOME", ""),
                "PYTHONDONTWRITEBYTECODE": "1",
                "GIT_TERMINAL_PROMPT": "0",
                "CI": "1",
            }
            started = time.monotonic()
            start_profile = partial(
                subprocess.Popen,
                list(profile.argv),
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=False,
                env=environment,
                start_new_session=True,
            )

            if cancellation is None:
                process = start_profile()
                stdout, stderr = _communicate(
                    process,
                    timeout=profile.timeout_seconds,
                )
            else:
                with cancellation.operation(OwnedOperationKind.TEST):
                    with cancellation.owned_process(
                        OwnedOperationKind.TEST,
                        start_profile,
                    ) as process:
                        stdout, stderr = _communicate(
                            process,
                            timeout=profile.timeout_seconds,
                        )
            elapsed_ms = max(0, int((time.monotonic() - started) * 1000))
            combined = "\n".join(
                part for part in (stdout, stderr) if part
            )
            output = sanitize_text(combined)[: profile.output_limit]
            results.append(
                TestExecutionResult(
                    profile_id=profile.profile_id,
                    passed=process.returncode == 0,
                    returncode=process.returncode,
                    duration_ms=elapsed_ms,
                    output=output,
                )
            )
        return tuple(results)


def _communicate(
    process: subprocess.Popen[str],
    *,
    timeout: int,
) -> tuple[str, str]:
    try:
        return process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        process.kill()
        process.communicate()
        raise
