"""Focused contracts for MiniMax H3 structured prompt composition."""

from __future__ import annotations

import json

import pytest

from modules.workflow_runner.prompts.minimax_h3 import (
    H3_PROMPT_REPORT_SCHEMA,
    build_h3_prompt_writer_system,
    compile_h3_prompt_response,
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


def _base_response(description: str = "[Shot 1] A quiet locked shot.") -> str:
    return json.dumps(
        {
            "integrated_multimodal_description": description,
            "overall_soundscape": "Soft room tone.",
            "non_diegetic_music": "N/A",
        }
    )


def test_final_h3_text_and_fenced_text_compile_like_legacy_section_json():
    fields = json.loads(_base_response())
    raw = "\n\n".join(f"{name}:\n{value}" for name, value in fields.items())
    expected, _ = compile_h3_prompt_response(json.dumps(fields), "t2va", 6, 0)
    for response in (raw, f"```text\n{raw}\n```", raw.replace("\n", "\r\n")):
        prompt, report = compile_h3_prompt_response(response, "t2va", 6, 0)
        assert prompt == expected
        assert report["sourceFormat"] == "h3_text"


def test_direct_text_rejects_duplicate_sections_and_commentary():
    raw = "integrated_multimodal_description:\n[Shot 1] Rain.\noverall_soundscape:\nRain.\nnon_diegetic_music:\nN/A"
    with pytest.raises(ValueError, match="repeated"):
        compile_h3_prompt_response(raw + "\noverall_soundscape:\nWind.", "t2va", 6, 0)
    with pytest.raises(ValueError, match="Return only"):
        compile_h3_prompt_response("Here is your prompt:\n" + raw, "t2va", 6, 0)
    with pytest.raises(ValueError, match="unexpected: subject_definitions"):
        compile_h3_prompt_response(raw + "\nsubject_definitions:\nExtra section.", "t2va", 6, 0)


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


def _base_plan(**overrides: object) -> str:
    values: dict[str, object] = {
        "shots": [
            {
                "start_seconds": 0,
                "description": "Rain moves across a locked window.",
                "dialogue": [],
            },
            {
                "start_seconds": 2.5,
                "description": "The camera pushes toward the glass.",
                "dialogue": [
                    {
                        "speaker": "Watcher",
                        "subject": None,
                        "voice_identity": (
                            "an off-screen adult with a low, hushed voice, "
                            "measured pace, and neutral accent"
                        ),
                        "cue": "says quietly",
                        "language": "English",
                        "text": "It is starting.",
                    }
                ],
            },
        ],
        "overall_soundscape": "Rain and soft room tone.",
        "non_diegetic_music": "N/A",
    }
    values.update(overrides)
    return json.dumps(values)


def _reference_plan(**overrides: object) -> str:
    values: dict[str, object] = {
        "style_lead": "Painterly fantasy with cool cathedral light.",
        "summary": (
            "Animate the warrior while preserving identity and final framing."
        ),
        "subjects": [
            {
                "definition": "A teal-haired elf warrior in silver-blue armor",
                "source_pictures": [1],
                "uses": [
                    {
                        "shot": 1,
                        "application": "sits calmly on the stone ledge",
                    },
                    {
                        "shot": 2,
                        "application": "turns toward the stained glass",
                    },
                ],
                "retention": {
                    "marker": "fully_preserved",
                    "rationale": "Her face, hair, eyes, and armor remain stable.",
                },
            }
        ],
        "picture_anchors": [
            {
                "picture": 2,
                "role": "last_frame",
                "definition": "The required closing composition",
                "uses": [
                    {
                        "shot": 2,
                        "application": "anchors the final framing",
                    }
                ],
                "retention": {
                    "marker": "fully_preserved",
                    "rationale": "The closing silhouette and framing remain stable.",
                },
            }
        ],
        "shots": [
            {
                "start_seconds": 0,
                "description": "A slow camera push begins through blue haze.",
                "dialogue": [],
            },
            {
                "start_seconds": 3.25,
                "description": "The camera settles as colored light shifts.",
                "dialogue": [],
            },
        ],
        "overall_soundscape": "Wind chimes and a low magical hum.",
        "non_diegetic_music": "Slow harp and cello with a gentle swell.",
    }
    values.update(overrides)
    return json.dumps(values)


def test_writer_system_owns_exact_schema_and_reference_context() -> None:
    system = build_h3_prompt_writer_system("ref2va", 8, 2)

    assert "Mode: ref2va. Target duration: 8.00 seconds." in system
    assert "Exactly 2 reference images are attached" in system
    assert "Return exactly one bare JSON object" in system
    example = json.loads(
        system[system.index("{\n") : system.index("\n}\n") + 2]
    )
    assert list(example) == [
        "style_lead",
        "summary",
        "subjects",
        "picture_anchors",
        "shots",
        "overall_soundscape",
        "non_diegetic_music",
    ]
    assert list(example["subjects"][0]) == [
        "definition",
        "source_pictures",
        "uses",
        "retention",
    ]
    assert list(example["shots"][0]) == [
        "start_seconds",
        "description",
        "dialogue",
    ]
    assert example["subjects"][0]["source_pictures"] == [1, 2]
    assert "compiler owns all H3 syntax" in system
    assert '"subject":1' in system
    assert '"voice_identity"' in system
    assert '"cue":"whispers softly"' in system
    assert '"picture":1,"role":"last_frame"' in system
    assert "compiler derives the official task prefix" in system
    assert "first is exactly 0" in system
    assert "fully_preserved" in system
    assert "Use picture_anchors only" in system
    assert "style_lead is one or two English sentences" in system
    assert "first_frame, keyframe, last_frame, storyboard" in system
    assert "Copy every user-supplied dialogue line verbatim" in system

    fl2va_system = build_h3_prompt_writer_system("fl2va", 8, 2)
    assert "Image 1 is the opening frame of the first shot" in fl2va_system
    assert "image 2 is the ending frame" in fl2va_system
    assert "style_lead owns the visual style" in system
    assert (
        "Shot 1 begins with visual style and initial composition"
        in fl2va_system
    )
    assert '"subject":null' in fl2va_system


def test_compile_semantic_base_plan_renders_all_h3_syntax() -> None:
    prompt, report = compile_h3_prompt_response(
        _base_plan(), "t2va", 6, 0
    )

    assert prompt == (
        "integrated_multimodal_description:\n"
        "[Shot 1] Rain moves across a locked window.\n\n"
        "[Shot 2] At 00:02.500, The camera pushes toward the glass. "
        "Dialogue: Watcher (S1), an off-screen adult with a low, hushed "
        "voice, measured pace, and neutral accent, says quietly: "
        "<d>[English] It is starting.</d>\n\n"
        "overall_soundscape:\nRain and soft room tone.\n\n"
        "non_diegetic_music:\nN/A"
    )
    assert report["shotCount"] == 2
    assert report["shotTimestamps"] == ["00:02.500"]
    assert report["dialogueCount"] == 1
    assert report["subjectOrdinals"] == []


@pytest.mark.parametrize(
    ("mode", "references", "preamble_fragment"),
    [
        ("i2va", 1, "<Picture 1> (from [Shot 1]) is fully referenced."),
        ("fl2va", 2, "Picture 2 (from Shot 2) aligns with"),
        ("l2va", 1, "<Picture 1> (from [Shot 2]) aligns with"),
    ],
)
def test_semantic_base_plan_keeps_mode_owned_reference_preamble(
    mode: str, references: int, preamble_fragment: str
) -> None:
    prompt, report = compile_h3_prompt_response(
        _base_plan(), mode, 6, references
    )

    assert preamble_fragment in prompt
    assert report["pictureOrdinals"] == list(range(1, references + 1))
    if mode in {"i2va", "fl2va"}:
        assert "[Shot 1] <Picture 1> defines the opening frame." in prompt
    if mode == "fl2va":
        description = "The camera pushes toward the glass."
        ending = "The final shot converges on <Picture 2> as its ending frame."
        assert prompt.index(description) < prompt.index(ending)
    if mode == "l2va":
        description = "The camera pushes toward the glass."
        ending = "The final shot converges on <Picture 1> as its ending frame."
        assert prompt.index(description) < prompt.index(ending)


def test_one_shot_fl2va_orders_opening_action_and_ending_frame() -> None:
    values = json.loads(_base_plan())
    values["shots"] = [
        {
            "start_seconds": 0,
            "description": "A dancer crosses the studio in one continuous take.",
            "dialogue": [],
        }
    ]

    prompt, _report = compile_h3_prompt_response(
        json.dumps(values), "fl2va", 6, 2
    )

    opening = "<Picture 1> defines the opening frame."
    action = "A dancer crosses the studio in one continuous take."
    ending = "The final shot converges on <Picture 2> as its ending frame."
    assert prompt.index(opening) < prompt.index(action) < prompt.index(ending)


def test_semantic_plan_assigns_speaker_ids_by_casefolded_first_use() -> None:
    values = json.loads(_base_plan())
    values["shots"][0]["dialogue"] = [
        {
            "speaker": "Watcher",
            "subject": None,
            "voice_identity": "a clear adult voice at a brisk pace",
            "cue": "calls out",
            "language": "English",
            "text": "Look.",
        }
    ]
    values["shots"][1]["dialogue"] = [
        {
            "speaker": "watcher",
            "subject": None,
            "voice_identity": "a clear adult voice at a brisk pace",
            "cue": "answers",
            "language": "English",
            "text": "There.",
        },
        {
            "speaker": "Guide",
            "subject": None,
            "voice_identity": "a warm adult voice at a measured pace",
            "cue": "urges",
            "language": "Italian",
            "text": "Andiamo.",
        },
    ]

    prompt, report = compile_h3_prompt_response(
        json.dumps(values), "t2va", 6, 0
    )

    assert (
        "Watcher (S1), a clear adult voice at a brisk pace, calls out: "
        "<d>[English] Look.</d>"
    ) in prompt
    assert "Watcher (S1) answers: <d>[English] There.</d>" in prompt
    assert (
        "Guide (S2), a warm adult voice at a measured pace, urges: "
        "<d>[Italian] Andiamo.</d>"
    ) in prompt
    assert report["dialogueCount"] == 3


def test_semantic_ref2va_dialogue_binds_speaker_to_subject() -> None:
    values = json.loads(_reference_plan())
    values["shots"][0]["dialogue"] = [
        {
            "speaker": "Elf warrior",
            "subject": 1,
            "voice_identity": (
                "an on-screen young adult woman with a low, breathy voice, "
                "measured pace, and neutral accent"
            ),
            "cue": "whispers softly",
            "language": "English",
            "text": "We should leave.",
        }
    ]
    values["shots"][1]["dialogue"] = [
        {
            "speaker": "Warrior",
            "subject": 1,
            "voice_identity": (
                "an on-screen young adult woman with a low, breathy voice, "
                "measured pace, and neutral accent"
            ),
            "cue": "answers firmly",
            "language": "English",
            "text": "Not yet.",
        }
    ]

    prompt, report = compile_h3_prompt_response(
        json.dumps(values), "ref2va", 6, 2
    )

    assert (
        "<Subject 1> (S1), an on-screen young adult woman with a low, "
        "breathy voice, measured pace, and neutral accent, whispers softly: "
        "<d>[English] We should leave.</d>"
    ) in prompt
    assert (
        "<Subject 1> (S1) answers firmly: <d>[English] Not yet.</d>"
        in prompt
    )
    assert "<Subject 1> (S2)" not in prompt
    assert report["dialogueCount"] == 2


@pytest.mark.parametrize(
    ("subject", "text", "message"),
    [
        (1, "Look.", "must be null when no tracked subjects exist"),
        (None, "Look", "must end with dialogue punctuation"),
    ],
)
def test_semantic_dialogue_rejects_invalid_binding_and_punctuation(
    subject: object, text: str, message: str
) -> None:
    values = json.loads(_base_plan())
    values["shots"][0]["dialogue"] = [
        {
            "speaker": "Watcher",
            "subject": subject,
            "voice_identity": "an off-screen adult with a steady low voice",
            "cue": "calls out",
            "language": "English",
            "text": text,
        }
    ]

    with pytest.raises(ValueError, match=message):
        compile_h3_prompt_response(json.dumps(values), "t2va", 6, 0)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("speaker", "Watcher (S7)", "compiler owns reserved H3 token"),
        ("speaker", "Dialogue: Phantom", "compiler owns reserved H3 token"),
        ("cue", "says (S8,S9) urgently", "compiler owns reserved H3 token"),
        ("cue", "says quietly: now", "must not contain a colon"),
    ],
)
def test_semantic_dialogue_rejects_compiler_owned_syntax(
    field: str, value: str, message: str
) -> None:
    values = json.loads(_base_plan())
    dialogue = values["shots"][1]["dialogue"][0]
    dialogue[field] = value

    with pytest.raises(ValueError, match=message):
        compile_h3_prompt_response(json.dumps(values), "t2va", 6, 0)


