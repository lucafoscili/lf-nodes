from __future__ import annotations

import pytest
import torch

from modules.nodes.image import lut_application
from modules.utils.constants import (
    BLUE_CHANNEL_ID,
    GREEN_CHANNEL_ID,
    RED_CHANNEL_ID,
)
from modules.utils.filters.blend import blend_effect


def test_blend_preserves_base_alpha_and_uses_overlay_alpha() -> None:
    base = torch.zeros((1, 2, 2, 4), dtype=torch.float32)
    base[..., :3] = 0.2
    base[..., 3] = torch.tensor([[0.1, 0.3], [0.7, 1.0]])
    overlay = torch.ones((1, 2, 2, 4), dtype=torch.float32)
    overlay[..., 3] = 0.5

    result = blend_effect(base, overlay, 0.5, mode="normal")

    assert result.shape == base.shape
    torch.testing.assert_close(result[..., :3], torch.full_like(base[..., :3], 0.4))
    torch.testing.assert_close(result[..., 3:4], base[..., 3:4])


def _identity_lut_dataset(image_count: int = 1) -> dict:
    identity_nodes = [
        {
            "cells": {
                RED_CHANNEL_ID: {"value": index},
                GREEN_CHANNEL_ID: {"value": index},
                BLUE_CHANNEL_ID: {"value": index},
            }
        }
        for index in range(256)
    ]
    return {
        f"Image #{index}": {"nodes": identity_nodes}
        for index in range(1, image_count + 1)
    }


def _patch_lut_preview(monkeypatch) -> None:
    monkeypatch.setattr(lut_application, "safe_send_sync", lambda *_args: None)
    monkeypatch.setattr(
        lut_application,
        "create_cached_compare_node",
        lambda *_args, **_kwargs: {"id": "comparison"},
    )


def test_lut_application_changes_only_rgb_on_rgba_input(monkeypatch) -> None:
    image = torch.tensor(
        [
            [
                [[0.0, 0.2, 0.4, 0.13], [0.6, 0.8, 1.0, 0.47]],
                [[1.0, 0.8, 0.6, 0.79], [0.4, 0.2, 0.0, 1.0]],
            ]
        ],
        dtype=torch.float32,
    )
    dataset = _identity_lut_dataset()
    _patch_lut_preview(monkeypatch)

    assert lut_application.LF_LUTApplication.INPUT_IS_LIST is True
    response = lut_application.LF_LUTApplication().on_exec(
        image=[image],
        strength=[1.0],
        lut_dataset=[dataset],
        preset=["auto_photoreal"],
    )
    result = response["result"][0]

    assert result.shape == image.shape
    torch.testing.assert_close(result[..., 3:4], image[..., 3:4])
    torch.testing.assert_close(result[..., :3], image[..., :3], atol=1 / 255, rtol=0)


def test_lut_application_broadcasts_one_lut_across_an_image_batch(monkeypatch) -> None:
    images = torch.rand((3, 4, 5, 3), dtype=torch.float32)
    _patch_lut_preview(monkeypatch)

    response = lut_application.LF_LUTApplication().on_exec(
        image=[images],
        strength=[1.0],
        lut_dataset=[_identity_lut_dataset()],
        preset=["legacy"],
    )
    batch, image_list = response["result"]

    assert batch.shape == images.shape
    assert len(image_list) == 3
    torch.testing.assert_close(batch, images, atol=1 / 255, rtol=0)


def test_lut_application_pairs_exact_per_image_luts(monkeypatch) -> None:
    images = torch.rand((2, 3, 4, 3), dtype=torch.float32)
    dataset = _identity_lut_dataset(2)
    dataset["Image #2"]["nodes"] = [
        {
            "cells": {
                RED_CHANNEL_ID: {"value": 0},
                GREEN_CHANNEL_ID: {"value": 0},
                BLUE_CHANNEL_ID: {"value": 0},
            }
        }
        for _index in range(256)
    ]
    _patch_lut_preview(monkeypatch)

    response = lut_application.LF_LUTApplication().on_exec(
        image=[images],
        strength=[1.0],
        lut_dataset=[dataset],
        preset=["legacy"],
    )
    batch = response["result"][0]

    torch.testing.assert_close(batch[0], images[0], atol=1 / 255, rtol=0)
    torch.testing.assert_close(batch[1], torch.zeros_like(batch[1]))


def test_lut_application_rejects_partial_lut_cardinality(monkeypatch) -> None:
    images = torch.rand((3, 2, 2, 3), dtype=torch.float32)
    _patch_lut_preview(monkeypatch)

    with pytest.raises(
        ValueError,
        match="one value to broadcast or exactly 3 values; got 2",
    ):
        lut_application.LF_LUTApplication().on_exec(
            image=[images],
            strength=[1.0],
            lut_dataset=[_identity_lut_dataset(2)],
            preset=["legacy"],
        )
