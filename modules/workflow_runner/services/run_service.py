import asyncio
import logging

from typing import Any, Coroutine, Dict

from server import PromptServer

from .admission import (
    AcquiredWorkflowAdmission,
    WorkflowAdmissionOutcome,
    WorkflowSubmissionRejectedBeforeQueue,
    acquire_workflow_admission,
    retain_workflow_admission,
)
from .job_store import JobStatus, create_job, get_job, set_job_status
from .executor import (
    _make_run_payload,
    _prepare_workflow_execution,
    drain_workflow,
    finalize_workflow,
    interrupt_workflow,
    post_workflow_submission,
    prepare_workflow_submission,
)
from .lifecycle import (
    SubmissionConflictError,
    SubmissionLifecycleError,
    bind_prompt,
    get_cancel_target,
    get_submission,
    record_cancel_requested,
    record_prequeue_failure,
    record_terminal,
    reserve_submission,
)
from ...utils.helpers.comfy import safe_send_sync


LOG = logging.getLogger(__name__)
_WORKER_TASKS: set[asyncio.Future[Any]] = set()


class WorkflowCancellationError(RuntimeError):
    def __init__(self, detail: str, message: str, status: int) -> None:
        super().__init__(message)
        self.detail = detail
        self.status = status


# region Helpers
def _emit_run_progress(prompt_id: str, message: str, **extra: Any) -> None:
    """Emit progress for a run whose canonical ID is the ComfyUI prompt ID."""

    payload = {"run_id": prompt_id, "message": message}
    if extra:
        payload.update(extra)
    try:
        safe_send_sync("lf-runner:progress", payload, prompt_id)
    except Exception:
        LOG.exception("Failed to send progress event for prompt %s", prompt_id)


async def _release_admission(
    admission: AcquiredWorkflowAdmission,
    outcome: WorkflowAdmissionOutcome,
) -> None:
    try:
        await admission.release(outcome)
    except BaseException:
        LOG.exception(
            "Workflow admission provider failed to release prompt %s",
            outcome.prompt_id,
        )


def _track_worker(task: Any) -> None:
    if not isinstance(task, asyncio.Future):
        return
    _WORKER_TASKS.add(task)
    task.add_done_callback(_WORKER_TASKS.discard)


def _schedule_worker(worker: Coroutine[Any, Any, None], prompt_id: str) -> bool:
    """Schedule on the server loop when available, otherwise the current loop."""

    try:
        loop = getattr(getattr(PromptServer, "instance", None), "loop", None)
        if loop is None:
            loop = asyncio.get_running_loop()
        task = loop.create_task(worker)
        _track_worker(task)
        LOG.debug("Scheduled lifecycle worker for prompt %s", prompt_id)
        return True
    except Exception:
        LOG.exception("Failed to schedule lifecycle worker for prompt %s", prompt_id)
        return False


def _submission_response(snapshot: Dict[str, Any], *, replayed: bool) -> Dict[str, Any]:
    """Keep the legacy run id while exposing the richer stable lifecycle."""

    return {
        "run_id": snapshot.get("run_id"),
        "submission_id": snapshot.get("submission_id"),
        "status": snapshot.get("status"),
        "idempotent_replay": replayed,
        "links": snapshot.get("links"),
    }


