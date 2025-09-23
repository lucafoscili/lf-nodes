import torch

from ._common import validate_image
from ...utils.helpers import hex_to_tuple

# region split_tone_effect
def split_tone_effect(image: torch.Tensor, shadows_tint: str, highlights_tint: str, balance: float, softness: float, intensity: float) -> torch.Tensor:
    """
    Applies a split-tone effect to a batch of images.

    Args:
        image (torch.Tensor): Input tensor of shape [B, H, W, C] with C=3 and values in [0, 255].
        shadows_tint (str): Hex color for shadows (e.g. "#FF0000").
        highlights_tint (str): Hex color for highlights.
        balance (float): Pivot luminance (0.0-1.0).
        softness (float): Width of transition band around balance.
        intensity (float): Strength of the tint (0.0-1.0).

    Returns:
        torch.Tensor: Tensor of same shape and dtype uint8 with effect applied.
    """
    def _hex_to_tensor(hex_color: str) -> torch.Tensor:
        rgb = hex_to_tuple(hex_color)
        t = torch.tensor(rgb, device=img.device, dtype=torch.float32) / 255.0
        return t.view(1,1,1,3)
    
    validate_image(image, expected_shape=(3,))

    orig_dtype = image.dtype
    if torch.is_floating_point(image):
        img = image.clamp(0.0, 1.0)
    else:
        img = image.float() / 255.0


    st = _hex_to_tensor(shadows_tint)
    ht = _hex_to_tensor(highlights_tint)

    lum = img.max(dim=-1, keepdim=True)[0]
    mask = ((lum - balance) / softness).clamp(0.0, 1.0)

    shadows = img * (1 - mask) + st * mask
    highlights = img * (1 - mask) + ht * mask
    blended = (shadows + highlights - img).clamp(0.0, 1.0)
    out = (img + blended * intensity).clamp(0.0, 1.0)

    if orig_dtype == torch.uint8:
        return (out * 255.0).round().clamp(0, 255).to(torch.uint8)
    return out
# endregion