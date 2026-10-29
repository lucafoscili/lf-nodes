from pathlib import Path
from typing import Any, Dict

from ..services.registry import WorkflowCardPresentation, WorkflowCell, WorkflowNode
from .utils import required_text as _required_text, resolve_load_image_reference


# region Workflow Config
def _configure(prompt: Dict[str, Any], inputs: Dict[str, Any]) -> None:
    filename_prefix = _required_text(inputs, "filename_prefix")
    image_reference = resolve_load_image_reference(inputs, "image_path")
    mask_reference = resolve_load_image_reference(inputs, "mask_path")

    prompt["load_image"]["inputs"]["image"] = image_reference
    prompt["load_mask"]["inputs"]["image"] = mask_reference
    prompt["save"]["inputs"]["filename_prefix"] = filename_prefix
# endregion


# region Inputs
input_image = WorkflowCell(
    node_id="load_image",
    id="image_path",
    value="Texture",
    shape="upload",
    description=(
        "Choose one PNG texture to pad, such as a baked map or an atlas. Every "
        "channel is padded, alpha included, and its values are read as stored "
        "(8 or 16 bits)."
    ),
    props={
        "lfHtmlAttributes": {
            "accept": "image/png",
        },
        "lfLabel": "1. Choose a texture",
    },
)

input_mask = WorkflowCell(
    node_id="load_mask",
    id="mask_path",
    value="Coverage mask",
    shape="upload",
    description=(
        "Choose a black-and-white image the same size as the texture: white marks "
        "the pixels to keep (a bake's UV coverage), black the pixels to fill. The "
        "red channel is read and values above half count as white."
    ),
    props={
        "lfHtmlAttributes": {
            "accept": "image/png",
        },
        "lfLabel": "2. Choose the coverage mask",
    },
)

input_filename_prefix = WorkflowCell(
    node_id="save",
    id="filename_prefix",
    value="Filename prefix",
    shape="textfield",
    description=(
        "The folder and filename inside ComfyUI's output directory. A counter and "
        "the .png extension are added automatically; the PNG keeps the texture's "
        "bit depth and holds no metadata."
    ),
    props={
        "lfHtmlAttributes": {
            "autocomplete": "off",
            "name": "filename_prefix",
            "placeholder": "LF_Nodes/EdgePadding",
            "type": "text",
        },
        "lfLabel": "3. Choose an output name",
        "lfValue": "LF_Nodes/EdgePadding",
    },
)
# endregion


# region Outputs
output_image = WorkflowCell(
    node_id="save",
    id="padded_image",
    shape="masonry",
    description=(
        "The padded texture: pixels inside the mask keep their stored values, every "
        "other pixel is filled and rounded to the nearest level."
    ),
)

output_receipt = WorkflowCell(
    node_id="display_receipt",
    id="padding_receipt",
    shape="code",
    description="The padding receipt: covered and padded pixel counts, the covered share and the pyramid's levels.",
    props={
        "lfLanguage": "json",
    },
)
# endregion


# region Workflow Definition
id = "texture_edge_padding"
node = WorkflowNode(
    id=id,
    value="Texture Edge Padding",
    description=(
        "Fill a texture outside its coverage mask from the pixels inside it, so "
        "mipmaps and filtering never blend the background into the border of a "
        "baked texture or an atlas island. Runs on CPU, loads no model and never "
        "resizes. Loads and saves stored values: 8 or 16-bit PNG, alpha kept as a "
        "channel, filled pixels rounded."
    ),
    category="Image Processing",
    card=WorkflowCardPresentation(
        summary="Pad a texture past its UV islands from a coverage mask.",
    ),
    inputs=[
        input_image,
        input_mask,
        input_filename_prefix,
    ],
    outputs=[
        output_image,
        output_receipt,
    ],
    configure_prompt=_configure,
    workflow_path=Path(__file__).resolve().parent / f"{id}.json",
)
# endregion


WORKFLOW = node
