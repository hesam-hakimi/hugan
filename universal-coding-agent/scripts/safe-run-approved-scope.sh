#!/usr/bin/env bash
set -u -o pipefail
IFS=$'\n\t'

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
VENV_PATH="${UCA_VENV_PATH:-$PROJECT_ROOT/.venv}"
PYTHON="$VENV_PATH/bin/python"

REPOSITORY=""
REF=""
TASK_FILE=""
SCOPE_FILE=""
POLICY_FILE=""
HOST_CLIENT="${UCA_HOST_CLIENT_PATH:-}"
HOST_PYTHON="${UCA_HOST_PYTHON:-}"
PROVIDER_FACTORY="${UCA_MODEL_PROVIDER_FACTORY:-universal_coding_agent.providers.host_subprocess:create_provider}"
STATE_ROOT=""
TITLE="Safe Mode approved scope run"
EXPECTED_BASE_SHA=""
EXPECTED_PLAN_HASH=""
EXPECTED_SCOPE_HASH=""
AUTO_APPROVE=0

usage() {
  cat <<'USAGE'
Usage: bash scripts/safe-run-approved-scope.sh [options]

Required:
  --repository PATH_OR_URL
  --ref REF
  --task-file PATH
  --scope-file PATH
  --policy-file PATH

Host provider:
  --host-client PATH
  --host-python PATH
  --provider-factory MODULE:FACTORY

Safety identity (recommended):
  --expected-base-sha SHA
  --expected-plan-hash HASH
  --expected-scope-hash HASH

Run options:
  --state-root PATH       Optional new state root. A unique directory is created
                          under ~/.uca-safe-runs when omitted.
  --title TEXT
  --approve               Approve only after deterministic preflight verifies
                          the exact frozen scope. Without this flag, type APPROVE
                          interactively after the preflight is printed.
  -h, --help

This script starts a NEW Safe Mode run from existing task/scope/policy control
files. It never stages, commits, pushes, creates/edits a PR, merges, or deploys.
A BLOCKED/FAILED engineering result is reported with exit code 0 so the terminal
remains available for diagnosis.
USAGE
}

fail() {
  printf 'UCA_SAFE_RUN_SCOPE_FAIL: %s\n' "$*" >&2
  exit 1
}

while (($#)); do
  case "$1" in
    --repository) REPOSITORY="$2"; shift 2 ;;
    --ref) REF="$2"; shift 2 ;;
    --task-file) TASK_FILE="$2"; shift 2 ;;
    --scope-file) SCOPE_FILE="$2"; shift 2 ;;
    --policy-file) POLICY_FILE="$2"; shift 2 ;;
    --host-client) HOST_CLIENT="$2"; shift 2 ;;
    --host-python) HOST_PYTHON="$2"; shift 2 ;;
    --provider-factory) PROVIDER_FACTORY="$2"; shift 2 ;;
    --state-root) STATE_ROOT="$2"; shift 2 ;;
    --title) TITLE="$2"; shift 2 ;;
    --expected-base-sha) EXPECTED_BASE_SHA="$2"; shift 2 ;;
    --expected-plan-hash) EXPECTED_PLAN_HASH="$2"; shift 2 ;;
    --expected-scope-hash) EXPECTED_SCOPE_HASH="$2"; shift 2 ;;
    --approve) AUTO_APPROVE=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) fail "unknown option: $1" ;;
  esac
done

[[ -n "$REPOSITORY" ]] || fail "--repository is required"
[[ -n "$REF" ]] || fail "--ref is required"
[[ -f "$TASK_FILE" ]] || fail "task file not found: $TASK_FILE"
[[ -f "$SCOPE_FILE" ]] || fail "scope file not found: $SCOPE_FILE"
[[ -f "$POLICY_FILE" ]] || fail "policy file not found: $POLICY_FILE"
[[ -x "$PYTHON" ]] || fail "Universal Agent virtual environment is missing: $VENV_PATH"

if [[ "$PROVIDER_FACTORY" == "universal_coding_agent.providers.host_subprocess:create_provider" ]]; then
  [[ -n "$HOST_CLIENT" && -f "$HOST_CLIENT" ]] || fail "valid --host-client is required"
  [[ -n "$HOST_PYTHON" && -x "$HOST_PYTHON" ]] || fail "valid --host-python is required"
  export UCA_HOST_CLIENT_PATH="$HOST_CLIENT"
  export UCA_HOST_PYTHON="$HOST_PYTHON"
fi

TASK_FILE="$(cd -- "$(dirname -- "$TASK_FILE")" && pwd)/$(basename -- "$TASK_FILE")"
SCOPE_FILE="$(cd -- "$(dirname -- "$SCOPE_FILE")" && pwd)/$(basename -- "$SCOPE_FILE")"
POLICY_FILE="$(cd -- "$(dirname -- "$POLICY_FILE")" && pwd)/$(basename -- "$POLICY_FILE")"

