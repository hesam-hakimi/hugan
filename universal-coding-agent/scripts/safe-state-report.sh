#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
VENV_PATH="${UCA_VENV_PATH:-$PROJECT_ROOT/.venv}"
PYTHON="$VENV_PATH/bin/python"
STATE_ROOT=""
THREAD_ID=""
HOST_CLIENT="${UCA_HOST_CLIENT_PATH:-}"
HOST_PYTHON="${UCA_HOST_PYTHON:-}"
PROVIDER_FACTORY="${UCA_MODEL_PROVIDER_FACTORY:-universal_coding_agent.providers.host_subprocess:create_provider}"

usage() {
  cat <<'USAGE'
Usage: bash scripts/safe-state-report.sh [options]

Required:
  --state-root PATH      Existing Safe Mode state root.
  --thread-id ID         Existing Safe Mode thread.

Optional host provider settings:
  --host-client PATH
  --host-python PATH
  --provider-factory MODULE:FACTORY

The script is read-only. It reports the current checkpoint state, Safe Mode
artifacts, patch/test/review diagnostics, and sandbox Git status. It never
approves, resumes, modifies, stages, commits, pushes, creates/edits a PR,
merges, or deploys. Terminal states such as BLOCKED/FAILED/COMPLETED are
reported with exit code 0 so an interactive terminal is not closed merely
because the task is not accepted.
USAGE
}

fail() {
  printf 'UCA_SAFE_STATE_REPORT_FAIL: %s\n' "$*" >&2
  exit 1
}

