from __future__ import annotations

import math
import sys
import types
from types import SimpleNamespace

import pytest
import torch


# Keep the focused tensor suite independent from Comfy's optional sampler stack
# and from deliberately incomplete module stubs installed by other test files.
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

if "comfy.samplers" not in sys.modules:
    comfy_samplers = types.ModuleType("comfy.samplers")
    comfy_samplers.KSampler = type(
        "KSampler",
        (),
        {"SAMPLERS": [], "SCHEDULERS": []},
    )
    sys.modules["comfy.samplers"] = comfy_samplers

from modules.nodes.image import select_settled_image_frame as selector_module


def _constant_frames(
    values: list[float],
    *,
    height: int = 3,
    width: int = 4,
    channels: int = 3,
    dtype: torch.dtype = torch.float32,
) -> torch.Tensor:
    return (
        torch.tensor(values, dtype=dtype)
        .reshape(len(values), 1, 1, 1)
        .expand(-1, height, width, channels)
        .clone()
    )


@pytest.fixture
def preview_runtime(monkeypatch: pytest.MonkeyPatch):
    previews: list[torch.Tensor] = []
    sent: list[tuple[str, dict, object]] = []

    def cache_generated_preview(image: torch.Tensor):
        previews.append(image.clone())
        return SimpleNamespace(
            url="/view?filename=settled.png&type=input&subfolder=_lf_external_previews",
        )

    monkeypatch.setattr(
        selector_module,
        "cache_generated_preview",
        cache_generated_preview,
    )
    monkeypatch.setattr(
        selector_module,
        "safe_send_sync",
        lambda event, payload, node_id: sent.append((event, payload, node_id)),
    )
    return {"previews": previews, "sent": sent}


def test_selects_the_locally_least_moving_frame_in_the_tail() -> None:
    source = _constant_frames([0.0, 0.2, 0.8, 0.9, 0.91, 1.0])

    selected, selected_index, receipt = selector_module.select_settled_image_frame(
        source,
        tail_fraction=0.5,
        analysis_max_edge=96,
    )

    assert selected_index == 4
    assert torch.equal(selected, source[4:5])
    assert receipt["candidateRange"] == {"startIndex": 3, "endIndex": 5}
    assert receipt["tailFrameCount"] == 3
    assert [candidate["index"] for candidate in receipt["candidates"]] == [3, 4, 5]
    assert [candidate["score"] for candidate in receipt["candidates"]] == pytest.approx(
        [0.055, 0.05, 0.09],
        abs=1e-6,
    )
    assert receipt["analysis"]["frameScorePolicy"] == (
        "mean_available_adjacent_transition_scores"
    )


def test_exact_motion_score_ties_choose_the_latest_frame() -> None:
    source = _constant_frames([0.4, 0.4, 0.4, 0.4])

    _selected, selected_index, receipt = selector_module.select_settled_image_frame(
        source,
        tail_fraction=1.0,
        analysis_max_edge=8,
    )

    assert selected_index == 3
    assert receipt["selectedScore"] == 0.0
    assert receipt["analysis"]["tieBreak"] == "latest_frame"
    assert receipt["candidates"] == [
        {"index": 0, "score": 0.0},
        {"index": 1, "score": 0.0},
        {"index": 2, "score": 0.0},
        {"index": 3, "score": 0.0},
    ]


def test_tail_window_uses_ceiling_and_analysis_keeps_aspect_ratio() -> None:
    source = _constant_frames([0.0, 0.25, 0.5, 0.75, 1.0], height=20, width=40)

    _selected, _selected_index, receipt = selector_module.select_settled_image_frame(
        source,
        tail_fraction=0.5,
        analysis_max_edge=8,
    )

    assert receipt["tailFrameCount"] == 3
    assert receipt["candidateRange"] == {"startIndex": 2, "endIndex": 4}
    assert receipt["analysis"]["frameRange"] == {"startIndex": 1, "endIndex": 4}
    assert receipt["analysis"]["width"] == 8
    assert receipt["analysis"]["height"] == 4


