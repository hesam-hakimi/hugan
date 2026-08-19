set -Eeuo pipefail

cd /home/tag5916/projects/universal-coding-agent/universal-coding-agent

echo "=== COMPILE ==="
.venv/bin/python -m compileall -q src tests

echo "=== LINT ==="
.venv/bin/ruff check .

echo "=== TESTS ==="
.venv/bin/python -m pytest -q

echo "=== SAFE MODE SMOKE ==="
bash scripts/safe-smoke.sh

echo
echo "============================================"
echo "STRUCTURED_EDIT_ANCHOR_REPAIR_LOCAL_GATES_OK"
echo "============================================"
