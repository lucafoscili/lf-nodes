import torch

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.logic import normalize_input_image
from ...utils.helpers.comfy import safe_send_sync

# region LF_IsLandscape
class LF_IsLandscape:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Input image/images."
                })
            },
            "optional": {
                "ui_widget": (Input.LF_TREE, {
                    "default": {}
                }),
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_IS_LIST = (False, False, False, True, True, True)
    OUTPUT_TOOLTIPS = (
        "Is the image in landscape orientation?",
        "Height of the image.",
        "Width of the image.",
        "List of landscape status for each image.",
        "List of heights for each image.",
        "List of widths for each image."
    )
    RETURN_NAMES = ("is_landscape", "height", "width",
                    "is_landscape_list", "heights_list", "widths_list")
    RETURN_TYPES = (Input.BOOLEAN, Input.INTEGER, Input.INTEGER,
                    Input.BOOLEAN, Input.INTEGER, Input.INTEGER)

    def on_exec(self, **kwargs: dict):
        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))

        nodes: list[dict] = []
        dataset: dict = {"nodes": nodes}

        heights_list: list[int] = []
        widths_list: list[int] = []
        is_landscape_list: list[bool] = []

        counter = 0

        for img in image:
            counter += 1
            _, height, width, _ = img.shape
            heights_list.append(height)
            widths_list.append(width)
            result = width >= height
            is_landscape_list.append(result)
            nodes.append({"icon": "check" if result else "x",
                          "id": counter,
                          "value": f"Image {counter}: {str(result)}"})

        safe_send_sync("islandscape", {
            "dataset": dataset,
        }, kwargs.get("node_id"))

        return (is_landscape_list[0], heights_list[0], widths_list[0],
                is_landscape_list, heights_list, widths_list)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_IsLandscape": LF_IsLandscape,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_IsLandscape": "Is image in landscape res.?",
}
# endregion
