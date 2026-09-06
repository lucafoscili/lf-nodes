"""Focused MiniMax H3 Workflow Runner cards over reusable local graphs.

The cards share base, anchored-guide, and reference graphs while keeping public
controls task-oriented. Canvas geometry is selected from a curated native-size
map, output is fixed at 24 fps, duration is selected directly on H3's 17k+5
frame grid, and the validated quality profile owns its sampler, scheduler, and
step count.
"""

from __future__ import annotations

import math
import re
from functools import partial
from pathlib import Path
from typing import Any, Callable, Dict, NamedTuple

from ..prompts import compose_base_prompt, compose_full_reference_prompt
from ..services.registry import (
    InputValidationError,
    WorkflowCardPresentation,
    WorkflowCell,
    WorkflowHeroImage,
    WorkflowInputOptionRequirement,
    WorkflowModelAsset,
    WorkflowNode,
)
from .minimax_h3_profiles import (
    MiniMaxH3ExecutionProfile,
    NATIVE_MAX_EDGE,
    NATIVE_MAX_PIXELS,
    TURBO_V4_6STEP_LORA,
    resolve_h3_execution_profile,
)
from .utils import (
    choice as _choice,
    has_input_value as _has_image,
    integer as _integer,
    require_input_value as _require_image,
    required_text as _required_text,
    resolve_load_image_reference,
)


_FPS = 24
_CANVAS_MULTIPLE = 32
_MIN_TRAINED_FRAMES = 124
_MAX_SEED = (1 << 53) - 1
_MAX_REFERENCE_IMAGES = 9
_SPRITE_FRAME_COUNT = 24
_DEFAULT_SPRITE_SIZE = 256
_DEFAULT_SPRITE_ALPHA_HEIGHT = 224
_DEFAULT_SPRITE_REFERENCE_FRAME = 0
_DEFAULT_SPRITE_BOTTOM_PADDING = 16
_DEFAULT_INTENDED_FPS = 12
_TURNAROUND_VIEW_COUNT = 4
_TURNAROUND_CANVAS_SIZE = 1024
_TURNAROUND_ALPHA_HEIGHT = 900
_TURNAROUND_BOTTOM_PADDING = 48
_TURNAROUND_PAD_COLOR = "E6E6E6"
_DIRECTED_VIEW_TAIL_FRACTION = 0.25
_DIRECTED_VIEW_ANALYSIS_RESOLUTION = 96

_RMBG2_MODEL_ASSETS = (
    WorkflowModelAsset(
        label="VNCCS RMBG-2.0 model",
        relative_paths=(
            "RMBG/RMBG-2.0/config.json",
            "RMBG/RMBG-2.0/model.safetensors",
            "RMBG/RMBG-2.0/birefnet.py",
            "RMBG/RMBG-2.0/BiRefNet_config.py",
        ),
    ),
)
_TURBO_V4_MODEL_PATH = "loras/" + TURBO_V4_6STEP_LORA.replace("\\", "/")
_TURBO_V4_OPTION_REQUIREMENT = WorkflowInputOptionRequirement(
    input_id="execution_profile",
    option_value="turbo_preview",
    required_node_types=("MiniMaxH3TurboLoRA", "MiniMaxH3TurboSampler"),
    required_model_assets=(
        WorkflowModelAsset(
            label="MiniMax H3 Turbo v4 LoRA",
            relative_paths=(_TURBO_V4_MODEL_PATH,),
        ),
    ),
)

_GUIDE_INPUTS = (
    ("guide_image_1", "guide_frame_1", "source_guide_1", "guide_1", 41),
    ("guide_image_2", "guide_frame_2", "source_guide_2", "guide_2", 82),
    ("guide_image_3", "guide_frame_3", "source_guide_3", "guide_3", 103),
)

# Every size is explicit, aligned to 32, and no larger than the native
# 768x1344 pixel budget.  21:9 legitimately has a longer edge while retaining
# the same 1,032,192-pixel budget, so max-edge validation would reject it
# incorrectly.
_ASPECT_RATIO_SIZES = {
    "16:9": (1344, 768),
    "4:3": (1024, 768),
    "1:1": (768, 768),
    "3:4": (768, 1024),
    "9:16": (768, 1344),
    "21:9": (1536, 672),
}
_ASPECT_RATIO_OPTIONS = tuple(
    (
        aspect_ratio,
        f"{aspect_ratio} - {width}x{height}",
        f"Native-size {width}x{height} canvas, aligned to {_CANVAS_MULTIPLE} pixels.",
    )
    for aspect_ratio, (width, height) in _ASPECT_RATIO_SIZES.items()
)

# All exposed choices are exact 17k+5 frame counts inside the documented
# approximately 5-15 second trained range.
_DURATION_OPTIONS = (
    ("124", "5.17 seconds - 124 frames", "124 frames at 24 fps."),
    ("192", "8 seconds - 192 frames", "192 frames at 24 fps."),
    ("243", "10.12 seconds - 243 frames", "243 frames at 24 fps."),
    ("362", "15.08 seconds - 362 frames", "362 frames at 24 fps."),
)
_DURATION_IDS = tuple(option[0] for option in _DURATION_OPTIONS)
_ANIMATE_EXECUTION_PROFILE_OPTIONS = (
    (
        "turbo_preview",
        "Fast · Turbo 6",
        "Six sampling passes with the community v4 Turbo recipe. It is much "
        "faster, but fine detail and motion consistency may be weaker.",
        "fast",
    ),
    (
        "kitchen_quality",
        "Baseline · Kitchen 20",
        "Twenty sampling passes with Kitchen attention and the base H3 model. "
        "Use this as the full-speed reference when judging the Fast result.",
        "baseline",
    ),
)
_ANIMATE_EXECUTION_PROFILE_IDS = tuple(
    option[0] for option in _ANIMATE_EXECUTION_PROFILE_OPTIONS
)

_REFERENCE_TAG = re.compile(
    r"<\s*(picture|video|audio)\s+(\d+)\s*>", re.IGNORECASE
)
_REFERENCE_LIKE_TAG = re.compile(
    r"<\s*(?:picture|video|audio)[^>]*(?:>|$)", re.IGNORECASE
)
_PROMPT_SECTION_NODES = (
    ("subject_definitions", "prompt_subject_definitions"),
    ("summary", "prompt_summary"),
    ("retention_analysis", "prompt_retention_analysis"),
    ("detailed_description", "prompt_detailed_description"),
    ("overall_soundscape", "prompt_overall_soundscape"),
    ("non_diegetic_music", "prompt_non_diegetic_music"),
)

_DEFAULT_DIALOGUE = "No spoken dialogue."
_DEFAULT_SOUNDSCAPE = "Natural ambience and restrained foley appropriate to the scene."
_DEFAULT_MUSIC = "N/A"
_TURNAROUND_DIRECTION_DEFAULT = (
    "One continuous technical character turntable. Keep the subject completely "
    "stationary in a neutral full-body stance with unchanged expression, anatomy, "
    "clothing, equipment, materials, and proportions. The camera performs one smooth "
    "clockwise 360-degree orbit at constant speed and eye-level height. Follow this "
    "camera-position convention exactly: front at the opening frame, camera on the "
    "subject's right side showing the subject's right profile at one quarter, back at "
    "one half, camera on the subject's left side showing the subject's left profile at "
    "three quarters, and front again at the final frame. "
    "Use a locked focal length, camera distance, subject scale, vertical alignment, "
    "plain neutral light-gray studio background, and even diffuse lighting. No cuts, "
    "camera roll, zoom, body motion, added elements, disappearing details, or dialogue."
)

_DIRECTED_VIEW_OPTIONS = (
    (
        "subject_right",
        "Subject right",
        "Move the camera to the subject's anatomical right side. In an ordinary "
        "front view, this is the side shown on the left of the image.",
    ),
    (
        "back",
        "Back",
        "Move the camera behind the subject for a strict rear view; front-facing "
        "features should no longer be visible.",
    ),
    (
        "subject_left",
        "Subject left",
        "Move the camera to the subject's anatomical left side. In an ordinary "
        "front view, this is the side shown on the right of the image.",
    ),
)
_DIRECTED_VIEW_IDS = tuple(option[0] for option in _DIRECTED_VIEW_OPTIONS)
_DIRECTED_VIEW_RETENTION_DEFAULT = (
    "Preserve the subject's recognizable identity, facial structure, body proportions, "
    "hairstyle, clothing, materials, colors, accessories, equipment, and every visible "
    "left-right asymmetry. Keep the same neutral full-body stance and leave generous "
    "clear margin around the complete silhouette."
)


class _CommonSettings(NamedTuple):
    aspect_ratio: str
    width: int
    height: int
    frames: int
    seed: int
    profile: MiniMaxH3ExecutionProfile


class _ImageGuide(NamedTuple):
    image_field: str
    source_node: str
    guide_node: str
    frame_index: int


class _AnchoredSpriteSettings(NamedTuple):
    common: _CommonSettings
    compiled_prompt: str
    sprite_size: int
    sprite_alpha_height: int
    sprite_reference_frame: int
    sprite_bottom_padding: int
    intended_fps: int


class _BaseCardSpec(NamedTuple):
    workflow_id: str
    title: str
    output_folder: str
    description: str
    direction_label: str
    direction_default: str
    direction_help: str
    instruction: str
    first_frame: tuple[str, str, str] | None
    last_frame: tuple[str, str, str] | None
    default_aspect_ratio: str
    card: WorkflowCardPresentation | None = None


class _ReferenceInputSpec(NamedTuple):
    field_id: str
    label: str
    help: str
    required: bool


class _ReferenceCardSpec(NamedTuple):
    workflow_id: str
    title: str
    output_folder: str
    description: str
    direction_label: str
    direction_default: str
    direction_help: str
    references: tuple[_ReferenceInputSpec, ...]
    prompt_fields: Callable[[int], tuple[str, str, str]]
    default_aspect_ratio: str
    card: WorkflowCardPresentation | None = None


def _optional_text(inputs: Dict[str, Any], name: str, default: str = "") -> str:
    value = inputs.get(name, default)
    if value is None:
        return ""
    if not isinstance(value, str):
        raise InputValidationError(name)
    return value.strip()


