#!/usr/bin/env python3
"""
Tests for API controller enhancements
"""
import json
from unittest.mock import patch, MagicMock

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


def load_api_controllers_module():
    """Dynamically load the controllers.api_controllers module for tests."""
    import sys
    import types

    base = find_workflow_runner_base(__file__)

    # Preload package structure entries
    pkg_prefix = "lf_nodes.modules.workflow_runner"
    pkg_parts = [
        "lf_nodes", "lf_nodes.modules", "lf_nodes.modules.workflow_runner",
        "lf_nodes.modules.workflow_runner.controllers",
        "lf_nodes.modules.workflow_runner.services",
        "lf_nodes.modules.workflow_runner.utils"
    ]
    for p in pkg_parts:
        if p not in sys.modules:
            sys.modules[p] = types.ModuleType(p)

    # Load required modules
    required_modules = {
        "utils.env": "env",
        "utils.constants": "constants",
        "services.auth_service": "auth_service",
        "services.executor": "executor",
        "services.job_service": "job_service",
        "services.job_store": "job_store",
        "services.run_service": "run_service",
        "services.workflow_service": "workflow_service",
        "controllers._helpers": "_helpers",
        "utils.serialize": "serialize"
    }

    for mod_key, mod_name in required_modules.items():
        mod_path = base / mod_key.replace(".", "/") / f"{mod_name}.py"
        try:
            spec = importlib.util.spec_from_file_location(
                f"{pkg_prefix}.{mod_key}.{mod_name}", str(mod_path)
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            sys.modules[f"{pkg_prefix}.{mod_key}.{mod_name}"] = mod
        except Exception:
            # Create mock modules for testing
            sys.modules[f"{pkg_prefix}.{mod_key}.{mod_name}"] = MagicMock()

    # Load the api_controllers module
    controllers_path = base / "controllers" / "api_controllers.py"
    spec = importlib.util.spec_from_file_location(
        f"{pkg_prefix}.controllers.api_controllers", str(controllers_path)
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


class TestApiControllers:
    """Test cases for API controller enhancements."""

    @pytest.fixture
    def api_controllers(self):
        return load_api_controllers_module()

    @pytest.mark.asyncio
    async def test_get_workflow_status_controller_success_with_data(self, api_controllers):
        """Test status controller returns data field for successful runs."""
        # Mock request
        mock_request = MagicMock()
        mock_request.match_info = {"run_id": "test-run-123"}

        # Mock job status with successful result
        mock_job_status = {
            "run_id": "test-run-123",
            "status": "succeeded",
            "result": {
                "http_status": 200,
                "body": {
                    "payload": {
                        "history": {
                            "outputs": {
                                "1": {
                                    "images": [
                                        {
                                            "filename": "test.png",
                                            "subfolder": "",
                                            "type": "output"
                                        }
                                    ]
                                }
                            }
                        }
                    }
                }
            }
        }

        with patch('folder_paths.get_directory_by_type', return_value='/tmp/output'), \
             patch('os.path.exists', return_value=True), \
             patch('PIL.Image.open') as mock_img_open, \
             patch('builtins.open', MagicMock()):

            # Mock image processing
            mock_img = mock_img_open.return_value.__enter__.return_value
            mock_img.mode = 'RGB'
            mock_img.convert.return_value = mock_img

            # Mock get_job_status
            with patch.object(api_controllers, 'get_job_status', return_value=mock_job_status):
                response = await api_controllers.get_workflow_status_controller(mock_request)

        assert response.status == 200
        response_data = json.loads(response.text)

        assert response_data["run_id"] == "test-run-123"
        assert response_data["status"] == "succeeded"
        assert "data" in response_data
        assert response_data["data"].startswith("data:image/png;base64,")

    @pytest.mark.asyncio
    async def test_get_workflow_status_controller_success_no_data(self, api_controllers):
        """Test status controller doesn't add data field when no images found."""
        # Mock request
        mock_request = MagicMock()
        mock_request.match_info = {"run_id": "test-run-123"}

        # Mock job status with successful result but no images
        mock_job_status = {
            "run_id": "test-run-123",
            "status": "succeeded",
            "result": {
                "http_status": 200,
                "body": {
                    "payload": {
                        "history": {
                            "outputs": {}
                        }
                    }
                }
            }
        }

        # Mock get_job_status
        with patch.object(api_controllers, 'get_job_status', return_value=mock_job_status):
            response = await api_controllers.get_workflow_status_controller(mock_request)

        assert response.status == 200
        response_data = json.loads(response.text)

        assert response_data["run_id"] == "test-run-123"
        assert response_data["status"] == "succeeded"
        assert "data" not in response_data

    @pytest.mark.asyncio
    async def test_get_workflow_status_controller_ready_status(self, api_controllers):
        """Test status controller handles 'ready' status."""
        # Mock request
        mock_request = MagicMock()
        mock_request.match_info = {"run_id": "test-run-123"}

        # Mock job status with 'ready' status
        mock_job_status = {
            "run_id": "test-run-123",
            "status": "ready",
            "result": {
                "http_status": 200,
                "body": {
                    "payload": {
                        "history": {
                            "outputs": {
                                "1": {
                                    "images": [
                                        {
                                            "filename": "test.png",
                                            "subfolder": "",
                                            "type": "output"
                                        }
                                    ]
                                }
                            }
                        }
                    }
                }
            }
        }

        with patch('folder_paths.get_directory_by_type', return_value='/tmp/output'), \
             patch('os.path.exists', return_value=True), \
             patch('PIL.Image.open') as mock_img_open, \
             patch('builtins.open', MagicMock()):

            # Mock image processing
            mock_img = mock_img_open.return_value.__enter__.return_value
            mock_img.mode = 'RGB'
            mock_img.convert.return_value = mock_img

            # Mock get_job_status
            with patch.object(api_controllers, 'get_job_status', return_value=mock_job_status):
                response = await api_controllers.get_workflow_status_controller(mock_request)

        assert response.status == 200
        response_data = json.loads(response.text)

        assert response_data["run_id"] == "test-run-123"
        assert response_data["status"] == "ready"
        assert "data" in response_data

    @pytest.mark.asyncio
    async def test_get_workflow_status_controller_pending_status(self, api_controllers):
        """Test status controller doesn't add data field for non-successful statuses."""
        # Mock request
        mock_request = MagicMock()
        mock_request.match_info = {"run_id": "test-run-123"}

        # Mock job status with pending status
        mock_job_status = {
            "run_id": "test-run-123",
            "status": "pending",
            "result": None
        }

        # Mock get_job_status
        with patch.object(api_controllers, 'get_job_status', return_value=mock_job_status):
            response = await api_controllers.get_workflow_status_controller(mock_request)

        assert response.status == 200
        response_data = json.loads(response.text)

        assert response_data["run_id"] == "test-run-123"
        assert response_data["status"] == "pending"
        assert "data" not in response_data

    @pytest.mark.asyncio
    async def test_get_workflow_status_controller_no_result(self, api_controllers):
        """Test status controller handles successful status with no result."""
        # Mock request
        mock_request = MagicMock()
        mock_request.match_info = {"run_id": "test-run-123"}

        # Mock job status with successful status but no result
        mock_job_status = {
            "run_id": "test-run-123",
            "status": "succeeded",
            "result": None
        }

        # Mock get_job_status
        with patch.object(api_controllers, 'get_job_status', return_value=mock_job_status):
            response = await api_controllers.get_workflow_status_controller(mock_request)

        assert response.status == 200
        response_data = json.loads(response.text)

        assert response_data["run_id"] == "test-run-123"
        assert response_data["status"] == "succeeded"
        assert "data" not in response_data

    @pytest.mark.asyncio
    async def test_get_workflow_status_controller_unknown_run_id(self, api_controllers):
        """Test status controller handles unknown run IDs."""
        # Mock request
        mock_request = MagicMock()
        mock_request.match_info = {"run_id": "unknown-run"}

        # Mock get_job_status returning None
        with patch.object(api_controllers, 'get_job_status', return_value=None):
            with pytest.raises(web.HTTPNotFound):
                await api_controllers.get_workflow_status_controller(mock_request)

    @pytest.mark.asyncio
    async def test_get_workflow_status_controller_missing_run_id(self, api_controllers):
        """Test status controller handles missing run_id parameter."""
        # Mock request without run_id
        mock_request = MagicMock()
        mock_request.match_info = {}

        with pytest.raises(web.HTTPBadRequest):
            await api_controllers.get_workflow_status_controller(mock_request)