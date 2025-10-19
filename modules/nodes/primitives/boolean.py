from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input, INT_MAX
from ...utils.helpers.logic import normalize_json_input, normalize_list_to_value, randomize_from_history
from ...utils.helpers.ui import create_history_node

# region LF_Boolean
class LF_Boolean:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "boolean": (Input.BOOLEAN, {
                    "default": False,
                    "tooltip": "Boolean value."
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
        "Boolean value.",
        "Boolean value as a list."
    )
    RETURN_NAMES = ("boolean", "boolean_list")
    RETURN_TYPES = (Input.BOOLEAN, Input.BOOLEAN)

    def on_exec(self, **kwargs: dict):
        boolean: bool = normalize_list_to_value(kwargs.get("boolean"))
        enable_history: bool = normalize_list_to_value(kwargs.get("enable_history"))
        randomize: bool = normalize_list_to_value(kwargs.get("randomize"))
        seed: int = normalize_list_to_value(kwargs.get("seed"))
        ui_widget: dict = normalize_json_input(kwargs.get("ui_widget", {}))

        nodes: list[dict] = ui_widget.get("nodes", [])
        dataset: dict = {
            "nodes": nodes
        }

        if enable_history:
            create_history_node(str(boolean), nodes)

        if randomize:
            result = randomize_from_history(nodes, seed)
            boolean = True if result.lower() == "true" else False

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}boolean", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })

        return (boolean, [boolean])
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_Boolean": LF_Boolean,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_Boolean": "Boolean",
}
# endregion
