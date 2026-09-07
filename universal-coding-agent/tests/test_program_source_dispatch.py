from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from test_program_source_acceptance import _git, _service

from universal_coding_agent.core.models import RepositorySpec
from universal_coding_agent.core.safe_models import SafeModePolicy, TestProfile
from universal_coding_agent.discovered_safe_service import DiscoveredSafeAgentService
from universal_coding_agent.product.models import (
    AcceptanceCriterion,
    RequirementContract,
    RequirementItem,
    RequirementStatus,
)
from universal_coding_agent.product.program_execution_base import ProgramExecutionBaseService
from universal_coding_agent.product.program_orchestrator import ProgramExecutionError
from universal_coding_agent.product.program_source_dispatch import ProgramSourceDispatchService
from universal_coding_agent.product.program_source_materialization import (
    ProgramSourceMaterializationService,
)
from universal_coding_agent.product.program_source_transitions import (
    ProgramSourceError,
    ProgramSourceIdentity,
    _canonical,
    _hash,
)
from universal_coding_agent.product.workspace import ProductWorkspace
from universal_coding_agent.providers.fake import FakeModelProvider
from universal_coding_agent.safe_service import SafeAgentService


def runtime(root, expected, *, create=False, failure="", protocol="v1", object_format="sha1"):
    os.environ["UCA_SAFE_EDIT_PROTOCOL"] = protocol
    source = root / "source"
    events = root / "calls.jsonl"

    def log(request):
        with events.open("a") as f:
            f.write(json.dumps({"role": request.role, "expected": expected}) + "\n")

    def discovery(request):
        log(request)
        assert f"return {expected}" in request.user_prompt
        return {
            "summary": "Change the current approved answer in app.py.",
            "components": ["app.py"],
            "changes": [
                {
                    "path": "app.py",
                    "operation": "modify",
                    "component": "app.py",
                    "confidence": "high",
                    "rationale": "The answer is here.",
                    "evidence_paths": ["app.py"],
                }
            ],
            "rejected_candidates": [],
        }

    def implement(request):
        log(request)
        assert f"return {expected}" in request.user_prompt
        old, new = f"return {expected}", f"return {expected + 1}"
        if protocol == "v2-line-addressed":
            match = re.search(rf"(?m)^(A[0-9]{{6}}) \|     return {expected}$", request.user_prompt)
            assert match
            old, new = f"@range:{match[1]}..{match[1]}", f"    return {expected + 1}\n"
        return {
            "summary": "Increment the current answer.",
            "edits": [
                {
                    "path": "app.py",
                    "operation": "modify",
                    "content": None,
                    "replacements": [{"old_text": old, "new_text": new}],
                }
            ],
            "requested_test_profiles": ["increment", "preserved"],
            "assumptions": [],
        }

    def review(request):
        log(request)
        assert f"return {expected + 1}" in request.user_prompt
        return {
            "verdict": "FAIL" if failure == "review" else "PASS",
            "required_actions": ["Reject this fixture."] if failure == "review" else [],
            "confidence": "high",
        }

    phases = [
        {
            "phase_id": f"phase-{i}",
            "title": f"Answer {n + 1}",
            "objective": f"Change answer in app.py from {n} to {n + 1}.",
            "dependencies": [] if i == 1 else ["phase-1"],
            "slices": [],
            "acceptance_criteria": [f"The answer is {n + 1}."],
        }
        for i, n in ((1, 42), (2, 43))
    ]
    provider = FakeModelProvider(
        {
            "solution_discovery": discovery,
            "implementer": implement,
            "reviewer": review,
            "program_planner": lambda _: {
                "title": "Cumulative answer",
                "objective": "Increment twice with exact acceptance.",
                "phases": phases,
                "definition_of_done": ["Accept tested and reviewed 44."],
            },
        }
    )
    if create:
        source.mkdir(parents=True)
        (source / "app.py").write_bytes(b"def answer():\n    return 42\n")
        (source / "binary.bin").write_bytes(b"\0\xff\r\n")
        (source / "empty.bin").write_bytes(b"")
        (source / "crlf.txt").write_bytes(b"first\r\nlast")
        (source / "run.sh").write_bytes(b"#!/bin/sh\nexit 0\n")
        (source / "run.sh").chmod(0o755)
        _git(source, "init", "-b", "fixture", "--object-format=" + object_format)
        _git(source, "config", "user.name", "Fixture")
        _git(source, "config", "user.email", "fixture@example.test")
        _git(source, "add", ".")
        _git(source, "commit", "-m", "Original 42")
    workspace = ProductWorkspace.create(root / "product", provider)
    policy = SafeModePolicy(
        profiles=(
            TestProfile(
                profile_id="increment",
                argv=(
                    sys.executable,
                    "-B",
                    "-c",
                    "import subprocess; from app import answer; ns={}; "
                    "exec(subprocess.check_output(['git','show','HEAD:app.py']),ns); "
                    "assert answer() == ns['answer']()+1",
                ),
            ),
            TestProfile(
                profile_id="preserved",
                argv=(
                    sys.executable,
                    "-B",
                    "-c",
                    "from pathlib import Path; "
                    "assert Path('binary.bin').read_bytes() == b'\\0\\xff\\r\\n'; "
                    "assert Path('crlf.txt').read_bytes() == b'first\\r\\nlast'; "
                    "assert Path('empty.bin').read_bytes() == b''; "
                    "assert Path('run.sh').stat().st_mode & 0o111",
                ),
            ),
        )
    )
    safe = SafeAgentService.create(
        root / "safe",
        provider,
        allow_local_sources=True,
        control=workspace.control,
        remote_operations=workspace.remote_operations,
    )
    store = _service(workspace, safe, source, policy)
    base = ProgramExecutionBaseService(ProgramSourceMaterializationService(store))
    dispatch = ProgramSourceDispatchService(base, provider)
    if create:
        requirement = RequirementContract(
            alignment_id="cumulative-requirement",
            version=1,
            title="Cumulative source",
            objective="Change the answer from 42 to 44 in two phases.",
            requirements=(
                RequirementItem(
                    requirement_id="R-001", statement="Use accepted source.", category="safety"
                ),
            ),
            acceptance_criteria=(
                AcceptanceCriterion(
                    criterion_id="AC-001",
                    statement="The final answer is 44.",
                    requirement_ids=("R-001",),
                ),
            ),
            status=RequirementStatus.APPROVED,
        )
        plan = workspace.programs.create_program(
            program_id="cumulative-program",
            requirement=requirement,
            requirement_hash=requirement.canonical_hash(),
        )
        workspace.programs.approve_program(plan.program_id, plan.canonical_hash())
        owner = workspace.lifecycle_reservations.reserve_program_worker(plan.program_id)
        identity = ProgramSourceIdentity(
            plan.program_id,
            hashlib.sha256(str(source).encode()).hexdigest(),
            requirement.canonical_hash(),
            plan.canonical_hash(),
            _git(source, "rev-parse", "HEAD"),
            _git(source, "rev-parse", "HEAD^{tree}"),
        )
        store.initialize(identity, owner_token=owner)
        (root / "fixture.json").write_text(json.dumps({"owner": owner}))
    else:
        owner = json.loads((root / "fixture.json").read_text())["owner"]
        identity = store.current("cumulative-program").identity
    return SimpleNamespace(
        root=root,
        source=source,
        workspace=workspace,
        safe=safe,
        store=store,
        base=base,
        dispatch=dispatch,
        provider=provider,
        policy=policy,
        owner=owner,
        identity=identity,
    )


