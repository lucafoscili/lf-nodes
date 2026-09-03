from __future__ import annotations

import importlib
import sys
import types
from pathlib import Path

import av
import numpy as np
import pytest
import torch


ROOT = Path(__file__).resolve().parents[4]
helpers = sys.modules.setdefault("modules.utils.helpers", types.ModuleType("modules.utils.helpers"))
helpers.__path__ = [str(ROOT / "modules/utils/helpers")]
comfy_helpers = sys.modules.setdefault("modules.utils.helpers.comfy", types.ModuleType("modules.utils.helpers.comfy"))
comfy_helpers.__path__ = [str(ROOT / "modules/utils/helpers/comfy")]
for name, value in {
    "get_comfy_dir": lambda _kind: ".",
    "resolve_filepath": lambda **_kwargs: ("audio.wav", "", "audio.wav"),
    "safe_send_sync": lambda *_args, **_kwargs: None,
}.items():
    if not hasattr(comfy_helpers, name):
        setattr(comfy_helpers, name, value)
constants = sys.modules.setdefault("modules.utils.constants", types.ModuleType("modules.utils.constants"))
constants.FUNCTION = "on_exec"
constants.Input = getattr(constants, "Input", types.SimpleNamespace())
for name in ("AUDIO", "STRING", "JSON", "LF_MASONRY"):
    if not hasattr(constants.Input, name):
        setattr(constants.Input, name, name)
io_package = sys.modules.setdefault("modules.nodes.io", types.ModuleType("modules.nodes.io"))
io_package.__path__ = [str(ROOT / "modules/nodes/io")]
io_package.CATEGORY = "LF Nodes/IO Operations"

from modules.nodes.io import save_audio
from modules.utils import audio as audio_helpers


@pytest.fixture
def output(tmp_path, monkeypatch):
    output_root = tmp_path / "output"
    monkeypatch.setattr(save_audio, "get_comfy_dir", lambda _kind: str(output_root))

    def resolve(**kwargs):
        prefix = Path(kwargs["base_output_path"]) / kwargs["filename_prefix"]
        prefix.parent.mkdir(parents=True, exist_ok=True)
        counter = 1
        while prefix.with_name(f"{prefix.name}_{counter}.wav").exists():
            counter += 1
        path = prefix.with_name(f"{prefix.name}_{counter}.wav")
        return str(path), path.parent.relative_to(output_root).as_posix(), path.name

    monkeypatch.setattr(save_audio, "resolve_filepath", resolve)
    return output_root


def decode(path):
    with av.open(str(path)) as container:
        stream = container.streams.audio[0]
        assert stream.codec_context.name == "pcm_f32le"
        frames = list(container.decode(stream))
        channels = stream.codec_context.channels
        samples = np.concatenate([frame.to_ndarray().reshape(-1, channels) for frame in frames])
        return samples.T, stream.codec_context.sample_rate


def test_schema_is_headless_and_outputs_an_ordered_reference_list():
    cls = save_audio.LF_SaveAudio
    schema = cls.INPUT_TYPES()
    assert set(schema["required"]) == {"audio", "filename_prefix"}
    assert schema["required"]["audio"][0] == "AUDIO"
    assert schema["required"]["filename_prefix"][1]["default"] == "audio/ComfyUI"
    assert schema["optional"]["ui_widget"][0] == "LF_MASONRY"
    assert cls.RETURN_NAMES == ("output_reference", "receipt")
    assert cls.RETURN_TYPES == ("STRING", "JSON")
    assert cls.OUTPUT_IS_LIST == (True, False)
    assert not getattr(cls, "INPUT_IS_LIST", False)
    assert cls.OUTPUT_NODE
    assert save_audio.NODE_CLASS_MAPPINGS == {"LF_SaveAudio": cls}


def test_stereo_batch_round_trip_preserves_order_amplitude_and_history(output, monkeypatch):
    waveform = torch.tensor([
        [[0.0, 1.25, -2.0, 0.125], [0.5, -0.25, 0.75, -0.5]],
        [[0.2, 0.4, 0.6, 0.8], [-0.2, -0.4, -0.6, -0.8]],
    ])
    original = waveform.clone()
    sent = []
    monkeypatch.setattr(save_audio, "safe_send_sync", lambda *args: sent.append(args))
    result = save_audio.LF_SaveAudio().on_exec(
        {"waveform": waveform, "sample_rate": 44100}, "sounds/écho", node_id=["audio-1"]
    )
    references, receipt = result["result"]
    assert references == ["sounds/écho_1.wav [output]", "sounds/écho_2.wav [output]"]
    assert receipt["schema"] == "lf.audio_file.receipt.v1"
    assert len(receipt["files"]) == 2
    for index, item in enumerate(receipt["files"]):
        path = output / item["file_name"]
        decoded, rate = decode(path)
        np.testing.assert_array_equal(decoded, waveform[index].numpy())
        assert rate == 44100
        assert item == {
            "index": index, "file_name": f"sounds/écho_{index + 1}.wav", "storage_type": "output",
            "format": "wav", "encoding": "pcm_f32le", "sample_rate": 44100,
            "channels": 2, "samples": 4, "duration_seconds": 4 / 44100,
            "byte_length": path.stat().st_size,
        }
    torch.testing.assert_close(waveform, original, rtol=0, atol=0)
    payload = result["ui"]["lf_output"][0]
    assert payload["receipt"] == receipt
    assert payload["file_names"] == [item["file_name"] for item in receipt["files"]]
    assert payload["audio"] == result["ui"]["audio"] == [
        {"filename": "écho_1.wav", "subfolder": "sounds", "type": "output"},
        {"filename": "écho_2.wav", "subfolder": "sounds", "type": "output"},
    ]
    assert sent == [("saveaudio", payload, ["audio-1"])]


