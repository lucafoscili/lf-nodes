from __future__ import annotations

import torch

from typing import Any, Callable, Dict, Tuple

from ..helpers.conversion import (
    base64_to_tensor,
    convert_to_boolean,
    convert_to_float,
    convert_to_int,
)
from .background_remover import background_remover_effect
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
from .unsharp_mask import unsharp_mask_effect
from .saturation import saturation_effect
from .sepia import sepia_effect
from .split_tone import split_tone_effect
from .tilt_shift import tilt_shift_effect
from .vibrance import vibrance_effect
from .vignette import vignette_effect
from ..helpers.torch import create_colored_tensor

FilterPayload = Dict[str, Any]
FilterResult = Tuple[torch.Tensor, FilterPayload]
FilterProcessor = Callable[[torch.Tensor, dict], FilterResult]

class UnknownFilterError(ValueError):
    """
    Exception raised when attempting to use a filter type that has not been registered.

    Attributes:
        message (str): Explanation of the error.
    """

def _as_result(image: torch.Tensor) -> FilterResult:
    """
    Converts a torch.Tensor image into a FilterResult tuple.

    Args:
        image (torch.Tensor): The image tensor to be wrapped.

    Returns:
        FilterResult: A tuple containing the image tensor and an empty dictionary.
    """
    return image, {}


# region Background Remover
def apply_background_remover_filter(image: torch.Tensor, settings: dict) -> FilterResult:
    """
    Applies a background remover filter to the given image tensor using specified settings.
    
    Args:
        image (torch.Tensor): The input image tensor to process.
        settings (dict): A dictionary of settings for the background remover filter. Supported keys:
            - "transparent_background" (bool or str, optional): Whether to make the background transparent. Defaults to True.
            - "color" (str, optional): Hex code for the background color if not transparent. Defaults to "#000000".
            - "model" (str, optional): The model name to use for background removal. Defaults to "u2net".

    Returns:
        Tuple[FilterResult, dict]: A tuple containing the processed image result and a payload dictionary with additional information.
    """

    transparent_raw = settings.get("transparent_background", True)
    transparent = convert_to_boolean(transparent_raw)
    if transparent is None:
        transparent = True

    color = str(settings.get("color") or "#000000")
    model_name = str(settings.get("model") or "u2net")

    composite, extra_payload = background_remover_effect(
        image,
        transparent_background=transparent,
        background_color=color,
        model_name=model_name,
    )

    image_result, payload = _as_result(composite)
    payload.update(extra_payload)
    return image_result, payload
# endregion

# region Blend
def apply_blend_filter(image: torch.Tensor, settings: dict) -> FilterResult:
    """
    Applies a blend filter to the given image tensor using specified settings.

    The function overlays a colored tensor onto the input image with a specified opacity.

    Args:
        image (torch.Tensor): The input image tensor to apply the blend filter to.
        settings (dict): A dictionary containing filter settings:
            - "opacity" (float, optional): The opacity level of the blend effect. Defaults to 1.0.
            - "color" (str, optional): The hex color code (e.g., "FF0000") for the overlay. Defaults to "FF0000".

    Returns:
        FilterResult: The result of applying the blend effect to the image.
    """
    opacity = convert_to_float(settings.get("opacity", 1.0))
    color: str = settings.get("color", "FF0000")
    overlay_image = create_colored_tensor(image, color)
    return _as_result(blend_effect(image, overlay_image, opacity))
# endregion

# region Bloom
def apply_bloom_filter(image: torch.Tensor, settings: dict) -> FilterResult:
    """
    Applies a bloom filter effect to the given image tensor using specified settings.

    Args:
        image (torch.Tensor): The input image tensor to process.
        settings (dict): A dictionary containing bloom filter parameters:
            - "intensity" (float, optional): Strength of the bloom effect. Defaults to 0.0.
            - "radius" (int, optional): Radius of the bloom effect. Defaults to 0.
            - "threshold" (float, optional): Threshold for bloom activation. Defaults to 0.0.
            - "tint" (str, optional): Hex color string for bloom tint. Defaults to "FFFFFF".

    Returns:
        FilterResult: The result of applying the bloom effect to the image.
    """
    intensity = convert_to_float(settings.get("intensity", 0.0))
    radius = convert_to_int(settings.get("radius", 0))
    threshold = convert_to_float(settings.get("threshold", 0.0))
    tint = settings.get("tint", "FFFFFF")
    return _as_result(bloom_effect(image, threshold, radius, intensity, tint))
