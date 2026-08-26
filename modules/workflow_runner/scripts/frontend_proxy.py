"""
Lightweight reverse proxy for exposing only the workflow-runner endpoints.

Run this alongside ComfyUI and forward the proxy port instead of Comfy's port.

Usage:
  python frontend_proxy.py

Configuration (env):
  PROXY_FRONTEND_PORT - port to bind (default 9188)
  COMFY_BACKEND_URL - backend Comfy base URL (default http://127.0.0.1:8188)
  PROXY_MAX_REQUEST_SIZE_MB - maximum proxied request body size in MiB (default 100)
  PROXY_ALLOWED_PREFIXES - comma-separated allowed path prefixes (optional)
  PROXY_CONNECT_TIMEOUT_SECONDS - upstream connection timeout (default 5)
  PROXY_READ_TIMEOUT_SECONDS - upstream socket-read timeout (default 30)
  PROXY_TOTAL_TIMEOUT_SECONDS - whole upstream request timeout (default 60)

This proxy forwards only configured prefixes and returns 403 for everything else.
It forwards headers, cookies and body and preserves response status and content-type.
"""
import asyncio
import logging
import ssl

from aiohttp import ClientSession, ClientTimeout, web
from pathlib import Path
import importlib.util

try:
    from ...utils.env import bool_env, int_env, list_env, maybe_load_dotenv, str_env
except Exception:
    env_path = Path(__file__).resolve().parents[2] / "utils" / "env.py"
    if env_path.exists():
        spec = importlib.util.spec_from_file_location("lf_nodes.modules.utils.env", str(env_path))
        env_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(env_mod)
        bool_env = env_mod.bool_env
        int_env = env_mod.int_env
        list_env = env_mod.list_env
        maybe_load_dotenv = env_mod.maybe_load_dotenv
        str_env = env_mod.str_env
    else:
        raise

# region Constants
DEFAULT_PREFIXES = [
    "/favicon.ico",
    "/history",
    "/models",
    "/prompt",
    "/queue",
    "/view",
    "/api/lf-nodes/fonts",
    "/api/lf-nodes/js",
    "/api/lf-nodes/proxy",
    "/api/lf-nodes/run",
    "/api/lf-nodes/static",
    "/api/lf-nodes/static-workflow-runner",
    "/api/lf-nodes/submissions",
    "/api/lf-nodes/upload",
    "/api/lf-nodes/workflow-runner",
    "/api/lf-nodes/workflow-runner/verify",
    "/api/lf-nodes/workflows",
]

repo_root = Path(__file__).resolve().parents[3]
logging.debug("Determined repo root: %s", repo_root)
maybe_load_dotenv(repo_root / ".env")

DEFAULT_BACKEND = str_env("COMFY_BACKEND_URL", "http://127.0.0.1:8188")
FRONTEND_PORT = int_env("PROXY_FRONTEND_PORT", 9188)
PROXY_MAX_REQUEST_SIZE_MB = max(1, int_env("PROXY_MAX_REQUEST_SIZE_MB", 100))
PROXY_MAX_REQUEST_SIZE_BYTES = PROXY_MAX_REQUEST_SIZE_MB * 1024 * 1024
_allowed = list_env("PROXY_ALLOWED_PREFIXES")
if _allowed:
    ALLOWED_PREFIXES = [p.strip() for p in _allowed if p.strip()]
else:
    ALLOWED_PREFIXES = DEFAULT_PREFIXES
PROXY_DEBUG = bool_env("WORKFLOW_RUNNER_DEBUG", False)
PROXY_SSL_CERT =  str_env("PROXY_SSL_CERT")
PROXY_SSL_KEY =  str_env("PROXY_SSL_KEY")
PROXY_SSL_KEY_PASSWORD = str_env("PROXY_SSL_KEY_PASSWORD")
PROXY_STREAMING_ONLY_PROXY = bool_env("PROXY_STREAMING_ONLY_PROXY", True)
PROXY_CONNECT_TIMEOUT_SECONDS = max(1, int_env("PROXY_CONNECT_TIMEOUT_SECONDS", 5))
PROXY_READ_TIMEOUT_SECONDS = max(1, int_env("PROXY_READ_TIMEOUT_SECONDS", 30))
PROXY_TOTAL_TIMEOUT_SECONDS = max(1, int_env("PROXY_TOTAL_TIMEOUT_SECONDS", 60))
logging.basicConfig(level=logging.DEBUG if PROXY_DEBUG else logging.INFO, format="[frontend-proxy] %(levelname)s: %(message)s")

