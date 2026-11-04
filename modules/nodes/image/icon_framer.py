"""Frame a cut-out subject as a square game-style icon.

The node takes an image and the mask of its subject (for example Background
Remover's mask), fits the subject's bounding box into a square at a chosen
fill, composites it over a flat or source backdrop with an optional glow and
outline, darkens the corners, draws a bevelled rim and writes the result at a
master size and at a small display size.
"""

from __future__ import annotations

import math
import re
from typing import Dict, List

import torch
import torch.nn.functional as F

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import (
    normalize_input_image,
    normalize_list_to_value,
    normalize_masks_for_images,
    normalize_output_image,
)
from ...utils.helpers.ui import create_cached_compare_node

BACKDROPS = ("color", "source")
_HEX = re.compile(r"^#?[0-9a-fA-F]{6}$")


def _color(value: str, name: str) -> torch.Tensor:
    text = str(value).strip()
    if not _HEX.match(text):
        raise ValueError(f"{name} must be a hexadecimal colour in the format #RRGGBB, got {value!r}.")
    text = text.lstrip("#")
    return torch.tensor([int(text[i : i + 2], 16) / 255.0 for i in (0, 2, 4)], dtype=torch.float32)


def _fraction(value: float, name: str, minimum: float, maximum: float) -> float:
    number = float(value)
    if not math.isfinite(number) or number < minimum or number > maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}, got {value!r}.")
    return number


def _resize(image: torch.Tensor, size: int) -> torch.Tensor:
    """Resize ``[H, W, C]`` to a ``size`` square with antialiasing."""

    chw = image.permute(2, 0, 1).unsqueeze(0)
    out = F.interpolate(chw, size=(size, size), mode="bilinear", align_corners=False, antialias=True)
    return out.squeeze(0).permute(1, 2, 0).clamp(0.0, 1.0)


def _blur(mask: torch.Tensor, radius: float) -> torch.Tensor:
    """Gaussian-blur a ``[H, W]`` map by ``radius`` pixels (sigma = radius / 2)."""

    if radius < 0.5:
        return mask
    sigma = radius / 2.0
    half = max(1, int(math.ceil(sigma * 3)))
    xs = torch.arange(-half, half + 1, dtype=torch.float32)
    kernel = torch.exp(-(xs**2) / (2 * sigma**2))
    kernel = kernel / kernel.sum()
    value = mask.unsqueeze(0).unsqueeze(0)
    value = F.pad(value, (half, half, half, half), mode="replicate")
    value = F.conv2d(value, kernel.view(1, 1, 1, -1))
    value = F.conv2d(value, kernel.view(1, 1, -1, 1))
    return value.squeeze(0).squeeze(0)


def _dilate(mask: torch.Tensor, radius: int) -> torch.Tensor:
    if radius < 1:
        return mask
    value = mask.unsqueeze(0).unsqueeze(0)
    value = F.max_pool2d(value, kernel_size=2 * radius + 1, stride=1, padding=radius)
    return value.squeeze(0).squeeze(0)


def _square_crop(image: torch.Tensor, mask: torch.Tensor, threshold: float, fill: float):
    """Crop ``image`` and ``mask`` to a square around the subject, padding outside the source."""

    height, width = int(mask.shape[0]), int(mask.shape[1])
    ys, xs = torch.nonzero(mask > threshold, as_tuple=True)
    if ys.numel() == 0:
        raise ValueError(
            f"The mask holds no subject above the threshold {threshold}: nothing to frame."
        )
    top, bottom = int(ys.min()), int(ys.max()) + 1
    left, right = int(xs.min()), int(xs.max()) + 1
    side = max(bottom - top, right - left) / fill
    side = max(1, int(round(side)))
    cy, cx = (top + bottom) / 2.0, (left + right) / 2.0
    y0, x0 = int(round(cy - side / 2.0)), int(round(cx - side / 2.0))

    channels = int(image.shape[-1])
    crop = torch.zeros(side, side, channels, dtype=image.dtype)
    crop_mask = torch.zeros(side, side, dtype=mask.dtype)
    sy0, sx0 = max(0, y0), max(0, x0)
    sy1, sx1 = min(height, y0 + side), min(width, x0 + side)
    crop[sy0 - y0 : sy1 - y0, sx0 - x0 : sx1 - x0] = image[sy0:sy1, sx0:sx1]
    crop_mask[sy0 - y0 : sy1 - y0, sx0 - x0 : sx1 - x0] = mask[sy0:sy1, sx0:sx1]
    inside = torch.zeros(side, side, dtype=mask.dtype)
    inside[sy0 - y0 : sy1 - y0, sx0 - x0 : sx1 - x0] = 1.0
    return crop, crop_mask, inside


