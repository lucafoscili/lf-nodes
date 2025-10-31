import aiohttp
import asyncio
import importlib
import json
import logging
import re
import uuid

from aiohttp import web
from time import time
from typing import Any, Dict, TYPE_CHECKING, cast

from server import PromptServer

from ..config import API_ROUTE_PREFIX
from ..services import job_store

if TYPE_CHECKING:
    from ..services import proxy_service as proxy_service_typing

# Import the services proxy module explicitly to avoid name shadowing with the
# route handler function (the handler is named `proxy_service`). We import
# by full module path to make sure we get the submodule object, not a
# package-level attribute that could be replaced.
proxy_svc = cast("proxy_service_typing", importlib.import_module("lf_nodes.modules.workflow_runner.services.proxy_service"))

LOG = logging.getLogger(__name__)

# region Proxy endpoint
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

        # Small trace id to correlate logs for this request across log lines
        trace_id = uuid.uuid4().hex[:8]

        # Read raw request text first so we can always log the exact incoming payload
        try:
            body_text = await request.text()
        except Exception:
            body_text = ""

        try:
            LOG.info("Raw proxy request body (trunc 1000): %s", (body_text[:1000] + "...") if isinstance(body_text, str) and len(body_text) > 1000 else body_text)
        except Exception:
            LOG.exception("Failed to log raw proxy request body")

        try:
            body = json.loads(body_text) if body_text else {}
        except Exception:
            # Attempt to parse a JS-like object literal (unquoted keys) that some clients send
            try:
                def _parse_js_like(text: str) -> dict:
                    out: dict = {}
                    # stream flag
                    m = re.search(r"\bstream\s*:\s*(true|false)", text, re.IGNORECASE)
                    if m:
                        out["stream"] = m.group(1).lower() == "true"

                    # numeric fields
                    for k in ("temperature", "max_tokens", "seed", "max_length", "top_k", "top_p"):
                        m = re.search(rf"\b{k}\s*:\s*([-+]?[0-9]*\.?[0-9]+)", text)
                        if m:
                            val = m.group(1)
                            try:
                                if "." in val:
                                    out[k] = float(val)
                                else:
                                    out[k] = int(val)
                            except Exception:
                                out[k] = float(val)

                    # messages array parsing (simple heuristic)
                    mm = re.search(r"messages\s*:\s*\[(.*?)\]\s*(,|\})", text, re.S)
                    if mm:
                        entries = mm.group(1)
                        parts = re.split(r"\},\s*\{", entries)
                        msgs = []
                        for part in parts:
                            p = part.strip().lstrip("{").rstrip("}")
                            # role
                            mr = re.search(r"role\s*:\s*([a-zA-Z0-9_\'\"]+)", p)
                            mc = re.search(r"content\s*:\s*(.+)$", p, re.S)
                            role = "user"
                            if mr:
                                role = mr.group(1).strip().strip('\"\'')
                            content = ""
                            if mc:
                                content = mc.group(1).strip().rstrip(',').strip()
                                # strip quotes if present
                                if (content.startswith('"') and content.endswith('"')) or (content.startswith("'") and content.endswith("'")):
                                    content = content[1:-1]
                            msgs.append({"role": role, "content": content})
                        out["messages"] = msgs

                    return out

                body = _parse_js_like(body_text) if body_text else {}
            except Exception:
                try:
                    body = await request.json()
                except Exception:
                    body = {}

        # Log parsed request body so we can verify what was received
        try:
            if isinstance(body, dict):
                LOG.info("Parsed proxy request body keys=%s", list(body.keys()))
                if body.get("messages") and isinstance(body.get("messages"), list):
                    LOG.info("First message preview: %s", str(body.get("messages")[0])[:200])
            else:
                LOG.info("Parsed proxy request body type=%s", type(body))
        except Exception:
            LOG.exception("Failed logging parsed proxy request body")

        # Additional diagnostic: if the parsed body is empty, log headers and a truncated raw body so
        # we can identify the caller (user-agent / forwarded-for / peer)
        try:
            if not body:
                ua = request.headers.get("User-Agent", "")
                xff = request.headers.get("X-Forwarded-For", "")
                ct = request.headers.get("Content-Type", "")
                cl = request.headers.get("Content-Length", "")
                peer = None
                try:
                    peer = request.transport.get_extra_info("peername") if request.transport is not None else None
                except Exception:
                    peer = None
                LOG.warning("Parsed proxy request body empty; trace_id=%s remote=%s peer=%s ua=%s xff=%s content_type=%s content_length=%s raw_preview=%s", trace_id, request.remote, peer, ua, xff, ct, cl, (body_text[:400] + "...") if isinstance(body_text, str) and len(body_text) > 400 else body_text)
        except Exception:
            LOG.exception("Failed logging empty parsed body diagnostic")

        upstream, headers, timeout, forward_body = proxy_svc._build_upstream_and_headers(cfg, body, proxypath=None)

        async with aiohttp.ClientSession() as sess:
            try:
                # Log what we're forwarding upstream so we can verify prompt mapping
                try:
                    LOG.info("Proxy upstream=%s forward_body_keys=%s", upstream, list(forward_body.keys()) if isinstance(forward_body, dict) else str(type(forward_body)))
                    if isinstance(forward_body, dict):
                        # Log truncated prompt if present
                        if "prompt" in forward_body:
                            p = forward_body.get("prompt")
                            LOG.info("Proxy forward prompt (trunc): %s", (p[:1000] + "...") if isinstance(p, str) and len(p) > 1000 else p)
                    # Warn if upstream forward body looks like it's missing messages/prompts
                    try:
                        if isinstance(forward_body, dict):
                            if not forward_body.get("messages") and not forward_body.get("prompt"):
                                LOG.warning("Forward body missing messages/prompt; trace_id=%s upstream=%s forward_keys=%s body_keys=%s", trace_id, upstream, list(forward_body.keys()), list(body.keys()) if isinstance(body, dict) else str(type(body)))
                    except Exception:
                        LOG.exception("Failed to evaluate forward_body diagnostic")
                except Exception:
                    LOG.exception("Failed logging forward_body for proxy")

                async with sess.post(upstream, json=forward_body, headers=headers, timeout=timeout) as resp:
                    # Determine if this request is intended to be streamed.
                    is_streaming = bool(body.get("stream")) or upstream.endswith("/stream")
                    content_type = resp.headers.get("Content-Type", "")
                    try:
                        LOG.info("Upstream responded status=%s headers=%s is_streaming=%s", resp.status, dict(resp.headers), is_streaming)
                    except Exception:
                        LOG.exception("Failed to log upstream response headers/status")

                    if is_streaming:
                        sresp = web.StreamResponse(status=200, reason="OK")
                        sresp.content_type = "text/event-stream"
                        sresp.headers["Cache-Control"] = "no-cache"
                        sresp.headers["Connection"] = "keep-alive"
                        await sresp.prepare(request)

                        try:
                            first_chunk = True
                            chunk_idx = 0
                            stream_start = time()
                            try:
                                LOG.info("Streaming start trace_id=%s upstream=%s service=%s", trace_id, upstream, service)
                            except Exception:
                                pass

                            async for chunk in resp.content.iter_chunked(1024):
                                if not chunk:
                                    continue
                                chunk_idx += 1
                                now = time()
                                elapsed_ms = int((now - stream_start) * 1000)
                                try:
                                    LOG.info("Upstream chunk idx=%d len=%d elapsed_ms=%d", chunk_idx, len(chunk), elapsed_ms)
                                except Exception:
                                    pass

                                try:
                                    text_chunk = chunk.decode("utf-8", errors="replace")
                                except Exception:
                                    text_chunk = str(chunk)

                                # For diagnosis: log a truncated preview of the first chunk
                                if first_chunk:
                                    try:
                                        preview = text_chunk[:1000]
                                        LOG.info("First upstream chunk preview: %s", preview)
                                    except Exception:
                                        LOG.exception("Failed to log first upstream chunk preview")
                                    first_chunk = False

                                # Try to parse upstream SSE-style 'data: {...}' segments
                                # into JSON objects so we can publish structured
                                # events and avoid double-encoding for the frontend.
                                parsed_objects: list[dict] = []
                                try:
                                    # Split on double-newline which separates SSE events
                                    parts = text_chunk.split("\n\n")
                                    for part in parts:
                                        if not part or not part.strip():
                                            continue
                                        # Strip leading 'data:' prefixes on each line
                                        lines = [l for l in part.splitlines() if l.strip()]
                                        content_lines = []
                                        for l in lines:
                                            if l.lstrip().startswith("data:"):
                                                content_lines.append(l.split("data:", 1)[1].lstrip())
                                            elif l.lstrip().startswith("event:"):
                                                # ignore event lines here
                                                continue
                                            else:
                                                content_lines.append(l)
                                        content = "\n".join(content_lines).strip()
                                        if not content:
                                            continue
                                        try:
                                            obj = json.loads(content)
                                            if isinstance(obj, dict):
                                                parsed_objects.append(obj)
                                                continue
                                        except Exception:
                                            # not JSON, fall through
                                            pass
                                        # If we couldn't parse as JSON, include raw content
                                        parsed_objects.append({"raw": content})
                                except Exception:
                                    parsed_objects = [{"raw": text_chunk}]

                                try:
                                    if parsed_objects:
                                        for obj in parsed_objects:
                                            job_store.publish_event({
                                                "type": "proxy",
                                                "service": service,
                                                "data": obj,
                                            })
                                    else:
                                        job_store.publish_event({
                                            "type": "proxy",
                                            "service": service,
                                            "data": {"chunk": text_chunk},
                                        })
                                except Exception:
                                    LOG.exception("Failed to publish proxy stream event")

                                forward_raw = False
                                try:
                                    forward_raw = bool(cfg.get("forward_raw_sse", False))
                                except Exception:
                                    forward_raw = False

                                try:
                                    lines = text_chunk.splitlines()
                                    if any(l.lstrip().startswith("data:") or l.lstrip().startswith("event:") for l in lines):
                                        raw = text_chunk
                                        if not raw.endswith("\n\n"):
                                            raw = raw + "\n\n"
                                    else:
                                        raw = "".join(f"data: {l}\n" for l in lines) + "\n\n"
                                except Exception:
                                    raw = text_chunk + "\n\n"

                                if forward_raw:
                                    # Send only the raw SSE lines (no wrapper)
                                    try:
                                        await sresp.write(raw.encode("utf-8"))
                                        await sresp.drain()
                                        try:
                                            LOG.info("Wrote raw-only SSE chunk idx=%d to client elapsed_ms=%d", chunk_idx, elapsed_ms)
                                        except Exception:
                                            pass
                                    except (ConnectionResetError, asyncio.CancelledError):
                                        break
                                    except Exception:
                                        LOG.exception("Failed to write raw-only SSE chunk to client")
                                else:
                                    try:
                                        if parsed_objects:
                                            for obj in parsed_objects:
                                                try:
                                                    payload = json.dumps(obj)
                                                except Exception:
                                                    payload = json.dumps({"data": obj})
                                                await sresp.write(f"event: proxy\ndata: {payload}\n\n".encode("utf-8"))
                                                await sresp.drain()
                                        else:
                                            payload = json.dumps({"service": service, "chunk": text_chunk})
                                            await sresp.write(f"event: proxy\ndata: {payload}\n\n".encode("utf-8"))
                                            await sresp.drain()
                                        try:
                                            LOG.info("Wrote chunk idx=%d to client elapsed_ms=%d", chunk_idx, elapsed_ms)
                                        except Exception:
                                            pass
                                    except (ConnectionResetError, asyncio.CancelledError):
                                        break
                                    except Exception:
                                        LOG.exception("Failed to write wrapper SSE chunk to client")

                                    # Also send raw SSE as compatibility
                                    try:
                                        await sresp.write(raw.encode("utf-8"))
                                        await sresp.drain()
                                        try:
                                            LOG.info("Wrote raw SSE chunk idx=%d to client elapsed_ms=%d", chunk_idx, elapsed_ms)
                                        except Exception:
                                            pass
                                    except Exception:
                                        LOG.exception("Failed to write raw SSE chunk to client")

                            try:
                                LOG.info("Streaming finished trace_id=%s upstream=%s service=%s total_chunks=%d total_elapsed_ms=%d", trace_id, upstream, service, chunk_idx, int((time() - stream_start) * 1000))
                            except Exception:
                                pass

                            return sresp
                        finally:
                            try:
                                await sresp.write_eof()
                            except Exception:
                                pass

                    # Non-streaming path continues below
                    text = await resp.text()
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