def test_semantic_dialogue_rejects_a_changed_voice_identity() -> None:
    values = json.loads(_base_plan())
    values["shots"][0]["dialogue"] = [
        {
            "speaker": "Watcher",
            "subject": None,
            "voice_identity": "a bright young voice at a rapid pace",
            "cue": "calls out",
            "language": "English",
            "text": "Look.",
        }
    ]

    with pytest.raises(ValueError, match="changes the stable voice identity"):
        compile_h3_prompt_response(json.dumps(values), "t2va", 6, 0)


def test_compile_semantic_ref2va_plan_renders_references_and_retention() -> None:
    prompt, report = compile_h3_prompt_response(
        _reference_plan(), "ref2va", 6, 2
    )

    assert prompt.startswith(
        "subject_definitions:\n"
        "<Subject 1> is defined as follows: "
        "A teal-haired elf warrior in silver-blue armor. "
        "Source reference: <Picture 1>.\n"
        "<Picture 2> is defined as a concrete ending-frame target "
        "for [Shot 2]: "
        "The required closing composition.\n\n"
        "summary:\n"
        "[reference generation + keyframe completion] Track <Subject 1>; "
        "apply <Picture 2> as a concrete ending-frame target. Animate the warrior"
    )
    assert (
        "<Subject 1> (all shots): fully_preserved - Her face, hair, eyes, "
        "and armor remain stable."
    ) in prompt
    assert (
        "<Picture 2> (appears in [Shot 2]): fully_preserved - The closing "
        "silhouette and framing remain stable."
    ) in prompt
    assert (
        "[Shot 1] <Subject 1> sits calmly on the stone ledge. "
        "A slow camera push begins"
    ) in prompt
    assert (
        "[Shot 2] At 00:03.250, <Subject 1> turns toward the stained glass. "
        "The camera settles as colored light shifts. The shot ends on "
        "<Picture 2>, which anchors the final framing."
    ) in prompt
    assert report["pictureOrdinals"] == [1, 2]
    assert report["subjectOrdinals"] == [1]
    assert report["shotCount"] == 2
    assert report["shotTimestamps"] == ["00:03.250"]


