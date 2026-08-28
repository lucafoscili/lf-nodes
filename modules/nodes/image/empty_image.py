import re

from PIL import Image

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.conversion import hex_to_tuple, pil_to_tensor
from ...utils.helpers.logic import normalize_input_list, normalize_output_image
from ...utils.helpers.ui import create_cached_masonry_node

# region LF_EmptyImage
class LF_EmptyImage:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": (Input.INTEGER, {
                    "default": 1024,
                    "min": 64,
                    "max": 8192,
                    "step": 64,
                    "tooltip": "Width of the empty image."
                }),
                "height": (Input.INTEGER, {
                    "default": 512,
                    "min": 1,
                    "max": 4096,
                    "step": 1,
                    "tooltip": "Height of the empty image."
                }),
                "color": (Input.STRING, {
                    "default": "000000",
                    "tooltip": "Color of the empty image. Format: RRGGBB (hexadecimal)."
                }),
            },
            "optional": {
                "ui_widget": (Input.LF_MASONRY, {
                    "default": {}
                })
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    INPUT_IS_LIST = True
    OUTPUT_IS_LIST = (False, True)
    OUTPUT_TOOLTIPS = (
        "Generated empty image tensor.",
        "List of generated empty image tensors."
    )
    RETURN_NAMES = ("image", "image_list")
    RETURN_TYPES = (Input.IMAGE, Input.IMAGE)

    def on_exec(self, **kwargs: dict):
        width: list[int] = normalize_input_list(kwargs.get("width"))
        height: list[int] = normalize_input_list(kwargs.get("height"))
        color: list[int] = normalize_input_list(kwargs.get("color"))

        nodes: list[dict] = []
        dataset: dict = { "nodes": nodes }

        if len(width) != len(height) or len(width) != len(color):
            raise ValueError("Width, height, and color lists must have the same length.")

        empty_images = []

        for w, h, c in zip(width, height, color):
            if not isinstance(c, str) or not re.fullmatch(r"[0-9A-Fa-f]{6}", c):
                raise ValueError("Color must be a hexadecimal string in the format RRGGBB.")

            rgb = hex_to_tuple(c)
            pil_image = Image.new("RGB", (w, h), rgb)
            empty_image_tensor = pil_to_tensor(pil_image)

            nodes.append(
                create_cached_masonry_node(
                    empty_image_tensor,
                    index=len(empty_images),
                    label=f"{w}×{h} #{c.upper()}",
                )
            )

            empty_images.append(empty_image_tensor)

        image_batch, image_list = normalize_output_image(empty_images)

        payload = {"dataset": dataset}
        safe_send_sync("emptyimage", payload, kwargs.get("node_id"))

        return {
            "ui": {"lf_output": [payload]},
            "result": (image_batch[0], image_list),
        }
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_EmptyImage": LF_EmptyImage,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_EmptyImage": "Empty image",
}
# endregion
