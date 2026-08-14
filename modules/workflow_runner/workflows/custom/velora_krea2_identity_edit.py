"""One- or two-reference Krea 2 Identity Edit proof for Velora.

When a scene is supplied it is reference one and the canonical character image
is reference two.  Without a scene, the canonical character image is the sole
reference.  Those modes follow the Identity Edit LoRA's native one- and
two-reference contracts; their ordering is deliberately not a UI choice.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict

from ...services.registry import (
    InputValidationError,
    WorkflowCell,
    WorkflowNode,
    WorkflowSubmissionPolicy,
)
from ..utils import resolve_load_image_reference


_MAX_SEED = (1 << 64) - 1
_JSON_SAFE_SEED_MAX = (1 << 53) - 1
_CANVAS_MULTIPLE = 16
_MAX_EDGE = 2048
_MAX_PIXELS = 2_000_000
_MODEL_NAMES = (
    "KR2\\darkBeast30BF16INT8_darkBeastKREA2FP8.safetensors",
    "KR2\\moodyKrea2Mix_v60.safetensors",
)
_DEFAULT_MODEL = _MODEL_NAMES[0]
_CLIP_NAME = "qwen3vl_4b_bf16.safetensors"
_VAE_NAME = "krea2RealVae_v10.safetensors"
_IDENTITY_LORA = "KR2\\krea2_identity_edit_v1_2.safetensors"
_OUTPUT_ROOT = "velora/krea2_identity_edit"
_APPEARANCE_BUCKET_SCHEMA = "velora.krea2-appearance-buckets.v1"
_WEIGHTED_SELECTION_MODE = "weighted_sha256_v1"
_MAX_APPEARANCE_BUCKETS = 9
_MAX_BUCKET_KEYS = 128
_MAX_BUCKET_KEY_BYTES = 1024
_MAX_BUCKET_WEIGHT = 1_000_001
_MAX_BUCKET_JSON_BYTES = 128 * 1024
_PLAN_RECEIPT = re.compile(r"^sha256:[0-9a-f]{64}$")
_UNSAFE_PROMPT_FRAGMENT = re.compile(r"[<>()\[\]{}\\,:\x00-\x1f\x7f]")


def _required_text(inputs: Dict[str, Any], name: str) -> str:
    value = inputs.get(name)
    if not isinstance(value, str) or not value.strip():
        raise InputValidationError(name)
    return value.strip()


def _required_image_input(inputs: Dict[str, Any], name: str) -> None:
    """Reject absent uploads before the resolver performs filesystem work."""

    value = inputs.get(name)
    if (
        value is None
        or (isinstance(value, str) and not value.strip())
        or (isinstance(value, (list, tuple)) and not value)
    ):
        raise InputValidationError(name)


def _has_image_input(inputs: Dict[str, Any], name: str) -> bool:
    value = inputs.get(name)
    return not (
        value is None
        or (isinstance(value, str) and not value.strip())
        or (isinstance(value, (list, tuple)) and not value)
    )


def _integer(
    inputs: Dict[str, Any],
    name: str,
    default: int,
    *,
    minimum: int,
    maximum: int,
) -> int:
    value = inputs.get(name, default)
    if value in (None, ""):
        value = default
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise InputValidationError(name) from exc
    if parsed < minimum or parsed > maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}.")
    return parsed


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
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise InputValidationError(name) from exc
    if parsed < minimum or parsed > maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}.")
    return parsed


def _model_name(inputs: Dict[str, Any]) -> str:
    value = inputs.get("model_name", _DEFAULT_MODEL)
    if not isinstance(value, str) or value not in _MODEL_NAMES:
        raise InputValidationError("model_name")
    return value


def _json_safe_integer(value: Any, name: str) -> int:
    """Read one exact browser/JSON integer, rejecting booleans and floats."""

    if isinstance(value, bool) or not isinstance(value, int):
        raise InputValidationError(name)
    if value < 0 or value > _JSON_SAFE_SEED_MAX:
        raise ValueError(
            f"{name} must be a JSON-safe nonnegative integer (at most {_JSON_SAFE_SEED_MAX})."
        )
    return value


def _appearance_buckets(inputs: Dict[str, Any]) -> dict[str, Any] | None:
    """Validate Velora's compact, ontology-agnostic appearance runtime wire.

    The normal Krea workflow remains intentionally unaware of races, roles, or
    trait names. It accepts only sealed, ordered weighted prompt buckets. Each
    bucket is written into the Comfy graph verbatim enough for its complete
    selection input (map + seed) to travel with the saved PNG prompt metadata.
    """

    raw = inputs.get("appearance_buckets")
    if raw is None or raw == "":
        return None
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise InputValidationError("appearance_buckets") from exc
    if not isinstance(raw, dict):
        raise InputValidationError("appearance_buckets")

    required_wire_keys = {
        "schema",
        "planReceipt",
        "selectionMode",
        "samplerSeed",
        "buckets",
    }
    if set(raw) != required_wire_keys:
        raise InputValidationError("appearance_buckets")
    if raw["schema"] != _APPEARANCE_BUCKET_SCHEMA:
        raise InputValidationError("appearance_buckets")
    if not isinstance(raw["planReceipt"], str) or not _PLAN_RECEIPT.fullmatch(
        raw["planReceipt"]
    ):
        raise InputValidationError("appearance_buckets")
    if raw["selectionMode"] != _WEIGHTED_SELECTION_MODE:
        raise InputValidationError("appearance_buckets")
    sampler_seed = _json_safe_integer(raw["samplerSeed"], "appearance_buckets")

    buckets = raw["buckets"]
    if not isinstance(buckets, list) or not 1 <= len(buckets) <= _MAX_APPEARANCE_BUCKETS:
        raise InputValidationError("appearance_buckets")

    normalized_buckets: list[dict[str, Any]] = []
    for bucket in buckets:
        if not isinstance(bucket, dict) or set(bucket) != {"seed", "json"}:
            raise InputValidationError("appearance_buckets")
        seed = _json_safe_integer(bucket["seed"], "appearance_buckets")
        weights = bucket["json"]
        if not isinstance(weights, dict) or not 1 <= len(weights) <= _MAX_BUCKET_KEYS:
            raise InputValidationError("appearance_buckets")

        normalized_weights: dict[str, int] = {}
        for fragment, weight in weights.items():
            if (
                not isinstance(fragment, str)
                or not fragment
                or fragment != fragment.strip()
                or _UNSAFE_PROMPT_FRAGMENT.search(fragment)
            ):
                raise InputValidationError("appearance_buckets")
            if len(fragment.encode("utf-8")) > _MAX_BUCKET_KEY_BYTES:
                raise InputValidationError("appearance_buckets")
            if (
                isinstance(weight, bool)
                or not isinstance(weight, int)
                or not 1 <= weight <= _MAX_BUCKET_WEIGHT
            ):
                raise InputValidationError("appearance_buckets")
            normalized_weights[fragment] = weight
        if len(
            json.dumps(normalized_weights, ensure_ascii=False, separators=(",", ":")).encode(
                "utf-8"
            )
        ) > _MAX_BUCKET_JSON_BYTES:
            raise InputValidationError("appearance_buckets")
        normalized_buckets.append({"seed": seed, "json": normalized_weights})

    return {
        "schema": _APPEARANCE_BUCKET_SCHEMA,
        "planReceipt": raw["planReceipt"],
        "selectionMode": _WEIGHTED_SELECTION_MODE,
        "samplerSeed": sampler_seed,
        "buckets": normalized_buckets,
    }


def _add_appearance_bucket_nodes(
    prompt: Dict[str, Any], instruction: str, appearance: dict[str, Any]
) -> None:
    """Attach native LF bucket nodes only for an explicit appearance wire."""

    wall_inputs: dict[str, Any] = {
        "separator": ", ",
        "text_1": instruction,
        "shuffle_inputs": False,
        # Harmless LF_WallOfText UI metadata: preserved in Comfy's native
        # prompt PNG chunk so the executable graph still names Velora's plan.
        "ui_widget": json.dumps(
            {
                "planReceipt": appearance["planReceipt"],
                "selectionMode": appearance["selectionMode"],
            },
            separators=(",", ":"),
        ),
    }
    for index, bucket in enumerate(appearance["buckets"], start=1):
        suffix = f"{index:02d}"
        json_node_id = f"appearance_json_{suffix}"
        pick_node_id = f"appearance_pick_{suffix}"
        # Compact JSON has deterministic separators but deliberately preserves
        # source mapping insertion order; the selector itself sorts UTF-8 keys.
        literal_bucket_json = json.dumps(
            bucket["json"], ensure_ascii=False, separators=(",", ":")
        )
        prompt[json_node_id] = {
            "class_type": "LF_WriteJSON",
            "inputs": {"ui_widget": literal_bucket_json},
            "_meta": {"title": f"Velora appearance bucket {suffix}"},
        }
        prompt[pick_node_id] = {
            "class_type": "LF_GetRandomKeyFromJSON",
            "inputs": {
                "seed": bucket["seed"],
                "json_input": [json_node_id, 0],
                "selection_mode": _WEIGHTED_SELECTION_MODE,
            },
            "_meta": {"title": f"Select Velora appearance {suffix}"},
        }
        wall_inputs[f"text_{index + 1}"] = [pick_node_id, 0]

    prompt["appearance_wall"] = {
        "class_type": "LF_WallOfText",
        "inputs": wall_inputs,
        "_meta": {"title": "Compose Velora appearance prompt"},
    }
    prompt["positive"]["inputs"]["prompt"] = ["appearance_wall", 0]


def _configure(prompt: Dict[str, Any], inputs: Dict[str, Any]) -> None:
    """Compile the native one- or two-reference graph without phantom inputs."""

    # With a scene, it remains first in both the VAE and Qwen3-VL paths and the
    # identity remains second. Without one, identity is the sole first source;
    # the optional B inputs and unused scene nodes are removed entirely.
    _required_image_input(inputs, "identity_image")
    has_scene = _has_image_input(inputs, "scene_image")
    scene_reference = (
        resolve_load_image_reference(inputs, "scene_image") if has_scene else None
    )
    identity_reference = resolve_load_image_reference(inputs, "identity_image")
    instruction = _required_text(inputs, "prompt")
    width = _integer(inputs, "width", 1024, minimum=256, maximum=_MAX_EDGE)
    height = _integer(inputs, "height", 1536, minimum=256, maximum=_MAX_EDGE)
    seed = _integer(inputs, "seed", 42, minimum=0, maximum=_MAX_SEED)
    steps = _integer(inputs, "steps", 10, minimum=8, maximum=12)
    cfg = _number(inputs, "cfg", 1.0, minimum=0.0, maximum=20.0)
    ref_boost = _number(inputs, "ref_boost", 4.0, minimum=0.0, maximum=100.0)
    grounding_px = _integer(
        inputs, "grounding_px", 1024, minimum=384, maximum=2048
    )
    model_name = _model_name(inputs)
    appearance = _appearance_buckets(inputs)

    if width % _CANVAS_MULTIPLE or height % _CANVAS_MULTIPLE:
        raise ValueError("width and height must be multiples of 16.")
    if width * height > _MAX_PIXELS:
        raise ValueError("Krea 2 Identity Edit proof is limited to 2,000,000 pixels.")

    prompt["identity"]["inputs"]["image"] = identity_reference
    if has_scene:
        prompt["scene"]["inputs"]["image"] = scene_reference
    else:
        prompt.pop("scene")
        prompt.pop("scene_latent")
        prompt["patch"]["inputs"]["source_latent"] = ["identity_latent", 0]
        prompt["patch"]["inputs"]["source_image"] = ["identity", 0]
        prompt["patch"]["inputs"].pop("source_latent_b")
        prompt["patch"]["inputs"].pop("source_image_b")
        for conditioning in ("positive", "negative"):
            prompt[conditioning]["inputs"]["image"] = ["identity", 0]
            prompt[conditioning]["inputs"].pop("image_b")
    prompt["unet"]["inputs"]["unet_name"] = model_name
    prompt["positive"]["inputs"].update(
        {"prompt": instruction, "grounding_px": grounding_px}
    )
    prompt["negative"]["inputs"]["grounding_px"] = grounding_px
    prompt["latent"]["inputs"].update({"width": width, "height": height})
    prompt["patch"]["inputs"]["ref_boost"] = ref_boost
    effective_seed = appearance["samplerSeed"] if appearance is not None else seed
    prompt["sampler"]["inputs"].update(
        {"seed": effective_seed, "steps": steps, "cfg": cfg}
    )
    prompt["save"]["inputs"]["filename_prefix"] = f"{_OUTPUT_ROOT}/seed-{effective_seed}"
    if appearance is not None:
        _add_appearance_bucket_nodes(prompt, instruction, appearance)


def _number_cell(
    *,
    node_id: str,
    id: str,
    label: str,
    value: str,
    minimum: float,
    maximum: float,
    step: float,
    helper: str,
) -> WorkflowCell:
    return WorkflowCell(
        node_id=node_id,
        id=id,
        value=label,
        shape="textfield",
        props={
            "lfHtmlAttributes": {
                "autocomplete": "off",
                "name": id,
                "type": "number",
                "min": minimum,
                "max": maximum,
                "step": step,
            },
            "lfLabel": label,
            "lfHelper": {"showWhenFocused": False, "value": helper},
            "lfValue": value,
        },
    )


def _choice_cell(
    *, node_id: str, id: str, label: str, value: str, choices: tuple[str, ...], helper: str
) -> WorkflowCell:
    return WorkflowCell(
        node_id=node_id,
        id=id,
        value=label,
        shape="choice",
        description=helper,
        props={
            "lfDataset": {"nodes": [{"id": choice, "value": choice} for choice in choices]},
            "lfTextfieldProps": {
                "lfLabel": label,
                "lfHelper": {"showWhenFocused": False, "value": helper},
            },
            "lfValue": value,
        },
    )


input_scene = WorkflowCell(
    node_id="scene",
    id="scene_image",
    value="Scene frame (optional reference 1)",
    shape="upload",
    description="Optional. When supplied, this is reference 1 and anchors composition, pose, and environment. Omit it for a native identity-only edit.",
    props={"lfHtmlAttributes": {"accept": "image/*"}, "lfLabel": "Scene frame (optional reference 1)"},
    required=False,
)
input_identity = WorkflowCell(
    node_id="identity",
    id="identity_image",
    value="Canonical identity",
    shape="upload",
    description="Required. This is reference 2 when a scene is supplied, or the sole reference when the scene is omitted.",
    props={"lfHtmlAttributes": {"accept": "image/*"}, "lfLabel": "Canonical identity (required)"},
)
input_prompt = WorkflowCell(
    node_id="positive",
    id="prompt",
    value="Restoration instruction",
    shape="textfield",
    props={
        "lfHtmlAttributes": {"autocomplete": "off", "name": "prompt", "type": "text"},
        "lfLabel": "Restoration instruction",
        "lfHelper": {
            "showWhenFocused": False,
            "value": "Describe the desired image. With a scene reference, say what to preserve from it; without one, direct the identity-only edit freely.",
        },
        "lfStyling": "textarea",
        "lfValue": "Use the supplied canonical identity to create the requested image. Preserve the character's identity and defining features.",
    },
)
input_model = _choice_cell(
    node_id="unet",
    id="model_name",
    label="Krea 2 model",
    value=_DEFAULT_MODEL,
    choices=_MODEL_NAMES,
    helper="Only the two locally available KR2 checkpoints are intentionally exposed for this proof.",
)
input_width = _number_cell(node_id="latent", id="width", label="Width", value="1024", minimum=256, maximum=_MAX_EDGE, step=_CANVAS_MULTIPLE, helper="Output canvas; multiples of 16 only and no more than 2MP.")
input_height = _number_cell(node_id="latent", id="height", label="Height", value="1536", minimum=256, maximum=_MAX_EDGE, step=_CANVAS_MULTIPLE, helper="Output canvas; multiples of 16 only and no more than 2MP.")
input_seed = _number_cell(node_id="sampler", id="seed", label="Seed", value="42", minimum=0, maximum=_MAX_SEED, step=1, helper="Reuse a seed for controlled restoration comparisons.")
input_steps = _number_cell(node_id="sampler", id="steps", label="Steps", value="10", minimum=8, maximum=12, step=1, helper="Turbo-style Krea 2 Identity Edit proof range: 8–12 steps.")
input_cfg = _number_cell(node_id="sampler", id="cfg", label="CFG", value="1", minimum=0, maximum=20, step=0.1, helper="CFG 1 is the recommended turbo-style starting point.")
input_ref_boost = _number_cell(node_id="patch", id="ref_boost", label="Identity fidelity", value="4", minimum=0, maximum=100, step=0.1, helper="Canonical identity fidelity dial. Four is the v1.2 recommended starting point.")
input_grounding = _number_cell(node_id="positive", id="grounding_px", label="Grounding pixels", value="1024", minimum=384, maximum=2048, step=64, helper="Qwen3-VL grounding resolution; 1024 favors person identity and detail.")
input_appearance_buckets = WorkflowCell(
    node_id="positive",
    id="appearance_buckets",
    value="Appearance buckets (optional sealed runtime wire)",
    shape="textfield",
    description="Optional. A Velora-sealed weighted prompt-bucket wire. Leave empty to preserve the original Krea prompt graph exactly.",
    props={
        "lfHtmlAttributes": {
            "autocomplete": "off",
            "name": "appearance_buckets",
            "type": "text",
        },
        "lfLabel": "Appearance buckets (optional sealed runtime wire)",
        "lfHelper": {
            "showWhenFocused": False,
            "value": "Advanced Velora input. Its JSON buckets are compiled into native LF nodes only when supplied.",
        },
        "lfStyling": "textarea",
        "lfValue": "",
    },
    required=False,
)

output_image = WorkflowCell(node_id="save", id="image", shape="masonry", description="One Krea 2 Identity Edit restoration PNG")


id = "velora_krea2_identity_edit"
node = WorkflowNode(
    id=id,
    value="Velora Krea 2 Identity Edit",
    description=(
        "Create from a canonical character alone, or restore one into an optional scene, "
        "with Krea 2 Identity Edit v1.2. With a scene it is reference one and identity "
        "is reference two; without a scene identity is the sole reference."
    ),
    category="Image Editing",
    inputs=[
        input_scene, input_identity, input_prompt, input_model, input_width, input_height,
        input_seed, input_steps, input_cfg, input_ref_boost, input_grounding,
        input_appearance_buckets,
    ],
    outputs=[output_image],
    configure_prompt=_configure,
    workflow_path=Path(__file__).resolve().with_suffix(".json"),
    submission_policy=WorkflowSubmissionPolicy(
        provider_id="velora_guarded_v1",
        expected_vram_mb=20_000,
        max_duration_seconds=600,
        required=True,
    ),
)

WORKFLOW = node
