#!/usr/bin/env python3
"""
Tests for API controller enhancements
"""
import base64
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

    # Set up controllers as a package
    controllers_mod = types.ModuleType("lf_nodes.modules.workflow_runner.controllers")
    sys.modules["lf_nodes.modules.workflow_runner.controllers"] = controllers_mod

    # Set up utils as a package
    utils_mod = types.ModuleType("lf_nodes.modules.workflow_runner.utils")
    sys.modules["lf_nodes.modules.workflow_runner.utils"] = utils_mod

    # Set up all service mocks before loading other modules
    auth_service_mock = MagicMock()
    auth_service_mock.create_server_session = MagicMock()
    auth_service_mock._require_auth = MagicMock()
    auth_service_mock._verify_token_and_email = MagicMock()
    auth_service_mock._ENABLE_GOOGLE_OAUTH = False
    auth_service_mock._WF_DEBUG = False
    sys.modules["lf_nodes.modules.workflow_runner.services.auth_service"] = auth_service_mock

    executor_mock = MagicMock()
    executor_mock.WorkflowPreparationError = Exception
    executor_mock.execute_workflow = MagicMock()
    sys.modules["lf_nodes.modules.workflow_runner.services.executor"] = executor_mock

    job_service_mock = MagicMock()
    job_service_mock.get_job_status = MagicMock()
    sys.modules["lf_nodes.modules.workflow_runner.services.job_service"] = job_service_mock

    job_store_mock = MagicMock()
    job_store_mock.get_job = MagicMock()
    job_store_mock.update_job = MagicMock()
    sys.modules["lf_nodes.modules.workflow_runner.services.job_store"] = job_store_mock

    run_service_mock = MagicMock()
    run_service_mock.run_workflow = MagicMock()
    sys.modules["lf_nodes.modules.workflow_runner.services.run_service"] = run_service_mock

    workflow_service_mock = MagicMock()
    workflow_service_mock.list_workflows = MagicMock()
    workflow_service_mock.get_workflow_content = MagicMock()
    sys.modules["lf_nodes.modules.workflow_runner.services.workflow_service"] = workflow_service_mock

    # Set up _helpers mock
    helpers_mock = MagicMock()
    helpers_mock.parse_json_body = MagicMock()
    helpers_mock.get_owner_from_request = MagicMock()
    helpers_mock.serialize_job = MagicMock(side_effect=lambda job, **kwargs: job)  # Return the job as-is
    helpers_mock.write_sse_event = MagicMock()
    helpers_mock.create_and_set_session_cookie = MagicMock()
    helpers_mock.extract_base64_data_from_result = MagicMock(side_effect=lambda result: ("image/png", base64.b64encode(b'mock_png_data').decode('utf-8')) if result and result.get("body", {}).get("payload", {}).get("history", {}).get("outputs") else None)
    sys.modules["lf_nodes.modules.workflow_runner.controllers._helpers"] = helpers_mock

    # Set up config mock
    config_mock = MagicMock()
    config_mock.get_settings = MagicMock(return_value=MagicMock(COMFY_BACKEND_URL="http://127.0.0.1:8188"))
    sys.modules["lf_nodes.modules.workflow_runner.config"] = config_mock

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
        "utils.serialize": "serialize",
        "config": "config"
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
            # Create mock modules for testing with required attributes
            mock_mod = MagicMock()
            if mod_key == "services.auth_service":
                # Set up auth_service mock with required functions/variables
                mock_mod.create_server_session = MagicMock()
                mock_mod._require_auth = MagicMock()
                mock_mod._verify_token_and_email = MagicMock()
                mock_mod._ENABLE_GOOGLE_OAUTH = False
                mock_mod._WF_DEBUG = False
            elif mod_key == "services.executor":
                mock_mod.WorkflowPreparationError = Exception
                mock_mod.execute_workflow = MagicMock()
            elif mod_key == "services.job_service":
                mock_mod.get_job_status = MagicMock()
            elif mod_key == "services.job_store":
                mock_mod.get_job = MagicMock()
                mock_mod.update_job = MagicMock()
            elif mod_key == "services.run_service":
                mock_mod.run_workflow = MagicMock()
            elif mod_key == "services.workflow_service":
                mock_mod.list_workflows = MagicMock()
                mock_mod.get_workflow_content = MagicMock()
            elif mod_key == "controllers._helpers":
                mock_mod.extract_base64_data_from_result = MagicMock(return_value=("image/png", "mock_base64_data"))
                mock_mod.serialize_job = MagicMock()
            elif mod_key == "utils.serialize":
                mock_mod.serialize_job = MagicMock()
            elif mod_key == "config":
                mock_mod.get_settings = MagicMock(return_value=MagicMock(COMFY_BACKEND_URL="http://127.0.0.1:8188"))
            sys.modules[f"{pkg_prefix}.{mod_key}.{mod_name}"] = mock_mod

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

        with patch('lf_nodes.modules.workflow_runner.controllers._helpers.folder_paths.get_directory_by_type', return_value='/tmp/output'), \
             patch('lf_nodes.modules.workflow_runner.controllers._helpers.os.path.exists', return_value=True), \
             patch('lf_nodes.modules.workflow_runner.controllers._helpers.PIL.Image.open') as mock_img_open, \
             patch('lf_nodes.modules.workflow_runner.controllers._helpers.builtins.open', MagicMock()):

            # Mock image processing
            mock_img = mock_img_open.return_value.__enter__.return_value
            mock_img.mode = 'RGB'
            mock_img.convert.return_value = mock_img

            # Mock get_job_status
            async def mock_get_job_status(run_id):
                return mock_job_status
            with patch.object(api_controllers, 'get_job_status', side_effect=mock_get_job_status):
                response = await api_controllers.get_workflow_status_controller(mock_request)

        assert response.status == 200
        assert response.content_type == "image/png"
        response_data = json.loads(response.text)

        assert response_data["run_id"] == "test-run-123"
        assert response_data["status"] == "succeeded"
        assert "data" in response_data
        # Data should be just the base64 string, not a data URL
        assert response_data["data"] == base64.b64encode(b'mock_png_data').decode('utf-8')

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
        async def mock_get_job_status(run_id):
            return mock_job_status
        with patch.object(api_controllers, 'get_job_status', side_effect=mock_get_job_status):
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

        with patch('lf_nodes.modules.workflow_runner.controllers._helpers.folder_paths.get_directory_by_type', return_value='/tmp/output'), \
             patch('lf_nodes.modules.workflow_runner.controllers._helpers.os.path.exists', return_value=True), \
             patch('lf_nodes.modules.workflow_runner.controllers._helpers.PIL.Image.open') as mock_img_open, \
             patch('lf_nodes.modules.workflow_runner.controllers._helpers.builtins.open', MagicMock()):

            # Mock image processing
            mock_img = mock_img_open.return_value.__enter__.return_value
            mock_img.mode = 'RGB'
            mock_img.convert.return_value = mock_img

            # Mock get_job_status
            async def mock_get_job_status(run_id):
                return mock_job_status
            with patch.object(api_controllers, 'get_job_status', side_effect=mock_get_job_status):
                response = await api_controllers.get_workflow_status_controller(mock_request)

        assert response.status == 200
        response_data = json.loads(response.text)

        assert response_data["run_id"] == "test-run-123"
        assert response_data["status"] == "ready"
        assert "data" not in response_data

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
        async def mock_get_job_status(run_id):
            return mock_job_status
        with patch.object(api_controllers, 'get_job_status', side_effect=mock_get_job_status):
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
        async def mock_get_job_status(run_id):
            return mock_job_status
        with patch.object(api_controllers, 'get_job_status', side_effect=mock_get_job_status):
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
        async def mock_get_job_status(run_id):
            return None
        
        # Mock aiohttp session to simulate history fetch failure
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status = 404
        mock_session.get.return_value.__aenter__.return_value = mock_response
        
        with patch.object(api_controllers, 'get_job_status', side_effect=mock_get_job_status), \
             patch('aiohttp.ClientSession', return_value=mock_session):
            response = await api_controllers.get_workflow_status_controller(mock_request)

        assert response.status == 404
        response_data = json.loads(response.text)
        assert response_data["detail"] == "Headless run not found"

    @pytest.mark.asyncio
    async def test_get_workflow_status_controller_missing_run_id(self, api_controllers):
        """Test status controller handles missing run_id parameter."""
        # Mock request without run_id
        mock_request = MagicMock()
        mock_request.match_info = {}

        response = await api_controllers.get_workflow_status_controller(mock_request)

        assert response.status == 400
        response_data = json.loads(response.text)
        assert response_data["detail"] == "missing_run_id"

    @pytest.mark.asyncio
    async def test_get_workflow_status_controller_headless_run_success(self, api_controllers):
        """Test status controller handles headless runs found in ComfyUI history with successful output."""
        # Mock request
        mock_request = MagicMock()
        mock_request.match_info = {"run_id": "headless-run-123"}

        # Mock get_job_status returning None (not in DB)
        async def mock_get_job_status(run_id):
            return None

        # Mock aiohttp session (similar to working unknown_run_id test)
        from unittest.mock import AsyncMock
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "headless-run-123": {
                "status": {"completed": True},
                "outputs": {
                    "1": {
                        "images": [
                            {
                                "filename": "result.png",
                                "subfolder": "",
                                "type": "output"
                            }
                        ]
                    }
                }
            }
        })
        mock_session.get.return_value.__aenter__.return_value = mock_response
        mock_session.get.return_value.__aexit__.return_value = None
        # Also need to mock the session context manager
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None

        with patch.object(api_controllers, 'get_job_status', side_effect=mock_get_job_status), \
             patch('aiohttp.ClientSession', return_value=mock_session), \
             patch('lf_nodes.modules.workflow_runner.controllers._helpers.folder_paths.get_directory_by_type', return_value='/tmp/output'), \
             patch('lf_nodes.modules.workflow_runner.controllers._helpers.os.path.exists', return_value=True), \
             patch('lf_nodes.modules.workflow_runner.controllers._helpers.PIL.Image.open') as mock_img_open, \
             patch('lf_nodes.modules.workflow_runner.controllers._helpers.builtins.open', MagicMock()):

            # Mock image processing
            mock_img = mock_img_open.return_value.__enter__.return_value
            mock_img.mode = 'RGB'
            mock_img.convert.return_value = mock_img

            response = await api_controllers.get_workflow_status_controller(mock_request)

        assert response.status == 200
        assert response.content_type == "image/png"
        response_data = json.loads(response.text)
        assert "data" in response_data
        assert response_data["data"] == base64.b64encode(b'mock_png_data').decode('utf-8')

    @pytest.mark.asyncio
    async def test_get_workflow_status_controller_headless_run_no_outputs(self, api_controllers):
        """Test status controller handles headless runs found in ComfyUI history with no outputs."""
        # Mock request
        mock_request = MagicMock()
        mock_request.match_info = {"run_id": "headless-run-456"}

        # Mock get_job_status returning None (not in DB)
        async def mock_get_job_status(run_id):
            return None

        # Mock aiohttp session (similar to working unknown_run_id test)
        from unittest.mock import AsyncMock
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "headless-run-456": {
                "status": {"completed": True},
                "outputs": {}
            }
        })
        mock_session.get.return_value.__aenter__.return_value = mock_response
        mock_session.get.return_value.__aexit__.return_value = None
        # Also need to mock the session context manager
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None

        with patch.object(api_controllers, 'get_job_status', side_effect=mock_get_job_status), \
             patch('aiohttp.ClientSession', return_value=mock_session):
            response = await api_controllers.get_workflow_status_controller(mock_request)

        assert response.status == 200
        response_data = json.loads(response.text)
        assert "data" not in response_data

    @pytest.mark.asyncio
    async def test_get_workflow_status_controller_pending_job_updated_from_history(self, api_controllers):
        """Test status controller handles pending jobs (existing functionality)."""
        # Mock request
        mock_request = MagicMock()
        mock_request.match_info = {"run_id": "pending-run-789"}

        # Mock job status as pending
        mock_job_status = {
            "run_id": "pending-run-789",
            "status": "pending",
            "result": None
        }

        # Mock get_job_status
        async def mock_get_job_status(run_id):
            return mock_job_status

        with patch.object(api_controllers, 'get_job_status', side_effect=mock_get_job_status):
            response = await api_controllers.get_workflow_status_controller(mock_request)

        assert response.status == 200
        response_data = json.loads(response.text)
        assert response_data["run_id"] == "pending-run-789"
        assert response_data["status"] == "pending"
        assert "data" not in response_data

    @pytest.mark.asyncio
    async def test_get_workflow_status_controller_history_fetch_error(self, api_controllers):
        """Test status controller handles errors when fetching ComfyUI history."""
        # Mock request
        mock_request = MagicMock()
        mock_request.match_info = {"run_id": "error-run-999"}

        # Mock get_job_status returning None (not in DB)
        async def mock_get_job_status(run_id):
            return None

        # Mock aiohttp session to raise exception
        mock_session = MagicMock()
        mock_session.get.side_effect = Exception("Connection failed")

        with patch.object(api_controllers, 'get_job_status', side_effect=mock_get_job_status), \
             patch('aiohttp.ClientSession', return_value=mock_session):
            response = await api_controllers.get_workflow_status_controller(mock_request)

        assert response.status == 404
        response_data = json.loads(response.text)
        assert response_data["detail"] == "Headless run not found"