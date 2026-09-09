from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from dataclasses import FrozenInstanceError, replace

import pytest

from universal_coding_agent.product.program_source_transitions import (
    ProgramSourceEdit,
    ProgramSourceError,
    ProgramSourceFile,
    ProgramSourceIdentity,
    ProgramSourcePolicy,
    ProgramSourceSnapshot,
    ProgramSourceTransitionService,
)


def _identity(**changes) -> ProgramSourceIdentity:
    return replace(ProgramSourceIdentity("program-alpha", "1" * 64, "2" * 64, "3" * 64,
                                         "4" * 40, "5" * 40), **changes)


def _snapshot() -> ProgramSourceSnapshot:
    return ProgramSourceSnapshot(_identity(), (
        ProgramSourceFile("src/a.py", b"VALUE = 1\r\n"),
        ProgramSourceFile("src/remove.py", b"old\x00\xff"),
    ))


def _prepare(service, before, edits=None, **changes):
    if edits is None:
        edits = (ProgramSourceEdit("src/a.py", before.files[0].fingerprint(),
                                  ProgramSourceFile("src/a.py", b"VALUE = 2\r\n")),)
    kwargs = dict(expected_source_sha256=service.snapshot_hash(before), phase_id="phase-one",
                  task_id="task-one", allowed_paths=tuple(edit.path for edit in edits),
                  evidence_sha256=("6" * 64,), edits=edits)
    kwargs.update(changes)
    return service.prepare(before, **kwargs)


def test_cumulative_create_modify_delete_mode_and_rename_preserve_immutable_source():
    service = ProgramSourceTransitionService()
    before = _snapshot()
    original = service.snapshot_bytes(before)
    edits = (
        ProgramSourceEdit("bin/start.sh", None,
                          ProgramSourceFile("bin/start.sh", b"#!/bin/sh\nexit 0\n", "100755")),
        ProgramSourceEdit("src/a.py", before.files[0].fingerprint(),
                          ProgramSourceFile("src/a.py", b"VALUE = 2\r\n")),
        ProgramSourceEdit("src/remove.py", before.files[1].fingerprint(), None),
        ProgramSourceEdit("src/renamed.py", None,
                          ProgramSourceFile("src/renamed.py", before.files[1].content)),
    )
    transition = _prepare(service, before, edits)
    after = service.materialize(before, transition,
                                approved_transition_sha256=service.transition_hash(transition))
    assert after.identity == before.identity
    assert after.predecessor_sha256 == service.snapshot_hash(before)
    assert after.generation == 1
    assert [item.path for item in after.files] == ["bin/start.sh", "src/a.py", "src/renamed.py"]
    assert after.files[0].mode == "100755"
    assert after.files[1].content == b"VALUE = 2\r\n"
    assert after.files[2].content == b"old\x00\xff"
    assert service.snapshot_bytes(before) == original
    with pytest.raises(FrozenInstanceError):
        after.generation = 99
    with pytest.raises(FrozenInstanceError):
        after.files[0].content = b"changed"


def test_restart_roundtrip_exact_replay_rejects_a_noop_next_phase():
    first = ProgramSourceTransitionService()
    before = _snapshot()
    plan = _prepare(first, before)
    approved = first.transition_hash(plan)
    restarted = ProgramSourceTransitionService()
    loaded_before = restarted.load_snapshot(first.snapshot_bytes(before),
                                           expected_sha256=first.snapshot_hash(before))
    loaded_plan = restarted.load_transition(first.transition_bytes(plan), expected_sha256=approved)
    after = restarted.materialize(loaded_before, loaded_plan, approved_transition_sha256=approved)
    assert restarted.materialize(before, plan, approved_transition_sha256=approved) == after
    # A second phase must change the cumulative preimage, not silently reuse an old patch.
    with pytest.raises(ProgramSourceError, match="no effect"):
        _prepare(restarted, after, phase_id="phase-two", task_id="task-two")


