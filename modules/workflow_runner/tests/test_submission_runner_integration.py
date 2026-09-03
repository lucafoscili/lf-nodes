from __future__ import annotations

import asyncio
import importlib.util
import sys

from pathlib import Path
from types import SimpleNamespace
from types import ModuleType
from unittest.mock import AsyncMock, Mock, patch

import pytest

from modules.workflow_runner.services import job_store, lifecycle
from modules.workflow_runner.services.admission import (
    WorkflowPromptContext,
    WorkflowSubmissionRequest,
)


pytestmark = pytest.mark.anyio


@pytest.fixture
def run_service_module():
    """Load an isolated run_service without importing ComfyUI's host runtime."""

    module_name = "modules.workflow_runner.services._runner_integration_target"
    module_path = Path(__file__).resolve().parents[1] / "services" / "run_service.py"

    executor_stub = ModuleType("modules.workflow_runner.services.executor")
    class WorkflowPreparationError(RuntimeError):
        def __init__(self, response_body, status):
            super().__init__(response_body.get("payload", {}).get("detail"))
            self.response_body = response_body
            self.status = status

    executor_stub.WorkflowPreparationError = WorkflowPreparationError
    executor_stub.CANCEL_OUTCOME_NOOP = "noop"
    executor_stub.CANCEL_OUTCOME_ORPHANED = "execution_state_lost"
    executor_stub.CANCEL_OUTCOME_PENDING = "pending_cancelled"
    executor_stub.CANCEL_OUTCOME_RUNNING = "running_cancel_requested"
    executor_stub.CANCEL_OUTCOME_TERMINAL = "terminal"
    executor_stub.CANCEL_OUTCOME_UNSUPPORTED = "unsupported"
    executor_stub._make_run_payload = Mock(return_value={})
    executor_stub._prepare_workflow_execution = Mock()
    executor_stub.cancel_workflow = AsyncMock()
    executor_stub.drain_workflow = AsyncMock()
    executor_stub.finalize_workflow = AsyncMock()
    executor_stub.interrupt_workflow = AsyncMock()
    executor_stub.post_workflow_submission = AsyncMock()
    executor_stub.prepare_workflow_submission = AsyncMock()
    executor_stub.validate_sequence_stage_preflight = Mock()

    helpers_package = ModuleType("modules.utils.helpers")
    helpers_package.__path__ = []
    comfy_stub = ModuleType("modules.utils.helpers.comfy")
    comfy_stub.safe_send_sync = Mock()
    server_stub = ModuleType("server")
    server_stub.PromptServer = Mock()

    synthetic_modules = {
        "server": server_stub,
        "modules.workflow_runner.services.executor": executor_stub,
        "modules.utils.helpers": helpers_package,
        "modules.utils.helpers.comfy": comfy_stub,
    }
    with patch.dict(sys.modules, synthetic_modules):
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        try:
            yield module
        finally:
            sys.modules.pop(module_name, None)


def _submission() -> WorkflowSubmissionRequest:
    prompt = {"1": {"class_type": "Example"}}
    return WorkflowSubmissionRequest(
        workflow_id="remove_bg",
        owner_id=None,
        client_id="client-1",
        comfy_url="http://comfy:8188",
        prompt=prompt,
        validation=(True, "", [], []),
        queue_body={"prompt": prompt, "client_id": "client-1"},
        queue_body_json="{}",
    )


def _sequence_admission_plan():
    from modules.workflow_runner.workflows.krea2 import (
        character_restage,
        identity_edit,
    )

    return {
        "inputs": {"profile": "turbo"},
        "stages": [
            {
                "workflow_id": identity_edit.id,
                "defaults": {"sampler": "baseline", "steps": 20},
                "bindings": [
                    {
                        "kind": "public_input",
                        "target_input_id": "sampler",
                        "public_input_id": "profile",
                    },
                    {
                        "kind": "literal",
                        "target_input_id": "cfg",
                        "value": 2.5,
                    },
                ],
            },
            {
                "workflow_id": character_restage.id,
                "defaults": {"sampler": "quality", "strength": 0.8},
                "bindings": [
                    {
                        "kind": "artifact",
                        "target_input_id": "reference_image",
                        "output_id": "image",
                    },
                    {
                        "kind": "literal",
                        "target_input_id": "strength",
                        "value": 0.6,
                    },
                ],
            },
        ],
    }


