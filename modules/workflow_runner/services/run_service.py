import asyncio
import logging
import uuid

from typing import Any, Dict

from server import PromptServer

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
async def run_workflow(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Orchestrate running a workflow payload.

    This function mirrors the behaviour previously implemented inline in
    `handlers.route_run_workflow`: it creates a job, schedules the worker
    coroutine and returns a 202-like response containing the run_id.
    """
    try:
        prepared = _prepare_workflow_execution(payload)
    except WorkflowPreparationError as exc:
        raise

    run_id = str(uuid.uuid4())
    await create_job(run_id)
    _emit_run_progress(run_id, "workflow_received")

    async def worker() -> None:
        try:
            await set_job_status(run_id, JobStatus.RUNNING)
            _emit_run_progress(run_id, "workflow_started")

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
    except Exception:
        asyncio.create_task(worker())

    return {"run_id": run_id}
# endregion