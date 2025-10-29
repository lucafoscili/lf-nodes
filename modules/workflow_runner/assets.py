import logging
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

from aiohttp import web
from server import PromptServer

from .config import CONFIG as RUNNER_CONFIG
from .auth import _ENABLE_GOOGLE_OAUTH, _require_auth
from ..utils.constants import API_ROUTE_PREFIX, NOT_FND_HTML


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


# Static asset routes
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
