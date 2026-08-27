"""Focused MiniMax H3 Workflow Runner cards over reusable local graphs.

The cards share base, anchored-guide, and reference graphs while keeping public
controls task-oriented. Canvas geometry is selected from a curated native-size
map, output is fixed at 24 fps, duration is selected directly on H3's 17k+5
frame grid, and the validated quality profile owns its sampler, scheduler, and
step count.
"""

from __future__ import annotations

import re
from functools import partial
from pathlib import Path
from typing import Any, Callable, Dict, NamedTuple

from ..prompts import compose_base_prompt, compose_full_reference_prompt
from ..services.registry import (
    InputValidationError,
    WorkflowCell,
    WorkflowModelAsset,
    WorkflowNode,
)
from .minimax_h3_profiles import (
    MiniMaxH3ExecutionProfile,
    NATIVE_MAX_EDGE,
    NATIVE_MAX_PIXELS,
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
_DEFAULT_INTENDED_FPS = 12

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

_GUIDE_INPUTS = (
    ("guide_image_1", "guide_frame_1", "source_guide_1", "guide_1", 41),
    ("guide_image_2", "guide_frame_2", "source_guide_2", "guide_2", 82),
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


def _optional_text(inputs: Dict[str, Any], name: str, default: str = "") -> str:
    value = inputs.get(name, default)
    if value is None:
        return ""
    if not isinstance(value, str):
        raise InputValidationError(name)
    return value.strip()


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
) -> _CommonSettings:
    _validate_hard_bound_input(inputs, "execution_profile", "kitchen_quality")
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
    profile = resolve_h3_execution_profile("kitchen_quality", family=family)
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

    if profile.id != "kitchen_quality" or profile.accelerator != "kitchen":
        raise RuntimeError("Focused MiniMax H3 cards expose kitchen_quality only.")
    prompt["sampler_select"]["inputs"]["sampler_name"] = "res_multistep"
    prompt["scheduler"]["inputs"]["scheduler"] = "simple"
    prompt["sample"]["inputs"]["sampler"] = ["sampler_select", 0]
    prompt["attention_backend"]["inputs"]["attention"] = (
        "comfy kitchen attention"
    )
    model_output = ["attention_backend", 0]
    prompt["guider"]["inputs"]["model"] = list(model_output)
    prompt["scheduler"]["inputs"]["model"] = list(model_output)
    prompt["scheduler"]["inputs"]["steps"] = profile.steps


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
    prompt["sprite_scale"]["inputs"].update(
        {
            "width": settings.sprite_size,
            "height": settings.sprite_size,
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
    prompt["save_frames"]["inputs"]["filename_prefix"] = (
        f"{output_prefix}/frames-{settings.sprite_size}px-"
        f"{settings.intended_fps}fps"
    )
    prompt["save_atlas"]["inputs"]["filename_prefix"] = (
        f"{output_prefix}/atlas-6x4-{settings.sprite_size}px-"
        f"{settings.intended_fps}fps"
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
) -> None:
    reference_fields: list[str] = []
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

    resolved_references = [
        resolve_load_image_reference(inputs, field_id)
        for field_id in reference_fields
    ]

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
    return WorkflowNode(
        id=spec.workflow_id,
        value=spec.title,
        description=spec.description,
        category="MiniMax H3",
        inputs=[
            *uploads,
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
                "Generated video with synchronized stereo audio at 24 fps."
            )
        ],
        configure_prompt=partial(_configure_base_card, spec=spec),
        workflow_path=_BASE_GRAPH,
    )


def _make_anchored_sprite_loop_workflow() -> WorkflowNode:
    return WorkflowNode(
        id="minimax_h3_anchored_sprite_loop",
        value="Anchored Sprite Loop",
        description=(
            "Create a prompt-guided sprite or compact illustration loop between explicit "
            "opening and ending FL2VA frames, with up to two optional interior image "
            "anchors at selected frame indices. Use the same endpoint image when a "
            "visually closed cycle is required; the result remains generated motion, not "
            "deterministic in-betweening. The card saves a 24-frame transparent PNG batch, "
            "a zero-gap 6x4 atlas, and the original MP4 preview. RMBG-2.0 infers alpha per "
            "frame, so edge matte, framing, scale, and depicted content can still vary; "
            "this first slice does not add temporal stabilization or automatic cropping. "
            "It requires the installed VNCCS_RMBG2 node and the declared local RMBG-2.0 "
            "files; Runner does not start the wrapper's fallback download."
        ),
        category="MiniMax H3",
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
                node_id="sprite_scale",
                cell_id="sprite_size",
                label="Sprite size",
                default=str(_DEFAULT_SPRITE_SIZE),
                minimum=32,
                maximum=1024,
                description=(
                    "Square pixel size for every transparent PNG frame and each 6x4 atlas "
                    "cell. Core ImageScale applies one common RGBA canvas to the full batch."
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
        workflow_path=_REFERENCE_GRAPH,
    )


generate_video, animate_image, first_last_frame, sprite_motion = tuple(
    _make_base_workflow(spec) for spec in _BASE_CARD_SPECS
)
anchored_sprite_loop = _make_anchored_sprite_loop_workflow()
reference_restage, character_swap, outfit_transfer, scene_sheet = tuple(
    _make_reference_workflow(spec) for spec in _REFERENCE_CARD_SPECS
)

WORKFLOWS = (
    generate_video,
    animate_image,
    first_last_frame,
    anchored_sprite_loop,
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
    "first_last_frame",
    "generate_video",
    "outfit_transfer",
    "reference_restage",
    "scene_sheet",
    "sprite_motion",
]
