"""The Speech nodes' contracts, with the models replaced: schemas, the modes they take, what they refuse, and the
receipts they return. Synthetic tones stand in for speech; no weights or GPU."""

from __future__ import annotations

import math
import sys

import numpy as np
import pytest
import torch

from modules.nodes.speech import speech_match, voice_clone_speech, voice_convert
from modules.utils.helpers.speech import models, prosody
from modules.utils.helpers.speech.text import word_error_rate, words


def tone(seconds=1.0, rate=16000, channels=1, batch=1):
    samples = torch.arange(int(seconds * rate), dtype=torch.float32)
    wave = 0.1 * torch.sin(2 * math.pi * 220 * samples / rate)
    return {"waveform": wave.repeat(batch, channels, 1), "sample_rate": rate}


def test_schemas_are_published_api():
    clone = voice_clone_speech.LF_VoiceCloneSpeech
    assert list(clone.INPUT_TYPES()["required"]) == [
        "text", "model", "revision", "language", "seed", "num_step", "guidance_scale", "speed"]
    assert list(clone.INPUT_TYPES()["optional"]) == [
        "reference_audio", "reference_text", "voice_design", "t_shift"]
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
    assert options["t_shift"] == receipt["t_shift"] == 0.1, "the model's own default when none is given"


def test_clone_decodes_on_the_shift_asked_and_says_so(spoken):
    node = voice_clone_speech.LF_VoiceCloneSpeech()
    _, receipt = node.on_exec("Say this.", "k2-fsa/OmniVoice", "abc123", "English", 7, 32, 2.0, 0.0,
                              reference_audio=tone(), reference_text="Clip.", t_shift=0.5)
    assert spoken[0][1]["t_shift"] == receipt["t_shift"] == 0.5


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
    (dict(t_shift=0.0), "t_shift"),
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
    assert receipt["prosody"]["pitch_median_hz"] == pytest.approx(220, abs=3), "the recording's own delivery"


def pitched(*parts, rate=16000):
    """Tones played one after another: (seconds, hertz, amplitude) each; hertz 0 is silence."""
    waves = []
    for length, hertz, amplitude in parts:
        samples = torch.arange(int(length * rate), dtype=torch.float32)
        waves.append(amplitude * torch.sin(2 * math.pi * hertz * samples / rate) if hertz else 0 * samples)
    return torch.cat(waves), rate


def test_prosody_reads_pitch_and_loudness_from_voiced_frames():
    steady = prosody.prosody(*pitched((1.0, 220, 0.3)))
    assert steady["pitch_median_hz"] == pytest.approx(220, abs=3)
    assert steady["pitch_range_semitones"] < 0.5 and steady["voiced_fraction"] > 0.8
    octave = prosody.prosody(*pitched((0.6, 220, 0.3), (0.6, 440, 0.3)))
    assert octave["pitch_range_semitones"] == pytest.approx(12, abs=1)
    assert octave["pitch_spread_semitones"] == pytest.approx(6, abs=1)
    softer = prosody.prosody(*pitched((0.6, 220, 0.3), (0.6, 220, 0.03)))
    assert softer["energy_range_db"] == pytest.approx(20, abs=3) and softer["pitch_range_semitones"] < 0.5
    paused = prosody.prosody(*pitched((0.5, 220, 0.3), (0.5, 0, 0), (0.5, 220, 0.3)))
    assert paused["voiced_fraction"] == pytest.approx(2 / 3, abs=0.1), "a pause is not voiced"
    assert paused["energy_range_db"] < 6, "silence is not a quiet syllable (frames astride an edge read 3 to 6 dB down)"


def test_prosody_of_a_recording_without_voice_names_no_pitch():
    silent = prosody.prosody(*pitched((1.0, 0, 0)))
    assert silent["voiced_fraction"] == 0 and silent["pitch_median_hz"] is None
    assert silent["pitch_range_semitones"] is None and silent["energy_range_db"] is None


