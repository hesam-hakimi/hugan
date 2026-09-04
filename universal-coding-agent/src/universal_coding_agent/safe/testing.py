from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import time
from collections.abc import Mapping
from dataclasses import dataclass, field
from functools import partial
from pathlib import Path
from types import ModuleType
from typing import Any, Protocol, cast

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

TRUSTED_TEST_ADAPTER_PATH_ENV = "UCA_TRUSTED_TEST_ADAPTER_PATH"
TRUSTED_TEST_PAUSABLE_FACTORY_ENV = "UCA_TRUSTED_TEST_PAUSABLE_FACTORY"


def validate_selected_test_ids(test_ids: tuple[str, ...]) -> tuple[str, ...]:
    """Return canonical positional test IDs or reject option/path injection."""

    if not isinstance(test_ids, tuple) or not test_ids:
        raise ValueError("selected test IDs must be a non-empty tuple")
    if test_ids != tuple(sorted(set(test_ids))):
        raise ValueError("selected test IDs must be unique and sorted")
    for test_id in test_ids:
        if (
            not isinstance(test_id, str)
            or not test_id
            or test_id != test_id.strip()
            or len(test_id.encode("utf-8")) > 8_192
            or any(ord(character) < 32 for character in test_id)
        ):
            raise ValueError("selected test ID is invalid")
        test_path = test_id.split("::", 1)[0]
        if test_path.startswith(("-", "@")):
            raise ValueError("selected test ID may not use command-option syntax")
        try:
            normalized_path = normalize_repository_path(test_path)
        except ValueError as exc:
            raise ValueError("selected test ID path is not contained") from exc
        if normalized_path != test_path or not test_path.endswith(".py"):
            raise ValueError("selected test ID must begin with a canonical Python test path")
    return test_ids


def _validated_profile_ids(profile_ids: tuple[str, ...]) -> tuple[str, ...]:
    if not isinstance(profile_ids, tuple) or not profile_ids:
        raise ValueError("at least one test profile is required")
    if len(profile_ids) != len(set(profile_ids)):
        raise ValueError("test profile IDs must be unique")
    if any(
        not isinstance(profile_id, str)
        or not profile_id
        or profile_id != profile_id.strip()
        or any(ord(character) < 32 for character in profile_id)
        for profile_id in profile_ids
    ):
        raise ValueError("test profile ID is invalid")
    return profile_ids


class _PausableTestHandle(Protocol):
    def result(self, *, timeout_seconds: int) -> Any:
        """Wait for the bounded trusted-test result."""

    def cancel(self) -> None:
        """Request termination without blocking."""

    def done(self) -> bool:
        """Return without blocking whether the test terminated."""

    def pause(self) -> None:
        """Request a cooperative pause without blocking."""

    def resume(self) -> None:
        """Request continuation without blocking."""

    def paused(self) -> bool:
        """Return without blocking whether the pause was acknowledged."""


