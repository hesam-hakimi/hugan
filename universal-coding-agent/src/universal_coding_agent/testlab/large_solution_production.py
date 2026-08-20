from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from universal_coding_agent.core.models import RepositorySpec
from universal_coding_agent.core.safe_models import SafeModePolicy, TestProfile
from universal_coding_agent.discovered_safe_service import DiscoveredSafeAgentService
from universal_coding_agent.safety.sanitizer import sanitize_text
from universal_coding_agent.testlab.large_solution import (
    EXPECTED_SCOPE,
    OBJECTIVE,
    active_files,
    build_large_solution,
    decoy_files,
    hidden_integration_test,
)
from universal_coding_agent.testlab.live import _provider_preflight
from universal_coding_agent.testlab.openai_responses import OpenAIResponsesProvider

_ACCEPTANCE_CRITERIA = (
    "Only manager-role actors may create an override.",
    "Unauthorized and invalid attempts do not mutate repository or audit state.",
    "Override amount must be positive.",
    "Successful override record contains customer_id, amount, and expires_at.",
    "Successful override emits exactly one credit_limit_override_created audit event.",
    "Effective limit uses the override only while as_of is strictly before expires_at.",
    "At and after expires_at the base credit limit applies.",
    "Caller-owned role collections are not mutated.",
    "Do not change legacy, batch, analytics, examples, migrations, or unrelated files.",
)


