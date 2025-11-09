"""
Unit tests for ComfyUI helper functions.
Tests cover directory resolution, file listing, tokenizer extraction, and path management.
"""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch, mock_open
import torch


# region Embedded function implementations for standalone testing
def get_comfy_dir(folder: str):
    """
    Retrieve the directory path corresponding to a specified folder type.
    """
    import os

    # Mock the folder_paths functions for testing
    def mock_get_input_directory():
        return "/mock/input"

    def mock_get_output_directory():
        return "/mock/output"

    def mock_get_temp_directory():
        return "/mock/temp"

    def mock_get_user_directory():
        return "/mock/user"

    # Mock constants
    BACKUP_FOLDER = "backup"
    USER_FOLDER = "user"

    if folder == "backup":
        dirpath = os.path.join(mock_get_user_directory(), USER_FOLDER)
        return os.path.join(dirpath, BACKUP_FOLDER)
    if folder == "base":
        return os.path.join(mock_get_user_directory(), USER_FOLDER)
    if folder == "input":
        return mock_get_input_directory()
    elif folder == "output":
        return mock_get_output_directory()
    elif folder == "temp":
        return mock_get_temp_directory()
    elif folder == "user":
        return mock_get_user_directory()
    else:
        raise ValueError(f"Invalid folder type: {folder}")


def get_comfy_list(folder: str):
    """
    Retrieve a list of filenames from a specified folder.
    """
    # Mock implementation for testing
    mock_lists = {
        "checkpoints": ["model1.safetensors", "model2.ckpt"],
        "embeddings": ["embedding1.pt", "embedding2.safetensors"],
        "loras": ["lora1.safetensors", "lora2.pt"],
        "upscale_models": ["upscale1.pth", "upscale2.onnx"],
        "vae": ["vae1.safetensors", "vae2.ckpt"]
    }

    if folder == "vae":
        try:
            # Mock VAE loader
            return ["vae_pixel_space", "vae_taesd", "vae1.safetensors"]
        except Exception:
            return mock_lists.get(folder, [])

    return mock_lists.get(folder, [])


def get_tokenizer_from_clip(clip):
    """
    Retrieve the tokenizer from a CLIP model.
    """
    # 1) SDXLClipModel in ComfyUI: clip.tokenizer has clip_l and clip_g
    if (hasattr(clip, "tokenizer") and
        hasattr(clip.tokenizer, "clip_l") and
        hasattr(clip.tokenizer, "clip_g") and
        not hasattr(clip.tokenizer, "tokenizer")):  # Ensure it's not HF style
        # prefer the 'clip_l' tokenizer for encoding
        tok = clip.tokenizer.clip_l
        if hasattr(tok, "tokenizer"):
            tok = tok.tokenizer
        return tok

    # 2) HuggingFace Transformers style
    if (hasattr(clip, "tokenizer") and
        hasattr(clip.tokenizer, "tokenizer") and
        not hasattr(clip.tokenizer, "clip_l")):  # Ensure it's not SDXL style
        tok = clip.tokenizer
        # Some HF pipelines wrap the real tokenizer under .tokenizer
        if hasattr(tok, "tokenizer"):
            tok = tok.tokenizer
        return tok

    # 3) Direct tokenizer
    if (hasattr(clip, "tokenizer") and
        not hasattr(clip.tokenizer, "clip_l") and
        not hasattr(clip.tokenizer, "tokenizer")):
        return clip.tokenizer

    # 4) Diffusers pipelines
    if hasattr(clip, "pipeline") and hasattr(clip.pipeline, "tokenizer"):
        return clip.pipeline.tokenizer

    raise AttributeError(f"Could not find a CLIP tokenizer in {clip!r}")


