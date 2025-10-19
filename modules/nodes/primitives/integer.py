from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input, INT_MAX
from ...utils.helpers.logic import normalize_json_input, normalize_list_to_value, randomize_from_history
from ...utils.helpers.ui import create_history_node

# region LF_Integer
class LF_Integer:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "integer": (Input.INTEGER, {
                    "default": 0,
                    "max": INT_MAX,
                    "tooltip": "Integer value."
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
        "Integer value.",
        "Integer value as a list."
    )
    RETURN_NAMES = ("int", "int_list")
    RETURN_TYPES = (Input.INTEGER, Input.INTEGER)

    def on_exec(self, **kwargs: dict):
        integer_input: int = normalize_list_to_value(kwargs.get("integer"))
        enable_history: bool = normalize_list_to_value(kwargs.get("enable_history"))
        randomize: bool = normalize_list_to_value(kwargs.get("randomize"))
        seed: int = normalize_list_to_value(kwargs.get("seed"))
        ui_widget: dict = normalize_json_input(kwargs.get("ui_widget", {}))

        nodes = ui_widget.get("nodes", [])
        dataset = {
            "nodes": nodes
        }

        if enable_history:
            create_history_node(str(integer_input), nodes)

        if randomize:
            integer_input = int(randomize_from_history(nodes, seed))

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}integer", {
            "node": kwargs.get("node_id"),
            "dataset": dataset
        })

        return (integer_input, [integer_input])
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_Integer": LF_Integer,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_Integer": "Integer",
}
# endregion
