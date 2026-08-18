bash -lc '
set -Eeuo pipefail

UCA_ROOT="/home/tag5916/projects/universal-coding-agent/universal-coding-agent"
REPOSITORY="/app1/tag5916/projects/kmai-td-genie"
REF="phase2/semantic-plan-contract-validator"

OBSERVE_STATE_ROOT="/home/tag5916/.uca-project-runs/uca-observe-20260818T130108Z-1594237"
OBSERVE_TASK_ID="uca-observe-20260818T130108Z-1594237"

HOST_CLIENT="/app1/tag5916/projects/kmai-td-genie/.kmai-dev-agent/kmai_client.py"
HOST_PYTHON="/app1/tag5916/projects/kmai-td-genie/.venv/bin/python"

WORK_ROOT="$HOME/.uca-phase2c-safe-scope-v2"
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
from pathlib import Path

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

plan_payload = json.loads(
    (task_root / "phase-plan.json").read_text(encoding="utf-8")
)
report_payload = json.loads(
    (task_root / "final-report.json").read_text(encoding="utf-8")
)
summary_payload = json.loads(
    (observe_root / "run-summary.json").read_text(encoding="utf-8")
)

phase_plan = PhasePlan.model_validate(plan_payload)

base_sha = str(
    summary_payload.get("base_sha")
    or report_payload.get("base_sha")
    or ""
).strip()

plan_hash = str(summary_payload.get("plan_hash") or "").strip()

if not plan_hash:
    plan_hash = hashlib.sha256(
        phase_plan.model_dump_json().encode("utf-8")
    ).hexdigest()

if not base_sha:
    raise SystemExit("BASE_SHA_MISSING")

if len(plan_hash) != 64:
    raise SystemExit(f"PLAN_HASH_INVALID={plan_hash}")


