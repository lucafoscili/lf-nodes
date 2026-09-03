"""Save a Comfy AUDIO batch as unmodified float32 WAV files."""

from pathlib import Path

from . import CATEGORY
from ...utils.audio import encode_float_wav, normalize_audio, validate_audio_prefix, write_audio_file
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import get_comfy_dir, resolve_filepath, safe_send_sync


AUDIO_FILE_RECEIPT_SCHEMA = "lf.audio_file.receipt.v1"


class LF_SaveAudio:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio": (Input.AUDIO, {"tooltip": "Mono or stereo AUDIO batch; each item becomes one WAV file."}),
                "filename_prefix": (Input.STRING, {
                    "default": "audio/ComfyUI",
                    "tooltip": "Output-relative path and filename prefix. WAV files receive a collision-safe counter.",
                }),
            },
            "optional": {"ui_widget": (Input.LF_MASONRY, {"default": {}})},
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_NODE = True
    RETURN_TYPES = (Input.STRING, Input.JSON)
    RETURN_NAMES = ("output_reference", "receipt")
    OUTPUT_IS_LIST = (True, False)
    OUTPUT_TOOLTIPS = (
        "Ordered WAV references relative to ComfyUI output, annotated with [output].",
        "Batch receipt containing saved filenames, sample rates, channel counts, durations, and byte lengths.",
    )

    def on_exec(self, audio, filename_prefix="audio/ComfyUI", **kwargs):
        waveform, sample_rate = normalize_audio(audio)
        output_root = Path(get_comfy_dir("output")).resolve()
        filename_prefix = validate_audio_prefix(filename_prefix, output_root)
        references = []
        files = []
        descriptors = []
        for index, item in enumerate(waveform):
            data = encode_float_wav(item, sample_rate)
            output_file, _, _ = resolve_filepath(
                filename_prefix=filename_prefix,
                base_output_path=str(output_root),
                add_timestamp=False,
                extension="wav",
                add_counter=True,
            )
            output_path = Path(output_file).resolve()
            try:
                relative_name = output_path.relative_to(output_root).as_posix()
            except ValueError as error:
                raise ValueError("Audio output path must remain inside ComfyUI output.") from error
            write_audio_file(output_path, data)
            references.append(f"{relative_name} [output]")
            files.append({
                "index": index,
                "file_name": relative_name,
                "storage_type": "output",
                "format": "wav",
                "encoding": "pcm_f32le",
                "sample_rate": sample_rate,
                "channels": item.shape[0],
                "samples": item.shape[1],
                "duration_seconds": item.shape[1] / sample_rate,
                "byte_length": len(data),
            })
            descriptors.append({
                "filename": output_path.name,
                "subfolder": "" if output_path.parent == output_root else output_path.parent.relative_to(output_root).as_posix(),
                "type": "output",
            })
        receipt = {"schema": AUDIO_FILE_RECEIPT_SCHEMA, "files": files}
        payload = {"audio": descriptors, "file_names": [item["file_name"] for item in files], "receipt": receipt}
        safe_send_sync("saveaudio", payload, kwargs.get("node_id"))
        return {"ui": {"audio": descriptors, "lf_output": [payload]}, "result": (references, receipt)}


NODE_CLASS_MAPPINGS = {"LF_SaveAudio": LF_SaveAudio}
NODE_DISPLAY_NAME_MAPPINGS = {"LF_SaveAudio": "Save Audio (WAV)"}
