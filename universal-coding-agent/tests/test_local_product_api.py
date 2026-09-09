"""H01 uses actual TCP HTTP, separate server processes, Git, Program and Safe."""

from __future__ import annotations

import base64
import json
import os
import re
import socket
import sqlite3
import subprocess
import sys
import time
from contextlib import contextmanager
from pathlib import Path

import httpx
import pytest

from universal_coding_agent.core.safe_models import SafeModePolicy, TestProfile
from universal_coding_agent.product.local_product_binding import COMMANDS, LocalProductBinding
from universal_coding_agent.product.models import (
    AcceptanceCriterion,
    RequirementContract,
    RequirementItem,
    RequirementStatus,
)
from universal_coding_agent.product.workspace import ProductWorkspace
from universal_coding_agent.providers.fake import FakeModelProvider
from universal_coding_agent.web.app import ProductWebRuntime, create_product_app

PROGRAM = "local-two-phase"
PROJECT = "local-fixture"
PREFIX = f"/api/local-product/v1/projects/{PROJECT}/programs/{PROGRAM}"


def git(root, *args):
    return subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, check=True
    ).stdout.strip()


def provider(root, *, failure="", protocol="v1"):
    def log(request):
        with (root / "provider-calls.jsonl").open("a") as stream:
            stream.write(json.dumps({"role": request.role}) + "\n")

    def discovery(request):
        log(request)
        return {
            "summary": "Increment the approved answer.",
            "components": ["app.py"],
            "changes": [
                {
                    "path": "app.py",
                    "operation": "modify",
                    "component": "app.py",
                    "confidence": "high",
                    "rationale": "The current answer is here.",
                    "evidence_paths": ["app.py"],
                }
            ],
            "rejected_candidates": [],
        }

    def implement(request):
        log(request)
        old = max(int(value) for value in re.findall(r"return (42|43)\b", request.user_prompt))
        before, after = f"return {old}", f"return {old + 1}"
        if protocol == "v2-line-addressed":
            match = re.search(rf"(?m)^(A[0-9]{{6}}) \|     return {old}$", request.user_prompt)
            assert match
            before, after = f"@range:{match[1]}..{match[1]}", f"    return {old + 1}\n"
        return {
            "summary": "Increment the answer.",
            "edits": [
                {
                    "path": "app.py",
                    "operation": "modify",
                    "content": None,
                    "replacements": [{"old_text": before, "new_text": after}],
                }
            ],
            "requested_test_profiles": ["increment", "preserved"],
            "assumptions": [],
        }

    def review(request):
        log(request)
        second = "return 44" in request.user_prompt
        verdict = (
            "FAIL"
            if failure == "review" or failure == "second_review" and second
            else "PASS_WITH_CONDITIONS"
            if failure == "second_conditional" and second
            else "PASS"
        )
        return {
            "verdict": verdict,
            "required_actions": ["Reject the fixture."] if verdict != "PASS" else [],
            "confidence": "high",
        }

    phases = [
        {
            "phase_id": f"phase-{index}",
            "title": f"Answer {old + 1}",
            "objective": f"Change the answer in app.py from {old} to {old + 1}.",
            "dependencies": [] if index == 1 else ["phase-1"],
            "slices": [],
            "acceptance_criteria": [f"The answer is {old + 1}."],
        }
        for index, old in ((1, 42), (2, 43))
    ]
    return FakeModelProvider(
        {
            "solution_discovery": discovery,
            "implementer": implement,
            "reviewer": review,
            "program_planner": lambda _: {
                "title": "Two increments",
                "objective": "Accept tested 44.",
                "phases": phases,
                "definition_of_done": ["Accept 44."],
            },
        }
    )


def fixture(root, port, *, object_format="sha1", protocol="v1", failure=""):
    root.mkdir(parents=True, exist_ok=True)
    (root / "trusted-tests.jsonl").write_text("")
    (root / "actual-applies.jsonl").write_text("")
    source = root / "source"
    source.mkdir()
    for name, raw in {
        "app.py": b"def answer():\n    return 42\n",
        "binary.bin": b"\x00\xff\r\n",
        "empty.bin": b"",
        "crlf.txt": b"first\r\nlast",
        "run.sh": b"#!/bin/sh\nexit 0\n",
    }.items():
        (source / name).write_bytes(raw)
    (source / "run.sh").chmod(0o755)
    git(source, "init", "-b", "fixture", "--object-format=" + object_format)
    git(source, "config", "user.name", "Fixture")
    git(source, "config", "user.email", "fixture@example.test")
    git(source, "add", ".")
    git(source, "commit", "-m", "Original 42")
    workspace = ProductWorkspace.create(root / "product", provider(root))
    requirement = RequirementContract(
        alignment_id="local-requirement",
        version=1,
        title="Cumulative answer",
        objective="Increment twice with separate source decisions.",
        requirements=(
            RequirementItem(
                requirement_id="R-001", statement="Preserve source.", category="safety"
            ),
        ),
        acceptance_criteria=(
            AcceptanceCriterion(
                criterion_id="AC-001", statement="Accept tested 44.", requirement_ids=("R-001",)
            ),
        ),
        status=RequirementStatus.APPROVED,
    )
    plan = workspace.programs.create_program(
        program_id=PROGRAM, requirement=requirement, requirement_hash=requirement.canonical_hash()
    )
    workspace.programs.approve_program(PROGRAM, plan.canonical_hash())
    workspace.close()
    policy = SafeModePolicy(
        profiles=(
            TestProfile(
                profile_id="increment",
                argv=(
                    sys.executable,
                    "-B",
                    "-c",
                    f"from pathlib import Path; Path({str(root / 'trusted-tests.jsonl')!r})"
                    ".open('a').write('increment\\n'); "
                    "import subprocess; from app import answer; ns={}; "
                    "exec(subprocess.check_output(['git','show','HEAD:app.py']),ns); "
                    "assert answer()==ns['answer']()+1",
                ),
            ),
            TestProfile(
                profile_id="preserved",
                argv=(
                    sys.executable,
                    "-B",
                    "-c",
                    f"from pathlib import Path; Path({str(root / 'trusted-tests.jsonl')!r})"
                    ".open('a').write('preserved\\n'); "
                    "assert Path('binary.bin').read_bytes()==b'\\0\\xff\\r\\n'; "
                    "assert Path('empty.bin').read_bytes()==b''; "
                    "assert Path('crlf.txt').read_bytes()==b'first\\r\\nlast'; "
                    "assert Path('run.sh').stat().st_mode & 0o111",
                ),
            ),
        )
    )
    config = {
        "schema": "uca-local-product-binding-1",
        "project_id": PROJECT,
        "display_name": "Local fixture",
        "source_root": str(source),
        "origin_repository_url": str(source),
        "origin_commit_sha": git(source, "rev-parse", "HEAD"),
        "origin_tree_sha": git(source, "rev-parse", "HEAD^{tree}"),
        "object_format": object_format,
        "owned_execution_root": str(root / "safe" / "sandboxes"),
        "safe_state_root": str(root / "safe"),
        "transport_id": "fixture-synchronous",
        "edit_protocol": protocol,
        "policy": policy.model_dump(mode="json"),
        "programs": [
            {
                "program_id": PROGRAM,
                "requirement_sha256": requirement.canonical_hash(),
                "plan_sha256": plan.canonical_hash(),
            }
        ],
        "local_origin": f"http://127.0.0.1:{port}",
    }
    (root / "binding.json").write_text(json.dumps(config))
    (root / "fixture-options.json").write_text(json.dumps({"failure": failure}))
    return config


