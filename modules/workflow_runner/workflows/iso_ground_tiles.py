"""Turn one top-down texture into a seamless wrap and an isometric diamond tile set."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from ..services.registry import InputValidationError, WorkflowCell, WorkflowNode
from .utils import resolve_load_image_reference


_DEFAULT_BLEND = 0.25
_DEFAULT_TILE_WIDTH = 128
_DEFAULT_TILE_HEIGHT = 64
_DEFAULT_VARIANTS = 4
_DEFAULT_TEXTURE_SCALE = 0.5
_DEFAULT_SEED = 42
_MAX_TILE_EDGE = 1024
_MAX_VARIANTS = 64


def _read(inputs: Dict[str, Any], field_id: str, default: Any) -> str:
    raw = inputs.get(field_id, default)
    if isinstance(raw, list):
        raw = raw[0] if raw else default
    if raw in (None, ""):
        raw = default
    return str(raw).strip()


def _integer(inputs: Dict[str, Any], field_id: str, default: int, minimum: int, maximum: int) -> int:
    try:
        value = int(_read(inputs, field_id, default))
    except (TypeError, ValueError) as error:
        raise InputValidationError(field_id) from error
    if value < minimum or value > maximum:
        raise InputValidationError(field_id)
    return value


def _number(inputs: Dict[str, Any], field_id: str, default: float, minimum: float, maximum: float) -> float:
    try:
        value = float(_read(inputs, field_id, default))
    except (TypeError, ValueError) as error:
        raise InputValidationError(field_id) from error
    if value < minimum or value > maximum:
        raise InputValidationError(field_id)
    return value


def settings(inputs: Dict[str, Any]) -> dict[str, Any]:
    return {
        "blend_fraction": _number(inputs, "blend_fraction", _DEFAULT_BLEND, 0.02, 0.5),
        "tile_width": _integer(inputs, "tile_width", _DEFAULT_TILE_WIDTH, 8, _MAX_TILE_EDGE),
        "tile_height": _integer(inputs, "tile_height", _DEFAULT_TILE_HEIGHT, 4, _MAX_TILE_EDGE),
        "variants": _integer(inputs, "variants", _DEFAULT_VARIANTS, 1, _MAX_VARIANTS),
        "seed": _integer(inputs, "seed", _DEFAULT_SEED, 0, 2**31 - 1),
        "texture_scale": _number(inputs, "texture_scale", _DEFAULT_TEXTURE_SCALE, 0.05, 4.0),
    }


def apply_settings(prompt: Dict[str, Any], values: dict[str, Any]) -> None:
    prompt["seamless"]["inputs"]["blend_fraction"] = values["blend_fraction"]
    prompt["diamonds"]["inputs"].update(
        {
            "tile_width": values["tile_width"],
            "tile_height": values["tile_height"],
            "variants": values["variants"],
            "seed": values["seed"],
            "texture_scale": values["texture_scale"],
        }
    )
    prefix = (
        "LF_Nodes/IsoGroundTiles/"
        f"{values['tile_width']}x{values['tile_height']}-v{values['variants']}-seed-{values['seed']}"
    )
    prompt["save_texture"]["inputs"]["filename_prefix"] = f"{prefix}/texture"
    prompt["save_tiles"]["inputs"]["filename_prefix"] = f"{prefix}/tiles"


def _configure(prompt: Dict[str, Any], inputs: Dict[str, Any], *, resolve_uploads: bool) -> None:
    values = settings(inputs)
    if resolve_uploads:
        prompt["load_texture"]["inputs"]["image"] = resolve_load_image_reference(inputs, "source_texture")
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
        node_id="load_texture",
        id="source_texture",
        value="Top-down texture",
        shape="upload",
        description=(
            "One square top-down ground texture (grass, sand, water, stone). It does "
            "not need to tile yet; the first step makes it wrap."
        ),
        props={"lfHtmlAttributes": {"accept": "image/*"}, "lfLabel": "Top-down texture"},
    ),
    _number_cell(
        "seamless", "blend_fraction", "Seam blend", _DEFAULT_BLEND, 0.02, 0.5, 0.01,
        "Width of the blend that hides the wrap seam, as a fraction of the texture size.",
    ),
    _number_cell(
        "diamonds", "tile_width", "Tile width", _DEFAULT_TILE_WIDTH, 8, _MAX_TILE_EDGE, 2,
        "Diamond tile width in pixels. Den draws 64 px cells from 128 px tiles.",
    ),
    _number_cell(
        "diamonds", "tile_height", "Tile height", _DEFAULT_TILE_HEIGHT, 4, _MAX_TILE_EDGE, 2,
        "Diamond tile height in pixels; half the width for the classic 2:1 diamond.",
    ),
    _number_cell(
        "diamonds", "variants", "Variants", _DEFAULT_VARIANTS, 1, _MAX_VARIANTS, 1,
        "How many differently offset diamonds to cut so repetition breaks up.",
    ),
    _number_cell(
        "diamonds", "texture_scale", "Texture per tile", _DEFAULT_TEXTURE_SCALE, 0.05, 4.0, 0.05,
        "Fraction of the texture one diamond spans along its diagonal. Smaller means finer grain.",
    ),
    _number_cell(
        "diamonds", "seed", "Seed", _DEFAULT_SEED, 0, 2**31 - 1, 1,
        "Seed for the variant offsets; the same seed always cuts the same tiles.",
    ),
]

outputs = [
    WorkflowCell(
        node_id="save_tiles",
        id="tiles",
        shape="masonry",
        description="One-row RGBA atlas of diamond tiles with transparent corners.",
    ),
    WorkflowCell(
        node_id="save_texture",
        id="texture",
        shape="masonry",
        description="The seamless top-down texture the tiles were cut from.",
    ),
    WorkflowCell(
        node_id="display_receipt",
        id="receipt",
        shape="code",
        description="Tile geometry, seed, offsets and the projection used.",
        props={"lfLanguage": "json"},
    ),
]

id = "iso_ground_tiles"
WORKFLOW = WorkflowNode(
    id=id,
    value="Iso Ground Tiles",
    description=(
        "Make a top-down texture wrap seamlessly, then cut isometric diamond tiles "
        "from it at seeded offsets: the top-down square rotated 45 degrees and "
        "squashed 2:1, so every variant tiles with every other."
    ),
    category="Image Processing",
    inputs=inputs,
    outputs=outputs,
    configure_prompt=_configure_run,
    configure_download=_configure_download,
    workflow_path=Path(__file__).resolve().with_suffix(".json"),
)

__all__ = ["WORKFLOW", "settings", "apply_settings"]
