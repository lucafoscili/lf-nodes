from pathlib import Path
from typing import Any, Dict

from ..services.registry import InputValidationError, WorkflowCell, WorkflowNode

# region Workflow Config
def _configure(prompt: Dict[str, Any], inputs: Dict[str, Any]) -> None:
    for (node_id, node) in prompt.items():
        if not isinstance(node, dict):
            continue

        inputs_map = node.setdefault("inputs", {})

        if node_id == "12":  # Prompt
            name = "prompt"
            prompt = inputs.get(name)
            if prompt:
                inputs_map["string"] = str(prompt)
            else:
                raise InputValidationError(name)

        if node_id == "5":  # Batch size (Optional)
            name = "batch_size"
            batch_size = inputs.get(name)
            if batch_size:
                inputs_map["batch_size"] = int(batch_size)
# endregion

# region Inputs
input_prompt = WorkflowCell(
    node_id="12",
    id="prompt",
    value="Prompt",
    shape="textfield",
    props={
        "lfHtmlAttributes": {
            "autocomplete": "off",
            "name": "prompt",
            "type": "text"
        },
        "lfLabel": "Prompt",
        "lfHelper": {
            "showWhenFocused": False,
            "value": "The prompt to generate the image.",
        },
        "lfStyling": "textarea",
        "lfValue": "sports car, night, traffic lights, urban, cinematic, dramatic lighting, highly detailed, 8k",
    },
)
input_size = WorkflowCell(
    node_id="5",
    id="batch_size",
    value="Batch size",
    shape="textfield",
    props={
        "lfHtmlAttributes": {
            "autocomplete": "off",
            "min": 1,
            "max": 4,
            "step": 1,
            "name": "batch_size",
            "type": "number",
        },
        "lfLabel": "Batch size",
        "lfHelper": {
            "showWhenFocused": False,
            "value": "Optional: the size of the batch. Default is 1.",
        },
        "lfValue": "1",
    },
)
# endregion

# region Outputs
output_png = WorkflowCell(
    node_id="10",
    id="png_file",
    shape="masonry",
    description="PNG File",
)
# endregion

# region Workflow Definition
id = "t2i_15_lcm"
category = "Text to Image"
value = "SD1.5 LCM (Dreamshaper8)"
description = "Simple text-to-image workflow using Stable Diffusion 1.5 LCM (Dreamshaper8) model. SD1.5 works best with English prompts and tags (i.e.: 'highly detailed', '8k', 'cinematic lighting')."
node = WorkflowNode(
    id=id,
    value=value,
    description=description,
    inputs=[
        input_prompt,
        input_size,
    ],
    outputs=[
        output_png,
    ],
    configure_prompt=_configure,
    workflow_path=Path(__file__).resolve().parent / f"{id}.json",
    category=category
)
# endregion

WORKFLOW = node