def make_app(root):
    from universal_coding_agent.safe.patching import SafeEditEngine

    actual_apply = getattr(SafeEditEngine.apply, "_fixture_original", SafeEditEngine.apply)

    def counted_apply(self, *args, **kwargs):
        result = actual_apply(self, *args, **kwargs)
        with (root / "actual-applies.jsonl").open("a") as stream:
            stream.write("applied\n")
        return result

    counted_apply._fixture_original = actual_apply
    if __name__ == "__main__":
        SafeEditEngine.apply = counted_apply
    binding = LocalProductBinding.load(root / "binding.json")
    options = json.loads((root / "fixture-options.json").read_text())
    workspace = ProductWorkspace.create(
        root / "product",
        provider(root, protocol=binding.value["edit_protocol"], failure=options["failure"]),
    )
    runtime = ProductWebRuntime(workspace, root / "web-runtime", allow_local_sources=True)
    app = create_product_app(
        runtime, local_product_binding=binding, enable_local_product_commands=True
    )
    original = runtime.local_product_host.execute
    host = runtime.local_product_host

    def fault(seam, name):
        from universal_coding_agent.product.local_product_command_store import current_participant

        part = current_participant()
        fault_path = root / "fault.json"
        if part is None or not fault_path.exists():
            return
        selected = json.loads(fault_path.read_text())
        if (selected["action"], selected["seam"], selected["name"]) != (
            part.payload["action"],
            seam,
            name,
        ):
            return
        if selected.get("completed") and part.response is None:
            return
        try:
            fault_path.rename(root / "fault-consumed.json")
        except FileNotFoundError:
            return
        (root / "fault-hit").write_text(name)
        if selected["mode"].startswith("retain_") or selected["mode"] == "late_registration":
            from universal_coding_agent.core.cancellation import OwnedOperationKind

            driver = part.driver
            coordinator = driver.coordinator
            if selected["mode"] == "late_registration":
                with pytest.raises(RuntimeError, match="revoked"):
                    with coordinator._invocation_context(driver.context):
                        pytest.fail("Returned invocation was reactivated")
                (root / "late-registration-denied").write_text("revoked")
                return

            class Handle:
                def cancel(self):
                    pass

                def done(self):
                    return selected["mode"] == "retain_cancellable"

                def pause(self):
                    self.stopped = True

                def resume(self):
                    self.stopped = False

                def paused(self):
                    return getattr(self, "stopped", False)

            held = []
            host.fixture_retained = held

            def hold(context):
                held.append(context)
                return context.__enter__()

            with coordinator._invocation_context(driver.context):
                signal = coordinator.signal(driver.task_id)
                kind = OwnedOperationKind.PROVIDER
                mode = selected["mode"]
                if mode == "retain_process":
                    process = hold(
                        signal.owned_process(
                            OwnedOperationKind.TEST,
                            lambda: subprocess.Popen([sys.executable, "-c", "pass"]),
                        )
                    )
                    process.wait(timeout=5)
                elif mode == "retain_cancellable":
                    hold(signal.owned_cancellable_operation(kind, Handle))
                else:
                    hold(signal.operation(kind))
                    if mode in {"retain_pausable", "retain_paused"}:
                        hold(signal.owned_pausable_operation(kind, Handle))
                    if mode == "retain_paused":
                        coordinator.pause_task(driver.task_id, reason="Retained fixture handle")
            (root / "retained-registrations.json").write_text(
                json.dumps(coordinator._registration_snapshot(driver.task_id))
            )
            return
        if selected["mode"] == "crash":
            os._exit(87)
        if selected["mode"] == "block":
            deadline = time.monotonic() + 30
            while not (root / "fault-release").exists() and time.monotonic() < deadline:
                time.sleep(0.02)
            assert (root / "fault-release").exists(), "Fixture boundary timed out"
            return
        raise RuntimeError(
            "Private fixture failure: /private/operator sk-secret-fixture-do-not-project"
        )

    host.commands_store.boundary = lambda name: fault("local", name)
    host.continuation.db.boundary = lambda name: fault("v3", name)

    def traced(payload):
        try:
            return original(payload)
        except Exception:
            import traceback

            tb = sys.exc_info()[2]
            while tb is not None:
                frame = tb.tb_frame
                if frame.f_code.co_name == "_operate" and "blobs" in frame.f_locals:
                    blobs = frame.f_locals["blobs"]
                    current = [
                        json.loads(raw)
                        for raw in blobs
                        if raw.startswith(b'{"') and b'"schema":"uca-source-evidence-core-2"' in raw
                    ]
                    if current and payload.get("core_sha256"):
                        original_core = json.loads(host.source._get(payload["core_sha256"]))
                        changes = {
                            k: [original_core[k], current[0][k]]
                            for k in current[0]
                            if original_core.get(k) != current[0][k]
                        }
                        if "inventory_sha256" in changes:
                            old_inventory = json.loads(
                                host.source._get(original_core["inventory_sha256"])
                            )
                            new_inventory = json.loads(blobs[5])
                            changes["inventory_details"] = {
                                k: [old_inventory.get(k), new_inventory.get(k)]
                                for k in set(old_inventory) | set(new_inventory)
                                if old_inventory.get(k) != new_inventory.get(k)
                            }
                        (root / "final-core-drift.json").write_text(json.dumps(changes, indent=2))
                tb = tb.tb_next
            with (root / "command-errors.jsonl").open("a") as output:
                output.write(
                    json.dumps({"action": payload["action"], "traceback": traceback.format_exc()})
                    + "\n"
                )
            raise

    runtime.local_product_host.execute = traced
    return app, runtime


