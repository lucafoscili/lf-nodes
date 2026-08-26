"""Generic local TripoSplat image-to-Gaussian workflow."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from ..services.registry import InputValidationError, WorkflowCell, WorkflowNode
from .utils import choice, integer, resolve_load_image_reference


_MAX_SEED = (1 << 53) - 1
_DENSITY_OPTIONS = (
    (
        "full",
        "Full · 262k (Recommended)",
        "Native octree density and the best default for a final Gaussian splat.",
        262144,
    ),
    (
        "balanced",
        "Balanced · 131k",
        "Half-density export for faster iteration and smaller files.",
        131072,
    ),
    (
        "light",
        "Light · 64k",
        "A lighter result for quick review or constrained downstream viewers.",
        65536,
    ),
    (
        "draft",
        "Draft · 32k",
        "The minimum supported density for a fast structural check.",
        32768,
    ),
)
_DENSITY_BY_ID = {option_id: count for option_id, _label, _help, count in _DENSITY_OPTIONS}

_EXPORT_OPTIONS = (
    (
        "spz",
        "SPZ · compact (Recommended)",
        "Compressed base-color splat for practical storage and transfer.",
    ),
    (
        "ply",
        "PLY · full spherical harmonics",
        "Highest-fidelity export from this graph, with a much larger file.",
    ),
    (
        "ksplat",
        "KSPLAT · uncompressed base color",
        "Uncompressed base-color SplatBuffer for compatible viewers.",
    ),
)
_EXPORT_IDS = tuple(option[0] for option in _EXPORT_OPTIONS)

_EDGE_OPTIONS = (
    (
        "gentle",
        "Gentle (Recommended)",
        "Erode the foreground edge by one pixel to reduce background color bleed.",
        1,
    ),
    (
        "off",
        "Off",
        "Keep the foreground mask unchanged; useful for fine transparent details.",
        0,
    ),
    (
        "strong",
        "Strong",
        "Erode by two pixels when the source has a visible background halo.",
        2,
    ),
)
_EDGE_BY_ID = {option_id: radius for option_id, _label, _help, radius in _EDGE_OPTIONS}

_GRAPH = Path(__file__).resolve().parent / "triposplat_image_to_splat.json"


def _boolean(inputs: Dict[str, Any], name: str, default: bool) -> bool:
    value = inputs.get(name, default)
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().casefold()
        if normalized in {"true", "1", "yes", "on"}:
            return True
        if normalized in {"false", "0", "no", "off"}:
            return False
    raise InputValidationError(name)


def _apply_settings(
    prompt: Dict[str, Any],
    inputs: Dict[str, Any],
    *,
    resolve_upload: bool,
) -> None:
    density_id = choice(inputs, "density", "full", _DENSITY_BY_ID)
    export_format = choice(inputs, "export_format", "spz", _EXPORT_IDS)
    edge_cleanup = choice(inputs, "edge_cleanup", "gentle", _EDGE_BY_ID)
    seed = integer(inputs, "seed", 42, minimum=0, maximum=_MAX_SEED)
    automatic_background = _boolean(inputs, "automatic_background_removal", True)

    prompt["load_image"]["inputs"]["image"] = (
        resolve_load_image_reference(inputs, "image") if resolve_upload else "example.png"
    )
    prompt["mask_source"]["inputs"]["switch"] = automatic_background
    prompt["preprocess"]["inputs"]["erode_radius"] = _EDGE_BY_ID[edge_cleanup]
    prompt["sample"]["inputs"]["seed"] = seed
    prompt["decode"]["inputs"].update(
        {
            "num_gaussians": _DENSITY_BY_ID[density_id],
            "seed": seed,
        }
    )
    prompt["splat_file"]["inputs"]["format"] = export_format

    prefix = f"LF_Nodes/TripoSplat/seed-{seed}-{density_id}"
    prompt["save_splat"]["inputs"]["filename_prefix"] = prefix
    prompt["save_preview"]["inputs"]["filename_prefix"] = f"{prefix}-preview"
    prompt["save_video"]["inputs"]["filename_prefix"] = f"{prefix}-orbit"


def _configure(prompt: Dict[str, Any], inputs: Dict[str, Any]) -> None:
    _apply_settings(prompt, inputs, resolve_upload=True)


def _configure_download(prompt: Dict[str, Any], inputs: Dict[str, Any]) -> None:
    _apply_settings(prompt, inputs, resolve_upload=False)


def _select_cell(
    input_id: str,
    node_id: str,
    label: str,
    default: str,
    description: str,
    options: tuple[tuple[str, str, str], ...],
) -> WorkflowCell:
    return WorkflowCell(
        node_id=node_id,
        id=input_id,
        value=label,
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
                    for option_id, option_label, option_help in options
                ]
            },
            "lfTextfieldProps": {
                "lfHelper": {"showWhenFocused": False, "value": description},
                "lfLabel": label,
            },
            "lfValue": default,
        },
    )


def _upload_cell() -> WorkflowCell:
    description = (
        "Upload one image containing a complete, clearly visible subject. An isolated "
        "object or stylized character against a simple background gives the most reliable "
        "shape; hidden surfaces are inferred and may differ from the source."
    )
    return WorkflowCell(
        node_id="load_image",
        id="image",
        value="Source image",
        shape="upload",
        description=description,
        props={
            "lfHtmlAttributes": {"accept": "image/*"},
            "lfLabel": "Source image",
        },
    )


def _background_cell() -> WorkflowCell:
    description = (
        "Use the installed BiRefNet model to isolate the subject. Turn this off only when "
        "the uploaded image already has a clean transparent background."
    )
    return WorkflowCell(
        node_id="mask_source",
        id="automatic_background_removal",
        value="Automatic background removal",
        shape="toggle",
        description=description,
        props={
            "lfLabel": "Automatic background removal",
            "lfValue": True,
        },
    )


def _seed_cell() -> WorkflowCell:
    description = (
        "Controls both diffusion and deterministic Gaussian point sampling. Reuse the same "
        "seed and settings for a controlled comparison."
    )
    return WorkflowCell(
        node_id="sample",
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


_density_cell_options = tuple(
    (option_id, label, description)
    for option_id, label, description, _count in _DENSITY_OPTIONS
)
_edge_cell_options = tuple(
    (option_id, label, description)
    for option_id, label, description, _radius in _EDGE_OPTIONS
)

inputs = [
    _upload_cell(),
    _background_cell(),
    _select_cell(
        "density",
        "decode",
        "Gaussian density",
        "full",
        "Choose the number of exported Gaussians. Higher density costs more memory, time, and disk space; counts above 262k do not add new model detail.",
        _density_cell_options,
    ),
    _select_cell(
        "edge_cleanup",
        "preprocess",
        "Foreground edge cleanup",
        "gentle",
        "Control how much of a background-colored halo is removed before reconstruction.",
        _edge_cell_options,
    ),
    _select_cell(
        "export_format",
        "splat_file",
        "Export format",
        "spz",
        "Choose the saved Gaussian-splat container. This changes representation and file size, not the generated geometry.",
        _EXPORT_OPTIONS,
    ),
    _seed_cell(),
]

outputs = [
    WorkflowCell(
        node_id="save_preview",
        id="preview",
        shape="masonry",
        description="A durable still preview from the generated Gaussian splat.",
    ),
    WorkflowCell(
        node_id="save_video",
        id="orbit",
        shape="code",
        description="A 1024px, three-second MP4 orbit for inspecting the result from every side.",
    ),
    WorkflowCell(
        node_id="save_splat",
        id="splat",
        shape="code",
        description="The saved SPZ, PLY, or KSPLAT 3D artifact.",
    ),
]

WORKFLOW = WorkflowNode(
    id="triposplat_image_to_splat",
    value="Image to Gaussian Splat",
    description=(
        "Reconstruct one isolated subject as a local 3D Gaussian splat and save both the "
        "asset and a full orbit preview. This produces a viewable splat, not a watertight, "
        "rig-ready, or game-ready mesh."
    ),
    category="TripoSplat",
    inputs=inputs,
    outputs=outputs,
    configure_prompt=_configure,
    configure_download=_configure_download,
    workflow_path=_GRAPH,
)

__all__ = ["WORKFLOW"]
