import json
from typing import Any, Dict, List

# Import the shared json_safe helper from the top-level modules utils package.
# Use the same three-dot relative import pattern used elsewhere in services.
from importlib import util
from pathlib import Path

# Dynamically load the shared conversion helpers by file path. This avoids
# ambiguous package-relative imports that can resolve to the local
# `workflow_runner.utils` package (which doesn't contain `conversion`).
_conv_path = (
    Path(__file__).parent.parent.parent
    / "utils"
    / "helpers"
    / "conversion"
    / "json_safe.py"
)
if not _conv_path.exists():
    # Fallback to the package-style module if the file layout differs.
    try:
        from ...utils.helpers.conversion import json_safe  # type: ignore
    except Exception:
        raise ImportError("Could not locate json_safe conversion helper")
else:
    spec = util.spec_from_file_location("workflow_runner._json_safe", str(_conv_path))
    if spec is None or spec.loader is None:
        raise ImportError("Could not load json_safe helper module")
    _mod = util.module_from_spec(spec)
    spec.loader.exec_module(_mod)
    json_safe = getattr(_mod, "json_safe")


def _workflow_to_prompt(workflow: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a workflow graph (the format saved under user/default/workflows)
    into the prompt dictionary expected by ComfyUI's execution queue.
    """
    nodes_list = None
    if isinstance(workflow, dict) and "nodes" in workflow and isinstance(workflow.get("nodes"), list):
        nodes_list = workflow.get("nodes", [])
    else:
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
                "inputs": json_safe(raw_inputs),
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
                prompt_inputs[input_name] = json_safe(widget_value)
            else:
                if input_def.get("value") is not None:
                    prompt_inputs[input_name] = json_safe(input_def.get("value"))

        prompt[node_id] = {
            "class_type": class_type,
            "inputs": prompt_inputs,
        }

    return prompt
