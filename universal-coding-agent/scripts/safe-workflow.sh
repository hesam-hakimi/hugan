#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
VENV_PATH="${UCA_VENV_PATH:-$PROJECT_ROOT/.venv}"
PYTHON="$VENV_PATH/bin/python"
DEFAULT_PROVIDER_FACTORY="universal_coding_agent.providers.host_subprocess:create_provider"

fail() {
  printf 'UCA_SAFE_WORKFLOW_FAIL: %s\n' "$*" >&2
  exit 1
}

usage() {
  cat <<'USAGE'
Usage:

  Start and pause at human approval:
    bash scripts/safe-workflow.sh start \
      --state-root PATH \
      --repository PATH_OR_URL \
      --ref REF \
      --task-file PATH \
      --scope-file PATH \
      --policy-file PATH \
      [--host-client PATH] \
      [--host-python PATH] \
      [--provider-factory MODULE:FACTORY] \
      [--title TITLE] \
      [--task-id ID] \
      [--thread-id ID]

  Show current state or terminal result:
    bash scripts/safe-workflow.sh status --context-file PATH

  Approve or reject an already-paused task:
    bash scripts/safe-workflow.sh approve --context-file PATH
    bash scripts/safe-workflow.sh reject  --context-file PATH

The wrapper writes durable run context under STATE_ROOT. Subsequent commands
need only that context file. It never stages, commits, pushes, creates a pull
request, merges, or deploys.
USAGE
}

[[ -x "$PYTHON" ]] || fail "virtual-environment Python not found: $PYTHON"
command -v git >/dev/null 2>&1 || fail "git is not available"

COMMAND="${1:-}"
[[ -n "$COMMAND" ]] || { usage; exit 1; }
shift

json_get() {
  local file="$1"
  local key="$2"
  "$PYTHON" - "$file" "$key" <<'PY'
import json
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
value = payload
for part in sys.argv[2].split("."):
    if not isinstance(value, dict):
        value = None
        break
    value = value.get(part)
if value is None:
    print("")
elif isinstance(value, bool):
    print("true" if value else "false")
else:
    print(value)
PY
}

load_context() {
  local context_file="$1"
  [[ -f "$context_file" ]] || fail "context file not found: $context_file"
  CONTEXT_FILE="$(cd -- "$(dirname -- "$context_file")" && pwd)/$(basename -- "$context_file")"
  STATE_ROOT="$(json_get "$CONTEXT_FILE" state_root)"
  TASK_ID="$(json_get "$CONTEXT_FILE" task_id)"
  THREAD_ID="$(json_get "$CONTEXT_FILE" thread_id)"
  REPOSITORY="$(json_get "$CONTEXT_FILE" repository)"
  SCOPE_FILE="$(json_get "$CONTEXT_FILE" scope_file)"
  POLICY_FILE="$(json_get "$CONTEXT_FILE" policy_file)"
  HOST_CLIENT="$(json_get "$CONTEXT_FILE" host_client)"
  HOST_PYTHON="$(json_get "$CONTEXT_FILE" host_python)"
  PROVIDER_FACTORY="$(json_get "$CONTEXT_FILE" provider_factory)"
  EXPECTED_BASE_SHA="$(json_get "$CONTEXT_FILE" base_sha)"
  EXPECTED_PLAN_HASH="$(json_get "$CONTEXT_FILE" plan_hash)"
  EXPECTED_SCOPE_HASH="$(json_get "$CONTEXT_FILE" scope_hash)"

  [[ -n "$STATE_ROOT" ]] || fail "context missing state_root"
  [[ -n "$TASK_ID" ]] || fail "context missing task_id"
  [[ -n "$THREAD_ID" ]] || fail "context missing thread_id"
  [[ -n "$REPOSITORY" ]] || fail "context missing repository"
  [[ -n "$SCOPE_FILE" ]] || fail "context missing scope_file"
  [[ -n "$PROVIDER_FACTORY" ]] || PROVIDER_FACTORY="$DEFAULT_PROVIDER_FACTORY"

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
}

