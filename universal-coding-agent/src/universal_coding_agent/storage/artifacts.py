from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any

from universal_coding_agent.core.models import ArtifactReference

_SAFE_NAME = re.compile(r"^[a-zA-Z0-9._/-]+$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


class ArtifactSizeLimitExceeded(ValueError):
    """Raised before a caller can consume an oversized artifact payload."""


class ArtifactIntegrityError(ValueError):
    """Raised before decoding when artifact bytes do not match trusted evidence."""


class ArtifactStore:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def write_json(self, name: str, value: Any) -> ArtifactReference:
        data = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False).encode("utf-8")
        return self._write(name, data, "application/json")

    def write_text(
        self, name: str, value: str, media_type: str = "text/plain"
    ) -> ArtifactReference:
        return self._write(name, value.encode("utf-8"), media_type)

    def read_json(self, reference: str | ArtifactReference) -> Any:
        uri = reference.uri if isinstance(reference, ArtifactReference) else reference
        path = self._path_for(uri)
        return json.loads(path.read_text(encoding="utf-8"))

    def read_json_bounded(
        self,
        reference: str | ArtifactReference,
        *,
        max_bytes: int,
    ) -> Any:
        """Read JSON while consuming at most one byte beyond the caller's limit."""

        data = self._read_bytes_bounded(reference, max_bytes=max_bytes)
        return json.loads(data.decode("utf-8"))

    def read_bytes_bounded_verified(
        self,
        reference: str | ArtifactReference,
        *,
        expected_sha256: str,
        max_bytes: int,
    ) -> bytes:
        """Read bounded bytes only when they match the caller's trusted SHA-256."""

        if not isinstance(expected_sha256, str) or not _SHA256.fullmatch(
            expected_sha256
        ):
            raise ArtifactIntegrityError(
                "expected artifact SHA-256 must be 64 lowercase hexadecimal characters"
            )
        data = self._read_bytes_bounded(reference, max_bytes=max_bytes)
        actual_sha256 = hashlib.sha256(data).hexdigest()
        if not hmac.compare_digest(actual_sha256, expected_sha256):
            raise ArtifactIntegrityError("artifact SHA-256 does not match trusted evidence")
        return data

    def read_text_bounded_verified(
        self,
        reference: str | ArtifactReference,
        *,
        expected_sha256: str,
        max_bytes: int,
    ) -> str:
        """Verify bounded artifact bytes before decoding UTF-8 text."""

        data = self.read_bytes_bounded_verified(
            reference,
            expected_sha256=expected_sha256,
            max_bytes=max_bytes,
        )
        return data.decode("utf-8")

    def read_json_bounded_verified(
        self,
        reference: str | ArtifactReference,
        *,
        expected_sha256: str,
        max_bytes: int,
    ) -> Any:
        """Verify bounded artifact bytes before decoding UTF-8 JSON."""

        data = self.read_bytes_bounded_verified(
            reference,
            expected_sha256=expected_sha256,
            max_bytes=max_bytes,
        )
        return json.loads(data.decode("utf-8"))

    def read_text(self, reference: str | ArtifactReference) -> str:
        uri = reference.uri if isinstance(reference, ArtifactReference) else reference
        path = self._path_for(uri)
        return path.read_text(encoding="utf-8")

    def _read_bytes_bounded(
        self,
        reference: str | ArtifactReference,
        *,
        max_bytes: int,
    ) -> bytes:
        if max_bytes < 1:
            raise ValueError("artifact read limit must be positive")
        uri = reference.uri if isinstance(reference, ArtifactReference) else reference
        path = self._path_for(uri)
        with path.open("rb") as handle:
            data = handle.read(max_bytes + 1)
        if len(data) > max_bytes:
            raise ArtifactSizeLimitExceeded(
                "artifact exceeds the configured byte read limit"
            )
        return data

    def _write(self, name: str, data: bytes, media_type: str) -> ArtifactReference:
        relative = self._validate_name(name)
        path = (self.root / relative).resolve()
        self._assert_contained(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary = tempfile.mkstemp(prefix=".tmp-", dir=path.parent)
        try:
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
        digest = hashlib.sha256(data).hexdigest()
        return ArtifactReference(
            uri=f"artifact://{relative.as_posix()}",
            sha256=digest,
            media_type=media_type,
            size=len(data),
        )

    def _path_for(self, uri: str) -> Path:
        if not uri.startswith("artifact://"):
            raise ValueError("invalid artifact URI")
        relative = self._validate_name(uri.removeprefix("artifact://"))
        path = (self.root / relative).resolve()
        self._assert_contained(path)
        if not path.is_file():
            raise FileNotFoundError(uri)
        return path

    def _validate_name(self, value: str) -> Path:
        if not value or not _SAFE_NAME.fullmatch(value):
            raise ValueError("artifact name contains unsupported characters")
        path = Path(value)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError("artifact name escapes the store")
        return path

    def _assert_contained(self, path: Path) -> None:
        if path != self.root and self.root not in path.parents:
            raise ValueError("artifact path escapes the store")
