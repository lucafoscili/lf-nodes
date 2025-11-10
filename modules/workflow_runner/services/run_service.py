import asyncio
import logging

from typing import Any, Dict

from server import PromptServer

LOG = logging.getLogger(__name__)

from .job_store import JobStatus, create_job, set_job_status
from .executor import (
    submit_workflow,
    finalize_workflow,
    _make_run_payload,
    _prepare_workflow_execution,
    WorkflowPreparationError,
)
from ...utils.helpers.comfy import safe_send_sync

# region Helpers
def _emit_run_progress(prompt_id: str, message: str, **extra: Any) -> None:
    """Emit progress event for a workflow run.
    
    Args:
        prompt_id: ComfyUI's prompt_id (now our canonical run identifier)
        message: Progress message
        **extra: Additional fields to include in the payload
    """
    payload = {"run_id": prompt_id, "message": message}  # Keep "run_id" field name for compatibility
    if extra:
        payload.update(extra)
    try:
        safe_send_sync("lf-runner:progress", payload, prompt_id)
    except Exception:
        logging.exception("Failed to send progress event for prompt %s", prompt_id)
# endregion

# region Run Workflow
async def run_workflow(payload: Dict[str, Any], owner_id: str | None = None, is_api_call: bool = False) -> Dict[str, Any]:
    """Orchestrate running a workflow payload.

    Now returns the prompt_id from ComfyUI as the run identifier.
    This function submits the workflow to ComfyUI, gets the prompt_id,
    creates a job with that ID, and schedules background processing.
    
    Returns:
        dict: {"run_id": prompt_id} where prompt_id is ComfyUI's execution ID
    """
    from .job_store import _WF_DEBUG
    
    try:
        prepared = _prepare_workflow_execution(payload)
    except WorkflowPreparationError as exc:
        raise

    workflow_id = payload.get("workflowId")
    
    if _WF_DEBUG:
        LOG.debug(f"[DEBUG] run_workflow: owner_id={owner_id}, workflow_id={workflow_id}")
    
    try:
        prompt_id, client_id, comfy_url, prompt, validation, _ = await submit_workflow(payload, prepared)
    except WorkflowPreparationError as exc:
        raise

    LOG.info("Received prompt_id %s from ComfyUI for workflow %s", prompt_id, workflow_id)

    if is_api_call:
        LOG.debug("API call detected - skipping job registration and background processing")
        return {"run_id": prompt_id}

    await create_job(prompt_id, workflow_id, owner_id=owner_id)
    LOG.debug("Created job %s and published pending event", prompt_id)
    _emit_run_progress(prompt_id, "workflow_received")

    worker_scheduled = False
    try:
        loop = getattr(getattr(PromptServer, "instance", None), "loop", None)
        if loop is not None:
            async def worker() -> None:
                try:
                    final_status, response_body, http_status = await finalize_workflow(
                        prompt_id, client_id, comfy_url, validation
                    )
                    job_result = {"http_status": http_status, "body": response_body}
                    await set_job_status(prompt_id, final_status, result=job_result)
                    _emit_run_progress(prompt_id, "workflow_completed", status=final_status.value)
                except asyncio.CancelledError:
                    await set_job_status(prompt_id, JobStatus.CANCELLED, error="cancelled")
                    _emit_run_progress(prompt_id, "workflow_cancelled")
                    raise
                except WorkflowPreparationError as exc:
                    # Shouldn't happen here, but convert to FAILED
                    LOG.exception("Finalize failed for %s with prep error: %s", prompt_id, exc)
                    job_result = {"http_status": exc.status, "body": exc.response_body}
                    await set_job_status(prompt_id, JobStatus.FAILED, error="prep_failed", result=job_result)
                    _emit_run_progress(prompt_id, "workflow_failed", error="prep_failed")
                except Exception as exc:
                    LOG.exception("Workflow prompt %s failed unexpectedly: %s", prompt_id, exc)
                    error_payload = _make_run_payload(detail=str(exc), error_message="unhandled_exception")
                    job_result = {"http_status": 500, "body": error_payload}
                    await set_job_status(prompt_id, JobStatus.FAILED, error=str(exc), result=job_result)
                    _emit_run_progress(prompt_id, "workflow_failed", error=str(exc))
            
            loop.create_task(worker())
            worker_scheduled = True
            LOG.debug("Scheduled worker coroutine on PromptServer loop for prompt %s", prompt_id)
        else:
            running_loop = asyncio.get_running_loop()
            
            async def worker() -> None:
                try:
                    final_status, response_body, http_status = await finalize_workflow(
                        prompt_id, client_id, comfy_url, validation
                    )
                    job_result = {"http_status": http_status, "body": response_body}
                    await set_job_status(prompt_id, final_status, result=job_result)
                    _emit_run_progress(prompt_id, "workflow_completed", status=final_status.value)
                except asyncio.CancelledError:
                    await set_job_status(prompt_id, JobStatus.CANCELLED, error="cancelled")
                    _emit_run_progress(prompt_id, "workflow_cancelled")
                    raise
                except WorkflowPreparationError as exc:
                    # Shouldn't happen here, but convert to FAILED
                    logging.exception("Finalize failed for %s with prep error: %s", prompt_id, exc)
                    job_result = {"http_status": exc.status, "body": exc.response_body}
                    await set_job_status(prompt_id, JobStatus.FAILED, error="prep_failed", result=job_result)
                    _emit_run_progress(prompt_id, "workflow_failed", error="prep_failed")
                except Exception as exc:
                    logging.exception("Workflow prompt %s failed unexpectedly: %s", prompt_id, exc)
                    error_payload = _make_run_payload(detail=str(exc), error_message="unhandled_exception")
                    job_result = {"http_status": 500, "body": error_payload}
                    await set_job_status(prompt_id, JobStatus.FAILED, error=str(exc), result=job_result)
                    _emit_run_progress(prompt_id, "workflow_failed", error=str(exc))
            
            running_loop.create_task(worker())
            worker_scheduled = True
            LOG.debug("Scheduled worker coroutine on running asyncio loop for prompt %s", prompt_id)
    except RuntimeError:
        LOG.warning("No running asyncio loop; skipping background worker scheduling for prompt %s (test/CLI context)", prompt_id)
    except Exception:
        LOG.exception("Unexpected error scheduling background worker for prompt %s; skipping", prompt_id)
    
    # CRITICAL: If background worker failed to schedule, run synchronously to prevent stuck jobs
    if not worker_scheduled:
        LOG.warning("Background worker failed to schedule for prompt %s, falling back to synchronous execution", prompt_id)
        try:
            async def sync_finalize() -> None:
                try:
                    final_status, response_body, http_status = await finalize_workflow(
                        prompt_id, client_id, comfy_url, validation
                    )
                    job_result = {"http_status": http_status, "body": response_body}
                    await set_job_status(prompt_id, final_status, result=job_result)
                    _emit_run_progress(prompt_id, "workflow_completed", status=final_status.value)
                except Exception as exc:
                    LOG.exception("Synchronous finalize failed for %s: %s", prompt_id, exc)
                    error_payload = _make_run_payload(detail=str(exc), error_message="unhandled_exception")
                    job_result = {"http_status": 500, "body": error_payload}
                    await set_job_status(prompt_id, JobStatus.FAILED, error=str(exc), result=job_result)
                    _emit_run_progress(prompt_id, "workflow_failed", error=str(exc))
            
            try:
                asyncio.create_task(sync_finalize())
                LOG.debug("Scheduled synchronous finalization for prompt %s", prompt_id)
            except RuntimeError:
                # Even create_task failed - this is a severe environment issue
                LOG.error("CRITICAL: Cannot schedule workflow finalization for %s - job will remain pending", prompt_id)
                # At minimum, mark as failed with a clear error
                error_payload = _make_run_payload(detail="Background processing unavailable", error_message="background_unavailable")
                job_result = {"http_status": 500, "body": error_payload}
                asyncio.create_task(set_job_status(prompt_id, JobStatus.FAILED, error="background_unavailable", result=job_result))
        except Exception as exc:
            LOG.exception("Failed to schedule synchronous fallback for %s: %s", prompt_id, exc)

    return {"run_id": prompt_id}
# endregion