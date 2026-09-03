"""Offline contracts for the cardinal-turnaround assembly block."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import types
from typing import Any, Iterable

import pytest


# Declarative workflow tests do not need Comfy's torch/xformers startup.
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
from modules.workflow_runner.workflows import cardinal_turnaround as workflow_module


WORKFLOW = workflow_module.WORKFLOW
DIRECTIONS = ("front", "right", "back", "left")
UPLOAD_IDS = tuple(f"{direction}_image" for direction in DIRECTIONS)


def _inputs(**overrides: Any) -> dict[str, Any]:
    return {
        **{
            field_id: [Path(f"C:/uploads/{field_id}.png")]
            for field_id in UPLOAD_IDS
        },
        "canvas_size": "1280",
        "content_height": "1120",
        "bottom_padding": "64",
        **overrides,
    }


def _linked_node_ids(value: Any) -> Iterable[str]:
    if (
        isinstance(value, list)
        and len(value) == 2
        and isinstance(value[0], str)
        and isinstance(value[1], int)
    ):
        yield value[0]
        return
    if isinstance(value, dict):
        for child in value.values():
            yield from _linked_node_ids(child)
    elif isinstance(value, list):
        for child in value:
            yield from _linked_node_ids(child)


def test_declaration_is_one_small_generic_registered_block() -> None:
    assert WORKFLOW.id == "assemble_cardinal_turnaround"
    assert WORKFLOW.value == "Assemble Cardinal Turnaround"
    assert WORKFLOW.category == "Image Processing"
    assert "one shared scale and horizontal registration" in WORKFLOW.description
    assert "contain-fitted into the front canvas" in WORKFLOW.description
    assert "transparent centered padding and no crop" in WORKFLOW.description
    assert [cell.id for cell in WORKFLOW.inputs] == [
        *UPLOAD_IDS,
        "canvas_size",
        "content_height",
        "bottom_padding",
    ]
    assert all(cell.shape == "upload" for cell in WORKFLOW.inputs[:4])
    assert all(cell.required for cell in WORKFLOW.inputs[:4])
    assert all(
        cell.props["lfHtmlAttributes"]["accept"] == "image/*"
        for cell in WORKFLOW.inputs[:4]
    )
    assert [(cell.node_id, cell.id, cell.shape) for cell in WORKFLOW.outputs] == [
        ("save_front", "front", "masonry"),
        ("save_right", "right", "masonry"),
        ("save_back", "back", "masonry"),
        ("save_left", "left", "masonry"),
        ("save_contact_sheet", "contact_sheet", "masonry"),
        ("display_normalization_receipt", "normalization_receipt", "code"),
    ]
    assert all(cell.description for cell in (*WORKFLOW.inputs, *WORKFLOW.outputs))
    assert WORKFLOW.outputs[-1].props == {"lfLanguage": "json"}
    assert "cardinal_turnaround" in _WORKFLOW_MODULES


def test_registration_knobs_have_concrete_eli5_defaults() -> None:
    cells = {cell.id: cell for cell in WORKFLOW.inputs}
    assert cells["canvas_size"].props["lfValue"] == "1024"
    assert cells["content_height"].props["lfValue"] == "900"
    assert cells["bottom_padding"].props["lfValue"] == "48"
    assert "one scale" in cells["content_height"].description.lower()
    assert "equipment and shadows" in cells["content_height"].description
    assert "vertical baseline" in cells["bottom_padding"].description
    assert "shared with the front" in cells["bottom_padding"].description


def test_every_direction_has_the_same_rmbg_and_alpha_validation_chain() -> None:
    prompt = WORKFLOW.load_prompt()

    for direction in DIRECTIONS:
        assert prompt[f"remove_{direction}"]["inputs"] == {
            "image": [f"load_{direction}", 0],
            "model": "RMBG-2.0",
            "sensitivity": 1.0,
            "process_res": 1024,
            "mask_blur": 0,
            "mask_offset": 0,
            "invert_output": False,
            "refine_foreground": False,
            "background": "Alpha",
        }
        assert prompt[f"verify_{direction}_alpha"]["class_type"] == "ImageToMask"
        assert prompt[f"verify_{direction}_alpha"]["inputs"] == {
            "image": [f"remove_{direction}", 0],
            "channel": "alpha",
        }
        assert prompt[f"invert_{direction}_alpha"]["inputs"] == {
            "mask": [f"verify_{direction}_alpha", 0]
        }
        assert prompt[f"validated_{direction}"]["inputs"] == {
            "image": [f"remove_{direction}", 0],
            "alpha": [f"invert_{direction}_alpha", 0],
        }

    assert sum(
        node["class_type"] == "VNCCS_RMBG2" for node in prompt.values()
    ) == 4
    assert sum(node["class_type"] == "ImageToMask" for node in prompt.values()) == 4


def test_one_lossless_list_and_front_authoritative_normalizer_register_all_views() -> None:
    prompt = WORKFLOW.load_prompt()

    assert prompt["list_views"] == {
        "inputs": {
            "image_1": ["validated_front", 0],
            "image_2": ["validated_right", 0],
            "image_3": ["validated_back", 0],
            "image_4": ["validated_left", 0],
            "ui_widget": {},
        },
        "class_type": "LF_ImageList",
        "_meta": {
            "title": "Keep cardinal source canvases in explicit clockwise order"
        },
    }
    normalizers = [
        node for node in prompt.values() if node["class_type"] == "LF_NormalizeSpriteBatch"
    ]
    assert len(normalizers) == 1
    assert normalizers[0]["inputs"] == {
        "image": ["list_views", 0],
        "canvas_width": 1024,
        "canvas_height": 1024,
        "target_reference_alpha_height": 900,
        "reference_frame_index": 0,
        "bottom_padding": 48,
        "ui_widget": {},
    }
    assert not any(
        node["class_type"]
        in {"BatchImagesNode", "ImageScale", "LF_ResizeImageToDimension"}
        for node in prompt.values()
    )


def test_each_direction_becomes_one_distinct_reusable_artifact() -> None:
    prompt = WORKFLOW.load_prompt()

    for index, direction in enumerate(DIRECTIONS):
        assert prompt[f"select_{direction}"]["inputs"] == {
            "image": ["normalize_views", 0],
            "batch_index": index,
            "length": 1,
        }
        assert prompt[f"save_{direction}"]["inputs"]["images"] == [
            f"select_{direction}",
            0,
        ]
        assert prompt[f"save_{direction}"]["inputs"]["filename_prefix"].endswith(
            f"/{direction}"
        )
    assert len({WORKFLOW.outputs[index].node_id for index in range(4)}) == 4


def test_contact_sheet_is_full_resolution_labeled_and_not_the_artifact_transport() -> None:
    prompt = WORKFLOW.load_prompt()
    grid = prompt["contact_sheet"]

    assert grid["class_type"] == "LF_ImageGrid"
    assert grid["inputs"] == {
        "image": ["normalize_views", 0],
        "cell_width": 1024,
        "cell_height": 1024,
        "gap_px": 8,
        "background": "transparent",
        "show_headers": True,
        "title": "Cardinal Turnaround",
        "dataset": {
            "columns": [
                {"id": "front", "title": "FRONT"},
                {"id": "right", "title": "SUBJECT RIGHT"},
                {"id": "back", "title": "BACK"},
                {"id": "left", "title": "SUBJECT LEFT"},
            ],
            "nodes": [{"id": "views", "value": "VIEWS"}],
        },
        "ui_widget": {},
    }
    assert prompt["save_contact_sheet"]["inputs"]["images"] == [
        "contact_sheet",
        0,
    ]
    assert all(
        prompt[f"save_{direction}"]["inputs"]["images"][0]
        != "contact_sheet"
        for direction in DIRECTIONS
    )


def test_configuration_maps_uploads_and_all_registration_settings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []

    def resolve(inputs: dict[str, Any], field_id: str) -> str:
        calls.append(field_id)
        assert inputs[field_id] == [Path(f"C:/uploads/{field_id}.png")]
        return f"lf_workflow_runner/{field_id}.png [input]"

    monkeypatch.setattr(workflow_module, "resolve_load_image_reference", resolve)
    prompt = WORKFLOW.load_prompt()
    WORKFLOW.configure_prompt(prompt, _inputs())

    assert calls == list(UPLOAD_IDS)
    for direction in DIRECTIONS:
        assert prompt[f"load_{direction}"]["inputs"]["image"] == (
            f"lf_workflow_runner/{direction}_image.png [input]"
        )
    assert prompt["normalize_views"]["inputs"] == {
        "image": ["list_views", 0],
        "canvas_width": 1280,
        "canvas_height": 1280,
        "target_reference_alpha_height": 1120,
        "reference_frame_index": 0,
        "bottom_padding": 64,
        "ui_widget": {},
    }
    assert prompt["contact_sheet"]["inputs"]["cell_width"] == 1280
    assert prompt["contact_sheet"]["inputs"]["cell_height"] == 1280
    expected_root = (
        "LF_Nodes/CardinalTurnaround/1280px-content-1120px-bottom-64px"
    )
    for direction in DIRECTIONS:
        assert prompt[f"save_{direction}"]["inputs"]["filename_prefix"] == (
            f"{expected_root}/{direction}"
        )
    assert prompt["save_contact_sheet"]["inputs"]["filename_prefix"] == (
        f"{expected_root}/contact-sheet"
    )


@pytest.mark.parametrize("missing_input", UPLOAD_IDS)
def test_all_four_uploads_are_required_before_staging(
    monkeypatch: pytest.MonkeyPatch,
    missing_input: str,
) -> None:
    inputs = _inputs()
    inputs.pop(missing_input)
    monkeypatch.setattr(
        workflow_module,
        "resolve_load_image_reference",
        lambda *_args: pytest.fail("incomplete turnaround must not stage uploads"),
    )
    prompt = WORKFLOW.load_prompt()
    original = copy.deepcopy(prompt)

    with pytest.raises(InputValidationError) as error:
        WORKFLOW.configure_prompt(prompt, inputs)

    assert error.value.input_name == missing_input
    assert prompt == original


@pytest.mark.parametrize(
    ("overrides", "input_name", "error_type"),
    [
        ({"canvas_size": True}, "canvas_size", InputValidationError),
        ({"canvas_size": 128}, "canvas_size", ValueError),
        ({"content_height": "large"}, "content_height", InputValidationError),
        ({"bottom_padding": -1}, "bottom_padding", ValueError),
        (
            {"canvas_size": 1024, "content_height": 1000, "bottom_padding": 48},
            "content_height",
            ValueError,
        ),
    ],
)
def test_invalid_geometry_fails_before_staging(
    monkeypatch: pytest.MonkeyPatch,
    overrides: dict[str, Any],
    input_name: str,
    error_type: type[Exception],
) -> None:
    monkeypatch.setattr(
        workflow_module,
        "resolve_load_image_reference",
        lambda *_args: pytest.fail("invalid geometry must not stage uploads"),
    )

    with pytest.raises(error_type) as error:
        WORKFLOW.configure_prompt(WORKFLOW.load_prompt(), _inputs(**overrides))

    if isinstance(error.value, InputValidationError):
        assert error.value.input_name == input_name
    else:
        assert input_name in str(error.value)


def test_download_configuration_uses_placeholders_without_staging(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        workflow_module,
        "resolve_load_image_reference",
        lambda *_args: pytest.fail("download must retain portable placeholders"),
    )
    prompt = WORKFLOW.load_prompt()
    placeholders = {
        direction: prompt[f"load_{direction}"]["inputs"]["image"]
        for direction in DIRECTIONS
    }

    assert WORKFLOW.configure_download is not None
    WORKFLOW.configure_download(
        prompt,
        {"canvas_size": 768, "content_height": 672, "bottom_padding": 32},
    )

    assert {
        direction: prompt[f"load_{direction}"]["inputs"]["image"]
        for direction in DIRECTIONS
    } == placeholders
    assert prompt["normalize_views"]["inputs"]["canvas_width"] == 768
    assert prompt["normalize_views"]["inputs"]["canvas_height"] == 768
    assert prompt["normalize_views"]["inputs"][
        "target_reference_alpha_height"
    ] == 672
    assert prompt["normalize_views"]["inputs"]["bottom_padding"] == 32


def test_graph_links_model_assets_and_copy_are_portable() -> None:
    prompt = WORKFLOW.load_prompt()
    for node in prompt.values():
        for source_id in _linked_node_ids(node.get("inputs", {})):
            assert source_id in prompt

    assert {
        path
        for asset in WORKFLOW.required_model_assets
        for path in asset.relative_paths
    } == {
        "RMBG/RMBG-2.0/config.json",
        "RMBG/RMBG-2.0/model.safetensors",
        "RMBG/RMBG-2.0/birefnet.py",
        "RMBG/RMBG-2.0/BiRefNet_config.py",
    }

    public = json.dumps(
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
    public += WORKFLOW.workflow_path.read_text(encoding="utf-8").lower()
    for forbidden in ("velora", "eden", "sentinel", "azeroth", "stellaris"):
        assert forbidden not in public