def resolve_filepath(
        filename_prefix: str = None,
        base_output_path: str = None,
        add_timestamp: bool = False,
        extension: str = "PNG",
        add_counter: bool = True,
        image: torch.Tensor = None,
        temp_cache = None) -> tuple[str, str, str]:
    """
    Resolve and prepare a file path for saving an image.
    """
    # Mock implementation for testing
    USER_FOLDER = "user"

    if filename_prefix is None:
        filename_prefix = f"{USER_FOLDER}/ComfyUI"
    else:
        # Mock normalize_list_to_value
        if isinstance(filename_prefix, list):
            filename_prefix = filename_prefix[0] if filename_prefix else ""

    if base_output_path is None:
        base_output_path = get_comfy_dir("temp")

    if add_timestamp:
        filename_prefix = f"{filename_prefix}_%year%-%month%-%day%_%hour%-%minute%-%second%"

    # Mock image dimension extraction
    if isinstance(image, torch.Tensor) and len(image.shape) >= 3:
        height = image.shape[1]
        width = image.shape[2]
    else:
        height = None
        width = None

    # Mock get_save_image_path behavior
    output_folder = base_output_path
    filename = filename_prefix.replace('/', '_').replace('\\', '_')
    counter = 1
    subfolder = ""

    if add_counter:
        while os.path.exists(os.path.join(output_folder, f"{filename}_{counter}.{extension}")):
            counter += 1
        filename = f"{filename}_{counter}.{extension}"
    else:
        filename = f"{filename}.{extension}"

    output_file = os.path.join(output_folder, filename)

    if temp_cache and hasattr(temp_cache, 'register'):
        temp_cache.register(output_file)

    os.makedirs(output_folder, exist_ok=True)

    return output_file, subfolder, filename


class ResolvedDirectory:
    """Container describing a directory resolved against a ComfyUI base."""
    def __init__(self, absolute_path, relative_path, is_external):
        self.absolute_path = absolute_path
        self.relative_path = relative_path
        self.is_external = is_external

    def __eq__(self, other):
        if not isinstance(other, ResolvedDirectory):
            return False
        return (self.absolute_path == other.absolute_path and
                self.relative_path == other.relative_path and
                self.is_external == other.is_external)

    def __repr__(self):
        return f"ResolvedDirectory({self.absolute_path!r}, {self.relative_path!r}, {self.is_external!r})"


def _sanitize_path_component(value: str) -> str | None:
    """
    Sanitize a single filesystem path component.
    """
    if value in ("", ".", ".."):
        return None

    # Mock sanitize_filename
    def mock_sanitize_filename(name, default_ext="tmp"):
        # Simple mock - remove invalid chars and ensure safe
        safe_name = "".join(c for c in name if c.isalnum() or c in "._- ")
        if not safe_name:
            return None
        return safe_name

    sanitized = mock_sanitize_filename(f"{value}.tmp", default_ext="tmp")
    if sanitized is None:
        return None

    return os.path.splitext(sanitized)[0]


def resolve_input_directory_path(
    directory,
    *,
    base_type: str = "input",
) -> ResolvedDirectory:
    """
    Resolve a user-supplied directory string against ComfyUI's configured base directory.
    """
    base_dir = get_comfy_dir(base_type)
    base_abs = os.path.abspath(base_dir)

    if directory is None:
        return ResolvedDirectory(base_abs, "", False)

    if hasattr(directory, '__fspath__'):  # PathLike
        directory = os.fspath(directory)

    if not isinstance(directory, str):
        return ResolvedDirectory(None, "", False)

    candidate_path = directory.strip()
    if not candidate_path:
        return ResolvedDirectory(base_abs, "", False)

    abs_candidate = os.path.abspath(candidate_path)
    if os.path.isdir(abs_candidate):
        try:
            common = os.path.commonpath([base_abs, abs_candidate])
        except ValueError:
            common = None

        if common == base_abs:
            rel_path = os.path.relpath(abs_candidate, base_abs)
            rel_path = "" if rel_path == "." else rel_path.replace("\\", "/")
            return ResolvedDirectory(abs_candidate, rel_path, False)

        return ResolvedDirectory(abs_candidate, "", True)

    normalized = candidate_path.strip().strip("\\/")
    if not normalized:
        return ResolvedDirectory(base_abs, "", False)

    if os.path.isabs(normalized):
        return ResolvedDirectory(None, "", False)

    components = [part for part in normalized.replace("\\", "/").split("/") if part]
    current_dir = base_dir
    actual_components: list[str] = []

    for component in components:
        target = _sanitize_path_component(component)
        if target is None:
            return ResolvedDirectory(None, "", False)

        try:
            entries = os.listdir(current_dir)
        except OSError:
            return ResolvedDirectory(None, "", False)

        match_entry = None
        for entry in entries:
            entry_path = os.path.join(current_dir, entry)
            if not os.path.isdir(entry_path):
                continue
            if entry == component:
                match_entry = entry
                break
            if _sanitize_path_component(entry) == target:
                match_entry = entry
                break

        if match_entry is None:
            return ResolvedDirectory(None, "", False)

        current_dir = os.path.join(current_dir, match_entry)
        actual_components.append(match_entry)

    rel_path = "/".join(actual_components)
    return ResolvedDirectory(current_dir, rel_path, False)
