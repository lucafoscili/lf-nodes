"""Focused outage and recovery tests for the standalone frontend proxy."""

import asyncio
import importlib.util
from contextlib import suppress
from pathlib import Path

import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer, unused_port


def load_frontend_proxy_module():
    script = Path(__file__).resolve().parents[1] / "scripts" / "frontend_proxy.py"
    spec = importlib.util.spec_from_file_location("frontend_proxy_resilience_under_test", script)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def set_short_upstream_timeouts(monkeypatch, proxy):
    monkeypatch.setattr(proxy, "PROXY_CONNECT_TIMEOUT_SECONDS", 0.1)
    monkeypatch.setattr(proxy, "PROXY_READ_TIMEOUT_SECONDS", 0.1)
    monkeypatch.setattr(proxy, "PROXY_TOTAL_TIMEOUT_SECONDS", 0.2)


def test_proxy_configures_connect_read_and_total_timeouts(monkeypatch):
    proxy = load_frontend_proxy_module()
    set_short_upstream_timeouts(monkeypatch, proxy)

    timeout = proxy._upstream_timeout()

    assert timeout.connect == 0.1
    assert timeout.sock_connect == 0.1
    assert timeout.sock_read == 0.1
    assert timeout.total == 0.2


@pytest.mark.parametrize(
    "path",
    [
        "/api/lf-nodes/run/events",
        "/api/lf-nodes/workflow-runner/events",
        "/view",
    ],
)
def test_exact_long_lived_get_routes_have_bounded_idle_but_no_total_deadline(
    monkeypatch,
    path,
):
    """Long streams may live forever, but a silent wedged upstream may not."""
    proxy = load_frontend_proxy_module()
    set_short_upstream_timeouts(monkeypatch, proxy)

    timeout = proxy._upstream_timeout(stream_path=path)

    assert timeout.connect == 0.1
    assert timeout.sock_connect == 0.1
    assert timeout.sock_read == (120 if path == "/view" else 45)
    assert timeout.total is None


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("POST", "/view"),
        ("GET", "/viewer"),
        ("GET", "/api/lf-nodes/run/events/extra"),
        ("GET", "/api/lf-nodes/workflow-runner/events-extra"),
        ("GET", "/api/lf-nodes/submissions/id/events"),
    ],
)
def test_unbounded_timeout_does_not_spread_to_route_lookalikes(method, path):
    proxy = load_frontend_proxy_module()

    assert proxy._is_unbounded_stream_request(method, path) is False


@pytest.mark.asyncio
async def test_hung_upstream_does_not_block_health_or_other_requests(monkeypatch):
    proxy = load_frontend_proxy_module()
    set_short_upstream_timeouts(monkeypatch, proxy)
    hang_started = asyncio.Event()
    release_hang = asyncio.Event()

    async def history(_request):
        hang_started.set()
        await release_hang.wait()
        return web.json_response({"status": "recovered"})

    async def queue(_request):
        return web.json_response({"queue_running": []})

    upstream = TestServer(web.Application())
    upstream.app.router.add_get("/history", history)
    upstream.app.router.add_get("/queue", queue)
    await upstream.start_server()
    monkeypatch.setattr(proxy, "DEFAULT_BACKEND", str(upstream.make_url("/")).rstrip("/"))

    client = TestClient(TestServer(proxy.create_app()))
    await client.start_server()
    hung_request = asyncio.create_task(client.get("/history"))
    try:
        await asyncio.wait_for(hang_started.wait(), timeout=1)

        health_response = await asyncio.wait_for(client.get("/health"), timeout=0.5)
        queue_response = await asyncio.wait_for(client.get("/queue"), timeout=0.5)
        timeout_response = await asyncio.wait_for(hung_request, timeout=1)

        assert health_response.status == 200
        assert await health_response.json() == {"status": "ok"}
        assert queue_response.status == 200
        assert await queue_response.json() == {"queue_running": []}
        assert timeout_response.status == 502
        assert timeout_response.content_type == "application/json"
        assert await timeout_response.json() == {"detail": "upstream_error"}

        release_hang.set()
        recovered_response = await asyncio.wait_for(client.get("/history"), timeout=0.5)
        assert recovered_response.status == 200
        assert await recovered_response.json() == {"status": "recovered"}
    finally:
        release_hang.set()
        if not hung_request.done():
            hung_request.cancel()
            with suppress(asyncio.CancelledError):
                await hung_request
        await client.close()
        await upstream.close()


