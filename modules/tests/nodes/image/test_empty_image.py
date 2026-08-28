from __future__ import annotations

import pytest
import torch

from modules.nodes.image import empty_image
from modules.nodes.image.empty_image import LF_EmptyImage
from modules.utils.constants import Input


def test_empty_image_declares_both_returned_image_outputs() -> None:
    assert LF_EmptyImage.INPUT_IS_LIST is True
    assert LF_EmptyImage.RETURN_NAMES == ("image", "image_list")
    assert LF_EmptyImage.RETURN_TYPES == (Input.IMAGE, Input.IMAGE)
    assert LF_EmptyImage.OUTPUT_IS_LIST == (False, True)


def test_empty_image_processes_parallel_lists_and_publishes_final_history(
    monkeypatch,
) -> None:
    sent = []
    monkeypatch.setattr(
        empty_image,
        "create_cached_masonry_node",
        lambda image, *, index, label: {
            "id": index,
            "label": label,
            "mean": float(image.mean()),
        },
    )
    monkeypatch.setattr(
        empty_image,
        "safe_send_sync",
        lambda event, payload, node_id: sent.append((event, payload, node_id)),
    )

    response = LF_EmptyImage().on_exec(
        width=[64, 96],
        height=[32, 48],
        color=["FF0000", "00FF00"],
        node_id=["empty-node"],
    )
    primary, image_list = response["result"]

    assert primary.shape == (1, 32, 64, 3)
    assert [tuple(image.shape) for image in image_list] == [
        (1, 32, 64, 3),
        (1, 48, 96, 3),
    ]
    torch.testing.assert_close(image_list[0][0, 0, 0], torch.tensor([1.0, 0.0, 0.0]))
    torch.testing.assert_close(image_list[1][0, 0, 0], torch.tensor([0.0, 1.0, 0.0]))
    assert sent[0][0] == "emptyimage"
    assert sent[0][2] == ["empty-node"]
    assert response["ui"]["lf_output"][0] is sent[0][1]


def test_empty_image_rejects_mismatched_parallel_lists() -> None:
    with pytest.raises(ValueError, match="same length"):
        LF_EmptyImage().on_exec(
            width=[64, 96],
            height=[32],
            color=["FF0000", "00FF00"],
        )
