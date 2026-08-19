#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

STATE_ROOT="${1:-$HOME/.uca-pretransfer-lab/$(date -u +%Y%m%dT%H%M%SZ)}"
mkdir -p "$STATE_ROOT"

echo "PRETRANSFER_LAB_START"
echo "STATE_ROOT=$STATE_ROOT"

python -m compileall -q src tests
ruff check .
env -u UCA_SAFE_EDIT_PROTOCOL python -m pytest -q \
  tests/test_model_line_addressing.py \
  tests/test_sharded_line_edit_protocol.py \
  tests/test_pretransfer_lab.py \
  tests/test_openai_testlab_provider.py \
  --junitxml "$STATE_ROOT/pretransfer-junit.xml"

echo "PRETRANSFER_LAB_PASS"
echo "JUNIT=$STATE_ROOT/pretransfer-junit.xml"
