from __future__ import annotations

import pytest
import torch

from modules.nodes.image import compare_images as compare_module
from modules.utils.helpers.ui import create_compare_node


def test_compare_images_publishes_history_dataset_and_preserves_rgba(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    node = compare_module.LF_CompareImages()
    cached_pairs = []
    sent = []

    def create_cached_compare(before, after, *, index):
        cached_pairs.append((before.clone(), after.clone(), index))
        return create_compare_node(
            f"/view?filename=before-{index}.png&type=input",
            f"/view?filename=after-{index}.png&type=input",
            index,
        )

    monkeypatch.setattr(
        compare_module,
        "create_cached_compare_node",
        create_cached_compare,
    )
    monkeypatch.setattr(
        compare_module,
        "safe_send_sync",
        lambda event, payload, node_id: sent.append((event, payload, node_id)),
    )

    before = torch.rand(1, 7, 5, 4)
    after = torch.rand(1, 12, 9, 4)
    response = node.on_exec(
        image_before=before,
        image_after=after,
        node_id="compare-node",
    )

    dataset = response["ui"]["lf_output"][0]["dataset"]
    assert response["result"][3] is dataset
    assert len(dataset["nodes"]) == 1
    assert dataset["nodes"][0]["cells"]["lfImage"]["lfValue"].startswith("/view?")
    assert dataset["nodes"][0]["cells"]["lfImage_after"]["lfValue"].startswith(
        "/view?"
    )
    assert sent == [("compareimages", {"dataset": dataset}, "compare-node")]
    assert len(cached_pairs) == 1
    cached_before, cached_after, cached_index = cached_pairs[0]
    assert cached_index == 0
    assert torch.equal(cached_before, before)
    assert torch.equal(cached_after, after)


def test_compare_images_rejects_mismatched_batches(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    node = compare_module.LF_CompareImages()

    with pytest.raises(ValueError, match="same length"):
        node.on_exec(
            image_before=torch.rand(2, 8, 8, 3),
            image_after=torch.rand(1, 8, 8, 3),
        )
