from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from types import SimpleNamespace

import pytest

from universal_coding_agent.core.models import RepositorySpec
from universal_coding_agent.core.safe_models import (
    ApprovedChangeManifest,
    ChangeOperation,
    ChangeScopeEntry,
    SafeModePolicy,
    SafeTaskRequest,
    TestProfile,
)
from universal_coding_agent.product.models import (
    AcceptanceCriterion,
    RequirementContract,
    RequirementItem,
    RequirementStatus,
)
from universal_coding_agent.product.program_source_acceptance import ProgramSourceAcceptanceService
from universal_coding_agent.product.program_source_attestation import (
    ProgramGitSourceAttestationService,
)
from universal_coding_agent.product.program_source_transitions import (
    ProgramSourceError,
    ProgramSourceIdentity,
)
from universal_coding_agent.product.workspace import ProductWorkspace
from universal_coding_agent.providers.fake import FakeModelProvider
from universal_coding_agent.safe.line_editing import line_id
from universal_coding_agent.safe_service import SafeAgentService


def _git(root, *args):
    return subprocess.run(["git", *args], cwd=root, check=True,
                          capture_output=True, text=True).stdout.strip()


class _ActualSafePort:
    """Host-provided approved scope; every execution result comes from the actual Safe graph."""

    def __init__(self, safe, base_sha, *, multi=False):
        self.safe, self.base_sha, self.multi = safe, base_sha, multi

    def start(self, **kwargs):
        task = SafeTaskRequest(
            task_id=kwargs["task_id"], thread_id=kwargs["thread_id"], title=kwargs["title"],
            objective=kwargs["objective"], repository=kwargs["repository"],
            policy=kwargs["policy"],
            manifest=ApprovedChangeManifest(
                base_sha=self.base_sha, plan_hash="d" * 64,
                allowed_changes=(ChangeScopeEntry(path="app.py", operation=ChangeOperation.MODIFY,
                                                  purpose="Change the approved answer."),) + (
                    (ChangeScopeEntry(path="notes.md", operation=ChangeOperation.MODIFY,
                                      purpose="Change the approved note."),) if self.multi else ()),
                acceptance_criteria=kwargs["acceptance_criteria"],
                test_profiles=kwargs["test_profiles"]))
        return self.safe.run(task)

    def resume(self, thread_id, approved):
        return self.safe.resume(thread_id, approved)


def _service(workspace, safe, source, policy):
    return ProgramSourceAcceptanceService(
        programs=workspace.programs, lifecycle=workspace.lifecycle_reservations, safe=safe,
        attestor=ProgramGitSourceAttestationService(
            source, hashlib.sha256(str(source).encode()).hexdigest()),
        repository_url=str(source), trusted_policy=policy)


