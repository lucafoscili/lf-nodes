from __future__ import annotations

from pathlib import Path

from PIL import Image
import pytest
import torch

from modules.utils.helpers.ui import generated_preview as preview_module


@pytest.fixture
def input_root(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    root = tmp_path / "input"
    root.mkdir()
    monkeypatch.setattr(
        preview_module,
        "get_comfy_dir",
        lambda kind: str(root) if kind == "input" else str(tmp_path / kind),
    )
    return root


def test_same_pixels_deduplicate_to_one_restart_stable_resource(input_root: Path) -> None:
    image = torch.linspace(0.0, 1.0, 12).reshape(1, 2, 2, 3)

    first = preview_module.cache_generated_preview(image)
    first_mtime = Path(first.absolute_path).stat().st_mtime_ns
    second = preview_module.cache_generated_preview(image.clone())

    assert first == second
    assert Path(first.absolute_path).stat().st_mtime_ns == first_mtime
    assert list(input_root.rglob("*.png")) == [Path(first.absolute_path)]
    assert first.subfolder.startswith("_lf_external_previews/generated/v1/")
    assert first.url == (
        f"/view?filename={first.sha256}.png&type=input&subfolder={first.subfolder}"
    )
    assert "nonce=" not in first.url


def test_changed_pixels_and_alpha_produce_different_resources(input_root: Path) -> None:
    opaque = torch.zeros((1, 2, 2, 4), dtype=torch.float32)
    opaque[..., 0] = 1.0
    opaque[..., 3] = 1.0
    transparent = opaque.clone()
    transparent[0, 0, 0, 3] = 0.25

    first = preview_module.cache_generated_preview(opaque)
    second = preview_module.cache_generated_preview(transparent)

    assert first.sha256 != second.sha256
    assert len(list(input_root.rglob("*.png"))) == 2
    with Image.open(second.absolute_path) as stored:
        assert stored.mode == "RGBA"
        assert stored.getpixel((0, 0)) == (255, 0, 0, 64)


def test_preview_downscales_long_edge_deterministically(input_root: Path) -> None:
    image = torch.zeros((1, 400, 800, 3), dtype=torch.float32)

    result = preview_module.cache_generated_preview(image, max_long_edge=512)

    assert (result.width, result.height, result.mode) == (512, 256, "RGB")
    with Image.open(result.absolute_path) as stored:
        assert stored.size == (512, 256)


def test_rgba_resize_does_not_bleed_hidden_transparent_rgb(input_root: Path) -> None:
    image = torch.tensor(
        [[[[1.0, 0.0, 0.0, 0.0], [0.0, 0.0, 1.0, 1.0]]]],
        dtype=torch.float32,
    )

    result = preview_module.cache_generated_preview(
        image,
        target_size=(1, 1),
        max_long_edge=0,
    )

    with Image.open(result.absolute_path) as stored:
        red, green, blue, alpha = stored.getpixel((0, 0))
    assert red == 0
    assert green == 0
    assert blue == 255
    assert 0 < alpha < 255


def test_corrupt_hash_path_is_atomically_repaired(input_root: Path) -> None:
    image = torch.rand((1, 8, 8, 3), generator=torch.Generator().manual_seed(7))
    first = preview_module.cache_generated_preview(image)
    path = Path(first.absolute_path)
    expected = path.read_bytes()
    path.write_bytes(b"not a png")

    repaired = preview_module.cache_generated_preview(image)

    assert repaired == first
    assert path.read_bytes() == expected
    assert not list(path.parent.glob("*.tmp"))


@pytest.mark.parametrize(
    "image, message",
    [
        (torch.zeros((2, 4, 4, 3)), "exactly one"),
        (torch.zeros((1, 4, 4, 1)), "RGB or RGBA"),
        (torch.zeros((4, 4)), "exactly one"),
    ],
)
def test_invalid_preview_shapes_fail_closed(
    input_root: Path,
    image: torch.Tensor,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        preview_module.cache_generated_preview(image)

    assert not list(input_root.rglob("*.png"))
