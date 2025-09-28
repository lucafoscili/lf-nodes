from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from typing import Any, Dict, Tuple

import numpy as np
import torch
from PIL import Image
from rembg import remove

from ...utils.helpers.api import get_resource_url
from ...utils.helpers.comfy import resolve_filepath
from ...utils.helpers.conversion import (
    convert_to_boolean,
    hex_to_tuple,
    numpy_to_tensor,
    tensor_to_pil,
)
from ...utils.helpers.detection import get_rembg_session

FilterPayload = Dict[str, Any]
FilterResult = Tuple[torch.Tensor, FilterPayload]

@dataclass
class BackgroundRemovalResult:
    """
    Represents the result of a background removal operation.

    Attributes:
        composite (torch.Tensor): The image with the background removed and replaced, typically with transparency or a new background.
        cutout (torch.Tensor): The foreground object extracted from the original image.
        mask (torch.Tensor): The binary or alpha mask indicating the foreground region.
        stats (Dict[str, Any]): Additional statistics or metadata about the background removal process.
    """
    composite: torch.Tensor
    cutout: torch.Tensor
    mask: torch.Tensor
    stats: Dict[str, Any]

def normalize_hex_color(color: str | None) -> str:
    """
    Normalizes a hex color string to the standard 7-character format (#RRGGBB).

    Args:
        color (str | None): The input color string, which may be in shorthand (#RGB), missing the hash, or None.

    Returns:
        str: The normalized hex color string in uppercase (#RRGGBB). Returns "#000000" if the input is invalid.
    """
    color = (color or "#000000").strip()
    if not color.startswith("#"):
        color = f"#{color}"
    if len(color) == 4:  # #RGB
        color = "#" + "".join(ch * 2 for ch in color[1:])
    if len(color) != 7:
        return "#000000"
    return color.upper()

def _ensure_rgba_image(value: Image.Image | bytes) -> Image.Image:
    """
    Ensures that the input image is in RGBA mode.

    Args:
        value (Image.Image | bytes): The input image, either as a PIL Image object or as bytes.

    Returns:
        Image.Image: The image in RGBA mode.

    Raises:
        UnidentifiedImageError: If the input bytes cannot be opened as an image.
    """
    image: Image.Image
    if isinstance(value, Image.Image):
        image = value
    else:
        image = Image.open(BytesIO(value))
    if image.mode != "RGBA":
        image = image.convert("RGBA")
    return image

def _compute_stats(alpha: np.ndarray, width: int, height: int) -> Dict[str, Any]:
    """
    Computes statistics about the foreground and background regions in an alpha mask.

    Args:
        alpha (np.ndarray): A 2D numpy array representing the alpha mask, where values > 0.01 are considered foreground.
        width (int): The width of the image.
        height (int): The height of the image.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - "width": The width of the image.
            - "height": The height of the image.
            - "foreground_pixels": Number of pixels classified as foreground.
            - "background_pixels": Number of pixels classified as background.
            - "foreground_ratio": Ratio of foreground coverage (mean of alpha values).
            - "bounding_box" (optional): [x_min, y_min, x_max, y_max] coordinates of the foreground bounding box, if any foreground pixels are present.
    """
    foreground_mask = alpha > 0.01
    foreground_pixels = int(foreground_mask.sum())
    total_pixels = int(alpha.size)
    background_pixels = total_pixels - foreground_pixels
    coverage = float(alpha.mean())

    stats: Dict[str, Any] = {
        "width": width,
        "height": height,
        "foreground_pixels": foreground_pixels,
        "background_pixels": background_pixels,
        "foreground_ratio": coverage,
    }

    if foreground_pixels:
        ys, xs = np.nonzero(foreground_mask)
        bbox = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]
        stats["bounding_box"] = bbox

    return stats