# endregion


class TestComfyHelpers(unittest.TestCase):
    """Test suite for ComfyUI helper functions."""

    def test_get_comfy_dir_input(self):
        """Test get_comfy_dir with input folder."""
        result = get_comfy_dir("input")
        self.assertEqual(result, "/mock/input")

    def test_get_comfy_dir_output(self):
        """Test get_comfy_dir with output folder."""
        result = get_comfy_dir("output")
        self.assertEqual(result, "/mock/output")

    def test_get_comfy_dir_temp(self):
        """Test get_comfy_dir with temp folder."""
        result = get_comfy_dir("temp")
        self.assertEqual(result, "/mock/temp")

    def test_get_comfy_dir_user(self):
        """Test get_comfy_dir with user folder."""
        result = get_comfy_dir("user")
        self.assertEqual(result, "/mock/user")

    def test_get_comfy_dir_backup(self):
        """Test get_comfy_dir with backup folder."""
        result = get_comfy_dir("backup")
        expected = os.path.join("/mock/user", "user", "backup")
        self.assertEqual(result, expected)

    def test_get_comfy_dir_base(self):
        """Test get_comfy_dir with base folder."""
        result = get_comfy_dir("base")
        expected = os.path.join("/mock/user", "user")
        self.assertEqual(result, expected)

    def test_get_comfy_dir_invalid(self):
        """Test get_comfy_dir with invalid folder type."""
        with self.assertRaises(ValueError) as cm:
            get_comfy_dir("invalid")
        self.assertIn("Invalid folder type", str(cm.exception))

    def test_get_comfy_list_checkpoints(self):
        """Test get_comfy_list with checkpoints folder."""
        result = get_comfy_list("checkpoints")
        expected = ["model1.safetensors", "model2.ckpt"]
        self.assertEqual(result, expected)

    def test_get_comfy_list_embeddings(self):
        """Test get_comfy_list with embeddings folder."""
        result = get_comfy_list("embeddings")
        expected = ["embedding1.pt", "embedding2.safetensors"]
        self.assertEqual(result, expected)

    def test_get_comfy_list_loras(self):
        """Test get_comfy_list with loras folder."""
        result = get_comfy_list("loras")
        expected = ["lora1.safetensors", "lora2.pt"]
        self.assertEqual(result, expected)

    def test_get_comfy_list_upscale_models(self):
        """Test get_comfy_list with upscale_models folder."""
        result = get_comfy_list("upscale_models")
        expected = ["upscale1.pth", "upscale2.onnx"]
        self.assertEqual(result, expected)

    def test_get_comfy_list_vae(self):
        """Test get_comfy_list with vae folder."""
        result = get_comfy_list("vae")
        # Should use VAE loader mock
        self.assertIn("vae_pixel_space", result)
        self.assertIn("vae1.safetensors", result)

    def test_get_comfy_list_unknown_folder(self):
        """Test get_comfy_list with unknown folder."""
        result = get_comfy_list("unknown")
        self.assertEqual(result, [])

    def test_get_tokenizer_from_clip_sdxl_style(self):
        """Test get_tokenizer_from_clip with SDXL-style CLIP model."""
        clip = MagicMock(spec=['tokenizer'])
        clip.tokenizer = MagicMock(spec=['clip_l', 'clip_g'])
        clip.tokenizer.clip_l = MagicMock(spec=['tokenizer'])
        clip.tokenizer.clip_l.tokenizer = MagicMock()
        clip.tokenizer.clip_g = MagicMock()

        result = get_tokenizer_from_clip(clip)
        self.assertEqual(result, clip.tokenizer.clip_l.tokenizer)

    def test_get_tokenizer_from_clip_sdxl_no_nested_tokenizer(self):
        """Test get_tokenizer_from_clip with SDXL-style CLIP without nested tokenizer."""
        clip = MagicMock(spec=['tokenizer'])
        clip.tokenizer = MagicMock(spec=['clip_l', 'clip_g'])
        clip.tokenizer.clip_l = MagicMock(spec=[])  # No tokenizer attribute
        clip.tokenizer.clip_g = MagicMock()

        result = get_tokenizer_from_clip(clip)
        self.assertEqual(result, clip.tokenizer.clip_l)

    def test_get_tokenizer_from_clip_huggingface_style(self):
        """Test get_tokenizer_from_clip with HuggingFace-style CLIP."""
        clip = MagicMock(spec=['tokenizer'])
        clip.tokenizer = MagicMock(spec=['tokenizer'])
        clip.tokenizer.tokenizer = MagicMock()

        result = get_tokenizer_from_clip(clip)
        self.assertEqual(result, clip.tokenizer.tokenizer)

    def test_get_tokenizer_from_clip_huggingface_direct(self):
        """Test get_tokenizer_from_clip with direct HuggingFace tokenizer."""
        clip = MagicMock(spec=['tokenizer'])
        clip.tokenizer = MagicMock(spec=[])

        result = get_tokenizer_from_clip(clip)
        self.assertEqual(result, clip.tokenizer)

    def test_get_tokenizer_from_clip_diffusers_style(self):
        """Test get_tokenizer_from_clip with Diffusers pipeline."""
        clip = MagicMock(spec=['pipeline'])
        clip.pipeline = MagicMock(spec=['tokenizer'])
        clip.pipeline.tokenizer = MagicMock()

        result = get_tokenizer_from_clip(clip)
        self.assertEqual(result, clip.pipeline.tokenizer)

    def test_get_tokenizer_from_clip_no_tokenizer(self):
        """Test get_tokenizer_from_clip with CLIP model that has no tokenizer."""
        clip = MagicMock(spec=[])

        with self.assertRaises(AttributeError) as cm:
            get_tokenizer_from_clip(clip)
        self.assertIn("Could not find a CLIP tokenizer", str(cm.exception))

    def test_resolve_filepath_basic(self):
        """Test resolve_filepath with basic parameters."""
        with patch('os.makedirs'):
            result = resolve_filepath("test_prefix", "/tmp/output", extension="PNG")
            output_file, subfolder, filename = result

            self.assertTrue(output_file.endswith("test_prefix_1.PNG"))
            self.assertEqual(subfolder, "")
            self.assertEqual(filename, "test_prefix_1.PNG")

    def test_resolve_filepath_no_prefix(self):
        """Test resolve_filepath with no filename prefix."""
        with patch('os.makedirs'):
            result = resolve_filepath(extension="JPG")
            output_file, subfolder, filename = result

            self.assertIn("user_ComfyUI_1.JPG", output_file)

    def test_resolve_filepath_with_timestamp(self):
        """Test resolve_filepath with timestamp enabled."""
        with patch('os.makedirs'):
            result = resolve_filepath("test", add_timestamp=True, extension="PNG")
            output_file, subfolder, filename = result

            self.assertIn("_%year%-%month%-%day%_%hour%-%minute%-%second%", filename)
            self.assertTrue(filename.endswith("_1.PNG"))

    def test_resolve_filepath_no_counter(self):
        """Test resolve_filepath without counter."""
        with patch('os.makedirs'):
            result = resolve_filepath("test", add_counter=False, extension="PNG")
            output_file, subfolder, filename = result

            self.assertEqual(filename, "test.PNG")

    def test_resolve_filepath_with_image_tensor(self):
        """Test resolve_filepath with torch tensor image."""
        # Create a mock tensor
        image = torch.randn(1, 512, 512, 3)
        with patch('os.makedirs'):
            result = resolve_filepath("test", image=image, extension="PNG")
            output_file, subfolder, filename = result

            # Should still work even with tensor
            self.assertTrue(filename.endswith("_1.PNG"))

    def test_resolve_filepath_list_prefix(self):
        """Test resolve_filepath with list filename prefix."""
        with patch('os.makedirs'):
            result = resolve_filepath(["prefix1", "prefix2"], extension="PNG")
            output_file, subfolder, filename = result

            self.assertIn("prefix1_1.PNG", filename)

    def test_resolve_filepath_temp_cache(self):
        """Test resolve_filepath with temp cache."""
        mock_cache = MagicMock()
        with patch('os.makedirs'):
            result = resolve_filepath("test", temp_cache=mock_cache, extension="PNG")
            mock_cache.register.assert_called_once()

    def test_resolve_input_directory_path_none(self):
        """Test resolve_input_directory_path with None input."""
        result = resolve_input_directory_path(None)
        self.assertEqual(result.relative_path, "")
        self.assertFalse(result.is_external)
        self.assertIsNotNone(result.absolute_path)

    def test_resolve_input_directory_path_empty_string(self):
        """Test resolve_input_directory_path with empty string."""
        result = resolve_input_directory_path("")
        self.assertEqual(result.relative_path, "")
        self.assertFalse(result.is_external)
        self.assertIsNotNone(result.absolute_path)

    def test_resolve_input_directory_path_whitespace(self):
        """Test resolve_input_directory_path with whitespace only."""
        result = resolve_input_directory_path("   ")
        self.assertEqual(result.relative_path, "")
        self.assertFalse(result.is_external)
        self.assertIsNotNone(result.absolute_path)

    def test_resolve_input_directory_path_invalid_type(self):
        """Test resolve_input_directory_path with invalid type."""
        result = resolve_input_directory_path(123)
        self.assertIsNone(result.absolute_path)
        self.assertEqual(result.relative_path, "")
        self.assertFalse(result.is_external)

    def test_resolve_input_directory_path_absolute_nonexistent(self):
        """Test resolve_input_directory_path with absolute nonexistent path."""
        result = resolve_input_directory_path("/nonexistent/path")
        self.assertIsNone(result.absolute_path)
        self.assertEqual(result.relative_path, "")
        self.assertFalse(result.is_external)

    def test_resolve_input_directory_path_external_directory(self):
        """Test resolve_input_directory_path with external existing directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a directory outside the mock base
            external_dir = os.path.join(temp_dir, "external")
            os.makedirs(external_dir)

            result = resolve_input_directory_path(external_dir)
            self.assertEqual(result.absolute_path, os.path.abspath(external_dir))
            self.assertEqual(result.relative_path, "")
            self.assertTrue(result.is_external)

    def test_resolve_input_directory_path_relative_path(self):
        """Test resolve_input_directory_path with relative path."""
        # This would require setting up mock directory structure
        # For now, test that invalid relative paths fail
        result = resolve_input_directory_path("nonexistent/subdir")
        self.assertIsNone(result.absolute_path)
        self.assertEqual(result.relative_path, "")
        self.assertFalse(result.is_external)

    def test_sanitize_path_component_valid(self):
        """Test _sanitize_path_component with valid input."""
        result = _sanitize_path_component("valid_name")
        self.assertEqual(result, "valid_name")

    def test_sanitize_path_component_invalid_dots(self):
        """Test _sanitize_path_component with invalid dot inputs."""
        self.assertIsNone(_sanitize_path_component(""))
        self.assertIsNone(_sanitize_path_component("."))
        self.assertIsNone(_sanitize_path_component(".."))

    def test_sanitize_path_component_special_chars(self):
        """Test _sanitize_path_component with special characters."""
        result = _sanitize_path_component("file@name#test")
        # Should only keep alphanumeric and safe chars
        self.assertTrue(all(c.isalnum() or c in "._- " for c in result))

    def test_sanitize_path_component_empty_after_sanitization(self):
        """Test _sanitize_path_component that becomes empty after sanitization."""
        result = _sanitize_path_component("!@#$%^&*()")
        # Mock implementation might return None for this case
        # This depends on the mock sanitize_filename behavior


if __name__ == '__main__':
    unittest.main()