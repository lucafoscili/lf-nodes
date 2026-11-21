"""Image diff on synthetic images: exact numbers, the changed box, pair policy, regions and failures."""
import pytest
import torch

from modules.nodes.analytics.image_diff import LF_ImageDiff, image_diff
from modules.utils.helpers.tone.boxes import parse_boxes
from modules.utils.helpers.ui import generated_preview


@pytest.fixture(autouse=True)
def preview_root(monkeypatch, tmp_path):
    monkeypatch.setattr(generated_preview, "get_comfy_dir", lambda _kind: str(tmp_path / "input"))


def _flat(height=16, width=20, value=0.25):
    return torch.full((1, height, width, 3), value)


def _patched(height=16, width=20, value=0.25, box=(4, 2, 8, 6), patch=0.75):
    image = _flat(height, width, value)
    x0, y0, x1, y1 = box
    image[:, y0:y1, x0:x1, :] = patch
    return image


def test_identical_images_read_zero_with_no_changed_box():
    report, heat = image_diff([_flat()], [_flat()])
    pair = report["pairs"][0]
    assert pair["max"] == 0 and pair["mean"] == 0 and pair["changed_share"] == 0
    assert pair["changed_box"] is None
    assert heat[0].shape == (1, 16, 20, 3)


def test_a_patch_reads_its_levels_share_and_exclusive_box():
    report, _ = image_diff([_flat()], [_patched()], threshold=2)
    pair = report["pairs"][0]
    assert pair["max"] == pytest.approx(127.5)
    assert pair["changed_pixels"] == 16
    assert pair["changed_share"] == pytest.approx(16 / 320)
    assert pair["changed_box"] == [4, 2, 8, 6]
    assert pair["luma_delta"] == pytest.approx(127.5 * 16 / 320)
    assert report["scale_levels"] == pytest.approx(127.5)


def test_a_box_keeps_only_its_pixels():
    report, _ = image_diff([_flat()], [_patched()], box="10,0,20,16")
    pair = report["pairs"][0]
    assert pair["pixels"] == 160 and pair["max"] == 0 and pair["changed_box"] is None
    assert pair["box"] == [10, 0, 20, 16]


def test_one_reference_broadcasts_over_many_and_labels_name_the_pairs():
    report, heat = image_diff([_flat()], [_flat(), _patched()], labels="same,patched")
    assert [pair["label"] for pair in report["pairs"]] == ["same", "patched"]
    assert len(heat) == 2 and report["pairs"][1]["changed_pixels"] == 16


def test_sizes_that_differ_are_named():
    with pytest.raises(ValueError, match=r"pair 0: image_a is 20x16 and image_b is 21x16"):
        image_diff([_flat()], [_flat(width=21)])


def test_counts_that_do_not_pair_are_refused():
    with pytest.raises(ValueError, match="2 images in image_a and 3 in image_b"):
        image_diff([_flat(), _flat()], [_flat(), _flat(), _flat()])


def test_labels_must_match_the_pairs():
    with pytest.raises(ValueError, match="labels name 1 pairs, not 2"):
        image_diff([_flat()], [_flat(), _flat()], labels="one")


def test_empty_and_outside_boxes_are_refused():
    with pytest.raises(ValueError, match="empty"):
        image_diff([_flat()], [_flat()], box="4,4,4,8")
    with pytest.raises(ValueError, match="outside the 20x16 image"):
        image_diff([_flat()], [_flat()], box="0,0,21,16")


def test_a_mask_without_pixels_in_the_region_is_refused():
    with pytest.raises(ValueError, match="no pixels"):
        image_diff([_flat()], [_flat()], mask=torch.zeros(1, 16, 20))


def test_parse_boxes_names_and_refuses_bad_text():
    assert parse_boxes("face=1,2,3,4\n5,6,7,8") == [("face", (1, 2, 3, 4)), ("box2", (5, 6, 7, 8))]
    assert parse_boxes("  ") == []
    with pytest.raises(ValueError, match="x0,y0,x1,y1"):
        parse_boxes("face=1,2,3")
    with pytest.raises(ValueError, match="twice"):
        parse_boxes("a=0,0,1,1;a=0,0,2,2")


def test_node_returns_heat_list_report_and_compare_payload():
    sent = []
    node = LF_ImageDiff()
    import modules.nodes.analytics.image_diff as module

    original = module.safe_send_sync
    module.safe_send_sync = lambda event, payload, node_id: sent.append((event, payload))
    try:
        out = node.on_exec(image_a=[_flat()], image_b=[_patched()], threshold=[2.0], heat_max=[0.0], box=[""],
                           labels=[""], node_id=["7"])
    finally:
        module.safe_send_sync = original
    heat, heat_list, report = out["result"]
    assert heat.shape == (1, 16, 20, 3) and len(heat_list) == 1
    assert report["schema"] == "lf.image-diff.v1"
    assert sent and sent[0][0] == "imagediff" and sent[0][1]["dataset"]["nodes"]
