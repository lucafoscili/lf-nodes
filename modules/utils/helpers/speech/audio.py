"""Comfy AUDIO values as the mono waveforms speech models read, and back."""

from __future__ import annotations

import numpy as np
import torch

from ...audio import normalize_audio


def mono(audio: dict, *, name: str = "audio") -> tuple[torch.Tensor, int]:
    """One AUDIO item as a 1-D float32 CPU waveform and its rate; a batch of more than one is refused, since a
    speech model reads one recording at a time."""
    try:
        waveform, sample_rate = normalize_audio(audio)
    except ValueError as error:
        raise ValueError(f"{name}: {error}") from None
    if waveform.shape[0] != 1:
        raise ValueError(f"{name} holds {waveform.shape[0]} recordings; join them into one first.")
    return waveform[0].mean(dim=0), sample_rate


def resampled(waveform: torch.Tensor, sample_rate: int, target_rate: int) -> torch.Tensor:
    """`waveform` at `target_rate` (torchaudio's band-limited resampler); unchanged when the rates match."""
    if sample_rate == target_rate:
        return waveform
    import torchaudio

    return torchaudio.functional.resample(waveform, orig_freq=sample_rate, new_freq=target_rate)


def to_audio(waveform, sample_rate: int) -> dict:
    """A 1-D waveform (tensor or array) as a mono Comfy AUDIO value of one item."""
    if isinstance(waveform, np.ndarray):
        waveform = torch.from_numpy(np.ascontiguousarray(waveform))
    waveform = waveform.detach().to(device="cpu", dtype=torch.float32).reshape(-1)
    if waveform.numel() == 0:
        raise ValueError("The model returned no audio.")
    if not torch.isfinite(waveform).all().item():
        raise ValueError("The model returned audio with non-finite samples.")
    return {"waveform": waveform.reshape(1, 1, -1), "sample_rate": int(sample_rate)}


def seconds(waveform: torch.Tensor, sample_rate: int) -> float:
    return round(waveform.shape[-1] / sample_rate, 3)
