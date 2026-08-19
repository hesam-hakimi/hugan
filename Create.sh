set -Eeuo pipefail

cd /home/tag5916/projects/universal-coding-agent/universal-coding-agent

POLICY="/app1/tag5916/.uca-phase2c-safe-scope-v2/trusted-policy.json"
BACKUP="${POLICY}.bak.$(date -u +%Y%m%dT%H%M%SZ)"

cp "$POLICY" "$BACKUP"

export POLICY

.venv/bin/python - <<'PY'
import json
import os
from pathlib import Path

from universal_coding_agent.core.safe_models import SafeModePolicy

policy_path = Path(os.environ["POLICY"])
payload = json.loads(policy_path.read_text(encoding="utf-8"))

profiles = payload.get("profiles", [])
profile = next(
    (
        item
        for item in profiles
        if item.get("profile_id") == "phase2c-contract-tests"
    ),
    None,
)

if profile is None:
    raise SystemExit("PHASE2C_PROFILE_NOT_FOUND")

python_code = (
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

# Validate Python syntax BEFORE saving it.
compile(
    python_code,
    "<phase2c-contract-tests>",
    "exec",
)

profile["argv"] = [
    "/app1/tag5916/projects/kmai-td-genie/.venv/bin/python",
    "-c",
    python_code,
]

# Validate the complete Safe Mode policy contract.
validated = SafeModePolicy.model_validate(payload)

policy_path.write_text(
    json.dumps(
        validated.model_dump(mode="json"),
        indent=2,
    ) + "\n",
    encoding="utf-8",
)

print("PHASE2C_TEST_POLICY_FIX_OK")
print("PROFILE_ID=" + profile["profile_id"])
print("PYTHON=" + profile["argv"][0])
print("PYTHON_CODE_SYNTAX=PASS")
print("SAFE_MODE_POLICY_SCHEMA=PASS")
print("SHELL_INVOCATION=DISABLED")
PY

echo
echo "BACKUP=$BACKUP"
echo "POLICY=$POLICY"
echo "============================================"
echo "PHASE2C_POLICY_PREFLIGHT_OK"
echo "============================================"
