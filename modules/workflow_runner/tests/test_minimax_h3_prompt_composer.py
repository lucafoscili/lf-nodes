"""Focused contracts for MiniMax H3 structured prompt composition."""

from __future__ import annotations

import pytest

from modules.workflow_runner.prompts.minimax_h3 import (
    compose_base_prompt,
    compose_full_reference_prompt,
)


def test_base_prompt_uses_official_order_and_omits_empty_sections() -> None:
    prompt = compose_base_prompt(
        instruction="  Use <Picture 1> as the first frame.  ",
        integrated_multimodal_description="  [Shot 1] Maeva greets Luca.  ",
        overall_soundscape="  Water and distant birds.  ",
        non_diegetic_music="   ",
    )

    assert prompt == (
        "Use <Picture 1> as the first frame.\n\n"
        "integrated_multimodal_description:\n"
        "[Shot 1] Maeva greets Luca.\n\n"
        "overall_soundscape:\n"
        "Water and distant birds."
    )


def test_base_prompt_can_contain_only_the_required_visual_description() -> None:
    assert compose_base_prompt(
        integrated_multimodal_description="A locked portrait shot."
    ) == (
        "integrated_multimodal_description:\n"
        "A locked portrait shot."
    )


def test_full_reference_prompt_uses_official_order() -> None:
    prompt = compose_full_reference_prompt(
        subject_definitions="<Subject 1> is Maeva from <Picture 1>.",
        summary="The target is an identity-preserving greeting.",
        retention_analysis="<Subject 1>: fully_preserved",
        detailed_description="[Shot 1] <Subject 1> turns and waves.",
        overall_soundscape="Soft garden ambience.",
        non_diegetic_music="N/A",
    )

    assert prompt == (
        "subject_definitions:\n"
        "<Subject 1> is Maeva from <Picture 1>.\n\n"
        "summary:\n"
        "The target is an identity-preserving greeting.\n\n"
        "retention_analysis:\n"
        "<Subject 1>: fully_preserved\n\n"
        "detailed_description:\n"
        "[Shot 1] <Subject 1> turns and waves.\n\n"
        "overall_soundscape:\n"
        "Soft garden ambience.\n\n"
        "non_diegetic_music:\n"
        "N/A"
    )


def test_full_reference_prompt_omits_empty_optional_sections() -> None:
    assert compose_full_reference_prompt(
        subject_definitions=" ",
        summary=None,
        retention_analysis="\n",
        detailed_description="A reference-guided camera move.",
    ) == (
        "detailed_description:\n"
        "A reference-guided camera move."
    )


@pytest.mark.parametrize(
    ("composer", "field_name"),
    [
        (compose_base_prompt, "integrated_multimodal_description"),
        (compose_full_reference_prompt, "detailed_description"),
    ],
)
def test_structured_prompt_requires_a_visual_description(
    composer, field_name: str
) -> None:
    with pytest.raises(ValueError, match=field_name):
        composer(**{field_name: " \r\n "})


@pytest.mark.parametrize(
    "composer",
    [compose_base_prompt, compose_full_reference_prompt],
)
def test_raw_override_is_exact_and_bypasses_structured_validation(composer) -> None:
    raw = "  custom:\r\nverbatim prompt\n  "
    assert composer(raw_override=raw) == raw


def test_structured_sections_normalize_line_endings() -> None:
    assert compose_base_prompt(
        integrated_multimodal_description="Shot one.\r\nShot two.\rShot three."
    ) == (
        "integrated_multimodal_description:\n"
        "Shot one.\nShot two.\nShot three."
    )


def test_non_string_values_fail_with_the_offending_field_name() -> None:
    with pytest.raises(TypeError, match="overall_soundscape"):
        compose_base_prompt(
            integrated_multimodal_description="A shot.",
            overall_soundscape=123,  # type: ignore[arg-type]
        )

    with pytest.raises(TypeError, match="raw_override"):
        compose_full_reference_prompt(
            raw_override=object(),  # type: ignore[arg-type]
        )