def apply_background_removal(
    image: torch.Tensor,
    *,
    transparent_background: bool,
    background_color: str,
    model_name: str,
) -> BackgroundRemovalResult:
    """
    Removes the background from an input image tensor using a specified model, and returns the processed results.

    Args:
        image (torch.Tensor): The input image tensor to process.
        transparent_background (bool): If True, the output image will have a transparent background; 
            otherwise, the background will be filled with the specified color.
        background_color (str): The hex color code (e.g., "#FFFFFF") to use for the background if transparency is not desired.
        model_name (str): The name of the background removal model to use.

    Returns:
        BackgroundRemovalResult: An object containing:
            - composite (torch.Tensor): The final image tensor with the background removed or replaced.
            - cutout (torch.Tensor): The cutout image tensor with alpha channel.
            - mask (torch.Tensor): The alpha mask tensor indicating foreground regions.
            - stats (dict): Statistics and metadata about the background removal process.
    """
    pil_image = tensor_to_pil(image)
    session = get_rembg_session(model_name)

    removed = remove(pil_image, session=session)
    cutout_image = _ensure_rgba_image(removed)

    alpha = np.array(cutout_image.getchannel("A"), dtype=np.float32) / 255.0
    mask_tensor = torch.from_numpy(alpha).unsqueeze(0)

    if transparent_background:
        composite_image = cutout_image
    else:
        rgb = hex_to_tuple(background_color)
        background = Image.new("RGBA", cutout_image.size, rgb + (255,))
        composite_image = Image.alpha_composite(background, cutout_image).convert("RGB")

    composite_tensor = numpy_to_tensor(np.array(composite_image))
    cutout_tensor = numpy_to_tensor(np.array(cutout_image))
    stats = _compute_stats(alpha, cutout_image.width, cutout_image.height)
    stats.update(
        {
            "model": model_name,
            "transparent_background": transparent_background,
            "background_color": background_color,
        }
    )

    return BackgroundRemovalResult(
        composite=composite_tensor,
        cutout=cutout_tensor,
        mask=mask_tensor,
        stats=stats,
    )

def apply_background_remover_filter(image: torch.Tensor, settings: dict) -> FilterResult:
    """
    Applies a background removal filter to the given image tensor using specified settings.

    Args:
        image (torch.Tensor): The input image tensor to process.
        settings (dict): Dictionary containing filter settings. Supported keys:
            - "transparent_background" (bool or str, optional): Whether to make the background transparent. Defaults to True.
            - "color" (str, optional): Hex color code for the background if not transparent. Defaults to "#000000".
            - "model" (str, optional): Name of the background removal model to use. Defaults to "u2net".

    Returns:
        Tuple[torch.Tensor, dict]: 
            - The composite image tensor with background removed or replaced.
            - A payload dictionary containing:
                - "mask": URL to the saved mask image.
                - "cutout": URL to the saved cutout image.
                - "stats": Statistics from the background removal process.
    """
    transparent_raw = settings.get("transparent_background", True)
    transparent = convert_to_boolean(transparent_raw)
    if transparent is None:
        transparent = True

    color = normalize_hex_color(settings.get("color") or "#000000")
    model_name = str(settings.get("model") or "u2net")

    result = apply_background_removal(
        image,
        transparent_background=transparent,
        background_color=color,
        model_name=model_name,
    )

    cutout_image = tensor_to_pil(result.cutout)
    cutout_path, cutout_subfolder, cutout_filename = resolve_filepath(
        filename_prefix="background_cutout",
    )
    cutout_image.save(cutout_path, format="PNG")
    cutout_url = get_resource_url(cutout_subfolder, cutout_filename, "temp")

    mask_np = (result.mask.squeeze(0).cpu().numpy() * 255).astype(np.uint8)
    mask_image = Image.fromarray(mask_np, mode="L")
    mask_path, mask_subfolder, mask_filename = resolve_filepath(
        filename_prefix="background_mask",
    )
    mask_image.save(mask_path, format="PNG")
    mask_url = get_resource_url(mask_subfolder, mask_filename, "temp")

    payload: FilterPayload = {
        "mask": mask_url,
        "cutout": cutout_url,
        "stats": result.stats,
    }

    return result.composite, payload