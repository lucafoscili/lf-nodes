"""Beginner-facing Krea 2 workflows for LF Workflow Runner.

These workflows use installed checkpoints and community adapters.
They never call Krea's hosted API. Reference-image workflows remain explicit
about their semantics: a style reference guides visual language, while the
separate Identity Edit adapter is responsible for identity preservation.
"""

from __future__ import annotations

import math
import os
from pathlib import Path
from typing import Any, Dict, NamedTuple

from ..services.registry import InputValidationError, WorkflowCell, WorkflowNode
from .utils import (
    choice as _choice,
    has_input_value as _has_image,
    integer as _integer,
    require_input_value as _required_image,
    required_text as _required_text,
    resolve_load_image_reference,
)


_OFFICIAL_KREA2_MODEL = os.path.join(
    "KR2", "krea2_turbo_int8_convrot.safetensors"
)
_DARKBEAST_MODEL = os.path.join(
    "KR2", "darkBeast30BF16INT8_darkBeastKREA2FP8.safetensors"
)
_MOODY_MODEL = os.path.join("KR2", "moodyKrea2Mix_v60.safetensors")
_LUSTIFY_MODEL = os.path.join(
    "KR2", "lustifyNSFWCheckpoint_v10Krea2.safetensors"
)
_LOCAL_MODELS = (
    _DARKBEAST_MODEL,
    _MOODY_MODEL,
    _LUSTIFY_MODEL,
    _OFFICIAL_KREA2_MODEL,
)
_LOCAL_DEFAULT_MODEL = _LOCAL_MODELS[0]
_ADAPTER_MODELS = (
    _OFFICIAL_KREA2_MODEL,
    _DARKBEAST_MODEL,
    _MOODY_MODEL,
    _LUSTIFY_MODEL,
)
_ADAPTER_DEFAULT_MODEL = _OFFICIAL_KREA2_MODEL
_LOCAL_MAX_SEED = (1 << 53) - 1
_LOCAL_CANVAS_MULTIPLE = 16
_LOCAL_MAX_EDGE = 2048
_LOCAL_MAX_PIXELS = 2_000_000
_SQUARE_ASPECT_RATIO = "1:1 (Square)"
_PORTRAIT_ASPECT_RATIO = "2:3 (Portrait Photo)"
_ASPECT_RATIO_TARGETS = {
    _SQUARE_ASPECT_RATIO: ((1, 1), 1.9),
    _PORTRAIT_ASPECT_RATIO: ((2, 3), 1.9),
    "3:2 (Photo)": ((3, 2), 1.9),
    "3:4 (Portrait Standard)": ((3, 4), 1.9),
    "4:3 (Standard)": ((4, 3), 1.9),
    "9:16 (Portrait Widescreen)": ((9, 16), 1.9),
    "16:9 (Widescreen)": ((16, 9), 1.9),
    "21:9 (Ultrawide)": ((21, 9), 1.72),
}
_DEFAULT_SAMPLER = "euler"
_DEFAULT_SCHEDULER = "beta"
_SAMPLER_OPTIONS = (
    (
        "euler",
        "Euler — default",
        "The fast, established starting point for Krea 2 Turbo and edit recipes.",
    ),
    (
        "euler_ancestral",
        "Euler Ancestral",
        "Adds fresh noise during sampling, often increasing texture and variation.",
    ),
    (
        "heun",
        "Heun",
        "A two-stage method that can produce a steadier result at extra compute cost.",
    ),
    (
        "dpmpp_2m",
        "DPM++ 2M",
        "A smoother multistep alternative; compare it at the same seed and step count.",
    ),
    (
        "dpmpp_2m_sde",
        "DPM++ 2M SDE",
        "A stochastic multistep alternative that can trade speed for softer detail.",
    ),
)
_SCHEDULER_OPTIONS = (
    (
        "beta",
        "Beta — default",
        "The community Krea 2 edit starting point used by this Runner profile.",
    ),
    (
        "simple",
        "Simple",
        "The published ReID reference setting and the previous Runner default.",
    ),
    (
        "normal",
        "Normal",
        "Uses ComfyUI's standard model-derived noise schedule.",
    ),
    (
        "karras",
        "Karras",
        "Concentrates more steps near the cleaner end of denoising.",
    ),
    (
        "sgm_uniform",
        "SGM Uniform",
        "Evenly spaces the model's noise levels; useful for controlled comparisons.",
    ),
)
_REID_MODEL = _OFFICIAL_KREA2_MODEL
_REID_MODELS = (
    _REID_MODEL,
    _DARKBEAST_MODEL,
    _MOODY_MODEL,
    _LUSTIFY_MODEL,
)
_STYLE_LORA = os.path.join("KR2", "krea2_style_reference.safetensors")
_IDENTITY_LORA = os.path.join("KR2", "krea2_identity_edit_v1_2.safetensors")
_REID_LORA = os.path.join("KR2", "krea2_reid_rank32.safetensors")
_OFFICIAL_VAE = "qwen_image_vae.safetensors"
_LOCAL_VAE = "krea2RealVae_v10.safetensors"
_REID_VAE = _OFFICIAL_VAE
_GENERATION_VAE_BY_MODEL = {
    _DARKBEAST_MODEL: _LOCAL_VAE,
    _MOODY_MODEL: _LOCAL_VAE,
    _LUSTIFY_MODEL: _OFFICIAL_VAE,
    _OFFICIAL_KREA2_MODEL: _OFFICIAL_VAE,
}


class _LocalSettings(NamedTuple):
    prompt_text: str
    model_name: str
    aspect_ratio: str
    megapixels: float
    seed: int
    steps: int
    cfg: float
    sampler_name: str
    scheduler: str


