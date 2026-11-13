"""Split the change between two registered renders of one scene into a colour grade, a local tone operator and
what is left, the part only the scene's geometry, light and materials can explain.

* The grade is one colour lookup for the whole frame (a ``lut_size``^3 table, what a LUT or a tonemapper change can
  do): each output pixel is the mean ``after`` colour of the ``before`` pixels in its cell.
* The local operator keys that lookup by the neighbourhood's brightness too (a ``local_size``^3 colour table times
  ``local_size`` bins of the luma blurred at ``local_sigma`` times the width): shade fill, local contrast, a bloom.
* Each share is ``1 - residual energy / change energy`` over all pixels and channels. The lookups are fitted and
  scored on the same pixels, so they are upper bounds of what such an operator could explain.
* What is left after the local operator, and the raw change, are split into spatial bands of their luma: fine (below
  ``fine_sigma`` pixels), mid (up to ``coarse_sigma``) and coarse (above), as shares of their energy.
* The grade itself reads as a tone curve (mean ``after`` luma per tenth of ``before`` luma) and the saturation of the
  dark, mid and bright bands of ``before`` luma.
"""
from __future__ import annotations

import numpy as np

from .common import gaussian, luma, saturation, signed_picture

SCHEMA = 'lf.grade-split.v1'
SATURATION_BANDS = (('dark', 0.0, 0.2), ('mid', 0.2, 0.5), ('bright', 0.5, None))


def _table_fit(keys: np.ndarray, target: np.ndarray, bins: tuple[int, ...]) -> np.ndarray:
    """Mean of ``target`` per cell of ``keys`` (an N x k integer array), applied back as a lookup."""
    flat = np.ravel_multi_index(keys.T, bins)
    cells = int(np.prod(bins))
    count = np.bincount(flat, minlength=cells)
    out = np.empty_like(target)
    for channel in range(target.shape[1]):
        total = np.bincount(flat, weights=target[:, channel], minlength=cells)
        out[:, channel] = (total / np.maximum(count, 1))[flat]
    return out


def _bands(values: np.ndarray, fine_sigma: float, coarse_sigma: float) -> dict:
    fine_blur, coarse_blur = gaussian(values, fine_sigma), gaussian(values, coarse_sigma)
    energy = [float((band ** 2).sum()) for band in (values - fine_blur, fine_blur - coarse_blur, coarse_blur)]
    total = sum(energy) or 1.0
    return {name: share / total for name, share in zip(('fine', 'mid', 'coarse'), energy)}


def grade_split(before: np.ndarray, after: np.ndarray, *, lut_size: int = 32, local_size: int = 16,
                local_sigma: float = 1 / 60, fine_sigma: float = 2.0, coarse_sigma: float = 16.0,
                map_gain: float = 4.0):
    """Return (report, change picture, left picture) for two registered float32 [H,W,3] display images."""
    if before.shape != after.shape:
        raise ValueError(f'before {before.shape[1]}x{before.shape[0]} and after {after.shape[1]}x{after.shape[0]} '
                         'must be registered renders of the same size.')
    if not 2 <= lut_size <= 64 or not 2 <= local_size <= 32:
        raise ValueError('lut_size must be 2..64 and local_size 2..32.')
    if not 0 < fine_sigma < coarse_sigma:
        raise ValueError('fine_sigma must be positive and below coarse_sigma.')
    height, width, _ = before.shape
    source, target = before.reshape(-1, 3), after.reshape(-1, 3)
    change = target - source
    total = float((change ** 2).sum())
    if total <= 0:
        raise ValueError('before and after are identical: there is no change to split.')

    cells = np.clip((source * lut_size).astype(int), 0, lut_size - 1)
    graded = _table_fit(cells, target, (lut_size,) * 3)
    grade_left = float(((target - graded) ** 2).sum())

    neighbourhood = gaussian(luma(before), local_sigma * width)
    keys = np.concatenate([np.clip((source * local_size).astype(int), 0, local_size - 1),
                           np.clip((neighbourhood.reshape(-1, 1) * local_size).astype(int), 0, local_size - 1)],
                          axis=1)
    local = _table_fit(keys, target, (local_size,) * 4)
    local_left = float(((target - local) ** 2).sum())

    left = luma((target - local).reshape(height, width, 3))
    raw = luma(after - before)

    before_luma, after_luma = luma(before).ravel(), luma(after).ravel()
    tenth = np.clip(np.digitize(before_luma, np.linspace(0, 1, 11)) - 1, 0, 9)
    curve = []
    for index in range(10):
        chosen = tenth == index
        if chosen.any():
            curve.append({'band': [index / 10, (index + 1) / 10], 'share': float(chosen.mean()),
                          'before': float(before_luma[chosen].mean()), 'after': float(after_luma[chosen].mean())})
    before_sat, after_sat = saturation(before).ravel(), saturation(after).ravel()
    sat_rows = []
    for name, low, high in SATURATION_BANDS:
        chosen = before_luma >= low if low > 0 else np.ones(before_luma.shape, bool)
        if high is not None:
            chosen &= before_luma < high
        sat_rows.append({'band': name, 'luma': [low, high], 'share': float(chosen.mean()),
                         'before': float(before_sat[chosen].mean()) if chosen.any() else None,
                         'after': float(after_sat[chosen].mean()) if chosen.any() else None})
    report = {
        'schema': SCHEMA,
        'size': [width, height],
        'change_rms': float(np.sqrt(total / change.size)),
        'explained': {'grade': 1 - grade_left / total, 'grade_and_local': 1 - local_left / total,
                      'local_adds': (grade_left - local_left) / total},
        'change_bands': _bands(raw, fine_sigma, coarse_sigma),
        'left_bands': _bands(left, fine_sigma, coarse_sigma),
        'tone_curve': curve,
        'saturation': sat_rows,
        'parameters': {'lut_size': lut_size, 'local_size': local_size, 'local_sigma': local_sigma,
                       'fine_sigma': fine_sigma, 'coarse_sigma': coarse_sigma},
        'method': ('Shares are 1 - residual/change energy over every pixel and channel, the lookups fitted and scored '
                   'on the same pixels. Bands split luma by Gaussian blurs at fine_sigma and coarse_sigma pixels.'),
    }
    return report, signed_picture(raw, map_gain), signed_picture(left, map_gain)
