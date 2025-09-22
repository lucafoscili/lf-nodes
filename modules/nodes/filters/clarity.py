import torch

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.filters import clarity_effect
from ...utils.helpers.logic import normalize_input_image, normalize_list_to_value, normalize_output_image
from ...utils.helpers.torch import process_and_save_image

# region LF_Clarity
class LF_Clarity:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Input image tensor or a list of image tensors."
                }),
                "clarity_strength": (Input.FLOAT, {
                    "default": 0.5, 
                    "min": 0.0, 
                    "max": 5.0, 
                    "step": 0.1, 
                    "tooltip": "Controls the amount of contrast enhancement in midtones."
                }),
                "sharpen_amount": (Input.FLOAT, {
                    "default": 1.0, 
                    "min": 0.0, 
                    "max": 5.0, 
                    "step": 0.1, 
                    "tooltip": "Controls how much sharpening is applied to the image."
                }),
                "blur_kernel_size": (Input.INTEGER, {
                    "default": 7, 
                    "min": 1, 
                    "max": 15, 
                    "step": 2, 
                    "tooltip": "Controls the size of the Gaussian blur kernel. Higher values mean more smoothing."
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
    RETURN_TYPES = ("IMAGE", "IMAGE")

    def on_exec(self, **kwargs: dict):
        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        clarity_strength: float = normalize_list_to_value(kwargs.get("clarity_strength"))
        sharpen_amount: float = normalize_list_to_value(kwargs.get("sharpen_amount"))
        blur_kernel_size: int = normalize_list_to_value(kwargs.get("blur_kernel_size"))

        nodes: list[dict] = []
        dataset: dict = {"nodes": nodes}

        processed_images = process_and_save_image(
            images=image,
            filter_function=clarity_effect,
            filter_args={
                'clarity_strength': clarity_strength,
                'sharpen_amount': sharpen_amount,
                'blur_kernel_size': blur_kernel_size,
            },
            filename_prefix="clarity",
            nodes=nodes,
        )

        batch_list, image_list = normalize_output_image(processed_images)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}clarity", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })

        return (batch_list[0], image_list)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_Clarity": LF_Clarity,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_Clarity": "Clarity",
}
# endregion