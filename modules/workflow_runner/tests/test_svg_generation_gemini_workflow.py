"""Offline wiring checks; these tests never call Gemini or save an SVG."""

import json
import sys
import types

import pytest

# Reuse the declaration-only Krea fixtures without loading the host/GPU stack.
constants_module = types.ModuleType("modules.utils.constants")
constants_module.API_ROUTE_PREFIX = "/api/lf-nodes"
helpers_module = types.ModuleType("modules.utils.helpers")
helpers_module.__path__ = []  # type: ignore[attr-defined]
conversion_module = types.ModuleType("modules.utils.helpers.conversion")
conversion_module.json_safe = lambda value: value
sys.modules.setdefault("modules.utils.constants", constants_module)
sys.modules.setdefault("modules.utils.helpers", helpers_module)
sys.modules.setdefault("modules.utils.helpers.conversion", conversion_module)

from modules.workflow_runner.services.registry import InputValidationError
from modules.workflow_runner.workflows.svg_generation_gemini import WORKFLOW


def _graph():
    return json.loads(WORKFLOW.workflow_path.read_text(encoding="utf-8"))


def test_public_model_and_icon_size_reach_the_real_graph_inputs() -> None:
    graph = _graph()

    WORKFLOW.configure_prompt(graph, {
        "prompt": "A compass icon",
        "icon_size": "96",
        "model": "explicit-test-model",
        "strip_attributes": False,
    })

    assert graph["21"]["inputs"]["replacement"] == "A compass icon"
    assert graph["22"]["class_type"] == "LF_StringReplace"
    assert graph["22"]["inputs"]["replacement"] == "96"
    assert "integer" not in graph["22"]["inputs"]
    assert graph["33"]["inputs"]["model"] == "explicit-test-model"
    assert graph["29"]["inputs"]["boolean"] is False


def test_existing_public_defaults_are_preserved() -> None:
    graph = _graph()
    defaults = {
        cell.id: cell.props["lfValue"]
        for cell in WORKFLOW.inputs
        if "lfValue" in cell.props
    }

    WORKFLOW.configure_prompt(graph, defaults)

    assert graph["21"]["inputs"]["replacement"] == "Una persona"
    assert graph["22"]["inputs"]["replacement"] == "24"
    assert graph["33"]["inputs"]["model"] == "gemini-2.5-flash-image"
    assert graph["29"]["inputs"]["boolean"] is True
    assert graph["15"]["inputs"]["filename_prefix"] == ""
    assert graph["15"]["inputs"]["add_timestamp"] is False
    assert graph["15"]["inputs"]["add_counter"] is True


@pytest.mark.parametrize(
    ("model_inputs", "expected"),
    (
        ({}, "gemini-2.5-flash-image"),
        ({"gemini_model": "legacy-test-model"}, "legacy-test-model"),
        ({"model": "public", "gemini_model": "legacy"}, "public"),
    ),
)
def test_optional_model_preserves_graph_default_and_legacy_alias(model_inputs, expected) -> None:
    graph = _graph()

    WORKFLOW.configure_prompt(graph, {"prompt": "A compass icon", **model_inputs})

    assert graph["22"]["inputs"]["replacement"] == "24"
    assert graph["33"]["inputs"]["model"] == expected


def test_saver_uses_existing_collision_counter_without_changing_output_location() -> None:
    graph = _graph()
    graph["15"]["inputs"].update({
        "filename_prefix": "custom-icons/compass",
        "add_timestamp": True,
        "add_counter": False,
    })

    WORKFLOW.configure_prompt(graph, {"prompt": "A compass icon"})

    assert graph["15"]["inputs"]["filename_prefix"] == "custom-icons/compass"
    assert graph["15"]["inputs"]["add_timestamp"] is True
    assert graph["15"]["inputs"]["add_counter"] is True


def test_prompt_remains_required() -> None:
    with pytest.raises(InputValidationError) as error:
        WORKFLOW.configure_prompt(_graph(), {})

    assert error.value.input_name == "prompt"
