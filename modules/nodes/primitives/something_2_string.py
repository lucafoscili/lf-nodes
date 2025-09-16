from itertools import combinations

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input

# region LF_Something2String
class LF_Something2String:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "separator": (Input.STRING, {
                    "default": ", ", 
                    "tooltip": "Character(s) separating each string apart."
                }),
            },
            "optional": {
                "json": (Input.JSON, {
                    "tooltip": "JSON value to convert to string."
                }),
                "boolean": (Input.BOOLEAN, {
                    "tooltip": "Boolean value to convert to string."
                }),
                "float": (Input.FLOAT, {
                    "tooltip": "Float value to convert to string."
                }),
                "integer": (Input.INTEGER, {
                    "tooltip": "Integer value to convert to string."
                }),
                "ui_widget": (Input.LF_CODE, {
                    "default": ""
                }),
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION

    input_keys = ["json", "boolean", "float", "integer"]
    combinations_list = []

    for r in range(1, len(input_keys) + 1):
        for combo in combinations(input_keys, r):
            combo_name = "_".join(combo)
            combinations_list.append(combo_name)

    OUTPUT_IS_LIST = tuple([False] * len(combinations_list))
    RETURN_TYPES = tuple(["STRING"] * len(combinations_list))
    RETURN_NAMES = tuple(combinations_list)

    def on_exec(self, **kwargs: dict):
        def flatten_input(input_item):
            if isinstance(input_item, list):
                return [str(sub_item) for item in input_item for sub_item in flatten_input(item)]
            elif isinstance(input_item, (dict, bool, float, int)):
                flattened_value = str(input_item)
                breakdown.append(f"**{type(input_item).__name__}** detected => {flattened_value}")
                return [flattened_value]
            elif input_item is not None:
                flattened_value = str(input_item)
                breakdown.append(f"**string** detected => {flattened_value}")
                return [flattened_value]
            return []

        separator = kwargs.get("separator", ", ")
        breakdown = []

        results = []
        combination_logs = []

        for combo_name in self.RETURN_NAMES:
            items = combo_name.split("_")
            flattened_combo = []

            for item in items:
                if item in kwargs:
                    flattened_combo.extend(flatten_input(kwargs[item]))

            combined_string = separator.join(flattened_combo)
            results.append(combined_string)
            combination_logs.append(f"**{combo_name}** => {combined_string}")

        flattened_log = "\n".join([f"{i+1}. {val}" for i, val in enumerate(breakdown)]) if breakdown else "*Empty*"
        combinations_log = "\n".join([f"{i+1}. {val}" for i, val in enumerate(combination_logs)]) if combination_logs else "*Empty*"

        log = f"""## Breakdown

{flattened_log}

## Combination Results:
{combinations_log}
        """
        
        PromptServer.instance.send_sync(f"{EVENT_PREFIX}something2string", {
            "node": kwargs.get("node_id"), 
            "value": log,
        })

        return tuple(results)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_Something2String": LF_Something2String,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_Something2String": "Convert to string",
}
# endregion