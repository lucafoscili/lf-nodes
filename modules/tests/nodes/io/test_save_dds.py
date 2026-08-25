from __future__ import annotations

import io
import sys
import types
from pathlib import Path

import numpy as np
import pytest
import torch
from PIL import Image


REPO_ROOT = Path(__file__).resolve().parents[4]

server = types.ModuleType("server")
server.PromptServer = types.SimpleNamespace(instance=None)
sys.modules.setdefault("server", server)

if "folder_paths" not in sys.modules:
    folder_paths = types.ModuleType("folder_paths")
    folder_paths.models_dir = "."
    folder_paths.get_input_directory = lambda: "."
    folder_paths.get_output_directory = lambda: "."
    folder_paths.get_temp_directory = lambda: "."
    folder_paths.get_user_directory = lambda: "."
    folder_paths.get_filename_list = lambda _folder_type: []
    folder_paths.get_save_image_path = lambda *args, **kwargs: (
        ".",
        "output",
        1,
        "",
        None,
    )
    sys.modules["folder_paths"] = folder_paths

# Keep this focused codec/node suite independent from Comfy's optional native
# model stack. The production node imports these through LF's package barrels;
# provide only the narrow helpers exercised here.
helpers = types.ModuleType("modules.utils.helpers")
helpers.__path__ = [str(REPO_ROOT / "modules" / "utils" / "helpers")]
sys.modules.setdefault("modules.utils.helpers", helpers)

comfy_helpers = types.ModuleType("modules.utils.helpers.comfy")
comfy_helpers.get_comfy_dir = lambda _kind: "."
comfy_helpers.resolve_filepath = lambda **_kwargs: ("output.dds", "", "output.dds")
comfy_helpers.safe_send_sync = lambda *_args, **_kwargs: None
sys.modules.setdefault("modules.utils.helpers.comfy", comfy_helpers)


def _normalize_input_image(image):
    if image is None:
        return []
    images = []

    def collect(item):
        if item is None:
            return
        if isinstance(item, torch.Tensor):
            if item.ndim == 4:
                images.extend(single.unsqueeze(0) for single in item)
            elif item.ndim == 3:
                images.append(item.unsqueeze(0))
            else:
                raise ValueError("Input tensor must be 3D or 4D.")
        elif isinstance(item, (list, tuple)):
            for child in item:
                collect(child)
        else:
            raise TypeError("Unsupported image container type.")

    collect(image)
    return images


logic_helpers = types.ModuleType("modules.utils.helpers.logic")
logic_helpers.normalize_input_image = _normalize_input_image
logic_helpers.normalize_list_to_value = (
    lambda value: value[0] if isinstance(value, list) and value else value
)
sys.modules.setdefault("modules.utils.helpers.logic", logic_helpers)

constants = types.ModuleType("modules.utils.constants")
constants.FUNCTION = "on_exec"
constants.Input = types.SimpleNamespace(
    IMAGE="IMAGE",
    JSON="JSON",
    LF_TREE="LF_TREE",
    STRING="STRING",
)
sys.modules.setdefault("modules.utils.constants", constants)

io_package = types.ModuleType("modules.nodes.io")
io_package.__path__ = [str(REPO_ROOT / "modules" / "nodes" / "io")]
io_package.CATEGORY = "LF Nodes/IO Operations"
sys.modules.setdefault("modules.nodes.io", io_package)

from modules.nodes.io import dds_codec, save_dds
from modules.nodes.io.dds_codec import (
    DDSOutputError,
    encode_dds,
    normalize_tensor_image,
    read_dds_header,
    write_dds_atomic,
)


def pattern(width: int, height: int, channels: int) -> np.ndarray:
    y, x = np.indices((height, width))
    pixels = np.empty((height, width, channels), dtype=np.uint8)
    pixels[..., 0] = x % 256
    pixels[..., 1] = y % 256
    pixels[..., 2] = (x + y) % 256
    if channels == 4:
        pixels[..., 3] = (x * 7 + y * 11) % 256
    return pixels


