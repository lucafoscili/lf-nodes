"""Cut one shot into a registered sprite loop: pick, cut out, normalize, pack."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from ..services.registry import (
    InputValidationError,
    WorkflowCell,
    WorkflowModelAsset,
    WorkflowNode,
)
from .utils import resolve_load_image_reference


_DEFAULT_FRAME_COUNT = 24
_DEFAULT_COLUMNS = 6
_DEFAULT_MIN_PERIOD = 12
_DEFAULT_MAX_PERIOD = 96
_DEFAULT_MOTION_FLOOR = 0.6
_DEFAULT_CANVAS_SIZE = 256
_DEFAULT_CONTENT_HEIGHT = 144
_DEFAULT_BOTTOM_PADDING = 20
_MAX_CANVAS_SIZE = 2048
_MAX_FRAME_COUNT = 240

_RMBG2_MODEL_ASSETS = (
    WorkflowModelAsset(
        label="VNCCS RMBG-2.0 model",
        relative_paths=(
            "RMBG/RMBG-2.0/config.json",
            "RMBG/RMBG-2.0/model.safetensors",
            "RMBG/RMBG-2.0/birefnet.py",
            "RMBG/RMBG-2.0/BiRefNet_config.py",
        ),
    ),
)


def _integer(inputs: Dict[str, Any], field_id: str, default: int, minimum: int, maximum: int) -> int:
    raw = inputs.get(field_id, default)
    if isinstance(raw, list):
        raw = raw[0] if raw else default
    if raw in (None, ""):
        raw = default
    try:
        value = int(str(raw).strip())
    except (TypeError, ValueError) as error:
        raise InputValidationError(field_id) from error
    if value < minimum or value > maximum:
        raise InputValidationError(field_id)
    return value


def _number(inputs: Dict[str, Any], field_id: str, default: float, minimum: float, maximum: float) -> float:
    raw = inputs.get(field_id, default)
    if isinstance(raw, list):
        raw = raw[0] if raw else default
    if raw in (None, ""):
        raw = default
    try:
        value = float(str(raw).strip())
    except (TypeError, ValueError) as error:
        raise InputValidationError(field_id) from error
    if value < minimum or value > maximum:
        raise InputValidationError(field_id)
    return value


def settings(inputs: Dict[str, Any]) -> dict[str, Any]:
    frame_count = _integer(inputs, "frame_count", _DEFAULT_FRAME_COUNT, 1, _MAX_FRAME_COUNT)
    columns = _integer(inputs, "columns", _DEFAULT_COLUMNS, 1, _MAX_FRAME_COUNT)
    if columns > frame_count or frame_count % columns != 0:
        raise InputValidationError("columns")
    min_period = _integer(inputs, "min_period_frames", _DEFAULT_MIN_PERIOD, 2, 4096)
    max_period = _integer(inputs, "max_period_frames", _DEFAULT_MAX_PERIOD, 2, 4096)
    if max_period < min_period:
        raise InputValidationError("max_period_frames")
    canvas_size = _integer(inputs, "canvas_size", _DEFAULT_CANVAS_SIZE, 32, _MAX_CANVAS_SIZE)
    content_height = _integer(inputs, "content_height", _DEFAULT_CONTENT_HEIGHT, 8, _MAX_CANVAS_SIZE)
    bottom_padding = _integer(inputs, "bottom_padding", _DEFAULT_BOTTOM_PADDING, 0, _MAX_CANVAS_SIZE - 1)
    if content_height + bottom_padding > canvas_size:
        raise InputValidationError("content_height")
    return {
        "frame_count": frame_count,
        "columns": columns,
        "rows": frame_count // columns,
        "min_period_frames": min_period,
        "max_period_frames": max_period,
        "motion_floor": _number(inputs, "motion_floor", _DEFAULT_MOTION_FLOOR, 0.0, 4.0),
        "canvas_size": canvas_size,
        "content_height": content_height,
        "bottom_padding": bottom_padding,
    }


def apply_settings(prompt: Dict[str, Any], values: dict[str, Any]) -> None:
    prompt["select_loop"]["inputs"].update(
        {
            "target_count": values["frame_count"],
            "min_period_frames": values["min_period_frames"],
            "max_period_frames": values["max_period_frames"],
            "motion_floor": values["motion_floor"],
        }
    )
    prompt["normalize"]["inputs"].update(
        {
            "canvas_width": values["canvas_size"],
            "canvas_height": values["canvas_size"],
            "target_reference_alpha_height": values["content_height"],
            "reference_frame_index": 0,
            "bottom_padding": values["bottom_padding"],
        }
    )
    prompt["sprite_grid"]["inputs"].update(
        {
            "cell_width": values["canvas_size"],
            "cell_height": values["canvas_size"],
            "dataset": {
                "columns": [
                    {"id": f"frame_{index + 1:02d}", "title": ""}
                    for index in range(values["columns"])
                ],
                "nodes": [
                    {"id": f"row_{index + 1:02d}", "value": ""}
                    for index in range(values["rows"])
                ],
            },
        }
    )
    prefix = (
        "LF_Nodes/SpriteLoopCut/"
        f"{values['canvas_size']}px-content-{values['content_height']}px-"
        f"bottom-{values['bottom_padding']}px-f{values['frame_count']}"
    )
    prompt["save_frames"]["inputs"]["filename_prefix"] = f"{prefix}/frames"
    prompt["save_atlas"]["inputs"]["filename_prefix"] = (
        f"{prefix}/atlas-{values['columns']}x{values['rows']}"
    )


def _configure(prompt: Dict[str, Any], inputs: Dict[str, Any], *, resolve_uploads: bool) -> None:
    values = settings(inputs)
    if resolve_uploads:
        prompt["load_video"]["inputs"]["file"] = resolve_load_image_reference(inputs, "source_video")
    apply_settings(prompt, values)


def _configure_run(prompt: Dict[str, Any], inputs: Dict[str, Any]) -> None:
    _configure(prompt, inputs, resolve_uploads=True)


def _configure_download(prompt: Dict[str, Any], inputs: Dict[str, Any]) -> None:
    _configure(prompt, inputs, resolve_uploads=False)


def _number_cell(
    node_id: str,
    field_id: str,
    label: str,
    default: float | int,
    minimum: float | int,
    maximum: float | int,
    step: float | int,
    description: str,
) -> WorkflowCell:
    return WorkflowCell(
        node_id=node_id,
        id=field_id,
        value=label,
        shape="textfield",
        description=description,
        props={
            "lfHtmlAttributes": {
                "autocomplete": "off",
                "max": maximum,
                "min": minimum,
                "name": field_id,
                "step": step,
                "type": "number",
            },
            "lfLabel": label,
            "lfHelper": {"showWhenFocused": False, "value": description},
            "lfValue": str(default),
        },
    )


inputs = [
    WorkflowCell(
        node_id="load_video",
        id="source_video",
        value="Source shot",
        shape="upload",
        description=(
            "One video of the subject performing its action on a plain background, "
            "camera locked. A reference-restage or sprite-motion output works as is."
        ),
        props={
            "lfHtmlAttributes": {"accept": "video/mp4,video/webm,video/*"},
            "lfLabel": "Source shot",
        },
    ),
    _number_cell(
        "select_loop", "frame_count", "Loop frames", _DEFAULT_FRAME_COUNT, 1, _MAX_FRAME_COUNT, 1,
        "Frames in the finished loop. The chosen cycle is resampled to exactly this count.",
    ),
    _number_cell(
        "sprite_grid", "columns", "Atlas columns", _DEFAULT_COLUMNS, 1, _MAX_FRAME_COUNT, 1,
        "Cells per atlas row; must divide the loop frame count.",
    ),
    _number_cell(
        "select_loop", "min_period_frames", "Shortest cycle", _DEFAULT_MIN_PERIOD, 2, 4096, 1,
        "Shortest cycle to consider, in source frames.",
    ),
    _number_cell(
        "select_loop", "max_period_frames", "Longest cycle", _DEFAULT_MAX_PERIOD, 2, 4096, 1,
        "Longest cycle to consider, in source frames.",
    ),
    _number_cell(
        "select_loop", "motion_floor", "Motion floor", _DEFAULT_MOTION_FLOOR, 0.0, 4.0, 0.05,
        "Minimum motion inside a cycle as a multiple of the shot's median frame step. "
        "Keeps a frozen stretch from winning on a tiny seam.",
    ),
    _number_cell(
        "normalize", "canvas_size", "Canvas size", _DEFAULT_CANVAS_SIZE, 32, _MAX_CANVAS_SIZE, 1,
        "Square transparent cell for every frame.",
    ),
    _number_cell(
        "normalize", "content_height", "Visible-content height", _DEFAULT_CONTENT_HEIGHT, 8, _MAX_CANVAS_SIZE, 1,
        "Alpha height of the FIRST loop frame; one scale is shared by the whole loop, so keep about a third of the canvas free for the tallest or widest stroke (a wide tail needs less, a walk can take more). The run refuses to clip rather than crop.",
    ),
    _number_cell(
        "normalize", "bottom_padding", "Bottom padding", _DEFAULT_BOTTOM_PADDING, 0, _MAX_CANVAS_SIZE - 1, 1,
        "Transparent rows below every frame's lowest opaque pixel (the runtime's grounding row).",
    ),
]

outputs = [
    WorkflowCell(
        node_id="save_frames",
        id="frames",
        shape="masonry",
        description="Every registered transparent loop frame, in order.",
    ),
    WorkflowCell(
        node_id="save_atlas",
        id="atlas",
        shape="masonry",
        description="The zero-gap row-major atlas the runtime reads.",
    ),
    WorkflowCell(
        node_id="display_loop_receipt",
        id="loop_receipt",
        shape="code",
        description="Chosen start, period, seam and motion scores, cycle seconds and the intended fps.",
        props={"lfLanguage": "json"},
    ),
    WorkflowCell(
        node_id="display_normalization_receipt",
        id="normalization_receipt",
        shape="code",
        description="Shared scale, per-frame alpha bounds and grounding rows.",
        props={"lfLanguage": "json"},
    ),
]

id = "sprite_loop_cut"
WORKFLOW = WorkflowNode(
    id=id,
    value="Sprite Loop Cut",
    description=(
        "Turn one action shot into a registered sprite loop: the best self-closing "
        "segment is chosen by seam versus motion, resampled to a fixed frame count, "
        "cut out with RMBG-2.0, registered on one transparent canvas, and packed into "
        "a zero-gap atlas with receipts the runtime can trust."
    ),
    category="Image Processing",
    inputs=inputs,
    outputs=outputs,
    configure_prompt=_configure_run,
    configure_download=_configure_download,
    workflow_path=Path(__file__).resolve().with_suffix(".json"),
    required_model_assets=_RMBG2_MODEL_ASSETS,
)

__all__ = ["WORKFLOW", "settings", "apply_settings"]
