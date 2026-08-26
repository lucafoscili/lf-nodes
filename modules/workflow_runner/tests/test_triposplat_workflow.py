"""Offline contracts for the generic TripoSplat Runner workflow."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import types
from typing import Any

import pytest


# Keep the declarative contract independent of Comfy's torch startup.
REPO_ROOT = Path(__file__).resolve().parents[3]
constants_module = sys.modules.setdefault(
    "modules.utils.constants", types.ModuleType("modules.utils.constants")
)
constants_module.API_ROUTE_PREFIX = "/api/lf-nodes"
constants_module.FUNCTION = "on_exec"
constants_module.Input = getattr(
    constants_module,
    "Input",
    types.SimpleNamespace(STRING="STRING", LF_TREE="LF_TREE"),
)
helpers_module = sys.modules.setdefault(
    "modules.utils.helpers", types.ModuleType("modules.utils.helpers")
)
helpers_module.__path__ = [str(REPO_ROOT / "modules" / "utils" / "helpers")]  # type: ignore[attr-defined]
conversion_module = types.ModuleType("modules.utils.helpers.conversion")
conversion_module.json_safe = lambda value: value
sys.modules.setdefault("modules.utils.helpers.conversion", conversion_module)

from modules.workflow_runner.services.registry import InputValidationError
from modules.workflow_runner.workflows import _WORKFLOW_MODULES
from modules.workflow_runner.workflows import triposplat as workflow_module


WORKFLOW = workflow_module.WORKFLOW
MAX_SEED = (1 << 53) - 1


def _defaults() -> dict[str, Any]:
    return {
        "image": [Path("C:/uploads/object.png")],
        "automatic_background_removal": True,
        "density": "full",
        "edge_cleanup": "gentle",
        "export_format": "spz",
        "seed": "42",
    }


def test_declaration_is_one_guided_generic_3d_workflow() -> None:
    assert WORKFLOW.id == "triposplat_image_to_splat"
    assert WORKFLOW.value == "Image to Gaussian Splat"
    assert WORKFLOW.category == "TripoSplat"
    assert "not a watertight" in WORKFLOW.description
    assert [cell.id for cell in WORKFLOW.inputs] == [
        "image",
        "automatic_background_removal",
        "density",
        "edge_cleanup",
        "export_format",
        "seed",
    ]
    assert [cell.shape for cell in WORKFLOW.inputs] == [
        "upload",
        "toggle",
        "select",
        "select",
        "select",
        "textfield",
    ]
    assert [(cell.node_id, cell.id) for cell in WORKFLOW.outputs] == [
        ("save_preview", "preview"),
        ("save_video", "orbit"),
        ("save_splat", "splat"),
    ]
    assert all(cell.description for cell in (*WORKFLOW.inputs, *WORKFLOW.outputs))
    assert "triposplat" in _WORKFLOW_MODULES


def test_choices_surface_only_native_density_and_export_options() -> None:
    cells = {cell.id: cell for cell in WORKFLOW.inputs}

    assert [
        node["workflowValue"]
        for node in cells["density"].props["lfDataset"]["nodes"]
    ] == ["full", "balanced", "light", "draft"]
    assert cells["density"].props["lfValue"] == "full"
    assert max(workflow_module._DENSITY_BY_ID.values()) == 262144
    assert min(workflow_module._DENSITY_BY_ID.values()) == 32768
    assert [
        node["workflowValue"]
        for node in cells["export_format"].props["lfDataset"]["nodes"]
    ] == ["spz", "ply", "ksplat"]
    assert cells["export_format"].props["lfValue"] == "spz"
    assert [
        node["workflowValue"]
        for node in cells["edge_cleanup"].props["lfDataset"]["nodes"]
    ] == ["gentle", "off", "strong"]


def test_graph_matches_the_pinned_core_recipe_and_outputs() -> None:
    prompt = WORKFLOW.load_prompt()

    assert len(prompt) == 21
    node_ids = list(prompt)
    assert node_ids[node_ids.index("preprocess") + 1] == "first_input"
    assert prompt["background_model"]["inputs"]["bg_removal_name"] == (
        "birefnet.safetensors"
    )
    assert prompt["diffusion_model"]["inputs"] == {
        "unet_name": "triposplat_fp16.safetensors",
        "weight_dtype": "default",
    }
    assert prompt["vision_encoder"]["inputs"]["clip_name"] == (
        "dino_v3_vit_h.safetensors"
    )
    assert prompt["image_vae"]["inputs"]["vae_name"] == "flux2-vae.safetensors"
    assert prompt["splat_vae"]["inputs"]["vae_name"] == (
        "triposplat_vae_decoder_fp16.safetensors"
    )
    assert prompt["preprocess"]["inputs"]["size"] == 1024
    assert prompt["first_input"] == {
        "inputs": {
            "image": ["preprocess", 0],
            "batch_index": 0,
            "length": 1,
        },
        "class_type": "ImageFromBatch",
        "_meta": {"title": "Use the first uploaded frame"},
    }
    assert prompt["conditioning"]["inputs"]["image"] == ["first_input", 0]
    assert prompt["sample"]["inputs"] == {
        "model": ["diffusion_model", 0],
        "positive": ["conditioning", 0],
        "negative": ["conditioning", 1],
        "latent_image": ["conditioning", 2],
        "seed": 42,
        "steps": 20,
        "cfg": 3.0,
        "sampler_name": "dpmpp_2m",
        "scheduler": "simple",
        "denoise": 1.0,
    }
    assert prompt["decode"]["inputs"]["num_gaussians"] == 262144
    assert prompt["decode"]["inputs"]["seed"] == 42
    assert prompt["render_orbit"]["inputs"]["width"] == 1024
    assert prompt["render_orbit"]["inputs"]["height"] == 1024
    assert prompt["render_orbit"]["inputs"]["frames"] == 75
    assert prompt["create_video"]["inputs"]["fps"] == 25.0
    assert prompt["save_video"]["inputs"]["format"] == "mp4"
    assert prompt["save_splat"]["class_type"] == "SaveGLB"
    assert prompt["splat_file"]["inputs"]["format"] == "spz"
    assert not any(
        "api" in node["class_type"].casefold() for node in prompt.values()
    )
    assert not any(
        node["class_type"] == "TripoSplatSamplingPreview"
        for node in prompt.values()
    )


def test_configure_maps_every_control_and_reuses_the_seed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    resolved = "lf_workflow_runner/sha256-object.png [input]"
    monkeypatch.setattr(
        workflow_module,
        "resolve_load_image_reference",
        lambda inputs, name: resolved
        if name == "image" and inputs[name] == [Path("C:/uploads/object.png")]
        else pytest.fail("unexpected upload resolution request"),
    )
    prompt = WORKFLOW.load_prompt()

    WORKFLOW.configure_prompt(
        prompt,
        {
            **_defaults(),
            "automatic_background_removal": False,
            "density": "light",
            "edge_cleanup": "strong",
            "export_format": "ply",
            "seed": "240826",
        },
    )

    assert prompt["load_image"]["inputs"]["image"] == resolved
    assert prompt["mask_source"]["inputs"]["switch"] is False
    assert prompt["preprocess"]["inputs"]["erode_radius"] == 2
    assert prompt["sample"]["inputs"]["seed"] == 240826
    assert prompt["decode"]["inputs"]["seed"] == 240826
    assert prompt["decode"]["inputs"]["num_gaussians"] == 65536
    assert prompt["splat_file"]["inputs"]["format"] == "ply"
    assert prompt["save_splat"]["inputs"]["filename_prefix"] == (
        "LF_Nodes/TripoSplat/seed-240826-light"
    )
    assert prompt["save_preview"]["inputs"]["filename_prefix"].endswith(
        "-preview"
    )
    assert prompt["save_video"]["inputs"]["filename_prefix"].endswith("-orbit")


@pytest.mark.parametrize(
    ("overrides", "input_name"),
    [
        ({"automatic_background_removal": object()}, "automatic_background_removal"),
        ({"density": "oversampled"}, "density"),
        ({"edge_cleanup": "maximum"}, "edge_cleanup"),
        ({"export_format": "splat"}, "export_format"),
        ({"seed": -1}, "seed"),
        ({"seed": MAX_SEED + 1}, "seed"),
    ],
)
def test_invalid_scalars_fail_before_upload_staging(
    monkeypatch: pytest.MonkeyPatch,
    overrides: dict[str, Any],
    input_name: str,
) -> None:
    monkeypatch.setattr(
        workflow_module,
        "resolve_load_image_reference",
        lambda *_args, **_kwargs: pytest.fail("invalid run must not stage uploads"),
    )
    prompt = WORKFLOW.load_prompt()
    original = copy.deepcopy(prompt)

    with pytest.raises((InputValidationError, ValueError)) as error:
        WORKFLOW.configure_prompt(prompt, {**_defaults(), **overrides})

    if isinstance(error.value, InputValidationError):
        assert error.value.input_name == input_name
    else:
        assert input_name in str(error.value)
    assert prompt == original


def test_download_graph_is_self_contained_and_uses_visible_defaults() -> None:
    assert WORKFLOW.configure_download is not None
    prompt = WORKFLOW.load_prompt()
    defaults = {
        cell.id: cell.props.get("lfValue")
        for cell in WORKFLOW.inputs
        if "lfValue" in cell.props
    }

    WORKFLOW.configure_download(prompt, defaults)

    assert prompt["load_image"]["inputs"]["image"] == "example.png"
    assert prompt["mask_source"]["inputs"]["switch"] is True
    assert prompt["decode"]["inputs"]["num_gaussians"] == 262144
    assert prompt["splat_file"]["inputs"]["format"] == "spz"


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
    ).casefold()
    public += WORKFLOW.workflow_path.read_text(encoding="utf-8").casefold()

    for forbidden in (
        "velora",
        "stellaris",
        "azeroth",
        "sentinel",
        "kaldorei",
        "portrait foundry",
    ):
        assert forbidden not in public