def _sequence_blocks_by_id():
    from modules.workflow_runner.workflows.krea2 import (
        character_restage,
        identity_edit,
    )

    return {
        identity_edit.id: identity_edit,
        character_restage.id: character_restage,
    }


async def test_external_call_cannot_claim_private_sequence_child_namespace(
    run_service_module,
):
    with pytest.raises(
        lifecycle.SubmissionConflictError,
        match="reserved for Runner orchestration",
    ):
        await run_service_module.run_workflow(
            {
                "workflowId": "remove_bg",
                "submissionId": "lfseq:0123456789abcdef0123456789abcdef:00",
                "inputs": {},
            }
        )


async def test_run_replay_with_stable_id_does_not_submit_twice(run_service_module):
    run_service = run_service_module
    request = _submission()
    context = WorkflowPromptContext(
        prompt_id="prompt-1",
        client_id=request.client_id,
        comfy_url=request.comfy_url,
        prompt=request.prompt,
        validation=request.validation,
        workflow_id=request.workflow_id,
    )
    admission = SimpleNamespace(submit=AsyncMock(return_value=context))

    def close_worker(worker, _prompt_id):
        worker.close()
        return True

    payload = {
        "workflowId": "remove_bg",
        "submissionId": "example:remove-bg:asset-001",
        "inputs": {"image": "asset-001.png"},
    }

    prepare = Mock(return_value=(SimpleNamespace(), request.prompt))
    with patch.object(
        run_service,
        "_prepare_workflow_execution",
        new=prepare,
    ), patch.object(
        run_service,
        "prepare_workflow_submission",
        new=AsyncMock(return_value=request),
    ), patch.object(
        run_service,
        "acquire_workflow_admission",
        new=AsyncMock(return_value=admission),
    ), patch.object(
        run_service,
        "create_job",
        new=AsyncMock(return_value=SimpleNamespace(id="prompt-1")),
    ) as create_job, patch.object(
        run_service,
        "_schedule_worker",
        side_effect=close_worker,
    ):
        first = await run_service.run_workflow(payload)
        replay = await run_service.run_workflow(payload)

    assert first["run_id"] == "prompt-1"
    assert first["submission_id"] == "example:remove-bg:asset-001"
    assert first["idempotent_replay"] is False
    assert replay["run_id"] == "prompt-1"
    assert replay["idempotent_replay"] is True
    prepare.assert_called_once_with(payload)
    admission.submit.assert_awaited_once()
    assert create_job.await_args.kwargs["submission_id"] == payload["submissionId"]
    assert create_job.await_args.kwargs["request_fingerprint"] == (
        lifecycle._fingerprint_payload(payload)
    )
    assert create_job.await_args.kwargs["comfy_url"] == request.comfy_url


async def test_run_replay_does_not_depend_on_mutable_workflow_preparation(
    run_service_module,
):
    run_service = run_service_module
    request = _submission()
    context = WorkflowPromptContext(
        prompt_id="prompt-replay",
        client_id=request.client_id,
        comfy_url=request.comfy_url,
        prompt=request.prompt,
        validation=request.validation,
        workflow_id=request.workflow_id,
    )
    admission = SimpleNamespace(submit=AsyncMock(return_value=context))
    payload = {
        "workflowId": "remove_bg",
        "submissionId": "example:remove-bg:mutable-001",
        "inputs": {"image": "asset-001.png"},
    }

    def close_worker(worker, _prompt_id):
        worker.close()
        return True

    prepare = Mock(return_value=(SimpleNamespace(), request.prompt))
    with patch.object(
        run_service,
        "_prepare_workflow_execution",
        new=prepare,
    ), patch.object(
        run_service,
        "prepare_workflow_submission",
        new=AsyncMock(return_value=request),
    ), patch.object(
        run_service,
        "acquire_workflow_admission",
        new=AsyncMock(return_value=admission),
    ), patch.object(
        run_service,
        "create_job",
        new=AsyncMock(return_value=SimpleNamespace(id="prompt-replay")),
    ), patch.object(run_service, "_schedule_worker", side_effect=close_worker):
        first = await run_service.run_workflow(payload)
        prepare.side_effect = RuntimeError("workflow definition was removed")
        replay = await run_service.run_workflow(payload)

    assert first["run_id"] == "prompt-replay"
    assert replay["run_id"] == "prompt-replay"
    assert replay["idempotent_replay"] is True
    prepare.assert_called_once_with(payload)
    admission.submit.assert_awaited_once()


