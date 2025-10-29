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
from .google_oauth import verify_id_token_with_google, load_allowed_users_from_file
import base64
import asyncio
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

# Google OAuth opt-in configuration (read at import)
_ENABLE_GOOGLE_OAUTH = os.environ.get("ENABLE_GOOGLE_OAUTH", "").lower() in ("1", "true", "yes")
_ALLOWED_USERS_FILE = os.environ.get("ALLOWED_USERS_FILE", "")
_ALLOWED_USERS_ENV = os.environ.get("ALLOWED_USERS", "")
# strip surrounding quotes if present and split on commas
_GOOGLE_CLIENT_IDS = [s.strip().strip("'\"") for s in os.environ.get("GOOGLE_CLIENT_IDS", "").split(",") if s.strip()]

# Simple in-memory token cache: id_token -> (email, expires_at)
_TOKEN_CACHE: dict[str, tuple[str, float]] = {}
_TOKEN_CACHE_TTL = int(os.environ.get("GOOGLE_IDTOKEN_CACHE_SECONDS", "300"))

# Require explicit allowlist? If true and no allowed users are configured, logins will be denied.
_REQUIRE_ALLOWED_USERS = os.environ.get("REQUIRE_ALLOWED_USERS", "1").lower() in ("1", "true", "yes")

# Server-side sessions: session_id -> (email, expires_at)
_SESSION_STORE: dict[str, tuple[str, float]] = {}
_SESSION_TTL = int(os.environ.get("SESSION_TTL_SECONDS", str(_TOKEN_CACHE_TTL)))
# Enable verbose debug for the workflow-runner verify handler
_WF_DEBUG = os.environ.get("WORKFLOW_RUNNER_DEBUG", "0").lower() in ("1", "true", "yes")

def _load_allowed_users() -> set:
    users = set()
    if _ALLOWED_USERS_FILE:
        users.update(load_allowed_users_from_file(_ALLOWED_USERS_FILE))
    if _ALLOWED_USERS_ENV:
        users.update(u.strip().lower() for u in _ALLOWED_USERS_ENV.split(",") if u.strip())
    return users

_ALLOWED_USERS = _load_allowed_users()

async def _verify_token_and_email(id_token: str) -> tuple[bool, str | None]:
    """Verify token (possibly cached) and ensure email is allowed.

    Returns (True, email) on success, (False, None) otherwise.
    """
    if not id_token:
        return False, None

    # check cache
    now = _time.time()
    cached = _TOKEN_CACHE.get(id_token)
    if cached and cached[1] > now:
        return True, cached[0]

    claims = await verify_id_token_with_google(id_token, expected_audiences=_GOOGLE_CLIENT_IDS or None)
    if not claims:
        return False, None

    email = (claims.get("email") or "").lower()
    return True, email


def _extract_token_from_request(request: web.Request) -> str | None:
    # Authorization header
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth.split(" ", 1)[1].strip()
    # fallback: cookie LF_SESSION (server-side session id)
    cookie = request.cookies.get("LF_SESSION")
    if cookie:
        return cookie
    return None


def _cleanup_expired_sessions() -> None:
    now = _time.time()
    to_delete = [s for s, v in _SESSION_STORE.items() if v[1] <= now]
    for s in to_delete:
        _SESSION_STORE.pop(s, None)


async def _verify_session(session_id: str) -> tuple[bool, str | None]:
    if not session_id:
        return False, None
    _cleanup_expired_sessions()
    now = _time.time()
    val = _SESSION_STORE.get(session_id)
    if not val:
        return False, None
    email, exp = val
    if exp <= now:
        try:
            _SESSION_STORE.pop(session_id, None)
        except Exception:
            pass
        return False, None
    return True, email

async def _require_auth(request: web.Request) -> web.Response | None:
    if not _ENABLE_GOOGLE_OAUTH:
        return None
    token = _extract_token_from_request(request)
    if not token:
        logging.info("Auth missing for request %s %s", request.method, request.path)
        return web.json_response({"detail": "missing_bearer_token"}, status=401)
    # First, accept server-side sessions (LF_SESSION cookie)
    ok, email = await _verify_session(token)
    if not ok:
        # Fallback: treat token as an id_token and verify with Google
        ok, email = await _verify_token_and_email(token)
    if not ok:
        logging.info("Auth failed for request %s %s (invalid token or forbidden)", request.method, request.path)
        return web.json_response({"detail": "invalid_token_or_forbidden"}, status=401)
    # attach email to request for downstream use
    try:
        request['google_oauth_email'] = email
    except Exception:
        setattr(request, 'google_oauth_email', email)
    logging.info("Auth accepted for %s as %s on %s %s", email, request.remote, request.method, request.path)
    return None

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

# region Helpers

def _make_run_payload(
    *,
    detail: str = "",
    error_message: str | None = None,
    error_input: str | None = None,
    history: Dict[str, Any] | None = None,
    preferred_output: str | None = None,
) -> Dict[str, Any]:
    """
    Build a response payload compatible with the frontend's WorkflowAPIRunPayload:

    {
      "detail": string,
      "error": { "message": string, "input": string | undefined },
      "history": { outputs?: {...} },
      "preferred_output": string | undefined
    }
    """
    payload: Dict[str, Any] = {"detail": detail or ""}
    if error_message is not None:
        payload["error"] = {"message": str(error_message)}
        if error_input:
            payload["error"]["input"] = str(error_input)

    payload["history"] = history or {"outputs": {}}
    if preferred_output is not None:
        payload["preferred_output"] = preferred_output

    return {"message": detail or "", "payload": payload, "status": "error" if error_message else "ready"}

