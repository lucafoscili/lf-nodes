"""Shared conversions for the tone readers: tensors to float32 arrays, luma, saturation and signed pictures."""
from __future__ import annotations

import numpy as np
import torch

LUMA = np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)


def as_rgb(image, name: str) -> np.ndarray:
    """One IMAGE item ([1,H,W,C] or [H,W,C]) as a float32 [H,W,3] array; refuses non-finite values."""
    if torch.is_tensor(image):
        if image.ndim == 4:
            if image.shape[0] != 1:
                raise ValueError(f'{name} requires exactly one image, not a batch of {image.shape[0]}.')
            image = image[0]
        if image.ndim != 3 or image.shape[-1] not in (3, 4):
            raise ValueError(f'{name} must be an RGB or RGBA image.')
        array = image[..., :3].detach().to(device='cpu', dtype=torch.float32).numpy()
    else:
        array = np.asarray(image, dtype=np.float32)[..., :3]
    if not np.isfinite(array).all():
        raise ValueError(f'{name} holds non-finite pixels.')
    return np.ascontiguousarray(array)


def one_image(value, name: str) -> torch.Tensor:
    """Exactly one IMAGE item from a tensor, batch or list; values may lie outside 0..1 (linear layers)."""
    from ..logic import normalize_input_image

    images = normalize_input_image(value)
    if len(images) != 1:
        raise ValueError(f'{name} requires exactly one image, not {len(images)}.')
    return images[0]


def luma(rgb: np.ndarray) -> np.ndarray:
    """Rec. 709 luma of display values."""
    return 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]


def saturation(rgb: np.ndarray, floor: float = 1e-3) -> np.ndarray:
    """HSV saturation, (max - min) / max, zero where the pixel is black."""
    high, low = rgb.max(-1), rgb.min(-1)
    return np.where(high > floor, (high - low) / np.maximum(high, floor), 0)


def gaussian(values: np.ndarray, sigma: float) -> np.ndarray:
    from scipy.ndimage import gaussian_filter

    return gaussian_filter(values, sigma=sigma)


def signed_picture(values: np.ndarray, gain: float) -> torch.Tensor:
    """A signed map as an IMAGE: grey is zero, red is positive, blue is negative, full at 1 / gain."""
    picture = np.empty(values.shape + (3,), dtype=np.float32)
    picture[..., 0] = np.clip(0.5 + gain * values, 0, 1)
    picture[..., 1] = 0.5
    picture[..., 2] = np.clip(0.5 - gain * values, 0, 1)
    return torch.from_numpy(picture)[None]


def binary_masks(masks) -> np.ndarray:
    """MASK [R,H,W] or [H,W] as a boolean array (threshold 0.5)."""
    if torch.is_tensor(masks):
        masks = masks.detach().to(device='cpu', dtype=torch.float32).numpy()
    masks = np.asarray(masks)
    return masks > 0.5
