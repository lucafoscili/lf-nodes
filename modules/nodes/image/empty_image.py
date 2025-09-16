import re

from PIL import Image
from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers import create_masonry_node, get_resource_url, hex_to_tuple, normalize_input_list, normalize_output_image, pil_to_tensor, resolve_filepath

# region LF_EmptyImage
class LF_EmptyImage:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": (Input.INTEGER, {
                    "default": 1024, 
                    "min": 64, 
                    "max": 8192, 
                    "step": 64,
                    "tooltip": "Width of the empty image."
                }),
                "height": (Input.INTEGER, {
                    "default": 512, 
                    "min": 1, 
                    "max": 4096, 
                    "step": 1,
                    "tooltip": "Height of the empty image."
                }),
                "color": (Input.STRING, {
                    "default": "000000",
                    "tooltip": "Color of the empty image. Format: RRGGBB (hexadecimal)."
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
    INPUT_IS_LIST = (True, True, True)
    OUTPUT_IS_LIST = (False, True)
    RETURN_NAMES = ("image",)
    RETURN_TYPES = ("IMAGE",)

    def on_exec(self, **kwargs: dict):
        width: list[int] = normalize_input_list(kwargs.get("width"))
        height: list[int] = normalize_input_list(kwargs.get("height"))
        color: list[int] = normalize_input_list(kwargs.get("color"))
        
        nodes: list[dict] = []
        dataset: dict = { "nodes": nodes }


        if len(width) != len(height) or len(width) != len(color):
            raise ValueError("Width, height, and color lists must have the same length.")
        
        empty_images = []

        for w, h, c in zip(width, height, color):
            if not isinstance(c, str) or not re.fullmatch(r"[0-9A-Fa-f]{6}", c):
                raise ValueError("Color must be a hexadecimal string in the format RRGGBB.")
            
            rgb = hex_to_tuple(c)
            pil_image = Image.new("RGB", (w, h), rgb)
            empty_image_tensor = pil_to_tensor(pil_image)

            output_file, subfolder, filename = resolve_filepath(
                    filename_prefix="emptyimage",
                    image=empty_image_tensor,
            )
            pil_image.save(output_file, format="PNG")
            url = get_resource_url(subfolder, filename, "temp")

            nodes.append(create_masonry_node(filename, url, len(empty_images)))

            empty_images.append(empty_image_tensor)
        
        image_batch, image_list = normalize_output_image(empty_images)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}emptyimage", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })

        return (image_batch[0], image_list)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_EmptyImage": LF_EmptyImage,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_EmptyImage": "Empty image",
}
# endregion