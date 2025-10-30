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
