import torch

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.filters import unsharp_mask_effect
from ...utils.helpers.logic import (
    normalize_input_image,
    normalize_list_to_value,
    normalize_output_image,
)
from ...utils.helpers.torch.process_and_save_image import process_and_save_image
from ...utils.helpers.comfy import safe_send_sync

# region LF_UnsharpMask
class LF_UnsharpMask:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (
                    Input.IMAGE,
                    {
                        "tooltip": "Input image tensor or list of tensors to sharpen.",
                    },
                ),
                "amount": (
                    Input.FLOAT,
                    {
                        "default": 0.5,
                        "min": 0.0,
                        "max": 5.0,
                        "step": 0.05,
                        "tooltip": "Strength of the sharpening effect.",
                    },
                ),
                "radius": (
                    Input.INTEGER,
                    {
                        "default": 5,
                        "min": 1,
                        "max": 31,
                        "step": 2,
                        "tooltip": "Gaussian blur kernel size (odd values work best).",
                    },
                ),
                "sigma": (
                    Input.FLOAT,
                    {
                        "default": 1.0,
                        "min": 0.1,
                        "max": 5.0,
                        "step": 0.1,
                        "tooltip": "Gaussian blur sigma controlling softness of edges.",
                    },
                ),
                "threshold": (
                    Input.FLOAT,
                    {
                        "default": 0.0,
                        "min": 0.0,
                        "max": 1.0,
                        "step": 0.01,
                        "tooltip": "Suppress sharpening for pixels below this contrast threshold.",
                    },
                ),
            },
            "optional": {
                "ui_widget": (Input.LF_COMPARE, {
                    "default": {}
                }),
            },
            "hidden": {
                "node_id": "UNIQUE_ID",
            },
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_IS_LIST = (False, True)
    OUTPUT_TOOLTIPS = (
        "Image tensor with unsharp mask effect applied.",
        "List of image tensors with unsharp mask effect applied."
    )
    RETURN_NAMES = ("image", "image_list")
    RETURN_TYPES = (Input.IMAGE, Input.IMAGE)

    def on_exec(self, **kwargs: dict):
        images: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        amount: float = normalize_list_to_value(kwargs.get("amount"))
        radius: int = normalize_list_to_value(kwargs.get("radius"))
        sigma: float = normalize_list_to_value(kwargs.get("sigma"))
        threshold: float = normalize_list_to_value(kwargs.get("threshold"))

        nodes: list[dict] = []
        dataset: dict = {"nodes": nodes}

        processed_images = process_and_save_image(
            images=images,
            filter_function=unsharp_mask_effect,
            filter_args={
                "amount": amount,
                "radius": radius,
                "sigma": sigma,
                "threshold": threshold,
            },
            nodes=nodes,
        )

        batch_list, image_list = normalize_output_image(processed_images)

        payload = {"dataset": dataset}
        safe_send_sync("unsharpmask", payload, kwargs.get("node_id"))

        return {
            "ui": {"lf_output": [payload]},
            "result": (batch_list[0], image_list),
        }
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_UnsharpMask": LF_UnsharpMask,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_UnsharpMask": "Unsharp Mask",
}
# endregion
