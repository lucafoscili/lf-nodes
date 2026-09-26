"""Idea-to-video assembly: one brief, one duration, identical ordered references."""

from types import SimpleNamespace

import pytest

from modules.workflow_runner.services.registry import WorkflowRegistry, WorkflowSequenceTextBinding
from modules.workflow_runner.services.sequence_runtime import (
    normalize_sequence_definition,
    sequence_stage_declared_inputs,
    sequence_stage_preflight_inputs,
)
from modules.workflow_runner.workflows import orchestration
from modules.workflow_runner.workflows.minimax_h3_prompt_maker import WORKFLOW as maker
from modules.workflow_runner.workflows.minimax_h3_prompt_video import WORKFLOW as renderer


ORCHESTRA = orchestration.minimax_h3_video_orchestra
BLOCKS = {block.id: block for block in (maker, renderer)}


def _plan(inputs):
    return normalize_sequence_definition(
        ORCHESTRA, inputs,
        workflow_resolver=BLOCKS.get,
        output_node_resolver=lambda workflow_id, output_id: next(
            cell.node_id for cell in BLOCKS[workflow_id].outputs if cell.id == output_id
        ),
    )


def test_real_orchestra_exposes_video_and_exact_prompt():
    registry = WorkflowRegistry()
    for block in BLOCKS.values():
        registry.register(block)
    registry.register(ORCHESTRA)
    assert ORCHESTRA in orchestration.WORKFLOWS
    assert not hasattr(ORCHESTRA, "workflow_path")
    assert ORCHESTRA.final_output_ids == ("video", "prompt")
    assert ORCHESTRA.stages[1].bindings[0] == WorkflowSequenceTextBinding("prompt", "prompt")
    assert [cell.id for cell in ORCHESTRA.inputs if not cell.advanced] == [
        "intent", "picture_1", "duration", "aspect_ratio"
    ]


@pytest.mark.parametrize("count", [0, 1, 2, 9])
def test_preflight_uses_shared_duration_and_pictures_without_staging(monkeypatch, count):
    values = {
        "intent": "Walking from behind in a medieval town.",
        "manage_model": False,
        **{f"picture_{n}": [f"reference-{n}.png"] for n in range(1, count + 1)},
    }
    plan = _plan(values)
    writer_inputs = sequence_stage_declared_inputs(plan, 0)
    render_inputs = sequence_stage_preflight_inputs(plan, 1)
    assert writer_inputs["duration"] == render_inputs["duration"]
    for n in range(1, count + 1):
        assert writer_inputs[f"picture_{n}"] == render_inputs[f"picture_{n}"]
    assert "prompt" not in sequence_stage_declared_inputs(plan, 1) or (
        sequence_stage_declared_inputs(plan, 1)["prompt"] != render_inputs["prompt"]
    )
    writer_graph = maker.load_prompt()
    maker.configure_download(writer_graph, writer_inputs)
    render_graph = renderer.load_prompt()
    renderer.configure_download(render_graph, render_inputs)
    assert writer_graph["h3_prompt_maker"]["inputs"]["duration_seconds"] == (
        render_graph["h3"]["inputs"]["length"] / 24
    )
    assert writer_graph["h3_prompt_maker"]["inputs"]["mode"] == ("ref2va" if count else "t2va")


def test_host_defaults_are_cloned_and_do_not_mutate_standalone_blocks(monkeypatch):
    monkeypatch.setattr(orchestration, "get_settings", lambda: SimpleNamespace(
        WORKFLOW_RUNNER_LMS_ENDPOINT="http://localhost:9876/api/v1/chat",
        WORKFLOW_RUNNER_LMS_MODEL="downloaded-writer",
    ))
    cells = {cell.id: cell for cell in orchestration._h3_orchestra_inputs()}
    assert cells["endpoint"].props["lfValue"] == "http://localhost:9876/api/v1/chat"
    assert cells["model"].props["lfValue"] == "downloaded-writer"
    assert cells["manage_model"].props["lfValue"] is True
    assert cells["review"].props["lfValue"] is True
    assert next(cell for cell in maker.inputs if cell.id == "model").props["lfValue"] == ""
    monkeypatch.setattr(orchestration, "get_settings", lambda: SimpleNamespace())
    unconfigured = {cell.id: cell for cell in orchestration._h3_orchestra_inputs()}
    assert unconfigured["manage_model"].props["lfValue"] is False


@pytest.mark.parametrize("mode,count", [("i2va", 1), ("fl2va", 2), ("l2va", 1)])
def test_explicit_frame_modes_remain_in_sync(mode, count):
    plan = _plan({"mode": mode, "manage_model": False, **{
        f"picture_{n}": [f"frame-{n}.png"] for n in range(1, count + 1)
    }})
    assert sequence_stage_declared_inputs(plan, 0)["mode"] == mode
    assert sequence_stage_preflight_inputs(plan, 1)["mode"] == mode
