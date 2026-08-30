from __future__ import annotations

import hashlib
from pathlib import Path

from universal_coding_agent.context.safe_compiler import SafeContextCompiler
from universal_coding_agent.core.models import ProjectManifest
from universal_coding_agent.core.safe_models import SafeTaskRequest, safe_json
from universal_coding_agent.safe.line_editing import line_id
from universal_coding_agent.safety.sanitizer import sanitize_text


class LineAddressedContextCompiler(SafeContextCompiler):
    """Compile protocol-v2 contexts with deterministic line IDs."""

    def compile_implementer(
        self,
        root: Path,
        task: SafeTaskRequest,
        project_manifest: ProjectManifest,
    ) -> str:
        sections = [
            "# Safe task",
            task.objective,
            "# Immutable repository identity",
            (
                f"Repository: {project_manifest.repository_url}\n"
                f"Base ref: {project_manifest.base_ref}\n"
                f"Base SHA: {project_manifest.base_sha}"
            ),
            "# Human-approved change manifest",
            safe_json(task.manifest.model_dump(mode="json")),
            "# Exact allowed file state with deterministic line IDs",
            self._line_addressed_file_state(root, task),
            "# Mandatory structured-edit protocol v2",
            (
                "Return exactly one JSON object matching StructuredEditProposal. "
                "Do not emit a unified diff, Git patch syntax, shell commands, or "
                "Git commands. For each approved modify path, use "
                "TextReplacement.old_text only as one deterministic line-address "
                "token copied exactly from the supplied file state. Never place "
                "source text itself in old_text. Supported tokens are: "
                "@range:<LINE_ID>..<LINE_ID> to replace whole inclusive lines; "
                "@before:<LINE_ID> to insert complete lines immediately before one "
                "line; and @after:<LINE_ID> to insert complete lines immediately "
                "after one line. A LINE_ID has the exact form "
                "L000123-0123456789abcdef and must be copied from the file state "
                "above. new_text is the exact replacement or inserted text. Range "
                "edits replace complete lines, so preserve the existing final line "
                "ending. Insertions must contain complete lines and end with the "
                "file line ending. Use non-overlapping line ranges and do not issue "
                "two insertions at the same boundary. For approved create "
                "operations, use FileEdit.content with the complete UTF-8 text. "
                "Change only approved paths and operations. Do not delete, rename, "
                "copy, modify symlinks, stage, commit, push, create a pull request, "
                "merge, deploy, or run commands. The control plane verifies line "
                "number plus fingerprint against the frozen Base SHA before any "
                "write; Git, not the model, generates the canonical patch."
            ),
        ]
        return self._bound("\n\n".join(sections), self.implementer_char_budget)

    def _line_addressed_file_state(self, root: Path, task: SafeTaskRequest) -> str:
        repository_root = root.resolve()
        output: list[str] = []
        for entry in task.manifest.allowed_changes:
            path = repository_root / entry.path
            resolved = path.resolve()
            if resolved != repository_root and repository_root not in resolved.parents:
                raise ValueError("approved file escapes repository")
            if self._contains_symlink_component(repository_root, entry.path):
                output.append(f"## {entry.path}\nSYMLINK_REJECTED")
                continue
            if not path.exists():
                output.append(
                    f"## {entry.path}\nOperation: {entry.operation.value}\nState: ABSENT"
                )
                continue
            if not path.is_file():
                output.append(f"## {entry.path}\nState: NOT_A_REGULAR_FILE")
                continue

            try:
                payload = path.read_bytes()
                content = payload.decode("utf-8")
            except (OSError, UnicodeDecodeError):
                output.append(f"## {entry.path}\nState: NOT_READABLE_UTF8_TEXT")
                continue

            limit = self.max_chars_per_file
            truncated = len(content) > limit
            bounded_raw = content[:limit]
            if truncated:
                newline = max(bounded_raw.rfind("\n"), bounded_raw.rfind("\r"))
                bounded_raw = bounded_raw[: newline + 1] if newline >= 0 else ""
            bounded = sanitize_text(bounded_raw)
            content_sha = hashlib.sha256(payload).hexdigest()
            redacted = bounded != bounded_raw
            if redacted:
                output.append(
                    f"## {entry.path}\nOperation: {entry.operation.value}\n"
                    f"SHA256: {content_sha}\nState: CONTENT_REDACTED_FOR_SAFETY\n"
                    "Line-addressed model edits are not permitted for redacted content."
                )
                continue

            lines = bounded.splitlines(keepends=True)
            rendered = []
            for index, value in enumerate(lines, start=1):
                body = (
                    value[:-2]
                    if value.endswith("\r\n")
                    else value[:-1]
                    if value.endswith(("\n", "\r"))
                    else value
                )
                rendered.append(f"{line_id(index, value)} | {body}")
            suffix = (
                "\n[FILE CONTENT TRUNCATED; ONLY THE LINE IDS ABOVE MAY BE TARGETED]"
                if truncated
                else ""
            )
            output.append(
                f"## {entry.path}\nOperation: {entry.operation.value}\n"
                f"SHA256: {content_sha}\nTruncated: {str(truncated).lower()}\n"
                "Line IDs are immutable addresses for this Base SHA.\n"
                f"```text\n{chr(10).join(rendered)}{suffix}\n```"
            )
        return "\n\n".join(output)
