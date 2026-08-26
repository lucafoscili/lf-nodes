#!/usr/bin/env python3
"""
Tests for extract_base64_data_from_result function
"""
import base64
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
    mock_pil.Image = mock_pil_image
    sys.modules['folder_paths'] = mock_folder_paths
    sys.modules['PIL'] = mock_pil
    sys.modules['PIL.Image'] = mock_pil_image

    # Load utils.serialize into sys.modules under the package-qualified name
    media_path = base / "utils" / "media.py"
    media_spec = importlib.util.spec_from_file_location(pkg_prefix + ".utils.media", str(media_path))
    media_mod = importlib.util.module_from_spec(media_spec)
    media_spec.loader.exec_module(media_mod)
    sys.modules[pkg_prefix + ".utils.media"] = media_mod

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
    @patch('PIL.Image.open')
    def test_standard_comfyui_format(self, mock_image_open, mock_get_dir, helpers, tmp_path):
        """Test with standard ComfyUI output format."""
        # Create a mock image
        mock_img = mock_image_open.return_value.__enter__.return_value
        mock_img.mode = 'RGB'
        mock_img.convert.return_value = mock_img
        
        # Use a real contained path; Pillow itself remains mocked.
        output_root = tmp_path / 'output'
        output_root.mkdir()
        (output_root / 'test.png').touch()
        mock_get_dir.return_value = str(output_root)

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

        with patch('io.BytesIO') as mock_buffer_class:
            mock_buffer = mock_buffer_class.return_value
            mock_buffer.getvalue.return_value = b'mock_png_data'
            
            result_data = helpers.extract_base64_data_from_result(result)

        assert result_data is not None
        assert isinstance(result_data, tuple)
        assert len(result_data) == 2
        mime_type, base64_data = result_data
        assert mime_type == "image/png"
        assert base64_data == base64.b64encode(b'mock_png_data').decode('utf-8')

    @patch('folder_paths.get_directory_by_type')
    @patch('PIL.Image.open')
    def test_lf_custom_format(self, mock_image_open, mock_get_dir, helpers, tmp_path):
        """Test with LF custom output format."""
        # Create a mock image
        mock_img = mock_image_open.return_value.__enter__.return_value
        mock_img.mode = 'RGB'
        mock_img.convert.return_value = mock_img
        
        # Use a real contained path; Pillow itself remains mocked.
        output_root = tmp_path / 'output'
        (output_root / 'nested').mkdir(parents=True)
        (output_root / 'nested' / 'lf_test.png').touch()
        mock_get_dir.return_value = str(output_root)

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
                                        "file_names": ["nested/lf_test.png"]
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        }

        with patch('io.BytesIO') as mock_buffer_class:
            mock_buffer = mock_buffer_class.return_value
            mock_buffer.getvalue.return_value = b'mock_png_data'
            
            result_data = helpers.extract_base64_data_from_result(result)

        assert result_data is not None
        assert isinstance(result_data, tuple)
        assert len(result_data) == 2
        mime_type, base64_data = result_data
        assert mime_type == "image/png"
        assert base64_data == base64.b64encode(b'mock_png_data').decode('utf-8')

    @patch('folder_paths.get_directory_by_type')
    @patch('PIL.Image.open')
    def test_lf_custom_format_checks_every_lf_output_entry(
        self,
        mock_image_open,
        mock_get_dir,
        helpers,
        tmp_path,
    ):
        """Selection and extraction must agree when the image is not entry zero."""
        mock_img = mock_image_open.return_value.__enter__.return_value
        mock_img.mode = 'RGB'
        output_root = tmp_path / 'output'
        output_root.mkdir()
        (output_root / 'second.png').touch()
        mock_get_dir.return_value = str(output_root)
        result = {
            "http_status": 200,
            "body": {
                "payload": {
                    "history": {
                        "outputs": {
                            "save": {
                                "lf_output": [
                                    {"string": "first entry has no image"},
                                    {"file_names": ["second.png"]},
                                ]
                            }
                        }
                    }
                }
            },
        }

        with patch('io.BytesIO') as mock_buffer_class:
            mock_buffer_class.return_value.getvalue.return_value = b'second_png'
            result_data = helpers.extract_base64_data_from_result(result)

        assert result_data == (
            "image/png",
            base64.b64encode(b'second_png').decode('utf-8'),
        )
        opened_path = mock_image_open.call_args.args[0]
        assert str(opened_path).endswith('second.png')

    @patch('folder_paths.get_directory_by_type')
    @patch('PIL.Image.open')
    def test_jpeg_source_advertises_the_normalized_png_bytes(
        self,
        mock_image_open,
        mock_get_dir,
        helpers,
        tmp_path,
    ):
        mock_img = mock_image_open.return_value.__enter__.return_value
        mock_img.mode = 'RGB'
        output_root = tmp_path / 'output'
        output_root.mkdir()
        (output_root / 'source.jpg').touch()
        mock_get_dir.return_value = str(output_root)
        result = {
            "http_status": 200,
            "body": {
                "payload": {
                    "history": {
                        "outputs": {
                            "save": {
                                "images": [
                                    {
                                        "filename": "source.jpg",
                                        "subfolder": "",
                                        "type": "output",
                                    }
                                ]
                            }
                        }
                    }
                }
            },
        }

        with patch('io.BytesIO') as mock_buffer_class:
            mock_buffer_class.return_value.getvalue.return_value = b'normalized_png'
            mime_type, base64_data = helpers.extract_base64_data_from_result(result)

        assert mime_type == "image/png"
        assert base64_data == base64.b64encode(b'normalized_png').decode('utf-8')
        mock_img.save.assert_called_once_with(mock_buffer_class.return_value, format='PNG')

    @patch('folder_paths.get_directory_by_type')
    @patch('PIL.Image.open')
    def test_standard_comfy_video_is_not_opened_with_pillow(
        self,
        mock_image_open,
        mock_get_dir,
        helpers,
    ):
        """Comfy video savers expose MP4s under ``images`` for compatibility."""
        result = {
            "http_status": 200,
            "body": {
                "payload": {
                    "history": {
                        "outputs": {
                            "save": {
                                "images": [
                                    {
                                        "filename": "clip.mp4",
                                        "subfolder": "videos",
                                        "type": "output",
                                    }
                                ],
                                "animated": [True],
                            }
                        }
                    }
                }
            },
        }

        assert helpers.extract_base64_data_from_result(result) is None
        mock_get_dir.assert_not_called()
        mock_image_open.assert_not_called()

    @patch('folder_paths.get_directory_by_type')
    @patch('PIL.Image.open')
    def test_video_output_does_not_hide_a_later_image_output(
        self,
        mock_image_open,
        mock_get_dir,
        helpers,
        tmp_path,
    ):
        """Non-image descriptors are skipped while ordinary images stay unchanged."""
        mock_img = mock_image_open.return_value.__enter__.return_value
        mock_img.mode = 'RGB'
        output_root = tmp_path / 'output'
        output_root.mkdir()
        (output_root / 'poster.png').touch()
        mock_get_dir.return_value = str(output_root)
        result = {
            "http_status": 200,
            "body": {
                "payload": {
                    "history": {
                        "outputs": {
                            "video": {
                                "images": [
                                    {"filename": "clip.mp4", "type": "output"}
                                ]
                            },
                            "poster": {
                                "images": [
                                    {"filename": "poster.png", "type": "output"}
                                ]
                            },
                        }
                    }
                }
            },
        }

        with patch('io.BytesIO') as mock_buffer_class:
            mock_buffer_class.return_value.getvalue.return_value = b'mock_png_data'
            result_data = helpers.extract_base64_data_from_result(result)

        assert result_data == (
            "image/png",
            base64.b64encode(b'mock_png_data').decode('utf-8'),
        )
        mock_image_open.assert_called_once()
        opened_path = mock_image_open.call_args.args[0]
        assert str(opened_path).endswith('poster.png')
        assert 'clip.mp4' not in str(opened_path)

    @patch('folder_paths.get_directory_by_type')
    @patch('PIL.Image.open')
    def test_video_images_do_not_hide_lf_images_on_same_output(
        self,
        mock_image_open,
        mock_get_dir,
        helpers,
        tmp_path,
    ):
        """A legacy video descriptor must not mask a valid LF preview image."""
        mock_img = mock_image_open.return_value.__enter__.return_value
        mock_img.mode = 'RGB'
        output_root = tmp_path / 'output'
        output_root.mkdir()
        (output_root / 'poster.png').touch()
        mock_get_dir.return_value = str(output_root)
        result = {
            "http_status": 200,
            "body": {
                "payload": {
                    "history": {
                        "outputs": {
                            "save": {
                                "images": [
                                    {"filename": "clip.mp4", "type": "output"}
                                ],
                                "lf_images": [
                                    {"filename": "poster.png", "type": "output"}
                                ],
                            }
                        }
                    }
                }
            },
        }

        with patch('io.BytesIO') as mock_buffer_class:
            mock_buffer_class.return_value.getvalue.return_value = b'mock_png_data'
            result_data = helpers.extract_base64_data_from_result(result)

        assert result_data == (
            "image/png",
            base64.b64encode(b'mock_png_data').decode('utf-8'),
        )
        opened_path = mock_image_open.call_args.args[0]
        assert str(opened_path).endswith('poster.png')
        assert 'clip.mp4' not in str(opened_path)

    def test_lf_svg_direct_content(self, helpers):
        """Test with LF SVG direct content in slot_map."""
        # Create test result with LF SVG direct content
        svg_content = '<svg xmlns="http://www.w3.org/2000/svg"><circle cx="50" cy="50" r="40"/></svg>'
        result = {
            "http_status": 200,
            "body": {
                "payload": {
                    "history": {
                        "outputs": {
                            "20": {
                                "lf_output": [
                                    {
                                        "dataset": {
                                            "nodes": [
                                                {
                                                    "cells": {
                                                        "lfSlot": {
                                                            "shape": "slot",
                                                            "value": "icon.svg"
                                                        }
                                                    },
                                                    "id": "0",
                                                    "value": "0"
                                                }
                                            ]
                                        },
                                        "slot_map": {
                                            "icon.svg": svg_content
                                        },
                                        "svg": "plain svg string"
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        }
        
        result_data = helpers.extract_base64_data_from_result(result)

        assert result_data is not None
        assert isinstance(result_data, tuple)
        assert len(result_data) == 2
        mime_type, base64_data = result_data
        assert mime_type == "image/svg+xml"
        # Verify the base64 data decodes back to the original SVG
        decoded_svg = base64.b64decode(base64_data).decode('utf-8')
        assert decoded_svg == svg_content

    def test_lf_svg_json_escaped_content(self, helpers):
        """Test with LF SVG content that has JSON escaping."""
        # Create test result with JSON-escaped SVG content
        escaped_svg = '\\u003Csvg xmlns=\\"http://www.w3.org/2000/svg\\"\\u003E\\u003Ccircle cx=\\"50\\" cy=\\"50\\" r=\\"40\\"/\\u003E\\u003C/svg\\u003E'
        expected_svg = '<svg xmlns="http://www.w3.org/2000/svg"><circle cx="50" cy="50" r="40"/></svg>'
        result = {
            "http_status": 200,
            "body": {
                "payload": {
                    "history": {
                        "outputs": {
                            "20": {
                                "lf_output": [
                                    {
                                        "slot_map": {
                                            "icon.svg": escaped_svg
                                        }
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        }
        
        result_data = helpers.extract_base64_data_from_result(result)

        assert result_data is not None
        assert isinstance(result_data, tuple)
        assert len(result_data) == 2
        mime_type, base64_data = result_data
        assert mime_type == "image/svg+xml"
        # Verify the base64 data decodes back to the unescaped SVG
        decoded_svg = base64.b64decode(base64_data).decode('utf-8')
        assert decoded_svg == expected_svg

    @patch('folder_paths.get_directory_by_type')
    @patch('PIL.Image.open')
    def test_outputless_history_never_guesses_the_newest_global_file(
        self,
        mock_image_open,
        mock_get_dir,
        helpers,
    ):
        result = {
            "http_status": 200,
            "body": {"payload": {"history": {"outputs": {}}}},
        }

        assert helpers.extract_base64_data_from_result(result) is None
        mock_get_dir.assert_not_called()
        mock_image_open.assert_not_called()

    @patch('folder_paths.get_directory_by_type')
    def test_file_not_found(self, mock_get_dir, helpers, tmp_path):
        """Test when image file doesn't exist."""
        output_root = tmp_path / 'output'
        output_root.mkdir()
        mock_get_dir.return_value = str(output_root)

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

        assert helpers.extract_base64_data_from_result(result) is None

    @pytest.mark.parametrize(
        ("filename", "subfolder", "storage_type"),
        (
            ("../secret.png", "", "output"),
            ("secret.png", "../outside", "output"),
            (r"C:\\Windows\\secret.png", "", "output"),
            ("/tmp/secret.png", "", "output"),
            ("secret.png", "", "untrusted"),
        ),
    )
    @patch('folder_paths.get_directory_by_type')
    @patch('PIL.Image.open')
    def test_history_descriptor_cannot_escape_or_choose_an_unknown_root(
        self,
        mock_image_open,
        mock_get_dir,
        filename,
        subfolder,
        storage_type,
        helpers,
        tmp_path,
    ):
        output_root = tmp_path / 'output'
        output_root.mkdir()
        mock_get_dir.return_value = str(output_root)
        result = {
            "http_status": 200,
            "body": {
                "payload": {
                    "history": {
                        "outputs": {
                            "save": {
                                "images": [
                                    {
                                        "filename": filename,
                                        "subfolder": subfolder,
                                        "type": storage_type,
                                    }
                                ]
                            }
                        }
                    }
                }
            },
        }

        assert helpers.extract_base64_data_from_result(result) is None
        mock_image_open.assert_not_called()

    @patch('folder_paths.get_directory_by_type')
    @patch('PIL.Image.open')
    def test_history_descriptor_rejects_a_symlink_escape(
        self,
        mock_image_open,
        mock_get_dir,
        helpers,
        tmp_path,
    ):
        output_root = tmp_path / 'output'
        outside = tmp_path / 'outside'
        output_root.mkdir()
        outside.mkdir()
        (outside / 'secret.png').touch()
        try:
            (output_root / 'linked').symlink_to(outside, target_is_directory=True)
        except OSError:
            pytest.skip('directory symlinks are unavailable on this host')
        mock_get_dir.return_value = str(output_root)
        result = {
            "http_status": 200,
            "body": {
                "payload": {
                    "history": {
                        "outputs": {
                            "save": {
                                "images": [
                                    {
                                        "filename": "secret.png",
                                        "subfolder": "linked",
                                        "type": "output",
                                    }
                                ]
                            }
                        }
                    }
                }
            },
        }

        assert helpers.extract_base64_data_from_result(result) is None
        mock_image_open.assert_not_called()

    def test_preferred_output_selection(self, helpers, tmp_path):
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

        output_root = tmp_path / 'output'
        output_root.mkdir()
        (output_root / 'img1.png').touch()
        (output_root / 'img2.png').touch()

        with patch('folder_paths.get_directory_by_type', return_value=str(output_root)), \
             patch('PIL.Image.open') as mock_img_open, \
             patch('builtins.open', mock_open()):

            mock_img = mock_img_open.return_value.__enter__.return_value
            mock_img.mode = 'RGB'
            mock_img.convert.return_value = mock_img

            result_data = helpers.extract_base64_data_from_result(result)

            # Should use output "2" (preferred), not "1"
            assert result_data is not None
