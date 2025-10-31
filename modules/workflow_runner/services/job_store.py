import asyncio
import time
import logging
import json

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
_subscribers: list[asyncio.Queue] = []

LOG = logging.getLogger(__name__)

# region create
async def create_job(job_id: str) -> Job:
    async with _lock:
        job = Job(id=job_id)
        _jobs[job_id] = job
        updated = job

    event = {
        "run_id": updated.id,
        "status": updated.status.value,
        "created_at": updated.created_at,
        "error": updated.error,
        "result": updated.result if updated.status in {JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED} else None,
    }
    for q in list(_subscribers):
        try:
            q.put_nowait(event)
        except Exception:
            # If a subscriber's queue is full or closed, best-effort ignore.
            pass

    return updated
# endregion

# region read/update/delete
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
        updated = job

    # Notify subscribers outside of the lock to avoid blocking other callers.
    event = {
        "run_id": updated.id,
        "status": updated.status.value,
        "created_at": updated.created_at,
        "error": updated.error,
        "result": updated.result if updated.status in {JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED} else None,
    }
    for q in list(_subscribers):
        try:
            q.put_nowait(event)
        except Exception:
            # If a subscriber's queue is full or closed, best-effort ignore.
            pass

    return updated

async def list_jobs() -> Dict[str, Job]:
    async with _lock:
        return dict(_jobs)

async def remove_job(job_id: str) -> Optional[Job]:
    async with _lock:
        return _jobs.pop(job_id, None)
# endregion

__all__ = [
    "Job",
    "JobStatus",
    "create_job",
    "get_job",
    "list_jobs",
    "remove_job",
    "set_job_status",
]

# region PubSub for job events
def subscribe_events() -> asyncio.Queue:
    """
    Return a new asyncio.Queue that will receive job event dicts.

    Caller is responsible for consuming and ensuring the queue does not grow
    unbounded. Use `unsubscribe_events` to remove the queue when done.
    """
    q: asyncio.Queue = asyncio.Queue()
    _subscribers.append(q)
    return q

def unsubscribe_events(q: asyncio.Queue) -> None:
    try:
        _subscribers.remove(q)
    except ValueError:
        pass
# endregion


def publish_event(event: Dict[str, Any]) -> None:
    """Publish an arbitrary event dict to all subscribers.

    This is useful for streaming proxy outputs (kobold messages) into the
    same SSE channel used for run updates. The event dict should be JSON
    serializable and include an identifying key (for example, 'type' or
    'run_id').
    """
    # Log a brief summary of the published event for debugging (avoid huge payloads)
    try:
        summary = event if isinstance(event, dict) and len(json.dumps(event)) < 1000 else {k: event.get(k) for k in ("type", "run_id") if isinstance(event, dict) and k in event}
        LOG.info("Publishing event to %d subscribers: %s", len(_subscribers), summary)
    except Exception:
        LOG.exception("Failed creating publish_event summary")

    for q in list(_subscribers):
        try:
            q.put_nowait(event)
        except Exception:
            LOG.exception("Failed to enqueue event to subscriber queue")
