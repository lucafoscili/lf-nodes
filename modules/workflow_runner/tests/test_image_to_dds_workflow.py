"""Offline contract tests for the guided image-to-DDS Runner workflow."""

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
from modules.workflow_runner.workflows import image_to_dds as workflow_module
from modules.workflow_runner.workflows.image_to_dds import WORKFLOW


def test_declaration_is_a_small_guided_generic_conversion() -> None:
    assert WORKFLOW.id == "image_to_dds"
    assert WORKFLOW.value == "Image to DDS"
    assert WORKFLOW.category == "Image Processing"
    assert [(cell.node_id, cell.id, cell.shape) for cell in WORKFLOW.inputs] == [
        ("load_image", "source_path", "upload"),
        ("save_dds", "filename_prefix", "textfield"),
        ("save_dds", "pixel_format", "select"),
        ("save_dds", "mip_policy", "select"),
    ]
    assert [(cell.node_id, cell.id, cell.shape) for cell in WORKFLOW.outputs] == [
        ("save_dds", "dds_file", "masonry"),
        ("display_receipt", "dds_receipt", "code"),
    ]
    assert all(cell.description for cell in WORKFLOW.inputs)
    assert WORKFLOW.outputs[1].props["lfLanguage"] == "json"


def test_all_public_choices_have_plain_language_labels_and_descriptions() -> None:
    pixel_nodes = WORKFLOW.inputs[2].props["lfDataset"]["nodes"]
    mip_nodes = WORKFLOW.inputs[3].props["lfDataset"]["nodes"]

    assert [node["workflowValue"] for node in pixel_nodes] == [
        "RGB24",
        "RGBA32",
        "BC1",
        "BC3",
    ]
    assert [node["workflowValue"] for node in mip_nodes] == ["none", "full_chain"]
    assert all("—" in node["value"] and node["description"] for node in pixel_nodes)
    assert all(node["description"] for node in mip_nodes)
    assert WORKFLOW.inputs[2].props["lfValue"] == "RGBA32"
    assert WORKFLOW.inputs[3].props["lfValue"] == "none"


def test_workflow_is_part_of_the_packaged_inventory() -> None:
    assert "image_to_dds" in _WORKFLOW_MODULES


def test_graph_preserves_alpha_before_saving_and_displays_receipt() -> None:
    graph = json.loads(WORKFLOW.workflow_path.read_text(encoding="utf-8"))

    assert [node["class_type"] for node in graph.values()] == [
        "LoadImage",
        "JoinImageWithAlpha",
        "LF_SaveDDS",
        "LF_DisplayJSON",
    ]
    assert graph["restore_alpha"]["inputs"] == {
        "image": ["load_image", 0],
        "alpha": ["load_image", 1],
    }
    assert graph["save_dds"]["inputs"] == {
        "image": ["restore_alpha", 0],
        "filename_prefix": "LF_Nodes/DDS",
        "pixel_format": "RGBA32",
        "mip_policy": "none",
        "ui_widget": {},
    }
    assert graph["display_receipt"]["inputs"]["json_input"] == ["save_dds", 1]


def test_configure_maps_upload_and_all_options(monkeypatch: pytest.MonkeyPatch) -> None:
    resolved = "lf_workflow_runner/sha256-example.png [input]"
    monkeypatch.setattr(
        workflow_module,
        "resolve_load_image_reference",
        lambda inputs, name: resolved
        if inputs[name] == [Path("C:/uploads/example.png")] and name == "source_path"
        else pytest.fail("unexpected upload resolution request"),
    )
    prompt = WORKFLOW.load_prompt()

    WORKFLOW.configure_prompt(
        prompt,
        {
            "source_path": [Path("C:/uploads/example.png")],
            "filename_prefix": "exports/sample",
            "pixel_format": "BC3",
            "mip_policy": "full_chain",
        },
    )

    assert prompt["load_image"]["inputs"]["image"] == resolved
    assert prompt["save_dds"]["inputs"] == {
        "image": ["restore_alpha", 0],
        "filename_prefix": "exports/sample",
        "pixel_format": "BC3",
        "mip_policy": "full_chain",
        "ui_widget": {},
    }


@pytest.mark.parametrize(
    ("inputs", "input_name"),
    [
        ({}, "filename_prefix"),
        ({"filename_prefix": "   "}, "filename_prefix"),
        ({"filename_prefix": 42}, "filename_prefix"),
        ({"filename_prefix": "DDS"}, "pixel_format"),
        ({"filename_prefix": "DDS", "pixel_format": "BC7"}, "pixel_format"),
        ({"filename_prefix": "DDS", "pixel_format": True}, "pixel_format"),
        (
            {"filename_prefix": "DDS", "pixel_format": "RGBA32"},
            "mip_policy",
        ),
        (
            {
                "filename_prefix": "DDS",
                "pixel_format": "RGBA32",
                "mip_policy": "sometimes",
            },
            "mip_policy",
        ),
    ],
)
def test_configure_rejects_invalid_settings_before_staging_upload(
    monkeypatch: pytest.MonkeyPatch,
    inputs: dict,
    input_name: str,
) -> None:
    monkeypatch.setattr(
        workflow_module,
        "resolve_load_image_reference",
        lambda *_args, **_kwargs: pytest.fail("upload must not be staged"),
    )

    with pytest.raises(InputValidationError) as error:
        WORKFLOW.configure_prompt(WORKFLOW.load_prompt(), inputs)

    assert error.value.input_name == input_name


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