async def test_sequence_parent_uses_stable_replay_and_exact_cancel_seam(
    run_service_module,
):
    run_service = run_service_module
    from modules.workflow_runner.workflows.orchestration import (
        identity_cleanup_restage,
    )

    payload = {
        "workflowId": identity_cleanup_restage.id,
        "submissionId": "example:identity-cleanup-restage:001",
        "inputs": {"identity_image": "portrait.png"},
    }
    started = AsyncMock(
        return_value={
            "parent_run_id": "ignored-by-service-response",
            "status": "running",
        }
    )
    validate_preflight = Mock()
    with patch.object(
        run_service,
        "_prepare_workflow_execution",
        return_value=(identity_cleanup_restage, {}),
    ), patch.object(
        run_service,
        "normalize_sequence_definition",
        return_value=_sequence_admission_plan(),
    ), patch.object(
        run_service,
        "validate_sequence_stage_preflight",
        new=validate_preflight,
    ), patch.object(
        run_service,
        "get_workflow",
        side_effect=_sequence_blocks_by_id().get,
    ), patch.object(
        run_service,
        "start_sequence_execution",
        new=started,
    ):
        first = await run_service.run_workflow(payload)
        replay = await run_service.run_workflow(payload)

    assert first["run_id"].startswith("lf-sequence:")
    assert first["submission_id"] == payload["submissionId"]
    assert first["idempotent_replay"] is False
    assert replay["run_id"] == first["run_id"]
    assert replay["idempotent_replay"] is True
    started.assert_awaited_once()
    assert started.await_args.kwargs["parent_run_id"] == first["run_id"]
    parent = await job_store.get_job(first["run_id"])
    assert parent is not None
    assert parent.workflow_id == identity_cleanup_restage.id
    assert parent.submission_id == payload["submissionId"]
    assert parent.comfy_url == "sequence://runner"
    assert validate_preflight.call_count == 2
    assert validate_preflight.call_args_list[0].args[1] == {
        "sampler": "turbo",
        "steps": 20,
        "cfg": 2.5,
    }
    assert validate_preflight.call_args_list[1].args[1] == {
        "sampler": "quality",
        "strength": 0.6,
    }

    sequence_cancel = AsyncMock(
        return_value={"status": "running", "cancel_requested": True}
    )
    run_service.cancel_workflow.reset_mock()
    with patch.object(
        run_service,
        "cancel_sequence_execution",
        new=sequence_cancel,
    ):
        cancelled = await run_service.cancel_workflow_submission(
            payload["submissionId"]
        )

    assert cancelled["cancel_requested"] is True
    sequence_cancel.assert_awaited_once_with(first["run_id"])
    run_service.cancel_workflow.assert_not_awaited()


async def test_sequence_start_failure_terminalizes_public_and_private_authority(
    run_service_module,
):
    run_service = run_service_module
    from modules.workflow_runner.workflows.orchestration import (
        identity_cleanup_restage,
    )

    payload = {
        "workflowId": identity_cleanup_restage.id,
        "submissionId": "example:identity-cleanup-restage:start-failure",
        "inputs": {"identity_image": "portrait.png"},
    }
    private_failure = AsyncMock(return_value={"status": "failed"})
    with patch.object(
        run_service,
        "_prepare_workflow_execution",
        return_value=(identity_cleanup_restage, {}),
    ), patch.object(
        run_service,
        "normalize_sequence_definition",
        return_value=_sequence_admission_plan(),
    ), patch.object(
        run_service,
        "get_workflow",
        side_effect=_sequence_blocks_by_id().get,
    ), patch.object(
        run_service,
        "start_sequence_execution",
        new=AsyncMock(side_effect=RuntimeError("scheduler unavailable")),
    ), patch.object(
        run_service,
        "fail_sequence_execution",
        new=private_failure,
    ):
        with pytest.raises(RuntimeError, match="scheduler unavailable"):
            await run_service.run_workflow(payload)

    parent_run_id = private_failure.await_args.args[0]
    private_failure.assert_awaited_once_with(
        parent_run_id,
        error="scheduler unavailable",
        error_detail="sequence_start_failed",
    )
    parent = await job_store.get_job(parent_run_id)
    assert parent is not None
    assert parent.status is job_store.JobStatus.FAILED
    replay = await lifecycle.get_submission(payload["submissionId"])
    assert replay is not None
    assert replay["status"] == "failed"


