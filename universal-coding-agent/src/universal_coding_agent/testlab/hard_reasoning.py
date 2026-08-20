from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from textwrap import dedent
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
        "cdc_engine.py": dedent(
            '''\
            from __future__ import annotations

            from typing import Any


            def version_of(row: dict[str, Any]) -> tuple[str, int]:
                return str(row.get("event_ts", row.get("_event_ts"))), int(
                    row.get("ingest_seq", row.get("_ingest_seq", 0))
                )


            def in_window(event: dict[str, Any], start: str, end: str) -> bool:
                return start <= str(event["event_ts"]) <= end


            def validate_event(event: dict[str, Any]) -> None:
                return None


            def choose_latest(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
                latest: dict[str, dict[str, Any]] = {}
                for event in events:
                    latest[str(event["key"])] = dict(event)
                return list(latest.values())


            def apply_events(
                existing: list[dict[str, Any]],
                events: list[dict[str, Any]],
            ) -> list[dict[str, Any]]:
                state = {str(row["key"]): dict(row) for row in existing}
                for event in events:
                    key = str(event["key"])
                    if event["op"] == "delete":
                        state.pop(key, None)
                        continue
                    current = state.get(key, {})
                    merged = {k: v for k, v in current.items() if not k.startswith("_")}
                    merged.update(dict(event["payload"]))
                    merged["key"] = key
                    merged["_event_ts"] = str(event["event_ts"])
                    merged["_ingest_seq"] = int(event["ingest_seq"])
                    state[key] = merged
                return list(state.values())
            '''
        ),
        "pipeline.py": dedent(
            '''\
            from __future__ import annotations

            from typing import Any

            from cdc_engine import apply_events, choose_latest, in_window


            def run_incremental(
                existing: list[dict[str, Any]],
                events: list[dict[str, Any]],
                window_start: str,
                window_end: str,
            ) -> list[dict[str, Any]]:
                eligible = [
                    dict(event)
                    for event in events
                    if in_window(event, window_start, window_end)
                ]
                latest = choose_latest(eligible)
                return apply_events(existing, latest)
            '''
        ),
        "docs/cdc_contract.md": dedent(
            '''\
            # Incremental CDC Contract

            - The processing window is inclusive at both boundaries.
            - The last incoming event in input order wins for each key.
            - Deletes remove a key immediately.
            - Upserts merge payload fields into the existing business row.
            - Output order follows processing order.
            '''
        ),
    }


def hard_reference_files() -> dict[str, str]:
    return {
        "cdc_engine.py": dedent(
            '''\
            from __future__ import annotations

            from typing import Any


            def _incoming_version(event: dict[str, Any]) -> tuple[str, int]:
                return str(event["event_ts"]), int(event["ingest_seq"])


            def _stored_version(row: dict[str, Any]) -> tuple[str, int]:
                return str(row["_event_ts"]), int(row["_ingest_seq"])


            def version_of(row: dict[str, Any]) -> tuple[str, int]:
                if "_event_ts" in row and "_ingest_seq" in row:
                    return _stored_version(row)
                return _incoming_version(row)


            def in_window(event: dict[str, Any], start: str, end: str) -> bool:
                return start <= str(event["event_ts"]) < end


            def validate_event(event: dict[str, Any]) -> None:
                operation = event.get("op")
                if operation not in {"upsert", "delete"}:
                    raise ValueError("invalid CDC operation")
                if operation == "upsert" and not isinstance(event.get("payload"), dict):
                    raise ValueError("upsert payload must be a dictionary")


            def choose_latest(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
                for event in events:
                    validate_event(event)

                latest: dict[str, dict[str, Any]] = {}
                for event in events:
                    key = str(event["key"])
                    candidate = dict(event)
                    current = latest.get(key)
                    if current is None:
                        latest[key] = candidate
                        continue
                    candidate_version = _incoming_version(candidate)
                    current_version = _incoming_version(current)
                    if candidate_version > current_version:
                        latest[key] = candidate
                    elif candidate_version == current_version and candidate != current:
                        raise ValueError(
                            "conflicting CDC events share the same key and version"
                        )
                return [latest[key] for key in sorted(latest)]


            def apply_events(
                existing: list[dict[str, Any]],
                events: list[dict[str, Any]],
            ) -> list[dict[str, Any]]:
                state = {str(row["key"]): dict(row) for row in existing}
                reserved = {
                    "key",
                    "event_ts",
                    "ingest_seq",
                    "_event_ts",
                    "_ingest_seq",
                }
                for event in choose_latest(events):
                    key = str(event["key"])
                    current = state.get(key)
                    candidate_version = _incoming_version(event)
                    if current is not None and candidate_version <= _stored_version(current):
                        continue

                    if event["op"] == "delete":
                        if current is not None:
                            del state[key]
                        continue

                    payload = {
                        field: value
                        for field, value in event["payload"].items()
                        if field not in reserved
                    }
                    state[key] = {
                        **payload,
                        "key": key,
                        "_event_ts": candidate_version[0],
                        "_ingest_seq": candidate_version[1],
                    }
                return [state[key] for key in sorted(state)]
            '''
        ),
        "pipeline.py": dedent(
            '''\
            from __future__ import annotations

            from typing import Any

            from cdc_engine import apply_events, choose_latest, in_window, validate_event


            def run_incremental(
                existing: list[dict[str, Any]],
                events: list[dict[str, Any]],
                window_start: str,
                window_end: str,
            ) -> list[dict[str, Any]]:
                eligible = [
                    dict(event)
                    for event in events
                    if in_window(event, window_start, window_end)
                ]
                for event in eligible:
                    validate_event(event)
                latest = choose_latest(eligible)
                return apply_events(existing, latest)
            '''
        ),
        "docs/cdc_contract.md": dedent(
            '''\
            # Incremental CDC Contract

            - The event window is half-open: `[window_start, window_end)`.
            - Eligible events are validated before deduplication.
            - Per key, the maximum `(event_ts, ingest_seq)` incoming version wins.
            - Conflicting events with the same key and identical version are rejected.
            - Exact duplicate equal-version events may collapse to one candidate.
            - Stored-state comparisons use only `(_event_ts, _ingest_seq)`.
            - Business payload fields named `event_ts` or `ingest_seq` are not version metadata.
            - Candidate versions less than or equal to stored versions are stale and ignored.
            - Deletes apply only when their winning candidate version is newer.
            - Upserts replace business payload; reserved metadata comes from the event envelope.
            - Results are emitted in deterministic key order and inputs are not mutated.
            '''
        ),
    }


