#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_PATH="${UCA_VENV_PATH:-$PROJECT_ROOT/.venv}"
PROVIDER_FACTORY="${UCA_MODEL_PROVIDER_FACTORY:-}"
HOST_CLIENT="${UCA_HOST_CLIENT_PATH:-}"
HOST_PYTHON="${UCA_HOST_PYTHON:-}"
REPOSITORY=""
BASE_REF=""
TASK_FILE=""
PHASE_ID=""
TITLE=""
STATE_ROOT=""
TASK_ID=""
THREAD_ID=""
SKIP_INSTALL=0
SKIP_PROBE=0
REQUIRE_PLAN_APPROVAL=0
FOCUS_ITEMS=()

usage() {
  cat <<'USAGE'
Usage: bash scripts/observe-project.sh [options]

Required:
  --repository SOURCE      Credential-free HTTPS/SSH Git URL or a controlled
                           local Git repository path.
  --ref REF                Branch, tag, or immutable commit to inspect.
  One of:
    --task-file PATH       Complete task Markdown.
    --phase-id TEXT        Generate a standard read-only phase-qualification task.

Provider options:
  --provider-factory SPEC  Provider factory in module:function form. When omitted,
                           the host subprocess provider is used.
  --host-client PATH       Site-owned model client module for the host provider.
  --host-python PATH       Python interpreter for the site-owned client. When
                           omitted, parent .venv/venv directories are searched.

Task options:
  --focus TEXT             Add a focus area to a generated phase task. Repeatable.
  --title TEXT             Task title.
  --task-id ID             Stable task ID; generated when omitted.
  --thread-id ID           LangGraph thread ID; defaults to task ID.
  --require-plan-approval  Pause after planning instead of continuing to review.

Runtime options:
  --state-root PATH        Durable run-state directory.
  --skip-install           Reuse an already prepared Universal Agent environment.
  --skip-probe             Skip the model-provider probe before the Observe run.
  -h, --help               Show this help.

The command is Observe-only. It does not modify source, stage, commit, push,
create a pull request, merge, or deploy.
USAGE
}

fail() {
  printf 'UCA_PROJECT_OBSERVE_FAIL: %s\n' "$*" >&2
  exit 1
}

