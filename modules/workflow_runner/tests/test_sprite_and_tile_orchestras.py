"""Contracts for the sprite-loop and iso-ground-tiles orchestras."""

from __future__ import annotations

from typing import Any

from modules.workflow_runner.services.registry import (
    WorkflowOrchestraNode,
    WorkflowSequenceArtifactBinding,
    WorkflowSequencePublicInputBinding,
)
from modules.workflow_runner.services.sequence_runtime import (
    normalize_sequence_definition,
)
from modules.workflow_runner.workflows.iso_ground_tiles import (
    WORKFLOW as iso_ground_tiles,
)
from modules.workflow_runner.workflows.krea2 import generate as krea2_generate
from modules.workflow_runner.workflows.minimax_h3 import reference_restage
from modules.workflow_runner.workflows.orchestration import (
    WORKFLOWS,
    iso_ground_tiles_orchestra,
    sprite_loop_orchestra,
)
from modules.workflow_runner.workflows.sprite_loop_cut import (
    WORKFLOW as sprite_loop_cut,
)


_BLOCKS = {
    workflow.id: workflow
    for workflow in (reference_restage, sprite_loop_cut, krea2_generate, iso_ground_tiles)
}


def _cell(workflow: Any, cell_id: str, *, ports: str = "inputs") -> Any:
    matches = [cell for cell in getattr(workflow, ports) if cell.id == cell_id]
    assert len(matches) == 1, (workflow.id, cell_id)
    return matches[0]


def _output_node_id(workflow_id: str, output_id: str) -> str:
    return _cell(_BLOCKS[workflow_id], output_id, ports="outputs").node_id


def test_both_orchestras_are_shipped() -> None:
    assert sprite_loop_orchestra in WORKFLOWS
    assert iso_ground_tiles_orchestra in WORKFLOWS


def test_sprite_loop_orchestra_chains_restage_into_cut_by_video() -> None:
    sequence = sprite_loop_orchestra
    assert isinstance(sequence, WorkflowOrchestraNode)
    assert sequence.value == "Sprite Loop from One Still"
    assert tuple(stage.id for stage in sequence.stages) == ("restage", "cut")
    assert tuple(stage.workflow_id for stage in sequence.stages) == (
        "minimax_h3_reference_restage",
        "sprite_loop_cut",
    )
    assert sequence.final_output_ids == (
        "frames",
        "atlas",
        "loop_receipt",
        "normalization_receipt",
    )
    assert tuple(cell.id for cell in sequence.inputs) == (
        "source_image",
        "direction",
        "aspect_ratio",
        "output_quality",
        "duration_frames",
        "seed",
        "frame_count",
        "columns",
        "min_period_frames",
        "max_period_frames",
        "motion_floor",
        "canvas_size",
        "content_height",
        "bottom_padding",
    )
    direction = _cell(sequence, "direction")
    assert "no resting pose" in direction.props["lfValue"]
    assert "continuous cycle" in direction.description
    assert _cell(sequence, "source_image").shape == "upload"
    cut = sequence.stages[1]
    assert cut.bindings[0] == WorkflowSequenceArtifactBinding("source_video", "video")
    assert all(
        isinstance(binding, WorkflowSequencePublicInputBinding)
        for binding in cut.bindings[1:]
    )


def test_sprite_loop_plan_hands_the_saved_video_to_the_cut() -> None:
    plan = normalize_sequence_definition(
        sprite_loop_orchestra,
        {"source_image": {"kind": "upload", "name": "siren.png"}},
        workflow_resolver=_BLOCKS.__getitem__,
        output_node_resolver=_output_node_id,
    )
    assert plan["inputs"]["frame_count"] == "24"
    assert plan["inputs"]["columns"] == "6"
    assert plan["inputs"]["canvas_size"] == "256"
    source = plan["stages"][1]["bindings"][0]
    assert source["kind"] == "artifact"
    assert source.get("source_stage_id") in (None, "restage")
    assert source["output_node_id"] == "save"
    assert plan["final_outputs"] == [
        {"output_id": "frames", "output_node_id": "save_frames"},
        {"output_id": "atlas", "output_node_id": "save_atlas"},
        {"output_id": "loop_receipt", "output_node_id": "display_loop_receipt"},
        {
            "output_id": "normalization_receipt",
            "output_node_id": "display_normalization_receipt",
        },
    ]


def test_iso_ground_tiles_orchestra_chains_generate_into_tiles_by_image() -> None:
    sequence = iso_ground_tiles_orchestra
    assert tuple(stage.id for stage in sequence.stages) == ("generate", "tiles")
    assert tuple(stage.workflow_id for stage in sequence.stages) == (
        "krea2_generate",
        "iso_ground_tiles",
    )
    assert sequence.final_output_ids == ("tiles", "texture", "receipt")
    assert tuple(cell.id for cell in sequence.inputs) == (
        "texture_prompt",
        "aspect_ratio",
        "seed",
        "blend_fraction",
        "tile_width",
        "tile_height",
        "variants",
        "texture_scale",
    )
    prompt = _cell(sequence, "texture_prompt")
    assert "straight-down orthographic" in prompt.props["lfValue"]
    tiles = sequence.stages[1]
    assert tiles.bindings[0] == WorkflowSequenceArtifactBinding("source_texture", "image")
    assert WorkflowSequencePublicInputBinding("seed", "seed") in tiles.bindings


def test_iso_ground_tiles_plan_hands_the_generated_image_to_the_tiles() -> None:
    plan = normalize_sequence_definition(
        iso_ground_tiles_orchestra,
        {},
        workflow_resolver=_BLOCKS.__getitem__,
        output_node_resolver=_output_node_id,
    )
    source = plan["stages"][1]["bindings"][0]
    assert source["kind"] == "artifact"
    assert source["output_node_id"] == "save"
    assert plan["inputs"]["tile_width"] == "128"
    assert plan["inputs"]["variants"] == "4"
    assert plan["final_outputs"][0] == {"output_id": "tiles", "output_node_id": "save_tiles"}
