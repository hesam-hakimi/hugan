HOST_CLIENT="$(find "$HOME" /app1/"$USER" \
  -type f \
  -path '*/.kmai-dev-agent/kmai_client.py' \
  2>/dev/null | head -n 1)" \
&& echo "HOST_CLIENT=$HOST_CLIENT" \
&& test -n "$HOST_CLIENT" \
&& bash scripts/qualify-host-provider.sh \
     --host-client "$HOST_CLIENT"
