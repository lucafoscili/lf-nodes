"""Static, queue-free preflight for ComfyUI workflow JSON files."""

from __future__ import annotations

import argparse
import ast
import copy
import json
import sys

from pathlib import Path
from typing import Any, Callable, Iterable


_REPO_ROOT = Path(__file__).resolve().parents[3]
_LF_NODES_ROOT = _REPO_ROOT / "modules" / "nodes"


def discover_lf_node_types(nodes_root: Path = _LF_NODES_ROOT) -> frozenset[str]:
    """Read LF mapping keys from source without importing ComfyUI or model code."""

    discovered: dict[str, Path] = {}
    for source_path in sorted(nodes_root.rglob("*.py")):
        try:
            tree = ast.parse(source_path.read_text(encoding="utf-8-sig"), filename=str(source_path))
        except (OSError, SyntaxError) as error:
            raise ValueError(f"Could not inspect node mappings in {source_path}: {error}") from error

        for statement in ast.walk(tree):
            value: ast.AST | None = None
            if isinstance(statement, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == "NODE_CLASS_MAPPINGS"
                for target in statement.targets
            ):
                value = statement.value
            elif (
                isinstance(statement, ast.AnnAssign)
                and isinstance(statement.target, ast.Name)
                and statement.target.id == "NODE_CLASS_MAPPINGS"
            ):
                value = statement.value

            if isinstance(value, ast.Dict):
                for key in value.keys:
                    if not (isinstance(key, ast.Constant) and isinstance(key.value, str)):
                        continue
                    existing = discovered.get(key.value)
                    if existing is not None:
                        raise ValueError(
                            f"Duplicate published node mapping {key.value!r}: "
                            f"{existing} and {source_path}"
                        )
                    discovered[key.value] = source_path
    return frozenset(discovered)


def _workflow_to_prompt(workflow: dict[str, Any]) -> dict[str, Any]:
    if str(_REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(_REPO_ROOT))
    from modules.workflow_runner.utils.prompt import workflow_to_prompt as convert

    return convert(copy.deepcopy(workflow))


def _link_id(value: Any, context: str, errors: list[str]) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        errors.append(f"{context} has an invalid link id: {value!r}")
        return None


