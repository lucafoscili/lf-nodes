import asyncio
import time
import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional

class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class Job:
    id: str
    created_at: float = field(default_factory=time.time)
    status: JobStatus = JobStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None

_jobs: Dict[str, Job] = {}
_lock = asyncio.Lock()

# Job TTL and pruner configuration
_JOB_TTL_SECONDS = int(os.environ.get("JOB_TTL_SECONDS", "300"))
_JOB_PRUNE_INTERVAL = int(os.environ.get("JOB_PRUNE_INTERVAL_SECONDS", "60"))


async def _job_pruner() -> None:
    """Background task: remove terminal jobs older than _JOB_TTL_SECONDS."""
    try:
        while True:
            try:
                now = time.time()
                to_remove = []
                async with _lock:
                    for jid, job in list(_jobs.items()):
                        if job.status in {JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED}:
                            if (job.created_at + _JOB_TTL_SECONDS) <= now:
                                to_remove.append(jid)
                    for jid in to_remove:
                        _jobs.pop(jid, None)
                if to_remove:
                    logging.debug("Job pruner removed %d jobs", len(to_remove))
            except Exception:
                logging.exception("Error during job prune")
            await asyncio.sleep(_JOB_PRUNE_INTERVAL)
    except asyncio.CancelledError:
        logging.debug("Job pruner cancelled")


async def _start_job_pruner(app) -> None:
    try:
        if app.get("_job_pruner_task"):
            return
    except Exception:
        pass
    task = asyncio.create_task(_job_pruner())
    app["_job_pruner_task"] = task
    logging.info("Started job pruner task (ttl=%s seconds, interval=%s seconds)", _JOB_TTL_SECONDS, _JOB_PRUNE_INTERVAL)


async def _stop_job_pruner(app) -> None:
    task = app.pop("_job_pruner_task", None)
    if task is not None:
        task.cancel()
        try:
            await task
        except Exception:
            pass
        logging.info("Stopped job pruner task")

async def create_job(job_id: str) -> Job:
    async with _lock:
        job = Job(id=job_id)
        _jobs[job_id] = job
        return job

async def get_job(job_id: str) -> Optional[Job]:
    async with _lock:
        return _jobs.get(job_id)

async def set_job_status(
    job_id: str,
    status: JobStatus,
    *,
    result: Optional[Any] = None,
    error: Optional[str] = None,
) -> Optional[Job]:
    async with _lock:
        job = _jobs.get(job_id)
        if job is None:
            return None

        job.status = status
        if result is not None:
            job.result = result
        if error is not None:
            job.error = error
        return job

async def list_jobs() -> Dict[str, Job]:
    async with _lock:
        return dict(_jobs)

async def remove_job(job_id: str) -> Optional[Job]:
    async with _lock:
        return _jobs.pop(job_id, None)

__all__ = [
    "Job",
    "JobStatus",
    "create_job",
    "get_job",
    "list_jobs",
    "remove_job",
    "set_job_status",
]

# Register with PromptServer app lifecycle if available so the pruner runs automatically.
try:
    from server import PromptServer
    app = PromptServer.instance.app
    app.on_startup.append(_start_job_pruner)
    app.on_cleanup.append(_stop_job_pruner)
except Exception:
    logging.debug("PromptServer not available for job pruner registration at import time")
