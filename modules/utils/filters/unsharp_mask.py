import numpy as np
import torch

from ._common import apply_gaussian_blur, validate_image
from ...utils.helpers import numpy_to_tensor, tensor_to_numpy

# region unsharp_mask_effect
def unsharp_mask_effect(
    image: torch.Tensor,
    amount: float,
    radius: int,
    sigma: float,
    threshold: float,
) -> torch.Tensor:
    """
    Apply an unsharp mask to the provided image tensor.

    Args:
        image (torch.Tensor): Input image tensor with shape [1, H, W, 3].
        amount (float): Strength of the sharpening effect.
        radius (int): Kernel radius for the Gaussian blur (will be converted to an odd value).
        sigma (float): Standard deviation for the Gaussian blur.
        threshold (float): Minimum edge magnitude (0-1 range) required before sharpening is applied.

    Returns:
        torch.Tensor: The sharpened image tensor in the range [0, 1].
    """
    validate_image(image, expected_shape=(3,))

    radius = max(int(radius), 1)
    if radius % 2 == 0:
        radius += 1

    sigma = float(max(sigma, 0.0))
    amount = float(max(amount, 0.0))
    threshold = float(max(threshold, 0.0))

    image_np = tensor_to_numpy(image, threeD=True)
    image_float = image_np.astype(np.float32)

    blurred = apply_gaussian_blur(image_float, kernel_size=radius, sigma=sigma)

    high_freq = image_float - blurred

    if threshold > 0.0:
        threshold_value = threshold * 255.0
        magnitude = np.max(np.abs(high_freq), axis=2, keepdims=True)
        mask = magnitude >= threshold_value
        high_freq = high_freq * mask

    sharpened = image_float + (amount * high_freq)
    sharpened = np.clip(sharpened, 0.0, 255.0).astype(np.uint8)

    return numpy_to_tensor(sharpened)
# endregion
