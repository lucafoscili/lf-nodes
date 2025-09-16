from server import PromptServer

from . import CATEGORY
from ...utils.constants import ANY, EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers import normalize_input_list, normalize_list_item, normalize_list_to_value, normalize_json_input

# region LF_SetValueInJSON
class LF_SetValueInJSON:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "json_input": (Input.JSON, {
                    "tooltip": "JSON Object."
                }),
                "key": (Input.STRING, {
                    "tooltip": "Key to update or insert."
                }),
                "value": (ANY, {
                    "tooltip": "Value to set."
                }),
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
    INPUT_IS_LIST = (False, False, True)
    RETURN_NAMES = ("json", "json_list")
    RETURN_TYPES = ("JSON", "JSON")

    def on_exec(self, **kwargs: dict):
        json_input: dict = normalize_json_input(kwargs.get("json_input"))
        key: str = normalize_list_to_value(kwargs.get("key"))
        value = normalize_input_list(kwargs.get("value"))
    
        log = f"## Updated key\n{key}\n\n## Content:\n"
    
        if isinstance(json_input, list):
            for index, item in enumerate(json_input):
                v = normalize_list_item(value, index)
                if isinstance(item, dict):
                    item[key] = v
                    log += f"\n[{index}]: {v}"
                elif isinstance(item, list):
                    for sub_index, sub_item in enumerate(item):
                        if isinstance(sub_item, dict):
                            sub_item[key] = v
                            log += f"\n[{index}][{sub_index}]: {v}"
                else:
                    log += f"\n[{index}]: Could not update non-dict item."
    
            PromptServer.instance.send_sync(f"{EVENT_PREFIX}setvalueinjson", {
                "node": kwargs.get("node_id"),
                "value": log
            })
        else:
            json_input[key] = value
            log += f"\n{value}"
    
            PromptServer.instance.send_sync(f"{EVENT_PREFIX}setvalueinjson", {
                "node": kwargs.get("node_id"),
                "value": log
            })
    
        s = json_input[0] if isinstance(json_input, list) and len(json_input) == 1 else json_input
    
        return (s, json_input)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_SetValueInJSON": LF_SetValueInJSON,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_SetValueInJSON" : "Set/Create a Value in a JSON Object",
}
# endregion