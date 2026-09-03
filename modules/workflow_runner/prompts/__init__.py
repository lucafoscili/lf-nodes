"""Reusable prompt composers for Workflow Runner integrations."""

from .minimax_h3 import (
    H3_PROMPT_MODES,
    H3_PROMPT_REPORT_SCHEMA,
    build_h3_prompt_writer_system,
    compile_h3_prompt_response,
    compose_base_prompt,
    compose_full_reference_prompt,
)

__all__ = [
    "H3_PROMPT_MODES",
    "H3_PROMPT_REPORT_SCHEMA",
    "build_h3_prompt_writer_system",
    "compile_h3_prompt_response",
    "compose_base_prompt",
    "compose_full_reference_prompt",
]
