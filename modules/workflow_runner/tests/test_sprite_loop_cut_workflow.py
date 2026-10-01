"""Offline contracts for the sprite-loop-cut block."""

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
from modules.workflow_runner.workflows import sprite_loop_cut as workflow_module


WORKFLOW = workflow_module.WORKFLOW


def _inputs(**overrides: Any) -> dict[str, Any]:
    return {"source_video": [Path("C:/uploads/shot.mp4")], **overrides}


def test_block_declares_a_video_upload_and_atlas_outputs() -> None:
    assert WORKFLOW.id == "sprite_loop_cut"
    assert WORKFLOW.value == "Sprite Loop Cut"
    assert WORKFLOW.category == "Image Processing"
    assert "seam versus motion" in WORKFLOW.description
    assert [cell.id for cell in WORKFLOW.inputs] == [
        "source_video",
        "frame_count",
        "columns",
        "min_period_frames",
        "max_period_frames",
        "motion_floor",
        "canvas_size",
        "content_height",
        "bottom_padding",
    ]
    upload = WORKFLOW.inputs[0]
    assert upload.shape == "upload" and upload.required
    assert upload.props["lfHtmlAttributes"]["accept"].startswith("video/")
    assert [(cell.node_id, cell.id, cell.shape) for cell in WORKFLOW.outputs] == [
        ("save_frames", "frames", "masonry"),
        ("save_atlas", "atlas", "masonry"),
        ("display_loop_receipt", "loop_receipt", "code"),
        ("display_normalization_receipt", "normalization_receipt", "code"),
    ]
    assert all(cell.description for cell in (*WORKFLOW.inputs, *WORKFLOW.outputs))
    assert "sprite_loop_cut" in _WORKFLOW_MODULES


def test_graph_feeds_decoded_frames_and_fps_into_the_loop_picker() -> None:
    prompt = WORKFLOW.load_prompt()
    assert prompt["components"]["inputs"] == {"video": ["load_video", 0]}
    assert prompt["select_loop"]["class_type"] == "LF_SelectLoopSegment"
    assert prompt["select_loop"]["inputs"]["image"] == ["components", 0]
    assert prompt["select_loop"]["inputs"]["source_fps"] == ["components", 2]
    assert prompt["remove_background"]["class_type"] == "LF_BackgroundRemover"
    assert prompt["remove_background"]["inputs"] == {
        "image": ["select_loop", 0],
        "transparent_background": True,
        "background_color": "#000000",
        "model": "RMBG-2.0",
    }
    assert prompt["verify_alpha"]["inputs"] == {
        "image": ["remove_background", 0],
        "channel": "alpha",
    }
    assert prompt["invert_alpha"]["inputs"] == {"mask": ["verify_alpha", 0]}
    assert prompt["validated_cutout"]["inputs"] == {
        "image": ["remove_background", 0],
        "alpha": ["invert_alpha", 0],
    }
    assert prompt["normalize"]["inputs"]["image"] == ["validated_cutout", 0]
    assert prompt["save_frames"]["inputs"]["images"] == ["normalize", 0]
    assert prompt["sprite_grid"]["inputs"]["image"] == ["normalize", 0]
    assert prompt["save_atlas"]["inputs"]["images"] == ["sprite_grid", 0]
    assert prompt["display_loop_receipt"]["inputs"]["json_input"] == ["select_loop", 1]
    assert prompt["display_normalization_receipt"]["inputs"]["json_input"] == ["normalize", 1]


def test_configure_registers_the_upload_and_the_grid(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        workflow_module, "resolve_load_image_reference", lambda inputs, name: "lf/shot.mp4 [input]"
    )
    prompt = WORKFLOW.load_prompt()
    WORKFLOW.configure_prompt(prompt, _inputs(frame_count="30", columns="5", canvas_size="384", content_height="200", bottom_padding="20", motion_floor="0.5", min_period_frames="20", max_period_frames="72"))
    assert prompt["load_video"]["inputs"]["file"] == "lf/shot.mp4 [input]"
    assert prompt["select_loop"]["inputs"]["target_count"] == 30
    assert prompt["select_loop"]["inputs"]["min_period_frames"] == 20
    assert prompt["select_loop"]["inputs"]["max_period_frames"] == 72
    assert prompt["select_loop"]["inputs"]["motion_floor"] == 0.5
    assert prompt["normalize"]["inputs"]["canvas_width"] == 384
    assert prompt["normalize"]["inputs"]["target_reference_alpha_height"] == 200
    assert prompt["normalize"]["inputs"]["bottom_padding"] == 20
    dataset = prompt["sprite_grid"]["inputs"]["dataset"]
    assert len(dataset["columns"]) == 5 and len(dataset["nodes"]) == 6
    assert prompt["sprite_grid"]["inputs"]["cell_width"] == 384
    assert prompt["save_frames"]["inputs"]["filename_prefix"] == (
        "LF_Nodes/SpriteLoopCut/384px-content-200px-bottom-20px-f30/frames"
    )
    assert prompt["save_atlas"]["inputs"]["filename_prefix"].endswith("/atlas-5x6")


def test_download_keeps_the_placeholder_upload() -> None:
    prompt = WORKFLOW.load_prompt()
    WORKFLOW.configure_download(prompt, {"frame_count": "24", "columns": "6"})
    assert prompt["load_video"]["inputs"]["file"] == "shot.mp4"
    assert len(prompt["sprite_grid"]["inputs"]["dataset"]["nodes"]) == 4


def test_model_readiness_requires_the_local_rmbg2_package() -> None:
    assert len(WORKFLOW.required_model_assets) == 1
    asset = WORKFLOW.required_model_assets[0]
    assert asset.label == "RMBG-2.0 model"
    assert asset.relative_paths == (
        "RMBG/RMBG-2.0/config.json",
        "RMBG/RMBG-2.0/model.safetensors",
        "RMBG/RMBG-2.0/birefnet.py",
        "RMBG/RMBG-2.0/BiRefNet_config.py",
    )


@pytest.mark.parametrize(
    "overrides, field",
    [
        ({"columns": "5"}, "columns"),
        ({"columns": "0"}, "columns"),
        ({"frame_count": "x"}, "frame_count"),
        ({"max_period_frames": "6"}, "max_period_frames"),
        ({"content_height": "250"}, "content_height"),
        ({"motion_floor": "7"}, "motion_floor"),
    ],
)
def test_incoherent_controls_are_refused_by_field(overrides: dict, field: str) -> None:
    with pytest.raises(InputValidationError) as error:
        workflow_module.settings({"frame_count": "24", "columns": "6", **overrides})
    assert field in str(error.value)
