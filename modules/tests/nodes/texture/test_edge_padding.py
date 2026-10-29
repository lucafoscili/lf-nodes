from __future__ import annotations

import json

import pytest
import torch

from modules.nodes.texture import edge_padding as node_module
from modules.utils.helpers.torch.texture_maps import edge_pad


def _island(height=24, width=40):
    mask = torch.zeros(height, width)
    mask[6:14, 10:22] = 1
    return mask


def test_published_schema():
    node = node_module.LF_EdgePadding
    inputs = node.INPUT_TYPES()
    assert list(inputs["required"]) == ["image", "mask"]
    assert inputs["required"]["mask"][0] == "MASK"
    assert inputs["optional"]["ui_widget"][0] == "LF_COMPARE"
    assert node.INPUT_IS_LIST is True
    assert node.RETURN_TYPES == ("IMAGE", "JSON", "IMAGE")
    assert node.RETURN_NAMES == ("image", "receipt", "image_list")
    assert node.OUTPUT_IS_LIST == (False, False, True)
    assert not getattr(node, "OUTPUT_NODE", False)


def test_kept_pixels_are_exact_and_the_rest_take_the_island_colour():
    image = torch.zeros(24, 40, 4)
    image[6:14, 10:16] = torch.tensor([1.0, 0.0, 0.0, 1.0])
    image[6:14, 16:22] = torch.tensor([0.0, 0.0, 1.0, 0.5])
    image[~(_island() > 0.5)] = torch.tensor([0.2, 0.9, 0.2, 0.0])  # background that must not survive
    padded, receipt = edge_pad(image, _island())
    covered = _island() > 0.5
    assert torch.equal(padded[covered], image[covered])
    assert padded.dtype == image.dtype
    # Beside the island each side continues its own colour; far away the scales that first reach the island
    # average it. No background green survives anywhere.
    assert padded[10, 8, 0] > 0.9 and padded[10, 8, 2] < 0.1
    assert padded[10, 23, 2] > 0.9 and padded[10, 23, 0] < 0.1
    assert padded[10, 39, 0] == pytest.approx(0.5) and padded[10, 39, 2] == pytest.approx(0.5)
    assert float(padded[~covered][:, 1].max()) < 1e-6
    # Alpha is padded like colour: each side continues its own opacity.
    assert padded[10, 8, 3] == pytest.approx(1.0) and padded[10, 23, 3] == pytest.approx(0.5)
    assert receipt["covered_pixels"] == 96 and receipt["padded_pixels"] == 24 * 40 - 96
    assert receipt["levels"] == 6


def test_odd_sizes_full_and_partial_masks():
    image = torch.rand(7, 5, 3, generator=torch.Generator().manual_seed(1))
    mask = torch.zeros(7, 5)
    mask[3, 2] = 0.75
    padded, _ = edge_pad(image, mask)
    torch.testing.assert_close(padded, image[3, 2].expand(7, 5, 3))
    full, receipt = edge_pad(image, torch.ones(7, 5))
    assert torch.equal(full, image) and receipt["padded_pixels"] == 0


def test_node_pairs_one_mask_with_a_batch_and_reports(events):
    images = torch.rand(2, 24, 40, 3, generator=torch.Generator().manual_seed(2))
    response = node_module.LF_EdgePadding().on_exec(image=[images], mask=[_island()], node_id=["7"])
    batch, receipt, image_list = response["result"]
    assert batch.shape == (2, 24, 40, 3) and len(image_list) == 2
    assert receipt["schema"] == "lf.edge-padding.v1" and receipt["image_count"] == 2
    assert [row["index"] for row in receipt["images"]] == [0, 1]
    event, payload, node_id = events[0]
    assert (event, node_id) == ("edgepadding", "7")
    assert response["ui"]["lf_output"] == [payload]
    cells = payload["dataset"]["nodes"][0]["cells"]
    assert {"lfImage", "lfImage_after", "lfImage_debug"} <= set(cells)
    assert all(cell["lfValue"].startswith("/view?") for cell in cells.values())
    json.dumps(payload, allow_nan=False)


def test_failures_are_loud():
    image = torch.rand(1, 8, 8, 3)
    with pytest.raises(ValueError, match="nothing to pad from"):
        node_module.LF_EdgePadding().on_exec(image=[image], mask=[torch.zeros(1, 8, 8)])
    with pytest.raises(ValueError, match="does not match"):
        node_module.LF_EdgePadding().on_exec(image=[image], mask=[torch.ones(1, 4, 8)])
    with pytest.raises(ValueError, match="Mask count mismatch"):
        node_module.LF_EdgePadding().on_exec(image=[torch.rand(3, 8, 8, 3)], mask=[torch.ones(2, 8, 8)])
    with pytest.raises(ValueError, match="mask is required"):
        node_module.LF_EdgePadding().on_exec(image=[image], mask=None)
