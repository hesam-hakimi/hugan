#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

: "${OPENAI_API_KEY:?OPENAI_API_KEY must be set in the environment}"
: "${UCA_OPENAI_MODEL:?UCA_OPENAI_MODEL must be set in the environment}"

STATE_ROOT="${1:-$HOME/.uca-pretransfer-live/$(date -u +%Y%m%dT%H%M%SZ)}"
RUNS="${UCA_LIVE_RUNS:-1}"
MIN_SUCCESS_RATE="${UCA_LIVE_MIN_SUCCESS_RATE:-1.0}"
mkdir -p "$STATE_ROOT"

echo "PRETRANSFER_LIVE_OPENAI_START"
echo "MODEL=$UCA_OPENAI_MODEL"
echo "RUNS=$RUNS"
echo "STATE_ROOT=$STATE_ROOT"

python -m universal_coding_agent.testlab.live \
  --state-root "$STATE_ROOT" \
  --runs "$RUNS" \
  --min-success-rate "$MIN_SUCCESS_RATE"
