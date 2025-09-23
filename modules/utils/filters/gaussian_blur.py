import torch

from ._common import apply_gaussian_blur, validate_image
from ...utils.helpers import numpy_to_tensor, tensor_to_numpy

# region gaussian_blur_effect
def gaussian_blur_effect(image: torch.Tensor, blur_kernel_size: int, blur_sigma: float) -> torch.Tensor:
    """
    Applies Gaussian Blur to an image tensor.

    Args:
        image (torch.Tensor): The input image tensor.
        blur_kernel_size (int): Kernel size for the Gaussian blur (must be odd).
        blur_sigma (float): Standard deviation of the Gaussian kernel.

    Returns:
        torch.Tensor: The blurred image tensor.
    """
    validate_image(image, expected_shape=(3,))

    image_np = tensor_to_numpy(image, True)

    blurred_image = apply_gaussian_blur(image_np, kernel_size=blur_kernel_size, sigma=blur_sigma)

    return numpy_to_tensor(blurred_image)
# endregion