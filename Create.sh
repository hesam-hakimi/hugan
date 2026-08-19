set -Eeuo pipefail

cd /home/tag5916/projects/universal-coding-agent/universal-coding-agent

RUN_ROOT="/home/tag5916/.uca-safe-runs/phase2c-structured-testfix-v1-20260819T142102Z"
TASK_ID="safe-20260819T142102Z-2400636-task"
TASK_ROOT="$RUN_ROOT/artifacts/tasks/$TASK_ID"

echo
echo "============================================================"
echo "ANCHOR REPAIR DIAGNOSIS"
echo "============================================================"

for FILE in \
  safe-final-report.json \
  edit-validation.json \
  edit-repair-model-validation.json \
  edit-proposal-repaired.json \
  edit-validation-repaired.json
do
  echo
  echo "==================== $FILE ===================="

  if [[ -f "$TASK_ROOT/$FILE" ]]; then
    .venv/bin/python -m json.tool "$TASK_ROOT/$FILE"
  else
    echo "NOT_FOUND"
  fi
done

echo
echo "============================================================"
echo "SOURCE PRESERVATION CHECK FROM ORIGINAL APPROVE"
echo "============================================================"

for FIELD in head branch status worktrees
do
  BEFORE="$RUN_ROOT/source-${FIELD}-before-decision.txt"
  AFTER="$RUN_ROOT/source-${FIELD}-after-decision.txt"

  if [[ -f "$BEFORE" && -f "$AFTER" ]]; then
    if cmp -s "$BEFORE" "$AFTER"; then
      echo "SOURCE_${FIELD^^}_PRESERVED=YES"
    else
      echo "SOURCE_${FIELD^^}_PRESERVED=NO"
    fi
  else
    echo "SOURCE_${FIELD^^}_PRESERVED=NOT_RECORDED"
  fi
done

echo
echo "============================================================"
echo "ANCHOR_REPAIR_DIAGNOSIS_COMPLETE"
echo "============================================================"