def close(f):
    f.store.close()
    f.safe.close()
    f.workspace.close()


def accept(f, task, approval):
    before = f.store.current(f.identity.program_id)
    candidate = f.store.prepare(
        f.identity.program_id,
        task,
        owner_token=f.owner,
        expected_generation=before.generation,
        expected_source_sha256=f.store.source.snapshot_hash(before),
    )
    receipt = f.store.accept(
        candidate["candidate_sha256"],
        owner_token=f.owner,
        approved_transition_sha256=candidate["transition_sha256"],
        approval_id=approval,
    )
    return candidate, receipt


def first_phase(f, *, admit=True):
    port = DiscoveredSafeAgentService.create(
        f.root / "safe",
        f.provider,
        allow_local_sources=True,
        control=f.workspace.control,
        remote_operations=f.workspace.remote_operations,
    )
    binding = f.workspace.programs.start_next_execution(
        program_id=f.identity.program_id,
        current_requirement_hash=f.identity.requirement_sha256,
        repository=RepositorySpec(url=str(f.source), base_ref="fixture"),
        policy=f.policy,
        test_profiles=tuple(f.policy.profile_map()),
        executor=port,
    )
    assert binding.status.value == "awaiting_scope_approval"
    binding = f.workspace.programs.continue_execution(
        program_id=f.identity.program_id,
        task_id=binding.task_id,
        current_requirement_hash=f.identity.requirement_sha256,
        executor=port,
        approved=True,
    )
    assert binding.status.value == "completed"
    _, receipt = accept(f, binding.task_id, "approve-43")
    m = f.base.materialization.begin(
        f.identity.program_id,
        acceptance_receipt_sha256=_hash(_canonical(receipt)),
        owner_token=f.owner,
    )
    f.base.materialization.reconcile(m["operation_id"], owner_token=f.owner)
    b = f.base.begin(m["operation_id"], owner_token=f.owner)
    prepared = f.base.reconcile(b["operation_id"], owner_token=f.owner)
    if admit:
        f.dispatch.admit(
            b["operation_id"],
            owner_token=f.owner,
            preparation_receipt_sha256=_hash(_canonical(prepared)),
        )
    return b["operation_id"]


