"""Optional learned-HD finishing pass shared by MiniMax H3 Runner cards.

The standard path is deliberately inert: it adds no graph nodes and changes no
existing connections.  HD rebuilds the configured H3 conditioning at a curated
approximately-two-megapixel canvas, including any active intermediate guides,
then refines the first pass's denoised latent with the accepted four-step local
recipe.  Audio continues to come directly from the original joint AV sample.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping, MutableMapping

from ..services.registry import (
    InputValidationError,
    WorkflowCell,
    WorkflowInputOptionRequirement,
    WorkflowModelAsset,
)


OUTPUT_QUALITY_INPUT_ID = "output_quality"
OUTPUT_QUALITY_STANDARD = "standard"
OUTPUT_QUALITY_HD = "hd"

HD_UPSCALER_MODEL = (
    "minimax_h3_latent_upscaler_3d_conv_v1_bf16.safetensors"
)
HD_OPTION_REQUIREMENT = WorkflowInputOptionRequirement(
    input_id=OUTPUT_QUALITY_INPUT_ID,
    option_value=OUTPUT_QUALITY_HD,
    required_node_types=(
        "MMH3LatentUpscaleWithModelParams",
        "MMH3UltimateUpscale",
    ),
    required_model_assets=(
        WorkflowModelAsset(
            label="MiniMax H3 learned latent upscaler",
            relative_paths=(f"latent_upscale_models/{HD_UPSCALER_MODEL}",),
        ),
    ),
)

# Curated, 32-aligned canvases close to two megapixels.  The accepted 3:4
# trial is retained exactly.  Other entries keep the native canvas aspect as
# closely as the alignment and common HD dimensions allow; "HD" is not a
# promise of a particular 2K standard.
_HD_SIZE_BY_NATIVE_SIZE = {
    (1344, 768): (1920, 1088),
    (1024, 768): (1664, 1248),
    (768, 768): (1440, 1440),
    (768, 1024): (1248, 1664),
    (768, 1344): (1088, 1920),
    (1536, 672): (2208, 960),
}

_HD_NODE_PREFIX = "h3_hd_"
_HD_STEPS = 4
_HD_DENOISE = 0.25


def output_quality_cell() -> WorkflowCell:
    """Return the single public quality control shared by H3 renderers."""

    description = (
        "Standard keeps the native H3 render. HD adds the learned latent "
        "upscaler and a four-step refinement pass at an approximately "
        "two-megapixel, 32-aligned canvas. It is slower and may redraw small "
        "details, so it remains opt-in."
    )
    return WorkflowCell(
        node_id="save",
        id=OUTPUT_QUALITY_INPUT_ID,
        value="Output quality",
        shape="select",
        description=description,
        props={
            "lfDataset": {
                "nodes": [
                    {
                        "description": (
                            "Keep the validated native H3 canvas and skip the "
                            "learned finishing pass."
                        ),
                        "id": OUTPUT_QUALITY_STANDARD,
                        "value": "Standard · native",
                        "workflowValue": OUTPUT_QUALITY_STANDARD,
                    },
                    {
                        "description": (
                            "Run the learned latent upscaler plus the accepted "
                            "four-step, 0.25-denoise refinement at about two "
                            "megapixels."
                        ),
                        "id": OUTPUT_QUALITY_HD,
                        "value": "HD · learned 4-step",
                        "workflowValue": OUTPUT_QUALITY_HD,
                    },
                ]
            },
            "lfTextfieldProps": {
                "lfLabel": "Output quality",
                "lfHelper": {"showWhenFocused": False, "value": description},
            },
            "lfValue": OUTPUT_QUALITY_STANDARD,
        },
    )


def resolve_output_quality(
    inputs: Mapping[str, Any], *, profile_id: str
) -> str:
    """Validate the public quality choice and its accepted profile boundary."""

    value = inputs.get(OUTPUT_QUALITY_INPUT_ID, OUTPUT_QUALITY_STANDARD)
    if value not in (OUTPUT_QUALITY_STANDARD, OUTPUT_QUALITY_HD):
        raise InputValidationError(OUTPUT_QUALITY_INPUT_ID)
    if value == OUTPUT_QUALITY_HD and profile_id != "kitchen_quality":
        raise ValueError(
            "HD output requires Baseline · Kitchen 20. The learned four-step "
            "finishing pass has not been validated with MiniMax H3 Turbo."
        )
    return value


def hd_target_size(base_width: int, base_height: int) -> tuple[int, int]:
    """Return the curated HD canvas for one supported native H3 canvas."""

    try:
        return _HD_SIZE_BY_NATIVE_SIZE[(base_width, base_height)]
    except KeyError as error:
        raise ValueError(
            "HD output requires one of the curated native MiniMax H3 canvases; "
            f"received {base_width}x{base_height}."
        ) from error


def _require_node(
    prompt: Mapping[str, Any], node_id: str, class_type: str
) -> Mapping[str, Any]:
    node = prompt.get(node_id)
    if not isinstance(node, Mapping) or node.get("class_type") != class_type:
        raise ValueError(
            f"HD output expected Runner node {node_id!r} to be {class_type}."
        )
    inputs = node.get("inputs")
    if not isinstance(inputs, Mapping):
        raise ValueError(f"HD output expected inputs on Runner node {node_id!r}.")
    return node


def _clone_target_conditioning(
    prompt: MutableMapping[str, Any], *, target_width: int, target_height: int
) -> list[Any]:
    """Clone H3 and its active guide chain at the refinement canvas."""

    h3 = _require_node(prompt, "h3", prompt["h3"].get("class_type"))
    if h3.get("class_type") not in {
        "MiniMaxH3ImageToVideo",
        "MiniMaxH3ReferenceToVideo",
    }:
        raise ValueError("HD output requires a supported MiniMax H3 conditioner.")
    target_h3_id = f"{_HD_NODE_PREFIX}conditioning"
    target_h3 = deepcopy(h3)
    target_h3["inputs"].update(width=target_width, height=target_height)
    target_h3["_meta"] = {
        "title": "Rebuild MiniMax H3 conditioning at the HD canvas"
    }
    prompt[target_h3_id] = target_h3

    guider = _require_node(prompt, "guider", "BasicGuider")
    source_conditioning = guider["inputs"].get("conditioning")
    cloned: dict[str, list[Any]] = {}

    def clone_reference(reference: Any) -> list[Any]:
        if reference == ["h3", 0]:
            return [target_h3_id, 0]
        if (
            not isinstance(reference, list)
            or len(reference) != 2
            or not isinstance(reference[0], str)
            or reference[1] != 0
        ):
            raise ValueError(
                "HD output could not trace the active H3 conditioning chain."
            )
        source_id = reference[0]
        if source_id in cloned:
            return list(cloned[source_id])
        source = _require_node(prompt, source_id, "MiniMaxH3AddGuide")
        clone_id = f"{_HD_NODE_PREFIX}{source_id}"
        if clone_id in prompt:
            raise ValueError(f"HD output node id collision: {clone_id}.")
        target = deepcopy(source)
        target["inputs"]["positive"] = clone_reference(
            source["inputs"].get("positive")
        )
        target["inputs"]["latent"] = [target_h3_id, 1]
        target["_meta"] = {
            "title": f"Rebuild {source_id} at the HD canvas"
        }
        prompt[clone_id] = target
        cloned[source_id] = [clone_id, 0]
        return [clone_id, 0]

    return clone_reference(source_conditioning)


def apply_optional_hd_pass(
    prompt: MutableMapping[str, Any],
    inputs: Mapping[str, Any],
    *,
    base_width: int,
    base_height: int,
    profile_id: str,
) -> bool:
    """Insert the accepted four-step learned-HD pass when explicitly selected."""

    if resolve_output_quality(inputs, profile_id=profile_id) == OUTPUT_QUALITY_STANDARD:
        return False

    if any(node_id.startswith(_HD_NODE_PREFIX) for node_id in prompt):
        raise ValueError("The MiniMax H3 graph already contains an HD finishing pass.")
    target_width, target_height = hd_target_size(base_width, base_height)
    sample = _require_node(prompt, "sample", "SamplerCustomAdvanced")
    decode_video = _require_node(prompt, "decode_video", "VAEDecode")
    decode_audio = _require_node(prompt, "decode_audio", "VAEDecodeAudio")
    save = _require_node(prompt, "save", "SaveVideo")
    guider = _require_node(prompt, "guider", "BasicGuider")

    sample_inputs = sample["inputs"]
    expected_links = {
        "noise": ["noise", 0],
        "sampler": ["sampler_select", 0],
        "sigmas": ["scheduler", 0],
    }
    if any(sample_inputs.get(name) != link for name, link in expected_links.items()):
        raise ValueError("HD output requires the validated H3 sampling connections.")
    if decode_audio["inputs"].get("samples") != ["sample", 0]:
        raise ValueError("HD output requires the original joint AV sample for audio.")

    model = deepcopy(guider["inputs"].get("model"))
    if not isinstance(model, list) or len(model) != 2:
        raise ValueError("HD output could not resolve the configured H3 model.")
    target_conditioning = _clone_target_conditioning(
        prompt,
        target_width=target_width,
        target_height=target_height,
    )

    prompt[f"{_HD_NODE_PREFIX}scheduler"] = {
        "inputs": {
            "model": deepcopy(model),
            "scheduler": "simple",
            "steps": _HD_STEPS,
            "denoise": _HD_DENOISE,
        },
        "class_type": "BasicScheduler",
        "_meta": {"title": "Schedule the four-step H3 HD refinement"},
    }
    prompt[f"{_HD_NODE_PREFIX}parameters"] = {
        "inputs": {
            "model_name": HD_UPSCALER_MODEL,
            "width": target_width,
            "height": target_height,
            "device": "cuda",
            "precision": "bf16",
            "keep_models_resident": False,
        },
        "class_type": "MMH3LatentUpscaleWithModelParams",
        "_meta": {"title": "Configure the learned H3 latent upscaler"},
    }
    prompt[f"{_HD_NODE_PREFIX}upscale"] = {
        "inputs": {
            "model": deepcopy(model),
            "conditioning": target_conditioning,
            "latent": ["sample", 1],
            "noise": deepcopy(sample_inputs["noise"]),
            "sampler": deepcopy(sample_inputs["sampler"]),
            "sigmas": [f"{_HD_NODE_PREFIX}scheduler", 0],
            "cfg": 1.0,
            "latent_upscale_param": [f"{_HD_NODE_PREFIX}parameters", 0],
        },
        "class_type": "MMH3UltimateUpscale",
        "_meta": {"title": "Learned H3 upscale and four-step refinement"},
    }
    decode_video["inputs"]["samples"] = [f"{_HD_NODE_PREFIX}upscale", 0]
    prefix = save["inputs"].get("filename_prefix")
    if not isinstance(prefix, str) or not prefix:
        raise ValueError("HD output requires a configured video filename prefix.")
    save["inputs"]["filename_prefix"] = f"{prefix}-hd4"
    return True


__all__ = [
    "HD_OPTION_REQUIREMENT",
    "HD_UPSCALER_MODEL",
    "OUTPUT_QUALITY_HD",
    "OUTPUT_QUALITY_INPUT_ID",
    "OUTPUT_QUALITY_STANDARD",
    "apply_optional_hd_pass",
    "hd_target_size",
    "output_quality_cell",
    "resolve_output_quality",
]