def _rim(size: int, width: int, base: torch.Tensor, light: float) -> tuple[torch.Tensor, torch.Tensor]:
    """A bevelled square rim: colour ``[S, S, 3]`` and coverage ``[S, S]``.

    The band is lit from the top left: its top and left sides are lighter than its
    bottom and right ones, with a dark line on its outer and inner edge.
    """

    coords = torch.arange(size, dtype=torch.float32) + 0.5
    y = coords.view(-1, 1).expand(size, size)
    x = coords.view(1, -1).expand(size, size)
    distance = torch.minimum(torch.minimum(x, y), torch.minimum(size - x, size - y))
    coverage = (width - distance + 0.5).clamp(0.0, 1.0)
    # Which side owns each rim pixel: top/left are lit, bottom/right shaded.
    lit = ((x + y) < size).float()
    shade = 1.0 + light * (2.0 * lit - 1.0)
    # Across the band, brighter in its middle, a dark line at both edges.
    across = (distance / max(width, 1)).clamp(0.0, 1.0)
    profile = 0.55 + 0.45 * torch.sin(across * math.pi)
    edge = max(1.0, width * 0.12)
    dark_line = ((distance < edge) | ((width - distance) < edge)).float()
    colour = base.view(1, 1, 3) * (shade * profile).unsqueeze(-1)
    colour = colour * (1.0 - 0.75 * dark_line).unsqueeze(-1)
    return colour.clamp(0.0, 1.0), coverage


