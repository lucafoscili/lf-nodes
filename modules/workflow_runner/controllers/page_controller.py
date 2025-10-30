import asyncio
import logging
from aiohttp import web

from server import PromptServer

from ..config import CONFIG as RUNNER_CONFIG
from ..services.auth_service import (
    _ENABLE_GOOGLE_OAUTH,
    _GOOGLE_CLIENT_IDS,
    _extract_token_from_request,
    _verify_session,
    _verify_token_and_email,
)
from .assets_controller import _serve_first_existing
import importlib
"""Use a lightweight local API route prefix to avoid importing global
constants that pull in heavy dependencies during import-time.
Keep this value in sync with `utils.constants.API_ROUTE_PREFIX`.
"""

API_ROUTE_PREFIX = "/lf-nodes"
NOT_FND_HTML = """
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="utf-8" />
        <title>Workflow Runner Not Found</title>
        <meta name="viewport" content="width=device-width,initial-scale=1" />
        <style>body{font-family:Segoe UI,system-ui,Arial,sans-serif;background:#0b0d12;color:#e8ebf0;padding:2rem}main{max-width:720px;margin:2rem auto;background:#0f1115;padding:1.5rem;border-radius:12px;border:1px solid #1d2230}h1{margin-top:0}code{background:#0b0f14;padding:.15rem .35rem;border-radius:4px}</style>
    </head>
    <body>
        <main>
            <h1>LF Nodes — Workflow Runner</h1>
            <p>The workflow runner UI is not built or not available in the extension's <code>web/deploy</code> directory.</p>
            <p>To build the frontend, change into the extension directory and run the project build (this will produce <code>web/deploy/submit-prompt.html</code> and related JS):</p>
            <pre style="background:#071018;padding:.6rem;border-radius:6px;color:#9fb6ff">cd custom_nodes/lf-nodes; yarn build</pre>
            <p>After building, refresh this page. If you want to work on the frontend in dev mode, edit <code>web/src/workflow</code> and run the dev server described in the project's README.</p>
        </main>
    </body>
    </html>
    """


DEPLOY_ROOT = RUNNER_CONFIG.deploy_root
WORKFLOW_RUNNER_ROOT = RUNNER_CONFIG.runner_root
WORKFLOW_HTML = RUNNER_CONFIG.workflow_html


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
                ok, _email = await _verify_session(token)
                if not ok:
                    ok, _email = await _verify_token_and_email(token)
                if ok:
                    response = _serve_first_existing((WORKFLOW_HTML,))
                    if response is not None:
                        return response

            # serve the login splash page
            # prefer canonical auth_service values (avoids importing removed root-level shims)
            client_id_val = _GOOGLE_CLIENT_IDS[0] if (_GOOGLE_CLIENT_IDS and len(_GOOGLE_CLIENT_IDS) > 0) else ''

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



@PromptServer.instance.routes.post(f"{API_ROUTE_PREFIX}/workflow-runner/verify")
async def route_workflow_runner_verify(request: web.Request) -> web.Response:
    # Delegate to controller which contains the logic and cookie handling.
    # Import the controllers module lazily to avoid pulling heavy imports at
    # module-import time.
    api_controllers = importlib.import_module("lf_nodes.modules.workflow_runner.controllers.api_controllers")
    return await api_controllers.verify_controller(request)


@PromptServer.instance.routes.post(f"{API_ROUTE_PREFIX}/workflow-runner/debug-login")
async def route_workflow_runner_debug_login(request: web.Request) -> web.Response:
    api_controllers = importlib.import_module("lf_nodes.modules.workflow_runner.controllers.api_controllers")
    return await api_controllers.debug_login_controller(request)
