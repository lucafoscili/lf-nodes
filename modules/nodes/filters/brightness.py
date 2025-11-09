import torch

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.filters import brightness_effect
from ...utils.helpers.logic import normalize_input_image, normalize_list_to_value, normalize_output_image
from ...utils.helpers.temp_cache import TempFileCache
from ...utils.helpers.torch import process_and_save_image
from ...utils.helpers.comfy import safe_send_sync

# region LF_Brightness
class LF_Brightness:
    def __init__(self):
        self._temp_cache = TempFileCache()

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Input image tensor or a list of image tensors."
                }),
                "brightness_strength": (Input.FLOAT, {
                    "default": 0.0,
                    "min": -1.0,
                    "max": 1.0,
                    "step": 0.05,
                    "tooltip": "Adjust the brightness of the image. Negative values darken, positive values brighten."
                }),
                "gamma": (Input.FLOAT, {
                    "default": 1.0,
                    "min": 0.1,
                    "max": 3.0,
                    "step": 0.1,
                    "tooltip": "Adjust the gamma correction. Values < 1 brighten shadows, > 1 darken highlights."
                }),
            },
            "optional": {
                "midpoint": (Input.FLOAT, {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.05,
                    "tooltip": "Defines the tonal midpoint for brightness scaling."
                }),
                "localized_brightness": (Input.BOOLEAN, {
                    "default": False,
                    "tooltip": "Enhance brightness locally in darker regions."
                }),
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
        "Image tensor with brightness adjusted.",
        "List of image tensors with brightness adjusted."
    )
    RETURN_NAMES = ("image", "image_list")
    RETURN_TYPES = (Input.IMAGE, Input.IMAGE)

    def on_exec(self, **kwargs: dict):
        self._temp_cache.cleanup()

        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        brightness_strength: float = normalize_list_to_value(kwargs.get("brightness_strength"))
        gamma: float = normalize_list_to_value(kwargs.get("gamma"))
        midpoint: float = normalize_list_to_value(kwargs.get("midpoint", 0.5))
        localized_brightness: bool = kwargs.get("localized_brightness", False)

        nodes: list[dict] = []
        dataset: dict = {"nodes": nodes}

        processed_images = process_and_save_image(
            images=image,
            filter_function=brightness_effect,
            filter_args={
                'brightness_strength': brightness_strength,
                'gamma': gamma,
                'midpoint': midpoint,
                'localized_brightness': localized_brightness,
            },
            filename_prefix="brightness",
            nodes=nodes,
            temp_cache=self._temp_cache,
        )

        batch_list, image_list = normalize_output_image(processed_images)

        safe_send_sync("brightness", {
            "dataset": dataset,
        }, kwargs.get("node_id"))

        return (batch_list[0], image_list)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_Brightness": LF_Brightness,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_Brightness": "Brightness",
}
# endregion
