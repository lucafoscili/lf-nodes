from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input, INT_MAX
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import normalize_json_input, normalize_list_to_value, randomize_from_history
from ...utils.helpers.ui import create_history_node

# region LF_Float
class LF_Float:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "float": (Input.FLOAT, {
                    "default": 0,
                    "step": 0.1,
                    "tooltip": "Float value."
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
        "Float value.",
        "Float value as a list."
    )
    RETURN_NAMES = ("float", "float_list")
    RETURN_TYPES = (Input.FLOAT, Input.FLOAT)

    def on_exec(self, **kwargs: dict):
        float_input: float = normalize_list_to_value(kwargs.get("float"))
        enable_history: bool = normalize_list_to_value(kwargs.get("enable_history"))
        randomize: bool = normalize_list_to_value(kwargs.get("randomize"))
        seed: int = normalize_list_to_value(kwargs.get("seed"))
        ui_widget: dict = normalize_json_input(kwargs.get("ui_widget", {}))

        nodes = ui_widget.get("nodes", [])
        dataset = {
            "nodes": nodes
        }

        if enable_history:
            create_history_node(str(float_input), nodes)

        if randomize:
            float_input = float(randomize_from_history(nodes, seed))

        safe_send_sync("float", {
            "dataset": dataset,
        }, kwargs.get("node_id"))

        return (float_input, [float_input])
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_Float": LF_Float,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_Float": "Float",
}
# endregion
