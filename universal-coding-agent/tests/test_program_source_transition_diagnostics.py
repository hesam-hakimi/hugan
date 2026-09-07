from __future__ import annotations

import hashlib
import json

import pytest

from universal_coding_agent.product.program_source_transitions import (
    ProgramSourceEdit,
    ProgramSourceError,
    ProgramSourceFile,
    ProgramSourceIdentity,
    ProgramSourceSnapshot,
    ProgramSourceTransitionService,
)


def _encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")


@pytest.mark.parametrize("kind,location,field", [
    ("snapshot", (), "schema"),
    ("snapshot", ("identity",), "program_id"),
    ("snapshot", ("files", 0), "path"),
    ("transition", (), "schema"),
    ("transition", ("edits", 0), "path"),
    ("transition", ("edits", 0, "replacement"), "path"),
])
def test_duplicate_field_contract_reason_survives_json_hook(kind, location, field):
    service = ProgramSourceTransitionService()
    before = ProgramSourceSnapshot(
        ProgramSourceIdentity("program-test", "1" * 64, "2" * 64, "3" * 64,
                              "4" * 40, "5" * 40),
        (ProgramSourceFile("a.py", b"old\n"),),
    )
    plan = service.prepare(
        before, expected_source_sha256=service.snapshot_hash(before),
        phase_id="phase-test", task_id="task-test", allowed_paths=("a.py",),
        evidence_sha256=("6" * 64,),
        edits=(ProgramSourceEdit("a.py", before.files[0].fingerprint(),
                                ProgramSourceFile("a.py", b"new\n")),),
    )
    if kind == "snapshot":
        payload, loader = service.snapshot_bytes(before), service.load_snapshot
    else:
        payload, loader = service.transition_bytes(plan), service.load_transition
    selected = json.loads(payload)
    for component in location:
        selected = selected[component]
    original = _encode(selected)
    assert payload.count(original) == 1
    duplicate = original[:-1] + b"," + _encode(field) + b":" + _encode(selected[field]) + b"}"
    payload = payload.replace(original, duplicate, 1)
    with pytest.raises(ProgramSourceError, match="^duplicate source artifact field$") as failure:
        loader(payload, expected_sha256=hashlib.sha256(payload).hexdigest())
    assert failure.value.__cause__ is None


def test_malformed_json_still_has_a_typed_parse_failure_cause():
    service = ProgramSourceTransitionService()
    payload = b"{"
    with pytest.raises(ProgramSourceError, match="^invalid source artifact JSON$") as failure:
        service.load_snapshot(payload, expected_sha256=hashlib.sha256(payload).hexdigest())
    assert isinstance(failure.value.__cause__, json.JSONDecodeError)
