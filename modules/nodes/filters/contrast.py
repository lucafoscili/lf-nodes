import torch

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.filters import contrast_effect
from ...utils.helpers import normalize_input_image, normalize_list_to_value, normalize_output_image, process_and_save_image

# region LF_Contrast
class LF_Contrast:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Input image tensor or a list of image tensors."
                }),
                "contrast_strength": (Input.FLOAT, {
                    "default": 0.25, 
                    "min": -1.0, 
                    "max": 1.0, 
                    "step": 0.05, 
                    "tooltip": "Controls the intensity of the contrast adjustment. 1.0 is no change, below 1 reduces contrast, above 1 increases contrast."
                }),
                "midpoint": (Input.FLOAT, {
                    "default": 0.5, 
                    "min": 0.0, 
                    "max": 1.0, 
                    "step": 0.05, 
                    "tooltip": "Defines the tonal midpoint for contrast scaling."
                }),
            },
            "optional": {
                "localized_contrast": (Input.BOOLEAN, {
                    "default": False,
                    "tooltip": "Apply contrast enhancement locally to edges and textures."
                }),
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

    def on_exec(self, **kwargs: dict) -> None:
        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        contrast_strength: float = normalize_list_to_value(kwargs.get("contrast_strength"))
        midpoint: float = normalize_list_to_value(kwargs.get("midpoint"))
        localized_contrast: bool = kwargs.get("localized_contrast", False)

        nodes: list[dict] = []
        dataset: dict = {"nodes": nodes}

        processed_images = process_and_save_image(
            images=image,
            filter_function=contrast_effect,
            filter_args={
                'contrast_strength': contrast_strength,
                'midpoint': midpoint,
                'localized_contrast': localized_contrast,
            },
            filename_prefix="contrast",
            nodes=nodes,
        )

        batch_list, image_list = normalize_output_image(processed_images)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}contrast", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })

        return (batch_list[0], image_list)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_Contrast": LF_Contrast,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_Contrast": "Contrast",
}
# endregion