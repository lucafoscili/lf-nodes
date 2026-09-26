"""Contracts for the opt-in MiniMax H3 learned-HD finishing pass."""

from __future__ import annotations

from copy import deepcopy
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
from modules.workflow_runner.workflows import minimax_h3 as h3
from modules.workflow_runner.workflows import minimax_h3_hd as hd


EXPECTED_HD_SIZES = {
    "16:9": ((1344, 768), (1920, 1088)),
    "4:3": ((1024, 768), (1664, 1248)),
    "1:1": ((768, 768), (1440, 1440)),
    "3:4": ((768, 1024), (1248, 1664)),
    "9:16": ((768, 1344), (1088, 1920)),
    "21:9": ((1536, 672), (2208, 960)),
}


def _cells(workflow: Any) -> dict[str, Any]:
    return {cell.id: cell for cell in workflow.inputs}


def _default_inputs(workflow: Any) -> dict[str, Any]:
    inputs = {
        cell.id: cell.props["lfValue"]
        for cell in workflow.inputs
        if "lfValue" in cell.props
    }
    for cell in workflow.inputs:
        if cell.shape == "upload" and cell.required:
            inputs[cell.id] = [Path(f"C:/uploads/{cell.id}.png")]
    return inputs


def _configure(
    workflow: Any,
    monkeypatch: pytest.MonkeyPatch,
    **overrides: Any,
) -> dict[str, Any]:
    monkeypatch.setattr(
        h3,
        "resolve_load_image_reference",
        lambda _inputs, field: f"staged/{field}.png",
    )
    prompt = workflow.load_prompt()
    workflow.configure_prompt(
        prompt,
        {**_default_inputs(workflow), **overrides},
    )
    return prompt


def _assert_hd_core(
    prompt: dict[str, Any],
    *,
    base_size: tuple[int, int],
    target_size: tuple[int, int],
) -> None:
    assert (
        prompt["h3"]["inputs"]["width"],
        prompt["h3"]["inputs"]["height"],
    ) == base_size
    assert (
        prompt["h3_hd_conditioning"]["inputs"]["width"],
        prompt["h3_hd_conditioning"]["inputs"]["height"],
    ) == target_size
    assert prompt["h3_hd_scheduler"]["inputs"] == {
        "model": ["attention_backend", 0],
        "scheduler": "simple",
        "steps": 4,
        "denoise": 0.25,
    }
    assert prompt["h3_hd_parameters"]["inputs"] == {
        "model_name": hd.HD_UPSCALER_MODEL,
        "width": target_size[0],
        "height": target_size[1],
        "device": "cuda",
        "precision": "bf16",
        "keep_models_resident": False,
    }
    assert prompt["h3_hd_upscale"]["inputs"] == {
        "model": ["attention_backend", 0],
        "conditioning": ["h3_hd_conditioning", 0],
        "latent": ["sample", 1],
        "noise": ["noise", 0],
        "sampler": ["sampler_select", 0],
        "sigmas": ["h3_hd_scheduler", 0],
        "cfg": 1.0,
        "latent_upscale_param": ["h3_hd_parameters", 0],
    }
    assert prompt["decode_video"]["inputs"]["samples"] == [
        "h3_hd_upscale",
        0,
    ]
    assert prompt["decode_audio"]["inputs"]["samples"] == ["sample", 0]
    assert prompt["create_video"]["inputs"]["audio"] == ["decode_audio", 0]
    assert prompt["save"]["inputs"]["filename_prefix"].endswith("-hd4")


def test_every_h3_card_has_one_standard_default_quality_control_and_hd_prerequisite(
) -> None:
    for workflow in h3.WORKFLOWS:
        quality = _cells(workflow)[hd.OUTPUT_QUALITY_INPUT_ID]
        assert quality.props["lfValue"] == hd.OUTPUT_QUALITY_STANDARD
        assert [
            option["workflowValue"]
            for option in quality.props["lfDataset"]["nodes"]
        ] == [hd.OUTPUT_QUALITY_STANDARD, hd.OUTPUT_QUALITY_HD]
        assert workflow.input_option_requirements.count(
            hd.HD_OPTION_REQUIREMENT
        ) == 1

    assert hd.HD_OPTION_REQUIREMENT.required_node_types == (
        "MMH3LatentUpscaleWithModelParams",
        "MMH3UltimateUpscale",
    )
    assert hd.HD_OPTION_REQUIREMENT.required_model_assets[0].relative_paths == (
        "latent_upscale_models/"
        "minimax_h3_latent_upscaler_3d_conv_v1_bf16.safetensors",
    )


def test_standard_quality_keeps_every_configured_graph_on_the_native_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for workflow in h3.WORKFLOWS:
        implicit = _configure(workflow, monkeypatch)
        explicit = _configure(
            workflow,
            monkeypatch,
            output_quality=hd.OUTPUT_QUALITY_STANDARD,
        )
        assert implicit == explicit
        assert not any(node_id.startswith("h3_hd_") for node_id in implicit)
        assert implicit["decode_video"]["inputs"]["samples"] == ["sample", 0]
        assert implicit["decode_audio"]["inputs"]["samples"] == ["sample", 0]
        assert not implicit["save"]["inputs"]["filename_prefix"].endswith(
            "-hd4"
        )