@pytest.mark.parametrize(
    ("blocked_stage", "error_input"),
    [(0, None), (1, "sampler")],
    ids=("declared-model-asset", "selected-option"),
)
async def test_sequence_setup_requirement_fails_before_parent_creation(
    run_service_module,
    blocked_stage,
    error_input,
):
    run_service = run_service_module
    from modules.workflow_runner.workflows.orchestration import (
        identity_cleanup_restage,
    )

    payload = {
        "workflowId": identity_cleanup_restage.id,
        "submissionId": f"example:sequence-blocked:{blocked_stage}",
        "inputs": {"identity_image": "portrait.png"},
    }
    calls = 0

    def reject_blocked_stage(_definition, _inputs):
        nonlocal calls
        current = calls
        calls += 1
        if current != blocked_stage:
            return
        error = {"message": "workflow_setup_required"}
        if error_input is not None:
            error["input"] = error_input
        raise run_service.WorkflowPreparationError(
            {
                "payload": {
                    "detail": "Required stage setup is unavailable.",
                    "error": error,
                }
            },
            409,
        )

    make_parent_id = Mock(return_value="lf-sequence:must-not-exist")
    bind_parent = AsyncMock()
    create_parent = AsyncMock()
    start_sequence = AsyncMock()
    with patch.object(
        run_service,
        "_prepare_workflow_execution",
        return_value=(identity_cleanup_restage, {}),
    ), patch.object(
        run_service,
        "normalize_sequence_definition",
        return_value=_sequence_admission_plan(),
    ), patch.object(
        run_service,
        "validate_sequence_stage_preflight",
        side_effect=reject_blocked_stage,
    ), patch.object(
        run_service,
        "get_workflow",
        side_effect=_sequence_blocks_by_id().get,
    ), patch.object(
        run_service,
        "make_sequence_parent_run_id",
        new=make_parent_id,
    ), patch.object(
        run_service,
        "bind_prompt",
        new=bind_parent,
    ), patch.object(
        run_service,
        "create_job",
        new=create_parent,
    ), patch.object(
        run_service,
        "start_sequence_execution",
        new=start_sequence,
    ):
        with pytest.raises(run_service.WorkflowPreparationError) as error:
            await run_service.run_workflow(payload)

    assert error.value.status == 409
    assert error.value.response_body["payload"]["error"]["message"] == (
        "workflow_setup_required"
    )
    make_parent_id.assert_not_called()
    bind_parent.assert_not_awaited()
    create_parent.assert_not_awaited()
    start_sequence.assert_not_awaited()


async def test_stable_replay_does_not_revalidate_an_expired_upload_reference(
    run_service_module,
):
    run_service = run_service_module
    request = _submission()
    context = WorkflowPromptContext(
        prompt_id="prompt-upload-replay",
        client_id=request.client_id,
        comfy_url=request.comfy_url,
        prompt=request.prompt,
        validation=request.validation,
        workflow_id=request.workflow_id,
    )
    admission = SimpleNamespace(submit=AsyncMock(return_value=context))
    payload = {
        "workflowId": "remove_bg",
        "submissionId": "example:remove-bg:upload-001",
        "inputs": {
            "image": {
                "schema": "lf.workflow-upload-ref.v1",
                "sourceRunId": "source-run",
                "inputId": "image",
            }
        },
    }
    effective_payload = {
        **payload,
        "inputs": {"image": "C:/ComfyUI/temp/reference.png"},
    }

    def close_worker(worker, _prompt_id):
        worker.close()
        return True

    materialize = AsyncMock(return_value=effective_payload)
    prepare = Mock(return_value=(SimpleNamespace(), request.prompt))
    with patch.object(
        run_service,
        "materialize_upload_references",
        new=materialize,
    ), patch.object(
        run_service,
        "_prepare_workflow_execution",
        new=prepare,
    ), patch.object(
        run_service,
        "prepare_workflow_submission",
        new=AsyncMock(return_value=request),
    ), patch.object(
        run_service,
        "acquire_workflow_admission",
        new=AsyncMock(return_value=admission),
    ), patch.object(
        run_service,
        "create_job",
        new=AsyncMock(return_value=SimpleNamespace(id="prompt-upload-replay")),
    ), patch.object(run_service, "_schedule_worker", side_effect=close_worker):
        first = await run_service.run_workflow(payload)
        materialize.side_effect = RuntimeError("source upload expired")
        replay = await run_service.run_workflow(payload)

    assert first["run_id"] == "prompt-upload-replay"
    assert replay["run_id"] == "prompt-upload-replay"
    assert replay["idempotent_replay"] is True
    materialize.assert_awaited_once_with(payload, None)
    prepare.assert_called_once_with(effective_payload)
    admission.submit.assert_awaited_once()


