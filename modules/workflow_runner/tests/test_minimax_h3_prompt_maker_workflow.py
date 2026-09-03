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
        "max_tokens": "5000",
        "timeout": "180",
    }


def _configure(
    monkeypatch: pytest.MonkeyPatch,
    mode: str,
    reference_count: int,
) -> tuple[dict[str, Any], list[str], list[dict[str, Any]]]:
    resolved: list[str] = []
    systems: list[dict[str, Any]] = []

    def resolve(inputs: dict[str, Any], name: str) -> str:
        resolved.append(name)
        assert inputs[name] == [
            Path(f"C:/uploads/picture-{name.removeprefix('picture_')}.png")
        ]
        return f"staged/{name}.png [input]"

    def system(**kwargs: Any) -> str:
        systems.append(kwargs)
        return f"system:{kwargs['mode']}:{kwargs['reference_image_count']}"

    monkeypatch.setattr(workflow_module, "resolve_load_image_reference", resolve)
    monkeypatch.setattr(workflow_module, "build_h3_prompt_writer_system", system)
    graph = WORKFLOW.load_prompt()
    WORKFLOW.configure_prompt(graph, _inputs(mode, reference_count))
    return graph, resolved, systems


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
        "endpoint",
        "temperature",
        "reasoning",
        "max_tokens",
        "timeout",
        *PICTURE_IDS[2:],
    ]
    assert [cell.id for cell in WORKFLOW.outputs] == [
        "prompt",
        "validation_report",
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
            "max_tokens",
            "timeout",
        )
    )
    assert cells["model"].required
    assert not cells["model"].advanced
    assert all(
        not cells[name].required
        for name in (
            "endpoint",
            "temperature",
            "reasoning",
            "max_tokens",
            "timeout",
        )
    )
    assert cells["max_tokens"].props["lfValue"] == "8192"
    assert cells["endpoint"].props["lfValue"].endswith("/api/v1/chat")
    assert cells["temperature"].props["lfHtmlAttributes"]["max"] == 1.0
    assert cells["reasoning"].props["lfValue"] == "off"
    assert [
        option["workflowValue"]
        for option in cells["reasoning"].props["lfDataset"]["nodes"]
    ] == ["off", "auto", "on"]
    assert [
        option["workflowValue"]
        for option in cells["mode"].props["lfDataset"]["nodes"]
    ] == ["t2va", "i2va", "fl2va", "l2va", "ref2va"]


def test_graph_uses_public_local_chat_and_private_non_public_compiler() -> None:
    graph = WORKFLOW.load_prompt()

    assert graph["writer"]["class_type"] == "LF_LocalChatCompletions"
    assert set(graph["writer"]["inputs"]) == {
        "prompt",
        "url",
        "system_message",
        "image",
        "model",
        "temperature",
        "reasoning",
        "max_tokens",
        "timeout",
        "ui_widget",
    }
    assert "seed" not in graph["writer"]["inputs"]
    assert graph["writer"]["inputs"]["max_tokens"] == 8192
    assert graph["writer"]["inputs"]["reasoning"] == "off"
    assert graph["compiler"] == {
        "inputs": {
            "response": ["writer", 0],
            "mode": "t2va",
            "duration_seconds": 6.0,
            "reference_image_count": 0,
        },
        "class_type": "WorkflowRunnerH3PromptCompiler",
        "_meta": {"title": "Compile and validate the MiniMax H3 prompt"},
    }
    assert graph["display_prompt"]["inputs"]["string"] == ["compiler", 0]
    assert graph["display_report"]["inputs"]["json_input"] == ["compiler", 1]


def test_text_only_configuration_builds_the_real_h3_writer_system() -> None:
    graph = WORKFLOW.load_prompt()

    WORKFLOW.configure_prompt(graph, _inputs("t2va", 0))

    system = graph["writer"]["inputs"]["system_message"]
    assert "Mode: t2va. Target duration: 7.50 seconds." in system
    assert "No reference images are attached" in system
    assert '"shots"' in system
    assert '"start_seconds"' in system
    assert '"description"' in system
    assert '"dialogue"' in system
    assert '"overall_soundscape"' in system
    assert '"non_diegetic_music"' in system
    assert "image_list" not in graph
    assert "image" not in graph["writer"]["inputs"]


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
def test_configure_stages_and_keeps_only_the_exact_ordered_image_branch(
    monkeypatch: pytest.MonkeyPatch,
    mode: str,
    reference_count: int,
) -> None:
    graph, resolved, systems = _configure(monkeypatch, mode, reference_count)

    active_ids = list(PICTURE_IDS[:reference_count])
    assert resolved == active_ids
    assert systems == [
        {
            "mode": mode,
            "duration_seconds": 7.5,
            "reference_image_count": reference_count,
        }
    ]
    assert [name for name in PICTURE_IDS if name in graph] == active_ids
    for name in active_ids:
        assert graph[name]["inputs"]["image"] == f"staged/{name}.png [input]"

    writer = graph["writer"]["inputs"]
    assert writer["prompt"] == (
        "A crane crosses a misty harbor while its bell rings once."
    )
    assert writer["url"] == "http://127.0.0.1:1234/api/v1/chat"
    assert writer["system_message"] == f"system:{mode}:{reference_count}"
    assert writer["model"] == "vision-writer"
    assert writer["temperature"] == 0.3
    assert writer["reasoning"] == "off"
    assert writer["max_tokens"] == 5000
    assert writer["timeout"] == 180
    assert graph["compiler"]["inputs"] == {
        "response": ["writer", 0],
        "mode": mode,
        "duration_seconds": 7.5,
        "reference_image_count": reference_count,
    }

    if reference_count == 0:
        assert "image_list" not in graph
        assert "image" not in writer
    else:
        assert writer["image"] == ["image_list", 0]
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


def test_gapped_picture_sequence_fails_before_staging_or_graph_mutation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        workflow_module,
        "resolve_load_image_reference",
        lambda *_: pytest.fail("Gaps must be checked before staging."),
    )
    inputs = _inputs("ref2va", 1)
    inputs["picture_3"] = [Path("C:/uploads/picture-3.png")]
    graph = WORKFLOW.load_prompt()
    original = deepcopy(graph)

    with pytest.raises(ValueError, match="cannot contain a gap"):
        WORKFLOW.configure_prompt(graph, inputs)

    assert graph == original


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
        ("model", "  "),
        ("model", False),
        ("temperature", "nan"),
        ("temperature", 1.1),
        ("reasoning", "sometimes"),
        ("max_tokens", 0),
        ("timeout", 0),
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
