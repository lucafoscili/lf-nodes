"""What the Titanic specimen tests share: the canonical graph's widget values, its stock masks and named values in UI.

Each ``test_titanic_*_fixture.py`` runs a case's checked-in settings through the real CPU nodes offline and asserts
the named values its live case asserts in history.
"""
import copy
import importlib.util
import json
from pathlib import Path

import numpy as np
from PIL import Image
import torch

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = json.loads((ROOT / "scripts/quality/fixtures/E2E.json").read_text(encoding="utf-8"))
MANIFEST = json.loads((ROOT / "scripts/quality/titanic_cases.json").read_text(encoding="utf-8"))
STOCK_EXAMPLE = ROOT / "scripts/quality/fixtures/titanic-sam3/comfy-example.png"


def generator(name):
    """An ``update_titanic_*_coverage.py`` script loaded as a module (its CASE or CASES)."""
    path = ROOT / f"scripts/quality/update_titanic_{name}_coverage.py"
    spec = importlib.util.spec_from_file_location(f"titanic_{name}_fixture_generator", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def case(identifier):
    return next(item for item in MANIFEST["coverageCases"] if item["id"] == identifier)


def widgets(identifier, drop=("ui_widget",)):
    """A node's serialized widget values as the list inputs Comfy hands an ``on_exec``."""
    named = copy.deepcopy(next(n for n in WORKFLOW["nodes"] if n["id"] == identifier)["widgets_values_named"])
    for name in drop:
        named.pop(name, None)
    return {name: [value] for name, value in named.items()}


def single(controls):
    """``widgets`` for a node without INPUT_IS_LIST: each value itself."""
    return {name: values[0] for name, values in controls.items()}


def stock_example():
    pixels = np.asarray(Image.open(STOCK_EXAMPLE).convert("RGB"))
    return torch.from_numpy(pixels.astype(np.float32) / 255)[None]


def solid(identifier):
    controls = widgets(identifier)
    return torch.full((controls["height"][0], controls["width"][0]), float(controls["value"][0]))


def placed(destination, source, identifier):
    """Core MaskComposite ``add`` of two SolidMask nodes, from their serialized widgets."""
    controls = widgets(identifier)
    x, y = controls["x"][0], controls["y"][0]
    result = solid(destination).clone()
    piece = solid(source)
    result[y:y + piece.shape[0], x:x + piece.shape[1]] = (result[y:y + piece.shape[0], x:x + piece.shape[1]]
                                                          + piece).clamp(0, 1)
    return result[None]


def named_values(value, name):
    found = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key == name:
                found.append(item)
            found.extend(named_values(item, name))
    elif isinstance(value, list):
        for item in value:
            found.extend(named_values(item, name))
    return found


def assert_named_values(manifest_case, outputs):
    """Every ``requiredNamedValues`` entry found in its node's UI, as Titanic finds it in history."""
    for node_id, expectation in manifest_case["expect"].items():
        if node_id not in outputs:
            continue
        ui = outputs[node_id]["ui"]
        for name, expected in expectation.get("requiredNamedValues", {}).items():
            # JSON numbers compare by value (Titanic's Object.is on parsed history); booleans stay booleans.
            assert any(value == expected and isinstance(value, bool) == isinstance(expected, bool)
                       for value in named_values(ui, name)), (node_id, name, expected)