async def test_bind_failure_still_schedules_terminal_supervision(run_service_module):
    run_service = run_service_module
    request = _submission()
    context = WorkflowPromptContext(
        prompt_id="prompt-bind-failure",
        client_id=request.client_id,
        comfy_url=request.comfy_url,
        prompt=request.prompt,
        validation=request.validation,
        workflow_id=request.workflow_id,
    )
    admission = SimpleNamespace(submit=AsyncMock(return_value=context))
    scheduled = []

    def close_worker(worker, prompt_id):
        scheduled.append(prompt_id)
        worker.close()
        return True

    with patch.object(
        run_service,
        "_prepare_workflow_execution",
        return_value=(SimpleNamespace(), request.prompt),
    ), patch.object(
        run_service,
        "prepare_workflow_submission",
        new=AsyncMock(return_value=request),
    ), patch.object(
        run_service,
        "acquire_workflow_admission",
        new=AsyncMock(return_value=admission),
    ), patch.object(
        run_service,
        "bind_prompt",
        new=AsyncMock(side_effect=RuntimeError("bind failed")),
    ), patch.object(
        run_service,
        "create_job",
        new=AsyncMock(),
    ) as create_job, patch.object(
        run_service,
        "_schedule_worker",
        side_effect=close_worker,
    ):
        with pytest.raises(RuntimeError, match="bind failed"):
            await run_service.run_workflow(
                {"workflowId": "remove_bg", "inputs": {}}
            )

    assert scheduled == ["prompt-bind-failure"]
    create_job.assert_not_awaited()


async def test_targeted_cancel_uses_exact_running_prompt_and_is_idempotent(run_service_module):
    run_service = run_service_module
    payload = {
        "workflowId": "remove_bg",
        "submissionId": "example:cancel:001",
        "inputs": {},
    }
    await lifecycle.reserve_submission(payload, "remove_bg")
    await lifecycle.bind_prompt(
        "example:cancel:001",
        "prompt-cancel-001",
        "http://comfy:8188",
    )
    await lifecycle.record_running("prompt-cancel-001")
    await job_store.create_job("prompt-cancel-001", "remove_bg")
    await job_store.set_job_status("prompt-cancel-001", job_store.JobStatus.RUNNING)

    cancel = AsyncMock(return_value=run_service.CANCEL_OUTCOME_RUNNING)
    with patch.object(run_service, "cancel_workflow", new=cancel):
        first = await run_service.cancel_workflow_submission("example:cancel:001")
        replay = await run_service.cancel_workflow_submission("example:cancel:001")

    cancel.assert_awaited_once_with(
        "prompt-cancel-001",
        comfy_url="http://comfy:8188",
    )
    assert first["cancel_requested"] is True
    assert replay["event_count"] == first["event_count"]


