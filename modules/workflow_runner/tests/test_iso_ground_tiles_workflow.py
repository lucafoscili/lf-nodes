"""Offline contracts for the iso-ground-tiles block."""

from __future__ import annotations

from pathlib import Path
import sys
import types
from typing import Any

import pytest


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
from modules.workflow_runner.workflows import iso_ground_tiles as workflow_module


WORKFLOW = workflow_module.WORKFLOW


def test_block_declares_texture_upload_and_tile_outputs() -> None:
    assert WORKFLOW.id == "iso_ground_tiles"
    assert WORKFLOW.value == "Iso Ground Tiles"
    assert "squashed 2:1" in WORKFLOW.description
    assert [cell.id for cell in WORKFLOW.inputs] == [
        "source_texture",
        "blend_fraction",
        "tile_width",
        "tile_height",
        "variants",
        "texture_scale",
        "seed",
    ]
    assert WORKFLOW.inputs[0].shape == "upload" and WORKFLOW.inputs[0].required
    assert [(cell.node_id, cell.id, cell.shape) for cell in WORKFLOW.outputs] == [
        ("save_tiles", "tiles", "masonry"),
        ("save_texture", "texture", "masonry"),
        ("display_receipt", "receipt", "code"),
    ]
    assert all(cell.description for cell in (*WORKFLOW.inputs, *WORKFLOW.outputs))
    assert "iso_ground_tiles" in _WORKFLOW_MODULES


def test_graph_chains_seamless_then_diamonds() -> None:
    prompt = WORKFLOW.load_prompt()
    assert prompt["seamless"]["class_type"] == "LF_SeamlessTile"
    assert prompt["seamless"]["inputs"]["image"] == ["load_texture", 0]
    assert prompt["diamonds"]["class_type"] == "LF_IsoDiamondTiles"
    assert prompt["diamonds"]["inputs"]["image"] == ["seamless", 0]
    assert prompt["save_texture"]["inputs"]["images"] == ["seamless", 0]
    assert prompt["save_tiles"]["inputs"]["images"] == ["diamonds", 1]
    assert prompt["display_receipt"]["inputs"]["json_input"] == ["diamonds", 2]


def test_configure_registers_the_upload_and_tile_geometry(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        workflow_module, "resolve_load_image_reference", lambda inputs, name: "lf/texture.png [input]"
    )
    prompt = WORKFLOW.load_prompt()
    WORKFLOW.configure_prompt(
        prompt,
        {
            "source_texture": [Path("C:/uploads/texture.png")],
            "blend_fraction": "0.3",
            "tile_width": "256",
            "tile_height": "128",
            "variants": "6",
            "texture_scale": "0.75",
            "seed": "9",
        },
    )
    assert prompt["load_texture"]["inputs"]["image"] == "lf/texture.png [input]"
    assert prompt["seamless"]["inputs"]["blend_fraction"] == 0.3
    assert prompt["diamonds"]["inputs"] == {
        "image": ["seamless", 0],
        "tile_width": 256,
        "tile_height": 128,
        "variants": 6,
        "seed": 9,
        "texture_scale": 0.75,
        "ui_widget": {},
    }
    assert prompt["save_tiles"]["inputs"]["filename_prefix"] == (
        "LF_Nodes/IsoGroundTiles/256x128-v6-seed-9/tiles"
    )


def test_download_keeps_the_placeholder_upload_and_defaults() -> None:
    prompt = WORKFLOW.load_prompt()
    WORKFLOW.configure_download(prompt, {})
    assert prompt["load_texture"]["inputs"]["image"] == "texture.png"
    assert prompt["diamonds"]["inputs"]["variants"] == 4


@pytest.mark.parametrize(
    "overrides, field",
    [
        ({"blend_fraction": "0.9"}, "blend_fraction"),
        ({"tile_width": "2"}, "tile_width"),
        ({"variants": "0"}, "variants"),
        ({"seed": "-1"}, "seed"),
        ({"texture_scale": "abc"}, "texture_scale"),
    ],
)
def test_out_of_range_controls_are_refused_by_field(overrides: dict[str, Any], field: str) -> None:
    with pytest.raises(InputValidationError) as error:
        workflow_module.settings(overrides)
    assert field in str(error.value)