def _resolution_for(aspect_ratio: str) -> tuple[float, int, int]:
    """Mirror Core's ResolutionSelector and enforce the Krea canvas profile."""

    (width_ratio, height_ratio), megapixels = _ASPECT_RATIO_TARGETS[aspect_ratio]
    total_pixels = megapixels * 1024 * 1024
    scale = math.sqrt(total_pixels / (width_ratio * height_ratio))
    width = round(width_ratio * scale / _LOCAL_CANVAS_MULTIPLE) * _LOCAL_CANVAS_MULTIPLE
    height = round(height_ratio * scale / _LOCAL_CANVAS_MULTIPLE) * _LOCAL_CANVAS_MULTIPLE
    if (
        width < 256
        or height < 256
        or width > _LOCAL_MAX_EDGE
        or height > _LOCAL_MAX_EDGE
        or width * height > _LOCAL_MAX_PIXELS
    ):
        raise RuntimeError(
            f"Unsafe Krea 2 resolution profile for {aspect_ratio}: {width}x{height}."
        )
    return megapixels, width, height


def _apply_resolution(
    prompt: Dict[str, Any],
    aspect_ratio: str,
    megapixels: float,
) -> None:
    prompt["resolution"]["inputs"].update(
        {
            "aspect_ratio": aspect_ratio,
            "megapixels": megapixels,
            "multiple": _LOCAL_CANVAS_MULTIPLE,
        }
    )
    prompt["latent"]["inputs"].update(
        {"width": ["resolution", 0], "height": ["resolution", 1]}
    )


def _number(
    inputs: Dict[str, Any],
    name: str,
    default: float,
    *,
    minimum: float,
    maximum: float,
) -> float:
    value = inputs.get(name, default)
    if value in (None, ""):
        value = default
    if isinstance(value, bool):
        raise InputValidationError(name)
    try:
        parsed = float(value)
    except (TypeError, ValueError) as error:
        raise InputValidationError(name) from error
    if not math.isfinite(parsed) or parsed < minimum or parsed > maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}.")
    return parsed


def _local_settings(
    inputs: Dict[str, Any],
    *,
    default_aspect_ratio: str = _SQUARE_ASPECT_RATIO,
    default_model: str = _LOCAL_DEFAULT_MODEL,
    model_choices: tuple[str, ...] = _LOCAL_MODELS,
    min_steps: int = 4,
    max_steps: int = 20,
) -> _LocalSettings:
    prompt_text = _required_text(inputs, "prompt")
    model_name = _choice(
        inputs, "model_name", default_model, model_choices
    )
    aspect_ratio = _choice(
        inputs,
        "aspect_ratio",
        default_aspect_ratio,
        _ASPECT_RATIO_TARGETS,
    )
    megapixels, _, _ = _resolution_for(aspect_ratio)
    seed = _integer(
        inputs, "seed", 42, minimum=0, maximum=_LOCAL_MAX_SEED
    )
    steps = _integer(inputs, "steps", 8, minimum=min_steps, maximum=max_steps)
    cfg = _number(inputs, "cfg", 1.0, minimum=0.0, maximum=20.0)
    sampler_name = _choice(
        inputs,
        "sampler_name",
        _DEFAULT_SAMPLER,
        (option[0] for option in _SAMPLER_OPTIONS),
    )
    scheduler = _choice(
        inputs,
        "scheduler",
        _DEFAULT_SCHEDULER,
        (option[0] for option in _SCHEDULER_OPTIONS),
    )
    return _LocalSettings(
        prompt_text=prompt_text,
        model_name=model_name,
        aspect_ratio=aspect_ratio,
        megapixels=megapixels,
        seed=seed,
        steps=steps,
        cfg=cfg,
        sampler_name=sampler_name,
        scheduler=scheduler,
    )


def _apply_local_settings(
    prompt: Dict[str, Any],
    settings: _LocalSettings,
    output_folder: str,
    *,
    vae_name: str | None = None,
) -> None:
    prompt["unet"]["inputs"]["unet_name"] = settings.model_name
    prompt["vae"]["inputs"]["vae_name"] = vae_name or _GENERATION_VAE_BY_MODEL[
        settings.model_name
    ]
    prompt_input_name = (
        "prompt" if "prompt" in prompt["positive"]["inputs"] else "text"
    )
    prompt["positive"]["inputs"][prompt_input_name] = settings.prompt_text
    _apply_resolution(prompt, settings.aspect_ratio, settings.megapixels)
    prompt["sampler"]["inputs"].update(
        {
            "seed": settings.seed,
            "steps": settings.steps,
            "cfg": settings.cfg,
            "sampler_name": settings.sampler_name,
            "scheduler": settings.scheduler,
        }
    )
    prompt["save"]["inputs"]["filename_prefix"] = (
        f"LF_Nodes/Krea2/{output_folder}/seed-{settings.seed}"
    )


def _configure_generate(prompt: Dict[str, Any], inputs: Dict[str, Any]) -> None:
    _apply_local_settings(prompt, _local_settings(inputs), "Generate")


def _apply_style_adapter_settings(
    prompt: Dict[str, Any],
    inputs: Dict[str, Any],
    output_folder: str,
) -> None:
    if "cfg" in inputs:
        # These style-reference graphs deliberately zero the negative
        # conditioning.  CFG values above one therefore do not represent a
        # meaningful user control; reject stale/headless clients instead of
        # accepting a hidden quality trap.
        cfg = _number(inputs, "cfg", 1.0, minimum=1.0, maximum=1.0)
        if cfg != 1.0:  # Defensive clarity if the numeric helper changes.
            raise ValueError("cfg must be 1 for Krea 2 style-reference workflows.")
    settings_inputs = dict(inputs)
    settings_inputs["cfg"] = 1.0
    settings = _local_settings(
        settings_inputs,
        default_model=_ADAPTER_DEFAULT_MODEL,
        model_choices=_ADAPTER_MODELS,
    )
    strength = _number(
        inputs, "style_strength", 1.0, minimum=0.0, maximum=2.0
    )
    prompt["lora"]["inputs"]["lora_name"] = _STYLE_LORA
    prompt["lora"]["inputs"]["strength_model"] = strength
    _apply_local_settings(
        prompt,
        settings,
        output_folder,
        vae_name=_OFFICIAL_VAE,
    )