async def _finalize_admitted_workflow(
    *,
    prompt_id: str,
    client_id: str,
    comfy_url: str,
    validation: tuple[Any, ...],
    admission: AcquiredWorkflowAdmission,
    submission_id: str | None = None,
    persist_job: bool = True,
) -> None:
    """Finalize one prompt and release admission only after terminal proof."""

    terminal_proven = False
    outcome = WorkflowAdmissionOutcome(prompt_id, JobStatus.FAILED.value)

    try:
        final_status, response_body, http_status = await finalize_workflow(
            prompt_id,
            client_id,
            comfy_url,
            validation,
        )
        # finalize_workflow returns only after exact terminal history, including
        # its targeted-interrupt timeout drain.
        terminal_proven = True
        # A recorded cancellation request proves caller intent, not that
        # ComfyUI actually interrupted this prompt.  Its legacy /interrupt
        # endpoint can acknowledge a request after the prompt has already
        # failed, so preserve the terminal status proven by exact history.
        outcome = WorkflowAdmissionOutcome(prompt_id, final_status.value)
        job_result = {"http_status": http_status, "body": response_body}
        if persist_job:
            await set_job_status(prompt_id, final_status, result=job_result)
        await record_terminal(
            prompt_id,
            final_status.value,
            result=job_result,
        )
        _emit_run_progress(
            prompt_id,
            "workflow_completed",
            status=final_status.value,
        )
    except asyncio.CancelledError as exc:
        # Cancellation of LF bookkeeping is not proof that ComfyUI stopped.
        # Drain this exact prompt before releasing external admission authority.
        try:
            await drain_workflow(prompt_id, comfy_url=comfy_url)
            terminal_proven = True
        except BaseException:
            LOG.exception(
                "Could not prove terminal state for cancelled prompt %s; "
                "admission will remain held",
                prompt_id,
            )
        outcome = WorkflowAdmissionOutcome(
            prompt_id,
            JobStatus.CANCELLED.value,
            error=str(exc) or "cancelled",
        )
        if terminal_proven and persist_job:
            await set_job_status(prompt_id, JobStatus.CANCELLED, error="cancelled")
        if terminal_proven:
            await record_terminal(prompt_id, JobStatus.CANCELLED.value, error="cancelled")
        _emit_run_progress(prompt_id, "workflow_cancelled")
        raise
    except Exception as exc:
        LOG.exception("Workflow prompt %s failed unexpectedly: %s", prompt_id, exc)
        if not terminal_proven:
            try:
                await drain_workflow(prompt_id, comfy_url=comfy_url)
                terminal_proven = True
            except BaseException:
                LOG.exception(
                    "Could not prove terminal state for failed prompt %s; "
                    "admission will remain held",
                    prompt_id,
                )
        outcome = WorkflowAdmissionOutcome(
            prompt_id,
            JobStatus.FAILED.value,
            error=str(exc),
        )
        if terminal_proven and persist_job:
            error_payload = _make_run_payload(
                detail=str(exc),
                error_message="unhandled_exception",
            )
            job_result = {"http_status": 500, "body": error_payload}
            await set_job_status(
                prompt_id,
                JobStatus.FAILED,
                error=str(exc),
                result=job_result,
            )
        if terminal_proven:
            await record_terminal(
                prompt_id,
                JobStatus.FAILED.value,
                result=job_result if persist_job else None,
                error=str(exc),
            )
        _emit_run_progress(prompt_id, "workflow_failed", error=str(exc))
    finally:
        if terminal_proven:
            await _release_admission(admission, outcome)
        else:
            retain_workflow_admission(
                admission,
                outcome.error or "exact terminal state was not proven",
            )
            LOG.critical(
                "Admission retained for prompt %s because terminal state was not proven",
                prompt_id,
            )


async def _finalize_after_registration_failure(
    *,
    prompt_id: str,
    client_id: str,
    comfy_url: str,
    validation: tuple[Any, ...],
    admission: AcquiredWorkflowAdmission,
    submission_id: str | None = None,
) -> None:
    await _finalize_admitted_workflow(
        prompt_id=prompt_id,
        client_id=client_id,
        comfy_url=comfy_url,
        validation=validation,
        admission=admission,
        submission_id=submission_id,
        persist_job=False,
    )


# endregion


