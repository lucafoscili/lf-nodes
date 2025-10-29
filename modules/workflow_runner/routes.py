import asyncio
import execution
import json
import logging
import os
import time
import uuid

from aiohttp import web
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Tuple
from server import PromptServer

from .config import CONFIG as RUNNER_CONFIG
from .job_manager import JobStatus, create_job, get_job, set_job_status
from .registry import InputValidationError, WorkflowNode, get_workflow, list_workflows
from ..utils.constants import API_ROUTE_PREFIX, NOT_FND_HTML
from ..utils.helpers.conversion import json_safe
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
    _SESSION_STORE,
)
import base64
import time as _time

# Executor helpers (moved out of routes.py)
from .services.executor import (
    execute_workflow,
    _prepare_workflow_execution,
    _make_run_payload,
    _sanitize_history,
    _wait_for_completion,
    WorkflowPreparationError,
)

# Authentication helpers moved to auth.py

# Authentication helpers moved to auth.py

# Dev dotenv loader: load `.env` for local dev. The loader will run if either:
#  - DEV_ENV=1 is already set in the environment, OR
#  - a .env file exists next to this module (convenience for local dev).
try:
    env_path = Path(__file__).parent / ".env"
    should_load = os.environ.get("DEV_ENV") == "1" or env_path.exists()
    if should_load and env_path.exists():
        # lightweight loader to avoid adding a runtime dependency
        for line in env_path.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue
            k, v = line.split('=', 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k and not os.environ.get(k):
                os.environ[k] = v
except Exception:
    logging.exception('Failed to load local .env')

DEPLOY_ROOT = RUNNER_CONFIG.deploy_root
WORKFLOW_RUNNER_ROOT = RUNNER_CONFIG.runner_root
SHARED_JS_ROOT = RUNNER_CONFIG.shared_js_root

ASSET_SEARCH_ROOTS = (
    RUNNER_CONFIG.deploy_root,
    RUNNER_CONFIG.runner_root,
)

WORKFLOW_STATIC_ROOTS = (RUNNER_CONFIG.runner_root,)
WORKFLOW_HTML = RUNNER_CONFIG.workflow_html

# Helpers moved to smaller modules:
from .helpers import _emit_run_progress
from .assets import _serve_first_existing


# Catch-all protections: deny any other API paths not explicitly handled.
# This provides a defense-in-depth layer in case the port is exposed.
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

def _emit_run_progress(run_id: str, message: str, **extra: Any) -> None:
    payload = {"run_id": run_id, "message": message}
    if extra:
        payload.update(extra)
    try:
        PromptServer.instance.send_sync("lf-runner:progress", payload)
    except Exception:
        logging.exception("Failed to send progress event for run %s", run_id)


# Execution helpers have been moved to `services.executor`.

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
                # schedule as a task on the server loop if available
                PromptServer.instance.loop.create_task(_background.start_background_tasks(app))
            except Exception:
                # fallback: create a local asyncio task
                asyncio.create_task(_background.start_background_tasks(app))
        except Exception:
            # best-effort only; don't fail the request if background startup fails
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
                            // redirect to the runner page so the browser performs a full navigation
                            // and includes the LF_SESSION cookie the server just set.
                            // Use origin to ensure an absolute navigation and force reload.
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
            # Build absolute login_uri for Google's GSI. Use forwarded host when available.
            host = request.headers.get('Host') or getattr(request, 'host', '')
            xf_proto = request.headers.get('X-Forwarded-Proto')
            if xf_proto:
                proto = xf_proto
            else:
                # prefer https when serving through common tunnel hosts
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
    if not _ENABLE_GOOGLE_OAUTH:
        return web.json_response({"detail": "oauth_not_enabled"}, status=400)

    try:
        # Read raw body for debugging as well; aiohttp's request.json() will consume the body
        raw = await request.read()
        try:
            body = json.loads(raw.decode('utf-8')) if raw else {}
        except Exception:
            body = None
    except Exception:
        return web.json_response({"detail": "invalid_json"}, status=400)

    if _WF_DEBUG:
        try:
            logging.debug("Verify request headers: %s", dict(request.headers))
            logging.debug("Verify raw body: %s", raw.decode('utf-8', errors='replace'))
        except Exception:
            logging.exception("Failed to log verify request for debug")

    id_token = body.get("id_token") if isinstance(body, dict) else None
    if not id_token:
        return web.json_response({"detail": "missing_id_token"}, status=400)

    ok, email = await _verify_token_and_email(id_token)
    if not ok:
        if _WF_DEBUG:
            # try to provide a bit more detail when in debug mode
            return web.json_response({"detail": "invalid_token_or_forbidden", "debug": "token_verification_failed"}, status=401)
        return web.json_response({"detail": "invalid_token_or_forbidden"}, status=401)

    # Create a server-side session and set an opaque session cookie (LF_SESSION).
    try:
        session_id, expires_at = create_server_session(email)
    except Exception:
        logging.exception("Failed to create session in store")
        return web.json_response({"detail": "server_error"}, status=500)
        return web.json_response({"detail": "server_error"}, status=500)

    resp = web.json_response({"detail": "ok"})
    try:
        # Use secure flag when the request is over HTTPS. For local dev this may be False.
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
        # If an old LF_AUTH cookie exists, attempt to clear it for hygiene.
        if request.cookies.get('LF_AUTH'):
            resp.del_cookie('LF_AUTH')
    except Exception:
        logging.exception("Failed to set session cookie")

    return resp


# Debug-only quick login to create a test session (only when WORKFLOW_RUNNER_DEBUG=1).
@PromptServer.instance.routes.post(f"{API_ROUTE_PREFIX}/workflow-runner/debug-login")
async def route_workflow_runner_debug_login(request: web.Request) -> web.Response:
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

# region Run
@PromptServer.instance.routes.post(f"{API_ROUTE_PREFIX}/run")
async def route_run_workflow(request: web.Request) -> web.Response:
    # enforce google oauth if enabled
    if _ENABLE_GOOGLE_OAUTH:
        auth_resp = await _require_auth(request)
        if isinstance(auth_resp, web.Response):
            return auth_resp
    try:
        payload = await request.json()
    except Exception as exc:
        logging.warning("Failed to parse workflow request payload: %s", exc)
        return web.json_response(
            _make_run_payload(detail=str(exc), error_message="invalid_json"),
            status=400,
        )

    if not isinstance(payload, dict):
        return web.json_response(
            _make_run_payload(detail="Payload must be a JSON object.", error_message="invalid_payload"),
            status=400,
        )

    try:
        prepared = _prepare_workflow_execution(payload)
    except WorkflowPreparationError as exc:
        return web.json_response(exc.response_body, status=exc.status)

    run_id = str(uuid.uuid4())
    await create_job(run_id)
    _emit_run_progress(run_id, "workflow_received")

    async def worker() -> None:
        try:
            await set_job_status(run_id, JobStatus.RUNNING)
            _emit_run_progress(run_id, "workflow_started")

            job_status, response_body, http_status = await execute_workflow(payload, run_id, prepared)
            job_result = {"http_status": http_status, "body": response_body}

            await set_job_status(run_id, job_status, result=job_result)
            _emit_run_progress(run_id, "workflow_completed", status=job_status.value)
        except asyncio.CancelledError:
            await set_job_status(run_id, JobStatus.CANCELLED, error="cancelled")
            _emit_run_progress(run_id, "workflow_cancelled")
            raise
        except Exception as exc:
            logging.exception("Workflow run %s failed unexpectedly: %s", run_id, exc)
            error_payload = _make_run_payload(detail=str(exc), error_message="unhandled_exception")
            job_result = {"http_status": 500, "body": error_payload}
            await set_job_status(run_id, JobStatus.FAILED, error=str(exc), result=job_result)
            _emit_run_progress(run_id, "workflow_failed", error=str(exc))

    PromptServer.instance.loop.create_task(worker())

    return web.json_response({"run_id": run_id}, status=202)


@PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/run/{{run_id}}/status")
async def route_run_status(request: web.Request) -> web.Response:
    # require auth for run status
    if _ENABLE_GOOGLE_OAUTH:
        auth_resp = await _require_auth(request)
        if isinstance(auth_resp, web.Response):
            return auth_resp

    run_id = request.match_info.get("run_id")
    if not run_id:
        raise web.HTTPNotFound(text="Unknown run id")

    job = await get_job(run_id)
    if job is None:
        raise web.HTTPNotFound(text="Unknown run id")

    is_terminal = job.status in {JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED}
    payload = {
        "run_id": job.id,
        "status": job.status.value,
        "created_at": job.created_at,
        "error": job.error,
        "result": job.result if is_terminal else None,
    }
    return web.json_response(payload)
# endregion

# Static asset routes moved to assets.py

# region List workflows
@PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/workflows")
async def route_list_workflows(_: web.Request) -> web.Response:
    # require auth for listing workflows
    if _ENABLE_GOOGLE_OAUTH:
        auth_resp = await _require_auth(_)
        if isinstance(auth_resp, web.Response):
            return auth_resp
    return web.json_response({"workflows": list_workflows()})
# endregion

# region Get workflow
@PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/workflows/{{workflow_id}}")
async def route_get_workflow(request: web.Request) -> web.Response:
    workflow_id = request.match_info.get('workflow_id')
    if not workflow_id:
        return web.Response(status=400, text='Missing workflow_id')
    # require auth for getting a workflow
    if _ENABLE_GOOGLE_OAUTH:
        auth_resp = await _require_auth(request)
        if isinstance(auth_resp, web.Response):
            return auth_resp

    workflow = get_workflow(workflow_id)
    if not workflow:
        return web.Response(status=404, text='Workflow not found')
    
    try:
        with workflow.workflow_path.open("r", encoding="utf-8") as workflow_file:
            workflow_json = json.load(workflow_file)
        return web.json_response(workflow_json)
    except Exception as e:
        logging.exception(f"Error loading workflow {workflow_id}")
        return web.Response(status=500, text=f'Error loading workflow: {str(e)}')
# endregion


# NOTE: session pruner implementation was moved to `services/background.py`.
# Lifecycle is started on-demand when the workflow-runner page is first accessed.
