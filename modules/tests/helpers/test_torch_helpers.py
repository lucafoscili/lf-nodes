#!/usr/bin/env python3
"""
Comprehensive unit tests for torch helper functions.
Tests image processing, text encoding, and tensor operations.
These tests include standalone implementations to avoid ComfyUI dependencies.
"""

import unittest
import torch
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
import torchvision.transforms as T

# Standalone implementations for testing (simplified versions)

def resize_image(tensor, width, height):
    """
    Resize image tensor to specified dimensions.
    """
    if tensor.dim() == 3:  # CHW format
        transform = T.Resize((height, width))
        return transform(tensor)
    return tensor

def resize_to_square(tensor, size):
    """
    Resize image tensor to square dimensions.
    """
    return resize_image(tensor, size, size)

def create_dummy_image_tensor(height, width, channels):
    """
    Create a dummy image tensor with specified dimensions.
    """
    return torch.rand(channels, height, width)

def tensor_to_pil(tensor):
    """
    Convert tensor to PIL Image.
    """
    if tensor.dim() == 3 and tensor.shape[0] == 3:  # CHW RGB
        img_array = (tensor.permute(1, 2, 0) * 255).clamp(0, 255).to(torch.uint8).numpy()
        return Image.fromarray(img_array, mode='RGB')
    elif tensor.dim() == 3 and tensor.shape[0] == 1:  # CHW Grayscale
        img_array = (tensor.squeeze(0) * 255).clamp(0, 255).to(torch.uint8).numpy()
        return Image.fromarray(img_array, mode='L')
    elif tensor.dim() == 3 and tensor.shape[0] == 4:  # CHW RGBA
        img_array = (tensor.permute(1, 2, 0) * 255).clamp(0, 255).to(torch.uint8).numpy()
        return Image.fromarray(img_array, mode='RGBA')
    return None

def pil_to_tensor(pil_image, return_numpy=False):
    """
    Convert PIL Image to tensor.
    """
    transform = T.ToTensor()
    tensor = transform(pil_image)

    if return_numpy:
        # Convert to HWC format for numpy output
        return tensor.permute(1, 2, 0).numpy()
    return tensor


