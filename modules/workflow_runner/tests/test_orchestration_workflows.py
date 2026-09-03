"""Focused contracts for declaration-only Workflow Runner assemblies."""

from __future__ import annotations

from typing import Any

import pytest

from modules.workflow_runner.services import registry as registry_module
from modules.workflow_runner.services import workflow_service
from modules.workflow_runner.services.registry import (
    WorkflowOrchestraNode,
    WorkflowRegistry,
    WorkflowSequenceArtifactBinding,
    WorkflowSequenceLiteralBinding,
    WorkflowSequenceNode,
    WorkflowSequencePublicInputBinding,
)
from modules.workflow_runner.services.sequence_runtime import (
    normalize_sequence_definition,
)
from modules.workflow_runner.workflows.cardinal_turnaround import (
    WORKFLOW as assemble_cardinal_turnaround,
)
from modules.workflow_runner.workflows.krea2 import character_restage, identity_edit
from modules.workflow_runner.workflows.minimax_h3 import directed_view
from modules.workflow_runner.workflows.orchestration import (
    character_turnaround_orchestra,
    identity_cleanup_restage,
)


def _cell(workflow: Any, input_id: str, *, ports: str = "inputs") -> Any:
    matches = [
        cell for cell in getattr(workflow, ports) if cell.id == input_id
    ]
    assert len(matches) == 1
    return matches[0]


def _output_node_id(workflow_id: str, output_id: str) -> str:
    workflows = {
        identity_edit.id: identity_edit,
        character_restage.id: character_restage,
        directed_view.id: directed_view,
        assemble_cardinal_turnaround.id: assemble_cardinal_turnaround,
    }
    return _cell(workflows[workflow_id], output_id, ports="outputs").node_id


def test_orchestration_uses_author_facing_alias_and_owns_no_comfy_graph() -> None:
    assert isinstance(identity_cleanup_restage, WorkflowOrchestraNode)
    assert WorkflowOrchestraNode is WorkflowSequenceNode
    assert identity_cleanup_restage.category == "Krea 2"
    assert identity_cleanup_restage.value == "Identity-Preserved Restage"
    assert "krea" not in identity_cleanup_restage.value.lower()
    assert "local" not in identity_cleanup_restage.value.lower()
    for forbidden in (
        "workflow_path",
        "configure_prompt",
        "configure_download",
        "required_model_assets",
    ):
        assert not hasattr(identity_cleanup_restage, forbidden)


def test_orchestration_has_no_downloadable_graph_authority(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        workflow_service,
        "_get_workflow",
        lambda workflow_id: (
            identity_cleanup_restage
            if workflow_id == identity_cleanup_restage.id
            else None
        ),
    )

    with pytest.raises(
        workflow_service.WorkflowHasNoDownloadableGraphError
    ) as exc_info:
        workflow_service.get_workflow_content(identity_cleanup_restage.id)

    assert exc_info.value.code == "workflow_has_no_downloadable_graph"
    assert exc_info.value.workflow_id == identity_cleanup_restage.id


