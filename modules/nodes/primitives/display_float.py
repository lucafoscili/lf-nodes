from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import normalize_input_list

# region LF_DisplayFloat
class LF_DisplayFloat:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "float": (Input.FLOAT, {
                    "default": 0,
                    "forceInput": True,
                    "tooltip": "Float value."
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
        "Pass-through float value.",
        "Pass-through float value as a list."
    )
    RETURN_NAMES = ("float",)
    RETURN_TYPES = (Input.FLOAT,)

    def on_exec(self, **kwargs: dict):
        display_float: float = normalize_input_list(kwargs.get("float"))

        if isinstance(display_float, list):
            if len(display_float) > 1:
                markdown_value = "\n\n".join(f"{i+1}. {item}" for i, item in enumerate(display_float))
            else:
                markdown_value = str(display_float[0])
        else:
            markdown_value = ""

        safe_send_sync("displayfloat", {
            "value": markdown_value,
        }, kwargs.get("node_id"))

        return (kwargs.get("float"),)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_DisplayFloat": LF_DisplayFloat,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_DisplayFloat": "Display float",
}
# endregion
