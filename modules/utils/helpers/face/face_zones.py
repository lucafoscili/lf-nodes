"""Facial zones at the source image's own size, from iBUG 68-point landmarks.

Zones are bands laid out in the face's own frame: ``down`` runs from the nose bridge (27) to the chin (8), and every
distance is a share of one unit, the interocular distance (between the eye centres), so a zone covers the same part of
any face at any size or tilt. A turned face foreshortens the eyes' distance but not its height, so the unit is never
less than 0.52 of the bridge-to-chin length (about the interocular distance of a frontal face), and the far side's
under-eye and cheek are dropped once its eye is under half as wide as the near one (hidden behind the nose). Zones are
made for reading small shading differences (under-eye creases against the cheek, the forehead's outline against its
interior), not for editing; intersect them with a face mask, since a far-side zone of a turned face can reach past it:

* ``forehead``: from just above the brows to 0.6 interocular above them;
* ``under_eyes``: a band below each lower lid, 0.06 to 0.22 interocular down, as wide as the eye;
* ``cheeks``: 0.32 to 0.62 interocular below each lower lid, from the outer eye corner to three quarters of the eye;
* ``folds``: the nasolabial folds, from each nose wing (31, 35) to the mouth corner (48, 54), shifted outward;
* ``chin``: between the lower lip (57) and the chin (8), half an interocular wide.

Zones are disjoint (earlier ones win) and returned as an ``lf.text-region-masks.v1`` document.
"""
from __future__ import annotations

import numpy as np
import torch

from ..detection.region_masks import TEXT_REGION_MASK_SCHEMA, resolve_region_overlaps
from . import insightface_onnx as onnx_faces

ZONES_SCHEMA = 'lf.face-zones.v1'
HEIGHT_UNIT = 0.52  # the unit's floor as a share of the bridge-to-chin length (a frontal face's eyes' distance)
HIDDEN_EYE = 0.5  # an eye under this share of the other's width is the far side of a turned face
ZONES = (
    {'id': 'under_eyes', 'prompt': 'landmarks: 0.06-0.22 interocular below each lower lid', 'priority': 50},
    {'id': 'cheeks', 'prompt': 'landmarks: 0.32-0.62 interocular below each lower lid, outer three quarters',
     'priority': 40},
    {'id': 'folds', 'prompt': 'landmarks: nose wing to mouth corner, shifted outward', 'priority': 30},
    {'id': 'forehead', 'prompt': 'landmarks: 0.12-0.6 interocular above the brows', 'priority': 20},
    {'id': 'chin', 'prompt': 'landmarks: lower lip to chin, half an interocular wide', 'priority': 10},
)
EYE_LEFT, EYE_RIGHT = (36, 41, 40, 39), (42, 47, 46, 45)  # outer or inner corner, lower lid, other corner


def _fill(shape, polygon):
    import cv2

    mask = np.zeros(shape, np.uint8)
    cv2.fillPoly(mask, [np.round(np.asarray(polygon) * 8).astype(np.int32)], 1, lineType=cv2.LINE_8, shift=3)
    return mask.astype(bool)


def zone_masks(landmarks, shape) -> dict[str, np.ndarray]:
    """Return {zone id: bool [H,W]} for 68 landmarks in source pixels."""
    import cv2

    pts = np.asarray(landmarks, dtype=np.float64)
    if pts.shape != (68, 2) or not np.isfinite(pts).all():
        raise ValueError('landmarks must be 68 finite (x, y) points.')
    centres = pts[36:42].mean(0), pts[42:48].mean(0)
    down = pts[8] - pts[27]
    height = float(np.linalg.norm(down))
    iod = max(float(np.linalg.norm(centres[1] - centres[0])), HEIGHT_UNIT * height)
    if iod <= 2:
        raise ValueError(f'the zone unit is {iod:.1f} px: the face is too small to zone.')
    down /= max(height, 1e-9)
    widths = [float(np.linalg.norm(pts[eye[0]] - pts[eye[-1]])) for eye in (EYE_LEFT, EYE_RIGHT)]
    zones = {}
    under, cheeks = np.zeros(shape, bool), np.zeros(shape, bool)
    for eye, width in zip((EYE_LEFT, EYE_RIGHT), widths):
        if width < HIDDEN_EYE * max(widths):
            continue
        lid = pts[list(eye)]
        under |= _fill(shape, np.concatenate([lid + down * 0.06 * iod, (lid + down * 0.22 * iod)[::-1]]))
        outer, inner = (lid[0], lid[-1]) if eye == EYE_LEFT else (lid[-1], lid[0])
        stop = outer + 0.75 * (inner - outer)
        top, bottom = 0.32 * iod, 0.62 * iod
        cheeks |= _fill(shape, [outer + down * top, stop + down * top, stop + down * bottom, outer + down * bottom])
    zones['under_eyes'], zones['cheeks'] = under, cheeks
    folds = np.zeros(shape, np.uint8)
    middle = (pts[31] + pts[35]) / 2
    for wing, corner in ((pts[31], pts[48]), (pts[35], pts[54])):
        outward = wing - middle
        outward /= max(np.linalg.norm(outward), 1e-9)
        line = np.array([wing + outward * 0.08 * iod, corner + outward * 0.08 * iod])
        cv2.polylines(folds, [np.round(line).astype(np.int32)], False, 1, max(1, int(round(0.08 * iod))))
    zones['folds'] = folds.astype(bool)
    brows = pts[17:27]
    zones['forehead'] = _fill(shape, np.concatenate([brows - down * 0.12 * iod, (brows - down * 0.6 * iod)[::-1]]))
    across = np.array([-down[1], down[0]]) * 0.25 * iod
    lip, chin = pts[57] + down * 0.1 * iod, pts[8] - down * 0.1 * iod
    zones['chin'] = _fill(shape, [lip - across, lip + across, chin + across, chin - across])
    return zones


def face_zones(image, model_pack, *, select='largest', det_size=1280, score_threshold=0.5, pack=None):
    """Zone one face in a [1,H,W,C] image; return (masks [Z,H,W], document, landmarks)."""
    pack = pack or onnx_faces.load_pack(model_pack)
    source = image[0, ..., :3].detach().to(device='cpu', dtype=torch.float32).numpy()
    height, width = source.shape[:2]
    found = onnx_faces.detect_faces(pack, source, det_size, score_threshold)
    face = onnx_faces.select_face(found, select, (width, height), f'image ({width}x{height})')
    landmarks = onnx_faces.landmarks_68(pack, source, face['bbox'])
    zones = zone_masks(landmarks, (height, width))
    raw = [torch.from_numpy(zones[row['id']]).float()[None] for row in ZONES]
    resolved, records = resolve_region_overlaps(raw, list(ZONES))
    document = {'schema': TEXT_REGION_MASK_SCHEMA, 'source_size': [width, height], 'image_count': 1,
                'regions': [dict(row) for row in ZONES], 'ordering': 'image-major',
                'mask_sets': [{'image_index': 0, 'regions': records}],
                'face_zones': {'schema': ZONES_SCHEMA, 'model_pack': pack.name, 'select': select,
                               'det_size': det_size, 'score_threshold': score_threshold,
                               'faces_found': len(found), 'bbox': [round(v, 3) for v in face['bbox']],
                               'score': round(face['score'], 5),
                               'landmarks': np.round(landmarks, 3).tolist()}}
    return resolved, document
