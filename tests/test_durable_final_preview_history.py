"""Focused history contracts for representative final-preview producers.

These tests load the node modules into small synthetic packages.  That keeps
the checks independent of a live ComfyUI server while exercising the actual
``on_exec`` return shape used by Comfy's mapped execution.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from types import ModuleType
import uuid

import pytest
import torch


ROOT = Path(__file__).resolve().parents[1]


def _attach(name: str, module: ModuleType) -> ModuleType:
    sys.modules[name] = module
    if "." in name:
        parent_name, child_name = name.rsplit(".", 1)
        parent = sys.modules.get(parent_name)
        if parent is not None:
            setattr(parent, child_name, module)
    return module


def _package(name: str) -> ModuleType:
    package = ModuleType(name)
    package.__path__ = []
    return _attach(name, package)


def _module(name: str, **attributes) -> ModuleType:
    module = ModuleType(name)
    for key, value in attributes.items():
        setattr(module, key, value)
    return _attach(name, module)


def _normalize_input_image(value):
    source = value if isinstance(value, list) else [value]
    normalized = []
    for image in source:
        if image.ndim == 3:
            image = image.unsqueeze(0)
        normalized.extend(image[index : index + 1] for index in range(image.shape[0]))
    return normalized


def _normalize_list_to_value(value):
    while isinstance(value, (list, tuple)):
        value = value[0] if value else None
    return value


def _normalize_output_image(images):
    return [torch.cat(images, dim=0)], list(images)


def _load_harness():
    prefix = f"_lf_durable_history_{uuid.uuid4().hex}"
    sent = []

    _package(prefix)
    _package(f"{prefix}.nodes")
    node_filters = _package(f"{prefix}.nodes.filters")
    node_filters.CATEGORY = "test/filters"
    node_image = _package(f"{prefix}.nodes.image")
    node_image.CATEGORY = "test/image"
    _package(f"{prefix}.utils")
    _package(f"{prefix}.utils.helpers")

    class Input:
        IMAGE = "IMAGE"
        FLOAT = "FLOAT"
        BOOLEAN = "BOOLEAN"
        LF_COMPARE = "LF_COMPARE"
        LF_MASONRY = "LF_MASONRY"

    _module(f"{prefix}.utils.constants", FUNCTION="on_exec", Input=Input)
    _module(
        f"{prefix}.utils.helpers.logic",
        normalize_input_image=_normalize_input_image,
        normalize_list_to_value=_normalize_list_to_value,
        normalize_output_image=_normalize_output_image,
    )

    def safe_send_sync(event, payload, node_id=None):
        sent.append((event, payload, node_id))

    _module(f"{prefix}.utils.helpers.comfy", safe_send_sync=safe_send_sync)

    def brightness_effect(image, **kwargs):
        return image + float(kwargs["brightness_strength"])

    _module(f"{prefix}.utils.filters", brightness_effect=brightness_effect)

    def process_and_save_image(images, filter_function, filter_args, nodes):
        processed = []
        for index, image in enumerate(images):
            output = filter_function(image, **filter_args)
            nodes.append({"id": f"image_{index + 1}"})
            processed.append(output)
        return processed

    _module(
        f"{prefix}.utils.helpers.torch.process_and_save_image",
        process_and_save_image=process_and_save_image,
    )

    def create_cached_masonry_node(image, *, index, label):
        return {"id": index, "label": label, "marker": float(image[0, 0, 0, 0])}

    _module(
        f"{prefix}.utils.helpers.ui",
        create_cached_masonry_node=create_cached_masonry_node,
    )

    def load_node(relative_path: str, module_suffix: str) -> ModuleType:
        module_name = f"{prefix}.{module_suffix}"
        spec = importlib.util.spec_from_file_location(
            module_name,
            ROOT / relative_path,
        )
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        _attach(module_name, module)
        spec.loader.exec_module(module)
        return module

    brightness = load_node(
        "modules/nodes/filters/brightness.py",
        "nodes.filters.brightness",
    )
    view_images = load_node(
        "modules/nodes/image/view_images.py",
        "nodes.image.view_images",
    )
    return brightness, view_images, sent


def test_shared_filter_history_reuses_event_payload_and_result_tuple() -> None:
    brightness, _view_images, sent = _load_harness()
    image = torch.full((2, 2, 3, 3), 0.25, dtype=torch.float32)

    response = brightness.LF_Brightness().on_exec(
        image=[image],
        brightness_strength=[0.1],
        gamma=[1.0],
        midpoint=[0.5],
        localized_brightness=[False],
        node_id=["brightness-node"],
    )

    assert set(response) == {"ui", "result"}
    assert response["ui"]["lf_output"][0] is sent[0][1]
    assert sent[0] == ("brightness", response["ui"]["lf_output"][0], ["brightness-node"])

    result = response["result"]
    assert isinstance(result, tuple)
    assert len(result) == 2
    assert tuple(result[0].shape) == (2, 2, 3, 3)
    assert len(result[1]) == 2
    assert [float(item[0, 0, 0, 0]) for item in result[1]] == pytest.approx([0.35, 0.35])
    assert len(response["ui"]["lf_output"][0]["dataset"]["nodes"]) == 2


def test_direct_view_history_reuses_event_payload_and_result_tuple() -> None:
    _brightness, view_images, sent = _load_harness()
    image = torch.stack(
        (
            torch.full((2, 3, 3), 0.2, dtype=torch.float32),
            torch.full((2, 3, 3), 0.7, dtype=torch.float32),
        )
    )

    response = view_images.LF_ViewImages().on_exec(
        image=[image],
        node_id="view-node",
    )

    assert set(response) == {"ui", "result"}
    assert response["ui"]["lf_output"][0] is sent[0][1]
    assert sent[0] == ("viewimages", response["ui"]["lf_output"][0], "view-node")

    result = response["result"]
    assert isinstance(result, tuple)
    assert len(result) == 2
    assert tuple(result[0].shape) == (2, 2, 3, 3)
    assert [tuple(item.shape) for item in result[1]] == [(1, 2, 3, 3)] * 2
    assert [float(item[0, 0, 0, 0]) for item in result[1]] == pytest.approx([0.2, 0.7])
    assert len(response["ui"]["lf_output"][0]["dataset"]["nodes"]) == 2