def arm(root, action, name, *, seam="local", mode="raise", completed=False):
    (root / "fault.json").write_text(
        json.dumps(
            {"action": action, "name": name, "seam": seam, "mode": mode, "completed": completed}
        )
    )


def database(root, name="programs.sqlite"):
    paths = list((root / "product").rglob(name))
    assert len(paths) == 1
    return paths[0]


def sql(root, statement, args=()):
    from contextlib import closing

    with closing(sqlite3.connect(database(root))) as connection:
        result = connection.execute(statement, args).fetchall()
        connection.commit()
        return result


def artifact(root, value):
    return sql(root, "SELECT content FROM program_source_artifacts WHERE sha256=?", (value,))[0][0]


def source_files(root, value):
    snapshot = json.loads(artifact(root, value))
    return {
        item["path"]: (item["mode"], base64.b64decode(item["content"]))
        for item in snapshot["files"]
    }


def calls(root):
    path = root / "provider-calls.jsonl"
    return path.read_bytes() if path.exists() else b""


def post(client, payload):
    value = dict(payload)
    if value["action"] == "reconcile_outcome":
        suffix = "requests/" + value.pop("target_request_id") + "/reconcile"
    else:
        suffix = next(s for s, (a, _) in COMMANDS.items() if a == value["action"])
    return client.post(PREFIX + "/" + suffix, json=value)


def journey(client, config, *, until="accept-43", first_approved=True, second_approved=True):
    saved = {}

    def run(action, request, **fields):
        result, payload, raw = command(client, action, request, **fields)
        saved[request] = {"response": result, "payload": payload, "raw": raw}
        return result["result"]

    initial = run(
        "initialize_source",
        "initialize-42",
        origin_commit_sha=config["origin_commit_sha"],
        origin_tree_sha=config["origin_tree_sha"],
    )
    if until == "initialize-42":
        return saved
    first = run(
        "start_first_phase", "discover-42", before_sha256=initial["source_sha256"], generation=0
    )
    if until == "discover-42":
        return saved
    terminal = run(
        "decide_first_scope",
        "scope-43",
        task_id=first["task_id"],
        **{k: first[k] for k in ("scope_proposal_sha256", "scope_sha256", "checkpoint_sha256")},
        approval_id="approve-scope-43",
        approved=first_approved,
    )
    if until == "scope-43":
        return saved
    quote = run(
        "preview_first_source",
        "preview-43",
        task_id=first["task_id"],
        result_sha256=terminal["result_sha256"],
        before_sha256=initial["source_sha256"],
        generation=0,
    )
    if until == "preview-43":
        return saved
    accepted = run(
        "decide_first_source",
        "accept-43",
        **{
            k: quote[k]
            for k in (
                "task_id",
                "quote_sha256",
                "quote_revision",
                "core_sha256",
                "transition_sha256",
                "before_sha256",
                "generation",
                "predecessor_receipt_sha256",
                "evidence_view_sha256",
            )
        },
        approval_id="approve-source-43",
        approved=True,
    )
    if until == "accept-43":
        return saved
    continued = run(
        "start_continuation",
        "discover-43",
        before_sha256=accepted["source_sha256"],
        generation=1,
        acceptance_receipt_sha256=accepted["source_receipt_sha256"],
    )
    if until == "discover-43":
        return saved
    terminal = run(
        "decide_continuation_scope",
        "scope-44",
        **{
            k: continued[k]
            for k in (
                "operation_id",
                "task_id",
                "admission_sha256",
                "proposal_sha256",
                "scope_sha256",
            )
        },
        expected_epoch=continued["epoch"],
        expected_receipt_sha256=continued["v3_receipt_sha256"],
        approval_id="approve-scope-44",
        approved=second_approved,
    )
    if until == "scope-44":
        return saved
    candidate = run(
        "preview_final_source",
        "preview-44",
        operation_id=continued["operation_id"],
        task_id=continued["task_id"],
        terminal_receipt_sha256=terminal["v3_receipt_sha256"],
        before_sha256=accepted["source_sha256"],
        generation=1,
    )
    if until == "preview-44":
        return saved
    run(
        "decide_final_source",
        "accept-44",
        **{
            k: candidate[k]
            for k in (
                "operation_id",
                "task_id",
                "terminal_receipt_sha256",
                "before_sha256",
                "generation",
                "candidate_sha256",
                "revision",
                "core_sha256",
                "transition_sha256",
                "predecessor_receipt_sha256",
                "evidence_view_sha256",
            )
        },
        approval_id="approve-source-44",
        approved=True,
    )
    return saved


def continuation_payload(client, saved, *, request="discover-43"):
    source = saved["accept-43"]["response"]["result"]
    return request_payload(
        client,
        "start_continuation",
        request,
        before_sha256=source["source_sha256"],
        generation=1,
        acceptance_receipt_sha256=source["source_receipt_sha256"],
    )


def reconcile_payload(client, target, operation, *, request="observe-outcome"):
    public = client.get(PREFIX + "/requests/" + target["request_id"]).json()
    return request_payload(
        client,
        "reconcile_outcome",
        request,
        target_request_id=target["request_id"],
        target_request_sha256=public["request_sha256"],
        target_revision=target["expected_revision"],
        operation_id=operation,
        **{
            k: target[k]
            for k in (
                "program_control_revision",
                "task_control_revision",
                "requirement_sha256",
                "plan_sha256",
            )
        },
    )


@contextmanager
def server(root, port, *, number=1, listen_port=None):
    listen_port = listen_port or port
    log_path = root / f"server-{number}.log"
    with log_path.open("w") as output:
        client = httpx.Client(
            base_url=f"http://127.0.0.1:{listen_port}",
            timeout=120,
            trust_env=False,
            headers={
                "Host": f"127.0.0.1:{port}",
                "Origin": f"http://127.0.0.1:{port}",
                "X-UCA-Command": "1",
            },
        )
        process = subprocess.Popen(
            [sys.executable, str(Path(__file__).resolve()), "serve", str(root), str(listen_port)],
            stdout=output,
            stderr=subprocess.STDOUT,
        )
        client.fixture_process = process
        try:
            deadline = time.monotonic() + 20
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    pytest.fail(log_path.read_text())
                try:
                    if client.get("/api/health").status_code == 200:
                        break
                except httpx.TransportError:
                    pass
                time.sleep(0.05)
            else:
                pytest.fail("HTTP fixture startup timed out: " + log_path.read_text())
            yield client
        finally:
            client.close()
            process.terminate()
            try:
                process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
            with (root / "server-exits.jsonl").open("a") as exits:
                exits.write(json.dumps({"number": number, "returncode": process.returncode}) + "\n")


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def request_payload(client, action, request, **fields):
    snapshot = client.get(PREFIX)
    assert snapshot.status_code == 200, snapshot.text
    status = snapshot.json()
    payload = {
        "schema": "uca-local-product-command-1",
        "request_id": request,
        "action": action,
        "expected_binding_sha256": status["binding_sha256"],
        "expected_revision": status["command_revision"],
        "requirement_sha256": status["requirement_sha256"],
        "plan_sha256": status["plan_sha256"],
        "program_control_revision": status["program_control_revision"],
        "task_control_revision": status["task_control_revision"],
        **fields,
    }
    return payload


