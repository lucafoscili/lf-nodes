from __future__ import annotations

from types import SimpleNamespace

from PIL import Image
import pytest
import torch

from modules.nodes.image import side_by_side as side_by_side_module


def _solid(
    height: int,
    width: int,
    color: tuple[float, ...],
    *,
    batch: int = 1,
) -> torch.Tensor:
    image = torch.zeros(batch, height, width, len(color), dtype=torch.float32)
    for channel, value in enumerate(color):
        image[..., channel] = value
    return image


def test_composite_scales_to_taller_input_and_inserts_exact_gap() -> None:
    image_a = _solid(2, 4, (1.0, 0.0, 0.0))
    image_b = _solid(4, 2, (0.0, 0.0, 1.0))

    composite = side_by_side_module.compose_side_by_side(
        image_a,
        image_b,
        gap_px=8,
    )

    assert composite.shape == (1, 4, 18, 3)
    torch.testing.assert_close(composite[:, :, :8], _solid(4, 8, (1.0, 0.0, 0.0)))
    torch.testing.assert_close(composite[:, :, 8:16], torch.zeros(1, 4, 8, 3))
    torch.testing.assert_close(composite[:, :, 16:], _solid(4, 2, (0.0, 0.0, 1.0)))


def test_max_height_caps_both_panes_and_widths_round_half_up() -> None:
    image_a = _solid(4, 8, (1.0, 0.0, 0.0))
    image_b = _solid(2, 3, (0.0, 1.0, 0.0))

    composite = side_by_side_module.compose_side_by_side(
        image_a,
        image_b,
        gap_px=2,
        max_height=3,
    )

    # A becomes 6x3; B's exact width is 4.5 and deliberately rounds up to 5.
    assert composite.shape == (1, 3, 13, 3)


def test_rgba_is_preserved_and_rgb_partner_and_gap_become_opaque() -> None:
    image_a = _solid(2, 2, (1.0, 0.0, 0.0))
    image_b = _solid(2, 2, (0.0, 1.0, 0.0, 0.25))

    composite = side_by_side_module.compose_side_by_side(
        image_a,
        image_b,
        gap_px=1,
    )

    assert composite.shape == (1, 2, 5, 4)
    torch.testing.assert_close(composite[..., :2, 3], torch.ones(1, 2, 2))
    torch.testing.assert_close(composite[..., 2, :3], torch.zeros(1, 2, 3))
    torch.testing.assert_close(composite[..., 2, 3], torch.ones(1, 2))
    torch.testing.assert_close(composite[..., 3:, 3], torch.full((1, 2, 2), 0.25))


def test_rgba_resize_uses_premultiplied_alpha_without_transparent_color_halos() -> None:
    image_a = torch.tensor(
        [[[[1.0, 0.0, 0.0, 1.0], [0.0, 0.0, 1.0, 0.0]]]],
        dtype=torch.float32,
    )
    image_b = _solid(4, 1, (0.0, 0.0, 0.0))

    composite = side_by_side_module.compose_side_by_side(
        image_a,
        image_b,
        gap_px=0,
    )

    resized_a = composite[:, :, :8]
    transparent = resized_a[..., 3] <= 1e-6
    assert bool(transparent.any())
    assert torch.count_nonzero(resized_a[..., :3][transparent]) == 0


def test_labels_are_burned_into_the_correct_panes_deterministically() -> None:
    image_a = _solid(80, 100, (0.0, 0.0, 0.0))
    image_b = _solid(80, 100, (0.0, 0.0, 0.0))
    options = {
        "gap_px": 8,
        "show_labels": True,
        "label_a": "LEFT",
        "label_b": "RIGHT",
    }

    first = side_by_side_module.compose_side_by_side(image_a, image_b, **options)
    second = side_by_side_module.compose_side_by_side(image_a, image_b, **options)
    unlabeled = side_by_side_module.compose_side_by_side(image_a, image_b, gap_px=8)

    torch.testing.assert_close(first, second)
    assert torch.count_nonzero(unlabeled) == 0
    assert float(first[:, :, :100].max()) > 0.5
    assert float(first[:, :, 108:].max()) > 0.5
    assert torch.count_nonzero(first[:, :, 100:108]) == 0


def test_singleton_batches_broadcast_and_preserve_pair_order() -> None:
    image_a = torch.cat(
        (
            _solid(2, 2, (1.0, 0.0, 0.0)),
            _solid(2, 2, (0.0, 1.0, 0.0)),
        ),
        dim=0,
    )
    image_b = _solid(2, 2, (0.0, 0.0, 1.0))

    composite = side_by_side_module.compose_side_by_side(
        image_a,
        image_b,
        gap_px=0,
    )

    assert composite.shape == (2, 2, 4, 3)
    torch.testing.assert_close(composite[0, :, :2], image_a[0])
    torch.testing.assert_close(composite[1, :, :2], image_a[1])
    torch.testing.assert_close(composite[:, :, 2:], image_b.expand(2, -1, -1, -1))


