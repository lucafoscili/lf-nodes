import asyncio
import logging
import uuid

from typing import Any, Dict

from server import PromptServer

LOG = logging.getLogger(__name__)

from .job_store import JobStatus, create_job, set_job_status
from .executor import execute_workflow, _make_run_payload, _prepare_workflow_execution, WorkflowPreparationError

# region Helpers
def _emit_run_progress(run_id: str, message: str, **extra: Any) -> None:
    payload = {"run_id": run_id, "message": message}
    if extra:
        payload.update(extra)
    try:
        PromptServer.instance.send_sync("lf-runner:progress", payload)
    except Exception:
        logging.exception("Failed to send progress event for run %s", run_id)
# endregion

# region Run Workflow
async def run_workflow(payload: Dict[str, Any], owner_id: str | None = None) -> Dict[str, Any]:
    """Orchestrate running a workflow payload.

    This function mirrors the behaviour previously implemented inline in
    `handlers.route_run_workflow`: it creates a job, schedules the worker
    coroutine and returns a 202-like response containing the run_id.
    """
    from .job_store import _WF_DEBUG
    
    try:
        prepared = _prepare_workflow_execution(payload)
    except WorkflowPreparationError as exc:
        raise

    run_id = str(uuid.uuid4())
    workflow_id = payload.get("workflowId")
    LOG.info("Creating workflow run %s for workflow %s", run_id, workflow_id)
    
    if _WF_DEBUG:
        LOG.info(f"[DEBUG] run_workflow: owner_id={owner_id}, workflow_id={workflow_id}")
    
    await create_job(run_id, owner_id=owner_id, workflow_id=workflow_id)
    LOG.debug("Created run %s and published pending event", run_id)
    _emit_run_progress(run_id, "workflow_received")

    async def worker() -> None:
        try:
            job_status, response_body, http_status = await execute_workflow(payload, run_id, prepared)
            job_result = {"http_status": http_status, "body": response_body}

            await set_job_status(run_id, job_status, result=job_result)
            _emit_run_progress(run_id, "workflow_completed", status=job_status.value)
        except asyncio.CancelledError:
            await set_job_status(run_id, JobStatus.CANCELLED, error="cancelled")
            _emit_run_progress(run_id, "workflow_cancelled")
            raise
        except Exception as exc:
            logging.exception("Workflow run %s failed unexpectedly: %s", run_id, exc)
            error_payload = _make_run_payload(detail=str(exc), error_message="unhandled_exception")
            job_result = {"http_status": 500, "body": error_payload}
            await set_job_status(run_id, JobStatus.FAILED, error=str(exc), result=job_result)
            _emit_run_progress(run_id, "workflow_failed", error=str(exc))

    try:
        PromptServer.instance.loop.create_task(worker())
        LOG.debug("Scheduled worker coroutine on PromptServer loop for run %s", run_id)
    except Exception:
        LOG.exception("Failed to schedule worker on PromptServer loop for run %s; falling back to asyncio.create_task", run_id)
        asyncio.create_task(worker())

    return {"run_id": run_id}
# endregion