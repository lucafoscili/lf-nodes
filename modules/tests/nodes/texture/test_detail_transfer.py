from __future__ import annotations

import json

import pytest
import torch

from modules.nodes.texture import detail_transfer as node_module
from modules.utils.helpers.torch.region_color_stats import srgb_to_lab
from modules.utils.helpers.torch.texture_maps import box_blur, detail_transfer, high_pass_spread


def _noise(seed, amplitude, height=48, width=48, base=0.5):
    noise = torch.rand(height, width, generator=torch.Generator().manual_seed(seed)) - 0.5
    return (base + noise * amplitude).clamp(0, 1)[..., None].expand(height, width, 3).clone()


def _run(image, source, **kwargs):
    values = {"radius": 3, "mode": "match_reference", "strength": 1.0, **kwargs}
    images = {name: [values.pop(name)] for name in ("mask", "reference_image", "reference_mask") if name in values}
    return node_module.LF_DetailTransfer().on_exec(
        image=[image], detail_source=[source], **images, **{name: [value] for name, value in values.items()})


def test_published_schema():
    node = node_module.LF_DetailTransfer
    inputs = node.INPUT_TYPES()
    assert list(inputs["required"]) == ["image", "detail_source", "radius", "mode", "strength"]
    assert list(inputs["optional"]) == ["mask", "reference_image", "reference_mask", "ui_widget"]
    assert inputs["required"]["mode"][0] == ["match_reference", "fixed"]
    assert node.INPUT_IS_LIST is True
    assert node.RETURN_NAMES == ("image", "report", "image_list")
    assert node.OUTPUT_IS_LIST == (False, False, True)


def test_box_blur_matches_a_direct_mean():
    channel = torch.rand(9, 11, generator=torch.Generator().manual_seed(1), dtype=torch.float64)
    blurred = box_blur(channel, 2)
    padded = torch.nn.functional.pad(channel[None, None], (2, 2, 2, 2), mode="replicate")[0, 0]
    assert blurred[4, 5] == pytest.approx(float(padded[4:9, 5:10].mean()))
    assert blurred[0, 0] == pytest.approx(float(padded[0:5, 0:5].mean()))


def test_match_reference_reaches_the_reference_detail_spread():
    flat = torch.full((48, 48, 3), 0.5)
    reference = _noise(2, 0.3)
    _, report = detail_transfer(flat, _noise(3, 0.6), torch.ones(48, 48), radius=3, mode="match_reference",
                                strength=1.0, reference=reference, reference_mask=None)
    assert report["image_fine_l_std"] == pytest.approx(0.0, abs=1e-9)
    assert report["result_fine_l_std"] == pytest.approx(report["reference_fine_l_std"], rel=0.05)
    assert 0 < report["strength"] < 1
    # Detail the image already has counts toward the target.
    _, matched = detail_transfer(reference, _noise(3, 0.6), torch.ones(48, 48), radius=3, mode="match_reference",
                                 strength=1.0, reference=reference, reference_mask=None)
    assert matched["strength"] == pytest.approx(0.0, abs=1e-9)


def test_fixed_mode_mask_and_alpha(events):
    image = torch.cat((torch.full((48, 48, 3), 0.5), torch.full((48, 48, 1), 0.25)), -1)
    mask = torch.zeros(48, 48)
    mask[:, :24] = 1
    response = _run(image[None], _noise(4, 0.4)[None], mode="fixed", strength=2.0, mask=mask[None],
                    node_id=["3"])
    result, report, image_list = response["result"]
    assert result.shape == (1, 48, 48, 4) and len(image_list) == 1
    assert torch.equal(result[0, :, 24:], image[:, 24:])
    assert torch.equal(result[0, ..., 3], image[..., 3])
    assert float((result[0, :, :24, 0] - 0.5).abs().max()) > 0.05
    row = report["images"][0]
    assert row["strength"] == 2.0 and row["reference_fine_l_std"] is None
    lightness = srgb_to_lab(result[0, ..., :3])[..., 0]
    spread, _ = high_pass_spread(lightness, mask.double(), 3)
    assert spread == pytest.approx(row["result_fine_l_std"])
    event, payload, node_id = events[0]
    assert (event, node_id) == ("detailtransfer", "3") and response["ui"]["lf_output"] == [payload]
    assert report["schema"] == "lf.detail-transfer.v1"
    json.dumps(payload, allow_nan=False)


def test_failures_are_loud():
    image = torch.full((1, 48, 48, 3), 0.5)
    source = _noise(5, 0.4)[None]
    with pytest.raises(ValueError, match="needs reference_image"):
        _run(image, source)
    with pytest.raises(ValueError, match="H,W"):
        _run(image, source[:, :24], mode="fixed")
    with pytest.raises(ValueError, match="no pixel 3 px inside"):
        small = torch.zeros(1, 48, 48)
        small[0, 10:14, 10:14] = 1
        _run(image, source, reference_image=_noise(6, 0.3)[None], reference_mask=small)
    with pytest.raises(ValueError, match="no detail finer"):
        _run(image, image, reference_image=_noise(6, 0.3)[None])
    with pytest.raises(ValueError, match="mode must be"):
        _run(image, source, mode="auto")
