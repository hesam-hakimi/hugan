#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

: "${UCA_TRUSTED_TEST_ADAPTER_PATH:?UCA_TRUSTED_TEST_ADAPTER_PATH must be set in the environment}"
: "${UCA_TRUSTED_TEST_PAUSABLE_FACTORY:?UCA_TRUSTED_TEST_PAUSABLE_FACTORY must be set in the environment}"

STATE_ROOT="${1:-$HOME/.uca-pretransfer-trusted-test-pause/$(date -u +%Y%m%dT%H%M%SZ)}"
mkdir -p "$STATE_ROOT"

python -m universal_coding_agent.testlab.trusted_test_pause_live \
  --state-root "$STATE_ROOT" \
  --source-root "$(git rev-parse --show-toplevel)" \
  --adapter-path "$UCA_TRUSTED_TEST_ADAPTER_PATH" \
  --pausable-factory "$UCA_TRUSTED_TEST_PAUSABLE_FACTORY"
