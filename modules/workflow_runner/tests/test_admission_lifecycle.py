"""Focused tests for the generic Workflow Runner admission lifecycle."""

from __future__ import annotations

import asyncio
import json
import sys
import types

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest


# This suite exercises Workflow Runner orchestration, not ComfyUI internals.
# Install the two narrow runtime ABIs before importing executor/run_service so
# the tests remain pure and do not depend on a checkout-level Comfy bootstrap.
if "execution" not in sys.modules:
    execution_module = types.ModuleType("execution")

    async def _validate_prompt(*args, **kwargs):
        return True, "", (), ()

    execution_module.validate_prompt = _validate_prompt  # type: ignore[attr-defined]
    sys.modules["execution"] = execution_module

if "server" not in sys.modules:
    server_module = types.ModuleType("server")
    server_module.PromptServer = SimpleNamespace(  # type: ignore[attr-defined]
        instance=SimpleNamespace(loop=None)
    )
    sys.modules["server"] = server_module

if "modules.utils.helpers" not in sys.modules:
    helpers_module = types.ModuleType("modules.utils.helpers")
    helpers_module.__path__ = []  # type: ignore[attr-defined]
    sys.modules["modules.utils.helpers"] = helpers_module

if "modules.utils.helpers.conversion" not in sys.modules:
    conversion_module = types.ModuleType("modules.utils.helpers.conversion")
    conversion_module.json_safe = lambda value: value  # type: ignore[attr-defined]
    sys.modules["modules.utils.helpers.conversion"] = conversion_module

if "modules.utils.helpers.comfy" not in sys.modules:
    comfy_helpers_module = types.ModuleType("modules.utils.helpers.comfy")
    comfy_helpers_module.safe_send_sync = (  # type: ignore[attr-defined]
        lambda *args, **kwargs: None
    )
    sys.modules["modules.utils.helpers.comfy"] = comfy_helpers_module


pytestmark = pytest.mark.asyncio


def make_submission(
    *,
    owner_id: str | None = "owner-1",
    required_provider_id: str | None = None,
):
    from modules.workflow_runner.services.admission import WorkflowSubmissionRequest

    prompt = {"save": {"class_type": "SaveImage", "inputs": {}}}
    body = {
        "prompt": prompt,
        "client_id": "client-1",
        "extra_data": {
            "lf_nodes": {"workflow_id": "wf-1"},
            "trace_id": "trace-1",
        },
    }
    return WorkflowSubmissionRequest(
        workflow_id="wf-1",
        owner_id=owner_id,
        client_id="client-1",
        comfy_url="http://127.0.0.1:8188",
        prompt=prompt,
        validation=(True, "", ("save",), ()),
        queue_body=body,
        queue_body_json=json.dumps(body),
        required_provider_id=required_provider_id,
        admission_metadata=(
            {
                "provider_id": required_provider_id,
                "expected_vram_mb": 24576,
                "max_duration_seconds": 600.0,
                "required": True,
            }
            if required_provider_id
            else {}
        ),
    )


class RecordingLease:
    def __init__(self, events: list[str], *, submit_error: Exception | None = None) -> None:
        self.events = events
        self.submit_error = submit_error
        self.submissions = []
        self.outcomes = []
        self.released = asyncio.Event()

    async def submit(self, request, default_submit):
        from modules.workflow_runner.services.admission import WorkflowPromptContext

        self.events.append("provider_submit")
        self.submissions.append(request)
        if self.submit_error is not None:
            raise self.submit_error
        # A custom provider owns this queue boundary and deliberately does not
        # invoke LF's default aiohttp delegate.
        return WorkflowPromptContext(
            prompt_id="prompt-1",
            client_id=request.client_id,
            comfy_url=request.comfy_url,
            prompt=request.prompt,
            validation=request.validation,
            workflow_id=request.workflow_id,
        )

    async def release(self, outcome) -> None:
        self.events.append("release")
        self.outcomes.append(outcome)
        self.released.set()


class RecordingProvider:
    provider_id = "recording"

    def __init__(self, events: list[str], lease: RecordingLease) -> None:
        self.events = events
        self.lease = lease
        self.requests = []

    async def acquire(self, request):
        self.events.append("acquire")
        self.requests.append(request)
        return self.lease


