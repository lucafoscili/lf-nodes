from __future__ import annotations

import sys

from types import ModuleType, SimpleNamespace
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio

from modules.workflow_runner.services import (
    job_store,
    lifecycle,
    sequence_runtime,
    sequence_store,
)


pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest_asyncio.fixture(autouse=True)
async def reset_sequence_runtime_state():
    await sequence_runtime.stop_sequence_supervisors()
    await sequence_store.reset_for_tests()
    yield
    await sequence_runtime.stop_sequence_supervisors()
    await sequence_store.reset_for_tests()


def _public(target: str, source: str):
    return SimpleNamespace(target_input_id=target, public_input_id=source)


def _literal(target: str, value):
    return SimpleNamespace(target_input_id=target, value=value)


def _artifact(
    target: str,
    output_id: str,
    source_stage_id: str | None = None,
):
    return SimpleNamespace(
        target_input_id=target,
        output_id=output_id,
        source_stage_id=source_stage_id,
    )


def _stage(stage_id: str, workflow_id: str, *bindings):
    return SimpleNamespace(id=stage_id, workflow_id=workflow_id, bindings=bindings)


def _sequence(*stages, sequence_id: str = "portrait_monument"):
    return SimpleNamespace(id=sequence_id, stages=stages)


def _declared_sequence(*stages, sequence_id: str = "portrait_monument"):
    return SimpleNamespace(
        id=sequence_id,
        stages=stages,
        final_output_ids=("image",),
    )


def _empty_block(_workflow_id: str):
    return SimpleNamespace(inputs=())


def _result(label: str) -> dict:
    return {
        "http_status": 200,
        "body": {"payload": {"history": {"outputs": {"save": {"label": label}}}}},
    }


async def _create_bound_child(
    payload: dict,
    run_id: str,
    owner_id: str | None,
) -> None:
    submission_id = payload["submissionId"]
    await job_store.create_job(
        run_id,
        payload["workflowId"],
        owner_id=owner_id,
        submission_id=submission_id,
        request_fingerprint=lifecycle._fingerprint_payload(payload),
        comfy_url="http://comfy.test:8188",
    )


def test_normalization_is_linear_bounded_and_child_ids_are_deterministic() -> None:
    definition = _sequence(
        _stage("clean", "identity_clean", _public("reference", "source")),
        _stage("restage", "character_restage", _artifact("reference", "image")),
    )
    plan = sequence_runtime.normalize_sequence_definition(
        definition,
        {"source": "input.png"},
        output_node_resolver=lambda workflow_id, output_id: f"{workflow_id}:{output_id}",
        workflow_resolver=_empty_block,
    )

    assert plan["stages"][1]["bindings"][0] == {
        "kind": "artifact",
        "target_input_id": "reference",
        "output_id": "image",
        "output_node_id": "identity_clean:image",
    }
    assert plan["definition_fingerprint"] == (
        "5f01b1f7da95aa4d142ed2b6565e2dbc3ac391f48aa3618424721e379304cfd6"
    )
    first = sequence_runtime.child_submission_id(
        "lf-sequence:parent", 1, "restage"
    )
    assert first == sequence_runtime.child_submission_id(
        "lf-sequence:parent", 1, "restage"
    )
    assert first != sequence_runtime.child_submission_id(
        "lf-sequence:other", 1, "restage"
    )
    assert sequence_runtime.is_sequence_parent_run_id("lf-sequence:parent")
    assert sequence_runtime.is_sequence_child_submission_id(first)

    with pytest.raises(ValueError, match="first sequence stage"):
        sequence_runtime.normalize_sequence_definition(
            _sequence(
                _stage("bad", "workflow", _artifact("reference", "image")),
                _stage("later", "other"),
            ),
            {},
            output_node_resolver=lambda _workflow_id, _output_id: "save",
            workflow_resolver=_empty_block,
        )


def test_normalization_freezes_an_explicit_earlier_artifact_source() -> None:
    definition = _sequence(
        _stage("clean", "identity_clean", _public("reference", "source")),
        _stage(
            "right",
            "directed_view",
            _artifact("reference", "image", "clean"),
        ),
        _stage(
            "left",
            "directed_view",
            _artifact("reference", "image", "clean"),
        ),
    )
    plan = sequence_runtime.normalize_sequence_definition(
        definition,
        {"source": "input.png"},
        output_node_resolver=lambda workflow_id, output_id: f"{workflow_id}:{output_id}",
        workflow_resolver=_empty_block,
    )

    expected = {
        "kind": "artifact",
        "target_input_id": "reference",
        "source_stage_id": "clean",
        "source_stage_index": 0,
        "output_id": "image",
        "output_node_id": "identity_clean:image",
    }
    assert plan["stages"][1]["bindings"][0] == expected
    assert plan["stages"][2]["bindings"][0] == expected


@pytest.mark.parametrize(
    ("source_stage_id", "message"),
    (
        ("missing", "unknown artifact source stage 'missing'"),
        ("right", "cannot consume an artifact from itself"),
        ("left", "future artifact source stage 'left'"),
    ),
)
def test_normalization_rejects_non_earlier_named_artifact_sources(
    source_stage_id: str,
    message: str,
) -> None:
    definition = _sequence(
        _stage("clean", "identity_clean", _public("reference", "source")),
        _stage(
            "right",
            "directed_view",
            _artifact("reference", "image", source_stage_id),
        ),
        _stage("left", "directed_view"),
    )

    with pytest.raises(ValueError, match=message):
        sequence_runtime.normalize_sequence_definition(
            definition,
            {"source": "input.png"},
            output_node_resolver=lambda _workflow_id, _output_id: "save",
            workflow_resolver=_empty_block,
        )


def test_runtime_consumes_the_exact_registry_declaration_types() -> None:
    from modules.workflow_runner.services.registry import (
        WorkflowCell,
        WorkflowSequenceArtifactBinding,
        WorkflowSequenceLiteralBinding,
        WorkflowSequenceNode,
        WorkflowSequencePublicInputBinding,
        WorkflowSequenceStage,
    )

    definition = WorkflowSequenceNode(
        id="exact_types",
        value="Exact types",
        description="Declaration/runtime seam.",
        category="Tests",
        inputs=(WorkflowCell(id="source", node_id="sequence", shape="upload"),),
        stages=(
            WorkflowSequenceStage(
                id="clean",
                workflow_id="identity_clean",
                bindings=(
                    WorkflowSequencePublicInputBinding("reference", "source"),
                    WorkflowSequenceLiteralBinding("steps", 20),
                ),
            ),
            WorkflowSequenceStage(
                id="restage",
                workflow_id="character_restage",
                bindings=(WorkflowSequenceArtifactBinding("reference", "image"),),
            ),
        ),
        final_output_ids=("image",),
    )
    plan = sequence_runtime.normalize_sequence_definition(
        definition,
        {"source": "input.png"},
        output_node_resolver=lambda _workflow_id, _output_id: "save",
        workflow_resolver=_empty_block,
    )

    assert [binding["kind"] for binding in plan["stages"][0]["bindings"]] == [
        "public_input",
        "literal",
    ]
    assert plan["stages"][1]["bindings"][0]["kind"] == "artifact"
    assert plan["final_outputs"] == [
        {"output_id": "image", "output_node_id": "save"}
    ]
    assert sequence_runtime.sequence_stage_declared_inputs(plan, 0) == {
        "reference": "input.png",
        "steps": 20,
    }
    assert sequence_runtime.sequence_stage_declared_inputs(plan, 1) == {}