def command(client, action, request, **fields):
    payload = request_payload(client, action, request, **fields)
    suffix = next(s for s, (a, _) in COMMANDS.items() if a == action)
    result = client.post(PREFIX + "/" + suffix, json=payload)
    assert result.status_code == 200, result.text
    return result.json(), payload, result.content


@pytest.mark.parametrize(
    "object_format,protocol", [("sha1", "v1"), ("sha256", "v2-line-addressed")]
)
def test_h01_actual_http_first_source_restart_continuation_final_acceptance(
    tmp_path, object_format, protocol
):
    port = free_port()
    config = fixture(tmp_path, port, object_format=object_format, protocol=protocol)
    with server(tmp_path, port) as client:
        initialized, _, _ = command(
            client,
            "initialize_source",
            "initialize-42",
            origin_commit_sha=config["origin_commit_sha"],
            origin_tree_sha=config["origin_tree_sha"],
        )
        origin = initialized["result"]["source_sha256"]
        started, _, _ = command(
            client, "start_first_phase", "discover-42", before_sha256=origin, generation=0
        )
        first = started["result"]
        terminal, _, _ = command(
            client,
            "decide_first_scope",
            "scope-43",
            task_id=first["task_id"],
            **{k: first[k] for k in ("scope_proposal_sha256", "scope_sha256", "checkpoint_sha256")},
            approval_id="approve-scope-43",
            approved=True,
        )
        preview, _, _ = command(
            client,
            "preview_first_source",
            "preview-43",
            task_id=first["task_id"],
            result_sha256=terminal["result"]["result_sha256"],
            before_sha256=origin,
            generation=0,
        )
        quote = preview["result"]
    with server(tmp_path, port, number=2) as client:
        accepted, payload, exact_response = command(
            client,
            "decide_first_source",
            "accept-43",
            **{
                k: quote[k]
                for k in (
                    "task_id",
                    "quote_sha256",
                    "quote_revision",
                    "core_sha256",
                    "transition_sha256",
                    "before_sha256",
                    "generation",
                    "predecessor_receipt_sha256",
                    "evidence_view_sha256",
                )
            },
            approval_id="approve-source-43",
            approved=True,
        )
        assert accepted["result"]["generation"] == 1
        accepted43_raw = artifact(tmp_path, accepted["result"]["source_sha256"])
        accepted43_files = source_files(tmp_path, accepted["result"]["source_sha256"])
        assert accepted43_files["app.py"] == ("100644", b"def answer():\n    return 43\n")
    with server(tmp_path, port, number=3) as client:
        assert (
            client.post(PREFIX + "/source/first/decisions", json=payload).content == exact_response
        )
        parked, _, _ = command(
            client,
            "start_continuation",
            "discover-43",
            before_sha256=accepted["result"]["source_sha256"],
            generation=1,
            acceptance_receipt_sha256=accepted["result"]["source_receipt_sha256"],
        )
        continuation = parked["result"]
    with server(tmp_path, port, number=4) as client:
        terminal, _, _ = command(
            client,
            "decide_continuation_scope",
            "scope-44",
            **{
                k: continuation[k]
                for k in (
                    "operation_id",
                    "task_id",
                    "admission_sha256",
                    "proposal_sha256",
                    "scope_sha256",
                )
            },
            expected_epoch=continuation["epoch"],
            expected_receipt_sha256=continuation["v3_receipt_sha256"],
            approval_id="approve-scope-44",
            approved=True,
        )
        preview, _, _ = command(
            client,
            "preview_final_source",
            "preview-44",
            operation_id=continuation["operation_id"],
            task_id=continuation["task_id"],
            terminal_receipt_sha256=terminal["result"]["v3_receipt_sha256"],
            before_sha256=accepted["result"]["source_sha256"],
            generation=1,
        )
        candidate = preview["result"]
    with server(tmp_path, port, number=5) as client:
        final, _, _ = command(
            client,
            "decide_final_source",
            "accept-44",
            **{
                k: candidate[k]
                for k in (
                    "operation_id",
                    "task_id",
                    "terminal_receipt_sha256",
                    "before_sha256",
                    "generation",
                    "candidate_sha256",
                    "revision",
                    "core_sha256",
                    "transition_sha256",
                    "predecessor_receipt_sha256",
                    "evidence_view_sha256",
                )
            },
            approval_id="approve-source-44",
            approved=True,
        )
        assert final["result"]["generation"] == 2
        assert set(final["authority"].values()) == {False}
        assert client.get(PREFIX).json()["accepted"]["generation"] == 2
        before_reads = calls(tmp_path)
        assert client.get(PREFIX + "/operations/" + candidate["operation_id"]).status_code == 200
        assert client.get(PREFIX + "/requests/accept-43").content == exact_response
        assert (
            client.get(PREFIX + "/evidence/" + candidate["evidence_view_sha256"]).status_code == 200
        )
        assert client.get("/api/programs/" + PROGRAM + "/executions").status_code == 409
        assert calls(tmp_path) == before_reads
        forbidden = request_payload(
            client,
            "start_continuation",
            "third-phase-denied",
            before_sha256=final["result"]["source_sha256"],
            generation=1,
            acceptance_receipt_sha256=final["result"]["source_receipt_sha256"],
        )
        assert post(client, forbidden).status_code == 409
    assert (tmp_path / "source" / "app.py").read_bytes() == b"def answer():\n    return 42\n"
    assert git(tmp_path / "source", "rev-parse", "HEAD") == config["origin_commit_sha"]
    assert artifact(tmp_path, accepted["result"]["source_sha256"]) == accepted43_raw
    files44 = source_files(tmp_path, final["result"]["source_sha256"])
    assert files44["app.py"] == ("100644", b"def answer():\n    return 44\n")
    assert {k: v for k, v in files44.items() if k != "app.py"} == {
        k: v for k, v in accepted43_files.items() if k != "app.py"
    }
    owners = [
        json.loads(artifact(tmp_path, r[0]))["owner_sha256"]
        for r in sql(
            tmp_path, "SELECT claim_sha256 FROM local_product_requests_v1 ORDER BY sequence"
        )
    ]
    assert len(owners) == len(set(owners)) == 9


