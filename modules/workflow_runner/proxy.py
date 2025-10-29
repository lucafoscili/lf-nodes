import aiohttp
import json
import logging
import os
from time import time
from urllib.parse import urlsplit

from aiohttp import web
from typing import Any, Dict

from server import PromptServer
from ..utils.constants import API_ROUTE_PREFIX

LOG = logging.getLogger(__name__)

# region Proxy Service Config
SERVICES: Dict[str, Dict[str, Any]] = {
    # Clients may supply an optional "path" in the request body to select the upstream route.
    # Allowed paths are restricted for safety.
    "kobold": {
        "base_env": "KOBOLDCPP_BASE",
        "default_path": "/api/v1/generate",
        "allowed_paths": [
            "/api/v1/generate",
            "/api/v1/generate/stream",
        ],
        "timeout": 60,
    },
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
_RATE_LIMIT_STORE: dict[tuple[str, str], dict] = {}

DEFAULT_RATE_LIMIT = {
    "requests": int(os.environ.get("PROXY_RATE_LIMIT_REQUESTS", "60")),
    "window_seconds": int(os.environ.get("PROXY_RATE_LIMIT_WINDOW_SECONDS", "60")),
}

def _get_client_id(request: web.Request) -> str:
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
    svc_limit = cfg.get("rate_limit") if cfg else None
    if svc_limit is None:
        limit = DEFAULT_RATE_LIMIT
    else:
        try:
            limit = {
                "requests": int(svc_limit.get("requests", DEFAULT_RATE_LIMIT["requests"])),
                "window_seconds": int(svc_limit.get("window_seconds", DEFAULT_RATE_LIMIT["window_seconds"])),
            }
        except Exception:
            limit = DEFAULT_RATE_LIMIT

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

    retry_after = int(limit["window_seconds"] - (now - entry.get("start", 0)))
    return False, retry_after
# endregion

# region Internal helpers
def _build_upstream_and_headers(cfg: Dict[str, Any], body: Dict[str, Any], proxypath: str | None) -> tuple[str, Dict[str, str], int, Dict[str, Any]]:
    """Compute upstream URL, headers, timeout and forward body for a service.

    - endpoint-style services (openai/gemini):
      * if proxypath provided, use scheme://netloc + proxypath
      * else, use configured endpoint with optional {model} format
    - base+path services (kobold):
      * base from env, path from proxypath or body.path or default_path
      * enforce allowlist when configured
    """
    headers: Dict[str, str] = {}
    timeout = int(cfg.get("timeout", 60))

    if "endpoint" in cfg:
        if proxypath:
            parts = urlsplit(cfg["endpoint"])  # derive base from configured endpoint
            base = f"{parts.scheme}://{parts.netloc}"
            upstream = base.rstrip("/") + "/" + proxypath.lstrip("/")
        else:
            model = body.get("model") or cfg.get("default_model")
            upstream = cfg["endpoint"].format(model=model)

        api_env = cfg.get("api_key_env")
        if api_env:
            key = _read_secret(api_env, f"{api_env}_FILE")
            if key:
                header_name = cfg.get("api_key_header")
                if header_name == "Authorization":
                    headers[header_name] = f"Bearer {key}"
                else:
                    headers[header_name] = key
        forward_body = body
    else:
        base_env = cfg.get("base_env")
        base_url = _read_secret(base_env, f"{base_env}_FILE") if base_env else None
        if not base_url:
            raise web.HTTPInternalServerError(text=json.dumps({"detail": "proxy_not_configured", "error": f"Missing base URL: set {base_env}"}))

        path = proxypath or body.get("path") or cfg.get("default_path", "/")
        if not isinstance(path, str):
            raise web.HTTPBadRequest(text=json.dumps({"detail": "invalid_path"}))
        if not path.startswith('/'):
            path = "/" + path

        allowed = cfg.get("allowed_paths")
        mapped_for_openai_chat = False
        if path.lstrip("/").startswith("v1/chat/completions"):
            mapped_for_openai_chat = True
            if bool(body.get("stream")):
            #   path = "/api/v1/generate/stream"
                path = "/api/v1/generate" # TODO: Need SSE bridge to repackage chunks as OpenAI chat-completions events
            else:
                path = "/api/v1/generate"

        if isinstance(allowed, list) and path not in allowed:
            raise web.HTTPBadRequest(text=json.dumps({"detail": "path_not_allowed", "path": path}))

        upstream = base_url.rstrip("/") + path

        if mapped_for_openai_chat and isinstance(body.get("messages"), list):
            # Adapter: OpenAI Chat Completions -> Kobold generate
            messages = body.get("messages", [])

            def _extract_content(msg: Any) -> str:
                try:
                    c = msg.get("content")
                    if isinstance(c, list):
                        return " ".join(str(p.get("text", "")) for p in c if isinstance(p, dict))
                    return str(c)
                except Exception:
                    return ""

            system_parts: list[str] = []
            dialogue_lines: list[str] = []
            for m in messages:
                role = (m.get("role") if isinstance(m, dict) else "").strip() or "user"
                content = _extract_content(m).strip()
                if not content:
                    continue
                if role == "system":
                    system_parts.append(content)
                elif role == "assistant":
                    dialogue_lines.append(f"Assistant: {content}")
                else:  # user or unknown
                    dialogue_lines.append(f"User: {content}")

            prompt_lines: list[str] = []
            if system_parts:
                prompt_lines.append(f"System: {' '.join(system_parts)}")
                prompt_lines.append("")
            prompt_lines.extend(dialogue_lines)
            # Prime the model to answer as assistant
            prompt_lines.append("Assistant:")
            prompt = "\n".join(prompt_lines).strip()

            max_tokens = body.get("max_tokens")
            temperature = body.get("temperature")
            stop = body.get("stop")
            seed = body.get("seed")
            top_p = body.get("top_p")
            top_k = body.get("top_k")
            min_p = body.get("min_p")
            repetition_penalty = body.get("repetition_penalty")

            forward_body = {
                "prompt": prompt,
            }
            if isinstance(max_tokens, int):
                forward_body["max_length"] = max_tokens
            if isinstance(temperature, (int, float)):
                forward_body["temperature"] = float(temperature)
            if seed is not None:
                forward_body["seed"] = seed
            if isinstance(top_p, (int, float)):
                forward_body["top_p"] = float(top_p)
            if isinstance(top_k, int):
                forward_body["top_k"] = int(top_k)
            if isinstance(min_p, (int, float)):
                forward_body["min_p"] = float(min_p)
            if isinstance(repetition_penalty, (int, float)):
                forward_body["repetition_penalty"] = float(repetition_penalty)
            if stop is not None:
                forward_body["stop_sequence"] = stop
            else:
                # Default stop sequences to avoid the model switching roles
                forward_body["stop_sequence"] = ["\nUser:", "\nSystem:"]

            # Remove OpenAI-only keys we consumed
            forward_body.pop("messages", None)  # defensive
            # Do not forward stream to non-stream endpoint; handled at route layer
            # (we will pick the stream endpoint when stream=true)

            # Pass-through additional generation controls when present
            for extra_key in (
                "mirostat",
                "mirostat_eta",
                "mirostat_tau",
                "typical_p",
                "tfs",
                "sampler",
                "sampler_order",
                "use_default_prompt_template",
            ):
                if extra_key in body:
                    forward_body[extra_key] = body[extra_key]
        else:
            forward_body = {k: v for k, v in body.items() if k != "path"}

    return upstream, headers, timeout, forward_body
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
            client_id = _get_client_id(request)
            allowed, retry_after = _check_rate_limit(client_id, service, cfg)
            if not allowed:
                return web.json_response({"detail": "rate_limited"}, status=429, headers={"Retry-After": str(retry_after)})
        except Exception:
            LOG.exception("Rate limiter check failed; proceeding without limiting")

        try:
            body = await request.json()
        except Exception:
            body_text = await request.text()
            try:
                body = json.loads(body_text) if body_text else {}
            except Exception:
                body = {}

        upstream, headers, timeout, forward_body = _build_upstream_and_headers(cfg, body, proxypath=None)

        async with aiohttp.ClientSession() as sess:
            try:
                async with sess.post(upstream, json=forward_body, headers=headers, timeout=timeout) as resp:
                    text = await resp.text()
                    content_type = resp.headers.get("Content-Type", "")
                    if "application/json" in content_type.lower():
                        try:
                            data = await resp.json()
                        except Exception:
                            return web.Response(text=text or "", status=resp.status, content_type="application/json")

                        if isinstance(data, dict):
                            data.setdefault("lf_http_status", resp.status)

                            whitelist = cfg.get("response_whitelist")
                            if whitelist and isinstance(whitelist, list):
                                filtered: Dict[str, Any] = {}
                                for k in whitelist:
                                    if k in data:
                                        filtered[k] = data[k]
                                filtered.setdefault("lf_http_status", data.get("lf_http_status", resp.status))
                                return web.json_response(filtered, status=resp.status)

                            return web.json_response(data, status=resp.status)
                        else:
                            return web.json_response({"result": data, "lf_http_status": resp.status}, status=resp.status)
                    else:
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

# region Proxy Status (GET)
@PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/proxy/{{service}}")
async def proxy_service_status(request: web.Request) -> web.Response:
    """Lightweight readiness endpoint for proxy services.

    Returns 200 with a small JSON payload if the service is known and
    minimally configured on the server (e.g., API key or base URL available).
    """
    try:
        service = request.match_info.get("service", "")
        cfg = SERVICES.get(service)
        if cfg is None:
            return web.json_response({"detail": f"unknown_service: {service}"}, status=404)

        ready = False
        reason = None

        if "endpoint" in cfg:
            # If an API key env is declared, require it to consider the service ready.
            api_env = cfg.get("api_key_env")
            if api_env:
                key = _read_secret(api_env, f"{api_env}_FILE")
                ready = bool(key)
                if not ready:
                    reason = f"missing {api_env}"
            else:
                ready = True
        else:
            base_env = cfg.get("base_env")
            base_url = _read_secret(base_env, f"{base_env}_FILE") if base_env else None
            ready = bool(base_url)
            if not ready:
                reason = f"missing {base_env}"

        payload = {"service": service, "ready": ready}
        if reason and not ready:
            payload["reason"] = reason
        return web.json_response(payload, status=200 if ready else 503)
    except Exception as exc:
        LOG.exception("Proxy status check failed: %s", exc)
        return web.json_response({"detail": "proxy_error", "error": str(exc)}, status=500)
# endregion

# region Proxy with path suffix
@PromptServer.instance.routes.post(f"{API_ROUTE_PREFIX}/proxy/{{service}}/{{proxypath:.*}}")
async def proxy_service_with_path(request: web.Request) -> web.Response:
    try:
        if PROXY_SECRET:
            provided = request.headers.get(PROXY_SECRET_HEADER, "")
            if not provided or provided != PROXY_SECRET:
                return web.json_response({"detail": "unauthorized"}, status=401)

        service = request.match_info.get("service", "")
        proxypath = request.match_info.get("proxypath", "")
        cfg = SERVICES.get(service)
        if cfg is None:
            return web.json_response({"detail": f"unknown_service: {service}"}, status=404)

        try:
            client_id = _get_client_id(request)
            allowed, retry_after = _check_rate_limit(client_id, service, cfg)
            if not allowed:
                return web.json_response({"detail": "rate_limited"}, status=429, headers={"Retry-After": str(retry_after)})
        except Exception:
            LOG.exception("Rate limiter check failed; proceeding without limiting")

        try:
            body = await request.json()
        except Exception:
            body_text = await request.text()
            try:
                body = json.loads(body_text) if body_text else {}
            except Exception:
                body = {}

        upstream, headers, timeout, forward_body = _build_upstream_and_headers(cfg, body, proxypath=proxypath)

        async with aiohttp.ClientSession() as sess:
            try:
                async with sess.post(upstream, json=forward_body, headers=headers, timeout=timeout) as resp:
                    text = await resp.text()
                    content_type = resp.headers.get("Content-Type", "")
                    if "application/json" in content_type.lower():
                        try:
                            data = await resp.json()
                        except Exception:
                            return web.Response(text=text or "", status=resp.status, content_type="application/json")

                        if isinstance(data, dict):
                            data.setdefault("lf_http_status", resp.status)

                            whitelist = cfg.get("response_whitelist")
                            if whitelist and isinstance(whitelist, list):
                                filtered: Dict[str, Any] = {}
                                for k in whitelist:
                                    if k in data:
                                        filtered[k] = data[k]
                                filtered.setdefault("lf_http_status", data.get("lf_http_status", resp.status))
                                return web.json_response(filtered, status=resp.status)

                            # If client sent OpenAI chat-style body to kobold, wrap response
                            if service == "kobold" and isinstance(body.get("messages"), list):
                                text_out = None
                                try:
                                    if isinstance(data.get("results"), list) and data["results"]:
                                        cand = data["results"][0]
                                        if isinstance(cand, dict):
                                            text_out = cand.get("text") or cand.get("output")
                                except Exception:
                                    pass
                                if not text_out:
                                    text_out = data.get("text") or data.get("output") or ""

                                wrapped = {
                                    "id": data.get("id") or f"kobold-{int(time())}",
                                    "object": "chat.completion",
                                    "created": int(time()),
                                    "model": data.get("model") or "koboldcpp",
                                    "choices": [
                                        {
                                            "index": 0,
                                            "message": {"role": "assistant", "content": text_out or ""},
                                            "finish_reason": data.get("finish_reason") or "stop",
                                        }
                                    ],
                                    "lf_http_status": resp.status,
                                }
                                return web.json_response(wrapped, status=resp.status)

                            # Wrap kobold -> OpenAI chat schema when hitting /v1/chat/completions
                            if service == "kobold" and (proxypath or "").lstrip("/").startswith("v1/chat/completions"):
                                text_out = None
                                try:
                                    if isinstance(data.get("results"), list) and data["results"]:
                                        cand = data["results"][0]
                                        if isinstance(cand, dict):
                                            text_out = cand.get("text") or cand.get("output")
                                except Exception:
                                    pass
                                if not text_out:
                                    text_out = data.get("text") or data.get("output") or ""

                                wrapped = {
                                    "id": data.get("id") or f"kobold-{int(time())}",
                                    "object": "chat.completion",
                                    "created": int(time()),
                                    "model": data.get("model") or "koboldcpp",
                                    "choices": [
                                        {
                                            "index": 0,
                                            "message": {"role": "assistant", "content": text_out or ""},
                                            "finish_reason": data.get("finish_reason") or "stop",
                                        }
                                    ],
                                    "lf_http_status": resp.status,
                                }
                                return web.json_response(wrapped, status=resp.status)

                            return web.json_response(data, status=resp.status)
                        else:
                            return web.json_response({"result": data, "lf_http_status": resp.status}, status=resp.status)
                    else:
                        return web.Response(text=text or "", status=resp.status, content_type=content_type or "text/plain")
            except aiohttp.ClientError as exc:
                LOG.exception("Upstream request to %s failed: %s", upstream, exc)
                return web.json_response({"detail": "upstream_error", "error": str(exc)}, status=502)
            except Exception as exc:  # defensive
                LOG.exception("Unexpected error proxying to %s: %s", upstream, exc)
                return web.json_response({"detail": "proxy_error", "error": str(exc)}, status=500)
    except web.HTTPException:
        raise
    except Exception as exc_outer:
        LOG.exception("Proxy handler with path failed: %s", exc_outer)
        return web.json_response({"detail": "proxy_error", "error": str(exc_outer)}, status=500)
# endregion