@pytest.mark.parametrize("aspect_ratio", tuple(EXPECTED_HD_SIZES))
def test_hd_uses_curated_two_megapixel_canvas_and_shared_first_pass(
    monkeypatch: pytest.MonkeyPatch,
    aspect_ratio: str,
) -> None:
    workflow = h3.WORKFLOW_BY_ID["minimax_h3_generate_video"]
    prompt = _configure(
        workflow,
        monkeypatch,
        aspect_ratio=aspect_ratio,
        output_quality=hd.OUTPUT_QUALITY_HD,
        seed="73",
    )
    base_size, target_size = EXPECTED_HD_SIZES[aspect_ratio]
    _assert_hd_core(prompt, base_size=base_size, target_size=target_size)
    assert prompt["noise"]["inputs"]["noise_seed"] == 73
    assert prompt["h3_hd_conditioning"]["inputs"]["prompt"] == prompt["h3"][
        "inputs"
    ]["prompt"]


def test_hd_reference_conditioning_keeps_prompt_and_ordered_sources(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workflow = h3.WORKFLOW_BY_ID["minimax_h3_character_swap"]
    prompt = _configure(
        workflow,
        monkeypatch,
        aspect_ratio="3:4",
        output_quality=hd.OUTPUT_QUALITY_HD,
    )
    _assert_hd_core(
        prompt,
        base_size=(768, 1024),
        target_size=(1248, 1664),
    )
    target = prompt["h3_hd_conditioning"]
    assert target["class_type"] == "MiniMaxH3ReferenceToVideo"
    assert target["inputs"]["prompt"] == ["prompt_join", 0]
    assert target["inputs"]["ref_image_size"] == "max"
    assert target["inputs"]["ref_images.ref_image_0"] == ["source_1", 0]
    assert target["inputs"]["ref_images.ref_image_1"] == ["source_2", 0]


def test_hd_rebuilds_active_guide_chain_at_target_resolution_and_feeds_sprites(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workflow = h3.WORKFLOW_BY_ID["minimax_h3_anchored_sprite_loop"]
    prompt = _configure(
        workflow,
        monkeypatch,
        output_quality=hd.OUTPUT_QUALITY_HD,
        guide_image_1=[Path("C:/uploads/guide-1.png")],
        guide_frame_1="90",
        guide_image_2=[Path("C:/uploads/guide-2.png")],
        guide_frame_2="60",
    )

    assert prompt["guider"]["inputs"]["conditioning"] == ["guide_1", 0]
    assert prompt["h3_hd_guide_2"]["inputs"]["positive"] == [
        "h3_hd_conditioning",
        0,
    ]
    assert prompt["h3_hd_guide_1"]["inputs"]["positive"] == [
        "h3_hd_guide_2",
        0,
    ]
    for guide in ("h3_hd_guide_1", "h3_hd_guide_2"):
        assert prompt[guide]["inputs"]["latent"] == [
            "h3_hd_conditioning",
            1,
        ]
    assert prompt["h3_hd_upscale"]["inputs"]["conditioning"] == [
        "h3_hd_guide_1",
        0,
    ]
    assert prompt["sprite_sampler"]["inputs"]["image"] == ["decode_video", 0]
    assert prompt["decode_video"]["inputs"]["samples"] == [
        "h3_hd_upscale",
        0,
    ]


@pytest.mark.parametrize(
    ("workflow_id", "consumer"),
    [
        ("minimax_h3_directed_view", "settled_selector"),
        ("minimax_h3_character_turnaround", "sprite_sampler"),
    ],
)
def test_hd_is_applied_before_downstream_still_consumers(
    monkeypatch: pytest.MonkeyPatch,
    workflow_id: str,
    consumer: str,
) -> None:
    prompt = _configure(
        h3.WORKFLOW_BY_ID[workflow_id],
        monkeypatch,
        output_quality=hd.OUTPUT_QUALITY_HD,
    )
    assert prompt["decode_video"]["inputs"]["samples"] == [
        "h3_hd_upscale",
        0,
    ]
    assert prompt[consumer]["inputs"]["image"] == ["decode_video", 0]


@pytest.mark.parametrize(
    "updates",
    [
        {"output_quality": "ultra"},
        {
            "output_quality": hd.OUTPUT_QUALITY_HD,
            "execution_profile": "turbo_preview",
        },
    ],
)
def test_invalid_or_unvalidated_quality_fails_before_upload_staging_or_mutation(
    monkeypatch: pytest.MonkeyPatch,
    updates: dict[str, str],
) -> None:
    workflow = h3.WORKFLOW_BY_ID["minimax_h3_animate_image"]
    monkeypatch.setattr(
        h3,
        "resolve_load_image_reference",
        lambda *_args: pytest.fail("invalid quality must not stage uploads"),
    )
    prompt = workflow.load_prompt()
    original = deepcopy(prompt)
    with pytest.raises((InputValidationError, ValueError)):
        workflow.configure_prompt(
            prompt,
            {**_default_inputs(workflow), **updates},
        )
    assert prompt == original


def test_hd_target_size_rejects_unowned_canvases() -> None:
    with pytest.raises(ValueError, match="curated native"):
        hd.hd_target_size(800, 800)
