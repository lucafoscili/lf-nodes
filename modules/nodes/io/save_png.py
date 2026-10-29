"""Save images as PNG at 8 or 16 bits, rounded to the nearest level, with no metadata."""
import os
from pathlib import Path

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import get_comfy_dir, resolve_filepath, safe_send_sync
from ...utils.helpers.logic import normalize_input_image, normalize_list_to_value
from ...utils.helpers.ui import create_cached_masonry_node
from ...utils.stored_png import BIT_DEPTHS, ROUNDING, from_tensor, sha256, write_png

SCHEMA = "lf.save-png.v1"
CHANNEL_NAMES = {1: "grey", 3: "rgb", 4: "rgba"}


def _scalar(value, name: str):
    if isinstance(value, list) and len(value) != 1:
        raise ValueError(f"{name} takes one value for the whole node; got {len(value)}.")
    result = normalize_list_to_value(value)
    if result is None:
        raise ValueError(f"{name} is required.")
    return result


def _write_atomic(path: Path, data: bytes) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    try:
        temporary.write_bytes(data)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


# region LF_SavePNG
class LF_SavePNG:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Images to save. RGB saves as RGB, RGBA keeps its alpha channel as stored alpha.",
                }),
                "filename_prefix": (Input.STRING, {
                    "default": "LF_Nodes/PNG",
                    "tooltip": "Output-relative path and filename prefix; a counter and .png are added.",
                }),
                "bit_depth": (Input.INTEGER, {
                    "default": 8, "min": 8, "max": 16, "step": 8,
                    "tooltip": "8 or 16 bits per channel. Wire Load PNG's bit_depth here to keep a file's depth.",
                }),
                "compress_level": (Input.INTEGER, {
                    "default": 4, "min": 0, "max": 9,
                    "tooltip": "PNG compression effort, 0 to 9. Lossless at every level: only size and time change.",
                }),
            },
            "optional": {
                "ui_widget": (Input.LF_MASONRY, {"default": {}}),
            },
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    DESCRIPTION = ("Save images as PNG keeping what was computed: each value rounded to the nearest 8 or 16-bit "
                   "level (Core's save truncates), alpha written as alpha, and no prompt or other metadata.")
    FUNCTION = FUNCTION
    INPUT_IS_LIST = True
    OUTPUT_IS_LIST = (True, False)
    OUTPUT_NODE = True
    OUTPUT_TOOLTIPS = (
        "Ordered output-relative PNG filenames.",
        "lf.save-png.v1: each file's size, channels, bit depth and sha256.",
    )
    RETURN_NAMES = ("file_names", "receipt")
    RETURN_TYPES = (Input.STRING, Input.JSON)

    def on_exec(self, **kwargs):
        images = normalize_input_image(kwargs.get("image"))
        if not images:
            raise ValueError("image requires at least one image.")
        filename_prefix = _scalar(kwargs.get("filename_prefix"), "filename_prefix")
        bit_depth = _scalar(kwargs.get("bit_depth"), "bit_depth")
        compress_level = _scalar(kwargs.get("compress_level", 4), "compress_level")
        if isinstance(bit_depth, bool) or bit_depth not in BIT_DEPTHS:
            raise ValueError(f"bit_depth must be 8 or 16, not {bit_depth!r}.")
        encoded = []
        for image in images:
            pixels = from_tensor(image, int(bit_depth))
            encoded.append((write_png(pixels, int(compress_level)), pixels.shape))

        output_root = get_comfy_dir("output")
        file_names, rows, nodes = [], [], []
        for index, ((data, shape), image) in enumerate(zip(encoded, images)):
            output_file, subfolder, filename = resolve_filepath(
                filename_prefix=filename_prefix,
                base_output_path=output_root,
                add_timestamp=False,
                extension="png",
                add_counter=True,
            )
            _write_atomic(Path(output_file), data)
            name = (f"{subfolder}/{filename}" if subfolder else filename).replace("\\", "/")
            file_names.append(name)
            rows.append({"index": index, "file": name, "width": int(shape[1]), "height": int(shape[0]),
                         "channels": CHANNEL_NAMES[shape[2]], "bit_depth": int(bit_depth),
                         "bytes": len(data), "sha256": sha256(data)})
            preview = image[0] if image.ndim == 4 else image
            if preview.shape[-1] == 1:
                preview = preview.expand(-1, -1, 3)
            nodes.append(create_cached_masonry_node(
                preview, index=index, label=f"{filename} | {shape[1]} x {shape[0]} | {bit_depth}-bit"))

        receipt = {"schema": SCHEMA, "rounding": ROUNDING, "metadata": "none", "files": rows}
        payload = {"dataset": {"nodes": nodes}, "file_names": file_names, "receipt": receipt}
        safe_send_sync("savepng", payload, kwargs.get("node_id"))
        return {"ui": {"lf_output": [payload]}, "result": (file_names, receipt)}
# endregion


NODE_CLASS_MAPPINGS = {"LF_SavePNG": LF_SavePNG}
NODE_DISPLAY_NAME_MAPPINGS = {"LF_SavePNG": "Save PNG (stored values)"}
