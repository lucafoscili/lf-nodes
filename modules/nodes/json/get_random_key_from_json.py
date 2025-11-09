import random

from . import CATEGORY
from ...utils.constants import FUNCTION, Input, INT_MAX
from ...utils.helpers.comfy import safe_send_sync
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
        json_input = normalize_json_input(kwargs.get("json_input"))

        is_wrapped_single_dict = (
            isinstance(json_input, list)
            and len(json_input) == 1
            and isinstance(json_input[0], dict)
        )

        target = json_input[0] if is_wrapped_single_dict else json_input

        if not isinstance(target, dict) or not target:
            safe_send_sync("getrandomkeyfromjson", {
                "value": "**Warning**: JSON input does not contain any keys.",
            }, kwargs.get("node_id"))
            return ("",)

        random.seed(seed)
        keys = list(target.keys())
        selected_key = random.choice(keys)

        safe_send_sync("getrandomkeyfromjson", {
            "value": f"## Selected key\n{selected_key}\n\n## Content:\n{target.get(selected_key)}",
        }, kwargs.get("node_id"))

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