def run_large_solution_production_suite(
    state_root: Path,
    provider: OpenAIResponsesProvider,
    *,
    runs: int,
    min_success_rate: float,
) -> dict[str, Any]:
    if runs < 1 or runs > 5:
        raise ValueError("runs must be between 1 and 5")
    if not 0.0 <= min_success_rate <= 1.0:
        raise ValueError("min_success_rate must be between 0 and 1")

    state_root.mkdir(parents=True, exist_ok=True)
    provider_preflight = _provider_preflight(provider)
    records: list[dict[str, Any]] = []
    if provider_preflight["ok"]:
        for index in range(1, runs + 1):
            run_root = state_root / f"run-{index:02d}"
            try:
                records.append(_run_once(run_root, provider, index))
            except Exception as exc:
                records.append(_failed_record(run_root, index, exc))

    completed = sum(record.get("status") == "completed" for record in records)
    source_mutations = sum(not record.get("source_preserved", False) for record in records)
    exact_discovery = sum(record.get("discovery_scope_exact") is True for record in records)
    approval_gates = sum(record.get("approval_gate_reached") is True for record in records)
    success_rate = completed / runs
    summary = {
        "scenario": "large_solution_production_discovered_safe",
        "production_discovered_safe": True,
        "provider": "openai_responses",
        "model": provider.model,
        "runs": runs,
        "tracked_files_per_run": len(active_files()) + len(decoy_files()),
        "attempted_runs": len(records),
        "completed": completed,
        "discovery_scope_exact": exact_discovery,
        "approval_gate_reached": approval_gates,
        "source_mutations": source_mutations,
        "success_rate": success_rate,
        "min_success_rate": min_success_rate,
        "qualified": (
            provider_preflight["ok"]
            and len(records) == runs
            and exact_discovery == runs
            and approval_gates == runs
            and source_mutations == 0
            and success_rate >= min_success_rate
        ),
        "provider_preflight": provider_preflight,
        "records": records,
    }
    (state_root / "large-solution-summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return summary


def _run_once(
    root: Path,
    provider: OpenAIResponsesProvider,
    run_number: int,
) -> dict[str, Any]:
    base_sha = build_large_solution(root)
    source = root / "source"
    repository = RepositorySpec(url=str(source), base_ref="main")
    source_status_before = _git(source, "status", "--porcelain")
    checker_path = root / "large_solution_hidden_check.py"
    checker_path.write_text(hidden_integration_test() + "\n", encoding="utf-8")
    policy = SafeModePolicy(
        profiles=(
            TestProfile(
                profile_id="large-solution-contract",
                argv=(sys.executable, str(checker_path)),
            ),
        )
    )
    task_id = f"large-solution-production-{run_number:02d}-task"
    thread_id = f"large-solution-production-{run_number:02d}-thread"
    safe_state_root = root / "safe-state"

    previous_protocol = os.environ.get("UCA_SAFE_EDIT_PROTOCOL")
    os.environ["UCA_SAFE_EDIT_PROTOCOL"] = "v2-line-addressed"
    service = DiscoveredSafeAgentService.create(
        safe_state_root,
        provider,
        allow_local_sources=True,
    )
    try:
        start = service.start(
            task_id=task_id,
            thread_id=thread_id,
            title=f"Production discovered Safe large solution {run_number}",
            objective=OBJECTIVE,
            repository=repository,
            policy=policy,
            test_profiles=("large-solution-contract",),
            acceptance_criteria=_ACCEPTANCE_CRITERIA,
        )
        state = service.state(thread_id)
        approval_gate_reached = (
            state["values"].get("status") == "awaiting_scope_approval"
            and state["next"] == ["scope_approval"]
            and state["values"].get("edit_proposal_ref") is None
            and state["values"].get("patch_proposal_ref") is None
        )

        task_artifacts = safe_state_root / "artifacts" / "tasks" / task_id
        plan_payload = _read_json(task_artifacts / "solution-impact-plan.json")
        snapshot_payload = _read_json(task_artifacts / "solution-discovery-snapshot.json")
        provenance_payload = _read_json(task_artifacts / "solution-discovery-provenance.json")
        (root / "discovery-plan.json").write_text(
            json.dumps(plan_payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        (root / "discovery-snapshot.json").write_text(
            json.dumps(snapshot_payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        discovered_scope = {
            str(change["path"])
            for change in plan_payload.get("changes", [])
            if isinstance(change, dict) and "path" in change
        }
        discovery_scope_exact = discovered_scope == EXPECTED_SCOPE

        if not approval_gate_reached or not discovery_scope_exact:
            return {
                "run": run_number,
                "status": "blocked",
                "stage": "discovered_safe_scope_approval",
                "production_discovered_safe": True,
                "approval_gate_reached": approval_gate_reached,
                "discovered_scope": sorted(discovered_scope),
                "expected_scope": sorted(EXPECTED_SCOPE),
                "discovery_scope_exact": discovery_scope_exact,
                "edit_authority_before_approval": provenance_payload.get(
                    "edit_authority_granted"
                ),
                "source_preserved": _source_preserved(
                    source,
                    base_sha,
                    source_status_before,
                ),
            }

        final = service.resume(thread_id, True)
        report = _read_json(task_artifacts / "safe-final-report.json")
    finally:
        if previous_protocol is None:
            os.environ.pop("UCA_SAFE_EDIT_PROTOCOL", None)
        else:
            os.environ["UCA_SAFE_EDIT_PROTOCOL"] = previous_protocol

    return {
        "run": run_number,
        "status": report.get("status"),
        "stage": "production_discovered_safe_implementation",
        "production_discovered_safe": True,
        "approval_gate_reached": approval_gate_reached,
        "discovered_scope": sorted(discovered_scope),
        "expected_scope": sorted(EXPECTED_SCOPE),
        "discovery_scope_exact": discovery_scope_exact,
        "edit_authority_before_approval": provenance_payload.get("edit_authority_granted"),
        "reviewer_verdict": report.get("reviewer_verdict"),
        "safe_errors": report.get("safe_errors", []),
        "source_preserved": _source_preserved(source, base_sha, source_status_before),
        "sandbox_patch_retained": report.get("sandbox_patch_retained", False),
        "final_report_ref": final.get("final_report_ref"),
        "base_sha": start.get("base_sha"),
        "scope_hash": start.get("scope_hash"),
        "plan_hash": start.get("plan_hash"),
    }


def _failed_record(root: Path, run_number: int, exc: Exception) -> dict[str, Any]:
    source = root / "source"
    source_preserved = False
    if (source / ".git").is_dir():
        try:
            source_preserved = _git(source, "status", "--porcelain") == ""
        except (OSError, subprocess.SubprocessError):
            source_preserved = False

    task_id = f"large-solution-production-{run_number:02d}-task"
    failure_path = (
        root
        / "safe-state"
        / "artifacts"
        / "tasks"
        / task_id
        / "solution-discovery-failure.json"
    )
    failure = _read_json_if_exists(failure_path)
    error_code = getattr(exc, "code", type(exc).__name__)
    error_message = sanitize_text(str(exc))[:2000]
    return {
        "run": run_number,
        "status": "failed",
        "stage": "production_discovered_safe_harness",
        "production_discovered_safe": True,
        "approval_gate_reached": False,
        "discovery_scope_exact": False,
        "source_preserved": source_preserved,
        "error_type": type(exc).__name__,
        "error_code": str(error_code),
        "error_message": error_message,
        "failure_artifact_present": bool(failure),
        "failure_artifact_code": failure.get("code"),
        "failure_artifact_message": failure.get("message"),
    }


def _source_preserved(source: Path, base_sha: str, initial_status: str) -> bool:
    return (
        _git(source, "rev-parse", "HEAD") == base_sha
        and _git(source, "status", "--porcelain") == initial_status == ""
    )


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def _read_json_if_exists(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return _read_json(path)
    except (OSError, ValueError, json.JSONDecodeError):
        return {}


def _git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state-root", type=Path, required=True)
    parser.add_argument(
        "--runs",
        type=int,
        default=int(os.environ.get("UCA_LARGE_SOLUTION_RUNS", "1")),
    )
    parser.add_argument(
        "--min-success-rate",
        type=float,
        default=float(os.environ.get("UCA_LARGE_SOLUTION_MIN_SUCCESS_RATE", "1.0")),
    )
    args = parser.parse_args()

    provider = OpenAIResponsesProvider.from_env()
    summary = run_large_solution_production_suite(
        args.state_root,
        provider,
        runs=args.runs,
        min_success_rate=args.min_success_rate,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"LARGE_SOLUTION_SUMMARY={args.state_root / 'large-solution-summary.json'}")
    if summary["source_mutations"]:
        return 3
    if not summary["qualified"]:
        return 2
    print("PRETRANSFER_LIVE_OPENAI_PRODUCTION_LARGE_SOLUTION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
