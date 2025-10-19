import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List

import folder_paths

# Custom exception for input-level validation failures. Carries the offending input name so
# callers (the HTTP API) can map the problem back to the UI field to highlight.
class InputValidationError(ValueError):
    def __init__(self, message: str, input_name: str | None = None):
        super().__init__(message)
        self.input_name = input_name

# region Helpers
def _resolve_user_path(*relative_parts: str) -> Path:
    user_dir = Path(folder_paths.get_user_directory())
    return user_dir.joinpath(*relative_parts).resolve()
def _json_safe(value: Any) -> Any:
    """
    Recursively convert workflow values into JSON-safe types.
    """
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(v) for v in value]

    return str(value)

def _workflow_to_prompt(workflow: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a workflow graph (the format saved under user/default/workflows)
    into the prompt dictionary expected by ComfyUI's execution queue.
    """
    # Workflows can be saved in two formats:
    # 1) A dict with a "nodes" list (newer format produced by the web UI)
    # 2) A dict keyed by node id -> node info (older/user-saved format)
    # Normalize both into the prompt mapping expected by execution.validate_prompt.

    # Helper: if the workflow contains an explicit "nodes" list, use that.
    nodes_list = None
    if isinstance(workflow, dict) and "nodes" in workflow and isinstance(workflow.get("nodes"), list):
        nodes_list = workflow.get("nodes", [])
    else:
        # Detect a mapping of node_id -> node_info and convert to a list
        # Expect node_info to contain at least a "class_type" or "type" key.
        if isinstance(workflow, dict):
            maybe_nodes = []
            for k, v in workflow.items():
                if not isinstance(v, dict):
                    continue
                if "class_type" in v or "type" in v:
                    node = {**v}
                    node.setdefault("id", k)
                    maybe_nodes.append(node)
            if len(maybe_nodes) > 0:
                nodes_list = maybe_nodes

    links: Dict[int, tuple[str, int]] = {}
    for link in (workflow.get("links", []) if isinstance(workflow, dict) else []):
        if len(link) < 5:
            continue
        link_id, source_node, source_slot, *_ = link
        links[int(link_id)] = (str(source_node), int(source_slot))

    prompt: Dict[str, Dict[str, Any]] = {}
    if not nodes_list:
        return prompt

    for node in nodes_list:
        node_id = str(node.get("id"))
        class_type = node.get("class_type") or node.get("type")
        raw_inputs = node.get("inputs", {})
        if isinstance(raw_inputs, dict):
            prompt[node_id] = {
                "class_type": class_type,
                "inputs": _json_safe(raw_inputs),
            }
            continue

        prompt_inputs: Dict[str, Any] = {}
        widgets: List[Any] = list(node.get("widgets_values") or [])
        widget_index = 0

        for input_def in node.get("inputs", []):
            if not isinstance(input_def, dict):
                continue
            input_name = input_def.get("name")
            link_id = input_def.get("link")

            widget_value = None
            if input_def.get("widget") is not None:
                if widget_index < len(widgets):
                    widget_value = widgets[widget_index]
                widget_index += 1

            if link_id is not None:
                source = links.get(int(link_id))
                if source is None:
                    continue
                prompt_inputs[input_name] = [source[0], source[1]]
            elif input_def.get("widget") is not None:
                prompt_inputs[input_name] = _json_safe(widget_value)
            else:
                if input_def.get("value") is not None:
                    prompt_inputs[input_name] = _json_safe(input_def.get("value"))

        prompt[node_id] = {
            "class_type": class_type,
            "inputs": prompt_inputs,
        }

    return prompt
# endregion

# region Dataset
@dataclass
class WorkflowCell:
    id: str
    value: str
    shape: str
    description: str = ""
    default: Any | None = None
    props: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "id": self.id,
            "value": self.value,
            "shape": self.shape,
        }
        if self.props:
            data.update(self.props)
        if self.description:
            data["description"] = self.description

        return _json_safe(data)

@dataclass
class WorkflowNode:
    id: str
    value: str
    description: str
    workflow_path: Path
    cells: Iterable[WorkflowCell]
    configure_prompt: Callable[[Dict[str, Any], Dict[str, Any]], None]

    def load_prompt(self) -> Dict[str, Any]:
        with self.workflow_path.open("r", encoding="utf-8") as workflow_file:
            workflow_graph = json.load(workflow_file)
        return _workflow_to_prompt(workflow_graph)

    def cells_as_dict(self) -> Dict[str, Any]:
        return {f"{cell.id}": cell.to_dict() for i, cell in enumerate(self.cells)}
# endregion

# region Workflow Config
def _configure_image_to_svg_workflow(prompt: Dict[str, Any], inputs: Dict[str, Any]) -> None:
    for (node_id, node) in prompt.items():
        if not isinstance(node, dict):
            continue

        inputs_map = node.setdefault("inputs", {})

        if node_id == "16":  # Image Loader node
            input_name = "source_path"
            source_path = inputs.get(input_name)
            if not source_path:
                raise InputValidationError("Missing required input 'source_path'.", input_name=input_name)

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

        if node_id == "40":  # Color number node (optional)
            input_name = "number_of_colors"
            input_value = int(inputs.get(input_name, 0) or 0)
            if input_value is not None and input_value > 0:
                inputs_map["integer"] = input_value

        if node_id == "47":  # Icon name node (optional)
            input_name = "icon_name"
            icon_name = inputs.get(input_name)
            if icon_name:
                inputs_map["string"] = str(icon_name)

        if node_id == "51":  # Desaturate checkbox (optional)
            input_name = "desaturate"
            desaturate = inputs.get(input_name)
            inputs_map["boolean"] = bool(desaturate)

        if node_id == "72":  # Keep transparency checkbox (optional)
            input_name = "keep_transparency"
            keep_transparency = inputs.get(input_name)
            inputs_map["boolean"] = bool(keep_transparency)

# endregion

# region Workflow Defs
class WorkflowRegistry:
    def __init__(self) -> None:
        self._definitions: Dict[str, WorkflowNode] = {}

    def register(self, definition: WorkflowNode) -> None:
        self._definitions[definition.id] = definition

    def list(self) -> Dict[str, List[Dict[str, Any]]]:
        return {
            "columns": [],
            "nodes": [{
                "id": definition.id,
                "value": definition.value,
                "description": definition.description,
                "cells": definition.cells_as_dict(),
            } for definition in self._definitions.values()],
        }
    def get(self, id: str) -> WorkflowNode | None:
        return self._definitions.get(id)

REGISTRY = WorkflowRegistry()

image_to_svg_workflow_path = _resolve_user_path("default", "workflows", "Image 2 SVG.json")
REGISTRY.register(
    WorkflowNode(
        id="image-to-svg",
        value="Image to SVG",
        description="Converts a raster image to SVG format using the configured image processing model.",
        workflow_path=image_to_svg_workflow_path,
        cells=[
            WorkflowCell(
                id="source_path",
                value="Source File or Directory",
                shape="upload",
                props={
                    "lfHtmlAttributes": {
                        "accept": "image/*"
                    },
                    "lfLabel": "Source image",
                },
            ),
            WorkflowCell(
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
            ),
            WorkflowCell(
                id="number_of_colors",
                value="Number of Colors",
                shape="textfield",
                props={
                    "lfHtmlAttributes": {
                        "autocomplete": "off",
                        "type": "number",
                        "min": 1,
                        "max": 256
                    },
                    "lfHelper": {
                        "showWhenFocused": False,
                        "value": "Optional: the number of colors to reduce the image to. Default is 2.",
                    },
                    "lfLabel": "Number of colors",
                    "lfValue": "2",
                },
            ),
            WorkflowCell(
                id="desaturate",
                value="Desaturate",
                shape="toggle",
                description="Sets whether to desaturate the image before converting.",
                props={
                    "lfLabel": "Desaturate image",
                    "lfValue": False,
                },
            ),
            WorkflowCell(
                id="keep_transparency",
                value="Keep Transparency",
                shape="toggle",
                description="Sets whether to keep the transparency of the image.",
                props={
                    "lfLabel": "Keep transparency",
                    "lfValue": True,
                },
            ),
        ],
        configure_prompt=_configure_image_to_svg_workflow,
    )
)

def list_workflows() -> List[Dict[str, Any]]:
    return REGISTRY.list()

def get_workflow(id: str) -> WorkflowNode | None:
    return REGISTRY.get(id)
# endregion
