"""Pure helpers shared by workflow declaration consumers."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def select_option_value(option: Mapping[str, Any]) -> Any:
    """Return the value submitted by the Runner for one select option."""

    value = option.get("workflowValue")
    if value is None:
        value = option.get("value")
    if value is None:
        value = option.get("id")
    return value


def input_default_value(cell: object) -> tuple[bool, Any]:
    """Resolve one declared default using the browser's select semantics."""

    props = getattr(cell, "props", None)
    if not isinstance(props, Mapping) or "lfValue" not in props:
        return False, None

    raw_default = props["lfValue"]
    if str(getattr(cell, "shape", "") or "").lower() != "select":
        return True, raw_default

    dataset = props.get("lfDataset")
    nodes = dataset.get("nodes") if isinstance(dataset, Mapping) else None
    if not isinstance(nodes, (list, tuple)) or not nodes:
        return False, None

    selected: Any = None
    if type(raw_default) is int:
        # lf-select treats a numeric default as an option index. Numeric
        # workflow values therefore use a string option id in declarations.
        if 0 <= raw_default < len(nodes):
            selected = nodes[raw_default]
    else:
        selected = next(
            (
                option
                for option in nodes
                if isinstance(option, Mapping)
                and str(option.get("id", "")) == str(raw_default)
            ),
            None,
        )
    if not isinstance(selected, Mapping):
        return False, None
    return True, select_option_value(selected)


def default_input_values(workflow: object) -> dict[str, Any]:
    """Project one workflow declaration's semantic public defaults."""

    values: dict[str, Any] = {}
    for cell in getattr(workflow, "inputs", ()):
        input_id = getattr(cell, "id", None)
        has_default, value = input_default_value(cell)
        if isinstance(input_id, str) and has_default:
            values[input_id] = value
    return values


__all__ = ["default_input_values", "input_default_value", "select_option_value"]
