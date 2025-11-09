from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import normalize_input_list

# region LF_DisplayString
class LF_DisplayString:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "string": (Input.STRING, {
                    "default": "",
                    "forceInput": True,
                    "tooltip": "String value."
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
    OUTPUT_IS_LIST = (False, True)
    OUTPUT_NODE = True
    OUTPUT_TOOLTIPS = (
        "Pass-through string value.",
        "Pass-through string value as a list."
    )
    RETURN_NAMES = ("string", "string_list")
    RETURN_TYPES = (Input.STRING, Input.STRING)

    def on_exec(self, **kwargs: dict):
        display_string:str = normalize_input_list(kwargs.get("string"))

        if isinstance(display_string, list):
            if len(display_string) > 1:
                markdown_value = "\n\n".join(f"{i+1}. {item}" for i, item in enumerate(display_string))
            else:
                markdown_value = display_string[0]
        else:
            markdown_value = ""

        safe_send_sync("displaystring", {
            "value": markdown_value,
        }, kwargs.get("node_id"))

        out_string = display_string[0] if isinstance(display_string, list) else display_string
        out_list = display_string if isinstance(display_string, list) else [display_string]

        return {
            "ui": {
                "lf_output": [{
                    "string": out_string,
                }],
            },
            "result": (out_string, out_list),
        }
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_DisplayString": LF_DisplayString,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_DisplayString": "Display string",
}
# endregion
