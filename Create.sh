set -Eeuo pipefail

cd /home/tag5916/projects/universal-coding-agent/universal-coding-agent

STATE_ROOT="$HOME/.uca-safe-host-runs/structured-edits-$(date -u +%Y%m%dT%H%M%SZ)"

bash scripts/qualify-safe-host-provider.sh \
  --host-client /app1/tag5916/projects/kmai-td-genie/.kmai-dev-agent/kmai_client.py \
  --host-python /app1/tag5916/projects/kmai-td-genie/.venv/bin/python \
  --state-root "$STATE_ROOT" \
  --skip-install \
  --skip-quality

echo
echo "QUALIFICATION_STATE_ROOT=$STATE_ROOT"