print_terminal_report() {
  local state_root="$1"
  local task_id="$2"
  local source_preserved="${3:-UNKNOWN}"
  export UCA_SAFE_WORKFLOW_STATE_ROOT="$state_root"
  export UCA_SAFE_WORKFLOW_TASK_ID="$task_id"
  export UCA_SAFE_WORKFLOW_SOURCE_PRESERVED="$source_preserved"
  "$PYTHON" - <<'PY'
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

state_root = Path(os.environ["UCA_SAFE_WORKFLOW_STATE_ROOT"])
task_id = os.environ["UCA_SAFE_WORKFLOW_TASK_ID"]
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
edit_validation = load("edit-validation.json")
edit_apply = load("edit-apply.json")
validation = load("patch-validation.json")
tests = load("test-results.json")
review = load("safe-review.json")

print()
print("============================================================")
print("SAFE MODE WORKFLOW — CURRENT / FINAL RESULT")
print("============================================================")
print("FINAL_STATUS=" + str(report.get("status")))
print("REVIEWER_VERDICT=" + str(report.get("reviewer_verdict")))
print("SAFE_ERRORS=" + json.dumps(report.get("safe_errors", [])))
print("SCOPE_APPROVED=" + str(report.get("scope_approved")))
print("STRUCTURED_EDIT_PROTOCOL=" + str(report.get("structured_edit_protocol")))
print("MODEL_AUTHORED_PATCH=" + str(report.get("model_authored_patch")))
print("CANONICAL_PATCH_GENERATED_BY=" + str(report.get("canonical_patch_generated_by")))
print("ROLLED_BACK=" + str(report.get("rolled_back")))
print("SANDBOX_PATCH_RETAINED=" + str(report.get("sandbox_patch_retained")))
print("IMPLEMENTER_ACTUAL_MODEL=" + str(model(implementer)))
print("IMPLEMENTER_SCHEMA_REPAIR_USED=" + str(implementer.get("repair_used")))
print("EDIT_VALID=" + str(edit_validation.get("valid")))
print("EDIT_CHANGED_PATHS=" + json.dumps(edit_validation.get("changed_paths", [])))
print("EDIT_ERRORS=" + json.dumps(edit_validation.get("errors", [])))
print("EDIT_APPLIED_PATHS=" + json.dumps(edit_apply.get("changed_paths", [])))
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
print("SOURCE_REPOSITORY_PRESERVED=" + os.environ["UCA_SAFE_WORKFLOW_SOURCE_PRESERVED"])
print("SANDBOX_STATUS:")
lines = status_lines(sandbox)
for line in lines:
    print("- " + line)
if not lines:
    print("- CLEAN")
print("FINAL_REPORT=" + str(task_root / "safe-final-report.json"))
print("EDIT_PROPOSAL=" + str(task_root / "edit-proposal.json"))
print("EDIT_VALIDATION=" + str(task_root / "edit-validation.json"))
print("EDIT_APPLY=" + str(task_root / "edit-apply.json"))
print("PATCH=" + str(task_root / "proposed.patch"))
print("PATCH_VALIDATION=" + str(task_root / "patch-validation.json"))
print("TEST_RESULTS_FILE=" + str(task_root / "test-results.json"))
print("REVIEW_FILE=" + str(task_root / "safe-review.json"))
print("SANDBOX=" + str(sandbox))
print("STATE_ROOT=" + str(state_root))
print("============================================================")
PY
}

