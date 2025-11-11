from pathlib import Path
from typing import Any, Dict

from ..services.registry import InputValidationError, WorkflowCell, WorkflowNode

# region Workflow Config
def _configure(prompt: Dict[str, Any], inputs: Dict[str, Any]) -> None:
    for (node_id, node) in prompt.items():
        if not isinstance(node, dict):
            continue

        inputs_map = node.setdefault("inputs", {})

        if node_id == "21":  # Prompt
            name = "prompt"
            icon_name = inputs.get(name)
            if icon_name:
                inputs_map["replacement"] = str(icon_name)
            else:
                raise InputValidationError(name)
        
        if node_id == "22":  # Icon size (optional)
            name = "icon_size"
            icon_size = inputs.get(name)
            if icon_size:
                inputs_map["integer"] = int(icon_size)
            else:
                raise InputValidationError(name)

        if node_id == "29":  # Strip attributes checkbox (optional)
            name = "strip_attributes"
            strip_attributes = inputs.get(name)
            inputs_map["boolean"] = bool(strip_attributes)

        if node_id == "33":  # Gemini model (optional)
            name = "gemini_model"
            gemini_model = inputs.get(name)
            if gemini_model:
                inputs_map["model"] = str(gemini_model)
# endregion

# region Inputs
input_prompt = WorkflowCell(
    node_id="21",
    id="prompt",
    value="",
    shape="textfield",
    props={
        "lfHtmlAttributes": {
            "name": "prompt",
            "type": "text"
        },
        "lfLabel": "Prompt",
        "lfHelper": {
            "showWhenFocused": False,
            "value": "The prompt for the icon to generate. Default is 'Una persona'.",
        },
        "lfValue": "Una persona",
    },
)
input_size = WorkflowCell(
    node_id="22",
    id="icon_size",
    value="Icon size",
    shape="textfield",
    props={
        "lfHtmlAttributes": {
            "autocomplete": "off",
            "min": 24,
            "max": 2048,
            "step": 8,
            "name": "icon_size",
            "type": "number",
        },
        "lfLabel": "Icon size",
        "lfHelper": {
            "showWhenFocused": False,
            "value": "Optional: the size of the icon in DPI. Default is 24.",
        },
        "lfValue": "24",
    },
)
input_model = WorkflowCell(
    node_id="33",
    id="gemini_model",
    value="Gemini Model",
    shape="textfield",
    props={
        "lfHtmlAttributes": {
            "name": "gemini_model",
            "type": "text"
        },
        "lfLabel": "Gemini Model",
        "lfHelper": {
            "showWhenFocused": False,
            "value": "Optional: the Gemini model to use. Default is 'gemini-2.5-flash-image' (Nano Banana).",
        },
        "lfValue": "gemini-2.5-flash-image",
    },
)
input_strip = WorkflowCell(
    node_id="29",
    id="strip_attributes",
    shape="toggle",
    value="Strip Attributes",
    description="Sets whether to strip attributes from the SVG output.",
    props={
        "lfLabel": "Strip attributes",
        "lfValue": True,
    },
)
# endregion

# region Outputs
output_svg_file = WorkflowCell(
    node_id="15",
    id="svg_file",
    shape="masonry",
    description="SVG File",
    props={
        "lfShape": "slot",
    }
)
output_svg_data = WorkflowCell(
    node_id="15",
    id="svg_data",
    shape="code",
    description="SVG Data",
    props={
        "lfLanguage": "html",
    }
)
# endregion

# region Workflow Definition
id = "svg_generation_gemini"
category = "SVG"
value = "SVG Generation (Gemini)"
description = "Interfaces with the Gemini API prompting for SVG generation."
node = WorkflowNode(
    id=id,
    value=value,
    description=description,
    inputs=[
        input_prompt,
        input_size,
        input_strip,
        input_model,
    ],
    outputs=[
        output_svg_file,
        output_svg_data,
    ],
    configure_prompt=_configure,
    workflow_path=Path(__file__).resolve().parent / f"{id}.json",
    category=category
)
# endregion

WORKFLOW = node
