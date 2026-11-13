"""Tone profiles of regions, and reads of one region against another.

A profile describes a region's pixels in display values: mean and median luma, its deciles, the darkest quarter
(``shade``), that quarter over the median (``fill``, how far the shade is lifted), the darkest quarter's red over blue
(its warmth), the brightest 5% over the median (``sheen``), the mean absolute Laplacian of luma inside the region
times 1000 (``detail``) and the HSV saturation of its dark, mid and bright thirds (by the region's own terciles).

A read is one line, ``name: A / B``, comparing two pixel sets of the same image by their mean luma, mean saturation
and red over blue. Each side is an expression over named regions, evaluated left to right:

* ``face`` is a region; ``frame`` is every pixel;
* ``ring(face)`` is the band ``ring_inner`` to ``ring_outer`` pixels outside it (city-block distance);
* ``edge(face)`` is its outermost ``edge_px`` pixels, ``inside(face)`` what is left after removing ``inside_px``;
* ``near(hair)`` is the region and every pixel within ``ring_inner`` of it, to keep a read off a neighbour's border;
* a function takes one region or a union of them: ``ring(face|hair)`` rings the whole head;
* ``facing<0.3`` and ``facing>0.7`` select pixels by a facing map (N.V: 1 faces the viewer, 0 grazes), when given;
* ``&`` intersects, ``|`` unites and ``-`` subtracts: ``edge(face) & forehead``, ``skin - hair``.
"""
from __future__ import annotations

import re

import numpy as np

from ..detection.region_masks import region_mask_sets
from .common import LUMA, luma, saturation

PROFILE_SCHEMA = 'lf.tone-profile.v1'
READS_SCHEMA = 'lf.region-reads.v1'
DEFAULT_READS = 'face / ring(face)\nedge(face) / inside(face)'
_TOKEN = re.compile(r'\s*(?:(?P<func>ring|edge|inside|near)\s*\(\s*(?P<arg>[A-Za-z_][\w.]*(?:\s*\|\s*[A-Za-z_][\w.]*)*)\s*\)'
                    r'|facing\s*(?P<cmp>[<>])\s*(?P<num>\d*\.?\d+)'
                    r'|(?P<op>[&|-])'
                    r'|(?P<id>[A-Za-z_][\w.]*))')


def region_dict(masks, metadata, shape, name: str) -> dict[str, np.ndarray]:
    """One lf.text-region-masks.v1 set (exactly one image) as {id: bool [H,W]} at ``shape``."""
    tensor, document = region_mask_sets(masks, metadata)
    if tensor.shape[0] != 1:
        raise ValueError(f'{name} must hold the regions of exactly one image.')
    if tuple(tensor.shape[-2:]) != tuple(shape):
        raise ValueError(f'{name} are {tensor.shape[-1]}x{tensor.shape[-2]}, the image {shape[1]}x{shape[0]}.')
    return {row['id']: tensor[0, index].numpy() > 0.5 for index, row in enumerate(document['regions'])}


def _laplacian(values: np.ndarray) -> np.ndarray:
    out = np.zeros_like(values)
    out[1:-1, 1:-1] = np.abs(4 * values[1:-1, 1:-1] - values[:-2, 1:-1] - values[2:, 1:-1]
                             - values[1:-1, :-2] - values[1:-1, 2:])
    return out


