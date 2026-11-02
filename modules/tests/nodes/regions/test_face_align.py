"""Face Align and Face Identity on stub ONNX sessions: no weights, no faces.

The stubs return SCRFD-, 1k3d68- and ArcFace-shaped arrays, so the decoder,
the alignment geometry, the region masks and the node contracts are exercised
without InsightFace models or any real face image.
"""
import os
from types import SimpleNamespace

import numpy as np
import pytest
import torch

from modules.nodes.analytics import face_identity as identity_module
from modules.nodes.analytics.face_identity import LF_FaceIdentity
from modules.nodes.regions import face_align as align_module
from modules.nodes.regions.face_align import LF_FaceAlign
from modules.utils.helpers.detection.region_masks import region_mask_sets
from modules.utils.helpers.face import face_align as helper
from modules.utils.helpers.face import insightface_onnx as onnx_faces
from modules.utils.helpers.ui import generated_preview

DET = 640
# A face whose five points sit on ArcFace's template scaled 2x around (320, 240).
KPS = (onnx_faces.ARCFACE_TEMPLATE - 56) * 2 + np.array([320, 240])


@pytest.fixture(autouse=True)
def preview_root(monkeypatch, tmp_path):
    monkeypatch.setattr(generated_preview, 'get_comfy_dir', lambda _kind: str(tmp_path / 'input'))


class Session:
    def __init__(self, input_shape, outputs, run):
        self._inputs = [SimpleNamespace(name='x', shape=input_shape)]
        self._outputs = [SimpleNamespace(shape=shape) for shape in outputs]
        self._run = run
        self.calls = []

    def get_inputs(self):
        return self._inputs

    def get_outputs(self):
        return self._outputs

    def run(self, _names, feeds):
        self.calls.append(feeds['x'])
        return self._run(feeds['x'])


