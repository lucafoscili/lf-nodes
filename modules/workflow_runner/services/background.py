import asyncio
import logging
import time

from typing import Any

from ..config import get_settings

_settings = get_settings()

# region Pruner configuration
_JOB_TTL_SECONDS = int(_settings.JOB_TTL_SECONDS or 300)
_JOB_PRUNE_INTERVAL = int(_settings.JOB_PRUNE_INTERVAL_SECONDS or 60)
_SESSION_PRUNE_INTERVAL = int(_settings.SESSION_PRUNE_INTERVAL_SECONDS or 60)
_QUEUE_STATUS_INTERVAL = 1  # Send queue updates every second
# endregion

# region Helpers
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

async def _job_pruner_loop(job_manager_module) -> None:
    try:
        while True:
            try:
                now = time.time()
                try:
                    jobs = await job_manager_module.list_jobs()
                except Exception:
                    logging.exception("Failed to list jobs for pruning")
                    jobs = {}

                to_remove = []
                for jid, job in jobs.items():
                    if job.status in {job_manager_module.JobStatus.SUCCEEDED, job_manager_module.JobStatus.FAILED, job_manager_module.JobStatus.CANCELLED}:
                        if (job.created_at + _JOB_TTL_SECONDS) <= now:
                            to_remove.append(jid)

                for jid in to_remove:
                    try:
                        await job_manager_module.remove_job(jid)
                    except Exception:
                        logging.exception("Failed to remove job %s during pruning", jid)

                if to_remove:
                    logging.debug("Job pruner removed %d jobs", len(to_remove))
            except Exception:
                logging.exception("Error during job prune")
            await asyncio.sleep(_JOB_PRUNE_INTERVAL)
    except asyncio.CancelledError:
        logging.debug("Job pruner cancelled")

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
        - If 'job_manager' module is available, starts a job pruner task that runs at intervals
          defined by _JOB_PRUNE_INTERVAL, with job TTL defined by _JOB_TTL_SECONDS.
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

    if job_manager_mod:
        task = asyncio.create_task(_job_pruner_loop(job_manager_mod))
        app["_job_pruner_task"] = task
        logging.info("Started job pruner task (ttl=%s seconds, interval=%s seconds)", _JOB_TTL_SECONDS, _JOB_PRUNE_INTERVAL)

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