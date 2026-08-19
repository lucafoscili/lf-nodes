"""Offline contracts for the generic Illustrious XL runner workflow."""

from __future__ import annotations

import json
import sys
import types

import pytest


helpers_module = types.ModuleType("modules.utils.helpers")
helpers_module.__path__ = []  # type: ignore[attr-defined]
conversion_module = types.ModuleType("modules.utils.helpers.conversion")
conversion_module.json_safe = lambda value: value
sys.modules.setdefault("modules.utils.helpers", helpers_module)
sys.modules.setdefault("modules.utils.helpers.conversion", conversion_module)

from modules.workflow_runner.services.registry import InputValidationError
from modules.workflow_runner.workflows import _WORKFLOW_MODULES
from modules.workflow_runner.workflows.t2i_illustrious_xl import WORKFLOW


def test_definition_is_generic_and_exposes_optional_overrides() -> None:
    assert WORKFLOW.id == "t2i_illustrious_xl"
    assert WORKFLOW.value == "Illustrious XL Anime Portrait"
    assert WORKFLOW.category == "Text to Image"
    assert [(cell.id, cell.required) for cell in WORKFLOW.inputs] == [
        ("prompt", True),
        ("seed", False),
        ("checkpoint", False),
    ]


def test_configure_preserves_graph_defaults_when_overrides_are_omitted() -> None:
    prompt = WORKFLOW.load_prompt()
    WORKFLOW.configure_prompt(prompt, {"prompt": "masterpiece, 1girl, solo"})

    assert prompt["3"]["inputs"]["text"] == "masterpiece, 1girl, solo"
    assert prompt["6"]["inputs"]["seed"] == 42
    assert prompt["1"]["inputs"]["ckpt_name"] == "Genesis v0.10.safetensors"


def test_configure_applies_seed_and_checkpoint_overrides() -> None:
    prompt = WORKFLOW.load_prompt()
    WORKFLOW.configure_prompt(
        prompt,
        {
            "prompt": "best quality, moonlit forest",
            "seed": "77",
            "checkpoint": "models/illustrious.safetensors",
        },
    )

    assert prompt["6"]["inputs"]["seed"] == 77
    assert prompt["1"]["inputs"]["ckpt_name"] == "models/illustrious.safetensors"


def test_prompt_is_required() -> None:
    with pytest.raises(InputValidationError):
        WORKFLOW.configure_prompt(WORKFLOW.load_prompt(), {})


def test_graph_contains_no_project_vocabulary() -> None:
    graph_text = WORKFLOW.workflow_path.read_text(encoding="utf-8")
    lowered = graph_text.lower()
    assert "warden" not in lowered
    assert "velora" not in lowered
    graph = json.loads(graph_text)
    assert graph["7"]["inputs"]["filename_prefix"] == "lf-workflow-runner/illustrious-xl"


def test_workflow_is_in_the_packaged_inventory() -> None:
    assert "t2i_illustrious_xl" in _WORKFLOW_MODULES
