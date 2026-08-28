from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import normalize_json_input, normalize_list_to_value

# region LF_StringToJSON
class LF_StringToJSON:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "string": (Input.STRING, {
                    "default": "{}",
                    "multiline": True,
                    "tooltip": "Stringified JSON"
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
    OUTPUT_NODE = True
    OUTPUT_TOOLTIPS = (
        "Parsed JSON value.",
    )
    RETURN_NAMES = ("json",)
    RETURN_TYPES = (Input.JSON,)

    def on_exec(self, **kwargs: dict):
        raw_string = kwargs.get("string")
        json_data: dict = normalize_json_input(raw_string)
        display_value = normalize_list_to_value(raw_string)
        if not isinstance(display_value, str):
            display_value = str(display_value or "")

        payload = {"value": display_value}
        safe_send_sync("stringtojson", payload, kwargs.get("node_id"))

        return {
            "ui": {"lf_output": [payload]},
            "result": (json_data,),
        }
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_StringToJSON": LF_StringToJSON,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_StringToJSON": "Convert string to JSON",
}
# endregion
