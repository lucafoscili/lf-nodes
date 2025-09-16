import numpy as np

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers import create_masonry_node, get_resource_url, normalize_output_image, numpy_to_tensor, normalize_list_to_value, normalize_json_input, resolve_filepath, tensor_to_pil

# region LF_ImageListFromJSON
class LF_ImageListFromJSON:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "json_input": (Input.JSON, {
                    "tooltip": "Input JSON containing keys to determine batch size."
                }),
                "add_noise": (Input.BOOLEAN, {
                    "default": True, 
                    "tooltip": "Add noise to the images."
                }),
                "width": (Input.INTEGER, {
                    "default": 1024, 
                    "tooltip": "Width of the images."
                }),
                "height": (Input.INTEGER, {
                    "default": 1024, 
                    "tooltip": "Height of the images."
                }),
                "seed": (Input.INTEGER, {
                    "default": 42, 
                    "tooltip": "Seed for generating random noise."
                }),
            },
            "optional": {
                "ui_widget": (Input.LF_MASONRY, { 
                    "default": {} 
                }),
            },
            "hidden": { 
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_IS_LIST = (False, True, True, False, False, False)
    RETURN_NAMES = ("image", "image_list", "keys", "nr", "width", "height")
    RETURN_TYPES = ("IMAGE", "IMAGE", "STRING", "INT", "INT", "INT")

    def on_exec(self, **kwargs: dict):
        json_input: dict = normalize_json_input(kwargs.get("json_input"))
        add_noise: bool = normalize_list_to_value(kwargs.get("add_noise"))
        width: int = normalize_list_to_value(kwargs.get("width"))
        height: int = normalize_list_to_value(kwargs.get("height"))
        seed: int = normalize_list_to_value(kwargs.get("seed"))

        nodes = []
        dataset = { "nodes": nodes }

        keys = list(json_input.keys())
        num_images = len(keys)

        np.random.seed(seed)

        image = []
        for index in range(num_images):

            if add_noise:
                img = numpy_to_tensor(np.random.randint(0, 256, (height, width, 3), dtype=np.uint8))
            else:
                img = numpy_to_tensor(np.full((height, width, 3), 255, dtype=np.uint8))

            pil_img = tensor_to_pil(img)

            output_file, subfolder, filename = resolve_filepath(
                filename_prefix="jsonimage_",
                image=img
            )
            url = get_resource_url(subfolder, filename, "temp")
            pil_img.save(output_file, format="PNG")
            
            image.append(img)
            nodes.append(create_masonry_node(filename, url, index))


        PromptServer.instance.send_sync(f"{EVENT_PREFIX}imagelistfromjson", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })

        image_batch, image_list = normalize_output_image(image)

        return (image_batch[0], image_list, keys, num_images, width, height)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_ImageListFromJSON": LF_ImageListFromJSON,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_ImageListFromJSON": "Image list from JSON",
}
# endregion