@pytest.mark.parametrize("collection", ["subjects", "picture_anchors"])
@pytest.mark.parametrize("definition", [".", "...", " \t—…!?\r\n ", "。"])
def test_semantic_ref2va_rejects_punctuation_only_definitions(
    collection: str, definition: str
) -> None:
    values = json.loads(_reference_plan())
    values[collection][0]["definition"] = definition

    with pytest.raises(ValueError) as error:
        compile_h3_prompt_response(json.dumps(values), "ref2va", 6, 2)

    assert str(error.value) == (
        f"Semantic plan {collection}[0].definition must contain at least one "
        "letter or number"
    )


@pytest.mark.parametrize(
    "definition",
    ["A teal-haired elf warrior in silver-blue armor", "青い甲冑の戦士"],
)
def test_semantic_ref2va_keeps_one_subject_with_multiple_sources(
    definition: str,
) -> None:
    values = json.loads(_reference_plan())
    values["picture_anchors"] = []
    values["subjects"][0]["definition"] = definition
    values["subjects"][0]["source_pictures"] = [1, 2]

    prompt, report = compile_h3_prompt_response(
        json.dumps(values), "ref2va", 6, 2
    )

    assert f"<Subject 1> is defined as follows: {definition}." in prompt
    assert "Source references: <Picture 1>, <Picture 2>." in prompt
    assert report["subjectOrdinals"] == [1]
    assert report["pictureOrdinals"] == [1, 2]


