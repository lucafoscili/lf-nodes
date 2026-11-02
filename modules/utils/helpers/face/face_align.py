"""Landmark-aligned face crops with disjoint region masks, and ArcFace identity.

Every input face is mapped by one similarity transform onto ArcFace's five-point
template scaled into a square crop, so two renders of the same face line up
pixel for pixel. Regions come from the iBUG 68-point landmarks; workflow masks
(hair from a segmenter, say) ride the same transform. The metadata is an
``lf.text-region-masks.v1`` document, so Region Color Stats and Region Feature
Similarity consume it unchanged.
"""
from __future__ import annotations

import logging

import numpy as np
import torch

from ..detection.region_masks import TEXT_REGION_MASK_SCHEMA, resolve_region_overlaps
from ..logic.normalize_output_mask import normalize_output_mask
from . import insightface_onnx as onnx_faces

LOG = logging.getLogger(__name__)
ALIGNMENT_SCHEMA = 'lf.face-alignment.v1'
IDENTITY_SCHEMA = 'lf.face-identity.v1'
SELECT_POLICIES = ('center', 'largest', 'confident')
# iBUG 68 indices.
JAW, BROW_L, BROW_R = range(0, 17), range(17, 22), range(22, 27)
EYE_L, EYE_R, LIPS_OUT, LIPS_IN = range(36, 42), range(42, 48), range(48, 60), range(60, 68)
LANDMARK_REGIONS = (
    {'id': 'skin', 'prompt': 'landmarks: jaw line and raised brows, minus the parts below', 'priority': 0},
    {'id': 'brows', 'prompt': 'landmarks: brow polylines', 'priority': 30},
    {'id': 'eyes', 'prompt': 'landmarks: eye openings', 'priority': 40},
    {'id': 'lips', 'prompt': 'landmarks: outer lips minus the inner mouth', 'priority': 40},
)


def _polygon(mask, points):
    import cv2

    cv2.fillPoly(mask, [np.round(np.asarray(points) * 8).astype(np.int32)], 1, lineType=cv2.LINE_8, shift=3)


def landmark_masks(landmarks, size):
    """Return {id: bool [size,size]} for skin, brows, eyes and lips from crop-space landmarks."""
    import cv2

    pts = np.asarray(landmarks, dtype=np.float64)
    if pts.shape != (68, 2) or not np.isfinite(pts).all():
        raise ValueError('landmarks must be 68 finite (x, y) points.')
    interocular = np.linalg.norm(pts[list(EYE_R)].mean(0) - pts[list(EYE_L)].mean(0))
    up = pts[27] - pts[8]
    up /= max(np.linalg.norm(up), 1e-9)
    brows = np.concatenate([pts[list(BROW_L)], pts[list(BROW_R)]])
    forehead = brows + up * 0.6 * interocular
    masks = {key: np.zeros((size, size), np.uint8) for key in ('skin', 'brows', 'eyes', 'lips')}
    _polygon(masks['skin'], np.concatenate([pts[list(JAW)], forehead[::-1]]))
    thickness = max(1, int(round(0.12 * interocular)))
    for brow in (BROW_L, BROW_R):
        cv2.polylines(masks['brows'], [np.round(pts[list(brow)]).astype(np.int32)], False, 1, thickness)
    for eye in (EYE_L, EYE_R):
        _polygon(masks['eyes'], pts[list(eye)])
    grow = max(1, int(round(0.03 * interocular)))
    masks['eyes'] = cv2.dilate(masks['eyes'], np.ones((2 * grow + 1, 2 * grow + 1), np.uint8))
    _polygon(masks['lips'], pts[list(LIPS_OUT)])
    inner = np.zeros_like(masks['lips'])
    _polygon(inner, pts[list(LIPS_IN)])
    masks['lips'] &= 1 - inner
    return {key: value.astype(bool) for key, value in masks.items()}


def mask_items(value):
    """Flatten MASK tensors, batches and lists into ordered [H,W] items."""
    items = []

    def collect(item):
        if item is None:
            return
        if isinstance(item, (list, tuple)):
            for child in item:
                collect(child)
        elif torch.is_tensor(item):
            if item.ndim == 2:
                items.append(item)
            elif item.ndim == 3:
                items.extend(item.unbind(0))
            else:
                raise ValueError('extra_masks must be MASK tensors [B,H,W] or [H,W].')
        else:
            raise ValueError('extra_masks must be MASK tensors.')

    collect(value)
    return items


def _extra_rows(extra_ids, extra_priority, count):
    ids = [part.strip() for part in (extra_ids or '').split(',') if part.strip()]
    if count and len(ids) != count:
        raise ValueError(f'extra_ids names {len(ids)} region(s) but extra_masks carries {count} per image.')
    taken = {row['id'] for row in LANDMARK_REGIONS}
    if any(identifier in taken for identifier in ids) or len(set(ids)) != len(ids):
        raise ValueError('extra_ids must be unique and differ from skin, brows, eyes and lips.')
    return [{'id': identifier, 'prompt': f'workflow mask: {identifier}', 'priority': extra_priority}
            for identifier in ids] if count else []


