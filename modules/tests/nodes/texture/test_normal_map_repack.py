from __future__ import annotations

import json

import pytest
import torch

from modules.nodes.texture import normal_map_repack as node_module
from modules.utils.helpers.torch.texture_maps import normal_map_repack

SETTINGS = {"layout": "xyz_rgb", "green_in": "opengl", "green_out": "opengl", "z_mode": "rebuild_z",
            "max_invalid_share": 0.01}


def _dome(size=32, length=1.0):
    """A hemisphere's tangent normals (OpenGL green), scaled to ``length``, encoded."""
    coordinates = (torch.arange(size, dtype=torch.float64) + 0.5) / size * 2 - 1
    y, x = torch.meshgrid(-coordinates, coordinates, indexing="ij")
    planar = (x ** 2 + y ** 2).clamp(max=0.81)
    scale = torch.where(x ** 2 + y ** 2 > 0.81, 0.9 / (x ** 2 + y ** 2).sqrt(), torch.ones_like(x))
    vector = torch.stack((x * scale, y * scale, (1 - planar).sqrt()), -1) * length
    return (vector * 0.5 + 0.5).float()


def _decode(image):
    return image[..., :3].double() * 2 - 1


def _run(image, **overrides):
    values = {**SETTINGS, **overrides}
    mask = values.pop("mask", None)
    return node_module.LF_NormalMapRepack().on_exec(
        image=[image], **({"mask": [mask]} if mask is not None else {}),
        **{name: [value] for name, value in values.items()})


def test_published_schema():
    node = node_module.LF_NormalMapRepack
    inputs = node.INPUT_TYPES()
    assert list(inputs["required"]) == ["image", "layout", "green_in", "green_out", "z_mode", "max_invalid_share"]
    assert inputs["required"]["green_in"][0] == ["opengl", "directx"]
    assert inputs["required"]["z_mode"][0] == ["rebuild_z", "normalize_xyz"]
    assert list(inputs["optional"]) == ["mask", "ui_widget"]
    assert node.INPUT_IS_LIST is True
    assert node.RETURN_NAMES == ("image", "report", "image_list")
    assert node.OUTPUT_IS_LIST == (False, False, True)


def test_valid_map_is_unit_length_and_green_flips():
    dome = _dome(length=0.8)
    same, report = normal_map_repack(dome, None, **{**SETTINGS, "z_mode": "normalize_xyz"})
    torch.testing.assert_close(_decode(same).norm(dim=-1), torch.ones(32, 32, dtype=torch.float64), atol=2e-3,
                               rtol=0)
    assert report["invalid_share"] == 0 and report["renormalized_share"] == 1
    assert report["stored_length"]["mean"] == pytest.approx(0.8, abs=0.01)
    flipped, flip_report = normal_map_repack(dome, None, **{**SETTINGS, "green_out": "directx"})
    assert flip_report["green_flipped"] is True
    torch.testing.assert_close(_decode(flipped)[..., 1], -_decode(dome)[..., 1], atol=2e-3, rtol=0)
    torch.testing.assert_close(_decode(flipped)[..., 0], _decode(dome)[..., 0], atol=2e-3, rtol=0)
    assert float(_decode(flipped)[..., 2].min()) > 0.4


def test_rebuild_z_ignores_the_stored_z_and_alpha_passes_through():
    dome = _dome()
    damaged = torch.cat((dome[..., :2], torch.zeros(32, 32, 1), torch.full((32, 32, 1), 0.7)), -1)
    rebuilt, report = normal_map_repack(damaged, None, **SETTINGS)
    torch.testing.assert_close(rebuilt[..., :3], dome, atol=2e-3, rtol=0)
    assert torch.equal(rebuilt[..., 3], damaged[..., 3])
    # The stored Z (0, decoding to -1) is reported but does not count against rebuild_z.
    assert report["facing_away_share"] == 1 and report["invalid_share"] == 0


def test_two_channel_swizzled_layout():
    dome = _dome()
    swizzled = torch.stack((torch.ones(32, 32), dome[..., 1], torch.zeros(32, 32), dome[..., 0]), -1)
    rebuilt, report = normal_map_repack(swizzled, None, **{**SETTINGS, "layout": "xy_ag"})
    assert rebuilt.shape == (32, 32, 3)
    torch.testing.assert_close(rebuilt, dome, atol=2e-3, rtol=0)
    assert report["layout"] == "xy_ag"


def test_node_reports_and_masks_validation(events):
    photo = torch.rand(32, 32, 3, generator=torch.Generator().manual_seed(1))
    image = _dome().clone()
    image[:, :8] = photo[:, :8] * 0.2  # (X, Y) near (-1, -1): outside the disc on the masked-out strip
    mask = torch.ones(32, 32)
    mask[:, :8] = 0
    response = _run(image[None], mask=mask[None], green_out="directx", node_id=["5"])
    repacked, report, image_list = response["result"]
    assert repacked.shape == (1, 32, 32, 3) and len(image_list) == 1
    row = report["images"][0]
    assert row["checked_pixels"] == 32 * 24 and row["invalid_share"] == 0
    assert report["schema"] == "lf.normal-map-repack.v1" and row["green_flipped"] is True
    event, payload, node_id = events[0]
    assert (event, node_id) == ("normalmaprepack", "5") and response["ui"]["lf_output"] == [payload]
    assert "green opengl -> directx" in payload["dataset"]["nodes"][0]["value"]
    json.dumps(payload, allow_nan=False)


def test_failures_are_loud():
    corner = torch.zeros(1, 16, 16, 3)
    with pytest.raises(ValueError, match="outside the unit disc"):
        _run(corner)
    with pytest.raises(ValueError, match="facing away"):
        _run(corner, z_mode="normalize_xyz")
    with pytest.raises(ValueError, match="no alpha channel"):
        _run(_dome()[None], layout="xy_ag")
    with pytest.raises(ValueError, match="stores no Z"):
        _run(torch.ones(1, 8, 8, 4) * 0.5, layout="xy_ag", z_mode="normalize_xyz")
    with pytest.raises(ValueError, match="green_in"):
        _run(_dome()[None], green_in="up")
    with pytest.raises(ValueError, match="selects no pixel"):
        _run(_dome()[None], mask=torch.zeros(1, 32, 32))
    report = _run(corner, max_invalid_share=1.0)["result"][1]
    assert report["images"][0]["invalid_share"] == 1.0
