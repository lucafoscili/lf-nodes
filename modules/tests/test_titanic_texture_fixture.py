"""Execute the Titanic texture specimen's settings through the real CPU nodes.

The live case asserts named values in each node's history; this proves offline
that the pinned stock example and the checked-in widget values produce them.
"""
import copy
import importlib.util
import json
from pathlib import Path

import numpy as np
from PIL import Image
import pytest
import torch

from modules.nodes.texture.detail_transfer import LF_DetailTransfer
from modules.nodes.texture.edge_padding import LF_EdgePadding
from modules.nodes.texture.masked_lab_grade import LF_MaskedLabGrade
from modules.nodes.texture.normal_map_repack import LF_NormalMapRepack
from modules.utils.helpers.ui import generated_preview

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = json.loads((ROOT / "scripts/quality/fixtures/E2E.json").read_text(encoding="utf-8"))
MANIFEST = json.loads((ROOT / "scripts/quality/titanic_cases.json").read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def preview_root(monkeypatch, tmp_path):
    monkeypatch.setattr(generated_preview, "get_comfy_dir", lambda _kind: str(tmp_path / "input"))
    from modules.nodes.texture import detail_transfer, edge_padding, masked_lab_grade, normal_map_repack
    for module in (detail_transfer, edge_padding, masked_lab_grade, normal_map_repack):
        monkeypatch.setattr(module, "safe_send_sync", lambda *_args: None)


def widgets(identifier):
    named = copy.deepcopy(next(n for n in WORKFLOW["nodes"] if n["id"] == identifier)["widgets_values_named"])
    named.pop("ui_widget", None)
    return {name: [value] for name, value in named.items()}


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


def test_specimen_settings_produce_the_case_expectations():
    generator = ROOT / "scripts/quality/update_titanic_texture_coverage.py"
    spec = importlib.util.spec_from_file_location("titanic_texture_fixture_generator", generator)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    case = next(item for item in MANIFEST["coverageCases"] if item["id"] == "cpu.texture-tools")
    assert case == module.CASE
    pixels = np.asarray(Image.open(ROOT / "scripts/quality/fixtures/titanic-sam3/comfy-example.png").convert("RGB"))
    example = torch.from_numpy(pixels.astype(np.float32) / 255)[None]
    square, band = placed(655, 656, 657), placed(655, 658, 659)
    outputs = {}
    outputs["660"] = LF_MaskedLabGrade().on_exec(image=[example], mask=[square], reference_image=[example],
                                                 reference_mask=[band], **widgets(660))
    graded = outputs["660"]["result"][0]
    outputs["661"] = LF_DetailTransfer().on_exec(image=[graded], detail_source=[example], mask=[square],
                                                 reference_image=[example], reference_mask=[square],
                                                 **widgets(661))
    outputs["662"] = LF_EdgePadding().on_exec(image=[outputs["661"]["result"][0]], mask=[square], **widgets(662))
    normal = widgets(664)
    color = normal["color"][0]
    rgb = [int(color[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    flat = torch.tensor(rgb).expand(1, normal["height"][0], normal["width"][0], 3).clone()
    outputs["665"] = LF_NormalMapRepack().on_exec(image=[flat], **widgets(665))
    for node_id, expectation in case["expect"].items():
        ui = outputs[node_id]["ui"]
        for name, expected in expectation["requiredNamedValues"].items():
            # JSON numbers compare by value (Titanic's Object.is on parsed history); booleans stay booleans.
            assert any(value == expected and isinstance(value, bool) == isinstance(expected, bool)
                       for value in named_values(ui, name)), (node_id, name, expected)
    # The grade moved the square toward the band, and the detail transfer put fine detail back.
    grade = outputs["660"]["result"][1]["images"][0]
    # sRGB clipping keeps the darkest blues short of the band, so the gap closes most of the way, not all.
    before, after = (np.subtract(grade[key]["lab_mean"], grade["reference"]["lab_mean"]) for key in ("target", "result"))
    assert np.linalg.norm(after) < 0.25 * np.linalg.norm(before)
    assert grade["clipped_pixels"] > 0
    detail = outputs["661"]["result"][1]["images"][0]
    assert detail["result_fine_l_std"] == pytest.approx(detail["reference_fine_l_std"], rel=0.1)
    repacked = outputs["665"]["result"][0]
    assert float(repacked[0, 0, 0, 1]) < 0.5 < float(flat[0, 0, 0, 1])
