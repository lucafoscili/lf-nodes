import cv2
import numpy as np
import torch

from ._common import validate_image
from ...utils.helpers import numpy_to_tensor, tensor_to_numpy

# region tilt_shift_effect
def tilt_shift_effect(img: torch.Tensor, focus_position: float, focus_size: float, blur_radius: int, feather: str = "smooth", orient: str = "horizontal") -> torch.Tensor:
    """
    Applies a tilt-shift effect to an input image tensor, simulating a shallow depth-of-field by blending a focused region with a blurred background.

    Args:
        img (torch.Tensor): Input image tensor of shape [B, H, W, C] with values in [0, 255].
        focus_position (float): Position of the focus region, normalized between 0 (top/left) and 1 (bottom/right).
        focus_size (float): Size of the focus region as a fraction of the image dimension (0 to 1).
        blur_radius (int): Radius of the Gaussian blur applied to out-of-focus areas.
        feather (str, optional): Feathering curve for the transition between focused and blurred regions.
            Options are "smooth" (default, smoothstep curve) or "expo" (exponential curve).
        orient (str, optional): Orientation of the focus region. Options are "horizontal" (default), "vertical", or "circular".

    Returns:
        torch.Tensor: Image tensor with the tilt-shift effect applied, of shape [B, H, W, C] and dtype uint8.
    """    
    validate_image(img, expected_shape=(3,))
    _, h, w, _ = img.shape

    yy, xx = np.meshgrid(np.linspace(0, 1, h), np.linspace(0, 1, w), indexing="ij")
    if orient == "horizontal":
        dist = np.abs(yy - focus_position)
    elif orient == "vertical":
        dist = np.abs(xx - focus_position)
    else:
        dist = np.sqrt((yy - focus_position) ** 2 + (xx - 0.5) ** 2)

    half = focus_size / 2.0
    mask = np.clip((half - dist) / half, 0, 1)

    if feather == "smooth":
        mask = mask * mask * (3 - 2 * mask)
    elif feather == "expo":
        mask = mask ** 2

    mask = np.expand_dims(mask, 0)

    k = blur_radius | 1
    np_img = tensor_to_numpy(img, True)
    blurred = cv2.GaussianBlur(np_img, (k, k), k * 0.35)

    mask_expanded = np.transpose(mask, (1, 2, 0)) if mask.shape[0] == 1 else mask
    if mask_expanded.shape[-1] != np_img.shape[-1]:
        mask_expanded = np.repeat(mask_expanded, np_img.shape[-1], axis=-1)

    out = np_img * mask_expanded + blurred * (1 - mask_expanded)
    
    return numpy_to_tensor(out.astype(np.uint8))
# endregion