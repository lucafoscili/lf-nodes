import logging
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

from aiohttp import web
from server import PromptServer

from ..config import CONFIG as RUNNER_CONFIG
from ..services.auth_service import _ENABLE_GOOGLE_OAUTH, _require_auth
"""Use a local lightweight API prefix and not-found page to avoid importing
global constants that pull in large dependencies during import-time.
Keep the literal in sync with `utils.constants.API_ROUTE_PREFIX`.
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


def _sanitize_rel_path(raw_path: str) -> Optional[Path]:
    normalized = raw_path.replace("\\", "/")
    if ".." in normalized or normalized.startswith("/"):
        return None
    parts = [part for part in normalized.split("/") if part]
    return Path(*parts)


def _serve_first_existing(paths: Iterable[Path]) -> Optional[web.FileResponse]:
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


# Static asset routes — register on import just like the old module did.
@PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/static/{{path:.*}}")
async def route_static_asset(request: web.Request) -> web.Response:
    if _ENABLE_GOOGLE_OAUTH:
        auth_resp = await _require_auth(request)
        if isinstance(auth_resp, web.Response):
            return auth_resp

    roots = (RUNNER_CONFIG.deploy_root, RUNNER_CONFIG.runner_root)
    return _serve_static(request, roots=roots, prefix='assets/', log_context='static asset')


@PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/js/{{path:.*}}")
async def route_static_js(request: web.Request) -> web.Response:
    if _ENABLE_GOOGLE_OAUTH:
        auth_resp = await _require_auth(request)
        if isinstance(auth_resp, web.Response):
            return auth_resp

    roots = (RUNNER_CONFIG.shared_js_root,)
    return _serve_static(request, roots=roots, log_context='shared JS asset')


@PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/static-workflow-runner/{{path:.*}}")
async def route_static_workflow(request: web.Request) -> web.Response:
    if _ENABLE_GOOGLE_OAUTH:
        auth_resp = await _require_auth(request)
        if isinstance(auth_resp, web.Response):
            return auth_resp

    roots = (RUNNER_CONFIG.runner_root,)
    return _serve_static(request, roots=roots, log_context='workflow runner asset', log_errors=False)


__all__ = [
    "_serve_first_existing",
    "_serve_static",
]
