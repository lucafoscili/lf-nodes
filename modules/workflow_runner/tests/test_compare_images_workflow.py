"""Offline contract tests for the guided image comparison Runner workflow."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import types

import pytest


# Keep the declarative workflow contract independent of Comfy's torch/xformers
# startup. Production supplies these modules; the registry only needs these
# lightweight values during this test.
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
from modules.workflow_runner.workflows import _WORKFLOW_MODULES
from modules.workflow_runner.workflows import compare_images as workflow_module
from modules.workflow_runner.workflows.compare_images import WORKFLOW


def test_declaration_is_a_small_guided_generic_comparison() -> None:
    assert WORKFLOW.id == "compare_images"
    assert WORKFLOW.value == "Compare Images"
    assert WORKFLOW.category == "Image Processing"
    assert [(cell.node_id, cell.id, cell.shape) for cell in WORKFLOW.inputs] == [
        ("load_before", "before_path", "upload"),
        ("load_after", "after_path", "upload"),
    ]
    assert [(cell.node_id, cell.id, cell.shape) for cell in WORKFLOW.outputs] == [
        ("display_comparison", "comparison", "compare"),
    ]
    assert all(cell.description for cell in WORKFLOW.inputs)
    assert WORKFLOW.outputs[0].props == {
        "lfShape": "image",
        "lfView": "main",
    }


def test_workflow_is_part_of_the_packaged_inventory() -> None:
    assert "compare_images" in _WORKFLOW_MODULES


def test_graph_preserves_alpha_for_both_images_before_comparing() -> None:
    graph = json.loads(WORKFLOW.workflow_path.read_text(encoding="utf-8"))

    assert [node["class_type"] for node in graph.values()] == [
        "LoadImage",
        "JoinImageWithAlpha",
        "LoadImage",
        "JoinImageWithAlpha",
        "LF_CompareImages",
        "LF_DisplayJSON",
    ]
    assert graph["restore_before_alpha"]["inputs"] == {
        "image": ["load_before", 0],
        "alpha": ["load_before", 1],
    }
    assert graph["restore_after_alpha"]["inputs"] == {
        "image": ["load_after", 0],
        "alpha": ["load_after", 1],
    }
    assert graph["compare"]["inputs"] == {
        "image_after": ["restore_after_alpha", 0],
        "image_before": ["restore_before_alpha", 0],
        "ui_widget": {},
    }
    assert graph["display_comparison"]["inputs"] == {
        "json_input": ["compare", 3],
        "ui_widget": "",
    }


def test_configure_maps_both_uploads(monkeypatch: pytest.MonkeyPatch) -> None:
    references = {
        "before_path": "lf_workflow_runner/sha256-before.png [input]",
        "after_path": "lf_workflow_runner/sha256-after.png [input]",
    }
    expected_paths = {
        "before_path": [Path("C:/uploads/before.png")],
        "after_path": [Path("C:/uploads/after.png")],
    }

    def resolve(inputs: dict, name: str) -> str:
        assert inputs[name] == expected_paths[name]
        return references[name]

    monkeypatch.setattr(workflow_module, "resolve_load_image_reference", resolve)
    prompt = WORKFLOW.load_prompt()

    WORKFLOW.configure_prompt(prompt, expected_paths)

    assert prompt["load_before"]["inputs"]["image"] == references["before_path"]
    assert prompt["load_after"]["inputs"]["image"] == references["after_path"]


@pytest.mark.parametrize("missing_name", ["before_path", "after_path"])
def test_configure_fails_closed_when_an_upload_is_missing(
    monkeypatch: pytest.MonkeyPatch,
    missing_name: str,
) -> None:
    inputs = {
        name: [Path(f"C:/uploads/{name}.png")]
        for name in ("before_path", "after_path")
        if name != missing_name
    }

    def resolve(values: dict, name: str) -> str:
        if name not in values:
            raise InputValidationError(name)
        return f"lf_workflow_runner/sha256-{name}.png [input]"

    monkeypatch.setattr(workflow_module, "resolve_load_image_reference", resolve)

    with pytest.raises(InputValidationError) as error:
        WORKFLOW.configure_prompt(WORKFLOW.load_prompt(), inputs)

    assert error.value.input_name == missing_name


def test_public_workflow_copy_has_no_consumer_specific_vocabulary() -> None:
    public_text = json.dumps(
        {
            "id": WORKFLOW.id,
            "value": WORKFLOW.value,
            "description": WORKFLOW.description,
            "category": WORKFLOW.category,
            "inputs": [cell.to_dict() for cell in WORKFLOW.inputs],
            "outputs": [cell.to_dict() for cell in WORKFLOW.outputs],
        },
        ensure_ascii=False,
    ).lower()
    public_text += WORKFLOW.workflow_path.read_text(encoding="utf-8").lower()

    for forbidden in ("velora", "stellaris", "azeroth", "portrait", "sprite"):
        assert forbidden not in public_text
