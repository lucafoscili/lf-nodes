import torch

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.filters import tilt_shift_effect
from ...utils.helpers.logic import normalize_input_image, normalize_list_to_value, normalize_output_image
from ...utils.helpers.temp_cache import TempFileCache
from ...utils.helpers.torch import process_and_save_image

# region LF_TiltShift
class LF_TiltShift:
    def __init__(self):
        self._temp_cache = TempFileCache()
        
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Image to miniature-ify."
                }),
                "focus_position": (Input.FLOAT, {
                    "default": 0.5, 
                    "min": 0.0, 
                    "max": 1.0, 
                    "step": 0.01,
                    "tooltip": "Vertical centre of sharp band (0 = top, 1 = bottom)."
                }),
                "focus_size": (Input.FLOAT, {
                    "default": 0.25, 
                    "min": 0.05, 
                    "max": 0.9, 
                    "step": 0.01,
                    "tooltip": "Height of sharp zone as fraction of image."
                }),
                "blur_radius": (Input.INTEGER, {
                    "default": 25, 
                    "min": 3, 
                    "max": 151, 
                    "step": 2,
                    "tooltip": "Gaussian radius for out-of-focus areas."
                }),
                "feather": (["linear", "smooth", "expo"], {
                    "default": "smooth",
                    "tooltip": "Fall-off curve of blur vs distance."
                }),
            },
            "optional": {
                "orientation": (["horizontal", "vertical", "circular"], {
                    "default": "horizontal",
                    "tooltip": "Direction of the focus band."
                }),
                "ui_widget": (Input.LF_COMPARE, {"default": {}})
            },
            "hidden": {"node_id": "UNIQUE_ID"}
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_IS_LIST = (False, True)
    RETURN_NAMES = ("image", "image_list")
    RETURN_TYPES = ("IMAGE", "IMAGE")

    def on_exec(self, **kwargs: dict):
        self._temp_cache.cleanup()

        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        focus_position: float = normalize_list_to_value(kwargs.get("focus_position"))
        focus_size: float = normalize_list_to_value(kwargs.get("focus_size"))
        blur_radius: int = normalize_list_to_value(kwargs.get("blur_radius"))
        feather: str = normalize_list_to_value(kwargs.get("feather", "smooth"))
        orientation: str = normalize_list_to_value(kwargs.get("orientation", "horizontal"))

        nodes: list[dict] = []
        dataset: dict = {"nodes": nodes}

        processed_images = process_and_save_image(
            images=image,
            filter_function=tilt_shift_effect,
            filter_args={
                'focus_position': focus_position,
                'focus_size': focus_size,
                'blur_radius': blur_radius,
                'feather': feather,
                'orient': orientation
            },
            filename_prefix="tiltshift",
            nodes=nodes,
            temp_cache=self._temp_cache,
        )

        batch_list, image_list = normalize_output_image(processed_images)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}tiltshift", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })

        return (batch_list[0], image_list)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_TiltShift": LF_TiltShift,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_TiltShift": "Tilt Shift",
}
# endregion