@pytest.mark.parametrize("anyio_backend", ["asyncio"])
async def test_concurrent_cancel_requests_share_one_exact_core_operation(
    run_service_module,
    anyio_backend,
):
    run_service = run_service_module
    payload = {
        "workflowId": "remove_bg",
        "submissionId": "example:cancel-concurrent:001",
        "inputs": {},
    }
    await lifecycle.reserve_submission(payload, "remove_bg")
    await lifecycle.bind_prompt(
        "example:cancel-concurrent:001",
        "prompt-cancel-concurrent",
        "http://comfy:8188",
    )
    await lifecycle.record_running("prompt-cancel-concurrent")
    await job_store.create_job("prompt-cancel-concurrent", "remove_bg")
    await job_store.set_job_status(
        "prompt-cancel-concurrent",
        job_store.JobStatus.RUNNING,
    )

    release = asyncio.Event()

    async def cancel_once(*_args, **_kwargs):
        await release.wait()
        return run_service.CANCEL_OUTCOME_RUNNING

    cancel = AsyncMock(side_effect=cancel_once)
    with patch.object(run_service, "cancel_workflow", new=cancel):
        first = asyncio.create_task(
            run_service.cancel_workflow_submission("example:cancel-concurrent:001")
        )
        second = asyncio.create_task(
            run_service.cancel_workflow_submission("example:cancel-concurrent:001")
        )
        await asyncio.sleep(0)
        release.set()
        first_result, second_result = await asyncio.gather(first, second)

    cancel.assert_awaited_once_with(
        "prompt-cancel-concurrent",
        comfy_url="http://comfy:8188",
    )
    assert first_result == second_result
    assert first_result["cancel_requested"] is True


async def test_targeted_cancel_marks_exactly_dequeued_pending_prompt_cancelled(run_service_module):
    run_service = run_service_module
    payload = {
        "workflowId": "remove_bg",
        "submissionId": "example:pending:001",
        "inputs": {},
    }
    await lifecycle.reserve_submission(payload, "remove_bg")
    await lifecycle.bind_prompt(
        "example:pending:001",
        "prompt-pending-001",
        "http://comfy:8188",
    )
    await job_store.create_job("prompt-pending-001", "remove_bg")

    cancel = AsyncMock(return_value=run_service.CANCEL_OUTCOME_PENDING)
    with patch.object(run_service, "cancel_workflow", new=cancel):
        snapshot = await run_service.cancel_workflow_submission("example:pending:001")
        replay = await run_service.cancel_workflow_submission("example:pending:001")

    cancel.assert_awaited_once_with(
        "prompt-pending-001",
        comfy_url="http://comfy:8188",
    )
    assert snapshot["status"] == "cancelled"
    assert snapshot["cancel_requested"] is True
    assert replay["status"] == "cancelled"
    job = await job_store.get_job("prompt-pending-001")
    assert job is not None
    assert job.status == job_store.JobStatus.CANCELLED


async def test_targeted_cancel_terminalizes_proven_orphan_without_claiming_cancel(
    run_service_module,
):
    run_service = run_service_module
    submission_id = "example:orphaned:001"
    prompt_id = "prompt-orphaned-001"
    payload = {
        "workflowId": "remove_bg",
        "submissionId": submission_id,
        "inputs": {},
    }
    await lifecycle.reserve_submission(payload, "remove_bg")
    await lifecycle.bind_prompt(
        submission_id,
        prompt_id,
        "http://comfy:8188",
    )
    await lifecycle.record_running(prompt_id)
    await job_store.create_job(prompt_id, "remove_bg")
    await job_store.set_job_status(prompt_id, job_store.JobStatus.RUNNING)

    cancel = AsyncMock(return_value=run_service.CANCEL_OUTCOME_ORPHANED)
    with patch.object(run_service, "cancel_workflow", new=cancel):
        snapshot = await run_service.cancel_workflow_submission(submission_id)
        replay = await run_service.cancel_workflow_submission(submission_id)

    cancel.assert_awaited_once_with(prompt_id, comfy_url="http://comfy:8188")
    assert snapshot["status"] == "failed"
    assert snapshot["error"] == "execution_state_lost"
    assert snapshot["cancel_requested"] is False
    assert replay["status"] == "failed"
    job = await job_store.get_job(prompt_id)
    assert job is not None
    assert job.status == job_store.JobStatus.FAILED
    assert job.error == "execution_state_lost"
    assert (
        job.result["body"]["payload"]["error"]["message"]
        == "execution_state_lost"
    )


