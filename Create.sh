set -Eeuo pipefail

cd /home/tag5916/projects/universal-coding-agent/universal-coding-agent

export UCA_SAFE_EDIT_PROTOCOL=v2-line-addressed

STATE_ROOT="$HOME/.uca-safe-runs/phase2c-line-addressed-v2-$(date -u +%Y%m%dT%H%M%SZ)"

bash scripts/safe-workflow.sh start \
  --state-root "$STATE_ROOT" \
  --repository /app1/tag5916/projects/kmai-td-genie \
  --ref phase2/semantic-plan-contract-validator \
  --task-file /app1/tag5916/.uca-phase2c-safe-scope-v2/phase2c-safe-task.md \
  --scope-file /app1/tag5916/.uca-phase2c-safe-scope-v2/approved-scope.json \
  --policy-file /app1/tag5916/.uca-phase2c-safe-scope-v2/trusted-policy.json \
  --host-client /app1/tag5916/projects/kmai-td-genie/.kmai-dev-agent/kmai_client.py \
  --host-python /app1/tag5916/projects/kmai-td-genie/.venv/bin/python \
  --title "Phase 2C real Safe Mode - line-addressed structured edits v2"

echo
echo "PHASE2C_STATE_ROOT=$STATE_ROOT"
echo "UCA_SAFE_EDIT_PROTOCOL=$UCA_SAFE_EDIT_PROTOCOL"
