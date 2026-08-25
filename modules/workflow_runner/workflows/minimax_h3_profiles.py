"""Central execution profiles for MiniMax H3 workflows.

The profile is the operator-facing contract.  It deliberately owns the
sampling accelerator, step count, cache compatibility, and canvas tier so a
caller does not need to reconstruct a fragile node recipe for every run.

``manual_advanced`` preserves the pre-profile API: callers may choose their own
step count and EasyCache setting and may use the experimental two-megapixel
canvas.  All named production/preview profiles are deterministic.
"""

from __future__ import annotations

from typing import NamedTuple


# Core constrains the native canvas by a 768x1344 pixel-area budget, not by a
# universal 1344-pixel edge. Ultra-wide ratios can therefore reach 1536x672
# while staying inside the same trained-area envelope.
NATIVE_MAX_EDGE = 1536
NATIVE_MAX_PIXELS = 1344 * 768
EXPERIMENTAL_MAX_EDGE = 1920
EXPERIMENTAL_MAX_PIXELS = 1920 * 1088
KITCHEN_TURBO_8STEP_LORA = (
    "MiniMax-H3\\minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors"
)


class MiniMaxH3ExecutionProfile(NamedTuple):
    id: str
    accelerator: str
    steps: int | None
    max_edge: int
    max_pixels: int
    description: str

    @property
    def is_manual(self) -> bool:
        return self.accelerator == "manual"


_PROFILES = {
    "native_quality": MiniMaxH3ExecutionProfile(
        id="native_quality",
        accelerator="native",
        steps=20,
        max_edge=NATIVE_MAX_EDGE,
        max_pixels=NATIVE_MAX_PIXELS,
        description=(
            "Official open-weight H3 baseline: native one-megapixel canvas, "
            "20 RES multistep evaluations, and no approximate cache."
        ),
    ),
    "kitchen_quality": MiniMaxH3ExecutionProfile(
        id="kitchen_quality",
        accelerator="kitchen",
        steps=20,
        max_edge=NATIVE_MAX_EDGE,
        max_pixels=NATIVE_MAX_PIXELS,
        description=(
            "Official open-weight H3 baseline with the core Comfy Kitchen "
            "attention backend and the same native one-megapixel canvas."
        ),
    ),
    "kitchen_turbo_8step": MiniMaxH3ExecutionProfile(
        id="kitchen_turbo_8step",
        accelerator="kitchen_turbo",
        steps=8,
        max_edge=NATIVE_MAX_EDGE,
        max_pixels=NATIVE_MAX_PIXELS,
        description=(
            "Guarded FL2VA candidate: Comfy Kitchen attention followed by the "
            "pinned MiniMax-H3 8-step LoRA, Euler sampling, and the "
            "linear_quadratic schedule. Requires the exact LoRA asset; it is "
            "not silently substituted with Turbo v4."
        ),
    ),
    "spectrum_preview": MiniMaxH3ExecutionProfile(
        id="spectrum_preview",
        accelerator="spectrum",
        steps=20,
        max_edge=NATIVE_MAX_EDGE,
        max_pixels=NATIVE_MAX_PIXELS,
        description=(
            "Spectrum v0.2.1 offline replay over the native 20-step schedule. "
            "Approximate and intended for same-seed preview A/B tests."
        ),
    ),
    "turbo_preview": MiniMaxH3ExecutionProfile(
        id="turbo_preview",
        accelerator="turbo",
        steps=6,
        max_edge=NATIVE_MAX_EDGE,
        max_pixels=NATIVE_MAX_PIXELS,
        description=(
            "Six-step Larryvrh v4 Turbo LoRA preview for FL2VA T2V/I2V. "
            "Not admitted for REF2VA identity runs."
        ),
    ),
    "experimental_2mp": MiniMaxH3ExecutionProfile(
        id="experimental_2mp",
        accelerator="native",
        steps=20,
        max_edge=EXPERIMENTAL_MAX_EDGE,
        max_pixels=EXPERIMENTAL_MAX_PIXELS,
        description=(
            "Base-H3 extrapolation up to 1920x1088. This is not the unavailable "
            "H3-Regenerate-2K pipeline and may smear distant detail."
        ),
    ),
    "manual_advanced": MiniMaxH3ExecutionProfile(
        id="manual_advanced",
        accelerator="manual",
        steps=None,
        max_edge=EXPERIMENTAL_MAX_EDGE,
        max_pixels=EXPERIMENTAL_MAX_PIXELS,
        description=(
            "Legacy expert mode: caller-owned steps and optional EasyCache. "
            "No quality or compatibility claim is implied."
        ),
    ),
}

FL2VA_PROFILE_IDS = (
    "native_quality",
    "kitchen_quality",
    "kitchen_turbo_8step",
    "spectrum_preview",
    "turbo_preview",
    "experimental_2mp",
    "manual_advanced",
)
REF2VA_PROFILE_IDS = (
    "native_quality",
    "kitchen_quality",
    "spectrum_preview",
    "experimental_2mp",
    "manual_advanced",
)


def resolve_h3_execution_profile(
    profile_id: str,
    *,
    family: str,
) -> MiniMaxH3ExecutionProfile:
    """Resolve a profile and enforce the FL2VA/REF2VA capability boundary."""

    if family == "fl2va":
        allowed = FL2VA_PROFILE_IDS
    elif family == "ref2va":
        allowed = REF2VA_PROFILE_IDS
    else:
        raise ValueError(f"Unknown MiniMax H3 family: {family!r}.")

    if profile_id not in allowed:
        if profile_id == "turbo_preview" and family == "ref2va":
            raise ValueError(
                "turbo_preview is not validated for MiniMax H3 REF2VA; use "
                "kitchen_quality, spectrum_preview, or native_quality."
            )
        raise ValueError(
            f"Unknown MiniMax H3 {family} execution profile: {profile_id!r}."
        )
    return _PROFILES[profile_id]


def h3_profile_descriptions(profile_ids: tuple[str, ...]) -> str:
    """Return compact UI help without duplicating profile semantics."""

    return " ".join(f"{profile_id}: {_PROFILES[profile_id].description}" for profile_id in profile_ids)


__all__ = [
    "EXPERIMENTAL_MAX_EDGE",
    "EXPERIMENTAL_MAX_PIXELS",
    "FL2VA_PROFILE_IDS",
    "MiniMaxH3ExecutionProfile",
    "NATIVE_MAX_EDGE",
    "NATIVE_MAX_PIXELS",
    "KITCHEN_TURBO_8STEP_LORA",
    "REF2VA_PROFILE_IDS",
    "h3_profile_descriptions",
    "resolve_h3_execution_profile",
]
