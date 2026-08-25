"""Focused route-boundary tests for the standalone frontend proxy."""

import importlib.util
from pathlib import Path
from urllib.parse import quote

import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer


def load_frontend_proxy_module():
    script = Path(__file__).resolve().parents[1] / "scripts" / "frontend_proxy.py"
    spec = importlib.util.spec_from_file_location("frontend_proxy_routes_under_test", script)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@pytest.mark.asyncio
async def test_proxy_forwards_cancel_for_encoded_submission_id(monkeypatch):
    proxy = load_frontend_proxy_module()
    monkeypatch.setattr(proxy, "ALLOWED_PREFIXES", proxy.DEFAULT_PREFIXES)
    submission_id = "batch:take.001"
    encoded_id = quote(submission_id, safe="")
    received = {}

    async def cancel(request):
        received["submission_id"] = request.match_info["submission_id"]
        return web.json_response(
            {"submission_id": request.match_info["submission_id"]},
            status=202,
        )

    upstream = TestServer(web.Application())
    upstream.app.router.add_post(
        "/api/lf-nodes/submissions/{submission_id}/cancel",
        cancel,
    )
    await upstream.start_server()
    monkeypatch.setattr(
        proxy,
        "DEFAULT_BACKEND",
        str(upstream.make_url("/")).rstrip("/"),
    )

    client = TestClient(TestServer(proxy.create_app()))
    await client.start_server()
    try:
        path = f"/api/lf-nodes/submissions/{encoded_id}/cancel"
        assert encoded_id == "batch%3Atake.001"
        response = await client.post(path)

        assert response.status == 202
        assert await response.json() == {"submission_id": submission_id}
        assert received == {"submission_id": submission_id}
    finally:
        await client.close()
        await upstream.close()


@pytest.mark.asyncio
async def test_submission_route_allowlist_rejects_lookalike_prefix(monkeypatch):
    proxy = load_frontend_proxy_module()
    monkeypatch.setattr(proxy, "ALLOWED_PREFIXES", proxy.DEFAULT_PREFIXES)
    upstream_calls = 0

    async def unexpected(_request):
        nonlocal upstream_calls
        upstream_calls += 1
        return web.Response(text="unexpected")

    upstream = TestServer(web.Application())
    upstream.app.router.add_post("/{path:.*}", unexpected)
    await upstream.start_server()
    monkeypatch.setattr(
        proxy,
        "DEFAULT_BACKEND",
        str(upstream.make_url("/")).rstrip("/"),
    )

    client = TestClient(TestServer(proxy.create_app()))
    await client.start_server()
    try:
        response = await client.post(
            "/api/lf-nodes/submissions-archive/batch%3Atake.001/cancel"
        )

        assert response.status == 403
        assert await response.json() == {"detail": "forbidden"}
        assert upstream_calls == 0
    finally:
        await client.close()
        await upstream.close()
