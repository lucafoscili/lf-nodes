import random

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input, INT_MAX
from ...utils.helpers.comfy import get_comfy_list
from ...utils.helpers.logic import filter_list, normalize_json_input, normalize_list_to_value
from ...utils.helpers.ui import create_history_node

# region LF_UpscaleModelSelector
class LF_UpscaleModelSelector:
    initial_list = get_comfy_list("upscale_models")
        
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "upscale_model": (["None"] + self.initial_list, {
                    "default": "None", 
                    "tooltip": "Upscale model used to upscale the image."
                }),
                "enable_history": (Input.BOOLEAN, {
                    "default": True, 
                    "tooltip": "Enables history, saving the execution value and date of the widget."
                }),
                "randomize": (Input.BOOLEAN, {
                    "default": False, 
                    "tooltip": "Selects a scheduler randomly."
                }),
                "filter": (Input.STRING, {
                    "default": "", 
                    "tooltip": "When randomization is active, this field can be used to filter upscale models names. Supports wildcards (*)."
                }),
                "seed": (Input.INTEGER, {
                    "default": 42, 
                    "min": 0, 
                    "max": INT_MAX, 
                    "tooltip": "Seed value for when randomization is active."
                }),
            },
            "optional": {
                "ui_widget": (Input.LF_HISTORY, {
                    "default": {}
                }),
            },
            "hidden": {"node_id": "UNIQUE_ID"}
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    RETURN_NAMES = ("combo", "string")
    RETURN_TYPES = (initial_list, Input.STRING)
        
    def on_exec(self, **kwargs: dict):
        upscale_model: str = normalize_list_to_value(kwargs.get("upscale_model"))
        enable_history: bool = normalize_list_to_value(kwargs.get("enable_history"))
        randomize: bool = normalize_list_to_value(kwargs.get("randomize"))
        seed: int = normalize_list_to_value(kwargs.get("seed"))
        filter: str = normalize_list_to_value(kwargs.get("filter"))
        ui_widget: dict = normalize_json_input(kwargs.get("ui_widget", {}))

        upscalers = get_comfy_list("upscale_models")

        nodes: list[dict] = ui_widget.get("nodes", [])
        dataset: dict = {
            "nodes": nodes
        }

        if randomize:
            if filter:
                upscalers = filter_list(filter, upscalers)
                if not upscalers:
                    raise ValueError(f"Not found a model with the specified filter: {filter}")
            random.seed(seed)
            upscale_model = random.choice(upscalers)
        
        if enable_history:
            create_history_node(upscale_model, nodes)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}upscalemodelselector", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })

        return (upscale_model, upscale_model)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_UpscaleModelSelector": LF_UpscaleModelSelector,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_UpscaleModelSelector": "Upscale model selector",
}
# endregion