@pytest.fixture
def executed(tmp_path, monkeypatch, request):
    options = getattr(request, "param", {})
    monkeypatch.setenv("UCA_SAFE_EDIT_PROTOCOL", options.get("protocol", "v1"))
    source = tmp_path / "source"
    source.mkdir()
    _git(source, "init", "-b", "fixture", "--object-format=" + options.get("object_format", "sha1"))
    _git(source, "config", "user.email", "fixture@example.test")
    _git(source, "config", "user.name", "Fixture")
    (source / "app.py").write_bytes(options.get("source", b"def answer():\n    return 42\n"))
    (source / "unchanged.bin").write_bytes(b"\0\xff\r\n")
    (source / "script.sh").write_bytes(b"#!/bin/sh\nexit 0\n")
    (source / "script.sh").chmod(0o755)
    if options.get("materialization_files"):
        (source / "nested" / "deeper").mkdir(parents=True)
        (source / "nested" / "kept.txt").write_bytes(b"CRLF\r\nno-final-LF")
        (source / "nested" / "deeper" / "empty.bin").write_bytes(b"")
    if options.get("multi"):
        (source / "notes.md").write_text("Status: old\n")
    _git(source, "add", ".")
    _git(source, "commit", "-m", "Complete source fixture")
    base = _git(source, "rev-parse", "HEAD")
    origin_base, origin_tree = base, _git(source, "rev-parse", "HEAD^{tree}")
    if options.get("execution_commit"):
        if options["execution_commit"] == "changed-tree":
            (source / "unchanged.bin").write_bytes(b"different untouched binary\0")
            _git(source, "add", "unchanged.bin")
        _git(source, "commit", "--allow-empty", "-m", "Distinct execution Base fixture")
        base = _git(source, "rev-parse", "HEAD")
    phases = [{"phase_id": "phase-1", "title": "Approved answer",
               "objective": "Change the answer from 42 to 43.", "dependencies": [],
               "slices": [], "acceptance_criteria": ["The answer is 43."]}]
    if options.get("open_program"):
        phases.append({"phase_id": "phase-2", "title": "Future bounded work",
                       "objective": "Plan a later change without executing it.",
                       "dependencies": ["phase-1"], "slices": [],
                       "acceptance_criteria": ["Future work is separately approved."]})

    def implementer(_request):
        old, new = "return 42", "return 43"
        if options.get("protocol") == "v2-line-addressed":
            token = line_id(2, "    return 42\n")
            old, new = f"@range:{token}..{token}", "    return 43\n"
        changes = [{"path": "app.py",
                "operation": "modify", "replacements": [{"old_text": old, "new_text": new}],
                "content": None}]
        if options.get("multi"):
            changes.insert(0, {"path": "notes.md", "operation": "modify", "content": None,
                               "replacements": [{"old_text": "old", "new_text": "new"}]})
        return {"summary": "Update the approved answer.", "edits": changes,
                "requested_test_profiles": ["python-check"], "assumptions": []}

    provider = FakeModelProvider(handlers={"implementer": implementer,
                                         "program_planner": lambda _request: {
        "title": "Source acceptance fixture", "objective": "Change the answer safely.",
        "phases": phases,
        "definition_of_done": ["The approved test passes."]}})
    workspace = ProductWorkspace.create(tmp_path / "state", provider)
    requirement = RequirementContract(
        alignment_id="source-acceptance-requirement", version=1, title="Source acceptance",
        objective="Change the answer from 42 to 43.",
        requirements=(RequirementItem(requirement_id="R-001", statement="Preserve exact source.",
                                      category="safety"),),
        acceptance_criteria=(AcceptanceCriterion(criterion_id="AC-001",
                                                statement="The answer is 43.",
                                                requirement_ids=("R-001",)),),
        status=RequirementStatus.APPROVED)
    plan = workspace.programs.create_program(program_id="source-program", requirement=requirement,
                                             requirement_hash=requirement.canonical_hash())
    workspace.programs.approve_program(plan.program_id, plan.canonical_hash())
    policy = SafeModePolicy(profiles=(TestProfile(
        profile_id="python-check", argv=(sys.executable, "-B", "-c",
                                         "from app import answer; assert answer() == 43")),))
    if options.get("extra_profile"):
        policy = SafeModePolicy(profiles=(*policy.profiles, TestProfile(
            profile_id="required-extra", argv=(sys.executable, "-c", "pass"))))
    safe = SafeAgentService.create(tmp_path / "safe", provider, allow_local_sources=True,
                                   control=workspace.control,
                                   remote_operations=workspace.remote_operations)
    owner = workspace.lifecycle_reservations.reserve_program_worker(plan.program_id)
    port = _ActualSafePort(safe, base, multi=options.get("multi", False))
    binding = workspace.programs.start_next_execution(
        program_id=plan.program_id, current_requirement_hash=requirement.canonical_hash(),
        repository=RepositorySpec(url=str(source), base_ref="fixture"), policy=policy,
        test_profiles=("python-check",), executor=port)
    binding = workspace.programs.continue_execution(
        program_id=plan.program_id, task_id=binding.task_id,
        current_requirement_hash=requirement.canonical_hash(), executor=port, approved=True)
    assert binding.status.value == "completed"
    acceptance = _service(workspace, safe, source, policy)
    identity = ProgramSourceIdentity(plan.program_id,
                                     hashlib.sha256(str(source).encode()).hexdigest(),
                                     requirement.canonical_hash(), plan.canonical_hash(),
                                     origin_base, origin_tree)
    acceptance.initialize(identity, owner_token=owner)
    value = SimpleNamespace(workspace=workspace, safe=safe, source=source, policy=policy,
                            acceptance=acceptance, identity=identity, owner=owner, binding=binding,
                            tmp_path=tmp_path, provider=provider)
    yield value
    acceptance.close()
    safe.close()
    workspace.close()


