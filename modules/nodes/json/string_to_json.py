from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers.logic import normalize_json_input

# region LF_StringToJSON
class LF_StringToJSON:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "string": (Input.STRING, {
                    "default": "{}", 
                    "multiline": True, 
                    "tooltip": "Stringified JSON"
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
    INPUT_IS_LIST = (True,)
    OUTPUT_NODE = True
    RETURN_NAMES = ("json",)
    RETURN_TYPES = ("JSON",)

    def on_exec(self, **kwargs: dict):
        json_data: dict = normalize_json_input(kwargs.get("string"))

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}stringtojson", {
            "node": kwargs.get("node_id"),
            "value": kwargs.get("string"),
        })

        return (json_data,)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_StringToJSON": LF_StringToJSON,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_StringToJSON": "Convert string to JSON",
}
# endregion