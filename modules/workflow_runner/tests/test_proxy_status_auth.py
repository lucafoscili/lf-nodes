"""Proxy readiness uses POST's existing gate without credentials or inference."""

import importlib.util
import json
import sys
import types
from pathlib import Path
from unittest.mock import Mock

import pytest
from aiohttp.test_utils import make_mocked_request


_SECRET = "unit-test-proxy-secret"
_HEADER = "X-LF-Proxy-Secret"


@pytest.fixture
def proxy_modules(monkeypatch):
    """Load only the proxy code, with inert config, routes, and upstream calls."""
    base = Path(__file__).resolve().parents[1]
    prefix = "lf_nodes.modules.workflow_runner"
    for name in (
        "lf_nodes", "lf_nodes.modules", prefix,
        f"{prefix}.services", f"{prefix}.controllers",
    ):
        package = types.ModuleType(name)
        package.__path__ = []
        monkeypatch.setitem(sys.modules, name, package)

    config = types.ModuleType(f"{prefix}.config")
    config.API_ROUTE_PREFIX = "/lf-nodes"
    config.get_settings = lambda: types.SimpleNamespace(
        PROXY_RATE_LIMIT_REQUESTS=60,
        PROXY_RATE_LIMIT_WINDOW_SECONDS=60,
    )
    monkeypatch.setitem(sys.modules, config.__name__, config)
    job_store = types.ModuleType(f"{prefix}.services.job_store")
    monkeypatch.setitem(sys.modules, job_store.__name__, job_store)

    server = types.ModuleType("server")
    routes = types.SimpleNamespace(
        get=lambda _path: lambda function: function,
        post=lambda _path: lambda function: function,
    )
    server.PromptServer = types.SimpleNamespace(instance=types.SimpleNamespace(routes=routes))
    monkeypatch.setitem(sys.modules, "server", server)

    # A test value short-circuits file-backed secret loading at module import.
    # The real runtime config and any operator secret files are never loaded.
    monkeypatch.setenv("LF_PROXY_SECRET", _SECRET)

    def load(name, relative_path):
        spec = importlib.util.spec_from_file_location(name, base / relative_path)
        module = importlib.util.module_from_spec(spec)
        monkeypatch.setitem(sys.modules, name, module)
        spec.loader.exec_module(module)
        return module

    service = load(f"{prefix}.services.proxy_service", "services/proxy_service.py")
    controller = load(f"{prefix}.controllers.proxy_controller", "controllers/proxy_controller.py")
    monkeypatch.setattr(service, "_read_secret", Mock(return_value="configured-test-value"))
    monkeypatch.setattr(
        controller.aiohttp,
        "ClientSession",
        Mock(side_effect=AssertionError("Provider requests are forbidden in these tests.")),
    )
    return service, controller


def _request(method="GET", *, provided=None, service="kobold", headers=None):
    request_headers = dict(headers or {})
    if provided is not None:
        request_headers[_HEADER] = provided
    return make_mocked_request(
        method,
        f"/api/lf-nodes/proxy/{service}",
        headers=request_headers,
        match_info={"service": service, "proxypath": "v1/chat/completions"},
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("provided", (None, "", "incorrect"))
async def test_status_requires_the_configured_proxy_secret(proxy_modules, provided):
    service, controller = proxy_modules

    response = await controller.proxy_service_status(_request(provided=provided))

    assert response.status == 401
    assert json.loads(response.text) == {
        "service": "kobold",
        "ready": False,
        "detail": "unauthorized",
        "reason": "proxy_authentication_required",
    }
    assert _SECRET not in response.text
    service._read_secret.assert_not_called()
    controller.aiohttp.ClientSession.assert_not_called()


@pytest.mark.asyncio
async def test_runner_session_does_not_replace_the_proxy_secret(proxy_modules):
    _, controller = proxy_modules

    response = await controller.proxy_service_status(_request(headers={
        "Cookie": "LF_SESSION=unit-test-session",
        "Authorization": "Bearer unit-test-token",
    }))

    assert response.status == 401
    assert json.loads(response.text)["ready"] is False


@pytest.mark.asyncio
async def test_status_authentication_precedes_service_lookup(proxy_modules):
    service, controller = proxy_modules

    response = await controller.proxy_service_status(
        _request(service="not-a-configured-service")
    )

    assert response.status == 401
    assert json.loads(response.text) == {
        "service": "not-a-configured-service",
        "ready": False,
        "detail": "unauthorized",
        "reason": "proxy_authentication_required",
    }
    service._read_secret.assert_not_called()


@pytest.mark.asyncio
async def test_correct_header_reports_configured_upstream_without_contacting_it(proxy_modules):
    service, controller = proxy_modules

    response = await controller.proxy_service_status(_request(provided=_SECRET))

    assert response.status == 200
    assert json.loads(response.text) == {"service": "kobold", "ready": True}
    service._read_secret.assert_called_once_with("KOBOLDCPP_BASE", "KOBOLDCPP_BASE_FILE")
    controller.aiohttp.ClientSession.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("secret", (None, ""))
@pytest.mark.parametrize("provided", (None, "incorrect"))
async def test_secret_disabled_status_keeps_existing_behavior(proxy_modules, secret, provided):
    service, controller = proxy_modules
    service.PROXY_SECRET = secret

    response = await controller.proxy_service_status(_request(provided=provided))

    assert response.status == 200
    assert json.loads(response.text) == {"service": "kobold", "ready": True}


@pytest.mark.asyncio
@pytest.mark.parametrize("secret", (_SECRET, None))
@pytest.mark.parametrize("name, missing", (("kobold", "KOBOLDCPP_BASE"), ("openai", "OPENAI_API_KEY")))
async def test_missing_upstream_config_still_reports_503(proxy_modules, secret, name, missing):
    service, controller = proxy_modules
    service.PROXY_SECRET = secret
    service._read_secret.return_value = None

    response = await controller.proxy_service_status(_request(provided=_SECRET, service=name))

    assert response.status == 503
    assert json.loads(response.text) == {
        "service": name, "ready": False, "reason": f"missing {missing}",
    }
    controller.aiohttp.ClientSession.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("handler_name", ("proxy_service", "proxy_service_with_path"))
@pytest.mark.parametrize("secret", (_SECRET, None))
@pytest.mark.parametrize("provided", (None, "incorrect", _SECRET))
async def test_both_post_gates_keep_the_existing_policy(proxy_modules, handler_name, secret, provided):
    service, controller = proxy_modules
    service.PROXY_SECRET = secret
    service._check_rate_limit = Mock(return_value=(False, 7))
    expected_authorized = not secret or provided == secret

    response = await getattr(controller, handler_name)(_request("POST", provided=provided))

    if expected_authorized:
        assert response.status == 429
        assert json.loads(response.text) == {"detail": "rate_limited"}
        assert response.headers["Retry-After"] == "7"
        service._check_rate_limit.assert_called_once()
    else:
        assert response.status == 401
        assert json.loads(response.text) == {"detail": "unauthorized"}
        service._check_rate_limit.assert_not_called()
    service._read_secret.assert_not_called()
    controller.aiohttp.ClientSession.assert_not_called()
