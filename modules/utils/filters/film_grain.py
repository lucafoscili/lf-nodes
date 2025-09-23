import cv2
import numpy as np
import torch

from ._common import validate_image
from ...utils.helpers import hex_to_tuple, numpy_to_tensor, tensor_to_numpy

# region film_grain_effect
def film_grain_effect(image: torch.Tensor, intensity: float = 0.5, size: float = 1.0, tint: str = "FFFFFF", soft_blend = False) -> torch.Tensor:
    """
    Adds a refined film grain effect to the given image with tint and soft blend options.

    Args:
        image: The input image. [1, H, W, C]
        intensity: A float between 0 and 1 controlling the grain's opacity.
        size: A float controlling the granularity of the grain (higher = coarser).
        tint: Hexadecimal color (default is FFFFFF for no tint).
        soft_blend: If True, uses a soft blending mode for the grain.

    Returns:
        The image with film grain applied. [1, H, W, C]
    """
    validate_image(image, expected_shape=(3,))

    np_image = tensor_to_numpy(image)
    height, width, channels = np_image.shape

    grain_height = max(1, int(height / size))
    grain_width = max(1, int(width / size))
    noise = np.random.normal(0, 1, (grain_height, grain_width, 1))

    noise = cv2.resize(noise, (width, height), interpolation=cv2.INTER_LINEAR)
    noise = np.expand_dims(noise, axis=-1)
    noise = np.repeat(noise, channels, axis=-1)

    noise = (noise - np.mean(noise)) / (np.std(noise) + 1e-8)
    noise = noise * 255 * intensity

    tint = tint.lstrip("#").upper()
    if tint != "FFFFFF":
        tuple_tint = hex_to_tuple(tint)
        tint_array = np.array(tuple_tint).reshape(1, 1, 3)
        noise = noise * 0.5 + tint_array * 0.5

    if soft_blend:
        grainy_image = 1 - (1 - np_image / 255) * (1 - noise / 255)
        grainy_image = grainy_image * 255
    else:
        grainy_image = np_image + noise

    grainy_image = np.clip(grainy_image, 0, 255)

    return numpy_to_tensor(grainy_image.astype(np.uint8))
# endregion