def test_incompatible_batches_and_invalid_inputs_fail_closed() -> None:
    with pytest.raises(ValueError, match="batch sizes must match"):
        side_by_side_module.compose_side_by_side(
            torch.rand(2, 4, 4, 3),
            torch.rand(3, 4, 4, 3),
        )

    with pytest.raises(ValueError, match=r"3 \(RGB\) or 4 \(RGBA\)"):
        side_by_side_module.compose_side_by_side(
            torch.rand(1, 4, 4, 1),
            torch.rand(1, 4, 4, 3),
        )

    non_finite = torch.rand(1, 4, 4, 3)
    non_finite[0, 0, 0, 0] = float("nan")
    with pytest.raises(ValueError, match="NaN or infinite"):
        side_by_side_module.compose_side_by_side(
            non_finite,
            torch.rand(1, 4, 4, 3),
        )

    with pytest.raises(ValueError, match="gap_px must be greater than or equal to 0"):
        side_by_side_module.compose_side_by_side(
            torch.rand(1, 4, 4, 3),
            torch.rand(1, 4, 4, 3),
            gap_px=-1,
        )

    with pytest.raises(ValueError, match="max_height must be an integer"):
        side_by_side_module.compose_side_by_side(
            torch.rand(1, 4, 4, 3),
            torch.rand(1, 4, 4, 3),
            max_height=12.5,
        )


def test_node_publishes_durable_masonry_history_without_requiring_widget(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    node = side_by_side_module.LF_SideBySide()
    saved_paths = []

    def cache_generated_preview(image):
        path = tmp_path / f"preview_{len(saved_paths)}.png"
        saved_paths.append(path)
        pixels = image[0].clamp(0, 1).mul(255).round().to(torch.uint8).numpy()
        Image.fromarray(pixels).save(path, format="PNG")
        return SimpleNamespace(
            url=f"/view?filename={path.name}&type=input&subfolder=preview",
        )

    sent = []
    monkeypatch.setattr(
        side_by_side_module,
        "cache_generated_preview",
        cache_generated_preview,
    )
    monkeypatch.setattr(
        side_by_side_module,
        "safe_send_sync",
        lambda event, payload, node_id: sent.append((event, payload, node_id)),
    )

    response = node.on_exec(
        image_a=_solid(3, 2, (1.0, 0.0, 0.0)),
        image_b=_solid(3, 2, (0.0, 1.0, 0.0, 0.5), batch=2),
        gap_px=1,
    )

    composite = response["result"][0]
    image_list = response["result"][1]
    dataset = response["ui"]["lf_output"][0]["dataset"]
    assert composite.shape == (2, 3, 5, 4)
    assert len(image_list) == 2
    assert torch.equal(torch.cat(image_list, dim=0), composite)
    assert len(dataset["nodes"]) == 2
    assert all(
        "type=input" in node["cells"]["lfImage"]["lfValue"]
        for node in dataset["nodes"]
    )
    assert sent == [("sidebyside", {"dataset": dataset}, None)]
    assert len(saved_paths) == 2
    for path in saved_paths:
        with Image.open(path) as preview:
            assert preview.mode == "RGBA"
            assert preview.size == (5, 3)


def test_public_schema_and_mapping_remain_generic() -> None:
    schema = side_by_side_module.LF_SideBySide.INPUT_TYPES()

    assert set(schema["required"]) == {
        "image_a",
        "image_b",
        "gap_px",
        "max_height",
        "show_labels",
        "label_a",
        "label_b",
    }
    assert schema["optional"]["ui_widget"][0] == "LF_MASONRY"
    assert schema["hidden"] == {"node_id": "UNIQUE_ID"}
    assert side_by_side_module.LF_SideBySide.INPUT_IS_LIST is True
    assert side_by_side_module.LF_SideBySide.RETURN_TYPES == ("IMAGE", "IMAGE")
    assert side_by_side_module.LF_SideBySide.RETURN_NAMES == (
        "image",
        "image_list",
    )
    assert side_by_side_module.LF_SideBySide.OUTPUT_IS_LIST == (False, True)
    assert side_by_side_module.NODE_CLASS_MAPPINGS == {
        "LF_SideBySide": side_by_side_module.LF_SideBySide,
    }
    assert side_by_side_module.NODE_DISPLAY_NAME_MAPPINGS == {
        "LF_SideBySide": "Side by side",
    }
    public_contract = repr(schema).lower()
    assert "velora" not in public_contract
    assert "stellaris" not in public_contract
    assert "azeroth" not in public_contract
