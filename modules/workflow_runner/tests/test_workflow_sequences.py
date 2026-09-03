from dataclasses import FrozenInstanceError
from pathlib import Path
from types import SimpleNamespace

import pytest

from modules.workflow_runner.services import registry as registry_module
from modules.workflow_runner import workflows as workflows_module
from modules.workflow_runner.services.registry import (
    WorkflowBlockNode,
    WorkflowCell,
    WorkflowInputOptionRequirement,
    WorkflowNode,
    WorkflowOrchestraNode,
    WorkflowRegistry,
    WorkflowSequenceArtifactBinding,
    WorkflowSequenceLiteralBinding,
    WorkflowSequenceNode,
    WorkflowSequencePublicInputBinding,
    WorkflowSequenceStage,
)


def _block(
    workflow_id: str,
    *,
    inputs: tuple[WorkflowCell, ...],
    outputs: tuple[WorkflowCell, ...],
    option_requirements: tuple[WorkflowInputOptionRequirement, ...] = (),
) -> WorkflowNode:
    return WorkflowNode(
        id=workflow_id,
        value=workflow_id.replace("_", " ").title(),
        description=f"The {workflow_id} block.",
        inputs=inputs,
        outputs=outputs,
        configure_prompt=lambda _prompt, _inputs: None,
        configure_download=lambda _prompt, _inputs: None,
        workflow_path=Path(f"{workflow_id}.json"),
        category="Tests",
        input_option_requirements=option_requirements,
    )


def _profile_cell(*, default: str | int = "baseline") -> WorkflowCell:
    return WorkflowCell(
        id="profile",
        node_id="sample",
        shape="select",
        props={
            "lfValue": default,
            "lfDataset": {
                "nodes": [
                    {
                        "id": "baseline",
                        "value": "Baseline",
                        "workflowValue": "baseline",
                    },
                    {
                        "id": "quality",
                        "value": "Quality",
                        "workflowValue": "quality",
                    },
                ]
            },
        },
    )


def _blocks() -> tuple[WorkflowNode, WorkflowNode]:
    cleanup = _block(
        "identity_cleanup",
        inputs=(
            WorkflowCell(id="source", node_id="load", shape="upload"),
            WorkflowCell(id="steps", node_id="sample", shape="textfield"),
        ),
        outputs=(
            WorkflowCell(id="image", node_id="save", shape="masonry"),
        ),
    )
    restage = _block(
        "character_restage",
        inputs=(
            WorkflowCell(id="character", node_id="load", shape="upload"),
            WorkflowCell(id="prompt", node_id="prompt", shape="textfield"),
        ),
        outputs=(
            WorkflowCell(id="result", node_id="save", shape="masonry"),
            WorkflowCell(id="receipt", node_id="receipt", shape="code"),
        ),
    )
    return cleanup, restage


def _sequence(
    *,
    stages: tuple[WorkflowSequenceStage, ...] | None = None,
    final_output_ids: tuple[str, ...] = ("result",),
) -> WorkflowSequenceNode:
    return WorkflowSequenceNode(
        id="identity_to_restage",
        value="Identity to restage",
        description="Clean one identity, then restage the retained character.",
        category="Sequences",
        inputs=(
            WorkflowCell(id="source", node_id="sequence", shape="upload"),
        ),
        stages=stages
        or (
            WorkflowSequenceStage(
                id="cleanup",
                workflow_id="identity_cleanup",
                bindings=(
                    WorkflowSequencePublicInputBinding(
                        target_input_id="source",
                        public_input_id="source",
                    ),
                    WorkflowSequenceLiteralBinding(
                        target_input_id="steps",
                        value=20,
                    ),
                ),
            ),
            WorkflowSequenceStage(
                id="restage",
                workflow_id="character_restage",
                bindings=(
                    WorkflowSequenceArtifactBinding(
                        target_input_id="character",
                        output_id="image",
                    ),
                    WorkflowSequenceLiteralBinding(
                        target_input_id="prompt",
                        value="Thighs-up portrait at the piano.",
                    ),
                ),
            ),
        ),
        final_output_ids=final_output_ids,
    )


