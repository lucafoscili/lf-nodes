"""InsightFace model packs run through onnxruntime: SCRFD detection, 68-point
landmarks and ArcFace embeddings, without the insightface package.

A pack is a folder of ONNX files (``antelopev2``, ``buffalo_l``) under a
ComfyUI ``insightface`` model root. Each file's role is read from its own
input/output signature, never from its name. LF Nodes ships no weights.
"""
from __future__ import annotations

import logging
import os
import threading
from dataclasses import dataclass, field

import numpy as np

LOG = logging.getLogger(__name__)

# ArcFace's canonical five points (left eye, right eye, nose, left mouth, right
# mouth, in image terms) for its 112 x 112 input.
ARCFACE_TEMPLATE = np.array([
    [38.2946, 51.6963], [73.5318, 51.5014], [56.0252, 71.7366],
    [41.5493, 92.3655], [70.7299, 92.2041]], dtype=np.float64)
ARCFACE_SIZE = 112
SCRFD_STRIDES = (8, 16, 32)
SCRFD_ANCHORS = 2
LANDMARK_SIZE = 192


class FaceModelError(ValueError):
    """A pack, a model file or its signature cannot serve the request."""


def insightface_roots():
    """Return candidate ``insightface`` folders, registered first."""
    import folder_paths  # Comfy boundary, imported lazily for CPU tests.

    roots = []
    registered = getattr(folder_paths, 'folder_names_and_paths', {}).get('insightface')
    if registered:
        roots.extend(registered[0])
    roots.append(os.path.join(folder_paths.models_dir, 'insightface'))
    unique = []
    for root in roots:
        if root not in unique:
            unique.append(root)
    return unique


def pack_directories(roots=None):
    """Map each pack name to its folder: ``<root>/models/<pack>`` or ``<root>/<pack>``."""
    packs = {}
    for root in roots if roots is not None else insightface_roots():
        for parent in (os.path.join(root, 'models'), root):
            if not os.path.isdir(parent):
                continue
            for name in sorted(os.listdir(parent)):
                folder = os.path.join(parent, name)
                if os.path.isdir(folder) and any(f.endswith('.onnx') for f in os.listdir(folder)):
                    packs.setdefault(name, folder)
    return packs


def available_packs():
    try:
        names = sorted(pack_directories())
    except Exception as error:  # Listing must not break node registration.
        LOG.warning('InsightFace packs could not be listed: %s', error)
        names = []
    return names or ['(no insightface pack found)']


@dataclass
class FacePack:
    name: str
    folder: str
    detector: object = None
    landmarks: object = None
    recognition: object = None
    files: dict = field(default_factory=dict)


_PACKS: dict[str, FacePack] = {}
_LOCK = threading.Lock()


def _role(session):
    inputs, outputs = session.get_inputs(), session.get_outputs()
    if len(inputs) != 1:
        return None
    shape = list(inputs[0].shape)
    if len(outputs) == 3 * len(SCRFD_STRIDES) and len(shape) == 4 and shape[1] == 3:
        return 'detector'
    if shape[2:] == [ARCFACE_SIZE, ARCFACE_SIZE] and len(outputs) == 1 and outputs[0].shape[-1] == 512:
        return 'recognition'
    if shape[2:] == [LANDMARK_SIZE, LANDMARK_SIZE] and len(outputs) == 1 and outputs[0].shape[-1] == 3309:
        return 'landmarks'
    return None


def load_pack(name, roots=None, session_factory=None):
    """Open (once) the detector, 68-point landmark and recognition models of a pack."""
    if not isinstance(name, str) or not name.strip() or name.startswith('('):
        raise FaceModelError('model_pack must name an InsightFace pack folder (antelopev2, buffalo_l).')
    injected = session_factory is not None
    with _LOCK:
        if name in _PACKS and not injected:
            return _PACKS[name]
        folder = pack_directories(roots).get(name)
        if folder is None:
            raise FaceModelError(f"InsightFace pack '{name}' was not found under {roots or insightface_roots()}.")
        if session_factory is None:
            import onnxruntime as ort

            def session_factory(path):
                options = ort.SessionOptions()
                # SCRFD exports declare 640-canvas output shapes; other canvases log a warning per run.
                options.log_severity_level = 3
                return ort.InferenceSession(path, sess_options=options, providers=['CPUExecutionProvider'])
        pack = FacePack(name, folder)
        for filename in sorted(os.listdir(folder)):
            if not filename.endswith('.onnx'):
                continue
            session = session_factory(os.path.join(folder, filename))
            role = _role(session)
            if role and getattr(pack, role) is None:
                setattr(pack, role, session)
                pack.files[role] = filename
        missing = [role for role in ('detector', 'landmarks', 'recognition') if getattr(pack, role) is None]
        if missing:
            raise FaceModelError(f"InsightFace pack '{name}' ({folder}) lacks a {', '.join(missing)} model.")
        if not injected:
            _PACKS[name] = pack
        return pack


