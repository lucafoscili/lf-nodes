"""Face Zones on the stub InsightFace pack of the Face Align tests: no weights, no faces."""
import numpy as np
import pytest
import torch

from modules.nodes.regions import face_zones as zones_module
from modules.nodes.regions.face_zones import LF_FaceZones
from modules.tests.nodes.regions.test_face_align import _face_box, _landmark_template, _pack, KPS
from modules.utils.helpers.detection.region_masks import region_mask_sets
from modules.utils.helpers.face import face_zones as helper
from modules.utils.helpers.face import insightface_onnx as onnx_faces
from modules.utils.helpers.ui import generated_preview


@pytest.fixture(autouse=True)
def preview_root(monkeypatch, tmp_path):
    monkeypatch.setattr(generated_preview, 'get_comfy_dir', lambda _kind: str(tmp_path / 'input'))


def _landmarks(scale=120.0, centre=(200.0, 200.0)):
    return _landmark_template() * scale + np.array(centre)


def test_zones_sit_where_they_are_named():
    pts = _landmarks()
    zones = helper.zone_masks(pts, (400, 400))
    rows = {key: np.nonzero(mask)[0] for key, mask in zones.items()}
    assert all(mask.any() for mask in zones.values())
    lids = pts[[40, 41, 46, 47], 1].mean()
    assert rows['under_eyes'].min() > lids and rows['cheeks'].min() > rows['under_eyes'].max()
    assert rows['forehead'].max() < pts[17:27, 1].min()
    assert rows['chin'].min() > pts[57, 1]


def test_zones_follow_the_face_in_scale():
    small = helper.zone_masks(_landmarks(scale=60.0), (400, 400))
    large = helper.zone_masks(_landmarks(scale=120.0), (400, 400))
    for key in ('under_eyes', 'cheeks', 'forehead'):
        assert large[key].sum() / small[key].sum() == pytest.approx(4, rel=0.25)


def test_a_turned_face_keeps_its_zone_height_and_drops_its_far_side():
    pts = _landmarks()
    frontal = helper.zone_masks(pts, (400, 400))
    turned = pts.copy()
    nose = pts[30, 0]
    turned[:, 0] = nose + (pts[:, 0] - nose) * np.where(pts[:, 0] > nose, 0.2, 0.9)  # the right side turns away
    zones = helper.zone_masks(turned, (400, 400))
    height = np.linalg.norm(pts[8] - pts[27])
    iods = [np.linalg.norm(p[36:42].mean(0) - p[42:48].mean(0)) for p in (pts, turned)]
    assert iods[1] < helper.HEIGHT_UNIT * height < iods[0]  # the turned face's unit comes from its height

    def rows(mask):
        return np.ptp(np.nonzero(mask)[0])

    assert rows(zones['forehead']) == pytest.approx(rows(frontal['forehead']) * helper.HEIGHT_UNIT * height / iods[0],
                                                    rel=0.15)
    columns = np.nonzero(zones['under_eyes'])[1]
    assert columns.max() < nose and zones['cheeks'].sum() < frontal['cheeks'].sum()


def test_a_too_small_face_fails_loud():
    with pytest.raises(ValueError, match='too small'):
        helper.zone_masks(_landmarks(scale=1.0), (400, 400))


def test_node_returns_disjoint_zones_with_metadata(monkeypatch):
    pack = _pack([(0.9, _face_box(), KPS)])
    monkeypatch.setattr(onnx_faces, 'load_pack', lambda name, roots=None, session_factory=None: pack)
    monkeypatch.setattr(zones_module, 'available_packs', lambda: ['stub'])
    image = torch.full((1, 480, 640, 3), 0.5)
    response = LF_FaceZones().on_exec(image=image, model_pack='stub', det_size=640)
    masks, document, overlay = response['result']
    tensor, checked = region_mask_sets(masks, document)
    assert [row['id'] for row in checked['regions']] == ['under_eyes', 'cheeks', 'folds', 'forehead', 'chin']
    assert tensor.shape == (1, 5, 480, 640)
    assert document['face_zones']['faces_found'] == 1 and len(document['face_zones']['landmarks']) == 68
    assert overlay.shape == (1, 480, 640, 3)
    assert response['ui']['lf_output'][0]['metadata'] is document
