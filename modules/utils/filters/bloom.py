import cv2
import numpy as np
import torch

from ._common import validate_image
from ...utils.helpers import hex_to_tuple, numpy_to_tensor, tensor_to_numpy

# region bloom_effect
def bloom_effect(image: torch.Tensor, threshold: float, radius: int, intensity: float, tint: str = "FFFFFF") -> torch.Tensor:
    """
    Applies a bloom effect to an input image tensor.
    The bloom effect enhances bright areas of the image by blurring and blending highlights, 
    optionally tinting them with a specified color.

    Args:
        image (torch.Tensor): Input image tensor of shape (3, H, W) or (H, W, 3), with pixel values in [0, 255].
        threshold (float): Luminance threshold above which pixels are considered highlights (range: 0.0–1.0).
        radius (int): Radius of the Gaussian blur applied to highlights (should be a positive integer).
        intensity (float): Strength of the bloom effect (higher values produce a stronger effect).
        tint (str, optional): Hex color code (e.g., "FFFFFF" for white) used to tint the bloom highlights. Defaults to "FFFFFF".

    Returns:
        torch.Tensor: Image tensor with the bloom effect applied, in the same format as the input.
    """
    validate_image(image, expected_shape=(3,))

    np_img = tensor_to_numpy(image, True) / 255.0

    luminance = np.max(np_img, axis=-1, keepdims=True)
    mask = (luminance > threshold).astype(np.float32)

    tint = tint.lstrip("#").upper()
    colour = np_img if tint.upper() == "FFFFFF" else \
             np.tile(np.array(hex_to_tuple(tint)) / 255.0, (*mask.shape[:2], 1))
    highlights = mask * colour

    k = radius | 1
    blurred = cv2.GaussianBlur(highlights, (k, k), k * 0.4)

    out = np.clip(np_img + blurred * intensity, 0, 1) * 255
    return numpy_to_tensor(out.astype(np.uint8))
# endregion