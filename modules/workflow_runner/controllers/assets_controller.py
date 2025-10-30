import logging
import re

from aiohttp import web
from pathlib import Path
from typing import Iterable, Optional

from server import PromptServer

from ..config import CONFIG as RUNNER_CONFIG, API_ROUTE_PREFIX
from ..services.auth_service import _ENABLE_GOOGLE_OAUTH, _require_auth

# region Helpers
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
# endregion

# region Static route
@PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/static/{{path:.*}}")
async def route_static_asset(request: web.Request) -> web.Response:
    raw_path = request.match_info.get('path', '')
    allow_public = raw_path.endswith('.woff') or raw_path.endswith('.woff2')

    if _ENABLE_GOOGLE_OAUTH and not allow_public:
        auth_resp = await _require_auth(request)
        if isinstance(auth_resp, web.Response):
            return auth_resp

    roots = (RUNNER_CONFIG.deploy_root, RUNNER_CONFIG.runner_root)
    return _serve_static(request, roots=roots, prefix='assets/', log_context='static asset')
# endregion

# region Static JS route
@PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/js/{{path:.*}}")
async def route_static_js(request: web.Request) -> web.Response:
    raw_path = request.match_info.get('path', '')
    allow_public = False
    try:
        if re.match(r'^(lf-widgets|lf-).*\.js$', raw_path):
            allow_public = True
    except Exception:
        allow_public = False

    if _ENABLE_GOOGLE_OAUTH and not allow_public:
        auth_resp = await _require_auth(request)
        if isinstance(auth_resp, web.Response):
            return auth_resp

    roots = (RUNNER_CONFIG.shared_js_root,)
    return _serve_static(request, roots=roots, log_context='shared JS asset')
# endregion

# region JS route
@PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/static-workflow-runner/{{path:.*}}")
async def route_static_workflow(request: web.Request) -> web.Response:
    raw_path = request.match_info.get('path', '')
    allow_public = False
    try:
        if raw_path.startswith('css/') or raw_path.endswith('.css'):
            allow_public = True
        elif re.match(r'^js/lf-widgets(?:-[^/]+)*\.js$', raw_path):
            allow_public = True
        elif raw_path in ('js/bootstrap-login.js', 'js/bootstrap-not-found.js'):
            allow_public = True
    except Exception:
        allow_public = False

    if _ENABLE_GOOGLE_OAUTH and not allow_public:
        auth_resp = await _require_auth(request)
        if isinstance(auth_resp, web.Response):
            return auth_resp

    roots = (RUNNER_CONFIG.runner_root,)
    return _serve_static(request, roots=roots, log_context='workflow runner asset', log_errors=False)
# endregion

# region Fonts route
@PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/fonts/{{path:.*}}")
async def route_fonts(request: web.Request) -> web.Response:
    raw_path = request.match_info.get('path', '')
    allow_public = raw_path.endswith('.woff') or raw_path.endswith('.woff2')

    if _ENABLE_GOOGLE_OAUTH and not allow_public:
        auth_resp = await _require_auth(request)
        if isinstance(auth_resp, web.Response):
            return auth_resp

    rel_path = _sanitize_rel_path(raw_path)
    if rel_path is None:
        return web.Response(status=400, text='Invalid path')

    try:
        response = _serve_first_existing((RUNNER_CONFIG.deploy_root / 'assets' / 'fonts' / rel_path,))
        if response is not None:
            return response
    except Exception:
        logging.exception('Error while attempting to serve font: %s', request.path)
        return web.Response(status=404, text='Not found')

    return web.Response(status=404, text='Not found')
# endregion

__all__ = [
    "_serve_first_existing",
    "_serve_static",
]
