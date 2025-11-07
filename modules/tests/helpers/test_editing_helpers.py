#!/usr/bin/env python3
"""
Comprehensive test suite for editing helper functions.
Tests context management, dataset operations, and editing sessions.
"""

import json
import os
import tempfile
import unittest
from unittest.mock import MagicMock, mock_open, patch

# Embedded implementations for standalone testing
# region context.py functions
_EDITING_CONTEXTS = {}

def register_editing_context(identifier, **context):
    """Registers an editing context with the given identifier and any related values."""
    if not identifier:
        return
    _EDITING_CONTEXTS[identifier] = context

def get_editing_context(identifier):
    """Retrieves the editing context associated with a given identifier."""
    if not identifier:
        return None
    return _EDITING_CONTEXTS.get(identifier)

def clear_editing_context(identifier):
    """Removes the editing context associated with the given identifier."""
    if not identifier:
        return
    _EDITING_CONTEXTS.pop(identifier, None)
# endregion

# region dataset.py functions
def _as_dict(value):
    """Converts the input value to a dictionary if it is already a dictionary, otherwise returns an empty dictionary."""
    return value if isinstance(value, dict) else {}

def _build_fallback_entries(count, context_id=None):
    """Generates fallback entries for a dataset."""
    names = [f"Image {idx + 1}" for idx in range(count)]
    urls = [""] * count
    node_ids = [None] * count
    metadata = [
        {
            "index": idx,
            "name": names[idx],
            "url": "",
            "node_id": None,
            **({"context_id": context_id} if context_id else {}),
        }
        for idx in range(count)
    ]
    return names, urls, node_ids, metadata

def ensure_dataset_context(dataset, fallback_context=None):
    """Ensures that the provided dataset and its selection contain a context identifier."""
    if not isinstance(dataset, dict):
        return fallback_context

    context_id = dataset.get("context_id") or fallback_context

    selection = _as_dict(dataset.get("selection"))
    selection_context = selection.get("context_id") or context_id

    if selection_context:
        selection["context_id"] = selection_context
        if selection.get("context_id") and selection["context_id"] != context_id:
            context_id = selection["context_id"]
        dataset["selection"] = selection

    if context_id:
        dataset["context_id"] = context_id

    return context_id

def extract_dataset_entries(dataset, fallback_count=0, context_id=None):
    """Extract lightweight metadata for each image entry in the dataset."""
    if not isinstance(dataset, dict):
        return _build_fallback_entries(fallback_count, context_id)

    names = []
    urls = []
    node_ids = []
    metadata = []

    nodes = dataset.get("nodes")
    if not isinstance(nodes, list):
        return names, urls, node_ids, metadata

    for index, node in enumerate(nodes):
        if not isinstance(node, dict):
            continue

        image_cell = _as_dict(_as_dict(node.get("cells")).get("lfImage"))
        html_props = _as_dict(image_cell.get("htmlProps"))

        name = (
            html_props.get("title")
            or html_props.get("id")
            or (node.get("value") if isinstance(node.get("value"), str) else None)
            or f"{index + 1}"
        )

        url = image_cell.get("lfValue") or image_cell.get("value")
        node_id = node.get("id") if isinstance(node.get("id"), str) else None

        names.append(str(name))
        urls.append(url if isinstance(url, str) else "")
        node_ids.append(node_id)
        metadata.append(
            {
                "index": index,
                "name": str(name),
                "url": url if isinstance(url, str) else None,
                "node_id": node_id,
            }
        )

    if not names and fallback_count:
        fallback_names, fallback_urls, fallback_node_ids, fallback_metadata = _build_fallback_entries(
            fallback_count,
            context_id,
        )
        names = fallback_names
        urls = fallback_urls
        node_ids = fallback_node_ids
        metadata = fallback_metadata
    elif context_id:
        for entry in metadata:
            entry.setdefault("context_id", context_id)

    return names, urls, node_ids, metadata

def resolve_image_selection(
    image_list,
    names,
    *,
    selection_index=None,
    selection_name=None,
    selection_node_id=None,
    selection_url=None,
    node_ids=None,
    urls=None,
    fallback_to_first=True,
):
    """Resolve a selected image from a list based on various selection criteria."""
    def _valid_index(index, items):
        return isinstance(index, int) and 0 <= index < len(items)

    def _resolve_by_index(index):
        resolved_name = names[index] if index < len(names) else selection_name
        return image_list[index], index, resolved_name

    if _valid_index(selection_index, image_list):
        return _resolve_by_index(selection_index)

    if selection_node_id and node_ids:
        if selection_node_id in node_ids:
            idx = node_ids.index(selection_node_id)
            if _valid_index(idx, image_list):
                return _resolve_by_index(idx)

    if selection_url and urls:
        if selection_url in urls:
            idx = urls.index(selection_url)
            if _valid_index(idx, image_list):
                return _resolve_by_index(idx)

    if selection_name and selection_name in names:
        idx = names.index(selection_name)
        if _valid_index(idx, image_list):
            return _resolve_by_index(idx)

    if fallback_to_first and len(image_list) > 0:
        return _resolve_by_index(0)

    return None, None, selection_name
