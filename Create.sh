set -Eeuo pipefail

cd /home/tag5916/projects/universal-coding-agent/universal-coding-agent

export UCA_SAFE_EDIT_PROTOCOL=v2-line-addressed

bash scripts/safe-workflow.sh approve \
  --context-file /home/tag5916/.uca-safe-runs/phase2c-line-addressed-v2-20260819T201541Z/safe-workflow-context.json
