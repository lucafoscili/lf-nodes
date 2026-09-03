"""Offline contracts for the native TRELLIS.2 Runner workflow."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import types
from typing import Any, Iterable

import pytest


# Keep the declarative contract independent of Comfy's torch startup.
REPO_ROOT = Path(__file__).resolve().parents[3]
constants_module = sys.modules.setdefault(
    "modules.utils.constants", types.ModuleType("modules.utils.constants")
)
constants_module.API_ROUTE_PREFIX = getattr(
    constants_module, "API_ROUTE_PREFIX", "/api/lf-nodes"
)
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

from modules.workflow_runner.services.readiness import (
    WorkflowReadinessScanner,
    evaluate_workflow_readiness,
)
from modules.workflow_runner.services.registry import InputValidationError
from modules.workflow_runner.workflows import _WORKFLOW_MODULES
from modules.workflow_runner.workflows import trellis2 as workflow_module


SINGLE = workflow_module.WORKFLOWS[0]
MAX_SEED = 0x7FFFFFFF


def _single_inputs(**overrides: Any) -> dict[str, Any]:
    return {
        "image": [Path("C:/uploads/object.png")],
        "quality": "balanced",
        "seed": "42",
        **overrides,
    }


def _default_values(workflow: Any) -> dict[str, Any]:
    return {
        cell.id: cell.props["lfValue"]
        for cell in workflow.inputs
        if "lfValue" in cell.props
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


def _assert_links_resolve(prompt: dict[str, Any]) -> None:
    for node in prompt.values():
        for source_id in _linked_node_ids(node.get("inputs", {})):
            assert source_id in prompt


def test_declaration_is_one_small_native_mesh_card() -> None:
    assert [workflow.id for workflow in workflow_module.WORKFLOWS] == [
        "trellis2_image_to_textured_mesh"
    ]
    assert SINGLE.value == "Image to Textured Mesh"
    assert SINGLE.category == "TRELLIS.2"
    assert [cell.id for cell in SINGLE.inputs] == ["image", "quality", "seed"]
    assert [(cell.node_id, cell.id, cell.shape) for cell in SINGLE.outputs] == [
        ("save_preview", "preview", "masonry"),
        ("register_output", "mesh", "code"),
    ]
    assert all(cell.description for cell in (*SINGLE.inputs, *SINGLE.outputs))
    assert "watertight" in SINGLE.description
    assert "trellis2" in _WORKFLOW_MODULES


def test_quality_select_exposes_only_bounded_24_gb_profiles() -> None:
    cell = next(cell for cell in SINGLE.inputs if cell.id == "quality")
    assert cell.props["lfValue"] == "balanced"
    assert [
        option["workflowValue"] for option in cell.props["lfDataset"]["nodes"]
    ] == ["draft", "balanced"]
    assert [option["profileTier"] for option in cell.props["lfDataset"]["nodes"]] == [
        "fast",
        "baseline",
    ]
    assert [option["value"] for option in cell.props["lfDataset"]["nodes"]] == [
        "Fast · 512",
        "Baseline · 1024",
    ]
    assert workflow_module._QUALITY_SETTINGS == {
        "balanced": {
            "pipeline_type": "1024_cascade",
            "steps": 12,
            "target_face_num": 200000,
            "texture_size": 4096,
            "dual_contouring_resolution": "1024",
        },
        "draft": {
            "pipeline_type": "512",
            "steps": 12,
            "target_face_num": 100000,
            "texture_size": 2048,
            "dual_contouring_resolution": "512",
        },
    }


def test_graph_uses_the_core_mask_crop() -> None:
    prompt = SINGLE.load_prompt()
    assert prompt["background_model"] == {
        "class_type": "LoadBackgroundRemovalModel",
        "inputs": {"bg_removal_name": "birefnet.safetensors"},
        "_meta": {"title": "Load the foreground extraction model"},
    }
    assert prompt["preprocess"] == {
        "class_type": "ImageCropToMask",
        "inputs": {
            "images": ["load_image", 0],
            "masks": ["remove_background", 0],
            "width": 1024,
            "height": 1024,
            "pad_factor": 1.0,
            "grow_mask": 0,
            "background": "#000000",
        },
        "_meta": {"title": "Crop the isolated subject for native TRELLIS.2"},
    }
    assert not {
        "InvertMask",
        "JoinImageWithAlpha",
        "Trellis2PreProcessImage",
    }.intersection(node["class_type"] for node in prompt.values())


def test_graph_uses_the_official_core_stage_contract() -> None:
    prompt = SINGLE.load_prompt()
    class_types = {node["class_type"] for node in prompt.values()}
    assert prompt["load_model"]["inputs"] == {
        "unet_name": "trellis_2_int8_convrot.safetensors",
        "weight_dtype": "default",
    }
    assert prompt["clip_vision"]["inputs"] == {
        "clip_name": "dino_v3_vit_l.safetensors"
    }
    assert prompt["shape_vae"]["inputs"] == {
        "vae_name": "trellis_2_shape_vae_bf16.safetensors"
    }
    assert prompt["texture_vae"]["inputs"] == {
        "vae_name": "trellis_2_texture_vae_bf16.safetensors"
    }
    assert prompt["decode_structure"]["inputs"]["resolution"] == "32"
    assert prompt["upsample_shape"]["inputs"]["target_resolution"] == 1024
    assert prompt["sample_structure"]["inputs"]["cfg"] == 7.5
    assert prompt["sample_shape"]["inputs"]["scheduler"] == "simple"
    assert prompt["sample_texture"]["inputs"]["cfg"] == 1.0
    assert prompt["remesh"]["inputs"]["sign_mode"] == {
        "sign_mode": "udf",
        "qef": False,
        "drop_inverted_components": False,
        "drop_enclosed_components": False,
    }
    assert prompt["decimate"]["inputs"]["target_face_count"] == 200000
    assert prompt["unwrap"]["inputs"]["resolution"] == 4096
    assert prompt["bake_texture"]["inputs"]["texture_size"] == 4096
    assert "Pixal3DConditioning" not in class_types
    assert not any(class_type.startswith("MoGe") for class_type in class_types)


def test_export_uses_standard_comfy_3d_history() -> None:
    prompt = SINGLE.load_prompt()
    assert prompt["register_output"] == {
        "class_type": "SaveGLB",
        "inputs": {
            "mesh": ["final_mesh", 0],
            "filename_prefix": "LF_Nodes/TRELLIS2/ImageToTexturedMesh/seed-42-balanced",
        },
        "_meta": {"title": "Save the GLB in durable history"},
    }
    assert prompt["render_preview"] == {
        "class_type": "RenderMesh",
        "inputs": {
            "mesh": ["final_mesh", 0],
            "mode": "auto",
            "width": 512,
            "height": 512,
            "background": "#000000",
        },
        "_meta": {"title": "Render a deterministic front preview"},
    }
    assert prompt["save_preview"]["inputs"]["images"] == ["render_preview", 0]


def test_configuration_maps_upload_seed_and_draft_profile(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    resolved = "lf-workflow-runner/sha256-object.png [input]"
    monkeypatch.setattr(
        workflow_module,
        "resolve_load_image_reference",
        lambda inputs, name: resolved
        if name == "image" and inputs[name] == [Path("C:/uploads/object.png")]
        else pytest.fail("unexpected upload resolution request"),
    )
    prompt = SINGLE.load_prompt()
    SINGLE.configure_prompt(prompt, _single_inputs(quality="draft", seed="240826"))

    assert prompt["load_image"]["inputs"]["image"] == resolved
    for node_id in ("sample_structure", "sample_shape_512", "sample_texture"):
        assert prompt[node_id]["inputs"]["seed"] == 240826
        assert prompt[node_id]["inputs"]["steps"] == 12
    assert "upsample_shape" not in prompt
    assert "sample_shape" not in prompt
    assert prompt["texture_stage"]["inputs"] == {
        "positive": ["shape_stage", 0],
        "negative": ["shape_stage", 1],
        "shape_latent": ["sample_shape_512", 0],
    }
    assert prompt["decode_shape"]["inputs"]["samples"] == ["sample_shape_512", 0]
    assert prompt["remesh"]["inputs"]["resolution"] == 512
    assert prompt["decimate"]["inputs"]["target_face_count"] == 100000
    assert prompt["unwrap"]["inputs"]["resolution"] == 2048
    assert prompt["bake_texture"]["inputs"]["texture_size"] == 2048
    assert prompt["register_output"]["inputs"]["filename_prefix"] == (
        "LF_Nodes/TRELLIS2/ImageToTexturedMesh/seed-240826-draft"
    )
    assert prompt["save_preview"]["inputs"]["filename_prefix"] == (
        "LF_Nodes/TRELLIS2/ImageToTexturedMesh/seed-240826-draft-preview"
    )
    _assert_links_resolve(prompt)


def test_required_source_fails_before_upload_staging(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        workflow_module,
        "resolve_load_image_reference",
        lambda *_args, **_kwargs: pytest.fail("missing input must not stage uploads"),
    )
    prompt = SINGLE.load_prompt()
    original = copy.deepcopy(prompt)

    with pytest.raises(InputValidationError) as error:
        SINGLE.configure_prompt(prompt, {"quality": "balanced", "seed": "42"})

    assert error.value.input_name == "image"
    assert prompt == original


@pytest.mark.parametrize(
    ("inputs", "field"),
    [
        (_single_inputs(quality="1536"), "quality"),
        (_single_inputs(seed=-1), "seed"),
        (_single_inputs(seed=MAX_SEED + 1), "seed"),
    ],
)
def test_invalid_controls_fail_before_upload_staging_or_graph_mutation(
    monkeypatch: pytest.MonkeyPatch,
    inputs: dict[str, Any],
    field: str,
) -> None:
    monkeypatch.setattr(
        workflow_module,
        "resolve_load_image_reference",
        lambda *_args, **_kwargs: pytest.fail("invalid input must not stage uploads"),
    )
    prompt = SINGLE.load_prompt()
    original = copy.deepcopy(prompt)

    with pytest.raises((InputValidationError, ValueError)) as error:
        SINGLE.configure_prompt(prompt, inputs)

    if isinstance(error.value, InputValidationError):
        assert error.value.input_name == field
    else:
        assert field in str(error.value)
    assert prompt == original


def test_download_graph_uses_visible_defaults_without_local_upload_paths() -> None:
    prompt = SINGLE.load_prompt()
    assert SINGLE.configure_download is not None
    SINGLE.configure_download(prompt, _default_values(SINGLE))
    assert prompt["load_image"]["inputs"]["image"] == "example.png"
    assert prompt["upsample_shape"]["inputs"]["target_resolution"] == 1024
    assert prompt["decimate"]["inputs"]["target_face_count"] == 200000
    assert prompt["bake_texture"]["inputs"]["texture_size"] == 4096
    _assert_links_resolve(prompt)


def _installed_model_names(category: str) -> set[str]:
    return {
        "background_removal": {"birefnet.safetensors"},
        "clip_vision": {"dino_v3_vit_l.safetensors"},
        "diffusion_models": {"trellis_2_int8_convrot.safetensors"},
        "vae": {
            "trellis_2_shape_vae_bf16.safetensors",
            "trellis_2_texture_vae_bf16.safetensors",
        },
    }.get(category, set())


def test_readiness_is_ready_when_native_nodes_and_models_are_present() -> None:
    prompt = SINGLE.load_prompt()
    node_types = {node["class_type"] for node in prompt.values()}
    scanner = WorkflowReadinessScanner(
        node_mapping_loader=lambda: {name: object() for name in node_types},
        model_filename_loader=_installed_model_names,
    )
    assert evaluate_workflow_readiness(SINGLE, scanner=scanner) == {
        "status": "ready",
        "issues": [],
    }


def test_readiness_requires_the_official_trellis_dino_encoder() -> None:
    prompt = SINGLE.load_prompt()
    node_types = {node["class_type"] for node in prompt.values()}

    def installed_with_only_the_pixal_encoder(category: str) -> set[str]:
        if category == "clip_vision":
            return {"dino_v3_L_naf_fp32.safetensors"}
        return _installed_model_names(category)

    scanner = WorkflowReadinessScanner(
        node_mapping_loader=lambda: {name: object() for name in node_types},
        model_filename_loader=installed_with_only_the_pixal_encoder,
    )
    assert evaluate_workflow_readiness(SINGLE, scanner=scanner) == {
        "status": "setup_required",
        "issues": [
            {
                "code": "model_missing",
                "message": (
                    "Required CLIP Vision model file is not installed: "
                    "dino_v3_vit_l.safetensors."
                ),
            }
        ],
    }


def test_public_copy_and_graph_are_domain_neutral() -> None:
    public = json.dumps(
        {
            "id": SINGLE.id,
            "value": SINGLE.value,
            "description": SINGLE.description,
            "category": SINGLE.category,
            "inputs": [cell.to_dict() for cell in SINGLE.inputs],
            "outputs": [cell.to_dict() for cell in SINGLE.outputs],
        },
        ensure_ascii=False,
    ).casefold()
    public += SINGLE.workflow_path.read_text(encoding="utf-8").casefold()

    for forbidden in (
        "velora",
        "stellaris",
        "azeroth",
        "sentinel",
        "kaldorei",
        "portrait foundry",
        "tripo",
        "trellis-image-large",
    ):
        assert forbidden not in public
