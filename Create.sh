RUN_ID="uca-smoke-$(date +%Y%m%d%H%M%S)"
TEST_ROOT="/tmp/${RUN_ID}-source"
STATE_ROOT="/tmp/${RUN_ID}-state"

git clone \
  --depth 1 \
  --single-branch \
  --branch feature/universal-coding-agent-mvp \
  https://github.com/hesam-hakimi/hugan.git \
  "$TEST_ROOT"

cd "$TEST_ROOT/universal-coding-agent"

echo "RUN_ID=$RUN_ID"
echo "TEST_ROOT=$TEST_ROOT"
echo "STATE_ROOT=$STATE_ROOT"
