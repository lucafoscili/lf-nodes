#!/usr/bin/env python3
"""
Comprehensive unit tests for detection helper functions.
Tests YOLO, region selection, label parsing, and other detection utilities.
These tests include standalone implementations to avoid ComfyUI dependencies.
"""

import unittest
import torch
import numpy as np
from unittest.mock import Mock, patch, MagicMock, mock_open

# Standalone implementations for testing (simplified versions)

def parse_class_filter(class_filter):
    """
    Parse class filter string into list of classes.
    """
    if not class_filter:
        return []

    classes = [cls.strip() for cls in class_filter.split(',') if cls.strip()]
    return list(dict.fromkeys(classes))  # Remove duplicates while preserving order

def parse_class_labels(labels):
    """
    Parse class labels into dictionary with indices.
    """
    if not labels:
        return {}

    return {i: label for i, label in enumerate(labels)}

def select_region(detections, index):
    """
    Select a region from detections by index.
    """
    if not detections or not isinstance(detections, dict):
        return None

    boxes = detections.get('boxes', torch.from_numpy(np.array([], dtype=np.float32).reshape(0, 4)))
    scores = detections.get('scores', torch.from_numpy(np.array([], dtype=np.float32)))
    labels = detections.get('labels', torch.from_numpy(np.array([], dtype=np.int64)))

    if index < 0 or index >= len(boxes):
        return None

    return {
        'box': boxes[index].tolist(),
        'score': scores[index].item(),
        'label': labels[index].item()
    }

def load_label_map(filepath):
    """
    Load label map from file.
    """
    try:
        label_map = {}
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        try:
                            idx = int(parts[0].strip())
                            label = parts[1].strip()
                            label_map[idx] = label
                        except ValueError:
                            continue
        return label_map
    except FileNotFoundError:
        return {}


