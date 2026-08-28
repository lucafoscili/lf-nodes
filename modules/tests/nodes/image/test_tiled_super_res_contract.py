from __future__ import annotations

from types import SimpleNamespace

import torch
import torch.nn.functional as F

from modules.nodes.image import tiled_super_res


class _FakeUpscaler:
    scale = 2.0

    def __init__(self) -> None:
        self.calls: list[tuple[int, ...]] = []
        self.model = self

    def __call__(self, image: torch.Tensor) -> torch.Tensor:
        self.calls.append(tuple(image.shape))
        return F.interpolate(image, scale_factor=2, mode="nearest")

    def to(self, _device):
        return self


class _PreviewStream:
    def __init__(self, **kwargs) -> None:
        self.input_url = ""

    def save_preview(self, *_args, **_kwargs) -> str:
        return "/preview"

    def update_compare(self, *_args, **_kwargs) -> None:
        return None

    def emit(self) -> None:
        return None


def test_tiled_super_res_sends_only_rgb_to_model_and_preserves_alpha(
    monkeypatch,
) -> None:
    rgba = torch.zeros((1, 2, 3, 4), dtype=torch.float32)
    rgba[..., :3] = 0.25
    rgba[..., 3] = 0.4
    rgb = torch.full((1, 2, 3, 3), 0.75, dtype=torch.float32)
    upscaler = _FakeUpscaler()
    sharpen_shapes: list[tuple[int, ...]] = []

    monkeypatch.setattr(
        tiled_super_res.model_management,
        "get_torch_device",
        lambda: torch.device("cpu"),
        raising=False,
    )
    monkeypatch.setattr(
        tiled_super_res.model_management,
        "module_size",
        lambda _model: 0,
        raising=False,
    )
    monkeypatch.setattr(
        tiled_super_res.model_management,
        "get_free_memory",
        lambda _device: 10**12,
        raising=False,
    )
    monkeypatch.setattr(
        tiled_super_res.model_management,
        "free_memory",
        lambda *_args: None,
        raising=False,
    )
    monkeypatch.setattr(tiled_super_res, "ComparePreviewStream", _PreviewStream)
    monkeypatch.setattr(
        tiled_super_res,
        "cache_generated_preview",
        lambda *_args, **_kwargs: SimpleNamespace(url="/input"),
    )
    monkeypatch.setattr(
        tiled_super_res.LF_TiledSuperRes,
        "_save_compare_images",
        staticmethod(lambda *_args, **_kwargs: ("/clean", "/debug")),
    )
    monkeypatch.setattr(tiled_super_res, "safe_send_sync", lambda *_args: None)

    def fake_sharpen(image: torch.Tensor, **_kwargs) -> torch.Tensor:
        sharpen_shapes.append(tuple(image.shape))
        return image

    monkeypatch.setattr(tiled_super_res, "unsharp_mask_effect", fake_sharpen)

    response = tiled_super_res.LF_TiledSuperRes().on_exec(
        image=[rgba, rgb],
        upscale_model=[upscaler],
        target_long_edge=[0],
        tile_count=[1],
        sharpen=[0.25],
        node_id=["super-res"],
    )
    primary, image_list, stats = response["result"]

    assert all(shape[1] == 3 for shape in upscaler.calls)
    assert sharpen_shapes == [(1, 4, 6, 3), (1, 4, 6, 3)]
    assert [image.shape[-1] for image in image_list] == [4, 3]
    torch.testing.assert_close(
        image_list[0][..., 3],
        torch.full((1, 4, 6), 0.4),
    )
    assert primary.shape == (1, 4, 6, 4)
    assert [row["alpha_policy"] for row in stats["runs"]] == [
        "preserve",
        "opaque",
    ]
