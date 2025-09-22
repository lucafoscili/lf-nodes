import torch

from ._common import validate_image

# region desaturate_effect
def desaturate_effect(image: torch.Tensor, global_level: float, channel_levels: list[float]) -> torch.Tensor:
    """
    Applies partial desaturation per channel to the input image tensor.

    Args:
        image (torch.Tensor): Input image tensor with shape (B, H, W, C).
        global_level (float): Global desaturation level (0.0 to 1.0).
        channel_levels (list[float]): List of desaturation levels for [R, G, B].

    Returns:
        torch.Tensor: Partially desaturated image tensor.
    """
    validate_image(image, expected_shape=(3,))

    r, g, b = image[..., 0], image[..., 1], image[..., 2]
    gray_image = 0.299 * r + 0.587 * g + 0.114 * b

    desaturated_r = (1 - (global_level * channel_levels[0])) * r + (global_level * channel_levels[0]) * gray_image
    desaturated_g = (1 - (global_level * channel_levels[1])) * g + (global_level * channel_levels[1]) * gray_image
    desaturated_b = (1 - (global_level * channel_levels[2])) * b + (global_level * channel_levels[2]) * gray_image

    return torch.stack([desaturated_r, desaturated_g, desaturated_b], dim=-1)
# endregion