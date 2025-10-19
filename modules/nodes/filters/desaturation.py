import torch

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.filters import desaturate_effect
from ...utils.helpers.logic import normalize_input_image, normalize_list_to_value, normalize_output_image
from ...utils.helpers.temp_cache import TempFileCache
from ...utils.helpers.torch import process_and_save_image

# region LF_Desaturation
class LF_Desaturation:
    def __init__(self):
        self._temp_cache = TempFileCache()

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Input image tensor or a list of image tensors."
                }),
                "global_level": (Input.FLOAT, {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.05,
                    "tooltip": "Controls the total intensity of the desaturation. 0 is no effect, 1 is fully desaturated."
                }),
                "r_channel": (Input.FLOAT, {
                    "default": 1,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.05,
                    "tooltip": "Controls the intensity of the red channel desaturation relative to the total strength of the filter."
                }),
                "g_channel": (Input.FLOAT, {
                    "default": 1,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.05,
                    "tooltip": "Controls the intensity of the green channel desaturation relative to the total strength of the filter."
                }),
                "b_channel": (Input.FLOAT, {
                    "default": 1,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.05,
                    "tooltip": "Controls the intensity of the blue channel desaturation relative to the total strength of the filter."
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
        "Image tensor with desaturation effect applied.",
        "List of image tensors with desaturation effect applied."
    )
    RETURN_NAMES = ("image", "image_list")
    RETURN_TYPES = (Input.IMAGE, Input.IMAGE)

    def on_exec(self, **kwargs: dict):
        self._temp_cache.cleanup()

        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        global_level: float = normalize_list_to_value(kwargs.get("global_level"))
        r: float = normalize_list_to_value(kwargs.get("r_channel", 1))
        g: float = normalize_list_to_value(kwargs.get("g_channel", 1))
        b: float = normalize_list_to_value(kwargs.get("b_channel", 1))

        nodes: list[dict] = []
        dataset: dict = {"nodes": nodes}

        processed_images = process_and_save_image(
            images=image,
            filter_function=desaturate_effect,
            filter_args={
                'global_level': global_level,
                'channel_levels': [r, g, b],
            },
            filename_prefix="desaturation",
            nodes=nodes,
            temp_cache=self._temp_cache,
        )

        batch_list, image_list = normalize_output_image(processed_images)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}desaturation", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })

        return (batch_list[0], image_list)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_Desaturation": LF_Desaturation,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_Desaturation": "Desaturation",
}
# endregion
