set -Eeuo pipefail

cd /home/tag5916/projects/universal-coding-agent/universal-coding-agent

STATE_ROOT="/home/tag5916/.uca-safe-runs/phase2c-safe-v2-20260818T134704Z-369751"
TASK_ID="phase2c-safe-v2-20260818T134704Z-369751-task"
THREAD_ID="phase2c-safe-v2-20260818T134704Z-369751-thread"

HOST_CLIENT="/app1/tag5916/projects/kmai-td-genie/.kmai-dev-agent/kmai_client.py"
HOST_PYTHON="/app1/tag5916/projects/kmai-td-genie/.venv/bin/python"

EXPECTED_BASE_SHA="effd7ba7306021aa3561f2dcf3908a035511fd57"
EXPECTED_PLAN_HASH="e63f879d68804971a0f778b27d61c2352bf762ad0da7df8de751c9ea438a2da9"
EXPECTED_SCOPE_HASH="10dbb2e06da388df9f484f11b7c483f393903ad0f407d7bf78cee113a72de4715"

PRE_STATUS="$STATE_ROOT/pre-approval-status.json"
APPROVAL_RESULT="$STATE_ROOT/approval-result.json"
POST_STATUS="$STATE_ROOT/post-approval-status.json"

export UCA_HOST_CLIENT_PATH="$HOST_CLIENT"
export UCA_HOST_PYTHON="$HOST_PYTHON"

PROVIDER_FACTORY="universal_coding_agent.providers.host_subprocess:create_provider"

CLI=(
  .venv/bin/python
  -m universal_coding_agent.cli
  --state-root "$STATE_ROOT"
  --provider-factory "$PROVIDER_FACTORY"
  --allow-local-sources
)

# ------------------------------------------------------------
# 1. Final deterministic check BEFORE approval
# ------------------------------------------------------------

"${CLI[@]}" safe-status \
  --thread-id "$THREAD_ID" \
  > "$PRE_STATUS"

.venv/bin/python - \
  "$PRE_STATUS" \
  "$EXPECTED_BASE_SHA" \
  "$EXPECTED_PLAN_HASH" \
  "$EXPECTED_SCOPE_HASH" <<'PY'
from __future__ import annotations

import json
import sys
from pathlib import Path

status_file = Path(sys.argv[1])
expected_base = sys.argv[2]
expected_plan = sys.argv[3]
expected_scope = sys.argv[4]

payload = json.loads(status_file.read_text(encoding="utf-8"))

values = payload.get("values", {})
task = values.get("task", {})
manifest = task.get("manifest", {})
next_nodes = payload.get("next", [])

expected_changes = [
    (
        "modify",
        "kmai-td-genie/test/test_registry_contract.py",
    ),
    (
        "modify",
        "kmai-td-genie/test/test_registry_cache.py",
    ),
    (
        "modify",
        "kmai-td-genie/docs/adr/"
        "0002-phase2c-governed-semantic-plan-validator.md",
    ),
]

actual_changes = [
    (
        str(item.get("operation")),
        str(item.get("path")),
    )
    for item in manifest.get("allowed_changes", [])
]

if values.get("status") != "awaiting_scope_approval":
    raise SystemExit(
        "PRE_APPROVAL_STATUS_INVALID="
        + repr(values.get("status"))
    )

if next_nodes != ["scope_approval"]:
    raise SystemExit(
        "PRE_APPROVAL_NEXT_INVALID="
        + repr(next_nodes)
    )

if manifest.get("base_sha") != expected_base:
    raise SystemExit("BASE_SHA_CHANGED")

if manifest.get("plan_hash") != expected_plan:
    raise SystemExit("PLAN_HASH_CHANGED")

if values.get("scope_hash") != expected_scope:
    raise SystemExit("SCOPE_HASH_CHANGED")

if actual_changes != expected_changes:
    raise SystemExit(
        "SCOPE_CHANGED="
        + repr(actual_changes)
    )

