import torch

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.filters import split_tone_effect
from ...utils.helpers.logic import normalize_input_image, normalize_list_to_value, normalize_output_image
from ...utils.helpers.torch import process_and_save_image

# region LF_Split tone
class LF_SplitTone:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Base image to colour-grade."
                }),
                "shadows_tint": (Input.STRING, {
                    "default": "0066FF",
                    "tooltip": "Hex colour applied to shadows (e.g. 0066FF)."
                }),
                "highlights_tint": (Input.STRING, {
                    "default": "FFAA55",
                    "tooltip": "Hex colour applied to highlights (e.g. FFAA55)."
                }),
                "balance": (Input.FLOAT, {
                    "default": 0.50, 
                    "min": 0.0, 
                    "max": 1.0, 
                    "step": 0.01,
                    "tooltip": "Luminance pivot. 0 = lift even deep blacks; 1 = tint only the brightest pixels."
                    
                }),
                "softness": (Input.FLOAT, {
                    "default": 0.25, 
                    "min": 0.01, 
                    "max": 0.5, 
                    "step": 0.01,
                    "tooltip": "Width of the transition band around the balance value."
                }),
                "intensity": (Input.FLOAT, {
                    "default": 0.60, 
                    "min": 0.0, 
                    "max": 2.0, 
                    "step": 0.05,
                    "tooltip": "Strength of the tint applied."
                }),
            },
            "optional": {
                "ui_widget": ("LF_COMPARE", {"default": {}}),
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    RETURN_TYPES = ("IMAGE", "IMAGE")
    RETURN_NAMES = ("image", "image_list")
    FUNCTION = FUNCTION
    CATEGORY = CATEGORY
    OUTPUT_IS_LIST = (False, True)

    def on_exec(self, **kwargs: dict):
        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        shadows_tint: str = normalize_list_to_value(kwargs.get("shadows_tint", "0066FF"))
        highlights_tint: str = normalize_list_to_value(kwargs.get("highlights_tint", "FFAA55"))
        balance: float = normalize_list_to_value(kwargs.get("balance", 0.5))
        softness: float = normalize_list_to_value(kwargs.get("softness", 0.25))
        intensity: float = normalize_list_to_value(kwargs.get("intensity", 0.6))

        nodes: list[dict] = []
        dataset: dict = {"nodes": nodes}

        processed_images = process_and_save_image(
            images=image,
            filter_function=split_tone_effect,
            filter_args={
                'shadows_tint': shadows_tint,
                'highlights_tint': highlights_tint,
                'balance': balance,
                'softness': softness,
                'intensity': intensity
            },
            filename_prefix="splittone",
            nodes=nodes,
        )

        batch_list, image_list = normalize_output_image(processed_images)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}splittone", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })

        return (batch_list[0], image_list)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_SplitTone": LF_SplitTone,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_SplitTone": "Split Tone",
}
# endregion