# endregion

# region Brightness
def apply_brightness_filter(image: torch.Tensor, settings: dict) -> FilterResult:
    """
    Applies a brightness filter to the given image tensor using specified settings.

    Parameters:
        image (torch.Tensor): The input image tensor to process.
        settings (dict): A dictionary containing filter parameters:
            - "strength" (float, optional): The strength of the brightness effect. Defaults to 0.0.
            - "gamma" (float, optional): The gamma correction value. Defaults to 0.0.
            - "midpoint" (float, optional): The midpoint value for brightness adjustment. Defaults to 0.0.
            - "localized" (bool, optional): Whether to apply the effect locally. Defaults to False.

    Returns:
        FilterResult: The result of applying the brightness filter to the image.
    """
    strength = convert_to_float(settings.get("strength", 0.0))
    gamma = convert_to_float(settings.get("gamma", 0.0))
    midpoint = convert_to_float(settings.get("midpoint", 0.0))
    localized = convert_to_boolean(settings.get("localized", False))
    return _as_result(brightness_effect(image, strength, gamma, midpoint, localized))
# endregion

# region Brush
def apply_brush_filter(image: torch.Tensor, settings: dict) -> FilterResult:
    """
    Applies a brush filter to the given image using a canvas provided in the settings.

    Args:
        image (torch.Tensor): The input image tensor to which the brush filter will be applied.
        settings (dict): A dictionary containing filter settings. Must include a "b64_canvas" key with a base64-encoded canvas.

    Returns:
        FilterResult: The result of blending the brush effect onto the image.
    """
    canvas_b64: str = settings.get("b64_canvas", "")
    canvas = base64_to_tensor(canvas_b64, True)
    return _as_result(blend_effect(image, canvas, 1.0))
# endregion

# region Clarity
def apply_clarity_filter(image: torch.Tensor, settings: dict) -> FilterResult:
    """
    Applies a clarity filter to the given image tensor using specified settings.

    This function enhances the clarity of the input image by adjusting its sharpness and blur based on the provided settings.

    Args:
        image (torch.Tensor): The input image tensor to be processed.
        settings (dict): A dictionary containing filter parameters:
            - "clarity_strength" (float, optional): Strength of the clarity effect. Defaults to 0.0.
            - "sharpen_amount" (float, optional): Amount of sharpening to apply. Defaults to 0.0.
            - "blur_kernel_size" (int, optional): Size of the blur kernel. Defaults to 1.

    Returns:
        FilterResult: The result of applying the clarity filter to the image.
    """
    clarity_strength = convert_to_float(settings.get("clarity_strength", 0.0))
    sharpen_amount = convert_to_float(settings.get("sharpen_amount", 0.0))
    blur_kernel_size = convert_to_int(settings.get("blur_kernel_size", 1))
    return _as_result(clarity_effect(image, clarity_strength, sharpen_amount, blur_kernel_size))
# endregion

# region Contrast
def apply_contrast_filter(image: torch.Tensor, settings: dict) -> FilterResult:
    """
    Applies a contrast filter to the given image tensor using specified settings.

    Args:
        image (torch.Tensor): The input image tensor to process.
        settings (dict): A dictionary containing filter parameters:
            - "strength" (float, optional): The strength of the contrast effect. Defaults to 0.0.
            - "midpoint" (float, optional): The midpoint value for contrast adjustment. Defaults to 0.0.
            - "localized" (bool, optional): Whether to apply localized contrast. Defaults to False.

    Returns:
        FilterResult: The result of applying the contrast filter to the image.
    """
    strength = convert_to_float(settings.get("strength", 0.0))
    midpoint = convert_to_float(settings.get("midpoint", 0.0))
    localized = convert_to_boolean(settings.get("localized", False))
    return _as_result(contrast_effect(image, strength, midpoint, localized))
# endregion