# region Run Workflow
async def run_workflow(
    payload: Dict[str, Any],
    owner_id: str | None = None,
    is_api_call: bool = False,
) -> Dict[str, Any]:
    """Admit, queue, register, and supervise one workflow execution.

    Browser and headless callers intentionally share this exact lifecycle.  The
    ``is_api_call`` parameter remains for API compatibility but no longer skips
    job registration or terminal supervision.
    """

    from .job_store import _WF_DEBUG

    workflow_id = payload.get("workflowId")
    caller_supplied_submission_id = (
        payload.get("submissionId") is not None
        or payload.get("submission_id") is not None
    )
    lifecycle_snapshot, created = await reserve_submission(
        payload,
        str(workflow_id or ""),
        owner_id=owner_id,
    )
    submission_id = str(lifecycle_snapshot["submission_id"])
    if not created:
        return _submission_response(lifecycle_snapshot, replayed=True)
    if _WF_DEBUG:
        LOG.debug(
            "run_workflow: owner_id=%s workflow_id=%s headless=%s",
            owner_id,
            workflow_id,
            is_api_call,
        )

    try:
        # Stable-id replays are resolved before preparation.  Preparation can
        # load project-owned code and inspect mutable workflow/model state; a
        # retry must return its stored snapshot even when that state changed.
        prepared = _prepare_workflow_execution(payload)
        submission = await prepare_workflow_submission(
            payload,
            prepared,
            owner_id=owner_id,
        )
        admission = await acquire_workflow_admission(submission)
    except BaseException as exc:
        await record_prequeue_failure(submission_id, str(exc) or type(exc).__name__)
        raise

    try:
        prompt_context = await admission.submit(post_workflow_submission)
    except WorkflowSubmissionRejectedBeforeQueue as exc:
        await record_prequeue_failure(submission_id, str(exc) or type(exc).__name__)
        await _release_admission(
            admission,
            WorkflowAdmissionOutcome(
                None,
                "submission_rejected",
                error=str(exc) or type(exc).__name__,
            ),
        )
        raise
    except BaseException as exc:
        # A timeout, disconnect, malformed success response, or provider error
        # can occur after ComfyUI accepted a prompt.  With no canonical
        # prompt_id LF cannot safely drain it, so preserve the lease for the
        # admission provider to reconcile instead of guessing and releasing.
        retain_workflow_admission(
            admission,
            exc,
        )
        await record_prequeue_failure(
            submission_id,
            str(exc) or type(exc).__name__,
            ambiguous=True,
        )
        LOG.critical(
            "Admission retained for client %s after ambiguous submission failure",
            submission.client_id,
            exc_info=True,
        )
        raise

    prompt_id = prompt_context.prompt_id
    client_id = prompt_context.client_id
    comfy_url = prompt_context.comfy_url
    validation = prompt_context.validation

    try:
        await bind_prompt(submission_id, prompt_id, comfy_url)
    except BaseException:
        # Submission has already crossed the queue boundary.  Even if LF's
        # process-local lifecycle index cannot bind it, supervise the exact
        # prompt through terminal history before releasing admission.
        worker = _finalize_after_registration_failure(
            prompt_id=prompt_id,
            client_id=client_id,
            comfy_url=comfy_url,
            validation=validation,
            admission=admission,
        )
        if not _schedule_worker(worker, prompt_id):
            await worker
        raise

    LOG.info("Received prompt_id %s from ComfyUI for workflow %s", prompt_id, workflow_id)

    try:
        create_job_kwargs = {"owner_id": owner_id}
        # Keep the call compatible with lightweight third-party/job-store
        # adapters that predate durable input snapshots.
        if "inputs" in payload:
            create_job_kwargs["inputs"] = payload.get("inputs")
        await create_job(prompt_id, workflow_id, **create_job_kwargs)
    except BaseException:
        # The prompt is already queued.  Even if LF cannot persist its job, keep
        # supervising the exact prompt so admission is not released early.
        worker = _finalize_after_registration_failure(
            prompt_id=prompt_id,
            client_id=client_id,
            comfy_url=comfy_url,
            validation=validation,
            admission=admission,
            submission_id=submission_id,
        )
        if not _schedule_worker(worker, prompt_id):
            await worker
        raise

    LOG.debug("Created job %s and published pending event", prompt_id)
    _emit_run_progress(prompt_id, "workflow_received")

    worker = _finalize_admitted_workflow(
        prompt_id=prompt_id,
        client_id=client_id,
        comfy_url=comfy_url,
        validation=validation,
        admission=admission,
        submission_id=submission_id,
    )
    if not _schedule_worker(worker, prompt_id):
        # A scheduler failure must not strand the prompt or release its lease.
        # The HTTP request may block, but lifecycle integrity wins here.
        await worker

    lifecycle_snapshot = await get_submission(submission_id, include_events=False)
    if lifecycle_snapshot is None or not caller_supplied_submission_id:
        return {"run_id": prompt_id}
    return _submission_response(lifecycle_snapshot, replayed=False)


async def cancel_workflow_submission(submission_id: str) -> Dict[str, Any]:
    """Target cancellation at one proven-running ComfyUI prompt.

    Pending prompts are intentionally rejected for now: ComfyUI's interrupt API
    is authoritative for a running prompt, while deleting a queued prompt does
    not always produce terminal history for LF's lifecycle worker to reconcile.
    """

    target = await get_cancel_target(submission_id)
    if target is None:
        raise WorkflowCancellationError(
            "submission_not_found",
            "unknown submission",
            404,
        )
    if target.get("status") in {"succeeded", "failed", "cancelled"}:
        raise WorkflowCancellationError(
            "submission_already_terminal",
            "terminal submissions cannot be cancelled",
            409,
        )
    if target.get("cancel_requested") is True:
        snapshot = await get_submission(submission_id, include_events=False)
        assert snapshot is not None
        return snapshot

    prompt_id = target.get("run_id")
    comfy_url = target.get("comfy_url")
    if not isinstance(prompt_id, str) or not prompt_id or not isinstance(comfy_url, str):
        raise WorkflowCancellationError(
            "submission_not_running",
            "submission has not reached a cancellable ComfyUI prompt",
            409,
        )

    job = await get_job(prompt_id)
    if job is None or job.status != JobStatus.RUNNING:
        raise WorkflowCancellationError(
            "submission_not_running",
            "targeted cancellation is available once the prompt is running",
            409,
        )

    try:
        accepted = await interrupt_workflow(prompt_id, comfy_url=comfy_url)
    except Exception as exc:
        raise WorkflowCancellationError(
            "cancel_transport_failed",
            str(exc) or "targeted interrupt failed",
            502,
        ) from exc
    if not accepted:
        raise WorkflowCancellationError(
            "cancel_rejected",
            "ComfyUI rejected the targeted interrupt",
            502,
        )
    return await record_cancel_requested(submission_id)


# endregion


__all__ = [
    "SubmissionConflictError",
    "SubmissionLifecycleError",
    "WorkflowCancellationError",
    "cancel_workflow_submission",
    "run_workflow",
]