def _prepare(f):
    before = f.acceptance.current(f.identity.program_id)
    return f.acceptance.prepare(f.identity.program_id, f.binding.task_id, owner_token=f.owner,
                                expected_generation=before.generation,
                                expected_source_sha256=f.acceptance.source.snapshot_hash(before))


def _accept(f, candidate):
    return f.acceptance.accept(candidate["candidate_sha256"], owner_token=f.owner,
                               approved_transition_sha256=candidate["transition_sha256"],
                               approval_id="approval-one")


def test_actual_product_accepts_exact_bytes_and_replays_without_source_side_effects(executed):
    f = executed
    before = f.acceptance.current(f.identity.program_id)
    candidate = _prepare(f)
    assert f.acceptance.current(f.identity.program_id) == before
    assert f.owner not in json.dumps(candidate)
    receipt = _accept(f, candidate)
    after = f.acceptance.current(f.identity.program_id)
    assert after.generation == 1 and after.identity == before.identity
    assert after.predecessor_sha256 == f.acceptance.source.snapshot_hash(before)
    files = {item.path: item for item in after.files}
    assert files["app.py"].content == b"def answer():\n    return 43\n"
    assert files["unchanged.bin"].content == b"\0\xff\r\n"
    assert files["script.sh"].mode == "100755"
    assert receipt["materialization_ready"] is False
    assert _accept(f, candidate) == receipt
    assert f.acceptance.receipt(candidate["candidate_sha256"]) == receipt
    assert _git(f.source, "status", "--porcelain") == ""
    assert _git(f.source, "rev-parse", "HEAD") == f.identity.origin_base_sha
    assert (f.source / "app.py").read_bytes() == b"def answer():\n    return 42\n"
    with pytest.raises(ProgramSourceError, match="approval"):
        f.acceptance.accept(candidate["candidate_sha256"], owner_token=f.owner,
                            approved_transition_sha256=candidate["transition_sha256"],
                            approval_id="different-approval")


@pytest.mark.parametrize("field", ["tests_ref", "review_ref", "review_provenance_ref",
                                   "scope_ref", "scope_approval_ref", "patch_ref",
                                   "patch_proposal_ref", "patch_validation_ref", "final_report_ref",
                                   "reviewer_context_ref", "reviewer_validation_ref",
                                   "edit_proposal_ref"])
def test_actual_product_rejects_missing_task_owned_evidence(executed, field):
    f = executed
    state = f.safe.state(f.binding.thread_id)["values"]
    path = f.safe.artifacts.root / state[field].removeprefix("artifact://")
    path.unlink()
    with pytest.raises((ProgramSourceError, FileNotFoundError)):
        _prepare(f)
    assert f.acceptance.current(f.identity.program_id).generation == 0


@pytest.mark.parametrize("executed", [{"execution_commit": "same-tree"}], indirect=True)
def test_execution_commit_is_distinct_from_preserved_origin_identity(executed):
    f = executed
    candidate = _prepare(f)
    evidence = json.loads(f.acceptance._get(candidate["evidence_sha256"]))
    execution = evidence["safe"]["execution_base"]["identity"]
    assert execution["origin_base_sha"] != f.identity.origin_base_sha
    assert execution["origin_tree_sha"] == f.identity.origin_tree_sha
    _accept(f, candidate)
    assert f.acceptance.current(f.identity.program_id).identity == f.identity


@pytest.mark.parametrize("executed", [{"execution_commit": "changed-tree"}], indirect=True)
def test_untouched_execution_base_bytes_must_match_complete_cumulative_source(executed):
    with pytest.raises(ProgramSourceError, match="complete current cumulative source"):
        _prepare(executed)


@pytest.mark.parametrize("field", ["tests_ref", "review_ref", "review_provenance_ref",
                                   "scope_ref", "scope_approval_ref", "patch_ref",
                                   "patch_proposal_ref", "patch_validation_ref", "final_report_ref",
                                   "reviewer_context_ref", "reviewer_validation_ref",
                                   "edit_proposal_ref"])
