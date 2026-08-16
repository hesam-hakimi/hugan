#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_PATH="${UCA_VENV_PATH:-$PROJECT_ROOT/.venv}"
HOST_CLIENT="${UCA_HOST_CLIENT_PATH:-}"
STATE_ROOT=""
SKIP_INSTALL=0
SKIP_QUALITY=0

usage() {
  cat <<'USAGE'
Usage: bash scripts/qualify-host-provider.sh [options]

Options:
  --host-client PATH   Existing site-owned Python client module. Required unless
                       UCA_HOST_CLIENT_PATH is already set.
  --state-root PATH    Qualification state directory.
  --skip-install       Reuse the current environment; do not install the package.
  --skip-quality       Skip local compile/lint/test gates.
  -h, --help           Show this help.

The host module is expected to expose, by default:
  create_client()
  get_configured_model_or_deployment()

Symbol names can be overridden with:
  UCA_HOST_CLIENT_FACTORY
  UCA_HOST_MODEL_CONFIG_FACTORY
  UCA_HOST_DEPLOYMENT_ATTRIBUTE
USAGE
}

fail() {
  printf 'UCA_HOST_PROVIDER_QUALIFICATION_FAIL: %s\n' "$*" >&2
  exit 1
}

while (($#)); do
  case "$1" in
    --host-client)
      (($# >= 2)) || fail "--host-client requires a value"
      HOST_CLIENT="$2"
      shift 2
      ;;
    --state-root)
      (($# >= 2)) || fail "--state-root requires a value"
      STATE_ROOT="$2"
      shift 2
      ;;
    --skip-install)
      SKIP_INSTALL=1
      shift
      ;;
    --skip-quality)
      SKIP_QUALITY=1
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

[[ -n "$HOST_CLIENT" ]] || fail "set UCA_HOST_CLIENT_PATH or pass --host-client"
[[ -f "$HOST_CLIENT" ]] || fail "host client file does not exist: $HOST_CLIENT"
command -v git >/dev/null 2>&1 || fail "git is not available"
command -v "$PYTHON_BIN" >/dev/null 2>&1 || fail "$PYTHON_BIN is not available"
[[ -n "${HOME:-}" && -d "$HOME" && -w "$HOME" ]] || fail "HOME must be writable"

HOST_CLIENT="$(cd -- "$(dirname -- "$HOST_CLIENT")" && pwd)/$(basename -- "$HOST_CLIENT")"
RUN_ID="uca-host-$(date -u +%Y%m%dT%H%M%SZ)-$$"
if [[ -z "$STATE_ROOT" ]]; then
  STATE_ROOT="$HOME/.uca-host-runs/$RUN_ID"
fi
mkdir -p "$STATE_ROOT/tmp"
STATE_ROOT="$(cd -- "$STATE_ROOT" && pwd)"
export TMPDIR="$STATE_ROOT/tmp"
export PYTHONDONTWRITEBYTECODE=1
export PIP_DISABLE_PIP_VERSION_CHECK=1
export UCA_HOST_CLIENT_PATH="$HOST_CLIENT"
export UCA_MODEL_PROVIDER_FACTORY="universal_coding_agent.providers.host_chat:create_provider"

trap 'printf "UCA_HOST_PROVIDER_QUALIFICATION_FAIL: command failed at line %s\n" "$LINENO" >&2' ERR

"$PYTHON_BIN" - <<'PY'
import sys
if sys.version_info < (3, 11):
    raise SystemExit(f"Python 3.11+ required; found {sys.version.split()[0]}")
print(f"PYTHON_HOST_QUALIFICATION_OK={sys.version.split()[0]}")
PY

if ((SKIP_INSTALL == 0)); then
  if [[ ! -x "$VENV_PATH/bin/python" ]]; then
    "$PYTHON_BIN" -m venv "$VENV_PATH"
  fi
  PYTHON="$VENV_PATH/bin/python"
  "$PYTHON" -m pip install -e "$PROJECT_ROOT[dev]"
else
  if [[ -x "$VENV_PATH/bin/python" ]]; then
    PYTHON="$VENV_PATH/bin/python"
  else
    PYTHON="$PYTHON_BIN"
  fi
fi

"$PYTHON" -m pip check

if ((SKIP_QUALITY == 0)); then
  "$PYTHON" -m compileall -q "$PROJECT_ROOT/src" "$PROJECT_ROOT/tests"
  "$PYTHON" -m ruff check "$PROJECT_ROOT"
  "$PYTHON" -m pytest -q "$PROJECT_ROOT/tests"
  printf 'UCA_HOST_LOCAL_QUALITY_GATES_OK\n'
fi

CLI=(
  "$PYTHON" -m universal_coding_agent.cli
  --state-root "$STATE_ROOT"
  --provider-factory "$UCA_MODEL_PROVIDER_FACTORY"
  --allow-local-sources
)

"${CLI[@]}" probe
printf 'UCA_REAL_PROVIDER_PROBE_PASS\n'

"$PYTHON" - <<'PY'
from universal_coding_agent.core.models import ModelRequest
from universal_coding_agent.providers.host_chat import create_provider

provider = create_provider()
response = provider.invoke(
    ModelRequest(
        role="qualification",
        system_prompt="Return exactly one JSON object matching the supplied schema.",
        user_prompt='Return {"status":"OK"}.',
        response_schema={
            "type": "object",
            "properties": {"status": {"type": "string"}},
            "required": ["status"],
            "additionalProperties": False,
        },
        max_output_tokens=512,
    )
)
if not response.structured or response.structured.get("status") != "OK":
    raise SystemExit("UCA_REAL_PROVIDER_STRUCTURED_PROBE_FAIL")
print("UCA_REAL_PROVIDER_STRUCTURED_PROBE_PASS")
print(f"ACTUAL_MODEL={response.actual_model or 'unknown'}")
print(f"FINISH_REASON={response.finish_reason or 'unknown'}")
print(f"COMPLETION_TOKENS={response.completion_tokens}")
print(f"REASONING_TOKENS={response.reasoning_tokens}")
PY

SOURCE_FIXTURE="$STATE_ROOT/source-fixture"
mkdir -p "$SOURCE_FIXTURE"
git -C "$SOURCE_FIXTURE" init -q -b main
git -C "$SOURCE_FIXTURE" config user.email "uca-smoke@example.invalid"
git -C "$SOURCE_FIXTURE" config user.name "UCA Smoke"
printf '# Host Provider Fixture\n\nA small read-only qualification repository.\n' > "$SOURCE_FIXTURE/README.md"
printf 'def answer():\n    return 42\n' > "$SOURCE_FIXTURE/app.py"
printf 'def test_answer():\n    assert True\n' > "$SOURCE_FIXTURE/test_app.py"
git -C "$SOURCE_FIXTURE" add README.md app.py test_app.py
git -C "$SOURCE_FIXTURE" commit -q -m "fixture"

TASK_FILE="$STATE_ROOT/task.md"
cat > "$TASK_FILE" <<'TASK'
# Objective

Inspect this small repository and produce a concise, read-only phase plan.

# Requirements

1. Identify the repository structure and available test evidence.
2. Produce one small phase containing one or two slices.
3. Keep all work read-only.
4. Review the plan independently against the task and repository evidence.

# Constraints

- Do not modify repository source.
- Do not create, delete, or rename repository files.
- Do not commit, push, merge, open a pull request, or deploy.
- Missing evidence must be called out rather than invented.
TASK

TASK_ID="$RUN_ID-observe"
"${CLI[@]}" observe \
  --repository "$SOURCE_FIXTURE" \
  --ref main \
  --task-file "$TASK_FILE" \
  --title "Real Host Provider Observe Qualification" \
  --task-id "$TASK_ID" \
  --thread-id "$TASK_ID" \
  > "$STATE_ROOT/observe-result.json"

"$PYTHON" - "$STATE_ROOT" "$TASK_ID" <<'PY'
import json
import subprocess
import sys
from pathlib import Path

state_root = Path(sys.argv[1])
task_id = sys.argv[2]
report_path = state_root / "artifacts" / "tasks" / task_id / "final-report.json"
plan_path = state_root / "artifacts" / "tasks" / task_id / "phase-plan.json"
review_path = state_root / "artifacts" / "tasks" / task_id / "review.json"
if not report_path.is_file() or not plan_path.is_file() or not review_path.is_file():
    raise SystemExit("UCA_REAL_PROVIDER_ARTIFACTS_MISSING")
report = json.loads(report_path.read_text(encoding="utf-8"))
plan = json.loads(plan_path.read_text(encoding="utf-8"))
review = json.loads(review_path.read_text(encoding="utf-8"))
if report["status"] not in {"completed", "blocked"}:
    raise SystemExit(f"UCA_REAL_PROVIDER_BAD_STATUS:{report['status']}")
if not plan.get("phase_id") or not isinstance(plan.get("slices"), list):
    raise SystemExit("UCA_REAL_PROVIDER_PLAN_INVALID")
if review.get("verdict") not in {"PASS", "PASS_WITH_CONDITIONS", "BLOCKED", "FAIL"}:
    raise SystemExit("UCA_REAL_PROVIDER_REVIEW_INVALID")
if report["source_changes"] != [] or report["commit_push_pr_merge_deploy"] is not False:
    raise SystemExit("UCA_REAL_PROVIDER_SAFETY_VIOLATION")
sandbox = state_root / "sandboxes" / task_id / "repo"
status = subprocess.run(
    ["git", "-C", str(sandbox), "status", "--porcelain"],
    check=True,
    capture_output=True,
    text=True,
).stdout
if status:
    raise SystemExit(f"UCA_REAL_PROVIDER_SANDBOX_DIRTY:{status}")
print("UCA_REAL_PROVIDER_OBSERVE_PASS")
print(f"FINAL_STATUS={report['status']}")
print(f"REVIEWER_VERDICT={review['verdict']}")
print(f"PLAN_SLICES={len(plan['slices'])}")
print(f"FINAL_REPORT={report_path}")
PY

printf '\nUCA_HOST_PROVIDER_QUALIFICATION_PASS\n'
printf 'HOST_CLIENT=%s\n' "$HOST_CLIENT"
printf 'STATE_ROOT=%s\n' "$STATE_ROOT"
printf 'VENV=%s\n' "$VENV_PATH"
