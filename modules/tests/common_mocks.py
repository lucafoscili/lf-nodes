# region Common Test Mocks for LF Nodes
"""
Common test utilities and mocks for LF Nodes testing.
Provides centralized mocking setup to avoid code duplication across test files.
"""

import sys
import types
from contextlib import contextmanager
from unittest.mock import MagicMock


_COMMON_MOCK_MODULE_NAMES = (
    'torch',
    'torch.cuda',
    'torch.nn',
    'torch.nn.functional',
    'torch.hub',
    'torch.device',
    'torchvision',
    'torchvision.transforms',
    'torchvision.transforms.functional',
    'transformers',
    'modules.utils.helpers',
    'modules.utils.helpers.api',
    'modules.utils.helpers.comfy',
    'modules.utils.helpers.conversion',
    'modules.utils.helpers.conversion.base64_to_tensor',
    'modules.utils.helpers.conversion.tensor_to_base64',
    'modules.utils.helpers.detection',
    'modules.utils.helpers.editing',
    'modules.utils.helpers.logic',
    'modules.utils.helpers.torch',
    'modules.utils.helpers.ui',
    'modules.utils.helpers.tagging',
    'modules.utils.filters',
    'modules.utils.filters._common',
    'modules.utils.filters.inpaint',
    'modules.utils.filters.processors',
    'comfy',
    'comfy.model_management',
    'comfy.samplers',
    'comfy.lora',
    'comfy.hooks',
    'comfy.model_patcher',
    'comfy.k_diffusion',
    'comfy.k_diffusion.sampling',
    'comfy.sample',
    'folder_paths',
    'server',
)
_TORCH_MOCK_MODULE_NAMES = frozenset(
    {
        'torch',
        'torch.cuda',
        'torch.nn',
        'torch.nn.functional',
        'torch.hub',
        'torch.device',
        'torchvision',
        'torchvision.transforms',
        'torchvision.transforms.functional',
    }
)
_MISSING_MODULE = object()


@contextmanager
def scoped_common_mocks(torch_enabled=False):
    """Install the legacy import mocks without leaking them to other tests.

    Several older node tests need lightweight stand-ins while importing their
    module under test.  Pytest imports every test module during collection, so
    leaving those stand-ins in ``sys.modules`` makes unrelated tests observe a
    partial helpers package.  In particular, image nodes then cannot import the
    real conversion helpers.  Keep the mocks for the import that needs them and
    restore the process-wide module registry immediately afterwards.
    """
    tracked_names = (
        name
        for name in _COMMON_MOCK_MODULE_NAMES
        if not torch_enabled or name not in _TORCH_MOCK_MODULE_NAMES
    )
    previous_modules = {
        name: sys.modules.get(name, _MISSING_MODULE)
        for name in tracked_names
    }
    setup_common_mocks(torch_enabled=torch_enabled)
    try:
        yield
    finally:
        for name, previous in previous_modules.items():
            if previous is _MISSING_MODULE:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = previous


