from __future__ import annotations

import sys
import types

from PIL import Image
import pytest
import torch

# Some focused Workflow Runner tests install a deliberately minimal constants
# stub at module scope. Discard that incomplete test double before importing the
# real image package so this suite remains independent of pytest collection order.
constants_module = sys.modules.get("modules.utils.constants")
if constants_module is not None and not hasattr(constants_module, "CATEGORY_PREFIX"):
    sys.modules.pop("modules.utils.constants", None)
helpers_module = sys.modules.get("modules.utils.helpers")
if helpers_module is not None and getattr(helpers_module, "__path__", None) == []:
    for module_name in tuple(sys.modules):
        if module_name == "modules.utils.helpers" or module_name.startswith(
            "modules.utils.helpers."
        ):
            sys.modules.pop(module_name, None)

# Keep this focused CPU tensor test independent from Comfy's optional CUDA
# sampler stack during module import.
if "comfy.samplers" not in sys.modules:
    comfy_samplers = types.ModuleType("comfy.samplers")
    comfy_samplers.KSampler = type(
        "KSampler",
        (),
        {"SAMPLERS": [], "SCHEDULERS": []},
    )
    sys.modules["comfy.samplers"] = comfy_samplers

from modules.nodes.image import normalize_sprite_batch as normalizer_module


@pytest.fixture
def preview_runtime(monkeypatch: pytest.MonkeyPatch, tmp_path):
    saved_paths = []
    sent = []

    def resolve_filepath(*, filename_prefix, image, temp_cache):
        del image, temp_cache
        path = tmp_path / f"{filename_prefix}_{len(saved_paths)}.png"
        saved_paths.append(path)
        return path, "", path.name

    monkeypatch.setattr(normalizer_module, "resolve_filepath", resolve_filepath)
    monkeypatch.setattr(
        normalizer_module,
        "get_resource_url",
        lambda subfolder, filename, storage_type: (
            f"/view?filename={filename}&type={storage_type}&subfolder={subfolder}"
        ),
    )
    monkeypatch.setattr(
        normalizer_module,
        "safe_send_sync",
        lambda event, payload, node_id: sent.append((event, payload, node_id)),
    )
    return {"saved_paths": saved_paths, "sent": sent}


def _rgba_batch(frame_count: int, height: int, width: int) -> torch.Tensor:
    return torch.zeros((frame_count, height, width, 4), dtype=torch.float32)


def _paint(
    batch: torch.Tensor,
    frame: int,
    *,
    left: int,
    top: int,
    right: int,
    bottom: int,
    color: tuple[float, float, float] = (1.0, 0.25, 0.0),
) -> None:
    batch[frame, top : bottom + 1, left : right + 1, :3] = torch.tensor(color)
    batch[frame, top : bottom + 1, left : right + 1, 3] = 1.0


def _bounds(frame: torch.Tensor) -> tuple[int, int, int, int]:
    positions = torch.nonzero(frame[..., 3] > 1.0 / 255.0, as_tuple=False)
    assert positions.numel() > 0
    return (
        int(positions[:, 1].min()),
        int(positions[:, 0].min()),
        int(positions[:, 1].max()),
        int(positions[:, 0].max()),
    )


def test_one_reference_scale_is_applied_to_the_whole_batch() -> None:
    source = _rgba_batch(2, 12, 12)
    _paint(source, 0, left=4, top=4, right=7, bottom=7)
    _paint(source, 1, left=2, top=2, right=7, bottom=7)

    output, receipt = normalizer_module.normalize_sprite_batch(
        source,
        canvas_width=32,
        canvas_height=32,
        target_reference_alpha_height=8,
        bottom_padding=2,
        reference_frame_index=0,
    )

    assert output.shape == (2, 32, 32, 4)
    assert receipt["uniformScale"] == {
        "numerator": 8,
        "denominator": 4,
        "resizedCanvasWidth": 24,
        "resizedCanvasHeight": 24,
        "filter": "bicubic_antialiased_premultiplied_alpha",
    }
    assert receipt["targetReferenceAlphaHeight"] == 8
    assert receipt["scaledReferenceAlphaBounds"]["height"] == (
        receipt["frames"][0]["scaledAlphaBounds"]["height"]
    )
    scaled_heights = [
        frame["scaledAlphaBounds"]["height"] for frame in receipt["frames"]
    ]
    assert scaled_heights[1] > scaled_heights[0]
    assert scaled_heights[1] / scaled_heights[0] == pytest.approx(1.5, abs=0.2)
    assert {
        frame["translation"]["x"] for frame in receipt["frames"]
    } == {receipt["horizontalPlacement"]["translation"]}


