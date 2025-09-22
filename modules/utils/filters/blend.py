import torch

from ._common import blend_overlay

# region blend_effect
def blend_effect(image: torch.Tensor, overlay_image: torch.Tensor, alpha_mask: float) -> torch.Tensor:
    """
    Apply alpha blending between a base image and an overlay one.

    Args:
        image (torch.Tensor): Base image tensor. Shape: [1, H, W, C].
        overlay_image (torch.Tensor): Overlay image tensor to blend. Shape: [1, H, W, C].
        alpha_mask (float): Opacity for blending (0.0 to 1.0).

    Returns:
        torch.Tensor: Blended image tensor.
    """
    if image.shape != overlay_image.shape:
        _, base_h, base_w, _ = image.shape

        overlay_image: torch.Tensor = torch.nn.functional.interpolate(
            overlay_image.permute(0, 3, 1, 2),
            size=(base_h, base_w),
            mode='bilinear',
            align_corners=False
        ).permute(0, 2, 3, 1)

    alpha_tensor: torch.Tensor = torch.full_like(image[..., 0], alpha_mask).unsqueeze(-1)

    return blend_overlay(image, overlay_image, alpha_tensor)
# endregion