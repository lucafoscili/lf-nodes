"""Load PNG and Save PNG keep stored values: 8 and 16 bits, raw alpha, rounding, no metadata."""
from __future__ import annotations

import io
import types

import numpy as np
import pytest
import torch
from PIL import Image

from modules.nodes.io import load_png, save_png
from modules.utils import stored_png
from modules.utils.helpers.ui import generated_preview


@pytest.fixture(autouse=True)
def comfy_dirs(monkeypatch, tmp_path):
    roots = {kind: tmp_path / kind for kind in ("input", "output")}
    for root in roots.values():
        root.mkdir()
    monkeypatch.setattr(generated_preview, "get_comfy_dir", lambda _kind: str(roots["input"]))

    def annotated(name):
        reference = name[:-len(" [input]")] if name.endswith(" [input]") else name
        return str(roots["input"] / reference)

    fake = types.SimpleNamespace(
        get_input_directory=lambda: str(roots["input"]),
        get_annotated_filepath=annotated,
        exists_annotated_filepath=lambda name: (roots["input"] / name.replace(" [input]", "")).is_file(),
    )
    monkeypatch.setattr(load_png, "_folder_paths", lambda: fake)
    monkeypatch.setattr(save_png, "get_comfy_dir", lambda _kind: str(roots["output"]))
    counter = iter(range(1, 100))

    def resolve(filename_prefix, base_output_path, extension, **_kwargs):
        folder, _, stem = filename_prefix.rpartition("/")
        name = f"{stem}_{next(counter):05}.{extension}"
        (roots["output"] / folder).mkdir(parents=True, exist_ok=True)
        return str(roots["output"] / folder / name), folder, name

    monkeypatch.setattr(save_png, "resolve_filepath", resolve)
    return roots


@pytest.fixture
def events(monkeypatch):
    sent = []
    for module in (load_png, save_png):
        monkeypatch.setattr(module, "safe_send_sync", lambda event, payload, node_id: sent.append(
            (event, payload, node_id)))
    return sent


def _levels(dtype, channels, height=6, width=9):
    top = np.iinfo(dtype).max
    return np.random.default_rng(channels).integers(0, top + 1, (height, width, channels)).astype(dtype)


# region codec
@pytest.mark.parametrize("dtype", [np.uint8, np.uint16])
@pytest.mark.parametrize("channels", [1, 3, 4])
def test_png_bytes_round_trip_every_value(dtype, channels):
    pixels = _levels(dtype, channels)
    decoded, header = stored_png.read_png(stored_png.write_png(pixels))
    assert decoded.dtype == dtype
    np.testing.assert_array_equal(decoded, pixels)
    assert header["bit_depth"] == np.dtype(dtype).itemsize * 8
    assert header["color_type"] == {1: "grey", 3: "rgb", 4: "rgba"}[channels]


