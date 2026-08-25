"""Dependency-free JSON normalization shared by runtime and static tooling."""

from __future__ import annotations

from typing import Any


def json_safe(value: Any) -> Any:
    """Return a recursively JSON-serializable representation of ``value``."""

    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [json_safe(item) for item in value]
    return str(value)


__all__ = ["json_safe"]