def test_actual_product_rejects_evidence_drift_after_prepare(executed, field):
    f = executed
    candidate = _prepare(f)
    state = f.safe.state(f.binding.thread_id)["values"]
    path = f.safe.artifacts.root / state[field].removeprefix("artifact://")
    raw = path.read_bytes()
    path.write_bytes(raw + b" ")
    with pytest.raises((ProgramSourceError, ValueError)):
        _accept(f, candidate)
    assert f.acceptance.current(f.identity.program_id).generation == 0


def test_immutable_blob_corruption_rolls_back_acceptance(executed):
    f = executed
    candidate = _prepare(f)
    f.acceptance.connection.execute(
        "UPDATE program_source_artifacts SET content = ? WHERE sha256 = ?",
        (b"corrupted", candidate["after_sha256"]))
    with pytest.raises(ProgramSourceError, match="corrupt"):
        _accept(f, candidate)
    assert f.acceptance.current(f.identity.program_id).generation == 0
    assert f.acceptance.connection.execute(
        "SELECT count(*) FROM program_source_acceptances").fetchone()[0] == 0


def test_real_control_revision_and_owner_changes_reject_prepared_approval(executed):
    f = executed
    candidate = _prepare(f)
    f.workspace.lifecycle_reservations.release_program_worker(f.identity.program_id, f.owner)
    f.owner = f.workspace.lifecycle_reservations.reserve_program_worker(f.identity.program_id)
    with pytest.raises(ProgramSourceError, match="drifted"):
        _accept(f, candidate)
    assert f.acceptance.current(f.identity.program_id).generation == 0


@pytest.mark.parametrize("table,key,field,value", [
    ("control.control_state", "entity_id", "state", "cancelled"),
    ("control.control_state", "entity_id", "state", "paused"),
    ("control.control_state", "entity_id", "revision", 99),
    ("programs", "program_id", "status", "realignment_required"),
    ("programs", "program_id", "requirement_hash", "e" * 64),
    ("programs", "program_id", "plan_hash", "e" * 64),
])
def test_commit_checks_current_program_control_and_hashes(executed, table, key, field, value):
    f = executed
    candidate = _prepare(f)
    f.acceptance.connection.execute(f"UPDATE {table} SET {field} = ? WHERE {key} = ?",
                                    (value, f.identity.program_id))
    with pytest.raises(ProgramSourceError):
        _accept(f, candidate)
    assert f.acceptance.current(f.identity.program_id).generation == 0


def test_checkpoint_replacement_at_same_id_invalidates_candidate(executed):
    f = executed
    candidate = _prepare(f)
    f.acceptance.connection.execute("""UPDATE safe.checkpoints SET metadata = ?
        WHERE thread_id = ? AND checkpoint_id =
        (SELECT max(checkpoint_id) FROM safe.checkpoints WHERE thread_id = ?)""",
        (b'{"changed":true}', f.binding.thread_id, f.binding.thread_id))
    with pytest.raises(ProgramSourceError, match="drifted"):
        _accept(f, candidate)
    assert f.acceptance.current(f.identity.program_id).generation == 0


def test_fresh_connection_cannot_observe_uncommitted_head_and_sql_failure_is_atomic(executed):
    f = executed
    candidate = _prepare(f)
    reader = sqlite3.connect(f.workspace.programs.database_path)
    f.acceptance.connection.execute("""CREATE TEMP TRIGGER reject_source_update
        BEFORE UPDATE ON program_source_heads BEGIN SELECT RAISE(ABORT, 'fixture fault'); END""")
    with pytest.raises(ProgramSourceError, match="transaction"):
        _accept(f, candidate)
    assert reader.execute("SELECT generation FROM program_source_heads").fetchone()[0] == 0
    assert reader.execute("SELECT count(*) FROM program_source_acceptances").fetchone()[0] == 0
    reader.close()
    f.acceptance.connection.execute("DROP TRIGGER reject_source_update")
    assert _accept(f, candidate)["generation"] == 1