def test_identity_restage_reuses_public_knob_contracts_without_aliasing() -> None:
    sequence_cells = {
        cell.id: cell for cell in identity_cleanup_restage.inputs
    }
    assert tuple(sequence_cells) == (
        "identity_image",
        "identity_prompt",
        "restage_prompt",
        "aspect_ratio",
        "seed",
    )

    source_identity = _cell(identity_edit, "identity_image")
    public_identity = sequence_cells["identity_image"]
    assert public_identity is not source_identity
    assert public_identity.to_dict() == source_identity.to_dict()
    assert public_identity.props is not source_identity.props

    identity_prompt = _cell(identity_edit, "prompt")
    public_identity_prompt = sequence_cells["identity_prompt"]
    assert public_identity_prompt is not identity_prompt
    assert public_identity_prompt.description != identity_prompt.description
    assert public_identity_prompt.props["lfValue"] != identity_prompt.props["lfValue"]
    assert public_identity_prompt.props["lfHelper"] != identity_prompt.props["lfHelper"]
    assert public_identity_prompt.props["lfLabel"] == "Identity cleanup"
    assert identity_prompt.props["lfLabel"] == "Edit instruction"

    cleanup_default = public_identity_prompt.props["lfValue"]
    cleanup_helper = public_identity_prompt.props["lfHelper"]["value"]
    assert "supplied character reference" in cleanup_default
    assert "exact facial identity" in cleanup_default
    assert "scene reference" not in cleanup_default.lower()
    assert "scene image" not in cleanup_default.lower()
    assert "supplied character reference" in cleanup_helper
    assert "new pose, outfit, and environment" in cleanup_helper
    assert "scene reference" not in cleanup_helper.lower()
    assert "scene image" not in cleanup_helper.lower()

    restage_prompt = _cell(character_restage, "prompt")
    public_restage_prompt = sequence_cells["restage_prompt"]
    assert public_restage_prompt is not restage_prompt
    assert public_restage_prompt.description == restage_prompt.description
    assert public_restage_prompt.props["lfValue"] == restage_prompt.props["lfValue"]
    assert public_restage_prompt.props["lfHelper"] == restage_prompt.props["lfHelper"]
    assert public_restage_prompt.props["lfLabel"] == "Restage scene and pose"
    assert restage_prompt.props["lfLabel"] == "New scene and pose"

    # A shared public knob is safe only while both blocks expose the same
    # declaration. If either block diverges, this assembly must be reconsidered.
    for input_id in ("aspect_ratio", "seed"):
        public_cell = sequence_cells[input_id]
        identity_cell = _cell(identity_edit, input_id)
        restage_cell = _cell(character_restage, input_id)
        assert public_cell is not identity_cell
        assert public_cell.to_dict() == identity_cell.to_dict()
        assert public_cell.to_dict() == restage_cell.to_dict()


def test_identity_restage_topology_is_linear_and_artifact_driven() -> None:
    sequence = identity_cleanup_restage
    assert sequence.final_output_ids == ("image",)
    assert tuple(stage.id for stage in sequence.stages) == ("identity", "restage")
    assert tuple(stage.workflow_id for stage in sequence.stages) == (
        "krea2_identity_edit",
        "krea2_character_restage",
    )

    identity_bindings = sequence.stages[0].bindings
    assert identity_bindings == (
        WorkflowSequencePublicInputBinding("identity_image", "identity_image"),
        WorkflowSequencePublicInputBinding("prompt", "identity_prompt"),
        WorkflowSequencePublicInputBinding("aspect_ratio", "aspect_ratio"),
        WorkflowSequencePublicInputBinding("seed", "seed"),
    )
    assert sequence.stages[1].bindings == (
        WorkflowSequenceArtifactBinding("reference_image", "image"),
        WorkflowSequencePublicInputBinding("prompt", "restage_prompt"),
        WorkflowSequencePublicInputBinding("aspect_ratio", "aspect_ratio"),
        WorkflowSequencePublicInputBinding("seed", "seed"),
    )


