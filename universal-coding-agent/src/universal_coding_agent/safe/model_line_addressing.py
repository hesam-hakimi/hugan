from __future__ import annotations

import re

from universal_coding_agent.core.safe_models import TextReplacement
from universal_coding_agent.safe.line_editing import LineAddressedEditEngine, line_id

_MODEL_LINE_REF = r"A?[0-9]{6}"
_MODEL_RANGE = re.compile(
    rf"^@range:(?P<start>{_MODEL_LINE_REF})\.\.(?P<end>{_MODEL_LINE_REF})$"
)
_MODEL_BEFORE = re.compile(rf"^@before:(?P<anchor>{_MODEL_LINE_REF})$")
_MODEL_AFTER = re.compile(rf"^@after:(?P<anchor>{_MODEL_LINE_REF})$")


class ModelFacingLineAddressedEditEngine(LineAddressedEditEngine):
    """Accept compact model-facing line aliases and verify them against the frozen base.

    The model sees aliases such as ``A000123`` instead of a composite line-number/fingerprint
    token. Before the normal line-addressed validator runs, every alias is deterministically
    expanded to the full trusted ``L000123-<fingerprint>`` token from the current clean sandbox.
    The existing Base SHA, clean-worktree, scope, fingerprint, overlap, and EOL checks therefore
    remain authoritative while the model no longer needs to reproduce cryptographic fingerprints.
    """

    @classmethod
    def _resolve_replacements(
        cls,
        path: str,
        content: str,
        replacements,
    ):
        lines = content.splitlines(keepends=True)
        canonical: list[TextReplacement] = []
        for replacement in replacements:
            token = replacement.old_text.strip()
            normalized = cls._canonicalize_model_token(path, lines, token)
            canonical.append(replacement.model_copy(update={"old_text": normalized}))
        return super()._resolve_replacements(path, content, tuple(canonical))

    @classmethod
    def _canonicalize_model_token(
        cls,
        path: str,
        lines: list[str],
        token: str,
    ) -> str:
        range_match = _MODEL_RANGE.fullmatch(token)
        if range_match is not None:
            start = cls._trusted_line_id(path, lines, range_match.group("start"))
            end = cls._trusted_line_id(path, lines, range_match.group("end"))
            return f"@range:{start}..{end}"

        before_match = _MODEL_BEFORE.fullmatch(token)
        if before_match is not None:
            anchor = cls._trusted_line_id(path, lines, before_match.group("anchor"))
            return f"@before:{anchor}"

        after_match = _MODEL_AFTER.fullmatch(token)
        if after_match is not None:
            anchor = cls._trusted_line_id(path, lines, after_match.group("anchor"))
            return f"@after:{anchor}"

        # Preserve the original full protocol-v2 tokens for backward compatibility.
        return token

    @staticmethod
    def _trusted_line_id(path: str, lines: list[str], value: str) -> str:
        raw = value[1:] if value.startswith("A") else value
        line_number = int(raw)
        if line_number < 1 or line_number > len(lines):
            raise ValueError(f"model line reference is outside {path}: line {line_number}")
        return line_id(line_number, lines[line_number - 1])
