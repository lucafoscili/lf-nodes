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

# NOTE: job pruner implementation is now in `services/background.py`.
# Background lifecycle is started on-demand when the workflow-runner page is accessed.

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

# NOTE: job pruner registration is deferred and managed by
# `services/background.py` to allow on-demand startup when the workflow-runner
# app is actually used.