def tone_profile(rgb: np.ndarray, mask: np.ndarray | None = None, *, min_pixels: int = 200) -> dict:
    """Profile of the pixels of a float32 [H,W,3] display image under a bool mask (all pixels without one)."""
    if mask is None:
        mask = np.ones(rgb.shape[:2], bool)
    count = int(mask.sum())
    if count < min_pixels:
        return {'n': count, 'warning': f'{count} pixels, under the {min_pixels} needed.'}
    values = rgb @ LUMA
    region = values[mask]
    median = float(np.median(region))
    darkest = mask & (values <= np.quantile(region, 0.25))
    inner = mask.copy()
    inner[1:-1, 1:-1] &= mask[:-2, 1:-1] & mask[2:, 1:-1] & mask[1:-1, :-2] & mask[1:-1, 2:]
    inner[[0, -1], :] = False
    inner[:, [0, -1]] = False
    sat = saturation(rgb[mask], floor=1e-6)
    thirds = np.quantile(region, [1 / 3, 2 / 3])
    picks = (region <= thirds[0], (region > thirds[0]) & (region <= thirds[1]), region > thirds[1])
    shade = float(values[darkest].mean())
    return {
        'n': count,
        'mean': float(region.mean()),
        'median': median,
        'deciles': [float(v) for v in np.quantile(region, np.linspace(0.1, 0.9, 9))],
        'shade': shade,
        'fill': shade / median if median > 0 else None,
        'shade_rb': float(rgb[..., 0][darkest].mean() / max(rgb[..., 2][darkest].mean(), 1e-6)),
        'rb': float(rgb[..., 0][mask].mean() / max(rgb[..., 2][mask].mean(), 1e-6)),
        'sheen': float(region[region >= np.quantile(region, 0.95)].mean() / median) if median > 0 else None,
        'detail': float(_laplacian(values)[inner].mean() * 1000) if inner.any() else None,
        'saturation': float(sat.mean()),
        'saturation_thirds': [float(sat[pick].mean()) if pick.any() else None for pick in picks],
    }


def parse_reads(text: str) -> list[dict]:
    """Parse read lines (``name: A / B``) into {name, a, b} with tokenised sides; blank and # lines are skipped."""
    reads = []
    for number, raw in enumerate((text or '').splitlines(), 1):
        line = raw.split('#', 1)[0].strip()
        if not line:
            continue
        name, _, body = line.rpartition(':') if ':' in line else ('', '', line)
        sides = body.split('/')
        if len(sides) != 2:
            raise ValueError(f'read line {number} ({raw.strip()!r}) needs exactly one "/" between two sides.')
        parsed = [_tokens(side, number) for side in sides]
        reads.append({'name': name.strip() or ' / '.join(side.strip() for side in sides),
                      'a': parsed[0], 'b': parsed[1], 'text': body.strip()})
    if not reads:
        raise ValueError('reads holds no read lines.')
    return reads


def _tokens(side: str, number: int) -> list[tuple]:
    tokens, position, text = [], 0, side.strip()
    while position < len(text):
        match = _TOKEN.match(text, position)
        if not match or match.end() == position:
            raise ValueError(f'read line {number}: cannot parse {text[position:]!r}.')
        position = match.end()
        if match.group('func'):
            tokens.append(('func', match.group('func'), re.sub(r'\s+', '', match.group('arg'))))
        elif match.group('cmp'):
            tokens.append(('facing', match.group('cmp'), float(match.group('num'))))
        elif match.group('op'):
            tokens.append(('op', match.group('op')))
        else:
            tokens.append(('id', match.group('id')))
    kinds = ['op' if token[0] == 'op' else 'term' for token in tokens]
    if not kinds or kinds[0] != 'term' or kinds[-1] != 'term' or any(a == b for a, b in zip(kinds, kinds[1:])):
        raise ValueError(f'read line {number}: {text!r} must alternate terms and operators (&, |, -).')
    return tokens


