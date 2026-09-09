"""PR29 correction: missing committed preparation and predecessor links fail closed."""

from __future__ import annotations

import hashlib
import json

import pytest
from test_program_source_acceptance_v2 import counts, decide, preview
from test_program_source_acceptance_v2 import qualified as qualified

from universal_coding_agent.product.program_source_acceptance_v2_store import Reader


def damage_preview(f, prepared, target):
    db = f.store.connection
    if target == "request":
        db.execute("DELETE FROM program_source_requests_v2 WHERE action='preview'")
    elif target == "pending":
        db.execute("UPDATE program_source_requests_v2 SET status='pending' WHERE action='preview'")
    elif target == "owner":
        db.execute(
            "UPDATE program_source_requests_v2 SET owner_sha256=? WHERE action='preview'",
            ("0" * 64,),
        )
    else:
        value = (
            prepared["witness_sha256"]
            if target == "witness"
            else db.execute(
                "SELECT response_sha256 FROM program_source_requests_v2 WHERE action='preview'"
            ).fetchone()[0]
        )
        db.execute("DELETE FROM program_source_artifacts WHERE sha256=?", (value,))


@pytest.mark.parametrize("target", ["request", "response", "witness", "pending", "owner"])
@pytest.mark.parametrize("stage", ["before_decision", "after_accept", "after_reject"])
def test_a03_a04_a10_complete_preview_is_required(qualified, target, stage):
    f, operation, completed = qualified
    prepared = preview(f, operation, completed)
    approved = stage != "after_reject"
    if stage != "before_decision":
        decide(f, prepared, approved=approved)
    expected = counts(f)
    damage_preview(f, prepared, target)
    with pytest.raises(ValueError):
        decide(f, prepared, approved=approved)
    with pytest.raises(ValueError):
        f.acceptance2.source_transition_status(f.identity.program_id)
    assert counts(f) == expected


@pytest.mark.parametrize("approved", [False, True])
def test_a10_status_requires_recorded_decision_request(qualified, approved):
    f, operation, completed = qualified
    prepared = preview(f, operation, completed)
    decide(f, prepared, approved=approved)
    expected = counts(f)
    f.store.connection.execute("DELETE FROM program_source_requests_v2 WHERE action='decide'")
    with pytest.raises(ValueError):
        f.acceptance2.source_transition_status(f.identity.program_id)
    assert counts(f) == expected


@pytest.mark.parametrize("target", ["request", "response"])
def test_a04_a06_preview_loss_between_captures_retains_pending_owner(qualified, target):
    f, operation, completed = qualified
    prepared = preview(f, operation, completed)

    def boundary(name):
        if name == "capture_returned":
            damage_preview(f, prepared, target)

    f.acceptance2.db.boundary = boundary
    with pytest.raises(ValueError):
        decide(f, prepared)
    assert counts(f) == (1, 1, 1)
    assert f.store.connection.execute(
        "SELECT status,response_sha256 FROM program_source_requests_v2 WHERE action='decide'"
    ).fetchone()[:] == ("pending", None)


@pytest.mark.parametrize(
    "target",
    ["before_sha256", "after_sha256", "transition_sha256", "checkpoint_sha256", "evidence_sha256"],
)
@pytest.mark.parametrize("stage", ["before_preview", "before_decision", "after_accept"])
def test_a04_a05_a10_predecessor_artifact_links_are_complete(qualified, target, stage):
    f, operation, completed = qualified
    head = f.store.connection.execute("SELECT * FROM program_source_heads").fetchone()
    first = json.loads(f.store._get(head["receipt_sha256"]))
    candidate = json.loads(f.store._get(first["candidate_sha256"]))
    prepared = None if stage == "before_preview" else preview(f, operation, completed)
    if stage == "after_accept":
        decide(f, prepared)
    expected = counts(f)
    f.store.connection.execute(
        "DELETE FROM program_source_artifacts WHERE sha256=?", (candidate[target],)
    )
    with pytest.raises(ValueError):
        if prepared is None:
            preview(f, operation, completed)
        else:
            decide(f, prepared)
    with pytest.raises(ValueError):
        f.acceptance2.source_transition_status(f.identity.program_id)
    # current() itself requires the source blob; inspect the unchanged row for
    # the missing-current-snapshot case instead of attempting its decode.
    assert (
        f.store.connection.execute("SELECT generation FROM program_source_heads").fetchone()[0]
        == expected[0]
    )
    assert (
        f.workspace.lifecycle_reservations.connection.execute(
            "SELECT count(*) FROM lifecycle_worker_ownership"
        ).fetchone()[0]
        == expected[1]
    )
    assert (
        f.store.connection.execute("SELECT count(*) FROM program_source_acceptances").fetchone()[0]
        == expected[2]
    )


@pytest.mark.parametrize(
    "target",
    [
        "origin_sha256",
        "inventory_sha256",
        "program_evidence_sha256",
        "transition_sha256",
        "after_sha256",
    ],
)
def test_a04_a10_candidate_core_opaque_artifacts_are_hash_verified(qualified, target):
    f, operation, completed = qualified
    prepared = preview(f, operation, completed)
    core = json.loads(f.store._get(prepared["candidate"]["core_sha256"]))
    f.store.connection.execute(
        "UPDATE program_source_artifacts SET content=? WHERE sha256=?", (b"corrupt", core[target])
    )
    with pytest.raises(ValueError, match="artifact hash"):
        decide(f, prepared)
    with pytest.raises(ValueError, match="artifact hash"):
        f.acceptance2.source_transition_status(f.identity.program_id)
    assert counts(f) == (1, 0, 1)


def test_a11_opaque_artifact_bounds_are_distinct_from_small_metadata(qualified):
    f, _, _ = qualified
    raw = b"x" * 200_000
    value = hashlib.sha256(raw).hexdigest()
    f.store._put(raw)
    reader = Reader(f.store.connection)
    reader.artifact(value)
    assert reader.artifact_total == len(raw) and reader.total == 0
    with pytest.raises(ValueError, match="byte bound"):
        reader.raw(value)
    with pytest.raises(ValueError, match="exceeds bound"):
        reader.artifact(value, maximum=100)
    reader = Reader(f.store.connection)
    reader.artifact_total = 256_000_000
    with pytest.raises(ValueError, match="aggregate bound"):
        reader.artifact(value)
    f.store.connection.execute(
        "UPDATE program_source_artifacts SET content=zeroblob(24000001) WHERE sha256=?", (value,)
    )
    with pytest.raises(ValueError, match="oversized"):
        Reader(f.store.connection).artifact(value)
