from __future__ import annotations

import ast
import hashlib
import mimetypes
import subprocess
from collections import Counter
from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path

from universal_coding_agent.core.models import ProjectFile, ProjectManifest

DEFAULT_DENY_PATTERNS = (
    ".git/**",
    ".env",
    ".env.*",
    "*.pem",
    "*.key",
    "id_rsa*",
    "**/.git-credentials",
    "**/.netrc",
    "**/credentials.json",
    "**/token.json",
    "**/*shell_history*",
)
INDEX_POLICY_VERSION = "2"


class RepositoryIndexingError(ValueError):
    """Repository source cannot be indexed without violating its immutable contract."""


@dataclass(frozen=True)
class TrackedRepositoryFile:
    path: str
    git_mode: str
    git_blob_oid: str


class RepositoryIndexer:
    def __init__(self, *, max_file_bytes: int = 2_000_000):
        self.max_file_bytes = max_file_bytes

    def build_manifest(
        self,
        root: Path,
        *,
        repository_url: str,
        base_ref: str,
        base_sha: str,
    ) -> ProjectManifest:
        root = root.resolve()
        tracked = self.tracked_files(root)
        files: list[ProjectFile] = []
        language_counts: Counter[str] = Counter()
        instructions: list[str] = []
        architecture: list[str] = []
        tests: list[str] = []
        for tracked_file in tracked:
            project_file = self.project_file(root, tracked_file.path)
            if project_file is None:
                continue
            files.append(project_file)
            language_counts[project_file.language] += 1
            lower = project_file.path.lower()
            name = Path(project_file.path).name.lower()
            if name == "agents.md" or name.startswith("readme"):
                instructions.append(project_file.path)
            if "/adr/" in f"/{lower}" or "architecture" in lower:
                architecture.append(project_file.path)
            if project_file.is_test:
                tests.append(project_file.path)
        return ProjectManifest(
            repository_url=repository_url,
            base_ref=base_ref,
            base_sha=base_sha,
            files=tuple(files),
            instruction_paths=tuple(sorted(instructions)),
            architecture_paths=tuple(sorted(architecture)),
            test_paths=tuple(sorted(tests)),
            language_counts=dict(sorted(language_counts.items())),
        )

    def verify_clean_base(self, root: Path, *, base_sha: str) -> None:
        root = root.resolve()
        head = self._git(root, "rev-parse", "HEAD").decode("ascii").strip()
        if head != base_sha:
            raise RepositoryIndexingError("repository HEAD does not match the requested Base SHA")
        status = self._git(
            root,
            "status",
            "--porcelain=v1",
            "-z",
            "--untracked-files=no",
        )
        if status:
            raise RepositoryIndexingError("tracked repository state is not clean")

    def verify_ancestor(self, root: Path, *, ancestor_sha: str, descendant_sha: str) -> None:
        process = subprocess.run(
            [
                "git",
                "-C",
                str(root.resolve()),
                "merge-base",
                "--is-ancestor",
                ancestor_sha,
                descendant_sha,
            ],
            check=False,
            capture_output=True,
            shell=False,
        )
        if process.returncode == 1:
            raise RepositoryIndexingError(
                "previous repository index Base SHA is not an ancestor of the requested Base SHA"
            )
        if process.returncode != 0:
            raise RepositoryIndexingError("repository ancestry verification failed")

    def tracked_files(self, root: Path) -> tuple[TrackedRepositoryFile, ...]:
        output = self._git(root.resolve(), "ls-files", "-s", "-z")
        tracked: list[TrackedRepositoryFile] = []
        for raw_item in output.split(b"\0"):
            if not raw_item:
                continue
            try:
                metadata, raw_path = raw_item.split(b"\t", 1)
                mode, oid, stage = metadata.decode("ascii").split(" ", 2)
                path = raw_path.decode("utf-8", errors="strict")
            except (UnicodeDecodeError, ValueError) as exc:
                raise RepositoryIndexingError("tracked repository metadata is malformed") from exc
            if stage != "0":
                raise RepositoryIndexingError(
                    "tracked repository contains an unresolved index stage"
                )
            tracked.append(
                TrackedRepositoryFile(
                    path=path.replace("\\", "/"),
                    git_mode=mode,
                    git_blob_oid=oid,
                )
            )
        tracked.sort(key=lambda item: item.path)
        if len({item.path for item in tracked}) != len(tracked):
            raise RepositoryIndexingError("tracked repository contains duplicate paths")
        return tuple(tracked)

    def project_file(self, root: Path, relative: str) -> ProjectFile | None:
        root = root.resolve()
        if self.is_denied(relative):
            return None
        path = (root / relative).resolve()
        if (
            (path != root and root not in path.parents)
            or not path.is_file()
            or path.stat().st_size > self.max_file_bytes
        ):
            return None
        data = path.read_bytes()
        language = self._language(relative)
        symbols: tuple[str, ...] = ()
        imports: tuple[str, ...] = ()
        if language == "python":
            symbols, imports = self._python_metadata(data, relative)
        return ProjectFile(
            path=relative,
            size=len(data),
            sha256=hashlib.sha256(data).hexdigest(),
            language=language,
            is_test=self._is_test(relative),
            symbols=symbols,
            imports=imports,
        )

    @staticmethod
    def _git(root: Path, *args: str) -> bytes:
        process = subprocess.run(
            ["git", "-C", str(root), *args],
            check=True,
            capture_output=True,
            shell=False,
        )
        return process.stdout

    @staticmethod
    def is_denied(path: str) -> bool:
        normalized = path.replace("\\", "/")
        if normalized.startswith(".git/"):
            return True
        if normalized == ".env" or normalized.startswith(".env."):
            return not normalized.endswith((".example", ".sample", ".template"))
        return any(fnmatch(normalized, pattern) for pattern in DEFAULT_DENY_PATTERNS)

    @staticmethod
    def _language(path: str) -> str:
        suffix = Path(path).suffix.lower()
        mapping = {
            ".py": "python",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".js": "javascript",
            ".jsx": "javascript",
            ".java": "java",
            ".cs": "csharp",
            ".go": "go",
            ".rs": "rust",
            ".md": "markdown",
            ".json": "json",
            ".yml": "yaml",
            ".yaml": "yaml",
            ".sql": "sql",
            ".ps1": "powershell",
            ".sh": "shell",
        }
        return mapping.get(suffix, mimetypes.guess_type(path)[0] or "other")

    @staticmethod
    def _is_test(path: str) -> bool:
        lower = path.lower().replace("\\", "/")
        name = Path(lower).name
        return (
            "/test/" in f"/{lower}"
            or "/tests/" in f"/{lower}"
            or name.startswith("test_")
            or name.endswith((".test.ts", ".spec.ts", ".test.js", ".spec.js"))
        )

    @staticmethod
    def _python_metadata(data: bytes, path: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
        try:
            tree = ast.parse(data.decode("utf-8"), filename=path)
        except (SyntaxError, UnicodeDecodeError):
            return (), ()
        symbols: list[str] = []
        imports: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                symbols.append(f"{node.__class__.__name__}:{node.name}:{node.lineno}")
            elif isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                module = f"{'.' * node.level}{node.module or ''}"
                imports.extend(f"{module}:{alias.name}" for alias in node.names)
        return tuple(sorted(set(symbols))), tuple(sorted(set(imports)))
