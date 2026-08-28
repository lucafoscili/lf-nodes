import torch

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import normalize_input_image, normalize_output_image
from ...utils.helpers.ui import create_cached_compare_node

# region LF_CompareImages
class LF_CompareImages:
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
    INPUT_IS_LIST = True
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
        has_before : bool = "image_before" in kwargs and kwargs["image_before"] is not None

        image_list_a : list[torch.Tensor] = normalize_input_image(kwargs["image_after"])
        image_list_b : list[torch.Tensor] = normalize_input_image(kwargs["image_before"]) if has_before else image_list_a

        if len(image_list_a) != len(image_list_b):
            raise ValueError("Image lists must have the same length if both inputs are provided.")

        nodes: list[dict] = []
        dataset: dict = {"nodes": nodes}

        for idx, img_a in enumerate(image_list_a):
            img_b = image_list_b[idx] if has_before else img_a
            nodes.append(
                create_cached_compare_node(
                    img_b,
                    img_a,
                    index=idx,
                )
            )

        image_batch, image_list = normalize_output_image(image_list_a)
        combined = image_list_a + (image_list_b if has_before else [])
        _, all_images = normalize_output_image(combined)

        safe_send_sync(
            "compareimages", {"dataset": dataset}, kwargs.get("node_id")
        )

        return {
            "ui": {
                "lf_output": [{
                    "dataset": dataset,
                }],
            },
            "result": (image_batch[0], image_list, all_images, dataset),
        }
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_CompareImages": LF_CompareImages,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_CompareImages": "Compare images",
}
# endregion
