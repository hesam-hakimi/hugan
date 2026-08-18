cd /home/tag5916/projects/universal-coding-agent/universal-coding-agent \
&& .venv/bin/python -m compileall -q \
     src/universal_coding_agent/core/safe_models.py \
     tests/test_safe_models.py \
     tests/test_safe_graph.py \
&& .venv/bin/ruff check \
     src/universal_coding_agent/core/safe_models.py \
     tests/test_safe_models.py \
     tests/test_safe_graph.py \
&& .venv/bin/python -m pytest -q \
     tests/test_safe_models.py \
     tests/test_safe_patching.py \
     tests/test_safe_graph.py \
&& bash scripts/qualify-safe-host-provider.sh \
     --host-client /app1/tag5916/projects/kmai-td-genie/.kmai-dev-agent/kmai_client.py \
     --host-python /app1/tag5916/projects/kmai-td-genie/.venv/bin/python \
     --skip-install \
     --skip-quality \
     --state-root "$HOME/.uca-safe-host-runs/uca-safe-host-$(date -u +%Y%m%dT%H%M%SZ)"
