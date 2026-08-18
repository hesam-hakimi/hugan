#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

STATE_ROOT=""
TASK_ID=""

usage() {
  cat <<'USAGE'
Usage: bash scripts/safe-implementer-diagnose.sh --state-root PATH --task-id ID

Read-only diagnosis for a Safe Mode task that failed in the Implementer
structured-output stage. It prints sanitized per-attempt schema diagnostics,
artifact presence, final status, and sandbox Git status.

This script never invokes a model, approves/resumes a task, applies a patch,
runs tests, or modifies/stages/commits/pushes/merges/deploys anything.
USAGE
}

fail() {
  printf 'UCA_SAFE_IMPLEMENTER_DIAGNOSE_FAIL: %s\n' "$*" >&2
  exit 1
}

while (($#)); do
  case "$1" in
    --state-root)
      (($# >= 2)) || fail "--state-root requires a value"
      STATE_ROOT="$2"
      shift 2
      ;;
    --task-id)
      (($# >= 2)) || fail "--task-id requires a value"
      TASK_ID="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      fail "unknown option: $1"
      ;;
  esac
done

[[ -n "$STATE_ROOT" ]] || fail "--state-root is required"
[[ -d "$STATE_ROOT" ]] || fail "state root does not exist: $STATE_ROOT"
STATE_ROOT="$(cd -- "$STATE_ROOT" && pwd)"
[[ -n "$TASK_ID" ]] || fail "--task-id is required"

TASK_ROOT="$STATE_ROOT/artifacts/tasks/$TASK_ID"
[[ -d "$TASK_ROOT" ]] || fail "task artifact directory does not exist: $TASK_ROOT"

PYTHON="${PYTHON_BIN:-python3}"
command -v "$PYTHON" >/dev/null 2>&1 || fail "$PYTHON is not available"

"$PYTHON" - "$STATE_ROOT" "$TASK_ID" <<'PY'
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

state_root = Path(sys.argv[1]).resolve()
task_id = sys.argv[2]
task_root = state_root / "artifacts" / "tasks" / task_id
sandbox = state_root / "sandboxes" / task_id / "repo"


def load_json(name: str) -> dict[str, Any]:
    path = task_root / name
    if not path.is_file():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "_read_error": type(exc).__name__,
            "_path": str(path),
        }
    return value if isinstance(value, dict) else {"_value": value}


def exists(name: str) -> bool:
    return (task_root / name).is_file()


def git_status(root: Path) -> list[str]:
    if not root.is_dir():
        return ["SANDBOX_NOT_FOUND"]
    completed = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain=v1", "-uall"],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        return ["GIT_STATUS_FAILED"]
    return [line for line in completed.stdout.splitlines() if line.strip()]


diagnostics = load_json("implementer-model-validation.json")
report = load_json("safe-final-report.json")
scope = load_json("approved-change-manifest.json")
approval = load_json("scope-approval.json")

print("=" * 78)
print("SAFE MODE IMPLEMENTER — STRUCTURED OUTPUT DIAGNOSIS")
print("=" * 78)
print(f"STATE_ROOT={state_root}")
print(f"TASK_ID={task_id}")
print(f"TASK_ROOT={task_root}")
print(f"SANDBOX={sandbox}")
print()

print("FINAL_STATE:")
print("- status=" + str(report.get("status")))
print("- scope_approved=" + str(report.get("scope_approved")))
print("- reviewer_verdict=" + str(report.get("reviewer_verdict")))
print("- safe_errors=" + json.dumps(report.get("safe_errors", [])))
print("- rolled_back=" + str(report.get("rolled_back")))
print("- sandbox_patch_retained=" + str(report.get("sandbox_patch_retained")))
print()

print("FROZEN_SCOPE:")
print("- base_sha=" + str(scope.get("base_sha")))
print("- plan_hash=" + str(scope.get("plan_hash")))
print("- approved=" + str(approval.get("approved")))
print("- scope_hash=" + str(approval.get("scope_hash")))
print("- allowed_changes:")
for item in scope.get("allowed_changes", []):
    print("  - " + str(item.get("operation")).upper() + " " + str(item.get("path")))
if not scope.get("allowed_changes"):
    print("  - None")
print()

print("IMPLEMENTER_MODEL_VALIDATION:")
print("- role=" + str(diagnostics.get("role")))
print("- repair_used=" + str(diagnostics.get("repair_used")))
attempts = diagnostics.get("attempts", [])
if not isinstance(attempts, list) or not attempts:
    print("- attempts=None")
else:
    for index, attempt in enumerate(attempts, start=1):
        if not isinstance(attempt, dict):
            print(f"- attempt_{index}=INVALID_DIAGNOSTIC_SHAPE")
            continue
        print()
        print(f"ATTEMPT_{index}:")
        print("- actual_model=" + str(attempt.get("actual_model")))
        print("- finish_reason=" + str(attempt.get("finish_reason")))
        print("- completion_tokens=" + str(attempt.get("completion_tokens")))
        print("- reasoning_tokens=" + str(attempt.get("reasoning_tokens")))
        print("- output_chars=" + str(attempt.get("output_chars")))
        print("- output_sha256=" + str(attempt.get("output_sha256")))
        print("- schema_valid=" + str(attempt.get("schema_valid")))
        issue = attempt.get("validation_issue")
        print("- validation_issue=")
        if issue:
            print(str(issue))
        else:
            print("None")
print()

print("DOWNSTREAM_ARTIFACT_PRESENCE:")
for name in (
    "patch-proposal.json",
    "proposed.patch",
    "patch-validation.json",
    "patch-apply.json",
    "test-results.json",
    "safe-reviewer-model-validation.json",
    "safe-review.json",
    "rollback.json",
):
    print(f"- {name}={exists(name)}")
print()

print("SANDBOX_STATUS:")
lines = git_status(sandbox)
if lines:
    for line in lines:
        print("- " + line)
else:
    print("- CLEAN")
print()

print("DIAGNOSTIC_ARTIFACT=" + str(task_root / "implementer-model-validation.json"))
print("FINAL_REPORT=" + str(task_root / "safe-final-report.json"))
print("=" * 78)
print("UCA_SAFE_IMPLEMENTER_DIAGNOSIS_COMPLETE")
PY