def preflight_workflow_data(
    workflow: dict[str, Any],
    *,
    lf_node_types: Iterable[str] | None = None,
    require_all_lf_nodes: bool = False,
    converter: Callable[[dict[str, Any]], dict[str, Any]] = _workflow_to_prompt,
) -> dict[str, Any]:
    """Return a deterministic structural and LF-coverage report."""

    errors: list[str] = []
    warnings: list[str] = []
    nodes = workflow.get("nodes")
    raw_links = workflow.get("links", [])
    if not isinstance(nodes, list):
        nodes = []
        errors.append("Workflow must contain a nodes list")
    if not isinstance(raw_links, list):
        raw_links = []
        errors.append("Workflow links must be a list")

    node_by_id: dict[str, dict[str, Any]] = {}
    node_types: list[str] = []
    nonzero_modes: list[str] = []
    for index, node in enumerate(nodes):
        if not isinstance(node, dict):
            errors.append(f"Node at index {index} is not an object")
            continue
        node_id = str(node.get("id"))
        if node.get("id") is None:
            errors.append(f"Node at index {index} has no id")
            continue
        if node_id in node_by_id:
            errors.append(f"Duplicate node id: {node_id}")
            continue
        node_by_id[node_id] = node
        node_type = node.get("class_type") or node.get("type")
        if not isinstance(node_type, str) or not node_type:
            errors.append(f"Node {node_id} has no type")
        else:
            node_types.append(node_type)
        if node.get("mode", 0) not in (None, 0):
            nonzero_modes.append(node_id)

    link_by_id: dict[int, tuple[str, int, str, int]] = {}
    for index, link in enumerate(raw_links):
        if not isinstance(link, list) or len(link) < 5:
            errors.append(f"Link at index {index} is malformed")
            continue
        link_id = _link_id(link[0], f"Link at index {index}", errors)
        if link_id is None:
            continue
        if link_id in link_by_id:
            errors.append(f"Duplicate link id: {link_id}")
            continue
        try:
            source_id, source_slot = str(link[1]), int(link[2])
            target_id, target_slot = str(link[3]), int(link[4])
        except (TypeError, ValueError):
            errors.append(f"Link {link_id} has invalid endpoints")
            continue
        if source_id not in node_by_id:
            errors.append(f"Link {link_id} references missing source node {source_id}")
        if target_id not in node_by_id:
            errors.append(f"Link {link_id} references missing target node {target_id}")
        link_by_id[link_id] = (source_id, source_slot, target_id, target_slot)

    input_link_ids: set[int] = set()
    output_link_ids: set[int] = set()
    for node_id, node in node_by_id.items():
        inputs = node.get("inputs", [])
        if not isinstance(inputs, list):
            errors.append(f"Node {node_id} inputs must be a list")
        else:
            for slot, input_definition in enumerate(inputs):
                if not isinstance(input_definition, dict):
                    errors.append(f"Node {node_id} input {slot} is not an object")
                    continue
                if input_definition.get("link") is None:
                    continue
                link_id = _link_id(
                    input_definition.get("link"),
                    f"Node {node_id} input {slot}",
                    errors,
                )
                if link_id is not None:
                    input_link_ids.add(link_id)
                link = None if link_id is None else link_by_id.get(link_id)
                if link is None:
                    if link_id is not None:
                        errors.append(f"Node {node_id} input {slot} references missing link {link_id}")
                elif link[2:] != (node_id, slot):
                    errors.append(f"Link {link_id} does not target node {node_id} input {slot}")

        outputs = node.get("outputs", [])
        if not isinstance(outputs, list):
            errors.append(f"Node {node_id} outputs must be a list")
        else:
            for slot, output_definition in enumerate(outputs):
                if not isinstance(output_definition, dict):
                    errors.append(f"Node {node_id} output {slot} is not an object")
                    continue
                raw_output_links = output_definition.get("links")
                if raw_output_links is None:
                    continue
                if not isinstance(raw_output_links, list):
                    errors.append(f"Node {node_id} output {slot} links must be a list")
                    continue
                for raw_link_id in raw_output_links:
                    link_id = _link_id(raw_link_id, f"Node {node_id} output {slot}", errors)
                    if link_id is not None:
                        output_link_ids.add(link_id)
                    link = None if link_id is None else link_by_id.get(link_id)
                    if link is None:
                        if link_id is not None:
                            errors.append(f"Node {node_id} output {slot} references missing link {link_id}")
                    elif link[:2] != (node_id, slot):
                        errors.append(f"Link {link_id} does not originate at node {node_id} output {slot}")

    for link_id in sorted(link_by_id.keys() - input_link_ids):
        errors.append(f"Link {link_id} is not attached to target input metadata")
    for link_id in sorted(link_by_id.keys() - output_link_ids):
        errors.append(f"Link {link_id} is not attached to source output metadata")

    current_lf_types = (
        discover_lf_node_types()
        if lf_node_types is None
        else frozenset(lf_node_types)
    )
    used_lf_types = frozenset(node_type for node_type in node_types if node_type.startswith("LF_"))
    missing_lf_types = sorted(used_lf_types - current_lf_types)
    uncovered_lf_types = sorted(current_lf_types - used_lf_types)
    if missing_lf_types:
        errors.append("Workflow uses unknown LF node types: " + ", ".join(missing_lf_types))
    if uncovered_lf_types:
        message = "Workflow does not exercise LF node types: " + ", ".join(uncovered_lf_types)
        (errors if require_all_lf_nodes else warnings).append(message)
    if nonzero_modes:
        warnings.append("Workflow has non-default node modes: " + ", ".join(nonzero_modes))

    prompt: dict[str, Any] = {}
    if not errors or all("does not exercise LF node types" in error for error in errors):
        try:
            prompt = converter(workflow)
        except Exception as error:
            errors.append(f"Workflow-to-prompt conversion failed: {error}")
        else:
            if len(prompt) != len(node_by_id):
                errors.append(
                    f"Workflow-to-prompt conversion produced {len(prompt)} entries for "
                    f"{len(node_by_id)} nodes"
                )
            invalid_prompt_nodes = sorted(
                node_id
                for node_id, prompt_node in prompt.items()
                if not isinstance(prompt_node, dict)
                or not isinstance(prompt_node.get("class_type"), str)
                or not isinstance(prompt_node.get("inputs"), dict)
            )
            if invalid_prompt_nodes:
                errors.append("Converted prompt has invalid nodes: " + ", ".join(invalid_prompt_nodes))

    return {
        "schema": "lf.workflow-preflight.v1",
        "status": "complete" if not errors else "blocked",
        "counts": {
            "links": len(link_by_id),
            "nodes": len(node_by_id),
            "prompt_nodes": len(prompt),
            "unique_lf_types": len(used_lf_types),
            "unique_types": len(set(node_types)),
        },
        "missing_lf_types": missing_lf_types,
        "uncovered_lf_types": uncovered_lf_types,
        "non_lf_types": sorted(set(node_types) - used_lf_types),
        "errors": errors,
        "warnings": warnings,
    }


def preflight_workflow_file(
    workflow_path: Path,
    *,
    require_all_lf_nodes: bool = False,
) -> dict[str, Any]:
    try:
        workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return {
            "schema": "lf.workflow-preflight.v1",
            "status": "blocked",
            "path": str(workflow_path),
            "errors": [f"Could not read workflow: {error}"],
            "warnings": [],
        }
    if not isinstance(workflow, dict):
        return {
            "schema": "lf.workflow-preflight.v1",
            "status": "blocked",
            "path": str(workflow_path),
            "errors": ["Workflow root must be an object"],
            "warnings": [],
        }
    report = preflight_workflow_data(
        workflow,
        require_all_lf_nodes=require_all_lf_nodes,
    )
    report["path"] = str(workflow_path.resolve())
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workflow", type=Path)
    parser.add_argument(
        "--require-all-lf-nodes",
        action="store_true",
        help="Treat LF mappings absent from the workflow as a blocking error.",
    )
    args = parser.parse_args(argv)
    report = preflight_workflow_file(
        args.workflow,
        require_all_lf_nodes=args.require_all_lf_nodes,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
