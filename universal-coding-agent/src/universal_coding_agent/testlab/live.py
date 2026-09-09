from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from universal_coding_agent.core.models import ModelRequest, RepositorySpec
from universal_coding_agent.core.safe_models import (
    ApprovedChangeManifest,
    ChangeOperation,
    ChangeScopeEntry,
    SafeModePolicy,
    SafeTaskRequest,
    StructuredEditProposal,
    TestProfile,
)
from universal_coding_agent.providers.base import ModelProviderError
from universal_coding_agent.safe_service import SafeAgentService
from universal_coding_agent.testlab.openai_responses import OpenAIResponsesProvider


def run_live_suite(
    state_root: Path,
    provider: OpenAIResponsesProvider,
    *,
    runs: int,
    min_success_rate: float,
) -> dict[str, Any]:
    if runs < 1 or runs > 20:
        raise ValueError("runs must be between 1 and 20")
    if not 0.0 <= min_success_rate <= 1.0:
        raise ValueError("min_success_rate must be between 0 and 1")

    state_root.mkdir(parents=True, exist_ok=True)
    provider_preflight = _provider_preflight(provider)
    if not provider_preflight["ok"]:
        summary = {
            "provider": "openai_responses",
            "model": provider.model,
            "runs": runs,
            "attempted_runs": 0,
            "completed": 0,
            "blocked_or_failed": 0,
            "source_mutations": 0,
            "success_rate": 0.0,
            "min_success_rate": min_success_rate,
            "qualified": False,
            "provider_preflight": provider_preflight,
            "records": [],
        }
        _write_summary(state_root, summary)
        return summary

    records: list[dict[str, Any]] = []
    for run_number in range(1, runs + 1):
        records.append(_run_once(state_root / f"run-{run_number:02d}", provider, run_number))

    completed = sum(item["status"] == "completed" for item in records)
    source_mutations = sum(not item["source_preserved"] for item in records)
    success_rate = completed / runs
    qualified = source_mutations == 0 and success_rate >= min_success_rate
    summary = {
        "provider": "openai_responses",
        "model": provider.model,
        "runs": runs,
        "attempted_runs": len(records),
        "completed": completed,
        "blocked_or_failed": runs - completed,
        "source_mutations": source_mutations,
        "success_rate": success_rate,
        "min_success_rate": min_success_rate,
        "qualified": qualified,
        "provider_preflight": provider_preflight,
        "records": records,
    }
    _write_summary(state_root, summary)
    return summary


def _provider_preflight(provider: OpenAIResponsesProvider) -> dict[str, Any]:
    stages: list[dict[str, Any]] = []
    text_request = ModelRequest(
        role="pretransfer_text_probe",
        system_prompt="Return exactly the requested text.",
        user_prompt="Return exactly UCA_OPENAI_PROVIDER_OK.",
        max_output_tokens=128,
    )
    try:
        response = provider.invoke(text_request)
    except ModelProviderError as exc:
        return _preflight_failure("text_response", exc, stages)
    stages.append(
        {
            "stage": "text_response",
            "ok": True,
            "actual_model": response.actual_model,
            "finish_reason": response.finish_reason,
        }
    )

    schema_request = ModelRequest(
        role="pretransfer_structured_schema_probe",
        system_prompt=(
            "Return exactly one StructuredEditProposal JSON object matching the supplied schema."
        ),
        user_prompt=(
            "Return a minimal preflight proposal that modifies app.py. Use summary 'preflight', "
            "operation 'modify', old_text '@range:A000001..A000001', new_text 'VALUE = 43\\n', "
            "requested_test_profiles ['live-check'], and no assumptions."
        ),
        response_schema=StructuredEditProposal.model_json_schema(),
        max_output_tokens=2_048,
    )
    try:
        response = provider.invoke(schema_request)
    except ModelProviderError as exc:
        return _preflight_failure("structured_schema", exc, stages)
    stages.append(
        {
            "stage": "structured_schema",
            "ok": True,
            "actual_model": response.actual_model,
            "finish_reason": response.finish_reason,
            "structured_object": isinstance(response.structured, dict),
        }
    )
    return {"ok": True, "stages": stages}


def _preflight_failure(
    stage: str,
    exc: ModelProviderError,
    stages: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "ok": False,
        "failed_stage": stage,
        "error": {
            "code": exc.code,
            "message": str(exc)[:2_000],
        },
        "stages": stages,
    }


