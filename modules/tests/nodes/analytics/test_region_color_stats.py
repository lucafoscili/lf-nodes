from __future__ import annotations

import copy
import json
from urllib.parse import parse_qs, urlsplit

from PIL import Image
import pytest
import torch

from modules.nodes.analytics import region_color_stats as node_module
from modules.utils.helpers.torch.region_color_stats import (
    ciede2000, luminance_banding, luminance_row_profile, srgb_to_lab,
)
from modules.utils.helpers.ui import generated_preview


@pytest.fixture(autouse=True)
def preview_root(monkeypatch, tmp_path):
    root = tmp_path / "input"
    monkeypatch.setattr(generated_preview, "get_comfy_dir", lambda _kind: str(root))
    return root


def _metadata(masks):
    while isinstance(masks, (list, tuple)):
        masks = masks[0]
    if masks.ndim == 3:
        masks = masks.unsqueeze(0)
    count, regions, height, width = masks.shape
    definitions = [{"id": f"region_{i}", "prompt": f"region {i}", "priority": i}
                   for i in range(regions)]
    sets = []
    for image_index, image_masks in enumerate(masks):
        rows = []
        for definition, mask in zip(definitions, image_masks):
            area = int((mask > 0.5).sum())
            rows.append({"id": definition["id"], "area": area, "raw_area": area,
                         "empty": area == 0, "overlap_lost": []})
        sets.append({"image_index": image_index, "regions": rows})
    return {"schema": "lf.text-region-masks.v1", "source_size": [width, height],
            "image_count": count, "ordering": "image-major", "regions": definitions, "mask_sets": sets}


def _measure(a, b, masks, metadata=None, **kwargs):
    return node_module.LF_RegionColorStats().on_exec(
        image_a=a, image_b=b, masks=masks,
        metadata=_metadata(masks) if metadata is None else metadata, **kwargs)


