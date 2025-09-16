import torch

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input, INT_MAX, RESAMPLERS
from ...utils.helpers import create_resize_node, normalize_input_image, normalize_input_list, normalize_list_item, normalize_list_to_value, normalize_output_image, resize_image

# region LF_ResizeImageByEdge
class LF_ResizeImageByEdge:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Input image tensor or a list of image tensors."
                }),
                "longest_edge": (Input.BOOLEAN, {
                    "default": False, 
                    "tooltip": "Resizes the image by the longest side if set to True. Otherwise, resizes by the shortest side."
                }),
                "new_size": (Input.INTEGER, {
                    "default": 1024, 
                    "max": INT_MAX,
                    "tooltip": "The size of the longest edge of the output image."
                }),
                "resize_method": (RESAMPLERS, {
                    "default": "bicubic", 
                    "tooltip": "Method to resize the image."
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
    INPUT_IS_LIST = (True, False, True, False, False)
    OUTPUT_IS_LIST = (False, True, False)
    RETURN_NAMES = ("image", "image_list", "count")
    RETURN_TYPES = ("IMAGE", "IMAGE", "INT")

    def on_exec(self, **kwargs: dict):
        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        longest_edge: bool = normalize_list_to_value(kwargs.get("longest_edge"))
        new_size: list[int] = normalize_input_list(kwargs.get("new_size"))
        resize_method: str = normalize_list_to_value(kwargs.get("resize_method"))

        nodes: list[dict] = []
        root: dict = { "children": nodes, "icon":"info-hexagon", "id": "", "value": "" }
        dataset: dict = { "nodes": [root] }

        original_heights: list[int] = []
        original_widths: list[int] = []
        heights: list[int] = []
        widths: list[int] = []

        resized_images: list[torch.Tensor] = []

        for index, img in enumerate(image):
            n_size = normalize_list_item(new_size, index)

            original_height, original_width = img.shape[1], img.shape[2]
            original_heights.append(original_height)
            original_widths.append(original_width)

            resized_img = resize_image(img, resize_method, longest_edge, n_size)
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

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}resizeimagebyedge", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })

        return (image_batch[0], image_list, num_resized)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_ResizeImageByEdge": LF_ResizeImageByEdge,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_ResizeImageByEdge": "Resize image by edge",
}
# endregion