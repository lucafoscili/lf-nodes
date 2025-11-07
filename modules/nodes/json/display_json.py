from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import normalize_json_input

# region LF_DisplayJSON
class LF_DisplayJSON:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "json_input": (Input.JSON, {
                    "tooltip": "JSON object to display."
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
        "Pass-through JSON object.",
    )
    RETURN_NAMES = ("json",)
    RETURN_TYPES = (Input.JSON,)

    def on_exec(self, **kwargs: dict):
        json_input: dict = normalize_json_input(kwargs.get("json_input"))

        safe_send_sync("displayjson", {
            "value": json_input,
        }, kwargs.get("node_id"))

        return {
            "ui": {
                "lf_output": [{
                    "json": json_input
                }],
            },
            "result": (json_input,)
        }
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_DisplayJSON": LF_DisplayJSON,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_DisplayJSON": "Display JSON",
}
# endregion
