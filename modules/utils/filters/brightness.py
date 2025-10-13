import cv2
import numpy as np
import torch

from ._common import validate_image
from ...utils.helpers import tensor_to_numpy

# region brightness_effect
def brightness_effect(image: torch.Tensor, brightness_strength: float, gamma: float, midpoint: float, localized_brightness: bool) -> torch.Tensor:
    """
    Adjusts the brightness of the input image tensor with gamma correction and optional localized enhancement.

    Args:
        image (torch.Tensor): Input image tensor with shape [1, H, W, C].
        brightness_strength (float): Brightness adjustment factor (-1 to 1).
        gamma (float): Gamma correction factor.
        midpoint (float): Tonal midpoint for brightness scaling.
        localized_brightness (bool): Whether to enhance brightness locally in darker regions.

    Returns:
        torch.Tensor: Adjusted image tensor with shape [1, H, W, C].
    """
    validate_image(image, expected_shape=(3,))

    image_np = tensor_to_numpy(image, True).astype(np.float32) / 255.0

    adjusted_image = midpoint + (image_np - midpoint) + brightness_strength
    adjusted_image = np.clip(adjusted_image, 0.0, 1.0)

    adjusted_image = np.power(adjusted_image, gamma)

    if localized_brightness:
        gray = cv2.cvtColor((image_np * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
        darkness_map = 1 - (gray / 255.0)
        adjusted_image += darkness_map[:, :, np.newaxis] * 0.1
        adjusted_image = np.clip(adjusted_image, 0, 1)

    adjusted_image = np.clip(adjusted_image, 0, 1)

    final_tensor = torch.tensor(adjusted_image, dtype=image.dtype, device=image.device)

    return final_tensor
# endregion
