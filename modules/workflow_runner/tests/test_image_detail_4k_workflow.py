"""Offline contract tests for the public 4K diffusion-detail workflow."""

from __future__ import annotations

import json
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
from modules.workflow_runner.workflows import image_detail_4k as workflow_module


FORBIDDEN_VOCABULARY = ("velora", "stellaris", "azeroth", "sentinel", "sprite")


def _classes(prompt: dict[str, Any]) -> set[str]:
    return {
        node["class_type"]
        for node in prompt.values()
        if isinstance(node, dict) and "class_type" in node
    }


def test_workflow_is_discoverable_focused_and_fully_described() -> None:
    workflow = workflow_module.WORKFLOW

    assert "image_detail_4k" in _WORKFLOW_MODULES
    assert workflow.id == "image_detail_4k"
    assert workflow.value == "4K Detail Pass · SeedVR2"
    assert workflow.category == "Image Processing"
    assert "local" not in workflow.description.lower()
    assert [cell.id for cell in workflow.inputs] == [
        "source_path",
        "target_size",
        "seed",
    ]
    assert [cell.id for cell in workflow.outputs] == ["image"]
    assert "diffusion" in workflow.description.lower()
    assert "plain resize" in workflow.description.lower()
    for cell in (*workflow.inputs, *workflow.outputs):
        assert cell.description


def test_graph_pins_the_conservative_experience_checked_profile() -> None:
    prompt = workflow_module.WORKFLOW.load_prompt()

    assert _classes(prompt) == {
        "LoadImage",
        "JoinImageWithAlpha",
        "SeedVR2LoadDiTModel",
        "SeedVR2LoadVAEModel",
        "SeedVR2VideoUpscaler",
        "SaveImage",
    }
    assert prompt["join_alpha"]["inputs"] == {
        "image": ["load_image", 0],
        "alpha": ["load_image", 1],
    }
    assert prompt["dit"]["inputs"] == {
        "model": "seedvr2_ema_3b_fp8_e4m3fn.safetensors",
        "device": "cuda:0",
        "blocks_to_swap": 16,
        "swap_io_components": False,
        "offload_device": "cpu",
        "cache_model": False,
        "attention_mode": "sdpa",
    }
    assert prompt["vae"]["inputs"] == {
        "model": "ema_vae_fp16.safetensors",
        "device": "cuda:0",
        "encode_tiled": True,
        "encode_tile_size": 1024,
        "encode_tile_overlap": 128,
        "decode_tiled": True,
        "decode_tile_size": 1024,
        "decode_tile_overlap": 128,
        "tile_debug": "false",
        "offload_device": "cpu",
        "cache_model": False,
    }
    assert {
        key: prompt["detail_4k"]["inputs"][key]
        for key in (
            "batch_size",
            "color_correction",
            "input_noise_scale",
            "latent_noise_scale",
            "offload_device",
        )
    } == {
        "batch_size": 1,
        "color_correction": "lab",
        "input_noise_scale": 0.0,
        "latent_noise_scale": 0.0,
        "offload_device": "cpu",
    }


@pytest.mark.parametrize(
    ("target", "edge", "folder"),
    [
        ("uhd_3840", 3840, "UHD-3840"),
        ("dci_4096", 4096, "DCI-4096"),
    ],
)
def test_configure_maps_upload_target_and_seed(
    monkeypatch: pytest.MonkeyPatch,
    target: str,
    edge: int,
    folder: str,
) -> None:
    source = [Path("C:/uploads/finished.png")]
    calls: list[str] = []

    def resolve(inputs: dict[str, Any], name: str) -> str:
        calls.append(name)
        assert inputs[name] == source
        return "lf_workflow_runner/finished.png [input]"

    monkeypatch.setattr(workflow_module, "resolve_load_image_reference", resolve)
    prompt = workflow_module.WORKFLOW.load_prompt()
    workflow_module.WORKFLOW.configure_prompt(
        prompt,
        {"source_path": source, "target_size": target, "seed": 240824},
    )

    assert calls == ["source_path"]
    assert prompt["load_image"]["inputs"]["image"].endswith(
        "finished.png [input]"
    )
    assert prompt["detail_4k"]["inputs"]["resolution"] == edge
    assert prompt["detail_4k"]["inputs"]["max_resolution"] == edge
    assert prompt["detail_4k"]["inputs"]["seed"] == 240824
    assert prompt["save"]["inputs"]["filename_prefix"].endswith(
        f"4KDetail/{folder}/seed-240824"
    )


@pytest.mark.parametrize(
    ("inputs", "input_name"),
    [
        ({"target_size": "uhd_3840"}, "source_path"),
        (
            {
                "source_path": [Path("C:/uploads/finished.png")],
                "target_size": "8k",
            },
            "target_size",
        ),
        (
            {
                "source_path": [Path("C:/uploads/finished.png")],
                "target_size": "uhd_3840",
                "seed": "not-a-seed",
            },
            "seed",
        ),
    ],
)
def test_invalid_input_fails_before_staging_upload(
    monkeypatch: pytest.MonkeyPatch,
    inputs: dict[str, Any],
    input_name: str,
) -> None:
    monkeypatch.setattr(
        workflow_module,
        "resolve_load_image_reference",
        lambda *_args: pytest.fail("invalid request must not stage uploads"),
    )
    with pytest.raises(InputValidationError) as error:
        workflow_module.WORKFLOW.configure_prompt(
            workflow_module.WORKFLOW.load_prompt(),
            inputs,
        )
    assert error.value.input_name == input_name


def test_public_contract_is_consumer_agnostic() -> None:
    workflow = workflow_module.WORKFLOW
    public_text = json.dumps(
        {
            "id": workflow.id,
            "value": workflow.value,
            "description": workflow.description,
            "category": workflow.category,
            "inputs": [cell.to_dict() for cell in workflow.inputs],
            "outputs": [cell.to_dict() for cell in workflow.outputs],
        },
        ensure_ascii=False,
    ).lower()
    public_text += workflow.workflow_path.read_text(encoding="utf-8").lower()

    for forbidden in FORBIDDEN_VOCABULARY:
        assert forbidden not in public_text
