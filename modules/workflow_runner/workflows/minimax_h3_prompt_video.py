"""Render final H3 prose verbatim using the existing base/reference recipes."""

from __future__ import annotations

import json
from functools import partial
from typing import Any

from ..services.registry import (
    InputValidationError,
    WorkflowCardPresentation,
    WorkflowCell,
    WorkflowHeroImage,
    WorkflowNode,
)
from . import minimax_h3 as h3
from . import minimax_h3_hd as hd
from .minimax_h3_prompt_maker import _MODE_OPTIONS, _PICTURE_IDS, _reference_fields
from .utils import choice, has_input_value, resolve_load_image_reference


DEFAULT_DURATION = str(124 / h3._FPS)
DEFAULT_PROMPT = (
    "One continuous shot of rain falling across a quiet garden. "
    "The camera holds still as leaves move gently and rain taps the ground."
)
_DURATION_OPTIONS = tuple(
    (str(int(frames) / h3._FPS), label, description)
    for frames, label, description in h3._DURATION_OPTIONS
)


def _duration_frames(inputs: dict[str, Any]) -> str:
    value = inputs.get("duration", DEFAULT_DURATION)
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise InputValidationError("duration")
    try:
        seconds = float(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise InputValidationError("duration") from error
    for frames in h3._DURATION_IDS:
        if seconds == int(frames) / h3._FPS:
            return frames
    raise InputValidationError("duration")


def _configure(
    prompt: dict[str, Any], inputs: dict[str, Any], *, resolve_upload: bool
) -> None:
    # Validate every scalar and reference count before upload staging or mutation.
    prose = inputs.get("prompt")
    if not isinstance(prose, str) or not prose.strip():
        raise InputValidationError("prompt")
    mode = choice(inputs, "mode", "auto", tuple(option[0] for option in _MODE_OPTIONS))
    if mode == "auto":
        mode = (
            "ref2va"
            if any(has_input_value(inputs, field) for field in _PICTURE_IDS)
            else "t2va"
        )
    fields = _reference_fields(inputs, mode)
    family = "ref2va" if mode == "ref2va" else "fl2va"
    settings = h3._common_settings(
        {**inputs, "duration_frames": _duration_frames(inputs)},
        family=family,
        default_aspect_ratio="16:9",
    )
    references = [
        resolve_load_image_reference(inputs, field) if resolve_upload else f"{field}.png"
        for field in fields
    ]

    path = h3._REFERENCE_GRAPH if mode == "ref2va" else h3._BASE_GRAPH
    graph = json.loads(path.read_text(encoding="utf-8"))
    h3_inputs = graph["h3"]["inputs"]
    h3_inputs["prompt"] = prose
    if mode == "ref2va":
        # These templates also serve section-based cards; raw prose needs none of
        # their section writers or joiner. Reference images stay independent.
        for node_id in tuple(graph):
            if node_id.startswith("prompt_"):
                graph.pop(node_id)
        for ordinal in range(1, 10):
            source = f"source_{ordinal}"
            socket = f"ref_images.ref_image_{ordinal - 1}"
            if ordinal <= len(references):
                graph[source]["inputs"]["image"] = references[ordinal - 1]
            else:
                graph.pop(source)
                h3_inputs.pop(socket)
    else:
        first = references[0] if mode in {"i2va", "fl2va"} else None
        last = references[-1] if mode in {"l2va", "fl2va"} else None
        for source, socket, image in (
            ("source_first", "first_frame", first),
            ("source_last", "last_frame", last),
        ):
            if image is None:
                graph.pop(source)
                h3_inputs.pop(socket, None)
            else:
                graph[source]["inputs"]["image"] = image
                h3_inputs[socket] = [source, 0]
    h3._apply_execution_profile(graph, settings.profile)
    h3._apply_common_graph_settings(
        graph, settings, output_folder="PromptVideo", reference_count=len(references)
    )
    hd.apply_optional_hd_pass(
        graph, inputs, base_width=settings.width, base_height=settings.height,
        profile_id=settings.profile.id,
    )
    graph["display_prompt"] = {
        "class_type": "LF_DisplayString",
        "inputs": {"string": prose, "ui_widget": ""},
        "_meta": {"title": "Exact prompt sent to MiniMax H3"},
    }
    prompt.clear()
    prompt.update(graph)


_common_inputs = h3._common_cells(default_aspect_ratio="16:9")
WORKFLOW = WorkflowNode(
    id="minimax_h3_prompt_video",
    value="Render H3 Prompt",
    description=(
        "Render a finished prompt exactly as supplied, with optional ordered Pictures. "
        "Uses the Kitchen 20-step quality recipe with optional four-step HD refinement "
        "and saves video with the original stereo audio."
    ),
    category="MiniMax H3",
    card=WorkflowCardPresentation(
        summary="Render finished H3 prose and retain the exact prompt.",
        hero=WorkflowHeroImage(
            asset="minimax-h3/prompt-video.webp",
            alt="Actual rendered video frame of the mustard-jacket explorer walking along a forest path.",
        ),
    ),
    inputs=[
        h3._textarea_cell(
            node_id="h3", cell_id="prompt", label="Final prompt", default=DEFAULT_PROMPT,
            description="Final prompt prose, passed to H3 unchanged.",
        ),
        h3._select_cell(
            node_id="h3", cell_id="mode", label="H3 mode", default="auto",
            description="Automatic uses text alone or treats uploaded Pictures as references.",
            options=_MODE_OPTIONS,
        ),
        h3._select_cell(
            node_id="h3", cell_id="duration", label="Duration", default=DEFAULT_DURATION,
            description="Exact H3 frame presets at 24 fps; shared with prompt authoring.",
            options=_DURATION_OPTIONS,
        ),
        *[
            h3._upload_cell(
                node_id="h3", cell_id=field, label=f"Picture {ordinal}", required=False,
                description="Ordered reference image; fill Pictures consecutively without gaps.",
            )
            for ordinal, field in enumerate(_PICTURE_IDS, 1)
        ],
        *[cell for cell in _common_inputs if cell.id != "duration_frames"],
    ],
    outputs=[
        h3._video_output("Generated video with synchronized stereo audio at 24 fps."),
        WorkflowCell(
            node_id="display_prompt", id="prompt", shape="code",
            description="Exact prompt supplied to H3.", props={"lfLanguage": "markdown"},
        ),
    ],
    workflow_path=h3._BASE_GRAPH,
    configure_prompt=partial(_configure, resolve_upload=True),
    configure_download=partial(_configure, resolve_upload=False),
    input_option_requirements=(hd.HD_OPTION_REQUIREMENT,),
)

__all__ = ["WORKFLOW"]
