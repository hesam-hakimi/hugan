#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_PATH="${UCA_VENV_PATH:-$PROJECT_ROOT/.venv}"
HOST_CLIENT="${UCA_HOST_CLIENT_PATH:-}"
HOST_PYTHON="${UCA_HOST_PYTHON:-}"
STATE_ROOT=""
SKIP_INSTALL=0
SKIP_QUALITY=0

usage() {
  cat <<'USAGE'
Usage: bash scripts/qualify-safe-host-provider.sh [options]

Options:
  --host-client PATH   Existing site-owned Python client module. Required unless
                       UCA_HOST_CLIENT_PATH is already set.
  --host-python PATH   Python interpreter for the site-owned client. If omitted,
                       the script searches parent .venv/venv directories first.
  --state-root PATH    Durable qualification state directory.
  --skip-install       Reuse the current Universal Agent environment.
  --skip-quality       Skip local compile, lint, and unit-test gates.
  -h, --help           Show this help.

The qualification uses a disposable local Git fixture. It proves that the real
host model can generate a bounded patch, pause for human scope approval, resume,
pass deterministic patch validation, run an operator-owned test profile, receive
an independent PASS review, and retain the patch only inside the sandbox.

No stage, commit, push, pull request, merge, deploy, or source-checkout mutation
is performed.
USAGE
}

fail() {
  printf 'UCA_REAL_SAFE_PROVIDER_QUALIFICATION_FAIL: %s\n' "$*" >&2
  exit 1
}

