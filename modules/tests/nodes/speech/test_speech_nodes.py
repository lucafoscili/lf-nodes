"""The Speech nodes' contracts, with the models replaced: schemas, the modes they take, what they refuse, and the
receipts they return. Synthetic tones stand in for speech; no weights or GPU."""

from __future__ import annotations

import math

import numpy as np
import pytest
import torch

from modules.nodes.speech import speech_match, voice_clone_speech, voice_convert
from modules.utils.helpers.speech import models
from modules.utils.helpers.speech.text import word_error_rate, words


def tone(seconds=1.0, rate=16000, channels=1, batch=1):
    samples = torch.arange(int(seconds * rate), dtype=torch.float32)
    wave = 0.1 * torch.sin(2 * math.pi * 220 * samples / rate)
    return {"waveform": wave.repeat(batch, channels, 1), "sample_rate": rate}


def test_schemas_are_published_api():
    clone = voice_clone_speech.LF_VoiceCloneSpeech
    assert list(clone.INPUT_TYPES()["required"]) == [
        "text", "model", "revision", "language", "seed", "num_step", "guidance_scale", "speed"]
    assert list(clone.INPUT_TYPES()["optional"]) == ["reference_audio", "reference_text", "voice_design"]
    assert (clone.RETURN_TYPES, clone.RETURN_NAMES) == (("AUDIO", "JSON"), ("audio", "receipt"))
    convert = voice_convert.LF_VoiceConvert
    assert list(convert.INPUT_TYPES()["required"]) == ["source_audio", "target_audio", "model", "revision"]
    assert (convert.RETURN_TYPES, convert.RETURN_NAMES) == (("AUDIO", "JSON"), ("audio", "receipt"))
    match = speech_match.LF_SpeechMatch
    assert list(match.INPUT_TYPES()["required"]) == [
        "audio", "reference_audio", "expected_text", "language", "speaker_model", "speaker_revision", "asr_model",
        "asr_revision"]
    assert match.RETURN_NAMES == ("speaker_similarity", "transcript", "word_error_rate", "receipt")
    for node in (clone, convert, match):
        assert not getattr(node, "INPUT_IS_LIST", False)
        assert len(node.RETURN_TYPES) == len(node.OUTPUT_TOOLTIPS)


@pytest.fixture
def spoken(monkeypatch):
    calls = []

    def speak(text, **options):
        calls.append((text, options))
        return np.full(2400, 0.05, dtype=np.float32), 24000, {"load_seconds": 1.0, "run_seconds": 0.5}

    monkeypatch.setattr(models, "omnivoice_speak", speak)
    return calls


def test_clone_reads_the_reference_and_its_transcript(spoken):
    node = voice_clone_speech.LF_VoiceCloneSpeech()
    audio, receipt = node.on_exec("Say this.", "k2-fsa/OmniVoice", "abc123", "English", 7, 32, 2.0, 0.0,
                                  reference_audio=tone(2.0, channels=2), reference_text="What the clip says.")
    assert audio["waveform"].shape == (1, 1, 2400) and audio["sample_rate"] == 24000
    text, options = spoken[0]
    assert text == "Say this." and options["reference_text"] == "What the clip says." and options["design"] == ""
    reference, rate = options["reference"]
    assert reference.ndim == 1 and rate == 16000
    assert receipt["mode"] == "clone" and receipt["revision"] == "abc123" and receipt["seed"] == 7
    assert receipt["reference_seconds"] == 2.0 and receipt["seconds"] == 0.1 and receipt["speed"] is None


def test_design_needs_no_reference(spoken):
    node = voice_clone_speech.LF_VoiceCloneSpeech()
    _, receipt = node.on_exec("Say this.", "k2-fsa/OmniVoice", "abc123", "", 0, 16, 1.5, 1.1,
                              voice_design="female, low pitch")
    assert receipt["mode"] == "design" and receipt["voice_design"] == "female, low pitch"
    assert receipt["language"] is None and spoken[0][1]["reference"] is None


@pytest.mark.parametrize("change, message", [
    (dict(text="  "), "nothing to say"),
    (dict(revision=""), "needs a revision"),
    (dict(model="someone/else"), "is not one of"),
    (dict(reference_text=""), "transcript"),
    (dict(voice_design="female"), "not both"),
    (dict(reference_audio=None), "or a voice design"),
    (dict(reference_audio=tone(batch=2)), "join them"),
])
def test_clone_refuses_what_it_cannot_honour(spoken, change, message):
    inputs = dict(text="Say this.", model="k2-fsa/OmniVoice", revision="abc123", language="English", seed=0,
                  num_step=32, guidance_scale=2.0, speed=0.0, reference_audio=tone(), reference_text="Clip.")
    inputs.update(change)
    with pytest.raises(ValueError, match=message):
        voice_clone_speech.LF_VoiceCloneSpeech().on_exec(**inputs)
    assert not spoken


def test_convert_keeps_the_source_and_reads_the_target(monkeypatch):
    seen = {}

    def convert(source, source_rate, target, target_rate, *, revision):
        seen.update(source=source.shape, target=target.shape, rates=(source_rate, target_rate), revision=revision)
        return torch.full((4800,), 0.02), 24000, {"load_seconds": 2.0, "run_seconds": 0.3,
                                                  "target_seconds_read": 3.0, "watermark": "perth-implicit"}

    monkeypatch.setattr(models, "chatterbox_convert", convert)
    audio, receipt = voice_convert.LF_VoiceConvert().on_exec(tone(1.0), tone(3.0, rate=22050), "ResembleAI/chatterbox",
                                                             "def456")
    assert seen == dict(source=(16000,), target=(66150,), rates=(16000, 22050), revision="def456")
    assert audio["waveform"].shape == (1, 1, 4800)
    assert receipt["source_seconds"] == 1.0 and receipt["target_seconds"] == 3.0 and receipt["seconds"] == 0.2
    assert receipt["watermark"] == "perth-implicit"


def test_match_measures_voice_and_words(monkeypatch):
    monkeypatch.setattr(models, "speaker_similarity", lambda *args, **kwargs: (0.8123, {"seconds": 0.4}))
    monkeypatch.setattr(models, "transcribe", lambda *args, **kwargs: ("Anna, you're late.", {"seconds": 0.9}))
    similarity, transcript, error_rate, receipt = speech_match.LF_SpeechMatch().on_exec(
        tone(), tone(2.0), "Anna, you are late!", "english", "microsoft/wavlm-base-plus-sv", "r1",
        "openai/whisper-large-v3-turbo", "r2")
    assert (similarity, transcript) == (0.8123, "Anna, you're late.")
    assert error_rate == 0.5  # "you're" for "you are": one substitution, one deletion of four words
    assert receipt["speaker_revision"] == "r1" and receipt["asr_revision"] == "r2" and receipt["reference_seconds"] == 2.0


def test_match_refuses_an_empty_text():
    with pytest.raises(ValueError, match="no text"):
        speech_match.LF_SpeechMatch().on_exec(tone(), tone(), " ", "english", "microsoft/wavlm-base-plus-sv", "r1",
                                              "openai/whisper-large-v3-turbo", "r2")


def test_words_and_error_rate():
    assert words("It’s  DONE, isn't it?") == ["it's", "done", "isn't", "it"]
    assert word_error_rate("Lead the way.", "lead the way") == 0.0
    assert word_error_rate("Lead the way.", "lead way then") == round(2 / 3, 4)
    with pytest.raises(ValueError, match="no words"):
        word_error_rate("...", "anything")
