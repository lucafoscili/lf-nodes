"""Offline contracts for the generic 2x2 image-sheet Runner workflow."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import types
from typing import Any

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
from modules.workflow_runner.workflows import image_sheet as workflow_module


WORKFLOW = workflow_module.WORKFLOW
UPLOAD_IDS = (
    "top_left_image",
    "top_right_image",
    "bottom_left_image",
    "bottom_right_image",
)
LOAD_IDS = (
    "load_top_left",
    "load_top_right",
    "load_bottom_left",
    "load_bottom_right",
)
ALPHA_IDS = (
    "alpha_top_left",
    "alpha_top_right",
    "alpha_bottom_left",
    "alpha_bottom_right",
)
EXPECTED_DATASET = {
    "columns": [
        {"id": "column_1", "title": "Before"},
        {"id": "column_2", "title": "After"},
    ],
    "nodes": [
        {"id": "row_1", "value": "Wide"},
        {"id": "row_2", "value": "Close"},
    ],
}


def _inputs() -> dict[str, Any]:
    return {
        **{
            input_id: [Path(f"C:/uploads/{input_id}.png")]
            for input_id in UPLOAD_IDS
        },
        "sheet_title": "Review Sheet",
        "column_1_label": "Before",
        "column_2_label": "After",
        "row_1_label": "Wide",
        "row_2_label": "Close",
        "cell_width": "640",
        "cell_height": "480",
        "gap_px": "12",
        "background": "white",
        "show_headers": False,
    }


def _configure(
    monkeypatch: pytest.MonkeyPatch,
    **overrides: Any,
) -> tuple[dict[str, Any], list[str]]:
    calls: list[str] = []

    def resolve(inputs: dict[str, Any], name: str) -> str:
        calls.append(name)
        assert inputs[name] == [Path(f"C:/uploads/{name}.png")]
        return f"lf_workflow_runner/{name}.png [input]"

    monkeypatch.setattr(workflow_module, "resolve_load_image_reference", resolve)
    prompt = WORKFLOW.load_prompt()
    WORKFLOW.configure_prompt(prompt, {**_inputs(), **overrides})
    return prompt, calls


def test_public_card_schema_is_small_generic_and_fully_described() -> None:
    assert WORKFLOW.id == "image_sheet"
    assert WORKFLOW.value == "Compose Image Sheet"
    assert WORKFLOW.category == "Image Processing"
    assert "original dimensions and aspect ratio" in WORKFLOW.description
    assert "without cropping or stretching" in WORKFLOW.description
    assert [cell.id for cell in WORKFLOW.inputs] == [
        *UPLOAD_IDS,
        "sheet_title",
        "column_1_label",
        "column_2_label",
        "row_1_label",
        "row_2_label",
        "cell_width",
        "cell_height",
        "gap_px",
        "background",
        "show_headers",
    ]
    assert [cell.shape for cell in WORKFLOW.inputs[:4]] == ["upload"] * 4
    assert all(cell.required for cell in WORKFLOW.inputs[:4])
    assert [(cell.node_id, cell.id, cell.shape) for cell in WORKFLOW.outputs] == [
        ("save", "image", "masonry"),
        ("display_dataset", "dataset", "code"),
        ("display_receipt", "receipt", "code"),
    ]
    assert all(cell.description for cell in (*WORKFLOW.inputs, *WORKFLOW.outputs))
    assert WORKFLOW.outputs[1].props == {"lfLanguage": "json"}
    assert WORKFLOW.outputs[2].props == {"lfLanguage": "json"}


def test_editable_layout_controls_have_safe_visible_defaults() -> None:
    cells = {cell.id: cell for cell in WORKFLOW.inputs}
    assert {
        name: cells[name].props["lfValue"]
        for name in (
            "sheet_title",
            "column_1_label",
            "column_2_label",
            "row_1_label",
            "row_2_label",
        )
    } == {
        "sheet_title": "Image Sheet",
        "column_1_label": "Column 1",
        "column_2_label": "Column 2",
        "row_1_label": "Row 1",
        "row_2_label": "Row 2",
    }
    assert cells["cell_width"].props["lfValue"] == "512"
    assert cells["cell_height"].props["lfValue"] == "512"
    assert cells["gap_px"].props["lfValue"] == "8"
    assert cells["show_headers"].shape == "toggle"
    assert cells["show_headers"].props["lfValue"] is True
    assert [
        option["workflowValue"]
        for option in cells["background"].props["lfDataset"]["nodes"]
    ] == ["transparent", "white", "black"]
    assert cells["background"].props["lfValue"] == "transparent"


def test_graph_preserves_alpha_and_lists_original_images_row_major() -> None:
    prompt = WORKFLOW.load_prompt()

    assert [node["class_type"] for node in prompt.values()] == [
        "LoadImage",
        "JoinImageWithAlpha",
        "LoadImage",
        "JoinImageWithAlpha",
        "LoadImage",
        "JoinImageWithAlpha",
        "LoadImage",
        "JoinImageWithAlpha",
        "LF_ImageList",
        "LF_ImageGrid",
        "SaveImage",
        "LF_DisplayJSON",
        "LF_DisplayJSON",
    ]
    for load_id, alpha_id in zip(LOAD_IDS, ALPHA_IDS):
        assert prompt[alpha_id]["inputs"] == {
            "image": [load_id, 0],
            "alpha": [load_id, 1],
        }

    # LF_ImageList keeps every tensor at its original dimensions so ImageGrid,
    # rather than an upstream batch helper, owns contain-fit and letterboxing.
    assert prompt["image_list"]["inputs"] == {
        "image_1": ["alpha_top_left", 0],
        "image_2": ["alpha_top_right", 0],
        "image_3": ["alpha_bottom_left", 0],
        "image_4": ["alpha_bottom_right", 0],
    }
    assert prompt["grid"]["inputs"]["image"] == ["image_list", 0]


def test_graph_publishes_a_durable_png_plus_dataset_and_receipt() -> None:
    prompt = WORKFLOW.load_prompt()

    assert prompt["grid"]["class_type"] == "LF_ImageGrid"
    assert prompt["grid"]["inputs"]["ui_widget"] == {}
    assert prompt["save"] == {
        "class_type": "SaveImage",
        "inputs": {
            "filename_prefix": "LF_Nodes/ImageSheet/2x2",
            "images": ["grid", 0],
        },
        "_meta": {"title": "Save durable image sheet PNG"},
    }
    assert prompt["display_dataset"]["inputs"] == {
        "json_input": ["grid", 1],
        "ui_widget": "",
    }
    assert prompt["display_receipt"]["inputs"] == {
        "json_input": ["grid", 2],
        "ui_widget": "",
    }


def test_default_graph_contains_a_valid_two_by_two_lf_dataset() -> None:
    dataset = WORKFLOW.load_prompt()["grid"]["inputs"]["dataset"]

    assert dataset == {
        "columns": [
            {"id": "column_1", "title": "Column 1"},
            {"id": "column_2", "title": "Column 2"},
        ],
        "nodes": [
            {"id": "row_1", "value": "Row 1"},
            {"id": "row_2", "value": "Row 2"},
        ],
    }
    assert len(dataset["columns"]) * len(dataset["nodes"]) == len(UPLOAD_IDS)
    assert len({column["id"] for column in dataset["columns"]}) == 2
    assert len({node["id"] for node in dataset["nodes"]}) == 2


def test_configure_maps_uploads_controls_and_dataset_exactly(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prompt, calls = _configure(monkeypatch)

    assert calls == list(UPLOAD_IDS)
    for input_id, load_id in zip(UPLOAD_IDS, LOAD_IDS):
        assert prompt[load_id]["inputs"]["image"] == (
            f"lf_workflow_runner/{input_id}.png [input]"
        )
    assert prompt["grid"]["inputs"] == {
        "image": ["image_list", 0],
        "cell_width": 640,
        "cell_height": 480,
        "gap_px": 12,
        "background": "white",
        "show_headers": False,
        "title": "Review Sheet",
        "dataset": EXPECTED_DATASET,
        "ui_widget": {},
    }


def test_dataset_order_matches_top_left_to_bottom_right_batch_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prompt, _calls = _configure(monkeypatch)
    dataset = prompt["grid"]["inputs"]["dataset"]
    coordinates = [
        (node["id"], column["id"])
        for node in dataset["nodes"]
        for column in dataset["columns"]
    ]
    image_sources = [
        prompt["image_list"]["inputs"][f"image_{index}"][0]
        for index in range(1, 5)
    ]

    assert coordinates == [
        ("row_1", "column_1"),
        ("row_1", "column_2"),
        ("row_2", "column_1"),
        ("row_2", "column_2"),
    ]
    assert image_sources == list(ALPHA_IDS)


@pytest.mark.parametrize("missing_input", UPLOAD_IDS)
def test_each_upload_is_required_before_any_file_is_staged(
    monkeypatch: pytest.MonkeyPatch,
    missing_input: str,
) -> None:
    inputs = _inputs()
    inputs.pop(missing_input)
    monkeypatch.setattr(
        workflow_module,
        "resolve_load_image_reference",
        lambda *_args: pytest.fail("incomplete sheet must not stage uploads"),
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
        ({"cell_width": True}, "cell_width", InputValidationError),
        ({"cell_height": "huge"}, "cell_height", InputValidationError),
        ({"gap_px": -1}, "gap_px", ValueError),
        ({"background": "blue"}, "background", InputValidationError),
        ({"show_headers": "false"}, "show_headers", InputValidationError),
        ({"column_1_label": object()}, "column_1_label", InputValidationError),
    ],
)
def test_invalid_controls_fail_before_upload_staging(
    monkeypatch: pytest.MonkeyPatch,
    overrides: dict[str, Any],
    input_name: str,
    error_type: type[Exception],
) -> None:
    monkeypatch.setattr(
        workflow_module,
        "resolve_load_image_reference",
        lambda *_args: pytest.fail("invalid controls must not stage uploads"),
    )

    with pytest.raises(error_type) as error:
        WORKFLOW.configure_prompt(
            WORKFLOW.load_prompt(),
            {**_inputs(), **overrides},
        )

    if isinstance(error.value, InputValidationError):
        assert error.value.input_name == input_name
    else:
        assert input_name in str(error.value)


def test_filename_prefix_is_stable_and_independent_of_labels(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first, _calls = _configure(monkeypatch)
    second, _calls = _configure(
        monkeypatch,
        sheet_title="Another Sheet",
        column_1_label="Left",
        column_2_label="Right",
        row_1_label="Upper",
        row_2_label="Lower",
    )

    assert first["save"]["inputs"]["filename_prefix"] == (
        "LF_Nodes/ImageSheet/2x2"
    )
    assert second["save"]["inputs"]["filename_prefix"] == (
        "LF_Nodes/ImageSheet/2x2"
    )


def test_public_copy_and_graph_are_domain_neutral() -> None:
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

    for forbidden in (
        "velora",
        "stellaris",
        "azeroth",
        "sentinel",
        "character",
        "portrait",
        "sprite",
        "club",
    ):
        assert forbidden not in public
