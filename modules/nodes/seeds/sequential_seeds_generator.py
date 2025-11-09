from . import CATEGORY
from ...utils.constants import FUNCTION, Input, INT_MAX
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import normalize_json_input, normalize_list_to_value
from ...utils.helpers.ui import create_history_node

# region LF_SequentialSeedsGenerator
class LF_SequentialSeedsGenerator:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "seed": (Input.INTEGER, {
                    "default": 0, 
                    "max": INT_MAX, 
                    "tooltip": "Seed value from which the other seeds will be progressively increased."
                }),
                "enable_history": (Input.BOOLEAN, {
                    "default": True, 
                    "tooltip": "Enables history, saving the random seeds at execution time."
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
    RETURN_NAMES = ("seed",) * 20
    RETURN_TYPES = (Input.INTEGER,) * 20

    def on_exec(self, **kwargs: dict):
        seed: int = normalize_list_to_value(kwargs.get("seed"))
        enable_history: int = normalize_list_to_value(kwargs.get("enable_history"))
        ui_widget: dict = normalize_json_input(kwargs.get("ui_widget", {}))

        seeds = [seed + i for i in range(20)] 

        nodes: list[dict] = ui_widget.get("nodes", [])
        dataset: dict = {
            "nodes": nodes
        }

        if enable_history:
            create_history_node(str(seed), nodes)

        safe_send_sync("sequentialseedsgenerator", {
            "dataset": dataset,
        }, kwargs.get("node_id"))        

        return seeds
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_SequentialSeedsGenerator": LF_SequentialSeedsGenerator,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_SequentialSeedsGenerator": "Generate sequential seeds",
}
# endregion