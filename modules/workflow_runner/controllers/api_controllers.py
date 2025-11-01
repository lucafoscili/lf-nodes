import asyncio
import json
import logging

from aiohttp import web

from ..services.auth_service import (
    create_server_session,
    _require_auth,
    _verify_token_and_email,
    _ENABLE_GOOGLE_OAUTH,
    _WF_DEBUG,
    _SESSION_TTL,
)
from ..services.executor import WorkflowPreparationError
from ..services.job_service import get_job_status
from ..services import job_store
from ..services.run_service import run_workflow
from ..services.workflow_service import list_workflows as svc_list_workflows, get_workflow_content

# region Helpers
async def _send_initial_snapshot(resp: web.Response, subscriber_owner: str | None = None, last_event: tuple[str, int] | None = None) -> None:
        """
        Send an initial snapshot of active (pending or running) jobs to the SSE client.

        This function retrieves all jobs from the job store, filters for those with
        statuses PENDING or RUNNING, and sends each as an event to the client via
        Server-Sent Events (SSE). It ensures clients receive the current state before
        live events. If the client disconnects during sending, it stops gracefully.
        Handles exceptions for connection issues and general failures.

        Returns:
            None

        Raises:
            Logs exceptions for failures in building or sending the snapshot.
        """
        try:
            jobs = await job_store.list_jobs()
            for job in jobs.values():
                # only include runs that are active (pending or running)
                if job.status in (job_store.JobStatus.PENDING, job_store.JobStatus.RUNNING):
                    owner = getattr(job, "owner_id", None)
                    # owner filtering: if subscriber_owner is set, only send matching owner events
                    if subscriber_owner and owner and owner != subscriber_owner:
                        continue
                    # honor Last-Event-ID: if the client supplied last_event and the
                    # job matches that run and its seq is <= the last seen seq,
                    # skip sending the snapshot for that run to avoid duplicates.
                    if last_event is not None:
                        try:
                            last_run_id, last_seq = last_event
                            jid = getattr(job, "id", getattr(job, "run_id", None))
                            if jid == last_run_id and (getattr(job, "seq", 0) or 0) <= last_seq:
                                continue
                        except Exception:
                            # if parsing fails, be conservative and send the snapshot
                            pass
                    seq = getattr(job, "seq", 0) or 0
                    event = {
                        "id": f"{getattr(job, 'id', getattr(job, 'run_id', None))}:{seq}",
                        "run_id": getattr(job, "id", getattr(job, "run_id", None)),
                        "status": job.status.value if hasattr(job.status, "value") else str(job.status),
                        "created_at": getattr(job, "created_at", None),
                        "error": getattr(job, "error", None),
                        "result": getattr(job, "result", None)
                        if (getattr(job, "status", None) in (job_store.JobStatus.SUCCEEDED, job_store.JobStatus.FAILED, job_store.JobStatus.CANCELLED))
                        else None,
                        "owner_id": owner,
                        "seq": seq,
                    }
                    try:
                        data = json.dumps(event)
                        event_type = "queue" if event.get("type") == "queue_status" else "run"
                        event_id = event.get("id")
                        payload = f"id: {event_id}\nevent: {event_type}\ndata: {data}\n\n".encode("utf-8")
                        await resp.write(payload)
                        await resp.drain()
                    except (ConnectionResetError, asyncio.CancelledError):
                        # client disconnected while sending snapshot
                        break
                    except Exception:
                        logging.exception("Failed to send snapshot event to SSE client")
        except Exception:
            logging.exception("Failed to build/send run snapshot for SSE client")
# endregion