while (($#)); do
  case "$1" in
    --repository)
      (($# >= 2)) || fail "--repository requires a value"
      REPOSITORY="$2"
      shift 2
      ;;
    --ref)
      (($# >= 2)) || fail "--ref requires a value"
      BASE_REF="$2"
      shift 2
      ;;
    --task-file)
      (($# >= 2)) || fail "--task-file requires a value"
      TASK_FILE="$2"
      shift 2
      ;;
    --phase-id)
      (($# >= 2)) || fail "--phase-id requires a value"
      PHASE_ID="$2"
      shift 2
      ;;
    --focus)
      (($# >= 2)) || fail "--focus requires a value"
      FOCUS_ITEMS+=("$2")
      shift 2
      ;;
    --title)
      (($# >= 2)) || fail "--title requires a value"
      TITLE="$2"
      shift 2
      ;;
    --task-id)
      (($# >= 2)) || fail "--task-id requires a value"
      TASK_ID="$2"
      shift 2
      ;;
    --thread-id)
      (($# >= 2)) || fail "--thread-id requires a value"
      THREAD_ID="$2"
      shift 2
      ;;
    --provider-factory)
      (($# >= 2)) || fail "--provider-factory requires a value"
      PROVIDER_FACTORY="$2"
      shift 2
      ;;
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
    --require-plan-approval)
      REQUIRE_PLAN_APPROVAL=1
      shift
      ;;
    --skip-install)
      SKIP_INSTALL=1
      shift
      ;;
    --skip-probe)
      SKIP_PROBE=1
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

[[ -n "$REPOSITORY" ]] || fail "--repository is required"
[[ -n "$BASE_REF" ]] || fail "--ref is required"
if [[ -n "$TASK_FILE" && -n "$PHASE_ID" ]]; then
  fail "pass either --task-file or --phase-id, not both"
fi
[[ -n "$TASK_FILE" || -n "$PHASE_ID" ]] || fail "pass --task-file or --phase-id"
command -v git >/dev/null 2>&1 || fail "git is not available"
command -v "$PYTHON_BIN" >/dev/null 2>&1 || fail "$PYTHON_BIN is not available"
[[ -n "${HOME:-}" && -d "$HOME" && -w "$HOME" ]] || fail "HOME must be writable"

RUN_ID="uca-observe-$(date -u +%Y%m%dT%H%M%SZ)-$$"
TASK_ID="${TASK_ID:-$RUN_ID}"
THREAD_ID="${THREAD_ID:-$TASK_ID}"
if [[ -z "$STATE_ROOT" ]]; then
  STATE_ROOT="$HOME/.uca-project-runs/$RUN_ID"
fi
mkdir -p "$STATE_ROOT/tmp"
STATE_ROOT="$(cd -- "$STATE_ROOT" && pwd)"
export TMPDIR="$STATE_ROOT/tmp"
export PYTHONDONTWRITEBYTECODE=1
export PIP_DISABLE_PIP_VERSION_CHECK=1

LOCAL_SOURCE=0
if [[ -e "$REPOSITORY" ]]; then
  [[ -d "$REPOSITORY" ]] || fail "local repository source must be a directory"
  REPOSITORY="$(cd -- "$REPOSITORY" && pwd -P)"
  git -C "$REPOSITORY" rev-parse --git-dir >/dev/null 2>&1 \
    || fail "local repository source is not a Git repository"
  LOCAL_SOURCE=1
  git -C "$REPOSITORY" rev-parse HEAD > "$STATE_ROOT/source-head-before.txt"
  git -C "$REPOSITORY" branch --show-current > "$STATE_ROOT/source-branch-before.txt"
  git -C "$REPOSITORY" status --porcelain=v1 -uall > "$STATE_ROOT/source-status-before.txt"
  git -C "$REPOSITORY" worktree list --porcelain > "$STATE_ROOT/source-worktrees-before.txt"
fi

if [[ -n "$TASK_FILE" ]]; then
  [[ -f "$TASK_FILE" ]] || fail "task file does not exist: $TASK_FILE"
  TASK_FILE="$(cd -- "$(dirname -- "$TASK_FILE")" && pwd)/$(basename -- "$TASK_FILE")"
  TITLE="${TITLE:-$(basename -- "$TASK_FILE")}" 
else
  TASK_FILE="$STATE_ROOT/generated-task.md"
  TITLE="${TITLE:-Read-only qualification of $PHASE_ID}"
  {
    printf '# Objective\n\n'
    printf 'Perform a read-only, evidence-backed qualification of **%s**.\n\n' "$PHASE_ID"
    printf '# Required investigation\n\n'
    printf '1. Load repository instructions, architecture documents, ADRs, contracts, and tests.\n'
    printf '2. Reconstruct the phase objective and acceptance criteria from repository evidence.\n'
    printf '3. Classify requirements as implemented, incomplete, contradicted, or unsupported by evidence.\n'
    printf '4. Identify relevant source files, tests, dependencies, risks, and unresolved decisions.\n'
    printf '5. Produce bounded remediation slices with explicit dependencies and stop conditions.\n'
    printf '6. Perform an independent review of the resulting plan.\n\n'
    if ((${#FOCUS_ITEMS[@]})); then
      printf '# Focus areas\n\n'
      for item in "${FOCUS_ITEMS[@]}"; do
        printf -- '- %s\n' "$item"
      done
      printf '\n'
    fi
    printf '# Constraints\n\n'
    printf -- '- Observe only.\n'
    printf -- '- Do not modify, create, delete, or rename repository files.\n'
    printf -- '- Do not stage, commit, push, create or edit a pull request, merge, or deploy.\n'
    printf -- '- Do not infer missing requirements; record missing evidence as a blocker or question.\n'
    printf -- '- Distinguish confirmed facts, inferences, assumptions, and unresolved questions.\n'
    printf -- '- Preserve repository branch, HEAD, worktree inventory, and Git status.\n\n'
    printf '# Required output\n\n'
    printf -- '- Repository, ref, and immutable base SHA.\n'
    printf -- '- Evidence-backed requirement and finding summary.\n'
    printf -- '- Bounded phase/slice plan with dependencies, checks, and stop conditions.\n'
    printf -- '- Independent reviewer verdict and required actions.\n'
    printf -- '- Explicit confirmation that no source change or publication action occurred.\n'
  } > "$TASK_FILE"
fi

if [[ -z "$PROVIDER_FACTORY" ]]; then
  PROVIDER_FACTORY="universal_coding_agent.providers.host_subprocess:create_provider"
fi

if [[ "$PROVIDER_FACTORY" == "universal_coding_agent.providers.host_subprocess:create_provider" ]]; then
  [[ -n "$HOST_CLIENT" ]] || fail "pass --host-client or set UCA_HOST_CLIENT_PATH"
  [[ -f "$HOST_CLIENT" ]] || fail "host client file does not exist: $HOST_CLIENT"
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
  [[ -n "$HOST_PYTHON" && -x "$HOST_PYTHON" ]] \
    || fail "pass --host-python or place a Python environment above the host client"
  HOST_PYTHON="$(cd -- "$(dirname -- "$HOST_PYTHON")" && pwd)/$(basename -- "$HOST_PYTHON")"
  export UCA_HOST_CLIENT_PATH="$HOST_CLIENT"
  export UCA_HOST_PYTHON="$HOST_PYTHON"
fi
export UCA_MODEL_PROVIDER_FACTORY="$PROVIDER_FACTORY"

trap 'printf "UCA_PROJECT_OBSERVE_FAIL: command failed at line %s\n" "$LINENO" >&2' ERR

if [[ ! -x "$VENV_PATH/bin/python" ]]; then
  ((SKIP_INSTALL == 0)) || fail "Universal Agent virtual environment is missing"
  "$PYTHON_BIN" -m venv "$VENV_PATH"
fi
PYTHON="$VENV_PATH/bin/python"
if ! "$PYTHON" -c 'import universal_coding_agent' >/dev/null 2>&1; then
  ((SKIP_INSTALL == 0)) || fail "Universal Agent is not installed in the selected environment"
  "$PYTHON" -m pip install -e "$PROJECT_ROOT"
fi
"$PYTHON" -m pip check >/dev/null

CLI=(
  "$PYTHON" -m universal_coding_agent.cli
  --state-root "$STATE_ROOT"
  --provider-factory "$PROVIDER_FACTORY"
)
if ((LOCAL_SOURCE == 1)); then
  CLI+=(--allow-local-sources)
fi

printf 'UCA_PROJECT_OBSERVE_START\n'
printf 'REPOSITORY=%s\n' "$REPOSITORY"
printf 'REF=%s\n' "$BASE_REF"
printf 'TASK_ID=%s\n' "$TASK_ID"
printf 'THREAD_ID=%s\n' "$THREAD_ID"
printf 'STATE_ROOT=%s\n' "$STATE_ROOT"
printf 'PROVIDER_FACTORY=%s\n' "$PROVIDER_FACTORY"
if [[ -n "$HOST_CLIENT" ]]; then
  printf 'HOST_CLIENT=%s\n' "$HOST_CLIENT"
  printf 'HOST_PYTHON=%s\n' "$HOST_PYTHON"
fi

if ((SKIP_PROBE == 0)); then
  "${CLI[@]}" probe
  printf 'UCA_PROJECT_PROVIDER_PROBE_PASS\n'
fi

OBSERVE_COMMAND=(
  "${CLI[@]}" observe
  --repository "$REPOSITORY"
  --ref "$BASE_REF"
  --task-file "$TASK_FILE"
  --title "$TITLE"
  --task-id "$TASK_ID"
  --thread-id "$THREAD_ID"
)
if ((REQUIRE_PLAN_APPROVAL == 1)); then
  OBSERVE_COMMAND+=(--require-plan-approval)
fi
"${OBSERVE_COMMAND[@]}" | tee "$STATE_ROOT/observe-result.json"

REPORT_PATH="$STATE_ROOT/artifacts/tasks/$TASK_ID/final-report.json"
if [[ ! -f "$REPORT_PATH" ]]; then
  if ((REQUIRE_PLAN_APPROVAL == 1)); then
    "${CLI[@]}" status --thread-id "$THREAD_ID" > "$STATE_ROOT/status.json"
    printf '\nUCA_PROJECT_OBSERVE_AWAITING_PLAN_APPROVAL\n'
    printf 'THREAD_ID=%s\n' "$THREAD_ID"
    printf 'STATUS=%s\n' "$STATE_ROOT/status.json"
    printf 'RESUME_APPROVE=%q ' "${CLI[@]}"
    printf 'resume --thread-id %q --decision approve\n' "$THREAD_ID"
    exit 0
  fi
  fail "final report was not created"
fi

"$PYTHON" - "$STATE_ROOT" "$TASK_ID" <<'PY'
import json
import subprocess
import sys
from pathlib import Path

state_root = Path(sys.argv[1])
task_id = sys.argv[2]
task_root = state_root / "artifacts" / "tasks" / task_id
report_path = task_root / "final-report.json"
plan_path = task_root / "phase-plan.json"
review_path = task_root / "review.json"
manifest_path = task_root / "repository-manifest.json"
checks_path = task_root / "checks.json"
for path in (report_path, plan_path, review_path, manifest_path, checks_path):
    if not path.is_file():
        raise SystemExit(f"UCA_PROJECT_ARTIFACT_MISSING:{path.name}")

report = json.loads(report_path.read_text(encoding="utf-8"))
plan = json.loads(plan_path.read_text(encoding="utf-8"))
review = json.loads(review_path.read_text(encoding="utf-8"))
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
checks = json.loads(checks_path.read_text(encoding="utf-8"))

if report.get("status") not in {"completed", "blocked"}:
    raise SystemExit(f"UCA_PROJECT_STATUS_INVALID:{report.get('status')}")
if review.get("verdict") not in {"PASS", "PASS_WITH_CONDITIONS", "BLOCKED", "FAIL"}:
    raise SystemExit("UCA_PROJECT_REVIEW_INVALID")
if report.get("source_changes") != []:
    raise SystemExit("UCA_PROJECT_SOURCE_CHANGE_REPORTED")
if report.get("commit_push_pr_merge_deploy") is not False:
    raise SystemExit("UCA_PROJECT_PUBLICATION_ACTION_REPORTED")
if not plan.get("phase_id") or not isinstance(plan.get("slices"), list):
    raise SystemExit("UCA_PROJECT_PLAN_INVALID")
if not isinstance(checks, list) or any(not bool(item.get("passed")) for item in checks):
    raise SystemExit("UCA_PROJECT_READ_ONLY_CHECK_FAILED")

sandbox = state_root / "sandboxes" / task_id / "repo"
status = subprocess.run(
    ["git", "-C", str(sandbox), "status", "--porcelain=v1"],
    check=True,
    capture_output=True,
    text=True,
).stdout
if status:
    raise SystemExit(f"UCA_PROJECT_SANDBOX_DIRTY:{status}")

summary = {
    "task_id": task_id,
    "status": report["status"],
    "reviewer_verdict": review["verdict"],
    "phase_id": plan["phase_id"],
    "phase_title": plan.get("title"),
    "slice_count": len(plan["slices"]),
    "slice_ids": [item.get("slice_id") for item in plan["slices"]],
    "blockers": plan.get("blockers", []),
    "required_actions": review.get("required_actions", []),
    "base_sha": manifest.get("base_sha"),
    "tracked_file_count": len(manifest.get("files", [])),
    "final_report": str(report_path),
    "phase_plan": str(plan_path),
    "review": str(review_path),
    "repository_manifest": str(manifest_path),
    "checks": str(checks_path),
    "sandbox": str(sandbox),
}
summary_path = state_root / "run-summary.json"
summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")

print("UCA_PROJECT_OBSERVE_EXECUTION_PASS")
print(f"FINAL_STATUS={summary['status']}")
print(f"REVIEWER_VERDICT={summary['reviewer_verdict']}")
print(f"PHASE_ID={summary['phase_id']}")
print(f"PLAN_SLICES={summary['slice_count']}")
print(f"TRACKED_FILES={summary['tracked_file_count']}")
print(f"BASE_SHA={summary['base_sha']}")
print(f"FINAL_REPORT={summary['final_report']}")
print(f"PHASE_PLAN={summary['phase_plan']}")
print(f"REVIEW={summary['review']}")
print(f"RUN_SUMMARY={summary_path}")
print(f"SANDBOX={summary['sandbox']}")
PY

if ((LOCAL_SOURCE == 1)); then
  git -C "$REPOSITORY" rev-parse HEAD > "$STATE_ROOT/source-head-after.txt"
  git -C "$REPOSITORY" branch --show-current > "$STATE_ROOT/source-branch-after.txt"
  git -C "$REPOSITORY" status --porcelain=v1 -uall > "$STATE_ROOT/source-status-after.txt"
  git -C "$REPOSITORY" worktree list --porcelain > "$STATE_ROOT/source-worktrees-after.txt"
  cmp -s "$STATE_ROOT/source-head-before.txt" "$STATE_ROOT/source-head-after.txt" \
    || fail "source HEAD changed"
  cmp -s "$STATE_ROOT/source-branch-before.txt" "$STATE_ROOT/source-branch-after.txt" \
    || fail "source branch changed"
  cmp -s "$STATE_ROOT/source-status-before.txt" "$STATE_ROOT/source-status-after.txt" \
    || fail "source Git status changed"
  cmp -s "$STATE_ROOT/source-worktrees-before.txt" "$STATE_ROOT/source-worktrees-after.txt" \
    || fail "source worktree inventory changed"
  printf 'SOURCE_REPOSITORY_PRESERVED\n'
fi

printf 'UCA_PROJECT_OBSERVE_PASS\n'
printf 'STATE_ROOT=%s\n' "$STATE_ROOT"
