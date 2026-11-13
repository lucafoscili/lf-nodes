"""Tone readers on synthetic images: Grade split, Luma ratio map, Tone profile, Region reads and Intrinsic layers."""
import json
import sys
import types

import numpy as np
import pytest
import torch

from modules.nodes.analytics import intrinsic_layers as intrinsic_module
from modules.nodes.analytics.grade_split import LF_GradeSplit
from modules.nodes.analytics.luma_ratio_map import LF_LumaRatioMap
from modules.nodes.analytics.region_reads import LF_RegionReads
from modules.nodes.analytics.tone_profile import LF_ToneProfile
from modules.utils.helpers.tone import parse_reads
from modules.utils.helpers.torch import intrinsic_layers as intrinsic_helper
from modules.utils.helpers.ui import generated_preview


@pytest.fixture(autouse=True)
def preview_root(monkeypatch, tmp_path):
    monkeypatch.setattr(generated_preview, "get_comfy_dir", lambda _kind: str(tmp_path / "input"))


def _scene(height=96, width=128, seed=3):
    generator = torch.Generator().manual_seed(seed)
    return torch.rand(1, height, width, 3, generator=generator) * 0.8 + 0.1


def _regions(masks, ids):
    """An lf.text-region-masks.v1 set for disjoint [R,H,W] masks."""
    rows = [{"id": name, "prompt": name, "priority": index} for index, name in enumerate(ids)]
    records = [{"id": name, "area": int(mask.sum()), "raw_area": int(mask.sum()), "empty": int(mask.sum()) == 0,
                "overlap_lost": []} for name, mask in zip(ids, masks)]
    height, width = masks.shape[-2:]
    return masks.float(), {"schema": "lf.text-region-masks.v1", "source_size": [width, height], "image_count": 1,
                           "ordering": "image-major", "regions": rows,
                           "mask_sets": [{"image_index": 0, "regions": records}]}


def _square(height, width, top, left, side):
    mask = torch.zeros(height, width, dtype=torch.bool)
    mask[top:top + side, left:left + side] = True
    return mask


def test_grade_split_schema_is_published_api():
    types_ = LF_GradeSplit.INPUT_TYPES()
    assert list(types_["required"]) == ["before", "after", "lut_size", "local_size", "local_sigma", "fine_sigma",
                                        "coarse_sigma"]
    assert LF_GradeSplit.RETURN_NAMES == ("report", "change", "left")
    assert LF_GradeSplit.RETURN_TYPES == ("JSON", "IMAGE", "IMAGE")


def test_a_pure_grade_is_explained_by_the_lookup_and_a_light_gradient_is_not():
    before = _scene()
    graded = before ** 0.8
    response = LF_GradeSplit().on_exec(before=before, after=graded)
    report, change, left = response["result"]
    assert report["schema"] == "lf.grade-split.v1"
    assert report["explained"]["grade"] > 0.97
    assert change.shape == left.shape == (1, 96, 128, 3)
    assert [row["after"] > row["before"] for row in report["tone_curve"]] == [True] * len(report["tone_curve"])
    assert response["ui"]["lf_output"][0]["report"] is report
    json.dumps(report, allow_nan=False)

    ramp = torch.linspace(0.6, 1.4, 128).view(1, 1, 128, 1)
    lit = (before * ramp).clamp(0, 1)
    report = LF_GradeSplit().on_exec(before=before, after=lit)["result"][0]
    assert report["explained"]["grade"] < 0.85
    assert report["left_bands"]["coarse"] > report["left_bands"]["fine"]


def test_grade_split_refuses_unregistered_or_identical_frames():
    before = _scene()
    with pytest.raises(ValueError, match="registered renders of the same size"):
        LF_GradeSplit().on_exec(before=before, after=_scene(height=64))
    with pytest.raises(ValueError, match="identical"):
        LF_GradeSplit().on_exec(before=before, after=before.clone())


