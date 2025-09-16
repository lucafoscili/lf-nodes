import json

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input

# region LF_Something2Number
class LF_Something2Number:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {},
            "optional": {
                "JSON": (Input.JSON, {
                    "tooltip": "JSON value to convert to numbers."
                }),
                "boolean": (Input.BOOLEAN, {
                    "tooltip": "Boolean value to convert to numbers."
                }),
                "string": (Input.STRING, {
                    "tooltip": "String value to convert to numbers."
                }),
                "integer": (Input.INTEGER, {
                    "tooltip": "Integer value to convert to numbers."
                }),
                "float": (Input.FLOAT, {
                    "tooltip": "Float value to convert to numbers."
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
    OUTPUT_IS_LIST = (False, False, False, False, True, True)
    RETURN_NAMES = ("float_sum", "int_sum", "float_list", "int_list")
    RETURN_TYPES = ("FLOAT", "INT", "FLOAT", "INT")

    def on_exec(self, **kwargs: dict):
        def extract_numbers(data):
            if isinstance(data, bool):
                i_val = 1 if data else 0
                f_val = 1.0 if data else 0.0
                float_values.append(f_val)
                integer_values.append(i_val)
                breakdown.append(f"**boolean** detected => {f_val} (float) {i_val} (int)")
            elif isinstance(data, (int, float)):
                i_val = int(data)
                f_val = float(data)
                float_values.append(f_val)
                integer_values.append(i_val)
                breakdown.append(f"**number** detected => {f_val} (float) {i_val} (int)")
            elif isinstance(data, str):
                try:
                    f_val = float(data.strip())
                    i_val = int(f_val)
                    float_values.append(f_val)
                    integer_values.append(i_val)
                    breakdown.append(f"**string** detected => {f_val} (float) {i_val} (int)")
                except ValueError:
                    try:
                        parsed_json = json.loads(data)
                        extract_numbers(parsed_json)
                    except json.JSONDecodeError:
                        pass
            elif isinstance(data, dict):
                for value in data.values():
                    extract_numbers(value)
            elif isinstance(data, (list, tuple, set)):
                for item in data:
                    extract_numbers(item)

        empty = "*Empty*"
        float_values = []
        integer_values = []
        breakdown = []

        for value in kwargs.values():
            extract_numbers(value)

        float_sum = sum(float_values)
        integer_sum = sum(integer_values)
        
        float_log = "\n".join([str(val) for val in float_values]) if float_values else empty
        int_log = "\n".join([str(val) for val in integer_values]) if integer_values else empty
        breakdown_log = "\n".join([f"{i+1}. {val}" for i, val in enumerate(breakdown)]) if breakdown else empty

        log = f"""## Result:
  **Float sum: {str(float_sum)}**
  **Integer sum: {str(integer_sum)}**

## List of floats:
  {float_log}

## List of integers:
  {int_log}

## Breakdown:

  {breakdown_log}
    """
        PromptServer.instance.send_sync(f"{EVENT_PREFIX}something2number", {
            "node": kwargs.get("node_id"), 
            "value": log,
        })

        return (float_sum, integer_sum, float_values, integer_values)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_Something2Number": LF_Something2Number,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_Something2Number": "Convert to number",
}
# endregion