# region Start
async def start_workflow_controller(request: web.Request) -> web.Response:
    """
    Asynchronous controller for starting a workflow via API request.
    This function handles incoming requests to initiate a workflow execution. It first checks for
    authentication if Google OAuth is enabled. It then parses and validates the JSON payload from
    the request, ensuring it is a dictionary. The workflow is executed asynchronously, and the
    result is returned as a JSON response with a 202 status code.
    If the payload is invalid JSON or not a dictionary, appropriate error responses are returned.
    WorkflowPreparationError exceptions are handled by bubbling up the prepared response body
    and status. Other exceptions result in a generic service error response.

    Args:
        request (web.Request): The incoming web request containing the workflow payload.

    Returns:
        web.Response: A JSON response with the workflow result or an error message.
    """
    owner_id = None
    if _ENABLE_GOOGLE_OAUTH:
        auth_resp = await _require_auth(request)
        if isinstance(auth_resp, web.Response):
            return auth_resp
        # derive opaque owner id from the authenticated email (or subject)
        try:
            subj = request.get('google_oauth_email') if isinstance(request, dict) else getattr(request, 'google_oauth_email', None)
            from ..services.auth_service import derive_owner_id

            owner_id = derive_owner_id(subj or "")
        except Exception:
            owner_id = None
    try:
        payload = await request.json()
    except Exception:
        return web.json_response({"detail": "invalid_json"}, status=400)

    if not isinstance(payload, dict):
        return web.json_response({"detail": "invalid_payload"}, status=400)

    try:
        result = await run_workflow(payload, owner_id=owner_id)
        return web.json_response(result, status=202)
    except WorkflowPreparationError as exc:
        # Bubble the prepared response body and status (matches previous behaviour)
        return web.json_response(exc.response_body, status=exc.status)
    except Exception as exc:
        return web.json_response({"detail": "service_error", "error": str(exc)}, status=500)
# endregion

# region Status
async def get_workflow_status_controller(request: web.Request) -> web.Response:
    """
    Asynchronous controller to retrieve the status of a workflow run.

    This function handles GET requests to fetch the status of a specific workflow run
    identified by its run_id. It validates the presence of the run_id, queries the job
    status, and returns it as a JSON response. If the run_id is missing or unknown,
    appropriate HTTP errors are raised.

    Args:
        request (web.Request): The incoming web request containing the run_id in the URL match info.

    Returns:
        web.Response: A JSON response containing the workflow status.

    Raises:
        web.HTTPBadRequest: If the run_id is not provided in the request.
        web.HTTPNotFound: If the run_id does not correspond to any known job.
    """
    run_id = request.match_info.get("run_id")
    if not run_id:
        raise web.HTTPBadRequest(text="Missing run_id")
    status = await get_job_status(run_id)
    if status is None:
        raise web.HTTPNotFound(text="Unknown run id")
    return web.json_response(status)
# endregion

