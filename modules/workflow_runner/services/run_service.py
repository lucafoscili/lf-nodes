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
from .job_store import (
    JobStatus,
    create_job,
    get_job,
    set_job_status,
    set_job_status_if_unchanged,
)
from .executor import (
    CANCEL_OUTCOME_NOOP,
    CANCEL_OUTCOME_PENDING,
    CANCEL_OUTCOME_RUNNING,
    CANCEL_OUTCOME_TERMINAL,
    CANCEL_OUTCOME_UNSUPPORTED,
    WorkflowPreparationError,
    _make_run_payload,
    _prepare_workflow_execution,
    cancel_workflow,
    drain_workflow,
    finalize_workflow,
    post_workflow_submission,
    prepare_workflow_submission,
)
from .remix_inputs import (
    UploadRemixReferenceError,
    build_durable_input_snapshot,
    materialize_upload_references,
)
from .lifecycle import (
    SubmissionConflictError,
    SubmissionLifecycleError,
    bind_prompt,
    get_cancel_target,
    get_submission,
    get_submission_persistence_fields,
    record_cancel_requested,
    record_prequeue_failure,
    record_proven_pending_cancellation,
    record_terminal,
    reserve_submission,
)
from ...utils.helpers.comfy import safe_send_sync


LOG = logging.getLogger(__name__)
_WORKER_TASKS: set[asyncio.Future[Any]] = set()
_WORKERS_BY_PROMPT: dict[str, asyncio.Future[Any]] = {}
_PROVEN_PENDING_CANCELLATIONS: set[str] = set()
_CANCELLATIONS_IN_FLIGHT: dict[str, asyncio.Future[Dict[str, Any]]] = {}


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


async def _publish_proven_pending_cancellation(prompt_id: str) -> Dict[str, Any] | None:
    """Idempotently publish terminal state after an exact pending dequeue."""

    job_result = {
        "http_status": 200,
        "body": _make_run_payload(detail="cancelled"),
    }
    job_error: BaseException | None = None
    lifecycle_error: BaseException | None = None
    terminal = None
    try:
        # Correct only the active row observed by this exact pending-dequeue
        # operation, or the reconciler's one synthetic state-loss failure.
        # Compare-and-swap prevents this proof from overwriting a genuine
        # execution terminal that arrived concurrently.
        for _attempt in range(2):
            current_job = await get_job(prompt_id)
            if current_job is None or current_job.status == JobStatus.CANCELLED:
                break
            may_cancel = current_job.status == JobStatus.PENDING or (
                current_job.status == JobStatus.FAILED
                and current_job.error == "execution_state_lost"
            )
            if not may_cancel:
                break
            updated = await set_job_status_if_unchanged(
                prompt_id,
                JobStatus.CANCELLED,
                owner_id=current_job.owner_id,
                expected_status=current_job.status.value,
                seq=current_job.seq,
                updated_at=current_job.updated_at,
                result=job_result,
                clear_error=(
                    current_job.status == JobStatus.FAILED
                    and current_job.error == "execution_state_lost"
                ),
            )
            if updated is not None:
                break
        final_job = await get_job(prompt_id)
        if final_job is not None and (
            final_job.status == JobStatus.PENDING
            or (
                final_job.status == JobStatus.FAILED
                and final_job.error == "execution_state_lost"
            )
        ):
            raise RuntimeError(
                "job store could not publish proven pending cancellation atomically"
            )
    except BaseException as exc:
        job_error = exc

    # These stores are independent. Even if one is temporarily unavailable,
    # publish to the other so a refresh/retry never depends on nonexistent
    # Comfy history to learn this proven terminal outcome.
    try:
        terminal = await record_proven_pending_cancellation(
            prompt_id,
            result=job_result,
        )
    except BaseException as exc:
        lifecycle_error = exc

    if job_error is not None:
        raise job_error
    if lifecycle_error is not None:
        raise lifecycle_error
    return terminal


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
        _WORKERS_BY_PROMPT[prompt_id] = task

        def forget_worker(completed: asyncio.Future[Any]) -> None:
            if _WORKERS_BY_PROMPT.get(prompt_id) is completed:
                _WORKERS_BY_PROMPT.pop(prompt_id, None)

        task.add_done_callback(forget_worker)
        LOG.debug("Scheduled lifecycle worker for prompt %s", prompt_id)
        return True
    except Exception:
        LOG.exception("Failed to schedule lifecycle worker for prompt %s", prompt_id)
        return False