def test_match_without_librosa_refuses_before_any_model_runs(monkeypatch):
    ran = []
    monkeypatch.setattr(models, "speaker_similarity", lambda *args, **kwargs: ran.append("speaker"))
    monkeypatch.setattr(models, "transcribe", lambda *args, **kwargs: ran.append("asr"))
    monkeypatch.setitem(sys.modules, "librosa", None)  # its import fails, as where it is not installed
    with pytest.raises(RuntimeError, match="librosa"):
        speech_match.LF_SpeechMatch().on_exec(tone(), tone(), "Say this.", "english", "microsoft/wavlm-base-plus-sv",
                                              "r1", "openai/whisper-large-v3-turbo", "r2")
    assert ran == [], "no model loads for a measure it cannot finish"


def test_match_refuses_an_empty_text():
    with pytest.raises(ValueError, match="no text"):
        speech_match.LF_SpeechMatch().on_exec(tone(), tone(), " ", "english", "microsoft/wavlm-base-plus-sv", "r1",
                                              "openai/whisper-large-v3-turbo", "r2")


def test_words_and_error_rate():
    assert words("It’s  DONE, isn't it?") == ["it's", "done", "isn't", "it"]
    assert word_error_rate("Follow the river.", "follow the river") == 0.0
    assert word_error_rate("Follow the river.", "follow river now") == round(2 / 3, 4)
    with pytest.raises(ValueError, match="no words"):
        word_error_rate("...", "anything")


def test_every_model_has_its_room_and_a_load_that_leaves_weights_out_is_refused() -> None:
    families = {**models.SPEAKERS, **models.CONVERTERS, **models.SPEAKER_ENCODERS, **models.RECOGNIZERS}
    assert set(families) == set(models._ROOM), "each model frees its room before it loads"

    class Report:
        def __init__(self, missing, unexpected=()):
            self.missing_keys, self.unexpected_keys = list(missing), list(unexpected)

    models.loaded_whole(Report(["tokenizer.window"]), models.S3GEN_BUILT, "a/converter")
    with pytest.raises(RuntimeError, match="missing \\['flow.decoder'\\]"):
        models.loaded_whole(Report(["tokenizer.window", "flow.decoder"]), models.S3GEN_BUILT, "a/converter")
    with pytest.raises(RuntimeError, match="unexpected"):
        models.loaded_whole(Report([], ["extra"]), models.S3GEN_BUILT, "a/converter")


def test_a_run_lets_go_of_a_model_caught_in_a_cycle(monkeypatch) -> None:
    """A model whose modules refer back to each other (as WavLM's do) outlives `del` until the garbage collector
    runs; the GPU's cache is emptied after the run, so the run collects first (17 November 2026: 54 measures left
    22 GB of a 24 GB card allocated and the next run out of memory)."""
    import gc
    import weakref

    from comfy import model_management

    emptied = []
    for name, value in dict(get_torch_device=lambda: torch.device("cpu"), free_memory=lambda *args: None,
                            minimum_inference_memory=lambda: 0,
                            soft_empty_cache=lambda: emptied.append(gone() is None)).items():
        monkeypatch.setattr(model_management, name, value, raising=False)

    class Model:
        pass

    gc.disable()
    try:
        with models.running("microsoft/wavlm-base-plus-sv"):
            model = Model()
            model.me = model
            gone = weakref.ref(model)
            del model
        assert emptied == [True], "the run let go of its model before emptying the cache"
    finally:
        gc.enable()


def test_a_run_clears_the_method_caches_that_keep_its_model() -> None:
    """A method cached with functools.lru_cache keeps every instance it was called on, so a model whose class (or a
    class it derives from) caches a method outlives the run (17 November 2026: transformers 5.10's Higgs audio
    tokenizer caches `_get_conv1d_layers` on its base class, and each OmniVoice line kept 0.75 GB of the GPU)."""
    import functools
    import gc
    import weakref

    class Base(torch.nn.Module):
        @functools.lru_cache
        def layers(self, module):
            return [module]

    class Tokenizer(Base):
        pass

    class Model(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.tokenizer = Tokenizer()

    model = Model()
    model.tokenizer.layers(model.tokenizer)
    gone = weakref.ref(model.tokenizer)
    models.let_go(model)
    del model
    gc.collect()
    assert gone() is None, "the cache let go of the model's tokenizer"
