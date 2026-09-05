#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
VENV_PATH="${UCA_VENV_PATH:-$PROJECT_ROOT/.venv}"
PYTHON="$VENV_PATH/bin/python"

fail() {
  printf 'UCA_SAFE_PATCH_DIAGNOSE_FAIL: %s\n' "$*" >&2
  exit 1
}

usage() {
  cat <<'USAGE'
Usage:
  bash scripts/safe-patch-diagnose.sh \
    --state-root PATH \
    --task-id ID

Read-only diagnosis of a Safe Mode run that failed deterministic patch
validation. The script never applies the patch and never modifies the source
repository or sandbox.
USAGE
}

STATE_ROOT=""
TASK_ID=""

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

[[ -x "$PYTHON" ]] || fail "virtual-environment Python not found: $PYTHON"
command -v git >/dev/null 2>&1 || fail "git is not available"
[[ -n "$STATE_ROOT" ]] || fail "--state-root is required"
[[ -n "$TASK_ID" ]] || fail "--task-id is required"
[[ -d "$STATE_ROOT" ]] || fail "state root not found: $STATE_ROOT"

STATE_ROOT="$(cd -- "$STATE_ROOT" && pwd)"
TASK_ROOT="$STATE_ROOT/artifacts/tasks/$TASK_ID"
SANDBOX="$STATE_ROOT/sandboxes/$TASK_ID/repo"
PATCH="$TASK_ROOT/proposed.patch"
VALIDATION="$TASK_ROOT/patch-validation.json"
FINAL_REPORT="$TASK_ROOT/safe-final-report.json"
PROPOSAL="$TASK_ROOT/patch-proposal.json"

[[ -d "$TASK_ROOT" ]] || fail "task root not found: $TASK_ROOT"
[[ -d "$SANDBOX" ]] || fail "sandbox not found: $SANDBOX"
[[ -f "$PATCH" ]] || fail "proposed patch not found: $PATCH"

printf '%s\n' "============================================================"
printf '%s\n' "SAFE MODE PATCH — GIT APPLY DIAGNOSIS"
printf '%s\n' "============================================================"
printf 'STATE_ROOT=%s\n' "$STATE_ROOT"
printf 'TASK_ID=%s\n' "$TASK_ID"
printf 'TASK_ROOT=%s\n' "$TASK_ROOT"
printf 'SANDBOX=%s\n' "$SANDBOX"
printf 'PATCH=%s\n' "$PATCH"
printf '\n'

if [[ -f "$FINAL_REPORT" ]]; then
  "$PYTHON" - "$FINAL_REPORT" <<'PY'
import json
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print("FINAL_STATE:")
print("- status=" + str(payload.get("status")))
print("- reviewer_verdict=" + str(payload.get("reviewer_verdict")))
print("- safe_errors=" + json.dumps(payload.get("safe_errors", [])))
print("- rolled_back=" + str(payload.get("rolled_back")))
print("- source_repository_modified=" + str(payload.get("source_repository_modified")))
PY
fi

if [[ -f "$VALIDATION" ]]; then
  "$PYTHON" - "$VALIDATION" <<'PY'
import json
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print()
print("RECORDED_PATCH_VALIDATION:")
print("- valid=" + str(payload.get("valid")))
print("- changed_paths=" + json.dumps(payload.get("changed_paths", [])))
print("- errors=" + json.dumps(payload.get("errors", []), indent=2))
PY
fi

if [[ -f "$PROPOSAL" ]]; then
  "$PYTHON" - "$PROPOSAL" <<'PY'
import json
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print()
print("PROPOSAL_SUMMARY:")
print("- summary=" + str(payload.get("summary")))
print("- changed_paths=" + json.dumps(payload.get("changed_paths", [])))
print("- requested_test_profiles=" + json.dumps(payload.get("requested_test_profiles", [])))
PY
fi

printf '\n%s\n' "GIT_APPLY_CHECK_VERBOSE:"
set +e
GIT_OUTPUT="$(
  git -C "$SANDBOX" apply \
    --check \
    --verbose \
    --whitespace=error \
    --recount \
    "$PATCH" 2>&1
)"
GIT_RC=$?
set -e
printf 'returncode=%s\n' "$GIT_RC"
printf '%s\n' "$GIT_OUTPUT"

printf '\n%s\n' "SANDBOX_IDENTITY:"
printf 'HEAD=%s\n' "$(git -C "$SANDBOX" rev-parse HEAD)"
printf 'BRANCH=%s\n' "$(git -C "$SANDBOX" rev-parse --abbrev-ref HEAD)"
printf '%s\n' "STATUS:"
STATUS="$(git -C "$SANDBOX" status --porcelain=v1 -uall)"
if [[ -n "$STATUS" ]]; then
  printf '%s\n' "$STATUS"
else
  printf '%s\n' "CLEAN"
fi

printf '\n%s\n' "PATCH_SECTION_SUMMARY:"
"$PYTHON" - "$PATCH" "$SANDBOX" <<'PY'
from __future__ import annotations

import re
import sys
from pathlib import Path

patch = Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace")
sandbox = Path(sys.argv[2]).resolve()
headers = re.findall(r"^diff --git a/(\S+) b/(\S+)$", patch, flags=re.MULTILINE)
for index, (old_path, new_path) in enumerate(headers, start=1):
    target = (sandbox / new_path).resolve()
    exists = target.is_file() and not target.is_symlink()
    lines = 0
    if exists:
        lines = len(target.read_text(encoding="utf-8", errors="replace").splitlines())
    print(f"- section={index} old={old_path} new={new_path} target_exists={exists} target_lines={lines}")

for line in patch.splitlines():
    if line.startswith("@@ "):
        print("  hunk=" + line)
PY

printf '\n%s\n' "PROPOSED_PATCH_NUMBERED:"
nl -ba "$PATCH" | sed -n '1,320p'

printf '\n%s\n' "============================================================"
printf '%s\n' "UCA_SAFE_PATCH_DIAGNOSIS_COMPLETE"
printf 'GIT_APPLY_RETURNCODE=%s\n' "$GIT_RC"
printf '%s\n' "NO PATCH WAS APPLIED BY THIS DIAGNOSTIC."
printf '%s\n' "============================================================"

exit 0
