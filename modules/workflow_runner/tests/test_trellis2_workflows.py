"""Offline contracts for the generic TRELLIS.2 Runner workflows."""

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

from modules.workflow_runner.services.readiness import (
    WorkflowReadinessScanner,
    evaluate_workflow_readiness,
)
from modules.workflow_runner.services.registry import InputValidationError
from modules.workflow_runner.workflows import _WORKFLOW_MODULES
from modules.workflow_runner.workflows import trellis2 as workflow_module


SINGLE, MULTIVIEW = workflow_module.WORKFLOWS
MAX_SEED = 0x7FFFFFFF
DECLARED_MODEL_PATHS = {
    path
    for asset in SINGLE.required_model_assets
    for path in asset.relative_paths
}
EXPECTED_MODEL_PATHS = {
    "microsoft/TRELLIS.2-4B/pipeline.json",
    "facebook/dinov3-vitl16-pretrain-lvd1689m/config.json",
    "facebook/dinov3-vitl16-pretrain-lvd1689m/model.safetensors",
    "microsoft/TRELLIS-image-large/ckpts/ss_dec_conv3d_16l8_fp16.json",
    "microsoft/TRELLIS-image-large/ckpts/ss_dec_conv3d_16l8_fp16.safetensors",
    *{
        f"microsoft/TRELLIS.2-4B/ckpts/{stem}.{extension}"
        for stem in (
            "ss_flow_img_dit_1_3B_64_bf16",
            "shape_dec_next_dc_f16c32_fp16",
            "slat_flow_img2shape_dit_1_3B_512_bf16",
            "slat_flow_img2shape_dit_1_3B_1024_bf16",
            "tex_dec_next_dc_f16c32_fp16",
            "slat_flow_imgshape2tex_dit_1_3B_512_bf16",
            "slat_flow_imgshape2tex_dit_1_3B_1024_bf16",
        )
        for extension in ("json", "safetensors")
    },
}


def _single_inputs(**overrides: Any) -> dict[str, Any]:
    return {
        "image": [Path("C:/uploads/object.png")],
        "quality": "balanced",
        "seed": "42",
        **overrides,
    }