def test_ratio_map_reports_a_lift_inside_and_outside_a_mask():
    before = torch.full((1, 64, 64, 3), 0.2)
    after = before.clone()
    after[:, :, :32] *= 1.5
    mask = torch.zeros(1, 64, 64)
    mask[:, :, :32] = 1
    report, picture = LF_LumaRatioMap().on_exec(before=before, after=after, mask=mask, sigma=0.0)["result"]
    band = next(row for row in report["bands"] if row["band"][0] <= 0.2 < row["band"][1])
    assert band["ratio_inside"] == pytest.approx(1.5, rel=1e-4)
    assert band["ratio"] == pytest.approx(1.0, abs=1e-6)
    assert 1.0 < band["ratio_frame"] < 1.5
    assert band["share"] == pytest.approx(1.0)
    assert picture.shape == (1, 64, 64, 3)
    assert float(picture[0, 0, 0, 0]) > 0.7 and float(picture[0, 0, 63, 0]) == pytest.approx(0.5)
    with pytest.raises(ValueError, match="strictly increasing"):
        LF_LumaRatioMap().on_exec(before=before, after=after, band_edges="0.5,0.1")


def test_tone_profile_reads_each_region_and_its_curve_against_a_reference():
    image = torch.full((1, 40, 40, 3), 0.25)
    image[:, :20] = 0.75
    masks, metadata = _regions(torch.stack([_square(40, 40, 0, 0, 20) | _square(40, 40, 0, 20, 20),
                                            _square(40, 40, 20, 0, 20)]), ["top", "bottom_left"])
    report = LF_ToneProfile().on_exec(image=image, masks=masks, metadata=metadata)["result"][0]
    assert report["schema"] == "lf.tone-profile.v1"
    assert report["regions"]["top"]["mean"] == pytest.approx(0.75)
    assert report["regions"]["bottom_left"]["mean"] == pytest.approx(0.25)
    assert report["regions"]["frame"]["n"] == 1600
    brighter = (image * 1.2).clamp(0, 1)
    against = LF_ToneProfile().on_exec(image=brighter, masks=masks, metadata=metadata,
                                       reference=report)["result"][0]["against_reference"]
    assert against["bottom_left"]["mean_ratio"] == pytest.approx(1.2, rel=1e-4)
    small = LF_ToneProfile().on_exec(image=image, masks=masks, metadata=metadata, min_pixels=500)["result"][0]
    assert "warning" in small["regions"]["bottom_left"]
    with pytest.raises(ValueError, match="come together"):
        LF_ToneProfile().on_exec(image=image, masks=masks)


def test_region_reads_compare_a_region_with_its_ring_and_its_outline_with_its_interior():
    image = torch.full((1, 120, 120, 3), 0.2)
    face = _square(120, 120, 40, 40, 40)
    image[0, face] = 0.6
    image[0, 40:44, 40:80] = 0.9  # a bright rim along the face's top edge
    masks, metadata = _regions(face[None], ["face"])
    reads = "lift: face / ring(face)\nrim: edge(face) & top / inside(face)"
    top, top_meta = _regions(_square(120, 120, 40, 40, 40)[None] & (torch.arange(120)[None, :, None] < 44),
                             ["top"])
    response = LF_RegionReads().on_exec(image=image, masks=masks, metadata=metadata, masks_2=top,
                                        metadata_2=top_meta, reads=reads, edge_px=4, inside_px=4, min_pixels=100)
    report, preview, previews = response["result"]
    lift, rim = report["reads"]
    assert lift["luma_ratio"] > 2.5
    assert rim["a"]["luma"] == pytest.approx(0.9, rel=1e-3)
    assert rim["luma_ratio"] == pytest.approx(1.5, rel=1e-3)
    assert len(previews) == 2 and preview.shape[0] == 2
    json.dumps(report, allow_nan=False)


def test_region_reads_take_a_facing_map_and_fail_loud_on_bad_lines():
    image = torch.full((1, 32, 32, 3), 0.5)
    image[:, :, :8] = 0.25
    facing = torch.ones(1, 32, 32, 3)
    facing[:, :, :8] = 0.1
    masks, metadata = _regions(torch.ones(1, 32, 32, dtype=torch.bool), ["skin"])
    report = LF_RegionReads().on_exec(image=image, masks=masks, metadata=metadata, facing=facing,
                                      reads="skin & facing<0.3 / skin & facing>0.7")["result"][0]
    assert report["reads"][0]["luma_ratio"] == pytest.approx(0.5, rel=1e-4)
    with pytest.raises(ValueError, match="facing map"):
        LF_RegionReads().on_exec(image=image, masks=masks, metadata=metadata, reads="facing<0.3 / skin")
    with pytest.raises(ValueError, match="no region named 'hair'"):
        LF_RegionReads().on_exec(image=image, masks=masks, metadata=metadata, reads="hair / skin")
    with pytest.raises(ValueError, match="exactly one"):
        parse_reads("a / b / c")
    with pytest.raises(ValueError, match="alternate"):
        parse_reads("a & / b")


