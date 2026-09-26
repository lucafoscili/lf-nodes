"""Local vision-LLM prose authoring with MiniMax H3 writing guidance."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Dict

from ..services.registry import (
    InputValidationError,
    WorkflowCardPresentation,
    WorkflowCell,
    WorkflowNode,
)
from .utils import (
    choice,
    has_input_value,
    required_text,
    resolve_load_image_reference,
)


DEFAULT_ENDPOINT = "http://127.0.0.1:1234/api/v1/chat"
DEFAULT_INTENT = (
    "Create a cinematic video with clear action, coherent camera movement, "
    "and synchronized environmental sound."
)
DEFAULT_DURATION_SECONDS = 6.0
DEFAULT_MODEL = ""
DEFAULT_TEMPERATURE = 0.2
DEFAULT_REASONING = "vision"
DEFAULT_REVIEW = True

_MAX_REFERENCE_IMAGES = 9
_PICTURE_IDS = tuple(
    f"picture_{ordinal}" for ordinal in range(1, _MAX_REFERENCE_IMAGES + 1)
)
_FIXED_REFERENCE_COUNTS = {
    "t2va": 0,
    "i2va": 1,
    "fl2va": 2,
    "l2va": 1,
}
_REASONING_OPTIONS = (
    (
        "vision",
        "Vision only",
        "Enable reasoning when writing or reviewing with images; keep text-only requests direct.",
    ),
    (
        "off",
        "Off",
        "Use LM Studio's supported non-thinking mode so the answer budget is "
        "reserved for the H3 prompt.",
    ),
    (
        "auto",
        "Model default",
        "Let the loaded model choose whether to reason before answering.",
    ),
    (
        "on",
        "On",
        "Ask LM Studio to enable model reasoning when the loaded model supports it.",
    ),
)
_MODE_OPTIONS = (
    (
        "auto",
        "Automatic",
        "Write from text alone, or use uploaded Pictures as references.",
    ),
    (
        "t2va",
        "Text to video + audio",
        "Write from text only; no Picture uploads are used.",
    ),
    (
        "i2va",
        "First-frame image",
        "Use Picture 1 as the first frame of the target video.",
    ),
    (
        "fl2va",
        "First + last frames",
        "Use Picture 1 as the first frame and Picture 2 as the last frame.",
    ),
    (
        "l2va",
        "Last-frame image",
        "Use Picture 1 as the last frame of the target video.",
    ),
    (
        "ref2va",
        "Full reference",
        "Use one to nine ordered Pictures as subject, scene, or style references.",
    ),
)


def _bounded_float(
    inputs: Dict[str, Any],
    name: str,
    default: float,
    *,
    minimum: float,
    maximum: float | None,
) -> float:
    value = inputs.get(name, default)
    if value in (None, ""):
        value = default
    if isinstance(value, bool):
        raise InputValidationError(name)
    try:
        parsed = float(str(value).strip())
    except (TypeError, ValueError) as error:
        raise InputValidationError(name) from error
    if not math.isfinite(parsed):
        raise InputValidationError(name)
    if parsed < minimum:
        raise ValueError(f"{name} must be at least {minimum}.")
    if maximum is not None and parsed > maximum:
        raise ValueError(f"{name} must be at most {maximum}.")
    return parsed


def _text(
    inputs: Dict[str, Any],
    name: str,
    default: str,
    *,
    allow_empty: bool,
) -> str:
    value = inputs.get(name, default)
    if not isinstance(value, str):
        raise InputValidationError(name)
    normalized = value.strip()
    if not normalized and not allow_empty:
        raise InputValidationError(name)
    return normalized


def _boolean(inputs: Dict[str, Any], name: str, default: bool) -> bool:
    """Accept the native JSON boolean submitted by a Runner toggle."""

    value = inputs.get(name, default)
    if not isinstance(value, bool):
        raise InputValidationError(name)
    return value


def _reference_fields(inputs: Dict[str, Any], mode: str) -> tuple[str, ...]:
    """Validate one contiguous Picture prefix without resolving any upload."""

    present_fields: list[str] = []
    gap_seen = False
    for field_id in _PICTURE_IDS:
        present = has_input_value(inputs, field_id)
        if not present:
            gap_seen = True
            continue
        if gap_seen:
            raise ValueError("Picture uploads cannot contain a gap.")
        present_fields.append(field_id)

    count = len(present_fields)
    if mode == "ref2va":
        if count == 0:
            raise InputValidationError("picture_1")
        return tuple(present_fields)

    expected = _FIXED_REFERENCE_COUNTS[mode]
    if count < expected:
        raise InputValidationError(f"picture_{count + 1}")
    if count > expected:
        noun = "Picture upload" if expected == 1 else "Picture uploads"
        raise ValueError(f"{mode} requires exactly {expected} {noun}.")
    return tuple(present_fields)


def _configure(prompt: Dict[str, Any], inputs: Dict[str, Any]) -> None:
    # Validate scalar controls plus the mode/count/gap contract before staging.
    mode = choice(inputs, "mode", "auto", tuple(option[0] for option in _MODE_OPTIONS))
    if mode == "auto":
        mode = (
            "ref2va"
            if any(has_input_value(inputs, field_id) for field_id in _PICTURE_IDS)
            else "t2va"
        )
    intent = required_text(inputs, "intent")
    instructions = _text(inputs, "instructions", "", allow_empty=True)
    duration_seconds = _bounded_float(
        inputs,
        "duration",
        DEFAULT_DURATION_SECONDS,
        minimum=0.001,
        maximum=5_999.999,
    )
    endpoint = _text(
        inputs,
        "endpoint",
        DEFAULT_ENDPOINT,
        allow_empty=False,
    )
    model = _text(inputs, "model", DEFAULT_MODEL, allow_empty=True)
    temperature = _bounded_float(
        inputs,
        "temperature",
        DEFAULT_TEMPERATURE,
        minimum=0.0,
        maximum=1.0,
    )
    reasoning = choice(
        inputs,
        "reasoning",
        DEFAULT_REASONING,
        (option[0] for option in _REASONING_OPTIONS),
    )
    review = _boolean(inputs, "review", DEFAULT_REVIEW)
    reference_fields = _reference_fields(inputs, mode)
    reference_count = len(reference_fields)

    resolved_references = [
        resolve_load_image_reference(inputs, field_id)
        for field_id in reference_fields
    ]

    prompt["h3_prompt_maker"]["inputs"].update(
        {
            "intent": intent,
            "instructions": instructions,
            "mode": mode,
            "duration_seconds": duration_seconds,
            "url": endpoint,
            "model": model,
            "temperature": temperature,
            "reasoning": reasoning,
            "review": review,
        }
    )

    list_inputs = prompt["image_list"]["inputs"]
    for ordinal in range(1, _MAX_REFERENCE_IMAGES + 1):
        picture_node_id = f"picture_{ordinal}"
        list_input = f"image_{ordinal}"
        if ordinal <= reference_count:
            prompt[picture_node_id]["inputs"]["image"] = resolved_references[
                ordinal - 1
            ]
            list_inputs[list_input] = [picture_node_id, 0]
        else:
            prompt.pop(picture_node_id, None)
            list_inputs.pop(list_input, None)

    if reference_count:
        prompt["h3_prompt_maker"]["inputs"]["image"] = ["image_list", 0]
    else:
        prompt.pop("image_list", None)
        prompt["h3_prompt_maker"]["inputs"].pop("image", None)


def _mode_cell() -> WorkflowCell:
    description = (
        "Automatic uses uploaded Pictures as references. Choose a frame mode "
        "only when a Picture must be an exact first or last frame."
    )
    return WorkflowCell(
        node_id="h3_prompt_maker",
        id="mode",
        value="H3 mode",
        shape="select",
        description=description,
        props={
            "lfDataset": {
                "nodes": [
                    {
                        "description": option_description,
                        "id": option_id,
                        "value": option_label,
                        "workflowValue": option_id,
                    }
                    for option_id, option_label, option_description in _MODE_OPTIONS
                ]
            },
            "lfTextfieldProps": {
                "lfHelper": {"showWhenFocused": False, "value": description},
                "lfLabel": "H3 mode",
            },
            "lfValue": "auto",
        },
        advanced=True,
    )


def _reasoning_cell() -> WorkflowCell:
    description = (
        "Control reasoning for the writer and optional review. Vision only "
        "enables reasoning when reference images are present."
    )
    return WorkflowCell(
        node_id="h3_prompt_maker",
        id="reasoning",
        value="Reasoning",
        shape="select",
        description=description,
        props={
            "lfDataset": {
                "nodes": [
                    {
                        "description": option_description,
                        "id": option_id,
                        "value": option_label,
                        "workflowValue": option_id,
                    }
                    for option_id, option_label, option_description in (
                        _REASONING_OPTIONS
                    )
                ]
            },
            "lfTextfieldProps": {
                "lfHelper": {"showWhenFocused": False, "value": description},
                "lfLabel": "Reasoning",
            },
            "lfValue": DEFAULT_REASONING,
        },
        required=False,
        advanced=True,
    )


def _text_cell(
    *,
    node_id: str,
    cell_id: str,
    label: str,
    default: str,
    description: str,
    textarea: bool = False,
    advanced: bool = False,
    required: bool = True,
) -> WorkflowCell:
    props: dict[str, Any] = {
        "lfHtmlAttributes": {
            "autocomplete": "off",
            "name": cell_id,
            "type": "text",
        },
        "lfLabel": label,
        "lfHelper": {"showWhenFocused": False, "value": description},
        "lfValue": default,
    }
    if textarea:
        props["lfStyling"] = "textarea"
    return WorkflowCell(
        node_id=node_id,
        id=cell_id,
        value=label,
        shape="textfield",
        description=description,
        props=props,
        required=required,
        advanced=advanced,
    )


def _number_cell(
    *,
    node_id: str,
    cell_id: str,
    label: str,
    default: str,
    minimum: float,
    maximum: float | None,
    step: float,
    description: str,
    advanced: bool = False,
    required: bool = True,
) -> WorkflowCell:
    attributes: dict[str, Any] = {
        "autocomplete": "off",
        "min": minimum,
        "name": cell_id,
        "step": step,
        "type": "number",
    }
    if maximum is not None:
        attributes["max"] = maximum
    return WorkflowCell(
        node_id=node_id,
        id=cell_id,
        value=label,
        shape="textfield",
        description=description,
        props={
            "lfHtmlAttributes": attributes,
            "lfLabel": label,
            "lfHelper": {"showWhenFocused": False, "value": description},
            "lfValue": default,
        },
        required=required,
        advanced=advanced,
    )


def _picture_cell(ordinal: int) -> WorkflowCell:
    label = f"Picture {ordinal}"
    description = (
        f"Ordered MiniMax H3 reference <Picture {ordinal}>. Uploads must form a "
        "continuous prefix beginning with Picture 1."
    )
    return WorkflowCell(
        node_id=f"picture_{ordinal}",
        id=f"picture_{ordinal}",
        value=label,
        shape="upload",
        description=description,
        props={
            "lfHtmlAttributes": {"accept": "image/*"},
            "lfLabel": label,
            "lfHelper": {"showWhenFocused": False, "value": description},
        },
        required=False,
        advanced=ordinal >= 3,
    )


input_intent = _text_cell(
    node_id="h3_prompt_maker",
    cell_id="intent",
    label="Creative intent",
    default=DEFAULT_INTENT,
    description=(
        "Describe the desired video in ordinary language. Include any must-have "
        "action, camera, dialogue, sound, music, or reference-retention choices."
    ),
    textarea=True,
)
input_duration = _number_cell(
    node_id="h3_prompt_maker",
    cell_id="duration",
    label="Duration (seconds)",
    default="6",
    minimum=0.001,
    maximum=5_999.999,
    step=0.001,
    description="Exact target duration used to align H3 shot timestamps and frame references.",
)
input_endpoint = _text_cell(
    node_id="h3_prompt_maker",
    cell_id="endpoint",
    label="LM Studio endpoint",
    default=DEFAULT_ENDPOINT,
    description=(
        "LM Studio native /api/v1/chat URL. Image modes require a "
        "vision-capable model served by this endpoint."
    ),
    advanced=True,
    required=False,
)
input_model = _text_cell(
    node_id="h3_prompt_maker",
    cell_id="model",
    label="Model",
    default=DEFAULT_MODEL,
    description=(
        "Optional LM Studio model identifier shared by every stage. Leave empty "
        "to use the sole LLM already loaded at the endpoint."
    ),
    required=False,
    advanced=True,
)
input_instructions = _text_cell(
    node_id="h3_prompt_maker",
    cell_id="instructions",
    label="Additional instructions",
    default="",
    description="Optional preferences for the writer, such as tone, pacing, or creative constraints.",
    textarea=True,
    advanced=True,
    required=False,
)
input_temperature = _number_cell(
    node_id="h3_prompt_maker",
    cell_id="temperature",
    label="Temperature",
    default="0.2",
    minimum=0.0,
    maximum=1.0,
    step=0.1,
    description="Sampling randomness for writing and optional review.",
    advanced=True,
    required=False,
)
input_reasoning = _reasoning_cell()
input_review = WorkflowCell(
    node_id="h3_prompt_maker",
    id="review",
    value="Review",
    shape="toggle",
    description=(
        "Review and revise the written prompt against your idea and reference "
        "images. Disable to use the writer's prompt directly."
    ),
    props={"lfLabel": "Review", "lfValue": DEFAULT_REVIEW},
    required=False,
)
outputs = [
    WorkflowCell(
        node_id="display_prompt",
        id="prompt",
        shape="code",
        description="MiniMax H3 prompt prose returned by the writer or optional reviewer.",
        props={"lfLanguage": "markdown"},
    ),
    WorkflowCell(
        node_id="display_report",
        id="validation_report",
        shape="code",
        description="Authoring and review status; structural validation is not performed.",
        props={"lfLanguage": "json"},
    ),
    WorkflowCell(
        node_id="display_inventory",
        id="visual_inventory",
        shape="code",
        description=(
            "Reference Picture list for direct vision authoring. Images are read "
            "by the writer; no separate visual inventory is extracted."
        ),
        props={"lfLanguage": "json"},
    ),
]


id = "minimax_h3_prompt_maker"
WORKFLOW = WorkflowNode(
    id=id,
    value="MiniMax H3 / Prompt Maker",
    description=(
        "Turn a plain-language video idea and optional ordered Picture references "
        "into a copy-ready MiniMax H3 prompt using the official writing guides, "
        "direct image understanding, and optional review."
    ),
    category="MiniMax H3",
    card=WorkflowCardPresentation(
        summary="Write an H3 prompt from your idea and optional reference images."
    ),
    inputs=[
        _mode_cell(),
        input_intent,
        input_duration,
        *[_picture_cell(ordinal) for ordinal in range(1, 3)],
        input_model,
        input_review,
        input_endpoint,
        input_temperature,
        input_reasoning,
        input_instructions,
        *[_picture_cell(ordinal) for ordinal in range(3, 10)],
    ],
    outputs=outputs,
    configure_prompt=_configure,
    workflow_path=Path(__file__).resolve().with_suffix(".json"),
)

__all__ = ["WORKFLOW"]
