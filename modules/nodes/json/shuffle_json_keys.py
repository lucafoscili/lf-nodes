import random

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input, INT_MAX
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
    RETURN_NAMES = ("json",)
    RETURN_TYPES = (Input.JSON,)

    def on_exec(self, **kwargs: dict):
        json_input: dict = normalize_json_input(kwargs.get("json_input"))
        mutate_source: bool = normalize_list_to_value(kwargs.get("mutate_source"))
        seed: int = normalize_list_to_value(kwargs.get("seed"))

        random.seed(seed)

        if mutate_source:
            items = {key: json_input[key] for key in json_input}
            json_input.clear()
            keys = list(items.keys())
            random.shuffle(keys)
            for key in keys:
                json_input[key] = items[key]
            shuffled_json = json_input
        else:
            keys = list(json_input.keys())
            random.shuffle(keys)
            shuffled_json = {key: json_input[key] for key in keys}

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}shufflejsonkeys", {
            "node": kwargs.get("node_id"),
            "value": shuffled_json,
        })

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