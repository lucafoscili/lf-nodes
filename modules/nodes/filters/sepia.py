import torch

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.filters import sepia_effect
from ...utils.helpers.logic import normalize_input_image, normalize_list_to_value, normalize_output_image
from ...utils.helpers.temp_cache import TempFileCache
from ...utils.helpers.torch import process_and_save_image
from ...utils.helpers.comfy import safe_send_sync

# region LF_Sepia
class LF_Sepia:
    def __init__(self):
        self._temp_cache = TempFileCache()

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Input image tensor or a list of image tensors."
                }),
                "intensity": (Input.FLOAT, {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.05,
                    "tooltip": "Controls the strength of the sepia effect."
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
        "Image tensor with sepia effect applied.",
        "List of image tensors with sepia effect applied."
    )
    RETURN_NAMES = ("image", "image_list")
    RETURN_TYPES = (Input.IMAGE, Input.IMAGE)

    def on_exec(self, **kwargs: dict):
        self._temp_cache.cleanup()

        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        intensity: float = normalize_list_to_value(kwargs.get("intensity"))

        nodes: list[dict] = []
        dataset: dict = {"nodes": nodes}

        processed_images = process_and_save_image(
            images=image,
            filter_function=sepia_effect,
            filter_args={
                'intensity': intensity,
            },
            filename_prefix="sepia",
            nodes=nodes,
            temp_cache=self._temp_cache,
        )

        batch_list, image_list = normalize_output_image(processed_images)

        safe_send_sync("sepia", {
            "dataset": dataset,
        }, kwargs.get("node_id"))

        return (batch_list[0], image_list)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_Sepia": LF_Sepia,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_Sepia": "Sepia",
}
# endregion
