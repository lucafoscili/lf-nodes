from typing import Any, Dict, Optional

from . import job_store
from .job_store import JobStatus
from .remix_inputs import project_public_remix_inputs

# region Job service functions
async def create_job(run_id: str, workflow_id: str, owner_id: str | None = None) -> None:
    """
    Create a job record for run_id by delegating to the shared job_store.

    `workflow_id` is mandatory and will be forwarded to the underlying job_store.
    """
    await job_store.create_job(run_id, owner_id=owner_id, workflow_id=workflow_id)

async def get_job_status(run_id: str) -> Optional[Dict[str, Any]]:
    """
    Return a job status dict (matching previous API) or None if not found.

    The shape mirrors what `handlers.route_run_status` returned before the
    refactor so the frontend receives the expected fields.
    """
    job = await job_store.get_job(run_id)
    if job is None:
        return None

    is_terminal = job.status in {JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED}
    inputs = project_public_remix_inputs(
        str(job.id),
        str(job.workflow_id),
        getattr(job, "inputs", {}),
    )
    payload = {
        "run_id": job.id,
        "workflow_id": job.workflow_id,
        "status": job.status.value,
        "created_at": job.created_at,
        "error": job.error,
        "result": job.result if is_terminal else None,
        "seq": getattr(job, "seq", 0),
        "owner_id": job.owner_id,
        # Detail/status callers may use this bounded snapshot to replay/remix
        # a run.  List/SSE serializers intentionally do not read this field.
        "inputs": inputs,
        "updated_at": getattr(job, "updated_at", None),
    }
    return payload
# endregion
