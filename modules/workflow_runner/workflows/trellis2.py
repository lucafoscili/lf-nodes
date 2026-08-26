"""Generic local TRELLIS.2 image-to-textured-mesh workflows.

The cards deliberately expose a small, bounded profile instead of every
wrapper knob.  Both profiles keep the official 4B model on its documented
pipeline and release the wrapper-managed model after each run so another
Comfy pipeline can reclaim the GPU cleanly.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable

from ..services.registry import WorkflowCell, WorkflowModelAsset, WorkflowNode
from .utils import (
    choice,
    has_input_value,
    integer,
    require_input_value,
    resolve_load_image_reference,
)


_MAX_SEED = 0x7FFFFFFF
_SINGLE_GRAPH = Path(__file__).resolve().parent / "trellis2_image_to_textured_mesh.json"
_MULTIVIEW_GRAPH = (
    Path(__file__).resolve().parent / "trellis2_multiview_to_textured_mesh.json"
)

_QUALITY_OPTIONS = (
    (
        "balanced",
        "Balanced 1024 cascade (Recommended)",
        "The established 24 GB profile: 1024 cascade reconstruction, a 200k-face mesh, and 4K textures.",
    ),
    (
        "draft",
        "Draft 512",
        "A lighter 512 reconstruction with a 100k-face mesh and 2K textures for quicker iteration.",
    ),
)
_QUALITY_IDS = tuple(option[0] for option in _QUALITY_OPTIONS)
_QUALITY_SETTINGS: dict[str, dict[str, Any]] = {
    "balanced": {
        "pipeline_type": "1024_cascade",
        "steps": 12,
        "target_face_num": 200_000,
        "texture_size": 4096,
        "dual_contouring_resolution": "1024",
    },
    "draft": {
        "pipeline_type": "512",
        "steps": 12,
        "target_face_num": 100_000,
        "texture_size": 2048,
        "dual_contouring_resolution": "512",
    },
}

_VIEW_BRANCHES = {
    "front_image": ("load_front", "remove_front", "invert_front", "alpha_front", "preprocess_front"),
    "back_image": ("load_back", "remove_back", "invert_back", "alpha_back", "preprocess_back"),
    "left_image": ("load_left", "remove_left", "invert_left", "alpha_left", "preprocess_left"),
    "right_image": ("load_right", "remove_right", "invert_right", "alpha_right", "preprocess_right"),
}

_MODEL_ASSETS = (
    WorkflowModelAsset(
        label="official TRELLIS.2 4B model package",
        relative_paths=(
            "microsoft/TRELLIS.2-4B/pipeline.json",
            "microsoft/TRELLIS.2-4B/ckpts/ss_flow_img_dit_1_3B_64_bf16.json",
            "microsoft/TRELLIS.2-4B/ckpts/ss_flow_img_dit_1_3B_64_bf16.safetensors",
            "microsoft/TRELLIS.2-4B/ckpts/shape_dec_next_dc_f16c32_fp16.json",
            "microsoft/TRELLIS.2-4B/ckpts/shape_dec_next_dc_f16c32_fp16.safetensors",
            "microsoft/TRELLIS.2-4B/ckpts/slat_flow_img2shape_dit_1_3B_512_bf16.json",
            "microsoft/TRELLIS.2-4B/ckpts/slat_flow_img2shape_dit_1_3B_512_bf16.safetensors",
            "microsoft/TRELLIS.2-4B/ckpts/slat_flow_img2shape_dit_1_3B_1024_bf16.json",
            "microsoft/TRELLIS.2-4B/ckpts/slat_flow_img2shape_dit_1_3B_1024_bf16.safetensors",
            "microsoft/TRELLIS.2-4B/ckpts/tex_dec_next_dc_f16c32_fp16.json",
            "microsoft/TRELLIS.2-4B/ckpts/tex_dec_next_dc_f16c32_fp16.safetensors",
            "microsoft/TRELLIS.2-4B/ckpts/slat_flow_imgshape2tex_dit_1_3B_512_bf16.json",
            "microsoft/TRELLIS.2-4B/ckpts/slat_flow_imgshape2tex_dit_1_3B_512_bf16.safetensors",
            "microsoft/TRELLIS.2-4B/ckpts/slat_flow_imgshape2tex_dit_1_3B_1024_bf16.json",
            "microsoft/TRELLIS.2-4B/ckpts/slat_flow_imgshape2tex_dit_1_3B_1024_bf16.safetensors",
        ),
    ),
    WorkflowModelAsset(
        label="DINOv3 image encoder",
        relative_paths=(
            "facebook/dinov3-vitl16-pretrain-lvd1689m/config.json",
            "facebook/dinov3-vitl16-pretrain-lvd1689m/model.safetensors",
        ),
    ),
    WorkflowModelAsset(
        label="TRELLIS sparse-structure decoder package",
        relative_paths=(
            "microsoft/TRELLIS-image-large/ckpts/ss_dec_conv3d_16l8_fp16.json",
            "microsoft/TRELLIS-image-large/ckpts/ss_dec_conv3d_16l8_fp16.safetensors",
        ),
    ),
)


def _validate_settings(inputs: Dict[str, Any]) -> tuple[str, int]:
    quality = choice(inputs, "quality", "balanced", _QUALITY_IDS)
    seed = integer(inputs, "seed", 42, minimum=0, maximum=_MAX_SEED)
    return quality, seed


def _apply_profile(prompt: Dict[str, Any], quality: str, seed: int) -> None:
    profile = _QUALITY_SETTINGS[quality]
    generator = prompt["generate"]["inputs"]
    generator.update(
        {
            "seed": seed,
            "pipeline_type": profile["pipeline_type"],
            "sparse_structure_steps": profile["steps"],
            "shape_steps": profile["steps"],
            "texture_steps": profile["steps"],
        }
    )
    prompt["postprocess"]["inputs"].update(
        {
            "target_face_num": profile["target_face_num"],
            "texture_size": profile["texture_size"],
            "dual_contouring_resolution": profile["dual_contouring_resolution"],
        }
    )


def _apply_output_prefix(
    prompt: Dict[str, Any], *, workflow_name: str, quality: str, seed: int
) -> None:
    prefix = f"LF_Nodes/TRELLIS2/{workflow_name}/seed-{seed}-{quality}"
    prompt["export"]["inputs"]["filename_prefix"] = prefix
    prompt["save_preview"]["inputs"]["filename_prefix"] = f"{prefix}-preview"


def _configure_single(
    prompt: Dict[str, Any], inputs: Dict[str, Any], *, resolve_upload: bool
) -> None:
    quality, seed = _validate_settings(inputs)
    if resolve_upload:
        require_input_value(inputs, "image")
        image_reference = resolve_load_image_reference(inputs, "image")
    else:
        image_reference = "example.png"

    prompt["load_image"]["inputs"]["image"] = image_reference
    _apply_profile(prompt, quality, seed)
    _apply_output_prefix(
        prompt,
        workflow_name="ImageToTexturedMesh",
        quality=quality,
        seed=seed,
    )


def _configure_single_run(prompt: Dict[str, Any], inputs: Dict[str, Any]) -> None:
    _configure_single(prompt, inputs, resolve_upload=True)


def _configure_single_download(prompt: Dict[str, Any], inputs: Dict[str, Any]) -> None:
    _configure_single(prompt, inputs, resolve_upload=False)


def _remove_view_branch(
    prompt: Dict[str, Any], field_id: str, branch: Iterable[str]
) -> None:
    for node_id in branch:
        prompt.pop(node_id, None)
    prompt["generate"]["inputs"].pop(field_id, None)


def _configure_multiview(
    prompt: Dict[str, Any], inputs: Dict[str, Any], *, resolve_upload: bool
) -> None:
    quality, seed = _validate_settings(inputs)
    if resolve_upload:
        require_input_value(inputs, "front_image")
        present_fields = [
            field_id for field_id in _VIEW_BRANCHES if has_input_value(inputs, field_id)
        ]
        resolved = {
            field_id: resolve_load_image_reference(inputs, field_id)
            for field_id in present_fields
        }
    else:
        present_fields = ["front_image"]
        resolved = {"front_image": "example-front.png"}

    for field_id, branch in _VIEW_BRANCHES.items():
        if field_id not in resolved:
            _remove_view_branch(prompt, field_id, branch)
            continue
        load_id = branch[0]
        prompt[load_id]["inputs"]["image"] = resolved[field_id]

    _apply_profile(prompt, quality, seed)
    _apply_output_prefix(
        prompt,
        workflow_name="MultiViewToTexturedMesh",
        quality=quality,
        seed=seed,
    )


def _configure_multiview_run(prompt: Dict[str, Any], inputs: Dict[str, Any]) -> None:
    _configure_multiview(prompt, inputs, resolve_upload=True)


def _configure_multiview_download(
    prompt: Dict[str, Any], inputs: Dict[str, Any]
) -> None:
    _configure_multiview(prompt, inputs, resolve_upload=False)


def _upload_cell(
    *, field_id: str, node_id: str, label: str, description: str, required: bool = True
) -> WorkflowCell:
    return WorkflowCell(
        node_id=node_id,
        id=field_id,
        value=label,
        shape="upload",
        description=description,
        props={
            "lfHtmlAttributes": {"accept": "image/*"},
            "lfLabel": label,
        },
        required=required,
    )


def _quality_cell() -> WorkflowCell:
    description = (
        "Choose a bounded local reconstruction profile. Balanced is the established "
        "24 GB starting point; Draft reduces spatial detail, polygon count, and texture size."
    )
    return WorkflowCell(
        node_id="generate",
        id="quality",
        value="Quality",
        shape="select",
        description=description,
        props={
            "lfDataset": {
                "nodes": [
                    {
                        "description": option_help,
                        "id": option_id,
                        "value": option_label,
                        "workflowValue": option_id,
                    }
                    for option_id, option_label, option_help in _QUALITY_OPTIONS
                ]
            },
            "lfTextfieldProps": {
                "lfHelper": {"showWhenFocused": False, "value": description},
                "lfLabel": "Quality",
            },
            "lfValue": "balanced",
        },
    )


def _seed_cell() -> WorkflowCell:
    description = (
        "Controls reconstruction variation. Reuse the same source views, profile, and "
        "seed for a controlled comparison."
    )
    return WorkflowCell(
        node_id="generate",
        id="seed",
        value="Seed",
        shape="textfield",
        description=description,
        props={
            "lfHtmlAttributes": {
                "autocomplete": "off",
                "max": _MAX_SEED,
                "min": 0,
                "name": "seed",
                "step": 1,
                "type": "number",
            },
            "lfLabel": "Seed",
            "lfHelper": {"showWhenFocused": False, "value": description},
            "lfValue": "42",
        },
    )


def _mesh_output() -> WorkflowCell:
    return WorkflowCell(
        node_id="register_output",
        id="mesh",
        shape="code",
        description=(
            "The saved GLB textured mesh. Textures are embedded; transparency may need "
            "to be enabled explicitly in the destination material."
        ),
    )


def _preview_output() -> WorkflowCell:
    return WorkflowCell(
        node_id="save_preview",
        id="preview",
        shape="masonry",
        description=(
            "A durable 512px front render of the generated textured mesh for quick "
            "inspection in Runner history."
        ),
    )


_SINGLE_INPUTS = [
    _upload_cell(
        field_id="image",
        node_id="load_image",
        label="Source image",
        description=(
            "Upload one clear view of a complete subject. A simple background and visible "
            "silhouette improve reconstruction; surfaces hidden from the camera are inferred."
        ),
    ),
    _quality_cell(),
    _seed_cell(),
]

_MULTIVIEW_INPUTS = [
    _upload_cell(
        field_id="front_image",
        node_id="load_front",
        label="Front view",
        description=(
            "Required front-facing view. Keep scale, lighting, subject state, and framing "
            "consistent with every additional view."
        ),
    ),
    _upload_cell(
        field_id="back_image",
        node_id="load_back",
        label="Back view",
        description="Optional rear view of the same subject in the same state and framing.",
        required=False,
    ),
    _upload_cell(
        field_id="left_image",
        node_id="load_left",
        label="Left view",
        description="Optional left-side view of the same subject in the same state and framing.",
        required=False,
    ),
    _upload_cell(
        field_id="right_image",
        node_id="load_right",
        label="Right view",
        description="Optional right-side view of the same subject in the same state and framing.",
        required=False,
    ),
    _quality_cell(),
    _seed_cell(),
]

_REQUIREMENTS_COPY = (
    "Requires the local TRELLIS.2 wrapper, its matching native CUDA extensions, the "
    "official 4B model, DINOv3 weights, and the Core BiRefNet background-removal model. "
    "The third-party wrapper can download several gigabytes when its assets are missing; "
    "LF Nodes never starts those downloads and keeps this card at Setup required until "
    "its declared local files are present."
)

WORKFLOWS = (
    WorkflowNode(
        id="trellis2_image_to_textured_mesh",
        value="Image to Textured Mesh",
        description=(
            "Reconstruct one isolated subject as a locally generated PBR-textured GLB. "
            "Hidden surfaces are inferred, so the result is a presentation mesh rather "
            "than a guaranteed watertight, manifold, rig-ready, or game-ready asset. "
            f"{_REQUIREMENTS_COPY}"
        ),
        category="TRELLIS.2",
        inputs=_SINGLE_INPUTS,
        outputs=[_preview_output(), _mesh_output()],
        configure_prompt=_configure_single_run,
        configure_download=_configure_single_download,
        workflow_path=_SINGLE_GRAPH,
        required_model_assets=_MODEL_ASSETS,
    ),
    WorkflowNode(
        id="trellis2_multiview_to_textured_mesh",
        value="Multi-view to Textured Mesh",
        description=(
            "Reconstruct one subject from an explicit front view plus optional rear and "
            "side views, then export a PBR-textured GLB. Additional views constrain hidden "
            "surfaces but do not guarantee a watertight, manifold, rig-ready, or game-ready "
            f"asset. {_REQUIREMENTS_COPY}"
        ),
        category="TRELLIS.2",
        inputs=_MULTIVIEW_INPUTS,
        outputs=[_preview_output(), _mesh_output()],
        configure_prompt=_configure_multiview_run,
        configure_download=_configure_multiview_download,
        workflow_path=_MULTIVIEW_GRAPH,
        required_model_assets=_MODEL_ASSETS,
    ),
)

__all__ = ["WORKFLOWS"]
