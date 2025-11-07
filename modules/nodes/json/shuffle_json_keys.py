import random

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input, INT_MAX
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import normalize_list_to_value, normalize_json_input

# region LF_ShuffleJSONKeys
class LF_ShuffleJSONKeys:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "json_input": (Input.JSON, {
                    "tooltip": "Input JSON object."
                }),
                "mutate_source": (Input.BOOLEAN, {
                    "default": False,
                    "tooltip": "Shuffles the input JSON in place without creating a new dictionary as a copy."
                }),
                "seed": (Input.INTEGER, {
                    "default": 0,
                    "min": 0,
                    "max": INT_MAX,
                    "tooltip": "Seed for the random shuffle."
                })
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
    OUTPUT_NODE = True
    OUTPUT_TOOLTIPS = (
        "Shuffled JSON object.",
        "List of shuffled JSON objects."
    )
    RETURN_NAMES = ("json",)
    RETURN_TYPES = (Input.JSON,)

    def on_exec(self, **kwargs: dict):
        json_input = normalize_json_input(kwargs.get("json_input"))
        mutate_source: bool = normalize_list_to_value(kwargs.get("mutate_source"))
        seed: int = normalize_list_to_value(kwargs.get("seed"))

        random.seed(seed)

        is_wrapped_single_dict = (
            isinstance(json_input, list)
            and len(json_input) == 1
            and isinstance(json_input[0], dict)
        )

        target = json_input[0] if is_wrapped_single_dict else json_input

        if not isinstance(target, dict):
            shuffled_json = json_input
        elif mutate_source:
            items = {key: target[key] for key in target}
            target.clear()
            keys = list(items.keys())
            random.shuffle(keys)
            for key in keys:
                target[key] = items[key]
            shuffled_json = json_input if is_wrapped_single_dict else target
        else:
            keys = list(target.keys())
            random.shuffle(keys)
            shuffled_target = {key: target[key] for key in keys}
            shuffled_json = [shuffled_target] if is_wrapped_single_dict else shuffled_target

        safe_send_sync("shufflejsonkeys", {
            "value": shuffled_json,
        }, kwargs.get("node_id"))

        return (shuffled_json,)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_ShuffleJSONKeys": LF_ShuffleJSONKeys,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_ShuffleJSONKeys": "Shuffle JSON keys",
}
# endregion
