bash -lc '
set -Eeuo pipefail

cd /home/tag5916/projects/universal-coding-agent/universal-coding-agent

STATE_ROOT="/home/tag5916/.uca-project-runs/uca-observe-20260818T023011Z-1221115"

.venv/bin/python - "$STATE_ROOT" <<'"'"'PY'"'"'
import json
import sys
from pathlib import Path

state_root = Path(sys.argv[1])
run_summary = json.loads(
    (state_root / "run-summary.json").read_text(encoding="utf-8")
)

task_id = run_summary["task_id"]
task_root = state_root / "artifacts" / "tasks" / task_id

def load_json(name: str) -> dict:
    path = task_root / name
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))

plan = load_json("phase-plan.json")
review = load_json("review.json")
report = load_json("final-report.json")
planner_validation = load_json("planner-model-validation.json")
reviewer_validation = load_json("reviewer-model-validation.json")

result = {
    "task_id": task_id,
    "base_sha": report.get("base_sha"),
    "final_status": report.get("status"),
    "reviewer_verdict": review.get("verdict"),
    "safe_errors": report.get("safe_errors", []),
    "planner_schema_repair_used": planner_validation.get("repair_used"),
    "reviewer_schema_repair_used": reviewer_validation.get("repair_used"),
    "phase": {
        "phase_id": plan.get("phase_id"),
        "title": plan.get("title"),
        "objective": plan.get("objective"),
        "blockers": plan.get("blockers", []),
        "architecture_decisions_required": plan.get(
            "architecture_decisions_required", []
        ),
        "final_acceptance_criteria": plan.get(
            "final_acceptance_criteria", []
        ),
    },
    "slices": [
        {
            "slice_id": item.get("slice_id"),
            "title": item.get("title"),
            "objective": item.get("objective"),
            "dependencies": item.get("dependencies", []),
            "external_dependencies": item.get(
                "external_dependencies", []
            ),
            "expected_paths": item.get("expected_paths", []),
            "acceptance_criteria": item.get(
                "acceptance_criteria", []
            ),
            "recommended_checks": item.get(
                "recommended_checks", []
            ),
            "stop_conditions": item.get("stop_conditions", []),
        }
        for item in plan.get("slices", [])
    ],
    "review": {
        "requirement_findings": review.get(
            "requirement_findings", []
        ),
        "scope_findings": review.get("scope_findings", []),
        "security_findings": review.get(
            "security_findings", []
        ),
        "test_findings": review.get("test_findings", []),
        "required_actions": review.get("required_actions", []),
        "confidence": review.get("confidence"),
    },
    "source_repository_preserved": True,
    "publication_action_performed": report.get(
        "commit_push_pr_merge_deploy"
    ),
}

output = json.dumps(result, indent=2, ensure_ascii=False)
summary_path = state_root / "phase2c-decision-summary.json"
summary_path.write_text(output, encoding="utf-8")

print(output)
print()
print(f"PHASE2C_DECISION_SUMMARY={summary_path}")
PY
'
