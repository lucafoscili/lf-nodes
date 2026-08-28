"""Isolated contract test for LF_BackgroundRemover batch/list outputs."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType
import sys
import uuid

import torch


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "modules" / "nodes" / "filters" / "background_remover.py"


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


def _load_node():
    prefix = f"_lf_background_contract_{uuid.uuid4().hex}"
    _package(prefix)
    _package(f"{prefix}.nodes")
    filters_package = _package(f"{prefix}.nodes.filters")
    filters_package.CATEGORY = "test"
    _package(f"{prefix}.utils")
    _package(f"{prefix}.utils.helpers")

    class Input:
        IMAGE = "IMAGE"
        MASK = "MASK"
        JSON = "JSON"
        BOOLEAN = "BOOLEAN"
        STRING = "STRING"
        LF_COMPARE = "LF_COMPARE"

    _module(f"{prefix}.utils.constants", FUNCTION="on_exec", Input=Input)

    def normalize_input_image(value):
        if isinstance(value, list):
            source = value
        else:
            source = [value]
        normalized = []
        for image in source:
            normalized.extend(image[index : index + 1] for index in range(image.shape[0]))
        return normalized

    def normalize_list_to_value(value):
        while isinstance(value, (list, tuple)):
            value = value[0] if value else None
        return value

    def normalize_output_image(images):
        return [torch.cat(images, dim=0)], list(images)

    def normalize_output_mask(masks):
        return [torch.cat(masks, dim=0)], list(masks)

    _module(
        f"{prefix}.utils.helpers.logic",
        normalize_input_image=normalize_input_image,
        normalize_list_to_value=normalize_list_to_value,
        normalize_output_image=normalize_output_image,
        normalize_output_mask=normalize_output_mask,
    )

    sent = []
    _module(
        f"{prefix}.utils.helpers.comfy",
        safe_send_sync=lambda event, payload, node_id: sent.append(
            (event, payload, node_id)
        ),
    )

    def compare_node(before, after, index):
        return {
            "id": f"image_{index + 1}",
            "cells": {
                "lfImage": {"lfValue": before},
                "lfImage_after": {"lfValue": after},
            },
        }

    def cached_compare_node(_before, _after, *, index):
        return compare_node(f"input-before-{index}", f"input-after-{index}", index)

    _module(
        f"{prefix}.utils.helpers.ui",
        create_cached_compare_node=cached_compare_node,
        create_compare_node=compare_node,
    )

    def apply_filter(image, _settings):
        alpha = torch.full((*image.shape[:-1], 1), 0.75, dtype=image.dtype)
        cutout = torch.cat((image, alpha), dim=-1)
        mask = alpha[..., 0]
        marker = float(image[0, 0, 0, 0])
        return image + 0.1, {
            "cutout_tensor": cutout,
            "mask_tensor": mask,
            "stats": {"marker": marker},
            "cutout": f"input-cutout-{marker}",
            "mask": f"input-mask-{marker}",
        }

    _module(
        f"{prefix}.utils.filters",
        apply_background_remover_filter=apply_filter,
    )

    module_name = f"{prefix}.nodes.filters.background_remover"
    spec = importlib.util.spec_from_file_location(module_name, SOURCE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    _attach(module_name, module)
    spec.loader.exec_module(module)
    return module, sent, Input


def test_background_remover_preserves_published_outputs_and_appends_cutout_batch() -> None:
    module, sent, Input = _load_node()
    first = torch.full((4, 5, 3), 0.2)
    second = torch.full((4, 5, 3), 0.6)
    image_batch = torch.stack((first, second))

    response = module.LF_BackgroundRemover().on_exec(
        image=[image_batch],
        transparent_background=[True],
        background_color=["#000000"],
        model=["u2net"],
        node_id=["bg-node"],
    )

    assert set(response) == {"ui", "result"}
    result = response["result"]
    assert len(result) == 7
    composite_batch, composite_list, cutout_list, mask_batch, mask_list, stats, cutout_batch = result
    assert composite_batch.shape == (2, 4, 5, 3)
    assert [tuple(image.shape) for image in composite_list] == [
        (1, 4, 5, 3),
        (1, 4, 5, 3),
    ]
    assert [tuple(image.shape) for image in cutout_list] == [
        (1, 4, 5, 4),
        (1, 4, 5, 4),
    ]
    assert cutout_batch.shape == (2, 4, 5, 4)
    assert mask_batch.shape == (2, 4, 5)
    assert [tuple(mask.shape) for mask in mask_list] == [(1, 4, 5), (1, 4, 5)]
    assert [row["index"] for row in stats["runs"]] == [0, 1]
    assert len(sent) == 1
    assert sent[0][0] == "backgroundremover"
    assert response["ui"]["lf_output"][0] is sent[0][1]
    assert len(sent[0][1]["dataset"]["nodes"]) == 4

    assert module.LF_BackgroundRemover.RETURN_TYPES == (
        Input.IMAGE,
        Input.IMAGE,
        Input.IMAGE,
        Input.MASK,
        Input.MASK,
        Input.JSON,
        Input.IMAGE,
    )
    assert module.LF_BackgroundRemover.RETURN_NAMES == (
        "image",
        "image_list",
        "cutout_list",
        "mask",
        "mask_list",
        "stats",
        "cutout",
    )
    assert module.LF_BackgroundRemover.OUTPUT_IS_LIST == (
        False,
        True,
        True,
        False,
        True,
        False,
        False,
    )
