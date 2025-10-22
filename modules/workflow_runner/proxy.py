import aiohttp
import json
import logging
import os

from aiohttp import web
from typing import Any, Dict

from server import PromptServer
from ..utils.constants import API_ROUTE_PREFIX

LOG = logging.getLogger(__name__)

# region Proxy Service Config
# Basic per-service configuration. Add services here as needed.
# Each service entry supports:
#  - endpoint: upstream URL template (use {model} for model substitution)
#  - api_key_env: environment variable name containing the API key (optional)
#  - api_key_header: header to set with the key (if api_key_env set)
#  - default_model: default model if not provided by caller
#  - timeout: per-service timeout seconds
SERVICES: Dict[str, Dict[str, Any]] = {
    "gemini": {
        "endpoint": "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        "api_key_env": "GEMINI_API_KEY",
        "api_key_header": "X-goog-api-key",
        "default_model": "gemini-2.0-flash",
        "timeout": 60,
    },
    "openai": {
        "endpoint": "https://api.openai.com/v1/chat/completions",
        "api_key_env": "OPENAI_API_KEY",
        "api_key_header": "Authorization",  # value will be 'Bearer <key>' by convention
        "default_model": "gpt-4o",
        "timeout": 60,
    },
}

# Shared secret header name for simple auth between internal services/UI and this proxy.
# Supply the secret in env var `LF_PROXY_SECRET` (or `GEMINI_PROXY_SECRET` for compatibility).
def _read_secret(env_name: str, file_env_name: str | None = None) -> str | None:
    """Read a secret from environment variable or a file specified by *_FILE convention.

    Returns the secret string or None if not set.
    """
    val = os.environ.get(env_name)
    if val:
        return val
    if file_env_name:
        path = os.environ.get(file_env_name)
        if path and os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as fh:
                    return fh.read().strip()
            except Exception:
                LOG.exception("Failed reading secret file %s", path)
    return None

PROXY_SECRET = _read_secret("LF_PROXY_SECRET", "LF_PROXY_SECRET_FILE") or _read_secret("GEMINI_PROXY_SECRET", "GEMINI_PROXY_SECRET_FILE")
PROXY_SECRET_HEADER = "X-LF-Proxy-Secret"
# endregion

# region Proxy Handler
@PromptServer.instance.routes.post(f"{API_ROUTE_PREFIX}/proxy/{{service}}")
async def proxy_service(request: web.Request) -> web.Response:
    """Generic proxy endpoint for forwarding calls to configured LLM APIs.

    POST /api/proxy/{service}
    - Service must be declared in SERVICES.
    - Requires header X-LF-Proxy-Secret == env(LF_PROXY_SECRET) unless that env var is unset.
    - Body is forwarded (possibly adapted) to upstream and upstream response returned.
    """
    # Auth (optional): if secret configured, require it
    try:
        if PROXY_SECRET:
            provided = request.headers.get(PROXY_SECRET_HEADER, "")
            if not provided or provided != PROXY_SECRET:
                return web.json_response({"detail": "unauthorized"}, status=401)

        service = request.match_info.get("service", "")
        cfg = SERVICES.get(service)
        if cfg is None:
            return web.json_response({"detail": f"unknown_service: {service}"}, status=404)

        try:
            body = await request.json()
        except Exception:
            # We'll also accept plain text bodies
            body_text = await request.text()
            try:
                body = json.loads(body_text) if body_text else {}
            except Exception:
                body = {}

        model = body.get("model") or cfg.get("default_model")
        upstream = cfg["endpoint"].format(model=model)

        headers = {}
        # Copy through any useful client headers if needed (none by default)

        # Inject API key if configured. Support ENV or *_FILE
        api_env = cfg.get("api_key_env")
        if api_env:
            # support GEMINI_API_KEY_FILE style too
            key = _read_secret(api_env, f"{api_env}_FILE")
            if key:
                header_name = cfg.get("api_key_header")
                if header_name == "Authorization":
                    headers[header_name] = f"Bearer {key}"
                else:
                    headers[header_name] = key

        timeout = cfg.get("timeout", 60)

        async with aiohttp.ClientSession() as sess:
            try:
                async with sess.post(upstream, json=body, headers=headers, timeout=timeout) as resp:
                    text = await resp.text()
                    content_type = resp.headers.get("Content-Type", "")
                    # Try to parse JSON and attach lf_http_status for debugging
                    if "application/json" in content_type.lower():
                        try:
                            data = await resp.json()
                        except Exception:
                            # Fall back to raw text
                            return web.Response(text=text or "", status=resp.status, content_type="application/json")

                        if isinstance(data, dict):
                            data.setdefault("lf_http_status", resp.status)
                            return web.json_response(data, status=resp.status)
                        else:
                            # Non-dict JSON (list etc.) return as-is
                            return web.json_response({"result": data, "lf_http_status": resp.status}, status=resp.status)
                    else:
                        # Non-JSON: return raw body and mirror content-type
                        return web.Response(text=text or "", status=resp.status, content_type=content_type or "text/plain")
            except aiohttp.ClientError as exc:
                LOG.exception("Upstream request to %s failed: %s", upstream, exc)
                return web.json_response({"detail": "upstream_error", "error": str(exc)}, status=502)
            except Exception as exc:  # defensive
                LOG.exception("Unexpected error proxying to %s: %s", upstream, exc)
                return web.json_response({"detail": "proxy_error", "error": str(exc)}, status=500)
    except Exception as exc_outer:
        LOG.exception("Proxy handler failed: %s", exc_outer)
        return web.json_response({"detail": "proxy_error", "error": str(exc_outer)}, status=500)
# endregion