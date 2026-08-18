cd /home/tag5916/projects/universal-coding-agent/universal-coding-agent

.venv/bin/python -m compileall -q src tests && \
.venv/bin/ruff check \
  src/universal_coding_agent/context/safe_compiler.py \
  src/universal_coding_agent/safe/patching.py \
  src/universal_coding_agent/orchestration/safe_graph.py \
  tests/test_safe_graph.py && \
.venv/bin/python -m pytest -q \
  tests/test_safe_models.py \
  tests/test_safe_patching.py \
  tests/test_safe_graph.py
