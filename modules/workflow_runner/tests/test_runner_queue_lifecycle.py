"""Queue, drain, completion and cancellation contracts for Workflow Runner."""

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


def make_submission():
    from modules.workflow_runner.services.executor import WorkflowSubmissionRequest

    prompt = {"save": {"class_type": "SaveImage", "inputs": {}}}
    body = {
        "prompt": prompt,
        "client_id": "client-1",
        "extra_data": {"lf_nodes": {"workflow_id": "wf-1"}},
    }
    return WorkflowSubmissionRequest(
        workflow_id="wf-1",
        owner_id=None,
        client_id="client-1",
        comfy_url="http://127.0.0.1:8188",
        prompt=prompt,
        validation=(True, "", ("save",), ()),
        queue_body=body,
        queue_body_json=json.dumps(body),
    )


async def test_ambiguous_submission_failure_is_recorded_as_reconciling(monkeypatch):
    from modules.workflow_runner.services import lifecycle, run_service
    from modules.workflow_runner.services.executor import WorkflowPreparationError

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
    monkeypatch.setattr(
        run_service,
        "post_workflow_submission",
        AsyncMock(
            side_effect=WorkflowPreparationError({"detail": "connection reset"}, 502)
        ),
    )
    payload = {
        "workflowId": "wf-1",
        "submissionId": "example:ambiguous:001",
        "inputs": {},
    }

    with pytest.raises(WorkflowPreparationError):
        await run_service.run_workflow(payload)

    snapshot = await lifecycle.get_submission(
        "example:ambiguous:001",
        include_events=False,
    )
    assert snapshot is not None
    assert snapshot["status"] == "reconciling"


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
        (SimpleNamespace(), prompt),
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


async def test_unexpected_finalize_error_drains_before_recording_failure(monkeypatch):
    from modules.workflow_runner.services import run_service
    from modules.workflow_runner.services.job_store import JobStatus

    events: list[str] = []

    async def fail_finalize(*args, **kwargs):
        events.append("finalize")
        raise RuntimeError("bookkeeping failed")

    async def drain(*args, **kwargs):
        events.append("drain")
        return {"status": {"completed": True}}

    set_status = AsyncMock()
    monkeypatch.setattr(run_service, "finalize_workflow", fail_finalize)
    monkeypatch.setattr(run_service, "drain_workflow", drain)
    monkeypatch.setattr(run_service, "set_job_status", set_status)
    monkeypatch.setattr(run_service, "_emit_run_progress", lambda *args, **kwargs: None)

    await run_service._finalize_queued_workflow(
        prompt_id="prompt-drain",
        client_id="client-1",
        comfy_url="http://127.0.0.1:8188",
        validation=(True, "", (), ()),
    )

    assert events == ["finalize", "drain"]
    assert set_status.await_args.args[:2] == ("prompt-drain", JobStatus.FAILED)


async def test_failed_drain_records_no_terminal_state(monkeypatch):
    from modules.workflow_runner.services import run_service

    async def fail_finalize(*args, **kwargs):
        raise RuntimeError("finalizer failed")

    async def fail_drain(*args, **kwargs):
        raise ConnectionError("cannot prove terminal state")

    set_status = AsyncMock()
    record_terminal = AsyncMock()
    monkeypatch.setattr(run_service, "finalize_workflow", fail_finalize)
    monkeypatch.setattr(run_service, "drain_workflow", fail_drain)
    monkeypatch.setattr(run_service, "set_job_status", set_status)
    monkeypatch.setattr(run_service, "record_terminal", record_terminal)
    monkeypatch.setattr(run_service, "_emit_run_progress", lambda *args, **kwargs: None)

    await run_service._finalize_queued_workflow(
        prompt_id="prompt-unproven",
        client_id="client-1",
        comfy_url="http://127.0.0.1:8188",
        validation=(True, "", (), ()),
    )

    set_status.assert_not_awaited()
    record_terminal.assert_not_awaited()


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


class _CancelResponse:
    def __init__(self, status, body):
        self.status = status
        self.body = body

    async def json(self):
        return self.body

    def raise_for_status(self):
        if self.status >= 400:
            raise RuntimeError(f"HTTP {self.status}")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False