def _configure_style_reference(prompt: Dict[str, Any], inputs: Dict[str, Any]) -> None:
    # Validate the complete request before staging the upload.
    _required_image(inputs, "style_image")
    _apply_style_adapter_settings(prompt, inputs, "StyleReference")
    style_image = resolve_load_image_reference(inputs, "style_image")

    prompt["style"]["inputs"]["image"] = style_image


def _configure_style_reference_download(
    prompt: Dict[str, Any], inputs: Dict[str, Any]
) -> None:
    _apply_style_adapter_settings(prompt, inputs, "StyleReference")


def _configure_style_blend(prompt: Dict[str, Any], inputs: Dict[str, Any]) -> None:
    # Both references have the same graph role. Do not invent per-image weights.
    _required_image(inputs, "style_a_image")
    _required_image(inputs, "style_b_image")
    _apply_style_adapter_settings(prompt, inputs, "StyleBlend")
    style_a = resolve_load_image_reference(inputs, "style_a_image")
    style_b = resolve_load_image_reference(inputs, "style_b_image")

    prompt["style_a"]["inputs"]["image"] = style_a
    prompt["style_b"]["inputs"]["image"] = style_b


def _configure_style_blend_download(
    prompt: Dict[str, Any], inputs: Dict[str, Any]
) -> None:
    _apply_style_adapter_settings(prompt, inputs, "StyleBlend")


def _apply_identity_edit_settings(
    prompt: Dict[str, Any], inputs: Dict[str, Any]
) -> None:
    settings = _local_settings(
        inputs,
        default_aspect_ratio=_PORTRAIT_ASPECT_RATIO,
        default_model=_ADAPTER_DEFAULT_MODEL,
        model_choices=_ADAPTER_MODELS,
        min_steps=8,
        max_steps=12,
    )
    identity_fidelity = _number(
        inputs, "identity_fidelity", 4.0, minimum=0.0, maximum=100.0
    )
    grounding_px = _integer(
        inputs, "grounding_px", 1024, minimum=384, maximum=2048
    )

    prompt["unet"]["inputs"]["unet_name"] = settings.model_name
    prompt["vae"]["inputs"]["vae_name"] = _OFFICIAL_VAE
    prompt["lora"]["inputs"]["lora_name"] = _IDENTITY_LORA
    _apply_resolution(prompt, settings.aspect_ratio, settings.megapixels)
    prompt["patch"]["inputs"]["ref_boost"] = identity_fidelity
    prompt["positive"]["inputs"].update(
        {"prompt": settings.prompt_text, "grounding_px": grounding_px}
    )
    prompt["negative"]["inputs"]["grounding_px"] = grounding_px
    prompt["sampler"]["inputs"].update(
        {
            "seed": settings.seed,
            "steps": settings.steps,
            "cfg": settings.cfg,
            "sampler_name": settings.sampler_name,
            "scheduler": settings.scheduler,
        }
    )
    prompt["save"]["inputs"]["filename_prefix"] = (
        f"LF_Nodes/Krea2/IdentityEdit/seed-{settings.seed}"
    )


def _configure_identity_edit(prompt: Dict[str, Any], inputs: Dict[str, Any]) -> None:
    # Validate every scalar and both upload requirements before touching files.
    _required_image(inputs, "identity_image")
    has_scene = _has_image(inputs, "scene_image")
    _apply_identity_edit_settings(prompt, inputs)

    identity_image = resolve_load_image_reference(inputs, "identity_image")
    scene_image = (
        resolve_load_image_reference(inputs, "scene_image") if has_scene else None
    )

    prompt["identity"]["inputs"]["image"] = identity_image
    if has_scene:
        prompt["scene"]["inputs"]["image"] = scene_image
    else:
        _remove_identity_edit_scene_branch(prompt)


def _remove_identity_edit_scene_branch(prompt: Dict[str, Any]) -> None:
    """Make the Identity Edit graph's optional-scene default executable."""

    prompt.pop("scene", None)
    prompt.pop("scene_latent", None)
    prompt["patch"]["inputs"]["source_latent"] = ["identity_latent", 0]
    prompt["patch"]["inputs"]["source_image"] = ["identity", 0]
    prompt["patch"]["inputs"].pop("source_latent_b", None)
    prompt["patch"]["inputs"].pop("source_image_b", None)
    for conditioning_id in ("positive", "negative"):
        conditioning = prompt[conditioning_id]["inputs"]
        conditioning["image"] = ["identity", 0]
        conditioning.pop("image_b", None)


def _configure_identity_edit_download(
    prompt: Dict[str, Any], inputs: Dict[str, Any]
) -> None:
    _apply_identity_edit_settings(prompt, inputs)
    _remove_identity_edit_scene_branch(prompt)


