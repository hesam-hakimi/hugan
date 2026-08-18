cd /home/tag5916/projects/universal-coding-agent/universal-coding-agent

.venv/bin/python - <<'PY'
import json
from pathlib import Path

STATE_ROOT = Path(
    "/home/tag5916/.uca-project-runs/"
    "uca-observe-20260818T031615Z-1276240"
)
TASK_ID = "uca-observe-20260818T031615Z-1276240"

TASK_ROOT = STATE_ROOT / "artifacts" / "tasks" / TASK_ID
SANDBOX = STATE_ROOT / "sandboxes" / TASK_ID / "repo"


def load_json(name: str) -> dict:
    path = TASK_ROOT / name
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def add_items(lines: list[str], values: list | tuple, empty: str = "None") -> None:
    if not values:
        lines.append(f"- {empty}")
        return

    for value in values:
        lines.append(f"- {value}")


plan = load_json("phase-plan.json")
review = load_json("review.json")
report = load_json("final-report.json")
planner_validation = load_json("planner-model-validation.json")
reviewer_validation = load_json("reviewer-model-validation.json")

repository_url = report.get("repository", {}).get("url", "")
repo_name = Path(repository_url.rstrip("/")).name
if repo_name.endswith(".git"):
    repo_name = repo_name[:-4]


def inspect_expected_path(raw_path: str) -> tuple[str, str]:
    raw_path = raw_path.strip()
    relative = Path(raw_path)

    candidates = [SANDBOX / relative]

    # Some model outputs include the repository folder name.
    if relative.parts and relative.parts[0] == repo_name:
        candidates.append(SANDBOX / Path(*relative.parts[1:]))

    for candidate in candidates:
        if candidate.exists():
            try:
                resolved = str(candidate.relative_to(SANDBOX))
            except ValueError:
                resolved = str(candidate)
            return "EXISTS", resolved

    return "NOT_FOUND", raw_path


comparison_pairs = [
    ("source-head-before.txt", "source-head-after.txt"),
    ("source-branch-before.txt", "source-branch-after.txt"),
    ("source-status-before.txt", "source-status-after.txt"),
    ("source-worktrees-before.txt", "source-worktrees-after.txt"),
]

source_repository_preserved = True
for before_name, after_name in comparison_pairs:
    before = STATE_ROOT / before_name
    after = STATE_ROOT / after_name
    if not before.is_file() or not after.is_file():
        source_repository_preserved = False
        break
    if before.read_bytes() != after.read_bytes():
        source_repository_preserved = False
        break


lines: list[str] = []

lines.extend(
    [
        "# Phase 2C Evidence Closure — Decision Report",
        "",
        "## Run identity",
        "",
        f"- Task ID: `{TASK_ID}`",
        f"- Repository: `{repository_url}`",
        f"- Base ref: `{report.get('repository', {}).get('base_ref')}`",
        f"- Base SHA: `{report.get('base_sha')}`",
        f"- Final status: **{report.get('status')}**",
        f"- Reviewer verdict: **{review.get('verdict')}**",
        f"- Planner schema repair used: "
        f"**{planner_validation.get('repair_used', False)}**",
        f"- Reviewer schema repair used: "
        f"**{reviewer_validation.get('repair_used', False)}**",
        f"- Safe errors: `{report.get('safe_errors', [])}`",
        f"- Source repository preserved: "
        f"**{source_repository_preserved}**",
        f"- Publication action performed: "
        f"**{report.get('commit_push_pr_merge_deploy')}**",
        "",
        "## Phase",
        "",
        f"- Phase ID: `{plan.get('phase_id')}`",
        f"- Title: {plan.get('title')}",
        f"- Objective: {plan.get('objective')}",
        "",
        "## Phase blockers",
        "",
    ]
)

add_items(lines, plan.get("blockers", []))

lines.extend(
    [
        "",
        "## Architecture decisions required",
        "",
    ]
)
add_items(lines, plan.get("architecture_decisions_required", []))

lines.extend(
    [
        "",
        "## Confirmed evidence returned by Planner",
        "",
    ]
)