@pytest.mark.parametrize("executed", [{"extra_profile": True}], indirect=True)
def test_all_host_policy_profiles_are_required_even_if_safe_passed_a_subset(executed):
    with pytest.raises(ProgramSourceError, match="every host policy profile"):
        _prepare(executed)


@pytest.mark.parametrize("executed", [
    {"protocol": "v2-line-addressed"},
    {"source": b"def answer():\r\n    return 42\r\n"},
    {"source": b"def answer():\n    return 42"},
], indirect=True)
def test_actual_safe_protocol_and_exact_line_endings(executed):
    f = executed
    candidate = _prepare(f)
    _accept(f, candidate)
    actual = next(item for item in f.acceptance.current(f.identity.program_id).files
                  if item.path == "app.py").content
    assert actual == (f.source / "app.py").read_bytes().replace(b"42", b"43")


@pytest.mark.parametrize("field,value", [
    ("task_id", "other-task"), ("thread_id", "other-thread"),
    ("objective", "Different unapproved objective"),
])
def test_actual_checkpoint_cannot_substitute_another_task_or_objective(executed, field, value):
    f = executed
    state = f.safe.state(f.binding.thread_id)["values"]
    task = dict(state["task"])
    task[field] = value
    f.safe.graph.update_state({"configurable": {"thread_id": f.binding.thread_id}},
                              {"task": task}, as_node="finalize")
    with pytest.raises(ProgramSourceError):
        _prepare(f)


@pytest.mark.parametrize("field,value", [
    ("status", "blocked"), ("rolled_back", True), ("scope_approved", False),
    ("patch_applied", False), ("reviewer_verdict", "FAIL"),
    ("safe_errors", ["tests:failed"]), ("review_provenance_ref", "artifact://tasks/other/review.json"),
    ("edit_proposal_ref", "artifact://tasks/other/edit-proposal.json"),
    ("sandbox_path", "/different/repository"),
])
def test_incomplete_or_cross_task_checkpoint_cannot_supply_pass(executed, field, value):
    f = executed
    f.safe.graph.update_state({"configurable": {"thread_id": f.binding.thread_id}},
                              {field: value}, as_node="finalize")
    with pytest.raises(ProgramSourceError):
        _prepare(f)


@pytest.mark.parametrize("field", ["result_ref", "phase_report_ref"])
def test_program_reports_are_bound_and_retained(executed, field):
    f = executed
    candidate = _prepare(f)
    uri = getattr(f.binding, field)
    path = f.workspace.artifacts.root / uri.removeprefix("artifact://")
    path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises(ProgramSourceError, match="drifted"):
        _accept(f, candidate)


def test_source_worktree_and_git_helpers_cannot_bypass_acceptance(executed):
    f = executed
    sandbox = f.safe.artifacts.root.parent / "sandboxes" / f.binding.task_id / "repo"
    sentinel = f.tmp_path / "filter-executed"
    _git(sandbox, "config", "filter.tripwire.clean", f"touch {sentinel}")
    before_index = (sandbox / ".git" / "index").read_bytes()
    with pytest.raises(ProgramSourceError, match="filters"):
        _prepare(f)
    assert not sentinel.exists()
    assert (sandbox / ".git" / "index").read_bytes() == before_index
    _git(sandbox, "config", "--remove-section", "filter.tripwire")
    (sandbox / "app.py").write_text("def answer():\n    return 44\n")
    with pytest.raises(ProgramSourceError, match="drifted"):
        _prepare(f)


def test_two_independent_acceptance_connections_commit_one_identical_receipt(executed, monkeypatch):
    f = executed
    candidate = _prepare(f)
    second = _service(f.workspace, f.safe, f.source, f.policy)
    barrier = Barrier(2)
    for service in (f.acceptance, second):
        original = service._capture

        def capture(*args, _original=original):
            result = _original(*args)
            barrier.wait(timeout=10)
            return result

        monkeypatch.setattr(service, "_capture", capture)
    try:
        with ThreadPoolExecutor(2) as executor:
            futures = [executor.submit(
                service.accept, candidate["candidate_sha256"], owner_token=f.owner,
                approved_transition_sha256=candidate["transition_sha256"],
                approval_id="approval-one")
                for service in (f.acceptance, second)]
            receipts = [future.result(timeout=20) for future in futures]
        assert receipts[0] == receipts[1]
        assert second.current(f.identity.program_id).generation == 1
        assert second.connection.execute(
            "SELECT count(*) FROM program_source_acceptances").fetchone()[0] == 1
    finally:
        second.close()


