"""Reusable prompt composers for Workflow Runner integrations."""

from .minimax_h3 import (
    compose_base_prompt,
    compose_full_reference_prompt,
)

__all__ = [
    "compose_base_prompt",
    "compose_full_reference_prompt",
]
