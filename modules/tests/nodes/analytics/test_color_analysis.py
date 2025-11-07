# region Test Color Analysis Node
# Set up common mocks before any imports
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from common_mocks import setup_common_mocks
setup_common_mocks()

import json
import unittest
from unittest.mock import MagicMock, patch
import numpy as np
import torch

# Import the actual node implementation
from modules.nodes.analytics.color_analysis import LF_ColorAnalysis, NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
from modules.utils.constants import Input
from common_mocks import mock_prompt_server


class TestColorAnalysisNode(unittest.TestCase):
    """Test cases for LF_ColorAnalysis node following TDD principles."""

    def setUp(self):
        """Set up test fixtures."""
        self.node = LF_ColorAnalysis()
        self.test_node_id = "test_node_123"

    def test_class_attributes(self):
        """Test class attributes are properly set."""
        self.assertEqual(LF_ColorAnalysis.CATEGORY, "✨ LF Nodes/Analytics")
        self.assertEqual(LF_ColorAnalysis.FUNCTION, "on_exec")
        self.assertEqual(LF_ColorAnalysis.OUTPUT_IS_LIST, (False, True, False))
        self.assertEqual(LF_ColorAnalysis.RETURN_TYPES, (Input.IMAGE, Input.IMAGE, Input.JSON))
        self.assertEqual(LF_ColorAnalysis.RETURN_NAMES, ("image", "image_list", "dataset"))
        self.assertTrue(LF_ColorAnalysis.OUTPUT_NODE)

    def test_input_types_structure(self):
        """Test INPUT_TYPES returns correct structure."""
        inputs = LF_ColorAnalysis.INPUT_TYPES()

        # Check required inputs
        self.assertIn("required", inputs)
        self.assertIn("source_image", inputs["required"])
        self.assertIn("target_image", inputs["required"])

        # Check optional inputs
        self.assertIn("optional", inputs)
        self.assertIn("ui_widget", inputs["optional"])

        # Check hidden inputs
        self.assertIn("hidden", inputs)
        self.assertIn("node_id", inputs["hidden"])

    def test_input_types_validation(self):
        """Test INPUT_TYPES parameter validation."""
        inputs = LF_ColorAnalysis.INPUT_TYPES()

        # Check source_image input
        source_input = inputs["required"]["source_image"]
        self.assertEqual(source_input[0], Input.IMAGE)
        self.assertIn("tooltip", source_input[1])

        # Check target_image input
        target_input = inputs["required"]["target_image"]
        self.assertEqual(target_input[0], Input.IMAGE)
        self.assertIn("tooltip", target_input[1])

        # Check ui_widget input
        ui_widget_input = inputs["optional"]["ui_widget"]
        self.assertEqual(ui_widget_input[0], Input.LF_TAB_BAR_CHART)
        self.assertEqual(ui_widget_input[1]["default"], {})

    def test_node_mappings(self):
        """Test node class and display name mappings."""
        self.assertIn("LF_ColorAnalysis", NODE_CLASS_MAPPINGS)
        self.assertEqual(NODE_CLASS_MAPPINGS["LF_ColorAnalysis"], LF_ColorAnalysis)
        self.assertIn("LF_ColorAnalysis", NODE_DISPLAY_NAME_MAPPINGS)
        self.assertEqual(NODE_DISPLAY_NAME_MAPPINGS["LF_ColorAnalysis"], "Color Analysis")

    @patch('modules.nodes.analytics.color_analysis.safe_send_sync')
    def test_on_exec_successful_processing(self, mock_safe_send_sync):
        """Test successful color analysis processing."""
        # Create test images (simple 2x2 RGB images)
        source_image = torch.tensor([[[[255, 0, 0], [0, 255, 0]],
                                      [[0, 0, 255], [255, 255, 255]]]], dtype=torch.float32)  # 1x2x2x3

        target_image = torch.tensor([[[[100, 50, 25], [25, 100, 50]],
                                      [[50, 25, 100], [200, 150, 100]]]], dtype=torch.float32)  # 1x2x2x3

        # Execute the node
        result = self.node.on_exec(
            source_image=source_image,
            target_image=target_image,
            node_id=self.test_node_id
        )

        # Verify results
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)

        # Check image outputs
        image_batch, image_list, dataset = result
        self.assertIsNotNone(image_batch)
        self.assertIsInstance(image_list, list)
        self.assertIsInstance(dataset, dict)

        # Verify safe_send_sync was called
        mock_safe_send_sync.assert_called_once()
        call_args = mock_safe_send_sync.call_args
        self.assertEqual(call_args[0][0], "coloranalysis")
        self.assertIn("datasets", call_args[0][1])

    @patch('modules.nodes.analytics.color_analysis.safe_send_sync')
    def test_on_exec_batch_processing(self, mock_safe_send_sync):
        """Test color analysis with multiple image pairs."""
        # Create test images (batch of 2 images each)
        source_images = [
            torch.tensor([[[[255, 0, 0], [0, 255, 0]], [[0, 0, 255], [255, 255, 255]]]], dtype=torch.float32),
            torch.tensor([[[[100, 100, 100], [50, 50, 50]], [[150, 150, 150], [200, 200, 200]]]], dtype=torch.float32)
        ]

        target_images = [
            torch.tensor([[[[100, 50, 25], [25, 100, 50]], [[50, 25, 100], [200, 150, 100]]]], dtype=torch.float32),
            torch.tensor([[[[75, 125, 175], [25, 75, 125]], [[125, 175, 225], [150, 100, 50]]]], dtype=torch.float32)
        ]

        # Execute the node
        result = self.node.on_exec(
            source_image=source_images,
            target_image=target_images,
            node_id=self.test_node_id
        )

        # Verify results
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)

        image_batch, image_list, dataset = result
        self.assertIsNotNone(image_batch)
        self.assertIsInstance(image_list, list)
        self.assertIsInstance(dataset, dict)

        # Should have datasets for both images
        self.assertIn("Image #1", dataset)
        self.assertIn("Image #2", dataset)

    def test_on_exec_mismatched_batch_sizes(self):
        """Test on_exec raises error for mismatched batch sizes."""
        # Create images with different batch sizes that will result in different normalized lengths
        source_image = torch.tensor([[[[255, 0, 0], [0, 255, 0]],
                                      [[0, 0, 255], [255, 255, 255]]]], dtype=torch.float32)  # 1 image

        target_images = [
            torch.tensor([[[[100, 50, 25], [25, 100, 50]], [[50, 25, 100], [200, 150, 100]]]], dtype=torch.float32),  # 1 image
            torch.tensor([[[[75, 125, 175], [25, 75, 125]], [[125, 175, 225], [150, 100, 50]]]], dtype=torch.float32)   # 1 image
        ]  # 2 images total

        with self.assertRaises(ValueError) as context:
            self.node.on_exec(
                source_image=source_image,
                target_image=target_images,
                node_id=self.test_node_id
            )

        self.assertIn("Source and Target batches should have the same number of images", str(context.exception))

    def test_on_exec_empty_images(self):
        """Test on_exec with empty image inputs."""
        with self.assertRaises(ValueError):
            self.node.on_exec(
                source_image=None,
                target_image=None,
                node_id=self.test_node_id
            )

    @patch('modules.nodes.analytics.color_analysis.PromptServer')
    def test_on_exec_with_ui_widget(self, mock_prompt_server_class):
        """Test on_exec with ui_widget parameter."""
        # Setup mock PromptServer
        mock_prompt_server_instance = MagicMock()
        mock_prompt_server_class.instance = mock_prompt_server_instance

        # Create test images
        source_image = torch.tensor([[[[255, 0, 0], [0, 255, 0]],
                                      [[0, 0, 255], [255, 255, 255]]]], dtype=torch.float32)

        target_image = torch.tensor([[[[100, 50, 25], [25, 100, 50]],
                                      [[50, 25, 100], [200, 150, 100]]]], dtype=torch.float32)

        ui_widget = {"some": "config"}

        # Execute the node
        result = self.node.on_exec(
            source_image=source_image,
            target_image=target_image,
            ui_widget=ui_widget,
            node_id=self.test_node_id
        )

        # Verify results
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)

    def test_generate_mapping_basic(self):
        """Test generate_mapping with basic histograms."""
        # Create simple histograms (256 values for 0-255 intensity levels)
        source_hist = np.zeros(256, dtype=int)
        source_hist[3:6] = 1  # Peak at intensity 3-5

        target_hist = np.zeros(256, dtype=int)
        target_hist[2:5] = 1  # Peak at intensity 2-4

        mapping = LF_ColorAnalysis.generate_mapping(target_hist, source_hist)

        # Verify mapping is a list of length 256
        self.assertIsInstance(mapping, list)
        self.assertEqual(len(mapping), 256)

        # Verify all values are integers between 0-255
        for value in mapping:
            self.assertIsInstance(value, int)
            self.assertGreaterEqual(value, 0)
            self.assertLessEqual(value, 255)

    def test_generate_mapping_identical_histograms(self):
        """Test generate_mapping with identical histograms."""
        # Create identical histograms
        hist = np.zeros(256, dtype=int)
        hist[3:6] = 1

        mapping = LF_ColorAnalysis.generate_mapping(hist, hist)

        # For identical histograms, mapping should be identity (0->0, 1->1, etc.)
        for i in range(256):
            if i < len(hist) and hist[i] > 0:
                # Values should map to themselves for the range of the histogram
                self.assertEqual(mapping[i], i)
            else:
                # Values beyond histogram range should still be valid
                self.assertIsInstance(mapping[i], int)

    def test_generate_mapping_edge_cases(self):
        """Test generate_mapping with edge case histograms."""
        # Test with uniform distribution
        uniform_hist = np.ones(256, dtype=int)
        mapping = LF_ColorAnalysis.generate_mapping(uniform_hist, uniform_hist)

        self.assertIsInstance(mapping, list)
        self.assertEqual(len(mapping), 256)

        # Test with single peak
        peak_hist = np.zeros(256, dtype=int)
        peak_hist[128] = 100
        mapping = LF_ColorAnalysis.generate_mapping(peak_hist, peak_hist)

        self.assertIsInstance(mapping, list)
        self.assertEqual(len(mapping), 256)


if __name__ == '__main__':
    unittest.main()
# endregion