RUNNER_SSE_PATHS = frozenset(
    {
        "/api/lf-nodes/run/events",
        "/api/lf-nodes/workflow-runner/events",
    }
)
_STREAMING_ROUTE_ROOTS = (
    "/api/lf-nodes/proxy",
    "/api/lf-nodes/run",
    "/api/lf-nodes/queue",
)
_STREAM_CHUNK_SIZE_BYTES = 64 * 1024
# endregion

# region Main handler
def _normalize_response_header(path: str, name: str, value: str) -> str:
    """Normalize media types that strict browsers will not sniff for us."""
    if path == "/view" and name.lower() == "content-type":
        media_type, separator, parameters = value.partition(";")
        if media_type.strip().lower() == "audio/x-flac":
            return "audio/flac" + (separator + parameters if separator else "")
    return value


async def health(_request: web.Request) -> web.Response:
    """Report proxy liveness without contacting the Comfy backend."""
    return web.json_response({"status": "ok"}, status=200)


async def handle(request: web.Request) -> web.Response:
    path = request.rel_url.path
    if path == "/favicon.ico":
        return web.Response(status=204)
    for prefix in ALLOWED_PREFIXES:
        if _path_is_within(path, prefix):
            return await proxy_request(request)

    logging.warning("Blocked request to disallowed path %s from %s", path, request.remote)
    return web.json_response({"detail": "forbidden"}, status=403)
# endregion

# region Proxy logic
def _is_unbounded_stream_request(method: str, path: str) -> bool:
    """Return whether an exact GET route may legitimately stay idle indefinitely."""
    return method.upper() == "GET" and (path == "/view" or path in RUNNER_SSE_PATHS)


def _path_is_within(path: str, root: str) -> bool:
    """Match a route root without also matching lookalike path prefixes."""
    return path == root or path.startswith(f"{root}/")


def _path_allows_streaming(path: str) -> bool:
    """Apply the opt-in streaming gate to known endpoint boundaries only."""
    return (
        path == "/view"
        or path in RUNNER_SSE_PATHS
        or any(_path_is_within(path, root) for root in _STREAMING_ROUTE_ROOTS)
    )


def _stream_idle_timeout(path: str) -> float:
    """Bound silence on long-lived routes without imposing a total lifetime.

    Runner SSE emits a heartbeat every 15 seconds, so 45 seconds tolerates two
    missed beats before treating the upstream as wedged. Media reads get a
    wider two-minute silence window because a large file can pause between
    chunks on a busy disk.
    """

    minimum = 120 if path == "/view" else 45
    return float(max(PROXY_READ_TIMEOUT_SECONDS, minimum))


def _upstream_timeout(*, stream_path: str | None = None) -> ClientTimeout:
    """Build an explicit timeout for each independent upstream request."""

    streaming = stream_path is not None
    return ClientTimeout(
        total=None if streaming else PROXY_TOTAL_TIMEOUT_SECONDS,
        connect=PROXY_CONNECT_TIMEOUT_SECONDS,
        sock_connect=PROXY_CONNECT_TIMEOUT_SECONDS,
        sock_read=(
            _stream_idle_timeout(stream_path)
            if streaming
            else PROXY_READ_TIMEOUT_SECONDS
        ),
    )


def _upstream_error_response() -> web.Response:
    """Return a stable public error contract; details stay in server logs."""
    return web.json_response({"detail": "upstream_error"}, status=502)