def test_semantic_ref2va_anchor_only_plan_keeps_all_six_sections() -> None:
    values = json.loads(_reference_plan())
    values["subjects"] = []
    values["picture_anchors"][0]["picture"] = 1

    prompt, report = compile_h3_prompt_response(
        json.dumps(values), "ref2va", 6, 1
    )

    assert prompt.startswith(
        "subject_definitions:\n<Picture 1> is defined as a concrete ending-frame "
        "target for [Shot 2]: The required closing composition."
    )
    assert "<Subject " not in prompt
    assert report["subjectOrdinals"] == []
    assert report["pictureOrdinals"] == [1]
    assert all(f"{name}:\n" in prompt for name in _REFERENCE_SECTION_NAMES)


def test_semantic_ref2va_task_is_derived_from_actual_reference_roles() -> None:
    subjects_only = json.loads(_reference_plan())
    subjects_only["picture_anchors"] = []
    prompt, _report = compile_h3_prompt_response(
        json.dumps(subjects_only), "ref2va", 6, 1
    )
    assert "[reference generation] Track <Subject 1>." in prompt

    anchors_only = json.loads(_reference_plan())
    anchors_only["subjects"] = []
    anchors_only["picture_anchors"][0]["picture"] = 1
    prompt, _report = compile_h3_prompt_response(
        json.dumps(anchors_only), "ref2va", 6, 1
    )
    assert (
        "[keyframe completion] Apply <Picture 1> as a concrete ending-frame "
        "target."
        in prompt
    )

    anchors_only["picture_anchors"][0]["role"] = "storyboard"
    prompt, _report = compile_h3_prompt_response(
        json.dumps(anchors_only), "ref2va", 6, 1
    )
    assert (
        "[reference generation] Use <Picture 1> as storyboard guidance."
        in prompt
    )


@pytest.mark.parametrize(
    ("role", "shot", "message"),
    [
        ("first_frame", 2, "first_frame must use exactly Shot 1"),
        ("last_frame", 1, "last_frame must use exactly the final shot"),
    ],
)
def test_semantic_ref2va_concrete_frame_roles_are_shot_bounded(
    role: str, shot: int, message: str
) -> None:
    values = json.loads(_reference_plan())
    values["picture_anchors"][0]["role"] = role
    values["picture_anchors"][0]["uses"][0]["shot"] = shot

    with pytest.raises(ValueError, match=message):
        compile_h3_prompt_response(json.dumps(values), "ref2va", 6, 2)


