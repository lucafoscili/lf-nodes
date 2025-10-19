import random

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input, INT_MAX
from ...utils.helpers.logic import normalize_list_to_value, normalize_json_input

# region LF_GetRandomKeyFromJSON
class LF_GetRandomKeyFromJSON:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "seed": (Input.INTEGER, {
                    "default": 0,
                    "min": 0,
                    "max": INT_MAX,
                    "tooltip": "The seed for the random pick."
                }),
                "json_input": (Input.JSON, {
                    "tooltip": "JSON object from which a random key will be picked."
                }),
            },
            "optional": {
                "ui_widget": (Input.LF_CODE, {
                    "default": ""
                }),
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_TOOLTIPS = (
        "Randomly selected key from JSON.",
    )
    RETURN_NAMES = ("string",)
    RETURN_TYPES = (Input.STRING,)

    def on_exec(self, **kwargs: dict):
        seed: int = normalize_list_to_value(kwargs.get("seed"))
        json_input: dict = normalize_json_input(kwargs.get("json_input"))

        random.seed(seed)
        keys = list(json_input.keys())
        selected_key = random.choice(keys)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}getrandomkeyfromjson", {
            "node": kwargs.get("node_id"),
            "value": f"## Selected key\n{selected_key}\n\n## Content:\n{json_input.get(selected_key)}",
        })

        return (selected_key,)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_GetRandomKeyFromJSON": LF_GetRandomKeyFromJSON,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_GetRandomKeyFromJSON": "Get Random Key From JSON",
}
# endregion
