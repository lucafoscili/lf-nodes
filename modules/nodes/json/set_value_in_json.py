from . import CATEGORY
from ...utils.constants import ANY, FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import normalize_list_to_value, normalize_json_input, normalize_parallel_list

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
    INPUT_IS_LIST = True
    OUTPUT_IS_LIST = (False, False)
    OUTPUT_TOOLTIPS = (
        "Updated JSON object.",
        "Updated JSON array/object collection on the published scalar JSON socket."
    )
    RETURN_NAMES = ("json", "json_list")
    RETURN_TYPES = (Input.JSON, Input.JSON)

    def on_exec(self, **kwargs: dict):
        json_input: dict = normalize_json_input(kwargs.get("json_input"))
        key: str = normalize_list_to_value(kwargs.get("key"))
        value = kwargs.get("value")

        log = f"## Updated key\n{key}\n\n## Content:\n"

        if isinstance(json_input, list):
            values = normalize_parallel_list(value, len(json_input), "value")
            for index, item in enumerate(json_input):
                v = values[index]
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

            safe_send_sync("setvalueinjson", {
                "value": log
            }, kwargs.get("node_id"))
        else:
            scalar_value = normalize_parallel_list(value, 1, "value")[0]
            json_input[key] = scalar_value
            log += f"\n{scalar_value}"

            safe_send_sync("setvalueinjson", {
                "value": log
            }, kwargs.get("node_id"))

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
