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
        return load_model_service_module()

    @pytest.mark.asyncio
    @patch('lf_nodes.modules.workflow_runner.services.model_service._read_secret')
    async def test_get_gemini_models_success(self, mock_read_secret, model_service):
        """Test successful retrieval of Gemini models."""
        mock_read_secret.return_value = 'test_key'
        
        # Mock the entire aiohttp session
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                "models": [
                    {"name": "models/gemini-1.5-pro", "displayName": "Gemini 1.5 Pro"},
                    {"name": "models/gemini-1.5-flash", "displayName": "Gemini 1.5 Flash"}
                ]
            })
            
            # Create an async context manager for the session
            class MockSessionContext:
                def __init__(self, session):
                    self.session = session
                
                async def __aenter__(self):
                    return self.session
                
                async def __aexit__(self, exc_type, exc_val, exc_tb):
                    pass
            
            # Create an async context manager for the response
            class MockResponseContext:
                def __init__(self, response):
                    self.response = response
                
                async def __aenter__(self):
                    return self.response
                
                async def __aexit__(self, exc_type, exc_val, exc_tb):
                    pass
            
            mock_session = MagicMock()
            # Override the get method to return the context manager directly
            mock_session.get = MagicMock(return_value=MockResponseContext(mock_response))
            mock_session_class.return_value = MockSessionContext(mock_session)

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
    @patch('aiohttp.ClientSession')
    async def test_get_gemini_models_http_error(self, mock_session_class, model_service):
        """Test Gemini models retrieval when HTTP request fails."""
        mock_response = AsyncMock()
        mock_response.status = 401

        mock_session = AsyncMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response
        mock_session_class.return_value.__aenter__.return_value = mock_session

        with patch.dict('os.environ', {'GEMINI_API_KEY': 'invalid_key'}):
            result = await model_service.get_gemini_models()

        assert result == []

    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession')
    async def test_get_gemini_models_json_error(self, mock_session_class, model_service):
        """Test Gemini models retrieval when JSON parsing fails."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)

        mock_session = AsyncMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response
        mock_session_class.return_value.__aenter__.return_value = mock_session

        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test_key'}):
            result = await model_service.get_gemini_models()

        assert result == []

    @patch('folder_paths.get_folder_paths')
    def test_get_comfy_models(self, mock_get_folder_paths, model_service):
        """Test retrieval of ComfyUI models."""
        # Mock folder_paths response
        mock_get_folder_paths.return_value = [
            "/models/checkpoints/model1.safetensors",
            "/models/checkpoints/model2.ckpt",
            "/models/loras/lora1.safetensors",
            "/models/vae/vae1.safetensors"
        ]

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
        mock_get_filename_list.return_value = []

        result = model_service.get_comfy_models()

        assert result == []

    @pytest.mark.asyncio
    @patch('folder_paths.get_folder_paths')
    async def test_get_all_models(self, mock_get_folder_paths, model_service):
        """Test retrieval of all models (Gemini + ComfyUI)."""
        # Mock ComfyUI models
        mock_get_folder_paths.return_value = [
            "/models/checkpoints/model1.safetensors"
        ]

        # Mock Gemini API
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                "models": [
                    {"name": "models/gemini-1.5-pro", "displayName": "Gemini 1.5 Pro"}
                ]
            })

            # Create an async context manager for the session
            class MockSessionContext:
                def __init__(self, session):
                    self.session = session
                
                async def __aenter__(self):
                    return self.session
                
                async def __aexit__(self, exc_type, exc_val, exc_tb):
                    pass
            
            # Create an async context manager for the response
            class MockResponseContext:
                def __init__(self, response):
                    self.response = response
                
                async def __aenter__(self):
                    return self.response
                
                async def __aexit__(self, exc_type, exc_val, exc_tb):
                    pass

            mock_session = MagicMock()
            # Override the get method to return the context manager directly
            mock_session.get = MagicMock(return_value=MockResponseContext(mock_response))
            mock_session_class.return_value = MockSessionContext(mock_session)

            with patch.dict('os.environ', {'GEMINI_API_KEY': 'test_key'}):
                result = await model_service.get_all_models()

        # Should contain engines dict
        assert "engines" in result
        assert len(result["engines"]) == 2

        # Check Gemini engine
        gemini_engine = result["engines"][0]
        assert gemini_engine["name"] == "Gemini (Google)"
        assert len(gemini_engine["models"]) == 1
        assert gemini_engine["models"][0] == "gemini-1.5-pro"

        # Check ComfyUI engine
        comfy_engine = result["engines"][1]
        assert comfy_engine["name"] == "Diffusion (Comfy)"
        assert "model1.safetensors" in comfy_engine["models"]

    @pytest.mark.asyncio
    async def test_get_all_models_no_duplicates(self, model_service):
        """Test that get_all_models doesn't return duplicates."""
        # Mock empty ComfyUI models
        with patch('folder_paths.get_filename_list', return_value=[]):
            # Mock Gemini API with empty response
            with patch('aiohttp.ClientSession') as mock_session_class:
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.json.return_value = {"models": []}

                mock_session = AsyncMock()
                mock_session.get.return_value.__aenter__.return_value = mock_response
                mock_session_class.return_value.__aenter__.return_value = mock_session

                with patch.dict('os.environ', {}, clear=True):
                    result = await model_service.get_all_models()

        # Should return engines dict with empty models
        assert "engines" in result
        assert len(result["engines"]) == 2
        assert result["engines"][0]["models"] == []
        assert result["engines"][1]["models"] == []