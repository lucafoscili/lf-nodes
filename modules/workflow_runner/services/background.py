import asyncio
import logging
import math
import time
from collections.abc import Mapping
from typing import Any
from urllib.parse import quote, urlsplit

from ..config import get_settings
from .job_contracts import job_status_value as _status_value

_settings = get_settings()

# region Pruner configuration
_JOB_TTL_SECONDS = max(0, int(_settings.JOB_TTL_SECONDS))
_JOB_PRUNE_INTERVAL = int(_settings.JOB_PRUNE_INTERVAL_SECONDS or 60)
_SESSION_PRUNE_INTERVAL = int(_settings.SESSION_PRUNE_INTERVAL_SECONDS or 60)
_QUEUE_STATUS_INTERVAL = 1  # Send queue updates every second
_ACTIVE_RECONCILE_INTERVAL = 30
_ACTIVE_RECONCILE_GRACE_SECONDS = 120.0
_ACTIVE_RECONCILE_MAX_CANDIDATES = 64
_ACTIVE_STATUSES = {"pending", "running"}
_TERMINAL_STATUSES = {"succeeded", "failed", "cancelled", "timeout"}
_MAX_HISTORY_ERROR_BYTES = 4096
# endregion

# region Helpers
def _active_prompt_ids_from_queue(queue_data: Any) -> set[str] | None:
    """Return exact active prompt IDs, or ``None`` when absence is unproven."""

    if not isinstance(queue_data, Mapping):
        return None

    active_prompt_ids: set[str] = set()
    for queue_name in ("queue_running", "queue_pending"):
        rows = queue_data.get(queue_name)
        if not isinstance(rows, list):
            return None
        for row in rows:
            if (
                not isinstance(row, (list, tuple))
                or len(row) < 2
                or not isinstance(row[1], str)
                or not row[1]
            ):
                return None
            active_prompt_ids.add(row[1])
    return active_prompt_ids


def _validated_comfy_url(value: Any) -> str | None:
    """Return a bounded HTTP(S) Core authority, or preserve the row."""

    if not isinstance(value, str) or not value.strip() or len(value) > 2048:
        return None
    normalized = value.strip().rstrip("/")
    try:
        parsed = urlsplit(normalized)
    except ValueError:
        return None
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    return normalized


async def fetch_active_prompt_ids(
    *,
    session: Any = None,
    comfy_url: str | None = None,
) -> set[str] | None:
    """Fetch a validated snapshot of ComfyUI's running and pending prompts.

    ``None`` is deliberately distinct from an empty set: it means the queue
    could not prove that any prompt is absent, so destructive callers must
    preserve their records.
    """

    async def fetch(session_to_use: Any) -> set[str] | None:
        authority = _validated_comfy_url(comfy_url or _settings.COMFY_BACKEND_URL)
        if authority is None:
            return None
        queue_url = f"{authority}/queue"
        async with session_to_use.get(queue_url) as response:
            if response.status != 200:
                return None
            return _active_prompt_ids_from_queue(await response.json())

    try:
        if session is not None:
            return await fetch(session)

        import aiohttp

        timeout = aiohttp.ClientTimeout(total=5.0)
        async with aiohttp.ClientSession(timeout=timeout) as owned_session:
            return await fetch(owned_session)
    except Exception as exc:
        logging.debug("Could not verify ComfyUI active prompts: %s", exc)
        return None


async def _fetch_prompt_history(
    prompt_id: str,
    *,
    session: Any,
    comfy_url: str | None = None,
) -> tuple[bool, Mapping[str, Any] | None]:
    """Return ``(verified, entry)`` for one exact ComfyUI history lookup."""

    authority = _validated_comfy_url(comfy_url or _settings.COMFY_BACKEND_URL)
    if authority is None:
        return False, None
    history_url = f"{authority}/history/{quote(prompt_id, safe='')}"
    try:
        async with session.get(history_url) as response:
            if response.status != 200:
                return False, None
            body = await response.json()
    except Exception as exc:
        logging.debug("Could not verify ComfyUI history for %s: %s", prompt_id, exc)
        return False, None

    if not isinstance(body, Mapping):
        return False, None
    entry = body.get(prompt_id)
    if entry is not None:
        return (True, entry) if isinstance(entry, Mapping) else (False, None)
    if not body:
        return True, None
    # A few Comfy-compatible backends return the exact entry directly.
    if isinstance(body.get("status"), Mapping) or "outputs" in body:
        return True, body
    return False, None


