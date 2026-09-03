"""Deterministic composers for MiniMax H3's official prompt structures.

MiniMax H3 ultimately receives one text prompt.  These helpers let callers
surface that prompt as focused UI fields while retaining an exact raw escape
hatch for advanced authoring.  They deliberately live outside the workflow
discovery packages so importing them cannot register or load a workflow.
"""

from __future__ import annotations

import json
import math
import re
from decimal import Decimal, InvalidOperation
from typing import Any, Optional


H3_PROMPT_REPORT_SCHEMA = "lf.workflow_runner.minimax_h3.prompt_report.v1"
H3_PROMPT_MODES = ("t2va", "i2va", "fl2va", "l2va", "ref2va")

_MAX_PROMPT_CHARS = 7000
_MAX_REFERENCE_IMAGES = 9
_BASE_FIELDS = (
    "integrated_multimodal_description",
    "overall_soundscape",
    "non_diegetic_music",
)
_REFERENCE_FIELDS = (
    "subject_definitions",
    "summary",
    "retention_analysis",
    "detailed_description",
    "overall_soundscape",
    "non_diegetic_music",
)
_MODE_REFERENCE_COUNTS = {
    "t2va": 0,
    "i2va": 1,
    "fl2va": 2,
    "l2va": 1,
}
_REFERENCE_TASKS = (
    "reference generation",
    "keyframe completion",
    "reference generation + keyframe completion",
    "keyframe completion + reference generation",
)
_BASE_PLAN_FIELDS = (
    "shots",
    "overall_soundscape",
    "non_diegetic_music",
)
_REFERENCE_PLAN_FIELDS = (
    "style_lead",
    "summary",
    "subjects",
    "picture_anchors",
    "shots",
    "overall_soundscape",
    "non_diegetic_music",
)
_SHOT_PLAN_FIELDS = ("start_seconds", "description", "dialogue")
_DIALOGUE_PLAN_FIELDS = (
    "speaker",
    "subject",
    "voice_identity",
    "cue",
    "language",
    "text",
)
_SUBJECT_PLAN_FIELDS = (
    "definition",
    "source_pictures",
    "uses",
    "retention",
)
_PICTURE_ANCHOR_PLAN_FIELDS = (
    "picture",
    "role",
    "definition",
    "uses",
    "retention",
)
_USE_PLAN_FIELDS = ("shot", "application")
_RETENTION_PLAN_FIELDS = ("marker", "rationale")
_RETENTION_MARKERS = (
    "fully_preserved",
    "partially_preserved",
    "attribute_transfer",
    "weak_reference",
)
_PICTURE_ANCHOR_ROLES = (
    "first_frame",
    "keyframe",
    "last_frame",
    "storyboard",
    "composition_reference",
)
_CONCRETE_FRAME_ROLES = frozenset(
    {"first_frame", "keyframe", "last_frame"}
)
_PICTURE_ANCHOR_ROLE_TEXT = {
    "first_frame": "a concrete opening-frame target",
    "keyframe": "a concrete keyframe target",
    "last_frame": "a concrete ending-frame target",
    "storyboard": "storyboard guidance",
    "composition_reference": "composition guidance",
}

