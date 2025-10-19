import random

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers.logic import normalize_list_to_value

# region LF_ResolutionSwitcher
class LF_ResolutionSwitcher:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "chance_landscape": (Input.FLOAT, {
                    "default": 20.0,
                    "step": 5,
                    "min": 0,
                    "max": 100,
                    "tooltip": "Percentage chance for landscape output, 0-100."
                }),
                "portrait_width": (Input.INTEGER, {
                    "default": 832,
                    "min": 1,
                    "step": 1,
                    "tooltip": "Width when the image is portrait-oriented."
                }),
                "portrait_height": (Input.INTEGER, {
                    "default": 1216,
                    "min": 1,
                    "step": 1,
                    "tooltip": "Height when the image is portrait-oriented."
                }),
                "landscape_width": (Input.INTEGER, {
                    "default": 1216,
                    "min": 1,
                    "step": 1,
                    "tooltip": "Width when the image is landscape-oriented."
                }),
                "landscape_height": (Input.INTEGER, {
                    "default": 832,
                    "min": 1,
                    "step": 1,
                    "tooltip": "Height when the image is landscape-oriented."
                }),
            },
            "optional": {
                "ui_widget": (Input.LF_PROGRESSBAR, {"default": {}}),
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_TOOLTIPS = (
        "Width of the image depending on orientation.",
        "Height of the image depending on orientation.",
        "Whether the final image is in landscape orientation."
    )
    RETURN_NAMES = ("width", "height", "is_landscape")
    RETURN_TYPES = (Input.INTEGER, Input.INTEGER, Input.BOOLEAN)

    def on_exec(self, **kwargs: dict):
        chance_landscape: float = normalize_list_to_value(kwargs.get("chance_landscape"))
        landscape_width: int = normalize_list_to_value(kwargs.get("landscape_width"))
        portrait_width: int = normalize_list_to_value(kwargs.get("portrait_width"))
        landscape_height: int = normalize_list_to_value(kwargs.get("landscape_height"))
        portrait_height: int = normalize_list_to_value(kwargs.get("portrait_height"))

        percentage = max(0, min(100, chance_landscape))
        random_value = random.uniform(0, 100)

        is_landscape = random_value <= percentage

        width = landscape_width if is_landscape else portrait_width
        height = landscape_height if is_landscape else portrait_height

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}resolutionswitcher", {
            "node": kwargs.get("node_id"),
            "bool": is_landscape,
            "roll": random_value,
        })

        return (width, height, is_landscape)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_ResolutionSwitcher": LF_ResolutionSwitcher,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_ResolutionSwitcher": "Resolution switcher",
}
# endregion