def test_identity_restage_plan_uses_orchestra_prompt_and_block_defaults() -> None:
    workflows = {
        identity_edit.id: identity_edit,
        character_restage.id: character_restage,
    }
    plan = normalize_sequence_definition(
        identity_cleanup_restage,
        {"identity_image": {"kind": "upload", "name": "identity.png"}},
        workflow_resolver=workflows.__getitem__,
        output_node_resolver=_output_node_id,
    )

    assert plan["inputs"]["identity_prompt"] == _cell(
        identity_cleanup_restage, "identity_prompt"
    ).props["lfValue"]
    assert plan["inputs"]["identity_prompt"] != _cell(
        identity_edit, "prompt"
    ).props["lfValue"]
    assert plan["inputs"]["restage_prompt"] == _cell(
        character_restage, "prompt"
    ).props["lfValue"]
    assert plan["inputs"]["aspect_ratio"] == "2:3 (Portrait Photo)"
    assert plan["inputs"]["seed"] == "42"

    identity_defaults = plan["stages"][0]["defaults"]
    assert identity_defaults["steps"] == 10
    assert identity_defaults["sampler_name"] == "euler"
    assert identity_defaults["scheduler"] == "beta"
    assert identity_defaults["identity_fidelity"] == "4"
    assert identity_defaults["grounding_px"] == "1024"

    assert plan["stages"][1]["defaults"]["model_name"] == identity_defaults[
        "model_name"
    ]
    assert plan["final_outputs"] == [
        {"output_id": "image", "output_node_id": "save"}
    ]


def test_character_turnaround_orchestra_is_five_focused_blocks() -> None:
    sequence = character_turnaround_orchestra

    assert isinstance(sequence, WorkflowOrchestraNode)
    assert sequence.value == "3D-Ready Character Turnaround"
    assert sequence.category == "3D"
    assert tuple(stage.id for stage in sequence.stages) == (
        "cleanup",
        "subject_right",
        "back",
        "subject_left",
        "assemble",
    )
    assert tuple(stage.workflow_id for stage in sequence.stages) == (
        "krea2_identity_edit",
        "minimax_h3_directed_view",
        "minimax_h3_directed_view",
        "minimax_h3_directed_view",
        "assemble_cardinal_turnaround",
    )
    assert sequence.final_output_ids == (
        "front",
        "right",
        "back",
        "left",
        "contact_sheet",
        "normalization_receipt",
    )
    assert tuple(cell.id for cell in sequence.inputs) == (
        "source_image",
        "cleanup_prompt",
        "identity_fidelity",
        "grounding_px",
        "retention_details",
        "execution_profile",
        "duration_frames",
        "tail_fraction",
        "analysis_max_edge",
        "seed",
        "canvas_size",
        "content_height",
        "bottom_padding",
    )

    cleanup_prompt = _cell(sequence, "cleanup_prompt")
    assert "full-body technical front view" in cleanup_prompt.props["lfValue"]
    assert "relaxed A-pose" in cleanup_prompt.props["lfValue"]
    assert "anchor all later angles" in cleanup_prompt.description
    source_image = _cell(sequence, "source_image")
    assert "complete silhouette" in source_image.description
    assert "hands, and feet" in source_image.description


def test_character_turnaround_orchestra_fans_out_and_in_by_named_stage() -> None:
    sequence = character_turnaround_orchestra

    for stage, target_view in zip(
        sequence.stages[1:4],
        ("subject_right", "back", "subject_left"),
    ):
        assert stage.bindings[0] == WorkflowSequenceArtifactBinding(
            "source_image",
            "image",
            source_stage_id="cleanup",
        )
        assert stage.bindings[1] == WorkflowSequenceLiteralBinding(
            "target_view",
            target_view,
        )

    assemble = sequence.stages[-1]
    assert assemble.bindings[:4] == (
        WorkflowSequenceArtifactBinding(
            "front_image", "image", source_stage_id="cleanup"
        ),
        WorkflowSequenceArtifactBinding(
            "right_image", "view", source_stage_id="subject_right"
        ),
        WorkflowSequenceArtifactBinding(
            "back_image", "view", source_stage_id="back"
        ),
        WorkflowSequenceArtifactBinding(
            "left_image", "view", source_stage_id="subject_left"
        ),
    )


