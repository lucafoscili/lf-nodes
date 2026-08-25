"""Shared tensor primitives for deterministic image composites."""

from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import torch
import torch.nn.functional as F


MAX_COMPOSITE_PIXELS = 64_000_000

_ALPHA_EPSILON = 1e-6
_MAX_LABEL_LENGTH = 64


def validate_composite_image(image: torch.Tensor, name: str) -> torch.Tensor:
    """Validate and normalize a Comfy IMAGE tensor for compositing."""

    if not isinstance(image, torch.Tensor):
        raise TypeError(f"{name} must be an IMAGE tensor.")

    if image.ndim == 3:
        image = image.unsqueeze(0)
    if image.ndim != 4:
        raise ValueError(
            f"{name} must use BHWC or HWC layout; got shape {tuple(image.shape)}."
        )

    batch, height, width, channels = image.shape
    if batch < 1 or height < 1 or width < 1:
        raise ValueError(f"{name} must contain at least one non-empty image.")
    if channels not in (3, 4):
        raise ValueError(
            f"{name} must have 3 (RGB) or 4 (RGBA) channels; got {channels}."
        )
    if not torch.is_floating_point(image):
        raise TypeError(f"{name} must be a floating-point IMAGE tensor in [0, 1].")
    if not bool(torch.isfinite(image).all()):
        raise ValueError(f"{name} contains NaN or infinite values.")

    return image.to(dtype=torch.float32).clamp(0.0, 1.0)


def validate_composite_integer(value: int, name: str, *, minimum: int) -> int:
    """Validate an integer option used to size an image composite."""

    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(
            f"{name} must be an integer greater than or equal to {minimum}."
        )
    if value < minimum:
        raise ValueError(f"{name} must be greater than or equal to {minimum}.")
    return value


def resize_composite_image(
    image: torch.Tensor,
    target_height: int,
    target_width: int,
) -> torch.Tensor:
    """Resize a BHWC image batch, preserving RGBA through premultiplication."""

    if image.shape[1:3] == (target_height, target_width):
        return image

    channels_first = image.permute(0, 3, 1, 2)
    resize_options = {
        "size": (target_height, target_width),
        "mode": "bicubic",
        "align_corners": False,
        "antialias": True,
    }

    if image.shape[-1] == 4:
        rgb = channels_first[:, :3]
        alpha = channels_first[:, 3:4]
        resized_alpha = F.interpolate(alpha, **resize_options).clamp(0.0, 1.0)
        resized_premultiplied = F.interpolate(rgb * alpha, **resize_options).clamp(
            0.0, 1.0
        )
        resized_rgb = torch.where(
            resized_alpha > _ALPHA_EPSILON,
            resized_premultiplied / resized_alpha.clamp_min(_ALPHA_EPSILON),
            torch.zeros_like(resized_premultiplied),
        ).clamp(0.0, 1.0)
        resized = torch.cat((resized_rgb, resized_alpha), dim=1)
    else:
        resized = F.interpolate(channels_first, **resize_options).clamp(0.0, 1.0)

    return resized.permute(0, 2, 3, 1)


def promote_to_rgba(image: torch.Tensor) -> torch.Tensor:
    """Return an RGBA image batch, adding an opaque alpha channel to RGB."""

    if image.shape[-1] == 4:
        return image
    alpha = torch.ones(
        (*image.shape[:-1], 1), device=image.device, dtype=image.dtype
    )
    return torch.cat((image, alpha), dim=-1)


def _normalized_label(value: str) -> str:
    label = str(value).replace("\r", " ").replace("\n", " ").strip()
    return label[:_MAX_LABEL_LENGTH]


def render_label_chip(
    label: str,
    *,
    max_width: int,
    max_height: int,
    channels: int,
) -> torch.Tensor | None:
    """Render a deterministic black-and-white label chip as an HWC tensor."""

    label = _normalized_label(label)
    if not label or max_width < 1 or max_height < 1:
        return None

    font_size = max(8, min(32, max_height // 8))
    try:
        font = ImageFont.load_default(size=font_size)
    except TypeError:  # pragma: no cover - compatibility with older Pillow releases
        font = ImageFont.load_default()

    probe = Image.new("L", (1, 1))
    probe_draw = ImageDraw.Draw(probe)
    if hasattr(probe_draw, "textbbox"):
        left, top, right, bottom = probe_draw.textbbox((0, 0), label, font=font)
        text_width = max(1, right - left)
        text_height = max(1, bottom - top)
    else:  # pragma: no cover - compatibility with older Pillow releases
        text_width, text_height = probe_draw.textsize(label, font=font)
        left = top = 0

    padding = max(2, font_size // 4)
    chip_width = min(max_width, text_width + padding * 2)
    chip_height = min(max_height, text_height + padding * 2)
    if chip_width < 1 or chip_height < 1:
        return None

    mode = "RGBA" if channels == 4 else "RGB"
    background = (0, 0, 0, 255) if channels == 4 else (0, 0, 0)
    foreground = (255, 255, 255, 255) if channels == 4 else (255, 255, 255)
    chip = Image.new(mode, (chip_width, chip_height), background)
    draw = ImageDraw.Draw(chip)
    draw.text(
        (padding - left, padding - top),
        label,
        fill=foreground,
        font=font,
    )
    pixels = np.array(chip, dtype=np.float32, copy=True) / 255.0
    return torch.from_numpy(pixels)


__all__ = [
    "MAX_COMPOSITE_PIXELS",
    "promote_to_rgba",
    "render_label_chip",
    "resize_composite_image",
    "validate_composite_image",
    "validate_composite_integer",
]