async def test_pending_dequeue_corrects_only_reconciler_state_loss(run_service_module):
    run_service = run_service_module
    submission_id = "example:pending-reconcile-race:001"
    prompt_id = "prompt-pending-reconcile-race"
    payload = {
        "workflowId": "remove_bg",
        "submissionId": submission_id,
        "inputs": {},
    }
    await lifecycle.reserve_submission(payload, "remove_bg")
    await lifecycle.bind_prompt(
        submission_id,
        prompt_id,
        "http://comfy:8188",
    )
    await job_store.create_job(prompt_id, "remove_bg")

    async def dequeue_after_synthetic_failure(*_args, **_kwargs):
        await job_store.set_job_status(
            prompt_id,
            job_store.JobStatus.FAILED,
            error="execution_state_lost",
        )
        await lifecycle.record_terminal(
            prompt_id,
            "failed",
            error="execution_state_lost",
        )
        return run_service.CANCEL_OUTCOME_PENDING

    with patch.object(
        run_service,
        "cancel_workflow",
        new=AsyncMock(side_effect=dequeue_after_synthetic_failure),
    ):
        snapshot = await run_service.cancel_workflow_submission(submission_id)

    assert snapshot["status"] == "cancelled"
    assert snapshot["cancel_requested"] is True
    assert snapshot["error"] is None
    job = await job_store.get_job(prompt_id)
    assert job is not None
    assert job.status == job_store.JobStatus.CANCELLED
    assert job.error is None
    with_events = await lifecycle.get_submission(submission_id)
    assert with_events is not None
    assert with_events["events"][-1]["type"] == "execution_state_lost_corrected"
    assert with_events["events"][-1]["details"]["previous_error"] == "execution_state_lost"
    assert prompt_id not in run_service._PROVEN_PENDING_CANCELLATIONS


async def test_pending_dequeue_never_relabels_a_genuine_failure(run_service_module):
    run_service = run_service_module
    submission_id = "example:pending-real-failure-race:001"
    prompt_id = "prompt-pending-real-failure-race"
    payload = {
        "workflowId": "remove_bg",
        "submissionId": submission_id,
        "inputs": {},
    }
    await lifecycle.reserve_submission(payload, "remove_bg")
    await lifecycle.bind_prompt(submission_id, prompt_id, "http://comfy:8188")
    await job_store.create_job(prompt_id, "remove_bg")

    async def contradictory_terminal(*_args, **_kwargs):
        await job_store.set_job_status(
            prompt_id,
            job_store.JobStatus.FAILED,
            error="execution_failed",
        )
        await lifecycle.record_terminal(
            prompt_id,
            "failed",
            error="execution_failed",
        )
        return run_service.CANCEL_OUTCOME_PENDING

    with patch.object(
        run_service,
        "cancel_workflow",
        new=AsyncMock(side_effect=contradictory_terminal),
    ):
        snapshot = await run_service.cancel_workflow_submission(submission_id)

    assert snapshot["status"] == "failed"
    assert snapshot["cancel_requested"] is False
    assert snapshot["error"] == "execution_failed"
    job = await job_store.get_job(prompt_id)
    assert job is not None
    assert job.status == job_store.JobStatus.FAILED
    assert job.error == "execution_failed"