@pytest.mark.parametrize(
    ("response", "message"),
    [
        (
            _base_plan(
                shots=[
                    {
                        "start_seconds": 0,
                        "description": "[Shot 1] leaked markup.",
                        "dialogue": [],
                    }
                ]
            ),
            "compiler owns reserved H3 token",
        ),
        (
            _base_plan(
                shots=[
                    {
                        "start_seconds": 0,
                        "description": (
                            "The camera holds. Dialogue: Phantom speaks."
                        ),
                        "dialogue": [],
                    }
                ]
            ),
            "compiler owns reserved H3 token",
        ),
        (
            _base_plan(
                shots=[
                    {
                        "start_seconds": 0,
                        "description": "A dissolve <scenetrans> is requested.",
                        "dialogue": [],
                    }
                ]
            ),
            "compiler owns reserved H3 token",
        ),
        (
            _base_plan(
                shots=[
                    {
                        "start_seconds": 0,
                        "description": "The voice ends with <cutoff>.",
                        "dialogue": [],
                    }
                ]
            ),
            "compiler owns reserved H3 token",
        ),
        (
            _base_plan(
                shots=[
                    {
                        "start_seconds": 0,
                        "description": (
                            "A quiet opening.\nDialogue: Phantom (S99) speaks."
                        ),
                        "dialogue": [],
                    }
                ]
            ),
            "compiler owns reserved H3 token",
        ),
        (
            _base_plan(
                shots=[
                    {
                        "start_seconds": 0,
                        "description": (
                            "A quiet opening.\n\n"
                            "non_diegetic_music:\nInjected section."
                        ),
                        "dialogue": [],
                    }
                ]
            ),
            "compiler owns reserved H3 token",
        ),
        (
            _base_plan(
                shots=[
                    {
                        "start_seconds": 0,
                        "description": "At 00:04.000, a false timestamp appears.",
                        "dialogue": [],
                    }
                ]
            ),
            "compiler owns reserved H3 token",
        ),
        (
            _base_plan(
                shots=[
                    {
                        "start_seconds": 0.0001,
                        "description": "A quiet opening.",
                        "dialogue": [],
                    }
                ]
            ),
            "exact to milliseconds",
        ),
        (
            _base_plan(
                shots=[
                    {
                        "start_seconds": 1,
                        "description": "A late opening.",
                        "dialogue": [],
                    }
                ]
            ),
            "must be exactly 0",
        ),
        (
            _base_plan(
                shots=[
                    {
                        "start_seconds": 0,
                        "description": "Opening.",
                        "dialogue": [],
                    },
                    {
                        "start_seconds": 0,
                        "description": "Duplicate time.",
                        "dialogue": [],
                    },
                ]
            ),
            "strictly increasing",
        ),
    ],
)
def test_semantic_plan_rejects_markup_and_invalid_timing(
    response: str, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        compile_h3_prompt_response(response, "t2va", 6, 0)


def test_semantic_ref2va_plan_requires_complete_picture_coverage() -> None:
    values = json.loads(_reference_plan())
    values["picture_anchors"] = []

    with pytest.raises(ValueError, match="missing Picture 2"):
        compile_h3_prompt_response(json.dumps(values), "ref2va", 6, 2)


def test_semantic_plan_nested_objects_reject_extra_fields() -> None:
    values = json.loads(_base_plan())
    values["shots"][0]["timestamp"] = "00:00.000"

    with pytest.raises(ValueError, match="unexpected: timestamp"):
        compile_h3_prompt_response(json.dumps(values), "t2va", 6, 0)


def test_compile_t2va_bare_json_returns_exact_prompt_and_report() -> None:
    response = _base_response("[Shot 1] Rain moves across a locked window.")

    prompt, report = compile_h3_prompt_response(response, "t2va", 5.17, 0)

    assert prompt == (
        "integrated_multimodal_description:\n"
        "[Shot 1] Rain moves across a locked window.\n\n"
        "overall_soundscape:\nSoft room tone.\n\n"
        "non_diegetic_music:\nN/A"
    )
    assert report == {
        "schema": H3_PROMPT_REPORT_SCHEMA,
        "valid": True,
        "mode": "t2va",
        "sourceFormat": "bare_json",
        "sections": [
            "integrated_multimodal_description",
            "overall_soundscape",
            "non_diegetic_music",
        ],
        "durationSeconds": "5.17",
        "referenceImageCount": 0,
        "pictureOrdinals": [],
        "subjectOrdinals": [],
        "shotCount": 1,
        "shotTimestamps": [],
        "dialogueCount": 0,
        "characterCount": len(prompt),
    }


def test_compile_i2va_accepts_one_fenced_json_document_and_dialogue() -> None:
    response = _base_response(
        "[Shot 1] The person looks up. Dialogue:\n"
        "(S1) <d>[English] We should leave now.</d>"
    )

    prompt, report = compile_h3_prompt_response(
        f"```json\n{response}\n```",
        "i2va",
        5.166,
        1,
    )

    assert prompt.startswith(
        "For the target video, at 0.00 seconds into the target video, "
        "<Picture 1> (from [Shot 1]) is fully referenced.\n\n"
    )
    assert report["sourceFormat"] == "fenced_json"
    assert report["durationSeconds"] == "5.17"
    assert report["pictureOrdinals"] == [1]
    assert report["dialogueCount"] == 1


def test_compile_fl2va_uses_final_shot_and_two_decimal_duration() -> None:
    response = _base_response(
        "[Shot 1] The opening pose holds. "
        "[Shot 2] At 00:02.125, the subject starts walking. "
        "[Shot 3] At 00:06.750, the subject reaches the ending pose."
    )

    prompt, report = compile_h3_prompt_response(response, "fl2va", 8, 2)

    assert prompt.startswith(
        "How the reference pictures align with the target video — Picture 1 "
        "(from Shot 1) aligns with the 0.00-second mark of the target video; "
        "Picture 2 (from Shot 3) aligns with the 8.00-second mark of the target video."
    )
    assert report["shotCount"] == 3
    assert report["shotTimestamps"] == ["00:02.125", "00:06.750"]
    assert report["pictureOrdinals"] == [1, 2]


def test_compile_l2va_uses_final_shot_in_exact_preamble() -> None:
    response = _base_response(
        "[Shot 1] The camera follows an empty path. "
        "[Shot 2] At 00:04.000, the referenced subject enters the final pose."
    )

    prompt, _report = compile_h3_prompt_response(response, "l2va", 6, 1)

    assert prompt.startswith(
        "How the reference pictures align with the target video — "
        "<Picture 1> (from [Shot 2]) aligns with the 6.00-second mark "
        "of the target video."
    )


def test_compile_ref2va_uses_official_order_and_semantic_report() -> None:
    prompt, report = compile_h3_prompt_response(
        _reference_response(),
        "ref2va",
        8,
        2,
    )

    assert prompt.startswith(
        "subject_definitions:\n<Subject 1> is the person shown in <Picture 1>."
    )
    headers = [
        "subject_definitions:\n",
        "summary:\n",
        "retention_analysis:\n",
        "detailed_description:\n",
        "overall_soundscape:\n",
        "non_diegetic_music:\n",
    ]
    assert [prompt.index(header) for header in headers] == sorted(
        prompt.index(header) for header in headers
    )
    assert report["pictureOrdinals"] == [1, 2]
    assert report["subjectOrdinals"] == [1]
    assert report["shotTimestamps"] == ["00:03.250"]


def test_compile_ref2va_canonicalizes_plain_picture_provenance() -> None:
    prompt, report = compile_h3_prompt_response(
        _reference_response(
            subject_definitions=(
                "<Subject 1> is the person shown in Picture 1. "
                "<Picture 2> supplies the outfit."
            )
        ),
        "ref2va",
        8,
        2,
    )

    assert "shown in <Picture 1>" in prompt
    assert "shown in Picture 1" not in prompt
    assert report["pictureOrdinals"] == [1, 2]


def test_compile_ref2va_requires_and_preserves_official_style_lead() -> None:
    style_lead = "Tactile 35mm realism with cool, restrained color."
    prompt, report = compile_h3_prompt_response(
        _reference_response(
            detailed_description=(
                f"{style_lead} [Shot 1] <Subject 1> walks into frame."
            )
        ),
        "ref2va",
        8,
        2,
    )

    assert f"detailed_description:\n{style_lead}\n" not in prompt
    assert f"detailed_description:\n{style_lead} [Shot 1]" in prompt
    assert report["shotCount"] == 1


def test_compile_ref2va_rejects_a_missing_style_lead() -> None:
    with pytest.raises(ValueError, match="style lead before"):
        compile_h3_prompt_response(
            _reference_response(
                detailed_description=(
                    "[Shot 1] <Subject 1> walks into frame."
                )
            ),
            "ref2va",
            8,
            2,
        )


def test_compile_ref2va_accepts_picture_only_keyframe_definitions() -> None:
    response = json.dumps(
        {
            "subject_definitions": (
                "<Picture 1> is the opening harbor composition and lighting.\n"
                "<Picture 2> is the closing crane silhouette and framing."
            ),
            "summary": (
                "[keyframe completion] Connect the two concrete keyframes "
                "with one continuous camera move."
            ),
            "retention_analysis": (
                "<Picture 1> ([Shot 1] first frame): fully_preserved - the "
                "opening composition is retained.\n"
                "<Picture 2> ([Shot 2] last frame): fully_preserved - the "
                "closing composition is retained."
            ),
            "detailed_description": (
                "Tactile cinematic realism with cool harbor light. "
                "[Shot 1] <Picture 1> establishes the misty harbor. "
                "[Shot 2] At 00:04.000, the camera settles into <Picture 2>."
            ),
            "overall_soundscape": "Water, rigging, and a distant bell.",
            "non_diegetic_music": "N/A",
        }
    )

    prompt, report = compile_h3_prompt_response(response, "ref2va", 6, 2)

    assert "<Picture 1> ([Shot 1] first frame): fully_preserved" in prompt
    assert report["subjectOrdinals"] == []
    assert report["pictureOrdinals"] == [1, 2]


@pytest.mark.parametrize(
    ("response", "message"),
    [
        ("", "response is empty"),
        ("[]", "one JSON object"),
        ("before\n```json\n{}\n```", "only one bare"),
        ("```yaml\n{}\n```", "only one bare"),
        ('{"a": 1, "a": 2}', "repeats JSON field"),
        ("{not json}", "not valid JSON"),
    ],
)
def test_response_document_must_be_one_unambiguous_json_object(
    response: str, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        compile_h3_prompt_response(response, "t2va", 5, 0)


def test_bare_json_may_contain_literal_code_fence_text() -> None:
    values = json.loads(_base_response())
    values["non_diegetic_music"] = "A dry ``` click marks the edit."

    prompt, report = compile_h3_prompt_response(
        json.dumps(values), "t2va", 5, 0
    )

    assert "A dry ``` click marks the edit." in prompt
    assert report["sourceFormat"] == "bare_json"


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ({"non_diegetic_music": None}, "must be a string"),
        ({"overall_soundscape": "  "}, "must not be blank"),
        ({"extra": "value"}, "unexpected: extra"),
    ],
)
def test_response_fields_are_exact_nonblank_strings(
    mutation: dict[str, object], message: str
) -> None:
    values = json.loads(_base_response())
    values.update(mutation)

    with pytest.raises(ValueError, match=message):
        compile_h3_prompt_response(json.dumps(values), "t2va", 5, 0)

    values = json.loads(_base_response())
    values.pop("overall_soundscape")
    with pytest.raises(ValueError, match="missing: overall_soundscape"):
        compile_h3_prompt_response(json.dumps(values), "t2va", 5, 0)


