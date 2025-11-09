from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import normalize_list_to_value

# region LF_SwitchFloat
class LF_SwitchFloat:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "on_true": (Input.FLOAT, {
                    "lazy": True,
                    "default": 0,
                    "tooltip": "Value to return if the boolean condition is true."
                }),
                "on_false": (Input.FLOAT, {
                    "lazy": True,
                    "default": 0,
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
        "Final output float value.",
        "List of all output float values (if any)."
    )
    RETURN_NAMES = ("float", "float_list")
    RETURN_TYPES = (Input.FLOAT, Input.FLOAT)

    def check_lazy_status(self, **kwargs: dict):
        switch_value = kwargs["boolean"]
        if switch_value:
            return ["on_true"]
        else:
            return ["on_false"]

    def on_exec(self, **kwargs: dict):
        boolean: bool = normalize_list_to_value(kwargs.get("boolean"))
        on_false: float = kwargs.get("on_false")
        on_true: float = kwargs.get("on_true")

        safe_send_sync("switchfloat", {
            "node": kwargs.get("node_id"),
            "bool": boolean,
        })

        value = on_true if boolean else on_false

        return (value, [value])
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_SwitchFloat": LF_SwitchFloat,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_SwitchFloat": "Switch Float",
}
# endregion
