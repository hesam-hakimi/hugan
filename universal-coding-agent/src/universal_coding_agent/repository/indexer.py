from __future__ import annotations

import ast
import hashlib
import mimetypes
import subprocess
from collections import Counter
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
        tracked = self._tracked_files(root)
        files: list[ProjectFile] = []
        language_counts: Counter[str] = Counter()
        instructions: list[str] = []
        architecture: list[str] = []
        tests: list[str] = []
        for relative in tracked:
            if self._denied(relative):
                continue
            path = (root / relative).resolve()
            if (
                root not in path.parents
                or not path.is_file()
                or path.stat().st_size > self.max_file_bytes
            ):
                continue
            data = path.read_bytes()
            language = self._language(relative)
            symbols: tuple[str, ...] = ()
            imports: tuple[str, ...] = ()
            if language == "python":
                symbols, imports = self._python_metadata(data, relative)
            is_test = self._is_test(relative)
            files.append(
                ProjectFile(
                    path=relative,
                    size=len(data),
                    sha256=hashlib.sha256(data).hexdigest(),
                    language=language,
                    is_test=is_test,
                    symbols=symbols,
                    imports=imports,
                )
            )
            language_counts[language] += 1
            lower = relative.lower()
            name = Path(relative).name.lower()
            if name == "agents.md" or name.startswith("readme"):
                instructions.append(relative)
            if "/adr/" in f"/{lower}" or "architecture" in lower:
                architecture.append(relative)
            if is_test:
                tests.append(relative)
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

    def _tracked_files(self, root: Path) -> list[str]:
        process = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z"],
            check=True,
            capture_output=True,
            shell=False,
        )
        return [
            item.decode("utf-8", errors="strict")
            for item in process.stdout.split(b"\0")
            if item
        ]

    @staticmethod
    def _denied(path: str) -> bool:
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
                module = node.module or ""
                imports.extend(f"{module}:{alias.name}" for alias in node.names)
        return tuple(sorted(set(symbols))), tuple(sorted(set(imports)))
