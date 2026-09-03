"""Generic local TRELLIS.2 image-to-textured-mesh workflow."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from ..services.registry import (
    WorkflowCardPresentation,
    WorkflowCell,
    WorkflowHeroImage,
    WorkflowNode,
)
from .utils import (
    choice,
    integer,
    require_input_value,
    resolve_load_image_reference,
)


_MAX_SEED = 0x7FFFFFFF
_SINGLE_GRAPH = Path(__file__).resolve().parent / "trellis2_image_to_textured_mesh.json"

_QUALITY_OPTIONS = (
    (
        "draft",
        "Fast · 512",
        "Reconstructs at 512 with 100k faces and 2K textures. Faster, but loses fine geometry.",
        "fast",
    ),
    (
        "balanced",
        "Baseline · 1024",
        "Reconstructs at 1024 with 200k faces and 4K textures. Slower, but keeps more geometry.",
        "baseline",
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

def _validate_settings(inputs: Dict[str, Any]) -> tuple[str, int]:
    quality = choice(inputs, "quality", "balanced", _QUALITY_IDS)
    seed = integer(inputs, "seed", 42, minimum=0, maximum=_MAX_SEED)
    return quality, seed


def _apply_native_profile(prompt: Dict[str, Any], quality: str, seed: int) -> None:
    profile = _QUALITY_SETTINGS[quality]
    for node_id in (
        "sample_structure",
        "sample_shape_512",
        "sample_shape",
        "sample_texture",
    ):
        prompt[node_id]["inputs"].update({"seed": seed, "steps": profile["steps"]})

    prompt["remesh"]["inputs"]["resolution"] = int(
        profile["dual_contouring_resolution"]
    )
    prompt["decimate"]["inputs"]["target_face_count"] = profile["target_face_num"]
    prompt["unwrap"]["inputs"]["resolution"] = profile["texture_size"]
    prompt["bake_texture"]["inputs"]["texture_size"] = profile["texture_size"]

    if profile["pipeline_type"] == "1024_cascade":
        prompt["upsample_shape"]["inputs"]["target_resolution"] = 1024
        return

    prompt.pop("upsample_shape")
    prompt.pop("sample_shape")
    prompt["texture_stage"]["inputs"].update(
        {
            "positive": ["shape_stage", 0],
            "negative": ["shape_stage", 1],
            "shape_latent": ["sample_shape_512", 0],
        }
    )
    prompt["decode_shape"]["inputs"]["samples"] = ["sample_shape_512", 0]


def _apply_native_output_prefix(
    prompt: Dict[str, Any], *, workflow_name: str, quality: str, seed: int
) -> None:
    prefix = f"LF_Nodes/TRELLIS2/{workflow_name}/seed-{seed}-{quality}"
    prompt["register_output"]["inputs"]["filename_prefix"] = prefix
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
    _apply_native_profile(prompt, quality, seed)
    _apply_native_output_prefix(
        prompt,
        workflow_name="ImageToTexturedMesh",
        quality=quality,
        seed=seed,
    )


def _configure_single_run(prompt: Dict[str, Any], inputs: Dict[str, Any]) -> None:
    _configure_single(prompt, inputs, resolve_upload=True)


def _configure_single_download(prompt: Dict[str, Any], inputs: Dict[str, Any]) -> None:
    _configure_single(prompt, inputs, resolve_upload=False)


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
    description = "Controls reconstruction size, retained faces, and texture resolution."
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
                        "profileTier": profile_tier,
                        "value": option_label,
                        "workflowValue": option_id,
                    }
                    for option_id, option_label, option_help, profile_tier in _QUALITY_OPTIONS
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

_NATIVE_REQUIREMENTS_COPY = (
    "Requires ComfyUI's native TRELLIS.2 diffusion model, shape and texture VAEs, "
    "DINOv3 image encoder, and the Core BiRefNet background-removal model. LF Nodes "
    "never starts model downloads and keeps this card at Setup required until its "
    "declared local files are present."
)

WORKFLOWS = (
    WorkflowNode(
        id="trellis2_image_to_textured_mesh",
        value="Image to Textured Mesh",
        description=(
            "Reconstruct one isolated subject as a locally generated PBR-textured GLB. "
            "Hidden surfaces are inferred, so the result is a presentation mesh rather "
            "than a guaranteed watertight, manifold, rig-ready, or game-ready asset. "
            f"{_NATIVE_REQUIREMENTS_COPY}"
        ),
        category="TRELLIS.2",
        card=WorkflowCardPresentation(
            summary="Reconstruct a textured mesh from one image.",
            hero=WorkflowHeroImage(
                asset="trellis2/image-to-mesh.webp",
                alt=(
                    "Actual explorer input beside front and rear three-quarter renders "
                    "of its saved generated GLB. The imperfect rear strap remains visible."
                ),
            ),
        ),
        inputs=_SINGLE_INPUTS,
        outputs=[_preview_output(), _mesh_output()],
        configure_prompt=_configure_single_run,
        configure_download=_configure_single_download,
        workflow_path=_SINGLE_GRAPH,
    ),
)

__all__ = ["WORKFLOWS"]
