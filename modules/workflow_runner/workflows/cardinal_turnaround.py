"""Assemble four cardinal frames into one registered 3D-ready turnaround."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from ..services.registry import (
    WorkflowCardPresentation,
    WorkflowCell,
    WorkflowHeroImage,
    WorkflowModelAsset,
    WorkflowNode,
)
from .utils import (
    integer,
    require_input_value,
    resolve_load_image_reference,
)


_DEFAULT_CANVAS_SIZE = 1024
_DEFAULT_CONTENT_HEIGHT = 900
_DEFAULT_BOTTOM_PADDING = 48
_MAX_CANVAS_SIZE = 2048

_DIRECTIONS = (
    (
        "front",
        "Front",
        "Straight-on front frame. This is the registration reference: its visible "
        "height and horizontal center define the one transform shared by all views.",
    ),
    (
        "right",
        "Subject right",
        "The subject's anatomical right profile, not the camera operator's right.",
    ),
    (
        "back",
        "Back",
        "Straight-on rear frame with the same camera distance and lens as the front.",
    ),
    (
        "left",
        "Subject left",
        "The subject's anatomical left profile, not the camera operator's left.",
    ),
)

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


def _settings(inputs: Dict[str, Any]) -> tuple[int, int, int]:
    canvas_size = integer(
        inputs,
        "canvas_size",
        _DEFAULT_CANVAS_SIZE,
        minimum=256,
        maximum=_MAX_CANVAS_SIZE,
    )
    content_height = integer(
        inputs,
        "content_height",
        _DEFAULT_CONTENT_HEIGHT,
        minimum=64,
        maximum=_MAX_CANVAS_SIZE,
    )
    bottom_padding = integer(
        inputs,
        "bottom_padding",
        _DEFAULT_BOTTOM_PADDING,
        minimum=0,
        maximum=_MAX_CANVAS_SIZE - 1,
    )
    if content_height + bottom_padding > canvas_size:
        raise ValueError(
            "content_height plus bottom_padding must fit inside canvas_size."
        )
    return canvas_size, content_height, bottom_padding


def _apply_settings(
    prompt: Dict[str, Any],
    *,
    canvas_size: int,
    content_height: int,
    bottom_padding: int,
) -> None:
    prompt["normalize_views"]["inputs"].update(
        {
            "canvas_width": canvas_size,
            "canvas_height": canvas_size,
            "target_reference_alpha_height": content_height,
            "reference_frame_index": 0,
            "bottom_padding": bottom_padding,
        }
    )
    prompt["contact_sheet"]["inputs"].update(
        {
            "cell_width": canvas_size,
            "cell_height": canvas_size,
        }
    )

    prefix = (
        "LF_Nodes/CardinalTurnaround/"
        f"{canvas_size}px-content-{content_height}px-bottom-{bottom_padding}px"
    )
    for direction, _label, _description in _DIRECTIONS:
        prompt[f"save_{direction}"]["inputs"]["filename_prefix"] = (
            f"{prefix}/{direction}"
        )
    prompt["save_contact_sheet"]["inputs"]["filename_prefix"] = (
        f"{prefix}/contact-sheet"
    )


def _configure(
    prompt: Dict[str, Any],
    inputs: Dict[str, Any],
    *,
    resolve_uploads: bool,
) -> None:
    canvas_size, content_height, bottom_padding = _settings(inputs)

    if resolve_uploads:
        for direction, _label, _description in _DIRECTIONS:
            require_input_value(inputs, f"{direction}_image")
        resolved = {
            direction: resolve_load_image_reference(inputs, f"{direction}_image")
            for direction, _label, _description in _DIRECTIONS
        }
        for direction, reference in resolved.items():
            prompt[f"load_{direction}"]["inputs"]["image"] = reference

    _apply_settings(
        prompt,
        canvas_size=canvas_size,
        content_height=content_height,
        bottom_padding=bottom_padding,
    )


def _configure_run(prompt: Dict[str, Any], inputs: Dict[str, Any]) -> None:
    _configure(prompt, inputs, resolve_uploads=True)


def _configure_download(prompt: Dict[str, Any], inputs: Dict[str, Any]) -> None:
    _configure(prompt, inputs, resolve_uploads=False)


def _upload_cell(direction: str, label: str, description: str) -> WorkflowCell:
    field_id = f"{direction}_image"
    return WorkflowCell(
        node_id=f"load_{direction}",
        id=field_id,
        value=f"{label} frame",
        shape="upload",
        description=description,
        props={
            "lfHtmlAttributes": {"accept": "image/*"},
            "lfLabel": f"{label} frame",
        },
    )


def _number_cell(
    field_id: str,
    label: str,
    default: int,
    minimum: int,
    maximum: int,
    description: str,
) -> WorkflowCell:
    return WorkflowCell(
        node_id="normalize_views",
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
                "step": 1,
                "type": "number",
            },
            "lfLabel": label,
            "lfHelper": {"showWhenFocused": False, "value": description},
            "lfValue": str(default),
        },
    )


inputs = [
    *[
        _upload_cell(direction, label, description)
        for direction, label, description in _DIRECTIONS
    ],
    _number_cell(
        "canvas_size",
        "Canvas size",
        _DEFAULT_CANVAS_SIZE,
        256,
        _MAX_CANVAS_SIZE,
        "Square transparent canvas for every saved view. Larger canvases retain more "
        "edge detail but use more memory in later 3D reconstruction.",
    ),
    _number_cell(
        "content_height",
        "Visible-content height",
        _DEFAULT_CONTENT_HEIGHT,
        64,
        _MAX_CANVAS_SIZE,
        "How tall the front frame's non-transparent bounds should become. One scale "
        "derived from that front frame is reused for all four views, so equipment and "
        "shadows inside the alpha bounds count too.",
    ),
    _number_cell(
        "bottom_padding",
        "Bottom padding",
        _DEFAULT_BOTTOM_PADDING,
        0,
        _MAX_CANVAS_SIZE - 1,
        "Transparent rows below each view's lowest non-transparent pixel. Each view "
        "gets only this vertical baseline correction; scale and horizontal pivot stay "
        "shared with the front frame.",
    ),
]

outputs = [
    *[
        WorkflowCell(
            node_id=f"save_{direction}",
            id=direction,
            shape="masonry",
            description=f"One registered transparent PNG for the {label.lower()} view.",
        )
        for direction, label, _description in _DIRECTIONS
    ],
    WorkflowCell(
        node_id="save_contact_sheet",
        id="contact_sheet",
        shape="masonry",
        description=(
            "Full-resolution labeled contact sheet in front, subject-right, back, "
            "subject-left order. Use it for review, not as a replacement for the four "
            "separate reconstruction inputs."
        ),
    ),
    WorkflowCell(
        node_id="display_normalization_receipt",
        id="normalization_receipt",
        shape="code",
        description=(
            "Shared scale and horizontal pivot, per-view alpha baselines, measured "
            "bounds, and clipping policy. Alpha bounds include equipment and shadows."
        ),
        props={"lfLanguage": "json"},
    ),
]

id = "assemble_cardinal_turnaround"
WORKFLOW = WorkflowNode(
    id=id,
    value="Assemble Cardinal Turnaround",
    description=(
        "Turn front, subject-right, back, and subject-left frames into four separately "
        "saved transparent PNGs with one shared scale and horizontal registration. "
        "Background removal and alpha validation run on every input; only vertical "
        "alpha-baseline alignment varies by view. Different source canvas sizes are "
        "contain-fitted into the front canvas with transparent centered padding and "
        "no crop. Use the same camera profile, distance, and subject framing for "
        "trustworthy proportions."
    ),
    category="Image Processing",
    card=WorkflowCardPresentation(
        summary="Align four supplied views on transparent canvases.",
        hero=WorkflowHeroImage(
            asset="image/cardinal-turnaround.webp",
            alt=(
                "Four actual saved transparent views of an original adult explorer, "
                "labeled front, subject-right, back, and subject-left."
            ),
        ),
    ),
    inputs=inputs,
    outputs=outputs,
    configure_prompt=_configure_run,
    configure_download=_configure_download,
    workflow_path=Path(__file__).resolve().with_suffix(".json"),
    required_model_assets=_RMBG2_MODEL_ASSETS,
)

__all__ = ["WORKFLOW"]
