import torch

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.filters import gaussian_blur_effect
from ...utils.helpers.logic import normalize_input_image, normalize_list_to_value, normalize_output_image
from ...utils.helpers.temp_cache import TempFileCache
from ...utils.helpers.torch import process_and_save_image

# region LF_GaussianBlur
class LF_GaussianBlur:
    def __init__(self):
        self._temp_cache = TempFileCache()

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Input image tensor or a list of image tensors."
                }),
                "blur_kernel_size": (Input.INTEGER, {
                    "default": 7,
                    "min": 1,
                    "max": 51,
                    "step": 2,
                    "tooltip": "Controls the size of the Gaussian blur kernel. Higher values mean more smoothing."
                }),
                "blur_sigma": (Input.FLOAT, {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 10.0,
                    "step": 0.1,
                    "tooltip": "Standard deviation for the Gaussian kernel. Controls blur intensity."
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
        "Image tensor with Gaussian blur effect applied.",
        "List of image tensors with Gaussian blur effect applied."
    )
    RETURN_NAMES = ("image", "image_list")
    RETURN_TYPES = (Input.IMAGE, Input.IMAGE)

    def on_exec(self, **kwargs: dict):
        self._temp_cache.cleanup()

        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        blur_kernel_size: int = normalize_list_to_value(kwargs.get("blur_kernel_size"))
        blur_sigma: float = normalize_list_to_value(kwargs.get("blur_sigma"))

        nodes: list[dict] = []
        dataset: dict = {"nodes": nodes}

        processed_images = process_and_save_image(
            images=image,
            filter_function=gaussian_blur_effect,
            filter_args={
                'blur_kernel_size': blur_kernel_size,
                'blur_sigma': blur_sigma,
            },
            filename_prefix="gaussianblur",
            nodes=nodes,
            temp_cache=self._temp_cache,
        )

        batch_list, image_list = normalize_output_image(processed_images)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}gaussianblur", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })

        return (batch_list[0], image_list)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_GaussianBlur": LF_GaussianBlur,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_GaussianBlur": "Gaussian Blur",
}
# endregion
