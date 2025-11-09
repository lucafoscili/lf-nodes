import asyncio
import logging
import time

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional

from ..config import get_settings

#region Definitions
_settings = get_settings()
_WF_DEBUG = bool(_settings.WORKFLOW_RUNNER_DEBUG)

class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class Job:
    id: str
    workflow_id: str
    created_at: float = field(default_factory=time.time)
    status: JobStatus = JobStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    owner_id: Optional[str] = None
    # seq for event reconciliation; in-memory storage maintains this for parity with sqlite
    seq: int = 0
    # updated_at tracks last status/result change; defaults to created_at
    updated_at: Optional[float] = None

_jobs: Dict[str, Job] = {}
_lock = asyncio.Lock()
_subscribers: list[asyncio.Queue] = []

_settings = get_settings()
_USE_PERSISTENCE = getattr(_settings, "WORKFLOW_RUNNER_USE_PERSISTENCE", False)
_adapter = None

async def _get_adapter():
    global _adapter
    if _adapter is not None:
        return _adapter
    try:
        from . import job_store_sqlite as _job_store_sqlite
        try:
            db_path = getattr(_settings, "WORKFLOW_RUNNER_DB_PATH", "") or None
            _job_store_sqlite.configure(db_path)
        except Exception:
            LOG.debug("Failed to configure sqlite adapter with provided DB path; adapter will choose default")
        _adapter = _job_store_sqlite
    except Exception:
        _adapter = None
    return _adapter

LOG = logging.getLogger(__name__)
#endregion

# region create
async def create_job(job_id: str, workflow_id: str, owner_id: Optional[str] = None) -> Job:
    """Create a new job with the given ID (ComfyUI's prompt_id).
    
    Args:
        job_id: ComfyUI's prompt_id for this execution
        workflow_id: The workflow definition identifier
        owner_id: Optional owner/user identifier
    """
    if _WF_DEBUG:
        LOG.info(f"[DEBUG] create_job called: job_id={job_id}, workflow_id={workflow_id}, owner_id={owner_id}")
    
    if _USE_PERSISTENCE:
        adapter = await _get_adapter()
        if adapter is not None:
            if _WF_DEBUG:
                LOG.info(f"[DEBUG] create_job: calling adapter.create_job with workflow_id={workflow_id}, owner_id={owner_id}")
            rec = await adapter.create_job(job_id, workflow_id=workflow_id, owner_id=owner_id)
            # Normalize adapter record to in-memory Job dataclass for API consistency
            def _coerce_status(val: Any) -> JobStatus:
                try:
                    if isinstance(val, JobStatus):
                        return val
                    if isinstance(val, str) and val:
                        try:
                            return JobStatus(val)
                        except Exception:
                            return JobStatus.PENDING
                    return JobStatus.PENDING
                except Exception:
                    return JobStatus.PENDING

            try:
                status_val = getattr(rec, "status", JobStatus.PENDING.value)
                job = Job(
                    id=getattr(rec, "run_id"),
                    workflow_id=str(getattr(rec, "workflow_id", "")),
                    created_at=getattr(rec, "created_at", time.time()),
                    status=_coerce_status(status_val),
                    result=getattr(rec, "result", None),
                    error=getattr(rec, "error", None),
                    owner_id=getattr(rec, "owner_id", None),
                    seq=getattr(rec, "seq", 0),
                    updated_at=getattr(rec, "updated_at", None),
                )
            except Exception:
                # Fallback if adapter returns a dict-like or Mock
                status_val = getattr(rec, "status", JobStatus.PENDING.value)
                job = Job(
                    id=getattr(rec, "run_id", getattr(rec, "id", str(job_id))),
                    workflow_id=str(getattr(rec, "workflow_id", workflow_id)),
                    created_at=getattr(rec, "created_at", time.time()),
                    status=_coerce_status(status_val),
                    result=getattr(rec, "result", None),
                    error=getattr(rec, "error", None),
                    owner_id=getattr(rec, "owner_id", owner_id),
                    seq=getattr(rec, "seq", 0),
                    updated_at=getattr(rec, "updated_at", None),
                )
            return job

    async with _lock:
        job = Job(id=job_id, workflow_id=workflow_id, owner_id=owner_id, seq=0)
        _jobs[job_id] = job
        updated = job

    from ..utils.serialize import serialize_job as _serialize_job
    event = _serialize_job(updated)
    for q in list(_subscribers):
        try:
            q.put_nowait(event)
        except Exception:
            pass

    return updated
# endregion

# region read/update/delete
async def get_job(job_id: str) -> Optional[Job]:
    if _USE_PERSISTENCE:
        adapter = await _get_adapter()
        if adapter is not None:
            rec = await adapter.get_job(job_id)
            if rec is None:
                return None
            # convert to in-memory Job dataclass for compatibility
            job = Job(
                id=rec.run_id,
                workflow_id=str(getattr(rec, "workflow_id", "")),
                created_at=rec.created_at,
                status=JobStatus(rec.status),
                result=rec.result,
                error=rec.error,
                owner_id=getattr(rec, "owner_id", None),
                seq=getattr(rec, "seq", 0),
                updated_at=getattr(rec, "updated_at", rec.created_at),
            )
            return job
    async with _lock:
        return _jobs.get(job_id)

