cd /home/tag5916/projects/universal-coding-agent/universal-coding-agent \
&& STATE_ROOT="$(ls -dt "$HOME"/.uca-safe-host-runs/uca-safe-host-* 2>/dev/null | head -n 1)" \
&& test -n "$STATE_ROOT" \
&& .venv/bin/python - "$STATE_ROOT" <<'PY'
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

state_root = Path(sys.argv[1]).resolve()
tasks_root = state_root / "artifacts" / "tasks"

if not tasks_root.is_dir():
    raise SystemExit(f"TASKS_ROOT_NOT_FOUND={tasks_root}")

task_dirs = [path for path in tasks_root.iterdir() if path.is_dir()]
if not task_dirs:
    raise SystemExit(f"NO_TASK_DIRECTORY_FOUND={tasks_root}")

task_root = max(task_dirs, key=lambda path: path.stat().st_mtime)
task_id = task_root.name
sandbox = state_root / "sandboxes" / task_id / "repo"
source = state_root / "source-fixture"

def load_json(name: str) -> dict[str, Any]:
    path = task_root / name
    if not path.is_file():
        return {"_missing": str(path)}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "_read_error": type(exc).__name__,
            "_path": str(path),
        }
    return value if isinstance(value, dict) else {"_value": value}

def read_text(name: str) -> str:
    path = task_root / name
    if not path.is_file():
        return f"[MISSING: {path}]"
    return path.read_text(encoding="utf-8", errors="replace")

def git(root: Path, *args: str) -> str:
    if not root.is_dir():
        return f"[DIRECTORY NOT FOUND: {root}]"
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    output = completed.stdout.strip() or completed.stderr.strip()
    return output or "[CLEAN / EMPTY]"

proposal = load_json("patch-proposal.json")
validation = load_json("patch-validation.json")
implementer_validation = load_json("implementer-model-validation.json")
final_report = load_json("safe-final-report.json")
patch = read_text("proposed.patch")

lines: list[str] = [
    "============================================================",
    "REAL SAFE PROVIDER — PATCH VALIDATION DIAGNOSIS",
    "============================================================",
    f"STATE_ROOT={state_root}",
    f"TASK_ID={task_id}",
    f"TASK_ROOT={task_root}",
    f"SANDBOX={sandbox}",
    "",
    "---------------- FINAL STATUS ----------------",
    f"status={final_report.get('status')}",
    f"reviewer_verdict={final_report.get('reviewer_verdict')}",
    f"safe_errors={json.dumps(final_report.get('safe_errors', []))}",
    f"rolled_back={final_report.get('rolled_back')}",
    "",
    "---------------- VALIDATOR RESULT ----------------",
    f"valid={validation.get('valid')}",
    f"patch_sha256={validation.get('patch_sha256')}",
    f"changed_paths={json.dumps(validation.get('changed_paths', []))}",
    "errors=",
    json.dumps(validation.get("errors", []), indent=2),
    "",
    "---------------- IMPLEMENTER PROPOSAL ----------------",
    json.dumps(proposal, indent=2)[:20000],
    "",
    "---------------- RAW PROPOSED PATCH ----------------",
    patch[:30000],
    "",
    "---------------- IMPLEMENTER MODEL VALIDATION ----------------",
    json.dumps(implementer_validation, indent=2)[:30000],
    "",
    "---------------- SOURCE REPOSITORY STATUS ----------------",
    git(source, "status", "--porcelain=v1", "-uall"),
    "",
    "---------------- SANDBOX STATUS ----------------",
    git(sandbox, "status", "--porcelain=v1", "-uall"),
    "",
    "---------------- SOURCE app.py ----------------",
    (
        (source / "app.py").read_text(encoding="utf-8", errors="replace")
        if (source / "app.py").is_file()
        else "[MISSING]"
    ),
    "",
    "---------------- SANDBOX app.py ----------------",
    (
        (sandbox / "app.py").read_text(encoding="utf-8", errors="replace")
        if (sandbox / "app.py").is_file()
        else "[MISSING]"
    ),
    "============================================================",
]

report_text = "\n".join(lines)
diagnosis_path = state_root / "real-safe-provider-patch-diagnosis.txt"
diagnosis_path.write_text(report_text + "\n", encoding="utf-8")

print(report_text)
print()
print(f"DIAGNOSIS_FILE={diagnosis_path}")
PY
