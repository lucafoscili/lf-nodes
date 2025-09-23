from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers.logic import normalize_list_to_value, normalize_json_input

# region LF_SortJSONKeys
class LF_SortJSONKeys:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "json_input": (Input.JSON, {
                    "tooltip": "Input JSON object."
                }),
                "ascending": (Input.BOOLEAN, {
                    "default": True, 
                    "tooltip": "Sort ascending (True) or descending (False)."
                }),
                "mutate_source": (Input.BOOLEAN, {
                    "default": False, 
                    "tooltip": "Sorts the input JSON in place without creating a new dictionary as a copy."
                })
            },
            "optional": {
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
    OUTPUT_NODE = True
    RETURN_NAMES = ("json",)
    RETURN_TYPES = ("JSON",)

    def on_exec(self, **kwargs: dict):
        json_input: dict = normalize_json_input(kwargs.get("json_input"))
        mutate_source: bool = normalize_list_to_value(kwargs.get("mutate_source"))
        ascending: bool = normalize_list_to_value(kwargs.get("ascending"))
            
        if mutate_source:
            items = {key: json_input[key] for key in json_input}
            json_input.clear()
            for key in sorted(items.keys(), reverse=not ascending):
                json_input[key] = items[key]
            sorted_json = json_input
        else:
            sorted_json = {k: json_input[k] for k in sorted(json_input.keys(), reverse=not ascending)}

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}sortjsonkeys", {
            "node": kwargs.get("node_id"),
            "value": sorted_json,
        })

        return (sorted_json,)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_SortJSONKeys": LF_SortJSONKeys,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_SortJSONKeys": "Sort JSON keys",
}
# endregion