#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_PATH="${UCA_VENV_PATH:-$PROJECT_ROOT/.venv}"
STATE_ROOT="${UCA_SAFE_SMOKE_STATE_ROOT:-}"
SKIP_INSTALL=0

usage() {
  cat <<'USAGE'
Usage: bash scripts/safe-smoke.sh [--state-root PATH] [--skip-install]

Builds a local Git fixture, pauses for Safe Mode scope approval, resumes in a
separate CLI invocation, applies one approved patch in a sandbox, runs one fixed
test profile, performs independent review, and verifies that the source repository
was untouched. No stage, commit, push, pull request, merge, or deploy occurs.
USAGE
}

fail() {
  printf 'UCA_SAFE_SMOKE_FAIL: %s\n' "$*" >&2
  exit 1
}

while (($#)); do
  case "$1" in
    --state-root)
      (($# >= 2)) || fail "--state-root requires a value"
      STATE_ROOT="$2"
      shift 2
      ;;
    --skip-install)
      SKIP_INSTALL=1
      shift
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

command -v git >/dev/null 2>&1 || fail "git is not available"
command -v "$PYTHON_BIN" >/dev/null 2>&1 || fail "$PYTHON_BIN is not available"

if [[ -z "$STATE_ROOT" ]]; then
  STATE_ROOT="${RUNNER_TEMP:-${TMPDIR:-/tmp}}/uca-safe-smoke-$$"
fi
mkdir -p "$STATE_ROOT"
STATE_ROOT="$(cd -- "$STATE_ROOT" && pwd)"
SOURCE="$STATE_ROOT/source"
TASK_FILE="$STATE_ROOT/task.md"
SCOPE_FILE="$STATE_ROOT/scope.json"
POLICY_FILE="$STATE_ROOT/policy.json"
TASK_ID="safe-smoke-task"
THREAD_ID="safe-smoke-thread"

if [[ ! -x "$VENV_PATH/bin/python" ]]; then
  ((SKIP_INSTALL == 0)) || fail "virtual environment is missing"
  "$PYTHON_BIN" -m venv "$VENV_PATH"
fi
PYTHON="$VENV_PATH/bin/python"
if ! "$PYTHON" -c 'import universal_coding_agent' >/dev/null 2>&1; then
  ((SKIP_INSTALL == 0)) || fail "Universal Agent is not installed"
  "$PYTHON" -m pip install -e "$PROJECT_ROOT"
fi

rm -rf "$SOURCE"
mkdir -p "$SOURCE"
git -C "$SOURCE" init -b main >/dev/null
git -C "$SOURCE" config user.email test@example.test
git -C "$SOURCE" config user.name Test
printf 'def answer():\n    return 42\n' > "$SOURCE/app.py"
git -C "$SOURCE" add app.py
git -C "$SOURCE" commit -m fixture >/dev/null
BASE_SHA="$(git -C "$SOURCE" rev-parse HEAD)"
SOURCE_STATUS_BEFORE="$(git -C "$SOURCE" status --porcelain=v1 -uall)"
SOURCE_COUNT_BEFORE="$(git -C "$SOURCE" rev-list --count HEAD)"

cat > "$TASK_FILE" <<'EOF'
# Objective

Change the approved fixture answer from 42 to 43.

# Constraints

- Modify only app.py.
- Use only the approved patch operation.
- Run only the approved fixed test profile.
- Do not stage, commit, push, create a pull request, merge, or deploy.
EOF

"$PYTHON" - "$SCOPE_FILE" "$POLICY_FILE" "$BASE_SHA" "$PYTHON" <<'PY'
import json
import sys
from pathlib import Path

scope_path = Path(sys.argv[1])
policy_path = Path(sys.argv[2])
base_sha = sys.argv[3]
python = sys.argv[4]

scope = {
    "manifest_version": "1",
    "base_sha": base_sha,
    "plan_hash": "b" * 64,
    "allowed_changes": [
        {
            "path": "app.py",
            "operation": "modify",
            "purpose": "Apply the approved fixture change.",
        }
    ],
    "test_profiles": ["python-check"],
    "acceptance_criteria": ["app.py returns 43 and the focused check passes."],
}
policy = {
    "policy_version": "1",
    "profiles": [
        {
            "profile_id": "python-check",
            "argv": [
                python,
                "-c",
                (
                    "from pathlib import Path; "
                    "assert 'return 43' in Path('app.py').read_text()"
                ),
            ],
            "cwd": ".",
            "timeout_seconds": 60,
            "output_limit": 10000,
        }
    ],
}
scope_path.write_text(json.dumps(scope, indent=2), encoding="utf-8")
policy_path.write_text(json.dumps(policy, indent=2), encoding="utf-8")
PY

CLI=(
  "$PYTHON" -m universal_coding_agent.cli
  --state-root "$STATE_ROOT"
  --provider-factory universal_coding_agent.providers.fake:create_provider
  --allow-local-sources
)

"${CLI[@]}" safe \
  --repository "$SOURCE" \
  --ref main \
  --task-file "$TASK_FILE" \
  --scope-file "$SCOPE_FILE" \
  --policy-file "$POLICY_FILE" \
  --title "Safe Mode smoke qualification" \
  --task-id "$TASK_ID" \
  --thread-id "$THREAD_ID" \
  > "$STATE_ROOT/safe-start.json"

"${CLI[@]}" safe-status --thread-id "$THREAD_ID" > "$STATE_ROOT/safe-status.json"
"$PYTHON" - "$STATE_ROOT/safe-status.json" <<'PY'
import json
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
if payload.get("next") != ["scope_approval"]:
    raise SystemExit(f"UCA_SAFE_APPROVAL_INTERRUPT_INVALID:{payload.get('next')}")
if payload.get("values", {}).get("status") != "awaiting_scope_approval":
    raise SystemExit("UCA_SAFE_APPROVAL_STATUS_INVALID")
print("UCA_SAFE_APPROVAL_INTERRUPT_OK")
PY

"${CLI[@]}" safe-resume \
  --thread-id "$THREAD_ID" \
  --decision approve \
  > "$STATE_ROOT/safe-final.json"

"$PYTHON" - "$STATE_ROOT" "$SOURCE" "$TASK_ID" \
  "$SOURCE_STATUS_BEFORE" "$SOURCE_COUNT_BEFORE" <<'PY'
import json
import subprocess
import sys
from pathlib import Path

state_root = Path(sys.argv[1])
source = Path(sys.argv[2])
task_id = sys.argv[3]
source_status_before = sys.argv[4]
source_count_before = sys.argv[5]
report_path = state_root / "artifacts" / "tasks" / task_id / "safe-final-report.json"
report = json.loads(report_path.read_text(encoding="utf-8"))

assert report["status"] == "completed", report
assert report["reviewer_verdict"] == "PASS", report
assert report["sandbox_patch_retained"] is True, report
assert report["rolled_back"] is False, report
assert report["source_repository_modified"] is False, report
assert report["stage_commit_push_pr_merge_deploy"] is False, report
assert report["approved_changed_paths"] == ["app.py"], report

sandbox = state_root / "sandboxes" / task_id / "repo"
assert "return 43" in (sandbox / "app.py").read_text(encoding="utf-8")
assert "return 42" in (source / "app.py").read_text(encoding="utf-8")

source_status_after = subprocess.run(
    ["git", "-C", str(source), "status", "--porcelain=v1", "-uall"],
    check=True,
    capture_output=True,
    text=True,
).stdout.strip()
source_count_after = subprocess.run(
    ["git", "-C", str(source), "rev-list", "--count", "HEAD"],
    check=True,
    capture_output=True,
    text=True,
).stdout.strip()
sandbox_count = subprocess.run(
    ["git", "-C", str(sandbox), "rev-list", "--count", "HEAD"],
    check=True,
    capture_output=True,
    text=True,
).stdout.strip()

assert source_status_after == source_status_before
assert source_count_after == source_count_before
assert sandbox_count == source_count_before
print("UCA_SAFE_SMOKE_PASS")
print(f"SAFE_FINAL_REPORT={report_path}")
print(f"SAFE_SANDBOX={sandbox}")
PY