def _terminal_update_from_history(
    history_entry: Mapping[str, Any],
) -> tuple[str, Any, str | None] | None:
    """Project an explicit terminal history entry into Runner's result contract."""

    raw_status = history_entry.get("status")
    if not isinstance(raw_status, Mapping):
        return None
    status_str = raw_status.get("status_str")
    messages = raw_status.get("messages")
    messages = messages if isinstance(messages, (list, tuple)) else ()
    interrupted = any(
        isinstance(message, (list, tuple))
        and len(message) >= 1
        and message[0] == "execution_interrupted"
        for message in messages
    )
    # ``completed`` without Core's known terminal status is ambiguous. Do not
    # turn a malformed or future status value into a successful Runner record.
    if not interrupted and status_str not in {"success", "error"}:
        return None

    history = {
        "status": raw_status,
        "outputs": history_entry.get("outputs", {}) or {},
        "prompt": history_entry.get("prompt"),
    }
    outputs = history.get("outputs", {})
    if interrupted:
        result = {
            "http_status": 200,
            "body": _make_reconciliation_payload(
                detail="cancelled",
                history={"outputs": outputs},
            ),
        }
        return "cancelled", result, None
    if status_str == "error":
        detail = "error"
        for message in messages:
            if (
                isinstance(message, (list, tuple))
                and len(message) >= 2
                and message[0] == "execution_error"
                and isinstance(message[1], Mapping)
            ):
                value = message[1].get("exception_message")
                if isinstance(value, str) and value.strip():
                    encoded = value.replace("\x00", "").strip().encode(
                        "utf-8",
                        "replace",
                    )
                    detail = encoded[:_MAX_HISTORY_ERROR_BYTES].decode(
                        "utf-8",
                        "ignore",
                    )
                    break
        result = {
            "http_status": 500,
            "body": _make_reconciliation_payload(
                detail=detail,
                history={"outputs": outputs},
                error_message="execution_failed",
            ),
        }
        return "failed", result, "execution_failed"

    if status_str != "success":
        return None

    result = {
        "http_status": 200,
        "body": _make_reconciliation_payload(history=history),
    }
    return "succeeded", result, None


