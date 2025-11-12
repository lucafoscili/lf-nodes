#!/usr/bin/env python3
"""
Tests for proxy service functionality
"""
import json
import os
from unittest.mock import patch, MagicMock, AsyncMock

import pytest
from aiohttp import web

# import shared test utils from this helpers package
import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "test_utils",
    str(pathlib.Path(__file__).resolve().parent / "helpers" / "test_utils.py"),
)
test_utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(test_utils)

find_workflow_runner_base = test_utils.find_workflow_runner_base


def load_proxy_service_module():
    """Dynamically load the services.proxy_service module for tests."""
    import sys
    import types

    base = find_workflow_runner_base(__file__)

    # Preload package structure entries
    pkg_prefix = "lf_nodes.modules.workflow_runner"
    pkg_parts = [
        "lf_nodes", "lf_nodes.modules", "lf_nodes.modules.workflow_runner",
        "lf_nodes.modules.workflow_runner.services",
    ]
    for p in pkg_parts:
        if p not in sys.modules:
            sys.modules[p] = types.ModuleType(p)

    # Set up services as a package
    services_mod = types.ModuleType("lf_nodes.modules.workflow_runner.services")
    sys.modules["lf_nodes.modules.workflow_runner.services"] = services_mod

    # Import the proxy service
    spec = importlib.util.spec_from_file_location(
        "proxy_service",
        str(base / "services" / "proxy_service.py")
    )
    proxy_service = importlib.util.module_from_spec(spec)
    sys.modules["lf_nodes.modules.workflow_runner.services.proxy_service"] = proxy_service
    spec.loader.exec_module(proxy_service)

    return proxy_service


def test_stability_service_configuration():
    """Test that stability service is properly configured."""
    proxy_service = load_proxy_service_module()

    assert "stability" in proxy_service.SERVICES
    stability_config = proxy_service.SERVICES["stability"]

    assert stability_config["endpoint"] == "https://api.stability.ai/v1/generation/{model}/text-to-image"
    assert stability_config["api_key_env"] == "STABILITY_API_KEY"
    assert stability_config["api_key_header"] == "Authorization"
    assert stability_config["default_model"] == "stable-diffusion-xl-1024-v1-0"
    assert stability_config["timeout"] == 120


def test_build_upstream_and_headers_stability():
    """Test building upstream URL and headers for Stability AI."""
    proxy_service = load_proxy_service_module()

    cfg = proxy_service.SERVICES["stability"]
    body = {"model": "stable-diffusion-v1-6", "prompt": "test prompt"}

    with patch('lf_nodes.modules.workflow_runner.services.proxy_service._read_secret') as mock_read_secret:
        mock_read_secret.return_value = "test_api_key"

        upstream, headers, timeout, forward_body = proxy_service._build_upstream_and_headers(cfg, body, None)

        assert upstream == "https://api.stability.ai/v1/generation/stable-diffusion-v1-6/text-to-image"
        assert headers["Authorization"] == "Bearer test_api_key"
        assert timeout == 120
        assert forward_body == body


def test_build_upstream_and_headers_stability_default_model():
    """Test building upstream URL with default model when none specified."""
    proxy_service = load_proxy_service_module()

    cfg = proxy_service.SERVICES["stability"]
    body = {"prompt": "test prompt"}  # No model specified

    with patch('lf_nodes.modules.workflow_runner.services.proxy_service._read_secret') as mock_read_secret:
        mock_read_secret.return_value = "test_api_key"

        upstream, headers, timeout, forward_body = proxy_service._build_upstream_and_headers(cfg, body, None)

        assert upstream == "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
        assert headers["Authorization"] == "Bearer test_api_key"


def test_read_secret_from_env():
    """Test reading secret from environment variable."""
    proxy_service = load_proxy_service_module()

    with patch.dict(os.environ, {"TEST_API_KEY": "secret_value"}):
        result = proxy_service._read_secret("TEST_API_KEY")
        assert result == "secret_value"


def test_read_secret_from_file():
    """Test reading secret from file."""
    import tempfile

    proxy_service = load_proxy_service_module()

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("file_secret")
        temp_path = f.name

    try:
        with patch.dict(os.environ, {"TEST_API_KEY_FILE": temp_path}):
            result = proxy_service._read_secret("TEST_API_KEY", "TEST_API_KEY_FILE")
            assert result == "file_secret"
    finally:
        os.unlink(temp_path)


def test_check_rate_limit_allowed():
    """Test rate limiting allows requests within limits."""
    proxy_service = load_proxy_service_module()

    cfg = {"rate_limit": {"requests": 10, "window_seconds": 60}}
    client_id = "test_client"
    service = "stability"

    # First request should be allowed
    allowed, retry_after = proxy_service._check_rate_limit(client_id, service, cfg)
    assert allowed is True
    assert retry_after == 0


def test_check_rate_limit_blocked():
    """Test rate limiting blocks requests over limits."""
    proxy_service = load_proxy_service_module()

    cfg = {"rate_limit": {"requests": 1, "window_seconds": 60}}
    client_id = "test_client"
    service = "stability"

    # First request should be allowed
    allowed1, _ = proxy_service._check_rate_limit(client_id, service, cfg)
    assert allowed1 is True

    # Second request should be blocked
    allowed2, retry_after = proxy_service._check_rate_limit(client_id, service, cfg)
    assert allowed2 is False
    assert retry_after > 0


def test_get_client_id_from_remote():
    """Test extracting client ID from request remote."""
    proxy_service = load_proxy_service_module()

    mock_request = MagicMock()
    mock_request.remote = "192.168.1.100"

    client_id = proxy_service._get_client_id(mock_request)
    assert client_id == "192.168.1.100"


def test_get_client_id_from_transport():
    """Test extracting client ID from transport peername."""
    proxy_service = load_proxy_service_module()

    mock_request = MagicMock()
    mock_request.remote = None
    mock_transport = MagicMock()
    mock_transport.get_extra_info.return_value = ("192.168.1.101", 12345)
    mock_request.transport = mock_transport

    client_id = proxy_service._get_client_id(mock_request)
    assert client_id == "192.168.1.101"


def test_get_client_id_fallback():
    """Test client ID fallback when extraction fails."""
    proxy_service = load_proxy_service_module()

    mock_request = MagicMock()
    mock_request.remote = None
    mock_request.transport = None

    client_id = proxy_service._get_client_id(mock_request)
    assert client_id == "unknown"


# Integration-style test for proxy controller (would need more setup)
@pytest.mark.asyncio
async def test_proxy_controller_unknown_service():
    """Test proxy controller rejects unknown services."""
    # This would require setting up the full controller environment
    # For now, just document that this test is needed
    pass


if __name__ == '__main__':
    pytest.main([__file__])