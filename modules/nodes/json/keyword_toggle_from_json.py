from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.logic import normalize_list_to_value, normalize_json_input

# region LF_KeywordToggleFromJSON
class LF_KeywordToggleFromJSON:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "json_input": (Input.JSON, {
                    "tooltip": "LF Widgets compatible JSON dataset."
                }),
                "separator": (Input.STRING, {
                    "default": ", ", "tooltip": "Separator for keywords in the output prompt."
                }),
                "ui_widget": ("LF_CHIP", {
                    "default": ""
                })
            },
            "hidden": { 
                "node_id": "UNIQUE_ID"
            }
        }
    
    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_IS_LIST = (False, False, True)
    RETURN_NAMES = ("json", "keywords", "keywords_list")
    RETURN_TYPES = ("JSON", "STRING", "STRING")

    def on_exec(self, **kwargs: dict):
        json_input: dict = normalize_json_input(kwargs.get("json_input"))
        separator: str = normalize_list_to_value(kwargs.get("separator"))
        ui_widget: str = normalize_list_to_value(kwargs.get("ui_widget", ""))

        selected_keywords = ui_widget.split(", ")

        filtered_json = {
            "nodes": [
                node for node in json_input["nodes"]
                if node["id"] in selected_keywords or node["value"] in selected_keywords
            ]
        }

        keyword_values = [node["value"] for node in filtered_json["nodes"]]
        keywords_output = separator.join(keyword_values)

        return (filtered_json, keywords_output, keyword_values)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_KeywordToggleFromJSON": LF_KeywordToggleFromJSON,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_KeywordToggleFromJSON": "Keyword toggle from JSON",
}
# endregion