def hard_test_script() -> str:
    return dedent(
        r'''
        import copy
        import os
        import sys

        sys.path.insert(0, os.getcwd())
        from pipeline import run_incremental

        start = "2026-08-19T10:00:00Z"
        end = "2026-08-19T11:00:00Z"
        existing = [
            {
                "key": "A",
                "balance": 900,
                "legacy": "remove-me",
                "_event_ts": "2026-08-19T09:00:00Z",
                "_ingest_seq": 5,
            },
            {
                "key": "B",
                "balance": 500,
                "_event_ts": "2026-08-19T10:30:00Z",
                "_ingest_seq": 8,
            },
            {
                "key": "D",
                "balance": 100,
                "legacy": "old",
                "_event_ts": "2026-08-19T08:00:00Z",
                "_ingest_seq": 1,
            },
        ]
        events = [
            {
                "key": "A",
                "event_ts": "2026-08-19T10:10:00Z",
                "ingest_seq": 4,
                "op": "upsert",
                "payload": {"balance": 1100, "segment": "new"},
            },
            {
                "key": "A",
                "event_ts": "2026-08-19T10:10:00Z",
                "ingest_seq": 2,
                "op": "upsert",
                "payload": {"balance": 1000},
            },
            {
                "key": "B",
                "event_ts": "2026-08-19T10:20:00Z",
                "ingest_seq": 99,
                "op": "delete",
                "payload": {},
            },
            {
                "key": "B",
                "event_ts": "2026-08-19T10:30:00Z",
                "ingest_seq": 8,
                "op": "upsert",
                "payload": {"balance": 999},
            },
            {
                "key": "C",
                "event_ts": "2026-08-19T10:15:00Z",
                "ingest_seq": 1,
                "op": "upsert",
                "payload": {"balance": 300},
            },
            {
                "key": "C",
                "event_ts": "2026-08-19T10:15:00Z",
                "ingest_seq": 2,
                "op": "delete",
                "payload": {},
            },
            {
                "key": "D",
                "event_ts": "2026-08-19T10:40:00Z",
                "ingest_seq": 1,
                "op": "upsert",
                "payload": {
                    "key": "HACK",
                    "_event_ts": "BAD",
                    "_ingest_seq": 999,
                    "balance": 200,
                },
            },
            {
                "key": "E",
                "event_ts": "2026-08-19T11:00:00Z",
                "ingest_seq": 1,
                "op": "corrupt",
                "payload": {},
            },
        ]
        existing_before = copy.deepcopy(existing)
        events_before = copy.deepcopy(events)
        result = run_incremental(existing, events, start, end)
        assert result == [
            {
                "key": "A",
                "balance": 1100,
                "segment": "new",
                "_event_ts": "2026-08-19T10:10:00Z",
                "_ingest_seq": 4,
            },
            {
                "key": "B",
                "balance": 500,
                "_event_ts": "2026-08-19T10:30:00Z",
                "_ingest_seq": 8,
            },
            {
                "key": "D",
                "balance": 200,
                "_event_ts": "2026-08-19T10:40:00Z",
                "_ingest_seq": 1,
            },
        ]
        assert existing == existing_before
        assert events == events_before

        lower_event = {
            "key": "L",
            "event_ts": start,
            "ingest_seq": 1,
            "op": "upsert",
            "payload": {"value": 1},
        }
        lower = run_incremental([], [lower_event], start, end)
        assert lower == [
            {"key": "L", "value": 1, "_event_ts": start, "_ingest_seq": 1}
        ]

        fresh_delete = run_incremental(
            existing,
            [
                {
                    "key": "B",
                    "event_ts": "2026-08-19T10:31:00Z",
                    "ingest_seq": 1,
                    "op": "delete",
                    "payload": {},
                }
            ],
            start,
            end,
        )
        assert [row["key"] for row in fresh_delete] == ["A", "D"]

        try:
            run_incremental(
                [],
                [
                    {
                        "key": "X",
                        "event_ts": "2026-08-19T10:05:00Z",
                        "ingest_seq": 1,
                        "op": "corrupt",
                        "payload": {},
                    },
                    {
                        "key": "X",
                        "event_ts": "2026-08-19T10:06:00Z",
                        "ingest_seq": 2,
                        "op": "upsert",
                        "payload": {"value": 2},
                    },
                ],
                start,
                end,
            )
        except ValueError:
            pass
        else:
            raise AssertionError(
                "invalid in-window operation must be rejected before deduplication"
            )

        stored_with_business_version_fields = [
            {
                "key": "F",
                "balance": 10,
                "event_ts": "2099-01-01T00:00:00Z",
                "ingest_seq": 999999,
                "_event_ts": "2026-08-19T10:00:00Z",
                "_ingest_seq": 1,
            }
        ]
        protected = run_incremental(
            stored_with_business_version_fields,
            [
                {
                    "key": "F",
                    "event_ts": "2026-08-19T10:45:00Z",
                    "ingest_seq": 2,
                    "op": "upsert",
                    "payload": {
                        "balance": 700,
                        "event_ts": "2099-12-31T23:59:59Z",
                        "ingest_seq": 777777,
                        "_event_ts": "BAD",
                        "_ingest_seq": 888888,
                    },
                }
            ],
            start,
            end,
        )
        assert protected == [
            {
                "key": "F",
                "balance": 700,
                "_event_ts": "2026-08-19T10:45:00Z",
                "_ingest_seq": 2,
            }
        ]

        conflict_a = {
            "key": "T",
            "event_ts": "2026-08-19T10:50:00Z",
            "ingest_seq": 3,
            "op": "upsert",
            "payload": {"value": 1},
        }
        conflict_b = {
            "key": "T",
            "event_ts": "2026-08-19T10:50:00Z",
            "ingest_seq": 3,
            "op": "delete",
            "payload": {},
        }
        for tied_events in (
            [conflict_a, conflict_b],
            [conflict_b, conflict_a],
        ):
            try:
                run_incremental([], tied_events, start, end)
            except ValueError:
                pass
            else:
                raise AssertionError(
                    "conflicting equal-version events must reject in either order"
                )

        duplicate = {
            "key": "U",
            "event_ts": "2026-08-19T10:55:00Z",
            "ingest_seq": 4,
            "op": "upsert",
            "payload": {"value": 9},
        }
        duplicate_result = run_incremental(
            [],
            [duplicate, copy.deepcopy(duplicate)],
            start,
            end,
        )
        assert duplicate_result == [
            {
                "key": "U",
                "value": 9,
                "_event_ts": "2026-08-19T10:55:00Z",
                "_ingest_seq": 4,
            }
        ]

        doc = open("docs/cdc_contract.md", encoding="utf-8").read().lower()
        for token in (
            "half-open",
            "event_ts",
            "ingest_seq",
            "replace",
            "deterministic",
            "conflict",
        ):
            assert token in doc, token
        assert "stale" in doc or "less than or equal" in doc
        '''
    ).strip()


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
        return _finish_summary(
            state_root,
            provider,
            runs,
            min_success_rate,
            provider_preflight,
            [],
        )

    records: list[dict[str, Any]] = []
    harness_error: str | None = None
    try:
        for index in range(1, runs + 1):
            records.append(
                _run_hard_once(state_root / f"run-{index:02d}", provider, index)
            )
    except Exception as exc:
        harness_error = type(exc).__name__

    return _finish_summary(
        state_root,
        provider,
        runs,
        min_success_rate,
        provider_preflight,
        records,
        harness_error=harness_error,
    )


