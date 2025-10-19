import torch

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input, INT_MAX, RESAMPLERS, RESIZE_MODE_COMBO
from ...utils.helpers.logic import normalize_input_image, normalize_input_list, normalize_list_item, normalize_list_to_value, normalize_output_image
from ...utils.helpers.torch import resize_and_crop_image
from ...utils.helpers.ui import create_resize_node

# region LF_ResizeImageToDimension
class LF_ResizeImageToDimension:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Input image tensor or a list of image tensors."
                }),
                "height": (Input.INTEGER, {
                    "default": 1216,
                    "max": INT_MAX,
                    "tooltip": "The target height for the output image."
                }),
                "width": (Input.INTEGER, {
                    "default": 832,
                    "max": INT_MAX,
                    "tooltip": "The target width for the output image."
                }),
                "resize_method": (RESAMPLERS, {
                    "default": "bicubic",
                    "tooltip": "Method to resize the image."
                }),
                "resize_mode": (RESIZE_MODE_COMBO, {
                    "default": "crop",
                    "tooltip": "Choose whether to crop or pad when resizing."
                }),
                "pad_color": (Input.STRING, {
                    "default": "000000",
                    "tooltip": "Color to use for padding if 'pad' mode is selected (hexadecimal)."
                })
            },
            "optional": {
                "ui_widget": (Input.LF_TREE, {
                    "default": {}
                })
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    INPUT_IS_LIST = (True, True, True, False, False, False, False)
    OUTPUT_IS_LIST = (False, True, False)
    OUTPUT_TOOLTIPS = (
        "Resized image tensor.",
        "List of resized image tensors.",
        "Count of resized images."
    )
    RETURN_NAMES = ("image", "image_list", "count")
    RETURN_TYPES = (Input.IMAGE, Input.IMAGE, Input.INTEGER)

    def on_exec(self, **kwargs: dict):
        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        height: list[int] = normalize_input_list(kwargs.get("height"))
        width: list[int] = normalize_input_list(kwargs.get("width"))
        resize_method: str = normalize_list_to_value(kwargs.get("resize_method"))
        resize_mode: str = normalize_list_to_value(kwargs.get("resize_mode"))
        pad_color: str = normalize_list_to_value(kwargs.get("pad_color"))

        nodes: list[dict] = []
        root: dict = { "children": nodes, "icon":"info-hexagon", "id": "", "value": "" }
        dataset: dict = { "nodes": [root] }

        original_heights: list[int] = []
        original_widths: list[int] = []
        heights: list[int] = []
        widths: list[int] = []

        resized_images: list[torch.Tensor] = []

        for index, img in enumerate(image):
            h: int = normalize_list_item(height, index)
            w: int = normalize_list_item(width, index)

            original_height, original_width = img.shape[1], img.shape[2]
            original_heights.append(original_height)
            original_widths.append(original_width)

            resized_img = resize_and_crop_image(img, resize_method, h, w, resize_mode, pad_color)
            resized_images.append(resized_img)

            new_height, new_width = resized_img.shape[1], resized_img.shape[2]
            heights.append(new_height)
            widths.append(new_width)

            nodes.append(create_resize_node(original_height, original_width, new_height, new_width, index))

        num_resized = len(resized_images)
        summary_message = f"Resized {num_resized} {'image' if num_resized == 1 else 'images'}"
        root["id"] = summary_message
        root["value"] = summary_message

        image_batch, image_list = normalize_output_image(resized_images)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}resizeimagetodimension", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })

        return (image_batch[0], image_list, num_resized)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_ResizeImageToDimension": LF_ResizeImageToDimension,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_ResizeImageToDimension": "Resize image to dimension",
}
# endregion
