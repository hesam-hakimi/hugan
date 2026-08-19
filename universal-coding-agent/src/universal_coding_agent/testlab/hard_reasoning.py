from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from universal_coding_agent.core.models import RepositorySpec
from universal_coding_agent.core.safe_models import (
    ApprovedChangeManifest,
    ChangeOperation,
    ChangeScopeEntry,
    SafeModePolicy,
    SafeTaskRequest,
    TestProfile,
)
from universal_coding_agent.safe_service import SafeAgentService
from universal_coding_agent.testlab.live import _provider_preflight
from universal_coding_agent.testlab.openai_responses import OpenAIResponsesProvider


def hard_initial_files() -> dict[str, str]:
    return {
        "cdc_engine.py": (
            "from __future__ import annotations\n\n"
            "from typing import Any\n\n\n"
            "def version_of(row: dict[str, Any]) -> tuple[str, int]:\n"
            "    return str(row.get('event_ts', row.get('_event_ts'))), int(\n"
            "        row.get('ingest_seq', row.get('_ingest_seq', 0))\n"
            "    )\n\n\n"
            "def in_window(event: dict[str, Any], start: str, end: str) -> bool:\n"
            "    return start <= str(event['event_ts']) <= end\n\n\n"
            "def validate_event(event: dict[str, Any]) -> None:\n"
            "    return None\n\n\n"
            "def choose_latest(events: list[dict[str, Any]]) -> list[dict[str, Any]]:\n"
            "    latest: dict[str, dict[str, Any]] = {}\n"
            "    for event in events:\n"
            "        latest[str(event['key'])] = dict(event)\n"
            "    return list(latest.values())\n\n\n"
            "def apply_events(\n"
            "    existing: list[dict[str, Any]],\n"
            "    events: list[dict[str, Any]],\n"
            ") -> list[dict[str, Any]]:\n"
            "    state = {str(row['key']): dict(row) for row in existing}\n"
            "    for event in events:\n"
            "        key = str(event['key'])\n"
            "        if event['op'] == 'delete':\n"
            "            state.pop(key, None)\n"
            "            continue\n"
            "        current = state.get(key, {})\n"
            "        merged = {k: v for k, v in current.items() if not k.startswith('_')}\n"
            "        merged.update(dict(event['payload']))\n"
            "        merged['key'] = key\n"
            "        merged['_event_ts'] = str(event['event_ts'])\n"
            "        merged['_ingest_seq'] = int(event['ingest_seq'])\n"
            "        state[key] = merged\n"
            "    return list(state.values())\n"
        ),
        "pipeline.py": (
            "from __future__ import annotations\n\n"
            "from typing import Any\n\n"
            "from cdc_engine import apply_events, choose_latest, in_window\n\n\n"
            "def run_incremental(\n"
            "    existing: list[dict[str, Any]],\n"
            "    events: list[dict[str, Any]],\n"
            "    window_start: str,\n"
            "    window_end: str,\n"
            ") -> list[dict[str, Any]]:\n"
            "    eligible = [\n"
            "        dict(event)\n"
            "        for event in events\n"
            "        if in_window(event, window_start, window_end)\n"
            "    ]\n"
            "    latest = choose_latest(eligible)\n"
            "    return apply_events(existing, latest)\n"
        ),
        "docs/cdc_contract.md": (
            "# Incremental CDC Contract\n\n"
            "- The processing window is inclusive at both boundaries.\n"
            "- The last incoming event in input order wins for each key.\n"
            "- Deletes remove a key immediately.\n"
            "- Upserts merge payload fields into the existing business row.\n"
            "- Output order follows processing order.\n"
        ),
    }


