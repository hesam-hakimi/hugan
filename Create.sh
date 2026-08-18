set -Eeuo pipefail

cd /home/tag5916/projects/universal-coding-agent/universal-coding-agent

STATE_ROOT="/home/tag5916/.uca-safe-runs/phase2c-safe-v2-20260818T134704Z-369751"
TASK_ID="phase2c-safe-v2-20260818T134704Z-369751-task"
THREAD_ID="phase2c-safe-v2-20260818T134704Z-369751-thread"

REPOSITORY="/app1/tag5916/projects/kmai-td-genie"

HOST_CLIENT="/app1/tag5916/projects/kmai-td-genie/.kmai-dev-agent/kmai_client.py"
HOST_PYTHON="/app1/tag5916/projects/kmai-td-genie/.venv/bin/python"

EXPECTED_BASE_SHA="effd7ba7306021aa3561f2dcf3908a035511fd57"
EXPECTED_PLAN_HASH="e63f879d68804971a0f778b27d61c2352bf762ad0da7df8de751c9ea438a2da9"
EXPECTED_SCOPE_HASH="10dbb2e06d388df9f484f11b7c483f939303ad0f407d7bf78cee113a72de4715"

export UCA_HOST_CLIENT_PATH="$HOST_CLIENT"
export UCA_HOST_PYTHON="$HOST_PYTHON"

PROVIDER_FACTORY="universal_coding_agent.providers.host_subprocess:create_provider"

# ------------------------------------------------------------
# 1. Re-check the frozen approval state
# ------------------------------------------------------------

.venv/bin/python -m universal_coding_agent.cli \
  --state-root "$STATE_ROOT" \
  --provider-factory "$PROVIDER_FACTORY" \
  --allow-local-sources \
  safe-status \
  --thread-id "$THREAD_ID" \
  > "$STATE_ROOT/pre-approval-status.json"

export PRE_APPROVAL_STATUS="$STATE_ROOT/pre-approval-status.json"
export EXPECTED_BASE_SHA
export EXPECTED_PLAN_HASH
export EXPECTED_SCOPE_HASH

.venv/bin/python - <<'PY'
import json
import os

with open(os.environ["PRE_APPROVAL_STATUS"], encoding="utf-8") as f:
    payload = json.load(f)

values = payload.get("values", {})
manifest = values.get("task", {}).get("manifest", {})
next_nodes = payload.get("next", [])

assert values.get("status") == "awaiting_scope_approval", values.get("status")
assert next_nodes == ["scope_approval"], next_nodes
assert manifest.get("base_sha") == os.environ["EXPECTED_BASE_SHA"]
assert manifest.get("plan_hash") == os.environ["EXPECTED_PLAN_HASH"]
assert values.get("scope_hash") == os.environ["EXPECTED_SCOPE_HASH"]
assert not values.get("patch_proposal_ref")

paths = [
    (str(x.get("operation")).lower(), x.get("path"))
    for x in manifest.get("allowed_changes", [])
]

expected = [
    ("modify", "kmai-td-genie/test/test_registry_contract.py"),
    ("modify", "kmai-td-genie/test/test_registry_cache.py"),
    (
        "modify",
        "kmai-td-genie/docs/adr/"
        "0002-phase2c-governed-semantic-plan-validator.md",
    ),
]

assert paths == expected, paths

print("PHASE2C_APPROVAL_PREFLIGHT_PASS")
print("BASE_SHA=" + manifest["base_sha"])
print("PLAN_HASH=" + manifest["plan_hash"])
print("SCOPE_HASH=" + values["scope_hash"])
PY

# ------------------------------------------------------------
# 2. Freeze SOURCE repository state before approval
# ------------------------------------------------------------

git -C "$REPOSITORY" rev-parse HEAD \
  > "$STATE_ROOT/source-head-before-approval.txt"

git -C "$REPOSITORY" rev-parse --abbrev-ref HEAD \
  > "$STATE_ROOT/source-branch-before-approval.txt"

git -C "$REPOSITORY" status --porcelain=v1 -uall \
  > "$STATE_ROOT/source-status-before-approval.txt"

git -C "$REPOSITORY" worktree list --porcelain \
  > "$STATE_ROOT/source-worktrees-before-approval.txt"

echo "SOURCE_BASELINE_CAPTURED"

# ------------------------------------------------------------
# 3. HUMAN APPROVAL — continue the frozen Safe Mode task
# ------------------------------------------------------------

echo "PHASE2C_SCOPE_APPROVED_BY_USER"

.venv/bin/python -m universal_coding_agent.cli \
  --state-root "$STATE_ROOT" \
  --provider-factory "$PROVIDER_FACTORY" \
  --allow-local-sources \
  safe-resume \
  --thread-id "$THREAD_ID" \
  --decision approve \
  > "$STATE_ROOT/approval-run-result.json"

# ------------------------------------------------------------
# 4. Capture SOURCE state after execution
# ------------------------------------------------------------

