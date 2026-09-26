"""Offline graph/configuration contracts for the MiniMax H3 Prompt Maker."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys
import types
from typing import Any

import pytest


# Workflow declaration tests do not need Comfy's torch/xformers startup.
constants_module = types.ModuleType("modules.utils.constants")
constants_module.API_ROUTE_PREFIX = "/api/lf-nodes"
helpers_module = types.ModuleType("modules.utils.helpers")
helpers_module.__path__ = []  # type: ignore[attr-defined]
conversion_module = types.ModuleType("modules.utils.helpers.conversion")
conversion_module.json_safe = lambda value: value
sys.modules.setdefault("modules.utils.constants", constants_module)
sys.modules.setdefault("modules.utils.helpers", helpers_module)
sys.modules.setdefault("modules.utils.helpers.conversion", conversion_module)

from modules.workflow_runner.services.registry import InputValidationError
from modules.workflow_runner.workflows import _WORKFLOW_MODULES
from modules.workflow_runner.workflows import minimax_h3_prompt_maker as workflow_module


WORKFLOW = workflow_module.WORKFLOW
PICTURE_IDS = tuple(f"picture_{ordinal}" for ordinal in range(1, 10))


def _inputs(mode: str, reference_count: int) -> dict[str, Any]:
    return {
        "mode": mode,
        "intent": "A crane crosses a misty harbor while its bell rings once.",
        "duration": "7.5",
        **{
            f"picture_{ordinal}": [Path(f"C:/uploads/picture-{ordinal}.png")]
            for ordinal in range(1, reference_count + 1)
        },
        "endpoint": " http://127.0.0.1:1234/api/v1/chat ",
        "model": " vision-writer ",
        "temperature": "0.3",
        "reasoning": "off",
    }


def _configure(
    monkeypatch: pytest.MonkeyPatch,
    mode: str,
    reference_count: int,
) -> tuple[dict[str, Any], list[str]]:
    resolved: list[str] = []

    def resolve(inputs: dict[str, Any], name: str) -> str:
        resolved.append(name)
        assert inputs[name] == [
            Path(f"C:/uploads/picture-{name.removeprefix('picture_')}.png")
        ]
        return f"staged/{name}.png [input]"

    monkeypatch.setattr(workflow_module, "resolve_load_image_reference", resolve)
    graph = WORKFLOW.load_prompt()
    WORKFLOW.configure_prompt(graph, _inputs(mode, reference_count))
    return graph, resolved


def test_card_is_registered_and_exposes_the_small_standalone_contract() -> None:
    assert "minimax_h3_prompt_maker" in _WORKFLOW_MODULES
    assert WORKFLOW.id == "minimax_h3_prompt_maker"
    assert WORKFLOW.value == "MiniMax H3 / Prompt Maker"
    assert WORKFLOW.category == "MiniMax H3"
    assert WORKFLOW.card is not None
    assert WORKFLOW.card.hero is None
    assert [cell.id for cell in WORKFLOW.inputs] == [
        "mode",
        "intent",
        "duration",
        *PICTURE_IDS[:2],
        "model",
        "review",
        "endpoint",
        "temperature",
        "reasoning",
        "instructions",
        *PICTURE_IDS[2:],
    ]
    assert [cell.id for cell in WORKFLOW.outputs] == [
        "prompt",
        "validation_report",
        "visual_inventory",
    ]


def test_picture_and_transport_controls_have_the_required_progressive_disclosure() -> None:
    cells = {cell.id: cell for cell in WORKFLOW.inputs}

    assert all(cells[name].shape == "upload" for name in PICTURE_IDS)
    assert all(not cells[name].required for name in PICTURE_IDS)
    assert all(not cells[name].advanced for name in PICTURE_IDS[:2])
    assert all(cells[name].advanced for name in PICTURE_IDS[2:])
    assert all(cells[name].required for name in ("mode", "intent", "duration"))
    assert cells["duration"].props["lfHtmlAttributes"] == {
        "autocomplete": "off",
        "max": 5_999.999,
        "min": 0.001,
        "name": "duration",
        "step": 0.001,
        "type": "number",
    }
    assert all(
        cells[name].advanced
        for name in (
            "endpoint",
            "temperature",
            "reasoning",
        )
    )
    assert not cells["model"].required
    assert cells["model"].advanced
    assert cells["mode"].advanced
    assert cells["mode"].props["lfValue"] == "auto"
    assert cells["instructions"].advanced
    assert not cells["instructions"].required
    assert cells["review"].shape == "toggle"
    assert cells["review"].value == "Review"
    assert cells["review"].props == {"lfLabel": "Review", "lfValue": True}
    assert not cells["review"].advanced
    assert all(
        not cells[name].required
        for name in (
            "model",
            "review",
            "endpoint",
            "temperature",
            "reasoning",
        )
    )
    assert cells["endpoint"].props["lfValue"].endswith("/api/v1/chat")
    assert cells["temperature"].props["lfHtmlAttributes"]["max"] == 1.0
    assert cells["reasoning"].props["lfValue"] == "vision"
    assert [
        option["workflowValue"]
        for option in cells["reasoning"].props["lfDataset"]["nodes"]
    ] == ["vision", "off", "auto", "on"]
    assert [
        option["workflowValue"]
        for option in cells["mode"].props["lfDataset"]["nodes"]
    ] == ["auto", "t2va", "i2va", "fl2va", "l2va", "ref2va"]
    assert all(
        cells[name].node_id == "h3_prompt_maker"
        for name in (
            "mode",
            "intent",
            "duration",
            "model",
            "review",
            "endpoint",
            "temperature",
            "reasoning",
        )
    )


def test_graph_uses_one_public_atomic_h3_prompt_maker() -> None:
    graph = WORKFLOW.load_prompt()

    assert graph["h3_prompt_maker"] == {
        "inputs": {
            "intent": (
                "Create a cinematic video with clear action, coherent camera "
                "movement, and synchronized environmental sound."
            ),
            "mode": "auto",
            "instructions": "",
            "duration_seconds": 6.0,
            "url": "http://127.0.0.1:1234/api/v1/chat",
            "image": ["image_list", 0],
            "model": "",
            "temperature": 0.2,
            "reasoning": "vision",
            "review": True,
            "ui_widget": "",
        },
        "class_type": "LF_H3PromptMaker",
        "_meta": {"title": "MiniMax H3 prompt maker"},
    }
    assert not {
        "lms_config",
        "inventory_writer",
        "scope_context",
        "scope_writer",
        "inventory_context",
        "writer",
        "review_context",
        "reviewer",
        "compiler",
    }.intersection(graph)
    assert graph["display_prompt"]["inputs"]["string"] == [
        "h3_prompt_maker",
        0,
    ]
    assert graph["display_report"]["inputs"]["json_input"] == [
        "h3_prompt_maker",
        1,
    ]
    assert graph["display_inventory"]["inputs"]["json_input"] == [
        "h3_prompt_maker",
        2,
    ]


def test_text_only_configuration_removes_the_image_branch() -> None:
    graph = WORKFLOW.load_prompt()

    WORKFLOW.configure_prompt(graph, _inputs("t2va", 0))

    assert "image_list" not in graph
    assert "image" not in graph["h3_prompt_maker"]["inputs"]
    assert graph["h3_prompt_maker"]["inputs"] == {
        "intent": "A crane crosses a misty harbor while its bell rings once.",
        "mode": "t2va",
        "instructions": "",
        "duration_seconds": 7.5,
        "url": "http://127.0.0.1:1234/api/v1/chat",
        "model": "vision-writer",
        "temperature": 0.3,
        "reasoning": "off",
        "review": True,
        "ui_widget": "",
    }


@pytest.mark.parametrize(
    ("mode", "reference_count"),
    (
        ("t2va", 0),
        ("i2va", 1),
        ("fl2va", 2),
        ("l2va", 1),
        ("ref2va", 1),
        ("ref2va", 9),
    ),
)
def test_configure_atomic_node_and_keeps_only_the_exact_ordered_image_branch(
    monkeypatch: pytest.MonkeyPatch,
    mode: str,
    reference_count: int,
) -> None:
    graph, resolved = _configure(monkeypatch, mode, reference_count)

    active_ids = list(PICTURE_IDS[:reference_count])
    assert resolved == active_ids
    assert [name for name in PICTURE_IDS if name in graph] == active_ids
    for name in active_ids:
        assert graph[name]["inputs"]["image"] == f"staged/{name}.png [input]"

    expected_inputs = {
        "intent": "A crane crosses a misty harbor while its bell rings once.",
        "mode": mode,
        "instructions": "",
        "duration_seconds": 7.5,
        "url": "http://127.0.0.1:1234/api/v1/chat",
        "model": "vision-writer",
        "temperature": 0.3,
        "reasoning": "off",
        "review": True,
        "ui_widget": "",
    }

    if reference_count == 0:
        assert "image_list" not in graph
        assert graph["h3_prompt_maker"]["inputs"] == expected_inputs
    else:
        expected_inputs["image"] = ["image_list", 0]
        assert graph["h3_prompt_maker"]["inputs"] == expected_inputs
        assert graph["image_list"]["inputs"] == {
            f"image_{ordinal}": [f"picture_{ordinal}", 0]
            for ordinal in range(1, reference_count + 1)
        }


@pytest.mark.parametrize(
    ("mode", "reference_count", "missing_field"),
    (
        ("i2va", 0, "picture_1"),
        ("fl2va", 1, "picture_2"),
        ("l2va", 0, "picture_1"),
        ("ref2va", 0, "picture_1"),
    ),
)
def test_missing_required_picture_fails_before_staging_or_graph_mutation(
    monkeypatch: pytest.MonkeyPatch,
    mode: str,
    reference_count: int,
    missing_field: str,
) -> None:
    monkeypatch.setattr(
        workflow_module,
        "resolve_load_image_reference",
        lambda *_: pytest.fail("Picture counts must be checked before staging."),
    )
    graph = WORKFLOW.load_prompt()
    original = deepcopy(graph)

    with pytest.raises(InputValidationError) as error:
        WORKFLOW.configure_prompt(graph, _inputs(mode, reference_count))

    assert error.value.input_name == missing_field
    assert graph == original


@pytest.mark.parametrize(("mode", "reference_count"), (("t2va", 1), ("i2va", 2), ("l2va", 2)))
def test_extra_picture_fails_before_staging_or_graph_mutation(
    monkeypatch: pytest.MonkeyPatch,
    mode: str,
    reference_count: int,
) -> None:
    monkeypatch.setattr(
        workflow_module,
        "resolve_load_image_reference",
        lambda *_: pytest.fail("Picture counts must be checked before staging."),
    )
    graph = WORKFLOW.load_prompt()
    original = deepcopy(graph)

    with pytest.raises(ValueError, match="requires exactly"):
        WORKFLOW.configure_prompt(graph, _inputs(mode, reference_count))

    assert graph == original


@pytest.mark.parametrize("mode", ("ref2va", "auto"))
def test_gapped_picture_sequence_fails_before_staging_or_graph_mutation(
    monkeypatch: pytest.MonkeyPatch,
    mode: str,
) -> None:
    monkeypatch.setattr(
        workflow_module,
        "resolve_load_image_reference",
        lambda *_: pytest.fail("Gaps must be checked before staging."),
    )
    inputs = _inputs(mode, 1)
    inputs["picture_3"] = [Path("C:/uploads/picture-3.png")]
    graph = WORKFLOW.load_prompt()
    original = deepcopy(graph)

    with pytest.raises(ValueError, match="cannot contain a gap"):
        WORKFLOW.configure_prompt(graph, inputs)

    assert graph == original


@pytest.mark.parametrize("reference_count", (0, 1, 9))
@pytest.mark.parametrize("explicit_auto", (False, True))
def test_automatic_mode_uses_references_without_requiring_a_mode_choice(
    monkeypatch: pytest.MonkeyPatch,
    reference_count: int,
    explicit_auto: bool,
) -> None:
    staged: list[str] = []

    def resolve(inputs: dict[str, Any], name: str) -> str:
        staged.append(name)
        return f"staged/{name}.png [input]"

    monkeypatch.setattr(workflow_module, "resolve_load_image_reference", resolve)
    inputs = _inputs("auto", reference_count)
    if not explicit_auto:
        inputs.pop("mode")
    inputs["instructions"] = "  Give the scene a playful ending.  "
    graph = WORKFLOW.load_prompt()

    WORKFLOW.configure_prompt(graph, inputs)

    node_inputs = graph["h3_prompt_maker"]["inputs"]
    assert node_inputs["mode"] == ("ref2va" if reference_count else "t2va")
    assert node_inputs["instructions"] == "Give the scene a playful ending."
    assert staged == list(PICTURE_IDS[:reference_count])
    assert ("image" in node_inputs) is bool(reference_count)


@pytest.mark.parametrize("duration", (False, 0, "nan", 6_000, 6_000.001))
def test_invalid_duration_fails_before_staging_or_graph_mutation(
    monkeypatch: pytest.MonkeyPatch,
    duration: Any,
) -> None:
    monkeypatch.setattr(
        workflow_module,
        "resolve_load_image_reference",
        lambda *_: pytest.fail("Duration must be checked before staging."),
    )
    inputs = _inputs("i2va", 1)
    inputs["duration"] = duration
    graph = WORKFLOW.load_prompt()
    original = deepcopy(graph)

    with pytest.raises((InputValidationError, ValueError)):
        WORKFLOW.configure_prompt(graph, inputs)

    assert graph == original


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("endpoint", "  "),
        ("model", False),
        ("instructions", False),
        ("temperature", "nan"),
        ("temperature", 1.1),
        ("reasoning", "sometimes"),
    ),
)
def test_invalid_transport_control_fails_before_staging_or_graph_mutation(
    monkeypatch: pytest.MonkeyPatch,
    field: str,
    value: Any,
) -> None:
    monkeypatch.setattr(
        workflow_module,
        "resolve_load_image_reference",
        lambda *_: pytest.fail("Transport controls must be checked before staging."),
    )
    inputs = _inputs("i2va", 1)
    inputs[field] = value
    graph = WORKFLOW.load_prompt()
    original = deepcopy(graph)

    with pytest.raises((InputValidationError, ValueError)):
        WORKFLOW.configure_prompt(graph, inputs)

    assert graph == original


def test_empty_model_is_forwarded_for_loaded_model_discovery(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    inputs = _inputs("t2va", 0)
    inputs["model"] = "  "
    graph = WORKFLOW.load_prompt()

    monkeypatch.setattr(
        workflow_module,
        "resolve_load_image_reference",
        lambda *_: pytest.fail("Text mode must not stage pictures."),
    )
    WORKFLOW.configure_prompt(graph, inputs)

    assert graph["h3_prompt_maker"]["inputs"]["model"] == ""


@pytest.mark.parametrize(
    ("review_input", "expected"),
    (({}, True), ({"review": True}, True), ({"review": False}, False)),
)
def test_review_defaults_on_and_preserves_explicit_boolean_choices(
    review_input: dict[str, Any],
    expected: bool,
) -> None:
    graph = WORKFLOW.load_prompt()
    graph["h3_prompt_maker"]["inputs"]["review"] = not expected

    WORKFLOW.configure_prompt(graph, {**_inputs("t2va", 0), **review_input})

    assert graph["h3_prompt_maker"]["inputs"]["review"] is expected


@pytest.mark.parametrize("review", ("false", "true", "off", "on", "", 0, 1, None, [], {}))
def test_invalid_review_fails_before_staging_or_graph_mutation(
    monkeypatch: pytest.MonkeyPatch,
    review: Any,
) -> None:
    monkeypatch.setattr(
        workflow_module,
        "resolve_load_image_reference",
        lambda *_: pytest.fail("Review must be checked before staging."),
    )
    inputs = {**_inputs("i2va", 1), "review": review}
    graph = WORKFLOW.load_prompt()
    original = deepcopy(graph)

    with pytest.raises(InputValidationError) as error:
        WORKFLOW.configure_prompt(graph, inputs)

    assert error.value.input_name == "review"
    assert graph == original
