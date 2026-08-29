from __future__ import annotations

import importlib
import os

from universal_coding_agent.source_control.base import SourceControlAdapter

DEFAULT_SOURCE_CONTROL_FACTORY_ENV = "UCA_SOURCE_CONTROL_ADAPTER_FACTORY"


def load_source_control_adapter(factory_path: str | None = None) -> SourceControlAdapter:
    """Load an explicitly configured `module:function` source-control adapter."""

    value = (factory_path or os.getenv(DEFAULT_SOURCE_CONTROL_FACTORY_ENV, "")).strip()
    if not value:
        raise RuntimeError("source-control adapter is disabled until explicitly configured")
    if value.count(":") != 1:
        raise RuntimeError("source-control adapter factory must use module:function format")
    module_name, function_name = value.split(":", 1)
    if not module_name or not function_name:
        raise RuntimeError("source-control adapter factory must use module:function format")
    module = importlib.import_module(module_name)
    factory = getattr(module, function_name, None)
    if not callable(factory):
        raise RuntimeError(f"source-control adapter factory {value!r} is not callable")
    adapter = factory()
    if not isinstance(adapter, SourceControlAdapter):
        raise RuntimeError("source-control adapter factory returned an incompatible object")
    return adapter
