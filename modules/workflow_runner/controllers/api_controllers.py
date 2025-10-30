"""API controllers for the workflow_runner miniapp.

These are thin adapters between the aiohttp request/response objects and the
service layer. Keep them small: validate/deserialize input, call services,
and translate exceptions into HTTP responses.
"""
from typing import Any, Dict

from aiohttp import web

from ..services.run_service import run_workflow
from ..services.job_service import get_job_status
from ..services.executor import WorkflowPreparationError
from ..services.workflow_service import list_workflows as svc_list_workflows, get_workflow_content
from ..auth import _ENABLE_GOOGLE_OAUTH, _require_auth
import json
import logging

from ..auth import (
    create_server_session,
    _extract_token_from_request,
    _verify_token_and_email,
    _verify_session,
    _WF_DEBUG,
    _SESSION_TTL,
)


async def start_workflow_controller(request: web.Request) -> web.Response:
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


async def get_workflow_status_controller(request: web.Request) -> web.Response:
    run_id = request.match_info.get("run_id")
    if not run_id:
        raise web.HTTPBadRequest(text="Missing run_id")
    status = await get_job_status(run_id)
    if status is None:
        raise web.HTTPNotFound(text="Unknown run id")
    return web.json_response(status)


async def list_workflows_controller(request: web.Request) -> web.Response:
    if _ENABLE_GOOGLE_OAUTH:
        auth_resp = await _require_auth(request)
        if isinstance(auth_resp, web.Response):
            return auth_resp
    return web.json_response({"workflows": svc_list_workflows()})


async def get_workflow_controller(request: web.Request) -> web.Response:
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


# Auth endpoints (moved from handlers.py)
async def verify_controller(request: web.Request) -> web.Response:
    """Handle POST /workflow-runner/verify

    Validates a Google id_token via existing auth helpers and sets a session
    cookie on success. Mirrors original behaviour in handlers.py.
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


async def debug_login_controller(request: web.Request) -> web.Response:
    """Handle POST /workflow-runner/debug-login

    Only enabled when _WF_DEBUG is True. Creates a test session for the
    supplied email (or default) and sets an LF_SESSION cookie.
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
