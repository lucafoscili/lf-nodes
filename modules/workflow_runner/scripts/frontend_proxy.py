"""
Lightweight reverse proxy for exposing only the workflow-runner endpoints.

Run this alongside ComfyUI and forward the proxy port instead of Comfy's port.

Usage:
  python frontend_proxy.py

Configuration (env):
  PROXY_FRONTEND_PORT - port to bind (default 9188)
  COMFY_BACKEND_URL - backend Comfy base URL (default http://127.0.0.1:8188)
  PROXY_ALLOWED_PREFIXES - comma-separated allowed path prefixes (optional)

This proxy forwards only configured prefixes and returns 403 for everything else.
It forwards headers, cookies and body and preserves response status and content-type.
"""
import asyncio
import logging
import os

from aiohttp import web, ClientSession

# region Constants
DEFAULT_BACKEND = os.environ.get("COMFY_BACKEND_URL", "http://127.0.0.1:8188")
FRONTEND_PORT = int(os.environ.get("PROXY_FRONTEND_PORT", "9188"))
DEFAULT_PREFIXES = [
    "/queue",
    "/view",
    "/api/lf-nodes/js",
    "/api/lf-nodes/proxy",
    "/api/lf-nodes/run",
    "/api/lf-nodes/static",
    "/api/lf-nodes/static-workflow-runner",
    "/api/lf-nodes/upload",
    "/api/lf-nodes/workflow-runner",
    "/api/lf-nodes/workflow-runner/verify",
    "/api/lf-nodes/workflows",
]

_allowed = os.environ.get("PROXY_ALLOWED_PREFIXES")
if _allowed:
    ALLOWED_PREFIXES = [p.strip() for p in _allowed.split(",") if p.strip()]
else:
    ALLOWED_PREFIXES = DEFAULT_PREFIXES

PROXY_DEBUG = os.environ.get("WORKFLOW_RUNNER_DEBUG", "0").lower() in ("1", "true", "yes")
logging.basicConfig(level=logging.DEBUG if PROXY_DEBUG else logging.INFO, format="[frontend-proxy] %(levelname)s: %(message)s")
# endregion

# region Main handler
async def handle(request: web.Request) -> web.Response:
    path = request.rel_url.path
    if path == "/health":
        return web.json_response({"status": "ok"}, status=200)
    for prefix in ALLOWED_PREFIXES:
        if path.startswith(prefix):
            return await proxy_request(request)

    logging.warning("Blocked request to disallowed path %s from %s", path, request.remote)
    return web.json_response({"detail": "forbidden"}, status=403)
# endregion

# region Proxy logic
async def proxy_request(request: web.Request) -> web.Response:
    upstream = f"{DEFAULT_BACKEND}{request.rel_url}"
    method = request.method
    headers = dict(request.headers)
    for h in ("Host", "Content-Length", "Transfer-Encoding", "Connection"):
        headers.pop(h, None)

    original_host = request.headers.get('Host')
    if original_host:
        headers['Host'] = original_host

    existing_xff = request.headers.get('X-Forwarded-For')
    if request.remote:
        headers['X-Forwarded-For'] = (existing_xff + ", " if existing_xff else "") + str(request.remote)
    elif existing_xff:
        headers['X-Forwarded-For'] = existing_xff

    if 'X-Forwarded-Proto' not in headers:
        xf = request.headers.get('X-Forwarded-Proto')
        if xf:
            headers['X-Forwarded-Proto'] = xf
        else:
            if original_host and ('devtunnels.ms' in original_host or original_host.endswith('.trycloudflare.com') or original_host.endswith('.ngrok.io')):
                headers['X-Forwarded-Proto'] = 'https'
            else:
                headers['X-Forwarded-Proto'] = request.scheme

    data = None
    try:
        if method in ("POST", "PUT", "PATCH"):
            data = await request.read()
    except Exception:
        data = None

    async with ClientSession() as sess:
        try:
            async with sess.request(method, upstream, data=data, headers=headers, allow_redirects=False) as resp:
                # Determine if we should stream the response instead of buffering it.
                content_type = resp.headers.get("Content-Type", "")
                transfer_enc = resp.headers.get("Transfer-Encoding", "")
                should_stream = False
                try:
                    if content_type.lower().startswith("text/event-stream"):
                        should_stream = True
                    elif transfer_enc.lower() == "chunked":
                        should_stream = True
                except Exception:
                    should_stream = False

                # If streaming, forward chunks directly to the caller without
                # buffering the entire response in memory. Preserve most
                # response headers except hop-by-hop headers.
                if should_stream:
                    sresp = web.StreamResponse(status=resp.status, reason=resp.reason)
                    # copy headers (skip hop-by-hop)
                    for name, value in resp.headers.items():
                        lname = name.lower()
                        if lname in ("connection", "keep-alive", "proxy-authenticate", "proxy-authorization", "te", "trailers", "transfer-encoding", "upgrade"):
                            continue
                        try:
                            sresp.headers.add(name, value)
                        except Exception:
                            sresp.headers[name] = value

                    await sresp.prepare(request)
                    try:
                        async for chunk in resp.content.iter_chunked(1024):
                            if not chunk:
                                continue
                            try:
                                await sresp.write(chunk)
                                await sresp.drain()
                            except (ConnectionResetError, asyncio.CancelledError):
                                break
                            except Exception:
                                logging.exception("Failed to write chunk to client for %s -> %s", request.remote, upstream)
                        return sresp
                    finally:
                        try:
                            await sresp.write_eof()
                        except Exception:
                            pass

                # Non-streaming: buffer and return as a normal response
                body = await resp.read()
                response = web.Response(status=resp.status, body=body)
                for name, value in resp.headers.items():
                    lname = name.lower()
                    if lname in ("connection", "keep-alive", "proxy-authenticate", "proxy-authorization", "te", "trailers", "transfer-encoding", "upgrade"):
                        continue
                    try:
                        response.headers.add(name, value)
                    except Exception:
                        response.headers[name] = value

                if resp.status >= 400:
                    logging.warning("Upstream returned %s for %s -> %s", resp.status, request.remote, upstream)

                return response
        except Exception as e:
            logging.exception("Upstream request to %s failed: %s", upstream, e)
            if PROXY_DEBUG:
                return web.json_response({"detail": "upstream_error", "error": str(e)}, status=502)
            return web.json_response({"detail": "upstream_error"}, status=502)
# endregion

# region App startup
async def start_app() -> None:
    app = web.Application()
    app.router.add_route("GET", "/{path:.*}", handle)
    app.router.add_route("POST", "/{path:.*}", handle)
    app.router.add_route("PUT", "/{path:.*}", handle)
    app.router.add_route("PATCH", "/{path:.*}", handle)
    app.router.add_route("DELETE", "/{path:.*}", handle)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", FRONTEND_PORT)
    logging.info("Starting frontend proxy on port %s forwarding to %s", FRONTEND_PORT, DEFAULT_BACKEND)
    await site.start()

    # run forever
    while True:
        await asyncio.sleep(3600)
# endregion

if __name__ == "__main__":
    try:
        asyncio.run(start_app())
    except KeyboardInterrupt:
        logging.info("Shutting down frontend proxy")
