from . import CATEGORY
from ...utils.constants import FUNCTION, Input, INT_MAX
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import normalize_json_input, normalize_list_to_value, randomize_from_history
from ...utils.helpers.ui import create_history_node

# region LF_String
class LF_String:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "string": (Input.STRING, {
                    "default": "",
                    "tooltip": "String value."
                }),
                "enable_history": (Input.BOOLEAN, {
                    "default": True,
                    "tooltip": "Enables history, saving the execution value and date of the widget."
                }),
                "randomize": (Input.BOOLEAN, {
                    "default": False,
                    "tooltip": "Randomly selects a previously used value (must be present in the history list)."
                }),
                "seed": (Input.INTEGER, {
                    "default": 42,
                    "max": INT_MAX,
                    "tooltip": "Seed to control the randomness when 'randomize' is active."
                }),
            },
            "optional": {
                "ui_widget": (Input.LF_HISTORY, {
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
        "String value.",
        "String value as a list."
    )
    RETURN_NAMES = ("string", "string_list")
    RETURN_TYPES = (Input.STRING, Input.STRING)

    def on_exec(self, **kwargs: dict):
        string_input: str = normalize_list_to_value(kwargs.get("string"))
        enable_history: bool = normalize_list_to_value(kwargs.get("enable_history"))
        randomize: bool = normalize_list_to_value(kwargs.get("randomize"))
        seed: int = normalize_list_to_value(kwargs.get("seed"))
        ui_widget: dict = normalize_json_input(kwargs.get("ui_widget", {}))

        nodes = ui_widget.get("nodes", [])
        dataset = {
            "nodes": nodes
        }

        if enable_history:
            create_history_node(string_input, nodes)

        if randomize:
            string_input = randomize_from_history(nodes, seed)

        safe_send_sync("string", {
            "dataset": dataset,
        }, kwargs.get("node_id"))

        return (string_input, [string_input])
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_String": LF_String,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_String": "String",
}
# endregion