git -C "$REPOSITORY" rev-parse HEAD \
  > "$STATE_ROOT/source-head-after-approval.txt"

git -C "$REPOSITORY" rev-parse --abbrev-ref HEAD \
  > "$STATE_ROOT/source-branch-after-approval.txt"

git -C "$REPOSITORY" status --porcelain=v1 -uall \
  > "$STATE_ROOT/source-status-after-approval.txt"

git -C "$REPOSITORY" worktree list --porcelain \
  > "$STATE_ROOT/source-worktrees-after-approval.txt"

SOURCE_PRESERVED=YES

cmp -s \
  "$STATE_ROOT/source-head-before-approval.txt" \
  "$STATE_ROOT/source-head-after-approval.txt" \
  || SOURCE_PRESERVED=NO

cmp -s \
  "$STATE_ROOT/source-branch-before-approval.txt" \
  "$STATE_ROOT/source-branch-after-approval.txt" \
  || SOURCE_PRESERVED=NO

cmp -s \
  "$STATE_ROOT/source-status-before-approval.txt" \
  "$STATE_ROOT/source-status-after-approval.txt" \
  || SOURCE_PRESERVED=NO

cmp -s \
  "$STATE_ROOT/source-worktrees-before-approval.txt" \
  "$STATE_ROOT/source-worktrees-after-approval.txt" \
  || SOURCE_PRESERVED=NO

export SOURCE_PRESERVED
export STATE_ROOT
export TASK_ID

# ------------------------------------------------------------
# 5. Print one concise final decision report
# ------------------------------------------------------------

.venv/bin/python - <<'PY'
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

state_root = Path(os.environ["STATE_ROOT"])
task_id = os.environ["TASK_ID"]

task_root = state_root / "artifacts" / "tasks" / task_id
sandbox = state_root / "sandboxes" / task_id / "repo"

def load(name):
    path = task_root / name
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))

report = load("safe-final-report.json")
implementer = load("implementer-model-validation.json")
patch_validation = load("patch-validation.json")
tests = load("test-results.json")
review = load("safe-review.json")

def first_model(payload):
    attempts = payload.get("attempts", [])
    if not attempts:
        return None
    return attempts[-1].get("actual_model")

def git_status(path):
    if not path.is_dir():
        return ["SANDBOX_NOT_FOUND"]
    result = subprocess.run(
        ["git", "-C", str(path), "status", "--porcelain=v1", "-uall"],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.splitlines()

print()
print("============================================================")
print("PHASE2C FIRST REAL SAFE MODE — FINAL RESULT")
print("============================================================")

print("FINAL_STATUS=" + str(report.get("status")))
print("REVIEWER_VERDICT=" + str(report.get("reviewer_verdict")))
print("SAFE_ERRORS=" + json.dumps(report.get("safe_errors", [])))
print("SCOPE_APPROVED=" + str(report.get("scope_approved")))
print("ROLLED_BACK=" + str(report.get("rolled_back")))
print(
    "SANDBOX_PATCH_RETAINED="
    + str(report.get("sandbox_patch_retained"))
)

print()
print(
    "IMPLEMENTER_ACTUAL_MODEL="
    + str(first_model(implementer))
)
print(
    "IMPLEMENTER_SCHEMA_REPAIR_USED="
    + str(implementer.get("repair_used"))
)

print()
print(
    "PATCH_VALID="
    + str(patch_validation.get("valid"))
)
print(
    "PATCH_CHANGED_PATHS="
    + json.dumps(patch_validation.get("changed_paths", []))
)
print(
    "PATCH_ERRORS="
    + json.dumps(patch_validation.get("errors", []))
)

print()
print("TEST_RESULTS:")
for item in tests.get("results", []):
    print(
        "- "
        + str(item.get("profile_id"))
        + " passed="
        + str(item.get("passed"))
        + " returncode="
        + str(item.get("returncode"))
    )

print()
print(
    "REVIEW_CONFIDENCE="
    + str(review.get("confidence"))
)
print("REVIEW_REQUIRED_ACTIONS:")
for item in review.get("required_actions", []):
    print("- " + str(item))
if not review.get("required_actions"):
    print("- None")

print()
print(
    "SOURCE_REPOSITORY_PRESERVED="
    + os.environ["SOURCE_PRESERVED"]
)

print("SANDBOX_STATUS:")
status = git_status(sandbox)
if status:
    for line in status:
        print("- " + line)
else:
    print("- CLEAN")

print()
print("FINAL_REPORT=" + str(task_root / "safe-final-report.json"))
print("PATCH=" + str(task_root / "proposed.patch"))
print("TEST_RESULTS_FILE=" + str(task_root / "test-results.json"))
print("REVIEW_FILE=" + str(task_root / "safe-review.json"))
print("SANDBOX=" + str(sandbox))
print("============================================================")
PY

if [[ "$SOURCE_PRESERVED" != "YES" ]]; then
  echo "CRITICAL_SOURCE_PRESERVATION_FAILURE"
  exit 10
fi