def test_second_phase_extends_first_and_rejects_double_application():
    service = ProgramSourceTransitionService()
    before = _snapshot()
    plan = _prepare(service, before)
    after = service.materialize(before, plan,
                                approved_transition_sha256=service.transition_hash(plan))
    edit = ProgramSourceEdit("src/a.py", after.files[0].fingerprint(),
                             ProgramSourceFile("src/a.py", b"VALUE = 3\r\n"))
    second = _prepare(service, after, (edit,), phase_id="phase-two", task_id="task-two")
    final = service.materialize(after, second,
                                approved_transition_sha256=service.transition_hash(second))
    assert final.generation == 2
    assert final.files[0].content == b"VALUE = 3\r\n"
    assert final.predecessor_sha256 == service.snapshot_hash(after)
    assert final.identity.origin_base_sha == before.identity.origin_base_sha
    with pytest.raises(ProgramSourceError, match="snapshot drift"):
        service.materialize(after, plan, approved_transition_sha256=service.transition_hash(plan))


@pytest.mark.parametrize("field,value", [
    ("program_id", "program-other"), ("repository_sha256", "a" * 64),
    ("requirement_sha256", "a" * 64), ("plan_sha256", "a" * 64),
    ("origin_base_sha", "a" * 40), ("origin_tree_sha", "a" * 40),
])
def test_source_identity_drift_rejects_exact_approval(field, value):
    service = ProgramSourceTransitionService()
    before = _snapshot()
    plan = _prepare(service, before)
    drifted = replace(before, identity=replace(before.identity, **{field: value}))
    with pytest.raises(ProgramSourceError, match="snapshot drift"):
        service.materialize(drifted, plan,
                            approved_transition_sha256=service.transition_hash(plan))


@pytest.mark.parametrize("field,value", [
    ("phase_id", "other-phase"), ("slice_id", "other-slice"), ("task_id", "other-task"),
    ("evidence_sha256", ("a" * 64,)), ("after_sha256", "a" * 64),
    ("allowed_paths", ("src/a.py", "src/extra.py")),
])
def test_every_transition_identity_is_bound_to_approval(field, value):
    service = ProgramSourceTransitionService()
    before = _snapshot()
    plan = _prepare(service, before)
    with pytest.raises(ProgramSourceError, match="approval mismatch"):
        service.materialize(before, replace(plan, **{field: value}),
                            approved_transition_sha256=service.transition_hash(plan))


def test_policy_and_result_drift_cannot_be_bypassed_by_rehashing():
    service = ProgramSourceTransitionService()
    before = _snapshot()
    plan = _prepare(service, before)
    different = ProgramSourceTransitionService(ProgramSourcePolicy(max_changes=5))
    with pytest.raises(ProgramSourceError, match="policy drift"):
        different.materialize(before, plan,
                              approved_transition_sha256=service.transition_hash(plan))
    wrong_result = replace(plan, after_sha256="a" * 64)
    with pytest.raises(ProgramSourceError, match="result mismatch"):
        service.materialize(before, wrong_result,
                            approved_transition_sha256=service.transition_hash(wrong_result))


@pytest.mark.parametrize("kind", ["missing", "incorrect", "mode", "create-existing", "noop"])
def test_preimage_conflicts_fail_closed_without_changing_input(kind):
    service = ProgramSourceTransitionService()
    before = _snapshot()
    original = service.snapshot_bytes(before)
    file = before.files[0]
    path = "src/missing.py" if kind == "missing" else file.path
    fingerprint = None if kind == "create-existing" else file.fingerprint()
    if kind == "incorrect":
        fingerprint = "0" * 64
    if kind == "mode":
        fingerprint = replace(file, mode="100755").fingerprint()
    replacement = file if kind == "noop" else ProgramSourceFile(path, b"new")
    with pytest.raises(ProgramSourceError, match="preimage|no effect"):
        _prepare(service, before, (ProgramSourceEdit(path, fingerprint, replacement),))
    assert service.snapshot_bytes(before) == original


def test_exact_scope_no_glob_no_duplicate_edits_and_no_empty_evidence():
    service = ProgramSourceTransitionService()
    before = _snapshot()
    with pytest.raises(ProgramSourceError, match="outside exact"):
        _prepare(service, before, allowed_paths=("src/other.py",))
    with pytest.raises(ProgramSourceError):
        _prepare(service, before, allowed_paths=("src/*.py",))
    edit = ProgramSourceEdit("src/a.py", before.files[0].fingerprint(), None)
    with pytest.raises(ProgramSourceError, match="unique and sorted"):
        _prepare(service, before, (edit, edit))
    with pytest.raises(ProgramSourceError, match="evidence"):
        _prepare(service, before, evidence_sha256=())


