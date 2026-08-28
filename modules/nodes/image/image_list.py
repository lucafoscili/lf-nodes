from __future__ import annotations

from typing import Any

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import normalize_input_image, normalize_list_to_value
from ...utils.helpers.ui import create_cached_masonry_node


_MAX_IMAGES = 16
_IMAGE_INPUTS = tuple(f"image_{index}" for index in range(1, _MAX_IMAGES + 1))


class LF_ImageList:
    """Collect independently sized image inputs into one ordered Comfy list."""

    @classmethod
    def INPUT_TYPES(cls):
        image_input = (
            Input.IMAGE,
            {
                "tooltip": (
                    "Image or image batch to append without resizing. Inputs are "
                    "flattened in numeric order."
                )
            },
        )
        return {
            "required": {"image_1": image_input},
            "optional": {
                **{
                    name: image_input
                    for name in _IMAGE_INPUTS
                    if name != "image_1"
                },
                "ui_widget": (Input.LF_MASONRY, {"default": {}}),
            },
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    INPUT_IS_LIST = True
    OUTPUT_IS_LIST = (True,)
    OUTPUT_NODE = True
    OUTPUT_TOOLTIPS = (
        "Ordered image list. Original dimensions, channels, dtype, and pixel values are preserved.",
    )
    RETURN_NAMES = ("images",)
    RETURN_TYPES = (Input.IMAGE,)

    def on_exec(self, **kwargs: Any):
        images = []
        for name in _IMAGE_INPUTS:
            value = kwargs.get(name)
            if value is None:
                continue
            images.extend(normalize_input_image(value))
        if not images:
            raise ValueError("image_1 must contain at least one image.")

        nodes: list[dict] = []
        dataset = {"nodes": nodes}
        for index, image in enumerate(images):
            nodes.append(
                create_cached_masonry_node(
                    image,
                    index=index,
                    label=f"Image {index + 1}",
                )
            )

        node_id = normalize_list_to_value(kwargs.get("node_id"))
        safe_send_sync("imagelist", {"dataset": dataset}, node_id)
        return {
            "ui": {"lf_output": [{"dataset": dataset}]},
            "result": (images,),
        }


NODE_CLASS_MAPPINGS = {
    "LF_ImageList": LF_ImageList,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_ImageList": "Images to list",
}
