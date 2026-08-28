from __future__ import annotations

import importlib
from types import SimpleNamespace

import torch

from modules.nodes.filters import bloom as bloom_node
from modules.utils.filters.bloom import bloom_effect


process_module = importlib.import_module(
    "modules.utils.helpers.torch.process_and_save_image"
)


def test_bloom_effect_returns_bhwc_on_the_source_device_and_dtype() -> None:
    image = torch.full((1, 5, 7, 3), 0.2, dtype=torch.float64)

    result = bloom_effect(
        image,
        threshold=1.0,
        radius=3,
        intensity=0.6,
    )

    assert result.shape == image.shape
    assert result.dtype == image.dtype
    assert result.device == image.device


def test_bloom_node_preserves_batch_order_alpha_and_both_output_forms(
    monkeypatch,
) -> None:
    image = torch.zeros((2, 4, 5, 4), dtype=torch.float32)
    image[0, ..., :3] = 0.2
    image[1, ..., :3] = 0.4
    image[..., 3] = torch.linspace(0.0, 1.0, 20).reshape(1, 4, 5)
    previews: list[torch.Tensor] = []
    events: list[tuple] = []

    def fake_preview(value: torch.Tensor) -> SimpleNamespace:
        previews.append(value)
        return SimpleNamespace(url=f"/view?preview={len(previews)}&type=input")

    monkeypatch.setattr(process_module, "cache_generated_preview", fake_preview)
    monkeypatch.setattr(
        bloom_node,
        "safe_send_sync",
        lambda *args: events.append(args),
    )

    response = bloom_node.LF_Bloom().on_exec(
        image=image,
        threshold=1.0,
        radius=3,
        intensity=0.6,
        tint="FFFFFF",
        node_id="bloom-test",
    )
    batch, image_list = response["result"]

    assert batch.shape == image.shape
    assert len(image_list) == 2
    torch.testing.assert_close(batch[..., 3:4], image[..., 3:4])
    torch.testing.assert_close(batch[0, ..., :3], image[0, ..., :3])
    torch.testing.assert_close(batch[1, ..., :3], image[1, ..., :3])
    assert all(item.shape == (1, 4, 5, 4) for item in image_list)
    assert len(response["ui"]["lf_output"][0]["dataset"]["nodes"]) == 2
    assert len(previews) == 4
    assert events[0][0] == "bloom"
    assert events[0][2] == "bloom-test"
