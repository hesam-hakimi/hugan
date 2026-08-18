cd /home/tag5916/projects/universal-coding-agent/universal-coding-agent

STATE_ROOT="/home/tag5916/.uca-project-runs/uca-observe-20260818T130108Z-1594237"
TASK_ID="uca-observe-20260818T130108Z-1594237"
TASK_ROOT="$STATE_ROOT/artifacts/tasks/$TASK_ID"

python - <<'PY'
import json
from pathlib import Path

state_root = Path("/home/tag5916/.uca-project-runs/uca-observe-20260818T130108Z-1594237")
task_id = "uca-observe-20260818T130108Z-1594237"
task_root = state_root / "artifacts" / "tasks" / task_id

phase_plan = json.loads((task_root / "phase-plan.json").read_text(encoding="utf-8"))
review = json.loads((task_root / "review.json").read_text(encoding="utf-8"))
final_report = json.loads((task_root / "final-report.json").read_text(encoding="utf-8"))

print("\n=== RUN SUMMARY ===")
print("phase_id:", phase_plan.get("phase_id"))
print("title:", phase_plan.get("title"))
print("final_status:", final_report.get("status"))
print("reviewer_verdict:", review.get("verdict"))
print("slice_count:", len(phase_plan.get("slices", [])))

print("\n=== PHASE BLOCKERS ===")
for x in phase_plan.get("blockers", []):
    print("-", x)
if not phase_plan.get("blockers"):
    print("- None")

print("\n=== ARCHITECTURE DECISIONS REQUIRED ===")
for x in phase_plan.get("architecture_decisions_required", []):
    print("-", x)
if not phase_plan.get("architecture_decisions_required"):
    print("- None")

for i, s in enumerate(phase_plan.get("slices", []), start=1):
    print(f"\n=== SLICE {i} ===")
    print("slice_id:", s.get("slice_id"))
    print("title:", s.get("title"))
    print("objective:", s.get("objective"))

    print("\n[included_scope]")
    for x in s.get("included_scope", []):
        print("-", x)
    if not s.get("included_scope"):
        print("- None")

    print("\n[expected_paths]")
    for x in s.get("expected_paths", []):
        print("-", x)
    if not s.get("expected_paths"):
        print("- None")

    print("\n[acceptance_criteria]")
    for x in s.get("acceptance_criteria", []):
        print("-", x)
    if not s.get("acceptance_criteria"):
        print("- None")

    print("\n[recommended_checks]")
    for x in s.get("recommended_checks", []):
        print("-", x)
    if not s.get("recommended_checks"):
        print("- None")

    print("\n[excluded_scope]")
    for x in s.get("excluded_scope", []):
        print("-", x)
    if not s.get("excluded_scope"):
        print("- None")

    print("\n[dependencies]")
    for x in s.get("dependencies", []):
        print("-", x)
    if not s.get("dependencies"):
        print("- None")

    print("\n[external_dependencies]")
    for x in s.get("external_dependencies", []):
        print("-", x)
    if not s.get("external_dependencies"):
        print("- None")

    print("\n[stop_conditions]")
    for x in s.get("stop_conditions", []):
        print("-", x)
    if not s.get("stop_conditions"):
        print("- None")

print("\n=== REVIEW REQUIRED ACTIONS ===")
for x in review.get("required_actions", []):
    print("-", x)
if not review.get("required_actions"):
    print("- None")

print("\n=== REVIEW REQUIREMENT FINDINGS ===")
for x in review.get("requirement_findings", []):
    print("-", x)
if not review.get("requirement_findings"):
    print("- None")
PY
