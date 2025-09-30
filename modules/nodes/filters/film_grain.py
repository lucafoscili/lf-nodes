import torch

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.filters import film_grain_effect
from ...utils.helpers.logic import normalize_input_image, normalize_list_to_value, normalize_output_image
from ...utils.helpers.temp_cache import TempFileCache
from ...utils.helpers.torch import process_and_save_image

# region LF_FilmGrain
class LF_FilmGrain:
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
                    "tooltip": "Controls the strength of the film grain effect."
                }),
                "size": (Input.FLOAT, {
                    "default": 1.0,
                    "min": 0.5,
                    "max": 5.0,
                    "step": 0.1,
                    "tooltip": "Controls the size of the grain. Smaller values = finer grain."
                }),
                "tint": (Input.STRING, {
                    "default": "FFFFFF", 
                    "tooltip": "Hexadecimal color (default is FFFFFF for no tint)."
                }),
                "soft_blend": (Input.BOOLEAN, {
                    "default": False,
                    "tooltip": "If True, uses a soft blending mode for the grain."
                }),
            },
            "optional": {
                "ui_widget": (Input.LF_COMPARE, {
                    "default": {}
                }),
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_IS_LIST = (False, True)
    RETURN_NAMES = ("image", "image_list")
    RETURN_TYPES = ("IMAGE", "IMAGE")

    def on_exec(self, **kwargs: dict):
        self._temp_cache.cleanup()

        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        intensity: float = normalize_list_to_value(kwargs.get("intensity"))
        size: float = normalize_list_to_value(kwargs.get("size"))
        tint: str = normalize_list_to_value(kwargs.get("tint", "FFFFFF"))
        soft_blend: bool = normalize_list_to_value(kwargs.get("soft_blend", False))

        nodes: list[dict] = []
        dataset: dict = {"nodes": nodes}

        processed_images = process_and_save_image(
            images=image,
            filter_function=film_grain_effect,
            filter_args={
                "intensity": intensity,
                "size": size,
                "tint": tint,
                "soft_blend": soft_blend
            },
            filename_prefix="film_grain",
            nodes=nodes,
            temp_cache=self._temp_cache,
        )

        batch_list, image_list = normalize_output_image(processed_images)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}filmgrain", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })

        return (batch_list[0], image_list)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_FilmGrain": LF_FilmGrain,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_FilmGrain": "Film grain",
}
# endregion