class _CancelSession:
    def __init__(
        self,
        *,
        core_cancelled=None,
        core_status=200,
        queues=None,
        histories=None,
    ):
        self.core_cancelled = core_status == 200 if core_cancelled is None else core_cancelled
        self.core_status = core_status
        self.queues = list(queues or [])
        self.histories = list(histories or [])
        self.posts = []

    def post(self, url, **kwargs):
        self.posts.append((url, kwargs))
        if "/api/jobs/" in url:
            return _CancelResponse(
                self.core_status,
                {"cancelled": self.core_cancelled},
            )
        return _CancelResponse(200, {})

    def get(self, url, **kwargs):
        if "/history/" in url:
            return _CancelResponse(200, self.histories.pop(0))
        if url.endswith("/queue"):
            return _CancelResponse(200, self.queues.pop(0))
        return _CancelResponse(404, {})


async def test_core_cancel_targets_running_job_by_exact_id():
    from modules.workflow_runner.services import executor

    prompt_id = "aaaaaaaa-aaaa-4aaa-aaaa-aaaaaaaaaaaa"
    session = _CancelSession(
        histories=[{}],
        queues=[{"queue_running": [[0, prompt_id]], "queue_pending": []}],
    )

    outcome = await executor.cancel_workflow(
        prompt_id,
        comfy_url="http://comfy:8188",
        session=session,
    )

    assert outcome == executor.CANCEL_OUTCOME_RUNNING
    assert session.posts == [
        (f"http://comfy:8188/api/jobs/{prompt_id}/cancel", {})
    ]


async def test_core_cancel_proves_pending_dequeue_without_history():
    from modules.workflow_runner.services import executor

    prompt_id = "bbbbbbbb-bbbb-4bbb-bbbb-bbbbbbbbbbbb"
    session = _CancelSession(
        histories=[{}, {}],
        queues=[{"queue_running": [], "queue_pending": []}],
    )

    outcome = await executor.cancel_workflow(prompt_id, session=session)

    assert outcome == executor.CANCEL_OUTCOME_PENDING


async def test_core_cancel_preserves_terminal_race_between_history_and_queue():
    from modules.workflow_runner.services import executor

    prompt_id = "ffffffff-ffff-4fff-ffff-ffffffffffff"
    terminal = {prompt_id: {"status": {"status_str": "success"}}}
    session = _CancelSession(
        histories=[{}, terminal],
        queues=[{"queue_running": [], "queue_pending": []}],
    )

    outcome = await executor.cancel_workflow(prompt_id, session=session)

    assert outcome == executor.CANCEL_OUTCOME_TERMINAL


async def test_core_cancel_false_is_idempotent_when_exact_history_is_terminal():
    from modules.workflow_runner.services import executor

    prompt_id = "eeeeeeee-eeee-4eee-eeee-eeeeeeeeeeee"
    session = _CancelSession(
        core_cancelled=False,
        histories=[{prompt_id: {"status": {"status_str": "success"}}}],
    )

    outcome = await executor.cancel_workflow(prompt_id, session=session)

    assert outcome == executor.CANCEL_OUTCOME_TERMINAL
    assert session.posts == [
        (f"http://127.0.0.1:8188/api/jobs/{prompt_id}/cancel", {})
    ]


async def test_core_cancel_false_proves_orphan_after_double_history_absence():
    from modules.workflow_runner.services import executor

    prompt_id = "abababab-abab-4aba-abab-abababababab"
    session = _CancelSession(
        core_cancelled=False,
        histories=[{}, {}],
        queues=[{"queue_running": [], "queue_pending": []}],
    )

    outcome = await executor.cancel_workflow(prompt_id, session=session)

    assert outcome == executor.CANCEL_OUTCOME_ORPHANED


async def test_core_cancel_false_does_not_claim_running_cancel_intent():
    from modules.workflow_runner.services import executor

    prompt_id = "acacacac-acac-4aca-acac-acacacacacac"
    session = _CancelSession(
        core_cancelled=False,
        histories=[{}],
        queues=[{"queue_running": [[0, prompt_id]], "queue_pending": []}],
    )

    outcome = await executor.cancel_workflow(prompt_id, session=session)

    assert outcome == executor.CANCEL_OUTCOME_NOOP