def _make_reconciliation_payload(
    *,
    detail: str = "",
    error_message: str | None = None,
    history: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build Runner's small public result envelope without importing execution."""

    payload: dict[str, Any] = {
        "detail": detail or "",
        "history": dict(history) if history is not None else {"outputs": {}},
    }
    if error_message is not None:
        payload["error"] = {"message": error_message}
    return {
        "message": detail or "",
        "payload": payload,
        "status": "error" if error_message else "ready",
    }


def _execution_state_lost_update() -> tuple[str, Any, str]:
    """Build the bounded failure published for an authoritatively absent prompt."""

    error = "execution_state_lost"
    detail = "ComfyUI no longer has this prompt in its queue or history."
    return (
        "failed",
        {
            "http_status": 500,
            "body": _make_reconciliation_payload(
                detail=detail,
                error_message=error,
            ),
        },
        error,
    )


async def _record_reconciled_lifecycle(
    prompt_id: str,
    status: str,
    *,
    result: Any,
    error: str | None,
) -> None:
    """Mirror a successful job-store CAS into the process-local lifecycle."""

    try:
        from .lifecycle import record_terminal

        await record_terminal(prompt_id, status, result=result, error=error)
    except Exception:
        logging.exception("Failed to reconcile submission lifecycle for %s", prompt_id)


def _job_activity_timestamp(job: Any) -> float | None:
    """Return the latest trustworthy active-row timestamp, if one exists."""

    for value in (getattr(job, "updated_at", None), getattr(job, "created_at", None)):
        if (
            not isinstance(value, bool)
            and isinstance(value, (int, float))
            and math.isfinite(float(value))
            and float(value) >= 0
        ):
            return float(value)
    return None


async def _reconcile_active_jobs_once(
    job_manager_module: Any,
    *,
    now: float | None = None,
    grace_seconds: float = _ACTIVE_RECONCILE_GRACE_SECONDS,
    session: Any = None,
) -> list[tuple[str, str]]:
    """Close stale active rows only from verified queue and exact history state."""

    try:
        jobs = await job_manager_module.list_jobs()
    except Exception:
        logging.exception("Failed to list active jobs for reconciliation")
        return []

    current_time = time.time() if now is None else float(now)
    candidates: list[
        tuple[float, str, str, int, str | None, float | None, str]
    ] = []
    for job_id, job in jobs.items():
        expected_status = _status_value(job)
        if expected_status not in _ACTIVE_STATUSES:
            continue
        activity_at = _job_activity_timestamp(job)
        if activity_at is None or activity_at + max(0.0, grace_seconds) > current_time:
            continue
        comfy_url = _validated_comfy_url(getattr(job, "comfy_url", None))
        if comfy_url is None:
            # Legacy/unbound rows have no trustworthy negative-state authority.
            # Querying the current configured backend could falsely fail work
            # that was submitted to an earlier backend.
            continue
        candidates.append(
            (
                activity_at,
                str(job_id),
                expected_status,
                int(getattr(job, "seq", 0) or 0),
                getattr(job, "owner_id", None),
                getattr(job, "updated_at", None),
                comfy_url,
            )
        )

    if not candidates:
        return []
    candidates.sort(key=lambda candidate: (candidate[0], candidate[1]))
    candidates = candidates[:_ACTIVE_RECONCILE_MAX_CANDIDATES]

    update_if_unchanged = getattr(
        job_manager_module,
        "set_job_status_if_unchanged",
        None,
    )
    if update_if_unchanged is None:
        logging.error(
            "Job store has no compare-and-swap status update; preserving active jobs"
        )
        return []

    async def reconcile(session_to_use: Any) -> list[tuple[str, str]]:
        reconciled: list[tuple[str, str]] = []
        history_absent: list[
            tuple[float, str, str, int, str | None, float | None, str]
        ] = []

        async def publish_terminal(
            candidate: tuple[float, str, str, int, str | None, float | None, str],
            terminal_update: tuple[str, Any, str | None],
        ) -> None:
            _, prompt_id, expected_status, seq, owner_id, updated_at, _ = candidate
            terminal_status, result, error = terminal_update
            status_enum = getattr(
                getattr(job_manager_module, "JobStatus", object),
                terminal_status.upper(),
                terminal_status,
            )
            try:
                updated = await update_if_unchanged(
                    prompt_id,
                    status_enum,
                    owner_id=owner_id,
                    expected_status=expected_status,
                    seq=seq,
                    updated_at=updated_at,
                    result=result,
                    error=error,
                )
            except Exception:
                logging.exception("Failed to reconcile active job %s", prompt_id)
                return
            if updated is None:
                return
            reconciled.append((prompt_id, terminal_status))
            await _record_reconciled_lifecycle(
                prompt_id,
                terminal_status,
                result=result,
                error=error,
            )

        # First read: terminal history is already authoritative. Only an exact,
        # verified absence proceeds to the queue check; ambiguous or nonterminal
        # history preserves the active row.
        for candidate in candidates:
            prompt_id = candidate[1]
            comfy_url = candidate[6]
            history_verified, history_entry = await _fetch_prompt_history(
                prompt_id,
                session=session_to_use,
                comfy_url=comfy_url,
            )
            if not history_verified:
                continue
            if history_entry is None:
                history_absent.append(candidate)
                continue
            terminal_update = _terminal_update_from_history(history_entry)
            if terminal_update is None:
                continue
            await publish_terminal(candidate, terminal_update)

        if not history_absent:
            return reconciled

        # Second read after the validated queue snapshot closes the
        # queue-to-history publication race. Only a second exact absence is
        # evidence that Core has lost the execution state.
        by_authority: dict[
            str,
            list[tuple[float, str, str, int, str | None, float | None, str]],
        ] = {}
        for candidate in history_absent:
            by_authority.setdefault(candidate[6], []).append(candidate)

        for comfy_url, authority_candidates in by_authority.items():
            active_prompt_ids = await fetch_active_prompt_ids(
                session=session_to_use,
                comfy_url=comfy_url,
            )
            if active_prompt_ids is None:
                logging.warning(
                    "Skipping state-loss reconciliation for %d stale active jobs because ComfyUI's queue could not be verified",
                    len(authority_candidates),
                )
                continue
            for candidate in authority_candidates:
                prompt_id = candidate[1]
                if prompt_id in active_prompt_ids:
                    continue
                history_verified, history_entry = await _fetch_prompt_history(
                    prompt_id,
                    session=session_to_use,
                    comfy_url=comfy_url,
                )
                if not history_verified:
                    continue
                terminal_update = (
                    _execution_state_lost_update()
                    if history_entry is None
                    else _terminal_update_from_history(history_entry)
                )
                if terminal_update is None:
                    continue
                await publish_terminal(candidate, terminal_update)
        return reconciled

    if session is not None:
        return await reconcile(session)

    try:
        import aiohttp

        timeout = aiohttp.ClientTimeout(total=10.0)
        async with aiohttp.ClientSession(timeout=timeout) as owned_session:
            return await reconcile(owned_session)
    except Exception:
        logging.exception("Unexpected error while reconciling active jobs")
        return []


async def _session_pruner_loop(session_cleanup_callable) -> None:
    try:
        while True:
            try:
                before = None
                try:
                    # Attempt to call the provided cleanup function
                    session_cleanup_callable()
                except Exception:
                    logging.exception("Error while pruning sessions")
                await asyncio.sleep(_SESSION_PRUNE_INTERVAL)
            except Exception:
                logging.exception("Unexpected error in session pruner loop")
    except asyncio.CancelledError:
        logging.debug("Session pruner task cancelled")


async def _prune_jobs_once(
    job_manager_module: Any,
    *,
    now: float | None = None,
    ttl_seconds: float = _JOB_TTL_SECONDS,
) -> list[str]:
    """Remove expired terminal rows only after proving their prompts inactive."""

    if ttl_seconds <= 0:
        return []

    try:
        jobs = await job_manager_module.list_jobs()
    except Exception:
        logging.exception("Failed to list jobs for pruning")
        return []

    current_time = time.time() if now is None else now
    candidates: list[tuple[str, str, int, str | None, float]] = []
    for job_id, job in jobs.items():
        status = _status_value(job)
        if status not in _TERMINAL_STATUSES:
            # Pending and running jobs are never made terminal by age alone.
            continue

        updated_at = getattr(job, "updated_at", None)
        if (
            isinstance(updated_at, bool)
            or not isinstance(updated_at, (int, float))
            or not math.isfinite(float(updated_at))
            or float(updated_at) + ttl_seconds > current_time
        ):
            continue
        candidates.append(
            (
                str(job_id),
                status,
                int(getattr(job, "seq", 0) or 0),
                getattr(job, "owner_id", None),
                updated_at,
            )
        )

    if not candidates:
        return []

    try:
        active_prompt_ids = await fetch_active_prompt_ids()
    except Exception:
        logging.exception("Failed to verify ComfyUI queue before job pruning")
        return []
    if active_prompt_ids is None:
        logging.warning(
            "Skipping retention for %d expired terminal jobs because the ComfyUI queue could not be verified",
            len(candidates),
        )
        return []

    delete_if_unchanged = getattr(
        job_manager_module, "hard_delete_job_if_unchanged", None
    )
    if delete_if_unchanged is None:
        logging.error("Job store has no compare-and-swap retention delete; preserving jobs")
        return []

    removed_job_ids: list[str] = []
    for job_id, status, seq, owner_id, updated_at in candidates:
        if job_id in active_prompt_ids:
            continue
        try:
            removed = await delete_if_unchanged(
                job_id,
                owner_id=owner_id,
                status=status,
                seq=seq,
                updated_at=updated_at,
            )
        except Exception:
            logging.exception("Failed to remove job %s during pruning", job_id)
            continue
        if removed:
            removed_job_ids.append(job_id)

    return removed_job_ids


async def _job_pruner_loop(job_manager_module) -> None:
    try:
        while True:
            try:
                removed_job_ids = await _prune_jobs_once(job_manager_module)
                if removed_job_ids:
                    logging.debug("Job pruner removed %d jobs", len(removed_job_ids))
            except Exception:
                logging.exception("Error during job prune")
            await asyncio.sleep(_JOB_PRUNE_INTERVAL)
    except asyncio.CancelledError:
        logging.debug("Job pruner cancelled")


async def _active_job_reconciler_loop(job_manager_module: Any) -> None:
    try:
        while True:
            try:
                reconciled = await _reconcile_active_jobs_once(job_manager_module)
                if reconciled:
                    logging.warning(
                        "Reconciled %d orphaned or unpublished active Runner jobs",
                        len(reconciled),
                    )
            except Exception:
                logging.exception("Error during active job reconciliation")
            await asyncio.sleep(_ACTIVE_RECONCILE_INTERVAL)
    except asyncio.CancelledError:
        logging.debug("Active job reconciler cancelled")


async def _queue_status_publisher_loop(job_store_module) -> None:
    try:
        # Track last seen counts so we can avoid publishing duplicate identical
        # queue status events every interval. This significantly reduces SSE
        # noise when nothing has changed.
        last_pending = None
        last_running = None
        while True:
            try:
                # Fetch queue status from ComfyUI
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    try:
                        async with session.get('http://127.0.0.1:8188/queue') as resp:
                            if resp.status == 200:
                                queue_data = await resp.json()
                                pending = len(queue_data.get('queue_pending', []))
                                running = len(queue_data.get('queue_running', []))

                                # Only publish when counts change to avoid flooding
                                # subscribers with identical periodic updates.
                                if pending != last_pending or running != last_running:
                                    event = {
                                        "type": "queue_status",
                                        "pending": pending,
                                        "running": running,
                                    }
                                    try:
                                        job_store_module.publish_event(event)
                                    except Exception:
                                        logging.exception("Failed to publish queue_status event")
                                    last_pending = pending
                                    last_running = running
                    except Exception:
                        logging.debug("Failed to fetch queue status")
            except Exception:
                logging.exception("Error in queue status publisher")
            await asyncio.sleep(_QUEUE_STATUS_INTERVAL)
    except asyncio.CancelledError:
        logging.debug("Queue status publisher cancelled")


async def fetch_queue_status() -> dict | None:
    """
    Asynchronously fetches the current queue status from the local ComfyUI queue endpoint.
    This helper function makes an HTTP GET request to 'http://127.0.0.1:8188/queue' and parses the response
    to extract the number of pending and running tasks in the queue. It is designed to be exported for use
    by other modules, such as the SSE controller, to provide an initial queue status snapshot to newly
    connected clients without duplicating HTTP request logic.

    Returns:
        dict | None: A dictionary containing 'pending' (int) and 'running' (int) counts if successful,
                     or None if an error occurs during the request or parsing.
                     
    Raises:
        No exceptions are raised; errors are logged and None is returned on failure.
    """
    try:
        import aiohttp

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get('http://127.0.0.1:8188/queue') as resp:
                    if resp.status == 200:
                        queue_data = await resp.json()
                        pending = len(queue_data.get('queue_pending', []))
                        running = len(queue_data.get('queue_running', []))
                        return {"pending": pending, "running": running}
            except Exception:
                logging.debug("Failed to fetch queue status (fetch_queue_status)")
    except Exception:
        logging.exception("Unexpected error while fetching queue status")
    return None
# endregion

# region Background task management
async def start_background_tasks(app: Any) -> None:
    """
    Asynchronously start background tasks for the workflow runner, including session pruning and job pruning.
    This function is idempotent, meaning it can be called multiple times without adverse effects.
    It initializes and starts background tasks only once per application instance by checking
    a flag on the app object. The tasks are responsible for periodic cleanup of expired sessions
    and jobs, leveraging existing modules for session management and job handling.

    Parameters:
        app (Any): The application instance (e.g., a web framework app object) where background
                   tasks will be stored and managed. It must support dictionary-like access for
                   storing task references and flags.

    Notes:
        - Attempts to import 'routes' and 'job_manager' modules from the parent package.
        - If 'routes' module is available and has '_cleanup_expired_sessions', starts a session
          pruner task that runs at intervals defined by _SESSION_PRUNE_INTERVAL.
        - If 'job_manager' module is available, starts an active-state reconciler. It waits out
          the publication grace and requires verified ComfyUI queue/history evidence.
        - When terminal retention is enabled, starts a job pruner task at _JOB_PRUNE_INTERVAL.
        - Task references are stored on the app object for potential cancellation or monitoring.
        - Logs the start of each task with relevant configuration details.
        - Sets a flag '_workflow_runner_bg_started' on the app to prevent re-initialization.
    """
    if app.get("_workflow_runner_bg_started"):
        return

    try:
        from .. import routes as routes_mod
    except Exception:
        routes_mod = None

    try:
        from ..services import job_store as job_manager_mod
    except Exception:
        job_manager_mod = None

    if routes_mod and hasattr(routes_mod, "_cleanup_expired_sessions"):
        task = asyncio.create_task(_session_pruner_loop(routes_mod._cleanup_expired_sessions))
        app["_session_pruner_task"] = task
        logging.info("Started session pruner task (interval=%s seconds)", _SESSION_PRUNE_INTERVAL)

    if job_manager_mod and _JOB_TTL_SECONDS > 0:
        task = asyncio.create_task(_job_pruner_loop(job_manager_mod))
        app["_job_pruner_task"] = task
        logging.info("Started job pruner task (ttl=%s seconds, interval=%s seconds)", _JOB_TTL_SECONDS, _JOB_PRUNE_INTERVAL)

    if job_manager_mod:
        if _JOB_TTL_SECONDS <= 0:
            logging.info("Automatic terminal job retention is disabled")

        task = asyncio.create_task(_active_job_reconciler_loop(job_manager_mod))
        app["_active_job_reconciler_task"] = task
        logging.info(
            "Started active job reconciler (grace=%s seconds, interval=%s seconds)",
            _ACTIVE_RECONCILE_GRACE_SECONDS,
            _ACTIVE_RECONCILE_INTERVAL,
        )

        # Start queue status publisher
        task = asyncio.create_task(_queue_status_publisher_loop(job_manager_mod))
        app["_queue_status_publisher_task"] = task
        logging.info("Started queue status publisher task (interval=%s seconds)", _QUEUE_STATUS_INTERVAL)

    app["_workflow_runner_bg_started"] = True

async def stop_background_tasks(app: Any) -> None:
    """
    Asynchronously stop background tasks that were started by start_background_tasks.
    This function cancels and awaits the completion of the session pruner task and job pruner task
    stored in the provided app object. It also removes the background tasks started flag from the app.

    Args:
        app (Any): The application object (e.g., a FastAPI app) that holds the background tasks
                   in its attributes, such as '_session_pruner_task', '_job_pruner_task', and
                   '_workflow_runner_bg_started'.

    Returns:
        None
    """
    task = app.pop("_session_pruner_task", None)
    if task is not None:
        task.cancel()
        try:
            await task
        except Exception:
            pass
        logging.info("Stopped session pruner task")

    task = app.pop("_job_pruner_task", None)
    if task is not None:
        task.cancel()
        try:
            await task
        except Exception:
            pass
        logging.info("Stopped job pruner task")

    task = app.pop("_active_job_reconciler_task", None)
    if task is not None:
        task.cancel()
        try:
            await task
        except Exception:
            pass
        logging.info("Stopped active job reconciler")

    task = app.pop("_queue_status_publisher_task", None)
    if task is not None:
        task.cancel()
        try:
            await task
        except Exception:
            pass
        logging.info("Stopped queue status publisher task")

    app.pop("_workflow_runner_bg_started", None)
    logging.info("Workflow-runner background tasks stopped")
# endregion
