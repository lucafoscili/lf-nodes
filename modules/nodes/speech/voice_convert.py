"""Voice conversion (Chatterbox): a spoken recording's words and timing, said again in a target recording's voice."""

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.speech import models
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.speech.audio import mono, seconds, to_audio
from ...utils.helpers.ui import cache_generated_audio

RECEIPT_SCHEMA = "lf.voice_convert.receipt.v1"


class LF_VoiceConvert:
    @classmethod
    def INPUT_TYPES(cls):
        converters = list(models.CONVERTERS)
        return {
            "required": {
                "source_audio": (Input.AUDIO, {"tooltip": "The spoken recording whose words and timing are kept."}),
                "target_audio": (Input.AUDIO, {"tooltip": "A recording of the voice to speak in; the model reads its "
                                                          f"first {models.CHATTERBOX_REFERENCE_SECONDS:g} seconds."}),
                "model": (converters, {"default": converters[0], "tooltip": "The voice conversion model."}),
                "revision": (Input.STRING, {"default": models.CONVERTERS[converters[0]],
                                            "tooltip": "The model repository's commit, fetched once into the Hugging Face cache."}),
            },
            "optional": {"ui_widget": (Input.LF_MASONRY, {"default": {}})},
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    RETURN_TYPES = (Input.AUDIO, Input.JSON)
    RETURN_NAMES = ("audio", "receipt")
    OUTPUT_TOOLTIPS = (
        "The converted speech, mono at the model's rate, watermarked as the model's own conversion is.",
        "What made it: model and revision, the lengths read and written, timings and the watermark.",
    )

    def on_exec(self, source_audio, target_audio, model, revision, **kwargs):
        revision = models.revision_of(models.CONVERTERS, model, revision)
        source, source_rate = mono(source_audio, name="source_audio")
        target, target_rate = mono(target_audio, name="target_audio")
        waveform, rate, details = models.chatterbox_convert(source, source_rate, target, target_rate, revision=revision)
        audio = to_audio(waveform, rate)
        receipt = {
            "schema": RECEIPT_SCHEMA, "model": model, "revision": revision, "sample_rate": rate,
            "source_seconds": seconds(source, source_rate), "target_seconds": seconds(target, target_rate),
            "seconds": seconds(audio["waveform"], rate), **details,
        }
        payload = {"audio": [cache_generated_audio(audio, label=f"Converted, {receipt['seconds']:g} s")],
                   "receipt": receipt}
        safe_send_sync("voiceconvert", payload, kwargs.get("node_id"))
        return {"ui": {"lf_output": [payload]}, "result": (audio, receipt)}


NODE_CLASS_MAPPINGS = {"LF_VoiceConvert": LF_VoiceConvert}
NODE_DISPLAY_NAME_MAPPINGS = {"LF_VoiceConvert": "Voice convert"}
