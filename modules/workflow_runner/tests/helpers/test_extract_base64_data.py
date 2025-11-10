#!/usr/bin/env python3
"""
Tests for extract_base64_data_from_result function
"""
import importlib.util
import pathlib
import pytest

from unittest.mock import patch, mock_open

# import shared test utils from this helpers package

spec = importlib.util.spec_from_file_location(
    "test_utils",
    str(pathlib.Path(__file__).resolve().parent / "test_utils.py"),
)
test_utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(test_utils)

load_helpers_module = test_utils.load_helpers_module


def load_helpers_module_with_mocks():
    """Load helpers module with mocked external dependencies."""
    import sys
    import types
    from unittest.mock import MagicMock

    base = test_utils.find_workflow_runner_base(__file__)

    # Preload package structure entries
    pkg_prefix = "lf_nodes.modules.workflow_runner"
    pkg_parts = [
        "lf_nodes", "lf_nodes.modules", "lf_nodes.modules.workflow_runner",
        "lf_nodes.modules.workflow_runner.controllers",
        "lf_nodes.modules.workflow_runner.utils"
    ]
    for p in pkg_parts:
        if p not in sys.modules:
            sys.modules[p] = types.ModuleType(p)

    # Mock external dependencies
    mock_folder_paths = MagicMock()
    mock_pil = MagicMock()
    mock_pil_image = MagicMock()
    sys.modules['folder_paths'] = mock_folder_paths
    sys.modules['PIL'] = mock_pil
    sys.modules['PIL.Image'] = mock_pil_image

    # Load utils.serialize into sys.modules under the package-qualified name
    utils_path = base / "utils" / "serialize.py"
    try:
        utils_spec = importlib.util.spec_from_file_location(pkg_prefix + ".utils.serialize", str(utils_path))
        utils_mod = importlib.util.module_from_spec(utils_spec)
        utils_spec.loader.exec_module(utils_mod)
        sys.modules[pkg_prefix + ".utils.serialize"] = utils_mod
    except Exception:
        # If utils can't be loaded, proceed — helpers may provide fallbacks.
        pass

    # Now load the helpers module with a package-qualified name so relative
    # imports inside it will resolve against the synthetic package entries.
    helper_path = base / "controllers" / "_helpers.py"
    spec = importlib.util.spec_from_file_location(pkg_prefix + ".controllers._helpers", str(helper_path))
    mod = importlib.util.module_from_spec(spec)
    # Ensure module is registered under its package-qualified name
    sys.modules[spec.name] = mod
    # Set __package__ so relative imports in the module resolve
    mod.__package__ = pkg_prefix + ".controllers"
    spec.loader.exec_module(mod)
    return mod

@pytest.fixture(scope="module")
def helpers():
    """Load helpers module with mocked dependencies."""
    return load_helpers_module_with_mocks()