def test_mono_noncontiguous_float64_input_and_counter_do_not_overwrite(output):
    waveform = torch.linspace(-1, 1, 16, dtype=torch.float64).reshape(1, 1, 16)[..., ::2]
    audio = {"waveform": waveform, "sample_rate": 48000}
    first = save_audio.LF_SaveAudio().on_exec(audio, "clip")
    first_path = output / first["result"][1]["files"][0]["file_name"]
    original_bytes = first_path.read_bytes()
    second = save_audio.LF_SaveAudio().on_exec(audio, "clip")
    assert first_path.read_bytes() == original_bytes
    assert second["result"][0] == ["clip_2.wav [output]"]
    decoded, rate = decode(first_path)
    np.testing.assert_array_equal(decoded, waveform[0].float().numpy())
    assert rate == 48000
    assert first["ui"]["audio"][0]["subfolder"] == ""


@pytest.mark.parametrize("waveform", [
    None, [], torch.zeros(1, 4), torch.zeros(0, 1, 4), torch.zeros(1, 1, 0),
    torch.zeros(1, 3, 4), torch.zeros(1, 1, 4, dtype=torch.int16),
    torch.tensor([[[0.0]], [[float("nan")]]]), torch.tensor([[[float("inf")]]]),
    torch.tensor([[[1e100]]], dtype=torch.float64),
])
def test_invalid_waveforms_fail_before_any_file_or_directory_write(output, waveform):
    with pytest.raises(ValueError, match="waveform"):
        save_audio.LF_SaveAudio().on_exec({"waveform": waveform, "sample_rate": 44100})
    assert not output.exists()


@pytest.mark.parametrize("rate", [None, True, 0, -1, 384001, 44100.0, "44100", float("nan")])
def test_invalid_rates_fail_before_writes(output, rate):
    with pytest.raises(ValueError, match="sample_rate"):
        save_audio.LF_SaveAudio().on_exec({"waveform": torch.zeros(1, 1, 4), "sample_rate": rate})
    assert not output.exists()


@pytest.mark.parametrize("prefix", ["", " ", "../escape", ".. /escape", "/escape", "C:/escape", "C:escape", "clip:stream", "folder/../clip", "folder//clip", "clip\x00"])
def test_invalid_prefixes_fail_before_writes(output, prefix):
    with pytest.raises(ValueError, match="filename_prefix"):
        save_audio.LF_SaveAudio().on_exec({"waveform": torch.zeros(1, 1, 4), "sample_rate": 44100}, prefix)
    assert not output.exists()


def test_resolver_escape_is_rejected_without_writing(output, tmp_path, monkeypatch):
    outside = tmp_path / "outside.wav"
    monkeypatch.setattr(save_audio, "resolve_filepath", lambda **_kwargs: (str(outside), "", outside.name))
    with pytest.raises(ValueError, match="inside ComfyUI output"):
        save_audio.LF_SaveAudio().on_exec({"waveform": torch.zeros(1, 1, 4), "sample_rate": 44100})
    assert not outside.exists()


def test_symlink_prefix_escape_is_rejected_before_resolver(output, tmp_path, monkeypatch):
    output.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    try:
        (output / "linked").symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("Creating directory symlinks is unavailable")
    monkeypatch.setattr(save_audio, "resolve_filepath", lambda **_kwargs: pytest.fail("resolver must not run"))
    with pytest.raises(ValueError, match="inside ComfyUI output"):
        save_audio.LF_SaveAudio().on_exec({"waveform": torch.zeros(1, 1, 4), "sample_rate": 44100}, "linked/clip")
    assert list(outside.iterdir()) == []


def test_exclusive_writer_preserves_existing_file(tmp_path):
    path = tmp_path / "existing.wav"
    path.write_bytes(b"existing")
    with pytest.raises(FileExistsError):
        audio_helpers.write_audio_file(path, b"replacement")
    assert path.read_bytes() == b"existing"


def test_failed_write_removes_its_incomplete_file(tmp_path, monkeypatch):
    path = tmp_path / "failed.wav"
    open_file = Path.open

    class FailedWrite:
        def __init__(self):
            self.handle = open_file(path, "xb")

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            self.handle.close()

        def write(self, _data):
            self.handle.write(b"partial")
            raise OSError("disk write failed")

    monkeypatch.setattr(Path, "open", lambda _path, _mode: FailedWrite())
    with pytest.raises(OSError, match="disk write failed"):
        audio_helpers.write_audio_file(path, b"complete")
    assert not path.exists()


def test_headless_event_helper_and_list_wrapped_node_id(output, monkeypatch):
    helper = importlib.import_module("modules.utils.helpers.comfy.safe_send_sync")
    monkeypatch.setattr(save_audio, "safe_send_sync", helper.safe_send_sync)
    monkeypatch.setattr(sys.modules["server"].PromptServer, "instance", None)
    response = save_audio.LF_SaveAudio().on_exec(
        {"waveform": torch.zeros(1, 1, 4), "sample_rate": 44100}, node_id=["node-1"]
    )
    assert response["result"][0] == ["audio/ComfyUI_1.wav [output]"]