# region Proxy service status
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
# endregion

# region Proxy service with path
@PromptServer.instance.routes.post(f"{API_ROUTE_PREFIX}/proxy/{{service}}/{{proxypath:.*}}")
async def proxy_service_with_path(request: web.Request) -> web.Response:
    try:
        # Log the incoming request early so we know the route was matched
        try:
            hdrs = {k: request.headers.get(k) for k in ("Content-Type", "Origin", "User-Agent") if request.headers.get(k)}
            LOG.info("Incoming proxy_with_path request: %s %s from=%s headers=%s", request.method, request.path, request.remote, hdrs)
        except Exception:
            LOG.exception("Failed to log incoming proxy request")

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

        # Small trace id to correlate logs for this request across log lines
        trace_id = uuid.uuid4().hex[:8]

        # Read raw request text first so we can always log the exact incoming payload
        try:
            body_text = await request.text()
        except Exception:
            body_text = ""

        try:
            LOG.info("Raw proxy (path) request body (trunc 1000): %s", (body_text[:1000] + "...") if isinstance(body_text, str) and len(body_text) > 1000 else body_text)
        except Exception:
            LOG.exception("Failed to log raw proxy (path) request body")

        # Log request headers and peer info to help identify caller if parsing fails
        try:
            ua = request.headers.get("User-Agent", "")
            xff = request.headers.get("X-Forwarded-For", "")
            ct = request.headers.get("Content-Type", "")
            cl = request.headers.get("Content-Length", "")
            peer = None
            try:
                peer = request.transport.get_extra_info("peername") if request.transport is not None else None
            except Exception:
                peer = None
            LOG.info("Proxy (path) request meta trace_id=%s remote=%s peer=%s ua=%s xff=%s content_type=%s content_length=%s", trace_id, request.remote, peer, ua, xff, ct, cl)
        except Exception:
            LOG.exception("Failed to log proxy (path) request meta")

        try:
            body = json.loads(body_text) if body_text else {}
        except Exception:
            try:
                body = await request.json()
            except Exception:
                body = {}

        # If parsed body is empty, log diagnostics so the caller can be traced
        try:
            if not body:
                ua = request.headers.get("User-Agent", "")
                LOG.warning("Parsed proxy (path) request body empty; trace_id=%s remote=%s ua=%s raw_preview=%s", trace_id, request.remote, ua, (body_text[:400] + "...") if isinstance(body_text, str) and len(body_text) > 400 else body_text)
        except Exception:
            LOG.exception("Failed logging empty parsed body diagnostic for proxypath")

        upstream, headers, timeout, forward_body = proxy_svc._build_upstream_and_headers(cfg, body, proxypath=proxypath)
        # Log what we're forwarding upstream so we can verify prompt mapping
        try:
            LOG.info("Proxy upstream=%s forward_body_keys=%s", upstream, list(forward_body.keys()) if isinstance(forward_body, dict) else str(type(forward_body)))
            if isinstance(forward_body, dict):
                if "prompt" in forward_body:
                    p = forward_body.get("prompt")
                    LOG.info("Proxy forward prompt (trunc): %s", (p[:1000] + "...") if isinstance(p, str) and len(p) > 1000 else p)
            # Warn if upstream forward body looks like it's missing messages/prompts
            try:
                if isinstance(forward_body, dict):
                    if not forward_body.get("messages") and not forward_body.get("prompt"):
                        LOG.warning("Forward body missing messages/prompt; trace_id=%s upstream=%s forward_keys=%s body_keys=%s", trace_id, upstream, list(forward_body.keys()), list(body.keys()) if isinstance(body, dict) else str(type(body)))
            except Exception:
                LOG.exception("Failed to evaluate forward_body diagnostic for proxypath")
        except Exception:
            LOG.exception("Failed logging forward_body for proxy (path)")

        async with aiohttp.ClientSession() as sess:
            try:
                async with sess.post(upstream, json=forward_body, headers=headers, timeout=timeout) as resp:
                    # detect streaming: client requested stream or upstream path indicates streaming
                    is_streaming = bool(body.get("stream")) or upstream.endswith("/stream") or (proxypath or "").endswith("/stream")
                    content_type = resp.headers.get("Content-Type", "")
                    try:
                        LOG.info("Upstream responded status=%s headers=%s is_streaming=%s", resp.status, dict(resp.headers), is_streaming)
                    except Exception:
                        LOG.exception("Failed to log upstream response headers/status for proxypath")

                    if is_streaming:
                        sresp = web.StreamResponse(status=200, reason="OK")
                        sresp.content_type = "text/event-stream"
                        sresp.headers["Cache-Control"] = "no-cache"
                        sresp.headers["Connection"] = "keep-alive"
                        await sresp.prepare(request)

                        try:
                            chunk_idx = 0
                            stream_start = time()
                            try:
                                LOG.info("Streaming start (proxypath) trace_id=%s upstream=%s service=%s proxypath=%s", trace_id, upstream, service, proxypath)
                            except Exception:
                                pass

                            async for chunk in resp.content.iter_chunked(1024):
                                if not chunk:
                                    continue
                                chunk_idx += 1
                                now = time()
                                elapsed_ms = int((now - stream_start) * 1000)
                                try:
                                    LOG.info("Upstream chunk (proxypath) idx=%d len=%d elapsed_ms=%d", chunk_idx, len(chunk), elapsed_ms)
                                except Exception:
                                    pass

                                try:
                                    text_chunk = chunk.decode("utf-8", errors="replace")
                                except Exception:
                                    text_chunk = str(chunk)

                                try:
                                    job_store.publish_event({
                                        "type": "proxy",
                                        "service": service,
                                        "data": {"chunk": text_chunk},
                                    })
                                except Exception:
                                    LOG.exception("Failed to publish proxy stream event")

                                payload = json.dumps({"service": service, "chunk": text_chunk})
                                try:
                                    await sresp.write(f"event: proxy\ndata: {payload}\n\n".encode("utf-8"))
                                    await sresp.drain()
                                    try:
                                        LOG.info("Wrote chunk (proxypath) idx=%d to client elapsed_ms=%d", chunk_idx, elapsed_ms)
                                    except Exception:
                                        pass
                                except (ConnectionResetError, asyncio.CancelledError):
                                    break

                                # Also forward raw SSE-style data for clients that
                                # expect OpenAI-compatible server-sent-events.
                                try:
                                    lines = text_chunk.splitlines()
                                    if any(l.lstrip().startswith("data:") or l.lstrip().startswith("event:") for l in lines):
                                        raw = text_chunk
                                        if not raw.endswith("\n\n"):
                                            raw = raw + "\n\n"
                                        await sresp.write(raw.encode("utf-8"))
                                    else:
                                        raw_sse = "".join(f"data: {l}\n" for l in lines) + "\n\n"
                                        await sresp.write(raw_sse.encode("utf-8"))
                                    await sresp.drain()
                                    try:
                                        LOG.info("Wrote raw SSE chunk (proxypath) idx=%d to client elapsed_ms=%d", chunk_idx, elapsed_ms)
                                    except Exception:
                                        pass
                                except Exception:
                                    LOG.exception("Failed to write raw SSE chunk to client (proxypath)")

                            try:
                                LOG.info("Streaming finished (proxypath) trace_id=%s upstream=%s service=%s proxypath=%s total_chunks=%d total_elapsed_ms=%d", trace_id, upstream, service, proxypath, chunk_idx, int((time() - stream_start) * 1000))
                            except Exception:
                                pass

                            return sresp
                        finally:
                            try:
                                await sresp.write_eof()
                            except Exception:
                                pass

                    # Non-streaming path continues below
                    text = await resp.text()
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