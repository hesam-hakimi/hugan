bash -lc '
set -Eeuo pipefail

UCA_ROOT="/home/tag5916/projects/universal-coding-agent/universal-coding-agent"
REPOSITORY="/app1/tag5916/projects/kmai-td-genie"
REF="phase2/semantic-plan-contract-validator"

OBSERVE_STATE_ROOT="/home/tag5916/.uca-project-runs/uca-observe-20260818T130108Z-1594237"
OBSERVE_TASK_ID="uca-observe-20260818T130108Z-1594237"

HOST_CLIENT="/app1/tag5916/projects/kmai-td-genie/.kmai-dev-agent/kmai_client.py"
HOST_PYTHON="/app1/tag5916/projects/kmai-td-genie/.venv/bin/python"

WORK_ROOT="$HOME/.uca-phase2c-safe-scope"
TASK_FILE="$WORK_ROOT/phase2c-safe-task.md"
SCOPE_FILE="$WORK_ROOT/approved-scope.json"
POLICY_FILE="$WORK_ROOT/trusted-policy.json"

mkdir -p "$WORK_ROOT"
cd "$UCA_ROOT"

.venv/bin/python - \
  "$OBSERVE_STATE_ROOT" \
  "$OBSERVE_TASK_ID" \
  "$REPOSITORY" \
  "$REF" \
  "$TASK_FILE" \
  "$SCOPE_FILE" \
  "$POLICY_FILE" \
  "$HOST_PYTHON" <<'"'"'PY'"'"'
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path, PurePosixPath

from universal_coding_agent.core.models import PhasePlan


observe_root = Path(sys.argv[1]).resolve()
observe_task_id = sys.argv[2]
repository = Path(sys.argv[3]).resolve()
ref = sys.argv[4]
task_file = Path(sys.argv[5]).resolve()
scope_file = Path(sys.argv[6]).resolve()
policy_file = Path(sys.argv[7]).resolve()
host_python = str(Path(sys.argv[8]).resolve())

task_root = observe_root / "artifacts" / "tasks" / observe_task_id

plan_path = task_root / "phase-plan.json"
report_path = task_root / "final-report.json"
summary_path = observe_root / "run-summary.json"

for required in (plan_path, report_path, summary_path):
    if not required.is_file():
        raise SystemExit(f"REQUIRED_OBSERVE_ARTIFACT_MISSING={required}")

plan_payload = json.loads(plan_path.read_text(encoding="utf-8"))
report_payload = json.loads(report_path.read_text(encoding="utf-8"))
summary_payload = json.loads(summary_path.read_text(encoding="utf-8"))

phase_plan = PhasePlan.model_validate(plan_payload)

base_sha = str(
    summary_payload.get("base_sha")
    or report_payload.get("base_sha")
    or ""
).strip()

if not base_sha:
    raise SystemExit("BASE_SHA_MISSING")

plan_hash = str(summary_payload.get("plan_hash") or "").strip()

if not plan_hash:
    plan_hash = hashlib.sha256(
        phase_plan.model_dump_json().encode("utf-8")
    ).hexdigest()

if len(plan_hash) != 64:
    raise SystemExit(f"PLAN_HASH_INVALID={plan_hash}")

def git(*arguments: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        ["git", "-C", str(repository), *arguments],
        check=False,
        capture_output=True,
        text=True,
    )
    if check and completed.returncode != 0:
        raise SystemExit(
            "GIT_COMMAND_FAILED="
            + " ".join(arguments)
            + "\n"
            + completed.stderr.strip()
        )
    return completed


resolved_ref = git("rev-parse", f"{ref}^{{commit}}").stdout.strip()

if resolved_ref != base_sha:
    raise SystemExit(
        "BASE_SHA_MISMATCH\n"
        f"OBSERVED_BASE_SHA={base_sha}\n"
        f"CURRENT_REF_SHA={resolved_ref}"
    )


modify_paths = (
    "kmai-td-genie/test/test_registry_contract.py",
    "kmai-td-genie/test/test_registry_cache.py",
    "kmai-td-genie/docs/adr/"
    "0002-phase2c-governed-semantic-plan-validator.md",
)

create_paths = (
    "kmai-td-genie/docs/phase2c/safe_mode_scope.md",
)

expected_scope = {
    *(f"MODIFY {path}" for path in modify_paths),
    *(f"CREATE {path}" for path in create_paths),
}