# region Desaturate
def apply_desaturate_filter(image: torch.Tensor, settings: dict) -> FilterResult:
    """
    Applies a desaturation filter to the given image tensor using specified settings.

    Args:
        image (torch.Tensor): The input image tensor to be processed.
        settings (dict): A dictionary containing filter parameters:
            - "strength" (float, optional): The intensity of the desaturation effect. Defaults to 0.0.
            - "r_channel" (float, optional): Weight for the red channel. Defaults to 1.0.
            - "g_channel" (float, optional): Weight for the green channel. Defaults to 1.0.
            - "b_channel" (float, optional): Weight for the blue channel. Defaults to 1.0.

    Returns:
        FilterResult: The result of applying the desaturation effect to the image.
    """
    strength = convert_to_float(settings.get("strength", 0.0))
    r = convert_to_float(settings.get("r_channel", 1.0))
    g = convert_to_float(settings.get("g_channel", 1.0))
    b = convert_to_float(settings.get("b_channel", 1.0))
    return _as_result(desaturate_effect(image, strength, [r, g, b]))
# endregion

# region Film Grain
def apply_film_grain_filter(image: torch.Tensor, settings: dict) -> FilterResult:
    """
    Applies a film grain filter to the given image tensor using specified settings.

    Args:
        image (torch.Tensor): The input image tensor to process.
        settings (dict): A dictionary containing filter parameters:
            - "intensity" (float, optional): The strength of the grain effect. Defaults to 0.0.
            - "size" (float, optional): The size of the grain particles. Defaults to 1.0.
            - "tint" (str, optional): Hex color code for grain tint. Defaults to "FFFFFF".
            - "soft_blend" (bool, optional): Whether to use soft blending for the effect. Defaults to False.

    Returns:
        FilterResult: The result of applying the film grain effect to the image.
    """
    intensity = convert_to_float(settings.get("intensity", 0.0))
    size = convert_to_float(settings.get("size", 1.0))
    tint = settings.get("tint", "FFFFFF")
    soft_blend = convert_to_boolean(settings.get("soft_blend", False))
    return _as_result(film_grain_effect(image, intensity, size, tint, soft_blend))
# endregion

# region Gaussian Blur
def apply_gaussian_blur_filter(image: torch.Tensor, settings: dict) -> FilterResult:
    """
    Applies a Gaussian blur filter to the given image tensor using specified settings.

    Args:
        image (torch.Tensor): The input image tensor to be blurred.
        settings (dict): A dictionary containing filter parameters:
            - "blur_sigma" (float, optional): The standard deviation for the Gaussian kernel. Defaults to 0.0 if not provided.
            - "blur_kernel_size" (int, optional): The size of the Gaussian kernel. Defaults to 1 if not provided.

    Returns:
        FilterResult: The result of applying the Gaussian blur effect to the image.
    """
    sigma = convert_to_float(settings.get("blur_sigma", 0.0))
    kernel_size = convert_to_int(settings.get("blur_kernel_size", 1))
    return _as_result(gaussian_blur_effect(image, kernel_size, sigma))
# endregion

# region Line
def apply_line_filter(image: torch.Tensor, settings: dict) -> FilterResult:
    """
    Applies a line filter effect to the given image tensor based on the provided settings.

    Args:
        image (torch.Tensor): The input image tensor to process.
        settings (dict): A dictionary containing filter settings:
            - "points" (list of dict): List of points with "x" and "y" coordinates for the line.
            - "size" (int or str): Thickness of the line.
            - "color" (str): Hex color code for the line (default: "FF0000").
            - "opacity" (float or str): Opacity of the line (default: 1.0).
            - "smoooth" (bool or str): Whether to apply smoothing to the line (default: False).

    Returns:
        FilterResult: The result of applying the line filter effect to the image.
    """
    points_setting = settings.get("points", []) or []
    points = [(point["x"], point["y"]) for point in points_setting]
    size = convert_to_int(settings.get("size", 0))
    color = settings.get("color", "FF0000")
    opacity = convert_to_float(settings.get("opacity", 1.0))
    smooth = convert_to_boolean(settings.get("smoooth", False))
    return _as_result(line_effect(image, points, size, color, opacity, smooth))
