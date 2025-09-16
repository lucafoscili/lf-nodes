import random

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers import normalize_list_to_value

# region LF_RandomBoolean
class LF_RandomBoolean:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "chance_true": (Input.FLOAT, {
                    "default": 50.0, 
                    "step": 1, 
                    "min": 0, 
                    "max": 100, 
                    "tooltip": "Percentage chance for True output, 0-100."
                }),
            },
            "optional": {
                "ui_widget": (Input.LF_PROGRESSBAR, {
                    "default": {}
                }),
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_IS_LIST = (False, True)
    RETURN_NAMES = ("boolean", "boolean_list")
    RETURN_TYPES = ("BOOLEAN", "BOOLEAN")

    def on_exec(self, **kwargs: dict):
        chance_true: str = normalize_list_to_value(kwargs.get("chance_true"))
        
        percentage = max(0, min(100, chance_true))
        random_value = random.uniform(0, 100)

        result = random_value <= percentage

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}randomboolean", {
            "node": kwargs.get("node_id"),
            "bool": result,
            "roll": random_value,
        })

        return (result, [result])

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("NaN")
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_RandomBoolean": LF_RandomBoolean,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_RandomBoolean": "Random boolean",
}
# endregion