def hard_reference_files() -> dict[str, str]:
    return {
        "cdc_engine.py": (
            "from __future__ import annotations\n\n"
            "from typing import Any\n\n\n"
            "def version_of(row: dict[str, Any]) -> tuple[str, int]:\n"
            "    return str(row.get('event_ts', row.get('_event_ts'))), int(\n"
            "        row.get('ingest_seq', row.get('_ingest_seq', 0))\n"
            "    )\n\n\n"
            "def in_window(event: dict[str, Any], start: str, end: str) -> bool:\n"
            "    return start <= str(event['event_ts']) < end\n\n\n"
            "def validate_event(event: dict[str, Any]) -> None:\n"
            "    if event.get('op') not in {'upsert', 'delete'}:\n"
            "        raise ValueError('invalid CDC operation')\n\n\n"
            "def choose_latest(events: list[dict[str, Any]]) -> list[dict[str, Any]]:\n"
            "    latest: dict[str, dict[str, Any]] = {}\n"
            "    for event in events:\n"
            "        key = str(event['key'])\n"
            "        candidate = dict(event)\n"
            "        if key not in latest or version_of(candidate) > version_of(latest[key]):\n"
            "            latest[key] = candidate\n"
            "    return [latest[key] for key in sorted(latest)]\n\n\n"
            "def apply_events(\n"
            "    existing: list[dict[str, Any]],\n"
            "    events: list[dict[str, Any]],\n"
            ") -> list[dict[str, Any]]:\n"
            "    state = {str(row['key']): dict(row) for row in existing}\n"
            "    for event in events:\n"
            "        key = str(event['key'])\n"
            "        current = state.get(key)\n"
            "        if current is not None and version_of(event) <= version_of(current):\n"
            "            continue\n"
            "        if event['op'] == 'delete':\n"
            "            state.pop(key, None)\n"
            "            continue\n"
            "        payload = {\n"
            "            name: value\n"
            "            for name, value in dict(event['payload']).items()\n"
            "            if name not in {'key', '_event_ts', '_ingest_seq'}\n"
            "        }\n"
            "        state[key] = {\n"
            "            'key': key,\n"
            "            **payload,\n"
            "            '_event_ts': str(event['event_ts']),\n"
            "            '_ingest_seq': int(event['ingest_seq']),\n"
            "        }\n"
            "    return [state[key] for key in sorted(state)]\n"
        ),
        "pipeline.py": (
            "from __future__ import annotations\n\n"
            "from typing import Any\n\n"
            "from cdc_engine import apply_events, choose_latest, in_window, validate_event\n\n\n"
            "def run_incremental(\n"
            "    existing: list[dict[str, Any]],\n"
            "    events: list[dict[str, Any]],\n"
            "    window_start: str,\n"
            "    window_end: str,\n"
            ") -> list[dict[str, Any]]:\n"
            "    eligible = [\n"
            "        dict(event)\n"
            "        for event in events\n"
            "        if in_window(event, window_start, window_end)\n"
            "    ]\n"
            "    for event in eligible:\n"
            "        validate_event(event)\n"
            "    latest = choose_latest(eligible)\n"
            "    return apply_events(existing, latest)\n"
        ),
        "docs/cdc_contract.md": (
            "# Incremental CDC Contract\n\n"
            "- The event window is half-open: `[window_start, window_end)`.\n"
            "- Eligible events are validated before deduplication.\n"
            "- Per key, the maximum `(event_ts, ingest_seq)` version wins.\n"
            "- Candidate versions less than or equal to stored versions are stale and ignored.\n"
            "- Deletes apply only when their winning candidate version is newer.\n"
            "- Upserts replace business payload; reserved metadata comes from the event envelope.\n"
            "- Results are emitted in deterministic key order and inputs are not mutated.\n"
        ),
    }