RUN_ID="safe-scope-$(date -u +%Y%m%dT%H%M%SZ)-$$"
if [[ -z "$STATE_ROOT" ]]; then
  STATE_ROOT="$HOME/.uca-safe-runs/$RUN_ID"
fi
mkdir -p "$STATE_ROOT"
STATE_ROOT="$(cd -- "$STATE_ROOT" && pwd)"
TASK_ID="$RUN_ID-task"
THREAD_ID="$RUN_ID-thread"

SCOPE_PREFLIGHT="$STATE_ROOT/scope-preflight.json"
export UCA_RUN_SCOPE_FILE="$SCOPE_FILE"
export UCA_RUN_REPOSITORY="$REPOSITORY"
export UCA_RUN_REF="$REF"
export UCA_RUN_EXPECTED_BASE_SHA="$EXPECTED_BASE_SHA"
export UCA_RUN_EXPECTED_PLAN_HASH="$EXPECTED_PLAN_HASH"

"$PYTHON" - <<'PY' > "$SCOPE_PREFLIGHT"
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

scope_path = Path(os.environ["UCA_RUN_SCOPE_FILE"])
repository = os.environ["UCA_RUN_REPOSITORY"]
ref = os.environ["UCA_RUN_REF"]
expected_base = os.environ.get("UCA_RUN_EXPECTED_BASE_SHA", "").strip()
expected_plan = os.environ.get("UCA_RUN_EXPECTED_PLAN_HASH", "").strip()
scope = json.loads(scope_path.read_text(encoding="utf-8"))

if expected_base and scope.get("base_sha") != expected_base:
    raise SystemExit("CONTROL_BASE_SHA_MISMATCH")
if expected_plan and scope.get("plan_hash") != expected_plan:
    raise SystemExit("CONTROL_PLAN_HASH_MISMATCH")