@pytest.fixture
def admitted(tmp_path):
    f = runtime(tmp_path, 42, create=True)
    operation = first_phase(f)
    close(f)
    f = runtime(tmp_path, 43)
    f.operation = operation
    yield f
    close(f)


def _qualify_44(f):
    started = f.dispatch.dispatch(f.operation, owner_token=f.owner)
    assert started["state"] == "awaiting_scope_approval"
    task = f.dispatch._json(started["task_sha256"])
    assert task["repository"]["url"] == str(f.source)
    scope = f.safe.state(task["thread_id"])["values"]["scope_hash"]
    assert not f.safe.state(task["thread_id"])["values"].get("patch_applied")
    with pytest.raises(ProgramSourceError):
        f.base.verify_complete(f.operation, owner_token=f.owner)
    final = f.dispatch.approve_scope(
        f.operation, owner_token=f.owner, scope_sha256=scope, approved=True, approval_id="scope-44"
    )
    assert final["state"] == "terminal"
    candidate, receipt = accept(f, final["task_id"], "approve-44")
    assert receipt["generation"] == 2
    after = f.store.current(f.identity.program_id)
    assert next(x.content for x in after.files if x.path == "app.py").endswith(b"return 44\n")
    assert after.identity == f.identity
    assert (f.source / "app.py").read_bytes().endswith(b"return 42\n")
    assert _git(f.source, "status", "--porcelain") == ""
    assert f.workspace.programs.status(f.identity.program_id).value == "completed"
    evidence = f.dispatch._json(candidate["evidence_sha256"])
    assert evidence["schema"] == "uca-program-safe-source-evidence-2"
    assert evidence["safe"]["schema"] == "uca-safe-source-evidence-2"
    admission = evidence["safe"]["admission"]
    assert admission["source_sha256"] == receipt["predecessor_sha256"]
    assert admission["origin_base_sha"] != admission["derived_git_commit_sha"]


@pytest.mark.parametrize("failure", ["reject", "review", "tests"])
def test_failed_later_phase_preserves_accepted_source_and_rolls_back_owned_base(admitted, failure):
    f = admitted
    if failure == "review":
        replacement = runtime(f.root, 43, failure="review")
        f.dispatch.provider = replacement.provider
        close(replacement)
    if failure == "tests":
        original = f.provider._handlers["implementer"]

        def wrong(request):
            value = original(request)
            value["edits"][0]["replacements"][0]["new_text"] = "return 45"
            return value

        f.provider._handlers["implementer"] = wrong
        f.provider._handlers["reviewer"] = lambda _: {"verdict": "PASS", "confidence": "high"}
    status = f.dispatch.dispatch(f.operation, owner_token=f.owner)
    task = f.dispatch._json(status["task_sha256"])
    scope = f.safe.state(task["thread_id"])["values"]["scope_hash"]
    result = f.dispatch.approve_scope(
        f.operation,
        owner_token=f.owner,
        scope_sha256=scope,
        approved=failure != "reject",
        approval_id="reject-or-fail",
    )
    assert result["state"] == "terminal"
    assert f.store.current(f.identity.program_id).generation == 1
    assert f.workspace.programs.status(f.identity.program_id).value == "blocked"
    repo = f.base.filesystem.root / ("execution-" + f.operation) / "repo"
    assert (repo / "app.py").read_bytes().endswith(b"return 43\n")
    assert (f.source / "app.py").read_bytes().endswith(b"return 42\n")
    with pytest.raises(ProgramSourceError):
        accept(f, result["task_id"], "cannot-accept-failed")