@dataclass
class SafeTestRunner:
    """Run only operator-defined argv profiles with shell disabled."""

    adapter_module_path: Path | None = None
    pausable_factory_name: str | None = None
    _module: ModuleType | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        has_path = self.adapter_module_path is not None
        has_factory = bool(str(self.pausable_factory_name or "").strip())
        if has_path != has_factory:
            raise ValueError(
                "configure both trusted-test adapter path and pausable factory"
            )
        if not has_path:
            self.pausable_factory_name = None
            return
        assert self.adapter_module_path is not None
        self.adapter_module_path = self.adapter_module_path.expanduser().resolve()
        self.pausable_factory_name = str(self.pausable_factory_name).strip()
        if not self.adapter_module_path.is_file():
            raise ValueError("trusted-test adapter module was not found")

    @classmethod
    def from_environment(cls) -> SafeTestRunner:
        path_value = os.getenv(TRUSTED_TEST_ADAPTER_PATH_ENV, "").strip()
        factory_name = os.getenv(TRUSTED_TEST_PAUSABLE_FACTORY_ENV, "").strip()
        if not path_value and not factory_name:
            return cls()
        if not path_value or not factory_name:
            raise ValueError(
                "trusted-test pausable adapter configuration is incomplete"
            )
        return cls(
            adapter_module_path=Path(path_value),
            pausable_factory_name=factory_name,
        )

    def run_profiles(
        self,
        sandbox: Path,
        policy: SafeModePolicy,
        profile_ids: tuple[str, ...],
        *,
        cancellation: CancellationSignal | None = None,
    ) -> tuple[TestExecutionResult, ...]:
        return self._run_profiles(
            sandbox,
            policy,
            profile_ids,
            selected_test_ids=None,
            cancellation=cancellation,
        )

    def run_selected_profiles(
        self,
        sandbox: Path,
        policy: SafeModePolicy,
        profile_ids: tuple[str, ...],
        selected_test_ids: Mapping[str, tuple[str, ...]],
        *,
        cancellation: CancellationSignal | None = None,
    ) -> tuple[TestExecutionResult, ...]:
        """Append only validated positional test IDs to trusted profile argv."""

        requested = _validated_profile_ids(profile_ids)
        if set(selected_test_ids) != set(requested):
            raise ValueError(
                "selected-test mapping must match the requested test profiles"
            )
        normalized = {
            profile_id: validate_selected_test_ids(selected_test_ids[profile_id])
            for profile_id in requested
        }
        return self._run_profiles(
            sandbox,
            policy,
            requested,
            selected_test_ids=normalized,
            cancellation=cancellation,
        )

    def _run_profiles(
        self,
        sandbox: Path,
        policy: SafeModePolicy,
        profile_ids: tuple[str, ...],
        *,
        selected_test_ids: Mapping[str, tuple[str, ...]] | None,
        cancellation: CancellationSignal | None,
    ) -> tuple[TestExecutionResult, ...]:
        root = sandbox.resolve()
        profiles = policy.profile_map()
        results: list[TestExecutionResult] = []
        for profile_id in _validated_profile_ids(profile_ids):
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

            argv = tuple(profile.argv)
            if selected_test_ids is not None:
                argv += selected_test_ids[profile_id]

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
                list(argv),
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=False,
                env=environment,
                start_new_session=True,
            )

            if cancellation is not None and self.pausable_factory_name:
                factory = self._pausable_factory()
                start_pausable_test = partial(
                    _create_pausable_test_handle,
                    factory,
                    argv=argv,
                    cwd=str(cwd),
                    env=dict(environment),
                    timeout_seconds=profile.timeout_seconds,
                )

                with cancellation.operation(OwnedOperationKind.TEST):
                    with cancellation.owned_pausable_operation(
                        OwnedOperationKind.TEST,
                        start_pausable_test,
                    ) as operation:
                        returncode, stdout, stderr = _await_pausable_test_handle(
                            cast(_PausableTestHandle, operation),
                            timeout_seconds=profile.timeout_seconds,
                        )
            elif cancellation is None:
                process = start_profile()
                stdout, stderr = _communicate(
                    process,
                    timeout=profile.timeout_seconds,
                )
                returncode = process.returncode
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
                returncode = process.returncode
            elapsed_ms = max(0, int((time.monotonic() - started) * 1000))
            combined = "\n".join(
                part for part in (stdout, stderr) if part
            )
            output = sanitize_text(combined)[: profile.output_limit]
            results.append(
                TestExecutionResult(
                    profile_id=profile.profile_id,
                    passed=returncode == 0,
                    returncode=returncode,
                    duration_ms=elapsed_ms,
                    output=output,
                )
            )
        return tuple(results)

    def _pausable_factory(self):
        module = self._adapter_module()
        factory = getattr(module, str(self.pausable_factory_name), None)
        if not callable(factory):
            raise ValueError(
                "configured trusted-test pausable factory is unavailable"
            )
        return factory

    def _adapter_module(self) -> ModuleType:
        if self._module is not None:
            return self._module
        path = self.adapter_module_path
        if path is None:
            raise RuntimeError("trusted-test pausable adapter is not configured")
        module_name = f"_uca_trusted_test_adapter_{abs(hash(str(path)))}"
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise ValueError("trusted-test adapter module could not load")
        module = importlib.util.module_from_spec(spec)
        parent = str(path.parent)
        inserted = parent not in sys.path
        if inserted:
            sys.path.insert(0, parent)
        try:
            spec.loader.exec_module(module)
        except Exception as exc:
            raise ValueError(
                f"trusted-test adapter failed to load safely: {type(exc).__name__}"
            ) from None
        finally:
            if inserted and sys.path and sys.path[0] == parent:
                sys.path.pop(0)
        self._module = module
        return module


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


def _require_pausable_test_handle(value: Any) -> _PausableTestHandle:
    required = ("result", "cancel", "done", "pause", "resume", "paused")
    if not all(callable(getattr(value, name, None)) for name in required):
        _cancel_test_handle(value)
        raise RuntimeError("trusted-test pausable factory returned an invalid handle")
    return cast(_PausableTestHandle, value)


def _create_pausable_test_handle(
    factory: Any,
    *,
    argv: tuple[str, ...],
    cwd: str,
    env: dict[str, str],
    timeout_seconds: int,
) -> _PausableTestHandle:
    try:
        value = factory(
            argv=argv,
            cwd=cwd,
            env=env,
            timeout_seconds=timeout_seconds,
        )
    except Exception as exc:
        raise RuntimeError(
            f"trusted-test pausable factory failed safely: {type(exc).__name__}"
        ) from None
    return _require_pausable_test_handle(value)


def _await_pausable_test_handle(
    handle: _PausableTestHandle,
    *,
    timeout_seconds: int,
) -> tuple[int, str, str]:
    completed = False
    try:
        try:
            result = handle.result(timeout_seconds=timeout_seconds)
        except (OSError, RuntimeError, subprocess.SubprocessError):
            raise
        except Exception as exc:
            raise RuntimeError(
                f"trusted-test pausable handle failed safely: {type(exc).__name__}"
            ) from None
        completed = _test_handle_done(handle)
    finally:
        if not _test_handle_done(handle):
            _cancel_test_handle(handle)
    if not completed:
        raise RuntimeError("trusted-test pausable handle returned before termination")
    return _require_test_result(result)


def _require_test_result(value: Any) -> tuple[int, str, str]:
    returncode = getattr(value, "returncode", None)
    stdout = getattr(value, "stdout", None)
    stderr = getattr(value, "stderr", None)
    if isinstance(returncode, bool) or not isinstance(returncode, int):
        raise RuntimeError("trusted-test pausable handle returned an invalid result")
    if not isinstance(stdout, str) or not isinstance(stderr, str):
        raise RuntimeError("trusted-test pausable handle returned an invalid result")
    return returncode, stdout, stderr


def _test_handle_done(handle: _PausableTestHandle) -> bool:
    try:
        return bool(handle.done())
    except Exception:
        return False


def _cancel_test_handle(handle: Any) -> None:
    try:
        handle.cancel()
    except Exception:
        return
