from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from universal_coding_agent.storage.artifacts import (
    ArtifactIntegrityError,
    ArtifactSizeLimitExceeded,
    ArtifactStore,
)


def test_verified_bounded_reads_return_bytes_text_and_json(tmp_path: Path) -> None:
    store = ArtifactStore(tmp_path / "artifacts")
    text_reference = store.write_text("tasks/task-1/evidence.txt", "trusted evidence")
    payload = {"approved": True, "patch_sha256": "a" * 64}
    json_reference = store.write_json("tasks/task-1/evidence.json", payload)

    assert (
        store.read_bytes_bounded_verified(
            text_reference,
            expected_sha256=text_reference.sha256,
            max_bytes=text_reference.size,
        )
        == b"trusted evidence"
    )
    assert (
        store.read_text_bounded_verified(
            text_reference.uri,
            expected_sha256=text_reference.sha256,
            max_bytes=text_reference.size,
        )
        == "trusted evidence"
    )
    assert (
        store.read_json_bounded_verified(
            json_reference,
            expected_sha256=json_reference.sha256,
            max_bytes=json_reference.size,
        )
        == payload
    )


@pytest.mark.parametrize(
    "expected_sha256",
    ["", "a" * 63, "A" * 64, "g" * 64],
)
def test_verified_bounded_read_rejects_invalid_expected_hash(
    tmp_path: Path,
    expected_sha256: str,
) -> None:
    store = ArtifactStore(tmp_path / "artifacts")
    reference = store.write_text("evidence.txt", "trusted evidence")

    with pytest.raises(
        ArtifactIntegrityError,
        match="expected artifact SHA-256",
    ):
        store.read_bytes_bounded_verified(
            reference,
            expected_sha256=expected_sha256,
            max_bytes=reference.size,
        )


def test_verified_bounded_read_rejects_oversize_before_hashing(tmp_path: Path) -> None:
    store = ArtifactStore(tmp_path / "artifacts")
    reference = store.write_text("evidence.txt", "trusted evidence")

    with pytest.raises(
        ArtifactSizeLimitExceeded,
        match="configured byte read limit",
    ):
        store.read_bytes_bounded_verified(
            reference,
            expected_sha256="0" * 64,
            max_bytes=reference.size - 1,
        )

    with pytest.raises(ValueError, match="read limit must be positive"):
        store.read_bytes_bounded_verified(
            reference,
            expected_sha256=reference.sha256,
            max_bytes=0,
        )


def test_verified_bounded_read_rejects_digest_mismatch(tmp_path: Path) -> None:
    store = ArtifactStore(tmp_path / "artifacts")
    reference = store.write_text("evidence.txt", "trusted evidence")

    with pytest.raises(ArtifactIntegrityError, match="does not match trusted evidence"):
        store.read_bytes_bounded_verified(
            reference,
            expected_sha256="0" * 64,
            max_bytes=reference.size,
        )


def test_verified_json_read_checks_integrity_before_decoding(tmp_path: Path) -> None:
    store = ArtifactStore(tmp_path / "artifacts")
    reference = store.write_json("evidence.json", {"approved": True})
    artifact_path = store.root / "evidence.json"
    tampered = b"x" * reference.size
    artifact_path.write_bytes(tampered)

    with pytest.raises(ArtifactIntegrityError, match="does not match trusted evidence"):
        store.read_json_bounded_verified(
            reference,
            expected_sha256=reference.sha256,
            max_bytes=reference.size,
        )

    with pytest.raises(json.JSONDecodeError):
        store.read_json_bounded_verified(
            reference,
            expected_sha256=hashlib.sha256(tampered).hexdigest(),
            max_bytes=reference.size,
        )
