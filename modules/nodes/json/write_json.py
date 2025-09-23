from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION
from ...utils.helpers.logic import normalize_json_input

# region LF_WriteJSON
class LF_WriteJSON:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "ui_widget": ("LF_TEXTAREA", {
                    "default": "{}", 
                    "tooltip": "Write your JSON content here."
                }),
            },
            "hidden": { "node_id": "UNIQUE_ID" }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_NODE = True
    RETURN_TYPES = ("JSON",)

    def on_exec(self, **kwargs: dict):
        ui_widget: dict = normalize_json_input(kwargs.get("ui_widget", {}))

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}writejson", {
            "node": kwargs.get("node_id"),
            "value": ui_widget,
        })

        return (ui_widget,)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_WriteJSON": LF_WriteJSON
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_WriteJSON": "Write JSON"
}
# endregion