def _apply_reid_settings(
    prompt: Dict[str, Any],
    inputs: Dict[str, Any],
    *,
    output_folder: str,
) -> None:
    prompt_text = _required_text(inputs, "prompt")
    model_name = _choice(inputs, "model_name", _REID_MODEL, _REID_MODELS)
    aspect_ratio = _choice(
        inputs,
        "aspect_ratio",
        _PORTRAIT_ASPECT_RATIO,
        _ASPECT_RATIO_TARGETS,
    )
    megapixels, _width, _height = _resolution_for(aspect_ratio)
    seed = _integer(
        inputs, "seed", 42, minimum=0, maximum=_LOCAL_MAX_SEED
    )

    prompt["unet"]["inputs"]["unet_name"] = model_name
    prompt["vae"]["inputs"]["vae_name"] = _REID_VAE
    prompt["lora"]["inputs"]["lora_name"] = _REID_LORA
    prompt["positive_encode"]["inputs"]["prompt"] = prompt_text
    _apply_resolution(prompt, aspect_ratio, megapixels)
    prompt["sampler"]["inputs"]["seed"] = seed
    prompt["save"]["inputs"]["filename_prefix"] = (
        f"LF_Nodes/Krea2/{output_folder}/seed-{seed}"
    )


def _configure_reid(
    prompt: Dict[str, Any],
    inputs: Dict[str, Any],
    *,
    output_folder: str,
) -> None:
    """Apply creative controls while keeping the ReID sampler contract fixed."""

    _required_image(inputs, "reference_image")
    _apply_reid_settings(prompt, inputs, output_folder=output_folder)
    reference_image = resolve_load_image_reference(inputs, "reference_image")
    prompt["reference"]["inputs"]["image"] = reference_image


def _configure_character_restage(
    prompt: Dict[str, Any], inputs: Dict[str, Any]
) -> None:
    _configure_reid(prompt, inputs, output_folder="CharacterRestage")


def _configure_character_restage_download(
    prompt: Dict[str, Any], inputs: Dict[str, Any]
) -> None:
    _apply_reid_settings(prompt, inputs, output_folder="CharacterRestage")


def _configure_outfit_change(
    prompt: Dict[str, Any], inputs: Dict[str, Any]
) -> None:
    _configure_reid(prompt, inputs, output_folder="OutfitChange")


def _configure_outfit_change_download(
    prompt: Dict[str, Any], inputs: Dict[str, Any]
) -> None:
    _apply_reid_settings(prompt, inputs, output_folder="OutfitChange")


def _configure_pose_change(
    prompt: Dict[str, Any], inputs: Dict[str, Any]
) -> None:
    _configure_reid(prompt, inputs, output_folder="PoseChange")


def _configure_pose_change_download(
    prompt: Dict[str, Any], inputs: Dict[str, Any]
) -> None:
    _apply_reid_settings(prompt, inputs, output_folder="PoseChange")


def _configure_feature_edit(
    prompt: Dict[str, Any], inputs: Dict[str, Any]
) -> None:
    _configure_reid(prompt, inputs, output_folder="FeatureEdit")


def _configure_feature_edit_download(
    prompt: Dict[str, Any], inputs: Dict[str, Any]
) -> None:
    _apply_reid_settings(prompt, inputs, output_folder="FeatureEdit")


def _configure_character_restyle(
    prompt: Dict[str, Any], inputs: Dict[str, Any]
) -> None:
    _configure_reid(prompt, inputs, output_folder="CharacterRestyle")


def _configure_character_restyle_download(
    prompt: Dict[str, Any], inputs: Dict[str, Any]
) -> None:
    _apply_reid_settings(prompt, inputs, output_folder="CharacterRestyle")


def _select_cell(
    *,
    node_id: str,
    cell_id: str,
    label: str,
    default: str,
    description: str,
    options: tuple[tuple[str, str, str], ...],
) -> WorkflowCell:
    return WorkflowCell(
        node_id=node_id,
        id=cell_id,
        shape="select",
        value=label,
        description=description,
        props={
            "lfDataset": {
                "nodes": [
                    {
                        "description": option_description,
                        "id": value,
                        "value": option_label,
                        "workflowValue": value,
                    }
                    for value, option_label, option_description in options
                ]
            },
            "lfTextfieldProps": {
                "lfHelper": {
                    "showWhenFocused": False,
                    "value": description,
                },
                "lfLabel": label,
            },
            "lfValue": default,
        },
    )


def _number_cell(
    *,
    node_id: str,
    cell_id: str,
    label: str,
    default: str,
    minimum: float,
    maximum: float,
    step: float,
    description: str,
) -> WorkflowCell:
    return WorkflowCell(
        node_id=node_id,
        id=cell_id,
        shape="textfield",
        value=label,
        description=description,
        props={
            "lfHtmlAttributes": {
                "autocomplete": "off",
                "max": maximum,
                "min": minimum,
                "name": cell_id,
                "step": step,
                "type": "number",
            },
            "lfLabel": label,
            "lfHelper": {"showWhenFocused": False, "value": description},
            "lfValue": default,
        },
    )


def _prompt_cell(
    *,
    node_id: str = "positive",
    label: str = "Prompt",
    default: str = (
        "A cinematic waist-up portrait of an original traveler beside a rain-streaked "
        "train window at blue hour, looking calmly toward the camera. They wear a "
        "weathered charcoal coat over a textured linen shirt. Use balanced asymmetrical "
        "framing, natural anatomy, a 50 mm lens with shallow depth of field, soft cool "
        "window light balanced by a warm practical rim light, restrained teal-and-amber "
        "color, coherent skin, fabric, glass, and metal textures, and a layered station "
        "interior fading softly into the background."
    ),
    description: str = (
        "Describe the subject, scene, composition, and important details you want in the result."
    ),
) -> WorkflowCell:
    return WorkflowCell(
        node_id=node_id,
        id="prompt",
        shape="textfield",
        value=label,
        description=description,
        props={
            "lfHtmlAttributes": {
                "autocomplete": "off",
                "name": "prompt",
                "type": "text",
            },
            "lfLabel": label,
            "lfHelper": {"showWhenFocused": False, "value": description},
            "lfStyling": "textarea",
            "lfValue": default,
        },
    )


