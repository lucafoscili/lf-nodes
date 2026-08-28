from __future__ import annotations

import numpy as np
import torch

from modules.nodes.image import image_to_svg


def test_image_to_svg_owns_image_mask_pairing_in_true_list_mode(
    monkeypatch,
) -> None:
    images = torch.stack(
        (
            torch.full((2, 3, 3), 0.2),
            torch.full((2, 3, 3), 0.8),
        )
    )
    masks = torch.stack((torch.zeros((2, 3)), torch.ones((2, 3))))
    seen_masks = []

    def fake_vectorize(array, _config, *, mask):
        seen_masks.append(float(mask.mean()))
        return f"<svg>{float(array.mean()):.1f}</svg>", array, ["#000000"]

    monkeypatch.setattr(image_to_svg, "numpy_to_svg", fake_vectorize)
    monkeypatch.setattr(
        image_to_svg,
        "create_cached_compare_node",
        lambda *_args, **_kwargs: {"id": "compare"},
    )
    monkeypatch.setattr(image_to_svg, "safe_send_sync", lambda *_args: None)

    response = image_to_svg.LF_ImageToSVG().on_exec(
        image=[images],
        mask=[masks],
        preset=["max_speed"],
        advanced_config=[{}],
        render_mode=["preset"],
        fill_color=[""],
        stroke_color=[""],
        background_color=[""],
        stroke_width=[0.0],
        size_mode=["preset"],
        viewbox=[""],
    )
    svg, svg_list, _primary, image_list, _palette, palette_list = response[
        "result"
    ]

    assert image_to_svg.LF_ImageToSVG.INPUT_IS_LIST is True
    assert seen_masks == [0.0, 1.0]
    assert svg == svg_list[0]
    assert len(svg_list) == len(image_list) == len(palette_list) == 2