@pytest.mark.parametrize("path", ["/a", "../a", "a/../b", "a//b", "a/", "a\\b", "C:/a",
                                  ".git/config", "a/.GIT/config", "a/NUL.txt", "CON", "a.",
                                  "a\x00b", "a\nb", "a b", "a/./b", "x/" * 65 + "a"])
def test_unsafe_or_unsupported_paths_are_rejected(path):
    with pytest.raises(ProgramSourceError):
        ProgramSourceFile(path, b"data")


@pytest.mark.parametrize("mode", ["120000", "160000", "100600", 100644, None])
def test_symlinks_gitlinks_and_unsupported_modes_are_rejected(mode):
    with pytest.raises(ProgramSourceError):
        ProgramSourceFile("a", b"data", mode)


@pytest.mark.parametrize("paths", [("A.py", "a.py"), ("a", "a/b.py"), ("Src/a.py", "src/b.py")])
def test_portable_path_collisions_and_file_directory_conflicts_fail(paths):
    service = ProgramSourceTransitionService()
    before = ProgramSourceSnapshot(
        _identity(), tuple(ProgramSourceFile(path, b"x") for path in paths)
    )
    with pytest.raises(ProgramSourceError, match="collision|conflict"):
        service.snapshot_bytes(before)


@pytest.mark.parametrize("policy,files", [
    (ProgramSourcePolicy(max_files=1),
     (ProgramSourceFile("a", b"x"), ProgramSourceFile("b", b"x"))),
    (ProgramSourcePolicy(max_file_bytes=1), (ProgramSourceFile("a", b"xx"),)),
    (ProgramSourcePolicy(max_total_bytes=1),
     (ProgramSourceFile("a", b"x"), ProgramSourceFile("b", b"x"))),
    (ProgramSourcePolicy(max_artifact_bytes=10), ()),
])
def test_each_snapshot_bound_fails(policy, files):
    with pytest.raises(ProgramSourceError, match="exceeded"):
        service = ProgramSourceTransitionService(policy)
        service.snapshot_bytes(ProgramSourceSnapshot(_identity(), files))


@pytest.mark.parametrize("field", ["max_files", "max_changes", "max_file_bytes", "max_total_bytes",
                                    "max_artifact_bytes"])
@pytest.mark.parametrize("value", [True, 0, -1, 1.5, 64_000_001])
def test_policy_limits_reject_invalid_values(field, value):
    with pytest.raises(ProgramSourceError):
        ProgramSourcePolicy(**{field: value})


def test_bounds_fail_before_exposing_transition_and_after_cumulative_growth():
    service = ProgramSourceTransitionService(ProgramSourcePolicy(max_changes=1, max_total_bytes=30))
    before = _snapshot()
    with pytest.raises(ProgramSourceError, match="count exceeded"):
        _prepare(service, before, allowed_paths=("src/a.py", "src/extra.py"))
    edit = ProgramSourceEdit("new.py", None, ProgramSourceFile("new.py", b"x" * 25))
    with pytest.raises(ProgramSourceError, match="total bytes"):
        _prepare(service, before, (edit,))


