from __future__ import annotations

from typing import Callable, Dict, Tuple

import torch

from ..helpers.conversion import (
    base64_to_tensor,
    convert_to_boolean,
    convert_to_float,
    convert_to_int,
)
from ..helpers.torch import create_colored_tensor
from .blend import blend_effect
from .bloom import bloom_effect
from .brightness import brightness_effect
from .clarity import clarity_effect
from .contrast import contrast_effect
from .desaturate import desaturate_effect
from .film_grain import film_grain_effect
from .gaussian_blur import gaussian_blur_effect
from .inpaint import apply_inpaint_filter
from .line import line_effect
from .saturation import saturation_effect
from .sepia import sepia_effect
from .split_tone import split_tone_effect
from .tilt_shift import tilt_shift_effect
from .vibrance import vibrance_effect
from .vignette import vignette_effect

FilterPayload = Dict[str, str]
FilterResult = Tuple[torch.Tensor, FilterPayload]
FilterProcessor = Callable[[torch.Tensor, dict], FilterResult]


class UnknownFilterError(ValueError):
    """Raised when a filter type is not registered."""


def _as_result(image: torch.Tensor) -> FilterResult:
    return image, {}


def apply_blend_filter(image: torch.Tensor, settings: dict) -> FilterResult:
    opacity = convert_to_float(settings.get("opacity", 1.0))
    color: str = settings.get("color", "FF0000")
    overlay_image = create_colored_tensor(image, color)
    return _as_result(blend_effect(image, overlay_image, opacity))


def apply_bloom_filter(image: torch.Tensor, settings: dict) -> FilterResult:
    intensity = convert_to_float(settings.get("intensity", 0.0))
    radius = convert_to_int(settings.get("radius", 0))
    threshold = convert_to_float(settings.get("threshold", 0.0))
    tint = settings.get("tint", "FFFFFF")
    return _as_result(bloom_effect(image, threshold, radius, intensity, tint))


def apply_brightness_filter(image: torch.Tensor, settings: dict) -> FilterResult:
    strength = convert_to_float(settings.get("strength", 0.0))
    gamma = convert_to_float(settings.get("gamma", 0.0))
    midpoint = convert_to_float(settings.get("midpoint", 0.0))
    localized = convert_to_boolean(settings.get("localized", False))
    return _as_result(brightness_effect(image, strength, gamma, midpoint, localized))


def apply_brush_filter(image: torch.Tensor, settings: dict) -> FilterResult:
    canvas_b64: str = settings.get("b64_canvas", "")
    canvas = base64_to_tensor(canvas_b64, True)
    return _as_result(blend_effect(image, canvas, 1.0))


def apply_clarity_filter(image: torch.Tensor, settings: dict) -> FilterResult:
    clarity_strength = convert_to_float(settings.get("clarity_strength", 0.0))
    sharpen_amount = convert_to_float(settings.get("sharpen_amount", 0.0))
    blur_kernel_size = convert_to_int(settings.get("blur_kernel_size", 1))
    return _as_result(clarity_effect(image, clarity_strength, sharpen_amount, blur_kernel_size))


def apply_contrast_filter(image: torch.Tensor, settings: dict) -> FilterResult:
    strength = convert_to_float(settings.get("strength", 0.0))
    midpoint = convert_to_float(settings.get("midpoint", 0.0))
    localized = convert_to_boolean(settings.get("localized", False))
    return _as_result(contrast_effect(image, strength, midpoint, localized))


def apply_desaturate_filter(image: torch.Tensor, settings: dict) -> FilterResult:
    strength = convert_to_float(settings.get("strength", 0.0))
    r = convert_to_float(settings.get("r_channel", 1.0))
    g = convert_to_float(settings.get("g_channel", 1.0))
    b = convert_to_float(settings.get("b_channel", 1.0))
    return _as_result(desaturate_effect(image, strength, [r, g, b]))


def apply_film_grain_filter(image: torch.Tensor, settings: dict) -> FilterResult:
    intensity = convert_to_float(settings.get("intensity", 0.0))
    size = convert_to_float(settings.get("size", 1.0))
    tint = settings.get("tint", "FFFFFF")
    soft_blend = convert_to_boolean(settings.get("soft_blend", False))
    return _as_result(film_grain_effect(image, intensity, size, tint, soft_blend))


def apply_gaussian_blur_filter(image: torch.Tensor, settings: dict) -> FilterResult:
    sigma = convert_to_float(settings.get("blur_sigma", 0.0))
    kernel_size = convert_to_int(settings.get("blur_kernel_size", 1))
    return _as_result(gaussian_blur_effect(image, kernel_size, sigma))