def _multiview_inputs(**overrides: Any) -> dict[str, Any]:
    return {
        "front_image": [Path("C:/uploads/front.png")],
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


def test_declarations_are_two_small_generic_mesh_cards() -> None:
    assert [workflow.id for workflow in workflow_module.WORKFLOWS] == [
        "trellis2_image_to_textured_mesh",
        "trellis2_multiview_to_textured_mesh",
    ]
    assert [workflow.value for workflow in workflow_module.WORKFLOWS] == [
        "Image to Textured Mesh",
        "Multi-view to Textured Mesh",
    ]
    assert {workflow.category for workflow in workflow_module.WORKFLOWS} == {
        "TRELLIS.2"
    }
    assert [cell.id for cell in SINGLE.inputs] == ["image", "quality", "seed"]
    assert [cell.id for cell in MULTIVIEW.inputs] == [
        "front_image",
        "back_image",
        "left_image",
        "right_image",
        "quality",
        "seed",
    ]
    assert [cell.required for cell in MULTIVIEW.inputs[:4]] == [
        True,
        False,
        False,
        False,
    ]
    assert all(cell.shape == "upload" for cell in MULTIVIEW.inputs[:4])
    assert all(
        [(cell.node_id, cell.id, cell.shape) for cell in workflow.outputs]
        == [
            ("save_preview", "preview", "masonry"),
            ("register_output", "mesh", "code"),
        ]
        for workflow in workflow_module.WORKFLOWS
    )
    assert all(
        cell.description
        for workflow in workflow_module.WORKFLOWS
        for cell in (*workflow.inputs, *workflow.outputs)
    )
    assert all("watertight" in workflow.description for workflow in workflow_module.WORKFLOWS)
    assert "trellis2" in _WORKFLOW_MODULES


def test_quality_select_exposes_only_bounded_24_gb_profiles() -> None:
    for workflow in workflow_module.WORKFLOWS:
        cell = next(cell for cell in workflow.inputs if cell.id == "quality")
        assert cell.props["lfValue"] == "balanced"
        assert [
            option["workflowValue"] for option in cell.props["lfDataset"]["nodes"]
        ] == ["balanced", "draft"]

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


@pytest.mark.parametrize("workflow", workflow_module.WORKFLOWS)
def test_graph_uses_explicit_core_cutout_and_never_calls_wrapper_rembg(
    workflow: Any,
) -> None:
    prompt = workflow.load_prompt()

    assert prompt["background_model"] == {
        "class_type": "LoadBackgroundRemovalModel",
        "inputs": {"bg_removal_name": "birefnet.safetensors"},
        "_meta": {"title": "Load the foreground extraction model"},
    }
    preprocess_nodes = [
        node
        for node in prompt.values()
        if node["class_type"] == "Trellis2PreProcessImage"
    ]
    assert preprocess_nodes
    assert all(
        node["inputs"]["remove_background"] is False for node in preprocess_nodes
    )
    assert all(node["inputs"]["padding"] == 0 for node in preprocess_nodes)
    assert all(node["inputs"]["max_size"] == 2048 for node in preprocess_nodes)

    invert_nodes = {
        node_id
        for node_id, node in prompt.items()
        if node["class_type"] == "InvertMask"
    }
    for node in prompt.values():
        if node["class_type"] == "JoinImageWithAlpha":
            assert node["inputs"]["alpha"][0] in invert_nodes


@pytest.mark.parametrize("workflow", workflow_module.WORKFLOWS)
def test_graph_fixes_the_safe_loader_and_postprocess_contract(workflow: Any) -> None:
    prompt = workflow.load_prompt()

    assert prompt["load_model"]["inputs"] == {
        "modelname": "microsoft/TRELLIS.2-4B",
        "backend": "sdpa",
        "device": "cuda",
        "low_vram": True,
        "keep_models_loaded": False,
        "conv_backend": "flex_gemm",
        "sparse_backend": "xformers",
        "use_reconviagen": False,
    }
    assert prompt["generate"]["inputs"]["max_num_tokens"] == 49152
    assert prompt["generate"]["inputs"]["sparse_structure_resolution"] == 32
    assert prompt["generate"]["inputs"]["use_tiled_decoder"] is True
    assert prompt["generate"]["inputs"]["sampler"] == "euler"
    assert prompt["postprocess"]["inputs"]["simplify_method"] == "Cumesh"
    assert prompt["postprocess"]["inputs"]["texture_alpha_mode"] == "OPAQUE"
    assert prompt["postprocess"]["inputs"]["target_face_num"] == 200000
    assert prompt["postprocess"]["inputs"]["texture_size"] == 4096


@pytest.mark.parametrize("workflow", workflow_module.WORKFLOWS)
def test_export_is_glb_and_registered_from_the_relative_path(workflow: Any) -> None:
    prompt = workflow.load_prompt()

    assert prompt["export"]["class_type"] == "Trellis2ExportMesh"
    assert prompt["export"]["inputs"]["file_format"] == "glb"
    assert prompt["register_output"] == {
        "class_type": "LF_RegisterOutputFile",
        "inputs": {
            "relative_path": ["export", 1],
            "ui_widget": {},
        },
        "_meta": {"title": "Register the GLB in durable history"},
    }
    assert prompt["render_preview"] == {
        "class_type": "Trellis2RenderMultiViewNvdiffrast",
        "inputs": {
            "trimesh": ["postprocess", 0],
            "render_size": 512,
            "ortho_scale": 1.2,
            "azimuths": "0",
            "elevations": "0",
            "add_shading": True,
        },
        "_meta": {"title": "Render a deterministic front preview"},
    }
    assert prompt["save_preview"]["class_type"] == "SaveImage"
    assert prompt["save_preview"]["inputs"]["images"] == ["render_preview", 0]


def test_multiview_graph_uses_the_proven_guidance_profile() -> None:
    generator = MULTIVIEW.load_prompt()["generate"]

    assert generator["class_type"] == "Trellis2MeshWithVoxelMultiViewGenerator"
    assert generator["inputs"] == {
        "pipeline": ["load_model", 0],
        "front_image": ["preprocess_front", 0],
        "back_image": ["preprocess_back", 0],
        "left_image": ["preprocess_left", 0],
        "right_image": ["preprocess_right", 0],
        "seed": 42,
        "pipeline_type": "1024_cascade",
        "sparse_structure_steps": 12,
        "sparse_structure_guidance_strength": 6.5,
        "sparse_structure_guidance_rescale": 0.05,
        "sparse_structure_rescale_t": 4.0,
        "shape_steps": 12,
        "shape_guidance_strength": 6.5,
        "shape_guidance_rescale": 0.05,
        "shape_rescale_t": 4.0,
        "texture_steps": 12,
        "texture_guidance_strength": 3.0,
        "texture_guidance_rescale": 0.2,
        "texture_rescale_t": 3.0,
        "max_num_tokens": 49152,
        "sparse_structure_resolution": 32,
        "generate_texture_slat": True,
        "sparse_structure_guidance_interval_start": 0.1,
        "sparse_structure_guidance_interval_end": 1.0,
        "shape_guidance_interval_start": 0.1,
        "shape_guidance_interval_end": 1.0,
        "texture_guidance_interval_start": 0.0,
        "texture_guidance_interval_end": 0.9,
        "use_tiled_decoder": True,
        "front_axis": "z",
        "blend_temperature": 1.0,
        "sampler": "euler",
        "fill_holes": True,
        "hole_iterations": 1,
        "verbose": False,
        "dino_lock": 0.0,
        "dino_substeps": 4,
        "hole_fill_algorithm": "flood_fill",
        "dino_foundation_cap": 1.0,
        "keep_only_shell": True,
    }


def test_single_configuration_maps_upload_seed_and_draft_profile(
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

    SINGLE.configure_prompt(
        prompt,
        _single_inputs(quality="draft", seed="240826"),
    )

    assert prompt["load_image"]["inputs"]["image"] == resolved
    assert prompt["generate"]["inputs"]["seed"] == 240826
    assert prompt["generate"]["inputs"]["pipeline_type"] == "512"
    assert prompt["generate"]["inputs"]["sparse_structure_steps"] == 12
    assert prompt["postprocess"]["inputs"]["target_face_num"] == 100000
    assert prompt["postprocess"]["inputs"]["texture_size"] == 2048
    assert prompt["postprocess"]["inputs"]["dual_contouring_resolution"] == "512"
    assert prompt["export"]["inputs"]["filename_prefix"] == (
        "LF_Nodes/TRELLIS2/ImageToTexturedMesh/seed-240826-draft"
    )
    assert prompt["save_preview"]["inputs"]["filename_prefix"] == (
        "LF_Nodes/TRELLIS2/ImageToTexturedMesh/seed-240826-draft-preview"
    )


def test_multiview_configuration_keeps_only_uploaded_orientation_branches(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []

    def resolve(inputs: dict[str, Any], name: str) -> str:
        calls.append(name)
        assert inputs[name]
        return f"lf-workflow-runner/{name}.png [input]"

    monkeypatch.setattr(workflow_module, "resolve_load_image_reference", resolve)
    prompt = MULTIVIEW.load_prompt()

    MULTIVIEW.configure_prompt(
        prompt,
        _multiview_inputs(
            left_image=[Path("C:/uploads/left.png")],
            quality="draft",
            seed="7",
        ),
    )

    assert calls == ["front_image", "left_image"]
    assert prompt["load_front"]["inputs"]["image"].endswith("front_image.png [input]")
    assert prompt["load_left"]["inputs"]["image"].endswith("left_image.png [input]")
    for node_id in (
        "load_back",
        "remove_back",
        "invert_back",
        "alpha_back",
        "preprocess_back",
        "load_right",
        "remove_right",
        "invert_right",
        "alpha_right",
        "preprocess_right",
    ):
        assert node_id not in prompt
    assert set(prompt["generate"]["inputs"]) >= {"front_image", "left_image"}
    assert "back_image" not in prompt["generate"]["inputs"]
    assert "right_image" not in prompt["generate"]["inputs"]
    assert prompt["generate"]["inputs"]["pipeline_type"] == "512"
    assert prompt["generate"]["inputs"]["seed"] == 7
    _assert_links_resolve(prompt)


@pytest.mark.parametrize(
    ("workflow", "inputs", "missing_field"),
    [
        (SINGLE, {"quality": "balanced", "seed": "42"}, "image"),
        (MULTIVIEW, {"quality": "balanced", "seed": "42"}, "front_image"),
    ],
)
def test_required_source_fails_before_upload_staging(
    monkeypatch: pytest.MonkeyPatch,
    workflow: Any,
    inputs: dict[str, Any],
    missing_field: str,
) -> None:
    monkeypatch.setattr(
        workflow_module,
        "resolve_load_image_reference",
        lambda *_args, **_kwargs: pytest.fail("missing input must not stage uploads"),
    )
    prompt = workflow.load_prompt()
    original = copy.deepcopy(prompt)

    with pytest.raises(InputValidationError) as error:
        workflow.configure_prompt(prompt, inputs)

    assert error.value.input_name == missing_field
    assert prompt == original


@pytest.mark.parametrize(
    ("workflow", "inputs", "field"),
    [
        (SINGLE, _single_inputs(quality="1536"), "quality"),
        (SINGLE, _single_inputs(seed=-1), "seed"),
        (MULTIVIEW, _multiview_inputs(quality="hq"), "quality"),
        (MULTIVIEW, _multiview_inputs(seed=MAX_SEED + 1), "seed"),
    ],
)
def test_invalid_controls_fail_before_upload_staging_or_graph_mutation(
    monkeypatch: pytest.MonkeyPatch,
    workflow: Any,
    inputs: dict[str, Any],
    field: str,
) -> None:
    monkeypatch.setattr(
        workflow_module,
        "resolve_load_image_reference",
        lambda *_args, **_kwargs: pytest.fail("invalid input must not stage uploads"),
    )
    prompt = workflow.load_prompt()
    original = copy.deepcopy(prompt)

    with pytest.raises((InputValidationError, ValueError)) as error:
        workflow.configure_prompt(prompt, inputs)

    if isinstance(error.value, InputValidationError):
        assert error.value.input_name == field
    else:
        assert field in str(error.value)
    assert prompt == original


def test_download_graphs_use_visible_defaults_without_local_upload_paths() -> None:
    single_prompt = SINGLE.load_prompt()
    assert SINGLE.configure_download is not None
    SINGLE.configure_download(single_prompt, _default_values(SINGLE))
    assert single_prompt["load_image"]["inputs"]["image"] == "example.png"
    assert single_prompt["generate"]["inputs"]["pipeline_type"] == "1024_cascade"

    multiview_prompt = MULTIVIEW.load_prompt()
    assert MULTIVIEW.configure_download is not None
    MULTIVIEW.configure_download(multiview_prompt, _default_values(MULTIVIEW))
    assert multiview_prompt["load_front"]["inputs"]["image"] == "example-front.png"
    assert "load_back" not in multiview_prompt
    assert "load_left" not in multiview_prompt
    assert "load_right" not in multiview_prompt
    assert set(
        key
        for key in multiview_prompt["generate"]["inputs"]
        if key.endswith("_image")
    ) == {"front_image"}
    _assert_links_resolve(multiview_prompt)


def test_declares_every_local_model_file_used_by_both_profiles() -> None:
    assert DECLARED_MODEL_PATHS == EXPECTED_MODEL_PATHS
    assert SINGLE.required_model_assets == MULTIVIEW.required_model_assets


def test_readiness_reports_wrapper_and_birefnet_setup_failures() -> None:
    core_and_lf_nodes = {
        "InvertMask",
        "JoinImageWithAlpha",
        "LF_RegisterOutputFile",
        "LoadBackgroundRemovalModel",
        "LoadImage",
        "RemoveBackground",
        "SaveImage",
    }
    scanner = WorkflowReadinessScanner(
        node_mapping_loader=lambda: {name: object() for name in core_and_lf_nodes},
        model_filename_loader=lambda _category: (),
        model_file_exists_loader=lambda path: path in DECLARED_MODEL_PATHS,
    )

    result = evaluate_workflow_readiness(SINGLE, scanner=scanner)

    assert result["status"] == "setup_required"
    assert any(
        issue == {
            "code": "model_missing",
            "message": (
                "Required background-removal model file is not installed: "
                "birefnet.safetensors."
            ),
        }
        for issue in result["issues"]
    )
    missing_types = {
        issue["message"].removeprefix("Required node type is not installed: ").removesuffix(".")
        for issue in result["issues"]
        if issue["code"] == "node_missing"
    }
    assert missing_types == {
        "Trellis2ExportMesh",
        "Trellis2LoadModel",
        "Trellis2MeshWithVoxelGenerator",
        "Trellis2PostProcessAndUnWrapAndRasterizer",
        "Trellis2PreProcessImage",
        "Trellis2RenderMultiViewNvdiffrast",
    }


@pytest.mark.parametrize("workflow", workflow_module.WORKFLOWS)
def test_readiness_is_ready_when_declared_nodes_and_birefnet_are_present(
    workflow: Any,
) -> None:
    prompt = workflow.load_prompt()
    node_types = {node["class_type"] for node in prompt.values()}
    scanner = WorkflowReadinessScanner(
        node_mapping_loader=lambda: {name: object() for name in node_types},
        model_filename_loader=lambda category: (
            {"birefnet.safetensors"} if category == "background_removal" else ()
        ),
        model_file_exists_loader=lambda path: path in DECLARED_MODEL_PATHS,
    )

    assert evaluate_workflow_readiness(workflow, scanner=scanner) == {
        "status": "ready",
        "issues": [],
    }


@pytest.mark.parametrize("workflow", workflow_module.WORKFLOWS)
def test_readiness_blocks_an_incomplete_declared_model_asset(workflow: Any) -> None:
    prompt = workflow.load_prompt()
    node_types = {node["class_type"] for node in prompt.values()}
    missing_path = "facebook/dinov3-vitl16-pretrain-lvd1689m/model.safetensors"
    scanner = WorkflowReadinessScanner(
        node_mapping_loader=lambda: {name: object() for name in node_types},
        model_filename_loader=lambda category: (
            {"birefnet.safetensors"} if category == "background_removal" else ()
        ),
        model_file_exists_loader=lambda path: (
            path in DECLARED_MODEL_PATHS and path != missing_path
        ),
    )

    assert evaluate_workflow_readiness(workflow, scanner=scanner) == {
        "status": "setup_required",
        "issues": [
            {
                "code": "model_asset_missing",
                "message": (
                    "Required local model asset is incomplete: DINOv3 image encoder "
                    f"(missing {missing_path})."
                ),
            }
        ],
    }


def test_public_copy_and_graphs_are_domain_neutral() -> None:
    public = ""
    for workflow in workflow_module.WORKFLOWS:
        public += json.dumps(
            {
                "id": workflow.id,
                "value": workflow.value,
                "description": workflow.description,
                "category": workflow.category,
                "inputs": [cell.to_dict() for cell in workflow.inputs],
                "outputs": [cell.to_dict() for cell in workflow.outputs],
            },
            ensure_ascii=False,
        ).casefold()
        public += workflow.workflow_path.read_text(encoding="utf-8").casefold()

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
