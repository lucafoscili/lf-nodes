import asyncio
import inspect
import logging
import time

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional

from ..config import get_settings
from .input_snapshot import sanitize_input_snapshot
from .job_contracts import validate_submission_identity as _validate_submission_identity

#region Definitions
_settings = get_settings()
_WF_DEBUG = bool(_settings.WORKFLOW_RUNNER_DEBUG)

class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

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
    # Small, durable replay/remix input snapshot.  This is intentionally kept
    # out of generic serializers and event payloads; detail/status is the only
    # API surface that exposes it.
    inputs: Dict[str, Any] = field(default_factory=dict)
    # Stable submission authority is public only by its opaque id.  The
    # fingerprint and Core URL remain storage-internal and allow owner-bound
    # lifecycle recovery after a process restart.
    submission_id: Optional[str] = None
    request_fingerprint: Optional[str] = None
    comfy_url: Optional[str] = None

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


def _coerce_inputs(value: Any) -> Dict[str, Any]:
    """Accept records from pre-snapshot adapters without leaking mocks/objects."""

    return value if isinstance(value, dict) else {}


def _adapter_accepts_kwarg(create_job_callable: Any, name: str) -> bool:
    """Return whether a persistence adapter supports one additive keyword.

    Third-party adapters predate durable remix snapshots, so keep their
    published three-argument ``create_job`` contract working.  Signature
    inspection avoids retrying after an adapter has performed side effects.
    """

    try:
        parameters = inspect.signature(create_job_callable).parameters.values()
    except (TypeError, ValueError):
        # Opaque callables are treated as modern; Python callables and mocks
        # expose enough signature information for the compatibility path.
        return True
    return any(
        parameter.name == name or parameter.kind is inspect.Parameter.VAR_KEYWORD
        for parameter in parameters
    )


#endregion

# region create
async def create_job(
    job_id: str,
    workflow_id: str,
    owner_id: Optional[str] = None,
    *,
    inputs: Optional[Dict[str, Any]] = None,
    submission_id: Optional[str] = None,
    request_fingerprint: Optional[str] = None,
    comfy_url: Optional[str] = None,
) -> Job:
    """Create a new job with the given ID (ComfyUI's prompt_id).
    
    Args:
        job_id: ComfyUI's prompt_id for this execution
        workflow_id: The workflow definition identifier
        owner_id: Optional owner/user identifier
    """
    _validate_submission_identity(submission_id, request_fingerprint, comfy_url)
    if _WF_DEBUG:
        LOG.info(f"[DEBUG] create_job called: job_id={job_id}, workflow_id={workflow_id}, owner_id={owner_id}")
    
    if _USE_PERSISTENCE:
        adapter = await _get_adapter()
        if adapter is None:
            if submission_id is not None:
                raise RuntimeError(
                    "job-store persistence is unavailable for stable submission identity"
                )
        else:
            if _WF_DEBUG:
                LOG.info(f"[DEBUG] create_job: calling adapter.create_job with workflow_id={workflow_id}, owner_id={owner_id}")
            adapter_kwargs = {"workflow_id": workflow_id, "owner_id": owner_id}
            if inputs is not None and _adapter_accepts_kwarg(adapter.create_job, "inputs"):
                adapter_kwargs["inputs"] = sanitize_input_snapshot(inputs)
            if submission_id is not None:
                unsupported = [
                    name
                    for name in ("submission_id", "request_fingerprint", "comfy_url")
                    if not _adapter_accepts_kwarg(adapter.create_job, name)
                ]
                if unsupported:
                    raise RuntimeError(
                        "job-store adapter cannot persist stable submission identity"
                    )
                durable_lookup = getattr(
                    adapter,
                    "get_job_by_submission_id",
                    None,
                )
                if durable_lookup is None:
                    raise RuntimeError(
                        "job-store adapter cannot verify stable submission identity"
                    )
            else:
                durable_lookup = None
            for name, value in (
                ("submission_id", submission_id),
                ("request_fingerprint", request_fingerprint),
                ("comfy_url", comfy_url),
            ):
                if value is not None and _adapter_accepts_kwarg(adapter.create_job, name):
                    adapter_kwargs[name] = value
            rec = await adapter.create_job(job_id, **adapter_kwargs)
            if submission_id is not None:
                persisted = await durable_lookup(submission_id)
                if (
                    persisted is None
                    or getattr(persisted, "run_id", None) != job_id
                    or getattr(persisted, "workflow_id", None) != workflow_id
                    or getattr(persisted, "owner_id", None) != owner_id
                    or getattr(persisted, "submission_id", None) != submission_id
                    or getattr(persisted, "request_fingerprint", None)
                    != request_fingerprint
                    or getattr(persisted, "comfy_url", None) != comfy_url
                ):
                    raise RuntimeError(
                        "job-store adapter did not preserve stable submission identity"
                    )
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
                    inputs=_coerce_inputs(getattr(rec, "inputs", {})),
                    seq=getattr(rec, "seq", 0),
                    updated_at=getattr(rec, "updated_at", None),
                    submission_id=getattr(rec, "submission_id", submission_id),
                    request_fingerprint=getattr(
                        rec,
                        "request_fingerprint",
                        request_fingerprint,
                    ),
                    comfy_url=getattr(rec, "comfy_url", comfy_url),
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
                    inputs=_coerce_inputs(getattr(rec, "inputs", {})),
                    seq=getattr(rec, "seq", 0),
                    updated_at=getattr(rec, "updated_at", None),
                    submission_id=getattr(rec, "submission_id", submission_id),
                    request_fingerprint=getattr(
                        rec,
                        "request_fingerprint",
                        request_fingerprint,
                    ),
                    comfy_url=getattr(rec, "comfy_url", comfy_url),
                )
            return job

    async with _lock:
        existing_job = _jobs.get(job_id)
        if submission_id is not None and existing_job is not None:
            if (
                existing_job.workflow_id != workflow_id
                or existing_job.owner_id != owner_id
                or existing_job.submission_id != submission_id
                or existing_job.request_fingerprint != request_fingerprint
                or existing_job.comfy_url != comfy_url
            ):
                raise ValueError("job is already bound to another submission identity")
            return existing_job
        if submission_id is not None and any(
            existing.id != job_id and existing.submission_id == submission_id
            for existing in _jobs.values()
        ):
            raise ValueError("submission_id is already bound to another job")
        job = Job(
            id=job_id,
            workflow_id=workflow_id,
            owner_id=owner_id,
            inputs=sanitize_input_snapshot(inputs),
            submission_id=submission_id,
            request_fingerprint=request_fingerprint,
            comfy_url=comfy_url,
            seq=0,
        )
        _jobs[job_id] = job
        updated = job

    # The historical event contract includes terminal results.  Consumers that
    # need the bounded card shape opt in at the HTTP/SSE boundary and project
    # the event through ``serialize_run_summary`` there.
    from ..utils.serialize import serialize_job
    event = serialize_job(updated, include_result_for_terminal=True)
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
                inputs=_coerce_inputs(getattr(rec, "inputs", {})),
                seq=getattr(rec, "seq", 0),
                updated_at=getattr(rec, "updated_at", rec.created_at),
                submission_id=getattr(rec, "submission_id", None),
                request_fingerprint=getattr(rec, "request_fingerprint", None),
                comfy_url=getattr(rec, "comfy_url", None),
            )
            return job
    async with _lock:
        return _jobs.get(job_id)


