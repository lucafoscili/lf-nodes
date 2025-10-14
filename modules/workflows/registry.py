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


def _resolve_package_path(*relative_parts: str) -> Path:
    package_root = Path(__file__).resolve().parents[2]
    return package_root.joinpath(*relative_parts).resolve()


def _configure_markdown_workflow(prompt: Dict[str, Any], inputs: Dict[str, Any]) -> None:
    source_path = inputs.get("source_path")
    if not source_path:
        raise ValueError("Missing required input 'source_path'.")

    resolved_path = Path(source_path).expanduser()
    if not resolved_path.exists():
        raise FileNotFoundError(f"Input path does not exist: {resolved_path}")

    resolved_str = str(resolved_path)
    for node in prompt.values():
        # Be defensive: some prompt entries may not be dicts when imported from
        # external or API formats. Skip entries that aren't mappings.
        if not isinstance(node, dict):
            continue
        if node.get("class_type") == "LF_RegionExtractor":
            node.setdefault("inputs", {})["dir"] = resolved_str

def _configure_lora_workflow(prompt: Dict[str, Any], _: Dict[str, Any]) -> None:
    # Defaults baked into the workflow handle prompt execution.
    # No dynamic inputs required for the first iteration.
    return

def _configure_image_to_svg_workflow(prompt: Dict[str, Any], inputs: Dict[str, Any]) -> None:
    source_path = inputs.get("source_path")
    if not source_path:
        raise ValueError("Missing required input 'source_path'.")

    resolved_path = Path(source_path).expanduser()
    if not resolved_path.exists():
        raise FileNotFoundError(f"Input path does not exist: {resolved_path}")

    resolved_str = str(resolved_path)
    for node in prompt.values():
        # Defensive check: ensure node is a dict before accessing its keys.
        if not isinstance(node, dict):
            continue
        # If the node is a LoadImage node and doesn't already have a linked
        # 'image' input, set it to the uploaded path. Also set 'image_path' on
        # API_ImageToSVG nodes to support older workflow shapes.
        inputs_map = node.setdefault("inputs", {})
        class_type = node.get("class_type")
        # If this node expects a plain 'image' input and it's not linked, overwrite
        # only when its current value is a literal filename or missing.
        if class_type == "LoadImage":
            cur = inputs_map.get("image")
            # Skip if it's already a link ([node_id, slot])
            if not (isinstance(cur, list) and len(cur) == 2):
                inputs_map["image"] = resolved_str

        if class_type == "API_ImageToSVG":
            # older API-style node uses 'image_path'
            cur = inputs_map.get("image_path")
            if not (isinstance(cur, list) and len(cur) == 2):
                inputs_map["image_path"] = resolved_str

        # Generic fallback: set any unlinked input named 'image' or 'image_path'
        # to the resolved path — this helps if the workflow uses different node types.
        for possible in ("image", "image_path"):
            cur = inputs_map.get(possible)
            if cur is None:
                # only set when missing entirely
                inputs_map[possible] = resolved_str
            elif not (isinstance(cur, list) and len(cur) == 2):
                # if it's a literal string (old saved filename), prefer the uploaded path
                if isinstance(cur, str) and cur.strip() != "":
                    inputs_map[possible] = resolved_str
# endregion

# region Workflow Definitions
WORKFLOW_DEFINITIONS: Dict[str, WorkflowDefinition] = {}

markdown_workflow_path = _resolve_user_path("default", "workflows", "Markdown documentation.json")
WORKFLOW_DEFINITIONS["markdown-documentation"] = WorkflowDefinition(
    workflow_id="markdown-documentation",
    label="Markdown Documentation",
    description=(
        "Extracts annotated regions from a Python file and generates Markdown documentation "
        "using the configured LLM endpoint."
    ),
    workflow_path=markdown_workflow_path,
    fields=[
        WorkflowField(
            name="source_path",
            label="Source File or Directory",
            component="lf-textfield",
            description="Absolute path to the Python file (or folder) containing annotated regions.",
            placeholder="C:\\\\path\\\\to\\\\file.py",
            extra={"htmlAttributes": {"autocomplete": "off"}},
        ),
    ],
    configure_prompt=_configure_markdown_workflow,
)

lora_workflow_path = _resolve_package_path("example_workflows", "LoRa tester.json")
WORKFLOW_DEFINITIONS["lora-tester"] = WorkflowDefinition(
    workflow_id="lora-tester",
    label="LoRA Tester",
    description=(
        "Runs the LoRA tester workflow with the bundled defaults and returns the generated image metadata."
    ),
    workflow_path=lora_workflow_path,
    fields=[],
    configure_prompt=_configure_lora_workflow,
)

markdown_workflow_path = _resolve_user_path("default", "workflows", "API_ImageToSVG.json")
WORKFLOW_DEFINITIONS["image-to-svg"] = WorkflowDefinition(
    workflow_id="image-to-svg",
    label="Image to SVG",
    description=(
        "Converts a raster image to SVG format using the configured image processing model."
    ),
    workflow_path=markdown_workflow_path,
    fields=[
        WorkflowField(
            name="source_path",
            label="Source File or Directory",
            component="lf-textfield",
            description="Absolute path to the image file (or folder) to convert.",
            placeholder="C:\\\\path\\\\to\\\\file.png",
            extra={"htmlAttributes": {"autocomplete": "off"}},
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