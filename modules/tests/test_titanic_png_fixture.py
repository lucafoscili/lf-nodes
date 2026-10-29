"""Execute the Titanic stored-value PNG specimen's settings through the real CPU nodes.

The live case asserts named values in each node's history; this proves offline
that the pinned stock example and the checked-in widget values produce them, and
that the 16-bit file holds the example's values exactly.
"""
import copy
import importlib.util
import json
from pathlib import Path

import numpy as np
from PIL import Image
import pytest

from modules.nodes.io import load_png, save_png
from modules.utils import stored_png
from modules.utils.helpers.ui import generated_preview

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = json.loads((ROOT / "scripts/quality/fixtures/E2E.json").read_text(encoding="utf-8"))
MANIFEST = json.loads((ROOT / "scripts/quality/titanic_cases.json").read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def comfy_dirs(monkeypatch, tmp_path):
    monkeypatch.setattr(generated_preview, "get_comfy_dir", lambda _kind: str(tmp_path / "input"))
    monkeypatch.setattr(save_png, "get_comfy_dir", lambda _kind: str(tmp_path / "output"))

    def resolve(filename_prefix, base_output_path, extension, **_kwargs):
        target = Path(base_output_path) / f"{filename_prefix}_00001.{extension}"
        target.parent.mkdir(parents=True, exist_ok=True)
        subfolder, _, filename = f"{filename_prefix}_00001.{extension}".rpartition("/")
        return str(target), subfolder, filename

    monkeypatch.setattr(save_png, "resolve_filepath", resolve)
    for module in (load_png, save_png):
        monkeypatch.setattr(module, "safe_send_sync", lambda *_args: None)
    return tmp_path


def widgets(identifier):
    named = copy.deepcopy(next(n for n in WORKFLOW["nodes"] if n["id"] == identifier)["widgets_values_named"])
    for name in ("ui_widget", "upload", "image"):
        named.pop(name, None)
    return {name: [value] for name, value in named.items()}


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


def test_specimen_settings_produce_the_case_expectations(comfy_dirs):
    generator = ROOT / "scripts/quality/update_titanic_png_coverage.py"
    spec = importlib.util.spec_from_file_location("titanic_png_fixture_generator", generator)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    case = next(item for item in MANIFEST["coverageCases"] if item["id"] == "cpu.png-stored-values")
    assert case == module.CASE
    source = next(n for n in WORKFLOW["nodes"] if n["id"] == 667)["widgets_values_named"]["image"]
    outputs = {"667": load_png.LF_LoadPNG().on_exec(image=str(ROOT / source))}
    image = outputs["667"]["result"][0]
    outputs["668"] = save_png.LF_SavePNG().on_exec(image=[image], **widgets(668))
    for node_id, expectation in case["expect"].items():
        ui = outputs[node_id]["ui"]
        for name, expected in expectation["requiredNamedValues"].items():
            assert any(value == expected and isinstance(value, bool) == isinstance(expected, bool)
                       for value in named_values(ui, name)), (node_id, name, expected)
    written, header = stored_png.read_png((comfy_dirs / "output" / outputs["668"]["result"][0][0]).read_bytes())
    assert header["bit_depth"] == 16
    original = np.asarray(Image.open(ROOT / source).convert("RGB")).astype(np.uint16)
    np.testing.assert_array_equal(written, original * 257)  # v / 255 is exactly (257 v) / 65535
