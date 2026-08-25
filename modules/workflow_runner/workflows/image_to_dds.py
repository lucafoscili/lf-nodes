from pathlib import Path
from typing import Any, Dict

from ...dds_formats import MIP_POLICIES, PIXEL_FORMATS
from ..services.registry import InputValidationError, WorkflowCell, WorkflowNode
from .utils import required_text as _required_text, resolve_load_image_reference


def _required_choice(
    inputs: Dict[str, Any],
    name: str,
    choices: tuple[str, ...],
) -> str:
    value = inputs.get(name)
    if not isinstance(value, str) or value not in choices:
        raise InputValidationError(name)
    return value


# region Workflow Config
def _configure(prompt: Dict[str, Any], inputs: Dict[str, Any]) -> None:
    filename_prefix = _required_text(inputs, "filename_prefix")
    pixel_format = _required_choice(inputs, "pixel_format", PIXEL_FORMATS)
    mip_policy = _required_choice(inputs, "mip_policy", MIP_POLICIES)
    source_reference = resolve_load_image_reference(inputs, "source_path")

    prompt["load_image"]["inputs"]["image"] = source_reference
    prompt["save_dds"]["inputs"].update(
        {
            "filename_prefix": filename_prefix,
            "pixel_format": pixel_format,
            "mip_policy": mip_policy,
        }
    )
# endregion


def _select_cell(
    cell_id: str,
    label: str,
    default: str,
    description: str,
    options: tuple[tuple[str, str, str], ...],
) -> WorkflowCell:
    return WorkflowCell(
        node_id="save_dds",
        id=cell_id,
        shape="select",
        value=label,
        description=description,
        props={
            "lfDataset": {
                "nodes": [
                    {
                        "description": option_description,
                        "id": value,
                        "value": option_label,
                        "workflowValue": value,
                    }
                    for value, option_label, option_description in options
                ],
            },
            "lfTextfieldProps": {"lfLabel": label},
            "lfValue": default,
        },
    )


# region Inputs
input_upload = WorkflowCell(
    node_id="load_image",
    id="source_path",
    value="Source image",
    shape="upload",
    description=(
        "Choose one image to convert. PNG, JPEG, and WebP are good choices. "
        "If the file has transparency, this workflow carries it into RGBA32 or BC3."
    ),
    props={
        "lfHtmlAttributes": {
            "accept": "image/*",
        },
        "lfLabel": "1. Choose an image",
    },
)

input_filename_prefix = WorkflowCell(
    node_id="save_dds",
    id="filename_prefix",
    value="Filename prefix",
    shape="textfield",
    description=(
        "This is the folder and filename inside ComfyUI's output directory. "
        "The .dds extension and a collision-safe counter are added automatically; "
        "no timestamp is added."
    ),
    props={
        "lfHtmlAttributes": {
            "autocomplete": "off",
            "name": "filename_prefix",
            "placeholder": "LF_Nodes/DDS",
            "type": "text",
        },
        "lfLabel": "2. Choose an output name",
        "lfValue": "LF_Nodes/DDS",
    },
)

input_pixel_format = _select_cell(
    "pixel_format",
    "3. Choose how pixels are stored",
    "RGBA32",
    (
        "RGBA32 is the safest default because it keeps transparency. RGB24 is "
        "uncompressed and opaque. BC1 is smaller and opaque. BC3 is smaller and "
        "keeps transparency. Opaque formats stop with an error if alpha would be lost."
    ),
    (
        (
            "RGB24",
            "RGB24 — Uncompressed, opaque",
            "Exact 8-bit RGB channels with no transparency. Rejects an image that contains non-opaque alpha.",
        ),
        (
            "RGBA32",
            "RGBA32 — Uncompressed + transparency (recommended)",
            "Exact 8-bit red, green, blue, and alpha channels. This is the safest general-purpose choice.",
        ),
        (
            "BC1",
            "BC1 / DXT1 — Smaller, opaque",
            "Legacy block compression for opaque images. Rejects an image that contains non-opaque alpha.",
        ),
        (
            "BC3",
            "BC3 / DXT5 — Smaller + transparency",
            "Legacy block compression that preserves nontrivial alpha while using fewer bytes than RGBA32.",
        ),
    ),
)

input_mip_policy = _select_cell(
    "mip_policy",
    "4. Choose mip levels",
    "none",
    (
        "Choose Original size only unless the software that will read the DDS asks "
        "for mipmaps. A full chain adds deterministic half-size levels down to 1×1. "
        "The source canvas is never cropped or resized."
    ),
    (
        (
            "none",
            "Original size only (recommended)",
            "Writes one image level at the uploaded dimensions.",
        ),
        (
            "full_chain",
            "Full chain — Half-size levels down to 1×1",
            "Adds deterministic mip levels for consumers that explicitly expect them.",
        ),
    ),
)
# endregion


# region Outputs
output_dds_file = WorkflowCell(
    node_id="save_dds",
    id="dds_file",
    shape="masonry",
    description="Your converted DDS file — use the download link to save or inspect it.",
)

output_receipt = WorkflowCell(
    node_id="display_receipt",
    id="dds_receipt",
    shape="code",
    description=(
        "Verification receipt — records dimensions, format, alpha handling, mip count, "
        "byte length, SHA-256, and the pinned encoder revision."
    ),
    props={
        "lfLanguage": "json",
    },
)
# endregion


# region Workflow Definition
id = "image_to_dds"
node = WorkflowNode(
    id=id,
    value="Image to DDS",
    description=(
        "Convert one image to a verified DDS file in four guided choices. Transparency "
        "is preserved when the selected format supports it, and this workflow never "
        "crops or resizes your source image. No DDS lore required."
    ),
    category="Image Processing",
    inputs=[
        input_upload,
        input_filename_prefix,
        input_pixel_format,
        input_mip_policy,
    ],
    outputs=[
        output_dds_file,
        output_receipt,
    ],
    configure_prompt=_configure,
    workflow_path=Path(__file__).resolve().parent / f"{id}.json",
)
# endregion


WORKFLOW = node
