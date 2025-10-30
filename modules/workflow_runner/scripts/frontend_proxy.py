"""Lightweight reverse proxy for exposing only the workflow-runner endpoints.

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
from aiohttp import web, ClientSession
import asyncio
import os
import logging

DEFAULT_BACKEND = os.environ.get("COMFY_BACKEND_URL", "http://127.0.0.1:8188")
FRONTEND_PORT = int(os.environ.get("PROXY_FRONTEND_PORT", "9188"))

# Default allowed prefixes (only these are proxied)
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

PROXY_DEBUG = os.environ.get("PROXY_DEBUG", "0").lower() in ("1", "true", "yes")
logging.basicConfig(level=logging.DEBUG if PROXY_DEBUG else logging.INFO, format="[frontend-proxy] %(levelname)s: %(message)s")


async def handle(request: web.Request) -> web.Response:
    path = request.rel_url.path
    # health endpoint for tunnels to probe
    if path == "/health":
        return web.json_response({"status": "ok"}, status=200)
    for prefix in ALLOWED_PREFIXES:
        if path.startswith(prefix):
            return await proxy_request(request)

    logging.warning("Blocked request to disallowed path %s from %s", path, request.remote)
    return web.json_response({"detail": "forbidden"}, status=403)


async def proxy_request(request: web.Request) -> web.Response:
    # Build upstream URL
    upstream = f"{DEFAULT_BACKEND}{request.rel_url}"
    method = request.method
    headers = dict(request.headers)
    # Remove hop-by-hop headers that client session will set
    for h in ("Host", "Content-Length", "Transfer-Encoding", "Connection"):
        headers.pop(h, None)

    # Preserve original host and forwarding info so backend sees the public origin
    original_host = request.headers.get('Host')
    if original_host:
        headers['Host'] = original_host

    # X-Forwarded-For: include client IP and any existing forwarded-for chain
    existing_xff = request.headers.get('X-Forwarded-For')
    if request.remote:
        headers['X-Forwarded-For'] = (existing_xff + ", " if existing_xff else "") + str(request.remote)
    elif existing_xff:
        headers['X-Forwarded-For'] = existing_xff

    # X-Forwarded-Proto: preserve if set, otherwise derive from scheme.
    # If the public Host looks like a tunnel domain, prefer 'https' because the tunnel
    # typically terminates TLS at the provider.
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
                body = await resp.read()
                response = web.Response(status=resp.status, body=body)
                # copy headers from upstream except hop-by-hop
                for name, value in resp.headers.items():
                    lname = name.lower()
                    if lname in ("connection", "keep-alive", "proxy-authenticate", "proxy-authorization", "te", "trailers", "transfer-encoding", "upgrade"):
                        continue
                    # preserve Set-Cookie headers and others
                    try:
                        # CIMultiDict supports add; prefer to add to preserve multiples
                        response.headers.add(name, value)
                    except Exception:
                        response.headers[name] = value

                # log non-2xx upstream responses for debugging
                if resp.status >= 400:
                    logging.warning("Upstream returned %s for %s -> %s", resp.status, request.remote, upstream)

                return response
        except Exception as e:
            logging.exception("Upstream request to %s failed: %s", upstream, e)
            if PROXY_DEBUG:
                return web.json_response({"detail": "upstream_error", "error": str(e)}, status=502)
            return web.json_response({"detail": "upstream_error"}, status=502)


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


if __name__ == "__main__":
    try:
        asyncio.run(start_app())
    except KeyboardInterrupt:
        logging.info("Shutting down frontend proxy")
