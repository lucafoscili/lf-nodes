from __future__ import annotations

from collections.abc import Callable

import pytest
import torch

from modules.utils.filters import (
    bloom_effect,
    brightness_effect,
    clarity_effect,
    contrast_effect,
    desaturate_effect,
    film_grain_effect,
    gaussian_blur_effect,
    line_effect,
    saturation_effect,
    sepia_effect,
    split_tone_effect,
    tilt_shift_effect,
    unsharp_mask_effect,
    vibrance_effect,
    vignette_effect,
)


FilterCall = Callable[[torch.Tensor], torch.Tensor]


@pytest.mark.parametrize(
    "apply_filter",
    [
        pytest.param(
            lambda image: bloom_effect(image, 1.0, 3, 0.6),
            id="bloom",
        ),
        pytest.param(
            lambda image: brightness_effect(image, 0.0, 1.0, 0.5, False),
            id="brightness",
        ),
        pytest.param(
            lambda image: clarity_effect(image, 0.0, 0.0, 3),
            id="clarity",
        ),
        pytest.param(
            lambda image: contrast_effect(image, 0.0, 0.5, False),
            id="contrast",
        ),
        pytest.param(
            lambda image: desaturate_effect(image, 0.5, [1.0, 1.0, 1.0]),
            id="desaturate",
        ),
        pytest.param(
            lambda image: film_grain_effect(image, 0.0, 1.0),
            id="film-grain",
        ),
        pytest.param(
            lambda image: gaussian_blur_effect(image, 3, 1.0),
            id="gaussian-blur",
        ),
        pytest.param(
            lambda image: line_effect(
                image,
                [(0.1, 0.1), (0.8, 0.8)],
                1,
                "FFFFFF",
                1.0,
                False,
            ),
            id="line",
        ),
        pytest.param(
            lambda image: saturation_effect(image, 1.0),
            id="saturation",
        ),
        pytest.param(lambda image: sepia_effect(image, 0.5), id="sepia"),
        pytest.param(
            lambda image: split_tone_effect(
                image,
                "000000",
                "FFFFFF",
                0.5,
                0.2,
                0.5,
            ),
            id="split-tone",
        ),
        pytest.param(
            lambda image: tilt_shift_effect(image, 0.5, 0.5, 3),
            id="tilt-shift",
        ),
        pytest.param(
            lambda image: unsharp_mask_effect(image, 0.5, 3, 1.0, 0.0),
            id="unsharp-mask",
        ),
        pytest.param(
            lambda image: vibrance_effect(image, 0.2, False, True),
            id="vibrance",
        ),
        pytest.param(
            lambda image: vignette_effect(image, 0.5, 0.5, "elliptical"),
            id="vignette",
        ),
    ],
)
def test_shared_image_filters_return_strict_single_image_bhwc(
    apply_filter: FilterCall,
) -> None:
    image = torch.linspace(0.0, 1.0, 8 * 10 * 3, dtype=torch.float32).reshape(
        1,
        8,
        10,
        3,
    )

    result = apply_filter(image)

    assert result.shape == image.shape
    assert result.dtype == image.dtype
    assert result.device == image.device
    assert torch.isfinite(result).all()
