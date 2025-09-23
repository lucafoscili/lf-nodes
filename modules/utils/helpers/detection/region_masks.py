import math
import torch

from typing import Any, Dict, Tuple

from ...filters import apply_gaussian_blur


def _gaussian_blur_2d(tensor: torch.Tensor, kernel_size: Tuple[int, int], sigma: float) -> torch.Tensor:
    if sigma <= 0:
        return tensor
    _, kw = kernel_size
    array = tensor.squeeze(0).squeeze(0).detach().cpu().numpy().astype("float32")
    blurred = apply_gaussian_blur(array, max(1, kw), sigma)
    result = torch.from_numpy(blurred).to(tensor.device, tensor.dtype)
    return result.unsqueeze(0).unsqueeze(0)


def _ensure_bbox(region: Dict[str, Any], image_height: int, image_width: int) -> Tuple[float, float, float, float]:
    bbox = region.get("bbox_float") or region.get("bbox")
    if bbox is None or len(bbox) != 4:
        raise ValueError("Region metadata missing bbox information")
    x1, y1, x2, y2 = [float(v) for v in bbox]
    if region.get("bbox") is not None:
        # incoming bbox assumed inclusive pixel indices; treat as floats but clamp within image
        pass
    if x1 > x2:
        x1, x2 = x2, x1
    if y1 > y2:
        y1, y2 = y2, y1
    return (
        max(0.0, min(x1, image_width - 1.0)),
        max(0.0, min(y1, image_height - 1.0)),
        max(0.0, min(x2, image_width - 1.0)),
        max(0.0, min(y2, image_height - 1.0)),
    )


# region build_region_mask
def build_region_mask(
    image: torch.Tensor,
    region: Dict[str, Any],
    *,
    padding: float = 0.0,
    padding_px: float = 0.0,
    feather: float = 0.0,
    shape: str = "rectangle",
    invert: bool = False,
) -> torch.Tensor:
    """Create a float mask [1, H, W, 1] for the provided region metadata."""
    if image.dim() != 4:
        raise ValueError("image tensor must be [B,H,W,C]")
    device = image.device
    dtype = torch.float32
    _, H, W, _ = image.shape
    x1, y1, x2, y2 = _ensure_bbox(region, H, W)
    # ensure coordinates inclusive/exclusive ordering
    if x2 <= x1 or y2 <= y1:
        return torch.zeros((1, H, W, 1), device=device, dtype=dtype)

    width = x2 - x1
    height = y2 - y1
    padding = max(0.0, float(padding))
    padding_px = max(0.0, float(padding_px))
    pad_w = padding * width + padding_px
    pad_h = padding * height + padding_px

    x1 = max(0.0, x1 - pad_w)
    x2 = min(float(W), x2 + pad_w)
    y1 = max(0.0, y1 - pad_h)
    y2 = min(float(H), y2 + pad_h)

    if x2 <= x1 or y2 <= y1:
        return torch.zeros((1, H, W, 1), device=device, dtype=dtype)

    mask = torch.zeros((H, W), device=device, dtype=dtype)
    if shape == "ellipse":
        yy = torch.arange(H, device=device, dtype=dtype).unsqueeze(1)
        xx = torch.arange(W, device=device, dtype=dtype).unsqueeze(0)
        cx = (x1 + x2) * 0.5
        cy = (y1 + y2) * 0.5
        rx = max((x2 - x1) * 0.5, 1.0)
        ry = max((y2 - y1) * 0.5, 1.0)
        mask_inner = (((xx + 0.5 - cx) / rx) ** 2 + ((yy + 0.5 - cy) / ry) ** 2) <= 1.0
        mask = mask_inner.to(dtype)
    else:
        xi1 = int(math.floor(x1))
        yi1 = int(math.floor(y1))
        xi2 = int(math.ceil(x2))
        yi2 = int(math.ceil(y2))
        xi1 = max(0, min(xi1, W))
        yi1 = max(0, min(yi1, H))
        xi2 = max(0, min(xi2, W))
        yi2 = max(0, min(yi2, H))
        if xi2 > xi1 and yi2 > yi1:
            mask[yi1:yi2, xi1:xi2] = 1.0

    feather = max(0.0, float(feather))
    if feather > 0.0:
        sigma = feather * max(width, height, 1.0)
        if sigma > 0.0:
            kernel = max(3, int(math.ceil(sigma * 6.0)))
            if kernel % 2 == 0:
                kernel += 1
            mask = mask.unsqueeze(0).unsqueeze(0)
            mask = _gaussian_blur_2d(mask, (kernel, kernel), sigma)
            mask = mask.squeeze(0).squeeze(0)
            max_val = mask.max()
            if max_val > 0:
                mask = mask / max_val
    if invert:
        mask = 1.0 - mask
    mask = mask.clamp(0.0, 1.0)

    return mask.unsqueeze(0).unsqueeze(-1)
# endregion
