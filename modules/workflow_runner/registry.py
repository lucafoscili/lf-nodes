import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List

import folder_paths

# Custom exception for input-level validation failures. Carries the offending input name so
# callers (the HTTP API) can map the problem back to the UI field to highlight.
class InputValidationError(ValueError):
    def __init__(self, input_name: str | None = None):
        super().__init__(f"Missing required input {input_name}.")
        self.input_name = input_name

# region Helpers
def _resolve_user_path(*relative_parts: str) -> Path:
    user_dir = Path(folder_paths.get_user_directory())
    return user_dir.joinpath(*relative_parts).resolve()

# Public alias for workflow modules.
resolve_user_path = _resolve_user_path

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
    node_id: str
    shape: str = ""
    value: str = ""
    description: str = ""
    props: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "id": self.id,
            "nodeId": self.node_id,
            "shape": self.shape,
        }
        if self.props:
            data["props"] = _json_safe(self.props)
        if self.value:
            data["value"] = self.value
        if self.description:
            data["title"] = self.description

        return _json_safe(data)

@dataclass
class WorkflowNode:
    id: str
    value: str
    description: str
    inputs: Iterable[WorkflowCell]
    outputs: Iterable[WorkflowCell]
    configure_prompt: Callable[[Dict[str, Any], Dict[str, Any]], None]
    workflow_path: Path

    def load_prompt(self) -> Dict[str, Any]:
        with self.workflow_path.open("r", encoding="utf-8") as workflow_file:
            workflow_graph = json.load(workflow_file)
        return _workflow_to_prompt(workflow_graph)

    def cells_as_dict(self) -> Dict[str, Any]:
        return self.inputs_as_dict()

    def inputs_as_dict(self) -> Dict[str, Any]:
        return {cell.id: cell.to_dict() for cell in self.inputs}

    def outputs_as_dict(self) -> Dict[str, Any]:
        return {cell.id: cell.to_dict() for cell in self.outputs}
# endregion

# region Workflow Defs
class WorkflowRegistry:
    def __init__(self) -> None:
        self._definitions: Dict[str, WorkflowNode] = {}

    def register(self, definition: WorkflowNode) -> None:
        self._definitions[definition.id] = definition

    def list(self) -> Dict[str, List[Dict[str, Any]]]:
        nodes: List[Dict[str, Any]] = []
        for definition in self._definitions.values():
            workflow_node = {
                "id": definition.id,
                "value": definition.value,
                "description": definition.description,
                "children": [{
                    "id": f"{definition.id}:inputs",
                    "value": "Inputs",
                    "description": "Workflow inputs",
                    "cells": definition.inputs_as_dict(),
                    },{
                    "id": f"{definition.id}:outputs",
                    "value": "Outputs",
                    "description": "Workflow outputs",
                    "cells": definition.outputs_as_dict(),
                    },
                ],
            }
            nodes.append(workflow_node)

        return {
            "columns": [],
            "nodes": nodes,
        }
    def get(self, id: str) -> WorkflowNode | None:
        return self._definitions.get(id)

REGISTRY = WorkflowRegistry()

def _is_workflow_definition(definition: object) -> bool:
    if isinstance(definition, WorkflowNode):
        return True

    required_attrs = (
        "id",
        "value",
        "description",
        "workflow_path",
        "inputs",
        "outputs",
        "configure_prompt",
    )
    required_methods = ("load_prompt", "cells_as_dict")

    return all(hasattr(definition, attr) for attr in (*required_attrs, *required_methods))

def _register_packaged_workflows() -> None:
    """
    Import workflow definitions located in the workflows subpackage and add them to the registry.

    Keeping the import local prevents circular imports while registry types are still being defined.
    """
    from .workflows import iter_workflow_definitions

    for definition in iter_workflow_definitions():
        if not _is_workflow_definition(definition):
            raise TypeError(
                f"Workflow definition '{definition!r}' is not compatible with WorkflowNode."
            )
        REGISTRY.register(definition)  # type: ignore[arg-type]

_register_packaged_workflows()

def list_workflows() -> List[Dict[str, Any]]:
    return REGISTRY.list()

def get_workflow(id: str) -> WorkflowNode | None:
    return REGISTRY.get(id)
# endregion