def setup_common_mocks(torch_enabled=False):
    """
    Set up common mocks for LF Nodes testing.
    This includes torch, torchvision, transformers, and other dependencies
    that are commonly needed to avoid CUDA initialization and import issues.

    Args:
        torch_enabled: If True, don't mock torch modules, allowing real torch usage.
                      If False, mock torch to avoid CUDA and import issues.
    """
    # Conditionally mock torch based on torch_enabled parameter
    if not torch_enabled and 'torch' not in sys.modules:
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

        # Apply torch mocks only when the test process has not already loaded
        # the real package.  unittest discovery imports every test module
        # before executing any of them; replacing a real torch module here
        # corrupts torchvision's references for unrelated helper tests.
        sys.modules['torch'] = torch_mock
        sys.modules['torch.cuda'] = torch_cuda_mock
        sys.modules['torch.nn'] = torch_nn_mock
        sys.modules['torch.nn.functional'] = torch_nn_functional_mock
        sys.modules['torch.hub'] = torch_hub_mock
        sys.modules['torch.device'] = torch_device_mock

    # Do not replace torchvision after a helper test has imported it.  Its
    # functional implementation retains a reference to the original torch
    # module and fails with opaque isinstance errors if that reference is
    # replaced during discovery.
    if not torch_enabled and 'torchvision' not in sys.modules:
        sys.modules['torchvision'] = MagicMock()
        sys.modules['torchvision.transforms'] = MagicMock()
        sys.modules['torchvision.transforms.functional'] = MagicMock()
    # If torch_enabled=True, don't mock torch - let tests use real torch

    # Mock transformers to avoid import issues
    sys.modules['transformers'] = MagicMock()

    # Mock the entire helpers module to avoid deep import chains
    sys.modules['modules.utils.helpers'] = MagicMock()
    api_mock = MagicMock()

    def build_openai_multimodal_content(image, text):
        content = []
        if image is not None and (not isinstance(image, list) or image):
            content.append({"type": "image_url", "image_url": {"url": "data:image/png;charset=utf-8;base64,mock"}})
        if text:
            content.append({"type": "text", "text": text})
        return content

    api_mock.build_openai_multimodal_content = build_openai_multimodal_content
    api_mock.parse_gemini_image = lambda _data: None
    sys.modules['modules.utils.helpers.api'] = api_mock
    sys.modules['modules.utils.helpers.comfy'] = MagicMock()
    # Keep conversion importable as a package: Gemini imports the concrete
    # tensor_to_base64 submodule.  The node tests do not need its heavy image
    # implementation, so expose a harmless mock function while preserving
    # normal package semantics.
    conversion_mock = types.ModuleType('modules.utils.helpers.conversion')
    conversion_mock.__path__ = []
    conversion_mock.tensor_to_numpy = MagicMock()
    conversion_mock.tensor_to_base64 = MagicMock()
    sys.modules['modules.utils.helpers.conversion'] = conversion_mock
    tensor_to_base64_module = types.ModuleType('modules.utils.helpers.conversion.tensor_to_base64')
    tensor_to_base64_module.tensor_to_base64 = MagicMock()
    sys.modules['modules.utils.helpers.conversion.tensor_to_base64'] = tensor_to_base64_module
    sys.modules['modules.utils.helpers.detection'] = MagicMock()
    sys.modules['modules.utils.helpers.editing'] = MagicMock()
    logic_mock = MagicMock()

    def normalize_list_to_value(value):
        return value[0] if isinstance(value, list) and value else value

    def normalize_json_input(value):
        import json
        if value is None or isinstance(value, (dict, list)):
            return value
        if isinstance(value, str):
            try:
                return json.loads(value)
            except (TypeError, ValueError):
                return {}
        return value

    # JSON nodes are exercised alongside mocked node modules.  Preserve the
    # two normalization contracts they rely on instead of returning a fresh
    # MagicMock, which makes valid dict/list inputs look invalid.
    logic_mock.normalize_list_to_value = normalize_list_to_value
    logic_mock.normalize_json_input = normalize_json_input
    sys.modules['modules.utils.helpers.logic'] = logic_mock
    sys.modules['modules.utils.helpers.torch'] = MagicMock()
    sys.modules['modules.utils.helpers.ui'] = MagicMock()
    sys.modules['modules.utils.helpers.tagging'] = MagicMock()

    # Mock specific functions that need special behavior
    def mock_normalize_output_image(images):
        """Mock normalize_output_image to return proper tuple format."""
        if isinstance(images, list):
            return [images[0]] if images else [], images
        else:
            return [images], [images]

    def mock_normalize_input_image(image):
        """Mock normalize_input_image to return proper list format."""
        if image is None:
            return []
        if isinstance(image, list):
            # If it's already a list of tensors, return it
            return image
        # For tensors, simulate the real normalization logic
        # Check if it's a batch tensor (4D with first dim > 1)
        if hasattr(image, 'shape') and len(image.shape) == 4 and image.shape[0] > 1:
            # Split batch into individual images, keeping batch dimension as 1
            return [image[i:i+1] for i in range(image.shape[0])]
        # For single tensors, return as list
        return [image]

    sys.modules['modules.utils.helpers.logic'].normalize_output_image = mock_normalize_output_image
    sys.modules['modules.utils.helpers.logic'].normalize_input_image = mock_normalize_input_image

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
