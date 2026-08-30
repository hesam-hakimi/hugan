#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

: "${UCA_HOST_CLIENT_PATH:?UCA_HOST_CLIENT_PATH must be set in the environment}"
: "${UCA_HOST_PAUSABLE_COMPLETION_FACTORY:?UCA_HOST_PAUSABLE_COMPLETION_FACTORY must be set in the environment}"

STATE_ROOT="${1:-$HOME/.uca-pretransfer-host-pause/$(date -u +%Y%m%dT%H%M%SZ)}"
mkdir -p "$STATE_ROOT"

python -m universal_coding_agent.testlab.host_chat_pause_live \
  --state-root "$STATE_ROOT" \
  --source-root "$(git rev-parse --show-toplevel)" \
  --host-client-path "$UCA_HOST_CLIENT_PATH" \
  --pausable-factory "$UCA_HOST_PAUSABLE_COMPLETION_FACTORY"