def _bounded_float(
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


def _validate_hard_bound_input(
    inputs: Dict[str, Any], name: str, expected: str
) -> None:
    """Reject stale/headless attempts to override a hidden fixed setting."""

    if name in inputs and inputs[name] != expected:
        raise InputValidationError(name)


def _common_settings(
    inputs: Dict[str, Any],
    *,
    family: str,
    default_aspect_ratio: str,
    execution_profile_ids: tuple[str, ...] = ("kitchen_quality",),
) -> _CommonSettings:
    profile_id = _choice(
        inputs,
        "execution_profile",
        "kitchen_quality",
        execution_profile_ids,
    )
    aspect_ratio = _choice(
        inputs,
        "aspect_ratio",
        default_aspect_ratio,
        tuple(_ASPECT_RATIO_SIZES),
    )
    width, height = _ASPECT_RATIO_SIZES[aspect_ratio]
    if (
        width % _CANVAS_MULTIPLE
        or height % _CANVAS_MULTIPLE
        or width > NATIVE_MAX_EDGE
        or height > NATIVE_MAX_EDGE
        or width * height > NATIVE_MAX_PIXELS
    ):
        raise RuntimeError(
            f"Unsafe MiniMax H3 native canvas mapping for {aspect_ratio}: "
            f"{width}x{height}."
        )

    duration_frames = _choice(
        inputs,
        "duration_frames",
        "124",
        _DURATION_IDS,
    )
    frames = int(duration_frames)
    if frames < _MIN_TRAINED_FRAMES or frames % 17 != 5:
        raise RuntimeError(f"Invalid MiniMax H3 frame preset: {frames}.")

    seed = _integer(inputs, "seed", 42, minimum=0, maximum=_MAX_SEED)
    profile = resolve_h3_execution_profile(profile_id, family=family)
    if profile.steps is None:
        raise RuntimeError(
            f"Focused MiniMax H3 cards require a profile-owned step count: {profile.id}."
        )
    return _CommonSettings(
        aspect_ratio=aspect_ratio,
        width=width,
        height=height,
        frames=frames,
        seed=seed,
        profile=profile,
    )


def _apply_execution_profile(
    prompt: Dict[str, Any], profile: MiniMaxH3ExecutionProfile
) -> None:
    """Apply the shared sampler, scheduler, and accelerator recipe."""

    prompt["sampler_select"]["inputs"]["sampler_name"] = "res_multistep"
    prompt["scheduler"]["inputs"]["scheduler"] = "simple"
    prompt["attention_backend"]["inputs"]["attention"] = (
        "comfy kitchen attention"
    )
    model_output = ["attention_backend", 0]

    if profile.id == "kitchen_quality" and profile.accelerator == "kitchen":
        prompt.pop("turbo_lora", None)
        prompt.pop("turbo_sampler", None)
        sampler_output = ["sampler_select", 0]
    elif profile.id == "turbo_preview" and profile.accelerator == "turbo":
        prompt["turbo_lora"] = {
            "inputs": {
                "model": ["attention_backend", 0],
                "lora_name": TURBO_V4_6STEP_LORA,
                "strength": 1.0,
                "low_vram": False,
            },
            "class_type": "MiniMaxH3TurboLoRA",
            "_meta": {"title": "Apply the six-step H3 Turbo v4 LoRA"},
        }
        prompt["turbo_sampler"] = {
            "inputs": {},
            "class_type": "MiniMaxH3TurboSampler",
            "_meta": {"title": "Use the matching H3 Turbo sampler"},
        }
        model_output = ["turbo_lora", 0]
        sampler_output = ["turbo_sampler", 0]
    else:
        raise RuntimeError(
            f"Unsupported focused MiniMax H3 execution profile: {profile.id}."
        )

    prompt["guider"]["inputs"]["model"] = list(model_output)
    prompt["scheduler"]["inputs"]["model"] = list(model_output)
    prompt["scheduler"]["inputs"]["steps"] = profile.steps
    prompt["sample"]["inputs"]["sampler"] = list(sampler_output)


def _apply_common_graph_settings(
    prompt: Dict[str, Any],
    settings: _CommonSettings,
    *,
    output_folder: str,
    reference_count: int | None = None,
) -> None:
    prompt["h3"]["inputs"].update(
        {
            "width": settings.width,
            "height": settings.height,
            "length": settings.frames,
        }
    )
    prompt["noise"]["inputs"]["noise_seed"] = settings.seed
    prompt["model_device"]["inputs"]["device"] = "default"
    prompt["clip_device"]["inputs"]["device"] = "default"
    prompt["video_vae_device"]["inputs"]["device"] = "default"
    prompt["audio_vae_device"]["inputs"]["device"] = "default"
    prompt["create_video"]["inputs"]["fps"] = float(_FPS)

    reference_suffix = (
        f"-refs{reference_count}" if reference_count is not None else ""
    )
    prompt["save"]["inputs"]["filename_prefix"] = (
        f"LF_Nodes/MiniMaxH3/{output_folder}/{settings.profile.id}/"
        f"seed-{settings.seed}{reference_suffix}-f{settings.frames}"
    )


def _multimodal_description(direction: str, dialogue: str) -> str:
    if dialogue:
        return f"{direction}\n\nDialogue:\n{dialogue}"
    return direction


def _first_last_instruction(frames: int) -> str:
    return (
        "How the reference pictures align with the target video — Picture 1 "
        "(from Shot 1) aligns with the 0.00-second mark of the target video; "
        "Picture 2 (from Shot 1) aligns with the "
        f"{frames / _FPS:.2f}-second mark of the target video."
    )


def _directed_view_description(target_view: str, retention: str) -> str:
    """Build one strict, generic front-to-cardinal camera instruction."""

    target_instructions = {
        "subject_right": (
            "Move on one horizontal 90-degree arc toward the subject's anatomical "
            "right side, which normally appears on the left of the opening image. "
            "At the target, show a strict right profile: the nose points toward the "
            "right edge and the right cheek, shoulder, hip, and leg are the near side."
        ),
        "back": (
            "Move on one horizontal 180-degree arc via the subject's anatomical right "
            "side. At the target, show a strict symmetrical rear view: the face, eyes, "
            "nose, mouth, chest, and other front-facing details are not visible."
        ),
        "subject_left": (
            "Move on one horizontal 90-degree arc toward the subject's anatomical left "
            "side, which normally appears on the right of the opening image. At the "
            "target, show a strict left profile: the nose points toward the left edge "
            "and the left cheek, shoulder, hip, and leg are the near side."
        ),
    }
    target = target_instructions[target_view]
    return (
        "Create one continuous technical character-view capture from the supplied "
        "frontal opening image. Use that image as the identity and appearance authority. "
        f"{retention}\n\n"
        "The subject remains completely stationary; only the camera moves. "
        f"{target} The motion is monotonic: never reverse, overshoot, mirror, switch "
        "sides, zoom, roll, tilt, or change focal length, camera height, distance, "
        "subject scale, or vertical alignment. Reach the exact target view during the "
        "final fifth of the clip, then hold both camera and subject perfectly still "
        "through the final frame so a stable still can be selected.\n\n"
        "Keep the complete subject and all equipment inside frame against one plain "
        "neutral light-gray studio background with even diffuse lighting. No cuts, "
        "body motion, secondary motion, reframing, added elements, disappearing "
        "details, dialogue, or music."
    )


def _add_neutral_h3_source(
    prompt: Dict[str, Any],
    *,
    source_reference: str,
    settings: _CommonSettings,
) -> None:
    """Fit an RGBA upload without stretching and flatten it onto neutral gray."""

    prompt["source_first"]["inputs"]["image"] = source_reference
    prompt.pop("source_last", None)
    prompt["turnaround_source_rgba"] = {
        "inputs": {
            "image": ["source_first", 0],
            "alpha": ["source_first", 1],
        },
        "class_type": "JoinImageWithAlpha",
        "_meta": {"title": "Preserve uploaded source transparency"},
    }
    prompt["turnaround_fit"] = {
        "inputs": {
            "image": ["turnaround_source_rgba", 0],
            "height": settings.height,
            "width": settings.width,
            "resize_method": "bicubic",
            "resize_mode": "pad",
            "pad_color": _TURNAROUND_PAD_COLOR,
        },
        "class_type": "LF_ResizeImageToDimension",
        "_meta": {"title": "Fit the identity anchor without stretching"},
    }
    prompt["turnaround_split"] = {
        "inputs": {"image": ["turnaround_fit", 0]},
        "class_type": "SplitImageWithAlpha",
        "_meta": {"title": "Separate fitted RGB and transparency"},
    }
    prompt["turnaround_opacity"] = {
        "inputs": {"mask": ["turnaround_split", 1]},
        "class_type": "InvertMask",
        "_meta": {"title": "Convert transparency to source opacity"},
    }
    prompt["turnaround_background"] = {
        "inputs": {
            "width": settings.width,
            "height": settings.height,
            "batch_size": 1,
            "color": int(_TURNAROUND_PAD_COLOR, 16),
        },
        "class_type": "EmptyImage",
        "_meta": {"title": "Create the neutral H3 source background"},
    }
    prompt["turnaround_composite"] = {
        "inputs": {
            "destination": ["turnaround_background", 0],
            "source": ["turnaround_split", 0],
            "x": 0,
            "y": 0,
            "resize_source": False,
            "mask": ["turnaround_opacity", 0],
        },
        "class_type": "ImageCompositeMasked",
        "_meta": {"title": "Flatten source alpha onto neutral gray"},
    }


def _active_image_guides(
    inputs: Dict[str, Any], frames: int
) -> list[_ImageGuide]:
    guides: list[_ImageGuide] = []
    for image_field, frame_field, source_node, guide_node, default_frame in _GUIDE_INPUTS:
        if not _has_image(inputs, image_field):
            continue
        frame_index = _integer(
            inputs,
            frame_field,
            default_frame,
            minimum=1,
            maximum=frames - 2,
        )
        guides.append(
            _ImageGuide(
                image_field=image_field,
                source_node=source_node,
                guide_node=guide_node,
                frame_index=frame_index,
            )
        )

    if len({guide.frame_index for guide in guides}) != len(guides):
        raise ValueError("Intermediate guide frame indices must be distinct.")
    return guides


def _anchored_sprite_settings(inputs: Dict[str, Any]) -> _AnchoredSpriteSettings:
    direction = _required_text(inputs, "direction")
    dialogue = _optional_text(inputs, "dialogue", _DEFAULT_DIALOGUE)
    soundscape = _optional_text(inputs, "soundscape", _DEFAULT_SOUNDSCAPE)
    music = _optional_text(inputs, "music", _DEFAULT_MUSIC)
    common = _common_settings(
        inputs,
        family="fl2va",
        default_aspect_ratio="1:1",
    )
    sprite_size = _integer(
        inputs,
        "sprite_size",
        _DEFAULT_SPRITE_SIZE,
        minimum=32,
        maximum=1024,
    )
    sprite_alpha_height = _integer(
        inputs,
        "sprite_alpha_height",
        _DEFAULT_SPRITE_ALPHA_HEIGHT,
        minimum=1,
        maximum=1024,
    )
    sprite_reference_frame = _integer(
        inputs,
        "sprite_reference_frame",
        _DEFAULT_SPRITE_REFERENCE_FRAME,
        minimum=0,
        maximum=_SPRITE_FRAME_COUNT - 1,
    )
    sprite_bottom_padding = _integer(
        inputs,
        "sprite_bottom_padding",
        _DEFAULT_SPRITE_BOTTOM_PADDING,
        minimum=0,
        maximum=1023,
    )
    if sprite_alpha_height + sprite_bottom_padding > sprite_size:
        raise ValueError(
            "Sprite content height plus bottom padding must be less than or "
            "equal to the sprite canvas size."
        )
    intended_fps = _integer(
        inputs,
        "intended_fps",
        _DEFAULT_INTENDED_FPS,
        minimum=1,
        maximum=60,
    )
    compiled_prompt = compose_base_prompt(
        instruction=_first_last_instruction(common.frames),
        integrated_multimodal_description=_multimodal_description(
            direction, dialogue
        ),
        overall_soundscape=soundscape,
        non_diegetic_music=music,
    )
    return _AnchoredSpriteSettings(
        common=common,
        compiled_prompt=compiled_prompt,
        sprite_size=sprite_size,
        sprite_alpha_height=sprite_alpha_height,
        sprite_reference_frame=sprite_reference_frame,
        sprite_bottom_padding=sprite_bottom_padding,
        intended_fps=intended_fps,
    )


def _remove_inactive_anchored_guides(
    prompt: Dict[str, Any], active_guide_nodes: set[str]
) -> None:
    for _image_field, _frame_field, source_node, guide_node, _default in _GUIDE_INPUTS:
        if guide_node in active_guide_nodes:
            continue
        prompt.pop(source_node, None)
        prompt.pop(guide_node, None)


def _apply_anchored_sprite_graph_settings(
    prompt: Dict[str, Any], settings: _AnchoredSpriteSettings
) -> None:
    prompt["h3"]["inputs"]["prompt"] = settings.compiled_prompt
    _apply_execution_profile(prompt, settings.common.profile)
    _apply_common_graph_settings(
        prompt,
        settings.common,
        output_folder="AnchoredSpriteLoop",
    )
    prompt["sprite_sampler"]["inputs"].update(
        {
            "target_count": _SPRITE_FRAME_COUNT,
            "loop_endpoint_policy": "exclude_final_endpoint",
            "source_fps": float(_FPS),
            "intended_fps": float(settings.intended_fps),
        }
    )
    prompt["remove_background"]["inputs"].update(
        {
            "model": "RMBG-2.0",
            "sensitivity": 1.0,
            "process_res": 1024,
            "mask_blur": 0,
            "mask_offset": 0,
            "invert_output": False,
            "refine_foreground": False,
            "background": "Alpha",
        }
    )
    prompt["sprite_normalize"]["inputs"].update(
        {
            "canvas_width": settings.sprite_size,
            "canvas_height": settings.sprite_size,
            "target_reference_alpha_height": settings.sprite_alpha_height,
            "reference_frame_index": settings.sprite_reference_frame,
            "bottom_padding": settings.sprite_bottom_padding,
        }
    )
    prompt["sprite_grid"]["inputs"].update(
        {
            "cell_width": settings.sprite_size,
            "cell_height": settings.sprite_size,
            "gap_px": 0,
            "background": "transparent",
            "show_headers": False,
            "title": "",
        }
    )
    output_prefix = prompt["save"]["inputs"]["filename_prefix"]
    normalization_suffix = (
        f"content-{settings.sprite_alpha_height}px-"
        f"bottom-{settings.sprite_bottom_padding}px-"
        f"ref-{settings.sprite_reference_frame}"
    )
    prompt["save_frames"]["inputs"]["filename_prefix"] = (
        f"{output_prefix}/frames-{settings.sprite_size}px-"
        f"{normalization_suffix}-{settings.intended_fps}fps"
    )
    prompt["save_atlas"]["inputs"]["filename_prefix"] = (
        f"{output_prefix}/atlas-6x4-{settings.sprite_size}px-"
        f"{normalization_suffix}-{settings.intended_fps}fps"
    )


def _configure_base_card(
    prompt: Dict[str, Any],
    inputs: Dict[str, Any],
    *,
    spec: _BaseCardSpec,
) -> None:
    direction = _required_text(inputs, "direction")
    dialogue = _optional_text(inputs, "dialogue", _DEFAULT_DIALOGUE)
    soundscape = _optional_text(inputs, "soundscape", _DEFAULT_SOUNDSCAPE)
    music = _optional_text(inputs, "music", _DEFAULT_MUSIC)
    if spec.first_frame is not None:
        _require_image(inputs, spec.first_frame[0])
    if spec.last_frame is not None:
        _require_image(inputs, spec.last_frame[0])

    settings = _common_settings(
        inputs,
        family="fl2va",
        default_aspect_ratio=spec.default_aspect_ratio,
        execution_profile_ids=(
            _ANIMATE_EXECUTION_PROFILE_IDS
            if spec.workflow_id == "minimax_h3_animate_image"
            else ("kitchen_quality",)
        ),
    )
    instruction = spec.instruction
    if spec.last_frame is not None:
        instruction = _first_last_instruction(settings.frames)
    compiled_prompt = compose_base_prompt(
        instruction=instruction,
        integrated_multimodal_description=_multimodal_description(
            direction, dialogue
        ),
        overall_soundscape=soundscape,
        non_diegetic_music=music,
    )

    first_reference = (
        resolve_load_image_reference(inputs, spec.first_frame[0])
        if spec.first_frame is not None
        else None
    )
    last_reference = (
        resolve_load_image_reference(inputs, spec.last_frame[0])
        if spec.last_frame is not None
        else None
    )

    h3_inputs = prompt["h3"]["inputs"]
    h3_inputs["prompt"] = compiled_prompt
    if first_reference is None:
        prompt.pop("source_first", None)
        h3_inputs.pop("first_frame", None)
    else:
        prompt["source_first"]["inputs"]["image"] = first_reference
        h3_inputs["first_frame"] = ["source_first", 0]
    if last_reference is None:
        prompt.pop("source_last", None)
        h3_inputs.pop("last_frame", None)
    else:
        prompt["source_last"]["inputs"]["image"] = last_reference
        h3_inputs["last_frame"] = ["source_last", 0]

    _apply_execution_profile(prompt, settings.profile)
    _apply_common_graph_settings(
        prompt,
        settings,
        output_folder=spec.output_folder,
    )


def _configure_directed_view(
    prompt: Dict[str, Any], inputs: Dict[str, Any], *, resolve_upload: bool
) -> None:
    """Render one front-to-cardinal camera move and save one lossless still."""

    target_view = _choice(
        inputs,
        "target_view",
        "subject_right",
        _DIRECTED_VIEW_IDS,
    )
    retention = _required_text(inputs, "retention_details")
    tail_fraction = _bounded_float(
        inputs,
        "tail_fraction",
        _DIRECTED_VIEW_TAIL_FRACTION,
        minimum=0.01,
        maximum=1.0,
    )
    analysis_max_edge = _integer(
        inputs,
        "analysis_max_edge",
        _DIRECTED_VIEW_ANALYSIS_RESOLUTION,
        minimum=8,
        maximum=1024,
    )
    settings = _common_settings(
        inputs,
        family="fl2va",
        default_aspect_ratio="9:16",
        execution_profile_ids=_ANIMATE_EXECUTION_PROFILE_IDS,
    )
    if resolve_upload:
        _require_image(inputs, "source_image")
        source_reference = resolve_load_image_reference(inputs, "source_image")
    else:
        source_reference = prompt["source_first"]["inputs"]["image"]

    compiled_prompt = compose_base_prompt(
        instruction=(
            "For the target video, at 0.00 seconds into the target video, "
            "<Picture 1> (from [Shot 1]) is fully referenced."
        ),
        integrated_multimodal_description=_directed_view_description(
            target_view,
            retention,
        ),
        overall_soundscape="N/A",
        non_diegetic_music="N/A",
    )

    _add_neutral_h3_source(
        prompt,
        source_reference=source_reference,
        settings=settings,
    )
    prompt["h3"]["inputs"].update(
        {
            "prompt": compiled_prompt,
            "first_frame": ["turnaround_composite", 0],
        }
    )
    prompt["h3"]["inputs"].pop("last_frame", None)
    _remove_inactive_anchored_guides(prompt, set())
    prompt["guider"]["inputs"]["conditioning"] = ["h3", 0]
    _apply_execution_profile(prompt, settings.profile)
    _apply_common_graph_settings(
        prompt,
        settings,
        output_folder=f"DirectedView/{target_view}",
    )

    for node_id in (
        "sprite_sampler",
        "remove_background",
        "verify_rmbg_alpha",
        "rmbg_transparency_mask",
        "validated_cutout",
        "sprite_normalize",
        "sprite_grid",
        "save_frames",
        "save_atlas",
        "display_sampling_receipt",
        "display_normalization_receipt",
    ):
        prompt.pop(node_id, None)

    prompt["settled_selector"] = {
        "inputs": {
            "image": ["decode_video", 0],
            "tail_fraction": tail_fraction,
            "analysis_max_edge": analysis_max_edge,
        },
        "class_type": "LF_SelectSettledImageFrame",
        "_meta": {
            "title": "Select the least-moving frame from the settled tail"
        },
    }
    output_prefix = prompt["save"]["inputs"]["filename_prefix"]
    prompt["save_view"] = {
        "inputs": {
            "images": ["settled_selector", 0],
            "filename_prefix": f"{output_prefix}/selected-{target_view}",
        },
        "class_type": "SaveImage",
        "_meta": {"title": "Save one lossless selected cardinal view"},
    }
    prompt["display_selection_receipt"] = {
        "inputs": {
            "json_input": ["settled_selector", 3],
            "ui_widget": "",
        },
        "class_type": "LF_DisplayJSON",
        "_meta": {"title": "Publish settled-frame selection receipt"},
    }


def _configure_directed_view_run(
    prompt: Dict[str, Any], inputs: Dict[str, Any]
) -> None:
    _configure_directed_view(prompt, inputs, resolve_upload=True)


def _configure_directed_view_download(
    prompt: Dict[str, Any], inputs: Dict[str, Any]
) -> None:
    _configure_directed_view(prompt, inputs, resolve_upload=False)


def _configure_character_turnaround(
    prompt: Dict[str, Any], inputs: Dict[str, Any], *, resolve_upload: bool
) -> None:
    """Build one closed Kitchen-quality orbit and publish four ordered view images."""

    direction = _required_text(inputs, "direction")
    content_height = _integer(
        inputs,
        "content_height",
        _TURNAROUND_ALPHA_HEIGHT,
        minimum=512,
        maximum=_TURNAROUND_ALPHA_HEIGHT,
    )
    settings = _common_settings(
        inputs,
        family="fl2va",
        default_aspect_ratio="9:16",
    )
    if resolve_upload:
        _require_image(inputs, "source_image")
        source_reference = resolve_load_image_reference(inputs, "source_image")
    else:
        source_reference = prompt["source_first"]["inputs"]["image"]

    compiled_prompt = compose_base_prompt(
        instruction=_first_last_instruction(settings.frames),
        integrated_multimodal_description=_multimodal_description(
            direction, _DEFAULT_DIALOGUE
        ),
        overall_soundscape="N/A",
        non_diegetic_music="N/A",
    )

    _add_neutral_h3_source(
        prompt,
        source_reference=source_reference,
        settings=settings,
    )
    prompt["h3"]["inputs"].update(
        {
            "prompt": compiled_prompt,
            "first_frame": ["turnaround_composite", 0],
            "last_frame": ["turnaround_composite", 0],
        }
    )

    _remove_inactive_anchored_guides(prompt, set())
    prompt["guider"]["inputs"]["conditioning"] = ["h3", 0]
    _apply_execution_profile(prompt, settings.profile)
    _apply_common_graph_settings(
        prompt,
        settings,
        output_folder="CharacterTurnaround",
    )

    prompt["sprite_sampler"]["inputs"].update(
        {
            "target_count": _TURNAROUND_VIEW_COUNT,
            "loop_endpoint_policy": "exclude_final_endpoint",
            "source_fps": float(_FPS),
            "intended_fps": 1.0,
            "sampling_basis": "visual_motion",
        }
    )
    prompt["sprite_sampler"]["_meta"]["title"] = (
        "Select four visual-motion angle candidates"
    )
    prompt["remove_background"]["inputs"].update(
        {
            "model": "RMBG-2.0",
            "sensitivity": 1.0,
            "process_res": 1024,
            "mask_blur": 0,
            "mask_offset": 0,
            "invert_output": False,
            "refine_foreground": False,
            "background": "Alpha",
        }
    )
    prompt["sprite_normalize"]["inputs"].update(
        {
            "canvas_width": _TURNAROUND_CANVAS_SIZE,
            "canvas_height": _TURNAROUND_CANVAS_SIZE,
            "target_reference_alpha_height": content_height,
            "reference_frame_index": 0,
            "bottom_padding": _TURNAROUND_BOTTOM_PADDING,
        }
    )
    prompt["sprite_normalize"]["_meta"]["title"] = (
        "Normalize all four views from the front-view scale and pivot"
    )
    prompt["sprite_grid"]["inputs"].update(
        {
            "cell_width": 512,
            "cell_height": 512,
            "gap_px": 8,
            "background": "transparent",
            "show_headers": True,
            "title": "Character turnaround candidates",
            "dataset": {
                "columns": [
                    {"id": "front", "title": "FRONT CANDIDATE"},
                    {
                        "id": "subject_right",
                        "title": "SUBJECT-RIGHT CANDIDATE",
                    },
                    {"id": "back", "title": "BACK CANDIDATE"},
                    {
                        "id": "subject_left",
                        "title": "SUBJECT-LEFT CANDIDATE",
                    },
                ],
                "nodes": [{"id": "views", "value": ""}],
            },
        }
    )
    prompt["sprite_grid"]["_meta"]["title"] = (
        "Compose the intended cardinal-view candidate sheet"
    )

    output_prefix = prompt["save"]["inputs"]["filename_prefix"]
    prompt["save_frames"]["inputs"]["filename_prefix"] = (
        f"{output_prefix}/candidate-views-intended-cardinal-order-"
        f"{_TURNAROUND_CANVAS_SIZE}px"
    )
    prompt["save_frames"]["_meta"]["title"] = (
        "Save four ordered transparent reconstruction candidates"
    )
    prompt["save_atlas"]["inputs"]["filename_prefix"] = (
        f"{output_prefix}/candidate-contact-sheet-intended-cardinal-order"
    )
    prompt["save_atlas"]["_meta"]["title"] = (
        "Save the labeled turnaround contact sheet"
    )


def _configure_character_turnaround_run(
    prompt: Dict[str, Any], inputs: Dict[str, Any]
) -> None:
    _configure_character_turnaround(prompt, inputs, resolve_upload=True)


def _configure_character_turnaround_download(
    prompt: Dict[str, Any], inputs: Dict[str, Any]
) -> None:
    _configure_character_turnaround(prompt, inputs, resolve_upload=False)


def _configure_anchored_sprite_loop(
    prompt: Dict[str, Any], inputs: Dict[str, Any]
) -> None:
    # Validate the complete request before upload staging or graph mutation.
    _require_image(inputs, "first_frame_image")
    _require_image(inputs, "last_frame_image")
    settings = _anchored_sprite_settings(inputs)
    guides = _active_image_guides(inputs, settings.common.frames)

    upload_fields = [
        "first_frame_image",
        "last_frame_image",
        *(guide.image_field for guide in guides),
    ]
    resolved_images = {
        field: resolve_load_image_reference(inputs, field) for field in upload_fields
    }

    prompt["source_first"]["inputs"]["image"] = resolved_images[
        "first_frame_image"
    ]
    prompt["source_last"]["inputs"]["image"] = resolved_images[
        "last_frame_image"
    ]
    prompt["h3"]["inputs"].update(
        {
            "first_frame": ["source_first", 0],
            "last_frame": ["source_last", 0],
        }
    )

    active_guide_nodes = {guide.guide_node for guide in guides}
    _remove_inactive_anchored_guides(prompt, active_guide_nodes)

    conditioning = ["h3", 0]
    for guide in sorted(guides, key=lambda item: item.frame_index):
        prompt[guide.source_node]["inputs"]["image"] = resolved_images[
            guide.image_field
        ]
        prompt[guide.guide_node]["inputs"].update(
            {
                "positive": list(conditioning),
                "vae": ["video_vae_device", 0],
                "latent": ["h3", 1],
                "image": [guide.source_node, 0],
                "frame_idx": guide.frame_index,
            }
        )
        conditioning = [guide.guide_node, 0]
    prompt["guider"]["inputs"]["conditioning"] = conditioning
    _apply_anchored_sprite_graph_settings(prompt, settings)


def _configure_anchored_sprite_loop_download(
    prompt: Dict[str, Any], inputs: Dict[str, Any]
) -> None:
    """Export the default graph with its optional guide branches absent."""

    settings = _anchored_sprite_settings(inputs)
    _remove_inactive_anchored_guides(prompt, set())
    prompt["guider"]["inputs"]["conditioning"] = ["h3", 0]
    _apply_anchored_sprite_graph_settings(prompt, settings)


def _validate_reference_tags(compiled_prompt: str, reference_count: int) -> None:
    for token_match in _REFERENCE_LIKE_TAG.finditer(compiled_prompt):
        token = token_match.group(0)
        match = _REFERENCE_TAG.fullmatch(token)
        if match is None:
            raise ValueError(
                f"Malformed MiniMax H3 reference tag {token!r}; use exact "
                "<Picture N>, <Video N>, or <Audio N> syntax."
            )
        kind = match.group(1).lower()
        ordinal = int(match.group(2))
        canonical = f"<{kind.capitalize()} {ordinal}>"
        if token != canonical:
            raise ValueError(
                f"Reference tags are exact and case-sensitive; use {canonical}."
            )
        if kind != "picture":
            raise ValueError(
                f"{canonical} is unsupported by these image-reference cards."
            )
        if ordinal < 1 or ordinal > reference_count:
            raise ValueError(
                f"{canonical} has no connected image; this card has "
                f"<Picture 1> through <Picture {reference_count}>."
            )


def _write_reference_prompt(
    prompt: Dict[str, Any], fields: dict[str, str]
) -> str:
    compiled_prompt = compose_full_reference_prompt(**fields)
    graph_sections: list[str] = []
    for field_name, node_id in _PROMPT_SECTION_NODES:
        value = fields[field_name].strip()
        section = f"{field_name}:\n{value}" if value else ""
        prompt[node_id]["inputs"]["value"] = section
        if section:
            graph_sections.append(section)
    prompt["prompt_raw"]["inputs"]["value"] = ""
    if "\n\n".join(graph_sections) != compiled_prompt:
        raise RuntimeError("Reference graph prompt sections diverged from the composer.")
    return compiled_prompt


def _configure_reference_card(
    prompt: Dict[str, Any],
    inputs: Dict[str, Any],
    *,
    spec: _ReferenceCardSpec,
    resolve_upload: bool = True,
) -> None:
    reference_fields: list[str] = []
    if resolve_upload:
        gap_seen = False
        for reference in spec.references:
            present = _has_image(inputs, reference.field_id)
            if reference.required and not present:
                raise InputValidationError(reference.field_id)
            if not present:
                gap_seen = True
                continue
            if gap_seen:
                raise ValueError("Optional reference images cannot contain a gap.")
            reference_fields.append(reference.field_id)
        if not reference_fields:
            raise InputValidationError(spec.references[0].field_id)
    else:
        # Portable export / sequence preflight: keep the template's placeholder
        # filenames for the required references instead of staging uploads.
        reference_fields = [
            reference.field_id for reference in spec.references if reference.required
        ]

    direction = _required_text(inputs, "direction")
    dialogue = _optional_text(inputs, "dialogue", _DEFAULT_DIALOGUE)
    soundscape = _optional_text(inputs, "soundscape", _DEFAULT_SOUNDSCAPE)
    music = _optional_text(inputs, "music", _DEFAULT_MUSIC)
    _validate_hard_bound_input(inputs, "reference_detail", "max")
    settings = _common_settings(
        inputs,
        family="ref2va",
        default_aspect_ratio=spec.default_aspect_ratio,
    )

    subject_definitions, summary, retention_analysis = spec.prompt_fields(
        len(reference_fields)
    )
    fields = {
        "subject_definitions": subject_definitions,
        "summary": summary,
        "retention_analysis": retention_analysis,
        "detailed_description": (
            f"[Shot 1] {direction}\n\nDialogue:\n{dialogue}"
            if dialogue
            else f"[Shot 1] {direction}"
        ),
        "overall_soundscape": soundscape,
        "non_diegetic_music": music,
    }
    compiled_prompt = compose_full_reference_prompt(**fields)
    _validate_reference_tags(compiled_prompt, len(reference_fields))

    if resolve_upload:
        resolved_references = [
            resolve_load_image_reference(inputs, field_id)
            for field_id in reference_fields
        ]
    else:
        resolved_references = [f"{field_id}.png" for field_id in reference_fields]

    written_prompt = _write_reference_prompt(prompt, fields)
    if written_prompt != compiled_prompt:
        raise RuntimeError("Reference prompt changed while writing graph sections.")

    h3_inputs = prompt["h3"]["inputs"]
    h3_inputs.update(
        {
            "prompt": ["prompt_join", 0],
            "ref_image_size": "max",
        }
    )
    for ordinal in range(1, _MAX_REFERENCE_IMAGES + 1):
        source_id = f"source_{ordinal}"
        socket = f"ref_images.ref_image_{ordinal - 1}"
        if ordinal <= len(resolved_references):
            prompt[source_id]["inputs"]["image"] = resolved_references[ordinal - 1]
            h3_inputs[socket] = [source_id, 0]
        else:
            prompt.pop(source_id, None)
            h3_inputs.pop(socket, None)

    prompt["prompt_join"]["inputs"]["seed"] = settings.seed
    _apply_execution_profile(prompt, settings.profile)
    _apply_common_graph_settings(
        prompt,
        settings,
        output_folder=spec.output_folder,
        reference_count=len(resolved_references),
    )


def _configure_reference_card_download(
    prompt: Dict[str, Any],
    inputs: Dict[str, Any],
    *,
    spec: _ReferenceCardSpec,
) -> None:
    """Export the reference graph with placeholder sources (no upload staging)."""

    _configure_reference_card(prompt, inputs, spec=spec, resolve_upload=False)


def _restage_prompt_fields(reference_count: int) -> tuple[str, str, str]:
    if reference_count == 1:
        return (
            "<Subject 1> is the subject shown in <Picture 1>. Preserve defining appearance and proportions.",
            "[reference generation] Restage <Subject 1> in one coherent newly directed shot.",
            "<Subject 1> (appears in [Shot 1]): fully_preserved - defining appearance from <Picture 1> remains stable.",
        )
    return (
        "<Subject 1> is the subject shown in <Picture 1>. <Picture 2> supplies scene, pose, framing, and lighting reference without replacing <Subject 1>.",
        "[reference generation] Restage <Subject 1> using the composition and environment cues from <Picture 2>.",
        "<Subject 1> (appears in [Shot 1]): fully_preserved from <Picture 1>. Scene, pose, framing, and lighting: partially_preserved from <Picture 2>.",
    )


def _swap_prompt_fields(reference_count: int) -> tuple[str, str, str]:
    if reference_count != 2:
        raise RuntimeError("Character Swap requires exactly two references.")
    return (
        "<Picture 1> supplies the target pose, framing, clothing, lighting, and environment. <Subject 1> takes identity-defining appearance from <Picture 2>; the pictured identity in <Picture 1> is not the identity anchor.",
        "[reference generation] Restage <Subject 1> in the scene and composition represented by <Picture 1>.",
        "<Subject 1> (appears in [Shot 1]): fully_preserved from <Picture 2>. Pose, framing, clothing, lighting, and environment: partially_preserved from <Picture 1>; its pictured identity is a weak_reference.",
    )


def _outfit_prompt_fields(reference_count: int) -> tuple[str, str, str]:
    if reference_count != 2:
        raise RuntimeError("Outfit Transfer requires exactly two references.")
    return (
        "<Subject 1> is the subject shown in <Picture 1>. <Picture 2> is an outfit reference; transfer visible garment silhouette, materials, colors, and accessories without transferring the pictured person's identity.",
        "[reference generation] Generate <Subject 1> wearing the outfit represented by <Picture 2> in one coherent shot.",
        "<Subject 1> (appears in [Shot 1]): fully_preserved from <Picture 1>. Outfit silhouette, materials, colors, and accessories: attribute_transfer from <Picture 2>; its pictured identity is a weak_reference.",
    )


def _scene_sheet_prompt_fields(reference_count: int) -> tuple[str, str, str]:
    if reference_count != 1:
        raise RuntimeError("Scene Sheet requires exactly one composite reference.")
    return (
        "<Picture 1> is one composite design and scene sheet. Each distinct depicted character is a separate subject; preserve every depicted subject's recognizable identity, costume, proportions, palette, and defining design. Depicted props retain their design, and the depicted environment supplies the setting.",
        "[reference generation] Create one coherent continuous shot using the cast, props, costumes, and environment represented together in <Picture 1>.",
        "All subjects shown in <Picture 1> (appear in [Shot 1]): fully_preserved - identity, costume, proportions, palette, and defining design remain stable. Props and environment: partially_preserved from <Picture 1> as the shot's design and setting reference.",
    )


def _select_cell(
    *,
    node_id: str,
    cell_id: str,
    label: str,
    description: str,
    options: tuple[tuple[str, str, str], ...],
    default: str | None,
) -> WorkflowCell:
    props: dict[str, Any] = {
        "lfDataset": {
            "nodes": [
                {
                    "description": option_description,
                    "id": option_id,
                    "value": option_label,
                    "workflowValue": option_id,
                }
                for option_id, option_label, option_description in options
            ]
        },
        "lfTextfieldProps": {
            "lfLabel": label,
            "lfHelper": {"showWhenFocused": False, "value": description},
        },
    }
    if default is not None:
        props["lfValue"] = default
    return WorkflowCell(
        node_id=node_id,
        id=cell_id,
        value=label,
        shape="select",
        description=description,
        props=props,
    )


def _animate_execution_profile_cell() -> WorkflowCell:
    description = (
        "Choose the complete sampling recipe. Fast trades some fine detail and "
        "motion consistency for a much shorter render; Baseline spends twenty "
        "passes and is the default comparison reference."
    )
    return WorkflowCell(
        node_id="sample",
        id="execution_profile",
        value="Render profile",
        shape="select",
        description=description,
        props={
            "lfDataset": {
                "nodes": [
                    {
                        "description": option_description,
                        "id": profile_id,
                        "profileTier": profile_tier,
                        "value": option_label,
                        "workflowValue": profile_id,
                    }
                    for (
                        profile_id,
                        option_label,
                        option_description,
                        profile_tier,
                    ) in _ANIMATE_EXECUTION_PROFILE_OPTIONS
                ]
            },
            "lfTextfieldProps": {
                "lfLabel": "Render profile",
                "lfHelper": {
                    "showWhenFocused": False,
                    "value": description,
                },
            },
            "lfValue": "kitchen_quality",
        },
    )


def _textarea_cell(
    *,
    node_id: str,
    cell_id: str,
    label: str,
    default: str,
    description: str,
) -> WorkflowCell:
    return WorkflowCell(
        node_id=node_id,
        id=cell_id,
        value=label,
        shape="textfield",
        description=description,
        props={
            "lfHtmlAttributes": {
                "autocomplete": "off",
                "name": cell_id,
                "type": "text",
            },
            "lfLabel": label,
            "lfHelper": {"showWhenFocused": False, "value": description},
            "lfStyling": "textarea",
            "lfValue": default,
        },
    )


def _float_cell(
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
        value=label,
        shape="textfield",
        description=description,
        props={
            "lfHtmlAttributes": {
                "autocomplete": "off",
                "name": cell_id,
                "type": "number",
                "min": minimum,
                "max": maximum,
                "step": step,
            },
            "lfLabel": label,
            "lfHelper": {"showWhenFocused": False, "value": description},
            "lfValue": default,
        },
    )


def _number_cell(
    *,
    node_id: str,
    cell_id: str,
    label: str,
    default: str,
    minimum: int,
    maximum: int,
    description: str,
    required: bool = True,
) -> WorkflowCell:
    return WorkflowCell(
        node_id=node_id,
        id=cell_id,
        value=label,
        shape="textfield",
        description=description,
        props={
            "lfHtmlAttributes": {
                "autocomplete": "off",
                "name": cell_id,
                "type": "number",
                "min": minimum,
                "max": maximum,
                "step": 1,
            },
            "lfLabel": label,
            "lfHelper": {"showWhenFocused": False, "value": description},
            "lfValue": default,
        },
        required=required,
    )


def _upload_cell(
    *,
    node_id: str,
    cell_id: str,
    label: str,
    description: str,
    required: bool = True,
) -> WorkflowCell:
    return WorkflowCell(
        node_id=node_id,
        id=cell_id,
        value=label,
        shape="upload",
        description=description,
        props={
            "lfHtmlAttributes": {"accept": "image/*"},
            "lfLabel": label,
            "lfHelper": {"showWhenFocused": False, "value": description},
        },
        required=required,
    )


def _creative_cells(
    *,
    direction_label: str,
    direction_default: str,
    direction_help: str,
) -> list[WorkflowCell]:
    return [
        _textarea_cell(
            node_id="h3",
            cell_id="direction",
            label=direction_label,
            default=direction_default,
            description=direction_help,
        ),
        _textarea_cell(
            node_id="h3",
            cell_id="dialogue",
            label="Dialogue",
            default=_DEFAULT_DIALOGUE,
            description=(
                "Write exact spoken lines, speakers, delivery, and timing, or use "
                "'No spoken dialogue.'"
            ),
        ),
        _textarea_cell(
            node_id="h3",
            cell_id="soundscape",
            label="Soundscape",
            default=_DEFAULT_SOUNDSCAPE,
            description=(
                "Describe ambience, foley, environmental sound, and spatial placement. "
                "Audio is generated jointly with the video."
            ),
        ),
        _textarea_cell(
            node_id="h3",
            cell_id="music",
            label="Music",
            default=_DEFAULT_MUSIC,
            description="Describe non-diegetic score and timing, or use N/A for no music.",
        ),
    ]


def _common_cells(
    *,
    default_aspect_ratio: str,
) -> list[WorkflowCell]:
    return [
        _select_cell(
            node_id="h3",
            cell_id="aspect_ratio",
            label="Aspect ratio",
            description=(
                "Choose a curated native canvas. Dimensions are fixed, aligned to 32, "
                "and capped at the 768x1344 pixel budget."
            ),
            options=_ASPECT_RATIO_OPTIONS,
            default=default_aspect_ratio,
        ),
        _select_cell(
            node_id="h3",
            cell_id="duration_frames",
            label="Duration",
            description=(
                "Exact 17k+5 frame presets at the fixed 24 fps output rate; only the "
                "approximately 5-15 second trained range is exposed."
            ),
            options=_DURATION_OPTIONS,
            default="124",
        ),
        _number_cell(
            node_id="noise",
            cell_id="seed",
            label="Seed",
            default="42",
            minimum=0,
            maximum=_MAX_SEED,
            description="Reuse a seed for controlled prompt and profile comparisons.",
        ),
    ]


def _video_output(description: str) -> WorkflowCell:
    return WorkflowCell(
        node_id="save",
        id="video",
        shape="masonry",
        description=description,
    )


_BASE_GRAPH = Path(__file__).resolve().parent / "minimax_h3_base.json"
_ANCHORED_GRAPH = Path(__file__).resolve().parent / "minimax_h3_anchored_loop.json"
_REFERENCE_GRAPH = Path(__file__).resolve().parent / "minimax_h3_reference.json"

_BASE_CARD_SPECS = (
    _BaseCardSpec(
        workflow_id="minimax_h3_generate_video",
        title="Generate Video",
        output_folder="GenerateVideo",
        description=(
            "Create a new video and synchronized stereo audio from written direction at "
            "24 fps."
        ),
        direction_label="Scene and motion",
        direction_default=(
            "One continuous cinematic shot of a cyclist crossing a quiet riverside bridge "
            "at first light. The camera tracks gently from the side while mist drifts over "
            "the water, clothing and nearby leaves respond naturally to the breeze, and "
            "subject geometry, lighting, and background continuity remain stable."
        ),
        direction_help=(
            "Describe subject, setting, action timeline, camera, lighting, and continuity."
        ),
        instruction="",
        first_frame=None,
        last_frame=None,
        default_aspect_ratio="16:9",
        card=WorkflowCardPresentation(
            summary="Create a new video from written scene and motion direction.",
            hero=WorkflowHeroImage(
                asset="minimax-h3/generate-video.webp",
                alt="Actual generated video frame of a stylized adult explorer walking through a market.",
            ),
        ),
    ),
    _BaseCardSpec(
        workflow_id="minimax_h3_animate_image",
        title="Animate Image",
        output_folder="AnimateImage",
        description=(
            "Animate one opening image into a coherent video with synchronized stereo "
            "audio; the image is a strong first-frame anchor, not a guarantee of perfect "
            "identity or pixel stability."
        ),
        direction_label="Motion direction",
        direction_default=(
            "Bring the opening image naturally to life in one continuous shot. Preserve "
            "the recognizable subject, composition, materials, and environment while "
            "adding restrained primary motion, natural secondary motion, and a stable "
            "camera unless movement is explicitly requested."
        ),
        direction_help=(
            "Describe what moves, what stays fixed, the motion timeline, camera behavior, "
            "and continuity constraints."
        ),
        instruction=(
            "For the target video, at 0.00 seconds into the target video, <Picture 1> "
            "(from [Shot 1]) is fully referenced."
        ),
        first_frame=(
            "source_image",
            "Opening image",
            "The first-frame image. Core stretches it to the chosen canvas, so select a matching aspect ratio to avoid distortion.",
        ),
        last_frame=None,
        default_aspect_ratio="9:16",
        card=WorkflowCardPresentation(
            summary="Bring one opening image to life with directed motion.",
            hero=WorkflowHeroImage(
                asset="minimax-h3/animate-image.webp",
                alt=(
                    "Prepared adult explorer input beside actual video frames "
                    "showing a right-hand wave and return to the neutral pose."
                ),
            ),
        ),
    ),
    _BaseCardSpec(
        workflow_id="minimax_h3_first_last_frame",
        title="First & Last Frame",
        output_folder="FirstLastFrame",
        description=(
            "Generate a continuous transition between required opening and ending images "
            "with synchronized stereo audio. Intermediate motion is model-generated and "
            "is not deterministic morphing."
        ),
        direction_label="Transition direction",
        direction_default=(
            "Create one continuous, physically coherent transition from the opening frame "
            "to the ending frame. Use motivated subject and camera motion, preserve stable "
            "anatomy and scene geometry, and arrive cleanly at the ending composition "
            "without cuts, flashes, or unrelated inserted objects."
        ),
        direction_help=(
            "Describe the action and camera path that connect the two frames, plus details "
            "that must remain stable."
        ),
        instruction="",
        first_frame=(
            "first_frame_image",
            "First frame",
            "Required opening anchor. Core stretches it to the chosen canvas, so select a matching aspect ratio to avoid distortion.",
        ),
        last_frame=(
            "last_frame_image",
            "Last frame",
            "Required ending frame; it is aspect-preserving cover-cropped by the H3 node.",
        ),
        default_aspect_ratio="16:9",
        card=WorkflowCardPresentation(
            summary="Generate motion between supplied opening and ending frames.",
            hero=WorkflowHeroImage(
                asset="minimax-h3/first-last-frame.webp",
                alt="Actual neutral first input beside generated transition and final waving frames of the explorer.",
            ),
        ),
    ),
    _BaseCardSpec(
        workflow_id="minimax_h3_sprite_motion",
        title="Sprite Motion",
        output_folder="SpriteMotion",
        description=(
            "Animate a sprite or compact illustrated subject from one opening image. The "
            "saved video does not preserve alpha transparency, and this is prompt-guided "
            "motion rather than a frame-exact sprite-sheet tool."
        ),
        direction_label="Sprite action",
        direction_default=(
            "Animate the illustrated subject with a short readable idle-to-action cycle: "
            "a clear anticipation, one primary movement, a brief settle, and restrained "
            "secondary motion. Preserve silhouette, palette, line weight, proportions, "
            "and a fixed camera; avoid added limbs, texture drift, or scene cuts."
        ),
        direction_help=(
            "Describe a concise action cycle, timing, silhouette constraints, camera, and "
            "background behavior."
        ),
        instruction=(
            "For the target video, at 0.00 seconds into the target video, <Picture 1> "
            "(from [Shot 1]) is fully referenced."
        ),
        first_frame=(
            "source_image",
            "Sprite image",
            "Opening illustration or sprite reference. Core stretches it to the chosen canvas, and alpha is not retained in MP4 output.",
        ),
        last_frame=None,
        default_aspect_ratio="1:1",
        card=WorkflowCardPresentation(
            summary="Animate a compact subject into an opaque motion clip.",
            hero=WorkflowHeroImage(
                asset="minimax-h3/sprite-motion.webp",
                alt="Actual source beside wave and return frames from the opaque Sprite Motion video, not a sprite atlas.",
            ),
        ),
    ),
)

_REFERENCE_CARD_SPECS = (
    _ReferenceCardSpec(
        workflow_id="minimax_h3_reference_restage",
        title="Reference Restage",
        output_folder="ReferenceRestage",
        description=(
            "Restage a referenced subject in a newly directed shot. This is reference-"
            "guided generation, not exact geometry transfer."
        ),
        direction_label="New shot direction",
        direction_default=(
            "Show <Subject 1> walking through a bright covered market, glancing toward a "
            "nearby stall as the camera makes a slow parallel track. Preserve recognizable "
            "appearance and natural proportions, keep background geometry coherent, and "
            "use believable cloth, hair, and environmental motion in one continuous shot."
        ),
        direction_help=(
            "Describe the complete target shot in plain language. Reference tags are "
            "inserted by the card; do not add Picture tags yourself."
        ),
        references=(
            _ReferenceInputSpec(
                "reference_image",
                "Reference image",
                "Primary subject, design, and appearance reference.",
                True,
            ),
        ),
        prompt_fields=_restage_prompt_fields,
        default_aspect_ratio="16:9",
        card=WorkflowCardPresentation(
            summary="Restage a referenced subject in a newly directed video.",
            hero=WorkflowHeroImage(
                asset="minimax-h3/reference-restage.webp",
                alt=(
                    "Original explorer figurine reference beside an actual video "
                    "frame restaging her in profile in a more realistic market scene."
                ),
            ),
        ),
    ),
    _ReferenceCardSpec(
        workflow_id="minimax_h3_character_swap",
        title="Character Swap",
        output_folder="CharacterSwap",
        description=(
            "Prompt-guided restaging that takes the recognizable subject from one image "
            "and the scene/composition from another. It does not perform deterministic "
            "masking, tracking, or pixel replacement."
        ),
        direction_label="Swap direction",
        direction_default=(
            "Place <Subject 1> naturally into the target scene and performance while "
            "preserving the subject's recognizable face, hair, proportions, and defining "
            "features. Follow the target pose, framing, clothing, lighting, and environment "
            "where compatible, with coherent contact, motion, and scene continuity."
        ),
        direction_help=(
            "Describe how the referenced subject should perform in the target composition. "
            "The first upload supplies the target scene; the second supplies identity."
        ),
        references=(
            _ReferenceInputSpec(
                "scene_image",
                "Target scene reference",
                "The target pose, composition, clothing, lighting, and environment. This is <Picture 1>.",
                True,
            ),
            _ReferenceInputSpec(
                "character_image",
                "Character reference",
                "The recognizable subject to carry into the target scene. This is <Picture 2>.",
                True,
            ),
        ),
        prompt_fields=_swap_prompt_fields,
        default_aspect_ratio="9:16",
    ),
    _ReferenceCardSpec(
        workflow_id="minimax_h3_outfit_transfer",
        title="Outfit Transfer",
        output_folder="OutfitTransfer",
        description=(
            "Prompt-guided transfer of visible outfit cues from one image to a referenced "
            "subject. It can reinterpret garment details and does not guarantee an exact "
            "product, pattern, or logo copy."
        ),
        direction_label="Outfit and shot direction",
        direction_default=(
            "Show <Subject 1> wearing the referenced outfit in a natural three-quarter "
            "full-body shot. Preserve the subject's recognizable identity and proportions "
            "while carrying over the outfit silhouette, layering, material character, "
            "colors, and visible accessories. Use coherent garment fit, folds, motion, "
            "lighting, and contact throughout one continuous shot."
        ),
        direction_help=(
            "Describe the target framing, action, setting, and which visible garment "
            "attributes matter most. The card binds the two references automatically."
        ),
        references=(
            _ReferenceInputSpec(
                "character_image",
                "Character reference",
                "The recognizable subject whose identity should remain stable.",
                True,
            ),
            _ReferenceInputSpec(
                "outfit_image",
                "Outfit reference",
                "Visible garment silhouette, materials, colors, and accessory cues.",
                True,
            ),
        ),
        prompt_fields=_outfit_prompt_fields,
        default_aspect_ratio="9:16",
    ),
    _ReferenceCardSpec(
        workflow_id="minimax_h3_scene_sheet",
        title="Scene Sheet · Experimental",
        output_folder="SceneSheetExperimental",
        description=(
            "Community technique that uses one composite design/scene sheet as a dense "
            "reference for a continuous shot. Cast count, subject identity, costume, and "
            "composition can drift, especially when the sheet is crowded or ambiguous."
        ),
        direction_label="Scene direction",
        direction_default=(
            "Create one coherent continuous shot in the depicted environment using every "
            "clearly established subject and relevant prop from the composite sheet. Stage "
            "the cast in a readable group action with stable identities, costumes, body "
            "proportions, scale relationships, and spatial continuity. Use one motivated "
            "camera move, natural interaction, and no cuts or unreferenced new characters."
        ),
        direction_help=(
            "Describe one focused shot using the cast, props, and environment present in "
            "the uploaded composite. Dense or contradictory sheets increase drift."
        ),
        references=(
            _ReferenceInputSpec(
                "scene_sheet",
                "Composite scene sheet",
                "One image containing the character turnarounds, costumes, props, and environment to use together as <Picture 1>.",
                True,
            ),
        ),
        prompt_fields=_scene_sheet_prompt_fields,
        default_aspect_ratio="16:9",
    ),
)


def _make_base_workflow(spec: _BaseCardSpec) -> WorkflowNode:
    uploads: list[WorkflowCell] = []
    if spec.first_frame is not None:
        uploads.append(
            _upload_cell(
                node_id="source_first",
                cell_id=spec.first_frame[0],
                label=spec.first_frame[1],
                description=spec.first_frame[2],
            )
        )
    if spec.last_frame is not None:
        uploads.append(
            _upload_cell(
                node_id="source_last",
                cell_id=spec.last_frame[0],
                label=spec.last_frame[1],
                description=spec.last_frame[2],
            )
        )
    execution_profile_cells = (
        [_animate_execution_profile_cell()]
        if spec.workflow_id == "minimax_h3_animate_image"
        else []
    )
    return WorkflowNode(
        id=spec.workflow_id,
        value=spec.title,
        description=spec.description,
        category="MiniMax H3",
        card=spec.card,
        inputs=[
            *uploads,
            *_creative_cells(
                direction_label=spec.direction_label,
                direction_default=spec.direction_default,
                direction_help=spec.direction_help,
            ),
            *execution_profile_cells,
            *_common_cells(
                default_aspect_ratio=spec.default_aspect_ratio,
            ),
        ],
        outputs=[
            _video_output(
                "Generated video with synchronized stereo audio at 24 fps."
            )
        ],
        configure_prompt=partial(_configure_base_card, spec=spec),
        workflow_path=_BASE_GRAPH,
        input_option_requirements=(
            (_TURBO_V4_OPTION_REQUIREMENT,)
            if spec.workflow_id == "minimax_h3_animate_image"
            else ()
        ),
    )


def _make_anchored_sprite_loop_workflow() -> WorkflowNode:
    return WorkflowNode(
        id="minimax_h3_anchored_sprite_loop",
        value="Anchored Sprite Loop",
        description=(
            "Create a prompt-guided sprite or compact illustration loop between explicit "
            "opening and ending FL2VA frames, with up to three optional interior image "
            "anchors at selected frame indices. Use the same endpoint image when a "
            "visually closed cycle is required; the result remains generated motion, not "
            "deterministic in-betweening. The card saves a 24-frame transparent PNG batch, "
            "a zero-gap 6x4 atlas, and the original MP4 preview. RMBG-2.0 infers alpha per "
            "frame, then LF_NormalizeSpriteBatch applies one reference-derived scale and "
            "horizontal pivot to the entire batch while aligning each alpha baseline. It "
            "normalizes alpha-content bounds, not semantic body height: equipment, effects, "
            "and shadows count, and it does not stabilize the inferred matte itself. "
            "It requires the installed VNCCS_RMBG2 node and the declared local RMBG-2.0 "
            "files; Runner does not start the wrapper's fallback download."
        ),
        category="MiniMax H3",
        card=WorkflowCardPresentation(
            summary="Guide a motion cycle and export transparent sprite frames.",
            hero=WorkflowHeroImage(
                asset="minimax-h3/anchored-sprite-loop.webp",
                alt=(
                    "Four actual transparent sprites showing start, wave, lowering "
                    "and return from a 24-frame export played at 12 fps."
                ),
            ),
        ),
        inputs=[
            _upload_cell(
                node_id="source_first",
                cell_id="first_frame_image",
                label="First frame",
                description=(
                    "Required opening endpoint at frame 0. Core stretches it to the chosen "
                    "canvas, so select a matching aspect ratio to avoid distortion."
                ),
            ),
            _upload_cell(
                node_id="source_last",
                cell_id="last_frame_image",
                label="Last frame",
                description=(
                    "Required ending endpoint at the final frame. Reuse the opening asset "
                    "for a closed cycle; the sprite export deliberately omits this final "
                    "endpoint while the MP4 keeps it. Core cover-crops the image to the "
                    "selected canvas."
                ),
            ),
            _upload_cell(
                node_id="source_guide_1",
                cell_id="guide_image_1",
                label="Guide 1 image (optional)",
                description=(
                    "Optional pose or state anchor. It is added through Core's "
                    "MiniMaxH3AddGuide node at Guide 1 frame."
                ),
                required=False,
            ),
            _number_cell(
                node_id="guide_1",
                cell_id="guide_frame_1",
                label="Guide 1 frame",
                default="41",
                minimum=1,
                maximum=360,
                description=(
                    "Zero-based interior target frame for Guide 1. It must be after frame 0 "
                    "and before the selected duration's final frame."
                ),
                required=False,
            ),
            _upload_cell(
                node_id="source_guide_2",
                cell_id="guide_image_2",
                label="Guide 2 image (optional)",
                description=(
                    "Optional second pose or state anchor. It may appear before or after "
                    "Guide 1, but the two frame indices must differ."
                ),
                required=False,
            ),
            _number_cell(
                node_id="guide_2",
                cell_id="guide_frame_2",
                label="Guide 2 frame",
                default="82",
                minimum=1,
                maximum=360,
                description=(
                    "Zero-based interior target frame for Guide 2. It must be in range and "
                    "different from Guide 1 when both images are supplied."
                ),
                required=False,
            ),
            _upload_cell(
                node_id="source_guide_3",
                cell_id="guide_image_3",
                label="Guide 3 image (optional)",
                description=(
                    "Optional third pose or state anchor. Its frame index must be interior "
                    "and different from every other supplied guide."
                ),
                required=False,
            ),
            _number_cell(
                node_id="guide_3",
                cell_id="guide_frame_3",
                label="Guide 3 frame",
                default="103",
                minimum=1,
                maximum=360,
                description=(
                    "Zero-based interior target frame for Guide 3. Active guides are "
                    "chained in ascending frame order."
                ),
                required=False,
            ),
            *_creative_cells(
                direction_label="Loop direction",
                direction_default=(
                    "Create one seamless, readable action cycle between the supplied "
                    "endpoint frames. Preserve the subject's silhouette, palette, line "
                    "weight, proportions, and screen position; use clear anticipation, one "
                    "primary motion, a controlled settle, restrained secondary motion, and "
                    "a fixed camera with no cuts or added elements. Honor each supplied "
                    "intermediate guide at its selected frame."
                ),
                direction_help=(
                    "Describe the complete cycle, timing, fixed visual traits, camera and "
                    "background behavior, and how intermediate guide poses connect."
                ),
            ),
            *_common_cells(default_aspect_ratio="1:1"),
            _number_cell(
                node_id="sprite_normalize",
                cell_id="sprite_size",
                label="Sprite canvas",
                default=str(_DEFAULT_SPRITE_SIZE),
                minimum=32,
                maximum=1024,
                description=(
                    "Square width and height for every transparent PNG frame and each 6x4 "
                    "atlas cell. Content that cannot fit fails instead of being cropped."
                ),
            ),
            _number_cell(
                node_id="sprite_normalize",
                cell_id="sprite_alpha_height",
                label="Reference content height",
                default=str(_DEFAULT_SPRITE_ALPHA_HEIGHT),
                minimum=1,
                maximum=1024,
                description=(
                    "The reference frame's alpha bounds derive one scale for all frames. "
                    "Think 'how tall should the visible cutout be?' Bicubic edge filtering "
                    "can add a small measured halo."
                ),
            ),
            _number_cell(
                node_id="sprite_normalize",
                cell_id="sprite_reference_frame",
                label="Reference frame",
                default=str(_DEFAULT_SPRITE_REFERENCE_FRAME),
                minimum=0,
                maximum=_SPRITE_FRAME_COUNT - 1,
                description=(
                    "Zero-based sampled frame used to choose the shared scale and horizontal "
                    "pivot. Every other frame keeps its relative left/right motion."
                ),
            ),
            _number_cell(
                node_id="sprite_normalize",
                cell_id="sprite_bottom_padding",
                label="Bottom padding",
                default=str(_DEFAULT_SPRITE_BOTTOM_PADDING),
                minimum=0,
                maximum=1023,
                description=(
                    "Transparent rows below the feet or lowest alpha pixel. Each frame's "
                    "alpha baseline lands here; scale and horizontal placement stay shared."
                ),
            ),
            _number_cell(
                node_id="sprite_sampler",
                cell_id="intended_fps",
                label="Intended playback FPS",
                default=str(_DEFAULT_INTENDED_FPS),
                minimum=1,
                maximum=60,
                description=(
                    "Playback rate recorded in the sampling receipt and output names. It "
                    "does not change the original 24 fps MP4 preview."
                ),
            ),
        ],
        outputs=[
            _video_output(
                "Original anchored loop MP4 with synchronized stereo audio at 24 fps."
            ),
            WorkflowCell(
                node_id="save_frames",
                id="frames",
                shape="masonry",
                description="Twenty-four ordered square RGBA PNG sprite frames.",
            ),
            WorkflowCell(
                node_id="save_atlas",
                id="atlas",
                shape="masonry",
                description="Transparent zero-gap 6x4 PNG sprite atlas in row-major order.",
            ),
            WorkflowCell(
                node_id="display_sampling_receipt",
                id="receipt",
                shape="code",
                description=(
                    "Periodic sampling indices and source/intended playback timing receipt."
                ),
                props={"lfLanguage": "json"},
            ),
            WorkflowCell(
                node_id="display_normalization_receipt",
                id="normalization_receipt",
                shape="code",
                description=(
                    "Shared scale/pivot, per-frame baseline translations, measured alpha "
                    "bounds, and clipping policy. Bounds include equipment and shadows."
                ),
                props={"lfLanguage": "json"},
            ),
        ],
        configure_prompt=_configure_anchored_sprite_loop,
        configure_download=_configure_anchored_sprite_loop_download,
        workflow_path=_ANCHORED_GRAPH,
        required_model_assets=_RMBG2_MODEL_ASSETS,
    )


def _make_reference_workflow(spec: _ReferenceCardSpec) -> WorkflowNode:
    return WorkflowNode(
        id=spec.workflow_id,
        value=spec.title,
        description=(
            spec.description
            + " References use Core's Max detail for the strongest available identity "
            "fidelity; this can run several times slower than Match."
        ),
        category="MiniMax H3",
        card=spec.card,
        inputs=[
            *[
                _upload_cell(
                    node_id=f"source_{ordinal}",
                    cell_id=reference.field_id,
                    label=reference.label,
                    description=reference.help,
                    required=reference.required,
                )
                for ordinal, reference in enumerate(spec.references, start=1)
            ],
            *_creative_cells(
                direction_label=spec.direction_label,
                direction_default=spec.direction_default,
                direction_help=spec.direction_help,
            ),
            *_common_cells(
                default_aspect_ratio=spec.default_aspect_ratio,
            ),
        ],
        outputs=[
            _video_output(
                "Reference-guided video with synchronized stereo audio at 24 fps."
            )
        ],
        configure_prompt=partial(_configure_reference_card, spec=spec),
        configure_download=partial(_configure_reference_card_download, spec=spec),
        workflow_path=_REFERENCE_GRAPH,
    )


def _make_directed_view_workflow() -> WorkflowNode:
    return WorkflowNode(
        id="minimax_h3_directed_view",
        value="Directed View",
        description=(
            "Turn one frontal character reference toward one exact cardinal camera "
            "view, then save the least-moving full-resolution frame from the clip's "
            "settled tail. This block measures motion only; it cannot prove viewpoint, "
            "identity, anatomy, or geometric consistency."
        ),
        category="MiniMax H3",
        card=WorkflowCardPresentation(
            summary="Generate a requested view, then select a settled frame.",
            hero=WorkflowHeroImage(
                asset="minimax-h3/directed-view.webp",
                alt=(
                    "Front input beside the actual generated subject-right profile "
                    "of an original adult explorer figurine."
                ),
            ),
        ),
        inputs=[
            _upload_cell(
                node_id="source_first",
                cell_id="source_image",
                label="Frontal character",
                description=(
                    "Use one centered, full-body front view with visible extremities, "
                    "clear margin, a neutral stance, and as little occlusion as practical."
                ),
            ),
            _select_cell(
                node_id="h3",
                cell_id="target_view",
                label="Target view",
                description=(
                    "Choose where the camera should finish relative to the subject. "
                    "Subject right and left are anatomical, not the viewer's sides."
                ),
                options=_DIRECTED_VIEW_OPTIONS,
                default="subject_right",
            ),
            _textarea_cell(
                node_id="h3",
                cell_id="retention_details",
                label="Details to retain",
                default=_DIRECTED_VIEW_RETENTION_DEFAULT,
                description=(
                    "Name identity, silhouette, outfit, equipment, colors, materials, "
                    "and asymmetries that must survive the turn. The camera path and "
                    "stationary-pose rules are added automatically."
                ),
            ),
            _animate_execution_profile_cell(),
            _float_cell(
                node_id="settled_selector",
                cell_id="tail_fraction",
                label="Settled tail",
                default=str(_DIRECTED_VIEW_TAIL_FRACTION),
                minimum=0.01,
                maximum=1.0,
                step=0.01,
                description=(
                    "Final fraction of the clip searched for the least movement. 0.25 "
                    "means the last quarter; this does not judge whether the chosen "
                    "frame is the requested angle."
                ),
            ),
            _number_cell(
                node_id="settled_selector",
                cell_id="analysis_max_edge",
                label="Motion analysis size",
                default=str(_DIRECTED_VIEW_ANALYSIS_RESOLUTION),
                minimum=8,
                maximum=1024,
                description=(
                    "Temporary longest-edge size used only to compare frame motion. "
                    "Smaller is faster and less sensitive to tiny texture shimmer; the "
                    "saved image always stays at full decoded resolution."
                ),
            ),
            *_common_cells(default_aspect_ratio="9:16"),
        ],
        outputs=[
            WorkflowCell(
                node_id="save_view",
                id="view",
                shape="masonry",
                description=(
                    "One lossless PNG selected from the full-resolution decoded tensor "
                    "before MP4 compression. Visually verify the requested view and "
                    "identity before downstream reconstruction."
                ),
            ),
            _video_output(
                "The complete camera-turn clip used to select the still frame."
            ),
            WorkflowCell(
                node_id="display_selection_receipt",
                id="selection_receipt",
                shape="code",
                description=(
                    "Selected source index and tail-motion measurements. It reports "
                    "temporal stability, not semantic correctness."
                ),
                props={"lfLanguage": "json"},
            ),
        ],
        configure_prompt=_configure_directed_view_run,
        configure_download=_configure_directed_view_download,
        workflow_path=_ANCHORED_GRAPH,
        input_option_requirements=(_TURBO_V4_OPTION_REQUIREMENT,),
    )


def _make_character_turnaround_workflow() -> WorkflowNode:
    return WorkflowNode(
        id="minimax_h3_character_turnaround",
        value="Character Turnaround · Experimental",
        description=(
            "Generate one closed, identity-coupled H3 turntable and extract four "
            "ordered transparent angle candidates for reconstruction. The intended "
            "order is front, subject-right, back, and subject-left. The workflow keeps "
            "the native one-megapixel canvas and 20-step quality schedule while using "
            "Comfy Kitchen attention; neither it nor the motion-aware sampler can prove "
            "camera orientation. Review the contact sheet before treating the views "
            "as geometric evidence."
        ),
        category="MiniMax H3",
        card=WorkflowCardPresentation(
            summary="Sample four candidate views from one generated turntable.",
            hero=WorkflowHeroImage(
                asset="minimax-h3/character-turnaround.webp",
                alt=(
                    "Four actual transparent explorer view candidates sampled "
                    "from one generated turntable, shown on a neutral gray matte."
                ),
            ),
        ),
        inputs=[
            _upload_cell(
                node_id="source_first",
                cell_id="source_image",
                label="Character source",
                description=(
                    "Use a full-body character with visible extremities, generous margin, "
                    "a neutral stance, and as little occlusion as practical. The workflow "
                    "fits it to the selected H3 canvas without stretching."
                ),
            ),
            _textarea_cell(
                node_id="h3",
                cell_id="direction",
                label="Turntable direction",
                default=_TURNAROUND_DIRECTION_DEFAULT,
                description=(
                    "Keep the declared front → right → back → left → front order. Add "
                    "character-specific retention details here without introducing body "
                    "motion, cuts, zoom, or changing camera distance."
                ),
            ),
            _number_cell(
                node_id="sprite_normalize",
                cell_id="content_height",
                label="View content height",
                default=str(_TURNAROUND_ALPHA_HEIGHT),
                minimum=512,
                maximum=_TURNAROUND_ALPHA_HEIGHT,
                description=(
                    "How tall the front view should be on each 1024px output canvas. "
                    "Keep 900 for maximum detail; lower it when wings, weapons, or "
                    "stray matte pixels would otherwise clip at the sides."
                ),
            ),
            *_common_cells(default_aspect_ratio="9:16"),
        ],
        outputs=[
            _video_output(
                "The complete closed H3 turntable used as the four-view evidence source."
            ),
            WorkflowCell(
                node_id="save_frames",
                id="views",
                shape="masonry",
                description=(
                    "Four ordered 1024px transparent angle candidates: front, "
                    "subject-right, back, subject-left. Visual-motion sampling "
                    "compensates for pauses, but the contact sheet remains the "
                    "semantic acceptance gate."
                ),
            ),
            WorkflowCell(
                node_id="save_atlas",
                id="contact_sheet",
                shape="masonry",
                description=(
                    "Labeled intended-cardinal-view candidate sheet. Reject the set "
                    "if an angle is transitional, duplicated, reversed, or "
                    "identity-drifted."
                ),
            ),
            WorkflowCell(
                node_id="display_sampling_receipt",
                id="sampling_receipt",
                shape="code",
                description=(
                    "Exact source frame count, measured visual-motion arc, and the "
                    "deterministic candidate indices selected from it."
                ),
                props={"lfLanguage": "json"},
            ),
            WorkflowCell(
                node_id="display_normalization_receipt",
                id="normalization_receipt",
                shape="code",
                description=(
                    "Shared scale/pivot and per-view alpha-baseline translations. Alpha "
                    "bounds include equipment, hair, and shadows."
                ),
                props={"lfLanguage": "json"},
            ),
        ],
        configure_prompt=_configure_character_turnaround_run,
        configure_download=_configure_character_turnaround_download,
        workflow_path=_ANCHORED_GRAPH,
        required_model_assets=_RMBG2_MODEL_ASSETS,
    )


generate_video, animate_image, first_last_frame, sprite_motion = tuple(
    _make_base_workflow(spec) for spec in _BASE_CARD_SPECS
)
anchored_sprite_loop = _make_anchored_sprite_loop_workflow()
directed_view = _make_directed_view_workflow()
character_turnaround = _make_character_turnaround_workflow()
reference_restage, character_swap, outfit_transfer, scene_sheet = tuple(
    _make_reference_workflow(spec) for spec in _REFERENCE_CARD_SPECS
)

WORKFLOWS = (
    generate_video,
    animate_image,
    first_last_frame,
    anchored_sprite_loop,
    directed_view,
    character_turnaround,
    reference_restage,
    character_swap,
    outfit_transfer,
    sprite_motion,
    scene_sheet,
)
WORKFLOW_BY_ID = {workflow.id: workflow for workflow in WORKFLOWS}

__all__ = [
    "WORKFLOWS",
    "WORKFLOW_BY_ID",
    "anchored_sprite_loop",
    "animate_image",
    "character_swap",
    "character_turnaround",
    "directed_view",
    "first_last_frame",
    "generate_video",
    "outfit_transfer",
    "reference_restage",
    "scene_sheet",
    "sprite_motion",
]
