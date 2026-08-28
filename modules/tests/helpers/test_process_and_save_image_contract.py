from __future__ import annotations

import importlib
import inspect
from pathlib import Path
from types import SimpleNamespace

import torch

from modules.utils.helpers.ui import generated_preview as preview_module


process_module = importlib.import_module(
    "modules.utils.helpers.torch.process_and_save_image"
)


def test_process_and_save_image_is_directly_importable_with_public_signature() -> None:
    signature = inspect.signature(process_module.process_and_save_image)

    assert process_module.__name__ == (
        "modules.utils.helpers.torch.process_and_save_image"
    )
    assert tuple(signature.parameters) == (
        "images",
        "filter_function",
        "filter_args",
        "nodes",
    )
    assert all(
        parameter.default is inspect.Parameter.empty
        for parameter in signature.parameters.values()
    )


def test_process_and_save_image_uses_cached_preview_urls_and_preserves_order(
    monkeypatch,
) -> None:
    first = torch.zeros((1, 2, 2, 3), dtype=torch.float32)
    second = torch.ones((1, 2, 2, 3), dtype=torch.float32)
    previewed: list[torch.Tensor] = []

    def fake_cache_generated_preview(image: torch.Tensor) -> SimpleNamespace:
        previewed.append(image)
        return SimpleNamespace(url=f"/view?preview={len(previewed)}&type=input")

    filter_calls: list[tuple[torch.Tensor, float]] = []

    def brighten(image: torch.Tensor, amount: float) -> torch.Tensor:
        filter_calls.append((image, amount))
        return image + amount

    monkeypatch.setattr(
        process_module,
        "cache_generated_preview",
        fake_cache_generated_preview,
    )
    nodes: list[dict] = []

    result = process_module.process_and_save_image(
        [first, second],
        brighten,
        {"amount": 0.25},
        nodes,
    )

    assert len(result) == 2
    assert torch.equal(result[0], first + 0.25)
    assert torch.equal(result[1], second + 0.25)
    assert len(filter_calls) == 2
    assert filter_calls[0][0] is first
    assert filter_calls[0][1] == 0.25
    assert filter_calls[1][0] is second
    assert filter_calls[1][1] == 0.25
    assert previewed[0] is first
    assert previewed[1] is result[0]
    assert previewed[2] is second
    assert previewed[3] is result[1]
    assert nodes == [
        {
            "cells": {
                "lfImage": {
                    "shape": "image",
                    "lfValue": "/view?preview=1&type=input",
                    "value": "",
                },
                "lfImage_after": {
                    "shape": "image",
                    "lfValue": "/view?preview=2&type=input",
                    "value": "",
                },
            },
            "id": "image_1",
            "value": "Comparison 1",
        },
        {
            "cells": {
                "lfImage": {
                    "shape": "image",
                    "lfValue": "/view?preview=3&type=input",
                    "value": "",
                },
                "lfImage_after": {
                    "shape": "image",
                    "lfValue": "/view?preview=4&type=input",
                    "value": "",
                },
            },
            "id": "image_2",
            "value": "Comparison 2",
        },
    ]


def test_process_and_save_image_accepts_real_generated_preview_returns(
    monkeypatch,
    tmp_path: Path,
) -> None:
    input_root = tmp_path / "input"
    input_root.mkdir()
    monkeypatch.setattr(
        preview_module,
        "get_comfy_dir",
        lambda kind: str(input_root) if kind == "input" else str(tmp_path / kind),
    )
    source = torch.zeros((1, 2, 2, 3), dtype=torch.float32)
    nodes: list[dict] = []

    result = process_module.process_and_save_image(
        [source],
        lambda image, amount: image + amount,
        {"amount": 0.5},
        nodes,
    )

    assert torch.equal(result[0], torch.full_like(source, 0.5))
    before_url = nodes[0]["cells"]["lfImage"]["lfValue"]
    after_url = nodes[0]["cells"]["lfImage_after"]["lfValue"]
    assert before_url != after_url
    assert "&type=input&" in before_url
    assert "&type=input&" in after_url
    assert "nonce=" not in before_url
    assert "nonce=" not in after_url
    assert len(list(input_root.rglob("*.png"))) == 2


def test_process_and_save_image_filters_rgb_but_preserves_source_alpha(
    monkeypatch,
) -> None:
    source = torch.zeros((1, 2, 3, 4), dtype=torch.float32)
    source[..., :3] = 0.2
    source[..., 3] = torch.tensor(
        [[0.0, 0.25, 0.5], [0.75, 1.0, 0.1]], dtype=torch.float32
    )
    filter_inputs: list[torch.Tensor] = []

    def fake_cache_generated_preview(_image: torch.Tensor) -> SimpleNamespace:
        return SimpleNamespace(url="/view?preview=alpha&type=input")

    def brighten(image: torch.Tensor, amount: float) -> torch.Tensor:
        filter_inputs.append(image)
        return image + amount

    monkeypatch.setattr(
        process_module,
        "cache_generated_preview",
        fake_cache_generated_preview,
    )

    result = process_module.process_and_save_image(
        [source],
        brighten,
        {"amount": 0.3},
        [],
    )[0]

    assert filter_inputs[0].shape == (1, 2, 3, 3)
    torch.testing.assert_close(
        result[..., :3], torch.full_like(source[..., :3], 0.5)
    )
    torch.testing.assert_close(result[..., 3:4], source[..., 3:4])
