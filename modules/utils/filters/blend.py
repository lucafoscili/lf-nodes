import torch

from ._common import blend_overlay

# region blend_effect
def blend_effect(image: torch.Tensor, overlay_image: torch.Tensor, alpha_mask: float, mode: str = "normal") -> torch.Tensor:
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

    # Ensure inputs are floats in [0,1]
    img = image.float()
    over = overlay_image.float()

    # Resize overlay if needed (existing behavior)
    if img.shape != over.shape:
        _, base_h, base_w, _ = img.shape

        over = torch.nn.functional.interpolate(
            over.permute(0, 3, 1, 2),
            size=(base_h, base_w),
            mode='bilinear',
            align_corners=False
        ).permute(0, 2, 3, 1)

    def clamp01(x: torch.Tensor) -> torch.Tensor:
        return torch.clamp(x, 0.0, 1.0)

    # Extract alpha if overlay has an alpha channel
    if over.shape[-1] > img.shape[-1]:
        overlay_alpha = over[..., 3:4]
        over_rgb = over[..., :3]
        combined_alpha = alpha_tensor * overlay_alpha
    else:
        over_rgb = over
        combined_alpha = alpha_tensor

    a = combined_alpha
    A = a

    # Per-mode blending (operate on RGB channels)
    base = img[..., :3]
    top = over_rgb[..., :3]

    if mode == "normal":
        blended_rgb = top
    elif mode == "multiply":
        blended_rgb = base * top
    elif mode == "screen":
        blended_rgb = 1 - (1 - base) * (1 - top)
    elif mode == "overlay":
        blended_rgb = torch.where(base <= 0.5, 2 * base * top, 1 - 2 * (1 - base) * (1 - top))
    elif mode == "soft_light":
        # soft light approximation
        blended_rgb = torch.where(
            top <= 0.5,
            base - (1 - 2 * top) * base * (1 - base),
            base + (2 * top - 1) * (torch.sqrt(base.clamp(min=1e-6)) - base),
        )
    elif mode == "hard_light":
        blended_rgb = torch.where(top <= 0.5, 2 * base * top, 1 - 2 * (1 - base) * (1 - top))
    elif mode == "difference":
        blended_rgb = torch.abs(base - top)
    elif mode == "addition":
        blended_rgb = base + top
    elif mode == "subtract":
        blended_rgb = base - top
    else:
        # Unknown mode -> fallback to normal
        blended_rgb = top

    # Composite with alpha: out = base * (1 - A) + blended * A
    out_rgb = base * (1 - A) + blended_rgb * A

    out_rgb = clamp01(out_rgb)

    # If input had extra channels, preserve them (e.g., alpha). Otherwise, reconstruct 3-channel image.
    result = out_rgb

    # Ensure same batch/channel layout as input
    return result
# endregion