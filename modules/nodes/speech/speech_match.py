"""How close a recording is to a voice and to its text: the cosine of the two voices' speaker embeddings (WavLM), and
the word error rate of what Whisper hears against the text it should say; and how the recording moves, its pitch and
loudness ranges (its prosody, in the receipt)."""

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.speech import models, prosody
from ...utils.helpers.speech.audio import mono, seconds
from ...utils.helpers.speech.text import word_error_rate

RECEIPT_SCHEMA = "lf.speech_match.receipt.v1"


class LF_SpeechMatch:
    @classmethod
    def INPUT_TYPES(cls):
        encoders, recognizers = list(models.SPEAKER_ENCODERS), list(models.RECOGNIZERS)
        return {
            "required": {
                "audio": (Input.AUDIO, {"tooltip": "The recording to measure."}),
                "reference_audio": (Input.AUDIO, {"tooltip": "A recording of the voice it should be."}),
                "expected_text": (Input.STRING, {"multiline": True, "default": "",
                                                 "tooltip": "What the recording should say."}),
                "language": (Input.STRING, {"default": "english",
                                            "tooltip": "The language Whisper transcribes; empty lets it detect one."}),
                "speaker_model": (encoders, {"default": encoders[0], "tooltip": "The speaker embedding model."}),
                "speaker_revision": (Input.STRING, {"default": models.SPEAKER_ENCODERS[encoders[0]]}),
                "asr_model": (recognizers, {"default": recognizers[0], "tooltip": "The speech recognition model."}),
                "asr_revision": (Input.STRING, {"default": models.RECOGNIZERS[recognizers[0]]}),
            },
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    RETURN_TYPES = (Input.FLOAT, Input.STRING, Input.FLOAT, Input.JSON)
    RETURN_NAMES = ("speaker_similarity", "transcript", "word_error_rate", "receipt")
    OUTPUT_TOOLTIPS = (
        "Cosine of the two recordings' speaker embeddings: 1 is the same voice.",
        "What the speech recognition model heard.",
        "Word edits from the expected text to the transcript, per expected word: 0 is every word said.",
        "Both measures with the models, revisions, lengths and timings that made them, and the recording's prosody: "
        "its pitch median, range and spread, its loudness range and its voiced share.",
    )

    def on_exec(self, audio, reference_audio, expected_text, language, speaker_model, speaker_revision, asr_model,
                asr_revision, **kwargs):
        if not isinstance(expected_text, str) or not expected_text.strip():
            raise ValueError("expected_text is empty: there is no text to measure the recording against.")
        prosody.require()
        speaker_revision = models.revision_of(models.SPEAKER_ENCODERS, speaker_model, speaker_revision)
        asr_revision = models.revision_of(models.RECOGNIZERS, asr_model, asr_revision)
        heard, heard_rate = mono(audio, name="audio")
        voice, voice_rate = mono(reference_audio, name="reference_audio")
        similarity, speaker_timing = models.speaker_similarity(heard, heard_rate, voice, voice_rate,
                                                               repo=speaker_model, revision=speaker_revision)
        transcript, asr_timing = models.transcribe(heard, heard_rate, repo=asr_model, revision=asr_revision,
                                                   language=(language or "").strip())
        error_rate = word_error_rate(expected_text, transcript)
        receipt = {
            "schema": RECEIPT_SCHEMA, "speaker_similarity": similarity, "transcript": transcript,
            "expected_text": expected_text.strip(), "word_error_rate": error_rate,
            "speaker_model": speaker_model, "speaker_revision": speaker_revision,
            "asr_model": asr_model, "asr_revision": asr_revision, "language": (language or "").strip() or None,
            "seconds": seconds(heard, heard_rate), "reference_seconds": seconds(voice, voice_rate),
            "speaker_seconds": speaker_timing["seconds"], "asr_seconds": asr_timing["seconds"],
            "prosody": prosody.prosody(heard, heard_rate),
        }
        return (similarity, transcript, error_rate, receipt)


NODE_CLASS_MAPPINGS = {"LF_SpeechMatch": LF_SpeechMatch}
NODE_DISPLAY_NAME_MAPPINGS = {"LF_SpeechMatch": "Speech match"}