@pytest.mark.asyncio
async def test_live_proxy_recovers_after_upstream_returns(monkeypatch):
    proxy = load_frontend_proxy_module()
    set_short_upstream_timeouts(monkeypatch, proxy)
    monkeypatch.setattr(proxy, "PROXY_DEBUG", True)

    upstream_port = unused_port()
    monkeypatch.setattr(proxy, "DEFAULT_BACKEND", f"http://127.0.0.1:{upstream_port}")
    client = TestClient(TestServer(proxy.create_app()))
    await client.start_server()
    upstream_runner = None
    try:
        unavailable_response = await asyncio.wait_for(client.get("/queue"), timeout=1)

        assert unavailable_response.status == 502
        assert unavailable_response.content_type == "application/json"
        assert await unavailable_response.json() == {"detail": "upstream_error"}

        async def queue(_request):
            return web.json_response({"status": "available"})

        upstream_app = web.Application()
        upstream_app.router.add_get("/queue", queue)
        upstream_runner = web.AppRunner(upstream_app)
        await upstream_runner.setup()
        await web.TCPSite(upstream_runner, "127.0.0.1", upstream_port).start()

        recovered_response = await asyncio.wait_for(client.get("/queue"), timeout=1)

        assert recovered_response.status == 200
        assert await recovered_response.json() == {"status": "available"}
        health_response = await asyncio.wait_for(client.get("/health"), timeout=0.5)
        assert health_response.status == 200
        assert await health_response.json() == {"status": "ok"}
    finally:
        await client.close()
        if upstream_runner is not None:
            await upstream_runner.cleanup()


@pytest.mark.asyncio
async def test_view_with_content_length_streams_before_slow_body_finishes(monkeypatch):
    """A large media response reaches the client before its final chunk exists."""
    proxy = load_frontend_proxy_module()
    first_body = b"a" * (256 * 1024)
    second_body = b"b" * (256 * 1024)
    first_sent = asyncio.Event()
    release_second = asyncio.Event()

    async def view(request):
        response = web.StreamResponse(
            headers={
                "Content-Type": "video/mp4",
                "Content-Length": str(len(first_body) + len(second_body)),
            }
        )
        await response.prepare(request)
        await response.write(first_body)
        first_sent.set()
        await release_second.wait()
        await response.write(second_body)
        await response.write_eof()
        return response

    upstream = TestServer(web.Application())
    upstream.app.router.add_get("/view", view)
    await upstream.start_server()
    monkeypatch.setattr(proxy, "DEFAULT_BACKEND", str(upstream.make_url("/")).rstrip("/"))

    client = TestClient(TestServer(proxy.create_app()))
    await client.start_server()
    response_task = asyncio.create_task(
        client.get("/view?filename=slow.mp4&type=output")
    )
    try:
        await asyncio.wait_for(first_sent.wait(), timeout=1)

        # If /view were buffered, even the response headers would remain
        # unavailable here until release_second is set.
        response = await asyncio.wait_for(response_task, timeout=1)
        first_received = await asyncio.wait_for(
            response.content.readexactly(len(first_body)),
            timeout=1,
        )

        assert response.status == 200
        assert response.headers["Content-Type"] == "video/mp4"
        assert first_received == first_body
        assert not release_second.is_set()

        release_second.set()
        assert await response.content.read() == second_body
    finally:
        release_second.set()
        if not response_task.done():
            response_task.cancel()
            with suppress(asyncio.CancelledError):
                await response_task
        await client.close()
        await upstream.close()
