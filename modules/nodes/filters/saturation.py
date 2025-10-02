import torch

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.filters import saturation_effect
from ...utils.helpers.logic import normalize_input_image, normalize_list_to_value, normalize_output_image
from ...utils.helpers.temp_cache import TempFileCache
from ...utils.helpers.torch import process_and_save_image

# region LF_Saturation
class LF_Saturation:
    def __init__(self):
        self._temp_cache = TempFileCache()
        
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Input image tensor or a list of image tensors."
                }),
                "intensity": (Input.FLOAT, {
                    "default": 1.2, 
                    "min": 0.0, 
                    "max": 5.0, 
                    "step": 0.1, 
                    "tooltip": "1.0 = no change, <1 = desat, >1 = saturation boost."
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
    RETURN_NAMES = ("image", "image_list")
    RETURN_TYPES = (Input.IMAGE, Input.IMAGE)

    def on_exec(self, **kwargs):
        self._temp_cache.cleanup()

        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        intensity: float = normalize_list_to_value(kwargs["intensity"])

        nodes: list[dict] = []
        dataset: dict = {"nodes": nodes}

        processed = process_and_save_image(
            images=image,
            filter_function=saturation_effect,
            filter_args={
                "intensity": intensity
            },
            filename_prefix="saturation",
            nodes=nodes,
            temp_cache=self._temp_cache,
        )

        batch_list, image_list = normalize_output_image(processed)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}saturation", {
            "node": kwargs.get("node_id"), 
            "dataset": dataset
        })

        return (batch_list[0], image_list)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_Saturation": LF_Saturation,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_Saturation": "Saturation",
}
# endregion