@pytest.mark.parametrize(
    "drift",
    [
        "owner",
        "pause-resume",
        "cancel",
        "realign",
        "head",
        "missing",
        "extra",
        "same-bytes",
        "metadata",
        "symlink",
    ],
)
def test_admitted_authority_and_full_base_are_rechecked_before_discovery(admitted, drift):
    f = admitted
    calls = (f.root / "calls.jsonl").read_bytes()
    repo = f.base.filesystem.root / ("execution-" + f.operation) / "repo"
    token = f.owner
    if drift == "owner":
        token = "f" * 32
    elif drift == "pause-resume":
        f.workspace.programs.pause(f.identity.program_id)
        f.workspace.programs.resume(f.identity.program_id)
    elif drift == "cancel":
        f.workspace.programs.cancel(f.identity.program_id)
    elif drift == "realign":
        f.workspace.programs.require_realign(f.identity.program_id, "f" * 64)
    elif drift == "head":
        f.store.connection.execute("UPDATE program_source_heads SET generation = 9")
    elif drift == "missing":
        (repo / "empty.bin").unlink()
    elif drift == "extra":
        (repo / "extra.txt").write_bytes(b"unexpected")
    elif drift == "same-bytes":
        (repo / "binary.bin").write_bytes((repo / "binary.bin").read_bytes())
    elif drift == "metadata":
        (repo / ".git/config").write_text("[core]\nfilemode=false\n")
    else:
        (repo / "binary.bin").unlink()
        (repo / "binary.bin").symlink_to(f.source / "binary.bin")
    with pytest.raises(ProgramSourceError):
        f.dispatch.dispatch(f.operation, owner_token=token)
    assert (f.root / "calls.jsonl").read_bytes() == calls
    assert f.dispatch.status(f.operation)["state"] == "admitted"


def test_v1_paths_and_copied_task_cannot_consume_v2_authority(admitted):
    f = admitted
    started = f.dispatch.dispatch(f.operation, owner_token=f.owner)
    task = f.dispatch._json(started["task_sha256"])
    with pytest.raises(ValueError, match="explicit v2"):
        f.safe.resume(task["thread_id"], True)
    with pytest.raises(ProgramExecutionError, match="explicit v2"):
        f.workspace.programs.continue_execution(
            program_id=f.identity.program_id,
            task_id=task["task_id"],
            current_requirement_hash=f.identity.requirement_sha256,
            executor=object(),
            approved=True,
        )
    with pytest.raises(ProgramSourceError, match="scope hash"):
        f.dispatch.approve_scope(
            f.operation,
            owner_token=f.owner,
            scope_sha256="f" * 64,
            approved=True,
            approval_id="wrong-scope",
        )
    assert not f.safe.state(task["thread_id"])["values"].get("patch_applied")


