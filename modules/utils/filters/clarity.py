import cv2
import numpy as np
import torch

from ._common import validate_image, split_channels, merge_channels, apply_gaussian_blur
from ...utils.helpers import numpy_to_tensor, tensor_to_numpy

# region clarity_effect
def clarity_effect(image: torch.Tensor, clarity_strength: float, sharpen_amount: float, blur_kernel_size: int) -> torch.Tensor:
    """
    Processes a single image tensor by applying clarity and sharpen effects.

    Args:
        image (torch.Tensor): The input image tensor.
        clarity_strength (float): The clarity effect strength.
        sharpen_amount (float): The sharpening amount.
        blur_kernel_size (int): The kernel size for blurring.

    Returns:
        torch.Tensor: The processed image tensor.
    """
    validate_image(image, expected_shape=(3,))

    image_np = tensor_to_numpy(image, True)

    l_channel, a_channel, b_channel = split_channels(image_np, color_space="LAB")

    blurred_l_channel = apply_gaussian_blur(l_channel, blur_kernel_size, sigma=0)
    laplacian = cv2.Laplacian(blurred_l_channel, cv2.CV_64F)
    enhanced_l_channel = np.clip(l_channel + clarity_strength * laplacian, 0, 255).astype(np.uint8)

    final_image = merge_channels((enhanced_l_channel, a_channel, b_channel), color_space="LAB")

    gaussian_blur = apply_gaussian_blur(final_image, kernel_size=9, sigma=10.0)
    final_image = cv2.addWeighted(final_image, 1.0 + sharpen_amount, gaussian_blur, -sharpen_amount, 0)

    return numpy_to_tensor(final_image)
# endregion