if manifest.get("test_profiles") != [
    "phase2c-contract-tests"
]:
    raise SystemExit("TEST_PROFILE_CHANGED")

if values.get("patch_proposal_ref"):
    raise SystemExit(
        "PATCH_ALREADY_EXISTS_BEFORE_APPROVAL"
    )

print("PHASE2C_FINAL_PRE_APPROVAL_CHECK_PASS")
print("BASE_SHA=" + expected_base)
print("PLAN_HASH=" + expected_plan)
print("SCOPE_HASH=" + expected_scope)

print("APPROVED_CHANGES:")
for operation, path in actual_changes:
    print("- " + operation.upper() + " " + path)
PY

# ------------------------------------------------------------
# 2. HUMAN APPROVAL
# From this point the Implementer may generate a patch,
# but only inside the isolated Sandbox.
# ------------------------------------------------------------

echo
echo "PHASE2C_SCOPE_APPROVED"
echo "STARTING_SAFE_MODE_IMPLEMENTATION..."

"${CLI[@]}" safe-resume \
  --thread-id "$THREAD_ID" \
  --decision approve \
  > "$APPROVAL_RESULT"

# ------------------------------------------------------------
# 3. Read final state
# ------------------------------------------------------------

"${CLI[@]}" safe-status \
  --thread-id "$THREAD_ID" \
  > "$POST_STATUS"

# ------------------------------------------------------------
# 4. Print concise final result
# ------------------------------------------------------------

.venv/bin/python - \
  "$POST_STATUS" \
  "$STATE_ROOT" \
  "$TASK_ID" <<'PY'
from __future__ import annotations

import json
import sys
from pathlib import Path

status_file = Path(sys.argv[1])
state_root = Path(sys.argv[2])
task_id = sys.argv[3]

payload = json.loads(
    status_file.read_text(encoding="utf-8")
)

values = payload.get("values", {})
next_nodes = payload.get("next", [])

print()
print("=" * 70)
print("PHASE2C SAFE MODE RESULT")
print("=" * 70)

print(
    "FINAL_STATUS="
    + str(values.get("status"))
)
print(
    "REVIEWER_VERDICT="
    + str(values.get("reviewer_verdict"))
)
print(
    "PATCH_APPLIED="
    + str(values.get("patch_applied"))
)
print(
    "ROLLED_BACK="
    + str(values.get("rolled_back"))
)
print(
    "SAFE_ERRORS="
    + json.dumps(
        values.get("safe_errors", [])
    )
)
print(
    "NEXT="
    + repr(next_nodes)
)

refs = [
    ("IMPLEMENTER_VALIDATION", "implementer_validation_ref"),
    ("PATCH_PROPOSAL", "patch_proposal_ref"),
    ("PATCH", "patch_ref"),
    ("PATCH_VALIDATION", "patch_validation_ref"),
    ("PATCH_APPLY", "patch_apply_ref"),
    ("TEST_RESULTS", "tests_ref"),
    ("REVIEW", "review_ref"),
    ("ROLLBACK", "rollback_ref"),
    ("FINAL_REPORT", "final_report_ref"),
]

print()
print("ARTIFACTS:")

for label, field in refs:
    value = values.get(field)
    if value:
        print(f"{label}={value}")

task_root = (
    state_root
    / "artifacts"
    / "tasks"
    / task_id
)

print()
print("TASK_ARTIFACT_DIR=" + str(task_root))

print("=" * 70)

status = values.get("status")
verdict = values.get("reviewer_verdict")
errors = values.get("safe_errors", [])

if (
    status == "completed"
    and verdict == "PASS"
    and not errors
    and values.get("patch_applied") is True
    and values.get("rolled_back") is not True
):
    print("PHASE2C_FIRST_REAL_SAFE_SLICE_PASS")
else:
    print("PHASE2C_FIRST_REAL_SAFE_SLICE_NOT_ACCEPTED")
    print(
        "Do not manually modify the Sandbox or source repository."
    )
    print(
        "Use the generated artifacts for the next diagnosis."
    )
PY