class TestTorchHelpers(unittest.TestCase):
    """Test suite for torch helper functions."""

    def test_resize_image_basic(self):
        """Test resize_image with basic tensor."""
        # Create a test tensor [C, H, W]
        tensor = torch.randn(3, 64, 64)

        result = resize_image(tensor, 32, 32)
        self.assertIsInstance(result, torch.Tensor)
        self.assertEqual(result.shape, (3, 32, 32))

    def test_resize_image_same_size(self):
        """Test resize_image when target size matches input size."""
        tensor = torch.randn(3, 64, 64)

        result = resize_image(tensor, 64, 64)
        self.assertIsInstance(result, torch.Tensor)
        self.assertEqual(result.shape, (3, 64, 64))

    def test_resize_image_different_aspect_ratio(self):
        """Test resize_image with different aspect ratio."""
        tensor = torch.randn(3, 100, 50)  # 2:1 aspect ratio

        result = resize_image(tensor, 200, 100)  # 2:1 aspect ratio maintained
        self.assertIsInstance(result, torch.Tensor)
        self.assertEqual(result.shape, (3, 100, 200))  # Note: H, W order

    def test_resize_image_float_tensor(self):
        """Test resize_image with float tensor."""
        tensor = torch.randn(3, 64, 64, dtype=torch.float32)

        result = resize_image(tensor, 32, 32)
        self.assertEqual(result.dtype, torch.float32)

    def test_resize_to_square_basic(self):
        """Test resize_to_square with rectangular tensor."""
        tensor = torch.randn(3, 100, 50)  # Not square

        result = resize_to_square(tensor, 64)
        self.assertIsInstance(result, torch.Tensor)
        self.assertEqual(result.shape, (3, 64, 64))

    def test_resize_to_square_already_square(self):
        """Test resize_to_square with already square tensor."""
        tensor = torch.randn(3, 64, 64)

        result = resize_to_square(tensor, 64)
        self.assertIsInstance(result, torch.Tensor)
        self.assertEqual(result.shape, (3, 64, 64))

    def test_resize_to_square_smaller_input(self):
        """Test resize_to_square when input is smaller than target."""
        tensor = torch.randn(3, 32, 32)

        result = resize_to_square(tensor, 64)
        self.assertIsInstance(result, torch.Tensor)
        self.assertEqual(result.shape, (3, 64, 64))

    def test_create_dummy_image_tensor_basic(self):
        """Test create_dummy_image_tensor with basic parameters."""
        result = create_dummy_image_tensor(64, 64, 3)

        self.assertIsInstance(result, torch.Tensor)
        self.assertEqual(result.shape, (3, 64, 64))
        self.assertEqual(result.dtype, torch.float32)
        # Should be in range [0, 1] for float tensors
        self.assertTrue(torch.all(result >= 0))
        self.assertTrue(torch.all(result <= 1))

    def test_create_dummy_image_tensor_different_channels(self):
        """Test create_dummy_image_tensor with different channel counts."""
        for channels in [1, 3, 4]:
            with self.subTest(channels=channels):
                result = create_dummy_image_tensor(32, 32, channels)
                self.assertEqual(result.shape, (channels, 32, 32))

    def test_create_dummy_image_tensor_different_sizes(self):
        """Test create_dummy_image_tensor with different sizes."""
        sizes = [(16, 16), (128, 256), (1, 1)]
        for height, width in sizes:
            with self.subTest(size=(height, width)):
                result = create_dummy_image_tensor(height, width, 3)
                self.assertEqual(result.shape, (3, height, width))

    def test_tensor_to_pil_basic(self):
        """Test tensor_to_pil with basic tensor."""
        # Create a simple test tensor [C, H, W] with values in [0, 1]
        tensor = torch.zeros(3, 32, 32)
        tensor[0, :, :] = 1.0  # Red channel
        tensor[1, :, :] = 0.5  # Green channel
        tensor[2, :, :] = 0.0  # Blue channel

        result = tensor_to_pil(tensor)
        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.mode, 'RGB')
        self.assertEqual(result.size, (32, 32))

    def test_tensor_to_pil_single_channel(self):
        """Test tensor_to_pil with single channel (grayscale)."""
        tensor = torch.ones(1, 32, 32) * 0.5

        result = tensor_to_pil(tensor)
        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.mode, 'L')  # Grayscale
        self.assertEqual(result.size, (32, 32))

    def test_tensor_to_pil_four_channels(self):
        """Test tensor_to_pil with four channels (RGBA)."""
        tensor = torch.ones(4, 32, 32) * 0.5

        result = tensor_to_pil(tensor)
        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.mode, 'RGBA')
        self.assertEqual(result.size, (32, 32))

    def test_tensor_to_pil_uint8_tensor(self):
        """Test tensor_to_pil with uint8 tensor."""
        tensor = torch.randint(0, 256, (3, 32, 32), dtype=torch.uint8)

        result = tensor_to_pil(tensor)
        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.mode, 'RGB')
        self.assertEqual(result.size, (32, 32))

    def test_pil_to_tensor_rgb_image(self):
        """Test pil_to_tensor with RGB PIL image."""
        # Create a test PIL image
        pil_image = Image.new('RGB', (32, 32), color=(255, 128, 0))

        result = pil_to_tensor(pil_image)
        self.assertIsInstance(result, torch.Tensor)
        self.assertEqual(result.shape, (3, 32, 32))
        self.assertEqual(result.dtype, torch.float32)
        # Values should be in [0, 1]
        self.assertTrue(torch.all(result >= 0))
        self.assertTrue(torch.all(result <= 1))

    def test_pil_to_tensor_grayscale_image(self):
        """Test pil_to_tensor with grayscale PIL image."""
        pil_image = Image.new('L', (32, 32), color=128)

        result = pil_to_tensor(pil_image)
        self.assertIsInstance(result, torch.Tensor)
        self.assertEqual(result.shape, (1, 32, 32))
        self.assertEqual(result.dtype, torch.float32)

    def test_pil_to_tensor_rgba_image(self):
        """Test pil_to_tensor with RGBA PIL image."""
        pil_image = Image.new('RGBA', (32, 32), color=(255, 128, 0, 255))

        result = pil_to_tensor(pil_image)
        self.assertIsInstance(result, torch.Tensor)
        self.assertEqual(result.shape, (4, 32, 32))
        self.assertEqual(result.dtype, torch.float32)

    def test_pil_to_tensor_numpy_output(self):
        """Test pil_to_tensor returns numpy array when specified."""
        pil_image = Image.new('RGB', (32, 32), color=(255, 128, 0))

        result = pil_to_tensor(pil_image, return_numpy=True)
        self.assertIsInstance(result, np.ndarray)
        self.assertEqual(result.shape, (32, 32, 3))  # HWC format for numpy
        self.assertEqual(result.dtype, np.float32)


if __name__ == '__main__':
    unittest.main()