def _split_masks(height=16, width=24):
    masks = torch.zeros(3, height, width)
    masks[0, :, :width // 3] = 1
    masks[1, :, width // 3:2 * width // 3] = 1
    masks[2, :, 2 * width // 3:] = 1
    return masks


def test_identical_images_have_exact_zero_deltas_and_matched_distances():
    a = torch.rand(1, 16, 24, 3, generator=torch.Generator().manual_seed(4))
    response = _measure([a], [a.clone()], [_split_masks()])
    stats, overlay, overlay_list = response["result"]
    assert stats["schema"] == "lf.region-color-stats.v1"
    assert stats["mask_mode"] == "shared"
    assert overlay.shape == (1, 16, 56, 3)
    assert len(overlay_list) == 1 and torch.equal(overlay_list[0], overlay)
    for row in stats["regions"]:
        assert row["delta_b_minus_a"] == {"lab_mean": [0.0] * 3, "lab_median": [0.0] * 3}
        assert row["ciede2000"] == {"mean": 0.0, "p10": 0.0, "p50": 0.0, "p90": 0.0}
        assert row["matched_count"] == row["intersection_count"] == 128
    json.dumps(stats, allow_nan=False)


def test_region_color_and_darkening_changes_are_local():
    a = torch.full((1, 16, 24, 3), 0.5)
    b = a.clone()
    b[:, :, :8, 0] = 0.8
    b[:, :, 8:16, :] = 0.25
    stats = _measure(a, b, _split_masks())["result"][0]
    red, dark, unchanged = stats["regions"]
    assert red["delta_b_minus_a"]["lab_mean"][1] > 20
    assert abs(dark["delta_b_minus_a"]["lab_mean"][1]) < 0.001
    assert dark["delta_b_minus_a"]["lab_mean"][0] < -20
    assert unchanged["delta_b_minus_a"]["lab_mean"] == [0.0] * 3
    assert unchanged["ciede2000"]["mean"] == 0
    assert red["ciede2000"]["mean"] > 0 and dark["ciede2000"]["mean"] > 0


def test_decoded_srgb_lab_reference_values_and_float_precision():
    lab = srgb_to_lab(torch.tensor([[0., 0., 0.], [1., 1., 1.],
                                     [1., 0., 0.], [0.5, 0.5, 0.5]], dtype=torch.float64))
    torch.testing.assert_close(lab[0], torch.zeros(3, dtype=torch.float64), atol=1e-9, rtol=0)
    assert lab[1, 0] == pytest.approx(100, abs=1e-4)
    assert lab[2].tolist() == pytest.approx([53.2408, 80.0925, 67.2032], abs=0.001)
    assert lab[3, 0] == pytest.approx(53.3890, abs=0.001)
    # A sub-8-bit input change must survive measurement, not quantize away.
    a = torch.full((1, 8, 8, 3), 0.5, dtype=torch.float64)
    b = a + 0.0001
    row = _measure(a, b, torch.ones(1, 8, 8))["result"][0]["regions"][0]
    assert row["delta_b_minus_a"]["lab_mean"][0] > 0


@pytest.mark.parametrize("left,right,expected", [
    ([50, 2.6772, -79.7751], [50, 0, -82.7485], 2.0425),
    ([50, 3.1571, -77.2803], [50, 0, -82.7485], 2.8615),
    ([50, 2.8361, -74.0200], [50, 0, -82.7485], 3.4412),
    ([50, -1.3802, -84.2814], [50, 0, -82.7485], 1.0000),
    ([50, 0, 0], [50, -1, 2], 2.3669),
    ([50, 2.49, -0.001], [50, -2.49, 0.0011], 7.2195),
])
def test_ciede2000_published_sharma_reference_pairs(left, right, expected):
    # Sharma, Wu & Dalal supplementary test data, Color Res. Appl. 30 (2005).
    left, right = torch.tensor(left, dtype=torch.float64), torch.tensor(right, dtype=torch.float64)
    assert float(ciede2000(left, right)) == pytest.approx(expected, abs=0.0001)
    assert float(ciede2000(right, left)) == pytest.approx(expected, abs=0.0001)


def test_quantized_gradient_flags_banding_while_smooth_gradient_does_not():
    smooth = torch.linspace(0.1, 0.9, 512).view(1, 1, 512, 1).expand(1, 24, 512, 3).clone()
    quantized = (smooth * 15).round() / 15
    stats = _measure(smooth, quantized, torch.ones(1, 24, 512))["result"][0]
    a, b = stats["regions"][0]["a"]["banding"], stats["regions"][0]["b"]["banding"]
    assert a["eligible"] and not a["suspected"]
    assert b["eligible"] and b["suspected"]
    assert b["empty_bin_fraction"] > a["empty_bin_fraction"]
    checker = (torch.arange(24)[:, None] + torch.arange(512)[None, :]) % 2 * 80.0
    texture = luminance_banding(checker.double(), torch.ones(24, 512, dtype=torch.bool))
    assert not texture["eligible"] and not texture["suspected"]


def test_row_profile_finds_a_band_that_the_region_mean_cancels():
    # A smooth downward gradient against the same rows stepping up at row 20, with the rows above darkened
    # so the region's mean does not move.
    rows = torch.linspace(40, 44, 60, dtype=torch.float64)[:, None].expand(60, 90).clone()
    banded = rows.clone()
    banded[20:] += 1
    banded[:20] -= 2
    assert abs(float(banded.mean() - rows.mean())) < 0.01
    # Ten unmasked rows above and below keep the region off the image border, which the profile skips.
    rows, banded = (torch.nn.functional.pad(image, (0, 0, 10, 10)) for image in (rows, banded))
    mask = torch.zeros(80, 90, dtype=torch.bool)
    mask[10:70] = True
    smooth, band = luminance_row_profile(rows, mask), luminance_row_profile(banded, mask)
    assert abs(smooth["max_step_l"]) < 0.5
    assert band["max_step_l"] > 0.5 and band["step_row"] == 30
    assert band["rows"] == smooth["rows"] == 60


def test_row_profile_skips_narrow_rows_and_needs_two_windows():
    luminance = torch.full((32, 50), 50.0, dtype=torch.float64)
    mask = torch.zeros(32, 50, dtype=torch.bool)  # rows 10-21: clear of the 10-row image border
    mask[10:19, :] = True
    mask[19:22, :39] = True  # rows under ROW_PROFILE_MINIMUM_ROW_PIXELS do not count
    profile = luminance_row_profile(luminance, mask)
    assert profile["rows"] == 9 and profile["max_step_l"] is None and profile["step_row"] is None
    mask[10:20, :] = True
    profile = luminance_row_profile(luminance, mask)
    assert profile["rows"] == 10 and profile["max_step_l"] == 0.0


def test_region_rows_report_standard_deviation_and_row_profile():
    a = torch.full((1, 60, 48, 3), 0.4)
    row = _measure(a, a.clone(), torch.ones(1, 60, 48))["result"][0]["regions"][0]
    assert row["a"]["lab_std"] == pytest.approx([0.0, 0.0, 0.0], abs=1e-9)
    assert row["a"]["row_profile"]["max_step_l"] == pytest.approx(0.0, abs=1e-9)
    stats = _measure(a, a.clone(), torch.ones(1, 60, 48))["result"][0]
    assert stats["row_profile_method"]["window_rows"] == 5
    assert stats["row_profile_method"]["border_rows"] == 10


@pytest.mark.parametrize("a,b,match", [
    (torch.zeros(2, 8, 8, 3), torch.zeros(1, 8, 8, 3), "exactly one image"),
    (torch.zeros(1, 8, 8, 3), torch.zeros(1, 8, 9, 3), "same H,W"),
    (torch.zeros(1, 8, 8, 1), torch.zeros(1, 8, 8, 3), "RGB or RGBA"),
    (torch.full((1, 8, 8, 3), float("nan")), torch.zeros(1, 8, 8, 3), "finite"),
])
def test_invalid_image_cardinality_geometry_and_pixels_fail(a, b, match):
    with pytest.raises(ValueError, match=match):
        _measure(a, b, torch.ones(1, 8, 8))


def test_mask_metadata_geometry_count_order_and_area_mismatches_fail():
    masks = _split_masks()
    a = torch.zeros(1, 16, 24, 3)
    for mutation in ("size", "count", "order", "area"):
        document = copy.deepcopy(_metadata(masks))
        if mutation == "size":
            document["source_size"] = [25, 16]
        elif mutation == "count":
            document["regions"].pop()
        elif mutation == "order":
            document["mask_sets"][0]["regions"].reverse()
        else:
            document["mask_sets"][0]["regions"][0]["area"] += 1
        with pytest.raises(ValueError):
            _measure(a, a, masks, document)
    with pytest.raises(ValueError, match="H,W"):
        _measure(torch.zeros(1, 20, 24, 3), torch.zeros(1, 20, 24, 3), masks)


def test_per_image_areas_empty_regions_and_no_intersection_are_explicit(caplog):
    a = torch.full((1, 8, 8, 3), 0.4)
    masks = torch.zeros(2, 3, 8, 8)
    masks[0, 0, :2, :] = 1
    masks[1, 0, 5:, :] = 1
    masks[0, 1, 6:, :] = 1
    masks[:, 2, 3:5, :] = 1
    document = _metadata(masks)
    response = _measure(a, a, masks.flatten(0, 1), [document])
    stats = response["result"][0]
    disjoint, empty, same = stats["regions"]
    assert stats["mask_mode"] == "per_image"
    assert disjoint["a"]["area"] == 16 and disjoint["b"]["area"] == 24
    assert disjoint["matched_count"] == 0 and disjoint["ciede2000"] is None
    assert disjoint["warnings"]
    assert empty["b"]["empty"] and empty["b"]["lab_mean"] is None
    assert empty["delta_b_minus_a"]["lab_median"] is None
    assert same["matched_count"] == 16 and same["ciede2000"]["mean"] == 0
    assert "No same-coordinate mask intersection" in caplog.text
    payload = response['ui']['lf_output'][0]
    assert 'DE00 N/A' in payload['dataset']['nodes'][1]['value']
    assert set(payload) == {'dataset', 'stats'}
    json.dumps(stats, allow_nan=False)


def test_three_mask_sets_are_rejected_and_missing_inputs_are_named():
    a = torch.zeros(1, 8, 8, 3)
    masks = torch.ones(3, 1, 8, 8)
    with pytest.raises(ValueError, match="one shared set or exactly two"):
        _measure(a, a, masks.flatten(0, 1), _metadata(masks))
    with pytest.raises(ValueError, match="image_a requires exactly one image"):
        node_module.LF_RegionColorStats().on_exec()


def test_two_separate_metadata_documents_preserve_a_b_pairing():
    a = torch.full((1, 8, 8, 3), 0.3)
    masks_a = torch.zeros(1, 8, 8)
    masks_b = torch.zeros(1, 8, 8)
    masks_a[:, :, :4] = 1
    masks_b[:, :, :6] = 1
    response = _measure(a, a, [masks_a, masks_b], [_metadata(masks_a), _metadata(masks_b)])
    row = response["result"][0]["regions"][0]
    assert row["a"]["area"] == 32 and row["b"]["area"] == 48
    assert row["matched_count"] == 32


def test_ciede_sampling_is_bounded_coordinate_matched_and_deterministic():
    a = torch.full((1, 260, 260, 3), 0.3)
    b = a.clone()
    b[:, :130, :, 0] += 0.05
    masks = torch.ones(1, 260, 260)
    one = _measure(a, b, masks)["result"][0]
    two = _measure(a, b, masks)["result"][0]
    row = one["regions"][0]
    assert row["intersection_count"] == 67600 and row["matched_count"] == 65536
    assert row["ciede2000"] == two["regions"][0]["ciede2000"]
    assert row["ciede2000"]["p10"] == 0 and row["ciede2000"]["p90"] > 0


def test_headless_event_history_preview_persistence_and_rgba(preview_root, monkeypatch):
    sent = []
    monkeypatch.setattr(node_module, "safe_send_sync", lambda *args: sent.append(args))
    a = torch.full((1, 8, 8, 4), 0.25)
    b = torch.full((1, 8, 8, 3), 0.5)
    masks = torch.zeros(1, 8, 8)
    masks[:, 1:7, 1:7] = 1
    response = _measure([a], [b], [masks], [_metadata(masks)], node_id=["node-7"])
    stats, overlay, _ = response["result"]
    payload = response["ui"]["lf_output"][0]
    assert sent == [("regioncolorstats", payload, ["node-7"])]
    assert payload["stats"] == stats
    region_node = payload['dataset']['nodes'][1]
    assert 'region_0 | DE00 ' in region_node['value']
    assert 'Lab A [' in region_node['value'] and ' B [' in region_node['value']
    assert '| B-A [' in region_node['value']
    assert region_node['cells']['lfImage']['value'] == region_node['value'] + ' (before)'
    assert region_node['cells']['lfImage_after']['value'] == region_node['value'] + ' (after)'
    assert overlay.shape == (1, 8, 24, 4)
    torch.testing.assert_close(overlay[:, :, :8, 3], a[..., 3])
    assert torch.equal(overlay[0, 3, 3, :3], a[0, 3, 3, :3])
    assert not torch.equal(overlay[0, 1, 1, :3], a[0, 1, 1, :3])
    cells = [cell for node in payload['dataset']['nodes'] for cell in node['cells'].values()]
    saved = []
    for cell in cells:
        query = parse_qs(urlsplit(cell["lfValue"]).query)
        assert query["type"] == ["input"]
        assert "nonce" not in query and "base64" not in cell["lfValue"]
        path = preview_root / query["subfolder"][0] / query["filename"][0]
        saved.append((path, path.read_bytes(), path.stat().st_mtime_ns))
        with Image.open(path) as image:
            assert image.width <= 512 and image.height <= 512
    replay = json.loads(json.dumps(payload))
    assert replay == payload
    _measure([a], [b], [masks], [_metadata(masks)])
    assert all(path.read_bytes() == contents and path.stat().st_mtime_ns == modified
               for path, contents, modified in saved)


def test_public_schema_is_exact_single_pair_and_optional_compare():
    cls = node_module.LF_RegionColorStats
    schema = cls.INPUT_TYPES()
    assert set(schema["required"]) == {"image_a", "image_b", "masks", "metadata"}
    assert schema["optional"]["ui_widget"][0] == "LF_COMPARE"
    assert schema["hidden"] == {"node_id": "UNIQUE_ID"}
    assert cls.INPUT_IS_LIST is True
    assert cls.RETURN_TYPES == ("JSON", "IMAGE", "IMAGE")
    assert cls.RETURN_NAMES == ("stats", "overlay", "overlay_list")
    assert cls.OUTPUT_IS_LIST == (False, False, True)


def test_row_profile_skips_rows_at_the_image_border():
    # A smooth region that runs off the bottom of the frame, whose last rows are bright (the cut).
    luminance = torch.full((100, 64), 50.0)
    luminance[95:] = 90.0
    mask = torch.zeros((100, 64), dtype=torch.bool)
    mask[40:] = True
    profile = luminance_row_profile(luminance, mask)
    assert profile["max_step_l"] == pytest.approx(0.0, abs=1e-9)
    assert profile["rows"] == 50
