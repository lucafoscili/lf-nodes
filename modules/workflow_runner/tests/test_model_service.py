#!/usr/bin/env python3
"""
Tests for model_service.py
"""
import json
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

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


class _AsyncContext:
    def __init__(self, value):
        self.value = value

    async def __aenter__(self):
        return self.value

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return False


def load_model_service_module():
    """Dynamically load the services.model_service module for tests."""
    import sys
    import types

    base = find_workflow_runner_base(__file__)

    # Mock external dependencies
    mock_folder_paths = types.ModuleType('folder_paths')
    mock_folder_paths.get_directory_by_type = MagicMock(return_value='/tmp/models')
    mock_folder_paths.get_folder_paths = MagicMock(return_value=[])
    mock_folder_paths.get_filename_list = MagicMock(side_effect=lambda folder: {
        "checkpoints": ["model1.safetensors", "model2.ckpt"],
        "diffusion_models": ["model3.safetensors"]
    }.get(folder, []))
    sys.modules['folder_paths'] = mock_folder_paths

    # Preload package structure entries
    pkg_prefix = "lf_nodes.modules.workflow_runner"
    pkg_parts = [
        "lf_nodes", "lf_nodes.modules", "lf_nodes.modules.workflow_runner",
        "lf_nodes.modules.workflow_runner.services",
        "lf_nodes.modules.workflow_runner.utils",
        "lf_nodes.modules.workflow_runner.config",
        "lf_nodes.modules.utils"
    ]
    for p in pkg_parts:
        if p not in sys.modules:
            sys.modules[p] = types.ModuleType(p)

    # Load utils modules first (config depends on them)
    utils_modules = ["env", "constants"]
    for mod_name in utils_modules:
        # Utils are in the parent modules directory
        utils_path = base.parent / "utils" / f"{mod_name}.py"
        try:
            spec = importlib.util.spec_from_file_location(
                f"lf_nodes.modules.utils.{mod_name}", str(utils_path)
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            sys.modules[f"lf_nodes.modules.utils.{mod_name}"] = mod
        except Exception as e:
            print(f"Failed to load utils.{mod_name}: {e}")
            pass

    # Load config module
    config_path = base / "config.py"
    try:
        spec = importlib.util.spec_from_file_location(
            f"{pkg_prefix}.config", str(config_path)
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        sys.modules[f"{pkg_prefix}.config"] = mod
    except Exception as e:
        print(f"Failed to load config: {e}")
        pass

    # Load proxy_service module
    proxy_path = base / "services" / "proxy_service.py"
    try:
        spec = importlib.util.spec_from_file_location(
            f"{pkg_prefix}.services.proxy_service", str(proxy_path)
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        sys.modules[f"{pkg_prefix}.services.proxy_service"] = mod
    except Exception:
        pass

    # Load utils modules
    utils_modules = ["env", "constants"]
    for mod_name in utils_modules:
        utils_path = base / "utils" / f"{mod_name}.py"
        try:
            spec = importlib.util.spec_from_file_location(
                f"{pkg_prefix}.utils.{mod_name}", str(utils_path)
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            sys.modules[f"{pkg_prefix}.utils.{mod_name}"] = mod
        except Exception:
            pass

    # Load the model_service module
    service_path = base / "services" / "model_service.py"
    spec = importlib.util.spec_from_file_location(
        f"{pkg_prefix}.services.model_service", str(service_path)
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod

class TestModelService:
    """Test cases for model service functions."""

    @pytest.fixture
    def model_service(self):
        import sys

        previous_folder_paths = sys.modules.get("folder_paths")
        module = load_model_service_module()
        try:
            yield module
        finally:
            if previous_folder_paths is None:
                sys.modules.pop("folder_paths", None)
            else:
                sys.modules["folder_paths"] = previous_folder_paths

    @pytest.mark.asyncio
    async def test_get_gemini_models_success(self, model_service):
        """Test successful retrieval of Gemini models."""
        # Mock the loaded module directly; its synthetic package alias is an
        # implementation detail of this isolated test fixture.
        with patch.object(model_service, '_read_secret', return_value='test_key'), \
             patch('aiohttp.ClientSession') as mock_session_class:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                "models": [
                    {"name": "models/gemini-1.5-pro", "displayName": "Gemini 1.5 Pro"},
                    {"name": "models/gemini-1.5-flash", "displayName": "Gemini 1.5 Flash"}
                ]
            })
            
            mock_session = MagicMock()
            mock_session.get = MagicMock(return_value=_AsyncContext(mock_response))
            mock_session_class.return_value = _AsyncContext(mock_session)

            result = await model_service.get_gemini_models()
        assert "gemini-1.5-pro" in result
        assert "gemini-1.5-flash" in result

    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession')
    async def test_get_gemini_models_no_api_key(self, mock_session_class, model_service):
        """Test Gemini models retrieval when no API key is available."""
        with patch.dict('os.environ', {}, clear=True):
            result = await model_service.get_gemini_models()

        assert result == []

    @pytest.mark.asyncio
    async def test_get_gemini_models_http_error(self, model_service):
        """Test Gemini models retrieval when HTTP request fails."""
        mock_response = AsyncMock()
        mock_response.status = 401
        mock_response.text = AsyncMock(return_value="unauthorized")

        mock_session = MagicMock()
        mock_session.get.return_value = _AsyncContext(mock_response)

        with patch.object(model_service, '_read_secret', return_value='invalid_key'), \
             patch('aiohttp.ClientSession', return_value=_AsyncContext(mock_session)):
            result = await model_service.get_gemini_models()

        assert result == []

    @pytest.mark.asyncio
    async def test_get_gemini_models_json_error(self, model_service):
        """Test Gemini models retrieval when JSON parsing fails."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)

        mock_session = MagicMock()
        mock_session.get.return_value = _AsyncContext(mock_response)

        with patch.object(model_service, '_read_secret', return_value='test_key'), \
             patch('aiohttp.ClientSession', return_value=_AsyncContext(mock_session)):
            result = await model_service.get_gemini_models()

        assert result == []

    @patch('folder_paths.get_filename_list')
    def test_get_comfy_models(self, mock_get_filename_list, model_service):
        """Test retrieval of ComfyUI models."""
        mock_get_filename_list.side_effect = lambda folder: {
            "checkpoints": ["model1.safetensors", "model2.ckpt"],
            "diffusion_models": ["model3.safetensors"],
        }.get(folder, [])

        result = model_service.get_comfy_models()

        # Should return models from checkpoints and diffusion_models folders
        assert len(result) == 3
        assert "model1.safetensors" in result
        assert "model2.ckpt" in result
        assert "model3.safetensors" in result

    @patch('folder_paths.get_filename_list')
    def test_get_comfy_models_empty(self, mock_get_filename_list, model_service):
        """Test ComfyUI models retrieval when no models found."""
        mock_get_filename_list.return_value = []

        result = model_service.get_comfy_models()

        assert result == []

    @patch('folder_paths.get_filename_list')
    def test_get_comfy_models_invalid_paths(self, mock_get_filename_list, model_service):
        """Test ComfyUI models retrieval with invalid paths."""
        mock_get_filename_list.side_effect = OSError("model directory unavailable")

        result = model_service.get_comfy_models()

        assert result == []

    @pytest.mark.asyncio
    async def test_get_all_models(self, model_service):
        """Select the model engine requested by the caller."""
        with patch.object(
            model_service,
            'get_gemini_models',
            new=AsyncMock(return_value=['gemini-1.5-pro']),
        ), patch.object(
            model_service,
            'get_comfy_models',
            return_value=['model1.safetensors'],
        ):
            text_result = await model_service.get_all_models()
            image_result = await model_service.get_all_models(is_image_models=True)

        assert text_result == {
            "engines": [{"name": "Gemini (Google)", "models": ["gemini-1.5-pro"]}]
        }
        assert image_result == {
            "engines": [{"name": "Diffusion (Comfy)", "models": ["model1.safetensors"]}]
        }

    @pytest.mark.asyncio
    async def test_get_all_models_empty_results(self, model_service):
        with patch.object(
            model_service,
            'get_gemini_models',
            new=AsyncMock(return_value=[]),
        ), patch.object(model_service, 'get_comfy_models', return_value=[]):
            text_result = await model_service.get_all_models()
            image_result = await model_service.get_all_models(is_image_models=True)

        assert text_result["engines"][0]["models"] == []
        assert image_result["engines"][0]["models"] == []
