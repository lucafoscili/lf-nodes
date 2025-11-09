import torch

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.constants import BLEND_MODE_COMBO
from ...utils.filters import blend_effect
from ...utils.helpers.logic import normalize_input_image, normalize_list_to_value, normalize_output_image
from ...utils.helpers.temp_cache import TempFileCache
from ...utils.helpers.torch import process_and_save_image
from ...utils.helpers.comfy import safe_send_sync

# region LF_Blend
class LF_Blend:
    def __init__(self):
        self._temp_cache = TempFileCache()

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
    OUTPUT_IS_LIST = (False, True)
    OUTPUT_TOOLTIPS = (
        "Blended image tensor.",
        "List of blended image tensors."
    )
    RETURN_NAMES = ("image", "image_list")
    RETURN_TYPES = (Input.IMAGE, Input.IMAGE)

    def on_exec(self, **kwargs: dict):
        self._temp_cache.cleanup()

        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        overlay_image: list[torch.Tensor] = normalize_input_image(kwargs.get("overlay_image"))
        opacity: float = normalize_list_to_value(kwargs.get("opacity"))

        nodes: list[dict] = []
        dataset: dict = {"nodes": nodes}

        processed_images = process_and_save_image(
            images=image,
            filter_function=blend_effect,
            filter_args={
                'overlay_image': overlay_image[0],
                'alpha_mask': opacity,
                'mode': kwargs.get("blend_mode", "normal"),
            },
            filename_prefix="blend",
            nodes=nodes,
            temp_cache=self._temp_cache,
        )

        batch_list, image_list = normalize_output_image(processed_images)

        safe_send_sync("blend", {
            "dataset": dataset,
        }, kwargs.get("node_id"))

        return (batch_list[0], image_list)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_Blend": LF_Blend,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_Blend": "Blend",
}
# endregion
