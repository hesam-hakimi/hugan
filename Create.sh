set -Eeuo pipefail

UCA_ROOT="/home/tag5916/projects/universal-coding-agent/universal-coding-agent"
REPOSITORY="/app1/tag5916/projects/kmai-td-genie"
REF="phase2/semantic-plan-contract-validator"

HOST_CLIENT="/app1/tag5916/projects/kmai-td-genie/.kmai-dev-agent/kmai_client.py"
HOST_PYTHON="/app1/tag5916/projects/kmai-td-genie/.venv/bin/python"

WORK_ROOT="/app1/tag5916/.uca-phase2c-safe-scope-v2"
TASK_FILE="$WORK_ROOT/phase2c-safe-task.md"
SCOPE_FILE="$WORK_ROOT/approved-scope.json"
POLICY_FILE="$WORK_ROOT/trusted-policy.json"

cd "$UCA_ROOT"

# ------------------------------------------------------------
# 1. Verify the three generated control files before doing anything
# ------------------------------------------------------------

.venv/bin/python - "$TASK_FILE" "$SCOPE_FILE" "$POLICY_FILE" "$REPOSITORY" "$REF" <<'PY'
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

task_file = Path(sys.argv[1])
scope_file = Path(sys.argv[2])
policy_file = Path(sys.argv[3])
repository = Path(sys.argv[4])
ref = sys.argv[5]

for path in (task_file, scope_file, policy_file):
    if not path.is_file():
        raise SystemExit(f"CONTROL_FILE_MISSING={path}")

scope = json.loads(scope_file.read_text(encoding="utf-8"))
policy = json.loads(policy_file.read_text(encoding="utf-8"))

expected = [
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

actual = [
    (item.get("operation"), item.get("path"))
    for item in scope.get("allowed_changes", [])
]

if actual != expected:
    raise SystemExit(
        "APPROVED_SCOPE_MISMATCH\n"
        f"EXPECTED={expected!r}\n"
        f"ACTUAL={actual!r}"
    )

if scope.get("max_changed_files") != 3:
    raise SystemExit(
        f"MAX_CHANGED_FILES_INVALID={scope.get('max_changed_files')}"
    )

if scope.get("test_profiles") != ["phase2c-contract-tests"]:
    raise SystemExit(
        f"TEST_PROFILE_INVALID={scope.get('test_profiles')}"
    )

profiles = {
    item.get("profile_id")
    for item in policy.get("profiles", [])
}

if "phase2c-contract-tests" not in profiles:
    raise SystemExit("TRUSTED_TEST_PROFILE_NOT_FOUND")

resolved = subprocess.run(
    [
        "git",
        "-C",
        str(repository),
        "rev-parse",
        f"{ref}^{{commit}}",
    ],
    check=True,
    capture_output=True,
    text=True,
).stdout.strip()

if resolved != scope.get("base_sha"):
    raise SystemExit(
        "BASE_SHA_MISMATCH\n"
        f"SCOPE={scope.get('base_sha')}\n"
        f"REF={resolved}"
    )

for operation, path in expected:
    exists = subprocess.run(
        [
            "git",
            "-C",
            str(repository),
            "cat-file",
            "-e",
            f"{resolved}:{path}",
        ],
        check=False,
        capture_output=True,
        text=True,
    ).returncode == 0

    if operation == "modify" and not exists:
        raise SystemExit(f"MODIFY_PATH_NOT_FOUND={path}")

print("PHASE2C_SAFE_CONTROL_FILES_OK")
print(f"BASE_SHA={scope['base_sha']}")
print(f"PLAN_HASH={scope['plan_hash']}")
print("APPROVED_CHANGES:")

for item in scope["allowed_changes"]:
    print(
        "- "
        + str(item["operation"]).upper()
        + " "
        + str(item["path"])
    )

print("TEST_PROFILES:")
for profile in scope["test_profiles"]:
    print("- " + profile)
PY

# ------------------------------------------------------------
# 2. Start a NEW Safe Mode run
# ------------------------------------------------------------

RUN_ID="phase2c-safe-v2-$(date -u +%Y%m%dT%H%M%SZ)-$$"
STATE_ROOT="$HOME/.uca-safe-runs/$RUN_ID"
TASK_ID="$RUN_ID-task"
THREAD_ID="$RUN_ID-thread"

mkdir -p "$STATE_ROOT"

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

"${CLI[@]}" safe \
  --repository "$REPOSITORY" \
  --ref "$REF" \
  --task-file "$TASK_FILE" \
  --scope-file "$SCOPE_FILE" \
  --policy-file "$POLICY_FILE" \
  --title "Phase 2C first real Safe Mode slice" \
  --task-id "$TASK_ID" \
  --thread-id "$THREAD_ID" \
  > "$WORK_ROOT/safe-start-v2.json"

"${CLI[@]}" safe-status \
  --thread-id "$THREAD_ID" \
  > "$WORK_ROOT/safe-status-v2.json"

# ------------------------------------------------------------
# 3. Verify that we stopped BEFORE the Implementer
# ------------------------------------------------------------

.venv/bin/python - "$WORK_ROOT/safe-status-v2.json" "$STATE_ROOT" "$TASK_ID" "$THREAD_ID" <<'PY'
from __future__ import annotations

import json
import sys
from pathlib import Path

status_file = Path(sys.argv[1])
state_root = sys.argv[2]
task_id = sys.argv[3]
thread_id = sys.argv[4]

payload = json.loads(
    status_file.read_text(encoding="utf-8")
)

values = payload.get("values", {})
next_nodes = payload.get("next", [])
task = values.get("task", {})
manifest = task.get("manifest", {})

if next_nodes != ["scope_approval"]:
    raise SystemExit(
        "SAFE_SCOPE_APPROVAL_INTERRUPT_NOT_REACHED="
        + repr(next_nodes)
    )

if values.get("status") != "awaiting_scope_approval":
    raise SystemExit(
        "SAFE_STATUS_INVALID="
        + repr(values.get("status"))
    )

if values.get("patch_proposal_ref"):
    raise SystemExit("PATCH_ALREADY_GENERATED_UNEXPECTEDLY")

print()
print("============================================================")
print("SAFE_SCOPE_APPROVAL_READY")
print("============================================================")

print("STATUS=" + str(values.get("status")))
print("NEXT=" + repr(next_nodes))
print("STATE_ROOT=" + state_root)
print("TASK_ID=" + task_id)
print("THREAD_ID=" + thread_id)
print("BASE_SHA=" + str(manifest.get("base_sha")))
print("PLAN_HASH=" + str(manifest.get("plan_hash")))
print("SCOPE_HASH=" + str(values.get("scope_hash")))

print()
print("ALLOWED_CHANGES:")

for item in manifest.get("allowed_changes", []):
    print(
        "- "
        + str(item.get("operation")).upper()
        + " "
        + str(item.get("path"))
    )

print()
print("TEST_PROFILES:")

for profile in manifest.get("test_profiles", []):
    print("- " + str(profile))

print()
print("NO PATCH HAS BEEN GENERATED OR APPLIED.")
print("NO IMPLEMENTER HAS RUN YET.")
print("SOURCE REPOSITORY HAS NOT BEEN MODIFIED.")
print("============================================================")
PY
