import torch

from PIL import ImageFilter
from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers.api import get_resource_url
from ...utils.helpers.comfy import resolve_filepath
from ...utils.helpers.conversion import pil_to_tensor, tensor_to_pil
from ...utils.helpers.logic import normalize_input_image, normalize_input_list, normalize_list_to_value, normalize_output_image
from ...utils.helpers.temp_cache import TempFileCache
from ...utils.helpers.ui import create_masonry_node

# region LF_BlurImages
class LF_BlurImages:
    def __init__(self):
        self._temp_cache = TempFileCache()

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "List of images to blur."
                }),
                "blur_percentage": (Input.FLOAT, {
                    "default": 0.25, 
                    "min": 0.0, 
                    "max": 1.0, 
                    "step": 0.05, 
                    "tooltip": "0% Blur: No blur applied, the image remains as-is. 100% Blur: Maximum blur applied based on the image's dimensions, which would result in a highly blurred (almost unrecognizable) image."
                }),
            },
            "optional": {
                "file_name": (Input.STRING, {
                    "forceInput": True, 
                    "tooltip": "Corresponding list of file names for the images."
                }),
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
    INPUT_IS_LIST = (True, False, False, True)
    OUTPUT_IS_LIST = (False, True, True, False)
    RETURN_NAMES = ("image", "image_list", "file_name", "count")
    RETURN_TYPES = (Input.IMAGE, Input.IMAGE, Input.STRING, Input.INTEGER)

    def on_exec(self, **kwargs: dict):
        self._temp_cache.cleanup()

        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        blur_percentage: float = normalize_list_to_value(kwargs.get("blur_percentage"))
        file_name: list[str] = normalize_input_list(kwargs.get("file_name"))

        blurred_images = []
        blurred_file_names = []

        nodes = []
        dataset = { "nodes": nodes }

        for index, img in enumerate(image):
            if file_name:
                split_name = file_name[index].rsplit('.', 1)
                if len(split_name) == 2:
                    base_name, _ = split_name
                else:
                    base_name = split_name[0]
            else:
                base_name = ""
            
            pil_image = tensor_to_pil(img)
            
            width, height = pil_image.size
            min_dimension = min(width, height)
            adjusted_blur_radius: float = blur_percentage * (min_dimension / 10)
            
            blurred_image = pil_image.filter(ImageFilter.GaussianBlur(adjusted_blur_radius))
            
            blurred_tensor = pil_to_tensor(blurred_image)
            blurred_images.append(blurred_tensor)

            filename_prefix = f"{base_name}_Blur"
            output_file, subfolder, filename = resolve_filepath(
                    filename_prefix=filename_prefix,
                    add_counter=False,
                    image=blurred_tensor,
                    temp_cache=self._temp_cache
            )

            blurred_image.save(output_file, format="PNG")
            url = get_resource_url(subfolder, filename, "temp")

            blurred_file_names.append(filename_prefix)
            nodes.append(create_masonry_node(filename, url, index))

        image_batch, image_list = normalize_output_image(blurred_images)
        
        PromptServer.instance.send_sync(f"{EVENT_PREFIX}blurimages", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })

        return (image_batch[0], image_list, blurred_file_names, len(image_list))
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_BlurImages": LF_BlurImages,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_BlurImages": "Blur images",
}
# endregion