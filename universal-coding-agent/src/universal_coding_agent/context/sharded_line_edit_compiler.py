from __future__ import annotations

import re
from pathlib import Path

from universal_coding_agent.context.line_edit_compiler import LineAddressedContextCompiler
from universal_coding_agent.core.models import ProjectManifest
from universal_coding_agent.core.safe_models import (
    SafeTaskRequest,
    StructuredEditProposal,
    safe_json,
)

_MODEL_LINE_ID = re.compile(r"(?m)^L([0-9]{6})-[0-9a-f]{16}(?= \|)")


class ShardedLineAddressedContextCompiler(LineAddressedContextCompiler):
    """Compile one bounded implementer context per approved file.

    Keeping each model call file-local prevents line-address tokens from one approved
    file being accidentally reused for another file and keeps real-project prompts
    substantially smaller than the all-files protocol-v2 prompt.
    """

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
        sections = [
            "# Safe task",
            task.objective,
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
            "# Exact assigned file state with deterministic model line refs",
            self._line_addressed_file_state(root, narrow_task),
            "# Mandatory structured-edit protocol v2",
            (
                "Return exactly one StructuredEditProposal JSON object with exactly one edit. "
                "TextReplacement.old_text must use model line refs copied exactly from the "
                "assigned file state above. A model line ref has the exact form A000123. "
                "Supported tokens are @range:A000123..A000125, @before:A000123, and "
                "@after:A000123. Never invent a line ref and never copy one from another file. "
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

    def _line_addressed_file_state(self, root: Path, task: SafeTaskRequest) -> str:
        rendered = super()._line_addressed_file_state(root, task)
        # Rewrite only the address prefix at the start of rendered state lines. Source text that
        # happens to contain an L000123-<fingerprint> string is left untouched after the separator.
        return _MODEL_LINE_ID.sub(r"A\1", rendered)