# endregion

# region Saturation
def apply_saturation_filter(image: torch.Tensor, settings: dict) -> FilterResult:
    """
    Applies a saturation filter to the given image tensor using the specified settings.

    Args:
        image (torch.Tensor): The input image tensor to be processed.
        settings (dict): A dictionary containing filter settings. Expected key:
            - "intensity" (float, optional): The intensity of the saturation effect. Defaults to 1.0.

    Returns:
        FilterResult: The result of applying the saturation effect to the image.
    """
    intensity = convert_to_float(settings.get("intensity", 1.0))
    return _as_result(saturation_effect(image, intensity))
# endregion

# region Sepia
def apply_sepia_filter(image: torch.Tensor, settings: dict) -> FilterResult:
    """
    Applies a sepia filter to the given image tensor.

    Args:
        image (torch.Tensor): The input image tensor to be processed.
        settings (dict): A dictionary containing filter settings. Expected key:
            - "intensity" (float, optional): The intensity of the sepia effect. Defaults to 0.0 if not provided.

    Returns:
        FilterResult: The result of applying the sepia filter to the image.
    """
    intensity = convert_to_float(settings.get("intensity", 0.0))
    return _as_result(sepia_effect(image, intensity))
# endregion

# region Split Tone
def apply_split_tone_filter(image: torch.Tensor, settings: dict) -> FilterResult:
    """
    Applies a split tone filter to the given image tensor using specified settings.

    This filter tints the highlights and shadows of the image with user-defined colors,
    allowing for creative color grading effects. The balance, softness, and intensity
    parameters control the blending and strength of the effect.

    Args:
        image (torch.Tensor): The input image tensor to process.
        settings (dict): A dictionary containing filter parameters:
            - "highlights" (str): Hex color code for highlights (default: "FFAA55").
            - "shadows" (str): Hex color code for shadows (default: "0066FF").
            - "balance" (float or str): Balance between highlights and shadows (default: 0.0).
            - "softness" (float or str): Softness of the transition (default: 0.0).
            - "intensity" (float or str): Intensity of the effect (default: 0.0).

    Returns:
        FilterResult: The result of applying the split tone effect to the image.
    """
    highlights = settings.get("highlights", "FFAA55")
    shadows = settings.get("shadows", "0066FF")
    balance = convert_to_float(settings.get("balance", 0.0))
    softness = convert_to_float(settings.get("softness", 0.0))
    intensity = convert_to_float(settings.get("intensity", 0.0))
    return _as_result(split_tone_effect(image, shadows, highlights, balance, softness, intensity))
# endregion

# region Tilt-Shift
def apply_tilt_shift_filter(image: torch.Tensor, settings: dict) -> FilterResult:
    """
    Applies a tilt-shift filter effect to the given image tensor using specified settings.

    Args:
        image (torch.Tensor): The input image tensor to process.
        settings (dict): A dictionary containing filter parameters:
            - "focus_position" (float, optional): Position of the focus area (default: 0.5).
            - "focus_size" (float, optional): Size of the focus area (default: 0.25).
            - "radius" (int, optional): Blur radius for the out-of-focus regions (default: 25).
            - "feather" (str, optional): Feathering method for the transition (default: "smooth").
            - "orientation" (str, optional): Orientation of the tilt-shift effect, "horizontal" or "vertical" (default: "horizontal").

    Returns:
        FilterResult: The result of applying the tilt-shift effect to the image.
    """
    focus_position = convert_to_float(settings.get("focus_position", 0.5))
    focus_size = convert_to_float(settings.get("focus_size", 0.25))
    blur_radius = convert_to_int(settings.get("radius", 25))
    feather = settings.get("feather", "smooth")
    orientation = settings.get("orientation", "horizontal")
    return _as_result(tilt_shift_effect(image, focus_position, focus_size, blur_radius, feather, orientation))
# endregion