# endregion

# region session.py functions (simplified for testing)
class TempFileCache:
    def __init__(self):
        pass

def get_comfy_dir(folder_type):
    """Mock implementation for testing."""
    return f"/mock/comfy/{folder_type}"

def resolve_filepath(filename_prefix, image=None, temp_cache=None):
    """Mock implementation for testing."""
    filename = f"{filename_prefix}_001.png"
    return f"/mock/temp/{filename}", "", filename

def get_resource_url(subfolder, filename, temp_type):
    """Mock implementation for testing."""
    return f"/view?filename={filename}&type={temp_type}&subfolder={subfolder}"

def create_masonry_node(filename, url, index):
    """Mock implementation for testing."""
    return {
        "id": f"node_{index}",
        "cells": {
            "lfImage": {
                "lfValue": url,
                "value": url,
                "htmlProps": {
                    "title": filename,
                    "id": f"img_{index}"
                }
            }
        }
    }

def tensor_to_pil(tensor):
    """Mock implementation for testing."""
    class MockPILImage:
        def save(self, path, format=None):
            pass
    return MockPILImage()

def normalize_output_image(images):
    """Mock implementation for testing."""
    return images, list(images)

def pil_to_tensor(pil_image):
    """Mock implementation for testing."""
    return "mock_tensor"

class EditingSession:
    def __init__(self, node_id):
        self.node_id = node_id
        self.temp_cache = TempFileCache()

    def _build_context_path(self):
        """Builds a unique context path for the editing session."""
        import uuid
        unique_suffix = uuid.uuid4().hex
        return os.path.join(
            get_comfy_dir("temp"),
            f"{self.node_id}_{unique_suffix}_edit_dataset.json",
        )

    def build_dataset(self, images, *, filename_prefix, temp_type="temp"):
        """Builds a dataset from images."""
        nodes = []
        dataset = {"nodes": nodes}

        for index, img in enumerate(images):
            pil_image = tensor_to_pil(img)
            output_file, subfolder, filename = resolve_filepath(
                filename_prefix=filename_prefix,
                image=img,
                temp_cache=self.temp_cache,
            )
            pil_image.save(output_file, format="PNG")
            url = get_resource_url(subfolder, filename, temp_type)
            nodes.append(create_masonry_node(filename, url, index))

        dataset["context_id"] = self._build_context_path()
        dataset.setdefault("columns", []).extend(
            (
                {"id": "path", "title": dataset["context_id"]},
                {"id": "status", "title": "pending"},
            )
        )
        return dataset

    def register_context(self, dataset, **context):
        """Registers editing context and writes dataset."""
        register_editing_context(dataset["context_id"], **context)
        self._write_dataset(dataset)

    def _write_dataset(self, dataset):
        """Writes dataset to JSON file."""
        with open(dataset["context_id"], "w", encoding="utf-8") as json_file:
            json.dump(dataset, json_file, ensure_ascii=False, indent=4)

    def cleanup(self, dataset):
        """Cleans up editing context."""
        clear_editing_context(dataset.get("context_id"))

    def collect_results(self, dataset):
        """Collects results from completed editing session."""
        edited_images = []
        selected_entry = self._resolve_selected_entry(dataset)

        for node in dataset.get("nodes", []):
            lf_image = node.get("cells", {}).get("lfImage") or {}
            image_url = lf_image.get("lfValue") or lf_image.get("value")
            if not image_url:
                continue

            try:
                image_path = self._resolve_image_path(image_url)
                pil_image = self._load_pil(image_path)
            except (FileNotFoundError, OSError):
                continue

            edited_images.append(pil_to_tensor(pil_image))

        batch_list, image_list = self._to_normalized_lists(edited_images)
        return {
            "dataset": dataset,
            "batch_list": batch_list,
            "image_list": image_list,
            "selected_entry": selected_entry,
        }

    def _load_pil(self, path):
        """Loads PIL image from path."""
        from PIL import Image
        with Image.open(path) as img:
            return img.convert("RGB").copy()

    def _resolve_image_path(self, url):
        """Resolves image path from URL."""
        from urllib.parse import parse_qs, urlparse
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)

        filename = query_params.get("filename", [None])[0]
        file_type = query_params.get("type", [None])[0]
        subfolder = query_params.get("subfolder", [None])[0]

        return os.path.join(get_comfy_dir(file_type), subfolder or "", filename)

    def _resolve_selected_entry(self, dataset):
        """Resolves selected entry from dataset."""
        columns = dataset.get("columns", [])
        for column in columns:
            if column.get("id") == "selected" and isinstance(column.get("title"), dict):
                return column["title"]
        return None

    def _to_normalized_lists(self, images):
        """Converts images to normalized lists."""
        if not images:
            return [], []
        batch_list, image_list = normalize_output_image(images)
        return list(batch_list), list(image_list)
