import torch

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.filters import vibrance_effect
from ...utils.helpers.logic import normalize_input_image, normalize_list_to_value, normalize_output_image
from ...utils.helpers.temp_cache import TempFileCache
from ...utils.helpers.torch import process_and_save_image
from ...utils.helpers.comfy import safe_send_sync

# region LF_Vibrance
class LF_Vibrance:
    def __init__(self):
        self._temp_cache = TempFileCache()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (Input.IMAGE,  {
                    "tooltip": "Input image tensor or a list of image tensors."
                }),
                "intensity": (Input.FLOAT,  {
                    "default": 0.6,
                    "min": -1.0,
                    "max": 2.0,
                    "step": 0.05,
                    "tooltip": "Negative = tame colours, positive = boost muted hues"
                }),
            },
            "optional": {
                "protect_skin": (Input.BOOLEAN, {
                    "default": True,
                    "tooltip": "Less push on hue-range 15-50° (common skin)"
                }),
                "clip_soft": (Input.BOOLEAN, {
                    "default": True,
                    "tooltip": "Roll saturation off near max to avoid clipping"
                }),
                "ui_widget": (Input.LF_COMPARE, {
                    "default": {}
                })
            },
            "hidden": { "node_id": "UNIQUE_ID" }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_IS_LIST = (False, True)
    OUTPUT_TOOLTIPS = (
        "Image tensor with vibrance effect applied.",
        "List of image tensors with vibrance effect applied."
    )
    RETURN_NAMES = ("image", "image_list")
    RETURN_TYPES = (Input.IMAGE, Input.IMAGE)

    def on_exec(self, **kwargs: dict):
        self._temp_cache.cleanup()

        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        intensity: float = normalize_list_to_value(kwargs.get("intensity"))
        protect_skin: bool = normalize_list_to_value(kwargs.get("protect_skin", True))
        clip_soft: bool = normalize_list_to_value(kwargs.get("clip_soft", True))

        nodes: list[dict] = []
        dataset: dict = {"nodes": nodes}

        processed_images = process_and_save_image(
            images=image,
            filter_function=vibrance_effect,
            filter_args={
                'intensity': intensity,
                'protect_skin': protect_skin,
                'clip_soft': clip_soft
            },
            filename_prefix="vibrance",
            nodes=nodes,
            temp_cache=self._temp_cache,
        )

        batch_list, image_list = normalize_output_image(processed_images)

        safe_send_sync("vibrance", {
            "dataset": dataset,
        }, kwargs.get("node_id"))

        return (batch_list[0], image_list)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_Vibrance": LF_Vibrance,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_Vibrance": "Vibrance",
}
# endregion