def test_omitted_public_defaults_are_semantic_and_required_upload_stays_required() -> None:
    from modules.workflow_runner.services.registry import (
        WorkflowCell,
        WorkflowSequenceLiteralBinding,
        WorkflowSequenceNode,
        WorkflowSequencePublicInputBinding,
        WorkflowSequenceStage,
    )

    definition = WorkflowSequenceNode(
        id="public_defaults",
        value="Public defaults",
        description="Headless defaults.",
        category="Tests",
        inputs=(
            WorkflowCell(id="source", node_id="sequence", shape="upload"),
            WorkflowCell(
                id="prompt",
                node_id="sequence",
                shape="textfield",
                props={"lfValue": "preserve the face"},
            ),
            WorkflowCell(
                id="steps",
                node_id="sequence",
                shape="select",
                props={
                    "lfValue": "10",
                    "lfDataset": {
                        "nodes": [
                            {"id": "8", "value": "Fast", "workflowValue": 8},
                            {"id": "10", "value": "Baseline", "workflowValue": 10},
                        ]
                    },
                },
            ),
        ),
        stages=(
            WorkflowSequenceStage(
                id="clean",
                workflow_id="identity_clean",
                bindings=(
                    WorkflowSequencePublicInputBinding("reference", "source"),
                    WorkflowSequencePublicInputBinding("prompt", "prompt"),
                    WorkflowSequencePublicInputBinding("steps", "steps"),
                ),
            ),
            WorkflowSequenceStage(
                id="save",
                workflow_id="save_block",
                bindings=(WorkflowSequenceLiteralBinding("prefix", "clean"),),
            ),
        ),
        final_output_ids=("image",),
    )
    plan = sequence_runtime.normalize_sequence_definition(
        definition,
        {"source": "input.png"},
        output_node_resolver=lambda _workflow_id, _output_id: "save",
        workflow_resolver=_empty_block,
    )
    assert plan["inputs"] == {
        "source": "input.png",
        "prompt": "preserve the face",
        "steps": 10,
    }

    with pytest.raises(ValueError, match="required public input.*source"):
        sequence_runtime.normalize_sequence_definition(
            definition,
            {},
            output_node_resolver=lambda _workflow_id, _output_id: "save",
            workflow_resolver=_empty_block,
        )


async def test_two_stage_sequence_wires_opaque_artifact_and_projects_final_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    definition = _sequence(
        _stage(
            "clean",
            "identity_clean",
            _public("reference", "source"),
            _literal("steps", 20),
        ),
        _stage(
            "restage",
            "character_restage",
            _artifact("reference", "image"),
            _literal("framing", "thighs-up"),
        ),
    )
    calls: list[dict] = []

    async def run_child(payload, *, owner_id):
        calls.append(payload)
        run_id = f"child-{len(calls)}"
        await _create_bound_child(payload, run_id, owner_id)
        await job_store.set_job_status(
            run_id,
            job_store.JobStatus.SUCCEEDED,
            result=_result(payload["workflowId"]),
        )
        return {"run_id": run_id, "submission_id": payload["submissionId"]}

    monkeypatch.setattr(
        sequence_runtime,
        "project_public_output_artifacts",
        lambda run_id, _result_value: [
            {
                "nodeId": "save",
                "available": True,
                "reference": {
                    "schema": "lf.workflow-artifact-ref.v1",
                    "sourceRunId": run_id,
                    "artifactId": "a" * 64,
                    "filename": "candidate.png",
                },
            }
        ],
    )
    parent_id = "lf-sequence:two-stage"
    await sequence_runtime.create_sequence_execution(
        definition,
        {"source": "input.png"},
        owner_id="owner",
        parent_run_id=parent_id,
        output_node_resolver=lambda _workflow_id, _output_id: "save",
        workflow_resolver=_empty_block,
    )
    terminal = await sequence_runtime.drive_sequence_execution(
        parent_id,
        child_runner=run_child,
        poll_interval=0,
    )

    assert terminal["status"] == "succeeded"
    assert [call["workflowId"] for call in calls] == [
        "identity_clean",
        "character_restage",
    ]
    assert calls[0]["inputs"] == {"reference": "input.png", "steps": 20}
    assert calls[1]["inputs"]["reference"] == {
        "schema": "lf.workflow-artifact-ref.v1",
        "sourceRunId": "child-1",
        "artifactId": "a" * 64,
        "filename": "candidate.png",
    }
    assert calls[1]["inputs"]["framing"] == "thighs-up"
    assert calls[0]["submissionId"] == sequence_runtime.child_submission_id(
        parent_id, 0, "clean"
    )
    assert calls[1]["submissionId"] == sequence_runtime.child_submission_id(
        parent_id, 1, "restage"
    )

    parent = await job_store.get_job(parent_id)
    final_child = await job_store.get_job("child-2")
    assert parent is not None and parent.status == job_store.JobStatus.SUCCEEDED
    assert final_child is not None and parent.result == final_child.result
    assert await sequence_runtime.delete_sequence_execution_state(parent_id) is False

    # Private child cleanup cannot erase or resurrect public terminal history.
    await job_store.remove_job("child-2")
    await sequence_runtime.resume_sequence_executions()
    preserved = await job_store.get_job(parent_id)
    assert preserved is not None and preserved.result == parent.result
    await job_store.remove_job(parent_id)
    await sequence_runtime.resume_sequence_executions()
    assert await job_store.get_job(parent_id) is None
    replayed = await sequence_runtime.create_sequence_execution(
        definition,
        {"source": "input.png"},
        owner_id="owner",
        parent_run_id=parent_id,
        output_node_resolver=lambda _workflow_id, _output_id: "save",
        workflow_resolver=_empty_block,
    )
    assert replayed["status"] == "succeeded"
    assert await job_store.get_job(parent_id) is None
    assert await sequence_runtime.delete_sequence_execution_state(parent_id) is True


