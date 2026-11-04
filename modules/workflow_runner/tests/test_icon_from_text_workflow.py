"""Offline contracts for the Icon from Text Runner workflow."""

from __future__ import annotations

from pathlib import Path
import sys
import types
from typing import Any

import pytest


# Declarative workflow tests do not need Comfy's torch/xformers startup.
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
from modules.workflow_runner.workflows import icon_from_text as workflow_module


WORKFLOW = workflow_module.WORKFLOW


def _configure(monkeypatch: pytest.MonkeyPatch, **inputs: Any) -> tuple[dict[str, Any], list[str]]:
    staged: list[str] = []

    def resolve(given: dict[str, Any], name: str) -> str:
        staged.append(name)
        return f"lf_workflow_runner/{name}.png [input]"

    monkeypatch.setattr(workflow_module, "resolve_load_image_reference", resolve)
    prompt = WORKFLOW.load_prompt()
    WORKFLOW.configure_prompt(prompt, {"prompt": "A clay jug on a plain black background.", **inputs})
    return prompt, staged


def test_is_registered_and_described() -> None:
    assert "icon_from_text" in _WORKFLOW_MODULES
    assert WORKFLOW.id == "icon_from_text"
    assert all(cell.description for cell in (*WORKFLOW.inputs, *WORKFLOW.outputs))
    assert [(cell.node_id, cell.id) for cell in WORKFLOW.outputs] == [
        ("save_icon", "icon"),
        ("save_master", "master"),
        ("save_source", "source"),
    ]
    graph = WORKFLOW.load_prompt()
    for cell in (*WORKFLOW.inputs, *WORKFLOW.outputs):
        assert cell.node_id in graph, cell.id


def test_without_style_images_the_adapter_and_loaders_are_removed(monkeypatch: pytest.MonkeyPatch) -> None:
    prompt, staged = _configure(monkeypatch, seed="7")
    assert staged == []
    assert "lora" not in prompt
    assert prompt["patch"]["inputs"]["model"] == ["unet", 0]
    for slot in ("style_1", "style_2", "style_3"):
        assert slot not in prompt
    assert not {"image1", "image2", "image3"} & set(prompt["positive"]["inputs"])
    assert prompt["positive"]["inputs"]["prompt"] == "A clay jug on a plain black background."
    assert prompt["sampler"]["inputs"]["seed"] == 7
    assert prompt["save_icon"]["inputs"]["filename_prefix"] == "LF_Nodes/IconFromText/icon/seed-7"
    assert prompt["save_master"]["inputs"]["filename_prefix"] == "LF_Nodes/IconFromText/master/seed-7"
    assert prompt["save_source"]["inputs"]["filename_prefix"] == "LF_Nodes/IconFromText/source/seed-7"
    # Every remaining link points at a node that is still in the graph.
    for node in prompt.values():
        for value in node["inputs"].values():
            if isinstance(value, list) and len(value) == 2 and isinstance(value[0], str):
                assert value[0] in prompt


def test_two_style_images_keep_two_loaders_and_the_adapter(monkeypatch: pytest.MonkeyPatch) -> None:
    prompt, staged = _configure(
        monkeypatch,
        style_1_image=[Path("C:/uploads/a.png")],
        style_2_image=[Path("C:/uploads/b.png")],
        style_strength="0.8",
        output_folder="icons/round_1",
    )
    assert staged == ["style_1_image", "style_2_image"]
    assert prompt["lora"]["inputs"]["strength_model"] == pytest.approx(0.8)
    assert prompt["patch"]["inputs"]["model"] == ["lora", 0]
    assert prompt["style_1"]["inputs"]["image"] == "lf_workflow_runner/style_1_image.png [input]"
    assert "style_3" not in prompt
    assert prompt["positive"]["inputs"]["image2"] == ["style_2", 0]
    assert "image3" not in prompt["positive"]["inputs"]
    assert prompt["save_icon"]["inputs"]["filename_prefix"] == "icons/round_1/icon/seed-42"


def test_framing_controls_reach_the_framer(monkeypatch: pytest.MonkeyPatch) -> None:
    prompt, _ = _configure(
        monkeypatch, master_size="256", icon_size="32", fill="0.8", backdrop="source",
        backdrop_color="#101010", glow_color="#33ccff", glow_strength="0.5", bevel="0.04",
    )
    frame = prompt["frame"]["inputs"]
    assert (frame["master_size"], frame["icon_size"]) == (256, 32)
    assert frame["fill"] == pytest.approx(0.8)
    assert frame["backdrop"] == "source"
    assert (frame["backdrop_color"], frame["glow_color"]) == ("#101010", "#33ccff")
    assert frame["glow_strength"] == pytest.approx(0.5)
    assert frame["bevel"] == pytest.approx(0.04)
    assert frame["mask"] == ["cutout", 3]


@pytest.mark.parametrize(
    ("inputs", "error"),
    [
        ({"style_2_image": [Path("C:/uploads/b.png")]}, "in order"),
        ({"glow_color": "blue"}, "glow_color"),
        ({"output_folder": "../escape"}, "output_folder"),
        ({"icon_size": "600", "master_size": "512"}, "icon_size"),
    ],
)
def test_bad_inputs_fail_before_submission(monkeypatch: pytest.MonkeyPatch, inputs: dict[str, Any], error: str) -> None:
    with pytest.raises(ValueError, match=error):
        _configure(monkeypatch, **inputs)


def test_unknown_backdrop_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(InputValidationError):
        _configure(monkeypatch, backdrop="gradient")