def individual_level_files(data: bytes) -> list[tuple[int, int, bytes]]:
    header = read_dds_header(data)
    width = header["width"]
    height = header["height"]
    pixel_format = header["pixel_format"]
    offset = 128
    levels = []

    for _ in range(header["mip_count"]):
        if pixel_format in ("BC1", "BC3"):
            size = dds_codec._compressed_level_size(width, height, pixel_format)
        else:
            size = width * height * (3 if pixel_format == "RGB24" else 4)
        payload = data[offset : offset + size]
        levels.append(
            (
                width,
                height,
                dds_codec._build_header(width, height, pixel_format, 1) + payload,
            )
        )
        offset += size
        width = max(1, width // 2)
        height = max(1, height // 2)

    assert offset == len(data)
    return levels


@pytest.mark.parametrize(
    ("width", "height", "channels", "pixel_format", "mip_policy", "mip_count", "byte_length", "sha256"),
    (
        (
            450,
            150,
            3,
            "RGB24",
            "none",
            1,
            202_628,
            "sha256:2b78f24f071bfa00592599dc6b697b81419c4e076fcb88c14d93f380c3f32ece",
        ),
        (
            400,
            320,
            4,
            "RGBA32",
            "none",
            1,
            512_128,
            "sha256:9f394fbb50c0680db33ac4e834028e661f9c42b32c346989090f0c24bd2dc2cd",
        ),
        (
            29,
            29,
            4,
            "RGBA32",
            "none",
            1,
            3_492,
            "sha256:eec1ea43147968372e25e386666904aee33b10f20e27f9e727a9917e741fefe5",
        ),
        (
            1_920,
            1_080,
            3,
            "BC1",
            "full_chain",
            11,
            1_383_240,
            "sha256:3962ec9a013ad979d9ed39c8b3e5db90add348e5bc1e98a6747025691875b6c7",
        ),
        (
            512,
            512,
            4,
            "BC3",
            "none",
            1,
            262_272,
            "sha256:0a48b8bef317819e0b0903c45072c2bb9c704f870b6cfcaf0350f6c269b2855e",
        ),
    ),
)
def test_pinned_acceptance_shapes_are_deterministic_and_decodable(
    width: int,
    height: int,
    channels: int,
    pixel_format: str,
    mip_policy: str,
    mip_count: int,
    byte_length: int,
    sha256: str,
) -> None:
    data, receipt = encode_dds(
        pattern(width, height, channels),
        pixel_format,
        mip_policy,
    )

    assert receipt["width"] == width
    assert receipt["height"] == height
    assert receipt["pixel_format"] == pixel_format
    assert receipt["mip_count"] == mip_count
    assert receipt["byte_length"] == byte_length
    assert receipt["sha256"] == sha256
    assert read_dds_header(data)["mip_count"] == mip_count

    with Image.open(io.BytesIO(data)) as decoded:
        decoded.load()
        assert decoded.size == (width, height)


def test_full_chain_uses_floor_halving_and_correct_compressed_linear_size() -> None:
    data, receipt = encode_dds(pattern(1_920, 1_080, 3), "BC1", "full_chain")
    header = read_dds_header(data)

    assert receipt["mip_count"] == 11
    assert header["pitch_or_linear_size"] == 1_036_800
    assert header["byte_length"] == 1_383_240
    assert receipt["normalization"] == {
        "range": "clamp_0_1",
        "quantization": "round_half_up_u8",
        "mip_filter": "pillow_lanczos",
        "colorspace": "srgb_encoded",
        "alpha_filter": "none",
        "dimension_rule": "floor_half_until_1x1",
    }


def test_rgba_mips_use_premultiplied_alpha_filtering() -> None:
    _, receipt = encode_dds(pattern(17, 9, 4), "RGBA32", "full_chain")

    assert receipt["mip_count"] == 5
    assert receipt["alpha_policy"] == "preserve"
    assert receipt["normalization"]["alpha_filter"] == "premultiplied"


@pytest.mark.parametrize(
    ("pixel_format", "channels"),
    (("RGB24", 3), ("RGBA32", 4), ("BC1", 3), ("BC3", 4)),
)
def test_every_generated_mip_is_independently_decodable(
    pixel_format: str,
    channels: int,
) -> None:
    source = pattern(31, 19, channels)
    data, receipt = encode_dds(source, pixel_format, "full_chain")
    expected_levels = dds_codec._generate_levels(
        dds_codec._prepare_pixels(source, pixel_format)[0],
        "full_chain",
    )
    encoded_levels = individual_level_files(data)

    assert len(encoded_levels) == receipt["mip_count"] == len(expected_levels)
    for (width, height, level_file), expected in zip(encoded_levels, expected_levels):
        with Image.open(io.BytesIO(level_file)) as decoded:
            decoded.load()
            assert decoded.size == (width, height)
            rgba = decoded.convert("RGBA")
            alpha_extrema = rgba.getchannel("A").getextrema()

            if pixel_format in ("RGB24", "BC1"):
                assert alpha_extrema == (255, 255)
            else:
                assert alpha_extrema[0] < 255

            if pixel_format in ("RGB24", "RGBA32"):
                decoded_pixels = np.asarray(
                    decoded.convert("RGB" if pixel_format == "RGB24" else "RGBA")
                )
                assert np.array_equal(decoded_pixels, expected)


def test_normalization_is_explicit_clamp_and_round_half_up() -> None:
    tensor = torch.tensor(
        [[[-1.0, 0.5, 2.0], [0.0, 0.499, 1.0]]],
        dtype=torch.float32,
    )

    normalized = normalize_tensor_image(tensor)

    assert normalized.tolist() == [[[0, 128, 255], [0, 127, 255]]]


@pytest.mark.parametrize("pixel_format", ("RGB24", "BC1"))
def test_non_opaque_alpha_is_never_discarded(pixel_format: str) -> None:
    pixels = np.full((4, 4, 4), 255, dtype=np.uint8)
    pixels[0, 0, 3] = 254

    with pytest.raises(DDSOutputError) as raised:
        encode_dds(pixels, pixel_format, "none")

    assert raised.value.code == "invalid_alpha"
    assert raised.value.payload["error"]["details"]["non_opaque_pixels"] == 1


def test_opaque_rgba_can_enter_rgb_without_silent_data_loss() -> None:
    pixels = np.full((4, 4, 4), 255, dtype=np.uint8)

    _, receipt = encode_dds(pixels, "RGB24", "none")

    assert receipt["alpha_policy"] == "opaque_required"


@pytest.mark.parametrize(
    ("operation", "code"),
    (
        (lambda: encode_dds(pattern(4, 4, 3), "BC7", "none"), "unsupported_format"),
        (lambda: encode_dds(pattern(4, 4, 3), "RGB24", "nearest"), "unsupported_format"),
        (lambda: normalize_tensor_image(torch.zeros((1, 4, 4, 2))), "invalid_dimensions"),
        (lambda: normalize_tensor_image(torch.zeros((1, 4, 4, 3), dtype=torch.int16)), "encode_failure"),
    ),
)
def test_errors_are_machine_readable(operation, code: str) -> None:
    with pytest.raises(DDSOutputError) as raised:
        operation()

    assert raised.value.code == code
    assert raised.value.payload["schema"] == "lf.dds.error.v1"
    assert f'"code":"{code}"' in str(raised.value)


def test_backend_revision_drift_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(dds_codec.PIL, "__version__", "99.0.0")

    with pytest.raises(DDSOutputError) as raised:
        encode_dds(pattern(4, 4, 3), "BC1", "none")

    assert raised.value.code == "unsupported_backend"
    assert raised.value.payload["error"]["details"] == {
        "backend": "Pillow",
        "expected_revision": "12.2.0",
        "actual_revision": "99.0.0",
    }


def test_codec_failure_is_wrapped_in_stable_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_save(*_args, **_kwargs):
        raise OSError("codec unavailable")

    monkeypatch.setattr(Image.Image, "save", fail_save)

    with pytest.raises(DDSOutputError) as raised:
        encode_dds(pattern(4, 4, 3), "BC1", "none")

    assert raised.value.code == "encode_failure"


def test_readback_mismatch_detects_header_tampering() -> None:
    data, _ = encode_dds(pattern(8, 8, 3), "RGB24", "none")
    tampered = bytearray(data)
    tampered[16:20] = struct_width = (9).to_bytes(4, "little")
    assert struct_width == b"\x09\x00\x00\x00"

    with pytest.raises(DDSOutputError) as raised:
        read_dds_header(bytes(tampered))

    assert raised.value.code == "readback_mismatch"


def test_readback_rejects_extra_compressed_pixel_flags() -> None:
    data, _ = encode_dds(pattern(8, 8, 3), "BC1", "none")
    tampered = bytearray(data)
    pixel_flags_offset = 4 + (19 * 4)
    pixel_flags = int.from_bytes(
        tampered[pixel_flags_offset : pixel_flags_offset + 4],
        "little",
    )
    tampered[pixel_flags_offset : pixel_flags_offset + 4] = (
        pixel_flags | dds_codec._DDPF_RGB
    ).to_bytes(4, "little")

    with pytest.raises(DDSOutputError) as raised:
        read_dds_header(bytes(tampered))

    assert raised.value.code == "readback_mismatch"


def test_atomic_writer_removes_partial_output_after_final_readback_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    data, receipt = encode_dds(pattern(8, 8, 3), "RGB24", "none")
    target = tmp_path / "result.dds"
    original_verify = dds_codec._verify_dds_bytes
    calls = 0

    def fail_final(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise DDSOutputError("readback_mismatch", "forced final mismatch")
        return original_verify(*args, **kwargs)

    monkeypatch.setattr(dds_codec, "_verify_dds_bytes", fail_final)

    with pytest.raises(DDSOutputError) as raised:
        write_dds_atomic(target, data, receipt)

    assert raised.value.code == "readback_mismatch"
    assert not target.exists()
    assert list(tmp_path.glob("*.tmp")) == []


def test_atomic_writer_never_replaces_an_occupied_target(tmp_path: Path) -> None:
    data, receipt = encode_dds(pattern(8, 8, 3), "RGB24", "none")
    target = tmp_path / "result.dds"
    target.write_bytes(b"pre-existing")

    with pytest.raises(DDSOutputError) as raised:
        write_dds_atomic(target, data, receipt)

    assert raised.value.code == "encode_failure"
    assert raised.value.payload["error"]["details"]["stage"] == "publish_no_clobber"
    assert target.read_bytes() == b"pre-existing"
    assert list(tmp_path.glob("*.tmp")) == []


def test_node_publishes_ordered_files_and_receipt_envelope(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    paths = [
        (tmp_path / "generic_00001.dds", "", "generic_00001.dds"),
        (tmp_path / "generic_00002.dds", "", "generic_00002.dds"),
    ]
    sent = []
    monkeypatch.setattr(save_dds, "get_comfy_dir", lambda _kind: str(tmp_path))
    monkeypatch.setattr(save_dds, "resolve_filepath", lambda **_kwargs: paths.pop(0))
    monkeypatch.setattr(save_dds, "safe_send_sync", lambda *args: sent.append(args))
    batch = torch.from_numpy(
        np.stack((pattern(8, 8, 3), pattern(8, 8, 3)[::-1].copy()))
    ).to(torch.float32) / 255.0

    result = save_dds.LF_SaveDDS().on_exec(
        image=batch,
        filename_prefix="generic",
        pixel_format="RGB24",
        mip_policy="none",
        node_id="node-7",
    )

    assert result["result"][0] == ["generic_00001.dds", "generic_00002.dds"]
    receipt = result["result"][1]
    assert receipt["schema"] == "lf.dds.receipt.v1"
    assert [item["index"] for item in receipt["files"]] == [0, 1]
    assert result["ui"]["lf_output"][0]["file_names"] == result["result"][0]
    assert result["ui"]["lf_output"][0]["receipt"] == receipt
    assert all((tmp_path / name).is_file() for name in result["result"][0])
    assert sent[0][0] == "savedds"
    assert sent[0][2] == "node-7"


def test_node_rolls_back_earlier_batch_files_on_write_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    counter = 0
    first = tmp_path / "first.dds"
    second = tmp_path / "second.dds"
    paths = [(first, "", first.name), (second, "", second.name)]
    original_write = write_dds_atomic

    def fail_second(path, data, receipt, *, retain_custody=False):
        nonlocal counter
        counter += 1
        if counter == 2:
            raise DDSOutputError("encode_failure", "forced write failure")
        return original_write(
            path,
            data,
            receipt,
            retain_custody=retain_custody,
        )

    monkeypatch.setattr(save_dds, "get_comfy_dir", lambda _kind: str(tmp_path))
    monkeypatch.setattr(save_dds, "resolve_filepath", lambda **_kwargs: paths.pop(0))
    monkeypatch.setattr(save_dds, "write_dds_atomic", fail_second)
    batch = torch.ones((2, 4, 4, 3), dtype=torch.float32)

    with pytest.raises(DDSOutputError):
        save_dds.LF_SaveDDS().on_exec(
            image=batch,
            filename_prefix="generic",
            pixel_format="RGB24",
            mip_policy="none",
        )

    assert not first.exists()
    assert not second.exists()


def test_batch_rollback_preserves_a_replacement_at_an_earlier_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    counter = 0
    first = tmp_path / "first.dds"
    second = tmp_path / "second.dds"
    paths = [(first, "", first.name), (second, "", second.name)]
    original_write = write_dds_atomic

    def replace_then_fail(path, data, receipt, *, retain_custody=False):
        nonlocal counter
        counter += 1
        if counter == 2:
            raise DDSOutputError("encode_failure", "forced write failure")
        custody = original_write(
            path,
            data,
            receipt,
            retain_custody=retain_custody,
        )
        path = Path(path)
        path.unlink()
        path.write_bytes(b"replacement")
        return custody

    monkeypatch.setattr(save_dds, "get_comfy_dir", lambda _kind: str(tmp_path))
    monkeypatch.setattr(save_dds, "resolve_filepath", lambda **_kwargs: paths.pop(0))
    monkeypatch.setattr(save_dds, "write_dds_atomic", replace_then_fail)

    with pytest.raises(DDSOutputError) as raised:
        save_dds.LF_SaveDDS().on_exec(
            image=torch.ones((2, 4, 4, 3), dtype=torch.float32),
            filename_prefix="generic",
            pixel_format="RGB24",
            mip_policy="none",
        )

    assert raised.value.code == "encode_failure"
    assert first.read_bytes() == b"replacement"
    assert not second.exists()
    assert list(tmp_path.glob("*.tmp")) == []


def test_batch_cleanup_failure_does_not_mask_canonical_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    counter = 0
    first = tmp_path / "first.dds"
    second = tmp_path / "second.dds"
    paths = [(first, "", first.name), (second, "", second.name)]
    original_write = write_dds_atomic
    original_unlink = Path.unlink

    def publish_then_fail(path, data, receipt, *, retain_custody=False):
        nonlocal counter
        counter += 1
        if counter == 2:
            raise DDSOutputError("readback_mismatch", "forced canonical failure")
        return original_write(
            path,
            data,
            receipt,
            retain_custody=retain_custody,
        )

    def deny_target_unlink(path: Path, *args, **kwargs):
        if path == first:
            raise OSError("cleanup denied")
        return original_unlink(path, *args, **kwargs)

    monkeypatch.setattr(save_dds, "get_comfy_dir", lambda _kind: str(tmp_path))
    monkeypatch.setattr(save_dds, "resolve_filepath", lambda **_kwargs: paths.pop(0))
    monkeypatch.setattr(save_dds, "write_dds_atomic", publish_then_fail)
    monkeypatch.setattr(Path, "unlink", deny_target_unlink)

    with pytest.raises(DDSOutputError) as raised:
        save_dds.LF_SaveDDS().on_exec(
            image=torch.ones((2, 4, 4, 3), dtype=torch.float32),
            filename_prefix="generic",
            pixel_format="RGB24",
            mip_policy="none",
        )

    assert raised.value.code == "readback_mismatch"


def test_node_wraps_malformed_batch_in_stable_error() -> None:
    with pytest.raises(DDSOutputError) as raised:
        save_dds.LF_SaveDDS().on_exec(
            image=torch.zeros((4, 4)),
            filename_prefix="generic",
            pixel_format="RGB24",
            mip_policy="none",
        )

    assert raised.value.code == "invalid_dimensions"
    assert raised.value.payload["schema"] == "lf.dds.error.v1"


def test_node_wraps_output_resolution_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        save_dds,
        "get_comfy_dir",
        lambda _kind: (_ for _ in ()).throw(OSError("unavailable")),
    )

    with pytest.raises(DDSOutputError) as raised:
        save_dds.LF_SaveDDS().on_exec(
            image=torch.ones((1, 4, 4, 3), dtype=torch.float32),
            filename_prefix="generic",
            pixel_format="RGB24",
            mip_policy="none",
        )

    assert raised.value.code == "encode_failure"
    assert raised.value.payload["error"]["details"]["stage"] == "node_execution"


def test_public_node_contract_is_generic_and_registered() -> None:
    inputs = save_dds.LF_SaveDDS.INPUT_TYPES()

    assert inputs["required"]["pixel_format"][0] == ["RGB24", "RGBA32", "BC1", "BC3"]
    assert inputs["required"]["mip_policy"][0] == ["none", "full_chain"]
    assert inputs["optional"]["ui_widget"][0] == "LF_TREE"
    assert "add_timestamp" not in inputs["required"]
    assert save_dds.NODE_CLASS_MAPPINGS["LF_SaveDDS"] is save_dds.LF_SaveDDS
    assert save_dds.NODE_DISPLAY_NAME_MAPPINGS["LF_SaveDDS"] == "Save DDS"