def _finish_summary(
    state_root: Path,
    provider: OpenAIResponsesProvider,
    runs: int,
    min_success_rate: float,
    provider_preflight: dict[str, Any],
    records: list[dict[str, Any]],
    *,
    harness_error: str | None = None,
) -> dict[str, Any]:
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
        "qualified": (
            harness_error is None
            and source_mutations == 0
            and success_rate >= min_success_rate
        ),
        "provider_preflight": provider_preflight,
        "records": records,
    }
    if harness_error is not None:
        summary["harness_error"] = harness_error
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
    checker_path = root / "hard_contract_check.py"
    checker_path.write_text(hard_test_script() + "\n", encoding="utf-8")

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
                purpose="Implement deterministic CDC versioning and state transitions.",
            ),
            ChangeScopeEntry(
                path="pipeline.py",
                operation=ChangeOperation.MODIFY,
                purpose="Enforce filter, validation, deduplication, and apply order.",
            ),
            ChangeScopeEntry(
                path="docs/cdc_contract.md",
                operation=ChangeOperation.MODIFY,
                purpose="Replace the obsolete CDC contract with approved semantics.",
            ),
        ),
        test_profiles=("hard-cdc-contract",),
        acceptance_criteria=(
            "Use a half-open [window_start, window_end) event window.",
            "Ignore out-of-window events before validating operations.",
            "Reject every invalid in-window operation before per-key deduplication.",
            "Choose maximum (event_ts, ingest_seq) per key independent of input order.",
            (
                "Reject conflicting same-key events with identical (event_ts, ingest_seq) "
                "regardless of input order; exact duplicate events may collapse."
            ),
            "Candidate versions less than or equal to stored state must not mutate it.",
            "Stored-state comparisons always use _event_ts and _ingest_seq metadata.",
            "Business event_ts/ingest_seq fields in stored rows are never version metadata.",
            "Apply deletes only when the winning candidate is newer than stored state.",
            "Upserts replace business payload instead of merging omitted legacy fields.",
            (
                "Payload cannot persist or override key, event_ts, ingest_seq, "
                "_event_ts, or _ingest_seq version/envelope fields."
            ),
            "Return deterministic key order without mutating caller-owned inputs.",
            "Update docs/cdc_contract.md to match the implemented contract.",
            "Do not add dependencies, new files, clocks, randomness, or network access.",
        ),
        max_changed_files=3,
    )
    policy = SafeModePolicy(
        profiles=(
            TestProfile(
                profile_id="hard-cdc-contract",
                argv=(sys.executable, str(checker_path)),
            ),
        )
    )
    task = SafeTaskRequest(
        task_id=f"pretransfer-hard-{run_number:02d}-task",
        thread_id=f"pretransfer-hard-{run_number:02d}-thread",
        title=f"Hard CDC analysis qualification {run_number}",
        objective=(
            "Analyze the three approved files as one CDC contract and make the smallest "
            "coherent change satisfying every acceptance criterion. The current code and "
            "documentation intentionally contain interacting mistakes. Preserve public "
            "function names and signatures. event_ts values are canonical UTC ISO-8601 "
            "strings. Filter the half-open window first; validate every remaining operation "
            "before deduplication; then choose each key's maximum (event_ts, ingest_seq) "
            "candidate. The result must be independent of input order: if two same-key events "
            "share an identical version but conflict in operation or payload, reject the tie "
            "deterministically in either order; exact duplicate events may collapse. Compare "
            "incoming versions only with the existing row's (_event_ts, _ingest_seq) envelope "
            "metadata, even when stored business data also contains fields named event_ts or "
            "ingest_seq. A winning delete removes only a strictly older stored row. A winning "
            "upsert replaces business payload, discards omitted legacy fields, and must strip "
            "payload attempts to persist key, event_ts, ingest_seq, _event_ts, or _ingest_seq "
            "as envelope/version fields. Emit deterministic key ordering and do not mutate "
            "caller inputs. Correct the documentation. Use only model-facing line references "
            "from assigned file shards and do not modify any path outside approved scope."
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
            raise RuntimeError(
                f"hard live run did not reach scope approval: {next_nodes!r}"
            )
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
    parser.add_argument(
        "--runs",
        type=int,
        default=int(os.environ.get("UCA_HARD_LIVE_RUNS", "1")),
    )
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
