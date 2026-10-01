"""Execute the checked-in synthetic six-node inputs through real CPU nodes."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import types

from PIL import Image
import torch

from modules.nodes.filters.brightness import LF_Brightness
from modules.nodes.io.apply_texture_to_glb import LF_ApplyTextureToGLB
from modules.nodes.io.scale_glb_nodes import LF_ScaleGLBNodes
from modules.nodes.regions.image_layers import LF_LoadImageLayers, LF_ComposeImageLayers
from modules.nodes.regions.image_regions import LF_ExtractImageRegions, LF_ComposeImageRegions
from modules.utils.glb_texture import read_glb


ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "scripts/quality/fixtures/titanic-cpu"
WORKFLOW = json.loads((ROOT / "scripts/quality/fixtures/E2E.json").read_text(encoding="utf-8"))


def widgets(identifier):
    return copy.deepcopy(next(n for n in WORKFLOW["nodes"] if n["id"] == identifier)["widgets_values_named"])


def base_image():
    controls = widgets(617)
    rgb = [int(controls["color"][i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return torch.tensor(rgb).reshape(1, 1, 1, 3).expand(1, controls["height"], controls["width"], 3).clone()


def test_synthetic_asset_generator_reproduces_every_pinned_input():
    path = ROOT / "scripts/quality/update_titanic_cpu_coverage.py"
    spec = importlib.util.spec_from_file_location("titanic_cpu_fixture_generator", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    manifest = json.loads((ROOT / "scripts/quality/titanic_cases.json").read_text(encoding="utf-8"))
    pins = {Path(row["path"]).name: row["expectedSha256"] for row in manifest["fixtures"]}
    for name, data in module.synthetic_assets().items():
        assert data == (ASSETS / name).read_bytes()
        assert hashlib.sha256(data).hexdigest() == pins[name]


def test_glb_branch_replaces_texture_scales_skin_and_preserves_motion(monkeypatch):
    class File3D:
        def __init__(self, source, file_format):
            self.source, self.format = source, file_format

        def get_bytes(self):
            return self.source.getvalue()

    latest = types.ModuleType("comfy_api.latest")
    latest.Types = types.SimpleNamespace(File3D=File3D)
    monkeypatch.setitem(sys.modules, "comfy_api.latest", latest)
    source = ASSETS / "synthetic.glb"
    original_bytes = source.read_bytes()
    original, binary = read_glb(original_bytes)
    textured, = LF_ApplyTextureToGLB().on_exec([str(source)], [base_image()], [0])
    texture_document, texture_binary = read_glb(textured.get_bytes())
    targets = json.loads(widgets(613)["ui_widget"])
    scaled, = LF_ScaleGLBNodes().on_exec([textured], [targets], [widgets(614)["percent"]])
    document, payload = read_glb(scaled.get_bytes())
    assert document["meshes"] == original["meshes"]
    assert document["animations"] == original["animations"]
    assert payload == texture_binary and payload[:len(binary)] == binary
    assert document["materials"][0]["pbrMetallicRoughness"]["baseColorTexture"]["index"] == 1
    assert document["nodes"][-1]["scale"] == [.75] * 3
    assert document["skins"][0]["joints"] == [4, 2]
    view = texture_document["bufferViews"][-1]
    from io import BytesIO
    with Image.open(BytesIO(texture_binary[view["byteOffset"]:view["byteOffset"] + view["byteLength"]])) as image:
        assert image.mode == "RGB" and image.size == (64, 48)
    assert source.read_bytes() == original_bytes


def test_region_and_combined_layer_branches_edit_pixels_keep_alpha_and_reduce_coverage():
    base = base_image()
    regions = json.loads(widgets(616)["ui_widget"])
    batch, images, layout, config = LF_ExtractImageRegions().on_exec([base], [regions], [32])
    assert [row["id"] for row in config["image_entries"]] == ["left", "right"]
    edits = LF_Brightness().on_exec(image=batch, **widgets(619))["result"][1]
    composed, _ = LF_ComposeImageRegions().on_exec([base], edits, images, [layout])
    assert not torch.equal(composed[:, :24, :32], base[:, :24, :32])
    assert torch.equal(composed[:, :24, 32:], base[:, :24, 32:])
    assert torch.equal(composed[:, 24:, :32], base[:, 24:, :32])

    manifest = json.loads(widgets(622)["ui_widget"])
    manifest["root"] = str(ASSETS)
    before = {row["file"]: (ASSETS / row["file"]).read_bytes() for row in manifest["layers"]}
    batch, canvases, layout, config, sources = LF_LoadImageLayers().on_exec(
        [manifest], [32], [True], [base], [regions])
    assert [row["id"] for row in config["image_entries"]] == [
        "base:left", "base:right", "layer:lower", "mask:lower", "layer:upper", "mask:upper"]
    assert len(canvases) == 6 and [tuple(i.shape) for i in sources] == [(1, 8, 16, 4), (1, 8, 8, 4)]
    edited = LF_Brightness().on_exec(image=batch, **widgets(624))["result"][1]
    atlas, _, layers = LF_ComposeImageLayers().on_exec(
        [base], edited, canvases, sources, [layout], [torch.ones((1, 48, 64))])
    assert atlas.shape == (1, 48, 64, 4)
    assert torch.all(atlas[..., 3] == 1)
    for restored, source in zip(layers, sources):
        assert torch.equal(restored[..., 3] == 0, source[..., 3] == 0)
        assert torch.all(restored[..., 3] <= source[..., 3])
        assert torch.any(restored[..., 3] < source[..., 3])
    assert {name: (ASSETS / name).read_bytes() for name in before} == before
    assert torch.equal(base, base_image())
