"""A small, generic 2x2 image-sheet workflow over ``LF_ImageGrid``."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from ..services.registry import InputValidationError, WorkflowCell, WorkflowNode
from .utils import (
    choice as _choice,
    integer as _integer,
    require_input_value as _require_image,
    resolve_load_image_reference,
)


_OUTPUT_PREFIX = "LF_Nodes/ImageSheet/2x2"
_UPLOADS = (
    (
        "top_left_image",
        "load_top_left",
        "1. Top-left image",
        "First image in row-major order: top row, left column.",
    ),
    (
        "top_right_image",
        "load_top_right",
        "2. Top-right image",
        "Second image in row-major order: top row, right column.",
    ),
    (
        "bottom_left_image",
        "load_bottom_left",
        "3. Bottom-left image",
        "Third image in row-major order: bottom row, left column.",
    ),
    (
        "bottom_right_image",
        "load_bottom_right",
        "4. Bottom-right image",
        "Fourth image in row-major order: bottom row, right column.",
    ),
)
_TEXT_DEFAULTS = {
    "sheet_title": "Image Sheet",
    "column_1_label": "Column 1",
    "column_2_label": "Column 2",
    "row_1_label": "Row 1",
    "row_2_label": "Row 2",
}
_BACKGROUND_OPTIONS = (
    (
        "transparent",
        "Transparent",
        "Keep transparent gaps and letterboxing in the saved PNG.",
    ),
    ("white", "White", "Use white for gaps and letterboxing."),
    ("black", "Black", "Use black for gaps and letterboxing."),
)
_BACKGROUND_IDS = tuple(option[0] for option in _BACKGROUND_OPTIONS)


def _single_line_text(
    inputs: Dict[str, Any],
    name: str,
    default: str,
    *,
    maximum: int,
) -> str:
    value = inputs.get(name, default)
    if not isinstance(value, str):
        raise InputValidationError(name)
    normalized = value.replace("\r", " ").replace("\n", " ").strip()
    if len(normalized) > maximum:
        raise ValueError(f"{name} must be at most {maximum} characters.")
    return normalized


def _boolean(inputs: Dict[str, Any], name: str, default: bool) -> bool:
    value = inputs.get(name, default)
    if not isinstance(value, bool):
        raise InputValidationError(name)
    return value


def _matrix_dataset(
    column_1: str,
    column_2: str,
    row_1: str,
    row_2: str,
) -> dict[str, Any]:
    """Build the flat 2-column/2-node LfDataDataset consumed row-major."""

    return {
        "columns": [
            {"id": "column_1", "title": column_1},
            {"id": "column_2", "title": column_2},
        ],
        "nodes": [
            {"id": "row_1", "value": row_1},
            {"id": "row_2", "value": row_2},
        ],
    }


def _configure(prompt: Dict[str, Any], inputs: Dict[str, Any]) -> None:
    # Validate the complete request before staging any of the four uploads.
    for input_id, _node_id, _label, _description in _UPLOADS:
        _require_image(inputs, input_id)

    title = _single_line_text(
        inputs,
        "sheet_title",
        _TEXT_DEFAULTS["sheet_title"],
        maximum=128,
    )
    column_1 = _single_line_text(
        inputs,
        "column_1_label",
        _TEXT_DEFAULTS["column_1_label"],
        maximum=64,
    )
    column_2 = _single_line_text(
        inputs,
        "column_2_label",
        _TEXT_DEFAULTS["column_2_label"],
        maximum=64,
    )
    row_1 = _single_line_text(
        inputs,
        "row_1_label",
        _TEXT_DEFAULTS["row_1_label"],
        maximum=64,
    )
    row_2 = _single_line_text(
        inputs,
        "row_2_label",
        _TEXT_DEFAULTS["row_2_label"],
        maximum=64,
    )
    cell_width = _integer(
        inputs,
        "cell_width",
        512,
        minimum=32,
        maximum=2048,
    )
    cell_height = _integer(
        inputs,
        "cell_height",
        512,
        minimum=32,
        maximum=2048,
    )
    gap_px = _integer(inputs, "gap_px", 8, minimum=0, maximum=256)
    background = _choice(
        inputs,
        "background",
        "transparent",
        _BACKGROUND_IDS,
    )
    show_headers = _boolean(inputs, "show_headers", True)

    resolved = [
        resolve_load_image_reference(inputs, input_id)
        for input_id, _node_id, _label, _description in _UPLOADS
    ]
    for reference, (_input_id, node_id, _label, _description) in zip(
        resolved, _UPLOADS
    ):
        prompt[node_id]["inputs"]["image"] = reference

    prompt["grid"]["inputs"].update(
        {
            "dataset": _matrix_dataset(column_1, column_2, row_1, row_2),
            "title": title,
            "cell_width": cell_width,
            "cell_height": cell_height,
            "gap_px": gap_px,
            "background": background,
            "show_headers": show_headers,
        }
    )
    prompt["save"]["inputs"]["filename_prefix"] = _OUTPUT_PREFIX


def _upload_cell(
    input_id: str,
    node_id: str,
    label: str,
    description: str,
) -> WorkflowCell:
    return WorkflowCell(
        node_id=node_id,
        id=input_id,
        value=label,
        shape="upload",
        description=description,
        props={
            "lfHtmlAttributes": {"accept": "image/*"},
            "lfLabel": label,
        },
    )


def _text_cell(
    input_id: str,
    label: str,
    default: str,
    description: str,
    *,
    maximum: int,
) -> WorkflowCell:
    return WorkflowCell(
        node_id="grid",
        id=input_id,
        value=label,
        shape="textfield",
        description=description,
        props={
            "lfHtmlAttributes": {
                "autocomplete": "off",
                "maxlength": maximum,
                "name": input_id,
                "type": "text",
            },
            "lfLabel": label,
            "lfHelper": {"showWhenFocused": False, "value": description},
            "lfValue": default,
        },
    )


def _number_cell(
    input_id: str,
    label: str,
    default: int,
    minimum: int,
    maximum: int,
    description: str,
) -> WorkflowCell:
    return WorkflowCell(
        node_id="grid",
        id=input_id,
        value=label,
        shape="textfield",
        description=description,
        props={
            "lfHtmlAttributes": {
                "autocomplete": "off",
                "max": maximum,
                "min": minimum,
                "name": input_id,
                "step": 1,
                "type": "number",
            },
            "lfLabel": label,
            "lfHelper": {"showWhenFocused": False, "value": description},
            "lfValue": str(default),
        },
    )


def _background_cell() -> WorkflowCell:
    description = (
        "Choose the color for gaps and unused letterbox space. Source transparency "
        "is preserved; Transparent keeps an RGBA PNG wherever headers do not paint "
        "an opaque label strip."
    )
    return WorkflowCell(
        node_id="grid",
        id="background",
        value="Background",
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
                    for option_id, option_label, option_description in _BACKGROUND_OPTIONS
                ]
            },
            "lfTextfieldProps": {
                "lfHelper": {"showWhenFocused": False, "value": description},
                "lfLabel": "Background",
            },
            "lfValue": "transparent",
        },
    )


def _headers_cell() -> WorkflowCell:
    return WorkflowCell(
        node_id="grid",
        id="show_headers",
        value="Show column and row labels",
        shape="toggle",
        description="Show the two column labels and two row labels around the image matrix.",
        props={
            "lfLabel": "Show column and row labels",
            "lfValue": True,
        },
    )


inputs = [
    *[
        _upload_cell(input_id, node_id, label, description)
        for input_id, node_id, label, description in _UPLOADS
    ],
    _text_cell(
        "sheet_title",
        "Sheet title",
        _TEXT_DEFAULTS["sheet_title"],
        "Optional title rendered above the complete 2x2 sheet.",
        maximum=128,
    ),
    _text_cell(
        "column_1_label",
        "Left column label",
        _TEXT_DEFAULTS["column_1_label"],
        "Header for the left column.",
        maximum=64,
    ),
    _text_cell(
        "column_2_label",
        "Right column label",
        _TEXT_DEFAULTS["column_2_label"],
        "Header for the right column.",
        maximum=64,
    ),
    _text_cell(
        "row_1_label",
        "Top row label",
        _TEXT_DEFAULTS["row_1_label"],
        "Header for the top row.",
        maximum=64,
    ),
    _text_cell(
        "row_2_label",
        "Bottom row label",
        _TEXT_DEFAULTS["row_2_label"],
        "Header for the bottom row.",
        maximum=64,
    ),
    _number_cell(
        "cell_width",
        "Cell width",
        512,
        32,
        2048,
        "Width of each image cell in pixels.",
    ),
    _number_cell(
        "cell_height",
        "Cell height",
        512,
        32,
        2048,
        "Height of each image cell in pixels.",
    ),
    _number_cell(
        "gap_px",
        "Gap",
        8,
        0,
        256,
        "Spacing between cells, headers, and the title, in pixels.",
    ),
    _background_cell(),
    _headers_cell(),
]

outputs = [
    WorkflowCell(
        node_id="save",
        id="image",
        shape="masonry",
        description="The saved 2x2 PNG image sheet.",
    ),
    WorkflowCell(
        node_id="display_dataset",
        id="dataset",
        shape="code",
        description="The populated LfDataDataset used for the row-major matrix.",
        props={"lfLanguage": "json"},
    ),
    WorkflowCell(
        node_id="display_receipt",
        id="receipt",
        shape="code",
        description="The lf.image_grid.receipt.v1 layout receipt.",
        props={"lfLanguage": "json"},
    ),
]

id = "image_sheet"
WORKFLOW = WorkflowNode(
    id=id,
    value="Compose Image Sheet",
    description=(
        "Arrange four uploaded images into a labeled 2x2 PNG sheet in deterministic "
        "row-major order. Images are contained inside equal cells, and transparency "
        "is carried through the image pipeline. Every source keeps its original "
        "dimensions and aspect ratio; the grid scales it to fit without cropping "
        "or stretching and letterboxes any unused cell area."
    ),
    category="Image Processing",
    inputs=inputs,
    outputs=outputs,
    configure_prompt=_configure,
    workflow_path=Path(__file__).resolve().with_suffix(".json"),
)

__all__ = ["WORKFLOW"]
