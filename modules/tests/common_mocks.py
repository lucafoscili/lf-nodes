# region Common Test Mocks for LF Nodes
"""
Common test utilities and mocks for LF Nodes testing.
Provides centralized mocking setup to avoid code duplication across test files.
"""

import sys
from unittest.mock import MagicMock


def setup_common_mocks():
    """
    Set up common mocks for LF Nodes testing.
    This includes torch, torchvision, transformers, and other dependencies
    that are commonly needed to avoid CUDA initialization and import issues.
    """
    # Mock torch.cuda to avoid CUDA initialization
    torch_mock = MagicMock()
    torch_cuda_mock = MagicMock()
    torch_cuda_mock.current_device.return_value = 0
    torch_mock.cuda = torch_cuda_mock

    # Mock torch.nn and its submodules
    torch_nn_mock = MagicMock()
    torch_nn_functional_mock = MagicMock()
    torch_nn_mock.functional = torch_nn_functional_mock
    torch_mock.nn = torch_nn_mock

    # Mock torch.hub
    torch_hub_mock = MagicMock()
    torch_mock.hub = torch_hub_mock

    # Mock torch.device
    torch_device_mock = MagicMock()
    torch_mock.device = torch_device_mock

    # Apply torch mocks
    sys.modules['torch'] = torch_mock
    sys.modules['torch.cuda'] = torch_cuda_mock
    sys.modules['torch.nn'] = torch_nn_mock
    sys.modules['torch.nn.functional'] = torch_nn_functional_mock
    sys.modules['torch.hub'] = torch_hub_mock
    sys.modules['torch.device'] = torch_device_mock

    # Mock torchvision to avoid complex import chains
    sys.modules['torchvision'] = MagicMock()
    sys.modules['torchvision.transforms'] = MagicMock()
    sys.modules['torchvision.transforms.functional'] = MagicMock()

    # Mock transformers to avoid import issues
    sys.modules['transformers'] = MagicMock()

    # Mock the entire helpers module to avoid deep import chains
    sys.modules['modules.utils.helpers'] = MagicMock()
    sys.modules['modules.utils.helpers.api'] = MagicMock()
    sys.modules['modules.utils.helpers.comfy'] = MagicMock()
    sys.modules['modules.utils.helpers.detection'] = MagicMock()
    sys.modules['modules.utils.helpers.logic'] = MagicMock()
    sys.modules['modules.utils.helpers.torch'] = MagicMock()
    sys.modules['modules.utils.helpers.ui'] = MagicMock()
    sys.modules['modules.utils.helpers.tagging'] = MagicMock()

    # Mock filters modules
    sys.modules['modules.utils.filters'] = MagicMock()
    sys.modules['modules.utils.filters._common'] = MagicMock()
    sys.modules['modules.utils.filters.inpaint'] = MagicMock()
    sys.modules['modules.utils.filters.processors'] = MagicMock()

    # Mock comfy modules that depend on torch
    sys.modules['comfy'] = MagicMock()
    sys.modules['comfy.model_management'] = MagicMock()
    sys.modules['comfy.samplers'] = MagicMock()
    sys.modules['comfy.lora'] = MagicMock()
    sys.modules['comfy.hooks'] = MagicMock()
    sys.modules['comfy.model_patcher'] = MagicMock()
    sys.modules['comfy.k_diffusion'] = MagicMock()
    sys.modules['comfy.k_diffusion.sampling'] = MagicMock()
    sys.modules['comfy.sample'] = MagicMock()

    # Mock folder_paths
    sys.modules['folder_paths'] = MagicMock()

    # Mock server components
    sys.modules['server'] = MagicMock()


def mock_prompt_server(address="127.0.0.1", port=8188):
    """
    Create a mock PromptServer instance with specified address and port.

    Args:
        address: Server address (default: "127.0.0.1")
        port: Server port (default: 8188)

    Returns:
        Mock PromptServer instance
    """
    class MockPromptServer:
        def __init__(self):
            self.address = address
            self.port = port

    return MockPromptServer()


def mock_async_response(status=200, text="", json_data=None):
    """
    Create a mock aiohttp response for testing.

    Args:
        status: HTTP status code (default: 200)
        text: Response text content
        json_data: JSON data to return from .json() method

    Returns:
        Configured MagicMock response
    """
    from unittest.mock import AsyncMock

    response = MagicMock()
    response.status = status
    response.text = AsyncMock(return_value=text)

    if json_data is not None:
        response.json = AsyncMock(return_value=json_data)
    else:
        response.json = AsyncMock(side_effect=Exception("Invalid JSON"))

    return response


def mock_openai_response(content="Test response", usage=None):
    """
    Create a mock OpenAI API response.

    Args:
        content: The response content text
        usage: Optional usage statistics dict

    Returns:
        Dict representing OpenAI API response format
    """
    response = {
        "choices": [{
            "message": {
                "content": content
            }
        }]
    }

    if usage:
        response["usage"] = usage
    else:
        response["usage"] = {"total_tokens": 50}

    return response


def mock_gemini_response(content="Test response", usage=None):
    """
    Create a mock Gemini API response.

    Args:
        content: The response content text
        usage: Optional usage metadata dict

    Returns:
        Dict representing Gemini API response format
    """
    response = {
        "candidates": [{
            "content": {
                "parts": [{"text": content}]
            }
        }]
    }

    if usage:
        response["usageMetadata"] = usage
    else:
        response["usageMetadata"] = {"totalTokens": 50}

    return response

# endregion