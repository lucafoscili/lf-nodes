"""Focused contracts for MiniMax H3 structured prompt composition."""

from __future__ import annotations

import json

import pytest

from modules.workflow_runner.prompts.minimax_h3 import (
    compose_base_prompt,
    compose_full_reference_prompt,
)


_REFERENCE_SECTION_NAMES = (
    "subject_definitions",
    "summary",
    "retention_analysis",
    "detailed_description",
    "overall_soundscape",
    "non_diegetic_music",
)


def test_base_prompt_uses_official_order_and_omits_empty_sections() -> None:
    prompt = compose_base_prompt(
        instruction="  Use <Picture 1> as the first frame.  ",
        integrated_multimodal_description="  [Shot 1] The subject greets the viewer.  ",
        overall_soundscape="  Water and distant birds.  ",
        non_diegetic_music="   ",
    )

    assert prompt == (
        "Use <Picture 1> as the first frame.\n\n"
        "integrated_multimodal_description:\n"
        "[Shot 1] The subject greets the viewer.\n\n"
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
        subject_definitions="<Subject 1> is the person from <Picture 1>.",
        summary="The target is an identity-preserving greeting.",
        retention_analysis="<Subject 1>: fully_preserved",
        detailed_description="[Shot 1] <Subject 1> turns and waves.",
        overall_soundscape="Soft garden ambience.",
        non_diegetic_music="N/A",
    )

    assert prompt == (
        "subject_definitions:\n"
        "<Subject 1> is the person from <Picture 1>.\n\n"
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


@pytest.mark.parametrize("field_name", _REFERENCE_SECTION_NAMES)
@pytest.mark.parametrize("value", [None, "", " \t\r\n "])
def test_full_reference_prompt_rejects_every_blank_section(
    field_name: str, value: str | None
) -> None:
    fields = json.loads(_reference_response())
    fields[field_name] = value

    with pytest.raises(ValueError) as error:
        compose_full_reference_prompt(**fields)

    assert str(error.value) == (
        "Structured Ref2VA prompts require all six nonblank sections; "
        f"missing or blank: {field_name}"
    )


@pytest.mark.parametrize("field_name", _REFERENCE_SECTION_NAMES)
def test_full_reference_prompt_rejects_every_absent_section(
    field_name: str,
) -> None:
    fields = json.loads(_reference_response())
    del fields[field_name]

    with pytest.raises(ValueError, match=f"missing or blank: {field_name}$"):
        compose_full_reference_prompt(**fields)


def test_full_reference_prompt_reports_all_missing_sections() -> None:
    with pytest.raises(ValueError) as error:
        compose_full_reference_prompt()

    assert str(error.value) == (
        "Structured Ref2VA prompts require all six nonblank sections; "
        "missing or blank: " + ", ".join(_REFERENCE_SECTION_NAMES)
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
@pytest.mark.parametrize("raw", ["", "  custom:\r\nverbatim prompt\n  "])
def test_raw_override_is_exact_and_bypasses_structured_validation(
    composer, raw: str
) -> None:
    assert composer(
        raw_override=raw,
        overall_soundscape=" \r\n ",
        non_diegetic_music=123,
    ) == raw


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


def _reference_response(**overrides: str) -> str:
    values = {
        "subject_definitions": (
            "<Subject 1> is the person shown in <Picture 1>. "
            "<Picture 2> supplies the outfit."
        ),
        "summary": (
            "[reference generation + keyframe completion] "
            "Restage <Subject 1> with the referenced outfit."
        ),
        "retention_analysis": (
            "<Subject 1> (appears in [Shot 1], [Shot 2]): fully_preserved - "
            "the defining appearance and referenced outfit remain stable."
        ),
        "detailed_description": (
            "Naturalistic cinematic realism with restrained cool color. "
            "[Shot 1] <Subject 1> enters the room. "
            "[Shot 2] At 00:03.250, <Subject 1> turns toward the window."
        ),
        "overall_soundscape": "Footsteps and quiet room ambience.",
        "non_diegetic_music": "N/A",
    }
    values.update(overrides)
    return json.dumps(values)