def test_attached_transaction_holds_control_lifecycle_and_checkpoint_writers(executed):
    f = executed
    paths = [f.workspace.control.database_path, f.workspace.lifecycle_reservations.database_path,
             f.safe.artifacts.root.parent / "safe-checkpoints.sqlite"]
    with f.acceptance._transaction():
        for path in paths:
            competitor = sqlite3.connect(path, timeout=0.01, isolation_level=None)
            try:
                with pytest.raises(sqlite3.OperationalError, match="locked"):
                    competitor.execute("BEGIN IMMEDIATE")
            finally:
                competitor.close()


_RESTART = """
import json, os, sys
from pathlib import Path
from universal_coding_agent.product.workspace import ProductWorkspace
from universal_coding_agent.product.program_source_acceptance import ProgramSourceAcceptanceService
from universal_coding_agent.product.program_source_attestation import (
    ProgramGitSourceAttestationService)
from universal_coding_agent.core.safe_models import SafeModePolicy
from universal_coding_agent.providers.fake import FakeModelProvider
from universal_coding_agent.safe_service import SafeAgentService
payload = json.load(sys.stdin)
def forbidden(_request):
    raise AssertionError('restart must never invoke a provider')
provider = FakeModelProvider(handlers={role: forbidden for role in
    ('implementer', 'reviewer', 'program_planner', 'solution_architect', 'change_planner')})
workspace = ProductWorkspace.create(Path(payload['root']), provider)
safe = SafeAgentService.create(Path(payload['safe_root']), provider, control=workspace.control,
    remote_operations=workspace.remote_operations, allow_local_sources=True)
service = ProgramSourceAcceptanceService(programs=workspace.programs,
    lifecycle=workspace.lifecycle_reservations, safe=safe,
    attestor=ProgramGitSourceAttestationService(
        Path(payload['source']), payload['repository_sha256']),
    repository_url=payload['source'],
    trusted_policy=SafeModePolicy.model_validate(payload['policy']))
if payload['crash']:
    service.connection.create_function('crash_before_commit', 0, lambda: os._exit(73))
    service.connection.execute('''CREATE TEMP TRIGGER source_crash
        AFTER UPDATE ON program_source_heads
        BEGIN SELECT crash_before_commit(); END''')
    service.accept(payload['candidate_sha256'], owner_token=payload['owner'],
        approved_transition_sha256=payload['transition_sha256'], approval_id='approval-one')
else:
    before = service.current(payload['program_id'])
    result = {'generation': before.generation,
        'source_sha256': service.source.snapshot_hash(before)}
    if before.generation:
        result['receipt'] = service.receipt(payload['candidate_sha256'])
    print(json.dumps(result))
service.close()
safe.close()
workspace.close()
"""


def _restart(f, candidate, crash=False):
    data = {"root": str(f.workspace.root), "safe_root": str(f.safe.artifacts.root.parent),
            "source": str(f.source), "repository_sha256": f.identity.repository_sha256,
            "policy": f.policy.model_dump(mode="json"), "program_id": f.identity.program_id,
            "owner": f.owner, "crash": crash,
            "candidate_sha256": candidate["candidate_sha256"],
            "transition_sha256": candidate["transition_sha256"]}
    return subprocess.run([sys.executable, "-c", _RESTART], input=json.dumps(data),
                          capture_output=True, text=True, timeout=20)


def test_real_process_death_before_commit_and_fresh_process_read_only_reload(executed):
    f = executed
    candidate = _prepare(f)
    read = _restart(f, candidate)
    assert read.returncode == 0, read.stderr
    assert json.loads(read.stdout)["generation"] == 0
    crash = _restart(f, candidate, crash=True)
    assert crash.returncode == 73, crash.stderr
    assert f.acceptance.current(f.identity.program_id).generation == 0
    assert f.acceptance.connection.execute(
        "SELECT count(*) FROM program_source_acceptances").fetchone()[0] == 0
    receipt = _accept(f, candidate)
    read = _restart(f, candidate)
    assert read.returncode == 0, read.stderr
    result = json.loads(read.stdout)
    assert result["generation"] == 1 and result["receipt"] == receipt
    assert result["source_sha256"] == receipt["source_sha256"]