def _upload_cell(
    node_id: str,
    cell_id: str,
    label: str,
    description: str,
    *,
    required: bool = True,
) -> WorkflowCell:
    return WorkflowCell(
        node_id=node_id,
        id=cell_id,
        shape="upload",
        value=label,
        description=description,
        required=required,
        props={
            "lfHtmlAttributes": {"accept": "image/*"},
            "lfLabel": label,
        },
    )


def _generation_model_cell() -> WorkflowCell:
    return _select_cell(
        node_id="unet",
        cell_id="model_name",
        label="Checkpoint",
        default=_LOCAL_DEFAULT_MODEL,
        description="Choose an installed Krea 2-compatible checkpoint.",
        options=(
            (
                _DARKBEAST_MODEL,
                "DarkBeast Krea 2 FP8 — default",
                "The established default for balanced character and scene work.",
            ),
            (
                _MOODY_MODEL,
                "Moody Krea 2 Mix v6",
                "An alternate checkpoint with a more stylized visual bias.",
            ),
            (
                _LUSTIFY_MODEL,
                "Lustify v10 Krea 2 INT8 ConvRot — experimental",
                "Community checkpoint with a photoreal bias, available for "
                "same-seed visual comparisons.",
            ),
            (
                _OFFICIAL_KREA2_MODEL,
                "Official Krea 2 Turbo INT8 ConvRot",
                "The pinned official Comfy-Org Turbo base and neutral compatibility reference.",
            ),
        ),
    )


def _adapter_model_cell() -> WorkflowCell:
    return _select_cell(
        node_id="unet",
        cell_id="model_name",
        label="Adapter base",
        default=_ADAPTER_DEFAULT_MODEL,
        description=(
            "The official Turbo base and Qwen Image VAE are the documented adapter "
            "pairing. Community checkpoints remain explicit same-seed experiments; "
            "successful loading alone does not establish style or identity fidelity."
        ),
        options=(
            (
                _OFFICIAL_KREA2_MODEL,
                "Official Krea 2 Turbo INT8 — adapter default",
                "Pinned Comfy-Org Turbo base paired with the official Qwen Image VAE.",
            ),
            (
                _DARKBEAST_MODEL,
                "DarkBeast Krea 2 FP8 — experimental",
                "Community derivative available for controlled visual A/B comparison.",
            ),
            (
                _MOODY_MODEL,
                "Moody Krea 2 Mix v6 — experimental",
                "Community derivative whose adapter fidelity has not been characterized.",
            ),
            (
                _LUSTIFY_MODEL,
                "Lustify v10 Krea 2 INT8 ConvRot — experimental",
                "Structurally compatible community checkpoint; adapter fidelity "
                "still requires a visual A/B.",
            ),
        ),
    )


def _reid_model_cell() -> WorkflowCell:
    return _select_cell(
        node_id="unet",
        cell_id="model_name",
        label="ReID base",
        default=_REID_MODEL,
        description=(
            "The official INT8 ConvRot base is the validated ReID pairing. Community "
            "checkpoints are structurally compatible experiments whose ReID fidelity "
            "varies independently of loading compatibility."
        ),
        options=(
            (
                _REID_MODEL,
                "Official Krea 2 Turbo INT8 — validated",
                "Pinned Comfy-Org base used by the published ReID workflow contract.",
            ),
            (
                _DARKBEAST_MODEL,
                "DarkBeast Krea 2 FP8 — experimental",
                "Community derivative; structurally compatible, with ReID behavior "
                "best compared at the same seed.",
            ),
            (
                _MOODY_MODEL,
                "Moody Krea 2 Mix v6 — experimental",
                "Community derivative with unqualified ReID fidelity, available "
                "as a controlled visual probe.",
            ),
            (
                _LUSTIFY_MODEL,
                "Lustify v10 Krea 2 INT8 ConvRot — experimental",
                "Structurally compatible community checkpoint; ReID fidelity still "
                "requires a visual A/B.",
            ),
        ),
    )


def _seed_cell() -> WorkflowCell:
    return _number_cell(
        node_id="sampler",
        cell_id="seed",
        label="Seed",
        default="42",
        minimum=0,
        maximum=_LOCAL_MAX_SEED,
        step=1,
        description="Reuse the same seed and settings for a controlled comparison.",
    )


def _sampler_cell() -> WorkflowCell:
    return _select_cell(
        node_id="sampler",
        cell_id="sampler_name",
        label="Sampler",
        default=_DEFAULT_SAMPLER,
        description=(
            "The numerical method used for each denoising step. Euler is the fast "
            "Krea 2 starting point; alternate samplers are best treated as same-seed "
            "quality experiments."
        ),
        options=_SAMPLER_OPTIONS,
    )


def _scheduler_cell() -> WorkflowCell:
    return _select_cell(
        node_id="sampler",
        cell_id="scheduler",
        label="Scheduler",
        default=_DEFAULT_SCHEDULER,
        description=(
            "How denoising strength is distributed across the steps. Beta is this "
            "Runner profile's default; Simple remains available for reproducing older "
            "or published reference recipes."
        ),
        options=_SCHEDULER_OPTIONS,
    )


def _aspect_ratio_cell(
    default_aspect_ratio: str = _SQUARE_ASPECT_RATIO,
) -> WorkflowCell:
    options = []
    for value in _ASPECT_RATIO_TARGETS:
        _, width, height = _resolution_for(value)
        limit = "maximum edge" if value.startswith("21:9") else "canvas area"
        options.append(
            (
                value,
                f"{value} — {width} × {height}",
                f"Largest safe 16-pixel-aligned canvas for this shape; {limit}-bound.",
            )
        )
    return _select_cell(
        node_id="resolution",
        cell_id="aspect_ratio",
        label="Aspect ratio",
        default=default_aspect_ratio,
        description=(
            "Choose the canvas shape. The Runner automatically selects the largest "
            "safe 16-pixel-aligned Krea 2 resolution within 2 megapixels and a 2048 "
            "pixel maximum edge; it does not resize or crop an existing image."
        ),
        options=tuple(options),
    )


