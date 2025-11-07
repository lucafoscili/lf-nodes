from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import normalize_input_list

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
    OUTPUT_TOOLTIPS = (
        "Pass-through boolean value.",
        "Pass-through boolean value as a list."
    )
    RETURN_NAMES = ("boolean",)
    RETURN_TYPES = (Input.BOOLEAN,)

    def on_exec(self, **kwargs: dict):
        display_boolean: bool = normalize_input_list(kwargs.get("boolean"))

        if isinstance(display_boolean, list):
            if len(display_boolean) > 1:
                markdown_value = "\n\n".join(f"{i+1}. {item}" for i, item in enumerate(display_boolean))
            else:
                markdown_value = str(display_boolean[0])
        else:
            markdown_value = ""

        safe_send_sync("displayboolean", {
            "value": markdown_value,
        }, kwargs.get("node_id"))

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
