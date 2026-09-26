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
        "intent", "picture_1", "duration", "aspect_ratio", "output_quality"
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


@pytest.mark.parametrize("quality", ["standard", "hd"])
def test_output_quality_is_bound_only_to_renderer(quality):
    plan = _plan({"output_quality": quality, "manage_model": False})
    assert "output_quality" not in sequence_stage_declared_inputs(plan, 0)
    assert sequence_stage_declared_inputs(plan, 1)["output_quality"] == quality
    graph = renderer.load_prompt()
    renderer.configure_download(graph, sequence_stage_preflight_inputs(plan, 1))
    upscale_nodes = [node for node in graph.values() if node["class_type"] == "MMH3UltimateUpscale"]
    assert len(upscale_nodes) == (1 if quality == "hd" else 0)
    assert graph["create_video"]["inputs"]["audio"] == ["decode_audio", 0]


def test_output_quality_defaults_remain_standard():
    plan = _plan({"manage_model": False})
    assert sequence_stage_declared_inputs(plan, 1)["output_quality"] == "standard"


@pytest.mark.parametrize("orchestra,stage_ids", [
    (orchestration.character_turnaround_orchestra, {"subject_right", "back", "subject_left"}),
    (orchestration.sprite_loop_orchestra, {"restage"}),
    (ORCHESTRA, {"render_video"}),
])
def test_all_h3_assemblies_forward_the_shared_quality_choice(orchestra, stage_ids):
    from modules.workflow_runner.services.registry import WorkflowSequencePublicInputBinding

    quality = next(cell for cell in orchestra.inputs if cell.id == "output_quality")
    assert quality.props["lfValue"] == "standard"
    for stage in orchestra.stages:
        bindings = [binding for binding in stage.bindings
                    if isinstance(binding, WorkflowSequencePublicInputBinding)
                    and binding.target_input_id == "output_quality"]
        assert len(bindings) == (1 if stage.id in stage_ids else 0)
        if bindings:
            assert bindings[0].public_input_id == "output_quality"


@pytest.mark.parametrize("orchestra", [
    orchestration.character_turnaround_orchestra,
    orchestration.sprite_loop_orchestra,
    ORCHESTRA,
])
@pytest.mark.parametrize("nodes_ready,model_ready", [(False, True), (True, False), (True, True)])
def test_hd_prerequisites_filter_only_optional_orchestra_choice(monkeypatch, orchestra, nodes_ready, model_ready):
    from modules.workflow_runner.services import registry as registry_module
    from modules.workflow_runner.services.readiness import WorkflowReadinessScanner
    from modules.workflow_runner.workflows.minimax_h3_hd import HD_OPTION_REQUIREMENT

    scanner = WorkflowReadinessScanner(
        node_mapping_loader=lambda: dict.fromkeys(HD_OPTION_REQUIREMENT.required_node_types) if nodes_ready else {},
        model_filename_loader=lambda _category: (),
        model_file_exists_loader=lambda _path: model_ready,
    )
    monkeypatch.setattr(registry_module, "WorkflowReadinessScanner", lambda: scanner)
    monkeypatch.setattr(registry_module, "evaluate_workflow_readiness", lambda *_args, **_kwargs: {"status": "ready", "issues": []})
    registry = WorkflowRegistry()
    for block in (
        maker, renderer, orchestration.identity_edit, orchestration.directed_view,
        orchestration.assemble_cardinal_turnaround, orchestration.reference_restage,
        orchestration.sprite_loop_cut,
    ):
        registry.register(block)
    registry.register(orchestra)
    listed = next(node for node in registry.list()["nodes"] if node["id"] == orchestra.id)
    quality = listed["children"][0]["cells"]["output_quality"]["props"]
    assert [node["workflowValue"] for node in quality["lfDataset"]["nodes"]] == (
        ["standard", "hd"] if nodes_ready and model_ready else ["standard"]
    )
    assert quality["lfValue"] == "standard"
    assert listed["readiness"]["status"] == "ready"
    declared = next(cell for cell in orchestra.inputs if cell.id == "output_quality")
    assert len(declared.props["lfDataset"]["nodes"]) == 2