def align_faces(images, model_pack, *, crop_size=512, face_scale=0.5, select='center', det_size=640,
                score_threshold=0.5, extra_masks=None, extra_ids='', extra_priority=35, pack=None):
    """Align one face per image. ``images`` are [1,H,W,C] tensors; extra masks are region-major."""
    if select not in SELECT_POLICIES:
        raise ValueError(f"select must be one of {', '.join(SELECT_POLICIES)}.")
    if not 64 <= crop_size <= 4096 or crop_size % 16:
        raise ValueError('crop_size must be a multiple of 16 between 64 and 4096.')
    if not 0.1 <= face_scale <= 1.0:
        raise ValueError('face_scale must be between 0.1 and 1.0.')
    pack = pack or onnx_faces.load_pack(model_pack)
    extras = list(extra_masks or [])
    if len(extras) % len(images):
        raise ValueError(f'extra_masks holds {len(extras)} masks for {len(images)} images; '
                         'it needs image_count * region_count masks in region-major order.')
    extra_count = len(extras) // len(images)
    rows = list(LANDMARK_REGIONS) + _extra_rows(extra_ids, extra_priority, extra_count)
    template = onnx_faces.crop_template(crop_size, face_scale)
    crops, mask_sets, set_tensors, faces = [], [], [], []
    for index, image in enumerate(images):
        label = f'image {index}'
        source = image[0, ..., :3].detach().to(device='cpu', dtype=torch.float32).numpy()
        height, width = source.shape[:2]
        found = onnx_faces.detect_faces(pack, source, det_size, score_threshold)
        face = onnx_faces.select_face(found, select, (width, height), f'{label} ({width}x{height})')
        landmarks = onnx_faces.landmarks_68(pack, source, face['bbox'])
        matrix = onnx_faces.similarity_matrix(face['kps'], template)
        crop = np.clip(onnx_faces.warp(source, matrix, crop_size), 0, 1)
        to_crop = lambda p: np.asarray(p) @ matrix[:, :2].T + matrix[:, 2]
        lm_crop = to_crop(landmarks)
        parts = landmark_masks(lm_crop, crop_size)
        region_masks = [torch.from_numpy(parts[row['id']]).float()[None] for row in LANDMARK_REGIONS]
        for k in range(extra_count):
            extra = extras[k * len(images) + index]
            extra = extra.detach().to(device='cpu', dtype=torch.float32)
            if tuple(extra.shape) != (height, width):
                raise ValueError(f"{label}: extra mask '{rows[len(LANDMARK_REGIONS) + k]['id']}' is "
                                 f'{tuple(extra.shape[::-1])}, not the source size {width}x{height}.')
            warped = onnx_faces.warp(extra.numpy(), matrix, crop_size) >= 0.5
            region_masks.append(torch.from_numpy(warped).float()[None])
        resolved, records = resolve_region_overlaps(region_masks, rows)
        for record in records:
            if 'warning' in record:
                LOG.warning('%s region %s: %s', label, record['id'], record['warning'])
        crops.append(torch.from_numpy(crop).float()[None])
        set_tensors.append(resolved)
        mask_sets.append({'image_index': index, 'regions': records})
        faces.append({'image_index': index, 'source_size': [width, height], 'faces_found': len(found),
                      'bbox': [round(v, 3) for v in face['bbox']], 'score': round(face['score'], 5),
                      'kps': np.round(face['kps'], 3).tolist(), 'kps_crop': np.round(to_crop(face['kps']), 3).tolist(),
                      'landmarks_crop': np.round(lm_crop, 3).tolist(), 'matrix': np.round(matrix, 6).tolist()})
    document = {'schema': TEXT_REGION_MASK_SCHEMA, 'source_size': [crop_size, crop_size],
                'image_count': len(images), 'regions': rows, 'ordering': 'image-major', 'mask_sets': mask_sets,
                'face_alignment': {'schema': ALIGNMENT_SCHEMA, 'model_pack': pack.name, 'model_files': dict(pack.files),
                                   'crop_size': crop_size, 'face_scale': face_scale, 'select': select,
                                   'det_size': det_size, 'score_threshold': score_threshold,
                                   'template': 'arcface_112_five_point', 'faces': faces}}
    batches, mask_list = normalize_output_mask(set_tensors)
    return crops, batches[0], document, mask_list


def face_identity(images, metadata, model_pack, reference_index=0, pack=None):
    """ArcFace cosine of every aligned face against the reference, plus the full matrix."""
    alignment = metadata.get('face_alignment') if isinstance(metadata, dict) else None
    if not isinstance(alignment, dict) or alignment.get('schema') != ALIGNMENT_SCHEMA:
        raise ValueError('metadata must come from Face Align (it carries lf.face-alignment.v1).')
    faces = alignment['faces']
    if len(faces) != len(images):
        raise ValueError(f'metadata describes {len(faces)} faces but {len(images)} images arrived.')
    if not 0 <= reference_index < len(images):
        raise ValueError(f'reference_index {reference_index} is outside 0..{len(images) - 1}.')
    size = alignment['crop_size']
    pack = pack or onnx_faces.load_pack(model_pack)
    vectors = []
    for index, (image, face) in enumerate(zip(images, faces)):
        if tuple(image.shape[1:3]) != (size, size):
            raise ValueError(f'image {index} is not the {size}x{size} aligned crop its metadata describes.')
        source = image[0, ..., :3].detach().to(device='cpu', dtype=torch.float32).numpy()
        vectors.append(onnx_faces.embed(pack, source, np.asarray(face['kps_crop'])))
    matrix = np.clip(np.stack(vectors) @ np.stack(vectors).T, -1, 1)
    return {'schema': IDENTITY_SCHEMA, 'model_pack': pack.name, 'model_file': pack.files['recognition'],
            'metric': 'arcface_cosine', 'reference_index': reference_index,
            'pairs': [{'reference': reference_index, 'image': i, 'cosine': round(float(matrix[reference_index, i]), 6)}
                      for i in range(len(images))],
            'matrix': np.round(matrix, 6).tolist()}
