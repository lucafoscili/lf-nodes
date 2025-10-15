from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List

import folder_paths

# region Helpers
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

    # Build links mapping (older format used a separate "links" array)
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
        # Some formats call the node type "type", others use "class_type".
        class_type = node.get("class_type") or node.get("type")
        # If the node already contains an "inputs" mapping (prompt-shaped dict),
        # use it directly and skip the legacy/list-style parsing.
        raw_inputs = node.get("inputs", {})
        if isinstance(raw_inputs, dict):
            prompt[node_id] = {
                "class_type": class_type,
                "inputs": _json_safe(raw_inputs),
            }
            continue

        # Legacy/list-style node inputs (the node defines an "inputs" list of input defs)
        prompt_inputs: Dict[str, Any] = {}
        widgets: List[Any] = list(node.get("widgets_values") or [])
        widget_index = 0

        for input_def in node.get("inputs", []):
            # input_def is expected to be a dict with keys like 'name', 'link', 'widget'
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
                # Older/list formats may provide a literal 'value' field.
                if input_def.get("value") is not None:
                    prompt_inputs[input_name] = _json_safe(input_def.get("value"))

        prompt[node_id] = {
            "class_type": class_type,
            "inputs": prompt_inputs,
        }

    return prompt

@dataclass
class WorkflowField:
    name: str
    label: str
    component: str
    description: str = ""
    placeholder: str = ""
    required: bool = True
    default: Any | None = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "name": self.name,
            "label": self.label,
            "component": self.component,
            "description": self.description,
            "placeholder": self.placeholder,
            "required": self.required,
            "default": self.default,
        }
        if self.extra:
            data["extra"] = self.extra
        return _json_safe(data)

@dataclass
class WorkflowDefinition:
    workflow_id: str
    label: str
    description: str
    workflow_path: Path
    fields: Iterable[WorkflowField]
    configure_prompt: Callable[[Dict[str, Any], Dict[str, Any]], None]

    def load_prompt(self) -> Dict[str, Any]:
        with self.workflow_path.open("r", encoding="utf-8") as workflow_file:
            workflow_graph = json.load(workflow_file)
        return _workflow_to_prompt(workflow_graph)

    def fields_as_dict(self) -> List[Dict[str, Any]]:
        return [field.to_dict() for field in self.fields]

def _resolve_user_path(*relative_parts: str) -> Path:
    user_dir = Path(folder_paths.get_user_directory())
    return user_dir.joinpath(*relative_parts).resolve()

def _configure_image_to_svg_workflow(prompt: Dict[str, Any], inputs: Dict[str, Any]) -> None:
    for (node_id, node) in prompt.items():
        if not isinstance(node, dict):
            continue

        inputs_map = node.setdefault("inputs", {})
        
        if node_id == "16":  # Image Loader node
            source_path = inputs.get("source_path")
            if not source_path:
                raise ValueError("Missing required input 'source_path'.")

            resolved_path = Path(source_path).expanduser()
            if not resolved_path.exists():
                raise FileNotFoundError(f"Input path does not exist: {resolved_path}")

            resolved_str = str(resolved_path)
            inputs_map["image"] = resolved_str
        
        if node_id == "40":  # Color number node (optional)
            input_value = int(inputs.get("number_of_colors", 0) or 0)
            if input_value is not None and input_value > 0:
                inputs_map["integer"] = input_value

        if node_id == "47":  # Icon name node (optional)
            icon_name = inputs.get("icon_name")
            if icon_name:
                inputs_map["string"] = str(icon_name)

# endregion

# region Workflow Definitions
WORKFLOW_DEFINITIONS: Dict[str, WorkflowDefinition] = {}

image_to_svg_workflow_path = _resolve_user_path("default", "workflows", "ImageToSVG.json")
WORKFLOW_DEFINITIONS["image-to-svg"] = WorkflowDefinition(
    workflow_id="image-to-svg",
    label="Image to SVG",
    description=(
        "Converts a raster image to SVG format using the configured image processing model."
    ),
    workflow_path=image_to_svg_workflow_path,
    fields=[
        WorkflowField(
            name="source_path",
            label="Source File or Directory",
            component="lf-textfield",
            description="Absolute path to the image file (or folder) to convert.",
            placeholder="C:\\\\path\\\\to\\\\file.png",
            extra={"htmlAttributes": {"autocomplete": "off"}},
        ),
        WorkflowField(
            name="icon_name",
            label="Icon Name",
            component="lf-textfield",
            description="Optional: The name of the icon to use.",
            placeholder="icon",
            extra={"htmlAttributes": {"autocomplete": "off", "type": "text"}},
        ),
        WorkflowField(
            name="number_of_colors",
            label="Number of Colors",
            component="lf-textfield",
            description="Optional: the number of colors to reduce the image to.",
            placeholder="2",
            extra={"htmlAttributes": {"autocomplete": "off", "type": "number", "min": "1", "max": "256"}},
        ),
    ],
    configure_prompt=_configure_image_to_svg_workflow,
)
            
def list_workflows() -> List[Dict[str, Any]]:
    return [
        {
            "id": definition.workflow_id,
            "label": definition.label,
            "description": definition.description,
            "fields": definition.fields_as_dict(),
        }
        for definition in WORKFLOW_DEFINITIONS.values()
    ]

def get_workflow(workflow_id: str) -> WorkflowDefinition | None:
    return WORKFLOW_DEFINITIONS.get(workflow_id)
# endregion