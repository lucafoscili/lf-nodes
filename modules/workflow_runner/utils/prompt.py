"""Pure JSON and workflow-to-prompt helpers.

This module intentionally has no ComfyUI, Torch, or node-package imports so
static tooling can inspect saved workflows in a minimal Python environment.
"""

from __future__ import annotations

from typing import Any

from ...utils.json_safe import json_safe


def workflow_to_prompt(workflow: dict[str, Any]) -> dict[str, Any]:
    """Convert a saved Comfy workflow graph into an API prompt dictionary."""

    nodes_list: list[dict[str, Any]] | None = None
    if isinstance(workflow.get("nodes"), list):
        nodes_list = workflow.get("nodes", [])
    else:
        maybe_nodes: list[dict[str, Any]] = []
        for node_id, value in workflow.items():
            if not isinstance(value, dict):
                continue
            if "class_type" in value or "type" in value:
                node = {**value}
                node.setdefault("id", node_id)
                maybe_nodes.append(node)
        if maybe_nodes:
            nodes_list = maybe_nodes

    links: dict[int, tuple[str, int]] = {}
    for link in workflow.get("links", []):
        if not isinstance(link, (list, tuple)) or len(link) < 5:
            continue
        link_id, source_node, source_slot, *_ = link
        links[int(link_id)] = (str(source_node), int(source_slot))

    prompt: dict[str, dict[str, Any]] = {}
    if not nodes_list:
        return prompt

    for node in nodes_list:
        node_id = str(node.get("id"))
        class_type = node.get("class_type") or node.get("type")
        raw_inputs = node.get("inputs", {})
        if isinstance(raw_inputs, dict):
            prompt_node = {
                "class_type": class_type,
                "inputs": json_safe(raw_inputs),
            }
            raw_meta = node.get("_meta")
            if isinstance(raw_meta, dict):
                prompt_node["_meta"] = json_safe(raw_meta)
            prompt[node_id] = prompt_node
            continue

        prompt_inputs: dict[str, Any] = {}
        widgets = list(node.get("widgets_values") or [])
        widget_index = 0

        for input_definition in node.get("inputs", []):
            if not isinstance(input_definition, dict):
                continue
            input_name = input_definition.get("name")
            link_id = input_definition.get("link")

            widget_value = None
            if input_definition.get("widget") is not None:
                if widget_index < len(widgets):
                    widget_value = widgets[widget_index]
                widget_index += 1

            if link_id is not None:
                source = links.get(int(link_id))
                if source is not None:
                    prompt_inputs[input_name] = [source[0], source[1]]
            elif input_definition.get("widget") is not None:
                prompt_inputs[input_name] = json_safe(widget_value)
            elif input_definition.get("value") is not None:
                prompt_inputs[input_name] = json_safe(input_definition.get("value"))

        prompt_node = {
            "class_type": class_type,
            "inputs": prompt_inputs,
        }
        raw_meta = node.get("_meta")
        if isinstance(raw_meta, dict):
            prompt_node["_meta"] = json_safe(raw_meta)
        prompt[node_id] = prompt_node

    return prompt


__all__ = ["json_safe", "workflow_to_prompt"]
