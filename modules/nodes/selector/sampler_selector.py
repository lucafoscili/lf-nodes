import random

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input, INT_MAX, SAMPLERS
from ...utils.helpers import create_history_node, filter_list, normalize_json_input, normalize_list_to_value

# region LF_SamplerSelector
class LF_SamplerSelector:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "sampler": (["None"] + SAMPLERS, {
                    "default": "None", 
                    "tooltip": "Sampler used to generate the image."
                }),
                "enable_history": (Input.BOOLEAN, {
                    "default": True, 
                    "tooltip": "Enables history, saving the execution value and date of the widget."
                    }),
                "randomize": (Input.BOOLEAN, {
                    "default": False,
                    "tooltip": "Selects a sampler randomly."
                }),
                "filter": (Input.STRING, {
                    "default": "", 
                    "tooltip": "When randomization is active, this field can be used to filter sampler names. Supports wildcards (*)."
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
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    RETURN_NAMES = ("combo", "string")
    RETURN_TYPES = (SAMPLERS, "STRING")

    def on_exec(self, **kwargs: dict):
        sampler: str = normalize_list_to_value(kwargs.get("sampler"))
        enable_history: bool = normalize_list_to_value(kwargs.get("enable_history"))
        randomize: bool = normalize_list_to_value(kwargs.get("randomize"))
        seed: int = normalize_list_to_value(kwargs.get("seed"))
        filter: str = normalize_list_to_value(kwargs.get("filter"))
        ui_widget: dict = normalize_json_input(kwargs.get("ui_widget", {}))
        
        samplers = SAMPLERS

        nodes: list[dict] = ui_widget.get("nodes", [])
        dataset: dict = {
            "nodes": nodes
        }

        if randomize:
            if filter:
                samplers = filter_list(filter, samplers)
                if not samplers:
                    raise ValueError(f"Not found a model with the specified filter: {filter}")
            random.seed(seed)
            sampler = random.choice(samplers)
        
        if enable_history:
            create_history_node(sampler, nodes)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}samplerselector", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })

        return (sampler, sampler)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_SamplerSelector": LF_SamplerSelector,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_SamplerSelector": "Sampler selector",
}
# endregion