def test_character_turnaround_plan_preserves_named_artifact_authority() -> None:
    workflows = {
        identity_edit.id: identity_edit,
        directed_view.id: directed_view,
        assemble_cardinal_turnaround.id: assemble_cardinal_turnaround,
    }
    plan = normalize_sequence_definition(
        character_turnaround_orchestra,
        {"source_image": {"kind": "upload", "name": "character.png"}},
        workflow_resolver=workflows.__getitem__,
        output_node_resolver=_output_node_id,
    )

    assert plan["inputs"]["execution_profile"] == "kitchen_quality"
    assert plan["inputs"]["tail_fraction"] == "0.25"
    assert plan["inputs"]["analysis_max_edge"] == "96"
    cleanup_literals = {
        binding["target_input_id"]: binding["value"]
        for binding in plan["stages"][0]["bindings"]
        if binding["kind"] == "literal"
    }
    assert cleanup_literals == {
        "aspect_ratio": "9:16 (Portrait Widescreen)",
        "steps": 10,
    }
    for stage_index, target_view in zip(
        (1, 2, 3),
        ("subject_right", "back", "subject_left"),
    ):
        stage = plan["stages"][stage_index]
        assert {
            binding["target_input_id"]: binding["value"]
            for binding in stage["bindings"]
            if binding["kind"] == "literal"
        } == {
            "target_view": target_view,
            "aspect_ratio": "9:16",
        }
        source = stage["bindings"][0]
        assert source["source_stage_id"] == "cleanup"
        assert source["source_stage_index"] == 0
        assert source["output_node_id"] == "save"

    assembler_sources = plan["stages"][4]["bindings"][:4]
    assert [source["source_stage_id"] for source in assembler_sources] == [
        "cleanup",
        "subject_right",
        "back",
        "subject_left",
    ]
    assert [source["output_node_id"] for source in assembler_sources] == [
        "save",
        "save_view",
        "save_view",
        "save_view",
    ]
    assert plan["final_outputs"] == [
        {"output_id": "front", "output_node_id": "save_front"},
        {"output_id": "right", "output_node_id": "save_right"},
        {"output_id": "back", "output_node_id": "save_back"},
        {"output_id": "left", "output_node_id": "save_left"},
        {
            "output_id": "contact_sheet",
            "output_node_id": "save_contact_sheet",
        },
        {
            "output_id": "normalization_receipt",
            "output_node_id": "display_normalization_receipt",
        },
    ]


def test_identity_restage_catalogue_folds_stage_readiness(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry = WorkflowRegistry()
    for definition in (identity_edit, character_restage):
        registry.register(
            definition,
            origin="shipped",
            collection="LF Nodes",
        )
    registry.register(
        identity_cleanup_restage,
        origin="shipped",
        collection="LF Nodes",
    )

    def _readiness(definition: Any, **_kwargs: Any) -> dict[str, Any]:
        if definition.id == character_restage.id:
            return {
                "status": "setup_required",
                "issues": [
                    {
                        "code": "model_missing",
                        "message": "The ReID model is missing.",
                    }
                ],
            }
        return {"status": "ready", "issues": []}

    monkeypatch.setattr(registry_module, "evaluate_workflow_readiness", _readiness)
    listed = next(
        node
        for node in registry.list()["nodes"]
        if node["id"] == identity_cleanup_restage.id
    )

    assert listed["origin"] == "shipped"
    assert listed["collection"] == "LF Nodes"
    assert listed["kind"] == "orchestra"
    assert listed["downloadable"] is False
    assert listed["stages"] == [
        {"id": "identity", "workflowId": "krea2_identity_edit"},
        {"id": "restage", "workflowId": "krea2_character_restage"},
    ]
    assert listed["readiness"] == {
        "status": "setup_required",
        "issues": [
            {
                "code": "model_missing",
                "message": "Stage restage: The ReID model is missing.",
            }
        ],
    }
    assert tuple(listed["children"][0]["cells"]) == (
        "identity_image",
        "identity_prompt",
        "restage_prompt",
        "aspect_ratio",
        "seed",
    )
    assert listed["children"][1]["cells"] == {
        "image": _cell(character_restage, "image", ports="outputs").to_dict()
    }
