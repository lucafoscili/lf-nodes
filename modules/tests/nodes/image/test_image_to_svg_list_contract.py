from __future__ import annotations

import numpy as np
import torch

from modules.nodes.image import image_to_svg


def test_image_to_svg_published_schema_is_unchanged() -> None:
    node = image_to_svg.LF_ImageToSVG
    # Tooltips are observational; freeze serialized controls, bounds, placement,
    # and order independently of the constants used by the implementation.
    schema = {
        section: {
            name: declaration if isinstance(declaration, str) else (
                declaration[0],
                {key: value for key, value in declaration[1].items() if key != "tooltip"},
            )
            for name, declaration in inputs.items()
        }
        for section, inputs in node.INPUT_TYPES().items()
    }
    expected = {
        "required": {
            "image": ("IMAGE", {}),
            "preset": (
                ["max_quality", "high_quality", "balanced", "max_speed", "custom"],
                {"default": "max_quality"},
            ),
        },
        "optional": {
            "mask": ("MASK", {}),
            "advanced_config": ("JSON", {"default": {}}),
            "render_mode": (["preset", "fill", "stroke", "both"], {"default": "preset"}),
            "fill_color": ("STRING", {"default": ""}),
            "stroke_color": ("STRING", {"default": ""}),
            "background_color": ("STRING", {"default": ""}),
            "stroke_width": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 10.0, "step": 0.1}),
            "size_mode": (["preset", "responsive", "fixed"], {"default": "preset"}),
            "viewbox": ("STRING", {"default": ""}),
            "ui_widget": ("LF_COMPARE", {"default": {}}),
        },
        "hidden": {"node_id": "UNIQUE_ID"},
    }
    assert schema == expected
    assert list(schema) == list(expected)
    for section in expected:
        assert list(schema[section]) == list(expected[section])
    assert image_to_svg.NODE_CLASS_MAPPINGS == {"LF_ImageToSVG": node}
    assert node.RETURN_TYPES == ("STRING", "STRING", "IMAGE", "IMAGE", "STRING", "STRING")
    assert node.RETURN_NAMES == ("svg", "svg_list", "image", "image_list", "palette", "palette_list")
    assert node.OUTPUT_IS_LIST == (False, True, False, True, False, True)
    assert node.INPUT_IS_LIST is True
    assert getattr(node, "OUTPUT_NODE", False) is False
    assert node.FUNCTION == "on_exec"


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
