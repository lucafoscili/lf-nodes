"""Isolated event-routing contract for progressive compare previews."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType
import sys
import uuid

import torch


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "modules" / "utils" / "helpers" / "ui" / "progressive_preview.py"


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


def test_progressive_preview_uses_unprefixed_safe_sender_and_scalar_node_id() -> None:
    prefix = f"_lf_progressive_event_{uuid.uuid4().hex}"
    _package(prefix)
    _package(f"{prefix}.utils")
    _package(f"{prefix}.utils.helpers")
    _package(f"{prefix}.utils.helpers.ui")

    def create_compare_node(before, after, index, **_kwargs):
        return {
            "id": str(index),
            "cells": {
                "lfImage": {"lfValue": before},
                "lfImage_after": {"lfValue": after},
            },
        }

    _module(
        f"{prefix}.utils.helpers.ui.create_compare_node",
        create_compare_node=create_compare_node,
    )
    _module(
        f"{prefix}.utils.helpers.api",
        get_resource_url=lambda *_args, **_kwargs: "/view",
    )
    _module(
        f"{prefix}.utils.helpers.conversion",
        tensor_to_pil=lambda _tensor: None,
    )

    sent = []

    def normalize_node_id(value):
        while isinstance(value, (list, tuple)):
            value = value[0] if value else None
        return value

    def safe_send_sync(event, payload, node_id=None):
        sent.append((event, payload, node_id))

    _package(f"{prefix}.utils.helpers.comfy")
    _module(
        f"{prefix}.utils.helpers.comfy.safe_send_sync",
        normalize_node_id=normalize_node_id,
        safe_send_sync=safe_send_sync,
    )

    module_name = f"{prefix}.utils.helpers.ui.progressive_preview"
    spec = importlib.util.spec_from_file_location(module_name, SOURCE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    _attach(module_name, module)
    spec.loader.exec_module(module)

    module.prepare_preview_destination = lambda *_args, **_kwargs: {
        "file": "preview.png",
        "subfolder": "",
        "filename": "preview.png",
    }
    module.save_preview_image = lambda *_args, **_kwargs: "/view?type=temp"

    dataset = {"nodes": []}
    stream = module.ComparePreviewStream(
        node_id=[["node-42"]],
        index=0,
        input_image=torch.zeros((1, 2, 2, 3)),
        dataset=dataset,
        compare_nodes=dataset["nodes"],
        event="tiledsuperres",
        input_target_size=(2, 2),
        resolve_filepath=lambda **_kwargs: ("preview.png", "", "preview.png"),
    )
    stream.update_compare("/view?type=input")
    stream.emit()

    assert stream.node_id == "node-42"
    assert sent == [("tiledsuperres", {"dataset": dataset}, "node-42")]