evidence = plan.get("evidence", [])
if not evidence:
    lines.append("- No structured evidence items were returned.")
else:
    for item in evidence:
        path = item.get("path", "")
        line_start = item.get("line_start")
        line_end = item.get("line_end")

        location = path
        if line_start:
            location += f":{line_start}"
            if line_end and line_end != line_start:
                location += f"-{line_end}"

        lines.extend(
            [
                f"### `{location}`",
                "",
                f"- Kind: `{item.get('kind')}`",
                f"- Confidence: `{item.get('confidence')}`",
                f"- Summary: {item.get('summary')}",
                "",
            ]
        )

lines.extend(
    [
        "## Planned slices",
        "",
    ]
)

for index, item in enumerate(plan.get("slices", []), start=1):
    lines.extend(
        [
            f"### {index}. `{item.get('slice_id')}` — {item.get('title')}",
            "",
            f"**Objective:** {item.get('objective')}",
            "",
            "**Internal dependencies:**",
            "",
        ]
    )
    add_items(lines, item.get("dependencies", []))

    lines.extend(
        [
            "",
            "**External dependencies:**",
            "",
        ]
    )
    add_items(lines, item.get("external_dependencies", []))

    lines.extend(
        [
            "",
            "**Expected paths — verified against the Sandbox:**",
            "",
        ]
    )

    expected_paths = item.get("expected_paths", [])
    if not expected_paths:
        lines.append("- None")
    else:
        for raw_path in expected_paths:
            status, resolved = inspect_expected_path(raw_path)
            lines.append(f"- **{status}** — `{resolved}`")

    lines.extend(
        [
            "",
            "**Acceptance criteria:**",
            "",
        ]
    )
    add_items(lines, item.get("acceptance_criteria", []))

    lines.extend(
        [
            "",
            "**Recommended checks:**",
            "",
        ]
    )
    add_items(lines, item.get("recommended_checks", []))

    lines.extend(
        [
            "",
            "**Stop conditions:**",
            "",
        ]
    )
    add_items(lines, item.get("stop_conditions", []))

    lines.append("")

lines.extend(
    [
        "## Final acceptance criteria",
        "",
    ]
)
add_items(lines, plan.get("final_acceptance_criteria", []))

review_sections = [
    ("Requirement findings", "requirement_findings"),
    ("Scope findings", "scope_findings"),
    ("Security findings", "security_findings"),
    ("Test findings", "test_findings"),
    ("Required actions", "required_actions"),
]

lines.extend(
    [
        "",
        "## Independent review",
        "",
        f"- Verdict: **{review.get('verdict')}**",
        f"- Confidence: **{review.get('confidence')}**",
        "",
    ]
)

for title, field in review_sections:
    lines.extend([f"### {title}", ""])
    add_items(lines, review.get(field, []))
    lines.append("")

blockers = plan.get("blockers", [])
required_actions = review.get("required_actions", [])

lines.extend(
    [
        "## Safe Mode gate decision",
        "",
    ]
)

if blockers:
    lines.extend(
        [
            "**SAFE MODE NOT YET AUTHORIZED**",
            "",
            "The Phase Plan still contains explicit blockers. These blockers "
            "must be closed, explicitly deferred, or converted into bounded "
            "documentation/test slices before source modification is approved.",
        ]
    )
elif required_actions:
    lines.extend(
        [
            "**SAFE MODE REQUIRES A BOUNDED SCOPE APPROVAL**",
            "",
            "No phase blocker remains, but Reviewer-required actions must be "
            "converted into exact files, tests, acceptance criteria, and "
            "allowed paths before implementation.",
        ]
    )
else:
    lines.extend(
        [
            "**READY FOR SAFE MODE SCOPE DESIGN**",
            "",
            "No explicit phase blocker or mandatory Reviewer action remains. "
            "The next step is to create the first bounded implementation scope.",
        ]
    )

output_path = STATE_ROOT / "phase2c-evidence-closure-report.md"
output_path.write_text(
    "\n".join(lines).rstrip() + "\n",
    encoding="utf-8",
)

print("\n".join(lines))
print()
print(f"PHASE2C_EVIDENCE_REPORT={output_path}")
PY