case "$COMMAND" in
  start)
    STATE_ROOT=""
    REPOSITORY=""
    REF=""
    TASK_FILE=""
    SCOPE_FILE=""
    POLICY_FILE=""
    HOST_CLIENT=""
    HOST_PYTHON=""
    PROVIDER_FACTORY="$DEFAULT_PROVIDER_FACTORY"
    TITLE="Safe Mode task"
    TASK_ID=""
    THREAD_ID=""

    while (($#)); do
      case "$1" in
        --state-root) STATE_ROOT="$2"; shift 2 ;;
        --repository) REPOSITORY="$2"; shift 2 ;;
        --ref) REF="$2"; shift 2 ;;
        --task-file) TASK_FILE="$2"; shift 2 ;;
        --scope-file) SCOPE_FILE="$2"; shift 2 ;;
        --policy-file) POLICY_FILE="$2"; shift 2 ;;
        --host-client) HOST_CLIENT="$2"; shift 2 ;;
        --host-python) HOST_PYTHON="$2"; shift 2 ;;
        --provider-factory) PROVIDER_FACTORY="$2"; shift 2 ;;
        --title) TITLE="$2"; shift 2 ;;
        --task-id) TASK_ID="$2"; shift 2 ;;
        --thread-id) THREAD_ID="$2"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        *) fail "unknown start option: $1" ;;
      esac
    done

    [[ -n "$STATE_ROOT" ]] || fail "start requires --state-root"
    [[ -n "$REPOSITORY" ]] || fail "start requires --repository"
    [[ -n "$REF" ]] || fail "start requires --ref"
    [[ -f "$TASK_FILE" ]] || fail "task file not found: $TASK_FILE"
    [[ -f "$SCOPE_FILE" ]] || fail "scope file not found: $SCOPE_FILE"
    [[ -f "$POLICY_FILE" ]] || fail "policy file not found: $POLICY_FILE"

    mkdir -p "$STATE_ROOT"
    STATE_ROOT="$(cd -- "$STATE_ROOT" && pwd)"
    TASK_FILE="$(cd -- "$(dirname -- "$TASK_FILE")" && pwd)/$(basename -- "$TASK_FILE")"
    SCOPE_FILE="$(cd -- "$(dirname -- "$SCOPE_FILE")" && pwd)/$(basename -- "$SCOPE_FILE")"
    POLICY_FILE="$(cd -- "$(dirname -- "$POLICY_FILE")" && pwd)/$(basename -- "$POLICY_FILE")"

    if [[ -n "$HOST_CLIENT" ]]; then
      [[ -f "$HOST_CLIENT" ]] || fail "host client not found: $HOST_CLIENT"
      export UCA_HOST_CLIENT_PATH="$HOST_CLIENT"
    fi
    if [[ -n "$HOST_PYTHON" ]]; then
      [[ -x "$HOST_PYTHON" ]] || fail "host Python not executable: $HOST_PYTHON"
      export UCA_HOST_PYTHON="$HOST_PYTHON"
    fi

    if [[ -z "$TASK_ID" ]]; then
      TASK_ID="safe-$(date -u +%Y%m%dT%H%M%SZ)-$$-task"
    fi
    if [[ -z "$THREAD_ID" ]]; then
      THREAD_ID="${TASK_ID%-task}-thread"
    fi

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
      > "$STATE_ROOT/safe-start.json"

    "${CLI[@]}" safe-status --thread-id "$THREAD_ID" > "$STATE_ROOT/safe-status.json"

    export UCA_SAFE_WORKFLOW_STATUS_FILE="$STATE_ROOT/safe-status.json"
    export UCA_SAFE_WORKFLOW_CONTEXT_FILE="$STATE_ROOT/safe-workflow-context.json"
    export UCA_SAFE_WORKFLOW_STATE_ROOT="$STATE_ROOT"
    export UCA_SAFE_WORKFLOW_TASK_ID="$TASK_ID"
    export UCA_SAFE_WORKFLOW_THREAD_ID="$THREAD_ID"
    export UCA_SAFE_WORKFLOW_REPOSITORY="$REPOSITORY"
    export UCA_SAFE_WORKFLOW_REF="$REF"
    export UCA_SAFE_WORKFLOW_SCOPE_FILE="$SCOPE_FILE"
    export UCA_SAFE_WORKFLOW_POLICY_FILE="$POLICY_FILE"
    export UCA_SAFE_WORKFLOW_HOST_CLIENT="$HOST_CLIENT"
    export UCA_SAFE_WORKFLOW_HOST_PYTHON="$HOST_PYTHON"
    export UCA_SAFE_WORKFLOW_PROVIDER_FACTORY="$PROVIDER_FACTORY"

    "$PYTHON" - <<'PY'
from __future__ import annotations

import json
import os
from pathlib import Path

status_path = Path(os.environ["UCA_SAFE_WORKFLOW_STATUS_FILE"])
context_path = Path(os.environ["UCA_SAFE_WORKFLOW_CONTEXT_FILE"])
payload = json.loads(status_path.read_text(encoding="utf-8"))
values = payload.get("values", {})
next_nodes = payload.get("next", [])
manifest = values.get("task", {}).get("manifest", {})

if values.get("status") != "awaiting_scope_approval":
    raise SystemExit("SAFE_STATUS_NOT_AWAITING_SCOPE_APPROVAL=" + repr(values.get("status")))
if next_nodes != ["scope_approval"]:
    raise SystemExit("SAFE_SCOPE_APPROVAL_INTERRUPT_NOT_REACHED=" + repr(next_nodes))
if values.get("edit_proposal_ref") or values.get("patch_proposal_ref"):
    raise SystemExit("IMPLEMENTATION_ARTIFACT_ALREADY_GENERATED_UNEXPECTEDLY")

