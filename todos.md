cd /home/tag5916/projects/universal-coding-agent/universal-coding-agent \
&& bash scripts/observe-project.sh \
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