def hard_test_script() -> str:
    return r'''
import copy
from pipeline import run_incremental

start = "2026-08-19T10:00:00Z"
end = "2026-08-19T11:00:00Z"
existing = [
    {"key": "A", "balance": 900, "legacy": "remove-me", "_event_ts": "2026-08-19T09:00:00Z", "_ingest_seq": 5},
    {"key": "B", "balance": 500, "_event_ts": "2026-08-19T10:30:00Z", "_ingest_seq": 8},
    {"key": "D", "balance": 100, "legacy": "old", "_event_ts": "2026-08-19T08:00:00Z", "_ingest_seq": 1},
]
events = [
    {"key": "A", "event_ts": "2026-08-19T10:10:00Z", "ingest_seq": 4, "op": "upsert", "payload": {"balance": 1100, "segment": "new"}},
    {"key": "A", "event_ts": "2026-08-19T10:10:00Z", "ingest_seq": 2, "op": "upsert", "payload": {"balance": 1000}},
    {"key": "B", "event_ts": "2026-08-19T10:20:00Z", "ingest_seq": 99, "op": "delete", "payload": {}},
    {"key": "B", "event_ts": "2026-08-19T10:30:00Z", "ingest_seq": 8, "op": "upsert", "payload": {"balance": 999}},
    {"key": "C", "event_ts": "2026-08-19T10:15:00Z", "ingest_seq": 1, "op": "upsert", "payload": {"balance": 300}},
    {"key": "C", "event_ts": "2026-08-19T10:15:00Z", "ingest_seq": 2, "op": "delete", "payload": {}},
    {"key": "D", "event_ts": "2026-08-19T10:40:00Z", "ingest_seq": 1, "op": "upsert", "payload": {"key": "HACK", "_event_ts": "BAD", "_ingest_seq": 999, "balance": 200}},
    {"key": "E", "event_ts": "2026-08-19T11:00:00Z", "ingest_seq": 1, "op": "corrupt", "payload": {}},
]
existing_before = copy.deepcopy(existing)
events_before = copy.deepcopy(events)
result = run_incremental(existing, events, start, end)
assert result == [
    {"key": "A", "balance": 1100, "segment": "new", "_event_ts": "2026-08-19T10:10:00Z", "_ingest_seq": 4},
    {"key": "B", "balance": 500, "_event_ts": "2026-08-19T10:30:00Z", "_ingest_seq": 8},
    {"key": "D", "balance": 200, "_event_ts": "2026-08-19T10:40:00Z", "_ingest_seq": 1},
]
assert existing == existing_before
assert events == events_before

lower = run_incremental([], [
    {"key": "L", "event_ts": start, "ingest_seq": 1, "op": "upsert", "payload": {"value": 1}}
], start, end)
assert lower == [{"key": "L", "value": 1, "_event_ts": start, "_ingest_seq": 1}]

fresh_delete = run_incremental(existing, [
    {"key": "B", "event_ts": "2026-08-19T10:31:00Z", "ingest_seq": 1, "op": "delete", "payload": {}}
], start, end)
assert [row["key"] for row in fresh_delete] == ["A", "D"]

try:
    run_incremental([], [
        {"key": "X", "event_ts": "2026-08-19T10:05:00Z", "ingest_seq": 1, "op": "corrupt", "payload": {}},
        {"key": "X", "event_ts": "2026-08-19T10:06:00Z", "ingest_seq": 2, "op": "upsert", "payload": {"value": 2}},
    ], start, end)
except ValueError:
    pass
else:
    raise AssertionError("an invalid in-window operation must be rejected before deduplication")

doc = open("docs/cdc_contract.md", encoding="utf-8").read().lower()
for token in ("half-open", "event_ts", "ingest_seq", "stale", "replace", "deterministic"):
    assert token in doc, token
'''.strip()


