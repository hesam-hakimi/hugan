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
  tests/test_core.py \
  tests/test_model_line_addressing.py \
  tests/test_safe_models.py \
  tests/test_line_edit_protocol.py \
  tests/test_sharded_line_edit_protocol.py \
  tests/test_sharded_dependency_contracts.py \
  tests/test_discovered_safe_service.py \
  tests/test_pretransfer_lab.py \
  tests/test_openai_testlab_provider.py \
  tests/test_openai_background_cancellation_live.py \
  tests/test_openai_background_reconciliation_live.py \
  tests/test_remote_operation_reconciliation.py \
  tests/test_hard_reasoning_lab.py \
  tests/test_solution_discovery.py \
  tests/test_repository.py \
  tests/test_product_foundation.py \
  tests/test_lifecycle_reservations.py \
  tests/test_product_workspace_control.py \
  tests/test_safe_control.py \
  tests/test_requirement_draft_repair.py \
  tests/test_program_execution.py \
  tests/test_program_execution_qualification.py \
  tests/test_web_api.py \
  --junitxml "$STATE_ROOT/pretransfer-junit.xml"

echo "PRETRANSFER_LAB_PASS"
echo "DURABLE_LIFECYCLE_RESERVATION_PREFLIGHT_PASS"
echo "DURABLE_WORKER_OWNERSHIP_PREFLIGHT_PASS"
echo "EXPLICIT_LIFECYCLE_RECOVERY_PREFLIGHT_PASS"
echo "BOUNDED_LIFECYCLE_RECOVERY_INVENTORY_PREFLIGHT_PASS"
echo "INDEX_BACKED_LIFECYCLE_RECOVERY_CANDIDATE_PREFLIGHT_PASS"
echo "INDEX_BACKED_LIFECYCLE_RECOVERY_RECEIPT_PREFLIGHT_PASS"
echo "JUNIT=$STATE_ROOT/pretransfer-junit.xml"
