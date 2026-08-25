from __future__ import annotations

import ast
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
NODES_ROOT = ROOT / "modules" / "nodes"
WIDGET_TYPES = ROOT / "web" / "src" / "types" / "widgets" / "widgets.ts"
WIDGET_MANAGER = ROOT / "web" / "src" / "helpers" / "manager.ts"


def _typescript_enum(source: str, name: str) -> str:
    marker = f"export enum {name} {{"
    return source.split(marker, 1)[1].split("}", 1)[0]


def _frontend_contract() -> tuple[set[str], dict[str, set[str]]]:
    widget_source = WIDGET_TYPES.read_text(encoding="utf-8")
    node_block = _typescript_enum(widget_source, "NodeName")
    custom_widget_block = _typescript_enum(widget_source, "CustomWidgetName")

    node_names = set(re.findall(r"=\s*'(LF_[^']+)'", node_block))
    custom_widget_values = {
        name: value
        for name, value in re.findall(
            r"\b(\w+)\s*=\s*'(LF_[^']+)'",
            custom_widget_block,
        )
    }

    manager_source = WIDGET_MANAGER.read_text(encoding="utf-8")
    map_block = manager_source.split(
        "export const NODE_WIDGET_MAP",
        1,
    )[1].split("};", 1)[0]
    widget_map: dict[str, set[str]] = {}
    for node_name, registered in re.findall(
        r"^\s*(LF_[A-Za-z0-9_]+):\s*\[([^\]]*)\]",
        map_block,
        re.MULTILINE,
    ):
        widget_map[node_name] = {
            custom_widget_values[property_name]
            for property_name in re.findall(
                r"CustomWidgetName\.(\w+)",
                registered,
            )
        }
    return node_names, widget_map


def _backend_contract() -> dict[str, set[str]]:
    custom_widget_types = set(
        re.findall(
            r"=\s*'(LF_[^']+)'",
            _typescript_enum(
                WIDGET_TYPES.read_text(encoding="utf-8"),
                "CustomWidgetName",
            ),
        )
    )
    nodes: dict[str, set[str]] = {}

    for path in sorted(NODES_ROOT.rglob("*.py")):
        module = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
        classes = {
            item.name: item
            for item in module.body
            if isinstance(item, ast.ClassDef)
        }
        mappings: dict[str, str] = {}
        for item in module.body:
            if not isinstance(item, ast.Assign) or not isinstance(item.value, ast.Dict):
                continue
            if not any(
                isinstance(target, ast.Name)
                and target.id == "NODE_CLASS_MAPPINGS"
                for target in item.targets
            ):
                continue
            for key, value in zip(item.value.keys, item.value.values):
                if (
                    isinstance(key, ast.Constant)
                    and isinstance(key.value, str)
                    and isinstance(value, ast.Name)
                ):
                    mappings[key.value] = value.id

        for node_name, class_name in mappings.items():
            declared: set[str] = set()
            node_class = classes[class_name]
            for item in node_class.body:
                if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                if item.name != "INPUT_TYPES":
                    continue
                for token in ast.walk(item):
                    if (
                        isinstance(token, ast.Attribute)
                        and isinstance(token.value, ast.Name)
                        and token.value.id == "Input"
                        and token.attr in custom_widget_types
                    ):
                        declared.add(token.attr)
                    elif (
                        isinstance(token, ast.Constant)
                        and isinstance(token.value, str)
                        and token.value in custom_widget_types
                    ):
                        declared.add(token.value)
            nodes[node_name] = declared
    return nodes


def test_backend_and_frontend_node_widget_registries_are_exact() -> None:
    backend = _backend_contract()
    node_names, widget_map = _frontend_contract()

    assert set(backend) == node_names
    assert set(backend) == set(widget_map)
    assert widget_map["LF_ACEStepRemix"] == set()
    assert "LF_Brush" not in widget_map
    assert "LF_ExtractFaceEmbedding" not in widget_map

    for node_name, declared_widgets in backend.items():
        assert widget_map[node_name] == declared_widgets, node_name
