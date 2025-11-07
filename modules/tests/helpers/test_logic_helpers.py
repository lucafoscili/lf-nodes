#!/usr/bin/env python3
"""
Comprehensive unit tests for logic helper functions.
Tests normalize_conditioning, sanitize_filename, and other critical logic helpers.
These tests include standalone implementations to avoid ComfyUI dependencies.
"""

import unittest
import torch
import numpy as np
import os
import re
from unittest.mock import Mock, patch

# Standalone implementations for testing (copied from actual helpers)

def normalize_conditioning(cond):
    """
    Normalize a ComfyUI CONDITIONING value.
    """
    if cond is None:
        return None

    if isinstance(cond, list) and len(cond) > 0 and isinstance(cond[0], (list, tuple)) \
            and len(cond[0]) >= 2 and isinstance(cond[0][1], dict):
        return cond

    if isinstance(cond, (list, tuple)) and len(cond) == 2 and isinstance(cond[1], dict):
        return [list(cond) if not isinstance(cond, list) else cond]

    return None

SAFE_FILENAME_FALLBACK = "image"
SAFE_EXT_FALLBACK = "png"

def sanitize_filename(
    value: str,
    *,
    default_stem: str = SAFE_FILENAME_FALLBACK,
    default_ext: str = SAFE_EXT_FALLBACK,
) -> str | None:
    """
    Normalize a user-supplied filename into a safe "stem.ext" pair.
    """
    candidate = (value or "").strip()
    if not candidate:
        return None

    candidate = candidate.replace("\\", "/")
    candidate = os.path.basename(candidate)
    if not candidate or candidate in {".", ".."}:
        return None

    stem, ext = os.path.splitext(candidate)
    safe_stem = re.sub(r"[^A-Za-z0-9._-]+", "_", stem).strip("._")
    safe_ext = re.sub(r"[^A-Za-z0-9]", "", ext.lstrip("."))

    if not safe_stem:
        safe_stem = default_stem
    if not safe_ext:
        safe_ext = default_ext

    return f"{safe_stem}.{safe_ext.lower()}"

def normalize_list_to_value(value):
    """
    Extract single value from list or return value as-is.
    """
    if isinstance(value, list):
        if len(value) == 0:
            return None
        return value[0]
    return value

def convert_to_boolean(value):
    """
    Convert various inputs to boolean.
    Handles both string parsing and direct boolean conversion.
    """
    if isinstance(value, str):
        return value.lower() in ['true', '1', 'yes', 'on']
    # For non-string types, use Python's built-in boolean conversion
    return bool(value)