@pytest.mark.parametrize(
    ("description", "message"),
    [
        ("No shot marker.", "begin with exact"),
        ("[shot 1] Wrong case.", "Malformed shot tag"),
        ("[Shot 1] Start. [Shot 3] At 00:02.000, gap.", "contiguous order"),
        ("[Shot 1] At 0:00.1, start.", "must not include a timestamp"),
        ("[Shot 1] Start. [Shot 2] At 0:2.000, bad.", "must be followed"),
        ("[Shot 1] Start. [Shot 2] At 0:02.000 next.", "must be followed"),
        ("[Shot 1] Start. [Shot 2] At 0:02.0000, bad.", "must be followed"),
        (
            "[Shot 1] Start. [Shot 2] At 0:02.0, next. "
            "[Shot 3] At 0:02.00, same.",
            "strictly increasing",
        ),
        ("[Shot 1] Start. [Shot 2] At 0:05.0, late.", "earlier than"),
    ],
)
def test_shot_chronology_is_exact_and_bounded(
    description: str, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        compile_h3_prompt_response(_base_response(description), "t2va", 5, 0)


def test_qwen_shot_timestamp_spellings_compile_to_exact_h3_syntax() -> None:
    response = _reference_response(
        detailed_description=(
            "Painterly cinematic fantasy with cool cathedral light. "
            "[Shot 1] At 0:00.0, <Subject 1> sits calmly on a stone ledge. "
            "[Shot 2] At 0:02.5, <Subject 1> turns toward the window. "
            "[Shot 3] At 0:04.8, the camera closes on <Subject 1>."
        )
    )

    prompt, report = compile_h3_prompt_response(response, "ref2va", 6, 2)

    assert "[Shot 1] <Subject 1> sits" in prompt
    assert "[Shot 1] At" not in prompt
    assert "[Shot 2] At 00:02.500," in prompt
    assert "[Shot 3] At 00:04.800," in prompt
    assert report["shotCount"] == 3
    assert report["shotTimestamps"] == ["00:02.500", "00:04.800"]


def test_canonical_zero_timestamp_after_shot_one_is_removed() -> None:
    prompt, report = compile_h3_prompt_response(
        _base_response("[Shot 1] At 00:00.000, rain begins."),
        "t2va",
        5,
        0,
    )

    assert "[Shot 1] rain begins." in prompt
    assert "[Shot 1] At" not in prompt
    assert report["shotTimestamps"] == []


@pytest.mark.parametrize(
    ("overrides", "reference_count", "message"),
    [
        (
            {"subject_definitions": "<Subject 1> comes from <picture 1>."},
            1,
            "Malformed Picture tag",
        ),
        (
            {"subject_definitions": "<Subject 1> comes from <Picture 2>."},
            1,
            "has no attached image",
        ),
        (
            {"subject_definitions": "<Subject 1> comes from <Video 1>."},
            1,
            "references are unsupported",
        ),
        (
            {
                "subject_definitions": (
                    "<Subject 1> comes from <Picture 1>."
                ),
                "detailed_description": (
                    "Clean studio realism. [Shot 1] <Subject 1> wears the "
                    "outfit shown in <Picture 2>."
                ),
            },
            2,
            "missing <Picture 2>",
        ),
        (
            {
                "subject_definitions": (
                    "<Picture 1> is the opening frame and merely mentions "
                    "<Picture 2>."
                ),
                "retention_analysis": (
                    "<Picture 1> ([Shot 1]): fully_preserved - the opening "
                    "frame remains stable."
                ),
                "detailed_description": (
                    "Clean studio realism. [Shot 1] <Picture 1> anchors the "
                    "composition while <Picture 2> is mentioned."
                ),
            },
            2,
            "missing <Picture 2>",
        ),
    ],
)
def test_ref2va_picture_tags_are_canonical_bounded_and_complete(
    overrides: dict[str, str],
    reference_count: int,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        compile_h3_prompt_response(
            _reference_response(**overrides),
            "ref2va",
            8,
            reference_count,
        )


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        (
            {
                "subject_definitions": (
                    "<subject 1> comes from <Picture 1>; <Picture 2> supplies "
                    "wardrobe."
                )
            },
            "Malformed Subject tag",
        ),
        (
            {
                "subject_definitions": (
                    "<Subject 1> comes from <Picture 1>.\n"
                    "<Subject 3> comes from <Picture 2>."
                )
            },
            "contiguous starting",
        ),
        (
            {
                "detailed_description": (
                    "Clean studio realism. [Shot 1] <Subject 2> appears beside "
                    "<Subject 1>."
                )
            },
            "undefined <Subject 2>",
        ),
        (
            {
                "subject_definitions": (
                    "General reference notes.\n"
                    "<Subject 1> comes from <Picture 1>; <Picture 2> supplies "
                    "wardrobe."
                )
            },
            "Each nonblank subject_definitions line",
        ),
        (
            {
                "detailed_description": (
                    "Clean studio realism. [Shot 1] The person enters."
                )
            },
            "detailed_description must use every defined subject",
        ),
        (
            {
                "subject_definitions": (
                    "<Subject 1> comes from <Picture 1> and mentions "
                    "<Subject 2>; <Picture 2> supplies wardrobe."
                )
            },
            "undefined <Subject 2>",
        ),
    ],
)
def test_ref2va_subjects_are_canonical_defined_and_used(
    overrides: dict[str, str], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        compile_h3_prompt_response(
            _reference_response(**overrides), "ref2va", 8, 2
        )


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"summary": "Restage the subject."}, "exact task prefix"),
        ({"summary": "[reference_generation] Restage."}, "exact task prefix"),
        (
            {
                "retention_analysis": (
                    "<Subject 1> (all shots): Fully_Preserved - identity "
                    "remains stable."
                )
            },
            "Invalid retention marker",
        ),
        (
            {
                "retention_analysis": (
                    "<Subject 1> (all shots): fully preserved - identity "
                    "remains stable."
                )
            },
            "Invalid retention marker",
        ),
        (
            {
                "retention_analysis": (
                    "<Subject 1> arbitrary scope: fully_preserved rationale"
                )
            },
            "Each retention_analysis line",
        ),
        (
            {
                "retention_analysis": (
                    "<Subject 1> (all shots): appearance_retained - identity "
                    "remains stable."
                )
            },
            "Invalid retention marker",
        ),
        (
            {
                "retention_analysis": (
                    "<Subject 1> (scope): fully_preserved - identity remains "
                    "stable."
                )
            },
            "concrete retention scope",
        ),
        (
            {
                "retention_analysis": (
                    "<Subject 1> (all shots): fully_preserved - rationale"
                )
            },
            "concrete rationale",
        ),
    ],
)
def test_ref2va_task_and_retention_vocabulary_is_exact(
    overrides: dict[str, str], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        compile_h3_prompt_response(
            _reference_response(**overrides), "ref2va", 8, 2
        )


def test_ref2va_summary_accepts_punctuation_after_exact_task_prefix() -> None:
    prompt, report = compile_h3_prompt_response(
        _reference_response(
            summary=(
                "[reference generation + keyframe completion]. "
                "Restage <Subject 1> with the referenced outfit."
            )
        ),
        "ref2va",
        8,
        2,
    )

    assert "[reference generation + keyframe completion]. Restage" in prompt
    assert report["valid"] is True


def test_retention_entries_cannot_be_copied_into_detailed_description() -> None:
    with pytest.raises(ValueError, match="only valid in retention_analysis"):
        compile_h3_prompt_response(
            _reference_response(
                detailed_description=(
                    "Clean studio realism. [Shot 1] <Subject 1> walks in.\n"
                    "<Subject 1> (all shots): fully_preserved - identity is stable."
                )
            ),
            "ref2va",
            8,
            2,
        )


def test_each_defined_subject_needs_its_own_canonical_retention_entry() -> None:
    with pytest.raises(ValueError, match="invented_marker"):
        compile_h3_prompt_response(
            _reference_response(
                subject_definitions=(
                    "<Subject 1> is the person in <Picture 1>.\n"
                    "<Subject 2> is the outfit in <Picture 2>."
                ),
                detailed_description=(
                    "Clean studio realism. [Shot 1] <Subject 1> wears "
                    "<Subject 2> while walking into frame."
                ),
                retention_analysis=(
                    "<Subject 1> ([Shot 1]): fully_preserved - identity is "
                    "stable.\n"
                    "<Subject 2> ([Shot 1]): invented_marker - the outfit is "
                    "visible."
                ),
            ),
            "ref2va",
            8,
            2,
        )


def test_each_defined_subject_needs_a_retention_line() -> None:
    with pytest.raises(ValueError, match="missing <Subject 2>"):
        compile_h3_prompt_response(
            _reference_response(
                subject_definitions=(
                    "<Subject 1> is the person in <Picture 1>.\n"
                    "<Subject 2> is the outfit in <Picture 2>."
                ),
                detailed_description=(
                    "Clean studio realism. [Shot 1] <Subject 1> wears "
                    "<Subject 2> while walking into frame."
                ),
            ),
            "ref2va",
            8,
            2,
        )


def test_standalone_picture_must_be_used_in_timeline_and_retention() -> None:
    with pytest.raises(ValueError, match="standalone Picture"):
        compile_h3_prompt_response(
            _reference_response(
                subject_definitions=(
                    "<Subject 1> is the person in <Picture 1>.\n"
                    "<Picture 2> is a required closing composition."
                )
            ),
            "ref2va",
            8,
            2,
        )

    with pytest.raises(ValueError, match="missing <Picture 2>"):
        compile_h3_prompt_response(
            _reference_response(
                subject_definitions=(
                    "<Subject 1> is the person in <Picture 1>.\n"
                    "<Picture 2> is a required closing composition."
                ),
                detailed_description=(
                    "Clean studio realism. [Shot 1] <Subject 1> enters. "
                    "[Shot 2] At 00:04.000, the camera matches <Picture 2>."
                ),
            ),
            "ref2va",
            8,
            2,
        )


@pytest.mark.parametrize(
    "dialogue",
    [
        "<d>[English] </d>",
        "<d>[] Hello.</d>",
        "<D>[English] Hello.</D>",
        "<d>[English] Hello.",
        "</d>",
        "<d>[English] Outer <d>[Italian] Inner.</d></d>",
    ],
)
def test_dialogue_tags_must_be_balanced_exact_and_nonblank(dialogue: str) -> None:
    with pytest.raises(ValueError, match="Dialogue tags"):
        compile_h3_prompt_response(
            _base_response(f"[Shot 1] A speaker says {dialogue}"),
            "t2va",
            5,
            0,
        )


def test_dialogue_validation_covers_every_response_field() -> None:
    values = json.loads(_base_response())
    values["overall_soundscape"] = "A malformed <d>[English] whisper."

    with pytest.raises(ValueError, match="Dialogue tags"):
        compile_h3_prompt_response(json.dumps(values), "t2va", 5, 0)

    values = json.loads(_base_response())
    values["non_diegetic_music"] = "<d>[English] Even valid dialogue is misplaced.</d>"
    with pytest.raises(ValueError, match="only valid in integrated"):
        compile_h3_prompt_response(json.dumps(values), "t2va", 5, 0)


def test_compiled_prompt_has_a_hard_character_limit() -> None:
    response = _base_response("[Shot 1] " + "x" * 7000)

    with pytest.raises(ValueError, match="maximum is 7000"):
        compile_h3_prompt_response(response, "t2va", 5, 0)


@pytest.mark.parametrize(
    ("mode", "duration", "references", "error_type", "message"),
    [
        ("unknown", 5, 0, ValueError, "mode must be one of"),
        ("T2VA", 5, 0, ValueError, "mode must be one of"),
        ("t2va", 0, 0, ValueError, "greater than 0"),
        ("t2va", float("nan"), 0, ValueError, "greater than 0"),
        ("t2va", 5, 1, ValueError, "exactly 0 reference images"),
        ("i2va", 5, 0, ValueError, "exactly 1 reference image"),
        ("fl2va", 5, 1, ValueError, "exactly 2 reference images"),
        ("l2va", 5, 2, ValueError, "exactly 1 reference image"),
        ("ref2va", 5, 0, ValueError, "between 1 and 9"),
        ("ref2va", 5, 10, ValueError, "between 1 and 9"),
        ("t2va", True, 0, TypeError, "finite number"),
        ("t2va", 5, True, TypeError, "must be an integer"),
    ],
)
def test_writer_request_contract_is_strict(
    mode: str,
    duration: object,
    references: object,
    error_type: type[Exception],
    message: str,
) -> None:
    with pytest.raises(error_type, match=message):
        build_h3_prompt_writer_system(
            mode,
            duration,  # type: ignore[arg-type]
            references,  # type: ignore[arg-type]
        )