# region Vibrance
def apply_vibrance_filter(image: torch.Tensor, settings: dict) -> FilterResult:
    """
    Applies a vibrance filter to the given image tensor using specified settings.

    This function enhances the vibrance of the image, optionally protecting skin tones and applying soft clipping.

    Args:
        image (torch.Tensor): The input image tensor to process.
        settings (dict): Dictionary of filter settings. Supported keys:
            - "intensity" (float, optional): Strength of the vibrance effect. Defaults to 0.0.
            - "protect_skin" (bool, optional): Whether to protect skin tones from vibrance adjustment. Defaults to False.
            - "clip_soft" (bool, optional): Whether to apply soft clipping to the output. Defaults to False.

    Returns:
        FilterResult: The result of applying the vibrance filter to the image.
    """
    intensity = convert_to_float(settings.get("intensity", 0.0))
    protect_skin = convert_to_boolean(settings.get("protect_skin", False))
    clip_soft = convert_to_boolean(settings.get("clip_soft", False))
    return _as_result(vibrance_effect(image, intensity, protect_skin, clip_soft))
# endregion

# region Vignette
def apply_vignette_filter(image: torch.Tensor, settings: dict) -> FilterResult:
    """
    Applies a vignette filter to the given image tensor using specified settings.

    Args:
        image (torch.Tensor): The input image tensor to apply the vignette effect on.
        settings (dict): A dictionary containing vignette filter parameters:
            - "intensity" (float, optional): Strength of the vignette effect. Defaults to 0.0.
            - "radius" (float, optional): Radius of the vignette effect. Defaults to 0.0.
            - "shape" (str, optional): Shape of the vignette ("elliptical" by default).
            - "color" (str, optional): Hex color code for the vignette effect. Defaults to "000000".

    Returns:
        FilterResult: The result of applying the vignette effect to the image.
    """
    intensity = convert_to_float(settings.get("intensity", 0.0))
    radius = convert_to_float(settings.get("radius", 0.0))
    shape = settings.get("shape", "elliptical")
    color = settings.get("color", "000000")
    return _as_result(vignette_effect(image, intensity, radius, shape, color))
# endregion

# region Unsharp Mask
def apply_unsharp_mask_filter(image: torch.Tensor, settings: dict) -> FilterResult:
    """
    Applies an unsharp mask filter to the given image tensor using specified settings.

    The unsharp mask filter enhances the edges in the image by subtracting a blurred version of the image from the original, 
    then scaling and adding it back. This is commonly used to increase perceived sharpness.

    Args:
        image (torch.Tensor): The input image tensor to be processed.
        settings (dict): A dictionary containing filter parameters:
            - "amount" (float, optional): The strength of the sharpening effect. Default is 0.0.
            - "radius" (int, optional): The radius of the Gaussian blur. Default is 1.
            - "sigma" (float, optional): The standard deviation for Gaussian blur. Default is 1.0.
            - "threshold" (float, optional): Minimum brightness change to sharpen. Default is 0.0.

    Returns:
        FilterResult: The result of applying the unsharp mask filter to the image.
    """
    amount = convert_to_float(settings.get("amount", 0.0))
    radius = convert_to_int(settings.get("radius", 1))
    sigma = convert_to_float(settings.get("sigma", 1.0))
    threshold = convert_to_float(settings.get("threshold", 0.0))
    return _as_result(unsharp_mask_effect(image, amount, radius, sigma, threshold))
# endregion

FILTER_PROCESSORS: Dict[str, FilterProcessor] = {
    "background_remover": apply_background_remover_filter,
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
    "unsharp_mask": apply_unsharp_mask_filter,
    "vibrance": apply_vibrance_filter,
    "vignette": apply_vignette_filter,
}

# region Process
def process_filter(filter_type: str, image: torch.Tensor, settings: dict) -> FilterResult:
    """
    Processes an image using the specified filter type and settings.

    Args:
        filter_type (str): The type of filter to apply.
        image (torch.Tensor): The image tensor to process.
        settings (dict): A dictionary of settings specific to the filter.

    Returns:
        FilterResult: The result of the filter processing.

    Raises:
        UnknownFilterError: If the specified filter type is not supported.
    """
    try:
        processor = FILTER_PROCESSORS[filter_type]
    except KeyError as exc:
        raise UnknownFilterError(f"Unsupported filter type: {filter_type}") from exc
    return processor(image, settings)
# endregion