def test_h02_h12_real_http_boundary_and_strict_bodies_before_claim(tmp_path):
    port = free_port()
    config = fixture(tmp_path, port)
    with server(tmp_path, port) as client:
        payload = request_payload(
            client,
            "initialize_source",
            "strict-initialize",
            origin_commit_sha=config["origin_commit_sha"],
            origin_tree_sha=config["origin_tree_sha"],
        )
        endpoint = PREFIX + "/source/initialize"
        denied = [
            b"{",
            b"\xff",
            b"null",
            b"[]",
            b'{"schema":1,"schema":2}',
            b'{"x":' + b"[" * 9 + b"0" + b"]" * 9 + b"}",
            b" " * 65_537,
        ]
        for key, value in (
            ("approved", True),
            ("provider", "private.module"),
            ("policy", {}),
            ("owner_token", "private-token"),
            ("expected_revision", True),
            ("expected_revision", 0.0),
            ("task_control_revision", 0),
            ("request_id", "../private"),
            ("request_id", "ab"),
            ("action", "start_first_phase"),
            ("origin_tree_sha", "g" * 40),
        ):
            denied.append(json.dumps({**payload, key: value}).encode())
        for raw in denied:
            response = client.post(
                endpoint, content=raw, headers={"Content-Type": "application/json"}
            )
            assert response.status_code in {400, 413, 422}, response.text
            assert response.headers["cache-control"] == "no-store"
            assert "private" not in response.text
        for headers in (
            {"Host": "evil.test"},
            {"Origin": "null"},
            {"Origin": "http://evil.test"},
            {"X-UCA-Command": "0"},
            {"Content-Type": "application/x-www-form-urlencoded"},
            [("Origin", config["local_origin"]), ("Origin", config["local_origin"])],
        ):
            response = client.post(endpoint, json=payload, headers=headers)
            assert response.status_code == 403, response.text
        assert client.get(PREFIX + "?provider=evil").status_code == 422
        assert client.request("GET", PREFIX, content=b"{}").status_code == 422
        assert client.head(PREFIX).status_code == 422
        assert client.get(PREFIX.replace(PROJECT, "unknown-project")).status_code == 404
        assert client.get(PREFIX.replace(PROGRAM, "unknown-program")).status_code == 404
        assert sql(tmp_path, "SELECT * FROM local_product_requests_v1") == []
        assert calls(tmp_path) == b""


def test_h02_default_disabled_and_invalid_cli_before_provider(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient

    from universal_coding_agent import cli

    workspace = ProductWorkspace.create(tmp_path / "default", provider(tmp_path))
    runtime = ProductWebRuntime(workspace, tmp_path / "web")
    with TestClient(create_product_app(runtime)) as client:
        assert client.post(PREFIX + "/source/initialize", json={}).status_code == 503
    assert not list(tmp_path.rglob("local-product-root-v1.json"))
    invalid = tmp_path / "invalid.json"
    invalid.write_text('{"schema":"invalid"}')
    monkeypatch.setattr(
        cli,
        "load_provider",
        lambda *_: pytest.fail("Provider selected before invalid binding denial"),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "uca",
            "serve",
            "--local-product-binding",
            str(invalid),
            "--enable-local-product-commands",
        ],
    )
    with pytest.raises(ValueError):
        cli.main()


@pytest.mark.parametrize(
    "change", ["policy", "root", "program", "safe_inode", "missing_locator", "extra_schema"]
)
def test_h02_immutable_reopen_denies_changed_binding(tmp_path, change):
    port = free_port()
    config = fixture(tmp_path, port)
    with server(tmp_path, port):
        pass
    before = calls(tmp_path)
    if change == "policy":
        config["policy"]["profiles"][0]["argv"][-1] = "raise SystemExit(1)"
    elif change == "root":
        config["source_root"] = str(tmp_path / "other")
        (tmp_path / "other").mkdir()
    elif change == "program":
        config["programs"][0]["program_id"] = "other-program"
    elif change == "safe_inode":
        path = tmp_path / "safe" / "safe-checkpoints.sqlite"
        path.rename(path.with_suffix(".preimage"))
        path.write_bytes(path.with_suffix(".preimage").read_bytes())
    elif change == "missing_locator":
        (tmp_path / "safe" / "local-product-root-v1.json").rename(
            tmp_path / "locator-preimage.json"
        )
    else:
        sql(tmp_path, "CREATE TABLE local_product_requests_v9 (value TEXT)")
    (tmp_path / "binding.json").write_text(json.dumps(config))
    result = subprocess.run(
        [sys.executable, str(Path(__file__)), "serve", str(tmp_path), str(port)],
        capture_output=True,
        timeout=20,
    )
    assert result.returncode != 0
    assert calls(tmp_path) == before


@pytest.mark.parametrize("approved,failure", [(False, ""), (True, "review"), (True, "tests")])
def test_h03_h06_first_negative_scope_or_evidence_never_accepts(tmp_path, approved, failure):
    port = free_port()
    config = fixture(tmp_path, port, failure=failure)
    if failure == "tests":
        config["policy"]["profiles"][0]["argv"][-1] += "; assert False, 'negative trusted test'"
        (tmp_path / "binding.json").write_text(json.dumps(config))
    with server(tmp_path, port) as client:
        saved = journey(client, config, until="scope-43", first_approved=approved)
        terminal = saved["scope-43"]["response"]
        assert terminal["outcome"] in {"rejected", "failed"}
        assert client.get(PREFIX).json()["accepted"]["generation"] == 0
        before = calls(tmp_path)
        first = saved["discover-42"]["response"]["result"]
        payload = request_payload(
            client,
            "preview_first_source",
            "negative-preview",
            task_id=first["task_id"],
            result_sha256=terminal["result"]["result_sha256"],
            before_sha256=saved["initialize-42"]["response"]["result"]["source_sha256"],
            generation=0,
        )
        assert post(client, payload).status_code == 409
        assert calls(tmp_path) == before
        repo = tmp_path / "safe" / "sandboxes" / first["task_id"] / "repo"
        assert (repo / "app.py").read_bytes() == (tmp_path / "source" / "app.py").read_bytes()