def _scrfd_outputs(faces, det=DET):
    """faces: list of (score, bbox[4], kps[5,2]) on the canvas; one anchor each at stride 8."""
    outputs = []
    sizes = [(det // s) ** 2 * 2 for s in onnx_faces.SCRFD_STRIDES]
    scores = [np.zeros((n, 1), np.float32) for n in sizes]
    boxes = [np.zeros((n, 4), np.float32) for n in sizes]
    points = [np.zeros((n, 10), np.float32) for n in sizes]
    centers = onnx_faces.anchor_centers(det // 8, det // 8, 8)
    for score, bbox, kps in faces:
        cx, cy = (bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2
        index = int(np.argmin(((centers - [cx, cy]) ** 2).sum(1)))
        c = centers[index]
        scores[0][index, 0] = score
        boxes[0][index] = [(c[0] - bbox[0]) / 8, (c[1] - bbox[1]) / 8, (bbox[2] - c[0]) / 8, (bbox[3] - c[1]) / 8]
        points[0][index] = ((np.asarray(kps) - c) / 8).reshape(-1)
    outputs.extend(scores + boxes + points)
    return outputs


def _landmark_template():
    """A plausible iBUG 68 layout in a unit face (x right, y down), centred on 0."""
    pts = np.zeros((68, 2))
    t = np.linspace(-1, 1, 17)
    pts[0:17] = np.stack([0.9 * np.sin(t * 1.3), 0.1 + 0.9 * np.cos(t * 1.3) * 0.9], 1) * [1, 1]
    pts[0:17, 1] = -0.2 + 1.0 * np.cos(t * 1.2)
    pts[17:22] = np.stack([np.linspace(-0.75, -0.15, 5), np.full(5, -0.55)], 1)
    pts[22:27] = np.stack([np.linspace(0.15, 0.75, 5), np.full(5, -0.55)], 1)
    pts[27:31] = np.stack([np.zeros(4), np.linspace(-0.4, 0.05, 4)], 1)
    pts[31:36] = np.stack([np.linspace(-0.2, 0.2, 5), np.full(5, 0.15)], 1)
    for start, cx in ((36, -0.42), (42, 0.42)):
        angle = np.linspace(np.pi, -np.pi, 6, endpoint=False)
        pts[start:start + 6] = np.stack([cx + 0.18 * np.cos(angle), -0.38 + 0.07 * np.sin(angle)], 1)
    angle = np.linspace(np.pi, -np.pi, 12, endpoint=False)
    pts[48:60] = np.stack([0.38 * np.cos(angle), 0.45 + 0.14 * np.sin(angle)], 1)
    angle = np.linspace(np.pi, -np.pi, 8, endpoint=False)
    pts[60:68] = np.stack([0.3 * np.cos(angle), 0.45 + 0.03 * np.sin(angle)], 1)
    return pts


def _pack(faces, vector=None):
    detector = Session([1, 3, '?', '?'], [(1,)] * 9, lambda _x: _scrfd_outputs(faces))

    def landmarks(_x):
        # Normalised -1..1 around the 192 crop centre; 3309 values, the last 68 rows used.
        out = np.zeros((1103, 3), np.float32)
        out[-68:, :2] = _landmark_template() * 0.45
        return [out.reshape(1, -1)]

    def recognise(x):
        base = vector if vector is not None else np.arange(1, 513, dtype=np.float32)
        return [(base * (1 + float(x.mean()))).reshape(1, -1)]

    return onnx_faces.FacePack(
        'stub', 'stub', detector=detector,
        landmarks=Session([None, 3, 192, 192], [(1, 3309)], landmarks),
        recognition=Session([None, 3, 112, 112], [(1, 512)], recognise),
        files={'detector': 'det.onnx', 'landmarks': '1k3d68.onnx', 'recognition': 'arc.onnx'})


def _face_box():
    return [KPS[:, 0].min() - 40, KPS[:, 1].min() - 50, KPS[:, 0].max() + 40, KPS[:, 1].max() + 30]


def test_scrfd_decoder_recovers_box_points_and_score():
    bbox = [100., 120., 180., 220.]
    kps = np.array([[120, 150], [160, 150], [140, 170], [125, 195], [155, 195]], float)
    boxes, scores, points = onnx_faces.decode_scrfd(_scrfd_outputs([(0.9, bbox, kps)]), DET, 0.5)
    assert scores.tolist() == pytest.approx([0.9])
    np.testing.assert_allclose(boxes[0], bbox, atol=1e-3)
    np.testing.assert_allclose(points[0], kps, atol=1e-3)


def test_anchor_centres_repeat_each_cell_once_per_anchor_row_major():
    centers = onnx_faces.anchor_centers(2, 3, 8)
    assert centers.tolist() == [[0, 0], [0, 0], [8, 0], [8, 0], [16, 0], [16, 0],
                                [0, 8], [0, 8], [8, 8], [8, 8], [16, 8], [16, 8]]


def test_similarity_matrix_recovers_scale_rotation_and_shift():
    angle, scale, shift = 0.3, 1.7, np.array([12., -5.])
    rotation = scale * np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
    target = KPS @ rotation.T + shift
    matrix = onnx_faces.similarity_matrix(KPS, target)
    np.testing.assert_allclose(matrix[:, :2], rotation, atol=1e-9)
    np.testing.assert_allclose(matrix[:, 2], shift, atol=1e-6)


def test_selection_policies_and_no_face_fails_loud():
    faces = [{'bbox': [0, 0, 100, 100], 'score': 0.6}, {'bbox': [300, 220, 340, 260], 'score': 0.9}]
    assert onnx_faces.select_face(faces, 'largest', (640, 480), 'x') is faces[0]
    assert onnx_faces.select_face(faces, 'center', (640, 480), 'x') is faces[1]
    assert onnx_faces.select_face(faces, 'confident', (640, 480), 'x') is faces[1]
    with pytest.raises(onnx_faces.FaceModelError, match='frame.png: no face found'):
        onnx_faces.select_face([], 'center', (640, 480), 'frame.png')


def test_pack_roles_come_from_signatures_and_missing_roles_fail(tmp_path):
    folder = tmp_path / 'models' / 'pack'
    folder.mkdir(parents=True)
    for name in ('a.onnx', 'b.onnx', 'c.onnx'):
        (folder / name).write_bytes(b'')
    stub = _pack([])
    by_file = {'a.onnx': stub.recognition, 'b.onnx': stub.detector, 'c.onnx': stub.landmarks}
    pack = onnx_faces.load_pack('pack', roots=[str(tmp_path)],
                                session_factory=lambda path: by_file[os.path.basename(path)])
    assert pack.files == {'detector': 'b.onnx', 'landmarks': 'c.onnx', 'recognition': 'a.onnx'}
    with pytest.raises(onnx_faces.FaceModelError, match='lacks a landmarks, recognition model'):
        onnx_faces.load_pack('pack', roots=[str(tmp_path)], session_factory=lambda _path: stub.detector)


def test_landmark_masks_are_where_the_parts_are():
    pts = _landmark_template() * 100 + 256
    masks = helper.landmark_masks(pts, 512)
    assert masks['eyes'][int(pts[36:42, 1].mean()), int(pts[36:42, 0].mean())]
    assert masks["lips"][int(pts[51, 1]) - 5, int(pts[51, 0])]
    assert not masks['lips'][int(pts[62, 1]), int(pts[62, 0])]  # the inner mouth is not lips
    assert masks['skin'][int(pts[30, 1]), int(pts[30, 0])]  # nose tip
    assert masks['brows'][int(pts[19, 1]), int(pts[19, 0])]
    assert not masks['skin'][5, 5]


def test_align_maps_template_points_and_returns_region_document(monkeypatch):
    pack = _pack([(0.95, _face_box(), KPS)])
    monkeypatch.setattr(onnx_faces, 'load_pack', lambda _name: pack)
    image = torch.rand(1, 480, 640, 3)
    hair = torch.zeros(1, 480, 640)
    hair[:, :200] = 1
    result = LF_FaceAlign().on_exec(image=[image], model_pack=['stub'], crop_size=[256], face_scale=[0.5],
                                    det_size=[DET], extra_masks=[hair], extra_ids=['hair'], node_id=['7'])
    crops, masks, metadata, image_list, mask_list = result['result']
    assert crops.shape == (1, 256, 256, 3) and len(image_list) == 1
    face = metadata['face_alignment']['faces'][0]
    np.testing.assert_allclose(face['kps_crop'], onnx_faces.crop_template(256, 0.5), atol=1e-2)
    assert [row['id'] for row in metadata['regions']] == ['skin', 'brows', 'eyes', 'lips', 'hair']
    assert masks.shape == (5, 256, 256) and len(mask_list) == 5
    sets, _ = region_mask_sets(masks, metadata)  # the downstream region nodes accept it
    assert sets.shape == (1, 5, 256, 256)
    assert metadata['mask_sets'][0]['regions'][4]['area'] > 0
    assert result['ui']['lf_output'][0]['metadata'] is metadata


def test_align_fails_loud_without_a_face(monkeypatch):
    monkeypatch.setattr(onnx_faces, 'load_pack', lambda _name: _pack([]))
    with pytest.raises(onnx_faces.FaceModelError, match=r'image 0 \(640x480\): no face found'):
        LF_FaceAlign().on_exec(image=[torch.rand(1, 480, 640, 3)], model_pack=['stub'])


def test_extra_masks_must_match_source_size_and_ids(monkeypatch):
    monkeypatch.setattr(onnx_faces, 'load_pack', lambda _name: _pack([(0.95, _face_box(), KPS)]))
    image = torch.rand(1, 480, 640, 3)
    with pytest.raises(ValueError, match='not the source size 640x480'):
        LF_FaceAlign().on_exec(image=[image], model_pack=['stub'], extra_masks=[torch.zeros(1, 10, 10)],
                               extra_ids=['hair'])
    with pytest.raises(ValueError, match='names 2 region'):
        LF_FaceAlign().on_exec(image=[image], model_pack=['stub'], extra_masks=[torch.zeros(1, 480, 640)],
                               extra_ids=['hair, hat'])


def test_identity_scores_self_one_and_reads_aligned_points(monkeypatch):
    pack = _pack([(0.95, _face_box(), KPS)])
    monkeypatch.setattr(onnx_faces, 'load_pack', lambda _name: pack)
    images = torch.rand(2, 480, 640, 3)
    crops, _, metadata, _, _ = LF_FaceAlign().on_exec(image=[images], model_pack=['stub'],
                                                      crop_size=[256])['result']
    result = LF_FaceIdentity().on_exec(image=[crops], metadata=[metadata], model_pack=['stub'],
                                       reference_index=[0], node_id=['3'])
    identity = result['result'][0]
    assert identity['schema'] == 'lf.face-identity.v1'
    assert identity['pairs'][0]['cosine'] == pytest.approx(1.0)
    assert identity['pairs'][1]['cosine'] == pytest.approx(1.0)  # stub vector differs only in scale
    assert len(identity['matrix']) == 2
    assert result['ui']['lf_output'][0]['identity'] is identity


def test_identity_rejects_foreign_metadata_and_wrong_crops(monkeypatch):
    monkeypatch.setattr(onnx_faces, 'load_pack', lambda _name: _pack([]))
    with pytest.raises(ValueError, match='must come from Face Align'):
        LF_FaceIdentity().on_exec(image=[torch.rand(1, 64, 64, 3)], metadata=[{'schema': 'x'}],
                                  model_pack=['stub'])
    metadata = {'face_alignment': {'schema': helper.ALIGNMENT_SCHEMA, 'crop_size': 256,
                                   'faces': [{'kps_crop': KPS.tolist()}]}}
    with pytest.raises(ValueError, match='not the 256x256 aligned crop'):
        LF_FaceIdentity().on_exec(image=[torch.rand(1, 64, 64, 3)], metadata=[metadata], model_pack=['stub'])


def test_published_schemas():
    assert LF_FaceAlign.INPUT_IS_LIST is True
    assert LF_FaceAlign.RETURN_NAMES == ('image', 'masks', 'metadata', 'image_list', 'mask_list')
    assert LF_FaceAlign.OUTPUT_IS_LIST == (False, False, False, True, True)
    assert LF_FaceIdentity.RETURN_NAMES == ('identity',)
    assert align_module.NODE_CLASS_MAPPINGS == {'LF_FaceAlign': LF_FaceAlign}
    assert identity_module.NODE_CLASS_MAPPINGS == {'LF_FaceIdentity': LF_FaceIdentity}
