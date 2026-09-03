"""Real CPU palette/tracer regressions; no Comfy service or source files needed."""

from __future__ import annotations

import importlib
import xml.etree.ElementTree as ET

import numpy as np
import pytest

pytest.importorskip("vtracer")
pytest.importorskip("svgwrite")
svg_helper = importlib.import_module("modules.utils.helpers.conversion.numpy_to_svg")


@pytest.fixture
def textured_icon() -> np.ndarray:
    # Most pixels are slightly different near-whites. A frequency-driven median
    # cut spends its small palette on those whites and merges both foregrounds.
    rows, columns = np.indices((96, 96))
    image = np.stack(
        (243 + columns % 3, 247 + rows % 3, 244 + (columns + rows) % 2),
        axis=-1,
    ).astype(np.uint8)
    image[12:40, 35:63] = (212, 85, 28)
    image[61:81, 22:72] = (27, 25, 27)
    return image


def _config(num_colors: int = 3):
    return svg_helper.SVGTraceConfig(
        engine="vtracer",
        num_colors=num_colors,
        mask_blur=0,
        mask_close_iters=0,
        vtracer_filter_speckle=0,
    )


def test_small_palette_preserves_distinct_foregrounds_on_textured_background(
    textured_icon,
) -> None:
    svg, preview, palette = svg_helper.numpy_to_svg(textured_icon, _config())

    np.testing.assert_array_equal(preview[25, 49], (212, 85, 28))
    np.testing.assert_array_equal(preview[70, 46], (27, 25, 27))
    assert preview[0, 0].min() > 235
    assert len(np.unique(preview.reshape(-1, 3), axis=0)) == 3
    assert {"#d4551c", "#1b191b"} <= set(palette)
    fills = {
        element.attrib["fill"].lower()
        for element in ET.fromstring(svg).iter()
        if "fill" in element.attrib
    }
    assert {"#d4551c", "#1b191b"} <= fills


@pytest.mark.parametrize("num_colors", (1, 2, 3, 8, 256))
def test_palette_cap_and_determinism_preserve_input(textured_icon, num_colors) -> None:
    original = textured_icon.copy()
    first_svg, first_preview, first_palette = svg_helper.numpy_to_svg(
        textured_icon, _config(num_colors),
    )
    second_svg, second_preview, second_palette = svg_helper.numpy_to_svg(
        textured_icon, _config(num_colors),
    )

    assert first_svg == second_svg
    assert first_palette == second_palette
    np.testing.assert_array_equal(first_preview, second_preview)
    np.testing.assert_array_equal(textured_icon, original)
    assert first_preview.shape == textured_icon.shape
    assert first_preview.dtype == np.uint8
    assert 1 <= len(np.unique(first_preview.reshape(-1, 3), axis=0)) <= num_colors
    assert 1 <= len(first_palette) <= num_colors
    assert ET.fromstring(first_svg).tag == "{http://www.w3.org/2000/svg}svg"


def test_mask_still_sets_tracer_alpha_and_blacks_out_excluded_preview(
    monkeypatch, textured_icon,
) -> None:
    mask = np.zeros(textured_icon.shape[:2], dtype=np.float32)
    mask[12:40, 35:63] = 1
    mask[61:81, 22:72] = 1
    original_mask = mask.copy()
    captured = []
    real_trace = svg_helper.vtracer.convert_pixels_to_svg

    def capture_trace(**kwargs):
        width, height = kwargs["size"]
        captured.append(
            np.asarray(kwargs["rgba_pixels"], dtype=np.uint8).reshape(height, width, 4)
        )
        return real_trace(**kwargs)

    monkeypatch.setattr(svg_helper.vtracer, "convert_pixels_to_svg", capture_trace)
    svg, preview, _palette = svg_helper.numpy_to_svg(
        textured_icon, _config(), mask=mask,
    )

    assert len(captured) == 1  # Exercise native vtracer, not the contour fallback.
    np.testing.assert_array_equal(captured[0][..., 3], mask.astype(np.uint8) * 255)
    np.testing.assert_array_equal(mask, original_mask)
    assert (preview[mask == 0] == 0).all()
    np.testing.assert_array_equal(preview[25, 49], (212, 85, 28))
    np.testing.assert_array_equal(preview[70, 46], (27, 25, 27))
    assert ET.fromstring(svg).tag == "{http://www.w3.org/2000/svg}svg"