def _registry_with_blocks() -> WorkflowRegistry:
    registry = WorkflowRegistry()
    for block in _blocks():
        registry.register(block)
    return registry


def test_author_facing_block_and_orchestra_names_are_compatible_aliases() -> None:
    assert WorkflowBlockNode is WorkflowNode
    assert WorkflowOrchestraNode is WorkflowSequenceNode
    assert isinstance(_blocks()[0], WorkflowBlockNode)
    assert isinstance(_sequence(), WorkflowOrchestraNode)


def test_packaged_registration_is_independent_of_custom_orchestra_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    blocks = _blocks()
    orchestra = _sequence()
    registry = WorkflowRegistry()
    monkeypatch.setattr(registry_module, "REGISTRY", registry)
    monkeypatch.setattr(
        workflows_module,
        "iter_workflow_definitions",
        lambda: iter((orchestra, *blocks)),
    )

    registry_module._register_packaged_workflows()

    assert registry.get(orchestra.id) is orchestra
    kinds = {node["id"]: node["kind"] for node in registry.list()["nodes"]}
    assert kinds == {
        "identity_cleanup": "block",
        "character_restage": "block",
        "identity_to_restage": "orchestra",
    }


def test_packaged_custom_definition_replaces_a_shipped_id(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    shipped = _block("reserved", inputs=(), outputs=())
    shipped.origin = "shipped"
    shipped.collection = "LF Nodes"
    custom = _block("reserved", inputs=(), outputs=())
    registry = WorkflowRegistry()
    monkeypatch.setattr(registry_module, "REGISTRY", registry)
    monkeypatch.setattr(
        workflows_module,
        "iter_workflow_definitions",
        lambda: iter((shipped, custom)),
    )

    with caplog.at_level("WARNING"):
        registry_module._register_packaged_workflows()

    assert registry.get("reserved") is custom
    assert registry.list()["nodes"][0]["origin"] == "custom"
    assert "replaces an existing registration" in caplog.text


def test_custom_orchestra_validates_against_final_custom_block_override(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    custom_cleanup, restage = _blocks()
    shipped_cleanup = _block(
        "identity_cleanup",
        inputs=(
            WorkflowCell(id="source", node_id="load", shape="upload"),
            WorkflowCell(id="steps", node_id="sample", shape="textfield"),
        ),
        outputs=(
            WorkflowCell(id="legacy", node_id="save", shape="masonry"),
        ),
    )
    shipped_cleanup.origin = "shipped"
    shipped_cleanup.collection = "LF Nodes"
    orchestra = _sequence()
    registry = WorkflowRegistry()
    monkeypatch.setattr(registry_module, "REGISTRY", registry)
    monkeypatch.setattr(
        workflows_module,
        "iter_workflow_definitions",
        # The orchestra is deliberately discovered first. The block pass must
        # still apply the custom replacement before validating its `image` wire.
        lambda: iter((orchestra, shipped_cleanup, restage, custom_cleanup)),
    )

    registry_module._register_packaged_workflows()

    assert registry.get("identity_cleanup") is custom_cleanup
    assert registry.get(orchestra.id) is orchestra
    listed = {node["id"]: node for node in registry.list()["nodes"]}
    assert listed["identity_cleanup"]["origin"] == "custom"
    assert listed[orchestra.id]["kind"] == "orchestra"


def test_sequence_declarations_are_immutable_and_own_no_workflow_graph() -> None:
    sequence = _sequence()

    assert isinstance(sequence.inputs, tuple)
    assert isinstance(sequence.stages, tuple)
    assert isinstance(sequence.stages[0].bindings, tuple)
    for forbidden in (
        "workflow_path",
        "configure_prompt",
        "configure_download",
        "required_model_assets",
        "submission_policy",
    ):
        assert not hasattr(sequence, forbidden)

    with pytest.raises(FrozenInstanceError):
        sequence.category = "Changed"  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        sequence.stages[0].id = "changed"  # type: ignore[misc]


@pytest.mark.parametrize("value", ({"mutable": True}, ["mutable"], float("nan")))
def test_fixed_bindings_accept_only_immutable_json_scalars(value: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        WorkflowSequenceLiteralBinding(target_input_id="steps", value=value)  # type: ignore[arg-type]


def test_sequence_shape_rejects_duplicate_and_out_of_range_declarations() -> None:
    binding = WorkflowSequenceLiteralBinding(target_input_id="steps", value=8)
    with pytest.raises(ValueError, match="must not overlap"):
        WorkflowSequenceStage(
            id="cleanup",
            workflow_id="identity_cleanup",
            bindings=(binding, binding),
        )

    duplicate_stage = WorkflowSequenceStage(
        id="same",
        workflow_id="identity_cleanup",
    )
    with pytest.raises(ValueError, match="stage ids must be unique"):
        _sequence(stages=(duplicate_stage, duplicate_stage))

    with pytest.raises(ValueError, match="between 2 and 8"):
        _sequence(stages=(duplicate_stage,))

    with pytest.raises(ValueError, match="final output ids must be unique"):
        _sequence(final_output_ids=("result", "result"))


def test_sequence_registration_validates_references_and_ports() -> None:
    registry = _registry_with_blocks()
    sequence = _sequence()

    registry.register(sequence, origin="shipped", collection="LF Nodes")

    assert registry.get(sequence.id) is sequence


def test_sequence_registration_supports_named_earlier_artifact_fan_out() -> None:
    registry = _registry_with_blocks()
    sequence = _sequence(
        stages=(
            WorkflowSequenceStage(
                id="cleanup",
                workflow_id="identity_cleanup",
                bindings=(
                    WorkflowSequencePublicInputBinding("source", "source"),
                    WorkflowSequenceLiteralBinding("steps", 20),
                ),
            ),
            WorkflowSequenceStage(
                id="right",
                workflow_id="character_restage",
                bindings=(
                    WorkflowSequenceArtifactBinding(
                        "character",
                        "image",
                        source_stage_id="cleanup",
                    ),
                    WorkflowSequenceLiteralBinding("prompt", "Right view."),
                ),
            ),
            WorkflowSequenceStage(
                id="left",
                workflow_id="character_restage",
                bindings=(
                    WorkflowSequenceArtifactBinding(
                        "character",
                        "image",
                        source_stage_id="cleanup",
                    ),
                    WorkflowSequenceLiteralBinding("prompt", "Left view."),
                ),
            ),
        )
    )

    registry.register(sequence)

    assert registry.get(sequence.id) is sequence


@pytest.mark.parametrize(
    ("consumer_index", "source_stage_id", "message"),
    (
        (1, "missing", "unknown source stage 'missing'"),
        (1, "right", "cannot consume an artifact from itself"),
        (1, "left", "references future source stage 'left'"),
    ),
)
def test_sequence_registration_rejects_non_earlier_named_artifact_sources(
    consumer_index: int,
    source_stage_id: str,
    message: str,
) -> None:
    stages = [
        WorkflowSequenceStage(
            id="cleanup",
            workflow_id="identity_cleanup",
            bindings=(
                WorkflowSequencePublicInputBinding("source", "source"),
                WorkflowSequenceLiteralBinding("steps", 20),
            ),
        ),
        WorkflowSequenceStage(
            id="right",
            workflow_id="character_restage",
            bindings=(
                WorkflowSequenceArtifactBinding(
                    "character",
                    "image",
                    source_stage_id="cleanup",
                ),
                WorkflowSequenceLiteralBinding("prompt", "Right view."),
            ),
        ),
        WorkflowSequenceStage(
            id="left",
            workflow_id="character_restage",
            bindings=(
                WorkflowSequenceArtifactBinding(
                    "character",
                    "image",
                    source_stage_id="cleanup",
                ),
                WorkflowSequenceLiteralBinding("prompt", "Left view."),
            ),
        ),
    ]
    consumer = stages[consumer_index]
    stages[consumer_index] = WorkflowSequenceStage(
        id=consumer.id,
        workflow_id=consumer.workflow_id,
        bindings=(
            WorkflowSequenceArtifactBinding(
                "character",
                "image",
                source_stage_id=source_stage_id,
            ),
            WorkflowSequenceLiteralBinding("prompt", "Directed view."),
        ),
    )

    with pytest.raises(ValueError, match=message):
        _registry_with_blocks().register(_sequence(stages=tuple(stages)))


@pytest.mark.parametrize(
    ("target_input_id", "output_id", "message"),
    (
        ("character", "unknown", "unknown output port 'unknown'.*source stage 'cleanup'"),
        ("prompt", "image", "must be an upload input"),
    ),
)
def test_named_artifact_sources_still_validate_source_output_and_target_port(
    target_input_id: str,
    output_id: str,
    message: str,
) -> None:
    sequence = _sequence(
        stages=(
            WorkflowSequenceStage(
                id="cleanup",
                workflow_id="identity_cleanup",
                bindings=(
                    WorkflowSequencePublicInputBinding("source", "source"),
                    WorkflowSequenceLiteralBinding("steps", 20),
                ),
            ),
            WorkflowSequenceStage(
                id="restage",
                workflow_id="character_restage",
                bindings=(
                    WorkflowSequenceArtifactBinding(
                        target_input_id,
                        output_id,
                        source_stage_id="cleanup",
                    ),
                    *(
                        (
                            WorkflowSequenceArtifactBinding(
                                "character",
                                "image",
                                source_stage_id="cleanup",
                            ),
                        )
                        if target_input_id != "character"
                        else ()
                    ),
                    *(
                        (WorkflowSequenceLiteralBinding("prompt", "Restage."),)
                        if target_input_id != "prompt"
                        else ()
                    ),
                ),
            ),
        )
    )

    with pytest.raises(ValueError, match=message):
        _registry_with_blocks().register(sequence)


def test_packaged_provenance_wrapper_preserves_an_immutable_sequence() -> None:
    registry = _registry_with_blocks()
    sequence = _sequence()
    wrapped = SimpleNamespace(
        _definition=sequence,
        origin="shipped",
        collection="LF Nodes",
    )

    assert registry_module._is_workflow_definition(wrapped) is True
    registry.register(
        wrapped,  # type: ignore[arg-type]
        origin=wrapped.origin,
        collection=wrapped.collection,
    )

    assert registry.get(sequence.id) is sequence


def test_required_block_inputs_need_a_binding_or_declaration_default() -> None:
    registry = _registry_with_blocks()
    incomplete = _sequence(
        stages=(
            WorkflowSequenceStage(
                id="cleanup",
                workflow_id="identity_cleanup",
                bindings=(
                    WorkflowSequencePublicInputBinding("source", "source"),
                    # ``steps`` is intentionally missing and has no lfValue.
                ),
            ),
            WorkflowSequenceStage(
                id="restage",
                workflow_id="character_restage",
                bindings=(
                    WorkflowSequenceArtifactBinding("character", "image"),
                    WorkflowSequenceLiteralBinding("prompt", "Restage."),
                ),
            ),
        )
    )

    with pytest.raises(
        ValueError,
        match=r"must bind required input\(s\).*steps",
    ):
        registry.register(incomplete)

    first, second = _blocks()
    first.inputs[1].props["lfValue"] = 8
    registry = WorkflowRegistry()
    registry.register(first)
    registry.register(second)
    registry.register(incomplete)


def test_sequence_rejects_an_unregistered_or_nested_block() -> None:
    registry = _registry_with_blocks()
    missing = _sequence(
        stages=(
            WorkflowSequenceStage(id="first", workflow_id="missing"),
            WorkflowSequenceStage(id="second", workflow_id="character_restage"),
        )
    )
    with pytest.raises(ValueError, match="unregistered workflow 'missing'"):
        registry.register(missing)

    registry.register(_sequence())
    nested = WorkflowSequenceNode(
        id="nested",
        value="Nested",
        description="A forbidden nested sequence.",
        category="Sequences",
        inputs=(),
        stages=(
            WorkflowSequenceStage(
                id="nested_first",
                workflow_id="identity_to_restage",
            ),
            WorkflowSequenceStage(
                id="ordinary_last",
                workflow_id="character_restage",
            ),
        ),
        final_output_ids=("result",),
    )
    with pytest.raises(ValueError, match="sequence nesting is not supported"):
        registry.register(nested)


def test_sequence_rejects_a_block_without_portable_preflight() -> None:
    first, second = _blocks()
    second.configure_download = None
    registry = WorkflowRegistry()
    registry.register(first)
    registry.register(second)

    with pytest.raises(ValueError, match="without a portable configure_download"):
        registry.register(_sequence())


@pytest.mark.parametrize(
    ("stages", "message"),
    [
        (
            (
                WorkflowSequenceStage(
                    id="cleanup",
                    workflow_id="identity_cleanup",
                    bindings=(
                        WorkflowSequenceLiteralBinding("unknown", 8),
                    ),
                ),
                WorkflowSequenceStage(id="restage", workflow_id="character_restage"),
            ),
            "unknown input port 'unknown'",
        ),
        (
            (
                WorkflowSequenceStage(
                    id="cleanup",
                    workflow_id="identity_cleanup",
                    bindings=(
                        WorkflowSequencePublicInputBinding("source", "unknown"),
                    ),
                ),
                WorkflowSequenceStage(id="restage", workflow_id="character_restage"),
            ),
            "unknown public input 'unknown'",
        ),
        (
            (
                WorkflowSequenceStage(
                    id="cleanup",
                    workflow_id="identity_cleanup",
                    bindings=(
                        WorkflowSequenceArtifactBinding("source", "image"),
                    ),
                ),
                WorkflowSequenceStage(id="restage", workflow_id="character_restage"),
            ),
            "first sequence stage cannot bind a previous artifact",
        ),
        (
            (
                WorkflowSequenceStage(
                    id="cleanup",
                    workflow_id="identity_cleanup",
                    bindings=(
                        WorkflowSequencePublicInputBinding("source", "source"),
                        WorkflowSequenceLiteralBinding("steps", 8),
                    ),
                ),
                WorkflowSequenceStage(
                    id="restage",
                    workflow_id="character_restage",
                    bindings=(
                        WorkflowSequenceArtifactBinding("character", "unknown"),
                    ),
                ),
            ),
            "unknown output port 'unknown'",
        ),
        (
            (
                WorkflowSequenceStage(
                    id="cleanup",
                    workflow_id="identity_cleanup",
                    bindings=(
                        WorkflowSequencePublicInputBinding("source", "source"),
                        WorkflowSequenceLiteralBinding("steps", 8),
                    ),
                ),
                WorkflowSequenceStage(
                    id="restage",
                    workflow_id="character_restage",
                    bindings=(
                        WorkflowSequenceArtifactBinding("prompt", "image"),
                    ),
                ),
            ),
            "must be an upload input",
        ),
    ],
)
def test_sequence_registration_rejects_invalid_bindings(
    stages: tuple[WorkflowSequenceStage, ...],
    message: str,
) -> None:
    registry = _registry_with_blocks()

    with pytest.raises(ValueError, match=message):
        registry.register(_sequence(stages=stages))


def test_sequence_rejects_unknown_or_ambiguous_final_ports() -> None:
    registry = _registry_with_blocks()
    with pytest.raises(ValueError, match=r"unknown port\(s\): missing"):
        registry.register(_sequence(final_output_ids=("missing",)))

    first, _second = _blocks()
    ambiguous = _block(
        "ambiguous",
        inputs=(WorkflowCell(id="source", node_id="load", shape="upload"),),
        outputs=(
            WorkflowCell(id="result", node_id="one", shape="masonry"),
            WorkflowCell(id="result", node_id="two", shape="masonry"),
        ),
    )
    registry = WorkflowRegistry()
    registry.register(first)
    registry.register(ambiguous)
    sequence = _sequence(
        stages=(
            WorkflowSequenceStage(
                id="first",
                workflow_id=first.id,
                bindings=(
                    WorkflowSequencePublicInputBinding("source", "source"),
                    WorkflowSequenceLiteralBinding("steps", 8),
                ),
            ),
            WorkflowSequenceStage(
                id="last",
                workflow_id=ambiguous.id,
                bindings=(WorkflowSequenceArtifactBinding("source", "image"),),
            ),
        )
    )
    with pytest.raises(ValueError, match="duplicate outputs ports"):
        registry.register(sequence)


def test_catalogue_projects_sequence_inputs_and_final_block_outputs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry = _registry_with_blocks()
    registry.register(_sequence(), origin="shipped", collection="LF Nodes")

    def readiness(definition: WorkflowNode, **_kwargs):
        if definition.id == "identity_cleanup":
            return {
                "status": "warning",
                "issues": [{"code": "warmup", "message": "Warmup is uncertain."}],
            }
        if definition.id == "character_restage":
            return {
                "status": "setup_required",
                "issues": [{"code": "model_missing", "message": "Model is missing."}],
            }
        return {"status": "ready", "issues": []}

    monkeypatch.setattr(registry_module, "evaluate_workflow_readiness", readiness)
    listed = next(
        node for node in registry.list()["nodes"] if node["id"] == "identity_to_restage"
    )

    assert listed == {
        "id": "identity_to_restage",
        "value": "Identity to restage",
        "description": "Clean one identity, then restage the retained character.",
        "category": "Sequences",
        "origin": "shipped",
        "collection": "LF Nodes",
        "readiness": {
            "status": "setup_required",
            "issues": [
                {
                    "code": "model_missing",
                    "message": "Stage restage: Model is missing.",
                },
                {
                    "code": "warmup",
                    "message": "Stage cleanup: Warmup is uncertain.",
                },
            ],
        },
        "children": [
            {
                "id": "identity_to_restage:inputs",
                "value": "Inputs",
                "description": "Workflow inputs",
                "cells": {
                    "source": {
                        "id": "source",
                        "nodeId": "sequence",
                        "shape": "upload",
                    }
                },
            },
            {
                "id": "identity_to_restage:outputs",
                "value": "Outputs",
                "description": "Workflow outputs",
                "cells": {
                    "result": {
                        "id": "result",
                        "nodeId": "save",
                        "shape": "masonry",
                    }
                },
            },
        ],
        "kind": "orchestra",
        "downloadable": False,
        "stages": [
            {"id": "cleanup", "workflowId": "identity_cleanup"},
            {"id": "restage", "workflowId": "character_restage"},
        ],
    }
    assert "bindings" not in repr(listed)
    assert "source_stage_id" not in repr(listed)


def test_sequence_readiness_checks_a_fixed_optional_block_recipe(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    requirement = WorkflowInputOptionRequirement(
        input_id="profile",
        option_value="quality",
        required_node_types=("QualitySampler",),
    )
    first, _ = _blocks()
    second = _block(
        "optional_restage",
        inputs=(
            WorkflowCell(id="character", node_id="load", shape="upload"),
            WorkflowCell(
                id="guidance",
                node_id="sample",
                shape="textfield",
                props={"lfValue": "3.5"},
            ),
            WorkflowCell(
                id="profile",
                node_id="sample",
                shape="select",
                props={"lfValue": "baseline"},
            ),
        ),
        outputs=(WorkflowCell(id="result", node_id="save", shape="masonry"),),
        option_requirements=(requirement,),
    )
    registry = WorkflowRegistry()
    registry.register(first)
    registry.register(second)
    registry.register(
        _sequence(
            stages=(
                WorkflowSequenceStage(
                    id="first",
                    workflow_id=first.id,
                    bindings=(
                        WorkflowSequencePublicInputBinding("source", "source"),
                        WorkflowSequenceLiteralBinding("steps", 8),
                    ),
                ),
                WorkflowSequenceStage(
                    id="quality",
                    workflow_id=second.id,
                    bindings=(
                        WorkflowSequenceArtifactBinding("character", "image"),
                        WorkflowSequenceLiteralBinding("profile", "quality"),
                    ),
                ),
            )
        )
    )
    readiness_calls = {}

    def ready(definition, **kwargs):
        readiness_calls[definition.id] = kwargs
        return {"status": "ready", "issues": []}

    monkeypatch.setattr(
        registry_module,
        "evaluate_workflow_readiness",
        ready,
    )
    monkeypatch.setattr(
        registry_module,
        "evaluate_input_option_requirement",
        lambda _requirement, **_kwargs: {
            "status": "setup_required",
            "issues": [
                {"code": "option_node_missing", "message": "Quality is unavailable."}
            ],
        },
    )

    listed = next(
        node for node in registry.list()["nodes"] if node["id"] == "identity_to_restage"
    )

    assert listed["readiness"] == {
        "status": "setup_required",
        "issues": [
            {
                "code": "option_node_missing",
                "message": "Stage quality: Quality is unavailable.",
            }
        ],
    }
    assert readiness_calls["identity_cleanup"]["inputs"] == {"steps": 8}
    assert readiness_calls["identity_cleanup"]["replaceable_input_ids"] == {
        "source"
    }
    assert readiness_calls["optional_restage"]["inputs"] == {
        "guidance": "3.5",
        "profile": "quality",
    }
    assert readiness_calls["optional_restage"]["replaceable_input_ids"] == set()


def test_public_sequence_option_is_filtered_and_its_default_marks_readiness(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    requirement = WorkflowInputOptionRequirement(
        input_id="profile",
        option_value="quality",
        required_node_types=("QualitySampler",),
    )
    first, _ = _blocks()
    second = _block(
        "optional_restage",
        inputs=(
            WorkflowCell(id="character", node_id="load", shape="upload"),
            _profile_cell(),
        ),
        outputs=(WorkflowCell(id="result", node_id="save", shape="masonry"),),
        option_requirements=(requirement,),
    )
    sequence = WorkflowSequenceNode(
        id="public_profile_sequence",
        value="Public profile sequence",
        description="Exercise a gated block profile through a public control.",
        category="Sequences",
        inputs=(
            WorkflowCell(id="source", node_id="sequence", shape="upload"),
            # The browser/runtime interpret an integer select default as an
            # option index, so this deliberately selects ``quality``.
            _profile_cell(default=1),
        ),
        stages=(
            WorkflowSequenceStage(
                id="first",
                workflow_id=first.id,
                bindings=(
                    WorkflowSequencePublicInputBinding("source", "source"),
                    WorkflowSequenceLiteralBinding("steps", 8),
                ),
            ),
            WorkflowSequenceStage(
                id="restage",
                workflow_id=second.id,
                bindings=(
                    WorkflowSequenceArtifactBinding("character", "image"),
                    WorkflowSequencePublicInputBinding("profile", "profile"),
                ),
            ),
        ),
        final_output_ids=("result",),
    )
    registry = WorkflowRegistry()
    registry.register(first)
    registry.register(second)
    registry.register(sequence)
    monkeypatch.setattr(
        registry_module,
        "evaluate_workflow_readiness",
        lambda _definition, **_kwargs: {"status": "ready", "issues": []},
    )
    monkeypatch.setattr(
        registry_module,
        "evaluate_input_option_requirement",
        lambda _requirement, **_kwargs: {
            "status": "setup_required",
            "issues": [
                {
                    "code": "option_node_missing",
                    "message": "Quality is unavailable.",
                }
            ],
        },
    )

    listed = next(
        node for node in registry.list()["nodes"] if node["id"] == sequence.id
    )
    profile = listed["children"][0]["cells"]["profile"]

    assert [
        option["workflowValue"]
        for option in profile["props"]["lfDataset"]["nodes"]
    ] == ["baseline"]
    assert listed["readiness"] == {
        "status": "setup_required",
        "issues": [
            {
                "code": "option_node_missing",
                "message": "Stage restage: Quality is unavailable.",
            }
        ],
    }


def test_shared_public_option_fails_closed_across_multiple_block_bindings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first_requirement = WorkflowInputOptionRequirement(
        input_id="profile",
        option_value="quality",
        required_node_types=("UnavailableFirstSampler",),
    )
    second_requirement = WorkflowInputOptionRequirement(
        input_id="profile",
        option_value="quality",
        required_node_types=("AvailableSecondSampler",),
    )
    first = _block(
        "first_profile_block",
        inputs=(
            WorkflowCell(id="source", node_id="load", shape="upload"),
            _profile_cell(),
        ),
        outputs=(WorkflowCell(id="image", node_id="save", shape="masonry"),),
        option_requirements=(first_requirement,),
    )
    second = _block(
        "second_profile_block",
        inputs=(
            WorkflowCell(id="character", node_id="load", shape="upload"),
            _profile_cell(),
        ),
        outputs=(WorkflowCell(id="result", node_id="save", shape="masonry"),),
        option_requirements=(second_requirement,),
    )
    sequence = WorkflowSequenceNode(
        id="shared_profile_sequence",
        value="Shared profile sequence",
        description="Share one profile across two independently gated blocks.",
        category="Sequences",
        inputs=(
            WorkflowCell(id="source", node_id="sequence", shape="upload"),
            _profile_cell(),
        ),
        stages=(
            WorkflowSequenceStage(
                id="first",
                workflow_id=first.id,
                bindings=(
                    WorkflowSequencePublicInputBinding("source", "source"),
                    WorkflowSequencePublicInputBinding("profile", "profile"),
                ),
            ),
            WorkflowSequenceStage(
                id="second",
                workflow_id=second.id,
                bindings=(
                    WorkflowSequenceArtifactBinding("character", "image"),
                    WorkflowSequencePublicInputBinding("profile", "profile"),
                ),
            ),
        ),
        final_output_ids=("result",),
    )
    registry = WorkflowRegistry()
    registry.register(first)
    registry.register(second)
    registry.register(sequence)
    monkeypatch.setattr(
        registry_module,
        "evaluate_workflow_readiness",
        lambda _definition, **_kwargs: {"status": "ready", "issues": []},
    )

    def option_readiness(requirement, **_kwargs):
        unavailable = "UnavailableFirstSampler" in requirement.required_node_types
        return {
            "status": "setup_required" if unavailable else "ready",
            "issues": (
                [{"code": "option_node_missing", "message": "First is unavailable."}]
                if unavailable
                else []
            ),
        }

    monkeypatch.setattr(
        registry_module,
        "evaluate_input_option_requirement",
        option_readiness,
    )

    listed = next(
        node for node in registry.list()["nodes"] if node["id"] == sequence.id
    )
    profile = listed["children"][0]["cells"]["profile"]

    # A flattened public-input mapping would let the later ready requirement
    # overwrite the first blocker and incorrectly advertise ``quality``.
    assert [
        option["workflowValue"]
        for option in profile["props"]["lfDataset"]["nodes"]
    ] == ["baseline"]


def test_replacing_a_referenced_block_cannot_silently_invalidate_a_sequence() -> None:
    registry = _registry_with_blocks()
    registry.register(_sequence())
    incompatible = _block(
        "character_restage",
        inputs=(WorkflowCell(id="prompt", node_id="prompt", shape="textfield"),),
        outputs=(WorkflowCell(id="other", node_id="save", shape="masonry"),),
    )

    with pytest.raises(ValueError, match="unknown input port 'character'"):
        registry.register(incompatible)

    assert registry.get("character_restage") is not incompatible
    WorkflowOrchestraNode,
