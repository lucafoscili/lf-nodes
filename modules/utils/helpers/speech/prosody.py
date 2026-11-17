"""How a recording moves: its pitch and loudness over the frames where a voice sounds.

Pitch is librosa's probabilistic YIN, read every 10 ms; a frame counts when YIN calls it voiced and it is within
`LOUD_DB` of the recording's loudest frame, so breaths, room tone and silence never pass for a quiet syllable. Ranges
are the 5th to 95th percentile, so one stray frame does not set them. librosa is imported only here, when a recording
is read.
"""

from __future__ import annotations

import numpy as np
import torch

RATE = 16000
HOP = 160  # 10 ms
FRAME = 1024  # 64 ms: two periods of the lowest pitch read
LOWEST_HZ, HIGHEST_HZ = 65.0, 800.0
LOUD_DB = 40.0
FEWEST_FRAMES = 5  # voiced frames below which no pitch is read


def _span(values: np.ndarray) -> float:
    return round(float(np.percentile(values, 95) - np.percentile(values, 5)), 2)


def require():
    """librosa, which reading a recording's pitch needs; refused, naming it, where it is not installed (before a caller
    runs its models for a reading it could not finish)."""
    try:
        import librosa
    except ImportError as error:
        raise RuntimeError("Reading a recording's pitch needs the librosa package in ComfyUI's environment.") from error
    return librosa


def prosody(waveform: torch.Tensor, rate: int) -> dict:
    """The pitch (its median in hertz, its range and spread in semitones about that median) and the loudness range (in
    decibels) of `waveform`'s voiced frames, and the share of its frames that are voiced. A recording with fewer than
    `FEWEST_FRAMES` voiced frames names no pitch or loudness (None), and says so in its voiced share."""
    librosa = require()
    from .audio import resampled

    samples = resampled(waveform, rate, RATE).numpy().astype(np.float32)
    pitch, voiced, _ = librosa.pyin(samples, fmin=LOWEST_HZ, fmax=HIGHEST_HZ, sr=RATE, frame_length=FRAME,
                                    hop_length=HOP)
    loudness = librosa.feature.rms(y=samples, frame_length=FRAME, hop_length=HOP)[0]
    frames = min(len(pitch), len(loudness))
    pitch, voiced, loudness = pitch[:frames], voiced[:frames], loudness[:frames]
    decibels = 20 * np.log10(np.maximum(loudness, 1e-10))
    sounding = voiced & np.isfinite(pitch) & (decibels > decibels.max() - LOUD_DB)
    reading = {"voiced_fraction": round(float(sounding.mean()), 3) if frames else 0.0, "frames": int(frames)}
    if sounding.sum() < FEWEST_FRAMES:
        return {**reading, "pitch_median_hz": None, "pitch_range_semitones": None, "pitch_spread_semitones": None,
                "energy_range_db": None}
    median = float(np.median(pitch[sounding]))
    semitones = 12 * np.log2(pitch[sounding] / median)
    return {**reading, "pitch_median_hz": round(median, 1), "pitch_range_semitones": _span(semitones),
            "pitch_spread_semitones": round(float(np.std(semitones)), 2),
            "energy_range_db": _span(decibels[sounding])}