@pytest.mark.parametrize("anyio_backend", ["asyncio"])
async def test_pending_cancel_wakes_supervisor_when_status_publish_fails(
    run_service_module,
    anyio_backend,
):
    run_service = run_service_module
    payload = {
        "workflowId": "remove_bg",
        "submissionId": "example:pending-write-failure:001",
        "inputs": {},
    }
    prompt_id = "prompt-pending-write-failure"
    await lifecycle.reserve_submission(payload, "remove_bg")
    await lifecycle.bind_prompt(
        "example:pending-write-failure:001",
        prompt_id,
        "http://comfy:8188",
    )
    await job_store.create_job(prompt_id, "remove_bg")

    started = asyncio.Event()

    async def wait_for_history(*_args, **_kwargs):
        started.set()
        await asyncio.Event().wait()

    admission = SimpleNamespace(release=AsyncMock())
    real_cas_status = run_service.set_job_status_if_unchanged
    publish_calls = 0

    async def fail_first_publish(*args, **kwargs):
        nonlocal publish_calls
        publish_calls += 1
        if publish_calls == 1:
            raise RuntimeError("store unavailable")
        return await real_cas_status(*args, **kwargs)

    with patch.object(
        run_service,
        "cancel_workflow",
        new=AsyncMock(return_value=run_service.CANCEL_OUTCOME_PENDING),
    ), patch.object(
        run_service,
        "finalize_workflow",
        new=AsyncMock(side_effect=wait_for_history),
    ), patch.object(
        run_service,
        "set_job_status_if_unchanged",
        new=AsyncMock(side_effect=fail_first_publish),
    ):
        supervisor = asyncio.create_task(
            run_service._finalize_admitted_workflow(
                prompt_id=prompt_id,
                client_id="client-1",
                comfy_url="http://comfy:8188",
                validation=(True, "", [], []),
                admission=admission,
                submission_id="example:pending-write-failure:001",
            )
        )
        run_service._WORKERS_BY_PROMPT[prompt_id] = supervisor
        await started.wait()

        with pytest.raises(RuntimeError, match="store unavailable"):
            await run_service.cancel_workflow_submission(
                "example:pending-write-failure:001"
            )

        await supervisor

    snapshot = await lifecycle.get_submission(
        "example:pending-write-failure:001",
        include_events=False,
    )
    job = await job_store.get_job(prompt_id)
    assert snapshot is not None and snapshot["status"] == "cancelled"
    assert job is not None and job.status == job_store.JobStatus.CANCELLED
    assert admission.release.await_args.args[0].status == "cancelled"


async def test_terminal_cancel_race_is_idempotent_without_relabelling_intent(run_service_module):
    run_service = run_service_module
    payload = {
        "workflowId": "remove_bg",
        "submissionId": "example:terminal-race:001",
        "inputs": {},
    }
    await lifecycle.reserve_submission(payload, "remove_bg")
    await lifecycle.bind_prompt(
        "example:terminal-race:001",
        "prompt-terminal-race",
        "http://comfy:8188",
    )
    await lifecycle.record_running("prompt-terminal-race")
    await job_store.create_job("prompt-terminal-race", "remove_bg")
    await job_store.set_job_status("prompt-terminal-race", job_store.JobStatus.RUNNING)

    cancel = AsyncMock(return_value=run_service.CANCEL_OUTCOME_TERMINAL)
    with patch.object(run_service, "cancel_workflow", new=cancel):
        snapshot = await run_service.cancel_workflow_submission(
            "example:terminal-race:001"
        )

    assert snapshot["status"] == "running"
    assert snapshot["cancel_requested"] is False


async def test_cancel_request_does_not_relabel_proven_failure(run_service_module):
    run_service = run_service_module
    payload = {
        "workflowId": "remove_bg",
        "submissionId": "example:cancel-race:001",
        "inputs": {},
    }
    await lifecycle.reserve_submission(payload, "remove_bg")
    await lifecycle.bind_prompt(
        "example:cancel-race:001",
        "prompt-cancel-race",
        "http://comfy:8188",
    )
    await lifecycle.record_running("prompt-cancel-race")
    await lifecycle.record_cancel_requested("example:cancel-race:001")

    admission = SimpleNamespace(release=AsyncMock())
    with patch.object(
        run_service,
        "finalize_workflow",
        new=AsyncMock(
            return_value=(
                job_store.JobStatus.FAILED,
                {"error": "model execution failed"},
                500,
            )
        ),
    ), patch.object(
        run_service,
        "set_job_status",
        new=AsyncMock(),
    ) as set_status, patch.object(
        run_service,
        "_emit_run_progress",
    ):
        await run_service._finalize_admitted_workflow(
            prompt_id="prompt-cancel-race",
            client_id="client-1",
            comfy_url="http://comfy:8188",
            validation=(True, "", [], []),
            admission=admission,
            submission_id="example:cancel-race:001",
        )

    set_status.assert_awaited_once()
    assert set_status.await_args.args[1] == job_store.JobStatus.FAILED
    snapshot = await lifecycle.get_submission(
        "example:cancel-race:001",
        include_events=False,
    )
    assert snapshot is not None
    assert snapshot["status"] == "failed"
    assert admission.release.await_args.args[0].status == "failed"
