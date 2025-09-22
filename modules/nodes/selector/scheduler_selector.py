import random

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input, INT_MAX, SCHEDULERS
from ...utils.helpers.logic import filter_list, normalize_json_input, normalize_list_to_value
from ...utils.helpers.ui import create_history_node

# region LF_SchedulerSelector
class LF_SchedulerSelector:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "scheduler": (["None"] + SCHEDULERS, {
                    "default": "None", 
                    "tooltip": "Scheduler used to generate the image."
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
                    "tooltip": "When randomization is active, this field can be used to filter scheduler names. Supports wildcards (*)."
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
    RETURN_TYPES = (SCHEDULERS, "STRING")

    def on_exec(self, **kwargs: dict):
        scheduler: str = normalize_list_to_value(kwargs.get("scheduler"))
        enable_history: bool = normalize_list_to_value(kwargs.get("enable_history"))
        randomize: bool = normalize_list_to_value(kwargs.get("randomize"))
        seed: int = normalize_list_to_value(kwargs.get("seed"))
        filter: str = normalize_list_to_value(kwargs.get("filter"))
        ui_widget: dict = normalize_json_input(kwargs.get("ui_widget", {}))

        schedulers = SCHEDULERS

        nodes: list[dict] = ui_widget.get("nodes", [])
        dataset: dict = {
            "nodes": nodes
        }

        if randomize:
            if filter:
                schedulers = filter_list(filter, schedulers)
                if not schedulers:
                    raise ValueError(f"Not found a model with the specified filter: {filter}")
            random.seed(seed)
            scheduler = random.choice(schedulers)
        
        if enable_history:
            create_history_node(scheduler, nodes)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}schedulerselector", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })

        return (scheduler, scheduler)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_SchedulerSelector": LF_SchedulerSelector,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_SchedulerSelector": "Scheduler selector",
}
# endregion