from __future__ import annotations

from types import SimpleNamespace

import pytest
import torch

from modules.nodes.regions import region_mask


def _metadata(region_id: str, fill: float) -> dict:
    region = {"id": region_id, "fill": fill, "x": 0, "y": 0, "w": 2, "h": 2}
    return {"regions": [region], "selected_region": region}


def test_region_metadata_pairs_broadcasts_and_rejects_mismatch() -> None:
    assert region_mask.LF_RegionMask.RETURN_TYPES == (
        "MASK",
        "MASK",
        "REGION_META",
        "REGION_META",
    )
    assert region_mask.LF_RegionMask.RETURN_NAMES == (
        "mask",
        "mask_list",
        "region",
        "region_list",
    )
    assert region_mask.LF_RegionMask.OUTPUT_IS_LIST == (
        False,
        True,
        False,
        True,
    )
    first = _metadata("first", 0.25)
    second = _metadata("second", 0.75)

    assert region_mask._region_metadata_for_images(first, 2) == [first, first]
    assert region_mask._region_metadata_for_images([first], 2) == [first, first]
    assert region_mask._region_metadata_for_images([first, second], 2) == [
        first,
        second,
    ]

    with pytest.raises(ValueError, match="one metadata item to broadcast"):
        region_mask._region_metadata_for_images([first, second], 3)


def test_region_mask_uses_each_images_metadata_and_source_preview(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    images = torch.stack(
        (
            torch.full((3, 4, 3), 0.1, dtype=torch.float32),
            torch.full((3, 4, 3), 0.2, dtype=torch.float32),
        )
    )
    metadata = [_metadata("first", 0.25), _metadata("second", 0.75)]
    for item in metadata:
        item["selected_region"].update(
            {
                "mask_shape": "stale",
                "padding": 99,
                "padding_px": 99,
                "feather": 99,
                "invert": True,
            }
        )
    built = []
    preview_means = []
    sent = []

    def build_region_mask(image, target_region, **_kwargs):
        built.append((float(image.mean()), target_region["id"]))
        return torch.full(
            (1, image.shape[1], image.shape[2], 1),
            target_region["fill"],
            dtype=image.dtype,
        )

    def cache_generated_preview(image):
        value = round(float(image.mean()), 4)
        preview_means.append(value)
        return SimpleNamespace(url=f"/preview/{value}")

    monkeypatch.setattr(region_mask, "build_region_mask", build_region_mask)
    monkeypatch.setattr(
        region_mask,
        "cache_generated_preview",
        cache_generated_preview,
    )
    monkeypatch.setattr(
        region_mask,
        "safe_send_sync",
        lambda event, payload, node_id: sent.append((event, payload, node_id)),
    )

    response = region_mask.LF_RegionMask().on_exec(
        image=[images],
        region_meta=metadata,
        region_index=[-1],
        shape=["rectangle"],
        padding=[0.0],
        padding_px=[0.0],
        feather=[0.0],
        invert=[False],
        node_id=["region-2"],
    )
    mask, mask_list, first_region, region_list = response["result"]

    assert built == [(pytest.approx(0.1), "first"), (pytest.approx(0.2), "second")]
    assert mask.shape == (2, 3, 4)
    assert len(mask_list) == 2
    torch.testing.assert_close(mask_list[0], torch.full((1, 3, 4), 0.25))
    torch.testing.assert_close(mask_list[1], torch.full((1, 3, 4), 0.75))
    assert first_region["id"] == "first"
    assert [item["id"] for item in region_list] == ["first", "second"]
    for item in region_list:
        assert item["mask_shape"] == "rectangle"
        assert item["padding"] == 0.0
        assert item["padding_px"] == 0.0
        assert item["feather"] == 0.0
        assert item["invert"] is False
    assert preview_means == [0.1, 0.25, 0.2, 0.75]

    event, payload, node_id = sent[0]
    assert event == "regionmask"
    assert node_id == ["region-2"]
    assert response["ui"]["lf_output"][0] is payload
    assert len(payload["dataset"]["nodes"]) == 2
    values = [
        node["cells"]["lfImage"]["lfValue"]
        for node in payload["dataset"]["nodes"]
    ]
    assert values == ["/preview/0.25", "/preview/0.75"]
