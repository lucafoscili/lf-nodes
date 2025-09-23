import cv2
import numpy as np
import torch

from ._common import validate_image
from ...utils.helpers import numpy_to_tensor, tensor_to_numpy

# region vibrance_effect
def vibrance_effect(img: torch.Tensor, intensity: float, protect_skin: bool, clip_soft: bool):
    """
    Applies a vibrance effect to an image tensor, enhancing color intensity while optionally protecting skin tones and applying soft clipping.

    Args:
        img (torch.Tensor): Input image tensor with shape (3, H, W) in BGR format and values in [0, 1].
        intensity (float): Strength of the vibrance effect. Higher values increase color intensity.
        protect_skin (bool): If True, reduces the effect on skin-tone hues to avoid unnatural skin colors.
        clip_soft (bool): If True, applies a soft clipping to the saturation channel to prevent harsh saturation.
        
    Returns:
        torch.Tensor: The image tensor after applying the vibrance effect, with the same shape and type as the input.
    """
    validate_image(img, expected_shape=(3,))

    hsv = cv2.cvtColor(tensor_to_numpy(img, True), cv2.COLOR_BGR2HSV).astype(np.float32) / 255.0

    h, s, v = cv2.split(hsv)
    delta = intensity * (1.0 - s)
    if protect_skin:
        skin = ((h*360 >= 15) & (h*360 <= 50)).astype(np.float32)
        delta *= (1.0 - 0.7*skin)
    s = s + delta
    if clip_soft:
        s = np.clip(s, 0, 1)
        s = s - (s**4)*(s-1)
    hsv_boost = cv2.merge([h, s, v]) * 255
    out = cv2.cvtColor(hsv_boost.astype(np.uint8), cv2.COLOR_HSV2BGR)
    
    return numpy_to_tensor(out)
# endregion