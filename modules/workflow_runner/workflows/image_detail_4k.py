"""A focused diffusion-restoration workflow for genuine 4K output."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from ..services.registry import WorkflowCell, WorkflowNode
from .utils import choice, integer as _integer, require_input_value as _required_image, resolve_load_image_reference


_MAX_SEED = (1 << 32) - 1
_TARGETS = {
    "uhd_3840": (3840, "UHD-3840"),
    "dci_4096": (4096, "DCI-4096"),
}


def _choice(inputs: Dict[str, Any], name: str, default: str) -> str:
    return choice(inputs, name, default, _TARGETS)


def _configure(prompt: Dict[str, Any], inputs: Dict[str, Any]) -> None:
    # Validate the complete request before staging the upload.
    _required_image(inputs, "source_path")
    target = _choice(inputs, "target_size", "uhd_3840")
    seed = _integer(inputs, "seed", 42, minimum=0, maximum=_MAX_SEED)
    source_reference = resolve_load_image_reference(inputs, "source_path")

    long_edge, folder = _TARGETS[target]
    prompt["load_image"]["inputs"]["image"] = source_reference
    prompt["detail_4k"]["inputs"].update(
        {
            "seed": seed,
            "resolution": long_edge,
            "max_resolution": long_edge,
        }
    )
    prompt["save"]["inputs"]["filename_prefix"] = (
        f"LF_Nodes/4KDetail/{folder}/seed-{seed}"
    )


def _select_cell() -> WorkflowCell:
    description = (
        "UHD uses a 3840-pixel long edge for common displays and exports. DCI uses "
        "4096 pixels for extra headroom. Aspect ratio is preserved; the other edge "
        "is calculated from the source rather than cropped or stretched."
    )
    return WorkflowCell(
        node_id="detail_4k",
        id="target_size",
        shape="select",
        value="2. Choose the 4K standard",
        description=description,
        props={
            "lfDataset": {
                "nodes": [
                    {
                        "description": (
                            "Sets the longest edge to 3840 pixels. This is the common "
                            "consumer UHD width for a 16:9 landscape image."
                        ),
                        "id": "uhd_3840",
                        "value": "UHD 4K — 3840-pixel long edge (recommended)",
                        "workflowValue": "uhd_3840",
                    },
                    {
                        "description": (
                            "Sets the longest edge to 4096 pixels. Choose this for "
                            "DCI-style 4K or a little more finishing headroom."
                        ),
                        "id": "dci_4096",
                        "value": "DCI 4K — 4096-pixel long edge",
                        "workflowValue": "dci_4096",
                    },
                ]
            },
            "lfTextfieldProps": {"lfLabel": "2. Choose the 4K standard"},
            "lfValue": "uhd_3840",
        },
    )


input_upload = WorkflowCell(
    node_id="load_image",
    id="source_path",
    value="Source image",
    shape="upload",
    description=(
        "Choose the finished image to enhance. SeedVR2 reconstructs detail rather "
        "than merely stretching pixels, but it can also reinterpret uncertain source "
        "features. Inspect eyes, hands, text, fine patterns, and character identity."
    ),
    props={
        "lfHtmlAttributes": {"accept": "image/*"},
        "lfLabel": "1. Choose the finished image",
    },
)


input_seed = WorkflowCell(
    node_id="detail_4k",
    id="seed",
    shape="textfield",
    value="3. Choose a seed",
    description=(
        "The seed controls the reconstruction. Reuse it for repeatable comparisons; "
        "try another seed only when a local detail is reconstructed badly."
    ),
    props={
        "lfHtmlAttributes": {
            "autocomplete": "off",
            "max": _MAX_SEED,
            "min": 0,
            "name": "seed",
            "step": 1,
            "type": "number",
        },
        "lfLabel": "3. Choose a seed",
        "lfHelper": {
            "showWhenFocused": False,
            "value": "Use the same seed when comparing settings.",
        },
        "lfValue": "42",
    },
)


output_image = WorkflowCell(
    node_id="save",
    id="image",
    shape="masonry",
    description=(
        "The diffusion-reconstructed 4K PNG. Compare it with the source at 100% zoom "
        "before treating it as the final character asset."
    ),
)


id = "image_detail_4k"
node = WorkflowNode(
    id=id,
    value="4K Detail Pass · SeedVR2",
    description=(
        "Reconstruct one finished image at a true 3840- or 4096-pixel long edge with "
        "the SeedVR2 diffusion upscaler—not a plain resize. The conservative "
        "3B FP8 profile fixes noise at zero, locks color with Lab correction, and uses "
        "tiled VAE processing. It requires the SeedVR2 custom nodes, their roughly "
        "3.4 GB model, and a CUDA GPU; missing models may download on first use."
    ),
    category="Image Processing",
    inputs=[input_upload, _select_cell(), input_seed],
    outputs=[output_image],
    configure_prompt=_configure,
    workflow_path=Path(__file__).resolve().parent / f"{id}.json",
)


WORKFLOW = node
