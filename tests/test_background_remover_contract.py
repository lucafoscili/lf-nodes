"""Isolated contract test for LF_BackgroundRemover batch/list outputs."""

from __future__ import annotations

import importlib.util
from contextlib import contextmanager
from pathlib import Path
from types import ModuleType
import sys
import uuid

import torch
import pytest


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
        groups = {}
        for image in images:
            groups.setdefault(tuple(image.shape[1:]), []).append(image)
        return [torch.cat(items, dim=0) for items in groups.values()], list(images)

    def normalize_output_mask(masks):
        return normalize_output_image(masks)

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

    sessions = []
    effect_calls = []
    remover = object()

    @contextmanager
    def session(model):
        sessions.append(("open", model))
        try:
            yield remover
        finally:
            sessions.append(("close", model))

    def apply_filter(image, **settings):
        assert settings.pop("remover") is remover
        effect_calls.append(settings)
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
        background_removal_session=session,
        background_remover_effect=apply_filter,
    )

    module_name = f"{prefix}.nodes.filters.background_remover"
    spec = importlib.util.spec_from_file_location(module_name, SOURCE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    _attach(module_name, module)
    spec.loader.exec_module(module)
    module.session_events = sessions
    module.effect_calls = effect_calls
    return module, sent, Input


@pytest.mark.parametrize("model", ["u2net", "RMBG-2.0"])
def test_background_remover_preserves_published_outputs_and_appends_cutout_batch(model) -> None:
    module, sent, Input = _load_node()
    first = torch.full((4, 5, 3), 0.2)
    second = torch.full((4, 5, 3), 0.6)
    image_batch = torch.stack((first, second))

    response = module.LF_BackgroundRemover().on_exec(
        image=[image_batch],
        transparent_background=[True],
        background_color=["#000000"],
        model=[model],
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
    assert module.session_events == [("open", model), ("close", model)]
    assert len(module.effect_calls) == 2
    assert all(call == {
        "transparent_background": True,
        "background_color": "#000000",
        "model_name": model,
    } for call in module.effect_calls)

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


def test_background_remover_only_appends_model_choice_to_published_schema():
    module, _, Input = _load_node()
    schema = module.LF_BackgroundRemover.INPUT_TYPES()
    assert list(schema["required"]) == ["image", "transparent_background", "background_color", "model"]
    assert schema["required"]["image"][0] == Input.IMAGE
    assert schema["required"]["transparent_background"][0] == Input.BOOLEAN
    assert schema["required"]["transparent_background"][1]["default"] is True
    assert schema["required"]["background_color"][0] == Input.STRING
    assert schema["required"]["background_color"][1]["default"] == "#000000"
    assert schema["required"]["model"][0] == [
        "u2net", "u2netp", "u2net_human_seg", "silueta", "isnet-general-use", "isnet-anime", "RMBG-2.0",
    ]
    assert schema["required"]["model"][1]["default"] == "u2net"
    assert schema["optional"] == {"ui_widget": (Input.LF_COMPARE, {"default": {}})}
    assert schema["hidden"] == {"node_id": "UNIQUE_ID"}
    assert module.LF_BackgroundRemover.INPUT_IS_LIST is True


def test_rmbg2_keeps_mixed_sizes_in_order_with_one_model_session():
    module, sent, _ = _load_node()
    images = [torch.full((1, height, width, 3), value) for height, width, value in (
        (4, 5, 0.2), (7, 3, 0.6), (4, 5, 0.8),
    )]
    result = module.LF_BackgroundRemover().on_exec(image=images, model=["RMBG-2.0"])["result"]
    assert result[0].shape == (2, 4, 5, 3)
    assert [tuple(item.shape) for item in result[2]] == [(1, 4, 5, 4), (1, 7, 3, 4), (1, 4, 5, 4)]
    assert [row["marker"] for row in result[5]["runs"]] == pytest.approx([0.2, 0.6, 0.8])
    assert result[3].shape == (2, 4, 5)
    assert [tuple(item.shape) for item in result[4]] == [(1, 4, 5), (1, 7, 3), (1, 4, 5)]
    assert result[6].shape == (2, 4, 5, 4)
    assert module.session_events == [("open", "RMBG-2.0"), ("close", "RMBG-2.0")]
    assert len(sent) == 1


def test_rmbg2_releases_session_when_processing_fails():
    module, sent, _ = _load_node()

    def fail(*args, **kwargs):
        raise RuntimeError("inference failed")

    module.background_remover_effect = fail
    with pytest.raises(RuntimeError, match="inference failed"):
        module.LF_BackgroundRemover().on_exec(image=[torch.zeros(1, 4, 5, 3)], model=["RMBG-2.0"])
    assert module.session_events == [("open", "RMBG-2.0"), ("close", "RMBG-2.0")]
    assert sent == []
