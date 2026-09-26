"""Declared, owner-bound text handoff between ordinary Runner blocks."""

from dataclasses import replace
from pathlib import Path

import pytest
import pytest_asyncio

from modules.workflow_runner.services import job_store, lifecycle, sequence_runtime, sequence_store
from modules.workflow_runner.services.registry import (
    WorkflowCell,
    WorkflowNode,
    WorkflowRegistry,
    WorkflowSequenceNode,
    WorkflowSequencePublicInputBinding,
    WorkflowSequenceStage,
    WorkflowSequenceTextBinding,
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


def _block(workflow_id, *, inputs=(), output_shape="code"):
    return WorkflowNode(
        id=workflow_id, value=workflow_id, description="Text binding test block.",
        category="Tests", inputs=inputs,
        outputs=(WorkflowCell(id="text", node_id="display", shape=output_shape),),
        configure_prompt=lambda _prompt, _inputs: None,
        configure_download=lambda _prompt, _inputs: None,
        workflow_path=Path("unused.json"),
    )


def _declarations(*, source_stage_id=None, output_id="text", target_shape="textarea"):
    writer = _block("writer")
    renderer = _block("renderer", inputs=(
        WorkflowCell(id="prompt", node_id="encode", shape=target_shape),
    ))
    sequence = WorkflowSequenceNode(
        id="write_render", value="Write then render", description="Text handoff.",
        category="Tests", inputs=(), final_output_ids=("text",),
        stages=(
            WorkflowSequenceStage("write", "writer"),
            WorkflowSequenceStage("render", "renderer", (
                WorkflowSequenceTextBinding("prompt", output_id, source_stage_id),
            )),
        ),
    )
    return writer, renderer, sequence


def _registry(*blocks):
    registry = WorkflowRegistry()
    for block in blocks:
        registry.register(block)
    return registry


def _plan(registry, sequence, inputs=None):
    registry.register(sequence)
    return sequence_runtime.normalize_sequence_definition(
        sequence, inputs or {}, workflow_resolver=registry.get,
        output_node_resolver=lambda workflow_id, output_id: next(
            cell.node_id for cell in registry.get(workflow_id).outputs if cell.id == output_id
        ),
    )


def _result(items):
    return {"http_status": 200, "body": {"payload": {"history": {"outputs": {
        "display": {"lf_output": items},
        "private": {"lf_output": [{"value": "must not be selected"}]},
    }}}}}


@pytest.mark.parametrize("shape", ["textarea", "textfield"])
def test_text_binding_normalizes_declared_output_and_preflight_is_separate(shape):
    writer, renderer, sequence = _declarations(target_shape=shape)
    plan = _plan(_registry(writer, renderer), sequence)
    assert plan["stages"][1]["bindings"] == [{
        "kind": "text", "target_input_id": "prompt",
        "output_id": "text", "output_node_id": "display",
    }]
    preflight = sequence_runtime.sequence_stage_preflight_inputs(plan, 1)
    assert isinstance(preflight["prompt"], str) and preflight["prompt"].strip()
    assert sequence_runtime.sequence_stage_declared_inputs(plan, 1) == {}
    assert plan["stages"][1]["defaults"] == {}


@pytest.mark.parametrize(("source_stage_id", "message"), [
    ("missing", "unknown source stage"), ("render", "from itself"),
])
def test_text_binding_rejects_invalid_named_source(source_stage_id, message):
    writer, renderer, sequence = _declarations(source_stage_id=source_stage_id)
    with pytest.raises(ValueError, match=message):
        _registry(writer, renderer).register(sequence)


def test_text_binding_rejects_forward_and_first_stage_sources():
    writer, renderer, sequence = _declarations(source_stage_id="later")
    sequence = replace(sequence, stages=(*sequence.stages, WorkflowSequenceStage("later", "writer")))
    with pytest.raises(ValueError, match="future source stage"):
        _registry(writer, renderer).register(sequence)
    first = WorkflowSequenceStage("first", "renderer", (WorkflowSequenceTextBinding("prompt", "text"),))
    sequence = replace(sequence, stages=(first, WorkflowSequenceStage("last", "writer")))
    with pytest.raises(ValueError, match="first sequence stage"):
        _registry(writer, renderer).register(sequence)


def test_text_binding_cannot_read_undeclared_output_or_target_nontext_input():
    writer, renderer, sequence = _declarations(output_id="private")
    with pytest.raises(ValueError, match="unknown output port"):
        _registry(writer, renderer).register(sequence)
    writer, renderer, sequence = _declarations(target_shape="upload")
    with pytest.raises(ValueError, match="textarea or textfield"):
        _registry(writer, renderer).register(sequence)
    writer, renderer, sequence = _declarations()
    writer.outputs = (WorkflowCell(id="text", node_id="display", shape="masonry"),)
    with pytest.raises(ValueError, match="must be a text display"):
        _registry(writer, renderer).register(sequence)


@pytest.mark.parametrize("payload_key", ["string", "value"])
@pytest.mark.anyio
async def test_durable_text_handoff_preserves_verbatim_named_source(payload_key):
    writer, renderer, sequence = _declarations(source_stage_id="write")
    sequence = replace(sequence, stages=(
        sequence.stages[0], WorkflowSequenceStage("middle", "writer"), sequence.stages[1],
    ))
    registry = _registry(writer, renderer)
    registry.register(sequence)
    text = "  [Shot 1]\nCi vediamo domani.\n\nUnicode: è ☃\t  "
    calls = []

    async def run_child(payload, *, owner_id):
        calls.append(payload)
        run_id = f"child-{len(calls)}"
        await job_store.create_job(
            run_id, payload["workflowId"], owner_id=owner_id,
            submission_id=payload["submissionId"],
            request_fingerprint=lifecycle._fingerprint_payload(payload),
            comfy_url="http://comfy.test:8188",
        )
        await job_store.set_job_status(
            run_id, job_store.JobStatus.SUCCEEDED,
            result=_result([{payload_key: text if len(calls) == 1 else "other stage"}]),
        )
        return {"run_id": run_id, "submission_id": payload["submissionId"]}

    parent_id = "lf-sequence:text-handoff"
    await sequence_runtime.create_sequence_execution(
        sequence, {}, owner_id="owner", parent_run_id=parent_id,
        workflow_resolver=registry.get, output_node_resolver=lambda *_args: "display",
    )
    terminal = await sequence_runtime.drive_sequence_execution(
        parent_id, child_runner=run_child, poll_interval=0,
    )
    assert terminal["status"] == "succeeded", terminal
    assert calls[2]["inputs"] == {"prompt": text}
    assert "Pending text" not in str(calls)


@pytest.mark.parametrize(("items", "message"), [
    (None, "missing"), ([], "missing"),
    ([{"value": "one"}, {"value": "two"}], "ambiguous"),
    ([{"value": 17}], "one string or value"),
    ([{"json": {"value": "nested"}}], "one string or value"),
    ([{"value": "one", "string": "two"}], "one string or value"),
])
def test_missing_ambiguous_and_nontext_outputs_fail_without_coercion(items, message):
    with pytest.raises(sequence_runtime.SequenceExecutionError, match=message) as error:
        sequence_runtime._text_output(_result(items), "display", "text")
    assert error.value.detail == "sequence_text_unavailable"


@pytest.mark.anyio
async def test_text_handoff_checks_prior_child_owner_and_missing_result():
    writer, renderer, sequence = _declarations(source_stage_id="write")
    plan = _plan(_registry(writer, renderer), sequence)
    source = plan["stages"][0]
    source.update(child_run_id="prior", child_submission_id="submission", child_request_fingerprint="a" * 64)
    await job_store.create_job(
        "prior", "writer", owner_id="another-owner",
        submission_id="submission", request_fingerprint="a" * 64,
        comfy_url="http://comfy.test:8188",
    )
    await job_store.set_job_status("prior", job_store.JobStatus.SUCCEEDED, result=_result([{"value": "private"}]))
    with pytest.raises(sequence_runtime.SequenceExecutionError) as error:
        await sequence_runtime._stage_inputs(plan, 1, "owner")
    assert error.value.detail == "sequence_child_authority_mismatch"
    await job_store.remove_job("prior")
    with pytest.raises(sequence_runtime.SequenceExecutionError) as error:
        await sequence_runtime._stage_inputs(plan, 1, "owner")
    assert error.value.detail == "sequence_text_unavailable"


@pytest.mark.parametrize("target_required", [False, True])
def test_only_optional_upload_to_optional_upload_may_be_omitted(target_required):
    writer, renderer, sequence = _declarations()
    writer.inputs = (WorkflowCell("image", "load", shape="upload", required=target_required),)
    sequence = replace(
        sequence,
        inputs=(WorkflowCell("image", "sequence", shape="upload", required=False),),
        stages=(
            replace(sequence.stages[0], bindings=(WorkflowSequencePublicInputBinding("image", "image"),)),
            sequence.stages[1],
        ),
    )
    registry = _registry(writer, renderer)
    if target_required:
        with pytest.raises(ValueError, match="required by stage.*missing"):
            _plan(registry, sequence)
    else:
        plan = _plan(registry, sequence)
        assert plan["inputs"] == {}
        assert sequence_runtime.sequence_stage_declared_inputs(plan, 0) == {}
        assert not plan["stages"][0]["bindings"]
        supplied = _plan(registry, sequence, {"image": "source.png"})
        assert sequence_runtime.sequence_stage_declared_inputs(supplied, 0) == {"image": "source.png"}
