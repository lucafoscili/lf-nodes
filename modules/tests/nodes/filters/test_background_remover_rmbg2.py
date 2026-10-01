from contextlib import contextmanager
from types import SimpleNamespace

import numpy as np
import pytest
import torch
from PIL import Image

from modules.utils.filters import background_remover as filter_module
from modules.utils.helpers.detection import rmbg2


@pytest.fixture
def backend(monkeypatch):
    calls = []

    @contextmanager
    def session():
        calls.append("open")
        try:
            def predict(image):
                assert image.mode == "RGB"
                calls.append(image.size)
                return Image.new("L", image.size, 128)

            yield predict
        finally:
            calls.append("close")

    monkeypatch.setattr(rmbg2, "rmbg2_session", session)
    monkeypatch.setattr(filter_module, "get_rembg_session", lambda _: pytest.fail("RMBG2 must not use rembg"))
    return calls


def test_direct_model_preserves_rgb_and_intersects_existing_alpha(backend):
    source = torch.tensor([[[[0.2, 0.4, 0.6, 0.0], [0.2, 0.4, 0.6, 1.0]]]])
    before = source.clone()
    result = filter_module.apply_background_removal(
        source, transparent_background=True, background_color="#000000", model_name="RMBG-2.0",
    )
    assert backend == ["open", (2, 1), "close"]
    assert result.cutout.shape == (1, 2, 4)
    assert torch.equal(result.composite, result.cutout)
    assert torch.allclose(result.cutout[..., :3], source[..., :3], atol=1 / 255)
    assert result.mask[0, 0].tolist() == pytest.approx([0.0, 128 / 255])
    assert torch.equal(result.mask, result.cutout[..., 3].unsqueeze(0))
    assert torch.equal(source, before)
    assert result.stats["model"] == "RMBG-2.0"


def test_reused_session_handles_unequal_sizes_and_solid_background(backend, monkeypatch):
    monkeypatch.setattr(filter_module, "cache_generated_preview", lambda _: SimpleNamespace(url="/view?filename=preview.png&type=input"))
    with filter_module.background_removal_session("RMBG-2.0") as remover:
        for height, width in ((2, 3), (5, 2), (2, 3)):
            result, payload = filter_module.background_remover_effect(
                torch.zeros((1, height, width, 3)), transparent_background=False,
                background_color="#FFFFFF", model_name="RMBG-2.0", remover=remover,
            )
            assert result.shape == (height, width, 3)
            assert torch.allclose(result, torch.full_like(result, 127 / 255))
            assert payload["cutout_tensor"].shape == (height, width, 4)
            assert payload["mask_tensor"].shape == (1, height, width)
            assert "type=input" in payload["cutout"]
            assert "type=input" in payload["mask"]
    assert backend == ["open", (3, 2), (2, 5), (3, 2), "close"]


def test_legacy_rembg_still_uses_existing_session_and_cutout(monkeypatch):
    session = object()
    calls = []
    monkeypatch.setattr(filter_module, "get_rembg_session", lambda model: calls.append(model) or session)

    def remove(image, **kwargs):
        assert kwargs == {"session": session}
        image = image.convert("RGBA")
        image.putalpha(Image.new("L", image.size, 64))
        return image

    monkeypatch.setattr(filter_module, "remove", remove)
    result = filter_module.apply_background_removal(
        torch.zeros((1, 2, 3, 3)), transparent_background=True, background_color="#000000", model_name="u2net",
    )
    assert calls == ["u2net"]
    assert np.allclose(result.mask.numpy(), 64 / 255)
