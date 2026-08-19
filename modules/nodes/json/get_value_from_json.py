from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import normalize_list_to_value, normalize_json_input


def _parse_list_index(key):
    if isinstance(key, int):
        return key

    if isinstance(key, str):
        stripped = key.strip()
        if stripped != "":
            try:
                return int(stripped)
            except ValueError:
                return None

    return None


def _get_list_item(items, item_index):
    if not isinstance(items, list) or len(items) == 0:
        return None

    try:
        return items[item_index]
    except IndexError:
        return items[-1]


# region LF_GetValueFromJSON
class LF_GetValueFromJSON:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "json_input": (Input.JSON, {
                    "tooltip": "JSON object or list."
                }),
                "key": (Input.STRING, {
                    "default": "",
                    "tooltip": "Object key to select, or an integer index when the input is a JSON list."
                }),
                "index": (Input.INTEGER, {
                    "default": 0,
                    "tooltip": "When the input is a list of JSON objects, selects the occurrence used for object-key lookup."
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
    OUTPUT_TOOLTIPS = (
        "Extracted value as a JSON object.",
        "Extracted value as a string.",
        "Extracted value as a number.",
        "Extracted value as an integer.",
        "Extracted value as a float.",
        "Extracted value as a boolean."
    )
    RETURN_NAMES = ("json", "string", "number", "int", "float", "boolean")
    RETURN_TYPES = (Input.JSON, Input.STRING, Input.NUMBER, Input.INTEGER, Input.FLOAT, Input.BOOLEAN)

    def on_exec(self, **kwargs: dict):
        key: str = normalize_list_to_value(kwargs.get("key"))
        index: int = normalize_list_to_value(kwargs.get("index"))
        json_input = normalize_json_input(kwargs.get("json_input", {}))

        if isinstance(json_input, dict):
            value = json_input.get(key, None)
        elif isinstance(json_input, list):
            selected_item = _get_list_item(json_input, index)
            list_key_index = _parse_list_index(key)

            if isinstance(selected_item, dict) and key in selected_item:
                value = selected_item.get(key, None)
            elif list_key_index is not None:
                value = _get_list_item(json_input, list_key_index)
            else:
                if isinstance(selected_item, dict):
                    value = selected_item.get(key, None)
                else:
                    value = selected_item if key == "" else None
        else:
            value = None

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

        safe_send_sync("getvaluefromjson", {
            "value": f"## Selected key\n{key}\n\n## Content:\n{string_output}",
        }, kwargs.get("node_id"))

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