_PROCESS = r"""
import json, os, sys
from pathlib import Path
from test_program_source_dispatch import runtime, first_phase, close, accept
from universal_coding_agent.product.program_source_dispatch import AdmittedSafeExecution
from universal_coding_agent.safe.testing import SafeTestRunner
p=json.load(sys.stdin)
root=Path(p['root'])
f=runtime(root, 42 if p['action']=='init' else 43, create=p['action']=='init')
def die(*args, **kwargs):
    os._exit(73)
if p['action']=='init':
    if p.get('crash')=='admission-update':
        f.store.connection.create_function('die',0,die)
        f.store.connection.execute('CREATE TEMP TRIGGER crash AFTER INSERT ON '
            'program_source_dispatches BEGIN SELECT die(); END')
    elif p.get('crash')=='admission-commit':
        original=f.dispatch.admit
        def admit(*args,**kwargs):
            original(*args,**kwargs)
            die()
        f.dispatch.admit=admit
    operation=first_phase(f)
    (root/'operation.txt').write_text(operation)
    print(json.dumps({'operation_id':operation}))
else:
    operation=(root/'operation.txt').read_text()
    crash=p.get('crash','')
    if crash in ('discovery','implementer','reviewer'):
        invoke=f.provider.invoke
        def call(request):
            if request.role==('solution_discovery' if crash=='discovery' else crash):
                with (root/'calls.jsonl').open('a') as out:
                    out.write(json.dumps({'role':request.role,'crashed':True})+'\n')
                die()
            return invoke(request)
        f.provider.invoke=call
    elif crash in ('discovery-result','safe-intent'):
        name='discovery_completed' if crash=='discovery-result' else 'start_safe'
        original=getattr(AdmittedSafeExecution,name)
        def call(self,*args,**kwargs):
            original(self,*args,**kwargs)
            die()
        setattr(AdmittedSafeExecution,name,call)
    elif crash=='scope-intent':
        AdmittedSafeExecution.entry=die
    elif crash in ('scope-checkpoint','terminal-checkpoint'):
        f.dispatch.reconcile=die
    elif crash in ('apply-effect','review-result'):
        original=AdmittedSafeExecution.node
        def node(self,name,state,action):
            if crash=='apply-effect' and name=='apply_edits':
                def effect(s):
                    action(s)
                    die()
                return original(self,name,state,effect)
            result=original(self,name,state,action)
            if crash=='review-result' and name=='review':die()
            return result
        AdmittedSafeExecution.node=node
    elif crash=='tests':
        SafeTestRunner.run_profiles=die
    if crash in ('scope-update','record-update','accept-update'):
        f.store.connection.create_function('die',0,die)
        trigger={
          'scope-update':("AFTER UPDATE ON program_source_dispatches "
                          "WHEN NEW.state='resume_started'"),
          'record-update':"AFTER UPDATE ON program_executions WHEN NEW.safe_status='completed'",
          'accept-update':"AFTER UPDATE ON program_source_heads WHEN NEW.generation=2",
        }[crash]
        f.store.connection.execute('CREATE TEMP TRIGGER crash '+trigger+' BEGIN SELECT die(); END')
    action=p['action']
    if action=='status':
        f.provider.invoke=die
        def forbidden(*a,**k):raise AssertionError('status must not inspect or recover source')
        f.base.filesystem.root_handle=f.base.materialization.filesystem.root_handle=forbidden
        result=f.dispatch.status(operation)
    elif action=='dispatch':result=f.dispatch.dispatch(operation,owner_token=f.owner)
    elif action=='reconcile':
        f.provider.invoke=die
        result=f.dispatch.reconcile(operation,owner_token=f.owner)
    elif action=='approve':
        row=f.dispatch.status(operation)
        task=f.dispatch._json(row['task_sha256'])
        scope=f.safe.state(task['thread_id'])['values']['scope_hash']
        result=f.dispatch.approve_scope(operation,owner_token=f.owner,scope_sha256=scope,
            approved=True,approval_id='scope-44')
    elif action=='prepare':
        before=f.store.current(f.identity.program_id)
        result=f.store.prepare(f.identity.program_id,f.dispatch.status(operation)['task_id'],
            owner_token=f.owner,expected_generation=before.generation,
            expected_source_sha256=f.store.source.snapshot_hash(before))
        (root/'candidate.json').write_text(json.dumps(result))
        if crash=='candidate-commit':die()
    elif action=='accept':
        candidate=json.loads((root/'candidate.json').read_text())
        result=f.store.accept(candidate['candidate_sha256'],owner_token=f.owner,
            approved_transition_sha256=candidate['transition_sha256'],approval_id='approve-44')
        if crash=='accept-commit':die()
    else:raise AssertionError(action)
    print(json.dumps(result))
close(f)
"""


def process(root, action, crash="", *, expected=0):
    result = subprocess.run(
        [sys.executable, "-c", _PROCESS],
        input=json.dumps({"root": str(root), "action": action, "crash": crash}),
        env={**os.environ, "PYTHONPATH": str(Path(__file__).parent.resolve())},
        capture_output=True,
        text=True,
        timeout=30,
    )
    if expected is not None:
        assert result.returncode == expected, result.stderr
    return result


def test_genuinely_fresh_processes_accept_complete_42_43_44_lineage(tmp_path):
    process(tmp_path, "init")
    calls = (tmp_path / "calls.jsonl").read_bytes()
    status = json.loads(process(tmp_path, "status").stdout)
    assert status["state"] == "admitted"
    assert (tmp_path / "calls.jsonl").read_bytes() == calls
    process(tmp_path, "dispatch")
    process(tmp_path, "approve")
    process(tmp_path, "prepare")
    receipt = json.loads(process(tmp_path, "accept").stdout)
    assert receipt["generation"] == 2
    assert json.loads(process(tmp_path, "accept").stdout) == receipt
    observed = [json.loads(line) for line in (tmp_path / "calls.jsonl").read_text().splitlines()]
    assert [(r["role"], r["expected"]) for r in observed] == [
        (role, expected)
        for expected in (42, 43)
        for role in ("solution_discovery", "implementer", "reviewer")
    ]
    f = runtime(tmp_path, 43)
    try:
        after = f.store.current(f.identity.program_id)
        assert after.generation == 2 and after.predecessor_sha256 == receipt["predecessor_sha256"]
        assert next(x.content for x in after.files if x.path == "app.py").endswith(b"return 44\n")
        assert (f.source / "app.py").read_bytes().endswith(b"return 42\n")
    finally:
        close(f)