def _encoded(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode("ascii")


def test_snapshot_and_transition_artifacts_reject_hash_drift_and_oversize():
    service = ProgramSourceTransitionService()
    before = _snapshot()
    plan = _prepare(service, before)
    for loader, payload in [(service.load_snapshot, service.snapshot_bytes(before)),
                            (service.load_transition, service.transition_bytes(plan))]:
        with pytest.raises(ProgramSourceError, match="hash mismatch"):
            loader(payload + b" ", expected_sha256=hashlib.sha256(payload).hexdigest())
        with pytest.raises(ProgramSourceError):
            loader(b"[]", expected_sha256=hashlib.sha256(b"[]").hexdigest())
    tiny = ProgramSourceTransitionService(ProgramSourcePolicy(max_artifact_bytes=10))
    payload = service.snapshot_bytes(before)
    with pytest.raises(ProgramSourceError, match="artifact bytes"):
        tiny.load_snapshot(payload, expected_sha256=hashlib.sha256(payload).hexdigest())


@pytest.mark.parametrize("kind", ["unknown", "duplicate", "noncanonical", "base64", "fields",
                                  "mutable-type", "generation", "extra-identity", "schema"])
def test_snapshot_parser_rejects_malformed_noncanonical_or_extra_fields(kind):
    service = ProgramSourceTransitionService()
    original = service.snapshot_bytes(_snapshot())
    data = json.loads(original)
    if kind == "unknown":
        data["extra"] = True
    elif kind == "base64":
        data["files"][0]["content"] = "%%%%"
    elif kind == "fields":
        data["files"][0]["extra"] = True
    elif kind == "mutable-type":
        data["files"] = {}
    elif kind == "generation":
        data["generation"] = True
    elif kind == "extra-identity":
        data["identity"]["extra"] = True
    elif kind == "schema":
        data["schema"] = "2"
    payload = _encoded(data)
    if kind == "duplicate":
        payload = original[:-1] + b',"schema":"uca-source-snapshot-1"}'
    elif kind == "noncanonical":
        payload += b"\n"
    with pytest.raises(ProgramSourceError):
        service.load_snapshot(payload, expected_sha256=hashlib.sha256(payload).hexdigest())


def test_loaded_transition_revalidates_scope_preimage_and_serialization():
    service = ProgramSourceTransitionService()
    before = _snapshot()
    plan = _prepare(service, before)
    for key, value in [("allowed_paths", []), ("evidence_sha256", []), ("edits", {}),
                       ("policy_sha256", "f" * 64), ("extra", True)]:
        data = json.loads(service.transition_bytes(plan))
        data[key] = value
        payload = _encoded(data)
        with pytest.raises(ProgramSourceError):
            service.load_transition(payload, expected_sha256=hashlib.sha256(payload).hexdigest())


def test_snapshot_cannot_use_mutable_content_collections_or_invalid_lineage():
    with pytest.raises(ProgramSourceError):
        ProgramSourceFile("a", bytearray(b"x"))
    with pytest.raises(ProgramSourceError):
        ProgramSourceSnapshot(_identity(), [])
    with pytest.raises(ProgramSourceError):
        ProgramSourceSnapshot(_identity(), (), predecessor_sha256="a" * 64)
    with pytest.raises(ProgramSourceError):
        ProgramSourceSnapshot(_identity(), (), generation=1)


def test_serialized_source_and_approval_replay_in_a_fresh_python_process():
    service = ProgramSourceTransitionService()
    before = _snapshot()
    plan = _prepare(service, before)
    approval = service.transition_hash(plan)
    envelope = {
        "snapshot": service.snapshot_bytes(before).decode("ascii"),
        "snapshot_hash": service.snapshot_hash(before),
        "transition": service.transition_bytes(plan).decode("ascii"),
        "approval": approval,
    }
    script = """
import json
import sys
from universal_coding_agent.product.program_source_transitions import ProgramSourceTransitionService
service = ProgramSourceTransitionService()
data = json.load(sys.stdin)
before = service.load_snapshot(data["snapshot"].encode("ascii"),
                               expected_sha256=data["snapshot_hash"])
plan = service.load_transition(data["transition"].encode("ascii"), expected_sha256=data["approval"])
after = service.materialize(before, plan, approved_transition_sha256=data["approval"])
sys.stdout.buffer.write(service.snapshot_bytes(after))
"""
    result = subprocess.run([sys.executable, "-c", script], input=json.dumps(envelope).encode(),
                            capture_output=True, check=True, timeout=15)
    expected = service.materialize(before, plan, approved_transition_sha256=approval)
    assert result.stdout == service.snapshot_bytes(expected)
    assert result.stderr == b""


def test_large_source_and_generation_exhaustion_fail_without_output():
    before = _snapshot()
    service = ProgramSourceTransitionService()
    exhausted = replace(before, generation=10_000, predecessor_sha256="a" * 64)
    with pytest.raises(ProgramSourceError, match="generation"):
        _prepare(service, exhausted)
    data = json.loads(service.snapshot_bytes(before))
    data["files"][0]["content"] = "a" * 100
    payload = _encoded(data)
    tiny = ProgramSourceTransitionService(ProgramSourcePolicy(max_file_bytes=2))
    with pytest.raises(ProgramSourceError, match="encoding"):
        tiny.load_snapshot(payload, expected_sha256=hashlib.sha256(payload).hexdigest())


def test_conflicting_delete_create_is_an_explicit_rename_not_a_fuzzy_patch():
    service = ProgramSourceTransitionService()
    before = ProgramSourceSnapshot(_identity(), (ProgramSourceFile("a", b"x"),))
    edits = (ProgramSourceEdit("a", before.files[0].fingerprint(), None),
             ProgramSourceEdit("a/b", None, ProgramSourceFile("a/b", b"x")))
    plan = _prepare(service, before, edits)
    after = service.materialize(before, plan,
                                approved_transition_sha256=service.transition_hash(plan))
    assert after.files == (ProgramSourceFile("a/b", b"x"),)
    conflicting = (ProgramSourceEdit("a/b", None, ProgramSourceFile("a/b", b"x")),)
    with pytest.raises(ProgramSourceError, match="file/directory"):
        _prepare(service, before, conflicting)


def test_product_lazy_export_exposes_the_same_pure_service():
    from universal_coding_agent.product import ProgramSourceTransitionService as PublicService

    assert PublicService is ProgramSourceTransitionService


_IDENTIFIER_CASES = [
    ("program_id", "ab", False), ("program_id", "abc", True),
    ("program_id", "a" * 128, True), ("program_id", "a" * 129, False),
    ("program_id", "-abc", False), ("program_id", "A_b.c-7", True),
    ("task_id", "ab", False), ("task_id", "abc", True),
    ("task_id", "a" * 128, True), ("task_id", "a" * 129, False),
    ("task_id", "-abc", False), ("task_id", "A_b.c-7", True),
    ("phase_id", "a", False), ("phase_id", "ab", True),
    ("phase_id", "a" * 64, True), ("phase_id", "a" * 65, False),
    ("phase_id", "-abc", False), ("phase_id", "A_b.c-7", True),
    ("slice_id", None, True), ("slice_id", "", False),
    ("slice_id", "a", True), ("slice_id", "a" * 64, True),
    ("slice_id", "a" * 65, False), ("slice_id", "opaque label", True),
    ("slice_id", "\u03b1", True), ("slice_id", "-x", True),
]


def _source_accepts_identifier(field, value):
    service = ProgramSourceTransitionService()
    before = _snapshot()
    plan = _prepare(service, before)
    try:
        if field == "program_id":
            changed = replace(before, identity=replace(before.identity, program_id=value))
            loaded = service.load_snapshot(service.snapshot_bytes(changed),
                                           expected_sha256=service.snapshot_hash(changed))
        else:
            changed = replace(plan, **{field: value})
            loaded = service.load_transition(service.transition_bytes(changed),
                                             expected_sha256=service.transition_hash(changed))
    except ProgramSourceError:
        return False
    assert loaded == changed
    return True


@pytest.mark.parametrize("field,value,accepted", _IDENTIFIER_CASES)
def test_role_specific_identifiers_match_boundary_contract(field, value, accepted):
    assert _source_accepts_identifier(field, value) is accepted


@pytest.mark.parametrize("field,value,accepted", _IDENTIFIER_CASES)
def test_serialized_identifier_bounds_cannot_bypass_constructors(field, value, accepted):
    service = ProgramSourceTransitionService()
    before = _snapshot()
    if field == "program_id":
        data = json.loads(service.snapshot_bytes(before))
        data["identity"][field] = value
        loader = service.load_snapshot
    else:
        data = json.loads(service.transition_bytes(_prepare(service, before)))
        data[field] = value
        loader = service.load_transition
    payload = _encoded(data)
    digest = hashlib.sha256(payload).hexdigest()
    if accepted:
        loader(payload, expected_sha256=digest)
    else:
        with pytest.raises(ProgramSourceError):
            loader(payload, expected_sha256=digest)


@pytest.mark.parametrize("field,value,accepted", _IDENTIFIER_CASES)
def test_existing_program_binding_identifier_compatibility(field, value, accepted):
    # This contract test must run against the actual complete-checkout Product model.
    from universal_coding_agent.product.models import ProgramExecutionBinding

    payload = dict(program_id="program-alpha", task_id="task-alpha", phase_id="phase-alpha",
                   slice_id=None, thread_id="thread-alpha", requirement_hash="a" * 64,
                   status="starting")
    payload[field] = value
    try:
        ProgramExecutionBinding(**payload)
        existing_accepted = True
    except ValueError:
        existing_accepted = False
    assert existing_accepted is accepted
    assert _source_accepts_identifier(field, value) is existing_accepted
