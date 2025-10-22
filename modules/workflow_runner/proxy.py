import aiohttp
import json
import logging
import os
from time import time

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
# Simple in-memory fixed-window rate limiter store.
# Keyed by (client_id, service) -> {"count": int, "start": float}
_RATE_LIMIT_STORE: dict[tuple[str, str], dict] = {}

# Global default rate limit (can be overridden per-service). Configure via
# env PROXY_RATE_LIMIT_REQUESTS and PROXY_RATE_LIMIT_WINDOW_SECONDS.
DEFAULT_RATE_LIMIT = {
    "requests": int(os.environ.get("PROXY_RATE_LIMIT_REQUESTS", "60")),
    "window_seconds": int(os.environ.get("PROXY_RATE_LIMIT_WINDOW_SECONDS", "60")),
}

def _get_client_id(request: web.Request) -> str:
    # Prefer request.remote (IP). Fallback to peername if available.
    try:
        if getattr(request, 'remote', None):
            return str(request.remote)
        transport = request.transport
        if transport is not None:
            peer = transport.get_extra_info('peername')
            if peer and isinstance(peer, (list, tuple)) and len(peer) >= 1:
                return str(peer[0])
    except Exception:
        pass
    return "unknown"

def _check_rate_limit(client_id: str, service: str, cfg: dict) -> tuple[bool, int]:
    """Returns (allowed, retry_after_seconds).

    If rate limiting is disabled for the service (cfg rate_limit is falsy),
    returns (True, 0).
    """
    # Determine rate limit config (service overrides global DEFAULT_RATE_LIMIT)
    svc_limit = cfg.get("rate_limit") if cfg else None
    if svc_limit is None:
        limit = DEFAULT_RATE_LIMIT
    else:
        # Expect dict like {"requests": int, "window_seconds": int}
        try:
            limit = {
                "requests": int(svc_limit.get("requests", DEFAULT_RATE_LIMIT["requests"])),
                "window_seconds": int(svc_limit.get("window_seconds", DEFAULT_RATE_LIMIT["window_seconds"])),
            }
        except Exception:
            limit = DEFAULT_RATE_LIMIT

    # If requests set to 0 treat as disabled
    if limit.get("requests", 0) <= 0:
        return True, 0

    key = (client_id, service)
    now = time()
    entry = _RATE_LIMIT_STORE.get(key)
    if not entry or (now - entry.get("start", 0)) >= limit["window_seconds"]:
        _RATE_LIMIT_STORE[key] = {"count": 1, "start": now}
        return True, 0

    if entry["count"] < limit["requests"]:
        entry["count"] += 1
        return True, 0

    # Rate limited: compute retry-after
    retry_after = int(limit["window_seconds"] - (now - entry.get("start", 0)))
    return False, retry_after
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

        # Rate limiting: check per-client limits (opt-in per service via cfg["rate_limit"]).
        try:
            client_id = _get_client_id(request)
            allowed, retry_after = _check_rate_limit(client_id, service, cfg)
            if not allowed:
                return web.json_response({"detail": "rate_limited"}, status=429, headers={"Retry-After": str(retry_after)})
        except Exception:
            # Defensive: if rate limiter fails, proceed (don't block proxy)
            LOG.exception("Rate limiter check failed; proceeding without limiting")

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

                            # If the service defines a response_whitelist, return only
                            # those top-level keys (if present). This is opt-in and
                            # non-breaking: when unset we return the full response.
                            whitelist = cfg.get("response_whitelist")
                            if whitelist and isinstance(whitelist, list):
                                filtered: Dict[str, Any] = {}
                                for k in whitelist:
                                    if k in data:
                                        filtered[k] = data[k]
                                # Always include lf_http_status for debugging
                                filtered.setdefault("lf_http_status", data.get("lf_http_status", resp.status))
                                return web.json_response(filtered, status=resp.status)

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