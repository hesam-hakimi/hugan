#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
STATE_ROOT=""
ARGS=("$@")

for ((i = 0; i < ${#ARGS[@]}; i++)); do
  if [[ "${ARGS[$i]}" == "--state-root" && $((i + 1)) -lt ${#ARGS[@]} ]]; then
    STATE_ROOT="${ARGS[$((i + 1))]}"
    break
  fi
done

if [[ -z "$STATE_ROOT" ]]; then
  printf 'UCA_LINE_ADDRESSED_QUALIFICATION_FAIL: --state-root is required\n' >&2
  exit 2
fi

mkdir -p "$STATE_ROOT"
STATE_ROOT="$(cd -- "$STATE_ROOT" && pwd)"
LOG_FILE="$STATE_ROOT/legacy-qualification.log"

export UCA_SAFE_EDIT_PROTOCOL=v2-line-addressed

set +e
bash "$SCRIPT_DIR/qualify-safe-host-provider.sh" "${ARGS[@]}" >"$LOG_FILE" 2>&1
LEGACY_RC=$?
set -e

PYTHON="$PROJECT_ROOT/.venv/bin/python"
[[ -x "$PYTHON" ]] || {
  printf 'UCA_LINE_ADDRESSED_QUALIFICATION_FAIL: missing %s\n' "$PYTHON" >&2
  exit 2
}

"$PYTHON" - "$STATE_ROOT" "$LOG_FILE" "$LEGACY_RC" <<'PY'
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

state_root = Path(sys.argv[1])
log_file = Path(sys.argv[2])
legacy_rc = int(sys.argv[3])
reports = sorted((state_root / "artifacts" / "tasks").glob("*/safe-final-report.json"))
if len(reports) != 1:
    tail = ""
    if log_file.is_file():
        tail = "\n".join(log_file.read_text(encoding="utf-8", errors="replace").splitlines()[-40:])
    raise SystemExit(
        "UCA_LINE_ADDRESSED_QUALIFICATION_FAIL: expected one final report, "
        f"found {len(reports)}; legacy_rc={legacy_rc}\n{tail}"
    )

report_path = reports[0]
task_root = report_path.parent
report = json.loads(report_path.read_text(encoding="utf-8"))

assert report.get("status") == "completed", report
assert report.get("scope_approved") is True, report
assert report.get("sandbox_patch_retained") is True, report
assert report.get("rolled_back") is False, report
assert report.get("reviewer_verdict") == "PASS", report
assert report.get("safe_errors") == [], report
assert report.get("approved_changed_paths") == ["app.py"], report
assert report.get("source_repository_modified") is False, report
assert report.get("stage_commit_push_pr_merge_deploy") is False, report
assert report.get("structured_edit_protocol") == "v2-line-addressed", report
assert report.get("line_addressed_edits") is True, report
assert report.get("semantic_anchor_repair_enabled") is False, report
assert report.get("model_authored_patch") is False, report
assert report.get("canonical_patch_generated_by") == "git", report
assert report.get("patch_repair_used") is False, report

required = {
    "edit_proposal": task_root / "edit-proposal.json",
    "edit_validation": task_root / "edit-validation.json",
    "edit_apply": task_root / "edit-apply.json",
    "patch": task_root / "proposed.patch",
    "patch_validation": task_root / "patch-validation.json",
    "tests": task_root / "test-results.json",
    "review": task_root / "safe-review.json",
}
for name, path in required.items():
    assert path.is_file(), (name, path)

edit_proposal = json.loads(required["edit_proposal"].read_text(encoding="utf-8"))
edit_validation = json.loads(required["edit_validation"].read_text(encoding="utf-8"))
edit_apply = json.loads(required["edit_apply"].read_text(encoding="utf-8"))
patch_validation = json.loads(required["patch_validation"].read_text(encoding="utf-8"))
test_payload = json.loads(required["tests"].read_text(encoding="utf-8"))
review = json.loads(required["review"].read_text(encoding="utf-8"))
patch_text = required["patch"].read_text(encoding="utf-8")

assert [item.get("path") for item in edit_proposal.get("edits", [])] == ["app.py"], edit_proposal
replacements = edit_proposal["edits"][0].get("replacements", [])
assert replacements, edit_proposal
assert any(
    str(item.get("old_text") or "").startswith("@range:L")
    and "RETURN_VALUE = 43" in str(item.get("new_text") or "")
    for item in replacements
), edit_proposal
assert edit_validation.get("valid") is True, edit_validation
assert edit_validation.get("changed_paths") == ["app.py"], edit_validation
assert edit_apply.get("changed_paths") == ["app.py"], edit_apply
assert patch_text.startswith("diff --git a/app.py b/app.py\n"), patch_text
assert "-RETURN_VALUE = 42" in patch_text, patch_text
assert "+RETURN_VALUE = 43" in patch_text, patch_text
assert patch_validation.get("valid") is True, patch_validation
assert patch_validation.get("changed_paths") == ["app.py"], patch_validation
assert test_payload.get("scope_intact") is True, test_payload
assert test_payload.get("actual_changed_paths") == ["app.py"], test_payload
assert test_payload.get("results"), test_payload
assert all(item.get("passed") for item in test_payload["results"]), test_payload
assert review.get("verdict") == "PASS", review
assert review.get("required_actions", []) == [], review

source = state_root / "source-fixture"
sandbox = state_root / "sandboxes" / report["sandbox_id"] / "repo"


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

assert git(source, "status", "--porcelain=v1", "-uall") == ""
assert git(sandbox, "status", "--porcelain=v1", "-uall") == "M app.py"
assert "RETURN_VALUE = 42" in (source / "app.py").read_text(encoding="utf-8")
assert "RETURN_VALUE = 43" in (sandbox / "app.py").read_text(encoding="utf-8")

for before_name, after_name in (
    ("host-head-before.txt", "host-head-after.txt"),
    ("host-branch-before.txt", "host-branch-after.txt"),
    ("host-status-before.txt", "host-status-after.txt"),
    ("host-worktrees-before.txt", "host-worktrees-after.txt"),
):
    before = state_root / before_name
    after = state_root / after_name
    if before.exists() or after.exists():
        assert before.is_file() and after.is_file(), (before, after)
        assert before.read_bytes() == after.read_bytes(), before_name

print("UCA_REAL_SAFE_PROVIDER_STRUCTURED_EDIT_PASS")
print("UCA_REAL_SAFE_PROVIDER_LINE_ADDRESSED_EDIT_PASS")
print("UCA_REAL_SAFE_PROVIDER_GIT_PATCH_GENERATION_PASS")
print("UCA_REAL_SAFE_PROVIDER_PATCH_VALIDATION_PASS")
print("UCA_REAL_SAFE_PROVIDER_TESTS_PASS")
print("UCA_REAL_SAFE_PROVIDER_REVIEW_PASS")
print("UCA_REAL_SAFE_PROVIDER_SOURCE_PRESERVED")
print("UCA_REAL_SAFE_PROVIDER_HOST_REPOSITORY_PRESERVED")
print("UCA_REAL_SAFE_PROVIDER_QUALIFICATION_PASS")
print(f"SAFE_FINAL_REPORT={report_path}")
print(f"STATE_ROOT={state_root}")
PY
