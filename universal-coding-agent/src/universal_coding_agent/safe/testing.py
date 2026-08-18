from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

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
    ) -> tuple[TestExecutionResult, ...]:
        root = sandbox.resolve()
        profiles = policy.profile_map()
        results: list[TestExecutionResult] = []
        for profile_id in profile_ids:
            profile = profiles.get(profile_id)
            if profile is None:
                raise ValueError(f"unknown test profile: {profile_id}")
            cwd = root if profile.cwd == "." else (root / normalize_repository_path(profile.cwd)).resolve()
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
            completed = subprocess.run(
                list(profile.argv),
                cwd=cwd,
                check=False,
                capture_output=True,
                text=True,
                timeout=profile.timeout_seconds,
                shell=False,
                env=environment,
            )
            elapsed_ms = max(0, int((time.monotonic() - started) * 1000))
            combined = "\n".join(
                part for part in (completed.stdout, completed.stderr) if part
            )
            output = sanitize_text(combined)[: profile.output_limit]
            results.append(
                TestExecutionResult(
                    profile_id=profile.profile_id,
                    passed=completed.returncode == 0,
                    returncode=completed.returncode,
                    duration_ms=elapsed_ms,
                    output=output,
                )
            )
        return tuple(results)
