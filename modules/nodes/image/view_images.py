import torch

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers.api import get_resource_url
from ...utils.helpers.comfy import resolve_filepath
from ...utils.helpers.conversion import tensor_to_pil
from ...utils.helpers.logic import normalize_input_image, normalize_output_image
from ...utils.helpers.temp_cache import TempFileCache
from ...utils.helpers.ui import create_masonry_node

# region LF_ViewImages
class LF_ViewImages:
    def __init__(self):
        self._temp_cache = TempFileCache()

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
    INPUT_IS_LIST = (True, False)
    OUTPUT_IS_LIST = (False, True)
    OUTPUT_NODE = True
    RETURN_NAMES = ("image", "image_list")
    RETURN_TYPES = ("IMAGE", "IMAGE")

    def on_exec(self, **kwargs: dict):
        self._temp_cache.cleanup()
        
        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))

        nodes: list[dict] = []
        dataset: dict = { "nodes": nodes }
        
        for index, img in enumerate(image):
            pil_image = tensor_to_pil(img)

            output_file, subfolder, filename = resolve_filepath(
                    filename_prefix="view",
                    image=img,
                    temp_cache=self._temp_cache
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