def _sampling_cells(
    *,
    default_steps: int = 8,
    min_steps: int = 4,
    max_steps: int = 20,
    include_cfg: bool = True,
) -> list[WorkflowCell]:
    cells = [
        _seed_cell(),
        _number_cell(
            node_id="sampler",
            cell_id="steps",
            label="Steps",
            default=str(default_steps),
            minimum=min_steps,
            maximum=max_steps,
            step=1,
            description=(
                "Denoising passes. Eight is the established starting point for these "
                "Krea 2 recipes; "
                "more is slower and is not automatically better."
            ),
        ),
        _sampler_cell(),
        _scheduler_cell(),
    ]
    if include_cfg:
        cells.append(
            _number_cell(
                node_id="sampler",
                cell_id="cfg",
                label="CFG",
                default="1",
                minimum=0,
                maximum=20,
                step=0.1,
                description=(
                    "Prompt guidance. CFG 1 is the established starting point for these "
                    "Krea 2 recipes."
                ),
            )
        )
    return cells


def _local_common_inputs(
    *,
    default_aspect_ratio: str = _SQUARE_ASPECT_RATIO,
    default_steps: int = 8,
    min_steps: int = 4,
    max_steps: int = 20,
    adapter_profile: bool = False,
    include_cfg: bool = True,
) -> list[WorkflowCell]:
    return [
        _adapter_model_cell() if adapter_profile else _generation_model_cell(),
        _aspect_ratio_cell(default_aspect_ratio),
        *_sampling_cells(
            default_steps=default_steps,
            min_steps=min_steps,
            max_steps=max_steps,
            include_cfg=include_cfg,
        ),
    ]


def _image_output(description: str) -> WorkflowCell:
    return WorkflowCell(
        node_id="save",
        id="image",
        shape="masonry",
        description=description,
    )


def _reid_inputs(
    *,
    prompt_label: str,
    prompt_default: str,
    prompt_description: str,
    default_aspect_ratio: str = _PORTRAIT_ASPECT_RATIO,
) -> list[WorkflowCell]:
    return [
        _upload_cell(
            "reference",
            "reference_image",
            "Character reference",
            (
                "Upload one character reference image. A face or head-and-shoulders "
                "crop gives the prompt the most freedom over clothing and pose; a "
                "full-body image deliberately carries more costume and posture into "
                "the result. The node inserts its internal Picture 1 tokens for you."
            ),
        ),
        _prompt_cell(
            node_id="positive_encode",
            label=prompt_label,
            default=prompt_default,
            description=prompt_description,
        ),
        _reid_model_cell(),
        _aspect_ratio_cell(default_aspect_ratio),
        _seed_cell(),
    ]


_WORKFLOW_DIR = Path(__file__).resolve().parent


generate = WorkflowNode(
    id="krea2_generate",
    value="Generate Image",
    description="Generate an image from text with an installed Krea 2-compatible checkpoint.",
    category="Krea 2",
    inputs=[_prompt_cell(), *_local_common_inputs()],
    outputs=[_image_output("The generated PNG image.")],
    configure_prompt=_configure_generate,
    configure_download=_configure_generate,
    workflow_path=_WORKFLOW_DIR / "krea2_generate.json",
)


style_reference = WorkflowNode(
    id="krea2_style_reference",
    value="Style Reference",
    description=(
        "Generate new content in the visual language of one uploaded image "
        "using the community Krea 2 style-reference adapter. It can carry palette, linework, "
        "texture, lighting, and composition cues; it does not promise to preserve the "
        "uploaded image's subject identity."
    ),
    category="Krea 2",
    inputs=[
        _upload_cell(
            "style",
            "style_image",
            "Style image",
            (
                "Upload a visual reference for palette, rendering, linework, texture, "
                "and lighting. Its subject is not treated as an identity anchor. The "
                "node inserts the Picture 1 vision marker automatically."
            ),
        ),
        _prompt_cell(
            default=(
                "A young traveler waiting beneath a glass railway canopy during a "
                "summer rain, holding a folded map and looking toward an arriving train. "
                "Use a three-quarter full-body composition, a clear silhouette, natural "
                "posture and hands, wet stone reflections, a textured coat and leather "
                "bag, cool overcast daylight balanced by warm platform lights, and "
                "layered foreground, platform, and distant architecture."
            ),
            description=(
                "Describe the new subject and composition. The uploaded image supplies "
                "visual language, so focus on subject, action, framing, lighting, "
                "materials, and background rather than repeating style adjectives."
            ),
        ),
        _number_cell(
            node_id="lora",
            cell_id="style_strength",
            label="Style adapter strength",
            default="1",
            minimum=0,
            maximum=2,
            step=0.05,
            description=(
                "Strength of the community style-reference LoRA. Start at 1; lower it "
                "if the reference overwhelms the prompt."
            ),
        ),
        *_local_common_inputs(adapter_profile=True, include_cfg=False),
    ],
    outputs=[_image_output("The generated style-guided PNG image.")],
    configure_prompt=_configure_style_reference,
    configure_download=_configure_style_reference_download,
    workflow_path=_WORKFLOW_DIR / "krea2_style_reference.json",
)