async def set_job_status(
    job_id: str,
    status: JobStatus,
    *,
    result: Optional[Any] = None,
    error: Optional[str] = None,
) -> Optional[Job]:
    if _USE_PERSISTENCE:
        adapter = await _get_adapter()
        if adapter is not None:
            rec = await adapter.set_job_status(job_id, status.value if isinstance(status, JobStatus) else str(status), result=result, error=error)
            if rec is None:
                return None
            job = Job(
                id=rec.run_id,
                workflow_id=str(getattr(rec, "workflow_id", "")),
                created_at=rec.created_at,
                status=JobStatus(rec.status),
                result=rec.result,
                error=rec.error,
                owner_id=getattr(rec, "owner_id", None),
                seq=getattr(rec, "seq", 0),
                updated_at=getattr(rec, "updated_at", rec.created_at),
            )
            return job

    async with _lock:
        job = _jobs.get(job_id)
        if job is None:
            return None

        job.status = status
        if result is not None:
            job.result = result
        if error is not None:
            job.error = error
        # increment seq for event ordering
        try:
            job.seq = (job.seq or 0) + 1
        except Exception:
            job.seq = 1
        # Update timestamp for in-memory jobs
        job.updated_at = time.time()
        updated = job

    # Notify subscribers outside of the lock to avoid blocking other callers.
    # Use shared serializer to build the event dict
    from ..utils.serialize import serialize_job as _serialize_job
    event = _serialize_job(updated)
    for q in list(_subscribers):
        try:
            q.put_nowait(event)
        except Exception:
            # If a subscriber's queue is full or closed, best-effort ignore.
            pass

    return updated

async def list_jobs(owner_id: Optional[str] = None, status: Optional[str] = None) -> Dict[str, Job]:
    """
    List jobs, optionally filtered by owner_id and/or status.

    Returns a mapping of job_id -> Job dataclass.
    """
    if _USE_PERSISTENCE:
        adapter = await _get_adapter()
        if adapter is not None:
            recs = await adapter.list_jobs(owner_id=owner_id, status=status)
            out: Dict[str, Job] = {}
            for k, r in recs.items():
                out[k] = Job(
                    id=r.run_id,
                    workflow_id=str(getattr(r, "workflow_id", "")),
                    created_at=r.created_at,
                    status=JobStatus(r.status),
                    result=r.result,
                    error=r.error,
                    owner_id=getattr(r, "owner_id", None),
                    seq=getattr(r, "seq", 0),
                    updated_at=getattr(r, "updated_at", r.created_at),
                )
            return out
    async with _lock:
        # filter in-memory jobs
        out = {}
        for k, job in _jobs.items():
            if owner_id is not None and getattr(job, "owner_id", None) != owner_id:
                continue
            if status is not None and job.status.value != status:
                continue
            out[k] = job
        return out

async def remove_job(job_id: str) -> Optional[Job]:
    async with _lock:
        return _jobs.pop(job_id, None)
# endregion

# region PubSub for job events
def subscribe_events() -> asyncio.Queue:
    """
    Return a new asyncio.Queue that will receive job event dicts.

    Caller is responsible for consuming and ensuring the queue does not grow
    unbounded. Use `unsubscribe_events` to remove the queue when done.
    """
    if _USE_PERSISTENCE:
        # delegate to adapter if available (import synchronously and configure)
        try:
            adapter = __import__(__package__ + ".job_store_sqlite", fromlist=["*"])
            try:
                db_path = getattr(_settings, "WORKFLOW_RUNNER_DB_PATH", "") or None
                adapter.configure(db_path)
            except Exception:
                LOG.debug("sqlite adapter configure() failed in subscribe_events; continuing")
            return adapter.subscribe_events()
        except Exception:
            # fall back to in-memory pubsub
            pass
    q: asyncio.Queue = asyncio.Queue()
    _subscribers.append(q)
    return q

def unsubscribe_events(q: asyncio.Queue) -> None:
    try:
        if _USE_PERSISTENCE:
            try:
                adapter = __import__(__package__ + ".job_store_sqlite", fromlist=["*"])
                try:
                    db_path = getattr(_settings, "WORKFLOW_RUNNER_DB_PATH", "") or None
                    adapter.configure(db_path)
                except Exception:
                    LOG.debug("sqlite adapter configure() failed in unsubscribe_events; continuing")
                return adapter.unsubscribe_events(q)
            except Exception:
                pass
        _subscribers.remove(q)
    except ValueError:
        pass

def publish_event(event: Dict[str, Any]) -> None:
    """
    Publish an arbitrary event dict to all subscribers.

    This is useful for streaming proxy outputs (kobold messages) into the
    same SSE channel used for run updates. The event dict should be JSON
    serializable and include an identifying key (for example, 'type' or
    'run_id').
    """
    if _USE_PERSISTENCE:
        try:
            adapter = __import__(__package__ + ".job_store_sqlite", fromlist=["*"])
            try:
                db_path = getattr(_settings, "WORKFLOW_RUNNER_DB_PATH", "") or None
                adapter.configure(db_path)
            except Exception:
                LOG.debug("sqlite adapter configure() failed in publish_event; continuing")
            return adapter.publish_event(event)
        except Exception:
            LOG.exception("Failed to publish via sqlite adapter; falling back to in-memory pubsub")

    for q in list(_subscribers):
        try:
            q.put_nowait(event)
        except Exception:
            LOG.exception("Failed to enqueue event to subscriber queue")
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