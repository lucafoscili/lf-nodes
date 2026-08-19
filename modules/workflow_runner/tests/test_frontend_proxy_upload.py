"""Regression tests for multipart bodies forwarded by the standalone frontend proxy."""

import importlib.util
from pathlib import Path

import pytest
from aiohttp import FormData, web
from aiohttp.test_utils import TestClient, TestServer


def load_frontend_proxy_module():
    script = Path(__file__).resolve().parents[1] / "scripts" / "frontend_proxy.py"
    spec = importlib.util.spec_from_file_location("frontend_proxy_under_test", script)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@pytest.mark.asyncio
async def test_proxy_forwards_multipart_bodies_larger_than_aiohttp_default(monkeypatch):
    proxy = load_frontend_proxy_module()
    received = {}

    async def upload(request):
        received["content_type"] = request.headers["Content-Type"]
        received["body"] = await request.read()
        return web.Response(text="forwarded")

    upstream = TestServer(web.Application(client_max_size=2 * 1024 * 1024))
    upstream.app.router.add_post("/api/lf-nodes/upload", upload)
    await upstream.start_server()
    monkeypatch.setattr(proxy, "DEFAULT_BACKEND", str(upstream.make_url("/")).rstrip("/"))

    client = TestClient(TestServer(proxy.create_app()))
    await client.start_server()
    try:
        form = FormData()
        form.add_field(
            "file",
            b"x" * (1024 * 1024 + 1),
            filename="reference.png",
            content_type="image/png",
        )

        response = await client.post("/api/lf-nodes/upload", data=form)

        assert response.status == 200
        assert await response.text() == "forwarded"
        assert received["content_type"].startswith("multipart/form-data; boundary=")
        assert len(received["body"]) > 1024 * 1024
        assert b'filename="reference.png"' in received["body"]
    finally:
        await client.close()
        await upstream.close()


@pytest.mark.asyncio
async def test_proxy_rejects_over_cap_body_without_calling_upstream(monkeypatch):
    proxy = load_frontend_proxy_module()
    upstream_calls = 0

    async def upload(_request):
        nonlocal upstream_calls
        upstream_calls += 1
        return web.Response(text="unexpected")

    upstream = TestServer(web.Application())
    upstream.app.router.add_post("/api/lf-nodes/upload", upload)
    await upstream.start_server()
    monkeypatch.setattr(proxy, "DEFAULT_BACKEND", str(upstream.make_url("/")).rstrip("/"))
    monkeypatch.setattr(proxy, "PROXY_MAX_REQUEST_SIZE_BYTES", 1024)

    client = TestClient(TestServer(proxy.create_app()))
    await client.start_server()
    try:
        form = FormData()
        form.add_field("file", b"x" * 2048, filename="reference.png", content_type="image/png")

        response = await client.post("/api/lf-nodes/upload", data=form)

        assert response.status == 413
        assert await response.json() == {"detail": "request_too_large"}
        assert upstream_calls == 0
    finally:
        await client.close()
        await upstream.close()


@pytest.mark.asyncio
async def test_proxy_normalizes_flac_view_mime_for_strict_browsers(monkeypatch):
    proxy = load_frontend_proxy_module()

    async def view(_request):
        return web.Response(
            body=b"fLaC",
            headers={
                "Content-Type": "audio/x-flac",
                "X-Content-Type-Options": "nosniff",
                "Accept-Ranges": "bytes",
            },
            status=206,
        )

    upstream = TestServer(web.Application())
    upstream.app.router.add_get("/view", view)
    await upstream.start_server()
    monkeypatch.setattr(proxy, "DEFAULT_BACKEND", str(upstream.make_url("/")).rstrip("/"))

    client = TestClient(TestServer(proxy.create_app()))
    await client.start_server()
    try:
        response = await client.get("/view?filename=mix.flac&type=output")

        assert response.status == 206
        assert response.headers["Content-Type"] == "audio/flac"
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["Accept-Ranges"] == "bytes"
        assert await response.read() == b"fLaC"
    finally:
        await client.close()
        await upstream.close()
