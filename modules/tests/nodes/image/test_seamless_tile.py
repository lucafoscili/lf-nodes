from __future__ import annotations

import pytest
import torch

from modules.nodes.image import seamless_tile as module


def _gradient(height: int = 64, width: int = 64) -> torch.Tensor:
    ys = torch.linspace(0.0, 1.0, height).unsqueeze(1).expand(height, width)
    xs = torch.linspace(0.0, 1.0, width).unsqueeze(0).expand(height, width)
    return torch.stack([xs, ys, (xs + ys) / 2.0], dim=2).unsqueeze(0)


def _wrap_gap(image: torch.Tensor) -> tuple[float, float]:
    horizontal = (image[0, :, 0, :] - image[0, :, -1, :]).abs().mean().item()
    vertical = (image[0, 0, :, :] - image[0, -1, :, :]).abs().mean().item()
    return horizontal, vertical


def test_output_wraps_where_the_input_did_not() -> None:
    source = _gradient()
    before_h, before_v = _wrap_gap(source)
    result, receipt = module.make_seamless_tile(source, blend_fraction=0.25)
    after_h, after_v = _wrap_gap(result)
    assert before_h >= 0.4 and before_v >= 0.4
    assert after_h < 0.05 and after_v < 0.05
    assert result.shape == source.shape
    assert receipt["schema"] == module.SEAMLESS_TILE_RECEIPT_SCHEMA
    assert receipt["blendFraction"] == 0.25


def test_is_deterministic_and_keeps_the_centre() -> None:
    source = _gradient()
    first, _ = module.make_seamless_tile(source, blend_fraction=0.2)
    second, _ = module.make_seamless_tile(source, blend_fraction=0.2)
    assert torch.equal(first, second)
    # The centre is (almost) pure original inside the blend band; the rolled copy
    # would put the original's corner there instead.
    rolled_centre = source[0, 0, 0]
    assert (first[0, 32, 32] - source[0, 32, 32]).abs().max() < 0.05
    assert (first[0, 32, 32] - rolled_centre).abs().max() > 0.3


def test_batches_are_handled_per_image() -> None:
    source = torch.cat([_gradient(), _gradient() * 0.5], dim=0)
    result, receipt = module.make_seamless_tile(source)
    assert result.shape == source.shape
    assert receipt["count"] == 2


@pytest.mark.parametrize("blend", [0.0, 0.01, 0.6, True])
def test_invalid_blend_is_refused(blend: object) -> None:
    with pytest.raises(ValueError):
        module.make_seamless_tile(_gradient(), blend_fraction=blend)  # type: ignore[arg-type]


def test_tiny_or_malformed_images_are_refused() -> None:
    with pytest.raises(ValueError):
        module.make_seamless_tile(torch.zeros((1, 4, 4, 3)))
    with pytest.raises(ValueError):
        module.make_seamless_tile(torch.zeros((4, 4, 3)))


def test_node_declares_its_contract() -> None:
    types = module.LF_SeamlessTile.INPUT_TYPES()
    assert set(types["required"]) == {"image", "blend_fraction"}
    assert module.LF_SeamlessTile.RETURN_NAMES == ("image", "receipt", "image_list")
    assert module.NODE_CLASS_MAPPINGS["LF_SeamlessTile"] is module.LF_SeamlessTile
