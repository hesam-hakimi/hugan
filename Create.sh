export UCA_SAFE_EDIT_PROTOCOL=v2-line-addressed

STATE_ROOT="$HOME/.uca-safe-host-runs/line-addressed-v2-$(date -u +%Y%m%dT%H%M%SZ)"

bash scripts/qualify-line-addressed-host-provider.sh \
  --host-client /app1/tag5916/projects/kmai-td-genie/.kmai-dev-agent/kmai_client.py \
  --host-python /app1/tag5916/projects/kmai-td-genie/.venv/bin/python \
  --state-root "$STATE_ROOT" \
  --skip-install \
  --skip-quality
