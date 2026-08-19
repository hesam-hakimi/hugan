set -Eeuo pipefail

cd /home/tag5916/projects/universal-coding-agent/universal-coding-agent

RUN_ROOT="/home/tag5916/.uca-safe-runs/phase2c-structured-anchor-v1-20260819T121020Z"
TASK_ID="safe-20260819T121021Z-2341759-task"
TASK_ROOT="$RUN_ROOT/artifacts/tasks/$TASK_ID"

for FILE in \
  edit-validation.json \
  edit-validation-repaired.json \
  edit-repair-model-validation.json \
  test-results.json
do
  echo
  echo "============================================================"
  echo "$FILE"
  echo "============================================================"

  if [[ -f "$TASK_ROOT/$FILE" ]]; then
    .venv/bin/python -m json.tool "$TASK_ROOT/$FILE"
  else
    echo "NOT FOUND"
  fi
done
