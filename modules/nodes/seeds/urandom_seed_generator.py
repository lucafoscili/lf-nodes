import datetime
import json
import os
import time

from datetime import datetime

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers import normalize_json_input

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

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_UrandomSeedGenerator": LF_UrandomSeedGenerator,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_UrandomSeedGenerator": "Urandom Seed Generator",
}
# endregion