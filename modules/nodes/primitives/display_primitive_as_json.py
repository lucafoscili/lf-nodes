from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input, INT_MAX
from ...utils.helpers import normalize_input_list

# region LF_DisplayPrimitiveAsJSON
class LF_DisplayPrimitiveAsJSON:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {},
            "optional": {
                "integer": (Input.INTEGER, {
                    "default": 0, 
                    "forceInput": True, 
                    "max": INT_MAX, 
                    "tooltip": "Integer value."
                }),
                "float": (Input.FLOAT, {
                    "default": 0.0, 
                    "forceInput": True, 
                    "step": 0.1, 
                    "tooltip": "Float value."
                }),
                "string": (Input.STRING, {
                    "default": "", 
                    "forceInput": True, 
                    "tooltip": "String value."
                }),
                "boolean": (Input.BOOLEAN, {
                    "default": False, 
                    "forceInput": True, 
                    "tooltip": "Boolean value."
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
    OUTPUT_NODE = True
    RETURN_NAMES = ("json",)
    RETURN_TYPES = ("JSON",)

    def on_exec(self, **kwargs: dict):
        integer_list: int = normalize_input_list(kwargs.get("integer"))
        float_list: float = normalize_input_list(kwargs.get("float"))
        string_list: str = normalize_input_list(kwargs.get("string"))
        boolean_list: bool = normalize_input_list(kwargs.get("boolean"))

        nodes: list[dict] = []
        dataset: dict = {"nodes": nodes}

        if boolean_list:
            for idx, value in enumerate(boolean_list):
                nodes.append({
                    "children": [{"id": f"boolean_{idx}", "value": str(value)}],
                    "description": str(value), "id": f"boolean_{idx}", "value": "boolean"
                })
        
        if float_list:
            for idx, value in enumerate(float_list):
                nodes.append({
                    "children": [{"id": f"float_{idx}", "value": str(value)}],
                    "description": str(value), "id": f"float_{idx}", "value": "float"
                })
        
        if integer_list:
            for idx, value in enumerate(integer_list):
                nodes.append({
                    "children": [{"id": f"integer_{idx}", "value": str(value)}],
                    "description": str(value), "id": f"integer_{idx}", "value": "integer"
                })
        
        if string_list:
            for idx, value in enumerate(string_list):
                nodes.append({
                    "children": [{"id": f"string_{idx}", "value": value}],
                    "description": value, "id": f"string_{idx}", "value": "string"
                })

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}displayprimitiveasjson", {
            "node": kwargs.get("node_id"),
            "value": dataset,
        })

        return (dataset,)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_DisplayPrimitiveAsJSON": LF_DisplayPrimitiveAsJSON,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_DisplayPrimitiveAsJSON": "Display primitive as JSON",
}
# endregion