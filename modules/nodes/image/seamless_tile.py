from __future__ import annotations

import math
from typing import Any

import torch

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import normalize_list_to_value, normalize_output_image
from ...utils.helpers.ui import cache_generated_preview, create_masonry_node


SEAMLESS_TILE_RECEIPT_SCHEMA = "lf.seamless_tile.receipt.v1"
_MIN_BLEND = 0.02
_MAX_BLEND = 0.5


def _blend_fraction(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"blend_fraction must be a number between {_MIN_BLEND} and {_MAX_BLEND}.")
    parsed = float(value)
    if not math.isfinite(parsed) or parsed < _MIN_BLEND or parsed > _MAX_BLEND:
        raise ValueError(f"blend_fraction must be a number between {_MIN_BLEND} and {_MAX_BLEND}.")
    return parsed


def _ramp(length: int, center: float, band: float) -> torch.Tensor:
    positions = torch.arange(length, dtype=torch.float32) + 0.5
    return (1.0 - (positions - center).abs() / band).clamp(0.0, 1.0)


def _edge_fade(length: int, band: float) -> torch.Tensor:
    positions = torch.arange(length, dtype=torch.float32) + 0.5
    return (torch.minimum(positions, float(length) - positions) / band).clamp(0.0, 1.0)


def make_seamless_tile(
    image: torch.Tensor,
    *,
    blend_fraction: float = 0.25,
) -> tuple[torch.Tensor, dict[str, Any]]:
    """Make each image wrap without a visible seam, deterministically.

    The image rolled by half its size wraps perfectly at the output edges (they
    were the original's centre) but carries the original's edges as a cross in
    the middle. That cross is hidden by blending the untouched original back in
    over a soft band, faded out again toward the output edges so the wrap is
    never disturbed. No diffusion pass, no randomness.
    """

    if not isinstance(image, torch.Tensor) or image.ndim != 4:
        raise ValueError("image must be a batch shaped [count, height, width, channels].")
    blend_fraction = _blend_fraction(blend_fraction)
    _count, height, width, _channels = image.shape
    if height < 8 or width < 8:
        raise ValueError("image must be at least 8 x 8 pixels.")
    band_y = max(1.0, blend_fraction * float(height))
    band_x = max(1.0, blend_fraction * float(width))
    row_weight = _ramp(height, float(height) / 2.0, band_y) * 1.0
    column_weight = _ramp(width, float(width) / 2.0, band_x) * 1.0
    horizontal_band = row_weight.unsqueeze(1) * _edge_fade(width, band_x).unsqueeze(0)
    vertical_band = column_weight.unsqueeze(0) * _edge_fade(height, band_y).unsqueeze(1)
    mask = torch.maximum(horizontal_band, vertical_band).to(image.dtype)
    mask = mask.unsqueeze(0).unsqueeze(3)
    rolled = torch.roll(image, shifts=(height // 2, width // 2), dims=(1, 2))
    result = mask * image + (1.0 - mask) * rolled
    receipt = {
        "schema": SEAMLESS_TILE_RECEIPT_SCHEMA,
        "count": int(image.shape[0]),
        "width": int(width),
        "height": int(height),
        "blendFraction": blend_fraction,
        "blendBandPx": {"x": band_x, "y": band_y},
        "method": "half-roll with centre-cross blend, edge-faded",
    }
    return result.contiguous(), receipt


class LF_SeamlessTile:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (
                    Input.IMAGE,
                    {"tooltip": "Texture(s) to make tileable. Output keeps the input size."},
                ),
                "blend_fraction": (
                    Input.FLOAT,
                    {
                        "default": 0.25,
                        "min": _MIN_BLEND,
                        "max": _MAX_BLEND,
                        "step": 0.01,
                        "tooltip": (
                            "Width of the blend band as a fraction of the image size. Wider hides "
                            "the seam better and softens more of the centre."
                        ),
                    },
                ),
            },
            "optional": {
                "ui_widget": (Input.LF_MASONRY, {"default": {}}),
            },
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    DESCRIPTION = "Make a texture wrap seamlessly with a deterministic half-roll blend."
    FUNCTION = FUNCTION
    OUTPUT_IS_LIST = (False, False, True)
    RETURN_NAMES = ("image", "receipt", "image_list")
    OUTPUT_TOOLTIPS = (
        "Seamlessly wrapping texture batch at the source size.",
        "Receipt with the blend fraction and per-image dimensions.",
        "The same wrapped textures as an authoritative list.",
    )
    RETURN_TYPES = (Input.IMAGE, Input.JSON, Input.IMAGE)

    def on_exec(self, image: torch.Tensor, blend_fraction: float, **kwargs: Any) -> dict[str, Any]:
        result, receipt = make_seamless_tile(
            image, blend_fraction=normalize_list_to_value(blend_fraction)
        )
        nodes: list[dict[str, Any]] = []
        for index in range(min(int(result.shape[0]), 16)):
            preview = cache_generated_preview(result[index].unsqueeze(0))
            node = create_masonry_node(f"Seamless {index}", preview.url, index)
            node["cells"]["lfImage"]["htmlProps"]["title"] = f"Seamless {index}"
            nodes.append(node)
        payload = {"dataset": {"nodes": nodes}, "receipt": receipt}
        safe_send_sync("seamlesstile", payload, normalize_list_to_value(kwargs.get("node_id")))
        _, image_list = normalize_output_image(result)
        return {"ui": {"lf_output": [payload]}, "result": (result, receipt, image_list)}


NODE_CLASS_MAPPINGS = {
    "LF_SeamlessTile": LF_SeamlessTile,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_SeamlessTile": "Seamless tile",
}
