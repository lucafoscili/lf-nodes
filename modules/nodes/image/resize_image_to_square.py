import torch

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input, RESAMPLERS
from ...utils.helpers.logic import normalize_input_image, normalize_input_list, normalize_list_item, normalize_list_to_value, normalize_output_image
from ...utils.helpers.torch import resize_to_square
from ...utils.helpers.ui import create_resize_node

# region LF_ResizeImageToSquare
class LF_ResizeImageToSquare:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Input image tensor or a list of image tensors."
                }),
                "square_size": (Input.INTEGER, {
                    "default": 1024, 
                    "tooltip": "The length of the square's edge."
                }),
                "resize_method": (RESAMPLERS, {
                    "default": "bicubic", 
                    "tooltip": "Resampling method for resizing."
                }),
                "crop_position": (["top", "bottom", "left", "right", "center"], {
                    "default": "center", 
                    "tooltip": "Where to crop the image."
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
    INPUT_IS_LIST = (True, True, False, False, False)
    OUTPUT_IS_LIST = (False, True, False)
    RETURN_NAMES = ("image", "image_list", "count")
    RETURN_TYPES = ("IMAGE", "IMAGE", "INT")

    def on_exec(self, **kwargs: dict):
        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        square_size: list[int] = normalize_input_list(kwargs.get("square_size"))
        resize_method: str = normalize_list_to_value(kwargs.get("resize_method"))
        crop_position: str = normalize_list_to_value(kwargs.get("crop_position"))

        nodes: list[dict] = []
        root: dict = { "children": nodes, "icon":"info-hexagon", "id": "", "value": "" }
        dataset: dict = { "nodes": [root] }

        original_heights: list[int] = []
        original_widths: list[int] = []
        heights: list[int] = []
        widths: list[int] = []

        resized_images: list[torch.Tensor] = []

        for index, img in enumerate(image):
            s: int = normalize_list_item(square_size, index)

            original_height, original_width = img.shape[1], img.shape[2]
            original_heights.append(original_height)
            original_widths.append(original_width)

            resized_img = resize_to_square(img, s, resize_method, crop_position)
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

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}resizeimagetosquare", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })

        return (image_batch[0], image_list, num_resized)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_ResizeImageToSquare": LF_ResizeImageToSquare,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_ResizeImageToSquare": "Resize image to square",
}
# endregion