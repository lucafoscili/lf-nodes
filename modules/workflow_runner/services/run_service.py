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
async def run_workflow(payload: Dict[str, Any], owner_id: str | None = None) -> Dict[str, Any]:
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
        LOG.info(f"[DEBUG] run_workflow: owner_id={owner_id}, workflow_id={workflow_id}")
    
    # Submit to ComfyUI to obtain prompt_id first
    try:
        prompt_id, client_id, comfy_url, prompt, validation, _ = await submit_workflow(payload, prepared)
    except WorkflowPreparationError as exc:
        # Bubble up the same error response structure
        raise

    LOG.info("Received prompt_id %s from ComfyUI for workflow %s", prompt_id, workflow_id)

    # Immediately create the pending job so DB shows workflow_id from the start
    await create_job(prompt_id, workflow_id, owner_id=owner_id)
    LOG.debug("Created job %s and published pending event", prompt_id)
    _emit_run_progress(prompt_id, "workflow_received")

    # Background finalize: monitor + wait and set terminal status when done
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

    try:
        PromptServer.instance.loop.create_task(worker())
        LOG.debug("Scheduled worker coroutine on PromptServer loop for prompt %s", prompt_id)
    except Exception:
        LOG.exception("Failed to schedule worker on PromptServer loop for prompt %s; falling back to asyncio.create_task", prompt_id)
        asyncio.create_task(worker())

    return {"run_id": prompt_id}
# endregion