if len(phase_plan.slices) != 1:
    raise SystemExit(
        f"EXPECTED_ONE_SLICE_FOUND={len(phase_plan.slices)}"
    )

planned_scope = set(phase_plan.slices[0].included_scope)

missing_from_plan = expected_scope - planned_scope
if missing_from_plan:
    raise SystemExit(
        "EXPECTED_SCOPE_NOT_PRESENT_IN_PLAN="
        + json.dumps(sorted(missing_from_plan))
    )


def exists_at_base(path: str) -> bool:
    return (
        git(
            "cat-file",
            "-e",
            f"{base_sha}:{path}",
            check=False,
        ).returncode
        == 0
    )


for path in modify_paths:
    if not exists_at_base(path):
        raise SystemExit(f"MODIFY_PATH_NOT_FOUND_AT_BASE={path}")

for path in create_paths:
    if exists_at_base(path):
        raise SystemExit(f"CREATE_PATH_ALREADY_EXISTS_AT_BASE={path}")

    parent = PurePosixPath(path).parent.as_posix()
    if not exists_at_base(parent):
        raise SystemExit(f"CREATE_PARENT_NOT_FOUND_AT_BASE={parent}")


scope = {
    "manifest_version": "1",
    "base_sha": base_sha,
    "plan_hash": plan_hash,
    "allowed_changes": [
        {
            "path": modify_paths[0],
            "operation": "modify",
            "purpose": (
                "Add deterministic contract coverage for canonical full "
                "snapshot identity, field-governance deferral, and related "
                "registry invariants."
            ),
        },
        {
            "path": modify_paths[1],
            "operation": "modify",
            "purpose": (
                "Add deterministic synthetic tests for atomic snapshot "
                "publication, stale-writer rejection, cache identity, and "
                "deterministic cache invalidation."
            ),
        },
        {
            "path": modify_paths[2],
            "operation": "modify",
            "purpose": (
                "Record the seven approved Phase 2C architecture and "
                "contract decisions as the authoritative design boundary."
            ),
        },
        {
            "path": create_paths[0],
            "operation": "create",
            "purpose": (
                "Document the exact first Safe Mode scope, prerequisites, "
                "stop conditions, exclusions, and follow-up slices."
            ),
        },
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
    "test_profiles": [
        "phase2c-contract-tests",
    ],
    "acceptance_criteria": [
        (
            "The ADR records all seven user-approved Phase 2C architecture "
            "and contract decisions without altering production source code."
        ),
        (
            "Field-governance and metadata-classification enforcement are "
            "explicitly deferred while valid metadata preservation and "
            "malformed-value rejection remain documented and testable."
        ),
        (
            "Registry snapshot identity tests prove equal canonical content "
            "has equal identity, ordering-only changes do not alter identity, "
            "and semantic changes produce a new identity."
        ),
        (
            "Registry-cache tests use deterministic synthetic data and cover "
            "atomic publication, no partially visible state, stale-writer "
            "rejection, and deterministic stale-cache invalidation."
        ),
        (
            "Cross-ProductGroup relationship rules are documented as an "
            "approved contract and dedicated relationship tests are identified "
            "as a later bounded slice."
        ),
        (
            "Only the four approved documentation and test paths change."
        ),
        (
            "The two approved focused test files pass without live data."
        ),
    ],
    "max_patch_bytes": 250000,
    "max_changed_files": 4,
}

pytest_code = (
    "import sys; "
    "sys.path[:0] = ["
    "'kmai-td-genie/src/backend',"
    "'kmai-td-genie/src'"
    "]; "
    "import pytest; "
    "raise SystemExit(pytest.main(["
    "'-q',"
    "'-p','no:cacheprovider',"
    "'kmai-td-genie/test/test_registry_contract.py',"
    "'kmai-td-genie/test/test_registry_cache.py'"
    "]))"
)

policy = {
    "policy_version": "1",
    "profiles": [
        {
            "profile_id": "phase2c-contract-tests",
            "argv": [
                host_python,
                "-c",
                pytest_code,
            ],
            "cwd": ".",
            "timeout_seconds": 600,
            "output_limit": 60000,
        }
    ],
}

task_text = f"""# Objective

Implement the first approved Phase 2C documentation-and-contract-test slice.

This task is bound to:

- Base SHA: `{base_sha}`
- Observe plan hash: `{plan_hash}`
- Exact approved file manifest: `{scope_file}`

# Approved external prerequisite

The user has explicitly approved all seven Phase 2C architecture and contract
decisions below. This approval is the external prerequisite for this slice.

## Decision 1 — deterministic test data

Unit, contract, and standard CI tests use deterministic synthetic or mock data.
Live governed data is not a dependency of this slice.

## Decision 2 — optional live-data qualification

Live governed data may be used only by a separate, optional, read-only,
environment-gated integration qualification profile.

## Decision 3 — field-governance deferral

Field governance and classification enforcement are explicitly deferred in
Phase 2C.

Classification metadata may be absent, null, or unknown. Valid metadata is
preserved and serialized. Phase 2C does not grant authorization from
classification metadata. Malformed governance or classification values are
rejected.

## Decision 4 — immutable and atomic snapshots

Registry snapshots are immutable. Publication is atomic. A reader sees either
the complete previous snapshot or the complete new snapshot and never observes
partially published state.

## Decision 5 — stale-writer and cache contract

Stale writers are rejected using a version conflict. Cache identity includes
registry version or snapshot identity. Publishing a new snapshot
deterministically invalidates stale cache entries.

## Decision 6 — canonical full-snapshot identity

Registry identity is derived from canonical full snapshot content.

Semantic changes to ProductGroup, Schema, Dataset, Field, or Relationship
produce a new identity. Ordering-only changes do not. Equal canonical content
produces equal identity. Stale or conflicting snapshots are rejected.

## Decision 7 — explicit cross-ProductGroup relationships

Cross-ProductGroup relationships are explicit. Both endpoints must exist.
Relationships do not expand authorization. Each Dataset remains independently
authorized. Unknown endpoints are rejected.

# Exact included scope

- MODIFY `{modify_paths[0]}`
- MODIFY `{modify_paths[1]}`
- MODIFY `{modify_paths[2]}`
- CREATE `{create_paths[0]}`

# Required implementation

1. Update the existing ADR to record the seven decisions as the authoritative
   Phase 2C contract boundary.

2. Create `safe_mode_scope.md` describing:

   - the approved external prerequisite;
   - no internal slice dependency;
   - exact file scope;
   - acceptance criteria;
   - excluded scope;
   - stop conditions;
   - production-code follow-up rules;
   - the later dedicated cross-ProductGroup test slice.

3. Update `test_registry_contract.py` using existing repository conventions and
   deterministic synthetic fixtures to cover only contracts supported by the
   existing public test interfaces, including canonical snapshot identity and
   the approved field-governance deferral behavior.

4. Update `test_registry_cache.py` using existing repository conventions and
   deterministic synthetic fixtures to cover atomic publication, stale-writer
   rejection, cache identity, and stale-cache invalidation where existing
   public interfaces support those contracts.

5. Do not weaken or delete existing assertions.

# Internal dependencies

None.

# External dependencies

- The seven user-approved Phase 2C decisions written above.
- Repository evidence at Base SHA `{base_sha}`.
- Observe PhasePlan hash `{plan_hash}`.

# Stop conditions

Stop and do not expand scope when any of the following occurs:

- any approved MODIFY path is missing;
- the approved CREATE path already exists;
- implementing a contract requires changing production source code;
- a test requires live data, deployment access, credentials, or environment
  configuration;
- the approved contract conflicts with an existing authoritative repository
  decision that cannot be reconciled within the approved documentation files;
- a deterministic contract test exposes a production implementation gap;
- any path outside the four-file manifest would need to change.

When a contract test exposes a production-code gap, preserve that fact in the
test and review artifacts. Do not add production code to this patch.

# Explicitly excluded

- all production source code;
- deployment scripts;
- authentication code;
- environment configuration;
- credentials and secrets;
- live-data dependencies;
- Git stage, commit, push, pull request, merge, and deployment;
- automatic scope expansion.

# Test policy

Run only the operator-owned `phase2c-contract-tests` profile.

# Completion rule

The patch may be retained only when:

- all changes remain inside the exact four-file scope;
- the focused tests pass;
- the independent reviewer returns exactly `PASS`;
- the source repository remains unchanged;
- no Git publication operation occurs.
"""

task_file.parent.mkdir(parents=True, exist_ok=True)

scope_file.write_text(
    json.dumps(scope, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8",
)

policy_file.write_text(
    json.dumps(policy, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8",
)

task_file.write_text(task_text, encoding="utf-8")

print("PHASE2C_SAFE_PREFLIGHT_OK")
print(f"BASE_SHA={base_sha}")
print(f"PLAN_HASH={plan_hash}")
print(f"TASK_FILE={task_file}")
print(f"SCOPE_FILE={scope_file}")
print(f"POLICY_FILE={policy_file}")
print("APPROVED_PATHS:")
for item in scope["allowed_changes"]:
    print(
        f"- {item['operation'].upper()} "
        f"{item['path']}"
    )
PY

RUN_ID="phase2c-safe-$(date -u +%Y%m%dT%H%M%SZ)-$$"
STATE_ROOT="$HOME/.uca-safe-runs/$RUN_ID"
TASK_ID="$RUN_ID-task"
THREAD_ID="$RUN_ID-thread"

mkdir -p "$STATE_ROOT"

export UCA_HOST_CLIENT_PATH="$HOST_CLIENT"
export UCA_HOST_PYTHON="$HOST_PYTHON"

PROVIDER_FACTORY="universal_coding_agent.providers.host_subprocess:create_provider"

CLI=(
  .venv/bin/python
  -m universal_coding_agent.cli
  --state-root "$STATE_ROOT"
  --provider-factory "$PROVIDER_FACTORY"
  --allow-local-sources
)

"${CLI[@]}" safe \
  --repository "$REPOSITORY" \
  --ref "$REF" \
  --task-file "$TASK_FILE" \
  --scope-file "$SCOPE_FILE" \
  --policy-file "$POLICY_FILE" \
  --title "Phase 2C documentation and contract-test slice" \
  --task-id "$TASK_ID" \
  --thread-id "$THREAD_ID" \
  > "$WORK_ROOT/safe-start.json"

"${CLI[@]}" safe-status \
  --thread-id "$THREAD_ID" \
  > "$WORK_ROOT/safe-status.json"

.venv/bin/python - \
  "$WORK_ROOT/safe-status.json" \
  "$STATE_ROOT" \
  "$TASK_ID" \
  "$THREAD_ID" \
  "$SCOPE_FILE" \
  "$POLICY_FILE" <<'"'"'PY'"'"'
from __future__ import annotations

import json
import sys
from pathlib import Path

status_path = Path(sys.argv[1])
state_root = sys.argv[2]
task_id = sys.argv[3]
thread_id = sys.argv[4]
scope_file = sys.argv[5]
policy_file = sys.argv[6]

payload = json.loads(status_path.read_text(encoding="utf-8"))
values = payload.get("values", {})
next_nodes = payload.get("next", [])

if next_nodes != ["scope_approval"]:
    raise SystemExit(
        "SAFE_SCOPE_APPROVAL_INTERRUPT_NOT_REACHED="
        + json.dumps(next_nodes)
    )

task = values.get("task", {})
manifest = task.get("manifest", {})

print()
print("============================================================")
print("SAFE_SCOPE_APPROVAL_READY")
print("============================================================")
print(f"STATUS={values.get('status')}")
print(f"NEXT={next_nodes}")
print(f"STATE_ROOT={state_root}")
print(f"TASK_ID={task_id}")
print(f"THREAD_ID={thread_id}")
print(f"BASE_SHA={manifest.get('base_sha')}")
print(f"PLAN_HASH={manifest.get('plan_hash')}")
print(f"SCOPE_HASH={values.get('scope_hash')}")
print(f"SCOPE_FILE={scope_file}")
print(f"POLICY_FILE={policy_file}")
print()
print("ALLOWED_CHANGES:")
for item in manifest.get("allowed_changes", []):
    print(
        f"- {str(item.get('operation')).upper()} "
        f"{item.get('path')}"
    )
print()
print("TEST_PROFILES:")
for profile in manifest.get("test_profiles", []):
    print(f"- {profile}")
print()
print("ACCEPTANCE_CRITERIA:")
for criterion in manifest.get("acceptance_criteria", []):
    print(f"- {criterion}")
print()
print("NO PATCH HAS BEEN GENERATED OR APPLIED.")
print("SOURCE REPOSITORY HAS NOT BEEN MODIFIED.")
print("============================================================")
PY
'
