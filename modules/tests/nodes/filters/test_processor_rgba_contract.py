from __future__ import annotations

import pytest
import torch

from modules.utils.filters import processors


def rgba_image() -> torch.Tensor:
    image = torch.linspace(0.0, 1.0, 2 * 3 * 4, dtype=torch.float32).reshape(1, 2, 3, 4)
    image[..., 3] = torch.tensor([[0.0, 0.19, 0.37], [0.53, 0.81, 1.0]])
    return image


def test_real_sepia_processes_rgb_and_reattaches_original_alpha_exactly() -> None:
    image = rgba_image()
    before = image.clone()
    settings = {'intensity': 0.75}
    expected_rgb, _ = processors.apply_sepia_filter(image[..., :3], settings)

    result, payload = processors.process_filter('sepia', image, settings)

    assert result.shape == image.shape
    assert torch.equal(result[..., :3], expected_rgb)
    assert torch.equal(result[..., 3:4], image[..., 3:4])
    assert torch.equal(image, before)
    assert payload == {}


def test_rgb_dispatch_remains_the_existing_processor_result() -> None:
    image = rgba_image()[..., :3].clone()
    settings = {'intensity': 0.4}
    expected = processors.apply_sepia_filter(image, settings)

    actual = processors.process_filter('sepia', image, settings)

    assert torch.equal(actual[0], expected[0])
    assert actual[1] == expected[1]


def test_inpaint_adapter_preserves_payload_and_keeps_alpha_outside_model_call(monkeypatch) -> None:
    image = rgba_image()
    payload = {'mask': '/view?filename=mask.png&type=temp', 'roi': [1, 2, 3, 4]}
    settings = {'context_id': 'editor-session', 'denoise': 0.55}
    calls = []

    def fake_inpaint(rgb, supplied_settings):
        calls.append((rgb.clone(), supplied_settings))
        return 1 - rgb, payload

    monkeypatch.setitem(processors.FILTER_PROCESSORS, 'inpaint', fake_inpaint)
    result, actual_payload = processors.process_filter('inpaint', image, settings)

    assert len(calls) == 1
    assert calls[0][0].shape == (1, 2, 3, 3)
    assert torch.equal(calls[0][0], image[..., :3])
    assert calls[0][1] is settings
    assert torch.equal(result[..., :3], 1 - image[..., :3])
    assert torch.equal(result[..., 3:4], image[..., 3:4])
    assert actual_payload is payload


@pytest.mark.parametrize('filter_type', [
    'background_remover',
    'outpaint',
    'resizeEdge',
    'resizeFree',
])
def test_geometry_or_alpha_owning_filters_keep_direct_rgba_dispatch(monkeypatch, filter_type) -> None:
    image = rgba_image()
    settings = {'sentinel': filter_type}
    processed = torch.rand((1, 4, 5, 4), generator=torch.Generator().manual_seed(4))
    payload = {'owner': filter_type}
    calls = []

    def fake_processor(supplied_image, supplied_settings):
        calls.append((supplied_image, supplied_settings))
        return processed, payload

    monkeypatch.setitem(processors.FILTER_PROCESSORS, filter_type, fake_processor)
    result, actual_payload = processors.process_filter(filter_type, image, settings)

    assert calls == [(image, settings)]
    assert result is processed
    assert actual_payload is payload


def test_rgba_adapter_is_an_explicit_geometry_preserving_allowlist() -> None:
    assert processors.RGBA_RGB_PROCESSORS == frozenset({
        'blend',
        'bloom',
        'brightness',
        'brush',
        'clarity',
        'contrast',
        'desaturate',
        'film_grain',
        'gaussian_blur',
        'inpaint',
        'line',
        'saturation',
        'sepia',
        'split_tone',
        'tilt_shift',
        'unsharp_mask',
        'vibrance',
        'vignette',
    })


def test_rgba_adapter_fails_closed_if_a_supported_filter_changes_geometry(monkeypatch) -> None:
    monkeypatch.setitem(
        processors.FILTER_PROCESSORS,
        'inpaint',
        lambda _image, _settings: (torch.zeros((1, 3, 3, 3)), {'unexpected': True}),
    )

    with pytest.raises(ValueError, match='original RGB geometry'):
        processors.process_filter('inpaint', rgba_image(), {})