async def test_named_sources_fan_out_and_fan_in_after_recovery(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    definition = _sequence(
        _stage("cleanup", "identity_cleanup", _public("reference", "source")),
        _stage(
            "right",
            "directed_view",
            _artifact("reference", "image", "cleanup"),
        ),
        _stage(
            "back",
            "directed_view",
            _artifact("reference", "image", "cleanup"),
        ),
        _stage(
            "left",
            "directed_view",
            _artifact("reference", "image", "cleanup"),
        ),
        _stage(
            "sheet",
            "assemble_cardinal_turnaround",
            _artifact("front_image", "image", "cleanup"),
            _artifact("right_image", "image", "right"),
            _artifact("back_image", "image", "back"),
            _artifact("left_image", "image", "left"),
        ),
    )
    calls: list[dict] = []

    async def run_child(payload, *, owner_id):
        calls.append(payload)
        run_id = f"named-child-{len(calls)}"
        await _create_bound_child(payload, run_id, owner_id)
        await job_store.set_job_status(
            run_id,
            job_store.JobStatus.SUCCEEDED,
            result=_result(payload["workflowId"]),
        )
        return {"run_id": run_id, "submission_id": payload["submissionId"]}

    monkeypatch.setattr(
        sequence_runtime,
        "project_public_output_artifacts",
        lambda run_id, _result_value: [
            {
                "nodeId": "save",
                "available": True,
                "reference": {
                    "schema": "lf.workflow-artifact-ref.v1",
                    "sourceRunId": run_id,
                    "artifactId": "a" * 64,
                    "filename": f"{run_id}.png",
                },
            }
        ],
    )
    parent_id = "lf-sequence:named-fan-out-in"
    await sequence_runtime.create_sequence_execution(
        definition,
        {"source": "input.png"},
        owner_id="owner",
        parent_run_id=parent_id,
        output_node_resolver=lambda _workflow_id, _output_id: "save",
        workflow_resolver=_empty_block,
    )

    # Finish cleanup and the three directed views, then release all process-
    # local coordination. The final call must recover solely from the durable
    # plan and the four exact child rows; no earlier child may be resubmitted.
    for _stage_index in range(4):
        await sequence_runtime.advance_sequence_execution(
            parent_id,
            child_runner=run_child,
        )
    sequence_runtime._locks.pop(parent_id, None)
    assert [call["workflowId"] for call in calls] == [
        "identity_cleanup",
        "directed_view",
        "directed_view",
        "directed_view",
    ]
    for call in calls[1:]:
        assert call["inputs"]["reference"]["sourceRunId"] == "named-child-1"

    terminal = await sequence_runtime.drive_sequence_execution(
        parent_id,
        child_runner=run_child,
        poll_interval=0,
    )

    assert terminal["status"] == "succeeded"
    assert len(calls) == 5
    sheet_inputs = calls[-1]["inputs"]
    assert list(sheet_inputs) == [
        "front_image",
        "right_image",
        "back_image",
        "left_image",
    ]
    assert [
        sheet_inputs[input_id]["sourceRunId"]
        for input_id in sheet_inputs
    ] == [
        "named-child-1",
        "named-child-2",
        "named-child-3",
        "named-child-4",
    ]


async def test_malformed_persisted_named_source_fails_before_consumer_submission(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    definition = _sequence(
        _stage("cleanup", "identity_cleanup", _public("reference", "source")),
        _stage(
            "right",
            "directed_view",
            _artifact("reference", "image", "cleanup"),
        ),
    )
    calls: list[dict] = []

    async def run_child(payload, *, owner_id):
        calls.append(payload)
        run_id = f"authority-child-{len(calls)}"
        await _create_bound_child(payload, run_id, owner_id)
        await job_store.set_job_status(
            run_id,
            job_store.JobStatus.SUCCEEDED,
            result=_result(payload["workflowId"]),
        )
        return {"run_id": run_id}

    monkeypatch.setattr(
        sequence_runtime,
        "project_public_output_artifacts",
        lambda *_args: pytest.fail("malformed authority must fail before projection"),
    )
    parent_id = "lf-sequence:malformed-named-source"
    await sequence_runtime.create_sequence_execution(
        definition,
        {"source": "input.png"},
        owner_id="owner",
        parent_run_id=parent_id,
        output_node_resolver=lambda _workflow_id, _output_id: "save",
        workflow_resolver=_empty_block,
    )
    await sequence_runtime.advance_sequence_execution(
        parent_id,
        child_runner=run_child,
    )
    record = await sequence_store.get_state(parent_id)
    assert record is not None
    state = record.state
    state["stages"][1]["bindings"][0]["source_stage_id"] = "forged"
    await sequence_store.save_state(parent_id, state)

    terminal = await sequence_runtime.advance_sequence_execution(
        parent_id,
        child_runner=run_child,
    )

    assert terminal["status"] == "failed"
    assert terminal["error_detail"] == "sequence_artifact_source_invalid"
    assert len(calls) == 1


async def test_declared_final_outputs_filter_the_public_parent_result() -> None:
    from modules.workflow_runner.services.registry import (
        WorkflowCell,
        WorkflowSequenceLiteralBinding,
        WorkflowSequenceNode,
        WorkflowSequencePublicInputBinding,
        WorkflowSequenceStage,
    )

    definition = WorkflowSequenceNode(
        id="output_projection",
        value="Output projection",
        description="Only its assembly API is public.",
        category="Tests",
        inputs=(
            WorkflowCell(
                id="prompt",
                node_id="sequence",
                shape="textfield",
                props={"lfValue": "subject"},
            ),
        ),
        stages=(
            WorkflowSequenceStage(
                id="prepare",
                workflow_id="prepare_block",
                bindings=(WorkflowSequencePublicInputBinding("prompt", "prompt"),),
            ),
            WorkflowSequenceStage(
                id="finish",
                workflow_id="finish_block",
                bindings=(WorkflowSequenceLiteralBinding("mode", "quality"),),
            ),
        ),
        final_output_ids=("image",),
    )
    calls = 0

    async def run_child(payload, *, owner_id):
        nonlocal calls
        calls += 1
        run_id = f"projection-child-{calls}"
        await _create_bound_child(payload, run_id, owner_id)
        result = _result(payload["workflowId"])
        if calls == 2:
            result["body"]["payload"]["history"]["outputs"]["diagnostic"] = {
                "text": "private stage plumbing"
            }
            result["body"]["payload"]["preferred_output"] = "diagnostic"
        await job_store.set_job_status(
            run_id,
            job_store.JobStatus.SUCCEEDED,
            result=result,
        )
        return {"run_id": run_id}

    parent_id = "lf-sequence:output-projection"
    await sequence_runtime.create_sequence_execution(
        definition,
        {},
        parent_run_id=parent_id,
        output_node_resolver=lambda _workflow_id, _output_id: "save",
        workflow_resolver=_empty_block,
    )
    terminal = await sequence_runtime.drive_sequence_execution(
        parent_id,
        child_runner=run_child,
        poll_interval=0,
    )

    assert terminal["status"] == "succeeded"
    parent = await job_store.get_job(parent_id)
    final_child = await job_store.get_job("projection-child-2")
    assert parent is not None and final_child is not None
    assert set(parent.result["body"]["payload"]["history"]["outputs"]) == {"save"}
    assert parent.result["body"]["payload"]["preferred_output"] == "save"
    assert set(final_child.result["body"]["payload"]["history"]["outputs"]) == {
        "save",
        "diagnostic",
    }


async def test_missing_declared_final_output_fails_the_parent() -> None:
    from modules.workflow_runner.services.registry import (
        WorkflowSequenceLiteralBinding,
        WorkflowSequenceNode,
        WorkflowSequenceStage,
    )

    definition = WorkflowSequenceNode(
        id="missing_output",
        value="Missing output",
        description="Missing declared outputs fail closed.",
        category="Tests",
        inputs=(),
        stages=(
            WorkflowSequenceStage(
                id="prepare",
                workflow_id="prepare_block",
                bindings=(WorkflowSequenceLiteralBinding("mode", "prepare"),),
            ),
            WorkflowSequenceStage(
                id="finish",
                workflow_id="finish_block",
                bindings=(WorkflowSequenceLiteralBinding("mode", "quality"),),
            ),
        ),
        final_output_ids=("image",),
    )
    calls = 0

    async def run_child(payload, *, owner_id):
        nonlocal calls
        calls += 1
        run_id = f"missing-output-child-{calls}"
        await _create_bound_child(payload, run_id, owner_id)
        result = _result(payload["workflowId"])
        if calls == 2:
            result["body"]["payload"]["history"]["outputs"] = {
                "diagnostic": {"text": "not the declared image"}
            }
        await job_store.set_job_status(
            run_id,
            job_store.JobStatus.SUCCEEDED,
            result=result,
        )
        return {"run_id": run_id}

    parent_id = "lf-sequence:missing-final-output"
    await sequence_runtime.create_sequence_execution(
        definition,
        {},
        parent_run_id=parent_id,
        output_node_resolver=lambda _workflow_id, _output_id: "save",
        workflow_resolver=_empty_block,
    )
    terminal = await sequence_runtime.drive_sequence_execution(
        parent_id,
        child_runner=run_child,
        poll_interval=0,
    )

    assert terminal["status"] == "failed"
    assert terminal["error_detail"] == "sequence_output_missing"
    assert "did not produce declared output" in terminal["error"]
    parent = await job_store.get_job(parent_id)
    assert parent is not None and parent.status == job_store.JobStatus.FAILED
    assert parent.result is None


async def test_unbound_block_controls_receive_frozen_semantic_defaults() -> None:
    from modules.workflow_runner.services.registry import WorkflowCell

    definition = _sequence(
        _stage("quality", "quality_block", _public("reference", "source")),
        _stage("save", "save_block", _literal("prefix", "monument")),
    )
    blocks = {
        "quality_block": SimpleNamespace(
            inputs=(
                WorkflowCell(id="reference", node_id="load", shape="upload"),
                WorkflowCell(
                    id="steps",
                    node_id="sampler",
                    shape="select",
                    props={
                        "lfValue": "10",
                        "lfDataset": {
                            "nodes": [
                                {"id": "8", "value": "Fast", "workflowValue": 8},
                                {
                                    "id": "10",
                                    "value": "Baseline",
                                    "workflowValue": 10,
                                },
                            ]
                        },
                    },
                ),
                WorkflowCell(
                    id="cfg",
                    node_id="sampler",
                    shape="textfield",
                    props={"lfValue": "1"},
                ),
                WorkflowCell(
                    id="enabled",
                    node_id="switch",
                    shape="toggle",
                    props={"lfValue": False},
                ),
            )
        ),
        "save_block": SimpleNamespace(inputs=()),
    }
    calls: list[dict] = []

    async def run_child(payload, *, owner_id):
        calls.append(payload)
        run_id = f"defaults-child-{len(calls)}"
        await _create_bound_child(payload, run_id, owner_id)
        await job_store.set_job_status(
            run_id,
            job_store.JobStatus.SUCCEEDED,
            result=_result(payload["workflowId"]),
        )
        return {"run_id": run_id}

    parent_id = "lf-sequence:defaults"
    await sequence_runtime.create_sequence_execution(
        definition,
        {"source": "subject.png"},
        parent_run_id=parent_id,
        workflow_resolver=blocks.__getitem__,
    )
    await sequence_runtime.drive_sequence_execution(
        parent_id,
        child_runner=run_child,
        poll_interval=0,
    )

    assert calls[0]["inputs"] == {
        "reference": "subject.png",
        "steps": 10,
        "cfg": "1",
        "enabled": False,
    }
    persisted = await sequence_store.get_state(parent_id)
    assert persisted is not None
    assert persisted.state["stages"][0]["defaults"]["steps"] == 10


async def test_child_failure_stops_before_the_next_stage() -> None:
    definition = _sequence(
        _stage("first", "first_workflow", _public("prompt", "prompt")),
        _stage("never", "second_workflow", _literal("prompt", "no")),
    )
    calls: list[str] = []

    async def run_child(payload, *, owner_id):
        calls.append(payload["workflowId"])
        await _create_bound_child(payload, "failed-child", owner_id)
        await job_store.set_job_status(
            "failed-child",
            job_store.JobStatus.FAILED,
            error="model exploded",
        )
        return {"run_id": "failed-child"}

    parent_id = "lf-sequence:fail-fast"
    await sequence_runtime.create_sequence_execution(
        definition,
        {"prompt": "hello"},
        parent_run_id=parent_id,
        workflow_resolver=_empty_block,
    )
    terminal = await sequence_runtime.drive_sequence_execution(
        parent_id,
        child_runner=run_child,
        poll_interval=0,
    )

    assert terminal["status"] == "failed"
    assert terminal["current_stage"] == 0
    assert calls == ["first_workflow"]
    parent = await job_store.get_job(parent_id)
    assert parent is not None and parent.status == job_store.JobStatus.FAILED
    assert parent.error == "model exploded"


async def test_nonfinal_child_failure_preserves_diagnostics_without_partial_outputs() -> None:
    definition = _declared_sequence(
        _stage("first", "first_workflow", _public("prompt", "prompt")),
        _stage("never", "second_workflow", _literal("prompt", "no")),
    )
    partial_result = {
        "http_status": 500,
        "body": {
            "message": "model exploded",
            "status": "error",
            "payload": {
                "detail": "CUDA allocation failed after preview",
                "error": {"message": "execution_failed"},
                "preferred_output": "diagnostic",
                "history": {
                    "status": {"status_str": "error", "completed": True},
                    "outputs": {
                        # Deliberately reuse the final stage's public node id:
                        # node ids alone cannot grant an earlier stage authority.
                        "save": {"images": [{"filename": "partial.png"}]},
                        "diagnostic": {"text": ["private stage plumbing"]},
                    },
                },
            },
        },
    }

    async def run_child(payload, *, owner_id):
        await _create_bound_child(payload, "partial-failure-child", owner_id)
        await job_store.set_job_status(
            "partial-failure-child",
            job_store.JobStatus.FAILED,
            result=partial_result,
            error="model exploded",
        )
        return {"run_id": "partial-failure-child"}

    parent_id = "lf-sequence:partial-failure-projection"
    await sequence_runtime.create_sequence_execution(
        definition,
        {"prompt": "hello"},
        parent_run_id=parent_id,
        output_node_resolver=lambda _workflow_id, _output_id: "save",
        workflow_resolver=_empty_block,
    )
    terminal = await sequence_runtime.drive_sequence_execution(
        parent_id,
        child_runner=run_child,
        poll_interval=0,
    )

    assert terminal["status"] == "failed"
    parent = await job_store.get_job(parent_id)
    child = await job_store.get_job("partial-failure-child")
    assert parent is not None and child is not None
    assert parent.error == "model exploded"
    assert parent.result["http_status"] == 500
    assert parent.result["body"]["status"] == "error"
    payload = parent.result["body"]["payload"]
    assert payload["detail"] == "CUDA allocation failed after preview"
    assert payload["error"] == {"message": "execution_failed"}
    assert payload["history"]["status"] == {
        "status_str": "error",
        "completed": True,
    }
    assert payload["history"]["outputs"] == {}
    assert "preferred_output" not in payload
    assert child.result == partial_result


async def test_disappeared_active_child_fails_instead_of_stranding_parent() -> None:
    definition = _sequence(
        _stage("first", "first_workflow", _public("prompt", "prompt")),
        _stage("never", "second_workflow", _literal("prompt", "no")),
    )
    child_run_id = "disappearing-child"

    async def run_child(payload, *, owner_id):
        await _create_bound_child(payload, child_run_id, owner_id)
        await job_store.set_job_status(child_run_id, job_store.JobStatus.RUNNING)
        return {"run_id": child_run_id}

    parent_id = "lf-sequence:missing-child"
    await sequence_runtime.create_sequence_execution(
        definition,
        {"prompt": "hello"},
        parent_run_id=parent_id,
        workflow_resolver=_empty_block,
    )
    await sequence_runtime.advance_sequence_execution(
        parent_id,
        child_runner=run_child,
    )
    await job_store.remove_job(child_run_id)

    terminal = await sequence_runtime.advance_sequence_execution(parent_id)
    assert terminal["status"] == "failed"
    assert terminal["error_detail"] == "sequence_child_missing"
    assert "durable child job disappeared" in terminal["error"]
    parent = await job_store.get_job(parent_id)
    assert parent is not None and parent.status == job_store.JobStatus.FAILED


async def test_resumed_submitting_stage_fails_parent_when_artifact_disappeared(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    definition = _sequence(
        _stage("first", "first_workflow", _public("prompt", "prompt")),
        _stage("second", "second_workflow", _artifact("reference", "image")),
    )
    parent_id = "lf-sequence:missing-resumed-artifact"
    await sequence_runtime.create_sequence_execution(
        definition,
        {"prompt": "hello"},
        parent_run_id=parent_id,
        output_node_resolver=lambda _workflow_id, _output_id: "save",
        workflow_resolver=_empty_block,
    )
    first_submission_id = sequence_runtime.child_submission_id(
        parent_id, 0, "first"
    )
    first_payload = {
        "workflowId": "first_workflow",
        "inputs": {"prompt": "hello"},
        "submissionId": first_submission_id,
    }
    await _create_bound_child(
        first_payload,
        "finished-first",
        None,
    )
    await job_store.set_job_status(
        "finished-first",
        job_store.JobStatus.SUCCEEDED,
        result=_result("first"),
    )
    record = await sequence_store.get_state(parent_id)
    assert record is not None
    state = record.state
    state["stages"][0].update(
        {
            "status": "succeeded",
            "child_run_id": "finished-first",
            "child_submission_id": first_submission_id,
            "child_request_fingerprint": lifecycle._fingerprint_payload(
                first_payload
            ),
        }
    )
    state["current_stage"] = 1
    state["stages"][1].update(
        {
            "status": "submitting",
            "child_submission_id": sequence_runtime.child_submission_id(
                parent_id, 1, "second"
            ),
        }
    )
    await sequence_store.save_state(parent_id, state)
    monkeypatch.setattr(
        sequence_runtime, "project_public_output_artifacts", lambda *_args: []
    )

    terminal = await sequence_runtime.advance_sequence_execution(parent_id)
    assert terminal["status"] == "failed"
    assert "could not resolve its inputs" in terminal["error"]
    parent = await job_store.get_job(parent_id)
    assert parent is not None and parent.status == job_store.JobStatus.FAILED


async def test_idle_sequence_cancel_is_terminal_without_a_child() -> None:
    definition = _sequence(
        _stage("first", "first_workflow", _public("prompt", "prompt")),
        _stage("second", "second_workflow", _literal("prompt", "later")),
    )
    parent_id = "lf-sequence:idle-cancel"
    await sequence_runtime.create_sequence_execution(
        definition,
        {"prompt": "hello"},
        parent_run_id=parent_id,
        workflow_resolver=_empty_block,
    )
    assert await sequence_runtime.delete_sequence_execution_state(parent_id) is False

    terminal = await sequence_runtime.cancel_sequence_execution(parent_id)
    assert terminal["status"] == "cancelled"
    parent = await job_store.get_job(parent_id)
    assert parent is not None and parent.status == job_store.JobStatus.CANCELLED


async def test_resume_repairs_an_active_parent_left_pending() -> None:
    definition = _sequence(
        _stage("first", "first_workflow", _public("prompt", "prompt")),
        _stage("second", "second_workflow", _literal("prompt", "later")),
    )
    parent_id = "lf-sequence:pending-parent-repair"
    await sequence_runtime.create_sequence_execution(
        definition,
        {"prompt": "hello"},
        parent_run_id=parent_id,
        workflow_resolver=_empty_block,
    )
    record = await sequence_store.get_state(parent_id)
    assert record is not None
    private_state = record.state
    private_state["status"] = "pending"
    await sequence_store.save_state(parent_id, private_state)
    await job_store.set_job_status(parent_id, job_store.JobStatus.PENDING)

    async def inert_child(_payload, *, owner_id):
        raise AssertionError(f"unexpected child submission for {owner_id}")

    resumed = await sequence_runtime.resume_sequence_executions(
        child_runner=inert_child,
        poll_interval=60,
    )
    assert resumed == [parent_id]
    repaired = await job_store.get_job(parent_id)
    assert repaired is not None and repaired.status == job_store.JobStatus.RUNNING
    repaired_state = await sequence_store.get_state(parent_id)
    assert repaired_state is not None and repaired_state.status == "running"


async def test_cancel_targets_only_the_exact_active_child_submission() -> None:
    definition = _sequence(
        _stage("render", "slow_workflow", _public("prompt", "prompt")),
        _stage("never", "later_workflow", _literal("prompt", "never")),
    )
    child_run_id = "running-child"

    async def run_child(payload, *, owner_id):
        await _create_bound_child(payload, child_run_id, owner_id)
        await job_store.set_job_status(child_run_id, job_store.JobStatus.RUNNING)
        return {"run_id": child_run_id}

    parent_id = "lf-sequence:cancel"
    await sequence_runtime.create_sequence_execution(
        definition,
        {"prompt": "wait"},
        parent_run_id=parent_id,
        workflow_resolver=_empty_block,
    )
    active = await sequence_runtime.advance_sequence_execution(
        parent_id,
        child_runner=run_child,
    )
    expected_submission = active["stages"][0]["child_submission_id"]
    cancelled: list[str] = []

    async def cancel_child(submission_id: str):
        cancelled.append(submission_id)
        await job_store.set_job_status(
            child_run_id,
            job_store.JobStatus.CANCELLED,
            error="cancelled",
        )
        return {"status": "cancelled", "submission_id": submission_id}

    requested = await sequence_runtime.cancel_sequence_execution(
        parent_id,
        child_canceller=cancel_child,
    )
    assert requested["cancel_requested"] is True
    assert cancelled == [expected_submission]

    terminal = await sequence_runtime.advance_sequence_execution(
        parent_id,
        child_runner=run_child,
        child_canceller=cancel_child,
    )
    assert terminal["status"] == "cancelled"
    assert cancelled == [expected_submission]
    parent = await job_store.get_job(parent_id)
    assert parent is not None and parent.status == job_store.JobStatus.CANCELLED


async def test_final_child_cancel_projects_only_declared_outputs() -> None:
    definition = _declared_sequence(
        _stage("prepare", "prepare_workflow", _literal("prompt", "prepare")),
        _stage("finish", "finish_workflow", _literal("prompt", "finish")),
    )
    final_child_id = "partial-cancel-child"
    calls = 0

    async def run_child(payload, *, owner_id):
        nonlocal calls
        calls += 1
        run_id = "cancel-projection-child-1" if calls == 1 else final_child_id
        await _create_bound_child(payload, run_id, owner_id)
        if calls == 1:
            await job_store.set_job_status(
                run_id,
                job_store.JobStatus.SUCCEEDED,
                result=_result("prepare"),
            )
        else:
            assert run_id == final_child_id
            await job_store.set_job_status(run_id, job_store.JobStatus.RUNNING)
        return {"run_id": run_id}

    cancelled_result = {
        "http_status": 200,
        "body": {
            "message": "cancelled",
            "status": "ready",
            "payload": {
                "detail": "cancelled",
                "preferred_output": "diagnostic",
                "history": {
                    "status": {"status_str": "error", "completed": True},
                    "outputs": {
                        "save": {"images": [{"filename": "kept.png"}]},
                        "diagnostic": {"text": ["private stage plumbing"]},
                    },
                },
            },
        },
    }

    async def cancel_child(submission_id: str):
        await job_store.set_job_status(
            final_child_id,
            job_store.JobStatus.CANCELLED,
            result=cancelled_result,
            error="cancelled",
        )
        return {"status": "cancelled", "submission_id": submission_id}

    parent_id = "lf-sequence:cancel-output-projection"
    await sequence_runtime.create_sequence_execution(
        definition,
        {},
        parent_run_id=parent_id,
        output_node_resolver=lambda _workflow_id, _output_id: "save",
        workflow_resolver=_empty_block,
    )
    await sequence_runtime.advance_sequence_execution(
        parent_id,
        child_runner=run_child,
    )
    active = await sequence_runtime.advance_sequence_execution(
        parent_id,
        child_runner=run_child,
    )
    assert active["current_stage"] == 1
    assert active["stages"][1]["child_run_id"] == final_child_id

    await sequence_runtime.cancel_sequence_execution(
        parent_id,
        child_canceller=cancel_child,
    )
    terminal = await sequence_runtime.advance_sequence_execution(
        parent_id,
        child_runner=run_child,
        child_canceller=cancel_child,
    )

    assert terminal["status"] == "cancelled"
    parent = await job_store.get_job(parent_id)
    child = await job_store.get_job(final_child_id)
    assert parent is not None and child is not None
    assert parent.error == "cancelled"
    payload = parent.result["body"]["payload"]
    assert payload["detail"] == "cancelled"
    assert payload["history"]["status"] == {
        "status_str": "error",
        "completed": True,
    }
    assert payload["history"]["outputs"] == {
        "save": {"images": [{"filename": "kept.png"}]}
    }
    assert payload["preferred_output"] == "save"
    assert child.result == cancelled_result


async def test_resumed_cancel_dispatch_failure_keeps_supervision_retryable() -> None:
    definition = _sequence(
        _stage("render", "slow_workflow", _public("prompt", "prompt")),
        _stage("never", "later_workflow", _literal("prompt", "never")),
    )
    child_run_id = "cancel-retry-child"

    async def run_child(payload, *, owner_id):
        await _create_bound_child(payload, child_run_id, owner_id)
        await job_store.set_job_status(child_run_id, job_store.JobStatus.RUNNING)
        return {"run_id": child_run_id}

    parent_id = "lf-sequence:cancel-retry"
    await sequence_runtime.create_sequence_execution(
        definition,
        {"prompt": "wait"},
        parent_run_id=parent_id,
        workflow_resolver=_empty_block,
    )
    active = await sequence_runtime.advance_sequence_execution(
        parent_id,
        child_runner=run_child,
    )
    record = await sequence_store.get_state(parent_id)
    assert record is not None
    state = record.state
    state["cancel_requested"] = True
    state["cancel_dispatched"] = False
    await sequence_store.save_state(parent_id, state)
    attempts = 0

    async def flaky_cancel(_submission_id: str):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise ConnectionError("temporary transport loss")
        return {"status": "running", "cancel_requested": True}

    retryable = await sequence_runtime.advance_sequence_execution(
        parent_id,
        child_runner=run_child,
        child_canceller=flaky_cancel,
    )
    assert retryable["status"] == active["status"]
    assert retryable["cancel_requested"] is True
    assert retryable["cancel_dispatched"] is False
    assert "temporary transport loss" in retryable["stages"][0]["error"]

    dispatched = await sequence_runtime.advance_sequence_execution(
        parent_id,
        child_runner=run_child,
        child_canceller=flaky_cancel,
    )
    assert attempts == 2
    assert dispatched["cancel_dispatched"] is True
    assert dispatched["stages"][0]["error"] is None


async def test_final_stage_success_wins_a_late_cancel_race() -> None:
    definition = _sequence(
        _stage("prepare", "prepare_workflow", _public("prompt", "prompt")),
        _stage("final", "final_workflow", _literal("prompt", "finish")),
    )
    calls = 0

    async def run_child(payload, *, owner_id):
        nonlocal calls
        calls += 1
        run_id = f"race-child-{calls}"
        await _create_bound_child(payload, run_id, owner_id)
        await job_store.set_job_status(
            run_id,
            (
                job_store.JobStatus.SUCCEEDED
                if calls == 1
                else job_store.JobStatus.RUNNING
            ),
            result=_result(payload["workflowId"]) if calls == 1 else None,
        )
        return {"run_id": run_id}

    parent_id = "lf-sequence:success-cancel-race"
    await sequence_runtime.create_sequence_execution(
        definition,
        {"prompt": "hello"},
        parent_run_id=parent_id,
        workflow_resolver=_empty_block,
    )
    await sequence_runtime.advance_sequence_execution(
        parent_id, child_runner=run_child
    )
    await sequence_runtime.advance_sequence_execution(
        parent_id, child_runner=run_child
    )
    final_result = _result("final-success")

    async def cancel_after_success(_submission_id: str):
        await job_store.set_job_status(
            "race-child-2",
            job_store.JobStatus.SUCCEEDED,
            result=final_result,
        )
        return {"status": "succeeded", "cancel_requested": False}

    raced = await sequence_runtime.cancel_sequence_execution(
        parent_id,
        child_canceller=cancel_after_success,
    )
    assert raced["cancel_requested"] is False
    terminal = await sequence_runtime.advance_sequence_execution(
        parent_id,
        child_runner=run_child,
        child_canceller=cancel_after_success,
    )
    assert terminal["status"] == "succeeded"
    parent = await job_store.get_job(parent_id)
    assert parent is not None and parent.result == final_result


async def test_restart_window_cancel_recovers_durable_child_or_fails_closed() -> None:
    definition = _sequence(
        _stage("render", "slow_workflow", _public("prompt", "prompt")),
        _stage("never", "later_workflow", _literal("prompt", "never")),
    )
    parent_id = "lf-sequence:cancel-recovery"
    created = await sequence_runtime.create_sequence_execution(
        definition,
        {"prompt": "wait"},
        parent_run_id=parent_id,
        workflow_resolver=_empty_block,
    )
    submission_id = sequence_runtime.child_submission_id(parent_id, 0, "render")
    record = await sequence_store.get_state(parent_id)
    assert record is not None
    state = record.state
    state["stages"][0]["status"] = "submitting"
    state["stages"][0]["child_submission_id"] = submission_id
    recovery_payload = {
        "workflowId": "slow_workflow",
        "inputs": {"prompt": "wait"},
        "submissionId": submission_id,
    }
    state["stages"][0]["child_request_fingerprint"] = (
        lifecycle._fingerprint_payload(recovery_payload)
    )
    await sequence_store.save_state(parent_id, state)

    with pytest.raises(sequence_runtime.SequenceExecutionError) as exc_info:
        await sequence_runtime.cancel_sequence_execution(parent_id)
    assert exc_info.value.detail == "sequence_child_not_bound"
    unresolved = await sequence_runtime.get_sequence_execution(parent_id)
    assert unresolved is not None and unresolved["status"] == created["status"]
    assert unresolved["cancel_requested"] is False

    await job_store.create_job(
        "recovered-child",
        "slow_workflow",
        owner_id="foreign-owner",
        submission_id=submission_id,
        request_fingerprint=lifecycle._fingerprint_payload(recovery_payload),
        comfy_url="http://comfy:8188",
    )
    await job_store.set_job_status("recovered-child", job_store.JobStatus.RUNNING)
    with pytest.raises(sequence_runtime.SequenceExecutionError) as foreign_exc:
        await sequence_runtime.cancel_sequence_execution(parent_id)
    assert foreign_exc.value.detail == "sequence_child_authority_mismatch"
    await job_store.remove_job("recovered-child")
    await job_store.create_job(
        "recovered-child",
        "slow_workflow",
        submission_id=submission_id,
        request_fingerprint="a" * 64,
        comfy_url="http://comfy:8188",
    )
    await job_store.set_job_status("recovered-child", job_store.JobStatus.RUNNING)
    with pytest.raises(sequence_runtime.SequenceExecutionError) as fingerprint_exc:
        await sequence_runtime.cancel_sequence_execution(parent_id)
    assert fingerprint_exc.value.detail == "sequence_child_authority_mismatch"
    await job_store.remove_job("recovered-child")
    await job_store.create_job(
        "recovered-child",
        "slow_workflow",
        submission_id=submission_id,
        request_fingerprint=lifecycle._fingerprint_payload(recovery_payload),
        comfy_url="http://comfy:8188",
    )
    await job_store.set_job_status("recovered-child", job_store.JobStatus.RUNNING)
    cancelled: list[str] = []

    async def cancel_child(exact_submission_id: str):
        cancelled.append(exact_submission_id)
        return {"status": "running", "cancel_requested": True}

    recovered = await sequence_runtime.cancel_sequence_execution(
        parent_id,
        child_canceller=cancel_child,
    )
    assert recovered["stages"][0]["child_run_id"] == "recovered-child"
    assert recovered["cancel_requested"] is True
    assert cancelled == [submission_id]


async def test_default_runner_replays_a_persisted_submitting_stage(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(sys.modules, "execution", ModuleType("execution"))
    from modules.workflow_runner.services import run_service

    definition = _sequence(
        _stage("first", "first_workflow", _public("prompt", "prompt")),
        _stage("second", "second_workflow", _literal("prompt", "later")),
    )
    parent_id = "lf-sequence:default-runner-replay"
    await sequence_runtime.create_sequence_execution(
        definition,
        {"prompt": "hello"},
        parent_run_id=parent_id,
        workflow_resolver=_empty_block,
    )
    submission_id = sequence_runtime.child_submission_id(parent_id, 0, "first")
    child_payload = {
        "workflowId": "first_workflow",
        "inputs": {"prompt": "hello"},
        "submissionId": submission_id,
    }
    await _create_bound_child(child_payload, "already-admitted-child", None)
    await job_store.set_job_status(
        "already-admitted-child",
        job_store.JobStatus.SUCCEEDED,
        result=_result("first"),
    )
    record = await sequence_store.get_state(parent_id)
    assert record is not None
    state = record.state
    state["stages"][0].update(
        {
            "status": "submitting",
            "child_submission_id": submission_id,
            "child_run_id": None,
        }
    )
    await sequence_store.save_state(parent_id, state)
    replays: list[dict] = []

    async def replay_run_workflow(
        payload,
        owner_id=None,
        is_api_call=False,
        *,
        _sequence_child=False,
    ):
        replays.append(payload)
        assert owner_id is None and is_api_call is False
        assert _sequence_child is True
        existing = await job_store.get_job_by_submission_id(payload["submissionId"])
        assert existing is not None
        return {"run_id": existing.id, "replayed": True}

    monkeypatch.setattr(run_service, "run_workflow", replay_run_workflow)
    advanced = await sequence_runtime.advance_sequence_execution(parent_id)

    assert advanced["current_stage"] == 1
    assert advanced["stages"][0]["child_run_id"] == "already-admitted-child"
    assert replays == [child_payload]
    assert (await job_store.get_job_by_submission_id(submission_id)).id == (
        "already-admitted-child"
    )


async def test_sqlite_state_resumes_after_connection_restart(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from modules.workflow_runner.services import job_store_sqlite, lifecycle

    db_path = tmp_path / "runner.sqlite3"
    await job_store_sqlite.close()
    monkeypatch.setattr(job_store, "_USE_PERSISTENCE", True)
    monkeypatch.setattr(
        job_store,
        "_settings",
        SimpleNamespace(WORKFLOW_RUNNER_DB_PATH=str(db_path)),
    )
    job_store._adapter = None  # type: ignore[attr-defined]

    definition = _sequence(
        _stage("render", "restartable", _public("prompt", "prompt")),
        _stage("finish", "restartable_finish", _literal("prompt", "finish")),
    )
    child_run_id = "durable-child"

    async def run_child(payload, *, owner_id):
        await _create_bound_child(payload, child_run_id, owner_id)
        await job_store.set_job_status(child_run_id, job_store.JobStatus.RUNNING)
        return {"run_id": child_run_id}

    parent_id = "lf-sequence:restart"
    await sequence_runtime.create_sequence_execution(
        definition,
        {"prompt": "resume me"},
        owner_id="owner",
        parent_run_id=parent_id,
        workflow_resolver=_empty_block,
    )
    await sequence_runtime.advance_sequence_execution(
        parent_id,
        child_runner=run_child,
    )
    first_result = _result("first-stage-after-restart")
    await job_store.set_job_status(
        child_run_id,
        job_store.JobStatus.SUCCEEDED,
        result=first_result,
    )

    # Simulate process-local state loss while preserving the one configured DB.
    await job_store_sqlite.close()
    job_store._adapter = None  # type: ignore[attr-defined]
    await sequence_store.reset_for_tests()
    await lifecycle.reset_for_tests()

    final_result = _result("final-stage-after-restart")

    async def resume_child(payload, *, owner_id):
        assert payload["workflowId"] == "restartable_finish"
        await _create_bound_child(payload, "durable-final-child", owner_id)
        await job_store.set_job_status(
            "durable-final-child",
            job_store.JobStatus.SUCCEEDED,
            result=final_result,
        )
        return {"run_id": "durable-final-child"}

    resumed = await sequence_runtime.resume_sequence_executions(
        child_runner=resume_child,
        poll_interval=0,
    )
    assert resumed == [parent_id]
    task = sequence_runtime._supervisors[parent_id]  # type: ignore[attr-defined]
    terminal = await task
    assert terminal["status"] == "succeeded"
    parent = await job_store.get_job(parent_id)
    assert parent is not None and parent.result == final_result

    await job_store_sqlite.close()


async def test_startup_terminalizes_parent_missing_private_sequence_state() -> None:
    parent_id = "lf-sequence:missing-private-state"
    await job_store.create_job(
        parent_id,
        "portrait_monument",
        submission_id="test:orphaned-sequence-parent",
        request_fingerprint="a" * 64,
        comfy_url="sequence://runner",
    )

    resumed = await sequence_runtime.resume_sequence_executions()

    assert resumed == []
    parent = await job_store.get_job(parent_id)
    assert parent is not None
    assert parent.status == job_store.JobStatus.FAILED
    assert parent.error == "sequence_state_missing"
    assert parent.result["body"]["payload"]["error"] == {
        "message": "sequence_state_missing"
    }


async def test_orphan_recovery_failure_does_not_block_independent_parent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first_id = "lf-sequence:broken-orphan"
    second_id = "lf-sequence:recoverable-orphan"
    for index, parent_id in enumerate((first_id, second_id)):
        await job_store.create_job(
            parent_id,
            "portrait_monument",
            submission_id=f"test:orphan:{index}",
            request_fingerprint=str(index) * 64,
            comfy_url="sequence://runner",
        )
    original = job_store.set_job_status

    async def fail_first(job_id, *args, **kwargs):
        if job_id == first_id:
            raise RuntimeError("one damaged parent")
        return await original(job_id, *args, **kwargs)

    monkeypatch.setattr(job_store, "set_job_status", fail_first)

    assert await sequence_runtime.resume_sequence_executions() == []
    assert (await job_store.get_job(first_id)).status == job_store.JobStatus.PENDING
    assert (await job_store.get_job(second_id)).status == job_store.JobStatus.FAILED


async def test_unexpected_supervisor_error_terminalizes_parent_and_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    definition = _sequence(
        _stage("first", "identity_clean"),
        _stage("second", "character_restage"),
    )
    parent_id = "lf-sequence:supervisor-failure"
    await sequence_runtime.create_sequence_execution(
        definition,
        {},
        parent_run_id=parent_id,
        workflow_resolver=_empty_block,
    )

    async def crash(*_args, **_kwargs):
        raise RuntimeError("supervisor exploded")

    monkeypatch.setattr(sequence_runtime, "drive_sequence_execution", crash)
    terminal = await sequence_runtime.schedule_sequence_execution(parent_id)

    assert terminal["status"] == "failed"
    assert terminal["error_detail"] == "sequence_supervisor_failed"
    assert (await sequence_store.get_state(parent_id)).status == "failed"
    parent = await job_store.get_job(parent_id)
    assert parent is not None
    assert parent.status == job_store.JobStatus.FAILED
    assert parent.error == "supervisor exploded"


async def test_supervisor_failure_best_effort_cancels_exact_active_child(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    definition = _sequence(
        _stage("first", "identity_clean"),
        _stage("second", "character_restage"),
    )
    parent_id = "lf-sequence:supervisor-active-child"
    await sequence_runtime.create_sequence_execution(
        definition,
        {},
        owner_id="owner",
        parent_run_id=parent_id,
        workflow_resolver=_empty_block,
    )
    record = await sequence_store.get_state(parent_id)
    assert record is not None
    state = record.state
    stage = state["stages"][0]
    submission_id = sequence_runtime.child_submission_id(parent_id, 0, stage["id"])
    payload = {
        "workflowId": stage["workflow_id"],
        "inputs": {},
        "submissionId": submission_id,
    }
    stage["child_submission_id"] = submission_id
    stage["child_request_fingerprint"] = lifecycle._fingerprint_payload(payload)
    stage["child_run_id"] = "active-child"
    stage["status"] = "running"
    state["status"] = "running"
    await sequence_store.save_state(parent_id, state)
    await _create_bound_child(payload, "active-child", "owner")
    await job_store.set_job_status("active-child", job_store.JobStatus.RUNNING)

    async def crash(*_args, **_kwargs):
        raise RuntimeError("supervisor exploded")

    cancelled: list[str] = []

    async def cancel_exact(child_submission_id: str):
        cancelled.append(child_submission_id)
        return {"status": "running", "cancel_requested": True}

    monkeypatch.setattr(sequence_runtime, "drive_sequence_execution", crash)
    terminal = await sequence_runtime.schedule_sequence_execution(
        parent_id,
        child_canceller=cancel_exact,
    )

    assert terminal["status"] == "failed"
    assert cancelled == [submission_id]
    parent = await job_store.get_job(parent_id)
    assert parent is not None
    assert parent.status == job_store.JobStatus.FAILED


async def test_restart_never_resumes_private_state_after_public_terminal_truth() -> None:
    definition = _sequence(
        _stage("first", "identity_clean"),
        _stage("second", "character_restage"),
    )
    parent_id = "lf-sequence:public-failure-won"
    await sequence_runtime.create_sequence_execution(
        definition,
        {},
        parent_run_id=parent_id,
        workflow_resolver=_empty_block,
    )
    await job_store.set_job_status(
        parent_id,
        job_store.JobStatus.FAILED,
        error="sequence_start_failed",
    )
    runner = pytest.fail

    resumed = await sequence_runtime.resume_sequence_executions(
        child_runner=runner,
        poll_interval=0,
    )

    assert resumed == []
    state = await sequence_store.get_state(parent_id)
    assert state is not None
    assert state.status == "failed"
    assert state.state["error"] == "sequence_start_failed"
    assert state.state["error_detail"] == "sequence_parent_terminal_recovery"


async def test_supervisor_failure_never_overwrites_public_terminal_truth() -> None:
    definition = _sequence(
        _stage("first", "identity_clean"),
        _stage("second", "character_restage"),
    )
    parent_id = "lf-sequence:public-success-won"
    await sequence_runtime.create_sequence_execution(
        definition,
        {},
        parent_run_id=parent_id,
        workflow_resolver=_empty_block,
    )
    public_result = _result("already-published")
    await job_store.set_job_status(
        parent_id,
        job_store.JobStatus.SUCCEEDED,
        result=public_result,
    )

    terminal = await sequence_runtime.fail_sequence_execution(
        parent_id,
        error="late private commit failed",
    )

    assert terminal["status"] == "succeeded"
    parent = await job_store.get_job(parent_id)
    assert parent is not None
    assert parent.status == job_store.JobStatus.SUCCEEDED
    assert parent.result == public_result


async def test_parent_cleanup_preserves_parent_and_state_while_exact_child_is_active() -> None:
    definition = _sequence(
        _stage("first", "identity_clean"),
        _stage("second", "character_restage"),
    )
    parent_id = "lf-sequence:cleanup-active-child"
    await sequence_runtime.create_sequence_execution(
        definition,
        {},
        owner_id="owner",
        parent_run_id=parent_id,
        workflow_resolver=_empty_block,
    )
    record = await sequence_store.get_state(parent_id)
    assert record is not None
    state = record.state
    child_specs = (
        (0, "earlier-terminal-child", job_store.JobStatus.SUCCEEDED),
        (1, "later-active-child", job_store.JobStatus.RUNNING),
    )
    child_payloads = []
    for stage_index, child_run_id, child_status in child_specs:
        stage = state["stages"][stage_index]
        submission_id = sequence_runtime.child_submission_id(
            parent_id,
            stage_index,
            stage["id"],
        )
        payload = {
            "workflowId": stage["workflow_id"],
            "inputs": {},
            "submissionId": submission_id,
        }
        stage["child_submission_id"] = submission_id
        stage["child_request_fingerprint"] = lifecycle._fingerprint_payload(payload)
        stage["child_run_id"] = child_run_id
        stage["status"] = child_status.value
        child_payloads.append((payload, child_run_id, child_status))
    state["status"] = "failed"
    await sequence_store.save_state(parent_id, state)
    for payload, child_run_id, child_status in child_payloads:
        await _create_bound_child(payload, child_run_id, "owner")
        await job_store.set_job_status(child_run_id, child_status)
    parent = await job_store.set_job_status(parent_id, job_store.JobStatus.FAILED)
    assert parent is not None

    removed = await sequence_runtime.hard_delete_sequence_parent_if_unchanged(
        parent_id,
        owner_id=parent.owner_id,
        status="failed",
        seq=parent.seq,
        updated_at=parent.updated_at,
    )

    assert removed is False
    assert await job_store.get_job(parent_id) is not None
    assert await job_store.get_job("earlier-terminal-child") is not None
    assert await job_store.get_job("later-active-child") is not None
    assert await sequence_store.get_state(parent_id) is not None


async def test_parent_cleanup_validates_later_child_before_deleting_earlier_child() -> None:
    definition = _sequence(
        _stage("first", "identity_clean"),
        _stage("second", "character_restage"),
    )
    parent_id = "lf-sequence:cleanup-later-mismatch"
    await sequence_runtime.create_sequence_execution(
        definition,
        {},
        owner_id="owner",
        parent_run_id=parent_id,
        workflow_resolver=_empty_block,
    )
    record = await sequence_store.get_state(parent_id)
    assert record is not None
    state = record.state
    child_ids = ("earlier-exact-child", "later-mismatched-child")
    child_payloads = []
    for stage_index, child_run_id in enumerate(child_ids):
        stage = state["stages"][stage_index]
        submission_id = sequence_runtime.child_submission_id(
            parent_id,
            stage_index,
            stage["id"],
        )
        payload = {
            "workflowId": stage["workflow_id"],
            "inputs": {},
            "submissionId": submission_id,
        }
        stage["child_submission_id"] = submission_id
        stage["child_request_fingerprint"] = lifecycle._fingerprint_payload(payload)
        stage["child_run_id"] = child_run_id
        stage["status"] = "succeeded"
        child_payloads.append((payload, child_run_id))
    state["status"] = "failed"
    await sequence_store.save_state(parent_id, state)
    for payload, child_run_id in child_payloads:
        await _create_bound_child(payload, child_run_id, "owner")
        await job_store.set_job_status(child_run_id, job_store.JobStatus.SUCCEEDED)
    job_store._jobs["later-mismatched-child"].request_fingerprint = "f" * 64
    parent = await job_store.set_job_status(parent_id, job_store.JobStatus.FAILED)
    assert parent is not None

    removed = await sequence_runtime.hard_delete_sequence_parent_if_unchanged(
        parent_id,
        owner_id=parent.owner_id,
        status="failed",
        seq=parent.seq,
        updated_at=parent.updated_at,
    )

    assert removed is False
    assert await job_store.get_job(parent_id) is not None
    assert await job_store.get_job("earlier-exact-child") is not None
    assert await job_store.get_job("later-mismatched-child") is not None
    assert await sequence_store.get_state(parent_id) is not None


async def test_parent_cleanup_preserves_parent_when_private_state_delete_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    definition = _sequence(
        _stage("first", "identity_clean"),
        _stage("second", "character_restage"),
    )
    parent_id = "lf-sequence:cleanup-state-failure"
    await sequence_runtime.create_sequence_execution(
        definition,
        {},
        owner_id="owner",
        parent_run_id=parent_id,
        workflow_resolver=_empty_block,
    )
    record = await sequence_store.get_state(parent_id)
    assert record is not None
    state = record.state
    state["status"] = "failed"
    await sequence_store.save_state(parent_id, state)
    parent = await job_store.set_job_status(parent_id, job_store.JobStatus.FAILED)
    assert parent is not None
    delete_state = AsyncMock(return_value=False)
    monkeypatch.setattr(sequence_store, "delete_state", delete_state)

    removed = await sequence_runtime.hard_delete_sequence_parent_if_unchanged(
        parent_id,
        owner_id=parent.owner_id,
        status="failed",
        seq=parent.seq,
        updated_at=parent.updated_at,
    )

    assert removed is False
    assert await job_store.get_job(parent_id) is not None
    assert await sequence_store.get_state(parent_id) is not None
    delete_state.assert_awaited_once_with(parent_id)


async def test_parent_cleanup_restores_state_and_retries_after_parent_cas_race(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    definition = _sequence(
        _stage("first", "identity_clean"),
        _stage("second", "character_restage"),
    )
    parent_id = "lf-sequence:cleanup-cas-race"
    await sequence_runtime.create_sequence_execution(
        definition,
        {},
        owner_id="owner",
        parent_run_id=parent_id,
        workflow_resolver=_empty_block,
    )
    record = await sequence_store.get_state(parent_id)
    assert record is not None
    state = record.state
    state["status"] = "failed"
    await sequence_store.save_state(parent_id, state)
    parent = await job_store.set_job_status(parent_id, job_store.JobStatus.FAILED)
    assert parent is not None
    original_delete = job_store.hard_delete_job_if_unchanged

    async def lose_parent_cas(*_args, **_kwargs) -> bool:
        await job_store.set_job_status(
            parent_id,
            job_store.JobStatus.FAILED,
            error="changed during cleanup",
        )
        return False

    monkeypatch.setattr(
        job_store,
        "hard_delete_job_if_unchanged",
        lose_parent_cas,
    )

    removed = await sequence_runtime.hard_delete_sequence_parent_if_unchanged(
        parent_id,
        owner_id=parent.owner_id,
        status="failed",
        seq=parent.seq,
        updated_at=parent.updated_at,
    )

    assert removed is False
    assert await job_store.get_job(parent_id) is not None
    assert await sequence_store.get_state(parent_id) is not None

    monkeypatch.setattr(
        job_store,
        "hard_delete_job_if_unchanged",
        original_delete,
    )
    changed_parent = await job_store.get_job(parent_id)
    assert changed_parent is not None
    assert await sequence_runtime.hard_delete_sequence_parent_if_unchanged(
        parent_id,
        owner_id=changed_parent.owner_id,
        status="failed",
        seq=changed_parent.seq,
        updated_at=changed_parent.updated_at,
    )
    assert await job_store.get_job(parent_id) is None
    assert await sequence_store.get_state(parent_id) is None


async def test_parent_cleanup_child_cas_race_keeps_parent_and_retries_remaining_rows(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    definition = _sequence(
        _stage("first", "identity_clean"),
        _stage("second", "character_restage"),
    )
    parent_id = "lf-sequence:cleanup-cascade"
    await sequence_runtime.create_sequence_execution(
        definition,
        {},
        owner_id="owner",
        parent_run_id=parent_id,
        workflow_resolver=_empty_block,
    )
    record = await sequence_store.get_state(parent_id)
    assert record is not None
    state = record.state
    child_ids = []
    for stage_index, stage in enumerate(state["stages"]):
        submission_id = sequence_runtime.child_submission_id(
            parent_id,
            stage_index,
            stage["id"],
        )
        payload = {
            "workflowId": stage["workflow_id"],
            "inputs": {},
            "submissionId": submission_id,
        }
        child_run_id = f"terminal-child-{stage_index}"
        child_ids.append(child_run_id)
        stage["child_submission_id"] = submission_id
        stage["child_request_fingerprint"] = lifecycle._fingerprint_payload(payload)
        stage["child_run_id"] = child_run_id
        stage["status"] = "succeeded"
        await _create_bound_child(payload, child_run_id, "owner")
        await job_store.set_job_status(
            child_run_id,
            job_store.JobStatus.SUCCEEDED,
            result=_result(f"child-{stage_index}"),
        )
    state["status"] = "failed"
    state["error"] = "later stage failed"
    await sequence_store.save_state(parent_id, state)
    parent = await job_store.set_job_status(parent_id, job_store.JobStatus.FAILED)
    assert parent is not None
    original_delete = job_store.hard_delete_job_if_unchanged

    async def lose_later_child_cas(job_id: str, **snapshot) -> bool:
        if job_id == "terminal-child-1":
            return False
        return await original_delete(job_id, **snapshot)

    monkeypatch.setattr(
        job_store,
        "hard_delete_job_if_unchanged",
        lose_later_child_cas,
    )

    assert not await sequence_runtime.hard_delete_sequence_parent_if_unchanged(
        parent_id,
        owner_id=parent.owner_id,
        status="failed",
        seq=parent.seq,
        updated_at=parent.updated_at,
    )
    assert await job_store.get_job(parent_id) is not None
    assert await sequence_store.get_state(parent_id) is not None
    assert await job_store.get_job("terminal-child-0") is None
    assert await job_store.get_job("terminal-child-1") is not None

    monkeypatch.setattr(
        job_store,
        "hard_delete_job_if_unchanged",
        original_delete,
    )
    assert await sequence_runtime.hard_delete_sequence_parent_if_unchanged(
        parent_id,
        owner_id=parent.owner_id,
        status="failed",
        seq=parent.seq,
        updated_at=parent.updated_at,
    )
    assert await job_store.get_job(parent_id) is None
    assert await sequence_store.get_state(parent_id) is None
    for child_id in child_ids:
        assert await job_store.get_job(child_id) is None


def test_history_filter_helpers_distinguish_parent_child_and_ordinary_jobs() -> None:
    parent = SimpleNamespace(id="lf-sequence:parent", submission_id="public-sequence")
    child = SimpleNamespace(
        id="prompt-id",
        submission_id="lfseq:0123456789abcdef0123456789abcdef:00",
    )
    ordinary = SimpleNamespace(id="prompt-id", submission_id="ordinary")
    spoof = SimpleNamespace(id="prompt-id", submission_id="lfseq:not-a-child")

    assert sequence_runtime.is_sequence_parent_job(parent)
    assert sequence_runtime.is_sequence_parent_job(
        {"run_id": "lf-sequence:serialized-parent"}
    )
    assert not sequence_runtime.is_sequence_child_job(parent)
    assert sequence_runtime.is_sequence_child_job(child)
    assert not sequence_runtime.is_sequence_parent_job(child)
    assert not sequence_runtime.is_sequence_child_job(ordinary)
    assert not sequence_runtime.is_sequence_child_job(spoof)