@pytest.mark.parametrize(
    "crash,state,recoverable",
    [
        ("discovery", "discovery_started", False),
        ("discovery-result", "discovered", True),
        ("safe-intent", "safe_started", False),
        ("scope-checkpoint", "safe_started", True),
    ],
)
def test_process_death_during_discovery_and_safe_handoff(admitted, crash, state, recoverable):
    f = admitted
    (f.root / "operation.txt").write_text(f.operation)
    process(f.root, "dispatch", crash, expected=73)
    calls = (f.root / "calls.jsonl").read_bytes()
    assert json.loads(process(f.root, "status").stdout)["state"] == state
    assert (f.root / "calls.jsonl").read_bytes() == calls
    action = "dispatch" if state == "discovered" else "reconcile"
    result = process(f.root, action, expected=0 if recoverable else None)
    if recoverable:
        assert json.loads(result.stdout)["state"] == "awaiting_scope_approval"
    else:
        assert result.returncode != 0
    assert (f.root / "calls.jsonl").read_bytes() == calls
    assert f.store.current(f.identity.program_id).generation == 1


@pytest.mark.parametrize(
    "crash,recoverable",
    [
        ("scope-update", True),
        ("scope-intent", False),
        ("implementer", False),
        ("apply-effect", False),
        ("tests", False),
        ("reviewer", False),
        ("review-result", False),
        ("terminal-checkpoint", True),
        ("record-update", True),
    ],
)
def test_process_death_after_scope_never_repeats_ambiguous_work(admitted, crash, recoverable):
    f = admitted
    (f.root / "operation.txt").write_text(f.operation)
    process(f.root, "dispatch")
    process(f.root, "approve", crash, expected=73)
    calls = (f.root / "calls.jsonl").read_bytes()
    status = json.loads(process(f.root, "status").stdout)
    assert (f.root / "calls.jsonl").read_bytes() == calls
    if crash == "scope-update":
        assert status["state"] == "awaiting_scope_approval"
        process(f.root, "approve")
    else:
        result = process(f.root, "reconcile", expected=0 if recoverable else None)
        if recoverable:
            assert json.loads(result.stdout)["state"] == "terminal"
        else:
            assert result.returncode != 0
        assert (f.root / "calls.jsonl").read_bytes() == calls
    assert f.store.current(f.identity.program_id).generation == 1


@pytest.mark.parametrize("crash", ["candidate-commit", "accept-update", "accept-commit"])
def test_process_death_at_capture_and_exact_source_acceptance(admitted, crash):
    f = admitted
    (f.root / "operation.txt").write_text(f.operation)
    process(f.root, "dispatch")
    process(f.root, "approve")
    process(
        f.root,
        "prepare",
        "candidate-commit" if crash == "candidate-commit" else "",
        expected=73 if crash == "candidate-commit" else 0,
    )
    if crash != "candidate-commit":
        process(f.root, "accept", crash, expected=73)
    assert f.store.current(f.identity.program_id).generation == (
        2 if crash == "accept-commit" else 1
    )
    calls = (f.root / "calls.jsonl").read_bytes()
    result = json.loads(process(f.root, "accept").stdout)
    assert result["generation"] == 2
    assert (f.root / "calls.jsonl").read_bytes() == calls


@pytest.mark.parametrize("bad", ["receipt", "owner", "missing", "host", "transaction"])
def test_consumption_rejects_forged_authority_and_is_atomic_across_stores(tmp_path, bad):
    f = runtime(tmp_path, 42, create=True)
    try:
        operation = first_phase(f, admit=False)
        receipt_sha = f.base.status(operation)["completion_sha256"]
        target = f.dispatch
        if bad == "host":
            from universal_coding_agent.sandbox.owned_source import OwnedSourcePolicy

            target = ProgramSourceDispatchService(
                ProgramExecutionBaseService(
                    f.base.materialization, OwnedSourcePolicy(operation_seconds=61)
                ),
                f.provider,
            )
        if bad == "transaction":
            f.store.connection.execute("""CREATE TEMP TRIGGER reject_consumption
                BEFORE INSERT ON program_source_dispatches
                BEGIN SELECT RAISE(ABORT, 'Injected atomic consumption failure'); END""")
        before_calls = (f.root / "calls.jsonl").read_bytes()
        with pytest.raises(ProgramSourceError):
            target.admit(
                "f" * 32 if bad == "missing" else operation,
                preparation_receipt_sha256="f" * 64 if bad == "receipt" else receipt_sha,
                owner_token="f" * 32 if bad == "owner" else f.owner,
            )
        assert (f.root / "calls.jsonl").read_bytes() == before_calls
        assert (
            f.workspace.programs.phase_status(f.identity.program_id, "phase-2").value == "pending"
        )
        assert len(f.workspace.programs.execution_bindings(f.identity.program_id)) == 1
        assert (
            f.store.connection.execute(
                "SELECT count(*) FROM control.uca_source_dispatch_tasks"
            ).fetchone()[0]
            == 0
        )
        assert (
            f.store.connection.execute("SELECT count(*) FROM program_source_dispatches").fetchone()[
                0
            ]
            == 0
        )
        if bad == "transaction":
            f.store.connection.execute("DROP TRIGGER reject_consumption")
        f.dispatch.admit(operation, preparation_receipt_sha256=receipt_sha, owner_token=f.owner)
    finally:
        close(f)