# region Events (SSE)
async def stream_runs_controller(request: web.Request) -> web.Response:
    """
    Server-Sent Events endpoint streaming job status updates.

    Each connected client receives events of shape matching the job status
    payloads produced by `job_store`. The client should open an EventSource to this endpoint.
    """
    # Optional auth for SSE — re-use existing auth flow if enabled.
    if _ENABLE_GOOGLE_OAUTH:
        auth_resp = await _require_auth(request)
        if isinstance(auth_resp, web.Response):
            return auth_resp

    resp = web.StreamResponse(status=200, reason='OK')
    resp.content_type = 'text/event-stream'
    resp.headers['Cache-Control'] = 'no-cache'
    resp.headers['Connection'] = 'keep-alive'

    # examine Last-Event-ID header for resume semantics. Expect format '<run_id>:<seq>'
    last_event_header = request.headers.get("Last-Event-ID")
    last_event: tuple[str, int] | None = None
    if last_event_header:
        try:
            parts = last_event_header.split(":", 1)
            if len(parts) == 2:
                last_event = (parts[0], int(parts[1]))
        except Exception:
            last_event = None

    await resp.prepare(request)

    q = job_store.subscribe_events()

    # Determine subscriber owner if auth is enabled so snapshot can be filtered
    subscriber_owner = None
    if _ENABLE_GOOGLE_OAUTH:
        try:
            subj = request.get('google_oauth_email') if isinstance(request, dict) else getattr(request, 'google_oauth_email', None)
            from ..services.auth_service import derive_owner_id

            subscriber_owner = derive_owner_id(subj or "")
        except Exception:
            subscriber_owner = None

    try:
        await resp.write(b": connected\n\n")

        # Send an initial queue status snapshot so freshly connected clients
        # see the server queue state immediately (avoids UI showing a 'down'
        # indicator when nothing else is occurring). Use the background
        # helper to keep HTTP queue-fetching logic in one place (SoC).
        try:
            from ..services import background as _bg

            qinfo = await _bg.fetch_queue_status()
            if qinfo is not None:
                qevent = {"type": "queue_status", "pending": qinfo.get("pending", 0), "running": qinfo.get("running", 0)}
                try:
                    data = json.dumps(qevent)
                    # allow event id to be None; controller will normalize
                    payload = f"id: {qevent.get('id')}\nevent: queue\ndata: {data}\n\n".encode("utf-8")
                    await resp.write(payload)
                    await resp.drain()
                except (ConnectionResetError, asyncio.CancelledError):
                    pass
                except Exception:
                    logging.exception("Failed to write initial queue_status to SSE client")
        except Exception:
            # keep SSE path robust; if background helper is unavailable just continue
            logging.debug("Could not fetch/send initial queue status snapshot")

        await _send_initial_snapshot(resp, subscriber_owner, last_event)

        while True:
            try:
                event = await q.get()
            except asyncio.CancelledError:
                break

            if event is None:
                # sentinel to close
                break

            # If the client supplied Last-Event-ID, avoid resending events that
            # are for the same run and have seq <= last_seq. This is a best-effort
            # per-run resume: we don't maintain a global event ordering across runs.
            if last_event is not None:
                try:
                    last_run_id, last_seq = last_event
                    ev_run = event.get("run_id")
                    ev_seq = int(event.get("seq")) if event.get("seq") is not None else None
                    if ev_run is not None and ev_seq is not None:
                        if ev_run == last_run_id and ev_seq <= last_seq:
                            # skip duplicated/older event
                            continue
                except Exception:
                    # fall through and send the event if parsing fails
                    pass

            try:
                # ensure event has a resume-friendly id (run_id:seq) when available
                event_type = "queue" if event.get("type") == "queue_status" else "run"
                event_id = event.get("id") or (f"{event.get('run_id')}:{event.get('seq', 0)}")
                data = json.dumps(event)
                payload = f"id: {event_id}\nevent: {event_type}\ndata: {data}\n\n".encode("utf-8")
                await resp.write(payload)
                await resp.drain()
            except (ConnectionResetError, asyncio.CancelledError):
                break

            # periodic keepalive handled by the event loop if needed
    finally:
        job_store.unsubscribe_events(q)

    return resp
# endregion

# region List
async def list_workflows_controller(request: web.Request) -> web.Response:
    """
    Asynchronous controller for listing workflows.

    Checks for Google OAuth authentication if enabled, and returns an authentication response if required.
    Otherwise, retrieves and returns a JSON response containing the list of workflows.

    Args:
        request (web.Request): The incoming web request object.

    Returns:
        web.Response: A JSON response with the workflows data or an authentication error response.
    """
    if _ENABLE_GOOGLE_OAUTH:
        auth_resp = await _require_auth(request)
        if isinstance(auth_resp, web.Response):
            return auth_resp
    return web.json_response({"workflows": svc_list_workflows()})


