cat > /tmp/uca_fake_provider.py <<'PY'
from universal_coding_agent.providers.fake import FakeModelProvider


def create_provider():
    return FakeModelProvider()
PY
