from __future__ import annotations

import pytest
import torch

from modules.nodes.image import iso_diamond_tiles as module


def _texture(seed: int = 7) -> torch.Tensor:
    generator = torch.Generator().manual_seed(seed)
    return torch.rand((1, 64, 64, 3), generator=generator)


def test_tiles_have_diamond_alpha_and_a_one_row_atlas() -> None:
    tiles, atlas, receipt = module.render_iso_diamond_tiles(
        _texture(), tile_width=128, tile_height=64, variants=4, seed=42
    )
    assert tiles.shape == (4, 64, 128, 4)
    assert atlas.shape == (1, 64, 512, 4)
    alpha = tiles[0, :, :, 3]
    assert alpha[0, 0] == 0.0 and alpha[0, -1] == 0.0 and alpha[-1, 0] == 0.0 and alpha[-1, -1] == 0.0
    assert alpha[32, 64] == 1.0
    assert alpha[32, 0] > 0.0 and alpha[0, 64] > 0.0, "the diamond touches the tile's edge midpoints"
    assert receipt["schema"] == module.ISO_DIAMOND_RECEIPT_SCHEMA
    assert receipt["variants"] == 4 and len(receipt["offsets"]) == 4
    assert receipt["atlasSize"] == {"width": 512, "height": 64}


def test_same_seed_repeats_and_another_seed_moves_the_cut() -> None:
    first, _, first_receipt = module.render_iso_diamond_tiles(_texture(), seed=3)
    again, _, again_receipt = module.render_iso_diamond_tiles(_texture(), seed=3)
    other, _, other_receipt = module.render_iso_diamond_tiles(_texture(), seed=4)
    assert torch.equal(first, again)
    assert first_receipt["offsets"] == again_receipt["offsets"]
    assert first_receipt["offsets"] != other_receipt["offsets"]
    assert not torch.equal(first[..., :3], other[..., :3])


def test_constant_texture_gives_constant_colour_inside_the_diamond() -> None:
    flat = torch.full((1, 32, 32, 3), 0.25)
    tiles, _, _ = module.render_iso_diamond_tiles(flat, tile_width=64, tile_height=32, variants=2, texture_scale=1.0)
    inside = tiles[0, 16, 32, :3]
    assert torch.allclose(inside, torch.full((3,), 0.25), atol=1e-5)


def test_diamond_alpha_is_symmetric_and_antialiased() -> None:
    alpha = module.diamond_alpha(64, 32)
    assert torch.allclose(alpha, alpha.flip(0), atol=1e-6)
    assert torch.allclose(alpha, alpha.flip(1), atol=1e-6)
    assert ((alpha > 0.0) & (alpha < 1.0)).any(), "edges must carry partial coverage"


@pytest.mark.parametrize(
    "kwargs",
    [
        {"tile_width": 4},
        {"tile_height": 2},
        {"variants": 0},
        {"seed": -1},
        {"texture_scale": 0.0},
        {"texture_scale": 9.0},
    ],
)
def test_invalid_controls_are_refused(kwargs: dict) -> None:
    with pytest.raises(ValueError):
        module.render_iso_diamond_tiles(_texture(), **kwargs)


def test_node_declares_its_contract() -> None:
    types = module.LF_IsoDiamondTiles.INPUT_TYPES()
    assert set(types["required"]) == {"image", "tile_width", "tile_height", "variants", "seed", "texture_scale"}
    assert module.LF_IsoDiamondTiles.RETURN_NAMES == ("tiles", "atlas", "receipt", "tile_list")
    assert module.NODE_CLASS_MAPPINGS["LF_IsoDiamondTiles"] is module.LF_IsoDiamondTiles
