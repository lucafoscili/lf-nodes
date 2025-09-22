import cv2
import numpy as np
import torch

from ._common import validate_image
from ...utils.helpers import numpy_to_tensor, tensor_to_numpy

# region saturation_effect
def saturation_effect(
    image: torch.Tensor,
    intensity: float
) -> torch.Tensor:
    """
    Applies a saturation adjustment effect to an image tensor.

    Args:
        image (torch.Tensor): Input image tensor with shape [B, H, W, C] in BGR format.
        intensity (float): Saturation scaling factor. Values >1 increase saturation, values <1 decrease it.

    Returns:
        torch.Tensor: The image tensor with adjusted saturation, in the same format as the input.
    """    
    validate_image(image, expected_shape=(3,))

    # Convert tensor to numpy array
    np_img = tensor_to_numpy(image, True).astype(np.float32) / 255.0

    # Convert RGB to HSV
    hsv = cv2.cvtColor(np_img, cv2.COLOR_RGB2HSV)
    hsv[..., 1] = np.clip(hsv[..., 1] * intensity, 0, 1)
    adjusted = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
    adjusted = np.clip(adjusted * 255, 0, 255).astype(np.uint8)

    return numpy_to_tensor(adjusted)
# endregion