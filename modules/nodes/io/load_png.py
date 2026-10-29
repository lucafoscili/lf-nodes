"""Load a PNG as its stored values: 8 or 16 bits, alpha a plain channel."""
import os

import torch

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.ui import create_cached_masonry_node
from ...utils.stored_png import ROUNDING, read_png, sha256, to_tensor

SCHEMA = "lf.load-png.v1"


def _folder_paths():
    import folder_paths  # Comfy's own resolver for "name.png [input]" references.

    return folder_paths


def _input_pngs() -> list[str]:
    try:
        directory = _folder_paths().get_input_directory()
        names = os.listdir(directory)
    except (OSError, TypeError):
        return []
    return sorted(name for name in names
                  if name.lower().endswith(".png") and os.path.isfile(os.path.join(directory, name)))


def _exists(image) -> bool:
    if not isinstance(image, str) or not image.strip():
        return False
    if os.path.isabs(image):
        return os.path.isfile(image)
    return bool(_folder_paths().exists_annotated_filepath(image))


def _resolve(image: str) -> str:
    """A Comfy reference (``name.png``, ``sub/name.png [output]``) or an absolute file path."""
    if not _exists(image):
        raise ValueError(f"Invalid image file: {image}")
    return image if os.path.isabs(image) else _folder_paths().get_annotated_filepath(image)


# region LF_LoadPNG
class LF_LoadPNG:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (_input_pngs(), {
                    "image_upload": True,
                    "tooltip": ("PNG to load from ComfyUI's input (or an annotated temp/output reference, or an absolute "
                                "path). Its stored values are kept: 8 or 16 bits, alpha as a channel."),
                }),
            },
            "optional": {
                "ui_widget": (Input.LF_MASONRY, {"default": {}}),
            },
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    DESCRIPTION = ("Load a PNG without changing its values: 8 or 16-bit, alpha kept as the image's fourth channel "
                   "(and as an uninverted mask), no colour management, orientation or gamma.")
    FUNCTION = FUNCTION
    OUTPUT_IS_LIST = (False, False, False, False, True)
    RETURN_NAMES = ("image", "alpha", "bit_depth", "receipt", "image_list")
    RETURN_TYPES = (Input.IMAGE, Input.MASK, Input.INTEGER, Input.JSON, Input.IMAGE)
    OUTPUT_TOOLTIPS = (
        "The image in 0..1: RGB, or RGBA when the file stores alpha; grey is widened to RGB.",
        "The stored alpha as a mask, not inverted (1 is opaque); all ones when the file has no alpha.",
        "The file's bit depth, 8 or 16: wire it into Save PNG to write the same depth back.",
        "lf.load-png.v1: the file, its size, colour type, bit depth and sha256.",
        "The same image as a one-item list.",
    )

    def on_exec(self, image: str, **kwargs):
        path = _resolve(image)
        with open(path, "rb") as stream:
            data = stream.read()
        pixels, header = read_png(data)
        tensor = to_tensor(pixels)
        has_alpha = pixels.shape[2] in (2, 4)
        alpha = tensor[..., 3].clone() if has_alpha else torch.ones(tensor.shape[:3], dtype=torch.float32)
        bit_depth = 16 if pixels.dtype.itemsize == 2 else 8
        receipt = {
            "schema": SCHEMA,
            "file": image,
            "width": header["width"],
            "height": header["height"],
            "color_type": header["color_type"],
            "file_bit_depth": header["bit_depth"],
            "bit_depth": bit_depth,
            "channels": int(tensor.shape[-1]),
            "alpha": has_alpha,
            "scale": 255 if bit_depth == 8 else 65535,
            "rounding_on_save": ROUNDING,
            "sha256": sha256(data),
        }
        title = (f"{os.path.basename(path)} | {header['width']} x {header['height']} | {bit_depth}-bit "
                 f"{header['color_type']}")
        dataset = {"nodes": [create_cached_masonry_node(tensor, index=0, label=title)]}
        payload = {"dataset": dataset, "receipt": receipt}
        safe_send_sync("loadpng", payload, kwargs.get("node_id"))
        return {"ui": {"lf_output": [payload]}, "result": (tensor, alpha, bit_depth, receipt, [tensor])}

    @classmethod
    def IS_CHANGED(cls, image, **_kwargs):
        with open(_resolve(image), "rb") as stream:
            return sha256(stream.read())

    @classmethod
    def VALIDATE_INPUTS(cls, image, **_kwargs):
        if not _exists(image):
            return f"Invalid image file: {image}"
        return True
# endregion


NODE_CLASS_MAPPINGS = {"LF_LoadPNG": LF_LoadPNG}
NODE_DISPLAY_NAME_MAPPINGS = {"LF_LoadPNG": "Load PNG (stored values)"}
