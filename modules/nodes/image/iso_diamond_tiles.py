from __future__ import annotations

import math
from typing import Any

import torch
from torch.nn import functional

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import normalize_list_to_value, normalize_output_image
from ...utils.helpers.ui import cache_generated_preview, create_masonry_node


ISO_DIAMOND_RECEIPT_SCHEMA = "lf.iso_diamond_tiles.receipt.v1"
_MAX_TILE_EDGE = 1024
_MAX_VARIANTS = 64


def _integer(value: Any, name: str, *, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum or value > maximum:
        raise ValueError(f"{name} must be an integer between {minimum} and {maximum}.")
    return value


def _fraction(value: Any, name: str, *, minimum: float, maximum: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number between {minimum} and {maximum}.")
    parsed = float(value)
    if not math.isfinite(parsed) or parsed < minimum or parsed > maximum:
        raise ValueError(f"{name} must be a number between {minimum} and {maximum}.")
    return parsed


def diamond_alpha(tile_width: int, tile_height: int) -> torch.Tensor:
    """Antialiased coverage of the isometric diamond inscribed in the tile."""

    ys = (torch.arange(tile_height, dtype=torch.float32) + 0.5) / float(tile_height) * 2.0 - 1.0
    xs = (torch.arange(tile_width, dtype=torch.float32) + 0.5) / float(tile_width) * 2.0 - 1.0
    distance = ys.abs().unsqueeze(1) + xs.abs().unsqueeze(0)
    edge = float(min(tile_width, tile_height)) / 2.0
    return ((1.0 - distance) * edge + 0.5).clamp(0.0, 1.0)


def render_iso_diamond_tiles(
    texture: torch.Tensor,
    *,
    tile_width: int = 128,
    tile_height: int = 64,
    variants: int = 4,
    seed: int = 42,
    texture_scale: float = 0.5,
) -> tuple[torch.Tensor, torch.Tensor, dict[str, Any]]:
    """Derive isometric diamond tiles from one seamless top-down texture.

    A diamond is the top-down square rotated 45 degrees and squashed 2:1, so
    every variant is the same affine sample of the texture at a different
    seeded offset. Because the texture wraps, every diamond tiles with every
    other. Returns the tiles [variants, h, w, 4], a one-row atlas, and a receipt.
    """

    if not isinstance(texture, torch.Tensor) or texture.ndim != 4 or texture.shape[0] < 1:
        raise ValueError("texture must be an image batch shaped [count, height, width, channels].")
    tile_width = _integer(tile_width, "tile_width", minimum=8, maximum=_MAX_TILE_EDGE)
    tile_height = _integer(tile_height, "tile_height", minimum=4, maximum=_MAX_TILE_EDGE)
    variants = _integer(variants, "variants", minimum=1, maximum=_MAX_VARIANTS)
    seed = _integer(seed, "seed", minimum=0, maximum=2**31 - 1)
    texture_scale = _fraction(texture_scale, "texture_scale", minimum=0.05, maximum=4.0)

    source = texture[0, ..., :3].float().permute(2, 0, 1).unsqueeze(0)  # [1, 3, H, W]
    doubled = source.repeat(1, 1, 2, 2)
    ys = (torch.arange(tile_height, dtype=torch.float32) + 0.5) / float(tile_height) * 2.0 - 1.0
    xs = (torch.arange(tile_width, dtype=torch.float32) + 0.5) / float(tile_width) * 2.0 - 1.0
    py = ys.unsqueeze(1).expand(tile_height, tile_width)
    px = xs.unsqueeze(0).expand(tile_height, tile_width)
    u = (px + py) / 2.0 + 0.5
    v = (px - py) / 2.0 + 0.5
    alpha = diamond_alpha(tile_width, tile_height)

    generator = torch.Generator().manual_seed(seed)
    offsets = torch.rand((variants, 2), generator=generator)
    tiles: list[torch.Tensor] = []
    for index in range(variants):
        offset_u = float(offsets[index, 0])
        offset_v = float(offsets[index, 1])
        tu = torch.remainder(offset_u + u * texture_scale, 1.0)
        tv = torch.remainder(offset_v + v * texture_scale, 1.0)
        # Doubled texture: normalized coordinate for texture position t*W is t - 1.
        grid = torch.stack([tu - 1.0, tv - 1.0], dim=2).unsqueeze(0)
        sampled = functional.grid_sample(
            doubled, grid, mode="bilinear", padding_mode="border", align_corners=False
        )
        rgb = sampled[0].permute(1, 2, 0)  # [h, w, 3]
        tiles.append(torch.cat([rgb, alpha.unsqueeze(2)], dim=2))
    stacked = torch.stack(tiles, dim=0).contiguous()
    atlas = torch.cat(list(stacked), dim=1).unsqueeze(0).contiguous()
    receipt = {
        "schema": ISO_DIAMOND_RECEIPT_SCHEMA,
        "tileWidth": tile_width,
        "tileHeight": tile_height,
        "variants": variants,
        "seed": seed,
        "textureScale": texture_scale,
        "textureSize": {"width": int(source.shape[3]), "height": int(source.shape[2])},
        "offsets": [[float(offsets[i, 0]), float(offsets[i, 1])] for i in range(variants)],
        "atlasSize": {"width": int(atlas.shape[2]), "height": int(atlas.shape[1])},
        "projection": "top-down square rotated 45 degrees, squashed 2:1; transparent corners",
    }
    return stacked, atlas, receipt


class LF_IsoDiamondTiles:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (
                    Input.IMAGE,
                    {"tooltip": "One seamless top-down texture; only the first image is used."},
                ),
                "tile_width": (
                    Input.INTEGER,
                    {"default": 128, "min": 8, "max": _MAX_TILE_EDGE, "step": 2, "tooltip": "Diamond tile width in pixels."},
                ),
                "tile_height": (
                    Input.INTEGER,
                    {"default": 64, "min": 4, "max": _MAX_TILE_EDGE, "step": 2, "tooltip": "Diamond tile height in pixels (half the width for 2:1)."},
                ),
                "variants": (
                    Input.INTEGER,
                    {"default": 4, "min": 1, "max": _MAX_VARIANTS, "step": 1, "tooltip": "How many differently offset diamonds to cut."},
                ),
                "seed": (
                    Input.INTEGER,
                    {"default": 42, "min": 0, "max": 2**31 - 1, "step": 1, "tooltip": "Seed for the variant offsets."},
                ),
                "texture_scale": (
                    Input.FLOAT,
                    {
                        "default": 0.5,
                        "min": 0.05,
                        "max": 4.0,
                        "step": 0.05,
                        "tooltip": "Fraction of the texture one diamond spans along its diagonal.",
                    },
                ),
            },
            "optional": {
                "ui_widget": (Input.LF_MASONRY, {"default": {}}),
            },
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    DESCRIPTION = "Cut isometric diamond tiles from a seamless top-down texture."
    FUNCTION = FUNCTION
    OUTPUT_IS_LIST = (False, False, False, True)
    RETURN_NAMES = ("tiles", "atlas", "receipt", "tile_list")
    OUTPUT_TOOLTIPS = (
        "RGBA diamond tiles, one per variant, at the requested tile size.",
        "All variants side by side in one RGBA atlas row.",
        "Receipt with tile geometry, variant offsets and atlas size.",
        "The same tiles as an authoritative list.",
    )
    RETURN_TYPES = (Input.IMAGE, Input.IMAGE, Input.JSON, Input.IMAGE)

    def on_exec(
        self,
        image: torch.Tensor,
        tile_width: int,
        tile_height: int,
        variants: int,
        seed: int,
        texture_scale: float,
        **kwargs: Any,
    ) -> dict[str, Any]:
        tiles, atlas, receipt = render_iso_diamond_tiles(
            image,
            tile_width=normalize_list_to_value(tile_width),
            tile_height=normalize_list_to_value(tile_height),
            variants=normalize_list_to_value(variants),
            seed=normalize_list_to_value(seed),
            texture_scale=normalize_list_to_value(texture_scale),
        )
        nodes: list[dict[str, Any]] = []
        for index in range(min(int(tiles.shape[0]), 16)):
            preview = cache_generated_preview(tiles[index].unsqueeze(0))
            node = create_masonry_node(f"Tile {index}", preview.url, index)
            node["cells"]["lfImage"]["htmlProps"]["title"] = f"Tile {index}"
            nodes.append(node)
        payload = {"dataset": {"nodes": nodes}, "receipt": receipt}
        safe_send_sync("isodiamondtiles", payload, normalize_list_to_value(kwargs.get("node_id")))
        _, tile_list = normalize_output_image(tiles)
        return {"ui": {"lf_output": [payload]}, "result": (tiles, atlas, receipt, tile_list)}


NODE_CLASS_MAPPINGS = {
    "LF_IsoDiamondTiles": LF_IsoDiamondTiles,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_IsoDiamondTiles": "Iso diamond tiles",
}