def apply_line_filter(image: torch.Tensor, settings: dict) -> FilterResult:
    points_setting = settings.get("points", []) or []
    points = [(point["x"], point["y"]) for point in points_setting]
    size = convert_to_int(settings.get("size", 0))
    color = settings.get("color", "FF0000")
    opacity = convert_to_float(settings.get("opacity", 1.0))
    smooth = convert_to_boolean(settings.get("smoooth", False))
    return _as_result(line_effect(image, points, size, color, opacity, smooth))


def apply_saturation_filter(image: torch.Tensor, settings: dict) -> FilterResult:
    intensity = convert_to_float(settings.get("intensity", 1.0))
    return _as_result(saturation_effect(image, intensity))


def apply_sepia_filter(image: torch.Tensor, settings: dict) -> FilterResult:
    intensity = convert_to_float(settings.get("intensity", 0.0))
    return _as_result(sepia_effect(image, intensity))


def apply_split_tone_filter(image: torch.Tensor, settings: dict) -> FilterResult:
    highlights = settings.get("highlights", "FFAA55")
    shadows = settings.get("shadows", "0066FF")
    balance = convert_to_float(settings.get("balance", 0.0))
    softness = convert_to_float(settings.get("softness", 0.0))
    intensity = convert_to_float(settings.get("intensity", 0.0))
    return _as_result(split_tone_effect(image, shadows, highlights, balance, softness, intensity))


def apply_tilt_shift_filter(image: torch.Tensor, settings: dict) -> FilterResult:
    focus_position = convert_to_float(settings.get("focus_position", 0.5))
    focus_size = convert_to_float(settings.get("focus_size", 0.25))
    blur_radius = convert_to_int(settings.get("radius", 25))
    feather = settings.get("feather", "smooth")
    orientation = settings.get("orientation", "horizontal")
    return _as_result(tilt_shift_effect(image, focus_position, focus_size, blur_radius, feather, orientation))


def apply_vibrance_filter(image: torch.Tensor, settings: dict) -> FilterResult:
    intensity = convert_to_float(settings.get("intensity", 0.0))
    protect_skin = convert_to_boolean(settings.get("protect_skin", False))
    clip_soft = convert_to_boolean(settings.get("clip_soft", False))
    return _as_result(vibrance_effect(image, intensity, protect_skin, clip_soft))


def apply_vignette_filter(image: torch.Tensor, settings: dict) -> FilterResult:
    intensity = convert_to_float(settings.get("intensity", 0.0))
    radius = convert_to_float(settings.get("radius", 0.0))
    shape = settings.get("shape", "elliptical")
    color = settings.get("color", "000000")
    return _as_result(vignette_effect(image, intensity, radius, shape, color))


FILTER_PROCESSORS: Dict[str, FilterProcessor] = {
    "blend": apply_blend_filter,
    "bloom": apply_bloom_filter,
    "brightness": apply_brightness_filter,
    "brush": apply_brush_filter,
    "clarity": apply_clarity_filter,
    "contrast": apply_contrast_filter,
    "desaturate": apply_desaturate_filter,
    "film_grain": apply_film_grain_filter,
    "gaussian_blur": apply_gaussian_blur_filter,
    "inpaint": apply_inpaint_filter,
    "line": apply_line_filter,
    "saturation": apply_saturation_filter,
    "sepia": apply_sepia_filter,
    "split_tone": apply_split_tone_filter,
    "tilt_shift": apply_tilt_shift_filter,
    "vibrance": apply_vibrance_filter,
    "vignette": apply_vignette_filter,
}


def process_filter(filter_type: str, image: torch.Tensor, settings: dict) -> FilterResult:
    try:
        processor = FILTER_PROCESSORS[filter_type]
    except KeyError as exc:
        raise UnknownFilterError(f"Unsupported filter type: {filter_type}") from exc
    return processor(image, settings)


__all__ = [
    "FilterPayload",
    "FilterProcessor",
    "FilterResult",
    "UnknownFilterError",
    "FILTER_PROCESSORS",
    "apply_bloom_filter",
    "apply_blend_filter",
    "apply_brightness_filter",
    "apply_brush_filter",
    "apply_clarity_filter",
    "apply_contrast_filter",
    "apply_desaturate_filter",
    "apply_film_grain_filter",
    "apply_gaussian_blur_filter",
    "apply_line_filter",
    "apply_saturation_filter",
    "apply_sepia_filter",
    "apply_split_tone_filter",
    "apply_tilt_shift_filter",
    "apply_vibrance_filter",
    "apply_vignette_filter",
    "process_filter",
]