async def _await_worker_inline(
    worker: Coroutine[Any, Any, None],
    prompt_id: str,
) -> None:
    """Expose a scheduler-fallback worker to exact pending cancellation."""

    try:
        current = asyncio.current_task()
    except RuntimeError:
        current = None
    if current is not None:
        _WORKERS_BY_PROMPT[prompt_id] = current
    try:
        await worker
    finally:
        if current is not None and _WORKERS_BY_PROMPT.get(prompt_id) is current:
            _WORKERS_BY_PROMPT.pop(prompt_id, None)


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
        # A recorded cancellation request proves caller intent, while the
        # final status still comes from exact Core cancellation proof or exact
        # terminal history. Preserve a genuine failure/success race.
        outcome = WorkflowAdmissionOutcome(prompt_id, final_status.value)
        job_result = {"http_status": http_status, "body": response_body}
        if persist_job:
            current_job = await get_job(prompt_id)
            if current_job is None or current_job.status != final_status:
                await set_job_status(prompt_id, final_status, result=job_result)
        await record_terminal(
            prompt_id,
            final_status.value,
            result=job_result,
        )
        _emit_run_progress(
            prompt_id,
            "workflow_cancelled"
            if final_status == JobStatus.CANCELLED
            else "workflow_completed",
            status=final_status.value,
        )
    except asyncio.CancelledError as exc:
        if prompt_id in _PROVEN_PENDING_CANCELLATIONS:
            # The exact Core/fallback operation already proved this pending
            # prompt was dequeued and published its cancelled job/lifecycle
            # state. Cancellation only wakes this supervisor so it can release
            # admission authority; no history entry exists for a dequeue.
            terminal_proven = True
            outcome = WorkflowAdmissionOutcome(prompt_id, JobStatus.CANCELLED.value)
            try:
                # The endpoint normally publishes first, but the exact dequeue
                # is already terminal authority. Retry both stores here so a
                # transient publish failure cannot leave a forever-active run
                # with no Comfy history available for later reconciliation.
                await _publish_proven_pending_cancellation(prompt_id)
            except BaseException:
                LOG.exception(
                    "Failed to republish proven pending cancellation for %s",
                    prompt_id,
                )
            _emit_run_progress(
                prompt_id,
                "workflow_cancelled",
                status=JobStatus.CANCELLED.value,
            )
            return
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
        _PROVEN_PENDING_CANCELLATIONS.discard(prompt_id)
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
        try:
            effective_payload = await materialize_upload_references(payload, owner_id)
        except UploadRemixReferenceError as exc:
            response = _make_run_payload(
                detail=str(exc),
                error_message=exc.error_code,
                error_input=exc.input_name,
            )
            raise WorkflowPreparationError(response, 400) from exc
        prepared = _prepare_workflow_execution(effective_payload)
        submission = await prepare_workflow_submission(
            effective_payload,
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
            await _await_worker_inline(worker, prompt_id)
        raise

    LOG.info("Received prompt_id %s from ComfyUI for workflow %s", prompt_id, workflow_id)

    try:
        create_job_kwargs = {"owner_id": owner_id}
        submission_identity = await get_submission_persistence_fields(submission_id)
        if submission_identity is None:
            raise SubmissionLifecycleError(
                "submission_identity_unavailable",
                "submission identity could not be persisted",
            )
        create_job_kwargs.update(submission_identity)
        # Keep the call compatible with lightweight third-party/job-store
        # adapters that predate durable input snapshots.
        if "inputs" in effective_payload:
            create_job_kwargs["inputs"] = build_durable_input_snapshot(
                payload,
                effective_payload,
            )
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
            await _await_worker_inline(worker, prompt_id)
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
        await _await_worker_inline(worker, prompt_id)

    lifecycle_snapshot = await get_submission(submission_id, include_events=False)
    if lifecycle_snapshot is None or not caller_supplied_submission_id:
        return {"run_id": prompt_id}
    return _submission_response(lifecycle_snapshot, replayed=False)


async def _cancel_workflow_submission(submission_id: str) -> Dict[str, Any]:
    """Cancel one owner-checked stable submission without global side effects."""

    target = await get_cancel_target(submission_id)
    if target is None:
        raise WorkflowCancellationError(
            "submission_not_found",
            "unknown submission",
            404,
        )
    if target.get("status") in {"succeeded", "failed", "cancelled", "timeout"}:
        snapshot = await get_submission(submission_id, include_events=False)
        assert snapshot is not None
        return snapshot
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
    if job is None or job.status not in {JobStatus.PENDING, JobStatus.RUNNING}:
        raise WorkflowCancellationError(
            "submission_not_cancellable",
            "submission is not pending or running",
            409,
        )

    try:
        outcome = await cancel_workflow(prompt_id, comfy_url=comfy_url)
    except Exception as exc:
        raise WorkflowCancellationError(
            "cancel_transport_failed",
            str(exc) or "targeted interrupt failed",
            502,
        ) from exc
    if outcome == CANCEL_OUTCOME_UNSUPPORTED:
        raise WorkflowCancellationError(
            "exact_cancel_unavailable",
            "this ComfyUI backend cannot guarantee exact cancellation for the running job",
            501,
        )
    if outcome == CANCEL_OUTCOME_NOOP:
        raise WorkflowCancellationError(
            "cancel_rejected",
            "ComfyUI did not cancel the exact job",
            409,
        )
    if outcome == CANCEL_OUTCOME_TERMINAL:
        # The exact Core endpoint is idempotent and can report that this prompt
        # reached history immediately before cancellation. Do not manufacture
        # cancellation intent or relabel the history-backed terminal result;
        # the supervisor/status reconciler will publish its actual outcome.
        snapshot = await get_submission(submission_id, include_events=False)
        assert snapshot is not None
        return snapshot

    if outcome == CANCEL_OUTCOME_PENDING:
        # Core has irreversibly dequeued this exact pending prompt, so establish
        # the proof before any fallible persistence write. The supervisor must
        # be woken even if publishing the cancelled state raises; otherwise it
        # would wait forever for history Comfy will never create.
        _PROVEN_PENDING_CANCELLATIONS.add(prompt_id)
        worker = _WORKERS_BY_PROMPT.get(prompt_id)
        try:
            terminal = await _publish_proven_pending_cancellation(prompt_id)
            if terminal is not None:
                return terminal
            snapshot = await get_submission(submission_id, include_events=False)
            if snapshot is None:
                raise SubmissionLifecycleError(
                    "submission_not_found",
                    "submission disappeared while publishing cancellation",
                )
            return snapshot
        finally:
            if worker is not None and not worker.done():
                worker.cancel()
            else:
                _PROVEN_PENDING_CANCELLATIONS.discard(prompt_id)

    try:
        snapshot = await record_cancel_requested(submission_id)
    except SubmissionConflictError:
        snapshot = await get_submission(submission_id, include_events=False)
        if snapshot is None:
            raise
        return snapshot

    if outcome != CANCEL_OUTCOME_RUNNING:
        raise WorkflowCancellationError(
            "cancel_rejected",
            "ComfyUI returned an unknown cancellation outcome",
            502,
        )
    return snapshot


async def cancel_workflow_submission(submission_id: str) -> Dict[str, Any]:
    """Coalesce concurrent cancellation requests for one stable submission."""

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # The production aiohttp service is asyncio-based. Keeping the pure
        # coroutine path also supports alternate test/embedding runtimes that
        # do not expose an asyncio task loop.
        return await _cancel_workflow_submission(submission_id)

    existing = _CANCELLATIONS_IN_FLIGHT.get(submission_id)
    if existing is None:
        task = loop.create_task(_cancel_workflow_submission(submission_id))
        _CANCELLATIONS_IN_FLIGHT[submission_id] = task

        def forget(completed: asyncio.Future[Dict[str, Any]]) -> None:
            if _CANCELLATIONS_IN_FLIGHT.get(submission_id) is completed:
                _CANCELLATIONS_IN_FLIGHT.pop(submission_id, None)

        task.add_done_callback(forget)
        existing = task

    # A disconnected duplicate HTTP request must not cancel the shared exact
    # Core operation on behalf of every other waiter.
    return await asyncio.shield(existing)


# endregion


__all__ = [
    "SubmissionConflictError",
    "SubmissionLifecycleError",
    "WorkflowCancellationError",
    "cancel_workflow_submission",
    "run_workflow",
]