_FENCED_JSON = re.compile(
    r"\A\s*```(?:json)?[ \t]*\r?\n(?P<body>.*?)\r?\n```\s*\Z",
    re.IGNORECASE | re.DOTALL,
)
_SHOT_LIKE_TAG = re.compile(r"\[\s*shot[^\]]*(?:\]|$)", re.IGNORECASE)
_SHOT_TAG = re.compile(r"\[Shot ([1-9]\d*)\]")
_SHOT_TIMESTAMP = re.compile(r" At (\d{2}):([0-5]\d)\.(\d{3}),")
_CANONICALIZABLE_SHOT_TIMESTAMP = re.compile(
    r" At (?P<minutes>\d{1,2}):(?P<seconds>[0-5]\d)\."
    r"(?P<fraction>\d{1,3}),"
)
_REFERENCE_LIKE_TAG = re.compile(
    r"<\s*/?\s*(?:picture|video|audio)[^>]*(?:>|$)", re.IGNORECASE
)
_REFERENCE_TAG = re.compile(r"<(Picture|Video|Audio) ([1-9]\d*)>")
_BARE_PICTURE_REFERENCE = re.compile(
    r"(?<![<\w])Picture (?P<ordinal>[1-9]\d*)(?![>\d])"
)
_SUBJECT_LIKE_TAG = re.compile(
    r"<\s*/?\s*subject[^>]*(?:>|$)", re.IGNORECASE
)
_SUBJECT_TAG = re.compile(r"<Subject ([1-9]\d*)>")
_DEFINITION_LINE = re.compile(
    r"\A<(Subject|Picture) ([1-9]\d*)>[ \t]*(?P<definition>\S.*)\Z"
)
_DIALOGUE_BLOCK = re.compile(
    r"<d>\[([^\]\r\n]+)\]\s+(.+?)</d>", re.DOTALL
)
_DIALOGUE_TAG_LIKE = re.compile(r"</?\s*d(?:\s|>|$)", re.IGNORECASE)
_RETENTION_ENTRY = re.compile(
    r"\A<(?P<kind>Subject|Picture) (?P<ordinal>[1-9]\d*)>"
    r"(?: \((?P<scope>[^()\r\n]+)\))?: "
    r"(?P<marker>[^\r\n]+?) - "
    r"(?P<rationale>\S.*)\Z"
)
_RETENTION_MARKER = re.compile(
    r"\b(?:fully_preserved|partially_preserved|"
    r"attribute_transfer|weak_reference)\b"
)
_PLAN_MARKUP = re.compile(
    r"\[\s*shot\b"
    r"|<\s*/?\s*(?:subject|picture|video|audio|d|scenetrans|cutoff)\b"
    r"|\(\s*S\d+(?:\s*,\s*S\d+)*\s*\)"
    r"|\bDialogue[ \t]*:"
    r"|^[ \t]*(?:integrated_multimodal_description|subject_definitions|summary|"
    r"retention_analysis|detailed_description|overall_soundscape|"
    r"non_diegetic_music|dialogue)[ \t]*:"
    r"|\bAt[ \t]+\d{1,2}:[0-5]\d\.\d{1,3},",
    re.IGNORECASE | re.MULTILINE,
)


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

    ``detailed_description`` is the required visual description.  Other empty
    structured sections are omitted.  A supplied ``raw_override`` is returned
    exactly and bypasses all structured-field validation.
    """

    raw = _raw(raw_override)
    if raw is not None:
        return raw

    description = _normalize(detailed_description, "detailed_description")
    if not description:
        raise ValueError("detailed_description is required")

    values = (
        ("subject_definitions", subject_definitions),
        ("summary", summary),
        ("retention_analysis", retention_analysis),
        ("detailed_description", description),
        ("overall_soundscape", overall_soundscape),
        ("non_diegetic_music", non_diegetic_music),
    )

    sections = []
    for name, value in values:
        normalized = (
            value
            if name == "detailed_description"
            else _normalize(value, name)
        )
        if normalized:
            sections.append(_labeled(name, normalized))

    return "\n\n".join(sections)


def _validated_writer_request(
    mode: str,
    duration_seconds: float,
    reference_image_count: int,
) -> tuple[str, float, str, int]:
    if not isinstance(mode, str):
        raise TypeError("mode must be a string")
    if mode not in H3_PROMPT_MODES:
        raise ValueError(
            "mode must be one of: " + ", ".join(H3_PROMPT_MODES)
        )
    if isinstance(duration_seconds, bool) or not isinstance(
        duration_seconds, (int, float)
    ):
        raise TypeError("duration_seconds must be a finite number")
    duration = float(duration_seconds)
    if not math.isfinite(duration) or duration <= 0 or duration >= 6000:
        raise ValueError(
            "duration_seconds must be greater than 0 and less than 6000"
        )
    if isinstance(reference_image_count, bool) or not isinstance(
        reference_image_count, int
    ):
        raise TypeError("reference_image_count must be an integer")

    if mode == "ref2va":
        if not 1 <= reference_image_count <= _MAX_REFERENCE_IMAGES:
            raise ValueError(
                "ref2va requires between 1 and 9 reference images"
            )
    else:
        expected = _MODE_REFERENCE_COUNTS[mode]
        if reference_image_count != expected:
            raise ValueError(
                f"{mode} requires exactly {expected} reference image"
                + ("" if expected == 1 else "s")
            )
    return mode, duration, f"{duration:.2f}", reference_image_count


def _writer_plan_example(mode: str, reference_image_count: int) -> str:
    description = (
        "A wide opening composition establishes the subject and setting before "
        "the camera moves with the action."
        if mode == "ref2va"
        else (
            "Cinematic naturalism with cool, soft light. A wide opening "
            "composition establishes the subject and setting before the camera "
            "moves with the action."
        )
    )
    shot: dict[str, Any] = {
        "start_seconds": 0,
        "description": description,
        "dialogue": [],
    }
    example: dict[str, Any] = {
        "shots": [shot],
        "overall_soundscape": (
            "Natural ambience and synchronized physical sounds fill the scene."
        ),
        "non_diegetic_music": "N/A",
    }
    if mode != "ref2va":
        return json.dumps(example, ensure_ascii=False, indent=2)

    return json.dumps(
        {
            "style_lead": (
                "Cinematic realism with controlled light and detailed textures."
            ),
            "summary": (
                "Animate the tracked visual subject while preserving its identity."
            ),
            "subjects": [
                {
                    "definition": (
                        "The principal visible subject and its stable appearance."
                    ),
                    "source_pictures": list(
                        range(1, reference_image_count + 1)
                    ),
                    "uses": [
                        {
                            "shot": 1,
                            "application": (
                                "remains the central visual subject"
                            ),
                        }
                    ],
                    "retention": {
                        "marker": "fully_preserved",
                        "rationale": (
                            "Defining visible features remain stable."
                        ),
                    },
                }
            ],
            "picture_anchors": [],
            **example,
        },
        ensure_ascii=False,
        indent=2,
    )


def build_h3_prompt_writer_system(
    mode: str,
    duration_seconds: float,
    reference_image_count: int,
) -> str:
    """Build instructions for an LMS-backed semantic H3 plan writer."""

    mode, _duration, duration_text, reference_image_count = (
        _validated_writer_request(
            mode,
            duration_seconds,
            reference_image_count,
        )
    )
    reference_line = (
        "No reference images are attached."
        if reference_image_count == 0
        else (
            f"Exactly {reference_image_count} reference image"
            f"{' is' if reference_image_count == 1 else 's are'} attached in "
            f"ordinal order: {list(range(1, reference_image_count + 1))}. "
            "Inspect every image visually, keep those ordinals stable, and never "
            "invent another reference."
        )
    )
    mode_reference_roles = {
        "t2va": "Write from the user's text only.",
        "i2va": "Image 1 is the opening frame of the first shot.",
        "fl2va": (
            "Image 1 is the opening frame of the first shot; image 2 is the "
            "ending frame of the final shot."
        ),
        "l2va": "Image 1 is the ending frame of the final shot.",
        "ref2va": (
            "Follow every reference role stated by the user. Without an explicit "
            "frame role, derive tracked subjects for visible characters, objects, "
            "scenes, costumes, or styles; do not invent a frame/keyframe anchor."
        ),
    }[mode]
    content_rules = (
        "Each shot description must cover composition, visible subject appearance "
        "and position, environment and lighting, action or state change, camera "
        "motion, and synchronized diegetic sound. Name camera moves or shot types "
        "and their speed or amplitude when meaningful. overall_soundscape is one "
        "English paragraph covering ambience, physical sounds, and non-verbal "
        "human sounds without dialogue or music. non_diegetic_music describes "
        "only the audience-only score with instrumentation, tempo, rhythm, and "
        "dynamics; use N/A when no score is wanted. Write English prose except "
        "supplied dialogue, lyrics, and visible text."
    )
    plan_rules = (
        "For ref2va: summary is a complete relationship sentence without a "
        "bracketed prefix. The compiler derives the official task prefix from "
        "subjects and picture_anchors. subjects are numbered by array order; "
        "source_pictures contains attached image ordinals. Each use names a "
        "one-based shot and gives a short verb phrase that can follow the "
        "generated subject label. A picture_anchors item has exactly picture, "
        "role, definition, uses, and retention. Use picture_anchors only for "
        "images the user explicitly assigns a concrete or guiding role. role is "
        "exactly first_frame, keyframe, last_frame, storyboard, or "
        "composition_reference. The first three are concrete target frames; "
        "storyboard and composition_reference are visual guidance, not target "
        "frames. Example item: "
        '{"picture":1,"role":"last_frame","definition":"The concrete '
        'ending composition","uses":[{"shot":1,"application":"anchors the '
        'final framing"}],"retention":{"marker":"fully_preserved",'
        '"rationale":"The target framing remains stable."}}. Never copy this '
        "item unless the user assigns that role. "
        "Every attached ordinal must occur in at least one source_pictures list "
        "or one picture_anchors entry. Every subject and anchor needs at least "
        "one shot use and retention with one exact marker: fully_preserved, "
        "partially_preserved, attribute_transfer, or weak_reference. style_lead "
        "is one or two English sentences. Across style_lead and shot "
        "descriptions, write normally 350 to 500 English words."
        if mode == "ref2va"
        else (
            "The compiler owns the selected image-alignment preamble. Describe "
            "the visible image state faithfully in the relevant shots."
        )
    )

    dialogue_subject = "1" if mode == "ref2va" else "null"
    opening_rule = (
        "style_lead owns the visual style. Shot 1 begins with initial "
        "composition before its action and camera movement."
        if mode == "ref2va"
        else (
            "Shot 1 begins with visual style and initial composition before "
            "its action and camera movement."
        )
    )

    return (
        "You create a semantic video plan that a deterministic MiniMax H3 "
        "compiler will render.\n"
        f"Mode: {mode}. Target duration: {duration_text} seconds.\n"
        f"{reference_line} {mode_reference_roles}\n\n"
        "Return exactly one bare JSON object and no commentary or code fence. "
        "Match the example's keys and value types exactly; do not add keys. "
        "Replace all illustrative prose with details from the user and images:\n"
        f"{_writer_plan_example(mode, reference_image_count)}\n\n"
        "The compiler owns all H3 syntax. Do not write section labels, shot tags, "
        "timestamps inside descriptions, angle-bracket reference tags, retention "
        "lines, dialogue wrappers, or speaker IDs. shots is a nonempty array in "
        "timeline order. start_seconds is a JSON number with at most three decimal "
        "places: the first is exactly 0; later values strictly increase and remain "
        f"earlier than {duration_text}. dialogue is an array whose items have "
        "exactly speaker, subject, voice_identity, cue, language, and text. "
        "Example item: "
        f'{{"speaker":"elf","subject":{dialogue_subject},'
        '"voice_identity":"an on-screen young '
        'adult woman with a low, breathy voice, measured pace, and neutral '
        'accent","cue":"whispers softly",'
        '"language":"English","text":"We should leave."}. '
        "speaker is one stable natural name. voice_identity is one stable "
        "single-line phrase covering visible type or age, on- or off-screen "
        "position, pitch, timbre, rate, and accent. cue is a short delivery "
        "phrase without a colon; text ends in dialogue punctuation. In ref2va, subject "
        "is the one-based subjects array ordinal when that tracked subject "
        "speaks, otherwise null. In every other mode subject is null. Use [] "
        "when nobody speaks and never copy the example unless requested. Copy "
        "every user-supplied dialogue line verbatim: never paraphrase, translate, "
        "add, or omit it. Do not invent dialogue when the user supplied none.\n"
        f"{plan_rules}\n"
        f"{content_rules}\n"
        f"{opening_rule} Describe only observable reference details or "
        "explicitly requested "
        "changes. Keep the final compiled prompt at or below 7000 characters."
    )


def _json_object(response_text: str) -> tuple[dict[str, Any], str]:
    if not isinstance(response_text, str):
        raise TypeError("response_text must be a string")
    stripped = response_text.strip()
    if not stripped:
        raise ValueError("LMS response is empty; expected one JSON object")

    match = _FENCED_JSON.fullmatch(stripped)
    source_format = "fenced_json" if match is not None else "bare_json"
    if match is not None:
        stripped = match.group("body").strip()

    def object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if key in value:
                raise ValueError(f"LMS response repeats JSON field {key!r}")
            value[key] = item
        return value

    try:
        parsed = json.loads(stripped, object_pairs_hook=object_pairs)
    except json.JSONDecodeError as error:
        if "```" in stripped:
            raise ValueError(
                "LMS response must contain only one bare or ```json fenced "
                "JSON document"
            ) from error
        raise ValueError(
            f"LMS response is not valid JSON: {error.msg} at line "
            f"{error.lineno} column {error.colno}"
        ) from error
    if not isinstance(parsed, dict):
        raise ValueError("LMS response must be one JSON object")
    return parsed, source_format


def _validated_fields(
    parsed: dict[str, Any],
    expected: tuple[str, ...],
) -> dict[str, str]:
    missing = [field for field in expected if field not in parsed]
    extra = sorted(set(parsed) - set(expected))
    if missing or extra:
        details = []
        if missing:
            details.append("missing: " + ", ".join(missing))
        if extra:
            details.append("unexpected: " + ", ".join(extra))
        raise ValueError(
            "LMS response fields do not match the H3 schema ("
            + "; ".join(details)
            + ")"
        )

    fields: dict[str, str] = {}
    for name in expected:
        value = parsed[name]
        if not isinstance(value, str):
            raise ValueError(f"LMS response field {name!r} must be a string")
        normalized = _normalize(value, name)
        if not normalized:
            raise ValueError(f"LMS response field {name!r} must not be blank")
        fields[name] = normalized
    return fields


def _canonical_tag_ordinals(
    text: str,
    *,
    kind: str,
    like_pattern: re.Pattern[str],
    exact_pattern: re.Pattern[str],
) -> list[int]:
    ordinals = []
    for match in like_pattern.finditer(text):
        token = match.group(0)
        exact = exact_pattern.fullmatch(token)
        if exact is None:
            raise ValueError(
                f"Malformed {kind} tag {token!r}; use exact <{kind} N> syntax"
            )
        if kind == "Picture":
            tag_kind = exact.group(1)
            if tag_kind != "Picture":
                raise ValueError(
                    f"{tag_kind} references are unsupported; this prompt writer "
                    "accepts images only"
                )
            ordinal_group = exact.group(2)
        else:
            ordinal_group = exact.group(1)
        ordinals.append(int(ordinal_group))
    return ordinals


def _validate_picture_tags(
    text: str,
    *,
    reference_image_count: int,
    require_all: bool,
) -> list[int]:
    ordinals = _canonical_tag_ordinals(
        text,
        kind="Picture",
        like_pattern=_REFERENCE_LIKE_TAG,
        exact_pattern=_REFERENCE_TAG,
    )
    for ordinal in ordinals:
        if ordinal > reference_image_count:
            raise ValueError(
                f"<Picture {ordinal}> has no attached image; available references are "
                + (
                    "none"
                    if reference_image_count == 0
                    else f"<Picture 1> through <Picture {reference_image_count}>"
                )
            )
    found = set(ordinals)
    if require_all:
        missing = [
            ordinal
            for ordinal in range(1, reference_image_count + 1)
            if ordinal not in found
        ]
        if missing:
            formatted = ", ".join(f"<Picture {ordinal}>" for ordinal in missing)
            raise ValueError(
                f"Every attached reference must be represented; missing {formatted}"
            )
    return sorted(found)


def _validate_shots(
    description: str,
    duration: float,
    *,
    style_lead_required: bool,
) -> tuple[int, list[str]]:
    matches = list(_SHOT_LIKE_TAG.finditer(description))
    if not matches:
        raise ValueError("Visual description must begin with exact [Shot 1]")

    ordinals = []
    for match in matches:
        token = match.group(0)
        exact = _SHOT_TAG.fullmatch(token)
        if exact is None:
            raise ValueError(
                f"Malformed shot tag {token!r}; use exact [Shot N] syntax"
            )
        ordinals.append(int(exact.group(1)))
    expected = list(range(1, len(ordinals) + 1))
    if ordinals != expected:
        raise ValueError(
            "Shot tags must appear once in contiguous order starting at [Shot 1]"
        )
    style_lead = description[: matches[0].start()].strip()
    if style_lead_required:
        if not style_lead:
            raise ValueError(
                "ref2va detailed_description must include a one- or two-sentence "
                "English style lead before [Shot 1]"
            )
    elif style_lead:
        raise ValueError("Visual description must begin with [Shot 1]")

    timestamps = []
    previous_seconds = 0.0
    for index, match in enumerate(matches):
        following = description[match.end() :]
        timestamp = _SHOT_TIMESTAMP.match(following)
        if index == 0:
            if timestamp is not None or re.match(r"\s+At\b", following):
                raise ValueError("[Shot 1] must not include a timestamp")
            continue
        if timestamp is None:
            raise ValueError(
                f"[Shot {index + 1}] must be followed by exact ` At MM:SS.mmm,`"
            )
        minutes = int(timestamp.group(1))
        seconds = int(timestamp.group(2))
        milliseconds = int(timestamp.group(3))
        timestamp_seconds = minutes * 60 + seconds + milliseconds / 1000
        if timestamp_seconds <= previous_seconds:
            raise ValueError("Later shot timestamps must be strictly increasing")
        if timestamp_seconds >= duration:
            raise ValueError(
                f"Shot timestamp {timestamp.group(0).strip()} must be earlier "
                "than the target duration"
            )
        previous_seconds = timestamp_seconds
        timestamps.append(
            f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
        )
    return len(ordinals), timestamps


def _canonicalize_shot_timestamps(description: str) -> str:
    """Rewrite only mechanically equivalent shot timestamps to H3 syntax."""

    replacements: list[tuple[int, int, str]] = []
    for shot in _SHOT_TAG.finditer(description):
        timestamp = _CANONICALIZABLE_SHOT_TIMESTAMP.match(
            description[shot.end() :]
        )
        if timestamp is None:
            continue

        ordinal = int(shot.group(1))
        minutes = int(timestamp.group("minutes"))
        seconds = int(timestamp.group("seconds"))
        fraction = timestamp.group("fraction")
        milliseconds = int(fraction.ljust(3, "0"))
        original_start = shot.end()
        original_end = original_start + timestamp.end()

        if ordinal == 1:
            if minutes == 0 and seconds == 0 and milliseconds == 0:
                replacements.append((original_start, original_end, ""))
            continue

        canonical = (
            f" At {minutes:02d}:{seconds:02d}.{milliseconds:03d},"
        )
        if timestamp.group(0) != canonical:
            replacements.append((original_start, original_end, canonical))

    for start, end, replacement in reversed(replacements):
        description = description[:start] + replacement + description[end:]
    return description


def _canonicalize_subject_picture_references(
    subject_definitions: str,
) -> str:
    """Add omitted angle brackets to unambiguous Picture ordinals."""

    return _BARE_PICTURE_REFERENCE.sub(
        lambda match: f"<Picture {match.group('ordinal')}>",
        subject_definitions,
    )


def _validate_dialogue(text: str) -> int:
    matches = list(_DIALOGUE_BLOCK.finditer(text))
    remainder = _DIALOGUE_BLOCK.sub("", text)
    if _DIALOGUE_TAG_LIKE.search(remainder):
        raise ValueError(
            "Dialogue tags must use balanced <d>[Language] utterance</d> syntax"
        )
    for match in matches:
        language = match.group(1).strip()
        utterance = match.group(2).strip()
        if not language or not utterance:
            raise ValueError(
                "Dialogue tags require a nonblank language and utterance"
            )
        if _DIALOGUE_TAG_LIKE.search(utterance):
            raise ValueError("Dialogue tags cannot be nested")
    return len(matches)


def _validate_dialogue_fields(
    fields: dict[str, str], visual_field: str
) -> int:
    for field_name, value in fields.items():
        if field_name == visual_field:
            continue
        if _DIALOGUE_TAG_LIKE.search(value):
            raise ValueError(
                f"Dialogue tags are only valid in {visual_field}; found one in "
                f"{field_name}"
            )
    return _validate_dialogue(fields[visual_field])


def _definition_labels(
    subject_definitions: str,
) -> tuple[list[int], list[int], list[tuple[str, int]], list[int]]:
    labels: list[tuple[str, int]] = []
    represented_pictures: set[int] = set()
    for raw_line in subject_definitions.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = _DEFINITION_LINE.fullmatch(line)
        if match is None:
            raise ValueError(
                "Each nonblank subject_definitions line must begin with one "
                "canonical <Subject N> or <Picture N> label and a definition"
            )
        kind = match.group(1)
        ordinal = int(match.group(2))
        labels.append((kind, ordinal))
        if kind == "Picture":
            represented_pictures.add(ordinal)
        else:
            represented_pictures.update(
                _canonical_tag_ordinals(
                    line,
                    kind="Picture",
                    like_pattern=_REFERENCE_LIKE_TAG,
                    exact_pattern=_REFERENCE_TAG,
                )
            )

    seen: set[tuple[str, int]] = set()
    for label in labels:
        if label in seen:
            raise ValueError(
                f"subject_definitions repeats standalone <{label[0]} {label[1]}>"
            )
        seen.add(label)

    subjects = sorted(ordinal for kind, ordinal in labels if kind == "Subject")
    pictures = sorted(ordinal for kind, ordinal in labels if kind == "Picture")
    if subjects and subjects != list(range(1, subjects[-1] + 1)):
        raise ValueError(
            "Subject definitions must be contiguous starting at <Subject 1>"
        )
    return subjects, pictures, labels, sorted(represented_pictures)


def _retention_entries(
    retention_analysis: str,
) -> dict[tuple[str, int], str]:
    entries: dict[tuple[str, int], str] = {}
    for raw_line in retention_analysis.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = _RETENTION_ENTRY.fullmatch(line)
        if match is None:
            raise ValueError(
                "Each retention_analysis line must use exact `<Subject N> "
                "(scope): marker - rationale` or `<Picture N> (scope): marker "
                "- rationale` form"
            )
        label = (match.group("kind"), int(match.group("ordinal")))
        if label in entries:
            raise ValueError(
                f"retention_analysis repeats <{label[0]} {label[1]}>"
            )
        scope = match.group("scope")
        if scope is not None and scope.strip().casefold() == "scope":
            raise ValueError(
                f"<{label[0]} {label[1]}> needs a concrete retention scope; "
                "the placeholder word 'scope' is invalid"
            )
        marker = match.group("marker").strip()
        if marker not in _RETENTION_MARKERS:
            raise ValueError(
                f"Invalid retention marker {marker!r} for "
                f"<{label[0]} {label[1]}>; use exact snake_case vocabulary"
            )
        post_colon = line.split(":", 1)[1]
        marker_mentions = _RETENTION_MARKER.findall(post_colon)
        if len(marker_mentions) != 1:
            raise ValueError(
                f"<{label[0]} {label[1]}> must have exactly one retention marker"
            )
        rationale = match.group("rationale").strip()
        if not rationale or not any(character.isalnum() for character in rationale):
            raise ValueError(
                f"<{label[0]} {label[1]}> retention entry needs a rationale"
            )
        if rationale.strip(" .:;-_").casefold() == "rationale":
            raise ValueError(
                f"<{label[0]} {label[1]}> retention entry needs a concrete "
                "rationale; the placeholder word 'rationale' is invalid"
            )
        entries[label] = marker
    return entries


def _validate_reference_semantics(
    fields: dict[str, str], reference_image_count: int
) -> list[int]:
    summary = fields["summary"]
    task_prefix = next(
        (
            f"[{task}]"
            for task in _REFERENCE_TASKS
            if summary.startswith(f"[{task}]")
        ),
        None,
    )
    if task_prefix is None or not summary[len(task_prefix) :].strip():
        allowed = ", ".join(f"[{task}]" for task in _REFERENCE_TASKS)
        raise ValueError(
            "summary must start with an exact task prefix followed by a description: "
            + allowed
        )

    for raw_line in fields["detailed_description"].splitlines():
        if _RETENTION_ENTRY.fullmatch(raw_line.strip()):
            raise ValueError(
                "retention_analysis entries are only valid in retention_analysis; "
                "do not copy them into detailed_description"
            )

    all_subjects = _canonical_tag_ordinals(
        "\n".join(fields.values()),
        kind="Subject",
        like_pattern=_SUBJECT_LIKE_TAG,
        exact_pattern=_SUBJECT_TAG,
    )
    (
        defined,
        standalone_pictures,
        tracked_labels,
        represented_pictures,
    ) = _definition_labels(fields["subject_definitions"])
    missing_references = [
        ordinal
        for ordinal in range(1, reference_image_count + 1)
        if ordinal not in represented_pictures
    ]
    if missing_references:
        formatted = ", ".join(
            f"<Picture {ordinal}>" for ordinal in missing_references
        )
        raise ValueError(
            "Every attached reference must be represented in "
            "subject_definitions as a standalone Picture definition or cited "
            f"inside a Subject definition; missing {formatted}"
        )
    undefined = sorted(set(all_subjects) - set(defined))
    if undefined:
        raise ValueError(
            "Subject tags must be defined before use; undefined "
            + ", ".join(f"<Subject {ordinal}>" for ordinal in undefined)
        )
    detailed_subjects = set(
        _canonical_tag_ordinals(
            fields["detailed_description"],
            kind="Subject",
            like_pattern=_SUBJECT_LIKE_TAG,
            exact_pattern=_SUBJECT_TAG,
        )
    )
    missing_subjects = [
        ordinal for ordinal in defined if ordinal not in detailed_subjects
    ]
    if missing_subjects:
        raise ValueError(
            "detailed_description must use every defined subject; missing "
            + ", ".join(
                f"<Subject {ordinal}>" for ordinal in missing_subjects
            )
        )

    detailed_pictures = set(
        _canonical_tag_ordinals(
            fields["detailed_description"],
            kind="Picture",
            like_pattern=_REFERENCE_LIKE_TAG,
            exact_pattern=_REFERENCE_TAG,
        )
    )
    missing_pictures = [
        ordinal
        for ordinal in standalone_pictures
        if ordinal not in detailed_pictures
    ]
    if missing_pictures:
        raise ValueError(
            "detailed_description must use every standalone Picture; missing "
            + ", ".join(
                f"<Picture {ordinal}>" for ordinal in missing_pictures
            )
        )

    entries = _retention_entries(fields["retention_analysis"])
    missing_entries = [label for label in tracked_labels if label not in entries]
    if missing_entries:
        formatted = ", ".join(
            f"<{kind} {ordinal}>" for kind, ordinal in missing_entries
        )
        raise ValueError(
            "retention_analysis needs one entry for every standalone definition; "
            f"missing {formatted}"
        )
    unexpected_entries = [
        label for label in entries if label not in set(tracked_labels)
    ]
    if unexpected_entries:
        formatted = ", ".join(
            f"<{kind} {ordinal}>" for kind, ordinal in unexpected_entries
        )
        raise ValueError(
            "retention_analysis entries must have standalone definitions; "
            f"unexpected {formatted}"
        )
    return defined


def _mode_preamble(mode: str, duration_text: str, final_shot: int) -> str:
    if mode == "i2va":
        return (
            "For the target video, at 0.00 seconds into the target video, "
            "<Picture 1> (from [Shot 1]) is fully referenced."
        )
    if mode == "fl2va":
        return (
            "How the reference pictures align with the target video — Picture 1 "
            "(from Shot 1) aligns with the 0.00-second mark of the target video; "
            f"Picture 2 (from Shot {final_shot}) aligns with the {duration_text}-second "
            "mark of the target video."
        )
    if mode == "l2va":
        return (
            "How the reference pictures align with the target video — "
            f"<Picture 1> (from [Shot {final_shot}]) aligns with the "
            f"{duration_text}-second mark of the target video."
        )
    return ""


def _plan_object(
    value: Any,
    path: str,
    expected: tuple[str, ...],
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"Semantic plan {path} must be an object")
    missing = [field for field in expected if field not in value]
    extra = sorted(set(value) - set(expected))
    if missing or extra:
        details = []
        if missing:
            details.append("missing: " + ", ".join(missing))
        if extra:
            details.append("unexpected: " + ", ".join(extra))
        raise ValueError(
            f"Semantic plan {path} fields do not match the schema ("
            + "; ".join(details)
            + ")"
        )
    return value


def _plan_array(value: Any, path: str, *, nonempty: bool) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"Semantic plan {path} must be an array")
    if nonempty and not value:
        raise ValueError(f"Semantic plan {path} must not be empty")
    return value


def _plan_text(value: Any, path: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"Semantic plan {path} must be a string")
    normalized = _normalize(value, path)
    if not normalized:
        raise ValueError(f"Semantic plan {path} must not be blank")
    match = _PLAN_MARKUP.search(normalized)
    if match is not None:
        raise ValueError(
            f"Semantic plan {path} must contain plain prose; the compiler owns "
            f"reserved H3 token {match.group(0)!r}"
        )
    return normalized


def _plan_positive_ordinal(value: Any, path: str, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"Semantic plan {path} must be an integer")
    if value < 1 or value > maximum:
        raise ValueError(
            f"Semantic plan {path} must be between 1 and {maximum}"
        )
    return value


def _plan_ordinals(
    value: Any,
    path: str,
    maximum: int,
) -> list[int]:
    items = _plan_array(value, path, nonempty=True)
    ordinals = [
        _plan_positive_ordinal(item, f"{path}[{index}]", maximum)
        for index, item in enumerate(items)
    ]
    if len(set(ordinals)) != len(ordinals):
        raise ValueError(f"Semantic plan {path} must not repeat an ordinal")
    return ordinals


def _plan_start_milliseconds(
    value: Any,
    path: str,
    duration: float,
) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"Semantic plan {path} must be a finite number")
    try:
        seconds = Decimal(str(value))
    except InvalidOperation as error:
        raise ValueError(
            f"Semantic plan {path} must be a finite number"
        ) from error
    if not seconds.is_finite() or seconds < 0:
        raise ValueError(f"Semantic plan {path} must be a finite number")
    milliseconds = seconds * 1000
    if milliseconds != milliseconds.to_integral_value():
        raise ValueError(
            f"Semantic plan {path} must be exact to milliseconds"
        )
    if seconds >= Decimal(str(duration)):
        raise ValueError(
            f"Semantic plan {path} must be earlier than the target duration"
        )
    return int(milliseconds)


def _h3_timestamp(milliseconds: int) -> str:
    minutes, within_minute = divmod(milliseconds, 60_000)
    seconds, remainder = divmod(within_minute, 1000)
    return f"{minutes:02d}:{seconds:02d}.{remainder:03d}"


def _sentence(text: str) -> str:
    return text if text[-1] in ".!?…。！？" else f"{text}."


def _plan_inline_text(value: Any, path: str) -> str:
    text = _plan_text(value, path)
    if "\n" in text:
        raise ValueError(f"Semantic plan {path} must be a single line")
    return text


def _render_plan_dialogue(
    value: Any,
    path: str,
    speaker_ids: dict[tuple[str, object], int],
    speaker_bindings: dict[str, Optional[int]],
    speaker_names: dict[str, str],
    speaker_voices: dict[tuple[str, object], str],
    subject_count: int,
) -> tuple[list[str], int]:
    items = _plan_array(value, path, nonempty=False)
    rendered: list[str] = []
    for index, item in enumerate(items):
        item_path = f"{path}[{index}]"
        dialogue = _plan_object(item, item_path, _DIALOGUE_PLAN_FIELDS)
        speaker = _plan_inline_text(
            dialogue["speaker"], f"{item_path}.speaker"
        )
        voice_identity = _plan_inline_text(
            dialogue["voice_identity"],
            f"{item_path}.voice_identity",
        )
        cue = _plan_inline_text(dialogue["cue"], f"{item_path}.cue")
        language = _plan_inline_text(
            dialogue["language"], f"{item_path}.language"
        )
        text = _plan_text(dialogue["text"], f"{item_path}.text")
        if any(character in language for character in "[]"):
            raise ValueError(
                f"Semantic plan {item_path}.language cannot contain brackets "
                "or line breaks"
            )
        subject = dialogue["subject"]
        if subject is not None:
            if subject_count == 0:
                raise ValueError(
                    f"Semantic plan {item_path}.subject must be null when no "
                    "tracked subjects exist"
                )
            subject = _plan_positive_ordinal(
                subject,
                f"{item_path}.subject",
                subject_count,
            )
        if text[-1] not in ".!?…。！？":
            raise ValueError(
                f"Semantic plan {item_path}.text must end with dialogue "
                "punctuation"
            )
        if ":" in cue:
            raise ValueError(
                f"Semantic plan {item_path}.cue must not contain a colon"
            )
        cue = cue.rstrip(" \t;,.-!?")
        if not cue:
            raise ValueError(
                f"Semantic plan {item_path}.cue must contain a delivery phrase"
            )
        speaker_key = speaker.casefold()
        if speaker_key not in speaker_bindings:
            speaker_bindings[speaker_key] = subject
            speaker_names[speaker_key] = speaker
        elif speaker_bindings[speaker_key] != subject:
            raise ValueError(
                f"Semantic plan {item_path}.subject changes the tracked-subject "
                f"binding for speaker {speaker_names[speaker_key]!r}"
            )
        identity_key: tuple[str, object] = (
            ("subject", subject)
            if subject is not None
            else ("speaker", speaker_key)
        )
        first_vocal_event = identity_key not in speaker_ids
        if first_vocal_event:
            speaker_ids[identity_key] = len(speaker_ids) + 1
            speaker_voices[identity_key] = voice_identity
        elif speaker_voices[identity_key].casefold() != voice_identity.casefold():
            raise ValueError(
                f"Semantic plan {item_path}.voice_identity changes the stable "
                "voice identity for an existing speaker"
            )
        identity = (
            f"<Subject {subject}>"
            if subject is not None
            else speaker_names[speaker_key]
        )
        speaker_prefix = f"{identity} (S{speaker_ids[identity_key]})"
        if first_vocal_event:
            speaker_prefix += f", {voice_identity},"
        rendered.append(
            f"{speaker_prefix} {cue}: <d>[{language}] {text}</d>"
        )
    return rendered, len(items)


def _plan_shots(
    value: Any,
    duration: float,
) -> tuple[list[dict[str, Any]], list[str]]:
    items = _plan_array(value, "shots", nonempty=True)
    if len(items) > 99:
        raise ValueError("Semantic plan shots cannot contain more than 99 items")

    shots: list[dict[str, Any]] = []
    timestamps: list[str] = []
    previous_milliseconds = -1
    for index, item in enumerate(items):
        path = f"shots[{index}]"
        shot = _plan_object(item, path, _SHOT_PLAN_FIELDS)
        milliseconds = _plan_start_milliseconds(
            shot["start_seconds"],
            f"{path}.start_seconds",
            duration,
        )
        if index == 0 and milliseconds != 0:
            raise ValueError(
                "Semantic plan shots[0].start_seconds must be exactly 0"
            )
        if index > 0 and milliseconds <= previous_milliseconds:
            raise ValueError(
                "Semantic plan shot start_seconds values must be strictly "
                "increasing"
            )
        previous_milliseconds = milliseconds
        description = _plan_text(
            shot["description"], f"{path}.description"
        )
        dialogue = _plan_array(
            shot["dialogue"], f"{path}.dialogue", nonempty=False
        )
        shots.append(
            {
                "description": description,
                "dialogue": dialogue,
                "milliseconds": milliseconds,
            }
        )
        if index > 0:
            timestamps.append(_h3_timestamp(milliseconds))
    return shots, timestamps


def _plan_uses(
    value: Any,
    path: str,
    shot_count: int,
) -> list[tuple[int, str]]:
    items = _plan_array(value, path, nonempty=True)
    uses: list[tuple[int, str]] = []
    seen: set[int] = set()
    for index, item in enumerate(items):
        item_path = f"{path}[{index}]"
        usage = _plan_object(item, item_path, _USE_PLAN_FIELDS)
        shot = _plan_positive_ordinal(
            usage["shot"], f"{item_path}.shot", shot_count
        )
        if shot in seen:
            raise ValueError(f"Semantic plan {path} repeats shot {shot}")
        seen.add(shot)
        application = _plan_text(
            usage["application"], f"{item_path}.application"
        )
        uses.append((shot, application))
    return uses


def _plan_retention(
    value: Any,
    path: str,
) -> tuple[str, str]:
    retention = _plan_object(value, path, _RETENTION_PLAN_FIELDS)
    marker = retention["marker"]
    if not isinstance(marker, str) or marker not in _RETENTION_MARKERS:
        raise ValueError(
            f"Semantic plan {path}.marker must be one of: "
            + ", ".join(_RETENTION_MARKERS)
        )
    rationale = _plan_text(retention["rationale"], f"{path}.rationale")
    if rationale.strip(" .:;-_").casefold() == "rationale":
        raise ValueError(
            f"Semantic plan {path}.rationale must be concrete"
        )
    return marker, rationale


def _retention_scope(uses: list[tuple[int, str]], shot_count: int) -> str:
    ordinals = sorted(shot for shot, _application in uses)
    if ordinals == list(range(1, shot_count + 1)):
        return "all shots"
    return "appears in " + ", ".join(
        f"[Shot {ordinal}]" for ordinal in ordinals
    )


def _render_plan_shots(
    shots: list[dict[str, Any]],
    applications: list[list[str]],
    endings: list[list[str]],
    subject_count: int,
) -> str:
    rendered: list[str] = []
    speaker_ids: dict[tuple[str, object], int] = {}
    speaker_bindings: dict[str, Optional[int]] = {}
    speaker_names: dict[str, str] = {}
    speaker_voices: dict[tuple[str, object], str] = {}
    for index, shot in enumerate(shots):
        ordinal = index + 1
        prefix = f"[Shot {ordinal}]"
        if ordinal > 1:
            prefix += f" At {_h3_timestamp(shot['milliseconds'])},"
        pieces = [*applications[index], shot["description"]]
        dialogue, _count = _render_plan_dialogue(
            shot["dialogue"],
            f"shots[{index}].dialogue",
            speaker_ids,
            speaker_bindings,
            speaker_names,
            speaker_voices,
            subject_count,
        )
        if dialogue:
            pieces.append("Dialogue: " + " ".join(dialogue))
        pieces.extend(endings[index])
        rendered.append(f"{prefix} " + " ".join(pieces))
    return "\n\n".join(rendered)


def _shot_labels(uses: list[tuple[int, str]]) -> str:
    labels = [f"[Shot {shot}]" for shot, _application in uses]
    if len(labels) == 1:
        return labels[0]
    return ", ".join(labels[:-1]) + f", and {labels[-1]}"


def _joined_labels(labels: list[str]) -> str:
    if len(labels) == 1:
        return labels[0]
    if len(labels) == 2:
        return f"{labels[0]} and {labels[1]}"
    return ", ".join(labels[:-1]) + f", and {labels[-1]}"


def _reference_task_and_relationship(
    subject_count: int,
    anchors: list[tuple[int, str]],
) -> tuple[str, str]:
    clauses: list[str] = []
    has_reference_generation = subject_count > 0
    has_keyframe_completion = False
    if subject_count:
        subject_labels = [
            f"<Subject {ordinal}>" for ordinal in range(1, subject_count + 1)
        ]
        clauses.append(f"Track {_joined_labels(subject_labels)}")
    for picture, role in anchors:
        role_text = _PICTURE_ANCHOR_ROLE_TEXT[role]
        if role in _CONCRETE_FRAME_ROLES:
            has_keyframe_completion = True
            clauses.append(f"apply <Picture {picture}> as {role_text}")
        else:
            has_reference_generation = True
            clauses.append(f"use <Picture {picture}> as {role_text}")
    if not clauses:
        raise ValueError(
            "Semantic ref2va plan must define at least one subject or picture "
            "anchor"
        )
    if has_reference_generation and has_keyframe_completion:
        task = "reference generation + keyframe completion"
    elif has_keyframe_completion:
        task = "keyframe completion"
    else:
        task = "reference generation"
    relationship = "; ".join(clauses)
    relationship = relationship[0].upper() + relationship[1:] + "."
    return task, relationship


def _render_semantic_plan(
    parsed: dict[str, Any],
    mode: str,
    duration: float,
    reference_image_count: int,
) -> dict[str, str]:
    expected = _REFERENCE_PLAN_FIELDS if mode == "ref2va" else _BASE_PLAN_FIELDS
    plan = _plan_object(parsed, "response", expected)
    shots, _timestamps = _plan_shots(plan["shots"], duration)
    applications: list[list[str]] = [[] for _shot in shots]
    endings: list[list[str]] = [[] for _shot in shots]
    soundscape = _plan_text(
        plan["overall_soundscape"], "overall_soundscape"
    )
    music = _plan_text(
        plan["non_diegetic_music"], "non_diegetic_music"
    )

    if mode != "ref2va":
        if mode in {"i2va", "fl2va"}:
            applications[0].append(
                "<Picture 1> defines the opening frame."
            )
        if mode == "fl2va":
            endings[-1].append(
                "The final shot converges on <Picture 2> as its ending frame."
            )
        if mode == "l2va":
            endings[-1].append(
                "The final shot converges on <Picture 1> as its ending frame."
            )
        return {
            "integrated_multimodal_description": _render_plan_shots(
                shots, applications, endings, 0
            ),
            "overall_soundscape": soundscape,
            "non_diegetic_music": music,
        }

    style_lead = _plan_text(plan["style_lead"], "style_lead")
    summary = _plan_text(plan["summary"], "summary")
    if summary.startswith("["):
        raise ValueError(
            "Semantic plan summary must omit the task prefix; the compiler adds it"
        )

    subject_items = _plan_array(plan["subjects"], "subjects", nonempty=False)
    anchor_items = _plan_array(
        plan["picture_anchors"], "picture_anchors", nonempty=False
    )
    subject_lines: list[str] = []
    retention_lines: list[str] = []
    represented_pictures: set[int] = set()

    for index, item in enumerate(subject_items):
        ordinal = index + 1
        path = f"subjects[{index}]"
        subject = _plan_object(item, path, _SUBJECT_PLAN_FIELDS)
        definition = _plan_text(subject["definition"], f"{path}.definition")
        sources = _plan_ordinals(
            subject["source_pictures"],
            f"{path}.source_pictures",
            reference_image_count,
        )
        represented_pictures.update(sources)
        uses = _plan_uses(subject["uses"], f"{path}.uses", len(shots))
        marker, rationale = _plan_retention(
            subject["retention"], f"{path}.retention"
        )
        source_tags = ", ".join(
            f"<Picture {source}>" for source in sources
        )
        source_label = "Source reference" if len(sources) == 1 else "Source references"
        subject_lines.append(
            f"<Subject {ordinal}> is defined as follows: "
            f"{_sentence(definition)} "
            f"{source_label}: {source_tags}."
        )
        retention_lines.append(
            f"<Subject {ordinal}> ({_retention_scope(uses, len(shots))}): "
            f"{marker} - {rationale}"
        )
        for shot, application in uses:
            applications[shot - 1].append(
                f"<Subject {ordinal}> {_sentence(application)}"
            )

    anchor_ordinals: set[int] = set()
    anchor_roles: list[tuple[int, str]] = []
    for index, item in enumerate(anchor_items):
        path = f"picture_anchors[{index}]"
        anchor = _plan_object(item, path, _PICTURE_ANCHOR_PLAN_FIELDS)
        picture = _plan_positive_ordinal(
            anchor["picture"], f"{path}.picture", reference_image_count
        )
        if picture in anchor_ordinals:
            raise ValueError(
                f"Semantic plan picture_anchors repeats Picture {picture}"
            )
        anchor_ordinals.add(picture)
        represented_pictures.add(picture)
        role = anchor["role"]
        if not isinstance(role, str) or role not in _PICTURE_ANCHOR_ROLES:
            raise ValueError(
                f"Semantic plan {path}.role must be one of: "
                + ", ".join(_PICTURE_ANCHOR_ROLES)
            )
        anchor_roles.append((picture, role))
        definition = _plan_text(anchor["definition"], f"{path}.definition")
        uses = _plan_uses(anchor["uses"], f"{path}.uses", len(shots))
        use_shots = [shot for shot, _application in uses]
        if role == "first_frame" and use_shots != [1]:
            raise ValueError(
                f"Semantic plan {path} with role first_frame must use exactly "
                "Shot 1"
            )
        if role == "last_frame" and use_shots != [len(shots)]:
            raise ValueError(
                f"Semantic plan {path} with role last_frame must use exactly "
                f"the final shot, Shot {len(shots)}"
            )
        marker, rationale = _plan_retention(
            anchor["retention"], f"{path}.retention"
        )
        subject_lines.append(
            f"<Picture {picture}> is defined as "
            f"{_PICTURE_ANCHOR_ROLE_TEXT[role]} "
            f"for {_shot_labels(uses)}: {_sentence(definition)}"
        )
        retention_lines.append(
            f"<Picture {picture}> ({_retention_scope(uses, len(shots))}): "
            f"{marker} - {rationale}"
        )
        for shot, application in uses:
            if role == "last_frame":
                endings[shot - 1].append(
                    f"The shot ends on <Picture {picture}>, which "
                    f"{_sentence(application)}"
                )
            else:
                applications[shot - 1].append(
                    f"<Picture {picture}> {_sentence(application)}"
                )

    missing_pictures = sorted(
        set(range(1, reference_image_count + 1)) - represented_pictures
    )
    if missing_pictures:
        raise ValueError(
            "Semantic plan must represent every attached Picture; missing "
            + ", ".join(f"Picture {ordinal}" for ordinal in missing_pictures)
        )

    task, relationship = _reference_task_and_relationship(
        len(subject_items), anchor_roles
    )
    detailed_description = (
        f"{_sentence(style_lead)} "
        + _render_plan_shots(
            shots,
            applications,
            endings,
            len(subject_items),
        )
    )
    return {
        "subject_definitions": "\n".join(subject_lines),
        "summary": f"[{task}] {relationship} {_sentence(summary)}",
        "retention_analysis": "\n".join(retention_lines),
        "detailed_description": detailed_description,
        "overall_soundscape": soundscape,
        "non_diegetic_music": music,
    }


def _compile_fields(
    fields: dict[str, str],
    mode: str,
    duration: float,
    duration_text: str,
    reference_image_count: int,
    source_format: str,
) -> tuple[str, dict[str, Any]]:
    expected = _REFERENCE_FIELDS if mode == "ref2va" else _BASE_FIELDS
    fields = _validated_fields(fields, expected)
    description_field = (
        "detailed_description"
        if mode == "ref2va"
        else "integrated_multimodal_description"
    )
    fields[description_field] = _canonicalize_shot_timestamps(
        fields[description_field]
    )
    if mode == "ref2va":
        fields["subject_definitions"] = (
            _canonicalize_subject_picture_references(
                fields["subject_definitions"]
            )
        )
    shot_count, shot_timestamps = _validate_shots(
        fields[description_field],
        duration,
        style_lead_required=mode == "ref2va",
    )
    joined_fields = "\n".join(fields.values())
    dialogue_count = _validate_dialogue_fields(fields, description_field)
    picture_ordinals = _validate_picture_tags(
        joined_fields,
        reference_image_count=reference_image_count,
        require_all=False,
    )

    subject_ordinals: list[int] = []
    if mode == "ref2va":
        subject_ordinals = _validate_reference_semantics(
            fields, reference_image_count
        )
        prompt = compose_full_reference_prompt(**fields)
    else:
        if _SUBJECT_LIKE_TAG.search(joined_fields):
            raise ValueError(
                "Subject tags are only valid in ref2va prompts"
            )
        preamble = _mode_preamble(mode, duration_text, shot_count)
        prompt = compose_base_prompt(instruction=preamble, **fields)
        picture_ordinals = list(range(1, reference_image_count + 1))

    if len(prompt) > _MAX_PROMPT_CHARS:
        raise ValueError(
            f"Compiled H3 prompt is {len(prompt)} characters; maximum is "
            f"{_MAX_PROMPT_CHARS}"
        )

    report = {
        "schema": H3_PROMPT_REPORT_SCHEMA,
        "valid": True,
        "mode": mode,
        "sourceFormat": source_format,
        "sections": list(expected),
        "durationSeconds": duration_text,
        "referenceImageCount": reference_image_count,
        "pictureOrdinals": picture_ordinals,
        "subjectOrdinals": subject_ordinals,
        "shotCount": shot_count,
        "shotTimestamps": shot_timestamps,
        "dialogueCount": dialogue_count,
        "characterCount": len(prompt),
    }
    return prompt, report


def compile_h3_prompt_response(
    response_text: str,
    mode: str,
    duration_seconds: float,
    reference_image_count: int,
) -> tuple[str, dict[str, Any]]:
    """Validate one LMS JSON response and compile an exact H3 prompt."""

    mode, duration, duration_text, reference_image_count = (
        _validated_writer_request(
            mode,
            duration_seconds,
            reference_image_count,
        )
    )
    parsed, source_format = _json_object(response_text)
    legacy_discriminators = {
        "integrated_multimodal_description",
        "detailed_description",
        "subject_definitions",
    }
    if legacy_discriminators.intersection(parsed):
        expected = _REFERENCE_FIELDS if mode == "ref2va" else _BASE_FIELDS
        fields = _validated_fields(parsed, expected)
    else:
        fields = _render_semantic_plan(
            parsed,
            mode,
            duration,
            reference_image_count,
        )
    return _compile_fields(
        fields,
        mode,
        duration,
        duration_text,
        reference_image_count,
        source_format,
    )


__all__ = [
    "H3_PROMPT_MODES",
    "H3_PROMPT_REPORT_SCHEMA",
    "build_h3_prompt_writer_system",
    "compile_h3_prompt_response",
    "compose_base_prompt",
    "compose_full_reference_prompt",
]
