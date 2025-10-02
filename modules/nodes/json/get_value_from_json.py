from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers.logic import normalize_list_to_value, normalize_json_input

# region LF_GetValueFromJSON
class LF_GetValueFromJSON:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "json_input": (Input.JSON, {
                    "tooltip": "JSON Object."
                }),
                "key": (Input.STRING, {
                    "default": "", 
                    "tooltip": "Key to select."
                }),
                "index": (Input.INTEGER, {
                    "default": 0, 
                    "tooltip": "When the input is a list of JSON objects, it sets the index of the occurrence from which the value is extracted."
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
    RETURN_NAMES = ("json", "string", "number", "int", "float", "boolean")
    RETURN_TYPES = (Input.JSON, Input.STRING, Input.NUMBER, Input.INTEGER, Input.FLOAT, Input.BOOLEAN)

    def on_exec(self, **kwargs: dict):
        key: str = normalize_list_to_value(kwargs.get("key"))
        index: int = normalize_list_to_value(kwargs.get("index"))
        json_input: dict = normalize_json_input(kwargs.get("json_input", {}))

        if isinstance(json_input, list):
            length = len(json_input)
            json_input = json_input[index] if index < length else json_input[length - 1]

        value = json_input.get(key, None)

        json_output = None
        string_output = None
        number_output = None
        int_output = None
        float_output = None
        boolean_output = None

        if value is not None:
            if isinstance(value, dict) or isinstance(value, list):
                json_output = value
            else:
                json_output = {"value": value}
            
            string_output = str(value)
            
            if isinstance(value, str):
                try:
                    numeric_value = float(value)
                    number_output = numeric_value
                    float_output = numeric_value
                    int_output = round(numeric_value) if numeric_value.is_integer() else None
                    boolean_output = numeric_value > 0
                except ValueError:
                    pass
            elif isinstance(value, (int, float)):
                number_output = value
                float_output = float(value)
                int_output = round(value) if isinstance(value, float) else value
                boolean_output = value > 0
            elif isinstance(value, bool):
                boolean_output = value
            else:
                number_output = None
                int_output = None
                float_output = None

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}getvaluefromjson", {
            "node": kwargs.get("node_id"),
            "value": f"## Selected key\n{key}\n\n## Content:\n{string_output}",
        })

        return (json_output, string_output, number_output, int_output, float_output, boolean_output)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_GetValueFromJSON": LF_GetValueFromJSON,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_GetValueFromJSON": "Get Value from JSON",
}
# endregion