import asyncio
import json
import logging
import os
import uuid
from pathlib import Path
from typing import Any

from aiohttp import web

from server import PromptServer

from .config import CONFIG as RUNNER_CONFIG
from .job_manager import JobStatus, create_job, get_job, set_job_status
from .registry import get_workflow, list_workflows
from ..utils.constants import API_ROUTE_PREFIX, NOT_FND_HTML
from .auth import (
    _ENABLE_GOOGLE_OAUTH,
    _require_auth,
    _WF_DEBUG,
    create_server_session,
    _extract_token_from_request,
    _verify_session,
    _verify_token_and_email,
    _GOOGLE_CLIENT_IDS,
    _SESSION_TTL,
)

# Executor helpers
from .services.executor import (
    execute_workflow,
    _prepare_workflow_execution,
    _make_run_payload,
    WorkflowPreparationError,
)

# Helpers / assets
from .helpers import _emit_run_progress
from .assets import _serve_first_existing
from .controllers import api_controllers


DEPLOY_ROOT = RUNNER_CONFIG.deploy_root
WORKFLOW_RUNNER_ROOT = RUNNER_CONFIG.runner_root
WORKFLOW_STATIC_ROOTS = (RUNNER_CONFIG.runner_root,)
WORKFLOW_HTML = RUNNER_CONFIG.workflow_html


# Catch-all protections: deny any other API paths not explicitly handled.
@PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/{{path:.*}}")
async def route_api_catch_all_get(request: web.Request) -> web.Response:
    path = request.path
    # allow the workflow-runner page and verify endpoint to be publicly reachable
    if path.startswith(f"{API_ROUTE_PREFIX}/workflow-runner") or path.endswith("/verify"):
        # Not handled here; return 404 so more specific routes can match if present
        return web.Response(status=404, text="Not found")

    logging.info("Denied unauthenticated GET to %s", path)
    return web.json_response({"detail": "forbidden"}, status=403)


@PromptServer.instance.routes.post(f"{API_ROUTE_PREFIX}/{{path:.*}}")
async def route_api_catch_all_post(request: web.Request) -> web.Response:
    path = request.path
    # allow verify post to be processed
    if path.endswith("/verify"):
        return web.Response(status=404, text="Not found")

    logging.info("Denied unauthenticated POST to %s", path)
    return web.json_response({"detail": "forbidden"}, status=403)


# region Workflow runner page
@PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/workflow-runner")
async def route_workflow_runner_page(request: web.Request) -> web.Response:
    try:
        # Lazily start background tasks (pruners) the first time the runner page
        # is accessed so we don't run background work for users who never use it.
        try:
            from .services import background as _background
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
                ok, _email = await _verify_session(token)
                if not ok:
                    ok, _email = await _verify_token_and_email(token)
                if ok:
                    response = _serve_first_existing((WORKFLOW_HTML,))
                    if response is not None:
                        return response

            # serve the login splash page
            client_id_val = _GOOGLE_CLIENT_IDS[0] if _GOOGLE_CLIENT_IDS else ''
            login_template = '''<!doctype html>
<html>
    <head>
        <meta charset="utf-8" />
        <title>Login</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <script src="https://accounts.google.com/gsi/client" async defer></script>
        <style>body{font-family: Arial, sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;margin:0}.card{padding:24px;border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,0.1);text-align:center}</style>
    </head>
    <body>
        <div class="card">
            <h2>Sign in to continue</h2>
            <div id="g_id_onload"
                     data-client_id="{CLIENT_ID}"
                     data-login_uri="{LOGIN_URI}"
                     data-auto_prompt="false">
            </div>
            <div class="g_id_signin" data-type="standard" data-shape="rectangular"></div>
            <p id="message"></p>
        </div>
        <script>
            function handleCredentialResponse(response) {
                var id_token = response.credential;
                fetch('/api/lf-nodes/workflow-runner/verify', {
                    method: 'POST',
                    credentials: 'include',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({id_token: id_token})
                }).then(function(r) {
                    if (r.ok) {
                            setTimeout(function(){
                                window.location.href = window.location.origin + '/api/lf-nodes/workflow-runner';
                            }, 150);
                        } else {
                        r.json().then(function(j){ document.getElementById('message').innerText = j.detail || 'Login failed'; }).catch(function(){ document.getElementById('message').innerText = 'Login failed'; });
                    }
                }).catch(function(e){ document.getElementById('message').innerText = 'Network error'; });
            }
            window.handleCredentialResponse = handleCredentialResponse;
            window.onload = function(){
                if (window.google && google.accounts && google.accounts.id) {
                    google.accounts.id.initialize({client_id: "{CLIENT_ID}", callback: handleCredentialResponse});
                    google.accounts.id.renderButton(document.querySelector('.g_id_signin'), {theme: 'outline', size: 'large'});
                } else {
                    document.getElementById('message').innerText = 'Google Identity SDK not available.';
                }
            }
        </script>
    </body>
</html>'''
            host = request.headers.get('Host') or getattr(request, 'host', '')
            xf_proto = request.headers.get('X-Forwarded-Proto')
            if xf_proto:
                proto = xf_proto
            else:
                proto = 'https' if host and ('devtunnels.ms' in host or host.endswith('.trycloudflare.com')) else request.scheme

            login_uri = f"{proto}://{host}/api/lf-nodes/workflow-runner/verify"
            login_html = login_template.replace('{CLIENT_ID}', client_id_val).replace('{LOGIN_URI}', login_uri)
            return web.Response(text=login_html, content_type='text/html')
        else:
            response = _serve_first_existing((WORKFLOW_HTML,))
            if response is not None:
                return response
    except Exception:
        pass

    return web.Response(text=NOT_FND_HTML, content_type="text/html", status=404)
# endregion



# Endpoint the client-side login splash posts to with the Google id_token.
@PromptServer.instance.routes.post(f"{API_ROUTE_PREFIX}/workflow-runner/verify")
async def route_workflow_runner_verify(request: web.Request) -> web.Response:
    # Delegate to controller which contains the logic and cookie handling
    return await api_controllers.verify_controller(request)


# Debug-only quick login to create a test session (only when WORKFLOW_RUNNER_DEBUG=1).
@PromptServer.instance.routes.post(f"{API_ROUTE_PREFIX}/workflow-runner/debug-login")
async def route_workflow_runner_debug_login(request: web.Request) -> web.Response:
    return await api_controllers.debug_login_controller(request)


# region Run
@PromptServer.instance.routes.post(f"{API_ROUTE_PREFIX}/run")
async def route_run_workflow(request: web.Request) -> web.Response:
    # Delegate to the new controller while preserving the route registration.
    return await api_controllers.start_workflow_controller(request)


@PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/run/{{run_id}}/status")
async def route_run_status(request: web.Request) -> web.Response:
    # Delegate to controller for status lookup.
    return await api_controllers.get_workflow_status_controller(request)
# endregion


# region List workflows
@PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/workflows")
async def route_list_workflows(_: web.Request) -> web.Response:
    # Delegate to controller which handles auth and service call
    return await api_controllers.list_workflows_controller(_)
# endregion


# region Get workflow
@PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/workflows/{{workflow_id}}")
async def route_get_workflow(request: web.Request) -> web.Response:
    return await api_controllers.get_workflow_controller(request)
# endregion
