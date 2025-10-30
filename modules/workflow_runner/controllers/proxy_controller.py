import json
import logging
from time import time
from typing import Any, Dict, Optional

import aiohttp
from aiohttp import web

from server import PromptServer
import importlib
"""Use a lightweight local API prefix to avoid importing heavy global
constants at module import time. Keep this literal in sync with
`utils.constants.API_ROUTE_PREFIX`.
"""

API_ROUTE_PREFIX = "/lf-nodes"

# Import the services proxy module explicitly to avoid name shadowing with the
# route handler function (the handler is named `proxy_service`). We import
# by full module path to make sure we get the submodule object, not a
# package-level attribute that could be replaced.
proxy_svc = importlib.import_module("lf_nodes.modules.workflow_runner.services.proxy_service")

LOG = logging.getLogger(__name__)


@PromptServer.instance.routes.post(f"{API_ROUTE_PREFIX}/proxy/{{service}}")
async def proxy_service(request: web.Request) -> web.Response:
    try:
        if proxy_svc.PROXY_SECRET:
            provided = request.headers.get(proxy_svc.PROXY_SECRET_HEADER, "")
            if not provided or provided != proxy_svc.PROXY_SECRET:
                return web.json_response({"detail": "unauthorized"}, status=401)

        service = request.match_info.get("service", "")
        cfg = proxy_svc.SERVICES.get(service)
        if cfg is None:
            return web.json_response({"detail": f"unknown_service: {service}"}, status=404)

        try:
            client_id = proxy_svc._get_client_id(request)
            allowed, retry_after = proxy_svc._check_rate_limit(client_id, service, cfg)
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

        upstream, headers, timeout, forward_body = proxy_svc._build_upstream_and_headers(cfg, body, proxypath=None)

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


@PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/proxy/{{service}}")
async def proxy_service_status(request: web.Request) -> web.Response:
    try:
        service = request.match_info.get("service", "")
        cfg = proxy_svc.SERVICES.get(service)
        if cfg is None:
            return web.json_response({"detail": f"unknown_service: {service}"}, status=404)

        ready = False
        reason = None

        if "endpoint" in cfg:
            api_env = cfg.get("api_key_env")
            if api_env:
                key = proxy_svc._read_secret(api_env, f"{api_env}_FILE")
                ready = bool(key)
                if not ready:
                    reason = f"missing {api_env}"
            else:
                ready = True
        else:
            base_env = cfg.get("base_env")
            base_url = proxy_svc._read_secret(base_env, f"{base_env}_FILE") if base_env else None
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


@PromptServer.instance.routes.post(f"{API_ROUTE_PREFIX}/proxy/{{service}}/{{proxypath:.*}}")
async def proxy_service_with_path(request: web.Request) -> web.Response:
    try:
        if proxy_svc.PROXY_SECRET:
            provided = request.headers.get(proxy_svc.PROXY_SECRET_HEADER, "")
            if not provided or provided != proxy_svc.PROXY_SECRET:
                return web.json_response({"detail": "unauthorized"}, status=401)

        service = request.match_info.get("service", "")
        proxypath = request.match_info.get("proxypath", "")
        cfg = proxy_svc.SERVICES.get(service)
        if cfg is None:
            return web.json_response({"detail": f"unknown_service: {service}"}, status=404)

        try:
            client_id = proxy_svc._get_client_id(request)
            allowed, retry_after = proxy_svc._check_rate_limit(client_id, service, cfg)
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

        upstream, headers, timeout, forward_body = proxy_svc._build_upstream_and_headers(cfg, body, proxypath=proxypath)

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