context = {
    "state_root": os.environ["UCA_SAFE_WORKFLOW_STATE_ROOT"],
    "task_id": os.environ["UCA_SAFE_WORKFLOW_TASK_ID"],
    "thread_id": os.environ["UCA_SAFE_WORKFLOW_THREAD_ID"],
    "repository": os.environ["UCA_SAFE_WORKFLOW_REPOSITORY"],
    "ref": os.environ["UCA_SAFE_WORKFLOW_REF"],
    "scope_file": os.environ["UCA_SAFE_WORKFLOW_SCOPE_FILE"],
    "policy_file": os.environ["UCA_SAFE_WORKFLOW_POLICY_FILE"],
    "host_client": os.environ["UCA_SAFE_WORKFLOW_HOST_CLIENT"],
    "host_python": os.environ["UCA_SAFE_WORKFLOW_HOST_PYTHON"],
    "provider_factory": os.environ["UCA_SAFE_WORKFLOW_PROVIDER_FACTORY"],
    "base_sha": manifest.get("base_sha"),
    "plan_hash": manifest.get("plan_hash"),
    "scope_hash": values.get("scope_hash"),
}
context_path.write_text(json.dumps(context, indent=2) + "\n", encoding="utf-8")

print()
print("============================================================")
print("SAFE WORKFLOW — APPROVAL READY")
print("============================================================")
print("STATUS=" + str(values.get("status")))
print("NEXT=" + repr(next_nodes))
print("STATE_ROOT=" + context["state_root"])
print("TASK_ID=" + context["task_id"])
print("THREAD_ID=" + context["thread_id"])
print("BASE_SHA=" + str(context["base_sha"]))
print("PLAN_HASH=" + str(context["plan_hash"]))
print("SCOPE_HASH=" + str(context["scope_hash"]))
print("CONTEXT_FILE=" + str(context_path))
print("ALLOWED_CHANGES:")
for item in manifest.get("allowed_changes", []):
    print("- {} {}".format(str(item.get("operation")).upper(), item.get("path")))
print("TEST_PROFILES:")
for profile in manifest.get("test_profiles", []):
    print("- " + str(profile))
print("NO EDITS OR PATCH HAVE BEEN GENERATED OR APPLIED.")
print("NO IMPLEMENTER HAS RUN YET.")
print("============================================================")
print()
print("NEXT_COMMAND=bash scripts/safe-workflow.sh approve --context-file " + str(context_path))
PY
    ;;

  status|approve|reject)
    CONTEXT_FILE=""
    while (($#)); do
      case "$1" in
        --context-file) CONTEXT_FILE="$2"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        *) fail "unknown $COMMAND option: $1" ;;
      esac
    done
    [[ -n "$CONTEXT_FILE" ]] || fail "$COMMAND requires --context-file"
    load_context "$CONTEXT_FILE"

    STATUS_FILE="$STATE_ROOT/safe-workflow-current-status.json"
    "${CLI[@]}" safe-status --thread-id "$THREAD_ID" > "$STATUS_FILE"
    CURRENT_STATUS="$(json_get "$STATUS_FILE" values.status)"

    if [[ "$COMMAND" == "status" ]]; then
      if [[ "$CURRENT_STATUS" == "awaiting_scope_approval" ]]; then
        printf 'SAFE_WORKFLOW_STATUS=awaiting_scope_approval\n'
        printf 'CONTEXT_FILE=%s\n' "$CONTEXT_FILE"
        printf 'BASE_SHA=%s\n' "$EXPECTED_BASE_SHA"
        printf 'PLAN_HASH=%s\n' "$EXPECTED_PLAN_HASH"
        printf 'SCOPE_HASH=%s\n' "$EXPECTED_SCOPE_HASH"
        exit 0
      fi
      printf 'SAFE_WORKFLOW_STATUS=%s\n' "$CURRENT_STATUS"
      print_terminal_report "$STATE_ROOT" "$TASK_ID" "UNKNOWN"
      exit 0
    fi

    if [[ "$CURRENT_STATUS" != "awaiting_scope_approval" ]]; then
      printf 'SAFE_WORKFLOW_ALREADY_TERMINAL_OR_ADVANCED=%s\n' "$CURRENT_STATUS"
      print_terminal_report "$STATE_ROOT" "$TASK_ID" "UNKNOWN"
      exit 0
    fi

    export UCA_SAFE_WORKFLOW_STATUS_FILE="$STATUS_FILE"
    export UCA_SAFE_WORKFLOW_SCOPE_FILE="$SCOPE_FILE"
    export UCA_SAFE_WORKFLOW_EXPECTED_BASE_SHA="$EXPECTED_BASE_SHA"
    export UCA_SAFE_WORKFLOW_EXPECTED_PLAN_HASH="$EXPECTED_PLAN_HASH"
    export UCA_SAFE_WORKFLOW_EXPECTED_SCOPE_HASH="$EXPECTED_SCOPE_HASH"

    "$PYTHON" - <<'PY'
from __future__ import annotations

