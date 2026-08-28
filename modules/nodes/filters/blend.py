import torch

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.constants import BLEND_MODE_COMBO
from ...utils.filters import blend_effect
from ...utils.helpers.logic import normalize_input_image, normalize_list_to_value, normalize_output_image
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.ui import create_cached_compare_node

# region LF_Blend
class LF_Blend:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "The base image to blend with."
                }),
                "overlay_image": (Input.IMAGE, {
                    "tooltip": "The overlay image to blend onto the base image."
                }),
                "opacity": (Input.FLOAT, {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "tooltip": "Opacity of the overlay. 0 means invisible, 1 means fully opaque."
                }),
                "blend_mode": (BLEND_MODE_COMBO, {
                    "default": "normal",
                    "tooltip": "Pixel blend mode to use when combining base and overlay images."
                }),
            },
            "optional": {
                "ui_widget": (Input.LF_COMPARE, {
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
        "Blended image tensor.",
        "List of blended image tensors."
    )
    RETURN_NAMES = ("image", "image_list")
    RETURN_TYPES = (Input.IMAGE, Input.IMAGE)

    def on_exec(self, **kwargs: dict):
        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        overlay_image: list[torch.Tensor] = normalize_input_image(kwargs.get("overlay_image"))
        opacity: float = normalize_list_to_value(kwargs.get("opacity"))
        blend_mode = normalize_list_to_value(kwargs.get("blend_mode")) or "normal"

        image_count = len(image)
        overlay_count = len(overlay_image)
        if image_count != overlay_count and image_count != 1 and overlay_count != 1:
            raise ValueError(
                "image and overlay_image must contain the same number of images, "
                "or one input must contain exactly one image for broadcasting."
            )
        pair_count = max(image_count, overlay_count)

        nodes: list[dict] = []
        dataset: dict = {"nodes": nodes}

        processed_images = []
        for index in range(pair_count):
            base = image[0] if image_count == 1 else image[index]
            overlay = overlay_image[0] if overlay_count == 1 else overlay_image[index]
            processed = blend_effect(
                base,
                overlay_image=overlay,
                alpha_mask=opacity,
                mode=blend_mode,
            )
            processed_images.append(processed)
            nodes.append(
                create_cached_compare_node(
                    base,
                    processed,
                    index=index,
                )
            )

        batch_list, image_list = normalize_output_image(processed_images)

        payload = {"dataset": dataset}
        safe_send_sync("blend", payload, kwargs.get("node_id"))

        return {
            "ui": {"lf_output": [payload]},
            "result": (batch_list[0], image_list),
        }
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_Blend": LF_Blend,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_Blend": "Blend",
}
# endregion
