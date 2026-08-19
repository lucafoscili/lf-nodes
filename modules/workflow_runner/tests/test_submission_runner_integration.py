from __future__ import annotations

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
    executor_stub._make_run_payload = Mock(return_value={})
    executor_stub._prepare_workflow_execution = Mock()
    executor_stub.drain_workflow = AsyncMock()
    executor_stub.finalize_workflow = AsyncMock()
    executor_stub.interrupt_workflow = AsyncMock()
    executor_stub.post_workflow_submission = AsyncMock()
    executor_stub.prepare_workflow_submission = AsyncMock()

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
        "submissionId": "velora:remove-bg:asset-001",
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
    ), patch.object(run_service, "_schedule_worker", side_effect=close_worker):
        first = await run_service.run_workflow(payload)
        replay = await run_service.run_workflow(payload)

    assert first["run_id"] == "prompt-1"
    assert first["submission_id"] == "velora:remove-bg:asset-001"
    assert first["idempotent_replay"] is False
    assert replay["run_id"] == "prompt-1"
    assert replay["idempotent_replay"] is True
    prepare.assert_called_once_with(payload)
    admission.submit.assert_awaited_once()


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
        "submissionId": "velora:remove-bg:mutable-001",
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
        "submissionId": "velora:cancel:001",
        "inputs": {},
    }
    await lifecycle.reserve_submission(payload, "remove_bg")
    await lifecycle.bind_prompt(
        "velora:cancel:001",
        "prompt-cancel-001",
        "http://comfy:8188",
    )
    await lifecycle.record_running("prompt-cancel-001")
    await job_store.create_job("prompt-cancel-001", "remove_bg")
    await job_store.set_job_status("prompt-cancel-001", job_store.JobStatus.RUNNING)

    interrupt = AsyncMock(return_value=True)
    with patch.object(run_service, "interrupt_workflow", new=interrupt):
        first = await run_service.cancel_workflow_submission("velora:cancel:001")
        replay = await run_service.cancel_workflow_submission("velora:cancel:001")

    interrupt.assert_awaited_once_with(
        "prompt-cancel-001",
        comfy_url="http://comfy:8188",
    )
    assert first["cancel_requested"] is True
    assert replay["event_count"] == first["event_count"]


async def test_targeted_cancel_rejects_pending_prompt_without_interrupting(run_service_module):
    run_service = run_service_module
    payload = {
        "workflowId": "remove_bg",
        "submissionId": "velora:pending:001",
        "inputs": {},
    }
    await lifecycle.reserve_submission(payload, "remove_bg")
    await lifecycle.bind_prompt(
        "velora:pending:001",
        "prompt-pending-001",
        "http://comfy:8188",
    )
    await job_store.create_job("prompt-pending-001", "remove_bg")

    interrupt = AsyncMock(return_value=True)
    with patch.object(run_service, "interrupt_workflow", new=interrupt):
        with pytest.raises(run_service.WorkflowCancellationError) as error:
            await run_service.cancel_workflow_submission("velora:pending:001")

    assert error.value.detail == "submission_not_running"
    assert error.value.status == 409
    interrupt.assert_not_awaited()


async def test_cancel_request_does_not_relabel_proven_failure(run_service_module):
    run_service = run_service_module
    payload = {
        "workflowId": "remove_bg",
        "submissionId": "velora:cancel-race:001",
        "inputs": {},
    }
    await lifecycle.reserve_submission(payload, "remove_bg")
    await lifecycle.bind_prompt(
        "velora:cancel-race:001",
        "prompt-cancel-race",
        "http://comfy:8188",
    )
    await lifecycle.record_running("prompt-cancel-race")
    await lifecycle.record_cancel_requested("velora:cancel-race:001")

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
            submission_id="velora:cancel-race:001",
        )

    set_status.assert_awaited_once()
    assert set_status.await_args.args[1] == job_store.JobStatus.FAILED
    snapshot = await lifecycle.get_submission(
        "velora:cancel-race:001",
        include_events=False,
    )
    assert snapshot is not None
    assert snapshot["status"] == "failed"
    assert admission.release.await_args.args[0].status == "failed"