import json
import os
from pathlib import Path

from universal_coding_agent.core.safe_models import ApprovedChangeManifest

status = json.loads(Path(os.environ["UCA_SAFE_WORKFLOW_STATUS_FILE"]).read_text(encoding="utf-8"))
raw_scope = json.loads(Path(os.environ["UCA_SAFE_WORKFLOW_SCOPE_FILE"]).read_text(encoding="utf-8"))
values = status.get("values", {})
manifest = values.get("task", {}).get("manifest", {})

if values.get("status") != "awaiting_scope_approval":
    raise SystemExit("SAFE_STATUS_NOT_AWAITING_SCOPE_APPROVAL")
if status.get("next") != ["scope_approval"]:
    raise SystemExit("SAFE_SCOPE_APPROVAL_INTERRUPT_NOT_REACHED")
if values.get("edit_proposal_ref") or values.get("patch_proposal_ref"):
    raise SystemExit("IMPLEMENTATION_ARTIFACT_ALREADY_GENERATED_UNEXPECTEDLY")
if manifest.get("base_sha") != os.environ["UCA_SAFE_WORKFLOW_EXPECTED_BASE_SHA"]:
    raise SystemExit("BASE_SHA_MISMATCH")
if manifest.get("plan_hash") != os.environ["UCA_SAFE_WORKFLOW_EXPECTED_PLAN_HASH"]:
    raise SystemExit("PLAN_HASH_MISMATCH")
if values.get("scope_hash") != os.environ["UCA_SAFE_WORKFLOW_EXPECTED_SCOPE_HASH"]:
    raise SystemExit("SCOPE_HASH_MISMATCH")

normalized_scope = ApprovedChangeManifest.model_validate(raw_scope).model_dump(mode="json")
if manifest != normalized_scope:
    differing = sorted(
        key
        for key in set(manifest) | set(normalized_scope)
        if manifest.get(key) != normalized_scope.get(key)
    )
    raise SystemExit("SCOPE_FILE_STATE_MISMATCH=" + ",".join(differing))

print("SAFE_WORKFLOW_APPROVAL_PREFLIGHT_PASS")
PY

    SOURCE_PRESERVED="NOT_APPLICABLE"
    SOURCE_IS_LOCAL=0
    if [[ -d "$REPOSITORY/.git" || -f "$REPOSITORY/.git" ]]; then
      SOURCE_IS_LOCAL=1
      git -C "$REPOSITORY" rev-parse HEAD > "$STATE_ROOT/source-head-before-decision.txt"
      git -C "$REPOSITORY" rev-parse --abbrev-ref HEAD > "$STATE_ROOT/source-branch-before-decision.txt"
      git -C "$REPOSITORY" status --porcelain=v1 -uall > "$STATE_ROOT/source-status-before-decision.txt"
      git -C "$REPOSITORY" worktree list --porcelain > "$STATE_ROOT/source-worktrees-before-decision.txt"
    fi

    DECISION="approve"
    [[ "$COMMAND" == "reject" ]] && DECISION="reject"
    printf 'HUMAN_DECISION=%s\n' "$DECISION"

    "${CLI[@]}" safe-resume \
      --thread-id "$THREAD_ID" \
      --decision "$DECISION" \
      > "$STATE_ROOT/safe-workflow-resume-result.json"

    if ((SOURCE_IS_LOCAL)); then
      git -C "$REPOSITORY" rev-parse HEAD > "$STATE_ROOT/source-head-after-decision.txt"
      git -C "$REPOSITORY" rev-parse --abbrev-ref HEAD > "$STATE_ROOT/source-branch-after-decision.txt"
      git -C "$REPOSITORY" status --porcelain=v1 -uall > "$STATE_ROOT/source-status-after-decision.txt"
      git -C "$REPOSITORY" worktree list --porcelain > "$STATE_ROOT/source-worktrees-after-decision.txt"

      SOURCE_PRESERVED="YES"
      for field in head branch status worktrees; do
        if ! cmp -s \
          "$STATE_ROOT/source-${field}-before-decision.txt" \
          "$STATE_ROOT/source-${field}-after-decision.txt"; then
          SOURCE_PRESERVED="NO"
        fi
      done
    fi

    print_terminal_report "$STATE_ROOT" "$TASK_ID" "$SOURCE_PRESERVED"
    [[ "$SOURCE_PRESERVED" != "NO" ]] || fail "source repository changed during Safe Mode decision"
    ;;

  -h|--help|help)
    usage
    ;;

  *)
    fail "unknown command: $COMMAND"
    ;;
esac
