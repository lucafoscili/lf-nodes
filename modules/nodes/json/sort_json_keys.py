from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
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
    OUTPUT_TOOLTIPS = (
        "Sorted JSON object.",
        "List of sorted JSON objects."
    )
    RETURN_NAMES = ("json",)
    RETURN_TYPES = (Input.JSON,)

    def on_exec(self, **kwargs: dict):
        json_input = normalize_json_input(kwargs.get("json_input"))
        mutate_source: bool = normalize_list_to_value(kwargs.get("mutate_source"))
        ascending: bool = normalize_list_to_value(kwargs.get("ascending"))

        is_wrapped_single_dict = (
            isinstance(json_input, list)
            and len(json_input) == 1
            and isinstance(json_input[0], dict)
        )

        target = json_input[0] if is_wrapped_single_dict else json_input

        if not isinstance(target, dict):
            sorted_json = json_input
        elif mutate_source:
            items = {key: target[key] for key in target}
            target.clear()
            for key in sorted(items.keys(), reverse=not ascending):
                target[key] = items[key]
            sorted_json = json_input if is_wrapped_single_dict else target
        else:
            sorted_target = {
                key: target[key] for key in sorted(target.keys(), reverse=not ascending)
            }
            sorted_json = [sorted_target] if is_wrapped_single_dict else sorted_target

        safe_send_sync("sortjsonkeys", {
            "value": sorted_json,
        }, kwargs.get("node_id"))

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