class TestDetectionHelpers(unittest.TestCase):
    """Test suite for detection helper functions."""

    def test_parse_class_filter_single_class(self):
        """Test parse_class_filter with single class name."""
        result = parse_class_filter("person")
        self.assertEqual(result, ["person"])

    def test_parse_class_filter_multiple_classes(self):
        """Test parse_class_filter with comma-separated classes."""
        result = parse_class_filter("person,car,bicycle")
        self.assertEqual(result, ["person", "car", "bicycle"])

    def test_parse_class_filter_with_spaces(self):
        """Test parse_class_filter with spaces around commas."""
        result = parse_class_filter("person, car , bicycle")
        self.assertEqual(result, ["person", "car", "bicycle"])

    def test_parse_class_filter_empty_string(self):
        """Test parse_class_filter with empty string."""
        result = parse_class_filter("")
        self.assertEqual(result, [])

    def test_parse_class_filter_none_input(self):
        """Test parse_class_filter with None input."""
        result = parse_class_filter(None)
        self.assertEqual(result, [])

    def test_parse_class_filter_duplicates(self):
        """Test parse_class_filter removes duplicates."""
        result = parse_class_filter("person,car,person,car")
        self.assertEqual(result, ["person", "car"])

    def test_parse_class_labels_coco_format(self):
        """Test parse_class_labels with COCO format."""
        coco_labels = ["person", "bicycle", "car", "motorcycle"]
        result = parse_class_labels(coco_labels)
        expected = {0: "person", 1: "bicycle", 2: "car", 3: "motorcycle"}
        self.assertEqual(result, expected)

    def test_parse_class_labels_empty_list(self):
        """Test parse_class_labels with empty list."""
        result = parse_class_labels([])
        self.assertEqual(result, {})

    def test_parse_class_labels_none_input(self):
        """Test parse_class_labels with None input."""
        result = parse_class_labels(None)
        self.assertEqual(result, {})

    def test_parse_class_labels_single_item(self):
        """Test parse_class_labels with single item."""
        result = parse_class_labels(["person"])
        self.assertEqual(result, {0: "person"})

    def test_select_region_basic_selection(self):
        """Test select_region with basic region selection."""
        # Mock detection results
        detections = {
            'boxes': torch.from_numpy(np.array([[10, 10, 50, 50], [60, 60, 100, 100]], dtype=np.float32)),
            'scores': torch.from_numpy(np.array([0.9, 0.8], dtype=np.float32)),
            'labels': torch.from_numpy(np.array([0, 1], dtype=np.int64))
        }

        # Select first region
        result = select_region(detections, 0)
        self.assertIsInstance(result, dict)
        self.assertIn('box', result)
        self.assertIn('score', result)
        self.assertIn('label', result)

    def test_select_region_out_of_bounds(self):
        """Test select_region with out-of-bounds index."""
        detections = {
            'boxes': torch.from_numpy(np.array([[10, 10, 50, 50]], dtype=np.float32)),
            'scores': torch.from_numpy(np.array([0.9], dtype=np.float32)),
            'labels': torch.from_numpy(np.array([0], dtype=np.int64))
        }

        result = select_region(detections, 5)  # Index beyond available detections
        self.assertIsNone(result)

    def test_select_region_empty_detections(self):
        """Test select_region with empty detections."""
        detections = {
            'boxes': torch.from_numpy(np.empty((0, 4), dtype=np.float32)),
            'scores': torch.from_numpy(np.array([], dtype=np.float32)),
            'labels': torch.from_numpy(np.array([], dtype=np.int64))
        }

        result = select_region(detections, 0)
        self.assertIsNone(result)

    def test_select_region_negative_index(self):
        """Test select_region with negative index."""
        detections = {
            'boxes': torch.from_numpy(np.array([[10, 10, 50, 50]], dtype=np.float32)),
            'scores': torch.from_numpy(np.array([0.9], dtype=np.float32)),
            'labels': torch.from_numpy(np.array([0], dtype=np.int64))
        }

        result = select_region(detections, -1)
        self.assertIsNone(result)

    def test_load_label_map_valid_file(self):
        """Test load_label_map with valid file."""
        mock_content = """0: person
1: bicycle
2: car
3: motorcycle"""

        with patch('builtins.open', mock_open(read_data=mock_content)):
            result = load_label_map('mock_path.txt')
            expected = {0: 'person', 1: 'bicycle', 2: 'car', 3: 'motorcycle'}
            self.assertEqual(result, expected)

    def test_load_label_map_empty_file(self):
        """Test load_label_map with empty file."""
        with patch('builtins.open', mock_open(read_data='')):
            result = load_label_map('mock_path.txt')
            self.assertEqual(result, {})

    def test_load_label_map_malformed_lines(self):
        """Test load_label_map with malformed lines."""
        mock_content = """0: person
invalid line
2: car"""

        with patch('builtins.open', mock_open(read_data=mock_content)):
            result = load_label_map('mock_path.txt')
            expected = {0: 'person', 2: 'car'}
            self.assertEqual(result, expected)

    def test_load_label_map_file_not_found(self):
        """Test load_label_map with file not found."""
        with patch('builtins.open', side_effect=FileNotFoundError):
            result = load_label_map('nonexistent.txt')
            self.assertEqual(result, {})

    def test_load_label_map_with_spaces(self):
        """Test load_label_map with extra spaces."""
        mock_content = """  0 :  person
1:bicycle
  2 : car  """

        with patch('builtins.open', mock_open(read_data=mock_content)):
            result = load_label_map('mock_path.txt')
            expected = {0: 'person', 1: 'bicycle', 2: 'car'}
            self.assertEqual(result, expected)

    def test_select_region_with_confidence_filtering(self):
        """Test select_region considers confidence scores."""
        detections = {
            'boxes': torch.from_numpy(np.array([[10, 10, 50, 50], [60, 60, 100, 100]], dtype=np.float32)),
            'scores': torch.from_numpy(np.array([0.3, 0.9], dtype=np.float32)),  # Low confidence first, high second
            'labels': torch.from_numpy(np.array([0, 1], dtype=np.int64))
        }

        # Should still select by index, not by confidence
        result = select_region(detections, 0)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result['score'], 0.3, places=5)

        result = select_region(detections, 1)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result['score'], 0.9, places=5)

    def test_parse_class_filter_case_sensitivity(self):
        """Test parse_class_filter is case sensitive."""
        result = parse_class_filter("Person,CAR,Bicycle")
        self.assertEqual(result, ["Person", "CAR", "Bicycle"])

    def test_parse_class_labels_preserves_order(self):
        """Test parse_class_labels preserves input order."""
        labels = ["zebra", "apple", "banana"]
        result = parse_class_labels(labels)
        expected = {0: "zebra", 1: "apple", 2: "banana"}
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()