async def list_runs_controller(request: web.Request) -> web.Response:
    """GET /workflow-runner/runs?status=pending,running&owner=me&limit=100

    Returns a JSON payload:
      { runs: [ { run_id, status, seq, owner_id?, created_at, updated_at, result?, error? }, ... ] }
    """
    if _ENABLE_GOOGLE_OAUTH:
        auth_resp = await _require_auth(request)
        if isinstance(auth_resp, web.Response):
            return auth_resp

    # parse query params
    status_q = request.query.get("status")
    owner_q = request.query.get("owner")
    limit_q = request.query.get("limit")
    try:
        limit = int(limit_q) if limit_q else 100
    except Exception:
        limit = 100

    statuses = None
    if status_q:
        # allow comma-separated list, server supports single status filter per adapter call;
        # if multiple statuses provided we will fetch all and filter.
        statuses = [s.strip() for s in status_q.split(",") if s.strip()]

    owner_id = None
    if owner_q == "me" and _ENABLE_GOOGLE_OAUTH:
        try:
            subj = request.get('google_oauth_email') if isinstance(request, dict) else getattr(request, 'google_oauth_email', None)
            from ..services.auth_service import derive_owner_id
            owner_id = derive_owner_id(subj or "")
        except Exception:
            owner_id = None
    elif owner_q and owner_q != "me":
        owner_id = owner_q

    runs_out = []
    # If multiple statuses requested, call list_jobs once per status and merge (bounded)
    if statuses:
        seen = set()
        for s in statuses:
            recs = await job_store.list_jobs(owner_id=owner_id, status=s)
            for k, job in recs.items():
                if k in seen:
                    continue
                seen.add(k)
                runs_out.append({
                    "run_id": job.id,
                    "status": job.status.value,
                    "seq": getattr(job, "seq", 0),
                    "owner_id": job.owner_id,
                    "created_at": job.created_at,
                    "updated_at": getattr(job, "updated_at", None),
                    "result": job.result,
                    "error": job.error,
                })
                if len(runs_out) >= limit:
                    break
            if len(runs_out) >= limit:
                break
    else:
        recs = await job_store.list_jobs(owner_id=owner_id, status=None)
        for k, job in recs.items():
            runs_out.append({
                "run_id": job.id,
                "status": job.status.value,
                "seq": getattr(job, "seq", 0),
                "owner_id": job.owner_id,
                "created_at": job.created_at,
                "updated_at": getattr(job, "updated_at", None),
                "result": job.result,
                "error": job.error,
            })
            if len(runs_out) >= limit:
                break

    return web.json_response({"runs": runs_out})
# endregion

# region Get Workflow
async def get_workflow_controller(request: web.Request) -> web.Response:
    """
    Asynchronous handler for retrieving workflow content via API.
    This function processes a GET request to fetch the content of a specific workflow
    identified by its ID. It performs authentication if Google OAuth is enabled,
    validates the workflow ID, and returns the workflow content as a JSON response.

    Args:
        request (web.Request): The incoming web request object containing match info
            for the workflow ID.

    Returns:
        web.Response: A JSON response containing the workflow content if found,
            or an error response (400 for missing ID, 401/403 for auth failure,
            404 if workflow not found).

    Raises:
        None explicitly, but may propagate exceptions from underlying functions
        like _require_auth or get_workflow_content.
    """
    workflow_id = request.match_info.get('workflow_id')
    if not workflow_id:
        return web.Response(status=400, text='Missing workflow_id')
    if _ENABLE_GOOGLE_OAUTH:
        auth_resp = await _require_auth(request)
        if isinstance(auth_resp, web.Response):
            return auth_resp

    content = get_workflow_content(workflow_id)
    if content is None:
        return web.Response(status=404, text='Workflow not found')
    return web.json_response(content)
# endregion