def frame_icon(
    image: torch.Tensor,
    mask: torch.Tensor,
    *,
    master_size: int = 512,
    icon_size: int = 64,
    fill: float = 0.86,
    threshold: float = 0.5,
    backdrop: str = "color",
    backdrop_color: str = "#000000",
    glow_color: str = "#000000",
    glow_strength: float = 0.0,
    outline: float = 0.012,
    outline_color: str = "#000000",
    vignette: float = 0.35,
    bevel: float = 0.05,
    bevel_color: str = "#8a8a8a",
    bevel_light: float = 0.35,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Frame one ``[1, H, W, C]`` image with its ``[1, H, W]`` mask; returns (master, icon) as ``[1, S, S, 3]``."""

    if image.dim() != 4 or image.shape[0] != 1:
        raise ValueError("frame_icon takes one image shaped [1, H, W, C].")
    if mask.dim() != 3 or mask.shape[0] != 1:
        raise ValueError("frame_icon takes one mask shaped [1, H, W].")
    if tuple(mask.shape[1:]) != tuple(image.shape[1:3]):
        raise ValueError(
            f"The mask is {tuple(mask.shape[1:])} but the image is {tuple(image.shape[1:3])}: they must match."
        )
    if backdrop not in BACKDROPS:
        raise ValueError(f"backdrop must be one of {', '.join(BACKDROPS)}, got {backdrop!r}.")
    if not 16 <= int(master_size) <= 4096:
        raise ValueError(f"master_size must be between 16 and 4096, got {master_size!r}.")
    if not 8 <= int(icon_size) <= int(master_size):
        raise ValueError(f"icon_size must be between 8 and master_size ({master_size}), got {icon_size!r}.")
    fill = _fraction(fill, "fill", 0.1, 1.0)
    threshold = _fraction(threshold, "threshold", 0.0, 0.99)
    glow_strength = _fraction(glow_strength, "glow_strength", 0.0, 1.0)
    outline = _fraction(outline, "outline", 0.0, 0.1)
    vignette = _fraction(vignette, "vignette", 0.0, 1.0)
    bevel = _fraction(bevel, "bevel", 0.0, 0.2)
    bevel_light = _fraction(bevel_light, "bevel_light", 0.0, 1.0)
    backdrop_rgb = _color(backdrop_color, "backdrop_color")
    glow_rgb = _color(glow_color, "glow_color")
    outline_rgb = _color(outline_color, "outline_color")
    bevel_rgb = _color(bevel_color, "bevel_color")

    size = int(master_size)
    source = image[0, ..., :3].detach().float().cpu()
    subject = mask[0].detach().float().cpu().clamp(0.0, 1.0)

    # The subject fills ``fill`` of the area inside the rim.
    inner_fill = fill * (1.0 - 2.0 * bevel)
    crop, crop_mask, inside = _square_crop(source, subject, threshold, inner_fill)
    crop = _resize(crop, size)
    crop_mask = _resize(crop_mask.unsqueeze(-1), size)[..., 0]
    inside = _resize(inside.unsqueeze(-1), size)[..., 0]

    if backdrop == "source":
        canvas = crop * inside.unsqueeze(-1) + backdrop_rgb.view(1, 1, 3) * (1.0 - inside).unsqueeze(-1)
    else:
        canvas = backdrop_rgb.view(1, 1, 3).expand(size, size, 3).clone()

    if glow_strength > 0.0:
        glow = _blur(_dilate(crop_mask, max(1, int(size * 0.02))), size * 0.08) * glow_strength
        canvas = 1.0 - (1.0 - canvas) * (1.0 - glow.unsqueeze(-1) * glow_rgb.view(1, 1, 3))

    if outline > 0.0:
        radius = max(1, int(round(size * outline)))
        ring = _blur(_dilate(crop_mask, radius), radius * 0.5).clamp(0.0, 1.0)
        canvas = canvas * (1.0 - ring.unsqueeze(-1)) + outline_rgb.view(1, 1, 3) * ring.unsqueeze(-1)

    alpha = crop_mask.unsqueeze(-1)
    canvas = canvas * (1.0 - alpha) + crop * alpha

    if vignette > 0.0:
        coords = (torch.arange(size, dtype=torch.float32) + 0.5) / size * 2.0 - 1.0
        radius = torch.sqrt(coords.view(-1, 1) ** 2 + coords.view(1, -1) ** 2) / math.sqrt(2.0)
        falloff = ((radius - 0.45) / 0.55).clamp(0.0, 1.0) ** 2
        canvas = canvas * (1.0 - vignette * falloff).unsqueeze(-1)

    if bevel > 0.0:
        rim_colour, coverage = _rim(size, max(1, int(round(size * bevel))), bevel_rgb, bevel_light)
        canvas = canvas * (1.0 - coverage.unsqueeze(-1)) + rim_colour * coverage.unsqueeze(-1)

    master = canvas.clamp(0.0, 1.0)
    icon = _resize(master, int(icon_size))
    return master.unsqueeze(0), icon.unsqueeze(0)


# region LF_IconFramer
class LF_IconFramer:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (Input.IMAGE, {"tooltip": "Image (or list of images) holding the subject."}),
                "mask": (Input.MASK, {"tooltip": "Subject mask, one per image or one shared; 1 marks the subject."}),
                "master_size": (Input.INTEGER, {"default": 512, "min": 16, "max": 4096,
                    "tooltip": "Edge of the large square output, in pixels."}),
                "icon_size": (Input.INTEGER, {"default": 64, "min": 8, "max": 4096,
                    "tooltip": "Edge of the small square output, downscaled from the large one."}),
                "fill": (Input.FLOAT, {"default": 0.86, "min": 0.1, "max": 1.0, "step": 0.01,
                    "tooltip": "Share of the area inside the rim that the subject's longer side fills."}),
                "backdrop": (BACKDROPS, {"default": "color",
                    "tooltip": "color: a flat backdrop colour; source: the image's own surroundings."}),
                "backdrop_color": (Input.STRING, {"default": "#000000",
                    "tooltip": "Backdrop colour, and the fill outside the source image (#RRGGBB)."}),
                "glow_color": (Input.STRING, {"default": "#000000", "tooltip": "Colour of the glow behind the subject (#RRGGBB)."}),
                "glow_strength": (Input.FLOAT, {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.05,
                    "tooltip": "Glow behind the subject; 0 turns it off."}),
                "outline": (Input.FLOAT, {"default": 0.012, "min": 0.0, "max": 0.1, "step": 0.001,
                    "tooltip": "Width of the dark outline around the subject, as a share of the edge; 0 turns it off."}),
                "outline_color": (Input.STRING, {"default": "#000000", "tooltip": "Outline colour (#RRGGBB)."}),
                "vignette": (Input.FLOAT, {"default": 0.35, "min": 0.0, "max": 1.0, "step": 0.05,
                    "tooltip": "How much the corners darken; 0 turns it off."}),
                "bevel": (Input.FLOAT, {"default": 0.05, "min": 0.0, "max": 0.2, "step": 0.005,
                    "tooltip": "Width of the bevelled rim, as a share of the edge; 0 draws no rim."}),
                "bevel_color": (Input.STRING, {"default": "#8a8a8a", "tooltip": "Base colour of the rim (#RRGGBB)."}),
                "bevel_light": (Input.FLOAT, {"default": 0.35, "min": 0.0, "max": 1.0, "step": 0.05,
                    "tooltip": "Contrast between the rim's lit top-left and shaded bottom-right sides."}),
                "threshold": (Input.FLOAT, {"default": 0.5, "min": 0.0, "max": 0.99, "step": 0.01,
                    "tooltip": "Mask value above which a pixel counts towards the subject's bounding box."}),
            },
            "optional": {
                "ui_widget": (Input.LF_COMPARE, {"default": {}}),
            },
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    INPUT_IS_LIST = True
    OUTPUT_IS_LIST = (False, True, False, True)
    OUTPUT_TOOLTIPS = (
        "Framed icons at master size, as a batch.",
        "Framed icons at master size, one per input image.",
        "Framed icons at icon size, as a batch.",
        "Framed icons at icon size, one per input image.",
    )
    RETURN_NAMES = ("master", "master_list", "icon", "icon_list")
    RETURN_TYPES = (Input.IMAGE, Input.IMAGE, Input.IMAGE, Input.IMAGE)

    def on_exec(self, **kwargs: dict):
        images = normalize_input_image(kwargs.get("image"))
        if not images:
            raise ValueError("Icon Framer needs at least one image.")
        masks = normalize_masks_for_images(kwargs.get("mask"), len(images))
        if len(masks) == 1 and len(images) > 1:
            masks = masks * len(images)

        settings = {
            name: normalize_list_to_value(kwargs.get(name))
            for name in (
                "master_size", "icon_size", "fill", "backdrop", "backdrop_color", "glow_color",
                "glow_strength", "outline", "outline_color", "vignette", "bevel", "bevel_color",
                "bevel_light", "threshold",
            )
        }
        settings = {name: value for name, value in settings.items() if value is not None}

        masters: List[torch.Tensor] = []
        icons: List[torch.Tensor] = []
        nodes: List[dict] = []
        for index, (image, mask) in enumerate(zip(images, masks)):
            master, icon = frame_icon(image, mask, **settings)
            masters.append(master)
            icons.append(icon)
            nodes.append(create_cached_compare_node(image[..., :3], master, index=index))

        payload: Dict[str, object] = {"dataset": {"nodes": nodes}}
        safe_send_sync("iconframer", payload, normalize_list_to_value(kwargs.get("node_id")))

        master_batches, master_list = normalize_output_image(masters)
        icon_batches, icon_list = normalize_output_image(icons)
        return {
            "ui": {"lf_output": [payload]},
            "result": (master_batches[0], master_list, icon_batches[0], icon_list),
        }
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_IconFramer": LF_IconFramer,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_IconFramer": "Icon Framer",
}
# endregion
