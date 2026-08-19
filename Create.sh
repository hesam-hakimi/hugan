set -Eeuo pipefail

cd /home/tag5916/projects/universal-coding-agent/universal-coding-agent

RUN_ROOT="/home/tag5916/.uca-safe-runs/phase2c-structured-testfix-v1-20260819T142102Z"
TASK_ID="safe-20260819T142102Z-2400636-task"
TASK_ROOT="$RUN_ROOT/artifacts/tasks/$TASK_ID"

export TASK_ROOT

.venv/bin/python - <<'PY'
import json
import os
from pathlib import Path

root = Path(os.environ["TASK_ROOT"])

def load(name):
    p = root / name
    if not p.is_file():
        return None
    return json.loads(p.read_text(encoding="utf-8"))

def show(name):
    print()
    print("=" * 78)
    print(name)
    print("=" * 78)

    value = load(name)
    if value is None:
        print("NOT_FOUND")
        return

    print(json.dumps(value, indent=2, ensure_ascii=False))

final_report = load("safe-final-report.json") or {}

print("=" * 78)
print("ANCHOR_REPAIR_DIAGNOSIS")
print("=" * 78)

for key in (
    "status",
    "safe_errors",
    "edit_repair_used",
    "initial_edit_proposal_ref",
    "initial_edit_validation_ref",
    "edit_repair_context_ref",
    "edit_repair_validation_ref",
    "edit_repair_proposal_ref",
    "edit_validation_ref",
    "edit_apply_ref",
):
    print(f"{key}={final_report.get(key)}")

for filename in (
    "edit-validation.json",
    "edit-repair-model-validation.json",
    "edit-proposal-repaired.json",
    "edit-validation-repaired.json",
):
    show(filename)

print()
print("=" * 78)
print("ANCHOR_REPAIR_DIAGNOSIS_COMPLETE")
print("=" * 78)
PY