def test_independent_connections_consume_one_binding(tmp_path):
    from concurrent.futures import ThreadPoolExecutor

    f = runtime(tmp_path, 42, create=True)
    operation = first_phase(f, admit=False)
    other = runtime(tmp_path, 43)
    try:
        digest = f.base.status(operation)["completion_sha256"]
        with ThreadPoolExecutor(2) as pool:
            jobs = [
                pool.submit(
                    service.admit, operation, preparation_receipt_sha256=digest, owner_token=f.owner
                )
                for service in (f.dispatch, other.dispatch)
            ]
            results = [job.result(timeout=20) for job in jobs]
        assert results[0] == results[1]
        assert len(f.workspace.programs.execution_bindings(f.identity.program_id)) == 2
        assert (
            f.store.connection.execute("SELECT count(*) FROM program_source_dispatches").fetchone()[
                0
            ]
            == 1
        )
    finally:
        close(other)
        close(f)


@pytest.mark.parametrize(
    "action,role", [("dispatch", "solution_discovery"), ("approve", "implementer")]
)
def test_independent_duplicate_calls_cannot_repeat_provider_work(admitted, action, role):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Event

    f = admitted
    other = runtime(f.root, 43)
    entered, release = Event(), Event()
    invoke = f.provider.invoke

    def blocked(request):
        if request.role == role:
            entered.set()
            assert release.wait(10)
        return invoke(request)

    f.provider.invoke = blocked
    try:
        scope = None
        if action == "approve":
            started = f.dispatch.dispatch(f.operation, owner_token=f.owner)
            task = f.dispatch._json(started["task_sha256"])
            scope = f.safe.state(task["thread_id"])["values"]["scope_hash"]

        def call(service):
            if action == "dispatch":
                return service.dispatch(f.operation, owner_token=f.owner)
            return service.approve_scope(
                f.operation,
                owner_token=f.owner,
                scope_sha256=scope,
                approved=True,
                approval_id="only-scope",
            )

        with ThreadPoolExecutor(2) as pool:
            first = pool.submit(call, f.dispatch)
            assert entered.wait(10)
            try:
                with pytest.raises(ProgramSourceError):
                    call(other.dispatch)
            finally:
                release.set()
            assert first.result(timeout=20)["state"] in {"awaiting_scope_approval", "terminal"}
        events = [json.loads(line) for line in (f.root / "calls.jsonl").read_text().splitlines()]
        assert sum(event["role"] == role and event["expected"] == 43 for event in events) == 1
    finally:
        release.set()
        close(other)


@pytest.mark.parametrize("role", ["solution_discovery", "implementer", "reviewer"])
def test_control_revision_change_during_provider_cannot_advance_acceptance(admitted, role):
    f = admitted
    invoke = f.provider.invoke

    def drift(request):
        result = invoke(request)
        if request.role == role:
            f.workspace.programs.pause(f.identity.program_id)
            f.workspace.programs.resume(f.identity.program_id)
        return result

    f.provider.invoke = drift
    if role == "solution_discovery":
        with pytest.raises(ProgramSourceError):
            f.dispatch.dispatch(f.operation, owner_token=f.owner)
    else:
        started = f.dispatch.dispatch(f.operation, owner_token=f.owner)
        task = f.dispatch._json(started["task_sha256"])
        scope = f.safe.state(task["thread_id"])["values"]["scope_hash"]
        with pytest.raises(ProgramSourceError):
            f.dispatch.approve_scope(
                f.operation,
                owner_token=f.owner,
                scope_sha256=scope,
                approved=True,
                approval_id="stale-control",
            )
    assert f.store.current(f.identity.program_id).generation == 1
    assert f.workspace.programs.phase_status(f.identity.program_id, "phase-2").value != "completed"


def test_actual_source_dispatch_uses_new_discovery_scope_and_accepts_44(admitted):
    _qualify_44(admitted)


def test_execution_v2_is_distinct_from_line_edit_protocol_and_supports_sha256_git(tmp_path):
    f = runtime(tmp_path, 42, create=True, protocol="v2-line-addressed", object_format="sha256")
    operation = first_phase(f)
    close(f)
    f = runtime(tmp_path, 43, protocol="v2-line-addressed")
    f.operation = operation
    try:
        _qualify_44(f)
    finally:
        close(f)
        os.environ["UCA_SAFE_EDIT_PROTOCOL"] = "v1"


