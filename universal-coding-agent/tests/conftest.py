from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def isolate_safe_edit_protocol(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("UCA_SAFE_EDIT_PROTOCOL", raising=False)
