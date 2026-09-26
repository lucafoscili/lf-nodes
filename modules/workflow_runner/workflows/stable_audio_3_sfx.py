"""A focused text-to-sound-effects block using native Stable Audio 3 Medium."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from ..services.registry import (
    InputValidationError,
    WorkflowBlockNode,
    WorkflowCardPresentation,
    WorkflowCell,
    WorkflowHeroImage,
)
from .utils import integer, required_text


_DEFAULT_PROMPT = (
    "Close recording of a steady wood fire in a hearth, soft continuous flames "
    "and irregular dry crackles. Only the fire, with no voices, music, footsteps, "
    "or other background activity."
)
_DEFAULT_DURATION = 10.0
_DEFAULT_SEED = 42
_MAX_SEED = (1 << 53) - 1
_SFX_PREFIX = "TrackType: SFX, "


def _duration(inputs: dict[str, Any]) -> float:
    value = inputs.get("duration", _DEFAULT_DURATION)
    if value is None or value == "":
        value = _DEFAULT_DURATION
    if isinstance(value, bool):
        raise InputValidationError("duration")
    try:
        seconds = float(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise InputValidationError("duration") from error
    if not math.isfinite(seconds) or not 1.0 <= seconds <= 380.0:
        raise ValueError("duration must be between 1 and 380 seconds.")
    return seconds


def _configure(prompt: dict[str, Any], inputs: dict[str, Any]) -> None:
    description = required_text(inputs, "prompt")
    seconds = _duration(inputs)
    seed = integer(inputs, "seed", _DEFAULT_SEED, minimum=0, maximum=_MAX_SEED)

    # The SFX tag is part of this narrow block's task, not a second user knob.
    if not description.casefold().startswith("tracktype: sfx,"):
        description = _SFX_PREFIX + description
    prompt["positive"]["inputs"]["text"] = description
    prompt["latent"]["inputs"]["seconds"] = seconds
    prompt["sample"]["inputs"]["seed"] = seed
    prompt["save_audio"]["inputs"]["filename_prefix"] = (
        f"lf-workflow-runner/stable-audio-3/sfx-seed-{seed}"
    )


def _configure_download(prompt: dict[str, Any], inputs: dict[str, Any]) -> None:
    _configure(prompt, {"prompt": _DEFAULT_PROMPT, **inputs})


def _number_cell(
    input_id: str, node_id: str, label: str, default: int | float,
    minimum: int | float, maximum: int | float, step: int | float, helper: str,
) -> WorkflowCell:
    return WorkflowCell(
        id=input_id,
        node_id=node_id,
        shape="textfield",
        required=False,
        props={
            "lfLabel": label,
            "lfValue": str(default),
            "lfHtmlAttributes": {
                "name": input_id, "type": "number", "min": minimum,
                "max": maximum, "step": step,
            },
            "lfHelper": {"showWhenFocused": False, "value": helper},
        },
    )


WORKFLOW = WorkflowBlockNode(
    id="stable_audio_3_sfx",
    value="Sound Effects",
    category="Stable Audio 3",
    description="Turn a sound description into a stereo WAV with Stable Audio 3 Medium.",
    card=WorkflowCardPresentation(
        summary="Describe a sound and generate an editable stereo WAV.",
        hero=WorkflowHeroImage(
            asset="audio/hearth.webp",
            alt="Full stereo waveform of the accepted 10.03-second hearth recording, including its quiet tail.",
        ),
    ),
    inputs=(
        WorkflowCell(
            id="prompt",
            node_id="positive",
            shape="textfield",
            props={
                "lfLabel": "Describe the sound",
                "lfValue": _DEFAULT_PROMPT,
                "lfStyling": "textarea",
                "lfHelper": {
                    "showWhenFocused": False,
                    "value": (
                        "Say what makes the sound, what happens, and how close the mic is. "
                        "For one-shots, ask for a single isolated hit followed by silence. "
                        "The SFX tag is added for you; unwanted sounds may still need another take."
                    ),
                },
            },
        ),
        _number_cell(
            "duration", "latent", "Duration (seconds)", _DEFAULT_DURATION, 1, 380, 0.1,
            "How long to record: try 2–4 seconds for a single hit or 10–20 for ambience. "
            "Longer clips use more time and memory. The actual length can differ by about "
            "0.05 seconds; asking for a loop does not make its join seamless.",
        ),
        _number_cell(
            "seed", "sample", "Seed", _DEFAULT_SEED, 0, _MAX_SEED, 1,
            "The starting noise for this take. Keep it fixed when comparing descriptions; "
            "change it to hear another variation.",
        ),
    ),
    outputs=(
        WorkflowCell(
            id="audio", node_id="save_audio", shape="masonry",
            description="Decoded stereo WAV, without trimming or additional loudness adjustment.",
        ),
        WorkflowCell(
            id="receipt", node_id="display_receipt", shape="code",
            description="Saved file, sample rate, channel count, and actual duration.",
            props={"lfLanguage": "json"},
        ),
    ),
    configure_prompt=_configure,
    configure_download=_configure_download,
    workflow_path=Path(__file__).with_suffix(".json"),
)