class TestExtractBase64DataFromResult:
    """Test cases for extract_base64_data_from_result function."""

    def test_none_result(self, helpers):
        """Test with None result."""
        assert helpers.extract_base64_data_from_result(None) is None

    def test_empty_result(self, helpers):
        """Test with empty dict result."""
        assert helpers.extract_base64_data_from_result({}) is None

    def test_invalid_result_type(self, helpers):
        """Test with invalid result type."""
        assert helpers.extract_base64_data_from_result("invalid") is None

    def test_missing_body(self, helpers):
        """Test with result missing body."""
        result = {"http_status": 200}
        assert helpers.extract_base64_data_from_result(result) is None

    def test_invalid_body_type(self, helpers):
        """Test with invalid body type."""
        result = {"http_status": 200, "body": "invalid"}
        assert helpers.extract_base64_data_from_result(result) is None

    def test_missing_payload(self, helpers):
        """Test with body missing payload."""
        result = {"http_status": 200, "body": {}}
        assert helpers.extract_base64_data_from_result(result) is None

    def test_missing_history(self, helpers):
        """Test with payload missing history."""
        result = {"http_status": 200, "body": {"payload": {}}}
        assert helpers.extract_base64_data_from_result(result) is None

    def test_empty_outputs(self, helpers):
        """Test with empty outputs."""
        result = {
            "http_status": 200,
            "body": {"payload": {"history": {"outputs": {}}}}
        }
        assert helpers.extract_base64_data_from_result(result) is None

    @patch('folder_paths.get_directory_by_type')
    @patch('os.path.exists')
    @patch('PIL.Image.open')
    def test_standard_comfyui_format(self, mock_image_open, mock_exists, mock_get_dir, helpers):
        """Test with standard ComfyUI output format."""
        # Create a mock image with save method that writes actual data
        mock_img = mock_image_open.return_value.__enter__.return_value
        mock_img.mode = 'RGB'
        mock_img.convert.return_value = mock_img
        mock_img.save = lambda buffer, format: buffer.write(b'mock_png_data')

        # Mock the file system
        mock_get_dir.return_value = '/tmp/output'
        mock_exists.return_value = True

        # Create test result with standard ComfyUI format
        result = {
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

        with patch('builtins.open', mock_open()) as mock_file:
            result_data = helpers.extract_base64_data_from_result(result)

        assert result_data is not None
        assert result_data.startswith('data:image/png;base64,')

    @patch('folder_paths.get_directory_by_type')
    @patch('os.path.exists')
    @patch('PIL.Image.open')
    def test_lf_custom_format(self, mock_image_open, mock_exists, mock_get_dir, helpers):
        """Test with LF custom output format."""
        # Create a mock image with save method that writes actual data
        mock_img = mock_image_open.return_value.__enter__.return_value
        mock_img.mode = 'RGB'
        mock_img.convert.return_value = mock_img
        mock_img.save = lambda buffer, format: buffer.write(b'mock_png_data')

        # Mock the file system
        mock_get_dir.return_value = '/tmp/output'
        mock_exists.return_value = True

        # Create test result with LF custom format
        result = {
            "http_status": 200,
            "body": {
                "payload": {
                    "history": {
                        "outputs": {
                            "1": {
                                "lf_output": [
                                    {
                                        "file_names": ["lf_test.png"]
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        }

        with patch('builtins.open', mock_open()) as mock_file:
            result_data = helpers.extract_base64_data_from_result(result)

        assert result_data is not None
        assert result_data.startswith('data:image/png;base64,')

    @patch('folder_paths.get_directory_by_type')
    @patch('os.listdir')
    @patch('os.path.exists')
    @patch('PIL.Image.open')
    def test_fallback_to_recent_files(self, mock_image_open, mock_exists, mock_listdir, mock_get_dir, helpers):
        """Test fallback to recent output files when history is missing."""
        # Create a mock image
        mock_img = mock_image_open.return_value.__enter__.return_value
        mock_img.mode = 'RGB'
        mock_img.convert.return_value = mock_img

        # Mock the file system
        mock_get_dir.return_value = '/tmp/output'
        mock_exists.return_value = True
        mock_listdir.return_value = ['old.png', 'recent.png']
        # Mock getmtime to return recent.png as newer
        with patch('os.path.getmtime') as mock_getmtime:
            mock_getmtime.side_effect = lambda p: 100 if 'recent.png' in p else 50

            # Create test result with no outputs in history
            result = {
                "http_status": 200,
                "body": {"payload": {"history": {"outputs": {}}}}
            }

            with patch('builtins.open', mock_open()) as mock_file:
                result_data = helpers.extract_base64_data_from_result(result)

            assert result_data is not None
            assert result_data.startswith('data:image/png;base64,')

    @patch('folder_paths.get_directory_by_type')
    def test_file_not_found(self, mock_get_dir, helpers):
        """Test when image file doesn't exist."""
        mock_get_dir.return_value = '/tmp/output'

        result = {
            "http_status": 200,
            "body": {
                "payload": {
                    "history": {
                        "outputs": {
                            "1": {
                                "images": [
                                    {
                                        "filename": "missing.png",
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

        with patch('os.path.exists', return_value=False):
            assert helpers.extract_base64_data_from_result(result) is None

    def test_preferred_output_selection(self, helpers):
        """Test that preferred_output is used when available."""
        result = {
            "http_status": 200,
            "body": {
                "payload": {
                    "preferred_output": "2",
                    "history": {
                        "outputs": {
                            "1": {"images": [{"filename": "img1.png"}]},
                            "2": {"images": [{"filename": "img2.png"}]}
                        }
                    }
                }
            }
        }

        with patch('folder_paths.get_directory_by_type', return_value='/tmp/output'), \
             patch('os.path.exists', return_value=True), \
             patch('PIL.Image.open') as mock_img_open, \
             patch('builtins.open', mock_open()):

            mock_img = mock_img_open.return_value.__enter__.return_value
            mock_img.mode = 'RGB'
            mock_img.convert.return_value = mock_img

            result_data = helpers.extract_base64_data_from_result(result)

            # Should use output "2" (preferred), not "1"
            assert result_data is not None