@pytest.mark.parametrize(
    "crash,committed", [("admission-update", False), ("admission-commit", True)]
)
def test_process_death_at_atomic_admission_keeps_all_stores_consistent(tmp_path, crash, committed):
    process(tmp_path, "init", crash, expected=73)
    f = runtime(tmp_path, 43)
    try:
        operation = f.store.connection.execute(
            "SELECT operation_id FROM program_execution_bases"
        ).fetchone()[0]
        (tmp_path / "operation.txt").write_text(operation)
        assert len(f.workspace.programs.execution_bindings(f.identity.program_id)) == (
            2 if committed else 1
        )
        assert f.store.connection.execute(
            "SELECT count(*) FROM control.uca_source_dispatch_tasks"
        ).fetchone()[0] == int(committed)
        digest = f.base.status(operation)["completion_sha256"]
        f.dispatch.admit(operation, preparation_receipt_sha256=digest, owner_token=f.owner)
    finally:
        close(f)
    calls = (tmp_path / "calls.jsonl").read_bytes()
    assert json.loads(process(tmp_path, "status").stdout)["state"] == "admitted"
    assert (tmp_path / "calls.jsonl").read_bytes() == calls
    process(tmp_path, "dispatch")


@pytest.mark.parametrize("artifact", ["discovery", "dependency", "scope", "program-result"])
def test_recorded_evidence_drift_is_not_authority_for_resume(admitted, artifact):
    f = admitted
    started = f.dispatch.dispatch(f.operation, owner_token=f.owner)
    task = f.dispatch._json(started["task_sha256"])
    scope = f.safe.state(task["thread_id"])["values"]["scope_hash"]
    if artifact == "discovery":
        path = f.safe.artifacts.root / f"tasks/{task['task_id']}/solution-impact-plan.json"
    elif artifact == "dependency":
        path = (
            f.workspace.artifacts.root
            / "programs/cumulative-program/phases/phase-1/phase-summary.md"
        )
    elif artifact == "scope":
        f.safe.graph.update_state(
            {"configurable": {"thread_id": task["thread_id"]}},
            {"scope_hash": "f" * 64},
            as_node="index",
        )
        path = None
    else:
        binding = f.workspace.programs.execution_binding(task["task_id"])
        path = f.workspace.artifacts.root / binding.result_ref.removeprefix("artifact://")
    if path:
        path.write_bytes(path.read_bytes() + b" ")
    calls = (f.root / "calls.jsonl").read_bytes()
    with pytest.raises((ProgramSourceError, ValueError)):
        f.dispatch.approve_scope(
            f.operation,
            owner_token=f.owner,
            scope_sha256=scope,
            approved=True,
            approval_id="tampered-evidence",
        )
    assert (f.root / "calls.jsonl").read_bytes() == calls
    assert f.store.current(f.identity.program_id).generation == 1


@pytest.mark.parametrize(
    "alias,pragma", [("main", "synchronous=OFF"), ("control", "synchronous=NORMAL")]
)
def test_unsupported_atomic_durability_is_rejected_before_provider(admitted, alias, pragma):
    f = admitted
    f.store.connection.execute(f"PRAGMA {alias}.{pragma}")
    calls = (f.root / "calls.jsonl").read_bytes()
    with pytest.raises(ProgramSourceError, match="rollback journals"):
        f.dispatch.dispatch(f.operation, owner_token=f.owner)
    assert (f.root / "calls.jsonl").read_bytes() == calls
    assert f.store.current(f.identity.program_id).generation == 1


def test_admission_writes_only_rollback_stores_and_keeps_safe_wal_read_only(tmp_path):
    f = runtime(tmp_path, 42, create=True)
    try:
        operation = first_phase(f, admit=False)
        assert f.store.connection.execute("PRAGMA safe.journal_mode").fetchone()[0] == "wal"
        statements = []
        f.store.connection.set_trace_callback(statements.append)
        f.dispatch.admit(
            operation,
            owner_token=f.owner,
            preparation_receipt_sha256=f.base.status(operation)["completion_sha256"],
        )
        f.store.connection.set_trace_callback(None)
        assert not any(
            stmt.lstrip()
            .upper()
            .startswith(("INSERT INTO SAFE.", "UPDATE SAFE.", "DELETE FROM SAFE."))
            for stmt in statements
        )
        assert f.store.connection.execute("PRAGMA main.journal_mode").fetchone()[0] == "delete"
        assert f.store.connection.execute("PRAGMA control.journal_mode").fetchone()[0] == "delete"
    finally:
        close(f)
