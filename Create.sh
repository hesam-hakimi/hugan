# 1. Go to the Universal Coding Agent repo
cd /home/tag5916/projects/universal-coding-agent/universal-coding-agent

# 2. Compile
.venv/bin/python -m compileall -q src tests

# 3. Lint
.venv/bin/ruff check .

# 4. Unit tests
.venv/bin/python -m pytest -q

# 5. Safe Mode smoke test
bash scripts/safe-smoke.sh

# 6. Real KMAI host-provider qualification
# command will use the actual KMAI client/python paths

# 7. Final Phase 2C real Safe Mode run
# start → human approval → approve → final result