async def proxy_request(request: web.Request) -> web.Response:
    upstream = f"{DEFAULT_BACKEND}{request.rel_url}"
    method = request.method
    req_path = request.rel_url.path
    unbounded_stream = _is_unbounded_stream_request(method, req_path)
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
    if method in ("POST", "PUT", "PATCH"):
        try:
            data = await request.read()
        except web.HTTPRequestEntityTooLarge:
            logging.warning(
                "Rejected request body exceeding %s MiB from %s for %s",
                PROXY_MAX_REQUEST_SIZE_MB,
                request.remote,
                request.rel_url,
            )
            return web.json_response({"detail": "request_too_large"}, status=413)
        except Exception:
            logging.exception("Failed to read request body from %s for %s", request.remote, request.rel_url)
            return web.json_response({"detail": "invalid_request_body"}, status=400)

    # A session per inbound request keeps connection state isolated: a stalled
    # backend exchange cannot occupy a shared connector slot or poison later
    # requests when the backend comes back. Preserve upstream content codings
    # byte-for-byte: forwarding Content-Encoding after aiohttp transparently
    # decoded the body would give the downstream client invalid framing.
    async with ClientSession(
        timeout=_upstream_timeout(stream_path=req_path if unbounded_stream else None),
        auto_decompress=False,
        skip_auto_headers={"Accept-Encoding"},
    ) as sess:
        try:
            async with sess.request(method, upstream, data=data, headers=headers, allow_redirects=False) as resp:
                # Determine if we should stream the response instead of buffering it.
                content_type = resp.headers.get("Content-Type", "")
                transfer_enc = resp.headers.get("Transfer-Encoding", "")
                # Exact SSE and /view requests must stream even when the
                # upstream supplies Content-Length instead of chunked framing.
                should_stream = unbounded_stream
                try:
                    if content_type.lower().startswith("text/event-stream"):
                        should_stream = True
                    elif transfer_enc.lower() == "chunked":
                        should_stream = True
                except Exception:
                    # Header parsing must not undo route-required streaming.
                    should_stream = unbounded_stream

                if PROXY_STREAMING_ONLY_PROXY:
                    allowed_by_path = _path_allows_streaming(req_path)
                else:
                    allowed_by_path = True

                if should_stream:
                    if not allowed_by_path:
                        logging.info("Streaming response blocked by gate for path %s; buffering instead", req_path)
                        # fall back to buffered response (do nothing here)
                    else:
                        sresp = web.StreamResponse(status=resp.status, reason=resp.reason)
                        for name, value in resp.headers.items():
                            lname = name.lower()
                            if lname in ("connection", "keep-alive", "proxy-authenticate", "proxy-authorization", "te", "trailers", "transfer-encoding", "upgrade"):
                                continue
                            value = _normalize_response_header(req_path, name, value)
                            try:
                                sresp.headers.add(name, value)
                            except Exception:
                                sresp.headers[name] = value

                        await sresp.prepare(request)
                        try:
                            async for chunk in resp.content.iter_chunked(_STREAM_CHUNK_SIZE_BYTES):
                                if not chunk:
                                    continue
                                try:
                                    await sresp.write(chunk)
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

                body = await resp.read()
                response = web.Response(status=resp.status, body=body)
                for name, value in resp.headers.items():
                    lname = name.lower()
                    if lname in ("connection", "keep-alive", "proxy-authenticate", "proxy-authorization", "te", "trailers", "transfer-encoding", "upgrade"):
                        continue
                    value = _normalize_response_header(req_path, name, value)
                    try:
                        response.headers.add(name, value)
                    except Exception:
                        response.headers[name] = value

                if resp.status >= 400:
                    logging.warning("Upstream returned %s for %s -> %s", resp.status, request.remote, upstream)

                return response
        except asyncio.TimeoutError as exc:
            logging.warning("Upstream request to %s timed out: %s", upstream, exc)
            return _upstream_error_response()
        except Exception as exc:
            logging.exception("Upstream request to %s failed: %s", upstream, exc)
            return _upstream_error_response()
# endregion

# region App startup
def create_app() -> web.Application:
    """Create the proxy application with a configurable 100 MiB default body cap."""
    app = web.Application(client_max_size=PROXY_MAX_REQUEST_SIZE_BYTES)
    # Register liveness before the catch-all proxy routes so it never depends
    # on backend availability or timeout state.
    app.router.add_get("/health", health)
    app.router.add_route("GET", "/{path:.*}", handle)
    app.router.add_route("POST", "/{path:.*}", handle)
    app.router.add_route("PUT", "/{path:.*}", handle)
    app.router.add_route("PATCH", "/{path:.*}", handle)
    app.router.add_route("DELETE", "/{path:.*}", handle)
    return app


async def start_app() -> None:
    app = create_app()

    runner = web.AppRunner(app)
    await runner.setup()
    # If TLS cert+key are provided, create an SSL context and serve HTTPS
    ssl_context = None
    if PROXY_SSL_CERT and PROXY_SSL_KEY:
        try:
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            if PROXY_SSL_KEY_PASSWORD:
                ssl_context.load_cert_chain(PROXY_SSL_CERT, PROXY_SSL_KEY, password=PROXY_SSL_KEY_PASSWORD)
            else:
                ssl_context.load_cert_chain(PROXY_SSL_CERT, PROXY_SSL_KEY)
            logging.info("Loaded SSL cert %s and key %s; serving HTTPS", PROXY_SSL_CERT, PROXY_SSL_KEY)
        except Exception as e:
            logging.exception("Failed to load SSL cert/key: %s", e)
            raise

    site = web.TCPSite(runner, "0.0.0.0", FRONTEND_PORT, ssl_context=ssl_context)
    scheme = "https" if ssl_context else "http"
    logging.info("Starting frontend proxy on %s://0.0.0.0:%s forwarding to %s", scheme, FRONTEND_PORT, DEFAULT_BACKEND)
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