def test_h04_first_quote_distinct_candidates_rejection_is_final(tmp_path):
    port = free_port()
    config = fixture(tmp_path, port)
    with server(tmp_path, port) as client:
        saved = journey(client, config, until="preview-43")
        quote = saved["preview-43"]["response"]["result"]
        payload = request_payload(
            client,
            "decide_first_source",
            "reject-source-43",
            **{
                k: quote[k]
                for k in (
                    "task_id",
                    "quote_sha256",
                    "quote_revision",
                    "core_sha256",
                    "transition_sha256",
                    "before_sha256",
                    "generation",
                    "predecessor_receipt_sha256",
                    "evidence_view_sha256",
                )
            },
            approval_id="reject-source",
            approved=False,
        )
        rejected = post(client, payload)
        assert rejected.status_code == 200, rejected.text
        assert rejected.json()["outcome"] == "rejected"
        assert client.get(PREFIX).json()["accepted"]["generation"] == 0
        payload.update(
            request_id="accept-rejected-source",
            approved=True,
            expected_revision=rejected.json()["command_revision"],
        )
        assert post(client, payload).status_code == 409
        candidates = [
            json.loads(artifact(tmp_path, row[0]))
            for row in sql(tmp_path, "SELECT candidate_sha256 FROM program_source_candidates")
        ]
        assert len(candidates) == 2
        assert (
            candidates[0]["binding"]["owner_binding_sha256"]
            != candidates[1]["binding"]["owner_binding_sha256"]
        )
        assert candidates[0]["after_sha256"] == candidates[1]["after_sha256"]


@pytest.mark.parametrize("restart", [False, True])
def test_h09_real_v3_reversible_seal_only_original_live_adapter(tmp_path, restart):
    port = free_port()
    config = fixture(tmp_path, port)
    with server(tmp_path, port) as client:
        saved = journey(client, config)
        target = continuation_payload(client, saved)
        arm(tmp_path, "start_continuation", "after_response")
        failed = post(client, target)
        assert failed.status_code == 409
        assert "Private" not in failed.text and "sk-secret" not in failed.text
        observed = client.get(PREFIX + "/requests/discover-43")
        assert observed.status_code == 202, observed.text
        assert post(client, target).status_code == 202
        before = calls(tmp_path)
        operation = sql(tmp_path, "SELECT operation_id FROM program_source_dispatches_v3")[0][0]
        payload = reconcile_payload(client, target, operation)
        if not restart:
            response = post(client, payload)
            assert response.status_code == 200, response.text
            assert response.json()["outcome"] == "reconciled"
            assert response.json()["result"]["disposition"] == "original_live_seal_completed"
            assert client.get(PREFIX + "/requests/discover-43").status_code == 200
            assert post(client, payload).content == response.content
            assert calls(tmp_path) == before
    if restart:
        with server(tmp_path, port, number=2) as client:
            response = post(client, payload)
            assert response.status_code == 200, response.text
            assert response.json()["outcome"] == "blocked"
            assert response.json()["result"]["disposition"] == "original_live_evidence_missing"
            assert client.get(PREFIX + "/requests/discover-43").status_code == 202
            assert post(client, payload).content == response.content
            assert calls(tmp_path) == before
            assert sql(tmp_path, "SELECT pending_request_id FROM local_product_heads_v1") == [
                ("discover-43",)
            ]


def action_fields(action, saved, config):
    def get(key):
        return saved[key]["response"]["result"]

    if action == "initialize_source":
        fields = {k: config[k] for k in ("origin_commit_sha", "origin_tree_sha")}
    elif action == "start_first_phase":
        fields = {"before_sha256": get("initialize-42")["source_sha256"], "generation": 0}
    elif action == "decide_first_scope":
        fields = {
            k: get("discover-42")[k]
            for k in ("task_id", "scope_proposal_sha256", "scope_sha256", "checkpoint_sha256")
        }
        fields.update(approved=True, approval_id="crash-scope")
    elif action == "preview_first_source":
        fields = {
            "task_id": get("discover-42")["task_id"],
            "result_sha256": get("scope-43")["result_sha256"],
            "before_sha256": get("initialize-42")["source_sha256"],
            "generation": 0,
        }
    elif action == "decide_first_source":
        fields = {
            k: get("preview-43")[k]
            for k in (
                "task_id",
                "quote_sha256",
                "quote_revision",
                "core_sha256",
                "transition_sha256",
                "before_sha256",
                "generation",
                "predecessor_receipt_sha256",
                "evidence_view_sha256",
            )
        }
        fields.update(approved=True, approval_id="crash-source")
    elif action == "start_continuation":
        fields = {
            "before_sha256": get("accept-43")["source_sha256"],
            "generation": 1,
            "acceptance_receipt_sha256": get("accept-43")["source_receipt_sha256"],
        }
    elif action == "decide_continuation_scope":
        fields = {
            k: get("discover-43")[k]
            for k in (
                "operation_id",
                "task_id",
                "admission_sha256",
                "proposal_sha256",
                "scope_sha256",
            )
        }
        fields.update(
            approved=True,
            approval_id="crash-scope",
            expected_epoch=get("discover-43")["epoch"],
            expected_receipt_sha256=get("discover-43")["v3_receipt_sha256"],
        )
    elif action == "preview_final_source":
        fields = {k: get("discover-43")[k] for k in ("operation_id", "task_id")}
        fields.update(
            terminal_receipt_sha256=get("scope-44")["v3_receipt_sha256"],
            before_sha256=get("accept-43")["source_sha256"],
            generation=1,
        )
    else:
        fields = {
            k: get("preview-44")[k]
            for k in (
                "operation_id",
                "task_id",
                "terminal_receipt_sha256",
                "before_sha256",
                "generation",
                "candidate_sha256",
                "revision",
                "core_sha256",
                "transition_sha256",
                "predecessor_receipt_sha256",
                "evidence_view_sha256",
            )
        }
        fields.update(approved=True, approval_id="crash-source")
    return fields


