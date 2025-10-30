from pathlib import Path
from typing import Any, Dict

from ..services.registry import WorkflowCell, WorkflowNode
from .utils import resolve_upload_paths

# region Workflow Config
def _configure(prompt: Dict[str, Any], inputs: Dict[str, Any]) -> None:
    for (node_id, node) in prompt.items():
        if not isinstance(node, dict):
            continue

        inputs_map = node.setdefault("inputs", {})

        if node_id == "4":  # Image loader
            resolved_paths = resolve_upload_paths(inputs, "source_path", allow_multiple=True)
            inputs_map["image"] = (
                resolved_paths[0] if len(resolved_paths) == 1 else ";".join(resolved_paths)
            )
        
        if node_id == "1":  # Background color (optional) / Transparency
            name = "background_color"
            bg_color = inputs.get(name)
            if bg_color:
                inputs_map["background_color"] = str(bg_color)

            name = "transparent_background"
            transparent_background = inputs.get(name)
            if transparent_background is not None:
                inputs_map["transparent_background"] = transparent_background
# endregion

# region Inputs
input_upload = WorkflowCell(
    node_id="4",
    id="source_path",
    value="Source image",
    shape="upload",
    props={
        "lfHtmlAttributes": {
            "accept": "image/*"
        },
        "lfLabel": "Source image",
    },
)
input_bg_color = WorkflowCell(
    node_id="1",
    id="background_color",
    value="Background color",
    shape="textfield",
    props={
        "lfHtmlAttributes": {
            "autocomplete": "off",
            "name": "background_color",
            "type": "color",
        },
        "lfLabel": "Background color",
        "lfHelper": {
            "showWhenFocused": False,
            "value": "Optional: the background color for the image. Default is black.",
        },
        "lfValue": "#000000",
    },
)
input_bg_transparent = WorkflowCell(
    node_id="1",
    id="transparent_background",
    shape="toggle",
    value="Transparent background",
    description="If enabled, the background will be transparent.",
    props={
        "lfLabel": "Transparent background",
        "lfValue": False,
    },
)
# endregion

# region Outputs
output_image = WorkflowCell(
    node_id="5",
    id="image",
    shape="masonry",
    description="PNG File",
)
# endregion

# region Workflow Definition
id = "remove_bg"
category = "Image Processing"
value = "Remove background"
description = "Removes the background from an image."
node = WorkflowNode(
    id=id,
    value=value,
    description=description,
    inputs=[
        input_upload,
        input_bg_color,
        input_bg_transparent,
    ],
    outputs=[
        output_image,
    ],
    configure_prompt=_configure,
    workflow_path=Path(__file__).resolve().parent / f"{id}.json",
    category=category
)
# endregion

WORKFLOW = node
