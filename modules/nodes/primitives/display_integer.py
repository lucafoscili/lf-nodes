from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers.logic import normalize_input_list

# region LF_DisplayInteger
class LF_DisplayInteger:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "integer": (Input.INTEGER, {
                    "default": 0,
                    "forceInput": True,
                    "tooltip": "Integer value."
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
        "Pass-through integer value.",
        "Pass-through integer value as a list."
    )
    RETURN_NAMES = ("integer",)
    RETURN_TYPES = (Input.INTEGER,)

    def on_exec(self, **kwargs: dict):
        display_integer: int = normalize_input_list(kwargs.get("integer"))

        if isinstance(display_integer, list):
            if len(display_integer) > 1:
                markdown_value = "\n\n".join(f"{i+1}. {item}" for i, item in enumerate(display_integer))
            else:
                markdown_value = str(display_integer[0])
        else:
            markdown_value = ""

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}displayinteger", {
            "node": kwargs.get("node_id"),
            "value": markdown_value,
        })

        return (kwargs.get("integer"),)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_DisplayInteger": LF_DisplayInteger,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_DisplayInteger": "Display integer",
}
# endregion