@pytest.mark.parametrize("executed", [{"open_program": True}], indirect=True)
@pytest.mark.parametrize("action", ["pause", "cancel", "realign", "pause-resume"])
def test_existing_program_control_apis_invalidate_source_candidate(executed, action):
    f = executed
    candidate = _prepare(f)
    if action == "realign":
        assert f.workspace.programs.require_realign(f.identity.program_id, "f" * 64)
    elif action == "cancel":
        f.workspace.programs.cancel(f.identity.program_id, reason="Fixture cancellation")
    else:
        f.workspace.programs.pause(f.identity.program_id, reason="Fixture pause")
        if action == "pause-resume":
            f.workspace.programs.resume(f.identity.program_id)
    with pytest.raises(ProgramSourceError):
        _accept(f, candidate)
    assert f.acceptance.current(f.identity.program_id).generation == 0
    assert len(f.workspace.programs.execution_bindings(f.identity.program_id)) == 1


@pytest.mark.parametrize("executed", [{"multi": True}], indirect=True)
def test_model_edit_order_does_not_change_canonical_manifest_patch_order(executed):
    f = executed
    candidate = _prepare(f)
    _accept(f, candidate)
    files = {item.path: item.content for item in f.acceptance.current(f.identity.program_id).files}
    assert files["notes.md"] == b"Status: new\n"
    assert files["app.py"] == b"def answer():\n    return 43\n"


def test_promisor_missing_object_cannot_fetch_during_retained_source_read(executed):
    f = executed
    sandbox = f.safe.artifacts.root.parent / "sandboxes" / f.binding.task_id / "repo"
    oid = _git(sandbox, "rev-parse", "HEAD:app.py")
    object_path = sandbox / ".git" / "objects" / oid[:2] / oid[2:]
    assert object_path.is_file()
    _git(sandbox, "config", "extensions.partialClone", "origin")
    _git(sandbox, "config", "remote.origin.promisor", "true")
    _git(sandbox, "config", "remote.origin.partialCloneFilter", "blob:none")
    _git(sandbox, "config", "protocol.file.allow", "always")
    object_path.unlink()
    with pytest.raises(ProgramSourceError):
        _prepare(f)
    assert not object_path.exists()
    assert f.acceptance.current(f.identity.program_id).generation == 0


@pytest.mark.parametrize("kind", ["assume-unchanged", "skip-worktree", "mode", "symlink"])
def test_full_retained_bytes_cannot_be_hidden_from_git_status(executed, kind):
    f = executed
    sandbox = f.safe.artifacts.root.parent / "sandboxes" / f.binding.task_id / "repo"
    if kind == "mode":
        _git(sandbox, "config", "core.filemode", "false")
        (sandbox / "script.sh").chmod(0o644)
    else:
        _git(sandbox, "update-index", "--" + (
            kind if kind != "symlink" else "assume-unchanged"), "unchanged.bin")
        file = sandbox / "unchanged.bin"
        if kind == "symlink":
            file.unlink()
            file.symlink_to(f.source / "unchanged.bin")
        else:
            file.write_bytes(b"bad\0")  # Same length: exercise byte equality, not just size.
    with pytest.raises(ProgramSourceError, match="retained source"):
        _prepare(f)
    assert f.acceptance.current(f.identity.program_id).generation == 0


def test_retained_read_allows_access_time_updates_without_source_drift(executed):
    f = executed
    sandbox = f.safe.artifacts.root.parent / "sandboxes" / f.binding.task_id / "repo"
    file = sandbox / "unchanged.bin"
    _git(sandbox, "update-index", "--assume-unchanged", "unchanged.bin")
    os.utime(file, ns=(0, file.stat().st_mtime_ns))
    candidate = _prepare(f)
    assert _accept(f, candidate)["generation"] == 1
