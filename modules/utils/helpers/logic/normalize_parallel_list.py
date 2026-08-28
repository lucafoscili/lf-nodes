from __future__ import annotations

from typing import Any


def normalize_parallel_list(
    value: Any,
    expected_length: int,
    name: str,
    *,
    allow_singleton: bool = True,
) -> list[Any]:
    """Validate a parallel control list and apply explicit singleton broadcast."""

    if expected_length < 1:
        raise ValueError("expected_length must be at least 1.")
    items = value if isinstance(value, list) else [value]
    if not items or items == [None]:
        raise ValueError(f"{name} must contain at least one value.")
    if len(items) == expected_length:
        return items
    if allow_singleton and len(items) == 1:
        return items * expected_length
    policy = (
        f"one value to broadcast or exactly {expected_length} values"
        if allow_singleton
        else f"exactly {expected_length} values"
    )
    raise ValueError(f"{name} must contain {policy}; got {len(items)}.")