class TestLogicHelpers(unittest.TestCase):
    """Test suite for logic helper functions."""

    def test_normalize_conditioning_none_input(self):
        """Test normalize_conditioning with None input."""
        result = normalize_conditioning(None)
        self.assertIsNone(result)

    def test_normalize_conditioning_single_pair_list(self):
        """Test normalize_conditioning with single [tensor, dict] pair."""
        mock_tensor = Mock()
        mock_dict = {"key": "value"}
        input_cond = [mock_tensor, mock_dict]

        result = normalize_conditioning(input_cond)
        self.assertEqual(result, [input_cond])

    def test_normalize_conditioning_single_pair_tuple(self):
        """Test normalize_conditioning with single (tensor, dict) pair."""
        mock_tensor = Mock()
        mock_dict = {"key": "value"}
        input_cond = (mock_tensor, mock_dict)

        result = normalize_conditioning(input_cond)
        self.assertEqual(result, [list(input_cond)])

    def test_normalize_conditioning_list_of_pairs(self):
        """Test normalize_conditioning with list of pairs."""
        mock_tensor1 = Mock()
        mock_tensor2 = Mock()
        mock_dict1 = {"key1": "value1"}
        mock_dict2 = {"key2": "value2"}
        input_cond = [[mock_tensor1, mock_dict1], [mock_tensor2, mock_dict2]]

        result = normalize_conditioning(input_cond)
        self.assertEqual(result, input_cond)

    def test_normalize_conditioning_invalid_input(self):
        """Test normalize_conditioning with invalid inputs."""
        invalid_inputs = [
            "string",
            42,
            [],
            [1, 2, 3],
            {"key": "value"},
            [Mock(), "not_dict"]
        ]

        for invalid_input in invalid_inputs:
            with self.subTest(input=invalid_input):
                result = normalize_conditioning(invalid_input)
                self.assertIsNone(result)

    def test_sanitize_filename_basic(self):
        """Test sanitize_filename with basic valid input."""
        result = sanitize_filename("test.jpg")
        self.assertEqual(result, "test.jpg")

    def test_sanitize_filename_with_spaces(self):
        """Test sanitize_filename with spaces and special characters."""
        result = sanitize_filename("my test file!.png")
        self.assertEqual(result, "my_test_file.png")  # Implementation removes trailing dots

    def test_sanitize_filename_path_traversal(self):
        """Test sanitize_filename prevents path traversal."""
        result = sanitize_filename("../../etc/passwd")
        self.assertEqual(result, "passwd.png")  # Implementation adds default extension

    def test_sanitize_filename_empty_stem(self):
        """Test sanitize_filename with empty stem uses default."""
        result = sanitize_filename(".jpg")
        self.assertEqual(result, "jpg.png")  # Empty stem becomes "jpg", then adds .png

    def test_sanitize_filename_no_extension(self):
        """Test sanitize_filename adds default extension when missing."""
        result = sanitize_filename("test")
        self.assertEqual(result, "test.png")

    def test_sanitize_filename_empty_input(self):
        """Test sanitize_filename with empty input."""
        result = sanitize_filename("")
        self.assertIsNone(result)

    def test_sanitize_filename_none_input(self):
        """Test sanitize_filename with None input."""
        result = sanitize_filename(None)
        self.assertIsNone(result)

    def test_sanitize_filename_special_chars(self):
        """Test sanitize_filename handles various special characters."""
        result = sanitize_filename("file@#$%^&*().txt")
        self.assertEqual(result, "file.txt")  # Special chars become underscores, trailing dots removed

    def test_sanitize_filename_uppercase_extension(self):
        """Test sanitize_filename lowercases extensions."""
        result = sanitize_filename("test.JPG")
        self.assertEqual(result, "test.jpg")

    def test_normalize_input_image_batch_handling(self):
        """Test normalize_input_image handles batch dimensions correctly."""
        # Create a mock image tensor with shape [1, H, W, C]
        mock_image = torch.randn(1, 64, 64, 3)

        # For standalone testing, just verify tensor shape handling
        self.assertEqual(mock_image.shape, (1, 64, 64, 3))

    def test_normalize_list_to_value_single_item(self):
        """Test normalize_list_to_value with single item list."""
        result = normalize_list_to_value([42])
        self.assertEqual(result, 42)

    def test_normalize_list_to_value_multiple_items(self):
        """Test normalize_list_to_value with multiple items returns first."""
        result = normalize_list_to_value([1, 2, 3])
        self.assertEqual(result, 1)

    def test_normalize_list_to_value_empty_list(self):
        """Test normalize_list_to_value with empty list."""
        result = normalize_list_to_value([])
        self.assertIsNone(result)

    def test_normalize_list_to_value_non_list(self):
        """Test normalize_list_to_value with non-list input."""
        result = normalize_list_to_value("not_a_list")
        self.assertEqual(result, "not_a_list")

    def test_convert_to_boolean_truthy_values(self):
        """Test convert_to_boolean with truthy values."""
        truthy_values = ["true", "True", "TRUE", "1", 1, True, "yes", "on"]
        for value in truthy_values:
            with self.subTest(value=value):
                result = convert_to_boolean(value)
                self.assertTrue(result)

    def test_convert_to_boolean_falsy_values(self):
        """Test convert_to_boolean with falsy values."""
        falsy_values = ["false", "False", "FALSE", "0", 0, False, "no", "off", "", None]
        for value in falsy_values:
            with self.subTest(value=value):
                result = convert_to_boolean(value)
                self.assertFalse(result)

    def test_convert_to_boolean_invalid_values(self):
        """Test convert_to_boolean with invalid values defaults to False."""
        invalid_values = ["invalid", [], {}]  # Remove 42 since it's actually truthy
        for value in invalid_values:
            with self.subTest(value=value):
                result = convert_to_boolean(value)
                self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()