def _nms(boxes, scores, threshold):
    order = scores.argsort()[::-1]
    keep = []
    areas = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
    while order.size:
        i = order[0]
        keep.append(i)
        xx1 = np.maximum(boxes[i, 0], boxes[order[1:], 0])
        yy1 = np.maximum(boxes[i, 1], boxes[order[1:], 1])
        xx2 = np.minimum(boxes[i, 2], boxes[order[1:], 2])
        yy2 = np.minimum(boxes[i, 3], boxes[order[1:], 3])
        inter = np.maximum(0, xx2 - xx1) * np.maximum(0, yy2 - yy1)
        overlap = inter / (areas[i] + areas[order[1:]] - inter)
        order = order[1:][overlap <= threshold]
    return keep


def anchor_centers(height, width, stride):
    """SCRFD anchor centres, row-major, each repeated once per anchor."""
    grid = np.stack(np.mgrid[:height, :width][::-1], axis=-1).astype(np.float32)
    return np.repeat(grid.reshape(-1, 2) * stride, SCRFD_ANCHORS, axis=0)


def decode_scrfd(outputs, det_size, score_threshold):
    """Decode SCRFD's nine outputs (scores, boxes, keypoints per stride) on the canvas."""
    if len(outputs) != 3 * len(SCRFD_STRIDES):
        raise FaceModelError('The detector must return scores, boxes and keypoints for strides 8, 16 and 32.')
    boxes, scores, points = [], [], []
    count = len(SCRFD_STRIDES)
    for index, stride in enumerate(SCRFD_STRIDES):
        score, box, kps = (np.asarray(outputs[index + count * k]) for k in range(3))
        if score.ndim == 3:  # batched export
            score, box, kps = score[0], box[0], kps[0]
        centers = anchor_centers(det_size // stride, det_size // stride, stride)
        if score.shape[0] != centers.shape[0] or box.shape[-1] != 4 or kps.shape[-1] != 10:
            raise FaceModelError(f'Detector output at stride {stride} does not match a {det_size} canvas.')
        keep = np.where(score[:, 0] >= score_threshold)[0]
        if not keep.size:
            continue
        c, d = centers[keep], box[keep] * stride
        boxes.append(np.stack([c[:, 0] - d[:, 0], c[:, 1] - d[:, 1],
                               c[:, 0] + d[:, 2], c[:, 1] + d[:, 3]], axis=-1))
        k = kps[keep].reshape(-1, 5, 2) * stride
        points.append(c[:, None, :] + k)
        scores.append(score[keep, 0])
    if not boxes:
        return np.zeros((0, 4)), np.zeros(0), np.zeros((0, 5, 2))
    return np.concatenate(boxes), np.concatenate(scores), np.concatenate(points)


def detect_faces(pack, image, det_size=640, score_threshold=0.5, nms_threshold=0.4):
    """Detect faces in an RGB float [H,W,3] image in 0..1; return a list of dicts in source pixels."""
    import cv2

    if det_size % 32:
        raise FaceModelError('det_size must be a multiple of 32.')
    height, width = image.shape[:2]
    scale = det_size / max(height, width)
    new_w, new_h = max(1, round(width * scale)), max(1, round(height * scale))
    pixels = np.clip(np.asarray(image, dtype=np.float32) * 255.0, 0, 255)
    canvas = np.zeros((det_size, det_size, 3), dtype=np.float32)
    canvas[:new_h, :new_w] = cv2.resize(pixels, (new_w, new_h), interpolation=cv2.INTER_AREA
                                        if scale < 1 else cv2.INTER_LINEAR)
    blob = ((canvas - 127.5) / 128.0).transpose(2, 0, 1)[None]
    session = pack.detector
    outputs = session.run(None, {session.get_inputs()[0].name: blob})
    boxes, scores, points = decode_scrfd(outputs, det_size, score_threshold)
    faces = []
    for i in _nms(boxes, scores, nms_threshold) if len(scores) else []:
        faces.append({'bbox': (boxes[i] / scale).tolist(), 'score': float(scores[i]),
                      'kps': (points[i] / scale).tolist()})
    return faces


def select_face(faces, policy, image_size, label):
    """Pick one face by policy; fail loud when none was found."""
    if not faces:
        raise FaceModelError(f'{label}: no face found.')
    width, height = image_size
    if policy == 'largest':
        key = lambda f: -(f['bbox'][2] - f['bbox'][0]) * (f['bbox'][3] - f['bbox'][1])
    elif policy == 'center':
        key = lambda f: ((f['bbox'][0] + f['bbox'][2]) / 2 - width / 2) ** 2 + \
            ((f['bbox'][1] + f['bbox'][3]) / 2 - height / 2) ** 2
    elif policy == 'confident':
        key = lambda f: -f['score']
    else:
        raise FaceModelError("select must be 'center', 'largest' or 'confident'.")
    return sorted(faces, key=key)[0]


def landmarks_68(pack, image, bbox):
    """iBUG 68-point landmarks (x,y) in source pixels from the pack's 1k3d68 model."""
    import cv2

    x1, y1, x2, y2 = bbox
    side = max(x2 - x1, y2 - y1)
    if side <= 0:
        raise FaceModelError('Face box has no area.')
    scale = LANDMARK_SIZE / (side * 1.5)
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    matrix = np.array([[scale, 0, LANDMARK_SIZE / 2 - cx * scale],
                       [0, scale, LANDMARK_SIZE / 2 - cy * scale]], dtype=np.float64)
    pixels = np.clip(np.asarray(image, dtype=np.float32) * 255.0, 0, 255)
    crop = cv2.warpAffine(pixels, matrix, (LANDMARK_SIZE, LANDMARK_SIZE), flags=cv2.INTER_LINEAR)
    # The 1k3d68 export carries its own input normalisation (raw 0..255 RGB).
    blob = crop.transpose(2, 0, 1)[None].astype(np.float32)
    session = pack.landmarks
    pred = np.asarray(session.run(None, {session.get_inputs()[0].name: blob})[0][0], dtype=np.float64)
    pred = pred.reshape(-1, 3)[-68:, :2]
    pred = (pred + 1) * (LANDMARK_SIZE // 2)
    inverse = cv2.invertAffineTransform(matrix)
    return pred @ inverse[:, :2].T + inverse[:, 2]


def similarity_matrix(source, target):
    """Least-squares similarity (Umeyama) mapping source points onto target points, 2x3."""
    source, target = np.asarray(source, np.float64), np.asarray(target, np.float64)
    mu_s, mu_t = source.mean(0), target.mean(0)
    s, t = source - mu_s, target - mu_t
    cov = t.T @ s / len(source)
    u, sigma, vt = np.linalg.svd(cov)
    d = np.eye(2)
    if np.linalg.det(u) * np.linalg.det(vt) < 0:
        d[1, 1] = -1
    rotation = u @ d @ vt
    scale = (sigma * np.diag(d)).sum() / s.var(0).sum()
    matrix = np.zeros((2, 3))
    matrix[:, :2] = scale * rotation
    matrix[:, 2] = mu_t - matrix[:, :2] @ mu_s
    return matrix


def crop_template(size, face_scale):
    """ArcFace's five points placed in a ``size`` square, the face spanning ``face_scale`` of it."""
    return (ARCFACE_TEMPLATE - ARCFACE_SIZE / 2) * (size / ARCFACE_SIZE) * face_scale + size / 2


def warp(image, matrix, size):
    import cv2

    return cv2.warpAffine(np.asarray(image, dtype=np.float32), matrix, (size, size),
                          flags=cv2.INTER_CUBIC if matrix[0, 0] ** 2 + matrix[0, 1] ** 2 > 1 else cv2.INTER_AREA,
                          borderMode=cv2.BORDER_CONSTANT, borderValue=0)


def embed(pack, image, kps):
    """L2-normalised ArcFace embedding of the face whose five points are ``kps`` in ``image``."""
    matrix = similarity_matrix(kps, ARCFACE_TEMPLATE)
    face = np.clip(warp(image[..., :3], matrix, ARCFACE_SIZE), 0, 1) * 255.0
    blob = ((face - 127.5) / 127.5).transpose(2, 0, 1)[None].astype(np.float32)
    session = pack.recognition
    vector = np.asarray(session.run(None, {session.get_inputs()[0].name: blob})[0][0], dtype=np.float64)
    norm = np.linalg.norm(vector)
    if not np.isfinite(norm) or norm == 0:
        raise FaceModelError('The recognition model returned a zero or non-finite embedding.')
    return vector / norm