while (($#)); do
  case "$1" in
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

if [[ -z "$HOST_PYTHON" ]]; then
  search_dir="$(dirname -- "$HOST_CLIENT")"
  for _ in 1 2 3 4 5 6; do
    for candidate in "$search_dir/.venv/bin/python" "$search_dir/venv/bin/python"; do
      if [[ -x "$candidate" ]]; then
        HOST_PYTHON="$candidate"
        break 2
      fi
    done
    parent="$(dirname -- "$search_dir")"
    [[ "$parent" != "$search_dir" ]] || break
    search_dir="$parent"
  done
fi
if [[ -z "$HOST_PYTHON" ]]; then
  HOST_PYTHON="$(command -v python3 || true)"
fi
[[ -n "$HOST_PYTHON" && -x "$HOST_PYTHON" ]] || fail "unable to locate host Python interpreter"
HOST_PYTHON="$(cd -- "$(dirname -- "$HOST_PYTHON")" && pwd)/$(basename -- "$HOST_PYTHON")"

RUN_ID="uca-safe-host-$(date -u +%Y%m%dT%H%M%SZ)-$$"
if [[ -z "$STATE_ROOT" ]]; then
  STATE_ROOT="$HOME/.uca-safe-host-runs/$RUN_ID"
fi
mkdir -p "$STATE_ROOT/tmp"
STATE_ROOT="$(cd -- "$STATE_ROOT" && pwd)"
SOURCE="$STATE_ROOT/source-fixture"
TASK_FILE="$STATE_ROOT/task.md"
SCOPE_FILE="$STATE_ROOT/approved-scope.json"
POLICY_FILE="$STATE_ROOT/trusted-policy.json"
TASK_ID="$RUN_ID-task"
THREAD_ID="$RUN_ID-thread"

export TMPDIR="$STATE_ROOT/tmp"
export PYTHONDONTWRITEBYTECODE=1
export PIP_DISABLE_PIP_VERSION_CHECK=1
export UCA_HOST_CLIENT_PATH="$HOST_CLIENT"
export UCA_HOST_PYTHON="$HOST_PYTHON"
export UCA_HOST_BRIDGE_TIMEOUT_SECONDS="${UCA_HOST_BRIDGE_TIMEOUT_SECONDS:-300}"
export UCA_MODEL_PROVIDER_FACTORY="universal_coding_agent.providers.host_subprocess:create_provider"

trap 'printf "UCA_REAL_SAFE_PROVIDER_QUALIFICATION_FAIL: command failed at line %s\n" "$LINENO" >&2' ERR

printf 'UCA_REAL_SAFE_PROVIDER_START\n'
printf 'HOST_CLIENT=%s\n' "$HOST_CLIENT"
printf 'HOST_PYTHON=%s\n' "$HOST_PYTHON"
printf 'STATE_ROOT=%s\n' "$STATE_ROOT"
"$HOST_PYTHON" --version

if [[ ! -x "$VENV_PATH/bin/python" ]]; then
  ((SKIP_INSTALL == 0)) || fail "Universal Agent virtual environment is missing"
  "$PYTHON_BIN" -m venv "$VENV_PATH"
fi
PYTHON="$VENV_PATH/bin/python"
if ! "$PYTHON" -c 'import universal_coding_agent' >/dev/null 2>&1; then
  ((SKIP_INSTALL == 0)) || fail "Universal Agent is not installed"
  "$PYTHON" -m pip install -e "$PROJECT_ROOT[dev]"
fi
"$PYTHON" -m pip check

if ((SKIP_QUALITY == 0)); then
  "$PYTHON" -m compileall -q "$PROJECT_ROOT/src" "$PROJECT_ROOT/tests"
  "$PYTHON" -m ruff check "$PROJECT_ROOT"
  "$PYTHON" -m pytest -q "$PROJECT_ROOT/tests"
  printf 'UCA_REAL_SAFE_LOCAL_QUALITY_GATES_OK\n'
fi

"$PYTHON" - <<'PY'
import json
from universal_coding_agent.providers.host_subprocess import create_provider

provider = create_provider()
details = provider.probe_details()
print("UCA_REAL_SAFE_HOST_BRIDGE_PROBE=" + json.dumps(details, sort_keys=True))
if not details.get("ok"):
    raise SystemExit("UCA_REAL_SAFE_HOST_BRIDGE_PROBE_FAIL")
print("UCA_REAL_SAFE_HOST_BRIDGE_PROBE_PASS")
PY

HOST_REPOSITORY=""
if HOST_REPOSITORY="$(git -C "$(dirname -- "$HOST_CLIENT")" rev-parse --show-toplevel 2>/dev/null)"; then
  git -C "$HOST_REPOSITORY" rev-parse HEAD > "$STATE_ROOT/host-head-before.txt"
  git -C "$HOST_REPOSITORY" symbolic-ref --short -q HEAD > "$STATE_ROOT/host-branch-before.txt" || true
  git -C "$HOST_REPOSITORY" status --porcelain=v1 -uall > "$STATE_ROOT/host-status-before.txt"
  git -C "$HOST_REPOSITORY" worktree list --porcelain > "$STATE_ROOT/host-worktrees-before.txt"
  printf 'HOST_REPOSITORY=%s\n' "$HOST_REPOSITORY"
else
  HOST_REPOSITORY=""
  printf 'HOST_REPOSITORY=not-detected\n'
fi

rm -rf "$SOURCE"
mkdir -p "$SOURCE"
git -C "$SOURCE" init -q -b main
git -C "$SOURCE" config user.email "uca-safe@example.invalid"
git -C "$SOURCE" config user.name "UCA Safe Qualification"
cat > "$SOURCE/app.py" <<'PY'
RETURN_VALUE = 42


def answer() -> int:
    return RETURN_VALUE
PY
cat > "$SOURCE/README.md" <<'EOF'
# Disposable Safe Mode Qualification Fixture

This repository exists only to qualify bounded patch generation and review.
EOF
git -C "$SOURCE" add app.py README.md
git -C "$SOURCE" commit -q -m "fixture"
BASE_SHA="$(git -C "$SOURCE" rev-parse HEAD)"
SOURCE_HEAD_BEFORE="$BASE_SHA"
SOURCE_BRANCH_BEFORE="$(git -C "$SOURCE" symbolic-ref --short HEAD)"
SOURCE_STATUS_BEFORE="$(git -C "$SOURCE" status --porcelain=v1 -uall)"
SOURCE_WORKTREES_BEFORE="$(git -C "$SOURCE" worktree list --porcelain)"
SOURCE_COMMIT_COUNT_BEFORE="$(git -C "$SOURCE" rev-list --count HEAD)"

cat > "$TASK_FILE" <<'EOF'
# Objective

In the disposable qualification repository, modify only `app.py` and change the
exact assignment `RETURN_VALUE = 42` to `RETURN_VALUE = 43`.

# Acceptance contract

- `app.py` is the only changed file.
- The operation is a text-only modification, not a create, delete, rename, copy,
  binary, or symlink change.
- `answer()` returns 43 after the patch.
- The approved fixed test profile passes.
- No additional documentation, refactoring, cleanup, or test is required for this
  disposable qualification task.
- If the scope, one-line patch, and test evidence match exactly, the independent
  reviewer should return `PASS` with no required action.

# Safety constraints

- Work only in the isolated sandbox.
- Do not modify the source fixture.
- Do not run arbitrary commands.
- Do not stage, commit, push, create or edit a pull request, merge, or deploy.
EOF

"$PYTHON" - "$SCOPE_FILE" "$POLICY_FILE" "$BASE_SHA" "$PYTHON" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

scope_path = Path(sys.argv[1])
policy_path = Path(sys.argv[2])
base_sha = sys.argv[3]
python = sys.argv[4]
plan_hash = hashlib.sha256(
    b"real-host-safe-mode-disposable-fixture-v1"
).hexdigest()

scope = {
    "manifest_version": "1",
    "base_sha": base_sha,
    "plan_hash": plan_hash,
    "allowed_changes": [
        {
            "path": "app.py",
            "operation": "modify",
            "purpose": "Change the approved fixture constant from 42 to 43.",
        }
    ],
    "denied_prefixes": [
        ".git",
        ".ssh",
        ".env",
        ".venv",
        "venv",
        "node_modules",
        "secrets",
        "credentials",
    ],
    "test_profiles": ["python-check"],
    "acceptance_criteria": [
        "Only app.py changes in the sandbox.",
        "RETURN_VALUE is exactly 43.",
        "answer() returns 43.",
        "The approved focused test passes.",
        "No publication or source-checkout action occurs.",
    ],
    "max_patch_bytes": 20000,
    "max_changed_files": 1,
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
                    "from pathlib import Path; import app; "
                    "text=Path('app.py').read_text(encoding='utf-8'); "
                    "assert 'RETURN_VALUE = 43' in text; "
                    "assert 'RETURN_VALUE = 42' not in text; "
                    "assert app.answer() == 43"
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
  --provider-factory "$UCA_MODEL_PROVIDER_FACTORY"
  --allow-local-sources
)

"${CLI[@]}" probe > "$STATE_ROOT/provider-probe.txt"
printf 'UCA_REAL_SAFE_PROVIDER_PROBE_PASS\n'

"${CLI[@]}" safe \
  --repository "$SOURCE" \
  --ref main \
  --task-file "$TASK_FILE" \
  --scope-file "$SCOPE_FILE" \
  --policy-file "$POLICY_FILE" \
  --title "Real Host Safe Mode Qualification" \
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
    raise SystemExit(f"UCA_REAL_SAFE_APPROVAL_INTERRUPT_INVALID:{payload.get('next')}")
values = payload.get("values", {})
if values.get("status") != "awaiting_scope_approval":
    raise SystemExit(f"UCA_REAL_SAFE_APPROVAL_STATUS_INVALID:{values.get('status')}")
if values.get("scope_approved") is not None:
    raise SystemExit("UCA_REAL_SAFE_SCOPE_PREAPPROVED_UNEXPECTEDLY")
print("UCA_REAL_SAFE_APPROVAL_INTERRUPT_OK")
print(f"SCOPE_HASH={values.get('scope_hash')}")
PY

"${CLI[@]}" safe-resume \
  --thread-id "$THREAD_ID" \
  --decision approve \
  > "$STATE_ROOT/safe-final.json"

if [[ -n "$HOST_REPOSITORY" ]]; then
  git -C "$HOST_REPOSITORY" rev-parse HEAD > "$STATE_ROOT/host-head-after.txt"
  git -C "$HOST_REPOSITORY" symbolic-ref --short -q HEAD > "$STATE_ROOT/host-branch-after.txt" || true
  git -C "$HOST_REPOSITORY" status --porcelain=v1 -uall > "$STATE_ROOT/host-status-after.txt"
  git -C "$HOST_REPOSITORY" worktree list --porcelain > "$STATE_ROOT/host-worktrees-after.txt"
fi

"$PYTHON" - "$STATE_ROOT" "$SOURCE" "$TASK_ID" \
  "$SOURCE_HEAD_BEFORE" "$SOURCE_BRANCH_BEFORE" "$SOURCE_STATUS_BEFORE" \
  "$SOURCE_WORKTREES_BEFORE" "$SOURCE_COMMIT_COUNT_BEFORE" "$HOST_REPOSITORY" <<'PY'
import json
import subprocess
import sys
from pathlib import Path

state_root = Path(sys.argv[1])
source = Path(sys.argv[2])
task_id = sys.argv[3]
source_head_before = sys.argv[4]
source_branch_before = sys.argv[5]
source_status_before = sys.argv[6]
source_worktrees_before = sys.argv[7]
source_commit_count_before = sys.argv[8]
host_repository = sys.argv[9]
task_root = state_root / "artifacts" / "tasks" / task_id
report_path = task_root / "safe-final-report.json"

if not report_path.is_file():
    raise SystemExit("UCA_REAL_SAFE_FINAL_REPORT_MISSING")
report = json.loads(report_path.read_text(encoding="utf-8"))

artifact_names = {
    "proposal": "patch-proposal.json",
    "patch": "proposed.patch",
    "validation": "patch-validation.json",
    "apply": "patch-apply.json",
    "tests": "test-results.json",
    "implementer_validation": "implementer-model-validation.json",
    "review": "safe-review.json",
    "reviewer_validation": "safe-reviewer-model-validation.json",
}
artifacts = {name: task_root / filename for name, filename in artifact_names.items()}

if report.get("status") != "completed":
    print("UCA_REAL_SAFE_PROVIDER_RESULT_NOT_ACCEPTED")
    print(f"FINAL_STATUS={report.get('status')}")
    print(f"REVIEWER_VERDICT={report.get('reviewer_verdict')}")
    print(f"SAFE_ERRORS={json.dumps(report.get('safe_errors', []))}")
    print(f"ROLLED_BACK={report.get('rolled_back')}")
    print(f"FINAL_REPORT={report_path}")
    for name, path in artifacts.items():
        if path.exists():
            print(f"{name.upper()}_ARTIFACT={path}")
    raise SystemExit(2)

for name, path in artifacts.items():
    if not path.is_file():
        raise SystemExit(f"UCA_REAL_SAFE_ARTIFACT_MISSING:{name}:{path}")

proposal = json.loads(artifacts["proposal"].read_text(encoding="utf-8"))
validation = json.loads(artifacts["validation"].read_text(encoding="utf-8"))
test_payload = json.loads(artifacts["tests"].read_text(encoding="utf-8"))
review = json.loads(artifacts["review"].read_text(encoding="utf-8"))
implementer_validation = json.loads(
    artifacts["implementer_validation"].read_text(encoding="utf-8")
)
reviewer_validation = json.loads(
    artifacts["reviewer_validation"].read_text(encoding="utf-8")
)

assert report["scope_approved"] is True, report
assert report["sandbox_patch_retained"] is True, report
assert report["rolled_back"] is False, report
assert report["reviewer_verdict"] == "PASS", report
assert report["safe_errors"] == [], report
assert report["approved_changed_paths"] == ["app.py"], report
assert report["source_repository_modified"] is False, report
assert report["stage_commit_push_pr_merge_deploy"] is False, report
assert proposal["changed_paths"] == ["app.py"], proposal
assert set(proposal.get("requested_test_profiles", [])) <= {"python-check"}, proposal
assert validation["valid"] is True, validation
assert validation["changed_paths"] == ["app.py"], validation
assert test_payload["scope_intact"] is True, test_payload
assert test_payload["actual_changed_paths"] == ["app.py"], test_payload
assert test_payload["results"], test_payload
assert all(item["passed"] for item in test_payload["results"]), test_payload
assert review["verdict"] == "PASS", review
assert review.get("required_actions", []) == [], review

sandbox = state_root / "sandboxes" / task_id / "repo"
source_text = (source / "app.py").read_text(encoding="utf-8")
sandbox_text = (sandbox / "app.py").read_text(encoding="utf-8")
assert "RETURN_VALUE = 42" in source_text
assert "RETURN_VALUE = 43" in sandbox_text
assert "RETURN_VALUE = 42" not in sandbox_text


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

assert git(source, "rev-parse", "HEAD") == source_head_before
assert git(source, "symbolic-ref", "--short", "HEAD") == source_branch_before
assert git(source, "status", "--porcelain=v1", "-uall") == source_status_before
assert git(source, "worktree", "list", "--porcelain") == source_worktrees_before
assert git(source, "rev-list", "--count", "HEAD") == source_commit_count_before
assert git(sandbox, "rev-list", "--count", "HEAD") == source_commit_count_before
assert git(sandbox, "rev-parse", "HEAD") == source_head_before
assert git(sandbox, "status", "--porcelain=v1", "-uall") == "M app.py"

if host_repository:
    host_root = Path(host_repository)
    comparisons = (
        ("host-head-before.txt", "host-head-after.txt"),
        ("host-branch-before.txt", "host-branch-after.txt"),
        ("host-status-before.txt", "host-status-after.txt"),
        ("host-worktrees-before.txt", "host-worktrees-after.txt"),
    )
    for before_name, after_name in comparisons:
        before = state_root / before_name
        after = state_root / after_name
        if before.read_bytes() != after.read_bytes():
            raise SystemExit(f"UCA_REAL_SAFE_HOST_REPOSITORY_DRIFT:{before_name}")


def actual_model(payload: dict) -> str:
    attempts = payload.get("attempts") or []
    for attempt in reversed(attempts):
        value = str(attempt.get("actual_model") or "").strip()
        if value:
            return value
    return "unknown"

implementer_model = actual_model(implementer_validation)
reviewer_model = actual_model(reviewer_validation)
if implementer_model == "unknown" or reviewer_model == "unknown":
    raise SystemExit("UCA_REAL_SAFE_ACTUAL_MODEL_MISSING")

print("UCA_REAL_SAFE_PROVIDER_IMPLEMENTER_PASS")
print(f"IMPLEMENTER_ACTUAL_MODEL={implementer_model}")
print(f"IMPLEMENTER_SCHEMA_REPAIR_USED={implementer_validation.get('repair_used')}")
print("UCA_REAL_SAFE_PROVIDER_PATCH_VALIDATION_PASS")
print("UCA_REAL_SAFE_PROVIDER_TESTS_PASS")
print("UCA_REAL_SAFE_PROVIDER_REVIEW_PASS")
print(f"REVIEWER_ACTUAL_MODEL={reviewer_model}")
print(f"REVIEWER_SCHEMA_REPAIR_USED={reviewer_validation.get('repair_used')}")
print("UCA_REAL_SAFE_PROVIDER_SOURCE_PRESERVED")
if host_repository:
    print("UCA_REAL_SAFE_PROVIDER_HOST_REPOSITORY_PRESERVED")
print("UCA_REAL_SAFE_PROVIDER_QUALIFICATION_PASS")
print(f"SAFE_FINAL_REPORT={report_path}")
print(f"SAFE_PATCH={artifacts['patch']}")
print(f"SAFE_TEST_RESULTS={artifacts['tests']}")
print(f"SAFE_REVIEW={artifacts['review']}")
print(f"SAFE_SANDBOX={sandbox}")
print(f"STATE_ROOT={state_root}")
PY
