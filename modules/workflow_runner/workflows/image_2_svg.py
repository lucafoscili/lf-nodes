from pathlib import Path
from typing import Any, Dict

from ..registry import InputValidationError, WorkflowCell, resolve_user_path, WorkflowNode

# region Workflow Config
def _configure_image_to_svg_workflow(prompt: Dict[str, Any], inputs: Dict[str, Any]) -> None:
    for (node_id, node) in prompt.items():
        if not isinstance(node, dict):
            continue

        inputs_map = node.setdefault("inputs", {})

        if node_id == "16":  # Image loader
            name = "source_path"
            source_path = inputs.get(name)
            if not source_path:
                raise InputValidationError(name)

            if isinstance(source_path, (list, tuple)):
                source_path = next((v for v in source_path if v), source_path[0] if len(source_path) > 0 else None)

            if isinstance(source_path, dict):
                source_path = source_path.get('path') or source_path.get('file') or source_path.get('name')

            if isinstance(source_path, str) and ';' in source_path:
                parts = [p for p in (s.strip() for s in source_path.split(';')) if p]
                source_path = parts[0] if parts else source_path

            resolved_path = Path(source_path).expanduser()
            if not resolved_path.exists():
                raise FileNotFoundError(f"Input path does not exist: {resolved_path}")

            resolved_str = str(resolved_path)
            inputs_map["image"] = resolved_str

        if node_id == "40":  # Color number (optional)
            name = "number_of_colors"
            input_value = int(inputs.get(name, 0) or 0)
            if input_value is not None and input_value > 0:
                inputs_map["integer"] = input_value

        if node_id == "47":  # Icon name (optional)
            name = "icon_name"
            icon_name = inputs.get(name)
            if icon_name:
                inputs_map["string"] = str(icon_name)

        if node_id == "51":  # Desaturate checkbox (optional)
            name = "desaturate"
            desaturate = inputs.get(name)
            inputs_map["boolean"] = bool(desaturate)

        if node_id == "71":  # Keep transparency checkbox (optional)
            name = "keep_transparency"
            keep_transparency = inputs.get(name)
            inputs_map["boolean"] = bool(keep_transparency)

        if node_id == "80":  # Strip attributes checkbox (optional)
            name = "strip_attributes"
            strip_attributes = inputs.get(name)
            inputs_map["boolean"] = bool(strip_attributes)
# endregion

# region Inputs
input_upload = WorkflowCell(
    node_id="16",
    id="source_path",
    value="Source File or Directory",
    shape="upload",
    props={
        "lfHtmlAttributes": {
            "accept": "image/*"
        },
        "lfLabel": "Source image",
    },
)
input_name = WorkflowCell(
    node_id="47",
    id="icon_name",
    value="Icon Name",
    shape="textfield",
    props={
        "lfHtmlAttributes": {
            "autocomplete": "off",
            "type": "text"
        },
        "lfLabel": "Icon name",
        "lfHelper": {
            "showWhenFocused": False,
            "value": "Optional: The name of the icon to use. Default is 'icon'.",
        },
        "lfValue": "icon",
    },
)
input_colors = WorkflowCell(
    node_id="40",
    id="number_of_colors",
    value="Number of Colors",
    shape="textfield",
    props={
        "lfHtmlAttributes": {
            "autocomplete": "off",
            "type": "number",
            "min": 1,
            "max": 256,
        },
        "lfLabel": "Number of colors",
        "lfHelper": {
            "showWhenFocused": False,
            "value": "Optional: the number of colors to reduce the image to. Default is 2.",
        },
        "lfValue": "2",
    },
)
input_desaturate = WorkflowCell(
    id="desaturate",
    node_id="51",
    shape="toggle",
    value="Desaturate",
    description="Sets whether to desaturate the image before converting.",
    props={
        "lfLabel": "Desaturate image",
        "lfValue": False,
    },
)
input_transparency = WorkflowCell(
    id="keep_transparency",
    node_id="71",
    shape="toggle",
    value="Keep Transparency",
    description="Sets whether to keep the transparency of the image.",
    props={
        "lfLabel": "Keep transparency",
        "lfValue": True,
    },
)
input_strip = WorkflowCell(
    id="strip_attributes",
    node_id="80",
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
    id="svg_file",
    node_id="20",
    shape="masonry",
    description="SVG File",
    props={
        "lfShape": "slot",
    }
)
output_svg_data = WorkflowCell(
    id="svg_data",
    node_id="20",
    shape="code",
    description="SVG Data",
    props={
        "lfLanguage": "html",
    }
)
output_png = WorkflowCell(
    id="png_file",
    node_id="61",
    shape="masonry",
    description="PNG File",
)
# endregion

# region Workflow Definition
id = "image-to-svg"
value = "Image to SVG"
description = "Converts a raster image to SVG format using the configured image processing model."
image_to_svg_workflow_path = resolve_user_path("default", "workflows", "Image 2 SVG.json")
image_2_svg = WorkflowNode(
    id=id,
    value=value,
    description=description,
    inputs=[
        input_upload,
        input_name,
        input_colors,
        input_transparency,
        input_strip,
        input_desaturate,
    ],
    outputs=[
        output_svg_file,
        output_svg_data,
        output_png,
    ],
    configure_prompt=_configure_image_to_svg_workflow,
    workflow_path=image_to_svg_workflow_path,
)
# endregion

WORKFLOW = image_2_svg
