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

        if node_id == "2":  # Image loader
            resolved_paths = resolve_upload_paths(inputs, "source_path", allow_multiple=False)
            inputs_map["image"] = resolved_paths[0]
# endregion

# region Inputs
input_upload = WorkflowCell(
    node_id="2",
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
# endregion

# region Outputs
output_string = WorkflowCell(
    id="string",
    node_id="6",
    shape="code",
    description="Caption",
    props={
        "lfLanguage": "markdown",
    }
)
# endregion

# region Workflow Definition
id = "caption_image_vision"
category = "LLM"
value = "Caption image (Vision)"
description = "Generates a caption for an input image using a vision-capable LLM model."
node = WorkflowNode(
    id=id,
    value=value,
    description=description,
    inputs=[
        input_upload,
    ],
    outputs=[
        output_string,
    ],
    configure_prompt=_configure,
    workflow_path=Path(__file__).resolve().parent / f"{id}.json",
    category=category
)
# endregion

WORKFLOW = node