@pytest.mark.parametrize("dtype,top", [(np.uint8, 255), (np.uint16, 65535)])
def test_tensor_round_trip_is_exact_for_every_level(dtype, top):
    levels = np.arange(top + 1, dtype=dtype)
    pixels = np.resize(levels, (len(levels) // 256, 256, 1)).repeat(3, axis=2)
    tensor = stored_png.to_tensor(pixels)
    assert tensor.dtype == torch.float32 and tensor.shape == (1, *pixels.shape)
    np.testing.assert_array_equal(stored_png.from_tensor(tensor[0], 8 if top == 255 else 16), pixels)


def test_save_rounds_where_a_truncating_save_would_drop_a_level():
    image = torch.tensor([[[0.4 / 255, 0.6 / 255, 254.5 / 255 + 1e-4]]], dtype=torch.float32)
    np.testing.assert_array_equal(stored_png.from_tensor(image, 8), [[[0, 1, 255]]])
    # Core's save: clip(255 * x).astype(uint8) would give 0, 0, 254.
    np.testing.assert_array_equal(np.clip(255.0 * image.numpy(), 0, 255).astype(np.uint8), [[[0, 0, 254]]])


def test_alpha_is_read_as_stored_not_inverted_and_channels_keep_rgb_order():
    buffer = io.BytesIO()
    Image.new("RGBA", (2, 1), (10, 20, 30, 40)).save(buffer, "PNG")
    pixels, header = stored_png.read_png(buffer.getvalue())
    np.testing.assert_array_equal(pixels[0, 0], [10, 20, 30, 40])
    assert header["color_type"] == "rgba"
    written = Image.open(io.BytesIO(stored_png.write_png(pixels)))
    assert written.getpixel((0, 0)) == (10, 20, 30, 40)


def test_grey_alpha_keeps_two_stored_channels_and_widens_to_rgba():
    buffer = io.BytesIO()
    Image.new("LA", (1, 1), (100, 7)).save(buffer, "PNG")
    pixels, header = stored_png.read_png(buffer.getvalue())
    assert header["color_type"] == "grey_alpha"
    np.testing.assert_array_equal(pixels[0, 0], [100, 7])
    tensor = stored_png.to_tensor(pixels)
    np.testing.assert_array_equal(stored_png.from_tensor(tensor[0], 8)[0, 0], [100, 100, 100, 7])


def test_written_png_holds_only_its_pixels():
    data = stored_png.write_png(_levels(np.uint16, 4))
    chunks, offset = [], 8
    while offset < len(data):
        length = int.from_bytes(data[offset:offset + 4], "big")
        chunks.append(data[offset + 4:offset + 8])
        offset += 12 + length
    assert set(chunks) == {b"IHDR", b"IDAT", b"IEND"}


def test_failures_are_loud():
    with pytest.raises(ValueError, match="Not a PNG"):
        stored_png.read_png(b"GIF89a....")
    with pytest.raises(ValueError, match="bit_depth"):
        stored_png.from_tensor(torch.zeros(2, 2, 3), 12)
    with pytest.raises(ValueError, match="NaN"):
        stored_png.from_tensor(torch.full((2, 2, 3), float("nan")), 8)
    with pytest.raises(ValueError, match="channels"):
        stored_png.from_tensor(torch.zeros(2, 2, 2), 8)
    with pytest.raises(ValueError, match="compress_level"):
        stored_png.write_png(_levels(np.uint8, 3), 10)
# endregion


# region nodes
def test_published_schemas():
    load = load_png.LF_LoadPNG
    assert list(load.INPUT_TYPES()["required"]) == ["image"]
    assert load.INPUT_TYPES()["required"]["image"][1]["image_upload"] is True
    assert load.INPUT_TYPES()["optional"]["ui_widget"][0] == "LF_MASONRY"
    assert load.RETURN_NAMES == ("image", "alpha", "bit_depth", "receipt", "image_list")
    assert load.RETURN_TYPES == ("IMAGE", "MASK", "INT", "JSON", "IMAGE")
    assert load.OUTPUT_IS_LIST == (False, False, False, False, True)
    save = save_png.LF_SavePNG
    inputs = save.INPUT_TYPES()
    assert list(inputs["required"]) == ["image", "filename_prefix", "bit_depth", "compress_level"]
    assert inputs["required"]["bit_depth"][1]["default"] == 8
    assert inputs["optional"]["ui_widget"][0] == "LF_MASONRY"
    assert save.INPUT_IS_LIST is True and save.OUTPUT_NODE is True
    assert save.RETURN_NAMES == ("file_names", "receipt") and save.OUTPUT_IS_LIST == (True, False)
    assert load_png.NODE_DISPLAY_NAME_MAPPINGS["LF_LoadPNG"] == "Load PNG (stored values)"
    assert save_png.NODE_DISPLAY_NAME_MAPPINGS["LF_SavePNG"] == "Save PNG (stored values)"


@pytest.mark.parametrize("dtype,bits", [(np.uint8, 8), (np.uint16, 16)])
def test_load_then_save_reproduces_the_file_values(comfy_dirs, events, dtype, bits):
    pixels = _levels(dtype, 4)
    (comfy_dirs["input"] / "texture.png").write_bytes(stored_png.write_png(pixels))
    assert load_png.LF_LoadPNG.VALIDATE_INPUTS("texture.png [input]") is True
    assert load_png.LF_LoadPNG.VALIDATE_INPUTS("missing.png") != True

    loaded = load_png.LF_LoadPNG().on_exec(image="texture.png [input]", node_id="5")
    image, alpha, bit_depth, receipt, image_list = loaded["result"]
    assert image.shape == (1, 6, 9, 4) and bit_depth == bits and len(image_list) == 1
    torch.testing.assert_close(alpha[0], image[0, ..., 3])  # stored alpha, not 1 - alpha
    assert receipt["schema"] == "lf.load-png.v1" and receipt["alpha"] is True
    assert receipt["color_type"] == "rgba" and receipt["bit_depth"] == bits

    saved = save_png.LF_SavePNG().on_exec(image=[image], filename_prefix=["textures/out"], bit_depth=[bit_depth],
                                          compress_level=[4], node_id=["6"])
    file_names, save_receipt = saved["result"]
    assert file_names == ["textures/out_00001.png"]
    assert saved["ui"]["lf_output"][0]["file_names"] == file_names
    data = (comfy_dirs["output"] / file_names[0]).read_bytes()
    decoded, _ = stored_png.read_png(data)
    np.testing.assert_array_equal(decoded, pixels)
    row = save_receipt["files"][0]
    assert row["channels"] == "rgba" and row["bit_depth"] == bits and row["sha256"] == stored_png.sha256(data)
    assert save_receipt["rounding"] == "nearest" and save_receipt["metadata"] == "none"
    assert [event for event, _payload, _node in events] == ["loadpng", "savepng"]
    assert events[0][2] == "5" and events[1][2] == ["6"]
    assert all(payload["dataset"]["nodes"] for _event, payload, _node in events)


def test_load_without_alpha_gives_an_opaque_mask(comfy_dirs, events):
    (comfy_dirs["input"] / "rgb.png").write_bytes(stored_png.write_png(_levels(np.uint8, 3)))
    image, alpha, bit_depth, receipt, _ = load_png.LF_LoadPNG().on_exec(image="rgb.png")["result"]
    assert image.shape[-1] == 3 and bool((alpha == 1).all()) and receipt["alpha"] is False and bit_depth == 8


def test_load_accepts_an_absolute_path(tmp_path, events):
    path = tmp_path / "elsewhere.png"
    path.write_bytes(stored_png.write_png(_levels(np.uint16, 1)))
    assert load_png.LF_LoadPNG.VALIDATE_INPUTS(str(path)) is True
    image, _alpha, bit_depth, receipt, _ = load_png.LF_LoadPNG().on_exec(image=str(path))["result"]
    assert image.shape[-1] == 3 and bit_depth == 16 and receipt["color_type"] == "grey"
    assert load_png.LF_LoadPNG.VALIDATE_INPUTS(str(tmp_path / "absent.png")) != True


def test_save_refuses_an_unknown_bit_depth_and_a_missing_image(events):
    with pytest.raises(ValueError, match="bit_depth"):
        save_png.LF_SavePNG().on_exec(image=[torch.zeros(1, 2, 2, 3)], filename_prefix=["x"], bit_depth=[12])
    with pytest.raises(ValueError, match="at least one image"):
        save_png.LF_SavePNG().on_exec(image=None, filename_prefix=["x"], bit_depth=[8])
    with pytest.raises(ValueError, match="Invalid image file"):
        load_png.LF_LoadPNG().on_exec(image="missing.png")
# endregion