async def test_core_cancel_false_preserves_ambiguous_queue_without_cancel_intent():
    from modules.workflow_runner.services import executor

    prompt_id = "adadadad-adad-4ada-adad-adadadadadad"
    session = _CancelSession(
        core_cancelled=False,
        histories=[{}],
        queues=[{"queue_running": "malformed", "queue_pending": []}],
    )

    outcome = await executor.cancel_workflow(prompt_id, session=session)

    assert outcome == executor.CANCEL_OUTCOME_NOOP


async def test_core_cancel_false_preserves_direct_terminal_history_shape():
    from modules.workflow_runner.services import executor

    prompt_id = "aeaeaeae-aeae-4aea-aeae-aeaeaeaeaeae"
    session = _CancelSession(
        core_cancelled=False,
        histories=[{"status": {"status_str": "success"}, "outputs": {}}],
    )

    outcome = await executor.cancel_workflow(prompt_id, session=session)

    assert outcome == executor.CANCEL_OUTCOME_TERMINAL


async def test_core_cancel_false_does_not_treat_unrelated_history_as_absence():
    from modules.workflow_runner.services import executor

    prompt_id = "afafafaf-afaf-4afa-afaf-afafafafafaf"
    session = _CancelSession(
        core_cancelled=False,
        histories=[{"another-prompt": {"status": {"status_str": "success"}}}],
    )

    outcome = await executor.cancel_workflow(prompt_id, session=session)

    assert outcome == executor.CANCEL_OUTCOME_NOOP
    assert session.queues == []


async def test_core_cancel_false_preserves_ambiguous_second_history_read():
    from modules.workflow_runner.services import executor

    prompt_id = "bcbcbcbc-bcbc-4bcb-bcbc-bcbcbcbcbcbc"
    session = _CancelSession(
        core_cancelled=False,
        histories=[{}, {"another-prompt": {}}],
        queues=[{"queue_running": [], "queue_pending": []}],
    )

    outcome = await executor.cancel_workflow(prompt_id, session=session)

    assert outcome == executor.CANCEL_OUTCOME_NOOP


async def test_legacy_fallback_deletes_only_exact_pending_id():
    from modules.workflow_runner.services import executor

    prompt_id = "cccccccc-cccc-4ccc-cccc-cccccccccccc"
    session = _CancelSession(
        core_status=404,
        histories=[{}, {}],
        queues=[
            {"queue_running": [], "queue_pending": [[0, prompt_id]]},
            {"queue_running": [], "queue_pending": []},
        ],
    )

    outcome = await executor.cancel_workflow(prompt_id, session=session)

    assert outcome == executor.CANCEL_OUTCOME_PENDING
    assert all(not url.endswith("/interrupt") for url, _ in session.posts)
    delete_url, delete_kwargs = session.posts[1]
    assert delete_url.endswith("/queue")
    assert json.loads(delete_kwargs["data"]) == {"delete": [prompt_id]}


async def test_legacy_fallback_refuses_global_risk_for_running_job():
    from modules.workflow_runner.services import executor

    prompt_id = "dddddddd-dddd-4ddd-dddd-dddddddddddd"
    session = _CancelSession(
        core_status=404,
        queues=[{"queue_running": [[0, prompt_id]], "queue_pending": []}],
    )

    outcome = await executor.cancel_workflow(prompt_id, session=session)

    assert outcome == executor.CANCEL_OUTCOME_UNSUPPORTED
    assert all(not url.endswith("/interrupt") for url, _ in session.posts)


async def test_interrupted_history_is_cancelled_not_failed(monkeypatch):
    from modules.workflow_runner.services import executor
    from modules.workflow_runner.services.job_store import JobStatus

    history = {
        "status": {
            "status_str": "error",
            "completed": False,
            "messages": [["execution_interrupted", {"prompt_id": "prompt-cancelled"}]],
        },
        "outputs": {},
    }

    async def monitor(prompt_id, stop_event, **kwargs):
        return None

    monkeypatch.setattr(executor, "_wait_for_completion", AsyncMock(return_value=history))
    monkeypatch.setattr(executor, "_monitor_until_running", monitor)
    monkeypatch.setattr(executor.aiohttp, "ClientSession", lambda: _RecordingSession())

    status, response, http_status = await executor.finalize_workflow(
        "prompt-cancelled",
        "client-1",
        "http://comfy:8188",
        (True, "", [], []),
    )

    assert status == JobStatus.CANCELLED
    assert http_status == 200
    assert response["payload"]["detail"] == "cancelled"


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
