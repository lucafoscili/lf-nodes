"""Where a change of light lands: the after/before luma ratio per pixel, and its median per band of before luma.

Both lumas are blurred at ``sigma`` pixels first, so texture and slight misregistration do not read as light. Pixels
whose blurred before luma is under ``floor`` are left out (their ratio is noise). With a mask, each band reports the
pixels outside and inside it separately. The picture is grey where nothing changed, orange where after is brighter and
blue where it is darker, full at ``stops`` stops; left-out pixels are black.
"""
from __future__ import annotations

import numpy as np
import torch

from .common import LUMA, gaussian

SCHEMA = 'lf.luma-ratio-map.v1'
DEFAULT_EDGES = (0.03, 0.06, 0.10, 0.15, 0.20, 0.30, 0.45, 0.65, 1.01)


def parse_edges(value) -> tuple[float, ...]:
    if isinstance(value, str):
        parts = [part.strip() for part in value.replace(';', ',').split(',') if part.strip()]
        try:
            value = [float(part) for part in parts]
        except ValueError as error:
            raise ValueError(f'band edges must be comma-separated numbers, not {value!r}.') from error
    edges = tuple(float(edge) for edge in value)
    if len(edges) < 2 or any(b <= a for a, b in zip(edges, edges[1:])):
        raise ValueError('band edges need at least two strictly increasing values.')
    return edges


def luma_ratio_map(before: np.ndarray, after: np.ndarray, *, mask: np.ndarray | None = None, sigma: float = 3.0,
                   floor: float = 0.03, edges=DEFAULT_EDGES, stops: float = 1.0, min_pixels: int = 200):
    """Return (report, picture) for two registered float32 [H,W,3] display images and an optional bool mask."""
    if before.shape != after.shape:
        raise ValueError(f'before {before.shape[1]}x{before.shape[0]} and after {after.shape[1]}x{after.shape[0]} '
                         'must be registered renders of the same size.')
    if mask is not None and mask.shape != before.shape[:2]:
        raise ValueError(f'mask {mask.shape[1]}x{mask.shape[0]} must match the images '
                         f'{before.shape[1]}x{before.shape[0]}.')
    if sigma < 0 or floor <= 0 or stops <= 0:
        raise ValueError('sigma must be non-negative, floor and stops positive.')
    edges = parse_edges(edges)
    before_luma = gaussian(before @ LUMA, sigma) if sigma > 0 else before @ LUMA
    after_luma = gaussian(after @ LUMA, sigma) if sigma > 0 else after @ LUMA
    kept = before_luma > floor
    ratio = np.where(kept, np.log2(np.maximum(after_luma, 1e-4) / np.maximum(before_luma, 1e-4)), 0)

    scaled = np.clip(ratio / stops, -1, 1)
    picture = np.full(before.shape, 0.5, dtype=np.float32)
    picture[..., 0] = np.clip(0.5 + 0.5 * scaled, 0, 1)
    picture[..., 1] = np.clip(0.5 + 0.15 * scaled, 0, 1)
    picture[..., 2] = np.clip(0.5 - 0.5 * scaled, 0, 1)
    picture[~kept] = 0

    inside = mask if mask is not None else np.zeros(kept.shape, bool)
    kept_count = max(int(kept.sum()), 1)

    def median(selected):
        return float(np.median(2 ** ratio[selected])) if selected.sum() > min_pixels else None

    bands = []
    for low, high in zip(edges, edges[1:]):
        band = kept & (before_luma >= low) & (before_luma < high)
        row = {'band': [low, high], 'share': float(band.sum() / kept_count), 'ratio': median(band & ~inside)}
        if mask is not None:
            row['ratio_inside'] = median(band & inside)
            row['ratio_frame'] = median(band)
        bands.append(row)
    with_data = [row for row in bands if row['ratio'] is not None]
    report = {
        'schema': SCHEMA,
        'size': [before.shape[1], before.shape[0]],
        'bands': bands,
        'darkest': with_data[0]['ratio'] if with_data else None,
        'brightest': with_data[-1]['ratio'] if with_data else None,
        'kept_share': float(kept.mean()),
        'parameters': {'sigma': sigma, 'floor': floor, 'edges': list(edges), 'stops': stops,
                       'min_pixels': min_pixels, 'masked': mask is not None},
        'method': ('Median of after/before luma per band of before luma, both blurred at sigma pixels; ratio is '
                   'outside the mask (the whole frame without one), ratio_inside within it and ratio_frame over '
                   'both; None under min_pixels.'),
    }
    return report, torch.from_numpy(picture)[None]
