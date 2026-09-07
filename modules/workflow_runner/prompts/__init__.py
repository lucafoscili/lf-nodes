"""Reusable prompt composers for Workflow Runner integrations."""

from .minimax_h3 import (
    H3_PROMPT_MODES,
    H3_PROMPT_REPORT_SCHEMA,
    build_h3_prompt_writer_system,
    compile_h3_prompt_response,
    compose_base_prompt,
    compose_full_reference_prompt,
)
from .minimax_h3_pipeline import (
    build_h3_planner_context,
    build_h3_prompt_planner_system,
    build_h3_prompt_reviewer_system,
    build_h3_review_context,
    build_h3_scope_classifier_system,
    build_h3_scope_context,
    build_h3_visual_inventory_system,
)

__all__ = [
    "H3_PROMPT_MODES",
    "H3_PROMPT_REPORT_SCHEMA",
    "build_h3_prompt_writer_system",
    "build_h3_planner_context",
    "build_h3_prompt_planner_system",
    "build_h3_prompt_reviewer_system",
    "build_h3_review_context",
    "build_h3_scope_classifier_system",
    "build_h3_scope_context",
    "build_h3_visual_inventory_system",
    "compile_h3_prompt_response",
    "compose_base_prompt",
    "compose_full_reference_prompt",
]
