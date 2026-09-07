from . import CATEGORY
from ...utils.constants import FUNCTION, Input, INT_MAX
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import normalize_json_input, normalize_list_to_value


class LF_GetKeyFromJSONByIndex:
    """Select one key in object insertion order, without random selection."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_input": (Input.JSON, {"tooltip": "Object whose keys are read in insertion order."}),
                "index": (Input.INTEGER, {
                    "default": 0, "min": 0, "max": INT_MAX,
                    "tooltip": "Zero-based key position: 0 selects the first key. Does not wrap.",
                }),
            },
            "optional": {"ui_widget": (Input.LF_CODE, {"default": ""})},
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    RETURN_TYPES = (Input.STRING,)
    RETURN_NAMES = ("string",)
    OUTPUT_IS_LIST = (False,)
    OUTPUT_TOOLTIPS = ("Key at the requested zero-based position in JSON insertion order.",)

    def on_exec(self, **kwargs):
        target = normalize_json_input(kwargs.get("json_input"))
        if isinstance(target, list) and len(target) == 1 and isinstance(target[0], dict):
            target = target[0]
        if not isinstance(target, dict) or not target:
            raise ValueError("Get Key From JSON by Index requires a nonempty JSON object.")
        if any(not isinstance(key, str) for key in target):
            raise ValueError("JSON object keys must be strings.")

        index = normalize_list_to_value(kwargs.get("index"))
        if isinstance(index, bool) or not isinstance(index, int):
            raise ValueError("Index must be a zero-based integer.")
        if not 0 <= index < len(target):
            raise ValueError(f"Index {index} is out of range for {len(target)} keys; use 0 to {len(target) - 1}.")

        key = list(target)[index]
        payload = {"value": f"## Selected key (index {index})\n{key}"}
        safe_send_sync("getkeyfromjsonbyindex", payload, kwargs.get("node_id"))
        return {"ui": {"lf_output": [payload]}, "result": (key,)}


NODE_CLASS_MAPPINGS = {"LF_GetKeyFromJSONByIndex": LF_GetKeyFromJSONByIndex}
NODE_DISPLAY_NAME_MAPPINGS = {"LF_GetKeyFromJSONByIndex": "Get Key From JSON by Index"}
