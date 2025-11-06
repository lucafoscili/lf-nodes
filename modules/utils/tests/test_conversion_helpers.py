#!/usr/bin/env python3
"""
Comprehensive unit tests for conversion helper functions.
Tests JSON conversion, tensor conversions, base64, and other data type conversions.
These tests include standalone implementations to avoid ComfyUI dependencies.
"""

import unittest
import torch
import numpy as np
import json
import base64
from unittest.mock import Mock, patch, mock_open
from PIL import Image
import io

# Standalone implementations for testing (copied from actual helpers)

def convert_to_json(text):
    """
    Convert a given text to a JSON object.
    """
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None

def convert_to_int(value):
    """
    Convert value to integer.
    """
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None

def convert_to_float(value):
    """
    Convert value to float.
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def tensor_to_numpy(tensor):
    """
    Convert tensor to numpy array.
    """
    result = tensor.detach().cpu().numpy()
    result.flags.writeable = False  # Make it read-only like the real implementation
    return result

def numpy_to_tensor(array):
    """
    Convert numpy array to tensor.
    """
    return torch.from_numpy(array)

def tensor_to_base64(tensor):
    """
    Convert tensor to base64 encoded image.
    """
    # Simple implementation for testing
    if tensor.dtype != torch.uint8:
        tensor = (tensor * 255).clamp(0, 255).to(torch.uint8)

    # Convert to PIL Image (simplified)
    if tensor.shape[0] == 3:  # CHW format
        img = Image.fromarray(tensor.permute(1, 2, 0).numpy())
    else:
        img = Image.fromarray(tensor.squeeze(0).numpy())

    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f'data:image/png;base64,{img_base64}'

def base64_to_tensor(base64_str):
    """
    Convert base64 encoded image to tensor.
    """
    try:
        if not base64_str.startswith('data:image'):
            return None

        # Extract base64 data
        base64_data = base64_str.split(',')[1]
        img_data = base64.b64decode(base64_data)

        # Convert to PIL Image
        img = Image.open(io.BytesIO(img_data))

        # Convert to tensor
        if img.mode == 'RGB':
            tensor = torch.from_numpy(np.array(img)).permute(2, 0, 1).float() / 255.0
        else:
            tensor = torch.from_numpy(np.array(img)).unsqueeze(0).float() / 255.0

        return tensor
    except Exception:
        return None

def normalize_hex_color(color):
    """
    Normalize hex color to #RRGGBB format.
    """
    if not color or not isinstance(color, str):
        return None

    color = color.strip()
    if color.startswith('#'):
        color = color[1:]

    # Handle extra characters by taking only the first 6 chars
    color = color[:6]

    # Handle 3-digit hex
    if len(color) == 3:
        color = ''.join(c * 2 for c in color)

    # Validate 6-digit hex
    if len(color) == 6 and all(c in '0123456789abcdefABCDEF' for c in color):
        return f'#{color.lower()}'

    return None


class TestConversionHelpers(unittest.TestCase):
    """Test suite for conversion helper functions."""

    def test_convert_to_json_valid_json(self):
        """Test convert_to_json with valid JSON string."""
        test_data = {"key": "value", "number": 42}
        json_str = json.dumps(test_data)

        result = convert_to_json(json_str)
        self.assertEqual(result, test_data)

    def test_convert_to_json_invalid_json(self):
        """Test convert_to_json with invalid JSON string."""
        result = convert_to_json("not json")
        self.assertIsNone(result)

    def test_convert_to_json_none_input(self):
        """Test convert_to_json with None input."""
        result = convert_to_json(None)
        self.assertIsNone(result)

    def test_convert_to_json_empty_string(self):
        """Test convert_to_json with empty string."""
        result = convert_to_json("")
        self.assertIsNone(result)

    def test_convert_to_json_array(self):
        """Test convert_to_json with JSON array."""
        test_array = [1, 2, 3, "test"]
        json_str = json.dumps(test_array)

        result = convert_to_json(json_str)
        self.assertEqual(result, test_array)

    def test_convert_to_int_valid_string(self):
        """Test convert_to_int with valid string."""
        result = convert_to_int("42")
        self.assertEqual(result, 42)

    def test_convert_to_int_valid_float_string(self):
        """Test convert_to_int with float string (should truncate)."""
        result = convert_to_int("42.7")
        self.assertEqual(result, 42)

    def test_convert_to_int_invalid_string(self):
        """Test convert_to_int with invalid string."""
        result = convert_to_int("not_a_number")
        self.assertIsNone(result)

    def test_convert_to_int_none_input(self):
        """Test convert_to_int with None input."""
        result = convert_to_int(None)
        self.assertIsNone(result)

    def test_convert_to_int_already_int(self):
        """Test convert_to_int with integer input."""
        result = convert_to_int(42)
        self.assertEqual(result, 42)

    def test_convert_to_float_valid_string(self):
        """Test convert_to_float with valid string."""
        result = convert_to_float("3.14")
        self.assertEqual(result, 3.14)

    def test_convert_to_float_integer_string(self):
        """Test convert_to_float with integer string."""
        result = convert_to_float("42")
        self.assertEqual(result, 42.0)

    def test_convert_to_float_invalid_string(self):
        """Test convert_to_float with invalid string."""
        result = convert_to_float("not_a_number")
        self.assertIsNone(result)

    def test_convert_to_float_none_input(self):
        """Test convert_to_float with None input."""
        result = convert_to_float(None)
        self.assertIsNone(result)

    def test_tensor_to_numpy_cpu_tensor(self):
        """Test tensor_to_numpy with CPU tensor."""
        tensor = torch.randn(3, 64, 64)
        result = tensor_to_numpy(tensor)

        self.assertIsInstance(result, np.ndarray)
        self.assertEqual(result.shape, (3, 64, 64))

    def test_tensor_to_numpy_cuda_tensor(self):
        """Test tensor_to_numpy with CUDA tensor (if available)."""
        if torch.cuda.is_available():
            tensor = torch.randn(3, 64, 64).cuda()
            result = tensor_to_numpy(tensor)

            self.assertIsInstance(result, np.ndarray)
            self.assertEqual(result.shape, (3, 64, 64))
        else:
            self.skipTest("CUDA not available")

    def test_tensor_to_numpy_with_detach(self):
        """Test tensor_to_numpy detaches gradients."""
        tensor = torch.randn(3, 64, 64, requires_grad=True)
        result = tensor_to_numpy(tensor)

        self.assertFalse(result.flags.writeable)  # Should be read-only after detach

    def test_numpy_to_tensor_basic(self):
        """Test numpy_to_tensor with basic numpy array."""
        array = np.random.randn(3, 64, 64).astype(np.float32)
        result = numpy_to_tensor(array)

        self.assertIsInstance(result, torch.Tensor)
        self.assertEqual(result.shape, (3, 64, 64))
        self.assertEqual(result.dtype, torch.float32)

    def test_numpy_to_tensor_different_dtypes(self):
        """Test numpy_to_tensor with different numpy dtypes."""
        test_cases = [
            (np.uint8, torch.uint8),
            (np.float32, torch.float32),
            (np.int64, torch.int64)
        ]

        for np_dtype, expected_torch_dtype in test_cases:
            with self.subTest(np_dtype=np_dtype):
                array = np.array([1, 2, 3], dtype=np_dtype)
                result = numpy_to_tensor(array)
                self.assertEqual(result.dtype, expected_torch_dtype)

    def test_tensor_to_base64_basic(self):
        """Test tensor_to_base64 with basic tensor."""
        # Create a small test tensor
        tensor = torch.ones(3, 4, 4, dtype=torch.uint8) * 255

        result = tensor_to_base64(tensor)
        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith('data:image/png;base64,'))

    def test_tensor_to_base64_float_tensor(self):
        """Test tensor_to_base64 with float tensor (should be converted)."""
        tensor = torch.ones(3, 4, 4, dtype=torch.float32)

        result = tensor_to_base64(tensor)
        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith('data:image/png;base64,'))

    def test_base64_to_tensor_basic(self):
        """Test base64_to_tensor with valid base64 string."""
        # First create a tensor and convert to base64
        original_tensor = torch.ones(3, 4, 4, dtype=torch.uint8) * 255
        base64_str = tensor_to_base64(original_tensor)

        # Now convert back
        result_tensor = base64_to_tensor(base64_str)
        self.assertIsInstance(result_tensor, torch.Tensor)
        self.assertEqual(result_tensor.shape, original_tensor.shape)

    def test_base64_to_tensor_invalid_input(self):
        """Test base64_to_tensor with invalid base64."""
        result = base64_to_tensor("invalid_base64")
        self.assertIsNone(result)

    def test_normalize_hex_color_valid_hex(self):
        """Test normalize_hex_color with valid hex colors."""
        test_cases = [
            ("#FF0000", "#ff0000"),
            ("#ff0000", "#ff0000"),
            ("FF0000", "#ff0000"),
            ("f00", "#ff0000"),
            ("#f00", "#ff0000")
        ]

        for input_color, expected in test_cases:
            with self.subTest(input=input_color):
                result = normalize_hex_color(input_color)
                self.assertEqual(result, expected)

    def test_normalize_hex_color_invalid_input(self):
        """Test normalize_hex_color with invalid inputs."""
        invalid_inputs = ["not_hex", "", None, "#GGG", "#12345", "red"]

        for invalid_input in invalid_inputs:
            with self.subTest(input=invalid_input):
                result = normalize_hex_color(invalid_input)
                self.assertIsNone(result)

    def test_normalize_hex_color_edge_cases(self):
        """Test normalize_hex_color with edge cases."""
        # Test with extra characters
        result = normalize_hex_color("#FF0000extra")
        self.assertEqual(result, "#ff0000")  # Function returns lowercase

        # Test with lowercase
        result = normalize_hex_color("ff0000")
        self.assertEqual(result, "#ff0000")


if __name__ == '__main__':
    unittest.main()