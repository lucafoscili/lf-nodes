"""Execute the Titanic stored-value PNG specimen's settings through the real CPU nodes.

The live case asserts named values in each node's history; this proves offline
that the pinned stock example and the checked-in widget values produce them, and
that the 16-bit file holds the example's values exactly.
"""
from pathlib import Path

import numpy as np
from PIL import Image
import pytest

from modules.nodes.io import load_png, save_png
from modules.tests import titanic_specimen as titanic
from modules.utils import stored_png
from modules.utils.helpers.ui import generated_preview

ROOT = titanic.ROOT


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
    return titanic.widgets(identifier, drop=("ui_widget", "upload", "image"))


def test_specimen_settings_produce_the_case_expectations(comfy_dirs):
    case = titanic.case("cpu.png-stored-values")
    assert case == titanic.generator("png").CASE
    source = next(n for n in titanic.WORKFLOW["nodes"] if n["id"] == 667)["widgets_values_named"]["image"]
    outputs = {"667": load_png.LF_LoadPNG().on_exec(image=str(ROOT / source))}
    image = outputs["667"]["result"][0]
    outputs["668"] = save_png.LF_SavePNG().on_exec(image=[image], **widgets(668))
    titanic.assert_named_values(case, outputs)
    written, header = stored_png.read_png((comfy_dirs / "output" / outputs["668"]["result"][0][0]).read_bytes())
    assert header["bit_depth"] == 16
    original = np.asarray(Image.open(ROOT / source).convert("RGB")).astype(np.uint16)
    np.testing.assert_array_equal(written, original * 257)  # v / 255 is exactly (257 v) / 65535
