from __future__ import annotations

import ast
import re
from pathlib import Path

from universal_coding_agent.context.line_edit_compiler import LineAddressedContextCompiler
from universal_coding_agent.core.models import ProjectManifest
from universal_coding_agent.core.safe_models import (
    SafeTaskRequest,
    StructuredEditProposal,
    safe_json,
)
from universal_coding_agent.safety.sanitizer import sanitize_text

_MODEL_LINE_ID = re.compile(r"(?m)^L([0-9]{6})-[0-9a-f]{16}(?= \|)")


class ShardedLineAddressedContextCompiler(LineAddressedContextCompiler):
    """Compile one bounded implementer context per approved file.

    Line-address authority remains strictly file-local, while read-only interface contracts from
    related approved files preserve enough cross-file context for coherent multi-component edits.
    """

    dependency_contract_max_files = 16
    dependency_contract_char_budget = 36_000

    def compile_implementer_for_path(
        self,
        root: Path,
        task: SafeTaskRequest,
        project_manifest: ProjectManifest,
        target_path: str,
    ) -> str:
        matches = [item for item in task.manifest.allowed_changes if item.path == target_path]
        if len(matches) != 1:
            raise ValueError(f"approved shard path is not unique: {target_path}")
        entry = matches[0]
        narrow_manifest = task.manifest.model_copy(update={"allowed_changes": (entry,)})
        narrow_task = task.model_copy(update={"manifest": narrow_manifest})
        dependency_contracts = self._read_only_dependency_contracts(
            root,
            task,
            project_manifest,
            target_path,
        )
        sections = [
            "# Safe task",
            task.objective,
            *self._accepted_evidence_sections(task),
            "# File-shard assignment",
            (
                f"Target path: {target_path}\n"
                f"Approved operation: {entry.operation.value}\n"
                "Return exactly one StructuredEditProposal containing exactly one FileEdit "
                "for this target path. Do not edit any other path in this shard."
            ),
            "# Immutable repository identity",
            (
                f"Repository: {project_manifest.repository_url}\n"
                f"Base ref: {project_manifest.base_ref}\n"
                f"Base SHA: {project_manifest.base_sha}"
            ),
            "# Human-approved file shard",
            safe_json(narrow_manifest.model_dump(mode="json")),
            "# Read-only approved-scope dependency contracts",
            dependency_contracts,
            "# Exact assigned file state with deterministic model line refs",
            self._line_addressed_file_state(root, narrow_task),
            "# Mandatory structured-edit protocol v2",
            (
                "Return exactly one StructuredEditProposal JSON object with exactly one edit. "
                "TextReplacement.old_text must use model line refs copied exactly from the "
                "assigned file state above. A model line ref has the exact form A000123. "
                "Supported tokens are @range:A000123..A000125, @before:A000123, and "
                "@after:A000123. Never invent a line ref and never copy one from another file. "
                "The read-only dependency contracts above contain semantic/interface context only; "
                "they grant no edit authority and any A-like text there is never an address token. "
                "The control plane expands the compact ref to the trusted line fingerprint from "
                "the frozen Base SHA before the normal line-address validator runs. new_text is "
                "the exact replacement or inserted text. Range edits replace complete inclusive "
                "lines and must preserve the final line ending. Insertions must contain complete "
                "lines and end with the file line ending. Use only non-overlapping addresses. "
                "For an approved create operation, use FileEdit.content with complete UTF-8 text. "
                "Do not delete, rename, copy, modify symlinks, stage, commit, push, create a pull "
                "request, merge, deploy, or run commands. Git, not the model, generates the "
                "canonical patch after deterministic materialization."
            ),
        ]
        return self._bound("\n\n".join(sections), self.implementer_char_budget)

    def compile_address_correction_for_path(
        self,
        root: Path,
        task: SafeTaskRequest,
        project_manifest: ProjectManifest,
        target_path: str,
        proposal: StructuredEditProposal,
        errors: tuple[str, ...],
    ) -> str:
        base = self.compile_implementer_for_path(root, task, project_manifest, target_path)
        sections = [
            base,
            "# Deterministic shard validation failure",
            "\n".join(f"- {item}" for item in errors),
            "# Rejected shard proposal",
            safe_json(proposal.model_dump(mode="json")),
            "# Single bounded address correction",
            (
                "Correct only the model line-ref selection for this same target path and "
                "operation. Copy every A000123-style ref exactly from the assigned file state "
                "shown above and use only @range/@before/@after tokens. Do not reproduce or "
                "invent a fingerprint. Do not change the target path, approved operation, or "
                "requested test-profile set. Return exactly one StructuredEditProposal JSON "
                "object with exactly one FileEdit. This is the only address-correction attempt."
            ),
        ]
        return self._bound("\n\n".join(sections), self.implementer_char_budget)

    def _read_only_dependency_contracts(
        self,
        root: Path,
        task: SafeTaskRequest,
        project_manifest: ProjectManifest,
        target_path: str,
    ) -> str:
        metadata = {item.path: item for item in project_manifest.files}
        approved_paths = {item.path for item in task.manifest.allowed_changes}
        approved_paths.discard(target_path)
        if not approved_paths:
            return "(no other approved files)"

        module_map = {
            module: item.path
            for item in project_manifest.files
            if item.language == "python"
            for module in [self._python_module(item.path)]
            if module
        }
        target_item = metadata.get(target_path)
        direct: set[str] = set()
        if target_item is not None:
            for raw_import in target_item.imports:
                resolved = self._resolve_python_import(raw_import, module_map)
                if resolved in approved_paths:
                    direct.add(resolved)

        reverse: set[str] = set()
        for path in approved_paths:
            item = metadata.get(path)
            if item is None:
                continue
            for raw_import in item.imports:
                if self._resolve_python_import(raw_import, module_map) == target_path:
                    reverse.add(path)
                    break

        ordered = [
            *sorted(direct),
            *sorted(reverse - direct),
            *sorted(approved_paths - direct - reverse),
        ][: self.dependency_contract_max_files]

        sections: list[str] = [
            (
                "These contracts are read-only semantic context from the same frozen Base SHA. "
                "They expose dependency relationships and callable signatures without exposing "
                "line-address authority. Only the assigned target file below may be edited."
            )
        ]
        for path in ordered:
            item = metadata.get(path)
            relationships: list[str] = []
            if path in direct:
                relationships.append("target imports this approved file")
            if path in reverse:
                relationships.append("this approved file imports the target")
            if not relationships:
                relationships.append("approved peer in the same change scope")
            symbols = list(item.symbols) if item is not None else []
            imports = list(item.imports) if item is not None else []
            contract_surface = self._contract_surface(root, path)
            sections.append(
                "\n".join(
                    (
                        f"## {path}",
                        f"Relationship: {', '.join(relationships)}",
                        f"Symbols: {symbols}",
                        f"Imports: {imports}",
                        "Contract surface (READ ONLY; no line refs):",
                        contract_surface,
                    )
                )
            )

        value = "\n\n".join(sections)
        if len(value) <= self.dependency_contract_char_budget:
            return value
        marker = "\n[read-only dependency contract context truncated by deterministic budget]"
        return value[: self.dependency_contract_char_budget - len(marker)] + marker

    def _contract_surface(self, root: Path, relative_path: str) -> str:
        repository_root = root.resolve()
        path = (repository_root / relative_path).resolve()
        if repository_root not in path.parents or not path.is_file():
            return "(contract surface unavailable)"
        if path.suffix.lower() != ".py":
            return "(language-specific callable surface not yet available)"
        try:
            source = path.read_text(encoding="utf-8", errors="strict")
            tree = ast.parse(source)
        except (OSError, UnicodeDecodeError, SyntaxError):
            return "(Python contract surface unavailable)"

        lines: list[str] = []
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                lines.append(self._function_signature(node))
                continue
            if not isinstance(node, ast.ClassDef):
                continue
            lines.append(self._class_signature(node))
            for member in node.body:
                if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    lines.append(f"    {self._function_signature(member)}")
        if not lines:
            return "(no callable Python contract surface)"
        return sanitize_text("\n".join(lines))

    @staticmethod
    def _function_signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
        prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
        arguments = ast.unparse(node.args)
        returns = f" -> {ast.unparse(node.returns)}" if node.returns is not None else ""
        return f"{prefix} {node.name}({arguments}){returns}:"

    @staticmethod
    def _class_signature(node: ast.ClassDef) -> str:
        bases = [ast.unparse(base) for base in node.bases]
        bases.extend(
            f"{keyword.arg}={ast.unparse(keyword.value)}"
            for keyword in node.keywords
            if keyword.arg is not None
        )
        suffix = f"({', '.join(bases)})" if bases else ""
        return f"class {node.name}{suffix}:"

    @staticmethod
    def _python_module(path: str) -> str | None:
        if not path.endswith(".py"):
            return None
        parts = path[:-3].split("/")
        if parts[-1] == "__init__":
            parts = parts[:-1]
        return ".".join(parts) or None

    @staticmethod
    def _resolve_python_import(raw_import: str, module_map: dict[str, str]) -> str | None:
        module = raw_import.split(":", 1)[0].strip(".")
        if module in module_map:
            return module_map[module]
        parts = module.split(".")
        while len(parts) > 1:
            parts.pop()
            candidate = ".".join(parts)
            if candidate in module_map:
                return module_map[candidate]
        return None

    def _line_addressed_file_state(self, root: Path, task: SafeTaskRequest) -> str:
        rendered = super()._line_addressed_file_state(root, task)
        # Rewrite only the address prefix at the start of rendered state lines. Source text that
        # happens to contain an L000123-<fingerprint> string is left untouched after the separator.
        return _MODEL_LINE_ID.sub(r"A\1", rendered)