def test_intrinsic_releases_need_all_five_stages(tmp_path):
    complete, partial = tmp_path / "complete", tmp_path / "partial"
    complete.mkdir()
    partial.mkdir()
    for stage in range(5):
        (complete / f"stage_{stage}_v21.pt").write_bytes(b"")
    (partial / "stage_0.pt").write_bytes(b"")
    assert intrinsic_helper.available_releases([str(complete), str(partial)]) == ["v21"]
    assert intrinsic_helper.available_releases([str(partial)]) == ["none found"]
    with pytest.raises(FileNotFoundError, match="stage_0..stage_4"):
        intrinsic_helper.stage_paths("v2", [str(partial)])


def test_intrinsic_layers_come_back_at_the_source_size(monkeypatch):
    calls = {}

    def run_pipeline(models, image, resize_conf, base_size, device):
        calls.update(models=models, shape=image.shape, resize_conf=resize_conf, device=device)
        small = np.full((32, 48, 3), 0.25, np.float32)
        return {"image": small, "hr_alb": small, "dif_shd": small[..., 0] * 2, "residual": small - 0.25,
                "lin_img": small}

    pipeline = types.ModuleType("intrinsic.pipeline")
    pipeline.run_pipeline = run_pipeline
    monkeypatch.setitem(sys.modules, "intrinsic", types.ModuleType("intrinsic"))
    monkeypatch.setitem(sys.modules, "intrinsic.pipeline", pipeline)
    monkeypatch.setattr(intrinsic_helper, "load_release", lambda release, device: {"release": release})
    image = torch.full((1, 64, 96, 3), 0.5)
    result = intrinsic_module.LF_IntrinsicLayers().on_exec(image=image, release="v21", resize_conf=0.0)["result"]
    albedo, shading, residual, report = result[:4]
    assert albedo.shape == shading.shape == residual.shape == (1, 64, 96, 3)
    assert float(shading.mean()) == pytest.approx(0.5)
    assert report["worked_at"] == [48, 32] and report["size"] == [96, 64]
    assert calls["shape"] == (64, 96, 3) and calls["models"] == {"release": "v21"}
    with pytest.raises(ValueError, match="no intrinsic release"):
        intrinsic_module.LF_IntrinsicLayers().on_exec(image=image, release="none found")


def test_intrinsic_loading_refuses_a_console_prompt_instead_of_hanging():
    import builtins

    original = builtins.input
    with pytest.raises(RuntimeError, match="trusted_list"):
        with intrinsic_helper._no_console_prompts():
            input("Do you trust this repository (y/N)?")
    assert builtins.input is original


def test_tone_profile_labels_a_black_region():
    image = torch.full((1, 40, 40, 3), 0.5)
    image[:, 20:] = 0.0
    masks, metadata = _regions(_square(40, 40, 20, 0, 20)[None], ["night"])
    response = LF_ToneProfile().on_exec(image=image, masks=masks, metadata=metadata)
    night = response["result"][0]["regions"]["night"]
    assert night["fill"] is None and night["sheen"] is None
    assert "fill n/a" in response["ui"]["lf_output"][0]["dataset"]["nodes"][1]["value"]


def test_a_read_function_takes_a_union_of_regions():
    image = torch.full((1, 120, 120, 3), 0.2)
    image[0, :, :20] = 0.8  # far from both squares: outside every ring
    masks, metadata = _regions(torch.stack([_square(120, 120, 40, 30, 20), _square(120, 120, 40, 70, 20)]),
                               ["left", "right"])
    assert parse_reads("x: ring( left | right ) / left")[0]["a"] == [("func", "ring", "left|right")]
    report = LF_RegionReads().on_exec(image=image, masks=masks, metadata=metadata, ring_inner=2, ring_outer=6,
                                      min_pixels=10, reads="both: ring(left|right) / ring(left)")["result"][0]
    both = report["reads"][0]
    assert both["a"]["n"] > both["b"]["n"]
    assert both["a"]["luma"] == pytest.approx(0.2)