def test_shared_x_translation_preserves_cross_frame_horizontal_delta() -> None:
    source = _rgba_batch(2, 10, 16)
    _paint(source, 0, left=3, top=2, right=6, bottom=7)
    _paint(source, 1, left=7, top=2, right=10, bottom=7)

    output, receipt = normalizer_module.normalize_sprite_batch(
        source,
        canvas_width=48,
        canvas_height=20,
        target_reference_alpha_height=12,
        bottom_padding=1,
    )

    frame_0 = _bounds(output[0])
    frame_1 = _bounds(output[1])
    assert frame_1[0] - frame_0[0] == 8
    assert frame_1[2] - frame_0[2] == 8
    assert receipt["frames"][0]["translation"]["x"] == receipt["frames"][1][
        "translation"
    ]["x"]


def test_only_vertical_translation_varies_to_align_every_alpha_baseline() -> None:
    source = _rgba_batch(3, 12, 12)
    _paint(source, 0, left=4, top=2, right=7, bottom=6)
    _paint(source, 1, left=4, top=4, right=7, bottom=8)
    _paint(source, 2, left=4, top=6, right=7, bottom=10)

    output, receipt = normalizer_module.normalize_sprite_batch(
        source,
        canvas_width=16,
        canvas_height=16,
        target_reference_alpha_height=5,
        bottom_padding=3,
    )

    expected_baseline = 12
    assert [_bounds(frame)[3] for frame in output] == [expected_baseline] * 3
    assert receipt["baseline"] == {
        "policy": "per_frame_alpha_bottom",
        "bottomPadding": 3,
        "targetRow": expected_baseline,
    }
    assert [frame["translation"]["y"] for frame in receipt["frames"]] == [
        6,
        4,
        2,
    ]


def test_transparent_edges_and_rgba_are_preserved() -> None:
    source = _rgba_batch(1, 8, 8)
    _paint(source, 0, left=2, top=2, right=5, bottom=5)
    source[0, 2, 2, 3] = 0.5

    output, receipt = normalizer_module.normalize_sprite_batch(
        source,
        canvas_width=20,
        canvas_height=20,
        target_reference_alpha_height=8,
        bottom_padding=2,
    )

    assert output.shape[-1] == 4
    assert torch.count_nonzero(output[..., 3] == 0) > 0
    assert torch.all(output[..., :3][output[..., 3] == 0] == 0)
    assert torch.any((output[..., 3] > 0) & (output[..., 3] < 1))
    assert output[..., 3].max().item() == pytest.approx(1.0)
    assert receipt["source"]["channels"] == 4