# region Verify
async def verify_controller(request: web.Request) -> web.Response:
    """
    Asynchronous handler for POST /workflow-runner/verify endpoint.
    Validates a Google id_token using existing authentication helpers. On successful validation,
    creates a server session and sets a secure session cookie ("LF_SESSION") in the response.
    Deletes any existing "LF_AUTH" cookie if present. Mirrors original behavior from handlers.py.
    If Google OAuth is not enabled, returns a 400 error with "oauth_not_enabled".
    If the request body is invalid JSON, returns a 400 error with "invalid_json".
    If the id_token is missing, returns a 400 error with "missing_id_token".
    If token verification fails or is forbidden, returns a 401 error with "invalid_token_or_forbidden".
    If session creation fails, returns a 500 error with "server_error".
    On success, returns a 200 JSON response with {"detail": "ok"} and sets the session cookie.

    Args:
        request (web.Request): The incoming web request containing the id_token in the JSON body.

    Returns:
        web.Response: A JSON response indicating success or error, with appropriate status code and cookies set.
    """
    if not _ENABLE_GOOGLE_OAUTH:
        return web.json_response({"detail": "oauth_not_enabled"}, status=400)

    try:
        raw = await request.read()
        try:
            body = json.loads(raw.decode('utf-8')) if raw else {}
        except Exception:
            body = None
    except Exception:
        return web.json_response({"detail": "invalid_json"}, status=400)

    id_token = body.get("id_token") if isinstance(body, dict) else None
    if not id_token:
        return web.json_response({"detail": "missing_id_token"}, status=400)

    ok, email = await _verify_token_and_email(id_token)
    if not ok:
        return web.json_response({"detail": "invalid_token_or_forbidden"}, status=401)

    try:
        session_id, expires_at = create_server_session(email)
    except Exception:
        logging.exception("Failed to create session in store")
        return web.json_response({"detail": "server_error"}, status=500)

    resp = web.json_response({"detail": "ok"})
    try:
        secure_flag = getattr(request, 'secure', None)
        if secure_flag is None:
            secure_flag = (getattr(request, 'scheme', '') == 'https')

        resp.set_cookie(
            "LF_SESSION",
            session_id,
            max_age=_SESSION_TTL,
            httponly=True,
            path="/api/lf-nodes/",
            samesite="Lax",
            secure=bool(secure_flag),
        )
        if request.cookies.get('LF_AUTH'):
            resp.del_cookie('LF_AUTH', path="/api/lf-nodes/")
    except Exception:
        logging.exception("Failed to set session cookie")

    return resp
# endregion

# region Debug Login
async def debug_login_controller(request: web.Request) -> web.Response:
    """
    Asynchronous handler for the POST /workflow-runner/debug-login endpoint.
    This endpoint is only available when the `WORKFLOW_RUNNER_DEBUG` flag is
    enabled (represented in-code as `_WF_DEBUG`). It allows creating a test
    session for debugging purposes. The handler parses the request body for an
    optional 'email' field, defaulting to 'test@example.com' if not provided.
    It then creates a server session using the provided or default email and
    sets an LF_SESSION cookie in the response.

    Parameters:
        request (web.Request): The incoming web request object containing
            the JSON payload with optional 'email' field.

    Returns:
        web.Response: A JSON response indicating success or error.
            - On success: {"detail": "ok", "email": "<email>"}
            - On debug not enabled: {"detail": "not_enabled"} (404)
            - On invalid JSON: {"detail": "invalid_json"} (400)
            - On session creation failure: {"detail": "server_error"} (500)

    Notes:
        - The LF_SESSION cookie is set with httponly=True, samesite="Lax",
          secure=True, and max_age=_SESSION_TTL.
        - Do NOT enable this flag in production environments.
    """
    if not _WF_DEBUG:
        return web.json_response({"detail": "not_enabled"}, status=404)
    try:
        body = await request.json()
    except Exception:
        return web.json_response({"detail": "invalid_json"}, status=400)
    email = (body.get("email") or "test@example.com").lower()
    try:
        session_id, expires_at = create_server_session(email)
    except Exception:
        logging.exception("Failed to create debug session in store")
        return web.json_response({"detail": "server_error"}, status=500)
    resp = web.json_response({"detail": "ok", "email": email})
    try:
        resp.set_cookie("LF_SESSION", session_id, max_age=_SESSION_TTL, httponly=True, path="/api/lf-nodes/", samesite="Lax", secure=True)
    except Exception:
        logging.exception("Failed to set debug session cookie")
    return resp
# endregion