class _Masks:
    def __init__(self, regions, facing, ring_inner, ring_outer, edge_px, inside_px):
        self.regions, self.facing = regions, facing
        self.ring_inner, self.ring_outer, self.edge_px, self.inside_px = ring_inner, ring_outer, edge_px, inside_px
        self._outside, self._inward = {}, {}

    def region(self, name):
        if '|' in name:  # a function's argument may be a union: ring(face|hair) rings the head
            parts = [self.region(part) for part in name.split('|')]
            return np.logical_or.reduce(parts)
        if name == 'frame':
            return np.ones(next(iter(self.regions.values())).shape, bool) if self.regions else None
        if name not in self.regions:
            raise ValueError(f"no region named '{name}'; known: {', '.join(sorted(self.regions)) or 'none'}.")
        return self.regions[name]

    def distance_outside(self, name):
        if name not in self._outside:
            from scipy.ndimage import distance_transform_cdt

            self._outside[name] = distance_transform_cdt(~self.region(name), metric='taxicab')
        return self._outside[name]

    def distance_inward(self, name):
        if name not in self._inward:
            from scipy.ndimage import distance_transform_cdt

            self._inward[name] = distance_transform_cdt(self.region(name), metric='taxicab')
        return self._inward[name]

    def term(self, token):
        if token[0] == 'id':
            return self.region(token[1])
        if token[0] == 'facing':
            if self.facing is None:
                raise ValueError('a facing< or facing> term needs a facing map.')
            return self.facing < token[2] if token[1] == '<' else self.facing > token[2]
        _, func, name = token
        if func == 'ring':
            distance = self.distance_outside(name)
            return (distance > self.ring_inner) & (distance <= self.ring_outer)
        if func == 'near':
            return self.distance_outside(name) <= self.ring_inner
        inward = self.distance_inward(name)
        return (inward > 0) & (inward <= self.edge_px) if func == 'edge' else inward > self.inside_px

    def evaluate(self, tokens):
        result = self.term(tokens[0])
        for operator, token in zip(tokens[1::2], tokens[2::2]):
            other = self.term(token)
            result = result & other if operator[1] == '&' else result | other if operator[1] == '|' else result & ~other
        return result


def _side(rgb, values, mask, min_pixels):
    count = int(mask.sum())
    if count < min_pixels:
        return {'n': count, 'warning': f'{count} pixels, under the {min_pixels} needed.'}
    pixels = rgb[mask]
    return {'n': count, 'luma': float(values[mask].mean()), 'median': float(np.median(values[mask])),
            'saturation': float(saturation(pixels, floor=1e-6).mean()),
            'rb': float(pixels[:, 0].mean() / max(pixels[:, 2].mean(), 1e-6)),
            'rgb': [float(v) for v in pixels.mean(0)]}


def evaluate_reads(rgb: np.ndarray, regions: dict[str, np.ndarray], reads: list[dict], *,
                   facing: np.ndarray | None = None, ring_inner: int = 12, ring_outer: int = 40, edge_px: int = 4,
                   inside_px: int = 8, min_pixels: int = 200):
    """Return (rows, masks) for parsed reads: per read both sides and their ratios, and each side's bool mask."""
    if not 0 <= ring_inner < ring_outer:
        raise ValueError('ring_inner must be non-negative and below ring_outer.')
    if edge_px < 1 or inside_px < 0:
        raise ValueError('edge_px must be at least 1 and inside_px non-negative.')
    for name, mask in regions.items():
        if mask.shape != rgb.shape[:2]:
            raise ValueError(f"region '{name}' is {mask.shape[1]}x{mask.shape[0]}, the image "
                             f'{rgb.shape[1]}x{rgb.shape[0]}.')
    if facing is not None and facing.shape != rgb.shape[:2]:
        raise ValueError('the facing map must match the image size.')
    masks = _Masks(regions, facing, ring_inner, ring_outer, edge_px, inside_px)
    values = luma(rgb)
    rows, drawn = [], []
    for read in reads:
        a, b = masks.evaluate(read['a']), masks.evaluate(read['b'])
        side_a, side_b = _side(rgb, values, a, min_pixels), _side(rgb, values, b, min_pixels)
        row = {'name': read['name'], 'read': read['text'], 'a': side_a, 'b': side_b,
               'luma_ratio': None, 'saturation_ratio': None, 'rb_difference': None}
        if 'luma' in side_a and 'luma' in side_b:
            row['luma_ratio'] = side_a['luma'] / side_b['luma'] if side_b['luma'] > 0 else None
            row['saturation_ratio'] = (side_a['saturation'] / side_b['saturation']
                                       if side_b['saturation'] > 0 else None)
            row['rb_difference'] = side_a['rb'] - side_b['rb']
        else:
            row['warning'] = ' '.join(side.get('warning', '') for side in (side_a, side_b)).strip()
        rows.append(row)
        drawn.append((a, b))
    return rows, drawn
