import torch

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import normalize_input_image, normalize_output_image
from ...utils.helpers.ui import create_cached_masonry_node

# region LF_ViewImages
class LF_ViewImages:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Input image tensor or a list of image tensors."
                }),
            },
            "optional": {
                "ui_widget": (Input.LF_MASONRY, {
                    "default": {}
                })
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    INPUT_IS_LIST = True
    OUTPUT_IS_LIST = (False, True)
    OUTPUT_NODE = True
    OUTPUT_TOOLTIPS = (
        "Pass-through image tensor.",
        "List of pass-through image tensors.",
    )
    RETURN_NAMES = ("image", "image_list")
    RETURN_TYPES = (Input.IMAGE, Input.IMAGE)

    def on_exec(self, **kwargs: dict):
        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))

        nodes: list[dict] = []
        dataset: dict = { "nodes": nodes }

        for index, img in enumerate(image):
            nodes.append(
                create_cached_masonry_node(
                    img,
                    index=index,
                    label=f"Image {index + 1}",
                )
            )

        batch_list, image_list = normalize_output_image(image)

        payload = {"dataset": dataset}
        safe_send_sync("viewimages", payload, kwargs.get("node_id"))

        return {
            "ui": {"lf_output": [payload]},
            "result": (batch_list[0], image_list),
        }
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_ViewImages": LF_ViewImages,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_ViewImages": "View images",
}
# endregion
