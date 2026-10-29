"""Offline contract tests for the Texture Edge Padding Runner block."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import types

import pytest


# Keep this declarative workflow contract independent of Comfy's torch/xformers
# startup. The production host supplies these modules; this test needs only the
# lightweight values consumed by the registry and package config.
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
from modules.workflow_runner.workflows import texture_edge_padding as workflow_module
from modules.workflow_runner.workflows.texture_edge_padding import WORKFLOW


def test_declaration_is_a_file_in_file_out_block() -> None:
    assert WORKFLOW.id == "texture_edge_padding"
    assert WORKFLOW.value == "Texture Edge Padding"
    assert WORKFLOW.category == "Image Processing"
    assert [(cell.node_id, cell.id, cell.shape) for cell in WORKFLOW.inputs] == [
        ("load_image", "image_path", "upload"),
        ("load_mask", "mask_path", "upload"),
        ("save", "filename_prefix", "textfield"),
    ]
    assert [(cell.node_id, cell.id, cell.shape) for cell in WORKFLOW.outputs] == [
        ("save", "padded_image", "masonry"),
        ("display_receipt", "padding_receipt", "code"),
    ]
    assert all(cell.description for cell in WORKFLOW.inputs + WORKFLOW.outputs)
    assert WORKFLOW.outputs[1].props["lfLanguage"] == "json"


def test_workflow_is_part_of_the_packaged_inventory() -> None:
    assert "texture_edge_padding" in _WORKFLOW_MODULES


def test_graph_reads_the_mask_from_red_and_publishes_the_receipt() -> None:
    graph = json.loads(WORKFLOW.workflow_path.read_text(encoding="utf-8"))

    assert [node["class_type"] for node in graph.values()] == [
        "LoadImage",
        "LoadImageMask",
        "LF_EdgePadding",
        "SaveImage",
        "LF_DisplayJSON",
    ]
    # Red, not alpha: Core inverts only an alpha-channel mask.
    assert graph["load_mask"]["inputs"]["channel"] == "red"
    assert graph["pad"]["inputs"]["image"] == ["load_image", 0]
    assert graph["pad"]["inputs"]["mask"] == ["load_mask", 0]
    assert graph["save"]["inputs"]["images"] == ["pad", 0]
    assert graph["display_receipt"]["inputs"]["json_input"] == ["pad", 1]


def test_configure_maps_both_uploads_and_the_prefix(monkeypatch: pytest.MonkeyPatch) -> None:
    resolved = {
        "image_path": "lf_workflow_runner/sha256-texture.png [input]",
        "mask_path": "lf_workflow_runner/sha256-mask.png [input]",
    }
    monkeypatch.setattr(workflow_module, "resolve_load_image_reference", lambda inputs, name: resolved[name])
    prompt = WORKFLOW.load_prompt()

    WORKFLOW.configure_prompt(
        prompt,
        {
            "image_path": [Path("C:/uploads/texture.png")],
            "mask_path": [Path("C:/uploads/mask.png")],
            "filename_prefix": "textures/padded",
        },
    )

    assert prompt["load_image"]["inputs"]["image"] == resolved["image_path"]
    assert prompt["load_mask"]["inputs"]["image"] == resolved["mask_path"]
    assert prompt["save"]["inputs"]["filename_prefix"] == "textures/padded"


@pytest.mark.parametrize("prefix", [None, "", "   ", 42])
def test_configure_refuses_a_missing_prefix(prefix: object) -> None:
    inputs = {"image_path": "C:/uploads/texture.png", "mask_path": "C:/uploads/mask.png"}
    if prefix is not None:
        inputs["filename_prefix"] = prefix

    with pytest.raises(InputValidationError) as error:
        WORKFLOW.configure_prompt(WORKFLOW.load_prompt(), inputs)

    assert error.value.input_name == "filename_prefix"
