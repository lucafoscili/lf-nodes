from __future__ import annotations

import json

import pytest
import torch

from modules.nodes.texture import masked_lab_grade as node_module
from modules.utils.helpers.torch.region_color_stats import lab_to_srgb, srgb_to_lab
from modules.utils.helpers.torch.texture_maps import lab_grade

SETTINGS = {"min_stretch": 0.25, "max_stretch": 1.0, "amount": 1.0, "apply_to": "mask"}


def _grade(image, mask, reference, reference_mask, **overrides):
    return node_module.LF_MaskedLabGrade().on_exec(
        image=[image], mask=[mask], reference_image=[reference], reference_mask=[reference_mask],
        **{name: [value] for name, value in {**SETTINGS, **overrides}.items()})


def _texture(seed, base, spread, height=32, width=32):
    noise = torch.rand(height, width, 3, generator=torch.Generator().manual_seed(seed)) - 0.5
    return (torch.tensor(base) + noise * spread).clamp(0, 1)


def test_published_schema():
    node = node_module.LF_MaskedLabGrade
    inputs = node.INPUT_TYPES()
    assert list(inputs["required"]) == ["image", "mask", "reference_image", "reference_mask", "min_stretch",
                                        "max_stretch", "amount", "apply_to"]
    assert inputs["required"]["apply_to"][0] == ["mask", "image"]
    assert inputs["optional"]["ui_widget"][0] == "LF_COMPARE"
    assert node.INPUT_IS_LIST is True
    assert node.RETURN_NAMES == ("image", "report", "image_list")
    assert node.OUTPUT_IS_LIST == (False, False, True)


def test_lab_round_trip():
    rgb = torch.rand(64, 3, generator=torch.Generator().manual_seed(3), dtype=torch.float64)
    torch.testing.assert_close(lab_to_srgb(srgb_to_lab(rgb)), rgb, atol=1e-9, rtol=0)


def test_region_takes_the_reference_mean_and_narrower_spread():
    image = _texture(1, [0.7, 0.4, 0.3], 0.3)
    reference = _texture(2, [0.4, 0.5, 0.6], 0.1)
    mask = torch.zeros(32, 32)
    mask[8:24, 8:24] = 1
    graded, report = lab_grade(image, mask, reference, torch.ones(32, 32), **{
        key: value for key, value in SETTINGS.items()})
    assert report["result"]["lab_mean"] == pytest.approx(report["reference"]["lab_mean"], abs=0.5)
    for after, target, reference_std in zip(report["result"]["lab_std"], report["target"]["lab_std"],
                                            report["reference"]["lab_std"]):
        assert after <= target + 1e-6
        assert after == pytest.approx(max(reference_std, 0.25 * target), rel=0.1)
    outside = mask == 0
    assert torch.equal(graded[outside], image[outside])
    assert report["changed_pixels"] == 256


def test_spread_never_widens_by_default_and_amount_blends():
    image = _texture(4, [0.5, 0.5, 0.5], 0.05)
    reference = _texture(5, [0.5, 0.5, 0.5], 0.6)
    ones = torch.ones(32, 32)
    _, report = lab_grade(image, ones, reference, ones, **SETTINGS)
    assert report["stretch"] == [1.0, 1.0, 1.0]
    half, half_report = lab_grade(image, ones, _texture(6, [0.9, 0.2, 0.2], 0.05), ones,
                                  **{**SETTINGS, "amount": 0.5})
    target, reference_mean = half_report["target"]["lab_mean"][1], half_report["reference"]["lab_mean"][1]
    assert half_report["result"]["lab_mean"][1] == pytest.approx((target + reference_mean) / 2, abs=1.0)


def test_alpha_is_kept_and_apply_to_image_grades_everything(events):
    image = torch.cat((_texture(7, [0.6, 0.6, 0.2], 0.2), torch.full((32, 32, 1), 0.3)), -1)
    mask = torch.zeros(32, 32)
    mask[:8] = 1
    response = _grade(image[None], mask[None], _texture(8, [0.2, 0.3, 0.8], 0.1)[None], torch.ones(1, 32, 32),
                      apply_to="image")
    graded, report, image_list = response["result"]
    assert graded.shape == (1, 32, 32, 4) and len(image_list) == 1
    assert torch.equal(graded[..., 3], image[None, ..., 3])
    assert report["images"][0]["changed_pixels"] == 32 * 32
    assert report["schema"] == "lf.masked-lab-grade.v1" and report["apply_to"] == "image"
    event, payload, _ = events[0]
    assert event == "maskedlabgrade" and response["ui"]["lf_output"] == [payload]
    assert payload["dataset"]["nodes"][0]["value"].startswith("Image 1 | Lab mean")
    json.dumps(payload, allow_nan=False)


def test_failures_are_loud():
    image = _texture(9, [0.5, 0.5, 0.5], 0.2)[None]
    ones = torch.ones(1, 32, 32)
    with pytest.raises(ValueError, match="mask selects no pixel"):
        _grade(image, torch.zeros(1, 32, 32), image, ones)
    with pytest.raises(ValueError, match="reference_mask selects no pixel"):
        _grade(image, ones, image, torch.zeros(1, 32, 32))
    with pytest.raises(ValueError, match="no larger than max_stretch"):
        _grade(image, ones, image, ones, min_stretch=2.0, max_stretch=1.0)
    with pytest.raises(ValueError, match="one item for all 3"):
        node_module.LF_MaskedLabGrade().on_exec(
            image=[torch.rand(3, 32, 32, 3)], mask=[ones], reference_image=[torch.rand(2, 32, 32, 3)],
            reference_mask=[ones], **{name: [value] for name, value in SETTINGS.items()})
    with pytest.raises(ValueError, match="apply_to"):
        _grade(image, ones, image, ones, apply_to="everything")
