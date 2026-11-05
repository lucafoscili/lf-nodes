"""Input-expanded plans retain ordinary sequence validation and recovery."""

from dataclasses import replace
from pathlib import Path

import pytest
import pytest_asyncio

from modules.workflow_runner.services import job_store, lifecycle, sequence_runtime, sequence_store
from modules.workflow_runner.services.registry import (
    WorkflowCell, WorkflowNode, WorkflowRegistry, WorkflowSequenceLiteralBinding,
    WorkflowSequenceNode, WorkflowSequenceStage, WorkflowSequenceTextBinding,
)


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture(autouse=True)
async def clear_sequences():
    await sequence_runtime.stop_sequence_supervisors()
    await sequence_store.reset_for_tests()
    yield
    await sequence_runtime.stop_sequence_supervisors()
    await sequence_store.reset_for_tests()


def _declarations(factory):
    block = WorkflowNode(
        id="block", value="Block", description="Synthetic block.", category="Tests",
        inputs=(WorkflowCell("prompt", "encode", shape="textarea"),),
        outputs=(WorkflowCell("text", "display", shape="code"),),
        configure_prompt=lambda *_args: None, configure_download=lambda *_args: None,
        workflow_path=Path("unused.json"),
    )
    template = tuple(WorkflowSequenceStage(
        f"template_{index}", "block", (WorkflowSequenceLiteralBinding("prompt", "template"),),
    ) for index in range(2))
    sequence = WorkflowSequenceNode(
        id="dynamic", value="Dynamic", description="Synthetic expansion.", category="Tests",
        inputs=(WorkflowCell("count", "sequence", shape="textfield", props={"lfValue": 10}),),
        stages=template, final_output_ids=("text",), stages_factory=factory,
    )
    registry = WorkflowRegistry()
    registry.register(block)
    registry.register(sequence)
    return registry, sequence


def _stages(inputs):
    return tuple(WorkflowSequenceStage(
        f"item_{index}", "block",
        (WorkflowSequenceLiteralBinding("prompt", f"Item {index}"),),
        expose_in_history=index % 2 == 0,
    ) for index in range(int(inputs["count"])))


def _plan(registry, sequence, inputs=None):
    return sequence_runtime.normalize_sequence_definition(
        sequence, inputs or {}, workflow_resolver=registry.get,
        output_node_resolver=lambda *_args: "display",
    )


def test_factory_uses_public_defaults_and_input_override():
    registry, sequence = _declarations(_stages)
    plan = _plan(registry, sequence)
    assert len(plan["stages"]) == 10
    assert plan["stages"][0]["expose_in_history"] is True
    assert "expose_in_history" not in plan["stages"][1]
    assert plan["stages"][9]["bindings"][0]["value"] == "Item 9"
    assert len(sequence.stages) == 2  # Catalogue template stays immutable.
    assert len(_plan(registry, sequence, {"count": 3})["stages"]) == 3


def test_expanded_stages_reuse_declared_port_validation_and_bound():
    registry, sequence = _declarations(_stages)
    for count in (1, 65):
        with pytest.raises(ValueError, match="between 2 and 64"):
            _plan(registry, sequence, {"count": count})
    invalid = replace(sequence, stages_factory=lambda _inputs: (
        sequence.stages[0], WorkflowSequenceStage("invalid", "block", (
            WorkflowSequenceTextBinding("prompt", "private"),
        )),
    ))
    with pytest.raises(ValueError, match="unknown output port"):
        _plan(registry, invalid)


@pytest.mark.anyio
async def test_recovery_uses_frozen_stages_and_visible_history_children():
    factory_calls = []

    def factory(inputs):
        factory_calls.append(inputs)
        return _stages(inputs)

    registry, sequence = _declarations(factory)
    parent_id = "lf-sequence:dynamic-recovery"
    await sequence_runtime.create_sequence_execution(
        sequence, {"count": 10}, parent_run_id=parent_id,
        workflow_resolver=registry.get, output_node_resolver=lambda *_args: "display",
    )
    calls = []

    async def run_child(payload, *, owner_id):
        calls.append(payload)
        run_id = f"dynamic-child-{len(calls)}"
        await job_store.create_job(
            run_id, payload["workflowId"], owner_id=owner_id,
            submission_id=payload["submissionId"],
            request_fingerprint=lifecycle._fingerprint_payload(payload),
            comfy_url="http://comfy.test:8188",
        )
        await job_store.set_job_status(run_id, job_store.JobStatus.SUCCEEDED, result={
            "body": {"payload": {"history": {"outputs": {
                "display": {"lf_output": [{"value": payload["inputs"]["prompt"]}]},
            }}}},
        })
        return {"run_id": run_id}

    await sequence_runtime.advance_sequence_execution(parent_id, child_runner=run_child)
    sequence_runtime._locks.pop(parent_id, None)
    terminal = await sequence_runtime.drive_sequence_execution(
        parent_id, child_runner=run_child, poll_interval=0,
    )
    assert terminal["status"] == "succeeded", terminal["error"]
    assert len(factory_calls) == 1
    assert len(calls) == 10
    for index, payload in enumerate(calls):
        child = await job_store.get_job(f"dynamic-child-{index + 1}")
        assert sequence_runtime.is_sequence_child_submission_id(payload["submissionId"])
        assert sequence_runtime.is_sequence_child_job(child) is bool(index % 2)
        assert payload["inputs"]["prompt"] == f"Item {index}"
    assert sequence_runtime.is_sequence_child_submission_id(
        sequence_runtime.child_submission_id(parent_id, 63, "last"),
    )
    assert not sequence_runtime.is_sequence_child_submission_id(
        sequence_runtime.child_submission_id(parent_id, 64, "out_of_bound"),
    )