@pytest.mark.parametrize(
    "action,until,boundary",
    [
        ("initialize_source", None, "after_commit"),
        ("start_first_phase", "initialize-42", "first_outer_returned"),
        ("decide_first_scope", "discover-42", "first_outer_returned"),
        ("preview_first_source", "scope-43", "after_response"),
        ("decide_first_source", "preview-43", "after_response"),
        ("start_continuation", "accept-43", "after_response"),
        ("decide_continuation_scope", "discover-43", "after_response"),
        ("preview_final_source", "scope-44", "after_response"),
        ("decide_final_source", "preview-44", "after_response"),
    ],
)
def test_h08_crash_pending_has_no_replay_adoption_or_new_id_bypass(
    tmp_path, action, until, boundary
):
    port = free_port()
    config = fixture(tmp_path, port)
    with server(tmp_path, port) as client:
        saved = journey(client, config, until=until) if until else {}
        fields = action_fields(action, saved, config)
        payload = request_payload(client, action, "crash-request", **fields)
        arm(tmp_path, action, boundary, mode="crash")
        with pytest.raises(httpx.TransportError):
            post(client, payload)
    assert (tmp_path / "fault-hit").read_text() == boundary
    before = calls(tmp_path)
    with server(tmp_path, port, number=2) as client:
        response = post(client, payload)
        assert response.status_code == 202, response.text
        assert post(client, {**payload, "request_id": "cannot-retry"}).status_code == 409
        source = client.get(PREFIX).json()["accepted"]
        expected_generation = 1 if "accept-43" in saved else 0 if saved else None
        assert (source["generation"] if source else None) == expected_generation
        assert calls(tmp_path) == before
        assert sql(tmp_path, "SELECT pending_request_id FROM local_product_heads_v1") == [
            ("crash-request",)
        ]
    assert (tmp_path / "source" / "app.py").read_bytes() == b"def answer():\n    return 42\n"


def test_h07_lost_completed_response_replays_exact_bytes_after_source_drift(tmp_path):
    port = free_port()
    config = fixture(tmp_path, port)
    with server(tmp_path, port) as client:
        payload = request_payload(
            client,
            "initialize_source",
            "lost-response",
            origin_commit_sha=config["origin_commit_sha"],
            origin_tree_sha=config["origin_tree_sha"],
        )
        arm(tmp_path, "initialize_source", "after_commit", mode="crash", completed=True)
        with pytest.raises(httpx.TransportError):
            post(client, payload)
    response_sha = sql(tmp_path, "SELECT response_sha256 FROM local_product_requests_v1")[0][0]
    raw = artifact(tmp_path, response_sha)
    (tmp_path / "source" / "app.py").write_bytes(b"unaccepted drift\n")
    with server(tmp_path, port, number=2) as client:
        assert post(client, payload).content == raw
        assert client.get(PREFIX + "/requests/lost-response").content == raw
        assert post(client, {**payload, "origin_tree_sha": "0" * 40}).status_code == 409
        assert calls(tmp_path) == b""


@pytest.mark.parametrize(
    "mutation",
    ["empty_directory", "source_bytes", "execution_bytes", "program_control", "remote_thread"],
)
def test_h04_h10_reviewed_first_core_rejects_real_drift(tmp_path, mutation):
    port = free_port()
    config = fixture(tmp_path, port)
    (tmp_path / "source" / "empty-directory").mkdir()
    with server(tmp_path, port) as client:
        saved = journey(client, config, until="preview-43")
        quote = saved["preview-43"]["response"]["result"]
        payload = request_payload(
            client,
            "decide_first_source",
            "drifted-source-43",
            **{
                k: quote[k]
                for k in (
                    "task_id",
                    "quote_sha256",
                    "quote_revision",
                    "core_sha256",
                    "transition_sha256",
                    "before_sha256",
                    "generation",
                    "predecessor_receipt_sha256",
                    "evidence_view_sha256",
                )
            },
            approval_id="drifted-approval",
            approved=True,
        )
        if mutation == "empty_directory":
            (tmp_path / "source" / "empty-directory").chmod(0o700)
        elif mutation == "source_bytes":
            (tmp_path / "source" / "app.py").write_text("def answer():\n    return 999\n")
        elif mutation == "execution_bytes":
            (tmp_path / "safe" / "sandboxes" / quote["task_id"] / "repo" / "app.py").write_text(
                "def answer():\n    return 999\n"
            )
        elif mutation == "program_control":
            assert (
                client.post(
                    "/api/programs/" + PROGRAM + "/pause", json={"reason": "Real revision drift"}
                ).status_code
                == 200
            )
            assert client.post("/api/programs/" + PROGRAM + "/resume", json={}).status_code == 200
        else:
            from universal_coding_agent.core.remote_operations import RemoteOperationState
            from universal_coding_agent.product.remote_operations import (
                SqliteRemoteOperationLeaseStore,
            )

            remote = SqliteRemoteOperationLeaseStore(
                database(tmp_path, "private-remote-operations.sqlite")
            )
            try:
                remote.register(
                    task_id="different-task",
                    thread_id=saved["discover-42"]["response"]["result"]["thread_id"],
                    transport="fixture-synchronous",
                    transport_scope="sha256:" + "a" * 64,
                    operation_id="private-fixture-operation",
                    base_sha=config["origin_commit_sha"],
                    status="active",
                    state=RemoteOperationState.ACTIVE,
                )
            finally:
                remote.close()
        response = post(client, payload)
        assert response.status_code == 409, response.text
        assert sql(tmp_path, "SELECT generation FROM program_source_heads") == [(0,)]
        assert sql(tmp_path, "SELECT * FROM program_source_acceptances") == []


def test_h13_raw_v1_and_reconstructed_participants_cannot_bypass_managed_decision(tmp_path):
    port = free_port()
    config = fixture(tmp_path, port)
    with server(tmp_path, port) as client:
        saved = journey(client, config, until="preview-43")
    _, runtime = make_app(tmp_path)
    host = runtime.local_product_host
    owner = host.lifecycle.reserve_program_worker(PROGRAM)
    quote = saved["preview-43"]["response"]["result"]
    before = sql(tmp_path, "SELECT * FROM local_product_heads_v1")
    try:
        from universal_coding_agent.product.local_product_command_store import (
            LocalProductParticipation,
        )

        class Reconstructed(LocalProductParticipation):
            pass

        payload = {**saved["preview-43"]["payload"], "project_id": PROJECT, "program_id": PROGRAM}
        for kind in (LocalProductParticipation, Reconstructed):
            rebuilt = kind(host, payload)
            with pytest.raises(ValueError, match="recovery required"):
                with rebuilt.activate():
                    pytest.fail("A reconstructed participant registered itself")
        with pytest.raises(ValueError, match="recovery required"):
            host.source.prepare(
                PROGRAM,
                quote["task_id"],
                owner_token=owner,
                expected_source_sha256=quote["before_sha256"],
                expected_generation=0,
            )
        stored = json.loads(artifact(tmp_path, quote["quote_sha256"]))
        with pytest.raises(ValueError, match="recovery required"):
            host.source.accept(
                stored["preview_candidate_sha256"],
                owner_token=owner,
                approved_transition_sha256=quote["transition_sha256"],
                approval_id="raw-not-authorized",
            )
        with pytest.raises(ValueError, match="recovery required"):
            host.source.initialize(host.identity(PROGRAM), owner_token=owner)
        assert sql(tmp_path, "SELECT generation FROM program_source_heads") == [(0,)]
        assert sql(tmp_path, "SELECT * FROM local_product_heads_v1") == before
    finally:
        host.lifecycle.release_program_worker(PROGRAM, owner)
        runtime.close()


