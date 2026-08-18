#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
VENV_PATH="${UCA_VENV_PATH:-$PROJECT_ROOT/.venv}"
PYTHON="$VENV_PATH/bin/python"

STATE_ROOT=""
THREAD_ID=""
REPOSITORY=""
SCOPE_FILE=""
HOST_CLIENT=""
HOST_PYTHON=""
PROVIDER_FACTORY="universal_coding_agent.providers.host_subprocess:create_provider"
EXPECTED_BASE_SHA=""
EXPECTED_PLAN_HASH=""
EXPECTED_SCOPE_HASH=""
DECISION="approve"

usage() {
  cat <<'USAGE'
Usage:
  bash scripts/safe-approve-resume.sh \
    --state-root PATH \
    --thread-id ID \
    --repository PATH_OR_URL \
    --scope-file PATH \
    [--host-client PATH] \
    [--host-python PATH] \
    [--provider-factory MODULE:FACTORY] \
    [--expected-base-sha SHA] \
    [--expected-plan-hash HASH] \
    [--expected-scope-hash HASH] \
    [--decision approve|reject]

The script resumes an already-paused Safe Mode task. It verifies the frozen
approval state, compares the state manifest to the supplied approved scope,
captures source-repository identity before and after resume, and prints one
concise final report. It never stages, commits, pushes, creates a PR, merges,
or deploys.
USAGE
}

