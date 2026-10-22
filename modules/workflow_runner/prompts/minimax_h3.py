"""Deterministic composers for MiniMax H3's official prompt structures.

MiniMax H3 ultimately receives one text prompt.  These helpers let callers
surface that prompt as focused UI fields while retaining an exact raw escape
hatch for advanced authoring.  They deliberately live outside the workflow
discovery packages so importing them cannot register or load a workflow.
"""

from __future__ import annotations

from typing import Optional


def _normalize(value: Optional[str], field_name: str) -> str:
    """Normalize a structured section without rewriting its prose."""

    if value is None:
        return ""
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string or None")
    return value.replace("\r\n", "\n").replace("\r", "\n").strip()


def _raw(raw_override: Optional[str]) -> Optional[str]:
    """Return a supplied raw prompt exactly, including surrounding whitespace."""

    if raw_override is None:
        return None
    if not isinstance(raw_override, str):
        raise TypeError("raw_override must be a string or None")
    return raw_override


def _labeled(name: str, value: str) -> str:
    return f"{name}:\n{value}"


def compose_base_prompt(
    *,
    integrated_multimodal_description: Optional[str] = None,
    instruction: Optional[str] = None,
    overall_soundscape: Optional[str] = None,
    non_diegetic_music: Optional[str] = None,
    raw_override: Optional[str] = None,
) -> str:
    """Compose an H3 T2V, I2V, or FL2V prompt in official section order.

    ``instruction`` is the optional unlabelled instruction that precedes the
    official ``integrated_multimodal_description`` block (for example, a
    first-frame or first-and-last-frame reference instruction).  Empty
    optional sections are omitted.  A supplied ``raw_override`` is returned
    exactly and bypasses all structured-field validation.
    """

    raw = _raw(raw_override)
    if raw is not None:
        return raw

    description = _normalize(
        integrated_multimodal_description,
        "integrated_multimodal_description",
    )
    if not description:
        raise ValueError("integrated_multimodal_description is required")

    sections = []
    normalized_instruction = _normalize(instruction, "instruction")
    if normalized_instruction:
        sections.append(normalized_instruction)

    sections.append(_labeled("integrated_multimodal_description", description))

    soundscape = _normalize(overall_soundscape, "overall_soundscape")
    if soundscape:
        sections.append(_labeled("overall_soundscape", soundscape))

    music = _normalize(non_diegetic_music, "non_diegetic_music")
    if music:
        sections.append(_labeled("non_diegetic_music", music))

    return "\n\n".join(sections)


def compose_full_reference_prompt(
    *,
    detailed_description: Optional[str] = None,
    subject_definitions: Optional[str] = None,
    summary: Optional[str] = None,
    retention_analysis: Optional[str] = None,
    overall_soundscape: Optional[str] = None,
    non_diegetic_music: Optional[str] = None,
    raw_override: Optional[str] = None,
) -> str:
    """Compose an H3 full-reference/R2V prompt in official section order.

    All six structured sections are required and must be nonblank.  A supplied
    ``raw_override`` is returned exactly and bypasses all structured-field
    validation.
    """

    raw = _raw(raw_override)
    if raw is not None:
        return raw

    values = (
        ("subject_definitions", subject_definitions),
        ("summary", summary),
        ("retention_analysis", retention_analysis),
        ("detailed_description", detailed_description),
        ("overall_soundscape", overall_soundscape),
        ("non_diegetic_music", non_diegetic_music),
    )
    normalized = {name: _normalize(value, name) for name, value in values}
    missing = [name for name, value in normalized.items() if not value]
    if missing:
        raise ValueError(
            "Structured Ref2VA prompts require all six nonblank sections; "
            "missing or blank: " + ", ".join(missing)
        )

    return "\n\n".join(_labeled(name, value) for name, value in normalized.items())


__all__ = [
    "compose_base_prompt",
    "compose_full_reference_prompt",
]