def _write_summary(state_root: Path, summary: dict[str, Any]) -> None:
    (state_root / "live-summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _run_once(
    root: Path,
    provider: OpenAIResponsesProvider,
    run_number: int,
) -> dict[str, Any]:
    source = root / "source"
    state = root / "state"
    source.mkdir(parents=True)
    (source / "docs").mkdir()
    (source / "app.py").write_text("VALUE = 42\n", encoding="utf-8")
    (source / "docs" / "status.md").write_text(
        "# Qualification\nStatus: pending\n",
        encoding="utf-8",
    )
    _git(source, "init", "-b", "main")
    _git(source, "config", "user.email", "live-test@example.test")
    _git(source, "config", "user.name", "Live Pre-transfer Lab")
    _git(source, "add", "-A")
    _git(source, "commit", "-m", "live synthetic fixture")
    base_sha = _git(source, "rev-parse", "HEAD")

    manifest = ApprovedChangeManifest(
        base_sha=base_sha,
        plan_hash=hashlib.sha256(f"live-{run_number}".encode()).hexdigest(),
        allowed_changes=(
            ChangeScopeEntry(
                path="app.py",
                operation=ChangeOperation.MODIFY,
                purpose="Update the synthetic qualification constant from 42 to 43.",
            ),
            ChangeScopeEntry(
                path="docs/status.md",
                operation=ChangeOperation.MODIFY,
                purpose="Mark the synthetic qualification status as live-model-validated.",
            ),
        ),
        test_profiles=("live-check",),
        acceptance_criteria=(
            "app.py contains VALUE = 43 and no VALUE = 42.",
            "docs/status.md contains exactly Status: live-model-validated on its status line.",
            "No unapproved source path is modified.",
        ),
        max_changed_files=2,
    )
    test_script = (
        "from pathlib import Path; "
        "app=Path('app.py').read_text(encoding='utf-8'); "
        "status=Path('docs/status.md').read_text(encoding='utf-8'); "
        "assert 'VALUE = 43' in app and 'VALUE = 42' not in app; "
        "assert 'Status: live-model-validated\\n' in status"
    )
    policy = SafeModePolicy(
        profiles=(
            TestProfile(
                profile_id="live-check",
                argv=(sys.executable, "-c", test_script),
            ),
        )
    )
    task = SafeTaskRequest(
        task_id=f"pretransfer-live-{run_number:02d}-task",
        thread_id=f"pretransfer-live-{run_number:02d}-thread",
        title=f"Live OpenAI pre-transfer qualification {run_number}",
        objective=(
            "Modify only the two human-approved synthetic files. In app.py, replace the complete "
            "line VALUE = 42 with VALUE = 43. In docs/status.md, replace the complete line "
            "Status: pending with Status: live-model-validated. Use only the model-facing line "
            "references shown in each assigned file shard. Do not make any other change."
        ),
        repository=RepositorySpec(url=str(source), base_ref="main"),
        manifest=manifest,
        policy=policy,
    )

    previous_protocol = os.environ.get("UCA_SAFE_EDIT_PROTOCOL")
    os.environ["UCA_SAFE_EDIT_PROTOCOL"] = "v2-line-addressed"
    service = SafeAgentService.create(state, provider, allow_local_sources=True)
    try:
        service.run(task)
        next_nodes = service.state(task.thread_id)["next"]
        if next_nodes != ["scope_approval"]:
            raise RuntimeError(f"live run did not reach scope approval: {next_nodes!r}")
        final = service.resume(task.thread_id, True)
        report = service.artifacts.read_json(final["final_report_ref"])
    finally:
        service.close()
        if previous_protocol is None:
            os.environ.pop("UCA_SAFE_EDIT_PROTOCOL", None)
        else:
            os.environ["UCA_SAFE_EDIT_PROTOCOL"] = previous_protocol

    source_head_after = _git(source, "rev-parse", "HEAD")
    source_status_after = _git(source, "status", "--porcelain")
    source_preserved = source_head_after == base_sha and source_status_after == ""
    return {
        "run": run_number,
        "status": report.get("status"),
        "reviewer_verdict": report.get("reviewer_verdict"),
        "safe_errors": report.get("safe_errors", []),
        "source_preserved": source_preserved,
        "sandbox_patch_retained": report.get("sandbox_patch_retained", False),
        "final_report_ref": final["final_report_ref"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state-root", type=Path, required=True)
    parser.add_argument("--runs", type=int, default=int(os.environ.get("UCA_LIVE_RUNS", "1")))
    parser.add_argument(
        "--min-success-rate",
        type=float,
        default=float(os.environ.get("UCA_LIVE_MIN_SUCCESS_RATE", "1.0")),
    )
    args = parser.parse_args()

    provider = OpenAIResponsesProvider.from_env()
    summary = run_live_suite(
        args.state_root,
        provider,
        runs=args.runs,
        min_success_rate=args.min_success_rate,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"LIVE_SUMMARY={args.state_root / 'live-summary.json'}")
    if summary["source_mutations"]:
        return 3
    if not summary["qualified"]:
        return 2
    print("PRETRANSFER_LIVE_OPENAI_PASS")
    return 0


def _git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


if __name__ == "__main__":
    raise SystemExit(main())