@pytest.mark.parametrize("is_api_call", [False, True], ids=["browser", "headless"])
async def test_provider_owns_queue_and_spans_terminal_for_all_callers(
    monkeypatch,
    is_api_call: bool,
):
    from modules.workflow_runner.services import admission, run_service
    from modules.workflow_runner.services.job_store import JobStatus

    events: list[str] = []
    lease = RecordingLease(events)
    provider = RecordingProvider(events, lease)
    previous = admission.set_workflow_admission_provider(provider)
    submission = make_submission(required_provider_id="recording")
    default_submit = AsyncMock()

    async def prepare(*args, **kwargs):
        events.append("prepare")
        return submission

    async def create_job(*args, **kwargs):
        events.append("job")
        return SimpleNamespace(id="prompt-1")

    async def finalize(*args, **kwargs):
        events.append("finalize")
        return JobStatus.SUCCEEDED, {"payload": {"history": {"outputs": {}}}}, 200

    async def set_status(*args, **kwargs):
        events.append("job_status")

    monkeypatch.setattr(
        run_service,
        "_prepare_workflow_execution",
        lambda payload: (SimpleNamespace(), submission.prompt),
    )
    monkeypatch.setattr(run_service, "prepare_workflow_submission", prepare)
    monkeypatch.setattr(run_service, "post_workflow_submission", default_submit)
    monkeypatch.setattr(run_service, "create_job", create_job)
    monkeypatch.setattr(run_service, "finalize_workflow", finalize)
    monkeypatch.setattr(run_service, "set_job_status", set_status)
    monkeypatch.setattr(run_service, "_emit_run_progress", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        run_service.PromptServer,
        "instance",
        SimpleNamespace(loop=None),
        raising=False,
    )

    try:
        result = await run_service.run_workflow(
            {"workflowId": "wf-1", "inputs": {}},
            owner_id="owner-1",
            is_api_call=is_api_call,
        )
        await asyncio.wait_for(lease.released.wait(), timeout=1)
    finally:
        admission.set_workflow_admission_provider(previous)

    assert result == {"run_id": "prompt-1"}
    assert events == [
        "prepare",
        "acquire",
        "provider_submit",
        "job",
        "finalize",
        "job_status",
        "release",
    ]
    default_submit.assert_not_awaited()
    assert provider.requests == [submission]
    assert lease.submissions == [submission]
    assert lease.outcomes[0].prompt_id == "prompt-1"
    assert lease.outcomes[0].status == JobStatus.SUCCEEDED.value


async def test_default_provider_delegates_exact_submission_once():
    from modules.workflow_runner.services import admission
    from modules.workflow_runner.services.admission import WorkflowPromptContext

    previous = admission.set_workflow_admission_provider(None)
    submission = make_submission()
    received = []

    async def direct_submit(request):
        received.append(request)
        return WorkflowPromptContext(
            "prompt-default",
            request.client_id,
            request.comfy_url,
            request.prompt,
            request.validation,
            request.workflow_id,
        )

    try:
        handle = await admission.acquire_workflow_admission(submission)
        context = await handle.submit(direct_submit)
        with pytest.raises(RuntimeError, match="exactly one submission"):
            await handle.submit(direct_submit)
        await handle.release(
            admission.WorkflowAdmissionOutcome(context.prompt_id, "succeeded")
        )
    finally:
        admission.set_workflow_admission_provider(previous)

    assert received == [submission]
    assert context.prompt_id == "prompt-default"


async def test_required_provider_fails_closed_before_acquire():
    from modules.workflow_runner.services import admission

    previous = admission.set_workflow_admission_provider(None)
    submission = make_submission(required_provider_id="recording")
    try:
        with pytest.raises(PermissionError, match="requires admission provider 'recording'"):
            await admission.acquire_workflow_admission(submission)
        with pytest.raises(PermissionError, match="direct default submission is forbidden"):
            await admission.acquire_default_workflow_admission(submission)
    finally:
        admission.set_workflow_admission_provider(previous)


