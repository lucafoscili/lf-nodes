import asyncio
import importlib
import logging
from typing import TYPE_CHECKING, cast

from aiohttp import web
from pathlib import Path

from server import PromptServer

from .assets_controller import _serve_first_existing
from ..api_constants import API_ROUTE_PREFIX
from ..config import CONFIG as RUNNER_CONFIG
from ..services.auth_service import (
    _ENABLE_GOOGLE_OAUTH,
    _GOOGLE_CLIENT_IDS,
    _extract_token_from_request,
    _verify_session,
    _verify_token_and_email,
)

if TYPE_CHECKING:
    from . import api_controllers

# region Constants
DEPLOY_ROOT = RUNNER_CONFIG.deploy_root
WORKFLOW_RUNNER_ROOT = RUNNER_CONFIG.runner_root
WORKFLOW_HTML = RUNNER_CONFIG.workflow_html
NOT_FOUND_HTML_PATH = Path(__file__).parent.parent.parent.parent / "web" / "workflow-runner" / "src" / "not-found.html"
LOGIN_HTML_PATH = Path(__file__).parent.parent.parent.parent / "web" / "workflow-runner" / "src" / "login.html"
# endregion

# region Workflow Runner Page
@PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/workflow-runner")
async def route_workflow_runner_page(request: web.Request) -> web.Response:
    try:
        # Lazily start background tasks (pruners) the first time the runner page
        # is accessed so we don't run background work for users who never use it.
        try:
            from ..services import background as _background
            app = PromptServer.instance.app
            try:
                PromptServer.instance.loop.create_task(_background.start_background_tasks(app))
            except Exception:
                asyncio.create_task(_background.start_background_tasks(app))
        except Exception:
            logging.debug("Background starter not available or failed to schedule")

        if _ENABLE_GOOGLE_OAUTH:
            token = _extract_token_from_request(request)
            if token:
                ok, _ = await _verify_session(token)
                if not ok:
                    ok, _ = await _verify_token_and_email(token)
                if ok:
                    response = _serve_first_existing((WORKFLOW_HTML,))
                    if response is not None:
                        return response

            # serve the login splash page
            # prefer canonical auth_service values (avoids importing removed root-level shims)
            client_id_val = _GOOGLE_CLIENT_IDS[0] if (_GOOGLE_CLIENT_IDS and len(_GOOGLE_CLIENT_IDS) > 0) else ''

            host = request.headers.get('Host') or getattr(request, 'host', '')
            xf_proto = request.headers.get('X-Forwarded-Proto')
            if xf_proto:
                proto = xf_proto
            else:
                proto = 'https' if host and ('devtunnels.ms' in host or host.endswith('.trycloudflare.com')) else request.scheme

            login_uri = f"{proto}://{host}/api/lf-nodes/workflow-runner/verify"
            try:
                login_template = LOGIN_HTML_PATH.read_text(encoding='utf-8')
                login_html = login_template.replace('{CLIENT_ID}', client_id_val).replace('{LOGIN_URI}', login_uri)
            except Exception:
                login_html = "<html><body><h1>Login Required</h1><p>Error loading login page.</p></body></html>"
            return web.Response(text=login_html, content_type='text/html')
        else:
            response = _serve_first_existing((WORKFLOW_HTML,))
            if response is not None:
                return response
    except Exception:
        pass

    try:
        not_found_html = NOT_FOUND_HTML_PATH.read_text(encoding='utf-8')
    except Exception:
        not_found_html = "<html><body><h1>Workflow Runner Not Found</h1><p>Error loading not-found page.</p></body></html>"
    return web.Response(text=not_found_html, content_type="text/html", status=404)
# endregion

# region Verify Endpoint
@PromptServer.instance.routes.post(f"{API_ROUTE_PREFIX}/workflow-runner/verify")
async def route_workflow_runner_verify(request: web.Request) -> web.Response:
    api_controllers = cast("api_controllers", importlib.import_module("lf_nodes.modules.workflow_runner.controllers.api_controllers"))
    return await api_controllers.verify_controller(request)
# endregion

# region Debug Login Endpoint
@PromptServer.instance.routes.post(f"{API_ROUTE_PREFIX}/workflow-runner/debug-login")
async def route_workflow_runner_debug_login(request: web.Request) -> web.Response:
    api_controllers = cast("api_controllers", importlib.import_module("lf_nodes.modules.workflow_runner.controllers.api_controllers"))
    return await api_controllers.debug_login_controller(request)
# endregion