@pytest.mark.parametrize(
    ("image", "message"),
    [
        (torch.zeros((1, 8, 8, 3)), "RGBA with 4 channels"),
        (torch.zeros((1, 8, 8, 4)), "empty alpha"),
    ],
)
def test_absent_or_empty_alpha_fails_clearly(
    image: torch.Tensor,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        normalizer_module.normalize_sprite_batch(
            image,
            canvas_width=16,
            canvas_height=16,
            target_reference_alpha_height=12,
            bottom_padding=2,
        )


def test_any_empty_frame_fails_instead_of_publishing_a_partial_batch() -> None:
    source = _rgba_batch(2, 8, 8)
    _paint(source, 0, left=2, top=2, right=5, bottom=5)

    with pytest.raises(ValueError, match="frame 1 has empty alpha"):
        normalizer_module.normalize_sprite_batch(
            source,
            canvas_width=16,
            canvas_height=16,
            target_reference_alpha_height=12,
            bottom_padding=2,
        )


def test_nonzero_reference_frame_owns_scale_and_horizontal_pivot() -> None:
    source = _rgba_batch(2, 12, 16)
    _paint(source, 0, left=1, top=2, right=4, bottom=9)
    _paint(source, 1, left=8, top=4, right=11, bottom=7)

    _output, receipt = normalizer_module.normalize_sprite_batch(
        source,
        canvas_width=40,
        canvas_height=28,
        target_reference_alpha_height=8,
        reference_frame_index=1,
        bottom_padding=4,
    )

    assert receipt["referenceFrameIndex"] == 1
    assert receipt["uniformScale"]["numerator"] == 8
    assert receipt["uniformScale"]["denominator"] == 4
    reference = receipt["frames"][1]["translatedAlphaBounds"]
    assert reference["left"] + reference["right"] in {38, 39, 40}
    assert {
        frame["translation"]["x"] for frame in receipt["frames"]
    } == {receipt["horizontalPlacement"]["translation"]}


def test_subthreshold_alpha_is_preserved_but_does_not_define_bounds() -> None:
    source = _rgba_batch(1, 8, 8)
    _paint(source, 0, left=3, top=2, right=4, bottom=5)
    source[0, 1, 1, :3] = 0.75
    source[0, 1, 1, 3] = 1.0 / 510.0

    output, receipt = normalizer_module.normalize_sprite_batch(
        source,
        canvas_width=12,
        canvas_height=12,
        target_reference_alpha_height=4,
        reference_frame_index=0,
        bottom_padding=2,
    )

    assert receipt["referenceAlphaBounds"]["left"] == 3
    assert output[..., 3].max().item() == pytest.approx(1.0)
    assert torch.any((output[..., 3] > 0) & (output[..., 3] <= 1.0 / 255.0))


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"reference_frame_index": 2}, "reference_frame_index"),
        ({"reference_frame_index": True}, "reference_frame_index"),
        ({"target_reference_alpha_height": True}, "target_reference_alpha_height"),
        (
            {"target_reference_alpha_height": 13, "bottom_padding": 4},
            "plus bottom_padding",
        ),
    ],
)
def test_invalid_geometry_options_fail_before_transform(
    overrides: dict,
    message: str,
) -> None:
    source = _rgba_batch(1, 8, 8)
    _paint(source, 0, left=2, top=2, right=5, bottom=5)
    options = {
        "canvas_width": 16,
        "canvas_height": 16,
        "target_reference_alpha_height": 8,
        "reference_frame_index": 0,
        "bottom_padding": 2,
        **overrides,
    }

    with pytest.raises(ValueError, match=message):
        normalizer_module.normalize_sprite_batch(source, **options)


def test_alpha_content_clipping_fails_instead_of_cropping_motion() -> None:
    source = _rgba_batch(2, 8, 20)
    _paint(source, 0, left=8, top=2, right=11, bottom=5)
    _paint(source, 1, left=16, top=2, right=19, bottom=5)

    with pytest.raises(ValueError, match=r"frame 1.*right"):
        normalizer_module.normalize_sprite_batch(
            source,
            canvas_width=16,
            canvas_height=16,
            target_reference_alpha_height=8,
            reference_frame_index=0,
            bottom_padding=2,
        )


