import torch

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers import create_masonry_node, get_resource_url, normalize_input_image, normalize_output_image, resolve_filepath, tensor_to_pil

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
    OUTPUT_IS_LIST = (False, True)
    OUTPUT_NODE = True
    RETURN_NAMES = ("image", "image_list")
    RETURN_TYPES = ("IMAGE", "IMAGE")

    def on_exec(self, **kwargs: dict):
        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))

        nodes: list[dict] = []
        dataset: dict = { "nodes": nodes }
        
        for index, img in enumerate(image):
            pil_image = tensor_to_pil(img)

            output_file, subfolder, filename = resolve_filepath(
                    filename_prefix="view",
                    image=img,
            )
            pil_image.save(output_file, format="PNG")
            url = get_resource_url(subfolder, filename, "temp")

            nodes.append(create_masonry_node(filename, url, index))
        
        batch_list, image_list = normalize_output_image(image)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}viewimages", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })
        
        return (batch_list[0], image_list)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_ViewImages": LF_ViewImages,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_ViewImages": "View images",
}
# endregion