async def get_job_by_submission_id(submission_id: str) -> Optional[Job]:
    """Resolve one durable stable submission handle without exposing its fingerprint."""

    if not isinstance(submission_id, str) or not submission_id or len(submission_id) > 128:
        return None
    if _USE_PERSISTENCE:
        adapter = await _get_adapter()
        lookup = getattr(adapter, "get_job_by_submission_id", None) if adapter else None
        if lookup is None:
            raise RuntimeError(
                "job-store adapter cannot verify stable submission identity"
            )
        rec = await lookup(submission_id)
        if rec is None:
            return None
        return Job(
            id=rec.run_id,
            workflow_id=str(getattr(rec, "workflow_id", "")),
            created_at=rec.created_at,
            status=JobStatus(rec.status),
            result=rec.result,
            error=rec.error,
            owner_id=getattr(rec, "owner_id", None),
            inputs=_coerce_inputs(getattr(rec, "inputs", {})),
            seq=getattr(rec, "seq", 0),
            updated_at=getattr(rec, "updated_at", rec.created_at),
            submission_id=getattr(rec, "submission_id", None),
            request_fingerprint=getattr(rec, "request_fingerprint", None),
            comfy_url=getattr(rec, "comfy_url", None),
        )
    async with _lock:
        matches = [job for job in _jobs.values() if job.submission_id == submission_id]
        return matches[0] if len(matches) == 1 else None

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
                inputs=_coerce_inputs(getattr(rec, "inputs", {})),
                seq=getattr(rec, "seq", 0),
                updated_at=getattr(rec, "updated_at", rec.created_at),
                submission_id=getattr(rec, "submission_id", None),
                request_fingerprint=getattr(rec, "request_fingerprint", None),
                comfy_url=getattr(rec, "comfy_url", None),
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
    # Preserve the published SSE payload by default; summary callers project
    # this event explicitly in the controller.
    from ..utils.serialize import serialize_job
    event = serialize_job(updated, include_result_for_terminal=True)
    for q in list(_subscribers):
        try:
            q.put_nowait(event)
        except Exception:
            # If a subscriber's queue is full or closed, best-effort ignore.
            pass

    return updated


