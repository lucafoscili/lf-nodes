"""Region measure on synthetic frames: named boxes across frames, a mask, labels, the overlay and failures."""
import pytest
import torch

from modules.nodes.analytics.region_measure import LF_RegionMeasure, region_measure
from modules.utils.helpers.ui import generated_preview


@pytest.fixture(autouse=True)
def preview_root(monkeypatch, tmp_path):
    monkeypatch.setattr(generated_preview, "get_comfy_dir", lambda _kind: str(tmp_path / "input"))


def _frame(value, height=12, width=16):
    return torch.full((1, height, width, 3), value)


def test_each_frame_reads_each_named_box():
    left = _frame(0.2)
    left[:, :, 8:, :] = 0.6
    report, overlays = region_measure([left, _frame(0.4)], boxes="left=0,0,8,12\nright=8,0,16,12", labels="a,b")
    first, second = report["frames"]
    assert first["label"] == "a" and second["label"] == "b"
    assert first["regions"]["left"]["mean"] == pytest.approx(0.2)
    assert first["regions"]["right"]["mean"] == pytest.approx(0.6)
    assert first["regions"]["left"]["n"] == 96
    assert first["regions"]["left"]["rgb_mean"] == pytest.approx([0.2, 0.2, 0.2])
    assert second["regions"]["right"]["mean"] == pytest.approx(0.4)
    assert report["regions"] == ["left", "right"]
    assert len(overlays) == 2 and overlays[0].shape == (1, 12, 16, 3)
    # The box's outline is drawn on the overlay, the frame itself is untouched.
    assert not torch.equal(overlays[0], left)


def test_no_box_reads_the_whole_frame():
    report, _ = region_measure([_frame(0.5)])
    assert list(report["frames"][0]["regions"]) == ["frame"]
    assert report["frames"][0]["regions"]["frame"]["n"] == 192


def test_a_mask_narrows_every_box():
    mask = torch.zeros(1, 12, 16)
    mask[:, :6, :] = 1
    report, _ = region_measure([_frame(0.5)], boxes="all=0,0,16,12", mask=mask)
    assert report["frames"][0]["regions"]["all"]["n"] == 96


def test_a_region_without_pixels_is_refused_by_name():
    mask = torch.zeros(1, 12, 16)
    mask[:, :, :4] = 1
    with pytest.raises(ValueError, match=r"frame 0 \(f0\): region right holds no pixels"):
        region_measure([_frame(0.5)], boxes="right=8,0,16,12", mask=mask, labels="f0")


def test_a_box_outside_a_frame_is_refused():
    with pytest.raises(ValueError, match=r"frame 1: box wide .* outside the 8x12 image"):
        region_measure([_frame(0.5), _frame(0.5, width=8)], boxes="wide=0,0,16,12")


def test_labels_must_match_the_frames():
    with pytest.raises(ValueError, match="labels name 1 frames, not 2"):
        region_measure([_frame(0.5), _frame(0.5)], labels="one")


def test_masks_must_be_one_or_one_per_frame():
    with pytest.raises(ValueError, match="mask holds 2 masks for 3 frames"):
        region_measure([_frame(0.5)] * 3, mask=torch.ones(2, 12, 16))


def test_node_returns_report_and_overlays():
    out = LF_RegionMeasure().on_exec(image=[_frame(0.5)], boxes=["a=0,0,4,4"], labels=[""], node_id=["3"])
    report, overlay, overlay_list = out["result"]
    assert report["schema"] == "lf.region-measure.v1"
    assert overlay.shape == (1, 12, 16, 3) and len(overlay_list) == 1
    assert out["ui"]["lf_output"][0]["dataset"]["nodes"]
