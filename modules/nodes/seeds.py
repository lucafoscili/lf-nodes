import datetime
import json
import os
import time

from datetime import datetime

from server import PromptServer

from ..utils.constants import CATEGORY_PREFIX, EVENT_PREFIX, FUNCTION, Input, INT_MAX
from ..utils.helpers import create_history_node, normalize_json_input, normalize_list_to_value

CATEGORY = f"{CATEGORY_PREFIX}/Seed generation"
    
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
    RETURN_TYPES = ("INT",) * 20

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

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}sequentialseedsgenerator", {
            "node": kwargs.get("node_id"), 
            "dataset": dataset,
        })        

        return seeds
# endregion

# region LF_UrandomSeedGenerator
class LF_UrandomSeedGenerator:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "regen_each_run": (Input.BOOLEAN, {
                    "default": True, 
                    "tooltip": "Generates new random seeds each run, while still keeping the seeds fed through the fixed_seeds JSON."
                }),
            },
            "optional": {
                "fixed_seeds": (Input.JSON, {
                    "default": {}, 
                    "tooltip": "LF Widgets-compatible dataset containing 20 previously generated seeds."
                }),
                "ui_widget": (Input.LF_TREE, {
                    "default": {}
                }),
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    RETURN_NAMES = tuple(["fixed_seeds_dataset"] + ["seed"] * 20)
    RETURN_TYPES = tuple(["JSON"] + ["INT"] * 20)

    def on_exec(self, **kwargs: dict):
        json_input: dict = normalize_json_input(kwargs.get("fixed_seeds", {}))

        existing_seeds = [None] * 20

        if json_input:
            try:
                for node in json_input.get("nodes", []):
                    children = node.get("children", [])
                    for child in children:
                        seed_id = child["id"]
                        seed_value = int(child["value"])
                        # Extract the index from 'seedX'
                        index = int(seed_id.replace("seed", "")) - 1
                        if 0 <= index < 20:
                            existing_seeds[index] = seed_value
            except json.JSONDecodeError:
                print("Invalid JSON input. Generating all random seeds.")

        current_timestamp = int(datetime.now().timestamp())
        
        for i in range(20):
            urandom_seed = int.from_bytes(os.urandom(4), 'big')
            
            current_seconds = datetime.now().second
            if current_seconds % 2 == 0:
                urandom_seed ^= current_timestamp
            
            if existing_seeds[i] is None:
                existing_seeds[i] = urandom_seed
            
            time.sleep(0.05)

        execution_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        json_input = {
            "nodes": [
                {
                    "children": [
                        {"id": f"seed{i+1}", "value": str(seed)} for i, seed in enumerate(existing_seeds)
                    ],
                    "icon": "history",
                    "id": f"Execution time: {execution_time}",
                    "value": f"Execution time: {execution_time}"
                }
            ]
        }

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}urandomseedgenerator", {
            "node": kwargs.get("node_id"), 
            "dataset": json_input,
        })

        return (json_input, *existing_seeds)

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        regen_each_run = kwargs.get('regen_each_run', False)
        if regen_each_run:
            return float("NaN")
# endregion

NODE_CLASS_MAPPINGS = {
    "LF_SequentialSeedsGenerator": LF_SequentialSeedsGenerator,
    "LF_UrandomSeedGenerator": LF_UrandomSeedGenerator,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_SequentialSeedsGenerator": "Generate sequential seeds",
    "LF_UrandomSeedGenerator": "Urandom Seed Generator",
}