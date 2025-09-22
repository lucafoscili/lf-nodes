import torch

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.filters import vignette_effect
from ...utils.helpers.logic import normalize_input_image, normalize_list_to_value, normalize_output_image
from ...utils.helpers.torch import process_and_save_image
        
# region LF_Vignette
class LF_Vignette:
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
                    "tooltip": "Controls the darkness of the vignette effect. Higher values mean darker edges."
                }),
                "radius": (Input.FLOAT, {
                    "default": 0.75,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.05,
                    "tooltip": "Controls the size of the vignette effect. Lower values mean a smaller vignette."
                }),
                "shape": (["elliptical", "circular"], {
                    "default": "elliptical",
                    "tooltip": "Selects the shape of the vignette effect."
                }),
                "color": (Input.STRING, {
                    "default": "000000", 
                    "tooltip": "Color to use for padding if 'pad' mode is selected (hexadecimal)."
                })
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
    RETURN_TYPES = ("IMAGE", "IMAGE")

    def on_exec(self, **kwargs: dict):
        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        intensity: float = normalize_list_to_value(kwargs.get("intensity"))
        radius: float = normalize_list_to_value(kwargs.get("radius"))
        shape: str = normalize_list_to_value(kwargs.get("shape", "elliptical"))
        color: str = normalize_list_to_value(kwargs.get("color", "000000"))

        nodes: list[dict] = []
        dataset: dict = {"nodes": nodes}

        processed_images = process_and_save_image(
            images=image,
            filter_function=vignette_effect,
            filter_args={
                'intensity': intensity,
                'radius': radius,
                'shape': shape,
                'color': color,
            },
            filename_prefix="vignette",
            nodes=nodes,
        )

        batch_list, image_list = normalize_output_image(processed_images)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}vignette", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })

        return (batch_list[0], image_list)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_Vignette": LF_Vignette
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_Vignette": "Vignette"
}
# endregion