from pathlib import Path
from typing import Any, Dict

from ..registry import InputValidationError, WorkflowCell, resolve_user_path, WorkflowNode

# region Workflow Config
def _configure_image_generation_gemini_workflow(prompt: Dict[str, Any], inputs: Dict[str, Any]) -> None:
    for (node_id, node) in prompt.items():
        if not isinstance(node, dict):
            continue

        inputs_map = node.setdefault("inputs", {})

        if node_id == "25":  # Icon name
            name = "icon_name"
            icon_name = inputs.get(name)
            if icon_name:
                inputs_map["string"] = str(icon_name)
            else:
                raise InputValidationError(name)
        
        if node_id == "22":  # Icon size
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
        
        if node_id == "26":  # Prompt in Italian checkbox (optional)
            name = "italian"
            italian = inputs.get(name)
            inputs_map["boolean"] = bool(italian)
# endregion

# region Inputs
input_name = WorkflowCell(
    node_id="25",
    id="icon_name",
    value="Icon name",
    shape="textfield",
    props={
        "lfHtmlAttributes": {
            "autocomplete": "off",
            "type": "text"
        },
        "lfLabel": "Icon name",
        "lfHelper": {
            "showWhenFocused": False,
            "value": "Optional: The name of the icon to generate. Default is 'icon'.",
        },
        "lfValue": "icon",
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
            "type": "number",
            "min": 24,
            "max": 1024,
            "step": 8,
        },
        "lfLabel": "Icon size",
        "lfHelper": {
            "showWhenFocused": False,
            "value": "Optional: the size of the icon in DPI. Default is 24.",
        },
        "lfValue": "24",
    },
)
input_strip = WorkflowCell(
    id="strip_attributes",
    node_id="29",
    shape="toggle",
    value="Strip Attributes",
    description="Sets whether to strip attributes from the SVG output.",
    props={
        "lfLabel": "Strip attributes",
        "lfValue": True,
    },
)
input_italian = WorkflowCell(
    id="italian",
    node_id="26",
    shape="toggle",
    value="Prompt in Italian",
    description="Sets whether to prompt in Italian.",
    props={
        "lfLabel": "Prompt in Italian",
        "lfValue": False,
    },
)
# endregion

# region Outputs
output_svg_file = WorkflowCell(
    id="svg_file",
    node_id="15",
    shape="masonry",
    description="SVG File",
    props={
        "lfShape": "slot",
    }
)
output_svg_data = WorkflowCell(
    id="svg_data",
    node_id="15",
    shape="code",
    description="SVG Data",
    props={
        "lfLanguage": "html",
    }
)
# endregion

# region Workflow Definition
id = "svg-generation-gemini"
value = "SVG Generation (Gemini)"
description = "Interfaces with the Gemini API prompting for SVG generation."
svg_generation_gemini_workflow_path = resolve_user_path("default", "workflows", "SVG Generation (Gemini).json")
svg_generation_gemini = WorkflowNode(
    id=id,
    value=value,
    description=description,
    inputs=[
        input_name,
        input_size,
        input_strip,
        input_italian,
    ],
    outputs=[
        output_svg_file,
        output_svg_data,
    ],
    configure_prompt=_configure_image_generation_gemini_workflow,
    workflow_path=svg_generation_gemini_workflow_path,
    category="SVG"
)
# endregion

WORKFLOW = svg_generation_gemini
