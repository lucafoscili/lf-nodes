import asyncio
import json
import logging

from aiohttp import web

from ..services.auth_service import _ENABLE_GOOGLE_OAUTH, _require_auth
from ..services.executor import WorkflowPreparationError
from ..services.job_service import get_job_status
from ..services.run_service import run_workflow
from ..services.workflow_service import list_workflows as svc_list_workflows, get_workflow_content
from ..services.auth_service import (
    create_server_session,
    _verify_token_and_email,
    _WF_DEBUG,
    _SESSION_TTL,
)
from ..services import job_store

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
    if _ENABLE_GOOGLE_OAUTH:
        auth_resp = await _require_auth(request)
        if isinstance(auth_resp, web.Response):
            return auth_resp
    try:
        payload = await request.json()
    except Exception:
        return web.json_response({"detail": "invalid_json"}, status=400)

    if not isinstance(payload, dict):
        return web.json_response({"detail": "invalid_payload"}, status=400)

    try:
        result = await run_workflow(payload)
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
    payloads produced by `job_store`. The client should send an `Accept:` or
    simply open an EventSource to this endpoint.
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

    await resp.prepare(request)

    q = job_store.subscribe_events()

    try:
        # send an initial comment to establish the stream
        await resp.write(b": connected\n\n")

        while True:
            try:
                event = await q.get()
            except asyncio.CancelledError:
                break

            if event is None:
                # sentinel to close
                break

            data = json.dumps(event)
            payload = f"event: run\ndata: {data}\n\n".encode('utf-8')
            try:
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
            samesite="Lax",
            secure=bool(secure_flag),
        )
        if request.cookies.get('LF_AUTH'):
            resp.del_cookie('LF_AUTH')
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
        resp.set_cookie("LF_SESSION", session_id, max_age=_SESSION_TTL, httponly=True, samesite="Lax", secure=True)
    except Exception:
        logging.exception("Failed to set debug session cookie")
    return resp
# endregion