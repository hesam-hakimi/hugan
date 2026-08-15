from __future__ import annotations

import hashlib
import os
import re
import subprocess
import urllib.parse
from dataclasses import dataclass
from pathlib import Path

from universal_coding_agent.core.models import RepositorySpec, SandboxInfo

_SHA = re.compile(r"^[0-9a-f]{40,64}$")


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


class GitSandboxManager:
    """Create isolated clones from a credential-free mirror cache."""

    def __init__(
        self,
        state_root: Path,
        *,
        git_binary: str = "git",
        command_timeout_seconds: int = 300,
        allow_local_sources: bool = False,
    ) -> None:
        self.state_root = state_root.resolve()
        self.mirrors_root = self.state_root / "mirrors"
        self.sandboxes_root = self.state_root / "sandboxes"
        self.git_binary = git_binary
        self.timeout = command_timeout_seconds
        self.allow_local_sources = allow_local_sources
        self.mirrors_root.mkdir(parents=True, exist_ok=True)
        self.sandboxes_root.mkdir(parents=True, exist_ok=True)

    def prepare(self, task_id: str, repository: RepositorySpec) -> SandboxInfo:
        normalized_url = self._validate_repository_url(repository.url)
        repository_id = hashlib.sha256(normalized_url.encode("utf-8")).hexdigest()[:24]
        mirror = self.mirrors_root / f"{repository_id}.git"
        if mirror.exists():
            self._run([self.git_binary, "-C", str(mirror), "fetch", "--prune", "origin"])
        else:
            self._run([self.git_binary, "clone", "--mirror", normalized_url, str(mirror)])
        base_sha = self._resolve_ref(mirror, repository.base_ref)
        sandbox = (self.sandboxes_root / task_id / "repo").resolve()
        self._assert_contained(sandbox, self.sandboxes_root)
        if sandbox.exists():
            raise FileExistsError(f"sandbox already exists for task {task_id}")
        sandbox.parent.mkdir(parents=True, exist_ok=True)
        self._run([self.git_binary, "clone", "--no-hardlinks", str(mirror), str(sandbox)])
        self._run([self.git_binary, "-C", str(sandbox), "checkout", "--detach", base_sha])
        status = self._run([self.git_binary, "-C", str(sandbox), "status", "--porcelain=v1"])
        if status.stdout.strip():
            raise RuntimeError("new sandbox is not clean")
        return SandboxInfo(
            sandbox_id=task_id,
            repository_url=normalized_url,
            base_ref=repository.base_ref,
            base_sha=base_sha,
            path=str(sandbox),
            clean=True,
        )

    def read_only_git_checks(self, sandbox_path: Path) -> list[dict[str, object]]:
        root = sandbox_path.resolve()
        self._assert_contained(root, self.sandboxes_root)
        status = self._run([self.git_binary, "-C", str(root), "status", "--porcelain=v1"])
        diff = self._run([self.git_binary, "-C", str(root), "diff", "--check"])
        head = self._run([self.git_binary, "-C", str(root), "rev-parse", "HEAD"])
        return [
            {
                "name": "worktree-clean",
                "passed": not status.stdout.strip(),
                "summary": "clean" if not status.stdout.strip() else "worktree has changes",
            },
            {
                "name": "git-diff-check",
                "passed": diff.returncode == 0,
                "summary": (diff.stdout or diff.stderr or "git diff --check passed").strip()[:2000],
            },
            {
                "name": "head-readable",
                "passed": bool(_SHA.fullmatch(head.stdout.strip())),
                "summary": head.stdout.strip(),
            },
        ]

    def _resolve_ref(self, mirror: Path, base_ref: str) -> str:
        candidates = [base_ref, f"refs/heads/{base_ref}", f"refs/remotes/origin/{base_ref}"]
        for candidate in candidates:
            result = self._run(
                [
                    self.git_binary,
                    "-C",
                    str(mirror),
                    "rev-parse",
                    "--verify",
                    f"{candidate}^{{commit}}",
                ],
                check=False,
            )
            value = result.stdout.strip()
            if result.returncode == 0 and _SHA.fullmatch(value):
                return value
        raise RuntimeError(f"unable to resolve base ref {base_ref!r}")

    def _validate_repository_url(self, value: str) -> str:
        raw = value.strip()
        if self.allow_local_sources and Path(raw).exists():
            return str(Path(raw).resolve())
        if raw.startswith("git@"):
            if any(character in raw for character in ("\n", "\r", "\x00")):
                raise ValueError("invalid SSH repository URL")
            return raw
        parsed = urllib.parse.urlsplit(raw)
        if parsed.scheme != "https" or not parsed.hostname:
            raise ValueError("repository URL must be HTTPS or an SSH git@ URL")
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("repository URL must not embed credentials, query, or fragment")
        return urllib.parse.urlunsplit(parsed)

    def _run(self, arguments: list[str], *, check: bool = True) -> CommandResult:
        environment = {
            "PATH": os.environ.get("PATH", ""),
            "HOME": os.environ.get("HOME", ""),
            "GIT_TERMINAL_PROMPT": "0",
        }
        if os.environ.get("SSH_AUTH_SOCK"):
            environment["SSH_AUTH_SOCK"] = os.environ["SSH_AUTH_SOCK"]
        process = subprocess.run(
            arguments,
            check=False,
            capture_output=True,
            text=True,
            timeout=self.timeout,
            shell=False,
            env=environment,
        )
        result = CommandResult(process.returncode, process.stdout, process.stderr)
        if check and process.returncode != 0:
            summary = (process.stderr or process.stdout).strip()[:2000]
            raise RuntimeError(f"command failed ({process.returncode}): {summary}")
        return result

    @staticmethod
    def _assert_contained(path: Path, root: Path) -> None:
        root = root.resolve()
        path = path.resolve()
        if path != root and root not in path.parents:
            raise ValueError("path escapes sandbox root")