def git(*args: str, check: bool = True):
    result = subprocess.run(
        ["git", "-C", str(repository), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if check and result.returncode != 0:
        raise SystemExit(
            "GIT_FAILED="
            + " ".join(args)
            + "\n"
            + result.stderr.strip()
        )
    return result


resolved = git("rev-parse", f"{ref}^{{commit}}").stdout.strip()

if resolved != base_sha:
    raise SystemExit(
        "BASE_SHA_MISMATCH\n"
        f"EXPECTED={base_sha}\n"
        f"ACTUAL={resolved}"
    )


approved_paths = (
    "kmai-td-genie/test/test_registry_contract.py",
    "kmai-td-genie/test/test_registry_cache.py",
    "kmai-td-genie/docs/adr/"
    "0002-phase2c-governed-semantic-plan-validator.md",
)

for path in approved_paths:
    exists = git(
        "cat-file",
        "-e",
        f"{base_sha}:{path}",
        check=False,
    ).returncode == 0

    if not exists:
        raise SystemExit(f"APPROVED_PATH_NOT_FOUND_AT_BASE={path}")


scope = {
    "manifest_version": "1",
    "base_sha": base_sha,
    "plan_hash": plan_hash,
    "allowed_changes": [
        {
            "path": approved_paths[0],
            "operation": "modify",
            "purpose": (
                "Add deterministic contract coverage for canonical "
                "full-snapshot identity and approved field-governance "
                "deferral behavior."
            ),
        },
        {
            "path": approved_paths[1],
            "operation": "modify",
            "purpose": (
                "Add deterministic synthetic contract tests for atomic "
                "snapshot publication, stale-writer rejection, cache "
                "identity, and stale-cache invalidation."
            ),
        },
        {
            "path": approved_paths[2],
            "operation": "modify",
            "purpose": (
                "Record the seven approved Phase 2C contracts and the "
                "exact Safe Mode scope, prerequisites, exclusions, "
                "stop conditions, and follow-up rules."
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
        "phase2c-contract-tests"
    ],
    "acceptance_criteria": [
        (
            "Only the three explicitly approved existing files change."
        ),
        (
            "The ADR records all seven approved Phase 2C architecture "
            "and contract decisions."
        ),
        (
            "The ADR explicitly records the Safe Mode scope, external "
            "prerequisite, exclusions, stop conditions, and later "
            "cross-ProductGroup test slice."
        ),
        (
            "Field-governance and metadata-classification enforcement "
            "remain explicitly deferred in Phase 2C."
        ),
        (
            "Canonical snapshot identity contract tests use deterministic "
            "synthetic data and validate semantic-versus-ordering changes."
        ),
        (
            "Registry-cache contract tests cover atomic publication, "
            "stale-writer rejection, cache identity, and deterministic "
            "stale-cache invalidation where supported by existing public "
            "interfaces."
        ),
        (
            "Focused tests pass without live data."
        ),
        (
            "No production source code changes."
        ),
    ],
    "max_patch_bytes": 250000,
    "max_changed_files": 3,
}


pytest_code = (
    "import sys; "
    "sys.path[:0]=["
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

Implement the first real Phase 2C documentation-and-contract-test Safe Mode
slice.

The previous read-only scope design proposed a fourth CREATE path under
`kmai-td-genie/docs/phase2c`, but deterministic preflight proved that parent
directory does not exist at Base SHA `{base_sha}`.

Human scope has therefore been intentionally NARROWED to three existing files.
Do not create the missing directory and do not propose a substitute path.

# Frozen identity

Base SHA: `{base_sha}`

Observe Plan Hash: `{plan_hash}`

# Seven approved Phase 2C decisions

1. Unit, contract, and standard CI tests use deterministic synthetic or mock
   data. Live governed data is not required.

2. Live governed data may be used only by a separate optional read-only
   environment-gated integration qualification profile.

3. Field governance and classification enforcement are explicitly deferred
   in Phase 2C. Classification may be absent, null, or unknown. Valid metadata
   is preserved and serialized. Classification does not grant authorization.
   Malformed governance/classification values are rejected.

4. Registry snapshots are immutable and publication is atomic. Readers see
   either the complete old snapshot or complete new snapshot, never partial
   state.

5. Stale writers are rejected by version conflict. Cache identity contains
   registry version or snapshot identity, and new publication deterministically
   invalidates stale cache entries.

6. Registry identity is derived from canonical full snapshot content.
   Semantic ProductGroup, Schema, Dataset, Field, or Relationship changes
   create a new identity. Ordering-only differences do not. Equal canonical
   content has equal identity.

7. Cross-ProductGroup relationships are explicit. Both endpoints must exist.
   Relationships do not expand authorization. Dataset authorization remains
   independent. Unknown endpoints are rejected.

# Exact approved changes

MODIFY `{approved_paths[0]}`

MODIFY `{approved_paths[1]}`

MODIFY `{approved_paths[2]}`

No other path is authorized.

# Documentation requirement

Use the existing ADR:

`{approved_paths[2]}`

to document:

- all seven approved decisions;
- exact three-file Safe Mode scope;
- external prerequisite;
- no internal dependency;
- excluded scope;
- stop conditions;
- production-code follow-up rule;
- later dedicated cross-ProductGroup relationship-test slice.

Do not create a separate Safe Mode scope document.

# Contract-test requirement

Update only the two approved existing test files.

Use repository conventions and deterministic synthetic fixtures.

Do not weaken or delete existing assertions.

# Internal dependencies

None.

# External prerequisite

The seven user-approved Phase 2C decisions above.

# Stop conditions

Stop without expanding scope if:

- any approved file is absent;
- a contract requires production source changes;
- a test requires live data, credentials, deployment, or environment changes;
- the approved contract contradicts an authoritative repository contract;
- a deterministic test proves a production implementation gap;
- any fourth file would need to change.

If a test proves a production gap, leave that failure as evidence for a later
separately approved production-code slice.

# Explicit exclusions

- all production source code;
- all files outside the three approved paths;
- deployment;
- authentication;
- environment configuration;
- credentials;
- live data;
- Git stage/commit/push/PR/merge;
- deployment;
- automatic scope expansion.

# Completion rule

Retain the sandbox patch only when:

- exact scope is preserved;
- focused tests pass;
- independent reviewer returns exactly PASS;
- source repository remains unchanged;
- no publication action occurs.
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

print("PHASE2C_SAFE_SCOPE_V2_PREFLIGHT_OK")
print(f"BASE_SHA={base_sha}")
print(f"PLAN_HASH={plan_hash}")
print(f"TASK_FILE={task_file}")
print(f"SCOPE_FILE={scope_file}")
print(f"POLICY_FILE={policy_file}")
print("APPROVED_CHANGES:")
for item in scope["allowed_changes"]:
    print(
        f"- {item['operation'].upper()} {item['path']}"
    )
PY


RUN_ID="phase2c-safe-v2-$(date -u +%Y%m%dT%H%M%SZ)-$$"
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
  --title "Phase 2C first real Safe Mode slice" \
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

status_file = Path(sys.argv[1])
state_root = sys.argv[2]
task_id = sys.argv[3]
thread_id = sys.argv[4]
scope_file = sys.argv[5]
policy_file = sys.argv[6]

payload = json.loads(status_file.read_text(encoding="utf-8"))

values = payload.get("values", {})
next_nodes = payload.get("next", [])
task = values.get("task", {})
manifest = task.get("manifest", {})

if next_nodes != ["scope_approval"]:
    raise SystemExit(
        "SAFE_SCOPE_APPROVAL_INTERRUPT_NOT_REACHED="
        + json.dumps(next_nodes)
    )

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
print("NO PATCH HAS BEEN GENERATED OR APPLIED.")
print("NO IMPLEMENTER HAS RUN YET.")
print("SOURCE REPOSITORY HAS NOT BEEN MODIFIED.")
print("============================================================")
PY
'
