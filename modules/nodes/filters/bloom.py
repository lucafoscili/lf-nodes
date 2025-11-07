import torch

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.filters import bloom_effect
from ...utils.helpers.logic import normalize_input_image, normalize_list_to_value, normalize_output_image
from ...utils.helpers.temp_cache import TempFileCache
from ...utils.helpers.torch import process_and_save_image
from ...utils.helpers.comfy import safe_send_sync

# region LF_Bloom
class LF_Bloom:
    def __init__(self):
        self._temp_cache = TempFileCache()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": (
                        "Source frame to receive the glow.\n"
                        "Tip ▸ Works best if the image is already at final resolution; "
                        "up-res after blooming can soften the effect."
                    )
                }),
                "threshold": (Input.FLOAT, {
                    "default": 0.80,
                    "min": 0.00,
                    "max": 1.00,
                    "step": 0.01,
                    "tooltip": (
                        "Bright-pass cutoff.\n"
                        "‣ 0 = everything glows • 1 = nothing glows\n"
                        "‣ For dim scenes start around **0.15-0.35**; for high-key images **0.65-0.85**.\n"
                        "Accepts 0-1 *or* 0-255 (e.g. 200 ≈ 0.78)."
                    )
                }),
                "radius": (Input.INTEGER, {
                    "default": 15,
                    "min": 3,
                    "max": 127,
                    "step": 2,
                    "tooltip": (
                        "Blur radius in **pixels** (odd numbers only).\n"
                        "Bigger radius → softer, more cinematic glow.\n"
                        "A value ~1-2 % of image width is a good starting point."
                    )
                }),
                "intensity": (Input.FLOAT, {
                    "default": 0.60,
                    "min": 0.00,
                    "max": 2.00,
                    "step": 0.05,
                    "tooltip": (
                        "How strong the bloom reads after compositing.\n"
                        "1.0 = add the blurred highlights at full strength.\n"
                        "< 1.0 softens; > 1.0 exaggerates (can wash out mid-tones)."
                    )
                }),
            },
            "optional": {
                "tint": (Input.STRING, {
                    "default": "FFFFFF",
                    "tooltip": (
                        "Hex colour for the glow (e.g. FFCCAA).\n"
                        "Pure white **FFFFFF** keeps original hue."
                    )
                }),
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
    OUTPUT_TOOLTIPS = (
        "Image tensor with bloom effect applied.",
        "List of image tensors with bloom effect applied."
    )
    RETURN_NAMES = ("image", "image_list")
    RETURN_TYPES = (Input.IMAGE, Input.IMAGE)

    def on_exec(self, **kwargs: dict):
        self._temp_cache.cleanup()

        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        threshold: float = normalize_list_to_value(kwargs.get("threshold"))
        radius: int = normalize_list_to_value(kwargs.get("radius"))
        intensity: float = normalize_list_to_value(kwargs.get("intensity"))
        tint: str = normalize_list_to_value(kwargs.get("tint", "FFFFFF"))

        nodes: list[dict] = []
        dataset: dict = {"nodes": nodes}

        processed_images = process_and_save_image(
            images=image,
            filter_function=bloom_effect,
            filter_args={
                'threshold': threshold,
                'radius': radius,
                'intensity': intensity,
                'tint': tint
            },
            filename_prefix="bloom",
            nodes=nodes,
            temp_cache=self._temp_cache,
        )

        batch_list, image_list = normalize_output_image(processed_images)

        safe_send_sync("bloom", {
            "dataset": dataset,
        }, kwargs.get("node_id"))

        return (batch_list[0], image_list)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_Bloom": LF_Bloom,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_Bloom": "Bloom",
}
# endregion