def test_rgba_motion_ignores_invisible_rgb_but_preserves_exact_source_pixels() -> None:
    source = torch.zeros((3, 2, 3, 4), dtype=torch.float64)
    source[0, ..., :3] = 0.1
    source[1, ..., :3] = 0.9
    source[2, ..., :3] = 0.5

    selected, selected_index, receipt = selector_module.select_settled_image_frame(
        source,
        tail_fraction=1.0,
        analysis_max_edge=8,
    )

    assert selected_index == 2
    assert selected.dtype == torch.float64
    assert selected.shape == (1, 2, 3, 4)
    assert torch.equal(selected, source[2:3])
    assert receipt["analysis"]["metric"] == (
        "mean_absolute_rgb_or_premultiplied_rgba"
    )
    assert {candidate["score"] for candidate in receipt["candidates"]} == {0.0}


def test_nested_coherent_batches_are_one_ordered_sequence() -> None:
    source = _constant_frames([0.0, 0.5, 0.5, 0.5])

    selected, selected_index, receipt = selector_module.select_settled_image_frame(
        [source[:2], [source[2:]]],
        tail_fraction=1.0,
        analysis_max_edge=8,
    )

    assert selected_index == 3
    assert torch.equal(selected, source[3:4])
    assert receipt["source"]["frameCount"] == 4


def test_one_frame_is_a_valid_settled_sequence() -> None:
    source = torch.rand((1, 7, 9, 3))

    selected, selected_index, receipt = selector_module.select_settled_image_frame(
        source,
        tail_fraction=0.25,
        analysis_max_edge=16,
    )

    assert selected_index == 0
    assert torch.equal(selected, source)
    assert receipt["selectedScore"] == 0.0
    assert receipt["candidates"] == [{"index": 0, "score": 0.0}]


@pytest.mark.parametrize(
    "image",
    [
        None,
        [],
        [None, []],
    ],
)
def test_empty_image_input_fails_clearly(image) -> None:
    with pytest.raises(ValueError, match="at least one RGB or RGBA frame"):
        selector_module.select_settled_image_frame(
            image,
            tail_fraction=0.25,
            analysis_max_edge=96,
        )


def test_zero_frame_tensor_fails_clearly() -> None:
    with pytest.raises(ValueError, match="batch must contain at least one image"):
        selector_module.select_settled_image_frame(
            torch.empty((0, 4, 4, 3)),
            tail_fraction=0.25,
            analysis_max_edge=96,
        )


@pytest.mark.parametrize(
    "image",
    [
        [torch.zeros((1, 4, 4, 3)), torch.zeros((1, 5, 4, 3))],
        [torch.zeros((1, 4, 4, 3)), torch.zeros((1, 4, 4, 4))],
        [
            torch.zeros((1, 4, 4, 3), dtype=torch.float32),
            torch.zeros((1, 4, 4, 3), dtype=torch.float64),
        ],
    ],
)
def test_heterogeneous_sequences_fail_instead_of_silently_converting(image) -> None:
    with pytest.raises(ValueError, match="one coherent sequence"):
        selector_module.select_settled_image_frame(
            image,
            tail_fraction=0.25,
            analysis_max_edge=96,
        )


@pytest.mark.parametrize("tail_fraction", [0, -0.1, 1.01, True, math.nan, math.inf])
def test_invalid_tail_fraction_fails_clearly(tail_fraction) -> None:
    with pytest.raises(ValueError, match="tail_fraction"):
        selector_module.select_settled_image_frame(
            _constant_frames([0.0, 1.0]),
            tail_fraction=tail_fraction,
            analysis_max_edge=96,
        )


@pytest.mark.parametrize("analysis_max_edge", [7, 1025, True, 96.0, "96"])
def test_invalid_analysis_resolution_fails_clearly(analysis_max_edge) -> None:
    with pytest.raises(ValueError, match="analysis_max_edge"):
        selector_module.select_settled_image_frame(
            _constant_frames([0.0, 1.0]),
            tail_fraction=0.25,
            analysis_max_edge=analysis_max_edge,
        )