style_blend = WorkflowNode(
    id="krea2_style_blend",
    value="Blend Two Styles",
    description=(
        "Generate new content from two style images using the community Krea 2 "
        "style-reference adapter. Both images have the same conditioning role; their "
        "order can affect the result and this adapter does not expose separate weights."
    ),
    category="Krea 2",
    inputs=[
        _upload_cell(
            "style_a",
            "style_a_image",
            "First style image",
            "The first palette, rendering, texture, lighting, or composition reference.",
        ),
        _upload_cell(
            "style_b",
            "style_b_image",
            "Second style image",
            (
                "The second visual-language reference. Swap the two uploads if their "
                "ordering produces an unwanted bias. Picture 1 / Picture 2 markers are "
                "inserted automatically; do not add them to the prompt."
            ),
        ),
        _prompt_cell(
            default=(
                "A young traveler waiting beneath a glass railway canopy during a "
                "summer rain, holding a folded map and looking toward an arriving train. "
                "Use a three-quarter full-body composition, a clear silhouette, natural "
                "posture and hands, wet stone reflections, a textured coat and leather "
                "bag, cool overcast daylight balanced by warm platform lights, and "
                "layered foreground, platform, and distant architecture."
            ),
            description=(
                "Describe the new subject and composition. Both uploads contribute "
                "style cues, so focus on subject, action, framing, lighting, materials, "
                "and background rather than repeating style adjectives."
            ),
        ),
        _number_cell(
            node_id="lora",
            cell_id="style_strength",
            label="Style adapter strength",
            default="1",
            minimum=0,
            maximum=2,
            step=0.05,
            description=(
                "Shared strength of the style-reference LoRA. This is not an A/B mix "
                "slider; the underlying adapter gives both images the same role."
            ),
        ),
        *_local_common_inputs(adapter_profile=True, include_cfg=False),
    ],
    outputs=[_image_output("The generated two-style PNG image.")],
    configure_prompt=_configure_style_blend,
    configure_download=_configure_style_blend_download,
    workflow_path=_WORKFLOW_DIR / "krea2_style_blend.json",
)


identity_edit = WorkflowNode(
    id="krea2_identity_edit",
    value="Identity Edit",
    description=(
        "Create from one identity image, or place that identity into an optional scene, "
        "using the community Identity Edit v1.2 adapter. This workflow is the "
        "identity-preserving tool; ordinary style reference is not."
    ),
    category="Krea 2",
    inputs=[
        _upload_cell(
            "identity",
            "identity_image",
            "Identity image (required)",
            "The face or subject identity to preserve.",
        ),
        _upload_cell(
            "scene",
            "scene_image",
            "Scene image (optional)",
            "Optional composition, pose, clothing, and environment reference.",
            required=False,
        ),
        _prompt_cell(
            label="Edit instruction",
            default=(
                "Create a polished waist-up image of this person seated beside a large "
                "window at dusk, turned slightly toward the camera with a relaxed posture. "
                "Preserve the exact facial identity, hair, skin tone, body proportions, "
                "and defining features. Dress them in a tailored charcoal jacket, with "
                "soft cool window light, a warm interior rim light, natural anatomy, "
                "coherent fabric and skin texture, and a softly layered background. If a "
                "scene reference is supplied, follow its pose, framing, clothing, lighting, "
                "and environment instead while retaining the same identity."
            ),
            description=(
                "Write a plain-English edit, such as ‘Place this person at the table, "
                "holding a drink.’ The grounded encoder injects both images itself, so "
                "do not type Picture or image tags. The identity image remains the anchor."
            ),
        ),
        *_local_common_inputs(
            default_aspect_ratio=_PORTRAIT_ASPECT_RATIO,
            default_steps=10,
            min_steps=8,
            max_steps=12,
            adapter_profile=True,
        ),
        _number_cell(
            node_id="patch",
            cell_id="identity_fidelity",
            label="Identity fidelity",
            default="4",
            minimum=0,
            maximum=100,
            step=0.1,
            description=(
                "How strongly the identity reference is preserved. Version 1.2 "
                "recommends starting at 4."
            ),
        ),
        _number_cell(
            node_id="positive",
            cell_id="grounding_px",
            label="Grounding pixels",
            default="1024",
            minimum=384,
            maximum=2048,
            step=64,
            description=(
                "Qwen3-VL reference-analysis resolution; 1024 is the established "
                "identity starting point."
            ),
        ),
    ],
    outputs=[_image_output("The generated identity-preserving PNG image.")],
    configure_prompt=_configure_identity_edit,
    configure_download=_configure_identity_edit_download,
    workflow_path=_WORKFLOW_DIR / "krea2_identity_edit.json",
)


character_restage = WorkflowNode(
    id="krea2_character_restage",
    value="Character Restage",
    description=(
        "Keep a character recognizable while changing pose, clothing, framing, and "
        "environment with the community Krea 2 ReID adapter. The validated 8-step "
        "INT8 engine keeps its published technical settings fixed."
    ),
    category="Krea 2",
    inputs=_reid_inputs(
        prompt_label="New scene and pose",
        prompt_default=(
            "A polished narrative illustration of the same character seated naturally "
            "at a small wooden table in a warmly lit public interior, lifting a glass in "
            "one hand while the other rests comfortably on the table. Use a three-quarter "
            "full-body composition, eye-level camera, natural anatomy and hands, warm "
            "practical light balanced by cool window fill, readable wood, glass, fabric, "
            "and metal textures, and a softly layered background. Preserve the "
            "recognizable face, hair, proportions, colors, and defining identity features."
        ),
        prompt_description=(
            "Describe the complete result in plain English: medium, pose, action, "
            "clothing, framing, lighting, and setting. Say ‘the same character’ when "
            "identity matters. Do not type Picture or image tags; the reference node "
            "injects them automatically."
        ),
        default_aspect_ratio=_PORTRAIT_ASPECT_RATIO,
    ),
    outputs=[_image_output("The generated, identity-guided PNG image.")],
    configure_prompt=_configure_character_restage,
    configure_download=_configure_character_restage_download,
    workflow_path=_WORKFLOW_DIR / "krea2_character_restage.json",
)


