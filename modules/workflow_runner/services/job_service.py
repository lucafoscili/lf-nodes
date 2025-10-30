"""Job lifecycle management helper functions.

This module will wrap the job storage/management functions such as create_job,
set_job_status, get_job etc. For now this is a small stub to allow imports
from controllers while we migrate logic out of handlers.py incrementally.
"""
from typing import Any, Dict, Optional

from .. import job_manager
from ..job_manager import JobStatus


async def create_job(run_id: str) -> None:
    """Create a job record for run_id by delegating to the shared job_manager."""
    await job_manager.create_job(run_id)


async def get_job_status(run_id: str) -> Optional[Dict[str, Any]]:
    """Return a job status dict (matching previous API) or None if not found.

    The shape mirrors what `handlers.route_run_status` returned before the
    refactor so the frontend receives the expected fields.
    """
    job = await job_manager.get_job(run_id)
    if job is None:
        return None

    is_terminal = job.status in {JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED}
    payload = {
        "run_id": job.id,
        "status": job.status.value,
        "created_at": job.created_at,
        "error": job.error,
        "result": job.result if is_terminal else None,
    }
    return payload
