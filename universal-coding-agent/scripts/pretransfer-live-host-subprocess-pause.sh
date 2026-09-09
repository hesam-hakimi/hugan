#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

: "${UCA_HOST_CLIENT_PATH:?UCA_HOST_CLIENT_PATH must be set in the environment}"
: "${UCA_HOST_PYTHON:?UCA_HOST_PYTHON must be set in the environment}"
: "${UCA_HOST_SUBPROCESS_PAUSABLE_COMPLETION_FACTORY:?UCA_HOST_SUBPROCESS_PAUSABLE_COMPLETION_FACTORY must be set in the environment}"

STATE_ROOT="${1:-$HOME/.uca-pretransfer-host-subprocess-pause/$(date -u +%Y%m%dT%H%M%SZ)}"
mkdir -p "$STATE_ROOT"

"$UCA_HOST_PYTHON" -m universal_coding_agent.testlab.host_subprocess_pause_live \
  --state-root "$STATE_ROOT" \
  --source-root "$(git rev-parse --show-toplevel)" \
  --host-client-path "$UCA_HOST_CLIENT_PATH" \
  --host-python "$UCA_HOST_PYTHON" \
  --pausable-factory "$UCA_HOST_SUBPROCESS_PAUSABLE_COMPLETION_FACTORY"
