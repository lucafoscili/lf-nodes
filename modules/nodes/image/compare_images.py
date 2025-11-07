import torch

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers.api import get_resource_url
from ...utils.helpers.comfy import resolve_filepath, safe_send_sync
from ...utils.helpers.conversion import tensor_to_pil
from ...utils.helpers.logic import normalize_input_image, normalize_output_image
from ...utils.helpers.temp_cache import TempFileCache
from ...utils.helpers.ui import create_compare_node

# region LF_CompareImages
class LF_CompareImages:
    def __init__(self):
        self._temp_cache = TempFileCache()

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image_after": (Input.IMAGE, {
                    "tooltip": "Image to be compared (AFTER)."
                }),
            },
            "optional": {
                "image_before": (Input.IMAGE, {
                    "tooltip": "Reference image (BEFORE). If not provided, the AFTER image is reused."
                }),
                "ui_widget": (Input.LF_COMPARE, {
                    "default": {}
                })
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    INPUT_IS_LIST = (True, True, False)
    OUTPUT_IS_LIST = (False, True, True, False)
    OUTPUT_NODE = True
    OUTPUT_TOOLTIPS = (
        "Passthrough image tensor.",
        "List of passthrough image tensors.",
        "All images involved in the comparison.",
        "Dataset information for visualization."
    )
    RETURN_NAMES = ("image", "image_list", "all_images", "dataset")
    RETURN_TYPES = (Input.IMAGE, Input.IMAGE, Input.IMAGE, Input.JSON)

    def on_exec(self, **kwargs: dict):
        self._temp_cache.cleanup()

        has_before : bool = "image_before" in kwargs and kwargs["image_before"] is not None

        image_list_a : list[torch.Tensor] = normalize_input_image(kwargs["image_after"])
        image_list_b : list[torch.Tensor] = normalize_input_image(kwargs["image_before"]) if has_before else image_list_a

        if len(image_list_a) != len(image_list_b):
            raise ValueError("Image lists must have the same length if both inputs are provided.")

        nodes: list[dict] = []
        dataset: dict = {"nodes": nodes}

        for idx, img_a in enumerate(image_list_a):

            pil_a = tensor_to_pil(img_a)
            file_a, sub_a, name_a = resolve_filepath(
                filename_prefix="compare_after",
                image=img_a,
                temp_cache=self._temp_cache
            )
            pil_a.save(file_a, format="PNG")
            url_a = get_resource_url(sub_a, name_a, "temp")

            if has_before:
                img_b = image_list_b[idx]
                pil_b = tensor_to_pil(img_b)
                file_b, sub_b, name_b = resolve_filepath(
                    filename_prefix="compare_before",
                    image=img_b,
                    temp_cache=self._temp_cache
                )
                pil_b.save(file_b, format="PNG")
                url_b = get_resource_url(sub_b, name_b, "temp")
            else:
                url_b = url_a

            nodes.append(create_compare_node(url_b, url_a, idx))

        image_batch, image_list = normalize_output_image(image_list_a)
        combined = image_list_a + (image_list_b if has_before else [])
        _, all_images = normalize_output_image(combined)

        safe_send_sync(
            "compareimages", {"dataset": dataset}, kwargs.get("node_id")
        )

        return (image_batch[0], image_list, all_images, dataset)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_CompareImages": LF_CompareImages,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_CompareImages": "Compare images",
}
# endregion
