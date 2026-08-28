from __future__ import annotations

import pytest
import torch

from modules.nodes.logic import switch_image, switch_mask
from modules.nodes.logic.switch_image import LF_SwitchImage
from modules.nodes.logic.switch_mask import LF_SwitchMask
from modules.utils.constants import Input


def test_image_switch_preserves_selected_batch_and_order(monkeypatch) -> None:
    sent = []
    monkeypatch.setattr(
        switch_image,
        "safe_send_sync",
        lambda event, payload, node_id: sent.append((event, payload, node_id)),
    )
    selected = torch.stack(
        (
            torch.full((3, 4, 3), 0.25),
            torch.full((3, 4, 3), 0.75),
        )
    )
    ignored = torch.zeros((1, 2, 2, 3))

    image_batch, image_list = LF_SwitchImage().on_exec(
        on_true=selected,
        on_false=ignored,
        boolean=[True],
        node_id="switch-image",
    )

    assert LF_SwitchImage.RETURN_TYPES == (Input.IMAGE, Input.IMAGE)
    assert LF_SwitchImage.OUTPUT_IS_LIST == (False, True)
    assert image_batch.shape == (2, 3, 4, 3)
    assert [tuple(image.shape) for image in image_list] == [(1, 3, 4, 3)] * 2
    assert [float(image[0, 0, 0, 0]) for image in image_list] == [0.25, 0.75]
    torch.testing.assert_close(image_batch, selected)
    assert sent == [("switchimage", {"bool": True}, "switch-image")]


def test_mask_switch_preserves_selected_batch_and_order(monkeypatch) -> None:
    sent = []
    monkeypatch.setattr(
        switch_mask,
        "safe_send_sync",
        lambda event, payload, node_id: sent.append((event, payload, node_id)),
    )
    selected = torch.stack(
        (
            torch.full((3, 4), 0.2),
            torch.full((3, 4), 0.8),
        )
    )
    ignored = torch.zeros((1, 2, 2))

    mask_batch, mask_list = LF_SwitchMask().on_exec(
        on_true=ignored,
        on_false=selected,
        boolean=[False],
        node_id="switch-mask",
    )

    assert LF_SwitchMask.RETURN_TYPES == (Input.MASK, Input.MASK)
    assert LF_SwitchMask.OUTPUT_IS_LIST == (False, True)
    assert mask_batch.shape == (2, 3, 4)
    assert [tuple(mask.shape) for mask in mask_list] == [(1, 3, 4)] * 2
    assert [float(mask[0, 0, 0]) for mask in mask_list] == pytest.approx([0.2, 0.8])
    torch.testing.assert_close(mask_batch, selected)
    assert sent == [("switchmask", {"bool": False}, "switch-mask")]