def test_h13_raw_c1_after_actual_receipt_one_cannot_allocate(tmp_path):
    port = free_port()
    config = fixture(tmp_path, port)
    with server(tmp_path, port) as client:
        saved = journey(client, config, until="accept-43")
    _, runtime = make_app(tmp_path)
    host = runtime.local_product_host
    owner = host.lifecycle.reserve_program_worker(PROGRAM)
    try:
        with pytest.raises(ValueError, match="recovery required"):
            host.materialization.begin(
                PROGRAM,
                acceptance_receipt_sha256=saved["accept-43"]["response"]["result"][
                    "source_receipt_sha256"
                ],
                owner_token=owner,
            )
        assert sql(tmp_path, "SELECT * FROM program_source_materializations") == []
        assert sql(tmp_path, "SELECT * FROM program_execution_bases") == []
        assert sql(tmp_path, "SELECT generation FROM program_source_heads") == [(1,)]
    finally:
        host.lifecycle.release_program_worker(PROGRAM, owner)
        runtime.close()


def test_h06_premature_final_preview_is_pure_denial(tmp_path):
    port = free_port()
    config = fixture(tmp_path, port)
    with server(tmp_path, port) as client:
        saved = journey(client, config, until="discover-43")
        continued = saved["discover-43"]["response"]["result"]
        premature = request_payload(
            client,
            "preview_final_source",
            "premature-preview",
            operation_id=continued["operation_id"],
            task_id=continued["task_id"],
            terminal_receipt_sha256=continued["v3_receipt_sha256"],
            before_sha256=saved["accept-43"]["response"]["result"]["source_sha256"],
            generation=1,
        )
        before = sql(tmp_path, "SELECT name,sql FROM sqlite_master ORDER BY name")
        assert post(client, premature).status_code == 409
        assert sql(tmp_path, "SELECT name,sql FROM sqlite_master ORDER BY name") == before
        assert client.get(PREFIX).status_code == 200
        terminal, _, _ = command(
            client,
            "decide_continuation_scope",
            "scope-44",
            **{
                k: continued[k]
                for k in (
                    "operation_id",
                    "task_id",
                    "admission_sha256",
                    "proposal_sha256",
                    "scope_sha256",
                )
            },
            expected_epoch=continued["epoch"],
            expected_receipt_sha256=continued["v3_receipt_sha256"],
            approval_id="approve-scope-44",
            approved=True,
        )
        assert terminal["outcome"] == "terminal_unaccepted"


def test_h11_complete_http_ancestry_and_companion_deletion_denies_replay(tmp_path):
    from contextlib import closing

    port = free_port()
    config = fixture(tmp_path, port)
    with server(tmp_path, port) as client:
        saved = journey(client, config, until="accept-44")
        final = saved["accept-44"]
        payload = final["payload"]
        assert post(client, payload).content == final["raw"]
        before = calls(tmp_path)
        required = set()
        records = dict(sql(tmp_path, "SELECT sha256,content FROM program_source_artifacts"))

        def walk(value):
            if type(value) is dict:
                for item in value.values():
                    walk(item)
            elif type(value) is list:
                for item in value:
                    walk(item)
            elif type(value) is str and value in records and value not in required:
                required.add(value)
                try:
                    child = json.loads(records[value])
                except (ValueError, UnicodeError):
                    return
                walk(child)

        for row in sql(
            tmp_path,
            "SELECT payload_sha256,claim_sha256,child_map_sha256,response_sha256 "
            "FROM local_product_requests_v1",
        ):
            for value in row:
                walk(value)
        assert len(required) > 60
        failures = []
        for value in sorted(required):
            sql(tmp_path, "DELETE FROM program_source_artifacts WHERE sha256=?", (value,))
            try:
                if (
                    client.get(PREFIX).status_code != 409
                    or post(client, payload).status_code != 409
                ):
                    failures.append(value)
            finally:
                sql(
                    tmp_path,
                    "INSERT INTO program_source_artifacts VALUES (?,?)",
                    (value, records[value]),
                )
        (tmp_path / "deletion-coverage.json").write_text(
            json.dumps({"count": len(required), "missed": failures})
        )
        assert failures == []
        for name, table in (
            ("safe/safe-checkpoints.sqlite", "uca_source_dispatch_tasks_v3_guard"),
            ("product/control.sqlite", "uca_source_dispatch_tasks_v3"),
        ):
            with closing(sqlite3.connect(tmp_path / name)) as connection:
                rows = connection.execute(f"SELECT * FROM {table}").fetchall()
                assert rows
                connection.execute(f"DELETE FROM {table}")
                connection.commit()
                try:
                    assert client.get(PREFIX).status_code == 409
                    assert post(client, payload).status_code == 409
                finally:
                    connection.executemany(
                        f"INSERT INTO {table} VALUES ({','.join('?' for _ in rows[0])})", rows
                    )
                    connection.commit()
        assert post(client, payload).content == final["raw"]
        assert calls(tmp_path) == before


def test_h02_unsupported_methods_and_routes_have_fixed_uncacheable_errors(tmp_path):
    port = free_port()
    fixture(tmp_path, port)
    with server(tmp_path, port) as client:
        for method, path in (
            ("HEAD", PREFIX),
            ("POST", PREFIX),
            ("GET", PREFIX + "/source/initialize"),
            ("DELETE", PREFIX),
            ("OPTIONS", PREFIX),
            ("GET", PREFIX + "/unknown-command"),
        ):
            response = client.request(method, path, json={} if method == "POST" else None)
            assert response.status_code == 422
            assert response.headers["cache-control"] == "no-store"
            if method != "HEAD":
                assert response.json() == {
                    "schema": "uca-local-product-error-1",
                    "code": "invalid_command",
                    "message": "invalid command.",
                    "project_id": None,
                    "program_id": None,
                    "request_id": None,
                    "retry_effect": False,
                }
        assert calls(tmp_path) == b""
        assert sql(tmp_path, "SELECT * FROM local_product_requests_v1") == []


if __name__ == "__main__":
    import uvicorn

    os.environ["UCA_SAFE_EDIT_PROTOCOL"] = json.loads(
        (Path(sys.argv[2]) / "binding.json").read_text()
    )["edit_protocol"]
    app, _ = make_app(Path(sys.argv[2]))
    uvicorn.run(app, host="127.0.0.1", port=int(sys.argv[3]), log_level="warning")
