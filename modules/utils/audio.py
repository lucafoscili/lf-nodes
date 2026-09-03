"""Lossless WAV encoding and output-path checks for Comfy AUDIO values."""

from io import BytesIO
from numbers import Integral
from pathlib import Path, PureWindowsPath

import av
import torch


def normalize_audio(audio: dict) -> tuple[torch.Tensor, int]:
    if not isinstance(audio, dict):
        raise ValueError("Audio must contain a waveform tensor and sample_rate.")
    waveform = audio.get("waveform")
    if (
        not isinstance(waveform, torch.Tensor)
        or waveform.ndim != 3
        or any(size == 0 for size in waveform.shape)
        or waveform.shape[1] not in (1, 2)
        or not waveform.is_floating_point()
    ):
        raise ValueError("Audio waveform must be a non-empty floating-point [batch, 1 or 2 channels, samples] tensor.")
    sample_rate = audio.get("sample_rate")
    if isinstance(sample_rate, bool) or not isinstance(sample_rate, Integral) or not 1 <= sample_rate <= 384000:
        raise ValueError("Audio sample_rate must be an integer from 1 to 384000 Hz.")
    waveform = waveform.detach().to(device="cpu", dtype=torch.float32)
    if not torch.isfinite(waveform).all().item():
        raise ValueError("Audio waveform must contain only finite values.")
    return waveform, int(sample_rate)


def validate_audio_prefix(filename_prefix: str, output_root: Path) -> str:
    if not isinstance(filename_prefix, str) or not filename_prefix.strip():
        raise ValueError("filename_prefix must be a non-empty output-relative path.")
    portable = filename_prefix.replace("\\", "/")
    parts = portable.split("/")
    if (
        portable.startswith("/")
        or PureWindowsPath(portable).drive
        or any(part in ("", ".", "..") or part.rstrip(" .") != part for part in parts)
        or any(ord(character) < 32 or character in ':<>"|?*' for character in portable)
    ):
        raise ValueError("filename_prefix must be a safe path relative to ComfyUI output.")
    try:
        (output_root / portable).resolve().relative_to(output_root)
    except ValueError as error:
        raise ValueError("Audio output path must remain inside ComfyUI output.") from error
    return portable


def encode_float_wav(waveform: torch.Tensor, sample_rate: int) -> bytes:
    """Encode one validated [channels, samples] item without changing amplitude."""
    layout = "mono" if waveform.shape[0] == 1 else "stereo"
    buffer = BytesIO()
    with av.open(buffer, mode="w", format="wav") as container:
        stream = container.add_stream("pcm_f32le", rate=sample_rate, layout=layout)
        frame = av.AudioFrame.from_ndarray(
            waveform.transpose(0, 1).contiguous().reshape(1, -1).numpy(),
            format="flt",
            layout=layout,
        )
        frame.sample_rate = sample_rate
        frame.pts = 0
        container.mux(stream.encode(frame))
        container.mux(stream.encode(None))
    return buffer.getvalue()


def write_audio_file(path: Path, data: bytes) -> None:
    # Exclusive creation protects existing artifacts, including a racing saver.
    handle = path.open("xb")
    try:
        with handle:
            handle.write(data)
    except BaseException:
        path.unlink(missing_ok=True)
        raise
