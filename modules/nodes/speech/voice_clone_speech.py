"""Text to speech in a cloned or designed voice (OmniVoice): a reference recording and its transcript give the voice
to clone; without one, a few attributes describe the voice to design."""

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.speech import models
from ...utils.helpers.speech.audio import mono, seconds, to_audio

RECEIPT_SCHEMA = "lf.voice_clone_speech.receipt.v1"


class LF_VoiceCloneSpeech:
    @classmethod
    def INPUT_TYPES(cls):
        speakers = list(models.SPEAKERS)
        return {
            "required": {
                "text": (Input.STRING, {"multiline": True, "default": "",
                                        "tooltip": "What the voice says."}),
                "model": (speakers, {"default": speakers[0], "tooltip": "The text-to-speech model."}),
                "revision": (Input.STRING, {"default": models.SPEAKERS[speakers[0]],
                                            "tooltip": "The model repository's commit, fetched once into the Hugging Face cache."}),
                "language": (Input.STRING, {"default": "English",
                                            "tooltip": "The text's language (a name or a code); empty lets the model guess."}),
                "seed": (Input.INTEGER, {"default": 0, "min": 0, "max": 2**32 - 1}),
                "num_step": (Input.INTEGER, {"default": 32, "min": 4, "max": 128,
                                             "tooltip": "Iterative decoding steps."}),
                "guidance_scale": (Input.FLOAT, {"default": 2.0, "min": 0.0, "max": 10.0, "step": 0.1,
                                                 "tooltip": "Classifier-free guidance toward the text and the voice."}),
                "speed": (Input.FLOAT, {"default": 0.0, "min": 0.0, "max": 3.0, "step": 0.05,
                                        "tooltip": "Speaking rate; 0 lets the model estimate it from the text."}),
            },
            "optional": {
                "reference_audio": (Input.AUDIO, {"tooltip": "One recording of the voice to clone (a few seconds)."}),
                "reference_text": (Input.STRING, {"multiline": True, "default": "",
                                                  "tooltip": "Exactly what the reference recording says."}),
                "voice_design": (Input.STRING, {"default": "",
                                                "tooltip": "Without a reference: comma-separated attributes of the voice "
                                                           "to design (female, young adult, low pitch, british accent...)."}),
            },
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    RETURN_TYPES = (Input.AUDIO, Input.JSON)
    RETURN_NAMES = ("audio", "receipt")
    OUTPUT_TOOLTIPS = (
        "The speech, mono at the model's rate.",
        "What made it: model and revision, the mode (clone or design), the seed and settings, lengths and timings.",
    )

    def on_exec(self, text, model, revision, language, seed, num_step, guidance_scale, speed,
                reference_audio=None, reference_text="", voice_design="", **kwargs):
        if not isinstance(text, str) or not text.strip():
            raise ValueError("text is empty: there is nothing to say.")
        revision = models.revision_of(models.SPEAKERS, model, revision)
        design = (voice_design or "").strip()
        reference = None
        if reference_audio is not None:
            if design:
                raise ValueError("Give a reference recording or a voice design, not both.")
            if not (reference_text or "").strip():
                raise ValueError("reference_text is empty: the clone needs the reference recording's transcript.")
            reference = mono(reference_audio, name="reference_audio")
        elif not design:
            raise ValueError("Give a reference recording (with its transcript) to clone, or a voice design.")
        waveform, rate, timings = models.omnivoice_speak(
            text.strip(), revision=revision, language=(language or "").strip(), seed=int(seed), num_step=int(num_step),
            guidance_scale=float(guidance_scale), speed=float(speed), reference=reference,
            reference_text=(reference_text or "").strip(), design=design)
        audio = to_audio(waveform, rate)
        receipt = {
            "schema": RECEIPT_SCHEMA, "model": model, "revision": revision,
            "mode": "clone" if reference is not None else "design", "text": text.strip(),
            "language": (language or "").strip() or None, "seed": int(seed), "num_step": int(num_step),
            "guidance_scale": float(guidance_scale), "speed": float(speed) or None,
            "reference_seconds": seconds(*reference) if reference is not None else None,
            "voice_design": design or None, "sample_rate": rate,
            "seconds": seconds(audio["waveform"], rate), **timings,
        }
        return (audio, receipt)


NODE_CLASS_MAPPINGS = {"LF_VoiceCloneSpeech": LF_VoiceCloneSpeech}
NODE_DISPLAY_NAME_MAPPINGS = {"LF_VoiceCloneSpeech": "Voice clone speech"}
