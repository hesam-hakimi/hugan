from __future__ import annotations

import re

_REPLACEMENTS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"(?i)(authorization\s*:\s*bearer\s+)[A-Za-z0-9._~+\-/=]+"), r"\1<REDACTED>"),
    (re.compile(r"\b(?:ghp|ghs|github_pat)_[A-Za-z0-9_]{20,}\b"), "<REDACTED_GITHUB_TOKEN>"),
    (
        re.compile(
            r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----.*?"
            r"-----END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
            re.DOTALL,
        ),
        "<REDACTED_PRIVATE_KEY>",
    ),
    (
        re.compile(
            r"(?i)\b(password|passwd|pwd|client_secret|api_key|access_token)\s*[:=]\s*([^\s,;]+)"
        ),
        r"\1=<REDACTED>",
    ),
    (re.compile(r"(?i)([?&](?:sig|se|sp|sv|srt|spr)=)[^&\s]+"), r"\1<REDACTED>"),
)


def sanitize_text(value: str) -> str:
    """Redact common secret shapes from otherwise allowed text.

    Path denial remains the primary control. Sanitization is defense in depth and must not be
    used as justification to read a denied file.
    """

    result = value
    for pattern, replacement in _REPLACEMENTS:
        result = pattern.sub(replacement, result)
    return result
