import cv2
import numpy as np
import torch

from ._common import detect_edges, validate_image
from ...utils.helpers import tensor_to_numpy

# region contrast_effect
def contrast_effect(image: torch.Tensor, contrast_strength: float, midpoint: float, localized_contrast: bool) -> torch.Tensor:
    """
    Adjusts the contrast of the input image tensor.

    Args:
        image (torch.Tensor): Input image tensor with shape [1, H, W, C].
        contrast_strength (float): Contrast adjustment factor (-1 to 1).
        midpoint (float): Tonal midpoint for contrast scaling.
        localized_contrast (bool): Whether to enhance contrast locally around edges.

    Returns:
        torch.Tensor: Contrast-adjusted image tensor with shape [1, H, W, C].
    """
    validate_image(image, expected_shape=(3,))

    image_np = tensor_to_numpy(image, True) / 255.0

    scale_factor = 1 + contrast_strength
    adjusted_image = midpoint + scale_factor * (image_np - midpoint)

    adjusted_image = np.clip(adjusted_image, 0, 1)

    if localized_contrast:
        gray = cv2.cvtColor((image_np * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
        edges = detect_edges(gray, method='sobel')

        edges_3ch = np.repeat(edges[:, :, np.newaxis], 3, axis=2) / 255.0
        edge_contrast_factor = abs(contrast_strength) * 0.1

        adjusted_image += edges_3ch * edge_contrast_factor
        adjusted_image = np.clip(adjusted_image, 0, 1)

    final_tensor = torch.tensor(adjusted_image, dtype=image.dtype, device=image.device)
    return final_tensor
# endregion