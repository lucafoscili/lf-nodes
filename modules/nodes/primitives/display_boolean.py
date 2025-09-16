import json
import random

from itertools import combinations

from server import PromptServer

from . import CATEGORY
from ...utils.constants import CATEGORY_PREFIX, EVENT_PREFIX, FUNCTION, Input, INT_MAX
from ...utils.helpers import create_history_node, normalize_input_list, normalize_json_input, normalize_list_to_value, randomize_from_history

# region LF_DisplayBoolean
class LF_DisplayBoolean:
    @classmethod 
    def INPUT_TYPES(self):
        return {
            "required": {
                "boolean": (Input.BOOLEAN, {
                    "default": False, 
                    "forceInput": True, 
                    "tooltip": "Boolean value."
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
    OUTPUT_NODE = True
    RETURN_NAMES = ("boolean",)
    RETURN_TYPES = ("BOOLEAN",)

    def on_exec(self, **kwargs: dict):
        display_boolean: bool = normalize_input_list(kwargs.get("boolean"))

        if isinstance(display_boolean, list):
            if len(display_boolean) > 1:
                markdown_value = "\n\n".join(f"{i+1}. {item}" for i, item in enumerate(display_boolean))
            else:
                markdown_value = str(display_boolean[0])
        else:
            markdown_value = ""
        
        PromptServer.instance.send_sync(f"{EVENT_PREFIX}displayboolean", {
            "node": kwargs.get("node_id"),
            "value": markdown_value,
        })

        return (kwargs.get("boolean"),)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_DisplayBoolean": LF_DisplayBoolean,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_DisplayBoolean": "Display boolean",
}
# endregion