from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers import normalize_input_list

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
    OUTPUT_NODE = True
    RETURN_NAMES = ("string",)
    RETURN_TYPES = ("STRING",)

    def on_exec(self, **kwargs: dict):
        display_string:str = normalize_input_list(kwargs.get("string"))

        if isinstance(display_string, list):
            if len(display_string) > 1:
                markdown_value = "\n\n".join(f"{i+1}. {item}" for i, item in enumerate(display_string))
            else:
                markdown_value = display_string[0]
        else:
            markdown_value = ""
        
        PromptServer.instance.send_sync(f"{EVENT_PREFIX}displaystring", {
            "node": kwargs.get("node_id"),
            "value": markdown_value,
        })

        return (kwargs.get("string"),)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_DisplayString": LF_DisplayString,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_DisplayString": "Display string",
}
# endregion