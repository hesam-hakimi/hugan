export PYTHONPATH="$PWD/src${PYTHONPATH:+:$PYTHONPATH}"

python3 - <<'PY'
import sys
from importlib.metadata import PackageNotFoundError, version

if sys.version_info < (3, 11):
    raise SystemExit(
        f"PYTHON_TOO_OLD: {sys.version.split()[0]} — Python 3.11+ is required"
    )

packages = (
    "pydantic",
    "langgraph",
    "langgraph-checkpoint-sqlite",
)

for package in packages:
    try:
        print(f"{package}={version(package)}")
    except PackageNotFoundError:
        raise SystemExit(f"MISSING_DEPENDENCY:{package}")

from langgraph.checkpoint.sqlite import SqliteSaver
from universal_coding_agent.core.models import TaskRequest
from universal_coding_agent.orchestration.graph import ObserveGraph

print("UCA_PREREQUISITES_OK")
PY