async def test_submission_request_is_deep_frozen_and_canonical():
    from modules.workflow_runner.services.admission import WorkflowSubmissionRequest

    prompt = {
        "node": {
            "class_type": "Example",
            "inputs": {"values": [1, {"nested": "original"}]},
        }
    }
    body = {
        "extra_data": {"z": 2, "a": {"items": ["x", "y"]}},
        "client_id": "client-frozen",
        "prompt": prompt,
    }
    request = WorkflowSubmissionRequest(
        workflow_id="wf-frozen",
        owner_id=None,
        client_id="client-frozen",
        comfy_url="http://127.0.0.1:8188",
        prompt={"ignored": "request.prompt is derived from queue_body"},
        validation=(True, {"mutable": [1]}, (), ()),
        queue_body=body,
        queue_body_json="caller supplied bytes are deliberately ignored",
    )

    prompt["node"]["inputs"]["values"][1]["nested"] = "mutated"
    assert request.prompt is request.queue_body["prompt"]
    assert request.prompt["node"]["inputs"]["values"][1]["nested"] == "original"
    assert request.queue_body_json == json.dumps(
        json.loads(request.queue_body_json),
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    with pytest.raises(TypeError):
        request.queue_body["prompt"] = {}
    with pytest.raises(TypeError):
        request.prompt["node"]["inputs"] = {}
    with pytest.raises(TypeError):
        request.validation[1]["mutable"] = ()


async def test_delegated_context_cannot_be_replaced_or_delegate_reused():
    from modules.workflow_runner.services import admission
    from modules.workflow_runner.services.admission import WorkflowPromptContext

    submission = make_submission()
    saved = {}

    class ReplacingLease:
        async def submit(self, request, default_submit):
            saved["delegate"] = default_submit
            original = await default_submit(request)
            return WorkflowPromptContext(
                "swapped-prompt",
                original.client_id,
                original.comfy_url,
                original.prompt,
                original.validation,
                original.workflow_id,
            )

        async def release(self, outcome):
            return None

    async def direct_submit(request):
        return WorkflowPromptContext(
            "canonical-prompt",
            request.client_id,
            request.comfy_url,
            request.prompt,
            request.validation,
            request.workflow_id,
        )

    handle = admission.AcquiredWorkflowAdmission(ReplacingLease(), submission)
    with pytest.raises(PermissionError, match="replaced the delegated prompt context"):
        await handle.submit(direct_submit)
    with pytest.raises(RuntimeError, match="delegate has expired"):
        await saved["delegate"](submission)


async def test_prequeue_marker_after_delegation_becomes_ambiguous():
    from modules.workflow_runner.services import admission
    from modules.workflow_runner.services.admission import WorkflowPromptContext

    submission = make_submission()

    class ContradictoryLease:
        async def submit(self, request, default_submit):
            await default_submit(request)
            raise admission.WorkflowSubmissionRejectedBeforeQueue("too late")

        async def release(self, outcome):
            return None

    async def direct_submit(request):
        return WorkflowPromptContext(
            "accepted-prompt",
            request.client_id,
            request.comfy_url,
            request.prompt,
            request.validation,
            request.workflow_id,
        )

    handle = admission.AcquiredWorkflowAdmission(ContradictoryLease(), submission)
    with pytest.raises(admission.WorkflowSubmissionOutcomeUnknown):
        await handle.submit(direct_submit)


async def test_release_failure_remains_retryable_and_retained():
    from modules.workflow_runner.services import admission

    submission = make_submission()

    class FlakyReleaseLease:
        def __init__(self):
            self.calls = 0

        async def submit(self, request, default_submit):
            raise AssertionError("unused")

        async def release(self, outcome):
            self.calls += 1
            if self.calls == 1:
                raise RuntimeError("release failed")

    lease = FlakyReleaseLease()
    handle = admission.AcquiredWorkflowAdmission(lease, submission)
    outcome = admission.WorkflowAdmissionOutcome(None, "reconciled")

    with pytest.raises(RuntimeError, match="release failed"):
        await handle.release(outcome)
    assert handle.released is False
    assert admission.get_retained_workflow_admission(submission.client_id) is not None

    reconciled = await admission.reconcile_retained_workflow_admission(
        submission.client_id,
        outcome,
    )
    assert reconciled is True
    assert handle.released is True
    assert lease.calls == 2
    assert admission.get_retained_workflow_admission(submission.client_id) is None
    assert (
        await admission.reconcile_retained_workflow_admission(
            submission.client_id,
            outcome,
        )
        is False
    )


async def test_admission_denial_prevents_queue(monkeypatch):
    from modules.workflow_runner.services import admission, run_service

    class DenyingProvider:
        provider_id = "denying"

        async def acquire(self, request):
            raise RuntimeError("resource busy")

    previous = admission.set_workflow_admission_provider(DenyingProvider())
    submission = make_submission()
    default_submit = AsyncMock()
    monkeypatch.setattr(
        run_service,
        "_prepare_workflow_execution",
        lambda payload: (SimpleNamespace(), submission.prompt),
    )
    monkeypatch.setattr(
        run_service,
        "prepare_workflow_submission",
        AsyncMock(return_value=submission),
    )
    monkeypatch.setattr(run_service, "post_workflow_submission", default_submit)

    try:
        with pytest.raises(RuntimeError, match="resource busy"):
            await run_service.run_workflow({"workflowId": "wf-1", "inputs": {}})
    finally:
        admission.set_workflow_admission_provider(previous)

    default_submit.assert_not_awaited()


async def test_explicit_prequeue_rejection_releases_admission(monkeypatch):
    from modules.workflow_runner.services import admission, run_service

    events: list[str] = []
    queue_error = admission.WorkflowSubmissionRejectedBeforeQueue("not submitted")
    lease = RecordingLease(events, submit_error=queue_error)
    provider = RecordingProvider(events, lease)
    previous = admission.set_workflow_admission_provider(provider)
    submission = make_submission()

    monkeypatch.setattr(
        run_service,
        "_prepare_workflow_execution",
        lambda payload: (SimpleNamespace(), submission.prompt),
    )
    monkeypatch.setattr(
        run_service,
        "prepare_workflow_submission",
        AsyncMock(return_value=submission),
    )

    try:
        with pytest.raises(admission.WorkflowSubmissionRejectedBeforeQueue):
            await run_service.run_workflow({"workflowId": "wf-1", "inputs": {}})
    finally:
        admission.set_workflow_admission_provider(previous)

    assert events == ["acquire", "provider_submit", "release"]
    assert lease.outcomes[0].prompt_id is None
    assert lease.outcomes[0].status == "submission_rejected"


async def test_ambiguous_submission_failure_retains_admission(monkeypatch):
    from modules.workflow_runner.services import admission, run_service
    from modules.workflow_runner.services.executor import WorkflowPreparationError

    events: list[str] = []
    queue_error = WorkflowPreparationError({"detail": "connection reset"}, 502)
    lease = RecordingLease(events, submit_error=queue_error)
    provider = RecordingProvider(events, lease)
    previous = admission.set_workflow_admission_provider(provider)
    submission = make_submission()

    monkeypatch.setattr(
        run_service,
        "_prepare_workflow_execution",
        lambda payload: (SimpleNamespace(), submission.prompt),
    )
    monkeypatch.setattr(
        run_service,
        "prepare_workflow_submission",
        AsyncMock(return_value=submission),
    )

    try:
        with pytest.raises(WorkflowPreparationError):
            await run_service.run_workflow({"workflowId": "wf-1", "inputs": {}})
        retained = admission.get_retained_workflow_admission(submission.client_id)
        assert retained is not None
        assert retained.admission.released is False
        assert events == ["acquire", "provider_submit"]
        await retained.admission.release(
            admission.WorkflowAdmissionOutcome(None, "reconciled")
        )
    finally:
        admission.set_workflow_admission_provider(previous)

    assert events == ["acquire", "provider_submit", "release"]
    assert admission.get_retained_workflow_admission(submission.client_id) is None


async def test_prepare_preserves_ordinary_extra_data_but_seals_lf_provenance(
    monkeypatch,
):
    from modules.workflow_runner.services import executor

    async def validate(*args, **kwargs):
        return True, "", ("save",), ()

    prompt = {"save": {"class_type": "SaveImage", "inputs": {}}}
    payload = {
        "workflowId": "wf-extra",
        "clientId": "client-extra",
        "inputs": {},
        "extraData": {
            "trace_id": "abc",
            "custom": {"answer": 42},
            "lf_nodes": {"workflow_id": "caller-controlled"},
        },
    }
    monkeypatch.setattr(
        executor,
        "get_settings",
        lambda: SimpleNamespace(COMFY_BACKEND_URL="http://127.0.0.1:8188"),
    )
    monkeypatch.setattr(executor.execution, "validate_prompt", validate)

    request = await executor.prepare_workflow_submission(
        payload,
        (SimpleNamespace(submission_policy=None), prompt),
        owner_id="owner-extra",
    )

    assert json.loads(request.queue_body_json) == request.queue_body
    assert request.queue_body["extra_data"] == {
        "lf_nodes": {"workflow_id": "wf-extra"},
        "trace_id": "abc",
        "custom": {"answer": 42},
    }
    assert request.owner_id == "owner-extra"
    assert request.client_id != "client-extra"
    assert request.queue_body["client_id"] == request.client_id
    assert request.required_provider_id is None
    assert request.admission_metadata == {}


async def test_prepare_rejects_caller_extra_data_for_guarded_workflow(monkeypatch):
    from modules.workflow_runner.services import executor

    async def validate(*args, **kwargs):
        return True, "", ("save",), ()

    prompt = {"save": {"class_type": "SaveImage", "inputs": {}}}
    payload = {
        "workflowId": "wf-guarded",
        "inputs": {},
        "extraData": {"trace_id": "caller-controlled"},
    }
    monkeypatch.setattr(
        executor,
        "get_settings",
        lambda: SimpleNamespace(COMFY_BACKEND_URL="http://127.0.0.1:8188"),
    )
    monkeypatch.setattr(executor.execution, "validate_prompt", validate)
    definition = SimpleNamespace(
        submission_policy=SimpleNamespace(
            provider_id="velora_guarded_v1",
            expected_vram_mb=18_400,
            max_duration_seconds=90.0,
            required=True,
        )
    )

    with pytest.raises(executor.WorkflowPreparationError) as exc:
        await executor.prepare_workflow_submission(
            payload,
            (definition, prompt),
        )

    assert exc.value.status == 400
    assert (
        exc.value.response_body["payload"]["error"]["message"]
        == "invalid_extra_data"
    )


async def test_prepare_uses_exact_narrow_envelope_for_guarded_workflow(monkeypatch):
    from modules.workflow_runner.services import executor

    async def validate(*args, **kwargs):
        return True, "", ("save",), ()

    prompt = {"save": {"class_type": "SaveImage", "inputs": {}}}
    monkeypatch.setattr(
        executor,
        "get_settings",
        lambda: SimpleNamespace(COMFY_BACKEND_URL="http://127.0.0.1:8188"),
    )
    monkeypatch.setattr(executor.execution, "validate_prompt", validate)
    definition = SimpleNamespace(
        submission_policy=SimpleNamespace(
            provider_id="velora_guarded_v1",
            expected_vram_mb=18_400,
            max_duration_seconds=90,
            required=True,
        )
    )

    request = await executor.prepare_workflow_submission(
        {"workflowId": "wf-guarded", "inputs": {}},
        (definition, prompt),
    )

    assert set(request.queue_body) == {"prompt", "client_id"}
    assert json.loads(request.queue_body_json) == request.queue_body


async def test_unexpected_finalize_error_drains_before_release(monkeypatch):
    from modules.workflow_runner.services import admission, run_service

    events: list[str] = []
    lease = RecordingLease(events)
    admission_handle = admission.AcquiredWorkflowAdmission(lease, make_submission())

    async def fail_finalize(*args, **kwargs):
        events.append("finalize")
        raise RuntimeError("bookkeeping failed")

    async def drain(*args, **kwargs):
        events.append("drain")
        return {"status": {"completed": True}}

    monkeypatch.setattr(run_service, "finalize_workflow", fail_finalize)
    monkeypatch.setattr(run_service, "drain_workflow", drain)
    monkeypatch.setattr(run_service, "set_job_status", AsyncMock())
    monkeypatch.setattr(run_service, "_emit_run_progress", lambda *args, **kwargs: None)

    await run_service._finalize_admitted_workflow(
        prompt_id="prompt-drain",
        client_id="client-1",
        comfy_url="http://127.0.0.1:8188",
        validation=(True, "", (), ()),
        admission=admission_handle,
    )

    assert events == ["finalize", "drain", "release"]
    assert lease.outcomes[0].prompt_id == "prompt-drain"
    assert lease.outcomes[0].status == "failed"


async def test_failed_drain_keeps_admission_discoverably_retained(monkeypatch):
    from modules.workflow_runner.services import admission, run_service

    events: list[str] = []
    submission = make_submission()
    lease = RecordingLease(events)
    admission_handle = admission.AcquiredWorkflowAdmission(lease, submission)

    async def fail_finalize(*args, **kwargs):
        raise RuntimeError("finalizer failed")

    async def fail_drain(*args, **kwargs):
        raise ConnectionError("cannot prove terminal state")

    monkeypatch.setattr(run_service, "finalize_workflow", fail_finalize)
    monkeypatch.setattr(run_service, "drain_workflow", fail_drain)
    monkeypatch.setattr(run_service, "set_job_status", AsyncMock())
    monkeypatch.setattr(run_service, "_emit_run_progress", lambda *args, **kwargs: None)

    await run_service._finalize_admitted_workflow(
        prompt_id="prompt-unproven",
        client_id=submission.client_id,
        comfy_url=submission.comfy_url,
        validation=submission.validation,
        admission=admission_handle,
    )

    retained = admission.get_retained_workflow_admission(submission.client_id)
    assert retained is not None
    assert retained.admission is admission_handle
    assert admission_handle.released is False
    assert events == []

    await admission_handle.release(
        admission.WorkflowAdmissionOutcome("prompt-unproven", "reconciled")
    )
    assert admission.get_retained_workflow_admission(submission.client_id) is None


class _JsonResponse:
    status = 200

    def __init__(self, value):
        self.value = value

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False

    def raise_for_status(self):
        return None

    async def json(self):
        return self.value


class _CompletionSession:
    def __init__(self, histories, queues):
        self.histories = list(histories)
        self.queues = list(queues)
        self.queue_reads = 0

    def get(self, url):
        if "/history/" in url:
            return _JsonResponse(self.histories.pop(0))
        if url.endswith("/queue"):
            self.queue_reads += 1
            return _JsonResponse(self.queues.pop(0))
        raise AssertionError(url)


async def test_completion_requires_terminal_history_and_well_formed_queue_absence(
    monkeypatch,
):
    from modules.workflow_runner.services import executor

    prompt_id = "prompt-proof"
    outputs_only = {
        prompt_id: {
            "status": {},
            "outputs": {"save": {"images": [{"filename": "early.png"}]}},
        }
    }
    terminal = {
        prompt_id: {
            "status": {"status_str": "success", "completed": True},
            "outputs": {"save": {"images": [{"filename": "done.png"}]}},
        }
    }
    session = _CompletionSession(
        [outputs_only, terminal, terminal, terminal],
        [
            {"queue_running": "malformed", "queue_pending": []},
            {"queue_running": [], "queue_pending": [[7, prompt_id, {}]]},
            {"queue_running": [], "queue_pending": []},
        ],
    )

    async def no_sleep(_seconds):
        return None

    monkeypatch.setattr(executor.asyncio, "sleep", no_sleep)
    result = await executor._wait_for_completion(
        prompt_id,
        timeout_seconds=1,
        comfy_url="http://comfy",
        session=session,
    )

    assert result == terminal[prompt_id]
    # outputs-only never queried queue; malformed and still-pending queue states
    # both failed closed before the final authoritative absence proof.
    assert session.queue_reads == 3


class _InterruptResponse:
    status = 200

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False


class _RecordingSession:
    def __init__(self) -> None:
        self.posts = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False

    def post(self, url, **kwargs):
        self.posts.append((url, kwargs))
        return _InterruptResponse()


async def test_timeout_interrupt_is_targeted_and_drained(monkeypatch):
    from modules.workflow_runner.services import executor
    from modules.workflow_runner.services.job_store import JobStatus

    terminal = {
        "status": {"status_str": "error", "completed": True},
        "outputs": {},
    }
    waits = AsyncMock(side_effect=[TimeoutError("budget expired"), terminal])
    session = _RecordingSession()

    async def monitor(prompt_id, stop_event, **kwargs):
        return None

    monkeypatch.setattr(executor, "_wait_for_completion", waits)
    monkeypatch.setattr(executor, "_monitor_until_running", monitor)
    monkeypatch.setattr(executor.aiohttp, "ClientSession", lambda: session)

    status, response, http_status = await executor.finalize_workflow(
        "prompt-target",
        "client-must-not-be-used",
        "http://127.0.0.1:8188",
        (True, "", [], []),
    )

    assert status == JobStatus.FAILED
    assert http_status == 504
    assert response["payload"]["detail"] == "budget expired"
    assert len(session.posts) == 1
    url, kwargs = session.posts[0]
    assert url.endswith("/interrupt")
    assert json.loads(kwargs["data"]) == {"prompt_id": "prompt-target"}
    assert waits.await_count == 2
    assert waits.await_args_list[1].kwargs["timeout_seconds"] is None