async def set_job_status_if_unchanged(
    job_id: str,
    new_status: JobStatus,
    *,
    owner_id: Optional[str],
    expected_status: str,
    seq: int,
    updated_at: Optional[float],
    result: Optional[Any] = None,
    error: Optional[str] = None,
    clear_error: bool = False,
) -> Optional[Job]:
    """Publish a status transition only while one scanned snapshot is current.

    Background reconciliation performs network reads between scanning a job and
    publishing its terminal state.  Matching owner, status, sequence, and
    update time prevents that delayed evidence from overwriting a concurrent
    completion or cancellation.
    """

    normalized_status = (
        new_status if isinstance(new_status, JobStatus) else JobStatus(str(new_status))
    )
    normalized_expected = str(
        getattr(expected_status, "value", expected_status) or ""
    )

    if _USE_PERSISTENCE:
        adapter = await _get_adapter()
        update = (
            getattr(adapter, "set_job_status_if_unchanged", None)
            if adapter
            else None
        )
        if update is None:
            return None
        if clear_error and not _adapter_accepts_kwarg(update, "clear_error"):
            # Clearing a synthetic terminal error is part of the compare-and-
            # swap operation.  Falling back to a non-atomic second write could
            # overwrite a real terminal result, so older adapters fail closed.
            return None
        rec = await update(
            job_id,
            normalized_status.value,
            owner_id=owner_id,
            expected_status=normalized_expected,
            seq=int(seq),
            updated_at=updated_at,
            result=result,
            error=error,
            **({"clear_error": True} if clear_error else {}),
        )
        if rec is None:
            return None
        return Job(
            id=rec.run_id,
            workflow_id=str(getattr(rec, "workflow_id", "")),
            created_at=rec.created_at,
            status=JobStatus(rec.status),
            result=rec.result,
            error=rec.error,
            owner_id=getattr(rec, "owner_id", None),
            inputs=_coerce_inputs(getattr(rec, "inputs", {})),
            seq=getattr(rec, "seq", 0),
            updated_at=getattr(rec, "updated_at", rec.created_at),
            submission_id=getattr(rec, "submission_id", None),
            request_fingerprint=getattr(rec, "request_fingerprint", None),
            comfy_url=getattr(rec, "comfy_url", None),
        )

    async with _lock:
        job = _jobs.get(job_id)
        if job is None:
            return None
        raw_status = getattr(job, "status", "")
        current_status = str(getattr(raw_status, "value", raw_status) or "")
        if (
            getattr(job, "owner_id", None) != owner_id
            or current_status != normalized_expected
            or int(getattr(job, "seq", 0) or 0) != int(seq)
            or getattr(job, "updated_at", None) != updated_at
        ):
            return None

        job.status = normalized_status
        if result is not None:
            job.result = result
        if clear_error:
            job.error = None
        elif error is not None:
            job.error = error
        job.seq = int(getattr(job, "seq", 0) or 0) + 1
        job.updated_at = time.time()
        updated = job

    from ..utils.serialize import serialize_job

    event = serialize_job(updated, include_result_for_terminal=True)
    for q in list(_subscribers):
        try:
            q.put_nowait(event)
        except Exception:
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
                    inputs=_coerce_inputs(getattr(r, "inputs", {})),
                    seq=getattr(r, "seq", 0),
                    updated_at=getattr(r, "updated_at", r.created_at),
                    submission_id=getattr(r, "submission_id", None),
                    request_fingerprint=getattr(r, "request_fingerprint", None),
                    comfy_url=getattr(r, "comfy_url", None),
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


async def hard_delete_job_if_unchanged(
    job_id: str,
    *,
    owner_id: Optional[str],
    status: str,
    seq: int,
    updated_at: Optional[float],
) -> bool:
    """Hard-delete one exact history snapshot.

    This dedicated compare-and-swap path is intentionally separate from the
    generic/background ``remove_job`` behavior.  A run that changes after a
    cleanup scan is preserved.
    """

    if _USE_PERSISTENCE:
        adapter = await _get_adapter()
        delete = (
            getattr(adapter, "hard_delete_job_if_unchanged", None)
            if adapter
            else None
        )
        if delete is None:
            return False
        return bool(
            await delete(
                job_id,
                owner_id=owner_id,
                status=status,
                seq=seq,
                updated_at=updated_at,
            )
        )

    async with _lock:
        job = _jobs.get(job_id)
        if job is None:
            return False
        raw_status = getattr(job, "status", "")
        current_status = str(getattr(raw_status, "value", raw_status))
        if (
            getattr(job, "owner_id", None) != owner_id
            or current_status != status
            or int(getattr(job, "seq", 0) or 0) != int(seq)
            or getattr(job, "updated_at", None) != updated_at
        ):
            return False
        del _jobs[job_id]
        return True
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
    "get_job_by_submission_id",
    "list_jobs",
    "hard_delete_job_if_unchanged",
    "remove_job",
    "set_job_status",
    "set_job_status_if_unchanged",
]