def test_nonfinite_tail_pixels_fail_before_scoring() -> None:
    source = _constant_frames([0.0, 0.5, 1.0])
    source[-1, 0, 0, 0] = math.nan

    with pytest.raises(ValueError, match="NaN or infinite"):
        selector_module.select_settled_image_frame(
            source,
            tail_fraction=0.5,
            analysis_max_edge=8,
        )


def test_receipt_is_deterministic_and_declares_no_semantic_validation() -> None:
    source = _constant_frames([0.0, 0.2, 0.4, 0.4])

    first = selector_module.select_settled_image_frame(
        source,
        tail_fraction=0.75,
        analysis_max_edge=8,
    )[2]
    second = selector_module.select_settled_image_frame(
        source,
        tail_fraction=0.75,
        analysis_max_edge=8,
    )[2]

    assert first == second
    assert first["schema"] == "lf.select_settled_image_frame.receipt.v1"
    assert first["semanticValidation"] == "none"
    assert "angle" not in first


def test_node_publishes_restart_stable_preview_and_authoritative_image_list(
    preview_runtime,
) -> None:
    source = _constant_frames([0.0, 0.75, 0.75])

    response = selector_module.LF_SelectSettledImageFrame().on_exec(
        image=[source],
        tail_fraction=[1.0],
        analysis_max_edge=[8],
        node_id=["selector-4"],
    )

    selected, image_list, selected_index, receipt = response["result"]
    payload = response["ui"]["lf_output"][0]
    assert selected_index == 2
    assert len(image_list) == 1
    assert image_list[0] is selected
    assert torch.equal(selected, source[2:3])
    assert payload["receipt"] is receipt
    assert payload["dataset"]["nodes"][0]["cells"]["lfImage"]["htmlProps"] == {
        "id": "Selected frame 2",
        "title": "Selected frame 2",
    }
    assert payload["dataset"]["nodes"][0]["cells"]["lfImage"][
        "lfValue"
    ].startswith("/view?")
    assert preview_runtime["sent"] == [
        ("selectsettledimageframe", payload, "selector-4")
    ]
    assert len(preview_runtime["previews"]) == 1
    assert torch.equal(preview_runtime["previews"][0], selected)


def test_node_schema_and_public_mappings_are_exact_and_domain_neutral() -> None:
    node_class = selector_module.LF_SelectSettledImageFrame
    schema = node_class.INPUT_TYPES()

    assert list(schema["required"]) == [
        "image",
        "tail_fraction",
        "analysis_max_edge",
    ]
    assert schema["required"]["tail_fraction"][1]["default"] == 0.25
    assert schema["required"]["analysis_max_edge"][1]["default"] == 96
    assert schema["optional"] == {"ui_widget": ("LF_MASONRY", {"default": {}})}
    assert schema["hidden"] == {"node_id": "UNIQUE_ID"}
    assert node_class.INPUT_IS_LIST is True
    assert node_class.OUTPUT_NODE is True
    assert node_class.RETURN_TYPES == ("IMAGE", "IMAGE", "INT", "JSON")
    assert node_class.RETURN_NAMES == (
        "image",
        "image_list",
        "selected_index",
        "receipt",
    )
    assert node_class.OUTPUT_IS_LIST == (False, True, False, False)
    assert selector_module.NODE_CLASS_MAPPINGS == {
        "LF_SelectSettledImageFrame": node_class,
    }
    assert selector_module.NODE_DISPLAY_NAME_MAPPINGS == {
        "LF_SelectSettledImageFrame": "Select settled image frame",
    }
    public_contract = repr(schema).lower()
    assert "velora" not in public_contract
    assert "eden" not in public_contract
    assert "h3" not in public_contract


def test_tooltips_are_honest_about_motion_only_selection() -> None:
    node_class = selector_module.LF_SelectSettledImageFrame
    schema_text = repr(node_class.INPUT_TYPES()).lower()
    output_text = repr(node_class.OUTPUT_TOOLTIPS).lower()

    assert "measures image change only" in schema_text
    assert "does not recognize" in schema_text
    assert "semantic validation" in output_text