# endregion

class TestEditingHelpers(unittest.TestCase):
    """Test suite for editing helper functions."""

    def setUp(self):
        """Set up test fixtures."""
        # Clear global state between tests
        global _EDITING_CONTEXTS
        _EDITING_CONTEXTS.clear()

    # region Context tests
    def test_register_editing_context_valid(self):
        """Test register_editing_context with valid identifier."""
        register_editing_context("test_id", model="test_model", sampler="test_sampler")
        self.assertEqual(get_editing_context("test_id"), {"model": "test_model", "sampler": "test_sampler"})

    def test_register_editing_context_empty_identifier(self):
        """Test register_editing_context with empty identifier."""
        register_editing_context("", model="test")
        self.assertIsNone(get_editing_context(""))

    def test_register_editing_context_none_identifier(self):
        """Test register_editing_context with None identifier."""
        register_editing_context(None, model="test")
        self.assertIsNone(get_editing_context(None))

    def test_get_editing_context_existing(self):
        """Test get_editing_context with existing identifier."""
        register_editing_context("test_id", value="test")
        self.assertEqual(get_editing_context("test_id"), {"value": "test"})

    def test_get_editing_context_nonexistent(self):
        """Test get_editing_context with nonexistent identifier."""
        self.assertIsNone(get_editing_context("nonexistent"))

    def test_get_editing_context_empty_identifier(self):
        """Test get_editing_context with empty identifier."""
        self.assertIsNone(get_editing_context(""))

    def test_clear_editing_context_existing(self):
        """Test clear_editing_context with existing identifier."""
        register_editing_context("test_id", value="test")
        self.assertIsNotNone(get_editing_context("test_id"))
        clear_editing_context("test_id")
        self.assertIsNone(get_editing_context("test_id"))

    def test_clear_editing_context_nonexistent(self):
        """Test clear_editing_context with nonexistent identifier."""
        # Should not raise an error
        clear_editing_context("nonexistent")

    def test_clear_editing_context_empty_identifier(self):
        """Test clear_editing_context with empty identifier."""
        clear_editing_context("")
        # Should not raise an error
    # endregion

    # region Dataset helper tests
    def test_as_dict_dict_input(self):
        """Test _as_dict with dictionary input."""
        input_dict = {"key": "value"}
        self.assertEqual(_as_dict(input_dict), input_dict)

    def test_as_dict_non_dict_input(self):
        """Test _as_dict with non-dictionary input."""
        self.assertEqual(_as_dict("string"), {})
        self.assertEqual(_as_dict(123), {})
        self.assertEqual(_as_dict(None), {})

    def test_build_fallback_entries_basic(self):
        """Test _build_fallback_entries with basic parameters."""
        names, urls, node_ids, metadata = _build_fallback_entries(3)
        self.assertEqual(names, ["Image 1", "Image 2", "Image 3"])
        self.assertEqual(urls, ["", "", ""])
        self.assertEqual(node_ids, [None, None, None])
        self.assertEqual(len(metadata), 3)
        self.assertEqual(metadata[0]["name"], "Image 1")
        self.assertEqual(metadata[0]["index"], 0)

    def test_build_fallback_entries_with_context_id(self):
        """Test _build_fallback_entries with context_id."""
        names, urls, node_ids, metadata = _build_fallback_entries(2, "test_context")
        self.assertEqual(metadata[0]["context_id"], "test_context")
        self.assertEqual(metadata[1]["context_id"], "test_context")
    # endregion

    # region Dataset context tests
    def test_ensure_dataset_context_none_dataset(self):
        """Test ensure_dataset_context with None dataset."""
        result = ensure_dataset_context(None, "fallback")
        self.assertEqual(result, "fallback")

    def test_ensure_dataset_context_non_dict_dataset(self):
        """Test ensure_dataset_context with non-dict dataset."""
        result = ensure_dataset_context("string", "fallback")
        self.assertEqual(result, "fallback")

    def test_ensure_dataset_context_with_context_id(self):
        """Test ensure_dataset_context with existing context_id."""
        dataset = {"context_id": "existing"}
        result = ensure_dataset_context(dataset, "fallback")
        self.assertEqual(result, "existing")
        self.assertEqual(dataset["context_id"], "existing")

    def test_ensure_dataset_context_fallback(self):
        """Test ensure_dataset_context using fallback."""
        dataset = {}
        result = ensure_dataset_context(dataset, "fallback")
        self.assertEqual(result, "fallback")
        self.assertEqual(dataset["context_id"], "fallback")

    def test_ensure_dataset_context_with_selection(self):
        """Test ensure_dataset_context with selection context."""
        dataset = {
            "selection": {"context_id": "selection_context"}
        }
        result = ensure_dataset_context(dataset, "fallback")
        self.assertEqual(result, "selection_context")
        self.assertEqual(dataset["context_id"], "selection_context")
        self.assertEqual(dataset["selection"]["context_id"], "selection_context")
    # endregion

    # region Dataset extraction tests
    def test_extract_dataset_entries_none_dataset(self):
        """Test extract_dataset_entries with None dataset."""
        names, urls, node_ids, metadata = extract_dataset_entries(None, 2)
        self.assertEqual(names, ["Image 1", "Image 2"])
        self.assertEqual(urls, ["", ""])
        self.assertEqual(node_ids, [None, None])

    def test_extract_dataset_entries_empty_dataset(self):
        """Test extract_dataset_entries with empty dataset."""
        names, urls, node_ids, metadata = extract_dataset_entries({})
        self.assertEqual(names, [])
        self.assertEqual(urls, [])
        self.assertEqual(node_ids, [])

    def test_extract_dataset_entries_valid_dataset(self):
        """Test extract_dataset_entries with valid dataset."""
        dataset = {
            "nodes": [
                {
                    "id": "node1",
                    "cells": {
                        "lfImage": {
                            "lfValue": "http://example.com/image1.png",
                            "htmlProps": {
                                "title": "Test Image 1"
                            }
                        }
                    }
                },
                {
                    "id": "node2",
                    "cells": {
                        "lfImage": {
                            "value": "http://example.com/image2.png",
                            "htmlProps": {
                                "id": "img2"
                            }
                        }
                    }
                }
            ]
        }
        names, urls, node_ids, metadata = extract_dataset_entries(dataset)
        self.assertEqual(names, ["Test Image 1", "img2"])
        self.assertEqual(urls, ["http://example.com/image1.png", "http://example.com/image2.png"])
        self.assertEqual(node_ids, ["node1", "node2"])

    def test_extract_dataset_entries_with_context_id(self):
        """Test extract_dataset_entries with context_id."""
        dataset = {
            "nodes": [
                {
                    "cells": {
                        "lfImage": {
                            "lfValue": "http://example.com/image.png"
                        }
                    }
                }
            ]
        }
        names, urls, node_ids, metadata = extract_dataset_entries(dataset, context_id="test_context")
        self.assertEqual(metadata[0]["context_id"], "test_context")
    # endregion

    # region Image selection tests
    def test_resolve_image_selection_by_index(self):
        """Test resolve_image_selection by index."""
        images = ["img1", "img2", "img3"]
        names = ["Image 1", "Image 2", "Image 3"]
        result, index, name = resolve_image_selection(images, names, selection_index=1)
        self.assertEqual(result, "img2")
        self.assertEqual(index, 1)
        self.assertEqual(name, "Image 2")

    def test_resolve_image_selection_by_name(self):
        """Test resolve_image_selection by name."""
        images = ["img1", "img2", "img3"]
        names = ["Image 1", "Image 2", "Image 3"]
        result, index, name = resolve_image_selection(images, names, selection_name="Image 2")
        self.assertEqual(result, "img2")
        self.assertEqual(index, 1)
        self.assertEqual(name, "Image 2")

    def test_resolve_image_selection_by_node_id(self):
        """Test resolve_image_selection by node_id."""
        images = ["img1", "img2", "img3"]
        names = ["Image 1", "Image 2", "Image 3"]
        node_ids = ["node1", "node2", "node3"]
        result, index, name = resolve_image_selection(
            images, names, selection_node_id="node2", node_ids=node_ids
        )
        self.assertEqual(result, "img2")
        self.assertEqual(index, 1)

    def test_resolve_image_selection_by_url(self):
        """Test resolve_image_selection by URL."""
        images = ["img1", "img2", "img3"]
        names = ["Image 1", "Image 2", "Image 3"]
        urls = ["url1", "url2", "url3"]
        result, index, name = resolve_image_selection(
            images, names, selection_url="url2", urls=urls
        )
        self.assertEqual(result, "img2")
        self.assertEqual(index, 1)

    def test_resolve_image_selection_fallback_to_first(self):
        """Test resolve_image_selection fallback to first."""
        images = ["img1", "img2", "img3"]
        names = ["Image 1", "Image 2", "Image 3"]
        result, index, name = resolve_image_selection(images, names)
        self.assertEqual(result, "img1")
        self.assertEqual(index, 0)

    def test_resolve_image_selection_no_fallback(self):
        """Test resolve_image_selection with no fallback."""
        images = ["img1", "img2", "img3"]
        names = ["Image 1", "Image 2", "Image 3"]
        result, index, name = resolve_image_selection(
            images, names, selection_name="nonexistent", fallback_to_first=False
        )
        self.assertIsNone(result)
        self.assertIsNone(index)
        self.assertEqual(name, "nonexistent")

    def test_resolve_image_selection_invalid_index(self):
        """Test resolve_image_selection with invalid index."""
        images = ["img1", "img2"]
        names = ["Image 1", "Image 2"]
        result, index, name = resolve_image_selection(images, names, selection_index=5)
        self.assertEqual(result, "img1")  # Falls back to first
        self.assertEqual(index, 0)
    # endregion

    # region EditingSession tests
    def test_editing_session_build_dataset(self):
        """Test EditingSession.build_dataset."""
        session = EditingSession("test_node")
        images = ["mock_img1", "mock_img2"]

        with patch('uuid.uuid4') as mock_uuid:
            mock_uuid_instance = MagicMock()
            mock_uuid_instance.hex = "mock_hex"
            mock_uuid.return_value = mock_uuid_instance
            dataset = session.build_dataset(images, filename_prefix="test")

        self.assertIn("nodes", dataset)
        self.assertIn("context_id", dataset)
        self.assertIn("columns", dataset)
        self.assertEqual(len(dataset["nodes"]), 2)

    def test_editing_session_register_context(self):
        """Test EditingSession.register_context."""
        session = EditingSession("test_node")
        dataset = {"context_id": "test_context"}

        with patch('builtins.open', mock_open()) as mock_file:
            session.register_context(dataset, model="test_model")

        # Check that context was registered
        context = get_editing_context("test_context")
        self.assertEqual(context, {"model": "test_model"})

    def test_editing_session_cleanup(self):
        """Test EditingSession.cleanup."""
        session = EditingSession("test_node")
        dataset = {"context_id": "test_context"}
        register_editing_context("test_context", value="test")

        session.cleanup(dataset)
        self.assertIsNone(get_editing_context("test_context"))

    def test_editing_session_collect_results(self):
        """Test EditingSession.collect_results."""
        session = EditingSession("test_node")
        dataset = {
            "nodes": [
                {
                    "cells": {
                        "lfImage": {
                            "lfValue": "/view?filename=test.png&type=temp&subfolder="
                        }
                    }
                }
            ],
            "columns": []
        }

        with patch('builtins.open', mock_open(read_data='{"RGB": true}')) as mock_file, \
             patch('PIL.Image.open') as mock_pil_open:
            mock_image = MagicMock()
            mock_image.convert.return_value.copy.return_value = mock_image
            mock_pil_open.return_value.__enter__.return_value = mock_image

            result = session.collect_results(dataset)

        self.assertIn("dataset", result)
        self.assertIn("batch_list", result)
        self.assertIn("image_list", result)
        self.assertIn("selected_entry", result)

    def test_editing_session_resolve_selected_entry(self):
        """Test EditingSession._resolve_selected_entry."""
        session = EditingSession("test_node")
        dataset = {
            "columns": [
                {"id": "path", "title": "test"},
                {"id": "selected", "title": {"name": "selected_image"}},
                {"id": "status", "title": "completed"}
            ]
        }

        selected = session._resolve_selected_entry(dataset)
        self.assertEqual(selected, {"name": "selected_image"})

    def test_editing_session_resolve_selected_entry_no_selection(self):
        """Test EditingSession._resolve_selected_entry with no selection."""
        session = EditingSession("test_node")
        dataset = {"columns": [{"id": "path", "title": "test"}]}

        selected = session._resolve_selected_entry(dataset)
        self.assertIsNone(selected)
    # endregion

if __name__ == '__main__':
    unittest.main()