while (($#)); do
  case "$1" in
    --state-root)
      (($# >= 2)) || fail "--state-root requires a value"
      STATE_ROOT="$2"
      shift 2
      ;;
    --thread-id)
      (($# >= 2)) || fail "--thread-id requires a value"
      THREAD_ID="$2"
      shift 2
      ;;
    --host-client)
      (($# >= 2)) || fail "--host-client requires a value"
      HOST_CLIENT="$2"
      shift 2
      ;;
    --host-python)
      (($# >= 2)) || fail "--host-python requires a value"
      HOST_PYTHON="$2"
      shift 2
      ;;
    --provider-factory)
      (($# >= 2)) || fail "--provider-factory requires a value"
      PROVIDER_FACTORY="$2"
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
[[ -n "$THREAD_ID" ]] || fail "--thread-id is required"
[[ -x "$PYTHON" ]] || fail "Universal Agent virtual environment is missing: $VENV_PATH"

if [[ -n "$HOST_CLIENT" ]]; then
  [[ -f "$HOST_CLIENT" ]] || fail "host client not found: $HOST_CLIENT"
  export UCA_HOST_CLIENT_PATH="$HOST_CLIENT"
fi
if [[ -n "$HOST_PYTHON" ]]; then
  [[ -x "$HOST_PYTHON" ]] || fail "host Python not executable: $HOST_PYTHON"
  export UCA_HOST_PYTHON="$HOST_PYTHON"
fi

CLI=(
  "$PYTHON" -m universal_coding_agent.cli
  --state-root "$STATE_ROOT"
  --provider-factory "$PROVIDER_FACTORY"
  --allow-local-sources
)

STATUS_FILE="$STATE_ROOT/safe-state-report-status.json"
"${CLI[@]}" safe-status --thread-id "$THREAD_ID" > "$STATUS_FILE"

export UCA_SAFE_REPORT_STATUS_FILE="$STATUS_FILE"
export UCA_SAFE_REPORT_STATE_ROOT="$STATE_ROOT"

"$PYTHON" - <<'PY'
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

status_path = Path(os.environ["UCA_SAFE_REPORT_STATUS_FILE"])
state_root = Path(os.environ["UCA_SAFE_REPORT_STATE_ROOT"])
payload = json.loads(status_path.read_text(encoding="utf-8"))
values = payload.get("values", {})
next_nodes = payload.get("next", [])
task = values.get("task", {})
manifest = task.get("manifest", {})
task_id = str(task.get("task_id") or "")


def load(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"_read_error": type(exc).__name__, "_path": str(path)}
    return value if isinstance(value, dict) else {"_value": value}


def last_actual_model(payload: dict[str, Any]) -> Any:
    attempts = payload.get("attempts", [])
    if not isinstance(attempts, list) or not attempts:
        return None
    last = attempts[-1]
    return last.get("actual_model") if isinstance(last, dict) else None


def git_status(root: Path) -> list[str]:
    if not root.is_dir():
        return ["SANDBOX_NOT_FOUND"]
    result = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain=v1", "-uall"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return ["GIT_STATUS_FAILED"]
    return [line for line in result.stdout.splitlines() if line.strip()]


task_root = state_root / "artifacts" / "tasks" / task_id if task_id else Path("/")
sandbox = state_root / "sandboxes" / task_id / "repo" if task_id else Path("/")

report = load(task_root / "safe-final-report.json") if task_id else {}
implementer_validation = load(task_root / "implementer-model-validation.json") if task_id else {}
proposal = load(task_root / "patch-proposal.json") if task_id else {}
patch_validation = load(task_root / "patch-validation.json") if task_id else {}
patch_apply = load(task_root / "patch-apply.json") if task_id else {}
tests = load(task_root / "test-results.json") if task_id else {}
review = load(task_root / "safe-review.json") if task_id else {}
reviewer_validation = load(task_root / "safe-reviewer-model-validation.json") if task_id else {}
rollback = load(task_root / "rollback.json") if task_id else {}

print("=" * 76)
print("SAFE MODE STATE REPORT")
print("=" * 76)
print("STATUS=" + str(values.get("status")))
print("NEXT=" + repr(next_nodes))
print("TASK_ID=" + task_id)
print("THREAD_ID=" + str(task.get("thread_id")))
print("BASE_SHA=" + str(manifest.get("base_sha")))
print("PLAN_HASH=" + str(manifest.get("plan_hash")))
print("SCOPE_HASH=" + str(values.get("scope_hash")))
print("SCOPE_APPROVED=" + str(values.get("scope_approved")))
print("PATCH_APPLIED=" + str(values.get("patch_applied")))
print("ROLLED_BACK=" + str(values.get("rolled_back")))
print("REVIEWER_VERDICT=" + str(values.get("reviewer_verdict")))
print("SAFE_ERRORS=" + json.dumps(values.get("safe_errors", [])))
print()

print("ALLOWED_CHANGES:")
for item in manifest.get("allowed_changes", []):
    print("- " + str(item.get("operation")).upper() + " " + str(item.get("path")))
if not manifest.get("allowed_changes"):
    print("- None")

print()
print("IMPLEMENTER:")
print("- actual_model=" + str(last_actual_model(implementer_validation)))
print("- schema_repair_used=" + str(implementer_validation.get("repair_used")))
print("- proposal_changed_paths=" + json.dumps(proposal.get("changed_paths", [])))
print("- proposal_summary=" + str(proposal.get("summary")))

print()
print("PATCH_VALIDATION:")
print("- valid=" + str(patch_validation.get("valid")))
print("- changed_paths=" + json.dumps(patch_validation.get("changed_paths", [])))
print("- errors=" + json.dumps(patch_validation.get("errors", [])))
print("- patch_sha256=" + str(patch_validation.get("patch_sha256")))

print()
print("PATCH_APPLY:")
print("- changed_paths=" + json.dumps(patch_apply.get("changed_paths", [])))
print("- status_lines=" + json.dumps(patch_apply.get("status_lines", [])))

print()
print("TEST_RESULTS:")
results = tests.get("results", [])
if isinstance(results, list) and results:
    for item in results:
        if isinstance(item, dict):
            print(
                "- {} passed={} returncode={}".format(
                    item.get("profile_id"), item.get("passed"), item.get("returncode")
                )
            )
else:
    print("- None")
print("- actual_changed_paths=" + json.dumps(tests.get("actual_changed_paths", [])))
print("- scope_intact=" + str(tests.get("scope_intact")))

print()
print("REVIEW:")
print("- actual_model=" + str(last_actual_model(reviewer_validation)))
print("- verdict=" + str(review.get("verdict")))
print("- confidence=" + str(review.get("confidence")))
print("- required_actions=" + json.dumps(review.get("required_actions", [])))
print("- requirement_findings=" + json.dumps(review.get("requirement_findings", [])))
print("- test_findings=" + json.dumps(review.get("test_findings", [])))

print()
print("FINAL_REPORT:")
if report:
    print("- status=" + str(report.get("status")))
    print("- reviewer_verdict=" + str(report.get("reviewer_verdict")))
    print("- scope_approved=" + str(report.get("scope_approved")))
    print("- safe_errors=" + json.dumps(report.get("safe_errors", [])))
    print("- rolled_back=" + str(report.get("rolled_back")))
    print("- sandbox_patch_retained=" + str(report.get("sandbox_patch_retained")))
else:
    print("- None")

print()
print("ROLLBACK:")
if rollback:
    print(json.dumps(rollback, indent=2)[:12000])
else:
    print("- None")

print()
print("SANDBOX_STATUS:")
status_lines = git_status(sandbox)
if status_lines:
    for line in status_lines:
        print("- " + line)
else:
    print("- CLEAN")

print()
print("ARTIFACT_PATHS:")
for name in (
    "approved-change-manifest.json",
    "scope-approval.json",
    "implementer-model-validation.json",
    "patch-proposal.json",
    "proposed.patch",
    "patch-validation.json",
    "patch-apply.json",
    "test-results.json",
    "safe-reviewer-model-validation.json",
    "safe-review.json",
    "rollback.json",
    "safe-final-report.json",
):
    path = task_root / name
    if path.exists():
        print(f"- {name}={path}")
print("- sandbox=" + str(sandbox))
print("- state_root=" + str(state_root))
print("=" * 76)

status = str(values.get("status") or "")
if status == "awaiting_scope_approval" and next_nodes == ["scope_approval"]:
    print("UCA_SAFE_STATE_AWAITING_APPROVAL")
elif status == "completed" and values.get("reviewer_verdict") == "PASS":
    print("UCA_SAFE_STATE_COMPLETED_PASS")
else:
    print("UCA_SAFE_STATE_DIAGNOSIS_REQUIRED")
    print("Do not manually modify the source repository or sandbox.")
PY