def _sanitize_history(entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize a single history entry for safe JSON serialization.
    The function returns a dictionary containing only the "status", "outputs",
    and "prompt" keys, each passed through `_json_safe` so nested values remain
    JSON-serializable while preserving the original key names.
    """
    outputs = entry.get("outputs", {}) or {}
    safe_outputs = {}
    for node_id, node_out in outputs.items():
        try:
            safe_outputs[str(node_id)] = json_safe(node_out)
        except Exception:
            safe_outputs[str(node_id)] = node_out

    return {
        "status": json_safe(entry.get("status")),
        "outputs": json_safe(safe_outputs),
        "prompt": json_safe(entry.get("prompt")),
    }
def _sanitize_rel_path(raw_path: str) -> Optional[Path]:
    """Sanitizes a relative path to prevent directory traversal and ensure safety.

    This function normalizes the input path by converting backslashes to forward slashes,
    checks for potentially unsafe elements like ".." or paths starting with "/", and
    constructs a Path object from valid parts if the path is deemed safe.

    Args:
        raw_path (str): The raw path string to be sanitized.

    Returns:
        Optional[Path]: A Path object representing the sanitized relative path if valid,
        or None if the path contains unsafe elements (e.g., ".." or absolute path indicators).
    """
    normalized = raw_path.replace("\\", "/")
    if ".." in normalized or normalized.startswith("/"):
        return None
    parts = [part for part in normalized.split("/") if part]
    return Path(*parts)

def _serve_first_existing(paths: Iterable[Path]) -> Optional[web.FileResponse]:
    """
    Serves the first existing file from a list of candidate paths.

    This function iterates through the provided paths and returns a web.FileResponse
    for the first path that exists and is a file. If no such path is found, it returns None.

    Args:
        paths (Iterable[Path]): An iterable of Path objects to check for existence and file status.

    Returns:
        Optional[web.FileResponse]: A FileResponse for the first existing file, or None if no file is found.
    """
    for candidate in paths:
        if candidate.exists() and candidate.is_file():
            return web.FileResponse(str(candidate))
    return None

def _serve_static(
    request: web.Request,
    *,
    roots: Iterable[Path],
    prefix: Optional[str] = None,
    not_found_text: str = 'Not found',
    log_context: str = 'static asset',
    log_errors: bool = True,
) -> web.Response:
    raw_path = request.match_info.get('path', '')
    if prefix and not raw_path.startswith(prefix):
        return web.Response(status=404, text=not_found_text)

    rel_path = _sanitize_rel_path(raw_path)
    if rel_path is None:
        return web.Response(status=400, text='Invalid path')

    try:
        response = _serve_first_existing(root / rel_path for root in roots)
        if response is not None:
            return response
    except Exception:
        if log_errors:
            logging.exception('Error while attempting to serve %s: %s', log_context, request.path)
        return web.Response(status=404, text=not_found_text)

    return web.Response(status=404, text=not_found_text)

async def _wait_for_completion(prompt_id: str, timeout_seconds: float | None = None) -> Dict[str, Any]:
    """
    Poll the prompt queue history until the prompt either completes, fails,
    or the timeout is reached.
    """
    queue = PromptServer.instance.prompt_queue
    start = time.perf_counter()
    deadline = start + timeout_seconds if timeout_seconds and timeout_seconds > 0 else None

    while True:
        history = queue.get_history(prompt_id=prompt_id)
        if prompt_id in history:
            entry = history[prompt_id]
            status = entry.get("status") or {}
            if status.get("completed") is True or status.get("status_str") == "error":
                return entry
            if entry.get("outputs"):
                # Some nodes don't populate status but still produce outputs.
                return entry

        if deadline is not None and time.perf_counter() >= deadline:
            raise TimeoutError(f"Prompt {prompt_id} did not finish within {timeout_seconds} seconds.")

        await asyncio.sleep(0.35)
# endregion


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
    session_id = uuid.uuid4().hex
    expires_at = _time.time() + _SESSION_TTL
    try:
        _SESSION_STORE[session_id] = (email, expires_at)
    except Exception:
        logging.exception("Failed to create session in store")
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
    session_id = uuid.uuid4().hex
    expires_at = _time.time() + _SESSION_TTL
    _SESSION_STORE[session_id] = (email, expires_at)
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

# region Static assets
@PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/static/{{path:.*}}")
async def route_static_asset(request: web.Request) -> web.Response:
    # require auth for static assets (the UI will send the auth cookie)
    if _ENABLE_GOOGLE_OAUTH:
        auth_resp = await _require_auth(request)
        if isinstance(auth_resp, web.Response):
            return auth_resp

    return _serve_static(
        request,
        roots=ASSET_SEARCH_ROOTS,
        prefix='assets/',
        log_context='static asset',
    )
# endregion

# region Static JS
@PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/js/{{path:.*}}")
async def route_static_js(request: web.Request) -> web.Response:
    # require auth for shared JS assets
    if _ENABLE_GOOGLE_OAUTH:
        auth_resp = await _require_auth(request)
        if isinstance(auth_resp, web.Response):
            return auth_resp

    return _serve_static(
        request,
        roots=(SHARED_JS_ROOT,),
        log_context='shared JS asset',
    )
# endregion

# region Workflow static
@PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/static-workflow-runner/{'{path:.*}'}")
async def route_static_workflow(request: web.Request) -> web.Response:
    # require auth for workflow-runner static assets
    if _ENABLE_GOOGLE_OAUTH:
        auth_resp = await _require_auth(request)
        if isinstance(auth_resp, web.Response):
            return auth_resp

    return _serve_static(
        request,
        roots=WORKFLOW_STATIC_ROOTS,
        log_context='workflow runner asset',
        log_errors=False,
    )
# endregion

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