outfit_change = WorkflowNode(
    id="krea2_outfit_change",
    value="Outfit Change",
    description=(
        "Put a recognizable character in newly prompted clothing with the "
        "community ReID engine. This is a text-guided outfit change, not a pixel copy "
        "from a second garment image."
    ),
    category="Krea 2",
    inputs=_reid_inputs(
        prompt_label="Outfit direction",
        prompt_default=(
            "A polished full-body image of the same character wearing a tailored "
            "midnight-blue formal outfit with a structured jacket, layered silk details, "
            "subtle metal fastenings, and coordinated footwear. Use a relaxed standing "
            "pose, three-quarter camera angle, soft directional window light with a warm "
            "rim, coherent fabric folds and accessories, and a restrained interior "
            "background. Preserve the recognizable face, body proportions, skin tone, "
            "hair color, and defining identity features while changing the clothing "
            "and its palette."
        ),
        prompt_description=(
            "Describe the complete new outfit, material, silhouette, setting, and "
            "framing in plain English. Repeat what must stay recognizable. A close "
            "reference crop gives the prompt more freedom than a costume-heavy "
            "full-body reference. Do not type Picture or image tags."
        ),
        default_aspect_ratio=_PORTRAIT_ASPECT_RATIO,
    ),
    outputs=[_image_output("The generated outfit-change PNG image.")],
    configure_prompt=_configure_outfit_change,
    configure_download=_configure_outfit_change_download,
    workflow_path=_WORKFLOW_DIR / "krea2_character_restage.json",
)


pose_change = WorkflowNode(
    id="krea2_pose_change",
    value="Pose Change",
    description=(
        "Move a recognizable character into a newly prompted pose and composition "
        "with the community ReID engine. The pose is described with text rather "
        "than exact skeleton or pose-reference control."
    ),
    category="Krea 2",
    inputs=_reid_inputs(
        prompt_label="Pose and composition",
        prompt_default=(
            "A polished three-quarter image of the same character sitting naturally in "
            "a chair, torso turned slightly toward the viewer, shoulders relaxed, one "
            "hand resting open on a nearby table and both feet grounded. Use an eye-level "
            "camera, readable anatomy and foreshortening, soft directional light, coherent "
            "contact shadows, and an uncluttered layered interior. Preserve the "
            "recognizable face, hair, proportions, colors, and defining identity features "
            "while changing the pose and framing."
        ),
        prompt_description=(
            "Describe body position, gesture, camera angle, crop, and nearby props. "
            "Use concrete anatomy and spatial language. This is prompt-guided pose "
            "generation, not exact OpenPose control. Do not type Picture or image tags."
        ),
        default_aspect_ratio=_PORTRAIT_ASPECT_RATIO,
    ),
    outputs=[_image_output("The generated pose-change PNG image.")],
    configure_prompt=_configure_pose_change,
    configure_download=_configure_pose_change_download,
    workflow_path=_WORKFLOW_DIR / "krea2_character_restage.json",
)


feature_edit = WorkflowNode(
    id="krea2_feature_edit",
    value="Feature Edit",
    description=(
        "Change a prompted visible feature while retaining the broader character "
        "identity with the community ReID engine. Large changes can still drift, "
        "so the default asks for one bounded edit at a time."
    ),
    category="Krea 2",
    inputs=_reid_inputs(
        prompt_label="Feature edit",
        prompt_default=(
            "A polished close portrait of the same character with a shorter layered "
            "hairstyle while preserving the original hair color, facial structure, skin "
            "tone, eyes, expression, and every other defining identity feature. Use a "
            "clean three-quarter camera angle, soft directional portrait light, natural "
            "skin and hair texture, restrained contrast, and a simple softly blurred "
            "background so the single requested change remains unambiguous."
        ),
        prompt_description=(
            "Name one visible feature to change and explicitly name the important "
            "features that must stay unchanged. Small, isolated edits are more reliable "
            "than changing the face wholesale. Do not type Picture or image tags."
        ),
        default_aspect_ratio=_PORTRAIT_ASPECT_RATIO,
    ),
    outputs=[_image_output("The generated feature-edit PNG image.")],
    configure_prompt=_configure_feature_edit,
    configure_download=_configure_feature_edit_download,
    workflow_path=_WORKFLOW_DIR / "krea2_character_restage.json",
)


character_restyle = WorkflowNode(
    id="krea2_character_restyle",
    value="Character Restyle",
    description=(
        "Translate a recognizable character into a style described in text with the "
        "community ReID engine. Use Style Reference when an uploaded artwork, "
        "rather than a written art direction, should drive the visual language."
    ),
    category="Krea 2",
    inputs=_reid_inputs(
        prompt_label="Art direction",
        prompt_default=(
            "A hand-drawn 1990s television-anime cel illustration of the same character, "
            "crisp inked outlines, flat cel shading, restrained highlights, "
            "a hand-painted background, and subtle analog film grain. Preserve the "
            "recognizable face, skin tone, hair identity, silhouette, and defining "
            "features while allowing the requested artistic palette to change."
        ),
        prompt_description=(
            "Describe the target medium, era, linework, shading, palette, background, "
            "and finish in plain English. This is prompt-guided restyling; it does not "
            "copy the style of a second image. Do not type Picture or image tags."
        ),
        default_aspect_ratio=_PORTRAIT_ASPECT_RATIO,
    ),
    outputs=[_image_output("The generated character-restyle PNG image.")],
    configure_prompt=_configure_character_restyle,
    configure_download=_configure_character_restyle_download,
    workflow_path=_WORKFLOW_DIR / "krea2_character_restage.json",
)


WORKFLOWS = (
    generate,
    style_reference,
    style_blend,
    identity_edit,
    character_restage,
    outfit_change,
    pose_change,
    feature_edit,
    character_restyle,
)
WORKFLOW_BY_ID = {workflow.id: workflow for workflow in WORKFLOWS}