def test_pixel_budgets_fail_before_large_allocations(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = _rgba_batch(2, 8, 8)
    _paint(source, 0, left=3, top=3, right=4, bottom=4)
    _paint(source, 1, left=3, top=3, right=4, bottom=4)
    monkeypatch.setattr(normalizer_module, "MAX_COMPOSITE_PIXELS", 300)

    with pytest.raises(ValueError, match="output batch"):
        normalizer_module.normalize_sprite_batch(
            source,
            canvas_width=16,
            canvas_height=16,
            target_reference_alpha_height=4,
            reference_frame_index=0,
            bottom_padding=2,
        )

    monkeypatch.setattr(normalizer_module, "MAX_COMPOSITE_PIXELS", 1_000)
    with pytest.raises(ValueError, match="resized intermediate batch"):
        normalizer_module.normalize_sprite_batch(
            source,
            canvas_width=16,
            canvas_height=16,
            target_reference_alpha_height=16,
            reference_frame_index=0,
            bottom_padding=0,
        )


def test_dense_alpha_bounds_reduce_to_rows_and_columns_before_nonzero(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = torch.ones((2, 64, 96, 4), dtype=torch.float32)
    original_nonzero = torch.nonzero
    inspected_shapes: list[tuple[int, ...]] = []

    def bounded_nonzero(value, *args, **kwargs):
        inspected_shapes.append(tuple(value.shape))
        assert value.ndim == 1
        return original_nonzero(value, *args, **kwargs)

    monkeypatch.setattr(normalizer_module.torch, "nonzero", bounded_nonzero)

    output, receipt = normalizer_module.normalize_sprite_batch(
        source,
        canvas_width=96,
        canvas_height=64,
        target_reference_alpha_height=64,
        reference_frame_index=0,
        bottom_padding=0,
    )

    assert output.shape == source.shape
    assert receipt["referenceAlphaBounds"]["width"] == 96
    assert inspected_shapes
    assert set(inspected_shapes) == {(64,), (96,)}


def test_node_publishes_masonry_history_without_requiring_widget(
    preview_runtime,
) -> None:
    source = _rgba_batch(2, 8, 8)
    _paint(source, 0, left=2, top=2, right=5, bottom=5)
    _paint(source, 1, left=3, top=2, right=6, bottom=5)

    response = normalizer_module.LF_NormalizeSpriteBatch().on_exec(
        image=source,
        canvas_width=16,
        canvas_height=16,
        target_reference_alpha_height=8,
        reference_frame_index=0,
        bottom_padding=2,
        node_id=["normalizer-9"],
    )

    normalized, receipt = response["result"]
    payload = response["ui"]["lf_output"][0]
    assert normalized.shape == (2, 16, 16, 4)
    assert payload["receipt"] is receipt
    assert payload["preview"] == {
        "displayedFrameIndices": [0, 1],
        "displayedFrameCount": 2,
        "totalFrameCount": 2,
        "truncated": False,
    }
    assert [
        node["cells"]["lfImage"]["htmlProps"]["title"]
        for node in payload["dataset"]["nodes"]
    ] == ["Normalized frame 0", "Normalized frame 1"]
    assert preview_runtime["sent"] == [
        ("normalizespritebatch", payload, "normalizer-9")
    ]
    assert len(preview_runtime["saved_paths"]) == 2
    for path in preview_runtime["saved_paths"]:
        with Image.open(path) as preview:
            assert preview.mode == "RGBA"
            assert preview.size == (16, 16)


def test_receipt_and_public_node_contract_are_deterministic_and_generic() -> None:
    source = _rgba_batch(1, 8, 8)
    _paint(source, 0, left=2, top=1, right=5, bottom=6)
    first_output, first = normalizer_module.normalize_sprite_batch(
        source,
        canvas_width=16,
        canvas_height=18,
        target_reference_alpha_height=10,
        bottom_padding=2,
    )
    second_output, second = normalizer_module.normalize_sprite_batch(
        source.clone(),
        canvas_width=16,
        canvas_height=18,
        target_reference_alpha_height=10,
        bottom_padding=2,
    )

    assert torch.equal(first_output, second_output)
    assert first == second
    assert first["schema"] == "lf.sprite_batch_normalizer.receipt.v1"
    assert first["boundsPolicy"] == (
        "all_alpha_content_including_props_and_shadows"
    )
    assert first["subthresholdAlphaPolicy"] == (
        "preserved_but_ignored_for_geometry"
    )
    assert first["contentClippingPolicy"] == "fail"
    assert first["targetHeightPolicy"] == (
        "nominal_scale_before_bicubic_rasterization"
    )
    schema = normalizer_module.LF_NormalizeSpriteBatch.INPUT_TYPES()
    assert list(schema["required"]) == [
        "image",
        "canvas_width",
        "canvas_height",
        "target_reference_alpha_height",
        "reference_frame_index",
        "bottom_padding",
    ]
    assert schema["required"]["reference_frame_index"][1]["default"] == 0
    assert schema["optional"]["ui_widget"][0] == "LF_MASONRY"
    assert schema["hidden"] == {"node_id": "UNIQUE_ID"}
    assert normalizer_module.LF_NormalizeSpriteBatch.OUTPUT_NODE is True
    assert normalizer_module.LF_NormalizeSpriteBatch.RETURN_TYPES == (
        "IMAGE",
        "JSON",
    )
    assert normalizer_module.NODE_CLASS_MAPPINGS == {
        "LF_NormalizeSpriteBatch": normalizer_module.LF_NormalizeSpriteBatch,
    }
    assert "garage" not in repr(schema).lower()
    assert "velora" not in repr(schema).lower()