fail() {
  printf 'UCA_SAFE_APPROVE_RESUME_FAIL: %s\n' "$*" >&2
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
    --repository)
      (($# >= 2)) || fail "--repository requires a value"
      REPOSITORY="$2"
      shift 2
      ;;
    --scope-file)
      (($# >= 2)) || fail "--scope-file requires a value"
      SCOPE_FILE="$2"
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
    --expected-base-sha)
      (($# >= 2)) || fail "--expected-base-sha requires a value"
      EXPECTED_BASE_SHA="$2"
      shift 2
      ;;
    --expected-plan-hash)
      (($# >= 2)) || fail "--expected-plan-hash requires a value"
      EXPECTED_PLAN_HASH="$2"
      shift 2
      ;;
    --expected-scope-hash)
      (($# >= 2)) || fail "--expected-scope-hash requires a value"
      EXPECTED_SCOPE_HASH="$2"
      shift 2
      ;;
    --decision)
      (($# >= 2)) || fail "--decision requires a value"
      DECISION="$2"
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
[[ -n "$THREAD_ID" ]] || fail "--thread-id is required"
[[ -n "$REPOSITORY" ]] || fail "--repository is required"
[[ -n "$SCOPE_FILE" ]] || fail "--scope-file is required"
[[ "$DECISION" == "approve" || "$DECISION" == "reject" ]] || fail "decision must be approve or reject"
[[ -x "$PYTHON" ]] || fail "virtual-environment Python not found: $PYTHON"
[[ -f "$SCOPE_FILE" ]] || fail "scope file not found: $SCOPE_FILE"
command -v git >/dev/null 2>&1 || fail "git is not available"

mkdir -p "$STATE_ROOT"
STATE_ROOT="$(cd -- "$STATE_ROOT" && pwd)"
SCOPE_FILE="$(cd -- "$(dirname -- "$SCOPE_FILE")" && pwd)/$(basename -- "$SCOPE_FILE")"

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

PRE_STATUS="$STATE_ROOT/pre-approval-status.json"
RESUME_RESULT="$STATE_ROOT/approval-resume-result.json"

"${CLI[@]}" safe-status --thread-id "$THREAD_ID" > "$PRE_STATUS"

export UCA_APPROVE_PRE_STATUS="$PRE_STATUS"
export UCA_APPROVE_SCOPE_FILE="$SCOPE_FILE"
export UCA_APPROVE_EXPECTED_BASE_SHA="$EXPECTED_BASE_SHA"
export UCA_APPROVE_EXPECTED_PLAN_HASH="$EXPECTED_PLAN_HASH"
export UCA_APPROVE_EXPECTED_SCOPE_HASH="$EXPECTED_SCOPE_HASH"

TASK_ID="$($PYTHON - <<'PY'
from __future__ import annotations

import json
import os
from pathlib import Path

status = json.loads(Path(os.environ["UCA_APPROVE_PRE_STATUS"]).read_text(encoding="utf-8"))
scope = json.loads(Path(os.environ["UCA_APPROVE_SCOPE_FILE"]).read_text(encoding="utf-8"))
values = status.get("values", {})
task = values.get("task", {})
manifest = task.get("manifest", {})
next_nodes = status.get("next", [])

if values.get("status") != "awaiting_scope_approval":
    raise SystemExit("SAFE_STATUS_NOT_AWAITING_SCOPE_APPROVAL=" + repr(values.get("status")))
if next_nodes != ["scope_approval"]:
    raise SystemExit("SAFE_SCOPE_APPROVAL_INTERRUPT_NOT_REACHED=" + repr(next_nodes))
if values.get("patch_proposal_ref"):
    raise SystemExit("PATCH_ALREADY_GENERATED_UNEXPECTEDLY")

expected_base = os.environ.get("UCA_APPROVE_EXPECTED_BASE_SHA", "").strip()
expected_plan = os.environ.get("UCA_APPROVE_EXPECTED_PLAN_HASH", "").strip()
expected_scope = os.environ.get("UCA_APPROVE_EXPECTED_SCOPE_HASH", "").strip()

if expected_base and manifest.get("base_sha") != expected_base:
    raise SystemExit("BASE_SHA_MISMATCH")
if expected_plan and manifest.get("plan_hash") != expected_plan:
    raise SystemExit("PLAN_HASH_MISMATCH")
if expected_scope and values.get("scope_hash") != expected_scope:
    raise SystemExit("SCOPE_HASH_MISMATCH")

scope_keys = (
    "manifest_version",
    "base_sha",
    "plan_hash",
    "allowed_changes",
    "denied_prefixes",
    "test_profiles",
    "acceptance_criteria",
    "max_patch_bytes",
    "max_changed_files",
)
for key in scope_keys:
    if manifest.get(key) != scope.get(key):
        raise SystemExit(f"SCOPE_FILE_STATE_MISMATCH={key}")

print(str(task.get("task_id") or ""))
PY
)"

[[ -n "$TASK_ID" ]] || fail "task ID could not be recovered from checkpoint state"

printf 'UCA_SAFE_APPROVAL_PREFLIGHT_PASS\n'
printf 'TASK_ID=%s\n' "$TASK_ID"
printf 'THREAD_ID=%s\n' "$THREAD_ID"

$PYTHON - <<'PY'
from __future__ import annotations

import json
import os
from pathlib import Path

status = json.loads(Path(os.environ["UCA_APPROVE_PRE_STATUS"]).read_text(encoding="utf-8"))
values = status["values"]
manifest = values["task"]["manifest"]
print("BASE_SHA=" + str(manifest.get("base_sha")))
print("PLAN_HASH=" + str(manifest.get("plan_hash")))
print("SCOPE_HASH=" + str(values.get("scope_hash")))
print("ALLOWED_CHANGES:")
for item in manifest.get("allowed_changes", []):
    print("- {} {}".format(str(item.get("operation")).upper(), item.get("path")))
print("TEST_PROFILES:")
for profile in manifest.get("test_profiles", []):
    print("- " + str(profile))
PY

SOURCE_IS_LOCAL=0
if [[ -d "$REPOSITORY/.git" || -f "$REPOSITORY/.git" ]]; then
  SOURCE_IS_LOCAL=1
  git -C "$REPOSITORY" rev-parse HEAD > "$STATE_ROOT/source-head-before-approval.txt"
  git -C "$REPOSITORY" rev-parse --abbrev-ref HEAD > "$STATE_ROOT/source-branch-before-approval.txt"
  git -C "$REPOSITORY" status --porcelain=v1 -uall > "$STATE_ROOT/source-status-before-approval.txt"
  git -C "$REPOSITORY" worktree list --porcelain > "$STATE_ROOT/source-worktrees-before-approval.txt"
  printf 'SOURCE_BASELINE_CAPTURED\n'
else
  printf 'SOURCE_BASELINE_REMOTE_OR_NONLOCAL\n'
fi

printf 'HUMAN_DECISION=%s\n' "$DECISION"
"${CLI[@]}" safe-resume \
  --thread-id "$THREAD_ID" \
  --decision "$DECISION" \
  > "$RESUME_RESULT"

SOURCE_PRESERVED="NOT_APPLICABLE"
if ((SOURCE_IS_LOCAL)); then
  git -C "$REPOSITORY" rev-parse HEAD > "$STATE_ROOT/source-head-after-approval.txt"
  git -C "$REPOSITORY" rev-parse --abbrev-ref HEAD > "$STATE_ROOT/source-branch-after-approval.txt"
  git -C "$REPOSITORY" status --porcelain=v1 -uall > "$STATE_ROOT/source-status-after-approval.txt"
  git -C "$REPOSITORY" worktree list --porcelain > "$STATE_ROOT/source-worktrees-after-approval.txt"

  SOURCE_PRESERVED="YES"
  for field in head branch status worktrees; do
    if ! cmp -s \
      "$STATE_ROOT/source-${field}-before-approval.txt" \
      "$STATE_ROOT/source-${field}-after-approval.txt"; then
      SOURCE_PRESERVED="NO"
    fi
  done
fi

export UCA_APPROVE_STATE_ROOT="$STATE_ROOT"
export UCA_APPROVE_TASK_ID="$TASK_ID"
export UCA_APPROVE_SOURCE_PRESERVED="$SOURCE_PRESERVED"

"$PYTHON" - <<'PY'
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

state_root = Path(os.environ["UCA_APPROVE_STATE_ROOT"])
task_id = os.environ["UCA_APPROVE_TASK_ID"]
task_root = state_root / "artifacts" / "tasks" / task_id
sandbox = state_root / "sandboxes" / task_id / "repo"


def load(name: str) -> dict[str, Any]:
    path = task_root / name
    if not path.is_file():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else {"_value": value}


def model(payload: dict[str, Any]) -> Any:
    attempts = payload.get("attempts", [])
    if not attempts:
        return None
    return attempts[-1].get("actual_model")


def status_lines(path: Path) -> list[str]:
    if not path.is_dir():
        return ["SANDBOX_NOT_FOUND"]
    result = subprocess.run(
        ["git", "-C", str(path), "status", "--porcelain=v1", "-uall"],
        check=False,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]

report = load("safe-final-report.json")
implementer = load("implementer-model-validation.json")
validation = load("patch-validation.json")
tests = load("test-results.json")
review = load("safe-review.json")

print()
print("============================================================")
print("SAFE MODE APPROVAL / RESUME — FINAL RESULT")
print("============================================================")
print("FINAL_STATUS=" + str(report.get("status")))
print("REVIEWER_VERDICT=" + str(report.get("reviewer_verdict")))
print("SAFE_ERRORS=" + json.dumps(report.get("safe_errors", [])))
print("SCOPE_APPROVED=" + str(report.get("scope_approved")))
print("ROLLED_BACK=" + str(report.get("rolled_back")))
print("SANDBOX_PATCH_RETAINED=" + str(report.get("sandbox_patch_retained")))
print("IMPLEMENTER_ACTUAL_MODEL=" + str(model(implementer)))
print("IMPLEMENTER_SCHEMA_REPAIR_USED=" + str(implementer.get("repair_used")))
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
print("SOURCE_REPOSITORY_PRESERVED=" + os.environ["UCA_APPROVE_SOURCE_PRESERVED"])
print("SANDBOX_STATUS:")
lines = status_lines(sandbox)
for line in lines:
    print("- " + line)
if not lines:
    print("- CLEAN")
print("FINAL_REPORT=" + str(task_root / "safe-final-report.json"))
print("PATCH=" + str(task_root / "proposed.patch"))
print("TEST_RESULTS_FILE=" + str(task_root / "test-results.json"))
print("REVIEW_FILE=" + str(task_root / "safe-review.json"))
print("SANDBOX=" + str(sandbox))
print("STATE_ROOT=" + str(state_root))
print("============================================================")
PY

if [[ "$SOURCE_PRESERVED" == "NO" ]]; then
  fail "source repository changed during Safe Mode resume"
fi