if Path(repository).exists():
    resolved = subprocess.run(
        ["git", "-C", repository, "rev-parse", f"{ref}^{{commit}}"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if resolved != scope.get("base_sha"):
        raise SystemExit(
            "SOURCE_BASE_SHA_MISMATCH=" + resolved + " expected=" + str(scope.get("base_sha"))
        )

print(json.dumps(scope, sort_keys=True))
PY

CLI=(
  "$PYTHON" -m universal_coding_agent.cli
  --state-root "$STATE_ROOT"
  --provider-factory "$PROVIDER_FACTORY"
  --allow-local-sources
)

"${CLI[@]}" safe \
  --repository "$REPOSITORY" \
  --ref "$REF" \
  --task-file "$TASK_FILE" \
  --scope-file "$SCOPE_FILE" \
  --policy-file "$POLICY_FILE" \
  --title "$TITLE" \
  --task-id "$TASK_ID" \
  --thread-id "$THREAD_ID" \
  > "$STATE_ROOT/safe-start.json" || fail "Safe Mode start failed"

"${CLI[@]}" safe-status --thread-id "$THREAD_ID" > "$STATE_ROOT/pre-approval-status.json" \
  || fail "Safe Mode status failed"

export UCA_RUN_PRE_STATUS="$STATE_ROOT/pre-approval-status.json"
export UCA_RUN_EXPECTED_SCOPE_HASH="$EXPECTED_SCOPE_HASH"

"$PYTHON" - <<'PY'
from __future__ import annotations

import json
import os
from pathlib import Path

payload = json.loads(Path(os.environ["UCA_RUN_PRE_STATUS"]).read_text(encoding="utf-8"))
values = payload.get("values", {})
next_nodes = payload.get("next", [])
task = values.get("task", {})
manifest = task.get("manifest", {})
expected_scope = os.environ.get("UCA_RUN_EXPECTED_SCOPE_HASH", "").strip()

if values.get("status") != "awaiting_scope_approval" or next_nodes != ["scope_approval"]:
    raise SystemExit(
        "SAFE_SCOPE_APPROVAL_INTERRUPT_INVALID="
        + repr((values.get("status"), next_nodes))
    )
if values.get("patch_proposal_ref") or values.get("patch_ref") or values.get("patch_applied"):
    raise SystemExit("PATCH_EXISTS_BEFORE_APPROVAL")
if expected_scope and values.get("scope_hash") != expected_scope:
    raise SystemExit(
        "SCOPE_HASH_MISMATCH=" + str(values.get("scope_hash")) + " expected=" + expected_scope
    )

print("=" * 72)
print("SAFE_SCOPE_APPROVAL_READY")
print("=" * 72)
print("STATE_ROOT=" + str(Path(os.environ["UCA_RUN_PRE_STATUS"]).parent))
print("TASK_ID=" + str(task.get("task_id")))
print("THREAD_ID=" + str(task.get("thread_id")))
print("BASE_SHA=" + str(manifest.get("base_sha")))
print("PLAN_HASH=" + str(manifest.get("plan_hash")))
print("SCOPE_HASH=" + str(values.get("scope_hash")))
print("ALLOWED_CHANGES:")
for item in manifest.get("allowed_changes", []):
    print("- " + str(item.get("operation")).upper() + " " + str(item.get("path")))
print("TEST_PROFILES:")
for profile in manifest.get("test_profiles", []):
    print("- " + str(profile))
print("NO PATCH HAS BEEN GENERATED OR APPLIED.")
print("=" * 72)
PY

if ((AUTO_APPROVE == 0)); then
  printf '\nType APPROVE to continue with this exact frozen scope: '
  IFS= read -r decision
  if [[ "$decision" != "APPROVE" ]]; then
    printf 'UCA_SAFE_RUN_SCOPE_CANCELLED\n'
    exit 0
  fi
fi

printf '\nUCA_SAFE_SCOPE_APPROVED\n'
printf 'UCA_SAFE_IMPLEMENTATION_START\n'

"${CLI[@]}" safe-resume \
  --thread-id "$THREAD_ID" \
  --decision approve \
  > "$STATE_ROOT/safe-resume-result.json" || true

"${CLI[@]}" safe-status --thread-id "$THREAD_ID" > "$STATE_ROOT/final-status.json" \
  || fail "final Safe Mode status failed"

export UCA_RUN_FINAL_STATUS="$STATE_ROOT/final-status.json"
export UCA_RUN_STATE_ROOT="$STATE_ROOT"

"$PYTHON" - <<'PY'
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

status_path = Path(os.environ["UCA_RUN_FINAL_STATUS"])
state_root = Path(os.environ["UCA_RUN_STATE_ROOT"])
payload = json.loads(status_path.read_text(encoding="utf-8"))
values = payload.get("values", {})
task = values.get("task", {})
task_id = str(task.get("task_id") or "")
task_root = state_root / "artifacts" / "tasks" / task_id
sandbox = state_root / "sandboxes" / task_id / "repo"


def load(name: str) -> dict[str, Any]:
    path = task_root / name
    if not path.is_file():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else {"_value": value}


def last_model(payload: dict[str, Any]) -> Any:
    attempts = payload.get("attempts", [])
    if not attempts:
        return None
    return attempts[-1].get("actual_model")


def git_status() -> list[str]:
    if not sandbox.is_dir():
        return ["SANDBOX_NOT_FOUND"]
    result = subprocess.run(
        ["git", "-C", str(sandbox), "status", "--porcelain=v1", "-uall"],
        check=False,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]

report = load("safe-final-report.json")
impl = load("implementer-model-validation.json")
patch_validation = load("patch-validation.json")
tests = load("test-results.json")
review = load("safe-review.json")
reviewer = load("safe-reviewer-model-validation.json")

print()
print("=" * 72)
print("SAFE MODE RUN RESULT")
print("=" * 72)
print("FINAL_STATUS=" + str(values.get("status")))
print("SCOPE_APPROVED=" + str(values.get("scope_approved")))
print("PATCH_APPLIED=" + str(values.get("patch_applied")))
print("ROLLED_BACK=" + str(values.get("rolled_back")))
print("REVIEWER_VERDICT=" + str(values.get("reviewer_verdict")))
print("SAFE_ERRORS=" + json.dumps(values.get("safe_errors", [])))
print("IMPLEMENTER_ACTUAL_MODEL=" + str(last_model(impl)))
print("IMPLEMENTER_REPAIR_USED=" + str(impl.get("repair_used")))
print("IMPLEMENTER_BUDGET_RETRY_USED=" + str(impl.get("budget_retry_used")))
print("PATCH_VALID=" + str(patch_validation.get("valid")))
print("PATCH_CHANGED_PATHS=" + json.dumps(patch_validation.get("changed_paths", [])))
print("TEST_RESULTS:")
for item in tests.get("results", []):
    print(
        "- {} passed={} returncode={}".format(
            item.get("profile_id"), item.get("passed"), item.get("returncode")
        )
    )
if not tests.get("results"):
    print("- None")
print("REVIEWER_ACTUAL_MODEL=" + str(last_model(reviewer)))
print("REVIEW_REQUIRED_ACTIONS=" + json.dumps(review.get("required_actions", [])))
print("SANDBOX_STATUS:")
status_lines = git_status()
if status_lines:
    for line in status_lines:
        print("- " + line)
else:
    print("- CLEAN")
print("FINAL_REPORT=" + str(task_root / "safe-final-report.json"))
print("STATE_ROOT=" + str(state_root))
print("=" * 72)

accepted = (
    values.get("status") == "completed"
    and values.get("reviewer_verdict") == "PASS"
    and not values.get("safe_errors", [])
    and values.get("patch_applied") is True
    and values.get("rolled_back") is not True
)
if accepted:
    print("UCA_SAFE_RUN_SCOPE_PASS")
else:
    print("UCA_SAFE_RUN_SCOPE_NOT_ACCEPTED")
    print("No manual scope expansion or source modification is authorized.")
PY

exit 0
