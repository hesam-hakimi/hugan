bash -lc '
set -Eeuo pipefail

cd /home/tag5916/projects/universal-coding-agent/universal-coding-agent

test -f src/universal_coding_agent/orchestration/structured_output.py
grep -q "external_dependencies" \
  src/universal_coding_agent/core/models.py
grep -q "invoke_structured" \
  src/universal_coding_agent/orchestration/graph.py
grep -q "test_structured_output_repairs_external_dependency_once" \
  tests/test_structured_output.py

.venv/bin/python -m compileall -q src tests

.venv/bin/python -m pytest -q \
  tests/test_core.py \
  tests/test_structured_output.py \
  tests/test_graph.py

bash scripts/observe-project.sh \
  --skip-install \
  --repository /app1/tag5916/projects/kmai-td-genie \
  --ref phase2/semantic-plan-contract-validator \
  --phase-id "Phase 2C acceptance remediation" \
  --title "Phase 2C read-only qualification" \
  --focus "canonical ProductGroup -> Schema -> Dataset hierarchy and mandatory schema membership" \
  --focus "governed registry-version identity and full snapshot-content identity" \
  --focus "field governance and classification metadata deferral" \
  --focus "cross-ProductGroup relationship behavior and dedicated test coverage" \
  --focus "registry-cache concurrency behavior and acceptance-gate stability" \
  --focus "public API, security, compatibility, and unchanged-scope evidence" \
  --host-client /app1/tag5916/projects/kmai-td-genie/.kmai-dev-agent/kmai_client.py
'
