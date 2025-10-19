from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input, INT_MAX
from ...utils.helpers.logic import normalize_list_to_value

# region LF_SwitchInteger
class LF_SwitchInteger:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "on_true": (Input.INTEGER, {
                    "default": 0,
                    "max": INT_MAX,
                    "tooltip": "Value to return if the boolean condition is true."
                }),
                "on_false": (Input.INTEGER, {
                    "default": 0,
                    "max": INT_MAX,
                    "tooltip": "Value to return if the boolean condition is false."
                }),
                "boolean": (Input.BOOLEAN, {
                    "default": False,
                    "tooltip": "Boolean condition to switch between 'on_true' and 'on_false' values."
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
    OUTPUT_TOOLTIPS = (
        "Final output integer value.",
        "List of all output integer values (if any)."
    )
    RETURN_NAMES = ("int", "int_list")
    RETURN_TYPES = (Input.INTEGER, Input.INTEGER)

    def on_exec(self, **kwargs: dict):
        boolean: bool = normalize_list_to_value(kwargs.get("boolean"))
        on_false: int = kwargs.get("on_false")
        on_true: int = kwargs.get("on_true")
        on_true = normalize_list_to_value(on_true)
        on_false = normalize_list_to_value(on_false)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}switchinteger", {
            "node": kwargs.get("node_id"),
            "bool": boolean,
        })

        value = on_true if boolean else on_false

        return (value, [value])
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_SwitchInteger": LF_SwitchInteger,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_SwitchInteger": "Switch Integer",
}
# endregion