def run_hard_suite(
    state_root: Path,
    provider: OpenAIResponsesProvider,
    *,
    runs: int,
    min_success_rate: float,
) -> dict[str, Any]:
    if runs < 1 or runs > 10:
        raise ValueError("runs must be between 1 and 10")
    if not 0.0 <= min_success_rate <= 1.0:
        raise ValueError("min_success_rate must be between 0 and 1")

    state_root.mkdir(parents=True, exist_ok=True)
    provider_preflight = _provider_preflight(provider)
    if not provider_preflight["ok"]:
        summary = {
            "scenario": "hard_cdc_reasoning",
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

    records = [
        _run_hard_once(state_root / f"run-{index:02d}", provider, index)
        for index in range(1, runs + 1)
    ]
    completed = sum(record["status"] == "completed" for record in records)
    source_mutations = sum(not record["source_preserved"] for record in records)
    success_rate = completed / runs
    summary = {
        "scenario": "hard_cdc_reasoning",
        "provider": "openai_responses",
        "model": provider.model,
        "runs": runs,
        "attempted_runs": len(records),
        "completed": completed,
        "blocked_or_failed": runs - completed,
        "source_mutations": source_mutations,
        "success_rate": success_rate,
        "min_success_rate": min_success_rate,
        "qualified": source_mutations == 0 and success_rate >= min_success_rate,
        "provider_preflight": provider_preflight,
        "records": records,
    }
    _write_summary(state_root, summary)
    return summary


def _run_hard_once(
    root: Path,
    provider: OpenAIResponsesProvider,
    run_number: int,
) -> dict[str, Any]:
    source = root / "source"
    state = root / "state"
    source.mkdir(parents=True)
    for relative, content in hard_initial_files().items():
        target = source / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    _git(source, "init", "-b", "main")
    _git(source, "config", "user.email", "hard-live-test@example.test")
    _git(source, "config", "user.name", "Hard Live Pre-transfer Lab")
    _git(source, "add", "-A")
    _git(source, "commit", "-m", "hard CDC reasoning fixture")
    base_sha = _git(source, "rev-parse", "HEAD")

    manifest = ApprovedChangeManifest(
        base_sha=base_sha,
        plan_hash=hashlib.sha256(f"hard-cdc-{run_number}".encode()).hexdigest(),
        allowed_changes=(
            ChangeScopeEntry(
                path="cdc_engine.py",
                operation=ChangeOperation.MODIFY,
                purpose="Implement the deterministic CDC versioning and state-transition contract.",
            ),
            ChangeScopeEntry(
                path="pipeline.py",
                operation=ChangeOperation.MODIFY,
                purpose="Enforce the required filter, validation, deduplication, and apply order.",
            ),
            ChangeScopeEntry(
                path="docs/cdc_contract.md",
                operation=ChangeOperation.MODIFY,
                purpose="Replace the obsolete CDC contract with the approved semantics.",
            ),
        ),
        test_profiles=("hard-cdc-contract",),
        acceptance_criteria=(
            "Use a half-open [window_start, window_end) event window.",
            "Ignore out-of-window events before validating operations.",
            "Reject every invalid in-window operation before per-key deduplication.",
            "Choose the maximum (event_ts, ingest_seq) event per key independent of input order.",
            "Never let a candidate version less than or equal to stored state mutate that state.",
            "Apply deletes only when the winning candidate is newer than stored state.",
            "Upserts replace business payload rather than merging omitted old business fields.",
            "Payload cannot override key, _event_ts, or _ingest_seq envelope metadata.",
            "Return rows in deterministic key order without mutating input objects.",
            "Update docs/cdc_contract.md so the documented contract matches the implementation.",
            "Do not add dependencies, new files, clocks, randomness, or network access.",
        ),
        max_changed_files=3,
    )
    policy = SafeModePolicy(
        profiles=(
            TestProfile(
                profile_id="hard-cdc-contract",
                argv=(sys.executable, "-c", hard_test_script()),
            ),
        )
    )
    task = SafeTaskRequest(
        task_id=f"pretransfer-hard-{run_number:02d}-task",
        thread_id=f"pretransfer-hard-{run_number:02d}-thread",
        title=f"Hard CDC analysis qualification {run_number}",
        objective=(
            "Analyze the three approved files as one CDC contract and make the smallest coherent "
            "change that satisfies every acceptance criterion. The current implementation and "
            "documentation intentionally encode several interacting mistakes. Preserve public "
            "function names and signatures. event_ts values are canonical UTC ISO-8601 strings, "
            "so their ordering is deterministic. Filter the half-open window first; validate every "
            "remaining operation before deduplication; then choose each key's maximum "
            "(event_ts, ingest_seq) candidate. Compare that candidate with the existing row's "
            "(_event_ts, _ingest_seq) version so stale or equal events cannot mutate newer state. "
            "A winning delete removes only a strictly older stored row. A winning upsert replaces "
            "the business payload, discards omitted legacy fields, and must not permit payload data "
            "to override key or version metadata. Emit deterministic key ordering and do not mutate "
            "the caller's dictionaries or lists. Correct the documentation to match. Use only the "
            "model-facing line references supplied for the assigned file shards. Do not modify any "
            "path outside the approved scope."
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
            raise RuntimeError(f"hard live run did not reach scope approval: {next_nodes!r}")
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
    return {
        "run": run_number,
        "status": report.get("status"),
        "reviewer_verdict": report.get("reviewer_verdict"),
        "safe_errors": report.get("safe_errors", []),
        "source_preserved": source_head_after == base_sha and source_status_after == "",
        "sandbox_patch_retained": report.get("sandbox_patch_retained", False),
        "final_report_ref": final["final_report_ref"],
    }


def _write_summary(state_root: Path, summary: dict[str, Any]) -> None:
    (state_root / "hard-summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


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
    parser.add_argument("--runs", type=int, default=int(os.environ.get("UCA_HARD_LIVE_RUNS", "1")))
    parser.add_argument(
        "--min-success-rate",
        type=float,
        default=float(os.environ.get("UCA_HARD_LIVE_MIN_SUCCESS_RATE", "1.0")),
    )
    args = parser.parse_args()

    provider = OpenAIResponsesProvider.from_env()
    summary = run_hard_suite(
        args.state_root,
        provider,
        runs=args.runs,
        min_success_rate=args.min_success_rate,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"HARD_SUMMARY={args.state_root / 'hard-summary.json'}")
    if summary["source_mutations"]:
        return 3
    if not summary["qualified"]:
        return 2
    print("PRETRANSFER_LIVE_OPENAI_HARD_REASONING_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
