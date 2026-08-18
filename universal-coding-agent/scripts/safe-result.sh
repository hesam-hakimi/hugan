#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
VENV_PATH="${UCA_VENV_PATH:-$PROJECT_ROOT/.venv}"
PYTHON="$VENV_PATH/bin/python"

fail() {
  printf 'UCA_SAFE_RESULT_FAIL: %s\n' "$*" >&2
  exit 1
}

usage() {
  cat <<'USAGE'
Usage:
  bash scripts/safe-result.sh --context-file PATH
  bash scripts/safe-result.sh --state-root PATH --task-id ID

Print the canonical Safe Mode result by following the artifact references stored
in safe-final-report.json. This is repair-aware: when a bounded patch
applicability repair was used, it reports the repaired proposal and repaired
validation rather than the rejected initial patch.
USAGE
}

CONTEXT_FILE=""
STATE_ROOT=""
TASK_ID=""

while (($#)); do
  case "$1" in
    --context-file)
      (($# >= 2)) || fail "--context-file requires a value"
      CONTEXT_FILE="$2"
      shift 2
      ;;
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

[[ -x "$PYTHON" ]] || fail "virtual-environment Python not found: $PYTHON"

if [[ -n "$CONTEXT_FILE" ]]; then
  [[ -f "$CONTEXT_FILE" ]] || fail "context file not found: $CONTEXT_FILE"
  readarray -t VALUES < <(
    "$PYTHON" - "$CONTEXT_FILE" <<'PY'
import json
import sys
from pathlib import Path
payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print(payload.get("state_root", ""))
print(payload.get("task_id", ""))
PY
  )
  STATE_ROOT="${VALUES[0]:-}"
  TASK_ID="${VALUES[1]:-}"
fi

[[ -n "$STATE_ROOT" ]] || fail "state root is required"
[[ -n "$TASK_ID" ]] || fail "task id is required"
[[ -d "$STATE_ROOT" ]] || fail "state root not found: $STATE_ROOT"

STATE_ROOT="$(cd -- "$STATE_ROOT" && pwd)"
TASK_ROOT="$STATE_ROOT/artifacts/tasks/$TASK_ID"
REPORT="$TASK_ROOT/safe-final-report.json"

[[ -f "$REPORT" ]] || fail "final report not found: $REPORT"

export UCA_SAFE_RESULT_STATE_ROOT="$STATE_ROOT"
export UCA_SAFE_RESULT_TASK_ID="$TASK_ID"

"$PYTHON" - <<'PY'
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

state_root = Path(os.environ["UCA_SAFE_RESULT_STATE_ROOT"])
task_id = os.environ["UCA_SAFE_RESULT_TASK_ID"]
task_root = state_root / "artifacts" / "tasks" / task_id
sandbox = state_root / "sandboxes" / task_id / "repo"


def load_path(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else {"_value": value}


def artifact_path(reference: Any) -> Path | None:
    if not isinstance(reference, str) or not reference.startswith("artifact://"):
        return None
    relative = reference[len("artifact://") :]
    return state_root / "artifacts" / relative


def load_ref(reference: Any) -> dict[str, Any]:
    path = artifact_path(reference)
    return load_path(path) if path is not None else {}


def model(payload: dict[str, Any]) -> Any:
    attempts = payload.get("attempts", [])
    if not attempts:
        return None
    return attempts[-1].get("actual_model")


def git_status(path: Path) -> list[str]:
    if not path.is_dir():
        return ["SANDBOX_NOT_FOUND"]
    result = subprocess.run(
        ["git", "-C", str(path), "status", "--porcelain=v1", "-uall"],
        check=False,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


report = load_path(task_root / "safe-final-report.json")
implementer = load_ref(report.get("implementer_validation_ref"))
patch_repair_validation = load_ref(report.get("patch_repair_validation_ref"))
validation = load_ref(report.get("patch_validation_ref"))
tests = load_ref(report.get("tests_ref"))
review = load_ref(report.get("review_ref"))

print()
print("============================================================")
print("SAFE MODE — CANONICAL FINAL RESULT")
print("============================================================")
print("FINAL_STATUS=" + str(report.get("status")))
print("REVIEWER_VERDICT=" + str(report.get("reviewer_verdict")))
print("SAFE_ERRORS=" + json.dumps(report.get("safe_errors", [])))
print("SCOPE_APPROVED=" + str(report.get("scope_approved")))
print("PATCH_REPAIR_USED=" + str(report.get("patch_repair_used", False)))
print("ROLLED_BACK=" + str(report.get("rolled_back")))
print("SANDBOX_PATCH_RETAINED=" + str(report.get("sandbox_patch_retained")))
print("IMPLEMENTER_ACTUAL_MODEL=" + str(model(implementer)))
print("IMPLEMENTER_SCHEMA_REPAIR_USED=" + str(implementer.get("repair_used")))
print("PATCH_REPAIR_ACTUAL_MODEL=" + str(model(patch_repair_validation)))
print("PATCH_REPAIR_SCHEMA_REPAIR_USED=" + str(patch_repair_validation.get("repair_used")))
print("PATCH_VALID=" + str(validation.get("valid")))
print("PATCH_CHANGED_PATHS=" + json.dumps(validation.get("changed_paths", [])))
print("PATCH_ERRORS=" + json.dumps(validation.get("errors", [])))
print("TEST_RESULTS:")
for item in tests.get("results", []):
    print(
        "- {} passed={} returncode={}".format(
            item.get("profile_id"),
            item.get("passed"),
            item.get("returncode"),
        )
    )
if not tests.get("results"):
    print("- None")
print("REVIEW_CONFIDENCE=" + str(review.get("confidence")))
print("REVIEW_REQUIRED_ACTIONS:")
for item in review.get("required_actions", []):
    print("- " + str(item))
if not review.get("required_actions"):
    print("- None")
print("SOURCE_REPOSITORY_MODIFIED=" + str(report.get("source_repository_modified")))
print("PUBLICATION_ACTION=" + str(report.get("stage_commit_push_pr_merge_deploy")))
print("SANDBOX_STATUS:")
lines = git_status(sandbox)
for line in lines:
    print("- " + line)
if not lines:
    print("- CLEAN")
print("INITIAL_PATCH_REF=" + str(report.get("initial_patch_ref")))
print("FINAL_PATCH_REF=" + str(report.get("patch_ref")))
print("PATCH_VALIDATION_REF=" + str(report.get("patch_validation_ref")))
print("PATCH_REPAIR_CONTEXT_REF=" + str(report.get("patch_repair_context_ref")))
print("FINAL_REPORT=" + str(task_root / "safe-final-report.json"))
print("SANDBOX=" + str(sandbox))
print("STATE_ROOT=" + str(state_root))
print("============================================================")
PY
