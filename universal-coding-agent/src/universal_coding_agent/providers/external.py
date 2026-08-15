from __future__ import annotations

import importlib
import os
from collections.abc import Callable

from universal_coding_agent.providers.base import ModelProvider


DEFAULT_FACTORY_ENV = "UCA_MODEL_PROVIDER_FACTORY"


def load_provider(factory_path: str | None = None) -> ModelProvider:
    """Load `module:function` without importing a host application in the public core."""

    value = (factory_path or os.getenv(DEFAULT_FACTORY_ENV, "")).strip()
    if not value or ":" not in value:
        raise RuntimeError(
            f"set {DEFAULT_FACTORY_ENV}=<module>:<factory_function> or pass --provider-factory"
        )
    module_name, function_name = value.split(":", 1)
    if not module_name or not function_name:
        raise RuntimeError("provider factory must use module:function format")
    module = importlib.import_module(module_name)
    factory = getattr(module, function_name, None)
    if not callable(factory):
        raise RuntimeError(f"provider factory {value!r} is not callable")
    provider = _invoke_factory(factory)
    if not isinstance(provider, ModelProvider):
        raise RuntimeError("provider factory returned an incompatible object")
    return provider


def _invoke_factory(factory: Callable[[], object]) -> ModelProvider:
    return factory()  # type: ignore[return-value]
