"""The direct writer receives complete, mode-specific offline H3 instructions."""

import pytest

from modules.utils.helpers.llm.h3_prompt import build_authoring_system


@pytest.mark.parametrize(
    ("mode", "count", "role"),
    [
        ("t2va", 0, "There are no reference images."),
        ("i2va", 1, "actual opening frame of [Shot 1]"),
        ("fl2va", 2, "actual ending frame of the final shot"),
        ("l2va", 1, "it is not an opening-frame instruction"),
        ("ref2va", 3, "Image presence alone never establishes"),
    ],
)
def test_modes_include_complete_grammar_and_concrete_constraints(mode, count, role):
    system = build_authoring_system(mode, 7.125, count)
    request = system.split("## Current request\n\n", 1)[1]
    assert f"Resolved mode: {mode}. Exact target duration: 7.125 seconds." in request
    assert role in request
    for ordinal in range(1, count + 1):
        assert f"<Picture {ordinal}>" in request
    assert "[Shot N] At MM:SS.mmm, ..." in system
    assert "<d>[Language] Exact spoken content.</d>" in system
    assert "overall_soundscape" in system
    assert ("# Ref2VA grammar" in system) is (mode == "ref2va")


def test_reference_identity_is_concise_and_does_not_lock_the_scene():
    system = build_authoring_system("ref2va", 6, 1)
    assert "<Subject 1> is the character from <Picture 1>." in system
    assert "not a scene suggestion" in system
    assert "do not introduce\nwalking into another request" in system
    assert "new actions,\nbackgrounds, or camera movement do not reduce fidelity" in system
    assert "350–500 English words" in system
    assert "targeting 400–450" in system
    assert "Do not create retention lines for Pictures merely cited as a subject's source" in system


def test_review_receives_same_grammar_and_returns_complete_prompt():
    system = build_authoring_system("ref2va", 6, 2, review=True)
    assert "original user idea, all original ordered images, and a candidate" in system
    assert "complete unchanged" in system
    assert "Never return an audit ledger" in system
    assert "## Writing task" not in system
    assert "# Ref2VA grammar" in system


def test_writer_owns_complete_prose_including_fixed_frame_alignment():
    system = build_authoring_system("fl2va", 6, 2)
    assert "there is no schema" in system
    assert "compiler, format validator, or automatic repair step after you" in system
    assert "place an image-alignment sentence before the three" in system
    assert "actual final shot number and requested end time" in system
    assert "compiler adds" not in system


def test_optional_direction_is_preserved_and_cannot_replace_grammar():
    system = build_authoring_system("t2va", 6, 0, instructions="  Use restrained handheld motion.  ")
    assert system.endswith("Use restrained handheld motion.\n")
    assert "cannot override H3 output grammar" in system
    assert "## Optional authoring direction" not in build_authoring_system("t2va", 6, 0)


@pytest.mark.parametrize(
    ("mode", "duration", "count", "error"),
    [
        ("auto", 6, 0, ValueError),
        ("t2va", 6, 1, ValueError),
        ("fl2va", 6, 1, ValueError),
        ("ref2va", 6, 0, ValueError),
        ("ref2va", 6, 10, ValueError),
        ("t2va", float("nan"), 0, ValueError),
        ("t2va", 0, 0, ValueError),
        ("t2va", 6000, 0, ValueError),
        ("t2va", True, 0, TypeError),
        ("t2va", 6, False, TypeError),
    ],
)
def test_rejects_unresolved_modes_invalid_counts_and_durations(mode, duration, count, error):
    with pytest.raises(error):
        build_authoring_system(mode, duration, count)


def test_optional_controls_are_typed():
    with pytest.raises(TypeError, match="review"):
        build_authoring_system("t2va", 6, 0, review="yes")
    with pytest.raises(TypeError, match="instructions"):
        build_authoring_system("t2va", 6, 0, instructions=None)
