from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers import convert_to_boolean, convert_to_float, convert_to_int, convert_to_json, normalize_list_to_value

# region LF_ExtractString
class LF_ExtractString:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "text": (Input.STRING, {
                    "default": "", 
                    "multiline": True, 
                    "tooltip": "The string from which the output will be extracted."
                }),
                "starting_delimiter": (Input.STRING, {
                    "default": "{", 
                    "tooltip": "The delimiter where extraction starts."
                }),
                "ending_delimiter": (Input.STRING, {
                    "default": "}", 
                    "tooltip": "The delimiter where extraction ends."
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
    RETURN_NAMES = ("result_as_json", "extracted_text", "result_as_int", "result_as_float", "result_as_boolean")
    RETURN_TYPES = ("JSON", "STRING", "INT", "FLOAT", "BOOLEAN")

    def on_exec(self, **kwargs: dict):
        def extract_nested(text, start_delim, end_delim):
            start_idx = text.rfind(start_delim)
            if start_idx == -1:
                return ""
            end_idx = text.find(end_delim, start_idx + len(start_delim))
            if end_idx == -1:
                return ""
            return text[start_idx + len(start_delim):end_idx]
    
        text: str = normalize_list_to_value(kwargs.get("text"))
        starting_delimiter: str = normalize_list_to_value(kwargs.get("starting_delimiter"))
        ending_delimiter: str = normalize_list_to_value(kwargs.get("ending_delimiter"))
    
        extracted_text = extract_nested(text, starting_delimiter, ending_delimiter)
        
        result_as_json: dict = convert_to_json(extracted_text)
        result_as_int: int = convert_to_int(extracted_text)
        result_as_float: float = convert_to_float(extracted_text)
        result_as_boolean: bool = convert_to_boolean(extracted_text)
    
        PromptServer.instance.send_sync(f"{EVENT_PREFIX}extractstring", {
            "node": kwargs.get("node_id"),
            "value": extracted_text or "...No matches...",
        })
        
        return (result_as_json, extracted_text, result_as_int, result_as_float, result_as_boolean)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_ExtractString": LF_ExtractString,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_ExtractString": "Extract string",
}
# endregion