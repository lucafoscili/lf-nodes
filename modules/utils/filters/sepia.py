import numpy as np
import torch

from ._common import validate_image
from ...utils.helpers import numpy_to_tensor, tensor_to_numpy

# region sepia_effect
def sepia_effect(image: torch.Tensor, intensity = 1.0):
    """
    Applies a sepia tone filter to the given image.

    Args:
        image: The input image. [1, H, W, C]
        intensity: A float between 0 and 1 for sepia intensity.

    Returns:
        The sepia-toned image. [1, H, W, C]
    """
    validate_image(image, expected_shape=(3,))

    np_image = tensor_to_numpy(image)

    sepia_filter = np.array([
        [0.393 + 0.607 * (1 - intensity), 0.769 - 0.769 * (1 - intensity), 0.189 - 0.189 * (1 - intensity)],
        [0.349 - 0.349 * (1 - intensity), 0.686 + 0.314 * (1 - intensity), 0.168 - 0.168 * (1 - intensity)],
        [0.272 - 0.272 * (1 - intensity), 0.534 - 0.534 * (1 - intensity), 0.131 + 0.869 * (1 - intensity)],
    ])

    sepia_image = np_image @ sepia_filter.T
    sepia_image = np.clip(sepia_image, 0, 255)

    return numpy_to_tensor(sepia_image.astype(np.uint8))
# endregion